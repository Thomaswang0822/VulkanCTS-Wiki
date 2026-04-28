# vktSynchronizationCrossInstanceSharingTests

## Overview

This file implements tests that verify the correctness of Vulkan synchronization when resources and semaphores are shared across **different Vulkan instances**. A write operation is performed on one device (instance A) and a read operation is performed on a separate device (instance B), with external memory and external semaphore objects bridging the two. This tests the external memory and semaphore infrastructure that underpins cross-process and cross-device resource sharing in Vulkan.

## Role of File in Categories

| Category | Registration Path | SynchronizationType |
|---|---|---|
| synchronization (LEGACY) | `synchronization.cross_instance` | `SynchronizationType::LEGACY` |
| synchronization2 | `synchronization2.cross_instance` | `SynchronizationType::SYNCHRONIZATION2` |

The factory function [createCrossInstanceSharingTest](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1288) accepts a `SynchronizationType` parameter and is called once for each category in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L153). This test group is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`).

## Source Code

- Implementation: [vktSynchronizationCrossInstanceSharingTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp)
- Header: [vktSynchronizationCrossInstanceSharingTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.hpp)
- Shared operation data: [vktSynchronizationOperationTestData.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp)
- Shared resource data: [vktSynchronizationOperationResources.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp)
- Operation framework: [vktSynchronizationOperation.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperation.hpp)
- External memory utilities: [vktExternalMemoryUtil.hpp](../../../modules/vulkan/util/vktExternalMemoryUtil.hpp)

## Registration Path

```
synchronization.cross_instance          (LEGACY, non-SC)
synchronization2.cross_instance         (SYNCHRONIZATION2, non-SC)
```

Both paths are created by the same factory function invoked with different `SynchronizationType` values. This group is not registered for Vulkan SC.

## Test Hierarchy

```
cross_instance
|-- dedicated
|   |-- <writeOp>_<readOp>
|       |-- <resourceName>_<semaphoreType>_<handleTypeSuffix>
|-- suballocated
    |-- <writeOp>_<readOp>
        |-- <resourceName>_<semaphoreType>_<handleTypeSuffix>
```

Where:
- `<semaphoreType>` is `_binary_semaphore` or `_timeline_semaphore`
- `<handleTypeSuffix>` is one of the platform-specific handle type suffixes (see External Handle Types below)

## Test Families

### Dedicated Allocation Family (`dedicated`)

Tests cross-instance sharing with **dedicated memory allocations** (`VkMemoryDedicatedAllocateInfo`). The external memory is allocated with a dedicated allocation that is bound to the specific buffer or image resource.

### Suballocated Family (`suballocated`)

Tests cross-instance sharing with **suballocated memory** (no dedicated allocation). The external memory is allocated without binding to a specific resource. If the external memory type requires dedicated allocation only (`VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT`), the test is skipped via `checkSupport`.

Both families share the same test logic implemented in [SharingTestInstance](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L646).

## Parameter Dimensions

### Allocation Strategy

| Value | Group Name |
|---|---|
| `dedicated = true` | `dedicated` |
| `dedicated = false` | `suballocated` |

### Write Operations (33 total)

Same set as other operation tests, defined in [s_writeOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36).

### Read Operations (40 total)

Same set as other operation tests, defined in [s_readOps](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L72).

### Resource Types (16 total)

Same set as other operation tests, defined in [s_resources](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36).

### Semaphore Type

| Value | Suffix |
|---|---|
| `VK_SEMAPHORE_TYPE_BINARY` | `_binary_semaphore` |
| `VK_SEMAPHORE_TYPE_TIMELINE` | `_timeline_semaphore` |

Note: `VK_SEMAPHORE_TYPE_TIMELINE` is not combined with `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT` because sync FD semaphores do not support timeline semantics.

### External Handle Types

The test iterates over platform-specific combinations of external memory and semaphore handle types:

| Memory Handle Type | Semaphore Handle Type | Suffix | Platform |
|---|---|---|---|
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | `_fd` | Unix-like |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT` | `_fence_fd` | Unix-like |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `_win32_kmt` | Windows |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `_win32` | Windows |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | `_dma_buf` | Linux |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ZIRCON_VMO_BIT_FUCHSIA` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_ZIRCON_EVENT_BIT_FUCHSIA` | `_zircon_handle` | Fuchsia |

Only handle types supported by the device are actually executed; unsupported combinations are skipped via `checkSupport`.

## Support/Feature Requirements

### Instance-Level Requirements

| Requirement | Always Required |
|---|---|
| `VK_KHR_get_physical_device_properties2` | Yes |
| `VK_KHR_external_semaphore_capabilities` | Yes |
| `VK_KHR_external_memory_capabilities` | Yes |

### Device-Level Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_external_semaphore` | Always |
| `VK_KHR_external_memory` | Always |
| `VK_KHR_dedicated_allocation` | `dedicated = true` |
| `VK_KHR_synchronization2` | `SynchronizationType::SYNCHRONIZATION2` |
| `VK_KHR_timeline_semaphore` | `semaphoreType = TIMELINE` |
| `VK_KHR_external_semaphore_fd` | FD-based handle types |
| `VK_KHR_external_memory_fd` | FD-based handle types |
| `VK_EXT_external_memory_dma_buf` | `DMA_BUF_BIT_EXT` handle type |
| `VK_KHR_external_semaphore_win32` | Win32 handle types |
| `VK_KHR_external_memory_win32` | Win32 handle types |
| `VK_FUCHSIA_external_semaphore` | Zircon handle types |
| `VK_FUCHSIA_external_memory` | Zircon handle types |
| `VK_KHR_get_memory_requirements2` | When available |
| Exportable/importable external memory | Per resource + handle type |
| Exportable/importable external semaphore | Per semaphore + handle type |
| `shaderStorageImageMultisample` | Multisampled storage images |

## Verification Methods

1. **Data comparison**: After cross-instance synchronization, the data written on instance A is compared against the data read on instance B using `deMemCmp` for exact byte comparison.
2. **Indirect buffer comparison**: For indirect buffer resources, the counter value read must be at least as large as the expected value.
3. **Multi-queue iteration**: The test iterates over all queue family combinations across the two instances, verifying correctness for each pair. Unsupported queue combinations are skipped via `NotSupportedError`.
4. **Result collection**: A `tcu::ResultCollector` aggregates results across all queue pair iterations.
5. **Failure criteria**: `tcu::TestStatus::fail` is returned if memory contents do not match or counter values are too small for any queue pair.

## Test Principles

The core principle is: **after proper cross-instance synchronization using external semaphores and external memory, a read operation on one Vulkan instance must observe the data written by a write operation on a different Vulkan instance**. Each test:

1. Creates two independent Vulkan instances (A and B) with their own devices, managed by the [InstanceAndDevice](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L224) singleton.
2. On instance A: creates a resource (buffer or image) with exportable external memory, records and submits the write operation, and signals an exportable semaphore.
3. Exports the memory handle from instance A and imports it into instance B.
4. Exports the semaphore handle from instance A and imports it into instance B.
5. On instance B: waits on the imported semaphore, then records and submits the read operation on the imported resource.
6. Verifies that read data matches written data.

The external memory transfer uses platform-specific native handles (file descriptors on Unix, HANDLEs on Windows, VMO handles on Fuchsia) to share the resource backing memory between instances. The external semaphore provides the execution synchronization guarantee that the read on instance B does not start until the write on instance A has completed.

## Notes/Uncertainties

- The [InstanceAndDevice](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L224) class creates two separate `CustomInstance` objects (A and B) as singletons, shared across all test instances in the group. They are destroyed in the `cleanupGroup` callback.
- Unlike the single-queue and multi-queue tests, this file does **not** use `PipelineCacheData` shared from the parent group. Instead, each `SharingTestInstance` creates its own local `PipelineCacheData`.
- The test creates its own devices via `createCustomDevice` rather than using the context's default device, because it needs two independent devices with specific external memory/semaphore extensions enabled.
- The `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT` variant can only be used with binary semaphores (not timeline), which is enforced by skipping the combination in `createTests`.
- The `checkSupport` method performs extensive validation including checking external image/buffer format properties, external semaphore capabilities, and dedicated allocation requirements. Many combinations will be skipped as `NotSupportedError` on platforms that do not support the required handle types.
- The test iterates over all queue family pairs across the two instances. Queue families that do not support the required operation flags are skipped.
- On Vulkan SC, the entire `cross_instance` group is excluded via `#ifndef CTS_USES_VULKANSC` in the parent registration code.
