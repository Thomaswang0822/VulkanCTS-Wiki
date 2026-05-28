# vktPipelineMultisampleSampleLocationsExtTests.cpp

## Overview

[`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1) implements the [`sample_locations_ext`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) and [`std_sample_locations`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) topic groups under `multisample`. It verifies VK_EXT_sample_locations functionality including querying sample location properties, verifying programmable sample locations, verifying interpolation at sample locations, and drawing with various sample location configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1)
- Header: [`vktPipelineMultisampleSampleLocationsExtTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.hpp#L1)
- Utilities: [`vktPipelineSampleLocationsUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample.sample_locations_ext
├── query (monolithic, no fragment shading rate)
├── verify_location
├── verify_interpolation
└── draw

pipeline.monolithic.multisample.std_sample_locations
├── verify_location
├── verify_interpolation
└── draw
```

**Variant coverage**: All variants. The `sample_locations_ext` group is registered for all non-VulkanSC variants. The `std_sample_locations` group is limited to monolithic, fast-linked-library, and shader_object_unlinked_spirv variants.

## Test Families

### query — Sample location property queries

Verifies that sample location property queries return valid results. Contains two leaf tests: `sample_locations_properties` and `multisample_properties`, both checking `VK_EXT_sample_locations` support. Only registered under `sample_locations_ext` for the monolithic pipeline construction type without fragment shading rate.

### verify_location — Programmable sample location verification

Verifies that programmable sample locations are correctly applied. Contains per-sample-count subgroups (1, 2, 4, 8, 16, subject to device limits), each with leaf test cases generated from `VerifyLocationTest` parameterized by sample count, pipeline construction type, fragment shading rate usage, and standard vs. programmable locations. Present under both `sample_locations_ext` and `std_sample_locations`.

### verify_interpolation — Interpolation at sample locations

Verifies that `interpolateAtSample` returns values consistent with the configured sample locations. Contains per-sample-count subgroups (1, 2, 4, 8, 16, subject to device limits), each with leaf test cases generated from `VerifyInterpolationTest`. Present under both `sample_locations_ext` and `std_sample_locations`.

### draw — Drawing with programmable sample locations

Verifies rendering with programmable sample locations produces correct output. Contains per-image-aspect subgroups (`color`, `depth`, `stencil`), each with per-sample-count subgroups (1, 2, 4, 8, 16), each containing leaf tests parameterized by draw/clear configuration and option flags. The option flags vary between `sample_locations_ext` and `std_sample_locations`:

- Under `sample_locations_ext`: options include `same_pattern`, dynamic state, secondary command buffer, general layout, and wait events combinations
- Under `std_sample_locations`: options include `same_pattern`, secondary command buffer, general layout, and wait events combinations (no dynamic state option)

Draw/clear configurations include combinations of draw-in mode (render passes, subpasses, same subpass) and clear mode (no clear, load-op clear, cmd clear attachments, cmd clear image), with incompatible combinations filtered out.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Sample count | Array | 1, 2, 4, 8, 16 (subject to device limits) |
| Image aspect | Enum | Color, depth, stencil |
| useFragmentShadingRate | Bool | false / true |
| useStdLocations | Bool | false (sample_locations_ext), true (std_sample_locations) |
| PipelineConstructionType | Parameter | All variant types |

## Support / Feature Requirements

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
