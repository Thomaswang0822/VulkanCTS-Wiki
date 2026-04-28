# vktSynchronizationOperationMultiQueueTests

## Overview

This file implements tests that verify the correctness of Vulkan synchronization primitives when a write operation and a read operation are submitted to **different queues** (potentially from different queue families). It exercises queue family ownership transfer (QFOT), concurrent vs. exclusive sharing modes, and the `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR` flag. Only fence, binary semaphore, and timeline semaphore primitives are tested (no pipeline barrier or event, since those are intra-queue or intra-command-buffer mechanisms).

## Role of File in Categories

| Category | Registration Path | SynchronizationType |
|---|---|---|
| synchronization (LEGACY) | `synchronization.op.multi_queue` | `SynchronizationType::LEGACY` |
| synchronization2 | `synchronization2.op.multi_queue` | `SynchronizationType::SYNCHRONIZATION2` |

The factory function [createSynchronizedOperationMultiQueueTests](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1658) accepts a `SynchronizationType` parameter and is called once for each category by the `OperationTests` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L86). The sync2 mode enables additional sub-groups and test variants that exercise `VK_KHR_synchronization2`-specific features.

## Source Code

- Implementation: [vktSynchronizationOperationMultiQueueTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp)
- Header: [vktSynchronizationOperationMultiQueueTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.hpp)
- Shared operation data: [vktSynchronizationOperationTestData.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp)
- Shared resource data: [vktSynchronizationOperationResources.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp)
- Operation framework: [vktSynchronizationOperation.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperation.hpp)

## Registration Path

```
synchronization.op.multi_queue           (LEGACY)
synchronization2.op.multi_queue          (SYNCHRONIZATION2)
```

Both paths are created by the same factory function invoked with different `SynchronizationType` values.

## Test Hierarchy

```
multi_queue
|-- fence
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>_exclusive
|       |-- <resourceName>_concurrent
|       |-- <resourceName>_concurrent_maintenance9       (non-SC)
|-- binary_semaphore
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>_exclusive
|       |-- <resourceName>_exclusive_use_all_stages      (sync2 only, non-SC)
|       |-- <resourceName>_concurrent
|       |-- <resourceName>_concurrent_maintenance9       (non-SC)
|-- timeline_semaphore
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>_exclusive
|       |-- <resourceName>_concurrent
|       |-- <resourceName>_concurrent_maintenance9       (non-SC)
|-- intermediate_barrier_use_all                         (sync2 only, non-SC)
    |-- <writeOp>_<readOp>_<resourceName>
        |-- <extraReadOp>_<extraWriteOp>
        |-- <extraReadOp>_<extraWriteOp>_maintenance9
```

## Test Families

### Fence Family (`fence`)

Uses `VkFence` to synchronize across two separate command buffer submissions on different queues. The write command buffer is submitted to the write queue and waited on via fence, then the read command buffer is submitted to the read queue. Queue family ownership transfer barriers are inserted when the resource uses `VK_SHARING_MODE_EXCLUSIVE` and the queues belong to different families.

- Test instance: [FenceTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1124)

### Binary Semaphore Family (`binary_semaphore`)

Uses a binary `VkSemaphore` signaled by the write queue submission and waited on by the read queue submission. This is the primary family for testing queue family ownership transfer, including the `use_all_stages` variant (sync2 only) that uses `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR`.

- Test instance: [BinarySemaphoreTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L572)

### Timeline Semaphore Family (`timeline_semaphore`)

Uses a `VkSemaphoreType::VK_SEMAPHORE_TYPE_TIMELINE` semaphore with incrementing timeline points. Similar to the single-queue variant, this chains multiple copy operations across different queues in the system, exercising timeline semaphore synchronization across a multi-hop data transfer chain that visits every queue at least once.

- Test instance: [TimelineSemaphoreTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L919)

### Intermediate Barrier Use All Family (`intermediate_barrier_use_all`, sync2 only, non-SC)

Tests the interaction of `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR` with intermediate barriers. This family creates a scenario where:

1. The write queue records: write op -> QFOT release barrier -> intermediate barrier -> extra read op -> signal semaphore
2. The read queue records: extra write op -> intermediate barrier -> QFOT acquire barrier -> read op -> wait semaphore

The semaphore signals at the extra read stage and waits at the extra write stage, testing that the ownership transfer with `use_all_stages` correctly preserves the synchronization semantics even when additional work is interleaved.

- Test case: [IntermediateBarrierCase](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1370)
- Test instance: [IntermediateBarrierInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L708)

## Parameter Dimensions

### Synchronization Primitive

| Value | Group Name |
|---|---|
| `SYNC_PRIMITIVE_FENCE` | `fence` |
| `SYNC_PRIMITIVE_BINARY_SEMAPHORE` | `binary_semaphore` |
| `SYNC_PRIMITIVE_TIMELINE_SEMAPHORE` | `timeline_semaphore` |

Note: `SYNC_PRIMITIVE_BARRIER` and `SYNC_PRIMITIVE_EVENT` are not tested in the multi-queue context because they are intra-command-buffer or intra-queue mechanisms.

### Write Operations (33 total)

Same set as single-queue tests, defined in [s_writeOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36).

### Read Operations (40 total)

Same set as single-queue tests, defined in [s_readOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L72).

### Resource Types (16 total)

Same set as single-queue tests, defined in [s_resources](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36).

### Sharing Mode

| Value | Suffix | Description |
|---|---|---|
| `VK_SHARING_MODE_EXCLUSIVE` | `_exclusive` | Resource is owned by one queue family at a time; QFOT barriers required |
| `VK_SHARING_MODE_CONCURRENT` | `_concurrent` | Resource is accessible from multiple queue families without QFOT |

### Use All Stages (`_use_all_stages`, sync2 binary_semaphore exclusive only, non-SC)

When `SynchronizationType::SYNCHRONIZATION2`, the sync primitive is `binary_semaphore`, sharing mode is `exclusive`, and the resource type is buffer or image, an additional `_use_all_stages` variant is generated. This tests `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR` (from `VK_KHR_maintenance8`), which allows the QFOT barrier to use the actual pipeline stages of the operations rather than `TOP_OF_PIPE`/`BOTTOM_OF_PIPE`.

### Maintenance9 (`_maintenance9`, concurrent only, non-SC)

When sharing mode is `VK_SHARING_MODE_CONCURRENT`, a `_maintenance9` variant is added that enables `VK_KHR_maintenance9`. With maintenance9, the test checks whether queue family ownership transfer is actually required based on `VkQueueFamilyOwnershipTransferPropertiesKHR`, and may skip the QFOT barrier if the resource does not require it.

### Queue Pair Selection

The [MultiQueues](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L99) singleton creates a custom device with up to 2 queues per family. The `getQueuesPairs` method selects queue pairs where the write queue supports the write operation's queue flags and the read queue supports the read operation's queue flags. When `useAllStages` is true, it requires queues from different families.

## Support/Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_synchronization2` | `SynchronizationType::SYNCHRONIZATION2` |
| `VK_KHR_timeline_semaphore` | `SYNC_PRIMITIVE_TIMELINE_SEMAPHORE` |
| `VK_KHR_maintenance8` | `_use_all_stages` variants |
| `VK_KHR_maintenance9` | `_maintenance9` variants |
| Multiple queue families | `VK_SHARING_MODE_CONCURRENT` requires 2+ queue families |
| At least 2 total queues | `SYNC_PRIMITIVE_TIMELINE_SEMAPHORE` |
| Image format properties | All image resource types |
| Sample count support | Multisampled image resources |

## Verification Methods

All test instances use the same verification approach:

1. **Data comparison**: After synchronization, the data written by the write operation is compared against the data read by the read operation using `deMemCmp` for exact byte comparison.
2. **Indirect buffer comparison**: For indirect buffer resources, the counter value read must be at least as large as the expected value.
3. **Multi-queue iteration**: Tests iterate over all valid queue pairs returned by `getQueuesPairs`, verifying correctness for each pair.
4. **Failure criteria**: `tcu::TestStatus::fail` is returned if memory contents do not match or counter values are too small for any queue pair.

## Test Principles

The core principle is: **after proper cross-queue synchronization with queue family ownership transfer, a read operation on one queue must observe the data written by a write operation on another queue**. Each test:

1. Creates a custom device with multiple queues using the [MultiQueues](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L99) singleton.
2. Selects appropriate queue pairs based on operation requirements.
3. Creates a shared resource with the specified sharing mode.
4. Records the write operation on the write queue command buffer, inserting a QFOT release barrier if needed.
5. Records the read operation on the read queue command buffer, inserting a QFOT acquire barrier if needed.
6. Synchronizes the two submissions using the chosen primitive (fence, binary semaphore, or timeline semaphore).
7. Verifies that read data matches written data.

The `intermediate_barrier_use_all` family extends this by interleaving additional operations between the QFOT barriers and the semaphore signal/wait, testing that the `use_all_stages` flag correctly preserves ordering when extra pipeline stages are involved.

## Notes/Uncertainties

- The [MultiQueues](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L99) class is a singleton indexed by `(type, timelineSemaphore, maintenance8)`, shared across all test instances in the same group. It is destroyed in the `cleanupGroup` callback after all tests complete.
- The `intermediate_barrier_use_all` family uses a reduced set of operations (8 extra write stages, 9 extra read stages, 6 resource types) to limit combinatorial explosion.
- The `IntermediateBarrierCase` hardcodes `SynchronizationType::SYNCHRONIZATION2` and `SYNC_PRIMITIVE_BINARY_SEMAPHORE` regardless of the outer group's type, since this feature is inherently sync2-only.
- The `numOptions` field in the sync primitive definitions is set to 1 for all three primitives in the multi-queue file, which controls the exclusive/concurrent sharing mode iteration (0 = exclusive, 1 = concurrent).
- On Vulkan SC, `VK_DEPENDENCY_QUEUE_FAMILY_OWNERSHIP_TRANSFER_USE_ALL_STAGES_BIT_KHR` is not available, so `_use_all_stages` and `intermediate_barrier_use_all` are excluded via `#ifndef CTS_USES_VULKANSC`.
- The `maintenance9` variant for concurrent sharing mode checks `VkQueueFamilyOwnershipTransferPropertiesKHR` to determine whether QFOT is actually needed for the given resource and queue family combination, potentially skipping the ownership transfer barrier entirely.
