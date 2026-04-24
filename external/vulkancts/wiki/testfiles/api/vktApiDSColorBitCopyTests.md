# [vktApiDSColorBitCopyTests.cpp](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1)

## Overview

Tests depth/stencil to/from color image bit copies using vkCmdCopyImage, verifying that pixel data is preserved bit-exactly across format conversions between depth/stencil and compatible color image formats. Covers multiple mip levels, queue types (universal, compute-only, transfer-only), and attachment vs. transfer-only usage flags.

## Role of File

Implementation-heavy. Contains the full test infrastructure including format group definitions, random value generation, image/buffer creation, command buffer submission, pixel comparison logic, and the registration entry point.

## Source Code

- Implementation: [vktApiDSColorBitCopyTests.cpp](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1)
- Header: [vktApiDSColorBitCopyTests.hpp](../../modules/vulkan/api/vktApiDSColorBitCopyTests.hpp#L1)
- Registration function: [createDSColorBitCopyTests()](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L875)
- Registered under: api -> ds_color_bit_copy

## Registration Path

```
api
+-- ds_color_bit_copy
    +-- ds_color_copy
```

## Test Hierarchy

```
ds_color_copy
+-- d32_sfloat_r32_sfloat_depth_level0_to_level0
+-- d32_sfloat_r32_sfloat_depth_level0_to_level0_unrestricted
+-- d32_sfloat_r32_sfloat_depth_level0_to_level0_att_usage
+-- d32_sfloat_r32_sfloat_depth_level0_to_level0_cq
+-- d32_sfloat_r32_sfloat_depth_level0_to_level0_tq
+-- d32_sfloat_r32_sfloat_depth_level3_to_level0
+-- ... (many more format/direction/mip/queue combinations)
+-- r32_sfloat_d32_sfloat_depth_level0_to_level0
+-- ... (color-to-DS direction variants)
+-- s8_uint_r8_uint_stencil_level0_to_level0
+-- ... (stencil variants)
```

## Test Families

### ds_color_copy (single family, heavily parameterized)

Creates a source image (depth/stencil or color), fills it with pseudorandom pixel values, copies to a destination image (color or depth/stencil) via vkCmdCopyImage, reads back the destination, and performs bit-exact pixel-by-pixel comparison. Handles special cases: for transfer-only queues with depth/stencil source images, uses a staging image workaround because vkCmdCopyBufferToImage is not allowed on transfer queues for DS formats (VUID-vkCmdCopyBufferToImage-commandBuffer-07739).

- Instance: [DSColorCopyInstance](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L285)
- Case: [DSColorCopyCase](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L304)
- iterate(): [L604-L869](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L604)
- checkSupport(): [L362-L505](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L362)
- Staging workaround: [L718-L747](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L718)

Format groups defined at [getFormatGroups()](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L67):

| Group | Aspect | DS Formats | Color Formats |
|---|---|---|---|
| 32-bit depth | DEPTH_BIT | D32_SFLOAT, D32_SFLOAT_S8_UINT | R32_SFLOAT, R32_SINT, R32_UINT |
| 24-bit depth | DEPTH_BIT | X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT | R32_SFLOAT, R32_SINT, R32_UINT |
| 16-bit depth | DEPTH_BIT | D16_UNORM, D16_UNORM_S8_UINT | R16_SFLOAT, R16_UNORM, R16_SNORM, R16_UINT, R16_SINT |
| 8-bit stencil | STENCIL_BIT | S8_UINT, D32_SFLOAT_S8_UINT, D24_UNORM_S8_UINT, D16_UNORM_S8_UINT | R8_UINT, R8_SINT, R8_UNORM, R8_SNORM |

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|---|---|---|
| formatGroup | 4 groups (32-bit depth, 24-bit depth, 16-bit depth, 8-bit stencil) | [L67-L114](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L67) |
| dsFormat | Varies per group (2-4 formats) | [L79-L111](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L79) |
| colorFormat | Varies per group (3-5 formats) | [L80-L111](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L80) |
| dsToColor | true, false | Direction of copy; [L883](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L883) |
| srcMipLevel | 0u, 3u | [L884](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L884) |
| dstMipLevel | 0u, 3u | [L885](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L885) |
| attUsage | false, true | Skipped if srcMipLevel or dstMipLevel != 0; [L886-L888](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L886) |
| queueType | UNIVERSAL, COMPUTE_ONLY, TRANSFER_ONLY | COMPUTE_ONLY and TRANSFER_ONLY skipped on VKSC; [L900-L907](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L900) |
| unrestricted | false (always for non-32-bit); false, true (for 32-bit) | [L919-L923](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L919) |

## Support / Feature Requirements

| Requirement | Where | Context |
|---|---|---|
| VK_KHR_maintenance8 | [L501](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L501) | All tests |
| VK_EXT_depth_range_unrestricted | [L503-L504](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L503) | When unrestricted=true |
| VK_KHR_maintenance10 | [L384](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L384) | Non-universal queue types |
| VK_KHR_format_feature_flags2 | [L385](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L385) | Non-universal queue types |
| Format support check | [L339-L360](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L339) | Per-format image format properties |
| DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR | [L405-L406](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L405) | Compute queue + DS source |
| STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR | [L415-L416](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L415) | Compute queue + DS source stencil |
| DEPTH_COPY_ON_TRANSFER_QUEUE_BIT_KHR | [L455-L456](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L455) | Transfer queue + DS source |
| STENCIL_COPY_ON_TRANSFER_QUEUE_BIT_KHR | [L464-L465](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L465) | Transfer queue + DS source stencil |
| Compute queue availability | [L400](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L400) | COMPUTE_ONLY queue type |
| Transfer queue availability | [L449](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L449) | TRANSFER_ONLY queue type |

## Verification Methods

- **Bit-exact pixel comparison**: Compares every pixel in the source buffer against the destination buffer after the copy, using bit-exact matching via the [PixelValue](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L507) struct. For 24-bit depth, masks to 0xFFFFFF ([L528](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L528)). Mismatches are logged with coordinates and hex values ([L856-L863](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L856)).
- **Full image comparison**: Iterates over all pixels in the 16x16 base extent ([L850-L864](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L850)).

## Test Principles Observed

- **Bit-exact verification**: Uses raw bit comparison rather than tolerance-based comparison, appropriate for copy operations that must preserve data exactly ([L536-L550](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L536))
- **Pseudorandom data generation**: Uses seeded PRNG with format-aware value generation (e.g., snorm ranges for SNORM formats, depth range restrictions) at [L121-L175](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L121)
- **Queue family coverage**: Tests universal, compute-only, and transfer-only queues with appropriate format feature flag checks ([L900-L907](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L900))
- **Staging workaround for VUID compliance**: When using transfer-only queue with DS source, uses a staging image on the universal queue to work around VUID-vkCmdCopyBufferToImage-commandBuffer-07739 ([L718-L747](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L718))
- **Mip level testing**: Tests both base level (0) and a non-trivial mip level (3) to exercise mip-level copy paths ([L884-L885](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L884))

## Notes / Uncertainties

- The base image extent is fixed at 16x16x1 ([L607](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L607)). The actual image sizes are scaled by the mip level (e.g., 128x128 for level 3), but the copy region is always the 16x16 base extent.
- For D32 formats with unrestricted=true, the test uses depth values up to 10.0f ([L118](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L118)), which requires VK_EXT_depth_range_unrestricted. Without that extension, D32 values are limited to [0.125, 1.0].
- On VKSC builds, COMPUTE_ONLY and TRANSFER_ONLY queue types are skipped due to VUs *-10217 and *-10218 ([L903-L907](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L903)).
- The attachment usage flag (attUsage) is only tested at mip level 0 because attachment usage with non-zero mip levels is skipped ([L888-L889](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L888)).
- The seed for the PRNG is derived from the format pair, aspect, and mip levels ([L894-L898](../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L894)), making test results deterministic and reproducible.
