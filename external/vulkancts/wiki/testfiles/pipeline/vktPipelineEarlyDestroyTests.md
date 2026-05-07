# vktPipelineEarlyDestroyTests.cpp

## Overview

[`vktPipelineEarlyDestroyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L1) implements the [`early_destroy`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L549) topic group. It verifies that pipeline objects can be destroyed while still in use by command buffers, ensuring that the Vulkan implementation properly keeps pipelines alive until all referenced command buffer submissions complete.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineEarlyDestroyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L1)
- Header: [`vktPipelineEarlyDestroyTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.hpp#L1)

## Registration Path

[`createEarlyDestroyTests()`](../../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L546) returns the `early_destroy` group, attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L115) inside a `CTS_USES_VULKANSC` guard.

**Variant coverage**: All variants, VK only.

## Test Hierarchy

```text
early_destroy
├── no_cache
├── no_cache_destroy_layout
├── cache
├── cache_destroy_layout
├── no_cache_compute                              (monolithic and shader-object-unlinked-spirv only)
├── no_cache_destroy_layout_compute               (monolithic and shader-object-unlinked-spirv only)
├── cache_compute                                 (monolithic and shader-object-unlinked-spirv only)
├── cache_destroy_layout_compute                  (monolithic and shader-object-unlinked-spirv only)
└── no_cache_destroy_layout_maintenance5
```

## Test Families

| Family | Description |
|---|---|
| EarlyDestroyTestInstance | Verifies that destroying a pipeline object while command buffers referencing it are still in-flight does not cause errors or incorrect rendering results |

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
