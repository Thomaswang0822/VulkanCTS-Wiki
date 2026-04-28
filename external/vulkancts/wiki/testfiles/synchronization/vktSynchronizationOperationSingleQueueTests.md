# vktSynchronizationOperationSingleQueueTests

## Overview

This file implements tests that verify the correctness of Vulkan synchronization primitives when a write operation and a subsequent read operation are submitted to a **single queue**. It is one of the largest test files in the synchronization category, exercising all five sync primitives (fence, binary semaphore, timeline semaphore, pipeline barrier, event) across a combinatorial matrix of write/read operation pairs and resource types.

## Role of File in Categories

| Category | Registration Path | SynchronizationType |
|---|---|---|
| synchronization (LEGACY) | `synchronization.op.single_queue` | `SynchronizationType::LEGACY` |
| synchronization2 | `synchronization2.op.single_queue` | `SynchronizationType::SYNCHRONIZATION2` |

The factory function [createSynchronizedOperationSingleQueueTests](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293) accepts a `SynchronizationType` parameter and is called once for each category by the `OperationTests` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L85). The `SynchronizationType` determines whether legacy `vkCmdPipelineBarrier` / `vkCmdSetEvent` / `vkCmdWaitEvents` or the `synchronization2` variants (`vkCmdPipelineBarrier2KHR`, etc.) are used internally via the `SynchronizationWrapper`.

## Source Code

- Implementation: [vktSynchronizationOperationSingleQueueTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp)
- Header: [vktSynchronizationOperationSingleQueueTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.hpp)
- Shared operation data: [vktSynchronizationOperationTestData.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp)
- Shared resource data: [vktSynchronizationOperationResources.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp)
- Operation framework: [vktSynchronizationOperation.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperation.hpp)

## Registration Path

```
synchronization.op.single_queue          (LEGACY)
synchronization2.op.single_queue         (SYNCHRONIZATION2)
```

Both paths are created by the same factory function invoked with different `SynchronizationType` values.

## Test Hierarchy

```
single_queue
|-- fence
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>
|-- binary_semaphore
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>
|-- timeline_semaphore
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>
|-- barrier
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>
|       |-- <resourceName>_specialized_access_flag       (sync2 only)
|-- event
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>
|       |-- <resourceName>_specialized_access_flag       (sync2 only)
|       |-- <resourceName>_maintenance9                  (sync2 only, non-SC)
|       |-- <resourceName>_cq                            (compute-queue event)
|-- multi_events                                         (sync2 only)
    |-- <evt1>__<evt2>_res_<res1>_<res2>                (two-event combos)
    |-- <nop/evt>__<evt/nop>_res_<none/res>_<res/none>  (nop-event combos)
```

## Test Families

### Fence Family (`fence`)

Uses `VkFence` to synchronize across two separate command buffer submissions on the same queue. The write command buffer is submitted and waited on via fence, then the read command buffer is submitted. A pipeline barrier is recorded inside the write command buffer to establish the memory dependency.

- Test instance: [FenceTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L732)

### Binary Semaphore Family (`binary_semaphore`)

Uses a binary `VkSemaphore` signaled by the write submission and waited on by the read submission. Both command buffers are submitted to the same queue with the semaphore establishing the execution and memory dependency.

- Test instance: [BinarySemaphoreTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L458)

### Timeline Semaphore Family (`timeline_semaphore`)

Uses a `VkSemaphoreType::VK_SEMAPHORE_TYPE_TIMELINE` semaphore with incrementing timeline points. This family is unique in that it chains multiple copy operations between the initial write and final read, exercising the timeline semaphore across a multi-hop data transfer chain on a single queue.

- Test instance: [TimelineSemaphoreTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L575)

### Barrier Family (`barrier`)

Uses `vkCmdPipelineBarrier` (or `vkCmdPipelineBarrier2KHR` in sync2 mode) recorded in a single command buffer between the write and read operations. This is the simplest synchronization primitive, entirely intra-command-buffer.

- Test instance: [BarrierTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L372)

### Event Family (`event`)

Uses `vkCmdSetEvent` / `vkCmdWaitEvents` (or their sync2 equivalents) within a single command buffer. In sync2 mode, additional variants test:

- **maintenance9**: Uses `VK_DEPENDENCY_ASYMMETRIC_EVENT_BIT_KHR` and `VK_KHR_maintenance9` for asymmetric event semantics.
- **compute queue (cq)**: Submits the event test on a dedicated compute queue instead of the universal queue, when both write and read operations support compute queues.

- Test instance: [EventTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76)

### Multi-Events Family (`multi_events`, sync2 only)

Tests `vkCmdWaitEvents2KHR` with **two events** waited on simultaneously. Two sub-families exist:

1. **Two-event combos**: Both events have real write/read operation pairs; all combinations of valid op-pair/resource pairs are tested.
2. **Nop-event combos**: One event is a no-op (empty dependency), testing that waiting on a mix of real and null events works correctly.

- Test case: [SyncEventsTestCase](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L944)
- Test instance: [EventsTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L189)

## Parameter Dimensions

### Synchronization Primitive

| Value | Group Name |
|---|---|
| `SYNC_PRIMITIVE_FENCE` | `fence` |
| `SYNC_PRIMITIVE_BINARY_SEMAPHORE` | `binary_semaphore` |
| `SYNC_PRIMITIVE_TIMELINE_SEMAPHORE` | `timeline_semaphore` |
| `SYNC_PRIMITIVE_BARRIER` | `barrier` |
| `SYNC_PRIMITIVE_EVENT` | `event` |

### Write Operations (33 total)

Defined in [s_writeOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36). Major categories:

- **Transfer ops**: `WRITE_FILL_BUFFER`, `WRITE_UPDATE_BUFFER`, `WRITE_COPY_BUFFER`, `WRITE_COPY_BUFFER_TO_IMAGE`, `WRITE_COPY_IMAGE_TO_BUFFER`, `WRITE_COPY_IMAGE`, `WRITE_BLIT_IMAGE`
- **Shader storage writes**: `WRITE_SSBO_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT`
- **Shader image writes**: `WRITE_IMAGE_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT/COMPUTE_MULTISAMPLE`
- **Clear ops**: `WRITE_CLEAR_COLOR_IMAGE`, `WRITE_CLEAR_DEPTH_STENCIL_IMAGE`, `WRITE_CLEAR_ATTACHMENTS`
- **Draw ops**: `WRITE_DRAW`, `WRITE_DRAW_INDEXED`, `WRITE_DRAW_INDIRECT`, `WRITE_DRAW_INDEXED_INDIRECT`
- **Indirect buffer writes**: `WRITE_INDIRECT_BUFFER_DRAW/DRAW_INDEXED/DISPATCH`
- **Index buffer**: `WRITE_UPDATE_INDEX_BUFFER`

### Read Operations (40 total)

Defined in [s_readOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L72). Major categories:

- **Transfer reads**: `READ_COPY_BUFFER/BUFFER_TO_IMAGE/IMAGE_TO_BUFFER/IMAGE/BLIT_IMAGE/RESOLVE_IMAGE`
- **UBO reads**: `READ_UBO_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT`
- **Texel buffer reads**: `READ_UBO_TEXEL_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT`
- **SSBO reads**: `READ_SSBO_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT`
- **Image reads**: `READ_IMAGE_VERTEX/TESS_CTRL/TESS_EVAL/GEOMETRY/FRAGMENT/COMPUTE/COMPUTE_INDIRECT`
- **Indirect buffer reads**: `READ_INDIRECT_BUFFER_DRAW/DRAW_INDEXED/DISPATCH`
- **Input attachment reads**: `READ_VERTEX_INPUT`, `READ_INDEX_INPUT`

### Resource Types (16 total)

Defined in [s_resources](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36):

- **Buffers**: 16 KiB, 256 KiB
- **1D images**: R32_UINT 128px
- **2D images**: R8_UNORM, R16_UINT, R8G8B8A8_UNORM, R16G16B16A16_UINT, R32G32B32A32_SFLOAT (128x128)
- **3D images**: R32_SFLOAT (64x64x8)
- **Depth images**: D16_UNORM, D32_SFLOAT (128x128)
- **Stencil images**: S8_UINT (128x128)
- **Indirect buffers**: Draw, DrawIndexed, Dispatch command sizes
- **Index buffer**: 5 x uint32_t
- **Multisampled image**: R32_UINT 64x64, 4 samples

### Specialized Access Flag (sync2 only)

When `SynchronizationType::SYNCHRONIZATION2` is active and either the write or read operation supports specialized access flags, an additional test variant with the `_specialized_access_flag` suffix is generated. This tests the `VkAccessFlags2` specialized access flag variants introduced by `VK_KHR_synchronization2`.

### Maintenance9 (sync2 event only, non-SC)

When the sync primitive is `event` and `SynchronizationType::SYNCHRONIZATION2`, a `_maintenance9` variant is added that enables `VK_KHR_maintenance9` and uses `VK_DEPENDENCY_ASYMMETRIC_EVENT_BIT_KHR`.

### Compute Queue (event only)

When the sync primitive is `event` and both write and read operations can run on a compute queue, and the resource supports compute queues, a `_cq` variant is added that uses a dedicated compute queue instead of the universal queue.

## Support/Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_synchronization2` | `SynchronizationType::SYNCHRONIZATION2` |
| `VK_KHR_timeline_semaphore` | `SYNC_PRIMITIVE_TIMELINE_SEMAPHORE` |
| `VK_KHR_portability_subset` (events feature) | `SYNC_PRIMITIVE_EVENT` on portability subset devices |
| `VK_KHR_maintenance9` | `_maintenance9` event variants |
| Dedicated compute queue | `_cq` event variants |
| Image format properties | All image resource types |
| Sample count support | Multisampled image resources |

## Verification Methods

All test instances use the same verification approach:

1. **Data comparison**: After synchronization, the data written by the write operation is compared against the data read by the read operation. For standard buffer/image resources, `deMemCmp` is used for exact byte comparison.
2. **Indirect buffer comparison**: For indirect buffer resources, the counter value read must be at least as large as the expected value (not an exact match, since indirect counts are monotonic).
3. **Failure criteria**: `tcu::TestStatus::fail` is returned if memory contents do not match or counter values are too small.

## Test Principles

The core principle is: **after proper synchronization, a read operation must observe the data written by a preceding write operation**. Each test:

1. Creates a resource shared between write and read operations.
2. Records the write operation in a command buffer.
3. Inserts the appropriate synchronization primitive (barrier, event, semaphore signal, or fence).
4. Records the read operation.
5. Submits and waits for completion.
6. Verifies that read data matches written data.

The timeline semaphore variant extends this to a multi-hop chain: write -> copy1 -> copy2 -> ... -> read, with each hop synchronized by a different timeline semaphore value.

The multi-events variant verifies that `cmdWaitEvents2` correctly handles waiting on multiple events simultaneously, including the edge case where one event has no associated dependency (nop).

## Notes/Uncertainties

- The exact number of generated test cases is very large due to the combinatorial explosion of 33 write ops x 40 read ops x 16 resources x 5 sync primitives, filtered by `isResourceSupported`. Only valid combinations produce tests.
- The `numOptions` field in the sync primitive group definitions is defined but not used for fence, binary_semaphore, or timeline_semaphore (set to 0). For barrier and event it is set to 1 but the value does not appear to affect test generation in the single-queue file.
- The multi-events family uses a reduced set of operations (4 write ops, 4 read ops, 5 resources) compared to the full matrix, to limit combinatorial explosion.
- The `SyncTestCase` class stores a `PipelineCacheData` reference to share compiled pipelines across test instances for performance.
- The `_cq` (compute queue) variant for events is available in both LEGACY and SYNCHRONIZATION2 modes, unlike `_maintenance9` and `_specialized_access_flag` which are sync2-only.
