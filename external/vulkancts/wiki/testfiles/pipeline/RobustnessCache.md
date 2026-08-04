## Overview

**Core question:** Can cache-backed graphics and compute pipelines execute out-of-bounds accesses with the requested robustness state, and do `robustness2` pipelines return the values checked by the test?

- [`vktPipelineRobustnessCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L279-L860) implements the `pipeline.monolithic.pipeline_cache` family and its equivalent pipeline-library construction roots.
- The test creates a normal pipeline and a second pipeline with `VkPipelineRobustnessCreateInfoEXT` chained into pipeline creation, using the same `VkPipelineCache`.
- It executes both paths and copies the resulting 32×32 image to host memory. It always checks the initialized result, but checks the out-of-bounds pixel values only for `robustness2`.
- The source covers `robustness` behavior from `VK_EXT_pipeline_robustness` and `robustness2` behavior from `VK_KHR_robustness2` or `VK_EXT_robustness2`.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A [`VkPipelineCache`](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) stores implementation-managed data that can be reused during pipeline creation. The cache is opaque; this test observes the behavior of pipelines created with it rather than interpreting cache bytes.
- [`VkPipelineRobustnessCreateInfoEXT`](../../../../vulkan-docs/src/chapters/pipelines.adoc#VkPipelineRobustnessCreateInfo) selects out-of-bounds behavior for storage buffers, uniform buffers, vertex inputs, or images. Its scope can cover a whole pipeline when chained to the pipeline create info.
- The `pipelineRobustness` feature enables per-pipeline robustness selection. The `robustBufferAccess2` and `robustImageAccess2` features enable the stronger robustness2 guarantees used by the `robustness2` family.

## Registration Hierarchy

```text
pipeline.monolithic.pipeline_cache
├── robustness
└── robustness2
```

The source creates the same two direct test families for each supported non-shader-object pipeline construction type. Under each family it registers `storage`, `uniform`, `vertex_input`, and `image`. For monolithic construction only, `storage`, `uniform`, and `image` also receive `_compute` leaves. The current `vk-default` mustpass files contain 14 monolithic leaves in `pipeline/monolithic/monolithic.txt`, 8 pipeline-library leaves in `pipeline/pipeline-library.txt`, and 8 fast-linked-library leaves in `pipeline/fast-linked-library.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline construction type | monolithic, pipeline library, fast-linked library | Selects the pipeline wrapper and construction path. | [`createTests()` registration](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224-L263) |
| Robustness family | `robustness`, `robustness2` | Selects the robustness enum values and feature requirements. | [`robustnessTests`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L819-L827) |
| Resource type | `storage`, `uniform`, `vertex_input`, `image` | Selects the out-of-bounds access being observed. | [`typeTests`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L828-L837) |
| Execution path | graphics, monolithic compute | Selects draw or dispatch. Compute is omitted for `vertex_input` and non-monolithic construction. | [`createPipelineRobustnessCacheTests()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L839-L855) |
| Tested robustness value | `ROBUST_BUFFER_ACCESS_EXT`, `ROBUST_IMAGE_ACCESS_EXT`, `ROBUST_BUFFER_ACCESS_2_EXT`, `ROBUST_IMAGE_ACCESS_2_EXT` | Configures the matching member of `VkPipelineRobustnessCreateInfoEXT`. | [`pipelineRobustnessInfo` setup](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L454-L479) |

## Behavior Parameters

The primary behavioral axis is the robustness family combined with the resource type. The four resource types have distinct access mechanisms, so a result in one family does not establish that the others are correct.

### `robustness`: EXT pipeline robustness behavior

The test requires `VK_EXT_pipeline_robustness` and the `pipelineRobustness` feature. It sets the relevant buffer member to `VK_PIPELINE_ROBUSTNESS_BUFFER_BEHAVIOR_ROBUST_BUFFER_ACCESS_EXT` for `storage`, `uniform`, or `vertex_input`, and sets `images` to `VK_PIPELINE_ROBUSTNESS_IMAGE_BEHAVIOR_ROBUST_IMAGE_ACCESS_EXT` for `image`.

### `robustness2`: robustness2 behavior through pipeline robustness state

The test additionally requires either `VK_KHR_robustness2` or `VK_EXT_robustness2`. Buffer cases require `robustBufferAccess2`; the image case requires `robustImageAccess2`. The corresponding `_2_EXT` behavior values are placed in the pipeline robustness structure.

### Resource type: storage buffer

The shader reads `values[index]` from a storage buffer. The normal run uses index zero. The robustness run uses index `999`, beyond the four initialized float values.

### Resource type: uniform buffer

The shader reads `values[index]` from a `std140` uniform buffer. The normal run uses index zero; the robustness run uses index `999` in the 1000-element shader declaration, exercising the source's selected invalid-index path and resource-specific robustness setup.

### Resource type: vertex input

The graphics vertex shader reads `in_values[index]` from a 16-element vertex-input array. The normal run uses index zero and the robustness run uses index `15`, with the vertex buffer bound as a vertex-input source.

### Resource type: image

The shader reads `imageLoad(tex, ivec2(index, 0))` from a one-pixel storage image. The normal run uses index zero; the robustness run uses index `999`. The output predicate accepts only zero or one for individual components in the out-of-bounds image case.

## Shader Analysis

The generated shaders are small access fixtures, not the subject of the test. Compute cases use a local size of 8×8 and write the selected buffer or image value to a storage output image. Graphics cases use a vertex shader that forms a triangle strip and a fragment shader that reads the selected resource and writes the value to a color attachment. The test does not require a shader/SPIR-V walkthrough because it checks the effect of pipeline robustness and cache-backed creation through image output, not shader compilation details.

## Runtime Execution and Result Checking

- [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L657-L707) requires `VK_EXT_pipeline_robustness`, checks `pipelineRobustness`, and for `robustness2` checks the appropriate robustness2 extension and feature. Graphics paths also check pipeline-construction requirements; compute paths require a compute queue.
- [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L279-L452) creates the command pool and command buffer, input and index buffers, the one-pixel input image and sampler, the 32×32 render target, descriptor set, pipeline layout, and an empty pipeline cache. Host writes initialize the input values to `0.5` and the index to zero, then flush the allocations.
- For compute, the source creates a storage output image and dispatches the compute pipeline. For graphics, it creates a render pass and framebuffer, binds descriptors and the selected pipeline, draws four vertices, and copies the render target to the output buffer. Each submission is waited on before the next host-side operation.
- The normal pipeline is built without the robustness pNext chain and executed first. [`verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L246-L277) invalidates the host allocation and requires every pixel to equal `tcu::Vec4(0.5f)`.
- The source changes the index to `15` for `VERTEX_INPUT` or `999` otherwise, flushes it, and executes the robust pipeline built with the selected `VkPipelineRobustnessCreateInfoEXT`.
- For `ROBUSTNESS_2`, `verifyImage()` requires zero for buffer out-of-bounds results. For the `IMAGE` case it accepts each component only when it is `0.0f` or `1.0f`, which is the source's explicit predicate. The source does not make a second `verifyImage()` call for `ROBUSTNESS`; those leaves still execute the robust pipeline after the index update, but their pass condition is successful execution rather than a second final-pixel comparison.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `robustness.storage` | The cache-backed robust pipeline fails during creation or execution on the storage-buffer path. The test does not compare its out-of-bounds pixel values. |
| `robustness.uniform` | The cache-backed robust pipeline fails during creation or execution on the uniform-buffer path. The test does not compare its out-of-bounds pixel values. |
| `robustness.vertex_input` | The cache-backed robust pipeline fails during creation or execution on the vertex-input path. The test does not compare its out-of-bounds pixel values. |
| `robustness.image` | The cache-backed robust pipeline fails during creation or execution on the storage-image path. The test does not compare its out-of-bounds pixel values. |
| `robustness2.storage` | Robustness2 storage-buffer behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.uniform` | Robustness2 uniform-buffer behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.vertex_input` | Robustness2 vertex-input behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.image` | Robustness2 image behavior or its feature/extension integration is mishandled when using a pipeline cache. |

### Cause Analysis

#### Pipeline cache changes the selected robustness behavior

**Possible failure symptoms:** A `robustness2` pipeline produces pixels outside its accepted set after the normal pipeline produced the expected `0.5` image, or a `robustness` pipeline fails during creation or execution. A failure may occur only for one pipeline construction path.

**Possible implementation causes:** The implementation may associate cache data with pipeline state that does not include the effective `VkPipelineRobustnessCreateInfoEXT`, or it may reuse an executable whose robustness state does not match the requested create info. The CTS result cannot distinguish cache-key construction from later pipeline execution without driver-level investigation.

#### Buffer robustness does not handle an out-of-bounds index

**Possible failure symptoms:** A `robustness2.storage`, `robustness2.uniform`, or `robustness2.vertex_input` case produces a non-zero value after the invalid index is installed, or the normal in-bounds comparison fails first. The corresponding `robustness` leaves have no out-of-bounds pixel comparison.

**Possible implementation causes:** The implementation may apply the wrong robustness behavior member, fail to propagate pipeline-level state to the relevant shader access, or mishandle the buffer/vertex-input bounds check. The [pipeline robustness contract](../../../../vulkan-docs/src/chapters/pipelines.adoc#VkPipelineRobustnessCreateInfo) separates storage buffers, uniform buffers, and vertex inputs, so a failure is localized to the selected resource path but not to a specific compiler or hardware stage.

#### Image robustness does not produce an allowed out-of-bounds value

**Possible failure symptoms:** A `robustness2.image` output component is neither `0.0f` nor `1.0f`, or the normal image access does not reproduce the initialized value.

**Possible implementation causes:** The implementation may not apply the requested image robustness value, may use the wrong `robustImageAccess2` feature state, or may mishandle the out-of-range coordinate in the storage-image access path. The source predicate intentionally accepts either zero or one for out-of-bounds image components, so a failure means the result is outside that allowed set rather than identifying one exact implementation mechanism.

#### Robustness feature or extension integration is invalid

**Possible failure symptoms:** A case is reported unsupported when its required feature is advertised, or pipeline creation fails after support checks pass.

**Possible implementation causes:** The device may expose inconsistent feature and extension behavior, or the implementation may accept a robustness enum value without correctly enabling the corresponding `pipelineRobustness`, `robustBufferAccess2`, or `robustImageAccess2` feature. Vulkan valid-usage rules require device-feature support before selecting the corresponding robustness values.

## Case Pruning

### Requirement-based pruning

`checkSupport()` skips the family unless `VK_EXT_pipeline_robustness` and `pipelineRobustness` are available. `robustness2` additionally needs `VK_KHR_robustness2` or `VK_EXT_robustness2`; buffer cases need `robustBufferAccess2`, while the image case needs `robustImageAccess2`. Graphics construction requirements and a compute queue are checked on their respective paths.

### Design-based pruning

The source excludes the family from Vulkan SC and from shader-object variants. Pipeline-library and fast-linked-library roots are included because the test is about robustness state attached during supported pipeline construction, while compute variants are not multiplied across construction types. `vertex_input` has no compute variant because compute pipelines have no vertex-input stage. The test uses one resource type and one invalid-index pattern per leaf instead of multiplying the matrix by shader arithmetic, since the output is only an observation vehicle for the access behavior.

## Key Takeaways

- The test combines an opaque pipeline cache with explicit per-pipeline robustness state. It validates out-of-bounds pixel values for `robustness2`; `robustness` provides creation-and-execution coverage only after the normal-image check.
- Its behavioral coverage is the `robustness` versus `robustness2` family crossed with storage, uniform, vertex-input, and image accesses.
- The normal run establishes the initialized `0.5` result before the invalid-index run, separating setup or cache failures from robustness failures.
- Monolithic registration adds compute leaves for storage, uniform, and image; pipeline-library and fast-linked-library coverage is graphics-only.
- A `robustness2` output failure identifies a mismatch in cache-aware robustness state or the selected resource access path. A `robustness` failure is less localized because that family has no second image comparison. Neither result by itself reveals an internal cache-key or compiler defect.

## Source Reference Appendix

| Entry point or contract | Link | Why it matters |
|---|---|---|
| Registration matrix | [`createPipelineRobustnessCacheTests()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L813-L860) | Defines family, resource, construction, and compute coverage. |
| Feature and extension checks | [`PipelineCacheTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L657-L708) | Defines support and skip conditions. |
| Runtime setup and validation | [`PipelineCacheTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L279-L625) | Builds both pipelines, executes them, changes the index, and checks output. |
| Pixel predicate | [`verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L246-L277) | Defines exact host-side comparison behavior. |
| Program generation | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L710-L809) | Shows the selected resource access in graphics and compute shaders. |
| Pipeline robustness specification | [Pipeline robustness](../../../../vulkan-docs/src/chapters/pipelines.adoc#VkPipelineRobustnessCreateInfo) | Defines robustness members, scope, and valid-usage constraints. |
| Pipeline robustness feature specification | [Pipeline robustness feature](../../../../vulkan-docs/src/chapters/features.adoc#features-pipelineRobustness) | Defines per-pipeline robustness enablement. |
| Robustness2 feature specification | [Robustness2 features](../../../../vulkan-docs/src/chapters/features.adoc#features-robustBufferAccess2) | Defines robustness2 buffer and image guarantees. |
| Pipeline cache specification | [Pipeline Cache](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) | Defines cache reuse during pipeline creation. |
