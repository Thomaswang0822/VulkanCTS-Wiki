## Overview

**Core question:** Do generated mesh-task draws consume the selected command and shader state, then produce the expected image or storage-buffer values?

- [`vktDGCGraphicsMeshTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1) implements `dgc.ext.graphics.mesh` and registers the direct test families `token_draw`, `token_draw_count`, `misc`, and `conditional_rendering`.
- `token_draw` uses `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT`; `token_draw_count` uses `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_COUNT_EXT`.
- The regular cases generate a 32 by 32 image from per-pixel triangles. The `misc` cases either write integer results without a fragment shader or stress large sequence counts.
- The matrix varies pipeline construction, task shaders, execution sets, explicit preprocessing, sequence order, and direct versus count-form draws. The host checks the rendered image or copied storage-buffer data.

## Background Knowledge

- A mesh shader workgroup emits vertices and primitives directly. An optional task shader runs first and calls `EmitMeshTasksEXT` to create mesh workgroups. Without a task shader, the draw launches mesh workgroups directly. See [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc).
- A DGC layout places state tokens before an action token. The mesh action tokens consume `VkDrawMeshTasksIndirectCommandEXT`, or a count record that points to mesh draw records. Explicit preprocessing uses `vkCmdPreprocessGeneratedCommandsEXT` before `vkCmdExecuteGeneratedCommandsEXT`; separate command buffers need an explicit synchronization barrier. See [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout).
- `taskPayloadSharedEXT` carries data from a task shader to its mesh workgroups. It is shader-local payload storage, not a host-created descriptor resource.

## Registration Hierarchy

```text
dgc.ext.graphics.mesh
├── conditional_rendering (registration only)
├── misc
├── token_draw
└── token_draw_count
```

`conditional_rendering` is attached by this registration function but implemented by [`createDGCGraphicsMeshConditionalTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L680-L718). Its detailed `general` and `preprocess` paths remain in [the legacy conditional-rendering page](vktDGCGraphicsMeshConditionalTestsExt.md).

## Parameter Dimensions and Observed Values

The registration loops in [`createDGCGraphicsMeshTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2320-L2424) produce 120 `token_draw` cases, 120 `token_draw_count` cases, 32 `misc` cases, and 36 delegated `conditional_rendering` cases, for 308 mustpass paths under `dEQP-VK.dgc.ext.graphics.mesh`.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Direct test family | `token_draw`, `token_draw_count`, `misc`, `conditional_rendering` | Selects the mesh action, count-form action, supporting paths, or delegated conditional rendering. | [registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2320-L2424), [mustpass](../../../mustpass/main/vk-default/dgc.txt#L1806-L2113) |
| Draw form | `token_draw`, `token_draw_count` | Direct cases use eight generated sequences. Count-form cases group the eight direct draws into four indirect draw sequences, each with its own count record and indirect mesh-draw records. | [draw type and registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L159-L163), [count buffers](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L791-L819) |
| Pipeline construction | `monolithic`, `shader_objects`, `gpl_fast`, `gpl_optimized`, `gpl_mix_base_fast`, `gpl_mix_base_opt` | Selects a monolithic pipeline, shader objects, or graphics pipeline library construction. The mix forms alternate fast and optimized library construction per sequence. | [pipeline cases](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L165-L208), [pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L935-L999) |
| Task shader | no suffix, `_with_task_shader` | Uses direct mesh workgroup indexing or task payload indexing. | [task parameter](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L218-L306), [shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L449-L559) |
| Execution set | no suffix, `_with_execution_set` | Selects pipeline or shader-object entries per sequence and changes shader colors and task column order. | [execution-set construction](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L926-L1047) |
| Preprocessing | no suffix, `_preprocess_same_state_cmd_buffer`, `_preprocess_separate_state_cmd_buffer` | Chooses no preprocessing, preprocessing with the state command buffer, or preprocessing with a separate state command buffer. | [preprocess cases](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2344-L2352), [preprocess flow](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1241-L1314) |
| Sequence order | no suffix, `_unordered` | Adds `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`; expected colors come from sequence data rather than assumed processing order. | [layout flags](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1049-L1080), [reference mapping](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1504-L1537) |
| `misc` no-fragment construction | `no_frag_shader_monolithic`, `no_frag_shader_shader_objects`, `no_frag_shader_gpl_fast`, with `_with_task`, `_with_ies`, and `_preprocess` combinations | Writes integer values from task or mesh shaders while rasterization is discarded. | [no-fragment registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2391-L2410), [no-fragment parameters](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1549-L1608) |
| `misc` sequence count | `many_sequences_64`, `many_sequences_1024`, `many_sequences_8192`, `many_sequences_131072`, each with optional `_task` | Stresses one generated sequence per output counter, with an optional task shader. | [many-sequence registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2412-L2419) |

The registered regular-case name is the concatenation of the pipeline value, optional `_with_task_shader`, optional `_with_execution_set`, one preprocessing suffix, and optional `_unordered`. The registration skips only `gpl_mix_base_fast` and `gpl_mix_base_opt` without `_with_execution_set`. `token_draw` and `token_draw_count` use the same matrix, so the exact suffix sets above apply to both families.

## Behavior Parameters

The primary behavioral axis is the registered test family. The other dimensions alter the command representation, shader state, or execution arrangement around that family.

### `token_draw` | Direct mesh-task action

Each sequence ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` and a `VkDrawMeshTasksIndirectCommandEXT`. Its three group counts are initialized to one in two dimensions and a pseudorandom row count in the remaining dimension. Without a task shader, each launched workgroup handles one row and its 32 invocations emit the row's 32 triangles. With a task shader, 16 task invocations prepare two column indices each, and the task shader launches the selected number of mesh workgroups for the row.

### `token_draw_count` | Count-form mesh-task action

Each sequence ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_COUNT_EXT`. The eight direct draws are pseudorandomly grouped into four indirect draws. Each group has its own indirect buffer, group count, and stride, with up to three padding records between mesh draw records. The push-constant token carries the index of the first direct draw in the group, and the shader uses `gl_DrawID` to select the record within that group.

### `misc` | No-fragment and many-sequence paths

The no-fragment cases use mesh and optional task shaders that write predictable integers to one or two storage buffers, then call `SetMeshOutputsEXT(0, 0)` or `EmitMeshTasksEXT(1, 1, 1)`. The many-sequence cases write one atomic increment per sequence to a one-element-per-sequence output buffer. These cases test generated execution and shader-stage state without relying on rasterization.

### `conditional_rendering` | Delegated conditional mesh execution

This direct child is registered by this file, but its cases are created by `createDGCGraphicsMeshConditionalTestsExt`. The implementation owns the conditional-rendering behavior, so this page records the registration boundary rather than restating that family's matrix.

## Shader Analysis

The regular cases generate GLSL in `DGCMeshDrawCase::initPrograms`. The representative path below is the direct `token_draw` case without a task shader or execution set. Its mesh shader maps a flattened workgroup ID to a row, maps each local invocation to one column, copies the three vertices for that pixel triangle, and emits the primitive. The fragment shader combines the mesh outputs with a selected blue value. Task-shader and execution-set differences are summarized after the walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.mesh.token_draw.monolithic
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `token_draw` | Uses `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT`. |
| `monolithic` | Uses one ordinary graphics pipeline without an execution set. |
| no `_with_task_shader` | Mesh workgroups map directly to image rows. |
| no `_with_execution_set` | The shaders use red `0.25`, green `0.0`, and blue `1.0`. |
| no preprocess or `_unordered` suffix | The generated commands execute without explicit preprocessing or unordered-sequence layout usage. |

#### Purpose

This shader path checks the direct mesh action. Each generated draw supplies group counts and a sequence base row. Each mesh workgroup emits the triangles for one row, and each local invocation emits one pixel triangle.

#### Structural Design

| Step | Shader or generated-command action | Observable result |
|---|---|---|
| 1 | The sequence-index token supplies the sequence value, which selects `baseRow`. | The workgroup starts at the rows assigned to that sequence. |
| 2 | `getWorkGroupIndex` flattens `gl_WorkGroupID` using `gl_NumWorkGroups`. | The mesh shader handles the correct row even when X, Y, or Z carries the dispatch count. |
| 3 | Each of 32 local invocations reads three vertices and writes one primitive. | The row's pixel triangles cover their intended pixel centers. |
| 4 | The fragment shader writes the mesh colors and blue `1.0`. | The host can compare the copied color image with its reference. |

#### Shader Code

Reconstructed GLSL for the representative mesh stage:

```glsl
#version 460
#extension GL_EXT_mesh_shader : enable
struct VertexData { vec4 position; vec4 extraData; };
layout(set=0, binding=0, std430) readonly buffer VertexDataBlock { VertexData vertexData[]; } vtxData;
layout(set=0, binding=1, std430) readonly buffer DirectDrawBaseRowBlock { uint baseRow[]; } directDrawData;
layout(push_constant, std430) uniform PushConstantBlock { uint width; uint height; uint baseDrawIndex; } pc;
layout(local_size_x=32) in;
layout(triangles) out;
layout(max_vertices=96, max_primitives=32) out;
layout(location=0) out perprimitiveEXT float redColor[];
layout(location=1) out flat float greenColor[];
uint getWorkGroupIndex() {
    return gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z +
           gl_NumWorkGroups.x * gl_WorkGroupID.y + gl_WorkGroupID.x;
}
void main() {
    const uint triangleVertices = 3u;
    const uint wgIndex = getWorkGroupIndex();
    const uint rowIndex = directDrawData.baseRow[pc.baseDrawIndex] + wgIndex;
    const uint srcPrim = rowIndex * pc.width + gl_LocalInvocationIndex;
    const uint srcBaseVertex = srcPrim * triangleVertices;
    const uint dstPrim = gl_LocalInvocationIndex;
    const uint dstBaseVertex = dstPrim * triangleVertices;
    SetMeshOutputsEXT(96, 32);
    for (uint i = 0u; i < triangleVertices; ++i) {
        const uint dstIdx = dstBaseVertex + i;
        const uint srcIdx = srcBaseVertex + i;
        gl_MeshVerticesEXT[dstIdx].gl_Position = vtxData.vertexData[srcIdx].position;
        gl_MeshVerticesEXT[dstIdx].gl_PointSize = 1.0;
        gl_MeshVerticesEXT[dstIdx].gl_ClipDistance[0] = vtxData.vertexData[srcIdx].extraData.x;
        gl_MeshVerticesEXT[dstIdx].gl_CullDistance[0] = vtxData.vertexData[srcIdx].extraData.y;
        greenColor[dstIdx] = 0.0;
    }
    gl_PrimitiveTriangleIndicesEXT[dstPrim] = uvec3(dstBaseVertex, dstBaseVertex + 1, dstBaseVertex + 2);
    redColor[dstPrim] = 0.25;
}
```

#### Additional Info

- The source's task shader uses a 16-invocation workgroup. Each invocation writes two entries in `TaskData.columnIndices`, and `EmitMeshTasksEXT(cb.colsPerRow[rowIndex], 1, 1)` controls coverage.
- Direct mesh cases use `gl_LocalInvocationIndex` as the column. Task cases use `td.columnIndices[wgIndex]`, so the task shader can select a permutation of columns.
- Execution-set cases generate two mesh shaders, two fragment shaders, and, when requested, two task shaders. The selected task shader can reverse the column order. The expected red and green values come from the mesh shader, and the expected blue value comes from the fragment shader.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Task shader | Adds `TaskData`, a coverage buffer, a 16-invocation task stage, and one-invocation mesh workgroups. | [task and mesh generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L429-L559) |
| Execution set | Selects alternate mesh and fragment colors and can select ascending or descending task column indices. | [execution-set shader indices](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L926-L1047) |
| Draw form | Direct cases use sequence-index data and a mesh draw record; count-form cases use `gl_DrawID`, a push-constant base index, and grouped indirect records. | [DGC data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1049-L1203) |
| Pipeline construction | Uses ordinary pipelines, `VkShaderEXT` objects, or graphics pipeline libraries without changing the shader mapping. | [pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L935-L999) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 160
; Schema: 0
               OpCapability ClipDistance
               OpCapability CullDistance
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %gl_NumWorkGroups %gl_WorkGroupID %directDrawData %pc %gl_LocalInvocationIndex %gl_MeshVerticesEXT %vtxData %greenColor %gl_PrimitiveTriangleIndicesEXT %redColor
               OpExecutionMode %main LocalSize 32 1 1
               OpExecutionMode %main OutputVertices 96
               OpExecutionMode %main OutputPrimitivesEXT 32
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %getWorkGroupIndex_ "getWorkGroupIndex("
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %wgIndex "wgIndex"
               OpName %rowIndex "rowIndex"
               OpName %DirectDrawBaseRowBlock "DirectDrawBaseRowBlock"
               OpMemberName %DirectDrawBaseRowBlock 0 "baseRow"
               OpName %directDrawData "directDrawData"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "width"
               OpMemberName %PushConstantBlock 1 "height"
               OpMemberName %PushConstantBlock 2 "baseDrawIndex"
               OpName %pc "pc"
               OpName %srcBasePrim "srcBasePrim"
               OpName %srcPrim "srcPrim"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %srcBaseVertex "srcBaseVertex"
               OpName %dstPrim "dstPrim"
               OpName %dstBaseVertex "dstBaseVertex"
               OpName %i "i"
               OpName %dstIdx "dstIdx"
               OpName %srcIdx "srcIdx"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %VertexData "VertexData"
               OpMemberName %VertexData 0 "position"
               OpMemberName %VertexData 1 "extraData"
               OpName %VertexDataBlock "VertexDataBlock"
               OpMemberName %VertexDataBlock 0 "vertexData"
               OpName %vtxData "vtxData"
               OpName %greenColor "greenColor"
               OpName %gl_PrimitiveTriangleIndicesEXT "gl_PrimitiveTriangleIndicesEXT"
               OpName %redColor "redColor"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %DirectDrawBaseRowBlock Block
               OpMemberDecorate %DirectDrawBaseRowBlock 0 NonWritable
               OpMemberDecorate %DirectDrawBaseRowBlock 0 Offset 0
               OpDecorate %directDrawData NonWritable
               OpDecorate %directDrawData Binding 1
               OpDecorate %directDrawData DescriptorSet 0
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpMemberDecorate %PushConstantBlock 2 Offset 8
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpMemberDecorate %VertexData 0 Offset 0
               OpMemberDecorate %VertexData 1 Offset 16
               OpDecorate %_runtimearr_VertexData ArrayStride 32
               OpDecorate %VertexDataBlock Block
               OpMemberDecorate %VertexDataBlock 0 NonWritable
               OpMemberDecorate %VertexDataBlock 0 Offset 0
               OpDecorate %vtxData NonWritable
               OpDecorate %vtxData Binding 0
               OpDecorate %vtxData DescriptorSet 0
               OpDecorate %greenColor Flat
               OpDecorate %greenColor Location 1
               OpDecorate %gl_PrimitiveTriangleIndicesEXT BuiltIn PrimitiveTriangleIndicesEXT
               OpDecorate %redColor Location 0
               OpDecorate %redColor PerPrimitiveEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
          %7 = OpTypeFunction %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Function_uint = OpTypePointer Function %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
%DirectDrawBaseRowBlock = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_DirectDrawBaseRowBlock = OpTypePointer StorageBuffer %DirectDrawBaseRowBlock
%directDrawData = OpVariable %_ptr_StorageBuffer_DirectDrawBaseRowBlock StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
      %int_2 = OpConstant %int 2
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
     %uint_3 = OpConstant %uint 3
    %uint_96 = OpConstant %uint 96
    %uint_32 = OpConstant %uint 32
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_96 = OpTypeArray %gl_MeshPerVertexEXT %uint_96
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_96
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 Output
 %VertexData = OpTypeStruct %v4float %v4float
%_runtimearr_VertexData = OpTypeRuntimeArray %VertexData
%VertexDataBlock = OpTypeStruct %_runtimearr_VertexData
%_ptr_StorageBuffer_VertexDataBlock = OpTypePointer StorageBuffer %VertexDataBlock
    %vtxData = OpVariable %_ptr_StorageBuffer_VertexDataBlock StorageBuffer
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
      %int_3 = OpConstant %int 3
%_arr_float_uint_96 = OpTypeArray %float %uint_96
%_ptr_Output__arr_float_uint_96 = OpTypePointer Output %_arr_float_uint_96
 %greenColor = OpVariable %_ptr_Output__arr_float_uint_96 Output
    %float_0 = OpConstant %float 0
%_arr_v3uint_uint_32 = OpTypeArray %v3uint %uint_32
%_ptr_Output__arr_v3uint_uint_32 = OpTypePointer Output %_arr_v3uint_uint_32
%gl_PrimitiveTriangleIndicesEXT = OpVariable %_ptr_Output__arr_v3uint_uint_32 Output
%_ptr_Output_v3uint = OpTypePointer Output %v3uint
%_arr_float_uint_32 = OpTypeArray %float %uint_32
%_ptr_Output__arr_float_uint_32 = OpTypePointer Output %_arr_float_uint_32
   %redColor = OpVariable %_ptr_Output__arr_float_uint_32 Output
 %float_0_25 = OpConstant %float 0.25
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_32 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %wgIndex = OpVariable %_ptr_Function_uint Function
   %rowIndex = OpVariable %_ptr_Function_uint Function
%srcBasePrim = OpVariable %_ptr_Function_uint Function
    %srcPrim = OpVariable %_ptr_Function_uint Function
%srcBaseVertex = OpVariable %_ptr_Function_uint Function
    %dstPrim = OpVariable %_ptr_Function_uint Function
%dstBaseVertex = OpVariable %_ptr_Function_uint Function
          %i = OpVariable %_ptr_Function_uint Function
     %dstIdx = OpVariable %_ptr_Function_uint Function
     %srcIdx = OpVariable %_ptr_Function_uint Function
         %39 = OpFunctionCall %uint %getWorkGroupIndex_
               OpStore %wgIndex %39
         %52 = OpAccessChain %_ptr_PushConstant_uint %pc %int_2
         %53 = OpLoad %uint %52
         %55 = OpAccessChain %_ptr_StorageBuffer_uint %directDrawData %int_0 %53
         %56 = OpLoad %uint %55
         %57 = OpLoad %uint %wgIndex
         %58 = OpIAdd %uint %56 %57
               OpStore %rowIndex %58
         %60 = OpLoad %uint %rowIndex
         %61 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %62 = OpLoad %uint %61
         %63 = OpIMul %uint %60 %62
               OpStore %srcBasePrim %63
         %65 = OpLoad %uint %srcBasePrim
         %67 = OpLoad %uint %gl_LocalInvocationIndex
         %68 = OpIAdd %uint %65 %67
               OpStore %srcPrim %68
         %70 = OpLoad %uint %srcPrim
         %72 = OpIMul %uint %70 %uint_3
               OpStore %srcBaseVertex %72
         %74 = OpLoad %uint %gl_LocalInvocationIndex
               OpStore %dstPrim %74
         %76 = OpLoad %uint %dstPrim
         %77 = OpIMul %uint %76 %uint_3
               OpStore %dstBaseVertex %77
               OpSetMeshOutputsEXT %uint_96 %uint_32
               OpStore %i %uint_0
               OpBranch %81
         %81 = OpLabel
               OpLoopMerge %83 %84 None
               OpBranch %85
         %85 = OpLabel
         %86 = OpLoad %uint %i
         %88 = OpULessThan %bool %86 %uint_3
               OpBranchConditional %88 %82 %83
         %82 = OpLabel
         %90 = OpLoad %uint %dstBaseVertex
         %91 = OpLoad %uint %i
         %92 = OpIAdd %uint %90 %91
               OpStore %dstIdx %92
         %94 = OpLoad %uint %srcBaseVertex
         %95 = OpLoad %uint %i
         %96 = OpIAdd %uint %94 %95
               OpStore %srcIdx %96
        %104 = OpLoad %uint %dstIdx
        %110 = OpLoad %uint %srcIdx
        %112 = OpAccessChain %_ptr_StorageBuffer_v4float %vtxData %int_0 %110 %int_0
        %113 = OpLoad %v4float %112
        %115 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %104 %int_0
               OpStore %115 %113
        %116 = OpLoad %uint %dstIdx
        %120 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %116 %int_1
               OpStore %120 %float_1
        %121 = OpLoad %uint %dstIdx
        %122 = OpLoad %uint %srcIdx
        %124 = OpAccessChain %_ptr_StorageBuffer_float %vtxData %int_0 %122 %int_1 %uint_0
        %125 = OpLoad %float %124
        %126 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %121 %int_2 %int_0
               OpStore %126 %125
        %127 = OpLoad %uint %dstIdx
        %129 = OpLoad %uint %srcIdx
        %130 = OpAccessChain %_ptr_StorageBuffer_float %vtxData %int_0 %129 %int_1 %uint_1
        %131 = OpLoad %float %130
        %132 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %127 %int_3 %int_0
               OpStore %132 %131
        %136 = OpLoad %uint %dstIdx
        %138 = OpAccessChain %_ptr_Output_float %greenColor %136
               OpStore %138 %float_0
               OpBranch %84
         %84 = OpLabel
        %139 = OpLoad %uint %i
        %140 = OpIAdd %uint %139 %int_1
               OpStore %i %140
               OpBranch %81
         %83 = OpLabel
        %144 = OpLoad %uint %dstPrim
        %145 = OpLoad %uint %dstBaseVertex
        %146 = OpLoad %uint %dstBaseVertex
        %147 = OpIAdd %uint %146 %uint_1
        %148 = OpLoad %uint %dstBaseVertex
        %149 = OpIAdd %uint %148 %uint_2
        %150 = OpCompositeConstruct %v3uint %145 %147 %149
        %152 = OpAccessChain %_ptr_Output_v3uint %gl_PrimitiveTriangleIndicesEXT %144
               OpStore %152 %150
        %156 = OpLoad %uint %dstPrim
        %158 = OpAccessChain %_ptr_Output_float %redColor %156
               OpStore %158 %float_0_25
               OpReturn
               OpFunctionEnd
%getWorkGroupIndex_ = OpFunction %uint None %7
          %9 = OpLabel
         %15 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %16 = OpLoad %uint %15
         %18 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %19 = OpLoad %uint %18
         %20 = OpIMul %uint %16 %19
         %23 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %24 = OpLoad %uint %23
         %25 = OpIMul %uint %20 %24
         %26 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %27 = OpLoad %uint %26
         %28 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %29 = OpLoad %uint %28
         %30 = OpIMul %uint %27 %29
         %31 = OpIAdd %uint %25 %30
         %32 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %33 = OpLoad %uint %32
         %34 = OpIAdd %uint %31 %33
               OpReturnValue %34
               OpFunctionEnd
```
</details>

## Runtime Execution and Result Checking

- `DGCMeshDrawInstance::iterate` creates a 32 by 32 `VK_FORMAT_R8G8B8A8_UNORM` color image, a host-visible copy buffer, 1024 triangles with three vertices each, and storage buffers for vertex data, base rows, and task coverage.
- The host divides the 32 rows into eight direct sequences. It creates one `VkDrawMeshTasksIndirectCommandEXT` per sequence, putting the row count in a pseudorandomly chosen group-count dimension and leaving the other two dimensions at `1`.
- Count-form cases group the eight direct draws into four indirect buffers. Each buffer stores its records at a selected stride, and the DGC buffer carries `VkDrawIndirectCountIndirectCommandEXT` records with the device address, stride, and draw count.
- The DGC layout contains an optional execution-set token, a push-constant token for count-form cases or a sequence-index token for direct cases, and the matching mesh action token. The action token is last.
- The host builds pipeline, shader-object, or GPL state, binds descriptors, writes the static `width` and `height` push constants, and executes `vkCmdExecuteGeneratedCommandsEXT` inside rendering. Explicit-preprocess variants call `vkCmdPreprocessGeneratedCommandsEXT`; separate-state variants submit and synchronize that command buffer before execution.
- The task shader writes one row index and 32 column indices to `TaskData`. It launches `cb.colsPerRow[rowIndex]` mesh workgroups. The mesh shader copies each selected triangle and writes clip and cull distances. Negative distances leave the corresponding pixel clear.
- The host clears the image and reconstructs a reference pixel by pixel. It maps a row to its direct sequence, then to the indirect sequence when needed, applies task coverage and reversed order, checks clip and cull distances, and selects execution-set colors.
- After submission, the host copies the image, invalidates the allocation, and calls `tcu::floatThresholdCompare` with a `0.005` RGB threshold and zero alpha threshold. A mismatch calls `TCU_FAIL("Unexpected results in color buffer; check log for details")`.
- No-fragment cases discard rasterization and compare storage-buffer values computed from the sequence's push constant, workgroup index, and local invocation index. Many-sequence cases compare one `64` increment per sequence entry.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `token_draw` | Incorrect `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` decoding, push-constant or execution-set selection, mesh/task workgroup mapping, preprocessing, sequence ordering, rasterization, or image checking. |
| `token_draw_count` | Incorrect `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_COUNT_EXT` decoding, indirect count or stride handling, grouped draw mapping, mesh/task execution, preprocessing, rasterization, or image checking. |
| `misc` | Incorrect no-fragment pipeline path, large sequence handling, mesh/task storage-buffer writes, or related DGC execution. |
| `conditional_rendering` | Conditional rendering incorrectly controls the delegated generated mesh draw or preprocessing path. |

### Cause Analysis

#### Mesh action decoding and generated draw data

**Possible failure symptoms:** The rendered image covers the wrong rows or columns, or count-form cases use the wrong grouped draw. The log reports an unexpected color-buffer result. No-fragment cases may report an unexpected integer at a buffer index.

**Possible implementation causes:** The implementation may read the action at the wrong stream offset, decode a group count in the wrong dimension, apply the wrong sequence-index push constant, or misinterpret an indirect record's device address, count, or stride. Host-side command construction and reference mapping also need investigation when the observed output does not isolate generated execution.

#### Mesh and task shader execution

**Possible failure symptoms:** Direct cases leave expected pixels clear or draw triangles in the wrong row. Task cases cover too many or too few columns, use the wrong column order, or produce wrong colors. Buffer-only cases may show wrong per-workgroup values.

**Possible implementation causes:** The implementation may calculate `gl_WorkGroupID` flattening incorrectly, fail to pass `TaskData` from task to mesh workgroups, mishandle `EmitMeshTasksEXT` counts, or apply clip and cull distances incorrectly. The source check does not identify whether a symptom comes from shader compilation, device execution, or host setup, so those paths need separate investigation.

#### Pipeline selection, preprocessing, and sequence order

**Possible failure symptoms:** An execution-set case uses the wrong mesh or fragment color, a GPL mix case uses the wrong library construction, or a preprocess case fails during generated execution. An `_unordered` case differs from the reference even though the generated sequences are valid.

**Possible implementation causes:** The implementation may use the wrong execution-set index, fail to preserve per-stage shader-object selection, mishandle explicit-preprocess state, or execute a separately preprocessed buffer without the required synchronization. The output alone does not establish whether the cause lies in the driver, compiler, hardware, or host-side command setup.

#### Rendered-output and copyback checking

**Possible failure symptoms:** The device produces an image or storage-buffer value that differs from the reference. The regular path reports `Unexpected results in color buffer; check log for details`; the no-fragment path reports `Unexpected values found in output buffer; check log for details`.

**Possible implementation causes:** A mismatch can result from rasterization, shader output, image-to-buffer copy, allocation invalidation, reference construction, or comparison setup. The test's threshold and reference rules are source-backed, but a failure by itself does not assign the defect to a particular layer.

#### Delegated conditional rendering

**Possible failure symptoms:** A `conditional_rendering` case produces output when the condition should suppress generated work, or suppresses work when the condition should allow it. The exact conditional path determines whether the output is a color or buffer mismatch.

**Possible implementation causes:** The delegated implementation may mishandle condition state, the generated mesh action, preprocessing, or their required synchronization. Inspect [`vktDGCGraphicsMeshConditionalTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L1-L718) for that family's case-specific mapping.

## Case Pruning

### Requirement-based pruning

- Every regular mesh case requires `VK_EXT_mesh_shader`. The DGC support check also requires the selected mesh and task stages and the corresponding pipeline or shader-object support.
- Shader-object cases require `VK_EXT_shader_object`; an execution-set shader-object case requires a nonzero `maxIndirectShaderObjectCount`.
- Indirect count-form cases require `deviceGeneratedCommandsMultiDrawIndirectCount`.
- The no-fragment cases check the selected pipeline-construction requirements and the selected DGC stage bindings. The many-sequence cases require `VK_EXT_mesh_shader` and the selected DGC stages.
- Unsupported feature or limit combinations are reported as unsupported by `checkSupport`; they are not functional failures.

### Design-based pruning

- The registration skips `gpl_mix_base_fast` and `gpl_mix_base_opt` when `useExecutionSet` is false because those variants alternate pipeline construction per sequence and the implementation only prepares them through an execution set.
- The implementation keeps one representative shader walkthrough. It does not duplicate the walkthrough for every pipeline, preprocessing, ordering, task, and execution-set suffix because those variants reuse the same generated shader roles and change matrix-controlled state.
- Count-form cases use four grouped indirect buffers and variable strides by design. The padding records exercise stride interpretation without adding another behavioral family.
- `misc` separates no-fragment output and many-sequence stress from rendered-image checking because those cases test generated mesh execution through storage-buffer values.
- `conditional_rendering` stays in this hierarchy because the registration function attaches it, but its implementation remains delegated to the conditional-rendering source and page.

## Key Takeaways

- `token_draw` tests direct `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` records; `token_draw_count` tests the count form, grouped records, and variable strides.
- A task shader changes the mapping from one mesh workgroup per direct row operation to coverage-selected mesh workgroups that receive row and column data through `TaskData`.
- Execution sets, shader objects, GPL variants, preprocessing, and unordered sequences change generated state and execution arrangement. The regular cases still prove the same rendered pixel mapping.
- The host checks the complete path from command data and shader selection through rendering or storage-buffer writes, copyback, and comparison. A failure identifies a broken observable result, not a predetermined bug location.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test mechanism | [mesh test mechanism](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L61-L149) | Defines the rows, pixel triangles, direct and task-shader work, execution-set changes, and count-form model. |
| Parameters and support | [`TestParams::checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L218-L369) | Defines pipeline, preprocessing, task, execution-set, unordered, feature, and count-support dimensions. |
| Generated regular shaders | [`DGCMeshDrawCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L376-L561) | Generates fragment, mesh, and task GLSL programs. |
| Regular runtime and DGC layout | [`DGCMeshDrawInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L610-L1459) | Builds resources, command layouts, token data, preprocessing, rendering, and execution. |
| Regular reference and comparison | [`DGCMeshDrawInstance::iterate` result check](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1463-L1547) | Builds the expected image, applies coverage and clip/cull rules, and compares copyback. |
| No-fragment path | [`NoFragCase` and `NoFragInstance`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1549-L2088) | Tests task and mesh storage-buffer writes with pipeline, execution-set, and preprocess variants. |
| Many-sequence path | [`manySequencesRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2090-L2316) | Tests `64`, `1024`, `8192`, and `131072` sequences and checks one counter per sequence. |
| Registration | [`createDGCGraphicsMeshTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2320-L2424) | Registers the four direct children and exact variant-construction loops. |
| Mustpass evidence | [mesh paths in `dgc.txt`](../../../mustpass/main/vk-default/dgc.txt#L1806-L2113) | Records all 308 registered paths. |
| Mesh shader semantics | [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | Defines task and mesh workgroup behavior and emitted primitives. |
| DGC layout semantics | [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout) | Defines mesh action tokens, explicit preprocessing, synchronization, and sequence ordering. |
