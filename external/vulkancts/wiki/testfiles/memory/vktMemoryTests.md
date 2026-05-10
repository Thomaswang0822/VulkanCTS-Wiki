# Memory Tests — Root Registration

The `vktMemoryTests.cpp` file is the **registration dispatcher** for the entire Vulkan CTS memory category. It defines the top-level `memory` test group and populates it with child subgroups, each implemented in a separate source file.

## Source

[`vktMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryTests.cpp)

## Role

Central registration point. The [`createTests()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L82) factory function is called by the test package to create the top-level `memory` group. The [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52) function inside the anonymous namespace adds all child subgroups.

## Registration Hierarchy

```text
memory
├── allocation (VK only)
├── device_group_allocation (VK only)
├── external_memory_acquire_unmodified (VK only)
├── pageable_allocation (VK only)
├── mapping (VK only)
├── pipeline_barrier (VK only)
├── concurrent_access (VK + VKSC)
├── requirements (VK + VKSC)
├── binding (VK + VKSC)
├── external_memory_host (VK + VKSC)
├── device_memory_report (VK only)
├── address_binding_report (VK only)
├── decompression (VK only)
├── zero_initialize_device_memory (VK only)
├── dma_heap_memory (VK only)
└── map_placed (VK only)
```

### VK / VKSC Split

The memory category contains **16 child groups**. Groups are split between Vulkan (non-SC) and Vulkan SC due to the removal of `vkFreeMemory` in Vulkan SC, which makes random allocation/free tests unreliable.

| Group | VK | VKSC | Reason |
|-------|:--:|:----:|--------|
| `allocation` | ✓ | — | Random alloc/free tests fail when `vkFreeMemory` is absent ([line 57](../../../modules/vulkan/memory/vktMemoryTests.cpp#L57)) |
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

## Test Families

### allocation — Memory allocation tests

Source: [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | Doc: [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md)

### device_group_allocation — Device-group memory allocation tests

Source: [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | Doc: [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md)

### external_memory_acquire_unmodified — External memory acquire-unmodified tests

Source: [`vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp) | Doc: [vktMemoryExternalMemoryAcquireUnmodifiedTests.md](vktMemoryExternalMemoryAcquireUnmodifiedTests.md)

### pageable_allocation — Pageable host allocation tests

Source: [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | Doc: [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md)

### mapping — Memory mapping tests

Source: [`vktMemoryMappingTests.cpp`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp) | Doc: [vktMemoryMappingTests.md](vktMemoryMappingTests.md)

### pipeline_barrier — Memory pipeline barrier tests

Source: [`vktMemoryPipelineBarrierTests.cpp`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp) | Doc: [vktMemoryPipelineBarrierTests.md](vktMemoryPipelineBarrierTests.md)

### concurrent_access — Concurrent memory access tests

Source: [`vktMemoryConcurrentAccessTests.cpp`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp) | Doc: [vktMemoryConcurrentAccessTests.md](vktMemoryConcurrentAccessTests.md)

### requirements — Memory requirements tests

Source: [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp) | Doc: [vktMemoryRequirementsTests.md](vktMemoryRequirementsTests.md)

### binding — Memory binding tests

Source: [`vktMemoryBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp) | Doc: [vktMemoryBindingTests.md](vktMemoryBindingTests.md)

### external_memory_host — External memory host tests

Source: [`vktMemoryExternalMemoryHostTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp) | Doc: [vktMemoryExternalMemoryHostTests.md](vktMemoryExternalMemoryHostTests.md)

### device_memory_report — Device memory report tests

Source: [`vktMemoryDeviceMemoryReportTests.cpp`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp) | Doc: [vktMemoryDeviceMemoryReportTests.md](vktMemoryDeviceMemoryReportTests.md)

### address_binding_report — Address binding report tests

Source: [`vktMemoryAddressBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp) | Doc: [vktMemoryAddressBindingTests.md](vktMemoryAddressBindingTests.md)

### decompression — Memory decompression tests

Source: [`vktMemoryDecompressionTests.cpp`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp) | Doc: [vktMemoryDecompressionTests.md](vktMemoryDecompressionTests.md)

### zero_initialize_device_memory — Zero-initialize device memory tests

Source: [`vktMemoryZeroInitializeDeviceMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp) | Doc: [vktMemoryZeroInitializeDeviceMemoryTests.md](vktMemoryZeroInitializeDeviceMemoryTests.md)

### dma_heap_memory — DMA heap memory tests

Source: [`vktMemoryExternalDmaHeapTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp) | Doc: [vktMemoryExternalDmaHeapTests.md](vktMemoryExternalDmaHeapTests.md)

### map_placed — Map-placed memory tests

Source: [`vktMemoryMapPlacedTests.cpp`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp) | Doc: [vktMemoryMapPlacedTests.md](vktMemoryMapPlacedTests.md)

## Notes

- The `allocation`, `device_group_allocation`, and `pageable_allocation` groups share a single implementation via [`createAllocationTestsCommon()`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1029) with different `AllocationMode` values.
- The `pipeline_barrier` group is the largest subgroup (~10K lines), covering memory visibility across pipeline stages with various resource usages.
- VKSC-excluded groups are guarded by `#ifndef CTS_USES_VULKANSC` preprocessor blocks at the [`#include`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L34) level and within [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L56).
