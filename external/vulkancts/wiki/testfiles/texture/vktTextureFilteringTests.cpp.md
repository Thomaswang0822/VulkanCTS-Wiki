# vktTextureFilteringTests.cpp

## Overview

Tests texture filtering behavior across different texture types (2D, cube map, 2D array, 3D) with various filter modes, wrap modes, formats, and coordinate spaces. Verifies that GPU texture sampling matches CPU-computed reference results using exact LOD mode.

## Role

Implementation file

## Source Code

- [vktTextureFilteringTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp)
- Factory: [createTextureFilteringTests](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L2079)
- Populate: [populateTextureFilteringTests](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1207)

## Registration Hierarchy

```text
texture.filtering
├── 2d
├── unnormal
├── cube
├── 2d_array
└── 3d
```

## Test Families

### 2d

2D texture filtering tests. Sub-groups: formats, sizes, combinations.

- Tests 2D texture sampling with various formats, sizes, filter modes, and wrap mode combinations
- Both graphics and compute shader variants (_compute suffix)
- 9 min filter modes (including cubic), 3 mag filter modes (including cubic)
- 6 sizes: {4,8}, {32,64}, {128,128}, {3,7}, {31,55}, {127,99}
- 16 filterable formats
- 5 wrap modes: repeat, mirrored_repeat, clamp_to_edge, clamp_to_border, mirror_clamp_to_edge
- Seamless variants: seamless, non_seamless

Source: [lines 1322-1470](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1322-L1470)

### unnormal

Unnormalized coordinate texture filtering tests. Sub-groups: formats, sizes.

- Tests 2D texture sampling with unnormalized coordinates (unnormal=true)
- Only mag filter modes (nearest, linear, cubic) -- no mipmap modes
- Wrap modes restricted to CLAMP_TO_EDGE or CLAMP_TO_BORDER

Source: [lines 1472-1565](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1472-L1565)

### cube

Cube map texture filtering tests. Sub-groups: formats, sizes, combinations, no_edges_visible.

- Tests cube map texture sampling with seamless/non-seamless variants
- no_edges_visible group tests with onlySampleFaceInterior=true (nearest/linear only)
- 6 min filter modes (no cubic), 2 mag filter modes
- 5 cube sizes: {8}, {64}, {128}, {7}, {63}

Source: [lines 1567-1770](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1567-L1770)

### 2d_array

2D array texture filtering tests. Sub-groups: formats, sizes, combinations.

- Tests 2D array texture sampling across multiple layers
- 5 sizes: {4,8,8}, {32,64,16}, {128,32,64}, {3,7,5}, {63,63,63}

Source: [lines 1772-1918](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1772-L1918)

### 3d

3D texture filtering tests. Sub-groups: formats, sizes, combinations.

- Tests 3D texture sampling with wrapR in addition to wrapS/wrapT
- 5 sizes: {4,8,8}, {32,64,16}, {128,32,64}, {3,7,5}, {63,63,63}

Source: [lines 1920-2076](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1920-L2076)

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Filter modes (2D) | 9 min (nearest, linear, cubic, nearest_mipmap_nearest, linear_mipmap_nearest, nearest_mipmap_linear, linear_mipmap_linear, cubic_mipmap_nearest, cubic_mipmap_linear), 3 mag (nearest, linear, cubic) |
| Filter modes (cube/2d_array/3d) | 6 min, 2 mag |
| Wrap modes | 5 (repeat, mirrored_repeat, clamp_to_edge, clamp_to_border, mirror_clamp_to_edge) |
| Formats | 16 filterable formats |
| Seamless | {seamless, non_seamless} |

## Support/Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| Cubic filtering | Requires VK_EXT_filter_cubic, checks filterCubic property and VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_CUBIC_BIT_EXT |
| Mirror clamp to edge | Requires VK_KHR_sampler_mirror_clamp_to_edge |
| RGBA10X6 format | Requires formatRgba10x6WithoutYCbCrSampler from VK_EXT_rgba10x6_formats (non-VulkanSC) |
| Non-seamless cube map | Requires VK_EXT_non_seamless_cube_map when seamless==false |
| Verifier skip | Integer channel class formats + linear/cubic filtering are skipped |

## Verification Methods

Two-tier image comparison:

**High-precision**: verifyTextureResult() from tcu::TexVerifierUtil, compares rendered vs reference via tcu::Texture2DView/CubeView/2DArrayView/3DView
- 2D precision: coordBits=(20,20,0), uvwBits=(7,7,0), derivateBits=18, lodBits=6
- Cube precision: coordBits=(10,10,10), uvwBits=(6,6,0), derivateBits=10, lodBits=5

**Low-precision fallback**: lodBits=4, uvwBits=(4,4,0) or (4,4,4)

**VulkanSC**: Verification only runs in subprocess mode.

## Notes

- Render-and-compare with CPU-computed reference using exact LOD mode
- Two-texture approach (gradient + grid pattern)
- Multiple LOD cases per test
- Dual pipeline (graphics + compute)
- Stencil aspect testing for depth-stencil formats
