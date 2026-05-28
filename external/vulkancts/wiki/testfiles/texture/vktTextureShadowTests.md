# vktTextureShadowTests.cpp

## Overview

Tests texture shadow (depth comparison) sampling across 1D, 2D, cube map, and array texture types with various filter modes, compare operations, and formats. Verifies that GPU depth comparison results match CPU-computed PCF reference values.

## Role

Implementation file

## Source Code

- [vktTextureShadowTests.cpp](../../../modules/vulkan/texture/vktTextureShadowTests.cpp)
- Factory: [createTextureShadowTests](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L2080)
- Populate: [populateTextureShadowTests](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1729)

## Registration Hierarchy

```text
texture.shadow
├── 2d
├── cube
├── 2d_array
├── 1d
├── 1d_array
├── cube_array
└── texel_replacement (non-VulkanSC only)
```

## Test Families

### 2d

2D texture shadow lookup tests. Texture2DShadowTestInstance.

- Sub-groups by filter mode: nearest, linear, nearest_mipmap_nearest, linear_mipmap_nearest, nearest_mipmap_linear, linear_mipmap_linear
- Leaf tests parameterized by compare op, format, and backing mode
- Texture: 32x64

Source: [lines 1795-1837](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1795-L1837)

### cube

Cube map texture shadow lookup tests. TextureCubeShadowTestInstance.

- Same filter sub-groups as 2d
- Tests each face, with seamless/non-seamless modes
- Texture: 32x32 cube

Source: [lines 1838-1883](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1838-L1883)

### 2d_array

2D array texture shadow lookup tests. Texture2DArrayShadowTestInstance.

- Same filter sub-groups
- Layer interpolation
- Texture: 32x64, 8 layers

Source: [lines 1884-1927](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1884-L1927)

### 1d

1D texture shadow lookup tests. Texture1DShadowTestInstance.

- Same filter sub-groups
- No sparse backing (VUID-VkImageCreateInfo-imageType-00970)
- Texture: 32x1

Source: [lines 1928-1973](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1928-L1973)

### 1d_array

1D array texture shadow lookup tests. Texture1DArrayShadowTestInstance.

- Same filter sub-groups
- No sparse backing
- Texture: 32x1, 8 layers

Source: [lines 1974-2021](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1974-L2021)

### cube_array

Cube map array texture shadow lookup tests. TextureCubeArrayShadowTestInstance.

- Same filter sub-groups
- Seamless/non-seamless modes
- Texture: 32x32, 24 layers (4*6)

Source: [lines 2022-2068](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L2022-L2068)

### texel_replacement

Texel replacement amber test (non-VulkanSC only).

- D32_SFLOAT texel replacement test

Source: [lines 2069-2077](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L2069-L2077)

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Formats | 8: D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT, R16_UNORM, R32_SFLOAT |
| Filter modes | 6: nearest, linear, nearest_mipmap_nearest, linear_mipmap_nearest, nearest_mipmap_linear, linear_mipmap_linear |
| Compare ops | 8: less_or_equal, greater_or_equal, less, greater, equal, not_equal, always, never |
| Backing modes | 2: regular, sparse (1D and 1D_array skip sparse) |
| Seamless modes | 2: seamless, non_seamless (cube and cube_array only; requires VK_EXT_non_seamless_cube_map) |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| Non-VulkanSC | Requires VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_DEPTH_COMPARISON_BIT_KHR |
| VulkanSC | Checks isDepthFormat(format) |
| Sparse backing | Requires DEVICE_CORE_FEATURE_SPARSE_BINDING + SPARSE_RESIDENCY_IMAGE2D |
| Non-seamless | Requires VK_EXT_non_seamless_cube_map |

## Verification Methods

Two-tier PCF comparison via verifyTexCompareResult():

**Tier 1 (high quality)**: tcu::TexComparePrecision + tcu::LodPrecision with tight tolerances, computeTextureCompareDiff()
- 2D: coordBits=(20,20,0), uvwBits=(7,7,0), pcfBits=5, refBits=16, lodBits=6, derivateBits=18
- Cube: coordBits=(10,10,10), uvwBits=(6,6,0), pcfBits=5, refBits=16, lodBits=5, derivateBits=10
- 2D Array: coordBits=(20,20,20), uvwBits=(7,7,7), pcfBits=5, refBits=16, lodBits=6, derivateBits=18
- 1D: coordBits=(20,0,0), uvwBits=(7,0,0), pcfBits=5, refBits=16, lodBits=6, derivateBits=18
- 1D Array: coordBits=(20,20,20), uvwBits=(7,7,7), pcfBits=5, refBits=16, lodBits=6, derivateBits=18
- Cube Array: coordBits=(10,10,10), uvwBits=(6,6,0), pcfBits=5, refBits=16, lodBits=5, derivateBits=10

**Tier 2 (low precision fallback)**: lodBits reduced to 4, uvwBits reduced to 4, pcfBits reduced to 0.

**D32_SFLOAT and D32_SFLOAT_S8_UINT**: Depth values clamped to [0,1] before reference sampling.

**VulkanSC**: Verification only runs in subprocess mode.

## Notes

- Shadow comparison - fragment shader performs depth comparison between reference value and texture depth value
- Multiple filter cases with varying LODs, reference values (in-range, out-of-bounds), and texture indices
- Iterative execution (one FilterCase per call)
- Cube map tests iterate over all 6 faces
