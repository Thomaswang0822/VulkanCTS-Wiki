# Understanding Brief: graphics pipeline library tests

## One-Sentence Test Purpose

This test checks whether Vulkan graphics pipeline libraries can be created from partial pipeline state, linked into a complete graphics pipeline, and executed with the expected rendering and descriptor-layout behavior.

## Background Knowledge

### Graphics pipeline library subsets

`VK_EXT_graphics_pipeline_library` divides graphics pipeline state into four subsets: vertex input interface, pre-rasterization shaders, fragment shader, and fragment output interface. A test can create each subset as a pipeline library, then pass those library handles through `VkPipelineLibraryCreateInfoKHR` when creating a linked pipeline. The Vulkan pipeline rules describe which state belongs to each subset and how a complete pipeline is formed ([graphics pipeline subsets](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-subsets-complete)).

### Pipeline layout compatibility

A pipeline library can use a layout that exposes only the descriptor-set layouts needed by its shader stages. The final linked pipeline combines those partial layouts. The independent-set cases exercise `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`, while null-layout cases exercise `VK_NULL_HANDLE` entries in the layout array. These choices affect whether the library can link, not merely how descriptors are bound.

## One Concrete Example

A configuration such as `0_00_11_11` describes a pipeline tree. Each number identifies how many shader-library parts a tree level contains, and underscores separate levels. The implementation builds the leaves first, records their library handles and subset flags in the parent, and continues toward the root. The root is created without `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR` once the linked subsets provide the complete graphics pipeline.

The four subset flags are `VK_GRAPHICS_PIPELINE_LIBRARY_VERTEX_INPUT_INTERFACE_BIT_EXT`, `VK_GRAPHICS_PIPELINE_LIBRARY_PRE_RASTERIZATION_SHADERS_BIT_EXT`, `VK_GRAPHICS_PIPELINE_LIBRARY_FRAGMENT_SHADER_BIT_EXT`, and `VK_GRAPHICS_PIPELINE_LIBRARY_FRAGMENT_OUTPUT_INTERFACE_BIT_EXT`.

## End-to-End Test Flow

```text
[host] select a registered pipeline-tree configuration or miscellaneous mode
[host] require the extensions, features, limits, and construction properties for that case
[host] generate or load vertex and fragment shader programs
[host] create pipeline layouts, descriptor layouts, buffers, render targets, and pipeline-library create info
[host] create library leaves from selected graphics-pipeline subsets
[host] link library handles into parent pipelines and finally create the executable root pipeline
[host] record a draw, submit it, and wait for completion
[device] execute the linked graphics pipeline and write color/depth or storage-buffer results
[host] copy or invalidate results, compare pixels or values with the expected data, and decide pass/fail
```

Miscellaneous leaves use the same setup where applicable, but some validate creation-time behavior or command-buffer pipeline rebinding instead of the main rendered image.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The configuration tests generate vertex and fragment shader sources through `initPrograms`. The shaders read optional descriptor-buffer values and produce the color/depth patterns checked by `verifyColorImage` and `verifyDepthImage`.
- The tree configuration is converted into test names by `getTestName`; the registered names are the generated strings listed in `pipeline-library.txt`.
- Miscellaneous modes generate shaders for null descriptor layouts, mesh-shader fragment-library sharing, device-group view-index behavior, shader-module create-info checks, and primary-command-buffer rebinding.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read by vertex input | no | Supplies geometry for the configuration render. |
| Z-coordinate and palette buffers | yes | yes | read by vertex and fragment shaders | no | Distinguish descriptor layouts and make stage-specific layouts observable. |
| Color image and host-visible copy buffer | yes | yes | color attachment write, then transfer write | yes | `verifyColorImage` checks the expected green, blue, and black regions. |
| Depth image and host-visible copy buffer | yes | yes | depth-test/write, then transfer write | yes | `verifyDepthImage` reconstructs the expected depth pattern. |
| Descriptor set layouts and descriptor sets | yes | yes | shader reads | indirectly | Exercise compatible, independent, and null set-layout combinations. |
| Pipeline libraries and linked root pipeline | yes | bound for the draw | execute graphics state | no | The object-lifetime and linkage behavior under test. |

## What Is Checked

The configuration tests render a 16 by 16 image. The color comparison expects green in the upper-left three-quarters, blue in the lower-left three-quarters, and black in the rightmost quarter. The depth comparison converts the observed depth to an 8-bit reference and checks the diagonal and right-hand regions with an exact integer comparison.

Miscellaneous image tests compare selected texels or reference images with a small tolerance. `always_null_set_layout` writes stage-derived values to a storage buffer and checks those values after synchronization. Creation and shader-module cases pass when the intended Vulkan object creation succeeds or produces the expected validation result. `primary_rebind` checks the result after rebinding the pipeline in a primary command buffer following secondary-command execution.

## Behavior Parameter Identification

> **Behavior parameter:** registered intermediate test family
>
> **Candidate values:** `fast`, `optimize`, `misc`

The main behavioral split is the first-level child under `graphics_library`. `fast` and `optimize` use the same pipeline-tree matrix with different link optimization flags. `misc` contains focused linkage, layout, creation, execution, and lifetime checks.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fast` | Incorrect creation or linkage of graphics pipeline libraries without link-time optimization. |
| `optimize` | Incorrect retention or use of link-time optimization information when linking libraries. |
| `misc` | A focused pipeline-library contract failed, such as layout compatibility, null descriptor handling, creation-info validation, resource lifetime, device-group view selection, or pipeline rebinding. |

## Important Variations and Special Cases

- All leaves are registered under `pipeline.pipeline_library.graphics_library`, which is created only for `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`; the `fast` leaves explicitly exercise fast-linked library construction inside that group.
- The `maintenance5` fast leaf changes pipeline-library creation behavior to use the Maintenance5 path rather than the independent-set flag path.
- Null descriptor names encode set-layout presence. For example, `1010` means that the first and third positions are used while the other positions are null.
- The source also registers non-graphics shader-module cases for compute, ray-tracing, and ray-tracing-library pipeline create information. The ray-tracing-library case requires `VK_KHR_pipeline_library`.
- `view_mask` creates four graphics libraries with view masks and checks that the fragment-output library receives the correct view-mask state.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Registration | [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6246-L6462) | Defines `graphics_library`, its three direct children, and all miscellaneous descendants. |
| Pipeline-tree generation | [`addPipelineLibraryConfigurationsTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L5046-L5280) | Defines the `fast` and `optimize` configuration matrix. |
| Library creation and linking | [`PipelineLibraryTestInstance::runTest()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L837-L1089) | Builds library leaves, links them toward the root, draws, and reads back results. |
| Miscellaneous dispatch | [`PipelineLibraryMiscTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1495-L1540) | Selects the focused behavior implementation for each `misc` leaf. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L218) | Attaches this implementation under the pipeline-library construction root. |
| Mustpass | [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L1-L112) | Contains 112 registered `graphics_library` leaves: 15 `fast`, 13 `optimize`, and 84 `misc`. |

## Questions / Risk Points for User Audit

- Is the distinction between the generated pipeline-tree leaves and the focused `misc` leaves clear?
- Should the final page include a separate representative walkthrough for the null descriptor and view-mask cases?
- Are the layout compatibility consequences of independent sets explained at the right depth?

## Conversion Notes for Final Wiki Rewrite

Carry the `fast`/`optimize`/`misc` behavioral axis into the final page. Keep the pipeline-tree example as the main execution explanation. Copy the failure mapping table into `## Failure Meaning`, then write fresh cause analysis for each value. Keep the detailed leaf inventory in the mustpass reference rather than expanding the registration tree.
