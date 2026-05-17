# vktDrawNegativeViewportHeightTests.cpp

## Overview

Tests for negative and zero viewport height behavior, as introduced by `VK_KHR_maintenance1`. This file produces three separate top-level test groups that verify correct rendering when the viewport height is negative (causing a Y-flip), zero (producing no visible output), or when the viewport is positioned entirely off-screen.

## Role

Validates that implementations correctly handle non-standard viewport height configurations:

- **Negative viewport height**: A negative height inverts the Y-axis, which reverses the winding order of triangles. The tests verify that front-face / back-face determination and culling behave correctly after the Y-flip.
- **Zero viewport height**: A zero-height viewport should produce no visible fragments. The tests confirm the framebuffer remains in its clear color.
- **Off-screen viewport**: Viewports positioned entirely outside the framebuffer bounds should not produce any visible output. This is tested with both positive and negative viewport heights.

## Source Code

- [vktDrawNegativeViewportHeightTests.cpp](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp)

## Registration Hierarchy

### Group: negative_viewport_height

```text
draw.renderpass.negative_viewport_height
├── front_ccw_cull_none
├── front_ccw_cull_front
├── front_ccw_cull_back
├── front_ccw_cull_both
├── front_cw_cull_none
├── front_cw_cull_front
├── front_cw_cull_back
└── front_cw_cull_both
```

### Group: zero_viewport_height

```text
draw.renderpass.zero_viewport_height
├── front_ccw_cull_none
├── front_ccw_cull_front
├── front_ccw_cull_back
├── front_ccw_cull_both
├── front_cw_cull_none
├── front_cw_cull_front
├── front_cw_cull_back
└── front_cw_cull_both
```

### Group: offscreen_viewport

```text
draw.renderpass.offscreen_viewport
├── x_on_screen_y_off_screen_negative
├── x_on_screen_y_off_screen_negative_negative_height
├── x_on_screen_y_off_screen_positive
├── x_on_screen_y_off_screen_positive_negative_height
├── x_off_screen_negative_y_on_screen
├── x_off_screen_negative_y_on_screen_negative_height
├── x_off_screen_negative_y_off_screen_negative
├── x_off_screen_negative_y_off_screen_negative_negative_height
├── x_off_screen_negative_y_off_screen_positive
├── x_off_screen_negative_y_off_screen_positive_negative_height
├── x_off_screen_positive_y_on_screen
├── x_off_screen_positive_y_on_screen_negative_height
├── x_off_screen_positive_y_off_screen_negative
├── x_off_screen_positive_y_off_screen_negative_negative_height
├── x_off_screen_positive_y_off_screen_positive
└── x_off_screen_positive_y_off_screen_positive_negative_height
```

## Test Families

### front_ccw_cull_* / front_cw_cull_* — Negative/Zero viewport height with face culling combinations

Tests rendering two triangles (one CCW, one CW) with a negative viewport height. The Y-flip reverses winding order: the originally CCW triangle becomes CW and vice versa. Each test varies the front-face orientation (`VK_FRONT_FACE_COUNTER_CLOCKWISE` or `VK_FRONT_FACE_CLOCKWISE`) and cull mode (`VK_CULL_MODE_NONE`, `VK_CULL_MODE_FRONT_BIT`, `VK_CULL_MODE_BACK_BIT`, `VK_CULL_MODE_FRONT_AND_BACK`). The fragment shader colors front-facing triangles white and back-facing triangles gray, allowing visual verification of correct face orientation after the flip.

For the `zero_viewport_height` group, the viewport height is set to zero, so no fragments should be produced and the result image should match the clear color.

**Test class**: [NegativeViewportHeightTest](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L593) / [NegativeViewportHeightTestInstance](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L147)

**Registration**: [populateTestGroup](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L665)

### x_*_y_* — Off-screen viewport rendering

Tests that viewports positioned entirely outside the framebuffer bounds produce no visible fragments. Each test generates a pseudorandom viewport with at least one axis off-screen (negative side or positive side). The viewport is used to render a full-screen quad, but since the viewport is off-screen, the framebuffer should remain in its clear color (black). A subset of tests also use negative viewport height, requiring `VK_KHR_maintenance1`.

**Test class**: [OffScreenViewportCase](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L726) / [OffScreenViewportInstance](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L778)

**Registration**: [createOffScreenViewportTests](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L1016)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| frontFace | `front_ccw`, `front_cw` | VkFrontFace: COUNTER_CLOCKWISE or CLOCKWISE |
| cullMode | `cull_none`, `cull_front`, `cull_back`, `cull_both` | VkCullModeFlagBits: NONE, FRONT_BIT, BACK_BIT, FRONT_AND_BACK |
| zeroViewportHeight | true (zero group), false (negative group) | Whether viewport height is zero vs negative |
| xAxis | ONSCREEN, NEGATIVE_SIDE, POSITIVE_SIDE | X-axis placement of off-screen viewport |
| yAxis | ONSCREEN, NEGATIVE_SIDE, POSITIVE_SIDE | Y-axis placement of off-screen viewport |
| negativeHeight | false, true | Whether the off-screen viewport uses negative height |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_KHR_maintenance1` | Always (negative/zero viewport height groups); when `negativeHeight` is true (offscreen group) | [checkSupport](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L643), [checkSupport](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L804) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [checkSupport](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L645) |

## Verification Methods

| Method | Description | Source |
|--------|-------------|--------|
| Fuzzy image comparison | For negative viewport height: `tcu::fuzzyCompare` with 0.02f threshold against a reference image that accounts for Y-flip and culling | [iterate](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L586) |
| Fuzzy image comparison (empty) | For zero viewport height: `tcu::fuzzyCompare` with 0.02f threshold against the clear color (no geometry should be visible) | [iterate](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L564-L568) |
| Float threshold comparison | For off-screen viewport: `tcu::floatThresholdCompare` with zero threshold against the clear color (framebuffer must remain unchanged) | [iterate](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L994) |

## Notes

- The `negative_viewport_height` and `zero_viewport_height` groups share the same `populateTestGroup` function and the same `NegativeViewportHeightTest` class, differing only in the `zeroViewportHeight` flag in `SubGroupParams`.
- The off-screen viewport tests use a fixed framebuffer size of 32x32 and generate viewport coordinates pseudorandomly from a seeded RNG (seed 1674229780).
- The `OffScreenAxisCase::ONSCREEN` value for one axis is allowed as long as the other axis is off-screen, ensuring at least one dimension places the viewport outside the framebuffer.
