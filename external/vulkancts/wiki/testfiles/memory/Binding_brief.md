# Understanding Brief: Memory Binding Tests

## One-Sentence Test Purpose

This test checks whether batched buffer and image memory binding preserves transfer data across ordinary, aliased, priority-tagged, dynamically reprioritized, and per-bind-status variants.

## Background Knowledge

### Resource binding and allocation identity

A Vulkan buffer or image has no backing storage until the application binds compatible `VkDeviceMemory`. `vkBindBufferMemory2` and `vkBindImageMemory2` accept arrays of binding descriptions, so one call can bind several resources. A dedicated allocation carries the identity of its buffer or image in the allocation chain; a non-dedicated allocation does not.

Why it matters here:
- Every case binds ten resources in one batch.
- The source calls one path `suballocated`, but it allocates one non-dedicated `VkDeviceMemory` object per target rather than placing ten targets in one shared allocation.

### Aliases, memory priority, and individual status

Two resources alias when both bind the same memory range. Writes through one resource then affect the bytes observed through the other, subject to the resource and synchronization rules. `VkMemoryPriorityAllocateInfoEXT` supplies an allocation-time priority between 0 and 1, while `vkSetDeviceMemoryPriorityEXT` changes an existing allocation's priority. With maintenance6, a `VkBindMemoryStatusKHR` in each bind-info chain receives the result for that individual bind.

Why it matters here:
- The aliasing path writes through the first resource set and reads through the second.
- Priority and maintenance6 alter allocation or binding metadata without changing the expected payload.

## One Concrete Example

For `dEQP-VK.memory.binding.aliasing.suballocated.buffer_33`, the host creates two sets of ten 33-byte buffers. For each index, both buffers bind the same non-dedicated memory object. The host fills a source buffer with a deterministic byte sequence, copies it into the first alias, copies from the second alias into a readback buffer, and compares all 33 bytes with the same sequence. A mismatch means the alias did not expose the storage written through its partner or the transfer/readback path corrupted the data.

## End-to-End Test Flow

```text
[host] select regular or aliasing behavior and allocation/binding modifiers
[host] create ten buffers or images; aliasing creates two sets of ten
[host] query memory requirements and allocate one memory object per index
[host] attach static priority, set dynamic priority, or prepare per-bind status when selected
[host] batch-bind all resources with vkBindBufferMemory2 or vkBindImageMemory2
[host] fill a host-visible source buffer with deterministic bytes and flush it
[host] submit transfer commands that copy source data into each target
[device] execute buffer copies or buffer-to-image copies
[host] regular: copy back from the same target; aliasing: copy back through its paired alias
[device] execute buffer or image readback copies
[host] invalidate mapped readback memory and compare every payload byte
[host] pass only if every target matches and every requested individual bind result is VK_SUCCESS
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source generates a registration matrix from resource sizes, allocation modes, priority modes, and maintenance6 status checking. It does not generate, load, or execute shaders. Commands use Vulkan transfer operations only, so no GLSL, HLSL, SPIR-V, descriptor layout, or graphics/compute pipeline participates.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Ten target buffers or images | yes | yes | yes | indirectly | They receive and return the test payload after batched binding. |
| Second target set in aliasing cases | yes | yes, to the first set's memory objects | read by transfer commands | indirectly | Reading this set checks shared backing-memory visibility. |
| Target `VkDeviceMemory` objects | yes | yes | yes | no | Their allocation form, priority, and bind status are the tested configuration. |
| Source buffer and host-visible memory | yes | yes | read by transfer commands | host writes it | It contains the deterministic expected payload. |
| Destination buffer and host-visible memory | yes | yes | written by transfer commands | yes | It carries bytes into the host comparison. |

## What Is Checked

- `vkBindBufferMemory2` or `vkBindImageMemory2` must return success.
- Maintenance6 cases also require every `VkBindMemoryStatusKHR::pResult` value to report success.
- After each target round trip, each of the first `bufferSize` destination bytes must match the deterministic sequence generated from seed 1 for regular cases or seed 2 for aliasing cases.
- One mismatch makes the test case fail; the loop still checks the remaining targets.

## Behavior Parameter Identification

> **Behavior parameter:** test-family behavior
>
> **Candidate values:** `regular`, `aliasing`, `priority`, `priority_dynamic`, `maintenance6`

`priority` and `priority_dynamic` contain regular and aliasing paths with different priority mechanisms. `maintenance6` contains regular, aliasing, static-priority, and dynamic-priority paths with individual bind-result checking enabled.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `regular` | Batched binding, non-dedicated or dedicated allocation binding, oversized image allocation binding, or transfer data-integrity failure. |
| `aliasing` | Aliased resource binding or cross-alias transfer visibility failure. |
| `priority` | Allocation-time memory-priority handling, or the underlying regular/aliasing binding and transfer path, failed. |
| `priority_dynamic` | Dynamic memory-priority update handling, custom-device setup, or the underlying regular/aliasing binding and transfer path, failed. |
| `maintenance6` | Individual bind-status reporting, or the enclosed default/static/dynamic regular/aliasing path, failed. |

## Important Variations and Special Cases

- Resource leaves cover five buffer sizes and nine image extents. Every case uses ten targets.
- `regular` has `suballocated`, `dedicated`, and `overallocated` intermediate nodes. In the implementation, `suballocated` means non-dedicated one-allocation-per-resource, not a shared suballocation.
- The overallocation factor cycles through 1.5, 2.3, and 3.0. The implementation multiplies image memory requirements by that factor, but its dedicated-buffer allocator does not apply the factor even though `regular.overallocated.buffer_*` leaves are registered.
- Static and dynamic priorities use `i / 10` for allocation index `i`, producing 0.0 through 0.9. Most dynamic paths allocate without a priority chain and call `vkSetDeviceMemoryPriorityEXT` afterward. The dedicated-image specialization chains the priority structure for every non-default mode and also calls the dynamic update.
- Vulkan SC builds register only the default-priority variant and omit maintenance6.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and image setup | [parameter construction](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L143-L215) | Defines target count, sizes, transfer usage, and image format/layout. |
| Priority and allocation paths | [memory creation](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L575-L724) | Shows one allocation per target, dedicated chains, priority values, dynamic updates, and image overallocation. |
| Batched binding and status checks | [binding functions](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L726-L815) | Builds the bind arrays and checks optional per-bind results. |
| Transfer and host comparison | [copy/check helpers](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L817-L988) | Establishes synchronization, copyback, and byte validation. |
| Regular and aliasing flows | [test instances](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L990-L1084) | Shows same-resource round trips versus paired-alias round trips. |
| Registration matrix | [`createMemoryBindingTests`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1126-L1237) | Defines the exact hierarchy, sizes, factors, and variant nesting. |
| Bind-memory semantics | [Vulkan resources chapter](../../../../vulkan-docs/src/chapters/resources.adoc#L10511-L10562) | Defines multi-resource binding and command failure behavior. |
| Priority semantics | [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L2108-L2170) | Defines allocation-time and dynamic priority ranges and operations. |

## Questions / Risk Points for User Audit

- The source resolves the main semantic risk: `suballocated` is a registered identifier but does not use one shared allocation.
- The source also resolves the overallocation caveat: only the dedicated-image allocator applies `overallocationFactor`; registered overallocated buffer leaves run the ordinary dedicated-buffer allocation size.
- No shader risk remains because the implementation uses transfer commands and host comparison without shader modules or pipelines.

## Conversion Notes for Final Wiki Rewrite

- Keep resource binding, aliasing, priority, and per-bind status as compact prerequisites.
- Carry the five test-family behavior values into `## Behavior Parameters`.
- Copy the Failure Cause Mapping table unchanged.
- Preserve the `suballocated` and buffer-overallocation caveats in parameter or pruning discussion rather than hiding implementation behavior behind registered names.
- State explicitly that shader analysis does not apply.
- Move detailed helper links to the source appendix.
