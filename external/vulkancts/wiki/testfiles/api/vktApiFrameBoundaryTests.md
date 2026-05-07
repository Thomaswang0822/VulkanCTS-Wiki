# [vktApiFrameBoundaryTests.cpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1)

## Overview

Tests VK_EXT_frame_boundary by submitting command buffers with `VkFrameBoundaryEXT` structures attached to queue submissions and present operations. Verifies correct behavior for single frames, multiple submissions per frame, multiple frames, and overlapping submissions, both with and without VK_KHR_synchronization2. Also tests WSI swapchain integration with frame boundary.

## Role of File

Implementation-heavy. Contains test logic, support functions, and registration in one file.

## Source Code

| File | Description |
|------|-------------|
| [vktApiFrameBoundaryTests.cpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1) | Test implementation and registration |
| [vktApiFrameBoundaryTests.hpp](../../../modules/vulkan/api/vktApiFrameBoundaryTests.hpp#L1) | Declares `createFrameBoundaryTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L132) | Parent registration: `apiTests->addChild(createFrameBoundaryTests(testCtx))` |

## Registration Path

```
api
  +-- frame_boundary
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
            +-- <wsi_type_name>
```

## Test Hierarchy

```
frame_boundary
  +-- core
  |    Uses VkSubmitInfo with VkFrameBoundaryEXT in pNext
  |    +-- single_frame
  |    +-- single_frame_multi_submissions
  |    +-- multi_frame
  |    +-- multi_frame_multi_submissions
  |    +-- multi_frame_overlapping_submissions
  +-- sync2
  |    Uses VkSubmitInfo2 with VkFrameBoundaryEXT in pNext
  |    +-- single_frame
  |    +-- single_frame_multi_submissions
  |    +-- multi_frame
  |    +-- multi_frame_multi_submissions
  |    +-- multi_frame_overlapping_submissions
  +-- wsi
       Uses VkPresentInfoKHR with VkFrameBoundaryEXT in pNext
       +-- <per-WSI-type test cases>
```

## Test Families

### frame_boundary

Group name verified at [vktApiFrameBoundaryTests.cpp:507](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L507): `createTestGroup(testCtx, "frame_boundary", createTestCases)`.

Test types defined in enum `TestType` at [lines 61-69](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L61):

| Test Name | TestType | Description |
|-----------|----------|-------------|
| `single_frame` | TEST_TYPE_SINGLE_FRAME | One submission with frame end flag and frameID=1 |
| `single_frame_multi_submissions` | TEST_TYPE_SINGLE_FRAME_MULTIPLE_SUBMISSIONS | 4 submissions for same frameID=1, only last has frame end flag |
| `multi_frame` | TEST_TYPE_MULTIPLE_FRAMES | 4 sequential frames, each with frame end flag |
| `multi_frame_multi_submissions` | TEST_TYPE_MULTIPLE_FRAMES_MULTIPLE_SUBMISSIONS | 4 frames, each with 2 submissions (no-end then end) |
| `multi_frame_overlapping_submissions` | TEST_TYPE_MULTIPLE_OVERLAPPING_SUBMISSIONS | 4 frames with interleaved submissions |

The `core` and `sync2` subgroups are created by `createExecTestCases` at [line 469](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L469), which iterates all `TestType` values. The `wsi` subgroup is created by `createWsiTestCases` at [line 486](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L486), iterating all WSI types.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Extension use | EXTENSION_USE_NONE, EXTENSION_USE_SYNC2 | Controls VkSubmitInfo vs VkSubmitInfo2 path |
| Test type | 5 types | See table above |
| WSI type | All wsi::TYPE_LAST types | For wsi subgroup only |
| Image format | VK_FORMAT_R8G8B8A8_UNORM | Hard-coded at [line 221](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L221) |
| Image extent | 16x16 | Hard-coded at [line 215](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L215) |

## Support / Feature Requirements

- `VK_EXT_frame_boundary` required for all tests ([line 79](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L79))
- `VK_KHR_synchronization2` additionally required for `sync2` subgroup ([line 82](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L82))
- WSI subgroup requires `VK_KHR_surface`, `VK_KHR_swapchain`, and platform-specific WSI extension ([lines 89-91](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L89))

## Verification Methods

- **Submission completion**: Tests submit commands with frame boundary structures and wait on fences. If the submission completes without error, the test passes. No image content verification is performed for the core/sync2 tests ([line 297](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L297)).
- **WSI present**: The WSI test acquires a swapchain image, renders to it, and presents with a frame boundary structure. Passes if `queuePresentKHR` succeeds ([line 464](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L464)).

## Test Principles Observed

- API usage validation: exercises the frame boundary extension's core submission paths
- Synchronization variant coverage: tests both traditional and synchronization2 submission APIs
- WSI integration: validates frame boundary with real swapchain present operations

## Notes / Uncertainties

- The core and sync2 tests do not verify frame boundary behavior beyond successful submission; they do not check whether a frame boundary callback or tool would receive the correct metadata
- The WSI test iterates all WSI types but may skip unsupported ones at runtime
- The `VkFrameBoundaryEXT` structure is populated with frameID, image count, and image pointers but buffer count and tag fields are always zero/null
