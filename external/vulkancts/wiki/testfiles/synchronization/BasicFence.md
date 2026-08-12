## Overview

**Core question:** Do Vulkan fences report and transition between their required states when queue submissions signal them, when the host waits, and when the fence is reset or created signaled?

This page covers the six legacy `synchronization.basic.fence` test cases implemented and registered by [`createBasicFenceTests`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L368). The cases check one-fence lifecycle behavior, two-fence waits and reuse, an empty queue submission, and initially signaled fences. The source does not create a synchronization2 variant; the parent registration adds this test family only for legacy synchronization ([`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L61-L66)).

## Background Knowledge

- A `VkFence` has signaled and unsignaled states. Queue submission can signal a fence; the host can query it with `vkGetFenceStatus`, wait with `vkWaitForFences`, and reset it with `vkResetFences`. This is the queue-to-host dependency described by the Vulkan specification ([Fences](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-fences)).
- `vkWaitForFences` with `waitAll=VK_TRUE` waits until every listed fence is signaled. With `VK_FALSE`, one signaled fence is enough. If the condition is not met before the timeout, the result is `VK_TIMEOUT` ([`vkWaitForFences`](../../../../vulkan-docs/src/chapters/synchronization.adoc#vkWaitForFences)).

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

These six test case leaves are also present in the legacy mustpass file as `dEQP-VK.synchronization.basic.fence.*` ([`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L16-L21)). The Vulkan SC mustpass contains the corresponding `dEQP-VKSC` paths ([`vksc-default/synchronization.txt`](../../../mustpass/main/vksc-default/synchronization.txt#L16-L21)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `one`, `multi`, `empty_submit`, `multi_waitall_false`, `one_signaled`, `multiple_signaled` | Selects the fence behavior being checked. | [`createBasicFenceTests`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L349-L366) |
| `FenceConfig::numFences` | `0`, `1`, `10` | `1` and `10` select the number of initially signaled fences; `0` is used for the other families. | [`FenceConfig`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L45-L52), [`basicSignaledCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L131-L164) |
| `videoCodecOperationFlags` | `0` or video codec flags | Selects the normal synchronization device or a supported video-capable device/queue. It does not change the fence assertions. | [`checkVideoSupport`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L115-L119) |
| Wait timeout | `SHORT_FENCE_WAIT = 1000` ns; `LONG_FENCE_WAIT = 1000000000` ns | The short timeout checks that an unmet condition returns `VK_TIMEOUT`; the long timeout is used for waits expected to succeed. | [`SHORT_FENCE_WAIT` and `LONG_FENCE_WAIT`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L45-L46) |

## Behavior Parameters

The primary behavioral axis is the test family. Each family uses a different fence state or wait condition.

### `one` - single-fence lifecycle

[`basicOneFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L54-L113) creates an unsignaled fence, checks `VK_NOT_READY`, and confirms that a short wait returns `VK_TIMEOUT`. It submits an empty command buffer with the fence, waits successfully, checks `VK_SUCCESS`, resets the fence, and checks `VK_NOT_READY` again.

### `multi` - reuse and wait for both fences

[`basicMultiFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L166-L235) submits a command buffer with the first fence, waits for it, resets and reuses it, then verifies that waiting for both fences times out until the second submission signals the second fence. The command buffer is recorded with `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT` because it is submitted again.

### `empty_submit` - zero-command-buffer submission

[`emptySubmitCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L237-L259) calls `vkQueueSubmit` with `commandBufferCount=0` and `pCommandBuffers=nullptr`, but supplies a fence. The subsequent long wait must return `VK_SUCCESS`.

### `multi_waitall_false` - any versus all

[`basicMultiFenceWaitAllFalseCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L261-L340) checks two unsignaled fences, then signals only the second, and finally signals the first. In each state it compares `waitAll=VK_FALSE` with `waitAll=VK_TRUE`: neither condition is satisfied with no signaled fences, only the any condition is satisfied with one signaled fence, and both conditions are satisfied with both fences signaled.

### `one_signaled` - one initially signaled fence

`basicSignaledCase` creates one fence with `VK_FENCE_CREATE_SIGNALED_BIT`, checks that `vkGetFenceStatus` returns `VK_SUCCESS` immediately, and waits for it with `waitAll=VK_TRUE` ([registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L361-L363), [implementation](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L131-L164)). The Vulkan specification defines this flag as selecting the initial signaled state ([`VkFenceCreateFlagBits`](../../../../vulkan-docs/src/chapters/synchronization.adoc#VkFenceCreateFlagBits)).

### `multiple_signaled` - ten initially signaled fences

The same `basicSignaledCase` creates ten signaled fences and waits for all ten. This changes the count, not the fence-state rule ([registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L364-L366)).

## Shader Analysis

No shader or SPIR-V code is part of these tests. The command buffers contain no application-visible commands; they are used only where a queue submission is needed to exercise fence signaling.

## Runtime Execution and Result Checking

- The helpers select the synchronization device and queue. If `videoCodecOperationFlags` is nonzero, they construct a `VideoDevice` after checking the requested video support.
- `one`, `multi`, and `multi_waitall_false` create a command pool and command buffer. The command buffer is empty; the multi-fence cases record it for simultaneous use.
- Each case creates the required fence objects, submits work where applicable, and calls the Vulkan fence APIs through the device interface.
- The test compares each return value with the expected `VkResult` and checks queried fence states. Any mismatch returns a failing `tcu::TestStatus`; reaching the end returns pass.
- The short timeout is a bounded negative check. It is not evidence that a device operation completed; it checks that the requested wait condition was still unmet when the timeout expired.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `one` | Incorrect fence initial state, queue-to-host signal/wait behavior, status query, or reset behavior. |
| `multi` | Incorrect fence reuse or `waitAll=VK_TRUE` behavior with two submissions; simultaneous-use command-buffer support or setup may also be unavailable. |
| `empty_submit` | Incorrect handling of a zero-command-buffer queue submission with a fence, or fence wait behavior. |
| `multi_waitall_false` | Incorrect any-versus-all wait condition or transition between none, partial, and complete signaling. |
| `one_signaled` | Incorrect handling of `VK_FENCE_CREATE_SIGNALED_BIT` or waiting on an initially signaled fence. |
| `multiple_signaled` | Incorrect creation or all-fence wait behavior for ten initially signaled fences; simultaneous-use support or setup may also be unavailable. |

### Cause Analysis

#### Fence state and queue signal failures

**Possible failure symptoms:** `one` may report the wrong initial status, return `VK_SUCCESS` during the short wait, fail to become signaled after the queue submission, or remain signaled after `vkResetFences`.

**Possible implementation causes:** The implementation may not expose the fence state transitions required by the Vulkan fence model, or the queue completion and fence signal operation may not establish the expected queue-to-host dependency. The source checks the result of each operation but does not identify a particular implementation layer as the cause.

#### Any/all wait condition failures

**Possible failure symptoms:** `multi` or `multi_waitall_false` may succeed while one required fence is unsignaled, time out when one fence is already signaled and `waitAll=VK_FALSE`, or fail to succeed after all listed fences are signaled.

**Possible implementation causes:** The `waitAll` condition may be evaluated incorrectly, or fence reuse/submission state may not be tracked correctly. The specification defines `VK_FALSE` as an any-fence condition and `VK_TRUE` as an all-fences condition; further bug-location analysis requires implementation investigation.

#### Initial-signaled or empty-submission failures

**Possible failure symptoms:** `one_signaled` or `multiple_signaled` may create fences that query as `VK_NOT_READY`, or `empty_submit` may not complete its wait even though the submission contains zero command buffers.

**Possible implementation causes:** Fence creation may not honor `VK_FENCE_CREATE_SIGNALED_BIT`, or queue submission may mishandle the fence signal operation when `commandBufferCount` is zero. The test itself does not distinguish host wrapper, driver, or hardware causes.

## Case Pruning

### Requirement-based pruning

- The video variants are checked with `VideoDevice::checkSupport` when `videoCodecOperationFlags` is nonzero.
- `multi`, `multi_waitall_false`, and `multiple_signaled` require command-buffer simultaneous-use support. On Vulkan SC, the support check rejects `commandBufferSimultaneousUse == VK_FALSE`.

### Design-based pruning

- The source registers only one and ten initially signaled fences. Other counts are not part of this test family.
- `numFences=0` is a non-signaled-test configuration value, not a test case that creates zero fences.
- The fence family is legacy-only because `createBasicFenceTests` is not called from the synchronization2 registration path.

## Key Takeaways

- `one` checks the complete ordinary lifecycle: unsignaled creation, timeout, queue signal, successful wait, query, reset, and unsignaled state again.
- `multi_waitall_false` isolates the semantic difference between waiting for any fence and waiting for all fences by testing none, partial, and complete signaling.
- `empty_submit` checks fence signaling for a queue submission with no command buffers.
- The pre-signaled cases test the creation flag directly and do not need a queue submission to reach the signaled state.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Fence constants and configuration | [`SHORT_FENCE_WAIT`, `LONG_FENCE_WAIT`, `FenceConfig`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L45-L52) | Defines timeout and configuration dimensions. |
| Single-fence lifecycle | [`basicOneFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L54-L113) | Implements the create, wait, submit, query, and reset sequence. |
| Support checks | [`checkVideoSupport` and `checkCommandBufferSimultaneousUseSupport`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L115-L129) | Defines feature and Vulkan SC gating. |
| Pre-signaled cases | [`basicSignaledCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L131-L164) | Implements one- and ten-fence creation checks. |
| Two-fence reuse | [`basicMultiFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L166-L235) | Tests reuse and waiting for both fences. |
| Empty submission | [`emptySubmitCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L237-L259) | Tests a zero-command-buffer submission with a fence. |
| Any/all waits | [`basicMultiFenceWaitAllFalseCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L261-L340) | Tests none, partial, and complete signaling. |
| Registration | [`createBasicFenceTests`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L368) | Defines the exact six test case leaves. |
| Parent registration | [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L61-L66) | Establishes the legacy-only page boundary. |
| Legacy mustpass | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L16-L21) | Lists all six `dEQP-VK` cases. |
| Vulkan fence semantics | [`Fences`](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-fences) | Defines states and queue-to-host use. |
| Vulkan wait semantics | [`vkWaitForFences`](../../../../vulkan-docs/src/chapters/synchronization.adoc#vkWaitForFences) | Defines `waitAll`, timeout, and return values. |
| Vulkan initial state | [`VkFenceCreateFlagBits`](../../../../vulkan-docs/src/chapters/synchronization.adoc#VkFenceCreateFlagBits) | Defines `VK_FENCE_CREATE_SIGNALED_BIT`. |
