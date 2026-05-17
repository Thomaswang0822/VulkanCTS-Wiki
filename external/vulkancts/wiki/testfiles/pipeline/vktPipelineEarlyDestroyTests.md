# vktPipelineEarlyDestroyTests.cpp

## Overview

[`vktPipelineEarlyDestroyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L1) implements the [`early_destroy`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L549) topic group. It verifies that pipeline objects can be destroyed while still in use by command buffers, ensuring that the Vulkan implementation properly keeps pipelines alive until all referenced command buffer submissions complete.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineEarlyDestroyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L1)
- Header: [`vktPipelineEarlyDestroyTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.early_destroy
├── no_cache
├── no_cache_destroy_layout
├── cache
├── cache_destroy_layout
├── no_cache_compute
├── no_cache_destroy_layout_compute
├── cache_compute
├── cache_destroy_layout_compute
└── no_cache_destroy_layout_maintenance5
```

## Test Families

### no_cache — Early destroy without pipeline cache

Destroys a graphics pipeline object while command buffers referencing it are still in-flight, without using a pipeline cache. Verifies the implementation properly keeps the pipeline alive until all submissions complete.

### no_cache_destroy_layout — Early destroy without cache, destroy layout

Destroys both the graphics pipeline and its layout while command buffers referencing the pipeline are still in-flight, without using a pipeline cache. Verifies the implementation handles layout destruction correctly.

### cache — Early destroy with pipeline cache

Destroys a graphics pipeline object while command buffers referencing it are still in-flight, with a pipeline cache in use. Verifies the implementation properly keeps the pipeline alive even when a cache is involved.

### cache_destroy_layout — Early destroy with cache, destroy layout

Destroys both the graphics pipeline and its layout while command buffers referencing the pipeline are still in-flight, with a pipeline cache in use.

### no_cache_compute — Early destroy compute pipeline without cache

Destroys a compute pipeline object while command buffers referencing it are still in-flight, without using a pipeline cache. Compute variants are only available for monolithic and shader-object-unlinked-spirv construction types.

### no_cache_destroy_layout_compute — Early destroy compute pipeline without cache, destroy layout

Destroys both the compute pipeline and its layout while command buffers are still in-flight, without a pipeline cache.

### cache_compute — Early destroy compute pipeline with cache

Destroys a compute pipeline object while command buffers referencing it are still in-flight, with a pipeline cache in use.

### cache_destroy_layout_compute — Early destroy compute pipeline with cache, destroy layout

Destroys both the compute pipeline and its layout while command buffers are still in-flight, with a pipeline cache in use.

### no_cache_destroy_layout_maintenance5 — Early destroy with maintenance5

Destroys the pipeline and layout while command buffers are in-flight, with `VK_KHR_maintenance5` enabled. Uses graphics pipeline only, without pipeline cache. Requires `VK_KHR_maintenance5`.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Use pipeline cache | Boolean | `true` / `false` |
| Destroy pipeline layout | Boolean | Whether the pipeline layout is also destroyed early |
| Use compute pipeline | Boolean | Whether to test with compute pipeline (vs. graphics) |
| Use maintenance5 | Boolean | Whether to enable `VK_KHR_maintenance5` features |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_maintenance5` | Required for the `no_cache_destroy_layout_maintenance5` test variant |
| Pipeline construction type | Checked via `checkPipelineConstructionRequirements()` for graphics, `checkShaderObjectRequirements()` for compute |

## Verification Methods

- **No-crash validation**: Test passes as long as destroying the pipeline (and optionally layout) while command buffers are in-flight does not cause a crash or device loss
- **Pixel value verification**: For graphics tests, framebuffer contents are read back and compared against expected clear color values after the pipeline has been destroyed
- **Compute result verification**: For compute tests, storage image contents are verified after pipeline destruction

## Notes

- The `early_destroy` topic group is VK only (guarded by `#ifndef CTS_USES_VULKANSC` at [`vktPipelineTests.cpp#L114`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L114))
- Compute pipeline variants are only added when `pipelineConstructionType` is `MONOLITHIC` or `SHADER_OBJECT_UNLINKED_SPIRV` (checked via `compCompatible` at [`vktPipelineEarlyDestroyTests.cpp#L498`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L498))
- The `no_cache_destroy_layout_maintenance5` test is always added regardless of compute compatibility, using graphics pipeline only with `VK_KHR_maintenance5` enabled
- Pipeline wrapper scoping ensures the pipeline object is destroyed before the command buffer completes, exercising the internal reference-counting path
