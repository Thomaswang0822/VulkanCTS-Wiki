# Understanding Brief: ScissorTests

## One-Sentence Test Purpose

This test verifies that Vulkan static and dynamic scissor rectangles clip draw and clear commands exactly as modeled, including empty, out-of-bounds, multi-viewport, update-order, large-integer, and framebuffer-border cases.

## Background Knowledge

- A scissor rectangle discards fragments outside its integer region; effective coverage is also bounded by the viewport and framebuffer.
- Static scissors are pipeline viewport state. Dynamic scissors are changed during command recording with `vkCmdSetScissor(firstScissor, scissorCount, ...)`.
- Multiple scissors require matching viewport slots. The generated geometry shader emits the same triangle for each invocation and selects `gl_ViewportIndex = gl_InvocationID`.
- `vkCmdDraw` and `vkCmdClearAttachments` are different command paths. The source's reference model treats `RectClearTestCommand` as unscissored (`isScissored() == false`) while iterating active rectangles, so documentation must preserve that implementation detail rather than assume draw semantics.

## One Concrete Example

`dynamic_scissor_out_of_order_updates` first sets scissor slots 2, 1, and 0 separately, draws a red large quad, shifts every rectangle by 20 pixels in x, then updates slots 1, 0, and 2 in a different order before drawing green. This isolates both `firstScissor` slot addressing and the requirement that updates affect later commands rather than earlier ones. ([registration](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L920-L949))

## End-to-End Test Flow

1. The draw suite places the factory under `draw.renderpass.scissor`; it also reuses the factory under eligible dynamic-rendering command-buffer groups.
2. `createTests` registers 22 exact case names, covering static/dynamic state, one/two/three/16 rectangles, empty and boundary rectangles, draws, clears, and mixed updates.
3. Support checks require `VK_KHR_dynamic_rendering` for dynamic rendering, and geometry-shader plus multi-viewport core features when more than one scissor is used.
4. The instance creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` target, pass-through shaders/pipeline, vertex data for quad draws, and either a render pass/framebuffer or dynamic-rendering scope. Border cases use a 127x127 framebuffer/render area.
5. It clears the target, records the ordered draw/clear command list, applies dynamic updates at their recorded positions, submits with `submitCommandsAndWait`, transitions for transfer, and reads the image back.
6. The reference starts black and applies the same ordered operations. `scissorQuad` intersects draw rectangles with each scissor and framebuffer; clear-command rectangles are evaluated for each active scissor slot.
7. `intThresholdCompare` compares the reference and readback using `UVec4(0)`. Any mismatch returns `QP_TEST_RESULT_FAIL`.

## Generated Artifacts and Bound Resources

| Artifact/resource | Role |
|---|---|
| GLSL 430 vertex shader | Passes position/color to the pipeline. |
| Optional GLSL 430 geometry shader | Broadcasts one triangle to all viewport/scissor indices for multi-scissor cases. |
| GLSL 430 fragment shader | Writes the interpolated color. |
| Host-visible vertex buffer | Stores generated quad vertices for all draw commands. |
| Color target image/view | Receives draw and clear results and is read back for comparison. |
| Render pass/framebuffer or dynamic-rendering state | Defines the color attachment scope selected by shared `GroupParams`. |
| Command pool and primary/optional secondary buffers | Record the ordered state updates and workloads. |

## What Is Checked

The checked artifact is the complete final RGBA image, not an intermediate scissor value. The software model clips each draw quad with rectangle and framebuffer bounds, applies operations in order, and compares every channel with zero integer threshold. This catches incorrect static state, dynamic updates, viewport-slot selection, multi-viewport broadcast, clear clipping, boundary arithmetic, rendering scope, and image transfer.

## Behavior Parameters

- `static_scissor_two_quads`, `static_scissor_two_clears`, `dynamic_scissor_two_quads`, `dynamic_scissor_two_clears`: one inset scissor over two commands.
- `two_static_scissors_one_quad`, `16_static_scissors`, `16_dynamic_scissors`: multiple viewport/scissor slots and geometry broadcast.
- `empty_static_scissor`, `empty_dynamic_scissor_first_draw`: zero-area coverage and a later non-empty dynamic update.
- `*_partially_outside_viewport`, `*_outside_viewport`, `*_viewport_border`, `*_max_int32`: intersection, no intersection, touching edge, and `INT32_MAX` arithmetic.
- `dynamic_scissor_updates_between_draws`, `dynamic_scissor_out_of_order_updates`, `dynamic_scissor_mix`: state lifetime, slot order, and draw/clear interaction.
- `*_framebuffer_border_in`: one-pixel-inside clipping against a 127x127 framebuffer.

## What Failure Means

| Failing behavior | Main areas implicated |
|---|---|
| Static cases | Pipeline scissor state, viewport state, rasterization, or framebuffer clipping. |
| Dynamic cases | `vkCmdSetScissor`, update timing, `firstScissor` addressing, or dynamic pipeline state. |
| Multiple-scissor cases | Geometry shader invocations, `gl_ViewportIndex`, multi-viewport limits, or per-slot scissor state. |
| Clear cases | `vkCmdClearAttachments` scissor interaction or render-pass command semantics. |
| Max-int32/border cases | Signed offset/extent arithmetic or off-by-one intersection behavior. |
| All cases | Attachment setup, layout transition, queue submission, readback, or comparison path. |

Missing required functionality is an unsupported case, not evidence of a failed image comparison.

## Important Variations and Source Map

- Exact registration and workload values: [`createTests`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L761-L1074)
- Scissor intersection model: [`scissorQuad`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L73-L90)
- Dynamic state updates: [`DynamicScissorTestCommand`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L230-L272)
- Support and shader setup: [`ScissorTestCase`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L333-L415)
- Execution/readback/reference/compare: [`ScissorTestInstance::iterate`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L422-L704)
- Suite placement and rendering variants: [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198)

## Audit Risks

- Do not treat the legacy `vktDrawScissorTests.md` prose as the registration source; the C++ `addChild` calls are authoritative.
- Do not collapse dynamic-rendering variants into new case names: the shared draw hierarchy supplies those prefixes.
- Do not describe a clear command as a draw; the source uses `vkCmdClearAttachments` and models its clipping separately.
- Do not call a missing feature a test failure; `checkSupport` rejects unsupported configurations before execution.
