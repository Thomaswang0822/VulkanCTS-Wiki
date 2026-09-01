# Understanding Brief: ClearAttachments

## One-Sentence Test Purpose

This test checks whether `vkCmdClearAttachments` executes or is suppressed according to a conditional-rendering value when recorded in primary or secondary command buffers, including inherited and nested secondary paths.

## Background Knowledge

### Conditional rendering around a graphics command

`VK_EXT_conditional_rendering` lets a command buffer conditionally execute rendering commands based on a 32-bit value in a buffer. `vkCmdBeginConditionalRenderingEXT` selects the buffer, byte offset, and optional `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`; commands recorded until `vkCmdEndConditionalRenderingEXT` then either execute or become no-ops according to the value. The extension limits the affected rendering commands to draws, compute dispatches, and attachment clears.

Why it matters here:
- The test places `vkCmdClearAttachments` inside the conditional block and uses a known value, `0` or `1`, so the expected image color is unambiguous.
- An inverted condition swaps which of those values allows the clear to execute.

### Conditional state and secondary command buffers

A secondary command buffer can carry `VkCommandBufferInheritanceConditionalRenderingInfoEXT`. With `conditionalRenderingEnable = VK_TRUE`, the secondary may execute while its primary command buffer has conditional rendering active. The test also places a conditional block inside a secondary command buffer and, for nested cases, executes that secondary through another secondary command buffer.

Why it matters here:
- The same clear must obey the condition whether the conditional block is in the primary, in the secondary, or inherited by the secondary.
- The inherited state is a command-buffer execution rule, not a shader input or a property of the color attachment.

## One Concrete Example

Consider `dEQP-VK.conditional_rendering.clear_attachments.condition_host_memory_expect_execution.clear_attachments`.

- The host-visible conditional buffer contains the 32-bit value `1`.
- The primary command buffer begins conditional rendering without inversion.
- The command buffer records `vkCmdClearAttachments` for the full render area with `drawColor`, which is blue.
- The condition allows the clear, so the host expects the color attachment to be blue after execution.

For the matching `expect_noop` case, the value is `0`. The clear is suppressed, and the attachment remains the black value written during setup.

## End-to-End Test Flow

```text
[host] select one ConditionalData row and skip rows whose clearInRenderPass is true
[host] create a host-visible conditional buffer and write the selected 32-bit value
[host] copy the condition to a device-local buffer when memoryType is LOCAL
[host] create the color attachment, render pass, framebuffer, graphics pipeline, and command buffers
[host] clear the color image to black and insert a transfer-to-color-attachment barrier
[host] begin the render pass and prepare inline, secondary, inherited, or nested command-buffer recording
[host] begin conditional rendering in the selected primary or secondary command buffer when the row requests it
[device] execute or suppress vkCmdClearAttachments according to the selected value and inversion flag
[host] end command buffers and the render pass, submit the primary command buffer, and wait
[host] read the color attachment and compare it with a full-frame blue or black reference
[host] report pass when fuzzyCompare accepts the image, otherwise report fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test loads the fixed `vulkan/dynamic_state/VertexFetch.vert` and `vulkan/dynamic_state/VertexFetch.frag` shaders through the common draw-test pipeline setup. The clear test records no draw, so these shaders are bound pipeline support rather than the behavior under test. The render-pass and framebuffer descriptions are created for one `VK_FORMAT_R8G8B8A8_UNORM` color attachment.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Conditional buffer | Yes | Passed through `VkConditionalRenderingBeginInfoEXT` | Read as the condition value | No | Controls whether the clear executes. It is host-visible for `HOST`, and copied to device-local memory for `LOCAL`. |
| Color target image and view | Yes | Framebuffer color attachment | Cleared to black during setup, then possibly cleared to blue by `vkCmdClearAttachments` | Yes, through `readSurface()` | Carries the externally visible result. |
| Render pass and framebuffer | Yes | Used by the graphics pipeline and render-pass instance | Defines the color attachment and render area | No | Provides the render-pass context required by `vkCmdClearAttachments`. |
| Graphics pipeline | Yes | Bound before the clear command | No draw uses its shader stages | No | Supplies the valid graphics command context; the Vulkan specification says `vkCmdClearAttachments` is not affected by bound pipeline state. |
| Primary, secondary, and nested command buffers | Yes | Submitted or executed with `vkCmdExecuteCommands` | Record conditional state and the clear | No | Exercise primary, secondary, inherited, and nested recording paths. |

## What Is Checked

- Setup clears the entire color image to `clearColor`, which is black.
- The clear command uses `drawColor`, which is blue, and a `VkClearRect` covering `m_renderWidth` by `m_renderHeight` with one layer.
- The host chooses `drawColor` when `expectCommandExecution` is true and `clearColor` otherwise.
- `readSurface()` reads the color target in `VK_IMAGE_LAYOUT_GENERAL` after submission. `tcu::fuzzyCompare()` compares the rendered image with the full-frame reference using a threshold of `0.05f`.

## Behavior Parameter Identification

> **Behavior parameter:** conditional execution context and predicate outcome
>
> **Candidate values:** primary conditional block, secondary conditional block, inherited conditional state, nested secondary execution, no active condition, with execution or no-op outcome

The page treats the condition-data row as the behavioral axis because each registered child selects where conditional state is established, whether the value is inverted, whether command buffers inherit or nest that state, and whether the clear should execute. Memory placement changes how the condition reaches the GPU but does not change the expected image.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Primary conditional block | The primary command buffer did not apply the condition to `vkCmdClearAttachments`, or it applied inversion incorrectly. |
| Secondary conditional block | The secondary command buffer did not apply its own conditional block to the clear, or it ended the block incorrectly. |
| Inherited conditional state | The inherited `conditionalRenderingEnable` state did not match the active primary condition when the secondary executed. |
| Nested secondary execution | Conditional state was not preserved across the nested `vkCmdExecuteCommands` chain. |
| No active condition | The unconditional secondary path changed the clear result or command-buffer execution state. |
| Any context with `expect_execution` or `expect_noop` | The condition buffer value, inversion flag, memory placement, or condition offset was interpreted incorrectly. |

## Important Variations and Special Cases

- `HOST` uses a host-visible buffer with `VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT`. `LOCAL` first writes a host-visible staging buffer, then copies it to a device-local buffer with conditional-rendering and transfer-destination usage.
- The shared table contains rows with `clearInRenderPass = true`, but this page excludes them. The clear-attachments implementation registers only rows with the flag false. Those excluded rows test a render-pass load-clear path rather than `vkCmdClearAttachments`.
- The active condition can be established in the primary command buffer, in the secondary command buffer, or through inheritance. Nested rows execute the clear secondary through a nested secondary command buffer.
- The shared table keeps `padConditionValue` and `allocationOffset` false for this family. The utility still supports those dimensions for other conditional-rendering families.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Condition-data fields and matrix | [ConditionalData and s_testsData](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L38-L144) | Defines the condition location, inversion, inheritance, nesting, expected outcome, and memory dimensions. |
| Capability checks | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) | Requires `VK_EXT_conditional_rendering` and gates inherited and nested command-buffer cases. |
| Conditional buffer creation | [createConditionalRenderingBuffer()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Shows host-visible staging, device-local copying, and the condition buffer usage flags. |
| Conditional begin helper | [beginConditionalRendering()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L135) | Sets the buffer offset and inversion flag. |
| Clear execution and validation | [ConditionalClearAttachmentTest::iterate()](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L92-L254) | Records command buffers, clears the attachment, submits work, and compares the resulting image. |
| Test registration | [ConditionalClearAttachmentTests::init()](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L259-L290) | Skips render-pass-clear rows and registers each remaining condition-data row with a `clear_attachments` test case leaf. |
| Extension semantics | [VK_EXT_conditional_rendering description](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L45) | Defines the affected command classes and primary-to-secondary conditional behavior. |
| Clear command semantics | [vkCmdClearAttachments](../../../../vulkan-docs/src/chapters/clears.adoc#L245-L295) | Defines the render-pass requirement, rasterization-order execution, color attachment writes, and pipeline independence. |
| Inheritance semantics | [VkCommandBufferInheritanceConditionalRenderingInfoEXT](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L1288-L1321) | Defines how an executing secondary interacts with active primary conditional rendering. |

## Questions / Risk Points for User Audit

- Does the page make clear that the bound shaders are pipeline support and are not executed by a draw in this test?
- Is the distinction between a conditional block recorded in a secondary and inherited state from the primary clear?
- Does the `expect_execution` versus `expect_noop` mapping remain clear for inverted conditions?
- Are the device-local copy and the host-visible condition buffer described without implying that the image result comes from shader memory?
- Should the final page show the full 60 registered condition-data children or summarize them by dimensions?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's Background Knowledge limited to conditional rendering state, attachment clearing, and secondary-command-buffer inheritance.
- Make `ConditionalData` the primary behavioral axis and explain its values by execution context, predicate, memory placement, and command-buffer topology.
- Use one representative vertex shader walkthrough only to document the fixed pipeline artifact. State that no draw consumes it, and keep the page's correctness argument in the fixed-function clear and image comparison sections.
- Copy the Failure Cause Mapping table above into the final page unchanged. Write Cause Analysis separately for the predicate, command-buffer context, condition-buffer transport, and image validation mechanisms.
- Keep the complete registration child list in the canonical hierarchy tree so the registration validator can verify every mustpass prefix.
