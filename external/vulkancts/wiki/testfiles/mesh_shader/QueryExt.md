## Overview

**Core question:** Do EXT mesh-shader queries report the expected primitive and shader-invocation counts across the registered draw, reset, retrieval, availability, command-buffer, and multiview paths?

- `vktMeshShaderQueryTestsEXT.cpp` implements the `mesh_shader.ext.query` test family. It combines an optional mesh-primitives query pool with a pipeline-statistics pool that can count task invocations, mesh invocations, or both.
- The source registers 24,680 exact `vk-default` test cases. Every case renders a deterministic image, and query cases also inspect counter values and, when requested, availability values.
- The matrix covers direct and indirect draw forms, grouped draw calls, task and mesh execution, query scope relative to the render pass, primary and secondary command buffers, and two-view rendering.
- This page explains the registered matrix, the generated geometry, query result layout, support gates, execution and checking rules, expected failure meaning, and source-controlled pruning.

## Background Knowledge

- **Query state and retrieval.** Each Vulkan query stores numerical results and has an available or unavailable state. Reset makes the query unavailable and its numerical result undefined; ending the query makes it available. Both `vkGetQueryPoolResults` and `vkCmdCopyQueryPoolResults` retrieve results [query operation](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation).
- **Mesh query counters.** `VK_QUERY_TYPE_MESH_PRIMITIVES_GENERATED_EXT` counts mesh-shader primitives that reach the fragment stage. Pipeline-statistics bits count task-shader and mesh-shader invocations [mesh shader queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-mesh-shader).
- **Multiview queries.** An active query in a multiview subpass uses one query index per enabled view. Vulkan permits implementation-dependent distribution between those indices, but their sum must equal the total for all views [multiview query operation](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation).

## Registration Hierarchy

```text
mesh_shader.ext.query
├── no_queries
├── prim_query
├── task_invs_query
├── mesh_invs_query
├── all_stats_query
└── all_queries
```

Each child is a query combination. Thirteen deeper path components select geometry, reset, access, wait behavior, draw form, integer width, availability, draw blocks, task use, query/render-pass ordering, view count, and command-buffer level. The complete construction loop is in [EXT query registration](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387-L1690).

## Parameter Dimensions and Observed Values

The exact `vk-default` list contains 24,680 leaves from [line 2063 through line 26742](../../../mustpass/main/vk-default/mesh-shader.txt#L2063-L26742). The path after `mesh_shader.ext.query` follows the dimension order below.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Query combination | `no_queries`, `prim_query`, `task_invs_query`, `mesh_invs_query`, `all_stats_query`, `all_queries` | Selects no query pool, one primitive pool, one statistics pool, or both pool types. | [query combinations](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1391-L1402) |
| Geometry | `points`, `lines`, `triangles` | Chooses mesh output topology and one, two, or three vertices per emitted primitive. | [geometry values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1444-L1452) |
| Reset | `no_reset`, `host_reset`, `reset_before`, `reset_after` | Selects ordinary retrieval, a post-check host reset, a command reset before retrieval, or a command reset after an in-command copy. | [reset values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1424-L1433) |
| Access | `copy`, `get` | Uses `vkCmdCopyQueryPoolResults` into a buffer or `vkGetQueryPoolResults` into host memory. | [access values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1435-L1442) |
| Wait behavior | `no_wait`, `wait` | Chooses `VK_QUERY_RESULT_PARTIAL_BIT` or `VK_QUERY_RESULT_WAIT_BIT`. | [flags](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L272-L278), [registered values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1472-L1479) |
| Draw call | `draw`, `indirect_draw`, `indirect_with_count_draw` | Executes direct commands, indirect command arrays, or indirect arrays with a count buffer. | [draw values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1404-L1412) |
| Result size | `32bit`, `64bit` | Selects the integer width of every result and availability item. | [result sizes](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1454-L1461) |
| Availability | `no_availability`, `with_availability` | Optionally appends one availability item to each query result. | [availability values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1463-L1470) |
| Draw blocks | `no_blocks`, `single_block`, `multiple_blocks` | Supplies `{}`, `{10}`, or `{10,20,30}` draws. Blocks change command count and the global draw-row offset. | [block values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1414-L1422) |
| Shader stages | `mesh_only`, `task_mesh` | Dispatches four mesh workgroups directly or two task workgroups that each emit two mesh workgroups. | [task values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1481-L1488), [workgroup rule](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L264-L270) |
| Query ordering | `include_rp`, `inside_rp` | Begins and ends queries around the whole render pass or within the render pass. | [ordering values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1490-L1497) |
| Views | `single_view`, `multi_view` | Uses one view or a two-bit view mask and two query indices. | [view values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1499-L1506) |
| Command buffers | `only_primary`, `with_secondary` | Records drawing in the primary buffer or executes a secondary buffer. | [command-buffer values](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1508-L1515) |

Default-mustpass coverage by query combination is exact: `no_queries` has 8 leaves; `prim_query` and `all_queries` have 4,560 each; `task_invs_query`, `mesh_invs_query`, and `all_stats_query` have 5,184 each.

## Behavior Parameters

The primary behavioral axis is the **query combination**. It changes which query pools exist, which device counters the test requests, how result records are sized, and which values the host validates. The other dimensions exercise each counter through different draw and query-control paths.

### `no_queries`: Drawing control without query accounting

This combination creates no query pools and does not require `meshShaderQueries`. It retains eight line-rendering paths that exercise drawing, task use, multiview, and secondary recording while the host checks only the color target.

### `prim_query`: Generated mesh primitive count

The case creates a `VK_QUERY_TYPE_MESH_PRIMITIVES_GENERATED_EXT` pool. The host sums its query slots and checks the emitted primitive total. Points and lines appear only in this primitive-query branch and the control branch; all three topologies emit 32 primitives per mesh workgroup.

### `task_invs_query`: Task invocation count

The statistics pool enables only `VK_QUERY_PIPELINE_STATISTIC_TASK_SHADER_INVOCATIONS_BIT_EXT`. `mesh_only` remains registered and produces an expected task count of zero, while `task_mesh` executes 24 task invocations per task workgroup.

### `mesh_invs_query`: Mesh invocation count

The statistics pool enables only `VK_QUERY_PIPELINE_STATISTIC_MESH_SHADER_INVOCATIONS_BIT_EXT`. Every draw ultimately launches four mesh workgroups, each with 40 local invocations, whether task shading is present or not.

### `all_stats_query`: Combined task and mesh statistics

One pipeline-statistics pool enables both bits. Results appear in pipeline-statistic bit order, with task invocations followed by mesh invocations for each view, then one optional availability item for that query.

### `all_queries`: Primitive and statistics pools together

This combination runs the primitive pool and the two-counter statistics pool over the same draws. The retrieval layout places all primitive records first, followed by the statistics records at a computed offset. Under two-view rendering, the maximum 64-bit layout has ten items: `(primitive, availability, task, mesh, availability)` for each view.

## Shader Analysis

The query operations and result checks are host-side, but the generated mesh shader fixes the exact work and primitive counts that the queries must report. One walkthrough covers the full triangle, multiple-block, indirect-count path. Task-shader variation is summarized instead of adding a second similar walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.query.all_queries.triangles.no_reset.get.wait.indirect_with_count_draw.64bit.with_availability.multiple_blocks.mesh_only.inside_rp.multi_view.with_secondary
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `all_queries` | Both the primitive pool and the two-counter statistics pool are active. |
| `triangles` | Each mesh workgroup emits 32 triangles from 96 vertices. |
| `multiple_blocks` | Three draw blocks contain 10, 20, and 30 draws, giving an image height of 240 rows. |
| `mesh_only` | Each draw launches four mesh workgroups without a task stage. |
| `indirect_with_count_draw` | The indirect command buffer supplies randomized X/Y/Z group counts, and a count buffer selects each block size. |
| `inside_rp.multi_view.with_secondary` | Queries and draws are recorded in a secondary command buffer inside a two-view render pass. |

#### Purpose

This mesh shader gives the host predictable work: 60 draws, four mesh workgroups per draw, 40 invocations per workgroup, and 32 triangles per workgroup. Its row mapping also produces a complete image in each view, so the test checks rendering independently of query data.

#### Structural Design

| Phase | Mesh-stage operation | Observable effect |
|-------|----------------------|-------------------|
| Workgroup setup | Reset `currentCol`, synchronize 40 local invocations, and derive a row from `prevDrawCalls`, `gl_DrawID`, and the shuffled workgroup coordinates. | Every dispatched mesh workgroup owns one of 240 rows. |
| Output sizing | Call `SetMeshOutputsEXT(96, 32)`. | The primitive counter has 32 generated triangles per workgroup. |
| Column allocation | Atomically claim a column and let the first 32 local invocations write one triangle each. | Every row covers all 32 image columns. |
| Fragment output | Rasterize the triangles; the fixed fragment shader writes a view-dependent blue or blue-green color. | The host can verify all draws and both views through image readback. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_mesh_shader : enable

/// Each mesh workgroup has 40 local invocations. Every dispatched workgroup emits 32 triangles.
layout (local_size_x=10, local_size_y=4, local_size_z=1) in;
layout (triangles) out;
layout (max_vertices=256, max_primitives=256) out;

/// The host updates this value before each indirect-count draw block so gl_DrawID maps to a global draw row.
layout (push_constant, std430) uniform PushConstants {
    uint prevDrawCalls;
} pc;

/// Workgroup-local allocation lets the 40 invocations claim the 32 output columns once each.
shared uint currentCol;

void main (void)
{
    atomicExchange(currentCol, 0u);
    barrier();

    const uint colCount = uint(32);
    const uint rowCount = uint(240);
    const uint rowsPerDraw = uint(4);

    const float pixWidth = 2.0 / float(colCount);
    const float pixHeight = 2.0 / float(rowCount);
    const float horDelta = pixWidth / 4.0;
    const float verDelta = (pixHeight * 3.0) / 8.0;

    const uint DrawIndex = uint(gl_DrawID);
    const uint currentWGIndex = (gl_WorkGroupID.x + gl_WorkGroupID.y + gl_WorkGroupID.z);
    const uint row = (pc.prevDrawCalls + DrawIndex) * rowsPerDraw + currentWGIndex;
    const uint vertsPerPrimitive = 3;

    SetMeshOutputsEXT(colCount * vertsPerPrimitive, colCount);

    const uint col = atomicAdd(currentCol, 1);
    if (col < colCount)
    {
        const float xCenter = (float(col) + 0.5) / colCount * 2.0 - 1.0;
        const float yCenter = (float(row) + 0.5) / rowCount * 2.0 - 1.0;

        const uint firstVert = col * vertsPerPrimitive;

        gl_MeshVerticesEXT[firstVert + 0].gl_Position = vec4(xCenter           , yCenter - verDelta, 0.0, 1.0);
        gl_MeshVerticesEXT[firstVert + 1].gl_Position = vec4(xCenter - horDelta, yCenter + verDelta, 0.0, 1.0);
        gl_MeshVerticesEXT[firstVert + 2].gl_Position = vec4(xCenter + horDelta, yCenter + verDelta, 0.0, 1.0);
        gl_PrimitiveTriangleIndicesEXT[col] = uvec3(firstVert, firstVert + 1, firstVert + 2);
    }
}
```

#### Additional Info

- The fragment shader adds `GL_EXT_multiview` for this case and writes `float(gl_ViewIndex)` to green, so view 0 is blue and view 1 is blue-green [fragment generation](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L412-L418).
- The push constant advances by the accumulated draw count before each indirect-count block. Each count command sets `maxDrawCount` to twice the actual block size, so the count buffer determines the executed draw count [indirect-count recording](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L641-L670).
- The EXT mesh build helper targets SPIR-V 1.4 [build options](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L141-L144).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Geometry | Points use one vertex and `gl_PrimitivePointIndicesEXT`; lines use two vertices and `gl_PrimitiveLineIndicesEXT`; triangles use three vertices. | [geometry branches](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L461-L499) |
| Draw blocks | The total draw count changes the generated `rowCount`; `no_blocks` still creates a one-row image but emits no geometry. | [image-height rule](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L253-L262), [shader dimensions](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L445-L460) |
| Task use | `task_mesh` adds task payload declarations, derives the draw index from `td.drawIndex`, and maps each task workgroup to two mesh workgroups. | [task-dependent mesh generation](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L404-L410), [task shader generation](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L505-L529) |
| Multiview | The mesh shader stays unchanged; the fragment shader uses `gl_ViewIndex`, and the render pass supplies a two-bit view mask. | [fragment generation](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L412-L418), [render-pass view mask](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L842-L853) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 130
; Schema: 0
               OpCapability DrawParameters
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %currentCol %gl_DrawID %gl_WorkGroupID %pc %gl_MeshVerticesEXT %gl_PrimitiveTriangleIndicesEXT
               OpExecutionMode %main LocalSize 10 4 1
               OpExecutionMode %main OutputVertices 256
               OpExecutionMode %main OutputPrimitivesEXT 256
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %currentCol "currentCol"
               OpName %DrawIndex "DrawIndex"
               OpName %gl_DrawID "gl_DrawID"
               OpName %currentWGIndex "currentWGIndex"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %row "row"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "prevDrawCalls"
               OpName %pc "pc"
               OpName %col "col"
               OpName %xCenter "xCenter"
               OpName %yCenter "yCenter"
               OpName %firstVert "firstVert"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %gl_PrimitiveTriangleIndicesEXT "gl_PrimitiveTriangleIndicesEXT"
               OpDecorate %gl_DrawID BuiltIn DrawIndex
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %gl_PrimitiveTriangleIndicesEXT BuiltIn PrimitiveTriangleIndicesEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Workgroup_uint = OpTypePointer Workgroup %uint
 %currentCol = OpVariable %_ptr_Workgroup_uint Workgroup
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
   %uint_264 = OpConstant %uint 264
%_ptr_Function_uint = OpTypePointer Function %uint
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
  %gl_DrawID = OpVariable %_ptr_Input_int Input
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%PushConstants = OpTypeStruct %uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_4 = OpConstant %uint 4
    %uint_96 = OpConstant %uint 96
    %uint_32 = OpConstant %uint 32
       %bool = OpTypeBool
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
  %float_0_5 = OpConstant %float 0.5
   %float_32 = OpConstant %float 32
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
  %float_240 = OpConstant %float 240
     %uint_3 = OpConstant %uint 3
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
   %uint_256 = OpConstant %uint 256
%_arr_gl_MeshPerVertexEXT_uint_256 = OpTypeArray %gl_MeshPerVertexEXT %uint_256
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_256
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 Output
%float_0_00312500005 = OpConstant %float 0.00312500005
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%float_0_015625 = OpConstant %float 0.015625
%_arr_v3uint_uint_256 = OpTypeArray %v3uint %uint_256
%_ptr_Output__arr_v3uint_uint_256 = OpTypePointer Output %_arr_v3uint_uint_256
%gl_PrimitiveTriangleIndicesEXT = OpVariable %_ptr_Output__arr_v3uint_uint_256 Output
%_ptr_Output_v3uint = OpTypePointer Output %v3uint
    %uint_10 = OpConstant %uint 10
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_10 %uint_4 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %DrawIndex = OpVariable %_ptr_Function_uint Function
%currentWGIndex = OpVariable %_ptr_Function_uint Function
        %row = OpVariable %_ptr_Function_uint Function
        %col = OpVariable %_ptr_Function_uint Function
    %xCenter = OpVariable %_ptr_Function_float Function
    %yCenter = OpVariable %_ptr_Function_float Function
  %firstVert = OpVariable %_ptr_Function_uint Function
         %11 = OpAtomicExchange %uint %currentCol %uint_1 %uint_0 %uint_0
               OpControlBarrier %uint_2 %uint_2 %uint_264
         %19 = OpLoad %int %gl_DrawID
         %20 = OpBitcast %uint %19
               OpStore %DrawIndex %20
         %26 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %27 = OpLoad %uint %26
         %28 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %29 = OpLoad %uint %28
         %30 = OpIAdd %uint %27 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %currentWGIndex %33
         %40 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %41 = OpLoad %uint %40
         %42 = OpLoad %uint %DrawIndex
         %43 = OpIAdd %uint %41 %42
         %45 = OpIMul %uint %43 %uint_4
         %46 = OpLoad %uint %currentWGIndex
         %47 = OpIAdd %uint %45 %46
               OpStore %row %47
               OpSetMeshOutputsEXT %uint_96 %uint_32
         %51 = OpAtomicIAdd %uint %currentCol %uint_1 %uint_0 %uint_1
               OpStore %col %51
         %52 = OpLoad %uint %col
         %54 = OpULessThan %bool %52 %uint_32
               OpSelectionMerge %56 None
               OpBranchConditional %54 %55 %56
         %55 = OpLabel
         %60 = OpLoad %uint %col
         %61 = OpConvertUToF %float %60
         %63 = OpFAdd %float %61 %float_0_5
         %65 = OpFDiv %float %63 %float_32
         %67 = OpFMul %float %65 %float_2
         %69 = OpFSub %float %67 %float_1
               OpStore %xCenter %69
         %71 = OpLoad %uint %row
         %72 = OpConvertUToF %float %71
         %73 = OpFAdd %float %72 %float_0_5
         %75 = OpFDiv %float %73 %float_240
         %76 = OpFMul %float %75 %float_2
         %77 = OpFSub %float %76 %float_1
               OpStore %yCenter %77
         %79 = OpLoad %uint %col
         %81 = OpIMul %uint %79 %uint_3
               OpStore %firstVert %81
         %89 = OpLoad %uint %firstVert
         %90 = OpIAdd %uint %89 %uint_0
         %91 = OpLoad %float %xCenter
         %92 = OpLoad %float %yCenter
         %94 = OpFSub %float %92 %float_0_00312500005
         %96 = OpCompositeConstruct %v4float %91 %94 %float_0 %float_1
         %98 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %90 %int_0
               OpStore %98 %96
         %99 = OpLoad %uint %firstVert
        %100 = OpIAdd %uint %99 %uint_1
        %101 = OpLoad %float %xCenter
        %103 = OpFSub %float %101 %float_0_015625
        %104 = OpLoad %float %yCenter
        %105 = OpFAdd %float %104 %float_0_00312500005
        %106 = OpCompositeConstruct %v4float %103 %105 %float_0 %float_1
        %107 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %100 %int_0
               OpStore %107 %106
        %108 = OpLoad %uint %firstVert
        %109 = OpIAdd %uint %108 %uint_2
        %110 = OpLoad %float %xCenter
        %111 = OpFAdd %float %110 %float_0_015625
        %112 = OpLoad %float %yCenter
        %113 = OpFAdd %float %112 %float_0_00312500005
        %114 = OpCompositeConstruct %v4float %111 %113 %float_0 %float_1
        %115 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %109 %int_0
               OpStore %115 %114
        %119 = OpLoad %uint %col
        %120 = OpLoad %uint %firstVert
        %121 = OpLoad %uint %firstVert
        %122 = OpIAdd %uint %121 %uint_1
        %123 = OpLoad %uint %firstVert
        %124 = OpIAdd %uint %123 %uint_2
        %125 = OpCompositeConstruct %v3uint %120 %122 %124
        %127 = OpAccessChain %_ptr_Output_v3uint %gl_PrimitiveTriangleIndicesEXT %119
               OpStore %127 %125
               OpBranch %56
         %56 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a `32 x max(imageHeight, 1)` color image with one or two array layers. The image height is total draw count times four mesh workgroups per draw. A host-visible transfer-destination buffer receives an exact image copy.
- The primitive pool uses `VK_QUERY_TYPE_MESH_PRIMITIVES_GENERATED_EXT`. The statistics pool uses `VK_QUERY_TYPE_PIPELINE_STATISTICS` with task and/or mesh invocation bits. Each pool has one query per view [query-pool creation](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L963-L1004).
- Result width is four or eight bytes. A primitive record contains one count plus optional availability. A statistics record contains its selected task and mesh counters plus one optional availability. The primitive region is multiplied by view count before the statistics offset [result layout](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L311-L338).
- Before use, a separate primary command buffer resets every query slot and the host waits for completion. `reset_before` adds another reset before retrieval. `reset_after` records the reset after copied results. `host_reset` performs `vkResetQueryPool` after normal checking and retrieves availability again [initial and command resets](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1028-L1036), [retrieval-adjacent resets](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1136-L1152), [host-reset check](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1303-L1377).
- Primary-only paths place begin, draws, and end either inside the render pass or around it. Secondary paths either perform the whole query in the secondary buffer inside the render pass, or inherit an active primary pipeline-statistics query when `include_rp` is selected [four command-buffer arrangements](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1041-L1125).
- Direct draws issue one command per draw. Indirect draws issue one command per block over an array of randomized X/Y/Z workgroup counts. Indirect-count draws also read each block size from a count buffer [draw recording](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L575-L677).
- `copy` records query copies before submission completes. `get` requests host results before waiting on the fence when possible; without `WAIT_BIT`, `VK_NOT_READY` is accepted. `reset_before` waits for the reset to execute before the host attempts retrieval [access paths](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1139-L1196).
- The image check requires exact blue output in view 0, blue-green output in view 1, or the clear color when no draws execute. This catches missing, duplicate, or misplaced mesh work independently of the query counters [image verification](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1198-L1226).
- Expected single-view totals are `imageHeight * 32` primitives, `imageHeight * 24 / 2` task invocations when the task stage exists, and `imageHeight * 40` mesh invocations. For a completed waiting query, the source accepts a summed value from the single-view total through that total times view count. Vulkan independently permits implementation-dependent distribution among per-view query slots and requires their sum to represent all views. Without wait, zero becomes the lower bound for partial results. A value reset before retrieval is ignored because Vulkan defines it as undefined [counter calculation and checking](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L782-L807), [query parsing](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1228-L1300).
- Requested availability must be zero after `reset_before` and nonzero after a waiting, non-reset query. The post-completion host-reset path also requires zero availability and deliberately ignores numerical data [availability checking](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L754-L780), [host-reset verification](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1303-L1377).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_queries` | Mesh draw, render-pass, secondary-command-buffer, or image verification failure independent of query accounting. |
| `prim_query` | Mesh primitive query creation, primitive counting, reset/retrieval, or selected draw/control path failure. |
| `task_invs_query` | Task invocation statistics, task-to-mesh execution, reset/retrieval, or selected draw/control path failure. |
| `mesh_invs_query` | Mesh invocation statistics, reset/retrieval, or selected draw/control path failure. |
| `all_stats_query` | Combined task/mesh statistic ordering or sizing, either stage counter, reset/retrieval, or selected draw/control path failure. |
| `all_queries` | Coordination of separate primitive and statistics pools, result offsets/sizing, any selected counter, reset/retrieval, or selected draw/control path failure. |

Shared failures can also come from incorrect 32/64-bit parsing, availability handling, wait/partial semantics, multiview aggregation, or query inheritance.

### Cause Analysis

#### Draw execution or image verification failure

**Possible failure symptoms:** The color comparison reports an incorrect pixel or layer, including query-free cases where no counter check runs.

**Possible implementation causes:** A direct or indirect mesh draw may execute the wrong workgroup count, `gl_DrawID` or the block push constant may map work to the wrong row, secondary execution may omit work, or the mesh/fragment pipeline may write the wrong view layer. The separate image check prevents a plausible counter from hiding missing rendering.

#### Primitive or invocation counter failure

**Possible failure symptoms:** A summed primitive, task, or mesh value falls outside the source-derived range. A task counter can also be nonzero for `mesh_only`.

**Possible implementation causes:** The implementation may increment the wrong EXT query counter, count the wrong number of stage invocations, or mishandle the active query scope around draw commands. The specification defines primitive counts at the point mesh output reaches fragment processing and increments task and mesh statistics whenever each respective shader is invoked [mesh query definitions](../../../../vulkan-docs/src/chapters/queries.adoc#queries-mesh-shader), [pipeline statistics definitions](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

#### Result layout or retrieval failure

**Possible failure symptoms:** One query type passes alone but combined statistics or `all_queries` reads the wrong value; failures may depend on 32/64-bit width, availability, view count, or `copy` versus `get`.

**Possible implementation causes:** The implementation or CTS-side interpretation may use the wrong statistic bit order, stride, item width, per-query availability placement, or offset between query pools. Vulkan requires statistics in bit order and appends availability directly after each query result [query result layout](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation-memorylayout).

#### Reset, wait, or availability failure

**Possible failure symptoms:** A reset query reports nonzero availability, a completed waiting query reports zero availability, or a host retrieval returns an unexpected status. Numerical data from a reset query is not itself treated as a failure.

**Possible implementation causes:** Reset may fail to make the query unavailable, wait may fail to order retrieval after query completion, or retrieval may report stale availability. Vulkan defines reset values as undefined, permits `VK_NOT_READY` without wait, and requires the availability item to indicate completion [query state](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation), [query result retrieval](../../../../vulkan-docs/src/chapters/queries.adoc#vkGetQueryPoolResults).

#### Inheritance or multiview query failure

**Possible failure symptoms:** Failures appear only with `with_secondary.include_rp` pipeline statistics or only with `multi_view`; the summed multiview total or availability may be wrong even though the rendered layers pass.

**Possible implementation causes:** A secondary command buffer may not inherit the active pipeline-statistics state declared through `VkCommandBufferInheritanceInfo`. In multiview, an implementation may allocate or aggregate the consecutive query slots incorrectly. Vulkan permits any per-view distribution but requires the sum to reflect all enabled views [query inheritance and multiview](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation).

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_mesh_shader` and the `meshShader` feature. `task_mesh` also requires `taskShader` [shared support helper](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139).
- Any nonempty query combination requires `meshShaderQueries`. The specification ties this feature to the mesh-primitives query type and task/mesh pipeline-statistics bits [case support](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L537-L547), [`meshShaderQueries`](../../../../vulkan-docs/src/chapters/features.adoc#features-meshShaderQueries).
- An inherited query requires the core `inheritedQueries` feature. `host_reset` requires `VK_EXT_host_query_reset` [case support](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L549-L553).
- `multi_view` requires `multiviewMeshShader` and `maxMeshMultiviewViewCount >= 2` [multiview support](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L555-L563), [mesh multiview limit](../../../../vulkan-docs/src/chapters/limits.adoc#limits-maxMeshMultiviewViewCount).

### Design-based pruning

- `no_queries` keeps only lines, `no_reset`, `copy`, `no_wait`, direct draw, 32-bit, no availability, `multiple_blocks`, and `inside_rp`. These values leave eight combinations across task use, view count, and command-buffer type.
- Statistics-only combinations use triangles. Points and lines remain only for `prim_query`, `all_queries`, and `no_queries`, because geometry changes the primitive count but not invocation accounting.
- Non-triangle cases retain direct draw, 32-bit results, no availability, and multiple blocks. These exclusions reduce duplicate topology coverage.
- `get.reset_after` is excluded because host retrieval occurs after submission, so an in-command reset cannot be placed after that access. `reset_before.wait` is excluded because waiting on a query that was reset and never ended again would not finish.
- Multiview is excluded from `include_rp`; multiview queries must begin and end in the same subpass. Inherited primitive queries are excluded for the `with_secondary.include_rp` arrangement by `VUID-vkCmdExecuteCommands-commandBuffer-07594` [matrix pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1517-L1647).

## Key Takeaways

- The six direct children select which EXT mesh counters exist. Thirteen further dimensions stress the same accounting through reset, retrieval, draw, command-buffer, and multiview paths.
- Rendering and query validation are independent. A case must produce the exact image before its query results can be accepted.
- Reset changes availability and makes numerical results undefined. Non-waiting retrieval accepts partial counts and `VK_NOT_READY`; waiting retrieval requires final availability.
- Multiview checks the sum over two query slots because Vulkan does not prescribe how an implementation distributes counts between views.
- See `## Failure Meaning` for how failures separate draw execution, counter accounting, layout/retrieval, reset/availability, inheritance, and multiview causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter model | [`TestParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L177-L338) | Defines draw totals, result flags, inherited-query choice, view count, and packed result sizes. |
| Shader generation | [`MeshQueryCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L399-L530) | Builds the exact fragment, mesh, and optional task shaders. |
| Support gates | [`MeshQueryCase::checkSupport`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L537-L564) | Applies mesh/task, query, inheritance, host-reset, and multiview requirements. |
| Draw commands | [`recordDraws`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L575-L677) | Records direct, indirect, indirect-count, and block-specific drawing. |
| Counter and availability checks | [query-value helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L731-L807) | Defines width parsing and reset/wait-sensitive acceptance rules. |
| Runtime execution | [`MeshQueryInstance::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L870-L1380) | Creates resources and pools, records query arrangements, retrieves results, and checks image/query data. |
| Registration and pruning | [`createMeshShaderQueryTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387-L1690) | Generates all path dimensions and excludes invalid or duplicate combinations. |
| EXT support utilities | [mesh support and SPIR-V 1.4 options](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L148) | Supplies shared feature checks and shader build target. |
| Exact default coverage | [`vk-default` query block](../../../mustpass/main/vk-default/mesh-shader.txt#L2063-L26742) | Lists all 24,680 query test cases included in the default mustpass. |
| Query semantics | [Vulkan queries chapter](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation) | Defines state, retrieval, result layout, wait/partial behavior, inheritance, multiview, and mesh counters. |
| Mesh query features | [Vulkan mesh-shader feature definitions](../../../../vulkan-docs/src/chapters/features.adoc#features-meshShaderQueries) | Defines the feature gates for mesh query pools and multiview mesh pipelines. |
