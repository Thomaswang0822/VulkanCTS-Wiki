# Memory Tests — Root Registration

The `vktMemoryTests.cpp` file is the **registration dispatcher** for the entire Vulkan CTS memory category. It defines the top-level `memory` test group and populates it with child subgroups, each implemented in a separate source file.

## Source

[`vktMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryTests.cpp)

## Role

Central registration point. The [`createTests()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L82) factory function is called by the test package to create the top-level `memory` group. The [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52) function inside the anonymous namespace adds all child subgroups.

## Registration Path

```
vk-test-package → memory (createTests) → <children>
```

## Test Hierarchy

The memory category contains **16 child groups**. Groups are split between Vulkan (non-SC) and Vulkan SC due to the removal of `vkFreeMemory` in Vulkan SC, which makes random allocation/free tests unreliable.

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

## Child Group Reference

| Group Name | Source File | Level-3 Doc |
|------------|------------|-------------|
| `allocation` | [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md) |
| `device_group_allocation` | [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md) |
| `pageable_allocation` | [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp) | [vktMemoryAllocationTests.md](vktMemoryAllocationTests.md) |
| `mapping` | [`vktMemoryMappingTests.cpp`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp) | [vktMemoryMappingTests.md](vktMemoryMappingTests.md) |
| `pipeline_barrier` | [`vktMemoryPipelineBarrierTests.cpp`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp) | [vktMemoryPipelineBarrierTests.md](vktMemoryPipelineBarrierTests.md) |
| `concurrent_access` | [`vktMemoryConcurrentAccessTests.cpp`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp) | [vktMemoryConcurrentAccessTests.md](vktMemoryConcurrentAccessTests.md) |
| `requirements` | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp) | [vktMemoryRequirementsTests.md](vktMemoryRequirementsTests.md) |
| `binding` | [`vktMemoryBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp) | [vktMemoryBindingTests.md](vktMemoryBindingTests.md) |
| `external_memory_host` | [`vktMemoryExternalMemoryHostTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp) | [vktMemoryExternalMemoryHostTests.md](vktMemoryExternalMemoryHostTests.md) |
| `external_memory_acquire_unmodified` | [`vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp) | [vktMemoryExternalMemoryAcquireUnmodifiedTests.md](vktMemoryExternalMemoryAcquireUnmodifiedTests.md) |
| `device_memory_report` | [`vktMemoryDeviceMemoryReportTests.cpp`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp) | [vktMemoryDeviceMemoryReportTests.md](vktMemoryDeviceMemoryReportTests.md) |
| `address_binding_report` | [`vktMemoryAddressBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp) | [vktMemoryAddressBindingTests.md](vktMemoryAddressBindingTests.md) |
| `decompression` | [`vktMemoryDecompressionTests.cpp`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp) | [vktMemoryDecompressionTests.md](vktMemoryDecompressionTests.md) |
| `zero_initialize_device_memory` | [`vktMemoryZeroInitializeDeviceMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp) | [vktMemoryZeroInitializeDeviceMemoryTests.md](vktMemoryZeroInitializeDeviceMemoryTests.md) |
| `dma_heap_memory` | [`vktMemoryExternalDmaHeapTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp) | [vktMemoryExternalDmaHeapTests.md](vktMemoryExternalDmaHeapTests.md) |
| `map_placed` | [`vktMemoryMapPlacedTests.cpp`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp) | [vktMemoryMapPlacedTests.md](vktMemoryMapPlacedTests.md) |

## Notes

- The `allocation`, `device_group_allocation`, and `pageable_allocation` groups share a single implementation via [`createAllocationTestsCommon()`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1029) with different `AllocationMode` values.
- The `pipeline_barrier` group is the largest subgroup (~10K lines), covering memory visibility across pipeline stages with various resource usages.
- VKSC-excluded groups are guarded by `#ifndef CTS_USES_VULKANSC` preprocessor blocks at the [`#include`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L34) level and within [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L56).
