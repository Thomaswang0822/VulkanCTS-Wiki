# Discard Rectangles Tests

## Overview

Tests for the `VK_EXT_discard_rectangles` extension, which provides additional coarse-grained rasterization discard rectangles. These rectangles define areas where fragments are either discarded (exclusive mode) or kept (inclusive mode), applied before the scissor test and after the viewport transform.

## Role

Validates that Vulkan implementations correctly implement discard rectangles in both inclusive and exclusive modes, with both static (pipeline state) and dynamic (`vkCmdSetDiscardRectangleEXT`) discard rectangle specification. Tests also verify the interaction between discard rectangles and scissor rectangles (both static and dynamic). The test renders a full-screen quad with a green color and checks that the discard rectangle logic correctly includes or excludes the specified rectangular regions.

## Source Code

- [vktDrawDiscardRectanglesTests.cpp](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.discard_rectangles
├── inclusive_rect_1
├── inclusive_rect_2
├── inclusive_rect_3
├── inclusive_rect_4
├── inclusive_rect_8
├── inclusive_rect_16
├── exclusive_rect_1
├── exclusive_rect_2
├── exclusive_rect_3
├── exclusive_rect_4
├── exclusive_rect_8
├── exclusive_rect_16
├── scissor_inclusive_rect_1
├── scissor_inclusive_rect_2
├── scissor_inclusive_rect_3
├── scissor_inclusive_rect_4
├── scissor_inclusive_rect_8
├── scissor_inclusive_rect_16
├── scissor_exclusive_rect_1
├── scissor_exclusive_rect_2
├── scissor_exclusive_rect_3
├── scissor_exclusive_rect_4
├── scissor_exclusive_rect_8
├── scissor_exclusive_rect_16
├── dynamic_scissor_inclusive_rect_1
├── dynamic_scissor_inclusive_rect_2
├── dynamic_scissor_inclusive_rect_3
├── dynamic_scissor_inclusive_rect_4
├── dynamic_scissor_inclusive_rect_8
├── dynamic_scissor_inclusive_rect_16
├── dynamic_scissor_exclusive_rect_1
├── dynamic_scissor_exclusive_rect_2
├── dynamic_scissor_exclusive_rect_3
├── dynamic_scissor_exclusive_rect_4
├── dynamic_scissor_exclusive_rect_8
├── dynamic_scissor_exclusive_rect_16
├── dynamic_discard_inclusive_rect_1
├── dynamic_discard_inclusive_rect_2
├── dynamic_discard_inclusive_rect_3
├── dynamic_discard_inclusive_rect_4
├── dynamic_discard_inclusive_rect_8
├── dynamic_discard_inclusive_rect_16
├── dynamic_discard_exclusive_rect_1
├── dynamic_discard_exclusive_rect_2
├── dynamic_discard_exclusive_rect_3
├── dynamic_discard_exclusive_rect_4
├── dynamic_discard_exclusive_rect_8
├── dynamic_discard_exclusive_rect_16
├── dynamic_discard_scissor_inclusive_rect_1
├── dynamic_discard_scissor_inclusive_rect_2
├── dynamic_discard_scissor_inclusive_rect_3
├── dynamic_discard_scissor_inclusive_rect_4
├── dynamic_discard_scissor_inclusive_rect_8
├── dynamic_discard_scissor_inclusive_rect_16
├── dynamic_discard_scissor_exclusive_rect_1
├── dynamic_discard_scissor_exclusive_rect_2
├── dynamic_discard_scissor_exclusive_rect_3
├── dynamic_discard_scissor_exclusive_rect_4
├── dynamic_discard_scissor_exclusive_rect_8
├── dynamic_discard_scissor_exclusive_rect_16
├── dynamic_discard_dynamic_scissor_inclusive_rect_1
├── dynamic_discard_dynamic_scissor_inclusive_rect_2
├── dynamic_discard_dynamic_scissor_inclusive_rect_3
├── dynamic_discard_dynamic_scissor_inclusive_rect_4
├── dynamic_discard_dynamic_scissor_inclusive_rect_8
├── dynamic_discard_dynamic_scissor_inclusive_rect_16
├── dynamic_discard_dynamic_scissor_exclusive_rect_1
├── dynamic_discard_dynamic_scissor_exclusive_rect_2
├── dynamic_discard_dynamic_scissor_exclusive_rect_3
├── dynamic_discard_dynamic_scissor_exclusive_rect_4
├── dynamic_discard_dynamic_scissor_exclusive_rect_8
└── dynamic_discard_dynamic_scissor_exclusive_rect_16
```

## Test Families

### inclusive_rect_* — Inclusive discard rectangle mode

In inclusive mode (`VK_DISCARD_RECTANGLE_MODE_INCLUSIVE_EXT`), fragments inside the discard rectangles are kept and fragments outside are discarded. The test renders a full-screen green quad; only the discard rectangle areas should appear green, with the rest showing the clear color (red). Tests vary the number of discard rectangles from 1 to 16.

### exclusive_rect_* — Exclusive discard rectangle mode

In exclusive mode (`VK_DISCARD_RECTANGLE_MODE_EXCLUSIVE_EXT`), fragments inside the discard rectangles are discarded and fragments outside are kept. The test renders a full-screen green quad; the discard rectangle areas should show the clear color (red), with the rest appearing green. Tests vary the number of discard rectangles from 1 to 16.

### scissor_inclusive_rect_* — Inclusive discard rectangles with static scissor

Tests the interaction between inclusive discard rectangles and a static scissor rectangle. The scissor further clips the rendering area, and the discard rectangles are applied within the scissored region. Both the scissor and discard rectangle constraints must be satisfied.

### scissor_exclusive_rect_* — Exclusive discard rectangles with static scissor

Tests the interaction between exclusive discard rectangles and a static scissor rectangle.

### dynamic_scissor_inclusive_rect_* — Inclusive discard rectangles with dynamic scissor

Same as `scissor_inclusive_rect_*` but the scissor is set dynamically via `vkCmdSetScissor`.

### dynamic_scissor_exclusive_rect_* — Exclusive discard rectangles with dynamic scissor

Same as `scissor_exclusive_rect_*` but the scissor is set dynamically via `vkCmdSetScissor`.

### dynamic_discard_inclusive_rect_* — Dynamic inclusive discard rectangles

Discard rectangles are set dynamically via `vkCmdSetDiscardRectangleEXT` instead of being specified at pipeline creation time. Uses inclusive mode.

### dynamic_discard_exclusive_rect_* — Dynamic exclusive discard rectangles

Discard rectangles are set dynamically via `vkCmdSetDiscardRectangleEXT` in exclusive mode.

### dynamic_discard_scissor_inclusive_rect_* — Dynamic discard rectangles with static scissor (inclusive)

Combines dynamically set discard rectangles with a statically defined scissor in inclusive mode.

### dynamic_discard_scissor_exclusive_rect_* — Dynamic discard rectangles with static scissor (exclusive)

Combines dynamically set discard rectangles with a statically defined scissor in exclusive mode.

### dynamic_discard_dynamic_scissor_inclusive_rect_* — Dynamic discard rectangles with dynamic scissor (inclusive)

Both discard rectangles and scissor are set dynamically. Uses inclusive mode.

### dynamic_discard_dynamic_scissor_exclusive_rect_* — Dynamic discard rectangles with dynamic scissor (exclusive)

Both discard rectangles and scissor are set dynamically. Uses exclusive mode.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Discard rectangle mode | inclusive, exclusive | Whether fragments inside or outside the rectangles are kept |
| Number of rectangles | 1, 2, 3, 4, 8, 16 | Count of discard rectangles active simultaneously |
| Discard rectangle type | static, dynamic | Whether rectangles are set at pipeline creation or via `vkCmdSetDiscardRectangleEXT` |
| Scissor mode | none, static, dynamic | Whether a scissor rectangle is active and how it is set |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_EXT_discard_rectangles` | Always required | [vktDrawDiscardRectanglesTests.cpp#L767](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L767) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawDiscardRectanglesTests.cpp#L768-L769](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L768-L769) |
| `maxDiscardRectangles >= numRectangles` | Implementation must support the requested number of discard rectangles | [vktDrawDiscardRectanglesTests.cpp#L785-L791](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L785-L791) |

## Verification Methods

- **Floating-point threshold comparison**: A reference image is generated in software by `generateReferenceImage()` at [vktDrawDiscardRectanglesTests.cpp#L367-L418](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L367-L418), which applies the same discard rectangle and scissor logic. The rendered output is compared against this reference using `tcu::floatThresholdCompare` with a threshold of 0.02 per channel at [vktDrawDiscardRectanglesTests.cpp#L636-L638](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L636-L638).

## Notes

- The render size is 340x100 pixels at [vktDrawDiscardRectanglesTests.cpp#L465](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L465).
- The clear color is red (1.0, 0.0, 0.0, 1.0) and the drawn color is green (0.0, 1.0, 0.0, 1.0) at [vktDrawDiscardRectanglesTests.cpp#L464](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L464).
- Discard rectangles are evenly distributed across the framebuffer width by `generateDiscardRectangles()` at [vktDrawDiscardRectanglesTests.cpp#L348-L364](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L348-L364).
- The scissor rectangle used in scissor tests is at offset (90, 25) with extent (160, 50) at [vktDrawDiscardRectanglesTests.cpp#L479](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L479).
- The total number of leaf test cases is 72 (2 discard types x 3 scissor modes x 2 discard rectangle modes x 6 rectangle counts).
