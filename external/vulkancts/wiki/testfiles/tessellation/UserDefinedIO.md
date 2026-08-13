## Overview

**Core question:** Do user-defined values survive every tested tessellation control-to-evaluation interface form without a type, array, block-member, or per-vertex indexing error?

- This page covers the `tessellation.user_defined_io` test family implemented by [`vktTessellationUserDefinedIO.cpp`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1-L1090).
- The family tests six IO forms: singular and arrayed per-patch data, singular and arrayed per-patch interface blocks, standalone per-vertex values, and per-vertex interface blocks.
- Each case assigns a deterministic value sequence in the tessellation control shader. The tessellation evaluation shader checks every scalar/vector leaf, renders green for correct input, renders red for a mismatch, and returns a diagnostic index through an SSBO.
- Three array-size spellings and three primitive types extend the matrix to 54 executable cases.

## Background Knowledge

For the shared concepts tessellation pipeline stages and patch interfaces, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Tessellation stage interface:** A tessellation control shader produces an output patch. Each invocation supplies one output control point and may also write data shared by the patch. The tessellation evaluation shader receives that patch and runs for tessellator-generated coordinates. See [Tessellation Control and Evaluation Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2576-L2681).
- **User-defined interface matching:** Non-built-in shader inputs and outputs use `Location` decorations. Producer and consumer declarations must match in decorations and type structure. Arrays at tessellation stage boundaries have special matching rules described in [User-Defined Variable Interface and Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L104-L180).
- **Basic subobject:** This source treats each scalar or vector reached while recursively traversing a variable, array, structure, or block as one basic subobject. That gives the test an ordered unit for assignment, comparison, and failure reporting.

## Registration Hierarchy

```text
tessellation.user_defined_io
├── per_patch
├── per_patch_array
├── per_patch_block
├── per_patch_block_array
├── per_vertex
└── per_vertex_block
```

Each direct child expands to the three `vertex_io_array_size_*` intermediate nodes, and each of those contains the `isolines`, `quads`, and `triangles` leaves. The source registration loop and mustpass list contain all 54 combinations ([registration source](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1031-L1087), [mustpass inventory](../../../mustpass/main/vk-default/tessellation.txt#L1002-L1055)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| IO form | `per_patch`, `per_patch_array`, `per_patch_block`, `per_patch_block_array`, `per_vertex`, `per_vertex_block` | Selects patch-wide or control-point-specific ownership, singular or arrayed top-level objects, and standalone variables or interface blocks. | [`IOType` and `ioCases`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L70-L80), [registration names](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1035-L1052) |
| Vertex IO array size | `vertex_io_array_size_implicit`, `vertex_io_array_size_shader_builtin`, `vertex_io_array_size_spec_min` | Spells the tessellation-control input capacity as unsized, `gl_MaxPatchVertices`, or `32`. For per-vertex user-defined IO, it also changes the evaluation input declaration. The shader still checks the five elements produced by the output patch. | [`VertexIOArraySize` and size selection](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L82-L89), [declaration branches](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L486-L496), [TES array declaration](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L627-L658) |
| Primitive type | `isolines`, `quads`, `triangles` | Selects the evaluation input primitive and reference PNG; with the fixed tessellation levels, it determines the tessellated vertex count. It does not change the generated user-defined value sequence. | [`CaseDefinition`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L91-L97), [TES layout](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L716-L750), [registration loop](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1071-L1080) |

Fixed values that shape every case:

| Value | Use |
|-------|-----|
| 5 | Tessellation control output vertices and produced per-vertex elements. |
| 3 | Elements in a standalone per-patch array. |
| 2 | Elements in a per-patch interface-block array. |
| 32 | Explicit specification-minimum array capacity. |
| `3, 4` and `5, 6, 7, 8` | Positive inner and outer tessellation levels. |
| `1.2, 1.3` and `-0.3, -0.4` | Position scale and offset used to place the rendered primitive. |
| 256 by 256 | Color target and reference-image extent. |

## Behavior Parameters

The primary behavioral axis is **IO form**. It changes who owns the value and how the producer and consumer declare the stage interface.

### `per_patch`: singular patch-wide variables

The control shader writes one `patch out` structure and one `patch out` float. The evaluation shader receives matching singular `patch in` variables and compares their basic subobjects once per invocation. This is the smallest case that combines structure and scalar transport.

### `per_patch_array`: patch-wide standalone array

The control shader and evaluation shader exchange a three-element `patch` array of floats. The generator omits the structure variable for this form because the intended standalone array-of-structure output declaration is outside the legal shape selected by the source. This value focuses on explicit array traversal and index preservation.

### `per_patch_block`: singular patch-wide interface block

A `patch`-qualified `TheBlock` carries a structure, a three-float array, an array of two structures, and one float. The nested structure contains an additional two-float array in block forms. The evaluation shader recursively checks every block member and nested array element.

### `per_patch_block_array`: arrayed patch-wide interface block

The interface consists of two `patch`-qualified `TheBlock` elements. The source uses a smaller block for this form by omitting the direct `blockS` member, which keeps the generated per-patch declaration within the intended storage budget while retaining member-array and structure-array coverage.

### `per_vertex`: standalone control-point values

Each of the five control-shader invocations writes one array element selected by `gl_InvocationID`. The element contains a structure and a separate float. The evaluation shader traverses all five produced elements in a fixed order, which checks both invocation-to-element mapping and cross-stage value transport.

### `per_vertex_block`: control-point interface blocks

Each control-shader invocation writes one element of an interface-block array. The block combines structures, nested arrays, and a scalar. This form checks per-vertex indexing together with member matching and nested composite transport.

## Shader Analysis

One walkthrough is enough to expose the central mechanism. `per_vertex.vertex_io_array_size_spec_min.triangles` combines per-invocation producer indexing, an explicit 32-element consumer declaration, structure transport, scalar transport, and SSBO diagnostics. Block variants add more recursively generated members but preserve the same assign-then-compare design.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.user_defined_io.per_vertex.vertex_io_array_size_spec_min.triangles
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `per_vertex` | Each of five control-shader invocations writes its own structure and float array elements. |
| `vertex_io_array_size_spec_min` | Per-vertex inputs declare capacity `32`, the required minimum `maxTessellationPatchSize`; only the five produced elements are checked. |
| `triangles` | The evaluation shader uses `layout(triangles) in`, and runtime verification loads the triangle reference image. |

#### Purpose

The evaluation shader verifies that all five per-vertex structure elements and all five scalar elements contain the deterministic sequence produced by the control shader. It reports the first mismatching basic-subobject index for every evaluation invocation.

#### Structural Design

| Phase | Evaluation-shader action | Observable result |
|-------|--------------------------|-------------------|
| Interface receive | Read `in_te_s[32]` at location 2 and `in_te_f[32]` at location 4. | Five producer-written elements are available through an explicitly sized declaration. |
| Structure checks | Compare `x` and `y` for elements 0 through 4. | Ten basic-subobject checks advance the diagnostic index while values remain correct. |
| Scalar checks | Compare `in_te_f[0..4]`. | Five more checks complete an expected success index of 15. |
| Render signal | Select green when all comparisons pass, red otherwise. | Image comparison catches visible corruption or broader rendering failure. |
| Diagnostic signal | Atomically allocate one SSBO slot and store the first-failure index. | Host code identifies the exact failing input path. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(triangles) in;

layout(location = 0) patch in highp vec2 in_te_positionScale;
layout(location = 1) patch in highp vec2 in_te_positionOffset;

struct S
{
    highp int x;
    highp vec4 y;
};

/// The producer emits five elements; this declaration spells the permitted
/// capacity with the specification minimum maxTessellationPatchSize.
layout(location = 2) in S in_te_s[32];
layout(location = 4) in highp float in_te_f[32];

layout(location = 0) out highp vec4 in_f_color;

// Will contain the index of the first incorrect input,
// or the number of inputs if all are correct
layout (set = 0, binding = 0, std430) coherent restrict buffer Output {
    int  numInvocations;
    uint firstFailedInputIndex[];
} sb_out;

bool compare_int   (int   a, int   b) { return a == b; }
bool compare_float (float a, float b) { return abs(a - b) < 0.01f; }
bool compare_vec4  (vec4  a, vec4  b) { return all(lessThan(abs(a - b), vec4(0.01f))); }

void main (void)
{
    bool allOk = true;
    highp uint firstFailedInputIndex = 0u;
    {
        highp float v = 1.3;

        // Check values in input in_te_s
        /// Compare both basic subobjects in each of the five produced elements.
        for (int i0 = 0; i0 < 5; ++i0)
        {
            allOk = allOk && compare_int(in_te_s[i0].x, int(v));
            v += 0.4;
            if (allOk) ++firstFailedInputIndex;
            allOk = allOk && compare_vec4(in_te_s[i0].y, vec4(v, v+0.8, v+1.6, v+2.4));
            v += 0.4;
            if (allOk) ++firstFailedInputIndex;
        }

        // Check values in input in_te_f
        for (int i0 = 0; i0 < 5; ++i0)
        {
            allOk = allOk && compare_float(in_te_f[i0], v);
            v += 0.4;
            if (allOk) ++firstFailedInputIndex;
        }
    }

    gl_Position = vec4(gl_TessCoord.xy*in_te_positionScale + in_te_positionOffset, 0.0, 1.0);
    in_f_color  = allOk ? vec4(0.0, 1.0, 0.0, 1.0)
                        : vec4(1.0, 0.0, 0.0, 1.0);

    /// Append this invocation's first-failure index to the host-visible result buffer.
    int index = atomicAdd(sb_out.numInvocations, 1);
    sb_out.firstFailedInputIndex[index] = firstFailedInputIndex;
}
```

#### Additional Info

- [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L568-L665) generates the assignment and comparison statements from the same ordered object model, but through separate producer and consumer traversals.
- The evaluation shader compares floats and vectors with an absolute tolerance of `0.01`; integer components use exact equality ([comparison helpers](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L730-L750)).
- The shown evaluation shader is the primary stage. The matching control shader writes each `gl_InvocationID` element and preserves global sequence order by adjusting `v` around each invocation's local writes ([producer generation](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L568-L613)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| IO form | Changes `patch` qualification, top-level array length, standalone-variable versus block declarations, nested members, and whether producer assignment uses `gl_InvocationID`. | [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L478-L665) |
| Vertex IO array size | Replaces `[32]` with `[]` or `[gl_MaxPatchVertices]` in applicable input declarations. The comparison loop still visits five per-vertex elements. | [size and declaration selection](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L486-L496), [TES traversal](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L627-L658) |
| Primitive type | Replaces `layout(triangles) in` with `layout(isolines) in` or `layout(quads) in`; interface comparison code stays unchanged. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L716-L752) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 202
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %in_te_s %in_te_f %_ %gl_TessCoord %in_te_positionScale %in_te_positionOffset %in_f_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %compare_int_i1_i1_ "compare_int(i1;i1;"
               OpName %a "a"
               OpName %b "b"
               OpName %compare_float_f1_f1_ "compare_float(f1;f1;"
               OpName %a_0 "a"
               OpName %b_0 "b"
               OpName %compare_vec4_vf4_vf4_ "compare_vec4(vf4;vf4;"
               OpName %a_1 "a"
               OpName %b_1 "b"
               OpName %allOk "allOk"
               OpName %firstFailedInputIndex "firstFailedInputIndex"
               OpName %v "v"
               OpName %i0 "i0"
               OpName %S "S"
               OpMemberName %S 0 "x"
               OpMemberName %S 1 "y"
               OpName %in_te_s "in_te_s"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %param_1 "param"
               OpName %param_2 "param"
               OpName %i0_0 "i0"
               OpName %in_te_f "in_te_f"
               OpName %param_3 "param"
               OpName %param_4 "param"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %in_te_positionScale "in_te_positionScale"
               OpName %in_te_positionOffset "in_te_positionOffset"
               OpName %in_f_color "in_f_color"
               OpName %index "index"
               OpName %Output "Output"
               OpMemberName %Output 0 "numInvocations"
               OpMemberName %Output 1 "firstFailedInputIndex"
               OpName %sb_out "sb_out"
               OpDecorate %in_te_s Location 2
               OpDecorate %in_te_f Location 4
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %in_te_positionScale Patch
               OpDecorate %in_te_positionScale Location 0
               OpDecorate %in_te_positionOffset Patch
               OpDecorate %in_te_positionOffset Location 1
               OpDecorate %in_f_color Location 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Restrict
               OpMemberDecorate %Output 0 Coherent
               OpMemberDecorate %Output 0 Offset 0
               OpMemberDecorate %Output 1 Restrict
               OpMemberDecorate %Output 1 Coherent
               OpMemberDecorate %Output 1 Offset 4
               OpDecorate %sb_out Restrict
               OpDecorate %sb_out Coherent
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %bool = OpTypeBool
          %9 = OpTypeFunction %bool %_ptr_Function_int %_ptr_Function_int
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
         %16 = OpTypeFunction %bool %_ptr_Function_float %_ptr_Function_float
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %23 = OpTypeFunction %bool %_ptr_Function_v4float %_ptr_Function_v4float
%float_0_00999999978 = OpConstant %float 0.00999999978
         %45 = OpConstantComposite %v4float %float_0_00999999978 %float_0_00999999978 %float_0_00999999978 %float_0_00999999978
     %v4bool = OpTypeVector %bool 4
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
%float_1_29999995 = OpConstant %float 1.29999995
      %int_0 = OpConstant %int 0
      %int_5 = OpConstant %int 5
          %S = OpTypeStruct %int %v4float
    %uint_32 = OpConstant %uint 32
%_arr_S_uint_32 = OpTypeArray %S %uint_32
%_ptr_Input__arr_S_uint_32 = OpTypePointer Input %_arr_S_uint_32
    %in_te_s = OpVariable %_ptr_Input__arr_S_uint_32 Input
%_ptr_Input_int = OpTypePointer Input %int
%float_0_400000006 = OpConstant %float 0.400000006
      %int_1 = OpConstant %int 1
%float_0_800000012 = OpConstant %float 0.800000012
%float_1_60000002 = OpConstant %float 1.60000002
%float_2_4000001 = OpConstant %float 2.4000001
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_arr_float_uint_32 = OpTypeArray %float %uint_32
%_ptr_Input__arr_float_uint_32 = OpTypePointer Input %_arr_float_uint_32
    %in_te_f = OpVariable %_ptr_Input__arr_float_uint_32 Input
%_ptr_Input_float = OpTypePointer Input %float
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
%in_te_positionScale = OpVariable %_ptr_Input_v2float Input
%in_te_positionOffset = OpVariable %_ptr_Input_v2float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
 %in_f_color = OpVariable %_ptr_Output_v4float Output
        %185 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %186 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Output = OpTypeStruct %int %_runtimearr_uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
     %uint_1 = OpConstant %uint 1
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
      %allOk = OpVariable %_ptr_Function_bool Function
%firstFailedInputIndex = OpVariable %_ptr_Function_uint Function
          %v = OpVariable %_ptr_Function_float Function
         %i0 = OpVariable %_ptr_Function_int Function
      %param = OpVariable %_ptr_Function_int Function
    %param_0 = OpVariable %_ptr_Function_int Function
    %param_1 = OpVariable %_ptr_Function_v4float Function
    %param_2 = OpVariable %_ptr_Function_v4float Function
       %i0_0 = OpVariable %_ptr_Function_int Function
    %param_3 = OpVariable %_ptr_Function_float Function
    %param_4 = OpVariable %_ptr_Function_float Function
      %index = OpVariable %_ptr_Function_int Function
               OpStore %allOk %true
               OpStore %firstFailedInputIndex %uint_0
               OpStore %v %float_1_29999995
               OpStore %i0 %int_0
               OpBranch %62
         %62 = OpLabel
               OpLoopMerge %64 %65 None
               OpBranch %66
         %66 = OpLabel
         %67 = OpLoad %int %i0
         %69 = OpSLessThan %bool %67 %int_5
               OpBranchConditional %69 %63 %64
         %63 = OpLabel
         %70 = OpLoad %bool %allOk
               OpSelectionMerge %72 None
               OpBranchConditional %70 %71 %72
         %71 = OpLabel
         %78 = OpLoad %int %i0
         %79 = OpLoad %float %v
         %80 = OpConvertFToS %int %79
         %83 = OpAccessChain %_ptr_Input_int %in_te_s %78 %int_0
         %84 = OpLoad %int %83
               OpStore %param %84
               OpStore %param_0 %80
         %86 = OpFunctionCall %bool %compare_int_i1_i1_ %param %param_0
               OpBranch %72
         %72 = OpLabel
         %87 = OpPhi %bool %70 %63 %86 %71
               OpStore %allOk %87
         %89 = OpLoad %float %v
         %90 = OpFAdd %float %89 %float_0_400000006
               OpStore %v %90
         %91 = OpLoad %bool %allOk
               OpSelectionMerge %93 None
               OpBranchConditional %91 %92 %93
         %92 = OpLabel
         %94 = OpLoad %uint %firstFailedInputIndex
         %96 = OpIAdd %uint %94 %int_1
               OpStore %firstFailedInputIndex %96
               OpBranch %93
         %93 = OpLabel
         %97 = OpLoad %bool %allOk
               OpSelectionMerge %99 None
               OpBranchConditional %97 %98 %99
         %98 = OpLabel
        %100 = OpLoad %int %i0
        %101 = OpLoad %float %v
        %102 = OpLoad %float %v
        %104 = OpFAdd %float %102 %float_0_800000012
        %105 = OpLoad %float %v
        %107 = OpFAdd %float %105 %float_1_60000002
        %108 = OpLoad %float %v
        %110 = OpFAdd %float %108 %float_2_4000001
        %111 = OpCompositeConstruct %v4float %101 %104 %107 %110
        %114 = OpAccessChain %_ptr_Input_v4float %in_te_s %100 %int_1
        %115 = OpLoad %v4float %114
               OpStore %param_1 %115
               OpStore %param_2 %111
        %117 = OpFunctionCall %bool %compare_vec4_vf4_vf4_ %param_1 %param_2
               OpBranch %99
         %99 = OpLabel
        %118 = OpPhi %bool %97 %93 %117 %98
               OpStore %allOk %118
        %119 = OpLoad %float %v
        %120 = OpFAdd %float %119 %float_0_400000006
               OpStore %v %120
        %121 = OpLoad %bool %allOk
               OpSelectionMerge %123 None
               OpBranchConditional %121 %122 %123
        %122 = OpLabel
        %124 = OpLoad %uint %firstFailedInputIndex
        %125 = OpIAdd %uint %124 %int_1
               OpStore %firstFailedInputIndex %125
               OpBranch %123
        %123 = OpLabel
               OpBranch %65
         %65 = OpLabel
        %126 = OpLoad %int %i0
        %127 = OpIAdd %int %126 %int_1
               OpStore %i0 %127
               OpBranch %62
         %64 = OpLabel
               OpStore %i0_0 %int_0
               OpBranch %129
        %129 = OpLabel
               OpLoopMerge %131 %132 None
               OpBranch %133
        %133 = OpLabel
        %134 = OpLoad %int %i0_0
        %135 = OpSLessThan %bool %134 %int_5
               OpBranchConditional %135 %130 %131
        %130 = OpLabel
        %136 = OpLoad %bool %allOk
               OpSelectionMerge %138 None
               OpBranchConditional %136 %137 %138
        %137 = OpLabel
        %142 = OpLoad %int %i0_0
        %145 = OpAccessChain %_ptr_Input_float %in_te_f %142
        %146 = OpLoad %float %145
               OpStore %param_3 %146
        %148 = OpLoad %float %v
               OpStore %param_4 %148
        %149 = OpFunctionCall %bool %compare_float_f1_f1_ %param_3 %param_4
               OpBranch %138
        %138 = OpLabel
        %150 = OpPhi %bool %136 %130 %149 %137
               OpStore %allOk %150
        %151 = OpLoad %float %v
        %152 = OpFAdd %float %151 %float_0_400000006
               OpStore %v %152
        %153 = OpLoad %bool %allOk
               OpSelectionMerge %155 None
               OpBranchConditional %153 %154 %155
        %154 = OpLabel
        %156 = OpLoad %uint %firstFailedInputIndex
        %157 = OpIAdd %uint %156 %int_1
               OpStore %firstFailedInputIndex %157
               OpBranch %155
        %155 = OpLabel
               OpBranch %132
        %132 = OpLabel
        %158 = OpLoad %int %i0_0
        %159 = OpIAdd %int %158 %int_1
               OpStore %i0_0 %159
               OpBranch %129
        %131 = OpLabel
        %167 = OpLoad %v3float %gl_TessCoord
        %168 = OpVectorShuffle %v2float %167 %167 0 1
        %171 = OpLoad %v2float %in_te_positionScale
        %172 = OpFMul %v2float %168 %171
        %174 = OpLoad %v2float %in_te_positionOffset
        %175 = OpFAdd %v2float %172 %174
        %178 = OpCompositeExtract %float %175 0
        %179 = OpCompositeExtract %float %175 1
        %180 = OpCompositeConstruct %v4float %178 %179 %float_0 %float_1
        %182 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %182 %180
        %184 = OpLoad %bool %allOk
        %187 = OpCompositeConstruct %v4bool %184 %184 %184 %184
        %188 = OpSelect %v4float %187 %185 %186
               OpStore %in_f_color %188
        %195 = OpAccessChain %_ptr_Uniform_int %sb_out %int_0
        %197 = OpAtomicIAdd %int %195 %uint_1 %uint_0 %int_1
               OpStore %index %197
        %198 = OpLoad %int %index
        %199 = OpLoad %uint %firstFailedInputIndex
        %201 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_1 %198
               OpStore %201 %199
               OpReturn
               OpFunctionEnd
%compare_int_i1_i1_ = OpFunction %bool None %9
          %a = OpFunctionParameter %_ptr_Function_int
          %b = OpFunctionParameter %_ptr_Function_int
         %13 = OpLabel
         %28 = OpLoad %int %a
         %29 = OpLoad %int %b
         %30 = OpIEqual %bool %28 %29
               OpReturnValue %30
               OpFunctionEnd
%compare_float_f1_f1_ = OpFunction %bool None %16
        %a_0 = OpFunctionParameter %_ptr_Function_float
        %b_0 = OpFunctionParameter %_ptr_Function_float
         %20 = OpLabel
         %33 = OpLoad %float %a_0
         %34 = OpLoad %float %b_0
         %35 = OpFSub %float %33 %34
         %36 = OpExtInst %float %1 FAbs %35
         %38 = OpFOrdLessThan %bool %36 %float_0_00999999978
               OpReturnValue %38
               OpFunctionEnd
%compare_vec4_vf4_vf4_ = OpFunction %bool None %23
        %a_1 = OpFunctionParameter %_ptr_Function_v4float
        %b_1 = OpFunctionParameter %_ptr_Function_v4float
         %27 = OpLabel
         %41 = OpLoad %v4float %a_1
         %42 = OpLoad %v4float %b_1
         %43 = OpFSub %v4float %41 %42
         %44 = OpExtInst %v4float %1 FAbs %43
         %47 = OpFOrdLessThan %v4bool %44 %45
         %48 = OpAll %bool %47
               OpReturnValue %48
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host uploads ten floats as one patch of ten scalar vertex attributes: six tessellation levels plus two scale and two offset components. The graphics pipeline uses ten input control points, while the tessellation control shader emits five output vertices ([attribute setup and pipeline](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L803-L826), [pipeline construction](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L884-L907)).
- The result SSBO holds a signed invocation count followed by enough unsigned diagnostic entries for the reference maximum vertex count. The host clears it to zero and binds it only to the tessellation evaluation stage at set 0, binding 0 ([result buffer and descriptors](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L828-L883)).
- The host creates a 256 by 256 `VK_FORMAT_R8G8B8A8_UNORM` color attachment and a host-visible transfer destination. One draw renders into the black-cleared image; the command buffer then copies the image to the readback buffer and waits for completion ([image setup](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L843-L862), [draw and copy](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L909-L946)).
- The host fuzzy-compares the result against the primitive-specific PNG with threshold `0.02`. Correct interface values produce green; a device-side comparison mismatch selects red ([image check](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L948-L967)).
- The observed evaluation invocation count must reach at least the primitive's reference unique-vertex count. The buffer allocation uses the larger reference vertex count as capacity. This accounts for implementations that reuse evaluation results at duplicate coordinates ([reference counts](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L807-L810), [count check](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L973-L987)).
- For every recorded invocation, the host requires the diagnostic index to equal `numTEInputs`. A smaller value names the first failing basic subobject through `basicSubobjectAtIndex()`; a larger value is rejected as invalid. The case passes only after these checks and a successful image comparison ([diagnostic scan and final result](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L969-L1017)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `per_patch` | Incorrect matching or transport of singular `patch`-qualified structure/scalar variables. |
| `per_patch_array` | Incorrect matching, indexing, or transport of a `patch`-qualified standalone array. |
| `per_patch_block` | Incorrect matching or member layout/transport for a singular `patch`-qualified interface block. |
| `per_patch_block_array` | Incorrect matching, element indexing, or member transport for an array of `patch`-qualified interface blocks. |
| `per_vertex` | Incorrect invocation-to-element writes or transport of standalone per-vertex structure/scalar arrays. |
| `per_vertex_block` | Incorrect invocation-to-element writes, matching, or nested member transport for a per-vertex interface-block array. |

All six values also depend on the shared shader generator, tessellation execution, SSBO diagnostics, rasterization, synchronization, copyback, and image comparison paths.

### Cause Analysis

#### Singular patch-variable matching or transport

**Possible failure symptoms:** `per_patch` diagnostics name `in_te_s` or `in_te_f`, or the rendered result contains red where the reference is green.

**Possible implementation causes:** Producer and consumer `patch` variables may be matched with the wrong location, type, or patch storage semantics. Vulkan requires equivalent interface decorations and matching type structure across stages ([interface matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L180)).

#### Patch-array matching, indexing, or transport

**Possible failure symptoms:** `per_patch_array` reports one of the three `in_te_f` elements as the first mismatch while singular `per_patch` cases pass.

**Possible implementation causes:** The compiler or stage-interface implementation may preserve the base location but calculate an incorrect array element location or index. The source emits and checks all three elements in order, so the returned path distinguishes which element first diverged.

#### Singular patch-block member transport

**Possible failure symptoms:** `per_patch_block` reports `tcBlock`/`teBlock` member paths, possibly inside `blockFa`, `blockSa`, or a nested `z` array.

**Possible implementation causes:** Interface-block matching or composite lowering may assign an incorrect member location, array stride, or nested access path. Source-level investigation should compare the generated SPIR-V producer/consumer interfaces for the named member before assigning the defect to one layer.

#### Patch-block-array element or member transport

**Possible failure symptoms:** `per_patch_block_array` fails at a member of block element 0 or 1 while the singular block form passes.

**Possible implementation causes:** The stage interface may handle the block's members correctly but apply the wrong top-level array element offset or matching rule. The lightweight block choice keeps this case within its intended per-patch component budget, so a failure should be investigated from the named element/member rather than presumed to be a limit overflow.

#### Per-vertex invocation-to-element transport

**Possible failure symptoms:** `per_vertex` returns a path containing the wrong control-point element, often with a sequence shifted at an invocation boundary; the invocation count or image may also fail.

**Possible implementation causes:** A control invocation may write the wrong `gl_InvocationID` element, or the evaluation-stage per-vertex input array may not map the five output control points correctly. The shader source writes each invocation's own element and the specification defines one control-shader invocation per output vertex ([control-shader execution](../../../../vulkan-docs/src/chapters/shaders.adoc#L2642-L2665)).

#### Per-vertex block indexing and nested transport

**Possible failure symptoms:** `per_vertex_block` reports a block member nested beneath one of the five control-point elements. Standalone per-vertex cases may pass if only block lowering is affected.

**Possible implementation causes:** The implementation may combine an incorrect per-vertex array index with an incorrect interface-block member path. The diagnostic identifies the first basic subobject, but producer and consumer SPIR-V must be inspected to separate array-index lowering from block-member matching.

#### Shared execution or result-observation path

**Possible failure symptoms:** Many or all IO forms have too few invocations, invalid diagnostic indices, a fully incorrect image, or an image failure with no named input mismatch.

**Possible implementation causes:** Shared setup and observation mechanisms include tessellation-level transport, tessellator execution, evaluation-stage SSBO atomics, rasterization, image copyback, host invalidation, and reference-image comparison. The source exposes multiple signals, so investigation should first separate a diagnostic mismatch from an invocation-count or image-only failure.

## Case Pruning

### Requirement-based pruning

- Runtime execution requires `tessellationShader` and `vertexPipelineStoresAndAtomics`; a device without either feature reports the case as unsupported ([feature requirement](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L792-L796)).
- Under `VK_KHR_portability_subset`, isoline cases require the portability feature for tessellation isolines. [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L473-L476) delegates this primitive check to the shared tessellation utility ([utility check](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L537-L549)).
- The explicit `32` declaration relies only on the required minimum `maxTessellationPatchSize`, so the test does not need a device-specific larger value ([limit definition and minimum](../../../../vulkan-docs/src/chapters/limits.adoc#L430-L458), [minimum table](../../../../vulkan-docs/src/chapters/limits.adoc#L6622-L6632)).

### Design-based pruning

- The generator does not place an array member inside the standalone output structure. Its source marks that declaration as illegal and adds the nested `z[2]` member only for block forms ([structure construction](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L514-L527)).
- `per_patch_array` omits the standalone structure variable, leaving the float array as its legal arrayed standalone form ([variable selection](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L547-L563)).
- `per_patch_block_array` omits `blockS` to keep the generated array of blocks within limited per-patch storage. It retains other scalar, array, and nested-structure members ([block selection](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L528-L545)).
- Negative shader-compilation cases from the related GLES tests were not ported because this Vulkan shader-library path cannot represent expected compilation failure ([registration note](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1027-L1031)). This is a suite-scope exclusion, not runtime pruning.

## Key Takeaways

- The six IO forms are the core behavior choices. Together they cover patch-wide and control-point-specific ownership, top-level arrays, structures, and interface blocks.
- The three array-size spellings test declaration equivalence. Explicit capacity does not change the five per-vertex values produced and checked.
- Device-side comparison provides an exact first-failure index, while invocation count and reference-image comparison catch broader tessellation or rendering failures.
- The generator avoids illegal or over-budget declaration combinations instead of treating their absence as device support behavior.
- See `## Failure Meaning` to interpret form-specific diagnostics and shared observation failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Dimensions and constants | [`Constants`, `IOType`, `VertexIOArraySize`, `CaseDefinition`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L60-L97) | Defines all fixed sizes and matrix dimensions. |
| Recursive generator | [`TopLevelObject` and basic-type traversal](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L102-L243) | Assigns/checks nested basic subobjects and maps diagnostic indices. |
| Declaration models | [`Variable` and `IOBlock`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L245-L452) | Emits standalone and block declarations, traversals, counts, and names. |
| Case construction | [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L478-L665) | Chooses each concrete interface and deterministic sequence. |
| Generated shader stages | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L668-L770) | Produces the vertex, control, evaluation, and fragment shaders. |
| Runtime and verdict | [`UserDefinedIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L792-L1018) | Builds resources and pipeline, draws, reads back, and checks all signals. |
| Test registration | [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1027-L1087) | Registers six by three by three cases and records the negative-test boundary. |
| Public factory | [`vktTessellationUserDefinedIO.hpp`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.hpp#L30-L36) | Declares the family factory used by category registration. |
| Vulkan interface rules | [User-Defined Variable Interface and Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L104-L180) | Grounds locations, decorations, and matching types. |
| Vulkan tessellation model | [Tessellation Control and Evaluation Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2576-L2681) | Grounds patch ownership and stage invocation roles. |
| Mustpass paths | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L1002-L1055) | Confirms all 54 executable paths. |
| Understanding Brief | [UserDefinedIO_brief.md](UserDefinedIO_brief.md) | Records the source-backed learning model and audit decisions used for this rewrite. |
