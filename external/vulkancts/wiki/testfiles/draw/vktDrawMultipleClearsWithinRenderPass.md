# Multiple Clears Within Render Pass Tests

## Overview

Tests for multiple color and depth clear operations within a single render pass, verifying that sequences of load, clear, and draw operations produce the correct final attachment values. The tests cover various combinations of clear methods, color and depth format pairs, and primitive topologies.

## Role

Validates that `vkCmdClearAttachments` and render pass load operations interact correctly with draw commands within a single render pass. Ensures that multiple clears (via `VK_ATTACHMENT_LOAD_OP_LOAD`, `vkCmdClearAttachments`, and fullscreen draws) produce the expected final color and depth values. Tests that blending is correctly applied when enabled, and that both color-only, depth-only, and combined color+depth attachments behave as specified.

## Source Code

- [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp)

## Registration Hierarchy

```text
draw.renderpass.multiple_clears_within_render_pass
├── clear_clear_c_r8g8b8a8_snorm_big_triangle
├── clear_clear_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── clear_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── clear_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── clear_clear_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── clear_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── clear_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── clear_clear_c_r8g8b8a8_snorm_triangle_strip
├── clear_clear_c_r8g8b8a8_snorm_triangles
├── clear_clear_c_r8g8b8a8_unorm_big_triangle
├── clear_clear_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── clear_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── clear_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── clear_clear_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── clear_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── clear_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── clear_clear_c_r8g8b8a8_unorm_triangle_strip
├── clear_clear_c_r8g8b8a8_unorm_triangles
├── clear_clear_d_d16_unorm_big_triangle
├── clear_clear_d_d16_unorm_triangle_strip
├── clear_clear_d_d16_unorm_triangles
├── clear_clear_d_d32_sfloat_big_triangle
├── clear_clear_d_d32_sfloat_triangle_strip
├── clear_clear_d_d32_sfloat_triangles
├── clear_clear_draw_c_r8g8b8a8_snorm_big_triangle
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── clear_clear_draw_c_r8g8b8a8_snorm_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_snorm_triangles
├── clear_clear_draw_c_r8g8b8a8_unorm_big_triangle
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── clear_clear_draw_c_r8g8b8a8_unorm_triangle_strip
├── clear_clear_draw_c_r8g8b8a8_unorm_triangles
├── clear_clear_draw_d_d16_unorm_big_triangle
├── clear_clear_draw_d_d16_unorm_triangle_strip
├── clear_clear_draw_d_d16_unorm_triangles
├── clear_clear_draw_d_d32_sfloat_big_triangle
├── clear_clear_draw_d_d32_sfloat_triangle_strip
├── clear_clear_draw_d_d32_sfloat_triangles
├── draw_clear_c_r8g8b8a8_snorm_big_triangle
├── draw_clear_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── draw_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── draw_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── draw_clear_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── draw_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── draw_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── draw_clear_c_r8g8b8a8_snorm_triangle_strip
├── draw_clear_c_r8g8b8a8_snorm_triangles
├── draw_clear_c_r8g8b8a8_unorm_big_triangle
├── draw_clear_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── draw_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── draw_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── draw_clear_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── draw_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── draw_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── draw_clear_c_r8g8b8a8_unorm_triangle_strip
├── draw_clear_c_r8g8b8a8_unorm_triangles
├── draw_clear_d_d16_unorm_big_triangle
├── draw_clear_d_d16_unorm_triangle_strip
├── draw_clear_d_d16_unorm_triangles
├── draw_clear_d_d32_sfloat_big_triangle
├── draw_clear_d_d32_sfloat_triangle_strip
├── draw_clear_d_d32_sfloat_triangles
├── draw_clear_draw_c_r8g8b8a8_snorm_big_triangle
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── draw_clear_draw_c_r8g8b8a8_snorm_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_snorm_triangles
├── draw_clear_draw_c_r8g8b8a8_unorm_big_triangle
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── draw_clear_draw_c_r8g8b8a8_unorm_triangle_strip
├── draw_clear_draw_c_r8g8b8a8_unorm_triangles
├── draw_clear_draw_d_d16_unorm_big_triangle
├── draw_clear_draw_d_d16_unorm_triangle_strip
├── draw_clear_draw_d_d16_unorm_triangles
├── draw_clear_draw_d_d32_sfloat_big_triangle
├── draw_clear_draw_d_d32_sfloat_triangle_strip
├── draw_clear_draw_d_d32_sfloat_triangles
├── load_clear_c_r8g8b8a8_snorm_big_triangle
├── load_clear_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── load_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── load_clear_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── load_clear_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── load_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── load_clear_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── load_clear_c_r8g8b8a8_snorm_triangle_strip
├── load_clear_c_r8g8b8a8_snorm_triangles
├── load_clear_c_r8g8b8a8_unorm_big_triangle
├── load_clear_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── load_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── load_clear_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── load_clear_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── load_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── load_clear_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── load_clear_c_r8g8b8a8_unorm_triangle_strip
├── load_clear_c_r8g8b8a8_unorm_triangles
├── load_clear_d_d16_unorm_big_triangle
├── load_clear_d_d16_unorm_triangle_strip
├── load_clear_d_d16_unorm_triangles
├── load_clear_d_d32_sfloat_big_triangle
├── load_clear_d_d32_sfloat_triangle_strip
├── load_clear_d_d32_sfloat_triangles
├── load_clear_draw_c_r8g8b8a8_snorm_big_triangle
├── load_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_big_triangle
├── load_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangle_strip
├── load_clear_draw_c_r8g8b8a8_snorm_d_d16_unorm_triangles
├── load_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_big_triangle
├── load_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangle_strip
├── load_clear_draw_c_r8g8b8a8_snorm_d_d32_sfloat_triangles
├── load_clear_draw_c_r8g8b8a8_snorm_triangle_strip
├── load_clear_draw_c_r8g8b8a8_snorm_triangles
├── load_clear_draw_c_r8g8b8a8_unorm_big_triangle
├── load_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_big_triangle
├── load_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip
├── load_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangles
├── load_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_big_triangle
├── load_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangle_strip
├── load_clear_draw_c_r8g8b8a8_unorm_d_d32_sfloat_triangles
├── load_clear_draw_c_r8g8b8a8_unorm_triangle_strip
├── load_clear_draw_c_r8g8b8a8_unorm_triangles
├── load_clear_draw_d_d16_unorm_big_triangle
├── load_clear_draw_d_d16_unorm_triangle_strip
├── load_clear_draw_d_d16_unorm_triangles
├── load_clear_draw_d_d32_sfloat_big_triangle
├── load_clear_draw_d_d32_sfloat_triangle_strip
└── load_clear_draw_d_d32_sfloat_triangles
```

## Test Families

### load_clear_draw — Load, clear, then draw within a render pass

A three-step sequence within a single render pass: (1) `VK_ATTACHMENT_LOAD_OP_LOAD` with red color and depth 0.7, (2) `vkCmdClearAttachments` to green with depth 0.3, (3) draw with blue (alpha 0.5) and depth 0.9. Blending is enabled. The expected final color is (0.0, 0.5, 0.5, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

### draw_clear_draw — Draw, clear, then draw within a render pass

A three-step sequence: (1) draw with red and depth 0.7, (2) `vkCmdClearAttachments` to green with depth 0.3, (3) draw with blue (alpha 0.5) and depth 0.9. Blending is enabled. The expected final color is (0.0, 0.5, 0.5, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

### clear_clear_draw — Clear, clear, then draw within a render pass

A three-step sequence: (1) `vkCmdClearAttachments` to red with depth 0.7, (2) `vkCmdClearAttachments` to green with depth 0.3, (3) draw with blue (alpha 0.5) and depth 0.9. Blending is enabled. The expected final color is (0.0, 0.5, 0.5, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

### load_clear — Load then clear within a render pass

A two-step sequence: (1) `VK_ATTACHMENT_LOAD_OP_LOAD` with red color and depth 0.3, (2) `vkCmdClearAttachments` to green with depth 0.9. Blending is disabled. The expected final color is (0.0, 1.0, 0.0, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

### draw_clear — Draw then clear within a render pass

A two-step sequence: (1) draw with red and depth 0.3, (2) `vkCmdClearAttachments` to green with depth 0.9. Blending is disabled. The expected final color is (0.0, 1.0, 0.0, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

### clear_clear — Two consecutive clears within a render pass

A two-step sequence: (1) `vkCmdClearAttachments` to red with depth 0.3, (2) `vkCmdClearAttachments` to green with depth 0.9. Blending is disabled. The expected final color is (0.0, 1.0, 0.0, 1.0) and expected depth is 0.9. Parameterized by format pair and topology.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Color format | R8G8B8A8_UNORM, R8G8B8A8_SNORM, undefined | Color attachment format (undefined means depth-only test) |
| Depth format | D32_SFLOAT, D16_UNORM, undefined | Depth attachment format (undefined means color-only test) |
| Format pair | 8 combinations | All valid combinations of color and depth formats (defined at [vktDrawMultipleClearsWithinRenderPass.cpp#L82-L87](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L82-L87)) |
| Topology | TRIANGLE_STRIP, TRIANGLES, TRIANGLE (big triangle) | Primitive topology used for draw steps (defined at [vktDrawMultipleClearsWithinRenderPass.cpp#L120-L125](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L120-L125)) |
| Clear sequence | load_clear_draw, draw_clear_draw, clear_clear_draw, load_clear, draw_clear, clear_clear | Order and type of clear/draw operations |
| Blending | enabled (3-step), disabled (2-step) | Whether alpha blending is enabled in the pipeline |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| Color format image support | When color format is not undefined | [vktDrawMultipleClearsWithinRenderPass.cpp#L779-L787](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L779-L787) |
| `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT` | When color format is not undefined | [vktDrawMultipleClearsWithinRenderPass.cpp#L788-L791](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L788-L791) |
| Depth format image support | When depth format is not undefined | [vktDrawMultipleClearsWithinRenderPass.cpp#L793-L800](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L793-L800) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawMultipleClearsWithinRenderPass.cpp#L803-L804](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L803-L804) |

## Verification Methods

- **Color pixel comparison**: When a color attachment is present, the rendered color image is read back and each pixel is compared against the expected color value. A test fails if any channel difference exceeds `colorEpsilon` (0.01). The comparison is at [vktDrawMultipleClearsWithinRenderPass.cpp#L673-L689](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L673-L689).

- **Depth pixel comparison**: When a depth attachment is present, the rendered depth image is read back and each pixel's depth value is compared against the expected depth. A test fails if the difference exceeds `depthEpsilon` (0.01). The comparison is at [vktDrawMultipleClearsWithinRenderPass.cpp#L691-L716](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L691-L716).

## Notes

- The framebuffer size is 400x300 (defined by `WIDTH` and `HEIGHT` at [vktDrawMultipleClearsWithinRenderPass.cpp#L64-L65](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L64-L65)).
- The fragment shader uses push constants to pass the draw color, allowing different colors per draw step without pipeline changes.
- A separate `frag_depthonly` shader is used for depth-only tests (no color output).
- For dynamic rendering with secondary command buffers, the test count is reduced by only testing `TRIANGLE_STRIP` topology.
- The three-step tests use blending with `VK_BLEND_FACTOR_SRC_ALPHA` / `VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA`, while the two-step tests disable blending entirely.
- The "big triangle" topology uses a single oversized triangle that covers the entire framebuffer, as opposed to the triangle strip or two-triangle approaches.
