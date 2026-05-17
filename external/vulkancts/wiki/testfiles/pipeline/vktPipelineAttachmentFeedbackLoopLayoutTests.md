# vktPipelineAttachmentFeedbackLoopLayoutTests.cpp

## Overview

[`vktPipelineAttachmentFeedbackLoopLayoutTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L1) implements the [`attachment_feedback_loop_layout`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L3370) topic group. It verifies VK_EXT_attachment_feedback_loop_layout functionality, testing rendering to and sampling from the same image simultaneously using feedback loop optimal or general layout.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineAttachmentFeedbackLoopLayoutTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L1)
- Header: [`vktPipelineAttachmentFeedbackLoopLayoutTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.hpp#L1)
- Shared instance: [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1)

## Registration Hierarchy

[`createAttachmentFeedbackLoopLayoutTests()`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L3366) returns the `attachment_feedback_loop_layout` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants (VulkanSC only). Misc sub-group is monolithic only.

```text
pipeline.monolithic.attachment_feedback_loop_layout
├── sampler
└── misc (monolithic only)
```

## Test Families

### sampler — Comprehensive sampling-from-feedback-loop tests

Comprehensive sampling-from-feedback-loop tests. Renders to an image while simultaneously sampling from it. Covers read-only, read-write-same-pixel, and read-write-different-areas modes across image view types, formats, and descriptor types.

The `sampler` group contains two image-layout sub-groups:
- `attachment_feedback_loop_optimal` — tests using `VK_IMAGE_LAYOUT_ATTACHMENT_FEEDBACK_LOOP_OPTIMAL_EXT`
- `general` — tests using `VK_IMAGE_LAYOUT_GENERAL`

Each layout sub-group contains `combined_image_sampler` and `sampled_image` descriptor-type sub-groups, which in turn contain `image_type` sub-groups for the 9 view types (1d, 1d_unnormalized, 1d_array, 2d, 2d_unnormalized, 2d_array, 3d, cube, cube_array), each with `format/` leaf tests spanning 7 formats across color, depth, and stencil aspects with read, read_write_same_pixel, and read_write_different_areas modes (plus interleave and dynamic-state variants).

Each layout sub-group also contains a `misc` sub-group (monolithic only) with `maintenance5_color_attachment` and `maintenance5_ds_attachment` tests for VK_KHR_maintenance5 compatibility with feedback loop layout.

### misc — Non-sampler feedback-loop tests (monolithic only)

Contains tests that do not fit the sampler pattern:
- `no_color_draw` — Draws with no color attachment bound but uses feedback loop layout. Verifies via storage buffer atomic counter.
- `separate_mip_levels` — Creates feedback loop using different mip levels of the same image (32x32).
- `separate_mip_levels_large_fb` — Same as `separate_mip_levels` but with a large framebuffer (512x512).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| TestMode | [Enum](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L72) | READ_ONLY, WRITE_ONLY, READ_WRITE_SAME_PIXEL, READ_WRITE_DIFFERENT_AREAS |
| ImageAspectTestMode | [Enum](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L81) | COLOR, DEPTH, STENCIL |
| PipelineStateMode | [Enum](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L106) | STATIC, DYNAMIC_WITH_ZERO_STATIC, DYNAMIC_WITH_CONTRADICTORY_STATIC |
| Image layout | Loop | attachment_feedback_loop_optimal, general |
| SamplerViewType | Custom class | 9 variants |
| VkFormat | Array | 7 formats (R8G8B8A8_UNORM, D16_UNORM, D32_SFLOAT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT, S8_UINT) |
| Descriptor type | Loop | COMBINED_IMAGE_SAMPLER, SAMPLED_IMAGE |
| interleaveReadWriteComponents | bool | false/true (READ_WRITE_SAME_PIXEL only) |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_EXT_attachment_feedback_loop_layout` | Always |
| `VK_EXT_attachment_feedback_loop_dynamic_state` | Non-STATIC pipeline state or shader object |
| `VK_KHR_unified_image_layouts` | GENERAL layout |
| `VK_EXT_shader_stencil_export` | Stencil aspect without interleave, or depth with interleave |
| `VK_KHR_maintenance5` | maintenance5 misc tests |
| `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` | no_color_draw |

## Verification Methods

- **Sampler tests**: `tcu::floatThresholdCompare` for color; separate depth/stencil threshold comparisons ([line 1835](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L1835))
- **no_color_draw**: Atomic counter verification (exact match) ([line 2831](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L2831))
- **separate_mip_levels**: `tcu::floatThresholdCompare` with threshold 0.005 for color, 0.0 for alpha ([line 3150](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L3150))
