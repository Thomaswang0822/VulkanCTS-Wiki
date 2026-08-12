# Understanding Brief: WSI present ID and present wait tests

## One-Sentence Test Purpose

This test checks whether a presentation implementation associates monotonically increasing IDs with the correct swapchain requests and reports completion or timeout through the version 1 and version 2 present-wait APIs.

## Background Knowledge

### Present IDs belong to individual swapchains

`VkPresentIdKHR` and `VkPresentId2KHR` attach one 64-bit value to each corresponding swapchain entry in `VkPresentInfoKHR`. Zero means that the request has no associated present ID. Every nonzero ID must be greater than earlier nonzero IDs submitted for the same swapchain.

Why it matters here:

- A request without an ID does not advance the swapchain's tracked ID.
- One `vkQueuePresentKHR` call may carry separate ID sequences for multiple swapchains.

### Present waits observe presentation-engine progress

`vkWaitForPresentKHR` waits until the swapchain's tracked present ID reaches at least the requested value or the timeout expires. `vkWaitForPresent2KHR` waits for the request with the specified submitted ID to take effect in the presentation engine or be replaced, subject to its timeout.

Why it matters here:

- Version 1 permits the CTS to wait for an ID that has not been submitted and expect `VK_TIMEOUT`.
- Version 2 requires the requested ID to have been associated with a successful present request, so the equivalent negative cases would violate valid usage.

## One Concrete Example

Consider `dEQP-VK.wsi.headless.present_id_wait.wait.two_swapchains`. One `vkQueuePresentKHR` call presents to two swapchains with IDs 1 and 2. Later calls use IDs 4 and 3, then 5 and 6. Each swapchain's sequence increases independently: 1, 4, 5 for the first and 2, 3, 6 for the second. The test waits for selected IDs on the matching swapchain. A wait that consults a device-wide or queue-wide ID instead of the selected swapchain could return for the wrong presentation.

## End-to-End Test Flow

```text
[host] select one WSI platform, API family, and test case leaf
[host] check surface, swapchain, present-ID, present-wait, and version-specific support
[host] create one surface and swapchain, or two for two_swapchains
[host] acquire an image, record the shared triangle workload, and submit rendering
[device] render to the acquired swapchain image and signal a render-complete semaphore
[host] attach VkPresentIdKHR or VkPresentId2KHR when the sequence supplies an ID
[host] call vkQueuePresentKHR and check the expected result
[host] call vkWaitForPresentKHR or vkWaitForPresent2KHR for each requested wait
[host] check VK_SUCCESS or VK_TIMEOUT; for expected timeouts, check elapsed wall-clock time
[host] repeat the sequence, wait for device idle, and report the CTS result
```

The `two_swapchains` path creates two independent frame streams. It submits both rendered images in one present call, supplies two IDs in the same present-ID structure, then waits on selected ID and swapchain pairs.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `PresentIdWaitCase::initPrograms` loads the fixed `WsiTriangleRenderer` vertex and fragment shaders. The vertex shader rotates a triangle from a frame-index push constant, and the fragment shader writes magenta.
- The test sequence is static host data. Each `PresentAndWaitOps` entry specifies presents followed by waits, including IDs, expected results, timeout values, and whether timeout is expected.
- No generated shader variant, specialization constant, descriptor layout, or shader result controls the present-ID assertions.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Swapchain image or images | yes | yes | device writes; presentation engine reads | no | Each present ID and wait is associated with a particular swapchain request. |
| Per-frame command buffer | yes | yes | device reads | no | Records a valid rendered frame before presentation. |
| Acquire and render-complete semaphores | yes | yes | device waits/signals | host does not read payload | Order image acquisition, rendering, and presentation. |
| Rotating submission fences | yes | yes | device signals | host waits and resets | Bound the number of queued frames and permit resource reuse. |
| `VkPresentIdKHR` or `VkPresentId2KHR` arrays | yes | passed to `vkQueuePresentKHR` | presentation implementation reads | no | Associate each nonzero ID with the swapchain at the same array index. |
| `VkPresentWait2InfoKHR` | yes | passed to `vkWaitForPresent2KHR` | no shader access | host receives the result | Carries the version 2 ID and timeout. |

The test has no image readback or shader-written verdict buffer. Host-observed API results and elapsed time determine the result.

## What Is Checked

- Every present expected to succeed must return `VK_SUCCESS` or `VK_SUBOPTIMAL_KHR`.
- A non-timeout wait must return `VK_SUCCESS`.
- A timeout case must return `VK_TIMEOUT`.
- Expected timeout duration must fall within the requested timeout plus or minus 100 ms, with the lower bound clamped to zero.
- The dual-swapchain cases must complete waits for the selected ID on the selected swapchain without mixing the two ID streams.
- Version 2 runs only when both `presentId2Supported` and `presentWait2Supported` are true for each surface used.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `id`, `id2`, `wait`, `wait2`

The test case leaves refine each family. `zero`, `increasing`, and `interleaved` cover ID submission; `single_no_timeout`, `past_no_timeout`, timeout-negative leaves, and `two_swapchains` cover wait behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `id` | Incorrect version 1 present-ID structure handling, zero/no-ID treatment, or monotonic ID tracking for one swapchain. |
| `id2` | Incorrect version 2 capability, swapchain-flag, present-ID structure, zero/no-ID, or monotonic ID handling. |
| `wait` | Incorrect version 1 completion tracking, timeout result or duration, past/future ID handling, or per-swapchain isolation. |
| `wait2` | Incorrect version 2 capability, swapchain-flag, submitted-ID completion tracking, or per-swapchain isolation. |

All four families also depend on ordinary surface creation, swapchain creation, image acquisition, rendering submission, and presentation. A Vulkan error in that shared path does not by itself identify a present-ID defect.

## Important Variations and Special Cases

- `id` and `id2` share the same three sequences. `zero` submits zero, `increasing` submits 1 then `UINT64_MAX`, and `interleaved` submits zero, 1, no ID, then `UINT64_MAX`.
- `wait` adds three legal negative scenarios: no presentation, presentations with zero or no ID, and requests for future IDs. Each uses zero and/or one-second waits that must time out.
- `wait2` omits those negative scenarios because `vkWaitForPresent2KHR` requires an ID from a non-error `vkQueuePresentKHR` request on that swapchain.
- Both wait versions include success cases for one submitted ID, past IDs including repeated waits, and two independent swapchains.
- Version 2 requires `VK_KHR_get_surface_capabilities2`, both version 2 device extensions, both surface capability flags, and both `VK_SWAPCHAIN_CREATE_PRESENT_ID_2_BIT_KHR` and `VK_SWAPCHAIN_CREATE_PRESENT_WAIT_2_BIT_KHR`.
- All swapchains use `VK_PRESENT_MODE_FIFO_KHR`. The source chooses two desired images, clamped to the surface limits.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Version 2 surface support | [`surfaceSupportsPresentIdWait2`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L92-L108) | Queries and combines the two version 2 surface capability flags. |
| Device features | [`createDeviceWithWsi`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L199-L274) | Enables the feature structure corresponding to each requested extension. |
| Swapchain flags and FIFO mode | [`getBasicSwapchainParameters`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L298-L344) | Applies both version 2 flags and fixes the present mode. |
| Frame acquisition and submission | [`recordAndSubmitFrame`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L523-L566) | Produces a rendered image and the semaphore consumed by presentation. |
| Present and wait checks | [`PresentIdWaitSimpleInstance::run`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L568-L682) | Attaches IDs, checks present results, issues both wait APIs, and validates timeout duration. |
| ID sequences | [`PresentIdZeroInstance` through `PresentIdInterleavedInstance`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L803-L913) | Defines zero, increasing, and interleaved present operations. |
| Wait sequences | [`PresentWaitSingleFrameInstance` through `PresentWaitFutureFrameInstance`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L914-L1109) | Defines successful, past-ID, and version 1 timeout scenarios. |
| Two-swapchain path | [`PresentWaitDualInstance::iterate`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1162-L1312) | Presents paired IDs and waits against the corresponding swapchains. |
| Family and leaf registration | [`createPresentIdTests` through `createPresentIdWaitTests`](../../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L1407-L1491) | Registers all four families and their exact leaves. |
| WSI routing | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L73) | Places `present_id_wait` below each WSI platform branch. |
| Present ID and wait semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8144-L8404) | Defines version 1 and version 2 IDs, waits, capabilities, flags, and valid usage. |
| Mustpass paths | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L14812-L14826) | Confirms the four families and executable leaves for the headless branch. |

## Questions / Risk Points for User Audit

- The API result is the oracle. The triangle workload keeps presentation realistic but does not test shader output or displayed pixels.
- Version 1 and version 2 waits have related but distinct completion language and valid usage. The final page should not describe them as identical APIs.
- The timeout duration check uses a fixed 100 ms margin around the requested interval and may expose severe scheduling delay as a test failure.
- The hierarchy repeats under platform branches. The final tree should use one representative platform-qualified root and state the other branches in prose.

No unresolved point changes the final page's semantics, shader decision, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Keep per-swapchain monotonic ID tracking and the version-specific wait contract as compact prerequisites.
- Use `id`, `id2`, `wait`, and `wait2` as the behavior parameter values and preserve the failure mapping table verbatim.
- Explain the exact leaves in the parameter table and behavior subsections rather than expanding the registration tree beyond one level.
- State that the generic triangle shaders do not control the tested behavior. Do not create a representative shader walkthrough or SPIR-V subsection.
- Keep the runtime section centered on present structure chaining, result checks, timeout measurement, and dual-swapchain isolation.
