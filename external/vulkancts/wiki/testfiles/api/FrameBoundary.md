## Overview

**Core question:** Does the implementation accept a `VkFrameBoundaryEXT` structure chained through `VkSubmitInfo`, `VkSubmitInfo2`, and `VkPresentInfoKHR`, and complete the associated queue submission or present operation without returning an error?

- [vktApiFrameBoundaryTests.cpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp) implements the `frame_boundary` test family under the `api` test category. The same file holds the test logic, support checks, and registration.
- The family registers three intermediate nodes: `core`, `sync2`, and `wsi`. The first two exercise queue submission through `VkSubmitInfo` and `VkSubmitInfo2` respectively; the third exercises swapchain present through `VkPresentInfoKHR`.
- The core test idea is API acceptance: the test builds a `VkFrameBoundaryEXT`, chains it into the relevant submit or present structure, and passes only if `vk.queueSubmit`, `vk.queueSubmit2`, or `vk.queuePresentKHR` returns `VK_SUCCESS` and the surrounding fence wait or present call also succeeds.
- The page covers registered paths, the per-leaf submission patterns, runtime setup, pass/fail condition, and what a failure points to. It does not analyze shaders because no shader runs as part of the tested behavior.
- This test family is registered only when `CTS_USES_VULKANSC` is not defined; Vulkan SC builds do not include `frame_boundary` [vktApiTests.cpp#L127-L136](../../../modules/vulkan/api/vktApiTests.cpp#L127-L136).

## Background Knowledge

- **`VK_EXT_frame_boundary` extension.** The extension lets an application tag queue submissions and present operations with frame metadata that external tooling can consume. The conformance test does not validate tooling consumption; it validates that the implementation accepts the metadata structure in the `pNext` chain of submit and present calls.
- **`VkFrameBoundaryEXT` structure.** The structure carries a `frameID`, an optional set of `flags` (notably `VK_FRAME_BOUNDARY_FRAME_END_BIT_EXT`), and resource lists (`pImages`, `pBuffers`, `pTag`). In this test family only `frameID`, `imageCount`, and `pImages` are populated; buffer and tag fields remain zero or null [vktApiFrameBoundaryTests.cpp#L143-L155](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L143-L155).
- **Frame boundary placement.** The boundary structure is chained into `VkSubmitInfo::pNext`, `VkSubmitInfo2::pNext`, or `VkPresentInfoKHR::pNext`. The structure is the same in each path; what changes is the surrounding submission API.
- **`VK_KHR_synchronization2`.** The synchronization2 extension replaces `VkSubmitInfo` with `VkSubmitInfo2` and `vk.queueSubmit` with `vk.queueSubmit2`. The `sync2` intermediate node reuses the same test scenarios as `core` but routes them through the synchronization2 entry points.

## Registration Hierarchy

```text
api.frame_boundary
├── core
├── sync2
└── wsi
```

`createFrameBoundaryTests` creates the `frame_boundary` test family and [vktApiTests.cpp#L131](../../../modules/vulkan/api/vktApiTests.cpp#L131) attaches it to the `api` test category. [createTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) registers the three intermediate nodes, dispatching `core` and `sync2` to the shared `createExecTestCases` generator and `wsi` to `createWsiTestCases`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `core`, `sync2`, `wsi` | Selects the API path that carries `VkFrameBoundaryEXT`: `VkSubmitInfo`, `VkSubmitInfo2`, or `VkPresentInfoKHR`. | [createTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) |
| Execution test type | `single_frame`, `single_frame_multi_submissions`, `multi_frame`, `multi_frame_multi_submissions`, `multi_frame_overlapping_submissions` | Used by both `core` and `sync2`. Changes the number of submissions per frame, the number of frames, and whether submissions overlap across frame IDs. | [createExecTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469-L484), [TestType enum](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L60-L69) |
| WSI type | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` | Used by `wsi` only. Each leaf registers one `wsi::Type` value as the platform name returned by `wsi::getName()`. | [createWsiTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486-L492) |
| Frame boundary flag | `0`, `VK_FRAME_BOUNDARY_FRAME_END_BIT_EXT` | Set when the submission is the last one in a frame; cleared for intermediate submissions inside the same frame ID. | [submitCommands flag assignment](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L157-L158) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed format for the dummy image cleared and referenced by the frame boundary. | [image create info](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L221) |
| Image extent | `16x16` | Fixed extent for the dummy image. | [extent literal](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L215) |

## Behavior Parameters

The primary behavioral axis for this page is the **intermediate node** under `api.frame_boundary`. Each intermediate node selects a distinct Vulkan entry point that must accept `VkFrameBoundaryEXT` in its `pNext` chain. Within `core` and `sync2`, a secondary axis varies the frame and submission pattern through the execution test type. Within `wsi`, the secondary axis is the platform WSI type.

### core: Queue submission through `VkSubmitInfo`

`core` exercises the legacy queue submission path. [submitCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L129-L208) builds a `VkSubmitInfo` whose `pNext` points to a `VkFrameBoundaryEXT`, calls `vk.queueSubmit` with a fence, then waits on the fence. The intermediate node itself does not change the test scenarios; it selects `EXTENSION_USE_NONE` and reuses the same five execution test types as `sync2`. Pass requires `VK_CHECK` on `vk.queueSubmit` and `vk.waitForFences` to succeed.

### sync2: Queue submission through `VkSubmitInfo2`

`sync2` reuses the same five execution test types as `core` but routes them through the synchronization2 submission API. [submitCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L179-L202) builds a `VkSubmitInfo2` whose `pNext` points to the same `VkFrameBoundaryEXT`, calls `vk.queueSubmit2` with a fence, then waits on the fence. The `VkFrameBoundaryEXT` payload is identical to the `core` path; only the surrounding submit structure differs. Pass requires `VK_CHECK` on `vk.queueSubmit2` and `vk.waitForFences` to succeed.

### wsi: Swapchain present through `VkPresentInfoKHR`

`wsi` moves the frame boundary from queue submission to presentation. [testCaseWsi](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L397-L467) creates a platform display and window, builds a swapchain, acquires one image, records the same clear command buffer used by `core` and `sync2`, submits it with `acquireSemaphore` waiting, then chains a `VkFrameBoundaryEXT` (with `VK_FRAME_BOUNDARY_FRAME_END_BIT_EXT` set and `frameID = 1`) into `VkPresentInfoKHR::pNext` and calls `vk.queuePresentKHR`. Pass requires `VK_CHECK` on `vk.queuePresentKHR` to succeed. Each registered leaf is one WSI platform name.

### Execution test type: Secondary axis for `core` and `sync2`

Both `core` and `sync2` share the same five test type leaves, registered by [createExecTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469-L484). Each leaf changes the pattern of `frameID` and `lastInFrame` values submitted to the queue. The submission patterns come from the `TestType` enum and the switch in [testCase](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L247-L295).

- **`single_frame`**: One submission with `frameID = 1` and `lastInFrame = true`. The frame boundary is marked as the end of the frame on the only submission.
- **`single_frame_multi_submissions`**: Four submissions, all with `frameID = 1`. Only the fourth sets `lastInFrame = true`; the first three carry the boundary structure without the frame-end flag.
- **`multi_frame`**: Four submissions, one per frame (`frameID` from 1 to 4), each with `lastInFrame = true`. Frames do not overlap.
- **`multi_frame_multi_submissions`**: Four frames, each built from two submissions. The first submission in each frame has `lastInFrame = false`; the second has `lastInFrame = true`. `frameID` ranges from 1 to 4 across the four frames.
- **`multi_frame_overlapping_submissions`**: Eight submissions interleaving frames 1, 2, 1, 3, 2, 4, 3, 4. The last-in-frame markers land on submissions 3, 5, 7, and 8. This exercises frame boundary tracking when multiple frame IDs are in flight at the same time.

## Shader Analysis

No shader is part of the tested behavior. The command buffer recorded by [recordCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L94-L127) only transitions an image layout and calls `vk.cmdClearColorImage` to produce a known image for the frame boundary to reference. The test does not validate shader output, so no representative shader walkthrough is included.

## Runtime Execution and Result Checking

- **Resource setup.** The `core` and `sync2` paths create a single 16x16 `VK_FORMAT_R8G8B8A8_UNORM` 2D image with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, bind memory, and allocate a primary command buffer [testCase](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L215-L243). The `wsi` path replaces this with a swapchain image acquired from a platform surface [testCaseWsi](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L397-L429).
- **Command recording.** [recordCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L94-L127) begins the command buffer, inserts a pipeline barrier from `TOP_OF_PIPE` to `TRANSFER` that transitions the image to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, and clears it to white `{1.0f, 1.0f, 1.0f, 1.0f}`. No draw or dispatch is recorded.
- **Frame boundary payload.** For `core` and `sync2`, each call to [submitCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L129-L208) builds a fresh `VkFrameBoundaryEXT` with the current `frameID`, `imageCount = 1` when `lastInFrame` is true (otherwise 0), `pImages` pointing at the image when `lastInFrame` is true (otherwise null), and `VK_FRAME_BOUNDARY_FRAME_END_BIT_EXT` set only when `lastInFrame` is true. Buffer and tag fields are zero or null.
- **Submission and fence wait.** `core` chains the structure into `VkSubmitInfo::pNext` and calls `vk.queueSubmit`; `sync2` chains it into `VkSubmitInfo2::pNext` and calls `vk.queueSubmit2`. Both pass a freshly created fence and immediately call `vk.waitForFences` with an infinite timeout [submitCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L176-L207).
- **WSI present flow.** `wsi` acquires a swapchain image with `acquireSemaphore`, records and submits the clear command buffer with that semaphore as a wait dependency, then chains `VkFrameBoundaryEXT` (with `frameID = 1`, `imageCount = 1`, `pImages` pointing at the acquired swapchain image, and the frame-end flag set) into `VkPresentInfoKHR::pNext` and calls `vk.queuePresentKHR` [testCaseWsi](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L439-L464).
- **Pass/fail rule.** The `core` and `sync2` leaves return `tcu::TestStatus::pass("Pass")` after the fence wait completes successfully [testCase return](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L297). The `wsi` leaves return pass after `vk.queuePresentKHR` returns `VK_SUCCESS` [testCaseWsi return](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L466). There is no image-content verification in any path; the test only checks that the API calls return success.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | `vk.queueSubmit` or `vk.waitForFences` returned a non-success result when `VkFrameBoundaryEXT` was chained into `VkSubmitInfo::pNext`. |
| `sync2` | `vk.queueSubmit2` or `vk.waitForFences` returned a non-success result when `VkFrameBoundaryEXT` was chained into `VkSubmitInfo2::pNext`. |
| `wsi` | `vk.queuePresentKHR` returned a non-success result when `VkFrameBoundaryEXT` was chained into `VkPresentInfoKHR::pNext`, or the surrounding swapchain acquire or submit failed. |

All three intermediate nodes share the same pass condition shape: a `VK_CHECK` macro on the relevant Vulkan entry point must succeed. A failure in any leaf ultimately surfaces as a failed `VK_CHECK` or an unexpected exception from the support checks.

### Cause Analysis

#### Queue submission rejected the frame boundary pNext chain

**Possible failure symptoms:** A `core` or `sync2` leaf fails with the `VK_CHECK` macro reporting a non-`VK_SUCCESS` return from `vk.queueSubmit` or `vk.queueSubmit2`, or with `vk.waitForFences` returning a non-success result.

**Possible implementation causes:** The implementation may reject `VK_STRUCTURE_TYPE_FRAME_BOUNDARY_EXT` in the `pNext` chain of `VkSubmitInfo` or `VkSubmitInfo2` even though `VK_EXT_frame_boundary` is supported, mishandle the frame-end flag, or fail to accept the image handle passed through `pImages`. The `sync2` path additionally exercises the synchronization2 variant of the same chain, so a `sync2`-only failure would point to the `VkSubmitInfo2` pNext handling rather than the frame boundary extension itself. Confirming which condition triggered the rejection requires source-level investigation of the driver's pNext walking.

#### Present rejected the frame boundary pNext chain

**Possible failure symptoms:** A `wsi` leaf fails with the `VK_CHECK` macro reporting a non-`VK_SUCCESS` return from `vk.queuePresentKHR`, or the test throws before reaching present because swapchain acquisition or the supporting clear-submit step failed.

**Possible implementation causes:** The implementation may reject `VK_STRUCTURE_TYPE_FRAME_BOUNDARY_EXT` in `VkPresentInfoKHR::pNext`, may not honor the frame-end flag at present time, or may reject the swapchain image pointer carried by `pImages`. A failure here could also stem from WSI setup unrelated to the frame boundary, since the test creates a real surface, swapchain, and acquired image before reaching the present call. Separating frame-boundary rejection from generic present-path failures requires source-level investigation of the WSI and frame boundary interaction.

#### Support check or resource setup failure

**Possible failure symptoms:** The case throws `NotSupportedError` before reaching the submit or present call, or fails during image creation, memory binding, command pool allocation, or swapchain creation.

**Possible implementation causes:** [checkSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L77-L83) requires `VK_EXT_frame_boundary` for every leaf and additionally requires `VK_KHR_synchronization2` for `sync2`. [checkWsiSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L85-L92) requires `VK_KHR_surface`, `VK_KHR_swapchain`, and the platform-specific WSI extension for `wsi` leaves. The `wsi` path also throws `NotSupportedError` when the swapchain's `supportedUsageFlags` lacks `VK_IMAGE_USAGE_TRANSFER_DST_BIT` [createSwapchain](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L361-L362). These failures are not frame-boundary failures; they indicate the implementation does not expose the required extension or surface capability for the leaf under test.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_EXT_frame_boundary` [checkSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L77-L83), [checkWsiSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L85-L92).
- `sync2` leaves additionally require `VK_KHR_synchronization2` [checkSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L81-L82).
- `wsi` leaves additionally require `VK_KHR_surface`, `VK_KHR_swapchain`, and the platform-specific WSI extension returned by `wsi::getExtensionName(wsiType)` [checkWsiSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L89-L91).
- `wsi` leaves are skipped at runtime when the swapchain does not support `VK_IMAGE_USAGE_TRANSFER_DST_BIT` [createSwapchain](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L361-L362).
- The `wsi` path uses `wsi::TYPE_LAST` to iterate every registered WSI type [createWsiTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486-L491); platforms without a surface or display are skipped through the standard WSI support path.

### Design-based pruning

- The image format (`VK_FORMAT_R8G8B8A8_UNORM`), image extent (`16x16`), and image usage flags are fixed across all leaves. The test does not vary them because the frame boundary extension accepts any image handle; the image is only a placeholder payload.
- The `VkFrameBoundaryEXT` payload is fixed to populate only `frameID`, `imageCount`, `pImages`, and the frame-end flag. Buffer and tag fields are intentionally left zero or null in every inspected path; the test does not exercise the buffer or tag portions of the structure.
- The execution test type matrix is shared between `core` and `sync2`. The two intermediate nodes use the same five leaves because the only meaningful difference between them is the submission API path, not the submission pattern.
- The `wsi` path uses a fixed `frameID = 1` and a single present per leaf. It does not iterate the multi-frame or multi-submission patterns because the present operation is the focus of that path.

## Key Takeaways

- The test family validates API acceptance of `VkFrameBoundaryEXT`, not external tooling consumption of the metadata. A pass means the implementation accepted the structure and completed the submit or present call.
- `core`, `sync2`, and `wsi` cover the three documented chaining points for the extension: `VkSubmitInfo::pNext`, `VkSubmitInfo2::pNext`, and `VkPresentInfoKHR::pNext`.
- `core` and `sync2` share the same five execution test type leaves; the difference is only the submission entry point. A failure specific to `sync2` points to the `VkSubmitInfo2` pNext handling, not the frame boundary extension itself.
- The execution test type axis varies `frameID` and `lastInFrame` patterns, including overlapping frames in flight. The implementation is expected to accept these patterns without rejecting the boundary structure.
- The `wsi` leaves are platform-gated; absence of a surface or swapchain extension is reported as `NotSupportedError`, not as a failure.
- See `## Failure Meaning` for the mapping between failing leaves and the underlying cause categories.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration | [vktApiTests.cpp#L131](../../../modules/vulkan/api/vktApiTests.cpp#L131) | Attaches `createFrameBoundaryTests` to the `api` test category inside the `#ifndef CTS_USES_VULKANSC` block. |
| Family factory | [vktApiFrameBoundaryTests.cpp#L504-L508](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L504-L508) | Creates the `frame_boundary` test family root. |
| Intermediate node registration | [createTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) | Registers `core`, `sync2`, and `wsi` and dispatches their generators. |
| Execution test type registration | [createExecTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469-L484) | Registers the five shared leaves under `core` and `sync2`. |
| WSI type registration | [createWsiTestCases](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486-L492) | Registers one leaf per `wsi::Type`. |
| Support checks | [checkSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L77-L83), [checkWsiSupport](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L85-L92) | Gates leaves on `VK_EXT_frame_boundary`, `VK_KHR_synchronization2`, and WSI extensions. |
| Command recording | [recordCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L94-L127) | Records the image layout transition and clear used by every leaf. |
| Submission path | [submitCommands](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L129-L208) | Builds `VkFrameBoundaryEXT`, chains it into `VkSubmitInfo` or `VkSubmitInfo2`, submits, and waits on a fence. |
| Test type dispatch | [testCase switch](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L247-L295) | Implements the five `frameID` and `lastInFrame` patterns. |
| WSI present path | [testCaseWsi](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L397-L467) | Builds the swapchain, acquires an image, clears it, and presents with `VkFrameBoundaryEXT` chained into `VkPresentInfoKHR`. |
| Header declaration | [vktApiFrameBoundaryTests.hpp#L36](../../../modules/vulkan/api/vktApiFrameBoundaryTests.hpp#L36) | Declares `createFrameBoundaryTests`. |
