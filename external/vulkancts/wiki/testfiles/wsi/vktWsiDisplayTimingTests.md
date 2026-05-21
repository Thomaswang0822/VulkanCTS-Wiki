# vktWsiDisplayTimingTests

## Overview

Tests for the `VK_GOOGLE_display_timing` extension. These tests verify that an application can accurately specify desired presentation times for swapchain images and retrieve past presentation timing information. The test renders 300 frames (60 fps for 5 seconds) per configuration, exercising the display timing API by setting `desiredPresentTime` values via `VkPresentTimesInfoGOOGLE` and validating past presentation timing data returned by `getPastPresentationTimingGOOGLE`.

## Role of file

Implementation file. Contains the `DisplayTimingTestInstance` class and the `createDisplayTimingTests` registration function that builds the test hierarchy.

## Source code

[vktWsiDisplayTimingTests.cpp](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp)

## Registration Hierarchy

```text
wsi.headless.display_timing
├── fifo
├── fifo_relaxed
├── immediate
├── mailbox
└── fifo_latest_ready
```

## Test Families

### fifo

Tests display timing behavior with `VK_PRESENT_MODE_FIFO_KHR`. This is a vsync-enabled mode where images are presented in order on the next vertical blank. The group contains two sub-tests:

- **reference** -- Renders frames without using the display timing extension (standard `VkPresentInfoKHR` with no `VkPresentTimesInfoGOOGLE` pNext). Serves as a baseline to confirm the swapchain operates correctly in this present mode.
- **display_timing** -- Renders frames using the display timing extension, setting `desiredPresentTime` per frame and querying `getPastPresentationTimingGOOGLE` to validate timing accuracy. Includes a deliberate late-present test at frame 80 (presentID 80) where `desiredPresentTime` is set 1 second earlier than the previous image could have been presented.

### fifo_relaxed

Tests display timing behavior with `VK_PRESENT_MODE_FIFO_RELAXED_KHR`. Same structure as the `fifo` group (reference + display_timing sub-tests). In this mode, images may be presented outside of vertical blank if the image arrives late relative to the previous v-blank.

### immediate

Tests display timing behavior with `VK_PRESENT_MODE_IMMEDIATE_KHR`. Same structure (reference + display_timing sub-tests). In this mode, images are presented immediately without waiting for vertical blank, making timing validation particularly relevant for verifying that `desiredPresentTime` constraints are still respected.

### mailbox

Tests display timing behavior with `VK_PRESENT_MODE_MAILBOX_KHR`. Same structure (reference + display_timing sub-tests). In mailbox mode, the last submitted image replaces previously queued images. The frame 80 late-present test is skipped for this mode (the code explicitly excludes mailbox from the 1-second-early desiredPresentTime test at [vktWsiDisplayTimingTests.cpp#L937-L939](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L937-L939)).

### fifo_latest_ready

Tests display timing behavior with `VK_PRESENT_MODE_FIFO_LATEST_READY_KHR`. Same structure (reference + display_timing sub-tests). This present mode is similar to FIFO but allows the latest ready image to be presented. Like mailbox, the frame 80 late-present test is skipped for this mode ([vktWsiDisplayTimingTests.cpp#L937-L939](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L937-L939)).

## Parameter Dimensions

Each test family is parameterized by present mode (`VkPresentModeKHR`), as defined in the `presentModes` array at [vktWsiDisplayTimingTests.cpp#L1091-L1101](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1091-L1101):

| Present Mode | Vulkan Constant | Group Name |
|---|---|---|
| FIFO | `VK_PRESENT_MODE_FIFO_KHR` | `fifo` |
| FIFO Relaxed | `VK_PRESENT_MODE_FIFO_RELAXED_KHR` | `fifo_relaxed` |
| Immediate | `VK_PRESENT_MODE_IMMEDIATE_KHR` | `immediate` |
| Mailbox | `VK_PRESENT_MODE_MAILBOX_KHR` | `mailbox` |
| FIFO Latest Ready | `VK_PRESENT_MODE_FIFO_LATEST_READY_KHR` | `fifo_latest_ready` |

Each present mode group contains exactly two sub-tests:
- **reference** (`useDisplayTiming = false`) -- Standard presentation without timing extension.
- **display_timing** (`useDisplayTiming = true`) -- Presentation with `VK_GOOGLE_display_timing` enabled.

Additional fixed parameters:
- Frame count: 300 (60 fps * 5 seconds) at [vktWsiDisplayTimingTests.cpp#L619](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L619)
- Quad count: 16 at [vktWsiDisplayTimingTests.cpp#L583](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L583)
- Max out-of-date count: 20 at [vktWsiDisplayTimingTests.cpp#L622](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L622)
- Fence count: 6 at [vktWsiDisplayTimingTests.cpp#L640](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L640)

## Support / Feature Requirements

- **VK_GOOGLE_display_timing** -- The core extension under test. Must be supported by the device for the `display_timing` sub-tests. The `reference` sub-tests do not enable this extension (see `requiresDisplayTiming` parameter in [vktWsiDisplayTimingTests.cpp#L108-L109](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L108-L109) and the conditional extension count at [vktWsiDisplayTimingTests.cpp#L125](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L125)).
- **VK_KHR_swapchain** -- Required for swapchain creation.
- **VK_KHR_surface** -- Required for WSI surface.
- Platform-specific surface extension (e.g., `VK_KHR_android_surface`, `VK_KHR_xlib_surface`, etc.) -- Required based on the WSI platform type.
- **VK_KHR_display** -- Required if the WSI type is a display surface (checked at [vktWsiDisplayTimingTests.cpp#L86-L87](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L86-L87)).
- **VK_EXT_direct_mode_display** -- Required for `TYPE_DIRECT_DRM` WSI type (at [vktWsiDisplayTimingTests.cpp#L90-L91](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L90-L91)).
- Each present mode must be supported by the surface; otherwise, the test throws `NotSupportedError` (at [vktWsiDisplayTimingTests.cpp#L533-L534](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L533-L534)).

## Verification Methods

The `display_timing` sub-tests perform the following verifications:

1. **No early display** -- Validates that no image was displayed before `vkQueuePresentKHR` was called, by comparing `actualPresentTime` against the recorded queue present time ([vktWsiDisplayTimingTests.cpp#L785-L791](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L785-L791)).

2. **Late frame detection** -- Reports frames where `actualPresentTime` exceeds `desiredPresentTime + refreshDuration + 1ms`. For FIFO and FIFO_RELAXED modes, frame 80 is deliberately set with a `desiredPresentTime` 1 second too early, and the test verifies this frame is late by approximately 1 second ([vktWsiDisplayTimingTests.cpp#L806-L828](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L806-L828)).

3. **Early frame detection** -- Reports frames where `actualPresentTime > earliestPresentTime` with `presentMargin > 2ms`, indicating the image could have been presented earlier ([vktWsiDisplayTimingTests.cpp#L844-L864](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L844-L864)).

4. **Adaptive frame rate** -- Adjusts `refreshDurationMultiplier` up (slower) when frames are late and down (faster) when frames are early, demonstrating the intended usage pattern of the extension ([vktWsiDisplayTimingTests.cpp#L868-L886](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L868-L886)).

5. **Refresh cycle duration query** -- Calls `getRefreshCycleDurationGOOGLE` at swapchain initialization to obtain the display's refresh cycle duration, which is used as the basis for all timing calculations ([vktWsiDisplayTimingTests.cpp#L679](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L679)).

6. **Out-of-date recovery** -- Handles `VK_ERROR_OUT_OF_DATE_KHR` by recreating the swapchain up to 20 times before failing ([vktWsiDisplayTimingTests.cpp#L1005-L1024](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1005-L1024)).

The `reference` sub-tests do not perform timing-specific verifications; they serve as a baseline confirming that standard swapchain presentation works correctly in each present mode.

## Notes / Uncertainties

- The test is replicated per WSI platform (9 platform types), using `headless` as the representative in the registration hierarchy. The actual test paths follow the pattern `wsi.{platform}.display_timing.{present_mode}.{reference|display_timing}`.
- The `VK_PRESENT_MODE_FIFO_LATEST_READY_KHR` present mode is not a core Vulkan present mode; it may be defined by a vendor extension. Tests using this mode will be skipped if the mode is not supported by the surface.
- The frame 80 late-present test is performed for `fifo`, `fifo_relaxed`, and `immediate` present modes. It is explicitly skipped for `mailbox` and `fifo_latest_ready` modes because those modes may replace queued images, making the late-present expectation unreliable ([vktWsiDisplayTimingTests.cpp#L937-L938](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L937-L938)).
- The test uses a fixed 300-frame run (5 seconds at 60 fps), which may take significant time on slow devices.
- The `reference` sub-test creates a device with `enabledExtensionCount = 1` (only `VK_KHR_swapchain`), while the `display_timing` sub-test enables both extensions. However, the extension support validation loop at [vktWsiDisplayTimingTests.cpp#L129-L132](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L129-L132) unconditionally checks both extensions regardless of the `requiresDisplayTiming` parameter. This means the `reference` test will also throw `NotSupportedError` if `VK_GOOGLE_display_timing` is not supported by the physical device, even though the extension is not enabled on the device.
