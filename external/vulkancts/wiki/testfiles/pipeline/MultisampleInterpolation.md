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

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.multisample_interpolation.centroid_interpolation_consistency.all_components.128_128_1.samples_16
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `centroid_interpolation_consistency` | Compares an explicitly centroid-interpolated value with a centroid-qualified varying at the same pixel. |
| `all_components`, `128_128_1`, `samples_16` | Uses the full `vec2` screen-position varying on a 128×128×1 image with 16 samples; no component selector or push constant changes the generated path. |
| `shader_object_linked_binary` | Runs the same generated vertex/fragment shader logic through the linked-binary shader-object pipeline construction. |

#### Purpose

The fragment shader checks that `interpolateAtCentroid` applied to a sample-qualified input produces the same screen-space value as a centroid-qualified input. A green output means the two vectors agree within the source threshold; red is the failure signal observed after resolving the multisampled color image.

#### Structural Design

| Phase | Dataflow |
|-------|----------|
| Vertex transport | Read NDC position plus screen position; write `gl_Position` and copy the screen position to both location-0 and location-2 outputs. |
| Fragment interpolation | Receive location 0 as `sample` and location 2 as `centroid`; explicitly re-interpolate the sample-qualified input at the centroid. |
| Validation output | Compare both `vec2` values componentwise with threshold `0.0005`; write green on equality and red otherwise. |

#### Shader Code

##### Vertex Shader

```glsl
#version 440
layout(location = 0) in vec4 vs_in_position_ndc;
layout(location = 1) in vec2 vs_in_position_screen;

layout(location = 0) out vec2 vs_out_pos_screen_sample[2];
layout(location = 2) out vec2 vs_out_pos_screen_centroid[2];

out gl_PerVertex {
    vec4  gl_Position;
};
void main (void)
{
    gl_Position                      = vs_in_position_ndc;
    // Index 0 is never read, so we'll populate them with bad values
    vs_out_pos_screen_sample[0]      = vec2(-70.3, 42.1);
    vs_out_pos_screen_centroid[0] = vec2(7.7, -3.2);
    // Actual coordinates in index 1:
    vs_out_pos_screen_sample[1]      = vs_in_position_screen;
    vs_out_pos_screen_centroid[1] = vs_in_position_screen;
}
```

##### Fragment Shader

```glsl
#version 440
layout(location = 0) sample   in vec2 fs_in_pos_screen_sample[2];
layout(location = 2) centroid in vec2 fs_in_pos_screen_centroid[2];

layout(location = 0) out vec4 fs_out_color;

void main (void)
{
    /// The generated all-components case compares the complete two-component screen position.
    const float threshold = 0.0005;

    /// Explicit centroid evaluation of the sample-qualified input must match the centroid-qualified input.
    const vec2 pos_interpolated_at_centroid = interpolateAtCentroid(fs_in_pos_screen_sample[1]);
    const bool valuesEqual                  = all(lessThan(abs(pos_interpolated_at_centroid - fs_in_pos_screen_centroid[1]), vec2(threshold)));

    /// The resolved image carries the device-side pass/fail result: green is equal, red is a mismatch.
    if (valuesEqual)
        fs_out_color = vec4(0.0, 1.0, 0.0, 1.0);
    else
        fs_out_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The vertex stage is fixed support for this representative family: it only transports the same screen-space attribute to two output locations, while the fragment input qualifiers select the behavior under test.
- The `all_components` specialization emits the vector comparison shown above. `component_0`, `component_1`, and `pushc_component_0/1` instead emit scalar comparisons, with the last two selecting the component through a push-constant block.
- The host-side `MSInstanceInterpolateScreenPosition::verifyImageData` scans resolved component 0 and fails if any pixel contains a nonzero error component ([source](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L426-L434)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Consistency family | `sample_interpolation_consistency` uses `interpolateAtSample` against a `sample` input, whereas `centroid_interpolation_consistency` uses `interpolateAtCentroid` against a `centroid` input; the shown case is the latter. | [sample builder](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L606-L684), [centroid builder](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L725-L807) |
| Component selection | `all_components` compares `vec2`; constant component cases compare one indexed scalar; push-constant cases add `layout(push_constant) uniform PushConstants { uint component; }` and index dynamically. | [centroid component branches](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L764-L798) |
| Image size and sample count | These values change render-target dimensions and sample count, but not the generated shader source for this family. | [matrix creation](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1151-L1163), [centroid registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1217-L1235) |
| Pipeline construction | The same generated sources are attached under the supported construction roots; this case is registered in the linked-binary shader-object list. | [family attachment](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L100-L161) |

#### SPIR-V

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 41
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %vs_in_position_ndc %vs_out_pos_screen_sample %vs_out_pos_screen_centroid %vs_in_position_screen
               OpSource GLSL 440
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %vs_in_position_ndc "vs_in_position_ndc"
               OpName %vs_out_pos_screen_sample "vs_out_pos_screen_sample"
               OpName %vs_out_pos_screen_centroid "vs_out_pos_screen_centroid"
               OpName %vs_in_position_screen "vs_in_position_screen"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %vs_in_position_ndc Location 0
               OpDecorate %vs_out_pos_screen_sample Location 0
               OpDecorate %vs_out_pos_screen_centroid Location 2
               OpDecorate %vs_in_position_screen Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%vs_in_position_ndc = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v2float = OpTypeVector %float 2
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_v2float_uint_2 = OpTypeArray %v2float %uint_2
%_ptr_Output__arr_v2float_uint_2 = OpTypePointer Output %_arr_v2float_uint_2
%vs_out_pos_screen_sample = OpVariable %_ptr_Output__arr_v2float_uint_2 Output
%float_n70_3000031 = OpConstant %float -70.3000031
%float_42_0999985 = OpConstant %float 42.0999985
         %26 = OpConstantComposite %v2float %float_n70_3000031 %float_42_0999985
%_ptr_Output_v2float = OpTypePointer Output %v2float
%vs_out_pos_screen_centroid = OpVariable %_ptr_Output__arr_v2float_uint_2 Output
%float_7_69999981 = OpConstant %float 7.69999981
%float_n3_20000005 = OpConstant %float -3.20000005
         %32 = OpConstantComposite %v2float %float_7_69999981 %float_n3_20000005
      %int_1 = OpConstant %int 1
%_ptr_Input_v2float = OpTypePointer Input %v2float
%vs_in_position_screen = OpVariable %_ptr_Input_v2float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %vs_in_position_ndc
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %28 = OpAccessChain %_ptr_Output_v2float %vs_out_pos_screen_sample %int_0
               OpStore %28 %26
         %33 = OpAccessChain %_ptr_Output_v2float %vs_out_pos_screen_centroid %int_0
               OpStore %33 %32
         %37 = OpLoad %v2float %vs_in_position_screen
         %38 = OpAccessChain %_ptr_Output_v2float %vs_out_pos_screen_sample %int_1
               OpStore %38 %37
         %39 = OpLoad %v2float %vs_in_position_screen
         %40 = OpAccessChain %_ptr_Output_v2float %vs_out_pos_screen_centroid %int_1
               OpStore %40 %39
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 45
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
               OpCapability InterpolationFunction
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fs_in_pos_screen_sample %fs_in_pos_screen_centroid %fs_out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 440
               OpName %main "main"
               OpName %pos_interpolated_at_centroid "pos_interpolated_at_centroid"
               OpName %fs_in_pos_screen_sample "fs_in_pos_screen_sample"
               OpName %valuesEqual "valuesEqual"
               OpName %fs_in_pos_screen_centroid "fs_in_pos_screen_centroid"
               OpName %fs_out_color "fs_out_color"
               OpDecorate %fs_in_pos_screen_sample Sample
               OpDecorate %fs_in_pos_screen_sample Location 0
               OpDecorate %fs_in_pos_screen_centroid Centroid
               OpDecorate %fs_in_pos_screen_centroid Location 2
               OpDecorate %fs_out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_v2float_uint_2 = OpTypeArray %v2float %uint_2
%_ptr_Input__arr_v2float_uint_2 = OpTypePointer Input %_arr_v2float_uint_2
%fs_in_pos_screen_sample = OpVariable %_ptr_Input__arr_v2float_uint_2 Input
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%_ptr_Input_v2float = OpTypePointer Input %v2float
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
%fs_in_pos_screen_centroid = OpVariable %_ptr_Input__arr_v2float_uint_2 Input
%float_0_000500000024 = OpConstant %float 0.000500000024
         %30 = OpConstantComposite %v2float %float_0_000500000024 %float_0_000500000024
     %v2bool = OpTypeVector %bool 2
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%fs_out_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %42 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %44 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%pos_interpolated_at_centroid = OpVariable %_ptr_Function_v2float Function
%valuesEqual = OpVariable %_ptr_Function_bool Function
         %18 = OpAccessChain %_ptr_Input_v2float %fs_in_pos_screen_sample %int_1
         %19 = OpExtInst %v2float %1 InterpolateAtCentroid %18
               OpStore %pos_interpolated_at_centroid %19
         %23 = OpLoad %v2float %pos_interpolated_at_centroid
         %25 = OpAccessChain %_ptr_Input_v2float %fs_in_pos_screen_centroid %int_1
         %26 = OpLoad %v2float %25
         %27 = OpFSub %v2float %23 %26
         %28 = OpExtInst %v2float %1 FAbs %27
         %32 = OpFOrdLessThan %v2bool %28 %30
         %33 = OpAll %bool %32
               OpStore %valuesEqual %33
         %34 = OpLoad %bool %valuesEqual
               OpSelectionMerge %36 None
               OpBranchConditional %34 %35 %43
         %35 = OpLabel
               OpStore %fs_out_color %42
               OpBranch %36
         %43 = OpLabel
               OpStore %fs_out_color %44
               OpBranch %36
         %36 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

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
