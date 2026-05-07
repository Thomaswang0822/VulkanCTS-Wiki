# vktPipelineBlendOperationAdvancedTests.cpp

## Overview

[`vktPipelineBlendOperationAdvancedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1) implements the [`blend_operation_advanced`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237) topic group. It verifies VK_EXT_blend_operation_advanced functionality, testing advanced blending operations including HSL blend modes, overlap modes, and premultiplied source colors.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBlendOperationAdvancedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1)
- Header: [`vktPipelineBlendOperationAdvancedTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.hpp#L1)

## Registration Path

[`createBlendOperationAdvancedTests()`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2236) returns the `blend_operation_advanced` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
blend_operation_advanced
├── ops
│   └── {blend_op}
│       └── {format}
├── independent
│   └── {blend_op}
│       └── {format}
└── coherent
    └── {blend_op}
        └── {format}
```

## Test Families

| Family | Description |
|---|---|
| BlendOperationAdvancedTest | Verifies advanced blend operations produce correct results |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkBlendOp | Loop | ZERO, SRC, DST, SRC_OVER, DST_OVER, SRC_IN, DST_IN, SRC_OUT, DST_OUT, SRC_ATOP, DST_ATOP, XOR, MULTIPLY, SCREEN, OVERLAY, DARKEN, LIGHTEN, COLORDODGE, COLORBURN, HARDLIGHT, SOFTLIGHT, DIFFERENCE, EXCLUSION, INVERT, INVERT_RGB, LINEARDODGE, LINEARBURN, HSL_HUE, HSL_SATURATION, HSL_COLOR, HSL_LUMINOSITY |
| VkBlendOverlapModeEXT | Enum | UNCORRELATED, CONJOINT, DISJOINT |
| VkFormat | Loop | R8G8B8A8_UNORM, R8G8B8A8_SRGB, etc. |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_blend_operation_advanced` | Primary extension for all tests |

## Verification Methods

- **Pixel comparison**: Render with advanced blend operation, compare against software reference implementation
- **Overlap mode verification**: Verify that overlap modes produce correct blending results
- **Premultiplied color verification**: Verify that premultiplied source colors are handled correctly

## Notes

- Advanced blend operations are computed using a software reference for comparison
- The test verifies both per-attachment and coherent (all-attachments) blending
