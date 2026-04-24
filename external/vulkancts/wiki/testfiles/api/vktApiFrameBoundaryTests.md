# [vktApiFrameBoundaryTests.cpp](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1)

## Overview

Tests the `VK_EXT_frame_boundary` extension, which allows applications to annotate command buffer submissions with frame boundary information. Validates that frame boundary tags can be correctly attached to queue submissions and swapchain present operations using both legacy `vkQueueSubmit` and `vkQueueSubmit2` (synchronization2) paths.

## Role of File

Implementation-heavy. Contains test logic, WSI integration, and registration in a single source file (~511 lines). The public entry point [createFrameBoundaryTests()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L504) assembles the full test tree.

## Source Code

- Source: [vktApiFrameBoundaryTests.cpp](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1)
- Header: [vktApiFrameBoundaryTests.hpp](../../modules/vulkan/api/vktApiFrameBoundaryTests.hpp#L1)
- Parent registration: `api` test group, child `frame_boundary` (non-VKSC only)

## Registration Path

```
api
 +-- frame_boundary
      +-- core
      +-- sync2
      +-- wsi
```

## Test Hierarchy

```
frame_boundary
 +-- core
 |    +-- single_frame
 |    +-- single_frame_multi_submissions
 |    +-- multi_frame
 |    +-- multi_frame_multi_submissions
 |    +-- multi_frame_overlapping_submissions
 +-- sync2
 |    +-- single_frame
 |    +-- single_frame_multi_submissions
 |    +-- multi_frame
 |    +-- multi_frame_multi_submissions
 |    +-- multi_frame_overlapping_submissions
 +-- wsi
      +-- <wsi_type>                   -- e.g. xlib, xcb, wayland, win32, android, etc.
```

## Test Families

### Core Family

Tests frame boundary annotation using `vkQueueSubmit` with `VkFrameBoundaryEXT` in the `pNext` chain of `VkSubmitInfo`. Uses [testCase()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L210) with `EXTENSION_USE_NONE`. Creates a 16x16 R8G8B8A8_UNORM image, records a clear-color-image command, and submits with frame boundary tags. Five submission patterns are tested:

- **single_frame**: One submission with `VK_FRAME_BOUNDARY_FRAME_END_BIT_EXT` and frameID=1 ([line 249](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L249))
- **single_frame_multi_submissions**: Four submissions for the same frameID=1, only the last has `FRAME_END_BIT` ([line 254](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L254))
- **multi_frame**: Four submissions, each a separate frame with `FRAME_END_BIT` and frameID 1-4 ([line 264](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L264))
- **multi_frame_multi_submissions**: Four frames, each with two submissions (non-end + end) ([line 271](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L271))
- **multi_frame_overlapping_submissions**: Interleaved submissions from frames 1-4 with overlapping non-end/end pairs ([line 281](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L281))

### Sync2 Family

Same test patterns as Core, but uses `vkQueueSubmit2` with `VkFrameBoundaryEXT` in the `pNext` chain of `VkSubmitInfo2`. Uses `EXTENSION_USE_SYNC2` which requires `VK_KHR_synchronization2` ([checkSupport()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L82)).

### WSI Family

Tests frame boundary annotation on swapchain present operations via `VkFrameBoundaryEXT` in the `pNext` chain of `VkPresentInfoKHR`. Uses [testCaseWsi()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L397). Acquires a swapchain image, records and submits a clear command, then presents with `FRAME_END_BIT` and frameID=1. Iterates over all WSI platform types.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Extension Use | EXTENSION_USE_NONE, EXTENSION_USE_SYNC2 |
| Test Type | single_frame, single_frame_multi_submissions, multi_frame, multi_frame_multi_submissions, multi_frame_overlapping_submissions |
| WSI Type | All platform WSI types (xlib, xcb, wayland, win32, android, etc.) |

## Support / Feature Requirements

- `VK_EXT_frame_boundary` required for all tests ([checkSupport()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L79))
- `VK_KHR_synchronization2` required for sync2 sub-group ([checkSupport()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L82))
- WSI tests require `VK_KHR_surface`, platform-specific surface extension, and `VK_KHR_swapchain` ([checkWsiSupport()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L85))
- Swapchain must support `VK_IMAGE_USAGE_TRANSFER_DST_BIT` ([createSwapchain()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L361))

## Verification Methods

- Core and Sync2 tests: Submit commands with frame boundary annotations and wait for fence completion. Tests pass if `vkQueueSubmit`/`vkQueueSubmit2` and `vkWaitForFences` return `VK_SUCCESS` ([testCase()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L297))
- WSI tests: Acquire, render, present with frame boundary annotation. Tests pass if `vkQueuePresentKHR` returns `VK_SUCCESS` ([testCaseWsi()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L466))
- No pixel-level verification is performed; these tests validate API usage correctness rather than rendering results

## Test Principles Observed

- Progressive complexity from single-frame single-submit to multi-frame overlapping submissions
- Both legacy and synchronization2 submission paths covered
- Frame boundary image references included in `VkFrameBoundaryEXT::pImages` for `FRAME_END_BIT` submissions ([submitCommands()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L148))
- WSI integration tests validate the present path with frame boundary

## Notes / Uncertainties

- The tests do not verify that frame boundary callbacks or debug tools actually receive the annotations; they only validate that the API calls succeed
- The overlapping submissions test pattern is hardcoded with a specific interleaving sequence ([line 281-291](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L281)) rather than being parameterized
- The WSI test uses `VK_PRESENT_MODE_FIFO_KHR` unconditionally ([createSwapchain()](../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L389))
- Buffer references in `VkFrameBoundaryEXT` are always zero (bufferCount=0, pBuffers=nullptr); no buffer-based frame boundary tests exist
