## Overview

**Core question:** Do the EXT direct, indirect, indirect-count, and device-address mesh draw commands launch exactly the requested work and preserve the same result through primary and secondary command buffers?

- [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp) implements the `mesh_shader.ext.api` test family.
- The matrix covers `vkCmdDrawMeshTasksEXT`, `vkCmdDrawMeshTasksIndirectEXT`, `vkCmdDrawMeshTasksIndirectCountEXT`, and sampled `VK_KHR_device_address_commands` forms.
- Every ordinary case runs with and without a task shader, and inline or through a render-pass-continuing secondary command buffer.
- The test turns each launched mesh workgroup into one colored framebuffer row. A host-side reference image exposes missing, extra, or misaddressed draws.

## Background Knowledge

- **Mesh and task workgroups.** A mesh draw assembles a workgroup grid from X, Y, and Z group counts. Without a task shader, those workgroups run the mesh shader directly. With a task shader, each task workgroup calls `EmitMeshTasksEXT` and can pass a payload to the mesh workgroup it emits. The specification defines this relationship in [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L12-L19).
- **Indirect command records.** `vkCmdDrawMeshTasksIndirectEXT` reads `VkDrawMeshTasksIndirectCommandEXT` records from a buffer at a byte offset and stride. `drawCount` selects the number of records. The count form reads a 32-bit count from another buffer and executes the smaller of that value and `maxDrawCount` [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2554-L2579).
- **Device-address commands.** The `*2EXT` commands replace buffer handles and offsets with address ranges for indirect draws. They preserve the corresponding indirect and indirect-count semantics, but require `VK_KHR_device_address_commands` and buffers that can supply device addresses [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2519-L2547).

## Registration Hierarchy

```text
mesh_shader.ext.api
├── draw
├── draw_indirect
└── draw_indirect_count
```

The canonical default mustpass contains 540 executable leaves for this family: 20 `draw`, 120 `draw_indirect`, and 400 `draw_indirect_count` cases [mesh-shader.txt](../../../mustpass/main/vk-default/mesh-shader.txt#L1-L540).

## Parameter Dimensions and Observed Values

The source builds the matrix in [createMeshShaderApiTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783-L951). Some registered placeholders, such as `no_indirect_args`, appear only where a dimension does not apply.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw command family | `draw`, `draw_indirect`, `draw_indirect_count` | Selects whether workgroup counts come from command arguments, an indirect buffer, or an indirect buffer plus a device-read count. | [drawCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L787-L791) |
| Draw or task count | `draw_count_0`, `draw_count_1`, `draw_count_2`, `draw_count_32`, `draw_count_64` | Direct cases use the value as the workgroup count. Indirect cases use it as the number of records or effective count limit. | [drawCountCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L793-L795) |
| Indirect record offset and stride | `offset_0_stride_0`, `offset_0_stride_normal`, `offset_0_stride_large`, `offset_alt_stride_0`, `offset_alt_stride_normal`, `offset_alt_stride_large` | Varies the first record address and spacing. `alt` is 20 bytes, `normal` is the command-structure size, and `large` is twice that size plus 4 bytes. | [indirectArgsCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L796-L816) |
| Count limiter | `count_limit_buffer`, `count_limit_max_count` | Chooses whether the count-buffer value or the command's `maxDrawCount` supplies the smaller effective count. | [countLimitCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L818-L826) |
| Count-buffer offset | `count_offset_0`, `count_offset_alt` | Places the 32-bit count at byte offset 0 or 20. | [countOffsetCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L828-L836) |
| Task stage | `no_task_shader`, `with_task_shader` | Launches mesh workgroups directly or through a task shader and payload. | [taskCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L838-L845) |
| Command-buffer level | no suffix, `_secondary_cmd` | Records render-pass commands inline in the primary buffer or in a secondary buffer executed by the primary. | [cmdBufferCases](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L847-L854) |
| Command argument transport | ordinary leaf, `_device_address` | Uses buffer-handle commands or sampled `VK_KHR_device_address_commands` address-range forms. | [address-case selection](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L924-L932) |

The canonical `vk-default` list reflects the source filters and address sampling:

| Mustpass branch | Default leaves | Coverage notes |
|-----------------|---------------:|----------------|
| `draw` | 20 | Five counts times task/no-task times primary/secondary. No device-address form exists for direct draws. |
| `draw_indirect` | 120 | Zero and one allow all six offset/stride layouts; larger counts omit zero stride. Twenty-four selected leaves add `_device_address`. |
| `draw_indirect_count` | 400 | Five counts, four nonzero-stride layouts, two limiters, two count offsets, task/no-task, primary/secondary, plus 80 sampled address leaves. |

## Behavior Parameters

The primary behavioral axis is the draw command family and the source from which the device obtains the workgroup counts. Task, command-buffer, layout, and address options vary that behavior without changing the expected image.

### draw - Direct group counts

`draw` calls `vkCmdDrawMeshTasksEXT` with the selected group-count component set to the registered count and the other two components left at one. The test selects X, Y, or Z from its pseudorandom seed, so count zero launches no workgroups and count one launches one. Each resulting mesh workgroup fills one framebuffer row [direct command](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L654-L658).

### draw_indirect - Group counts from command records

`draw_indirect` builds one `VkDrawMeshTasksIndirectCommandEXT` per row block. The records partition all 64 rows when the draw count is nonzero. Offset and stride variants verify that the implementation reads the intended records rather than adjacent padding. Ordinary cases call `vkCmdDrawMeshTasksIndirectEXT`; sampled address cases call `vkCmdDrawMeshTasksIndirect2EXT` with a `VkDrawIndirect2InfoKHR` address range [indirect commands](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L659-L681).

### draw_indirect_count - Device-read count and maximum

`draw_indirect_count` adds a 32-bit count source. `count_limit_buffer` stores the requested count and supplies a larger `maxDrawCount`; `count_limit_max_count` stores one extra record count and supplies the requested count as the maximum. Both must execute the same effective number of records. The ordinary path uses `vkCmdDrawMeshTasksIndirectCountEXT`; selected address cases use `vkCmdDrawMeshTasksIndirectCount2EXT` [count commands](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L683-L714).

## Shader Analysis

The draw command behavior is visible through one generated mesh shader. This walkthrough chooses a direct, no-task case so the workgroup-to-row mapping is explicit. Task and indirect variants keep the mesh output logic and change how the row coordinate and draw block reach it.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.api.draw.draw_count_1.no_indirect_args.no_count_limit.no_count_offset.no_task_shader
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw` + `draw_count_1` | One direct EXT mesh workgroup fills one framebuffer row. |
| `no_task_shader` | The mesh shader reads `gl_DrawID` and the selected mesh workgroup coordinate directly. |
| primary command buffer | The draw is recorded inline in the render pass. The shader output is identical in the secondary variant. |

#### Purpose

The mesh shader converts each launched workgroup into a uniquely colored row. The output makes the exact number and identity of launched workgroups visible to the host image comparison.

#### Structural Design

| Shader step | Observable role |
|-------------|-----------------|
| Select X, Y, or Z workgroup coordinate | Exercises all three mesh draw group-count dimensions while keeping one linear row index. |
| Add prior indirect block sizes | Maps `gl_DrawID` and the record's local workgroup coordinate into one global framebuffer row. |
| Assign one local invocation per column | Produces 32 triangles, one around each pixel center in the row. |
| Write normalized row and column color | Gives every expected pixel a deterministic value that identifies its row and column. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_mesh_shader : enable

// 32 local invocations in total.
/// The direct case uses one MeshEXT workgroup. The host selects which workgroup coordinate supplies the row.
layout (local_size_x=4, local_size_y=2, local_size_z=4) in;
layout (triangles) out;
layout (max_vertices=96, max_primitives=32) out;

layout (push_constant, std430) uniform MeshPushConstantBlock {
    /// The host supplies the 32 by 64 framebuffer extent and selected coordinate dimension.
    uint width;
    uint height;
    uint dimCoord;
} pc;

layout (location=0) perprimitiveEXT out vec4 primitiveColor[];

/// Binding 0 contains one storage-buffer block size per draw. Direct cases have a single block.
layout (set=0, binding=0, std430) readonly buffer BlockSizes {
    uint blockSize[];
} bsz;

uint startOfBlock (uint blockNumber)
{
    uint start = 0;
    for (uint i = 0; i < blockNumber; i++)
        start += bsz.blockSize[i];
    return start;
}

void main ()
{
    const uint workGroupID = ((pc.dimCoord == 2) ? gl_WorkGroupID.z : ((pc.dimCoord == 1) ? gl_WorkGroupID.y : gl_WorkGroupID.x));
    const uint blockNumber = uint(gl_DrawID);
    const uint blockRow = workGroupID;

    // Each workgroup will fill one row, and each invocation will generate a
    // triangle around the pixel center in each column.
    const uint row = startOfBlock(blockNumber) + blockRow;
    const uint col = gl_LocalInvocationIndex;

    const float fHeight = float(pc.height);
    const float fWidth = float(pc.width);

    // Pixel coordinates, normalized.
    const float rowNorm = (float(row) + 0.5) / fHeight;
    const float colNorm = (float(col) + 0.5) / fWidth;

    // Framebuffer coordinates.
    const float coordX = (colNorm * 2.0) - 1.0;
    const float coordY = (rowNorm * 2.0) - 1.0;

    const float pixelWidth = 2.0 / fWidth;
    const float pixelHeight = 2.0 / fHeight;

    const float offsetX = pixelWidth / 2.0;
    const float offsetY = pixelHeight / 2.0;

    const uint baseIndex = col*3;
    const uvec3 indices = uvec3(baseIndex, baseIndex + 1, baseIndex + 2);

    SetMeshOutputsEXT(96u, 32u);
    primitiveColor[col] = vec4(rowNorm, colNorm, 0.0, 1.0);
    gl_PrimitiveTriangleIndicesEXT[col] = uvec3(indices.x, indices.y, indices.z);

    gl_MeshVerticesEXT[indices.x].gl_Position = vec4(coordX - offsetX, coordY + offsetY, 0.0, 1.0);
    gl_MeshVerticesEXT[indices.y].gl_Position = vec4(coordX + offsetX, coordY + offsetY, 0.0, 1.0);
    gl_MeshVerticesEXT[indices.z].gl_Position = vec4(coordX, coordY - offsetY, 0.0, 1.0);
}
```

#### Additional Info

- `getMinMeshEXTBuildOptions` targets SPIR-V 1.4 for all generated stages [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L141-L144).
- The fixed fragment shader copies `primitiveColor` to the color attachment. It does not alter the workgroup-to-row mapping [fragment generation](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L326-L340).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Task stage | `with_task_shader` adds a TaskEXT shader and `taskPayloadSharedEXT`. The task shader writes `gl_DrawID` and its selected workgroup coordinate, emits one mesh workgroup, and the mesh shader reads those payload fields. | [task and payload generation](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L219-L248), [mesh selection](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L270-L288) |
| Draw command family | Indirect families do not change the mesh shader body. They change the number and contents of command records, which changes `gl_DrawID` and the workgroup counts seen by this shader. | [indirect command generation](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L582-L612) |
| Draw count | Changes the number of workgroups or records. The host generates block sizes whose sum is 64 for every nonzero indirect case. | [block-size generation](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L467-L484) |
| Coordinate dimension | The seed selects `dimCoord` 0, 1, or 2. Both the indirect record and shader use the same component. | [dimension selection](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L519-L526), [indirect record helper](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L399-L419) |

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
; Bound: 210
; Schema: 0
               OpCapability DrawParameters
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %bsz %pc %gl_WorkGroupID %gl_DrawID %gl_LocalInvocationIndex %primitiveColor %gl_PrimitiveTriangleIndicesEXT %gl_MeshVerticesEXT
               OpExecutionMode %main LocalSize 4 2 4
               OpExecutionMode %main OutputVertices 96
               OpExecutionMode %main OutputPrimitivesEXT 32
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %startOfBlock_u1_ "startOfBlock(u1;"
               OpName %blockNumber "blockNumber"
               OpName %start "start"
               OpName %i "i"
               OpName %BlockSizes "BlockSizes"
               OpMemberName %BlockSizes 0 "blockSize"
               OpName %bsz "bsz"
               OpName %workGroupID "workGroupID"
               OpName %MeshPushConstantBlock "MeshPushConstantBlock"
               OpMemberName %MeshPushConstantBlock 0 "width"
               OpMemberName %MeshPushConstantBlock 1 "height"
               OpMemberName %MeshPushConstantBlock 2 "dimCoord"
               OpName %pc "pc"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %blockNumber_0 "blockNumber"
               OpName %gl_DrawID "gl_DrawID"
               OpName %blockRow "blockRow"
               OpName %row "row"
               OpName %param "param"
               OpName %col "col"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %fHeight "fHeight"
               OpName %fWidth "fWidth"
               OpName %rowNorm "rowNorm"
               OpName %colNorm "colNorm"
               OpName %coordX "coordX"
               OpName %coordY "coordY"
               OpName %pixelWidth "pixelWidth"
               OpName %pixelHeight "pixelHeight"
               OpName %offsetX "offsetX"
               OpName %offsetY "offsetY"
               OpName %baseIndex "baseIndex"
               OpName %indices "indices"
               OpName %primitiveColor "primitiveColor"
               OpName %gl_PrimitiveTriangleIndicesEXT "gl_PrimitiveTriangleIndicesEXT"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %BlockSizes Block
               OpMemberDecorate %BlockSizes 0 NonWritable
               OpMemberDecorate %BlockSizes 0 Offset 0
               OpDecorate %bsz NonWritable
               OpDecorate %bsz Binding 0
               OpDecorate %bsz DescriptorSet 0
               OpDecorate %MeshPushConstantBlock Block
               OpMemberDecorate %MeshPushConstantBlock 0 Offset 0
               OpMemberDecorate %MeshPushConstantBlock 1 Offset 4
               OpMemberDecorate %MeshPushConstantBlock 2 Offset 8
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_DrawID BuiltIn DrawIndex
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %primitiveColor Location 0
               OpDecorate %primitiveColor PerPrimitiveEXT
               OpDecorate %gl_PrimitiveTriangleIndicesEXT BuiltIn PrimitiveTriangleIndicesEXT
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
          %8 = OpTypeFunction %uint %_ptr_Function_uint
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
%_runtimearr_uint = OpTypeRuntimeArray %uint
 %BlockSizes = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_BlockSizes = OpTypePointer StorageBuffer %BlockSizes
        %bsz = OpVariable %_ptr_StorageBuffer_BlockSizes StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_1 = OpConstant %int 1
%MeshPushConstantBlock = OpTypeStruct %uint %uint %uint
%_ptr_PushConstant_MeshPushConstantBlock = OpTypePointer PushConstant %MeshPushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_MeshPushConstantBlock PushConstant
      %int_2 = OpConstant %int 2
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_2 = OpConstant %uint 2
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%_ptr_Input_int = OpTypePointer Input %int
  %gl_DrawID = OpVariable %_ptr_Input_int Input
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
  %float_0_5 = OpConstant %float 0.5
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
     %uint_3 = OpConstant %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
    %uint_96 = OpConstant %uint 96
    %uint_32 = OpConstant %uint 32
    %v4float = OpTypeVector %float 4
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Output__arr_v4float_uint_32 = OpTypePointer Output %_arr_v4float_uint_32
%primitiveColor = OpVariable %_ptr_Output__arr_v4float_uint_32 Output
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_arr_v3uint_uint_32 = OpTypeArray %v3uint %uint_32
%_ptr_Output__arr_v3uint_uint_32 = OpTypePointer Output %_arr_v3uint_uint_32
%gl_PrimitiveTriangleIndicesEXT = OpVariable %_ptr_Output__arr_v3uint_uint_32 Output
%_ptr_Output_v3uint = OpTypePointer Output %v3uint
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_96 = OpTypeArray %gl_MeshPerVertexEXT %uint_96
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_96
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 Output
     %uint_4 = OpConstant %uint 4
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_4 %uint_2 %uint_4
       %main = OpFunction %void None %3
          %5 = OpLabel
%workGroupID = OpVariable %_ptr_Function_uint Function
         %52 = OpVariable %_ptr_Function_uint Function
         %66 = OpVariable %_ptr_Function_uint Function
%blockNumber_0 = OpVariable %_ptr_Function_uint Function
   %blockRow = OpVariable %_ptr_Function_uint Function
        %row = OpVariable %_ptr_Function_uint Function
      %param = OpVariable %_ptr_Function_uint Function
        %col = OpVariable %_ptr_Function_uint Function
    %fHeight = OpVariable %_ptr_Function_float Function
     %fWidth = OpVariable %_ptr_Function_float Function
    %rowNorm = OpVariable %_ptr_Function_float Function
    %colNorm = OpVariable %_ptr_Function_float Function
     %coordX = OpVariable %_ptr_Function_float Function
     %coordY = OpVariable %_ptr_Function_float Function
 %pixelWidth = OpVariable %_ptr_Function_float Function
%pixelHeight = OpVariable %_ptr_Function_float Function
    %offsetX = OpVariable %_ptr_Function_float Function
    %offsetY = OpVariable %_ptr_Function_float Function
  %baseIndex = OpVariable %_ptr_Function_uint Function
    %indices = OpVariable %_ptr_Function_v3uint Function
         %48 = OpAccessChain %_ptr_PushConstant_uint %pc %int_2
         %49 = OpLoad %uint %48
         %51 = OpIEqual %bool %49 %uint_2
               OpSelectionMerge %54 None
               OpBranchConditional %51 %53 %61
         %53 = OpLabel
         %59 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %60 = OpLoad %uint %59
               OpStore %52 %60
               OpBranch %54
         %61 = OpLabel
         %62 = OpAccessChain %_ptr_PushConstant_uint %pc %int_2
         %63 = OpLoad %uint %62
         %65 = OpIEqual %bool %63 %uint_1
               OpSelectionMerge %68 None
               OpBranchConditional %65 %67 %71
         %67 = OpLabel
         %69 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %70 = OpLoad %uint %69
               OpStore %66 %70
               OpBranch %68
         %71 = OpLabel
         %72 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %73 = OpLoad %uint %72
               OpStore %66 %73
               OpBranch %68
         %68 = OpLabel
         %74 = OpLoad %uint %66
               OpStore %52 %74
               OpBranch %54
         %54 = OpLabel
         %75 = OpLoad %uint %52
               OpStore %workGroupID %75
         %79 = OpLoad %int %gl_DrawID
         %80 = OpBitcast %uint %79
               OpStore %blockNumber_0 %80
         %82 = OpLoad %uint %workGroupID
               OpStore %blockRow %82
         %85 = OpLoad %uint %blockNumber_0
               OpStore %param %85
         %86 = OpFunctionCall %uint %startOfBlock_u1_ %param
         %87 = OpLoad %uint %blockRow
         %88 = OpIAdd %uint %86 %87
               OpStore %row %88
         %91 = OpLoad %uint %gl_LocalInvocationIndex
               OpStore %col %91
         %95 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %96 = OpLoad %uint %95
         %97 = OpConvertUToF %float %96
               OpStore %fHeight %97
         %99 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
        %100 = OpLoad %uint %99
        %101 = OpConvertUToF %float %100
               OpStore %fWidth %101
        %103 = OpLoad %uint %row
        %104 = OpConvertUToF %float %103
        %106 = OpFAdd %float %104 %float_0_5
        %107 = OpLoad %float %fHeight
        %108 = OpFDiv %float %106 %107
               OpStore %rowNorm %108
        %110 = OpLoad %uint %col
        %111 = OpConvertUToF %float %110
        %112 = OpFAdd %float %111 %float_0_5
        %113 = OpLoad %float %fWidth
        %114 = OpFDiv %float %112 %113
               OpStore %colNorm %114
        %116 = OpLoad %float %colNorm
        %118 = OpFMul %float %116 %float_2
        %120 = OpFSub %float %118 %float_1
               OpStore %coordX %120
        %122 = OpLoad %float %rowNorm
        %123 = OpFMul %float %122 %float_2
        %124 = OpFSub %float %123 %float_1
               OpStore %coordY %124
        %126 = OpLoad %float %fWidth
        %127 = OpFDiv %float %float_2 %126
               OpStore %pixelWidth %127
        %129 = OpLoad %float %fHeight
        %130 = OpFDiv %float %float_2 %129
               OpStore %pixelHeight %130
        %132 = OpLoad %float %pixelWidth
        %133 = OpFDiv %float %132 %float_2
               OpStore %offsetX %133
        %135 = OpLoad %float %pixelHeight
        %136 = OpFDiv %float %135 %float_2
               OpStore %offsetY %136
        %138 = OpLoad %uint %col
        %140 = OpIMul %uint %138 %uint_3
               OpStore %baseIndex %140
        %143 = OpLoad %uint %baseIndex
        %144 = OpLoad %uint %baseIndex
        %145 = OpIAdd %uint %144 %uint_1
        %146 = OpLoad %uint %baseIndex
        %147 = OpIAdd %uint %146 %uint_2
        %148 = OpCompositeConstruct %v3uint %143 %145 %147
               OpStore %indices %148
               OpSetMeshOutputsEXT %uint_96 %uint_32
        %155 = OpLoad %uint %col
        %156 = OpLoad %float %rowNorm
        %157 = OpLoad %float %colNorm
        %159 = OpCompositeConstruct %v4float %156 %157 %float_0 %float_1
        %161 = OpAccessChain %_ptr_Output_v4float %primitiveColor %155
               OpStore %161 %159
        %165 = OpLoad %uint %col
        %166 = OpAccessChain %_ptr_Function_uint %indices %uint_0
        %167 = OpLoad %uint %166
        %168 = OpAccessChain %_ptr_Function_uint %indices %uint_1
        %169 = OpLoad %uint %168
        %170 = OpAccessChain %_ptr_Function_uint %indices %uint_2
        %171 = OpLoad %uint %170
        %172 = OpCompositeConstruct %v3uint %167 %169 %171
        %174 = OpAccessChain %_ptr_Output_v3uint %gl_PrimitiveTriangleIndicesEXT %165
               OpStore %174 %172
        %180 = OpAccessChain %_ptr_Function_uint %indices %uint_0
        %181 = OpLoad %uint %180
        %182 = OpLoad %float %coordX
        %183 = OpLoad %float %offsetX
        %184 = OpFSub %float %182 %183
        %185 = OpLoad %float %coordY
        %186 = OpLoad %float %offsetY
        %187 = OpFAdd %float %185 %186
        %188 = OpCompositeConstruct %v4float %184 %187 %float_0 %float_1
        %189 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %181 %int_0
               OpStore %189 %188
        %190 = OpAccessChain %_ptr_Function_uint %indices %uint_1
        %191 = OpLoad %uint %190
        %192 = OpLoad %float %coordX
        %193 = OpLoad %float %offsetX
        %194 = OpFAdd %float %192 %193
        %195 = OpLoad %float %coordY
        %196 = OpLoad %float %offsetY
        %197 = OpFAdd %float %195 %196
        %198 = OpCompositeConstruct %v4float %194 %197 %float_0 %float_1
        %199 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %191 %int_0
               OpStore %199 %198
        %200 = OpAccessChain %_ptr_Function_uint %indices %uint_2
        %201 = OpLoad %uint %200
        %202 = OpLoad %float %coordX
        %203 = OpLoad %float %coordY
        %204 = OpLoad %float %offsetY
        %205 = OpFSub %float %203 %204
        %206 = OpCompositeConstruct %v4float %202 %205 %float_0 %float_1
        %207 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %201 %int_0
               OpStore %207 %206
               OpReturn
               OpFunctionEnd
%startOfBlock_u1_ = OpFunction %uint None %8
%blockNumber = OpFunctionParameter %_ptr_Function_uint
         %11 = OpLabel
      %start = OpVariable %_ptr_Function_uint Function
          %i = OpVariable %_ptr_Function_uint Function
               OpStore %start %uint_0
               OpStore %i %uint_0
               OpBranch %15
         %15 = OpLabel
               OpLoopMerge %17 %18 None
               OpBranch %19
         %19 = OpLabel
         %20 = OpLoad %uint %i
         %21 = OpLoad %uint %blockNumber
         %23 = OpULessThan %bool %20 %21
               OpBranchConditional %23 %16 %17
         %16 = OpLabel
         %30 = OpLoad %uint %i
         %32 = OpAccessChain %_ptr_StorageBuffer_uint %bsz %int_0 %30
         %33 = OpLoad %uint %32
         %34 = OpLoad %uint %start
         %35 = OpIAdd %uint %34 %33
               OpStore %start %35
               OpBranch %18
         %18 = OpLabel
         %36 = OpLoad %uint %i
         %38 = OpIAdd %uint %36 %int_1
               OpStore %i %38
               OpBranch %15
         %17 = OpLabel
         %39 = OpLoad %uint %start
               OpReturnValue %39
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a 32 by 64 `VK_FORMAT_R8G8B8A8_UNORM` color image, clears it to opaque black, and uses it as the render-pass color attachment [image setup](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L430-L465).
- A seeded generator partitions 64 rows into `max(1, drawCount)` positive block sizes. Descriptor set 0 binding 0 exposes those sizes to the mesh shader. The same seed selects whether X, Y, or Z carries the varying group count [resource setup](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L467-L526).
- Indirect cases create host-visible indirect buffers with the selected offset and stride. Address cases add `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`, allocate addressable memory, and query the buffer address. Count cases create a second indirect buffer with the 32-bit count at offset 0 or 20 [indirect resources](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L564-L612).
- Secondary cases begin the render pass with `VK_SUBPASS_CONTENTS_SECONDARY_COMMAND_BUFFERS`, record descriptor, push-constant, pipeline, and draw commands in a secondary buffer with inheritance information, then call `vkCmdExecuteCommands` from the primary [secondary path](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L550-L562) and [recording](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L615-L723).
- Address cases vary valid `addressFlags` and `countAddressFlags`, including fully-bound and unknown-usage forms. This extends address interpretation coverage without changing the expected image [address command setup](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L662-L708).
- After rendering, the primary command buffer copies the image to a host-visible output buffer and waits for completion. The host invalidates the allocation, builds a full reference image, and compares every pixel with a `0.005` threshold [copy and submit](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L727-L758).
- Direct count zero and direct rows at or above the selected count remain clear. Any nonzero indirect/count case must cover all 64 rows. Other pixels must equal `(row + 0.5) / 64`, `(column + 0.5) / 32`, `0`, `1` [reference construction](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L760-L775).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Direct EXT mesh-task group-count handling, task/no-task launch behavior, or mesh output and image validation. |
| `draw_indirect` | Indirect command-buffer offset, stride, multi-draw, or device-address interpretation. |
| `draw_indirect_count` | Count-buffer or count-address interpretation, `maxDrawCount` limiting, indirect layout, or device-address count handling. |

### Cause Analysis

#### Direct launch or mesh output handling

**Possible failure symptoms:** expected colored rows remain clear, rows beyond the direct count become colored, or generated colors differ from their row and column reference values.

**Possible implementation causes:** the implementation may use the wrong X/Y/Z group count, mishandle zero or multi-workgroup direct draws, lose the task payload, or lower `SetMeshOutputsEXT` and mesh output indices incorrectly. The EXT mesh specification defines direct workgroup assembly, task emission, and mesh output counts [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L12-L19) and [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L149-L166).

#### Indirect record addressing

**Possible failure symptoms:** indirect cases color too few or too many rows, reorder row blocks, or fail only for nonzero offsets, padded strides, multiple records, secondary command buffers, or `_device_address` leaves.

**Possible implementation causes:** the command processor may compute a record address from offset and stride incorrectly, ignore a record, read padding as a record, mishandle `drawCount`, or interpret the supplied address range or valid address flags incorrectly. Vulkan requires successive records to begin at `offset + i * stride`, and requires a nonzero suitably aligned stride when multiple records are consumed [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2571-L2599).

#### Count limiting and count addressing

**Possible failure symptoms:** `count_limit_buffer` and `count_limit_max_count` produce different images, count-offset variants fail, or count-address cases execute the stored large count instead of the requested maximum.

**Possible implementation causes:** the implementation may read the count from the wrong byte offset or address, fail to use `min(count, maxDrawCount)`, or combine the count with indirect record stride incorrectly. The specification defines the minimum rule and 4-byte count alignment [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2671-L2714) and [draw_indirect_count_common.adoc](../../../../vulkan-docs/src/chapters/commonvalidity/draw_indirect_count_common.adoc#L7-L25).

#### Command-buffer execution or readback

**Possible failure symptoms:** only `_secondary_cmd` leaves fail, or output is uniformly clear, stale, or corrupted across all command families.

**Possible implementation causes:** render-pass inheritance or secondary execution may not preserve the bound descriptor, pipeline, push constants, or draw commands. A shared failure can also arise from color attachment writes, image-to-buffer synchronization, memory invalidation, or comparison setup rather than the draw command itself. Source-level investigation is needed to separate these paths from the image log.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_mesh_shader` and the `meshShader` feature. `with_task_shader` also requires `taskShader` [checkTaskMeshShaderSupportEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139).
- `draw_indirect` with more than one record requires the core `multiDrawIndirect` feature, matching the draw-count validity rule [checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L343-L351) and [draw_indirect_drawcount.adoc](../../../../vulkan-docs/src/chapters/commonvalidity/draw_indirect_drawcount.adoc#L7-L12).
- `draw_indirect_count` requires draw-indirect-count functionality (`VK_KHR_draw_indirect_count` when not provided by its promoted core feature path) [checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L353-L355) and [functionality check](../../../modules/vulkan/vktTestCase.cpp#L1104-L1147).
- `_device_address` leaves require `VK_KHR_device_address_commands`; their indirect and count buffers request shader-device-address usage and addressable memory [checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L357-L358).

### Design-based pruning

- Direct draws use only `no_indirect_args`, `no_count_limit`, and `no_count_offset`. Indirect draws use real indirect layouts but no count limiter or count offset. Indirect-count draws require all three.
- Zero stride is retained for `draw_indirect` only when `drawCount` is 0 or 1. The source removes it when more than one record would be consumed and removes it from every indirect-count case [matrix filters](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L872-L883).
- Device-address variants are sampled to control test volume. `draw_indirect` samples only no-task cases; `draw_indirect_count` samples only task cases. Offset/stride parity selects primary versus secondary variants [address-case filter](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L924-L932).
- The Android 2026-03-01 mustpass isolates the 104 device-address leaves, while the canonical `vk-default` mustpass includes all 540 leaves. This packaging split does not change source registration [Android mesh-shader.txt](../../../../../android/cts/main/vk-main-2026-03-01/mesh-shader.txt#L1-L104).

## Key Takeaways

- One image pattern validates five API entry paths: direct, buffer-indirect, buffer-indirect-count, address-indirect, and address-indirect-count.
- Offset, stride, count offset, effective-count source, task use, and command-buffer level all preserve the same workgroup-to-row result.
- The 540 default leaves include 104 sampled device-address cases; the source deliberately avoids multiplying that variant across the complete ordinary matrix.
- Image differences localize failures by branch and variant. See `## Failure Meaning` before attributing a mismatch to command processing, shader execution, or readback.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameters and shader generation | [TestParams and `initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L98-L341) | Defines the draw dimensions and generated task, mesh, and fragment stages. |
| Support checks | [`MeshApiCase::checkSupport`](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L343-L359) | Applies extension and feature gates. |
| Indirect buffer construction | [`makeStridedBuffer` and `getIndirectCommand`](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L361-L420) | Defines offset, stride, padding, memory, and X/Y/Z record construction. |
| Runtime and command recording | [`MeshApiInstance::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L422-L744) | Creates resources and records all command variants. |
| Result checking | [reference image comparison](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L746-L778) | Defines expected pixels, threshold, and failure status. |
| Registration | [`createMeshShaderApiTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783-L951) | Generates the hierarchy, matrix, filters, names, and address samples. |
| Default mustpass coverage | [`vk-default/mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L1-L540) | Lists the exact 540 default executable leaves for this family. |
| Vulkan mesh draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L2484-L2717) | Defines direct, indirect, count, and address-range behavior. |
