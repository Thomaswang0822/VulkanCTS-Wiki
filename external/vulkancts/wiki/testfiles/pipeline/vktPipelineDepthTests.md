# vktPipelineDepthTests.cpp

## Overview

[`vktPipelineDepthTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1) implements the [`depth`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2609) topic group of the pipeline category. It verifies depth testing operations including compare operators, depth bounds testing, depth-only rendering passes, depth clip control, and transfer queue layout transitions for depth/stencil images.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDepthTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1)
- Header: [`vktPipelineDepthTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1), [`vktPipelineImageUtil`](../../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.depth
├── format_features (monolithic only)
├── format (genFormatTests only)
├── nocolor (genFormatTests only)
├── no_depth_attachment (not shader-object)
├── depth_clip_control (non-VulkanSC)
├── xfer_queue_layout (monolithic only)
└── depth_only (monolithic, fast_linked_library, shader_object_unlinked_spirv)
```

Source: [`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2515). This group is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1) in the pipeline category root. Variant coverage: all variants.

## Test Families

### format_features — Mandatory depth/stencil format support

Verifies mandatory depth/stencil format support requirements: D16_UNORM must always be supported; at least one of D24_UNORM/X8_D24 or D32_SFLOAT must be supported; at least one of D24_UNORM_S8_UINT or D32_SFLOAT_S8_UINT must be supported. Contains three test cases: `support_d16_unorm`, `support_d24_unorm_or_d32_sfloat`, `support_d24_unorm_s8_uint_or_d32_sfloat_s8_uint`. Monolithic only.

### format — Depth tests with color attachment

Core depth test family. For each depth format and topology, tests pair-wise combinations of compare operators across 4 quads. Each format group contains `compare_ops` (with per-topology compare-op combinations, depth bounds test variants, and a special `never_zerodepthbounds_depthdisabled_stencilenabled` case), `depth_test_disabled` (with `depth_write_enabled` child), and `host_visible` (with `local_memory_depth_buffer` child). Also includes depth bounds test variants and a special case with zero depth bounds, depth disabled, and stencil enabled. GenFormatTests only; colorAttachmentEnabled = true.

### nocolor — Depth tests without color attachment

Same depth test structure as `format` but without a color attachment bound. Contains a `format` child group with the same per-format structure. GenFormatTests only.

### no_depth_attachment — Depth bounds test with no depth attachment

Tests depth bounds test when no depth attachment is bound (VK_FORMAT_UNDEFINED). Verifies the depth bounds test is effectively a no-op. Contains a `depth_bound_test` child test case. Not generated for shader object variants.

### depth_clip_control — Depth clip control tests

Tests `VK_EXT_depth_clip_control` which allows a [-1,1] depth range instead of [0,1]. Tests multiple viewport ordering scenarios (static, dynamic, before/after pipeline bind). Test case names follow the pattern `<format>_<compareOp>[_different_w|_viewport_before_static|_viewport_before_dynamic|...]`. Non-VulkanSC only.

### xfer_queue_layout — Transfer queue layout transition tests

Tests layout transitions of depth/stencil images using a transfer queue. Verifies correct rendering after layout changes between transfer and attachment usage. Contains three test cases: `aspect_depth`, `aspect_stencil`, `aspect_depth_stencil`. Monolithic only.

### depth_only — Depth-only rendering pass tests

Tests depth-only rendering passes (no color attachment in some passes). Verifies depth pre-pass and post-pass scenarios with separate render passes, subpasses, and dynamic rendering. Also tests with multiview (addViewIndex). Test case names follow the pattern `separate_render_passes|subpasses|dynamic_rendering[_prepass|_postpass][_add_view_index]`. Limited to monolithic, fast_linked_library, and shader_object_unlinked_spirv. VulkanSC skips the `dynamic_rendering` sub-type; shader objects skip `SEPARATE_RENDER_PASSES` and `SUBPASSES` sub-types.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Depth format | `formats::depthFormats` | `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` (6 formats) |
| Separate depth/stencil layouts | Conditional loop | `false`, `true` (only for combined depth+stencil formats) |
| Color attachment enabled | [`colorAttachmentEnabled[]`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2604) | `true`, `false` |
| Depth compare ops | [`depthOps[]`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2523) | 72 pair-wise combinations of 4 compare ops per quad |
| Primitive topology | [`primitiveTopologies[]`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2606) | `POINT_LIST`, `LINE_LIST`, `TRIANGLE_LIST` |
| Depth bounds test | Parameter | `false`, `true` (with min=0.1, max=0.25) |
| General layout | Conditional (every 10th combo) | `false` (OPTIMAL), `true` (GENERAL) |
| DepthClipControlCase | [Enum](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L65) | `DISABLED`, `NORMAL`, `NORMAL_W`, `BEFORE_STATIC`, `BEFORE_DYNAMIC`, `BEFORE_TWO_DYNAMICS`, `AFTER_DYNAMIC` |
| Image aspects (xfer_queue_layout) | [`aspectCases`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2824) | `DEPTH_BIT`, `STENCIL_BIT`, `DEPTH_BIT\|STENCIL_BIT` |
| DepthOnlyType | [Enum](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1643) | `SEPARATE_RENDER_PASSES`, `SUBPASSES`, `DYNAMIC_RENDERING` |
| Prepass/Postpass | Loop | `false` (postpass), `true` (prepass) |
| Add view index | Loop | `false`, `true` |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` (when depthBoundsTestEnable) | `DepthTest::checkSupport` | [278](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L278) |
| `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` (when depthAttachmentBound) | `DepthTest::checkSupport` | [280](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L280) |
| `VK_KHR_separate_depth_stencil_layouts` (separate layouts) | `DepthTest::checkSupport` | [284](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L284) |
| `VK_EXT_depth_clip_control` (when depthClipControl != DISABLED) | `DepthTest::checkSupport` | [292](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L292) |
| Transfer queue existence | `transferLayoutChangeSupportCheck` | [1254](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1254) |
| `VK_KHR_dynamic_rendering` (depth_only, DYNAMIC_RENDERING type) | `DepthOnlyCase::checkSupport` | [1725](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1725) |

## Verification Methods

### format and nocolor families

[`DepthTestInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1028) uses [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) with matching depth/compare state:

- **Color**: Reads back via `readColorAttachment()`, compares with `tcu::intThresholdPositionDeviationCompare` (threshold UVec4(2,2,2,2), position deviation IVec3(1,1,0)).
- **Depth**: Reads back via `readDepthAttachment()`, compares with `tcu::dsThresholdCompare` (format-dependent threshold).

### xfer_queue_layout family

[`transferLayoutChangeTest()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1277) verifies depth and stencil values after layout transitions using `tcu::dsThresholdCompare` (threshold 0.0 for both).

### depth_only family

[`DepthOnlyInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1761) verifies color and depth buffers using `tcu::floatThresholdCompare` (color threshold 0.0) and `tcu::dsThresholdCompare` (depth threshold 0.000025).

## Test Principles Observed

- **Pair-wise compare-op coverage**: Uses pair-wise combinations of compare ops across quads rather than exhaustive enumeration
- **Attachment presence orthogonality**: Depth behavior verified both with and without color attachment
- **Missing attachment robustness**: `no_depth_attachment` verifies depth bounds test is a no-op without a depth attachment
- **Memory type coverage**: `host_visible` tests non-device-local memory placement
- **Multi-pass depth scenarios**: `depth_only` tests realistic depth pre-pass/post-pass rendering patterns

## Notes / Uncertainties

- `genFormatTests` flag controls `format` and `nocolor` groups: only `shader_object_unlinked_spirv` gets format tests among shader object types
- `format_features` is monolithic only; `xfer_queue_layout` is monolithic only
- `depth_clip_control` and `dynamic_rendering` sub-type of `depth_only` are guarded by `#ifndef CTS_USES_VULKANSC`
- Shader objects skip `SEPARATE_RENDER_PASSES` and `SUBPASSES` sub-types in `depth_only`
