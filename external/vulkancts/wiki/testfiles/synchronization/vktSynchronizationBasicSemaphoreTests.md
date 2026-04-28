# vktSynchronizationBasicSemaphoreTests

## Overview

Basic semaphore tests for Vulkan synchronization. These tests validate the behavior of binary and timeline semaphores across single-queue and multi-queue scenarios, including signal/wait chains, multi-queue synchronization, and timeline-specific features such as CPU wait/signal and value-based waiting. The file contributes to both the LEGACY and synchronization2 categories via the `SynchronizationType` parameter.

## Role of File

| Category | Group Name | Registration Path |
|---|---|---|
| synchronization (LEGACY) | `basic.binary_semaphore` | `synchronization.basic.binary_semaphore` |
| synchronization (LEGACY) | `basic.timeline_semaphore` | `synchronization.basic.timeline_semaphore` |
| synchronization2 | `basic.binary_semaphore` | `synchronization2.basic.binary_semaphore` |
| synchronization2 | `basic.timeline_semaphore` | `synchronization2.basic.timeline_semaphore` |

The file provides two factory functions, each accepting a `SynchronizationType` parameter. Both are called for LEGACY and synchronization2, producing groups under `synchronization.basic` and `synchronization2.basic` respectively.

## Source Code

- Implementation: [vktSynchronizationBasicSemaphoreTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp)
- Header: [vktSynchronizationBasicSemaphoreTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.hpp)

## Registration Path

```
synchronization.basic.binary_semaphore       (LEGACY)
synchronization.basic.timeline_semaphore     (LEGACY)
synchronization2.basic.binary_semaphore      (sync2)
synchronization2.basic.timeline_semaphore    (sync2)
```

## Test Hierarchy

### binary_semaphore (both categories)

```
binary_semaphore
|-- one_queue
|-- one_queue_typed
|-- multi_queue
|-- multi_queue_typed
|-- chain
|-- none_wait_submit          (sync2 only)
```

### timeline_semaphore (both categories)

```
timeline_semaphore
|-- one_queue
|-- multi_queue
|-- chain
|-- two_threads               (LEGACY only)
|-- wait_for_any_current_value    (LEGACY only)
|-- wait_for_any_lesser_value     (LEGACY only)
|-- wait_for_all_current_value    (LEGACY only)
|-- wait_for_all_lesser_value     (LEGACY only)
```

## Test Families

### Binary Semaphore - Single Queue Family

| Test Name | Function | LEGACY | sync2 | useTypeCreate | Description |
|---|---|---|---|---|---|
| `one_queue` | `basicOneQueueCase` | Yes | Yes | false | Signal and wait on a binary semaphore within a single queue using two submits |
| `one_queue_typed` | `basicOneQueueCase` | Yes | Yes | true | Same as `one_queue` but creates semaphore via `createSemaphoreType` |

### Binary Semaphore - Multi Queue Family

| Test Name | Function | LEGACY | sync2 | useTypeCreate | Description |
|---|---|---|---|---|---|
| `multi_queue` | `basicMultiQueueCase` | Yes | Yes | false | Signal on one queue, wait on another; then swap roles |
| `multi_queue_typed` | `basicMultiQueueCase` | Yes | Yes | true | Same as `multi_queue` but creates semaphore via `createSemaphoreType` |

### Binary Semaphore - Chain Family

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `chain` | `basicChainCase` | Yes | Yes | Chains 32768 (1024 on Vulkan SC) binary semaphores: each submit signals one and the next waits on it |

### Binary Semaphore - None Stage Family

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `none_wait_submit` | `noneWaitSubmitTest` | No | Yes | Waits on a binary semaphore with VK_PIPELINE_STAGE_NONE_KHR as the wait destination stage |

### Timeline Semaphore - Single Queue Family

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `one_queue` | `basicOneQueueCase` | Yes | Yes | Signal and wait on a timeline semaphore (value 1) within a single queue |

### Timeline Semaphore - Multi Queue Family

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `multi_queue` | `basicMultiQueueCase` | Yes | Yes | Signal/wait across two queues with increasing timeline values; then swap signal/wait roles |

### Timeline Semaphore - Chain Family

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `chain` | `basicChainTimelineCase` | Yes | Yes | Chains 32768 (1024 on Vulkan SC) submits using a single timeline semaphore with incrementing values |

### Timeline Semaphore - Thread Family (LEGACY only)

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `two_threads` | `basicThreadTimelineCase` | Yes | No | Main thread signals value 1, worker thread waits for 1 then signals value 2, main thread waits for 2 |

### Timeline Semaphore - CPU Wait Family (LEGACY only)

| Test Name | Function | LEGACY | sync2 | wait_flags | signal_value | wait_value | Description |
|---|---|---|---|---|---|---|---|
| `wait_for_any_current_value` | `basicWaitForAnyCurrentTimelineValueCase` | Yes | No | VK_SEMAPHORE_WAIT_ANY_BIT | 1 | 1 | Wait for any: signal==wait value |
| `wait_for_any_lesser_value` | `basicWaitForAnyLesserTimelineValueCase` | Yes | No | VK_SEMAPHORE_WAIT_ANY_BIT | 4 | 1 | Wait for any: signal > wait value |
| `wait_for_all_current_value` | `basicWaitForAllCurrentTimelineValueCase` | Yes | No | 0 | 1 | 1 | Wait for all: signal==wait value |
| `wait_for_all_lesser_value` | `basicWaitForAllLesserTimelineValueCase` | Yes | No | 0 | 4 | 1 | Wait for all: signal > wait value |

## Parameter Dimensions

### TestConfig

| Field | Type | Values | Description |
|---|---|---|---|
| `useTypeCreate` | bool | false, true | If true, create semaphore via `createSemaphoreType`; if false, use `createSemaphore` |
| `semaphoreType` | VkSemaphoreType | VK_SEMAPHORE_TYPE_BINARY, VK_SEMAPHORE_TYPE_TIMELINE | Semaphore type |
| `type` | SynchronizationType | LEGACY, SYNCHRONIZATION2 | Synchronization model |
| `videoCodecOperationFlags` | VideoCodecOperationFlags | 0 or codec flags | When non-zero, tests run on a video-capable queue |

### Chain Length

| Platform | basicChainLength |
|---|---|
| Default | 32768 |
| Vulkan SC | 1024 |

## Support / Feature Requirements

| Test | Check Function | Requirement |
|---|---|---|
| All timeline semaphore tests | `checkSupport` | VK_KHR_timeline_semaphore, timelineSemaphoreFeatures.timelineSemaphore == true |
| All sync2 tests | `checkSupport` | VK_KHR_synchronization2 |
| `one_queue` (binary) | `checkCommandBufferSimultaneousUseSupport` | VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT; on Vulkan SC requires commandBufferSimultaneousUse == VK_TRUE |
| `multi_queue` (binary) | `checkMultiQueueSupport` | Two queues available (same or different family); simultaneous-use support |
| `chain` (binary) | `checkSupport` | Basic semaphore and sync2 support |
| `none_wait_submit` | `checkCommandBufferSimultaneousUseSupport` | sync2 only; simultaneous-use support |
| `one_queue` (timeline) | `checkCommandBufferSimultaneousUseSupport` | Timeline semaphore + simultaneous-use support |
| `multi_queue` (timeline) | `checkMultiQueueSupport` | Timeline semaphore + two queues + simultaneous-use support |
| `chain` (timeline) | `checkSupport` | Timeline semaphore + sync2 support |
| `two_threads` | `checkSupport` | Timeline semaphore support |
| `wait_for_*` | `checkSupport` | Timeline semaphore support |

## Verification Methods

### basicOneQueueCase

1. Create a semaphore and a simultaneous-use command buffer.
2. First submit: signal the semaphore at BOTTOM_OF_PIPE.
3. Second submit: wait on the semaphore at TOP_OF_PIPE.
4. Wait on the fence; verify VK_SUCCESS.

### basicMultiQueueCase

1. Create a custom device with two queues (same or different families).
2. First round: queue[0] signals semaphore (value 1), queue[1] waits and signals (value 2 for timeline).
3. Wait for both fences; verify VK_SUCCESS.
4. Second round: swap signal/wait roles (queue[0] waits, queue[1] signals).
5. Wait for both fences; verify VK_SUCCESS.

### basicChainCase

1. Create a chain of 32768 (or 1024) binary semaphores.
2. Each iteration: create a new semaphore, submit with wait on previous and signal on current.
3. Final submit waits on the last semaphore.
4. Wait on a fence; verify VK_SUCCESS.

### basicChainTimelineCase

1. Create a single timeline semaphore.
2. Chain 32768 (or 1024) submits with incrementing timeline values.
3. Each submit waits on value i and signals value i+1.
4. Final submit waits on the last value.
5. Wait on a fence; verify VK_SUCCESS.

### noneWaitSubmitTest

1. Create a binary semaphore and an event.
2. First submit: signal the semaphore.
3. Second submit: wait on the semaphore with VK_PIPELINE_STAGE_NONE_KHR, then set an event at TOP_OF_PIPE.
4. Wait for queue idle; verify both fences signaled.
5. Verify event is set via `getEventStatus`.

### basicThreadTimelineCase

1. Create a timeline semaphore (initial value 0).
2. Worker thread: waits for value 1, then signals value 2.
3. Main thread: signals value 1, then waits for value 2.
4. Verify both threads complete successfully; return QUALITY_WARNING if timeout is reached.

### basicWaitForTimelineValueHelper (shared by wait_for_* tests)

1. Create a timeline semaphore.
2. Signal the semaphore with `signal_value` via `vk.signalSemaphore`.
3. Call `vk.waitSemaphores` with `wait_value` and the specified `wait_flags`.
4. Verify VK_SUCCESS (the wait should complete immediately since signal_value >= wait_value).

## Test Principles

- **Dual API path**: All tests use `SynchronizationWrapper` which abstracts the difference between `vkQueueSubmit` (LEGACY) and `vkQueueSubmit2` (sync2), ensuring both APIs produce equivalent behavior.
- **Typed vs. untyped creation**: Binary semaphore tests are run twice: once with `createSemaphore` (untyped) and once with `createSemaphoreType` (typed), to verify both creation paths.
- **Chain stress testing**: The chain tests submit thousands of semaphore-dependent operations to stress-test the implementation's handling of long dependency chains.
- **Timeline value semantics**: The timeline-specific tests verify that `waitSemaphores` correctly handles the case where the signaled value is greater than or equal to the waited value, for both VK_SEMAPHORE_WAIT_ANY_BIT and wait-for-all modes.
- **Cross-queue role reversal**: The `basicMultiQueueCase` test performs two rounds with swapped signal/wait roles to verify that semaphores can be reused across multiple submission patterns.
- **None stage wait**: The `none_wait_submit` test (sync2 only) validates that VK_PIPELINE_STAGE_NONE_KHR is accepted as a valid wait destination stage for binary semaphore waits.

## Notes / Uncertainties

- The `two_threads` and `wait_for_*` tests are LEGACY-only. The source code comment at line 988 states "dont repeat this test for synchronization2" without further explanation. These tests exercise CPU-side `waitSemaphores` and `signalSemaphore` which are not affected by the VK_KHR_synchronization2 extension.
- The `none_wait_submit` test is sync2-only because VK_PIPELINE_STAGE_NONE_KHR is a synchronization2 concept.
- The `basicThreadTimelineCase` test uses a 50 ms timeout for `waitSemaphores` and returns QUALITY_WARNING if the timeout is reached, rather than a hard failure.
- The `basicChainCase` and `basicChainTimelineCase` tests touch the watchdog every quarter of the chain length to avoid timeout during long test runs.
- The `basicMultiQueueCase` test creates a custom device to obtain two queues, which may fail on implementations that do not expose sufficient queues.
