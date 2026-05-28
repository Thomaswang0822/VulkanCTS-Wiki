# vktTextureConversionTests.cpp

## Overview

Tests for texture format conversion behavior, including handling of negative values in UFLOAT packed formats, SNORM clamping during sampling, and SNORM clamping during linear filtering.

## Role

Implementation file

## Source Code

- [vktTextureConversionTests.cpp](../../../modules/vulkan/texture/vktTextureConversionTests.cpp)

## Registration Hierarchy

```text
texture.conversion
├── ufloat_negative_values (non-VulkanSC only)
├── snorm_clamp (non-VulkanSC only)
└── snorm_clamp_linear
```

## Test Families

### ufloat_negative_values

Populated by `populateUfloatNegativeValuesTests` at [line 429](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L429). Non-VulkanSC only.

Contains 1 Amber test case:

- `b10g11r11` - Tests VK_FORMAT_B10G11R11_UFLOAT_PACK32 with negative float values
  - Amber data dir: `texture/conversion/ufloat_negative_values`, file: `b10g11r11-ufloat-pack32.amber`

### snorm_clamp

Populated by `populateSnormClampTests` at [line 431](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L431). Non-VulkanSC only.

Contains 13 Amber test cases, one per SNORM format:

- a2b10g10r10_snorm_pack32
- a2r10g10b10_snorm_pack32
- a8b8g8r8_snorm_pack32
- b8g8r8a8_snorm
- b8g8r8_snorm
- r16g16b16a16_snorm
- r16g16b16_snorm
- r16g16_snorm
- r16_snorm
- r8g8b8a8_snorm
- r8g8b8_snorm
- r8g8_snorm
- r8_snorm

Amber data dir: `texture/conversion/snorm_clamp`

### snorm_clamp_linear

Populated by `populateSnormLinearClampTests` at [line 433](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L433).

Contains 26 test cases (13 formats x 2 pipeline types: graphics + compute). Same 13 SNORM formats as snorm_clamp, each with a `_compute` variant.

- Test class: `SnormLinearClampTestCase` / `SnormLinearClampInstance`
- Params: format, width, height, useCompute
- Render size varies per format via sizeMultiplier starting at 20, incrementing by 2

## Parameter Dimensions

| Family | Format | Pipeline | Render Size |
|--------|--------|----------|-------------|
| snorm_clamp_linear | 13 SNORM formats | graphics, compute | varies by sizeMultiplier (base 20, +2 per format) |

## Support / Feature Requirements

- **ufloat_negative_values** and **snorm_clamp**: guarded by `#ifndef CTS_USES_VULKANSC`
- **snorm_clamp_linear**: NOT guarded by `#ifndef CTS_USES_VULKANSC` — available on VulkanSC. [checkSupport](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L270-L279) checks `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` for the format's optimal tiling features

## Verification Methods

- **ufloat_negative_values** and **snorm_clamp**: Amber-based verification
- **snorm_clamp_linear**: Two-stage verification in [SnormLinearClampInstance::verifyPixels](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L145-L215):
  1. Texture lookup difference using `glu::TextureTestUtil::computeTextureLookupDiff` with precision:
     - lodPrec.derivateBits=18, lodPrec.lodBits=5
     - lookupPrec.uvwBits=(5,5,0), lookupPrec.coordBits=(20,20,0)
  2. Out-of-range check: verifies no rendered pixel falls outside [-1.0, +1.0]
  - Pass only if both `numFailedPixels==0` and `numOutOfRangePixels==0`

## Notes

- **ufloat_negative_values**: Validates UFLOAT packed formats correctly handle negative float values during conversion
- **snorm_clamp**: Validates SNORM minimum negative integer correctly clamps to -1.0 when sampled
- **snorm_clamp_linear**: Validates linear filtering of SNORM textures correctly clamps to [-1.0, +1.0] post-interpolation, using carefully constructed 7x7 texture with extreme SNORM values
