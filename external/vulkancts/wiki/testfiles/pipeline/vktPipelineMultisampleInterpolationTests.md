# vktPipelineMultisampleInterpolationTests.cpp

## Overview

[`vktPipelineMultisampleInterpolationTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1) implements the [`multisample_interpolation`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1149) topic group. It verifies multisample interpolation behavior including `interpolateAtSample`, `interpolateAtCentroid`, `interpolateAtOffset`, sample qualifier distinct values, centroid qualifier positioning, and consistency of interpolation results.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleInterpolationTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1)
- Header: [`vktPipelineMultisampleInterpolationTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Path

[`createMultisampleInterpolationTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1148) returns the `multisample_interpolation` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
multisample_interpolation
├── sample_interpolate_at_single_sample
│   └── {image_size}
├── sample_interpolate_at_distinct_values
├── sample_interpolate_at_ignores_centroid
├── sample_interpolation_consistency
│   └── {sample_count}
├── sample_qualifier_distinct_values
├── centroid_interpolation_consistency
│   └── {sample_count}
├── reinterpolation_consistency          (VK_KHR_portability_subset guarded)
│   ├── component
│   └── interpolate_at_sample
├── nonuniform_interpolant_indexing      (VK_KHR_portability_subset guarded)
│   ├── component
│   ├── interpolate_at_sample
│   └── interpolate_at_offset
├── centroid_qualifier_inside_primitive
├── interpolate_at_offset_pixel_center
└── offset_interpolation_at_sample_position
    └── {sample_count}
```

## Test Families

| Family | Description |
|---|---|
| MSCaseInterpolateAtSampleSingleSample | Verifies `interpolateAtSample` returns the same value for all samples when only one sample is used |
| MSCaseInterpolateAtSampleDistinctValues | Verifies `interpolateAtSample` returns distinct values per sample index |
| MSCaseInterpolateAtSampleIgnoresCentroid | Verifies `interpolateAtSample` ignores centroid qualifier |
| MSCaseInterpolateAtSampleConsistency | Verifies `interpolateAtSample` returns consistent results across invocations |
| MSCaseSampleQualifierDistinctValues | Verifies sample qualifier variables produce distinct per-sample values |
| MSCaseInterpolateAtCentroidConsistency | Verifies `interpolateAtCentroid` returns consistent results |
| MSCaseCentroidQualifierInsidePrimitive | Verifies centroid-qualified values lie inside the primitive |
| MSCaseInterpolateAtOffsetPixelCenter | Verifies `interpolateAtOffset(0,0)` matches pixel center |
| MSCaseInterpolateAtOffsetSamplePosition | Verifies `interpolateAtOffset` matches sample positions |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Image size | Array | 128x128, 256x256, 512x512 |
| Sample count | Array | 2, 4, 8, 16 |
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
