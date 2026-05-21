# tensor.copies

## Overview

This test group validates the `vkCmdCopyTensorARM` command for copying data between Vulkan tensors. It exercises tensor-to-tensor copies across all supported integer formats, both tiling modes (linear and optimal), multiple tensor ranks (1D through 4D), and both packed and non-packed (strided) memory layouts. The tests ensure that tensor copy operations preserve data exactly, regardless of format, tiling, shape, or stride configuration.

## Role of file

[vktTensorCopies.cpp](../../../modules/vulkan/tensor/vktTensorCopies.cpp) implements the `copies` subgroup under `dEQP-VK.tensor`. It is registered via [createTensorCopyTests()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L521-L531), which creates a `tcu::TestCaseGroup` named `"copies"` and populates it by calling the templated helper [addTensorCopyTests<T>()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L457-L519) for four unsigned integer types (`uint64_t`, `uint32_t`, `uint16_t`, `uint8_t`). Each instantiation generates tests for the format pairs corresponding to that type's width.

The file defines two test case class hierarchies:
- [LinearTensorCopyTestCase](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L84-L133) / [LinearTensorCopyTestInstance](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L64-L81): Tests copies between linear-tiling tensors using `vkCmdCopyTensorARM` directly.
- [OptimalTensorCopyTestCase](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L273-L312) / [OptimalTensorCopyTestInstance](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L237-L254): Tests copies between optimal-tiling tensors by staging through linear tensors (Linear -> Optimal -> Optimal -> Linear) since optimal-tiling tensors cannot be directly accessed from the host.

Shared utilities come from [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp), including `TensorParameters`, `getTestFormats<T>()`, `paramsToString()`, `formatSupportTensorFlags()`, `deviceSupportsNonPackedTensors()`, and `getTensorPhysicalDeviceProperties()`.

## Source code

- Test file: [vktTensorCopies.cpp](../../../modules/vulkan/tensor/vktTensorCopies.cpp)
- Utility header: [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp)
- Utility implementation: [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp)

## Registration Hierarchy

```text
tensor.copies
├── r64_uint_linear_shape_71693_to_r64_uint_linear_shape_71693
├── r64_uint_optimal_shape_71693_to_r64_uint_optimal_shape_71693
├── r64_uint_linear_shape_71693_to_r64_sint_linear_shape_71693
├── r64_uint_optimal_shape_71693_to_r64_sint_optimal_shape_71693
├── r64_sint_linear_shape_71693_to_r64_uint_linear_shape_71693
├── r64_sint_optimal_shape_71693_to_r64_uint_optimal_shape_71693
├── r64_sint_linear_shape_71693_to_r64_sint_linear_shape_71693
├── r64_sint_optimal_shape_71693_to_r64_sint_optimal_shape_71693
├── r64_uint_linear_shape_263_269_to_r64_uint_linear_shape_263_269
├── r64_uint_linear_shape_263_269_to_r64_uint_linear_shape_263_269_strides_2256_8
├── r64_uint_linear_shape_263_269_strides_2256_8_to_r64_uint_linear_shape_263_269
├── r64_uint_optimal_shape_263_269_to_r64_uint_optimal_shape_263_269
├── r64_uint_linear_shape_263_269_to_r64_sint_linear_shape_263_269
├── r64_uint_linear_shape_263_269_to_r64_sint_linear_shape_263_269_strides_2256_8
├── r64_uint_linear_shape_263_269_strides_2256_8_to_r64_sint_linear_shape_263_269
├── r64_uint_optimal_shape_263_269_to_r64_sint_optimal_shape_263_269
├── r64_sint_linear_shape_263_269_to_r64_uint_linear_shape_263_269
├── r64_sint_linear_shape_263_269_to_r64_uint_linear_shape_263_269_strides_2256_8
├── r64_sint_linear_shape_263_269_strides_2256_8_to_r64_uint_linear_shape_263_269
├── r64_sint_optimal_shape_263_269_to_r64_uint_optimal_shape_263_269
├── r64_sint_linear_shape_263_269_to_r64_sint_linear_shape_263_269
├── r64_sint_linear_shape_263_269_to_r64_sint_linear_shape_263_269_strides_2256_8
├── r64_sint_linear_shape_263_269_strides_2256_8_to_r64_sint_linear_shape_263_269
├── r64_sint_optimal_shape_263_269_to_r64_sint_optimal_shape_263_269
├── r64_uint_linear_shape_37_43_47_to_r64_uint_linear_shape_37_43_47
├── r64_uint_linear_shape_37_43_47_to_r64_uint_linear_shape_37_43_47_strides_20744_480_8
├── r64_uint_linear_shape_37_43_47_strides_20744_480_8_to_r64_uint_linear_shape_37_43_47
├── r64_uint_optimal_shape_37_43_47_to_r64_uint_optimal_shape_37_43_47
├── r64_uint_linear_shape_37_43_47_to_r64_sint_linear_shape_37_43_47
├── r64_uint_linear_shape_37_43_47_to_r64_sint_linear_shape_37_43_47_strides_20744_480_8
├── r64_uint_linear_shape_37_43_47_strides_20744_480_8_to_r64_sint_linear_shape_37_43_47
├── r64_uint_optimal_shape_37_43_47_to_r64_sint_optimal_shape_37_43_47
├── r64_sint_linear_shape_37_43_47_to_r64_uint_linear_shape_37_43_47
├── r64_sint_linear_shape_37_43_47_to_r64_uint_linear_shape_37_43_47_strides_20744_480_8
├── r64_sint_linear_shape_37_43_47_strides_20744_480_8_to_r64_uint_linear_shape_37_43_47
├── r64_sint_optimal_shape_37_43_47_to_r64_uint_optimal_shape_37_43_47
├── r64_sint_linear_shape_37_43_47_to_r64_sint_linear_shape_37_43_47
├── r64_sint_linear_shape_37_43_47_to_r64_sint_linear_shape_37_43_47_strides_20744_480_8
├── r64_sint_linear_shape_37_43_47_strides_20744_480_8_to_r64_sint_linear_shape_37_43_47
├── r64_sint_optimal_shape_37_43_47_to_r64_sint_optimal_shape_37_43_47
├── r64_uint_linear_shape_13_17_19_23_to_r64_uint_linear_shape_13_17_19_23
├── r64_uint_linear_shape_13_17_19_23_to_r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8
├── r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8_to_r64_uint_linear_shape_13_17_19_23
├── r64_uint_optimal_shape_13_17_19_23_to_r64_uint_optimal_shape_13_17_19_23
├── r64_uint_linear_shape_13_17_19_23_to_r64_sint_linear_shape_13_17_19_23
├── r64_uint_linear_shape_13_17_19_23_to_r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8
├── r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8_to_r64_sint_linear_shape_13_17_19_23
├── r64_uint_optimal_shape_13_17_19_23_to_r64_sint_optimal_shape_13_17_19_23
├── r64_sint_linear_shape_13_17_19_23_to_r64_uint_linear_shape_13_17_19_23
├── r64_sint_linear_shape_13_17_19_23_to_r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8
├── r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8_to_r64_uint_linear_shape_13_17_19_23
├── r64_sint_optimal_shape_13_17_19_23_to_r64_uint_optimal_shape_13_17_19_23
├── r64_sint_linear_shape_13_17_19_23_to_r64_sint_linear_shape_13_17_19_23
├── r64_sint_linear_shape_13_17_19_23_to_r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8
├── r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8_to_r64_sint_linear_shape_13_17_19_23
├── r64_sint_optimal_shape_13_17_19_23_to_r64_sint_optimal_shape_13_17_19_23
├── r32_uint_linear_shape_71693_to_r32_uint_linear_shape_71693
├── r32_uint_optimal_shape_71693_to_r32_uint_optimal_shape_71693
├── r32_uint_linear_shape_71693_to_r32_sint_linear_shape_71693
├── r32_uint_optimal_shape_71693_to_r32_sint_optimal_shape_71693
├── r32_sint_linear_shape_71693_to_r32_uint_linear_shape_71693
├── r32_sint_optimal_shape_71693_to_r32_uint_optimal_shape_71693
├── r32_sint_linear_shape_71693_to_r32_sint_linear_shape_71693
├── r32_sint_optimal_shape_71693_to_r32_sint_optimal_shape_71693
├── r32_uint_linear_shape_263_269_to_r32_uint_linear_shape_263_269
├── r32_uint_linear_shape_263_269_to_r32_uint_linear_shape_263_269_strides_1128_4
├── r32_uint_linear_shape_263_269_strides_1128_4_to_r32_uint_linear_shape_263_269
├── r32_uint_optimal_shape_263_269_to_r32_uint_optimal_shape_263_269
├── r32_uint_linear_shape_263_269_to_r32_sint_linear_shape_263_269
├── r32_uint_linear_shape_263_269_to_r32_sint_linear_shape_263_269_strides_1128_4
├── r32_uint_linear_shape_263_269_strides_1128_4_to_r32_sint_linear_shape_263_269
├── r32_uint_optimal_shape_263_269_to_r32_sint_optimal_shape_263_269
├── r32_sint_linear_shape_263_269_to_r32_uint_linear_shape_263_269
├── r32_sint_linear_shape_263_269_to_r32_uint_linear_shape_263_269_strides_1128_4
├── r32_sint_linear_shape_263_269_strides_1128_4_to_r32_uint_linear_shape_263_269
├── r32_sint_optimal_shape_263_269_to_r32_uint_optimal_shape_263_269
├── r32_sint_linear_shape_263_269_to_r32_sint_linear_shape_263_269
├── r32_sint_linear_shape_263_269_to_r32_sint_linear_shape_263_269_strides_1128_4
├── r32_sint_linear_shape_263_269_strides_1128_4_to_r32_sint_linear_shape_263_269
├── r32_sint_optimal_shape_263_269_to_r32_sint_optimal_shape_263_269
├── r32_uint_linear_shape_37_43_47_to_r32_uint_linear_shape_37_43_47
├── r32_uint_linear_shape_37_43_47_to_r32_uint_linear_shape_37_43_47_strides_10372_240_4
├── r32_uint_linear_shape_37_43_47_strides_10372_240_4_to_r32_uint_linear_shape_37_43_47
├── r32_uint_optimal_shape_37_43_47_to_r32_uint_optimal_shape_37_43_47
├── r32_uint_linear_shape_37_43_47_to_r32_sint_linear_shape_37_43_47
├── r32_uint_linear_shape_37_43_47_to_r32_sint_linear_shape_37_43_47_strides_10372_240_4
├── r32_uint_linear_shape_37_43_47_strides_10372_240_4_to_r32_sint_linear_shape_37_43_47
├── r32_uint_optimal_shape_37_43_47_to_r32_sint_optimal_shape_37_43_47
├── r32_sint_linear_shape_37_43_47_to_r32_uint_linear_shape_37_43_47
├── r32_sint_linear_shape_37_43_47_to_r32_uint_linear_shape_37_43_47_strides_10372_240_4
├── r32_sint_linear_shape_37_43_47_strides_10372_240_4_to_r32_uint_linear_shape_37_43_47
├── r32_sint_optimal_shape_37_43_47_to_r32_uint_optimal_shape_37_43_47
├── r32_sint_linear_shape_37_43_47_to_r32_sint_linear_shape_37_43_47
├── r32_sint_linear_shape_37_43_47_to_r32_sint_linear_shape_37_43_47_strides_10372_240_4
├── r32_sint_linear_shape_37_43_47_strides_10372_240_4_to_r32_sint_linear_shape_37_43_47
├── r32_sint_optimal_shape_37_43_47_to_r32_sint_optimal_shape_37_43_47
├── r32_uint_linear_shape_13_17_19_23_to_r32_uint_linear_shape_13_17_19_23
├── r32_uint_linear_shape_13_17_19_23_to_r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4
├── r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4_to_r32_uint_linear_shape_13_17_19_23
├── r32_uint_optimal_shape_13_17_19_23_to_r32_uint_optimal_shape_13_17_19_23
├── r32_uint_linear_shape_13_17_19_23_to_r32_sint_linear_shape_13_17_19_23
├── r32_uint_linear_shape_13_17_19_23_to_r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4
├── r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4_to_r32_sint_linear_shape_13_17_19_23
├── r32_uint_optimal_shape_13_17_19_23_to_r32_sint_optimal_shape_13_17_19_23
├── r32_sint_linear_shape_13_17_19_23_to_r32_uint_linear_shape_13_17_19_23
├── r32_sint_linear_shape_13_17_19_23_to_r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4
├── r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4_to_r32_uint_linear_shape_13_17_19_23
├── r32_sint_optimal_shape_13_17_19_23_to_r32_uint_optimal_shape_13_17_19_23
├── r32_sint_linear_shape_13_17_19_23_to_r32_sint_linear_shape_13_17_19_23
├── r32_sint_linear_shape_13_17_19_23_to_r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4
├── r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4_to_r32_sint_linear_shape_13_17_19_23
├── r32_sint_optimal_shape_13_17_19_23_to_r32_sint_optimal_shape_13_17_19_23
├── r16_uint_linear_shape_71693_to_r16_uint_linear_shape_71693
├── r16_uint_optimal_shape_71693_to_r16_uint_optimal_shape_71693
├── r16_uint_linear_shape_71693_to_r16_sint_linear_shape_71693
├── r16_uint_optimal_shape_71693_to_r16_sint_optimal_shape_71693
├── r16_sint_linear_shape_71693_to_r16_uint_linear_shape_71693
├── r16_sint_optimal_shape_71693_to_r16_uint_optimal_shape_71693
├── r16_sint_linear_shape_71693_to_r16_sint_linear_shape_71693
├── r16_sint_optimal_shape_71693_to_r16_sint_optimal_shape_71693
├── r16_uint_linear_shape_263_269_to_r16_uint_linear_shape_263_269
├── r16_uint_linear_shape_263_269_to_r16_uint_linear_shape_263_269_strides_564_2
├── r16_uint_linear_shape_263_269_strides_564_2_to_r16_uint_linear_shape_263_269
├── r16_uint_optimal_shape_263_269_to_r16_uint_optimal_shape_263_269
├── r16_uint_linear_shape_263_269_to_r16_sint_linear_shape_263_269
├── r16_uint_linear_shape_263_269_to_r16_sint_linear_shape_263_269_strides_564_2
├── r16_uint_linear_shape_263_269_strides_564_2_to_r16_sint_linear_shape_263_269
├── r16_uint_optimal_shape_263_269_to_r16_sint_optimal_shape_263_269
├── r16_sint_linear_shape_263_269_to_r16_uint_linear_shape_263_269
├── r16_sint_linear_shape_263_269_to_r16_uint_linear_shape_263_269_strides_564_2
├── r16_sint_linear_shape_263_269_strides_564_2_to_r16_uint_linear_shape_263_269
├── r16_sint_optimal_shape_263_269_to_r16_uint_optimal_shape_263_269
├── r16_sint_linear_shape_263_269_to_r16_sint_linear_shape_263_269
├── r16_sint_linear_shape_263_269_to_r16_sint_linear_shape_263_269_strides_564_2
├── r16_sint_linear_shape_263_269_strides_564_2_to_r16_sint_linear_shape_263_269
├── r16_sint_optimal_shape_263_269_to_r16_sint_optimal_shape_263_269
├── r16_uint_linear_shape_37_43_47_to_r16_uint_linear_shape_37_43_47
├── r16_uint_linear_shape_37_43_47_to_r16_uint_linear_shape_37_43_47_strides_5186_120_2
├── r16_uint_linear_shape_37_43_47_strides_5186_120_2_to_r16_uint_linear_shape_37_43_47
├── r16_uint_optimal_shape_37_43_47_to_r16_uint_optimal_shape_37_43_47
├── r16_uint_linear_shape_37_43_47_to_r16_sint_linear_shape_37_43_47
├── r16_uint_linear_shape_37_43_47_to_r16_sint_linear_shape_37_43_47_strides_5186_120_2
├── r16_uint_linear_shape_37_43_47_strides_5186_120_2_to_r16_sint_linear_shape_37_43_47
├── r16_uint_optimal_shape_37_43_47_to_r16_sint_optimal_shape_37_43_47
├── r16_sint_linear_shape_37_43_47_to_r16_uint_linear_shape_37_43_47
├── r16_sint_linear_shape_37_43_47_to_r16_uint_linear_shape_37_43_47_strides_5186_120_2
├── r16_sint_linear_shape_37_43_47_strides_5186_120_2_to_r16_uint_linear_shape_37_43_47
├── r16_sint_optimal_shape_37_43_47_to_r16_uint_optimal_shape_37_43_47
├── r16_sint_linear_shape_37_43_47_to_r16_sint_linear_shape_37_43_47
├── r16_sint_linear_shape_37_43_47_to_r16_sint_linear_shape_37_43_47_strides_5186_120_2
├── r16_sint_linear_shape_37_43_47_strides_5186_120_2_to_r16_sint_linear_shape_37_43_47
├── r16_sint_optimal_shape_37_43_47_to_r16_sint_optimal_shape_37_43_47
├── r16_uint_linear_shape_13_17_19_23_to_r16_uint_linear_shape_13_17_19_23
├── r16_uint_linear_shape_13_17_19_23_to_r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2
├── r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2_to_r16_uint_linear_shape_13_17_19_23
├── r16_uint_optimal_shape_13_17_19_23_to_r16_uint_optimal_shape_13_17_19_23
├── r16_uint_linear_shape_13_17_19_23_to_r16_sint_linear_shape_13_17_19_23
├── r16_uint_linear_shape_13_17_19_23_to_r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2
├── r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2_to_r16_sint_linear_shape_13_17_19_23
├── r16_uint_optimal_shape_13_17_19_23_to_r16_sint_optimal_shape_13_17_19_23
├── r16_sint_linear_shape_13_17_19_23_to_r16_uint_linear_shape_13_17_19_23
├── r16_sint_linear_shape_13_17_19_23_to_r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2
├── r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2_to_r16_uint_linear_shape_13_17_19_23
├── r16_sint_optimal_shape_13_17_19_23_to_r16_uint_optimal_shape_13_17_19_23
├── r16_sint_linear_shape_13_17_19_23_to_r16_sint_linear_shape_13_17_19_23
├── r16_sint_linear_shape_13_17_19_23_to_r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2
├── r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2_to_r16_sint_linear_shape_13_17_19_23
├── r16_sint_optimal_shape_13_17_19_23_to_r16_sint_optimal_shape_13_17_19_23
├── r8_uint_linear_shape_71693_to_r8_uint_linear_shape_71693
├── r8_uint_optimal_shape_71693_to_r8_uint_optimal_shape_71693
├── r8_uint_linear_shape_71693_to_r8_sint_linear_shape_71693
├── r8_uint_optimal_shape_71693_to_r8_sint_optimal_shape_71693
├── r8_sint_linear_shape_71693_to_r8_uint_linear_shape_71693
├── r8_sint_optimal_shape_71693_to_r8_uint_optimal_shape_71693
├── r8_sint_linear_shape_71693_to_r8_sint_linear_shape_71693
├── r8_sint_optimal_shape_71693_to_r8_sint_optimal_shape_71693
├── r8_uint_linear_shape_263_269_to_r8_uint_linear_shape_263_269
├── r8_uint_linear_shape_263_269_to_r8_uint_linear_shape_263_269_strides_282_1
├── r8_uint_linear_shape_263_269_strides_282_1_to_r8_uint_linear_shape_263_269
├── r8_uint_optimal_shape_263_269_to_r8_uint_optimal_shape_263_269
├── r8_uint_linear_shape_263_269_to_r8_sint_linear_shape_263_269
├── r8_uint_linear_shape_263_269_to_r8_sint_linear_shape_263_269_strides_282_1
├── r8_uint_linear_shape_263_269_strides_282_1_to_r8_sint_linear_shape_263_269
├── r8_uint_optimal_shape_263_269_to_r8_sint_optimal_shape_263_269
├── r8_sint_linear_shape_263_269_to_r8_uint_linear_shape_263_269
├── r8_sint_linear_shape_263_269_to_r8_uint_linear_shape_263_269_strides_282_1
├── r8_sint_linear_shape_263_269_strides_282_1_to_r8_uint_linear_shape_263_269
├── r8_sint_optimal_shape_263_269_to_r8_uint_optimal_shape_263_269
├── r8_sint_linear_shape_263_269_to_r8_sint_linear_shape_263_269
├── r8_sint_linear_shape_263_269_to_r8_sint_linear_shape_263_269_strides_282_1
├── r8_sint_linear_shape_263_269_strides_282_1_to_r8_sint_linear_shape_263_269
├── r8_sint_optimal_shape_263_269_to_r8_sint_optimal_shape_263_269
├── r8_uint_linear_shape_37_43_47_to_r8_uint_linear_shape_37_43_47
├── r8_uint_linear_shape_37_43_47_to_r8_uint_linear_shape_37_43_47_strides_2593_60_1
├── r8_uint_linear_shape_37_43_47_strides_2593_60_1_to_r8_uint_linear_shape_37_43_47
├── r8_uint_optimal_shape_37_43_47_to_r8_uint_optimal_shape_37_43_47
├── r8_uint_linear_shape_37_43_47_to_r8_sint_linear_shape_37_43_47
├── r8_uint_linear_shape_37_43_47_to_r8_sint_linear_shape_37_43_47_strides_2593_60_1
├── r8_uint_linear_shape_37_43_47_strides_2593_60_1_to_r8_sint_linear_shape_37_43_47
├── r8_uint_optimal_shape_37_43_47_to_r8_sint_optimal_shape_37_43_47
├── r8_sint_linear_shape_37_43_47_to_r8_uint_linear_shape_37_43_47
├── r8_sint_linear_shape_37_43_47_to_r8_uint_linear_shape_37_43_47_strides_2593_60_1
├── r8_sint_linear_shape_37_43_47_strides_2593_60_1_to_r8_uint_linear_shape_37_43_47
├── r8_sint_optimal_shape_37_43_47_to_r8_uint_optimal_shape_37_43_47
├── r8_sint_linear_shape_37_43_47_to_r8_sint_linear_shape_37_43_47
├── r8_sint_linear_shape_37_43_47_to_r8_sint_linear_shape_37_43_47_strides_2593_60_1
├── r8_sint_linear_shape_37_43_47_strides_2593_60_1_to_r8_sint_linear_shape_37_43_47
├── r8_sint_optimal_shape_37_43_47_to_r8_sint_optimal_shape_37_43_47
├── r8_uint_linear_shape_13_17_19_23_to_r8_uint_linear_shape_13_17_19_23
├── r8_uint_linear_shape_13_17_19_23_to_r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1
├── r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1_to_r8_uint_linear_shape_13_17_19_23
├── r8_uint_optimal_shape_13_17_19_23_to_r8_uint_optimal_shape_13_17_19_23
├── r8_uint_linear_shape_13_17_19_23_to_r8_sint_linear_shape_13_17_19_23
├── r8_uint_linear_shape_13_17_19_23_to_r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1
├── r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1_to_r8_sint_linear_shape_13_17_19_23
├── r8_uint_optimal_shape_13_17_19_23_to_r8_sint_optimal_shape_13_17_19_23
├── r8_sint_linear_shape_13_17_19_23_to_r8_uint_linear_shape_13_17_19_23
├── r8_sint_linear_shape_13_17_19_23_to_r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1
├── r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1_to_r8_uint_linear_shape_13_17_19_23
├── r8_sint_optimal_shape_13_17_19_23_to_r8_uint_optimal_shape_13_17_19_23
├── r8_sint_linear_shape_13_17_19_23_to_r8_sint_linear_shape_13_17_19_23
├── r8_sint_linear_shape_13_17_19_23_to_r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1
├── r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1_to_r8_sint_linear_shape_13_17_19_23
└── r8_sint_optimal_shape_13_17_19_23_to_r8_sint_optimal_shape_13_17_19_23
```

## Test Families

### LinearTensorCopyTestCase / LinearTensorCopyTestInstance

This family tests direct tensor-to-tensor copies between linear-tiling tensors. It is instantiated as [LinearTensorCopyTestCase<T>](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L84-L133) with the corresponding [LinearTensorCopyTestInstance<T>](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L64-L81).

The test instance [iterate()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L136-L234) performs the following steps:

1. Creates two linear-tiling tensors (source and destination) with the specified parameters ([lines 147-157](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L147-L157)).
2. Fills source tensor memory with sequential data via `StridedMemoryUtils<T>::fill()` and uploads it ([lines 161-164](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L161-L164)).
3. Clears the destination tensor to zero via `clearTensor()` ([line 166](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L166)).
4. Records and submits a command buffer that calls `vkCmdCopyTensorARM` with a single `VkTensorCopyARM` region covering the full tensor, followed by a pipeline barrier ([lines 170-212](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L170-L212)).
5. Downloads the destination tensor data and performs element-wise comparison against the source data ([lines 216-231](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L216-L231)).

Three sub-categories of linear copy tests are generated per shape/format combination (when rank > 1):
- **Packed to packed**: Both source and destination have default (empty) strides ([lines 473-478](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L473-L478)).
- **Packed to non-packed**: Source is packed, destination has padded strides ([lines 491-498](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L491-L498)).
- **Non-packed to packed**: Source has padded strides, destination is packed ([lines 500-507](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L500-L507)).

For rank-1 tensors (shape `{71693}`), only packed-to-packed linear tests are generated because non-packed strides are only meaningful for multi-dimensional tensors (the `rank > 1` guard at [line 492](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L492) and [line 501](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L501)).

### OptimalTensorCopyTestCase / OptimalTensorCopyTestInstance

This family tests copies between optimal-tiling tensors. It is instantiated as [OptimalTensorCopyTestCase<T>](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L273-L312) with the corresponding [OptimalTensorCopyTestInstance<T>](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L237-L254).

Since optimal-tiling tensors cannot be directly read or written by the host, the test uses a three-hop staging strategy observed in [iterate()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L314-L452):

1. Creates four tensors: a linear source, an optimal source, an optimal destination, and a linear destination ([lines 326-348](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L326-L348)). The optimal tensors have both `TRANSFER_SRC` and `TRANSFER_DST` usage flags.
2. Uploads input data to the linear source tensor and clears the linear destination tensor ([lines 352-358](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L352-L358)).
3. Records three sequential copy operations in a single command buffer:
   - **Linear -> Optimal**: Copy from linear source to optimal source ([lines 387-402](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L387-L402)).
   - **Optimal -> Optimal**: Copy from optimal source to optimal destination ([lines 404-413](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L404-L413)).
   - **Optimal -> Linear**: Copy from optimal destination to linear destination ([lines 415-423](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L415-L423)).
   - An `interCopiesBarrier` (global memory barrier) is inserted between each copy to ensure write-to-read visibility ([lines 375-376](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L375-L376)).
4. Downloads the linear destination tensor and compares element-wise against the original input data ([lines 434-449](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L434-L449)).

Only packed optimal-to-optimal tests are generated ([lines 509-515](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L509-L515)), since optimal-tiling tensors do not expose stride information to the application.

## Parameter dimensions

### Formats

Tests are generated per template instantiation of [addTensorCopyTests<T>()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L457), which calls [getTestFormats<T>()](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L118-L119) to obtain the format list for each type width:

| Template type | Formats | Element size |
|---|---|---|
| `uint64_t` | `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | 8 bytes |
| `uint32_t` | `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT` | 4 bytes |
| `uint16_t` | `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT` | 2 bytes |
| `uint8_t` | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT` | 1 byte |

The format lists are defined in [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L116-L157). Source and destination formats are independently iterated, so cross-format copies (e.g., `r64_uint` to `r64_sint`) are tested within the same type width.

### Tilings

Two tiling modes are tested, as defined by `VkTensorTilingARM`:

- `VK_TENSOR_TILING_LINEAR_ARM` (short name: `linear`) -- used in `LinearTensorCopyTestCase`
- `VK_TENSOR_TILING_OPTIMAL_ARM` (short name: `optimal`) -- used in `OptimalTensorCopyTestCase`

Short names are produced by [tensorTilingShortName()](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L217-L230).

### Shapes

Four tensor shapes are defined at [lines 459-464](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L459-L464):

| Shape | Rank | Element count |
|---|---|---|
| `{71693}` | 1 | 71,693 |
| `{263, 269}` | 2 | 70,747 |
| `{37, 43, 47}` | 3 | 74,777 |
| `{13, 17, 19, 23}` | 4 | 96,577 |

### Strides (non-packed layouts)

Non-packed (padded) strides are computed at [lines 484-489](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L484-L489). The formula adds `13 * elementSize` of padding between consecutive dimensions:

```
paddedStrides[rank-1] = elementSize
paddedStrides[rank-i] = paddedStrides[rank-i+1] * shape[rank-i+1] + 13 * elementSize   (for i = 2..rank)
```

The resulting stride values per format and shape (for rank >= 2) are:

| Shape | r8 strides | r16 strides | r32 strides | r64 strides |
|---|---|---|---|---|
| `{263, 269}` | `{282, 1}` | `{564, 2}` | `{1128, 4}` | `{2256, 8}` |
| `{37, 43, 47}` | `{2593, 60, 1}` | `{5186, 120, 2}` | `{10372, 240, 4}` | `{20744, 480, 8}` |
| `{13, 17, 19, 23}` | `{11862, 697, 36, 1}` | `{23724, 1394, 72, 2}` | `{47448, 2788, 144, 4}` | `{94896, 5576, 288, 8}` |

Non-packed stride tests are only generated for rank > 1 shapes, guarded by the condition at [line 492](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L492) and [line 501](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L501).

### Test count

For each of the 4 shapes and each of the 4 template type instantiations (each with 2 formats yielding 2x2 = 4 format pairs):
- Rank-1 shape: 2 test cases per format pair (packed-linear + optimal) = 8 tests
- Each rank > 1 shape (3 shapes): 4 test cases per format pair (packed-linear, packed-to-nonpacked, nonpacked-to-packed, optimal) = 16 tests

Total: 4 instantiations x (8 + 3 x 16) = 4 x 56 = **224 tests**.

## Support / feature requirements

### Extension requirement

Both test case classes require the `VK_ARM_tensors` extension via `context.requireDeviceFunctionality("VK_ARM_tensors")`:
- [LinearTensorCopyTestCase::checkSupport()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L100-L128) at [line 102](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L102)
- [OptimalTensorCopyTestCase::checkSupport()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L289-L307) at [line 291](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L291)

### Dimension count check

Both classes check that the tensor rank does not exceed `maxTensorDimensionCount` from `VkPhysicalDeviceTensorPropertiesARM` ([lines 104-109](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L104-L109) for linear, [lines 293-298](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L293-L298) for optimal). If exceeded, `NotSupportedError` is thrown.

### Format feature checks

**LinearTensorCopyTestCase** checks format support individually for source and destination:
- Source format must support `VK_FORMAT_FEATURE_2_TRANSFER_SRC_BIT` with linear tiling ([lines 111-115](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L111-L115))
- Destination format must support `VK_FORMAT_FEATURE_2_TRANSFER_DST_BIT` with linear tiling ([lines 117-121](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L117-L121))

**OptimalTensorCopyTestCase** checks format support for all four tensors used in the staging chain ([lines 300-306](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L300-L306)):
- Source format must support `VK_FORMAT_FEATURE_2_TRANSFER_SRC_BIT` with linear tiling (for the linear source staging tensor) via [checkSupportLinearSrcStorageTensor()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L256-L259)
- Source format must support both `VK_FORMAT_FEATURE_2_TRANSFER_SRC_BIT` and `VK_FORMAT_FEATURE_2_TRANSFER_DST_BIT` with optimal tiling (for the optimal source tensor) via [checkSupportOptimalStorageTensor()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L266-L270)
- Destination format must support both bits with optimal tiling (for the optimal destination tensor)
- Destination format must support `VK_FORMAT_FEATURE_2_TRANSFER_DST_BIT` with linear tiling (for the linear destination staging tensor) via [checkSupportLinearDstStorageTensor()](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L261-L264)

The format feature queries are performed by [formatSupportTensorFlags()](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L363), which inspects `VkTensorFormatPropertiesARM` queried via `vkGetPhysicalDeviceFormatProperties2`.

### Non-packed tensor support

LinearTensorCopyTestCase additionally checks whether the device supports non-packed tensors when either source or destination has non-default strides ([lines 123-127](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L123-L127)). This uses [deviceSupportsNonPackedTensors()](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L365-L380), which queries `VkPhysicalDeviceTensorFeaturesARM::tensorNonPacked`. If the device does not support non-packed tensors, tests with explicit strides throw `NotSupportedError`.

## Verification methods

Both test families use **exact element-wise comparison** as the verification method:

1. Source tensor data is generated by `StridedMemoryUtils<T>::fill()` which fills elements with sequential values respecting the stride layout.
2. After the copy operation, the destination tensor data is downloaded via `downloadFromTensor()`.
3. Each element of the downloaded result is compared against the corresponding element of the input data using `!=` ([lines 221-229](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L221-L229) for linear, [lines 439-448](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L439-L448) for optimal).
4. On mismatch, the test fails with a message indicating the index and the expected vs. actual values.
5. If all elements match, the test passes with `"Tensor test succeeded"`.

The comparison is performed using the C++ type `T` (the template parameter), and values are cast to `int` for the failure message ([line 226](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L226) and [line 445](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L445)).

## Test principles

The core principle is that `vkCmdCopyTensorARM` must produce a bit-exact copy of all tensor elements from source to destination, regardless of:

- **Format**: Both same-format and cross-format copies (within the same type width, e.g., uint vs. sint of the same bit width) must preserve data.
- **Tiling**: Both linear and optimal tiling must produce identical results. For optimal tiling, the test validates the full staging chain (linear -> optimal -> optimal -> linear) to ensure no data corruption occurs at any hop.
- **Shape/rank**: 1D through 4D tensors must all copy correctly.
- **Strides**: Both packed (contiguous) and non-packed (padded) stride layouts must be handled correctly. The non-packed strides add 13 elements of padding per dimension, exercising the implementation's stride-aware copy logic.

The assertion at [line 138](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L138) (`DE_ASSERT(m_srcParameters.dimensions == m_dstParameters.dimensions)`) confirms that source and destination tensors must have identical dimensions for a copy operation, as required by the `VkCopyTensorInfoARM` structure.

## Notes / uncertainties

- The `VkTensorCopyARM` region structure is initialized with `dimensionCount` set to the source rank ([line 195](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L195)), but all other fields are zero-initialized. The test relies on the implementation interpreting a single full-tensor region with default (zero) offsets. Whether zero offsets are explicitly defined by the spec or are an implementation convention is not verified in this file.
- Cross-format copies (e.g., `r64_uint` source to `r64_sint` destination) are tested, but the verification compares raw element values via the C++ type `T`. Since `uint64_t` and `int64_t` have the same bit width, this is a bitwise comparison. Whether the Vulkan spec defines format conversion semantics for cross-format tensor copies or requires identical formats is not clarified in this test file.
- The optimal-tiling test creates optimal tensors with both `TRANSFER_SRC` and `TRANSFER_DST` usage flags ([lines 332-334](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L332-L334) and [lines 338-340](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L338-L340)), which is necessary for the multi-hop staging approach but may not reflect all real-world usage patterns.
- The `StridedMemoryUtils<T>::fill()` method is defined outside the inspected files (observed in included headers). The exact fill pattern is not verified here but is assumed to produce deterministic, stride-aware sequential data.
- The `addTensorCopyTests` template function is called in the order `uint64_t`, `uint32_t`, `uint16_t`, `uint8_t` ([lines 525-528](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L525-L528)), which determines the ordering of tests in the hierarchy tree.
