# vktBasicDrawTests.cpp

## Overview

Comprehensive draw command validation tests covering all four core Vulkan draw command types (`vkCmdDraw`, `vkCmdDrawIndexed`, `vkCmdDrawIndirect`, `vkCmdDrawIndexedIndirect`) across all primitive topologies. Tests generate random vertex and index data, render primitives, and compare results against a software reference renderer.

## Role

This file provides the `basic_draw` test group, which is one of the primary entry points for draw command conformance testing. It exercises each draw command type with varying primitive counts, topologies, and parameter offsets to validate correct rendering behavior. The tests also cover secondary command buffers, dynamic rendering, nested command buffers, and VK_KHR_maintenance5 buffer usage flags.

## Source Code

- [vktBasicDrawTests.cpp](../../../modules/vulkan/draw/vktBasicDrawTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.basic_draw
├── draw
├── draw_indexed
├── draw_indirect
├── draw_indexed_indirect
└── misc
```

## Test Families

### draw — vkCmdDraw validation

Tests `vkCmdDraw` across all primitive topologies (point_list through triangle_strip_with_adjacency). For each topology, sub-groups are created per primitive count (1, 3, 17, 45), generating random vertex data with a random `firstVertex` offset. The draw call parameters (`vertexCount`, `instanceCount`, `firstVertex`, `firstInstance`) are populated into [DrawParams](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L158-L172) and rendered via the templated [DrawTestInstance<DrawParams>](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L731-L744) specialization.

### draw_indexed — vkCmdDrawIndexed validation

Tests `vkCmdDrawIndexed` across all primitive topologies. For each topology and primitive count, generates random index data with random `firstIndex` and `vertexOffset` values. For simple list topologies (point_list, line_list, triangle_list) with more than one primitive, an additional `_multi_command` variant issues multiple `cmdDrawIndexed` calls per primitive. Parameters are stored in [DrawIndexedParams](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L200-L225) and rendered via [DrawTestInstance<DrawIndexedParams>](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1047-L1233).

### draw_indirect — vkCmdDrawIndirect validation

Tests `vkCmdDrawIndirect` across all primitive topologies. For each topology and primitive count, creates three variants:
- `_single_command`: one indirect command with `firstVertex=0`
- `_multi_command`: two indirect commands (second with random `firstVertex`)
- `_multi_command_multi_draw`: same commands but issued via a single `cmdDrawIndirect` call with `drawCount > 1`

Parameters are stored in [DrawIndirectParams](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L227-L255) and rendered via [DrawTestInstance<DrawIndirectParams>](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1295-L1433).

### draw_indexed_indirect — vkCmdDrawIndexedIndirect validation

Tests `vkCmdDrawIndexedIndirect` across all primitive topologies. Mirrors the `draw_indirect` structure with three variants (`_single_command`, `_multi_command`, `_multi_command_multi_draw`), but also includes random `firstIndex` and `vertexOffset` parameters. Parameters are stored in [DrawIndexedIndirectParams](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L257-L289) and rendered via [DrawTestInstance<DrawIndexedIndirectParams>](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1515-L1702).

### misc — Miscellaneous draw tests (VulkanSC-gated)

Contains tests that do not fit the standard topology-per-command pattern. Only present when `CTS_USES_VULKANSC` is not defined. Includes:
- `maintenance5`: Tests `vkCmdDrawIndexedIndirect` with VK_KHR_maintenance5 buffer usage flags (using `VkBufferUsageFlags2CreateInfoKHR` with `VK_BUFFER_USAGE_2_*_BIT_KHR` and `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`)
- `flat_b_sat_error`: Amber test for a specific flat shading saturation error

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Draw command type | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect` | Vulkan draw command under test |
| Primitive topology | point_list, line_list, line_strip, triangle_list, triangle_strip, triangle_fan, line_list_with_adjacency, line_strip_with_adjacency, triangle_list_with_adjacency, triangle_strip_with_adjacency | All topologies except patch_list |
| Primitive count | 1, 3, 17, 45 | Number of primitives to draw (reduced to 1 and 45 for dynamic rendering variants) |
| firstVertex / firstIndex / vertexOffset | Random (seeded) | Randomized offsets for draw parameters |
| Indirect command count | single, multi, multi_draw | Number of indirect commands and whether they use multi-draw |
| multipleDraws (indexed) | false, true | Whether to issue multiple `cmdDrawIndexed` calls per primitive (simple list topologies only) |
| useMaintenance5 | false, true | Whether to use VK_KHR_maintenance5 `VkBufferUsageFlags2CreateInfoKHR` for buffer creation |
| Rendering variant | renderpass, dynamic_rendering, secondary_cmd_buffer, nested_secondary_cmd_buffer | Controlled by `SharedGroupParams` |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| `VK_KHR_dynamic_rendering` | When `groupParams.useDynamicRendering` is true |
| `VK_KHR_maintenance5` | When `useMaintenance5` is true |
| `VK_EXT_nested_command_buffer` | When `groupParams.nestedSecondaryCmdBuffer` is true; also requires `nestedCommandBuffer` and `nestedCommandBufferRendering` features |
| `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` | When topology uses adjacency (line_list_with_adjacency, line_strip_with_adjacency, triangle_list_with_adjacency, triangle_strip_with_adjacency) |
| `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` | When `multiDraw` is true and more than one indirect command is used |
| `VK_KHR_portability_subset` triangleFans | When topology is `triangle_fan` and portability subset is supported; requires `triangleFans` feature |

## Verification Methods

All test families use **image comparison** against a software reference renderer:

1. A reference image is generated using the `rr::Renderer` software rasterizer with `PassthruVertShader` and `PassthruFragShader` (see [generateRefImage](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L708-L729))
2. The Vulkan-rendered image is read back from the color attachment
3. For point_list topology: `tcu::intThresholdPositionDeviationCompare` with color threshold 4, position deviation tolerance (1,1,0)
4. For all other topologies: `tcu::fuzzyCompare` with threshold 0.053

The comparison is performed in [imageCompare](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L349-L363).

## Notes

- The `populateSubGroup` function (line 1725) generates test cases per primitive count, with randomized offsets seeded by `SEED ^ deStringHash(groupName)`.
- For dynamic rendering variants, only primitive counts 1 and 45 are used to reduce test count.
- For secondary command buffer variants, only even-indexed topologies are tested to reduce test count.
- For nested secondary command buffer variants, only `DRAW_COMMAND_TYPE_DRAW` is tested.
- The `misc` group is gated by `#ifndef CTS_USES_VULKANSC` and only appears in non-VulkanSC builds.
- When `useMaintenance5` is true, buffer creation uses `VkBufferUsageFlags2CreateInfoKHR` with the correct `VK_BUFFER_USAGE_2_*_BIT_KHR` flag while setting the legacy `usage` field to `0xBAD00000`, and the pipeline is created with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR` combined with `VkPipelineCreateFlags2CreateInfoKHR`.
