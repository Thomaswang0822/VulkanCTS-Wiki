# vktWsiPresentTimingTests

## Overview

This file implements tests for the `VK_EXT_present_timing` extension, which provides applications with precise control over when frames are presented and detailed timing information about the presentation pipeline. The tests cover surface capability queries, timing queue management, past presentation timing retrieval, time domain enumeration and calibration, and present-at-time functionality (absolute and relative).

## Role

Implementation file.

## Source

[vktWsiPresentTimingTests.cpp](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp)

## Registration Hierarchy

```text
wsi.headless.present_timing
├── basic
├── query
├── time_domain
└── present_at
```

> **Per-Platform Note:** The root path uses "headless" as the representative platform. The same structure is replicated for all 9 WSI platform types.

## Test Families

### basic

Contains fundamental present timing tests that do not require per-mode or per-stage parameterization. Registered by `populateBasicGroup` ([vktWsiPresentTimingTests.cpp#L2306-L2312](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2306-L2312)).

- **surface_capabilities** -- Verifies that `VkPresentTimingSurfaceCapabilitiesEXT` can be queried via `vkGetPhysicalDeviceSurfaceCapabilities2KHR` and that `VK_PRESENT_STAGE_QUEUE_OPERATIONS_END_BIT_EXT` is reported as supported when `presentTimingSupported` is true.
- **timing_queue** -- Exercises `vkSetSwapchainPresentTimingQueueSizeEXT` to grow, shrink, and zero the timing queue. Verifies that `VK_ERROR_PRESENT_TIMING_QUEUE_FULL_EXT` is returned when the queue is full, that shrinking a non-empty queue returns `VK_NOT_READY`, and that draining results makes space for new presents.
- **retired_swapchain** -- Creates two swapchains in succession (the second replaces the first via `oldSwapchain`), presents frames on each, then queries and verifies that past presentation timing data is returned for both the retired and active swapchains.
- **large_queue_size** -- Presents frames with a large timing queue (queue size 512 in immediate mode, 64 in FIFO). The actual frame count is double the queue size (1024 in immediate mode, 128 in FIFO). Verifies that the queue fills exactly once, that all results can be drained, and that present IDs and stage counts are correct.

### query

Tests querying past presentation timing information across combinatorial parameter combinations. Registered by `populateQueryGroup` ([vktWsiPresentTimingTests.cpp#L2314-L2346](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2314-L2346)).

The group is structured as:

- **\<present_mode\>** (7 modes) -- One child group per present mode: `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `demand`, `continuous`, `fifo_latest_ready`.
  - **\<present_stage\>** (4 stages) -- One child group per present stage query flag: `queue_operations_end`, `request_dequeued`, `image_first_pixel_out`, `image_first_pixel_visible`.
    - **\<time_domain\>** (6 domains) -- One leaf test per time domain: `device`, `clock_monotonic`, `clock_monotonic_raw`, `query_performance_counter`, `present_stage_local`, `swapchain_local`.
- **parallel** -- A single test that runs `timingTestWithBackgroundQueryThreads`, which presents frames on the main thread while 4 parallel background threads concurrently call `vkGetPastPresentationTimingEXT`. Verifies that all results are eventually collected and present IDs are correct.

Each leaf test in the present_mode/present_stage/time_domain hierarchy runs `timingTest`, which presents 10 frames with incrementing present IDs, drains timing results, and verifies present IDs, stage counts, and timestamp monotonicity.

### time_domain

Tests time domain enumeration, properties, and calibration. Registered by `populateTimeDomainGroup` ([vktWsiPresentTimingTests.cpp#L2348-L2364](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2348-L2364)).

- **calibration** -- One child test per time domain (6 domains). Each test runs `timeDomainCalibrationTest`, which takes calibrated timestamps before and after each present using `vkGetCalibratedTimestampsKHR`, then verifies that reported present stage timestamps fall within the before/after calibrated window and that host-vs-device timestamp differences are within the reported deviation.
- **properties** -- Runs `timeDomainPropertiesTest`, which presents 30 frames and after each present calls `vkGetSwapchainTimeDomainPropertiesEXT` to verify: `VK_TIME_DOMAIN_PRESENT_STAGE_LOCAL_EXT` is always reported, time domain IDs are unique, the `timeDomainsCounter` is non-decreasing, and if it has not changed the domain data is identical to the previous query. Also handles the case where a past presentation timing result returns an unknown `timeDomainId`, confirming the counter has been updated.

### present_at

Tests the present-at-time feature, which allows applications to request that frames be presented at specific target times. Registered by `populatePresentAtGroup` ([vktWsiPresentTimingTests.cpp#L2366-L2439](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2366-L2439)).

Present-at is restricted to FIFO-based present modes: `fifo`, `fifo_relaxed`, and `fifo_latest_ready`.

The group is structured as:

- **\<presentAtMode\>** (2 modes) -- `absolute` and `relative`.
  - **\<allowed_present_mode\>** (3 modes) -- `fifo`, `fifo_relaxed`, `fifo_latest_ready`.
    - **\<time_domain\>** (6 domains) -- Same 6 time domains as the query group.
      - **\<out_of_order\>** (2 values) -- `allow_out_of_order_results` or `disallow_out_of_order_results`.
        - **\<partial\>** (2 values) -- `allow_partial_results` or `disallow_partial_results`.
          - **nearest** -- Present-at targeting the nearest refresh cycle (`VK_PRESENT_TIMING_INFO_PRESENT_AT_NEAREST_REFRESH_CYCLE_BIT_EXT` set).
          - **after** -- Present-at targeting after the specified time (nearest refresh cycle flag not set).

Each leaf test runs `presentAtTest`, which presents 10 frames with calculated target times. For absolute mode, the target time is computed from a base presentation timestamp. For relative mode, the target time is a relative offset from the previous present. The test verifies that frames are not presented earlier than the requested time (within `kTargetTimeMarginNs` tolerance, plus one refresh cycle duration if nearest-refresh-cycle is used). One frame intentionally omits `presentStageQueries` to verify that no timing feedback is returned for it.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| PresentAtMode | `ABSOLUTE`, `RELATIVE` | [vktWsiPresentTimingTests.cpp#L2241-L2248](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2241-L2248) |
| Present modes | 7: `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `demand`, `continuous`, `fifo_latest_ready` | [vktWsiPresentTimingTests.cpp#L2250-L2262](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2250-L2262) |
| Present stages | 4: `queue_operations_end`, `request_dequeued`, `image_first_pixel_out`, `image_first_pixel_visible` | [vktWsiPresentTimingTests.cpp#L2264-L2273](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2264-L2273) |
| Time domains | 6: `device`, `clock_monotonic`, `clock_monotonic_raw`, `query_performance_counter`, `present_stage_local`, `swapchain_local` | [vktWsiPresentTimingTests.cpp#L2275-L2286](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2275-L2286) |
| Out-of-order results | 2: allow / disallow | [vktWsiPresentTimingTests.cpp#L2288-L2295](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2288-L2295) |
| Partial results | 2: allow / disallow | [vktWsiPresentTimingTests.cpp#L2297-L2304](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2297-L2304) |
| Present-at nearest refresh cycle | 2: `nearest` / `after` | [vktWsiPresentTimingTests.cpp#L2420-L2423](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2420-L2423) |

## Support / Feature Requirements

- **Device extensions (always required):** `VK_KHR_swapchain`, `VK_KHR_present_id2`, `VK_KHR_calibrated_timestamps`, `VK_EXT_present_timing`
- **Device extension (conditional):** `VK_KHR_shared_presentable_image` -- enabled if supported by the device
- **Device extension (conditional):** `VK_EXT_present_mode_fifo_latest_ready` -- enabled if the test uses `VK_PRESENT_MODE_FIFO_LATEST_READY_KHR`
- **Feature struct:** `VkPhysicalDevicePresentTimingFeaturesEXT` -- `presentTiming` must be `VK_TRUE`; `presentAtAbsoluteTime` must be `VK_TRUE` for absolute present-at tests; `presentAtRelativeTime` must be `VK_TRUE` for relative present-at tests
- **Feature struct:** `VkPhysicalDevicePresentId2FeaturesKHR` -- `presentId2` must be `VK_TRUE`
- **Surface capabilities:** `VkPresentTimingSurfaceCapabilitiesEXT::presentTimingSupported` must be true; `presentAtAbsoluteTimeSupported` / `presentAtRelativeTimeSupported` must be true for respective present-at modes; `presentStageQueries` must include the requested stage bits
- **Surface capabilities:** `VkSurfaceCapabilitiesPresentId2KHR::presentId2Supported` must be true
- **Per-test skip conditions:** If the requested present mode, present stage, or time domain is not supported by the surface, the test throws `NotSupportedError`

## Verification Methods

- **Present ID verification:** `PresentTimingHelper::verifyPresentIds` ([vktWsiPresentTimingTests.cpp#L519-L544](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L519-L544)) checks that the number of results matches the expected frame count, that present IDs follow the expected sequence (initial ID + step), and that timestamps are monotonically increasing.
- **Stage count and mask verification:** For each result, verifies that `presentStageCount` and the reported stage flags match the expected values.
- **Timing queue full detection:** `timingQueueTest` verifies that `VK_ERROR_PRESENT_TIMING_QUEUE_FULL_EXT` is returned when the queue is at capacity.
- **Timing queue resize:** `timingQueueTest` verifies that `vkSetSwapchainPresentTimingQueueSizeEXT` returns `VK_NOT_READY` when attempting to shrink a non-empty queue.
- **Counter monotonicity:** `getPastPresentationTiming` verifies that `timingPropertiesCounter` and `timeDomainsCounter` are set and non-decreasing across queries.
- **Present-at time accuracy:** `presentAtTest` verifies that actual presentation timestamps (at the `VK_PRESENT_STAGE_IMAGE_FIRST_PIXEL_VISIBLE_BIT_EXT` stage) are not earlier than the requested target time, within a tolerance of `kTargetTimeMarginNs` (100 us) plus one refresh cycle duration if `VK_PRESENT_TIMING_INFO_PRESENT_AT_NEAREST_REFRESH_CYCLE_BIT_EXT` is set.
- **Out-of-order enforcement:** When out-of-order results are disallowed, verifies that timestamps are strictly increasing across consecutive frames.
- **Time domain calibration:** `timeDomainCalibrationTest` takes calibrated timestamps before and after each present and verifies that the reported present stage timestamp falls within the calibrated window. Also verifies that the difference between host and present stage timestamps is within the reported calibration deviation plus `kCalibratedHostTimeMarginNs`.
- **Time domain property consistency:** `timeDomainPropertiesTest` verifies that `VK_TIME_DOMAIN_PRESENT_STAGE_LOCAL_EXT` is always reported, that time domain IDs are unique, and that domain data is stable when `timeDomainsCounter` has not changed.
- **Parallel thread safety:** `timingTestWithBackgroundQueryThreads` verifies that 4 concurrent threads can safely call `vkGetPastPresentationTimingEXT` while the main thread is presenting, and that all results are eventually collected.

## Notes / Uncertainties

- The `query` sub-group generates 168 leaf tests (7 present modes x 4 stages x 6 time domains) plus 1 parallel test. Many combinations may be skipped at runtime if the surface does not support the requested present mode or stage.
- The `present_at` sub-group generates 288 leaf tests (2 present-at modes x 3 allowed present modes x 6 time domains x 2 out-of-order x 2 partial x 2 nearest/after). Many may be skipped on implementations with limited present-at support.
- Timing verification relies on wall-clock measurements with tolerance margins (`kTargetTimeMarginNs` = 100 us, `kCalibratedHostTimeMarginNs` = 10 us), which may be affected by system load and scheduling jitter.
- The `retired_swapchain` test creates two swapchains in succession and queries timing data for both; the spec behavior for querying timing data on a retired swapchain may vary across implementations.
- The `parallel` test under `query` uses 4 background threads with a shared mutex for swapchain operations, testing thread safety of `vkGetPastPresentationTimingEXT`.
- The `present_at` test intentionally skips setting `presentStageQueries` on one frame to verify that no timing feedback is returned, reducing the expected result count by one.
