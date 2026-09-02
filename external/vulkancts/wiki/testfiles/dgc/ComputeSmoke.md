## Overview

**Core question:** Do NV device-generated compute commands execute every registered dispatch with the expected workgroup coverage?

- This page covers `dgc.nv.compute.smoke`, implemented and registered by [`vktDGCComputeSmokeTests.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L53-L580).
- Each case generates 4 or 1024 indirect dispatches, executes them through a one-token NV DGC layout, and checks a 256-entry atomic-counter result buffer.
- The 32 variants select sequence count, command-buffer memory placement, command generation path, preprocessing mode, and queue type.

## Background Knowledge

For the shared concept device-generated-command layouts, see [Background Knowledge](../../categories/dgc.md#background-knowledge) of the `dgc` page.

- A `VkDispatchIndirectCommand` record stores the `x`, `y`, and `z` workgroup counts for one indirect compute dispatch. These dimensions determine which workgroup IDs exist when the generated dispatch executes.

## Registration Hierarchy

```text
dgc.nv.compute.smoke
├── 1024_sequences_device_local_from_compute_explicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_explicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_compute_implicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_implicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_explicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_explicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_implicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_implicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_explicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_explicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_implicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_implicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_explicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_explicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_implicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_implicit_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_explicit_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_explicit_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_implicit_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_implicit_preprocess_universal_queue
├── 4_sequences_device_local_from_host_explicit_preprocess_compute_queue
├── 4_sequences_device_local_from_host_explicit_preprocess_universal_queue
├── 4_sequences_device_local_from_host_implicit_preprocess_compute_queue
├── 4_sequences_device_local_from_host_implicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_explicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_explicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_implicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_implicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_explicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_host_explicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_implicit_preprocess_compute_queue
└── 4_sequences_host_visible_from_host_implicit_preprocess_universal_queue
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Sequence count | `4`, `1024` | Sets the number of indirect dispatch records and the `sequencesCount` passed to `VkGeneratedCommandsInfoNV`. The `1024` variants also set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_NV`. | [`SmokeTestParams` and registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L53-L64), [`createDGCComputeSmokeTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L554-L580) |
| Command-buffer memory placement | `device_local`, `host_visible` | Selects the memory requirement for the destination command buffer. The initial host upload remains host-visible in every case. | [`command-buffer setup`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L288-L359) |
| Command generation | `from_host`, `from_compute` | Selects direct host data or the generated `gen` compute shader copy into the destination command buffer. | [`SmokeTestCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L149-L182), [`command preparation`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L407-L429) |
| Preprocessing | `implicit_preprocess`, `explicit_preprocess` | Selects whether `vkCmdPreprocessGeneratedCommandsNV` runs before execution. | [`preprocess and execute`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L430-L456) |
| Queue | `compute_queue`, `universal_queue` | Selects a dedicated compute queue and its family index, or the context queue and family index. | [`queue selection`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L197-L204) |

## Behavior Parameters

The primary behavioral axis is the complete registered execution variant. Each name combines the five dimensions above and identifies the command stream, preparation path, preprocessing mode, and queue path under test.

### `4_sequences_*` and `1024_sequences_*` : sequence count

The test generates 4 or 1024 `VkDispatchIndirectCommand` records. For each record, deterministic pseudo-random generation chooses a total workgroup count from 1 through 256 and places that count in one major dimension, `x`, `y`, or `z`; the other two dimensions remain 1. The `1024` cases also set the unordered-sequences layout flag. Compute pipelines are unordered by default, so the flag exercises that layout setting without changing the expected counter values.

### `*_device_local_*` and `*_host_visible_*` : command memory

The host first writes all records to a host-visible buffer. With `host_visible`, the destination buffer is host-visible. With `device_local`, `from_host` cases use a second device-local buffer and copy the records into it with `vkCmdCopyBuffer`; `from_compute` cases use a second device-local buffer as the `gen` shader's destination. The test uses the destination buffer as the indirect-command stream.

### `*_from_host_*` and `*_from_compute_*` : command production

`from_host` uses the host-uploaded records directly when the destination is host-visible. For a device-local destination, it copies the records with a transfer command and then synchronizes transfer writes with indirect-command reads. `from_compute` creates the `gen` shader, dispatches it once with one workgroup, and has its 64 local invocations copy chunks of the records from the initial storage buffer to the destination storage and indirect buffer. A compute-to-indirect-read barrier follows that dispatch.

### `*_explicit_preprocess_*` and `*_implicit_preprocess_*` : DGC preparation

Explicit variants record `vkCmdPreprocessGeneratedCommandsNV`, then call the helper that synchronizes preprocessing with execution. They pass `VK_TRUE` to `vkCmdExecuteGeneratedCommandsNV`. Implicit variants skip the preprocess command and pass `VK_FALSE`.

### `*_compute_queue` and `*_universal_queue` : queue path

Compute-queue variants obtain a compute queue and its queue-family index for command-pool creation and submission. Universal-queue variants use the context queue and family index. A compute-queue case is unsupported when no suitable queue exists.

## Shader Analysis

The test creates two generated compute programs. `comp` is present in every case. It flattens `gl_WorkGroupID` using `gl_NumWorkGroups`, then performs an acquire-release atomic add with `gl_ScopeQueueFamily`, `gl_StorageSemanticsBuffer`, `gl_SemanticsMakeAvailable`, and `gl_SemanticsMakeVisible`. The `gen` program appears only in `from_compute` cases. It copies `VkDispatchIndirectCommand` records from the initial storage buffer to the destination buffer, with bounds checking for its fixed chunks. Both programs target SPIR-V 1.3. Source generation is in [`SmokeTestCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L128-L182).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.smoke.4_sequences_host_visible_from_host_implicit_preprocess_universal_queue
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `4_sequences` | Generates four indirect dispatch records. |
| `host_visible_from_host` | The host-visible upload buffer is also the indirect-command buffer. |
| `implicit_preprocess` | Execution skips the explicit preprocess command. |
| `universal_queue` | Submission uses the context queue and queue-family index. |

#### Purpose

The shader checks that each generated dispatch reaches the workgroups described by its indirect command and updates the counter for each reached workgroup.

#### Structural Design

| Shader phase | Operation | Result |
|---|---|---|
| Interface | Declare 256 `uint` counters and a compute workgroup with local size 64. | The host can check one counter for each flattened workgroup index. |
| Index calculation | Flatten `gl_WorkGroupID` with `gl_NumWorkGroups`. | All three dispatch dimensions address the same counter space. |
| Atomic update | Add 1 with queue-family scope and buffer memory semantics. | One covered workgroup contributes 64 to its counter. |

#### Shader Code

```glsl
#version 460
#extension GL_KHR_memory_scope_semantics : enable
layout (set=0, binding=0, std430) buffer AtomicCountersBlock {
    uint value[256];
} atomicCounters;
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
void main ()
{
    const uint workGroupIndex = gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z +
        gl_NumWorkGroups.x * gl_WorkGroupID.y + gl_WorkGroupID.x;
    atomicAdd(atomicCounters.value[workGroupIndex], 1u, gl_ScopeQueueFamily,
        gl_StorageSemanticsBuffer,
        (gl_SemanticsAcquireRelease | gl_SemanticsMakeAvailable | gl_SemanticsMakeVisible));
}
```

#### Additional Info

- `SmokeTestCase::initPrograms` emits this shader for every registered variant. The `gen` shader is added only for `from_compute` variants.
- The command-generation, preprocessing, and queue choices change host-side execution paths. They do not change this shader's interface or counter operation.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Sequence count | Changes the number of generated dispatches; the shader source and 256-counter array stay fixed. | [`SmokeTestParams`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L53-L64) |
| Command generation | `from_compute` adds the separate `gen` program; `comp` is unchanged. | [`initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L149-L182) |
| Memory placement, preprocessing, and queue | Change command preparation, layout flags, or submission; they do not change `comp`. | [`SmokeTestInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L197-L464) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from the `comp` generator
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 51
; Schema: 0
               OpCapability Shader
               OpCapability VulkanMemoryModel
               OpExtension "SPV_KHR_vulkan_memory_model"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical Vulkan
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_KHR_memory_scope_semantics"
               OpName %main "main"
               OpName %workGroupIndex "workGroupIndex"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %AtomicCountersBlock "AtomicCountersBlock"
               OpMemberName %AtomicCountersBlock 0 "value"
               OpName %atomicCounters "atomicCounters"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_arr_uint_uint_256 ArrayStride 4
               OpDecorate %AtomicCountersBlock Block
               OpMemberDecorate %AtomicCountersBlock 0 Offset 0
               OpDecorate %atomicCounters Binding 0
               OpDecorate %atomicCounters DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
   %uint_256 = OpConstant %uint 256
%_arr_uint_uint_256 = OpTypeArray %uint %uint_256
%AtomicCountersBlock = OpTypeStruct %_arr_uint_uint_256
%_ptr_StorageBuffer_AtomicCountersBlock = OpTypePointer StorageBuffer %AtomicCountersBlock
%atomicCounters = OpVariable %_ptr_StorageBuffer_AtomicCountersBlock StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_5 = OpConstant %int 5
     %int_64 = OpConstant %int 64
  %int_24584 = OpConstant %int 24584
 %uint_24648 = OpConstant %uint 24648
    %uint_64 = OpConstant %uint 64
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%workGroupIndex = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIMul %uint %15 %18
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %19 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %workGroupIndex %33
         %41 = OpLoad %uint %workGroupIndex
         %43 = OpAccessChain %_ptr_StorageBuffer_uint %atomicCounters %int_0 %41
         %48 = OpAtomicIAdd %uint %43 %int_5 %uint_24648 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checks require NV DGC compute support and `vulkanMemoryModel`. Compute-queue cases also require an available compute queue. Unsupported cases stop in `checkSupport`.
- The host creates the compute pipeline, a one-dispatch-token indirect-command layout, a `PreprocessBuffer` sized for the selected sequence count, command buffers, storage-buffer descriptors, and a host-visible result buffer containing 256 zeroed counters.
- The host seeds `de::Random` from the registered parameters and builds the indirect command list. It uploads that list, then records either the `gen` dispatch and its barrier, the transfer copy and its barrier, or no preparation command when the initial buffer is already the indirect destination.
- The command buffer binds the result descriptor and compute pipeline. Explicit variants preprocess the generated commands before execution. The test then executes all selected sequences through `vkCmdExecuteGeneratedCommandsNV`.
- A compute-to-host memory barrier makes shader writes available for host reads. The test submits the command buffer to the selected queue and waits for completion.
- The host invalidates the result allocation and reconstructs the expected counter ranges from the indirect command list. For each range, it counts how many dispatches cover that workgroup index and multiplies the count by 64.
- The case passes only when every entry in the 256-counter result buffer equals its reconstructed value. On failure, the test logs the full indirect-command list and result buffer.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `4` or `1024` sequence count | The implementation may execute the wrong number of sequences, use the wrong `sequencesCount`, or mishandle the unordered-sequences layout flag used by the `1024` variants. |
| `device_local` or `host_visible` | The destination command buffer may have incompatible memory or usage behavior, or the host-visible result readback may expose stale data. |
| `from_host` or `from_compute` | A host upload, transfer copy, or `gen` shader write may not produce the command records consumed by indirect execution. |
| `implicit_preprocess` or `explicit_preprocess` | Preprocessing may be omitted, performed with the wrong state, or not synchronized with execution. |
| `compute_queue` or `universal_queue` | Queue-family selection or submission synchronization may lead to incorrect generated dispatch execution. |

### Cause Analysis

#### Generated dispatch or shader result mismatch

**Possible failure symptoms:** One or more entries in the 256-counter result buffer differs from the host-computed value. The log identifies the affected range and records the complete command and result buffers.

**Possible implementation causes:** The implementation may execute a generated dispatch with incorrect dimensions or omit a dispatch. Shader compilation or lowering may compute the workgroup index or atomic operation incorrectly. Source-level investigation is needed to distinguish these cases.

#### Command preparation or memory synchronization mismatch

**Possible failure symptoms:** Failures cluster in `from_host` device-local cases or `from_compute` cases, while the result buffer remains readable.

**Possible implementation causes:** A transfer write or `gen` shader write may not become visible to indirect-command reads. The implementation may also use the wrong destination buffer or buffer usage. The source records the required barriers; further source-level or validation-layer investigation is needed to identify the failing operation.

#### Preprocessing mismatch

**Possible failure symptoms:** An explicit-preprocess variant returns unexpected counters while the matching implicit-preprocess variant passes, or the failure affects all explicit cases.

**Possible implementation causes:** The implementation may mishandle `vkCmdPreprocessGeneratedCommandsNV`, the preprocess buffer, or the synchronization between preprocessing and execution. Source-level investigation is needed to isolate the failing step.

#### Queue-path mismatch

**Possible failure symptoms:** A `compute_queue` case produces unexpected counters after the corresponding `universal_queue` case passes.

**Possible implementation causes:** Queue-family command execution or queue synchronization may differ from the required compute execution semantics. The test selects the queue and family index explicitly, so source-level investigation is needed to isolate the cause.

#### Result visibility mismatch

**Possible failure symptoms:** The generated dispatches complete, but the host sees stale or incorrect counter values after submission.

**Possible implementation causes:** Shader writes may not become available to host reads, or the host may invalidate the result allocation incorrectly. The test records a compute-to-host barrier and invalidates the allocation before copying the data; further source-level investigation is needed.

## Case Pruning

### Requirement-based pruning

- Cases require NV DGC compute support and `vulkanMemoryModel` because the shader uses queue-family scope and buffer memory semantics.
- `compute_queue` cases require an available compute queue. Unsupported cases stop in `checkSupport` rather than becoming failures.

### Design-based pruning

- The matrix fixes the shader local size at 64 and the result array at 256 counters. It varies sequence count, command production, memory placement, preprocessing, and queue selection instead of adding unrelated shader or pipeline variants.
- The `1024` cases set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_NV`. Compute dispatches are unordered by default, so the flag exercises that layout option without changing the counter expectation.

## Key Takeaways

- The test detects missing or malformed generated compute dispatches through a counter pattern reconstructed from every indirect command.
- `from_compute`, device-local storage, explicit preprocessing, and compute-queue execution each add a distinct preparation or synchronization path while keeping the shader result contract unchanged.
- The two sequence counts provide a short case and a larger case that also exercises the unordered-sequences layout flag.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `SmokeTestParams` | [`SmokeTestParams`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L53-L64) | Defines the registered dimensions, unordered flag, and fixed shader constants. |
| `SmokeTestCase::initPrograms` | [`initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L128-L182) | Generates `comp` and optional `gen` GLSL programs. |
| `SmokeTestCase::checkSupport` | [`checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L184-L195) | Applies feature and queue support gates. |
| `SmokeTestInstance::iterate` | [`iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L197-L467) | Creates resources, selects memory and queues, records preparation, preprocesses, executes, and reads back results. |
| Result verification | [`result verification`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L469-L549) | Reconstructs expected ranges and returns pass or fail. |
| Registration | [`createDGCComputeSmokeTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L554-L580) | Registers the 32 direct children listed above. |
