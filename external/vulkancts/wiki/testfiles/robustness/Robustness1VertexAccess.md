## Overview

**Core question:** Does robust vertex input access keep valid attributes intact and constrain out-of-range fetches to permitted results across four buffer-layout patterns?

- This page covers the `robustness.robustness1_vertex_access` test family implemented by [`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L92-L134).
- The four test case leaves generate an indexed 3-by-3 triangle grid, deliberately place vertex indices `5`, `6`, `9`, and `10` outside the valid data arrangement, and validate fetched colors in a vertex shader.
- Each case uses a dedicated device with `robustBufferAccess` enabled. The host verdict is an image-wide check that every pixel is `vec4(0, 1, 0, 1)`.
- The page explains the registered leaves, their stride and allocation variations, the shader-side color contract, runtime setup, and what a failure can mean.

## Background Knowledge

For the shared model of bounded resource access and robustness contracts, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **Vertex input addressing.** A vertex input attribute selects a format, byte offset, and binding. The binding supplies a stride and input rate; `VK_VERTEX_INPUT_RATE_VERTEX` advances with the vertex index, while the test cases use the resulting binding addresses to exercise attribute fetch boundaries [Vertex Input Description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L12-L24).

## Registration Hierarchy

```text
robustness.robustness1_vertex_access
├── out_of_bounds_stride_0
├── out_of_bounds_stride_16_single_buffer
├── out_of_bounds_stride_30_middle_of_buffer
└── out_of_bounds_stride_8_middle_of_buffer_separate
```

The group is created by `createRobustness1VertexAccessTests(testCtx)` and adds the four leaves from `robustness1Tests` [registration](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L210), [factory](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951). The same four paths are present in the inspected default mustpass list [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `out_of_bounds_stride_0`, `out_of_bounds_stride_16_single_buffer`, `out_of_bounds_stride_30_middle_of_buffer`, `out_of_bounds_stride_8_middle_of_buffer_separate` | Selects the vertex-buffer stride, allocation, and binding arrangement used to expose an out-of-range fetch. | [`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389) |
| Grid | `3 x 3` tiles; `(3 + 1) * (3 + 1)` vertices | Creates a small indexed triangle mesh with sixteen logical vertex positions. | [`GetVerticesCountForTriangles()` and `GenerateTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L391-L456) |
| Invalid logical vertex indices | `5`, `6`, `9`, `10` | Moves these logical vertices to the end of the generated allocation so their attribute fetches cross the shortened valid range. | [`GenerateTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L396-L423) |
| Vertex attribute format | `VK_FORMAT_R32G32B32A32_SFLOAT` | Gives positions and colors a common four-component floating-point representation. | Attribute descriptions in the four leaves, for example [`out_of_bounds_stride_0`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L234-L240) |
| Render target | `12 x 12` pixels | Provides the color attachment used for the final all-green result check. | [`renderTargetSize`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L195-L202) |
| Draw mode | Indexed draw with a `uint32` index buffer | All four observed leaves pass generated indices to `vkCmdDrawIndexed`. | [`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L731-L750) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each value keeps the same mesh and shader contract but changes how vertex bindings and valid ranges expose out-of-range access.

### `out_of_bounds_stride_0` — zero-stride auxiliary color binding

Positions use a normal vertex-rate binding, while one color binding has stride `0` and contains one expected color. A separate color structure binding is shortened so the invalid logical vertices can fetch beyond its valid range [case setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L210-L251).

### `out_of_bounds_stride_16_single_buffer` — shortened binding into one allocation

A single `Vertex` allocation contains position, unused, and two color members. Two bindings use `sizeof(Vertex)` stride, but the second binding is shortened before its `color2` member, testing an out-of-range attribute read through a shared underlying allocation [case setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L252-L293).

### `out_of_bounds_stride_30_middle_of_buffer` — padded middle access

A padded `Vertex` array is bound with attribute offsets that include the padding start. The second binding is shortened by the number of invalid indices, so the selected color attributes reach beyond that binding's valid range while remaining inside the larger allocation [case setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L294-L346).

### `out_of_bounds_stride_8_middle_of_buffer_separate` — separate padded position and color arrays

Positions and colors are stored in separate padded arrays. Padding is initialized with `unusedColor` because an out-of-range access may return a value from within the bound memory range; the shader therefore accepts that value but rejects the sentinel `outOfRangeColor` [case setup and note](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L347-L389).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.robustness.robustness1_vertex_access.out_of_bounds_stride_0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `out_of_bounds_stride_0` | Uses a zero-stride color binding together with a shortened color structure binding, while positions use a vertex-rate binding. |
| `3 x 3` tile grid with invalid logical indices `5`, `6`, `9`, `10` | Places the invalid vertices at the end of the generated records so their color attributes exercise the shortened binding range. |

#### Purpose

This vertex shader checks the colors fetched for valid and deliberately out-of-range vertex records. It emits green when both colors satisfy the appropriate accepted-color set, allowing the host to reduce the result to an all-green image check.

#### Structural Design

| Shader phase | Operation | Result |
|--------------|-----------|--------|
| Inputs | Read `in_position`, `in_color0`, and `in_color1`. | The position `z` component identifies whether the generated vertex is valid. |
| Color predicates | Apply the generated one-sided test `component - reference < 0.00001` for each component and each listed reference color. | Values sufficiently above a reference component are rejected; values below it are not bounded by this predicate. |
| Validation | For valid vertices, require both colors to pass `is_valid`; otherwise require both to pass `is_invalid`. | The invocation receives a Boolean result, but this source predicate is weaker than an absolute-difference comparison. |
| Outputs | Select green on success or `in_color0` on failure, then write the position from `in_position.xy`. | Failed classifications remain visible in the rendered image. |

#### Shader Code

```glsl
#version 310 es
precision highp float;
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color0;
layout(location = 2) in vec4 in_color1;
layout(location = 0) out vec4 out_color;
bool is_valid(vec4 color)
{
  return
    (color.r - 0.25000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.75000 < 0.00001 && color.a - 1.00000 < 0.00001) ||
    (color.r - 0.75000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.25000 < 0.00001 && color.a - 1.00000 < 0.00001);
}
bool is_invalid(vec4 color)
{
  return
    (color.r - 0.25000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.75000 < 0.00001 && color.a - 1.00000 < 0.00001) ||
    (color.r - 0.75000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.25000 < 0.00001 && color.a - 1.00000 < 0.00001) ||
    (color.r - 0.00000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.00000 < 0.00001 && color.a - 0.00000 < 0.00001) ||
    (color.r - 0.00000 < 0.00001 && color.g - 0.00000 < 0.00001 && color.b - 0.00000 < 0.00001 && color.a - 1.00000 < 0.00001);
}
bool validate(bool should_be_valid, vec4 color0, vec4 color1)
{
  return (should_be_valid && is_valid(color0) && is_valid(color1)) || (is_invalid(color0) && is_invalid(color1));
}
void main()
{
  out_color = validate(in_position.z >= 1.0, in_color0, in_color1) ? vec4(0,1,0,1) : in_color0;  gl_Position = vec4(in_position.xy, 0.0, 1.0);
}
```

#### Additional Info

- The source uses the same generated vertex and fragment shader programs for the four registered leaves; the selected path changes vertex-buffer bindings, attribute offsets, and valid ranges rather than shader text [shader generation and case setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case leaf | The shader interface and validation logic stay fixed; each leaf changes the vertex-buffer layout and the range from which the same inputs are fetched. | [registered leaf definitions](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389) |

#### SPIR-V

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
; Bound: 266
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %out_color %in_position %in_color0 %in_color1 %_
               OpSource ESSL 310
               OpName %main "main"
               OpName %is_valid_vf4_ "is_valid(vf4;"
               OpName %color "color"
               OpName %is_invalid_vf4_ "is_invalid(vf4;"
               OpName %color_0 "color"
               OpName %validate_b1_vf4_vf4_ "validate(b1;vf4;vf4;"
               OpName %should_be_valid "should_be_valid"
               OpName %color0 "color0"
               OpName %color1 "color1"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %param_1 "param"
               OpName %param_2 "param"
               OpName %out_color "out_color"
               OpName %in_position "in_position"
               OpName %in_color0 "in_color0"
               OpName %in_color1 "in_color1"
               OpName %param_3 "param"
               OpName %param_4 "param"
               OpName %param_5 "param"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpDecorate %out_color Location 0
               OpDecorate %in_position Location 0
               OpDecorate %in_color0 Location 1
               OpDecorate %in_color1 Location 2
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
       %bool = OpTypeBool
         %10 = OpTypeFunction %bool %_ptr_Function_v4float
%_ptr_Function_bool = OpTypePointer Function %bool
         %18 = OpTypeFunction %bool %_ptr_Function_bool %_ptr_Function_v4float %_ptr_Function_v4float
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
 %float_0_25 = OpConstant %float 0.25
%float_9_99999975en06 = OpConstant %float 9.99999975e-06
     %uint_1 = OpConstant %uint 1
    %float_0 = OpConstant %float 0
     %uint_2 = OpConstant %uint 2
 %float_0_75 = OpConstant %float 0.75
     %uint_3 = OpConstant %uint 3
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Input_float = OpTypePointer Input %float
  %in_color0 = OpVariable %_ptr_Input_v4float Input
  %in_color1 = OpVariable %_ptr_Input_v4float Input
        %249 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
     %v4bool = OpTypeVector %bool 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v2float = OpTypeVector %float 2
       %main = OpFunction %void None %3
          %5 = OpLabel
    %param_3 = OpVariable %_ptr_Function_bool Function
    %param_4 = OpVariable %_ptr_Function_v4float Function
    %param_5 = OpVariable %_ptr_Function_v4float Function
        %238 = OpAccessChain %_ptr_Input_float %in_position %uint_2
        %239 = OpLoad %float %238
        %240 = OpFOrdGreaterThanEqual %bool %239 %float_1
               OpStore %param_3 %240
        %245 = OpLoad %v4float %in_color0
               OpStore %param_4 %245
        %247 = OpLoad %v4float %in_color1
               OpStore %param_5 %247
        %248 = OpFunctionCall %bool %validate_b1_vf4_vf4_ %param_3 %param_4 %param_5
        %250 = OpLoad %v4float %in_color0
        %252 = OpCompositeConstruct %v4bool %248 %248 %248 %248
        %253 = OpSelect %v4float %252 %249 %250
               OpStore %out_color %253
        %260 = OpLoad %v4float %in_position
        %261 = OpVectorShuffle %v2float %260 %260 0 1
        %262 = OpCompositeExtract %float %261 0
        %263 = OpCompositeExtract %float %261 1
        %264 = OpCompositeConstruct %v4float %262 %263 %float_0 %float_1
        %265 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %265 %264
               OpReturn
               OpFunctionEnd
%is_valid_vf4_ = OpFunction %bool None %10
      %color = OpFunctionParameter %_ptr_Function_v4float
         %13 = OpLabel
         %27 = OpAccessChain %_ptr_Function_float %color %uint_0
         %28 = OpLoad %float %27
         %30 = OpFSub %float %28 %float_0_25
         %32 = OpFOrdLessThan %bool %30 %float_9_99999975en06
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
         %36 = OpAccessChain %_ptr_Function_float %color %uint_1
         %37 = OpLoad %float %36
         %39 = OpFSub %float %37 %float_0
         %40 = OpFOrdLessThan %bool %39 %float_9_99999975en06
               OpBranch %34
         %34 = OpLabel
         %41 = OpPhi %bool %32 %13 %40 %33
               OpSelectionMerge %43 None
               OpBranchConditional %41 %42 %43
         %42 = OpLabel
         %45 = OpAccessChain %_ptr_Function_float %color %uint_2
         %46 = OpLoad %float %45
         %48 = OpFSub %float %46 %float_0_75
         %49 = OpFOrdLessThan %bool %48 %float_9_99999975en06
               OpBranch %43
         %43 = OpLabel
         %50 = OpPhi %bool %41 %34 %49 %42
               OpSelectionMerge %52 None
               OpBranchConditional %50 %51 %52
         %51 = OpLabel
         %54 = OpAccessChain %_ptr_Function_float %color %uint_3
         %55 = OpLoad %float %54
         %57 = OpFSub %float %55 %float_1
         %58 = OpFOrdLessThan %bool %57 %float_9_99999975en06
               OpBranch %52
         %52 = OpLabel
         %59 = OpPhi %bool %50 %43 %58 %51
         %60 = OpLogicalNot %bool %59
               OpSelectionMerge %62 None
               OpBranchConditional %60 %61 %62
         %61 = OpLabel
         %63 = OpAccessChain %_ptr_Function_float %color %uint_0
         %64 = OpLoad %float %63
         %65 = OpFSub %float %64 %float_0_75
         %66 = OpFOrdLessThan %bool %65 %float_9_99999975en06
               OpSelectionMerge %68 None
               OpBranchConditional %66 %67 %68
         %67 = OpLabel
         %69 = OpAccessChain %_ptr_Function_float %color %uint_1
         %70 = OpLoad %float %69
         %71 = OpFSub %float %70 %float_0
         %72 = OpFOrdLessThan %bool %71 %float_9_99999975en06
               OpBranch %68
         %68 = OpLabel
         %73 = OpPhi %bool %66 %61 %72 %67
               OpSelectionMerge %75 None
               OpBranchConditional %73 %74 %75
         %74 = OpLabel
         %76 = OpAccessChain %_ptr_Function_float %color %uint_2
         %77 = OpLoad %float %76
         %78 = OpFSub %float %77 %float_0_25
         %79 = OpFOrdLessThan %bool %78 %float_9_99999975en06
               OpBranch %75
         %75 = OpLabel
         %80 = OpPhi %bool %73 %68 %79 %74
               OpSelectionMerge %82 None
               OpBranchConditional %80 %81 %82
         %81 = OpLabel
         %83 = OpAccessChain %_ptr_Function_float %color %uint_3
         %84 = OpLoad %float %83
         %85 = OpFSub %float %84 %float_1
         %86 = OpFOrdLessThan %bool %85 %float_9_99999975en06
               OpBranch %82
         %82 = OpLabel
         %87 = OpPhi %bool %80 %75 %86 %81
               OpBranch %62
         %62 = OpLabel
         %88 = OpPhi %bool %59 %52 %87 %82
               OpReturnValue %88
               OpFunctionEnd
%is_invalid_vf4_ = OpFunction %bool None %10
    %color_0 = OpFunctionParameter %_ptr_Function_v4float
         %16 = OpLabel
         %91 = OpAccessChain %_ptr_Function_float %color_0 %uint_0
         %92 = OpLoad %float %91
         %93 = OpFSub %float %92 %float_0_25
         %94 = OpFOrdLessThan %bool %93 %float_9_99999975en06
               OpSelectionMerge %96 None
               OpBranchConditional %94 %95 %96
         %95 = OpLabel
         %97 = OpAccessChain %_ptr_Function_float %color_0 %uint_1
         %98 = OpLoad %float %97
         %99 = OpFSub %float %98 %float_0
        %100 = OpFOrdLessThan %bool %99 %float_9_99999975en06
               OpBranch %96
         %96 = OpLabel
        %101 = OpPhi %bool %94 %16 %100 %95
               OpSelectionMerge %103 None
               OpBranchConditional %101 %102 %103
        %102 = OpLabel
        %104 = OpAccessChain %_ptr_Function_float %color_0 %uint_2
        %105 = OpLoad %float %104
        %106 = OpFSub %float %105 %float_0_75
        %107 = OpFOrdLessThan %bool %106 %float_9_99999975en06
               OpBranch %103
        %103 = OpLabel
        %108 = OpPhi %bool %101 %96 %107 %102
               OpSelectionMerge %110 None
               OpBranchConditional %108 %109 %110
        %109 = OpLabel
        %111 = OpAccessChain %_ptr_Function_float %color_0 %uint_3
        %112 = OpLoad %float %111
        %113 = OpFSub %float %112 %float_1
        %114 = OpFOrdLessThan %bool %113 %float_9_99999975en06
               OpBranch %110
        %110 = OpLabel
        %115 = OpPhi %bool %108 %103 %114 %109
        %116 = OpLogicalNot %bool %115
               OpSelectionMerge %118 None
               OpBranchConditional %116 %117 %118
        %117 = OpLabel
        %119 = OpAccessChain %_ptr_Function_float %color_0 %uint_0
        %120 = OpLoad %float %119
        %121 = OpFSub %float %120 %float_0_75
        %122 = OpFOrdLessThan %bool %121 %float_9_99999975en06
               OpSelectionMerge %124 None
               OpBranchConditional %122 %123 %124
        %123 = OpLabel
        %125 = OpAccessChain %_ptr_Function_float %color_0 %uint_1
        %126 = OpLoad %float %125
        %127 = OpFSub %float %126 %float_0
        %128 = OpFOrdLessThan %bool %127 %float_9_99999975en06
               OpBranch %124
        %124 = OpLabel
        %129 = OpPhi %bool %122 %117 %128 %123
               OpSelectionMerge %131 None
               OpBranchConditional %129 %130 %131
        %130 = OpLabel
        %132 = OpAccessChain %_ptr_Function_float %color_0 %uint_2
        %133 = OpLoad %float %132
        %134 = OpFSub %float %133 %float_0_25
        %135 = OpFOrdLessThan %bool %134 %float_9_99999975en06
               OpBranch %131
        %131 = OpLabel
        %136 = OpPhi %bool %129 %124 %135 %130
               OpSelectionMerge %138 None
               OpBranchConditional %136 %137 %138
        %137 = OpLabel
        %139 = OpAccessChain %_ptr_Function_float %color_0 %uint_3
        %140 = OpLoad %float %139
        %141 = OpFSub %float %140 %float_1
        %142 = OpFOrdLessThan %bool %141 %float_9_99999975en06
               OpBranch %138
        %138 = OpLabel
        %143 = OpPhi %bool %136 %131 %142 %137
               OpBranch %118
        %118 = OpLabel
        %144 = OpPhi %bool %115 %110 %143 %138
        %145 = OpLogicalNot %bool %144
               OpSelectionMerge %147 None
               OpBranchConditional %145 %146 %147
        %146 = OpLabel
        %148 = OpAccessChain %_ptr_Function_float %color_0 %uint_0
        %149 = OpLoad %float %148
        %150 = OpFSub %float %149 %float_0
        %151 = OpFOrdLessThan %bool %150 %float_9_99999975en06
               OpSelectionMerge %153 None
               OpBranchConditional %151 %152 %153
        %152 = OpLabel
        %154 = OpAccessChain %_ptr_Function_float %color_0 %uint_1
        %155 = OpLoad %float %154
        %156 = OpFSub %float %155 %float_0
        %157 = OpFOrdLessThan %bool %156 %float_9_99999975en06
               OpBranch %153
        %153 = OpLabel
        %158 = OpPhi %bool %151 %146 %157 %152
               OpSelectionMerge %160 None
               OpBranchConditional %158 %159 %160
        %159 = OpLabel
        %161 = OpAccessChain %_ptr_Function_float %color_0 %uint_2
        %162 = OpLoad %float %161
        %163 = OpFSub %float %162 %float_0
        %164 = OpFOrdLessThan %bool %163 %float_9_99999975en06
               OpBranch %160
        %160 = OpLabel
        %165 = OpPhi %bool %158 %153 %164 %159
               OpSelectionMerge %167 None
               OpBranchConditional %165 %166 %167
        %166 = OpLabel
        %168 = OpAccessChain %_ptr_Function_float %color_0 %uint_3
        %169 = OpLoad %float %168
        %170 = OpFSub %float %169 %float_1
        %171 = OpFOrdLessThan %bool %170 %float_9_99999975en06
               OpBranch %167
        %167 = OpLabel
        %172 = OpPhi %bool %165 %160 %171 %166
               OpBranch %147
        %147 = OpLabel
        %173 = OpPhi %bool %144 %118 %172 %167
        %174 = OpLogicalNot %bool %173
               OpSelectionMerge %176 None
               OpBranchConditional %174 %175 %176
        %175 = OpLabel
        %177 = OpAccessChain %_ptr_Function_float %color_0 %uint_0
        %178 = OpLoad %float %177
        %179 = OpFSub %float %178 %float_0
        %180 = OpFOrdLessThan %bool %179 %float_9_99999975en06
               OpSelectionMerge %182 None
               OpBranchConditional %180 %181 %182
        %181 = OpLabel
        %183 = OpAccessChain %_ptr_Function_float %color_0 %uint_1
        %184 = OpLoad %float %183
        %185 = OpFSub %float %184 %float_0
        %186 = OpFOrdLessThan %bool %185 %float_9_99999975en06
               OpBranch %182
        %182 = OpLabel
        %187 = OpPhi %bool %180 %175 %186 %181
               OpSelectionMerge %189 None
               OpBranchConditional %187 %188 %189
        %188 = OpLabel
        %190 = OpAccessChain %_ptr_Function_float %color_0 %uint_2
        %191 = OpLoad %float %190
        %192 = OpFSub %float %191 %float_0
        %193 = OpFOrdLessThan %bool %192 %float_9_99999975en06
               OpBranch %189
        %189 = OpLabel
        %194 = OpPhi %bool %187 %182 %193 %188
               OpSelectionMerge %196 None
               OpBranchConditional %194 %195 %196
        %195 = OpLabel
        %197 = OpAccessChain %_ptr_Function_float %color_0 %uint_3
        %198 = OpLoad %float %197
        %199 = OpFSub %float %198 %float_1
        %200 = OpFOrdLessThan %bool %199 %float_9_99999975en06
               OpBranch %196
        %196 = OpLabel
        %201 = OpPhi %bool %194 %189 %200 %195
               OpBranch %176
        %176 = OpLabel
        %202 = OpPhi %bool %173 %147 %201 %196
               OpReturnValue %202
               OpFunctionEnd
%validate_b1_vf4_vf4_ = OpFunction %bool None %18
%should_be_valid = OpFunctionParameter %_ptr_Function_bool
     %color0 = OpFunctionParameter %_ptr_Function_v4float
     %color1 = OpFunctionParameter %_ptr_Function_v4float
         %23 = OpLabel
      %param = OpVariable %_ptr_Function_v4float Function
    %param_0 = OpVariable %_ptr_Function_v4float Function
    %param_1 = OpVariable %_ptr_Function_v4float Function
    %param_2 = OpVariable %_ptr_Function_v4float Function
        %205 = OpLoad %bool %should_be_valid
               OpSelectionMerge %207 None
               OpBranchConditional %205 %206 %207
        %206 = OpLabel
        %209 = OpLoad %v4float %color0
               OpStore %param %209
        %210 = OpFunctionCall %bool %is_valid_vf4_ %param
               OpBranch %207
        %207 = OpLabel
        %211 = OpPhi %bool %205 %23 %210 %206
               OpSelectionMerge %213 None
               OpBranchConditional %211 %212 %213
        %212 = OpLabel
        %215 = OpLoad %v4float %color1
               OpStore %param_0 %215
        %216 = OpFunctionCall %bool %is_valid_vf4_ %param_0
               OpBranch %213
        %213 = OpLabel
        %217 = OpPhi %bool %211 %207 %216 %212
        %218 = OpLogicalNot %bool %217
               OpSelectionMerge %220 None
               OpBranchConditional %218 %219 %220
        %219 = OpLabel
        %222 = OpLoad %v4float %color0
               OpStore %param_1 %222
        %223 = OpFunctionCall %bool %is_invalid_vf4_ %param_1
               OpSelectionMerge %225 None
               OpBranchConditional %223 %224 %225
        %224 = OpLabel
        %227 = OpLoad %v4float %color1
               OpStore %param_2 %227
        %228 = OpFunctionCall %bool %is_invalid_vf4_ %param_2
               OpBranch %225
        %225 = OpLabel
        %229 = OpPhi %bool %223 %219 %228 %224
               OpBranch %220
        %220 = OpLabel
        %230 = OpPhi %bool %217 %213 %229 %225
               OpReturnValue %230
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Before each leaf runs, `Robustness1AccessTest::createInstance()` creates a dedicated device through `createRobustBufferAccessDevice(context)`, which enables `robustBufferAccess` [instance creation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L861-L884), [device helper](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87).
- The helper creates a `VK_FORMAT_R8G8B8A8_UNORM` color image, render pass, framebuffer, host-visible vertex buffers, an index buffer, descriptor state, and one graphics pipeline for the supplied `InputInfo` [resource setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L480-L710).
- `GenerateTriangles()` builds the 3-by-3 grid, remaps invalid logical indices to the final generated records, and emits six indices per tile for triangle-list drawing [mesh generation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L396-L456).
- The command buffer binds each case's pipeline, descriptors, vertex buffers, and index buffer, then submits `vkCmdDrawIndexed` and waits for completion [draw and submission](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L725-L759).
- The vertex shader applies its generated one-sided component predicates using `validColors` or `invalidColors`. The fragment shader copies the vertex result to the color attachment [shader generation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L940).
- The host reads the color attachment and requires every pixel to equal `vec4(0, 1, 0, 1)`. The first mismatch logs the result image and returns `TestStatus::fail("Image comparison failed.")` [result check](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L761-L779).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `out_of_bounds_stride_0` | Incorrect bounds handling for a zero-stride binding or shortened structure binding. |
| `out_of_bounds_stride_16_single_buffer` | Incorrect bounds handling when two bindings address one allocation and one ends inside a record. |
| `out_of_bounds_stride_30_middle_of_buffer` | Incorrect bounds or offset handling for a padded allocation and shortened middle binding. |
| `out_of_bounds_stride_8_middle_of_buffer_separate` | Incorrect robust result handling for separate padded position and color buffers, or rejection of an allowed in-range padding value. |

All four leaves can also expose errors in generated shader classification, vertex attribute extraction, or the final image check.

### Cause Analysis

#### Vertex input bounds and address calculation

**Possible failure symptoms:** A valid vertex produces a color that is not accepted, an invalid vertex produces `outOfRangeColor` or another rejected value, or only one of the two color attributes is classified inconsistently. The rendered image contains a pixel other than green.

**Possible implementation causes:** The implementation may calculate the checked range with the wrong binding stride, attribute offset, binding size, or allocation origin. For the separate and padded cases, it may also mishandle an attribute offset into a padded allocation. The precise cause requires source-level investigation if a failing device cannot be narrowed by the affected leaf.

#### Robust result and same-binding semantics

**Possible failure symptoms:** A fetch beyond the shortened range does not satisfy the generated predicate for `expectedColor`, `unusedColor`, or a zero variant, even though the rest of the shader classification is correct.

**Possible implementation causes:** Robust vertex input behavior may be applied with an incorrect bound-memory range or with a result that the generated shader rejects. The source lists multiple reference outcomes, so a failure does not identify one mandatory replacement value; its one-sided comparisons must also be considered when interpreting what the shader actually rejects [spec rule](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030), [reference colors and generated comparison](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L123-L130).

#### Generated shader or final image validation

**Possible failure symptoms:** The shader fails to turn a valid result green, or a correctly classified vertex result is not propagated to the attachment, causing the all-pixel comparison to fail.

**Possible implementation causes:** A compiler or runtime issue in the generated vertex-stage comparisons, vertex-to-fragment color propagation, or graphics pipeline execution could produce the observed image mismatch. The host-side readback and image comparison are also part of the checked path; source-level investigation is needed to distinguish them from a vertex-fetch failure.

## Case Pruning

### Requirement-based pruning

- The test creates a device with `robustBufferAccess` enabled before executing a leaf [device creation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L861-L884).
- No additional `checkSupport()` override or explicit format/feature gate is present in the inspected source. Other requirements come from the Vulkan graphics operations used by the pipeline setup.
- No case is conditionally removed in the `robustness1Tests` vector; unsupported device creation or setup failures are handled by the normal CTS framework.

### Design-based pruning

- The registered matrix fixes the grid at `3 x 3` tiles and the invalid logical indices at `5`, `6`, `9`, and `10`; it does not enumerate arbitrary tile sizes or invalid-index placements [mesh generation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L391-L456).
- The four leaves intentionally cover distinct buffer layouts: zero stride, a shortened single-allocation binding, padded middle access, and separate padded buffers. Other stride and allocation combinations are outside this test family's registered design [test definitions](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389).

## Key Takeaways

- The four leaves test the same robustness contract through different vertex-buffer layouts rather than through different shader programs.
- The generated shader lists expected, unused, and zero reference colors, but its source comparison is one-sided rather than an absolute-difference equality test. Device failures must be interpreted against that actual predicate.
- `out_of_bounds_stride_8_middle_of_buffer_separate` is deliberately initialized with `unusedColor` in padding because that value may legally be returned from bound memory.
- The test records an indexed graphics draw and reduces the verdict to an all-green `12 x 12` color attachment.
- A failing pixel can implicate vertex-input addressing, robust result selection, generated shader validation, pipeline propagation, or host readback; see `## Failure Meaning` for the bounded interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test inputs and four leaves | [`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L195-L389) | Defines the registered names, buffers, strides, attributes, colors, and invalid indices. |
| Padded allocation helper | [`PaddedAlloc`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L136-L193) | Places recognizable values before and after valid data. |
| Triangle/index generation | [`GenerateTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L391-L456) | Builds the mesh and remaps invalid logical vertices. |
| Graphics setup and draw | [`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L480-L779) | Creates resources, pipelines, submits indexed drawing, and checks the image. |
| Generated shader | [`Robustness1AccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L940) | Defines accepted valid/invalid colors and green-result logic. |
| Test registration | [`createRobustness1VertexAccessTests()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951) | Adds the four leaves under `robustness1_vertex_access`. |
| Robust device helper | [`createRobustBufferAccessDevice()`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87) | Enables `robustBufferAccess` for the test device. |
| Mustpass coverage | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029) | Confirms the four default-profile registered paths. |
| Robust access semantics | [Vulkan specification: Robust Buffer Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030) | Defines the relevant bounds and permitted out-of-range result rules. |
