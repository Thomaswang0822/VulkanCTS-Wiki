# synchronization

## Overview

The [`synchronization`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L175) category tests Vulkan's legacy synchronization primitives and execution dependency mechanisms as defined by the original Vulkan 1.0 API. It covers fences, semaphores (binary and timeline), events, pipeline barriers, cross-instance resource sharing, signal ordering, and implicit synchronization guarantees.

The historical Vulkan API test plan describes synchronization coverage as verification that execution-ordering primitives work as expected across non-trivial workloads, and separately calls out fences, semaphores, and events as important primitive families ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L370-L425)). Treat this as high-level background only; the current source and mustpass files below define the active registration, parameters, support gates, and verification details.

This category uses `SynchronizationType::LEGACY`, meaning it calls the original Vulkan 1.0 synchronization APIs such as `vkCmdPipelineBarrier()`, `vkQueueSubmit()`, and `vkCmdSetEvent()`/`vkCmdWaitEvents()`. A companion category [`synchronization2`](synchronization2.md) tests the same concepts using the `VK_KHR_synchronization2` extension API.

## Registration Entry Point

The category is rooted in [`createSynchronizationTests()`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L175), which delegates to [`createTestsInternal()`](../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114) with `SynchronizationType::LEGACY`. Group names below are verified against [`synchronization.txt`](../../mustpass/main/vk-default/synchronization.txt).

```text
synchronization
├── smoke
├── timeline_semaphore
├── internally_synchronized_objects
├── win32_keyed_mutex                  [not in Vulkan SC]
├── global_priority_transition         [not in Vulkan SC]
├── basic
│   ├── event
│   ├── fence
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
| [`vktSynchronizationBasicFenceTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L1) | Implementation | `basic.fence` | [`vktSynchronizationBasicFenceTests.md`](../testfiles/synchronization/vktSynchronizationBasicFenceTests.md) |
| [`vktSynchronizationBasicSemaphoreTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L1) | Implementation | `basic.binary_semaphore`, `basic.timeline_semaphore` | [`vktSynchronizationBasicSemaphoreTests.md`](../testfiles/synchronization/vktSynchronizationBasicSemaphoreTests.md) |
| [`vktSynchronizationBasicEventTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L1) | Implementation | `basic.event` | [`vktSynchronizationBasicEventTests.md`](../testfiles/synchronization/vktSynchronizationBasicEventTests.md) |
| [`vktSynchronizationOperationSingleQueueTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1) | Implementation | `op.single_queue` | [`vktSynchronizationOperationSingleQueueTests.md`](../testfiles/synchronization/vktSynchronizationOperationSingleQueueTests.md) |
| [`vktSynchronizationOperationMultiQueueTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1) | Implementation | `op.multi_queue` | [`vktSynchronizationOperationMultiQueueTests.md`](../testfiles/synchronization/vktSynchronizationOperationMultiQueueTests.md) |
| [`vktSynchronizationCrossInstanceSharingTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1) | Implementation | `cross_instance` | [`vktSynchronizationCrossInstanceSharingTests.md`](../testfiles/synchronization/vktSynchronizationCrossInstanceSharingTests.md) |
| [`vktSynchronizationSignalOrderTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1) | Implementation | `signal_order` | [`vktSynchronizationSignalOrderTests.md`](../testfiles/synchronization/vktSynchronizationSignalOrderTests.md) |
| [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1) | Implementation | `timeline_semaphore` | [`vktSynchronizationTimelineSemaphoreTests.md`](../testfiles/synchronization/vktSynchronizationTimelineSemaphoreTests.md) |
| [`vktSynchronizationWin32KeyedMutexTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp#L1) | Implementation | `win32_keyed_mutex` | [`vktSynchronizationWin32KeyedMutexTests.md`](../testfiles/synchronization/vktSynchronizationWin32KeyedMutexTests.md) |
| [`vktGlobalPriorityQueueTests.cpp`](../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L1) | Implementation | `global_priority_transition` | [`vktGlobalPriorityQueueTests.md`](../testfiles/synchronization/vktGlobalPriorityQueueTests.md) |
| [`vktSynchronizationInternallySynchronizedObjectsTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1) | Implementation | `internally_synchronized_objects` | [`vktSynchronizationInternallySynchronizedObjectsTests.md`](../testfiles/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.md) |
| [`vktSynchronizationImplicitTests.cpp`](../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L1) | Implementation | `implicit` | [`vktSynchronizationImplicitTests.md`](../testfiles/synchronization/vktSynchronizationImplicitTests.md) |

## Cross-file Recurring Themes

### SynchronizationType parameterization

Most implementation files accept a [`SynchronizationType`](../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp#L43) parameter and are shared between this category and [`synchronization2`](synchronization2.md). The LEGACY path uses `vkCmdPipelineBarrier()`, `vkQueueSubmit()`, and `vkCmdSetEvent()`/`vkCmdWaitEvents()`. The SYNCHRONIZATION2 path uses `vkCmdPipelineBarrier2()`, `vkQueueSubmit2()`, and `vkCmdSetEvent2()`/`vkCmdWaitEvents2()`.

### Synchronization primitive as primary axis

The `op` subtree (single_queue and multi_queue) is organized by synchronization primitive: fence, binary_semaphore, timeline_semaphore, barrier, and event. Each primitive is tested against the same matrix of write/read operation pairs and resource types.

### Operation pair matrix

The `op` subgroups share a common operation framework defined in [`vktSynchronizationOperation.cpp`](../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L1), which enumerates ~33 write operations and ~40 read operations across buffer and image resources.

### External memory handle types

Cross-instance sharing tests iterate over platform-specific external handle types: `opaque_fd`, `dma_buf`, `fence_fd` (POSIX), `opaque_win32`, `opaque_win32_kmt` (Windows), and `zircon_handle` (Fuchsia).

## Cross-file Recurring Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Synchronization primitive | fence, binary_semaphore, timeline_semaphore, barrier, event |
| Queue topology | single_queue, multi_queue |
| Allocation strategy | suballocated, dedicated |
| Resource type | buffer, image (multiple formats) |
| External handle type | opaque_fd, dma_buf, fence_fd, opaque_win32, opaque_win32_kmt, zircon_handle |

## Cross-file Recurring Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_timeline_semaphore | `timeline_semaphore`, `basic.timeline_semaphore` |
| VK_KHR_external_memory | `cross_instance` |
| VK_KHR_external_semaphore | `cross_instance` |
| VK_KHR_external_semaphore_fd | `cross_instance` (POSIX) |
| VK_KHR_external_semaphore_win32 | `cross_instance` (Windows) |
| VK_EXT_external_memory_dma_buf | `cross_instance` (Linux) |
| VK_KHR_win32_keyed_mutex | `win32_keyed_mutex` |
| VK_EXT_global_priority | `global_priority_transition` |
| VK_EXT_global_priority_query | `global_priority_transition` |

## Cross-file Recurring Verification Methods

- **Fence/semaphore wait**: Submit work with a sync primitive, wait on CPU, then read back and compare results
- **Pixel comparison**: Image operations verified by reading back and comparing against expected values via `tcu::floatThresholdCompare()`
- **Buffer content comparison**: Buffer operations verified by mapping and comparing memory contents
- **Implicit ordering validation**: Verify that operations within a single submit happen in the documented order by checking resource state

## Notes / Uncertainties

- This category shares its source code folder with [`synchronization2`](synchronization2.md). See the root registration doc [`vktSynchronizationTests.md`](../testfiles/synchronization/vktSynchronizationTests.md) for the full dual-category structure.
- 5 of 10 top-level groups are guarded by `#ifndef CTS_USES_VULKANSC` and are excluded from Vulkan SC builds.
- The group name `global_priority_transition` differs from the source filename `vktGlobalPriorityQueueTests.cpp`.
