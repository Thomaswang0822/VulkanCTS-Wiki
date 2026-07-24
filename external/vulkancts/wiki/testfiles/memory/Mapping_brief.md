# Understanding Brief: `memory.mapping`

## One-Sentence Test Purpose

This test checks whether host-visible Vulkan memory can be mapped, modified, remapped, flushed, invalidated, and released correctly for suballocated and dedicated allocations.

## Background Knowledge

### Mapped-memory visibility

Host-visible memory can be mapped into process memory. For non-coherent memory, host writes need a flush before device visibility, while device writes need the required device-to-host dependency and invalidate before host observation. [Host access to device memory](../../../../vulkan-docs/src/chapters/memory.adoc#L4820-L4880)

Why it matters here:

- The deterministic and random paths compare mapped bytes after flush and invalidate sequences.
- Every non-coherent range is expanded to `nonCoherentAtomSize` boundaries before cache operations.

### Allocation ownership

A mapping may cover a suballocation, a dedicated buffer allocation, or a dedicated linear-image allocation. Dedicated allocation requirements can restrict which memory types are valid for a selected resource. [Dedicated memory allocation](../../../../vulkan-docs/src/chapters/memory.adoc#L1833-L1875)

Why it matters here:

- The registered hierarchy groups suballocation separately from dedicated buffer and image cases.
- The source skips unsupported selected resource/type combinations instead of treating them as failures.

## One Concrete Example

A `suballocation.sub.size_257.offset_17.size_31.flush_map2` case maps a 31-byte subrange of a 257-byte suballocation with `vkMapMemory2KHR`, writes the test pattern, rounds the flush range to the device's non-coherent atom size, flushes it, and compares the mapped data with the reference model.

## End-to-End Test Flow

```text
[host] select allocation kind, mapping range, operation, and map API variant
[host] create host-visible memory and any selected buffer or image resource
[host] map the full allocation or requested subrange
[host] write, read, unmap/remap, flush, or invalidate according to the case
[host] update the ReferenceMemory model alongside each observable operation
[host] compare sampled mapped bytes against the model or verify allocation-callback cleanup
[host] continue eligible memory types and report the aggregated result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The page has no shaders. `ReferenceMemory` is a host-side model that tracks defined bytes and flushed atom ranges.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkDeviceMemory` | yes | no | no | mapped by host | The object being mapped and cache-managed. |
| Buffer or linear image | selected dedicated paths | yes | no | no | Provides memory requirements for dedicated allocation cases. |
| `ReferenceMemory` | yes | no | no | host-only | Defines the expected byte and flush state for verification. |

## What Is Checked

- `simple` verifies that host writes and reads through the selected mapping agree with the reference model.
- `remap` verifies that the data remains correct after unmap and remap.
- `flush` and `subflush` variants exercise full, middle, separate, and registered overlapping-named cache ranges.
- `invalidate` variants test reference-state behavior after flush/invalidate sequences.
- `implicit_unmap` frees a mapped allocation and checks allocation-callback cleanup.
- Random cases execute 100 seeded iterations of allocation, mapping, byte operations, and cache operations against `ReferenceMemory`.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node and operation leaf
>
> **Candidate values:** `suballocation`, `dedicated_alloc.buffer`, `dedicated_alloc.image`; `simple`, `remap`, `implicit_unmap`, `flush`, `subflush`, `subflush_separate`, `subflush_overlapping`, `invalidate`, `subinvalidate`, `subinvalidate_separate`, `subinvalidate_overlapping`, `random`

## What Failure Means

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

## Important Variations and Special Cases

- Each applicable deterministic leaf has normal and `_map2` forms.
- `suballocation.random` has 100 seeds, each with normal and `_map2` forms.
- The registered names `subflush_overlapping` and `subinvalidate_overlapping` currently use the separate-range operation enum in source; the final page should state source behavior rather than infer overlapping semantics from those names.
- Vulkan SC omits `implicit_unmap` because the path uses allocation callbacks.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Reference model | [`ReferenceMemory`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L222-L302) | Defines expected byte and atom-flush state. |
| Deterministic path | [`testMemoryMapping`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L636-L977) | Implements mapping, operations, and comparison. |
| Random path | [`RandomMappingTestInstance`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1214-L1790) | Implements seeded stress behavior. |
| Registration | [`createMappingTests`](../../../modules/vulkan/memory/vktMemoryMappingTests.cpp#L1959-L2114) | Defines hierarchy, ranges, operations, and API variants. |

## Questions / Risk Points for User Audit

- Does the page clearly separate the registered operation names from their source-bound operation behavior?
- Is `ReferenceMemory` explained as a host-side oracle rather than a GPU resource?

## Conversion Notes for Final Wiki Rewrite

- Use allocation kind as the first behavioral axis and operation leaf as the second.
- Copy the Failure Cause Mapping table unchanged into the final page.
- State that no shader participates.
