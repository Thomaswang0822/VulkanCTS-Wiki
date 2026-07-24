## Overview

The `memory` test category collects tests that check device-memory allocation, requirements, binding, host access, synchronization, external-memory integration, reporting, decompression, and extension-specific mapping behavior.

## Background Knowledge

- **Memory types, heaps, and resource compatibility.** A physical device exposes memory heaps and memory types. Each memory type names a heap and a set of properties. Buffer and image memory requirements provide the allocation size, alignment, and compatible memory-type mask that constrain allocation and binding.
- **Host-visible and non-coherent memory.** Host-visible memory can be mapped into the process address space. Host-coherent memory does not require explicit cache-management calls for host visibility; non-coherent memory uses atom-aligned flushes after host writes and invalidations before host reads.
- **Memory dependencies.** Pipeline stages and access scopes define how writes become available and visible to later device or host accesses. Cache management and execution/memory dependencies solve different parts of host-device visibility, so tests often need both.

## Category Structure

```text
memory
├── allocation
├── device_group_allocation
├── external_memory_acquire_unmodified
├── pageable_allocation
├── mapping
├── pipeline_barrier
├── concurrent_access
├── requirements
├── binding
├── external_memory_host
├── device_memory_report
├── address_binding_report
├── decompression
├── zero_initialize_device_memory
├── dma_heap_memory
└── map_placed
```

The registration-only dispatcher routes these 16 test families to 14 implementation-focused Level-3 pages. `allocation`, `device_group_allocation`, and `pageable_allocation` share one implementation and one page.

## How the Families Fit Together

The test families cover the lifetime of device memory and the ways applications observe or move its contents:

- **Allocation and compatibility:** `allocation`, `device_group_allocation`, `pageable_allocation`, `requirements`, and `binding` check which memory can be created and attached to resources.
- **Host access and visibility:** `mapping`, `map_placed`, `pipeline_barrier`, `concurrent_access`, and `zero_initialize_device_memory` check mapped access, address placement, synchronization, and observable initial contents.
- **External and platform memory:** `external_memory_acquire_unmodified`, `external_memory_host`, and `dma_heap_memory` check ownership transfer or import from host and operating-system memory facilities.
- **Specialized operations and reporting:** `decompression`, `device_memory_report`, and `address_binding_report` check decompression commands and callback records for memory or address-space events.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `allocation`, `device_group_allocation`, `pageable_allocation` | [Allocation.md](../testfiles/memory/Allocation.md) | Deterministic and randomized allocation/free behavior, device masks, and pageable device-local allocation. |
| `external_memory_acquire_unmodified` | [ExternalMemoryAcquireUnmodified.md](../testfiles/memory/ExternalMemoryAcquireUnmodified.md) | Foreign queue-family release/acquire behavior and preservation of untouched external-image regions. |
| `mapping` | [Mapping.md](../testfiles/memory/Mapping.md) | Full and subrange mapping, remapping, flush/invalidate behavior, and dedicated allocations. |
| `pipeline_barrier` | [PipelineBarrier.md](../testfiles/memory/PipelineBarrier.md) | Generated producer-consumer pairs, stage/access scopes, image layouts, and host/device visibility. |
| `concurrent_access` | [ConcurrentAccess.md](../testfiles/memory/ConcurrentAccess.md) | Disjoint host and compute-shader access to one storage buffer. |
| `requirements` | [Requirements.md](../testfiles/memory/Requirements.md) | Buffer/image requirement queries, dedicated and multiplane outputs, memory flags, and create-info queries. |
| `binding` | [Binding.md](../testfiles/memory/Binding.md) | Regular and aliased binding, allocation priority, dynamic priority, and per-bind status. |
| `external_memory_host` | [ExternalMemoryHost.md](../testfiles/memory/ExternalMemoryHost.md) | Host-pointer import, rendering from imported memory, and host/device synchronization. |
| `device_memory_report` | [DeviceMemoryReport.md](../testfiles/memory/DeviceMemoryReport.md) | Allocation, free, import, and unimport callback records and memory-object identity. |
| `address_binding_report` | [AddressBinding.md](../testfiles/memory/AddressBinding.md) | Device-address BIND/UNBIND callback pairing across Vulkan object types. |
| `decompression` | [Decompression.md](../testfiles/memory/Decompression.md) | Direct and indirect memory-decompression dispatch and host verification. |
| `zero_initialize_device_memory` | [ZeroInitializeDeviceMemory.md](../testfiles/memory/ZeroInitializeDeviceMemory.md) | Zero-initialized buffer and image allocations observed through transfer, shader, and depth/stencil paths. |
| `dma_heap_memory` | [ExternalDmaHeap.md](../testfiles/memory/ExternalDmaHeap.md) | DMA-heap allocation, dma-buf import, binding, shader access, offsets, and readback. |
| `map_placed` | [MapPlaced.md](../testfiles/memory/MapPlaced.md) | Caller-selected mapping addresses, CPU/GPU access, and unmap-with-reservation behavior. |
