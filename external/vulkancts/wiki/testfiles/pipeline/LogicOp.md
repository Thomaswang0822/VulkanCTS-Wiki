## Overview

**Core question:** Does `vktPipelineLogicOpTests.cpp` apply the selected `VkLogicOp` component-wise on UINT color attachments and leave the operation unapplied on floating-point and sRGB attachments?

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

`logicOpEnable` and `logicOp` in `VkPipelineColorBlendStateCreateInfo` control a logical operation between the fragment output and the value already held by a color attachment. Vulkan applies logical operations only to signed, unsigned, and normalized integer color formats. Floating-point and sRGB formats are not affected. The device must support the `logicOp` feature.

The render-pass clear supplies the destination color. The fragment shader supplies the source color through a push constant. The tested operation belongs to fixed-function color output state, not to the shader.

## Registration Hierarchy

```text
pipeline.monolithic.logic_op

pipeline.monolithic.logic_op_na_formats
```

[`createLogicOpTests()` and `createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886-L1030) register these two test families. `createChildren()` adds them for each pipeline construction type. This page uses `monolithic` as the parseable representative root. The mustpass evidence also covers `pipeline_library`, `fast_linked_library`, and shader-object construction roots.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `logic_op`, `logic_op_na_formats` | Selects the integer-result path or the no-effect path for inapplicable formats. | [family registration](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886-L1030) |
| `VkLogicOp` | `clear`, `and`, `and_reverse`, `copy`, `and_inverted`, `no_op`, `xor`, `or`, `nor`, `equivalent`, `invert`, `or_reverse`, `copy_inverted`, `or_inverted`, `nand`, `set` | Selects one of the 16 bitwise operations. | [operation array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L910-L925) |
| UINT format | 14 formats from `r8_uint` through `r32g32b32a32_uint` | Selects the integer attachment channel count and channel width. | [UINT format array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L928-L933) |
| Floating-point or sRGB format | 12 floating-point formats and 6 sRGB formats | Selects an attachment where logical operations must not apply. | [inapplicable format array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L983-L1005) |
| Blending | `_noblend`, `_blend` | Selects whether blending is also enabled in `logic_op_na_formats`. | [blend loop](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1014-L1024) |
| Source and destination colors | `kQuadColor` and `kFbColor`; floating-point constants for the inapplicable-format path | Supplies the operation inputs or the expected unaffected fragment output. | [integer constants](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L905-L906) and [floating-point constants](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L960-L961) |

## Behavior Parameters

### `logic_op`: logical operations on UINT attachments

Each test selects an integer format and one `VkLogicOp`. The host clears a 32 by 32 attachment and draws a full-screen triangle strip. Fixed-function color output state applies the selected operation to the source and destination components. The reference path calls `calcOpResult()` for each used component and then applies the channel-width mask.

### `logic_op_na_formats`: no logical operation on inapplicable formats

Each test selects a floating-point or sRGB format, a `VkLogicOp`, and whether blending is enabled. The pipeline still sets `logicOpEnable` to `VK_TRUE`. In `_blend` cases, the configured `ZERO` source and `ONE` destination factors would preserve the clear color if blending ran. Vulkan instead treats blending as disabled when logical operations are enabled, while an attachment format that does not support logical operations passes the fragment color through unmodified. The expected image therefore contains the ordinary fragment color. The sRGB reference value is produced with `tcu::linearToSRGB`; other formats use `quadColor` directly.

## Shader Analysis

The GLSL shaders do not perform the tested logical operation. They generate the full-screen triangle strip and write the push-constant source color to the fragment output. `VkPipelineColorBlendStateCreateInfo` performs or skips the operation in fixed-function state, so this page has no representative shader walkthrough or SPIR-V disassembly.

## Runtime Execution and Result Checking

Both test classes first check `features.logicOp`, pipeline construction requirements, and `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT`. `_blend` cases additionally require `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT`. Each case creates a 32 by 32 color image with the selected format, an image view, render pass, pipeline layouts, graphics pipeline, transient command pool, and primary command buffer.

The command buffer clears the attachment, writes the fragment-stage push constant, binds the pipeline, issues one `vk.cmdDraw`, ends the render pass, submits, and waits. The UINT path reads the attachment into a `TextureLevel`, computes `calcOpResult(logicOp, quadColor, fbColor)` per component, applies the channel mask, and compares pixels with `tcu::intThresholdCompare` using an all-zero threshold. The floating-point and sRGB path builds the expected unaffected color, converts sRGB with `tcu::linearToSRGB`, and compares with `tcu::floatThresholdCompare` using `0.01f`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `logic_op` | Incorrect operation selection or per-component integer evaluation, incorrect channel-width masking, color-attachment setup, or readback/reference comparison. |
| `logic_op_na_formats` | A logical operation is incorrectly applied to floating-point or sRGB output, blending incorrectly remains active while `logicOpEnable` is true, sRGB conversion differs from the expected value, blend-support gating is wrong, or readback/reference comparison is incorrect. |

### Cause Analysis

#### Logical operation or channel-mask error

**Possible failure symptoms:** `logic_op` reports mismatched pixels from `tcu::intThresholdCompare`. The mismatch may affect only some channels or may change with 8-, 16-, and 32-bit formats.

**Possible implementation causes:** The implementation may select the wrong `VkLogicOp`, reverse source and destination, omit the complement in `calcOpResult()`, or fail to truncate unused bits with `getChannelMask()`. The four colors use different high and low nibbles, so channel mixing also changes the result. The final image alone normally cannot distinguish operation-order and channel-mapping defects; source-level investigation is needed.

#### Logical operation incorrectly applied to an inapplicable format

**Possible failure symptoms:** A `logic_op_na_formats` float comparison fails with the clear color in an `_blend` case, indicating that the configured `ZERO` source and `ONE` destination blend factors ran instead of being treated as disabled. A result that resembles a bitwise operation indicates that the logical operation ran on an inapplicable format. An sRGB failure may appear only after conversion.

**Possible implementation causes:** The implementation may apply logical operations to floating-point or sRGB formats, fail to treat blending as disabled when `logicOpEnable` is true, or treat `logicOpEnable` as an unconditional request to execute the selected operation. The defect may instead be in linear-to-sRGB conversion, blend-state selection, format support reporting, or readback. For `_blend`, inspect both `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT` gating and fixed-function state.

#### Feature or attachment-capability check error

**Possible failure symptoms:** A case is incorrectly reported unsupported, or a pipeline is created for a format that lacks the required capability and then fails.

**Possible implementation causes:** Both `checkSupport()` methods require `features.logicOp` and `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT`; only blending cases check `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT`. Incorrect propagation of format properties can prune legal cases or admit unsupported combinations.

## Case Pruning

### Requirement-based pruning

- Both test classes require `features.logicOp == VK_TRUE`.
- Both require `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and the relevant pipeline construction requirements.
- `logic_op_na_formats` `_blend` variants additionally require `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT`.

### Design-based pruning

- `logic_op` lists 14 UINT formats and covers all 16 operations for each format.
- `logic_op_na_formats` lists 12 floating-point and 6 sRGB formats, then emits `_noblend` and `_blend` for every operation.
- `kQuadColor` and `kFbColor` use contrasting nibble patterns to exercise high and low bits and expose channel mixing. They are fixed test inputs, not runtime-random parameters.

## Key Takeaways

- `logic_op` checks exact fixed-function bitwise results on UINT attachments with a zero-threshold integer comparison.
- `logic_op_na_formats` checks that Vulkan does not apply logical operations to floating-point and sRGB attachments; the sRGB oracle performs the required linear-to-sRGB conversion.
- The shaders only supply the source color. Failure investigation should start with `logicOp` state, format applicability, channel masks, format properties, and readback.
- Each inspected mustpass file contains 800 leaves from this source file: 224 `logic_op` leaves plus 576 `logic_op_na_formats` leaves. The inspected roots are `monolithic`, `pipeline_library`, `fast_linked_library`, and the four shader-object roots.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Logical-operation implementation and format checks | [`calcOpResult()`, `getChannelMask()`, and `checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L89-L202) | Defines the 16 operations, channel mask, and feature/format gates. |
| UINT shader and runtime | [`LogicOpTest::initPrograms()` and `LogicOpTestInstance`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L204-L503) | Shows that the shader only supplies source data and defines the exact integer oracle. |
| Inapplicable-format runtime | [`LogicOpInapplicableFormatsTest`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L525-L876) | Defines floating-point/sRGB output, blend gating, and the float oracle. |
| Registration | [`createLogicOpTests()` and `createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886-L1030) | Defines the two families, formats, operations, and leaves. |
| Vulkan contract | [Logical Operations](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1676-L1756) | Defines applicable format classes, `logicOpEnable`, and operation semantics. |
| Mustpass evidence | [pipeline mustpass files](../../../mustpass/main/vk-default/pipeline/) | Provides selected registered cases for each construction root. |
