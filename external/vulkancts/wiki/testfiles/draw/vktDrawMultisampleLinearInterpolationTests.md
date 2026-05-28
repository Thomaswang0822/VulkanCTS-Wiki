# Multisample Linear Interpolation Tests

## Overview

Tests for the `interpolateAtOffset` and `interpolateAtSample` GLSL functions with `noperspective` (linear) interpolation in multisample rendering. Verifies that linear interpolation at explicit offsets and sample positions produces results consistent with a reference image computed from fragment coordinates.

## Role

Validates that Vulkan implementations correctly perform linear (noperspective) interpolation when using the `interpolateAtOffset` and `interpolateAtSample` built-in functions. The test renders two images: a reference image using smooth interpolation with color computed from `gl_FragCoord`, and a result image using noperspective interpolation with `interpolateAtOffset` and `interpolateAtSample`. The two images are compared with a small floating-point threshold. An additional check within the fragment shader verifies that `interpolateAtSample` and `interpolateAtOffset` at the sample position produce consistent results.

## Source Code

- [vktDrawMultisampleLinearInterpolationTests.cpp](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.linear_interpolation
├── no_offset_1_sample
├── no_offset_2_samples
├── no_offset_4_samples
├── no_offset_8_samples
├── no_offset_16_samples
├── no_offset_32_samples
├── no_offset_64_samples
├── offset_min_1_sample
├── offset_min_2_samples
├── offset_min_4_samples
├── offset_min_8_samples
├── offset_min_16_samples
├── offset_min_32_samples
├── offset_min_64_samples
├── offset_max_1_sample
├── offset_max_2_samples
├── offset_max_4_samples
├── offset_max_8_samples
├── offset_max_16_samples
├── offset_max_32_samples
└── offset_max_64_samples
```

## Test Families

### no_offset_* — Interpolation with zero offset

Tests `interpolateAtOffset` with an offset of (0.0, 0.0) and `interpolateAtSample` at the current sample ID. The reference image is computed using `gl_FragCoord` without any offset adjustment. Each leaf test varies the sample count from 1 to 64.

### offset_min_* — Interpolation with minimum negative offset

Tests `interpolateAtOffset` with an offset of (-0.5, -0.5), the minimum valid offset value. The reference image accounts for this offset in its `gl_FragCoord`-based computation. Each leaf test varies the sample count.

### offset_max_* — Interpolation with maximum positive offset

Tests `interpolateAtOffset` with an offset of (0.4375, 0.4375), the maximum valid offset value (in half-pixel units, the maximum is 1/2 - 1/16 = 0.4375). The reference image accounts for this offset. Each leaf test varies the sample count.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Offset | (0.0, 0.0), (-0.5, -0.5), (0.4375, 0.4375) | The offset passed to `interpolateAtOffset` |
| Sample count | 1, 2, 4, 8, 16, 32, 64 | Number of MSAA samples; reduced to 4 max when using secondary command buffers |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `sampleRateShading` feature | Always required | [vktDrawMultisampleLinearInterpolationTests.cpp#L645](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L645) |
| `framebufferColorSampleCounts` | Sample count must be supported | [vktDrawMultisampleLinearInterpolationTests.cpp#L647-L649](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L647-L649) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawMultisampleLinearInterpolationTests.cpp#L652-L653](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L652-L653) |
| `VK_KHR_portability_subset` + `shaderSampleRateInterpolationFunctions` | When portability subset is supported | [vktDrawMultisampleLinearInterpolationTests.cpp#L655-L660](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L655-L660) |

## Verification Methods

- **Floating-point threshold comparison**: The reference image (smooth interpolation with `gl_FragCoord`-based color) is compared against the result image (noperspective interpolation with `interpolateAtOffset`/`interpolateAtSample`) using `tcu::floatThresholdCompare` with a threshold of 0.005 per channel at [vktDrawMultisampleLinearInterpolationTests.cpp#L511-L513](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L511-L513).
- **In-shader consistency check**: The fragment shader compares `interpolateAtSample(in_color, gl_SampleID)` against `interpolateAtOffset(in_color, gl_SamplePosition - vec2(0.5))`. If the difference exceeds a tiny threshold (0.000001), the blue channel is set to 1.0, which would cause the overall image comparison to fail at [vktDrawMultisampleLinearInterpolationTests.cpp#L629-L635](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L629-L635).

## Notes

- The render size is 16x16 pixels at [vktDrawMultisampleLinearInterpolationTests.cpp#L699](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L699).
- The interpolation range is 1.0, meaning vertex color values span [0, 1] at [vktDrawMultisampleLinearInterpolationTests.cpp#L699](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L699).
- The test draws a diamond shape (two triangles) where the reference draw clips to the viewport and the noperspective draw extends beyond it, ensuring the interpolation produces a visually distinct result.
- When using secondary command buffers with dynamic rendering, sample counts above 4 are skipped to reduce test count at [vktDrawMultisampleLinearInterpolationTests.cpp#L696-L697](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L696-L697).
- The `VK_KHR_portability_subset` check for `shaderSampleRateInterpolationFunctions` ensures the implementation supports the interpolation functions required by this test.
