## Overview

**Core question:** Do `vkCmdDrawMultiEXT` and `vkCmdDrawMultiIndexedEXT` execute every packed draw correctly across draw counts, strides, indexed offsets, shader stages, views, and command-buffer modes?

- [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L60-L1637) implements the `multi_draw` test family for `VK_EXT_multi_draw`.
- Each case submits an ordered sequence through either the non-indexed or indexed multi-draw command, then compares color and stencil readback against a CPU-generated image.
- Mosaic geometry makes each triangle address a separate pixel. Overlapping geometry uses depth testing so the surviving triangle exposes ordering and repeated-draw behavior.
- The page describes the registered matrix, the generated shaders, the render and readback path, and what a mismatch isolates.

## Background Knowledge

- `vkCmdDrawMultiEXT` records `drawCount` ordinary draw operations from `VkMultiDrawInfoEXT` records. Each record supplies `firstVertex` and `vertexCount`; `stride` gives the byte distance to the next record.
- `vkCmdDrawMultiIndexedEXT` does the indexed equivalent with `VkMultiDrawIndexedInfoEXT`. A non-null `pVertexOffset` overrides each record's `vertexOffset`; a null pointer makes each record's member effective.
- A depth test can make many overlapping primitives produce one visible result, while stencil operations can count fragments that pass the configured stencil test. The test uses both observations because final color alone cannot prove that all intended operations occurred.

## Registration Hierarchy

The parent draw registration adds this family for legacy render passes and for three dynamic-rendering command-buffer arrangements. Secondary-command-buffer variants register a reduced matrix. The family is Vulkan-only: [`CTS_USES_VULKANSC` excludes its declaration](../../../modules/vulkan/draw/vktDrawTests.cpp#L51-L57) and [its registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L120).

```text
draw.renderpass.multi_draw
├── mosaic
└── overlapping

draw.dynamic_rendering.primary_cmd_buff.multi_draw
├── mosaic
└── overlapping

draw.dynamic_rendering.partial_secondary_cmd_buff.multi_draw
└── mosaic

draw.dynamic_rendering.complete_secondary_cmd_buff.multi_draw
└── mosaic
```

The parent does not add the family beneath either nested-secondary-command-buffer group. `createChildren()` omits it when `nestedSecondaryCmdBuffer` is set.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Mesh layout | `mosaic`, `overlapping` | Separates per-pixel draw placement from depth-selected full-screen overlap. | [mesh registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1402-L1409) |
| Command form | `normal`; `indexed_mixed`, `indexed_random`, `indexed_packed` | Chooses `vkCmdDrawMultiEXT` or `vkCmdDrawMultiIndexedEXT`, and exercises record-supplied, common-pointer, and packed indexed offsets. | [draw and offset registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1411-L1429) |
| Draw count | `no_draws`, `one_draw`, `16_draws`, `max_draws` | Checks zero, one, several, and 1024 draw records. `1024` is the minimum permitted `maxMultiDrawCount`. | [count registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1431-L1440) |
| Record stride | `stride_zero`, `standard_stride`, `stride_extra_4`, `stride_extra_12` | Checks zero stride where no record advancement is needed, the base record layout, and valid padding between records. | [stride registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1442-L1451) |
| Instance range | `no_instances`, `1_instance`, `10_instances`, `2_instances_base_3` | Exercises zero instances, multiple instances, and a nonzero `firstInstance`. | [instance registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1453-L1463) |
| Shader-stage path | `vert_only`, `with_geom`, `with_tess`, `tess_geom` | Carries the generated integer value through optional geometry and tessellation stages. | [shader registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1465-L1475) |
| View and draw ID | `single_view`, `multiview`; `no_offset`, `no_offset_no_draw_id`, and indexed `offset_6`, `offset_6_no_draw_id` | Makes output depend on `gl_ViewIndex` when applicable and on `gl_DrawID` or a primitive-derived fallback. | [view and draw-ID registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1477-L1493) |

The source removes invalid or unhelpful combinations while it builds the hierarchy. Normal draws have no indexed-offset form; indexed draws always have one. Multi-record cases must use a four-byte-aligned stride at least as large as the applicable record. Overlapping cases omit instance counts above one.

## Behavior Parameters

The primary behavior axis is the mesh layout. It changes how the test makes the effects of the submitted sequence observable. Command form, count, stride, instances, shader stages, views, and offsets then stress that observation under different registered configurations.

### `mosaic`: independently placed triangles

The generator places one small triangle around each pixel center in a 32 by 32 target. A correct sequence distributes triangles according to the packed records, so the reference can identify which draw or primitive produced every pixel.

### `overlapping`: depth-selected full-screen triangles

The generator gives 1024 full-screen triangles decreasing depths. Depth testing retains the expected frontmost result, while stencil records the number of relevant fragments. This layout exposes ordering, depth, and draw-count effects without requiring a different output geometry for each triangle.

## Shader Analysis

`MultiDrawTest::initPrograms` generates a stage chain rather than loading fixed shader files. The representative case below selects the multiview, draw-ID, tessellation-plus-geometry path. The vertex stage computes the per-draw/per-instance/per-view payload; tessellation and geometry preserve it while preserving the triangle; the fragment stage flatly copies it into the unsigned color attachment. The payload is an observer for multi-draw execution: the host independently checks color and stencil results, so a mismatch can expose record selection, draw identity, instance/view routing, or stage-interface handling.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.multi_draw.mosaic.indexed_mixed.16_draws.standard_stride.10_instances.tess_geom.multiview.no_offset
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `mosaic` | The host creates one small triangle around each pixel center, making the encoded primitive/draw value spatially observable. |
| `indexed_mixed` + `no_offset` | The command is `vkCmdDrawMultiIndexedEXT`; records use mixed per-record offsets, while the command-wide `pVertexOffset` is null. This changes vertex/primitive placement, not shader source. |
| `16_draws` + `standard_stride` | Sixteen packed records divide the 1024 triangles into equal blocks and use the base `VkMultiDrawIndexedInfoEXT` stride. |
| `10_instances` + `tess_geom` | The vertex built-in `gl_InstanceIndex` varies the blue channel, while tessellation control/evaluation and geometry stages must preserve the payload and position. |
| `multiview` + `no_offset` test leaf | Two view layers are rendered; `gl_ViewIndex` changes alpha. The unsuffixed leaf enables `gl_DrawID`, so red/green encode the command-provided draw index. |

#### Purpose

This shader chain turns each multi-draw invocation's built-in identity into an exact unsigned color value and carries it through the optional stages. The independent stencil comparison confirms that the expected fragments were produced, while the color comparison confirms which draw, instance, and view produced them.

#### Structural Design

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Vertex | `inPos` and `gl_DrawID`, `gl_InstanceIndex`, `gl_ViewIndex` | Copy position; pack draw ID (or the no-draw-ID primitive fallback), `255 - instance`, and `255 - view` into four unsigned channels | Location 0 `uvec4` plus `gl_Position` |
| Tessellation control (when selected) | Three vertex positions and colors | Set all tessellation levels to 1; copy each invocation's position and color | Three-vertex patch and per-vertex `uvec4` |
| Tessellation evaluation (when selected) | Patch positions and colors | Barycentrically reconstruct position; select patch input 0 for the flat payload | Position and flat-compatible `uvec4` |
| Geometry (when selected) | One triangle and three colors | Emit the three input vertices in a triangle strip, preserving position/color pairs | Rasterizable triangle and `uvec4` |
| Fragment | Flat location 0 `uvec4` | Copy the payload without arithmetic or filtering | Unsigned location 0 color |

#### Shader Code

##### Vertex Shader

```glsl
#version 460
/// Multiview is enabled only for the multiview parameter branch; the selected case uses gl_ViewIndex.
#extension GL_EXT_multiview : enable

/// Vulkan's built-in output block carries clip-space position to rasterization.
out gl_PerVertex
{
    vec4 gl_Position;
};

/// Host-uploaded triangle position; the host creates one triangle per 32x32 pixel.
layout (location=0) in vec4 inPos;
/// Integer payload sent to the next graphics stage without interpolation.
layout (location=0) out uvec4 outColor;

void main()
{
    /// Position is test geometry; all multi-draw observability is in the integer payload.
    gl_Position = inPos;
    /// The selected leaf uses gl_DrawID. The no-draw-ID branch substitutes gl_VertexIndex / 3.
    const uint storedIndex = uint(gl_DrawID);
    /// Split the selected draw/primitive value into two independently comparable bytes.
    outColor.r = ((storedIndex >> 8u) & 0xFFu);
    outColor.g = ((storedIndex      ) & 0xFFu);
    /// Instance index includes firstInstance and therefore exposes instance routing.
    outColor.b = 255u - uint(gl_InstanceIndex);
    /// Each multiview layer gets a distinct alpha byte; the single-view branch emits 255.
    outColor.a = 255u - uint(gl_ViewIndex);
}
```

##### Tessellation Control Shader

```glsl
#version 460

/// Each generated input triangle is one three-control-point patch.
layout (vertices=3) out;
/// Position input from the vertex stage.
in gl_PerVertex
{
    vec4 gl_Position;
} gl_in[gl_MaxPatchVertices];
/// Position output to tessellation evaluation.
out gl_PerVertex
{
    vec4 gl_Position;
} gl_out[];

/// Per-control-point integer payload from the vertex stage.
layout (location=0) in uvec4 inColor[gl_MaxPatchVertices];
/// Per-control-point payload forwarded unchanged.
layout (location=0) out uvec4 outColor[];

void main (void)
{
    /// Unit levels preserve one triangle while still exercising the tessellation path.
    gl_TessLevelInner[0] = 1.0;
    gl_TessLevelInner[1] = 1.0;
    gl_TessLevelOuter[0] = 1.0;
    gl_TessLevelOuter[1] = 1.0;
    gl_TessLevelOuter[2] = 1.0;
    gl_TessLevelOuter[3] = 1.0;
    /// Keep each invocation's position and payload aligned by gl_InvocationID.
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    outColor[gl_InvocationID] = inColor[gl_InvocationID];
}
```

##### Tessellation Evaluation Shader

```glsl
#version 460

/// The generated patch is evaluated as a clockwise triangle.
layout (triangles, fractional_odd_spacing, cw) in;
in gl_PerVertex
{
    vec4 gl_Position;
} gl_in[gl_MaxPatchVertices];
out gl_PerVertex
{
    vec4 gl_Position;
};

/// The payload is constant over the generated primitive; the first control point is used.
layout (location=0) in uvec4 inColor[gl_MaxPatchVertices];
layout (location=0) out uvec4 outColor;

void main (void)
{
    /// Reconstruct the position from the three patch corners using tessellation barycentrics.
    gl_Position = (gl_TessCoord.x * gl_in[0].gl_Position) +
                  (gl_TessCoord.y * gl_in[1].gl_Position) +
                  (gl_TessCoord.z * gl_in[2].gl_Position);
    outColor = inColor[0];
}
```

##### Geometry Shader

```glsl
#version 460

/// The selected geometry branch consumes triangles and emits exactly one equivalent triangle.
layout (triangles) in;
layout (triangle_strip, max_vertices=3) out;
in gl_PerVertex
{
    vec4 gl_Position;
} gl_in[3];
out gl_PerVertex
{
    vec4 gl_Position;
};

/// Per-vertex payload received from the preceding stage.
layout (location=0) in uvec4 inColor[3];
/// Flat interpolation is established by the fragment input declaration.
layout (location=0) out uvec4 outColor;

void main ()
{
    /// Emit each input vertex in order, retaining its position/payload pairing.
    gl_Position = gl_in[0].gl_Position; outColor = inColor[0]; EmitVertex();
    gl_Position = gl_in[1].gl_Position; outColor = inColor[1]; EmitVertex();
    gl_Position = gl_in[2].gl_Position; outColor = inColor[2]; EmitVertex();
}
```

##### Fragment Shader

```glsl
#version 460

/// Flat transport makes the integer payload constant for the rasterized triangle.
layout (location=0) flat in uvec4 inColor;
/// The host creates an unsigned color attachment and compares every component exactly.
layout (location=0) out uvec4 outColor;

void main ()
{
    /// No shader-side color conversion is performed; this is the final multi-draw observer.
    outColor = inColor;
}
```

#### Additional Info

- The vertex `gl_DrawID` branch is selected by the unsuffixed `no_offset` leaf; `no_offset_no_draw_id` instead emits `gl_VertexIndex / 3`, which is why the page's draw-ID dimension changes vertex shader logic while the later stages remain fixed.
- The selected multiview case creates two layers and records one view mask per layer/subpass. The alpha expression is the only generated-source difference from the single-view vertex shader.
- Indexed mixed mode affects host vertex/index buffers and draw-info records. In this case `drawCommands` passes a null `pVertexOffset`, so the per-record `vertexOffset` values are shader-visible only through the resulting primitive positions and the host's reference calculation, not through a shader input.
- The source registers `vert`, `frag`, and conditionally `tesc`, `tese`, and `geom`; the representative path therefore exercises all five stages shown above. The generated source is in [`MultiDrawTest::initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L454-L604), and the selected modules are created in [`MultiDrawInstance::iterate`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L929-L943).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `drawId` (`no_draw_id` suffix) | Selects `gl_DrawID` versus `gl_VertexIndex / 3` for `storedIndex`; draw-ID cases require `VK_KHR_shader_draw_parameters`. | [`initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L497-L506), [`checkSupport`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L423-L429) |
| `multiview` | Adds `GL_EXT_multiview` and emits `255 - gl_ViewIndex` instead of constant alpha 255; later stages are unchanged. | [`initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L486-L505) |
| `tess_geom` / `with_tess` / `with_geom` / `vert_only` | Conditionally adds tessellation-control/evaluation and/or geometry modules; their source preserves the vertex payload and geometry. | [`initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L520-L604), [`createDrawMultiExtTests`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1465-L1475) |
| `mosaic` versus `overlapping` | Does not change shader source; it changes host-generated positions/depth and thus which encoded payload and stencil result are visible. | [`TriangleMosaicGenerator` and `TriangleOverlapGenerator`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L180-L243) |
| draw count, stride, indexed offset, and instance range | Do not change generated shader text; they change built-in values, primitive placement, and host reference expectations consumed by the same shader chain. | [`iterate` draw preparation and reference](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1041-L1144), [`drawCommands`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L798-L821) |

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
; Bound: 52
; Schema: 0
               OpCapability Shader
               OpCapability DrawParameters
               OpCapability MultiView
               OpExtension "SPV_KHR_multiview"
               OpExtension "SPV_KHR_shader_draw_parameters"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %gl_DrawID %outColor %gl_InstanceIndex %gl_ViewIndex
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_multiview"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %storedIndex "storedIndex"
               OpName %gl_DrawID "gl_DrawID"
               OpName %outColor "outColor"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %gl_ViewIndex "gl_ViewIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %inPos Location 0
               OpDecorate %gl_DrawID BuiltIn DrawIndex
               OpDecorate %outColor Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %gl_ViewIndex BuiltIn ViewIndex
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
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_int = OpTypePointer Input %int
  %gl_DrawID = OpVariable %_ptr_Input_int Input
     %v4uint = OpTypeVector %uint 4
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
   %outColor = OpVariable %_ptr_Output_v4uint Output
     %uint_8 = OpConstant %uint 8
   %uint_255 = OpConstant %uint 255
     %uint_0 = OpConstant %uint 0
%_ptr_Output_uint = OpTypePointer Output %uint
     %uint_1 = OpConstant %uint 1
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
     %uint_2 = OpConstant %uint 2
%gl_ViewIndex = OpVariable %_ptr_Input_int Input
     %uint_3 = OpConstant %uint 3
       %main = OpFunction %void None %3
          %5 = OpLabel
%storedIndex = OpVariable %_ptr_Function_uint Function
         %15 = OpLoad %v4float %inPos
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %23 = OpLoad %int %gl_DrawID
         %24 = OpBitcast %uint %23
               OpStore %storedIndex %24
         %28 = OpLoad %uint %storedIndex
         %30 = OpShiftRightLogical %uint %28 %uint_8
         %32 = OpBitwiseAnd %uint %30 %uint_255
         %35 = OpAccessChain %_ptr_Output_uint %outColor %uint_0
               OpStore %35 %32
         %36 = OpLoad %uint %storedIndex
         %37 = OpBitwiseAnd %uint %36 %uint_255
         %39 = OpAccessChain %_ptr_Output_uint %outColor %uint_1
               OpStore %39 %37
         %41 = OpLoad %int %gl_InstanceIndex
         %42 = OpBitcast %uint %41
         %43 = OpISub %uint %uint_255 %42
         %45 = OpAccessChain %_ptr_Output_uint %outColor %uint_2
               OpStore %45 %43
         %47 = OpLoad %int %gl_ViewIndex
         %48 = OpBitcast %uint %47
         %49 = OpISub %uint %uint_255 %48
         %51 = OpAccessChain %_ptr_Output_uint %outColor %uint_3
               OpStore %51 %49
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 63
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %gl_TessLevelInner %gl_TessLevelOuter %gl_out %gl_InvocationID %gl_in %outColor %inColor
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %gl_out "gl_out"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %gl_in "gl_in"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
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
%gl_PerVertex = OpTypeStruct %v4float
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_uint_3 = OpTypeArray %gl_PerVertex %uint_3
%_ptr_Output__arr_gl_PerVertex_uint_3 = OpTypePointer Output %_arr_gl_PerVertex_uint_3
     %gl_out = OpVariable %_ptr_Output__arr_gl_PerVertex_uint_3 Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
%gl_PerVertex_0 = OpTypeStruct %v4float
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
     %v4uint = OpTypeVector %uint 4
%_arr_v4uint_uint_3 = OpTypeArray %v4uint %uint_3
%_ptr_Output__arr_v4uint_uint_3 = OpTypePointer Output %_arr_v4uint_uint_3
   %outColor = OpVariable %_ptr_Output__arr_v4uint_uint_3 Output
%_arr_v4uint_uint_32 = OpTypeArray %v4uint %uint_32
%_ptr_Input__arr_v4uint_uint_32 = OpTypePointer Input %_arr_v4uint_uint_32
    %inColor = OpVariable %_ptr_Input__arr_v4uint_uint_32 Input
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %16 %float_1
         %18 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %18 %float_1
         %23 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %23 %float_1
         %24 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %24 %float_1
         %26 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %26 %float_1
         %28 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %28 %float_1
         %37 = OpLoad %int %gl_InvocationID
         %43 = OpLoad %int %gl_InvocationID
         %45 = OpAccessChain %_ptr_Input_v4float %gl_in %43 %int_0
         %46 = OpLoad %v4float %45
         %48 = OpAccessChain %_ptr_Output_v4float %gl_out %37 %int_0
               OpStore %48 %46
         %53 = OpLoad %int %gl_InvocationID
         %57 = OpLoad %int %gl_InvocationID
         %59 = OpAccessChain %_ptr_Input_v4uint %inColor %57
         %60 = OpLoad %v4uint %59
         %62 = OpAccessChain %_ptr_Output_v4uint %outColor %53
               OpStore %62 %60
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
; Bound: 57
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %_ %gl_TessCoord %gl_in %outColor %inColor
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingFractionalOdd
               OpExecutionMode %main VertexOrderCw
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %gl_in "gl_in"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
%gl_PerVertex_0 = OpTypeStruct %v4float
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
     %uint_2 = OpConstant %uint 2
      %int_2 = OpConstant %int 2
%_ptr_Output_v4float = OpTypePointer Output %v4float
     %v4uint = OpTypeVector %uint 4
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
   %outColor = OpVariable %_ptr_Output_v4uint Output
%_arr_v4uint_uint_32 = OpTypeArray %v4uint %uint_32
%_ptr_Input__arr_v4uint_uint_32 = OpTypePointer Input %_arr_v4uint_uint_32
    %inColor = OpVariable %_ptr_Input__arr_v4uint_uint_32 Input
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %20 = OpLoad %float %19
         %27 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %28 = OpLoad %v4float %27
         %29 = OpVectorTimesScalar %v4float %28 %20
         %31 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %32 = OpLoad %float %31
         %34 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %35 = OpLoad %v4float %34
         %36 = OpVectorTimesScalar %v4float %35 %32
         %37 = OpFAdd %v4float %29 %36
         %39 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
         %40 = OpLoad %float %39
         %42 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %43 = OpLoad %v4float %42
         %44 = OpVectorTimesScalar %v4float %43 %40
         %45 = OpFAdd %v4float %37 %44
         %47 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %47 %45
         %55 = OpAccessChain %_ptr_Input_v4uint %inColor %int_0
         %56 = OpLoad %v4uint %55
               OpStore %outColor %56
               OpReturn
               OpFunctionEnd
```

</details>

##### Geometry Shader
- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 45
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in %outColor %inColor
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %gl_in "gl_in"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
     %v4uint = OpTypeVector %uint 4
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
   %outColor = OpVariable %_ptr_Output_v4uint Output
%_arr_v4uint_uint_3 = OpTypeArray %v4uint %uint_3
%_ptr_Input__arr_v4uint_uint_3 = OpTypePointer Input %_arr_v4uint_uint_3
    %inColor = OpVariable %_ptr_Input__arr_v4uint_uint_3 Input
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
         %20 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %21 = OpLoad %v4float %20
         %23 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %23 %21
         %31 = OpAccessChain %_ptr_Input_v4uint %inColor %int_0
         %32 = OpLoad %v4uint %31
               OpStore %outColor %32
               OpEmitVertex
         %34 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %35 = OpLoad %v4float %34
         %36 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %36 %35
         %37 = OpAccessChain %_ptr_Input_v4uint %inColor %int_1
         %38 = OpLoad %v4uint %37
               OpStore %outColor %38
               OpEmitVertex
         %40 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %41 = OpLoad %v4float %40
         %42 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %42 %41
         %43 = OpAccessChain %_ptr_Input_v4uint %inColor %int_2
         %44 = OpLoad %v4uint %43
               OpStore %outColor %44
               OpEmitVertex
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
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %outColor Location 0
               OpDecorate %inColor Flat
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
   %outColor = OpVariable %_ptr_Output_v4uint Output
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
    %inColor = OpVariable %_ptr_Input_v4uint Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4uint %inColor
               OpStore %outColor %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The case requires `VK_EXT_multi_draw`; draw-ID cases also require `VK_KHR_shader_draw_parameters`. Tessellation, geometry, multiview, and dynamic-rendering cases check their corresponding feature or extension requirements before execution.
- `iterate()` creates a 32 by 32 `VK_FORMAT_R8G8B8A8_UINT` color image and a supported depth/stencil image. Multiview uses two array layers. It also creates host-visible transfer-destination buffers for each color and stencil layer.
- The host generates 1024 triangles, uploads a vertex buffer, and creates reversed indices for indexed cases. `DrawInfoPacker` serializes the applicable multi-draw records, including padded storage and the extra trailing bytes needed to keep packed indexed records legal.
- The test records either `vkCmdDrawMultiEXT` or `vkCmdDrawMultiIndexedEXT`. It supports a legacy render pass, dynamic rendering in a primary command buffer, and the registered dynamic-rendering secondary-command-buffer modes.
- After rendering, the command buffer transitions the color and depth/stencil images, copies the color and stencil aspects to host-visible buffers, and makes transfer writes available to the host.
- The CPU builds a reference for every pixel and view layer. It derives the encoded draw or primitive value, highest used instance index, view layer, and expected stencil increment count from the case parameters. Exact color and stencil comparisons decide the result.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mosaic` | Incorrect multi-draw record selection, stride advancement, indexed vertex-offset handling, draw-ID propagation, or per-pixel reference/readback handling. |
| `overlapping` | Incorrect ordered multi-draw execution, depth or stencil interaction, record selection, or the shared reference/readback handling. |

### Cause Analysis

#### Multi-draw record interpretation and draw identity

**Possible failure symptoms:** Mosaic color differs from the exact reference at one or more pixels, often in the encoded red and green draw or primitive components. Indexed offset cases, stride variants, or draw-ID variants can fail independently.

**Possible implementation causes:** The command implementation may read the wrong record, advance by the wrong byte stride, apply an indexed offset from the wrong source, or provide an incorrect draw ID. The command definitions require sequential record interpretation and specify the `pVertexOffset` override rule for indexed draws in [Multi-draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L1283-L1393).

#### Ordered depth and stencil behavior

**Possible failure symptoms:** An overlapping case has the wrong uniform color, the wrong stencil value, or both. A mismatch can vary with draw count because that parameter changes how the 1024 triangles are divided among records.

**Possible implementation causes:** The implementation may execute the sequence out of order, use incorrect depth comparison or depth writes for the selected geometry, or apply stencil increment-and-wrap incorrectly. The source-level reference combines these effects, so inspection of the failing attachment and parameter path is needed to distinguish them.

#### Shared rendering, copyback, or reference handling

**Possible failure symptoms:** Both mesh layouts fail across unrelated command forms or shader-stage paths, or a failure affects only a multiview layer despite otherwise matching color encoding.

**Possible implementation causes:** Source-level investigation is needed to distinguish pipeline setup, multiview layer selection, command-buffer recording, image transitions, attachment copies, host invalidation, or reference generation from command execution defects.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_multi_draw`; draw-ID cases require `VK_KHR_shader_draw_parameters`.
- Tessellation and geometry variants require their core features. Multiview variants require `multiview`, plus the relevant multiview tessellation or geometry feature.
- Dynamic-rendering registrations require `VK_KHR_dynamic_rendering`.
- For more than one draw, the source retains only strides that meet the commands' minimum-size and four-byte-alignment valid-usage rules.

### Design-based pruning

- Secondary-command-buffer registrations retain only `mosaic` and `one_draw`; normal commands remain, while indexed commands retain only the `random` offset representation.
- Normal commands do not register indexed offset variants; indexed commands do not register an absent offset type.
- Overlapping geometry omits instance counts greater than one because its depth-selected observation is designed for one instance.
- The two nested-secondary-command-buffer parent configurations do not add this family.

## Key Takeaways

- The family uses two independent observables: encoded integer color identifies the winning draw or primitive, and stencil verifies the expected amount of rendering work.
- `stride_zero` is registered only with zero or one draw. Because no command in those cases advances to another record, it does not exercise repeated-record execution.
- Indexed tests distinguish per-record offsets, a command-wide offset pointer, and packed storage while preserving the same color and stencil contract.
- The registered dynamic-rendering secondary modes reduce the matrix, but mustpass still includes real `multi_draw` cases for both complete-secondary and render-pass paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and draw-info packing | [parameter types and `DrawInfoPacker`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L60-L369) | Defines command form, offset modes, record packing, and packed-indexed safety padding. |
| Support checks and generated shaders | [`checkSupport` and `initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L423-L604) | Defines feature gates and the color encoding carried through the graphics stages. |
| Command recording | [`drawCommands`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L798-L821) | Calls the two extension commands and selects indexed offset-pointer behavior. |
| Resource setup, rendering, and comparison | [`MultiDrawInstance::iterate`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L823-L1392) | Creates resources, records rendering, copies attachments, and compares exact CPU references. |
| Matrix registration | [`createDrawMultiExtTests`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1396-L1637) | Registers the mesh, command, count, stride, instance, shader, view, and draw-ID hierarchy. |
| Parent draw registration | [`createChildren` and `createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L190) | Places the family in legacy and applicable dynamic-rendering branches. |
| Default Vulkan mustpass | [dynamic-rendering examples](../../../mustpass/main/vk-default/draw.txt#L1130-L1142) and [render-pass examples](../../../mustpass/main/vk-default/draw.txt#L28660-L28672) | Confirms registered default-profile entries in both execution paths. |
| Vulkan command semantics | [multi-draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L1283-L1425) | Defines ordered records, stride, instance behavior, indexed offsets, and valid usage. |
