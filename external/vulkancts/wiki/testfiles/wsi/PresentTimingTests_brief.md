# Understanding Brief: WSI present timing tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_present_timing` reports and schedules swapchain presentations through supported stages and time domains while preserving queue, counter, ordering, and timing contracts.

## Background Knowledge

### Presentation timing is asynchronous and stage-specific

A `vkQueuePresentKHR` request passes through several presentation-engine stages. `VK_EXT_present_timing` can record timestamps for the supported stages named in `VkPresentTimingInfoEXT::presentStageQueries`, but those records may become available after the presentation has occurred. A swapchain therefore owns an internal timing-results queue that the application sizes and drains.

Why it matters here:

- The query tests ask for one or all supported stages, poll `vkGetPastPresentationTimingEXT`, and match complete reports to present IDs.
- Queue capacity affects whether a timed present succeeds. Retrieving complete reports releases queue slots for later presents.

### Time-domain identifiers bind clock values to a swapchain

`vkGetSwapchainTimeDomainPropertiesEXT` returns time-domain values with unique IDs. The list and its counter can change as surface or presentation-engine conditions change. A returned timing report may use a fallback domain ID if the requested domain cannot be used when the presentation engine processes the request.

Why it matters here:

- The tests select one advertised ID for each registered time-domain value and reject unsupported combinations.
- Property and calibration tests check counter behavior, ID uniqueness, stable data while the counter is unchanged, and timestamp consistency across calibrated clocks.

### Present-at requests express an earliest or nearest target

A nonzero absolute target names a time in the selected domain. A relative target is a duration from the previous presentation's `VK_PRESENT_STAGE_IMAGE_FIRST_PIXEL_VISIBLE_BIT_EXT` stage. Without the nearest-refresh-cycle flag, the application prefers that the image not become visible before the target. With the flag, the presentation engine may choose the nearest refresh-cycle boundary, including an earlier boundary when the target lies in the first half of that cycle.

Why it matters here:

- The test evaluates absolute and relative targets under FIFO-based present modes.
- Its early-presentation allowance is `kTargetTimeMarginNs`, plus one refresh duration for `nearest` cases.

## One Concrete Example

Consider:

```text
dEQP-VK.wsi.headless.present_timing.present_at.absolute.fifo.present_stage_local.disallow_out_of_order_results.disallow_partial_results.after
```

The host first obtains a nonzero presentation timestamp to establish a base. It then schedules ten presentations at intervals of twice the current refresh duration. Each present asks for all four timing stages except one deliberate request with `presentStageQueries` set to zero. The host expects nine reports for the scheduled sequence, verifies their present IDs, rejects non-increasing stage times because this case disallows out-of-order results, and checks that a nonzero `image_first_pixel_visible` time is no more than 100 microseconds earlier than its absolute target.

## End-to-End Test Flow

```text
[host] create the platform surface and require present-timing and present-ID support
[host] select a supported present mode, stage query, and swapchain time-domain ID for the registered case
[host] create a swapchain with PRESENT_TIMING and PRESENT_ID_2 flags and allocate its timing-results queue
[host] acquire a swapchain image, record a transfer clear to red, and transition the image for presentation
[device] execute the clear and signal the per-image render semaphore
[host] attach VkPresentTimingInfoEXT and VkPresentId2KHR to VkPresentInfoKHR, then call vkQueuePresentKHR
[presentation engine] process the request and produce requested stage timestamps asynchronously
[host] poll vkGetPastPresentationTimingEXT, accept VK_INCOMPLETE where allowed by enumeration, and collect complete reports
[host] update timing properties when counters change and continue polling until the expected reports arrive
[host] sort reports by present ID and apply the family-specific queue, ID, stage, clock, or target-time checks
```

The `basic`, `query`, `time_domain`, and `present_at` test families share this setup but use different frame counts and verdict rules.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The implementation creates no shader module or graphics pipeline. `recordAndSubmitFrame` records an image-layout transition, `vkCmdClearColorImage` with red, and a transition to `VK_IMAGE_LAYOUT_PRESENT_SRC_KHR`. Presentation timing rather than rendered content is the tested behavior.

The host builds these per-present structures:

- `VkPresentTimingInfoEXT` selects the time-domain ID, target interpretation, requested stages, and local-stage basis when needed.
- `VkPresentTimingsInfoEXT` associates one timing record with the one swapchain in `VkPresentInfoKHR`.
- `VkPresentId2KHR` supplies nonzero present IDs for result matching.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Swapchain and images | yes | yes | transfer writes; presentation engine reads | no | Each image becomes a timed presentation request. |
| Command buffers | yes | yes | device executes | no | They clear and transition each acquired image before presentation. |
| Acquire and render fences | yes | yes | device signals | host waits/resets | They make frame-slot and image reuse safe. |
| Render semaphores | yes | yes | queue signals; presentation waits | no | They order the clear before `vkQueuePresentKHR`. |
| Swapchain timing-results queue | sized by host | internal to presentation engine | presentation engine writes | host queries | It stores asynchronous reports and can become full. |
| Host result arrays | yes | no | no | yes | `PresentTimingHelper` stores reports, stage entries, counters, and normalized results for validation. |

## What Is Checked

- `basic.surface_capabilities` requires `queue_operations_end` when the surface reports present timing support.
- `basic.timing_queue` checks queue growth, shrink-to-zero, `VK_ERROR_PRESENT_TIMING_QUEUE_FULL_EXT`, `VK_NOT_READY` when shrinking a nonempty queue, and slot reuse after retrieval.
- `basic.retired_swapchain` obtains complete reports from both an old swapchain and its replacement. `basic.large_queue_size` checks a queue of 512 entries in immediate mode or 64 in FIFO fallback across twice that many frames.
- Each ordinary `query` case presents ten frames with IDs `1, 4, 7, ...`, retrieves every complete report, and checks the requested stage, stage count, ID sequence, and nondecreasing nonzero timestamps. `query.parallel.parallel` performs the retrieval from four background threads while the main thread presents.
- `time_domain.properties.properties` checks the required `present_stage_local` domain, unique IDs, nondecreasing counters, and unchanged domain data while its counter is stable. Each `time_domain.calibration` case brackets three presents with calibrated timestamp calls and checks both ordering and host/device interval deviation.
- Each `present_at` case schedules ten target times, expects nine timing reports because one request asks for no stage feedback, checks IDs and optional in-order behavior, and rejects visibility timestamps that are too early for the selected `after` or `nearest` rule.

The test does not read swapchain pixels. The red clear only supplies valid presentable image content.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `basic`, `query`, `time_domain`, `present_at`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Incorrect surface capability reporting, timing-results queue behavior, large-queue handling, or timing-data retention across swapchain retirement. |
| `query` | Incorrect past-timing retrieval, present-ID/stage association, timestamp ordering, counter updates, or concurrent query handling for a supported parameter path. |
| `time_domain` | Incorrect time-domain enumeration, identifier/counter stability, fallback-domain handling, or calibrated timestamp relationship. |
| `present_at` | Incorrect absolute/relative target interpretation, FIFO-mode scheduling, result-order/partial-query handling, feedback suppression, or early-presentation behavior. |

## Important Variations and Special Cases

- Source registration creates 468 executable cases per WSI platform: four `basic` leaves, 169 `query` leaves, seven `time_domain` leaves, and 288 `present_at` leaves. Current mustpass data repeats this set for nine platform branches.
- `query` crosses seven present modes, four stage queries, and six time domains, then adds `parallel.parallel`.
- `present_at` uses only `fifo`, `fifo_relaxed`, and `fifo_latest_ready`. It crosses two target modes, six time domains, two result-order policies, two partial-result policies, and `nearest`/`after` leaves.
- Unsupported present modes, stage queries, time domains, calibratable domains, present-at features, or surface capabilities produce `NotSupportedError` rather than an execution failure.
- Shared present modes reuse their one acquired image. `fifo_latest_ready` requires its extension and feature.
- Timing results may contain zero for an unavailable stage time. The source skips comparisons that need a nonzero timestamp.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Device and feature setup | [`createDeviceWithWsi`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L196-L265) | Enables swapchain, present ID, calibrated timestamps, present timing, and case-dependent present-at features. |
| Surface and swapchain setup | [`getSurfacePresentTimingCapabilities` and `getBasicSwapchainParameters`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L267-L344) | Checks surface support and sets both timing-related swapchain creation flags. |
| Result normalization and checks | [`PresentTimingHelper`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L470-L545) | Stores reports and verifies IDs, stage masks, counts, and time order. |
| Present submission | [`presentWithTimingInfo` and `recordAndSubmitFrame`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L819-L882) | Builds the timing/present-ID chain and records the transfer-only frame. |
| Past timing retrieval | [`getPastPresentationTiming` and `drainPresentationTimingResults`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L925-L1024) | Handles counters, complete reports, queue draining, and polling. |
| Basic and query execution | [`surfaceCapabilitiesTest` through `timingTestWithBackgroundQueryThreads`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1026-L1564) | Implements capability, queue, matrix-query, large-queue, and concurrent retrieval checks. |
| Retired swapchains | [`retiredSwapchainTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1566-L1662) | Checks data retrieval from old and replacement swapchains. |
| Target-time execution | [`presentAtTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1674-L1913) | Computes targets and applies ID, ordering, and early-time checks. |
| Time-domain checks | [`timeDomainPropertiesTest` and `timeDomainCalibrationTest`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L1916-L2235) | Validates domain metadata and calibrated clock relationships. |
| Registration matrix | [`populateBasicGroup` through `createPresentTimingTests`](../../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp#L2306-L2449) | Defines the four test families and all registered dimensions. |
| WSI family routing | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Registers `present_timing` under each platform branch. |
| Present-timing query semantics | [`Present Timing Queries`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4738-L5291) | Defines result queues, counters, domains, report availability, ordering, and partial results. |
| Per-present target semantics | [`VkPresentTimingInfoEXT`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7898-L8027) | Defines absolute/relative targets, nearest-cycle behavior, stage queries, and queue-full behavior. |
| Mustpass paths | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L14827) | Confirms the platform-qualified executable hierarchy. |

## Questions / Risk Points for User Audit

- Source, mustpass, and specification evidence agree on the four test families and the parameter matrices.
- The implementation uses transfer clears and no shader, so the final page should not contain a representative shader or SPIR-V walkthrough.
- `allow_partial_results` changes retrieval permissions. The host retains only complete reports for its final checks, so the page must not claim that the case requires the implementation to return a partial report.
- Present-at features provide timing capability rather than a strict physical-display guarantee. The final page should describe the CTS tolerance check, not a stronger guarantee.

No unresolved point changes the final page's semantics, walkthrough selection, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Keep asynchronous timing queues, time-domain IDs, and target-time interpretation as compact prerequisites.
- Use `basic`, `query`, `time_domain`, and `present_at` as the behavioral axis.
- Preserve the `### Failure Cause Mapping` table above verbatim.
- State that `recordAndSubmitFrame` uses transfer commands and that shader/SPIR-V analysis does not apply.
- Keep the runtime section centered on swapchain setup, timed presentation, result polling, and family-specific validation.
- Move detailed function navigation and specification links to the appendix.
