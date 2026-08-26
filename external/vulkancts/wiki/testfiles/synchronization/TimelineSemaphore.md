## Overview

**Core question:** Do timeline semaphore values correctly order device work, host work, host waits, fan-out dependencies, and out-of-order queue submissions?

- This page covers the timeline semaphore suites implemented in [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp).
- The source registers parallel suites under `synchronization.timeline_semaphore` and `synchronization2.timeline_semaphore`. Most behavior is shared; the selected `SynchronizationType` controls the submit and barrier API path.
- Generated operation cases combine writer and reader operations with compatible resources. Smaller fixed families check host waits, counter values, sparse binding, and handling of irrelevant timeline submit information.
- A case passes only when the observed data, wait result, or semaphore counter agrees with the timeline dependency it constructed.

## Background Knowledge

- A timeline semaphore carries a monotonically increasing 64-bit payload. A wait for value `N` is satisfied when the semaphore reaches at least `N`; signal operations must advance the payload rather than reset it.
- Queue submissions may wait for a value before any host or queue operation has signaled it. The pending work becomes eligible after a later signal reaches the requested value.
- A semaphore establishes execution ordering between submissions. The submitted operations and their synchronization scopes still determine which resource writes become visible to later reads.
- `maxTimelineSemaphoreValueDifference` limits how far outstanding waits and signals may be separated from the current semaphore value.

## Registration Hierarchy

```text
synchronization.timeline_semaphore
├── device_host
├── one_to_n
├── wait_before_signal
├── wait
├── sparse_bind (non-VulkanSC only)
└── misc
```

```text
synchronization2.timeline_semaphore
├── device_host
├── one_to_n
├── wait_before_signal
└── wait
```

The legacy suite alone includes `device_host.misc.initial_value`, `sparse_bind`, and `misc.ignore_timeline_semaphore_info`. The two snippets are separate because this page owns test cases in both synchronization test categories.

## Parameter Dimensions and Observed Values

`device_host`, `one_to_n`, and `wait_before_signal` use the same case-generation scheme. They enumerate 19 writers and 30 readers, then visit the resource descriptions in [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp). A leaf is added only when both operations support that resource, so the tree is a filtered cross-product rather than every theoretical combination.

The writers cover transfer operations and SSBO/image writes from graphics and compute stages. The readers cover transfer operations; UBO, SSBO, and image reads from graphics and compute stages; indirect draw/dispatch buffers; and vertex input. Names come from the shared operation and resource helpers, producing paths such as:

```text
<root>.timeline_semaphore.device_host.<write>_<read>.<resource>
<root>.timeline_semaphore.one_to_n.<write>_<read>.<resource>
<root>.timeline_semaphore.wait_before_signal.<write>_<read>.<resource>
```

Each family shares pipeline-cache data across its generated leaves to reduce repeated pipeline construction.

The default mustpass lists contain 2,880 leaves under the legacy family and 2,873 under the synchronization2 family. Each generated operation family contributes 955 compatible writer-reader-resource leaves in each test category.

## Behavior Parameters

### `device_host`

Builds twelve iterations around one timeline semaphore. Each iteration records a GPU writer followed by a GPU reader. Timeline values order the writer, reader, and host handoff. A host thread waits for each reader value, copies that reader's output into the next writer, and signals the next CPU value. After all submissions complete, the test compares the first input with the final output.

The nested `misc` group adds:

- `max_difference_value`: exercises values constrained by `maxTimelineSemaphoreValueDifference`.
- `initial_value`: checks immediate waits and counter queries for zero and nonzero initial values. This case is registered only in the legacy tree.

### `one_to_n`

Submits one producer and fans its result out through multiple copy/read operations on available queues. A timeline signal gates the downstream work. The test waits for completion and checks every consumer's data, covering the rule that one timeline point can release multiple dependent submissions.

### `wait_before_signal`

Submits dependent queue work before the value it waits for has been signaled. The host later signals the starting timeline point, allowing the queued chain to run. Final data checks show that waits submitted ahead of their matching signal are honored and that the dependency chain completes correctly.

### `wait`

Exercises host wait and counter-query behavior directly:

| Case | Expected behavior |
|---|---|
| `all_signal_from_device` | Wait-all completes after device submissions signal every semaphore. |
| `one_signal_from_device` | Wait-any completes after a device submission signals one semaphore. |
| `all_signal_from_host` | Wait-all completes after host signals every semaphore. |
| `one_signal_from_host` | Wait-any completes after host signals one semaphore. |
| `host_wait_before_signal` | A zero-timeout wait first returns `VK_TIMEOUT`; after the prerequisite signal, the wait succeeds. |
| `poll_signal_from_device` | Counter polling observes a value signaled by queue submission. |
| `poll_signal_from_host` | Counter polling observes a host-signaled value. |

### `sparse_bind` (legacy only)

Combines timeline semaphore waits and signals with `vkQueueBindSparse`. The five leaves cover 0/0, 0/1, 1/0, 1/1, and 2/2 wait/signal semaphore counts. The group is guarded by `#ifndef CTS_USES_VULKANSC`.

### `misc.ignore_timeline_semaphore_info` (legacy only)

Submits binary semaphores with a `VkTimelineSemaphoreSubmitInfo` structure in the `pNext` chain whose value counts do not describe timeline semaphores. Compute work and a copied result confirm that the structure is ignored when no timeline semaphore is present, including avoiding use of irrelevant value arrays.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization.timeline_semaphore.device_host.write_ssbo_compute_read_ssbo_compute.buffer_16384
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `device_host` | Builds twelve writer/reader iterations whose GPU and host handoffs advance one timeline semaphore. |
| `write_ssbo_compute_read_ssbo_compute` | Selects storage-buffer write and read operations, both implemented by generated compute shaders. |
| `buffer_16384` | Uses a 16 KiB buffer, represented in each shader as 1,024 `uvec4` elements. |

#### Purpose

The writer copies each iteration's host-provided data into that iteration's SSBO, and the reader copies the SSBO into a host-visible result buffer. Timeline values order twelve GPU writer/reader pairs and the intervening host copies so that the first input must reach the final reader unchanged.

#### Structural Design

| Chain step | Shader-visible data flow | Timeline handoff |
|------------|--------------------------|------------------|
| Writer dispatch | Iteration host-input SSBO at binding 0 → iteration resource SSBO at binding 1 | Waits for the preceding iteration's CPU value (except the first writer), then signals this iteration's writer value. |
| Reader dispatch | Iteration resource SSBO at binding 0 → iteration host-result SSBO at binding 1 | Waits for the writer value, then signals the reader value. |
| Host handoff | No shader executes; the reader result becomes the next writer's host input. | Waits for the reader value, performs the copy, then signals the CPU value that releases the next writer. |
| Final check | First writer input ↔ twelfth reader result | Runs after queue completion and the host thread join; all 16 KiB must match. |

#### Shader Code

##### Writer Compute Shader

```glsl
#version 440

/// One workgroup with one invocation executes the entire copy loop.
layout(local_size_x = 1) in;

/// Binding 0 is a 16 KiB source SSBO initialized from host data for this iteration.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is the 16 KiB iteration resource written by this operation.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// A single invocation copies every vector into the resource consumed by the paired reader.
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

/// Binding 0 is the 16 KiB iteration resource made visible after the writer dispatch.
layout(set = 0, binding = 0, std140) readonly buffer Input {
    uvec4 data[1024];
} b_in;

/// Binding 1 is a 16 KiB host-visible result SSBO used by the host copy thread.
layout(set = 0, binding = 1, std140) writeonly buffer Output {
    uvec4 data[1024];
} b_out;

void main (void)
{
    /// A single invocation copies every vector out for the host handoff or final comparison.
    for (int i = 0; i < 1024; ++i) {
        b_out.data[i] = b_in.data[i];
    }
}
```

#### Additional Info

- The reader is the non-primary shader shown here. For this SSBO/compute pair its generated GLSL is instruction-for-instruction identical to the writer's; descriptor binding 0 instead names the iteration resource and binding 1 names the reader's host-visible result, so the two stages have different runtime roles but the same SPIR-V assembly.
- Both operations issue a direct `vkCmdDispatch(1, 1, 1)`. The one invocation performs all 1,024 copies rather than deriving an element index from `gl_GlobalInvocationID`.
- `DeviceHostSyncTestCase::initPrograms()` initializes both operation programs, while `BufferSupport::initPrograms()` obtains the fixed array length and loop bound from `resource size / sizeof(uvec4)`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation pair | The selected operation determines the access direction, buffer kind, stage, and generated program set. Other matrix entries can use transfer operations, graphics stages, uniform buffers, or images instead of these two compute SSBO shaders. | [`makeOperationSupport`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L6130-L6336) |
| Resource | Buffer byte size determines the fixed `uvec4` array length and loop bound (`size / 16`); the 256 KiB sibling therefore generates 16,384 elements instead of 1,024. | [`BufferSupport::initPrograms`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L2446-L2494) |
| Timeline family and API path | `device_host` scheduling does not alter these generated shaders; it controls the twelve writer/reader submissions and host handoffs. The synchronization2 counterpart uses the same operation programs while selecting the synchronization2 wrapper path. | [`DeviceHostTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L923-L1069) |

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

- All leaves require timeline semaphore functionality through `VK_KHR_timeline_semaphore` or its core equivalent. Synchronization2 leaves also require `VK_KHR_synchronization2`. Generated cases run the support checks for their selected operations and resources.
- The common code creates timeline semaphores and uses `vkWaitSemaphores`, `vkSignalSemaphore`, and `vkGetSemaphoreCounterValue`. `SynchronizationWrapper` selects legacy or synchronization2 submission structures according to the test category.
- `device_host` alternates submitted operation pairs with a host thread that waits, copies data for the next iteration, and signals the next timeline value. It compares the first input with the final output after twelve iterations.
- `one_to_n` submits one producer and distributes its data through compatible queue operations. Every consumer is compared with the producer data after the timeline dependency completes.
- `wait_before_signal` queues the dependent work first, signals the starting value from the host, waits for device idle, and compares the first writer data with the final reader data.
- The fixed wait and polling leaves check Vulkan return values and counter payloads. The sparse-bind leaves check the values signaled by `vkQueueBindSparse`; the ignored-submit-info leaf reads back the compute output and requires value `777`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `device_host` | Incorrect ordering or visibility across the alternating device and host timeline values, or an incorrect semaphore counter value. |
| `one_to_n` | Incorrect fan-out release or data visibility for one or more downstream queue operations. |
| `wait_before_signal` | Incorrect handling of a queued wait whose matching timeline value is signaled later. |
| `wait` | Incorrect wait-all, wait-any, timeout, host-signal, device-signal, or counter-query behavior. |
| `sparse_bind` | Incorrect timeline wait or signal processing in `vkQueueBindSparse`. |
| `misc.ignore_timeline_semaphore_info` | Incorrectly consuming timeline value arrays when a submission contains only binary semaphores, or failing the submitted compute work. |

### Cause Analysis

#### Timeline value progression or wait handling is incorrect

**Possible failure symptoms:** A host wait returns the wrong result, a counter reports an unexpected payload, a waiter observes a decreasing value, or dependent work fails to complete after the required value is signaled.

**Possible implementation causes:** The implementation may mishandle timeline payload comparison, host signal/wait operations, queue signal ordering, or the `maxTimelineSemaphoreValueDifference` constraint. The failing path and observed return value are needed to distinguish these mechanisms.

#### Submission dependency does not make operation data visible

**Possible failure symptoms:** The final reader data differs from the original writer data, or one consumer in a fan-out case contains stale or incomplete bytes.

**Possible implementation causes:** The implementation may fail to preserve the execution and memory dependency associated with the selected timeline wait/signal pair, or may mishandle the operation-specific resource scope. The selected writer, reader, and resource identify the dependency that needs investigation.

#### Legacy special-path handling is incorrect

**Possible failure symptoms:** A sparse-bind semaphore reaches the wrong value, or the binary-semaphore submission returns an output other than `777` when irrelevant timeline value arrays are attached.

**Possible implementation causes:** The implementation may mishandle timeline values in `vkQueueBindSparse` or may read `VkTimelineSemaphoreSubmitInfo` value arrays that do not correspond to timeline semaphores. A compute execution failure can produce the same output mismatch in the ignored-submit-info leaf.

## Case Pruning

### Requirement-based pruning

- Every leaf requires timeline semaphore support; synchronization2 leaves require synchronization2 support as well.
- Generated writer, reader, and resource combinations run their operation-specific feature, format, usage, and shader-stage checks.
- `sparse_bind` is omitted from Vulkan SC builds and requires queue sparse-binding support.

### Design-based pruning

- The three generated operation families register a leaf only when both operations support the selected resource. Unsupported pairs do not create empty intermediate nodes.
- `device_host.misc.initial_value`, `sparse_bind`, and `misc.ignore_timeline_semaphore_info` are intentionally registered only under the legacy test category.
- The `wait` family uses seven focused cases instead of combining wait modes with the operation/resource matrix.

## Key Takeaways

- The generated families check the same timeline semaphore rule through three execution shapes: host/device chaining, one-to-many release, and waits submitted before their signal.
- The legacy and synchronization2 suites share most test logic, while `SynchronizationWrapper` selects the submission API path.
- Fixed leaves cover host waits, counter values, sparse binding, and one legacy rule for ignoring irrelevant timeline submit information.
- A failed data comparison proves that the constructed dependency did not preserve the expected result; it does not by itself identify a predetermined driver or hardware component.

## Source Reference Appendix

| Area | Source link | Why it matters |
|------|-------------|----------------|
| Legacy and synchronization2 roots | [`createTimelineSemaphoreTests()` and `createSynchronization2TimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2937-L2969) | Registers the direct children shown in both hierarchy snippets. |
| Host waits and fixed counter cases | [`WaitTests` and timeline property cases](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L558-L759) | Implements wait-all, wait-any, polling, initial-value, and maximum-difference behavior. |
| Device/host generation | [`DeviceHostTestsBase`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1123-L1262) | Builds the shared operation matrix and category-specific `misc` children. |
| Wait-before-signal generation | [`WaitBeforeSignalTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1809-L1914) | Registers compatible operation/resource leaves for pre-signaled waits. |
| One-to-many generation | [`OneToNTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2354-L2458) | Registers the fan-out operation/resource matrix. |
| Sparse binding | [`SparseBindGroup`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2708-L2740) | Registers the five legacy sparse-bind leaves. |
| Irrelevant timeline submit info | [`ignoreTimelineSemaphoreSubmitInfoRun()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2818-L2933) | Checks that binary-semaphore submissions ignore unrelated timeline value arrays. |
| Shared operation data | [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp) | Defines the operation and resource inventory used by generated leaves. |
| Submission wrapper | [`vktSynchronizationUtil.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) | Selects the legacy or synchronization2 submission implementation. |
| Legacy mustpass | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) | Lists the legacy timeline semaphore leaves. |
| Synchronization2 mustpass | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) | Lists the synchronization2 timeline semaphore leaves. |
| Timeline semaphore semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines timeline semaphore waits, signals, and payload behavior. |
