# vktPipelineMultisampleInterpolationTests.cpp

## Overview

[`vktPipelineMultisampleInterpolationTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1) implements the [`multisample_interpolation`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1149) topic group. It verifies multisample interpolation behavior including `interpolateAtSample`, `interpolateAtCentroid`, `interpolateAtOffset`, sample qualifier distinct values, centroid qualifier positioning, and consistency of interpolation results.

## Role

Implementation file. The [`createMultisampleInterpolationTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1148) factory function creates the `multisample_interpolation` group, attached directly under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L135).

## Source Code

- Primary source: [`vktPipelineMultisampleInterpolationTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1)
- Header: [`vktPipelineMultisampleInterpolationTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample_interpolation
├── sample_interpolate_at_single_sample
├── sample_interpolate_at_distinct_values
├── sample_interpolate_at_ignores_centroid
├── sample_interpolation_consistency
├── sample_qualifier_distinct_values
├── centroid_interpolation_consistency
├── reinterpolation_consistency (VK_KHR_portability_subset guarded)
├── nonuniform_interpolant_indexing (VK_KHR_portability_subset guarded)
├── centroid_qualifier_inside_primitive
├── offset_interpolate_at_pixel_center
└── offset_interpolation_at_sample_position
```

**Variant coverage**: All variants.

## Test Families

### sample_interpolate_at_single_sample — InterpolateAtSample with single sample

Verifies `interpolateAtSample` returns the same value for all samples when only one sample is used. Contains image size subgroups (128x128, 137x191).

### sample_interpolate_at_distinct_values — InterpolateAtSample distinct per-sample values

Verifies `interpolateAtSample` returns distinct values per sample index.

### sample_interpolate_at_ignores_centroid — InterpolateAtSample ignores centroid

Verifies `interpolateAtSample` ignores the centroid qualifier.

### sample_interpolation_consistency — InterpolateAtSample consistency

Verifies `interpolateAtSample` returns consistent results across invocations. Contains sample count subgroups (2, 4, 8, 16, 32).

### sample_qualifier_distinct_values — Sample qualifier distinct values

Verifies sample qualifier variables produce distinct per-sample values.

### centroid_interpolation_consistency — InterpolateAtCentroid consistency

Verifies `interpolateAtCentroid` returns consistent results. Contains sample count subgroups (2, 4, 8, 16, 32).

### reinterpolation_consistency — Reinterpolation consistency (VK_KHR_portability_subset guarded)

Verifies reinterpolation consistency. Only added when `VK_KHR_portability_subset` is not supported or reports shader sample rate interpolation functions as supported. Contains `component` and `interpolate_at_sample` sub-tests, some using Amber test cases.

### nonuniform_interpolant_indexing — Nonuniform interpolant indexing (VK_KHR_portability_subset guarded)

Verifies nonuniform interpolant indexing. Only added when `VK_KHR_portability_subset` is not supported or reports shader sample rate interpolation functions as supported. Contains `component`, `interpolate_at_sample`, and `interpolate_at_offset` sub-tests.

### centroid_qualifier_inside_primitive — Centroid qualifier inside primitive

Verifies centroid-qualified values lie inside the primitive boundary.

### offset_interpolate_at_pixel_center — InterpolateAtOffset at pixel center

Verifies `interpolateAtOffset(0,0)` matches pixel center.

### offset_interpolation_at_sample_position — Offset interpolation at sample position

Verifies `interpolateAtOffset` matches sample positions. Contains sample count subgroups (2, 4, 8, 16, 32).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Image size | Array | 128x128, 137x191 |
| Sample count | Array | 2, 4, 8, 16, 32 |
| ComponentSource | Enum | CONSTANT, PUSH_CONSTANT, NONE |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `sampleRateShading` | Core feature required for all interpolation tests |
| `VK_KHR_portability_subset` | Guards reinterpolation_consistency and nonuniform_interpolant_indexing groups |

## Verification Methods

- **Pixel value comparison**: Render with interpolation, read back resolved image, compare against expected values
- **Distinct value check**: Verify that per-sample interpolation produces different values for different sample indices
- **Consistency check**: Verify that repeated interpolation calls produce identical results
- **Position validation**: Verify centroid-qualified values fall within the primitive boundary

## Notes

- The `reinterpolation_consistency` and `nonuniform_interpolant_indexing` groups are only added when `VK_KHR_portability_subset` is not supported or reports shader sample rate interpolation functions as supported
- Amber test cases are used for some reinterpolation_consistency sub-tests
