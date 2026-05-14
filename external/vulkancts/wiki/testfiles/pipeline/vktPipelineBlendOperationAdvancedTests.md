# vktPipelineBlendOperationAdvancedTests.cpp

## Overview

[`vktPipelineBlendOperationAdvancedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1) implements the [`blend_operation_advanced`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237) topic group. It verifies VK_EXT_blend_operation_advanced functionality, testing advanced blending operations including HSL blend modes, overlap modes, and premultiplied source colors.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBlendOperationAdvancedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1)
- Header: [`vktPipelineBlendOperationAdvancedTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.blend_operation_advanced
├── ops
├── independent
└── coherent
```

## Test Families

### ops — Per-operation advanced blend verification

Tests each advanced blend operation individually across multiple overlap modes (UNCORRELATED, CONJOINT, DISJOINT) and premultiplied source/destination color combinations. Each test case is parameterized by blend operation, format (R16G16B16A16_SFLOAT and R8G8B8A8_UNORM), overlap mode, and premultiply mode. Additional RGB blend operations (PLUS, MINUS, etc.) are only tested with UNCORRELATED overlap.

### independent — Independent blend per attachment

Tests advanced blend operations with independent blending enabled across multiple color attachments (2, 4, and 8). Each attachment receives a randomly selected blend operation. Uses premultiplied source and destination colors with UNCORRELATED overlap.

### coherent — Coherent advanced blending

Tests coherent advanced blending where two consecutive advanced blend operations are performed on the same color attachment. Each test case uses two randomly selected blend operations. Verifies that coherent blending produces correct results when operations are applied sequentially.

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
