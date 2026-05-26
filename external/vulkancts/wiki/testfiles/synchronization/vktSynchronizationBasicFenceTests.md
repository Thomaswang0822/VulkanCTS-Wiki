# vktSynchronizationBasicFenceTests

## Overview

Basic fence tests for Vulkan synchronization. These tests validate the lifecycle and behavior of VkFence objects, including creation state, signaling via queue submission, waiting with various timeout and waitAll configurations, resetting, and empty submissions. The tests cover single-fence and multi-fence scenarios. The historical API test plan explicitly calls out fence waiting, reset/reuse, unsignaled status queries, and signaled-create behavior as objectives ([apitests.adoc](../../../../../doc/testspecs/VK/apitests.adoc#L384-L395)).

## Role of File

| Category | Group Name | Registration Path |
|---|---|---|
| synchronization (LEGACY) | `basic.fence` | `synchronization.basic.fence` |
| synchronization2 | N/A | N/A |

This file contributes **only to the LEGACY** synchronization category. Fence operations are not affected by the VK_KHR_synchronization2 extension, so there is no synchronization2 variant of these tests. The `basic.fence` group is added under `synchronization.basic` only when the synchronization type is LEGACY (see [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L61)).

## Source Code

- Implementation: [vktSynchronizationBasicFenceTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp)
- Header: [vktSynchronizationBasicFenceTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.hpp)

## Registration Hierarchy

```text
synchronization.basic.fence
├── one
├── multi
├── empty_submit
├── multi_waitall_false
├── one_signaled
└── multiple_signaled
```

The Level-3 root is `synchronization.basic.fence`, registered as the `fence` subgroup under `synchronization.basic` by [createBasicFenceTests()](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344). This group is LEGACY-only; the synchronization2 path in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp) does not call `createBasicFenceTests`. All six direct children are leaf test cases added with `addFunctionCase`.

## Test Families

### one — Single fence lifecycle

| Test Name | Function | Description |
|---|---|---|
| `one` | `basicOneFenceCase` | Creates a single unsignaled fence, submits an empty command buffer, waits for signaling, resets, and verifies all state transitions |

### multi — Multi-fence with simultaneous-use command buffer

| Test Name | Function | Description |
|---|---|---|
| `multi` | `basicMultiFenceCase` | Two fences with a simultaneous-use command buffer; tests submit-wait-reset-resubmit and waiting for both fences |

### empty_submit — Empty queue submission

| Test Name | Function | Description |
|---|---|---|
| `empty_submit` | `emptySubmitCase` | Submits an empty queue submission (commandBufferCount=0) with a fence and verifies the fence is signaled |

### multi_waitall_false — Multi-fence waitAll semantics

| Test Name | Function | Description |
|---|---|---|
| `multi_waitall_false` | `basicMultiFenceWaitAllFalseCase` | Two fences; exercises vkWaitForFences with waitAll=VK_FALSE and waitAll=VK_TRUE under various signaling states |

### one_signaled — Single pre-signaled fence

| Test Name | Function | Description |
|---|---|---|
| `one_signaled` | `basicSignaledCase` | Creates a single pre-signaled fence (VK_FENCE_CREATE_SIGNALED_BIT), verifies status, and waits |

### multiple_signaled — Multiple pre-signaled fences

| Test Name | Function | Description |
|---|---|---|
| `multiple_signaled` | `basicSignaledCase` | Creates 10 pre-signaled fences and waits for all of them |

## Parameter Dimensions

### FenceConfig

| Field | Type | Values | Description |
|---|---|---|---|
| `numFences` | uint32_t | 0, 1, 10 | Number of fences for signaled-fence tests; 0 means not applicable (used for non-signaled tests) |
| `videoCodecOperationFlags` | VideoCodecOperationFlags | 0 or codec flags | When non-zero, tests run on a video-capable queue via VideoDevice |

### Timeout Constants

| Constant | Value | Description |
|---|---|---|
| `SHORT_FENCE_WAIT` | 1000 (1 us) | Used to verify VK_TIMEOUT on unsignaled fences |
| `LONG_FENCE_WAIT` | 1000000000 (1 s) | Used for expected-successful waits |

## Support / Feature Requirements

| Test | Check Function | Requirement |
|---|---|---|
| `one` | `checkVideoSupport` | Video codec support if videoCodecOperationFlags != 0 |
| `one_signaled` | `checkVideoSupport` | Video codec support if videoCodecOperationFlags != 0 |
| `empty_submit` | `checkVideoSupport` | Video codec support if videoCodecOperationFlags != 0 |
| `multi` | `checkCommandBufferSimultaneousUseSupport` | VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT; on Vulkan SC requires commandBufferSimultaneousUse == VK_TRUE |
| `multi_waitall_false` | `checkCommandBufferSimultaneousUseSupport` | Same as `multi` |
| `multiple_signaled` | `checkCommandBufferSimultaneousUseSupport` | Same as `multi` |

## Verification Methods

### basicOneFenceCase

1. Create an unsignaled fence; verify `getFenceStatus` returns VK_NOT_READY.
2. Call `waitForFences` with SHORT_FENCE_WAIT; verify VK_TIMEOUT.
3. Verify `getFenceStatus` still returns VK_NOT_READY.
4. Begin and end an empty command buffer; submit to queue with the fence.
5. Call `waitForFences` with LONG_FENCE_WAIT; verify VK_SUCCESS.
6. Verify `getFenceStatus` returns VK_SUCCESS (signaled).
7. Call `resetFences`; verify `getFenceStatus` returns VK_NOT_READY (unsignaled again).

### basicSignaledCase

1. Create `numFences` fences with VK_FENCE_CREATE_SIGNALED_BIT.
2. Verify each fence has `getFenceStatus` == VK_SUCCESS immediately after creation.
3. Call `waitForFences` on all fences with waitAll=VK_TRUE and LONG_FENCE_WAIT.
4. Verify VK_SUCCESS.

### basicMultiFenceCase

1. Create two unsignaled fences and a simultaneous-use command buffer.
2. Submit the command buffer with fence[FIRST]; wait for it; verify VK_SUCCESS.
3. Reset fence[FIRST]; re-submit with fence[FIRST].
4. Call `waitForFences` on both fences with waitAll=VK_TRUE and SHORT_FENCE_WAIT; expect VK_TIMEOUT (fence[SECOND] not yet submitted).
5. Submit with fence[SECOND].
6. Call `waitForFences` on both with waitAll=VK_TRUE and LONG_FENCE_WAIT; verify VK_SUCCESS.

### emptySubmitCase

1. Create an unsignaled fence.
2. Call `queueSubmit` with commandBufferCount=0 and the fence.
3. Call `waitForFences` with LONG_FENCE_WAIT; verify VK_SUCCESS.

### basicMultiFenceWaitAllFalseCase

1. Create two unsignaled fences and a simultaneous-use command buffer.
2. Verify VK_TIMEOUT for waitAll=false when no fence is signaled.
3. Verify VK_TIMEOUT for waitAll=true when no fence is signaled.
4. Submit with fence[SECOND]; verify VK_SUCCESS for waitAll=false (any fence signaled).
5. Verify VK_TIMEOUT for waitAll=true (not all fences signaled).
6. Submit with fence[FIRST]; verify VK_SUCCESS for waitAll=false.
7. Verify VK_SUCCESS for waitAll=true (all fences signaled).

## Test Principles

- **Complete lifecycle coverage**: The `one` test walks through the entire fence lifecycle: create (unsignaled) -> submit -> wait -> signaled -> reset -> unsignaled.
- **Timeout validation**: SHORT_FENCE_WAIT (1 us) is used to confirm that `waitForFences` correctly returns VK_TIMEOUT when fences are not yet signaled, rather than blocking.
- **waitAll semantics**: The `multi_waitall_false` test systematically exercises both waitAll=VK_FALSE (wait for any) and waitAll=VK_TRUE (wait for all) under three signaling states: none, partial, and all.
- **Empty submission**: The `empty_submit` test verifies that a queue submission with zero command buffers still signals the associated fence, as required by the Vulkan specification.
- **Pre-signaled fences**: The `one_signaled` and `multiple_signaled` tests verify that VK_FENCE_CREATE_SIGNALED_BIT produces fences that are immediately in the signaled state and can be waited on without any queue submission.
- **Simultaneous use**: The `multi` and `multi_waitall_false` tests use VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT to allow the same command buffer to be submitted multiple times concurrently.

## Notes / Uncertainties

- These tests are LEGACY-only because fences are not part of the VK_KHR_synchronization2 extension. The synchronization2 path in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L63-L66) does not call `createBasicFenceTests`.
- The `basicSignaledCase` function is shared between `one_signaled` (numFences=1) and `multiple_signaled` (numFences=10), differing only in the FenceConfig parameter.
- On Vulkan SC, the `multi`, `multi_waitall_false`, and `multiple_signaled` tests require `commandBufferSimultaneousUse == VK_TRUE`, which may not be available on all SC implementations.
- Video codec operation flags are passed through but do not change the fence logic; they only affect which queue and device are used for submission.
