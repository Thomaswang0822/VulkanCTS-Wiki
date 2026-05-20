# vktDrawInvertedDepthRangesTests.cpp

## Overview

Tests for inverted depth ranges, where `minDepth > maxDepth` in the viewport state. This configuration causes depth values to be remapped in reverse. The tests verify that depth buffer values and color output (which encodes `gl_FragCoord.z`) are correct for various depth range inversions, with and without depth clamping and depth bias.

## Role

Validates that implementations correctly handle inverted depth ranges (`minDepth > maxDepth`) as specified by the Vulkan specification. When the depth range is inverted, the depth value `d` is mapped to `d * maxDepth + (1 - d) * minDepth`, which reverses the depth ordering. The tests cover:

- Different inversion magnitudes (delta zero, small delta, full delta, and unrestricted range).
- Depth clamping enabled vs disabled.
- Depth bias with positive and negative clamp values.

## Source Code

- [vktDrawInvertedDepthRangesTests.cpp](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.inverted_depth_ranges
├── depthclamp_deltazero
├── depthclamp_deltasmall
├── depthclamp_deltaone
├── depthclamp_deltaone_bias_clamp_neg
├── depthclamp_deltasmall_bias_clamp_pos
├── depthclamp_depth_range_unrestricted
├── nodepthclamp_deltazero
├── nodepthclamp_deltasmall
├── nodepthclamp_deltaone
├── nodepthclamp_deltaone_bias_clamp_neg
├── nodepthclamp_deltasmall_bias_clamp_pos
└── nodepthclamp_depth_range_unrestricted
```

## Test Families

### depthclamp_* — Inverted depth ranges with depth clamping enabled

Tests inverted depth ranges with `depthClampEnable = VK_TRUE`. When depth clamping is enabled, fragments with depth values outside [0,1] are clamped rather than discarded. The depth range inversion is applied after clamping. The reference image accounts for clamping to the [minDepth, maxDepth] range.

**Test class**: [InvertedDepthRangesTest](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L665) / [InvertedDepthRangesTestInstance](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L93)

### nodepthclamp_* — Inverted depth ranges with depth clamping disabled

Tests inverted depth ranges with `depthClampEnable = VK_FALSE`. Without depth clamping, fragments whose depth values fall outside [0,1] are discarded. The reference image excludes such fragments. Pixels near the depth boundaries (0.0 and 1.0) are masked in the stencil aspect of the reference to avoid rounding-related comparison failures.

**Test class**: [InvertedDepthRangesTest](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L665) / [InvertedDepthRangesTestInstance](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L93)

### Depth delta sub-cases

Each depth clamp group contains the following depth parameter sub-cases:

| Sub-case | Delta | Depth Bias | Bias Clamp | minDepth | maxDepth |
|----------|-------|------------|------------|----------|----------|
| `deltazero` | 0.0 | No | 0.0 | 0.5 | 0.5 |
| `deltasmall` | 0.3 | No | 0.0 | 0.65 | 0.35 |
| `deltaone` | 1.0 | No | 0.0 | 1.0 | 0.0 |
| `deltaone_bias_clamp_neg` | 1.0 | Yes | -0.003 | 1.0 | 0.0 |
| `deltasmall_bias_clamp_pos` | 0.3 | Yes | 0.003 | 0.65 | 0.35 |
| `depth_range_unrestricted` | 2.7 | No | 0.0 | 1.85 | -0.85 |

**Registration**: [populateTestGroup](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L737)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| depthClamp | `depthclamp`, `nodepthclamp` | Whether VK_PIPELINE_RASTERIZATION_STATE depthClampEnable is true |
| depthDelta | 0.0, 0.3, 1.0, 2.7 | Difference between minDepth and maxDepth |
| depthBiasEnable | false, true | Whether depth bias is applied |
| depthBiasClamp | 0.0, -0.003, 0.003 | Depth bias clamp value |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `DEVICE_CORE_FEATURE_DEPTH_CLAMP` | When `depthClampEnable = VK_TRUE` | [checkSupport](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L714-L715) |
| `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` | When `depthBiasEnable = true` and `depthBiasClamp != 0.0` | [checkSupport](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L717-L718) |
| `VK_EXT_depth_range_unrestricted` | When minDepth or maxDepth is outside [0,1] | [checkSupport](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L720-L722) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [checkSupport](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L724-L725) |

## Verification Methods

| Method | Description | Source |
|--------|-------------|--------|
| Fuzzy image comparison (color) | `tcu::fuzzyCompare` with 0.02f threshold on the color attachment, where the red channel encodes the final depth value | [iterate](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L615-L617) |
| Per-pixel depth threshold comparison | Each depth pixel compared against reference with `kDepthThreshold` (0.0064f) tolerance; pixels near depth boundaries are masked via stencil to avoid rounding issues | [iterate](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L632-L657) |
| Error mask generation | A green/red error mask image is produced for depth comparison failures, logged alongside result and reference depth images | [iterate](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L626-L657) |

## Notes

- The fragment shader outputs `vec4(gl_FragCoord.z, 0.5, 0.5, 1.0)`, encoding the interpolated depth value in the red channel of the color attachment for independent verification alongside the depth buffer.
- The depth attachment format is `VK_FORMAT_D16_UNORM`, providing 16-bit depth precision.
- The reference image generation accounts for depth bias calculations including the `dbclamp` function, which clamps the bias based on the sign of `depthBiasClamp` and inverts the bias when the depth range is inverted (`maxDepth < minDepth`).
- The `depth_range_unrestricted` sub-case requires the `VK_EXT_depth_range_unrestricted` extension because it uses minDepth=1.85 and maxDepth=-0.85, which are outside the standard [0,1] range.
