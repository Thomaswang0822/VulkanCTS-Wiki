## Overview

**Core question:** Do indirect draws consume the intended command records, count limit, index-buffer location, and instance values, including after device-side command generation?

- The `indirect_draw` test family covers non-indexed and indexed indirect draws, ordinary and count-limited execution, first-instance and instanced variants, multiview, compute-restored command data, index-buffer offsets, and count clamping.
- `vktDrawIndirectTest.cpp` implements this family below the render-pass path and the applicable non-nested dynamic-rendering paths.
- Every executable case ultimately uses an image comparison, so the registered path identifies the mechanism under test while a failed image does not by itself localize the faulty pipeline stage.

## Background Knowledge

For the shared concepts draw parameters, rendering paths, and image-reference oracles, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- `VkDrawIndirectCommand` and `VkDrawIndexedIndirectCommand` place draw parameters in a buffer for the device to read when an indirect draw executes.
- In a count-buffer command, the device reads a `uint32_t` count and executes the lesser of that value and the command's `maxDrawCount` argument.
- The indirect offset selects the first record and the stride selects successive records. Implementations cannot assume records start at buffer offset zero or are tightly packed.
- A compute-shader write to command or count data must be made visible to the later indirect-command read before the draw executes.

## Registration Hierarchy

```text
draw.renderpass.indirect_draw
├── sequential
├── sequential_data_from_compute
├── indexed
├── indexed_bind_offset_16
├── indexed_alloc_offset_16
├── indexed_bind_offset_16_alloc_offset_16
├── indexed_data_from_compute
├── indexed_data_from_compute_bind_offset_16
├── indexed_data_from_compute_alloc_offset_16
├── indexed_data_from_compute_bind_offset_16_alloc_offset_16
└── indexed_draw_count_clamping
```

The Vulkan dispatcher also registers this test family below `dynamic_rendering.primary_cmd_buff`, `dynamic_rendering.partial_secondary_cmd_buff`, and `dynamic_rendering.complete_secondary_cmd_buff`; nested-secondary modes omit it. Primary-command-buffer registration includes host-written and compute-restored data. To reduce the secondary-command-buffer matrix, partial-secondary registration keeps the compute-restored variants while complete-secondary registration keeps the host-written variants. The rendering path does not change the deeper mechanism-group and leaf names ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100), [matrix reduction](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1877-L1924)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Draw type and index-buffer location | `sequential`; `indexed` with no suffix, `_bind_offset_16`, `_alloc_offset_16`, or both | Selects non-indexed or indexed records and, for indexed draws, changes the index-buffer bind and memory-allocation offsets. | [`init`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1877-L1924) |
| Data producer | host-written with no suffix; `_data_from_compute` | Selects records consumed after the host upload or after `NegateData.comp` restores bitwise-negated bytes. | [`init`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1877-L1942) |
| Execution mechanism | `indirect_draw`, `indirect_draw_count`, `indirect_draw_param_count`, their `_first_instance` and `_instanced` forms, and `indirect_draw_multiview` | Selects ordinary execution, which operand limits a count command, instance addressing, or two-view rendering. | [`mechanism groups`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1925-L2052), [`instance groups`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L2055-L2321) |
| Topology and command grouping | `triangle_list`, `triangle_list_multi_draw`, `triangle_strip`; selected compute/indexed render-pass paths also add `triangle_strip_memory_access` | Changes primitive assembly, whether one call consumes two records, and, for the memory-access leaf, the synchronization access masks. | [`leaf registration`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1944-L2027) |
| Instanced child | `no_first_instance`, `first_instance` | Selects `firstInstance` 0 or 2 for a four-instance indirect command. | [`instanced registration`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L2114-L2317) |
| Rendering path | `renderpass`, `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Changes render-pass versus dynamic-rendering setup and which command buffer records the draw. | [`dispatcher`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |
| Count-clamping leaf | `indexed_draw_count_clamping.triangle_list`, `indexed_draw_count_clamping.triangle_list_multi_draw` | Supplies a count of 4096 while passing `maxDrawCount = 4`, making failure to honor the API limit visible. | [`clamping registration`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L2327-L2349) |

## Behavior Parameters

The primary behavioral axis is the registered execution mechanism. Draw type, data producer, offsets, topology, and rendering path are cross-cutting dimensions of those mechanisms.

### `indirect_draw`

Ordinary cases use `vkCmdDrawIndirect` or `vkCmdDrawIndexedIndirect`. A multi-draw leaf consumes two records in one call using the supplied stride; the other leaves issue two one-record commands at separately calculated offsets.

### `indirect_draw_count` and `indirect_draw_param_count`

Both groups call `vkCmdDrawIndirectCount` or `vkCmdDrawIndexedIndirectCount`; they differ in which operand is intended to bind. In `indirect_draw_count`, the count-buffer value is lower than `maxDrawCount`. In `indirect_draw_param_count`, the count-buffer value is deliberately higher and the `maxDrawCount` argument is lower. The pair therefore checks both sides of the specification's `min(countBufferValue, maxDrawCount)` rule ([command issue](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L591-L667), [count values](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L922-L953)).

### First-instance mechanism groups

`indirect_draw_first_instance`, `indirect_draw_count_first_instance`, and `indirect_draw_param_count_first_instance` use a nonzero `firstInstance` and a vertex shader that checks `gl_InstanceIndex`. These cases require `drawIndirectFirstInstance`.

### Instanced mechanism groups

`indirect_draw_instanced`, `indirect_draw_count_instanced`, and `indirect_draw_param_count_instanced` each contain `no_first_instance` and `first_instance`. Their indirect records request four instances; the vertex shader uses the absolute instance index to place each copy, so a wrong count or base instance changes the reference image.

### `indirect_draw_multiview`

This group uses the count-buffer mechanism with a two-bit view mask and a two-layer color target. The current host oracle reads and compares array layer 0 only, so these cases exercise multiview draw setup but do not independently validate the rendered contents of layer 1 ([registration](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L2031-L2046), [readback call](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1061-L1069)).

### `indexed_draw_count_clamping`

The count buffer contains 4096 and the command passes `maxDrawCount = 4`. The first four records render the expected blue outer and green inner regions. This checks that the implementation executes `min(countBufferValue, maxDrawCount)` rather than using the oversized count-buffer value ([draw command](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1607-L1631), [count and reference](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1704-L1714)).

## Shader Analysis

- `VertexFetch.vert` compares `gl_VertexIndex` with a reference index carried in the vertex data. It emits the intended vertex color on equality and red on a mismatch, making incorrect `firstVertex`, `firstIndex`, or `vertexOffset` handling visible.
- `VertexFetchInstanceIndex.vert` performs the analogous check for `gl_InstanceIndex`. The instanced vertex programs additionally translate each instance according to its absolute instance index, exposing incorrect `instanceCount` or `firstInstance` handling.
- `VertexFetch.frag` writes the interpolated vertex color without adding another test-specific decision.
- In `_data_from_compute` cases, `NegateData.comp` bitwise-negates every `uint` in its bound storage buffer. Because the host initially stores the bitwise inverse of the intended bytes, one dispatch restores the command buffer and a second dispatch restores the count buffer when present ([compute setup](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L427-L500)).

## Runtime Execution and Result Checking

- The host packs command records after a 4096-byte junk prefix and inserts one junk structure between usable records. The draw therefore has to honor both the command offset and a stride twice the record size ([packing](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L676-L953)).
- Indexed cases bind an index buffer and apply the selected 16-byte bind and allocation offsets. Host-written cases consume flushed data directly. Compute-restored cases first dispatch `NegateData.comp`, then use a compute-shader-to-draw-indirect barrier for command data and count data before drawing ([index-buffer setup](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L530-L553), [compute barriers](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L470-L499)).
- The selected render-pass or dynamic-rendering path records the draw in a primary or secondary command buffer, submits it, waits for completion, and reads the color attachment back to the host ([recording and submission](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L956-L1033)).
- Ordinary and instanced paths build a blue software reference image. The clamping path builds a blue outer region with a green inner region. All paths call `tcu::fuzzyCompare` with threshold `0.05`; any mismatch fails the case ([ordinary comparison](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1034-L1074), [instanced comparison](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1451-L1494), [clamping comparison](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1788-L1835)).
- The image is an end-to-end oracle. The exact registered path narrows likely causes, but the comparison does not separately identify command fetch, synchronization, shader execution, rasterization, attachment handling, or readback as the failing stage.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `indirect_draw` | Indirect record addressing, stride, field interpretation, or vertex/index fetch. |
| `indirect_draw_count` | Count-buffer addressing or failure to use the count-buffer value as the lower limit. |
| `indirect_draw_param_count` | Failure to use `maxDrawCount` as the lower limit. |
| `indirect_draw_first_instance`, `indirect_draw_count_first_instance`, `indirect_draw_param_count_first_instance` | Nonzero `firstInstance` interpretation or `gl_InstanceIndex` handling. |
| `indirect_draw_instanced`, `indirect_draw_count_instanced`, `indirect_draw_param_count_instanced` | Instance count, absolute instance index, or instance-dependent placement. |
| `indirect_draw_multiview` | Indirect/count execution or multiview rendering in array layer 0; layer 1 is not checked by the current oracle. |
| `indexed_draw_count_clamping` | Failure to limit execution to `maxDrawCount = 4`. |

A failure isolated to a `_data_from_compute` direct child additionally points toward compute writes or compute-to-indirect visibility. A failure isolated to an indexed offset suffix points toward index-buffer address arithmetic.

### Cause Analysis

#### Indirect record and index interpretation

**Possible failure symptoms:** Geometry is missing, red appears where blue is expected, or one topology or indexed-offset suffix fails while nearby cases pass.

**Possible implementation causes:** The implementation may apply the wrong indirect offset or stride, decode a command field incorrectly, or combine `firstIndex`, `vertexOffset`, and the index-buffer bind address incorrectly.

#### Count limiting and clamping

**Possible failure symptoms:** A count case renders too few or too many primitives; the clamping case differs from its expected blue outer and green inner regions.

**Possible implementation causes:** The implementation may read the wrong count-buffer address or fail to execute exactly `min(countBufferValue, maxDrawCount)` as required by the indirect-count command semantics.

#### Compute producer visibility

**Possible failure symptoms:** A `_data_from_compute` case fails while the corresponding host-written case passes, often producing geometry consistent with stale or still-negated records.

**Possible implementation causes:** The implementation may not make compute shader storage writes available and visible to indirect-command reads according to the recorded compute-to-draw-indirect dependency.

#### Instance and multiview interpretation

**Possible failure symptoms:** First-instance or instanced cases produce red vertices or misplaced copies; a multiview case differs from the reference in the first array layer.

**Possible implementation causes:** The implementation may derive `gl_InstanceIndex` from the wrong base instance, execute the wrong number of instances, or mishandle the active multiview view mask. Because the current multiview oracle reads only layer 0, a defect confined to layer 1 cannot cause this test to fail.

## Case Pruning

### Requirement-based pruning

- Count-mechanism and clamping cases are skipped unless `VK_KHR_draw_indirect_count` is available.
- Multi-draw leaves require `multiDrawIndirect` and `maxDrawIndirectCount >= 2`.
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`, two-view cases require the `multiview` feature, and nonzero-first-instance cases require `drawIndirectFirstInstance` ([`checkSupport`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1838-L1866)).
- Vulkan SC excludes the dynamic-rendering dispatcher branches at build time; its mustpass scope therefore contains the render-pass path only.

### Design-based pruning

- Nonzero index bind and allocation offsets are generated only for indexed direct children.
- Secondary-command-buffer modes deliberately split the producer matrix: partial-secondary keeps compute-restored data and complete-secondary keeps host-written data.
- `triangle_strip_memory_access` is generated only for indexed, compute-restored, render-pass cases without a secondary command buffer because the source intentionally samples the broader memory-access masks once.
- The multiview mechanism has triangle-list leaves only, first-instance mechanisms omit multi-draw leaves, and count clamping is restricted to indexed triangle-list and triangle-list-multi-draw leaves. These exclusions define the test matrix rather than unsupported Vulkan behavior.

## Key Takeaways

- The family tests indirect record interpretation across non-indexed, indexed, count-limited, first-instance, instanced, multiview, and compute-restored paths.
- Junk prefixes, padded strides, index-buffer offsets, and deliberately competing count limits turn address and record-boundary mistakes into image differences.
- `indirect_draw_count` and `indirect_draw_param_count` use the same count commands but arrange opposite operands as the limiting value.
- Count clamping is specifically the `min(4096, maxDrawCount)` rule with `maxDrawCount = 4`.
- The oracle is end to end, and the current multiview cases compare only array layer 0.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration and matrix generation | [`IndirectDrawTests::init`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1877-L2351) | Defines exact direct children, mechanism groups, leaves, and design exclusions. |
| Draw command selection | [`IndirectDraw::draw`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L581-L674) | Selects ordinary versus count commands, one-record versus multi-draw issue, offsets, stride, and count limits. |
| Ordinary execution and oracle | [`IndirectDraw::iterate`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L676-L1075) | Packs buffers, records work, submits, reads back, and compares ordinary cases. |
| Instanced execution and oracle | [`IndirectDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1095-L1495) | Defines four-instance records, absolute instance values, and the instanced reference. |
| Count-clamping execution and oracle | [`IndirectDrawCountClampTest`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1497-L1836) | Defines count 4096, `maxDrawCount = 4`, sentinel records, and the blue/green reference. |
| Support gates | [`checkSupport`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1838-L1866) | Defines extension, feature, and limit requirements. |
| Draw-path dispatcher | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) | Defines render-pass, dynamic-rendering, and nested-secondary scope. |
| Graphics and compute shaders | [`VertexFetch.vert`](../../../data/vulkan/draw/VertexFetch.vert), [`VertexFetchInstanceIndex.vert`](../../../data/vulkan/draw/VertexFetchInstanceIndex.vert), [`VertexFetchInstanced.vert`](../../../data/vulkan/draw/VertexFetchInstanced.vert), [`VertexFetchInstancedFirstInstance.vert`](../../../data/vulkan/draw/VertexFetchInstancedFirstInstance.vert), [`VertexFetch.frag`](../../../data/vulkan/draw/VertexFetch.frag), [`NegateData.comp`](../../../data/vulkan/draw/NegateData.comp) | Establish built-in checks, instance placement, fragment output, and compute restoration. |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) | Defines indirect records, offset and stride rules, count-buffer reads, and `min(countBufferValue, maxDrawCount)`. |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines availability and visibility between compute writes and indirect reads. |
| Vulkan default mustpass scope | [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt) | Confirms render-pass and non-nested dynamic-rendering paths and exact identifiers for the default profile. |
| Vulkan SC mustpass scope | [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt) | Confirms exact render-pass identifiers for the Vulkan SC profile. |
