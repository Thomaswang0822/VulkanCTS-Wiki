# vktTextureSwizzleTests.cpp

## Overview

Tests for texture component swizzle (VkComponentMapping) and texture coordinate swizzling, verifying that channel remapping at image view creation and shader-side coordinate manipulation produce correct results.

## Role

Implementation file

## Source Code

- [vktTextureSwizzleTests.cpp](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp)

## Registration Hierarchy

```text
texture.swizzle
├── component_mapping
└── texture_coordinate
```

The `component_mapping` child contains `color`, `depth`, and `stencil` sub-groups; `depth` and `stencil` are non-VulkanSC only and are described below rather than expanded in the parseable one-level hierarchy tree.

## Test Families

### component_mapping

TestCaseGroup at [line 511](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L511). Contains 3 sub-groups: color, depth, stencil.

#### component_mapping.color

[Lines 518-546](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L518-L546). Tests VkComponentMapping swizzle on 2D color textures.

- 119 color formats (81 uncompressed + 38 compressed: 6 ETC2, 4 EAC, 28 ASTC 2D)
- 2 sizes: pot (128x64), npot (51x65)
- 9 component mappings: zzzz, oooo, rrrr, gggg, bbbb, aaaa, rgba, iiii, abgr
- 2 backing modes: regular, sparse (non-VulkanSC)
- Compute shader variants for each test

#### component_mapping.depth

[Lines 551-578](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L551-L578). Non-VulkanSC only. Tests VkComponentMapping swizzle on 2D depth textures.

- 6 depth formats: D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT
- 2 sizes: pot (128x64), npot (51x65)
- Only uses "oooo" (all ONE) component mapping
- 2 backing modes: regular, sparse (non-VulkanSC)
- Compute shader variants for each test
- Requires VK_KHR_maintenance5 + depthStencilSwizzleOneSupport

#### component_mapping.stencil

[Lines 582-609](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L582-L609). Non-VulkanSC only. Tests VkComponentMapping swizzle on 2D stencil textures.

- 4 stencil formats: S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT
- 2 sizes: pot (128x64), npot (51x65)
- Only uses "oooo" (all ONE) component mapping
- 2 backing modes: regular, sparse (non-VulkanSC)
- Compute shader variants for each test
- Requires VK_KHR_maintenance5 + depthStencilSwizzleOneSupport

### texture_coordinate

TestCaseGroup at [line 515](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L515). Tests texture coordinate swizzling in shaders.

- 3 coordinate swizzles: yx (swap s/t), xx (s for both), yy (t for both)
- Same 119 color formats as component_mapping.color
- 2 sizes: pot, npot
- 2 backing modes: regular, sparse (non-VulkanSC)
- Compute shader variants

## Parameter Dimensions

| Family | Formats | Sizes | Mappings/Swizzles | Backing Modes | Pipeline |
|--------|---------|-------|-------------------|---------------|----------|
| component_mapping.color | 119 | pot, npot | 9 component mappings | regular, sparse | graphics, compute |
| component_mapping.depth | 6 | pot, npot | oooo | regular, sparse | graphics, compute |
| component_mapping.stencil | 4 | pot, npot | oooo | regular, sparse | graphics, compute |
| texture_coordinate | 119 | pot, npot | 3 coordinate swizzles | regular, sparse | graphics, compute |

## Support/Feature Requirements

- [SwizzleTestCase::checkSupport()](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L75-L91): calls `checkTextureSupport`, plus for depth/stencil requires `VK_KHR_maintenance5` and `depthStencilSwizzleOneSupport`
- Sparse backing mode requires sparse binding support (non-VulkanSC only)

## Verification Methods

[Swizzle2DTestInstance::iterate()](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L147-L307):

1. Render textured quad with specified component mapping via GPU
2. Compute software reference using `tcu::Texture2DView::sample()`
3. Apply component mapping swizzle to reference manually
4. Compare using `tcu::compareImages()` with threshold: `pixelFormat.getColorThreshold() + RGBA(2,2,2,2)`

## Notes

- Verifies VkComponentMapping at image view creation correctly remaps texture channels
- GPU result compared against software reference with same remapping applied
- Also tests shader-side coordinate manipulation via texture_coordinate family
- Depth and stencil swizzle tests are limited to the "oooo" (all ONE) mapping due to VK_KHR_maintenance5 depthStencilSwizzleOneSupport semantics
