# vktYCbCrImageOffsetTests.cpp

## Overview

Tests that `VkSubresourceLayout::offset` is zero for each plane of a disjoint YCbCr image. When planes are separately bound to memory via `vkBindImageMemory2`, the subresource layout offset for each plane should be zero (since each plane's memory binding starts at the beginning of its allocated memory region).

**Role:** Implementation (registers group `ycbcr.subresource_offset`)

**Source:** [vktYCbCrImageOffsetTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp)

## Registration Hierarchy

```text
ycbcr.subresource_offset
├── g8_b8_r8_3plane_420_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
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

### subresource_offset

Verifies that for a disjoint YCbCr image with linear tiling, `vkGetImageSubresourceLayout` reports an offset of 0 for each plane's subresource. This is a conformance requirement: when disjoint planes are bound separately, each plane's subresource offset should be relative to the start of that plane's memory allocation, not the overall image.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | All formats in `formats::disjointPlanesFormats` | Only formats that support disjoint planes |

**Test Configuration:**

- Image size: 8x8
- Tiling: `VK_IMAGE_TILING_LINEAR`
- Create flags: `VK_IMAGE_CREATE_DISJOINT_BIT`
- Layout: `VK_IMAGE_LAYOUT_PREINITIALIZED`
- Usage: `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`
- Memory: Host-visible, with each plane bound separately via `vkBindImageMemory2` with `VkBindImagePlaneMemoryInfo`

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension
- `VK_FORMAT_FEATURE_DISJOINT_BIT` for the format (linear tiling features)

**Verification Method:**

For each plane (0, 1, 2 as applicable), calls `vkGetImageSubresourceLayout` with the corresponding aspect mask (`VK_IMAGE_ASPECT_PLANE_0_BIT`, etc.) and checks that `subresourceLayout.offset == 0`. A non-zero offset is a test failure.

**Key Functions:**

- [imageOffsetTest()](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93) - Main test implementation
- [initYcbcrImageOffsetTests()](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154) - Test case generation
- [createImageOffsetTests()](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167) - Factory function returning the `subresource_offset` group
