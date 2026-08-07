## Overview

**Core question:** Do static and dynamic scissor state produce the source-defined clipped draw and clear regions in every supported recording path?

`vktDrawScissorTests.cpp` checks Vulkan scissor state by rendering colored quads and issuing rectangular clears, then comparing the resulting color image with a software-computed image. The same registered cases are instantiated under the draw suite's render-pass and, in non-VulkanSC builds, dynamic-rendering command-recording groups. The core behavioral split is pipeline-defined static scissors versus `vkCmdSetScissor` dynamic scissors.

The implementation uses a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color target. Two border cases use a 127x127 framebuffer/render area while retaining the 256x256 target image and viewport constants; this deliberately exercises clipping at a smaller framebuffer boundary. ([constants](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L49-L53), [instance setup](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L445-L458))

## Background Knowledge

A scissor rectangle is an integer rectangle applied after viewport transformation: fragments outside it are discarded. Its effective region is also bounded by the viewport/framebuffer. A zero extent has no covered pixels, and a rectangle that begins at the viewport's right edge has no intersection with the viewport.

Static scissors are supplied in `VkPipelineViewportStateCreateInfo` when the pipeline is created. Dynamic cases include `VK_DYNAMIC_STATE_SCISSOR` and record `vkCmdSetScissor` calls before the affected draw or clear. With more than one scissor, the pipeline has matching viewport/scissor slots; a geometry shader uses `gl_InvocationID` to broadcast the same primitive to each viewport index. ([pipeline state](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L515-L559), [dynamic command](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L230-L272), [geometry shader](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L385-L406))

## Registration Hierarchy

The draw suite adds `createScissorTests()` beneath its render-pass group. `createScissorTests()` creates the literal `scissor` group. Consequently the render-pass path is rooted at `draw.renderpass.scissor`; the same factory is also called by the primary, partial-secondary, and complete-secondary dynamic-rendering command-buffer groups. The two nested-secondary groups do **not** receive ScissorTests because `vktDrawTests.cpp::createChildren()` skips all draw-test factories when `nestedSecondaryCmdBuffer` is true. ([draw-suite registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L99), [dynamic-rendering group setup](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198), [factory](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L1079-L1082))

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

The names above are copied from the `addChild` calls in [`createTests`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L761-L1074). The dynamic-rendering prefix is supplied by the shared draw-suite hierarchy, not by this file.

## Parameter Dimensions and Observed Values

| Axis | Registered values | Implementation meaning |
|---|---|---|
| Scissor state | static, dynamic | Static rectangles are pipeline state; dynamic rectangles are recorded with `vkCmdSetScissor`. |
| Rectangle count | 1, 2, 3, 16 | Multiple rectangles use one viewport/scissor slot per rectangle and the geometry shader path. Sixteen is the minimum exercised for the multi-viewport case. |
| Rectangle geometry | inset, partially outside, fully outside, border-touching, zero extent, large extent | Exercises intersection, empty coverage, boundary behavior, and `offset + extent = 0x7fffffff`. |
| Command workload | quad draw, rectangular clear, draw/clear mix | `QuadDrawTestCommand` records `vkCmdDraw`; `RectClearTestCommand` records `vkCmdClearAttachments`. |
| Dynamic update order | between draws, reverse slot order, mixed slot updates | Verifies state changes affect later commands and that nonzero `firstScissor` updates address the intended slot. |
| Target size | 256x256; 127x127 border cases | The render area/framebuffer is selected from `TestParams::framebufferSize`. |

The static cases are configured with `TestParams::staticScissors`; dynamic cases derive the required count from the largest `firstScissor + count` in their command list. Missing dynamic slots are initialized as empty rectangles in the reference model as well as in the command-state model. ([parameters/counting](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L274-L301))

## Behavior Parameters

- **`static_scissor_two_quads` / `dynamic_scissor_two_quads`**: draw red and green quads that overlap an inset rectangle. The dynamic case sets the rectangle before the draws.
- **`static_scissor_two_clears` / `dynamic_scissor_two_clears`**: issue two `vkCmdClearAttachments` operations with the test's configured rectangle state, checking rectangular-clear coverage separately from rasterized-draw scissoring. Vulkan clear attachments are clipped by each `VkClearRect` and render area, not by the graphics scissor test.
- **`two_static_scissors_one_quad`**: use two static rectangles and one large quad. The geometry shader broadcasts the primitive to both viewport indices; the reference applies each rectangle in turn.
- **`*_partially_outside_viewport`**: use a rectangle extending beyond the viewport and a quad that also exceeds the target, checking that output remains bounded.
- **`*_outside_viewport`**: place the rectangle wholly beyond the viewport; the colored quad must produce no covered pixels.
- **`*_viewport_border`**: place the rectangle at `x = WIDTH`, exactly touching the right edge without overlapping it.
- **`*_max_int32`**: set offset `(100,100)` and extent `(0x7fffffff - 100, 0x7fffffff - 100)`, testing large rectangle arithmetic without requiring a huge image.
- **`16_static_scissors` / `16_dynamic_scissors`**: configure sixteen slots with incrementally shifted rectangles and broadcast one quad through all slots.
- **`empty_static_scissor`**: use a zero-width, zero-height static rectangle for two draws.
- **`empty_dynamic_scissor_first_draw`**: first set an empty rectangle, draw red, then set an inset rectangle and draw green; this distinguishes stale dynamic state from the intended update.
- **`dynamic_scissor_updates_between_draws`**: set three rectangles, draw red, shift all three in x, update all three, and draw green.
- **`dynamic_scissor_out_of_order_updates`**: set slots 2, 1, and 0 in that order, draw, then update slots 1, 0, and 2 in another order before the second draw.
- **`dynamic_scissor_mix`**: set two rectangles, clear red, draw green, update slot 1, then draw blue and clear yellow. It checks dynamic state across both command types.
- **`*_framebuffer_border_in`**: use size `{WIDTH / 2 - 1, HEIGHT / 2 - 1}` (127x127), rectangle `(1,1,size.width-2,size.height-2)`, and a quad larger than the target to expose one-pixel border errors.

All registrations and exact rectangle values are in [`createTests`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L769-L1074); command implementations are [`QuadDrawTestCommand`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L130-L188) and [`RectClearTestCommand`](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L190-L228).

## Shader Analysis

The geometry shader used by multi-scissor cases broadcasts the primitive to viewport indices. The fragment shader writes the selected color; scissor behavior is fixed-function state rather than shader logic.

## Runtime Execution and Result Checking

1. `ScissorTestCase` records whether the case needs multiple scissors. It requires `VK_KHR_dynamic_rendering` for dynamic-rendering variants and requires core geometry-shader and multi-viewport features for multiple-scissor cases. ([support](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L333-L371))
2. The instance creates command-pool/buffer objects, shader modules, a color image/view, a render pass and framebuffer when using the render-pass path, and a host-visible vertex buffer containing vertices for all quad draws. ([resource setup](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L422-L509))
3. It builds a pass-through vertex/fragment pipeline. A geometry stage is added only for multiple scissors. Static scissors are placed directly in viewport state; dynamic cases use the dynamic scissor state and initialize viewport slots with empty rectangles. ([pipeline creation](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L515-L575))
4. The color image is cleared, the selected render-pass or dynamic-rendering scope is begun, and `drawCommands()` binds the vertex buffer/pipeline and records each test command in order. Secondary-command-buffer variants use the shared `GroupParams` path. The image is transitioned from color-attachment-optimal to transfer-source-optimal, submitted on the universal queue, waited on, and read back. ([record/submit/readback](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L577-L663), [draw loop](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L707-L718))
5. The reference starts black, applies each command's dynamic scissor updates, and processes every active rectangle in command order. Draw commands intersect their quad with the scissor and framebuffer bounds; `RectClearTestCommand` reports `isScissored() == false`, so the reference clears its rectangle without the `scissorQuad` intersection. ([intersection helper](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L73-L90), [reference](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L665-L695))
6. `intThresholdCompare` compares the readback and reference with `UVec4(0)`; a mismatch returns `QP_TEST_RESULT_FAIL`. ([comparison](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L697-L704))

## Failure Meaning

The host clears the image before recording, records all commands in one command buffer (or the selected secondary arrangement), transitions the image for transfer, submits with `submitCommandsAndWait`, and only then reads it. The source contains no test-specific semaphore or fence choreography beyond this helper. The ordered command list is significant: later clears/draws overwrite earlier reference subregions, and dynamic scissor updates apply to subsequent commands.

A failure means the final image differs exactly from the software clipping model. Depending on the case, likely fault domains include static pipeline scissor state, dynamic update handling or `firstScissor` addressing, multi-viewport/geometry broadcast, clear-attachment clipping, viewport/framebuffer intersection, large signed rectangle arithmetic, command-buffer/rendering setup, or image transition/readback. A support failure is not a rendering failure: missing dynamic-rendering, geometry-shader, or multi-viewport functionality causes the case to be unsupported before comparison.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| Static scissor cases | Incorrect pipeline scissor state, viewport intersection, or framebuffer clipping. |
| Dynamic scissor cases | Incorrect `vkCmdSetScissor` state, `firstScissor` addressing, update timing, or dynamic-state enablement. |
| Multiple-scissor cases | Incorrect geometry-shader broadcast, `gl_ViewportIndex` selection, multi-viewport state, or per-slot scissors. |
| Clear and draw/clear-mix cases | Incorrect `VkClearRect` or render-area handling, command ordering, or clear-attachment execution. |
| Empty, outside, border, or max-int32 cases | Incorrect zero-area/intersection rules, framebuffer boundary handling, or signed rectangle arithmetic. |

### Cause Analysis

#### Static and dynamic scissor state

**Possible failure symptoms:** The final image differs only in regions controlled by a static rectangle or by a dynamic update, while unrelated command regions match the reference.

**Possible implementation causes:** The pipeline may apply the wrong static rectangle, or the implementation may mishandle `vkCmdSetScissor`, `firstScissor`, update timing, or dynamic-state enablement. The source-based comparison does not isolate a narrower implementation layer.

#### Multiple viewport and scissor slots

**Possible failure symptoms:** Multi-scissor cases produce incorrect colors or coverage in one or more viewport slots while single-scissor cases pass.

**Possible implementation causes:** The geometry shader, `gl_ViewportIndex`, multi-viewport state, or per-slot scissor state may not route the primitive and rectangles as specified. The failure image cannot distinguish those mechanisms without further investigation.

#### Clear, boundary, and arithmetic behavior

**Possible failure symptoms:** Clear cases, empty/outside rectangles, framebuffer-border cases, or the large-extent case differ from the reference despite ordinary inset draw cases passing.

**Possible implementation causes:** The implementation may apply the wrong `VkClearRect`/render-area clipping, mishandle zero or edge-touching intersections, or overflow signed offset/extent arithmetic. Layout transition, readback, and command ordering remain shared alternatives.

### Source evidence

- [Test command classes and dynamic updates](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L92-L272)
- [Support checks and generated shaders](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L361-L415)
- [Resource, pipeline, and command execution](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L422-L663)
- [Reference generation and comparison](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L665-L704)
- [All case registrations](../../../modules/vulkan/draw/vktDrawScissorTests.cpp#L761-L1074)
- [Public factory declaration](../../../modules/vulkan/draw/vktDrawScissorTests.hpp#L27-L36)
- [Shared draw-suite placement and rendering variants](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L99), [../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198)

## Case Pruning

### Requirement-based pruning

Cases are omitted when the selected dynamic state or device capability is not supported by the implementation.

### Design-based pruning

The dispatcher selects the supported rendering arrangements and excludes paths not registered for this family.

## Key Takeaways

- The page's exact root is `draw.renderpass.scissor`; the factory's `scissor` name is reused under every eligible dynamic-rendering command-buffer group.
- Static and dynamic cases exercise the same clipping contract through different state paths.
- Multiple scissors are genuine multi-viewport tests, not merely repeated single-scissor draws.

## Source Reference Appendix

The implementation and dispatcher references cited above are the authoritative source map for the registered cases and execution paths.
- The oracle is the final color image, compared with zero channel threshold against a source-grounded rectangle model.
