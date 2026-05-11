# vktSynchronizationSmokeTests

## Overview

Smoke tests for Vulkan synchronization primitives. These tests exercise basic fence, semaphore, and queue-family barrier operations to verify that the core synchronization mechanisms of the implementation are functional. The file provides a quick sanity-check layer before more detailed synchronization tests run.

## Role of File

| Category | Group Name | Registration Path |
|---|---|---|
| synchronization (LEGACY) | `smoke` | `synchronization.smoke` |
| synchronization2 | `smoke` | `synchronization2.smoke` |

The file contributes two factory functions that each create a `smoke` group, one per synchronization category. The LEGACY group includes a `fences` test that is absent from the synchronization2 group because fence operations are not affected by the VK_KHR_synchronization2 extension.

## Source Code

- Implementation: [vktSynchronizationSmokeTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp)
- Header: [vktSynchronizationSmokeTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.hpp)

## Registration Hierarchy

```text
synchronization.smoke
├── fences (LEGACY only)
├── binary_semaphores
├── timeline_semaphores
├── queue_type_ignore_buffer_ignored
├── queue_type_ignore_buffer_external
├── queue_type_ignore_buffer_foreign
├── queue_type_ignore_buffer_arbitrary
├── queue_type_ignore_image_ignored
├── queue_type_ignore_image_external
├── queue_type_ignore_image_foreign
└── queue_type_ignore_image_arbitrary
```

This group is also registered under `synchronization2.smoke` via [`createSynchronization2SmokeTests()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1756). The `synchronization2.smoke` tree is identical except `fences` is absent — fence signaling is not affected by VK_KHR_synchronization2.

## Test Families

### fences — Fence state transition smoke test

| Test Name | Function | LEGACY | sync2 | Description |
|---|---|---|---|---|
| `fences` | `testFences` | Yes | No | Renders a triangle, submits work with a fence, verifies fence state transitions and image output |

### binary_semaphores — Binary semaphore smoke test

| Test Name | Function | LEGACY | sync2 | Semaphore Type | Description |
|---|---|---|---|---|---|
| `binary_semaphores` | `testSemaphores` | Yes | Yes | VK_SEMAPHORE_TYPE_BINARY | Two-queue rendering with binary semaphore synchronization |

### timeline_semaphores — Timeline semaphore smoke test

| Test Name | Function | LEGACY | sync2 | Semaphore Type | Description |
|---|---|---|---|---|---|
| `timeline_semaphores` | `testSemaphores` | Yes | Yes | VK_SEMAPHORE_TYPE_TIMELINE | Two-queue rendering with timeline semaphore synchronization |

### queue_type_ignore_buffer_* — Buffer barrier queue-family index smoke tests

Four leaf test cases using `ignoreQueueFamilyTypeBuffer`, differing only in the `FamilyType` parameter:

| Test Name | LEGACY | sync2 | FamilyType | Extension Required |
|---|---|---|---|---|
| `queue_type_ignore_buffer_ignored` | Yes | Yes | IGNORED | None |
| `queue_type_ignore_buffer_external` | Yes | Yes | EXTERNAL | VK_KHR_external_memory |
| `queue_type_ignore_buffer_foreign` | Yes | Yes | FOREIGN | VK_EXT_queue_family_foreign |
| `queue_type_ignore_buffer_arbitrary` | Yes | Yes | ARBITRARY | None |

### queue_type_ignore_image_* — Image barrier queue-family index smoke tests

Four leaf test cases using `ignoreQueueFamilyTypeImage`, differing only in the `FamilyType` parameter:

| Test Name | LEGACY | sync2 | FamilyType | Extension Required |
|---|---|---|---|---|
| `queue_type_ignore_image_ignored` | Yes | Yes | IGNORED | None |
| `queue_type_ignore_image_external` | Yes | Yes | EXTERNAL | VK_KHR_external_memory |
| `queue_type_ignore_image_foreign` | Yes | Yes | FOREIGN | VK_EXT_queue_family_foreign |
| `queue_type_ignore_image_arbitrary` | Yes | Yes | ARBITRARY | None |

## Parameter Dimensions

### SemaphoreTestConfig

| Field | Type | Values | Description |
|---|---|---|---|
| `synchronizationType` | SynchronizationType | LEGACY, SYNCHRONIZATION2 | Selects the synchronization model |
| `semaphoreType` | VkSemaphoreType | VK_SEMAPHORE_TYPE_BINARY, VK_SEMAPHORE_TYPE_TIMELINE | Type of semaphore to create |

### IgnoreQueueFamilyBufferParams / IgnoreQueueFamilyImageParams

| Field | Type | Values | Description |
|---|---|---|---|
| `familyType` | FamilyType | IGNORED, EXTERNAL, FOREIGN, ARBITRARY | The queue family index value used in memory barriers |
| `sync2` | bool | false (LEGACY), true (sync2) | Whether to use VkBufferMemoryBarrier2 / VkImageMemoryBarrier2 |

### FamilyType Enum

| Value | Queue Family Index | Extension Required |
|---|---|---|
| IGNORED | VK_QUEUE_FAMILY_IGNORED | None |
| EXTERNAL | VK_QUEUE_FAMILY_EXTERNAL | VK_KHR_external_memory |
| FOREIGN | VK_QUEUE_FAMILY_FOREIGN_EXT | VK_EXT_queue_family_foreign |
| ARBITRARY | 0xDEADBEEF | None |

## Support / Feature Requirements

| Test | Requirement |
|---|---|
| `binary_semaphores` (sync2) | VK_KHR_synchronization2 |
| `timeline_semaphores` | VK_KHR_timeline_semaphore, timelineSemaphoreFeatures.timelineSemaphore == true |
| `timeline_semaphores` (sync2) | VK_KHR_synchronization2 + VK_KHR_timeline_semaphore |
| `queue_type_ignore_buffer_external` | VK_KHR_external_memory |
| `queue_type_ignore_buffer_foreign` | VK_EXT_queue_family_foreign |
| `queue_type_ignore_image_external` | VK_KHR_external_memory |
| `queue_type_ignore_image_foreign` | VK_EXT_queue_family_foreign |
| `queue_type_ignore_*` (sync2) | VK_KHR_synchronization2 |
| `fences` | Graphics queue with at least 1 queue; 256x256 R8G8B8A8_UNORM render target |
| `binary_semaphores` / `timeline_semaphores` | Graphics queue family with at least 2 queues |

## Verification Methods

### testFences

1. Creates two unsignaled fences and verifies VK_NOT_READY status.
2. Submits a rendering command buffer with fence[0].
3. Waits with timeout=0 (expects VK_SUCCESS or VK_TIMEOUT).
4. Waits with DEFAULT_TIMEOUT (2 seconds).
5. Waits with UINT64_MAX (infinite) and verifies VK_SUCCESS.
6. Waits on unsubmitted fence[1] with timeout=1 (expects VK_TIMEOUT).
7. Verifies fence[0] is VK_SUCCESS (signaled).
8. Invalidates allocation and logs the rendered image.

### testSemaphores

1. Creates a custom device with 2 queues from the same family.
2. Renders triangle 1 on queue[0], signals semaphore on completion.
3. Waits on semaphore on queue[1], renders triangle 2.
4. Waits on fences for both submissions.
5. Invalidates allocations and logs both rendered images.

### ignoreQueueFamilyTypeBuffer

1. Creates a zero-filled host-visible buffer (64 uint32_t elements).
2. Records cmdFillBuffer with a known pattern (0xAABBCCDD).
3. Inserts a buffer memory barrier with the specified queue family index type (srcFamilyIndex == dstFamilyIndex).
4. Submits and waits.
5. Invalidates allocation and compares every element against the expected value.

### ignoreQueueFamilyTypeImage

1. Creates a 1x1 R8G8B8A8_UNORM image with color attachment and transfer usage.
2. Clears the image to black (0,0,0,1).
3. Renders a full-screen triangle that outputs blue (0,0,1,1).
4. Transitions layout and copies image to a host-visible buffer.
5. Compares result against reference using `tcu::floatThresholdCompare` with zero threshold.

## Test Principles

- **Smoke-level coverage**: Each test validates a single synchronization primitive or barrier behavior in isolation, not complex interaction scenarios.
- **State transition verification**: Fence tests explicitly check every state transition (unsignaled -> signaled -> reset -> unsignaled).
- **Cross-queue synchronization**: Semaphore tests use two queues from the same family to validate that signal/wait ordering is respected.
- **Barrier queue-family semantics**: The queue_type_ignore tests verify that memory barriers with special queue family indices (IGNORED, EXTERNAL, FOREIGN, ARBITRARY) do not cause errors and still provide correct synchronization.
- **Dual API path**: Buffer and image barrier tests exercise both the legacy `cmdPipelineBarrier` path and the sync2 `cmdPipelineBarrier2` path depending on the `sync2` parameter.

## Notes / Uncertainties

- The `fences` test is LEGACY-only because fence signaling is not affected by VK_KHR_synchronization2; the sync2 smoke group omits it.
- The ARBITRARY family type uses the sentinel value 0xDEADBEEF which is not a valid Vulkan queue family index. This tests implementation robustness when encountering nonsensical but same-value src/dst queue family indices in barriers.
- The `testSemaphores` function creates a custom device rather than using the default context device, because it requires 2 queues from the same family. This may cause the test to be skipped on devices that do not expose at least 2 queues in any graphics-capable family.
- The `ignoreQueueFamilyTypeImage` test uses `tcu::floatThresholdCompare` with a zero threshold, meaning any pixel deviation from the reference causes failure.
