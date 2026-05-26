# Memory Tests

The `memory` category validates Vulkan device memory management, including allocation, binding, mapping, visibility, synchronization, and external memory import. It covers core memory operations (`vkAllocateMemory`, `vkBindBufferMemory`, `vkMapMemory`), memory requirements queries, pipeline barrier visibility, and numerous extension-specific behaviors such as external memory host import, DMA heap integration, memory decompression, and placed memory mapping. The historical Vulkan API test plan frames the relevant memory-management objectives as allocation/suballocation, mapped CPU access, CPU/GPU cache-control visibility, and binding memory to buffers or images ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L191-L258)).

## Source

- **Root registration:** [`vktMemoryTests.cpp`](../../modules/vulkan/memory/vktMemoryTests.cpp)
- **Mustpass:** [`memory.txt`](../../mustpass/main/vk-default/memory.txt)

## Registration Entry Point

The [`createTests()`](../../modules/vulkan/memory/vktMemoryTests.cpp#L82) factory creates the top-level `memory` group. The internal [`createChildren()`](../../modules/vulkan/memory/vktMemoryTests.cpp#L52) function adds 16 child subgroups, split between Vulkan-only and Vulkan+VKSC builds.

## Subgroup Structure

```
memory
├── allocation                        (VK only)
├── device_group_allocation           (VK only)
├── external_memory_acquire_unmodified(VK only)
├── pageable_allocation               (VK only)
├── mapping                           (VK only)
├── pipeline_barrier                  (VK only)
├── concurrent_access                 (VK + VKSC)
├── requirements                      (VK + VKSC)
├── binding                           (VK + VKSC)
├── external_memory_host              (VK + VKSC)
├── device_memory_report              (VK only)
├── address_binding_report            (VK only)
├── decompression                     (VK only)
├── zero_initialize_device_memory     (VK only)
├── dma_heap_memory                   (VK only)
└── map_placed                        (VK only)
```

### VK / VKSC Split

| Group | VK | VKSC | Reason |
|-------|:--:|:----:|--------|
| `allocation` | ✓ | — | Random alloc/free tests fail when `vkFreeMemory` is absent ([line 57](../../modules/vulkan/memory/vktMemoryTests.cpp#L57)) |
| `device_group_allocation` | ✓ | — | Same as above |
| `external_memory_acquire_unmodified` | ✓ | — | Behind `CTS_USES_VULKANSC` guard |
| `pageable_allocation` | ✓ | — | Same as above |
| `mapping` | ✓ | — | Same as above |
| `pipeline_barrier` | ✓ | — | Same as above |
| `concurrent_access` | ✓ | ✓ | Always included |
| `requirements` | ✓ | ✓ | Always included |
| `binding` | ✓ | ✓ | Always included |
| `external_memory_host` | ✓ | ✓ | Always included |
| `device_memory_report` | ✓ | — | Behind `CTS_USES_VULKANSC` guard |
| `address_binding_report` | ✓ | — | Same as above |
| `decompression` | ✓ | — | Same as above |
| `zero_initialize_device_memory` | ✓ | — | Same as above |
| `dma_heap_memory` | ✓ | — | Same as above |
| `map_placed` | ✓ | — | Same as above |

## File Inventory

### Registration / Dispatcher

| File | Role |
|------|------|
| [`vktMemoryTests.cpp`](../../modules/vulkan/memory/vktMemoryTests.cpp) | Category root registration (dispatches to 16 factory functions) |
| [`vktMemoryTests.hpp`](../../modules/vulkan/memory/vktMemoryTests.hpp) | Category header (`createTests` declaration) |

### Implementation Files

| File | Group(s) | Level-3 Doc |
|------|----------|-------------|
| [`vktMemoryAllocationTests.cpp`](../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | `allocation`, `device_group_allocation`, `pageable_allocation` | [vktMemoryAllocationTests.md](../testfiles/memory/vktMemoryAllocationTests.md) |
| [`vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp`](../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp) | `external_memory_acquire_unmodified` | [vktMemoryExternalMemoryAcquireUnmodifiedTests.md](../testfiles/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.md) |
| [`vktMemoryMappingTests.cpp`](../../modules/vulkan/memory/vktMemoryMappingTests.cpp) | `mapping` | [vktMemoryMappingTests.md](../testfiles/memory/vktMemoryMappingTests.md) |
| [`vktMemoryPipelineBarrierTests.cpp`](../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp) | `pipeline_barrier` | [vktMemoryPipelineBarrierTests.md](../testfiles/memory/vktMemoryPipelineBarrierTests.md) |
| [`vktMemoryConcurrentAccessTests.cpp`](../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp) | `concurrent_access` | [vktMemoryConcurrentAccessTests.md](../testfiles/memory/vktMemoryConcurrentAccessTests.md) |
| [`vktMemoryRequirementsTests.cpp`](../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp) | `requirements` | [vktMemoryRequirementsTests.md](../testfiles/memory/vktMemoryRequirementsTests.md) |
| [`vktMemoryBindingTests.cpp`](../../modules/vulkan/memory/vktMemoryBindingTests.cpp) | `binding` | [vktMemoryBindingTests.md](../testfiles/memory/vktMemoryBindingTests.md) |
| [`vktMemoryExternalMemoryHostTests.cpp`](../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp) | `external_memory_host` | [vktMemoryExternalMemoryHostTests.md](../testfiles/memory/vktMemoryExternalMemoryHostTests.md) |
| [`vktMemoryDeviceMemoryReportTests.cpp`](../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp) | `device_memory_report` | [vktMemoryDeviceMemoryReportTests.md](../testfiles/memory/vktMemoryDeviceMemoryReportTests.md) |
| [`vktMemoryAddressBindingTests.cpp`](../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp) | `address_binding_report` | [vktMemoryAddressBindingTests.md](../testfiles/memory/vktMemoryAddressBindingTests.md) |
| [`vktMemoryDecompressionTests.cpp`](../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp) | `decompression` | [vktMemoryDecompressionTests.md](../testfiles/memory/vktMemoryDecompressionTests.md) |
| [`vktMemoryZeroInitializeDeviceMemoryTests.cpp`](../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp) | `zero_initialize_device_memory` | [vktMemoryZeroInitializeDeviceMemoryTests.md](../testfiles/memory/vktMemoryZeroInitializeDeviceMemoryTests.md) |
| [`vktMemoryExternalDmaHeapTests.cpp`](../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp) | `dma_heap_memory` | [vktMemoryExternalDmaHeapTests.md](../testfiles/memory/vktMemoryExternalDmaHeapTests.md) |
| [`vktMemoryMapPlacedTests.cpp`](../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp) | `map_placed` | [vktMemoryMapPlacedTests.md](../testfiles/memory/vktMemoryMapPlacedTests.md) |

### Utility / Header Files (no Level-3 docs)

| File | Role |
|------|------|
| [`vktMemoryAllocationTests.hpp`](../../modules/vulkan/memory/vktMemoryAllocationTests.hpp) | Allocation factory declarations |
| [`vktMemoryConcurrentAccessTests.hpp`](../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.hpp) | Concurrent access factory declaration |
| [`vktMemoryPipelineBarrierTests.hpp`](../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.hpp) | Pipeline barrier factory declaration |
| [`vktMemoryRequirementsTests.hpp`](../../modules/vulkan/memory/vktMemoryRequirementsTests.hpp) | Requirements factory declaration |
| [`vktMemoryBindingTests.hpp`](../../modules/vulkan/memory/vktMemoryBindingTests.hpp) | Binding factory declaration |
| [`vktMemoryExternalMemoryHostTests.hpp`](../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.hpp) | External memory host factory declaration |
| [`vktMemoryExternalDmaHeapTests.hpp`](../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.hpp) | DMA heap factory declaration |
| [`vktMemoryMappingTests.hpp`](../../modules/vulkan/memory/vktMemoryMappingTests.hpp) | Mapping factory declaration |
| [`vktMemoryAddressBindingTests.hpp`](../../modules/vulkan/memory/vktMemoryAddressBindingTests.hpp) | Address binding factory declaration |
| [`vktMemoryExternalMemoryAcquireUnmodifiedTests.hpp`](../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.hpp) | External memory acquire unmodified factory declaration |
| [`vktMemoryDeviceMemoryReportTests.hpp`](../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.hpp) | Device memory report factory declaration |
| [`vktMemoryDecompressionTests.hpp`](../../modules/vulkan/memory/vktMemoryDecompressionTests.hpp) | Decompression factory declaration |
| [`vktMemoryZeroInitializeDeviceMemoryTests.hpp`](../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.hpp) | Zero initialize factory declaration |
| [`vktMemoryMapPlacedTests.hpp`](../../modules/vulkan/memory/vktMemoryMapPlacedTests.hpp) | Map placed factory declaration |
| [`CMakeLists.txt`](../../modules/vulkan/memory/CMakeLists.txt) | Build configuration |

## Subgroup Summary

| Group | What It Verifies | Key Extensions |
|-------|-----------------|----------------|
| `allocation` | `vkAllocateMemory`/`vkFreeMemory` correctness across all memory types, sizes, and orderings | Core |
| `device_group_allocation` | Device group allocation with `VkMemoryAllocateFlagsInfo` | `VK_KHR_device_group` |
| `pageable_allocation` | Allocation with pageable device-local memory | `VK_EXT_pageable_device_local_memory` |
| `external_memory_acquire_unmodified` | Ownership acquire preserves unmodified image regions | `VK_EXT_external_memory_acquire_unmodified` |
| `mapping` | `vkMapMemory`/`vkUnmapMemory`/`vkFlushMappedMemoryRanges`/`vkInvalidateMappedMemoryRanges` correctness | `VK_KHR_map_memory2` |
| `pipeline_barrier` | Memory visibility across pipeline stages via `vkCmdPipelineBarrier` | Core |
| `concurrent_access` | Host+device concurrent access to storage buffers | Core |
| `requirements` | `VkMemoryRequirements` validity and API consistency | `VK_KHR_get_memory_requirements2`, `VK_KHR_dedicated_allocation`, `VK_KHR_maintenance4` |
| `binding` | `vkBindBufferMemory2`/`vkBindImageMemory2` correctness, aliasing, priority | `VK_KHR_bind_memory2`, `VK_EXT_memory_priority`, `VK_KHR_maintenance6` |
| `external_memory_host` | Importing host-allocated memory into Vulkan | `VK_EXT_external_memory_host` |
| `device_memory_report` | Device memory report callback correctness | `VK_EXT_device_memory_report` |
| `address_binding_report` | Device address binding callback correctness | `VK_EXT_device_address_binding_report` |
| `decompression` | GPU-accelerated GDeflate decompression | `VK_EXT_memory_decompression` |
| `zero_initialize_device_memory` | Zero-initialization of newly allocated device memory | `VK_EXT_zero_initialize_device_memory` |
| `dma_heap_memory` | DMA heap-backed buffer allocation and GPU access | `VK_EXT_external_memory_dma_buf` |
| `map_placed` | Caller-specified address memory mapping | `VK_EXT_map_memory_placed` |

## Cross-File Recurring Test Families

### Memory Type Iteration

Multiple subgroups iterate over all compatible device memory types at runtime, returning `incomplete()` between types:

- `allocation` — all memory types ([vktMemoryAllocationTests.cpp:627](../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L627))
- `mapping` — all host-visible types ([vktMemoryMappingTests.cpp:705](../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L705))
- `pipeline_barrier` — all non-protected, compatible types ([vktMemoryPipelineBarrierTests.cpp:9492](../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9492))
- `zero_initialize_device_memory` — all types matching `ZeroInitialize` requirement ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:101](../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L101))

### Allocate-Bind-Use Pattern

A common pattern across binding, mapping, and pipeline barrier tests:

1. Create resource (buffer/image)
2. Allocate memory
3. Bind memory to resource
4. Perform operations (write/read/transfer)
5. Verify correctness

### Host-Device Synchronization

Tests that verify data consistency between CPU and GPU access:

- `concurrent_access` — simultaneous host read during device write ([vktMemoryConcurrentAccessTests.cpp:77](../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L77))
- `external_memory_host` — host signals timeline semaphore, GPU reads ([vktMemoryExternalMemoryHostTests.cpp:758](../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L758))
- `dma_heap_memory` — host → GPU → host round-trip ([vktMemoryExternalDmaHeapTests.cpp:159](../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L159))
- `map_placed` — CPU write → GPU increment → CPU verify ([vktMemoryMapPlacedTests.cpp:435](../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L435))

### Callback/Report Validation

Two subgroups validate Vulkan callback mechanisms:

- `device_memory_report` — `ALLOCATE`/`FREE`/`IMPORT`/`UNIMPORT` event pairing ([vktMemoryDeviceMemoryReportTests.cpp:1663](../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1663))
- `address_binding_report` — `BIND`/`UNBIND` event pairing ([vktMemoryAddressBindingTests.cpp:1650](../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1650))

## Cross-File Recurring Parameter Dimensions

| Dimension | Subgroups | Typical Values |
|-----------|-----------|----------------|
| Buffer/image size | `allocation`, `mapping`, `binding`, `pipeline_barrier`, `map_placed` | 33B – 16MB, powers of 2 |
| Memory type | `allocation`, `mapping`, `pipeline_barrier`, `zero_initialize_device_memory` | All compatible types (runtime iteration) |
| Allocation kind | `allocation`, `mapping` | Suballocated, dedicated buffer, dedicated image |
| Free/mapping order | `allocation`, `mapping` | Forward, reverse, mixed |
| Format | `external_memory_acquire_unmodified`, `external_memory_host`, `zero_initialize_device_memory`, `requirements` | UNORM, SFLOAT, UINT, SINT, BC compressed, depth/stencil |
| External handle type | `external_memory_acquire_unmodified`, `external_memory_host`, `device_memory_report`, `dma_heap_memory` | DMA_BUF, OPAQUE_FD, ANDROID_HARDWARE_BUFFER, HOST_ALLOCATION |

## Cross-File Recurring Support Requirements

| Requirement | Subgroups |
|-------------|-----------|
| `VK_KHR_get_physical_device_properties2` | `allocation`, `mapping`, `requirements` |
| `VK_AMD_device_coherent_memory` (skip if feature not enabled) | `allocation`, `mapping`, `pipeline_barrier`, `zero_initialize_device_memory` |
| Protected memory exclusion | `pipeline_barrier`, `zero_initialize_device_memory` |
| Host-visible memory requirement | `mapping`, `pipeline_barrier` (host_read/write), `concurrent_access`, `map_placed` |
| Custom device creation | `allocation`, `mapping`, `device_memory_report`, `address_binding_report`, `binding` (priority_dynamic) |
| Linux/Android platform | `dma_heap_memory`, `map_placed` |

## Cross-File Recurring Verification Methods

| Method | Subgroups |
|--------|-----------|
| Reference model comparison | `mapping` (ReferenceMemory), `pipeline_barrier` (reference data), `dma_heap_memory` (pattern match) |
| Image comparison (tcu::imageCompare) | `external_memory_acquire_unmodified`, `external_memory_host`, `zero_initialize_device_memory` |
| Byte-by-byte memcmp | `zero_initialize_device_memory`, `decompression` |
| Callback pairing validation | `device_memory_report`, `address_binding_report` |
| /proc/self/maps inspection | `map_placed` |

## Notes

- The `allocation`, `device_group_allocation`, and `pageable_allocation` groups share a single implementation via a common factory function with different `AllocationMode` values ([vktMemoryAllocationTests.cpp:1029](../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1029)).
- The `pipeline_barrier` subgroup is the largest in the category (~10K lines) due to combinatorial coverage of write→read usage pairs.
- The `zero_initialize_device_memory` group uses factory symbol `createClearedAllocationControlTests()` but registers under the group name `zero_initialize_device_memory`.
- VKSC-excluded groups are guarded by `#ifndef CTS_USES_VULKANSC` at both the `#include` level ([line 34](../../modules/vulkan/memory/vktMemoryTests.cpp#L34)) and within `createChildren()` ([line 56](../../modules/vulkan/memory/vktMemoryTests.cpp#L56)).
- The `dma_heap_memory` and `map_placed` groups are Linux/Android-only, requiring platform-specific APIs (`memfd_create`, DMA heap ioctls).
