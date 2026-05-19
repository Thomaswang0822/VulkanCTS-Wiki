# Texture Function Tests

## Overview

Comprehensive tests for GLSL texture access and query functions, covering `texture()`, `textureProj()`, `textureLod()`, `textureProjLod()`, `textureGrad()`, `textureProjGrad()`, `texelFetch()`, and their offset/clamp variants, as well as texture query functions (`textureSize`, `textureQueryLod`, `textureQueryLevels`, `textureSamples`). Tests span multiple texture types (1D, 2D, 3D, cube, 2D array, 1D array, cube array), formats (fixed-point, float, int, uint, shadow), sampler configurations, and shader stages (vertex, fragment, compute).

## Role

Both registration and implementation. The `ShaderTextureFunctionTests` class (a `tcu::TestCaseGroup` named `"texture_functions"`) registers all sub-groups and test cases in its `init()` method ([L5009-L8298](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5009-L8298)). The `ShaderTextureFunctionCase` and `SparseShaderTextureFunctionCase` classes provide the full test implementation, and `TextureQueryCase` handles query function tests.

## Source Code

[vktShaderRenderTextureFunctionTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1-L8308)

## Registration Hierarchy

```text
glsl.texture_functions
├── texture
├── textureclamp
├── textureoffset
├── textureoffset_pcoffset
├── textureoffsetclamp
├── textureoffsetclamp_pcoffset
├── textureproj
├── textureprojoffset
├── textureprojoffset_pcoffset
├── textureprojlod
├── textureprojlodoffset
├── textureprojlodoffset_pcoffset
├── texturelod
├── texturelodoffset
├── texturelodoffset_pcoffset
├── texturegrad
├── texturegradclamp
├── texturegradoffset
├── texturegradoffset_pcoffset
├── texturegradoffsetclamp
├── texturegradoffsetclamp_pcoffset
├── textureprojgrad
├── textureprojgradoffset
├── textureprojgradoffset_pcoffset
├── texelfetch
├── texelfetchoffset
├── texelfetchoffset_pcoffset
└── query
```

## Test Families

- **ShaderTextureFunctionCase** ([L1966-L2045](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1966-L2045)): Extends `ShaderRenderCase`. Parameterized by `TextureLookupSpec`, `TextureSpec`, evaluation function, and shader stage flags. Creates `ShaderTextureFunctionInstance` for rendering and comparison.
- **SparseShaderTextureFunctionCase** ([L2047-L2100](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2047-L2100)): Variant that uses sparse image backing mode for testing texture functions with sparse residency.
- **TextureQueryCase** ([L8100-L8290](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8100-L8290)): Tests texture query functions (`textureSize`, `textureQueryLod`, `textureQueryLevels`, `textureSamples`) with various LOD clamp modes.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Texture function | `texture`, `textureProj`, `textureLod`, `textureProjLod`, `textureGrad`, `textureProjGrad`, `texelFetch` | The GLSL texture function being tested ([L57-L74](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L57-L74)) |
| Texture type | 1D, 2D, 3D, Cube, 2DArray, 1DArray, CubeArray | Dimensionality and array-ness of the sampled texture |
| Format | Fixed (RGBA8), Float (RGBA16F), Int (RGBA8I), Uint (RGBA8UI), Shadow (DEPTH_COMPONENT16) | Texel data format and signedness |
| Sampler | Nearest, Linear, NearestMipmap, LinearMipmap, TriLinear, Shadow | Min/mag filter and mipmap modes ([L5024-L5057](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5024-L5057)) |
| Bias/LOD range | Various min/max LOD values | LOD bias and clamp ranges for bias and Lod variants |
| Gradient ranges | Various dPdx/dPdy min/max | Gradient vector ranges for Grad variants |
| Offset values | IVec3 offsets (e.g., -8, 7, 3) | Texel offsets for Offset variants |
| Wrap mode | ClampToEdge, ClampToBorder, Repeat, MirroredRepeat, MirroredOnce | Texture wrap modes applied per offset group ([L5016-L5022](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5016-L5022)) |
| Shader stage | Vertex, Fragment, Compute | Which shader stage performs the texture operation |
| pcOffset flag | false, true | Whether to use push constant offset (splits offset groups into `_pcoffset` variants) |
| LOD clamp flag | false, true | Whether LOD clamping is applied (Clamp variants) |
| ImageBackingMode | Regular, Sparse | Whether the texture uses standard or sparse memory backing |

## Support/Feature Requirements

- **Sparse texture cases**: Require `sparseResidency*` features and are excluded on VulkanSC platforms.
- **Compute shader cases**: Require compute pipeline support; test cases with `COMPUTE` flag generate compute shader variants.
- **Shadow comparison modes**: Require depth format support in the device's format properties.
- **1D texture cases**: Require `shaderSampledImageArrayDynamicIndexing` or 1D texture support as appropriate.
- **Cube array texture cases**: Require `imageCubeArray` feature.

## Verification Methods

All tests use `ShaderRenderCase`-based reference comparison. Each test case provides a texture evaluation function (`TexEvalFunc`) that computes the expected texel value for a given coordinate:

- **Standard texture functions**: Evaluation functions (e.g., `evalTexture2D`, `evalTextureCube`, `evalTexture3D`) compute reference values via `tcu::TextureAccess` sampling, which implements the Vulkan texture sampling specification including filtering, wrapping, and LOD computation.
- **Offset variants**: Evaluation functions (e.g., `evalTexture2DOffset`, `evalTexture3DOffset`) apply the specified texel offset before sampling.
- **Bias variants**: Evaluation functions (e.g., `evalTexture2DBias`, `evalTexture2DOffsetBias`) add the bias value to the computed LOD before sampling.
- **LOD variants**: Evaluation functions (e.g., `evalTexture2DLod`, `evalTexture2DShadowLod`) use the explicitly provided LOD value.
- **Grad variants**: Evaluation functions (e.g., `evalTexture2DGrad`, `evalTexture2DGradOffset`) use the explicitly provided gradient vectors.
- **Projection variants**: Evaluation functions divide coordinates by the w component before sampling.
- **Query functions**: Results are verified against known texture dimensions and mipmap counts.

The rendered output is compared against the reference image using the `ShaderRenderCase` framework's built-in threshold comparison with format-appropriate tolerances.

## Notes

- The `createCaseGroup` helper ([L4960-L5007](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4960-L5007)) generates vertex, fragment, and/or compute test cases from a `TexFuncCaseSpec` array based on the `CaseFlags` (VERTEX/FRAGMENT/COMPUTE).
- Offset variants are further subdivided by wrap mode (clamp_to_edge, clamp_to_border, repeat, mirrored_repeat, mirrored) and pcOffset flag, creating a deep hierarchy under each offset group name.
- The `FUNCTION_TEXTUREPROJ2` and `FUNCTION_TEXTUREPROJ3` enumerators handle the different coordinate signatures of `textureProj` for 1D and 2D samplers respectively ([L60-L63](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L60-L63)).
- Texture query tests are organized under the `query` sub-group with separate groups for each query function and LOD clamp mode.
