## Overview

**Core question:** Do fragment-shader interpolation functions and interpolation qualifiers produce values at the requested sample, centroid, or offset location?

- This page documents the `pipeline.multisample_interpolation` test family implemented by [`vktPipelineMultisampleInterpolationTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1-L1298).
- The family uses generated vertex and fragment shaders, multisampled color images, and resolved-image checks to expose interpolation-location mistakes as colors or invalid barycentric values.
- Its direct children choose the interpolation contract under test. Image size, sample count, vector-component selection, and pipeline construction type vary coverage without changing that contract.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Interpolation locations.** A fragment input receives an interpolated value. The `sample` qualifier selects per-sample interpolation, while `centroid` selects a location inside the pixel and covered primitive. `interpolateAtSample`, `interpolateAtCentroid`, and `interpolateAtOffset` explicitly request one of those locations.
- **Sample-rate shading.** Vulkan's [`sampleRateShading`](../../../../vulkan-docs/src/chapters/features.adoc#L258-L265) feature covers sample shading and multisample interpolation. The interpolation-offset limits define the supported interval and precision for `InterpolateAtOffset` ([`minInterpolationOffset` through `subPixelInterpolationOffsetBits`](../../../../vulkan-docs/src/chapters/limits.adoc#L685-L694)).
- **Resolve-image observation.** The test renders to a multisampled `VK_FORMAT_R8G8B8A8_UNORM` color image, resolves it to a single-sampled image, and lets the host inspect the resolved pixels. A shader commonly writes green for a local comparison success and red for a mismatch.

## Registration Hierarchy

```text
pipeline.monolithic.multisample_interpolation
├── sample_interpolate_at_single_sample
├── sample_interpolate_at_distinct_values
├── sample_interpolate_at_ignores_centroid
├── sample_interpolation_consistency
├── sample_qualifier_distinct_values
├── centroid_interpolation_consistency
├── reinterpolation_consistency                 (monolithic Vulkan only)
├── nonuniform_interpolant_indexing             (monolithic Vulkan only)
├── centroid_qualifier_inside_primitive
├── offset_interpolate_at_pixel_center
└── offset_interpolation_at_sample_position
```

The tree shows the concrete monolithic registration. [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L161) also attaches this test family under every other supported pipeline construction root. The Vulkan default mustpass files contain 1,699 leaves for `.multisample_interpolation.`: 247 in the monolithic list and 242 in each of the six non-monolithic lists (`pipeline-library`, `fast-linked-library`, the linked and unlinked SPIR-V shader-object lists, and the linked and unlinked binary shader-object lists). The five extra monolithic leaves are the two `reinterpolation_consistency` and three `nonuniform_interpolant_indexing` Amber cases. Those groups are excluded by `CTS_USES_VULKANSC` and are not registered for non-monolithic construction because Amber does not support `PipelineConstructionType`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image size | `128_128_1`, `137_191_1` | Exercises the same interpolation rule on square and non-square render targets. | [`imageSizes`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1151-L1156) |
| Sample count | `samples_1` for the single-sample behavior; `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, `samples_64` elsewhere | Changes the multisample layout and the number of sample locations examined. | [`imageSamples`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1158-L1163) |
| Component selection | `all_components`, `component_0`, `component_1`, `pushc_component_0`, `pushc_component_1` | Checks whole vectors, constant component indexing, and push-constant-selected dynamic indexing. | [`sample_interpolation_consistency`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1194-L1211), [`centroid_interpolation_consistency`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1217-L1235), [`offset_interpolation_at_sample_position`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1275-L1292) |
| Pipeline construction type | Supported construction variants | Repeats the C++ cases through the pipeline registration framework. | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L100-L161) |

## Behavior Parameters

The primary behavioral axis is the direct test-family child. Each value selects a distinct interpolation rule or equivalence relation.

### `sample_interpolate_at_single_sample` - single-sample location

Uses `interpolateAtSample` with a single-sampled target and expects a screen-position varying near the pixel center. It checks that the explicit operation has the required single-sample interpretation.

### `sample_interpolate_at_distinct_values` - sample-selected distinction

Interpolates a varying at `gl_SampleID` over a full-screen triangle. A nonlinear color boundary makes different sample locations observable as at least `numSamples + 1` resolved colors.

### `sample_interpolate_at_ignores_centroid` - explicit sample overrides centroid

Calls `interpolateAtSample` on centroid-qualified and ordinary versions of the same varying with the same `gl_SampleID`. The generated shader expects equal values, so the explicit sample location must control the result.

### `sample_interpolation_consistency` - explicit sample matches a `sample` varying

Compares a centroid-qualified varying re-interpolated at `gl_SampleID` with a `sample`-qualified varying. Component variants select all components, a constant index, or a push-constant index.

### `sample_qualifier_distinct_values` - `sample` qualifier distinction

Uses a `sample`-qualified varying with the same nonlinear boundary used by the explicit-sample distinct-value case. It checks that the qualifier supplies per-sample values rather than one shared fragment value.

### `centroid_interpolation_consistency` - explicit centroid matches a centroid varying

Compares `interpolateAtCentroid` on a sample-qualified input with the centroid-qualified input. The array setup deliberately puts different sentinel values in the two inputs at array index `0` and the actual coordinates at index `1`; the shader accesses index `1` before optionally selecting a vector component.

### `reinterpolation_consistency` - Amber re-interpolation

Registers Amber cases for `interpolate_at_centroid` and `interpolate_at_sample` only in the monolithic path. These cases require `sampleRateShading` and are absent when `CTS_USES_VULKANSC` is defined.

### `nonuniform_interpolant_indexing` - Amber indexed interpolants

Registers Amber `centroid`, `sample`, and `offset` cases for monolithic construction. They extend the family to dynamically selected interpolants without changing the shared feature requirement.

### `centroid_qualifier_inside_primitive` - centroid placement

Interpolates triangle barycentric coordinates through a centroid-qualified input. The fragment shader requires every coordinate to remain in `[0, 1]`, which detects a centroid location outside the primitive.

### `offset_interpolate_at_pixel_center` - zero offset

Checks that `interpolateAtOffset(..., vec2(0.0))` agrees with the pixel-center position, then tests a generated screen-space offset against that center reference.

### `offset_interpolation_at_sample_position` - sample-position offset

Computes `gl_SamplePosition - vec2(0.5, 0.5)` and uses it as the explicit interpolation offset. The result must agree with the corresponding `sample`-qualified varying.

## Shader Analysis

The source generates a small vertex and fragment shader for each C++ `MSCase` specialization. Shader code is central to the test, but this broad family has many generated specializations rather than one stable shader artifact. The representative mechanism is the `sample_interpolation_consistency` fragment shader: it compares `interpolateAtSample(fs_in_pos_screen_centroid, gl_SampleID)` with `fs_in_pos_screen_sample`, applies a case-local threshold, and writes green or red ([source](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L631-L684)). The host observes that color after resolve.

## Runtime Execution and Result Checking

- The generated C++ cases check graphics-pipeline-library support and validate both multisampled and resolve-image capabilities for `VK_FORMAT_R8G8B8A8_UNORM`. Most use the common support path, which also requires `sampleRateShading` and, for `VK_KHR_portability_subset`, `shaderSampleRateInterpolationFunctions` ([source](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L112-L155)). `sample_qualifier_distinct_values` has a specialized support check that still requires `sampleRateShading`, while `centroid_qualifier_inside_primitive` has a specialized check that requires neither feature because it uses only a centroid-qualified input ([source](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L296-L302), [source](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1131-L1136)).
- Each selected case constructs its shaders and draws a triangle to a multisampled color attachment. The base framework resolves the result to a single-sampled image before the case-specific verifier runs.
- Screen-position and barycentric cases use [`checkForError()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L77-L91) to scan the configured error component for a nonzero pixel. Their shaders encode mismatches as red.
- The two distinct-value cases use [`MSInstanceDistinctValues::verifyImageData()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L217-L238), which collects unique resolved pixel values and requires at least `numSamples + 1` colors.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sample_interpolate_at_single_sample` | Incorrect single-sample interpolation location. |
| `sample_interpolate_at_distinct_values`, `sample_qualifier_distinct_values` | Sample-specific interpolation does not produce the required distinct values. |
| `sample_interpolate_at_ignores_centroid`, `sample_interpolation_consistency` | `interpolateAtSample` disagrees with the requested sample location or incorrectly retains centroid selection. |
| `centroid_interpolation_consistency`, `centroid_qualifier_inside_primitive` | Centroid interpolation disagrees with the centroid-qualified value or selects a location outside the primitive. |
| `reinterpolation_consistency`, `nonuniform_interpolant_indexing` | Re-interpolation or dynamically indexed interpolant behavior is incorrect. |
| `offset_interpolate_at_pixel_center`, `offset_interpolation_at_sample_position` | Offset interpolation does not match the pixel center or the selected sample position. |

### Cause Analysis

#### Incorrect interpolation-location selection

**Possible failure symptoms:** A screen-position comparison writes red, and the resolved-image scan finds a nonzero error component. The single-sample, centroid-override, consistency, and offset behaviors can expose this symptom.

**Possible implementation causes:** The fragment stage may select the wrong evaluation location for an explicit interpolation instruction, or fail to apply the requested sample ID or offset. The source isolates these relations by comparing differently declared inputs that should name the same location. Source-level investigation is needed to localize a failure beyond the observed operation class.

#### Missing per-sample variation

**Possible failure symptoms:** The distinct-value verifier observes fewer than `numSamples + 1` unique colors in the resolved output.

**Possible implementation causes:** Sample-qualified inputs or `interpolateAtSample` may be evaluated as a shared fragment value, or the per-sample values may be incorrectly collapsed before color output. The verifier classifies the final image only, so it cannot distinguish those paths by itself.

#### Incorrect centroid placement

**Possible failure symptoms:** The barycentric centroid shader writes red because an interpolated coordinate is below `0` or above `1`, or the explicit centroid comparison fails.

**Possible implementation causes:** Centroid interpolation may choose an invalid location relative to the covered primitive, or the explicit centroid operation may disagree with the centroid qualifier. The barycentric case specifically tests the geometric inside-primitive consequence.

#### Re-interpolation or indexing failure

**Possible failure symptoms:** An Amber case in `reinterpolation_consistency` or `nonuniform_interpolant_indexing` fails.

**Possible implementation causes:** The implementation may handle a re-interpolation function or a dynamically indexed interpolant incorrectly. These monolithic-only Amber cases have separate artifacts, so their result alone does not identify a generated C++ shader path.

## Case Pruning

### Requirement-based pruning

- All generated C++ cases require suitable multisampled and resolve-image support. All except `centroid_qualifier_inside_primitive` require `sampleRateShading`.
- On an implementation exposing `VK_KHR_portability_subset`, cases using the common support path stop as unsupported when `shaderSampleRateInterpolationFunctions` is unavailable. The specialized `sample_qualifier_distinct_values` and `centroid_qualifier_inside_primitive` support checks do not test that portability-subset feature.
- The `reinterpolation_consistency`, `nonuniform_interpolant_indexing`, and `centroid_qualifier_inside_primitive` registrations are excluded by `CTS_USES_VULKANSC`; the first two also exist only for monolithic construction.

### Design-based pruning

- The compact registration tree uses a construction-type placeholder and shows the union of direct children. The two Amber groups exist only under the monolithic Vulkan root; the large image-size, sample-count, and component matrices remain in the parameter table rather than expanding the tree.
- Generated shaders use local green/red comparisons where a direct numerical reference can be expressed in the fragment stage. Distinct-value cases instead use host-side color counting because their expected outcome is a population of different values.

## Key Takeaways

- `multisample_interpolation` tests explicit sample, centroid, and offset interpolation alongside `sample` and `centroid` qualifiers.
- Its direct test-family children are the behavioral axis; sizes, sample counts, component selectors, and construction roots extend coverage.
- Device-side comparisons become observable resolved pixels, which CTS validates with either an error-color scan or distinct-color count.
- Feature and portability checks prevent unsupported interpolation-function paths from being treated as failures.

## Source Reference Appendix

| Subject | Source reference |
|---------|------------------|
| Test-family registration and matrix creation | [`createMultisampleInterpolationTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1146-L1294) |
| Family attachment under pipeline variants | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L100-L161) |
| Common image and feature checks | [`MSCase::checkImagesSupport()` and `MSCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L112-L155) |
| Error-pixel scan | [`checkForError()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L77-L91) |
| Distinct-color validation | [`MSInstanceDistinctValues::verifyImageData()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L217-L238) |
| Vulkan feature contract | [`sampleRateShading`](../../../../vulkan-docs/src/chapters/features.adoc#L258-L265) |
| Portability-subset interpolation functions | [`shaderSampleRateInterpolationFunctions`](../../../../vulkan-docs/src/chapters/features.adoc#L5411-L5419) |
| Offset limits | [`minInterpolationOffset`, `maxInterpolationOffset`, and `subPixelInterpolationOffsetBits`](../../../../vulkan-docs/src/chapters/limits.adoc#L685-L694) |
