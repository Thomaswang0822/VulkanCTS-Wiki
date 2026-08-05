## Overview

[`vktShaderRenderTextureGatherTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1) implements `glsl.texture_gather`, the GLSL texture-gather test group. The factory registers graphics and compute variants, generates GLSL for the selected gather operation and sampler configuration, executes a quad render or compute dispatch, and compares the result with a texture-backed CPU reference.

The group covers ordinary and offset gather calls over 2D, 2D-array, and cube textures; normalized, signed/unsigned integer, and depth formats; comparison sampling; sampler wrap modes; and selected texture-view and LOD behavior. It is a generated matrix, not a fixed list of hand-written cases.

## Source Code

- Implementation and factory: [`vktShaderRenderTextureGatherTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1)
- Public declaration: [`vktShaderRenderTextureGatherTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.hpp#L1)
- GLSL-package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1270-L1271)
- Shared shader-render framework: [`vktShaderRender.hpp`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L85-L140)

## Registration Hierarchy

```text
glsl.texture_gather
├── graphics
└── compute
```

`TextureGatherTests::init()` creates the two pipeline roots, then adds gather-operation groups beneath each root ([registration loop](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2852-L2879)). The direct operation names are `basic`, `offset`, `offset_dynamic`, and `offsets` ([name mapping](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L818-L858)). `basic` has no offset-range subgroup; the other operations are split into `min_required_offset` and `implementation_offset`.

## Test Families

### Pipeline variants

`graphics` generates a shared vertex shader and one fragment shader per gather iteration, then renders a two-triangle quad ([program generation and execution](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2084-L2099), [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1465-L1497)). `compute` instead generates per-iteration compute shaders and supplies the quad coordinates through a uniform buffer ([compute program generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2101-L2115), [`setupUniforms()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1542-L1560)).

Both roots use the same principal gather, texture, format, size, comparison, wrap, filter, and base-level matrix where the registration conditions allow it. Texture-swizzle cases are graphics-only ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2975-L3013)).

### Gather operations and offsets

- `basic` exercises `textureGather` without an explicit offset.
- `offset` uses the single compile-time offset form.
- `offset_dynamic` selects an offset dynamically.
- `offsets` supplies four independent gather offsets.

The minimum-required range is `[-8, 7]`. Implementation-offset cases derive their range from the device's `minTexelGatherOffset` and `maxTexelGatherOffset`; `offsets.implementation_offset` additionally needs the `[-32, 31]` range used by its compile-time offset vectors ([limits and offset construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L71-L79), [`offset checks`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1044-L1056)).

Cube textures are generated only for `basic`; all non-basic gather forms skip cube textures ([factory constraints](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2881-L2890)). Cube cases include normal sampling and a `no_corners` variant to avoid cube-corner samples ([cube registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2898-L2907)).

### Texture and sampler matrix

The generated matrix includes:

| Dimension | Values / behavior |
|---|---|
| Texture type | `2d`, `2d_array`, and, for `basic`, `cube` |
| Format | `rgba8`, `rgba8ui`, `rgba8i`, and `depth32f` ([format table](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2829-L2836)) |
| Size | `size_pot` (`64 × 64 × 3`) and `size_npot` (`17 × 23 × 3`) ([size table](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2838-L2842)) |
| Depth comparison | `compare_less` and `compare_greater` for `depth32f`; non-depth formats do not use a comparison subgroup |
| Wrap pairs | Consecutive pairs made from `clamp_to_edge`, `repeat`, and `mirrored_repeat` ([wrap loop](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2844-L2850)) |
| Gather component | Non-depth cases include explicit components `0`–`3` and the implicit component form; depth has one component case |
| Array layers | Layer `0` receives all basic iterations; selected iterations cover `-1`, `1`, `2`, and `3` ([array generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2302-L2339)) |
| Cube faces | The first face receives all basic iterations; selected iterations cover the remaining faces ([cube generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2528-L2565)) |

Selected combinations also add `texture_swizzle`, `filter_mode`, and `base_level` groups. Swizzle is non-depth and graphics-only. Filter mode combines minification and magnification filter choices, omitting redundant nearest combinations and restricting integer formats to the nearest-only combination ([filter registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3015-L3074)). `base_level` tests levels 1 and 2; non-Vulkan-SC builds additionally register AMD gather-bias and gather-LOD variants for non-depth formats ([base-level registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3077-L3127)).

Regular, swizzle, filter, and base-level paths also create sparse-image variants outside Vulkan SC builds ([sparse guards](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2957-L2965), [`additional groups`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3004-L3011)). The generator intentionally trims the matrix: most extra groups are omitted for `min_required_offset` except `offsets` ([condition](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2971-L2974)).

## Support / Feature Requirements

| Requirement | Scope |
|---|---|
| `shaderImageGatherExtended` | Required by all concrete 2D, 2D-array, and cube cases ([support checks](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2275-L2287), [`array`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2501-L2513), [`cube`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2735-L2739)). |
| Extended gather syntax | Dynamic, multi-offset, and implementation-offset variants request `GL_EXT_gpu_shader5`; initialization checks the corresponding core feature ([helper](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L860-L865), [`runtime check`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1288-L1294)). |
| Gather offset limits | Implementation-range cases require at least the mandated range; multi-offset implementation cases require the wider `[-32, 31]` range. |
| Mutable comparison samplers | Depth-compare cases require `mutableComparisonSamplers` when `VK_KHR_portability_subset` is present, outside Vulkan SC builds ([check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1145-L1162)). |
| `VK_AMD_texture_gather_bias_lod` | Needed only by AMD bias/LOD leaves; the implementation also checks format-specific `supportsTextureGatherLODBiasAMD` properties ([initialization](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1296-L1361)). |
| Sparse images | Sparse leaves are not registered for Vulkan SC (`#ifndef CTS_USES_VULKANSC`). |

## Verification Methods

Every iteration produces an image, then invokes the concrete instance verifier; a failed reference comparison reports `Result verification failed` ([iteration path](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1459-L1513)). The verifier reconstructs active gather offsets from the operation type ([offset helper](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L889-L909)).

- Depth gathers use `verifyGatherOffsetsCompare()` with sampler comparison state and seamless cube-map behavior ([depth path](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1581-L1604)).
- UNORM gathers use `verifyGatherOffsets<float>()` with fixed-point color thresholds ([UNORM path](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1608-L1618)).
- Signed and unsigned integer gathers use `verifyGatherOffsets<int32_t>()` and `verifyGatherOffsets<uint32_t>()` with zero color threshold ([integer paths](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1620-L1634)).

The texture data is randomized into color tiles and swizzled when requested. Each concrete verifier builds the matching 2D, 2D-array, or cube texture view before evaluating the reference ([2D](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2207-L2213), [`array`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2433-L2439), [`cube`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2666-L2672)).

## Test Principles

- Coverage is defined by nested registration loops over pipeline, gather form, offset range, texture shape, format, sampler state, and selected texture-view behavior ([`init()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2821-L3135)).
- Shader generation and reference evaluation are deliberately separate: generated GLSL performs the gather, while host-side verification replays sampling from the configured texture view, coordinates, component, offsets, and sampler state.
- The group avoids a full Cartesian product where it would duplicate coverage: offset forms omit cubes, compute omits swizzle, and nonzero array layers and later cube faces use selected iterations rather than every component/offset iteration.
- Registration-time Vulkan-SC guards, per-case feature checks, and initialization-time limit/extension checks are distinct layers. A missing feature produces a not-supported result; it is not evidence that the test family was not registered.

## Notes

- This page describes source-defined registration and verification behavior. It does not claim that these cases were run on the current host.
- Sparse-image support checks are supplied by the shared shader-render infrastructure; this file's visible responsibility is sparse-case registration and parameterization.
