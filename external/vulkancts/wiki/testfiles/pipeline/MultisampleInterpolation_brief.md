# Understanding Brief: pipeline multisample interpolation tests

## One-Sentence Test Purpose

This test family checks whether fragment-shader interpolation functions and interpolation qualifiers select the required sample, centroid, or offset value when multisample shading is enabled.

## Background Knowledge

### Interpolation locations

A fragment input normally receives an interpolated value at a location determined by rasterization. The `sample` qualifier requests per-sample interpolation, while `centroid` selects a location inside both the pixel and its covered primitive. `interpolateAtSample`, `interpolateAtCentroid`, and `interpolateAtOffset` explicitly request values at a sample, centroid, or pixel-relative offset.

Why it matters here:
- The tests compare two paths that should name the same interpolation location.
- A controlled screen-position varying makes a wrong location visible as a color mismatch.

### Sample-rate shading support

The Vulkan `sampleRateShading` feature enables sample shading and multisample interpolation. When `VK_KHR_portability_subset` is present, its `shaderSampleRateInterpolationFunctions` feature controls support for the SPIR-V interpolation-function capability.

Why it matters here:
- The common case support check requires `sampleRateShading`.
- Some Amber-only test families are registered only for monolithic construction because their cases do not receive `PipelineConstructionType`.

## One Concrete Example

The `sample_interpolation_consistency` intermediate node compares a centroid-qualified screen-position varying re-interpolated with `interpolateAtSample(..., gl_SampleID)` against the same varying declared with `sample`. The fragment shader writes green when the values agree within its threshold and red otherwise. The output-image scan treats a nonzero error component as failure.

## End-to-End Test Flow

```text
[host] select image size, sample count, component source, and pipeline construction type
[host] check image support and require sampleRateShading
[host] generate vertex and fragment GLSL for the selected behavior
[host] create multisampled and single-sampled resolve images, then submit a draw
[device] interpolate the varying at the requested location and write a green or red result
[host] resolve and read the image, then either scan for red/error pixels or count distinct colors
[host] report pass only when the selected validation rule succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The C++ source builds GLSL strings for each C++ `MSCase` specialization. Most shaders encode a local comparison and write green for success or red for failure. `reinterpolation_consistency` and `nonuniform_interpolant_indexing` load Amber cases only for the monolithic construction path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multisampled `VK_FORMAT_R8G8B8A8_UNORM` color image | Yes | Yes | Written by the draw | Indirectly, after resolve | Stores per-sample shader output. |
| Single-sampled resolve image | Yes | Yes | Written by resolve | Yes | Supplies the pixels examined by CTS. |
| Vertex buffer | Yes | Yes | Read by the vertex shader | No | Carries positions and, where needed, screen or barycentric values. |
| Push constant `component` | Some cases | Yes | Read by fragment shader | No | Chooses a dynamic vector component in `pushc_component_*` cases. |

## What Is Checked

- Distinct-value cases require at least `numSamples + 1` distinct resolved colors.
- The screen-position and barycentric cases write an error color on an in-shader mismatch; CTS scans the designated error component over the resolve image.
- The centroid-inside-primitive case writes red if any interpolated barycentric component lies outside `[0, 1]`.

## Behavior Parameter Identification

> **Behavior parameter:** test-family behavior
>
> **Candidate values:** `sample_interpolate_at_single_sample`, `sample_interpolate_at_distinct_values`, `sample_interpolate_at_ignores_centroid`, `sample_interpolation_consistency`, `sample_qualifier_distinct_values`, `centroid_interpolation_consistency`, `reinterpolation_consistency`, `nonuniform_interpolant_indexing`, `centroid_qualifier_inside_primitive`, `offset_interpolate_at_pixel_center`, `offset_interpolation_at_sample_position`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sample_interpolate_at_single_sample` | Incorrect single-sample interpolation location. |
| `sample_interpolate_at_distinct_values`, `sample_qualifier_distinct_values` | Sample-specific interpolation does not produce the required distinct values. |
| `sample_interpolate_at_ignores_centroid`, `sample_interpolation_consistency` | `interpolateAtSample` disagrees with the requested sample location or incorrectly retains centroid selection. |
| `centroid_interpolation_consistency`, `centroid_qualifier_inside_primitive` | Centroid interpolation disagrees with the centroid-qualified value or selects a location outside the primitive. |
| `reinterpolation_consistency`, `nonuniform_interpolant_indexing` | Re-interpolation or dynamically indexed interpolant behavior is incorrect. |
| `offset_interpolate_at_pixel_center`, `offset_interpolation_at_sample_position` | Offset interpolation does not match the pixel center or the selected sample position. |

## Important Variations and Special Cases

- The C++ matrix uses image sizes `128x128` and `137x191`, plus sample counts `2`, `4`, `8`, `16`, `32`, and `64`; one single-sample family uses `samples_1`.
- The consistency families add `all_components`, `component_0`, `component_1`, `pushc_component_0`, and `pushc_component_1` intermediate values.
- The Amber families are compiled out under `CTS_USES_VULKANSC` and are registered only under monolithic construction.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Common support and image setup | [`MSCase::checkSupport()` and `checkImagesSupport()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L112-L155) | Establishes feature and image prerequisites. |
| Distinct-color validation | [`MSInstanceDistinctValues::verifyImageData()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L217-L238) | Counts the observed resolved colors. |
| Common error scan | [`checkForError()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L77-L91) | Defines the red/error-pixel check. |
| Registration | [`createMultisampleInterpolationTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1146-L1294) | Creates the registered test-family behaviors and matrices. |
| Core Vulkan feature | [`sampleRateShading`](../../../../vulkan-docs/src/chapters/features.adoc#L258-L265) | Specifies support for sample shading and multisample interpolation. |

## Questions / Risk Points for User Audit

- Is the test-family behavior axis a useful way to navigate this broad matrix?
- Does the brief distinguish the shader-local green/red check from the host image scan clearly enough?
- Are the monolithic-only Amber families described with their construction boundary?

## Conversion Notes for Final Wiki Rewrite

The final page should retain a compact interpolation-location prerequisite, use the test family as its behavioral axis, and copy the failure-cause mapping table unchanged. It should describe generated shaders by their role rather than reproduce source strings, because this page covers many specializations and no local shader-analyzer workflow is available in this repository checkout.
