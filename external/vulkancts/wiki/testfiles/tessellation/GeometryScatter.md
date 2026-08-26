## Overview

**Core question:** Can geometry shader output from many tessellated triangles, invocations, and emitted primitives be scattered so that it collectively covers a complete one-layer or eight-layer grid?

- [`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) implements the three test case leaves under `tessellation.geometry_interaction.scatter`.
- Every case tessellates one patch into 50 triangles in a small corner, runs four geometry shader invocations per triangle, then maps the output across the whole destination.
- The leaves isolate scattering by geometry invocation, by separately emitted primitive, and by primitive plus framebuffer layer.
- The host checks every pixel in every created layer. Black gaps expose missing output, while incorrect layer routing leaves at least one layer incomplete.

## Background Knowledge

For the shared concepts tessellation pipeline stages and geometry-stage routing, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Geometry shader instancing.** A geometry shader can run several invocations for one input primitive. `gl_InvocationID` distinguishes those invocations, letting each execution choose a different output location.
- **Separate output primitives.** Geometry shader vertices form a strip until `EndPrimitive()` or the end of the invocation. Calling `EndPrimitive()` lets one invocation emit disconnected quads at distant positions without creating triangles between them.
- **Layered rendering.** A geometry shader can write `gl_Layer` to route a primitive to one layer of a multi-layer framebuffer attachment. All vertices of one primitive must select the same valid layer.

## Registration Hierarchy

```text
tessellation.geometry_interaction.scatter
├── geometry_scatter_instances
├── geometry_scatter_primitives
└── geometry_scatter_layers
```

[`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) adds `scatter` beneath `geometry_interaction`. [`createGeometryGridRenderScatterTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L764-L782) registers the three leaves shown above. The [Vulkan](../../../mustpass/main/vk-default/tessellation.txt#L32-L34) and [Vulkan SC](../../../mustpass/main/vksc-default/tessellation.txt#L32-L34) default mustpass lists contain the corresponding paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or fixed values | Meaning in this test | Evidence |
|-----------|----------------------------|----------------------|----------|
| Test case leaf | `geometry_scatter_instances`, `geometry_scatter_primitives`, `geometry_scatter_layers` | Selects which geometry shader output identity controls destination placement. | [registration table](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L770-L780) |
| Tessellation generation level | 5 | Produces a 5 x 5 quad grid, split into 50 input triangles for the geometry stage. | [constructor](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L100) and [TCS generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L177-L205) |
| Tessellation evaluation output area | Lower-left 0.3 x 0.3 clip-space region | Keeps input geometry localized so full-frame coverage must come from geometry-stage relocation. | [TES generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L211-L235) |
| Geometry invocations | 4 per input triangle | Supplies four `gl_InvocationID` values that participate in each scatter mapping. | [geometry layout](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L240-L251) |
| Output topology per invocation | One 16-vertex strip for instances; four terminated four-vertex strips for primitives/layers | Distinguishes scattering complete invocation output from scattering individual output primitives. | [output-count calculation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L119-L144) and [scatter branches](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L285-L390) |
| Destination grid | 5 x 40 for instances; 20 x 40 for primitives; 20 x 5 in each layer for layers | Gives each source identity one destination cell. | [scatter formulas](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L285-L390) |
| Attachment layers | 1 for instances/primitives; 8 for layers | Makes layer selection part of the observable result only in `geometry_scatter_layers`. | [constructor and image setup](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L100) |
| Render target | 256 x 256, `VK_FORMAT_R8G8B8A8_UNORM` | Turns destination occupancy into an all-pixel coverage check. | [runtime image setup](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L634-L653) |

The integer multipliers and modulo operations form deterministic permutations rather than random placement. Across the complete draw, every destination cell is assigned once: 200 slots for instances, 800 cells for primitives, and 100 cells in each of eight layers for layers.

## Behavior Parameters

The primary behavior parameter is the **scatter target selected by the test case leaf**. Each value changes which geometry shader output unit the destination mapping separates.

### `geometry_scatter_instances` — relocate each invocation strip

Each of the 50 tessellated triangles launches four invocations. The shader combines `gl_InvocationID` with the triangle half, maps the resulting source slice to a distant slot, and emits one continuous 16-vertex strip there. The 200 invocation outputs fill a 5 x 40 grid. This case tests whether output from distinct geometry shader invocations remains complete when neighboring source invocations write far apart.

### `geometry_scatter_primitives` — relocate separate primitives from one invocation

Each invocation loops four times. Every loop iteration computes a distant cell in a 20 x 40 grid, emits a four-vertex quad, and calls `EndPrimitive()`. The full draw emits 800 quads, one for each destination cell. This case adds repeated primitive termination and restart to the destination remapping tested by the instances case.

### `geometry_scatter_layers` — relocate primitives across image layers

This case also emits four separate quads per invocation, but it uses a 20 x 5 destination grid and computes `gl_Layer` for every quad. The framebuffer has eight layers; each layer receives all 100 cells of its grid. Complete output therefore depends on both 2D placement and correct layer routing.

## Shader Analysis

The walkthrough uses `geometry_scatter_primitives` because it contains the shared destination-grid arithmetic and the separate-primitive emission form without adding the layers case's `gl_Layer` calculation. The parameter variation table covers the other two branches.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.geometry_interaction.scatter.geometry_scatter_primitives
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `FLAG_GEOMETRY_SCATTER_PRIMITIVES` and `FLAG_GEOMETRY_SEPARATE_PRIMITIVES` | Selects per-primitive remapping and terminates every four-vertex quad. |
| Tessellation level 5 | Supplies 25 source cells and 50 input triangles with integer grid coordinates. |
| Four geometry invocations | Multiplies each input triangle into four independent executions. |
| Four output primitives per invocation | Fills four distant cells and consumes the 16-vertex output declaration. |

#### Purpose

The geometry shader tests whether one invocation can emit several disconnected primitives at unrelated positions while output from all tessellated triangles and invocation IDs still covers the complete destination grid.

#### Structural Design

| Phase | Geometry shader action | Observable role |
|-------|------------------------|-----------------|
| Recover source identity | Find the input triangle's grid coordinate and determine which half of the tessellated cell it represents. | Distinguishes all 50 tessellated input triangles. |
| Add invocation identity | Combine triangle half with `gl_InvocationID` to produce an index from 0 through 7. | Keeps the four geometry invocations distinct. |
| Select destination | Combine grid position, invocation/half index, and loop index with integer permutation formulas. | Assigns one unique cell in the 20 x 40 output grid. |
| Emit and terminate | Write four vertices for the cell and call `EndPrimitive()`. | Produces one isolated quad without connecting it to the next distant quad. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
/// Four geometry invocations process each tessellated input triangle. The separate-primitive path emits four independent quads.
layout(triangles, invocations = 4) in;
layout(triangle_strip, max_vertices = 16) out;

/// The tessellation evaluation shader supplies integer coordinates in the original 5 x 5 tessellation grid.
layout(location = 0) in       mediump ivec2 v_tessellationGridPosition[];
layout(location = 0) flat out highp   vec4  v_color;

void main (void)
{
    const float equalThreshold = 0.001;
    const float gapOffset = 0.0001; // subdivision performed by the geometry shader might produce gaps. Fill potential gaps by enlarging the output slice a little.

    // Input triangle is generated from an axis-aligned rectangle by splitting it in half
    // Original rectangle can be found by finding the bounding AABB of the triangle
    vec4 aabb = vec4(min(gl_in[0].gl_Position.x, min(gl_in[1].gl_Position.x, gl_in[2].gl_Position.x)),
                     min(gl_in[0].gl_Position.y, min(gl_in[1].gl_Position.y, gl_in[2].gl_Position.y)),
                     max(gl_in[0].gl_Position.x, max(gl_in[1].gl_Position.x, gl_in[2].gl_Position.x)),
                     max(gl_in[0].gl_Position.y, max(gl_in[1].gl_Position.y, gl_in[2].gl_Position.y)));

    // Location in tessellation grid
    ivec2 gridPosition = ivec2(min(v_tessellationGridPosition[0], min(v_tessellationGridPosition[1], v_tessellationGridPosition[2])));

    // Which triangle of the two that split the grid cell
    int numVerticesOnBottomEdge = 0;
    for (int ndx = 0; ndx < 3; ++ndx)
        if (abs(gl_in[ndx].gl_Position.y - aabb.w) < equalThreshold)
            ++numVerticesOnBottomEdge;
    bool isBottomTriangle = numVerticesOnBottomEdge == 2;

    // Draw grid cells
    /// Combine invocation ID and triangle half into an index from 0 through 7.
    int inputTriangleNdx = gl_InvocationID * 2 + ((isBottomTriangle) ? (1) : (0));
    for (int ndx = 0; ndx < 4; ++ndx)
    {
        /// Map this emitted primitive to one cell of a 20 x 40 destination grid.
        ivec2 dstGridSize = ivec2(5 * 4, 2 * 5 * 4);
        ivec2 dstGridNdx = ivec2(5 * ndx + gridPosition.x, 5 * inputTriangleNdx + 2 * gridPosition.y + ndx * 127) % dstGridSize;
        vec4 dstArea;
        dstArea.x = float(dstGridNdx.x)   / float(dstGridSize.x) * 2.0 - 1.0 - gapOffset;
        dstArea.y = float(dstGridNdx.y)   / float(dstGridSize.y) * 2.0 - 1.0 - gapOffset;
        dstArea.z = float(dstGridNdx.x+1) / float(dstGridSize.x) * 2.0 - 1.0 + gapOffset;
        dstArea.w = float(dstGridNdx.y+1) / float(dstGridSize.y) * 2.0 - 1.0 + gapOffset;

        vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
        vec4 yellow = vec4(1.0, 1.0, 0.0, 1.0);
        vec4 outputColor = (((dstGridNdx.y + dstGridNdx.x) % 2) == 0) ? (green) : (yellow);

        /// Emit one four-vertex triangle strip, then terminate it before selecting the next distant cell.
        gl_Position = vec4(dstArea.x, dstArea.y, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();

        gl_Position = vec4(dstArea.x, dstArea.w, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();

        gl_Position = vec4(dstArea.z, dstArea.y, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();

        gl_Position = vec4(dstArea.z, dstArea.w, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();
        EndPrimitive();
    }
}
```

#### Additional Info

- The tessellation evaluation shader places all source triangles in the lower-left 0.3 x 0.3 clip-space area. The shown geometry shader ignores those source bounds when it selects destination cells.
- `gapOffset` expands cell edges by 0.0001 in clip space. That overlap prevents rasterization seams from exposing black pixels between neighboring destination cells.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| `geometry_scatter_instances` | Replaces the four-quad loop with one destination slice per invocation and emits one continuous 16-vertex strip without `EndPrimitive()`. | [instances branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L369-L424) |
| `geometry_scatter_primitives` | Produces the shown four-invocation shader with four terminated quads per invocation and no layer output. | [primitives branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L285-L323) |
| `geometry_scatter_layers` | Changes the destination grid to 20 x 5 and writes the same computed `gl_Layer` for all four vertices of each quad. | [layers branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L324-L368) |

#### SPIR-V

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
; Bound: 248
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_in %v_tessellationGridPosition %gl_InvocationID %_ %v_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 4
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 16
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %aabb "aabb"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %gridPosition "gridPosition"
               OpName %v_tessellationGridPosition "v_tessellationGridPosition"
               OpName %numVerticesOnBottomEdge "numVerticesOnBottomEdge"
               OpName %ndx "ndx"
               OpName %isBottomTriangle "isBottomTriangle"
               OpName %inputTriangleNdx "inputTriangleNdx"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %ndx_0 "ndx"
               OpName %dstGridSize "dstGridSize"
               OpName %dstGridNdx "dstGridNdx"
               OpName %dstArea "dstArea"
               OpName %green "green"
               OpName %yellow "yellow"
               OpName %outputColor "outputColor"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %_ ""
               OpName %v_color "v_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %v_tessellationGridPosition RelaxedPrecision
               OpDecorate %v_tessellationGridPosition Location 0
               OpDecorate %64 RelaxedPrecision
               OpDecorate %66 RelaxedPrecision
               OpDecorate %68 RelaxedPrecision
               OpDecorate %69 RelaxedPrecision
               OpDecorate %70 RelaxedPrecision
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpDecorate %v_color Flat
               OpDecorate %v_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
%gl_PerVertex = OpTypeStruct %v4float %float
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_uint_3 = OpTypeArray %gl_PerVertex %uint_3
%_ptr_Input__arr_gl_PerVertex_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_uint_3 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
     %uint_1 = OpConstant %uint 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
%_arr_v2int_uint_3 = OpTypeArray %v2int %uint_3
%_ptr_Input__arr_v2int_uint_3 = OpTypePointer Input %_arr_v2int_uint_3
%v_tessellationGridPosition = OpVariable %_ptr_Input__arr_v2int_uint_3 Input
%_ptr_Input_v2int = OpTypePointer Input %v2int
%_ptr_Function_int = OpTypePointer Function %int
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
%_ptr_Function_float = OpTypePointer Function %float
%float_0_00100000005 = OpConstant %float 0.00100000005
%_ptr_Function_bool = OpTypePointer Function %bool
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
      %int_4 = OpConstant %int 4
     %int_20 = OpConstant %int 20
     %int_40 = OpConstant %int 40
        %123 = OpConstantComposite %v2int %int_20 %int_40
      %int_5 = OpConstant %int 5
    %int_127 = OpConstant %int 127
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
%float_9_99999975en05 = OpConstant %float 9.99999975e-05
     %uint_2 = OpConstant %uint 2
    %float_0 = OpConstant %float 0
        %197 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %199 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
     %v4bool = OpTypeVector %bool 4
%gl_PerVertex_0 = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex_0 = OpTypePointer Output %gl_PerVertex_0
          %_ = OpVariable %_ptr_Output_gl_PerVertex_0 Output
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
       %aabb = OpVariable %_ptr_Function_v4float Function
%gridPosition = OpVariable %_ptr_Function_v2int Function
%numVerticesOnBottomEdge = OpVariable %_ptr_Function_int Function
        %ndx = OpVariable %_ptr_Function_int Function
%isBottomTriangle = OpVariable %_ptr_Function_bool Function
%inputTriangleNdx = OpVariable %_ptr_Function_int Function
      %ndx_0 = OpVariable %_ptr_Function_int Function
%dstGridSize = OpVariable %_ptr_Function_v2int Function
 %dstGridNdx = OpVariable %_ptr_Function_v2int Function
    %dstArea = OpVariable %_ptr_Function_v4float Function
      %green = OpVariable %_ptr_Function_v4float Function
     %yellow = OpVariable %_ptr_Function_v4float Function
%outputColor = OpVariable %_ptr_Function_v4float Function
         %20 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_0 %uint_0
         %21 = OpLoad %float %20
         %23 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_0 %uint_0
         %24 = OpLoad %float %23
         %26 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_0 %uint_0
         %27 = OpLoad %float %26
         %28 = OpExtInst %float %1 FMin %24 %27
         %29 = OpExtInst %float %1 FMin %21 %28
         %31 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_0 %uint_1
         %32 = OpLoad %float %31
         %33 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_0 %uint_1
         %34 = OpLoad %float %33
         %35 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_0 %uint_1
         %36 = OpLoad %float %35
         %37 = OpExtInst %float %1 FMin %34 %36
         %38 = OpExtInst %float %1 FMin %32 %37
         %39 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_0 %uint_0
         %40 = OpLoad %float %39
         %41 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_0 %uint_0
         %42 = OpLoad %float %41
         %43 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_0 %uint_0
         %44 = OpLoad %float %43
         %45 = OpExtInst %float %1 FMax %42 %44
         %46 = OpExtInst %float %1 FMax %40 %45
         %47 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_0 %uint_1
         %48 = OpLoad %float %47
         %49 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_0 %uint_1
         %50 = OpLoad %float %49
         %51 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_0 %uint_1
         %52 = OpLoad %float %51
         %53 = OpExtInst %float %1 FMax %50 %52
         %54 = OpExtInst %float %1 FMax %48 %53
         %55 = OpCompositeConstruct %v4float %29 %38 %46 %54
               OpStore %aabb %55
         %63 = OpAccessChain %_ptr_Input_v2int %v_tessellationGridPosition %int_0
         %64 = OpLoad %v2int %63
         %65 = OpAccessChain %_ptr_Input_v2int %v_tessellationGridPosition %int_1
         %66 = OpLoad %v2int %65
         %67 = OpAccessChain %_ptr_Input_v2int %v_tessellationGridPosition %int_2
         %68 = OpLoad %v2int %67
         %69 = OpExtInst %v2int %1 SMin %66 %68
         %70 = OpExtInst %v2int %1 SMin %64 %69
               OpStore %gridPosition %70
               OpStore %numVerticesOnBottomEdge %int_0
               OpStore %ndx %int_0
               OpBranch %74
         %74 = OpLabel
               OpLoopMerge %76 %77 None
               OpBranch %78
         %78 = OpLabel
         %79 = OpLoad %int %ndx
         %82 = OpSLessThan %bool %79 %int_3
               OpBranchConditional %82 %75 %76
         %75 = OpLabel
         %83 = OpLoad %int %ndx
         %84 = OpAccessChain %_ptr_Input_float %gl_in %83 %int_0 %uint_1
         %85 = OpLoad %float %84
         %87 = OpAccessChain %_ptr_Function_float %aabb %uint_3
         %88 = OpLoad %float %87
         %89 = OpFSub %float %85 %88
         %90 = OpExtInst %float %1 FAbs %89
         %92 = OpFOrdLessThan %bool %90 %float_0_00100000005
               OpSelectionMerge %94 None
               OpBranchConditional %92 %93 %94
         %93 = OpLabel
         %95 = OpLoad %int %numVerticesOnBottomEdge
         %96 = OpIAdd %int %95 %int_1
               OpStore %numVerticesOnBottomEdge %96
               OpBranch %94
         %94 = OpLabel
               OpBranch %77
         %77 = OpLabel
         %97 = OpLoad %int %ndx
         %98 = OpIAdd %int %97 %int_1
               OpStore %ndx %98
               OpBranch %74
         %76 = OpLabel
        %101 = OpLoad %int %numVerticesOnBottomEdge
        %102 = OpIEqual %bool %101 %int_2
               OpStore %isBottomTriangle %102
        %106 = OpLoad %int %gl_InvocationID
        %107 = OpIMul %int %106 %int_2
        %108 = OpLoad %bool %isBottomTriangle
        %109 = OpSelect %int %108 %int_1 %int_0
        %110 = OpIAdd %int %107 %109
               OpStore %inputTriangleNdx %110
               OpStore %ndx_0 %int_0
               OpBranch %112
        %112 = OpLabel
               OpLoopMerge %114 %115 None
               OpBranch %116
        %116 = OpLabel
        %117 = OpLoad %int %ndx_0
        %119 = OpSLessThan %bool %117 %int_4
               OpBranchConditional %119 %113 %114
        %113 = OpLabel
               OpStore %dstGridSize %123
        %126 = OpLoad %int %ndx_0
        %127 = OpIMul %int %int_5 %126
        %128 = OpAccessChain %_ptr_Function_int %gridPosition %uint_0
        %129 = OpLoad %int %128
        %130 = OpIAdd %int %127 %129
        %131 = OpLoad %int %inputTriangleNdx
        %132 = OpIMul %int %int_5 %131
        %133 = OpAccessChain %_ptr_Function_int %gridPosition %uint_1
        %134 = OpLoad %int %133
        %135 = OpIMul %int %int_2 %134
        %136 = OpIAdd %int %132 %135
        %137 = OpLoad %int %ndx_0
        %139 = OpIMul %int %137 %int_127
        %140 = OpIAdd %int %136 %139
        %141 = OpCompositeConstruct %v2int %130 %140
        %142 = OpLoad %v2int %dstGridSize
        %143 = OpSMod %v2int %141 %142
               OpStore %dstGridNdx %143
        %145 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_0
        %146 = OpLoad %int %145
        %147 = OpConvertSToF %float %146
        %148 = OpAccessChain %_ptr_Function_int %dstGridSize %uint_0
        %149 = OpLoad %int %148
        %150 = OpConvertSToF %float %149
        %151 = OpFDiv %float %147 %150
        %153 = OpFMul %float %151 %float_2
        %155 = OpFSub %float %153 %float_1
        %157 = OpFSub %float %155 %float_9_99999975en05
        %158 = OpAccessChain %_ptr_Function_float %dstArea %uint_0
               OpStore %158 %157
        %159 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_1
        %160 = OpLoad %int %159
        %161 = OpConvertSToF %float %160
        %162 = OpAccessChain %_ptr_Function_int %dstGridSize %uint_1
        %163 = OpLoad %int %162
        %164 = OpConvertSToF %float %163
        %165 = OpFDiv %float %161 %164
        %166 = OpFMul %float %165 %float_2
        %167 = OpFSub %float %166 %float_1
        %168 = OpFSub %float %167 %float_9_99999975en05
        %169 = OpAccessChain %_ptr_Function_float %dstArea %uint_1
               OpStore %169 %168
        %170 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_0
        %171 = OpLoad %int %170
        %172 = OpIAdd %int %171 %int_1
        %173 = OpConvertSToF %float %172
        %174 = OpAccessChain %_ptr_Function_int %dstGridSize %uint_0
        %175 = OpLoad %int %174
        %176 = OpConvertSToF %float %175
        %177 = OpFDiv %float %173 %176
        %178 = OpFMul %float %177 %float_2
        %179 = OpFSub %float %178 %float_1
        %180 = OpFAdd %float %179 %float_9_99999975en05
        %182 = OpAccessChain %_ptr_Function_float %dstArea %uint_2
               OpStore %182 %180
        %183 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_1
        %184 = OpLoad %int %183
        %185 = OpIAdd %int %184 %int_1
        %186 = OpConvertSToF %float %185
        %187 = OpAccessChain %_ptr_Function_int %dstGridSize %uint_1
        %188 = OpLoad %int %187
        %189 = OpConvertSToF %float %188
        %190 = OpFDiv %float %186 %189
        %191 = OpFMul %float %190 %float_2
        %192 = OpFSub %float %191 %float_1
        %193 = OpFAdd %float %192 %float_9_99999975en05
        %194 = OpAccessChain %_ptr_Function_float %dstArea %uint_3
               OpStore %194 %193
               OpStore %green %197
               OpStore %yellow %199
        %201 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_1
        %202 = OpLoad %int %201
        %203 = OpAccessChain %_ptr_Function_int %dstGridNdx %uint_0
        %204 = OpLoad %int %203
        %205 = OpIAdd %int %202 %204
        %206 = OpSMod %int %205 %int_2
        %207 = OpIEqual %bool %206 %int_0
        %208 = OpLoad %v4float %green
        %209 = OpLoad %v4float %yellow
        %211 = OpCompositeConstruct %v4bool %207 %207 %207 %207
        %212 = OpSelect %v4float %211 %208 %209
               OpStore %outputColor %212
        %216 = OpAccessChain %_ptr_Function_float %dstArea %uint_0
        %217 = OpLoad %float %216
        %218 = OpAccessChain %_ptr_Function_float %dstArea %uint_1
        %219 = OpLoad %float %218
        %220 = OpCompositeConstruct %v4float %217 %219 %float_0 %float_1
        %222 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %222 %220
        %224 = OpLoad %v4float %outputColor
               OpStore %v_color %224
               OpEmitVertex
        %225 = OpAccessChain %_ptr_Function_float %dstArea %uint_0
        %226 = OpLoad %float %225
        %227 = OpAccessChain %_ptr_Function_float %dstArea %uint_3
        %228 = OpLoad %float %227
        %229 = OpCompositeConstruct %v4float %226 %228 %float_0 %float_1
        %230 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %230 %229
        %231 = OpLoad %v4float %outputColor
               OpStore %v_color %231
               OpEmitVertex
        %232 = OpAccessChain %_ptr_Function_float %dstArea %uint_2
        %233 = OpLoad %float %232
        %234 = OpAccessChain %_ptr_Function_float %dstArea %uint_1
        %235 = OpLoad %float %234
        %236 = OpCompositeConstruct %v4float %233 %235 %float_0 %float_1
        %237 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %237 %236
        %238 = OpLoad %v4float %outputColor
               OpStore %v_color %238
               OpEmitVertex
        %239 = OpAccessChain %_ptr_Function_float %dstArea %uint_2
        %240 = OpLoad %float %239
        %241 = OpAccessChain %_ptr_Function_float %dstArea %uint_3
        %242 = OpLoad %float %241
        %243 = OpCompositeConstruct %v4float %240 %242 %float_0 %float_1
        %244 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %244 %243
        %245 = OpLoad %v4float %outputColor
               OpStore %v_color %245
               OpEmitVertex
               OpEndPrimitive
               OpBranch %115
        %115 = OpLabel
        %246 = OpLoad %int %ndx_0
        %247 = OpIAdd %int %246 %int_1
               OpStore %ndx_0 %247
               OpBranch %112
        %114 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L729) requires tessellation shader and geometry shader features before creating graphics work.
- The host creates a 256 x 256 `VK_FORMAT_R8G8B8A8_UNORM` image. Instances and primitives cases use one layer and a 2D view; the layers case uses eight layers and a 2D-array view. A host-visible transfer-destination buffer holds the copied bytes for every layer.
- The pipeline uses the five generated shader stages and has no vertex attributes or descriptors. The host transitions the complete image range, clears all layers to opaque black, and records `vkCmdDraw(..., 1, 1, ...)` for one patch.
- After the draw, `copyImageToBuffer()` copies all layers to the host-visible buffer. The host waits for completion and invalidates the allocation before reading it.
- [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) scans every pixel in every layer. A pixel passes when green is at least 247 and blue is at most 8. Red and alpha do not decide validity. The shader emits flat green or yellow values, but any value meeting the green/blue predicate would pass, including a linear mixture if one were produced.
- Black clear pixels fail the green threshold. Wrong layer selection fails when it leaves invalid pixels in a checked layer. The verifier logs the rendered image for each valid layer; on failure it also logs a red error mask and returns `Image comparison failed`.
- The host does not compare exact cell ownership, checkerboard parity, red, or alpha. A placement error that preserves complete accepted-color coverage in every checked layer can escape the predicate.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `geometry_scatter_instances` | Geometry shader invocations, `gl_InvocationID`, or continuous triangle-strip output may be misplaced or lost while each invocation writes to a distant destination slot; or the shared render/readback path may be faulty. |
| `geometry_scatter_primitives` | Separate output primitives, `EndPrimitive()`, or per-primitive destination arithmetic may be handled incorrectly while one invocation scatters four quads; or the shared render/readback path may be faulty. |
| `geometry_scatter_layers` | Separate output primitives or `gl_Layer` routing into the eight-layer framebuffer may be handled incorrectly; or the shared render/readback path may be faulty. |

### Cause Analysis

#### Invocation-strip relocation failures

**Possible failure symptoms:** Pipeline creation or drawing can fail, or the copied image can contain black regions where one or more of the 200 destination slots received no valid strip output. The error mask marks those rejected pixels red.

**Possible implementation causes:** The compiler or geometry stage may mishandle the four-invocation execution mode, produce an incorrect `gl_InvocationID`, lose output from an invocation, or assemble the emitted 16-vertex triangle strip incorrectly. The geometry shader invocation and output-strip rules define the behavior this leaf relies on.

#### Separate-primitive relocation failures

**Possible failure symptoms:** The framebuffer can contain missing cells or corrupted coverage whose green/blue bytes fall outside the accepted range. The per-pixel predicate does not reject extra green/yellow geometry by itself.

**Possible implementation causes:** The geometry stage may mishandle repeated `EmitVertex()` and `EndPrimitive()` operations, fail to restart strip assembly after termination, or compile the integer destination mapping incorrectly. Each loop iteration emits four vertices and explicitly terminates its primitive before computing the next cell.

#### Layer-routing failures

**Possible failure symptoms:** One or more of the eight copied layers can contain black cells or broad missing regions. Output sent to a wrong layer can make another layer look overdrawn, but the source layer still fails because the host verifies every layer.

**Possible implementation causes:** The compiler or pre-rasterization pipeline may write or consume `gl_Layer` incorrectly, or layered framebuffer routing may direct a primitive to the wrong attachment layer. The shader writes one valid layer value to every vertex of each primitive, as required by the `Layer` built-in rules.

#### Shared render and readback failures

**Possible failure symptoms:** Any leaf can remain black, contain widespread invalid pixels, or disagree with the expected bytes after copyback.

**Possible implementation causes:** A defect in tessellation-to-geometry stage linkage, rasterization, color writes, image layout/access transitions, image-to-buffer copy, or host-cache invalidation can alter the checked image. All leaves share those operations, so image corruption alone does not isolate the scatter branch.

## Case Pruning

### Requirement-based pruning

- The source calls `requireFeatures()` with `FEATURE_TESSELLATION_SHADER | FEATURE_GEOMETRY_SHADER`. A device without either feature does not execute these cases.
- The tests use fixed values that fit Vulkan's required geometry limits: four invocations and at most 16 output vertices per invocation. They do not query larger device-specific limits.
- Only `geometry_scatter_layers` creates a layered framebuffer and writes `gl_Layer`; the other cases use a single-layer image.

### Design-based pruning

- The registration table selects exactly one scatter mechanism per leaf. It does not combine instances, primitives, and layers flags.
- Tessellation level, invocation count, render extent, format, patch count, colors, and verification thresholds remain fixed across the family.
- The instances case keeps one continuous strip because its subject is placement of complete invocation output. The primitives and layers cases set `FLAG_GEOMETRY_SEPARATE_PRIMITIVES` because their subject requires individually placeable quads.
- The same C++ implementation also owns the separate `limits` family, but its required-limit behavior is outside this page.

## Key Takeaways

- The family turns three kinds of geometry output identity into deterministic destination permutations: invocation, emitted primitive, and framebuffer layer.
- Full destination coverage detects lost or misplaced output when it creates a gap. The predicate does not identify which source invocation or primitive supplied an accepted pixel, so coverage-preserving swaps or overdraw can escape detection.
- One continuous strip distinguishes `geometry_scatter_instances` from the `EndPrimitive()`-terminated quads used by the other leaves.
- The all-pixel green/blue check makes missing output visible as black gaps while tolerating interpolation between the generated green and yellow colors. See `Failure Meaning` for cause distinctions.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Scatter flags and case state | [`FlagBits` and `GridRenderTestCase`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L103) | Defines the three modes, separate-primitive choice, fixed level/invocations, and one/eight-layer state. |
| Output-count calculation | [`GridRenderTestCase` constructor](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L105-L145) | Selects one 14-triangle strip or four separate quads per invocation. |
| Generated graphics shaders | [`GridRenderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L147-L430) | Generates the small source patch and all three geometry scatter branches. |
| Exact image predicate | [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) | Defines the green/blue threshold and failure mask. |
| Resource setup, draw, and copyback | [`GridRenderTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L729) | Requires features, creates one/eight-layer resources, draws, copies, and verifies each layer. |
| Scatter-family registration | [`createGeometryGridRenderScatterTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L764-L782) | Registers the exact leaves and flag combinations. |
| Parent family placement | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places `scatter` under `tessellation.geometry_interaction`. |
| Tessellation semantics | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines patch subdivision and tessellation-generated triangles. |
| Geometry shader semantics | [Vulkan geometry chapter](../../../../vulkan-docs/src/chapters/geometry.adoc#geometry) | Defines input primitives, output strips, multiple invocations, and invocation identity. |
| Layer selection semantics | [Vulkan `Layer` built-in](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-layer) | Defines geometry-stage selection of framebuffer attachment layers. |