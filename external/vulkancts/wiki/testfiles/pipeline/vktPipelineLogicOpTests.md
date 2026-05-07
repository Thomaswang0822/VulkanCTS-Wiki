# vktPipelineLogicOpTests.cpp

## Overview

[`vktPipelineLogicOpTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1) implements two topic groups of the pipeline category: [`logic_op`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886) and [`logic_op_na_formats`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L955). It verifies that all 16 `VkLogicOp` operations produce correct bitwise results on UINT color attachments, and that logic operations are correctly not applied on float and sRGB formats where they are inapplicable per spec.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineLogicOpTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1)
- Header: [`vktPipelineLogicOpTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.hpp#L1)

## Registration Path

This file contributes two subgroups:
- [`createLogicOpTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886) returns the `logic_op` group
- [`createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L955) returns the `logic_op_na_formats` group

Both are attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1).

**Variant coverage**: All variants.

## Test Hierarchy

```text
logic_op
├── <format_name>                         (14 UINT formats)
│   ├── clear
│   ├── and
│   ├── and_reverse
│   ├── copy
│   ├── and_inverted
│   ├── no_op
│   ├── xor
│   ├── or
│   ├── nor
│   ├── equivalent
│   ├── invert
│   ├── or_reverse
│   ├── copy_inverted
│   ├── or_inverted
│   ├── nand
│   └── set

logic_op_na_formats
├── <format_name>                         (18 float/sRGB formats)
│   ├── <logicOp>_noblend
│   └── <logicOp>_blend
```

Source: [`createLogicOpTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886), [`createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L955).

## Test Families

### 1. logic_op

Verifies all 16 `VkLogicOp` operations on UINT color attachment formats. Renders a fullscreen quad with a source color onto a framebuffer pre-cleared with a destination color, with logicOp enabled. Each test computes the expected result as `calcOpResult(logicOp, srcColor, dstColor) & channelMask` and compares against the GPU output.

### 2. logic_op_na_formats

Verifies that logic operations are correctly *not applied* when using float and sRGB color attachment formats where logic ops are inapplicable per spec. Tests both with and without blending enabled. For sRGB formats, applies `tcu::linearToSRGB` to the quad color for the expected result; for non-sRGB, expects the raw quad color.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkLogicOp | Loop at [line 910](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L910) | All 16: CLEAR, AND, AND_REVERSE, COPY, AND_INVERTED, NO_OP, XOR, OR, NOR, EQUIVALENT, INVERT, OR_REVERSE, COPY_INVERTED, OR_INVERTED, NAND, SET |
| UINT format | [Array](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L928) | 14 UINT formats: R8_UINT through R32G32B32A32_UINT |
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
