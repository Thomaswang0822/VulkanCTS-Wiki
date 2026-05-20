# Texture Gather Tests

## Overview

Tests for GLSL `textureGather()`, `textureGatherOffset()`, and `textureGatherOffsets()` functions. These functions return a four-component vector containing one component from each of the four texels that would be used in a bilinear filtering operation. Tests cover multiple texture types (2D, 2D array, cube), formats (RGBA8 unorm, RGBA8 uint, RGBA8 int, depth32f), gather types (basic, offset, offsets), and offset sizes (minimum required, implementation maximum).

## Role

Both registration and implementation. The `TextureGatherTests` class (a `tcu::TestCaseGroup` named `"texture_gather"`) registers all sub-groups and test cases in its `init()` method ([L2821-L3135](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2821-L3135)). The `TextureGather2DCase`, `TextureGather2DArrayCase`, and `TextureGatherCubeCase` classes provide the full test implementation.

## Source Code

[vktShaderRenderTextureGatherTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1-L3145)

## Registration Hierarchy

```text
glsl.texture_gather
├── graphics
└── compute
```

## Test Families

- **TextureGather2DCase** ([L2772-L2775](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2772-L2775)): Tests `textureGather*` on 2D textures. Parameterized by gather type, offset size, format, compare mode, wrap mode, texture swizzle, filter mode, level mode, and base level.
- **TextureGather2DArrayCase** ([L2777-L2780](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2777-L2780)): Tests `textureGather*` on 2D array textures. Same parameterization as 2D case with additional layer dimension.
- **TextureGatherCubeCase** ([L2782-L2787](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2782-L2787)): Tests `textureGather()` on cube map textures. Restricted to basic gather type with no offset (per GLSL specification constraints).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pipeline | `graphics`, `compute` | Whether the gather operation runs in a graphics or compute pipeline ([L2852-L2856](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2852-L2856)) |
| GatherType | `basic`, `offset`, `offsets` | Which textureGather variant: `textureGather`, `textureGatherOffset`, or `textureGatherOffsets` |
| OffsetSize | `none`, `min_required_offset`, `implementation_maximum` | Offset range: none for basic, spec minimum (-8..7) or implementation maximum for offset variants ([L72-L78](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L72-L78)) |
| TextureType | `2d`, `2d_array`, `cube` | Texture dimensionality ([L2823-L2827](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2823-L2827)) |
| Format | `rgba8`, `rgba8ui`, `rgba8i`, `depth32f` | Texel format ([L2829-L2836](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2829-L2836)) |
| Texture size | `size_pot` (64x64), `size_npot` (17x23) | Power-of-two and non-power-of-two texture dimensions ([L2838-L2842](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2838-L2842)) |
| Compare mode | `none`, `less`, `greater` | Shadow comparison mode for depth formats |
| Wrap mode | `clamp_to_edge`, `repeat`, `mirrored_repeat` | Texture coordinate wrap modes ([L2844-L2850](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2844-L2850)) |
| Texture swizzle | Various component swizzle variants | Texture swizzle configuration sub-group |
| Filter mode | Nearest/Linear min/mag combinations | Texture filter mode sub-group |
| Base level | Various base level values | Base level sub-group |
| No corners | `no_corners` variant | For cube maps: avoids sampling near cube map seams |

## Support/Feature Requirements

- **Compute pipeline**: Compute tests require compute pipeline support.
- **Sparse texture support**: Sparse variants (when enabled) require `sparseResidency*` features and are excluded on VulkanSC platforms.
- **Implementation maximum offset range**: The `implementation_offset` sub-group queries `maxSamplerOffset` from device properties to determine the implementation's maximum supported offset range ([L72-L78](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L72-L78)).
- **Depth format**: Shadow comparison modes require depth format support in device format properties.
- **Cube map gather**: Only `GATHERTYPE_BASIC` is valid for cube map textures; offset variants are skipped ([L2885-L2886](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2885-L2886)).

## Verification Methods

All tests use `ShaderRenderCase`-based reference comparison. Reference values are computed using `tcu::TextureAccess::gather` which implements the Vulkan texture gather specification:

- **Basic gather**: `textureGather(sampler, coord)` returns one component from each of the four texels that contribute to bilinear filtering.
- **Gather with offset**: `textureGatherOffset(sampler, coord, offset)` applies a constant texel offset before gathering.
- **Gather with offsets**: `textureGatherOffsets(sampler, coord, offsets)` applies four independent texel offsets, one per gathered texel.

The rendered output is compared against the reference image using the `ShaderRenderCase` framework's built-in threshold comparison with format-appropriate tolerances. For depth comparison modes, `tcu::TexCompareVerifier` is used.

## Notes

- The hierarchy under each pipeline group is deep: `graphics`/`compute` -> gatherType (`basic`/`offset`/`offsets`) -> offsetSize -> textureType -> format -> (no_corners) -> textureSize -> compareMode -> wrapMode.
- The `GATHERTYPE_BASIC` variant does not create a separate offset size group; it is placed directly under the gather type group ([L2867-L2879](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2867-L2879)).
- The `makeTextureGatherCase` factory function ([L2761-L2793](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2761-L2793)) dispatches to the appropriate test case class based on `TextureType`.
- Spec minimum offset range is -8 to 7; implementation maximum range is typically -32 to 31 but is queried from device properties.
