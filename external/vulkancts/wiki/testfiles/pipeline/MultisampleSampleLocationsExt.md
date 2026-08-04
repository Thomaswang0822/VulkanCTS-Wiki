## Overview

**Core question:** Does Vulkan report valid sample-location capabilities and correctly use programmable or standard sample locations when it queries properties, verifies per-sample location and interpolation, and performs multi-pass color, depth, or stencil drawing?

- This page documents the `sample_locations_ext` and `std_sample_locations` test families implemented by [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1-L3696). They appear below both `pipeline.<construction>.multisample` and `pipeline.<construction>.multisample_with_fragment_shading_rate`; the latter selects the fragment-shading-rate variants.
- The file contains both registration and implementation logic. [`createMultisampleSampleLocationsTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3685-L3692) selects `sample_locations_ext` for programmable locations or `std_sample_locations` for standard locations; [`createTestsInGroup()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3511-L3680) creates the four direct families. Its `GroupParams` carries `PipelineConstructionType`, fragment-shading-rate selection, and `useStdLocations` into each group.
- The direct family is the behavioral axis: `query` validates device-reported extension data, `verify_location` validates sample-to-primitive association, `verify_interpolation` validates interpolation at each sample, and `draw` validates selected multi-pass drawing configurations. Sample count, pipeline construction type, fragment shading rate, and draw options expand coverage of the selected behavior.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Programmable and standard sample locations.** `VK_EXT_sample_locations` provides programmable sample positions and exposes `VkPhysicalDeviceSampleLocationsPropertiesEXT`, including supported sample counts, the maximum grid size, coordinate range, subpixel precision, and whether locations can vary. Standard positions use the `standardSampleLocations` device limit instead. [`checkSupportSampleLocations()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L152-L162) chooses the required support path.
- **Sample-location grids.** A sample-location grid supplies positions for the samples of a pixel. For programmable locations, the implementation queries `VkMultisamplePropertiesEXT` for a supported grid size. The draw path uses the full returned grid; standard locations use a `1x1` grid ([draw initialization](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2203-L2232)).
- **Per-sample observation.** The verify paths render to a color attachment, produce a single-sample result (by resolving when the selected count is greater than one), copy that result to host-visible memory, and compare it with the expected green image. They make a per-sample error observable through a final color image, not through an independently observable pipeline-stage diagnosis.
- **Fragment shading rate variants.** A fragment-shading-rate leaf requires `VK_KHR_fragment_shading_rate`, `pipelineFragmentShadingRate`, and a supported `2x2` fragment size for the selected sample count ([requirement check](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L198-L230)).

## Registration Hierarchy

```text
pipeline.monolithic.multisample.sample_locations_ext
├── query
├── verify_location
├── verify_interpolation
└── draw
```

The tree shows the concrete monolithic programmable-location branch and its direct children. A sibling `pipeline.monolithic.multisample.std_sample_locations` branch contains `verify_location`, `verify_interpolation`, and `draw`. Additional `multisample_with_fragment_shading_rate` roots contain `sample_locations_ext` and, for supported construction types, `std_sample_locations`; each of those intermediate nodes contains the applicable verification and draw groups. `sample_locations_ext` is attached for every construction root passed to the parent multisample factory. `std_sample_locations` is attached only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction ([parent registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7745-L7755)). `query` is registered only for programmable locations in the non-FSR monolithic branch. The implementation intentionally limits the verify and draw range to sample counts `1`, `2`, `4`, `8`, and `16`; the source notes that no implementation currently supports `32` or `64` programmable samples ([registration range](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3530-L3534)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Group | `sample_locations_ext`, `std_sample_locations` | Selects programmable extension locations or standard locations. | [Group factory](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3685-L3692) |
| Direct family | `query`, `verify_location`, `verify_interpolation`, `draw` | Selects the capability-query, per-sample verification, or multi-pass drawing contract. | [Family construction](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3517-L3680) |
| Sample count | `samples_1`, `samples_2`, `samples_4`, `samples_8`, `samples_16` | Changes the number of samples that must use the selected location behavior. | [Range and loops](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3530-L3554) |
| Location pattern | programmable variable, programmable invariable, standard | Selects whether the test uses extension-programmable locations, permits variation, or uses standard locations. | [`addCases()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1934-L1991) |
| Verify options | dynamic state; closely packed pattern where applicable; fragment shading rate | Expands programmable-location verification coverage. | [`addCases()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1951-L1989) |
| Image aspect | `color`, `depth`, `stencil` | Selects the attachment aspect for draw validation. | [Aspect matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3619-L3635) |
| Draw placement | `separate_renderpass`, `separate_subpass`, `same_subpass` | Changes where the two drawing passes execute. | [Draw/clear matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3604-L3617) |
| Clear mode | `no_clear`, `load_op_clear`, `clear_attachments`, `clear_image` | Changes clearing between selected draw operations. | [Draw/clear matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3604-L3617) |
| Draw options | `same_pattern`, `dynamic`, `secondary_cmd_buf`, `general_layout`, `event` | Exercises sample-pattern, command-buffer, layout, and synchronization choices when compatible. | [Option sets](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3564-L3602) |
| Pipeline construction type | supported construction variants | Repeats each selected matrix through the pipeline registration framework. | [Support checks](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1346-L1371) |

## Behavior Parameters

The direct family below the selected sample-location group determines the observable behavior and validator.

### `query`: extension property consistency

The two `query` leaves validate data returned by the extension's physical-device query APIs. `sample_locations_properties` requires at least one legal MSAA count, a nonzero bounded maximum grid, coordinate ranges in `[0, 1]`, and nonzero bounded subpixel precision. `multisample_properties` iterates counts from `1` to `64`: a count advertised in `sampleLocationSampleCounts` must report a grid at least as large as the extension property grid, while an unadvertised count must report `(0, 0)` ([validators](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1174-L1285)).

### `verify_location`: sample-to-primitive association

This family checks that every custom or standard sample location is associated with the intended primitive. It renders generated verification geometry and produces a single-sample image, resolving the color attachment for multisample cases. The fragment shader compares `gl_PrimitiveID` with the index calculated from fragment coordinates and `gl_SampleID`; green means a match and red means a mismatch ([shader](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1393-L1436)). [`VerifyLocationTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1838-L1889) accepts only an all-green final image.

### `verify_interpolation`: interpolation at each sample

This family checks interpolation of a sample-qualified input at every selected sample location. CTS fills an SSBO with coordinates generated for the current sample grid, renders a full quad, and has the fragment shader compare `in_value` against the indexed expected coordinate. Both components must differ by less than `0.002`; the shader emits green on success and red otherwise ([shader](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1438-L1485)). [`VerifyInterpolationTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1891-L1932) checks the final single-sample image, which is resolved for multisample cases.

### `draw`: multi-pass drawing with selected sample-pattern operations

This family draws with two passes, selected sample patterns, and compatible color, depth, or stencil operations. It creates a color image at the selected sample count and a single-sample resolve image (the latter is used when the count is greater than one); depth and stencil leaves additionally create a compatible depth/stencil image using `VK_IMAGE_CREATE_SAMPLE_LOCATIONS_COMPATIBLE_DEPTH_BIT_EXT` for programmable locations ([image setup](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2234-L2280)). Depth and stencil behavior is observed indirectly through the final color image rather than by reading those attachments. The option matrix covers same or changing patterns, dynamic state, secondary command buffers, general layouts, and event-based barriers where those choices are valid.

## Shader Analysis

The file generates GLSL at runtime. The representative interpolation shader is compact and makes the expected sample coordinate explicit, so it demonstrates the family without implying that the draw path uses the same shader.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
pipeline.monolithic.multisample.sample_locations_ext.verify_interpolation.samples_4_dynamic
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `samples_4` | Four sample locations are evaluated for each pixel. |
| `sample_locations_ext` | The case uses programmable-location support rather than `standardSampleLocations`. |
| `dynamic` | Sample locations are supplied through dynamic pipeline state. |
| `verify_interpolation` | The expected per-sample position is compared with a sample-qualified interpolated input. |

#### Purpose

The shader checks whether the rasterizer evaluates the sample-qualified input at the coordinate selected by the current sample-location grid. A mismatch in either component produces red output, which becomes visible in the copied final image (after resolve for multisample cases).

#### Structural Design

The vertex shader copies the position to `o_position`. The fragment shader receives it as `sample in vec2 in_value`, derives an SSBO index from `gl_FragCoord` and `gl_SampleID`, loads the expected coordinate, and compares it with a fixed tolerance. The host prepares the SSBO from the same selected grid before the draw.

#### Shader Code

The source-generated GLSL has this essential structure:

```glsl
layout(location = 0) sample in  vec2 in_value;
layout(location = 0)        out vec4 o_color;

layout(set = 0, binding = 0, std430) readonly buffer SampleData {
    uvec2 renderSize;
    uvec2 gridSize;
    uint  samplesPerPixel;
          // padding 1-uint size;
    vec2  data[];
} sb_data;

void main(void)
{
    uvec2 fragCoord = uvec2(gl_FragCoord.xy);
    uint  index     = (fragCoord.y * sb_data.renderSize.x + fragCoord.x) *
                      sb_data.samplesPerPixel + gl_SampleID;
    vec2  diff      = abs(sb_data.data[index] - in_value);
    vec2  threshold = vec2(0.002);

    if (all(lessThan(diff, threshold)))
        o_color = vec4(0.0, 1.0, 0.0, 1.0);
    else
        o_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

The full source emits this fragment program through [`addProgramsVerifyInterpolation()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1438-L1485). The host-side `VerifyInterpolationTest` fills `data[]` with expected positions from `genFramebufferSampleLocations()` before submitting the draw ([setup](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1899-L1930)).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level change relative to this shader | Evidence |
|---------------------|--------------------------------------------|----------|
| Sample count | The same indexing structure uses the selected `samplesPerPixel` and corresponding SSBO data. | [`addCases()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1934-L1991) |
| Programmable versus standard locations | The generated verification shader remains the same; support and grid preparation choose programmable or standard positions. | [Support selection](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L152-L162) |
| Dynamic state and packed pattern | These alter the configured sample pattern and registration options, not this GLSL comparison. | [`addCases()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1951-L1989) |

## Runtime Execution and Result Checking

- `query` directly retrieves extension properties with `vkGetPhysicalDeviceProperties2` and per-sample-count data with `vkGetPhysicalDeviceMultisamplePropertiesEXT`; it returns pass only after the property contracts hold.
- Verify leaves require extension support or `standardSampleLocations`, sample-rate shading, the requested framebuffer color sample count, and pipeline-construction support. Programmable variable-pattern leaves also require `variableSampleLocations`; location verification additionally requires geometry shader support ([support checks](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1346-L1378)).
- `VerifyLocationTest` and `VerifyInterpolationTest` build vertex data and a sample-data buffer, render one pass to the selected-sample-count color image, produce a single-sample result (resolving only when needed), and compare the mapped result with a green image. Interpolation prepares one `vec2` expected coordinate for each sample of each render pixel.
- Draw leaves require extension or standard support, the requested color sample count, and compatible draw options. Changing a depth/stencil pattern without clearing is not registered; event-based layout changes are allowed only outside a render pass; general layout is not selected inside the same subpass ([filters](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3649-L3666)).
- A failure identifies the selected test contract but does not alone isolate property reporting, sample-pattern programming, rasterization, resolve, synchronization, transfer, or host comparison as the exclusive faulting stage.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `query` | The implementation reports invalid or internally inconsistent `VK_EXT_sample_locations` property or multisample-grid data. |
| `verify_location` | The selected sample pattern, `gl_SampleID`, primitive association, resolve, transfer, or final image observation is incorrect. |
| `verify_interpolation` | Per-sample interpolation differs from the sample-location-derived expected coordinate, or the associated rendering, resolve, transfer, or observation path is incorrect. |
| `draw` | A selected sample-pattern transition or compatible color, depth, or stencil draw sequence produces an incorrect final color result; depth/stencil behavior is observed through its effect on color drawing. |

### Cause Analysis

#### Invalid sample-location property or grid data

**Possible failure symptoms:** `query.sample_locations_properties` reports that no legal sample count is present, the grid is invalid, a coordinate range lies outside `[0, 1]`, or subpixel precision is invalid. `query.multisample_properties` reports a grid that is too small for a supported count or nonzero for an unsupported count.

**Possible implementation causes:** Physical-device property reporting may be inconsistent between `VkPhysicalDeviceSampleLocationsPropertiesEXT` and `VkMultisamplePropertiesEXT`, or may violate the test's validity bounds. These leaves do not exercise rendering, so the observation is limited to the queried API data.

#### Sample-to-primitive association mismatch

**Possible failure symptoms:** `verify_location` resolves a result that is not entirely green.

**Possible implementation causes:** The implementation may apply the selected sample locations incorrectly, associate `gl_SampleID` with the wrong primitive, rasterize a verification primitive incorrectly, or mishandle resolve or readback. The resolved color result exposes the contract failure but does not distinguish those stages.

#### Sample interpolation mismatch

**Possible failure symptoms:** `verify_interpolation` resolves red output because one or both components of `in_value` differ from the expected SSBO coordinate by at least `0.002`.

**Possible implementation causes:** The sample-location grid, sample-qualified interpolation, fragment sample identity, SSBO indexing, rasterization, resolve, or readback can cause the mismatch. The expected coordinates come from the host's selected pixel grid, so a failure means the final observed interpolation does not agree with that configuration.

#### Multi-pass draw mismatch

**Possible failure symptoms:** A `draw` leaf rejects the final resolved-or-copied color image after the selected clear, layout, command-buffer, or synchronization configuration. Depth and stencil leaves still validate color output; their depth/stencil state controls which color fragments are produced.

**Possible implementation causes:** The implementation may mishandle changing or preserving a sample pattern, depth/stencil compatibility, dynamic state, a secondary command buffer, a layout transition, or an event barrier. The final image classifies the selected combination but does not establish an exclusive internal cause.

## Case Pruning

### Requirement-based pruning

- Programmable-location leaves require `VK_EXT_sample_locations`; standard-location leaves require `standardSampleLocations` ([support selector](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L152-L162)).
- Verify leaves require sample-rate shading, supported framebuffer color sample counts, and, for programmable locations, the requested extension sample count. Variable-pattern leaves require `variableSampleLocations`; location verification requires the geometry shader feature.
- Fragment-shading-rate leaves require the extension, `pipelineFragmentShadingRate`, and a supported `2x2` rate for the chosen sample count.
- Draw leaves check the requested sample count, extension or standard support, variable locations when changing a same-subpass programmable pattern, pipeline-construction requirements, and event support for portability-subset implementations ([draw support](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2050-L2082)).

### Design-based pruning

- The registration range stops at `16` samples because the source does not register programmable `32`- or `64`-sample cases.
- `query` is intentionally limited to the non-FSR monolithic programmable-location branch because it validates extension properties rather than pipeline variants.
- Standard-location verify cases use the invariable pattern. Standard draw cases require `same_pattern` and therefore exclude dynamic state.
- Draw registration removes combinations that would be undefined or illegal: depth/stencil changing-pattern cases cannot use `no_clear`; event-based layout changes cannot occur inside render passes; and a general-layout transition cannot occur inside the same subpass.

## Key Takeaways

- The file tests two location modes: programmable `VK_EXT_sample_locations` and standard sample locations.
- Its four direct families separate device-property consistency, sample-to-primitive association, per-sample interpolation, and multi-pass drawing behavior.
- The verify families use generated shaders and an all-green resolved image to make per-sample correctness observable.
- The draw family expands coverage through compatible color/depth/stencil, clear, layout, command-buffer, synchronization, and pipeline-construction combinations.
- The observed final image or property result identifies a behavior-contract failure, not one exclusive internal pipeline stage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support selection and property retrieval | [`checkSupportSampleLocations()` and `getSampleLocationsPropertiesEXT()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L152-L267) | Chooses extension or standard support and retrieves programmable-location data. |
| Property-query tests | [`testQuerySampleLocationProperties()` and `testQueryMultisampleProperties()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1174-L1285) | Defines valid property and grid results. |
| Verify support | [`checkSupportVerifyTests()` and `checkSupportVerifyTestsPrimID()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1346-L1378) | Defines verify-family feature and capability requirements. |
| Location shader and test | [`addProgramsVerifyLocationGeometry()` and `VerifyLocationTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1393-L1436) | Implements primitive/sample association observation. |
| Interpolation shader and test | [`addProgramsVerifyInterpolation()` and `VerifyInterpolationTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1438-L1485) | Implements sample-coordinate interpolation observation. |
| Draw support and shaders | [`checkSupportDrawTests()` and `Draw::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2050-L2195) | Defines draw requirements and generated graphics shaders. |
| Draw image setup | [`DrawTest::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L2234-L2280) | Creates multisampled, resolve, and optional depth/stencil images. |
| Registration matrix | [`createTestsInGroup()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3511-L3680) | Builds behavior families, option sets, and compatible leaves. |
| Source implementation and supporting interfaces | [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1), [`vktPipelineMultisampleSampleLocationsExtTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.hpp#L1), and [`vktPipelineSampleLocationsUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.cpp#L1) | Identify the implementation file, its interface, and shared sample-location utilities. |
| Group factory | [`createMultisampleSampleLocationsTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L3692) | Creates the programmable or standard group name. |
