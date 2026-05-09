# [vktApiFrameBoundaryTests.cpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1)

## Overview

Tests `VK_EXT_frame_boundary` by submitting command buffers with `VkFrameBoundaryEXT` structures attached to queue submissions and present operations. Verifies correct behavior for single frames, multiple submissions per frame, multiple frames, and overlapping submissions, both with and without `VK_KHR_synchronization2`. Also tests WSI swapchain integration with frame boundary.

## Role of File

Implementation-heavy. Contains test logic, support functions, and registration in one file.

## Source Code

| File | Description |
|------|-------------|
| [vktApiFrameBoundaryTests.cpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1) | Test implementation and registration |
| [vktApiFrameBoundaryTests.hpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.hpp#L1) | Declares `createFrameBoundaryTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L132) | Parent registration: `apiTests->addChild(createFrameBoundaryTests(testCtx))` |

## Registration Hierarchy

```text
api.frame_boundary
├── core
├── sync2
└── wsi
```

The confirmed Level-3 root is `frame_boundary`, which [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L132) adds directly under `api`. [createFrameBoundaryTests()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L504-L507) creates that root group, and [createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) registers exactly three direct child subgroups: `core`, `sync2`, and `wsi`.

## Test Families

### core — Queue submission tests using `VkSubmitInfo`

[createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) registers `core` as the direct child subgroup for the baseline submission path by calling [`addTestGroup()`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L497) with `EXTENSION_USE_NONE`. [createExecTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469-L484) then expands this subgroup into five leaf tests: `single_frame`, `single_frame_multi_submissions`, `multi_frame`, `multi_frame_multi_submissions`, and `multi_frame_overlapping_submissions`.

Those leaf names come from the local `testName` table at [vktApiFrameBoundaryTests.cpp#L471-L477](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L471-L477), while the scenario semantics are driven by the `TestType` enum at [vktApiFrameBoundaryTests.cpp#L61-L68](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L61-L68). This branch exercises submissions built through the non-synchronization2 path, attaching `VkFrameBoundaryEXT` through `VkSubmitInfo`.

### sync2 — Queue submission tests using `VkSubmitInfo2`

[createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) registers `sync2` as the second direct child subgroup by calling [`addTestGroup()`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L498) with `EXTENSION_USE_SYNC2`. It reuses the same [createExecTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469-L484) generator as `core`, so it produces the same five leaf test names and frame-submission patterns.

The difference is the API path selected by the `ExtensionUse` parameter, which toggles the synchronization2 submission flow and therefore exercises `VkSubmitInfo2`-based submission with `VkFrameBoundaryEXT` attached in the submission chain.

### wsi — Swapchain present tests by WSI type

[createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) registers `wsi` as the third direct child subgroup, and [createWsiTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486-L491) expands it by iterating from `0` to `wsi::TYPE_LAST - 1`. Each leaf test is registered with the exact per-platform WSI name returned by [wsi::getName()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L490).

This branch covers present-time frame-boundary usage rather than queue-submission-only behavior. The WSI test path attaches `VkFrameBoundaryEXT` to [`VkPresentInfoKHR`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L453-L462) and passes when [`vk.queuePresentKHR()`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L464) succeeds.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Registration root | `api.frame_boundary` | Confirmed by [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L132) and [createFrameBoundaryTests()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L504-L507) |
| Direct child subgroup names | `core`, `sync2`, `wsi` | Registered by [createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L494-L500) |
| Extension use | `EXTENSION_USE_NONE`, `EXTENSION_USE_SYNC2` | Selects `VkSubmitInfo` vs `VkSubmitInfo2` execution paths in [createTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L497-L498) |
| Test type | `single_frame`, `single_frame_multi_submissions`, `multi_frame`, `multi_frame_multi_submissions`, `multi_frame_overlapping_submissions` | Leaf names from [vktApiFrameBoundaryTests.cpp#L471-L477](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L471-L477), mapped to enum values at [vktApiFrameBoundaryTests.cpp#L61-L68](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L61-L68) |
| WSI type | All `wsi::Type` values in `[0, wsi::TYPE_LAST)` | Iterated in [createWsiTestCases()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486-L491) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` | Hard-coded at [vktApiFrameBoundaryTests.cpp#L221](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L221) |
| Image extent | `16x16` | Hard-coded at [vktApiFrameBoundaryTests.cpp#L215](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L215) |

## Support / Feature Requirements

- `VK_EXT_frame_boundary` is required for all tests ([vktApiFrameBoundaryTests.cpp#L79](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L79)).
- `VK_KHR_synchronization2` is additionally required for the `sync2` subgroup ([vktApiFrameBoundaryTests.cpp#L82](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L82)).
- The `wsi` subgroup requires `VK_KHR_surface`, `VK_KHR_swapchain`, and the platform-specific WSI extension checked in [checkWsiSupport()](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L89-L91).

## Verification Methods

- **Submission completion**: the `core` and `sync2` branches submit commands with frame-boundary structures and wait on fences. These branches pass if the submission sequence completes without error; no image-content verification is performed in this path ([vktApiFrameBoundaryTests.cpp#L297](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L297)).
- **WSI present**: the `wsi` branch acquires a swapchain image, renders to it, and presents with a frame-boundary structure chained through `VkPresentInfoKHR`. It passes if [`vk.queuePresentKHR()`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L464) succeeds after setup and rendering.

## Test Principles Observed

- API usage validation: exercises the frame-boundary extension's queue-submission and present-operation paths.
- Synchronization variant coverage: tests both traditional and synchronization2 submission APIs.
- WSI integration: validates frame-boundary use with real swapchain present operations.

## Notes / Uncertainties

- The `core` and `sync2` branches verify successful submission completion rather than any external tooling callback or metadata-consumption behavior.
- The `wsi` branch iterates all registered WSI types, but unsupported platforms may be skipped at runtime by support checks.
- The `VkFrameBoundaryEXT` payload observed in this file populates `frameID`, `imageCount`, and image pointers, while buffer-count and tag-related fields remain zero or null in the inspected paths.
