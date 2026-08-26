## Overview

**Core question:** Does the selected synchronization primitive make a preceding write visible to a following read when both operations use one queue?

- This page covers the implementation in `vktSynchronizationOperationSingleQueueTests.cpp` and the shared operation/resource framework.
- The factory registers the same test families below both `synchronization.op.single_queue` and `synchronization2.op.single_queue`.
- Each case combines a write operation, a read operation, and a supported resource. The test compares what the write should produce with what the read observes.
- The `synchronization` root uses legacy synchronization commands. The `synchronization2` root uses the synchronization2 command and flag forms and adds sync2-specific variants.

## Background Knowledge

- A Vulkan memory dependency connects a source access to a destination access. The source and destination stage/access masks describe where the write and read occur; image dependencies also describe the layout transition. The test obtains these values from the selected operation implementations.
- Queue order alone does not describe all memory visibility needed by later accesses. The selected barrier, event, semaphore, or fence path must provide the dependency that lets the read observe the write. The Vulkan synchronization chapter defines the execution and memory-dependency rules used here: [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc).
- The legacy and synchronization2 APIs express the same test idea through different command and flag structures. A sync2 case therefore checks the synchronization2 path itself, including `VkPipelineStageFlags2KHR` and `VkAccessFlags2KHR` values.

## Registration Hierarchy

```text
synchronization.op.single_queue
├── fence
├── binary_semaphore
├── timeline_semaphore
├── barrier
└── event
```

```text
synchronization2.op.single_queue
├── fence
├── binary_semaphore
├── timeline_semaphore
├── barrier
├── event
└── multi_events
```

The trees show direct test families; operation-pair and resource descendants are generated below them.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Synchronization root | `synchronization.op.single_queue`, `synchronization2.op.single_queue` | Selects `LEGACY` or `SYNCHRONIZATION2` in the shared factory. | [`createSynchronizedOperationSingleQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293-L1300) |
| Synchronization primitive | `fence`, `binary_semaphore`, `timeline_semaphore`, `barrier`, `event` | Selects the test instance and dependency arrangement. | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1187-L1289) |
| Operation pair | `write_<operation>_read_<operation>` | Selects the source write, destination read, and their stage/access/layout requirements. | [`s_writeOps` and `s_readOps`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36-L112) |
| Resource | Supported entries from `s_resources` | Selects buffer, image, indirect, index, or multisampled resource behavior. | [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36-L71) |
| Sync2 suffix | `_specialized_access_flag`, event `_maintenance9` | Adds specialized access masks or asymmetric event handling where the source and build support them. | [`createTests` variant generation](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1243-L1276) |
| Event queue suffix | `_cq` | Runs an eligible event case on a compute queue. | [`createTests` compute-queue branch](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1265-L1272) |
| Multi-event form | Two real events, or one real event plus `nop` | Exercises two-event waits and a null dependency in sync2. | [`createMultipleEventsTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1085-L1185) |

The default mustpass files contain 7,324 legacy leaves and 15,090 synchronization2 leaves for these roots. In the legacy root, `barrier`, `binary_semaphore`, `fence`, and `timeline_semaphore` each have 1,423 leaves, while `event` has 1,632. In the synchronization2 root, those four primitive families each have 2,634 leaves, while `event` has 4,266 and `multi_events` has 288. Unsupported operation/resource combinations do not create test cases.

## Behavior Parameters

The primary behavioral axis is the synchronization primitive. The operation pair and resource dimensions vary the memory dependency that the primitive must carry.

### `fence`: submission boundary

The test submits the write command buffer, waits for its fence, then submits the read command buffer. The result checks whether the read observes the completed write across this two-submission sequence. See [`FenceTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L732-L818).

### `binary_semaphore`: signal and wait

The write submission signals a binary semaphore and the read submission waits on it. The selected operation scopes still determine the resource access relationship. See [`BinarySemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L458-L574).

### `timeline_semaphore`: chained values

The test places intermediate copy operations between the initial write and final read and advances a timeline semaphore through the chain. Each hop must preserve the data dependency. See [`TimelineSemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L575-L731).

### `barrier`: one command-buffer dependency

The test records the write, a pipeline barrier built from the write and read `SyncInfo`, and the read in one command buffer. Image cases include the write-to-read layout transition. See [`BarrierTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L372-L457).

### `event`: set and wait

The test records the write, sets an event with a dependency, waits for it with the read dependency, and records the read. Eligible cases can use a compute queue. Sync2 event cases also cover specialized access and `VK_DEPENDENCY_ASYMMETRIC_EVENT_BIT_KHR` maintenance9 variants. See [`EventTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76-L187).

### `multi_events`: two-event wait (sync2 only)

The test sets two events and waits on both before recording the reads. One generated form replaces either event with a `nop` event whose dependency contains no resource work. See [`EventsTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L189-L370).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization.op.single_queue.barrier.write_ssbo_compute_read_ssbo_compute.buffer_16384
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `barrier` | Records the writer, a buffer memory barrier, and the reader in one command buffer. |
| `write_ssbo_compute_read_ssbo_compute` | Selects storage-buffer write and read operations implemented by generated compute shaders. |
| `buffer_16384` | Uses a 16 KiB buffer, represented in each shader as 1,024 `uvec4` elements. |

#### Purpose

The writer copies a deterministic host pattern into the tested SSBO, and the reader copies that SSBO into a host-visible result buffer. The intervening barrier must make the compute shader writes visible to the subsequent compute shader reads.

#### Structural Design

| Phase | Shader-visible data flow | Synchronization role |
|-------|--------------------------|----------------------|
| Writer compute dispatch | Host-pattern SSBO at binding 0 → tested SSBO at binding 1 | Produces shader writes to the tested 16 KiB range. |
| Buffer barrier | No shader executes. | Connects compute shader writes to compute shader reads for that range. |
| Reader compute dispatch | Tested SSBO at binding 0 → host-visible result SSBO at binding 1 | Consumes the data made visible by the barrier. |
| Host comparison | Expected writer pattern ↔ reader result | Requires all 16 KiB to match byte-for-byte. |

#### Shader Code

##### Writer Compute Shader

```glsl
#version 440

/// One workgroup with one invocation executes the entire copy loop.
layout(local_size_x = 1) in;

/// Binding 0 is a 16 KiB source SSBO initialized with the deterministic host pattern.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is the 16 KiB tested SSBO written by this operation.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// Copy all 1,024 vectors into the resource covered by the subsequent barrier.
    for (int i = 0; i < 1024; ++i) {
        b_out.data[i] = b_in.data[i];
    }
}
```

##### Reader Compute Shader

```glsl
#version 440

/// One workgroup with one invocation executes the entire copy loop.
layout(local_size_x = 1) in;

/// Binding 0 is the 16 KiB tested SSBO made visible by the pipeline barrier.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is a 16 KiB host-visible result SSBO used for the final byte comparison.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// Copy all 1,024 vectors out of the tested resource for host verification.
    for (int i = 0; i < 1024; ++i) {
        b_out.data[i] = b_in.data[i];
    }
}
```

#### Additional Info

- The reader is the non-primary shader shown here. Its generated GLSL has the same copy-loop structure as the writer for this SSBO/compute pairing, but descriptor binding 0 references the tested resource and binding 1 references the reader's host-visible result buffer; other operation pairs on this page can select a different stage or resource access implementation.
- Each compute operation dispatches exactly one `1 × 1 × 1` workgroup, so the single invocation performs all 1,024 copies rather than indexing by `gl_GlobalInvocationID`.
- The writer's expected data and the reader's result are compared across the complete 16 KiB range after queue completion.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation pair | The selected read/write operation chooses the buffer type, access direction, shader stage, and therefore the generated shader set; non-shader operations use different implementations. | [`createOperationSupport`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L6145-L6306) |
| Resource | Buffer byte size determines the fixed `uvec4` array length and loop bound (`size / 16`), so `buffer_262144` generates 16,384 elements instead of 1,024. | [`BufferSupport::initPrograms`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L2446-L2494) |
| Synchronization primitive | It does not change these generated shaders; it changes how the write and read operations are ordered and made visible. For `barrier`, the test inserts a buffer memory barrier between their recorded commands. | [`BarrierTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L382-L454) |

#### SPIR-V

##### Writer Compute Shader

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

##### Reader Compute Shader

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

- The test constructs `OperationContext`, a shared `Resource`, and write/read `Operation` objects. Resource usage is the union of the write output and read input usage flags.
- The selected operations record commands against that resource. For images, the dependency uses the operation layouts and the image subresource range. For buffers, it uses the buffer range.
- `SynchronizationWrapper` dispatches the common calls to legacy or synchronization2 commands. [`LegacySynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L381-L845) maps to legacy commands; [`Synchronization2Wrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L846-L916) maps to the synchronization2 forms.
- Sync2 variants require `VK_KHR_synchronization2`. Timeline cases require timeline semaphore support. Event cases check portability-subset event support when applicable, and `_maintenance9` cases require `VK_KHR_maintenance9`. Image format and sample-count support, operation support, and compute-queue availability prune unsupported cases.
- After completion, the test compares the write operation's `Data` with the read operation's `Data`. Standard resources require an exact byte match. Indirect buffers pass when the actual counter is at least the expected counter. A mismatch returns `fail`; a successful comparison returns `pass("OK")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fence` | Incorrect ordering or visibility across the two fence-separated submissions; operation stage/access or resource handling is also implicated. |
| `binary_semaphore` | Incorrect semaphore signal/wait submission dependency or incomplete visibility for the selected resource access pair. |
| `timeline_semaphore` | Incorrect timeline value chaining, intermediate-copy dependency, or visibility across one of the hops. |
| `barrier` | Incorrect pipeline-barrier stage/access or image-layout dependency in the single command buffer. |
| `event` | Incorrect event set/wait dependency, event scope handling, image layout handling, or compute-queue path. |
| `multi_events` | Incorrect `vkCmdWaitEvents2KHR` handling when waiting on two event dependencies, including a null dependency. |

### Cause Analysis

#### Dependency scope does not cover the selected accesses

**Possible failure symptoms:** The read-side bytes differ from the write-side bytes, or an indirect read reports a counter below the expected value.

**Possible implementation causes:** The implementation may fail to apply the source/destination stage or access scopes required by the operation pair, or may mishandle an image layout transition. The test source derives these scopes from the operation implementations; a specific implementation cause needs investigation against that operation and the Vulkan synchronization rules.

#### Primitive-specific ordering or signal handling is incorrect

**Possible failure symptoms:** A fence, binary semaphore, timeline semaphore, or event case reaches the final comparison with stale or incomplete data. Timeline failures can identify a particular hop only through the aggregate result check.

**Possible implementation causes:** The implementation may mishandle the selected synchronization object's signal, wait, timeline value, event dependency, or submission sequencing. The source confirms the command arrangement, but it does not assign a failure to a particular driver, hardware, compiler, or host component.

#### Synchronization2 or special event path is incorrect

**Possible failure symptoms:** A sync2-only specialized-access, maintenance9, compute-queue, or multi-event leaf fails its same data comparison, including a two-event case with a `nop` dependency.

**Possible implementation causes:** The implementation may mishandle the synchronization2 command entry point, `VkAccessFlags2KHR` interpretation, asymmetric event dependency, compute queue selection, or multiple-event dependency array. The exact cause requires investigation of the failing path and implementation behavior.

## Case Pruning

### Requirement-based pruning

- Sync2 cases require `VK_KHR_synchronization2`; timeline cases require timeline semaphore support.
- Event cases require the portability-subset event feature when that feature is exposed and disabled.
- `_maintenance9` requires `VK_KHR_maintenance9`; `_cq` requires a suitable compute queue.
- Image cases require supported format usage and sample counts. Every operation must support the selected resource.

### Design-based pruning

- The ordinary matrix includes only operation/resource pairs accepted by `isResourceSupported` for both operations.
- Sync2 suffixes are added only when the selected operation supports specialized access or when the event primitive selects maintenance9 behavior.
- `multi_events` uses four write operations, four read operations, and five resources rather than the full matrix. It generates both real-event pairs and one-real-event/no-op pairs to keep the two-event behavior focused.

## Key Takeaways

- The page tests one invariant across several synchronization mechanisms: the read must observe the preceding write for the selected operation scopes and resource.
- `synchronization.op.single_queue` and `synchronization2.op.single_queue` share the matrix but exercise different API paths; sync2 also expands event and access-flag coverage.
- The expected result comes from the write operation, while the actual result comes from the read operation. Exact byte comparison is the normal check; indirect counters use a lower-bound check.
- A passing case shows that this particular operation/resource combination completed with the selected dependency. A failure identifies an observable synchronization result, not a predetermined bug location.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Single-queue registration | [`createSynchronizedOperationSingleQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293-L1300) | Creates the `single_queue` group for either synchronization type. |
| Matrix and suffix generation | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1187-L1289) | Registers primitive, operation/resource, sync2 suffix, and compute-queue variants. |
| Two-event generation | [`createMultipleEventsTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1085-L1185) | Registers sync2 `multi_events` cases. |
| Primitive implementations | [`vktSynchronizationOperationSingleQueueTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76-L818) | Contains event, barrier, binary semaphore, timeline semaphore, and fence execution. |
| Shared operation behavior | [`vktSynchronizationOperation.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp) | Builds operations, stage/access scopes, layouts, data, and generated programs. |
| Command dispatch | [`vktSynchronizationUtil.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L381-L916) | Selects legacy versus synchronization2 Vulkan calls. |
| Resource descriptions | [`vktSynchronizationOperationResources.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36-L71) | Defines resources used by the matrix. |
| Legacy mustpass | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) | Lists `dEQP-VK.synchronization.op.single_queue` leaves. |
| Sync2 mustpass | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) | Lists `dEQP-VK.synchronization2.op.single_queue` leaves, including sync2-only variants. |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines the memory and execution dependency model used to interpret the checks. |
