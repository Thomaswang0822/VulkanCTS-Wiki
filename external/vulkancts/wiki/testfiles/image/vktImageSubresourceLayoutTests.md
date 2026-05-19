# vktImageSubresourceLayoutTests.cpp

## Overview

Tests for `vkGetImageSubresourceLayout` API and related functions. This file verifies that the Vulkan implementation correctly reports memory layout parameters for image subresources, including offsets, row pitches, array pitches, and depth pitches. The tests also validate invariance between different subresource layout query functions.

## Role of File

This is a registration and implementation file that:
- Registers the `subresource_layout` test group
- Provides test cases for validating subresource layout queries
- Tests multiple image types, mip levels, and formats
- Includes invariance tests comparing different layout query APIs (non-VulkanSC)

## Source Code Link

[vktImageSubresourceLayoutTests.cpp](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp)

## Registration Hierarchy

```text
image.subresource_layout
├── 2d
�?  ├── 1_level
�?  ├── 2_levels
�?  ├── 4_levels
�?  └── all_levels
├── 2d_array
�?  ├── 1_level
�?  ├── 2_levels
�?  ├── 4_levels
�?  └── all_levels
└── 3d
    ├── 1_level
    ├── 2_levels
    ├── 4_levels
    └── all_levels
```

Additional `invariance` subgroup (non-VulkanSC only) contains tests for `VK_KHR_maintenance5` APIs.

## Test Families

### basic_subresource_layout �?Subresource Layout Query Tests

Tests the accuracy of `vkGetImageSubresourceLayout` by:
1. Creating a linear-tiling image with multiple mipmap levels
2. Filling levels with unique random data appropriate to each format
3. Querying subresource layout parameters (offset, size, rowPitch, arrayPitch, depthPitch)
4. Verifying layout parameter consistency across array layers
5. Reading back image data and comparing with original buffer data

**Key test logic** ([vktImageSubresourceLayoutTests.cpp#L412-L692](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L412-L692)):
- Tests each supported aspect (color, depth, stencil) per format
- Validates array pitch consistency across layers
- Checks offset consistency with array pitch calculations
- Verifies minimum size requirements for subresources
- Validates row pitch, array pitch, and depth pitch are sufficient
- Compares image data byte-by-byte with source buffer data

### invariance �?Layout Query Invariance Tests (non-VulkanSC only)

Verifies that different subresource layout query methods return identical results:
1. `vkGetImageSubresourceLayout` (standard API)
2. `vkGetDeviceImageSubresourceLayoutKHR` (VK_KHR_maintenance5)
3. `vkGetImageSubresourceLayout2EXT` (VK_EXT_image_compression_control)

**Key test logic** ([vktImageSubresourceLayoutTests.cpp#L714-L787](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L714-L787)):
- Creates an image and queries layout using the standard API
- Queries layout using maintenance5 API without image handle
- Compares results byte-by-byte
- If VK_EXT_image_compression_control is supported, also tests the 2EXT variant

## Parameter Dimensions

| Parameter | Values |
|-----------|--------|
| Image Types | VK_IMAGE_TYPE_2D, VK_IMAGE_TYPE_3D |
| Image Classes | 2D, 2D_array, 3D |
| Mip Level Configurations | 1, 2, 4, all_possible |
| Formats | formats::basicColorFormats (excluding depth/stencil) |
| Default 2D Dimensions | 240 x 320 x 1 |
| Default 2D Array Dimensions | 32 x 48 x 56 layers |
| Default 3D Dimensions | 32 x 48 x 56 |
| Image Offset Variants | false (no offset), true (with memory offset) |

## Support Requirements

- **Required format features** ([vktImageSubresourceLayoutTests.cpp#L200-L204](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L200-L204)):
  - `VK_FORMAT_FEATURE_TRANSFER_DST_BIT`
  - `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT`
  - For linear tiling images

- **Image tiling**: `VK_IMAGE_TILING_LINEAR`

- **Conditional requirements**:
  - `VK_KHR_maintenance5` for formats VK_FORMAT_A8_UNORM_KHR and VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR
  - `VK_KHR_maintenance5` for invariance tests
  - `VK_EXT_image_compression_control` for 2EXT variant (optional, tested if supported)

- **Format restrictions**: Depth/stencil formats excluded because their texel size is implementation-dependent

## Verification Methods

1. **Layout parameter validation**:
   - Array pitch consistency check across layers at the same mip level
   - Offset verification against array pitch calculations
   - Minimum size verification (size >= pixelSize * numPixels)
   - Row pitch minimum check (rowPitch >= pixelSize * width)
   - Array pitch minimum check for multi-layer images
   - Depth pitch minimum check for 3D images

2. **Data integrity verification**:
   - Pixel-by-pixel comparison between buffer and image data
   - Special handling for 24-bit formats (X8_D24_UNORM, D24_S8_UINT)
   - Masking of unused bits for 24-bit depth formats

3. **Invariance verification** (non-VulkanSC):
   - Byte-by-byte comparison of `VkSubresourceLayout` structures
   - Tested across multiple query method variants

## Test Principles Observed

- Linear tiling images used to ensure predictable memory layouts
- Random data generation with format-appropriate constraints (avoiding denormals for floating-point)
- Separate test variants with and without image memory offset to catch alignment-related issues
- Each mip level tested independently as a separate subresource
- All supported aspects (color, depth, stencil) tested per format

## Notes

- The file creates two test instances per format per mip configuration: one without offset and one with image memory offset
- Invariance tests are conditionally compiled out for VulkanSC due to VK_KHR_maintenance5 not being available
- Test data uses deterministic random seeding based on format and aspect for reproducibility
