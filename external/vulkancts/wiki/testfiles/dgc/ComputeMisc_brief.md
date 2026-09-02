# Understanding Brief: NV DGC compute miscellaneous tests

## One-Sentence Test Purpose

This test family checks whether NV device-generated compute commands remain correct when many generated sequences are executed, a generated pipeline address is captured and replayed, or a compute pipeline needs implementation-managed scratch space.

## Background Knowledge

### Device-generated commands and preprocessing

A `VkIndirectCommandsLayoutNV` describes how records in an indirect buffer become command tokens such as a pipeline bind, push constant update, or dispatch. For the NV path, the implementation may preprocess those records into a preprocess buffer and then execute the resulting generated commands. The Vulkan device-generated-commands chapter describes preprocessing as a separate logical pipeline and requires the preprocess buffer to be allocated from the queried memory requirements ([generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands)).

Why it matters here:

- `execute_many_*` reuses one large preprocess allocation, but gives each one-sequence execution its own aligned region.
- `full_replay` performs the metadata update and generated dispatch once per iteration while checking that the replayed indirect pipeline address is identical.
- The command stream is an input buffer read by generated-command processing, not a host-side description that bypasses Vulkan command execution.

### Compute queues, secondary command buffers, and visibility

A compute pipeline executes only the compute shader stage ([shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-execution-model)). A command buffer may be submitted through the universal queue or a compute queue; `execute_many_*` also places the generated execution in either a primary or secondary command buffer. After shader writes, the source inserts a compute-to-host memory barrier before reading the host-visible output allocation. Vulkan defines indirect-command reads and shader writes as distinct access types and stages ([synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-access-types)).

Why it matters here:

- Queue selection and command-buffer level are execution-path dimensions, not different shader algorithms.
- A successful host read depends on the submitted command buffer completing and on the shader-write-to-host-read dependency.

### Pipeline capture/replay and scratch storage

The `full_replay` case uses the NV compute-pipeline helper with capture/replay enabled. The first iteration records the indirect device address returned by the generated pipeline; the second creates the pipeline with that address and asserts that the returned address matches. `scratch_space` supplies a deliberately register-heavy direct-SPIR-V compute shader so the DGC compute pipeline's scratch allocation path is exercised. The source comment says the shader's varied inputs and non-uniform control flow are intended to make register spilling likely; that is an implementation stress condition, not a Vulkan API result that the host can query directly.

## One Concrete Example

For `dEQP-VK.dgc.nv.compute.misc.execute_many_64_primary_cmd_compute_queue`, the host creates a 64-element host-visible storage buffer initialized to zero. Each generated record contains one push-constant value followed by `VkDispatchIndirectCommand` dimensions `(1, 1, 1)`. The compute shader launches 64 invocations and performs `atomicAdd` on the selected output element. Each element must therefore become `64`.

For the replay case, the generated stream instead contains a captured pipeline address, a push-constant index, and one dispatch. Two submissions target output indices `0` and `1`; each must become `1`.

## End-to-End Test Flow

```text
1. [host] choose one registered case
2. [host] check NV DGC compute support; require a compute queue for `scratch_space`
3. [host] generate or load the compute shader
4. [host] create the storage buffer, descriptor set, pipeline layout, compute pipeline, and NV indirect-command layout
5. [host] write the generated command stream and flush host-visible allocations
6. [host] query generated-command memory requirements and allocate aligned preprocess storage
7. [host] record primary or secondary command-buffer work
8. [device] preprocess and execute the generated dispatch or dispatches
9. [device] update the storage-buffer outputs through `atomicAdd`, or run the direct-SPIR-V scratch-space shader
10. [host] wait for completion, invalidate the output allocation, and compare every element with its expected value
11. [host] pass only when every checked element matches
```

`full_replay` has a distinct loop: it updates the indirect pipeline metadata, inserts the metadata-to-preprocess barrier, preprocesses and executes one sequence, waits for the queue, then repeats with the captured address. `scratch_space` updates the pipeline metadata on the universal queue and submits the generated dispatch on the compute queue before checking four signed results.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `manyExecutesInitPrograms` emits GLSL 4.60 with `local_size_x = 64`, one storage-buffer declaration, one `uint` push constant, and `atomicAdd` ([vktDGCComputeMiscTests.cpp#L72-L83](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L72-L83)).
- `fullReplayInitPrograms` emits the same shape with `local_size_x = 1` ([vktDGCComputeMiscTests.cpp#L85-L96](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L85-L96)).
- `ScratchSpaceCase::initPrograms` loads the checked-in `ScratchSpace.comp.spvasm` artifact directly ([vktDGCComputeMiscTests.cpp#L494-L502](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L494-L502)).
- NV indirect-command layouts encode push-constant/dispatch tokens for `execute_many_*`, and pipeline/push-constant/dispatch tokens for `full_replay` and `scratch_space` ([vktDGCComputeMiscTests.cpp#L150-L154](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L150-L154), [vktDGCComputeMiscTests.cpp#L344-L350](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L344-L350)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Output storage buffer | Yes | Descriptor binding 0 | Atomic shader writes | Yes | Records one result per generated sequence, or four scratch outputs. |
| Input storage buffer | Yes, `scratch_space` only | Descriptor binding 0 | Scratch shader reads | No | Supplies values used by the register-spilling stress shader. |
| Generated indirect-command buffer | Yes | NV generated-command stream | Generated-command processing reads | No | Supplies push constants, dispatch dimensions, and, where required, the pipeline address. |
| Preprocess buffer | Yes, from queried requirements | NV generated-command execution | Preprocessing writes; execution reads | No | Stores implementation-generated command state. `execute_many_*` partitions it by aligned per-execution offsets. |
| Push constants | Yes | Pipeline layout | Compute shader reads | No | Selects the output-buffer index in the generated GLSL cases. |
| Descriptor set and pipeline layout | Yes | Compute pipeline state | Shader accesses the declared buffers | No | Connects the generated shader to its storage buffers. |

## What Is Checked

- `execute_many_*`: all `executeCount` output entries must equal `64`, the shader's `kManyexecutesLocalInvocations` value.
- `full_replay`: both output entries must equal `1`, and the second pipeline's indirect device address must equal the captured first address.
- `scratch_space`: four signed output entries must equal `{-256, -46, -327, -722}`.
- Any mismatch logs the element or execution index and returns a failing `tcu::TestStatus`; there is no tolerance or partial-pass rule.

## Behavior Parameter Identification

> **Behavior parameter:** test family and execution variant
>
> **Candidate values:** `execute_many_64`, `execute_many_1024`, `execute_many_8192`; primary versus secondary command buffer; compute versus universal queue; `full_replay`; `scratch_space`

The primary behavioral axis is the registered test-family behavior, with the `execute_many_*` queue and command-buffer suffixes acting as execution-path variants. The sequence count changes the number of independently generated and checked executions; command-buffer level and queue selection change submission coverage. `full_replay` and `scratch_space` exercise different DGC mechanisms and therefore remain separate behavior values.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `execute_many_64`, `execute_many_1024`, or `execute_many_8192` | Incorrect generated-command stream interpretation, sequence/preprocess offset handling, repeated execution state, push-constant selection, dispatch execution, or output-buffer synchronization. |
| `execute_many_*` with `primary_cmd` or `secondary_cmd` | Incorrect execution of generated commands in the selected command-buffer level, including secondary-command execution inheritance. |
| `execute_many_*` with `compute_queue` or `universal_queue` | Incorrect compute-queue capability or queue-path handling, or missing synchronization for the selected submission path. |
| `full_replay` | Failure to preserve or reuse the captured indirect pipeline address, incorrect pipeline metadata update, replayed stream interpretation, or output visibility failure. |
| `scratch_space` | Incorrect generated compute-pipeline scratch allocation/use, shader execution, descriptor access, or output visibility. |

## Important Variations and Special Cases

- `executeCount` is exactly `64`, `1024`, or `8192`; the test allocates one output element and one aligned preprocess region per execution.
- The 64-invocation shader increments the selected output element once per invocation. It does not use one dispatch with `executeCount` workgroups; the host executes `executeCount` one-workgroup generated sequences.
- `full_replay` uses `DGCComputePipelineMetaDataPool(..., true)` and `cmdUpdatePipelineIndirectBufferNV` before preprocessing. The address comparison is explicit in the source.
- `scratch_space` uses direct SPIR-V and fixed expected signed values. The source does not provide a portable algebraic derivation for those constants, so the page should describe them as the checked reference outputs rather than infering a formula.
- `checkDGCComputeSupport` is a support gate. Unsupported devices are skipped by the CTS support path, not treated as functional failures ([vktDGCComputeMiscTests.cpp#L62-L70](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L62-L70)).

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| `execute_many_*` parameters and registration | [vktDGCComputeMiscTests.cpp#L53-L83](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L53-L83), [vktDGCComputeMiscTests.cpp#L733-L750](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L733-L750) | Defines counts, queue and command-buffer variants, shader generation, and names. |
| Repeated execution runtime | [vktDGCComputeMiscTests.cpp#L98-L291](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L98-L291) | Builds buffers and streams, partitions preprocess memory, submits, and checks `64`. |
| Replay runtime | [vktDGCComputeMiscTests.cpp#L294-L458](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L294-L458) | Captures/reuses the address and checks two output values. |
| Scratch support, artifact, and setup | [vktDGCComputeMiscTests.cpp#L460-L585](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L460-L585) | Defines the compute-queue gate, direct-SPIR-V input, resources, and DGC pipeline. |
| Scratch submission and checking | [vktDGCComputeMiscTests.cpp#L627-L728](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L627-L728) | Shows metadata update, universal/compute queue split, barrier, and four reference values. |
| NV category registration | [vktDGCTests.cpp#L72-L93](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L72-L93) | Places this group under `dgc.nv.compute.misc`. |
| Mustpass coverage | [dgc.txt#L4480-L4493](../../../mustpass/main/vk-default/dgc.txt#L4480-L4493) | Lists all fourteen registered NV miscellaneous cases. |
| DGC specification | [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines indirect layouts, preprocessing, and NV compute constraints. |
| Synchronization specification | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-access-types) | Grounds indirect-command, shader, and host access ordering. |

## Questions / Risk Points for User Audit

- Is the separation between the 12 `execute_many_*` leaves, `full_replay`, and `scratch_space` clear?
- Does the page distinguish the aligned preprocess regions from the generated command stream?
- Is the direct-SPIR-V scratch shader described without claiming that the expected constants have a portable derivation?
- Are queue and command-buffer variants presented as execution coverage rather than separate shader algorithms?

## Conversion Notes for Final Wiki Rewrite

- Use the registered family `misc` as the page scope and show its fourteen direct children in the hierarchy.
- Make `execute_many_*` the representative generated-GLSL walkthrough; summarize the 1024/8192, primary/secondary, and queue variants in tables rather than duplicating shader code.
- Keep `full_replay` and `scratch_space` as separate behavior-parameter subsections with their distinct checks.
- Copy the `### Failure Cause Mapping` table into the final page, then write fresh cause-analysis subsections.
- Mention that `scratch_space` loads direct SPIR-V and has fixed reference outputs; do not fabricate a GLSL reconstruction or SPIR-V assembly.
