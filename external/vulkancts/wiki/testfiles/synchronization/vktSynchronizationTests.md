# [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L1)

## Overview

This is the root registration file for both the `synchronization` and `synchronization2` categories. It defines [`createTestsInternal()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114) which assembles the test tree parameterized by [`SynchronizationType`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp#L43). The two public entry points [`createSynchronizationTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L175) and [`createSynchronization2Tests()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L186) call it with `LEGACY` and `SYNCHRONIZATION2` respectively.

## Role of File

Registration / dispatcher. This file does not contain test logic itself. It includes headers for each sub-module, defines a local helper [`createBasicTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53) and an [`OperationTests`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L74) class, and attaches the resulting children to the root group.

## Source Code

| File | Description |
|------|-------------|
| [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L1) | Root registration implementation |
| [`vktSynchronizationTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.hpp#L1) | Public header |

## Registration Hierarchy

### synchronization (LEGACY)

```text
synchronization
├── smoke
├── timeline_semaphore
├── internally_synchronized_objects
├── win32_keyed_mutex (not in Vulkan SC)
├── global_priority_transition (not in Vulkan SC)
├── basic
├── op
├── cross_instance (not in Vulkan SC)
├── signal_order (not in Vulkan SC)
└── implicit (not in Vulkan SC)
```

Source: [`createTestsInternal()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114) with `SynchronizationType::LEGACY`, verified against mustpass [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt).

### synchronization2 (SYNCHRONIZATION2)

```text
synchronization2
├── smoke
├── timeline_semaphore
├── none_stage (not in Vulkan SC)
├── internally_synchronized_queues (not in Vulkan SC)
├── layout_transition
├── basic
├── op
├── cross_instance (not in Vulkan SC)
├── signal_order (not in Vulkan SC)
└── implicit (not in Vulkan SC)
```

Source: [`createTestsInternal()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114) with `SynchronizationType::SYNCHRONIZATION2`, verified against mustpass [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt).

## Test Families

### smoke — Smoke tests

Shared between both categories. Registered by [`createSmokeTests()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1) (LEGACY) and [`createSynchronization2SmokeTests()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1) (SYNCHRONIZATION2).

Source: [`vktSynchronizationSmokeTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1)

### timeline_semaphore — Timeline semaphore tests

Shared between both categories. Registered by [`createTimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1) (LEGACY) and [`createSynchronization2TimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1) (SYNCHRONIZATION2).

Source: [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1)

### internally_synchronized_objects — Internally synchronized objects (LEGACY only)

LEGACY-only group.

Source: [`vktSynchronizationInternallySynchronizedObjectsTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1)

### win32_keyed_mutex — Win32 keyed mutex (LEGACY only, not in Vulkan SC)

LEGACY-only group.

Source: [`vktSynchronizationWin32KeyedMutexTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp#L1)

### global_priority_transition — Global priority transition (LEGACY only, not in Vulkan SC)

LEGACY-only group. The group name differs from what the source filename (`vktGlobalPriorityQueueTests.cpp`) might suggest.

Source: [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L1)

### none_stage — None stage tests (synchronization2 only, not in Vulkan SC)

synchronization2-only group.

Source: [`vktSynchronizationNoneStageTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L1)

### internally_synchronized_queues — Internally synchronized queues (synchronization2 only, not in Vulkan SC)

synchronization2-only group. The group name differs from the LEGACY counterpart `internally_synchronized_objects` despite testing related concepts.

Source: [`vktSynchronizationInternallySynchronizedTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1)

### layout_transition — Image layout transition (synchronization2 only)

synchronization2-only group. The group name differs from the source filename (`vktSynchronizationImageLayoutTransitionTests.cpp`).

Source: [`vktSynchronizationImageLayoutTransitionTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L1)

### basic — Basic synchronization primitives

Shared between both categories. Built by [`createBasicTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53) which adds different children depending on `SynchronizationType`:

| Subgroup | LEGACY | sync2 | Source |
|---|---|---|---|
| `event` | Yes | Yes | [`vktSynchronizationBasicEventTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L1) |
| `fence` | Yes | No | [`vktSynchronizationBasicFenceTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L1) |
| `binary_semaphore` | Yes | Yes | [`vktSynchronizationBasicSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L1) |
| `timeline_semaphore` | Yes | Yes | [`vktSynchronizationBasicSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L1) |

The `basic.fence` subgroup exists only in LEGACY because `vkQueueSubmit` (used by fence tests) has no synchronization2 equivalent that would add distinct test coverage.

### op — Synchronized operation tests

Shared between both categories. Implemented by the [`OperationTests`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L74) class which shares [`PipelineCacheData`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L93) between its subgroups to speed up shader compilation.

| Subgroup | Source |
|---|---|
| `single_queue` | [`vktSynchronizationOperationSingleQueueTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1) |
| `multi_queue` | [`vktSynchronizationOperationMultiQueueTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp#L1) |

### cross_instance — Cross-instance sharing (not in Vulkan SC)

Shared between both categories.

Source: [`vktSynchronizationCrossInstanceSharingTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1)

### signal_order — Signal order tests (not in Vulkan SC)

Shared between both categories.

Source: [`vktSynchronizationSignalOrderTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1)

### implicit — Implicit synchronization tests (not in Vulkan SC)

Shared between both categories.

Source: [`vktSynchronizationImplicitTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L1)

## Test Principles Observed

- **API variant parameterization**: The entire test tree is duplicated across LEGACY and SYNCHRONIZATION2 API paths via a single `SynchronizationType` enum, maximizing code reuse
- **Category split by extension**: The two categories are registered as separate root children in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1365) so that devices without `VK_KHR_synchronization2` can still run the LEGACY tests
- **Shared pipeline cache**: The `OperationTests` class shares [`PipelineCacheData`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L93) between single_queue and multi_queue subgroups to speed up shader compilation

## Notes / Uncertainties

- The `basic.fence` subgroup exists only in LEGACY because `vkQueueSubmit` (used by fence tests) has no synchronization2 equivalent that would add distinct test coverage
- The group name `internally_synchronized_objects` (LEGACY) differs from `internally_synchronized_queues` (sync2) despite testing related concepts
- The group name `global_priority_transition` differs from what the source filename (`vktGlobalPriorityQueueTests.cpp`) might suggest
- The group name `layout_transition` differs from the source filename (`vktSynchronizationImageLayoutTransitionTests.cpp`)
- Both categories also have video codec overloads registered from [`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L55), but these are outside the scope of the synchronization category docs
