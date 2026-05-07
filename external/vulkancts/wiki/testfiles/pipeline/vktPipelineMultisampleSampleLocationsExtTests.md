# vktPipelineMultisampleSampleLocationsExtTests.cpp

## Overview

[`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1) implements the [`sample_locations_ext`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) and [`std_sample_locations`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) topic groups under `multisample`. It verifies VK_EXT_sample_locations functionality including querying sample location properties, verifying programmable sample locations, verifying interpolation at sample locations, and drawing with various sample location configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1)
- Header: [`vktPipelineMultisampleSampleLocationsExtTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.hpp#L1)
- Utilities: [`vktPipelineSampleLocationsUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.cpp#L1)

## Registration Path

[`createMultisampleSampleLocationsTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3686) returns the `sample_locations_ext` (when `useStdLocations=false`) or `std_sample_locations` (when `useStdLocations=true`) group, added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
sample_locations_ext
├── query
├── verify_location
│   └── {sample_case}
├── verify_interpolation
│   └── {sample_case}
└── draw
    └── {image_aspect}
        └── {sample_count}

std_sample_locations
├── query
├── verify_location
│   └── {sample_case}
├── verify_interpolation
│   └── {sample_case}
└── draw
    └── {image_aspect}
        └── {sample_count}
```

## Test Families

| Family | Description |
|---|---|
| Query test | Verifies sample location property queries return valid results |
| Verify location test | Verifies that programmable sample locations are correctly applied |
| Verify interpolation test | Verifies that interpolation at sample locations produces correct results |
| Draw test | Verifies rendering with programmable sample locations produces correct output |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Sample count | Array | 1, 2, 4, 8, 16 (subject to device limits) |
| Image aspect | Enum | Color, depth, stencil |
| useFragmentShadingRate | Bool | false / true |
| useStdLocations | Bool | false (sample_locations_ext), true (std_sample_locations) |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_sample_locations` | Primary extension for all tests |
| `VK_KHR_fragment_shading_rate` | Required for fragment shading rate variants |

## Verification Methods

- **Property query verification**: Verify that `vkGetPhysicalDeviceProperties2` returns valid sample location properties
- **Location verification**: Set programmable sample locations, render, verify output matches expected positions
- **Interpolation verification**: Verify that `interpolateAtSample` returns values consistent with the configured sample locations
- **Draw verification**: Render with programmable sample locations, compare resolved image against expected values

## Notes

- The group name depends on `useStdLocations`: `sample_locations_ext` for programmable locations, `std_sample_locations` for standard locations
- Fragment shading rate variants are only registered when `VK_KHR_fragment_shading_rate` is supported
