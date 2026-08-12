## Overview

**Core question:** Does `VK_EXT_present_timing` report and schedule supported presentation events with correct queue, clock, ordering, and target-time behavior?

- This page covers the four test families implemented by `vktWsiPresentTimingTests.cpp`: `basic`, `query`, `time_domain`, and `present_at`.
- The tests create timed swapchains, attach present IDs and `VkPresentTimingInfoEXT` to presentation requests, and retrieve asynchronous stage timestamps through `vkGetPastPresentationTimingEXT`.
- Validation covers surface capabilities, timing-results queue capacity, present IDs and stages, changing clock metadata, calibrated timestamps, concurrent retrieval, and absolute or relative target times.
- The WSI dispatcher registers the same family under nine platform branches. The hierarchy below uses `headless` as one exact mustpass-backed example.

## Background Knowledge

For the shared concepts asynchronous presentation and presentation completion, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- A presentation request passes through stages including queue-operation completion, request dequeue, first pixel output, and first pixel visibility. A surface advertises which stages it can timestamp.
- Presentation timing reports arrive asynchronously. Each timed swapchain owns a result queue; a nonzero `presentStageQueries` reserves a slot until the application retrieves a complete report.
- Time-domain values define the clocks used for target and result timestamps. Swapchains expose domain IDs and a change counter because the available domains can change with presentation-engine conditions.
- A relative target uses the previous presentation's first-pixel-visible stage as its origin. An absolute target names a time in the selected domain. The nearest-refresh-cycle flag permits selection of a nearby refresh boundary, while the unflagged form expresses a preference against early visibility.

## Registration Hierarchy

```text
wsi.headless.present_timing
├── basic
├── query
├── time_domain
└── present_at
```

Current mustpass data repeats this structure for `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, and `xlib`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `basic`, `query`, `time_domain`, `present_at` | Selects capability/queue checks, past-timing retrieval, clock metadata/calibration, or target-time scheduling. | [`createPresentTimingTests`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2443-L2449) |
| `basic` leaf | `surface_capabilities`, `timing_queue`, `retired_swapchain`, `large_queue_size` | Selects one fixed infrastructure behavior. | [`populateBasicGroup`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2306-L2312) |
| Query present mode | `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `demand`, `continuous`, `fifo_latest_ready` | Changes swapchain presentation behavior and result latency. | [`presentModes`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2250-L2262) |
| Query present stage | `queue_operations_end`, `request_dequeued`, `image_first_pixel_out`, `image_first_pixel_visible` | Selects the single stage timestamp requested by an ordinary query case. | [`presentStages`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2264-L2273) |
| Time domain | `device`, `clock_monotonic`, `clock_monotonic_raw`, `query_performance_counter`, `present_stage_local`, `swapchain_local` | Selects the advertised clock domain used for result timestamps, calibration, or present-at targets. | [`timeDomains`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2275-L2286) |
| Present-at mode | `absolute`, `relative` | Interprets `targetTime` as a timestamp or as a duration from the previous first-pixel-visible event. | [`presentAtModes`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2241-L2248) |
| Present-at present mode | `fifo`, `fifo_relaxed`, `fifo_latest_ready` | Restricts nonzero target times to the FIFO-based modes allowed by the API. | [`populatePresentAtGroup`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2366-L2395) |
| Result order | `allow_out_of_order_results`, `disallow_out_of_order_results` | Controls whether retrieval may return reports out of presentation order. | [`outOfOrderResults`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2288-L2295) |
| Report completeness | `allow_partial_results`, `disallow_partial_results` | Controls whether retrieval may return an incomplete set of requested stages. The host retains complete reports for final checking. | [`partialResults`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2297-L2304) |
| Target-cycle choice | `nearest`, `after` | Allows the nearest refresh boundary or applies the stricter early-visibility preference. | [`populatePresentAtGroup`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2412-L2423) |

Each platform branch contains 468 executable cases: 4 under `basic`, 169 under `query`, 7 under `time_domain`, and 288 under `present_at`.

## Behavior Parameters

The primary behavioral axis is the test family because each family tests a different API contract and uses a different verdict.

### `basic`: capability, result-queue, and swapchain-lifetime contracts

The four leaves isolate fixed infrastructure behavior. `surface_capabilities` requires `queue_operations_end` support when present timing is supported. `timing_queue` resizes and fills the result queue, verifies `VK_ERROR_PRESENT_TIMING_QUEUE_FULL_EXT` and `VK_NOT_READY`, drains reports, and proves that retrieval frees slots. `retired_swapchain` retrieves timing data from both an old swapchain and its replacement. `large_queue_size` submits twice the selected queue capacity and expects the queue to fill once before a full drain.

### `query`: stage timestamps across modes and clocks

Each matrix case requests one presentation stage in one supported time domain for ten frames under one present mode. The host associates reports with IDs `1, 4, 7, ...`, checks one returned stage per report, and requires nondecreasing nonzero timestamps after sorting by ID. `parallel.parallel` instead requests every surface-supported stage and lets four background threads call `vkGetPastPresentationTimingEXT` while the main thread presents ten frames.

### `time_domain`: domain metadata and calibrated-clock consistency

The six `calibration` leaves bracket three presentations with `vkGetCalibratedTimestampsKHR` calls in one registered time domain. A reported stage time must lie between the corresponding before/after calibrated values when all three values are nonzero, and host versus target-domain interval differences must stay within the measured deviation or the 10-microsecond floor. `properties.properties` presents 30 frames while checking required domain availability, unique IDs, nondecreasing counters, and stable domain data while the counter does not change.

### `present_at`: absolute and relative target scheduling

These cases schedule ten presentations at intervals of twice the current refresh duration. Absolute cases first obtain a nonzero report as a clock base; relative cases use the interval itself. One request sets `presentStageQueries` to zero, so the host expects nine feedback reports. It verifies present IDs, enforces increasing times when the case disallows out-of-order results, and checks nonzero `image_first_pixel_visible` times against the selected target. An `after` case allows up to `kTargetTimeMarginNs` (100 microseconds) of early error. A `nearest` case adds one refresh duration to that allowance.

## Shader Analysis

This test uses no shader. [`recordAndSubmitFrame`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L852-L882) clears each acquired image with `vkCmdClearColorImage` and transitions it to `VK_IMAGE_LAYOUT_PRESENT_SRC_KHR`; no shader module or graphics pipeline participates in the tested behavior. A representative shader and SPIR-V walkthrough therefore do not apply.

## Runtime Execution and Result Checking

- Instance setup enables the selected platform surface extension and `VK_KHR_get_surface_capabilities2`. Device setup requires `VK_KHR_swapchain`, `VK_KHR_present_id2`, `VK_KHR_calibrated_timestamps`, and `VK_EXT_present_timing`; it enables the absolute or relative present-at feature for the matching family.
- Swapchain creation sets `VK_SWAPCHAIN_CREATE_PRESENT_TIMING_BIT_EXT` and `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR`. Each test chooses a presentation-capable queue and a supported surface format, then allocates timing-result slots for its expected workload.
- For each frame, the host acquires an image with a fence, records a red transfer clear, transitions the image for presentation, and submits the command buffer. A render semaphore orders `vkQueuePresentKHR` after the clear.
- `presentWithTimingInfo` chains one `VkPresentTimingInfoEXT` through `VkPresentTimingsInfoEXT` and, for nonzero IDs, chains `VkPresentId2KHR` behind it. The timing record names a time-domain ID, requested stage mask, optional target, and target interpretation flags.
- `getPastPresentationTiming` accepts `VK_INCOMPLETE`, verifies that timing-property and time-domain counters were written and did not regress, refreshes swapchain timing properties when their counter changes, and stores complete reports. Polling sleeps for at least the refresh duration or 5 milliseconds until the required count arrives or 100 attempts expire.
- `PresentTimingHelper::verifyPresentIds` checks result count, ID progression, stage count, stage mask, and nondecreasing nonzero timestamps. The other families add queue-status, domain-property, calibration, concurrent-access, and target-time checks described above.
- Shared-demand and shared-continuous modes keep the one acquired shared-present image. Other modes acquire an image for each frame.
- The test never reads pixels back. The image clear provides valid presentable content but does not form part of the verdict.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Incorrect surface capability reporting, timing-results queue behavior, large-queue handling, or timing-data retention across swapchain retirement. |
| `query` | Incorrect past-timing retrieval, present-ID/stage association, timestamp ordering, counter updates, or concurrent query handling for a supported parameter path. |
| `time_domain` | Incorrect time-domain enumeration, identifier/counter stability, fallback-domain handling, or calibrated timestamp relationship. |
| `present_at` | Incorrect absolute/relative target interpretation, FIFO-mode scheduling, result-order/partial-query handling, feedback suppression, or early-presentation behavior. |

### Cause Analysis

#### Capability, queue, or retired-swapchain handling

**Possible failure symptoms:** a required capability bit is absent; queue resize returns the wrong status; a full queue accepts another timed request or rejects an untimed one; draining does not free capacity; the large queue fills more than once; or complete timing records cannot be retrieved from one of the two swapchains.

**Possible implementation causes:** investigation should compare surface capability reporting with enabled features, internal timing-slot accounting with complete-report retrieval, and timing-data lifetime with old-swapchain retirement. The specification requires a result slot for nonzero stage queries and releases complete-report slots after retrieval. The test result may identify one of these contracts without isolating its internal implementation.

#### Past-timing retrieval or association

**Possible failure symptoms:** a query case misses reports, returns an unexpected present ID, stage count, or stage bit, produces decreasing nonzero timestamps, regresses a counter, or fails during concurrent retrieval.

**Possible implementation causes:** source and specification evidence support checking result production, present-ID association, stage-mask handling, result ordering, atomic access to swapchain timing information, and counter updates. A failure in one parameter path can also involve support reporting for its present mode, stage, or domain; compare the exact failing path with the surface and swapchain properties.

#### Time-domain enumeration or calibration

**Possible failure symptoms:** `present_stage_local` is absent, IDs are duplicated, a counter regresses, domain data changes while its counter stays fixed, a fallback ID appears without a corresponding update, a stage timestamp falls outside its calibrated bracket, or host and target-domain intervals differ beyond the measured allowance.

**Possible implementation causes:** investigation should cover swapchain domain-list publication, stable ID mapping, fallback-domain reporting, counter synchronization, and calibrated timestamp conversion for the selected domain. Zero or changed-domain timestamps are skipped by design, so a reported mismatch comes from values the source deemed comparable.

#### Present-at target interpretation or feedback

**Possible failure symptoms:** the host receives a report for the request with no stage query, misses another expected ID, sees non-increasing times when disallowed, or observes first-pixel visibility earlier than the source's allowance for `after` or `nearest`.

**Possible implementation causes:** inspect absolute versus relative `targetTime` interpretation, local-stage clock selection, FIFO scheduling, nearest-cycle rounding, result-order and partial-result flags, and stage-query suppression. The feature does not promise exact physical-display timing; this CTS verdict applies its explicit early-time margin and skips zero timestamps.

## Case Pruning

### Requirement-based pruning

- The selected WSI platform must provide its surface extension, and the device must support `VK_KHR_swapchain`, `VK_KHR_present_id2`, `VK_KHR_calibrated_timestamps`, and `VK_EXT_present_timing` with the needed surface capabilities.
- A query case skips when its present mode, stage query, or time domain is not supported. Calibration also requires its registered domain in the calibratable-domain list.
- Absolute and relative target cases require their matching device feature and surface capability. `fifo_latest_ready` also requires its extension and feature.
- The source enables shared-presentable-image support when available so the `demand` and `continuous` query paths can run; unsupported modes skip.

### Design-based pruning

- `present_at` excludes `immediate`, `mailbox`, `demand`, and `continuous` because nonzero target times are restricted to `fifo`, `fifo_relaxed`, and `fifo_latest_ready`.
- Ordinary `query` cases request one stage at a time. Multi-stage coverage belongs to the large-queue, retired-swapchain, parallel-query, calibration, and present-at paths.
- Fixed image format selection, a 128 by 128 target, transfer-only rendering, and opaque identity presentation keep image content outside the timing matrix.
- The implementation compares only nonzero timestamps. A zero stage time means that stage's timing value is unavailable and does not support an ordering or target-time verdict.

## Key Takeaways

- The page covers four distinct contracts: timing infrastructure, past-stage queries, time-domain integrity, and target-time scheduling.
- Timed presentations consume swapchain result slots. Complete retrieval must free those slots, and the queue tests exercise this lifecycle at small and large capacities.
- Present IDs connect asynchronous reports to requests; stage masks and time-domain IDs define what each timestamp means.
- Present-at checks use source-defined tolerances and only comparable nonzero timestamps. They do not claim perfect physical-display timing.
- The test is host and presentation-engine focused. It clears images through transfer commands and performs no shader execution or pixel comparison.
- See `## Failure Meaning` for the evidence each failing test family provides and the limits of diagnosis from a CTS result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Device and feature setup | [`createDeviceWithWsi`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L196-L265) | Enables required extensions and case-dependent present-at features. |
| Surface and swapchain setup | [`getSurfacePresentTimingCapabilities` and `getBasicSwapchainParameters`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L267-L344) | Checks support and sets present-timing and present-ID creation flags. |
| Result model and shared checks | [`PresentTimingHelper`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L470-L545) | Stores normalized reports and checks IDs, stages, counts, and time order. |
| Time-domain metadata | [`TimeDomainHelper`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L608-L718) | Enumerates domains, IDs, and counters and compares stable snapshots. |
| Timed present and transfer frame | [`presentWithTimingInfo` and `recordAndSubmitFrame`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L819-L882) | Builds the `pNext` chain and records the shader-free image clear. |
| Result retrieval | [`getPastPresentationTiming` and `drainPresentationTimingResults`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L925-L1024) | Polls reports, checks counters, and releases complete entries. |
| Basic and query tests | [`surfaceCapabilitiesTest` through `timingTestWithBackgroundQueryThreads`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1026-L1564) | Implements capability, queue, matrix, large-queue, and parallel checks. |
| Retired swapchain | [`retiredSwapchainTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1566-L1662) | Retrieves timing data for an old swapchain and its replacement. |
| Present-at behavior | [`presentAtTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1674-L1913) | Computes targets and validates IDs, ordering, and early visibility. |
| Time-domain behavior | [`timeDomainPropertiesTest` and `timeDomainCalibrationTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1916-L2235) | Checks dynamic domain metadata and calibrated clock relationships. |
| Parameter arrays and registration | [`presentAtModes` through `createPresentTimingTests`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2241-L2449) | Defines every registered value and the four test families. |
| WSI dispatcher | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Registers `present_timing` under each platform branch. |
| Present-timing query specification | [`Present Timing Queries`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4738-L5291) | Defines queue allocation, timing/domain counters, asynchronous retrieval, ordering, and partial reports. |
| Target-time specification | [`VkPresentTimingInfoEXT`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7898-L8027) | Defines target semantics, stage queries, nearest-cycle selection, and queue-full behavior. |
| Mustpass registration | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L14827) | Confirms all platform-qualified executable paths. |
