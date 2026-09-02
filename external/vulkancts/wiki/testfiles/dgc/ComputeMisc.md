## Overview

**Core question:** Does NV device-generated compute command execution preserve correctness across repeated sequences, pipeline replay, and scratch-space use?

- [`vktDGCComputeMiscTests.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L53-L83) generates and implements the `dgc.nv.compute.misc` test family.
- The family covers twelve `execute_many_*` variants, `full_replay`, and `scratch_space`.
- The tests exercise repeated one-sequence executions, capture/replay of an indirect pipeline address, and a register-heavy direct-SPIR-V compute pipeline.
- This page documents the registered matrix, generated shader, command-stream and preprocess handling, result checks, and failure meaning.

## Background Knowledge

- NV device-generated commands interpret indirect command records through a `VkIndirectCommandsLayoutNV`. The layout can provide a pipeline, push constants, and dispatch arguments; preprocessing stores implementation-generated command state in a preprocess buffer ([device-generated commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands)).
- A secondary command buffer records work for execution by a primary command buffer. A compute queue and a universal queue provide different submission paths for the same compute stage ([shader execution model](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-execution-model)).
- A shader write becomes host-readable only after completion and an appropriate memory dependency. The source uses a compute-shader to host memory barrier before invalidating and reading the output allocation ([synchronization access types](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-access-types)).
- Pipeline capture/replay preserves an implementation-provided indirect device address across pipeline creation. The scratch-space case stresses the pipeline's implementation-managed temporary storage with a deliberately register-heavy shader.

## Registration Hierarchy

```text
dgc.nv.compute.misc
├── execute_many_64_primary_cmd_compute_queue
├── execute_many_64_primary_cmd_universal_queue
├── execute_many_64_secondary_cmd_compute_queue
├── execute_many_64_secondary_cmd_universal_queue
├── execute_many_1024_primary_cmd_compute_queue
├── execute_many_1024_primary_cmd_universal_queue
├── execute_many_1024_secondary_cmd_compute_queue
├── execute_many_1024_secondary_cmd_universal_queue
├── execute_many_8192_primary_cmd_compute_queue
├── execute_many_8192_primary_cmd_universal_queue
├── execute_many_8192_secondary_cmd_compute_queue
├── execute_many_8192_secondary_cmd_universal_queue
├── full_replay
└── scratch_space
```

The category root is attached by [`createTests()`](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L72-L93). The fourteen direct children are created by [`createDGCComputeMiscTests()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L733-L757) and listed in [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4480-L4493).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution count | `64`, `1024`, `8192` | Selects how many independently generated one-sequence executions update separate output elements. | [`createDGCComputeMiscTests()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L739-L750) |
| Command-buffer level | `primary_cmd`, `secondary_cmd` | Selects whether generated work is recorded directly in the submitted primary command buffer or in a secondary command buffer executed by it. | [`ManyExecutesParams`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L55-L60), [`manyExecutesRun()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L209-L268) |
| Queue path | `compute_queue`, `universal_queue` | Selects the queue family and queue used for submission. | [`manyExecutesRun()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L98-L105) |
| Independent mechanism | `full_replay`, `scratch_space` | Exercises pipeline-address capture/replay or the scratch allocation path rather than repeated execution. | [`createDGCComputeMiscTests()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L752-L755) |

## Behavior Parameters

The primary behavioral axis is the registered test-family behavior. The `execute_many_*` suffixes vary execution coverage; `full_replay` and `scratch_space` select distinct DGC mechanisms.

### `execute_many_*`: repeated generated execution

Each sequence supplies a push-constant output index and `(1, 1, 1)` dispatch dimensions. The 64-invocation shader atomically increments the selected output element, so each element must reach `64`. The count, queue, and command-buffer suffixes change execution coverage, not shader logic.

### `full_replay`: captured pipeline address

The test submits two iterations. The first stores the generated pipeline's indirect device address; the second recreates the pipeline with that address and checks that the address matches before executing a dispatch targeting the second output element.

### `scratch_space`: register-spilling stress

The test loads `ScratchSpace.comp.spvasm` directly and creates a DGC compute pipeline from it. Its varied inputs and non-uniform control flow are intended to make register spilling likely, exercising scratch storage; the four signed output values are fixed source-defined references.

## Shader Analysis

The generated GLSL for `execute_many_*` is part of the tested data path. One representative walkthrough covers the shared shader; `full_replay` uses the same interface with a one-invocation workgroup, while `scratch_space` uses direct SPIR-V and is summarized in the behavior section.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.misc.execute_many_64_primary_cmd_compute_queue
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `execute_many_64` | Runs 64 generated one-workgroup sequences and checks 64 output elements. |
| `primary_cmd_compute_queue` | Records generated execution in a primary command buffer and submits it through the compute queue; the shader is unchanged by this choice. |
| `valueIndex` | The generated push-constant token selects which output element this sequence updates. |

#### Purpose

This shader checks that each generated sequence supplies its push constant and dispatch correctly, and that all 64 local invocations contribute to the selected storage-buffer element.

#### Structural Design

| Shader phase | Operation | Result |
|--------------|-----------|--------|
| Interface | Declare a compute workgroup of `64`, one storage buffer, and one `uint` push constant. | The host can select an output element for each sequence. |
| Device update | Execute `atomicAdd(outputBuffer.values[pc.valueIndex], 1u)` once per invocation. | Each selected element receives 64 atomic increments. |
| Host validation | Read back all output elements after the barrier. | Every element must equal `64`. |

#### Shader Code

```glsl
#version 460
/// One generated dispatch launches one workgroup with 64 local invocations.
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
/// Binding 0 is the host-created storage buffer with one uint result per generated sequence.
layout (set=0, binding=0, std430) buffer OutputBlock { uint values[]; } outputBuffer;
/// The generated push-constant token selects the output element for this sequence.
layout (push_constant, std430) uniform PushConstantBlock { uint valueIndex; } pc;
/// Every invocation contributes one atomic increment to the selected result.
void main (void) { atomicAdd(outputBuffer.values[pc.valueIndex], 1u); }
```

#### Additional Info

- `manyExecutesInitPrograms()` emits this shader with `#version 460`; `fullReplayInitPrograms()` emits the same interface with `local_size_x=1` ([shader generators](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L72-L96)).
- The host executes one sequence at a time and uses a separate aligned preprocess region for each execution; the command stream and preprocess storage are distinct resources.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `execute_many_64`, `execute_many_1024`, `execute_many_8192` | Changes the number of output elements and generated sequences, but not the shader source. | [`createDGCComputeMiscTests()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L739-L750) |
| `primary_cmd`, `secondary_cmd` | Changes command-buffer recording and inheritance; the compute interface and shader operations stay fixed. | [`manyExecutesRun()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L209-L268) |
| `compute_queue`, `universal_queue` | Changes the submission queue and family; the compute shader stays fixed. | [`manyExecutesRun()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L98-L105) |

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
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "values"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "valueIndex"
               OpName %pc "pc"
               OpDecorate %_runtimearr_uint ArrayStride 4
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
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
     %v3uint = OpTypeVector %uint 3
    %uint_64 = OpConstant %uint 64
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0 %18
         %23 = OpAtomicIAdd %uint %20 %uint_1 %uint_0 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `execute_many_*` creates a zeroed host-visible storage buffer with `executeCount` `uint` elements, binds it at descriptor binding `0`, and builds the compute pipeline and push-constant-aware indirect layout.
- The generated command stream contains, for each sequence, one output index followed by dispatch dimensions `(1, 1, 1)`. The host flushes it and selects its per-sequence stream offset.
- The source queries generated-command memory requirements, rounds the required preprocess size up to `minIndirectCommandsBufferOffsetAlignment`, and allocates one such region per execution.
- The command buffer binds the descriptor set and pipeline, records one generated sequence per loop iteration, then inserts a compute-shader-to-host-read barrier, submits the command buffer once, and waits. Secondary cases execute the recorded secondary command buffer from a primary buffer.
- The host invalidates the output allocation and checks every element against `64`; any mismatch logs its execution index and fails the case.
- `full_replay` updates pipeline metadata, inserts the metadata-to-preprocess barrier, executes one sequence per submission, and repeats with the captured address. Both output entries must equal `1` ([`fullReplayRun()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L294-L458)).
- `scratch_space` updates metadata on the universal queue, submits generated execution on the compute queue, then checks `{-256, -46, -327, -722}` ([`ScratchSpaceInstance::iterate()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L627-L728)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `execute_many_64`, `execute_many_1024`, or `execute_many_8192` | Incorrect generated-command stream interpretation, sequence/preprocess offset handling, repeated execution state, push-constant selection, dispatch execution, or output-buffer synchronization. |
| `execute_many_*` with `primary_cmd` or `secondary_cmd` | Incorrect execution of generated commands in the selected command-buffer level, including secondary-command execution inheritance. |
| `execute_many_*` with `compute_queue` or `universal_queue` | Incorrect compute-queue capability or queue-path handling, or missing synchronization for the selected submission path. |
| `full_replay` | Failure to preserve or reuse the captured indirect pipeline address, incorrect pipeline metadata update, replayed stream interpretation, or output visibility failure. |
| `scratch_space` | Incorrect generated compute-pipeline scratch allocation/use, shader execution, descriptor access, or output visibility. |

### Cause Analysis

#### Repeated generated execution

**Possible failure symptoms:** One or more output elements differ from `64`; the log identifies the execution index and observed value.

**Possible implementation causes:** The implementation may mishandle the generated stream offset, the aligned preprocess region, repeated execution state, push-constant data, dispatch execution, or the shader-write to host-read dependency. The source and synchronization specification establish these as the relevant stages and accesses; a more specific fault location requires investigation.

#### Capture/replay address or metadata

**Possible failure symptoms:** The second pipeline address differs from the captured address, or either output element differs from `1`.

**Possible implementation causes:** Pipeline capture/replay, indirect pipeline metadata update, generated stream interpretation, or completion/visibility handling may be incorrect. The test's explicit address comparison and output scan distinguish these symptoms, but do not identify a single internal cause.

#### Scratch-space execution

**Possible failure symptoms:** One of four signed output values differs from `{-256, -46, -327, -722}`.

**Possible implementation causes:** The generated compute pipeline may allocate or use scratch storage incorrectly, or the direct-SPIR-V shader may execute with incorrect resource access or synchronization. The source does not provide a portable algebraic derivation for the constants, so a more specific cause requires source-level investigation.

## Case Pruning

### Requirement-based pruning

- `manyExecutesCheckSupport()` requires NV DGC compute support. `fullReplayCheckSupport()` additionally requires device-generated compute pipelines and capture/replay support ([support checks](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L62-L70)).
- `scratch_space` requires NV DGC compute support with device-generated compute pipelines supported and a compute queue ([`ScratchSpaceCase::checkSupport()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L488-L492)). Unsupported cases are skipped by CTS support handling.

### Design-based pruning

- The repeated-execution matrix contains only the Cartesian product of `64`, `1024`, and `8192` with primary/secondary recording and compute/universal submission.
- `full_replay` and `scratch_space` are single cases because they test separate mechanisms rather than variants of the repeated-execution shader.
- The page does not treat queue and command-buffer choices as separate shader algorithms: they intentionally reuse the same generated program.

## Key Takeaways

- `execute_many_*` executes one generated sequence at a time, with separate command-stream and aligned preprocess offsets, and requires every selected output element to become `64`.
- `full_replay` checks both the captured indirect pipeline address and the two output values.
- `scratch_space` uses direct SPIR-V to stress implementation-managed scratch storage and compares four fixed signed references.
- Support checks remove unsupported feature or queue configurations; completed cases fail only when their explicit address or output checks mismatch.

## Source Reference Appendix

| Topic | Source link | Why it matters |
|---|---|---|
| Registration and generated GLSL | [`vktDGCComputeMiscTests.cpp#L53-L96`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L53-L96) | Defines parameters, support gates, and generated shader text. |
| Repeated execution | [`vktDGCComputeMiscTests.cpp#L98-L291`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L98-L291) | Builds resources and streams, partitions preprocess memory, submits, and checks `64`. |
| Capture/replay | [`vktDGCComputeMiscTests.cpp#L294-L458`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L294-L458) | Captures and reuses the indirect pipeline address and checks two outputs. |
| Scratch-space case | [`vktDGCComputeMiscTests.cpp#L460-L728`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L460-L728) | Loads direct SPIR-V, submits through two queue paths, and checks four references. |
| Test registration | [`vktDGCComputeMiscTests.cpp#L733-L757`](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L733-L757) | Creates all fourteen direct children under `misc`. |
| Category routing | [`vktDGCTests.cpp#L72-L93`](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L72-L93) | Places the group under `dgc.nv.compute.misc`. |
| Mustpass coverage | [`dgc.txt#L4480-L4493`](../../../mustpass/main/vk-default/dgc.txt#L4480-L4493) | Lists the registered NV miscellaneous cases. |
| DGC semantics | [device-generated commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines indirect layouts, preprocessing, and compute-command requirements. |
| Synchronization semantics | [synchronization access types](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-access-types) | Grounds shader-write and host-read ordering. |
