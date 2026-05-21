# Tensor

## Overview

The `tensor` category tests the `VK_ARM_tensors` extension, which introduces tensor objects as first-class Vulkan resources. Tensor objects represent multi-dimensional arrays with configurable format, tiling, strides, and rank, and can be accessed from shaders via dedicated built-in functions. This category validates tensor creation, memory requirements, data copies, shader read/write access, dimension queries, array-of-tensor access, boolean operations, and graphics-pipeline integration.

## Registration Entry Point

The category root is registered in [vktTensorTests.cpp#L37-L50](../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L50), which creates a `TestCaseGroup` named `"tensor"` and adds seven direct children.

## Subgroup Structure

```
tensor
├── creation_and_requirements
├── copies
├── basic_access
├── dimension_query
├── array_access
├── graphics_pipeline
└── boolean
```

| Subgroup | Factory Function | Source File | Level-3 Doc |
|----------|-----------------|-------------|-------------|
| `creation_and_requirements` | `createTensorCreateRequirementsTests` | [vktTensorCreateRequirements.cpp](../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp) | [vktTensorCreateRequirements](../testfiles/tensor/vktTensorCreateRequirements.md) |
| `copies` | `createTensorCopyTests` | [vktTensorCopies.cpp](../../modules/vulkan/tensor/vktTensorCopies.cpp) | [vktTensorCopies](../testfiles/tensor/vktTensorCopies.md) |
| `basic_access` | `createBasicAccessTests` | [vktTensorBasicShaderAccess.cpp](../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp) | [vktTensorBasicShaderAccess](../testfiles/tensor/vktTensorBasicShaderAccess.md) |
| `dimension_query` | `createDimensionQueryTests` | [vktTensorDimensionQuery.cpp](../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp) | [vktTensorDimensionQuery](../testfiles/tensor/vktTensorDimensionQuery.md) |
| `array_access` | `createArrayAccessTests` | [vktTensorArrayAccess.cpp](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp) | [vktTensorArrayAccess](../testfiles/tensor/vktTensorArrayAccess.md) |
| `graphics_pipeline` | `createGraphicsPipelineTests` | [vktTensorGraphicsPipeline.cpp](../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp) | [vktTensorGraphicsPipeline](../testfiles/tensor/vktTensorGraphicsPipeline.md) |
| `boolean` | `createTensorBoolTests` | [vktTensorBool.cpp](../../modules/vulkan/tensor/vktTensorBool.cpp) | [vktTensorBool](../testfiles/tensor/vktTensorBool.md) |

## File Inventory

### Registration Files

- [vktTensorTests.cpp](../../modules/vulkan/tensor/vktTensorTests.cpp) / [vktTensorTests.hpp](../../modules/vulkan/tensor/vktTensorTests.hpp) — Category root; creates the `tensor` group and adds the seven subgroups.

### Implementation Files

- [vktTensorCreateRequirements.cpp](../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp) — Tensor creation and memory requirement queries.
- [vktTensorCopies.cpp](../../modules/vulkan/tensor/vktTensorCopies.cpp) — Tensor-to-tensor copy operations via `vkCmdCopyTensorToTensorARM`.
- [vktTensorBasicShaderAccess.cpp](../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp) — Shader read/write access to individual tensor elements.
- [vktTensorDimensionQuery.cpp](../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp) — Shader-side dimension queries via `tensorSizeARM()`.
- [vktTensorArrayAccess.cpp](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp) — Shader access to arrays of tensors.
- [vktTensorGraphicsPipeline.cpp](../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp) — Tensor access from graphics pipeline (vertex + fragment stages).
- [vktTensorBool.cpp](../../modules/vulkan/tensor/vktTensorBool.cpp) — Boolean tensor operations (AND, OR, NOT, XOR).

### Utility Files

- [vktTensorTestsUtil.cpp](../../modules/vulkan/tensor/vktTensorTestsUtil.cpp) / [vktTensorTestsUtil.hpp](../../modules/vulkan/tensor/vktTensorTestsUtil.hpp) — Shared helpers: `TensorParameters`, format lists, support queries, naming utilities.

### Shader Files

- [vktTensorAccessShaders.cpp](../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp) — Shader generation for basic tensor read/write.
- [vktTensorArrayAccessShaders.cpp](../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp) — Shader generation for array-of-tensor access.
- [vktTensorBooleanShader.cpp](../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp) — Shader generation for boolean tensor operations.
- [vktTensorQueryDimensionsShaders.cpp](../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp) — Shader generation for dimension queries.
- [vktTensorShaderUtil.cpp](../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp) / [vktTensorShaderUtil.hpp](../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.hpp) — Shared shader utility functions.
- [vktTensorShaders.hpp](../../modules/vulkan/tensor/shaders/vktTensorShaders.hpp) — Shader header.

## Cross-File Recurring Test Families

| Theme | Subgroups | Description |
|-------|-----------|-------------|
| Tensor creation and memory requirements | `creation_and_requirements` | Validates `vkCreateTensorARM` and `vkGetTensorMemoryRequirementsARM` across formats and tilings. |
| Tensor-to-tensor copies | `copies` | Tests `vkCmdCopyTensorToTensorARM` between packed and non-packed tensors, including cross-format copies. |
| Shader tensor access | `basic_access`, `array_access`, `graphics_pipeline` | Validates reading from and writing to tensor elements in shaders. |
| Dimension queries | `dimension_query` | Tests the `tensorSizeARM()` shader built-in. |
| Boolean operations | `boolean` | Tests boolean tensor operations (AND, OR, NOT, XOR) using `VK_FORMAT_R8_BOOL_ARM`. |

## Cross-File Recurring Parameter Dimensions

| Parameter | Values | Subgroups |
|-----------|--------|-----------|
| Format | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | `creation_and_requirements`, `copies`, `basic_access`, `dimension_query`, `array_access` |
| Format (boolean) | `VK_FORMAT_R8_BOOL_ARM` | `boolean` |
| Tiling | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` | All subgroups |
| Shapes (ranks 1–4) | `{71693}`, `{263, 269}`, `{37, 43, 47}`, `{13, 17, 19, 23}` | `basic_access`, `copies`, `boolean` |
| Shapes (ranks 1–5) | `{1}`, `{2, 1}`, `{4, 2, 1}`, `{8, 4, 2, 1}`, `{4, 8, 16, 2, 1}` | `dimension_query` |
| Strides | Packed and non-packed stride variants for linear tiling | `basic_access`, `copies`, `boolean` |
| Max rank | Tensors created at the device's `maxTensorDimensionCount` limit | `creation_and_requirements`, `basic_access` |
| Access variant | `shader_read` / `shader_write` (basic); `array_read` / `array_write` (array) | `basic_access`, `array_access` |
| Boolean operator | `AND`, `OR`, `NOT`, `XOR` | `boolean` |
| DMA heap buffer | External memory import via DMA-buf | `basic_access` |
| Forced staging | Staging buffer path even when host-visible | `basic_access` |
| Offset | Non-zero tensor memory offset (2000 bytes) | `basic_access` |
| Image dimensions | `600x600`, `1280x720`, `567x891`, `891x567` | `graphics_pipeline` |

## Cross-File Recurring Support Requirements

| Requirement | Check | Subgroups |
|-------------|-------|-----------|
| `VK_ARM_tensors` extension | `context.requireDeviceFunctionality("VK_ARM_tensors")` | All subgroups |
| Format-tiling compatibility | `formatSupportTensorFlags()` queries `VkTensorFormatPropertiesARM` | `creation_and_requirements`, `basic_access`, `dimension_query`, `array_access`, `graphics_pipeline` |
| `shaderTensorAccess` feature | `deviceSupportsShaderTensorAccess()` queries `VkPhysicalDeviceTensorFeaturesARM` | `basic_access`, `dimension_query`, `array_access`, `graphics_pipeline` |
| Shader stage support | `deviceSupportsShaderStagesTensorAccess()` queries `VkPhysicalDeviceTensorPropertiesARM::shaderTensorSupportedStages` | `basic_access` (compute), `graphics_pipeline` (vertex + fragment), `dimension_query` (compute), `array_access` (compute) |
| `tensorNonPacked` feature | `deviceSupportsNonPackedTensors()` queries `VkPhysicalDeviceTensorFeaturesARM` | `basic_access`, `copies`, `boolean` (for non-packed stride variants) |
| `maxTensorDimensionCount` | Compared against required rank | `creation_and_requirements`, `basic_access`, `dimension_query`, `graphics_pipeline` |
| DMA-buf import support | `tensorSupportsDmaBufImport()` queries `VkPhysicalDeviceExternalTensorPropertiesARM` | `basic_access` (DMA heap buffer variants only) |

## Cross-File Recurring Verification Methods

| Method | Description | Subgroups |
|--------|-------------|-----------|
| Host-visible byte comparison | Direct `memcmp` of tensor data against expected values after download | `basic_access`, `array_access`, `boolean` |
| Staging-buffer comparison | For non-host-visible tensors, copy through staging buffer then compare on host | `basic_access`, `array_access` |
| CPU reference computation | Compute expected values on CPU (e.g., boolean ops, array indexing) and compare | `boolean`, `array_access` |
| Memory requirement validation | Check `vkGetTensorMemoryRequirementsARM` returns valid type bits and size | `creation_and_requirements` |
| Shader output buffer comparison | Read back shader output buffer and compare against expected values | `dimension_query` |
| Rendered-image pixel comparison | Compare rendered framebuffer pixels against expected colour/tensor values | `graphics_pipeline` |
| Copy-then-download comparison | Copy source tensor to destination, download destination, compare against source data | `copies` |

## Notes

- This category targets the `VK_ARM_tensors` vendor extension. No test-plan coverage was found in `apitests.adoc`.
- The `vktTensorTestsUtil.hpp` shared utility defines `TensorParameters` (format, tiling, dimensions, strides) and helper functions used across all implementation files.
- The `AccessVariant` enum (`WRITE_TO_BUFFER`, `READ_FROM_BUFFER`, `ARRAY_READ`, `ARRAY_WRITE`) has counterintuitive naming: `WRITE_TO_BUFFER` maps to `shader_read` (shader reads tensor, writes to buffer) and `READ_FROM_BUFFER` maps to `shader_write` (shader reads buffer, writes to tensor).
- All shader files are located in the `shaders/` subdirectory under the tensor module.
