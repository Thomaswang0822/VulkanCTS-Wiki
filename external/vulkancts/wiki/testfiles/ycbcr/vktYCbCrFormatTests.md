# vktYCbCrFormatTests.cpp

## Overview

[`vktYCbCrFormatTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp) implements the `ycbcr.format` subgroup returned by [`createFormatTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L734-L737). Each test creates a YCbCr image, binds memory, constructs a `VkSamplerYcbcrConversion` using RGB identity/full range/midpoint/nearest parameters, samples through a combined image sampler, and compares shader results with a software texture reference in [`testFormat()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L353-L590).

## Registration Hierarchy

```text
ycbcr.format
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── b16g16r16g16_422_unorm
├── b8g8r8g8_422_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g16b16g16r16_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8r8_2plane_444_unorm
├── g8b8g8r8_422_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
└── r12x4g12x4b12x4a12x4_unorm_4pack16
```

`populateFormatGroup()` iterates `VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST` and the 2-plane 444 EXT range, creating one direct child per source-derived format name in [`populateFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L712-L729).

## Test Families

### format

Per-format case generation covers all executor-supported shader stages, optimal and linear tiling, array-layer variants, disjoint variants for multi-plane formats, mapped linear-memory variants, and descriptor-set/buffer/heap binding modes in [`populatePerFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L640-L710).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Formats | `VK_YCBCR_FORMAT_FIRST` to `VK_YCBCR_FORMAT_LAST`, plus `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM_EXT` to `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT` in [`populateFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L714-L729). |
| Shader type | Vertex, fragment, geometry, tessellation control, tessellation evaluation, and compute stages are listed, then filtered by `executorSupported()` in [`populatePerFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L643-L672). |
| Tiling and memory | Optimal and linear tiling are generated; mapped-memory cases are generated only for linear tiling in [`populatePerFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L674-L705). |
| Array layers | Array variants use two array layers in [`testFormat()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L363-L365) and are gated by `VK_EXT_ycbcr_image_arrays` plus `maxArrayLayers >= 2` in [`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L316-L326). |
| Descriptor mode | Descriptor-set, descriptor-buffer, and descriptor-heap modes are generated in [`populatePerFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L655-L665) and executed by `execute()`, `executeBuffer()`, or `executeHeap()` in [`testFormat()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L557-L578). |

## Support Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L312-L337) delegates image support to shared [`checkImageSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L176-L201), requires `VK_EXT_ycbcr_image_arrays` and two array layers for array cases, requires `DEVICE_CORE_FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS` for vertex/tessellation/geometry execution, and gates descriptor-buffer/heap variants on `VK_EXT_descriptor_buffer` and `VK_EXT_descriptor_heap`.

## Verification Method

[`testFormat()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L353-L590) uploads gradient data, verifies `combinedImageSamplerDescriptorCount >= 1` using `VkSamplerYcbcrConversionImageFormatProperties`, executes the selected shader/descriptor path, and compares each available channel against `tcu::Texture2DView::sample()` with a `0.02f` threshold.

## Notes / Uncertainties

The generated case tree is runtime-filtered by executor and device support, so this page documents the source generator rather than an exact mustpass-expanded case count.
