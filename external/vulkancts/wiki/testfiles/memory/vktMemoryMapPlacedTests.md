# Map Placed Memory Tests

Tests for `VK_EXT_map_memory_placed` and `VK_KHR_map_memory2`. Validates that memory can be mapped at a caller-specified address (placed mapping), that the mapping is accessible to both CPU and GPU, and that the `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` unmap flag correctly reserves the address range.

## Source

- [vktMemoryMapPlacedTests.cpp](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp)

## Registration

- **Group name:** `map_placed`
- **Registration function:** [`createMapPlacedTests()`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L926)
- **Parent group:** `memory`

## Registration Hierarchy

```text
memory.map_placed
├── exact_size
├── gpu_access
├── unmap_reserve
└── normal_unmap_reserve
```

## Test Families

### exact_size — Exact-size placed mapping verification

Tests that `vkMapMemory2` with `VK_MEMORY_MAP_PLACED_BIT_EXT` maps memory at exactly the requested address, without mapping extra pages on either side. Uses a double-mmap strategy:
1. A memfd file is created and mapped twice (reserved map and inspector map)
2. Memory is allocated and mapped at a placed address within the reserved map
3. The file is filled with a pattern (`0xAB`)
4. After unmapping, the inspector map verifies:
   - Guard pages before the Vulkan mapping retain the fill pattern
   - The Vulkan region itself does NOT show the fill pattern (driver mapped its own pages)
   - Guard pages after the Vulkan mapping retain the fill pattern ([vktMemoryMapPlacedTests.cpp:130-433](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L130))

### gpu_access — CPU/GPU round-trip through placed mapping

Tests that placed-mapped memory is accessible to both CPU and GPU without corruption:
1. CPU writes sequential values (`data[i] = i`) to the placed mapping
2. GPU (compute shader) increments each value by 1
3. CPU reads back and verifies `data[i] == i + 1` ([vktMemoryMapPlacedTests.cpp:435-724](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L435))

### unmap_reserve — UNMAP_RESERVE after placed mapping

Tests `vkUnmapMemory2` with `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` after a placed mapping. After unmap:
1. Guard pages before and after the Vulkan mapping are verified to still be accessible and contain the fill pattern
2. `/proc/self/maps` is checked to confirm the reserved range is still covered ([vktMemoryMapPlacedTests.cpp:86-128](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L86))

### normal_unmap_reserve — UNMAP_RESERVE after normal vkMapMemory

Tests `vkUnmapMemory2` with `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` after a **normal** `vkMapMemory` (not placed mapping). Verifies:
1. The address range remains reserved after unmap
2. A subsequent `mmap(NULL)` does not land in the reserved range
3. `/proc/self/maps` shows the range is still covered ([vktMemoryMapPlacedTests.cpp:726-815](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L726))

## Parameter Dimensions

### Memory sizes

| Size | Pages (4KB) | Test Groups |
|------|-------------|-------------|
| 4096 | 1 | exact_size, unmap_reserve, normal_unmap_reserve |
| 8192 | 2 | exact_size, unmap_reserve, normal_unmap_reserve |
| 65536 | 16 | exact_size, unmap_reserve, normal_unmap_reserve, gpu_access |
| 1048576 (1MB) | 256 | exact_size, unmap_reserve, normal_unmap_reserve |

### Alignment

The placed mapping must be aligned to `max(system_page_size, minPlacedMemoryMapAlignment)`:
- `minPlacedMemoryMapAlignment` is queried from `VkPhysicalDeviceMapMemoryPlacedPropertiesEXT` ([vktMemoryMapPlacedTests.cpp:147-154](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L147))
- The test rounds the Vulkan allocation size up to a multiple of this alignment ([vktMemoryMapPlacedTests.cpp:162-164](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L162))

## Support Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_map_memory_placed` | All tests ([vktMemoryMapPlacedTests.cpp:830](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L830)) |
| `VK_KHR_map_memory2` | All tests ([vktMemoryMapPlacedTests.cpp:831](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L831)) |
| `memoryMapPlaced` feature | All tests ([vktMemoryMapPlacedTests.cpp:841-842](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L841)) |
| `memoryUnmapReserve` feature | unmap_reserve, normal_unmap_reserve ([vktMemoryMapPlacedTests.cpp:844-845](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L844), [vktMemoryMapPlacedTests.cpp:907-908](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L907)) |
| Linux/Android with `memfd_create` | All tests ([vktMemoryMapPlacedTests.cpp:139](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L139)) |

## Verification Methods

### Exact address mapping ([vktMemoryMapPlacedTests.cpp:250-258](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L250))

After `vkMapMemory2`, the returned pointer is compared against the requested `pPlacedAddress`:
```
mappedPtr == placedAddr  // must be exact match
```

### Inspector map verification ([vktMemoryMapPlacedTests.cpp:328-383](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L328))

The inspector map (a second independent mmap of the same memfd) is used to verify:
1. **Guard before:** Bytes before the Vulkan mapping show the fill pattern (`0xAB`)
2. **Vulkan region:** Bytes in the Vulkan region do NOT show the fill pattern (driver mapped different pages)
3. **Guard after:** Bytes after the Vulkan mapping show the fill pattern

### CPU/GPU round-trip ([vktMemoryMapPlacedTests.cpp:686-702](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L686))

For non-coherent memory, `vkFlushMappedMemoryRanges` is called before GPU access and `vkInvalidateMappedMemoryRanges` is called after GPU access. Each element is verified:
```
data[i] == i + 1  // CPU wrote i, GPU added 1
```

### /proc/self/maps verification ([vktMemoryMapPlacedTests.cpp:86-128](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L86))

On Linux (non-Android), the test reads `/proc/self/maps` and checks that some region fully covers the `[rangeStart, rangeEnd)` range after `UNMAP_RESERVE`.

### mmap probe ([vktMemoryMapPlacedTests.cpp:783-801](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L783))

For `normal_unmap_reserve`, a `mmap(NULL, pageSize, PROT_NONE, ...)` is performed and verified not to overlap the reserved range.

## Test Principles

- **Double-mmap isolation:** The exact_size and unmap_reserve tests use two independent mmaps of the same memfd to isolate the driver's mapping behavior from the test's reserved address space
- **Guard page verification:** Fill patterns on both sides of the Vulkan mapping confirm the driver maps exactly the requested pages
- **Re-mapping verification:** After unmap, the test attempts to re-map at the same address and performs a CPU read/write verification (`0xCAFEBABE`) ([vktMemoryMapPlacedTests.cpp:385-419](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L385))
- **Address reservation:** `UNMAP_RESERVE` ensures the virtual address range remains reserved, preventing the OS from recycling it for other mappings

## Notes

- All tests are Linux/Android-only — they require `memfd_create`, `mmap`, and `/proc/self/maps` ([vktMemoryMapPlacedTests.cpp:60-65](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L60))
- The `gpu_access` test uses a single size (65536 bytes) and tests with a buffer bound as a storage buffer to a compute shader
- The test prefers device-local host-visible memory if available, falling back to any host-visible memory type ([vktMemoryMapPlacedTests.cpp:465-469](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L465))
- The `normal_unmap_reserve` tests use `vkMapMemory` (the legacy API) rather than `vkMapMemory2` with `VK_MEMORY_MAP_PLACED_BIT_EXT`, testing that `UNMAP_RESERVE` works with both mapping methods
