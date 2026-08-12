## Overview

**Core question:** Does swapchain presentation report coherent timing data while the application schedules frames through `VK_GOOGLE_display_timing`?

- This page covers the `display_timing` test family implemented in [vktWsiDisplayTimingTests.cpp](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp).
- The WSI dispatcher registers the same five present-mode intermediate nodes for each supported platform. Each contains a baseline `reference` test case and a `display_timing` test case.
- Both test cases render and present 300 frames. The timed case supplies desired presentation times, queries past presentation records, checks their timestamps, and adjusts its target frame interval from the returned data.
- The host performs all timing checks. The shaders only render a frame-dependent color pattern into the swapchain image.

## Background Knowledge

For the shared concepts asynchronous presentation and presentation timing, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- `VkPresentTimeGOOGLE` pairs an application-provided `presentID` with a `desiredPresentTime`. A nonzero desired time asks the presentation engine not to display the image before that time.
- `vkGetPastPresentationTimingGOOGLE` returns records after presentation. Each record reports the requested time, the actual display time, the earliest possible display time, and the processing margin. All times use nanoseconds against a monotonically increasing clock.
- `vkGetRefreshCycleDurationGOOGLE` reports the interval between display refresh-cycle starts. An application can use that duration to choose a target image-present interval and revise the target when frames arrive late or leave enough margin for a faster rate.
- The specification defines full `VK_GOOGLE_display_timing` semantics for `VK_PRESENT_MODE_FIFO_KHR`. Other present modes permit different treatment, including immediate display or replacement of an image before display.

## Registration Hierarchy

The implementation repeats this hierarchy under each WSI platform. `headless` provides one concrete mustpass-backed example:

```text
wsi.headless.display_timing
├── fifo
├── fifo_relaxed
├── immediate
├── mailbox
└── fifo_latest_ready
```

Each shown intermediate node contains the `reference` and `display_timing` test case leaves. The [default WSI mustpass list](../../../mustpass/main/vk-default/wsi.txt#L11528-L11537) confirms those ten paths for `headless`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` in the default mustpass list | Selects the native display, window, surface extension, and surface implementation. The `display_timing` family logic stays the same. | Default mustpass paths for [Android](../../../mustpass/main/vk-default/wsi.txt#L20-L29), [direct](../../../mustpass/main/vk-default/wsi.txt#L4428-L4437), [direct DRM](../../../mustpass/main/vk-default/wsi.txt#L7970-L7979), [headless](../../../mustpass/main/vk-default/wsi.txt#L11528-L11537), [Metal](../../../mustpass/main/vk-default/wsi.txt#L15449-L15458), [Wayland](../../../mustpass/main/vk-default/wsi.txt#L20236-L20245), [Win32](../../../mustpass/main/vk-default/wsi.txt#L24157-L24166), [XCB](../../../mustpass/main/vk-default/wsi.txt#L28079-L28088), and [Xlib](../../../mustpass/main/vk-default/wsi.txt#L32001-L32010) |
| Present-mode intermediate node | `fifo`, `fifo_relaxed`, `immediate`, `mailbox`, `fifo_latest_ready` | Selects swapchain presentation semantics. It also controls whether the deliberate present-ID-80 timing perturbation runs. | [present mode registration](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1089-L1123) |
| Test case leaf | `reference`, `display_timing` | Selects baseline presentation or extension-driven scheduling and timing checks. This is the primary behavioral axis. | [test case registration](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1108-L1119) |

Fixed execution values include 300 frames, 16 quads per draw, six fences, and at most 20 out-of-date recoveries. These values bound the run but do not create registered cases.

## Behavior Parameters

The test case leaf is the primary behavioral axis because it switches the extension behavior and all timing validation on or off.

### `reference`: baseline presentation

The reference case exercises the common WSI path without adding `VkPresentTimesInfoGOOGLE` to `VkPresentInfoKHR`. It acquires, renders, submits, and presents each image, so failures isolate setup, rendering, synchronization, swapchain, or ordinary presentation behavior shared with the timed case. The source enables only `VK_KHR_swapchain` for this device, although its support-check loop still checks both device-extension names.

### `display_timing`: scheduled presentation and timing feedback

The timed case enables `VK_GOOGLE_display_timing`, queries the refresh duration, assigns a `presentID` and desired time to each present, and consumes returned `VkPastPresentationTimingGOOGLE` records. It checks timestamp coherence and one deliberate late-present condition, then uses late or early observations to choose a target interval of one or two refresh durations.

## Shader Analysis

The shaders do not implement the timing property or produce the pass/fail signal, so this page has no representative shader walkthrough or SPIR-V subsection.

`Programs::init` creates a fixed vertex shader that derives full-screen triangle positions from `gl_VertexIndex` and a fragment shader that mixes the pushed frame index with `gl_FragCoord` to produce a changing color pattern. The host does not read pixels back. The presentation engine receives distinct rendered frames, while extension queries and host timestamps provide all timing evidence.

## Runtime Execution and Result Checking

- The test creates a native display and window, a surface, a present-capable queue, and a swapchain for the selected present mode. Unsupported present modes stop as not supported.
- Per-swapchain resources include image views, framebuffers, a render pass, a graphics pipeline, acquire/render semaphores, and six fences. The fence ring limits command-buffer reuse while frames remain in flight.
- The timed case calls `vkGetRefreshCycleDurationGOOGLE` after swapchain creation. It starts with a target image-present duration equal to one refresh duration.
- Each iteration waits for the reusable fence when needed, acquires an image, records a draw with the frame index as a fragment push constant, and queries newly available past-presentation records before submitting the current draw.
- For every returned record, the host compares `actualPresentTime` with the timestamp sampled before the matching `vkQueuePresentKHR`. An image reported as displayed before that host timestamp fails the test.
- Initial timing records synchronize the future desired-time sequence with observed presentation time. Later records count as late when `actualPresentTime` exceeds `desiredPresentTime + refreshDuration + 1 ms`. A record indicates spare timing margin when `actualPresentTime > earliestPresentTime` and `presentMargin > 2 ms`.
- The host raises the refresh-duration multiplier to at most two after a late observation and lowers it to at least one after an observation with spare margin. The host favors a late observation if the same query batch contains both classifications.
- For present ID 80 in `fifo`, `fifo_relaxed`, and `immediate`, the test shifts the submitted desired time one second earlier than the normal schedule. If that record reaches the late branch, the lateness beyond one refresh duration must exceed half a second. `mailbox` and `fifo_latest_ready` skip this perturbation because their queues may replace images.
- The timed path attaches `VkPresentTimesInfoGOOGLE`; the reference path presents without it. Both paths check `vkQueuePresentKHR` and its per-swapchain result.
- `VK_ERROR_OUT_OF_DATE_KHR` causes swapchain-resource recreation and restarts the frame index. A twenty-first occurrence fails. Other Vulkan errors fail through the result collector.
- The case returns the accumulated result after 300 completed frames. The source does not require one timing record per present, compare rendered pixels, or assert after the loop that a record for present ID 80 arrived.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reference` | Common WSI setup, rendering, synchronization, acquisition, presentation, or swapchain-recreation failure. |
| `display_timing` | A common WSI-path failure, incoherent returned presentation timestamps, an insufficient late-present interval for the checked present-ID-80 record, or a `VK_GOOGLE_display_timing` query/presentation failure. |

### Cause Analysis

#### Common WSI-path failure

**Possible failure symptoms:** The case reports an error while creating or recreating WSI resources, acquiring an image, submitting rendering, or presenting. Both test case leaves can fail through this path.

**Possible implementation causes:** The selected platform's surface or swapchain path may mishandle required extension setup, presentation support, image acquisition, queue synchronization, or swapchain replacement. The failing Vulkan call and CTS log identify the next source-level investigation point.

#### Incoherent returned presentation timestamps

**Possible failure symptoms:** A returned `actualPresentTime` precedes the host timestamp recorded before the corresponding `vkQueuePresentKHR` call.

**Possible implementation causes:** `VkPastPresentationTimingGOOGLE` must identify the earlier present by `presentID` and report when its image was displayed. A wrong ID association, clock-domain mismatch, or invalid presentation-engine timestamp can produce this ordering contradiction.

#### Insufficient checked late-present interval

**Possible failure symptoms:** Present ID 80 enters the late branch, but the measured excess beyond `desiredPresentTime + refreshDuration` is no more than half a second, despite the one-second perturbation.

**Possible implementation causes:** The presentation engine may report a desired or actual time that does not match the submitted present, or the implementation may associate the returned timing record with the wrong `presentID`. The check only runs when that record appears and meets the late classification.

#### Display-timing query or timed-presentation failure

**Possible failure symptoms:** The timed case reports an error from the refresh-duration query, the past-presentation query, or a presentation carrying `VkPresentTimesInfoGOOGLE`.

**Possible implementation causes:** The implementation may fail extension command dispatch, swapchain timing-state maintenance, asynchronous history retrieval, or processing of the timed-present `pNext` chain. The returned error and log determine which path needs inspection.

## Case Pruning

### Requirement-based pruning

- The instance requires `VK_KHR_surface`, the selected platform surface extension, `VK_KHR_display` for display surfaces, and `VK_EXT_direct_mode_display` for `direct_drm`.
- Device setup requires `VK_KHR_swapchain`. The source also checks advertised support for `VK_GOOGLE_display_timing` for both test case leaves, although only `display_timing` enables it.
- The selected surface must advertise the registered present mode. Otherwise, the case reports not supported before swapchain creation.

### Design-based pruning

- All five present-mode intermediate nodes receive both test case leaves; the registration matrix has no omitted mode/leaf pair.
- The deliberate present-ID-80 perturbation excludes `mailbox` and `fifo_latest_ready`. Replacing queued images makes the expected late record unreliable for those modes.
- The test does not turn frame count, quad count, fence count, or target refresh multiplier into registered dimensions.

## Key Takeaways

- `reference` and `display_timing` share the same rendering and presentation loop; the timed leaf adds scheduling metadata, timing-history queries, and host checks.
- The decisive failure check compares returned display time against the recorded call time. The present-ID-80 check adds one bounded late-presentation probe for three present modes.
- The host uses early and late timing observations to choose a target interval of one or two refresh durations, matching the feedback use described by the extension.
- Shader output makes frames visually distinct but does not validate timing. See `Failure Meaning` for the host-observed failure paths and their limits.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Device and extension creation | [createDeviceWithWsi](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L105-L136) | Selects enabled extensions and performs the unconditional support loop. |
| Swapchain configuration | [createSwapchainConfig](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L502-L578) | Checks the present mode and builds the swapchain parameters. |
| Resource and timing initialization | [DisplayTimingTestInstance::initSwapchainResources](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L638-L687) | Creates swapchain resources and initializes refresh-based scheduling. |
| Timing checks and adaptation | [DisplayTimingTestInstance::render](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L737-L887) | Consumes timing records, performs checks, and adjusts the target interval. |
| Timed and reference presentation | [presentation branches](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L905-L975) | Submits desired times, injects the present-ID-80 case, or uses baseline presentation. |
| Completion and out-of-date recovery | [DisplayTimingTestInstance::iterate](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L986-L1046) | Defines the 300-frame completion rule and recreation limit. |
| Shader source | [Programs::init](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1048-L1085) | Generates the frame-dependent render pattern. |
| Registration | [createDisplayTimingTests](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1089-L1124) | Registers all present-mode intermediate nodes and both test case leaves. |
| WSI dispatch | [vktWsiTests.cpp](../../../modules/vulkan/wsi/vktWsiTests.cpp#L42-L81) | Attaches this test family under each platform-specific WSI branch. |
| Extension timing semantics | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5293-L5465) | Defines refresh duration, timing-history fields, and present-mode behavior. |
| Desired presentation times | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8077-L8141) | Defines the timed-present structures and requested-time contract. |
| Representative mustpass registration | [default WSI mustpass list](../../../mustpass/main/vk-default/wsi.txt#L11528-L11537) | Confirms the five modes and two leaves under `wsi.headless.display_timing`. |
