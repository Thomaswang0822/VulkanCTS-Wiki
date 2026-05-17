# Memory Mapping Tests

Tests for `vkMapMemory`, `vkUnmapMemory`, `vkFlushMappedMemoryRanges`, and `vkInvalidateMappedMemoryRanges` correctness. Also covers `vkMapMemory2KHR` / `vkUnmapMemory2KHR` from `VK_KHR_map_memory2`. Verifies that host-visible memory can be correctly written, read, flushed, and invalidated across all memory types and allocation kinds.

## Source

[`vktMemoryMappingTests.cpp`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp)

## Verified Group Name

`mapping` ([line 1963](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1963))

## Registration Hierarchy

```text
memory.mapping
├── suballocation
└── dedicated_alloc
```

Evidence:
- `mapping` group created at [`createMappingTests()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1960)
- `suballocation` subgroup added at [line 2134](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L2134)
- `dedicated_alloc` subgroup added at [line 2137](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L2137)

## Test Families

### suballocation — Suballocated memory mapping

Tests using suballocated (`ALLOCATION_KIND_SUBALLOCATED`) host-visible memory. Contains three sub-families:

#### full — Full Mapping

Maps the entire allocation (offset=0, size=allocationSize). Writes random data, optionally flushes, optionally remaps, optionally invalidates, then reads back and compares against a reference model. Implemented by [`testMemoryMapping()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L637).

The `full` subgroup is further organized by allocation size, each containing operation-based leaf tests:
- `variable` — contains `implicit_unmap` and `implicit_unmap_map2` (VK only)
- `33`, `257`, `4087`, `8095`, `1048577` — each contains `simple`, `simple_map2`, `remap`, `remap_map2`, `flush`, `flush_map2`, `subflush`, `subflush_map2`, `subflush_separate`, `subflush_separate_map2`, `subflush_overlapping`, `subflush_overlapping_map2`, `invalidate`, `invalidate_map2`, `subinvalidate`, `subinvalidate_map2`, `subinvalidate_separate`, `subinvalidate_separate_map2`, `subinvalidate_overlapping`, `subinvalidate_overlapping_map2`

#### sub — Sub Mapping

Maps a sub-range of the allocation with explicit offset and size. Same write-flush-invalidate-read cycle as full mapping, but exercises partial mapping correctness. Uses [`subMappedConfig()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1813) to build test configs.

The `sub` subgroup is further organized by allocation size, then by offset (`offset_N`) and size (`size_N`) subgroups, each containing the same operation-based leaf tests as `full`.

#### random — Random Mapping

Performs 100 random operations: allocate, free, map, unmap, read, write, modify, flush, and invalidate across all host-visible memory heaps. Uses a [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L229) model to track defined/flushed state per byte. Implemented by [`RandomMemoryMappingInstance`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1487).

The `random` subgroup contains 100 seeded cases (0-99), each duplicated with `_map2` suffix for `VK_KHR_map_memory2` coverage.

### dedicated_alloc — Dedicated allocation memory mapping

Tests using dedicated allocations with `VK_KHR_dedicated_allocation`. Contains two sub-families:

#### buffer — Buffer dedicated allocation

Tests with `ALLOCATION_KIND_DEDICATED_BUFFER`. Contains `full` and `sub` subgroups with the same structure as the suballocation variants, exercising the same mapping operations but backed by dedicated buffer memory.

#### image — Image dedicated allocation

Tests with `ALLOCATION_KIND_DEDICATED_IMAGE`. Contains `full` and `sub` subgroups with the same structure as the suballocation variants, exercising the same mapping operations but backed by dedicated image memory.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Allocation size | 0 (variable), 33, 257, 4087, 8095, 1MiB+1 | [line 1971](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1971) |
| Allocation kind | SUBALLOCATED, DEDICATED_BUFFER, DEDICATED_IMAGE | [`AllocationKind`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L91) |
| Mapping offset | 0, 17, 129, 255, 1025, 32KiB+1 (sub only) | [line 1975](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1975) |
| Mapping size | 31, 255, 1025, 4085, 1MiB-1 (sub only) | [line 1977](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1977) |
| Operation | simple, remap, implicit_unmap, flush, subflush, subflush_separate, subflush_overlapping, invalidate, subinvalidate, subinvalidate_separate, subinvalidate_overlapping | [`Op`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1793) |
| Map function | vkMapMemory / vkMapMemory2KHR | [line 2002](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L2002) |
| Random seed | `rng.getUint32()` from seed 3927960301u | [line 2115](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L2115) |
| Memory type | All host-visible device memory types (iterated at runtime) | [line 705](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L705) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_get_physical_device_properties2 | Always required | [`checkSupport()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1942) |
| VK_KHR_dedicated_allocation | Required for DEDICATED_BUFFER or DEDICATED_IMAGE allocation kinds | [line 1947](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1947) |
| VK_KHR_map_memory2 | Required for `memoryMap2=true` tests | [`checkMapMemory2Support()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1934) |
| VK_AMD_device_coherent_memory | Types skipped if feature not enabled | [line 723](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L723) |
| Host-visible memory | Only host-visible types are tested; non-host-visible types are skipped with log message | [line 818](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L818) |

## Verification Methods

1. **Reference model comparison**: [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L229) tracks per-byte defined/flushed state. After write, flush, and invalidate operations, the mapped memory contents are compared against the reference model using [`compareAndLogBuffer()`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L542).
2. **Non-coherent atom alignment**: All mapping offsets, sizes, flush ranges, and invalidate ranges are aligned to `nonCoherentAtomSize` ([line 713](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L713)).
3. **Implicit unmap validation**: For `OP_IMPLICIT_UNMAP`, uses `AllocationCallbackRecorder` to verify that no live allocations remain after `vkFreeMemory` on mapped memory ([line 922](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L922)).
4. **Random mapping reference**: [`MemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L952) class tracks reads/writes/modifies against `ReferenceMemory`, checking that undefined bytes read back correctly.

## Test Principles

- **Coherency model verification**: The `ReferenceMemory` class models the Vulkan coherency rules: bytes are "defined" after write or invalidate, and "flushed" after `vkFlushMappedMemoryRanges`. Invalidating a non-flushed range marks bytes as undefined ([line 277](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L277)).
- **Sub-range correctness**: Sub-mapping tests verify that partial mappings with explicit offset/size work correctly, including flush and invalidate of sub-ranges within the mapping.
- **Remap correctness**: The `OP_REMAP` variant unmaps and remaps between flush and invalidate, testing that the implementation correctly preserves data across remap operations.
- **VK_KHR_map_memory2 coverage**: Every test case is duplicated with `_map2` suffix, using `vkMapMemory2KHR` / `vkUnmapMemory2KHR` instead of the original functions ([line 2002](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L2002)).

## Notes

- `implicit_unmap` tests are VK-only (excluded in Vulkan SC) because they use `VkAllocationCallbacks` ([line 1986](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1986)).
- The `implicit_unmap` variant uses a variable allocation size (found via binary search) rather than a fixed size ([line 728](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L728)).
- Protected memory device creation is handled separately when `implicitUnmap` is true and protected memory is supported ([line 664](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L664)).
- Heap size must be at least 4x the allocation size for a test to run; otherwise the memory type is skipped ([line 822](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L822)).
