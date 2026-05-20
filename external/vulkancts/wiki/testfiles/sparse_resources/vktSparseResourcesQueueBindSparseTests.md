# vktSparseResourcesQueueBindSparseTests.cpp

## Overview

[`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L1) registers the [`sparse_resources.queue_bind`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L505) branch. Its source comment states that this branch targets sparse queue-binding edge cases and semaphore/fence synchronization, while actual sparse binding and usage are covered by other sparse-resource groups ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L501)).

## Role

Implementation file for sparse queue-bind synchronization cases.

## Source Code

- Primary source: [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L1)
- Parent dispatcher registration: [`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L64)
- Shared sparse base inspected for queue creation: [`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194)

## Registration Hierarchy

```text
sparse_resources.queue_bind
├── no_dependency
├── no_dependency_fence
├── single_queue_wait_one
├── single_queue_wait_many
├── single_queue_signal_one
├── single_queue_signal_many
├── single_queue_wait_one_signal_one
├── single_queue_wait_many_signal_many
├── multi_queue_wait_one
├── multi_queue_wait_many
├── multi_queue_signal_one
├── multi_queue_signal_many
├── multi_queue_wait_one_signal_one
├── multi_queue_wait_many_signal_many
├── multi_queue_wait_one_signal_one_other
├── multi_queue_wait_many_signal_many_other
├── empty
└── empty_fence
```

## Test Families

### no_dependency — sparse bind without semaphore/fence dependency

`no_dependency` submits one non-empty sparse-bind operation with one sparse queue, no wait semaphores, no signal semaphores, and no bind-sparse fence ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L352)). The bind operation uses a `VkBindSparseInfo` with zero buffer/image bind counts, so this case checks queue operation behavior rather than resource binding contents ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L100-L125), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L221-L227)).

### no_dependency_fence — sparse bind with fence completion

`no_dependency_fence` uses the same one-queue/no-semaphore sparse bind as `no_dependency`, but sets `bindSparseUseFence=true` in the table ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L353-L360)). During submission, the instance creates a fence for sparse-bind submissions when that flag is set and fails if the fence is not signaled ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L295)).

### single_queue_wait_one — one wait semaphore on the sparse queue

`single_queue_wait_one` uses one queue, one wait semaphore, zero signal semaphores, and a bind-sparse fence ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L362-L369)). The setup creates wait semaphores, emits regular queue submissions to signal them, then submits `vkQueueBindSparse` waiting on them ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L176-L226)).

### single_queue_wait_many — multiple wait semaphores on the sparse queue

`single_queue_wait_many` is the single-queue wait case with three wait semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L370-L377)). The preparation loop can aggregate remaining wait semaphores into a regular submission on the sparse queue before the sparse bind waits on them ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L195-L219)).

### single_queue_signal_one — one signal semaphore from sparse bind

`single_queue_signal_one` uses one queue, no wait semaphores, one signal semaphore, and a bind-sparse fence ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L378-L385)). The instance appends regular submissions that wait on sparse-bind signal semaphores, and failure of regular fences is reported as possible missing semaphore signaling from `vkQueueBindSparse` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L234-L258), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L293-L299)).

### single_queue_signal_many — multiple signal semaphores from sparse bind

`single_queue_signal_many` is the one-queue signal case with three signal semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L386-L393)). The sparse submission's `signalSemaphoreCount` is populated from the generated signal-semaphore vector ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L188-L193), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L224-L226)).

### single_queue_wait_one_signal_one — one wait and one signal semaphore

`single_queue_wait_one_signal_one` combines one wait and one signal semaphore on a single queue ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L394-L401)). The implementation surrounds the sparse submission with regular submissions before and after the bind to exercise both wait and signal paths ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L195-L258)).

### single_queue_wait_many_signal_many — multiple waits and signals

`single_queue_wait_many_signal_many` combines two wait semaphores and three signal semaphores on a single queue ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L402-L409)). This expands the same submit/bind/wait sequencing to multiple semaphore objects ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L182-L193), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L299)).

### multi_queue_wait_one — wait dependency involving two queues

`multi_queue_wait_one` requests two queues and one wait semaphore ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L411-L418)). The instance requests a sparse queue plus `numQueues` additional queues, filters out duplicate handles, and can signal wait semaphores from other queues before the sparse bind ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L152-L172), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L195-L219)).

### multi_queue_wait_many — multiple wait dependencies involving two queues

`multi_queue_wait_many` uses two queues and two wait semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L419-L426)). The queue-preparation loop distributes available wait-semaphore signaling across other queues before falling back to the sparse queue as the last assigned queue ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L195-L219)).

### multi_queue_signal_one — one signal dependency involving two queues

`multi_queue_signal_one` uses two queues and one signal semaphore ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L427-L434)). After sparse binding signals the semaphore, regular submissions on other queues may wait on it, and their fences determine pass/fail ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L234-L258), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L285-L299)).

### multi_queue_signal_many — multiple signal dependencies involving two queues

`multi_queue_signal_many` uses two queues and two signal semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L435-L442)). It exercises the same signal-distribution path with more than one semaphore object ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L234-L258)).

### multi_queue_wait_one_signal_one — one wait and one signal across queues

`multi_queue_wait_one_signal_one` combines one wait and one signal semaphore with two requested queues ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L443-L450)). This case checks both dependency directions with the filtered sparse/other queue set ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L152-L172), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L195-L258)).

### multi_queue_wait_many_signal_many — multiple waits and signals across queues

`multi_queue_wait_many_signal_many` uses two queues, two wait semaphores, and two signal semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L451-L458)). Verification remains fence-based after all regular and sparse submissions are issued ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L302)).

### multi_queue_wait_one_signal_one_other — alternate multi-queue one-and-one case

`multi_queue_wait_one_signal_one_other` has the same explicit parameters as `multi_queue_wait_one_signal_one`: two queues, one wait semaphore, one signal semaphore, non-empty bind, and bind-sparse fence ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L459-L466)). In the inspected source, no additional distinguishing parameter is visible beyond the registered name and table row.

### multi_queue_wait_many_signal_many_other — three requested queues with multiple waits/signals

`multi_queue_wait_many_signal_many_other` requests three queues, two wait semaphores, and two signal semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L467-L474)). The implementation can use more than one non-sparse queue after duplicate sparse-queue handles are filtered ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L152-L172)).

### empty — empty `vkQueueBindSparse` submission

`empty` sets `emptySubmission=true`, uses no semaphores, and does not use a fence ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L476-L483)). The instance calls `vkQueueBindSparse` with `bindInfoCount=0` and a null info pointer for empty submissions ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L221-L232), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L279-L283)).

### empty_fence — empty `vkQueueBindSparse` submission with fence

`empty_fence` is the empty submission variant with `bindSparseUseFence=true` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L484-L491)). Its fence is included in the bind-sparse fence wait loop, so failure to signal reports `vkQueueBindSparse didn't signal the fence` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L271-L295)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct cases | Eighteen case names are listed in the `cases[]` table and added to the group by the loop in [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L496). |
| Queue count | `numQueues` is `1`, `2`, or `3` depending on the table row ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L491)). |
| Wait semaphores | `numWaitSemaphores` values observed are `0`, `1`, `2`, and `3` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L491)). |
| Signal semaphores | `numSignalSemaphores` values observed are `0`, `1`, `2`, and `3` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L491)). |
| Empty submission | Only `empty` and `empty_fence` set `emptySubmission=true` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L476-L491)). |
| Bind-sparse fence | Fence use is controlled by `bindSparseUseFence`; the two no-fence cases in the table are `no_dependency` and `empty` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L491)). |

## Support / Feature Requirements

Each queue-bind case requires the core sparse-binding feature through `checkSupport()` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L328-L331)). At runtime the instance requests one queue supporting `VK_QUEUE_SPARSE_BINDING_BIT` plus `numQueues` generic queue requirements from the case table; after device creation it filters out generic queue handles that duplicate the sparse queue, so the number of distinct non-sparse queues can be smaller than `numQueues` ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L155-L171)). The shared base throws `NotSupportedError` if it cannot match queue requirements ([`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L158-L194)).

## Verification Methods

The queue-bind branch verifies synchronization by waiting for fences created for sparse-bind submissions and regular submissions; it fails if a sparse-bind fence is not signaled, or if regular submission fences do not signal after waiting on semaphores that should have been signaled by sparse bind ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L127-L135), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L299)). It also calls `deviceWaitIdle()` after the submissions, with a source comment noting that an error can indicate unsignaled wait semaphores ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L301-L304)).

## Test Principles Observed

- The branch isolates sparse-queue synchronization behavior from real resource binding by using `VkBindSparseInfo` objects with zero buffer/image bind counts ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L100-L117)).
- It covers both sparse-bind fences and semaphore handoff between regular `vkQueueSubmit` and `vkQueueBindSparse` submissions ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L76-L125), [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L299)).

## Notes / Uncertainties

- The two `*_other` rows do not expose a separate boolean or enum in `TestParams`; their distinction is only the registered name and, for `multi_queue_wait_many_signal_many_other`, requesting three queues instead of two ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L459-L474)).
