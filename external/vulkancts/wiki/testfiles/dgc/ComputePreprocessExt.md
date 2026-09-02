## Overview

**Core question:** Does `VK_EXT_device_generated_commands` preprocess and execute generated compute commands correctly across queue, count-buffer, and state-command-buffer variants?

- This page covers the implementation and registrations in [`vktDGCComputePreprocessTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L51-L575) for `dgc.ext.compute.preprocess`.
- The 24 registered test cases vary four preprocessing/execution queue methods, three count-buffer modes, and two state command buffer placements.
- Each case prepares two generated compute sequences, preprocesses them explicitly, executes them with `isPreprocessed` set to `VK_TRUE`, and checks two host-visible output buffers.
- The page explains the registered paths, the generated command and preprocess buffers, queue synchronization, state command buffers, and result checking.

## Background Knowledge

- **Explicit preprocessing:** A layout with `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` requires `vkCmdPreprocessGeneratedCommandsEXT` to prepare generated-command state before `vkCmdExecuteGeneratedCommandsEXT` consumes it with `isPreprocessed` set to `VK_TRUE`. The two operations therefore need an execution dependency and, when they use different queue families, ownership transfer.
- **Sequence counts:** A sequence count buffer supplies the number of generated sequences to process. A zero count is a valid boundary case that should leave the corresponding output at its initialized value.
- **State command buffers:** The command buffer passed as `stateCommandBuffer` supplies the pipeline and descriptor state used while preprocessing. It may be the command buffer that records preprocessing or a separate command buffer recorded for that purpose.

## Registration Hierarchy

The page covers one implementation-bearing test family with 24 registered direct children:

```text
dgc.ext.compute.preprocess
├── parallel_preprocessing_compute
├── parallel_preprocessing_compute_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_count_buffer
├── parallel_preprocessing_compute_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec
├── parallel_preprocessing_compute_with_universal_exec_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_universal
├── parallel_preprocessing_universal_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec
├── parallel_preprocessing_universal_with_compute_exec_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_count_buffer
├── parallel_preprocessing_universal_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_count_buffer_zero_count
└── parallel_preprocessing_universal_with_count_buffer_zero_count_separate_state_cmd_buffer
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `Method` | `universal`, `compute`, `compute_with_universal_exec`, `universal_with_compute_exec` | Chooses the queue used for preprocessing and, for the last two values, the different queue used for execution. | [`Method` and queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L51-L57), [`parallelPreprocessRun` queue setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L318-L344) |
| `CountBuffer` | no suffix, `with_count_buffer`, `with_count_buffer_zero_count` | Selects no sequence count buffer, a count of one, or a count of zero for each of the two sequences. | [`countBufferCases`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L544-L552), [`sequence count setup`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L143-L161) |
| `StateCmdBuffer` | no suffix, `separate_state_cmd_buffer` | Records preprocessing state in the current command buffer or in another command buffer. | [`stateCmdBufferCases`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L554-L561), [`state command buffer recording`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L349-L375) |
| Registered combination | 4 × 3 × 2 exact names in the hierarchy above | The source constructs every combination of the three dimensions. | [`createDGCComputePreprocessTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L526-L575) |

## Behavior Parameters

`Method` is the primary behavioral axis because it changes which queue preprocesses the generated commands and which queue executes them. `CountBuffer` and `StateCmdBuffer` are secondary dimensions applied to every method.

### `universal` method

The universal queue preprocesses and executes the generated commands. This is the same-queue baseline for the universal path.

### `compute` method

The compute queue preprocesses and executes the generated commands. This is the same-queue baseline for the compute path and requires a compute queue.

### `compute_with_universal_exec` method

The compute queue preprocesses the first sequence and the universal queue executes it. The test transfers the buffers used by preprocessing and execution between queue families when their family indices differ.

### `universal_with_compute_exec` method

The universal queue preprocesses the first sequence and the compute queue executes it. This exercises the reverse queue-family transition and the same preprocessed-state contract.

The secondary dimensions change the common flow as follows:

- `CountBuffer::NO` omits sequence count buffers and uses one sequence in each `VkGeneratedCommandsInfoEXT` structure.
- `CountBuffer::YES` creates two sequence count buffers and writes one to each. The preprocessing information uses a maximum sequence count of `100` to satisfy the source's EXT validity workaround, while the actual count buffer value remains one.
- `CountBuffer::YES_BUT_ZERO` creates the same two buffers but writes zero. The commands are still preprocessed and submitted, but neither counted sequence should modify its output buffer.
- `StateCmdBuffer::SAME` binds the descriptor set and compute pipeline in the command buffer that records preprocessing.
- `StateCmdBuffer::OTHER` records those bindings in a separate state command buffer from the same queue's command pool and passes it to preprocessing.

## Shader Analysis

The device-side program is fixed across all 24 registered paths. Queue selection, count-buffer handling, and state command buffer placement occur in host-side command recording, so one representative walkthrough covers the shader behavior.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.preprocess.parallel_preprocessing_compute_with_universal_exec_with_count_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute_with_universal_exec` | The first sequence is preprocessed on the compute queue and executed on the universal queue. |
| `with_count_buffer` | Each sequence has a count buffer containing `1`. |
| Generated command layout | Each sequence contains one push-constant token followed by one indirect dispatch token. |
| Push constant values | The two sequences supply `100` and `101`. |

#### Purpose

The compute shader copies the push-constant value into a storage buffer. The output value tells the host that the generated push constant reached the shader and that the generated dispatch ran.

#### Structural Design

| Phase | Shader operation | Observable effect |
|-------|------------------|-------------------|
| Input | Read `pc.value` from the push-constant block. | Gets the value encoded in the generated command sequence. |
| Output | Store that value in `outputBuffer.value`. | Produces the value that the host reads after execution. |

#### Shader Code

```glsl
#version 460
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (set=0, binding=0, std430) buffer OutputBlock { uint value; } outputBuffer;
layout (push_constant, std430) uniform PushConstantBlock { uint value; } pc;
void main (void) { outputBuffer.value = pc.value; }
```

#### Additional Info

- `storePushConstantProgram` supplies the compute shader. The generated layout adds a push-constant token at offset zero and a dispatch token after it ([shader and layout setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L97-L107), [generated command layout](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L223-L228)).
- Each command stream contains four `uint32_t` values: one push constant and the three fields of `VkDispatchIndirectCommand`. The two streams use `100` and `101` ([generated command data](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L230-L249)).
- The shader does not vary with `Method`, `CountBuffer`, or `StateCmdBuffer`; those values affect command information, queue submissions, and whether execution occurs.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `Method` | The shader remains unchanged. The selected queues and ownership barriers determine where preprocessing and execution happen. | [queue selection and barriers](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L318-L429) |
| `CountBuffer` | The shader remains unchanged. The count buffer controls whether the generated dispatch runs. | [count-buffer setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L143-L161), [result reference](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L496-L517) |
| `StateCmdBuffer` | The shader remains unchanged. The choice changes where descriptor and pipeline state are recorded for preprocessing. | [state command buffer recording](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L360-L375) |

#### SPIR-V

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
; Bound: 23
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "value"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "value"
               OpName %pc "pc"
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %outputBuffer Binding 0
               OpDecorate %outputBuffer DescriptorSet 0
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%OutputBlock = OpTypeStruct %uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %17 = OpLoad %uint %16
         %19 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0
               OpStore %19 %17
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test first checks `VK_EXT_device_generated_commands` compute support. Methods that use a compute queue also require an available compute queue.
- It creates two host-visible storage output buffers and initializes each to zero. It creates two descriptor sets, one per output buffer, plus a compute pipeline and its push-constant range.
- It creates an explicit-preprocess indirect command layout with a push-constant token followed by a dispatch token. It writes one four-word command stream per sequence and allocates one `PreprocessBufferExt` per sequence from the queried EXT preprocess-memory requirements.
- Count-buffer variants create two `DGCBuffer` objects of one `uint32_t` each. `YES` writes `1` to both buffers. `YES_BUT_ZERO` writes `0` to both. The resulting device addresses become `sequenceCountAddress` in the two `DGCGenCmdsInfo` structures.
- The test selects the preprocessing and execution queue from `Method`. The first sequence is recorded with descriptor and pipeline state, preprocessed, and submitted with a fence. When queue families differ, release barriers cover the output buffer, generated command buffer, preprocess buffer, and count buffer, followed by an acquire barrier on the execution queue.
- The execution command buffer binds the first descriptor set and pipeline, then calls `vkCmdExecuteGeneratedCommandsEXT` with `isPreprocessed` equal to `VK_TRUE`. The test also records preprocessing and execution for the second sequence. For a queue switch, it submits the execution command buffer and the second sequence's preprocessing/execution command buffer to their respective queues and waits on both fences.
- A shader-write-to-host barrier makes the output writes available for host reads. The host invalidates each output allocation, reads one `uint32_t`, and compares it with `i + 100` for output buffer `i` when execution is enabled.
- In `YES_BUT_ZERO` cases, the expected value is `0` for both buffers because the count buffers suppress the generated sequences. Any mismatch logs the buffer position, expected value, and observed value, then fails the test.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `universal` | Same universal-queue path: generated command layout, preprocessing, synchronization, compute execution, or output validation. |
| `compute` | Same compute-queue path: compute-queue command recording, preprocessing, synchronization, compute execution, or output validation. |
| `compute_with_universal_exec` | Cross-queue path with compute preprocessing and universal-queue execution: queue ownership transfer, cross-queue synchronization, generated command execution, or output validation. |
| `universal_with_compute_exec` | Cross-queue path with universal preprocessing and compute-queue execution: queue ownership transfer, cross-queue synchronization, generated command execution, or output validation. |

### Cause Analysis

#### Preprocess or generated-command execution failure

**Possible failure symptoms:** A baseline or nonzero-count case reports an output buffer value other than the generated push constant, `100` or `101`.

**Possible implementation causes:** The implementation may prepare the explicit preprocess state incorrectly, consume it incorrectly during `vkCmdExecuteGeneratedCommandsEXT`, or fail to execute the generated compute dispatch. The failing layer requires investigation of the reported case and validation data.

#### Count-buffer handling failure

**Possible failure symptoms:** A `with_count_buffer` case produces the wrong value, or the implementation runs a different number of generated sequences from the count supplied in the buffer.

**Possible implementation causes:** The command processing path may read `sequenceCountAddress` incorrectly, use stale count-buffer data, or apply the count to the wrong generated-command information. The specific cause requires investigation of the failing case.

#### Zero-count handling failure

**Possible failure symptoms:** A `with_count_buffer_zero_count` case changes an output from its initialized zero value, or otherwise reports a nonzero result.

**Possible implementation causes:** The execution path may fail to honor a zero sequence count, or synchronization may expose incorrect count data or stale output data. Source-level investigation is needed to distinguish these possibilities.

#### Queue-switch or visibility failure

**Possible failure symptoms:** A cross-queue method cannot consume the preprocessed sequence, or produces a result different from the equivalent same-queue method.

**Possible implementation causes:** The queue-family release/acquire barriers may not transfer the generated command, preprocess, count, and output buffers as required, or the implementation may mishandle visibility of preprocess writes before indirect-command reads. The exact cause requires investigation rather than a predetermined hardware, driver, or host attribution.

#### State command buffer handling failure

**Possible failure symptoms:** A `separate_state_cmd_buffer` case fails while its same-state counterpart passes, with an output mismatch after preprocessing and execution.

**Possible implementation causes:** The preprocessing path may not use the pipeline or descriptor state recorded in the supplied state command buffer correctly. The exact cause requires source and validation investigation.

#### Host result-checking failure

**Possible failure symptoms:** The host reports an output mismatch even though generated work may have completed, or reports a nonzero value for a zero-count case.

**Possible implementation causes:** The result-buffer barrier, host allocation invalidation, initialization, readback, or comparison path may be incorrect. Investigation of the recorded expected values and readback sequence is needed.

## Case Pruning

### Requirement-based pruning

- Every case requires the `VK_EXT_device_generated_commands` compute support checked by `checkDGCComputeAndQueueSupport`.
- Methods other than `universal` require a compute queue. A device without the required compute queue is unsupported for those cases and is skipped through the support check rather than reported as a generated-command failure.
- The EXT preprocessing path must support the explicit-preprocess layout and the memory requirements queried for the selected command information.

### Design-based pruning

- The source registers exactly the 4 × 3 × 2 combinations shown in the hierarchy. No other queue, count, or state combinations are implied by the parameter enums.
- The test uses two sequences so it can preprocess one sequence separately, execute it, and then preprocess plus execute the second sequence in the later submission flow.
- The zero-count cases remain separate registrations because they check the boundary where preprocessing still occurs but counted execution must not change the initialized outputs.

## Key Takeaways

- The test separates explicit preprocessing from execution and checks that `VK_TRUE` execution consumes the prepared state correctly.
- The 24 registered names encode queue method, count-buffer mode, and state command buffer placement without changing the compute shader.
- Count-buffer cases check both a nonzero count and the zero-count boundary. The latter must leave both initialized output buffers at zero.
- Cross-queue methods check ownership and visibility for every buffer used by preprocessing and execution, including the preprocess and count buffers.
- The host-visible output values provide the final contract: `100` and `101` when the generated sequences run, and `0` in the zero-count cases.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter enums and support gate | [Method, StateCmdBuffer, CountBuffer, and `checkDGCComputeAndQueueSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L51-L95) | Defines the three dimensions and the compute-queue requirement. |
| Compute shader generator | [`storePushConstantProgram`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L97-L107) | Defines the shader's push-constant to output-buffer behavior. |
| Resource and generated-command setup | [`parallelPreprocessRun` setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L125-L302) | Creates output, count, generated-command, preprocess, descriptor, pipeline, and command-layout resources. |
| Queue selection and ownership | [`parallelPreprocessRun` queue setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L304-L348) | Maps methods to queues and prepares queue-family barriers. |
| Preprocessing and execution submissions | [`parallelPreprocessRun` submissions](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L349-L494) | Shows state command buffers, fences, barriers, preprocessing, and `VK_TRUE` execution. |
| Result checking | [`parallelPreprocessRun` verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L496-L521) | Defines expected values and the failure result. |
| Registration matrix | [`createDGCComputePreprocessTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L526-L575) | Forms all 4 × 3 × 2 registered test cases. |
| EXT preprocessing semantics | [Vulkan device-generated commands specification](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L1827-L1918) | Defines EXT preprocess-buffer requirements and generated-command execution information. |
| Explicit preprocessing rules | [Vulkan layout usage and processing rules](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L326-L337) | Defines explicit preprocessing and the separate preprocessing operation. |
