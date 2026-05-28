# Indirect Draw Tests

## Overview

Tests for Vulkan indirect drawing commands (`vkCmdDrawIndirect`, `vkCmdDrawIndexedIndirect`, `vkCmdDrawIndirectCount`, `vkCmdDrawIndexedIndirectCount`), verifying correct rendering when draw parameters are sourced from GPU buffers rather than direct API arguments. The tests cover sequential and indexed draw types, instanced indirect draws, the `VK_KHR_draw_indirect_count` extension, multi-draw indirect, `drawIndirectFirstInstance` feature, compute-shader-generated indirect data, and index buffer offset variants.

## Role

Validates that indirect draw commands correctly read vertex count, instance count, first vertex, first instance, and index-related parameters from buffer memory. Ensures that junk data placed between draw command structures (stride padding) does not affect rendering. Verifies that the `VK_KHR_draw_indirect_count` extension properly limits the number of draws via both buffer-count and parameter-count mechanisms. Tests that compute shaders can generate indirect draw data with correct memory barriers. Confirms that indexed indirect draws with non-zero `cmdBindIndexBuffer` offsets and non-zero allocation offsets work correctly. Exercises the `drawIndirectFirstInstance` feature for both non-instanced and instanced indirect draws.

## Source Code

- [vktDrawIndirectTest.cpp](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp)

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

## Test Families

### sequential — Sequential (non-indexed) indirect draw tests

Contains sub-groups for basic indirect draw, indirect draw count (buffer-limited), indirect draw param count, indirect draw multiview, indirect draw first instance, indirect draw count first instance, indirect draw param count first instance, and instanced variants with nested `no_first_instance` / `first_instance` sub-groups. Leaf test cases cover `triangle_list`, `triangle_list_multi_draw`, `triangle_strip`, and optionally `triangle_strip_memory_access` topologies. Uses `IndirectDraw` and `IndirectDrawInstanced` test classes with `DRAW_TYPE_SEQUENTIAL`.

### sequential_data_from_compute — Sequential indirect draw with compute-generated data

Same structure as `sequential` but with `dataFromCompute` enabled. Indirect buffer contents are bitwise-negated and a compute shader restores them before the draw. Tests correct memory barrier usage between compute write and indirect read. Includes `triangle_strip_memory_access` variants that use `VK_ACCESS_MEMORY_WRITE_BIT`/`VK_ACCESS_MEMORY_READ_BIT` instead of stage-specific access flags.

### indexed — Indexed indirect draw tests

Contains the same sub-group structure as `sequential` but uses `DRAW_TYPE_INDEXED`. The vertex buffer includes a `VERTEX_OFFSET` prefix of junk vertices, and an index buffer is bound. Leaf tests exercise `triangle_list`, `triangle_list_multi_draw`, and `triangle_strip` topologies with index-based vertex fetching.

### indexed_bind_offset_16 — Indexed indirect draw with non-zero bind offset

Same as `indexed` but with `bindIndexBufferOffset = sizeof(uint32_t) * 4 = 16`. Tests that `vkCmdBindIndexBuffer` with a non-zero offset works correctly with indirect indexed draws.

### indexed_alloc_offset_16 — Indexed indirect draw with non-zero allocation offset

Same as `indexed` but with `indexBufferAllocOffset = sizeof(tcu::Vec4) = 16`. Tests that index buffer memory allocation with a non-zero starting offset works correctly.

### indexed_bind_offset_16_alloc_offset_16 — Indexed indirect draw with both bind and allocation offsets

Combines both `bindIndexBufferOffset = 16` and `indexBufferAllocOffset = 16`. Tests the interaction of both offset types simultaneously.

### indexed_data_from_compute — Indexed indirect draw with compute-generated data

Same as `indexed` but with `dataFromCompute` enabled. Indirect and count buffer data is negated and restored by a compute shader before the draw.

### indexed_data_from_compute_bind_offset_16 — Indexed compute-data draw with bind offset

Combines `indexed_data_from_compute` with `bindIndexBufferOffset = 16`.

### indexed_data_from_compute_alloc_offset_16 — Indexed compute-data draw with allocation offset

Combines `indexed_data_from_compute` with `indexBufferAllocOffset = 16`.

### indexed_data_from_compute_bind_offset_16_alloc_offset_16 — Indexed compute-data draw with both offsets

Combines `indexed_data_from_compute` with both `bindIndexBufferOffset = 16` and `indexBufferAllocOffset = 16`.

### indexed_draw_count_clamping — Count clamping with out-of-bounds draw count

Uses `IndirectDrawCountClampTest` class with `IndirectCountType::BUFFER_LIMIT` and a very large count buffer value (`kOOBDrawCount = 4096`). Verifies that the implementation correctly clamps the draw count to the actual number of valid commands in the indirect buffer. Contains `triangle_list` and `triangle_list_multi_draw` leaf tests.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Draw type | `DRAW_TYPE_SEQUENTIAL`, `DRAW_TYPE_INDEXED` | Whether the indirect draw uses indexed or sequential vertex fetch |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Primitive topology used for rendering |
| Indirect count type | `NONE`, `BUFFER_LIMIT`, `PARAM_LIMIT` | Whether and how `VK_KHR_draw_indirect_count` is used: none, buffer-limited count, or parameter-limited count |
| Multi-draw | false, true | Whether `vkCmdDrawIndirect`/`vkCmdDrawIndexedIndirect` is called with drawCount > 1 |
| First instance | not tested, tested (firstInstance = 0), tested (firstInstance > 0) | Whether `firstInstance` is tested, and whether non-zero values are used |
| Instanced | false, true | Whether the draw uses instancing (instanceCount > 1) |
| Data from compute | false, true | Whether indirect buffer data is generated by a compute shader |
| Memory access flags | stage-specific, `VK_ACCESS_MEMORY_WRITE/READ_BIT` | Barrier access flags used when compute generates data |
| Multiview | 1 layer, 2 layers | Number of rendering layers (multiview when > 1) |
| Bind index buffer offset | 0, 16 | Offset passed to `vkCmdBindIndexBuffer` |
| Index buffer allocation offset | 0, 16 | Offset applied to index buffer memory allocation |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_KHR_draw_indirect_count` | When `testIndirectCountExt != NONE` | [vktDrawIndirectTest.cpp#L1840-L1841](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1840-L1841) |
| `multiDrawIndirect` feature | When multi-draw is enabled | [vktDrawIndirectTest.cpp#L1843-L1845](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1843-L1845) |
| `maxDrawIndirectCount >= 2` limit | When multi-draw is enabled | [vktDrawIndirectTest.cpp#L1847-L1849](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1847-L1849) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawIndirectTest.cpp#L1852-L1853](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1852-L1853) |
| `multiview` feature | When `layerCount > 1` | [vktDrawIndirectTest.cpp#L1855-L1859](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1855-L1859) |
| `drawIndirectFirstInstance` feature | When `requireIndirectFirstInstance` is true | [vktDrawIndirectTest.cpp#L1862-L1865](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1862-L1865) |

## Verification Methods

- **Fuzzy image comparison against software reference**: A reference image is generated by computing expected pixel coordinates based on `ReferenceImageCoordinates` or `ReferenceImageInstancedCoordinates` structs. The rendered output is compared using `tcu::fuzzyCompare` with a threshold of 0.05 at [vktDrawIndirectTest.cpp#L1068-L1072](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1068-L1072) for non-instanced and [vktDrawIndirectTest.cpp#L1488-L1492](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1488-L1492) for instanced draws.
- **Count clamping verification**: The `IndirectDrawCountClampTest` at [vktDrawIndirectTest.cpp#L1497-L1508](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1497-L1508) uses an oversized count buffer value (`kOOBDrawCount = 4096`) and verifies that only the valid draws are executed by comparing against a reference with outer and inner quad regions at [vktDrawIndirectTest.cpp#L1799-L1820](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1799-L1820).

## Notes

- The indirect buffer is prefixed with 1024 uint32 junk values (`JunkData` struct at [vktDrawIndirectTest.cpp#L66-L75](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L66-L75)) to ensure the implementation reads from the correct offset.
- Stride between draw commands is set to `2 * sizeof(VkDrawIndirectCommand)` (or indexed variant), with junk data placed in the stride gap at [vktDrawIndirectTest.cpp#L783](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L783).
- The `IndirectDrawInstanced` template class at [vktDrawIndirectTest.cpp#L230-L236](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L230-L236) is parameterized on `FirstInstanceSupport` to control whether `firstInstance` is set to 0 or 2, enabling the same test structure to cover both the supported and unsupported cases.
- The `MultiDrawScopedSetter` RAII class at [vktDrawIndirectTest.cpp#L145-L162](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L145-L162) temporarily enables multi-draw mode for selected test cases within a group.
- Compute-shader data generation uses a `NegateData.comp` shader that bitwise-negates buffer contents, with appropriate pipeline barriers between compute write and indirect read at [vktDrawIndirectTest.cpp#L429-L500](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L429-L500).
- The `triangle_strip_memory_access` variant is only added for specific combinations: when `dataFromCompute` is true, `drawType` is indexed, and neither dynamic rendering nor secondary command buffers are used, at [vktDrawIndirectTest.cpp#L1964-L1973](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1964-L1973).
- Test count is reduced for dynamic rendering with secondary command buffers by skipping certain combinations at [vktDrawIndirectTest.cpp#L1896-L1898](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1896-L1898).
