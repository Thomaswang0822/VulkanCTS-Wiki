## Overview

**Core question:** Do depth-clamp, viewport-range, and depth-bias settings produce the source-defined depth values for each supported attachment format and recording path?

`DepthClampTests` verifies how Vulkan maps fragment depth through viewport depth ranges and depth-clamp state before the value is written to a depth attachment. It covers ordinary clamping, depth bias, unrestricted viewport ranges, user-defined clamp ranges, dynamic clamp-range commands, multiple viewports, and the depth/stencil formats selected by the implementation. The cases render a full-screen primitive and compare the depth image read back from the attachment.

## Background Knowledge

Depth clamping is enabled in the rasterization state. For the ordinary `[0,1]` viewport range, an input below the minimum is expected at `0.0`, an input above the maximum at `1.0`, and an in-range input passes through. `VK_EXT_depth_range_unrestricted` permits viewport depth endpoints outside `[0,1]`; `VK_EXT_depth_clamp_control` permits a user-defined clamp range instead of the viewport range. The latter also has a dynamic-state form that uses `vkCmdSetDepthClampRangeEXT`.

The implementation tests both depth-only and combined depth/stencil images. Values and expected results are fixed constants in the C++ parameter table, not random inputs. Cases outside the representable `[0,1]` domain are filtered for UNORM and SNORM formats.

## Registration Hierarchy

```text
draw.renderpass.depth_clamp
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
└── x8_d24_unorm_pack32

draw.dynamic_rendering.primary_cmd_buff.depth_clamp
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
└── x8_d24_unorm_pack32

draw.dynamic_rendering.partial_secondary_cmd_buff.depth_clamp
└── d16_unorm

draw.dynamic_rendering.complete_secondary_cmd_buff.depth_clamp
└── d16_unorm
```

Each format child expands to the baseline leaf and the source-defined suffix leaves: `_clamp_input_negative`, `_clamp_input_positive`, `_depth_bias_clamp_input_negative`, `_depth_bias_clamp_input_positive`, `_depth_range_unrestricted_negative`, `_depth_range_unrestricted_positive`, `_clamp_four_viewports`, `_clamp_control_viewport_range`, `_clamp_control_half_viewport_range`, `_clamp_control_input_negative`, `_clamp_control_input_positive`, `_depth_bias_clamp_control_input_negative`, `_depth_bias_clamp_control_input_positive`, `_unrestricted_clamp_control_negative`, `_unrestricted_clamp_control_positive`, `_unrestricted_bias_clamp_control_negative`, and `_unrestricted_bias_clamp_control_positive`. User-defined clamp-control leaves additionally have a `_dynamic` sibling. Format and extension filtering removes inapplicable combinations.

The render-pass root is created by `createDepthClampTests` from `vktDrawTests.cpp`. The five dynamic-rendering roots are created by the same dispatcher and reuse the factory with different `SharedGroupParams`. The dynamic-rendering secondary-command-buffer modes intentionally reduce the format matrix to `d16_unorm` in the implementation.

## Parameter Dimensions and Observed Values

| Dimension | Values observed in `vktDrawDepthClampTests.cpp` | Consequence |
|---|---|---|
| Format | `VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` | Selects the attachment and comparison epsilon. |
| Input and viewport | `0.3` in `[0,1]`; `-1e6` or `1e6` in `[0,1]` | Baseline or endpoint clamping. |
| Unrestricted viewport | `[-1.5,1.0]` with `-1.5`; `[0.0,1.5]` with `1.5` | Requires `VK_EXT_depth_range_unrestricted`; skipped for UNORM/SNORM. |
| Four viewports | `(0.0,0.5,0.7→0.35)`, `(0.9,1.0,1.0→1.0)`, `(0.5,1.0,0.9→0.95)`, `(0.5,0.9,0.4→0.66)` | Checks per-viewport state and viewport-index routing; skipped for UNORM/SNORM. |
| User-defined clamp range | `[0.1,0.9]`, `[-1.4,0.9]`, `[0.1,1.4]` | Requires `VK_EXT_depth_clamp_control`; unrestricted ranges also require `VK_EXT_depth_range_unrestricted`. |
| Depth bias | Disabled, `-2e11`, or `2e11` constant factor | Exercises bias-driven excursions to the active clamp endpoint. |

## Behavior Parameters

- **Attachment format:** one of the six source-listed depth formats; this controls numeric precision and epsilon (`1e-5` for the D16 formats and machine epsilon for the other listed formats).
- **Input excursion:** baseline `0.3`, negative `-1e6`, positive `1e6`, or the fixed inputs used by the four-viewport and unrestricted cases.
- **Viewport range:** ordinary `[0,1]`, unrestricted negative/positive endpoint, or one of four fixed viewport ranges.
- **Clamp mode:** viewport-range clamping or user-defined range; user-defined cases have static and `_dynamic` command-state variants.
- **Bias direction and magnitude:** no bias, `-2e11`, or `2e11`.
- **Rendering command mode:** render pass, dynamic-rendering primary, or dynamic-rendering secondary-command-buffer arrangement. This axis changes command recording and supported format coverage, not the expected depth rules.

## Shader Analysis

The vertex shader is generated as `vert` and assigns `gl_Position = in_position`; its four fixed vertices form a `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` covering the render target. The fragment shader is generated as `frag` and has an empty `main`, leaving depth testing and depth writing to fixed-function state. When more than one viewport is configured, the implementation generates `geom`: it uses geometry-shader invocations, assigns `gl_ViewportIndex`, copies each input position, replaces `gl_Position.z` with the corresponding fixed depth value, and emits the triangle strip. No shader file or disassembly is claimed beyond these generated GLSL strings.

## Runtime Execution and Result Checking

The instance creates a 256×256 depth image, image view, framebuffer/render pass or dynamic-rendering attachment, vertex buffer, pipeline layout, and graphics pipeline. The rasterizer sets `depthClampEnable` to `VK_TRUE`; depth bias state is enabled only for the bias parameter sets. The image is cleared to depth `0.5`, transitioned for rendering, and then transitioned to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` after the draw. Dynamic-rendering cases exercise the dispatcher-selected primary/secondary command-buffer arrangement. Dynamic clamp cases set `VK_DEPTH_CLAMP_MODE_USER_DEFINED_RANGE_EXT` and the source-defined `VkDepthClampRangeEXT` immediately before viewport/scissor and draw commands.

The test reads the depth aspect back and checks every pixel inside each scissor rectangle. A pixel fails when the absolute difference from its source-defined expected value is at least the format epsilon. Failure logs the result image and reports the expected value, observed value, and coordinates.

## Failure Meaning

A failure means the complete path from command interpretation to depth readback did not produce the source-defined value within tolerance. Possible causes include missing or incorrect depth-clamp state, depth-bias application, extension state, viewport transformation, viewport/scissor index selection, geometry-shader routing, vertex fetch, depth/stencil attachment transitions, format conversion, readback, or numeric comparison. A result-image mismatch alone does not isolate a shader-only defect.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| Baseline or ordinary clamp inputs | Incorrect viewport-depth mapping or ordinary depth-clamp state, or a shared attachment/readback comparison defect. |
| Unrestricted viewport or user-defined clamp-range inputs | Incorrect extension state, endpoint handling, viewport transformation, or range selection. |
| Four-viewport inputs | Incorrect geometry-shader viewport-index routing, per-viewport depth state, or multi-viewport rasterization. |
| Depth-bias inputs | Incorrect depth-bias application or interaction between bias and the active clamp range. |
| Dynamic clamp-range inputs | Incorrect `vkCmdSetDepthClampRangeEXT` state recording or dynamic-state application. |

### Cause Analysis

#### Depth mapping and clamp state

**Possible failure symptoms:** Pixels containing an out-of-range input differ from the expected clamp endpoint, while the readback reports the expected coordinates and values for the affected depth attachment.

**Possible implementation causes:** The implementation may apply the viewport transformation or ordinary/user-defined clamp range incorrectly. The source-backed test does not isolate a narrower implementation layer.

#### Extension and dynamic state

**Possible failure symptoms:** Only unrestricted, user-defined-range, or `_dynamic` cases fail; baseline cases using the ordinary viewport range pass.

**Possible implementation causes:** The relevant extension state may not be enabled, may use the wrong range, or may not be applied at the command location where the test sets it. Source-level investigation is needed to distinguish extension behavior from command-state recording.

#### Multi-viewport or depth-bias path

**Possible failure symptoms:** Four-viewport cases or one bias direction fails while single-viewport, no-bias cases pass, with mismatches localized to the affected viewport or biased depth values.

**Possible implementation causes:** The failure can indicate incorrect geometry-shader `gl_ViewportIndex` routing, per-viewport state, depth-bias arithmetic, or clamp ordering. The image comparison cannot by itself identify which stage is responsible.

## Case Pruning

### Requirement-based pruning

The factory requires the core depth-clamp feature for every case. It requires each extension listed by the parameter set, multi-viewport plus geometry-shader support for the four-viewport case, and `VK_KHR_dynamic_rendering` for dynamic-rendering groups. UNORM/SNORM filters remove unrestricted and other out-of-range cases that cannot represent the expected value.

### Design-based pruning

Secondary-command-buffer groups intentionally reduce the format matrix to `d16_unorm` in the implementation. Under `CTS_USES_VULKANSC`, extension-dependent parameter entries and dynamic-rendering dispatcher branches are excluded by conditional compilation.

## Key Takeaways

- The test family uses fixed, source-visible depth inputs and expected outputs.
- Ordinary clamping, unrestricted viewport ranges, and user-defined clamp ranges are separate behaviors.
- User-defined clamp control has both static and `_dynamic` state-setting cases.
- Four-viewport cases validate viewport-index routing as well as depth mapping.
- The final verdict is based on per-pixel depth readback with format-specific epsilon.

## Source Reference Appendix

- [Implementation and parameter table](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp)
- [Test-group declaration](../../../modules/vulkan/draw/vktDrawDepthClampTests.hpp)
- [Draw registration and rendering-mode dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp)
- [Understanding Brief](DepthClampTests_brief.md)
- [Vulkan viewport and depth-range specification](https://registry.khronos.org/vulkan/specs/latest/html/chapters/viewport.html)
