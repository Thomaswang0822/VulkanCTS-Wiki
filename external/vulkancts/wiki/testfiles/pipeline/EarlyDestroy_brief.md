# Understanding Brief: pipeline early_destroy

## One-Sentence Test Purpose

This test checks whether pipeline construction variants can release a `VkPipelineLayout` before later command-buffer work completes, while pipeline wrappers and cache choices follow their intended lifetime paths.

## Background Knowledge

### Object lifetime and command-buffer references

An application owns Vulkan object lifetimes. Objects passed to recorded commands may be accessed while the command buffer is pending, and an application must not destroy an object while it is accessed. The specification separately requires submitted commands that refer to a pipeline to complete before `vkDestroyPipeline`.

Why it matters here:
- `PipelineLayoutWrapper::destroy()` makes the layout-lifetime case explicit.
- The source keeps the pipeline wrapper alive through `submitCommandsAndWait()`, so the checked early-destruction event is the layout release, not an in-flight `vkDestroyPipeline` call.

### Pipeline construction variants

`PipelineConstructionType` selects the construction route used by CTS wrappers. The same leaf names appear under several construction roots. Compute leaves appear only for monolithic and unlinked-SPIR-V shader-object construction because the registration function marks those two routes as compatible.

## One Concrete Example

Consider `pipeline.monolithic.early_destroy.no_cache_destroy_layout`:

1. The test creates a 32x32 `VK_FORMAT_R8G8B8A8_UNORM` image, a host-visible readback buffer, and a graphics pipeline with a rasterizer-discard configuration.
2. It calls `pipelineLayout.destroy()` while the pipeline wrapper remains in scope.
3. It records a render-pass clear, copies the image to the readback buffer, submits, waits, and checks that every pixel equals `{0.2, 0.6, 0.8, 1.0}` when the build enables the pixel loop.
4. The pipeline wrapper leaves scope only after the wait. The submitted commands in this path clear and copy the image; they do not bind or draw with that pipeline.

The example tests host-object lifetime handling around pipeline setup rather than a rendered pipeline result.

## End-to-End Test Flow

```text
[host] choose construction type, cache option, layout-destruction option, and graphics or compute mode
[host] create a target image, readback buffer, optional compute descriptor objects, and a pipeline cache
[host] create a pipeline layout and a graphics or compute pipeline wrapper
[host] optionally destroy the pipeline layout while the pipeline wrapper remains alive
[host] for layout-destruction variants, record a clear, copy the target image to the buffer, submit, and wait
[host] invalidate the host-visible readback allocation and compare pixels when the check is compiled in
[host] leave the pipeline-wrapper scope after the wait; return pass if no failure or crash occurred
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `comp` writes opaque green to a storage image for compute construction.
- `color_vert` supplies a fullscreen triangle position, but the graphics pipeline enables rasterizer discard and has no fragment stage. The layout-destruction graphics path clears the attachment with a command rather than drawing with this pipeline.
- CTS wrapper objects build the graphics or compute pipeline under the selected `PipelineConstructionType`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| target image | yes | yes | clear writes it; copy reads it | indirectly | Provides an observable clear result for layout-destruction paths. |
| readback buffer | yes | yes | transfer copy writes it | yes | Holds the copied image data. |
| storage-image descriptor set | yes, compute only | yes | compute pipeline may use it | no | Supplies compute-pipeline layout state. |
| pipeline layout | yes | used to build pipeline | no direct device write | no | The object explicitly released by selected leaves. |
| pipeline cache | yes | passed at build time when selected | no direct device write | no | Distinguishes cache and no-cache construction paths. |

## What Is Checked

- The test returns pass if execution completes without a CTS failure or crash.
- In `destroy_layout` paths, the code submits a clear and image-to-buffer copy after `pipelineLayout.destroy()`.
- In builds that execute the pixel loop, every readback pixel must equal the clear color. The source excludes that loop for Vulkan SC subprocess execution.
- The source does not bind either pipeline in the submitted layout-destruction command buffer, and it releases pipeline wrappers after the wait. The result does not directly validate execution through a destroyed pipeline.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `no_cache`, `no_cache_destroy_layout`, `cache`, `cache_destroy_layout`, `no_cache_compute`, `no_cache_destroy_layout_compute`, `cache_compute`, `cache_destroy_layout_compute`, `no_cache_destroy_layout_maintenance5`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_cache`, `cache`, `no_cache_compute`, `cache_compute` | Pipeline construction or wrapper lifetime handling fails before the no-crash return; these leaves do not submit the clear/copy sequence. |
| `no_cache_destroy_layout`, `cache_destroy_layout` | Releasing the graphics pipeline layout before the clear/copy sequence, pipeline-wrapper bookkeeping, render-pass clear, transfer, or readback visibility fails. |
| `no_cache_destroy_layout_compute`, `cache_destroy_layout_compute` | The compute construction route or descriptor-layout lifetime handling fails; the submitted observable work is still a transfer clear and copy, not a compute dispatch. |
| `no_cache_destroy_layout_maintenance5` | `VK_KHR_maintenance5` support, the flags2 construction path, layout release, or the subsequent graphics clear/copy path fails. |

## Important Variations and Special Cases

- The four cache/layout combinations are generated for graphics and, when compatible, compute. Cache selection affects `buildPipeline(validCache)`; it does not create a separate cache-destruction test.
- `destroy_layout` determines whether the source records and submits the clear/copy sequence. Without it, the instance completes after pipeline construction and scope exit.
- `no_cache_destroy_layout_maintenance5` is graphics-only, has no pipeline cache, enables `VK_KHR_maintenance5`, and uses `VK_PIPELINE_CREATE_2_DISABLE_OPTIMIZATION_BIT_KHR`.
- Compute leaves are registered only for `MONOLITHIC` and `SHADER_OBJECT_UNLINKED_SPIRV`. Mustpass has 9 leaves in each of those roots and 5 leaves in each of the other five roots, for 43 leaves total.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Instance lifetime, layout release, clear/copy/readback | [EarlyDestroyTestInstance::iterate](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L91-L415) | Shows the actual ordering and pass condition. |
| Program collection | [EarlyDestroyTestCase::initPrograms](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L434-L471) | Defines the simple graphics and compute artifacts. |
| Support checks | [EarlyDestroyTestCase::checkSupport](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L478-L494) | Gates maintenance5 and construction routes. |
| Leaf generation | [addEarlyDestroyTests](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L496-L542) | Defines all leaf combinations and compute pruning. |
| Object lifetime | [Vulkan object lifetime](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L272-L320) | Defines application lifetime responsibility and command access. |
| Pipeline destruction validity | [vkDestroyPipeline](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7910-L7937) | States the submitted-command completion requirement for pipeline destruction. |

## Questions / Risk Points for User Audit

- Is the distinction between the legacy early-destruction description and the source's actual layout-release ordering clear?
- Does the page make clear that the submitted layout-destruction work clears and copies an image without binding the created pipeline?
- Are the split mustpass totals and compute compatibility limits clear?

## Conversion Notes for Final Wiki Rewrite

- Keep the source-grounded layout-release distinction in the final page.
- Use test case leaf as the behavioral axis and copy the failure table unchanged.
- Keep shader discussion short because generated shaders are not the submitted observable mechanism in this source.
