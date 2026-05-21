# vktAttachmentRateTests.cpp

This page documents the `attachment_rate` branch contributed by [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L1).

## Overview

The file registers attachment-backed fragment shading rate tests through [`createAttachmentRateTests()`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2539-L2753). It varies how the shading-rate attachment is prepared, the shading-rate image format, and the requested fragment size.

## Role of File

- Implementation-heavy registered subgroup file.
- It creates `TestCaseGroup(testCtx, "attachment_rate")` and adds mode groups plus a conditional `misc` group at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2595-L2675).

## Registration Hierarchy

```text
fragment_shading_rate.renderpass2.monolithic.attachment_rate
├── setup_with_atomics
├── setup_with_fragment
├── setup_with_copying
├── setup_with_copying_using_transfer_queue_concurent
├── setup_with_copying_using_transfer_queue_exclusive
├── setup_with_linear_tiled_image
└── misc
```

## Test Families

### setup_with_atomics — Compute-shader atomic setup

This mode is registered from `testModeParams[]` as `setup_with_atomics` at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2584-L2586).

### setup_with_fragment — Fragment-shader setup

This mode is registered at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2585-L2587).

### setup_with_copying — Copy-from-other-image setup

This mode is registered at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2586-L2588).

### setup_with_copying_using_transfer_queue_concurent — Concurrent transfer-queue copy setup

This mode is registered at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2588-L2589).

### setup_with_copying_using_transfer_queue_exclusive — Exclusive transfer-queue copy setup

This mode is registered at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2590-L2591).

### setup_with_linear_tiled_image — Linear-tiled image setup

This mode is registered at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2592-L2593).

### misc — Additional attachment-rate scenarios

The `misc` group contains renderpass-only `two_subpass`, `memory_access`, read-only depth/stencil layout cases, and a dynamic-rendering maintenance5 case outside Vulkan SC at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2675-L2750).

## Parameter Dimensions

Attachment-rate cases combine 16 unsigned integer formats listed at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2548-L2565) with nine fragment-size rates from `rate_1x1` through `rate_4x4` at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2573-L2576). Dynamic rendering duplicates cases for null shading-rate image handles, while renderpass cases duplicate imageless-framebuffer and general-layout variants at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2619-L2666).

## Support / Feature Requirements

`AttachmentRateTestCase::checkSupport()` requires `VK_KHR_fragment_shading_rate`, conditionally requires dynamic rendering or imageless framebuffer extensions, requires `attachmentFragmentShadingRate`, verifies format support for fragment shading rate attachment usage, checks that the requested rate is reported by `vkGetPhysicalDeviceFragmentShadingRatesKHR`, and requires `VK_KHR_maintenance5` for the maintenance5 mode at [`vktAttachmentRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2336-L2391).

## Verification Methods

The branch computes an encoded rate with [`calculateRate()`](../../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L161-L164), prepares attachment data through the selected mode, renders using the shading-rate attachment, and validates resulting fragment-rate behavior in the test instance. The support and registration evidence above identifies the mode/format/rate axes; this page does not claim a single comparison method for all modes beyond source-visible attachment-rate validation.

## Test Principles

The file isolates attachment-rate setup paths and attachment format/rate coverage from the larger basic matrix, including transfer-queue and memory-access variants.

## Notes / Uncertainties

The source uses the spelling `concurent` in the registered path; this page preserves that observed registered name.
