# vktSpvAsmIntegerDotProductTests

## Overview

Functional tests for the integer dot product instructions introduced by VK_KHR_shader_integer_dot_product: `OpSDotKHR`, `OpUDotKHR`, `OpSUDotKHR`, `OpSDotAccSatKHR`, `OpUDotAccSatKHR`, and `OpSUDotAccSatKHR`.

## Role

Implementation file

## Source

- [vktSpvAsmIntegerDotProductTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp)

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

Tests signed integer dot product. Covers 8-bit, 16-bit, and 32-bit element sizes with vector lengths 2–4. Tests both "all" range and "small" range (8-bit only) input values. Includes packed (4x8-bit) and unpacked formats with all signedness combinations for LHS and RHS.

### opudotkhr — Tests OpUDotKHR instruction

Tests unsigned integer dot product. Same structure as opsdotkhr but with unsigned operands.

### opsudotkhr — Tests OpSUDotKHR instruction

Tests mixed signedness dot product (signed LHS, unsigned RHS). Covers 8-bit, 16-bit, and 32-bit element sizes.

### opsdotaccsatkhr — Tests OpSDotAccSatKHR instruction

Tests signed integer dot product with accumulate and saturate. Includes "all", "limits", "limits-neg", "small", and "small-neg" input ranges to exercise saturation behavior. Uses custom `compareDotProductAccSat` verifier that accounts for overflow.

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

- `VK_KHR_shader_integer_dot_product` extension / `shaderIntegerDotProduct` feature
- `SPV_KHR_integer_dot_product` SPIR-V extension
- `VK_KHR_8bit_storage` / `shaderInt8` / `storageBuffer8BitAccess` for 8-bit tests
- `VK_KHR_16bit_storage` / `shaderInt16` / `storageBuffer16BitAccess` for 16-bit tests
- DotProduct input capabilities: `DotProductInputAllKHR`, `DotProductInput4x8BitKHR`, `DotProductInput4x8BitPackedKHR`

## Verification Methods

- **Non-accumulate ops**: Pre-computed reference dot product values compared directly against shader output
- **Accumulate-saturate ops**: Custom `compareDotProductAccSat` template function (`vktSpvAsmIntegerDotProductTests.cpp#L95-L183`) that separates positive and negative products, checks for overflow, and applies saturating addition logic

## Notes

- Non-VulkanSC only
- 64-bit integer results are not currently covered (noted in source comments)
- Packed format tests only apply to 4-wide 8-bit vectors
