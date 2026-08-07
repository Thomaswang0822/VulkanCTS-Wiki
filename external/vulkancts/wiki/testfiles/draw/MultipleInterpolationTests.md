## Overview

**Core question:** Can one fragment shader receive several differently decorated inputs and preserve the result of each interpolation rule independently?

- This page covers the `multiple_interpolation` test family implemented by `vktDrawMultipleInterpolationTests.cpp`.
- The test generates a shader that carries the same vertex color through `smooth`, `flat`, `noperspective`, `centroid`, and, when enabled, `sample` inputs. A fragment-stage push constant selects one input per draw.
- Each selected result is compared with a separately rendered program that declares only that qualifier. The test also checks which results may coincide and which must remain distinguishable.

## Background Knowledge

- Fragment inputs normally use perspective-correct interpolation. `noperspective` uses linear interpolation, while `flat` takes the provoking vertex value instead of interpolating it.
- `centroid` constrains the interpolation position to covered primitive area. `sample` uses the position of the sample being shaded. These constraints matter most around partially covered pixels in multisampled rendering.
- An interface block can carry stage inputs and outputs as members. The structured variant applies interpolation decorations to those members rather than to standalone variables.

## Registration Hierarchy

```text
draw.renderpass.multiple_interpolation
├── separate
└── structured
```

Each test family contains the `no_sample_decoration` and `with_sample_decoration` intermediate nodes, which each generate the seven sample-count test case leaves. The same implementation is registered under the draw category's dynamic-rendering command-buffer paths in the default Vulkan mustpass list; Vulkan SC lists the render-pass path.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interface representation | `separate`, `structured` | Places interpolation decorations on standalone interface variables or interface-block members. | [shader generation](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L151-L293) |
| Included decorations | `no_sample_decoration`, `with_sample_decoration` | Selects four qualifiers or all five, and determines whether `sampleRateShading` is required. | [support checks and registration](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L295-L305) [createTests](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L831-L895) |
| Sample-count test case leaf | `1_sample`, `2_samples`, `4_samples`, `8_samples`, `16_samples`, `32_samples`, `64_samples` | Controls whether multisample positions can expose differences between interpolation rules. | [createTests](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L831-L895) |
| Selected result | `smooth`, `flat`, `noperspective`, `centroid`, `sample` | The fragment push constant selects one multi-program input for an image result and reference comparison. | [generated fragment shader](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L199-L230) |

## Behavior Parameters

The primary behavioral axes are the interface representation and the decoration set. Sample count changes the observation conditions, but it does not change the shader-interface property under test.

### separate: Decorated standalone variables

The vertex and fragment shaders declare one independently located variable for each active qualifier. This tests separate interface variables and their decoration/location matching while the fragment shader selects among their values.

### structured: Decorated interface-block members

The same values occupy members of `InterfaceBlock`, accessed through `ifb.`. The generated shaders require `GL_ARB_enhanced_layouts`, and this variant checks decoration placement on block members rather than plain interface IDs.

### no_sample_decoration: Four interpolation rules

This set contains `smooth`, `flat`, `noperspective`, and `centroid`. It avoids the `sampleRateShading` feature requirement while retaining comparison and distinctness checks for the other rules.

### with_sample_decoration: Adds sample interpolation

This set adds the `sample` input at location 4 and creates a sample-qualified reference program. The source requires `sampleRateShading` before running this configuration.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.multiple_interpolation.separate.with_sample_decoration.4_samples
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `separate` | The five inputs are standalone variables, so their SPIR-V interpolation decorations apply to input variables. |
| `with_sample_decoration` | Includes the sample-qualified fifth input and enables the sample interpolation path. |
| `4_samples` | Uses multisampling, where centroid and sample position constraints can affect the resolved image. |

#### Purpose

This fragment shader selects one of the five independently decorated inputs. It provides the multi-interpolation image that the test compares to a matching single-qualifier reference image.

#### Structural Design

| Element | Role |
|---------|------|
| Locations 0-4 | Carry the same vertex-color value through five interpolation modes. |
| `PushConstants.interpolationIndex` | Chooses the active input without changing the shader interface. |
| `in_colors` | Places the inputs in qualifier order so the pushed integer selects the corresponding result. |
| `out_color` | Produces the image read back for comparison. |

#### Shader Code

```glsl
#version 430

/// Each input receives the vertex color through one independently decorated interface location.
layout(location = 0) in vec4 in_color_smooth;
layout(location = 1) flat in vec4 in_color_flat;
layout(location = 2) noperspective in vec4 in_color_noperspective;
layout(location = 3) centroid in vec4 in_color_centroid;
layout(location = 4) sample in vec4 in_color_sample;

/// The host pushes an interpolation enum value before each draw to select the result image.
layout(push_constant, std430) uniform PushConstants {
    uint interpolationIndex;
} pc;

layout(location=0) out vec4 out_color;

void main()
{
    const vec4 in_colors[5] = vec4[](
        in_color_smooth,
        in_color_flat,
        in_color_noperspective,
        in_color_centroid,
        in_color_sample
    );
    out_color = in_colors[pc.interpolationIndex];
}
```

#### Additional Info

- `initPrograms` emits this program as `frag_multi`; it emits separate single-input fragment programs as the comparison references.
- The structured variant retains the same input order and selection logic, but declares the inputs as `InterfaceBlock` members and accesses them through `ifb.`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Interface representation | `structured` wraps the declarations in `InterfaceBlock`, adds `ifb.` accesses, and requires `GL_ARB_enhanced_layouts`. | [generator branches](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L151-L193) |
| Included decorations | `no_sample_decoration` omits location 4, the sample input, and its reference programs. | [generator branches](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L197-L292) |
| Selected result | The pushed index changes the array element written to `out_color`; it does not change the declarations. | [generated fragment shader](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L199-L230) |

#### SPIR-V

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
; Bound: 38
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %in_color_smooth %in_color_flat %in_color_noperspective %in_color_centroid %in_color_sample %out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 430
               OpName %main "main"
               OpName %in_colors "in_colors"
               OpName %in_color_smooth "in_color_smooth"
               OpName %in_color_flat "in_color_flat"
               OpName %in_color_noperspective "in_color_noperspective"
               OpName %in_color_centroid "in_color_centroid"
               OpName %in_color_sample "in_color_sample"
               OpName %out_color "out_color"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "interpolationIndex"
               OpName %pc "pc"
               OpDecorate %in_color_smooth Location 0
               OpDecorate %in_color_flat Flat
               OpDecorate %in_color_flat Location 1
               OpDecorate %in_color_noperspective NoPerspective
               OpDecorate %in_color_noperspective Location 2
               OpDecorate %in_color_centroid Centroid
               OpDecorate %in_color_centroid Location 3
               OpDecorate %in_color_sample Sample
               OpDecorate %in_color_sample Location 4
               OpDecorate %out_color Location 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_5 = OpConstant %uint 5
%_arr_v4float_uint_5 = OpTypeArray %v4float %uint_5
%_ptr_Function__arr_v4float_uint_5 = OpTypePointer Function %_arr_v4float_uint_5
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_color_smooth = OpVariable %_ptr_Input_v4float Input
%in_color_flat = OpVariable %_ptr_Input_v4float Input
%in_color_noperspective = OpVariable %_ptr_Input_v4float Input
%in_color_centroid = OpVariable %_ptr_Input_v4float Input
%in_color_sample = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%PushConstants = OpTypeStruct %uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Function_v4float = OpTypePointer Function %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
  %in_colors = OpVariable %_ptr_Function__arr_v4float_uint_5 Function
         %15 = OpLoad %v4float %in_color_smooth
         %17 = OpLoad %v4float %in_color_flat
         %19 = OpLoad %v4float %in_color_noperspective
         %21 = OpLoad %v4float %in_color_centroid
         %23 = OpLoad %v4float %in_color_sample
         %24 = OpCompositeConstruct %_arr_v4float_uint_5 %15 %17 %19 %21 %23
               OpStore %in_colors %24
         %33 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %34 = OpLoad %uint %33
         %36 = OpAccessChain %_ptr_Function_v4float %in_colors %34
         %37 = OpLoad %v4float %36
               OpStore %out_color %37
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a 128 × 128 `VK_FORMAT_R8G8B8A8_UNORM` color target. Multisample leaves also create a multisample attachment that resolves into the single-sample target.
- The vertex buffer supplies three position/color pairs. Its nonuniform positions and colors make the interpolation choices visible.
- For every active qualifier, `iterate` renders the multi-input program with that qualifier's integer index. It then renders a single-qualifier reference for every active qualifier. `with_sample_decoration` also produces references with sample-rate shading enabled.
- The draw uses a legacy render pass unless shared draw parameters select dynamic rendering. Dynamic rendering performs its image transitions before beginning rendering; secondary command-buffer modes record and execute the same draw sequence through the selected command-buffer arrangement.
- The host reads each result image and compares every pixel channel to its reference with threshold 1.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `separate` | Incorrect independent interpolation decoration, location matching, generated multi-program selection, or image comparison for standalone variables. |
| `structured` | Incorrect interpolation decoration handling on interface-block members, block member matching, or the same shared rendering and checking path. |
| `no_sample_decoration` | Incorrect handling of `smooth`, `flat`, `noperspective`, or `centroid`, including the non-multisample equivalence rule. |
| `with_sample_decoration` | Incorrect `sample` interpolation or sample-rate-shading handling, or missing `sampleRateShading` feature gating. |

### Cause Analysis

#### Interpolation decoration or interface matching

**Possible failure symptoms:** A selected multi-input result differs from its same-qualifier reference by more than the per-channel threshold, or an impermissible pair of outputs compares equal.

**Possible implementation causes:** The shader compiler or pipeline interface may apply a decoration to the wrong location, fail to preserve `Flat`, `NoPerspective`, `Centroid`, or `Sample`, or mismatch matching interface variables. For `structured`, the relevant risk is incorrect member-level decoration or member matching. Vulkan defines these interpolation rules for fragment inputs in [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2949).

#### Sample-position or sample-rate-shading handling

**Possible failure symptoms:** A `with_sample_decoration` result matches neither its ordinary single-qualifier reference nor its sample-rate-shading reference, or the test runs without the required feature.

**Possible implementation causes:** The implementation may use an incorrect sample position for a sample-qualified input, compile sample-qualified interpolation incorrectly, or expose `sampleRateShading` inconsistently with pipeline sample-shading behavior.

#### Rendering and comparison path

**Possible failure symptoms:** Several qualifier rows fail together, including rows whose shaders have different decorations, or read-back comparison reports a mismatch unrelated to a particular qualifier.

**Possible implementation causes:** Source inspection would be needed to distinguish shared attachment creation, resolve, dynamic-rendering/secondary-command-buffer recording, readback, or comparison defects from interpolation defects.

## Case Pruning

### Requirement-based pruning

- A leaf is skipped when its selected count is absent from `framebufferColorSampleCounts`.
- `with_sample_decoration` is skipped without `sampleRateShading`.
- Dynamic-rendering execution requires `VK_KHR_dynamic_rendering`.

### Design-based pruning

- `no_sample_decoration` omits the `sample` shader input and reference programs because that test set intentionally avoids the feature dependency.
- The result-comparison loop excludes the sample slot for this four-qualifier set.
- The test does not require every pair of interpolation images to differ. It explicitly permits `smooth`, `centroid`, and `sample` pairs where the source's stated rules allow equality; without multisampling it requires those three results to be equal.

## Key Takeaways

- The test compares one multi-decorated interface against independent single-decorated references, which isolates whether qualifier coexistence changes an input's result.
- `separate` and `structured` cover two SPIR-V interface representations for the same interpolation behavior.
- MSAA exposes constrained interpolation positions, while the validation logic preserves the permitted `smooth`/`centroid`/`sample` equivalences.
- The `sample` path adds both a feature gate and a sample-rate-shading reference, rather than assuming a single rendering schedule.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shader generation | [DrawTestCase::initPrograms](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L151-L293) | Emits multi-input and single-input GLSL programs for both interface representations. |
| Support checks | [DrawTestCase::checkSupport](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L295-L305) | Checks sample counts, `sampleRateShading`, and dynamic rendering. |
| Rendering setup and draw recording | [DrawTestInstance::render](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L312-L624) | Creates images, pipeline state, command buffers, draws, and reads back output. |
| Validation | [compare and iterate](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L626-L829) | Implements per-channel comparison plus same/different-result rules. |
| Test matrix registration | [createTests and createMultipleInterpolationTests](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L831-L903) | Registers interface, decoration, and sample-count paths. |
| Parent draw registration | [createChildren](../../../modules/vulkan/draw/vktDrawTests.cpp#L65-L115) | Attaches `multiple_interpolation` to each applicable draw configuration. |
| Default Vulkan mustpass entries | [draw.txt](../../../mustpass/main/vk-default/draw.txt#L1946-L1973) | Shows the dynamic-rendering complete-secondary scope; the file also contains primary, partial-secondary, and render-pass entries. |
| Vulkan SC mustpass entries | [draw.txt](../../../mustpass/main/vksc-default/draw.txt#L1476-L1503) | Shows the render-pass Vulkan SC scope. |
| Vulkan interpolation semantics | [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2949) | Defines qualifier behavior and interpolation-position constraints. |
