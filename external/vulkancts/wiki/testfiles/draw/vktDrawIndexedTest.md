# vktDrawIndexedTest.cpp

## Overview

Tests for indexed draw commands (`vkCmdDrawIndexed`, `vkCmdDrawIndexedIndirect`, `vkCmdDrawIndexedIndirectCount`, `vkCmdDrawMultiIndexedEXT`) with various vertex offsets, index buffer bind offsets, memory allocation offsets, and VK_KHR_maintenance6 null descriptor scenarios. Also includes specialized tests for 8-bit index multibind patterns and index buffer update-before-draw scenarios.

## Role

This file provides the `indexed_draw` test group, which validates the full range of indexed drawing functionality. It covers basic indexed draws with vertex offsets and buffer offsets, instanced indexed draws, maintenance6 null descriptor and bindIndexBuffer2 scenarios, 8-bit index type multibind sequences, and index buffer updates via transfer operations before drawing.

## Source Code

- [vktDrawIndexedTest.cpp](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp)

## Registration Hierarchy

```text
draw.renderpass.indexed_draw
├── draw_indexed_*
├── draw_instanced_indexed_*
├── draw_indexed*_maintenance6
├── multibind_8bit_case_*
└── update_index_buffer_before_draw_*
```

## Test Families

### draw_indexed_* — Basic indexed draw tests

Tests `vkCmdDrawIndexed` with `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` and `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`. Test names are constructed dynamically from the combination of topology, vertex offset, index buffer bind offset, and memory allocation offset:

- **Vertex offset**: default (13), minus_one (-1), negative_large (-13)
- **Index bind offset**: default (0), positive (16)
- **Memory bind offset**: default (0), positive (16)
- **Maintenance5 suffix**: empty or `_maintenance5` (uses `cmdBindIndexBuffer2` when enabled)

Each test renders 6 indices (triangle_list) or 4 indices (triangle_strip) with the specified `vertexOffset`, and compares the result against a reference blue rectangle. The `DrawIndexed` class handles vertex data setup with offset padding and index buffer creation with bind offsets.

### draw_instanced_indexed_* — Instanced indexed draw tests

Tests `vkCmdDrawIndexed` with instancing (4 instances, firstInstance=2) using `DrawInstancedIndexed`, which inherits from `DrawIndexed`. Uses shader `VertexFetchInstancedFirstInstance.vert` and validates against `ReferenceImageInstancedCoordinates`. The same parameter combinations (topology, vertex offset, bind offset, alloc offset, maintenance5) apply as the non-instanced variant.

### draw_indexed*_maintenance6 — VK_KHR_maintenance6 indexed draw tests

Tests indexed drawing with null index buffer descriptors and `cmdBindIndexBuffer2`, exercising VK_KHR_maintenance6 behavior. Uses `DrawIndexedMaintenance6` with `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` and a 1x1 render target. Test name structure:

`draw_indexed[_count][_indirect|_indirect_count|_multi][_bindindexbuffer2][_nulldescriptor][_maintenance_5]_maintenance6`

Parameter combinations:
- **Draw type**: indexed, indexed_indirect, indexed_indirect_count, multi_indexed_ext (VK_EXT_multi_draw, VulkanSC-excluded)
- **bindIndexBuffer2**: false/true (uses `cmdBindIndexBuffer2` with `VK_NULL_HANDLE`)
- **nullDescriptor**: false/true (binds `VK_NULL_HANDLE` as index buffer, requires `VK_EXT_robustness2` nullDescriptor)
- **testDrawCount**: false/true (uses `VertexFetchCount.vert/frag` shaders with an SSBO counter; validates both image and counter value)

When `nullDescriptor` is true and `testDrawCount` is false, the reference image is generated using the `rr::Renderer` software rasterizer. When `testDrawCount` is true, the test validates the SSBO counter equals the `indexCount` value, and uses `tcu::intThresholdCompare` for image comparison.

### multibind_8bit_case_* — 8-bit index multibind tests

Tests multiple `vkCmdBindIndexBuffer` + `vkCmdDrawIndexed` sequences using `VK_INDEX_TYPE_UINT8`. Each test case divides a 16x16 framebuffer into 8 blocks of pseudorandom size, with each block using a separate index buffer. Variants include unsorted and sorted block sizes. 20 cases per variant are generated with different pseudorandom seeds. Uses `Multibind8BitCase`/`Multibind8BitInstance` classes. Only added when not using dynamic rendering or secondary command buffers.

### update_index_buffer_before_draw_* — Index buffer update before draw

Tests that updating an index buffer via a transfer operation (cmdCopyBuffer) after binding it but before drawing produces correct results. Uses `VK_INDEX_TYPE_UINT32`, `VK_INDEX_TYPE_UINT16`, and `VK_INDEX_TYPE_UINT8` index types. A staging buffer is copied to the device-local index buffer, followed by a pipeline barrier, then a render pass with `vkCmdDrawIndexed`. Uses `UpdateBeforeDrawCase`/`UpdateBeforeDrawInstance` classes. Only added when not using dynamic rendering or secondary command buffers.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Topology | triangle_list, triangle_strip | Primitive topology for standard indexed draws |
| Vertex offset | 13 (default), -1 (minus_one), -13 (negative_large) | `vertexOffset` parameter in `vkCmdDrawIndexed` |
| Index bind offset | 0 (default), 16 (positive) | Offset passed to `cmdBindIndexBuffer` / `cmdBindIndexBuffer2` |
| Memory bind offset | 0 (default), 16 (positive) | Extra allocation offset for index buffer memory |
| Maintenance5 | false, true | Whether to use `cmdBindIndexBuffer2` instead of `cmdBindIndexBuffer` |
| Maintenance6 draw type | indexed, indexed_indirect, indexed_indirect_count, multi_indexed_ext | Draw command variant for maintenance6 tests |
| nullDescriptor | false, true | Whether to bind VK_NULL_HANDLE as index buffer |
| testDrawCount | false, true | Whether to use SSBO-based draw count validation |
| 8-bit multibind case | 0-19, sorted/unsorted | Pseudorandom seed and sort mode for multibind tests |
| Update index type | uint32, uint16, uint8 | Index type for update-before-draw tests |
| Rendering variant | renderpass, dynamic_rendering, secondary_cmd_buffer | Controlled by `SharedGroupParams` (not nested variants only) |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| `VK_KHR_dynamic_rendering` | When `groupParams.useDynamicRendering` is true |
| `VK_KHR_maintenance6` | When `testType != TEST_TYPE_NON_MAINTENANCE_6` |
| `VK_EXT_robustness2` nullDescriptor feature | When `nullDescriptor` is true |
| `robustBufferAccess` | When `nullDescriptor` is true (asserted, not checked) |
| `VK_KHR_maintenance5` | When `bindIndexBuffer2` is true or `useMaintenance5Ext` is true |
| `VK_EXT_multi_draw` | When `testType == TEST_TYPE_MAINTENANCE6_MULTI_INDEXED_EXT` |
| `VK_KHR_draw_indirect_count` | When `testType == TEST_TYPE_MAINTENANCE6_INDEXED_INDIRECT_COUNT` |
| `fragmentStoresAndAtomics` | When `testDrawCount` is true |
| `indexTypeUint8` (VK_KHR_index_type_uint8) | For multibind 8-bit tests and update-before-draw with uint8 index type |
| `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` | Not required (no adjacency topologies used) |

## Verification Methods

Different verification methods are used depending on the test family:

1. **Standard indexed draws** (`DrawIndexed`, `DrawInstancedIndexed`): Fuzzy image comparison using `tcu::fuzzyCompare` with threshold 0.05 against a manually constructed reference blue rectangle.

2. **Maintenance6 draws with nullDescriptor and no testDrawCount**: Position-deviation comparison using `tcu::intThresholdPositionDeviationCompare` with color threshold (4,4,4,4) and position deviation (1,1,0). Reference image generated via `rr::Renderer` software rasterizer with `PassthruVertShader`/`PassthruFragShader`.

3. **Maintenance6 draws with testDrawCount**: Exact integer threshold comparison using `tcu::intThresholdCompare` with threshold (0,0,0,0), plus SSBO counter validation checking `ssboCounter == indexCount`.

4. **8-bit multibind tests**: Exact float threshold comparison using `tcu::floatThresholdCompare` with threshold (0,0,0,0) against a fully blue reference image.

5. **Update-before-draw tests**: Exact float threshold comparison using `tcu::floatThresholdCompare` with threshold (0,0,0,0) against a fully blue reference image.

## Notes

- The `init()` method calls `init(false)` and then `init(true)` (VulkanSC-gated) to generate tests both with and without the `_maintenance_5` suffix, doubling the standard indexed draw test count.
- The `maintenance6InstanceFactory` class (line 1622) is a custom `TestCase` subclass that provides `initDeviceCapabilities()` for capability pre-declaration and `getRequiredCapabilitiesId()` for capability grouping.
- For negative vertex offsets, indices are increased by `abs(offset)` so that subtracting the offset yields the correct vertex positions. For positive vertex offsets, padding vertices are inserted at the start of the vertex buffer.
- The multibind 8-bit and update-before-draw tests are only added when `!useDynamicRendering && !useSecondaryCmdBuffer && !useMaintenance5Ext`.
- The `cmdBindIndexBufferImpl` method (line 353) dispatches between `cmdBindIndexBuffer` and `cmdBindIndexBuffer2` based on `useMaintenance5Ext`.
