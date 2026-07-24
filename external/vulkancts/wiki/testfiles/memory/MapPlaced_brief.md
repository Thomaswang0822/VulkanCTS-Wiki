# Understanding Brief: `memory.map_placed`

## One-Sentence Test Purpose

This test checks whether `VK_EXT_map_memory_placed` maps host-visible device memory at a requested virtual address and whether `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` preserves the intended address range after unmapping.

## Background Knowledge

### Host-visible device memory and placed mappings

`VkDeviceMemory` with `VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT` can be mapped into the process address space. `vkMapMemory2` accepts extensible mapping parameters. With `VK_MEMORY_MAP_PLACED_BIT_EXT`, the `VkMemoryMapPlacedInfoEXT` structure supplies the requested address.

Why it matters here:

- A successful placed map must return the requested address; the test checks pointer equality.
- The requested address and allocation size have alignment restrictions derived from `minPlacedMemoryMapAlignment`.

### Host/device visibility for non-coherent memory

A host write to non-coherent mapped memory needs `vkFlushMappedMemoryRanges` before the device reads it. A device write needs execution and memory dependencies, completion, and `vkInvalidateMappedMemoryRanges` before the host reads it.

Why it matters here:

- The `gpu_access` test initializes a storage buffer through the placed mapping, dispatches a compute shader, then checks the same mapping.
- The test flushes and invalidates only when the chosen memory type is not host coherent.

## One Concrete Example

The `dEQP-VK.memory.map_placed.gpu_access.read_write` test allocates and binds a host-visible storage buffer, then reserves an aligned virtual address with `mmap`. It maps the `VkDeviceMemory` at that address with `vkMapMemory2` and `VK_MEMORY_MAP_PLACED_BIT_EXT`. The host writes `data[i] = i`; a compute shader increments each element; the host verifies `data[i] == i + 1` after the queue completes.

## End-to-End Test Flow

```text
[host] check VK_EXT_map_memory_placed, VK_KHR_map_memory2, feature bits, and POSIX support
[host] choose a host-visible memory type and size; align the placed range when needed
[host] reserve or create a process address range with mmap or memfd-backed mappings
[host] allocate VkDeviceMemory and map it at the selected address, or map normally for the legacy path
[host] run the behavior selected by the registered test family
[device] for gpu_access, compute invocations increment storage-buffer elements
[host] unmap or unmap with VK_MEMORY_UNMAP_RESERVE_BIT_EXT
[host] inspect pointer placement, guard ranges, process-map coverage, or GPU results
[host] report pass or the first failed assertion
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

Only `gpu_access` generates a shader. [`MapPlacedTestCase::initPrograms()`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L860-L877) adds a GLSL 4.50 compute shader with `local_size_x = 64`; each in-range invocation increments one `uint` in the storage buffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkDeviceMemory` | yes | for `gpu_access` | yes | yes | The object under test is mapped at a caller-chosen address. |
| Storage buffer | yes, `gpu_access` only | yes | compute shader reads and writes it | through the placed map | Carries the CPU-to-GPU-to-CPU data round trip. |
| Reserved virtual range | yes, with `mmap` | no | no | host inspection only | Supplies the requested placed address and exposes unwanted range replacement. |
| `memfd` double mappings | yes, exact-size paths | no | no | yes | Lets the test distinguish guard pages from the driver's placed mapping. |

## What Is Checked

- `exact_size` checks that `vkMapMemory2` returns exactly `pPlacedAddress`, that surrounding guard pages retain the fill pattern, and that the inspector mapping does not see the fill pattern in the Vulkan-mapped range.
- `gpu_access` checks every element against `i + 1` after CPU initialization, compute dispatch, synchronization, and any required invalidate.
- `unmap_reserve` checks that guards remain accessible after unmapping a placed map with `VK_MEMORY_UNMAP_RESERVE_BIT_EXT`, then checks that `/proc/self/maps` covers the reserved range on supported Linux hosts.
- `normal_unmap_reserve` applies the same unmap flag to a legacy `vkMapMemory` mapping, probes a fresh `mmap(NULL, ...)` for overlap, and checks `/proc/self/maps` coverage.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `exact_size`, `gpu_access`, `unmap_reserve`, `normal_unmap_reserve`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `exact_size` | Incorrect requested-address placement, replacement of pages outside the placed range, or inaccessible/corrupted guard ranges. |
| `gpu_access` | Incorrect placed mapping access, host/device visibility handling, buffer binding, compute execution, or readback. |
| `unmap_reserve` | Incorrect reservation semantics after unmapping a placed mapping. |
| `normal_unmap_reserve` | Incorrect reservation semantics after `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` is applied to a normal mapping. |

## Important Variations and Special Cases

- `exact_size`, `unmap_reserve`, and `normal_unmap_reserve` use 4096, 8192, 65536, and 1048576 byte cases. `gpu_access` uses 65536 bytes.
- Tests require Linux or Android POSIX mapping support. The `/proc/self/maps` check is skipped on Android by its implementation.
- `gpu_access` prefers a device-local and host-visible memory type, then falls back to any host-visible compatible type.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Exact-size placed map | [`MapPlacedExactSizeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L130-L433) | Builds the memfd guard layout, maps at the selected address, and performs the range checks. |
| CPU/GPU data path | [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L435-L724) | Binds the storage buffer, dispatches compute work, and checks the incremented values. |
| Shader construction | [`MapPlacedTestCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L860-L877) | Emits the compute shader. |
| Registration and feature checks | [`createMapPlacedTests`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L817-L997) | Defines the registered families, sizes, and prerequisites. |
| Vulkan mapping semantics | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L4820-L5316) | Defines host mapping, placed map placement, and non-coherent flush/invalidate behavior. |

## Questions / Risk Points for User Audit

- Does the four-family behavior axis make the separation between placement, GPU access, and reservation semantics clear?
- Is the distinction between the memfd inspector checks and real `VkDeviceMemory` contents clear?
- Does the compute walkthrough have enough detail to explain the GPU path without duplicating the page runtime section?

## Conversion Notes for Final Wiki Rewrite

- Use the four registered test families as `## Behavior Parameters` subsections.
- Copy the Failure Cause Mapping table unchanged into the final page.
- Use `gpu_access.read_write` for the single representative shader walkthrough.
- Keep the POSIX and extension feature gates in `## Case Pruning`.
- Keep the full source inventory in the final appendix rather than in the explanation flow.
