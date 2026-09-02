## Overview

**Core question:** Does `VK_EXT_device_generated_commands` execute every generated compute dispatch with the selected buffer, preprocessing, and queue setup?

- This page covers the implementation and registration of `dgc.ext.compute.smoke` in [`vktDGCComputeSmokeTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L584-L620).
- Each test builds an indirect-command layout with one `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH_EXT` token, executes 4 or 1024 generated sequences, and checks an atomic-counter pattern produced by the compute shader.
- The matrix varies command-buffer input generation, indirect-buffer memory, preprocessing state, queue family, and sequence count. The registered names appear exactly below.
- The test does not use an indirect execution set. `DGCGenCmdsInfo` passes `VK_NULL_HANDLE`, so generated commands do not select a pipeline or shader object. The already bound compute pipeline executes the dispatch token.

## Background Knowledge

- A device-generated command sequence is interpreted from an indirect buffer according to a layout. Here each sequence contains one `VkDispatchIndirectCommand`, and the layout's dispatch token turns that structure into a compute dispatch.
- Explicit preprocessing separates command preparation from command execution. The EXT API requires the preprocess result to be synchronized before execution. A preprocess state can reuse the main command buffer or use a separate primary command buffer.
- A compute queue is a queue family that supports compute operations without requiring graphics support. The test uses it when available; otherwise the case is unsupported rather than failed.

## Registration Hierarchy

```text
dgc.ext.compute.smoke
├── 4_sequences_device_local_from_host_no_preprocess_compute_queue
├── 4_sequences_device_local_from_host_no_preprocess_universal_queue
├── 4_sequences_device_local_from_host_preprocess_state_same_compute_queue
├── 4_sequences_device_local_from_host_preprocess_state_same_universal_queue
├── 4_sequences_device_local_from_host_preprocess_state_separate_compute_queue
├── 4_sequences_device_local_from_host_preprocess_state_separate_universal_queue
├── 4_sequences_device_local_from_compute_no_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_no_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_preprocess_state_same_compute_queue
├── 4_sequences_device_local_from_compute_preprocess_state_same_universal_queue
├── 4_sequences_device_local_from_compute_preprocess_state_separate_compute_queue
├── 4_sequences_device_local_from_compute_preprocess_state_separate_universal_queue
├── 4_sequences_host_visible_from_host_no_preprocess_compute_queue
├── 4_sequences_host_visible_from_host_no_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_preprocess_state_same_compute_queue
├── 4_sequences_host_visible_from_host_preprocess_state_same_universal_queue
├── 4_sequences_host_visible_from_host_preprocess_state_separate_compute_queue
├── 4_sequences_host_visible_from_host_preprocess_state_separate_universal_queue
├── 4_sequences_host_visible_from_compute_no_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_no_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_same_compute_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_same_universal_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue
├── 1024_sequences_device_local_from_host_no_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_no_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_preprocess_state_same_compute_queue
├── 1024_sequences_device_local_from_host_preprocess_state_same_universal_queue
├── 1024_sequences_device_local_from_host_preprocess_state_separate_compute_queue
├── 1024_sequences_device_local_from_host_preprocess_state_separate_universal_queue
├── 1024_sequences_device_local_from_compute_no_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_no_preprocess_universal_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_same_compute_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_same_universal_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_separate_compute_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_separate_universal_queue
├── 1024_sequences_host_visible_from_host_no_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_no_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_same_compute_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_same_universal_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_separate_compute_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_separate_universal_queue
├── 1024_sequences_host_visible_from_compute_no_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_no_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_same_compute_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_same_universal_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue
└── 1024_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Sequence count | `4`, `1024` | Tests a small and large command stream. For `1024`, the implementation also sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`; compute processing is unordered by definition, so the flag is a no-op. | [`SmokeTestParams` and registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L53-L73) |
| Indirect-command memory | `host_visible`, `device_local` | Selects whether the buffer consumed by the dispatch token is host-visible or device-local. | [`iterate`, buffer selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L300-L373) |
| Command source | `from_host`, `from_compute` | Copies commands directly from host memory, or runs a compute shader that copies them into the indirect buffer before DGC execution. | [`initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L161-L193) |
| Preprocess mode | `no_preprocess`, `preprocess_state_same`, `preprocess_state_separate` | Selects implicit preparation, explicit preparation in the main command buffer state, or explicit preparation with a separate state command buffer. | [`PreprocessType` and preprocess calls](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L53-L72), [`iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L468-L484) |
| Queue choice | `compute_queue`, `universal_queue` | Submits to a compute queue family or the context's universal queue. | [`iterate`, queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L209-L216) |
| Execution set | none | Every variant passes `VK_NULL_HANDLE` as `indirectExecutionSet`; this matrix tests dispatch generation and execution, not per-sequence pipeline selection. | [`DGCGenCmdsInfo`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L450-L463) |

The registration loops form the Cartesian product of sequence count `{4, 1024}`, `hostVisible` `{false, true}`, `preCompute` `{false, true}`, preprocessing `{none, same state, separate state}`, and queue choice `{universal, compute}`. This produces 48 direct children. Each name uses `<count>_sequences_<memory>_<source>_<preprocess>_<queue>`.

## Behavior Parameters

The primary behavioral axis is the indirect-command preparation path. Its values change how dispatch data reaches DGC; memory placement, sequence count, and queue selection exercise that path under different conditions.

### `from_host` and `no_preprocess` / direct indirect execution

The host writes `VkDispatchIndirectCommand` structures into a host-visible indirect buffer, or writes a host-visible staging buffer that the command buffer copies into a device-local indirect buffer. Generated execution then reads the selected buffer through its device address.

### `from_compute` / device-generated command data

The host initializes a source storage buffer. A one-workgroup `gen` compute shader copies each command into a second storage buffer that also has indirect-buffer and shader-device-address usage. A shader-write-to-indirect-read barrier makes the copied data available to generated dispatch execution.

### `preprocess_state_same` and `preprocess_state_separate` / explicit preparation

Both values set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`, call `vkCmdPreprocessGeneratedCommandsEXT`, and execute with `isPreprocessed` set to `VK_TRUE`. The same-state value uses the main command buffer as `stateCommandBuffer`. The separate-state value records pipeline and descriptor state in another primary command buffer, then passes it to preprocessing. The helper synchronizes preprocessing with execution.

## Shader Analysis

The page has two inline GLSL compute shaders. The `comp` shader is part of the tested behavior. The `gen` shader appears only in `from_compute` variants and copies indirect command records; it does not choose dispatch dimensions. The walkthrough uses a `from_host` case so it can isolate the shader that records generated dispatch coverage.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.smoke.4_sequences_device_local_from_host_no_preprocess_universal_queue
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `4_sequences` | Executes four generated dispatch sequences, giving a small counter pattern that can be checked range by range. |
| `device_local_from_host` | The host writes the commands to a staging buffer, then a transfer copies them to the device-local indirect buffer consumed by DGC. |
| `no_preprocess` | Executes generated commands without a separate explicit preprocessing command. |
| `universal_queue` | Records and submits the transfer, generated dispatches, and result barrier on the context's universal queue. |

#### Purpose

The shader records which workgroup indices each generated dispatch reaches. The host can then detect missing, duplicated, or incorrectly sized dispatches by comparing the counters with the generated command list.

#### Structural Design

| Shader step | Operation | Observable effect |
|-------------|-----------|-------------------|
| Select a counter | Flatten `gl_WorkGroupID` using `gl_NumWorkGroups`. | X-, Y-, and Z-major dispatches map their workgroups to the same linear range starting at counter 0. |
| Record one invocation | Atomically add 1 at queue-family scope. | Each workgroup contributes 64 increments to its counter because the local size is 64. |
| Accumulate dispatch coverage | Repeat for every generated sequence. | Counter `i` equals 64 times the number of dispatches containing workgroup index `i`. |

#### Shader Code

```glsl
#version 460
#extension GL_KHR_memory_scope_semantics : enable
/// Binding 0 is a host-visible std430 storage buffer with 256 counters. Every local invocation atomically
/// increments the counter for its flattened workgroup index.
layout (set=0, binding=0, std430) buffer AtomicCountersBlock {
    uint value[256];
} atomicCounters;
/// Each generated dispatch uses 64 local invocations per workgroup.
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
void main ()
{
    /// Flatten the possibly X-, Y-, or Z-major dispatch into the same linear counter range.
    const uint workGroupIndex = gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z + gl_NumWorkGroups.x * gl_WorkGroupID.y + gl_WorkGroupID.x;
    /// Queue-family scope matches execution on either the universal or compute queue selected by the case.
    atomicAdd(atomicCounters.value[workGroupIndex], 1u, gl_ScopeQueueFamily, gl_StorageSemanticsBuffer, (gl_SemanticsAcquireRelease | gl_SemanticsMakeAvailable | gl_SemanticsMakeVisible));
}
```

#### Additional Info

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Sequence count | `4` and `1024` change how many times this fixed shader is dispatched, but do not change its source. | [`SmokeTestCase::initPrograms` and registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L141-L193) |
| Dispatch size and major dimension | Each command selects a workgroup count in `[1, 256]` and assigns it to X, Y, or Z. The flattening expression maps all three forms to one counter range. | [`SmokeTestInstance::iterate`, command generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L285-L298) |
| Command source | `from_compute` adds the separate `gen` shader, but the generated commands still dispatch this `comp` shader. | [`SmokeTestCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L141-L193) |
| Indirect memory, preprocessing, and queue | These dimensions change how commands reach execution and which queue runs them. They do not change the `comp` shader text. | [`SmokeTestInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L209-L494) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
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

- The case checks basic DGC compute support and `vulkanMemoryModel`, which the shader needs for its scopes and semantics. A compute-queue variant requests a compute queue and becomes unsupported if none is available. [`SmokeTestCase::checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L196-L207)
- The host initializes a 256-entry, host-visible `resultsBuffer` to zero and binds it as storage buffer binding 0 for `comp`.
- The host creates one or two command-data buffers. `from_host` with host-visible memory uses one indirect buffer directly. `from_host` with device-local memory uses a transfer source and indirect destination. `from_compute` uses a storage source and an indirect/storage destination, with the destination memory matching the selected host-visible or device-local mode.
- The host creates a preprocess buffer sized for the sequence count and a one-token compute layout. It generates each `VkDispatchIndirectCommand` pseudorandomly: one dimension is in `[1, 256]`, and the other two are 1.
- The command buffer first runs `gen` for `from_compute`, then inserts a compute-to-indirect-read barrier. For device-local `from_host`, it copies the staging buffer and inserts a transfer-to-indirect-read barrier.
- The host binds `comp` and records implicit generated-command execution or explicit preprocess followed by execution. It inserts a shader-write-to-host-read barrier, submits the selected queue, and waits before reading the result allocation.
- The host counts how many generated dispatches have at least each workgroup count. It expects every counter in a range to equal `64 * number_of_covering_dispatches`; counters above the largest dispatch count must be zero. Any mismatch fails the case and logs the complete command list and result buffer.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `from_host` | Host initialization, transfer to a device-local indirect buffer, device-address use, or DGC dispatch-token interpretation produced unexpected command data or execution. |
| `from_compute` | The generator shader, compute-to-indirect synchronization, storage-buffer binding, or DGC consumption of shader-produced command data produced an unexpected dispatch pattern. |
| `no_preprocess` | Implicit DGC preparation or direct command execution produced incorrect dispatch coverage. |
| `preprocess_state_same` | Explicit preprocessing using the main command buffer state or its synchronization with execution produced incorrect dispatch coverage. |
| `preprocess_state_separate` | Explicit preprocessing using a separate state command buffer or its synchronization with execution produced incorrect dispatch coverage. |

All values also depend on the shared compute pipeline, indirect layout, atomic result buffer, queue submission, and host-side expected-range calculation.

### Cause Analysis

#### Indirect command data and address consumption

**Possible failure symptoms:** One or more ranges in `resultsBuffer` contain a value different from `64 * number_of_covering_dispatches`, or a counter that should be zero is nonzero.

**Possible implementation causes:** The implementation may have read the wrong `VkDispatchIndirectCommand`, used an incorrect sequence stride or device address, or failed to execute one or more generated dispatches. For `from_compute`, source-to-destination storage writes may not have become visible to indirect command reads. The source identifies the barriers and buffer usage; a more specific cause requires investigation.

#### Explicit preprocessing and state command buffers

**Possible failure symptoms:** A preprocessing variant reports the same range mismatch, with failures possible after either same-state or separate-state preprocessing.

**Possible implementation causes:** The implementation may have mishandled `vkCmdPreprocessGeneratedCommandsEXT`, the `isPreprocessed` execution path, the preprocess buffer, or the state command buffer used for preprocessing. The Vulkan specification requires explicit synchronization between a separate preprocessing action and execution. A more specific cause requires investigation against the implementation and synchronization validation.

#### Queue-family execution and result visibility

**Possible failure symptoms:** The host reads stale or incomplete counter values after the queue wait, causing range verification to fail.

**Possible implementation causes:** The selected queue may not have honored compute execution or the shader-write-to-host-read dependency as recorded. The shader uses queue-family memory scope, and the source records a host-read barrier before submission completes. A more specific hardware, driver, or host cause requires investigation.

## Case Pruning

### Requirement-based pruning

- `checkDGCExtComputeSupport(context, DGCComputeSupportType::BASIC)` gates DGC compute requirements.
- `vulkanMemoryModel` is required for the shader's queue-family scope and memory semantics.
- `compute_queue` variants require an available compute queue through `context.getComputeQueue()`.

Unsupported requirements produce `NotSupportedError`; they are not expected test failures.

### Design-based pruning

- The matrix uses only sequence counts `4` and `1024`, host-visible/device-local indirect memory, host/compute command generation, three preprocess modes, and two queue choices.
- The `unordered` field is true only for the 1024-sequence variants. Compute dispatch sequences are already unordered, and the specification says the unordered flag is ignored for compute, so setting it checks that the explicit flag is harmless.
- The layout contains only a dispatch token. It has no execution-set token, pipeline token, or push-constant token, because this smoke family isolates generated compute dispatch execution.

## Key Takeaways

- The test exercises generated compute dispatch through direct host data, a transfer, and a compute-produced indirect buffer.
- Preprocessing changes the command preparation timeline and state command buffer, while the expected counter pattern stays the same.
- A pass requires every counter range to match the number of dispatches that cover it, multiplied by the shader's 64 local invocations.
- The matrix has no execution-set selection. The bound compute pipeline is fixed for every generated sequence.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `SmokeTestParams` and shader generation | [`vktDGCComputeSmokeTestsExt.cpp#L53-L193`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L53-L193) | Defines dimensions and the two compute shaders. |
| Support checks | [`vktDGCComputeSmokeTestsExt.cpp#L196-L207`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L196-L207) | Defines feature and queue requirements. |
| Resource and command setup | [`vktDGCComputeSmokeTestsExt.cpp#L209-L484`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L209-L484) | Shows buffers, layout, queue, preprocessing, barriers, and generated execution. |
| Result verification | [`vktDGCComputeSmokeTestsExt.cpp#L485-L579`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L485-L579) | Defines copyback, expected ranges, diagnostics, and pass/fail. |
| Registered test construction | [`vktDGCComputeSmokeTestsExt.cpp#L584-L620`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L584-L620) | Defines the exact 48 direct children. |
| Mustpass evidence | [`dgc.txt`](../../../mustpass/main/vk-default/dgc.txt) | Canonical mustpass list for DGC paths. |
| EXT DGC specification | [`generatedcommands.adoc`](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L23-L29) | Defines preprocessing synchronization. |
| Layout usage flags | [`generatedcommands.adoc`](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L318-L337) | Defines explicit preprocessing and unordered compute semantics. |
