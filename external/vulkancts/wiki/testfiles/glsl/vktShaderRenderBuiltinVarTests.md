# Shader Builtin Variable Tests

## Overview

Tests for GLSL built-in shader variables including `gl_FragCoord` (xyz and w components), `gl_PointCoord`, `gl_FrontFacing`, and `gl_FragDepth`. Also includes MSAA-specific `gl_FragCoord` tests that verify per-sample coordinate correctness, and input variation tests that exercise different shader input types (builtin, varying, constant). Tests cover various primitive topologies, cull modes, depth formats, and sample counts.

## Role

Both registration and implementation. The `createBuiltinVarTests` function ([L2499-L2691](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2691)) creates the `builtin_var` test group and populates it with six direct sub-groups, each containing test cases implemented by dedicated test case classes.

## Source Code

[vktShaderRenderBuiltinVarTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1-L2694)

## Registration Hierarchy

```text
glsl.builtin_var
├── frontfacing
├── fragdepth
├── fragcoord_msaa
├── fragcoord_msaa_input
├── simple
└── input_variations
```

## Test Families

- **BuiltinGlFragCoordXYZCase** ([L1899-L1949](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1899-L1949)): Tests that `gl_FragCoord.xyz` correctly reflects the fragment's window-space position. Registered as `fragcoord_xyz` under the `simple` group.
- **BuiltinGlFragCoordWCase** ([L2015-L2065](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2015-L2065)): Tests that `gl_FragCoord.w` correctly reflects the 1/w interpolation. Registered as `fragcoord_w` under the `simple` group.
- **BuiltinGlPointCoordCase** ([L2187-L2301](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2187-L2301)): Tests `gl_PointCoord` with point primitives. Includes variants for default, uniform-in-fragment, and uniform-in-vertex configurations. Registered as `pointcoord`, `pointcoord_uniform_frag`, and `pointcoord_uniform_vert` under the `simple` group.
- **BuiltinGlFrontFacingCase** ([L285-L384](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L285-L384)): Tests `gl_FrontFacing` with various primitive topologies and cull modes. Uses `FrontFacingVertexShader` and `FrontFacingFragmentShader` for reference rendering.
- **BuiltinFragDepthCase** ([L1696-L1835](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1696-L1835)): Tests `gl_FragDepth` output with various depth formats, primitive topologies, large depth ranges, depth clamp, and multisample configurations.
- **BuiltinFragCoordMsaaTestCase** ([L1533-L1695](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1533-L1695)): Tests `gl_FragCoord` correctness under MSAA rendering with various sample counts, sample shading, and centroid interpolation.
- **BuiltinInputVariationsCase** ([L2410-L2495](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2410-L2495)): Tests different shader input type combinations (builtin, varying, constant bits).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Built-in variable | FragCoord.xyz, FragCoord.w, PointCoord, FrontFacing, FragDepth | The GLSL built-in variable under test |
| Primitive topology | `point_list`, `line_list`, `triangle_list`, `triangle_strip`, `triangle_fan` | Primitive topology used for rendering ([L2574-L2585](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2574-L2585)) |
| Cull mode | `none`, `front`, `back`, `front_and_back` | Face culling mode for FrontFacing tests ([L2587-L2596](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2587-L2596)) |
| Depth format | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | Depth buffer format for FragDepth tests ([L2640-L2663](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2640-L2663)) |
| Sample count | 1, 2, 4, 8, 16, 32, 64 | MSAA sample count for FragCoord MSAA tests ([L2524-L2532](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2524-L2532)) |
| Large depth enable | true, false | Whether to use large depth range for FragDepth tests |
| Depth clamp enable | true, false | Whether to enable depth clamp for FragDepth tests |
| Sample shading | enabled, disabled | Whether sample shading is enabled for MSAA tests |
| Centroid interpolation | enabled, disabled | Whether centroid interpolation decoration is used |
| UBO load variant | false, true | Whether gl_FrontFacing value is loaded through UBO for additional verification ([L2598-L2622](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2598-L2622)) |
| Shader input type bits | BUILTIN_BIT, VARYING_BIT, CONSTANT_BIT | Combinations of shader input types for input variation tests ([L2682-L2687](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687)) |

## Support/Feature Requirements

- **Sample count support**: Depends on the device's `sampleCounts` property. Each sample count test checks whether the device supports the requested count before proceeding.
- **Depth format support**: Depends on the device's format properties for the specific depth format being tested.
- **Depth clamp**: Requires the `depthClamp` device feature to be enabled for tests with `depthClampEnable = true`.
- **MSAA tests**: Require the `sampleRateShading` device feature for tests with sample shading enabled.
- **Large depth range**: Requires `D32_SFLOAT` format support with sufficient precision.

## Verification Methods

- **FragCoord.xyz/w**: Pixel threshold comparison against analytically computed reference images where the expected color encodes the fragment's window-space position.
- **PointCoord**: Image comparison against reference rendering that encodes the point coordinate as color output.
- **FrontFacing**: Reference rendering using `FrontFacingVertexShader` and `FrontFacingFragmentShader` ([L69-L100](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L69-L100)) that encode the facing value as color (white for front-facing, black for back-facing). The UBO load variant additionally verifies the value through a uniform buffer round-trip.
- **FragDepth**: Depth buffer value comparison after rendering. The shader writes a computed depth value via `gl_FragDepth`, and the resulting depth buffer is compared against the expected depth values.
- **FragCoord MSAA**: Per-sample coordinate correctness verification. Each sample's `gl_FragCoord` value is verified against the expected sample position within the pixel.
- **Input variations**: `ShaderRenderCase`-based reference comparison verifying correct rendering with different input type combinations.

## Notes

- The `frontfacing` group is organized as `none`/`add_ubo_load` -> primitive topology -> cull mode (for UBO load variant) or `simple` (for non-UBO variant) ([L2598-L2622](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2598-L2622)).
- The `fragdepth` group generates test cases from the cross-product of primitive topologies and depth format/largeDepth/depthClamp/sample configurations ([L2665-L2673](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2665-L2673)).
- The `fragcoord_msaa` group tests with sample shading enabled, while `fragcoord_msaa_input` tests both with and without sample shading, plus centroid interpolation variants ([L2537-L2566](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2537-L2566)).
- The `input_variations` group iterates over all combinations of `SHADER_INPUT_BUILTIN_BIT`, `SHADER_INPUT_VARYING_BIT`, and `SHADER_INPUT_CONSTANT_BIT` flags ([L2682-L2687](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687)).
