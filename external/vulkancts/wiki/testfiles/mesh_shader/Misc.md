## Overview

**Core question:** Do the NV mesh and task shader paths preserve generated data and produce the primitives, interfaces, barriers, and pipeline results that each registered case requires?

- [`vktMeshShaderMiscTests.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp) owns two implemented NV test families: the direct-leaf `misc` family and the generated `in_out` family.
- `misc` checks primitive emission, task-to-mesh payloads, barriers, custom attributes, push constants, large workgroups, output limits, and mixing classic and mesh pipelines.
- `in_out` generates interface-variable permutations across vertex/per-primitive ownership, numeric type, bit width, vector dimension, interpolation, and mesh-only/task-mesh execution.
- Both families render to an RGBA8 image, copy it to a host-visible buffer, and compare against a source-generated reference. A failing image means that at least one tested shader, interface, runtime, or result path did not meet its case-specific contract.

## Background Knowledge

- **Task and mesh workgroups.** A task shader is optional. When present, it writes `gl_TaskCountNV` to create mesh workgroups and can pass a task payload to every mesh workgroup it creates. A mesh workgroup writes its primitive count, vertices, indices, and stage outputs. See [NV mesh-shader execution](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc).
- **Shader interfaces.** A shader output matches the next stage's input by interface type and location. Mesh outputs can be per-vertex or per-primitive. Wide 64-bit vectors can consume two locations, and flat interpolation is needed for integer and per-primitive values. See [shader input and output interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292).
- **Workgroup synchronization.** `barrier()` synchronizes invocations in a local workgroup; `memoryBarrierShared()` orders shared-memory accesses, while `groupMemoryBarrier()` provides the corresponding group memory barrier operation. The test deliberately uses these operations to check whether a workgroup observes the state it expects. See [shader workgroups](../../../../vulkan-docs/src/chapters/shaders.adoc#L2389-L2480).

## Registration Hierarchy

```text
mesh_shader.nv.misc
├── complex_task_data
├── single_point
├── single_line
├── single_triangle
├── max_points
├── max_lines
├── max_triangles
├── many_task_work_groups
├── many_mesh_work_groups
├── many_task_mesh_work_groups
├── no_points
├── no_lines
├── no_triangles
├── no_points_extra_writes
├── no_lines_extra_writes
├── no_triangles_extra_writes
├── barrier_in_task
├── barrier_in_mesh
├── memory_barrier_shared_in_task
├── memory_barrier_shared_in_mesh
├── group_memory_barrier_in_task
├── group_memory_barrier_in_mesh
├── custom_attributes
├── custom_attributes_and_task_shader
├── push_constant
├── push_constant_and_task_shader
├── maximize_primitives
├── maximize_vertices
├── maximize_invocations_32
├── maximize_invocations_64
├── maximize_invocations_128
├── maximize_invocations_256
└── mixed_pipelines

mesh_shader.nv.in_out
├── 32_bits_only
├── with_i64
├── with_f64
├── all_but_16_bits
├── with_i16
├── with_f16
└── all_types
```

The first tree is registered by `createMeshShaderMiscTests`. The second is registered by `createMeshShaderInOutTests`; its feature-group children expand to `permutation_0` through `permutation_39`, each with `mesh_only` and `task_mesh` leaves. The complete executable coverage is listed in [`vk-default` mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L27356-L27948).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `misc`, `in_out` | Selects the direct miscellaneous behavior or generated interface-variable behavior. | [`createMeshShaderMiscTests` and `createMeshShaderInOutTests`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5232) |
| `misc` leaf | 33 exact leaves from the tree above | Selects primitive topology, task use, synchronization operation, resource/interface feature, workgroup stress, or pipeline behavior. | [`misc` registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5101) |
| Task execution | `taskCount` absent or fixed values such as `1`, `2`, `512`, `65535` | An absent value makes `drawCount()` use `meshCount`; a present value emits task shader workgroups and makes `drawCount()` use `taskCount`. | [`MiscTestParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L92-L124) |
| Mesh workgroups | `meshCount` values including `1`, `2`, `512`, `65535` | Controls direct mesh dispatch or the number of mesh workgroups created by a task shader. | [`misc` parameter construction](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4813-L4920) |
| Render extent | Exact leaf values including `1x1`, `5x7`, `8x5`, `16x16`, `32x32`, `1360x1542`, `4096x2048` | Changes rasterization coverage, reference-image size, and stress-case geometry. | [`misc` parameter construction](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4823-L4920) |
| Primitive mode | `points`, `lines`, `triangles` | Selects the mesh output topology for no-primitive and single-primitive paths. | [`NoPrimitives` registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4922-L4950) |
| Barrier location | `task`, `mesh` | Places the barrier protocol in the task or mesh shader. | [`barrier` registration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4953-L4999) |
| Memory barrier operation | `memory_barrier_shared`, `group_memory_barrier` | Selects the GLSL memory-barrier function while keeping the two-invocation protocol otherwise comparable. | [`MemoryBarrierParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L1576-L1613) |
| Extra writes | absent or `_extra_writes` | The extra-write variants emit vertices/indices and task payload data even though the computed primitive count is zero. | [`NoPrimitivesExtraWritesCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L1315-L1444) |
| Maximization axis | `primitives`, `vertices`, `invocations_32`, `invocations_64`, `invocations_128`, `invocations_256` | Holds most output dimensions fixed while stressing one local-size or output-count limit. | [`Maximize*` registrations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5034-L5082) |
| Interface feature group | `32_bits_only`, `with_i64`, `with_f64`, `all_but_16_bits`, `with_i16`, `with_f16`, `all_types` | Enables the corresponding 64-bit or 16-bit candidate types without expanding to every feature combination. | [`requiredFeatures`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5109-L5123) |
| Interface owner | `vertex`, `primitive` | Makes a generated value per-vertex or per-primitive and changes its array length and checking rule. | [`IfaceVar`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L2958-L3133) |
| Interface data type | `float`, `integer` | Selects floating-point or integer GLSL types. Integer values use flat interpolation. | [`IfaceVar::getGLSLType` and declaration](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3018-L3055) |
| Interface bit width | `64`, `32`, `16` | Changes the scalar/vector type and, for 64-bit vectors of dimension 3 or 4, consumes two locations. | [`IfaceVar::getLocationSize`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3012-L3016) |
| Interface dimension | `scalar`, `vec2`, `vec3`, `vec4` | Changes the generated declaration, source buffer member, assignment, and comparison. | [`dataDimCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5125-L5129) |
| Interpolation | `normal`, `flat` | Selects interpolated per-vertex delivery or flat delivery. Per-primitive values are flat by construction. | [`interpolationCases` and pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5125-L5168) |
| Permutation | `permutation_0` through `permutation_39` | Uses a fixed-seed shuffle to vary declaration order and location packing; the full permutation space is intentionally not registered. | [`in_out` permutation generation](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5175-L5202) |
| Interface pipeline shape | `mesh_only`, `task_mesh` | Reads source data directly in the mesh shader or copies it through task payload memory first. | [`in_out` leaf construction](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5204-L5224) |

`vk-default` contains exactly 33 `dEQP-VK.mesh_shader.nv.misc.*` entries and 560 `dEQP-VK.mesh_shader.nv.in_out.*` entries. The latter is seven feature groups × 40 permutations × two pipeline shapes.

## Behavior Parameters

The primary behavioral axis is the test family. `misc` selects one of 33 distinct implementation behaviors; `in_out` selects the generated interface-preservation contract. The matrix above records the secondary dimensions that shape each family.

### `misc` — focused NV mesh behavior

The direct leaves use small, fixed parameter sets rather than a single Cartesian product. They cover ordinary point/line/triangle emission, zero output, task payloads, local barriers, attributes, push constants, output-limit stress, large dispatch counts, and a render pass that switches between classic and mesh pipelines.

### `in_out` — generated interface preservation

Each leaf carries one legal, shuffled interface-variable list. The mesh shader emits a two-triangle quad and copies each variable from a descriptor-backed source or task payload into a matching output. The fragment shader checks the corresponding inputs and emits blue only when the aggregate condition succeeds.

## Shader Analysis

The source generates GLSL for every selected case through `vk::SourceCollections`; CTS then compiles those sources to the runtime shader modules. The representative walkthrough below follows the task-payload path. `in_out` has the same task-to-mesh shape but expands declarations and checks from its selected permutation, so the generated source is better explained by the parameter and resource tables than by duplicating a very large permutation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.nv.misc.complex_task_data
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `taskCount = 2`, `meshCount = 2` | The task shader creates two mesh workgroups, each carrying one nested payload. |
| `width = 8`, `height = 8` | The mesh workgroups place their two-triangle quads into a 2x2 image arrangement. |
| `taskNV TaskData` with nested structures and arrays | Exercises scalar, vector, array, structure, and nested task-to-mesh layout transport rather than a single scalar. |

#### Purpose

This case checks that a task shader can write a nested `taskNV` payload and that the mesh shader receives the correct values before emitting its quadrant.

#### Structural Design

| Phase | Task shader | Mesh shader |
|-------|-------------|-------------|
| Publish | Set `gl_TaskCountNV = 2u` and fill `td` with constants and workgroup-derived values. | Read `td` as an input block. |
| Validate | The task shader writes the payload. | Check `td.yes`, the million-valued fields, the row ID, and each generated array/vector value. |
| Emit | No mesh vertices. | Set `gl_PrimitiveCountNV = 2u`, write a colored quad, and place it from `rowId` and `gl_WorkGroupID.x`. |
| Failure signal | A malformed payload is not directly reported. | Set primitive count to zero, so the corresponding image region does not match the reference. |

#### Shader Code

##### Compute-style Task Shader

```glsl
#version 450
#extension GL_NV_mesh_shader : enable

layout (local_size_x=1) in;

/// The task shader creates two mesh workgroups and publishes one nested payload to each.
out taskNV TaskData {
    uint yes;
    struct ExternalData {
        float OneMillion;
        uint TwoMillion;
        struct WorkGroupData {
            float WorkGroupIdPlusOnex1000Iota[10];
            uint rowId;
            uvec3 WorkGroupIdPlusOnex2000Iota;
            vec2 WorkGroupIdPlusOnex3000Iota;
        } workGroupData;
    } externalData;
} td;

void main ()
{
    gl_TaskCountNV = 2u;
    td.yes = 1u;
    td.externalData.OneMillion = 1000000.0;
    td.externalData.TwoMillion = 2000000u;
    for (uint i = 0; i < 10; i++) {
        td.externalData.workGroupData.WorkGroupIdPlusOnex1000Iota[i] =
            float((gl_WorkGroupID.x + 1u) * 1000 + i);
    }
    uint baseVal = (gl_WorkGroupID.x + 1u) * 2000;
    td.externalData.workGroupData.WorkGroupIdPlusOnex2000Iota =
        uvec3(baseVal, baseVal + 1, baseVal + 2);
    baseVal = (gl_WorkGroupID.x + 1u) * 3000;
    td.externalData.workGroupData.WorkGroupIdPlusOnex3000Iota =
        vec2(baseVal, baseVal + 1);
    td.externalData.workGroupData.rowId = gl_WorkGroupID.x;
}
```

##### Geometry-producing Mesh Shader

```glsl
#version 450
#extension GL_NV_mesh_shader : enable

layout(local_size_x=2) in;
layout(triangles) out;
layout(max_vertices=4, max_primitives=2) out;

/// The mesh consumes the task payload and emits two per-primitive colors.
in taskNV TaskData {
    uint yes;
    struct ExternalData {
        float OneMillion;
        uint TwoMillion;
        struct WorkGroupData {
            float WorkGroupIdPlusOnex1000Iota[10];
            uint rowId;
            uvec3 WorkGroupIdPlusOnex2000Iota;
            vec2 WorkGroupIdPlusOnex3000Iota;
        } workGroupData;
    } externalData;
} td;
layout (location=0) out perprimitiveNV vec4 triangleColor[];

void main ()
{
    bool dataOK = true;
    dataOK = dataOK && (td.yes == 1u);
    dataOK = dataOK && (td.externalData.OneMillion == 1000000.0 &&
                        td.externalData.TwoMillion == 2000000u);
    uint rowId = td.externalData.workGroupData.rowId;
    dataOK = dataOK && (rowId == 0u || rowId == 1u);
    /// The generator emits further loops here for all ten scalar and both vector payload checks.
    if (dataOK) {
        gl_PrimitiveCountNV = 2u;
    } else {
        gl_PrimitiveCountNV = 0u;
        return;
    }
    uint columnId = gl_WorkGroupID.x;
    triangleColor[0] = vec4(rowId, columnId, 1.0f, 1.0f);
    triangleColor[1] = triangleColor[0];
    /// Each local invocation writes two vertices; the two invocations form the quadrant quad.
    vec4 left  = vec4(0.0, 0.0, 0.0, 1.0);
    vec4 right = vec4(1.0, 0.0, 0.0, 1.0);
    left.y += float(gl_LocalInvocationID.x);
    right.y += float(gl_LocalInvocationID.x);
    left.x += float(int(columnId) - 1);
    right.x += float(int(columnId) - 1);
    left.y += float(int(rowId) - 1);
    right.y += float(int(rowId) - 1);
    uint baseVertexId = 2 * gl_LocalInvocationID.x;
    gl_MeshVerticesNV[baseVertexId + 0].gl_Position = left;
    gl_MeshVerticesNV[baseVertexId + 1].gl_Position = right;
    uint baseIndexId = 3 * gl_LocalInvocationID.x;
    gl_PrimitiveIndicesNV[baseIndexId + 0] = 0 + gl_LocalInvocationID.x;
    gl_PrimitiveIndicesNV[baseIndexId + 1] = 1 + gl_LocalInvocationID.x;
    gl_PrimitiveIndicesNV[baseIndexId + 2] = 2 + gl_LocalInvocationID.x;
}
```

#### Additional Info

- The task and mesh blocks above are a compact reconstruction of the generator branch; the source emits the complete nested declarations and all value checks in [`ComplexTaskDataCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L455-L614).
- The fixed fragment shader passes `primitiveColor` through to `outColor`; it does not perform the payload checks itself. The mesh shader's primitive count determines whether the expected colored region exists.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Task execution | Mesh-only cases omit the task block; task-enabled cases add `taskNV` output and mesh input declarations. | [`MeshShaderMiscCase` and `MiscTestParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L92-L167) |
| Primitive leaf | Single, zero, maximum, and stress leaves change topology, output counts, local size, and vertex/index generation. | [`misc` case builders](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L621-L1444) |
| Interface pipeline shape | `in_out.mesh_only` reads `pvd`/`ppd` directly; `in_out.task_mesh` copies the same selected values through `td`. | [`InterfaceVariablesCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3570-L3747) |
| Interface variable list | Each fixed-seed permutation changes declaration order, locations, types, arrays, and generated assignments/checks. | [`in_out` generation](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5132-L5229) |

#### SPIR-V

##### Compute-style Task SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `task`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 62
; Schema: 0
               OpCapability MeshShadingNV
               OpExtension "SPV_NV_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TaskNV %main "main" %gl_TaskCountNV %td %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_NV_mesh_shader"
               OpName %main "main"
               OpName %gl_TaskCountNV "gl_TaskCountNV"
               OpName %RowId "RowId"
               OpMemberName %RowId 0 "id"
               OpName %WorkGroupData "WorkGroupData"
               OpMemberName %WorkGroupData 0 "values"
               OpMemberName %WorkGroupData 1 "rowId"
               OpMemberName %WorkGroupData 2 "vectorValues"
               OpMemberName %WorkGroupData 3 "floatValues"
               OpName %ExternalData "ExternalData"
               OpMemberName %ExternalData 0 "oneMillion"
               OpMemberName %ExternalData 1 "twoMillion"
               OpMemberName %ExternalData 2 "workGroupData"
               OpName %TaskData "TaskData"
               OpMemberName %TaskData 0 "yes"
               OpMemberName %TaskData 1 "externalData"
               OpName %td "td"
               OpName %i "i"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpDecorate %gl_TaskCountNV BuiltIn TaskCountNV
               OpDecorate %_arr_float_uint_10 ArrayStride 4
               OpMemberDecorate %RowId 0 Offset 0
               OpMemberDecorate %WorkGroupData 0 Offset 0
               OpMemberDecorate %WorkGroupData 1 Offset 40
               OpMemberDecorate %WorkGroupData 2 Offset 48
               OpMemberDecorate %WorkGroupData 3 Offset 64
               OpMemberDecorate %ExternalData 0 Offset 0
               OpMemberDecorate %ExternalData 1 Offset 4
               OpMemberDecorate %ExternalData 2 Offset 16
               OpDecorate %TaskData Block
               OpMemberDecorate %TaskData 0 Offset 0
               OpMemberDecorate %TaskData 0 PerTaskNV
               OpMemberDecorate %TaskData 1 Offset 16
               OpMemberDecorate %TaskData 1 PerTaskNV
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_TaskCountNV = OpVariable %_ptr_Output_uint Output
     %uint_2 = OpConstant %uint 2
      %float = OpTypeFloat 32
    %uint_10 = OpConstant %uint 10
%_arr_float_uint_10 = OpTypeArray %float %uint_10
      %RowId = OpTypeStruct %uint
     %v3uint = OpTypeVector %uint 3
    %v2float = OpTypeVector %float 2
%WorkGroupData = OpTypeStruct %_arr_float_uint_10 %RowId %v3uint %v2float
%ExternalData = OpTypeStruct %float %uint %WorkGroupData
   %TaskData = OpTypeStruct %uint %ExternalData
%_ptr_Output_TaskData = OpTypePointer Output %TaskData
         %td = OpVariable %_ptr_Output_TaskData Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
%float_1000000 = OpConstant %float 1000000
%_ptr_Output_float = OpTypePointer Output %float
%uint_2000000 = OpConstant %uint 2000000
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
      %int_2 = OpConstant %int 2
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
  %uint_1000 = OpConstant %uint 1000
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
               OpStore %gl_TaskCountNV %uint_2
         %24 = OpAccessChain %_ptr_Output_uint %td %int_0
               OpStore %24 %uint_1
         %28 = OpAccessChain %_ptr_Output_float %td %int_1 %int_0
               OpStore %28 %float_1000000
         %30 = OpAccessChain %_ptr_Output_uint %td %int_1 %int_1
               OpStore %30 %uint_2000000
               OpStore %i %uint_0
               OpBranch %34
         %34 = OpLabel
               OpLoopMerge %36 %37 None
               OpBranch %38
         %38 = OpLabel
         %39 = OpLoad %uint %i
         %41 = OpULessThan %bool %39 %uint_10
               OpBranchConditional %41 %35 %36
         %35 = OpLabel
         %43 = OpLoad %uint %i
         %47 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %48 = OpLoad %uint %47
         %49 = OpIAdd %uint %48 %uint_1
         %51 = OpIMul %uint %49 %uint_1000
         %52 = OpLoad %uint %i
         %53 = OpIAdd %uint %51 %52
         %54 = OpConvertUToF %float %53
         %55 = OpAccessChain %_ptr_Output_float %td %int_1 %int_2 %int_0 %43
               OpStore %55 %54
               OpBranch %37
         %37 = OpLabel
         %56 = OpLoad %uint %i
         %57 = OpIAdd %uint %56 %int_1
               OpStore %i %57
               OpBranch %34
         %36 = OpLabel
         %58 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %59 = OpLoad %uint %58
         %60 = OpAccessChain %_ptr_Output_uint %td %int_1 %int_2 %int_1 %int_0
               OpStore %60 %59
               OpReturn
               OpFunctionEnd
```

</details>

##### Geometry-producing Mesh SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 141
; Schema: 0
               OpCapability MeshShadingNV
               OpExtension "SPV_NV_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshNV %main "main" %td %gl_PrimitiveCountNV %gl_WorkGroupID %triangleColor %gl_MeshVerticesNV %gl_PrimitiveIndicesNV
               OpExecutionMode %main LocalSize 2 1 1
               OpExecutionMode %main OutputVertices 4
               OpExecutionMode %main OutputPrimitivesEXT 2
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 450
               OpSourceExtension "GL_NV_mesh_shader"
               OpName %main "main"
               OpName %dataOK "dataOK"
               OpName %RowId "RowId"
               OpMemberName %RowId 0 "id"
               OpName %WorkGroupData "WorkGroupData"
               OpMemberName %WorkGroupData 0 "values"
               OpMemberName %WorkGroupData 1 "rowId"
               OpMemberName %WorkGroupData 2 "vectorValues"
               OpMemberName %WorkGroupData 3 "floatValues"
               OpName %ExternalData "ExternalData"
               OpMemberName %ExternalData 0 "oneMillion"
               OpMemberName %ExternalData 1 "twoMillion"
               OpMemberName %ExternalData 2 "workGroupData"
               OpName %TaskData "TaskData"
               OpMemberName %TaskData 0 "yes"
               OpMemberName %TaskData 1 "externalData"
               OpName %td "td"
               OpName %rowId "rowId"
               OpName %gl_PrimitiveCountNV "gl_PrimitiveCountNV"
               OpName %columnId "columnId"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %triangleColor "triangleColor"
               OpName %gl_MeshPerVertexNV "gl_MeshPerVertexNV"
               OpMemberName %gl_MeshPerVertexNV 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexNV 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexNV 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexNV 3 "gl_CullDistance"
               OpMemberName %gl_MeshPerVertexNV 4 "gl_PositionPerViewNV"
               OpMemberName %gl_MeshPerVertexNV 5 "gl_ClipDistancePerViewNV"
               OpMemberName %gl_MeshPerVertexNV 6 "gl_CullDistancePerViewNV"
               OpName %gl_MeshVerticesNV "gl_MeshVerticesNV"
               OpName %gl_PrimitiveIndicesNV "gl_PrimitiveIndicesNV"
               OpDecorate %_arr_float_uint_10 ArrayStride 4
               OpMemberDecorate %RowId 0 Offset 0
               OpMemberDecorate %WorkGroupData 0 Offset 0
               OpMemberDecorate %WorkGroupData 1 Offset 40
               OpMemberDecorate %WorkGroupData 2 Offset 48
               OpMemberDecorate %WorkGroupData 3 Offset 64
               OpMemberDecorate %ExternalData 0 Offset 0
               OpMemberDecorate %ExternalData 1 Offset 4
               OpMemberDecorate %ExternalData 2 Offset 16
               OpDecorate %TaskData Block
               OpMemberDecorate %TaskData 0 Offset 0
               OpMemberDecorate %TaskData 0 PerTaskNV
               OpMemberDecorate %TaskData 1 Offset 16
               OpMemberDecorate %TaskData 1 PerTaskNV
               OpDecorate %gl_PrimitiveCountNV BuiltIn PrimitiveCountNV
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %triangleColor Location 0
               OpDecorate %triangleColor PerPrimitiveEXT
               OpDecorate %gl_MeshPerVertexNV Block
               OpMemberDecorate %gl_MeshPerVertexNV 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexNV 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexNV 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexNV 3 BuiltIn CullDistance
               OpMemberDecorate %gl_MeshPerVertexNV 4 BuiltIn PositionPerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 4 PerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 5 BuiltIn ClipDistancePerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 5 PerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 6 BuiltIn CullDistancePerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 6 PerViewNV
               OpDecorate %gl_PrimitiveIndicesNV BuiltIn PrimitiveIndicesNV
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %uint = OpTypeInt 32 0
      %float = OpTypeFloat 32
    %uint_10 = OpConstant %uint 10
%_arr_float_uint_10 = OpTypeArray %float %uint_10
      %RowId = OpTypeStruct %uint
     %v3uint = OpTypeVector %uint 3
    %v2float = OpTypeVector %float 2
%WorkGroupData = OpTypeStruct %_arr_float_uint_10 %RowId %v3uint %v2float
%ExternalData = OpTypeStruct %float %uint %WorkGroupData
   %TaskData = OpTypeStruct %uint %ExternalData
%_ptr_Input_TaskData = OpTypePointer Input %TaskData
         %td = OpVariable %_ptr_Input_TaskData Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
%_ptr_Input_float = OpTypePointer Input %float
%float_1000000 = OpConstant %float 1000000
%uint_2000000 = OpConstant %uint 2000000
%_ptr_Function_uint = OpTypePointer Function %uint
      %int_2 = OpConstant %int 2
     %uint_0 = OpConstant %uint 0
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_PrimitiveCountNV = OpVariable %_ptr_Output_uint Output
     %uint_2 = OpConstant %uint 2
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
    %v4float = OpTypeVector %float 4
%_arr_v4float_uint_2 = OpTypeArray %v4float %uint_2
%_ptr_Output__arr_v4float_uint_2 = OpTypePointer Output %_arr_v4float_uint_2
%triangleColor = OpVariable %_ptr_Output__arr_v4float_uint_2 Output
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_arr_float_uint_1 = OpTypeArray %float %uint_1
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_arr__arr_float_uint_1_uint_4 = OpTypeArray %_arr_float_uint_1 %uint_4
%gl_MeshPerVertexNV = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1 %_arr_v4float_uint_4 %_arr__arr_float_uint_1_uint_4 %_arr__arr_float_uint_1_uint_4
%_arr_gl_MeshPerVertexNV_uint_4 = OpTypeArray %gl_MeshPerVertexNV %uint_4
%_ptr_Output__arr_gl_MeshPerVertexNV_uint_4 = OpTypePointer Output %_arr_gl_MeshPerVertexNV_uint_4
%gl_MeshVerticesNV = OpVariable %_ptr_Output__arr_gl_MeshPerVertexNV_uint_4 Output
%uint_4294967295 = OpConstant %uint 4294967295
    %float_0 = OpConstant %float 0
      %int_3 = OpConstant %int 3
     %uint_6 = OpConstant %uint 6
%_arr_uint_uint_6 = OpTypeArray %uint %uint_6
%_ptr_Output__arr_uint_uint_6 = OpTypePointer Output %_arr_uint_uint_6
%gl_PrimitiveIndicesNV = OpVariable %_ptr_Output__arr_uint_uint_6 Output
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
     %uint_3 = OpConstant %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_2 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %dataOK = OpVariable %_ptr_Function_bool Function
      %rowId = OpVariable %_ptr_Function_uint Function
   %columnId = OpVariable %_ptr_Function_uint Function
         %24 = OpAccessChain %_ptr_Input_uint %td %int_0
         %25 = OpLoad %uint %24
         %27 = OpIEqual %bool %25 %uint_1
               OpStore %dataOK %27
         %28 = OpLoad %bool %dataOK
               OpSelectionMerge %30 None
               OpBranchConditional %28 %29 %30
         %29 = OpLabel
         %33 = OpAccessChain %_ptr_Input_float %td %int_1 %int_0
         %34 = OpLoad %float %33
         %36 = OpFOrdEqual %bool %34 %float_1000000
               OpSelectionMerge %38 None
               OpBranchConditional %36 %37 %38
         %37 = OpLabel
         %39 = OpAccessChain %_ptr_Input_uint %td %int_1 %int_1
         %40 = OpLoad %uint %39
         %42 = OpIEqual %bool %40 %uint_2000000
               OpBranch %38
         %38 = OpLabel
         %43 = OpPhi %bool %36 %29 %42 %37
               OpBranch %30
         %30 = OpLabel
         %44 = OpPhi %bool %28 %5 %43 %38
               OpStore %dataOK %44
         %48 = OpAccessChain %_ptr_Input_uint %td %int_1 %int_2 %int_1 %int_0
         %49 = OpLoad %uint %48
               OpStore %rowId %49
         %50 = OpLoad %bool %dataOK
               OpSelectionMerge %52 None
               OpBranchConditional %50 %51 %52
         %51 = OpLabel
         %53 = OpLoad %uint %rowId
         %55 = OpIEqual %bool %53 %uint_0
         %56 = OpLoad %uint %rowId
         %57 = OpIEqual %bool %56 %uint_1
         %58 = OpLogicalOr %bool %55 %57
               OpBranch %52
         %52 = OpLabel
         %59 = OpPhi %bool %50 %30 %58 %51
               OpStore %dataOK %59
         %60 = OpLoad %bool %dataOK
               OpSelectionMerge %62 None
               OpBranchConditional %60 %61 %66
         %61 = OpLabel
               OpStore %gl_PrimitiveCountNV %uint_2
               OpBranch %62
         %66 = OpLabel
               OpStore %gl_PrimitiveCountNV %uint_0
               OpReturn
         %62 = OpLabel
         %71 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %72 = OpLoad %uint %71
               OpStore %columnId %72
         %77 = OpLoad %uint %rowId
         %78 = OpConvertUToF %float %77
         %79 = OpLoad %uint %columnId
         %80 = OpConvertUToF %float %79
         %82 = OpCompositeConstruct %v4float %78 %80 %float_1 %float_1
         %84 = OpAccessChain %_ptr_Output_v4float %triangleColor %int_0
               OpStore %84 %82
         %85 = OpAccessChain %_ptr_Output_v4float %triangleColor %int_0
         %86 = OpLoad %v4float %85
         %87 = OpAccessChain %_ptr_Output_v4float %triangleColor %int_1
               OpStore %87 %86
         %97 = OpLoad %uint %columnId
         %98 = OpIAdd %uint %uint_4294967295 %97
         %99 = OpConvertUToF %float %98
        %100 = OpLoad %uint %rowId
        %101 = OpIAdd %uint %uint_4294967295 %100
        %102 = OpConvertUToF %float %101
        %104 = OpCompositeConstruct %v4float %99 %102 %float_0 %float_1
        %105 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_0 %int_0
               OpStore %105 %104
        %106 = OpLoad %uint %columnId
        %107 = OpConvertUToF %float %106
        %108 = OpLoad %uint %rowId
        %109 = OpIAdd %uint %uint_4294967295 %108
        %110 = OpConvertUToF %float %109
        %111 = OpCompositeConstruct %v4float %107 %110 %float_0 %float_1
        %112 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_1 %int_0
               OpStore %112 %111
        %113 = OpLoad %uint %columnId
        %114 = OpIAdd %uint %uint_4294967295 %113
        %115 = OpConvertUToF %float %114
        %116 = OpLoad %uint %rowId
        %117 = OpConvertUToF %float %116
        %118 = OpCompositeConstruct %v4float %115 %117 %float_0 %float_1
        %119 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_2 %int_0
               OpStore %119 %118
        %121 = OpLoad %uint %columnId
        %122 = OpConvertUToF %float %121
        %123 = OpLoad %uint %rowId
        %124 = OpConvertUToF %float %123
        %125 = OpCompositeConstruct %v4float %122 %124 %float_0 %float_1
        %126 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_3 %int_0
               OpStore %126 %125
        %131 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_0
               OpStore %131 %uint_0
        %132 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_1
               OpStore %132 %uint_1
        %133 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_2
               OpStore %133 %uint_2
        %134 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_3
               OpStore %134 %uint_2
        %136 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_4
               OpStore %136 %uint_1
        %139 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_5
               OpStore %139 %uint_3
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The shared NV case requires `VK_NV_mesh_shader`, then checks the requested task and mesh feature bits. It creates a 2D `VK_FORMAT_R8G8B8A8_UNORM` color image with color-attachment and transfer-source usage.
- The host creates a host-visible transfer-destination verification buffer sized for the configured image extent. It builds the pipeline from the generated `task`, `mesh`, and fixed `frag` binaries, records `vkCmdDrawMeshTasksNV`, submits, waits, and copies the image to the buffer.
- A color-attachment-to-transfer barrier changes the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`; a transfer-to-host memory barrier makes the copied bytes available for host inspection. The default comparison threshold is `0.005` in each channel.
- `complex_task_data` builds a quadrant reference from `rowId` and workgroup position. Single-primitive leaves build a solid clear image and paint the expected point, center line, or triangle. Maximum and large-workgroup leaves use reference geometry that reflects their generated output.
- `in_out` uses two host-filled storage buffers at descriptor bindings 0 and 1 for per-vertex and per-primitive source data. The generated mesh writes a two-triangle quad and sets `gl_MeshPrimitivesNV[].gl_PrimitiveID`; the generated fragment checks all selected interface values and emits solid blue only when every check succeeds.
- The `in_out` host then performs the same image copyback and compares the 8x8 image with solid blue. The image does not identify which variable failed; it is an aggregate result for that generated permutation.
- `mixed_pipelines` creates classic vertex/index buffers and a mesh-readable storage buffer, alternates classic indexed draws with `vkCmdDrawMeshTasksNV` in one render pass, and compares four exact colored quadrants.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `misc` | Incorrect NV task/mesh dispatch, payload transport, primitive emission, workgroup synchronization, push-constant/attribute access, output-limit handling, pipeline switching, rasterization, transfer/readback, or reference comparison for the failing leaf. |
| `in_out` | Incorrect generated interface declaration or location handling, task-payload transport, type conversion, per-vertex interpolation, flat/per-primitive delivery, feature handling, descriptor-backed source reads, rasterization, transfer/readback, or fragment-side comparison. |

### Cause Analysis

#### Task and mesh execution or dispatch

**Possible failure symptoms:** A task-enabled case emits no expected quadrant, produces the wrong number of primitives, or fails a large-workgroup image comparison. A mesh-only case can fail in the same way when direct mesh dispatch or output indexing is wrong.

**Possible implementation causes:** The implementation may mishandle `gl_TaskCountNV`, mesh-workgroup creation, NV local invocation built-ins, primitive count, vertex arrays, or primitive indices. The exact failing layer needs investigation from the failing case and validation log; the test does not assume a GPU, driver, or host location in advance.

#### Task payload and interface transport

**Possible failure symptoms:** `complex_task_data` loses a quadrant, or `in_out.task_mesh` renders black while `mesh_only` succeeds. `in_out` may fail only for particular numeric widths, vector dimensions, owners, or permutations.

**Possible implementation causes:** The task-to-mesh payload layout, generated member access, stage interface matching, location assignment, type conversion, or per-vertex/per-primitive transport may be incorrect. For `in_out`, a single failed generated fragment predicate makes the full image black, so the image alone cannot distinguish these causes.

#### Workgroup barriers and memory ordering

**Possible failure symptoms:** A barrier case renders black or an unexpected partial image; extra-write cases fail despite setting primitive count to zero; memory-barrier cases match neither accepted solid-blue nor solid-black reference.

**Possible implementation causes:** The implementation may mishandle local-workgroup control synchronization, shared-memory ordering, atomic updates, or the selected `memoryBarrierShared()` / `groupMemoryBarrier()` semantics. The accepted two-color result in the memory-barrier family reflects the source's permitted loop parity, not a weaker pass condition for arbitrary images.

#### Shader interface features and limits

**Possible failure symptoms:** A feature-group case fails to compile, links incorrectly, renders black, or fails only when 64-bit vectors, 16-bit types, flat values, or two-location vectors are present. Maximize cases fail at a particular requested local size or output count.

**Possible implementation causes:** The device may lack a required feature and should be pruned before execution; if support checks pass, a failure can indicate incorrect feature exposure, interface location/component accounting, shader compilation, or mesh output-limit handling. `in_out` explicitly checks the relevant core feature structures and the fragment-input-component budget.

#### Host setup, copyback, or reference comparison

**Possible failure symptoms:** The shader behavior appears correct in a rendered image but the case fails during copyback or image comparison, or the failure affects all leaves with a common extent.

**Possible implementation causes:** The image layout transition, transfer synchronization, buffer visibility, format interpretation, viewport/scissor setup, or host comparison path may be wrong. The test uses `VK_FORMAT_R8G8B8A8_UNORM` and a 0.005 threshold for the shared path; `mixed_pipelines` uses an exact threshold because its selected colors are exactly representable.

## Case Pruning

### Requirement-based pruning

- All executable leaves require `VK_NV_mesh_shader`, the NV mesh-shader feature, and the mesh stage. Task-enabled leaves additionally require the NV task-shader feature through `checkTaskMeshShaderSupportNV`.
- `custom_attributes` additionally requests `multiViewport` and `shaderClipDistance`, because its fragment checks `gl_ViewportIndex` and its mesh shader uses `gl_ClipDistance`.
- `in_out.with_i64` and groups that include integer 64-bit candidates require `shaderInt64`; groups with floating 64-bit candidates require `shaderFloat64`; `with_i16` and `all_types` require `shaderInt16`; `with_f16` and `all_types` require `shaderFloat16` and `storageInputOutput16`.
- `in_out` also rejects a device whose `maxFragmentInputComponents` is below `(11 + 16) * 4`, accounting for the glslang-generated built-ins and the maximum generated interface-location budget.
- Maximize cases use NV mesh-shader properties to test output and invocation limits; an unsupported device is not evidence of a shader failure.

This pruning means that the case is not legal or supported on the current implementation. The shared helper requires the extension and throws `NotSupportedError` when requested task or mesh features are absent.

### Design-based pruning

- The source intentionally registers only seven `in_out` feature groups instead of all 16 combinations of four feature booleans.
- It creates 40 fixed-seed pseudorandom permutations per feature group rather than every permutation of the candidate variable list. After shuffling, it truncates the list when adding another variable would exceed `InterfaceVariablesCase::kMaxLocations` (16).
- Integer values with normal interpolation, all per-primitive values with normal interpolation, and 64-bit floating-point values with normal interpolation are omitted because those combinations are not legal for this generated interface design.
- `count_reads` is not a registered executable case. Its construction is inside `if (false)` because the test did not work and the source notes that the specification was unclear; it must not be counted in coverage.
- The paired `mesh_only` and `task_mesh` leaves reuse the same shuffled interface list so the comparison isolates direct versus task-payload transport.

These exclusions are part of the test design and do not indicate a failed implementation.

## Key Takeaways

- The source owns two registration roots with different shapes: 33 direct `misc` leaves and 560 generated `in_out` leaves below seven feature groups, 40 permutations, and two pipeline shapes.
- `misc` turns NV mesh features into visible image contracts for payloads, primitive counts, barriers, output limits, push constants, attributes, and pipeline switching.
- `in_out` stresses the complete path from descriptor-backed host data through optional task payloads and generated mesh interfaces to fragment-side type and interpolation checks.
- A blue/black image is an aggregate signal. Use the exact leaf, generated branch, support checks, and comparison log to narrow the failure cause.
- `count_reads` is deliberately pruned and is absent from both registration and `vk-default` coverage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shared support, shader collection, image setup, dispatch, copyback | [`MeshShaderMiscCase`, `MeshShaderMiscInstance`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L69-L404) | Defines the NV support gate and common runtime/result path. |
| Complex task payload | [`ComplexTaskDataCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L406-L614) | Generates nested task data and mesh-side validation. |
| Primitive, zero-output, and extra-write cases | [case builders](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L621-L1444) | Shows topology, primitive-count, and output-array behavior. |
| Barrier cases | [`SimpleBarrierCase` and `MemoryBarrierCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L1446-L1776) | Generates control- and memory-barrier variants and accepted references. |
| Custom attributes and push constants | [attribute and push-constant cases](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L1778-L2604) | Covers generated custom outputs, resources, and push-constant paths. |
| Limit-oriented cases | [maximization cases](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L2610-L2916) | Varies primitive, vertex, and invocation pressure. |
| Interface variable model | [`IfaceVar`, `InterfaceVariableParams`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L2958-L3159) | Defines names, GLSL types, location sizes, arrays, and checks. |
| Interface support and generated shaders | [`InterfaceVariablesCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3161-L3747) | Applies feature gates and emits matching task/mesh/fragment interfaces. |
| Interface runtime and source data | [`InterfaceVariablesInstance`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3750-L4373) | Initializes buffers, dispatches, copies back, and compares blue output. |
| Mixed pipelines | [`initMixedPipelinesPrograms`, `testMixedPipelines`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4375-L4701) | Alternates classic and mesh pipelines in one render pass. |
| Registration roots | [`createMeshShaderMiscTests`, `createMeshShaderInOutTests`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5232) | Defines exact direct leaves, generated groups, permutations, and paired leaves. |
| NV extension and feature gate | [`checkTaskMeshShaderSupportNV`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires `VK_NV_mesh_shader` and requested task/mesh features. |
| Mustpass coverage | [`vk-default` mesh-shader list](../../../mustpass/main/vk-default/mesh-shader.txt#L27356-L27948) | Enumerates the exact 560 `in_out` and 33 `misc` executable paths. |
| Task/mesh execution specification | [NV mesh shader chapter](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | Defines task output, mesh input/output, and primitive production. |
| Interface matching and locations specification | [interfaces chapter](../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292) | Grounds generated location and stage-matching explanations. |
| Workgroup and barrier specification | [shaders chapter](../../../../vulkan-docs/src/chapters/shaders.adoc#L2389-L2480) | Grounds local workgroup and synchronization explanations. |