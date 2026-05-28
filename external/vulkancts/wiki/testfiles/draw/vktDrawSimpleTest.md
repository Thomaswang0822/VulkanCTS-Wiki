# vktDrawSimpleTest.cpp

## Overview

Basic draw tests that validate `vkCmdDraw` rendering of simple triangle primitives using triangle_list and triangle_strip topologies, both with single-instance and multi-instance draws. Tests render a blue rectangle on a black background and compare against a manually constructed reference image.

## Role

This file provides the `simple_draw` test group, which serves as a fundamental smoke test for the draw pipeline. It validates that vertex fetch, primitive assembly, and rasterization produce correct output for the most common draw scenarios (non-indexed, non-indirect draws with triangle topologies).

## Source Code

- [vktDrawSimpleTest.cpp](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp)

## Registration Hierarchy

```text
draw.renderpass.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip
```

## Test Families

### simple_draw_triangle_list — Single-instance triangle list draw

Renders two triangles forming a blue rectangle using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` with 6 vertices starting at vertex index 2. The `SimpleDraw` class issues `vkCmdDraw(cmdBuffer, 6, 1, 2, 0)`. Uses shaders `VertexFetch.vert` and `VertexFetch.frag`.

### simple_draw_triangle_strip — Single-instance triangle strip draw

Renders two triangles forming a blue rectangle using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` with 4 vertices starting at vertex index 2. The `SimpleDraw` class issues `vkCmdDraw(cmdBuffer, 4, 1, 2, 0)`. Uses shaders `VertexFetch.vert` and `VertexFetch.frag`.

### simple_draw_instanced_triangle_list — Instanced triangle list draw

Renders instanced triangles using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` with `instanceCount=4` and `firstInstance=2`. The `SimpleDrawInstanced` class issues `vkCmdDraw(cmdBuffer, 6, 4, 2, 2)`. Uses shader `VertexFetchInstancedFirstInstance.vert` to validate instanced vertex fetch with a non-zero `firstInstance`.

### simple_draw_instanced_triangle_strip — Instanced triangle strip draw

Renders instanced triangles using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` with `instanceCount=4` and `firstInstance=2`. The `SimpleDrawInstanced` class issues `vkCmdDraw(cmdBuffer, 4, 4, 2, 2)`. Uses shader `VertexFetchInstancedFirstInstance.vert`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Topology | triangle_list, triangle_strip | Primitive topology for the draw call |
| Instancing | non-instanced, instanced (4 instances, firstInstance=2) | Whether to test instanced draw with non-zero firstInstance |
| Rendering variant | renderpass, dynamic_rendering, secondary_cmd_buffer | Controlled by `SharedGroupParams` (not nested variants only) |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| `VK_KHR_dynamic_rendering` | When `groupParams.useDynamicRendering` is true |

## Verification Methods

All test cases use **fuzzy image comparison**:

1. A reference image is constructed manually by iterating over pixel coordinates and setting pixels within a reference rectangle to blue (0, 0, 1, 1) on a black background
2. For non-instanced tests, `ReferenceImageCoordinates` defines the expected rectangle bounds
3. For instanced tests, `ReferenceImageInstancedCoordinates` defines the expected rectangle bounds
4. The Vulkan-rendered image is read back from the color attachment
5. Comparison is performed using `tcu::fuzzyCompare` with threshold 0.05

The non-instanced validation is in [SimpleDraw::iterate](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L123-L239) and the instanced validation is in [SimpleDrawInstanced::iterate](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L273-L391).

## Notes

- The `SimpleDraw` class inherits from `DrawTestsBaseClass` and overrides the `draw()` method to issue `vkCmdDraw` with topology-specific vertex counts.
- The `SimpleDrawInstanced` class inherits from `SimpleDraw` and overrides `iterate()` to draw with `instanceCount=4` and `firstInstance=2`.
- Vertex data includes two degenerate vertices (clipped to screen edges) at indices 0-1, the visible geometry at indices 2+, and a final degenerate vertex. This pattern ensures that `firstVertex` offset handling is tested.
- The `checkSupport` function (line 393) only checks for `VK_KHR_dynamic_rendering` when dynamic rendering is enabled.
