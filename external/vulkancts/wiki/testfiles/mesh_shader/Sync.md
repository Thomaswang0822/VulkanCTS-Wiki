## Overview

**Core question:** Does the selected Vulkan memory dependency deliver one known value from the source stage to the destination stage in an NV mesh-shader pipeline?

- This page covers the `mesh_shader.nv.synchronization` test family implemented by [createMeshShaderSyncTests](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332-L1453).
- The factory combines 11 explicit stage pairs, four resource kinds, two registered barrier forms, and legal write/read access pairs. Each leaf carries a distinct `uint32_t` test value.
- The source stage writes or supplies the value, the destination stage reads it, and the test observes the value in a host-visible buffer or a color attachment copied into one.
- The current `vk-default` mesh-shader mustpass contains 50 NV synchronization cases. The exact entries are in [mesh-shader.txt](../../../mustpass/main/vk-default/mesh-shader.txt#L27964-L28013).

## Background Knowledge

- Vulkan execution order does not by itself make a write visible to a later access. A memory dependency supplies execution ordering plus availability and visibility operations for source and destination access scopes. The Vulkan synchronization chapter defines this model in [Execution and Memory Dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies).
- The implementation's stage vocabulary is `host`, `transfer`, `task`, `mesh`, and `frag`. The last three are shader stages in the generated graphics pipeline; task output reaches mesh through the NV task/mesh interface.
- A global memory barrier covers arbitrary memory accesses. A buffer or image barrier additionally names the affected resource range or image subresource and can perform an image layout transition. The relevant API rules are in [Pipeline Barriers](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-barriers).

## Registration Hierarchy

```text
mesh_shader.nv.synchronization
├── host_to_task
├── host_to_mesh
├── transfer_to_task
├── transfer_to_mesh
├── task_to_mesh
├── task_to_frag
├── task_to_transfer
├── task_to_host
├── mesh_to_frag
├── mesh_to_transfer
└── mesh_to_host
```

The direct children are the explicit stage-pair test families. Their resource, barrier, and access leaves are expanded in the parameter section and in the mustpass file.

## Parameter Dimensions and Observed Values

The factory starts with a matrix, then removes combinations that the selected stages, resource, access type, or barrier position cannot support. The registered names below are exact.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Source and destination stages | `host_to_task`, `host_to_mesh`, `transfer_to_task`, `transfer_to_mesh`, `task_to_mesh`, `task_to_frag`, `task_to_transfer`, `task_to_host`, `mesh_to_frag`, `mesh_to_transfer`, `mesh_to_host` | Selects the producer and consumer access, pipeline stage masks, generated shader roles, and result location. | [stage combinations](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1336-L1345) |
| Resource | `uniform_buffer`, `storage_buffer`, `storage_image`, `sampled_image` | Selects the descriptor type, GLSL declaration, buffer or image setup, and read operation. | [resource types](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1347-L1356), [resource declarations](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L444-L471) |
| Barrier | `memory_barrier`, `specific_barrier` | Selects a global `VkMemoryBarrier`, or a `VkBufferMemoryBarrier`/`VkImageMemoryBarrier` for the resource. Shader-to-shader cases retain only the `memory_barrier` leaf: the generic barrier is recorded between two draws inside the render pass, alongside the render-pass self-dependency. | [barrier types and pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1358-L1365), [render-pass dependency](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L752-L766), [in-render-pass barrier](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1150-L1173) |
| Write access | `host_write`, `transfer_write`, `shader_write` | Selects the source access mask: `VK_ACCESS_HOST_WRITE_BIT`, `VK_ACCESS_TRANSFER_WRITE_BIT`, or `VK_ACCESS_SHADER_WRITE_BIT`. | [write access](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L171-L197) |
| Read access | `host_read`, `transfer_read`, `shader_read`, `uniform_read` | Selects the destination access mask: host, transfer, shader, or uniform read. | [read access](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L199-L228) |
| Access leaf | Examples include `host_write_uniform_read`, `host_write_shader_read`, `transfer_write_uniform_read`, `transfer_write_shader_read`, `shader_write_shader_read`, `shader_write_transfer_read`, and `shader_write_host_read` | Combines the selected source and destination access names into the final executable leaf. | [leaf construction](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1417-L1442) |
| Test value | Per-case values beginning at `1628510124u` | Gives the destination a value that the host can distinguish from an uninitialized or stale result. | [test-value seed](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1388-L1388), [case construction](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1429-L1439) |

The exact default mustpass distribution is 50 cases:

| Stage-pair family | Cases | Resource distribution |
|-------------------|------:|-----------------------|
| `host_to_mesh`, `host_to_task` | 12 | Each has 2 `storage_buffer` and 4 `uniform_buffer` cases. |
| `transfer_to_mesh`, `transfer_to_task` | 20 | Each has 2 `storage_buffer`, 2 `storage_image`, 2 `sampled_image`, and 4 `uniform_buffer` cases. |
| `task_to_mesh`, `task_to_frag` | 4 | Each has one `storage_buffer` and one `storage_image` case. |
| `task_to_transfer` | 4 | Two `storage_buffer` and two `storage_image` cases. |
| `task_to_host` | 2 | Two `storage_buffer` cases. |
| `mesh_to_frag` | 2 | One `storage_buffer` and one `storage_image` case. |
| `mesh_to_transfer` | 4 | Two `storage_buffer` and two `storage_image` cases. |
| `mesh_to_host` | 2 | Two `storage_buffer` cases. |

## Behavior Parameters

The primary behavioral axis is the complete synchronization scenario, represented by the registered stage-pair family. It changes which operation produces the value, which operation consumes it, where the dependency is recorded, and which output is checked. Resource, barrier, and access leaves refine that scenario.

### `host_to_task` and `host_to_mesh` | Host-to-shader visibility

The host writes a uniform or storage buffer, flushes the allocation, and the selected shader reads it. The generated mesh/task path forwards the read value through `TaskData` or `primitiveValue`; the color attachment then provides the host-visible oracle.

### `transfer_to_task` and `transfer_to_mesh` | Transfer-to-shader visibility

The host writes an auxiliary host-coherent buffer. A transfer copies the value into the selected buffer or image, then the task or mesh shader reads it. Sampled-image cases use a sampler, while buffer and storage-image cases use their corresponding shader read operations.

### `task_to_mesh` | Task-to-mesh visibility

The task shader writes a storage buffer or storage image, and the mesh shader reads it. Because both accesses are shader accesses, the render pass carries a self-dependency, and the command buffer records the registered generic memory barrier between two draws. The factory registers only `memory_barrier` leaves for this family in the current mustpass.

### `task_to_frag` and `mesh_to_frag` | Shader-to-fragment visibility

The task or mesh shader writes a storage buffer or storage image. The fragment shader reads it and writes the value to `outColor`. The host checks the copied color attachment.

### `task_to_transfer` and `mesh_to_transfer` | Shader-to-transfer visibility

The task or mesh shader writes a storage buffer or storage image. A later copy reads that resource into an auxiliary host-coherent buffer, which the host checks after a transfer-to-host barrier.

### `task_to_host` and `mesh_to_host` | Shader-to-host visibility

The task or mesh shader writes a storage buffer. The host reads the resource buffer directly after submission and invalidates its allocation before comparing the value.

### Barrier and access refinements

`memory_barrier` uses the selected stage and access masks in a global memory barrier. `specific_barrier` uses a buffer barrier for buffers or an image barrier plus a layout transition for images. The access leaf must agree with the endpoint: host uses host access, transfer uses transfer access, shader stages use `shader_read` or `uniform_read`, and only a uniform buffer accepts `uniform_read`.

## Shader Analysis

The selected host-to-mesh uniform-buffer case shows the common shader-side observation path. The synchronization behavior changes the resource declaration and read operation across variants, but the mesh shader still emits one triangle and forwards the observed value as a flat per-primitive output. One walkthrough is sufficient because the transfer and task variants change the producer or resource operation rather than requiring a separate mesh-output algorithm.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.nv.synchronization.host_to_mesh.uniform_buffer.memory_barrier.host_write_shader_read
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `host_to_mesh` | The host supplies the value and the mesh shader consumes it. |
| `uniform_buffer` | The mesh shader reads `ub.value` through a descriptor at set 0, binding 0. |
| `memory_barrier` | The command buffer uses a global memory barrier from host writes to mesh shader reads. |
| `host_write_shader_read` | The barrier uses `VK_ACCESS_HOST_WRITE_BIT` as the source access and `VK_ACCESS_SHADER_READ_BIT` as the destination access. |
| `readVal = 1u` | The generated mesh shader executes the resource read and stores it in `primitiveValue[0]`. |

#### Purpose

The mesh shader reads the value written by the host and passes it to the fragment stage as a flat per-primitive value. The fragment output lets the host determine whether the mesh-stage read saw `1628510124u`.

#### Structural Design

```mermaid
flowchart TD
    A[Host writes uniform buffer] --> B[Global host-to-mesh memory barrier]
    B --> C[Mesh shader reads ub.value]
    C --> D[Mesh shader stores primitiveValue[0]]
    D --> E[Fragment shader writes uvec4 color]
    E --> F[Host copies color and compares uint]
```

#### Shader Code

The source-generated mesh shader for this path is:

```glsl
#version 450
#extension GL_NV_mesh_shader : enable

layout(local_size_x=1) in;
layout(triangles) out;
layout(max_vertices=3, max_primitives=1) out;

/// The flat per-primitive value carries the resource read to the fragment shader.
layout (location=0) out perprimitiveNV uint primitiveValue[];

/// Binding 0 is the host-written uniform buffer used by this representative case.
layout (set=0, binding=0) uniform UniformBuffer { uint value; } ub;
/// Push constants select whether this generated stage writes or reads the resource.
layout (push_constant, std430) uniform PushConstantBlock {
    uint writeVal;
    uint readVal;
} pc;

void main ()
{
    /// The case enables the resource read, then emits one triangle covering the 1x1 color attachment.
    gl_PrimitiveCountNV = 1u;
    if (pc.readVal > 0u) { primitiveValue[0] = ub.value; }

    gl_MeshVerticesNV[0].gl_Position = vec4(-1.0, -1.0, 0.0, 1.0);
    gl_MeshVerticesNV[1].gl_Position = vec4(-1.0,  3.0, 0.0, 1.0);
    gl_MeshVerticesNV[2].gl_Position = vec4( 3.0, -1.0, 0.0, 1.0);
    gl_PrimitiveIndicesNV[0] = 0;
    gl_PrimitiveIndicesNV[1] = 1;
    gl_PrimitiveIndicesNV[2] = 2;
}
```

#### Additional Info

- The host creates a 1x1 `VK_FORMAT_R32_UINT` color attachment for the output path. The mesh shader's triangle covers it, so the copied pixel contains the per-primitive value.
- The generated fragment shader receives `primitiveValue` at location 0 and writes `uvec4(primitiveValue, 0, 0, 0)`. It does not read the synchronization resource for this representative path.
- The source uses the push-constant `writeVal` and `readVal` switches to share shader generators between producer and consumer cases. This case enables the read branch only.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Stage pair | A task endpoint adds a task shader and `TaskData`; a transfer or host endpoint changes the operation outside the mesh shader. | [shader generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L620-L698) |
| Resource | `uniform_buffer` emits `ub.value`; storage buffers, storage images, and sampled images emit their corresponding read expressions. | [resource read statements](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L491-L515) |
| Read access | `uniform_read` is the uniform-buffer access variant; `shader_read` uses the same generated load but selects a different barrier access mask. | [read-access mapping](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L199-L228) |
| Barrier | The global barrier changes to a buffer or image barrier for `specific_barrier`; shader source stays the same for this host-to-mesh case. | [barrier recording](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1093-L1127) |

#### SPIR-V

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
; Bound: 66
; Schema: 0
               OpCapability MeshShadingNV
               OpExtension "SPV_NV_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshNV %main "main" %gl_PrimitiveCountNV %primitiveValue %gl_MeshVerticesNV %gl_PrimitiveIndicesNV
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main OutputVertices 3
               OpExecutionMode %main OutputPrimitivesEXT 1
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 450
               OpSourceExtension "GL_NV_mesh_shader"
               OpName %main "main"
               OpName %gl_PrimitiveCountNV "gl_PrimitiveCountNV"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "writeVal"
               OpMemberName %PushConstantBlock 1 "readVal"
               OpName %pc "pc"
               OpName %primitiveValue "primitiveValue"
               OpName %UniformBuffer "UniformBuffer"
               OpMemberName %UniformBuffer 0 "value"
               OpName %ub "ub"
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
               OpDecorate %gl_PrimitiveCountNV BuiltIn PrimitiveCountNV
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpDecorate %primitiveValue Location 0
               OpDecorate %primitiveValue PerPrimitiveEXT
               OpDecorate %UniformBuffer Block
               OpMemberDecorate %UniformBuffer 0 Offset 0
               OpDecorate %ub Binding 0
               OpDecorate %ub DescriptorSet 0
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
       %uint = OpTypeInt 32 0
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_PrimitiveCountNV = OpVariable %_ptr_Output_uint Output
     %uint_1 = OpConstant %uint 1
%PushConstantBlock = OpTypeStruct %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
%_arr_uint_uint_1 = OpTypeArray %uint %uint_1
%_ptr_Output__arr_uint_uint_1 = OpTypePointer Output %_arr_uint_uint_1
%primitiveValue = OpVariable %_ptr_Output__arr_uint_uint_1 Output
      %int_0 = OpConstant %int 0
%UniformBuffer = OpTypeStruct %uint
%_ptr_Uniform_UniformBuffer = OpTypePointer Uniform %UniformBuffer
         %ub = OpVariable %_ptr_Uniform_UniformBuffer Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_arr__arr_float_uint_1_uint_4 = OpTypeArray %_arr_float_uint_1 %uint_4
%gl_MeshPerVertexNV = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1 %_arr_v4float_uint_4 %_arr__arr_float_uint_1_uint_4 %_arr__arr_float_uint_1_uint_4
     %uint_3 = OpConstant %uint 3
%_arr_gl_MeshPerVertexNV_uint_3 = OpTypeArray %gl_MeshPerVertexNV %uint_3
%_ptr_Output__arr_gl_MeshPerVertexNV_uint_3 = OpTypePointer Output %_arr_gl_MeshPerVertexNV_uint_3
%gl_MeshVerticesNV = OpVariable %_ptr_Output__arr_gl_MeshPerVertexNV_uint_3 Output
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %48 = OpConstantComposite %v4float %float_n1 %float_n1 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %float_3 = OpConstant %float 3
         %52 = OpConstantComposite %v4float %float_n1 %float_3 %float_0 %float_1
      %int_2 = OpConstant %int 2
         %55 = OpConstantComposite %v4float %float_3 %float_n1 %float_0 %float_1
%_arr_uint_uint_3 = OpTypeArray %uint %uint_3
%_ptr_Output__arr_uint_uint_3 = OpTypePointer Output %_arr_uint_uint_3
%gl_PrimitiveIndicesNV = OpVariable %_ptr_Output__arr_uint_uint_3 Output
     %uint_2 = OpConstant %uint 2
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %gl_PrimitiveCountNV %uint_1
         %16 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %17 = OpLoad %uint %16
         %20 = OpUGreaterThan %bool %17 %uint_0
               OpSelectionMerge %22 None
               OpBranchConditional %20 %21 %22
         %21 = OpLabel
         %31 = OpAccessChain %_ptr_Uniform_uint %ub %int_0
         %32 = OpLoad %uint %31
         %33 = OpAccessChain %_ptr_Output_uint %primitiveValue %int_0
               OpStore %33 %32
               OpBranch %22
         %22 = OpLabel
         %50 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_0 %int_0
               OpStore %50 %48
         %53 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_1 %int_0
               OpStore %53 %52
         %56 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_2 %int_0
               OpStore %56 %55
         %60 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_0
               OpStore %60 %uint_0
         %61 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_1
               OpStore %61 %uint_1
         %63 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_2
               OpStore %63 %uint_2
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- The case creates a 1x1 `VK_FORMAT_R32_UINT` color image for shader-visible results. Buffer resources are four-byte host-visible buffers. Image resources receive transfer source/destination usage plus storage or sampled usage as selected.
- The descriptor at set 0, binding 0 names the selected resource. The pipeline layout also exposes the two-word push-constant block to every shader stage that can access the resource.
- For a host source, the test writes the value directly into the resource buffer and flushes the allocation. For a transfer source, it writes the value into an auxiliary host-coherent buffer, records a host-to-transfer barrier, and copies into the resource.
- For a shader source, the test transitions an image to `GENERAL` when needed, then runs the generated task/mesh/fragment pipeline. Shader-to-shader pairs declare a render-pass self-dependency and use two mesh draws: the first enables only `writeVal`, the registered generic memory barrier separates the draws, and the second enables only `readVal`.
- For a shader destination, the test uses the selected global or resource-specific barrier before the pipeline for non-shader-source cases. When both endpoints are shader stages, the selected generic barrier is instead recorded between the two draws inside the render pass; specific resource barriers are pruned there. For a transfer destination, it copies the resource into the auxiliary host-coherent buffer. For a host destination, the resource buffer remains the final result.
- Shader destinations other than transfer or host write the value to the color attachment. The test transitions that attachment for transfer, copies its pixel into a host-coherent verification buffer, ends the command buffer, submits it, and waits for completion.
- The host compares the resulting `uint32_t` with the case's `testValue`. The test returns `Pass` only when the selected output equals that value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host_to_task`, `host_to_mesh` | Host-domain write not made visible to the selected shader access; incorrect host-to-device stage or access scope; resource setup problem. |
| `transfer_to_task`, `transfer_to_mesh` | Transfer write not made visible to shader or uniform access; incorrect image layout or transfer barrier; copy setup problem. |
| `task_to_mesh`, `task_to_frag` | Shader-to-shader dependency or render-pass subpass dependency does not make the task write visible to the consumer. |
| `task_to_transfer`, `mesh_to_transfer` | Shader write is not visible to the copy, or the image/buffer copy and transfer-to-host path is incorrect. |
| `task_to_host`, `mesh_to_host` | Shader write is not visible to the host, or host invalidation/readback is incorrect. |
| `mesh_to_frag` | Mesh write is not visible to the fragment read, or the fragment/color readback path is incorrect. |

### Cause Analysis

#### Host-to-shader visibility or resource setup

**Possible failure symptoms:** A `host_to_task` or `host_to_mesh` case reads a value different from its `testValue`, so the color verification buffer contains an unexpected value.

**Possible implementation causes:** The host write, flush, stage mask, access mask, or resource binding may not establish the required host-to-device memory dependency. The source also allows a host-visible resource buffer only for the legal host endpoints, so incorrect resource creation or readback could produce the same symptom. The synchronization specification states that host writes to non-coherent mapped memory require a flush before device access.

#### Transfer visibility, copy, or image layout

**Possible failure symptoms:** A transfer-to-task or transfer-to-mesh shader observes the wrong value, or a task/mesh-to-transfer case copies the wrong value into the auxiliary host-coherent buffer.

**Possible implementation causes:** The transfer access may not be included in the dependency, or an image may use a layout that does not match the transfer operation. The copy region, image layout transition, or transfer-to-host barrier can also expose a wrong value even when the main dependency is correct. These possibilities follow from the source's separate copy, image-barrier, and verification steps.

#### Task-to-mesh dependency

**Possible failure symptoms:** In `task_to_mesh`, the mesh shader's `primitiveValue[0]` does not equal the task shader's `testValue`, and the color buffer check fails.

**Possible implementation causes:** The render-pass subpass dependency may not cover the selected task write and mesh read access scopes. The test deliberately expresses this shader-to-shader dependency in the render pass and uses two draws so the write and read are separate operations.

#### Shader-to-fragment dependency

**Possible failure symptoms:** `task_to_frag` or `mesh_to_frag` produces a color pixel whose first component differs from the written value.

**Possible implementation causes:** The shader write may not become visible to the fragment read, or the per-primitive interface may not carry the value as intended. The later color-attachment transition and copy can also affect the observed result. The page does not assign the failure to a particular implementation layer without further investigation.

#### Shader-to-transfer or shader-to-host visibility

**Possible failure symptoms:** A transfer destination buffer or host destination resource buffer contains a value other than `testValue` after the queue submission completes.

**Possible implementation causes:** The shader-to-transfer or shader-to-host dependency, access mask, stage mask, or host invalidation path may not match the actual operation. The source uses a transfer-to-host barrier for the auxiliary result and invalidates the resource allocation for direct host checks, so either path can account for the symptom.

#### Color attachment copyback

**Possible failure symptoms:** A shader-destination case fails at `Unexpected value in color verification buffer`, even though the resource read or write itself may have been correct.

**Possible implementation causes:** The color attachment barrier, layout transition, image-to-buffer copy, or host-coherent verification buffer setup may have produced the wrong observed pixel. The source's final color copyback is a separate observable path from the synchronization resource.

## Case Pruning

### Requirement-based pruning

- `checkTaskMeshShaderSupportNV` requires `VK_NV_mesh_shader` and a mesh shader feature. It additionally requires a task shader feature when the stage pair contains `task`.
- Cases with `shader_write` require the core `vertexPipelineStoresAndAtomics` feature because shader stages write storage buffers or storage images.
- `canWriteTo` removes host writes to images, shader writes to uniform or sampled images, and any other source/resource pairing that the generated operations cannot perform.
- `canReadFrom` removes host reads from images. `canReadResourceAsAccess` permits `uniform_read` only for `uniform_buffer`; `canWriteResourceAsAccess` removes shader writes to uniform buffers.
- `canWriteFromStageAsAccess` and `canReadFromStageAsAccess` require the access leaf to match the endpoint stage. A task, mesh, or fragment endpoint uses shader access, while host and transfer endpoints use their matching access type.
- When both endpoints are shader stages, a specific buffer or image barrier is not registered. The implementation declares a render-pass self-dependency and uses the generic memory barrier inside the render pass because Vulkan validity rules cited in the source prohibit the specific barrier forms at that location for the tested resources.

These removals mean that the omitted case is unsupported, invalid for the selected operation, or unavailable under the device feature requirements. A skipped test is not a synchronization failure.

### Design-based pruning

- The factory lists only stage pairs that include task or mesh and cover the intended host, transfer, task, mesh, and fragment dependency directions. It does not generate every ordered pair among all five stages.
- It uses one scalar value and a one-element resource or image observation. Larger resources would add setup without changing the dependency being tested.
- The shader-to-shader path uses a subpass dependency rather than registering `subpass_dependency` as a barrier leaf. The mustpass therefore records only `memory_barrier` for those stage pairs.
- The `vk-default` file records only leaves that survive all predicates. Its 50 NV cases are the observed pruned matrix, not the unfiltered product of all table values.

## Key Takeaways

- The page tests visibility of one known value across a selected stage pair, not just command submission order.
- The stage pair controls the producer, consumer, stage masks, shader generation, and final observation path.
- Resource and access predicates matter: a legal synchronization combination must also describe an operation that the endpoint can perform.
- Shader-to-shader cases put the dependency in a render pass and split the write and read into two draws; specific resource barriers are intentionally absent from those registered leaves.
- A failure is an unexpected value in a result buffer. It can indicate a dependency, resource/layout, shader interface, copyback, or host cache-management problem, so the failing path determines what to investigate.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Stage/resource/barrier/access definitions | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L57-L228) | Defines the exact matrix vocabulary and Vulkan flag mappings. |
| Combination legality and result routing | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L230-L365) | Explains supported endpoint/resource/access combinations and where results land. |
| Support gate and generated programs | [checkSupport and initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L610-L698) | Requires NV mesh/task support and emits task, mesh, and fragment shaders. |
| Render-pass dependency and helper barriers | [render pass and barriers](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L722-L795) | Shows subpass dependency construction and host/transfer synchronization. |
| Resource setup and command execution | [MeshShaderSyncInstance::iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L797-L1277) | Shows buffers, images, descriptors, layouts, draws, copies, submit, and wait. |
| Observable result checks | [result verification](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1279-L1327) | Shows each host-side comparison and failure message. |
| Registration and pruning | [createMeshShaderSyncTests](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332-L1453) | Registers the hierarchy, matrix values, and skip predicates. |
| Shared NV support helper | [checkTaskMeshShaderSupportNV](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires `VK_NV_mesh_shader` and the selected task/mesh features. |
| Default mustpass | [NV synchronization entries](../../../mustpass/main/vk-default/mesh-shader.txt#L27964-L28013) | Records the exact 50 NV leaves selected for the default profile. |
| Synchronization semantics | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies) | Defines execution dependencies, availability, visibility, and access scopes. |
| Pipeline barriers | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-barriers) | Defines global, buffer, and image barrier semantics used by the cases. |
