## Overview

**Core question:** Does `vkQueueBindSparse` preserve the requested semaphore and fence dependencies on sparse-binding queues?

- This page covers the implementation in [`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L54-L61), registered as `sparse_resources.queue_bind` ([registration](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L505)).
- The 18 test case leaves vary queue count, wait and signal semaphore counts, fence use, and whether the call is empty.
- The `VkBindSparseInfo` objects contain no buffer or image bindings. The tests isolate queue submission and synchronization behavior rather than sparse memory mapping.
- The page describes the registered matrix, the host-side submission sequence, and what each failure says about the tested dependency.

## Background Knowledge

- A queue with `VK_QUEUE_SPARSE_BINDING_BIT` can process `vkQueueBindSparse`, whose call can wait on semaphores, signal semaphores, and optionally signal a fence. Sparse resources can be bound in page-sized regions rather than requiring one contiguous allocation, but this test does not create or bind a sparse resource; its `VkBindSparseInfo` binding counts are all zero ([Vulkan sparse resources](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory)).
- Semaphores order queue submissions, including submissions on the same queue or across queues. Fences let the host observe completion. Vulkan defines the resulting ordering as execution dependencies between the relevant submission scopes ([Vulkan synchronization](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies)).

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

## Parameter Dimensions and Observed Values

The case table in [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L496) supplies these dimensions:

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | 18 names listed in the hierarchy | Selects the synchronization scenario. | [`cases[]`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L492) |
| `numQueues` | `1`, `2`, `3` | Requests the sparse queue and generic queues used for cross-queue handoff. | [`TestParams`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L54-L61) |
| `numWaitSemaphores` | `0`, `1`, `2`, `3` | Controls how many regular submissions must signal before the sparse bind can proceed. | [`cases[]`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L474) |
| `numSignalSemaphores` | `0`, `1`, `2`, `3` | Controls how many later regular submissions wait for the sparse bind. | [`cases[]`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L344-L474) |
| `emptySubmission` | `false`, `true` | Selects a one-bind-info call or `bindInfoCount=0` with a null pointer. | [`makeSubmissionSparse()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L100-L124), [empty cases](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L476-L491) |
| `bindSparseUseFence` | `false`, `true` | Adds a fence to the `vkQueueBindSparse` call and checks it on the host. | [submission loop](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L295) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each leaf selects a distinct synchronization arrangement; the values below group cases that share the same mechanism.

### No dependency

`no_dependency` submits one non-empty sparse bind on one queue without semaphores or a bind-sparse fence. It checks the basic non-empty call path. `no_dependency_fence` adds the fence check.

### Single-queue waits and signals

`single_queue_wait_one` and `single_queue_wait_many` make regular submissions signal one or three wait semaphores before the sparse bind. `single_queue_signal_one` and `single_queue_signal_many` make regular submissions wait for one or three semaphores signaled by the sparse bind.

`single_queue_wait_one_signal_one` combines one wait and one signal. `single_queue_wait_many_signal_many` combines two waits and three signals on the same queue.

### Multi-queue waits and signals

`multi_queue_wait_one` and `multi_queue_wait_many` use two requested queues and exercise one or two wait semaphores. `multi_queue_signal_one` and `multi_queue_signal_many` use two requested queues and exercise one or two signal semaphores.

`multi_queue_wait_one_signal_one` and `multi_queue_wait_many_signal_many` combine both directions with two requested queues. The `multi_queue_wait_one_signal_one_other` case has the same parameter values as the first combined case. `multi_queue_wait_many_signal_many_other` requests three queues and two wait plus two signal semaphores. Neither `*_other` name maps to a separate `TestParams` flag.

### Empty submissions

`empty` calls `vkQueueBindSparse` with `bindInfoCount=0` and `pBindInfo=nullptr`. `empty_fence` makes the same call with a fence. Empty cases do not use semaphores.

## Shader Analysis

This test has no shader or device-side program artifact. Its behavior comes from host-created Vulkan submission structures and queue synchronization.

## Runtime Execution and Result Checking

- `checkSupport()` requires the core sparse-binding feature ([support check](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L328-L331)). The instance requests one sparse-binding queue and `numQueues` generic queues. It removes generic queue handles that duplicate the sparse queue ([queue selection](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L150-L172)).
- The instance creates the requested semaphore objects. It prepares regular `VkSubmitInfo` submissions to signal the wait semaphores, then places the sparse submission after them. For a non-empty case, the sparse submission contains a `VkBindSparseInfo` with the selected wait and signal semaphore arrays and zero binding counts ([submission preparation](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L176-L232)).
- After the sparse call, the instance prepares regular submissions that wait on its signal semaphores. It distributes these submissions over the available non-sparse queues when the case requests multiple queues ([signal wait preparation](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L234-L258)).
- The test attaches fences to regular submissions and, when requested, to the sparse submission. It waits for bind-sparse fences first and then regular fences. Finally, it calls `deviceWaitIdle()` ([result checking](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L304)).
- The case passes when all requested fence waits and the idle call succeed. The test does not compare buffer or image contents.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `no_dependency` | Basic non-empty sparse submission does not complete as expected. |
| `no_dependency_fence` | `vkQueueBindSparse` fails to signal its fence. |
| `single_queue_wait_one`, `single_queue_wait_many` | The sparse submission does not correctly wait for one or multiple semaphores. |
| `single_queue_signal_one`, `single_queue_signal_many` | The sparse submission does not correctly signal one or multiple semaphores. |
| `single_queue_wait_one_signal_one`, `single_queue_wait_many_signal_many` | Combined wait and signal sequencing on one queue fails. |
| `multi_queue_wait_one`, `multi_queue_wait_many` | A wait dependency involving multiple queues fails. |
| `multi_queue_signal_one`, `multi_queue_signal_many` | A signal dependency involving multiple queues fails. |
| `multi_queue_wait_one_signal_one`, `multi_queue_wait_many_signal_many`, `multi_queue_wait_one_signal_one_other`, `multi_queue_wait_many_signal_many_other` | Combined cross-queue wait and signal sequencing fails. |
| `empty` | The empty `vkQueueBindSparse` call is rejected or mishandled. |
| `empty_fence` | The empty call does not signal its requested fence. |

### Cause Analysis

#### Sparse submission completion

**Possible failure symptoms:** `no_dependency` fails during the final idle wait or does not complete as expected.

**Possible implementation causes:** The sparse queue submission path may fail to complete a valid non-empty `vkQueueBindSparse` call. The inspected test does not identify whether the cause is in queue handling, synchronization, or another implementation layer; source-level investigation is needed.

#### Bind-sparse fence signaling

**Possible failure symptoms:** The test reports `vkQueueBindSparse didn't signal the fence` for `no_dependency_fence` or `empty_fence`.

**Possible implementation causes:** The implementation did not signal the fence supplied to `vkQueueBindSparse` after processing the call. The test cannot distinguish the responsible implementation layer from this result alone.

#### Wait semaphore handling

**Possible failure symptoms:** A regular submission fence fails to signal, or `deviceWaitIdle()` reports an error after the sparse bind waits on its semaphores.

**Possible implementation causes:** The sparse queue may have proceeded without the required wait dependency, or may have failed to make progress after the preceding regular submissions signaled the semaphores. The cross-queue cases also depend on correct queue selection and semaphore propagation.

#### Signal semaphore handling

**Possible failure symptoms:** A regular submission that waits on a semaphore signaled by the sparse bind does not signal its fence.

**Possible implementation causes:** `vkQueueBindSparse` may not signal all requested semaphores, or the implementation may not propagate their completion dependency to the waiting regular submission. The test's fence result does not by itself locate the fault.

#### Empty submission handling

**Possible failure symptoms:** `empty` or `empty_fence` fails when the test calls `vkQueueBindSparse` with zero bind infos.

**Possible implementation causes:** The implementation may mishandle the valid empty-call form, or, for `empty_fence`, may fail to signal the supplied fence. The source provides no further distinction.

## Case Pruning

### Requirement-based pruning

- Support checks prune cases when the required sparse-binding queue, semaphore, or fence capabilities are unavailable.

### Design-based pruning

- Do not merge fence and no-fence cases: fence signaling is the property under test.
- Keep one- and many-semaphore cases because they exercise different array counts.
- Keep single-queue and multi-queue cases because they place the dependency on different queue relationships.
- Keep the `*_other` registrations because they are distinct registered leaves, even though one shares the same explicit parameters as another case.
- Keep both empty cases because the fence variant checks an additional completion result.

## Key Takeaways

- This page tests `vkQueueBindSparse` synchronization, not sparse resource contents.
- Wait semaphores are signaled by regular submissions before the sparse call; signal semaphores are consumed by regular submissions after it.
- Fences convert completion into a host-visible pass/fail result.
- Multi-queue cases test semaphore handoff across the sparse queue and other queues, while empty cases test the zero-bind-info call form.

## Source Reference Appendix

- [`TestParams` and submission builders](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L54-L124)
- [`SparseQueueBindTestInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L150-L304)
- [`SparseQueueBindTest::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L311-L331)
- [`populateTestGroup`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L496)
- [`createQueueBindSparseTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L505)
- [Vulkan sparse resources](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory)
- [Vulkan synchronization dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies)
