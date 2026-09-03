## Overview

**Core question:** Does each registered EXT miscellaneous case produce the required task/mesh behavior and the expected framebuffer result?

- [`vktMeshShaderMiscTestsEXT.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp) registers and implements the `mesh_shader.ext.misc` test family.
- The family covers task payloads, primitive emission and zero output, barriers, clip and interface behavior, push constants, output limits, large dispatches, descriptor rebinding, mixed pipelines, subgroup first-invocation behavior, `LocalSizeId`, control-flow emission, and workgroup ordering.
- The registration function creates 83 direct test-case leaves. It uses fixed parameter objects and small loops over dimensions rather than exposing a deeper CTS group hierarchy.
- Most cases generate EXT GLSL, compile it through the CTS shader collection, render into an RGBA8 image, copy that image to a host-visible buffer, and compare it with a generated reference. Two cases use source-controlled SPIR-V assembly.

## Background Knowledge

- **Task and mesh execution.** A task shader launches mesh workgroups with `EmitMeshTasksEXT`. A mesh shader calls `SetMeshOutputsEXT` before writing its valid vertex and primitive outputs. An optional `taskPayloadSharedEXT` object carries data from a task workgroup to its launched mesh workgroups. See [the mesh-shader specification chapter](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc).
- **Mesh outputs and interfaces.** Mesh shaders write positions, primitive indices, and per-vertex or per-primitive outputs. The next stage matches user-defined values by location and interpolation rules. See [shader interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292).
- **Workgroup synchronization.** `barrier()` synchronizes invocations in a workgroup. `memoryBarrierShared()` and `groupMemoryBarrier()` order memory accesses used by the barrier cases. See [shader workgroups and barriers](../../../../vulkan-docs/src/chapters/shaders.adoc#L2387-L2481).
- **EXT support and limits.** The extension exposes separate `taskShader` and `meshShader` feature bits plus mesh/task output and workgroup limits. The test uses these bits and properties to decide whether a case can run. See [EXT feature descriptions](../../../../vulkan-docs/src/chapters/features.adoc#L1845-L1911) and [mesh-shader limits](../../../../vulkan-docs/src/chapters/limits.adoc#L6213-L6242).

## Registration Hierarchy

```text
mesh_shader.ext.misc
├── barrier_in_mesh
├── barrier_in_task
├── clip_geom
├── clip_geom_and_task_shader
├── clip_geom_and_task_shader_multiview
├── clip_geom_and_task_shader_provoking_last
├── clip_geom_and_task_shader_provoking_last_multiview
├── clip_geom_multiview
├── clip_geom_provoking_last
├── clip_geom_provoking_last_multiview
├── clip_plane
├── clip_plane_and_task_shader
├── clip_plane_and_task_shader_multiview
├── clip_plane_and_task_shader_provoking_last
├── clip_plane_and_task_shader_provoking_last_multiview
├── clip_plane_multiview
├── clip_plane_provoking_last
├── clip_plane_provoking_last_multiview
├── complex_task_data
├── custom_attributes
├── custom_attributes_and_task_shader
├── emit_in_control_flow
├── emit_in_control_flow_bad_emit_last
├── first_invocation_mesh
├── first_invocation_task
├── group_memory_barrier_in_mesh_array
├── group_memory_barrier_in_mesh_float
├── group_memory_barrier_in_mesh_struct
├── group_memory_barrier_in_mesh_uint64
├── group_memory_barrier_in_mesh_vector
├── group_memory_barrier_in_task_array
├── group_memory_barrier_in_task_float
├── group_memory_barrier_in_task_struct
├── group_memory_barrier_in_task_uint64
├── group_memory_barrier_in_task_vector
├── local_size_id_mesh
├── local_size_id_task
├── many_mesh_work_groups_x
├── many_mesh_work_groups_y
├── many_mesh_work_groups_z
├── many_task_mesh_work_groups_x
├── many_task_mesh_work_groups_y
├── many_task_mesh_work_groups_z
├── many_task_work_groups_x
├── many_task_work_groups_y
├── many_task_work_groups_z
├── max_lines
├── max_points
├── max_triangles_workgroupsize_16
├── max_triangles_workgroupsize_32
├── max_triangles_workgroupsize_64
├── maximize_invocations_128
├── maximize_invocations_256
├── maximize_invocations_32
├── maximize_invocations_64
├── maximize_primitives
├── maximize_vertices
├── memory_barrier_shared_in_mesh_array
├── memory_barrier_shared_in_mesh_float
├── memory_barrier_shared_in_mesh_struct
├── memory_barrier_shared_in_mesh_uint64
├── memory_barrier_shared_in_mesh_vector
├── memory_barrier_shared_in_task_array
├── memory_barrier_shared_in_task_float
├── memory_barrier_shared_in_task_struct
├── memory_barrier_shared_in_task_uint64
├── memory_barrier_shared_in_task_vector
├── mixed_pipelines
├── mixed_pipelines_dynamic_topology
├── multiple_outputs_vertices
├── no_lines
├── no_points
├── no_triangles
├── payload_not_accessed
├── payload_read
├── push_constant
├── push_constant_and_task_shader
├── rebind_sets
├── single_line
├── single_point
├── single_point_default_size
├── single_triangle
└── work_group_ordering
```

The root comes from `createMeshShaderMiscTestsEXT`. The direct children above are the complete set of registered leaves. The `vk-default` mustpass file contains exactly 83 matching paths, from `dEQP-VK.mesh_shader.ext.misc.barrier_in_mesh` through `dEQP-VK.mesh_shader.ext.misc.work_group_ordering`; see [the exact mustpass slice](../../../mustpass/main/vk-default/mesh-shader.txt#L1930-L2012).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test leaf | The 83 names in the hierarchy | Selects one implementation path and its fixed or loop-generated parameters. | [`createMeshShaderMiscTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708-L7200) |
| Task execution | task count absent, or fixed `1x1x1`, `2x1x1`, `128`/`256`/`65535`-based counts | An absent task count dispatches mesh workgroups directly. A present count adds a task shader; `drawCount()` then uses the task count. | [`MiscTestParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L95-L133) |
| Mesh dispatch | `1x1x1`, `2x1x1`, `256`/`512`/`65535`-based counts | Controls direct mesh dispatch or the mesh-workgroup count emitted by a task shader. | [registration parameters](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6712-L6877) |
| Render extent | `1x1`, `1x1020`, `2x1`, `5x7`, `8x5`, `8x8`, `16x16`, `128x1`, `2040x2056`, `2048x2048`, `512x512` | Determines rasterization coverage, image allocation, and the reference-image dimensions. | [registration parameters](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6723-L6877) |
| Primitive topology | `points`, `lines`, `triangles` | Changes the EXT output topology and primitive-index array used by single-primitive, limit, and zero-output cases. | [primitive builders](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L721-L1204) |
| Large-dispatch axis | `_x`, `_y`, `_z` | Selects which component receives the large task or mesh workgroup count. | [large-workgroup registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6814-L6877) |
| Barrier location | `task`, `mesh` | Places the control or memory-barrier protocol in the task or mesh stage. | [barrier registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6918-L6977) |
| Memory barrier operation | `memory_barrier_shared`, `group_memory_barrier` | Selects `memoryBarrierShared()` or `groupMemoryBarrier()` while keeping the payload variants comparable. | [`MemoryBarrierParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L1754-L1786) |
| Barrier payload type | `struct`, `float`, `vector`, `array`, `uint64` | Changes the task payload declaration and the value written/read after the barrier. | [payload generation](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L1868-L1995) |
| Clip combination | `clip_geom` or `clip_plane`, with optional `_and_task_shader`, `_provoking_last`, and `_multiview` suffixes | Selects clip-distance versus clip-plane behavior and toggles task transport, provoking-vertex order, and multiview. | [clip registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6997-L7020) |
| Output-limit stress | `max_points`, `max_lines`, `max_triangles_workgroupsize_16`, `_32`, `_64`, `maximize_primitives`, `maximize_vertices`, `maximize_invocations_32`, `_64`, `_128`, `_256` | Holds the draw shape mostly fixed while stressing output counts, local size, or invocation count. | [limit registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6770-L6810), [maximization registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L7039-L7084) |
| Pipeline/state path | `mixed_pipelines`, `mixed_pipelines_dynamic_topology`, `rebind_sets`, `push_constant`, `push_constant_and_task_shader` | Changes classic/mesh pipeline use, dynamic topology, descriptor-set rebinding, or stage-visible push constants. | [stateful case registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L7023-L7035), [mixed pipelines](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L7087-L7103) |
| Invocation/assembly path | `first_invocation_mesh`, `first_invocation_task`, `local_size_id_mesh`, `local_size_id_task` | Selects direct mesh versus task execution and the first-invocation or specialization-constant behavior. | [invocation registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L7106-L7135) |
| Exact result path | image comparison, dual-reference comparison, or color/depth comparison | Selects the host result checker implemented by the case. | [common checker](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L220-L266), [specialized checks](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L1822-L1852), [ordering check](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6656-L6703) |

## Behavior Parameters

The primary behavioral axis is the registered test leaf. The source groups leaves by implementation mechanism, but it registers each as a direct child of `mesh_shader.ext.misc`.

### Task payload and primitive production

`complex_task_data` writes nested scalar, array, structure, vector, and workgroup-ID data in a task payload. The mesh shader validates the data before emitting two triangles per mesh workgroup. `payload_read` checks that all mesh invocations can read task payload data. `single_point`, `single_point_default_size`, `single_line`, and `single_triangle` provide minimal point, line, and triangle output paths. The default-size leaf omits the point-size write.

### Dispatch, zero output, and barriers

The `many_*_work_groups_*` leaves exercise large task, mesh, or task-plus-mesh dispatch counts along one selected axis. `no_points`, `no_lines`, and `no_triangles` call `SetMeshOutputsEXT(0, 0)` for the selected topology. `barrier_in_task` and `barrier_in_mesh` test control barriers. The 20 memory-barrier leaves combine stage, barrier function, and payload representation.

### Interfaces, clipping, and state

`custom_attributes` passes interpolated, flat, per-primitive, primitive-ID, viewport-index, and clip-distance data into the fragment shader. The 16 `clip_*` leaves vary clip implementation, task use, provoking-vertex order, and multiview. Push-constant leaves read values in mesh-only or task-plus-mesh pipelines. `multiple_outputs_vertices` checks interpolation of per-vertex values, while `payload_not_accessed` checks the corresponding mesh output path when task payload data is not used.

### Limits, pipeline switching, and invocation rules

The maximum-output leaves write the requested number of points, lines, triangles, vertices, or invocations. `mixed_pipelines` alternates classic indexed rendering and mesh rendering; its dynamic-topology sibling also changes the topology state. `rebind_sets` changes descriptor sets and mesh push constants between four draws. `first_invocation_*` tests the invocation that supplies task or mesh values used for work generation. `local_size_id_*` supplies workgroup dimensions through specialization constants and direct SPIR-V. The final `emit_in_control_flow*` and `work_group_ordering` leaves test dynamic `EmitMeshTasksEXT` placement and ordering of many workgroups.

## Shader Analysis

The selected representative below uses the smallest generated mesh shader, `single_point`. It shows the EXT output declarations, `SetMeshOutputsEXT`, per-primitive color, position, point size, and primitive index without reproducing the source-controlled direct assembly used by `local_size_id_*`. The source generates the mesh and fragment programs through `vk::SourceCollections`; the generated GLSL path uses SPIR-V 1.4 build options from `getMinMeshEXTBuildOptions`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.misc.single_point
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Mesh-only, `meshCount = 1x1x1` | One mesh workgroup runs without a task shader. |
| `width = 5`, `height = 7` | The reference image has odd dimensions, so its center pixel is unambiguous. |
| One point, `writePointSize = true` | The shader emits one cyan point at the clip-space origin and writes point size `1.0`. |

#### Purpose

This case checks the minimum EXT mesh-to-fragment rendering path: one mesh workgroup sets one point output, assigns its position and color, and produces the expected center pixel.

#### Structural Design

| Phase | Shader action | Observable effect |
|-------|---------------|-------------------|
| Configure | `layout(points) out` and `SetMeshOutputsEXT(1u, 1u)` | Declares one valid vertex and one valid point primitive. |
| Write | Store cyan `pointColor`, origin `gl_Position`, point size `1.0`, and index `0`. | Supplies the point to rasterization. |
| Consume | The common fragment shader copies `primitiveColor` to `outColor`. | The point is cyan; untouched pixels remain clear. |
| Check | The host compares the copied image with the reference. | Only pixel `(2, 3)` should contain the cyan point. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable

layout(local_size_x=1) in;
layout(points) out;
layout(max_vertices=256, max_primitives=256) out;

layout (location=0) out perprimitiveEXT vec4 pointColor[];

void main ()
{
    SetMeshOutputsEXT(1u, 1u);
    pointColor[0] = vec4(0.0f, 1.0f, 1.0f, 1.0f);
    gl_MeshVerticesEXT[0].gl_Position = vec4(0.0f, 0.0f, 0.0f, 1.0f);
    gl_MeshVerticesEXT[0].gl_PointSize = 1.0f;
    gl_PrimitivePointIndicesEXT[0] = 0;
}
```

The fixed fragment shader declares `layout (location=0) in perprimitiveEXT vec4 primitiveColor` and writes it unchanged to the RGBA8 color attachment.

#### Additional Info

- The `single_point_default_size` sibling uses the same geometry but omits the `gl_PointSize` store and requires `VK_KHR_maintenance5`; the source comment identifies the tested default as `1.0f`.
- `local_size_id_mesh` and `local_size_id_task` use source-controlled SPIR-V assembly, not generated GLSL. The page does not edit or reconstruct those assembly artifacts.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Primitive topology | Point output becomes line or triangle output with different index arrays and reference coverage. | [single primitive builders](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L721-L907) |
| Task execution | A task stage and `taskPayloadSharedEXT` transport appear when the leaf has a task count. | [common task selection](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L117-L132) |
| Point-size behavior | The default-size sibling omits the explicit point-size store and adds the maintenance5 support gate. | [single-point case](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L681-L750) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: mesh
- Target SPIRV version: spirv1.4

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 39
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %pointColor %gl_MeshVerticesEXT %gl_PrimitivePointIndicesEXT
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main OutputVertices 256
               OpExecutionMode %main OutputPrimitivesEXT 256
               OpExecutionMode %main OutputPoints
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %pointColor "pointColor"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %gl_PrimitivePointIndicesEXT "gl_PrimitivePointIndicesEXT"
               OpDecorate %pointColor Location 0
               OpDecorate %pointColor PerPrimitiveEXT
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %gl_PrimitivePointIndicesEXT BuiltIn PrimitivePointIndicesEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
   %uint_256 = OpConstant %uint 256
%_arr_v4float_uint_256 = OpTypeArray %v4float %uint_256
%_ptr_Output__arr_v4float_uint_256 = OpTypePointer Output %_arr_v4float_uint_256
 %pointColor = OpVariable %_ptr_Output__arr_v4float_uint_256 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %18 = OpConstantComposite %v4float %float_0 %float_1 %float_1 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_256 = OpTypeArray %gl_MeshPerVertexEXT %uint_256
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_256
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 Output
         %26 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
      %int_1 = OpConstant %int 1
%_ptr_Output_float = OpTypePointer Output %float
%_arr_uint_uint_256 = OpTypeArray %uint %uint_256
%_ptr_Output__arr_uint_uint_256 = OpTypePointer Output %_arr_uint_uint_256
%gl_PrimitivePointIndicesEXT = OpVariable %_ptr_Output__arr_uint_uint_256 Output
     %uint_0 = OpConstant %uint 0
%_ptr_Output_uint = OpTypePointer Output %uint
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpSetMeshOutputsEXT %uint_1 %uint_1
         %20 = OpAccessChain %_ptr_Output_v4float %pointColor %int_0
               OpStore %20 %18
         %27 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %int_0 %int_0
               OpStore %27 %26
         %30 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %int_0 %int_1
               OpStore %30 %float_1
         %36 = OpAccessChain %_ptr_Output_uint %gl_PrimitivePointIndicesEXT %int_0
               OpStore %36 %uint_0
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The common case requires `VK_EXT_mesh_shader`, then checks the EXT `taskShader` feature when a task count is present and the EXT `meshShader` feature for every ordinary mesh case. It allocates a single-sample `VK_FORMAT_R8G8B8A8_UNORM` image with color-attachment and transfer-source usage; task-only paths also use storage-image usage and a task-stage descriptor.
- The host creates the generated shader modules and graphics pipeline, begins a command buffer, optionally transitions the image to `VK_IMAGE_LAYOUT_GENERAL`, binds the pipeline and descriptor set, and calls `vkCmdDrawMeshTasksEXT` with `drawCount().x/y/z`.
- After rendering, the host transitions the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, copies it to a host-visible verification buffer, inserts a transfer-to-host barrier, waits for submission, invalidates the allocation, and compares the result.
- The common `tcu::floatThresholdCompare` uses `0.005` in all four channels. The point, line, triangle, maximum, large-workgroup, payload, barrier, clip, push-constant, and most state cases generate their reference image from the same fixed dimensions and expected geometry.
- `MemoryBarrierInstance` accepts either a solid blue or solid black reference. `emit_in_control_flow` uses a 2x1 image and an exact threshold. `work_group_ordering` copies both an RGBA8 color image and a D16 depth image and compares them with color threshold `0.005` and depth threshold `0.000025`.
- `rebind_sets` uploads four host-visible red-component buffers and four 1x1 sampled images, binds a different set and push-constant offset for each draw, and checks four colored quadrants. `mixed_pipelines` alternates classic and mesh draws and checks four exact quadrant colors.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `complex_task_data` | Task-payload layout or value transport, mesh validation, workgroup-ID placement, primitive emission, rasterization, copyback, or reference mismatch. |
| `single_point`, `single_point_default_size`, `single_line`, `single_triangle` | Primitive topology, `SetMeshOutputsEXT`, point-size/default-size behavior, vertex/index emission, rasterization, or image comparison. |
| `max_points`, `max_lines`, `max_triangles_workgroupsize_64`, `max_triangles_workgroupsize_32`, `max_triangles_workgroupsize_16`, `maximize_primitives`, `maximize_vertices`, `maximize_invocations_32`, `maximize_invocations_64`, `maximize_invocations_128`, `maximize_invocations_256` | Mesh output-count/local-size limit handling, generated indexing, shader compilation, rasterization, or host reference construction. |
| `many_task_work_groups_x`, `many_mesh_work_groups_x`, `many_task_mesh_work_groups_x`, and the corresponding `_y`/`_z` leaves | Dispatch dimension limits, task-to-mesh indexing, generated point placement, or large-image copyback/comparison. |
| `no_points`, `no_lines`, `no_triangles` | Incorrect zero primitive count, illegal output writes, topology handling, or non-clear framebuffer result. |
| `barrier_in_task`, `barrier_in_mesh`, the `memory_barrier_shared_*` leaves, or the `group_memory_barrier_*` leaves | Workgroup control synchronization, shared-memory ordering, payload representation, atomic/update behavior, or accepted-reference handling. |
| `custom_attributes`, `custom_attributes_and_task_shader` | Custom interface qualifiers, primitive ID, viewport index, clip-distance data, task transport, or descriptor-backed value checks. |
| Any `clip_*` or `clip_plane*` leaf | Clip-distance/clip-plane behavior, multiview mesh support, provoking-vertex selection, task transport, or framebuffer comparison. |
| `push_constant`, `push_constant_and_task_shader` | Push-constant range/stage visibility, payload transport, primitive output, or image comparison. |
| `mixed_pipelines`, `mixed_pipelines_dynamic_topology` | Classic/mesh pipeline compatibility, dynamic topology state, descriptor or push-constant state, rasterization, or quadrant reference. |
| `first_invocation_mesh`, `first_invocation_task` | First-invocation semantics, subgroup-basic behavior, task count, mesh output count, or pixel-count comparison. |
| `local_size_id_mesh`, `local_size_id_task` | Maintenance4/SPIR-V `LocalSizeId` handling, specialization-map values, direct assembly, or output comparison. |
| `payload_read`, `rebind_sets`, `multiple_outputs_vertices`, `payload_not_accessed` | Payload visibility, descriptor-set rebinding, per-vertex interpolation, push constants, generated outputs, or copyback. |
| `emit_in_control_flow`, `emit_in_control_flow_bad_emit_last` | Dynamic control-flow placement of `EmitMeshTasksEXT`, first-invocation semantics, or exact 2x1 image result. |
| `work_group_ordering` | Task/mesh workgroup ordering, storage-buffer geometry reads, color/depth rasterization, or final-batch reference comparison. |

### Cause Analysis

#### Task and mesh execution

**Possible failure symptoms:** A task-enabled case emits no expected geometry, produces the wrong primitive count, or fails a large-dispatch comparison. A mesh-only case can fail when direct mesh dispatch or output indexing is wrong.

**Possible implementation causes:** The implementation may mishandle `EmitMeshTasksEXT`, `SetMeshOutputsEXT`, task/mesh workgroup IDs, local invocation values, output arrays, or primitive indices. The failing case and validation log are needed to separate those possibilities.

#### Payload and stage interface transport

**Possible failure symptoms:** `complex_task_data` loses a quadrant, a payload read case fails, or a state/interface case renders the wrong color. A bad custom attribute or payload predicate can make a whole rendered region fail.

**Possible implementation causes:** The task payload layout, stage interface location, interpolation qualifier, descriptor read, push-constant visibility, or per-primitive transport may be wrong. The source does not identify a single fault location before the failing leaf and log are known.

#### Synchronization and ordering

**Possible failure symptoms:** A barrier case produces neither accepted solid image, or `work_group_ordering` reports color/depth mismatches against the final geometry batch.

**Possible implementation causes:** The implementation may mishandle workgroup control synchronization, shared-memory ordering, task/mesh ordering, or the selected barrier operation. The dual memory-barrier references encode the two results permitted by the source's loop-parity behavior.

#### Limits, features, and shader compilation

**Possible failure symptoms:** A limit case cannot run or produces incomplete geometry; a clip or default-size case fails only on its optional feature; a `LocalSizeId` case fails during pipeline creation or result comparison.

**Possible implementation causes:** A support check may have exposed an unsupported feature or property, or the implementation may mishandle the enabled feature, output limit, SPIR-V execution mode, specialization map, or generated shader. A pruned case is a support result, not a conformance failure.

#### Host resources and result checking

**Possible failure symptoms:** Multiple leaves fail at copyback, image layout, descriptor setup, or comparison even when shader output appears plausible.

**Possible implementation causes:** The image transition, transfer synchronization, host visibility, descriptor rebinding, color/depth format interpretation, viewport, or reference construction may be wrong. The checker reports image differences, so the comparison log must be read with the leaf's reference-generation code.

## Case Pruning

### Requirement-based pruning

- `checkTaskMeshShaderSupportEXT` requires `VK_EXT_mesh_shader` and the requested EXT `taskShader` and `meshShader` feature bits. Ordinary task-enabled leaves request both; mesh-only leaves request only mesh support.
- `single_point_default_size` requires `VK_KHR_maintenance5` because it omits the explicit point-size write.
- `custom_attributes` requires core `multiViewport` and `shaderClipDistance`. Clip cases require those features as well. Provoking-last variants require `VK_EXT_provoking_vertex`; multiview variants require core multiview and EXT `multiviewMeshShader`.
- `maximize_*` cases query EXT mesh-shader properties and throw `NotSupportedError` if the requested local size, output vertex count, or output primitive count is not supported.
- `first_invocation_*` requires Vulkan API 1.1 and subgroup basic operations. `local_size_id_*` requires `VK_KHR_maintenance4` and uses SPIR-V 1.5 assembly with maintenance4 enabled.
- `work_group_ordering` and `emit_in_control_flow*` request task/mesh support and `vertexPipelineStoresAndAtomics` through their explicit support helpers.

A requirement-pruned case is unsupported on the current device or API configuration. It does not establish that the shader or runtime behavior failed.

### Design-based pruning

- The `no_*_extra_writes` branch is skipped by `continue`; it is preceded by a source comment questioning legality and is absent from the registration tree and mustpass file.
- `multiple_task_payloads` is inside `if (false)` with a source comment that the case may be illegal. Its class and direct SPIR-V builder remain in the source, but the test is not registered and must not be counted.
- The source therefore registers 83 leaves, not every branch or every possible Cartesian product of the dimensions shown above.
- `local_size_id_*` is documented as a direct-SPIR-V path. The CTS source owns that assembly; this page does not rewrite, synthesize, or hand-edit it.

## Key Takeaways

- `mesh_shader.ext.misc` is one direct-child test family with 83 executable leaves in `vk-default`.
- The leaf names encode the meaningful behavior choice: stage use, topology, barrier and payload type, clip combination, limit stress, pipeline state, invocation rule, or ordering mode.
- Generated GLSL cases compile to EXT mesh-shader SPIR-V and render into host-checked images. `local_size_id_*` uses source-controlled SPIR-V and remains distinct from the generated-GLSL workflow.
- A failure means that the selected leaf's execution, generated interface, resource/state setup, result transfer, or reference comparison did not meet its contract. A support-pruned case means that the required feature or property was unavailable.
- The disabled extra-write and multiple-payload branches are source evidence for pruning, not additional coverage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Common parameters, support, shader collection, dispatch, copyback, comparison | [`MiscTestParams`, `MeshShaderMiscCase`, `MeshShaderMiscInstance`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L72-L465) | Defines the common parameter model, EXT feature gate, generated fragment shader, image setup, dispatch, copyback, and threshold. |
| Payload, primitive, large-workgroup, zero-output, and barrier cases | [early implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L467-L2128) | Defines the generated task/mesh programs and result references for the first case groups. |
| Custom attributes, clipping, and push constants | [interface and state cases](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L2129-L3660) | Defines stage interfaces, feature gates, clip combinations, and push-constant paths. |
| Limit and pipeline cases | [limit and mixed-pipeline implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L3661-L4378) | Defines output-limit checks, specialization of generated output counts, and classic/mesh pipeline switching. |
| Invocation and `LocalSizeId` cases | [invocation implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L4379-L4954) | Defines subgroup/API gates, first-invocation generation, and source-controlled SPIR-V specialization. |
| Payload, descriptors, output, control-flow, and ordering cases | [later implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L4955-L6704) | Defines descriptor rebinding, output interpolation, exact control-flow result, and color/depth ordering checks. |
| Registration and disabled branches | [`createMeshShaderMiscTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708-L7200) | Defines the exact 83 direct children and the branches excluded from coverage. |
| EXT support and generated shader target | [`checkTaskMeshShaderSupportEXT`, `getMinMeshEXTBuildOptions`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L149) | Requires EXT task/mesh features and selects SPIR-V 1.4 for generated GLSL. |
| vk-default coverage | [mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L1930-L2012) | Lists the exact 83 executable `mesh_shader.ext.misc` paths. |
| Task/mesh execution | [mesh-shader specification](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | Grounds task dispatch, payload, and mesh output explanations for the EXT conditional text. |
| Interfaces | [interfaces specification](../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292) | Grounds stage matching, locations, and interpolation. |
| Workgroups and barriers | [shaders specification](../../../../vulkan-docs/src/chapters/shaders.adoc#L2387-L2481) | Grounds workgroup and synchronization explanations. |
| Features and limits | [feature chapter](../../../../vulkan-docs/src/chapters/features.adoc#L1845-L1911), [limits chapter](../../../../vulkan-docs/src/chapters/limits.adoc#L6213-L6242) | Grounds feature/property pruning. |
| Mesh pipeline and draw validity | [pipeline chapter](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1155-L1170), [mesh draw validity](../../../../vulkan-docs/src/chapters/commonvalidity/draw_mesh_common.adoc) | Grounds mesh pipeline stages and `vkCmdDrawMeshTasksEXT`. |
