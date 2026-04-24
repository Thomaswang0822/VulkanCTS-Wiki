# [vktApiImageClearingTests.cpp](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)

## Overview

Tests Vulkan image clearing commands: `vkCmdClearColorImage`, `vkCmdClearDepthStencilImage`, and `vkCmdClearAttachments` (full and partial). Validates that cleared pixel values match expected results across a wide range of formats, image types, tiling modes, layer configurations, and allocation strategies.

## Role of File

Implementation-heavy. Contains all test instance classes, comparison utilities, and the registration function in a single large source file (~3218 lines). The public entry point [createImageClearingTests()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204) assembles the full test tree.

## Source Code

- Source: [vktApiImageClearingTests.cpp](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)
- Header: [vktApiImageClearingTests.hpp](../../modules/vulkan/api/vktApiImageClearingTests.hpp#L1)
- Parent registration: `api` test group, child `image_clearing`

## Registration Path

```
api
 +-- image_clearing
      +-- core
      +-- dedicated_allocation
```

## Test Hierarchy

```
image_clearing
 +-- core
 |    +-- clear_color_image
 |    |    +-- <1d|2d|3d>
 |    |         +-- <optimal|linear>
 |    |              +-- <single_layer|multiple_layers|remaining_array_layers|remaining_array_layers_twostep>
 |    |                   +-- <format_dimensions[_clamp_input][_multiple_subresourcerange][_sample_count_4]>
 |    +-- clear_depth_stencil_image
 |    |    +-- <2d|3d>
 |    |         +-- <single_layer|multiple_layers|remaining_array_layers|remaining_array_layers_twostep>
 |    |              +-- <format[_separate_layouts_depth|_separate_layouts_stencil]_dimensions[_multiple_subresourcerange]>
 |    +-- clear_color_attachment
 |    |    +-- <single_layer|multiple_layers|cube_layers>
 |    |         +-- <format_dimensions[_clamp_input]>
 |    +-- clear_depth_stencil_attachment
 |    |    +-- <single_layer|multiple_layers|cube_layers>
 |    |         +-- <format[_separate_layouts_depth|_separate_layouts_stencil]_dimensions>
 |    +-- partial_clear_color_attachment
 |    |    +-- <single_layer|multiple_layers|cube_layers>
 |    |         +-- <format_dimensions[_clamp_input]>
 |    +-- partial_clear_depth_stencil_attachment
 |         +-- <single_layer|multiple_layers|cube_layers>
 |              +-- <format[_separate_layouts_depth|_separate_layouts_stencil]_dimensions>
 +-- dedicated_allocation
      +-- (same structure as core)
```

## Test Families

### Clear Color Image Family

Tests `vkCmdClearColorImage` across image types (1D, 2D, 3D), tiling modes (optimal, linear), and layer configurations. Uses [ClearColorImageTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1594) for standard clears, [TwoStepClearColorImageTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1609) for two-step remaining-layers clears, and [ClearColorImageMultipleSubresourceRangeTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1618) for per-mip-level subresource range clears. Includes MSAA variants with `VK_SAMPLE_COUNT_4_BIT` for 2D optimal images.

### Clear Depth/Stencil Image Family

Tests `vkCmdClearDepthStencilImage` for 2D and 3D images with depth/stencil formats. Uses [ClearDepthStencilImageTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1827), [TwoStepClearDepthStencilImageTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1841), and [ClearDepthStencilImageMultipleSubresourceRangeTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1850). Supports separate depth/stencil layout modes via `VK_KHR_separate_depth_stencil_layouts`.

### Clear Attachment Family

Tests `vkCmdClearAttachments` for both color and depth/stencil attachments within a render pass. Uses [ClearAttachmentTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1978) for full clears and [PartialClearAttachmentTestInstance](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2111) for partial (cross-pattern) clears. Supports cube layer configurations.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Image Type | 1D, 2D, 3D |
| Image Tiling | optimal, linear |
| Allocation Kind | suballocated, dedicated |
| Image Dimensions | 256x1x1, 256x256x1, 256x256x16, 200x1x1, 200x180x1, 200x180x16, 71x1x1, 1x33x1, 55x21x11, 64x11x1, 33x128x1, 32x29x3 |
| Layer Config | single_layer (1), multiple_layers (16, range 3-12), cube_layers (15, range 3-6), remaining_array_layers (16, range 8+), remaining_array_layers_twostep |
| Color Formats | ~90+ formats from R4G4_UNORM_PACK8 through E5B9G9R9_UFLOAT_PACK32, plus A4R4G4B4/A4B4G4R4 EXT, A8_UNORM_KHR, A1B5G5R5_UNORM_PACK16_KHR |
| Depth/Stencil Formats | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT |
| Clear Color | default (0.1,0.5,0.3,0.9 / 0.3,0.6,0.2,0.7), clamp_input (negative values clamped to 0) |
| Separate DS Layout | none, depth_only, stencil_only |
| Sample Count | 1, 4 (MSAA variants for 2D optimal) |
| 2D Array Compatible | true/false (randomly for 3D images) |
| General Layout | true/false (randomly for 2D images) |

## Support / Feature Requirements

- Format must support `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` and `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` ([checkSupport()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L517))
- `VK_KHR_dedicated_allocation` required for dedicated allocation tests ([checkSupport()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L528))
- `VK_KHR_separate_depth_stencil_layouts` required for separate DS layout tests ([checkSupport()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L531))
- `VK_KHR_maintenance5` required for `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` ([checkSupport()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L522))
- Attachment clear tests require format to support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` or `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`

## Verification Methods

- Pixel-level comparison via [verifyResultImage()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1317) which reads back image data and compares against expected clear values
- Color comparison uses threshold-based checks via [comparePixelToColorClearValue()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L336) with channel-class-specific logic (fixed-point threshold, integer exact match, floating-point ULP)
- Depth comparison via [comparePixelToDepthClearValue()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L263) with bit-depth-aware thresholds
- Stencil comparison via [comparePixelToStencilClearValue()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L318) with exact match
- Partial clear verification uses [isInClearRange()](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L197) to check cross-pattern clear regions

## Test Principles Observed

- Comprehensive format coverage with ~90+ color formats and 7 depth/stencil formats
- Layer range testing including `VK_REMAINING_ARRAY_LAYERS` with two-step clear pattern
- Multiple subresource range testing for per-mip-level clears
- Clamped input testing for unsigned fixed-point formats (negative values clamped to zero)
- 64-bit format support with packed comparison logic
- MSAA multisample image clearing with pre-clear via `cmdClearColorImage`
- Separate depth/stencil layout mode testing

## Notes / Uncertainties

- Compressed formats (BC, ETC2, EAC, ASTC) are commented out in the format list and not tested ([colorImageFormatsToTest](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2368))
- Some 64-bit float formats (R64_SFLOAT, R64G64_SFLOAT, etc.) are commented out due to framework limitations ([colorImageFormatsToTest](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2356))
- The `create2DArrayCompatible` and `generalLayout` flags are set pseudo-randomly based on loop indices rather than explicit test parameters ([line 2666-2682](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2666))
- Helper functions `calcFloatDiff`, `comparePixelToDepthClearValue`, `comparePixelToStencilClearValue`, `comparePixelToColorClearValue` are noted as copied from vktRenderPassTests.cpp ([line 245-262](../../modules/vulkan/api/vktApiImageClearingTests.cpp#L245))
