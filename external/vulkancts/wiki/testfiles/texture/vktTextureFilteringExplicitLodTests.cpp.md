# vktTextureFilteringExplicitLodTests.cpp

## Overview

Tests for 2D texture filtering with explicit LOD and explicit gradient (derivative) instructions, using per-sample mathematical verification against device-aware precision bounds.

## Role

Implementation file

## Source Code

- [vktTextureFilteringExplicitLodTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp)

## Registration Hierarchy

```text
texture.explicit_lod
└── 2d
```

The `2d` group contains 3 sub-groups (sizes, formats, derivatives) which are one level below the root expansion and not listed as separate mustpass entries.

## Test Families

### 2d

Created by `create2DTests` at [line 1398](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1398). Contains 3 sub-groups: sizes, formats, derivatives.

#### 2d.formats

[Lines 1150-1201](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1150-L1201). Tests 2D texture filtering with explicit LOD across 19 formats.

- 19 formats:
  - B4G4R4A4_UNORM_PACK16, R5G6B5_UNORM_PACK16, A1R5G5B5_UNORM_PACK16
  - R8_UNORM, R8_SNORM, R8G8_UNORM, R8G8_SNORM
  - R8G8B8A8_UNORM, R8G8B8A8_SNORM, B8G8R8A8_UNORM
  - A8B8G8R8_UNORM_PACK32, A8B8G8R8_SNORM_PACK32
  - A2B10G10R10_UNORM_PACK32
  - R16_SFLOAT, R16G16_SFLOAT, R16G16B16A16_SFLOAT
  - R32_SFLOAT, R32G32_SFLOAT, R32G32B32A32_SFLOAT
- Uses `Texture2DGradientTestCase` with useDerivatives=false (explicit LOD mode)
- 7 LOD values: {-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0}
- Each format tested with nearest and linear filtering, in both graphics and compute pipelines

#### 2d.derivatives

[Lines 1203-1288](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1203-L1288). Tests 2D texture filtering with explicit gradient (derivative) instructions.

- Uses `Texture2DGradientTestCase` with useDerivatives=true
- 5 derivative pairs:
  - {(0,0,0,0), (0,0,0,0)}
  - {(1,1,1,0), (1,1,1,0)}
  - {(0,0,0,0), (1,1,1,0)}
  - {(1,1,1,0), (0,0,0,0)}
  - {(2,2,2,0), (2,2,2,0)}
- Uses R8G8B8A8_UNORM format, 16x16 texture size, CLAMP_TO_EDGE wrapping
- 8 filter combinations (2 mag x 2 min x 2 mipmap) x graphics and compute pipelines

#### 2d.sizes

[Lines 1290-1396](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1290-L1396). Tests 2D texture filtering with explicit LOD across 9 sizes.

- 9 sizes: {2,2}, {2,3}, {3,7}, {4,8}, {31,55}, {32,32}, {32,64}, {57,35}, {128,128}
- Uses R8G8B8A8_UNORM format
- 7 LOD values: {-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0}
- 16 filter/wrap combinations per size: 2 mag filters x 2 min filters x 2 mipmap modes x 2 wrap modes
- Graphics and compute pipeline variants

## Parameter Dimensions

| Family | Formats | Sizes | Filter Combos | LOD Values | Derivative Pairs | Pipeline |
|--------|---------|-------|---------------|------------|------------------|----------|
| 2d.formats | 19 | - | nearest, linear | 7 | - | graphics, compute |
| 2d.derivatives | - | 16x16 | 8 (2x2x2) | - | 5 | graphics, compute |
| 2d.sizes | - | 9 | 16 (2x2x2x2) | 7 | - | graphics, compute |

## Support/Feature Requirements

- [TextureFilteringTestCase::checkSupport](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L916-L919) calls `util::checkTextureSupport` (no-op template specialization)
- Actual format support check and `NotSupportedError` throw occur in `isSupported()` (line 887) and `runTest()` (line 577)
- **VulkanSC**: On VulkanSC, the main process skips verification entirely and returns pass (line 600-604); verification only runs in subprocess mode

## Verification Methods

Per-sample mathematical verification via [SampleVerifier](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L615-L685):

1. Precision from device limits: coordBits = subTexelPrecisionBits, mipmapBits = mipmapPrecisionBits
2. Strict verification: SampleVerifier with strict precision verifies each sample
3. Relaxed fallback: if strict fails and allowRelaxedPrecision (half-float or SNORM8 with linear), use relaxed precision (delta=-6 for HALF_FLOAT, delta=-2 for SNORM_INT8)
4. Result: any failure -> fail, warnings only -> quality warning, all pass -> pass

## Notes

- Uses ShaderExecutor to run GLSL texture lookup instructions directly (textureLod or textureGrad)
- Per-sample verification against mathematically computed acceptable range
- Device-aware precision using actual device limits
- Dual pipeline support (graphics + compute) for all test families
