# [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1)

## Overview

[`vktShaderObjectRenderingTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1) implements the `shader_object/rendering` branch. It registers dynamic-rendering shader-object cases under `rendering` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1201-L1395). The main matrix varies color attachment count, extra attachments, extra fragment outputs, dummy render pass mode, random versus same color formats, shader bind timing, `gl_FragDepth` writing, and color/depth formats. Verification compares generated expected color images using float or integer thresholds and checks depth values when a depth attachment is used at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1000-L1068).

## Role of File

Implementation-heavy test file for the root-level `rendering` branch.

## Source Code

- Primary source: [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L59)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Hierarchy

```text
shader_object.rendering
├── color_attachment_count_0
├── color_attachment_count_1
├── color_attachment_count_4
├── color_attachment_count_8
└── output_array
```

The displayed branch name is verified from `TestCaseGroup(testCtx, "rendering")` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1201-L1203). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L59).

## Test Families

### color_attachment_count_0 — Dynamic rendering attachment/output matrix

The main registration loop starts with four color attachment counts (`0`, `1`, `4`, `8`) at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1205-L1214). Each count creates a sub-group (`color_attachment_count_0` through `color_attachment_count_8`). Within each, the loop combines extra color attachments and extra fragment outputs from two seven-entry arrays, with a guard that skips cases where both extra attachments and extra outputs are active at the same time at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1216-L1259). The loop then varies dummy render pass mode, random versus same color formats, bind timing, and `gl_FragDepth` writing before adding per-format cases at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1262-L1341).

### color_attachment_count_1 — Dynamic rendering with one color attachment

Same matrix structure as `color_attachment_count_0` but with one color attachment. Random color format cases are skipped for fewer than two color attachments at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1269-L1270).

### color_attachment_count_4 — Dynamic rendering with four color attachments

Same matrix structure as `color_attachment_count_0` but with four color attachments. Both random and same color format cases are registered.

### color_attachment_count_8 — Dynamic rendering with eight color attachments

Same matrix structure as `color_attachment_count_0` but with eight color attachments. Both random and same color format cases are registered.

### output_array — Output array cases

The `output_array` family registers seven selected color formats and two color-write modes at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1356-L1394). These cases set `outputArray = true`, use four color attachments and two extra attachments, and require or disable color writes according to the registered case name at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1374-L1389).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Color attachment count | `0`, `1`, `4`, `8` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1205-L1214) |
| Extra attachment count/placement | none, one/two before, one/two between, one/two after at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1216-L1227) |
| Extra fragment output count/placement | none, one/two before, one/two between, one/two after at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1229-L1240) |
| Dummy render pass mode | `none`, `dynamic`, `static` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1242-L1247) |
| Color-format selection | random color formats skipped for fewer than two color attachments; otherwise `random_color_formats` and `same_color_formats` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1266-L1274) |
| Bind timing | `before` and `after` from `bindShadersBeforeBeginRendering` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1275-L1280) |
| Depth write mode | `gl_frag_write` and `none`; depth-format cases are skipped when `gl_FragDepth` is written at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1281-L1328) |
| Output array formats | seven `colorFormats2[]` entries at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1362-L1365) |

## Support / Feature Requirements

- Cases require `VK_EXT_shader_object` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1093-L1100).
- The support check rejects combinations whose color attachment count plus extra attachment/output counts exceed `VkPhysicalDeviceLimits::maxColorAttachments` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1101-L1104).
- The support check queries physical-device image format properties for the selected color format and color-attachment/transfer-source usage at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1106-L1110).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L59).

## Verification Methods

- For each active color attachment, the instance generates an expected image with `generateExpectedImage()` and compares against the copied result buffer. Float formats use `tcu::floatThresholdCompare()` with `Vec4(0.02f)`, and non-float formats use `tcu::intThresholdCompare()` with `UVec4(2)` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1009-L1030).
- Extra attachments marked unused are skipped during color comparison according to the computed unused attachment interval at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1000-L1013).
- When a depth attachment is used, the depth image is copied and read back; pixels inside the rendered rectangle must be close to `0.5`, and outside pixels must be close to `1.0`, using epsilon `0.02f` at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1032-L1067).
- The instance uses `chooseDevice()` before rendering, indicating some cases may create or select a custom device before executing the test body at [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L758-L775).

## Test Principles Observed

- Stress shader-object dynamic rendering across attachment/output mismatches and format combinations.
- Verify color and depth outputs with explicit image readback rather than relying only on command success.
- Use support checks for device attachment limits and image format availability instead of pruning registration at the root.

## Notes / Uncertainties

- The support-check excerpt confirms color-format querying; any additional depth-format or custom-device gating beyond the inspected range is not described here.
