## Overview

**Core question:** Does `VK_AMD_shader_explicit_vertex_parameter` let a fragment shader reconstruct the same interpolated value as Vulkan's standard interpolation path?

- The [`explicit_vertex_parameter`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L764-L768) test family generates smooth and noperspective cases, with no auxiliary qualifier or with `sample`/`centroid`. Render-pass and primary-command-buffer paths generate sample counts 1 through 64; secondary-command-buffer paths are pruned to 1, 2, and 4.
- The vertex shader exports one value through `__explicitInterpAMD` and a second copy through the selected ordinary interpolation qualifier. The fragment shader fetches the first copy at each primitive vertex with `interpolateAtVertexAMD`, combines those values with the matching `gl_BaryCoord*AMD` coordinates, and compares the result with the ordinary input.
- The host reads the per-fragment expected/computed pairs from a storage buffer. The family is registered below the draw category's render-pass path and, when supported, each dynamic-rendering command-buffer path.

## Background Knowledge

- **Shader-stage interfaces:** Vertex outputs and fragment inputs form a user-defined interface matched by location and compatible decorations. This test deliberately carries two separately located values so one uses explicit vertex interpolation while the other supplies the comparison value. See [Shader Input and Output Interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-iointerfaces).
- **Barycentric interpolation:** A fragment's value over a triangle can be reconstructed from the three vertex values and barycentric coordinates. Smooth coordinates account for perspective; noperspective coordinates do not. `sample` and `centroid` select different sampling locations for the ordinary interpolated input and its corresponding AMD barycentric built-in.
- **Multisampling:** `gl_SampleID` distinguishes the storage-buffer result slot for each sample. The family requires the core `sampleRateShading` feature for every case, including sample-count-1 and non-`sample` branches; the pipeline itself leaves `sampleShadingEnable` false, while the fragment shader's use of `gl_SampleID` makes sample identity observable.

## Registration Hierarchy

The dispatcher adds this test family to the render-pass path and to the three non-nested dynamic-rendering paths. Nested secondary-command-buffer variants intentionally omit this family because the dispatcher stops after the `basic` family for nested variants.

```text
draw.renderpass
└── explicit_vertex_parameter

draw.dynamic_rendering.primary_cmd_buff
└── explicit_vertex_parameter

draw.dynamic_rendering.partial_secondary_cmd_buff
└── explicit_vertex_parameter

draw.dynamic_rendering.complete_secondary_cmd_buff
└── explicit_vertex_parameter
```

Within each applicable `explicit_vertex_parameter` test family, the direct behavior branches are:

The direct behavior branches are `smooth_samples_<count>`, `noperspective_samples_<count>`, `smooth_sample_samples_<count>`, `noperspective_sample_samples_<count>`, `smooth_centroid_samples_<count>`, and `noperspective_centroid_samples_<count>`.

The family is attached by [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120), and its branches are created by [`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L727-L760).

The generated default mustpass lists confirm 38 render-pass cases and 38 primary-command-buffer cases. Each secondary-command-buffer path contains 14 cases because it retains only sample counts 1, 2, and 4. Vulkan SC has only the 38 render-pass cases. See the [`vk-default` draw list](../../../mustpass/main/vk-default/draw.txt) and [`vksc-default` draw list](../../../mustpass/main/vksc-default/draw.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Interpolation | `smooth`, `noperspective` | Selects both the ordinary comparison qualifier and the matching AMD barycentric coordinate family. | [`Interpolation`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L62-L66), [`getTestName()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L166-L177) |
| Auxiliary qualifier | none, `sample`, `centroid` | Changes the sampling rule for the ordinary input and selects `gl_BaryCoord*SampleAMD` or `gl_BaryCoord*CentroidAMD`. | [`AuxiliaryQualifier`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L68-L73), [`barycentricVariableString()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L115-L146) |
| Sample count | Render pass/primary: `1`, `2`, `4`, `8`, `16`, `32`, `64`; secondary: `1`, `2`, `4` | Controls multisample attachments and the number of result values per pixel. | [`samples[]` and secondary pruning](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L731-L748) |
| Rendering path | `renderpass`; dynamic rendering `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Reuses the same interpolation matrix with different rendering and command-buffer recording. | [`createTests()` dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |
| Render target | 16 × 16 pixels, `VK_FORMAT_R8G8B8A8_UNORM` | Bounds the color target and storage-buffer indexing workload. | [`WIDTH`/`HEIGHT`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L75-L79), image creation [`#L356-L379`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L356-L379) |

## Behavior Parameters

The primary behavioral axis is the interpolation/auxiliary branch. Sample count is an orthogonal coverage dimension and is explained in the matrix above.

### `smooth`: perspective-correct reconstruction

The ordinary input uses `smooth`; the explicit path uses `gl_BaryCoordSmoothAMD`, `gl_BaryCoordSmoothSampleAMD`, or `gl_BaryCoordSmoothCentroidAMD`. The fragment shader's weighted sum must agree with standard perspective-correct interpolation.

### `noperspective`: screen-space reconstruction

The ordinary input uses `noperspective`; the explicit path uses the matching `gl_BaryCoordNoPersp*AMD` built-in. Agreement here checks that the explicit coordinates and vertex fetch follow the non-perspective interpolation rule.

### `sample` and `centroid`: auxiliary sampling

These branches apply the auxiliary qualifier to the ordinary input and use the corresponding AMD barycentric variable. They are only registered for sample counts at least 2, where the qualifier can distinguish sampling behavior.

## Shader Analysis

[`DrawTestCase::initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331) generates both shader stages from the interpolation mode, auxiliary qualifier, and sample count. The fragment stage is primary because it performs the explicit per-vertex fetch, barycentric reconstruction, and comparison; the vertex stage is included because its two output paths establish the values being compared.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.explicit_vertex_parameter.smooth_sample_samples_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass` | Uses the legacy render-pass path; the rendering path does not alter either generated shader. |
| `smooth` | Selects perspective-correct ordinary interpolation and `gl_BaryCoordSmoothSampleAMD`. |
| `sample` | Applies sample interpolation to the ordinary interface value and selects sample-position barycentric coordinates. |
| `samples_4` | Uses four samples per pixel, makes `gl_SampleID` observable, and sizes the shader-declared result array to 4096 `vec4` elements. |

#### Purpose

The shaders compare ordinary sample-qualified smooth interpolation with an explicit reconstruction from all three primitive-vertex values and matching AMD barycentric coordinates. Each fragment invocation stores both results for the host verdict.

#### Structural Design

| Phase | Operation | Observable result |
|-------|-----------|-------------------|
| Vertex export | Write `in_data` to location 0 with `__explicitInterpAMD` and to sample-qualified smooth location 1. | The same source value reaches two independently decorated fragment inputs. |
| Explicit fetch | Fetch location 0 at primitive vertices 0, 1, and 2 with `interpolateAtVertexAMD`. | `data0`, `data1`, and `data2` contain the original per-vertex values. |
| Reconstruction | Reorder the fetched values to match `(I, J, K)` and apply `gl_BaryCoordSmoothSampleAMD`. | `res` reconstructs the sample-position smooth value. |
| Comparison | Store `(expected, res)` in the sample-specific SSBO slot and compare with `0.0005`. | Host readback supplies the effective verdict; green/red attachment output is diagnostic only. |

#### Shader Code

##### Fragment Shader

```glsl
#version 450
#extension GL_AMD_shader_explicit_vertex_parameter : require

/// Location 0 retains primitive-vertex values for explicit AMD interpolation.
layout(location = 0) __explicitInterpAMD in float in_data_explicit;
/// Location 1 supplies the implementation's ordinary sample-position smooth result.
layout(location = 1) sample smooth        in float in_data_smooth;
/// Diagnostic color: green below the shader threshold, red otherwise.
layout(location = 0) out vec4 out_color;
/// Set 0, binding 0 is a host-visible storage buffer; this case declares 256 * 4 * 4 entries.
layout (binding = 0, std140) writeonly buffer Output {
    vec4 values [4096];
} sb_out;

void main()
{
    /// Select one result slot for this pixel and sample.
    uint index = (uint(gl_FragCoord.y) * 16 * 4) + uint(gl_FragCoord.x) * 4 + gl_SampleID;
    // Barycentric coodinates (I, J, K)
    /// The built-in exposes I and J; K is reconstructed so the three weights sum to one.
    vec3 bary_coord = vec3(gl_BaryCoordSmoothSampleAMD.x, gl_BaryCoordSmoothSampleAMD.y, 1.0f - gl_BaryCoordSmoothSampleAMD.x - gl_BaryCoordSmoothSampleAMD.y);

    // Vertex 0 -> (I = 0, J = 0, K = 1)
    float data0 = interpolateAtVertexAMD(in_data_explicit, 0);
    // Vertex 1 -> (I = 1, J = 0, K = 0)
    float data1 = interpolateAtVertexAMD(in_data_explicit, 1);
    // Vertex 1 -> (I = 0, J = 1, K = 0)
    float data2 = interpolateAtVertexAMD(in_data_explicit, 2);
    // Match data component with barycentric coordinate
    vec3  data  = vec3(data1, data2, data0);

    /// Reconstruct the explicit value and retain the ordinary value as the reference.
    float res      = (bary_coord.x * data.x) + (bary_coord.y * data.y) + (bary_coord.z * data.z);
    float expected = in_data_smooth;

    /// Host verification reads only the first two components.
    sb_out.values[ index ] = vec4(expected, res, 0u, 0u);

    const float threshold = 0.0005f;
    if (abs(res - expected) < threshold)
        out_color = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    else
        out_color = vec4(1.0f, 0.0f, 0.0f, 1.0f);
}
```

##### Vertex Shader

```glsl
#version 450
#extension GL_AMD_shader_explicit_vertex_parameter : require

/// Host vertex attributes contain clip-space position and the scalar interpolation payload.
layout(location = 0) in vec4 in_position;
layout(location = 1) in float in_data;
/// The explicit path preserves access to each primitive vertex's scalar value.
layout(location = 0) __explicitInterpAMD out float out_data_explicit;
/// The comparison path requests ordinary sample-position smooth interpolation.
layout(location = 1) sample smooth        out float out_data_smooth;

out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
};

void main() {
    gl_PointSize              = 1.0;
    gl_Position               = in_position;
    /// Export the same scalar through both interface paths.
    out_data_explicit         = in_data;
    out_data_smooth     = in_data;
}
```

#### Additional Info

- The vertex shader keeps the same assignments across the family; only the ordinary output's interpolation/auxiliary qualifiers and generated name vary. It is required here because it proves that both fragment inputs originate from the same per-vertex scalar.
- For this case, `numValues` is `16 * 16 * 4 = 1024`, but template substitution declares `numValues * samples = 4096` entries. The host allocates and the shader indexes only the first 1024 entries ([shader specialization](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L327), [buffer allocation](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L451-L460)).
- The source-generated comment before `data2` says “Vertex 1”; the call uses vertex index 2 and the documented `(I = 0, J = 1, K = 0)` mapping. The walkthrough preserves that source comment verbatim.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Interpolation | `noperspective` renames the ordinary interface variables, applies `noperspective`, and replaces the barycentric built-in with the corresponding `gl_BaryCoordNoPersp*AMD` form. | [`interpolationToString()` and `barycentricVariableString()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L100-L147) |
| Auxiliary qualifier | No qualifier selects the base barycentric built-in; `centroid` replaces `sample` on both ordinary interfaces and selects the `*CentroidAMD` built-in. | [`auxiliaryQualifierToString()` and `barycentricVariableString()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L115-L161) |
| Sample count | Substitutes the stride in the SSBO index and both factors in the declared result-array length; it does not change the interpolation algorithm. | [`initPrograms()` substitutions](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L327) |
| Rendering path | Render-pass and dynamic-rendering variants compile the same shader templates; the parameter is consumed only by host setup and command recording. | [`DrawParams` and `initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L92-L98), [`iterate()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L338-L627) |

#### SPIR-V

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
; Bound: 115
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
               OpExtension "SPV_AMD_shader_explicit_vertex_parameter"
          %1 = OpExtInstImport "GLSL.std.450"
         %55 = OpExtInstImport "SPV_AMD_shader_explicit_vertex_parameter"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_SampleID %gl_BaryCoordSmoothSampleAMD %in_data_explicit %in_data_smooth %out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_AMD_shader_explicit_vertex_parameter"
               OpName %main "main"
               OpName %index "index"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %gl_SampleID "gl_SampleID"
               OpName %bary_coord "bary_coord"
               OpName %gl_BaryCoordSmoothSampleAMD "gl_BaryCoordSmoothSampleAMD"
               OpName %data0 "data0"
               OpName %in_data_explicit "in_data_explicit"
               OpName %data1 "data1"
               OpName %data2 "data2"
               OpName %data "data"
               OpName %res "res"
               OpName %expected "expected"
               OpName %in_data_smooth "in_data_smooth"
               OpName %Output "Output"
               OpMemberName %Output 0 "values"
               OpName %sb_out "sb_out"
               OpName %out_color "out_color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %gl_SampleID BuiltIn SampleId
               OpDecorate %gl_SampleID Flat
               OpDecorate %gl_BaryCoordSmoothSampleAMD BuiltIn BaryCoordSmoothSampleAMD
               OpDecorate %in_data_explicit Location 0
               OpDecorate %in_data_explicit ExplicitInterpAMD
               OpDecorate %in_data_smooth Sample
               OpDecorate %in_data_smooth Location 1
               OpDecorate %_arr_v4float_uint_4096 ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_float = OpTypePointer Input %float
    %uint_16 = OpConstant %uint 16
     %uint_4 = OpConstant %uint 4
     %uint_0 = OpConstant %uint 0
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_SampleID = OpVariable %_ptr_Input_int Input
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
%gl_BaryCoordSmoothSampleAMD = OpVariable %_ptr_Input_v2float Input
    %float_1 = OpConstant %float 1
%_ptr_Function_float = OpTypePointer Function %float
%in_data_explicit = OpVariable %_ptr_Input_float Input
     %uint_2 = OpConstant %uint 2
%in_data_smooth = OpVariable %_ptr_Input_float Input
  %uint_4096 = OpConstant %uint 4096
%_arr_v4float_uint_4096 = OpTypeArray %v4float %uint_4096
     %Output = OpTypeStruct %_arr_v4float_uint_4096
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
      %int_0 = OpConstant %int 0
    %float_0 = OpConstant %float 0
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
%float_0_000500000024 = OpConstant %float 0.000500000024
       %bool = OpTypeBool
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
        %112 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %114 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
 %bary_coord = OpVariable %_ptr_Function_v3float Function
      %data0 = OpVariable %_ptr_Function_float Function
      %data1 = OpVariable %_ptr_Function_float Function
      %data2 = OpVariable %_ptr_Function_float Function
       %data = OpVariable %_ptr_Function_v3float Function
        %res = OpVariable %_ptr_Function_float Function
   %expected = OpVariable %_ptr_Function_float Function
         %15 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %16 = OpLoad %float %15
         %17 = OpConvertFToU %uint %16
         %19 = OpIMul %uint %17 %uint_16
         %21 = OpIMul %uint %19 %uint_4
         %23 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %24 = OpLoad %float %23
         %25 = OpConvertFToU %uint %24
         %26 = OpIMul %uint %25 %uint_4
         %27 = OpIAdd %uint %21 %26
         %31 = OpLoad %int %gl_SampleID
         %32 = OpBitcast %uint %31
         %33 = OpIAdd %uint %27 %32
               OpStore %index %33
         %40 = OpAccessChain %_ptr_Input_float %gl_BaryCoordSmoothSampleAMD %uint_0
         %41 = OpLoad %float %40
         %42 = OpAccessChain %_ptr_Input_float %gl_BaryCoordSmoothSampleAMD %uint_1
         %43 = OpLoad %float %42
         %45 = OpAccessChain %_ptr_Input_float %gl_BaryCoordSmoothSampleAMD %uint_0
         %46 = OpLoad %float %45
         %47 = OpFSub %float %float_1 %46
         %48 = OpAccessChain %_ptr_Input_float %gl_BaryCoordSmoothSampleAMD %uint_1
         %49 = OpLoad %float %48
         %50 = OpFSub %float %47 %49
         %51 = OpCompositeConstruct %v3float %41 %43 %50
               OpStore %bary_coord %51
         %56 = OpExtInst %float %55 InterpolateAtVertexAMD %in_data_explicit %uint_0
               OpStore %data0 %56
         %58 = OpExtInst %float %55 InterpolateAtVertexAMD %in_data_explicit %uint_1
               OpStore %data1 %58
         %61 = OpExtInst %float %55 InterpolateAtVertexAMD %in_data_explicit %uint_2
               OpStore %data2 %61
         %63 = OpLoad %float %data1
         %64 = OpLoad %float %data2
         %65 = OpLoad %float %data0
         %66 = OpCompositeConstruct %v3float %63 %64 %65
               OpStore %data %66
         %68 = OpAccessChain %_ptr_Function_float %bary_coord %uint_0
         %69 = OpLoad %float %68
         %70 = OpAccessChain %_ptr_Function_float %data %uint_0
         %71 = OpLoad %float %70
         %72 = OpFMul %float %69 %71
         %73 = OpAccessChain %_ptr_Function_float %bary_coord %uint_1
         %74 = OpLoad %float %73
         %75 = OpAccessChain %_ptr_Function_float %data %uint_1
         %76 = OpLoad %float %75
         %77 = OpFMul %float %74 %76
         %78 = OpFAdd %float %72 %77
         %79 = OpAccessChain %_ptr_Function_float %bary_coord %uint_2
         %80 = OpLoad %float %79
         %81 = OpAccessChain %_ptr_Function_float %data %uint_2
         %82 = OpLoad %float %81
         %83 = OpFMul %float %80 %82
         %84 = OpFAdd %float %78 %83
               OpStore %res %84
         %87 = OpLoad %float %in_data_smooth
               OpStore %expected %87
         %94 = OpLoad %uint %index
         %95 = OpLoad %float %expected
         %96 = OpLoad %float %res
         %98 = OpCompositeConstruct %v4float %95 %96 %float_0 %float_0
        %100 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_0 %94
               OpStore %100 %98
        %101 = OpLoad %float %res
        %102 = OpLoad %float %expected
        %103 = OpFSub %float %101 %102
        %104 = OpExtInst %float %1 FAbs %103
        %107 = OpFOrdLessThan %bool %104 %float_0_000500000024
               OpSelectionMerge %109 None
               OpBranchConditional %107 %108 %113
        %108 = OpLabel
               OpStore %out_color %112
               OpBranch %109
        %113 = OpLabel
               OpStore %out_color %114
               OpBranch %109
        %109 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 28
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
               OpExtension "SPV_AMD_shader_explicit_vertex_parameter"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_data_explicit %in_data %out_data_smooth
               OpSource GLSL 450
               OpSourceExtension "GL_AMD_shader_explicit_vertex_parameter"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_data_explicit "out_data_explicit"
               OpName %in_data "in_data"
               OpName %out_data_smooth "out_data_smooth"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %in_position Location 0
               OpDecorate %out_data_explicit Location 0
               OpDecorate %out_data_explicit ExplicitInterpAMD
               OpDecorate %in_data Location 1
               OpDecorate %out_data_smooth Sample
               OpDecorate %out_data_smooth Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
%out_data_explicit = OpVariable %_ptr_Output_float Output
%_ptr_Input_float = OpTypePointer Input %float
    %in_data = OpVariable %_ptr_Input_float Input
%out_data_smooth = OpVariable %_ptr_Output_float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %15 %float_1
         %19 = OpLoad %v4float %in_position
         %21 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %21 %19
         %25 = OpLoad %float %in_data
               OpStore %out_data_explicit %25
         %27 = OpLoad %float %in_data
               OpStore %out_data_smooth %27
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checking requires `VK_AMD_shader_explicit_vertex_parameter`, a supported framebuffer color sample count, and the core `sampleRateShading` feature. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering`; unsupported combinations are reported as unsupported. See [`checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L255).
- The instance creates a single-sample color image and, for multisample cases, a multisample color image plus resolve attachment. It also creates a host-visible vertex buffer and host-visible storage buffer, binds the latter at descriptor binding 0, and builds a graphics pipeline using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`.
- The command path records either a render pass or dynamic rendering. Secondary-buffer variants record the draw in a secondary command buffer and execute it from a primary buffer; the complete variant contains the dynamic-rendering scope in the secondary buffer.
- A four-vertex triangle strip is drawn into the 16 × 16 target. After `submitCommandsAndWait`, the host invalidates the storage-buffer allocation and checks every `WIDTH * HEIGHT * samples` entry. Any `abs(expected - computed) > 0.0005` changes the result to fail. See [`iterate()` readback](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L606-L627).

### Verdict limitations visible in the source

- The SSBO is initialized to zero, and an untouched entry therefore contains `(expected, computed) = (0, 0)` and passes. The check detects disagreement in shader-written entries, but by itself does not prove that every intended pixel/sample invocation wrote an entry.
- The host uses `> 0.0005`, whereas the shader color uses `< 0.0005`; a difference exactly equal to the threshold passes host verification but produces red. Because the color attachment is not read back, the host rule is the effective pass/fail rule.
- A NaN in either stored component also does not satisfy the host's `> 0.0005` condition under ordinary floating-point comparison. Thus the readback predicate is specifically a finite-difference check, not a comprehensive validation of stored numeric values.
- The fragment block is declared with `WIDTH * HEIGHT * samples * samples` elements because the already sample-scaled `numValues` is multiplied by `samples` again during template substitution ([shader specialization](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L327)). The backing buffer and all actual indices use only `WIDTH * HEIGHT * samples`; the extra declared range is not accessed by this shader.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `smooth` | Incorrect smooth AMD barycentric coordinates, explicit vertex fetch, perspective handling, or ordinary interface interpolation. |
| `noperspective` | Incorrect non-perspective AMD barycentric coordinates, explicit vertex fetch, or ordinary interface interpolation. |
| `sample` | Incorrect sample-qualified interpolation/barycentric behavior, sample identification, or sample-rate execution. |
| `centroid` | Incorrect centroid-qualified interpolation/barycentric behavior or mismatch between the two sampling paths. |
| Any sample count | Multisample attachment/resolve setup, per-sample indexing, pipeline sample state, or host readback can make otherwise-correct shader results fail. |

### Cause Analysis

#### Explicit and ordinary interpolation disagree

**Possible failure symptoms:** One or more storage-buffer entries have expected and computed values differing by more than `0.0005`; the corresponding shader color is red.

**Possible implementation causes:** The implementation may produce inconsistent interpolation decorations between the vertex and fragment stages, lower `interpolateAtVertexAMD` incorrectly, or calculate the selected smooth/non-perspective barycentric coordinates incorrectly. The source and Vulkan interface rules establish the compared paths, but a more specific fault location requires implementation investigation.

#### Sample or centroid behavior disagrees

**Possible failure symptoms:** Only `sample` or `centroid` branches, or only particular sample IDs, show mismatched expected/computed pairs.

**Possible implementation causes:** The implementation may use the wrong interpolation sampling location, mishandle the AMD `SampleAMD`/`CentroidAMD` coordinate variant, or fail to execute the sample-qualified input at sample rate. The test source supports these hypotheses; it does not identify which implementation component is responsible.

#### Multisample setup or result indexing fails

**Possible failure symptoms:** Failures correlate with sample counts greater than one, with wrong or missing entries in the storage buffer.

**Possible implementation causes:** The multisample attachment, resolve path, sample state, `gl_SampleID`-based index, command-buffer rendering arrangement, or host-visible buffer handling may be incorrect. Source-level investigation is needed to distinguish these causes.

## Case Pruning

### Requirement-based pruning

- `sample` and `centroid` cases are not registered for `VK_SAMPLE_COUNT_1_BIT`, because the source treats those qualifiers as ineffective for a single sample ([`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L744-L758)).
- A requested sample count is skipped as unsupported when it is absent from `framebufferColorSampleCounts` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L250)).
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`, and all cases require `VK_AMD_shader_explicit_vertex_parameter` and sample-rate shading.

### Design-based pruning

- Secondary-command-buffer dynamic-rendering variants keep only sample counts 1, 2, and 4 to control the generated test count ([`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L744-L748)).
- Nested secondary variants are omitted at category registration time because `vktDrawTests.cpp` intentionally registers only `basic` for nested modes. This is a dispatcher design boundary, not evidence that explicit vertex parameters are unsupported there.

## Key Takeaways

- The family compares two independent shader paths: ordinary interpolation and explicit per-vertex fetch plus AMD barycentric reconstruction.
- `smooth` and `noperspective` test different interpolation mathematics; `sample` and `centroid` add sampling-location variants.
- The effective verdict is a host-side `abs(expected - computed) > 0.0005` check over every allocated storage-buffer entry, with the untouched-entry and NaN limitations described above.
- Render-pass and non-nested dynamic-rendering command-buffer arrangements reuse the same behavioral matrix, while nested dynamic-rendering paths intentionally do not register this family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test-family factory | [`createExplicitVertexParameterTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L764-L768) | Registers `explicit_vertex_parameter`. |
| Case generator | [`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L727-L760) | Defines interpolation, auxiliary, sample-count, and pruning matrix. |
| Support gate | [`DrawTestCase::checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L255) | Defines required extension, feature, sample-count, and dynamic-rendering support. |
| Shader generation | [`DrawTestCase::initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331) | Generates the compared vertex/fragment shader paths. |
| Host execution and verdict | [`DrawTestInstance::iterate()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L338-L627) | Creates resources, records rendering, reads results, and applies tolerance. |
| Draw dispatcher | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Establishes variant coverage and nested-mode omission. |
| Default mustpass coverage | [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt) | Confirms 104 Vulkan cases: 38 render-pass, 38 primary, and 14 per secondary path. |
| Vulkan SC mustpass coverage | [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt) | Confirms the 38 render-pass-only Vulkan SC cases. |
| AMD shader semantics | [`VK_AMD_shader_explicit_vertex_parameter`](https://registry.khronos.org/vulkan/specs/latest/html/appendices.html#VK_AMD_shader_explicit_vertex_parameter) | Connects Vulkan support to the AMD SPIR-V explicit-vertex-parameter extension. |
| Vulkan interface semantics | [Shader Input and Output Interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-iointerfaces) | Background for stage interface matching. |
| Understanding Brief | [ExplicitVertexParameterTests_brief.md](ExplicitVertexParameterTests_brief.md) | Learning-oriented analysis and source mapping. |
