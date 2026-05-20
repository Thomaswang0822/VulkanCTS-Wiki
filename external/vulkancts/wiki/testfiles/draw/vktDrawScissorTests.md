# Scissor Tests

## Overview

Tests for Vulkan scissor rectangle functionality, verifying that static and dynamic scissor rectangles correctly clip rendering output. The tests cover single and multiple scissor rectangles, scissor rectangles that extend outside the viewport, empty scissors, and interactions between scissor clipping and draw/clear commands.

## Role

Validates that the Vulkan pipeline correctly applies scissor rectangles to both draw commands (`vkCmdDraw`) and clear commands (`vkCmdClearAttachments`). Ensures that static scissors (set at pipeline creation time) and dynamic scissors (set via `vkCmdSetScissor` at command buffer recording time) produce identical clipping behavior. Tests edge cases such as scissors partially or completely outside the viewport, scissors at viewport borders, scissors with maximum int32 offset+extent, and empty scissors with zero extent.

## Source Code

- [vktDrawScissorTests.cpp](../../../modules/vulkan/draw/vktDrawScissorTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.scissor
├── static_scissor_two_quads
├── static_scissor_two_clears
├── two_static_scissors_one_quad
├── static_scissor_partially_outside_viewport
├── static_scissor_outside_viewport
├── static_scissor_viewport_border
├── static_scissor_max_int32
├── 16_static_scissors
├── empty_static_scissor
├── dynamic_scissor_two_quads
├── empty_dynamic_scissor_first_draw
├── dynamic_scissor_updates_between_draws
├── dynamic_scissor_out_of_order_updates
├── dynamic_scissor_partially_outside_viewport
├── dynamic_scissor_outside_viewport
├── dynamic_scissor_viewport_border
├── dynamic_scissor_max_int32
├── 16_dynamic_scissors
├── dynamic_scissor_two_clears
├── dynamic_scissor_mix
├── static_scissor_framebuffer_border_in
└── dynamic_scissor_framebuffer_border_in
```

## Test Families

### static_scissor_two_quads — Two quad draws clipped by a single static scissor

Two colored quads are drawn with a single static scissor rectangle. Verifies that both quads are correctly clipped to the scissor region. The scissor is inset from the framebuffer edges, and the quads are positioned to overlap the scissor boundary.

### static_scissor_two_clears — Two clear operations clipped by a single static scissor

Two `vkCmdClearAttachments` operations are issued with a single static scissor. Verifies that clear operations respect the scissor rectangle, producing the same clipping as draw commands.

### two_static_scissors_one_quad — One quad drawn with two static scissors

A single full-screen quad is drawn with two static scissors. Uses a geometry shader with multiple invocations to broadcast the triangle to each viewport/scissor. Verifies that the result is the intersection of both scissor regions.

### static_scissor_partially_outside_viewport — Static scissor extending beyond viewport bounds

A static scissor whose extent exceeds the viewport dimensions. Verifies that rendering is clipped to both the scissor and the viewport boundary, with no out-of-bounds rendering.

### static_scissor_outside_viewport — Static scissor completely outside the viewport

A static scissor positioned entirely outside the viewport area. Verifies that no rendering occurs when the scissor does not intersect the viewport.

### static_scissor_viewport_border — Static scissor touching the viewport right border

A static scissor whose left edge is exactly at the viewport right border (offset.x equals viewport width). Verifies that no pixels are rendered when the scissor only touches the border.

### static_scissor_max_int32 — Static scissor with offset+extent at INT32_MAX

A static scissor where offset + extent equals the largest positive int32 value (0x7FFFFFFF). Verifies that the implementation correctly handles large scissor dimensions without overflow.

### 16_static_scissors — Sixteen static scissors (minimum required by multiViewport)

Sixteen static scissors are defined (the minimum number required when the multiViewport feature is supported). A geometry shader with 16 invocations broadcasts the triangle to all viewports. Verifies correct clipping with the maximum guaranteed number of scissors.

### empty_static_scissor — Static scissor with zero extent

A static scissor with zero width and height. Verifies that no rendering occurs when the scissor has an empty area.

### dynamic_scissor_two_quads — Two quad draws clipped by a single dynamic scissor

Equivalent to `static_scissor_two_quads` but uses `vkCmdSetScissor` to set the scissor dynamically. Verifies that dynamic scissors produce the same result as static scissors.

### empty_dynamic_scissor_first_draw — Empty dynamic scissor for the first draw, non-empty for the second

The first draw uses an empty dynamic scissor (zero extent), then the scissor is updated to a non-empty region for the second draw. Verifies that scissor updates between draws take effect correctly.

### dynamic_scissor_updates_between_draws — Three dynamic scissors updated between draws

Three scissors are set dynamically, then updated between two draw calls. Verifies that `vkCmdSetScissor` updates are correctly applied to subsequent draws.

### dynamic_scissor_out_of_order_updates — Dynamic scissors updated out of order

Three scissors are updated in reverse order (scissor 2, then 1, then 0) using `vkCmdSetScissor` with a `firstScissor` parameter. Verifies that out-of-order scissor updates work correctly.

### dynamic_scissor_partially_outside_viewport — Dynamic scissor extending beyond viewport bounds

Dynamic equivalent of `static_scissor_partially_outside_viewport`. Verifies that dynamic scissors are clipped to viewport boundaries.

### dynamic_scissor_outside_viewport — Dynamic scissor completely outside the viewport

Dynamic equivalent of `static_scissor_outside_viewport`. Verifies no rendering when the dynamic scissor is entirely outside the viewport.

### dynamic_scissor_viewport_border — Dynamic scissor touching the viewport right border

Dynamic equivalent of `static_scissor_viewport_border`. Verifies no rendering when the dynamic scissor touches but does not overlap the viewport.

### dynamic_scissor_max_int32 — Dynamic scissor with offset+extent at INT32_MAX

Dynamic equivalent of `static_scissor_max_int32`. Verifies correct handling of large dynamic scissor dimensions.

### 16_dynamic_scissors — Sixteen dynamic scissors (minimum required by multiViewport)

Dynamic equivalent of `16_static_scissors`. Verifies correct clipping with 16 dynamically set scissors.

### dynamic_scissor_two_clears — Two clear operations clipped by a single dynamic scissor

Dynamic equivalent of `static_scissor_two_clears`. Verifies that `vkCmdClearAttachments` respects dynamic scissor rectangles.

### dynamic_scissor_mix — Mixture of draws and clears with dynamic scissor updates

A combination of `vkCmdDraw` and `vkCmdClearAttachments` operations with dynamic scissor updates between them. Tests the interaction between different command types and scissor state changes.

### static_scissor_framebuffer_border_in — Static scissor at framebuffer border (off-by-one inside)

Uses a smaller framebuffer (127x127) with a static scissor inset by one pixel from the border. Verifies correct behavior when the scissor is one pixel inside the framebuffer boundary.

### dynamic_scissor_framebuffer_border_in — Dynamic scissor at framebuffer border (off-by-one inside)

Dynamic equivalent of `static_scissor_framebuffer_border_in`. Verifies correct dynamic scissor behavior at framebuffer boundaries.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Scissor type | static, dynamic | Whether the scissor is set at pipeline creation or via `vkCmdSetScissor` |
| Scissor count | 1, 2, 3, 16 | Number of active scissor rectangles |
| Scissor position | inside, partially outside, completely outside, viewport border, max int32 | Position of the scissor relative to the viewport |
| Scissor extent | normal, zero (empty), max int32 | Size of the scissor rectangle |
| Command type | draw (quad), clear (rect) | The type of rendering command used |
| Command mix | draws only, clears only, mixed | Combination of draw and clear commands |
| Framebuffer size | 256x256, 127x127 | Size of the framebuffer (reduced for border tests) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawScissorTests.cpp#L363-L364](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L363-L364) |
| `geometryShader` feature | When using multiple scissors (>1) | [vktDrawScissorTests.cpp#L367-L368](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L367-L368) |
| `multiViewport` feature | When using multiple scissors (>1) | [vktDrawScissorTests.cpp#L369-L370](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L369-L370) |

## Verification Methods

- **Pixel comparison against software reference**: A reference image is generated by applying the same scissor clipping logic in software (`scissorQuad()` function at [vktDrawScissorTests.cpp#L73-L90](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L73-L90)). The rendered output is compared against this reference using `intThresholdCompare` with a threshold of zero (exact match) at [vktDrawScissorTests.cpp#L700-L702](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L700-L702).

## Notes

- The framebuffer size is 256x256 by default (defined by `WIDTH` and `HEIGHT` constants at [vktDrawScissorTests.cpp#L50-L53](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L50-L53)), except for the `*_framebuffer_border_in` tests which use 127x127.
- Multiple scissors require a geometry shader with invocations equal to the number of scissors, broadcasting the triangle to each viewport index. This is why the `geometryShader` and `multiViewport` features are required for those tests.
- Dynamic scissor tests use `VK_DYNAMIC_STATE_SCISSOR` in the pipeline dynamic state and set the scissor via `vkCmdSetScissor` during command buffer recording.
- The `RectClearTestCommand` tests verify that `vkCmdClearAttachments` also respects scissor rectangles, which is important because clear operations have different clipping semantics than draw operations.
