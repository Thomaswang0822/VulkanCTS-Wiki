## Overview

**Core question:** Does the selected EXT mesh-shader stage pair observe the value written by its predecessor when the requested resource, access masks, and synchronization form are used?

- `vktMeshShaderSyncTestsEXT.cpp` implements the `mesh_shader.ext.synchronization` test family. It generates a regular stage, resource, barrier, and access matrix, plus the auxiliary `other.barrier_across_secondary` case.
- The regular cases pass one 32-bit value through a host, transfer, task, mesh, or fragment operation and check it at a later stage. The check ends in a host buffer, the resource buffer, or a 1x1 color image readback.
- The source registers 81 EXT synchronization paths in the exact `vk-default` mesh-shader mustpass. The matrix is pruned before test cases are created, so unsupported combinations do not appear as empty or invalid leaves.
- This page explains the registered hierarchy, the legal parameter combinations, support gates, generated shader roles, command-buffer execution, observable checks, failure meaning, and the secondary-command-buffer test.

## Background Knowledge

- **Memory dependency.** A Vulkan memory dependency orders earlier and later operations and makes selected earlier writes available and visible to selected later accesses. Its stage masks select pipeline stages; its access masks select the reads and writes included in those scopes. The synchronization specification describes this relationship in [memory dependency semantics](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies-memory).
- **Image layout.** An image barrier also changes a specified image subresource from an old layout to a new layout. The old layout must be `VK_IMAGE_LAYOUT_UNDEFINED` or match the image's current layout; the transition is part of the dependency, as described in [image layout transitions](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-image-layout-transitions).
- **Mesh-shader pipeline.** A task shader can call `EmitMeshTasksEXT` to launch mesh work. A mesh shader emits primitives, and a fragment shader can write the resulting value to a color attachment. Reverse-order pairs such as mesh-to-task need separate graphics pipelines so the producer and consumer occur in the intended order.

## Registration Hierarchy

```text
mesh_shader.ext.synchronization
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
├── mesh_to_host
├── mesh_to_task
├── frag_to_task
├── frag_to_mesh
└── other
```

`other` is an auxiliary test family under the same registered `synchronization` group. Its only test case is `barrier_across_secondary`. The regular children are registered by the stage-combination loop in [EXT registration](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772-L1906); the auxiliary child is added at [the `other` registration block](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1908-L1915).

## Parameter Dimensions and Observed Values

The regular leaf name is formed as `<write access>_<read access>` below a stage pair, resource type, and barrier type. The table lists the source-controlled dimensions and their registered values.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Stage pair | `host_to_task`, `host_to_mesh`, `transfer_to_task`, `transfer_to_mesh`, `task_to_mesh`, `task_to_frag`, `task_to_transfer`, `task_to_host`, `mesh_to_frag`, `mesh_to_transfer`, `mesh_to_host`, `mesh_to_task`, `frag_to_task`, `frag_to_mesh` | Selects the producer and consumer operations. The last three reverse or cross-pipeline pairs require two graphics pipelines. | [stage combinations](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1774-L1797) |
| Resource type | `uniform_buffer`, `storage_buffer`, `storage_image`, `sampled_image` | Selects the descriptor type and whether the value travels through a buffer or a 1x1 image. | [resource types](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1799-L1808) |
| Barrier type | `memory_barrier`, `specific_barrier`, `subpass_dependency` | Selects a general memory barrier, a buffer or image memory barrier, or a render-pass dependency. | [barrier types](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1810-L1818) |
| Write access | `host_write`, `transfer_write`, `shader_write` | Selects the source access mask. The stage legality predicate permits host writes only from `host`, transfer writes only from `transfer`, and shader writes only from task, mesh, or fragment stages. | [write access values and legality](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L173-L199), [stage access pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L234-L253) |
| Read access | `host_read`, `transfer_read`, `shader_read`, `uniform_read` | Selects the destination access mask. Shader destinations accept shader or uniform reads; `uniform_read` is valid only for a uniform buffer. | [read access values and legality](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L201-L230), [resource access pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L255-L290) |
| Auxiliary family | `other.barrier_across_secondary` | Uses compute-to-task synchronization across secondary command-buffer boundaries instead of the regular matrix. | [auxiliary case registration](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1908-L1915) |

The exact default mustpass contains 81 EXT paths: 80 regular leaves and one auxiliary leaf. For example, [the mustpass block](../../../mustpass/main/vk-default/mesh-shader.txt#L26810-L26890) includes the `frag_to_mesh` through `transfer_to_task` paths and `other.barrier_across_secondary`.

## Behavior Parameters

The primary behavioral axis is the **stage pair**. Each value changes where the write occurs, where the read occurs, how the resource reaches the result, and whether one or two pipelines or render-pass subpasses are needed. The resource, barrier, and access dimensions then specialize that handoff.

### `host_to_task` and `host_to_mesh`: Host publication to a mesh pipeline

The host writes only buffer resources, flushes the host-visible allocation, and the task or mesh shader reads the value. `host_to_task` places the read in the task shader and carries it through task payload to the mesh and fragment stages. `host_to_mesh` reads it directly in the mesh shader. The destination is checked through the color attachment.

### `transfer_to_task` and `transfer_to_mesh`: Transfer publication to a mesh pipeline

The host writes an auxiliary host-coherent buffer, then a transfer command copies the value into the selected buffer or image. The test applies a host-to-transfer barrier before the copy and a selected transfer-to-shader dependency before the task or mesh read. The color attachment carries the result to host readback.

### `task_to_mesh`, `task_to_frag`, and `mesh_to_frag`: Shader writes followed by graphics reads

The producer shader writes a storage buffer or storage image. The consumer reads it with `shader_read`. In `task_to_mesh`, task payload also supplies the normal task-to-mesh interface, while the resource read happens in the mesh shader. `task_to_frag` and `mesh_to_frag` read the resource in the fragment shader and write the value to the color attachment.

### `task_to_transfer` and `mesh_to_transfer`: Shader publication to transfer

The task or mesh shader writes the storage resource. A shader-to-transfer dependency makes the value available to the copy. The command buffer copies the resource into the auxiliary host-coherent buffer, inserts a transfer-to-host barrier, and the host compares the copied value.

### `task_to_host` and `mesh_to_host`: Shader publication to host

The producer writes a host-visible storage buffer. The selected shader-to-host dependency orders the write before host access. The host invalidates the allocation and compares the resource buffer directly. These pairs cannot use a uniform buffer because shader writes to that resource are not legal.

### `mesh_to_task`, `frag_to_task`, and `frag_to_mesh`: Reverse or cross-pipeline graphics order

These pairs put the producer in an earlier pipeline and the consumer in a later pipeline. Passthrough task, mesh, and fragment shaders keep the graphics pipeline complete while the selected producer or consumer performs the resource operation. A subpass dependency uses two subpasses; a memory or specific barrier uses two render passes.

### `other.barrier_across_secondary`: Compute-to-task secondary-buffer handoff

This fixed case dispatches compute work in one secondary command buffer, records a compute-to-task memory barrier there, then executes a graphics secondary command buffer containing task and mesh work. Each task invocation verifies one compute-written index and writes a one-valued result to a second storage buffer.

## Shader Analysis

The regular shaders are generated inline by `MeshShaderSyncCase::initPrograms`. This page uses one walkthrough for the representative `host_to_task` resource-read path. The stage-pair, resource, and barrier variations are summarized below rather than duplicating similar generated shaders.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.synchronization.host_to_task.storage_buffer.memory_barrier.host_write_shader_read
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `host_to_task` | The host publishes the value and the task shader consumes it. |
| `storage_buffer` | Binding 0 is a storage buffer containing one `uint` value. |
| `memory_barrier` | A general host-to-task memory barrier carries the selected write and read access masks. |
| `host_write_shader_read` | The source access is `VK_ACCESS_HOST_WRITE_BIT`; the destination access is `VK_ACCESS_SHADER_READ_BIT`. |
| `1628510124` | The generated case's test value is compared at the final color readback. |

#### Purpose

This generated task shader checks that a host write made visible by the host-to-task dependency can be read by the task stage. The task payload carries the value onward so the normal mesh pipeline can expose it in the color attachment.

#### Structural Design

| Step | Task stage | Following graphics stages | Meaning |
|------|------------|---------------------------|---------|
| 1 | Read `sb.value` when `pc.readVal > 0u` | Mesh receives `td.value` as task payload | The consumer observes the resource published by the host. |
| 2 | Call `EmitMeshTasksEXT(1u, 1u, 1u)` | Mesh emits one triangle and fragment writes the payload | The graphics path transports the observed value to the color output. |
| 3 | No direct host access | The color image is copied to a verification buffer | The host obtains an observable result after submission. |

#### Shader Code

Reconstructed GLSL for the task stage:

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable

layout(local_size_x=1) in;

struct TaskData { uint value; };
taskPayloadSharedEXT TaskData td;

layout (set=0, binding=0) readonly buffer StorageBuffer { uint value; } sb;
layout (push_constant, std430) uniform PushConstantBlock {
    uint writeVal;
    uint readVal;
} pc;

void main ()
{
    td.value = 0u;
    if (pc.readVal > 0u) { td.value = sb.value; }
    EmitMeshTasksEXT(1u, 1u, 1u);
}
```

#### Additional Info

- `writeVal` is present in the common push-constant block but the host-to-task path performs the write on the host, so the task shader only uses `readVal` [push constants and task generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L500-L543), [task source generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L666-L683).
- The mesh stage receives `td.value` as `primitiveValue[0]`, and the fragment stage writes that value to `outColor` [mesh generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L686-L716), [fragment generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L719-L739).
- The EXT helper selects SPIR-V 1.4 for these generated programs [EXT build options](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L141-L144).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Stage pair | The read and write statements move between task, mesh, and fragment shaders; host and transfer cases replace the producer shader operation with host or copy commands. | [stage-specific generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L666-L739) |
| Resource type | `uniform_buffer` emits a uniform block, `storage_image` emits `uimage2D`, and `sampled_image` emits `usampler2D`; read statements use the matching GLSL operation. | [resource declaration and read generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L470-L543) |
| Barrier type | `memory_barrier` uses a general dependency, `specific_barrier` targets the buffer or image, and `subpass_dependency` places the dependency in the render pass. | [barrier recording](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1289-L1317), [render-pass dependencies](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L832-L887) |
| Access pair | The selected write and read access values become the barrier access masks; legality predicates remove stage/resource/access mismatches. | [access-mask selection](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L938-L941), [matrix pruning](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1872-L1882) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `task`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 37
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TaskEXT %main "main" %td %pc %sb
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %TaskData "TaskData"
               OpMemberName %TaskData 0 "value"
               OpName %td "td"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "writeVal"
               OpMemberName %PushConstantBlock 1 "readVal"
               OpName %pc "pc"
               OpName %StorageBuffer "StorageBuffer"
               OpMemberName %StorageBuffer 0 "value"
               OpName %sb "sb"
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpDecorate %StorageBuffer Block
               OpMemberDecorate %StorageBuffer 0 NonWritable
               OpMemberDecorate %StorageBuffer 0 Offset 0
               OpDecorate %sb NonWritable
               OpDecorate %sb Binding 0
               OpDecorate %sb DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
   %TaskData = OpTypeStruct %uint
%_ptr_TaskPayloadWorkgroupEXT_TaskData = OpTypePointer TaskPayloadWorkgroupEXT %TaskData
         %td = OpVariable %_ptr_TaskPayloadWorkgroupEXT_TaskData TaskPayloadWorkgroupEXT
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
%_ptr_TaskPayloadWorkgroupEXT_uint = OpTypePointer TaskPayloadWorkgroupEXT %uint
%PushConstantBlock = OpTypeStruct %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
       %bool = OpTypeBool
%StorageBuffer = OpTypeStruct %uint
%_ptr_StorageBuffer_StorageBuffer = OpTypePointer StorageBuffer %StorageBuffer
         %sb = OpVariable %_ptr_StorageBuffer_StorageBuffer StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
     %uint_1 = OpConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpAccessChain %_ptr_TaskPayloadWorkgroupEXT_uint %td %int_0
               OpStore %14 %uint_0
         %20 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %21 = OpLoad %uint %20
         %23 = OpUGreaterThan %bool %21 %uint_0
               OpSelectionMerge %25 None
               OpBranchConditional %23 %24 %25
         %24 = OpLabel
         %30 = OpAccessChain %_ptr_StorageBuffer_uint %sb %int_0
         %31 = OpLoad %uint %30
         %32 = OpAccessChain %_ptr_TaskPayloadWorkgroupEXT_uint %td %int_0
               OpStore %32 %31
               OpBranch %25
         %25 = OpLabel
               OpEmitMeshTasksEXT %uint_1 %uint_1 %uint_1 %td
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The regular instance creates a 1x1 `VK_FORMAT_R32_UINT` color image. It creates either a 4-byte host-visible buffer for a buffer resource or a 1x1 image with transfer and descriptor usage flags. Sampled-image cases also create a nearest, clamp-to-edge sampler.
- Binding 0 exposes the selected resource to the shader stages that participate in the stage pair. A push-constant range carries `writeVal` and `readVal`. Transfer source or destination cases allocate a separate host-visible, host-coherent auxiliary buffer so preparation and readback do not add an unintended host-memory dependency.
- Host sources write `testValue` into a resource buffer and flush it. Transfer sources write the same value to the auxiliary buffer, record a host-to-transfer barrier, and copy it into the resource buffer or image. Shader image sources transition the image to `GENERAL` before the shader write.
- General barriers use `makeMemoryBarrier`. Specific barriers use a `VkBufferMemoryBarrier` for buffers or a `VkImageMemoryBarrier` for images. Image barriers choose `GENERAL`, `SHADER_READ_ONLY_OPTIMAL`, or `TRANSFER_SRC_OPTIMAL` according to the resource and path.
- For shader-to-shader dependency cases, the render pass contains a dependency from subpass 0 to the last subpass with the selected stage and access masks. Reverse-order or non-dependency cases use two pipelines and, when needed, two render passes. A self-dependency draw uses two draws in one subpass and a general memory barrier because buffer and non-attachment image barriers are not valid there [render-pass construction](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L832-L905), [self-dependency execution](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1326-L1400).
- The test binds the descriptor set, pushes the control values, draws one mesh task, ends the render pass, and inserts the shader-to-host or shader-to-transfer dependency when the destination is not a shader stage. It submits the command buffer with `submitCommandsAndWait`.
- A transfer destination copies the resource into the auxiliary buffer and then uses a transfer-to-host barrier. A host destination reads the host-visible resource buffer after invalidation. A shader destination transitions and copies the color attachment into a host-coherent verification buffer.
- The regular instance compares the selected result with `testValue`. The `other` instance invalidates its verification buffer and compares all `128 * 16384` entries with `1` after executing the compute and graphics secondary command buffers [regular result checks](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1438-L1539), [secondary-buffer execution and check](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1710-L1767).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host_to_task`, `host_to_mesh` | Host flush, host-to-shader dependency, descriptor/resource visibility, or task/mesh read path failure. |
| `transfer_to_task`, `transfer_to_mesh` | Host-to-transfer preparation, transfer-to-shader dependency, image layout, descriptor/resource visibility, or shader read path failure. |
| `task_to_mesh`, `task_to_frag`, `mesh_to_frag` | Shader write-to-read dependency, render-pass dependency, storage resource access, or stage-specific shader path failure. |
| `task_to_transfer`, `mesh_to_transfer` | Shader-to-transfer dependency, image copy/layout handling, or auxiliary readback path failure. |
| `task_to_host`, `mesh_to_host` | Shader-to-host dependency, host-visible storage-buffer writeback, or host invalidation/readback failure. |
| `mesh_to_task`, `frag_to_task`, `frag_to_mesh` | Two-pipeline ordering, reverse-stage dependency, or passthrough/selected shader path failure. |
| `other.barrier_across_secondary` | Secondary-command-buffer execution ordering, compute-to-task barrier, task verification writes, or task-to-host readback failure. |

### Cause Analysis

#### Source value not visible at the consumer

**Possible failure symptoms:** The auxiliary destination buffer, resource buffer, or color verification buffer contains a value other than the per-case `testValue`. The regular instance reports the found and expected values and fails the case.

**Possible implementation causes:** The selected source and destination access scopes may not include the actual resource accesses, or the stage masks may not order the producer and consumer. Vulkan defines availability and visibility through those scopes, so a mismatch can leave a read unable to observe the write [access scopes](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies-access-scopes). For image cases, an incorrect old or new layout can also make the image operation invalid or prevent the intended contents from reaching the copy.

#### Pipeline or render-pass handoff does not carry the value

**Possible failure symptoms:** Shader-destination cases produce a wrong color value, especially in reverse-stage pairs that use two pipelines or in dependency cases that use two subpasses.

**Possible implementation causes:** The pipeline or subpass order may not match the selected producer and consumer. A subpass dependency limits its first and second scopes by the declared stage and access masks [subpass dependency scopes](../../../../vulkan-docs/src/chapters/renderpass.adoc#vksubpassdependency). A selected shader may also fail to write or read the resource while the passthrough stages continue to produce a valid-looking triangle.

#### Secondary-command-buffer synchronization fails

**Possible failure symptoms:** One or more entries in `verificationBuffer` is `0` instead of `1`, and the `other` case reports unexpected values.

**Possible implementation causes:** The compute secondary command buffer may not publish its storage-buffer writes to the task stage, or the primary command buffer may not preserve the intended execution order while executing the compute and graphics secondary buffers. The recorded task-to-host barrier must also make the verification writes visible before host invalidation. The source checks the whole verification array, so a localized failure is sufficient to fail the test.

## Case Pruning

### Requirement-based pruning

- Every regular case requires `VK_EXT_mesh_shader` and mesh support. A task-stage pair also requires task-shader support through `checkTaskMeshShaderSupportEXT` [EXT support helper](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139).
- Cases with `shader_write` require `DEVICE_CORE_FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS`. The `other` case requires task and mesh support plus that same feature [regular support gate](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L647-L655), [secondary support gate](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1574-L1578).
- The registration loop removes resource types that the source stage cannot write or the destination stage cannot read. It removes `uniform_read` except for uniform buffers and removes write/read access values that do not match the selected stage or resource.

This pruning means the case is not legal or not supported for the selected implementation path. A skipped case is not a synchronization failure.

### Design-based pruning

- `subpass_dependency` is kept only for shader-to-shader pairs because the source places it between graphics subpasses.
- Uniform buffers are read-only to shader stages, sampled images are read-only, and host stages use only buffer resources. Storage images and storage buffers are the shader-writable resources.
- Reverse shader pairs use two pipelines because one pipeline cannot execute fragment before task or mesh in the requested producer-consumer order. The dependency form expresses the handoff with two subpasses; the other barrier forms use separate render passes.
- The `other` family is not expanded into the regular matrix. It intentionally fixes the resource shape, compute dimensions, and secondary-command-buffer sequence to isolate the cross-secondary-buffer barrier behavior.

## Key Takeaways

- The regular test family varies synchronization along independent stage, resource, barrier, write-access, and read-access dimensions, but it creates only combinations that the source predicates consider meaningful.
- The final value is always observable: by a host-visible resource buffer, an auxiliary transfer buffer, or a color attachment copied to a host-coherent buffer.
- `subpass_dependency` is a render-pass synchronization form for shader-to-shader cases; `memory_barrier` and `specific_barrier` exercise general and resource-targeted pipeline barriers.
- `other.barrier_across_secondary` tests a different boundary. Compute fills a storage buffer in one secondary command buffer, task validates it in another, and the host checks every verification element.
- A mismatch means that the selected source-to-destination path did not deliver the expected value, but the exact cause can be in access scopes, stage ordering, image layout handling, shader generation, command-buffer execution, or result readback.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Stage, resource, barrier, and access definitions | [parameter helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L58-L411) | Defines enum values, Vulkan stage/access flags, resource declarations, and legality predicates. |
| Regular shader generation | [generated task, mesh, and fragment programs](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L657-L799) | Shows how the selected stage performs the read or write and how passthrough stages transport the result. |
| Render-pass dependency construction | [custom render passes](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L832-L905) | Shows when dependencies create two subpasses and which stage/access masks they use. |
| Regular runtime | [regular `iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L919-L1539) | Shows resource creation, layout transitions, barriers, command recording, submission, readback, and checks. |
| Auxiliary runtime | [secondary command-buffer case](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1542-L1768) | Shows compute and graphics secondary buffers, barrier placement, primary execution, and full-buffer verification. |
| Registration and pruning | [EXT test factory](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772-L1918) | Shows exact registered dimensions, pruning predicates, incrementing test values, and the `other` family. |
| Support gates | [mesh-shader support helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L148) | Shows the required EXT functionality, task/mesh feature checks, and SPIR-V 1.4 build target. |
| Default mustpass | [vk-default mesh-shader entries](../../../mustpass/main/vk-default/mesh-shader.txt#L26810-L26890) | Confirms the exact EXT synchronization paths included in the default mustpass. |
| Memory dependency rules | [Vulkan synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies-memory) | Defines availability, visibility, dependency access scopes, and pipeline barrier ordering. |
| Subpass dependency rules | [Vulkan `VkSubpassDependency`](../../../../vulkan-docs/src/chapters/renderpass.adoc#vksubpassdependency) | Defines the source and destination subpass, stage, and access scopes used by dependency cases. |