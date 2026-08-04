# Understanding Brief: pipeline multisample sample-locations tests

## One-Sentence Test Purpose

This test family checks whether `VK_EXT_sample_locations` reports valid capabilities and applies programmable sample locations correctly for sample-location verification, interpolation, and multi-pass color, depth, and stencil drawing; it also exercises the corresponding standard sample-location paths.

## Background Knowledge

### Sample locations and multisampling

A multisampled pixel has several samples. `VK_EXT_sample_locations` lets an application query supported sample-location properties and program sample positions for those samples. The extension reports supported sample counts, a maximum sample-location grid, the coordinate range, subpixel precision, and whether sample locations may vary. Standard locations instead use the device's `standardSampleLocations` limit.

Why it matters here:
- The programmable group checks extension-provided properties and uses supported sample counts from `1` through `16`.
- The standard-location group uses standard positions and omits programmable-location state.

### Observation through rendering

The verification paths render to a multisampled color attachment, resolve it, and inspect a host-visible result. The location path maps each fragment/sample pair to a primitive; the interpolation path compares interpolated vertex data with expected sample coordinates. The draw path exercises two rendering passes with selected clear, layout, command-buffer, and synchronization variations.

Why it matters here:
- A resolved all-green image is the success signal for the location and interpolation paths.
- The draw path covers color, depth, and stencil attachments and checks the final rendering result after selected sample-pattern changes.

## One Concrete Example

For `pipeline.monolithic.multisample.sample_locations_ext.verify_interpolation.samples_4_dynamic`, CTS uses four programmable samples per pixel and dynamic sample-location state. It computes the expected interpolated `vec2` value at every sample into an SSBO, draws a full-screen quad, resolves the color target, and expects every resolved result to be green. A red result means the interpolated value differed from the sample-location-derived reference by at least `0.002` in one component.

## End-to-End Test Flow

```text
[host] select group, pipeline construction type, sample count, sample-location mode, and behavior options
[host] check extension or standard-location support, sample-count support, feature requirements, and variant requirements
[host] query sample-location properties or construct the expected standard-location configuration
[host] create images, image views, buffers, descriptors, pipelines, and host-visible result storage
[device] set or use the selected sample pattern and render verification primitives or two draw passes
[device] resolve or copy the resulting image and make the result visible to the host
[host] compare the observed result with the expected green image or draw reference and report pass or failure
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| `VkPhysicalDeviceSampleLocationsPropertiesEXT` and `VkMultisamplePropertiesEXT` | yes | queried from physical device | yes | Supply the capability and grid values used by programmable-location tests. |
| Multisampled color image and single-sample resolve image | yes | attachments and transfer sources | yes | Hold the rendered verification result and resolved observation. |
| Depth/stencil image and view | yes, for depth or stencil draw leaves | attachment and transfer destination | yes | Exercise compatible sample-location handling for depth or stencil. |
| Sample-data SSBO | yes, for verify paths | read by fragment shader | no | Holds expected coordinates or per-sample indexing data. |
| Generated vertex, fragment, and optional geometry shaders | yes | graphics pipeline | no | Turn the selected sample location into a visible green-or-red result. |
| Host-visible color buffer | yes | transfer destination | yes | Carries the resolved color output to CTS for validation. |

## What Is Checked

- `query.sample_locations_properties` requires at least one legal MSAA sample count, a nonzero bounded grid size, coordinate-range values in `[0, 1]`, and nonzero bounded subpixel precision.
- `query.multisample_properties` checks `vkGetPhysicalDeviceMultisamplePropertiesEXT`, while `sample_locations_properties` uses `vkGetPhysicalDeviceProperties2`: a supported sample count must report a grid at least as large as the extension property grid, while an unsupported count must report `(0, 0)`.
- `verify_location` requires each fragment/sample pair to map to its intended primitive and resolves the pass result to green.
- `verify_interpolation` checks sample-qualified interpolation with `interpolateAtSample`-equivalent sample-position expectations: it calculates expected sample positions in an SSBO and accepts an interpolated value only when both components differ by less than `0.002`.
- `draw` renders selected multi-pass color, depth, or stencil cases and validates the resulting image after `same_pattern`, clear, layout, command-buffer, and event variations.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family under `pipeline.monolithic.multisample.sample_locations_ext` or `pipeline.monolithic.multisample.std_sample_locations`
>
> **Candidate values:** `query`, `verify_location`, `verify_interpolation`, `draw`

## Important Variations and Special Cases

- `query` is registered only for monolithic `sample_locations_ext` without fragment shading rate. It contains `sample_locations_properties` and `multisample_properties`.
- The verify families cover sample counts `1`, `2`, `4`, `8`, and `16`. Programmable-location leaves include variable/invariable patterns, dynamic state, and, except at one sample, closely packed patterns; standard-location leaves use the invariable path.
- Programmable-location variants require `VK_EXT_sample_locations`; standard-location variants require `standardSampleLocations`. Verify paths also require sample-rate shading, and location verification requires geometry shader support.
- Fragment-shading-rate variants require `VK_KHR_fragment_shading_rate`, `pipelineFragmentShadingRate`, and a supported `2x2` rate for the selected sample count.
- Draw cases combine `color`, `depth`, and `stencil`; sample counts `1`, `2`, `4`, `8`, and `16`; separate render passes, separate subpasses, or the same subpass; and compatible clear and option combinations. Incompatible depth/stencil, event, and layout combinations are not registered.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `query` | The implementation reports invalid or internally inconsistent `VK_EXT_sample_locations` property or multisample-grid data. |
| `verify_location` | The selected sample pattern, `gl_SampleID`, primitive association, resolve, transfer, or final image observation is incorrect. |
| `verify_interpolation` | Per-sample interpolation differs from the sample-location-derived expected coordinate, or the associated rendering, resolve, transfer, or observation path is incorrect. |
| `draw` | A selected sample-pattern transition or compatible color, depth, or stencil draw sequence produces an incorrect final result. |

## Source Mapping

- Primary source: [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1)
- Header: [`vktPipelineMultisampleSampleLocationsExtTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.hpp#L1)
- Utilities: [`vktPipelineSampleLocationsUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.cpp#L1)

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support and property query | [`checkSupportSampleLocations()` and property helpers](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L152-L267) | Selects extension or standard support and retrieves sample-location properties. |
| Query validators | [`testQuerySampleLocationProperties()` and `testQueryMultisampleProperties()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1174-L1285) | Defines the property and grid checks. |
| Verify support and shaders | [`checkSupportVerifyTests()` and generated programs](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1346-L1485) | Defines feature requirements and green-or-red verification shaders. |
| Verify test instances | [`VerifyLocationTest` and `VerifyInterpolationTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1838-L1932) | Implements sample-location and interpolation observations. |
| Draw support and programs | [`checkSupportDrawTests()` and `Draw::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2050-L2195) | Defines draw requirements and generated shaders. |
| Registration matrix | [`createTestsInGroup()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3511-L3680) | Builds families, sample-count coverage, options, and compatible draw leaves. |
| Group selection | [`createMultisampleSampleLocationsTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) selects the group using `useStdLocations`, choosing `sample_locations_ext` or `std_sample_locations`. |

## Questions / Risk Points for User Audit

- Does the final page make the separation between extension-programmable and standard sample locations clear?
- Does it distinguish capability queries from rendering-based verification?
- Is the compatibility filtering for draw options clear enough without listing every registered leaf?

## Conversion Notes for Final Wiki Rewrite

Keep the final page centered on the four direct behavior families. Preserve the query contracts, the programmable-versus-standard support split, the per-sample verification mechanism, the draw compatibility constraints, and the complete failure mapping. Include a representative shader walkthrough for interpolation or location verification, but do not duplicate every generated shader or draw leaf.
