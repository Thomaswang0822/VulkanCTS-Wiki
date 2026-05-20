# vktTextureCompressedFormatTests.cpp

## Overview

Tests compressed texture (ETC2, EAC, ASTC, BC) sampling and verification for both 2D and 3D textures. Verifies that GPU correctly decodes compressed blocks by comparing against a software reference decoder. This file registers two top-level groups: `compressed` and `compressed_3D`.

## Role

Implementation file

## Source Code

- [vktTextureCompressedFormatTests.cpp](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp)
- Factory: [createTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L721)
- Factory: [create3DTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L726)
- Populate: [populateTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L604)
- Populate: [populate3DTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L658)

## Registration Hierarchy

```text
texture.compressed
texture.compressed_3D
```

Both groups have flat leaf test cases (no sub-groups). The `compressed` group uses naming pattern `{format}_2d_{size}{backingMode}` generated from 54 formats × 3 sizes × 2 backing modes × 2 pipeline types, plus ASTC void extent variants. The `compressed_3D` group uses naming pattern `{format}_3d_{size}{backingMode}` with the same parameter matrix, plus ASTC 3D format variants (non-VulkanSC only).

## Test Families

### Compressed 2D

Compressed2DTestInstance. Tests sampling and verification of 2D compressed textures (ETC2, EAC, ASTC, BC).

- 54 formats: 6 ETC2, 4 EAC, 28 ASTC 2D (14 block sizes x UNORM/SRGB), 16 BC
- 3 sizes: pot (128x64x8), npot (51x65x17), npot_mip1 (51x65x17 with mipmaps)
- 2 backing modes: regular, sparse (non-VulkanSC)
- Filters: NEAREST_MIPMAP_NEAREST / NEAREST
- Compute shader variants for each test
- ASTC void extent block variants
- Test name pattern: `{format}_2d_{size}{backingMode}` and `{format}_2d_compute_{size}{backingMode}_compute`
- ASTC formats also have void extent variants: `{format}_voidextent_2d_{size}{backingMode}` and `_compute` suffix

Source: [lines 156-429](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L156-L429)

### Compressed 3D

Compressed3DTestInstance. Tests sampling and verification of 3D compressed textures across multiple Z-slices.

- Same 54 formats for base 3D tests
- 30 ASTC 3D formats (non-VulkanSC): 10 block sizes (3x3x3 through 6x6x6) x 3 data types (UNORM/SRGB/SFLOAT_EXT)
- Same 3 sizes and 2 backing modes
- Tests 3 slices of the 3D texture at evenly spaced Z positions
- Base 3D tests: compute shader variants (`_compute` suffix), filters NEAREST_MIPMAP_NEAREST / NEAREST
- ASTC 3D tests: graphics only (no compute variants), filters NEAREST / NEAREST (no mipmapping)
- Test name pattern: `{format}_3d_{size}{backingMode}` and `{format}_3d_{size}{backingMode}_compute` (base formats only)

Source: [lines 431-600](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L431-L600)

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Formats (2D) | 54: 6 ETC2, 4 EAC, 28 ASTC 2D (14 block sizes x UNORM/SRGB), 16 BC |
| Formats (3D base) | 54 (same as 2D) |
| Formats (3D ASTC, non-VulkanSC) | 30: 10 block sizes (3x3x3 through 6x6x6) x 3 data types (UNORM/SRGB/SFLOAT_EXT) |
| Sizes | 3: pot (128x64x8), npot (51x65x17), npot_mip1 (51x65x17 with mipmaps) |
| Backing modes | 2: regular, sparse (non-VulkanSC) |
| Pipeline types | 2: graphics, compute (base formats); graphics only (ASTC 3D) |
| Filters | NEAREST_MIPMAP_NEAREST / NEAREST (base); NEAREST / NEAREST (ASTC 3D) |

## Support/Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| Compressed2D | No explicit checkSupport; relies on texture creation failing if format unsupported |
| ASTC LDR | Requires textureCompressionASTC_LDR |
| ASTC 3D (non-VulkanSC) | Requires VK_EXT_texture_compression_astc_3d AND textureCompressionASTC_3D==VK_TRUE |
| ETC2/EAC | Requires textureCompressionETC2 |
| BC | Requires textureCompressionBC |

Compressed3D support checks at construction time: [lines 460-508](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L460-L508)

## Verification Methods

validateTexture() template:

1. Compute software reference using sampleTexture()
2. For each rendered pixel, compute texture coordinates and sample neighborhood within coordThreshold (0.01f)
3. Compare rendered color against reference neighborhood using compareColor() with per-channel colorThreshold
4. Build error mask (green=match, red=mismatch)
5. Log results with scale/bias normalization

Threshold values:

| Format category | Color threshold (RGBA) |
|----------------|----------------------|
| BC bit-exact (BC6H_UFLOAT, BC6H_SFLOAT, BC7_UNORM, BC7_SRGB) | (1,1,1,1) |
| BC sRGB (3D only: BC1_RGB_SRGB, BC1_RGBA_SRGB, BC2_SRGB, BC3_SRGB) | (9,9,9,9) |
| BC other | (8,8,8,8) |
| All other (ETC2, EAC, ASTC) | pixelFormat.getColorThreshold() + (2,2,2,2) |

Coord threshold: 0.01f

Source: [lines 248-349](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L248-L349)

## Notes

- Compressed texture decoding - GPU correctly decodes compressed blocks by comparing against software reference decoder
- Coordinate tolerance for rasterization differences
- Mipmap testing via npot_mip1 size
- Void extent blocks for ASTC
- Compute shader path verification
- 3D depth slicing
- Both groups have flat leaf test cases (no sub-groups); test names encode all parameter dimensions
