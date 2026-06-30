## Overview

**Core question:** Does the geometry shader correctly handle fixed, runtime-selected, instanced, zero-output, maximum-output,
and side-effect-only emission patterns?

- This page covers the `geometry.basic` test family implemented by
  [vktGeometryBasicGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1).
- The test family has three behavioral groups: fixed output-count cases, runtime-varying output-count cases, and
  side-effect cases that write an SSBO while leaving the color buffer unchanged.
- Most cases render generated geometry into a small color attachment and compare the copied image with a reference PNG.
  The side-effect cases instead validate an SSBO sentinel plus exact color-buffer invariance.
- Failures point to geometry-stage emit-count handling, geometry-shader instancing, geometry-stage resource access,
  storage-buffer side effects, or rasterization of deliberately empty/degenerate output.

## Background Knowledge

- A geometry shader declares `max_vertices`, but each invocation can emit any legal count up to that limit. These cases
  deliberately exercise counts such as `0`, `6`, `10`, `100`, and `128`.
- `EmitVertex()` appends the current output values to the active output primitive. A wrong loop bound, skipped emit, or
  mishandled zero-count path changes the rendered reference image.
- Geometry-shader instancing runs multiple geometry invocations for one input primitive. The instanced varying-output
  cases use `gl_InvocationID` to select one of four expected output counts.
- The runtime count source is part of the test: some cases read counts from vertex attributes, some from a uniform buffer,
  and some from a sampled texture.
- Storage-buffer writes from a geometry shader are observable side effects. The side-effect cases prove those writes occur
  even when the geometry path should not produce visible color output.

## Registration Hierarchy

```text
geometry.basic
├── output_10
├── output_128
├── output_10_and_100
├── output_100_and_10
├── output_0_and_128
├── output_128_and_0
├── output_vary_by_attribute
├── output_vary_by_uniform
├── output_vary_by_texture
├── output_vary_by_attribute_instancing
├── output_vary_by_uniform_instancing
├── output_vary_by_texture_instancing
├── side_effect_with_condition
└── side_effect_with_degenerate
```

The leaves are registered by
[createBasicGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000-L1047)
and appear in the default geometry mustpass list at
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L1-L14). This test family has no intermediate nodes below
`geometry.basic`; each listed child is an executable test case leaf.

## Intermediate Nodes

`geometry.basic` goes directly from the test family to executable test case leaves. The leaves are best understood as three
behavioral groups rather than as registered intermediate nodes.

### Fixed output-count leaves — deterministic emit patterns

`output_10`, `output_128`, `output_10_and_100`, `output_100_and_10`, `output_0_and_128`, and `output_128_and_0` use
[GeometryOutputCountTest](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L451-L548). The host
draws one point per pattern entry. The geometry shader chooses a fixed emit count, or chooses between two emit counts with
`gl_PrimitiveIDIn`, and emits a triangle-strip row whose visible size reflects the selected count.

These leaves are especially useful for catching implementation mistakes around large geometry output, zero-output
invocations, and changes in output count between consecutive input primitives.

### Runtime-varying output-count leaves — count source and instancing behavior

The `output_vary_by_*` leaves use
[VaryingOutputCountCase](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L550-L769). They all target
the same expected count vector, `6`, `0`, `128`, and `10`, but the geometry shader obtains that count vector through different
paths:

- vertex attributes for `output_vary_by_attribute` and `output_vary_by_attribute_instancing`;
- a uniform buffer for `output_vary_by_uniform` and `output_vary_by_uniform_instancing`;
- a sampled RGBA8 texture for `output_vary_by_texture` and `output_vary_by_texture_instancing`.

The instanced variants set `layout(points, invocations=4) in` and use `gl_InvocationID` to choose which count applies to the
current invocation. This turns a single submitted point into four independent geometry-shader invocations.

### Side-effect leaves — storage-buffer writes without visible output

`side_effect_with_condition` and `side_effect_with_degenerate` are added with
[addFunctionCaseWithPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1037-L1042) instead
of the shared image-reference test instance. Their geometry shader writes `ssbo.value = 777u` and then avoids visible color
output either by taking a false conditional path or by emitting only two vertices for a triangle-strip output primitive.

The host checks both observations: the SSBO must contain `777u`, and the 1x1 color buffer must still equal the clear color.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Fixed output pattern | `10`, `128`, `10/100`, `100/10`, `0/128`, `128/0` | Selects how many vertices each point-input geometry invocation emits. | [fixed registrations](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1004-L1011) |
| Runtime count source | `attribute`, `uniform`, `texture` | Changes whether the geometry shader reads the count from vertex input, a uniform buffer, or a sampled texture. | [varying registrations](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1013-L1025) |
| Instancing mode | non-instanced, instanced | Changes whether one input point is processed by one geometry invocation or four invocations indexed by `gl_InvocationID`. | [instancing mode enum](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L72-L78) |
| Canonical varying counts | `6`, `0`, `128`, `10` | Exercises small, zero, maximum, and medium emit counts through every runtime count source. | [count constants](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L79-L85) |
| Side-effect scenario | `condition`, `degenerate` | Changes how the shader prevents visible color output after writing the SSBO sentinel. | [side-effect registrations](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1027-L1043) |
| Shared image comparison | reference PNG named from the test case leaf | Converts geometry-stage output correctness into a host-visible pass/fail image comparison. | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) |

## Shader Analysis

The representative walkthrough uses `dEQP-VK.geometry.basic.output_vary_by_texture_instancing` because it combines the most
important moving parts in this test family: descriptor-backed count selection, texture sampling in the geometry stage,
`gl_InvocationID`, four invocations, a zero-output invocation, and the maximum `128` output count. Fixed-pattern cases use the
same `EmitVertex()` principle with simpler count selection, while side-effect cases replace the image-reference shader with an
SSBO-writing shader described in the variation summary.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.basic.output_vary_by_texture_instancing
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `READ_TEXTURE` | The geometry shader samples a bound RGBA8 texture to derive the emitted vertex count. |
| `MODE_WITH_INSTANCING` | The geometry shader declares `layout(points, invocations=4) in` and uses `gl_InvocationID`. |
| Count vector | The four invocations select `6`, `0`, `128`, and `10` emitted vertices. |
| Output topology | `layout(triangle_strip, max_vertices = 128) out` gives enough budget for the maximum count. |

#### Purpose

This shader verifies that a geometry shader can use `gl_InvocationID` to sample a per-invocation texture slot and then use the
sampled channel to control a dynamic `EmitVertex()` loop. The rendered arcs prove the count source, invocation indexing, loop
bound, emitted positions, and output colors are all coherent.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Invocation setup | `layout(points, invocations=4) in` | Runs four geometry invocations for the single input point. |
| Texture coordinate selection | `1.0 / 8.0 + primitiveNdx / 4.0` | Samples the center of one of the four 4x1 texture texels. |
| Count decoding | Red, green, blue, and alpha channels map to `6`, `0`, `128`, and `10`. | Exercises small, zero, max, and medium output counts through a sampled resource. |
| Invocation placement | Adds `0.5 * vec4(cos(gl_InvocationID), sin(gl_InvocationID), 0, 0)` | Separates the four invocation outputs in screen space. |
| Emit loop | Emits two vertices per loop iteration until `emitCount / 2`. | Makes the dynamic count visible as triangle-strip geometry. |

#### Shader Code

This representative path is primarily a geometry-shader dynamic-output test, but the vertex and fragment shaders are shown to
separate incidental stage transport from the texture-backed count selection that the geometry shader actually tests.

##### Vertex Shader

```glsl
#version 310 es
/// Location 0 vertex input is the single point position used as the base for all geometry invocations.
layout(location = 0) in highp vec4 a_position;
/// Location 1 is forwarded by the common shader form; this texture-backed instanced case does not use it for count selection.
layout(location = 1) in highp vec4 a_emitCount;
/// Location 0 output exists because attribute and texture count-source variants share the same vertex shader shape.
layout(location = 0) out highp vec4 v_geom_emitCount;
void main (void)
{
    gl_Position = a_position;
    v_geom_emitCount = a_emitCount;
}
```

##### Geometry Shader

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
#extension GL_OES_texture_storage_multisample_2d_array : require
/// Geometry-stage execution shape: one input point is processed by four geometry invocations.
layout(points, invocations=4) in;
/// Triangle-strip output can emit up to the test's maximum dynamic count, `128`, in one invocation.
layout(triangle_strip, max_vertices = 128) out;
/// Location 0 input is present because the common vertex shader forwards an attribute, but this texture-backed path uses `gl_InvocationID` instead.
layout(location = 0) in highp vec4 v_geom_vertexNdx[];
/// Binding 0 is a combined image sampler populated by the host with four RGBA8 texels.
layout(binding = 0) uniform highp sampler2D u_sampler;
/// Location 0 output carries the selected invocation color to the fragment shader.
layout(location = 0) out highp vec4 v_frag_FragColor;
/// Explicit output block keeps `gl_Position` available for generated geometry vertices.
out gl_PerVertex
{
    vec4 gl_Position;
};
void main (void)
{
    /// Each geometry invocation selects one texel slot.
    highp float primitiveNdx = float(gl_InvocationID);
    highp vec2 texCoord = vec2(1.0 / 8.0 + primitiveNdx / 4.0, 0.5);
    highp vec4 texColor = texture(u_sampler, texCoord);
    mediump int emitCount = 0;
    if (texColor.x > 0.0)
        emitCount += 6;
    if (texColor.y > 0.0)
        emitCount += 0;
    if (texColor.z > 0.0)
        emitCount += 128;
    if (texColor.w > 0.0)
        emitCount += 10;

    const highp vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
    const highp vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
    const highp vec4 blue = vec4(0.0, 0.0, 1.0, 1.0);
    const highp vec4 yellow = vec4(1.0, 1.0, 0.0, 1.0);
    highp vec4 color = red;
    if (primitiveNdx == 1.0)
        color = green;
    else if (primitiveNdx == 2.0)
        color = blue;
    else if (primitiveNdx == 3.0)
        color = yellow;

    /// Invocation-specific offset separates the four generated arcs.
    highp vec4 basePos = gl_in[0].gl_Position +
        0.5 * vec4(cos(float(gl_InvocationID)), sin(float(gl_InvocationID)), 0.0, 0.0);
    for (mediump int i = 0; i < emitCount / 2; i++)
    {
        highp float angle = (float(i) + 0.5) / float(emitCount / 2) * 3.142;
        gl_Position = basePos + vec4(cos(angle),  sin(angle), 0.0, 0.0) * 0.15;
        v_frag_FragColor = color;
        EmitVertex();
        gl_Position = basePos + vec4(cos(angle), -sin(angle), 0.0, 0.0) * 0.15;
        v_frag_FragColor = color;
        EmitVertex();
    }
}
```

##### Fragment Shader

```glsl
#version 310 es
layout(location = 0) out mediump vec4 fragColor;
/// Location 0 input is the color selected by the geometry shader from the invocation/count path.
layout(location = 0) in highp vec4 v_frag_FragColor;
void main (void)
{
    fragColor = v_frag_FragColor;
}
```

#### Additional Info

- The vertex shader varies by count-source family: this representative texture case uses the attribute/texture form and
  forwards `a_emitCount`, but the geometry shader ignores that forwarded value and selects counts from `u_sampler` instead.
- The fragment shader is stable for the fixed-output and varying-output render cases: it directly writes the geometry
  shader's selected color, so visible differences come from geometry-stage emission behavior.
- The host creates a 4x1 RGBA8 sampled image whose texels are red, green, blue, and alpha-only. The geometry shader maps
  those active channels to `6`, `0`, `128`, and `10`.
- The non-instanced texture case uses the same texture decoding but selects the primitive index from forwarded vertex data
  instead of `gl_InvocationID`.
- The primary geometry shader uses default shader-build options; the walkthrough disassembly was generated for Vulkan 1.0 /
  SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Count source | Attribute variants read `v_geom_emitCount`; uniform variants read `emit.u_emitCount`; texture variants sample `u_sampler`. | [VaryingOutputCountCase::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L577-L764) |
| Instancing | Instanced cases use `layout(points, invocations=4) in` and `gl_InvocationID`; non-instanced cases use ordinary `layout(points) in`. | [instanced layout generation](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L613-L623) |
| Descriptor use | Uniform variants bind a uniform buffer; texture variants bind a combined image sampler. | [createPipelineLayout()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L235-L309) |
| Fixed-output leaves | Replace resource-derived counts with fixed pattern values and optionally `gl_PrimitiveIDIn`. | [fixed geometry shader generation](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L491-L528) |
| Side-effect leaves | Replace the visible arc shader with a GLSL 460 geometry shader that writes `ssbo.value = 777u`. | [sideEffectInitPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L803-L866) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 10
; Bound: 168
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_InvocationID %gl_in %_ %v_frag_FragColor %v_geom_vertexNdx
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 4
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 128
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_OES_texture_storage_multisample_2d_array"
               OpName %main "main"
               OpName %primitiveNdx "primitiveNdx"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %texCoord "texCoord"
               OpName %texColor "texColor"
               OpName %u_sampler "u_sampler"
               OpName %emitCount "emitCount"
               OpName %color "color"
               OpName %basePos "basePos"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %i "i"
               OpName %angle "angle"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %_ ""
               OpName %v_frag_FragColor "v_frag_FragColor"
               OpName %v_geom_vertexNdx "v_geom_vertexNdx"
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %u_sampler DescriptorSet 0
               OpDecorate %u_sampler Binding 0
               OpDecorate %emitCount RelaxedPrecision
               OpDecorate %47 RelaxedPrecision
               OpDecorate %48 RelaxedPrecision
               OpDecorate %55 RelaxedPrecision
               OpDecorate %56 RelaxedPrecision
               OpDecorate %64 RelaxedPrecision
               OpDecorate %65 RelaxedPrecision
               OpDecorate %73 RelaxedPrecision
               OpDecorate %74 RelaxedPrecision
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex Block
               OpDecorate %i RelaxedPrecision
               OpDecorate %120 RelaxedPrecision
               OpDecorate %121 RelaxedPrecision
               OpDecorate %123 RelaxedPrecision
               OpDecorate %126 RelaxedPrecision
               OpDecorate %127 RelaxedPrecision
               OpDecorate %128 RelaxedPrecision
               OpDecorate %129 RelaxedPrecision
               OpDecorate %130 RelaxedPrecision
               OpDecorate %131 RelaxedPrecision
               OpDecorate %132 RelaxedPrecision
               OpDecorate %134 RelaxedPrecision
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %v_frag_FragColor Location 0
               OpDecorate %162 RelaxedPrecision
               OpDecorate %164 RelaxedPrecision
               OpDecorate %v_geom_vertexNdx Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
%float_0_125 = OpConstant %float 0.125
    %float_4 = OpConstant %float 4
  %float_0_5 = OpConstant %float 0.5
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %27 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %28 = OpTypeSampledImage %27
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
  %u_sampler = OpVariable %_ptr_UniformConstant_28 UniformConstant
    %float_0 = OpConstant %float 0
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
      %int_6 = OpConstant %int 6
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
    %int_128 = OpConstant %int 128
     %uint_3 = OpConstant %uint 3
     %int_10 = OpConstant %int 10
    %float_1 = OpConstant %float 1
         %77 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %82 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
    %float_2 = OpConstant %float 2
         %89 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
    %float_3 = OpConstant %float 3
         %96 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
%gl_PerVertex = OpTypeStruct %v4float %float
%_arr_gl_PerVertex_uint_1 = OpTypeArray %gl_PerVertex %uint_1
%_ptr_Input__arr_gl_PerVertex_uint_1 = OpTypePointer Input %_arr_gl_PerVertex_uint_1
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_uint_1 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %int_2 = OpConstant %int 2
%float_3_14199996 = OpConstant %float 3.14199996
%gl_PerVertex_0 = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex_0 = OpTypePointer Output %gl_PerVertex_0
          %_ = OpVariable %_ptr_Output_gl_PerVertex_0 Output
%float_0_150000006 = OpConstant %float 0.150000006
%_ptr_Output_v4float = OpTypePointer Output %v4float
%v_frag_FragColor = OpVariable %_ptr_Output_v4float Output
      %int_1 = OpConstant %int 1
%_arr_v4float_uint_1 = OpTypeArray %v4float %uint_1
%_ptr_Input__arr_v4float_uint_1 = OpTypePointer Input %_arr_v4float_uint_1
%v_geom_vertexNdx = OpVariable %_ptr_Input__arr_v4float_uint_1 Input
       %main = OpFunction %void None %3
          %5 = OpLabel
%primitiveNdx = OpVariable %_ptr_Function_float Function
   %texCoord = OpVariable %_ptr_Function_v2float Function
   %texColor = OpVariable %_ptr_Function_v4float Function
  %emitCount = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4float Function
    %basePos = OpVariable %_ptr_Function_v4float Function
          %i = OpVariable %_ptr_Function_int Function
      %angle = OpVariable %_ptr_Function_float Function
         %12 = OpLoad %int %gl_InvocationID
         %13 = OpConvertSToF %float %12
               OpStore %primitiveNdx %13
         %18 = OpLoad %float %primitiveNdx
         %20 = OpFDiv %float %18 %float_4
         %21 = OpFAdd %float %float_0_125 %20
         %23 = OpCompositeConstruct %v2float %21 %float_0_5
               OpStore %texCoord %23
         %31 = OpLoad %28 %u_sampler
         %32 = OpLoad %v2float %texCoord
         %34 = OpImageSampleExplicitLod %v4float %31 %32 Lod %float_0
               OpStore %texColor %34
               OpStore %emitCount %int_0
         %40 = OpAccessChain %_ptr_Function_float %texColor %uint_0
         %41 = OpLoad %float %40
         %43 = OpFOrdGreaterThan %bool %41 %float_0
               OpSelectionMerge %45 None
               OpBranchConditional %43 %44 %45
         %44 = OpLabel
         %47 = OpLoad %int %emitCount
         %48 = OpIAdd %int %47 %int_6
               OpStore %emitCount %48
               OpBranch %45
         %45 = OpLabel
         %50 = OpAccessChain %_ptr_Function_float %texColor %uint_1
         %51 = OpLoad %float %50
         %52 = OpFOrdGreaterThan %bool %51 %float_0
               OpSelectionMerge %54 None
               OpBranchConditional %52 %53 %54
         %53 = OpLabel
         %55 = OpLoad %int %emitCount
         %56 = OpIAdd %int %55 %int_0
               OpStore %emitCount %56
               OpBranch %54
         %54 = OpLabel
         %58 = OpAccessChain %_ptr_Function_float %texColor %uint_2
         %59 = OpLoad %float %58
         %60 = OpFOrdGreaterThan %bool %59 %float_0
               OpSelectionMerge %62 None
               OpBranchConditional %60 %61 %62
         %61 = OpLabel
         %64 = OpLoad %int %emitCount
         %65 = OpIAdd %int %64 %int_128
               OpStore %emitCount %65
               OpBranch %62
         %62 = OpLabel
         %67 = OpAccessChain %_ptr_Function_float %texColor %uint_3
         %68 = OpLoad %float %67
         %69 = OpFOrdGreaterThan %bool %68 %float_0
               OpSelectionMerge %71 None
               OpBranchConditional %69 %70 %71
         %70 = OpLabel
         %73 = OpLoad %int %emitCount
         %74 = OpIAdd %int %73 %int_10
               OpStore %emitCount %74
               OpBranch %71
         %71 = OpLabel
               OpStore %color %77
         %78 = OpLoad %float %primitiveNdx
         %79 = OpFOrdEqual %bool %78 %float_1
               OpSelectionMerge %81 None
               OpBranchConditional %79 %80 %83
         %80 = OpLabel
               OpStore %color %82
               OpBranch %81
         %83 = OpLabel
         %84 = OpLoad %float %primitiveNdx
         %86 = OpFOrdEqual %bool %84 %float_2
               OpSelectionMerge %88 None
               OpBranchConditional %86 %87 %90
         %87 = OpLabel
               OpStore %color %89
               OpBranch %88
         %90 = OpLabel
         %91 = OpLoad %float %primitiveNdx
         %93 = OpFOrdEqual %bool %91 %float_3
               OpSelectionMerge %95 None
               OpBranchConditional %93 %94 %95
         %94 = OpLabel
               OpStore %color %96
               OpBranch %95
         %95 = OpLabel
               OpBranch %88
         %88 = OpLabel
               OpBranch %81
         %81 = OpLabel
        %103 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
        %104 = OpLoad %v4float %103
        %105 = OpLoad %int %gl_InvocationID
        %106 = OpConvertSToF %float %105
        %107 = OpExtInst %float %1 Cos %106
        %108 = OpLoad %int %gl_InvocationID
        %109 = OpConvertSToF %float %108
        %110 = OpExtInst %float %1 Sin %109
        %111 = OpCompositeConstruct %v4float %107 %110 %float_0 %float_0
        %112 = OpVectorTimesScalar %v4float %111 %float_0_5
        %113 = OpFAdd %v4float %104 %112
               OpStore %basePos %113
               OpStore %i %int_0
               OpBranch %115
        %115 = OpLabel
               OpLoopMerge %117 %118 None
               OpBranch %119
        %119 = OpLabel
        %120 = OpLoad %int %i
        %121 = OpLoad %int %emitCount
        %123 = OpSDiv %int %121 %int_2
        %124 = OpSLessThan %bool %120 %123
               OpBranchConditional %124 %116 %117
        %116 = OpLabel
        %126 = OpLoad %int %i
        %127 = OpConvertSToF %float %126
        %128 = OpFAdd %float %127 %float_0_5
        %129 = OpLoad %int %emitCount
        %130 = OpSDiv %int %129 %int_2
        %131 = OpConvertSToF %float %130
        %132 = OpFDiv %float %128 %131
        %134 = OpFMul %float %132 %float_3_14199996
               OpStore %angle %134
        %138 = OpLoad %v4float %basePos
        %139 = OpLoad %float %angle
        %140 = OpExtInst %float %1 Cos %139
        %141 = OpLoad %float %angle
        %142 = OpExtInst %float %1 Sin %141
        %143 = OpCompositeConstruct %v4float %140 %142 %float_0 %float_0
        %145 = OpVectorTimesScalar %v4float %143 %float_0_150000006
        %146 = OpFAdd %v4float %138 %145
        %148 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %148 %146
        %150 = OpLoad %v4float %color
               OpStore %v_frag_FragColor %150
               OpEmitVertex
        %151 = OpLoad %v4float %basePos
        %152 = OpLoad %float %angle
        %153 = OpExtInst %float %1 Cos %152
        %154 = OpLoad %float %angle
        %155 = OpExtInst %float %1 Sin %154
        %156 = OpFNegate %float %155
        %157 = OpCompositeConstruct %v4float %153 %156 %float_0 %float_0
        %158 = OpVectorTimesScalar %v4float %157 %float_0_150000006
        %159 = OpFAdd %v4float %151 %158
        %160 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %160 %159
        %161 = OpLoad %v4float %color
               OpStore %v_frag_FragColor %161
               OpEmitVertex
               OpBranch %118
        %118 = OpLabel
        %162 = OpLoad %int %i
        %164 = OpIAdd %int %162 %int_1
               OpStore %i %164
               OpBranch %115
        %117 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- For fixed-output and varying-output leaves, support checking requires the Vulkan `geometryShader` core feature.
- The shared render instance creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color image, a vertex buffer, a graphics pipeline,
  and any descriptor set needed by the selected count source.
- The vertex buffer stores one `vec4` position and one `vec4` attribute per input vertex. Depending on the case, the attribute
  is a color, an emitted-count vector, or an index into uniform/texture data.
- Uniform variants allocate a host-visible uniform buffer containing `{6, 0, 128, 10}` and bind it at descriptor binding `0`.
- Texture variants create a 4x1 RGBA8 sampled image whose four texels encode the same count vector by active channel, then
  bind a combined image sampler at descriptor binding `0`.
- The command buffer renders the draw, copies the color attachment into a host-visible buffer, and waits for completion.
- Host validation compares the copied image with `vulkan/data/geometry/<test-name>.png` through `tcu::fuzzyCompare()` followed
  by `tcu::intThresholdPositionDeviationCompare()`.

For side-effect leaves:

- support checking requires both `geometryShader` and `vertexPipelineStoresAndAtomics`;
- the host initializes a storage buffer with `condition = 0` and `value = 0`;
- the geometry shader writes `ssbo.value = 777u`;
- validation requires the storage buffer value to equal `777u` and the copied 1x1 color buffer to remain exactly equal to the
  clear color.

A rendered-image failure means the emitted geometry did not match the expected pattern. A side-effect failure means either the
geometry-stage storage-buffer write was lost/incorrect or the shader produced visible raster output when the case design says
it should not.

## Case Pruning

### Requirement-based pruning

- Fixed-output and varying-output leaves require the `geometryShader` core feature through their `checkSupport()` methods.
- Side-effect leaves require both `geometryShader` and `vertexPipelineStoresAndAtomics`, because the geometry shader writes a
  storage buffer.

### Design-based pruning

- The fixed-output matrix is intentionally small: it uses representative single-count and two-count patterns rather than every
  possible `max_vertices` value.
- Runtime-varying cases reuse the same canonical count vector across attributes, uniforms, and textures so differences in
  output isolate the count source or instancing behavior.
- Side-effect cases are separated from image-reference output cases because their central property is the preservation of a
  geometry-stage side effect when visible raster output should be absent.

## Key Takeaways

- `geometry.basic` checks more than ordinary geometry-shader rendering; it combines fixed emission, resource-derived dynamic
  emission, geometry-shader instancing, and side-effect preservation.
- The zero-count and `128`-count paths are central stress points: they can expose skipped invocation handling, loop-bound bugs,
  or incorrect maximum-output handling.
- Descriptor-backed variants can expose implementations that do not correctly make uniform buffers or sampled images available
  to the geometry stage.
- Side-effect leaves can expose shader compiler or driver optimizations that incorrectly remove geometry-stage storage-buffer
  writes when raster output is conditional or degenerate.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [createBasicGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000-L1047) | Defines every `geometry.basic` test case leaf. |
| Fixed-output shader generator | [GeometryOutputCountTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L475-L542) | Generates the fixed-pattern vertex, geometry, and fragment shaders. |
| Varying-output resource setup | [VaryingOutputCountTestInstance](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L184-L391) | Builds vertex data, uniform buffers, sampled images, samplers, and descriptors for runtime count sources. |
| Varying-output shader generator | [VaryingOutputCountCase::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L577-L764) | Generates the attribute, uniform, texture, and instanced geometry shader variants. |
| Fixed and varying render execution | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Provides the common render, copyback, and image-reference validation path. |
| Reference-image comparison helper | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Defines the image comparison tolerance and reference file naming. |
| Side-effect shader generator | [sideEffectInitPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L803-L866) | Generates the SSBO-writing geometry shaders. |
| Side-effect validation | [sideEffectTest()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L868-L996) | Checks the `777u` SSBO sentinel and unchanged color buffer. |
