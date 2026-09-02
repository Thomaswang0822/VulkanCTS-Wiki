# Understanding Brief: NV compute conditional rendering

## One-Sentence Test Purpose

This test checks whether NV device-generated compute commands obey `VK_EXT_conditional_rendering` when execution and explicit preprocessing use different command-buffer and queue paths.

## Background Knowledge

### Conditional rendering predicate and inversion

`vkCmdBeginConditionalRenderingEXT` reads a 32-bit value from a buffer created with `VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT`. A zero value makes commands in the conditional block inactive; a nonzero value makes them active. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that predicate. Conditional rendering can affect compute dispatches, and an active conditional block in a primary command buffer can affect commands recorded in a secondary command buffer when the secondary inheritance info enables it.

Why it matters here:
- The test uses `0` and `2`, so the true case tests the zero/nonzero rule rather than equality with one.
- The inverted flag must change only the effective predicate. The generated command stream and compute shader remain the same.

### Device-generated compute commands

`VkIndirectCommandsLayoutNV` describes how the device reads a generated command stream. These cases use a push-constant token followed by a dispatch token. `pipeline_token` cases add a pipeline token before them. A sequence count controls how many command sequences the device considers. With a count buffer, `VkGeneratedCommandsInfoNV` advertises 256 potential sequences while the buffer supplies a count of 1; without it, the info directly specifies one sequence.

Why it matters here:
- Count-buffer variants exercise indirect sequence-count handling without changing the one-dispatch result.
- `preprocess` separates generated-state creation from later execution, so conditional rendering must not make preprocessing and execution disagree.

## One Concrete Example

The smallest representative test case is:

```text
dEQP-VK.dgc.nv.compute.conditional_rendering.general.classic_bind_without_count_buffer_condition_true_primary_uq
```

The host writes `2` to the conditional buffer, initializes a one-word output buffer to zero, and places `777` plus dispatch dimensions `(1, 1, 1)` in the generated command stream. The `comp` shader copies its push constant to the output buffer. The non-inverted nonzero predicate permits the generated dispatch, so the expected word is `777`.

## End-to-End Test Flow

```text
[host] choose pipeline binding, count-buffer, predicate, inversion, command-buffer, and queue parameters
[host] create the output, generated-command, predicate, and optional sequence-count buffers
[host] create the compute pipeline or NV indirect pipeline and the push-constant plus dispatch layout
[host] record conditional rendering around generated execution, or around preprocessing and execution
[device] evaluate the predicate and either execute or suppress the generated dispatch
[device] write the push constant to the output buffer when the dispatch runs
[host] wait for completion, invalidate the output allocation, and read the word
[host] compare the word with the logical-xor expectation and decide pass or fail
```

For `preprocess`, the host records `vkCmdPreprocessGeneratedCommandsNV` inside the conditional block, inserts the preprocess-to-execute barrier, and calls `vkCmdExecuteGeneratedCommandsNV` with `isPreprocessed = VK_TRUE`. An `_exec_on_compute` case submits preprocessing on the universal queue, transfers ownership of the relevant buffers, and executes on a compute queue.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The generated `comp` GLSL program launches one invocation and stores `pc.value` in `outputBuffer.value`.
- `VkIndirectCommandsLayoutNV` contains a push-constant token and a dispatch token. `pipeline_token` adds a pipeline token and uses `DGCComputePipeline` for the generated pipeline.
- The generated stream contains the optional pipeline address, `777`, and `VkDispatchIndirectCommand` dimensions `1, 1, 1`.
- `preprocess` sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_NV` and allocates a preprocess buffer for 256 potential sequences while executing one sequence.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `outputBuffer` | yes | yes, as a storage buffer | written by the compute shader | yes | Contains `777` only when the dispatch executes. |
| generated-command buffer | yes | yes | read as an indirect command stream | no | Supplies the push constant and dispatch, plus the optional pipeline token. |
| `conditionBuffer` | yes | yes, as conditional-rendering input | read by conditional rendering | no | Contains `0` or `2`. |
| `sequenceCountBuffer` | optional | yes when selected | read as an indirect sequence count | no | Contains `1` while `infoSequencesCount` remains 256. |
| `PreprocessBuffer` | yes | yes | written during preprocessing and read during execution | no | Holds generated state for explicit preprocessing. |

## What Is Checked

- The host reads one `uint32_t` from `outputBuffer` after queue completion and invalidation.
- The expected value is `777` when `conditionValue != inverted`; otherwise it is `0`.
- A mismatch returns `tcu::TestStatus::fail` with the observed and expected values. A match returns pass.

## Behavior Parameter Identification

> **Behavior parameter:** effective conditional outcome
>
> **Candidate values:** `effective condition true`, `effective condition false`

The outcome is the logical XOR of the source predicate (`condition_true` or `condition_false`) and `inverted_flag`. Other registered dimensions transport that same one-dispatch property through different NV DGC paths.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `effective condition true` | The permitted generated dispatch did not write `777`, which can indicate predicate evaluation, generated-command decoding, pipeline or shader execution, synchronization, queue ownership, or host readback trouble. |
| `effective condition false` | The suppressed generated dispatch wrote a value, or the output was not initialized or read correctly. |

## Important Variations and Special Cases

- `general` varies `classic_bind` and `pipeline_token`, with and without a count buffer, the two predicate values, the inversion flag, primary or secondary command recording, and universal or compute queue submission.
- `secondary_with_inheritance` carries conditional-rendering inheritance information in the secondary command buffer and requires `inheritedConditionalRendering`.
- `_cq` and `_exec_on_compute` select a compute queue. The latter also requires queue-family ownership barriers for preprocessing and execution.
- `preprocess` fixes a normal pipeline, one sequence, and explicit preprocessing. It varies the predicate, inversion, and whether execution moves to the compute queue.
- The preprocess buffer's capacity of 256 is setup capacity, not a second execution count. The count-buffer general cases still execute one sequence because the count buffer contains `1`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structures | [TestParams and ConditionalPreprocessParams](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L55-L77) | Defines the predicate, inversion, count, command-buffer, and queue dimensions. |
| Support checks | [conditional support checks](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L79-L107) | Defines extension, inheritance, DGC, and queue requirements. |
| Conditional predicate setup | [conditional rendering begin](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L138-L153) | Sets the conditional buffer and `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`. |
| General runtime | [conditionalDispatchRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L171-L404) | Builds resources, records generated execution, and checks the output. |
| Preprocess runtime | [conditionalPreprocessRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L406-L611) | Separates preprocessing from execution and handles queue transfer. |
| Registration | [createDGCComputeConditionalTests](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L615-L677) | Generates the two test families and their exact case names. |
| Conditional rendering semantics | [VK_EXT_conditional_rendering](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L45) | Defines conditional dispatch and secondary-command-buffer behavior. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4350-L4453) | Lists the NV registered identifiers. |

## Questions / Risk Points for User Audit

- Is the zero/nonzero predicate and inversion rule clear?
- Is the distinction between a count buffer containing `1` and a preprocess buffer sized for 256 sequences clear?
- Is the universal-queue versus compute-queue flow understandable?
- Does the failure mapping distinguish an effective permitted dispatch from an effective suppressed dispatch?
- Should the final page include every exact mustpass path or only representative paths plus the registration hierarchy?

## Conversion Notes for Final Wiki Rewrite

- Use the effective conditional outcome as the primary behavior axis, with `effective condition true` and `effective condition false` as its values.
- Distill the predicate and DGC explanations into concise `Background Knowledge` bullets. Keep setup and expected values in the runtime and behavior sections.
- Use `dEQP-VK.dgc.nv.compute.conditional_rendering.general.classic_bind_without_count_buffer_condition_true_primary_uq` as the representative shader walkthrough.
- Copy the `### Failure Cause Mapping` table directly into the final page, then write fresh cause-analysis subsections.
- Keep exact NV paths in a dedicated registration or observed-path block, and retain source links in the appendix.
- Generate the SPIR-V subsection from the representative `comp` shader with the local shader-disassembler tools.
