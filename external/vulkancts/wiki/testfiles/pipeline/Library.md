## Overview

**Core question:** Can graphics pipeline libraries supply compatible partial state that links into a complete graphics pipeline and produces the expected results?

- [`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1-L6465) implements the `graphics_library` test family under the `pipeline_library` construction root.
- Most cases build graphics-pipeline libraries from vertex input, pre-rasterization, fragment-shader, and fragment-output subsets, link their handles into a root graphics pipeline, then validate rendering or a focused special-case result. The `fast.4` and `fast.maintenance5` generated leaves create a single complete, monolithic pipeline, and `misc.primary_rebind` also includes monolithic and shader-object variants.
- `fast` and `optimize` run the generated pipeline-tree configurations without and with link-time optimization. `misc` covers focused contracts such as independent layouts, null descriptor-set layouts, dynamic-rendering create information, library resource lifetime, device-group view selection, and command-buffer rebinding.
- The Vulkan rules define the subset state and the compatibility requirements for graphics pipeline libraries ([graphics pipeline subsets](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-subsets-complete), [pipeline-library layouts](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-pipeline-library-layouts)).

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Graphics pipeline library subsets.** `VK_EXT_graphics_pipeline_library` lets a graphics pipeline provide one or more of four state subsets: vertex input interface, pre-rasterization shaders, fragment shader, and fragment output interface. A linked root obtains missing state through `VkPipelineLibraryCreateInfoKHR`.
- **Linking modes.** Library creation sets `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`. The optimized path retains link-time optimization information in the library and requests `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` for the final linked pipeline. The fast path omits those optimization flags.
- **Pipeline layouts.** A library layout can include descriptor-set layouts for the shader stages it supplies. `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT` permits compatible independently specified set layouts. Some test cases deliberately use `VK_NULL_HANDLE` slots, so the test distinguishes unused layout positions from descriptors that shaders actually access.

## Registration Hierarchy

```text
pipeline.pipeline_library.graphics_library
├── fast
├── optimize
└── misc
```

[`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L218) attaches `graphics_library` only while it builds `pipeline_library` with `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`, and excludes this registration in Vulkan SC builds. [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6246-L6462) registers the three intermediate nodes. The Vulkan mustpass file contains 112 executable leaves below this family: 15 under `fast`, 13 under `optimize`, and 84 under `misc` ([`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L1-L112)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Why it changes the test |
|---|---|---|
| First-level intermediate node | `fast`, `optimize`, `misc` | Chooses generated-tree linkage with a selected optimization mode or focused special behavior. |
| Pipeline tree | Registered names such as `0_00_11_11`, `1_1_1_1`, `4`, and `maintenance5` | Determines the arrangement and subset ownership of library leaves before linking. |
| Graphics pipeline subset | Vertex input interface, pre-rasterization shaders, fragment shader, fragment output interface | Determines which create-info state each library provides. |
| Link optimization | Disabled for `fast`; retained and enabled for `optimize` | Changes pipeline create flags while keeping the configuration matrix largely shared. |
| Pipeline layouts | Combined, vertex-only, fragment-only, independent sets, and layouts with null entries | Exercises stage-scoped layout compatibility during library creation and linking. |
| Null descriptor layout pattern | `1`, `11`, `01`, `10`, `101`, `1010`, `1001` | Encodes which layout-array positions are used by vertex or fragment shaders. |
| Miscellaneous execution mode | Layout, descriptor, dynamic rendering, shared fragment library, multiview, multisample, transform feedback, resource lifetime, rebind, and view-mask modes | Selects a narrow API contract with its own setup and result check. |
| Construction type within selected miscellaneous cases | `monolithic`, `fast_lib`, `optimized_lib`, `eso_unlinked_spriv` | Lets `primary_rebind` compare rebinding behavior across construction models. |

The configuration helper uses a `PipelineTreeConfiguration`: each entry supplies a parent index and shader count. [`getTestName()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L129-L149) serializes that shape into the leaf suffix, and [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5046-L5280) registers the generated matrix.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node registered below `graphics_library`.

### fast: fast-linked graphics pipeline library configurations

`fast` passes `optimize=false` to [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5046-L5280). For multi-node pipeline-tree shapes, the implementation creates partial libraries and links the root without the link-time optimization flags. The single-node `4` leaf instead creates a complete monolithic pipeline. `maintenance5` repeats that single-node shape with delayed shader creation to exercise the Maintenance5 shader-module behavior.

### optimize: link-time-optimized graphics pipeline library configurations

`optimize` passes `optimize=true` to the same configuration generator. [`calcPipelineCreateFlags()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L151-L167) adds `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` for a library and `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` for the final non-library pipeline. The rendered output must remain correct after this alternate linkage path.

### misc: focused graphics pipeline library contracts

`misc` groups specialized leaves rather than one generated tree matrix. Its intermediate descendants cover:

- `independent_pipeline_layout_sets` and `bind_null_descriptor_set`, which exercise set-layout compatibility and null positions;
- `other`, which includes link-time comparison, dynamic-rendering create-info cases, shared fragment library behavior, device-index/view-index behavior, unusual multisample state, transform feedback, and destruction before linking;
- `non_graphics`, which checks shader-module create information for compute, ray tracing, and ray tracing libraries;
- `always_null_set_layout`, which validates used and unused sets across fast and optimized construction;
- `primary_rebind`, which tests a pipeline bind in the primary command buffer after secondary-command work; and
- `view_mask`, which checks view-mask state split across graphics pipeline libraries.

## Shader Analysis

The test family generates or loads vertex and fragment programs for its variants, but shader instruction behavior is not the primary behavioral axis. The configuration flow uses shaders to make stage-specific descriptor layouts and linked rendering observable. Specialized miscellaneous leaves generate their own programs where necessary, including the storage-buffer programs used by `always_null_set_layout` ([`AlwaysNullSetLayoutCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5324-L5393)). No single shader walkthrough represents the family without obscuring the more important library-creation and linkage choices.

## Runtime Execution and Result Checking

### Generated configuration flow

1. The test selects a tree configuration, an optimization choice, delayed shader creation, and the Maintenance5 choice. [`PipelineLibraryTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1270-L1335) requires the applicable graphics pipeline library support and selected extensions.
2. [`PipelineLibraryTestInstance::runTest()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L837-L1001) creates a render pass, vertex and descriptor buffers, descriptor layouts, descriptor sets, and pipeline layouts. It uses a combined layout or stage-specific layouts according to the subset coverage.
3. The implementation walks the tree from leaves to root. For each entry it adds state for the subsets that entry owns, supplies any child library handles through `VkPipelineLibraryCreateInfoKHR`, and creates a graphics pipeline. In multi-node cases, non-root entries retain `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`, while the root becomes executable after the complete subset mask is present. The single-node `fast.4` and `fast.maintenance5` cases have no child libraries; their root supplies all four subsets directly.
4. The test records a render pass, binds the vertex buffer, root pipeline, and two descriptor sets, then draws. It copies both color and depth images into host-visible buffers, submits the command buffer, waits, and invalidates the allocations.
5. [`verifyColorImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1091-L1119) compares a precise green, blue, and black region pattern. [`verifyDepthImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1121-L1160) compares the expected diagonal depth pattern.

### Focused miscellaneous flow

[`PipelineLibraryMiscTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1495-L1540) dispatches each focused mode after shared render-target and command-buffer setup. Layout and descriptor modes render or write storage-buffer data, then compare it with expected values. [`verifyResult()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L2806-L2832) reports the first mismatched texel and expected color; another helper compares a generated reference image with a small tolerance. Some modes validate Vulkan creation or command behavior instead of the standard image:

- The dynamic-rendering cases vary absent, null-pointer, or intentionally invalid rendering create information.
- `destroy_resources_before_link_samplers_2` and `destroy_resources_before_link_samplers_3` validate library linkage after selected resources are destroyed.
- `primary_rebind` records secondary work, then checks a primary-command-buffer pipeline rebind.
- `view_mask` creates all four library subsets, links them, renders two layers with a view mask, and compares the layers with separate expected colors ([`viewMaskRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6007-L6241)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fast` | Incorrect creation or linkage of graphics pipeline libraries without link-time optimization. |
| `optimize` | Incorrect retention or use of link-time optimization information when linking libraries. |
| `misc` | A focused pipeline-library contract failed, such as layout compatibility, null descriptor handling, creation-info validation, resource lifetime, device-group view selection, or pipeline rebinding. |

### Cause Analysis

#### Fast-linked library creation or linkage

**Possible failure symptoms:** A `fast` leaf fails pipeline creation, or its color/depth readback differs from the exact reference patterns.

**Possible implementation causes:** The implementation may assign state to the wrong graphics-pipeline-library subset, lose a child library handle while building the tree, or fail to combine the supplied subset flags into a complete root pipeline. The source creates leaf libraries first and merges their handles and flags toward the root, so a defect in that linkage path can leave the executable pipeline with missing or incompatible state.

#### Link-time optimization retention or final linking

**Possible failure symptoms:** An `optimize` leaf fails while its comparable fast-linked configuration succeeds, or the optimized root produces an incorrect color/depth pattern.

**Possible implementation causes:** The implementation may mishandle `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` on libraries or `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` on the final pipeline. A compiler or driver can also apply an optimization that changes shader-stage, layout, or fixed-function behavior during library linking. The test compares execution, not timing, so it localizes the problem to optimized linkage behavior rather than proving a particular compiler stage caused it.

#### Focused pipeline-library contract

**Possible failure symptoms:** A `misc` leaf reports a creation error, an unexpected validation outcome, an incorrect texel or storage-buffer value, a wrong multiview layer color, or an incorrect pipeline-rebind result.

**Possible implementation causes:** Each descendant isolates a different API contract. Examples include incorrect independent-set layout compatibility, treating null layout entries as shader-accessible descriptors, losing dynamic-rendering information across libraries, retaining destroyed resources incorrectly, propagating the wrong device index into `gl_ViewIndex`, or preserving stale pipeline state across primary and secondary command buffers. The final image may identify the selected behavior but does not always isolate a single lower-level driver subsystem; source-level investigation should follow the failing leaf.

## Case Pruning

### Requirement-based pruning

The generated cases require `VK_KHR_pipeline_library`, except `fast.maintenance5`, whose support check requires `VK_KHR_maintenance5` instead. Generated cases with delayed shader creation or multiple tree nodes additionally require the `VK_EXT_graphics_pipeline_library` extension and its `graphicsPipelineLibrary` feature; therefore the single-node `fast.4` and Maintenance5 leaves do not have that requirement. The `PipelineLibraryMiscTestCase` cases require `VK_EXT_graphics_pipeline_library`. [`PipelineLibraryMiscTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L4405-L4464) adds requirements for selected modes: device-group creation and multiview for view-index tests, `graphicsPipelineLibraryFastLinking` for the fast independent-layout path, ray-tracing pipeline support for ray-tracing shader-module cases, `VK_KHR_pipeline_library` for the ray-tracing-library case, dynamic rendering for its create-info modes, mesh-shader plus clip/cull-distance support for the shared-fragment-library case, transform feedback for its focused case, and Maintenance4 for destroy-before-link cases. `always_null_set_layout` separately requires the selected library-construction prerequisites and fragment stores and atomics. `view_mask` requires graphics pipeline library, dynamic rendering, and multiview support. `primary_rebind` uses construction-specific requirements plus dynamic rendering and `extendedDynamicState3ColorWriteMask`; consequently, its monolithic and shader-object leaves do not unconditionally require `VK_EXT_graphics_pipeline_library`. The complete family is absent from Vulkan SC builds.

### Design-based pruning

The configuration generator keeps a curated set of pipeline-tree shapes rather than every possible tree. It creates only shapes that exercise distinct subset and link relationships. The null-layout generator skips uninteresting arrangements, including same-set pairs and a two-set case with no gap. The page registers its own family only under `pipeline_library`, so the main generated suite does not duplicate the same family under every CTS construction root.

## Key Takeaways

- The configuration matrix validates execution after library linking, so a pass requires more than successful `vkCreateGraphicsPipelines` calls.
- `fast` and `optimize` differ in the link-time optimization contract, while their shared tree vocabulary lets failures be compared across those modes.
- `misc` broadens coverage beyond rendering to layouts, null handles, dynamic rendering, resource lifetime, device groups, and command-buffer state.
- The 112 mustpass leaves are intentionally summarized by their first-level behavior; the parseable registration tree stays limited to the three direct intermediate nodes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration root | [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6246-L6462) | Registers `graphics_library`, `fast`, `optimize`, and all `misc` descendants. |
| Parent construction-root registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L218) | Runs this implementation only under `pipeline_library`. |
| Tree configuration generator | [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5046-L5280) | Supplies the generated `fast` and `optimize` leaves. |
| Configuration execution and checking | [`PipelineLibraryTestInstance::runTest()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L837-L1089) | Creates, links, runs, copies, and validates the main pipeline-tree cases. |
| Main color/depth reference checks | [`verifyColorImage()` and `verifyDepthImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1091-L1160) | Define the expected rendering output. |
| Miscellaneous mode dispatch | [`PipelineLibraryMiscTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1495-L1540) | Selects focused `misc` behavior. |
| Multiview view-mask execution | [`viewMaskRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6007-L6241) | Creates four libraries, links them, renders two layers, and compares them. |
| Mustpass coverage | [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L1-L112) | Lists the 112 executable `graphics_library` leaves. |
| Vulkan graphics pipeline rules | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-subsets-complete) | Defines graphics pipeline subsets and linked-state requirements. |
