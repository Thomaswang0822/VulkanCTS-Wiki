# Shader Limit Tests

## Overview

Tests that verify correct shader behavior when using near-maximum numbers of fragment input components. Exercises the device's reported `maxFragmentInputComponents` and `maxVertexOutputComponents` limits by declaring varying variables that approach these limits and verifying that the data is correctly passed from the vertex shader to the fragment shader.

## Role

Both registration and implementation. The `createLimitTests` function creates the test group hierarchy. `FragmentInputComponentCase` (derived from `TestCase`) handles program generation and support checking, while `FragmentInputComponentCaseInstance` (derived from `ShaderRenderCaseInstance`) handles rendering and verification.

## Source Code

[../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L1-L265)

## Registration Hierarchy

```text
glsl.limits
└── near_max
```

## Test Families

- **FragmentInputComponentCase** - Tests near-maximum fragment input component counts. The vertex shader declares output varyings that fill the specified number of components, and the fragment shader verifies that each varying received the expected value. Each varying is assigned its location index as a float value (e.g., `o_color0 = vec4(0.0)`, `o_color1 = vec4(1.0)`).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Component counts | 59, 60, 61, 62, 63 (for 64 limit), 123, 124, 125, 126, 127 (for 128 limit), 251, 252, 253, 254, 255 (for 256 limit) | Number of fragment input components, near the three standard spec minimum limits |

### Component Count Details

The test generates cases for three standard minimum limit thresholds (64, 128, 256 components). For each threshold, five test cases are created at `threshold - 5` through `threshold - 1`:
- **64-component limit**: components_59 through components_63
- **128-component limit**: components_123 through components_127
- **256-component limit**: components_251 through components_255

Note that `gl_Position` always consumes 4 components of the vertex output, so the actual user-declared output components are `inputComponents - 4` for the vertex shader.

## Support/Feature Requirements

- The device must support the tested component count. The `createInstance()` method checks both `maxFragmentInputComponents` and `maxVertexOutputComponents` against the requested count, throwing `NotSupportedError` if the device does not support the required number of components.
- Since `gl_Position` counts as 4 vertex output components, the vertex output component requirement is `inputComponents + 4`.

## Verification Methods

- **Pixel threshold comparison**: Renders a full-screen quad and compares the result against a solid green reference image using `tcu::pixelThresholdCompare` with a threshold of `tcu::RGBA(2, 2, 2, 2)`. The fragment shader verifies each varying value against its expected value (the location index), incrementing an error counter for mismatches. If no errors are found, the fragment outputs green (0, 1, 0, 1); otherwise it outputs red (1, 0, 0, 1).

## Notes

- The test is structured as `limits/near_max/fragment_input/components_N` in the test hierarchy.
- The varying type for each location is `vec4` by default, with the last location potentially using `float`, `vec2`, or `vec3` to exactly fill the requested component count.
- Each varying is assigned its location index as a float value, and the fragment shader performs an exact equality check (`i_colorN == type(N.0)`).
- The test uses 6 vertices forming a quad with specific indexing (12 indices for 4 triangles) to cover the full viewport.
