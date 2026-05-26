# vktSynchronizationImageLayoutTransitionTests

## Overview

Tests no-op image layout transitions using `VkImageMemoryBarrier2` from the `VK_KHR_synchronization2` extension. These tests verify that when `oldLayout` and `newLayout` are both `VK_IMAGE_LAYOUT_UNDEFINED`, the implementation is allowed to skip the layout transition without discarding image contents. The tests also verify that image layout transitions work correctly when submitted on different queue families (universal and compute).

This is a **sync2-only** test file. It is registered under the `synchronization2` category only.

## Role of File

Provides the `layout_transition` test group, which validates two scenarios:
1. **No-op transition**: A graphics rendering test that draws to an image, issues a barrier with `oldLayout=UNDEFINED` and `newLayout=UNDEFINED` (which should not discard image contents), then draws again and verifies the blended result.
2. **Compute transition**: A compute-based test that transitions an image across queue families (universal to compute and back), clears the image, reads it via compute, and verifies the result.

## Source Code

- [vktSynchronizationImageLayoutTransitionTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp)

## Registration Hierarchy

```text
synchronization2.layout_transition
├── no_op
├── compute_transition
└── compute_transition_storage
```

Registered in the sync2 path via [`createImageLayoutTransitionTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744), added to the `synchronization2` group in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L132).

## Test Families

### no_op — No-op layout transition

Graphics test: draws a full-screen quad with alpha blending, issues a no-op UNDEFINED-to-UNDEFINED barrier via `cmdPipelineBarrier2`, draws again, and verifies the blended result matches expected color.

### compute_transition — Compute queue layout transition

Compute test: transitions a multisample image across universal and compute queues, clears the image, reads via compute using `sampler2DMS`, and verifies the clear color. Uses `ComputeLayoutTransitionCase` with `storageUsage=false`.

### compute_transition_storage — Compute queue layout transition with storage image

Same as compute_transition but reads the image via `image2DMS` (storage image) instead of sampler. Uses `ComputeLayoutTransitionCase` with `storageUsage=true`. Requires additional format support check for storage usage with multisample.

## Parameter Dimensions

| Dimension | Values | Notes |
|-----------|--------|-------|
| Test type | no_op, compute_transition, compute_transition_storage | Fixed set of 3 tests |
| Image format | VK_FORMAT_R8G8B8A8_UNORM | Fixed for all tests |
| Image extent | 64x64 (no_op), 8x8 (compute) | Fixed per test type |
| Sample count | VK_SAMPLE_COUNT_1_BIT (no_op), VK_SAMPLE_COUNT_4_BIT (compute) | Fixed per test type |
| Storage usage | false, true | Only for compute tests |

## Support/Feature Requirements

| Requirement | Type | Notes |
|-------------|------|-------|
| VK_KHR_synchronization2 | Device Extension | Required for all tests (checked in `checkSupport`) |
| Compute queue | Queue Family | Required for compute_transition tests (checked via `context.getComputeQueue()`) |
| Storage image with multisample | Format Properties | Required for compute_transition_storage; checked via `getPhysicalDeviceImageFormatProperties` |

## Verification Methods

1. **no_op test**: Uses `tcu::floatThresholdCompare` with a threshold of `Vec4(0.01f)` to compare the rendered result against an expected image. The expected color is computed from two alpha-blended passes: `color = Vec4(red, green, blue, alpha)` where `alpha=0.4`, `red=green=(2.0-alpha)*alpha`, `blue=0`. The fragment shader outputs `vec4(1.0, 1.0, 0.0, 0.4)`.

2. **compute_transition tests**: Uses `tcu::floatThresholdCompare` with a zero threshold (`Vec4(0.0f, 0.0f, 0.0f, 0.0f)`) to compare the compute output buffer against a reference buffer filled with the clear color `Vec4(0.0, 0.0, 1.0, 1.0)` (blue).

## Test Principles

1. **No-op layout transition**: Per the Vulkan spec, when both `oldLayout` and `newLayout` in an image memory barrier are `VK_IMAGE_LAYOUT_UNDEFINED`, the implementation may skip the layout transition. The test verifies that this does not cause the image contents to be discarded. The barrier still establishes an execution dependency (srcStage=COLOR_ATTACHMENT_OUTPUT, dstStage=COLOR_ATTACHMENT_OUTPUT).

2. **Cross-queue layout transitions**: The compute tests exercise layout transitions submitted on different queue families. The image is transitioned to COLOR_ATTACHMENT_OPTIMAL on the universal queue, then to TRANSFER_DST_OPTIMAL on the compute queue, then cleared and read back on the universal queue. This validates that `VkImageMemoryBarrier2` correctly handles queue family ownership transfers.

3. **Multisample image access**: The compute tests use a multisample image (4 samples) and read it via either `sampler2DMS` or `image2DMS`, verifying that layout transitions do not corrupt multisample data.

## Notes/Uncertainties

- **sync2-only**: The `layout_transition` group is only added to the `synchronization2` test tree. It is not included in the LEGACY `synchronization` tree.
- **Vulkan SC handling**: The code uses `#ifndef CTS_USES_VULKANSC` to select between `cmdPipelineBarrier2` and `cmdPipelineBarrier2KHR`, but the test itself is registered outside any SC guard in the sync2 path.
- **Small test count**: Only 3 test cases are generated, making this a focused test file.
- **Fixed parameters**: Image dimensions, formats, and sample counts are hardcoded rather than parameterized.
