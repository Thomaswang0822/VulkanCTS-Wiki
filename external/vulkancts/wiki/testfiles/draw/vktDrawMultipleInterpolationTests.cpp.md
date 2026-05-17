# Multiple Interpolation Tests

## Overview

Tests for multiple interpolation decorations used simultaneously in a single shader stage. Verifies that when a fragment shader receives multiple inputs with different interpolation qualifiers (smooth, flat, noperspective, centroid, sample), the correct interpolation is applied to each input independently. The tests compare results from a multi-interpolation shader against reference images generated with single-interpolation shaders.

## Role

Validates that Vulkan implementations correctly handle multiple interpolation decorations on separate fragment shader inputs within the same draw call. The test renders a triangle with five differently-interpolated color outputs from the vertex shader, then uses a push constant to select which interpolation result to output from the fragment shader. This result is compared against a reference image rendered with only that single interpolation qualifier active. Additionally, the test verifies that different interpolation types produce distinguishable results under multisampling, and that smooth/centroid/sample interpolations may produce equivalent results without multisampling.

## Source Code

- [vktDrawMultipleInterpolationTests.cpp](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.multiple_interpolation
├── separate
└── structured
```

## Test Families

### separate — Interpolation decorations on separate variables

Tests where each interpolation qualifier (smooth, flat, noperspective, centroid, sample) is applied to a separate `out`/`in` variable in the vertex/fragment shaders. No interface block is used; each decorated output is a standalone variable.

#### no_sample_decoration — Without the `sample` qualifier

Tests four interpolation types: smooth, flat, noperspective, and centroid. The `sample` qualifier is excluded, so the `sampleRateShading` feature is not required. Each leaf test name indicates the sample count (e.g., `1_sample`, `2_samples`, etc.).

#### with_sample_decoration — Including the `sample` qualifier

Tests all five interpolation types including `sample`. Requires the `sampleRateShading` device feature. Each leaf test name indicates the sample count.

### structured — Interpolation decorations on struct members

Tests where the interpolation-qualified variables are wrapped in an interface block (`InterfaceBlock`). This requires the `GL_ARB_enhanced_layouts` extension in GLSL. Struct members are accessed with a block prefix (e.g., `ifb.out_color_smooth`). The same sub-structure as `separate` applies.

#### no_sample_decoration — Without the `sample` qualifier (structured)

Same as `separate/no_sample_decoration` but with interpolation qualifiers on struct members inside an interface block.

#### with_sample_decoration — Including the `sample` qualifier (structured)

Same as `separate/with_sample_decoration` but with interpolation qualifiers on struct members inside an interface block.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Sample count | 1, 2, 4, 8, 16, 32, 64 | Number of MSAA samples; 1 means no multisampling |
| Structure type | separate, structured | Whether interpolation qualifiers are on standalone variables or struct members in an interface block |
| Sample decoration | no_sample_decoration, with_sample_decoration | Whether the `sample` auxiliary qualifier is included among the interpolation types |
| Interpolation type | smooth, flat, noperspective, centroid, sample | The interpolation qualifier being tested (used internally for reference comparison) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `framebufferColorSampleCounts` | Sample count must be supported by the device | [vktDrawMultipleInterpolationTests.cpp#L297-L298](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L297-L298) |
| `sampleRateShading` feature | When `includeSampleDecoration` is true | [vktDrawMultipleInterpolationTests.cpp#L300-L301](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L300-L301) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawMultipleInterpolationTests.cpp#L303-L304](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L303-L304) |

## Verification Methods

- **Cross-interpolation comparison**: For each interpolation type, the multi-interpolation shader result is compared against a reference image rendered with only that single interpolation qualifier. The comparison uses a per-pixel integer threshold of 1 per channel at [vktDrawMultipleInterpolationTests.cpp#L626-L646](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L626-L646).
- **Distinctness check**: Different interpolation types must produce distinguishable results under multisampling. If two different interpolation types produce identical results (except for known equivalent pairs like smooth/centroid without multisampling), the test fails at [vktDrawMultipleInterpolationTests.cpp#L817-L823](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L817-L823).
- **Equivalence check for smooth/centroid/sample without multisampling**: When not using multisampling, smooth, centroid, and sample interpolations are expected to produce the same results at [vktDrawMultipleInterpolationTests.cpp#L803-L811](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L803-L811).
- **Sample rate shading fallback**: For the `sample` decoration, results are also compared against a reference rendered with sample rate shading enabled at [vktDrawMultipleInterpolationTests.cpp#L799-L801](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L799-L801).

## Notes

- The render size is 128x128 with format `VK_FORMAT_R8G8B8A8_UNORM` at [vktDrawMultipleInterpolationTests.cpp#L834-L835](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L834-L835).
- A push constant with the interpolation index is used to select which of the five interpolation results the multi-interpolation fragment shader outputs, enabling comparison against single-interpolation reference images.
- The structured variant requires `GL_ARB_enhanced_layouts` because interpolation qualifiers on struct members are not part of core GLSL 430 at [vktDrawMultipleInterpolationTests.cpp#L161](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L161).
- The vertex shader outputs five (or four) color values, each with a different interpolation qualifier, at locations 0-4 (or 0-3).
