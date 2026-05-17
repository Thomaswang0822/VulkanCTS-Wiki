# [vktDrawNonLineTests.cpp](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L1)

## Overview

Tests that line drawing parameters (line rasterization mode and stippling) do not affect the rendering of non-line primitives. This file (~679 lines) renders the same scene twice -- once without line rasterization parameters and once with them -- and verifies that both renderings produce identical results. This validates that `VkPipelineRasterizationLineStateCreateInfoKHR` settings are properly ignored for non-line output primitives.

## Role of File

Implementation-heavy test file for the `non_line_with_params` subgroup. Contains the `NonLineDrawCase` test case class, the `NonLineDrawInstance` test instance class, and the test registration loop over vertex topology, geometry output, polygon mode, and line rasterization mode combinations.

## Source Code

- Primary source: [vktDrawNonLineTests.cpp](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L1)
- Header: [vktDrawNonLineTests.hpp](../../../modules/vulkan/draw/vktDrawNonLineTests.hpp#L1)
- Parent-category registration: [createChildren()](../../../modules/vulkan/draw/vktDrawTests.cpp#L70)

## Registration Hierarchy

```text
draw.renderpass.non_line_with_params
├── vtx_triangles...
├── vtx_lines...
└── vtx_points...
```

The `non_line_with_params` group is registered by [`createDrawNonLineTests()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L595) and appears only under the `draw.renderpass` variant branch. It is gated by `!CTS_USES_VULKANSC` and `!useDynamicRendering` at registration in [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L106-L117). The leaf test case names combine vertex topology, geometry output suffix, polygon mode suffix, and line rasterization mode suffix (e.g., `vtx_triangles_mode_fill_line_raster_rect`).

Evidence:
- `non_line_with_params` group added at [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L116)
- Leaf test cases added from [`vktDrawNonLineTests.cpp`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L641) through [`vktDrawNonLineTests.cpp`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L673)

## Test Families

### vtx_triangles — Triangle vertex topology with non-line parameters

Leaf test cases with `VertexTopology::TRIANGLES` as the input primitive topology. These test that line rasterization parameters do not affect triangle rendering, including when the geometry shader outputs non-line primitives or when polygon mode is `VK_POLYGON_MODE_POINT`. Cases where polygon mode is `VK_POLYGON_MODE_LINE` are skipped because they would produce line output, which could legitimately be affected by line rasterization parameters.

### vtx_lines — Line vertex topology with non-line parameters

Leaf test cases with `VertexTopology::LINES` as the input primitive topology. Only cases where a geometry shader transforms lines into non-line output (triangles or points) are included. Cases without a geometry shader (where lines would be rasterized directly) are skipped because line rasterization parameters would legitimately affect the output.

### vtx_points — Point vertex topology with non-line parameters

Leaf test cases with `VertexTopology::POINTS` as the input primitive topology. Points are never affected by line rasterization parameters, so all combinations of geometry output, polygon mode, and line rasterization mode are tested.

Implementation: The [`NonLineDrawInstance::iterate()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L379) method renders the same vertex data twice into separate color buffers using two pipelines. The first pipeline has no line rasterization state in its `pNext` chain; the second pipeline includes a `VkPipelineRasterizationLineStateCreateInfoKHR` struct with the specified line rasterization mode. Both results are compared for exact equality.

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Vertex topology | `TRIANGLES` (vtx_triangles), `LINES` (vtx_lines), `POINTS` (vtx_points) |
| Geometry output | `NONE` (no geometry shader), `TRIANGLES` (_geom_triangles), `LINES` (_geom_lines), `POINTS` (_geom_points) |
| Polygon mode | `VK_POLYGON_MODE_FILL` (_mode_fill), `VK_POLYGON_MODE_LINE` (_mode_line), `VK_POLYGON_MODE_POINT` (_mode_point) |
| Line rasterization mode | `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_KHR` (_line_raster_rect), `VK_LINE_RASTERIZATION_MODE_BRESENHAM_KHR` (_line_raster_bresenham), `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR` (_line_raster_smooth) |

## Support Requirements

- `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` when geometry shader is used (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L224))
- `DEVICE_CORE_FEATURE_SHADER_TESSELLATION_AND_GEOMETRY_POINT_SIZE` when geometry shader is used (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L255))
- Corresponding line rasterization feature depending on mode: `rectangularLines`, `bresenhamLines`, or `smoothLines` (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L229))
- `fillModeNonSolid` device feature when polygon mode is not `VK_POLYGON_MODE_FILL` (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L251))

## Verification Methods

- **Float threshold comparison**: [`tcu::floatThresholdCompare()`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L586) with zero threshold. The test compares the output of the first draw (without line parameters) against the second draw (with line parameters). Identical results confirm that line rasterization parameters have no effect on non-line primitives.

## Notes

- Renderpass-only and VK-only: gated by `!CTS_USES_VULKANSC` and `!useDynamicRendering` at [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L106-L116)
- Cases that produce line output are skipped: (1) `VertexTopology::LINES` without geometry shader, (2) `GeometryOutput::LINES`, (3) `VertexTopology::TRIANGLES` with `GeometryOutput::NONE` and `VK_POLYGON_MODE_LINE`, (4) `GeometryOutput::TRIANGLES` with `VK_POLYGON_MODE_LINE`. The skip logic uses `break` at [`vktDrawNonLineTests.cpp`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L659) which skips the entire inner loop (line rasterization mode cases) for line-producing combinations.
- The test uses a 32x32 framebuffer with random vertex positions generated per quadrant using a deterministic seed derived from the parameter combination
