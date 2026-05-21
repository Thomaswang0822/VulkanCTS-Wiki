# vktWsiPresentIdWaitTests

## Overview

This file implements tests for the `VK_KHR_present_id`, `VK_KHR_present_wait`, `VK_KHR_present_id2`, and `VK_KHR_present_wait2` extensions. These extensions allow applications to associate an ID with a present operation and to wait for a previously-presented ID to be displayed. The tests verify correct behavior of present ID assignment, present wait signaling, timeout handling, and multi-swapchain isolation.

## Role of file

Implementation file. Contains all test case definitions, test instance classes, and the registration entry point `createPresentIdWaitTests`.

## Source code

[vktWsiPresentIdWaitTests.cpp](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp)

## Registration Hierarchy

```text
wsi.headless.present_id_wait
├── id
├── id2
├── wait
└── wait2
```

## Test Families

### id

Tests for `VK_KHR_present_id` (version 1). Verifies that present IDs can be correctly associated with `vkQueuePresentKHR` calls via the `VkPresentIdKHR` structure. Three sub-tests:

- **zero**: Presents a frame with present ID 0. Expects `VK_SUCCESS`. Validates that a zero ID is accepted by the implementation.
- **increasing**: Presents two frames with strictly increasing IDs (1 and `UINT64_MAX`). Expects `VK_SUCCESS` for both. Validates that IDs can span the full uint64_t range.
- **interleaved**: Presents four frames alternating between frames with IDs (0, 1, `UINT64_MAX`) and frames with no ID. Expects `VK_SUCCESS` for all. Validates that present operations without IDs do not interfere with the ID tracking.

### id2

Tests for `VK_KHR_present_id2` (version 2). Mirrors the `id` family but uses `VkPresentId2KHR` instead of `VkPresentIdKHR`, and the swapchain is created with `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR`. Also requires `VK_KHR_get_surface_capabilities2` and checks `VkSurfaceCapabilitiesPresentId2KHR` support. Same three sub-tests as `id`:

- **zero**: Present with ID 0, expects `VK_SUCCESS`.
- **increasing**: Present with IDs 1 and `UINT64_MAX`, expects `VK_SUCCESS`.
- **interleaved**: Present with interleaved IDs and no-ID frames, expects `VK_SUCCESS`.

### wait

Tests for `VK_KHR_present_wait` (version 1). Uses `vkWaitForPresentKHR` to wait for previously-presented IDs. Six sub-tests:

- **single_no_timeout**: Presents a frame with ID 1, then waits for that ID with a 10-second timeout. Expects `VK_SUCCESS` (no timeout).
- **past_no_timeout**: Presents frames with IDs 1 and `UINT64_MAX`, then waits for past IDs (including re-waiting on already-presented IDs) with zero and non-zero timeouts. Also presents frames without IDs after using the max ID. All waits expect `VK_SUCCESS` (no timeout).
- **no_frames**: Does not present any frames, then waits for ID 1 with zero and 1-second timeouts. Expects `VK_TIMEOUT` for both waits. Also validates that the actual wall-clock wait duration falls within the expected timeout range (with a 100ms margin).
- **no_frame_id**: Presents frames with ID 0 or no ID, then waits for ID 1 with zero and 1-second timeouts. Expects `VK_TIMEOUT` for all waits, since ID 1 was never submitted.
- **future_frame**: Presents a frame with ID 1, then waits for IDs that have not been presented (`UINT64_MAX` and 2) with zero and 1-second timeouts. Expects `VK_TIMEOUT` for all waits.
- **two_swapchains**: Creates two windows, surfaces, and swapchains. Presents frames with different IDs on each swapchain simultaneously, then waits on selected IDs. Verifies that present IDs are not mixed up between swapchains.

### wait2

Tests for `VK_KHR_present_wait2` (version 2). Uses `vkWaitForPresent2KHR` with `VkPresentWait2InfoKHR` instead of `vkWaitForPresentKHR`. The swapchain is created with `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR`. Also requires `VK_KHR_get_surface_capabilities2` and checks `VkSurfaceCapabilitiesPresentWait2KHR` support. Three sub-tests:

- **single_no_timeout**: Present with ID 1, wait with 10-second timeout, expects `VK_SUCCESS`.
- **past_no_timeout**: Wait for already-presented IDs, expects `VK_SUCCESS` (no timeout).
- **two_swapchains**: Dual-swapchain smoke test, same as the `wait` family version.

Note: The `wait2` family does not include `no_frames`, `no_frame_id`, or `future_frame` tests because `vkWaitForPresent2KHR` has a VU requiring that the present ID must have actually been submitted as a presentId, making those scenarios invalid rather than timeout-expected.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| WSI platform | 9 types (headless, win32, xcb, xlib, wayland, android, display, directfb, direct_drm) | Tests are replicated per platform via the `wsi.{platform}` registration path |
| Extension version | 1, 2 | Version 1 uses `VK_KHR_present_id`/`VK_KHR_present_wait`; version 2 uses `VK_KHR_present_id2`/`VK_KHR_present_wait2` |
| Present ID value | 0, 1, `UINT64_MAX`, absent | Various ID values used across test sequences |
| Timeout | 0, 1 sec, 10 sec | Nanosecond timeouts for wait operations |

## Support/Feature Requirements

| Requirement | Applicable Families | Details |
|-------------|---------------------|---------|
| `VK_KHR_surface` | All | Base WSI surface extension |
| `VK_KHR_swapchain` | All | Required for swapchain creation |
| Platform-specific surface extension | All | e.g. `VK_KHR_win32_surface`, `VK_KHR_xcb_surface`, etc. |
| `VK_KHR_present_id` | id, wait | Device extension for present ID (v1) |
| `VK_KHR_present_wait` | wait | Device extension for present wait (v1) |
| `VK_KHR_present_id2` | id2, wait2 | Device extension for present ID (v2) |
| `VK_KHR_present_wait2` | id2, wait2 | Device extension for present wait (v2); also enabled by `id2` tests because the v2 swapchain creation flags set both `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` and `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR` |
| `VK_KHR_get_surface_capabilities2` | id2, wait2 | Instance extension required for v2 surface capability queries |
| `presentId2Supported` | id2, wait2 | Surface capability flag from `VkSurfaceCapabilitiesPresentId2KHR` |
| `presentWait2Supported` | id2, wait2 | Surface capability flag from `VkSurfaceCapabilitiesPresentWait2KHR`; checked for all `ver == 2` tests |
| `maxWindowsPerDisplay >= 2` | wait/two_swapchains, wait2/two_swapchains | Platform must support creating 2 windows |

## Verification Methods

- **Result code checking**: Each present operation can specify an expected `VkResult` (typically `VK_SUCCESS`, with `VK_SUBOPTIMAL_KHR` also accepted as success). Each wait operation checks for `VK_SUCCESS` or `VK_TIMEOUT` depending on the test scenario.
- **Timeout duration validation**: For wait operations that expect `VK_TIMEOUT`, the actual wall-clock duration is measured using `std::chrono::high_resolution_clock` and validated against the requested timeout within a 100ms margin (see [calcTimeoutRange](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L76-L90)).
- **Multi-swapchain isolation**: The `two_swapchains` tests verify that present IDs are tracked independently per swapchain by presenting different IDs on two swapchains and waiting on specific IDs for each.
- **Extension support check**: The `checkSupport` method (see [PresentIdWaitCase::checkSupport](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1375-L1405)) verifies that all required instance and device extensions are supported before running a test.

## Notes/Uncertainties

- The `wait2` family intentionally omits `no_frames`, `no_frame_id`, and `future_frame` sub-tests because `vkWaitForPresent2KHR` has a valid usage requirement that the present ID must have been previously submitted. These scenarios would trigger a VU violation rather than a timeout.
- The `PresentWaitDualInstance` class (used for `two_swapchains` tests) is not a subclass of `PresentIdWaitSimpleInstance`; it has its own `iterate()` method and directly manages two swapchains with interleaved present/wait sequences.
- The `id` and `id2` families only test present operations (no wait calls); the `wait` and `wait2` families test both present and wait operations together.
- Present mode `VK_PRESENT_MODE_FIFO_KHR` is used for all swapchains, which guarantees that present operations are queued and will eventually complete.
- The `PresentId2Instance` and `PresentWait2Instance` classes both enable `VK_KHR_present_id2` and `VK_KHR_present_wait2` device extensions, even though `id2` tests only use present ID functionality. This is because the v2 swapchain creation flags (`VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` and `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR`) are both set when `ver == 2`.
