# Understanding Brief: conditional_rendering draw

## One-Sentence Test Purpose

This test checks whether Vulkan draw commands execute or become no-ops according to a value in a conditional-rendering buffer across direct, indirect, indexed, and command-buffer-inherited paths.

## Background Knowledge

### Conditional rendering and command-buffer inheritance

`VK_EXT_conditional_rendering` makes draws conditional on a 32-bit value in buffer memory. With the normal flag, a zero value suppresses the commands in the block and a nonzero value permits them. The inverted flag swaps that interpretation. The extension limits the affected commands to draws, compute dispatches, and attachment clears, while copy and blit commands are outside the conditional block's effect. See the [extension description](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L29) and its secondary-command-buffer resolution [at lines 38-45](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L38-L45).

A secondary command buffer can carry conditional-rendering state from its primary command buffer when its inheritance info enables it. This test also records a secondary command buffer inside another secondary command buffer, so the reader must distinguish the command buffer where the conditional block is recorded from the command buffer where the draw is finally executed.

## One Concrete Example

Consider `condition_host_memory_expect_execution.draw`. The host creates a host-visible condition buffer containing `1`, begins conditional rendering in the primary command buffer, and records four direct draws. Each draw covers one horizontal strip of the central part of the target. The vertex shader forwards position and color, and the fragment shader writes the interpolated color. Since the predicate is nonzero and execution is expected, the strips are blue over a black background.

The inverted counterpart uses the same buffer value but sets `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`. It expects the draws to be suppressed, so the central area remains black.

## End-to-End Test Flow

```text
[host] select one ConditionalData row and one of six draw command types
[host] create a condition buffer and write conditionValue at the selected offset
[host] create the color target, graphics pipeline, vertex data, and any indexed or indirect buffers
[host] begin the primary command buffer and render pass
[host] begin conditional rendering in the primary or secondary command buffer, or inherit it into a secondary command buffer
[host] record four draw operations, optionally through a nested secondary command buffer
[host] end conditional rendering and the render pass, then submit and wait
[host] build a reference image with the expected background and central blue or background strips
[host] read the rendered color image and compare it to the reference with a 0.05f fuzzy threshold
[host] report pass only when the image comparison succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test loads `vulkan/dynamic_state/VertexFetch.vert` and `vulkan/dynamic_state/VertexFetch.frag` as the vertex and fragment stages. The test case generator fixes `drawCalls` at `4` and selects one `DrawCommandType` for each condition row. Indexed and indirect command variants add host-filled command buffers; indirect-count variants add a one-element count buffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Conditional buffer | yes | yes, through `VkConditionalRenderingBeginInfoEXT` | read by conditional-rendering execution | no | Supplies the predicate value and tests host-visible or device-local storage. |
| Vertex buffer | yes | yes, at binding 0 | read by the vertex stage | no | Contains four blue central rectangles followed by a red full-target background rectangle. |
| Index buffer | yes, for indexed variants | yes | read by indexed draw commands | no | Reuses the same vertex data with six indices per draw. |
| Indirect buffer | yes, for indirect variants | yes | read by indirect draw commands | no | Holds one valid command followed by two deliberately invalid-position commands for each draw slot. |
| Indirect count buffer | yes, for indirect-count variants | yes | read by the indirect-count command | no | Contains `1`, limiting each count command to the valid command in its three-command stride. |
| Color target image | yes | as the render-pass color attachment | written by rasterization | yes | Records whether the conditional draw operations affected the central area. |

The condition buffer is host-visible for `*_host_memory` rows. For `*_local_memory` rows, the utility stages the same bytes through a host-visible buffer, copies them to a device-local buffer, and uses the latter for conditional rendering. `padConditionValue` and `allocationOffset` are available fields in `ConditionalData`, but the draw table uses them as false for every row.

## What Is Checked

- The background is black for the ordinary render path and white when the render pass clear variant is active.
- The central rectangle area is blue when `expectCommandExecution` is true and has the clear color when it is false.
- The host reads the color target after submission and compares every pixel with the generated reference image using `tcu::fuzzyCompare()` and threshold `0.05f`.
- A command submission that succeeds but produces the wrong image fails the test.

## Behavior Parameter Identification

> **Behavior parameter:** conditional command path, represented by the registered condition-data test family plus its draw-command leaf
>
> **Candidate values:** `expect_execution`, `expect_noop`, `conditionInverted`, primary conditional block, secondary conditional block, inherited conditional state, nested secondary command buffer, `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_indirect_count`, `draw_indexed_indirect_count`

The primary behavioral axis is the condition-data row, because its values select whether rendering is permitted, where the condition is recorded or inherited, and how secondary command buffers participate. The six draw-command leaves extend that behavior to direct, indexed, indirect, and indirect-count execution mechanisms.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `expect_execution` | Conditional rendering incorrectly suppresses an allowed draw, or the selected direct, indexed, indirect, or count command does not execute as recorded. |
| `expect_noop` | Conditional rendering incorrectly executes a suppressed draw, or the image clear and conditional block interaction is wrong. |
| `conditionInverted` | The implementation applies the non-inverted predicate rule when `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` is set. |
| primary conditional block | The primary command buffer does not apply the buffer value and flags to its draw commands. |
| secondary conditional block | The conditional block recorded in a secondary command buffer does not control the draws in that buffer. |
| inherited conditional state | Command-buffer inheritance does not propagate the enabled state required by the selected `VkCommandBufferInheritanceConditionalRenderingInfoEXT`. |
| nested secondary command buffer | Conditional state is lost or applied at the wrong level when a primary command buffer executes a nested secondary command buffer. |
| `draw`, `draw_indexed` | Direct or indexed draw recording, vertex access, or index-buffer binding produces the wrong central image. |
| `draw_indirect`, `draw_indexed_indirect` | Indirect command decoding or conditional suppression allows a deliberately invalid-position command to render or suppresses the valid command. |
| `draw_indirect_count`, `draw_indexed_indirect_count` | The count-command path ignores the conditional state, command stride, or count value. |
| host versus local condition buffer | Conditional-rendering buffer reads or the staging copy expose different predicate values between host-visible and device-local memory. |
| render-pass clear variant | The conditional block does not correctly cover the render-pass begin clear, or the clear color is not preserved for the expected no-op result. |

## Important Variations and Special Cases

- The condition-data formatter emits names from the boolean layout: `condition` or `no_condition`, memory type, secondary-buffer placement, inheritance, expected result, inversion, padding, and render-pass clear. The draw source currently registers only rows from `s_testsData`; in those rows padding and allocation offset remain false.
- The normal draw rows use a legacy render-pass path. Four additional rows set `clearInRenderPass` and use a render pass whose color attachment load operation is `VK_ATTACHMENT_LOAD_OP_CLEAR`; those rows begin conditional rendering before `vk::beginRenderPass()` so the clear itself is tested.
- Indirect buffers repeat `goodCommand badCommand badCommand` for each of four draw slots. The valid command points at the blue rectangle for that slot; the bad commands point after the blue vertices. The count buffer value `1` selects only the valid command in each three-command window.
- The two indirect-count leaves require `VK_KHR_draw_indirect_count`. Inherited conditions recorded outside the secondary command buffer require `VK_KHR_maintenance7`. Nested command-buffer rows require `VK_EXT_nested_command_buffer` with both nested-command-buffer features used by the test.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Draw test registration and six command leaves | [ConditionalDrawTests::init()](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L618-L643) | Creates one condition-data test family and six draw-command leaves per row. |
| Condition-data values and row names | [`ConditionalData` and `s_testsData`](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) | Defines predicate placement, inversion, inheritance, clear, nesting, expected result, and memory variants. |
| Condition buffer construction | [createConditionalRenderingBuffer()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Shows host-visible staging, device-local copies, offsets, and predicate bytes. |
| Conditional block setup | [beginConditionalRendering()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L136) | Maps padding and inversion to `VkConditionalRenderingBeginInfoEXT`. |
| Draw command encoding | [recordDraw()](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L326-L374) | Selects the six direct, indexed, indirect, and count commands. |
| Command-buffer and render-pass control flow | [ConditionalDraw::iterate()](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L376-L559) | Records primary, secondary, inherited, nested, and render-pass-clear paths. |
| Image validation | [ConditionalDraw::iterate()](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L561-L604) | Builds the expected image and performs the fuzzy comparison. |
| Extension semantics | [VK_EXT_conditional_rendering description](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L45) | Grounds the affected-command and secondary-command-buffer behavior. |

## Questions / Risk Points for User Audit

- Is the condition-data row the clearest primary behavioral axis, with the six draw command leaves treated as a second axis?
- Should the final page show one representative vertex and fragment walkthrough, or only the vertex stage because the shader behavior is pass-through and the conditional predicate acts outside shader execution?
- Does the explanation of the indirect buffer's three-command stride make the expected no-op image clear?
- Are the nested secondary command-buffer and render-pass-clear cases distinct enough to keep separate in the final failure analysis?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page focused on conditional command execution. Treat `VertexFetch.vert` and `VertexFetch.frag` as the fixed image-producing shader pair, not as the source of the predicate logic.
- Use the condition-data family as the main behavior axis and describe six draw command leaves in a compact table.
- Preserve the failure mapping table in the final page without changing its rows. Write fresh cause-analysis subsections from the validation logic.
- Use one walkthrough for `dEQP-VK.conditional_rendering.draw.condition_host_memory_expect_execution.draw`, showing both stages because their interface explains the blue central rectangles. Generate the required SPIR-V artifact from the reconstructed vertex shader.
- Distill the background section to conditional rendering and secondary-command-buffer inheritance. Move setup, values, execution, and checks into their dedicated sections.
