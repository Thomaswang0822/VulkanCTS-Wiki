# [vktSynchronizationSignalOrderTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1)

## Overview

This file implements tests that verify the signaling order of semaphores across multiple `VkSubmitInfo` structures within a single `vkQueueSubmit` call. The core principle is that when multiple write operations each signal a semaphore in order, and a downstream read waits only on the last signal, all prior writes must be visible due to the guaranteed ordering of signal operations. The file tests this with both binary and timeline semaphores, and with both same-device and cross-device (shared) configurations.

## Role of File

This file contributes the `signal_order` group to **both** the `synchronization` (LEGACY) and `synchronization2` categories. The factory function [`createSignalOrderTests()`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1633) takes a `SynchronizationType` parameter, and the same test logic is reused across both API paths via [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp).

## Source Code

| File | Description |
|------|-------------|
| [`vktSynchronizationSignalOrderTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1) | Implementation |
| [`vktSynchronizationSignalOrderTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.hpp#L1) | Public header |

## Registration Hierarchy

```text
synchronization.signal_order
├── binary_semaphore
├── timeline_semaphore
├── shared_binary_semaphore
└── shared_timeline_semaphore
```

This file contributes the `signal_order` group to **both** the `synchronization` (LEGACY) and `synchronization2` categories. The factory function [`createSignalOrderTests()`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1633) takes a `SynchronizationType` parameter, and the same test logic is reused across both API paths via [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp). The tree structure is identical between both categories; only the `SynchronizationType` parameter differs. In the `synchronization2` category, the root path is `synchronization2.signal_order`.

Below each direct child, the hierarchy continues as `<writeOp>_<readOp>` / `<resource>` for non-shared groups, and `<writeOp>_<readOp>` / `<resource>_<externalSemaphoreType>` for shared groups. See Test Families below for details.

## Test Families

### binary_semaphore — Single-device binary semaphore signal ordering

Verifies signaling order on a single device with two queues from the same `VkDevice`, using binary semaphores (`VK_SEMAPHORE_TYPE_BINARY_KHR`). Each write gets its own binary semaphore, and the read waits on the last one.

Tests are registered under `synchronization.signal_order.binary_semaphore` (LEGACY) and `synchronization2.signal_order.binary_semaphore` (sync2).

**Hierarchy below this group**:

```text
binary_semaphore
└── <writeOp>_<readOp>
    └── <resource>
```

- `<writeOp>_<readOp>`: Operation pair group (e.g., `copy_buffer_copy_buffer`, `ssbo_vertex_ssbo_fragment`). See Parameter Dimensions for the full operation set.
- `<resource>`: The compatible resource from [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp) that supports both the write and read operation.

**Algorithm**:
1. Submit 12 write operations on queueA, each in its own `VkSubmitInfo`, each signaling a semaphore
2. Submit all 12 read operations on queueB in a single command buffer, waiting only on the **last** write's semaphore
3. Because signal operations are guaranteed to happen in order, waiting on the last signal implies all prior signals (and their writes) have completed
4. Verify that all read data matches the corresponding write data

- Test instance: [QueueSubmitSignalOrderTests](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1638)

### timeline_semaphore — Single-device timeline semaphore signal ordering

Verifies signaling order on a single device with two queues from the same `VkDevice`, using timeline semaphores (`VK_SEMAPHORE_TYPE_TIMELINE_KHR`). A single timeline semaphore is used with incrementing values. A host signal on the first value kicks off the chain.

Tests are registered under `synchronization.signal_order.timeline_semaphore` (LEGACY) and `synchronization2.signal_order.timeline_semaphore` (sync2).

**Hierarchy below this group**:

```text
timeline_semaphore
└── <writeOp>_<readOp>
    └── <resource>
```

The hierarchy structure and test generation algorithm are identical to `binary_semaphore`. The only difference is the semaphore type: a single timeline semaphore with incrementing values is used instead of separate binary semaphores.

- Test instance: [QueueSubmitSignalOrderTests](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1640)

### shared_binary_semaphore — Cross-device binary semaphore signal ordering

Same algorithm as the non-shared binary semaphore variant, but uses two **different** `VkDevice` instances (queueA on deviceA, queueB on deviceB). Resources are exported from deviceA and imported into deviceB via external memory handles. Binary semaphores are exported/imported via external semaphore handles.

Tests are registered under `synchronization.signal_order.shared_binary_semaphore` (LEGACY) and `synchronization2.signal_order.shared_binary_semaphore` (sync2).

**Hierarchy below this group**:

```text
shared_binary_semaphore
└── <writeOp>_<readOp>
    └── <resource>_<externalSemaphoreType>
```

- `<externalSemaphoreType>`: The external semaphore handle type (e.g., `opaque_fd`, `opaque_win32_kmt`, `opaque_win32`). See External Handle Types in Parameter Dimensions.

This variant requires:
- Exportable and importable external memory
- Exportable and importable external semaphores with reference semantics (not sync_fd)

- Test instance: [QueueSubmitSignalOrderSharedTests](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1642)

### shared_timeline_semaphore — Cross-device timeline semaphore signal ordering

Same algorithm as the non-shared timeline semaphore variant, but uses two **different** `VkDevice` instances (queueA on deviceA, queueB on deviceB). Resources are exported from deviceA and imported into deviceB via external memory handles. Timeline semaphores are exported/imported via external semaphore handles.

Tests are registered under `synchronization.signal_order.shared_timeline_semaphore` (LEGACY) and `synchronization2.signal_order.shared_timeline_semaphore` (sync2).

**Hierarchy below this group**:

```text
shared_timeline_semaphore
└── <writeOp>_<readOp>
    └── <resource>_<externalSemaphoreType>
```

The hierarchy structure and test generation algorithm are identical to `shared_binary_semaphore`. The only difference is the semaphore type: timeline semaphores with incrementing values are used instead of binary semaphores.

This variant requires:
- Exportable and importable external memory
- Exportable and importable external semaphores with reference semantics (not sync_fd)

- Test instance: [QueueSubmitSignalOrderSharedTests](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1643)

## Parameter Dimensions

### Semaphore Type

| Group Name | VkSemaphoreType |
|------------|-----------------|
| `binary_semaphore` | `VK_SEMAPHORE_TYPE_BINARY_KHR` |
| `timeline_semaphore` | `VK_SEMAPHORE_TYPE_TIMELINE_KHR` |
| `shared_binary_semaphore` | `VK_SEMAPHORE_TYPE_BINARY_KHR` |
| `shared_timeline_semaphore` | `VK_SEMAPHORE_TYPE_TIMELINE_KHR` |

### Operation Pairs

Each family iterates over the full cross-product of write and read operations:

**Write Operations (19)**:
`COPY_BUFFER`, `COPY_BUFFER_TO_IMAGE`, `COPY_IMAGE_TO_BUFFER`, `COPY_IMAGE`, `BLIT_IMAGE`, `SSBO_VERTEX`, `SSBO_TESSELLATION_CONTROL`, `SSBO_TESSELLATION_EVALUATION`, `SSBO_GEOMETRY`, `SSBO_FRAGMENT`, `SSBO_COMPUTE`, `SSBO_COMPUTE_INDIRECT`, `IMAGE_VERTEX`, `IMAGE_TESSELLATION_CONTROL`, `IMAGE_TESSELLATION_EVALUATION`, `IMAGE_GEOMETRY`, `IMAGE_FRAGMENT`, `IMAGE_COMPUTE`, `IMAGE_COMPUTE_INDIRECT`

**Read Operations (28)**:
`COPY_BUFFER`, `COPY_BUFFER_TO_IMAGE`, `COPY_IMAGE_TO_BUFFER`, `COPY_IMAGE`, `BLIT_IMAGE`, `UBO_VERTEX`, `UBO_TESSELLATION_CONTROL`, `UBO_TESSELLATION_EVALUATION`, `UBO_GEOMETRY`, `UBO_FRAGMENT`, `UBO_COMPUTE`, `UBO_COMPUTE_INDIRECT`, `SSBO_VERTEX`, `SSBO_TESSELLATION_CONTROL`, `SSBO_TESSELLATION_EVALUATION`, `SSBO_GEOMETRY`, `SSBO_FRAGMENT`, `SSBO_COMPUTE`, `SSBO_COMPUTE_INDIRECT`, `IMAGE_VERTEX`, `IMAGE_TESSELLATION_CONTROL`, `IMAGE_TESSELLATION_EVALUATION`, `IMAGE_GEOMETRY`, `IMAGE_FRAGMENT`, `IMAGE_COMPUTE`, `IMAGE_COMPUTE_INDIRECT`, `INDIRECT_BUFFER_DRAW`, `INDIRECT_BUFFER_DRAW_INDEXED`, `INDIRECT_BUFFER_DISPATCH`, `VERTEX_INPUT`

### Resources

Each write/read pair is further iterated over [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp) entries that support both operations. Only compatible resource types are included.

### External Handle Types (shared variants only)

| Memory Handle Type | Semaphore Handle Type | Platform |
|--------------------|-----------------------|----------|
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | Linux/Unix |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | Windows |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_BIT` | Windows |

### SynchronizationType

Every test case is instantiated for both `LEGACY` and `SYNCHRONIZATION2` via the `SynchronizationType` parameter.

## Support / Feature Requirements

| Requirement | Applicable Tests |
|-------------|-----------------|
| `VK_KHR_timeline_semaphore` | `timeline_semaphore` and `shared_timeline_semaphore` groups |
| `VK_KHR_synchronization2` | All tests when `SynchronizationType::SYNCHRONIZATION2` |
| `VK_KHR_external_semaphore` | `shared_*` groups |
| `VK_KHR_external_memory` | `shared_*` groups |
| `VK_KHR_external_semaphore_fd` | `shared_*` with FD handle types |
| `VK_KHR_external_semaphore_win32` | `shared_*` with Win32 handle types |
| `VK_KHR_external_memory_win32` | `shared_*` with Win32 memory handle types |
| Exportable + importable semaphore | `shared_*` groups (checked via `vkGetPhysicalDeviceExternalSemaphoreProperties`) |
| Exportable + importable memory | `shared_*` groups (checked via `vkGetPhysicalDeviceExternalImageFormatProperties2` / `vkGetPhysicalDeviceExternalBufferProperties`) |
| Two distinct queues | Non-shared groups require queueA != queueB on the same device |

## Verification Methods

- **Data comparison**: For buffer resources, `deMemCmp` compares write-output data against read-output data. For indirect buffers, the counter value is checked to be at least the expected value.
- **Device idle guard**: [`DeviceWaitIdleGuard`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L88) ensures `vkDeviceWaitIdle` is called before resources are destroyed, preventing use-after-free in the cross-device scenario.

## Test Principles

- **Signal ordering guarantee**: The Vulkan specification guarantees that signal operations within a single `vkQueueSubmit` happen in order. By waiting only on the last signal, all prior signals (and their associated writes) are guaranteed to have completed.
- **Cross-device isolation**: The shared variants use a [`SingletonDevice`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L197) pattern to create a second logical device, ensuring true queue isolation even on single-queue implementations.
- **API variant abstraction**: [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) abstracts `vkQueueSubmit` vs `vkQueueSubmit2KHR`, allowing the same test logic to cover both API paths.
- **Shared pipeline cache**: [`PipelineCacheData`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L93) is shared across operation pair tests to reduce shader compilation overhead.
- **Cleanup via deinit**: The [`cleanupGroup()`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L225) function destroys the singleton device when the test group is deinitialized.

## Notes / Uncertainties

- The `shared_*` groups only test semaphore handle types with **reference semantics** (opaque FD, opaque Win32, opaque Win32 KMT). Handle types with copy semantics (e.g., `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT`) are excluded because they cannot be waited on after being signaled once.
- The [`SingletonDevice`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L197) creates a custom device with all queue families and all available queues, plus the required extensions. This device is shared across all `shared_*` test instances.
- The non-shared variant requires two distinct queues from the same device. If no second queue is available, the test throws `NotSupportedError`.
- The `shared_*` variants use `VK_SHARING_MODE_EXCLUSIVE` for resources with explicit queue family ownership transfer via pipeline barriers.
