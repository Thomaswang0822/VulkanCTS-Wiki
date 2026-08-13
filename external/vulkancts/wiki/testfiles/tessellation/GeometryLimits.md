## Overview

**Core question:** Can the tessellation and geometry stages amplify one patch into a complete rendered image when the selected path uses a required tessellation/geometry value or a geometry-output declaration derived from required values?

- [`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) implements the three leaves under `tessellation.geometry_interaction.limits`.
- The tessellation and invocation leaves use the required values 64 and 32 directly. The geometry-output leaf derives a conservative 112-vertex declaration from the required 256-vertex and 1024-total-component values.
- The pipeline draws one patch into a 256 x 256 attachment. It passes only when every pixel contains an accepted green/yellow result, so missing geometry remains visible as a failure.
- The same source file implements the separate `scatter` test family. This page covers only `limits`, where each leaf selects a required-value path.

## Background Knowledge

For the shared concepts tessellation pipeline stages and geometry-stage amplification, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Tessellation followed by geometry shading.** A tessellation control shader writes subdivision levels for a patch. The fixed-function tessellator generates primitives, the tessellation evaluation shader positions their vertices, and the geometry shader can emit more primitives for each tessellated input primitive. The work produced by these stages therefore multiplies rather than adds.
- **Required minimum maximum values.** Vulkan reports maximum limits for each physical device and defines a minimum value that every conformant implementation must report for a supported feature. This family uses fixed specification-required constants rather than querying a device's potentially higher maxima. Tessellation level 64 and 32 geometry invocations appear directly in shaders; the geometry-output constants feed a conservative strip-length calculation.
- **Geometry shader output and instancing.** A geometry shader declares a maximum emitted-vertex count. It can also request multiple invocations per input primitive; `gl_InvocationID` identifies the invocation. Both values affect how the generated shader partitions and fills each tessellated cell.

## Registration Hierarchy

```text
tessellation.geometry_interaction.limits
├── output_required_max_tessellation
├── output_required_max_geometry
└── output_required_max_invocations
```

[`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) adds the `limits` family beneath `geometry_interaction`. [`createGeometryGridRenderLimitsTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L740-L761) registers the three leaves shown above. The [Vulkan](../../../mustpass/main/vk-default/tessellation.txt#L17-L19) and [Vulkan SC](../../../mustpass/main/vksc-default/tessellation.txt#L17-L19) default mustpass lists contain all three paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or fixed values | Meaning in this test | Evidence |
|-----------|----------------------------|----------------------|----------|
| Test case leaf | `output_required_max_tessellation`, `output_required_max_geometry`, `output_required_max_invocations` | Selects the required-limit branch used to generate the shaders. | [registration table](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L749-L759) |
| Tessellation generation level | 64 for `output_required_max_tessellation`; 5 otherwise | Sets all inner and outer tessellation levels for the quad patch. | [constructor and TCS generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L100) |
| Geometry invocations | 32 for `output_required_max_invocations`; 4 otherwise | Sets the geometry shader's `invocations` layout value for every tessellated triangle. | [constructor and geometry layout](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L100) |
| Geometry required values | output components per vertex 64; output vertices 256; total output components 1024 | The source logs all three for `output_required_max_geometry`; only the 256-vertex and 1024-total-component values feed the strip-length calculation. The generated vertex has 8 components, well below 64. | [calculation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L105-L144), [logged values](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L480-L509) |
| Generated geometry `max_vertices` | 112 for `output_required_max_geometry`; 16 otherwise | Bounds each invocation's emitted triangle strip. The shader emits exactly this many vertices as position pairs. | [geometry shader generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L240-L251) |
| Primitives per geometry invocation | 110 for `output_required_max_geometry`; 14 otherwise | A strip with 112 or 16 vertices produces 110 or 14 triangles. | [strip calculation and emission loop](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L119-L144) |
| Render target | 256 x 256, `VK_FORMAT_R8G8B8A8_UNORM`, one layer | Converts the amplified primitive stream into an all-pixel coverage result. | [image setup](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L634-L653) |

Only one limit flag is active per leaf. The source does not register a combined case that uses tessellation level 64, 32 geometry invocations, and the longer geometry strip at once.

## Behavior Parameters

The primary behavior parameter is the **required-limit path selected by the test case leaf**. The shaders and render path stay structurally the same; the tessellation and invocation paths put one amplification control at its required value, while the geometry-output path lengthens the strip using a calculation based on required values.

### `output_required_max_tessellation`: generation level 64

All six tessellation levels are 64. The quad tessellator produces 64 x 64 cells, or 8192 triangles, from one patch. Four geometry invocations process each triangle and each invocation emits a 16-vertex strip containing 14 triangles. This leaf puts the pressure on tessellation generation and on the downstream geometry/rasterization path that consumes its output.

### `output_required_max_geometry`: geometry output derived from required values

Tessellation stays at level 5 and the geometry invocation count stays at four. The constructor switches to the required 256-vertex and 1024-total-component values, then uses its conservative strip calculation to select 56 vertex pairs. The generated shader declares and emits 112 vertices (896 position/color components), producing 110 triangles per invocation. It therefore stays below both required maxima; this leaf exercises the source's required-geometry branch and a longer sustained emission workload rather than literally setting `max_vertices` to 256 or consuming all 1024 components.

### `output_required_max_invocations`: 32 invocations

Tessellation stays at level 5 and each geometry invocation emits the default 16-vertex strip. The geometry shader requests 32 invocations for every tessellated triangle. Each invocation uses `gl_InvocationID` to claim its own horizontal slice, so complete coverage depends on executing and assembling output from the full required invocation count.

## Shader Analysis

The geometry shader carries the common grid-filling mechanism and all geometry-limit choices. The walkthrough uses `output_required_max_geometry` because its 112-vertex strip exposes the required-value-derived output branch while retaining the same cell reconstruction, invocation partitioning, and color signal used by the other leaves.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.geometry_interaction.limits.output_required_max_geometry
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `FLAG_GEOMETRY_MAX_SPEC` | Selects required geometry output values 256 vertices and 1024 total components for the source's conservative strip calculation. |
| Tessellation level 5 | Produces 25 quad cells, split into 50 geometry input triangles. |
| Four geometry invocations | Divides each input triangle's half-cell into four horizontal slices. |
| `max_vertices = 112` | Allows 56 emitted vertex pairs and a 110-triangle strip per invocation. |

#### Purpose

The geometry shader turns every tessellated triangle into horizontal colored slices while emitting 112 vertices per invocation. Complete green/yellow framebuffer coverage makes execution of the longer output strip selected by the required-geometry branch visible to the host.

#### Structural Design

| Phase | Geometry shader action | Observable role |
|-------|------------------------|-----------------|
| Recover cell | Compute the input triangle's axis-aligned bounds and identify its tessellation-grid position. | Reconstructs the rectangular cell split by the tessellator. |
| Select half | Count vertices on one edge to distinguish the two triangles in the cell. | Assigns each input triangle to one half of the cell. |
| Select slice | Use `gl_InvocationID` to choose one of four slices in that half. | Gives the four invocations non-overlapping output regions, apart from a small gap-closing overlap. |
| Emit strip | Emit 56 bottom/top position pairs with alternating green and yellow colors. | Produces 112 vertices and 110 rasterized triangles per invocation. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
/// Each tessellated triangle launches four geometry invocations. Each invocation may emit the 112
/// vertices selected by the required-geometry-output case.
layout(triangles, invocations = 4) in;
layout(triangle_strip, max_vertices = 112) out;

/// The tessellation evaluation shader supplies integer grid coordinates for the triangle vertices.
/// The flat color becomes the fragment shader's only input.
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

    // Fill the input area with slices
    // Upper triangle produces slices only to the upper half of the quad and vice-versa
    float triangleOffset = (isBottomTriangle) ? ((aabb.w + aabb.y) / 2.0) : (aabb.y);
    // Each slice is a invocation
    float sliceHeight = (aabb.w - aabb.y) / float(2 * 4);
    float invocationOffset = float(gl_InvocationID) * sliceHeight;

    /// Expand each slice by gapOffset so rasterization does not expose seams between adjacent slices.
    vec4 outputSliceArea;
    outputSliceArea.x = aabb.x - gapOffset;
    outputSliceArea.y = triangleOffset + invocationOffset - gapOffset;
    outputSliceArea.z = aabb.z + gapOffset;
    outputSliceArea.w = triangleOffset + invocationOffset + sliceHeight + gapOffset;

    // Draw slice
    /// Fifty-six x positions, with two vertices at each position, consume the full 112-vertex declaration.
    for (int ndx = 0; ndx < 56; ++ndx)
    {
        vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
        vec4 yellow = vec4(1.0, 1.0, 0.0, 1.0);
        vec4 outputColor = (((gl_InvocationID + ndx) % 2) == 0) ? (green) : (yellow);
        float xpos = mix(outputSliceArea.x, outputSliceArea.z, float(ndx) / float(55));

        gl_Position = vec4(xpos, outputSliceArea.y, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();

        gl_Position = vec4(xpos, outputSliceArea.w, 0.0, 1.0);
        v_color = outputColor;
        EmitVertex();
    }
}
```

#### Additional Info

- The `gridPosition` calculation is shared with scatter variants in the same generator, although the limits branch does not use the local value after calculating it.
- The tessellation evaluation shader fills the whole viewport for limit cases and supplies the rounded grid coordinate. This geometry shader loads it to calculate `gridPosition`, but that local value does not affect the limits branch.
- The fragment shader only forwards `v_color`; all spatial subdivision and the accepted color choice originate in this geometry shader.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Required tessellation maximum | Changes tessellation level 5 to 64 in the control shader; this geometry shader uses four invocations and `max_vertices = 16`. | [constructor and TCS generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L100) |
| Required geometry maximum | Produces the shown four-invocation, 112-vertex geometry shader. | [geometry output calculation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L105-L144) |
| Required invocation maximum | Changes the geometry layout to 32 invocations; `sliceHeight` and `gl_InvocationID` partition each triangle into 32 slices while `max_vertices` returns to 16. | [geometry layout and slice generation](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L240-L251) |

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
; Bound: 212
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_in %v_tessellationGridPosition %gl_InvocationID %_ %v_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 4
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 112
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
               OpName %triangleOffset "triangleOffset"
               OpName %sliceHeight "sliceHeight"
               OpName %invocationOffset "invocationOffset"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %outputSliceArea "outputSliceArea"
               OpName %ndx_0 "ndx"
               OpName %green "green"
               OpName %yellow "yellow"
               OpName %outputColor "outputColor"
               OpName %xpos "xpos"
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
    %float_2 = OpConstant %float 2
    %float_8 = OpConstant %float 8
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
%float_9_99999975en05 = OpConstant %float 9.99999975e-05
     %uint_2 = OpConstant %uint 2
     %int_56 = OpConstant %int 56
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
        %169 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %171 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
     %v4bool = OpTypeVector %bool 4
   %float_55 = OpConstant %float 55
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
%triangleOffset = OpVariable %_ptr_Function_float Function
        %105 = OpVariable %_ptr_Function_float Function
%sliceHeight = OpVariable %_ptr_Function_float Function
%invocationOffset = OpVariable %_ptr_Function_float Function
%outputSliceArea = OpVariable %_ptr_Function_v4float Function
      %ndx_0 = OpVariable %_ptr_Function_int Function
      %green = OpVariable %_ptr_Function_v4float Function
     %yellow = OpVariable %_ptr_Function_v4float Function
%outputColor = OpVariable %_ptr_Function_v4float Function
       %xpos = OpVariable %_ptr_Function_float Function
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
        %104 = OpLoad %bool %isBottomTriangle
               OpSelectionMerge %107 None
               OpBranchConditional %104 %106 %115
        %106 = OpLabel
        %108 = OpAccessChain %_ptr_Function_float %aabb %uint_3
        %109 = OpLoad %float %108
        %110 = OpAccessChain %_ptr_Function_float %aabb %uint_1
        %111 = OpLoad %float %110
        %112 = OpFAdd %float %109 %111
        %114 = OpFDiv %float %112 %float_2
               OpStore %105 %114
               OpBranch %107
        %115 = OpLabel
        %116 = OpAccessChain %_ptr_Function_float %aabb %uint_1
        %117 = OpLoad %float %116
               OpStore %105 %117
               OpBranch %107
        %107 = OpLabel
        %118 = OpLoad %float %105
               OpStore %triangleOffset %118
        %120 = OpAccessChain %_ptr_Function_float %aabb %uint_3
        %121 = OpLoad %float %120
        %122 = OpAccessChain %_ptr_Function_float %aabb %uint_1
        %123 = OpLoad %float %122
        %124 = OpFSub %float %121 %123
        %126 = OpFDiv %float %124 %float_8
               OpStore %sliceHeight %126
        %130 = OpLoad %int %gl_InvocationID
        %131 = OpConvertSToF %float %130
        %132 = OpLoad %float %sliceHeight
        %133 = OpFMul %float %131 %132
               OpStore %invocationOffset %133
        %135 = OpAccessChain %_ptr_Function_float %aabb %uint_0
        %136 = OpLoad %float %135
        %138 = OpFSub %float %136 %float_9_99999975en05
        %139 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_0
               OpStore %139 %138
        %140 = OpLoad %float %triangleOffset
        %141 = OpLoad %float %invocationOffset
        %142 = OpFAdd %float %140 %141
        %143 = OpFSub %float %142 %float_9_99999975en05
        %144 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_1
               OpStore %144 %143
        %146 = OpAccessChain %_ptr_Function_float %aabb %uint_2
        %147 = OpLoad %float %146
        %148 = OpFAdd %float %147 %float_9_99999975en05
        %149 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_2
               OpStore %149 %148
        %150 = OpLoad %float %triangleOffset
        %151 = OpLoad %float %invocationOffset
        %152 = OpFAdd %float %150 %151
        %153 = OpLoad %float %sliceHeight
        %154 = OpFAdd %float %152 %153
        %155 = OpFAdd %float %154 %float_9_99999975en05
        %156 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_3
               OpStore %156 %155
               OpStore %ndx_0 %int_0
               OpBranch %158
        %158 = OpLabel
               OpLoopMerge %160 %161 None
               OpBranch %162
        %162 = OpLabel
        %163 = OpLoad %int %ndx_0
        %165 = OpSLessThan %bool %163 %int_56
               OpBranchConditional %165 %159 %160
        %159 = OpLabel
               OpStore %green %169
               OpStore %yellow %171
        %173 = OpLoad %int %gl_InvocationID
        %174 = OpLoad %int %ndx_0
        %175 = OpIAdd %int %173 %174
        %176 = OpSMod %int %175 %int_2
        %177 = OpIEqual %bool %176 %int_0
        %178 = OpLoad %v4float %green
        %179 = OpLoad %v4float %yellow
        %181 = OpCompositeConstruct %v4bool %177 %177 %177 %177
        %182 = OpSelect %v4float %181 %178 %179
               OpStore %outputColor %182
        %184 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_0
        %185 = OpLoad %float %184
        %186 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_2
        %187 = OpLoad %float %186
        %188 = OpLoad %int %ndx_0
        %189 = OpConvertSToF %float %188
        %191 = OpFDiv %float %189 %float_55
        %192 = OpExtInst %float %1 FMix %185 %187 %191
               OpStore %xpos %192
        %196 = OpLoad %float %xpos
        %197 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_1
        %198 = OpLoad %float %197
        %199 = OpCompositeConstruct %v4float %196 %198 %float_0 %float_1
        %201 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %201 %199
        %203 = OpLoad %v4float %outputColor
               OpStore %v_color %203
               OpEmitVertex
        %204 = OpLoad %float %xpos
        %205 = OpAccessChain %_ptr_Function_float %outputSliceArea %uint_3
        %206 = OpLoad %float %205
        %207 = OpCompositeConstruct %v4float %204 %206 %float_0 %float_1
        %208 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %208 %207
        %209 = OpLoad %v4float %outputColor
               OpStore %v_color %209
               OpEmitVertex
               OpBranch %161
        %161 = OpLabel
        %210 = OpLoad %int %ndx_0
        %211 = OpIAdd %int %210 %int_1
               OpStore %ndx_0 %211
               OpBranch %158
        %160 = OpLabel
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- [`iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L729) first requires tessellation and geometry shader features. Unsupported devices do not run the draw.
- The host creates a one-layer, 256 x 256 `VK_FORMAT_R8G8B8A8_UNORM` image as the color attachment and a host-visible transfer-destination buffer large enough for the copied image. The pipeline uses no vertex attributes or descriptors.
- The graphics pipeline contains all five generated stages. The command buffer transitions the image to color-attachment layout, clears it to opaque black, and records `vkCmdDraw(..., 1, 1, ...)` for one patch.
- After rendering, `copyImageToBuffer()` places the attachment in the host-visible buffer. The host waits for completion and invalidates the allocation before reading pixels.
- [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) scans every pixel. A pixel is valid when green is at least 247 and blue is at most 8. Red and alpha do not enter the predicate, which admits both generated colors and their linear mixtures.
- The black clear color has green 0, so an uncovered pixel fails. The verifier logs the result image on success; on failure it also logs an error mask with each rejected pixel marked red. The case returns `Image comparison failed` if any pixel is invalid.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `output_required_max_tessellation` | Failure to compile, execute, or rasterize the tessellation-to-geometry workload at tessellation generation level 64; or a shared render/readback defect. |
| `output_required_max_geometry` | Failure while compiling or executing the 112-vertex strip derived from required geometry output values; or a shared render/readback defect. The image result alone does not prove that an advertised maximum is wrong. |
| `output_required_max_invocations` | Failure to compile or execute 32 geometry shader invocations per input primitive and assemble their output; or a shared render/readback defect. |

### Cause Analysis

#### Tessellation generation at level 64

**Possible failure symptoms:** The shader or pipeline cannot be created, the draw cannot complete, or one or more copied pixels have green below 247 or blue above 8. Coverage loss may appear as black regions in the logged image and red regions in the error mask.

**Possible implementation causes:** The tessellation control levels may be compiled or consumed incorrectly, the fixed-function tessellator may fail to generate the required quad subdivisions, or the evaluation-to-geometry interface may lose or misplace generated vertices. The Vulkan limit requirements state that `maxTessellationGenerationLevel` must support at least 64 when tessellation is available.

#### Geometry output derived from required limits

**Possible failure symptoms:** Pipeline creation or shader execution may fail for the 112-vertex declaration, or strip output may leave invalid pixels where emitted vertices or triangles are missing or corrupted.

**Possible implementation causes:** The compiler or geometry stage may mishandle the `OutputVertices 112` declaration, repeated `EmitVertex` operations, output-component accounting, or triangle-strip assembly. The generated shader emits 112 vertices with 8 components each (896 total), staying within the required 256 output-vertex, 64 per-vertex-component, and 1024 total-output-component values. Because it does not reach those maxima, failure is evidence about this derived legal workload, not direct proof that the device cannot support declarations at 256 vertices or 1024 emitted components.

#### Thirty-two geometry shader invocations

**Possible failure symptoms:** The case may fail before drawing, or the framebuffer may contain invalid horizontal regions because output from one or more invocation IDs did not reach rasterization correctly.

**Possible implementation causes:** The geometry shader's 32-invocation execution mode may be rejected or lowered incorrectly, `gl_InvocationID` may produce a wrong slice offset, or output from the instanced invocations may be omitted during primitive assembly. Vulkan requires `maxGeometryShaderInvocations` of at least 32 when geometry shading is supported.

#### Shared render and readback path

**Possible failure symptoms:** The same broad framebuffer corruption can affect any leaf: invalid pixels, an image that remains black, or disagreement between rendered output and host-visible copied bytes.

**Possible implementation causes:** A defect in pipeline stage linkage, rasterization, color-attachment writes, image layout/access transitions, image-to-buffer copy, or host-cache invalidation can alter the checked bytes. Since all three leaves share this path and use the same predicate, the image alone does not isolate one of these operations.

## Case Pruning

### Requirement-based pruning

- The source calls `requireFeatures()` with `FEATURE_TESSELLATION_SHADER | FEATURE_GEOMETRY_SHADER`. A device without either feature does not execute these cases.
- The shaders use required specification values, so the family has no per-device branch that scales them down. Feature support establishes that the corresponding required maxima apply.

### Design-based pruning

- Each leaf selects one pressure point. The registration table omits combinations of the three limit flags.
- The source comments state that implementation-defined maximum tests were omitted because they require runtime-dependent shader source. Some CTS targets require precompiled shaders, so this family uses fixed specification-required values instead.
- The render format, extent, patch count, quad domain, image layer count, and green/yellow verification predicate are fixed.
- `scatter` cases use the same implementation file but test output placement across instances, primitives, or layers. Their registration and behavior fall outside this page.

## Key Takeaways

- The three leaves isolate tessellation level, geometry output length, and geometry invocation count while sharing one all-pixel image check.
- Fixed required specification values make the shaders portable across devices that expose the tessellation and geometry features; two values are used directly and the geometry-output values conservatively derive a legal 112-vertex shader. The tests do not chase implementation-specific maxima.
- Alternating green/yellow strips turn amplified primitive output into a tolerant coverage signal. Any black gap fails because every pixel must have high green and near-zero blue.
- A failure can come from the selected limit path or from shared pipeline, rasterization, copyback, and host-visibility operations. See `Failure Meaning` for the source-grounded distinctions.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Limit flags and case state | [`FlagBits` and `GridRenderTestCase`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L100) | Defines the three selected properties and their 64/5 and 32/4 values. |
| Geometry strip calculation | [`GridRenderTestCase` constructor](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L105-L145) | Derives the default and required-geometry strip sizes. |
| Generated shader programs | [`GridRenderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L147-L430) | Emits all five graphics stages and specializes them from the selected flags. |
| Exact image predicate | [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) | Defines the all-pixel green/blue threshold and error-mask output. |
| Resource setup, draw, and copyback | [`GridRenderTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L729) | Requires features, renders one patch, copies the image, and returns pass or fail. |
| Limit-family registration | [`createGeometryGridRenderLimitsTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L740-L761) | Registers `limits` and its three test case leaves. |
| Parent family placement | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places `limits` under `tessellation.geometry_interaction`. |
| Tessellation semantics | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines the control, fixed-function generation, and evaluation stages. |
| Geometry shader semantics | [Vulkan geometry chapter](../../../../vulkan-docs/src/chapters/geometry.adoc#geometry) | Defines primitive input, output strips, output vertex limits, and multiple invocations. |
| Required values | [Vulkan limit requirements](../../../../vulkan-docs/src/chapters/limits.adoc#limits-minmax) | Lists the minimum required maximum values used directly or as inputs to this family's geometry-strip calculation. |
