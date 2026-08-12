# ImageLayoutTransition

## Overview

**Core question:** Does synchronization2 preserve image contents for an intentional `UNDEFINED`-to-`UNDEFINED` barrier, and does it correctly carry a multisample image through layout transitions submitted on universal and compute queues?

This page documents the synchronization2-only `layout_transition` family from [`vktSynchronizationImageLayoutTransitionTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp). It is registered under `synchronization2`; the legacy `synchronization` category has no corresponding family.

## Background Knowledge

An image memory barrier describes an image's old and new layouts and can establish execution and memory dependencies. Synchronization2 carries this information in `VkImageMemoryBarrier2` inside `VkDependencyInfo`, recorded with `vkCmdPipelineBarrier2` (or `vkCmdPipelineBarrier2KHR` for Vulkan SC builds). When both layouts are `VK_IMAGE_LAYOUT_UNDEFINED`, Vulkan permits the implementation to skip the layout transition. The `no_op` case checks that this permitted optimization does not discard existing contents.

Queue-family ownership and layout are related but distinct concerns. The compute cases submit barriers on a universal queue, a compute queue, and the universal queue again. Their four-sample image is then read through either a multisample sampler or a multisample storage image.

## Registration Hierarchy

```text
synchronization2.layout_transition
├── compute_transition
├── compute_transition_storage
└── no_op
```

The exact default mustpass leaves are [listed here](../../../mustpass/main/vk-default/synchronization2.txt#L32027-L32029). The factory creates the group and three leaves in [`createImageLayoutTransitionTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757). The category dispatch adds the group to `synchronization2` in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L128-L132).

## Test Families

### `no_op`

This graphics case uses a 64x64 single-sample `VK_FORMAT_R8G8B8A8_UNORM` image. It first clears and transitions the image for color attachment use, draws a full-screen quad whose fragment shader outputs yellow with alpha `0.4`, and ends the render pass. It then records an execution dependency with `oldLayout = VK_IMAGE_LAYOUT_UNDEFINED` and `newLayout = VK_IMAGE_LAYOUT_UNDEFINED`, draws the quad again, copies the image to a host-visible buffer, and compares every pixel with the expected result of the two alpha-blended passes.

### `compute_transition`

This case uses an 8x8 four-sample `VK_FORMAT_R8G8B8A8_UNORM` image. A barrier on the universal queue changes `UNDEFINED` to `COLOR_ATTACHMENT_OPTIMAL`; a barrier on the compute queue changes that to `TRANSFER_DST_OPTIMAL`. The universal queue clears the image blue, changes it to `SHADER_READ_ONLY_OPTIMAL`, and dispatches an 8x8x4 compute shader. The shader reads each sample with `texelFetch` from `sampler2DMS` and writes it to a storage buffer. The host requires an exact blue result.

### `compute_transition_storage`

This follows the same queue and barrier sequence, but uses `VK_IMAGE_LAYOUT_GENERAL`, a storage-image descriptor, and `imageLoad` from `image2DMS`. It is registered separately so the storage-image path and its format/sample support gate are tested independently.

## Parameter Dimensions

| Dimension | Values | Notes |
|---|---|---|
| Scenario | `no_op`, `compute_transition`, `compute_transition_storage` | Exactly three fixed leaves |
| Format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed |
| Extent | 64x64 for `no_op`; 8x8 for compute | Fixed by scenario |
| Samples | `VK_SAMPLE_COUNT_1_BIT` for `no_op`; `VK_SAMPLE_COUNT_4_BIT` for compute | Fixed by scenario |
| Compute read mode | multisample sampler or storage image | Selects the two compute leaves |

## Support / Feature Requirements

| Requirement | Applies to | Evidence |
|---|---|---|
| `VK_KHR_synchronization2` | All leaves | [support check](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L375-L378) |
| Compute queue | Both compute leaves | [compute support check](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L461-L465) |
| Four-sample storage-image format support | `compute_transition_storage` | [format property check](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L466-L488) |

## Verification Methods

- `no_op` uses `tcu::floatThresholdCompare` with `Vec4(0.01f)`. The expected pixel is derived from two draws of `vec4(1.0, 1.0, 0.0, 0.4)`.
- Both compute leaves compare the host-visible output buffer against a blue `Vec4(0.0, 0.0, 1.0, 1.0)` reference with a zero threshold.
- A failed no-op comparison indicates content loss or incorrect dependency handling. A failed compute comparison points to queue/layout ownership, visibility to compute, multisample access, or (for storage) format support behavior.

## End-to-End Execution

```text
no_op:
  clear image -> draw -> UNDEFINED/UNDEFINED barrier -> draw -> copy -> compare

compute leaves:
  universal: UNDEFINED -> COLOR_ATTACHMENT_OPTIMAL
  compute:   COLOR_ATTACHMENT_OPTIMAL -> TRANSFER_DST_OPTIMAL
  universal: clear blue -> shader-read layout -> dispatch -> host barrier
  host:      compare one output value for every pixel/sample
```

## Important Variations and Special Cases

- No legacy equivalent is registered: do not look for `synchronization.layout_transition` in the legacy mustpass file.
- The compute image is multisampled and the dispatch uses one workgroup with local size 8x8x4, so each invocation reads one pixel/sample pair.
- The source uses core synchronization2 command names in ordinary builds and KHR command names under `CTS_USES_VULKANSC`; this does not add extra test leaves.
- Image dimensions, format, sample counts, and usage are fixed in the source rather than generated as a parameter matrix.

## Source Reference Appendix

| Topic | Link | Why it matters |
|---|---|---|
| No-op image and expected rendering | [graphics implementation](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L170-L337) | Barrier semantics and image comparison |
| Generated graphics shaders | [graphics case setup](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L339-L383) | Defines GLSL and support requirement |
| Compute parameters and support | [compute setup](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L385-L489) | Defines formats, queues, and skip conditions |
| Compute barriers, dispatch, and check | [compute implementation](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L520-L739) | Defines the cross-queue flow and result check |
| Registration | [test factory](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757) | Defines the exact tree |
| Mustpass coverage | [synchronization2 entries](../../../mustpass/main/vk-default/synchronization2.txt#L32027-L32029) | Confirms all three default leaves |
