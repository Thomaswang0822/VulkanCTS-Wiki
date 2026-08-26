## Overview

**Core question:** If twelve writes are submitted in order and a later read waits only for the last signal, does every read observe its corresponding write?

This page documents the `signal_order` family implemented in [`vktSynchronizationSignalOrderTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp). The same factory is used for both registered categories: `synchronization.signal_order` uses `SynchronizationType::LEGACY`, while `synchronization2.signal_order` uses `SynchronizationType::SYNCHRONIZATION2`. The wrapper in [`vktSynchronizationUtil.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) selects the corresponding submit and barrier commands.

The test checks signal ordering together with explicit write-to-read memory barriers. Waiting for the final signal is therefore the ordering trigger; it is not a substitute for the source's operation-specific synchronization scopes.

## Background Knowledge

- Queue submissions to one queue execute in submission order, but memory visibility between the writes and later reads still depends on the explicit synchronization scopes recorded for the resources.
- A binary semaphore carries no payload and returns to the unsignaled state after a wait. A timeline semaphore carries increasing integer values and can release work waiting for a specified value.
- External memory and semaphore handles let two logical devices refer to the same allocation and synchronization state. Export/import support depends on the selected platform handle type.

## Registration Hierarchy

```text
synchronization.signal_order
├── binary_semaphore
├── timeline_semaphore
├── shared_binary_semaphore
└── shared_timeline_semaphore
```

```text
synchronization2.signal_order
├── binary_semaphore
├── timeline_semaphore
├── shared_binary_semaphore
└── shared_timeline_semaphore
```

The four direct children are registered by [`createSignalOrderTests`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1632-L1645). The operation and resource levels are generated at group initialization; unsupported operation/resource pairs are omitted. The exact executable leaves are generated, so the mustpass files are the authoritative snapshot of currently materialized combinations: [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) and [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt).

## Parameter Dimensions and Observed Values

| Dimension | Values / rule |
|---|---|
| API path | `LEGACY` → `synchronization`; `SYNCHRONIZATION2` → `synchronization2` |
| Semaphore family | `binary_semaphore`, `timeline_semaphore`, `shared_binary_semaphore`, `shared_timeline_semaphore` |
| Write operation | 19 values: copy buffer, buffer/image copies, blit, SSBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, and image vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect |
| Read operation | 30 values: copy buffer, buffer/image copies, blit, UBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, SSBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, image vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, indirect draw, indexed indirect draw, indirect dispatch, and vertex input |
| Resource | Entries from `s_resources` compatible with both selected operations |
| Shared handle pair | Opaque FD; opaque Win32 KMT; opaque Win32. Memory and semaphore handle types are paired. |

Operation names in generated paths use the source's `getOperationName()` spelling. Compatibility and implementation support determine which resource leaves are registered. Each test category has 7,640 default mustpass leaves: 955 in each non-shared family and 2,865 in each shared family.

## Behavior Parameters

### `binary_semaphore`

A single device uses two distinct queues. Each of twelve write command buffers is submitted as a separate submit entry and signals its own binary semaphore. One read command buffer contains all twelve reads and waits only on the last write semaphore.

### `timeline_semaphore`

The single-device flow is the same, but one timeline semaphore carries increasing values. A host signal releases the initial timeline value; the ordered submit entries signal later values, and the read submission waits for the final value. Timeline support is checked before execution.

### `shared_binary_semaphore`

The write queue runs on the context device and the read queue on a second logical device created through [`SingletonDevice`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L197). Each resource is exportable on the first device and imported on the second. The final binary semaphore is exported/imported across devices before the read submit.

### `shared_timeline_semaphore`

This is the shared-device flow with a timeline semaphore and increasing values. The source uses one exportable timeline semaphore per device path, imports the final signal into the read device, and waits for the final value.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization.signal_order.binary_semaphore.write_ssbo_compute_read_ssbo_compute.buffer_16384
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `binary_semaphore` | Twelve write submissions signal distinct binary semaphores; the single read submission waits only for the final write semaphore. |
| `write_ssbo_compute` → `read_ssbo_compute` | Both operations use compute-stage storage-buffer access, so the generated writer and reader each use a one-workgroup compute shader with the same SSBO copy loop. |
| `buffer_16384` | The resource is 16,384 bytes, represented as 1,024 `uvec4` elements (`16384 / 16`), which fixes the generated loop bound. |

#### Purpose

The compute shaders copy the complete SSBO between the operation's input and output resources. The synchronization test then checks that the reader observes the writer's pattern after waiting only for the last ordered binary-semaphore signal.

#### Structural Design

| Phase | Compute-shader structure | Synchronization meaning |
|-------|--------------------------|-------------------------|
| Writer | Binding 0 reads the host-filled pattern; binding 1 writes the shared test buffer; loop copies 1,024 `uvec4` values. | The writer's shader write is the source scope of the operation-specific barrier. |
| Reader | Binding 0 reads the shared test buffer; binding 1 writes the host-visible result buffer; loop copies 1,024 `uvec4` values. | The reader's shader read is the destination scope of the barrier; its result is compared with the writer data. |

#### Shader Code

##### Writer Compute Shader

```glsl
#version 440

layout(local_size_x = 1) in;

/// Binding 0 is the host-filled input buffer for the writer operation.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is the shared 16384-byte test resource written by this operation.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// Copy the complete resource as 1024 std140-aligned uvec4 elements.
    for (int i = 0; i < 1024; ++i) {
        b_out.data[i] = b_in.data[i];
    }
}
```

##### Reader Compute Shader

```glsl
#version 440

layout(local_size_x = 1) in;

/// Binding 0 is the shared 16384-byte test resource read by this operation.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is the host-visible result buffer written by the reader operation.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// Copy the complete resource as 1024 std140-aligned uvec4 elements.
    for (int i = 0; i < 1024; ++i) {
        b_out.data[i] = b_in.data[i];
    }
}
```

#### Additional Info

- `BufferSupport::initPrograms` emits the SSBO declarations and copy loop, then `initPassthroughPrograms` supplies the compute header and `layout(local_size_x = 1) in;`; the writer and reader source text is therefore structurally identical, while descriptor contents give the bindings their different roles.
- The host-side `BufferImplementation` binds the operation resource at binding 1 for the writer and binding 0 for the reader, and places the host buffer at the other binding; after a reader dispatch it adds a shader-write-to-host-read barrier before result extraction.
- The selected 16,384-byte resource is also allocated for each of twelve write/read iterations; the signal-order iterate path records each writer separately, records all readers together, and compares ordinary buffer data byte-for-byte.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Write/read operation stage | `write_ssbo_compute` and `read_ssbo_compute` select `VK_SHADER_STAGE_COMPUTE_BIT`; other SSBO stage variants use the same buffer declarations and copy body but are emitted into the corresponding graphics-stage passthrough shader. | [`makeOperationSupport`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L6162-L6164) and [`BufferSupport::initPrograms`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L2446-L2493) |
| Resource size | The generated array and loop bound change with `resourceDesc.size / sizeof(tcu::UVec4)`; this case yields 1,024 elements, while `buffer_262144` yields 16,384. | [`BufferSupport::initPrograms`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L2446-L2463) and mustpass entry [`buffer_16384`](../../../mustpass/main/vk-default/synchronization.txt#L53174) |
| Access direction | Writer and reader keep the same generated copy shader shape, but host/runtime descriptor updates reverse which operation resource is at binding 0 versus binding 1 and change the synchronization access scope. | [`BufferImplementation`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L1820-L1862) and [`getInSyncInfo`/`getOutSyncInfo`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L1900-L1957) |
| Semaphore family | `binary_semaphore` changes submission and wait behavior, not the compute shader source; timeline and shared families exercise different semaphore or device paths around the same operation-generated shader. | [`QueueSubmitSignalOrderTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1330-L1405) |

#### SPIR-V

##### Writer Compute Shader SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %i "i"
               OpName %Output "Output"
               OpMemberName %Output 0 "data"
               OpName %b_out "b_out"
               OpName %Input "Input"
               OpMemberName %Input 0 "data"
               OpName %b_in "b_in"
               OpDecorate %_arr_v4uint_uint_1024 ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %b_out NonReadable
               OpDecorate %b_out Binding 1
               OpDecorate %b_out DescriptorSet 0
               OpDecorate %_arr_v4uint_uint_1024_0 ArrayStride 16
               OpDecorate %Input BufferBlock
               OpMemberDecorate %Input 0 NonWritable
               OpMemberDecorate %Input 0 Offset 0
               OpDecorate %b_in NonWritable
               OpDecorate %b_in Binding 0
               OpDecorate %b_in DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
   %int_1024 = OpConstant %int 1024
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
  %uint_1024 = OpConstant %uint 1024
%_arr_v4uint_uint_1024 = OpTypeArray %v4uint %uint_1024
     %Output = OpTypeStruct %_arr_v4uint_uint_1024
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
      %b_out = OpVariable %_ptr_Uniform_Output Uniform
%_arr_v4uint_uint_1024_0 = OpTypeArray %v4uint %uint_1024
      %Input = OpTypeStruct %_arr_v4uint_uint_1024_0
%_ptr_Uniform_Input = OpTypePointer Uniform %Input
       %b_in = OpVariable %_ptr_Uniform_Input Uniform
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
      %int_1 = OpConstant %int 1
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %i
         %18 = OpSLessThan %bool %15 %int_1024
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %26 = OpLoad %int %i
         %31 = OpLoad %int %i
         %33 = OpAccessChain %_ptr_Uniform_v4uint %b_in %int_0 %31
         %34 = OpLoad %v4uint %33
         %35 = OpAccessChain %_ptr_Uniform_v4uint %b_out %int_0 %26
               OpStore %35 %34
               OpBranch %13
         %13 = OpLabel
         %36 = OpLoad %int %i
         %38 = OpIAdd %int %36 %int_1
               OpStore %i %38
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Reader Compute Shader SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %i "i"
               OpName %Output "Output"
               OpMemberName %Output 0 "data"
               OpName %b_out "b_out"
               OpName %Input "Input"
               OpMemberName %Input 0 "data"
               OpName %b_in "b_in"
               OpDecorate %_arr_v4uint_uint_1024 ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %b_out NonReadable
               OpDecorate %b_out Binding 1
               OpDecorate %b_out DescriptorSet 0
               OpDecorate %_arr_v4uint_uint_1024_0 ArrayStride 16
               OpDecorate %Input BufferBlock
               OpMemberDecorate %Input 0 NonWritable
               OpMemberDecorate %Input 0 Offset 0
               OpDecorate %b_in NonWritable
               OpDecorate %b_in Binding 0
               OpDecorate %b_in DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
   %int_1024 = OpConstant %int 1024
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
  %uint_1024 = OpConstant %uint 1024
%_arr_v4uint_uint_1024 = OpTypeArray %v4uint %uint_1024
     %Output = OpTypeStruct %_arr_v4uint_uint_1024
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
      %b_out = OpVariable %_ptr_Uniform_Output Uniform
%_arr_v4uint_uint_1024_0 = OpTypeArray %v4uint %uint_1024
      %Input = OpTypeStruct %_arr_v4uint_uint_1024_0
%_ptr_Uniform_Input = OpTypePointer Uniform %Input
       %b_in = OpVariable %_ptr_Uniform_Input Uniform
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
      %int_1 = OpConstant %int 1
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %i
         %18 = OpSLessThan %bool %15 %int_1024
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %26 = OpLoad %int %i
         %31 = OpLoad %int %i
         %33 = OpAccessChain %_ptr_Uniform_v4uint %b_in %int_0 %31
         %34 = OpLoad %v4uint %33
         %35 = OpAccessChain %_ptr_Uniform_v4uint %b_out %int_0 %26
               OpStore %35 %34
               OpBranch %13
         %13 = OpLabel
         %36 = OpLoad %int %i
         %38 = OpIAdd %int %36 %int_1
               OpStore %i %38
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The test selects queues capable of the write and read operations. Non-shared cases require two different queues on one device; if no suitable second queue exists, the case is unsupported.
2. It creates twelve resource/operation pairs and records each write in its own command buffer. Each command buffer ends with a barrier from the write operation's stage/access scope to the read operation's scope; images also carry the required layout transition.
3. It records all twelve reads in one command buffer. In the shared path it unions their destination stage masks for the final wait; the non-shared path uses the wrapper's top-of-pipe wait stage.
4. It submits the writes together as twelve ordered submit entries. Binary entries signal separate semaphores; timeline entries use increasing values and the initial host signal.
5. It submits the read command buffer with a wait for only the final write signal, then waits for the read completion. Shared cases perform the equivalent operation on the imported resources and semaphore on device B.
6. It compares each read result with the corresponding write result and waits for device idle before resource destruction. [`DeviceWaitIdleGuard`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L87-L103) protects teardown.

For ordinary buffer and image results, the expected write data is compared with data produced by the read operation using `deMemCmp`. For indirect buffers, the observed counter must be at least the expected value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `binary_semaphore` | Incorrect ordering of binary semaphore signals or waits, or incomplete visibility for the selected resource dependency. |
| `timeline_semaphore` | Incorrect increasing-value signal order, host release, final-value wait, or resource visibility. |
| `shared_binary_semaphore` | Incorrect external memory/semaphore import-export behavior or cross-device binary signal ordering. |
| `shared_timeline_semaphore` | Incorrect external timeline payload sharing, final-value ordering, or cross-device resource visibility. |

### Cause Analysis

#### Signal ordering or resource dependency is incorrect

**Possible failure symptoms:** One or more ordinary buffer or image reads differ from their corresponding writes, or an indirect counter is lower than expected even though the read waited for the last signal.

**Possible implementation causes:** The implementation may allow the final wait to complete before an earlier ordered signal and its submitted work are complete, or may mishandle the explicit stage, access, queue-family, or image-layout dependency for the selected operation pair.

#### External sharing path is incorrect

**Possible failure symptoms:** Only `shared_*` leaves fail, with imported resources containing stale data or the imported final semaphore failing to release the read submission.

**Possible implementation causes:** The implementation may mishandle external memory binding, semaphore payload import/export, compatible handle types, or synchronization between the two logical devices. The failing handle pair and resource identify the path that needs investigation.

## Case Pruning

### Requirement-based pruning

- Timeline families require timeline semaphore feature support; synchronization2 leaves require `VK_KHR_synchronization2`.
- Generated leaves require both operations to support the selected resource and require queues with the necessary capabilities.
- Shared leaves require compatible exportable/importable external memory and semaphore handle types. Platform-specific opaque FD or Win32 support determines which handle-pair leaves can run.

### Design-based pruning

- Empty operation-pair groups are not registered when no resource supports both operations.
- Shared families use opaque FD, opaque Win32 KMT, and opaque Win32 handles when available; copy-semantics handles such as sync FD are intentionally excluded.
- Each case uses twelve write/read iterations to test ordered signals without multiplying that count into another registered dimension.

## Key Takeaways

- The test deliberately submits twelve writes in one ordered queue-submit call and waits only for the final signal.
- Explicit operation-specific barriers connect each write to its corresponding read.
- Binary and timeline semaphore families cover both one-signal-per-iteration and increasing-value signaling.
- Shared families additionally test external memory and semaphore import/export across two logical devices.
- Both category roots are covered by one implementation page; their API submission path is selected by `SynchronizationType`.

## Source Reference Appendix

| Topic | Evidence |
|---|---|
| Factory and four families | [`createSignalOrderTests`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1632-L1645) |
| Non-shared generated matrix | [`QueueSubmitSignalOrderTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1522-L1617) |
| Shared matrix and handle pairs | [`QueueSubmitSignalOrderSharedTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L975-L1094) |
| Non-shared execution | [`QueueSubmitSignalOrderTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1198-L1470) |
| Shared execution and import/export | [`QueueSubmitSignalOrderSharedTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L431-L815) |
| Operation/resource definitions | [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36-L112) and `s_resources` in the synchronization operation resources headers |
| API abstraction | [`vktSynchronizationUtil.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) |
| Registered leaves | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) and [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) |
