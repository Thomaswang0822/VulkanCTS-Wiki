# Shader Derivate Function Tests

## Overview

Tests for GLSL derivative functions (`dFdx`, `dFdy`, `fwidth` and their coarse/fine/subgroup variants) in fragment shaders. Verifies that implementations compute correct derivatives for constant, linearly interpolated, and texture-sampled values across a range of precisions, surface types, and control flow contexts.

## Role

Both registration and implementation. The `ShaderDerivateTests` class (derived from `tcu::TestCaseGroup`) serves as the test group registrar and populates all child test cases in its `init()` method. Test case classes (`ConstantDerivateCase`, `LinearDerivateCase`, `TextureDerivateCase`) extend `TriangleDerivateCase` which extends `ShaderRenderCase`.

## Source Code

[../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1-L2179)

## Registration Hierarchy

```text
glsl.derivate
├── dfdx
├── dfdxfine
├── dfdxcoarse
├── dfdxsubgroup (VK_KHR_shader_subgroup_uniform_control_flow)
├── dfdy
├── dfdyfine
├── dfdycoarse
├── dfdysubgroup (VK_KHR_shader_subgroup_uniform_control_flow)
├── fwidth
├── fwidthfine
└── fwidthcoarse
```

## Test Families

- **ConstantDerivateCase** - Verifies that the derivative of a constant argument is zero. Iterates over vector sizes (float, vec2, vec3, vec4). Not applicable to subgroup derivative functions.
- **LinearDerivateCase** - Verifies derivatives of linearly interpolated values. Covers multiple source contexts (basic linear, in_function, static_if, static_loop, static_switch, uniform_if, uniform_loop, uniform_switch, dynamic_if, dynamic_loop, dynamic_switch, output_store, private_store, linear_vec8). Each case is parameterized by data type and precision.
- **TextureDerivateCase** - Verifies derivatives of texture lookup results. Parameterized by surface type (basic/msaa4/float), data type, and precision.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| DerivateFunc | dfdx, dfdxfine, dfdxcoarse, dfdxsubgroup, dfdy, dfdyfine, dfdycoarse, dfdysubgroup, fwidth, fwidthfine, fwidthcoarse | The GLSL derivative function under test |
| DataType | float, vec2, vec3, vec4 | Input/output vector type |
| Precision | mediump, highp (lowp skipped for UNORM surfaces) | GLSL precision qualifier |
| SurfaceType | UNORM_FBO, FLOAT_FBO | Render target format (UNORM8 or RGBA32UI for float) |
| numSamples | 0, 2, 4 | MSAA sample count for FBO configurations |
| Source context | linear, in_function, static_if, static_loop, static_switch, uniform_if, uniform_loop, uniform_switch, dynamic_if, dynamic_loop, dynamic_switch, output_store, private_store, linear_vec8 | Control flow context in which the derivative is computed |

## Support/Feature Requirements

- **Subgroup derivative functions** (dfdxsubgroup, dfdysubgroup): Require `VK_SUBGROUP_FEATURE_QUAD_BIT`, `VK_SUBGROUP_FEATURE_BALLOT_BIT`, subgroup size >= 4, and quad operations supported for fragment stage. These are associated with `VK_KHR_shader_subgroup_uniform_control_flow`.
- **Non-uniform control flow cases** (dynamic_if, dynamic_loop, dynamic_switch): Require the same subgroup features as subgroup derivative functions.
- **Demote cases** (output_store, private_store): Require `VK_EXT_shader_demote_to_helper_invocation`.
- **Long vector case** (linear_vec8): Requires `VK_EXT_shader_long_vector` (not available in Vulkan SC builds).

## Verification Methods

- **Interval-based comparison**: Uses `tcu::Interval` arithmetic to compute analytically expected derivative ranges. The rendered pixel values (encoded as `derivative * scale + bias`) are decoded and compared against the computed interval bounds.
- **ConstantDerivateCase**: Verifies that all derivative components are exactly zero.
- **LinearDerivateCase**: Computes expected derivative analytically from the known linear interpolation and viewport dimensions, then checks that rendered values fall within the interval bounds with appropriate floating-point error margins.
- **TextureDerivateCase**: Samples the reference texture at nearby pixels to estimate expected derivatives and compares against rendered results.

## Notes

- Viewport size is 99x133 pixels (non-square to ensure different x/y derivative magnitudes).
- For UNORM FBO surfaces, derivatives are encoded using scale/bias to map into the [0,1] renderable range. For FLOAT_FBO (RGBA32UI), derivatives are written directly.
- Lowp precision cases are skipped for UNORM surfaces because lowp does not produce enough bits when rendered to U8 render targets.
- The `output_store` and `private_store` cases test that derivatives are correctly computed even when the value has been stored to an output variable or global variable before being used in a derivative call, with demotion used to exercise helper invocation behavior.
