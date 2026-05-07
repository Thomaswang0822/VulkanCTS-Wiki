# vktPipelineStencilTests.cpp

## Overview

[`vktPipelineStencilTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1) implements the [`stencil`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1484) topic group of the pipeline category. It verifies stencil buffer operations across all `VkStencilOp` and `VkCompareOp` combinations, with and without color attachments, and tests stencil-test behavior when no stencil attachment is bound.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineStencilTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1)
- Header: [`vktPipelineStencilTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1), [`vktPipelineImageUtil`](../../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L1)

## Registration Path

This file contributes the subgroup returned by [`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1469), which is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1) in the pipeline category root.

**Variant coverage**: Not extra shader-object (skipped by extra shader-object variants).

## Test Hierarchy

```text
stencil
├── format                                (colorAttachmentEnabled = true)
│   └── <format_name>[_separate_layouts]
│       └── states
│           ├── fail_<failOp>
│           │   └── pass_<passOp>
│           │       └── dfail_<depthFailOp>
│           │           └── <compareOp>
│           │               ├── any       (VK_IMAGE_LAYOUT_OPTIMAL)
│           │               └── general   (VK_IMAGE_LAYOUT_GENERAL, limited subset)
│           ...
├── nocolor                               (colorAttachmentEnabled = false)
│   └── format
│       └── <same structure as above>
└── no_stencil_att                        (monolithic, fast_linked_library, shader_object_unlinked_spirv only)
    ├── render_passes
    │   ├── static_enable
    │   │   └── <depth_format_name>
    │   └── dynamic_enable
    │       └── <depth_format_name>
    └── dynamic_rendering                 (skipped on VulkanSC)
        ├── static_enable
        │   └── <depth_format_name>
        └── dynamic_enable
            └── <depth_format_name>
```

Source: [`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1469).

## Test Families

### 1. format/states

Core stencil test family. Iterates all combinations of stencil operations (fail, pass, depth-fail) and compare operations across front/back faces for each supported stencil format. Front face iterates systematically; back face uses a seeded random iterator ([`StencilOpStateUniqueRandomIterator`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L71)) over all 8^4 = 4096 combinations. Verifies stencil operations produce correct results against a software reference renderer.

### 2. nocolor/format/states

Same as `format/states` but with no color attachment bound. Verifies stencil operations work correctly when only a depth/stencil attachment is present.

### 3. no_stencil_att

Tests enabling the stencil test when no stencil attachment is bound. Verifies the stencil test is effectively ignored (no crash, correct depth/color output). Uses both render passes and dynamic rendering, with static and dynamic stencil enable. Only registered for `monolithic`, `fast_linked_library`, and `shader_object_unlinked_spirv` variants ([line 1613](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1613)). Shader objects skip the `render_passes` sub-group ([line 1623](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1623)).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Stencil format | `formats::stencilFormats` | `S8_UINT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` (4 formats) |
| Separate depth/stencil layouts | Conditional loop | `false`, `true` (only for combined depth+stencil formats) |
| Color attachment enabled | [`colorAttachmentEnabled[]`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1487) | `true`, `false` |
| failOp | [`stencilOps[]`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L179) | All 8 `VkStencilOp` values |
| passOp | Same `stencilOps[]` | All 8 `VkStencilOp` values |
| depthFailOp | Same `stencilOps[]` | All 8 `VkStencilOp` values |
| compareOp | [`compareOps[]`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L188) | All 8 `VkCompareOp` values |
| Image layout | Loop at [line 1574](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1574) | `any` (OPTIMAL), `general` (GENERAL, limited subset) |
| Dynamic rendering (no_stencil_att) | Loop | `false`, `true` |
| Dynamic enable (no_stencil_att) | Loop | `false` (static), `true` (VK_EXT_extended_dynamic_state) |
| Depth format (no_stencil_att) | `formats::depthFormats` | 6 depth formats |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` | `StencilTest::checkSupport` | [267](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L267) |
| `VK_KHR_separate_depth_stencil_layouts` (separate layouts) | `StencilTest::checkSupport` | [272](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L272) |
| Pipeline construction requirements | `StencilTest::checkSupport` | [275](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L275) |
| `VK_KHR_portability_subset` / `separateStencilMaskRef` (non-VulkanSC) | `StencilTest::checkSupport` | [279](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L279) |
| `VK_KHR_dynamic_rendering` (no_stencil_att, dynamic rendering) | `NoStencilAttachmentCase::checkSupport` | [979](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L979) |
| `VK_EXT_extended_dynamic_state` (no_stencil_att, dynamic enable) | `NoStencilAttachmentCase::checkSupport` | [982](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L982) |

## Verification Methods

### format/states and nocolor families

[`StencilTestInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L766) uses [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) (software rasterizer) with matching stencil state:

- **Color**: Reads back via `readColorAttachment()`, compares with [`tcu::intThresholdPositionDeviationCompare`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L766) (threshold UVec4(2,2,2,2), position deviation IVec3(1,1,0)).
- **Stencil**: Reads back via `readStencilAttachment()`, compares with `tcu::intThresholdPositionDeviationCompare` (same thresholds).

### no_stencil_att family

[`NoStencilAttachmentInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1036) reads back color, depth, and stencil buffers and compares against expected clear/geometry values using `tcu::floatThresholdCompare` (color threshold 0.0) and `tcu::dsThresholdCompare` (depth threshold 0.000025, stencil threshold 0.0).

## Test Principles Observed

- **Exhaustive stencil-op coverage**: All 8^3 = 512 operation combinations are tested per compare op, rather than sampling
- **Front/back independence**: Front face iterates systematically; back face uses seeded random to cover the full 8^4 space without explosion
- **Attachment presence orthogonality**: Stencil behavior is verified both with and without a color attachment
- **Missing attachment robustness**: `no_stencil_att` verifies that enabling stencil test without a stencil attachment does not crash and produces correct depth/color output

## Notes / Uncertainties

- The `general` layout variant is only applied to a limited subset (first 3 values of each op dimension) to control test count
- VulkanSC skips the `dynamic_rendering` sub-group of `no_stencil_att`
