# Understanding Brief: multi-queue synchronization operation tests

## One-Sentence Test Purpose

This test checks whether a write submitted to one Vulkan queue becomes visible to a read submitted to another queue, including queue-family ownership transfer (QFOT), resource sharing mode, and synchronization primitive behavior.

## Background Knowledge

A queue submission boundary supplies execution ordering, but an exclusive resource also needs a release/acquire queue-family ownership transfer when queue families differ. The dependency must cover the source and destination pipeline stages and access types selected by the operations; image cases also carry layouts. Concurrent resources can be accessed by multiple queue families without a QFOT barrier, subject to the implementation's maintenance9 ownership-transfer requirements.

The same generated matrix is created under `synchronization.op.multi_queue` (legacy commands) and `synchronization2.op.multi_queue` (`SynchronizationType::SYNCHRONIZATION2`). Sync2-specific cases exercise the synchronization2 command and flag forms, not merely a duplicate registration.

## Concrete Example

A conceptual case such as `binary_semaphore.write_fill_buffer_read_copy_buffer.buffer_16384_exclusive` does this:

```text
[queue A] write/fill the shared buffer
[queue A] release ownership to queue family B, when required
[queue A] signal a binary semaphore
[queue B] wait for the semaphore
[queue B] acquire ownership, when required, then read/copy the buffer
[host] compare expected bytes with observed bytes
```

The operation pair determines the actual stage/access scopes. Queue pairs are selected only when their queue flags support both operations.

## End-to-End Test Flow

1. Select a primitive, write operation, read operation, resource, sharing mode, and optional variant.
2. Build a custom device with up to two queues per queue family and select compatible write/read queue pairs.
3. Create the shared resource and operation objects; reject unsupported formats, samples, operations, queue pairs, and required extensions.
4. Record the write-side command buffer and the read-side command buffer. Add QFOT release/acquire barriers for exclusive resources when needed.
5. Connect submissions with a fence, binary semaphore, or timeline semaphore.
6. For sync2's `use_all_stages` family, exercise `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR`; for `intermediate_barrier_use_all`, insert extra operations between ownership-transfer barriers and semaphore signal/wait.
7. Compare readback against the write operation's expected data. Standard data must match exactly; indirect counters must meet the expected lower bound.

## Behavior Parameter Identification

> **Primary behavior parameter:** synchronization primitive/test family
>
> **Values:** `fence`, `binary_semaphore`, `timeline_semaphore`; sync2-only `intermediate_barrier_use_all`.

The operation pair, resource, and sharing mode form the coverage matrix. Each primitive changes how the two submissions are ordered: fences wait on completion, binary semaphores signal/wait once, and timeline semaphores chain increasing values.

## Important Variations

- `_exclusive`: resource ownership is transferred between queue families when required.
- `_concurrent`: resource uses `VK_SHARING_MODE_CONCURRENT`; no ordinary QFOT is needed.
- `_concurrent_maintenance9`: non-Vulkan-SC variant requiring `VK_KHR_maintenance9`; consults `VkQueueFamilyOwnershipTransferPropertiesKHR` and may omit QFOT when the implementation says it is unnecessary.
- `_exclusive_use_all_stages`: sync2 binary-semaphore variant for buffer/image resources, non-Vulkan-SC, requiring `VK_KHR_maintenance8`.
- `intermediate_barrier_use_all`: sync2-only, non-Vulkan-SC family with a reduced six-resource and 8-extra-write/9-extra-read matrix; its leaf names add `_maintenance9` where applicable.

## What Failure Means

A failure means that at least one supported queue pair did not produce the expected data. Likely areas are semaphore/fence submission ordering, missing or incorrectly scoped QFOT release/acquire barriers, wrong sharing-mode handling, incorrect synchronization2 or maintenance flag usage, or an operation/resource implementation that reports incorrect stage/access/layout information. The source does not by itself identify whether the cause is a driver, hardware, compiler, or test implementation.

## Source Mapping

| Topic | Source |
|---|---|
| Registration and generated matrix | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1444-L1644) |
| Factory and `multi_queue` group | [`createSynchronizedOperationMultiQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1657-L1664) |
| Legacy/sync2 parent registration | [`OperationTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L83-L87) |
| Queue selection and custom queues | [`MultiQueues`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L99-L250) |
| Primitive implementations | [`FenceTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1124-L1230), [`BinarySemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L572-L918), [`TimelineSemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L919-L1123) |
| Intermediate barrier case | [`IntermediateBarrierCase`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1330-L1436) |
| Operation stage/access/layout data | [`vktSynchronizationOperation.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp) |
| Mustpass lists | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt), [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) |

## Audit Questions

- Are the distinction between queue order, semaphore/fence execution dependency, and QFOT memory visibility clear?
- Do the maintenance9 and `use_all_stages` conditions match the target Vulkan profile?
- Should a future update publish generated leaf counts, or is source/mustpass evidence sufficient?
