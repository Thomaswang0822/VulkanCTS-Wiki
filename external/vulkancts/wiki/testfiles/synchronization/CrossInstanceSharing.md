# vktSynchronizationCrossInstanceSharingTests

## Purpose

`vktSynchronizationCrossInstanceSharingTests.cpp` tests Vulkan resource and semaphore sharing between **two independent Vulkan instances/devices**. Instance A writes an exportable buffer or image and signals an exportable semaphore. Instance B imports both native handles, waits on the imported semaphore, reads the resource, and checks that the write is visible. This exercises external-memory ownership plus cross-instance execution and memory synchronization.

## Registration

The factory is called once for each synchronization category:

| Category | Path | Synchronization mode |
|---|---|---|
| Legacy synchronization | `synchronization.cross_instance` | `SynchronizationType::LEGACY` |
| Synchronization 2 | `synchronization2.cross_instance` | `SynchronizationType::SYNCHRONIZATION2` |

Both paths contain `suballocated` and `dedicated` groups. The parent registration is inside `#ifndef CTS_USES_VULKANSC`; cross-instance tests are therefore absent from Vulkan SC builds.

## Generated hierarchy

```text
<root>.cross_instance
├── suballocated
│   └── <writeOp>_<readOp>
│       └── <resource>_<semaphore>_<handle>
└── dedicated
    └── <writeOp>_<readOp>
        └── <resource>_<semaphore>_<handle>
```

`<root>` is `synchronization` or `synchronization2`. The operation group name is formed from `getOperationName(writeOp) + "_" + getOperationName(readOp)`. A leaf is formed from `getResourceName(resource)`, `_binary_semaphore` or `_timeline_semaphore`, and the external-handle suffix. A leaf is added only when both operations support that resource; capability checks can later skip it with `NotSupportedError`.

`createTests()` loops over 33 entries in `s_writeOps`, 40 entries in `s_readOps`, 16 entries in `s_resources`, six handle pairs, and both semaphore types. The `_fence_fd` (`VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT`) pair is deliberately omitted for timeline semaphores.

## Families

### `suballocated`

Uses external memory that is not dedicated to one resource. If the queried external-memory properties advertise `VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT`, this configuration is skipped. This group passes `dedicated=false` to the allocation/import helpers.

### `dedicated`

Uses a `VkMemoryDedicatedAllocateInfo`-style dedicated allocation bound to the selected buffer or image. It passes `dedicated=true` and requires `VK_KHR_dedicated_allocation`.

The two families otherwise use the same `SharingTestCase`/`SharingTestInstance` implementation.

## External handle matrix

| Leaf suffix | Memory handle type | Semaphore handle type | Platform family |
|---|---|---|---|
| `_fd` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | Unix-like |
| `_fence_fd` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT` | Unix-like |
| `_win32_kmt` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | Windows |
| `_win32` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_BIT` | Windows |
| `_dma_buf` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | Linux |
| `_zircon_handle` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ZIRCON_VMO_BIT_FUCHSIA` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_ZIRCON_EVENT_BIT_FUCHSIA` | Fuchsia |

The source registers all six combinations, but a test executes only when the implementation supports the selected operation, resource format, external memory export/import, external semaphore export/import, queue requirements, and handle APIs. The suffix describes the requested handle pair; it is not a guarantee that the host platform supports it.

## Required functionality and gates

Every leaf requires these instance capabilities:

- `VK_KHR_get_physical_device_properties2`
- `VK_KHR_external_semaphore_capabilities`
- `VK_KHR_external_memory_capabilities`

Every leaf requires device `VK_KHR_external_memory` and `VK_KHR_external_semaphore`. Additional requirements are conditional:

| Condition | Required functionality |
|---|---|
| `dedicated` | `VK_KHR_dedicated_allocation` |
| `SynchronizationType::SYNCHRONIZATION2` | `VK_KHR_synchronization2` |
| Timeline semaphore | `VK_KHR_timeline_semaphore` |
| FD memory or semaphore handle | `VK_KHR_external_memory_fd`, `VK_KHR_external_semaphore_fd` |
| DMA-BUF memory handle | `VK_EXT_external_memory_dma_buf` |
| Win32 memory or semaphore handle | `VK_KHR_external_memory_win32`, `VK_KHR_external_semaphore_win32` |
| Zircon memory or semaphore handle | `VK_FUCHSIA_external_memory`, `VK_FUCHSIA_external_semaphore` |
| Available memory-requirements-2 path | `VK_KHR_get_memory_requirements2` is enabled when supported |
| Multisampled storage image | `shaderStorageImageMultisample` feature |

`checkSupport()` additionally queries external image/buffer properties and external semaphore properties. Both memory and semaphore must advertise exportable and importable support. Images must support the requested format, tiling, usage, and sample count. Operation support and required queue flags are checked independently for A and B. Unsupported queue-family pairs are reported as skips.

## Execution and verification

`InstanceAndDevice` owns two custom instances/devices and their interfaces. For each queue-family pair, the test:

1. Creates and binds the exportable resource on A.
2. Exports its native memory handle and imports it into B.
3. Creates semaphores of the selected binary or timeline type.
4. Records the write operation and its release barrier on A.
5. Submits A and exports/imports the semaphore handle.
6. Records B's acquire barrier and read operation, then submits B waiting on the imported semaphore.
7. Waits for both queues and, for timeline semaphores, compares the counters reported by A and B.
8. Compares expected write data with actual read data.

Normal resources use exact `deMemCmp` comparison. For indirect-buffer resources, the actual counter must be at least the expected counter. Any mismatch is collected as a test failure; `NotSupportedError` from capability or queue checks is a skip. Validation messages from both instances are collected before the result is returned. The group cleanup destroys the two-instance singleton.

The `SynchronizationWrapper` selects the legacy or synchronization2 submission/barrier API, while the external-handle and readback algorithm remains shared.

## Exact test paths and mustpass files

A concrete path has this form (with the selected operation/resource/handle names substituted):

```text
dEQP-VK.synchronization.cross_instance.<suballocated|dedicated>.<writeOp>_<readOp>.<resource>_<binary_semaphore|timeline_semaphore>_<fd|fence_fd|win32_kmt|win32|dma_buf|zircon_handle>
dEQP-VK.synchronization2.cross_instance.<suballocated|dedicated>.<writeOp>_<readOp>.<resource>_<binary_semaphore|timeline_semaphore>_<fd|fence_fd|win32_kmt|win32|dma_buf|zircon_handle>
```

Repository mustpass lists containing these paths:

- [`external/vulkancts/mustpass/main/vk-default/synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt)
- [`external/vulkancts/mustpass/main/vk-default/synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt)

Historical Android mustpass lists also contain the legacy path in `android/cts/main/src/vk-main-2019-03-01.txt`, `vk-main-2020-03-01.txt`, `vk-main-2021-03-01.txt`, `vk-main-2023-03-01.txt`, and `vk-main-2024-03-01-part2.txt`; synchronization2 appears in the latter three. Platform-specific lists do not necessarily enumerate every generated leaf, and unsupported leaves are expected to skip.

## Source map

- [Factory and leaf generation](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1199-L1289)
- [Two-instance/device management](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L224-L645)
- [Execution and result checks](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L646-L1006)
- [Capability checks](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1019-L1178)
- [Category registration](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L156)
- [Public declaration](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.hpp#L34)
- [Operation tables](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp)
- [Resource table](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp)

## Audit notes

- The matrix dimensions describe generator loops; they do not imply all combinations are compatible or present in a mustpass list.
- The `_fence_fd` suffix denotes sync-FD semaphores, not Vulkan fences; it is binary-only.
- Vulkan SC exclusion comes from the parent registration site, not from the cross-instance factory itself.
