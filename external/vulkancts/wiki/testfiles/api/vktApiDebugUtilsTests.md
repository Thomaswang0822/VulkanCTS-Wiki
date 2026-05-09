# [vktApiDebugUtilsTests.cpp](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1)

## Overview

[`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.debug_utils` subtree. It registers three direct children under the `debug_utils` group and uses a shared execution body to stress extremely long debug-utils object names and labels on queue families selected by required/excluded capability masks.

## Role of File

Implementation-heavy test file for the `api.debug_utils` subgroup.

## Source Code

- Primary source: [vktApiDebugUtilsTests.cpp](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1)
- Header: [vktApiDebugUtilsTests.hpp](../../../modules/vulkan/api/vktApiDebugUtilsTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L115)

## Registration Hierarchy

```text
api.debug_utils
├── long_labels_graphics
├── long_labels_transfer
└── long_labels_video_decode (not in Vulkan SC)
```

The confirmed Level-3 root is `api.debug_utils`, created by [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144-L167) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L115). The exact direct children are `long_labels_graphics`, `long_labels_transfer`, and `long_labels_video_decode`; the last child is conditionally omitted for Vulkan SC builds by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164).

## Test Families

### long_labels_graphics — Long debug labels on a graphics-capable queue

Covers the `long_labels_graphics` direct child registered by [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L149-L152). This case sets [`TestParams`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L44-L47) so `required = VK_QUEUE_GRAPHICS_BIT` and `excluded = 0`, then runs the shared body [`testLongDebugLabelsTest()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L50-L132).

Inside that shared body, the test enables `VK_EXT_debug_utils`, chooses a matching queue family, creates a `64 * 1024 + 1` character string, applies it as a buffer object name, inserts it as a command-buffer label, inserts it again as a queue label, and submits the command buffer for completion in [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L56-L131).

### long_labels_transfer — Long debug labels on a transfer-only-style queue

Covers the `long_labels_transfer` direct child registered by [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L154-L157). This case reuses the same execution body but changes the queue-family selection to `required = VK_QUEUE_TRANSFER_BIT` and `excluded = VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT`, so the stress path is exercised on a non-graphics, non-compute transfer-capable queue when such a family exists.

The observed semantics are still the same long-label stress operations from [`testLongDebugLabelsTest()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L50-L132); only the queue capability filter differs.

### long_labels_video_decode — Long debug labels on a video-decode queue

Covers the `long_labels_video_decode` direct child registered under [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164). It reuses the same shared test body again, but sets `required = VK_QUEUE_VIDEO_DECODE_BIT_KHR` and `excluded = VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT`, targeting a video-decode-capable queue when that subgroup is compiled in.

Because the registration itself is excluded for Vulkan SC builds, this child is documented in the hierarchy with a trailing note instead of being expanded into a separate structural exception.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Level-3 direct child | `long_labels_graphics`, `long_labels_transfer`, `long_labels_video_decode` from [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144-L167) |
| Required queue flags | `VK_QUEUE_GRAPHICS_BIT` at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L149-L152), `VK_QUEUE_TRANSFER_BIT` at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L154-L157), `VK_QUEUE_VIDEO_DECODE_BIT_KHR` at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164) |
| Excluded queue flags | `0` for graphics at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L149-L150); `VK_QUEUE_GRAPHICS_BIT \| VK_QUEUE_COMPUTE_BIT` for transfer and video-decode at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L154-L162) |
| Long label length | `64 * 1024 + 1` characters in [`testLongDebugLabelsTest()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97-L97) |
| Debug-utils target objects | buffer object naming at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L104-L109), command-buffer label insertion at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L119-L125), queue label insertion at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L127-L127) |
| Command content variation | buffer fill command only emitted when required flags overlap graphics/compute/transfer at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L114-L118) |

## Support / Feature Requirements

- every case requires the instance functionality `VK_EXT_debug_utils` through [`checkDebugUtilsSupport()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L134-L140)
- every case requires a queue family matching the provided required/excluded flag mask via [`findQueueFamilyIndexWithCaps()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L138-L139)
- the `long_labels_video_decode` child is omitted entirely for Vulkan SC builds via [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164)
- Vulkan SC builds inject reservation-related `pNext` structures for device and command-pool creation under [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L71-L91)

## Verification Methods

The visible verification style is execution-based rather than result-buffer comparison:

- the test performs debug-utils name and label API calls on a real instance, device, queue, and command buffer at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L108-L127)
- it records and submits a command buffer successfully at [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L110-L129)
- it returns pass unconditionally after successful completion via [`tcu::TestStatus::pass()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L131-L131)

From the inspected code, the pass criterion is that the long-name and long-label operations complete without earlier failure; the file does not compare callback output or read back stored label text.

## Test Principles Observed

- Stress an API path with oversized but valid-looking label/name input.
- Reuse one shared test body with queue-family parameterization via [`TestParams`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L44-L47).
- Exercise multiple debug-utils attachment points: buffer object names, command-buffer labels, and queue labels.
- Tie debug metadata to executable work by actually submitting the recorded command buffer.

## Notes / Uncertainties

- This normalization confirms the canonical Level-3 root as `api.debug_utils`, not a legacy `api -> debug_utils` path sketch, because the canonical contract requires the category-qualified root from [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144-L167).
- The exact direct children are only `long_labels_graphics`, `long_labels_transfer`, and `long_labels_video_decode`; there are no deeper registered subgroup nodes below them in this file.
- The inspected file does not assert a specification-derived maximum label length; it only demonstrates that a `64 * 1024 + 1` character string is attempted in code.
- The test does not inspect callback output or read back stored names, so no stronger claim about persistence, truncation, or external tooling visibility is made here.
