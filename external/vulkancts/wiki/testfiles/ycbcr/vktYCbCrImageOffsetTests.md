# vktYCbCrImageOffsetTests.cpp

## Overview

[`vktYCbCrImageOffsetTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp) implements the `ycbcr.subresource_offset` subgroup returned by [`createImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167-L170). It creates linear disjoint YCbCr images, binds each plane separately with an aligned nonzero memory offset, and verifies plane subresource layout offsets in [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L139).

## Registration Hierarchy

```text
ycbcr.subresource_offset
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
└── g8_b8r8_2plane_444_unorm
```

`initYcbcrImageOffsetTests()` registers one direct child per format in `formats::disjointPlanesFormats`, using source-derived lowercase format names in [`initYcbcrImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L162).

## Test Families

### subresource_offset

The test allocates separate memory for each plane, binds with `vkBindImageMemory2` and `VkBindImagePlaneMemoryInfo`, then queries each plane aspect using `vkGetImageSubresourceLayout` in [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L139).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Format | `formats::disjointPlanesFormats` in [`initYcbcrImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L162). |
| Image setup | The image size is `8x8`, memory is host-visible, and per-plane memory requirements are used in [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L98-L118). |
| Plane aspects | Plane aspects are selected from `VK_IMAGE_ASPECT_PLANE_0_BIT`, `VK_IMAGE_ASPECT_PLANE_1_BIT`, and `VK_IMAGE_ASPECT_PLANE_2_BIT` in [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L136-L139). |

## Support Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L61-L69) requires `VK_KHR_sampler_ycbcr_conversion` and linear-tiling `VK_FORMAT_FEATURE_DISJOINT_BIT` support for the tested format.

## Verification Method

The verification is source-local: after per-plane binding, [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L134-L139) iterates plane aspects and checks the returned `VkSubresourceLayout::offset` for each plane; nonzero offsets are failures in the continuation of that same function.

## Notes / Uncertainties

This page intentionally narrows the claim to linear disjoint images because the support check uses `linearTilingFeatures` in [`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L64-L68).
