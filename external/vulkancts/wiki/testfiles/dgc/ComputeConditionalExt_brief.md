# Understanding Brief: EXT compute conditional rendering

## One-Sentence Test Purpose

This test checks whether EXT device-generated compute dispatches obey a conditional predicate during execution while conditional rendering around preprocessing alone has no effect.

## Background Knowledge

### Conditional rendering predicate and inversion

`vkCmdBeginConditionalRenderingEXT` reads a 32-bit predicate from a buffer. Without `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`, zero suppresses affected commands and any nonzero value permits them. The inverted flag reverses that decision. Conditional rendering affects dispatch commands inside its begin and end commands.

Why it matters here:
- `condition_false` stores `0` and `condition_true` stores `2` or `256`, depending on the test family. Both nonzero values test the zero versus nonzero rule rather than equality with one.
- The expected execution decision is `conditionValue != inverted` unless the conditional block surrounds preprocessing only.

### Explicit preprocessing and state

An EXT indirect commands layout marked with `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` requires `vkCmdPreprocessGeneratedCommandsEXT` before execution with `isPreprocessed = VK_TRUE`. Preprocessing receives a state command buffer. The later execution must use matching compute and conditional state.

Why it matters here:
- `separate_state` records compute state in the execution command buffer and supplies that command buffer as preprocessing state. Without it, the preprocessing command buffer supplies its own state.
- `preprocess_only` puts conditional rendering around `vkCmdPreprocessGeneratedCommandsEXT`, but not around generated-command execution. The predicate must not suppress preprocessing, so the dispatch must still execute.

## One Concrete Example

A representative general case is:

```text
dEQP-VK.dgc.ext.compute.conditional_rendering.general.classic_bind_without_count_buffer_condition_true_uq
```

The host clears a one-word output buffer, stores `2` in the predicate buffer, and places push constant `777` followed by dispatch dimensions `(1, 1, 1)` in the generated command stream. The non-inverted predicate permits execution. The compute shader copies `777` to the output buffer, which the host then checks.

A contrasting preprocessing case is:

```text
dEQP-VK.dgc.ext.compute.conditional_rendering.preprocess.condition_false_preprocess_only_separate_state
```

Here the zero predicate surrounds preprocessing only. Execution has no active conditional block, so the dispatch still writes `777`.

## End-to-End Test Flow

```text
1. General path
[host] choose pipeline binding, count-buffer use, predicate value, inversion, and queue
[host] create the output, generated-command, predicate, preprocess, and optional count buffers
[host] build the pipeline, indirect commands layout, and optional indirect execution set
[host] record conditional rendering around vkCmdExecuteGeneratedCommandsEXT
[device] evaluate the predicate and either execute or suppress one generated dispatch
[device] write 777 when the dispatch executes
[host] wait, invalidate the output allocation, and compare the word with 777 or 0

2. Explicit-preprocess path
[host] choose predicate value, inversion, execution queue, state command buffer, and conditional-block placement
[host] record compute state in the preprocessing command buffer or a separate execution command buffer
[host] preprocess on the universal queue and make preprocess writes visible to indirect-command reads
[host] transfer buffer ownership when execution uses the compute queue
[device] execute the preprocessed dispatch with isPreprocessed set to VK_TRUE
[host] read the output and expect the predicate result, or always 777 for preprocess_only
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The generated `comp` shader uses one invocation and stores `pc.value` in `outputBuffer.value`.
- The general indirect commands layout contains push-constant and dispatch tokens. `pipeline_token` prepends a compute-pipeline token and supplies the pipeline through an indirect execution set.
- The explicit-preprocess layout contains push-constant and dispatch tokens and sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`.
- Each generated stream carries `777` and dispatch dimensions `1, 1, 1`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `outputBuffer` | yes | yes, as a storage buffer | written by the compute shader | yes | Remains `0` when execution is suppressed and becomes `777` when the dispatch runs. |
| generated-command buffer | yes | yes | read as token data | no | Supplies the optional pipeline index, push constant, and dispatch dimensions. |
| `conditionBuffer` | yes | yes, as conditional-rendering input | read as a predicate | no | Holds the zero or nonzero value used with the inversion flag. |
| `sequenceCountBuffer` | optional | yes | read as an indirect sequence count | no | Contains `1` while the general command info allows up to 256 sequences. |
| `PreprocessBufferExt` | yes | yes | written by preprocessing and read by execution | no | Holds preprocessed generated-command state. |
| descriptor set and pipeline state | yes | yes | consumed by the dispatch | no | Connects the shader to `outputBuffer` and supplies the compute pipeline. |

## What Is Checked

- The host initializes `outputBuffer` to `0`, waits for submission completion, invalidates the mapped allocation, and reads one `uint32_t`.
- General cases expect `777` when `conditionValue != inverted`; otherwise they expect `0`.
- Explicit-preprocess cases use the same rule when conditional rendering covers execution. A `preprocess_only` case always expects `777` because conditional rendering around preprocessing must not suppress the later dispatch.
- A mismatch returns failure with both expected and observed values. A match returns pass.

## Behavior Parameter Identification

> **Behavior parameter:** conditional execution outcome
>
> **Candidate values:** `effective condition true`, `effective condition false`, `preprocess_only`

`effective condition true` and `effective condition false` come from the predicate and inversion pair. `preprocess_only` is distinct because it removes conditional rendering from execution and checks that preprocessing itself remains unaffected.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `effective condition true` | The permitted dispatch did not write `777`; predicate evaluation, generated-command decoding, pipeline or shader execution, synchronization, queue ownership, or host readback may be wrong. |
| `effective condition false` | A suppressed dispatch changed the output, or output initialization and host readback did not preserve the expected `0`. |
| `preprocess_only` | Conditional rendering incorrectly affected preprocessing, or the separate-state, preprocessed execution, queue-transfer, or result path failed to produce `777`. |

## Important Variations and Special Cases

- `general` registers every combination of `classic_bind` or `pipeline_token`, `with_count_buffer` or `without_count_buffer`, `condition_false` or `condition_true`, optional `inverted_flag`, and `_cq` or `_uq`. This produces 32 test cases.
- A count-buffer case still executes one sequence. The count buffer stores `1`, while `sequencesCount` in the command info is 256 as the upper bound.
- `preprocess` varies the two predicate values, optional inversion, universal or compute execution, same or separate state, and optional `preprocess_only`. The source removes `preprocess_only` when `separate_state` is false, leaving 24 test cases.
- Preprocessing always runs on the universal queue. `_exec_on_compute` executes on the compute queue and adds release and acquire ownership barriers for the output, generated-command, and preprocess buffers.
- The EXT implementation uses an ordinary pipeline or a generated pipeline token. It does not register a shader-object variant in this file.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structures and support | [test parameters and support checks](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L54-L96) | Defines the registered dimensions and feature or queue gates. |
| Predicate setup | [beginConditionalRendering](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L127-L142) | Applies `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` to the predicate buffer. |
| General execution | [conditionalDispatchRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L158-L331) | Builds both binding paths, handles count input, executes conditionally, and checks the result. |
| Explicit preprocessing | [conditionalPreprocessRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L343-L584) | Records state, preprocessing, queue transfer, execution, and the `preprocess_only` expectation. |
| Registration and pruning | [createDGCComputeConditionalTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L589-L647) | Constructs all 56 exact test case leaves and removes the illegal parameter combination. |
| EXT DGC support helper | [checkDGCExtComputeSupport](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L44-L75) | Requires EXT DGC compute support and generated pipeline binding when selected. |
| Conditional rendering semantics | [Conditional Rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#L2086-L2184) | Defines the predicate, inversion, and affected dispatch behavior. |
| Explicit-preprocess matching rules | [generated-command execution validity](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L3037-L3089) | Requires matching preprocessing input, conditional state, descriptors, and compute state. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L1-L56) | Lists the 32 general and 24 preprocess identifiers. |

## Questions / Risk Points for User Audit

- Is the XOR relationship between predicate value and inversion clear?
- Is it clear that the count buffer contains `1` while the advertised upper bound is 256?
- Does the `preprocess_only` explanation make clear why `777` is expected for both predicate values and both inversion settings?
- Is the separate-state and cross-queue timeline specific enough to audit the synchronization behavior?
- The source resolves the inspected risk points; no semantic blocker remains for the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Use conditional execution outcome as the behavior axis, with `effective condition true`, `effective condition false`, and `preprocess_only` as values.
- Preserve the exact name-building order and the 32 plus 24 case counts in the parameter and pruning sections.
- Use the simple `classic_bind_without_count_buffer_condition_true_uq` shader path for one representative walkthrough. Explain other dimensions in the variation table.
- Copy the Failure Cause Mapping table into the final page without changing it.
- Keep the explicit-preprocess state and queue timeline in Runtime Execution and Result Checking. Move source navigation to the appendix.
