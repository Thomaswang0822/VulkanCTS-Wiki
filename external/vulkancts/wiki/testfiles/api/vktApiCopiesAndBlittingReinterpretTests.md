# vktApiCopiesAndBlittingReinterpretTests ([source](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp))

## Overview

Tests that verify the correctness of image data reinterpretation through format-mutable image views during copy and sampling operations. The file exercises the scenario where an image is created with one format but accessed through an image view of a different, size-compatible format -- both during `vkCmdCopyImage` and during fragment shader sampling via `texelFetch`. This verifies that implementations correctly handle the `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` and `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` flags when copying and sampling reinterpreted image data.

## Role of File

This file provides the test implementation and registration for format reinterpretation tests in the Vulkan CTS `api` test group. It contains one test instance class, one test case class, and one registration function. The tests verify both the copy result (destination image data matches source) and the sampling result (fragment shader reads the reinterpreted data correctly).

## Source Code

- Implementation: [vktApiCopiesAndBlittingReinterpretTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp)
- Header: [vktApiCopiesAndBlittingReinterpretTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.hpp)

## Registration Path

```
api > copy_and_blit > reinterpret
```

The top-level registration function `createReinterpretationTests` at [line 1119](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1119) creates the `reinterpret` group. This is registered directly under `copy_and_blit` in [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) at [line 289](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L289).

## Test Hierarchy

```
reinterpret
|-- 1d
|   |-- copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat
|   |-- copy_bc1_rgb_unorm_block_sample_r32g32_uint
|   |-- copy_bc3_unorm_block_sample_r32g32b32a32_uint
|-- 2d
    |-- copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat
    |-- copy_bc1_rgb_unorm_block_sample_r32g32_uint
    |-- copy_bc3_unorm_block_sample_r32g32b32a32_uint
```

## Test Families

### Reinterpret Copy + Sample (ReinterpretTestInstance)

Registered in `createReinterpretationTests` at [line 1119](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1119). Uses `ReinterpretTestCase` at [line 886](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L886) and `ReinterpretTestInstance` at [line 35](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L35).

| Family | Description |
|--------|-------------|
| copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat | Uncompressed B10G11R11_UFLOAT image copied and sampled through R16G16_SFLOAT view |
| copy_bc1_rgb_unorm_block_sample_r32g32_uint | BC1 compressed image copied and sampled through R32G32_UINT view (64-bit block) |
| copy_bc3_unorm_block_sample_r32g32b32a32_uint | BC3 compressed image copied and sampled through R32G32B32A32_UINT view (128-bit block) |

Each test performs two verifications:
1. **Copy verification**: The destination image data is read back and compared against the expected result computed by `copyRegionToTextureLevel` at [line 152](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L152)
2. **Sampling verification**: The source image is sampled via fragment shader `texelFetch` using the view format, and the result is compared against the expected reinterpreted data at [line 847](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L847)

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Type | VK_IMAGE_TYPE_1D, VK_IMAGE_TYPE_2D | [line 1139](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1139) |
| Image Format / View Format Pairs | B10G11R11_UFLOAT_PACK32 / R16G16_SFLOAT, BC1_RGB_UNORM_BLOCK / R32G32_UINT, BC3_UNORM_BLOCK / R32G32B32A32_UINT | [line 1128](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1128) |
| Tiling | VK_IMAGE_TILING_OPTIMAL only | [line 896](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L896) |
| Allocation Kind | ALLOCATION_KIND_SUBALLOCATED only | [line 897](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L897) |
| Queue Selection | Universal only | [line 898](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L898) |
| Image Extent | default1dExtent (1D), defaultExtent (2D) | [line 1139](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1139) |
| Copy Region | Single whole-image copy region | [line 1173](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1173) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT | Required when image format differs from view format | [line 92](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L92), [line 127](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L127) |
| VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT | Required for compressed format images | [line 95](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L95), [line 131](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L131) |
| VK_IMAGE_CREATE_EXTENDED_USAGE_BIT | Required for compressed format images | [line 96](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L96), [line 132](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L132) |
| VK_KHR_maintenance2 | Required for compressed format images (extended usage) | [line 924](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L924) |
| Image format properties | vkGetPhysicalDeviceImageFormatProperties must succeed for the format/tiling/usage/flags | [line 931](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L931) |
| View format properties | vkGetPhysicalDeviceImageFormatProperties must succeed for the view format | [line 940](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L940) |
| maxImageDimension1D / maxImageDimension2D | Image dimensions must not exceed limits | [line 953](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L953), [line 963](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L963) |
| COPY_COMMANDS_2 extension | Checked via checkExtensionSupport | [line 948](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L948) |

## Verification Methods

### Uncompressed Format Verification (Copy)

Uses CPU-side reference comparison via `tcu::floatThresholdCompare` at [line 144](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L144) with a threshold of 0.01. The `copyRegionToTextureLevel` method at [line 152](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L152) computes the expected result by treating `vkCmdCopyImage` as a memcpy: the destination format is replaced with the source format at [line 210](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L210) to perform a byte-for-byte copy.

### Uncompressed Format Verification (Sampling)

Uses CPU-side reference comparison via `tcu::floatThresholdCompare` at [line 847](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L847) with a threshold of 0.01. The expected data is generated by creating a texture level in the source format and then reinterpreting it through the view format at [line 529](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L529).

### Compressed Format Verification (Copy)

Uses a compute shader to verify the destination image at [line 316](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L316). The `compVerify` shader at [line 1090](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1090) reads the destination image through the view format, compares each texel against the expected value, and writes green (match) or red (mismatch) to an R8G8B8A8_UNORM output image. The output image is then read back and compared against an all-green reference at [line 461](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L461).

### Compressed Format Verification (Sampling)

Same compute shader verification approach, but applied to the render output image at [line 854](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L854).

## Test Principles Observed

- **Dual verification**: Every test verifies both the copy result and the sampling result independently at [line 818](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L818) and [line 839](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L839). A failure in either check causes the test to fail.
- **Format reinterpretation**: The core test principle is that `vkCmdCopyImage` acts as a memcpy at [line 209](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L209), so the destination data should be byte-identical to the source data regardless of format differences. The `copyRegionToTextureLevel` method replaces the destination format with the source format to model this behavior.
- **MUTABLE_FORMAT_BIT**: When the image format differs from the view format, `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is added at [line 92](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L92) and [line 127](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L127).
- **BLOCK_TEXEL_VIEW_COMPATIBLE_BIT**: For compressed formats, `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` are added at [line 95](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L95) and [line 131](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L131), enabling the image to be viewed as an uncompressed format.
- **Compressed image fill**: Compressed images cannot be filled via `uploadImage`, so a compute shader (`compFill`) at [line 1070](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1070) is used to write known data patterns (blue for source, red for destination) via storage image writes.
- **Compressed block size handling**: The test distinguishes between 64-bit blocks (BC1) and 128-bit blocks (BC3) at [line 1054](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1054), using different view formats and verification patterns for each.
- **Command variants**: Both `vkCmdCopyImage` and `vkCmdCopyImage2` (COPY_COMMANDS_2) are supported at [line 761](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L761).

## Notes / Uncertainties

- The test constrains several parameters via DE_ASSERT at [line 895](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L895): source and destination formats must be identical, tiling must be optimal, allocation must be suballocated, queue must be universal, and various other flags must be at their defaults. This means the test only exercises the format reinterpretation scenario, not the full parameter space of copy operations.
- Only three format pairs are tested at [line 1128](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1128): one uncompressed pair (B10G11R11_UFLOAT / R16G16_SFLOAT) and two compressed pairs (BC1 / R32G32_UINT and BC3 / R32G32B32A32_UINT). Other format reinterpretation combinations are not covered.
- The `formatsAreCompatible` function at [line 881](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L881) checks that the pixel sizes match, but for compressed formats this check is bypassed at [line 1151](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1151) because the view format represents the block size rather than the texel size.
- The compressed image verification uses hardcoded color values (blue for source, red for destination) at [line 1057](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1057) rather than the `generateBuffer` / `FILL_MODE` mechanism used for uncompressed images.
- 3D image types are not tested in this file.
- The test does not exercise `vkCmdBlitImage` with reinterpreted formats, only `vkCmdCopyImage`.
