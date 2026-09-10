## Overview

**Core question:** Can graphics pipeline libraries supply compatible partial state that links into a complete graphics pipeline and produces the expected results?

- [`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1-L6897) implements the `graphics_library` test family under the `pipeline_library` construction root.
- Most cases build graphics-pipeline libraries from vertex input, pre-rasterization, fragment-shader, and fragment-output subsets, link their handles into a root graphics pipeline, then validate rendering or a focused special-case result. The `fast.4` and `fast.maintenance5` generated leaves create a single complete, monolithic pipeline, and `misc.primary_rebind` and `misc.primary_rebind_diff_layouts` also include monolithic and shader-object variants.
- `fast` and `optimize` run the generated pipeline-tree configurations without and with link-time optimization. `misc` covers focused contracts such as independent layouts, null descriptor-set layouts, dynamic-rendering create information, library resource lifetime, device-group view selection, and command-buffer rebinding. `independent_sets_random` generates pseudorandom per-stage descriptor-set layouts and links them with `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`.
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
├── independent_sets_random
└── misc
```

[`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L213-L218) attaches `graphics_library` only while it builds `pipeline_library` with `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`, and excludes this registration in Vulkan SC builds. [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6651-L6895) registers the four intermediate nodes; `independent_sets_random` is populated by [`IndependentSets::createRandomTests()`](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995). The Vulkan mustpass file contains 836 executable leaves below this family: 15 under `fast`, 13 under `optimize`, 720 under `independent_sets_random`, and 88 under `misc` ([`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L36654-L37489)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Why it changes the test |
|---|---|---|
| First-level intermediate node | `fast`, `optimize`, `independent_sets_random`, `misc` | Chooses generated-tree linkage with a selected optimization mode, pseudorandom independent set layouts, or focused special behavior. |
| Pipeline tree | Registered names such as `0_00_11_11`, `1_1_1_1`, `4`, and `maintenance5` | Determines the arrangement and subset ownership of library leaves before linking. |
| Graphics pipeline subset | Vertex input interface, pre-rasterization shaders, fragment shader, fragment output interface | Determines which create-info state each library provides. |
| Link optimization | Disabled for `fast`; retained and enabled for `optimize` | Changes pipeline create flags while keeping the configuration matrix largely shared. |
| Pipeline layouts | Combined, vertex-only, fragment-only, independent sets, and layouts with null entries | Exercises stage-scoped layout compatibility during library creation and linking. |
| Null descriptor layout pattern | `1`, `11`, `01`, `10`, `101`, `1010`, `1001` | Encodes which layout-array positions are used by vertex or fragment shaders. |
| Miscellaneous execution mode | Layout, descriptor, dynamic rendering, shared fragment library, multiview, multisample, transform feedback, resource lifetime, rebind, and view-mask modes | Selects a narrow API contract with its own setup and result check. |
| Construction type within selected miscellaneous cases | `monolithic`, `fast_lib`, `optimized_lib`, `eso_unlinked_spriv` | Lets `primary_rebind` and `primary_rebind_diff_layouts` compare rebinding behavior across construction models. |
| Independent-sets construction type | `monolithic`, `fast_lib`, `optimized_lib` | Selects how the pseudorandom per-stage layouts are assembled: a single monolithic layout or library pieces whose union needs `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`. |
| Independent-sets stage combination | `vert`, `vert_frag`, `vert_geom`, `vert_geom_frag`, `vert_tesc_tese`, `vert_tesc_tese_frag`, `vert_tesc_tese_geom`, `vert_tesc_tese_geom_frag`, `mesh`, `mesh_frag`, `task_mesh`, `task_mesh_frag` | Determines which shader stages receive their own randomly generated descriptor sets. |
| Pseudorandom case seed | `case_0` through `case_9`, each with or without `_io_ssbo_first` | Selects the seeded descriptor content, binding counts, and set-index assignment per stage ([case generation](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995)). |

The configuration helper uses a `PipelineTreeConfiguration`: each entry supplies a parent index and shader count. [`getTestName()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L132-L152) serializes that shape into the leaf suffix, and [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5042-L5191) registers the generated matrix.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node registered below `graphics_library`.

### fast: fast-linked graphics pipeline library configurations

`fast` passes `optimize=false` to [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5042-L5191). For multi-node pipeline-tree shapes, the implementation creates partial libraries and links the root without the link-time optimization flags. The single-node `4` leaf instead creates a complete monolithic pipeline. `maintenance5` repeats that single-node shape with delayed shader creation to exercise the Maintenance5 shader-module behavior.

### optimize: link-time-optimized graphics pipeline library configurations

`optimize` passes `optimize=true` to the same configuration generator. [`calcPipelineCreateFlags()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L154-L170) adds `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` for a library and `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` for the final non-library pipeline. The rendered output must remain correct after this alternate linkage path.

### independent_sets_random: pseudorandom independent descriptor-set layouts

`independent_sets_random` is registered directly below `graphics_library` and populated by [`IndependentSets::createRandomTests()`](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995). For each of the three construction types (`monolithic`, `fast_lib`, `optimized_lib`), it registers twelve stage-combination groups — eight classic combinations built from vertex, tessellation, geometry, and fragment stages, and four mesh-pipeline combinations built from mesh, task, and fragment stages — and each stage group adds ten seeded cases (`case_0` through `case_9`), each with and without the `_io_ssbo_first` set-order variant, for 720 leaves in total. The case seed deterministically generates per-stage descriptor sets with pseudorandom descriptor types, binding counts, and set-index assignments. Every shader stage reads its own descriptors and copies their values into a shared storage-buffer set; the host then compares each descriptor's stored contents against the value the shader wrote, with a zero threshold, so any layout-incompatible set assignment produces a mismatch. Library construction types link stage-specific layouts whose union requires `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`, while the monolithic variant uses one general layout created with the same flag.

### misc: focused graphics pipeline library contracts

`misc` groups specialized leaves rather than one generated tree matrix. Its intermediate descendants cover:

- `independent_pipeline_layout_sets` and `bind_null_descriptor_set`, which exercise set-layout compatibility and null positions;
- `other`, which includes link-time comparison, dynamic-rendering create-info cases, shared fragment library behavior, device-index/view-index behavior, unusual multisample state, transform feedback, and destruction before linking;
- `non_graphics`, which checks shader-module create information for compute, ray tracing, and ray tracing libraries;
- `always_null_set_layout`, which validates used and unused sets across fast and optimized construction;
- `primary_rebind`, which tests a pipeline bind in the primary command buffer after secondary-command work, and `primary_rebind_diff_layouts`, which repeats the rebind with different descriptor-set counts between the bound pipelines; and
- `view_mask`, which checks view-mask state split across graphics pipeline libraries.

## Shader Analysis

The test family generates or loads vertex and fragment programs for its variants, but shader instruction behavior is not the primary behavioral axis. The configuration flow uses shaders to make stage-specific descriptor layouts and linked rendering observable. Specialized miscellaneous leaves generate their own programs where necessary, including the storage-buffer programs used by `always_null_set_layout` ([`AlwaysNullSetLayoutCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5320-L5389)). No single shader walkthrough represents the family without obscuring the more important library-creation and linkage choices.

## Runtime Execution and Result Checking

### Generated configuration flow

1. The test selects a tree configuration, an optimization choice, delayed shader creation, and the Maintenance5 choice. [`PipelineLibraryTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1273-L1293) requires the applicable graphics pipeline library support and selected extensions.
2. [`PipelineLibraryTestInstance::runTest()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L840-L1092) creates a render pass, vertex and descriptor buffers, descriptor layouts, descriptor sets, and pipeline layouts. It uses a combined layout or stage-specific layouts according to the subset coverage.
3. The implementation walks the tree from leaves to root. For each entry it adds state for the subsets that entry owns, supplies any child library handles through `VkPipelineLibraryCreateInfoKHR`, and creates a graphics pipeline. In multi-node cases, non-root entries retain `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`, while the root becomes executable after the complete subset mask is present. The single-node `fast.4` and `fast.maintenance5` cases have no child libraries; their root supplies all four subsets directly.
4. The test records a render pass, binds the vertex buffer, root pipeline, and two descriptor sets, then draws. It copies both color and depth images into host-visible buffers, submits the command buffer, waits, and invalidates the allocations.
5. [`verifyColorImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1094-L1122) compares a precise green, blue, and black region pattern. [`verifyDepthImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1124-L1163) compares the expected diagonal depth pattern.

### Pseudorandom independent-sets flow

[`Instance::iterate()`](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L942-L1878) in the independent-sets utility drives the `independent_sets_random` leaves. It builds the seeded per-stage descriptor sets plus a storage-buffer IO set, binds them according to the construction type, records a one-pixel draw, and reads the IO buffer back. Every descriptor holds a known value; each shader stage copies the values it reads into the IO buffer, and the host compares them with a zero threshold, reporting the first set, binding, and descriptor index that mismatch.

### Focused miscellaneous flow

[`PipelineLibraryMiscTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1498-L1543) dispatches each focused mode after shared render-target and command-buffer setup. Layout and descriptor modes render or write storage-buffer data, then compare it with expected values. [`verifyResult()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L2809-L2835) reports the first mismatched texel and expected color; another helper compares a generated reference image with a small tolerance. Some modes validate Vulkan creation or command behavior instead of the standard image:

- The dynamic-rendering cases vary absent, null-pointer, or intentionally invalid rendering create information.
- `destroy_resources_before_link_samplers_2` and `destroy_resources_before_link_samplers_3` validate library linkage after selected resources are destroyed.
- `primary_rebind` records secondary work, then checks a primary-command-buffer pipeline rebind. `primary_rebind_diff_layouts` extends this by giving the secondary-bound pipeline one descriptor-set layout and the primary-bound pipeline two, so the primary must rebind a pipeline whose layout declares a different set count after the secondary command buffer has bound the smaller layout ([`PrimaryRebindDiffLayoutsRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6037-L6376)).
- `view_mask` creates all four library subsets, links them, renders two layers with a view mask, and compares the layers with separate expected colors ([`viewMaskRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6412-L6647)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fast` | Incorrect creation or linkage of graphics pipeline libraries without link-time optimization. |
| `optimize` | Incorrect retention or use of link-time optimization information when linking libraries. |
| `independent_sets_random` | Incorrect combination of independently specified per-stage descriptor-set layouts, or a shader stage reading a descriptor through the wrong set assignment when the general layout is assembled with `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`. |
| `misc` | A focused pipeline-library contract failed, such as layout compatibility, null descriptor handling, creation-info validation, resource lifetime, device-group view selection, or pipeline rebinding. |

### Cause Analysis

#### Fast-linked library creation or linkage

**Possible failure symptoms:** A `fast` leaf fails pipeline creation, or its color/depth readback differs from the exact reference patterns.

**Possible implementation causes:** The implementation may assign state to the wrong graphics-pipeline-library subset, lose a child library handle while building the tree, or fail to combine the supplied subset flags into a complete root pipeline. The source creates leaf libraries first and merges their handles and flags toward the root, so a defect in that linkage path can leave the executable pipeline with missing or incompatible state.

#### Link-time optimization retention or final linking

**Possible failure symptoms:** An `optimize` leaf fails while its comparable fast-linked configuration succeeds, or the optimized root produces an incorrect color/depth pattern.

**Possible implementation causes:** The implementation may mishandle `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` on libraries or `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` on the final pipeline. A compiler or driver can also apply an optimization that changes shader-stage, layout, or fixed-function behavior during library linking. The test compares execution, not timing, so it localizes the problem to optimized linkage behavior rather than proving a particular compiler stage caused it.

#### Independent-set layout combination

**Possible failure symptoms:** An `independent_sets_random` leaf fails with a reported set, binding, and descriptor index whose IO-buffer value differs from the descriptor contents, while other leaves in the same stage group pass.

**Possible implementation causes:** The implementation may merge independently specified set layouts into the general pipeline layout incorrectly, assign a stage's descriptors to the wrong set index, or mishandle the set-index offset introduced by the `_io_ssbo_first` variant. Because the case seed fixes the descriptor contents, a mismatch pinpoints which set and binding the driver resolved incorrectly, which separates a layout-compatibility defect from a shader-code defect.

#### Focused pipeline-library contract

**Possible failure symptoms:** A `misc` leaf reports a creation error, an unexpected validation outcome, an incorrect texel or storage-buffer value, a wrong multiview layer color, or an incorrect pipeline-rebind result.

**Possible implementation causes:** Each descendant isolates a different API contract. Examples include incorrect independent-set layout compatibility, treating null layout entries as shader-accessible descriptors, losing dynamic-rendering information across libraries, retaining destroyed resources incorrectly, propagating the wrong device index into `gl_ViewIndex`, or preserving stale pipeline state across primary and secondary command buffers. The final image may identify the selected behavior but does not always isolate a single lower-level driver subsystem; source-level investigation should follow the failing leaf.

## Case Pruning

### Requirement-based pruning

The generated cases require `VK_KHR_pipeline_library`, except `fast.maintenance5`, whose support check requires `VK_KHR_maintenance5` instead. Generated cases with delayed shader creation or multiple tree nodes additionally require the `VK_EXT_graphics_pipeline_library` extension and its `graphicsPipelineLibrary` feature; therefore the single-node `fast.4` and Maintenance5 leaves do not have that requirement. The `PipelineLibraryMiscTestCase` cases require `VK_EXT_graphics_pipeline_library`. [`PipelineLibraryMiscTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L4401-L4460) adds requirements for selected modes: device-group creation and multiview for view-index tests, `graphicsPipelineLibraryFastLinking` for the fast independent-layout path, ray-tracing pipeline support for ray-tracing shader-module cases, `VK_KHR_pipeline_library` for the ray-tracing-library case, dynamic rendering for its create-info modes, mesh-shader plus clip/cull-distance support for the shared-fragment-library case, transform feedback for its focused case, and Maintenance4 for destroy-before-link cases. `always_null_set_layout` separately requires the selected library-construction prerequisites and fragment stores and atomics. `view_mask` requires graphics pipeline library, dynamic rendering, and multiview support. `primary_rebind` and `primary_rebind_diff_layouts` use construction-specific requirements plus dynamic rendering and `extendedDynamicState3ColorWriteMask`; consequently, their monolithic and shader-object leaves do not unconditionally require `VK_EXT_graphics_pipeline_library`. The `independent_sets_random` leaves require `VK_EXT_graphics_pipeline_library` for the library construction types but not for the monolithic subgroup; [`Case::checkSupport()`](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L353-L410) additionally skips leaves whose total set count exceeds `maxBoundDescriptorSets`, requires `VK_EXT_mesh_shader`, tessellation, or geometry support for stage combinations using those stages, and requires `VK_KHR_push_descriptor` when a generated set uses push descriptors. The complete family is absent from Vulkan SC builds.

### Design-based pruning

The configuration generator keeps a curated set of pipeline-tree shapes rather than every possible tree. It creates only shapes that exercise distinct subset and link relationships. The null-layout generator skips uninteresting arrangements, including same-set pairs and a two-set case with no gap. The page registers its own family only under `pipeline_library`, so the main generated suite does not duplicate the same family under every CTS construction root.

## Key Takeaways

- The configuration matrix validates execution after library linking, so a pass requires more than successful `vkCreateGraphicsPipelines` calls.
- `fast` and `optimize` differ in the link-time optimization contract, while their shared tree vocabulary lets failures be compared across those modes.
- `independent_sets_random` stresses layout compatibility directly: each seeded case generates different per-stage set layouts, so a driver defect surfaces as a specific set and binding mismatch rather than a general rendering failure.
- `misc` broadens coverage beyond rendering to layouts, null handles, dynamic rendering, resource lifetime, device groups, and command-buffer state.
- The 836 mustpass leaves are intentionally summarized by their first-level behavior; the parseable registration tree stays limited to the four direct intermediate nodes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration root | [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6651-L6895) | Registers `graphics_library`, `fast`, `optimize`, `independent_sets_random`, and all `misc` descendants. |
| Parent construction-root registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L213-L218) | Runs this implementation only under `pipeline_library`. |
| Tree configuration generator | [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5042-L5191) | Supplies the generated `fast` and `optimize` leaves. |
| Configuration execution and checking | [`PipelineLibraryTestInstance::runTest()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L840-L1092) | Creates, links, runs, copies, and validates the main pipeline-tree cases. |
| Main color/depth reference checks | [`verifyColorImage()` and `verifyDepthImage()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1094-L1163) | Define the expected rendering output. |
| Miscellaneous mode dispatch | [`PipelineLibraryMiscTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1498-L1543) | Selects focused `misc` behavior. |
| Independent-sets generation and execution | [`vktIndependentSetsUtil.cpp`](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995) | Registers and runs the pseudorandom per-stage layout cases for `independent_sets_random`. |
| Diff-layout rebind execution | [`PrimaryRebindDiffLayoutsRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6037-L6376) | Rebinds a two-set pipeline after secondary work bound a one-set pipeline. |
| Multiview view-mask execution | [`viewMaskRun()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6412-L6647) | Creates four libraries, links them, renders two layers, and compares them. |
| Mustpass coverage | [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L36654-L37489) | Lists the 836 executable `graphics_library` leaves. |
| Vulkan graphics pipeline rules | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-subsets-complete) | Defines graphics pipeline subsets and linked-state requirements. |
