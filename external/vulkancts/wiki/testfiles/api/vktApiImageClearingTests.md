# [vktApiImageClearingTests.cpp](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)

## Overview

Tests Vulkan image clearing commands: vkCmdClearColorImage, vkCmdClearDepthStencilImage, and vkCmdClearAttachments. Covers a wide range of color and depth/stencil formats, image types, tilings, layer configurations, and allocation strategies.

## Role of File

Implementation-heavy. Contains all test logic, helper types, and the registration function [createImageClearingTests()](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204).

## Source Code

- Implementation: [vktApiImageClearingTests.cpp](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)
- Header: [vktApiImageClearingTests.hpp](../../../../../modules/vulkan/api/vktApiImageClearingTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L110)

## Registration Path

```
api
  +-- image_clearing
```

## Test Hierarchy

```
image_clearing
  +-- core
  |     +-- clear_color_image
  |     |     +-- <imageType>
  |     |           +-- <tiling>
  |     |                 +-- <layerConfig>
  |     |                       +-- <format><dimensions><colorSuffix>[_multiple_subresourcerange][_4_samples]
  |     +-- clear_depth_stencil_image
  |     |     +-- <format><dimensions><colorSuffix>
  |     +-- clear_color_attachment
  |     |     +-- <format><dimensions><colorSuffix>
  |     +-- clear_depth_stencil_attachment
  |     |     +-- <format><dimensions>
  |     +-- partial_clear_color_attachment
  |     |     +-- <format><dimensions><colorSuffix>
  |     +-- partial_clear_depth_stencil_attachment
  |           +-- <format><dimensions>
  +-- dedicated_allocation
        +-- (same structure as core)
```

## Test Families

### Clear Color Image

[ClearColorImageTestInstance](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224) tests vkCmdClearColorImage across all mandatory color formats, image types (1D, 2D, 3D), tilings (optimal, linear), layer configurations, and dimensions. Tests include multiple subresource range variants and MSAA variants for 2D images.

### Clear Depth/Stencil Image

Tests vkCmdClearDepthStencilImage with depth/stencil formats (D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT).

### Clear Color Attachment

Tests vkCmdClearAttachments for color attachments within a render pass, including partial clears and multi-layer configurations.

### Clear Depth/Stencil Attachment

Tests vkCmdClearAttachments for depth/stencil aspects, including separate depth/stencil layout modes and partial clears.

### Partial Clear Attachment

Tests partial clears of color and depth/stencil attachments using VkClearRect with specific layer ranges.

### Dedicated Allocation

The `dedicated_allocation` subgroup repeats the same test structure using dedicated memory allocation instead of suballocation, created by [createDedicatedAllocationImageClearingTests()](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3197).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| AllocationKind | ALLOCATION_KIND_SUBALLOCATED, ALLOCATION_KIND_DEDICATED |
| Image type | 1D, 2D, 3D |
| Image tiling | OPTIMAL, LINEAR |
| Color formats | 90+ formats from R4G4_UNORM_PACK8 through A4B4G4R4_UNORM_PACK16_EXT |
| Depth/stencil formats | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT |
| Image dimensions | 256x1x1, 256x256x1, 256x256x16, 200x1x1, 200x180x1, 200x180x16, 71x1x1, 1x33x1, 55x21x11, 64x11x1, 33x128x1, 32x29x3 |
| Layer config | single_layer, multiple_layers, cube_layers, remaining_array_layers, remaining_array_layers_twostep |
| Clear color params | default, clamp_input (for unsigned fixed-point) |
| Sample count | 1, 4 (for 2D MSAA variants) |
| 64-bit format | R64_UINT, R64_SINT, R64G64_UINT, R64G64_SINT |
| Separate depth/stencil layout | NONE, SEPARATE_DEPTH, SEPARATE_STENCIL, SEPARATE_DEPTH_STENCIL |
| 2D array compatible | true, false (for 3D images) |
| General layout | true, false (for 2D images) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_EXT_separate_depth_stencil_layouts | Depth/stencil tests with separate layout mode |
| VK_KHR_maintenance1 | 2D array compatible image tests |
| VK_EXT_4444_formats | A4R4G4B4_UNORM_PACK16_EXT, A4B4G4R4_UNORM_PACK16_EXT formats |
| VK_KHR_maintenance5 | Dynamic rendering variants (if applicable) |
| VK_EXT_shader_object | Shader object variants (if applicable) |

## Verification Methods

- **Pixel comparison**: After clearing, image contents are read back and compared against expected clear values
- **Threshold comparison**: Some formats use tolerance-based comparison via Threshold union
- **Multiple subresource range**: Verifies that clearing with two separate subresource ranges produces correct results
- **Two-step clear**: Verifies that VK_REMAINING_ARRAY_LAYERS works correctly across two separate clear commands

## Test Principles Observed

- Comprehensive format coverage: tests all mandatory Vulkan formats
- Multi-dimensional parameterization: image type, tiling, dimensions, and layer configs are all varied
- Allocation strategy coverage: both suballocated and dedicated allocation are tested
- Edge case coverage: VK_REMAINING_ARRAY_LAYERS, 64-bit formats, clamp-input values for unsigned formats
- MSAA coverage: sample count 4 is tested for 2D images

## Notes / Uncertainties

- The file is very large (3218 lines); the test hierarchy above shows the structural pattern but individual test names are auto-generated from format, dimension, and color parameters
- Some compressed formats (BC, ETC2, EAC, ASTC) are commented out in the format list at [lines 2368-2421](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2368) due to tcu::TextureFormat limitations
- R64_SFLOAT, R64G64_SFLOAT, and larger 64-bit formats are also commented out
- The `createImageClearingTestsCommon()` function at [line 2224](../../../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224) is the shared implementation for both core and dedicated_allocation groups
