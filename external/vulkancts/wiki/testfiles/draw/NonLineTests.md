## Overview

**Core question:** Does adding a selected line-rasterization mode leave every retained point or filled-triangle result unchanged?

This page covers the `non_line_with_params` test family registered under `draw.renderpass`. It compares rendering with no line-rasterization state against rendering with one selected line-rasterization mode, while keeping only cases whose effective output is a point or filled triangle. The goal is to prove that line-rasterization parameters are ignored for non-line primitives.

## Background Knowledge

- Line-rasterization state controls how line primitives are rasterized. It should not change point or filled-triangle output.
- Input topology and final rasterized primitive can differ: a geometry shader can emit points or triangles, and polygon mode can convert triangle output to points or lines.

## Registration Hierarchy

```text
draw.renderpass
└── non_line_with_params
```

`non_line_with_params` is added by `createDrawNonLineTests()` only when the draw test category is using the render-pass path and the build is not Vulkan SC. Its parent registration also excludes dynamic rendering. All executable leaves are direct children of this test family; the complete leaf inventory is summarized in the behavior and parameter sections below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Vertex topology | `vtx_triangles`, `vtx_lines`, `vtx_points` | Selects the input primitive assembled before optional geometry processing | [`vertexTopologyCases`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L600-L608) |
| Geometry output | no suffix, `_geom_triangles`, `_geom_lines`, `_geom_points` | Selects no geometry shader or the primitive emitted by the geometry shader | [`geometryOutputCases`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L610-L619) |
| Polygon mode | `_mode_fill`, `_mode_line`, `_mode_point` | Selects fill, line, or point rasterization for triangle output | [`polygonModeCases`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L621-L629) |
| Line rasterization mode | `_line_raster_rect`, `_line_raster_bresenham`, `_line_raster_smooth` | Selects the line state added to the second pipeline | [`lineRasterModeCases`](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L631-L639) |

The generated case name concatenates these suffixes, for example `vtx_triangles_geom_points_mode_fill_line_raster_bresenham`.

## Behavior Parameters

The primary behavioral axis is the line rasterization mode. Every retained case renders the same non-line scene twice and changes only whether the selected mode is present in the second pipeline.

### `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_KHR`: rectangular mode

The second pipeline carries rectangular line state. The output must remain byte-for-byte equivalent to the pipeline without that state whenever the effective primitive is a point or filled triangle.

### `VK_LINE_RASTERIZATION_MODE_BRESENHAM_KHR`: Bresenham mode

The second pipeline carries Bresenham line state. The same non-effect invariant is checked against the no-line-state reference draw.

### `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR`: smooth rectangular mode

The second pipeline carries smooth line state. It is compared using the same generated vertex data, shader modules, render targets, and exact threshold.

## Shader Analysis

The test generates a vertex shader and fragment shader for every case. A geometry shader is generated when the selected output is `TRIANGLES`, `LINES`, or `POINTS`; it emits the selected output primitive. For triangle output it either forwards triangle input or synthesizes the additional vertices needed from line or point input. Shader instructions are not the behavior under test: both pipelines use the same program artifacts, and the comparison isolates the effect of line-rasterization state. No representative shader walkthrough is included because the shader source is straightforward pass-through/generation logic and the tested property is fixed-function state scope.

## Runtime Execution and Result Checking

- The instance uses a 32x32 `VK_FORMAT_R8G8B8A8_UNORM` framebuffer and two color targets, one for each pipeline.
- A deterministic `de::Random` seed is derived from vertex topology, geometry output, and polygon mode; the line-rasterization mode is deliberately excluded so all three modes use identical generated input for a given non-line case.
- Four quadrants receive generated positions and per-primitive colors. The same host-visible vertex buffer is bound for both draws.
- The first pipeline omits line-rasterization state. The second pipeline includes `VkPipelineRasterizationLineStateCreateInfoKHR` with the selected mode.
- Both draws execute in separate render passes, then each color image is copied to a host-visible buffer and invalidated.
- `tcu::floatThresholdCompare()` compares the two images with a zero threshold. Equality returns `Pass`; any mismatch returns `Fail` with `Unexpected color in result buffer; check log for details`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_KHR` | Rectangular line state changes non-line rendering, or shared render/compare infrastructure differs |
| `VK_LINE_RASTERIZATION_MODE_BRESENHAM_KHR` | Bresenham line state changes non-line rendering, or shared render/compare infrastructure differs |
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR` | Smooth line state changes non-line rendering, or shared render/compare infrastructure differs |

### Cause Analysis

#### Line-rasterization state leaks into non-line rasterization

**Possible failure symptoms:** The second image differs from the no-line-state image for a retained point or filled-triangle case.

**Possible implementation causes:** The implementation may apply line-rasterization state outside line primitive rasterization, or pipeline compilation may incorrectly couple this state to non-line rasterization. The exact implementation location requires source-level investigation.

#### Rendering, copyback, or comparison mismatch

**Possible failure symptoms:** The two images differ despite identical input data and shader programs.

**Possible implementation causes:** Source-level investigation is needed to distinguish pipeline construction, render-pass execution, synchronization, image-to-buffer copyback, host invalidation, generated data, or comparison-path problems. A mismatch alone does not identify line state as the cause.

## Case Pruning

### Requirement-based pruning

- Cases requiring a geometry shader need `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` and `DEVICE_CORE_FEATURE_SHADER_TESSELLATION_AND_GEOMETRY_POINT_SIZE`.
- The selected line mode requires its corresponding `rectangularLines`, `bresenhamLines`, or `smoothLines` feature.
- Non-fill polygon modes require `fillModeNonSolid`.
- The test family is not registered for Vulkan SC or dynamic rendering because its parent registration excludes those paths.

### Design-based pruning

- Any `GeometryOutput::LINES` case is skipped because it intentionally rasterizes lines.
- Input `LINES` with no geometry shader is skipped for the same reason.
- Triangle output with `VK_POLYGON_MODE_LINE` is skipped, whether triangles are produced directly or by the geometry shader.
- The registration loop uses `break` for these combinations, skipping all line-rasterization mode leaves for that combination.

## Key Takeaways

- The invariant is about the final primitive being non-line, not simply the vertex input topology.
- Three line-rasterization modes are tested against a reference pipeline that omits the line state.
- Identical deterministic input and a zero-threshold image comparison make any retained pixel difference observable.
- Line-producing combinations are excluded so the test does not treat an expected line-rasterization effect as a failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `NonLineDrawCase::checkSupport()` | [feature checks](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L224-L256) | Per-case feature requirements |
| `NonLineDrawCase::initPrograms()` | [program generation](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L258-L372) | Vertex, fragment, and optional geometry shaders |
| `NonLineDrawInstance::iterate()` | [execution and comparison](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L379-L590) | Resource setup, two draws, copyback, and equality check |
| `createDrawNonLineTests()` | [registration and pruning](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L595-L675) | Exact dimensions, names, and skipped combinations |
| `createChildren()` | [parent registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Render-pass-only and build-variant placement |
| Factory declaration | [header](../../../modules/vulkan/draw/vktDrawNonLineTests.hpp#L22-L36) | Test-family entry point |
