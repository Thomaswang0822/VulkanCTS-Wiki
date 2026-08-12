## Overview

**Core question:** Does the implementation keep present IDs ordered per swapchain and make the matching present-wait call report completion or timeout at the right time?

- This page documents the `present_id_wait` test family implemented in `vktWsiPresentIdWaitTests.cpp` and registered below each platform-specific WSI branch.
- The `id` and `id2` families check how `vkQueuePresentKHR` associates zero, increasing, and absent IDs with presentations.
- The `wait` and `wait2` families check successful waits, repeated waits for completed IDs, timeout cases where valid, and independent ID streams on two swapchains.
- Version 1 uses `VkPresentIdKHR` and `vkWaitForPresentKHR`. Version 2 uses `VkPresentId2KHR` and `vkWaitForPresent2KHR`, with additional surface capability and swapchain-creation requirements.
- The fixed triangle shaders create valid rendered frames. The test verdict comes from Vulkan results, timeout measurements, and the dual-swapchain sequence, not from image readback.

## Background Knowledge

For the shared concept asynchronous presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- A `VkPresentIdKHR` or `VkPresentId2KHR` array associates each ID with the swapchain at the same index in `VkPresentInfoKHR`. A nonzero ID for one swapchain must be greater than earlier nonzero IDs submitted for that swapchain. Zero means that presentation has no associated ID. See [the Vulkan present-ID rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8144-L8203).
- Version 1 `vkWaitForPresentKHR` waits until the selected swapchain's tracked ID reaches at least the requested value or the timeout expires. Version 2 `vkWaitForPresent2KHR` waits for the submitted request with that ID to take effect or be replaced, and its valid usage requires that the ID came from a non-error present request. See [the Vulkan wait rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8206-L8265) and [the version 2 rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8342-L8404).

## Registration Hierarchy

```text
wsi.headless.present_id_wait
├── id
├── id2
├── wait
└── wait2
```

The dispatcher places the same `present_id_wait` family below the `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, and `xlib` platform branches. The tree above uses `headless` as the representative platform-qualified root. The family source registers all four children; their executable leaves are listed in the parameter sections below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` | Selects the native surface integration and its required instance extension. | [`createWsiTests` and `createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L83) |
| Test family | `id`, `id2`, `wait`, `wait2` | Selects the version 1 or version 2 ID and wait contract. | [`createPresentIdWaitTests`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1473-L1491) |
| ID leaf | `zero`, `increasing`, `interleaved` | Chooses the present-ID sequence for `id` and `id2`. | [`createPresentIdTests` and `createPresentId2Tests`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1407-L1429) |
| Wait leaf | `single_no_timeout`, `past_no_timeout`, `no_frames`, `no_frame_id`, `future_frame`, `two_swapchains` for `wait`; `single_no_timeout`, `past_no_timeout`, `two_swapchains` for `wait2` | Chooses successful, timeout, or per-swapchain wait behavior. | [`createPresentWaitTests` and `createPresentWait2Tests`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1431-L1469) |
| Present ID values | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `UINT64_MAX`, or no ID, depending on the leaf | Exercises zero/no-ID handling, monotonic ordering, the maximum 64-bit value, and independent streams. | [ID and wait sequences](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L823-L1109), [dual sequence](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1215-L1229) |
| Wait timeout | `0`, `1` second, `10` seconds | Selects an immediate check, a bounded timeout case, or a long completion wait. Values are passed in nanoseconds. | [`k10sec`, `k1sec`, and wait execution](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L65-L90) |
| Version 2 support | `presentId2Supported` and `presentWait2Supported` | Allows `id2` and `wait2` to run only when both capabilities are reported for the surface. | [`surfaceSupportsPresentIdWait2`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L92-L108) |

## Behavior Parameters

The primary behavioral axis is the test family. The leaf values refine the sequence within each family.

### `id`: version 1 present IDs

`zero` presents one frame with ID `0`. The test expects a successful present, while the zero value carries no associated ID. `increasing` presents IDs `1` and `UINT64_MAX`, checking the allowed increasing range. `interleaved` presents IDs `0`, `1`, no ID, and `UINT64_MAX` in one sequence. The no-ID presentation must not disturb the ID sequence.

### `id2`: version 2 present IDs

`id2` repeats the three ID sequences with `VkPresentId2KHR`. Version 2 also creates the swapchain with `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` and enables both `VK_KHR_present_id2` and `VK_KHR_present_wait2`, because the common version 2 setup sets both creation flags. The surface capability query must report both `presentId2Supported` and `presentWait2Supported`.

### `wait`: version 1 present waits

- `single_no_timeout` presents ID `1`, then waits for it with `k10sec` and expects `VK_SUCCESS`.
- `past_no_timeout` presents ID `1`, waits for it twice, then presents `UINT64_MAX`, waits for both IDs with zero and nonzero timeouts, and finally presents a no-ID frame and ID `0`. These later frames must not invalidate earlier completed waits.
- `no_frames` submits no presentation and waits for ID `1` with zero and `k1sec`; both calls must return `VK_TIMEOUT`.
- `no_frame_id` presents ID `0` or a frame with no ID, then waits for ID `1`; both timeout values must return `VK_TIMEOUT`.
- `future_frame` presents ID `1`, then waits for `UINT64_MAX` and `2`; each wait must time out because those IDs have not been submitted.
- `two_swapchains` presents paired IDs on two swapchains and waits on selected IDs on their matching swapchains.

### `wait2`: version 2 present waits

`single_no_timeout` and `past_no_timeout` use `vkWaitForPresent2KHR` with `VkPresentWait2InfoKHR`. `two_swapchains` runs the paired-ID sequence through the version 2 structures and flags. The family does not register the three version 1 timeout leaves: `vkWaitForPresent2KHR` requires the requested ID to have been associated with a non-error `vkQueuePresentKHR` request on that swapchain, so those cases would be invalid API calls rather than valid timeout tests.

## Shader Analysis

The source loads the fixed `WsiTriangleRenderer` vertex and fragment shaders. The vertex shader rotates a triangle using a frame-index push constant, and the fragment shader writes a constant magenta color. These shaders only provide a valid color-attachment workload before presentation. They do not generate, consume, or validate present IDs, and the CTS does not read the presented pixels. A representative shader walkthrough and SPIR-V subsection would therefore add no evidence about this test's behavioral contract.

## Runtime Execution and Result Checking

- `PresentIdWaitInstance::iterate` creates the WSI-specific instance, one surface, a device, a command pool, a FIFO swapchain, and the renderer. Version 2 adds `VK_KHR_get_surface_capabilities2` and checks both version 2 surface capability flags.
- Device creation enables `VK_KHR_swapchain` plus the extensions required by the selected family. It chains the matching `VkPhysicalDevicePresentIdFeaturesKHR`, `VkPhysicalDevicePresentWaitFeaturesKHR`, `VkPhysicalDevicePresentId2FeaturesKHR`, or `VkPhysicalDevicePresentWait2FeaturesKHR` structure when needed.
- `recordAndSubmitFrame` waits for and resets a rotating fence, acquires an image, records the triangle, submits it while waiting on the acquire semaphore, and signals the render-complete semaphore. The test allows `VK_SUBOPTIMAL_KHR` from acquisition and checks other results.
- For each present operation, the simple runner chains `VkPresentIdKHR` or `VkPresentId2KHR` only when the sequence supplies an ID. It checks the return from `vkQueuePresentKHR` against the expected result; `VK_SUBOPTIMAL_KHR` is accepted when success is expected.
- For each wait operation, version 1 calls `vkWaitForPresentKHR`; version 2 fills `VkPresentWait2InfoKHR` and calls `vkWaitForPresent2KHR`. A successful wait must return `VK_SUCCESS`. A timeout case must return `VK_TIMEOUT`.
- For expected timeouts, the host measures the call with `std::chrono::high_resolution_clock`. `calcTimeoutRange` accepts the requested nanosecond timeout with a 100 ms margin and clamps the range to the signed 64-bit limits.
- The dual-swapchain runner creates two windows, surfaces, swapchains, renderers, and frame streams. It presents both images together with an ID array ordered like the swapchain array, then waits only on the selected ID for each matching swapchain.
- Each simple sequence ends with `vkDeviceWaitIdle`. The dual path also waits for device idle and waits before resource destruction after an exception.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `id` | Incorrect version 1 present-ID structure handling, zero/no-ID treatment, or monotonic ID tracking for one swapchain. |
| `id2` | Incorrect version 2 capability, swapchain-flag, present-ID structure, zero/no-ID, or monotonic ID handling. |
| `wait` | Incorrect version 1 completion tracking, timeout result or duration, past/future ID handling, or per-swapchain isolation. |
| `wait2` | Incorrect version 2 capability, swapchain-flag, submitted-ID completion tracking, or per-swapchain isolation. |

All four families also depend on ordinary surface creation, swapchain creation, image acquisition, rendering submission, and presentation. A Vulkan error in that shared path does not by itself identify a present-ID defect.

### Cause Analysis

#### Version 1 present-ID association or ordering

**Possible failure symptoms:** An `id` leaf reports an unexpected result from `vkQueuePresentKHR`, or the `interleaved` sequence behaves as if a no-ID or zero-ID request changed the monotonic ID state.

**Possible implementation causes:** The implementation may associate an ID with the wrong swapchain array entry, treat zero as a usable ID, or reject a valid increasing transition to `UINT64_MAX`. The Vulkan rules require per-swapchain association and strictly increasing nonzero IDs, but the CTS result does not isolate which part of that contract failed.

#### Version 2 capability or present-ID setup

**Possible failure symptoms:** An `id2` or `wait2` case is unsupported even though the required capability flags are reported, or a present fails after the CTS supplies the version 2 structure and creation flags.

**Possible implementation causes:** Source and spec evidence support investigation of surface capability reporting, feature enablement, `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` or `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR` handling, and `VkPresentId2KHR` processing. The failure does not identify one of those mechanisms by itself.

#### Present completion and timeout behavior

**Possible failure symptoms:** A wait for a submitted ID fails to return `VK_SUCCESS`, a valid version 1 future/no-ID case returns success instead of `VK_TIMEOUT`, or the elapsed duration falls outside the requested timeout range.

**Possible implementation causes:** The presentation implementation may advance the tracked ID at the wrong point, complete a wait for an unsubmitted ID, fail to complete a submitted request, or return the wrong result at timeout. For version 2, a failure can also involve the separate request-completion rule for a submitted ID. A duration-only failure does not by itself prove an implementation defect: [the Vulkan specification permits implementation-dependent timeout adjustment that may exceed the requested period](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8222-L8226), while [the CTS source accepts only a fixed 100 ms margin](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L65-L89).

#### Per-swapchain isolation

**Possible failure symptoms:** `two_swapchains` waits return based on the ID submitted to the other swapchain, or a selected wait times out despite the matching presentation completing.

**Possible implementation causes:** The implementation may store or compare present IDs at device or queue scope instead of associating them with the `VkSwapchainKHR` passed to the wait. The source presents two IDs in one `VkPresentInfoKHR`, so an array-index or swapchain-association error can produce this symptom.

#### Shared WSI setup or rendering failure

**Possible failure symptoms:** Surface creation, swapchain creation, acquisition, submission, presentation, or device-idle checks fail before the ID-specific assertion runs.

**Possible implementation causes:** Investigation should cover the selected platform's surface integration, queue-family selection, FIFO swapchain setup, image ownership and synchronization, and the renderer's ordinary color-attachment path. The present-ID tests do not distinguish these shared failures from other WSI failures.

## Case Pruning

### Requirement-based pruning

- The test skips when `VK_KHR_surface`, the selected platform surface extension, or `VK_KHR_swapchain` is unavailable.
- `id` and `wait` require the matching version 1 device extensions. `id2` and `wait2` require `VK_KHR_get_surface_capabilities2`, `VK_KHR_present_id2`, and `VK_KHR_present_wait2`, plus both version 2 surface capability flags.
- The platform must support the requested native surface and queue family. The dual cases also require `maxWindowsPerDisplay >= 2`.
- Version 2 swapchains require both `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` and `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR` because the source sets both flags for every version 2 case.

### Design-based pruning

- `id2` reuses the version 1 ID sequences because the behavioral comparison is between the two API generations, not between different ID values.
- Version 2 omits `no_frames`, `no_frame_id`, and `future_frame` because their requested IDs would violate `vkWaitForPresent2KHR` valid usage.
- All cases use `VK_PRESENT_MODE_FIFO_KHR` and the common triangle renderer. The matrix isolates ID association and wait behavior instead of varying presentation modes or shader workloads.
- The registered hierarchy stops at the four test families. The static sequences and executable leaves provide the useful detail without expanding every leaf in the parseable tree.

## Key Takeaways

- Present IDs are monotonically increasing per swapchain. Zero and an absent ID do not create a waitable presentation.
- Version 1 can test timeout behavior for IDs that were never submitted. Version 2 cannot use those cases because its wait valid usage requires a submitted ID.
- The dual-swapchain sequence checks that an ID belongs to the swapchain whose presentation carried it.
- The timeout check covers both the returned `VkResult` and the measured duration, with a 100 ms margin.
- The renderer supplies valid frames but does not provide a pixel oracle. See `## Failure Meaning` for failure interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| WSI dispatcher | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L73) | Routes `present_id_wait` below each platform-specific WSI branch. |
| Family registration | [`createPresentIdWaitTests`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1407-L1491) | Registers the four families and exact executable leaves. |
| Version 2 surface query | [`surfaceSupportsPresentIdWait2`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L92-L108) | Checks both version 2 surface capability flags. |
| Device setup | [`createDeviceWithWsi`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L199-L274) | Adds mandatory extensions and version-specific feature structures. |
| Swapchain setup | [`getBasicSwapchainParameters`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L298-L344) | Selects FIFO and applies version 2 creation flags. |
| Frame submission | [`recordAndSubmitFrame`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L523-L566) | Acquires, renders, submits, and signals each frame. |
| Present and wait runner | [`PresentIdWaitSimpleInstance::run`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L568-L682) | Implements structure chaining, result checks, waits, and timeout measurement. |
| ID sequences | [`PresentIdZeroInstance` through `PresentIdInterleavedInstance`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L803-L913) | Defines the three `id` and `id2` leaves. |
| Wait sequences | [`PresentWaitSingleFrameInstance` through `PresentWaitFutureFrameInstance`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L914-L1109) | Defines success, past-ID, timeout, and future-ID cases. |
| Dual-swapchain runner | [`PresentWaitDualInstance::iterate`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1162-L1312) | Keeps IDs and waits paired with two swapchains. |
| Renderer programs | [`WsiTriangleRenderer::getPrograms`](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) | Supplies the fixed triangle shaders that provide the render workload. |
| Present-ID and wait specification | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8144-L8404) | Defines version 1 and version 2 association, wait, timeout, capability, and valid-usage rules. |
| Feature descriptions | [Present ID and wait features](../../../../vulkan-docs/src/chapters/features.adoc#L6444-L6532) | Defines the four feature structures enabled by the test setup. |
| Mustpass paths | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L14812-L14826) | Confirms the representative headless family and leaf coverage. |
