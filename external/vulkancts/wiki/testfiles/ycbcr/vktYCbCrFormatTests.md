# vktYCbCrFormatTests.cpp

## Overview

Tests basic YCbCr multi-planar format sampling across all Vulkan YCbCr formats. Each test creates a YCbCr image, uploads gradient data, samples it through a combined image sampler with a `VkSamplerYcbcrConversion`, and verifies the shader output against a software reference rasterizer.

**Role:** Implementation (registers group `ycbcr.format`)

**Source:** [vktYCbCrFormatTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp)

## Registration Hierarchy

```text
ycbcr.format
├── g8b8g8r8_422_unorm
├── b8g8r8g8_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
├── r12x4g12x4b12x4a12x4_unorm_4pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g16b16g16r16_422_unorm
├── b16g16r16g16_422_unorm
├── g16_b16_r16_3plane_420_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g8_b8r8_2plane_444_unorm
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
└── g16_b16r16_2plane_444_unorm
```

## Test Families

### format

Verifies that sampling a YCbCr image through a `VkSamplerYcbcrConversion` produces correct results for each supported multi-planar format. The test uses `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY` with `VK_SAMPLER_YCBCR_RANGE_ITU_FULL` and nearest filtering.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | `VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST`, plus `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM_EXT` through `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT` | All YCbCr multi-planar formats |
| Shader Type | vertex, fragment, geometry, tessellation_control, tessellation_evaluation, compute | All shader stages; descriptor modes are filtered by `executorSupported()` |
| Tiling | optimal, linear | `VK_IMAGE_TILING_OPTIMAL` and `VK_IMAGE_TILING_LINEAR` |
| Disjoint | false, true | `VK_IMAGE_CREATE_DISJOINT_BIT` (multi-plane formats only) |
| Mapped Memory | false, true | Host-visible memory mapping (linear tiling only) |
| Array Layers | false, true | 2-layer image arrays (requires `VK_EXT_ycbcr_image_arrays`) |
| Descriptor Mode | descriptor set, descriptor buffer, descriptor heap | Descriptor buffer and descriptor heap variants are non-VulkanSC only and use `_descriptor_buffer` / `_descriptor_heap` suffixes |

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension and `samplerYcbcrConversion` feature
- `VK_FORMAT_FEATURE_MIDPOINT_CHROMA_SAMPLES_BIT` for the format
- `VK_EXT_ycbcr_image_arrays` for array layer tests
- `VK_EXT_descriptor_buffer` for descriptor-buffer variants
- `VK_EXT_descriptor_heap` for descriptor-heap variants
- `DEVICE_CORE_FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS` for vertex/tessellation/geometry shader stages
- `maxArrayLayers >= 2` for array layer tests

**Verification Method:**

Shader execution via `ShaderExecutor`. Results are compared against a software reference using `tcu::Texture2DView::sample()` with a threshold of 0.02f per channel. The test also verifies that `combinedImageSamplerDescriptorCount >= 1` via `VkSamplerYcbcrConversionImageFormatProperties`. The descriptor mode controls whether execution uses descriptor sets, `executeBuffer()`, or `executeHeap()`.

**Key Functions:**

- [testFormat()](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L353) - Main test implementation
- [checkSupport()](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L312) - Format, array-layer, shader-stage, and descriptor-mode support checks
- [populatePerFormatGroup()](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L640) - Per-format test case generation, including descriptor-buffer and descriptor-heap suffix variants
- [populateFormatGroup()](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L712) - Top-level format group population
- [createFormatTests()](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L734) - Factory function returning the `format` group
