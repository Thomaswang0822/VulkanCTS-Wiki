# vktPipelineLogicOpTests.cpp

## Overview

[`vktPipelineLogicOpTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1) implements two topic groups of the pipeline category: [`logic_op`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886) and [`logic_op_na_formats`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L955). It verifies that all 16 `VkLogicOp` operations produce correct bitwise results on UINT color attachments, and that logic operations are correctly not applied on float and sRGB formats where they are inapplicable per spec.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineLogicOpTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1)
- Header: [`vktPipelineLogicOpTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.logic_op
├── r8_uint
├── r8g8_uint
├── r8g8b8a8_uint
├── b8g8r8a8_uint
├── r16_uint
├── r16g16_uint
├── r16g16b16_uint
├── r16g16b16a16_uint
├── r32_uint
├── r32g32_uint
├── r32g32b32_uint
└── r32g32b32a32_uint

pipeline.monolithic.logic_op_na_formats
├── r16_sfloat
├── r16g16_sfloat
├── r16g16b16_sfloat
├── r16g16b16a16_sfloat
├── r32_sfloat
├── r32g32_sfloat
├── r32g32b32_sfloat
├── r32g32b32a32_sfloat
├── r64_sfloat
├── r64g64_sfloat
├── r64g64b64_sfloat
├── r64g64b64a64_sfloat
├── r8_srgb
├── r8g8_srgb
├── r8g8b8_srgb
├── b8g8r8_srgb
├── r8g8b8a8_srgb
└── b8g8r8a8_srgb
```

Source: [`createLogicOpTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886), [`createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L955). Both groups are attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1). Variant coverage: all variants.

## Test Families

### logic_op — Logic operations on UINT formats

Verifies all 16 `VkLogicOp` operations on UINT color attachment formats. Each direct child in the hierarchy is a format-named group (12 UINT formats) containing 16 test cases named after the logic operations (clear, and, and_reverse, copy, and_inverted, no_op, xor, or, nor, equivalent, invert, or_reverse, copy_inverted, or_inverted, nand, set). Renders a fullscreen quad with a source color onto a framebuffer pre-cleared with a destination color, with logicOp enabled. Each test computes the expected result as `calcOpResult(logicOp, srcColor, dstColor) & channelMask` and compares against the GPU output. Source/dest colors are chosen to exercise all bit combinations per 4-bit nibble.

### logic_op_na_formats — Logic operations on inapplicable formats

Verifies that logic operations are correctly *not applied* when using float and sRGB color attachment formats where logic ops are inapplicable per spec. Each direct child in the hierarchy is a format-named group (12 float + 6 sRGB formats) containing test cases for each logic op with both `_noblend` and `_blend` suffixes. For sRGB formats, applies `tcu::linearToSRGB` to the quad color for the expected result; for non-sRGB, expects the raw quad color (since logicOp should not apply).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkLogicOp | Loop at [line 910](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L910) | All 16: CLEAR, AND, AND_REVERSE, COPY, AND_INVERTED, NO_OP, XOR, OR, NOR, EQUIVALENT, INVERT, OR_REVERSE, COPY_INVERTED, OR_INVERTED, NAND, SET |
| UINT format | [Array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L928) | 12 UINT formats: R8_UINT through R32G32B32A32_UINT |
| Float/sRGB format | [Array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L983) | 18 formats: 12 float + 6 sRGB |
| Blending | Loop at [line 1018](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1018) | `false`, `true` (logic_op_na_formats only) |
| Source/dest colors | Constants at [line 905](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L905) | Carefully chosen to exercise all bit combinations per 4-bit nibble |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `features.logicOp` == VK_TRUE | `LogicOpTest::checkSupport` | [193](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L193) |
| `features.logicOp` == VK_TRUE | `LogicOpInapplicableFormatsTest::checkSupport` | [555](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L555) |
| `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` | Both test classes | [199](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L199) |
| `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT` (when blending) | `LogicOpInapplicableFormatsTest::checkSupport` | [572](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L572) |
| Pipeline construction requirements | Both test classes | [196](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L196) |

## Verification Methods

### logic_op family

**Integer threshold comparison** (`tcu::intThresholdCompare`) with threshold (0,0,0,0) -- exact match. Computes expected color per channel as `calcOpResult(logicOp, srcColor, dstColor) & channelMask`, fills reference image, compares pixel-by-pixel. [Line 461](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L461).

### logic_op_na_formats family

**Float threshold comparison** (`tcu::floatThresholdCompare`) with threshold 0.01. For sRGB formats, applies `tcu::linearToSRGB` to the quad color for the expected result; for non-sRGB, expects the raw quad color (since logicOp should not apply). [Line 846](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L846).

## Test Principles Observed

- **Exhaustive logic-op coverage**: All 16 VkLogicOp values are tested per format
- **Bitwise correctness**: UINT format tests use exact integer comparison (zero threshold) to verify bitwise logic operations
- **Inapplicability verification**: Float/sRGB tests verify the *absence* of logic operation effects, not their presence
- **Source/dest color design**: Colors are chosen to exercise all bit combinations per 4-bit nibble, maximizing logic-op coverage

## Notes / Uncertainties

- The `logic_op` family uses exact integer comparison, which is appropriate for bitwise operations on UINT formats
- The `logic_op_na_formats` family uses a small float threshold (0.01) to account for blending precision
