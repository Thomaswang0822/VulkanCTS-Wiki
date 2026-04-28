# synchronization2

## Overview

The [`synchronization2`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L186) category tests Vulkan's `VK_KHR_synchronization2` extension (promoted to Vulkan 1.3 core), which introduces simplified synchronization APIs using unified `VkDependencyInfo` structs, `VkSubmitInfo2`, and more granular pipeline stage/access flags.

This category uses `SynchronizationType::SYNCHRONIZATION2`, meaning it calls the new APIs such as `vkCmdPipelineBarrier2()`, `vkQueueSubmit2()`, and `vkCmdSetEvent2()`/`vkCmdWaitEvents2()`. A companion category [`synchronization`](synchronization.md) tests the same concepts using the legacy Vulkan 1.0 API.

## Registration Entry Point

The category is rooted in [`createSynchronization2Tests()`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L186), which delegates to [`createTestsInternal()`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114) with `SynchronizationType::SYNCHRONIZATION2`. Group names below are verified against [`synchronization2.txt`](../../mustpass/main/vk-default/synchronization2.txt).

```text
synchronization2
├── smoke
├── timeline_semaphore
├── none_stage                         [not in Vulkan SC]
├── internally_synchronized_queues     [not in Vulkan SC]
├── layout_transition
├── basic
│   ├── event
│   ├── binary_semaphore
│   └── timeline_semaphore
├── op
│   ├── single_queue
│   └── multi_queue
├── cross_instance                     [not in Vulkan SC]
├── signal_order                       [not in Vulkan SC]
└── implicit                           [not in Vulkan SC]
```

## File Inventory

| File | Role | Verified group name | Level-3 doc |
|---|---|---|---|
| [`vktSynchronizationTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L1) | Registration / dispatcher | (root) | [`vktSynchronizationTests.md`](../testfiles/synchronization/vktSynchronizationTests.md) |
| [`vktSynchronizationSmokeTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1) | Implementation | `smoke` | [`vktSynchronizationSmokeTests.md`](../testfiles/synchronization/vktSynchronizationSmokeTests.md) |
| [`vktSynchronizationBasicSemaphoreTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L1) | Implementation | `basic.binary_semaphore`, `basic.timeline_semaphore` | [`vktSynchronizationBasicSemaphoreTests.md`](../testfiles/synchronization/vktSynchronizationBasicSemaphoreTests.md) |
| [`vktSynchronizationBasicEventTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L1) | Implementation | `basic.event` | [`vktSynchronizationBasicEventTests.md`](../testfiles/synchronization/vktSynchronizationBasicEventTests.md) |
| [`vktSynchronizationOperationSingleQueueTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1) | Implementation | `op.single_queue` | [`vktSynchronizationOperationSingleQueueTests.md`](../testfiles/synchronization/vktSynchronizationOperationSingleQueueTests.md) |
| [`vktSynchronizationOperationMultiQueueTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1) | Implementation | `op.multi_queue` | [`vktSynchronizationOperationMultiQueueTests.md`](../testfiles/synchronization/vktSynchronizationOperationMultiQueueTests.md) |
| [`vktSynchronizationCrossInstanceSharingTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1) | Implementation | `cross_instance` | [`vktSynchronizationCrossInstanceSharingTests.md`](../testfiles/synchronization/vktSynchronizationCrossInstanceSharingTests.md) |
| [`vktSynchronizationSignalOrderTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1) | Implementation | `signal_order` | [`vktSynchronizationSignalOrderTests.md`](../testfiles/synchronization/vktSynchronizationSignalOrderTests.md) |
| [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1) | Implementation | `timeline_semaphore` | [`vktSynchronizationTimelineSemaphoreTests.md`](../testfiles/synchronization/vktSynchronizationTimelineSemaphoreTests.md) |
| [`vktSynchronizationNoneStageTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L1) | Implementation | `none_stage` | [`vktSynchronizationNoneStageTests.md`](../testfiles/synchronization/vktSynchronizationNoneStageTests.md) |
| [`vktSynchronizationImageLayoutTransitionTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L1) | Implementation | `layout_transition` | [`vktSynchronizationImageLayoutTransitionTests.md`](../testfiles/synchronization/vktSynchronizationImageLayoutTransitionTests.md) |
| [`vktSynchronizationInternallySynchronizedTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1) | Implementation | `internally_synchronized_queues` | [`vktSynchronizationInternallySynchronizedTests.md`](../testfiles/synchronization/vktSynchronizationInternallySynchronizedTests.md) |
| [`vktSynchronizationImplicitTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L1) | Implementation | `implicit` | [`vktSynchronizationImplicitTests.md`](../testfiles/synchronization/vktSynchronizationImplicitTests.md) |

## Cross-file Recurring Themes

### SynchronizationType parameterization

Most implementation files accept a [`SynchronizationType`](../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp#L43) parameter and are shared with [`synchronization`](synchronization.md). The SYNCHRONIZATION2 path uses `vkCmdPipelineBarrier2()`, `vkQueueSubmit2()`, and `vkCmdSetEvent2()`/`vkCmdWaitEvents2()` with `VkDependencyInfo` structs.

### More granular pipeline stages

The synchronization2 API introduces finer-grained pipeline stages such as `VK_PIPELINE_STAGE_2_COPY_BIT`, `VK_PIPELINE_STAGE_2_BLIT_BIT`, and `VK_PIPELINE_STAGE_2_RESOLVE_BIT` (vs. the generic `VK_PIPELINE_STAGE_2_TRANSFER_BIT` in LEGACY). These are used in the `op` subgroups when `SynchronizationType::SYNCHRONIZATION2` is active.

### NONE stage and access flags

The `none_stage` group tests `VK_PIPELINE_STAGE_2_NONE_KHR` and `VK_ACCESS_2_NONE_KHR`, which are new concepts introduced by `VK_KHR_synchronization2` and have no LEGACY equivalent.

### Device-only events

The `basic.event` subgroup in sync2 includes `*_device_only` variants using `VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR`, which is a sync2 feature not available in the LEGACY API.

## Cross-file Recurring Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Synchronization primitive | fence, binary_semaphore, timeline_semaphore, barrier, event |
| Queue topology | single_queue, multi_queue |
| Allocation strategy | suballocated, dedicated |
| Resource type | buffer, image (multiple formats) |
| External handle type | opaque_fd, dma_buf, fence_fd, opaque_win32, opaque_win32_kmt, zircon_handle |
| Pipeline stage granularity | sync2-specific (COPY, BLIT, RESOLVE) vs. generic (TRANSFER) |

## Cross-file Recurring Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_synchronization2 | All groups (category prerequisite) |
| VK_KHR_timeline_semaphore | `timeline_semaphore`, `basic.timeline_semaphore` |
| VK_KHR_external_memory | `cross_instance` |
| VK_KHR_external_semaphore | `cross_instance` |
| VK_KHR_maintenance9 | `op.single_queue` (event), `op.multi_queue` (concurrent) |
| VK_KHR_internally_synchronized_queues | `internally_synchronized_queues` |

## Cross-file Recurring Verification Methods

- **Fence/semaphore wait**: Submit work with a sync primitive, wait on CPU, then read back and compare results
- **Pixel comparison**: Image operations verified by reading back and comparing against expected values
- **Buffer content comparison**: Buffer operations verified by mapping and comparing memory contents
- **Implicit ordering validation**: Verify that operations within a single submit happen in the documented order

## Notes / Uncertainties

- This category shares its source code folder with [`synchronization`](synchronization.md). See the root registration doc [`vktSynchronizationTests.md`](../testfiles/synchronization/vktSynchronizationTests.md) for the full dual-category structure.
- The `basic.fence` subgroup does NOT exist in this category because fences are not affected by `VK_KHR_synchronization2`.
- The group name `internally_synchronized_queues` differs from the LEGACY equivalent `internally_synchronized_objects` and from the source filename `vktSynchronizationInternallySynchronizedTests.cpp`.
- The group name `layout_transition` differs from the source filename `vktSynchronizationImageLayoutTransitionTests.cpp`.
- 5 of 10 top-level groups are guarded by `#ifndef CTS_USES_VULKANSC`.
