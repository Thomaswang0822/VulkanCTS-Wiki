# [vktImageAstcDecodeModeTests.cpp](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1)

## Overview

[`vktImageAstcDecodeModeTests.cpp`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.astc_decode_mode` subtree. It tests the `VK_EXT_astc_decode_mode` extension, which allows overriding the decode mode for ASTC-compressed textures at image view creation time. The tests verify that ASTC textures can be decoded with different precision modes (UNORM, SFLOAT, E5B9G9R9) and produce expected results.

## Role of File

- **Role:** implementation-heavy test file
- **Primary source:** [`vktImageAstcDecodeModeTests.cpp`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1)
- **Header:** [`vktImageAstcDecodeModeTests.hpp`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.hpp#L1)
- **Registration context:** registered under `image` in [`vktImageTests.cpp`](../../../../modules/vulkan/image/vktImageTests.cpp) as `astc_decode_mode` group via [`createImageAstcDecodeModeTests()`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L488-L618)

## Source Code

- Implementation: [vktImageAstcDecodeModeTests.cpp](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1)
- Header: [vktImageAstcDecodeModeTests.hpp](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.hpp#L1)

## Registration Hierarchy

```text
image.astc_decode_mode
├── 4x4_unorm_to_r16g16b16a16_sfloat
├── 4x4_unorm_to_r8g8b8a8_unorm
├── 4x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 4x4_srgb_to_r16g16b16a16_sfloat
├── 4x4_srgb_to_r8g8b8a8_unorm
├── 4x4_srgb_to_e5b9g9r9_ufloat_pack32
... (all ASTC format to decode mode combinations)
└── 12x12_srgb_to_e5b9g9r9_ufloat_pack32
```

## Test Families

### 2D ASTC format tests

Covers the 2D ASTC format tests registered by [`createImageAstcDecodeModeTests()`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L572-L591). Tests use `IMAGE_TYPE_2D` with 64x64 pixel resolution. Covers all 2D ASTC block formats (4x4 through 12x12, both UNORM and SRGB variants) with all three decode modes.

### 3D ASTC format tests (non-VulkanSC only)

Covers the 3D ASTC format tests registered by [`createImageAstcDecodeModeTests()`](../../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L592-L615). Tests use `IMAGE_TYPE_3D` with 64x64x3 resolution. Covers all 3D ASTC block formats with all three decode modes. Skips invalid combinations where ASTC sfloat format is decoded to r8g8b8a8_unorm.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Image type | `IMAGE_TYPE_2D`, `IMAGE_TYPE_3D` | [Line 577](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L577), [Line 600](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L600) |
| Image size (2D) | `UVec3(64u, 64u, 1u)` | [Line 578](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L578) |
| Image size (3D) | `UVec3(64u, 64u, 3u)` | [Line 601](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L601) |
| 2D ASTC formats | 4x4 through 12x12, UNORM and SRGB variants | [Lines 497-526](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L497-L526) |
| 3D ASTC formats | 3x3x3 through 6x6x6, UNORM, SRGB, SFLOAT variants | [Lines 528-559](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L528-L559) |
| Decode modes | `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_E5B9G9R9_UFLOAT_PACK32` | [Lines 567-569](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L567-L569) |
| Tested image usage | `VK_IMAGE_USAGE_TRANSFER_SRC_BIT \| VK_IMAGE_USAGE_TRANSFER_DST_BIT \| VK_IMAGE_USAGE_SAMPLED_BIT` | [Lines 583-584](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L583-L584), [Lines 606-607](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L606-L607) |
| Result image usage | `VK_IMAGE_USAGE_STORAGE_BIT` | [Lines 586](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L586), [Line 609](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L609) |

## Support / Feature Requirements

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_EXT_astc_decode_mode` | All ASTC decode mode tests | [Line 397](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L397) |
| `textureCompressionASTC_LDR` | All ASTC format tests | [Lines 398-399](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L398-L399) |
| `decodeModeSharedExponent` | Tests using `VK_FORMAT_E5B9G9R9_UFLOAT_PACK32` decode mode | [Lines 414-416](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L414-L416) |
| `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` | Result format must support storage images | [Lines 418-422](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L418-L422) |

## Verification Methods

- **Shader-based comparison:** Compute shader compares decoded values from both tested view (with decode mode) and reference view (default decode), outputting 0.5 for matching or 0.0 for mismatches
- **Expected value range check:** Result pixels are checked to be in range 100-150 (expected ~128 for matching decode modes)
- **Distance comparison:** Uses `distance()` function with threshold of 0.01 to determine if decoded values match between tested and reference views

## Test Principles Observed

- **Decode mode override:** Image view is created with `VkImageViewASTCDecodeModeEXT` structure to override the default ASTC decode behavior
- **Dual sampling:** Both tested view (with decode mode) and reference view (default) are sampled and results compared
- **Special case handling:** Shader handles special cases for UNORM and SFLOAT ASTC formats when decoded to E5B9G9R9 (clamping negative values to zero, setting alpha to 1, clamping excess values)
- **Compute pipeline:** Uses compute shader for the comparison and verification

## Notes / Uncertainties

- 3D ASTC tests are only available on non-VulkanSC builds
- Invalid combinations (ASTC sfloat with r8g8b8a8_unorm decode) are skipped
- The result image format is always `VK_FORMAT_R8G8B8A8_UNORM` with storage image usage for verification
- Tests verify decode mode functionality rather than specific pixel values, using comparison thresholds
