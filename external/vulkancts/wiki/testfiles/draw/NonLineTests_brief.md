## One-Sentence Test Purpose

This test checks that enabling each supported Vulkan line-rasterization mode leaves point and filled-triangle rendering unchanged.

## Background Knowledge

### Effective primitive versus input topology

The input assembly topology is not always the primitive that reaches rasterization. An optional geometry shader can emit points, lines, or triangles, and polygon mode can turn triangle output into points or lines. Line-rasterization state is relevant only when the final primitive is a line.

Why it matters here:
- The test includes line input that a geometry shader converts to non-line output.
- It removes every combination whose final output is a line, so a mismatch indicates a violation of the intended non-line invariant rather than an expected line-mode difference.

### Reference comparison

The test renders identical data twice. The reference pipeline omits `VkPipelineRasterizationLineStateCreateInfoKHR`; the second pipeline includes it with one selected mode. The images must match exactly, not merely within a visible tolerance.

## One Concrete Example

`vtx_points_geom_triangles_mode_fill_line_raster_smooth` starts with points, uses a geometry shader to emit triangles, keeps polygon mode at `VK_POLYGON_MODE_FILL`, and selects `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR`. Since the final output is filled triangles, adding the line state must not change the 32x32 color image.

## End-to-End Test Flow

```text
[host] choose topology, geometry output, polygon mode, and line mode
[host] check required device features
[host] generate deterministic positions and colors
[host] create the common shaders and two pipelines
[host] draw the same vertex buffer once without and once with line state
[device] rasterize the retained point or filled-triangle output
[host] copy both color images to host-visible buffers
[host] compare the images with zero threshold and return pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test constructs GLSL vertex and fragment shaders. It adds a geometry shader for geometry output other than `NONE`; that shader emits the selected output primitive. The two pipelines share these programs and differ only in the optional line-rasterization state.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read | no | Identical draw input |
| Two color images and buffers | yes | yes | images written; buffers copied | yes | Reference and result images |
| Render pass/framebuffers | yes | yes | used by draws | no | Separate comparable render targets |

## What Is Checked

The host compares the two copied color buffers as `tcu::ConstPixelBufferAccess` objects with `tcu::floatThresholdCompare()` and a zero threshold in all four channels. Equality passes; any mismatch fails.

## Behavior Parameter Identification

> **Behavior parameter:** line rasterization mode
>
> **Candidate values:** `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_KHR`, `VK_LINE_RASTERIZATION_MODE_BRESENHAM_KHR`, `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_KHR` | Line state changes non-line output, or shared rendering/comparison infrastructure differs |
| `VK_LINE_RASTERIZATION_MODE_BRESENHAM_KHR` | Line state changes non-line output, or shared rendering/comparison infrastructure differs |
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_KHR` | Line state changes non-line output, or shared rendering/comparison infrastructure differs |

## Important Variations and Special Cases

- `GeometryOutput::LINES`, direct line input, and triangle output with `VK_POLYGON_MODE_LINE` are design-pruned because they produce lines.
- Geometry cases require geometry-shader and geometry-point-size support; non-fill polygon modes require `fillModeNonSolid`.
- The family is registered only for the render-pass path, not dynamic rendering or Vulkan SC.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Feature checks | [checkSupport](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L224-L256) | Identifies requirements |
| Generated shaders | [initPrograms](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L258-L372) | Shows program variants |
| Render and compare | [iterate](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L379-L590) | Establishes the invariant and pass condition |
| Registration matrix | [createDrawNonLineTests](../../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L595-L675) | Defines names and pruning |
| Parent placement | [createChildren](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Establishes registration gates |

## Questions / Risk Points for User Audit

- Is the distinction between input topology and final rasterized primitive clear?
- Is exact image equality the intended explanation of the test's pass condition?
- Are the line-producing exclusions and feature-gated cases represented correctly?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's primary behavior axis as line-rasterization mode and copy the failure-cause table directly.
- Distill the background into the effective-primitive and reference-comparison prerequisites; keep setup and validation in their later sections.
- Use the deterministic seed exclusion of line mode as a concise runtime detail, not as a separate walkthrough.
- Keep shader analysis brief because shader code is shared support rather than the tested behavior.
