# Understanding brief: cross-instance sharing synchronization

## One-sentence purpose

These tests verify that a write submitted through one Vulkan instance becomes the data observed by a read submitted through a second Vulkan instance when exportable/importable external memory and an external semaphore provide the resource handoff and execution dependency.

## Registration and generated tree

The same factory is used for both synchronization APIs:

- `synchronization.cross_instance` — `SynchronizationType::LEGACY`.
- `synchronization2.cross_instance` — `SynchronizationType::SYNCHRONIZATION2` and therefore requires `VK_KHR_synchronization2`.

Both roots have the generated tree:

```text
<root>.cross_instance
├── suballocated
│   └── <writeOp>_<readOp>
│       └── <resource>_<semaphore>_<handle>
└── dedicated
    └── <writeOp>_<readOp>
        └── <resource>_<semaphore>_<handle>
```

`createTests()` loops over 33 write operations, 40 read operations, 16 resource descriptions, six external-handle pairs, and binary/timeline semaphore types. Unsupported operation/resource combinations are not registered. The sync-FD pair is not generated for timeline semaphores. Thus the tree is a generator description, not a promise that every Cartesian-product leaf exists or runs.

## What the test does

1. Create two independent custom instances/devices, A and B.
2. On A, allocate an exportable resource, either as a dedicated allocation or from a suballocation; bind and write it.
3. Export the resource memory handle and import it into B.
4. Signal an exportable semaphore from A, export its native handle, and import it into B.
5. On B, wait on the imported semaphore and read the imported resource.
6. Iterate every compatible source/destination queue-family pair; unsupported queue-operation combinations become `NotSupportedError` skips.
7. Wait for both queues and compare the write/read data. Timeline variants additionally require equal semaphore counter values. Indirect-buffer reads require an actual counter at least as large as expected.

Legacy and synchronization2 submit/barrier behavior is selected by `SynchronizationWrapper`; the sharing and result-check logic is common.

## Parameters and handle gates

Allocation groups are `suballocated` (`dedicated=false`) and `dedicated` (`dedicated=true`, requiring `VK_KHR_dedicated_allocation`). For suballocation, a resource whose external-memory properties contain `VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT` is skipped.

The generated memory/semaphore handle pairs and suffixes are:

| Suffix | Memory handle | Semaphore handle | Intended platform |
|---|---|---|---|
| `_fd` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | Unix-like |
| `_fence_fd` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_SYNC_FD_BIT` | Unix-like |
| `_win32_kmt` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | Windows |
| `_win32` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_WIN32_BIT` | Windows |
| `_dma_buf` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD_BIT` | Linux |
| `_zircon_handle` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ZIRCON_VMO_BIT_FUCHSIA` | `VK_EXTERNAL_SEMAPHORE_HANDLE_TYPE_ZIRCON_EVENT_BIT_FUCHSIA` | Fuchsia |

Only pairs supported by the implementation can execute. The test requires instance capabilities `VK_KHR_get_physical_device_properties2`, `VK_KHR_external_semaphore_capabilities`, and `VK_KHR_external_memory_capabilities`, plus device `VK_KHR_external_memory` and `VK_KHR_external_semaphore`. It conditionally requires timeline semaphore, synchronization2, FD, DMA-BUF, Win32, and Fuchsia extensions according to the selected configuration. It also checks operation support, external buffer/image export+import properties, image samples, and `shaderStorageImageMultisample` when multisampled storage images are used. A timeline semaphore is never paired with sync FD because sync FD has no timeline semantics.

## Failure meaning

A normal resource mismatch fails with `Memory contents don't match`; an indirect result below the expected counter fails with `Counter value is smaller than expected`; a timeline counter mismatch fails with `Inconsistent values between shared semaphores`. Queue-family or capability limitations are skips, not synchronization failures.

## Source anchors

- Registration and leaf generation: [createTests/createCrossInstanceSharingTest](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1199-L1289).
- Capability checks: [SharingTestCase::checkSupport](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L1019-L1178).
- Two-instance setup: [InstanceAndDevice](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L224-L645).
- Cross-instance submit/import/readback: [SharingTestInstance::iterate](../../../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp#L646-L1006).
- Category registration: [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L156).
- Shared operation/resource tables: [vktSynchronizationOperationTestData.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp) and [vktSynchronizationOperationResources.hpp](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp).

## Audit questions

- Are platform-specific native-handle suffixes clear enough for the target implementation?
- Is the distinction between capability skips and data/synchronization failures clear?
- Is the generated-tree notation sufficiently precise without enumerating the very large filtered matrix?
