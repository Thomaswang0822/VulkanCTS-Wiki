# ycbcr

## Overview

The [`ycbcr`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L1) category documents Vulkan YCbCr conversion tests registered by [`createTests()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63). In the inspected files, this category covers the `VK_KHR_sampler_ycbcr_conversion` extension (core in Vulkan 1.1), which provides hardware-accelerated YCbCr-to-RGB conversion, multi-planar image support, and chroma subsampling for video and camera content.

## Registration Entry Point

The category is rooted in [`populateTestGroup()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44), which adds eleven subgroups:

```text
ycbcr
├── format
├── filtering
├── plane_view
├── query
├── conversion
├── copy
├── single_plane_copy
├── copy_dimensions
├── storage_image_write
├── subresource_offset
└── misc
```

Source: [`vktYCbCrTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktYCbCrTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L1) | Registration | Top-level ycbcr category registration |
| [`vktYCbCrFormatTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L1) | Implementation | YCbCr format feature tests |
| [`vktYCbCrFilteringTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L1) | Implementation | YCbCr sampling/filtering tests |
| [`vktYCbCrViewTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1) | Implementation | Multi-plane image view tests |
| [`vktYCbCrImageQueryTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L1) | Implementation | Image query tests for multi-planar formats |
| [`vktYCbCrConversionTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1) | Implementation | Sampler YCbCr conversion tests |
| [`vktYCbCrCopyTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1) | Implementation | Copy tests (copy, single_plane_copy, copy_dimensions) |
| [`vktYCbCrStorageImageWriteTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L1) | Implementation | Storage image write tests |
| [`vktYCbCrImageOffsetTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L1) | Implementation | Subresource offset tests |
| [`vktYCbCrMiscTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L1) | Implementation | Miscellaneous tests |
| [`vktYCbCrUtil.cpp`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1) | Helper | Shared YCbCr test utilities |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktYCbCrTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L1) | [`vktYCbCrTests.md`](../testfiles/ycbcr/vktYCbCrTests.md) |
| [`vktYCbCrFormatTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L1) | [`vktYCbCrFormatTests.md`](../testfiles/ycbcr/vktYCbCrFormatTests.md) |
| [`vktYCbCrFilteringTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L1) | [`vktYCbCrFilteringTests.md`](../testfiles/ycbcr/vktYCbCrFilteringTests.md) |
| [`vktYCbCrViewTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1) | [`vktYCbCrViewTests.md`](../testfiles/ycbcr/vktYCbCrViewTests.md) |
| [`vktYCbCrImageQueryTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L1) | [`vktYCbCrImageQueryTests.md`](../testfiles/ycbcr/vktYCbCrImageQueryTests.md) |
| [`vktYCbCrConversionTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1) | [`vktYCbCrConversionTests.md`](../testfiles/ycbcr/vktYCbCrConversionTests.md) |
| [`vktYCbCrCopyTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1) | [`vktYCbCrCopyTests.md`](../testfiles/ycbcr/vktYCbCrCopyTests.md) |
| [`vktYCbCrStorageImageWriteTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L1) | [`vktYCbCrStorageImageWriteTests.md`](../testfiles/ycbcr/vktYCbCrStorageImageWriteTests.md) |
| [`vktYCbCrImageOffsetTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L1) | [`vktYCbCrImageOffsetTests.md`](../testfiles/ycbcr/vktYCbCrImageOffsetTests.md) |
| [`vktYCbCrMiscTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L1) | [`vktYCbCrMiscTests.md`](../testfiles/ycbcr/vktYCbCrMiscTests.md) |

## Subgroup Structure and Major Themes

### [`format`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L592)

Tests YCbCr format feature support, verifying that multi-planar formats report correct `VkFormatProperties` and feature flags.

### [`filtering`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787)

Tests YCbCr texture sampling with various formats, chroma offsets, and filter modes. Verifies that sampled values match expected RGB conversions.

### [`plane_view`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L901)

Tests multi-plane image views, verifying that individual plane views of multi-planar images produce correct results when sampled or used as attachments.

### [`query`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L603)

Tests image query operations on multi-planar formats, verifying that `vkGetImageSubresourceLayout` returns correct plane layouts.

### [`conversion`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192)

The largest subgroup, testing `VkSamplerYcbcrConversion` with:
- Color space conversions (BT.601, BT.709, BT.2020)
- Chroma reconstruction (explicit/implicit)
- Range reduction (full/luma/narrow)
- Sampler arrays and one-to-one mappings

### [`copy`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023)

Copy operation tests for multi-planar images, including default copy, single-plane copy, and dimension-specific copy variants.

### [`storage_image_write`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939)

Tests writing to YCbCr storage images from compute shaders, verifying that multi-planar formats can be used as storage images.

### [`subresource_offset`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167)

Tests subresource offset calculations for multi-planar images with mip levels and array layers.

### [`misc`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366)

Miscellaneous tests including relaxed precision handling for YCbCr conversion results.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| YCbCr formats | `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM`, `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, `VK_FORMAT_G8_B8R8_2PLANE_422_UNORM` |
| Chroma subsampling | 4:4:4, 4:2:2, 4:2:0 |
| Color spaces | BT.601, BT.709, BT.2020 |
| Chroma offsets | Cosited even, midpoint |
| Range | Full, luma, narrow |
| Filter modes | Nearest, linear |
| Plane counts | 1-plane, 2-plane, 3-plane |

## Recurring Support Requirements

- `VK_KHR_sampler_ycbcr_conversion` (core in Vulkan 1.1)
- `VK_KHR_maintenance1` for some view tests
- `VK_KHR_format_feature_flags2` for format tests
- `VK_EXT_ycbcr_2plane_444_formats` for 4:4:4 2-plane formats
- `VK_EXT_ycbcr_image_arrays` for array-layer YCbCr images
- `shaderStorageImageWriteWithoutFormat` for storage image write tests

## Recurring Verification Methods

- CPU reference conversion from YCbCr to RGB, compared against GPU-sampled values
- Image comparison with threshold tolerance for floating-point precision
- Format property validation against spec requirements
- Layout offset verification for multi-planar subresources

## Notes / Uncertainties

- Some packed 422 formats (e.g., `G8B8G8R8_422`) are remapped to compatible formats for storage image access.
- The `misc` group currently contains only a single test (`relaxed_precision`) but is designed to accommodate additional tests.
