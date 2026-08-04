## Overview

**Core question:** Can CTS release pipeline-layout state at the selected point in the pipeline-construction lifetime without breaking the surrounding command and object-lifetime path?

- This page documents the `pipeline.early_destroy` test family implemented by [`vktPipelineEarlyDestroyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp).
- The family creates graphics or compute pipeline wrappers, selects cache and layout-release options, and destroys the `PipelineLayoutWrapper` before the relevant wrapper scope ends when a `destroy_layout` leaf requests it.
- The source's observable submitted work in `destroy_layout` leaves clears an image and copies it to a host-visible buffer. It does not bind or execute the constructed pipeline in that command buffer.
- The family is registered under seven pipeline-construction roots. Its mustpass coverage is split across their files.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Vulkan object lifetime.** Applications manage Vulkan object and memory lifetimes. An object passed to a recorded command may be accessed while the command buffer is pending, and the application must not destroy it while that access is possible. See [Object Lifetime](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L272-L320).
- **Pipeline layouts.** A pipeline layout supplies descriptor-set and push-constant layout information at pipeline construction and binding time. This source explicitly releases the `PipelineLayoutWrapper` through `pipelineLayout.destroy()` in selected leaves.
- **Pipeline destruction is separate.** `vkDestroyPipeline` requires submitted commands that refer to the pipeline to have completed. The CTS source keeps its pipeline wrapper in scope through `submitCommandsAndWait()` in the submitted path; it does not call in-flight pipeline destruction. See [vkDestroyPipeline validity](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7910-L7937).

## Registration Hierarchy

```text
pipeline.monolithic.early_destroy
├── cache
├── cache_compute
├── cache_destroy_layout
├── cache_destroy_layout_compute
├── no_cache
├── no_cache_compute
├── no_cache_destroy_layout
├── no_cache_destroy_layout_compute
└── no_cache_destroy_layout_maintenance5
```

The same test family is registered beneath `pipeline.shader_object_unlinked_spirv`, which has the same nine leaves. Five graphics-only leaves occur beneath `pipeline.pipeline_library`, `pipeline.fast_linked_library`, `pipeline.shader_object_unlinked_binary`, `pipeline.shader_object_linked_spirv`, and `pipeline.shader_object_linked_binary`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction root | `monolithic`, `shader_object_unlinked_spirv`, `pipeline_library`, `fast_linked_library`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, `shader_object_linked_binary` | Selects the CTS wrapper construction route. | [registration](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L496-L550) |
| Pipeline cache | `no_cache`, `cache` | Selects `VK_NULL_HANDLE` or the locally created pipeline cache passed to `buildPipeline()`. | [cache selection](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L172-L189) |
| Layout release | absent or `_destroy_layout` | Selects whether `pipelineLayout.destroy()` runs before command recording in the wrapper scope. | [layout release](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L190-L320) |
| Pipeline kind | graphics, `_compute` | Selects graphics or compute wrapper setup. Compute is registered only for monolithic and unlinked-SPIR-V shader-object construction. | [compatibility predicate](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L498-L529) |
| maintenance5 | absent or `_maintenance5` | The special graphics-only leaf requires `VK_KHR_maintenance5` and uses flags2 pipeline creation. | [special leaf](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L297-L300) and [registration](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L531-L541) |

Mustpass contains 9 leaves in `monolithic/monolithic.txt` and 9 in `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`. Each of `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-unlinked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-linked-binary.txt` contains 5. The split scope totals 43 leaves.

## Behavior Parameters

The primary behavioral axis is the test case leaf. Cache selection and pipeline kind alter the construction route, while `destroy_layout` selects the source's explicit layout-release and observable clear/copy sequence.

### cache: graphics construction with a pipeline cache

This leaf follows the same no-layout-release path as `no_cache` but passes the locally created `VkPipelineCache` to pipeline construction. It isolates cache participation from layout release.

### cache_compute: compute construction with a pipeline cache

This leaf adds cache participation to the compute setup path. It is registered only where `graphicsToComputeConstructionType()` accepts the selected construction root.

### cache_destroy_layout: graphics layout release with a cache

This leaf combines the graphics layout-release path with cached pipeline construction. Its submitted work and readback check match `no_cache_destroy_layout`.

### cache_destroy_layout_compute: compute layout release with a cache

This leaf combines the compatible compute route, cached construction, explicit layout release, and the clear/copy readback sequence.

### no_cache: graphics construction without a pipeline cache

This leaf builds a graphics pipeline with `VK_NULL_HANDLE` as the cache. It does not release the layout early and does not submit the clear/copy sequence. The instance passes if the setup and scope exit complete without a CTS failure or crash.

### no_cache_compute: compute construction without a cache

This leaf builds a compute wrapper and its storage-image descriptor layout without cache participation. It is available only under construction roots accepted by `compCompatible`; it does not take the layout-release clear/copy path.

### no_cache_destroy_layout: graphics layout release without a cache

This leaf calls `pipelineLayout.destroy()` while the graphics wrapper remains in scope. It then begins a render pass, clears the target attachment, ends the render pass, copies the target image to the readback buffer, submits, waits, and checks the clear color when the pixel loop is enabled.

### no_cache_destroy_layout_compute: compute layout release without a cache

This leaf releases the compute pipeline layout before it records the image clear and readback copy. The source configures a storage-image descriptor set for the compute wrapper, but the submitted observable command sequence still clears and copies the image rather than dispatching the generated compute shader.

### no_cache_destroy_layout_maintenance5: maintenance5 graphics layout release

This graphics-only leaf has no cache, releases the layout, and requires `VK_KHR_maintenance5`. The graphics wrapper uses `VK_PIPELINE_CREATE_2_DISABLE_OPTIMIZATION_BIT_KHR` when `useMaintenance5` is set.

## Shader Analysis

The source creates a simple `comp` shader that stores green into a storage image and a `color_vert` shader that supplies a triangle position. They establish graphics and compute pipeline construction inputs, but neither runs in the submitted `destroy_layout` command sequence: the graphics pipeline has rasterizer discard and no fragment stage, while the command buffer clears and copies the image without a compute dispatch. Shader behavior is therefore not the primary tested mechanism.

## Runtime Execution and Result Checking

- `EarlyDestroyTestInstance::iterate()` creates a 32x32 `VK_FORMAT_R8G8B8A8_UNORM` target image and a host-visible transfer-destination readback buffer.
- Compute setup also creates a storage-image descriptor-set layout, descriptor pool, and descriptor set. Graphics setup creates a render pass and framebuffer plus a graphics wrapper configured with rasterizer discard.
- The instance creates a pipeline cache regardless of cache selection, then passes either that handle or `VK_NULL_HANDLE` to `buildPipeline()`.
- It loops once for ordinary leaves and three times when `destroyLayout` is true. Each iteration creates a new `PipelineLayoutWrapper` and pipeline wrapper.
- In the layout-release path, `pipelineLayout.destroy()` runs before command recording. The graphics command path begins and ends a render pass, then calls `cmdClearAttachments`; the compute path transitions and clears the image with `cmdClearColorImage`.
- Both layout-release paths copy the image to the buffer, call `submitCommandsAndWait()`, reset the command buffer, and invalidate the host allocation. The host compares every pixel with `{0.2, 0.6, 0.8, 1.0}` except in the Vulkan SC subprocess condition compiled out by the source.
- Pipeline wrappers leave scope after the wait. The function returns pass when no prior check failed or crash occurred.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_cache`, `cache`, `no_cache_compute`, `cache_compute` | Pipeline construction or wrapper lifetime handling fails before the no-crash return; these leaves do not submit the clear/copy sequence. |
| `no_cache_destroy_layout`, `cache_destroy_layout` | Releasing the graphics pipeline layout before the clear/copy sequence, pipeline-wrapper bookkeeping, render-pass clear, transfer, or readback visibility fails. |
| `no_cache_destroy_layout_compute`, `cache_destroy_layout_compute` | The compute construction route or descriptor-layout lifetime handling fails; the submitted observable work is still a transfer clear and copy, not a compute dispatch. |
| `no_cache_destroy_layout_maintenance5` | `VK_KHR_maintenance5` support, the flags2 construction path, layout release, or the subsequent graphics clear/copy path fails. |

### Cause Analysis

#### Pipeline construction or wrapper lifetime handling

**Possible failure symptoms:** A non-`destroy_layout` leaf fails by reporting a CTS error, crashing, or losing the device before `iterate()` returns pass. These leaves do not offer a pixel comparison that isolates an execution result.

**Possible implementation causes:** Source-level investigation is needed to localize failures among construction wrappers, cache handling, construction-type support, or object cleanup. The source only establishes that pipeline construction and wrapper scope must complete for these leaves.

#### Layout release and observable command path

**Possible failure symptoms:** A `destroy_layout` leaf can crash or report `Pixel value mismatch after clear.` The readback value differs from `{0.2, 0.6, 0.8, 1.0}` when the source executes the comparison.

**Possible implementation causes:** The failure can arise from CTS wrapper bookkeeping around the released layout, render-pass or image-clear execution, layout transitions, transfer-to-host visibility, or host readback. The final image cannot isolate those paths because the command buffer does not bind the constructed pipeline after the release.

#### Compute construction or descriptor-layout handling

**Possible failure symptoms:** A compatible compute leaf can fail during wrapper setup, layout release, submission, or the same clear/copy readback check used by other layout-release leaves.

**Possible implementation causes:** The compute route adds descriptor-set-layout and storage-image setup before construction. A source-level investigation must distinguish that setup from the common clear/copy path because this instance does not dispatch `comp`.

#### maintenance5 construction path

**Possible failure symptoms:** The maintenance5 leaf can report unsupported functionality, fail during graphics construction, crash, or produce the clear/readback mismatch.

**Possible implementation causes:** The source requires `VK_KHR_maintenance5` and changes the graphics wrapper's create flags2 setting. A failure may involve extension support or flags2 handling, but the same common layout-release and image-operation paths remain possible causes.

## Case Pruning

### Requirement-based pruning

`checkSupport()` requires `VK_KHR_maintenance5` for the special maintenance5 leaf. It calls `checkPipelineConstructionRequirements()` for graphics and `checkShaderObjectRequirements()` for compute. A device that cannot support the selected route does not run that test case.

### Design-based pruning

The registration loop produces cache and layout-release combinations for graphics under every construction root. It skips compute when the root is not `MONOLITHIC` or `SHADER_OBJECT_UNLINKED_SPIRV`, because `compCompatible` limits the compute-wrapper mapping. The maintenance5 leaf is a separate graphics-only case with no cache, so it does not multiply into the general matrix.

## Key Takeaways

- The source documents early release of `PipelineLayoutWrapper` in selected leaves, while it keeps pipeline wrappers alive until after the submitted clear/copy work completes.
- The submitted `destroy_layout` work validates image clear and readback behavior after layout release; it does not execute the constructed graphics or compute pipeline.
- Cache selection and construction roots broaden wrapper coverage. Compute coverage exists only under monolithic and unlinked-SPIR-V shader-object roots.
- The 43-leaf mustpass scope is split across seven construction-specific files, so the page reports file-scoped coverage rather than a single monolithic list.

## Source Reference Appendix

| Evidence | Source reference | Role |
|----------|------------------|------|
| Test implementation | [`EarlyDestroyTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L91-L415) | Creates resources, releases the layout, records operations, waits, and checks pixels. |
| Program setup | [`EarlyDestroyTestCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L434-L471) | Defines `comp`, `color_vert`, and `color_frag`. |
| Support checks | [`EarlyDestroyTestCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L478-L494) | Gates maintenance5 and construction routes. |
| Registration | [`addEarlyDestroyTests`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L496-L542) | Defines leaf names, compatibility pruning, and the maintenance5 leaf. |
| Family entry point | [`createEarlyDestroyTests`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L546-L550) | Registers the `early_destroy` test family. |
| Object lifetime rules | [Vulkan Fundamentals](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L272-L320) | Defines command access and application object-lifetime obligations. |
| Pipeline destruction rule | [Vulkan Pipelines](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7910-L7937) | Defines `vkDestroyPipeline` submitted-command completion validity. |
| Monolithic mustpass | [`monolithic/monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) | Contains 9 early-destroy leaves. |
| Unlinked-SPIR-V mustpass | [`shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) | Contains 9 early-destroy leaves. |
| Other split mustpass files | [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), [`fast-linked-library.txt`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt), [`shader-object-unlinked-binary.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-unlinked-binary.txt), [`shader-object-linked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-linked-spirv.txt), [`shader-object-linked-binary.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-linked-binary.txt) | Each contains 5 graphics early-destroy leaves. |
