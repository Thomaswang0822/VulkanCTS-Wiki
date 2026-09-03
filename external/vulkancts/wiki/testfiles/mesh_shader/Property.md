## Overview

**Core question:** Does an implementation that exposes `VK_NV_mesh_shader` report every required NV mesh-shader minimum, and can it execute shader probes at the applicable boundary values?

- [`vktMeshShaderPropertyTests.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L56-L685) implements nine direct test case leaves under `mesh_shader.nv.property`.
- Each case first reads `VkPhysicalDeviceMeshShaderPropertiesNV` through the CTS context and compares one advertised limit with the Vulkan-required minimum used by the test.
- The cases then exercise that minimum through `vkCmdDrawMeshTasksNV`, task or mesh workgroup size, task output count, or shader shared memory. A host-visible storage buffer carries the result back to the CPU.
- The Vulkan default mesh-shader mustpass lists all nine leaves in [`mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L27949-L27957).

## Background Knowledge

- Vulkan exposes extension limits through structures in the `pNext` chain of `VkPhysicalDeviceProperties2`. For `VK_NV_mesh_shader`, `VkPhysicalDeviceMeshShaderPropertiesNV` reports draw, task-stage, and mesh-stage limits.
- Task and mesh shaders run in local workgroups. `max*WorkGroupInvocations` limits the product of the local X, Y, and Z sizes, while `max*WorkGroupSize` limits each dimension separately.
- A task shader may write `gl_TaskCountNV` to emit mesh workgroups. The value must not exceed `maxTaskOutputCount`. Without a task shader, `vkCmdDrawMeshTasksNV` launches mesh workgroups directly.
- Task and mesh total-memory properties count shared and output memory together. The memory tests allocate a 16 KiB shared array, synchronize the workgroup, and use atomics so the allocation participates in executed shader behavior.

## Registration Hierarchy

```text
mesh_shader.nv.property
├── max_draw_mesh_tasks_count_with_task
├── max_draw_mesh_tasks_count_with_mesh
├── max_task_work_group_invocations
├── max_task_work_group_size
├── max_task_output_count
├── max_mesh_work_group_invocations
├── max_mesh_work_group_size
├── max_task_total_memory_size
└── max_mesh_total_memory_size
```

[`createTests()`](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55-L84) attaches the `nv` branch below `mesh_shader` and adds the property family through `createMeshShaderPropertyTests()`. That factory creates the `property` group and its nine direct leaves in [`vktMeshShaderPropertyTests.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669-L685). The exact full paths appear in the default mustpass file at [`mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L27949-L27957).

## Parameter Dimensions and Observed Values

The limits below are the required minima from the Vulkan limits table and the constants used by the CTS source. The test does not allocate or dispatch the implementation's advertised maximum when that maximum is larger.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw path at `maxDrawMeshTasksCount = 65535` | `max_draw_mesh_tasks_count_with_task`, `max_draw_mesh_tasks_count_with_mesh` | Dispatches 65,535 workgroups and selects whether the task or mesh stage writes one indexed result per workgroup. | [`MaxDrawMeshTasksCountCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L236-L307) |
| Task workgroup invocation limit | `max_task_work_group_invocations`; minimum `32` | Compiles a task shader with `local_size_x = 32`, and each local invocation writes its own index. | [`MaxTaskWorkGroupInvocationsCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L309-L359) |
| Task workgroup size components | `max_task_work_group_size`; minimum `(32, 1, 1)` | Checks the three advertised X, Y, and Z components. Runtime behavior reuses the task invocation case at local size `(32, 1, 1)`. | [`MaxTaskWorkGroupSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L361-L387) |
| Task output count | `max_task_output_count`; minimum `65535` | One task workgroup writes `gl_TaskCountNV = 65535`; the emitted mesh workgroups write their X workgroup IDs. | [`MaxTaskOutputCountCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L389-L437) |
| Mesh workgroup invocation limit | `max_mesh_work_group_invocations`; minimum `32` | Compiles a mesh shader with `local_size_x = 32`, and each local invocation writes its own index. | [`MaxMeshWorkGroupInvocationsCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L439-L484) |
| Mesh workgroup size components | `max_mesh_work_group_size`; minimum `(32, 1, 1)` | Checks the three advertised X, Y, and Z components. Runtime behavior reuses the mesh invocation case at local size `(32, 1, 1)`. | [`MaxMeshWorkGroupSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L486-L512) |
| Task total memory | `max_task_total_memory_size`; minimum `16384` bytes | Declares `4096` shared `uint` elements in the task shader, for 16 KiB, and executes the shared-memory check with 32 invocations. | [`MaxTaskTotalMemorySizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L557-L612) |
| Mesh total memory | `max_mesh_total_memory_size`; minimum `16384` bytes | Declares the same 16 KiB shared array in the mesh shader and executes it with 32 invocations. | [`MaxMeshTotalMemorySizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L614-L665) |

The Vulkan specification defines the property meanings in [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L2248-L2323) and records the NV minima in the limit table at [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L6858-L6868).

## Behavior Parameters

The primary behavioral axis is the direct test case leaf. Each leaf chooses a property, its stage, and the shader operation used to prove that the required minimum is usable.

### `max_draw_mesh_tasks_count_with_task` | task-stage writes for 65,535 draws

The support check requires both task and mesh shaders and rejects `maxDrawMeshTasksCount < 65535`. The command launches 65,535 workgroups. Each task workgroup writes `gl_WorkGroupID.x` into the matching storage-buffer element, while the task shader emits no mesh workgroups.

### `max_draw_mesh_tasks_count_with_mesh` | mesh-stage writes for 65,535 draws

This leaf requires only the mesh feature after the extension check. The same 65,535-workgroup command runs without a task stage, and each mesh workgroup writes its X ID into the corresponding element.

### `max_task_work_group_invocations` | 32 task invocations

The case rejects `maxTaskWorkGroupInvocations < 32`, then runs one task workgroup with `local_size_x = 32`. Invocation `i` writes `i` to output element `i`. The empty mesh shader exists to complete the graphics pipeline.

### `max_task_work_group_size` | task local size `(32, 1, 1)`

This leaf checks `maxTaskWorkGroupSize[0] >= 32`, `[1] >= 1`, and `[2] >= 1`. It inherits the 32-invocation task shader and runtime path from `max_task_work_group_invocations`, so the property check and shader-backed validation cover the required X dimension while confirming the required Y and Z values in the query.

### `max_task_output_count` | 65,535 emitted mesh workgroups

The task shader executes once and assigns `65535` to `gl_TaskCountNV`. The mesh stage therefore receives 65,535 workgroups and writes each `gl_WorkGroupID.x` to the corresponding output element. The specification's task-output rule is described in [`mesh.adoc`](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L33-L41).

### `max_mesh_work_group_invocations` | 32 mesh invocations

The case rejects `maxMeshWorkGroupInvocations < 32`, then directly launches one mesh workgroup with `local_size_x = 32`. Each invocation writes its local X ID to the matching output slot.

### `max_mesh_work_group_size` | mesh local size `(32, 1, 1)`

This leaf checks all three components of `maxMeshWorkGroupSize` against `(32, 1, 1)`. It inherits the same 32-invocation mesh shader and result path as `max_mesh_work_group_invocations`.

### `max_task_total_memory_size` | 16 KiB task shared memory

The task shader declares a 4,096-element shared `uint` array. Invocation zero clears it; all 32 invocations atomically increment every element between barriers; each invocation verifies that every element reached 32. A failed shader-side check writes the sentinel value `gl_WorkGroupSize.x`, which cannot equal any valid local invocation index from 0 through 31.

### `max_mesh_total_memory_size` | 16 KiB mesh shared memory

This leaf applies the same clear, barrier, atomic-add, and verify sequence to a 16 KiB shared array in the mesh stage. It requires no task shader and directly launches one 32-invocation mesh workgroup.

## Shader Analysis

Generated shaders are part of the validation path, but the nine cases use short boundary probes rather than a complex shader algorithm. One representative mesh shader captures the shared invocation mechanism used by both `max_mesh_work_group_invocations` and `max_mesh_work_group_size`; the parameter variation table covers the distinct task, draw-count, output-count, and shared-memory forms.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.nv.property.max_mesh_work_group_invocations
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `max_mesh_work_group_invocations` | Selects the mesh-stage invocation limit and its shader generator. |
| `local_size_x = 32` | Uses the Vulkan-required minimum number of mesh invocations in one workgroup. |
| One draw task | `vkCmdDrawMeshTasksNV(..., 1, 0)` launches one mesh workgroup because the pipeline has no task stage. |

#### Purpose

The shader proves that a mesh workgroup at the required 32-invocation minimum can execute all local invocations and write a distinct host-visible result for each one.

#### Structural Design

| Phase | Operation | Observable result |
|-------|-----------|-------------------|
| Workgroup shape | Declare `local_size_x = 32`, with implicit Y and Z sizes of one. | The workgroup contains local X invocation IDs 0 through 31. |
| Rasterization suppression | Set `gl_PrimitiveCountNV` to zero. | The test needs no framebuffer output or fragment shader. |
| Result write | Store each `gl_LocalInvocationID.x` at the same storage-buffer index. | A correct run produces `values[i] == i` for all 32 entries. |

#### Shader Code

```glsl
#version 460
#extension GL_NV_mesh_shader : enable

/// Exercise the required minimum of 32 mesh invocations in one workgroup.
layout (local_size_x=32) in;
layout (triangles) out;
layout (max_vertices=3, max_primitives=1) out;

/// Host-visible result array at descriptor set 0, binding 0.
layout (set=0, binding=0) buffer OutputBlock { uint values[]; } ov;

void main ()
{
    /// No primitives are needed; validation uses only the storage buffer.
    gl_PrimitiveCountNV = 0u;
    /// Each invocation proves execution by writing its own local index.
    ov.values[gl_LocalInvocationID.x] = gl_LocalInvocationID.x;
}
```

#### Additional Info

- The source collection supplies no explicit shader build options, so CTS uses its baseline SPIR-V target, SPIR-V 1.0.
- The shared runtime creates an empty render pass and framebuffer and omits a fragment shader because no primitives reach rasterization.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Mesh workgroup-size property | `max_mesh_work_group_size` reuses this exact generated shader and changes the queried property to the three-component size limit. | [`MaxMeshWorkGroupSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L486-L512) |
| Task invocation or size property | Moves the indexed write to a task shader with `local_size_x = 32`; the mesh shader becomes empty. | [`MaxTaskWorkGroupInvocationsCase::initPrograms()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L344-L359) |
| Draw task count | Uses local size one and indexes the output with `gl_WorkGroupID.x`; either the task or mesh stage performs the write. | [`MaxDrawMeshTasksCountCase::initPrograms()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L282-L307) |
| Task output count | A single task invocation writes `gl_TaskCountNV = 65535`, and the resulting mesh workgroups write their workgroup IDs. | [`MaxTaskOutputCountCase::initPrograms()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L424-L437) |
| Total memory | Adds a 4,096-element shared `uint` array and a 32-invocation synchronized atomic check in the selected task or mesh stage. | [`getSharedArrayDecl()` and `getSharedMemoryBody()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L514-L555) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 29
; Schema: 0
               OpCapability MeshShadingNV
               OpExtension "SPV_NV_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshNV %main "main" %gl_PrimitiveCountNV %gl_LocalInvocationID
               OpExecutionMode %main LocalSize 32 1 1
               OpExecutionMode %main OutputVertices 3
               OpExecutionMode %main OutputPrimitivesEXT 1
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_NV_mesh_shader"
               OpName %main "main"
               OpName %gl_PrimitiveCountNV "gl_PrimitiveCountNV"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "values"
               OpName %ov "ov"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpDecorate %gl_PrimitiveCountNV BuiltIn PrimitiveCountNV
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %ov Binding 0
               OpDecorate %ov DescriptorSet 0
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_PrimitiveCountNV = OpVariable %_ptr_Output_uint Output
     %uint_0 = OpConstant %uint 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
         %ov = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
    %uint_32 = OpConstant %uint 32
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_32 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %gl_PrimitiveCountNV %uint_0
         %20 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %21 = OpLoad %uint %20
         %22 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %23 = OpLoad %uint %22
         %25 = OpAccessChain %_ptr_Uniform_uint %ov %int_0 %21
               OpStore %25 %23
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Every leaf calls `genericCheckSupport()`. It requires `VK_NV_mesh_shader`, always requires the mesh shader feature, requires the task shader feature for task-stage cases, and requires the core `vertexPipelineStoresAndAtomics` feature because shaders write the storage buffer.
- Each leaf then reads `context.getMeshShaderProperties()` and fails before instance creation if its advertised property is below the CTS constant. This is a conformance failure, not a support skip, because an implementation exposing the extension must report at least the specified minimum.
- The instance allocates a host-visible storage buffer and initializes every word to `0xFFFFFFFF`. It exposes the buffer at set 0, binding 0 to the active task and mesh stages.
- The test builds a graphics pipeline with the generated task shader when needed, a mesh shader in every case, no fragment shader, and an empty render pass and framebuffer.
- A primary command buffer binds the descriptor set and pipeline, calls `vkCmdDrawMeshTasksNV` with either one or 65,535 tasks, and inserts a shader-write to host-read memory barrier. Submission waits for completion.
- After invalidating the allocation, the host scans every output element and requires `buffer[i] == i`. An untouched initial value, the shared-memory sentinel `32`, a duplicate, or any wrong index fails the case at the first mismatching position.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `max_draw_mesh_tasks_count_with_task` | The reported draw limit is below 65,535, or the implementation mishandles a 65,535-workgroup task-stage draw or its shader storage writes. |
| `max_draw_mesh_tasks_count_with_mesh` | The reported draw limit is below 65,535, or the implementation mishandles the same boundary draw without a task stage. |
| `max_task_work_group_invocations` | The task invocation limit is below 32, or a 32-invocation task workgroup does not execute and index all invocations correctly. |
| `max_task_work_group_size` | One advertised task size component is below `(32, 1, 1)`, or the inherited 32-invocation task execution fails. |
| `max_task_output_count` | The task output limit is below 65,535, or `gl_TaskCountNV = 65535` does not produce the expected mesh workgroups and IDs. |
| `max_mesh_work_group_invocations` | The mesh invocation limit is below 32, or a 32-invocation mesh workgroup does not execute and index all invocations correctly. |
| `max_mesh_work_group_size` | One advertised mesh size component is below `(32, 1, 1)`, or the inherited 32-invocation mesh execution fails. |
| `max_task_total_memory_size` | The task total-memory limit is below 16 KiB, or executed task-stage shared memory, barriers, or atomics produce a bad result. |
| `max_mesh_total_memory_size` | The mesh total-memory limit is below 16 KiB, or executed mesh-stage shared memory, barriers, or atomics produce a bad result. |

All shader-backed rows also share the storage-buffer, descriptor, pipeline, synchronization, and host-readback path. A failure there can affect more than one leaf.

### Cause Analysis

#### Advertised property below the required NV minimum

**Possible failure symptoms:** The support check reports a property-specific message such as `maxTaskOutputCount property below the minimum limit` before it creates the test instance or submits work.

**Possible implementation causes:** The physical-device property query returned a `VkPhysicalDeviceMeshShaderPropertiesNV` member below the conformance minimum in the specification's limits table. Investigation should confirm both the value supplied through `vkGetPhysicalDeviceProperties2` and the CTS context's property-chain setup.

#### Boundary draw or task-output expansion failure

**Possible failure symptoms:** A 65,535-element output buffer contains an untouched `0xFFFFFFFF`, a duplicate, or another value that differs from its index. The failure identifies the first wrong buffer position.

**Possible implementation causes:** `vkCmdDrawMeshTasksNV` did not launch every required workgroup, task-stage execution lost a workgroup ID, or `gl_TaskCountNV = 65535` did not emit the specified number of mesh workgroups. The command's `taskCount` must not exceed `maxDrawMeshTasksCount`, and `gl_TaskCountNV` must not exceed `maxTaskOutputCount`; these tests use the required minima at those boundaries.

#### Task or mesh local-workgroup execution failure

**Possible failure symptoms:** One of the 32 result words is untouched or differs from its local invocation index.

**Possible implementation causes:** The shader compiler or execution implementation mishandled `LocalSize 32 1 1`, local invocation IDs, or storage-buffer writes in the selected task or mesh stage. For the size leaves, a failure may instead occur before execution because one X, Y, or Z property component is too small.

#### Total-memory shared-state failure

**Possible failure symptoms:** One or more output words equal the sentinel `32` or another unexpected value instead of their invocation index.

**Possible implementation causes:** The stage could not provide the required 16 KiB combined memory budget, or the executed shader produced incorrect shared-array initialization, workgroup barrier behavior, shared-memory visibility, or atomic increments. The same result can also follow from incorrect compilation of the generated shared-memory shader, so the failing stage and shader binary need source-level investigation.

#### Common result-transport failure

**Possible failure symptoms:** Several otherwise different leaves report untouched or incorrect storage-buffer values, often from the first element.

**Possible implementation causes:** Descriptor binding, task/mesh-stage storage writes, the shader-to-host memory dependency, host-visible memory invalidation, or pipeline execution failed in the shared runtime path. Cross-case results distinguish this common path from a single property-specific mechanism.

## Case Pruning

### Requirement-based pruning

- If `VK_NV_mesh_shader` is unavailable, the shared support helper marks the case unsupported.
- Every leaf requires the `meshShader` feature. Task-stage leaves also require `taskShader`; mesh-only leaves do not.
- Every leaf requires the core `vertexPipelineStoresAndAtomics` feature because the task or mesh shader writes a storage buffer.
- These are support gates. A queried property below its Vulkan-required minimum calls `TCU_FAIL` and counts as a conformance failure rather than pruning the case.

### Design-based pruning

- The family covers eight distinct NV property dimensions with nine leaves. `maxDrawMeshTasksCount` has two leaves because the boundary command must work both with and without a task stage.
- `maxTaskWorkGroupSize` and `maxMeshWorkGroupSize` check all three reported components but execute only the required `(32, 1, 1)` shape. The NV minima for Y and Z are one, so no separate Y- or Z-heavy leaf is generated.
- Invocation and size leaves share shader-backed runtime behavior at 32 invocations. They differ in the property query that must satisfy the minimum.
- Memory leaves use exactly 16 KiB and 32 invocations. Larger advertised values are outside this family's conformance-minimum probe, so the source does not scale allocations to each device's maximum.

## Key Takeaways

- The nine mustpass leaves cover every property check registered by the NV `property` factory, including separate task and mesh paths for the 65,535 draw boundary.
- Passing requires both truthful property reporting and successful execution at the required minimum. A numeric query check alone is insufficient for these cases.
- All successful executions reduce to one host rule: output element `i` must contain `i`. The memory cases use `32` as a shader-side failure sentinel.
- Support skips apply only to the extension and required features. A property below the specification minimum is a test failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| NV property registration | [`createMeshShaderPropertyTests()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669-L685) | Creates the `property` family and all nine direct leaves. |
| Property support gates | [`genericCheckSupport()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L94-L104), [`checkTaskMeshShaderSupportNV()`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires the extension, stage features, and shader storage-write feature. |
| Shared runtime and host validation | [`MeshShaderPropertyInstance::iterate()`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L130-L234) | Builds resources and the pipeline, issues the draw, synchronizes, and checks `buffer[i] == i`. |
| Draw, invocation, size, and output cases | [`vktMeshShaderPropertyTests.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L236-L512) | Implements the first seven leaves and their generated shaders. |
| Shared-memory generator and memory cases | [`vktMeshShaderPropertyTests.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L514-L665) | Implements the 16 KiB task and mesh memory probes. |
| NV property definitions | [`VkPhysicalDeviceMeshShaderPropertiesNV`](../../../../vulkan-docs/src/chapters/limits.adoc#L2248-L2323) | Defines each queried property's meaning and property-query mechanism. |
| NV required minima | [`Vulkan limit requirements`](../../../../vulkan-docs/src/chapters/limits.adoc#L6858-L6868) | Gives the required values used by the test constants. |
| Mesh task generation | [`Task Shader Output`](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L33-L64) | Defines `gl_TaskCountNV` and its relation to `maxTaskOutputCount`. |
| Default mustpass paths | [`mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L27949-L27957) | Lists the exact nine conformance paths. |
