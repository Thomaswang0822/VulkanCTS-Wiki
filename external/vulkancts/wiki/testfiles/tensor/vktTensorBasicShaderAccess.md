# tensor.basic_access

## Overview

Tests basic compute shader read and write access to Vulkan tensors via the `VK_ARM_tensors` extension. The test family validates that a shader can correctly read tensor data into a storage buffer (shader_read / `WRITE_TO_BUFFER`) and write storage buffer data into a tensor (shader_write / `READ_FROM_BUFFER`), across multiple formats, tilings, shapes, stride configurations, allocation offsets, forced staging buffers, and DMA heap buffers.

## Role of file

[vktTensorBasicShaderAccess.cpp](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp) registers the `basic_access` subgroup under `dEQP-VK.tensor`. It defines two test case class hierarchies -- `LinearTensorAccessTestCase` / `LinearTensorAccessTestInstance` for linear-tiling tensors and `OptimalTensorAccessTestCase` / `OptimalTensorAccessTestInstance` for optimal-tiling tensors -- and populates 280 leaf tests through `addShaderAccessTests<T>()` (4 template instantiations) and `addDmaHeapBufferAccessTests()`.

## Source code link

- Test file: [vktTensorBasicShaderAccess.cpp](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp)
- Shared utilities: [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp) / [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp)
- Shader generator: [vktTensorAccessShaders.cpp](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp)
- Shader utilities: [vktTensorShaderUtil.hpp](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.hpp)

## Registration Hierarchy

```text
tensor.basic_access
├── r16_sint_linear_max_rank_shader_read
├── r16_sint_linear_max_rank_shader_write
├── r16_sint_linear_shape_13_17_19_23_shader_read
├── r16_sint_linear_shape_13_17_19_23_shader_write
├── r16_sint_linear_shape_13_17_19_23_strides_14858_874_46_2_shader_read
├── r16_sint_linear_shape_13_17_19_23_strides_14858_874_46_2_shader_write
├── r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2_shader_read
├── r16_sint_linear_shape_13_17_19_23_strides_23724_1394_72_2_shader_write
├── r16_sint_linear_shape_263_269_shader_read
├── r16_sint_linear_shape_263_269_shader_write
├── r16_sint_linear_shape_263_269_strides_538_2_shader_read
├── r16_sint_linear_shape_263_269_strides_538_2_shader_write
├── r16_sint_linear_shape_263_269_strides_564_2_shader_read
├── r16_sint_linear_shape_263_269_strides_564_2_shader_write
├── r16_sint_linear_shape_37_43_47_shader_read
├── r16_sint_linear_shape_37_43_47_shader_write
├── r16_sint_linear_shape_37_43_47_strides_4042_94_2_shader_read
├── r16_sint_linear_shape_37_43_47_strides_4042_94_2_shader_write
├── r16_sint_linear_shape_37_43_47_strides_5186_120_2_shader_read
├── r16_sint_linear_shape_37_43_47_strides_5186_120_2_shader_write
├── r16_sint_linear_shape_71693_shader_read
├── r16_sint_linear_shape_71693_shader_write
├── r16_sint_linear_shape_71693_strides_2_shader_read
├── r16_sint_linear_shape_71693_strides_2_shader_write
├── r16_sint_optimal_max_rank
├── r16_sint_optimal_shape_13_17_19_23
├── r16_sint_optimal_shape_263_269
├── r16_sint_optimal_shape_37_43_47
├── r16_sint_optimal_shape_71693
├── r16_uint_linear_max_rank_shader_read
├── r16_uint_linear_max_rank_shader_write
├── r16_uint_linear_shape_13_17_19_23_shader_read
├── r16_uint_linear_shape_13_17_19_23_shader_read_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_shader_read_forced_staging
├── r16_uint_linear_shape_13_17_19_23_shader_read_forced_staging_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_shader_read_offset_2000
├── r16_uint_linear_shape_13_17_19_23_shader_read_offset_2000_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_shader_write
├── r16_uint_linear_shape_13_17_19_23_shader_write_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_shader_write_forced_staging
├── r16_uint_linear_shape_13_17_19_23_shader_write_forced_staging_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_shader_write_offset_2000
├── r16_uint_linear_shape_13_17_19_23_shader_write_offset_2000_dma_heap_buffer
├── r16_uint_linear_shape_13_17_19_23_strides_14858_874_46_2_shader_read
├── r16_uint_linear_shape_13_17_19_23_strides_14858_874_46_2_shader_write
├── r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2_shader_read
├── r16_uint_linear_shape_13_17_19_23_strides_23724_1394_72_2_shader_write
├── r16_uint_linear_shape_263_269_shader_read
├── r16_uint_linear_shape_263_269_shader_write
├── r16_uint_linear_shape_263_269_strides_538_2_shader_read
├── r16_uint_linear_shape_263_269_strides_538_2_shader_write
├── r16_uint_linear_shape_263_269_strides_564_2_shader_read
├── r16_uint_linear_shape_263_269_strides_564_2_shader_write
├── r16_uint_linear_shape_37_43_47_shader_read
├── r16_uint_linear_shape_37_43_47_shader_write
├── r16_uint_linear_shape_37_43_47_strides_4042_94_2_shader_read
├── r16_uint_linear_shape_37_43_47_strides_4042_94_2_shader_write
├── r16_uint_linear_shape_37_43_47_strides_5186_120_2_shader_read
├── r16_uint_linear_shape_37_43_47_strides_5186_120_2_shader_write
├── r16_uint_linear_shape_71693_shader_read
├── r16_uint_linear_shape_71693_shader_write
├── r16_uint_linear_shape_71693_strides_2_shader_read
├── r16_uint_linear_shape_71693_strides_2_shader_write
├── r16_uint_optimal_max_rank
├── r16_uint_optimal_shape_13_17_19_23
├── r16_uint_optimal_shape_13_17_19_23_dma_heap_buffer
├── r16_uint_optimal_shape_13_17_19_23_offset_2000_dma_heap_buffer
├── r16_uint_optimal_shape_263_269
├── r16_uint_optimal_shape_37_43_47
├── r16_uint_optimal_shape_71693
├── r32_sint_linear_max_rank_shader_read
├── r32_sint_linear_max_rank_shader_write
├── r32_sint_linear_shape_13_17_19_23_shader_read
├── r32_sint_linear_shape_13_17_19_23_shader_write
├── r32_sint_linear_shape_13_17_19_23_strides_29716_1748_92_4_shader_read
├── r32_sint_linear_shape_13_17_19_23_strides_29716_1748_92_4_shader_write
├── r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4_shader_read
├── r32_sint_linear_shape_13_17_19_23_strides_47448_2788_144_4_shader_write
├── r32_sint_linear_shape_263_269_shader_read
├── r32_sint_linear_shape_263_269_shader_write
├── r32_sint_linear_shape_263_269_strides_1076_4_shader_read
├── r32_sint_linear_shape_263_269_strides_1076_4_shader_write
├── r32_sint_linear_shape_263_269_strides_1128_4_shader_read
├── r32_sint_linear_shape_263_269_strides_1128_4_shader_write
├── r32_sint_linear_shape_37_43_47_shader_read
├── r32_sint_linear_shape_37_43_47_shader_write
├── r32_sint_linear_shape_37_43_47_strides_10372_240_4_shader_read
├── r32_sint_linear_shape_37_43_47_strides_10372_240_4_shader_write
├── r32_sint_linear_shape_37_43_47_strides_8084_188_4_shader_read
├── r32_sint_linear_shape_37_43_47_strides_8084_188_4_shader_write
├── r32_sint_linear_shape_71693_shader_read
├── r32_sint_linear_shape_71693_shader_write
├── r32_sint_linear_shape_71693_strides_4_shader_read
├── r32_sint_linear_shape_71693_strides_4_shader_write
├── r32_sint_optimal_max_rank
├── r32_sint_optimal_shape_13_17_19_23
├── r32_sint_optimal_shape_263_269
├── r32_sint_optimal_shape_37_43_47
├── r32_sint_optimal_shape_71693
├── r32_uint_linear_max_rank_shader_read
├── r32_uint_linear_max_rank_shader_write
├── r32_uint_linear_shape_13_17_19_23_shader_read
├── r32_uint_linear_shape_13_17_19_23_shader_read_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_shader_read_forced_staging
├── r32_uint_linear_shape_13_17_19_23_shader_read_forced_staging_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_shader_read_offset_2000
├── r32_uint_linear_shape_13_17_19_23_shader_read_offset_2000_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_shader_write
├── r32_uint_linear_shape_13_17_19_23_shader_write_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_shader_write_forced_staging
├── r32_uint_linear_shape_13_17_19_23_shader_write_forced_staging_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_shader_write_offset_2000
├── r32_uint_linear_shape_13_17_19_23_shader_write_offset_2000_dma_heap_buffer
├── r32_uint_linear_shape_13_17_19_23_strides_29716_1748_92_4_shader_read
├── r32_uint_linear_shape_13_17_19_23_strides_29716_1748_92_4_shader_write
├── r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4_shader_read
├── r32_uint_linear_shape_13_17_19_23_strides_47448_2788_144_4_shader_write
├── r32_uint_linear_shape_263_269_shader_read
├── r32_uint_linear_shape_263_269_shader_write
├── r32_uint_linear_shape_263_269_strides_1076_4_shader_read
├── r32_uint_linear_shape_263_269_strides_1076_4_shader_write
├── r32_uint_linear_shape_263_269_strides_1128_4_shader_read
├── r32_uint_linear_shape_263_269_strides_1128_4_shader_write
├── r32_uint_linear_shape_37_43_47_shader_read
├── r32_uint_linear_shape_37_43_47_shader_write
├── r32_uint_linear_shape_37_43_47_strides_10372_240_4_shader_read
├── r32_uint_linear_shape_37_43_47_strides_10372_240_4_shader_write
├── r32_uint_linear_shape_37_43_47_strides_8084_188_4_shader_read
├── r32_uint_linear_shape_37_43_47_strides_8084_188_4_shader_write
├── r32_uint_linear_shape_71693_shader_read
├── r32_uint_linear_shape_71693_shader_write
├── r32_uint_linear_shape_71693_strides_4_shader_read
├── r32_uint_linear_shape_71693_strides_4_shader_write
├── r32_uint_optimal_max_rank
├── r32_uint_optimal_shape_13_17_19_23
├── r32_uint_optimal_shape_13_17_19_23_dma_heap_buffer
├── r32_uint_optimal_shape_13_17_19_23_offset_2000_dma_heap_buffer
├── r32_uint_optimal_shape_263_269
├── r32_uint_optimal_shape_37_43_47
├── r32_uint_optimal_shape_71693
├── r64_sint_linear_max_rank_shader_read
├── r64_sint_linear_max_rank_shader_write
├── r64_sint_linear_shape_13_17_19_23_shader_read
├── r64_sint_linear_shape_13_17_19_23_shader_write
├── r64_sint_linear_shape_13_17_19_23_strides_59432_3496_184_8_shader_read
├── r64_sint_linear_shape_13_17_19_23_strides_59432_3496_184_8_shader_write
├── r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8_shader_read
├── r64_sint_linear_shape_13_17_19_23_strides_94896_5576_288_8_shader_write
├── r64_sint_linear_shape_263_269_shader_read
├── r64_sint_linear_shape_263_269_shader_write
├── r64_sint_linear_shape_263_269_strides_2152_8_shader_read
├── r64_sint_linear_shape_263_269_strides_2152_8_shader_write
├── r64_sint_linear_shape_263_269_strides_2256_8_shader_read
├── r64_sint_linear_shape_263_269_strides_2256_8_shader_write
├── r64_sint_linear_shape_37_43_47_shader_read
├── r64_sint_linear_shape_37_43_47_shader_write
├── r64_sint_linear_shape_37_43_47_strides_16168_376_8_shader_read
├── r64_sint_linear_shape_37_43_47_strides_16168_376_8_shader_write
├── r64_sint_linear_shape_37_43_47_strides_20744_480_8_shader_read
├── r64_sint_linear_shape_37_43_47_strides_20744_480_8_shader_write
├── r64_sint_linear_shape_71693_shader_read
├── r64_sint_linear_shape_71693_shader_write
├── r64_sint_linear_shape_71693_strides_8_shader_read
├── r64_sint_linear_shape_71693_strides_8_shader_write
├── r64_sint_optimal_max_rank
├── r64_sint_optimal_shape_13_17_19_23
├── r64_sint_optimal_shape_263_269
├── r64_sint_optimal_shape_37_43_47
├── r64_sint_optimal_shape_71693
├── r64_uint_linear_max_rank_shader_read
├── r64_uint_linear_max_rank_shader_write
├── r64_uint_linear_shape_13_17_19_23_shader_read
├── r64_uint_linear_shape_13_17_19_23_shader_read_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_shader_read_forced_staging
├── r64_uint_linear_shape_13_17_19_23_shader_read_forced_staging_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_shader_read_offset_2000
├── r64_uint_linear_shape_13_17_19_23_shader_read_offset_2000_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_shader_write
├── r64_uint_linear_shape_13_17_19_23_shader_write_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_shader_write_forced_staging
├── r64_uint_linear_shape_13_17_19_23_shader_write_forced_staging_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_shader_write_offset_2000
├── r64_uint_linear_shape_13_17_19_23_shader_write_offset_2000_dma_heap_buffer
├── r64_uint_linear_shape_13_17_19_23_strides_59432_3496_184_8_shader_read
├── r64_uint_linear_shape_13_17_19_23_strides_59432_3496_184_8_shader_write
├── r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8_shader_read
├── r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8_shader_write
├── r64_uint_linear_shape_263_269_shader_read
├── r64_uint_linear_shape_263_269_shader_write
├── r64_uint_linear_shape_263_269_strides_2152_8_shader_read
├── r64_uint_linear_shape_263_269_strides_2152_8_shader_write
├── r64_uint_linear_shape_263_269_strides_2256_8_shader_read
├── r64_uint_linear_shape_263_269_strides_2256_8_shader_write
├── r64_uint_linear_shape_37_43_47_shader_read
├── r64_uint_linear_shape_37_43_47_shader_write
├── r64_uint_linear_shape_37_43_47_strides_16168_376_8_shader_read
├── r64_uint_linear_shape_37_43_47_strides_16168_376_8_shader_write
├── r64_uint_linear_shape_37_43_47_strides_20744_480_8_shader_read
├── r64_uint_linear_shape_37_43_47_strides_20744_480_8_shader_write
├── r64_uint_linear_shape_71693_shader_read
├── r64_uint_linear_shape_71693_shader_write
├── r64_uint_linear_shape_71693_strides_8_shader_read
├── r64_uint_linear_shape_71693_strides_8_shader_write
├── r64_uint_optimal_max_rank
├── r64_uint_optimal_shape_13_17_19_23
├── r64_uint_optimal_shape_13_17_19_23_dma_heap_buffer
├── r64_uint_optimal_shape_13_17_19_23_offset_2000_dma_heap_buffer
├── r64_uint_optimal_shape_263_269
├── r64_uint_optimal_shape_37_43_47
├── r64_uint_optimal_shape_71693
├── r8_sint_linear_max_rank_shader_read
├── r8_sint_linear_max_rank_shader_write
├── r8_sint_linear_shape_13_17_19_23_shader_read
├── r8_sint_linear_shape_13_17_19_23_shader_write
├── r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1_shader_read
├── r8_sint_linear_shape_13_17_19_23_strides_11862_697_36_1_shader_write
├── r8_sint_linear_shape_13_17_19_23_strides_7429_437_23_1_shader_read
├── r8_sint_linear_shape_13_17_19_23_strides_7429_437_23_1_shader_write
├── r8_sint_linear_shape_263_269_shader_read
├── r8_sint_linear_shape_263_269_shader_write
├── r8_sint_linear_shape_263_269_strides_269_1_shader_read
├── r8_sint_linear_shape_263_269_strides_269_1_shader_write
├── r8_sint_linear_shape_263_269_strides_282_1_shader_read
├── r8_sint_linear_shape_263_269_strides_282_1_shader_write
├── r8_sint_linear_shape_37_43_47_shader_read
├── r8_sint_linear_shape_37_43_47_shader_write
├── r8_sint_linear_shape_37_43_47_strides_2021_47_1_shader_read
├── r8_sint_linear_shape_37_43_47_strides_2021_47_1_shader_write
├── r8_sint_linear_shape_37_43_47_strides_2593_60_1_shader_read
├── r8_sint_linear_shape_37_43_47_strides_2593_60_1_shader_write
├── r8_sint_linear_shape_71693_shader_read
├── r8_sint_linear_shape_71693_shader_write
├── r8_sint_linear_shape_71693_strides_1_shader_read
├── r8_sint_linear_shape_71693_strides_1_shader_write
├── r8_sint_optimal_max_rank
├── r8_sint_optimal_shape_13_17_19_23
├── r8_sint_optimal_shape_263_269
├── r8_sint_optimal_shape_37_43_47
├── r8_sint_optimal_shape_71693
├── r8_uint_linear_max_rank_shader_read
├── r8_uint_linear_max_rank_shader_write
├── r8_uint_linear_shape_13_17_19_23_shader_read
├── r8_uint_linear_shape_13_17_19_23_shader_read_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_shader_read_forced_staging
├── r8_uint_linear_shape_13_17_19_23_shader_read_forced_staging_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_shader_read_offset_2000
├── r8_uint_linear_shape_13_17_19_23_shader_read_offset_2000_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_shader_write
├── r8_uint_linear_shape_13_17_19_23_shader_write_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_shader_write_forced_staging
├── r8_uint_linear_shape_13_17_19_23_shader_write_forced_staging_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_shader_write_offset_2000
├── r8_uint_linear_shape_13_17_19_23_shader_write_offset_2000_dma_heap_buffer
├── r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1_shader_read
├── r8_uint_linear_shape_13_17_19_23_strides_11862_697_36_1_shader_write
├── r8_uint_linear_shape_13_17_19_23_strides_7429_437_23_1_shader_read
├── r8_uint_linear_shape_13_17_19_23_strides_7429_437_23_1_shader_write
├── r8_uint_linear_shape_263_269_shader_read
├── r8_uint_linear_shape_263_269_shader_write
├── r8_uint_linear_shape_263_269_strides_269_1_shader_read
├── r8_uint_linear_shape_263_269_strides_269_1_shader_write
├── r8_uint_linear_shape_263_269_strides_282_1_shader_read
├── r8_uint_linear_shape_263_269_strides_282_1_shader_write
├── r8_uint_linear_shape_37_43_47_shader_read
├── r8_uint_linear_shape_37_43_47_shader_write
├── r8_uint_linear_shape_37_43_47_strides_2021_47_1_shader_read
├── r8_uint_linear_shape_37_43_47_strides_2021_47_1_shader_write
├── r8_uint_linear_shape_37_43_47_strides_2593_60_1_shader_read
├── r8_uint_linear_shape_37_43_47_strides_2593_60_1_shader_write
├── r8_uint_linear_shape_71693_shader_read
├── r8_uint_linear_shape_71693_shader_write
├── r8_uint_linear_shape_71693_strides_1_shader_read
├── r8_uint_linear_shape_71693_strides_1_shader_write
├── r8_uint_optimal_max_rank
├── r8_uint_optimal_shape_13_17_19_23
├── r8_uint_optimal_shape_13_17_19_23_dma_heap_buffer
├── r8_uint_optimal_shape_13_17_19_23_offset_2000_dma_heap_buffer
├── r8_uint_optimal_shape_263_269
├── r8_uint_optimal_shape_37_43_47
└── r8_uint_optimal_shape_71693
```

## Test Families

### r64_uint_linear_shape_71693_shader_write / shader_read

Linear-tiling 1D tensor with format `VK_FORMAT_R64_UINT`, shape `{71693}`, implicitly packed strides. The `shader_write` variant (internally `READ_FROM_BUFFER`) fills a storage buffer with known data, then a compute shader writes each element into the tensor via `tensorWriteARM`. The `shader_read` variant (internally `WRITE_TO_BUFFER`) pre-fills the tensor with known data, then a compute shader reads each element from the tensor via `tensorReadARM` into a storage buffer. Verification compares tensor data against buffer data element-by-element.

### r64_uint_linear_shape_71693_strides_8_shader_write / shader_read

Same as above but with explicitly specified packed strides `[8]` (byte stride equal to element size). This exercises the explicit-packed-stride code path for rank-1 tensors, which is semantically identical to the implicit-packed path.

### r64_uint_optimal_shape_71693

Optimal-tiling 1D tensor with format `VK_FORMAT_R64_UINT`, shape `{71693}`. Uses a two-dispatch pipeline: first dispatch reads from a source buffer into the tensor (`tensorWriteARM`), second dispatch reads from the tensor into a destination buffer (`tensorReadARM`). Verification compares source and destination buffers.

### r64_uint_linear_shape_263_269_shader_write / shader_read

Linear-tiling 2D tensor with format `VK_FORMAT_R64_UINT`, shape `{263, 269}`, implicitly packed strides. Same read/write verification pattern as the 1D case.

### r64_uint_linear_shape_263_269_strides_2256_8_shader_write / shader_read

Linear-tiling 2D tensor with non-packed (padded) strides `[2256, 8]`. The innermost stride is the element size (8 bytes), while the outer stride is `269 * 8 + 13 * 8 = 2256`, adding 13 elements of padding per row. This exercises the non-packed tensor path, which requires the `tensorNonPacked` feature ([vktTensorBasicShaderAccess.cpp#L236-L239](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L236-L239)).

### r64_uint_linear_shape_263_269_strides_2152_8_shader_write / shader_read

Linear-tiling 2D tensor with explicitly specified packed strides `[2152, 8]` (where `2152 = 269 * 8`). Semantically identical to the implicit-packed case but exercises the explicit-packed-stride code path.

### r64_uint_optimal_shape_263_269

Optimal-tiling 2D tensor with format `VK_FORMAT_R64_UINT`, shape `{263, 269}`. Two-dispatch buffer-to-tensor-to-buffer round-trip verification.

### r64_uint_linear_shape_37_43_47_shader_write / shader_read

Linear-tiling 3D tensor with format `VK_FORMAT_R64_UINT`, shape `{37, 43, 47}`, implicitly packed strides.

### r64_uint_linear_shape_37_43_47_strides_20744_480_8_shader_write / shader_read

Linear-tiling 3D tensor with non-packed strides `[20744, 480, 8]`. Each dimension adds `13 * elementSize` bytes of padding beyond the packed stride.

### r64_uint_linear_shape_37_43_47_strides_16168_376_8_shader_write / shader_read

Linear-tiling 3D tensor with explicitly specified packed strides `[16168, 376, 8]`.

### r64_uint_optimal_shape_37_43_47

Optimal-tiling 3D tensor, two-dispatch round-trip verification.

### r64_uint_linear_shape_13_17_19_23_shader_write / shader_read

Linear-tiling 4D tensor with format `VK_FORMAT_R64_UINT`, shape `{13, 17, 19, 23}`, implicitly packed strides.

### r64_uint_linear_shape_13_17_19_23_strides_94896_5576_288_8_shader_write / shader_read

Linear-tiling 4D tensor with non-packed strides `[94896, 5576, 288, 8]`.

### r64_uint_linear_shape_13_17_19_23_strides_59432_3496_184_8_shader_write / shader_read

Linear-tiling 4D tensor with explicitly specified packed strides `[59432, 3496, 184, 8]`.

### r64_uint_optimal_shape_13_17_19_23

Optimal-tiling 4D tensor, two-dispatch round-trip verification.

### r64_sint variants (same shapes)

All of the above patterns are repeated for `VK_FORMAT_R64_SINT`, producing the same set of test names with `r64_sint` in place of `r64_uint`. The stride values are identical because both 64-bit formats share the same element size of 8 bytes.

### r64_uint_linear_shape_13_17_19_23_shader_read_forced_staging

Linear-tiling 4D tensor with `VK_FORMAT_R64_UINT`, shape `{13, 17, 19, 23}`, implicitly packed strides, with `forceStagingBuffers = true`. This forces the use of a staging buffer for tensor data transfer even when the tensor memory is host-visible, exercising the staging-buffer upload/download code paths ([vktTensorBasicShaderAccess.cpp#L917-L924](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L917-L924)).

### r64_uint_linear_shape_13_17_19_23_shader_write_forced_staging

Same as above but with the `READ_FROM_BUFFER` (shader_write) variant.

### r64_uint_linear_shape_13_17_19_23_shader_read_offset_2000

Linear-tiling 4D tensor with `VK_FORMAT_R64_UINT`, shape `{13, 17, 19, 23}`, implicitly packed strides, with `tensorOffset = 2000`. The tensor is bound at a 2000-byte offset within its memory allocation, testing offset-based allocation ([vktTensorBasicShaderAccess.cpp#L927-L934](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L927-L934)).

### r64_uint_linear_shape_13_17_19_23_shader_write_offset_2000

Same as above but with the `READ_FROM_BUFFER` (shader_write) variant.

### r64_uint_linear_max_rank_shader_read / shader_write

Linear-tiling tensor with `VK_FORMAT_R64_UINT` and empty dimensions (rank=0 at registration time). At instance creation, the implementation's `maxTensorDimensionCount` is queried and a shape is constructed dynamically: dimensions are all 1 except `dimensions[0] = 151`, `dimensions[rank-2] = 3`, and `dimensions[rank-1] = 157` ([vktTensorBasicShaderAccess.cpp#L70-L84](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L70-L84)). This tests the maximum rank the implementation supports.

### r64_uint_optimal_max_rank

Optimal-tiling tensor with `VK_FORMAT_R64_UINT` and dynamically computed max-rank shape. Same two-dispatch round-trip as other optimal tests.

### r64_sint_linear_max_rank_shader_read / shader_write / optimal_max_rank

Same max-rank pattern for `VK_FORMAT_R64_SINT`.

### r32_uint / r32_sint variants

All the same test patterns as r64, but for 32-bit formats (`VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`) with element size 4 bytes. Stride values differ accordingly:
- Rank 1 packed strides: `[4]`
- Rank 2 packed strides: `[1076, 4]`; non-packed: `[1128, 4]`
- Rank 3 packed strides: `[8084, 188, 4]`; non-packed: `[10372, 240, 4]`
- Rank 4 packed strides: `[29716, 1748, 92, 4]`; non-packed: `[47448, 2788, 144, 4]`

### r16_uint / r16_sint variants

All the same test patterns for 16-bit formats (`VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`) with element size 2 bytes:
- Rank 1 packed strides: `[2]`
- Rank 2 packed strides: `[538, 2]`; non-packed: `[564, 2]`
- Rank 3 packed strides: `[4042, 94, 2]`; non-packed: `[5186, 120, 2]`
- Rank 4 packed strides: `[14858, 874, 46, 2]`; non-packed: `[23724, 1394, 72, 2]`

### r8_uint / r8_sint variants

All the same test patterns for 8-bit formats (`VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`) with element size 1 byte:
- Rank 1 packed strides: `[1]`
- Rank 2 packed strides: `[269, 1]`; non-packed: `[282, 1]`
- Rank 3 packed strides: `[2021, 47, 1]`; non-packed: `[2593, 60, 1]`
- Rank 4 packed strides: `[7429, 437, 23, 1]`; non-packed: `[11862, 697, 36, 1]`

### DMA heap buffer tests (r8_uint, r16_uint, r32_uint, r64_uint)

These tests use DMA heap-allocated memory for tensor backing, exercising the `VK_EXT_external_memory_dma_buf` import path. They all use shape `{13, 17, 19, 23}` and the `_uint` variant of each format size.

#### {format}_linear_shape_13_17_19_23_shader_write_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer, `READ_FROM_BUFFER` variant. The shader writes data from a storage buffer into the tensor backed by DMA heap memory.

#### {format}_linear_shape_13_17_19_23_shader_read_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer, `WRITE_TO_BUFFER` variant. The shader reads data from the DMA-heap-backed tensor into a storage buffer.

#### {format}_optimal_shape_13_17_19_23_dma_heap_buffer

Optimal-tiling tensor with DMA heap buffer, no offset. Two-dispatch round-trip verification.

#### {format}_optimal_shape_13_17_19_23_offset_2000_dma_heap_buffer

Optimal-tiling tensor with DMA heap buffer and 2000-byte offset within the allocation. Two-dispatch round-trip verification.

#### {format}_linear_shape_13_17_19_23_shader_write_forced_staging_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer and forced staging buffers. `READ_FROM_BUFFER` variant.

#### {format}_linear_shape_13_17_19_23_shader_read_forced_staging_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer and forced staging buffers. `WRITE_TO_BUFFER` variant.

#### {format}_linear_shape_13_17_19_23_shader_write_offset_2000_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer and 2000-byte offset. `READ_FROM_BUFFER` variant.

#### {format}_linear_shape_13_17_19_23_shader_read_offset_2000_dma_heap_buffer

Linear-tiling tensor with DMA heap buffer and 2000-byte offset. `WRITE_TO_BUFFER` variant.

## Parameter dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Format | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | Integer tensor element formats ([vktTensorTestsUtil.cpp#L48-L56](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56)) |
| Tiling | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` | Tensor memory layout |
| Shape | `{71693}`, `{263, 269}`, `{37, 43, 47}`, `{13, 17, 19, 23}` | Fixed tensor dimensions for ranks 1-4 ([vktTensorBasicShaderAccess.cpp#L856-L861](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L856-L861)) |
| Strides | Implicit (empty), explicit packed, explicit non-packed (padded with 13*elementSize per dimension) | Byte strides for linear tiling; non-packed strides add 13 elements of padding per dimension ([vktTensorBasicShaderAccess.cpp#L884-L889](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L884-L889)) |
| Access variant | `READ_FROM_BUFFER` (shader_write), `WRITE_TO_BUFFER` (shader_read) | Direction of data flow between tensor and storage buffer |
| Tensor offset | 0, 2000 | Byte offset within the memory allocation |
| Force staging | true, false | Whether to force staging buffer usage even for host-visible memory |
| DMA heap | true, false | Whether to use DMA heap allocator for tensor memory |

## Support / Feature Requirements

All tests require `VK_ARM_tensors` extension ([vktTensorBasicShaderAccess.cpp#L195](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L195)). Additional checks in `checkSupport`:

1. **Dimension count**: The tensor rank must not exceed `maxTensorDimensionCount` reported by the implementation ([vktTensorBasicShaderAccess.cpp#L197-L200](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L197-L200)).

2. **Format support**: The format must support `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` for the given tiling ([vktTensorBasicShaderAccess.cpp#L202-L206](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L202-L206)).

3. **Shader tensor access**: The device must support `shaderTensorAccess` feature ([vktTensorBasicShaderAccess.cpp#L208-L211](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L208-L211)).

4. **Compute shader stage**: The device must support shader tensor access in `VK_SHADER_STAGE_COMPUTE_BIT` ([vktTensorBasicShaderAccess.cpp#L213-L216](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L213-L216)).

5. **DMA heap** (DMA heap tests only): Requires `VK_EXT_external_memory_dma_buf`, platform DMA heap allocator support, and the tensor description must support DMA-BUF import ([vktTensorBasicShaderAccess.cpp#L218-L234](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L218-L234)).

6. **Non-packed tensors** (non-packed stride tests only): The device must support the `tensorNonPacked` feature ([vktTensorBasicShaderAccess.cpp#L236-L239](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L236-L239)).

## Verification methods

### Linear tiling tests

For `WRITE_TO_BUFFER` (shader_read) tests: the tensor is pre-filled with known data (via `uploadToTensor`), the shader reads each tensor element with `tensorReadARM` and writes it to a storage buffer, then the buffer contents are compared element-by-element against the original tensor data ([vktTensorBasicShaderAccess.cpp#L485-L489](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L485-L489), [vktTensorBasicShaderAccess.cpp#L600-L613](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L600-L613)).

For `READ_FROM_BUFFER` (shader_write) tests: a storage buffer is filled with known data, the shader reads each buffer element and writes it to the tensor via `tensorWriteARM`, then the tensor data is downloaded (via `downloadFromTensor`) and compared element-by-element against the buffer data ([vktTensorBasicShaderAccess.cpp#L493-L497](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L493-L497), [vktTensorBasicShaderAccess.cpp#L594-L613](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L594-L613)).

### Optimal tiling tests

Since optimal-tiling tensors are not host-accessible, a two-dispatch approach is used: the first dispatch reads from a source storage buffer and writes into the tensor; the second dispatch reads from the tensor and writes into a destination storage buffer. Verification compares source and destination buffers element-by-element ([vktTensorBasicShaderAccess.cpp#L800-L813](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L800-L813), [vktTensorBasicShaderAccess.cpp#L837-L848](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L837-L848)).

### Stride-aware comparison

The `StridedMemoryUtils<T>` class handles the mapping between flat indices and strided memory positions, ensuring that non-packed tensors with padding between elements are correctly compared. This is used both for tensor data and buffer data ([vktTensorBasicShaderAccess.cpp#L479](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L479)).

## Test principles

1. **Shader tensor read/write correctness**: The core principle is that data written to a tensor via `tensorWriteARM` in a compute shader must be identical to data read back via `tensorReadARM`. This validates the fundamental shader-tensor data path.

2. **Format coverage**: All 8 integer formats (R8/R16/R32/R64, uint/sint) are tested to ensure the format-specific GLSL type mapping and byte-level data layout are correct.

3. **Rank coverage**: Shapes of rank 1 through 4 are tested, plus a dynamic max-rank test that queries the implementation's maximum supported dimension count and constructs a tensor at that rank.

4. **Stride coverage**: Three stride configurations are tested for linear tiling -- implicit packed (empty strides), explicit packed (strides matching the natural layout), and explicit non-packed (padded strides with 13 extra elements per dimension). This ensures both packed and non-packed tensor access work correctly.

5. **Tiling coverage**: Both linear and optimal tilings are tested. Linear tiling allows direct host access for verification; optimal tiling requires a two-dispatch round-trip since the memory layout is opaque.

6. **Allocation offset**: Tests with `tensorOffset = 2000` verify that tensors can be bound at a non-zero offset within a memory allocation, using a custom allocator that respects the `nonCoherentAtomSize` alignment ([vktTensorBasicShaderAccess.cpp#L427-L444](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L427-L444)).

7. **Staging buffer forcing**: Tests with `forceStagingBuffers = true` exercise the staging-buffer upload/download paths even when tensor memory is host-visible, ensuring those code paths are functional.

8. **DMA heap allocation**: Tests with `useDmaHeapAllocator = true` verify that tensors can be backed by DMA heap memory imported via `VK_EXT_external_memory_dma_buf`, including combinations with forced staging and allocation offsets.

9. **Pipeline barriers**: Correct synchronization is validated through appropriate tensor and buffer memory barriers between shader dispatches and host access ([vktTensorBasicShaderAccess.cpp#L555-L578](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L555-L578)).

## Notes/uncertainties

- The naming convention maps `WRITE_TO_BUFFER` to `shader_read` and `READ_FROM_BUFFER` to `shader_write`, which is counterintuitive. The names refer to the shader's perspective: `shader_read` means the shader reads from the tensor, and `shader_write` means the shader writes to the tensor ([vktTensorTestsUtil.cpp#L272-L294](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L272-L294)).

- The non-packed stride padding of 13 elements per dimension is an arbitrary constant chosen to create meaningful padding without excessive memory waste. The specific value 13 is not derived from any hardware constraint observed in the inspected files ([vktTensorBasicShaderAccess.cpp#L888](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L888)).

- The max-rank tests use empty dimensions at registration time (`rank() == 0`) and dynamically compute the shape at instance creation. The shape is `{151, 1, ..., 1, 3, 157}` where the first dimension is 151, the second-to-last is 3, and the last is 157, with all other dimensions set to 1. The shader source cannot be generated without a physical device context, so `initPrograms` returns early in that case ([vktTensorBasicShaderAccess.cpp#L248-L261](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L248-L261)).

- The DMA heap tests only use the `_uint` variant of each format size (r8_uint, r16_uint, r32_uint, r64_uint), not the `_sint` variants, as observed in the inspected files ([vktTensorBasicShaderAccess.cpp#L962](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L962)).

- The forced-staging and offset tests in `addShaderAccessTests` also only use the first format for each template type (`getTestFormats<T>()[0]`), which is the `_uint` variant ([vktTensorBasicShaderAccess.cpp#L918](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L918)).

- The `addDmaHeapBufferAccessTests` function calls `addDmaHeapBufferAccessTestInternal` in the order uint8_t, uint16_t, uint32_t, uint64_t, so the DMA heap tests appear in the hierarchy in that format-size order (r8_uint first, r64_uint last) ([vktTensorBasicShaderAccess.cpp#L1017-L1021](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L1017-L1021)).
