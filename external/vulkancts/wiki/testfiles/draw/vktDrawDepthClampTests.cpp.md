# Depth Clamp Tests

## Overview

Tests for Vulkan depth clamping functionality, verifying that depth values are correctly clamped to the viewport depth range, that depth bias is properly clamped, and that extensions such as `VK_EXT_depth_range_unrestricted` and `VK_EXT_depth_clamp_control` behave as specified. The tests render a full-screen quad with controlled depth values and compare the resulting depth buffer against expected values.

## Role

Validates that the Vulkan pipeline correctly clamps fragment depth values to the viewport `[minDepth, maxDepth]` range when depth clamping is enabled. Ensures that out-of-range depth inputs (both negative and positive extremes) are clamped to the viewport boundaries. Verifies that depth bias applied via rasterizer state is also subject to clamping. Tests the `VK_EXT_depth_range_unrestricted` extension which allows viewport depth ranges outside `[0, 1]`, and the `VK_EXT_depth_clamp_control` extension which allows user-defined depth clamp ranges that differ from the viewport range. Also tests dynamic depth clamp range state via `vkCmdSetDepthClampRangeEXT`.

## Source Code

- [vktDrawDepthClampTests.cpp](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.depth_clamp
├── d16_unorm
├── d16_unorm_clamp_control_half_viewport_range
├── d16_unorm_clamp_control_half_viewport_range_dynamic
├── d16_unorm_clamp_control_input_negative
├── d16_unorm_clamp_control_input_negative_dynamic
├── d16_unorm_clamp_control_input_positive
├── d16_unorm_clamp_control_input_positive_dynamic
├── d16_unorm_clamp_control_viewport_range
├── d16_unorm_clamp_input_negative
├── d16_unorm_clamp_input_positive
├── d16_unorm_depth_bias_clamp_control_input_negative
├── d16_unorm_depth_bias_clamp_control_input_negative_dynamic
├── d16_unorm_depth_bias_clamp_control_input_positive
├── d16_unorm_depth_bias_clamp_control_input_positive_dynamic
├── d16_unorm_depth_bias_clamp_input_negative
├── d16_unorm_depth_bias_clamp_input_positive
├── d16_unorm_s8_uint
├── d16_unorm_s8_uint_clamp_control_half_viewport_range
├── d16_unorm_s8_uint_clamp_control_half_viewport_range_dynamic
├── d16_unorm_s8_uint_clamp_control_input_negative
├── d16_unorm_s8_uint_clamp_control_input_negative_dynamic
├── d16_unorm_s8_uint_clamp_control_input_positive
├── d16_unorm_s8_uint_clamp_control_input_positive_dynamic
├── d16_unorm_s8_uint_clamp_control_viewport_range
├── d16_unorm_s8_uint_clamp_input_negative
├── d16_unorm_s8_uint_clamp_input_positive
├── d16_unorm_s8_uint_depth_bias_clamp_control_input_negative
├── d16_unorm_s8_uint_depth_bias_clamp_control_input_negative_dynamic
├── d16_unorm_s8_uint_depth_bias_clamp_control_input_positive
├── d16_unorm_s8_uint_depth_bias_clamp_control_input_positive_dynamic
├── d16_unorm_s8_uint_depth_bias_clamp_input_negative
├── d16_unorm_s8_uint_depth_bias_clamp_input_positive
├── d24_unorm_s8_uint
├── d24_unorm_s8_uint_clamp_control_half_viewport_range
├── d24_unorm_s8_uint_clamp_control_half_viewport_range_dynamic
├── d24_unorm_s8_uint_clamp_control_input_negative
├── d24_unorm_s8_uint_clamp_control_input_negative_dynamic
├── d24_unorm_s8_uint_clamp_control_input_positive
├── d24_unorm_s8_uint_clamp_control_input_positive_dynamic
├── d24_unorm_s8_uint_clamp_control_viewport_range
├── d24_unorm_s8_uint_clamp_input_negative
├── d24_unorm_s8_uint_clamp_input_positive
├── d24_unorm_s8_uint_depth_bias_clamp_control_input_negative
├── d24_unorm_s8_uint_depth_bias_clamp_control_input_negative_dynamic
├── d24_unorm_s8_uint_depth_bias_clamp_control_input_positive
├── d24_unorm_s8_uint_depth_bias_clamp_control_input_positive_dynamic
├── d24_unorm_s8_uint_depth_bias_clamp_input_negative
├── d24_unorm_s8_uint_depth_bias_clamp_input_positive
├── d32_sfloat
├── d32_sfloat_clamp_control_half_viewport_range
├── d32_sfloat_clamp_control_half_viewport_range_dynamic
├── d32_sfloat_clamp_control_input_negative
├── d32_sfloat_clamp_control_input_negative_dynamic
├── d32_sfloat_clamp_control_input_positive
├── d32_sfloat_clamp_control_input_positive_dynamic
├── d32_sfloat_clamp_control_viewport_range
├── d32_sfloat_clamp_four_viewports
├── d32_sfloat_clamp_input_negative
├── d32_sfloat_clamp_input_positive
├── d32_sfloat_depth_bias_clamp_control_input_negative
├── d32_sfloat_depth_bias_clamp_control_input_negative_dynamic
├── d32_sfloat_depth_bias_clamp_control_input_positive
├── d32_sfloat_depth_bias_clamp_control_input_positive_dynamic
├── d32_sfloat_depth_bias_clamp_input_negative
├── d32_sfloat_depth_bias_clamp_input_positive
├── d32_sfloat_depth_range_unrestricted_negative
├── d32_sfloat_depth_range_unrestricted_positive
├── d32_sfloat_s8_uint
├── d32_sfloat_s8_uint_clamp_control_half_viewport_range
├── d32_sfloat_s8_uint_clamp_control_half_viewport_range_dynamic
├── d32_sfloat_s8_uint_clamp_control_input_negative
├── d32_sfloat_s8_uint_clamp_control_input_negative_dynamic
├── d32_sfloat_s8_uint_clamp_control_input_positive
├── d32_sfloat_s8_uint_clamp_control_input_positive_dynamic
├── d32_sfloat_s8_uint_clamp_control_viewport_range
├── d32_sfloat_s8_uint_clamp_four_viewports
├── d32_sfloat_s8_uint_clamp_input_negative
├── d32_sfloat_s8_uint_clamp_input_positive
├── d32_sfloat_s8_uint_depth_bias_clamp_control_input_negative
├── d32_sfloat_s8_uint_depth_bias_clamp_control_input_negative_dynamic
├── d32_sfloat_s8_uint_depth_bias_clamp_control_input_positive
├── d32_sfloat_s8_uint_depth_bias_clamp_control_input_positive_dynamic
├── d32_sfloat_s8_uint_depth_bias_clamp_input_negative
├── d32_sfloat_s8_uint_depth_bias_clamp_input_positive
├── d32_sfloat_s8_uint_depth_range_unrestricted_negative
├── d32_sfloat_s8_uint_depth_range_unrestricted_positive
├── d32_sfloat_s8_uint_unrestricted_bias_clamp_control_negative
├── d32_sfloat_s8_uint_unrestricted_bias_clamp_control_negative_dynamic
├── d32_sfloat_s8_uint_unrestricted_bias_clamp_control_positive
├── d32_sfloat_s8_uint_unrestricted_bias_clamp_control_positive_dynamic
├── d32_sfloat_s8_uint_unrestricted_clamp_control_negative
├── d32_sfloat_s8_uint_unrestricted_clamp_control_negative_dynamic
├── d32_sfloat_s8_uint_unrestricted_clamp_control_positive
├── d32_sfloat_s8_uint_unrestricted_clamp_control_positive_dynamic
├── d32_sfloat_unrestricted_bias_clamp_control_negative
├── d32_sfloat_unrestricted_bias_clamp_control_negative_dynamic
├── d32_sfloat_unrestricted_bias_clamp_control_positive
├── d32_sfloat_unrestricted_bias_clamp_control_positive_dynamic
├── d32_sfloat_unrestricted_clamp_control_negative
├── d32_sfloat_unrestricted_clamp_control_negative_dynamic
├── d32_sfloat_unrestricted_clamp_control_positive
├── d32_sfloat_unrestricted_clamp_control_positive_dynamic
├── x8_d24_unorm_pack32
├── x8_d24_unorm_pack32_clamp_control_half_viewport_range
├── x8_d24_unorm_pack32_clamp_control_half_viewport_range_dynamic
├── x8_d24_unorm_pack32_clamp_control_input_negative
├── x8_d24_unorm_pack32_clamp_control_input_negative_dynamic
├── x8_d24_unorm_pack32_clamp_control_input_positive
├── x8_d24_unorm_pack32_clamp_control_input_positive_dynamic
├── x8_d24_unorm_pack32_clamp_control_viewport_range
├── x8_d24_unorm_pack32_clamp_input_negative
├── x8_d24_unorm_pack32_clamp_input_positive
├── x8_d24_unorm_pack32_depth_bias_clamp_control_input_negative
├── x8_d24_unorm_pack32_depth_bias_clamp_control_input_negative_dynamic
├── x8_d24_unorm_pack32_depth_bias_clamp_control_input_positive
├── x8_d24_unorm_pack32_depth_bias_clamp_control_input_positive_dynamic
├── x8_d24_unorm_pack32_depth_bias_clamp_input_negative
└── x8_d24_unorm_pack32_depth_bias_clamp_input_positive
```

## Test Families

### basic — Depth value within viewport range

Renders a quad with depth value 0.3 in a viewport with range [0, 1]. The expected depth result is 0.3. This is the baseline test confirming that in-range depth values pass through clamping unchanged. Parameterized by depth/stencil format.

### clamp_input_negative — Clamping a large negative depth input

Renders a quad with depth value -1e6 in a viewport with range [0, 1]. The expected result is 0.0 (clamped to minDepth). Verifies that deeply negative depth values are clamped to the viewport minimum. Parameterized by depth/stencil format.

### clamp_input_positive — Clamping a large positive depth input

Renders a quad with depth value 1e6 in a viewport with range [0, 1]. The expected result is 1.0 (clamped to maxDepth). Verifies that deeply positive depth values are clamped to the viewport maximum. Parameterized by depth/stencil format.

### depth_bias_clamp_input_negative — Depth bias pushing depth below viewport minimum

Renders a quad with depth value 0.3 and a large negative depth bias constant factor (-2e11). The expected result is 0.0 (clamped to minDepth). Verifies that depth bias which pushes the depth value below the viewport minimum is correctly clamped. Parameterized by depth/stencil format.

### depth_bias_clamp_input_positive — Depth bias pushing depth above viewport maximum

Renders a quad with depth value 0.7 and a large positive depth bias constant factor (2e11). The expected result is 1.0 (clamped to maxDepth). Verifies that depth bias which pushes the depth value above the viewport maximum is correctly clamped. Parameterized by depth/stencil format.

### depth_range_unrestricted_negative — Unrestricted viewport with negative minDepth

Uses `VK_EXT_depth_range_unrestricted` to set viewport range [-1.5, 1.0] and renders a quad with depth -1.5. The expected result is -1.5. Verifies that negative viewport depth ranges are supported without clamping to [0, 1]. Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format.

### depth_range_unrestricted_positive — Unrestricted viewport with maxDepth > 1.0

Uses `VK_EXT_depth_range_unrestricted` to set viewport range [0, 1.5] and renders a quad with depth 1.5. The expected result is 1.5. Verifies that viewport depth ranges exceeding 1.0 are supported without clamping. Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format.

### clamp_four_viewports — Depth clamping across four viewports

Renders a quad using four viewports with different depth ranges and depth values. Each viewport has its own expected depth result computed from the viewport transformation formula. Tests that `vkCmdSetViewport`/`vkCmdSetScissor` work correctly with non-zero firstViewport/firstScissor indices. Uses a geometry shader to broadcast to multiple viewports. Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format.

### clamp_control_viewport_range — Depth clamp control using viewport range mode

Uses `VK_EXT_depth_clamp_control` with `VK_DEPTH_CLAMP_MODE_VIEWPORT_RANGE_EXT` (depth clamp control enabled but using viewport range). Renders a quad with depth 0.3 in a viewport with range [0, 1]. The expected result is 0.3. Verifies that the viewport range clamp mode produces the same result as the default behavior. Parameterized by depth/stencil format. Also has a `_dynamic` variant using `vkCmdSetDepthClampRangeEXT`.

### clamp_control_half_viewport_range — Depth clamp control with user-defined range inside viewport

Uses `VK_EXT_depth_clamp_control` with a user-defined clamp range [0.1, 0.9] in a viewport with range [0, 0.5]. Renders a quad with depth 0.4. The expected result is 0.2 (viewport-mapped then clamped). Verifies that the user-defined clamp range is correctly applied. Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### clamp_control_input_negative — Clamp control clamping negative input to user-defined minimum

Uses `VK_EXT_depth_clamp_control` with a user-defined clamp range [0.1, 0.9]. Renders a quad with depth -1e6 in a viewport with range [0, 1]. The expected result is 0.1 (clamped to user-defined minDepthClamp). Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### clamp_control_input_positive — Clamp control clamping positive input to user-defined maximum

Uses `VK_EXT_depth_clamp_control` with a user-defined clamp range [0.1, 0.9]. Renders a quad with depth 1e6 in a viewport with range [0, 1]. The expected result is 0.9 (clamped to user-defined maxDepthClamp). Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### depth_bias_clamp_control_input_negative — Depth bias with clamp control pushing below user-defined minimum

Uses `VK_EXT_depth_clamp_control` with a user-defined clamp range [0.1, 0.9] and a large negative depth bias (-2e11). Renders a quad with depth 0.3 in a viewport with range [0.3, 1.0]. The expected result is 0.1 (clamped to user-defined minDepthClamp). Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### depth_bias_clamp_control_input_positive — Depth bias with clamp control pushing above user-defined maximum

Uses `VK_EXT_depth_clamp_control` with a user-defined clamp range [0.1, 0.9] and a large positive depth bias (2e11). Renders a quad with depth 0.7 in a viewport with range [0, 0.7]. The expected result is 0.9 (clamped to user-defined maxDepthClamp). Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### unrestricted_clamp_control_negative — Unrestricted viewport with clamp control (negative range)

Combines `VK_EXT_depth_range_unrestricted` and `VK_EXT_depth_clamp_control`. Viewport range [-1.5, 1.0] with user-defined clamp range [-1.4, 0.9]. Renders a quad with depth -1.5. The expected result is -1.4 (clamped to user-defined minDepthClamp). Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### unrestricted_clamp_control_positive — Unrestricted viewport with clamp control (positive range)

Combines `VK_EXT_depth_range_unrestricted` and `VK_EXT_depth_clamp_control`. Viewport range [0, 1.5] with user-defined clamp range [0.1, 1.4]. Renders a quad with depth 1.5. The expected result is 1.4 (clamped to user-defined maxDepthClamp). Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### unrestricted_bias_clamp_control_negative — Unrestricted viewport with depth bias and clamp control (negative)

Combines `VK_EXT_depth_range_unrestricted` and `VK_EXT_depth_clamp_control` with depth bias. Viewport range [0, 1.0] with user-defined clamp range [-1.4, 0.9] and negative depth bias (-2e11). Renders a quad with depth 0.3. The expected result is -1.4. Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format. Also has a `_dynamic` variant.

### unrestricted_bias_clamp_control_positive — Unrestricted viewport with depth bias and clamp control (positive)

Combines `VK_EXT_depth_range_unrestricted` and `VK_EXT_depth_clamp_control` with depth bias. Viewport range [0, 1.0] with user-defined clamp range [0.1, 1.4] and positive depth bias (2e11). Renders a quad with depth 0.7. The expected result is 1.4. Skipped for UNORM and SNORM depth formats. Parameterized by depth/stencil format. Also has a `_dynamic` variant.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Depth/stencil format | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | Depth attachment format (defined at [vktDrawDepthClampTests.cpp#L87-L89](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L87-L89)) |
| Depth scenario | basic, clamp_input_negative, clamp_input_positive, depth_bias, depth_range_unrestricted, multi_viewport, clamp_control, unrestricted_clamp_control, unrestricted_bias_clamp_control | Test parameter configuration controlling depth value, viewport range, bias, and clamp control |
| Depth clamp control | disabled, enabled (pipeline static), enabled (dynamic) | Whether `VK_EXT_depth_clamp_control` is used and whether the clamp range is set statically or dynamically |
| Epsilon | 1e-5 (UNORM formats), machine epsilon (SFLOAT formats) | Format-dependent tolerance for depth comparison (defined at [vktDrawDepthClampTests.cpp#L90-L92](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L90-L92)) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `depthClamp` feature | Always | [vktDrawDepthClampTests.cpp#L1073](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1073) |
| `VK_EXT_depth_range_unrestricted` | When test uses unrestricted depth range | [vktDrawDepthClampTests.cpp#L191-L192](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L191-L192) |
| `VK_EXT_depth_clamp_control` | When test uses depth clamp control | [vktDrawDepthClampTests.cpp#L264-L265](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L264-L265) |
| `multiViewport` feature | When using multiple viewports (clamp_four_viewports) | [vktDrawDepthClampTests.cpp#L1079](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1079) |
| `geometryShader` feature | When using multiple viewports (clamp_four_viewports) | [vktDrawDepthClampTests.cpp#L1081-L1082](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1081-L1082) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawDepthClampTests.cpp#L1096-L1097](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1096-L1097) |
| Depth format support | Image format properties check for the specific depth format | [vktDrawDepthClampTests.cpp#L1084-L1093](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1084-L1093) |

## Verification Methods

- **Depth buffer pixel comparison**: After rendering, the depth buffer is read back and each pixel's depth value is compared against the expected value using a format-dependent epsilon tolerance. A test fails if any pixel differs from the expected value by more than epsilon. The comparison loop is at [vktDrawDepthClampTests.cpp#L978-L1004](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L978-L1004).

## Notes

- The framebuffer size is 256x256 (defined by `WIDTH` and `HEIGHT` at [vktDrawDepthClampTests.cpp#L57-L58](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L57-L58)).
- Tests using `VK_EXT_depth_clamp_control` with `depthClampControl.enabled == true` generate an additional `_dynamic` variant that uses `VK_DYNAMIC_STATE_DEPTH_CLAMP_RANGE_EXT` and `vkCmdSetDepthClampRangeEXT` instead of the pipeline static state. This is done at [vktDrawDepthClampTests.cpp#L1136-L1141](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1136-L1141).
- The `clamp_four_viewports` test uses a geometry shader with multiple invocations to broadcast different depth values to each viewport index. This requires both `multiViewport` and `geometryShader` features.
- UNORM and SNORM depth formats are skipped for tests with expected depth values outside [0, 1] (e.g., unrestricted depth range tests), since these formats cannot represent values outside that range.
- The depth bias clamp value is always set to 0.0 in the rasterizer state; clamping to the viewport range is performed by the hardware, not by `depthBiasClamp`.
- For dynamic rendering with secondary command buffers, the test count is reduced by only testing `D16_UNORM` format.
