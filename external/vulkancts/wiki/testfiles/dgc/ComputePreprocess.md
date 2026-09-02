## Overview

**Core question:** Does `VK_NV_device_generated_commands` preprocess and execute generated compute commands correctly across the registered count, queue, and zero-count variants?

- This page covers the implementation and registrations in [`vktDGCComputePreprocessTests.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp), the NV DGC compute-preprocess family.
- The registered test families vary the preprocessing queue, execution queue, execution-count source, and zero-count boundary case.
- Each case prepares generated compute commands, executes the prepared sequence, and checks a host-readable result buffer.
- The page explains the exact registered hierarchy, the parameter dimensions, queue-switch behavior, result checking, pruning, and failure interpretation.

## Background Knowledge

- **Preprocessing and indirect command execution:** Device-generated commands separate preparation of generated commands from their later execution. A preprocess operation prepares state in a preprocess buffer; a later execution operation consumes that state. The execution count may come from the recorded sequence count or a count buffer, making zero a meaningful legal boundary case.
- **Queue submissions and visibility:** Commands submitted to different queues do not become ordered merely because they use related buffers. The synchronization and ownership state established by the test must make the prepared command state and result data visible to the queue that uses or reads them.
- **NV compute device-generated commands:** The compute form requires `VK_NV_device_generated_commands_compute`; its `deviceGeneratedCompute` feature must be enabled. A selected compute queue is also needed when preprocessing or execution uses the compute queue. These support conditions determine whether a case can run before its generated commands are tested.

## Registration Hierarchy

The page covers one implementation-bearing test family with its twelve registered direct children:

```text
dgc.nv.compute.preprocess
├── parallel_preprocessing_compute
├── parallel_preprocessing_compute_with_count_buffer
├── parallel_preprocessing_compute_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_universal_exec
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal
├── parallel_preprocessing_universal_with_compute_exec
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal_with_count_buffer
└── parallel_preprocessing_universal_with_count_buffer_zero_count
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Preprocessing queue | `compute`, `universal` | Selects the queue family used to preprocess the generated command sequence. | [`createComputePreprocessTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) |
| Execution queue | implicit same-queue, `with_compute_exec`, `with_universal_exec` | Selects whether execution stays on the preprocessing queue or switches to the named queue. | [`createComputePreprocessTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) |
| Execution-count source | recorded sequence count, `with_count_buffer` | Chooses between the count recorded for the generated sequence and a GPU-visible count buffer. | [`createComputePreprocessTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) |
| Count value | nonzero, `zero_count` | Distinguishes normal generated execution from the boundary case where the count buffer supplies zero. | [`runComputePreprocessTest`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L430-L491) |
| Registered family | exact names listed above | The source registers selected combinations rather than every possible cross-product. | [`createComputePreprocessTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Its name encodes the preprocessing queue, any queue switch for execution, and whether execution uses a count buffer or its zero value.

### `parallel_preprocessing_compute`: compute preprocessing and execution

Preprocessing and execution use the compute queue path without a count-buffer override. This is the baseline for checking that prepared generated compute commands produce the expected result.

### `parallel_preprocessing_compute_with_count_buffer`: compute preprocessing with a count buffer

The compute preprocessing path uses a count buffer to supply a nonzero execution count. This isolates count-buffer consumption from the zero-count boundary case.

### `parallel_preprocessing_compute_with_count_buffer_zero_count`: compute preprocessing with zero count

The compute preprocessing path uses a count buffer containing zero. The generated sequence must perform no counted execution, and the final result must match the source's zero-count expectation.

### `parallel_preprocessing_compute_with_universal_exec`: compute preprocessing and universal execution

Preprocessing uses the compute queue and execution uses the universal queue. The queue transition must preserve the prepared generated-command state and the expected result.

### `parallel_preprocessing_compute_with_universal_exec_with_count_buffer`: compute preprocessing, universal execution, count buffer

This combines compute-queue preprocessing, universal-queue execution, and a nonzero count-buffer value. It checks both the queue transition and the alternate execution-count source.

### `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count`: compute preprocessing, universal execution, zero count

This is the corresponding queue-switch boundary case. A zero count must suppress counted generated execution while the cross-queue command flow remains valid.

### `parallel_preprocessing_universal`: universal preprocessing and execution

Preprocessing and execution use the universal queue path without a count-buffer override. It provides the baseline for the universal preprocessing route.

### `parallel_preprocessing_universal_with_compute_exec`: universal preprocessing and compute execution

Preprocessing uses the universal queue and execution switches to the compute queue. The prepared sequence must remain usable after the required synchronization.

### `parallel_preprocessing_universal_with_compute_exec_with_count_buffer`: universal preprocessing, compute execution, count buffer

This combines universal-queue preprocessing, compute-queue execution, and a nonzero count buffer. It checks the count source together with the reverse queue transition.

### `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count`: universal preprocessing, compute execution, zero count

This reverse queue-switch case supplies zero through the count buffer. No counted generated work should alter the result, and the queue transition must still complete legally.

### `parallel_preprocessing_universal_with_count_buffer`: universal preprocessing with a count buffer

The universal preprocessing path uses a nonzero count buffer without a separate execution-queue suffix. It checks count-buffer execution on the universal route.

### `parallel_preprocessing_universal_with_count_buffer_zero_count`: universal preprocessing with zero count

The universal path supplies zero from the count buffer. The result check validates the no-generated-work boundary behavior.

## Shader Analysis

The shader is the fixed compute program used to make generated command execution observable. Its code does not select preprocessing, count-buffer, or queue behavior, so one representative walkthrough is sufficient; those dimensions are controlled by host-side command recording and submission.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.preprocess.parallel_preprocessing_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `parallel_preprocessing_compute` | Uses the compute queue for preprocessing and execution without a count-buffer override. |
| Push constant value | The generated command supplies `100` for the first sequence and `101` for the second. |
| Generated command layout | Each sequence contains one push-constant token followed by one indirect dispatch token. |

#### Purpose

The compute shader copies its push-constant value into a storage buffer. The host can therefore determine whether the generated push constant and dispatch executed.

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

- The source builds this shader in `storePushConstantProgram`; the generated command layout supplies the push constant before the indirect dispatch ([shader and layout setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L89-L99)).
- The shader stays unchanged across the twelve registered families. Queue, count-buffer, and zero-count differences occur in command setup and submission, not in shader source ([case registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L504-L531)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Preprocessing and execution queue | The shader code stays fixed. Queue selection changes command pools, submissions, and ownership barriers. | [queue selection and barriers](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L321-L415) |
| Count-buffer mode | The shader code stays fixed. The count source controls whether the generated dispatch runs. | [count-buffer setup and result reference](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L134-L155) |
| Push constant | The shader always copies `pc.value`; the generated command data changes the value per sequence. | [generated command data](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L223-L242) |

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

- The test selects one registered family, resolving its preprocessing queue, execution queue, count-buffer mode, and zero-count mode.
- It creates the generated-command/preprocess storage, an optional count buffer, and a result buffer. The generated command sequence and preprocess operation are recorded for the selected queue path.
- The preprocessing submission prepares the generated sequence. When preprocessing and execution use different queues, the test establishes the synchronization needed before the execution queue consumes the prepared state.
- The execution submission uses either the recorded sequence count or the selected count-buffer value. A zero-count case therefore exercises the legal execution path without counted generated work.
- Executed generated compute commands write the result buffer. The host waits for completion, reads the result buffer, and compares it with the reference values.
- The case passes only when the result comparison matches the expected output for its registered count and queue configuration.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `parallel_preprocessing_compute` | Preprocessing or compute-queue execution does not produce the expected result. |
| `parallel_preprocessing_compute_with_count_buffer` | Count-buffer execution or preprocessing fails for a nonzero count. |
| `parallel_preprocessing_compute_with_count_buffer_zero_count` | Zero count does not suppress generated execution or leaves an unexpected result. |
| `parallel_preprocessing_compute_with_universal_exec` | Compute preprocessing followed by universal-queue execution does not preserve the expected result. |
| `parallel_preprocessing_compute_with_universal_exec_with_count_buffer` | Count-buffer execution across the selected queue path fails for a nonzero count. |
| `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count` | Zero-count execution across the selected queue path behaves incorrectly. |
| `parallel_preprocessing_universal` | Universal-queue preprocessing or execution does not produce the expected result. |
| `parallel_preprocessing_universal_with_compute_exec` | Universal preprocessing followed by compute-queue execution does not preserve the expected result. |
| `parallel_preprocessing_universal_with_compute_exec_with_count_buffer` | Count-buffer execution after universal preprocessing fails for a nonzero count. |
| `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count` | Zero-count execution after universal preprocessing behaves incorrectly. |
| `parallel_preprocessing_universal_with_count_buffer` | Universal-queue count-buffer execution fails for a nonzero count. |
| `parallel_preprocessing_universal_with_count_buffer_zero_count` | Universal-queue zero-count execution behaves incorrectly. |

### Cause Analysis

#### Preprocess or generated-command execution failure

**Possible failure symptoms:** The result buffer differs from the expected values in a baseline or nonzero-count case.

**Possible implementation causes:** Source inspection points to a failure in preparing the generated command state, consuming that state during execution, or executing the generated compute commands. The exact failing layer requires investigation of the reported case and validation data.

#### Count-buffer handling failure

**Possible failure symptoms:** A nonzero count-buffer case executes the wrong number of generated commands or produces a result inconsistent with that count.

**Possible implementation causes:** The implementation may read the count buffer incorrectly, use stale or incorrectly synchronized count data, or apply the execution count incorrectly. The specific cause must be determined from the failing case and implementation diagnostics.

#### Zero-count handling failure

**Possible failure symptoms:** A zero-count case changes the result as if generated commands ran, or does not match the result expected when no counted generated work executes.

**Possible implementation causes:** The execution path may fail to honor a zero count, or the test's count-buffer visibility and result initialization may not be preserved. Source-level investigation is needed to distinguish these possibilities.

#### Queue-switch or visibility failure

**Possible failure symptoms:** A case that changes between compute and universal queues produces a different result from the equivalent same-queue path or cannot consume the prepared sequence correctly.

**Possible implementation causes:** The queue transition may not make preprocess-buffer state visible to execution, or the implementation may mishandle the command-buffer/preprocess constraints for the selected queue arrangement. The exact cause requires investigation rather than a preconceived hardware, driver, or host attribution.

#### Host result-checking failure

**Possible failure symptoms:** The host reports a mismatch even though the generated work may have completed, or reports an unexpected result for the zero-count initialization state.

**Possible implementation causes:** The result-buffer synchronization, copyback/read, initialization, or comparison path may be incorrect. Source-level investigation of the recorded expected values and readback sequence is needed.

## Case Pruning

### Requirement-based pruning

- The test requires the Vulkan device-generated-commands functionality and the queue capabilities needed by the selected compute and universal paths.
- Cases are subject to the device-generated-commands preprocessing and execution requirements checked by the implementation. Unsupported queue, feature, or limit configurations are skipped rather than treated as execution failures.

### Design-based pruning

- Only the twelve explicitly registered family names are cases; unregistered combinations of preprocessing queue, execution queue, count source, and count value are not inferred as missing tests.
- The zero-count variants are kept as dedicated boundary cases instead of being folded into the nonzero count-buffer variants.

## Key Takeaways

- The family tests prepared device-generated compute commands, not just direct compute dispatch.
- The registered names explicitly distinguish preprocessing queue, execution queue, count-buffer source, and zero-count behavior.
- Count-buffer variants test execution-count consumption; their `zero_count` counterparts test that the boundary value suppresses counted generated work while the command flow remains valid.
- Queue-switch variants test the visibility and usability of preprocessed state when preprocessing and execution use different queues.
- The host-readable result buffer is the final observable contract: a mismatch identifies a failure in the selected preprocessing, count, queue, execution, synchronization, or result-checking path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and case construction | [`createComputePreprocessTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) | Defines the exact registered families and their parameter combinations. |
| Execution and result verification | [`parallelPreprocessRun`](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L119-L492) | Shows command execution, count handling, and host-side result checking. |
| DGC helper behavior | [device-generated-commands helpers](../../../modules/vulkan/device_generated_commands/) | Provides the helper implementation used by the test. |
| DGC specification | [Device-Generated Commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc) | Defines preprocessing and generated-command execution semantics. |
