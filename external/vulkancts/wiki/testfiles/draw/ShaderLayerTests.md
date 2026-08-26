## Overview

**Core question:** Does a graphics pipeline route each primitive to the array layer selected by a vertex or tessellation-evaluation shader through `gl_Layer`?

- `ShaderLayerTests` is implemented by `vktDrawShaderLayerTests.cpp` and registered as the `shader_layer` test family.
- It provides `vertex_shader_<numLayers>` and `tessellation_shader_<numLayers>` test cases.
- Each case renders one colored rectangle per requested layer into a 2D-array color attachment, copies the layers to host memory, and compares them with generated reference images.
- The same implementation is reused under render-pass and dynamic-rendering draw paths. Secondary-command-buffer variants deliberately use a reduced layer-count set.

## Background Knowledge

- `gl_Layer` is the shader `Layer` built-in used to route a primitive to a slice of a layered framebuffer. The Vulkan specification describes `shaderOutputLayer` as the capability that permits Layer output from vertex or tessellation-evaluation shaders; this family additionally requires the `VK_EXT_shader_viewport_index_layer` device functionality in `checkRequirements`.
- A 2D-array image view exposes several same-sized color-image layers to one rendering operation. The layer selected by a primitive is independent of the fragment color written into that layer.
- The vertex and tessellation-evaluation stages see different identifiers. This test derives the layer from `gl_VertexIndex` in one family and from `gl_PrimitiveID` in the other, so the two families exercise stage-specific Layer-output paths.

## Registration Hierarchy

The dispatcher registers the family under `renderpass` and, outside Vulkan SC, under five dynamic-rendering command-buffer modes. The relevant paths are:

```text
draw.renderpass.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.primary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.partial_secondary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.complete_secondary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1
```

`nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` do not contain this family: `vktDrawTests.cpp` omits all non-basic families when nested secondary command buffers are selected. The `<numLayers>` placeholder expands to the exact leaves documented below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader family | `vertex_shader`, `tessellation_shader` | Selects the stage that writes `gl_Layer` and the corresponding graphics pipeline. | [`createShaderLayerTests`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015-L1049) |
| Number of layers, render-pass and primary dynamic-rendering paths | `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `256` | Sets the array-image layer count, rectangle count, draw vertex count, and number of host-side image comparisons. | [`numLayersToTest`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1019-L1021) |
| Number of layers, dynamic-rendering secondary paths | `1`, `3`, `5`, `7`, `256` | The implementation skips odd indices of the source array when `useSecondaryCmdBuffer` is true, reducing the matrix for secondary recording. | [secondary reduction](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1025-L1029) |
| Rendering mode | `renderpass`; `dynamic_rendering.primary_cmd_buff`; `dynamic_rendering.partial_secondary_cmd_buff`; `dynamic_rendering.complete_secondary_cmd_buff` | Selects render-pass objects or dynamic rendering, and whether draw commands are recorded directly or in a secondary command buffer. | [draw dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

## Behavior Parameters

The primary behavioral axis is the shader family. Layer count and command-recording mode vary the same layered-rendering contract; the shader family changes which shader stage produces the Layer output.

### `vertex_shader`: vertex-stage Layer output

The generated vertex shader assigns `gl_Layer = gl_VertexIndex / 6`. Since each rectangle consists of two triangles and six vertices, all vertices of one rectangle select the same layer. It forwards position and color to the fragment shader.

### `tessellation_shader`: tessellation-evaluation-stage Layer output

The generated tessellation-control shader passes a three-vertex patch through and sets all tessellation levels to `1.0`. The tessellation-evaluation shader assigns `gl_Layer = gl_PrimitiveID / 2`, interpolates position and color, and emits the resulting primitive. This validates Layer output after tessellation rather than at the vertex stage.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.shader_layer.tessellation_shader_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass` | Uses the render-pass path; the shader interface and Layer calculation are the same in the dynamic-rendering variants. |
| `tessellation_shader` | Places the tested `gl_Layer` write in tessellation evaluation, after a three-vertex patch has passed through tessellation control. |
| `numLayers = 1` | Creates one array layer and one generated rectangle. The same shader source is used for every layer-count leaf; the host changes the amount of input geometry and the attachment extent in layers. |

#### Purpose

This shader pair checks that a tessellation-evaluation shader can export `gl_Layer` and route each generated primitive to the intended slice of a layered color attachment. The evaluation shader also interpolates position and color so the host can identify the routed rectangle in the readback image.

#### Structural Design

| Stage and phase | Source operation | Role in the observed result |
|-----------------|------------------|-----------------------------|
| Vertex | Copy position and color into the patch inputs. | Supplies the three vertices and their colors to tessellation control. |
| Tessellation control | Pass through the three vertices and set all inner/outer tessellation levels to `1.0` from invocation 0. | Produces one triangle per three-vertex patch with deterministic tessellation. |
| Tessellation evaluation | Set `gl_Layer = gl_PrimitiveID / 2`; barycentrically interpolate position and color. | Selects the array slice and preserves the patch identity in the rendered rectangle. |
| Fragment | Copy the interpolated color to the color attachment. | Makes layer routing and color coverage visible to host comparison. |

#### Shader Code

##### Tessellation Control Shader

```glsl
#version 450

/// One input patch is exactly three vertices, matching the generated triangle-list patch data.
layout(vertices = 3) out;

/// Position is carried by the built-in gl_in block; this user varying carries the per-vertex color.
layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color[];

void main(void)
{
    /// Invocation 0 alone writes the patch tessellation levels; all levels are one for deterministic output.
    if (gl_InvocationID == 0) {
        gl_TessLevelInner[0] = 1.0;
        gl_TessLevelInner[1] = 1.0;
        gl_TessLevelOuter[0] = 1.0;
        gl_TessLevelOuter[1] = 1.0;
        gl_TessLevelOuter[2] = 1.0;
        gl_TessLevelOuter[3] = 1.0;
    }

    /// Every invocation forwards its corresponding patch vertex and color to evaluation.
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    out_color[gl_InvocationID] = in_color[gl_InvocationID];
}
```

##### Tessellation Evaluation Shader

```glsl
#version 450
#extension GL_ARB_shader_viewport_layer_array : require

/// The generated patches are triangles. Equal spacing and clockwise order match the fixed generator branch.
layout(triangles, equal_spacing, cw) in;

/// These three values are the color and position inputs forwarded by tessellation control.
layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color;

void main(void)
{
    /// Two generated triangles represent one rectangle, so primitive IDs are grouped in pairs per layer.
    gl_Layer = gl_PrimitiveID / 2;

    /// Barycentric tessellation coordinates reconstruct the position of the generated vertex.
    gl_Position = gl_in[0].gl_Position * gl_TessCoord.x +
                  gl_in[1].gl_Position * gl_TessCoord.y +
                  gl_in[2].gl_Position * gl_TessCoord.z;

    /// Use the same barycentric weights for the interpolated color visible in the target layer.
    out_color = in_color[0] * gl_TessCoord.x +
                in_color[1] * gl_TessCoord.y +
                in_color[2] * gl_TessCoord.z;
}
```

#### Additional Info

- The tessellation-control shader is fixed across the `tessellation_shader_N` cases: it always forwards three vertices and sets unit tessellation levels. It matters here because it preserves the patch structure on which `gl_PrimitiveID / 2` relies. [Tessellation program generation](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L443)
- The vertex and fragment stages are fixed pass-through stages for this family. The renderer selects `vert_1_2` and `tese_1_2` when the context supports Vulkan 1.2; those sources are identical to `vert` and `tese` but use explicit SPIR-V 1.5 build options. [Module selection](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L638-L654)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `numLayers` | The tessellation-control and tessellation-evaluation source is unchanged. The host emits the corresponding patch data, and `gl_PrimitiveID / 2` maps the resulting pairs of triangles to the available array layers. | [Test registration](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1019-L1047), [tessellation program generation](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L479) |
| `renderpass` versus dynamic rendering | The shader is unchanged; the selected command-recording path changes how the same layered attachment is begun and submitted. | [Renderer draw](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L674-L752) |
| `tessellation_shader` versus `vertex_shader` | The Layer write moves from vertex processing (`gl_VertexIndex / 6`) to tessellation evaluation (`gl_PrimitiveID / 2`), with the tessellation path adding fixed control/evaluation stages. | [Vertex programs](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L349-L391), [tessellation programs](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L479) |

#### SPIR-V

##### Tessellation Control Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tesc`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 67
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %gl_InvocationID %gl_TessLevelInner %gl_TessLevelOuter %gl_out %gl_in %out_color %in_color
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %gl_out "gl_out"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
      %float = OpTypeFloat 32
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_1 = OpConstant %int 1
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
    %v4float = OpTypeVector %float 4
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_uint_3 = OpTypeArray %gl_PerVertex %uint_3
%_ptr_Output__arr_gl_PerVertex_uint_3 = OpTypePointer Output %_arr_gl_PerVertex_uint_3
     %gl_out = OpVariable %_ptr_Output__arr_gl_PerVertex_uint_3 Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Output__arr_v4float_uint_3 = OpTypePointer Output %_arr_v4float_uint_3
  %out_color = OpVariable %_ptr_Output__arr_v4float_uint_3 Output
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Input__arr_v4float_uint_32 = OpTypePointer Input %_arr_v4float_uint_32
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_32 Input
       %main = OpFunction %void None %3
          %5 = OpLabel
          %9 = OpLoad %int %gl_InvocationID
         %12 = OpIEqual %bool %9 %int_0
               OpSelectionMerge %14 None
               OpBranchConditional %12 %13 %14
         %13 = OpLabel
         %23 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %23 %float_1
         %25 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %25 %float_1
         %30 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %30 %float_1
         %31 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %31 %float_1
         %33 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %33 %float_1
         %35 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %35 %float_1
               OpBranch %14
         %14 = OpLabel
         %44 = OpLoad %int %gl_InvocationID
         %50 = OpLoad %int %gl_InvocationID
         %52 = OpAccessChain %_ptr_Input_v4float %gl_in %50 %int_0
         %53 = OpLoad %v4float %52
         %55 = OpAccessChain %_ptr_Output_v4float %gl_out %44 %int_0
               OpStore %55 %53
         %59 = OpLoad %int %gl_InvocationID
         %63 = OpLoad %int %gl_InvocationID
         %64 = OpAccessChain %_ptr_Input_v4float %in_color %63
         %65 = OpLoad %v4float %64
         %66 = OpAccessChain %_ptr_Output_v4float %out_color %59
               OpStore %66 %65
               OpReturn
               OpFunctionEnd
```

</details>

##### Tessellation Evaluation Shader

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
; Bound: 76
; Schema: 0
               OpCapability Tessellation
               OpCapability ShaderViewportIndexLayerEXT
               OpExtension "SPV_EXT_shader_viewport_index_layer"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_Layer %gl_PrimitiveID %_ %gl_in %gl_TessCoord %out_color %in_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCw
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_shader_viewport_layer_array"
               OpName %main "main"
               OpName %gl_Layer "gl_Layer"
               OpName %gl_PrimitiveID "gl_PrimitiveID"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_Layer BuiltIn Layer
               OpDecorate %gl_PrimitiveID BuiltIn PrimitiveId
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Output_int = OpTypePointer Output %int
   %gl_Layer = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_PrimitiveID = OpVariable %_ptr_Input_int Input
      %int_2 = OpConstant %int 2
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
      %int_1 = OpConstant %int 1
     %uint_2 = OpConstant %uint 2
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Input__arr_v4float_uint_32 = OpTypePointer Input %_arr_v4float_uint_32
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_32 Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %11 = OpLoad %int %gl_PrimitiveID
         %13 = OpSDiv %int %11 %int_2
               OpStore %gl_Layer %13
         %29 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %30 = OpLoad %v4float %29
         %36 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %37 = OpLoad %float %36
         %38 = OpVectorTimesScalar %v4float %30 %37
         %40 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %41 = OpLoad %v4float %40
         %42 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %43 = OpLoad %float %42
         %44 = OpVectorTimesScalar %v4float %41 %43
         %45 = OpFAdd %v4float %38 %44
         %46 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %47 = OpLoad %v4float %46
         %49 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
         %50 = OpLoad %float %49
         %51 = OpVectorTimesScalar %v4float %47 %50
         %52 = OpFAdd %v4float %45 %51
         %54 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %54 %52
         %59 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %60 = OpLoad %v4float %59
         %61 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %62 = OpLoad %float %61
         %63 = OpVectorTimesScalar %v4float %60 %62
         %64 = OpAccessChain %_ptr_Input_v4float %in_color %int_1
         %65 = OpLoad %v4float %64
         %66 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %67 = OpLoad %float %66
         %68 = OpVectorTimesScalar %v4float %65 %67
         %69 = OpFAdd %v4float %63 %68
         %70 = OpAccessChain %_ptr_Input_v4float %in_color %int_2
         %71 = OpLoad %v4float %70
         %72 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
         %73 = OpLoad %float %72
         %74 = OpVectorTimesScalar %v4float %71 %73
         %75 = OpFAdd %v4float %69 %74
               OpStore %out_color %75
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case uses a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color image with `numLayers` array layers and a `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view.
- The host generates a grid of rectangles and one deterministic color per layer, clears the target to `(0.5, 0.5, 0.5, 1.0)`, and uploads the vertex data through a host-visible vertex buffer.
- The graphics pipeline uses triangle-list topology for the vertex family and patch-list topology for the tessellation family. It binds the array view as the color attachment.
- Render-pass cases use a framebuffer whose layer count is `numLayers`. Dynamic-rendering cases transition the image, begin rendering with that layer count, draw, and end rendering.
- In secondary modes, the secondary command buffer records the draw; depending on the mode, it either contains only the draw commands or the complete dynamic-rendering instance. The primary command buffer executes it.
- After submission and completion, `copyImageToBuffer` copies the layered image to a host-visible buffer. The host partitions the buffer into one 256x256 image per layer.
- `generateReferenceImage` builds the expected clear-color background plus that layer's rectangle. Every layer is compared with `tcu::floatThresholdCompare` using `Vec4(0.02f)`; any mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_shader` | Incorrect Layer output handling in the vertex path; incorrect per-vertex routing or associated vertex/color processing; layered attachment or image-copy behavior. |
| `tessellation_shader` | Incorrect Layer output handling in the tessellation-evaluation path; patch/primitive processing or tessellation pipeline behavior; layered attachment or image-copy behavior. |

### Cause Analysis

#### Vertex-stage Layer routing

**Possible failure symptoms:** One or more per-layer image comparisons differ from the reference. A rectangle can appear in the wrong layer, be absent, or have incorrect coverage or color.

**Possible implementation causes:** The failure is consistent with incorrect handling of a vertex-stage `Layer` output, incorrect indexing of vertex input, or a problem in the layered attachment path. The CTS check alone does not localize the cause to shader compilation, rasterization, image operations, or host copyback; source-level and implementation-level investigation is needed to distinguish them.

#### Tessellation-evaluation-stage Layer routing

**Possible failure symptoms:** A layer image differs after the tessellation path executes, including missing or misplaced patch-derived rectangles or incorrect interpolated colors.

**Possible implementation causes:** The failure is consistent with incorrect Layer handling after tessellation, primitive-ID interpretation, patch processing, or the shared layered-rendering and readback path. The test does not by itself identify which implementation component is responsible, so source-level investigation is needed before assigning a narrower cause.

## Case Pruning

### Requirement-based pruning

- Every case requires multi-viewport support, `VK_EXT_shader_viewport_index_layer`, at least 256 `maxFramebufferLayers`, and at least 16 `maxViewports`.
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`.
- `tessellation_shader_*` cases require the core `tessellationShader` feature.
- On a Vulkan 1.2-capable context, the test uses the `_1_2` binaries; otherwise it uses the base binaries. Unsupported requirements prevent execution rather than turning into an image-comparison failure.

### Design-based pruning

- Secondary-command-buffer paths skip every odd index in the layer-count array, producing `1`, `3`, `5`, `7`, and `256` instead of all nine values. This is an intentional reduction in the dynamic secondary matrix.
- Nested secondary-command-buffer roots do not register this family because the draw dispatcher retains only `basic` for nested modes.

## Key Takeaways

- The two test-family leaves differ by the stage that writes `gl_Layer`: vertex processing versus tessellation evaluation.
- The expected result is layer-specific, not just one aggregate image: every array layer is copied back and compared independently.
- The `256` case exercises the minimum framebuffer-layer limit, while secondary dynamic-rendering paths intentionally use a smaller layer-count matrix.
- A failure proves that the observed layered image does not match the stage-specific Layer-routing contract; it does not, without further investigation, identify the failing implementation component.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test registration | [`createShaderLayerTests`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015-L1049) | Creates `shader_layer`, exact family prefixes, and layer-count leaves. |
| Vertex program generation | [`initVertexTestPrograms`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L349-L391) | Generates the vertex and fragment shader sources. |
| Tessellation program generation | [`initTessellationTestPrograms`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L479) | Generates vertex, tessellation-control, tessellation-evaluation, and fragment sources. |
| Renderer setup | [`Renderer::Renderer`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L596-L672) | Creates the layered image/view, buffers, shader modules, render-pass objects, and pipeline. |
| Command recording | [`Renderer::draw`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L674-L752) | Implements render-pass, dynamic-rendering, and secondary-command-buffer flows. |
| Requirements | [`checkRequirements`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L863-L881) | Enforces extension, feature, and limit prerequisites. |
| Vertex validation | [`testVertexShader`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L883-L946) | Generates references and compares each vertex-path layer. |
| Tessellation validation | [`testTessellationShader`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L948-L1012) | Generates references and compares each tessellation-path layer. |
| Draw-suite routing | [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Shows which roots receive this family and the nested-secondary exclusion. |
| Rendering-mode roots | [`createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) | Defines the exact render-pass and dynamic-rendering hierarchy. |
| Vulkan feature semantics | [`shaderOutputLayer`](../../../../vulkan-docs/src/chapters/features.adoc#L941-L948) | Documents the Layer capability required by the shader output. |
