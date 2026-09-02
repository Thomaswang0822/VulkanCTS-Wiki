# Understanding Brief: EXT graphics conditional rendering

## One-Sentence Test Purpose

This test checks whether `VK_EXT_conditional_rendering` correctly suppresses or permits EXT device-generated graphics commands, including commands that were explicitly preprocessed.

## Background Knowledge

### Conditional rendering predicates

`vkCmdBeginConditionalRenderingEXT` reads a 32-bit value from a buffer. A zero value discards affected drawing commands; a nonzero value lets them execute. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision. The predicate buffer is ordinary Vulkan buffer memory with `VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT`, not a shader resource.

Why it matters here:
- The test writes either zero or a nonzero value to the predicate buffer and compares the resulting attachment with the clear color or the fragment shader's push-constant color.
- The predicate is active around `vkCmdExecuteGeneratedCommandsEXT`, and in the preprocess family it is also active around `vkCmdPreprocessGeneratedCommandsEXT`.

### Device-generated graphics commands

An EXT indirect command layout describes a sequence of tokens. These tests use an optional execution-set pipeline token, a push-constant token, and a draw token. The device interprets the generated command stream and produces a full-screen triangle draw. Explicit preprocessing stores device-generated state in a preprocess buffer before a later execution command consumes it.

Why it matters here:
- Conditional rendering must control the generated graphics action, not merely the host recording path.
- Separate preprocessing introduces a second point where the predicate state must be compatible with execution. The Vulkan specification requires the predicate value at preprocessing and execution to match.

## One Concrete Example

Consider `dEQP-VK.dgc.ext.graphics.conditional_rendering.general.classic_bind_without_count_buffer_condition_true`.

The host writes `2` to the conditional-rendering buffer, clears a 1x1 `VK_FORMAT_R8G8B8A8_UNORM` color image to black, and begins conditional rendering without the inverted flag. The generated stream contains a push constant with `pcValue = (0, 0, 1, 1)` and `VkDrawIndirectCommand{3, 1, 0, 0}`. The vertex shader makes a full-screen triangle; the fragment shader copies the push-constant color to `outColor`. Because the predicate is nonzero, the draw executes and the host expects blue.

With `condition_false`, the buffer contains zero and the same draw is discarded, so the expected pixel remains black. Adding `_inverted_flag` swaps those two outcomes.

## End-to-End Test Flow

```text
[host] choose pipeline binding, optional count buffer, predicate value, and inverted flag
[host] require EXT conditional rendering and the DGC graphics support used by the case
[host] create a 1x1 color image, render pass, framebuffer, push-constant pipeline layout, and graphics pipeline
[host] build an indirect command layout with optional execution-set, push-constant, and draw tokens
[host] write the generated command stream and predicate value to device-addressable buffers
[host] optionally create a sequence-count buffer and a preprocess buffer
[host] record conditional rendering around generated-command execution
[device] evaluate the predicate and either discard or execute the generated full-screen draw
[device] run the vertex and fragment shaders when the draw executes
[host] submit and wait, copy the color image to a host-visible buffer, and invalidate the allocation
[host] compare the 1x1 result with blue when the effective predicate is true, otherwise black
```

The `preprocess` family records preprocessing and execution in separate primary command buffers. It places the conditional block around preprocessing, inserts `preprocessToExecuteBarrierExt`, then begins a new render pass and conditional block for `vkCmdExecuteGeneratedCommandsEXT` with `isPreprocessed = VK_TRUE`.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `fullScreenTrianglePrograms` emits a vertex shader that derives positions from `gl_VertexIndex` and a fragment shader that writes the push-constant `vec4 color`.
- The `general` family builds a token stream containing an optional execution-set index, the blue push constant, and `VkDrawIndirectCommand{3, 1, 0, 0}`.
- The `preprocess` family uses the same shader pair and stream, but creates the layout with `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 1x1 color image and its buffer-backed readback | yes | yes | device writes the color attachment; copy writes the buffer | yes | Distinguishes a discarded draw from a blue draw. |
| Conditional-rendering buffer | yes | yes | conditional-rendering logic reads one 32-bit predicate | no | Selects execution or discard, with inversion applied by the begin flags. |
| Generated commands buffer | yes | yes through a device address | command generation reads token data | no | Supplies the push constant, optional execution-set index, and draw command. |
| Preprocess buffer | yes in both paths | yes through a device address | preprocessing writes and execution reads generated state | no | Carries explicit preprocessing output in the `preprocess` family. |
| Sequence-count buffer | yes for `*_with_count_buffer` cases | yes through a device address | command generation reads the sequence count | no | Selects one sequence from the configured maximum of 256. |
| Push constant range | yes in the pipeline layout | yes as pipeline state | fragment shader reads `pc.color` | no | Supplies blue for an executed draw. |

The `general` family configures `potentialSequenceCount = 256` and `actualSequenceCount = 1`. Without a count buffer, the generated-command info uses one sequence. With a count buffer, it advertises 256 possible sequences and the buffer contains one.

## What Is Checked

- The host creates a reference 1x1 image filled with `pcValue` when `conditionValue != inverted`; otherwise it fills the reference with the render-pass clear value.
- `tcu::floatThresholdCompare` compares the copied color buffer against the reference with a zero threshold.
- Any pixel mismatch fails the case with `Unexpected output found in color buffer`.

## Behavior Parameter Identification

> **Behavior parameter:** effective conditional-rendering outcome
>
> **Candidate values:** `execute`, `discard`

`conditionValue` and `inverted` are registered dimensions that jointly select this behavioral axis. `pipelineToken` and `indirectCountBuffer` vary how the generated draw is supplied; the `preprocess` test family varies when generation happens.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `execute` | Predicate evaluation allowed the draw but generated-command execution, pipeline binding, push-constant delivery, shader execution, rendering, or copyback produced the wrong pixel. |
| `discard` | Predicate evaluation or `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` handling failed to suppress the generated draw, or stale attachment data reached the comparison. |

## Important Variations and Special Cases

- `classic_bind` binds the normal graphics pipeline before execution. `pipeline_token` adds an execution-set token and creates the pipeline with `VK_PIPELINE_CREATE_2_INDIRECT_BINDABLE_BIT_EXT`; the effective conditional outcome should remain the same.
- `with_count_buffer` advertises 256 possible sequences while the count buffer selects one. The no-count variant supplies one directly.
- The `preprocess` family checks that conditional rendering does not change preprocessing into an incorrect result. It uses an explicit-preprocess layout, a separate state command buffer, a barrier between preprocessing and execution, and `isPreprocessed = VK_TRUE` during execution.
- The source uses `2` and `512` for nonzero predicate values instead of `1`; both are nonzero under the Vulkan conditional-rendering rule.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader generation | [fullScreenTrianglePrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L94-L127) | Defines the vertex and fragment shader text. |
| General case parameters and registration | [createDGCGraphicsConditionalTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L506-L533) | Defines the four registered dimensions and exact `general` case names. |
| Preprocess registration | [preprocess case registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L535-L549) | Defines the `preprocess` cases. |
| General execution and result check | [conditionalDispatchRun](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L159-L350) | Shows resources, generated tokens, conditional block, submission, and expected color. |
| Preprocess execution and result check | [conditionalPreprocessRun](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L353-L502) | Shows separate preprocessing, barrier, execution, and result check. |
| Conditional rendering semantics | [Vulkan conditional rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#drawing-conditional-rendering) | Defines zero/nonzero predicate behavior and the inverted flag. |
| DGC preprocessing semantics | [EXT generated command preprocessing](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines generated-command stages, preprocessing, and synchronization requirements. |
| DGC helper behavior | [DGC EXT helpers](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.hpp#L199-L327) | Defines the layout-builder, preprocess-buffer, and barrier helpers used by the source. |
| Mustpass coverage | [dgc.txt graphics conditional cases](../../../mustpass/main/vk-default/dgc.txt#L488-L507) | Lists the registered EXT graphics conditional paths. |

## Questions / Risk Points for User Audit

- Does the `execute` versus `discard` axis capture the behavior shared by `general` and `preprocess`?
- Is the distinction between conditional rendering around execution and around explicit preprocessing clear?
- Are the execution-set and sequence-count variants treated as transport variations rather than separate rendering outcomes?
- Does the failure mapping stay tied to the color-buffer comparison instead of assuming a particular driver or hardware fault?

## Conversion Notes for Final Wiki Rewrite

- Distill the predicate and DGC concepts into short page-local prerequisite bullets.
- Use the `general` classic-bind, no-count, true-predicate case as the representative shader walkthrough. The fragment shader carries the tested color to the attachment; the conditional predicate remains host-side state.
- Preserve the exact `execute` and `discard` mapping table in the final page's `### Failure Cause Mapping`.
- Explain the `pipelineToken`, count-buffer, inversion, and explicit-preprocess variants in the parameter and runtime sections rather than adding more shader walkthroughs.
- Keep the Vulkan chapter links as semantic evidence and keep detailed source navigation in the final appendix.
