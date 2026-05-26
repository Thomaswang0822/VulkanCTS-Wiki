# vktSpvAsmIntegerDotProductTests

## Overview

Functional tests for the integer dot product instructions introduced by [`VK_KHR_shader_integer_dot_product`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L36): [`OpSDotKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1175-L1189), [`OpUDotKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1192-L1206), [`OpSUDotKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1209-L1226), `OpSDotAccSatKHR`, `OpUDotAccSatKHR`, and `OpSUDotAccSatKHR`.

## Role

Implementation file

## Source

- [vktSpvAsmIntegerDotProductTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1175)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute
├── opsdotkhr
├── opudotkhr
├── opsudotkhr
├── opsdotaccsatkhr
├── opudotaccsatkhr
└── opsudotaccsatkhr
```

## Test Families

### opsdotkhr — Tests OpSDotKHR instruction

Tests signed integer dot product. Covers [8-bit, 16-bit, and 32-bit element sizes](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1181-L1187) with vector lengths encoded by generated dot-product test names and vector metadata ([`getDotProductTestName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L533-L539)). Tests both `all` range and `small` range (8-bit only) input values ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1181-L1183)). Includes packed (4x8-bit) and unpacked formats with signedness combinations encoded in generated names ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L533-L538)).

### opudotkhr — Tests OpUDotKHR instruction

Tests unsigned integer dot product. Same structure as opsdotkhr but with unsigned operands.

### opsudotkhr — Tests OpSUDotKHR instruction

Tests mixed signedness dot product (signed LHS, unsigned RHS). Covers 8-bit, 16-bit, and 32-bit element sizes.

### opsdotaccsatkhr — Tests OpSDotAccSatKHR instruction

Tests signed integer dot product with accumulate and saturate. Includes "all", "limits", "limits-neg", "small", and "small-neg" input ranges to exercise saturation behavior. Uses custom [`compareDotProductAccSat`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L94-L183) verifier that accounts for overflow.

### opudotaccsatkhr — Tests OpUDotAccSatKHR instruction

Tests unsigned integer dot product with accumulate and saturate. Includes "all", "limits", "small", "small-nosat", and "nosat" input ranges.

### opsudotaccsatkhr — Tests OpSUDotAccSatKHR instruction

Tests mixed signedness dot product with accumulate and saturate. Includes "all", "limits", "limits-neg", "small", and "small-neg" input ranges.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Element size | 8, 16, 32 | Bit width of vector components |
| Vector length | 2, 3, 4 | Number of components per vector |
| Packing | packed, unpacked | Whether 4x8-bit vectors use PackedVectorFormat4x8BitKHR |
| Signedness (LHS/RHS) | ss, su, uu, us | Signed/unsigned combinations for left and right operands |
| Output size | 8, 16, 32 | Bit width of the result (for non-accumulate ops) |
| Input range | all, small, limits, limits-neg, nosat, small-neg, small-nosat | Range of input values to exercise different saturation scenarios |
| Accumulate addend | max, min | Whether addend values are near max or min for saturation testing |

## Support Requirements

- [`VK_KHR_shader_integer_dot_product`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L201) extension / [`shaderIntegerDotProduct`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L202) feature
- [`SPV_KHR_integer_dot_product`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L376-L378) SPIR-V extension
- [`VK_KHR_8bit_storage`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L207-L210) / `shaderInt8` / `storageBuffer8BitAccess` for 8-bit tests
- [`shaderInt16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L212-L216) / `storageBuffer16BitAccess` for 16-bit tests
- DotProduct input capabilities: [`DotProductInputAllKHR`, `DotProductInput4x8BitKHR`, `DotProductInput4x8BitPackedKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L369-L372)

## Verification Methods

- **Non-accumulate ops**: Pre-computed reference dot product values compared directly against shader output
- **Accumulate-saturate ops**: Custom [`compareDotProductAccSat`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L94-L183) template function that separates positive and negative products, checks for overflow, and applies saturating addition logic

## Notes

- Non-VulkanSC only
- 64-bit integer results are not currently covered (noted in [source comments](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L576-L578))
- Packed format tests only apply to 4-wide 8-bit vectors
