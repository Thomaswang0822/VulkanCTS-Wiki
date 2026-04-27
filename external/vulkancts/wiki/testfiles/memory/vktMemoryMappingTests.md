# Memory Mapping Tests

Tests for `vkMapMemory`, `vkUnmapMemory`, `vkFlushMappedMemoryRanges`, and `vkInvalidateMappedMemoryRanges` correctness. Also covers `vkMapMemory2KHR` / `vkUnmapMemory2KHR` from `VK_KHR_map_memory2`. Verifies that host-visible memory can be correctly written, read, flushed, and invalidated across all memory types and allocation kinds.

## Source

[`vktMemoryMappingTests.cpp`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp)

## Verified Group Name

`mapping` ([line 1963](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1963))

## Registration Path

```
memory → mapping
```

## Test Hierarchy

```
mapping/
├── suballocation/
│   ├── full/
│   │   ├── variable/
│   │   │   ├── implicit_unmap
│   │   │   └── implicit_unmap_map2
│   │   ├── 33/
│   │   │   ├── simple
│   │   │   ├── simple_map2
│   │   │   ├── remap / remap_map2
│   │   │   ├── flush / flush_map2
│   │   │   ├── subflush / subflush_map2
│   │   │   ├── subflush_separate / subflush_separate_map2
│   │   │   ├── subflush_overlapping / subflush_overlapping_map2
│   │   │   ├── invalidate / invalidate_map2
│   │   │   ├── subinvalidate / subinvalidate_map2
│   │   │   ├── subinvalidate_separate / subinvalidate_separate_map2
│   │   │   └── subinvalidate_overlapping / subinvalidate_overlapping_map2
│   │   ├── 257/ ...
│   │   ├── 4087/ ...
│   │   ├── 8095/ ...
│   │   └── 1048577/ ...
│   └── sub/
│   │   ├── variable/ ...
│   │   ├── 33/ ...
│   │   ├── 257/ ...
│   │   ├── 4087/ ...
│   │   ├── 8095/ ...
│   │   └── 1048577/ ...
│   └── random/ (100 seeded cases × 2 map variants)
│       ├── 0, 0_map2
│       ├── 1, 1_map2
│       ├── ...
│       └── 99, 99_map2
├── dedicated_alloc/
│   ├── buffer/
│   │   ├── full/ ...
│   │   └── sub/ ...
│   └── image/
│       ├── full/ ...
│       └── sub/ ...
```

## Test Families

### Full Mapping (full)

Maps the entire allocation (offset=0, size=allocationSize). Writes random data, optionally flushes, optionally remaps, optionally invalidates, then reads back and compares against a reference model. Implemented by [`testMemoryMapping()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:637).

### Sub Mapping (sub)

Maps a sub-range of the allocation with explicit offset and size. Same write-flush-invalidate-read cycle as full mapping, but exercises partial mapping correctness. Uses [`subMappedConfig()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1813) to build test configs.

### Random Mapping (random)

Performs 100 random operations: allocate, free, map, unmap, read, write, modify, flush, and invalidate across all host-visible memory heaps. Uses a [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:229) model to track defined/flushed state per byte. Implemented by [`RandomMemoryMappingInstance`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1487).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Allocation size | 0 (variable), 33, 257, 4087, 8095, 1MiB+1 | [line 1971](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1971) |
| Allocation kind | SUBALLOCATED, DEDICATED_BUFFER, DEDICATED_IMAGE | [`AllocationKind`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:91) |
| Mapping offset | 0, 17, 129, 255, 1025, 32KiB+1 (sub only) | [line 1975](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1975) |
| Mapping size | 31, 255, 1025, 4085, 1MiB-1 (sub only) | [line 1977](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1977) |
| Operation | simple, remap, implicit_unmap, flush, subflush, subflush_separate, subflush_overlapping, invalidate, subinvalidate, subinvalidate_separate, subinvalidate_overlapping | [`Op`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1793) |
| Map function | vkMapMemory / vkMapMemory2KHR | [line 2002](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:2002) |
| Random seed | `rng.getUint32()` from seed 3927960301u | [line 2115](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:2115) |
| Memory type | All host-visible device memory types (iterated at runtime) | [line 705](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:705) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_get_physical_device_properties2 | Always required | [`checkSupport()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1942) |
| VK_KHR_dedicated_allocation | Required for DEDICATED_BUFFER or DEDICATED_IMAGE allocation kinds | [line 1947](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1947) |
| VK_KHR_map_memory2 | Required for `memoryMap2=true` tests | [`checkMapMemory2Support()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1934) |
| VK_AMD_device_coherent_memory | Types skipped if feature not enabled | [line 723](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:723) |
| Host-visible memory | Only host-visible types are tested; non-host-visible types are skipped with log message | [line 818](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:818) |

## Verification Methods

1. **Reference model comparison**: [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:229) tracks per-byte defined/flushed state. After write, flush, and invalidate operations, the mapped memory contents are compared against the reference model using [`compareAndLogBuffer()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:542).
2. **Non-coherent atom alignment**: All mapping offsets, sizes, flush ranges, and invalidate ranges are aligned to `nonCoherentAtomSize` ([line 713](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:713)).
3. **Implicit unmap validation**: For `OP_IMPLICIT_UNMAP`, uses `AllocationCallbackRecorder` to verify that no live allocations remain after `vkFreeMemory` on mapped memory ([line 922](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:922)).
4. **Random mapping reference**: [`MemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:952) class tracks reads/writes/modifies against `ReferenceMemory`, checking that undefined bytes read back correctly.

## Test Principles

- **Coherency model verification**: The `ReferenceMemory` class models the Vulkan coherency rules: bytes are "defined" after write or invalidate, and "flushed" after `vkFlushMappedMemoryRanges`. Invalidating a non-flushed range marks bytes as undefined ([line 277](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:277)).
- **Sub-range correctness**: Sub-mapping tests verify that partial mappings with explicit offset/size work correctly, including flush and invalidate of sub-ranges within the mapping.
- **Remap correctness**: The `OP_REMAP` variant unmaps and remaps between flush and invalidate, testing that the implementation correctly preserves data across remap operations.
- **VK_KHR_map_memory2 coverage**: Every test case is duplicated with `_map2` suffix, using `vkMapMemory2KHR` / `vkUnmapMemory2KHR` instead of the original functions ([line 2002](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:2002)).

## Notes

- `implicit_unmap` tests are VK-only (excluded in Vulkan SC) because they use `VkAllocationCallbacks` ([line 1986](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:1986)).
- The `implicit_unmap` variant uses a variable allocation size (found via binary search) rather than a fixed size ([line 728](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:728)).
- Protected memory device creation is handled separately when `implicitUnmap` is true and protected memory is supported ([line 664](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:664)).
- Heap size must be at least 4× the allocation size for a test to run; otherwise the memory type is skipped ([line 822](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp:822)).
