# vktTextureMipmapTests.cpp

## Overview

Tests texture mipmap filtering behavior across 2D, cube map, and 3D texture types with different coordinate types, LOD controls, and image view min LOD extension. Verifies that GPU mipmap filtering matches CPU-computed reference results using grid-based verification.

## Role

Implementation file

## Source Code

- [vktTextureMipmapTests.cpp](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp)
- Factory: [createTextureMipmappingTests](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L4198)
- Populate: [populateTextureMipmappingTests](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L3343)

## Registration Hierarchy

```text
texture.mipmap
├── 2d
├── cubemap
├── 3d
└── min_lod_gather (non-VulkanSC only)
```

## Test Families

### 2d

2D mipmap tests. Sub-groups: basic, affine, projected (coord types), bias, min_lod, max_lod, base_level, max_level, image_view_min_lod (non-VulkanSC).

- Tests 2D mipmap filtering with different coordinate types, LOD controls, and image view min LOD extension

Source: [lines 3411-3686](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L3411-L3686)

### cubemap

Cube map mipmap tests. Sub-groups: basic, projected, bias (coord types), min_lod, max_lod, base_level, max_level, misc, image_view_min_lod (non-VulkanSC).

- misc contains projected_derivatives test using textureGrad
- No affine coordinate type for cube maps

Source: [lines 3688-3910](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L3688-L3910)

### 3d

3D mipmap tests. Sub-groups: basic, affine, projected (coord types), bias, min_lod, max_lod, base_level, max_level, image_view_min_lod (non-VulkanSC).

- Tests 3D mipmap filtering with different coordinate types, LOD controls, and image view min LOD extension

Source: [lines 3912-4187](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L3912-L4187)

### min_lod_gather

textureGather with minLod tests (non-VulkanSC only). Sub-groups: minlod_0_1, minlod_1_1.

- Tests textureGather with VK_EXT_image_view_min_lod
- Each sub-group has component_0 through component_3

Source: [lines 4189-4195](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L4189-L4195)

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Coordinate types (2D/3D) | COORDTYPE_BASIC, COORDTYPE_AFFINE, COORDTYPE_PROJECTED |
| Coordinate types (cube) | COORDTYPE_BASIC, COORDTYPE_PROJECTED, COORDTYPE_BASIC_BIAS |
| Min filter modes | nearest_nearest, linear_nearest, nearest_linear, linear_linear (4 modes) |
| Mag filter modes | nearest, linear (2 modes) |
| Wrap modes | clamp, repeat, mirror (3 modes) |
| 2D sizes | {64,64}, {63,57}, {32,64} |
| 3D sizes | {32,32,32}, {33,29,27} |
| Cube size | 64 |
| Bias values (all types) | {1.0, -2.0, 0.8, -0.5, 1.5, 0.9, 2.0, 4.0} (8 values per grid) |
| MinLOD values | 16 values per grid cell |
| MaxLOD values | 17 values per grid cell |

## Support/Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_image_view_min_lod | Required for all image_view_min_lod sub-tests (checks minLod feature bit) |
| VK_EXT_robustness2 | Required for TextureGatherMinLodTest when minLod >= 1.0 (checks robustImageAccess2) |
| VulkanSC exclusions | All image_view_min_lod groups and min_lod_gather group excluded |

## Verification Methods

**Mipmap filtering tests**: computeTextureLookupDiff() from tcu::TexLookupVerifier
- 2D precision: coordBits=(20,20,0), uvwBits=(16,16,0), derivateBits=10, lodBits=8 (basic) or 6 (projected)
- Cube precision: coordBits=(8-10), uvwBits=(5,5,0), derivateBits=10, lodBits=6 (basic) or 3 (projected)
- 3D precision: coordBits=(20,20,20), uvwBits=(16,16,16), derivateBits=10, lodBits=8 (basic) or 6 (projected)
- Tolerance for cube seams: up to 16 failed pixels (projected) or 1024 (bias) in compute-only mode; 0 in graphics mode

**LOD control tests**: Same computeTextureLookupDiff() approach.

**Gather minLod tests**: Creates 3-level 8x8 texture with unique colors per level, renders single pixel via textureGather, compares output against expected level.

## Notes

- Grid-based verification (4x4 grid, each cell has different LOD parameters)
- Colored level textures (each mipmap level has unique solid color)
- LOD control hierarchy: basic -> bias -> min/max LOD -> base/max level -> image view min LOD
- Dual pipeline (graphics + compute), except cubemap compute variants are skipped for projected and bias coordinate types due to inaccurate calculations
