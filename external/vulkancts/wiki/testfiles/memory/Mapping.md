## Overview

**Core question:** Do Vulkan mapping APIs preserve the expected host-visible byte state across full and subrange mappings, remaps, cache operations, and allocation lifetimes?

- This page covers [`vktMemoryMappingTests.cpp`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp), which implements the Vulkan-only `memory.mapping` test family.
- The test covers suballocated memory plus dedicated buffer and linear-image allocations.
- It uses deterministic cases for named mapping operations and seeded random cases for interleaved mapping, byte, and cache behavior.

## Background Knowledge

For the shared concepts memory types, heaps, resource compatibility, and host-visible and non-coherent memory, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- A suballocation is a range in a larger allocation. A dedicated allocation backs one selected resource and can have different compatible memory types from a general allocation.
- `ReferenceMemory` is host-side test state. It records which bytes are defined and which non-coherent atoms have been flushed; it is not a Vulkan resource.

## Registration Hierarchy

```text
memory.mapping
├── suballocation
└── dedicated_alloc
```

`suballocation` contains `full`, `sub`, and `random` intermediate nodes. `dedicated_alloc` contains `buffer` and `image` intermediate nodes, each with `full` and `sub` areas.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Allocation kind | `suballocation`, `dedicated_alloc.buffer`, `dedicated_alloc.image` | Selects the allocation/resource shape being mapped. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1959-L2114) |
| Mapping area | `full`, `sub`, `random` | Selects full-range, subrange, or seeded interleaved operations. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1959-L2114) |
| Allocation size | `variable`, `33`, `257`, `4087`, `8095`, `1048577` | Changes available mapping subranges and tests non-aligned sizes. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1960-L2095) |
| Subrange offset | `0`, `17`, `129`, `255`, `1025`, `32769` | Selects the start of a mapping within the allocation when valid for that size. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1960-L2095) |
| Subrange size | `31`, `255`, `1025`, `4085`, `1048575` | Selects the mapped portion and cache-operation range. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1960-L2095) |
| Map API | ordinary leaf, `_map2` leaf | Selects `vkMapMemory`/`vkUnmapMemory` or `vkMapMemory2KHR`/`vkUnmapMemory2KHR`. | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1959-L2114) |

## Behavior Parameters

The allocation-kind intermediate node and operation leaf jointly control behavior.

### suballocation: range within a larger allocation

This area maps a selected range from a general host-visible allocation. `full` covers whole allocations, `sub` exercises valid offset/size pairs, and `random` interleaves allocation, mapping, byte, flush, and invalidate operations.

### dedicated_alloc.buffer: dedicated buffer memory

This area creates a buffer and allocates memory dedicated to it. The same full and subrange operations check that resource-specific requirements do not change host mapping correctness.

### dedicated_alloc.image: dedicated linear-image memory

This area applies the full and subrange operations to a dedicated linear-image allocation. It is separate because selected image requirements can change compatible memory types.

The operation leaf supplies the second behavioral axis.

### simple and remap: mapped byte access

`simple` writes and checks mapped bytes. `remap` unmaps and maps again before checking that the expected byte state remains accessible.

### implicit_unmap: freeing a mapped allocation

This operation frees mapped memory without an explicit unmap and verifies allocation-callback cleanup. It exists only where Vulkan allocation callbacks are permitted.

### flush and invalidate operation leaves: cache-range behavior

These leaves apply full, partial, separate-range, or registered overlapping-named flush/invalidate sequences. The implementation expands non-coherent ranges to atom boundaries and compares resulting state against a host-side reference byte vector.

### random: seeded lifetime and cache stress

Each random case makes 100 seeded iterations across allocations, mappings, byte operations, and one to ten atom-aligned cache ranges. `ReferenceMemory` defines the expected state.

## Shader Analysis

No shader code participates in this test. All observations come from host mappings, cache commands, allocation callbacks, and the host-side reference byte vector or `ReferenceMemory` model.

## Runtime Execution and Result Checking

- The deterministic path selects eligible host-visible memory types, creates the selected allocation kind, maps the requested range, applies the operation, and compares mapped bytes against a host-side reference byte vector. [`testMemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L636-L977)
- The random path uses `ReferenceMemory`, which marks writes as defined and unflushed, marks flushed atoms, and removes defined state from unflushed bytes when an invalidate observes them. [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L222-L302)
- The source rounds flush and invalidate ranges to `nonCoherentAtomSize` boundaries before issuing Vulkan calls. [`testMemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L774-L914)
- Random cases cap relevant allocation usage, run 100 iterations per seed, and use `ReferenceMemory` to check map/unmap and cache behavior. [`RandomMemoryMappingInstance`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1214-L1790)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `suballocation` | Incorrect mapping or cache behavior for a range within a larger allocation. |
| `dedicated_alloc.buffer` | Incorrect mapping or requirements handling for a dedicated buffer allocation. |
| `dedicated_alloc.image` | Incorrect mapping or requirements handling for a dedicated linear-image allocation. |
| `simple` or `remap` | Incorrect mapped-memory access or preservation across a remap. |
| flush or invalidate operation leaf | Incorrect non-coherent cache-range handling or reference-visible byte behavior. |
| `implicit_unmap` | Incorrect cleanup when mapped memory is freed. |
| `random` | Incorrect lifetime, mapping, byte, or cache-range behavior during the seeded stress sequence. |

### Cause Analysis

#### Mapping or remapping failure

**Possible failure symptoms:** A mapped byte differs from the reference model, or a remapped range does not preserve the expected byte state.

**Possible implementation causes:** The result can indicate incorrect host mapping, range selection, or memory-lifetime handling. The source tests only eligible host-visible types and records expected bytes independently, so source-level investigation should compare the failing mapping range with the corresponding allocation and API variant.

#### Dedicated-allocation requirements failure

**Possible failure symptoms:** A dedicated buffer or image case fails while an equivalent suballocation behavior does not.

**Possible implementation causes:** The selected resource's requirements or compatible memory-type handling may differ from general allocation handling. The source skips unsupported combinations; an unexpected failure warrants investigation of the dedicated-resource requirement and mapping path.

#### Cache-range failure

**Possible failure symptoms:** A flush/invalidate leaf produces byte state different from the host-side reference byte vector after the source-adjusted atom-aligned ranges are applied.

**Possible implementation causes:** The implementation may handle non-coherent atom boundaries, flush availability, invalidate visibility, or the requested mapping range incorrectly. The test's model derives expected state from the same operation sequence, which makes the selected leaf and ranges the starting point for diagnosis.

#### Implicit-unmap or random-lifetime failure

**Possible failure symptoms:** Allocation-callback state remains live after `implicit_unmap`, or a deterministic random seed produces an allocation, mapping, or reference-state mismatch.

**Possible implementation causes:** The source may expose incorrect cleanup or lifetime accounting. Random seeds are fixed and therefore support reproduction; source-level investigation is needed to localize a specific implementation fault.

## Case Pruning

### Requirement-based pruning

- The test family is not registered for Vulkan SC.
- Deterministic cases require `VK_KHR_get_physical_device_properties2`; `_map2` cases require `VK_KHR_map_memory2`.
- Dedicated cases require `VK_KHR_dedicated_allocation` and skip memory types unsupported by the selected resource.
- The source works only with host-visible memory types, skips unavailable AMD device-coherent types, and returns Not Supported when no eligible type runs.

### Design-based pruning

- Invalid offset/size pairs are not registered for a selected allocation size.
- `implicit_unmap` is only generated for the variable-size case.
- Registered `subflush_overlapping` and `subinvalidate_overlapping` names currently bind to the separate-range operation enums; this page reports the current source behavior rather than asserting an unobserved overlapping operation.

## Key Takeaways

- `memory.mapping` combines API mapping variants, range selection, cache management, and allocation ownership into one host-side correctness matrix.
- `ReferenceMemory` gives expected state for seeded random stress; the deterministic path uses a simpler host-side reference byte vector.
- Dedicated buffer and image paths ensure that resource-specific memory requirements do not invalidate mapping behavior.
- The source-bound operation enum determines a leaf's effective behavior; its registered name alone does not.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Reference byte/cache model | [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L222-L302) | Defines expected defined-byte and flushed-atom state. |
| Deterministic mapping implementation | [`testMemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L636-L977) | Performs mapping, cache operations, and comparisons. |
| Random mapping implementation | [`RandomMemoryMappingInstance`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1214-L1790) | Performs seeded lifetime and cache stress. |
| Test registration | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1959-L2114) | Defines the hierarchy, values, operation names, and API variants. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt) | Contains registered `dEQP-VK.memory.mapping.*` paths. |
