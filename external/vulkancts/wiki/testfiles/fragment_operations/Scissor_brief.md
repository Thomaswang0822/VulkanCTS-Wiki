# Understanding Brief: fragment_operations.scissor

## One-Sentence Test Purpose

This test checks whether Vulkan's scissor test removes samples outside the selected `VkRect2D` for point, line, triangle, and multi-viewport drawing.

## Background Knowledge

### Scissor test coverage

The Vulkan scissor test compares each covered sample's framebuffer coordinates with the `VkRect2D` selected for the fragment's `ViewportIndex`. A sample inside the half-open rectangle remains covered; a sample outside has its coverage set to zero. The rectangle comes from `VkPipelineViewportStateCreateInfo` in these tests because the pipeline uses non-dynamic scissor state.

Why it matters here:
- A draw can produce geometry that spans the render target while the scissor state limits which samples can contribute to the color attachment.
- With multiple viewports, the scissor rectangle is selected by the same `ViewportIndex` that selects the viewport, so each viewport can clip to a different rectangle.

### Graphics pipeline state

The scissor rectangle is graphics pipeline state. It affects drawing commands, not clears performed outside those draws. This is why the direct cases compare rendered images rather than testing color, depth, or stencil clear behavior.

## One Concrete Example

Consider the `triangles.crossing` test. The renderer first draws the large triangle with a full-render-target scissor. It then creates another pipeline with the scissor rectangle `(0.4, 0.4, 0.2, 0.2)` in normalized test coordinates and draws the same vertices. The expected image is the full-scissor image with every pixel outside the corresponding 20%-by-20% rectangle replaced by the clear color.

## End-to-End Test Flow

```text
[host] select a registered primitive and its render/scissor areas
[host] generate vertices with deterministic random placement for short primitives, or create a full-span line/triangle
[host] create a 128x128 R8G8B8A8_UNORM color attachment, host-visible vertex buffer, render pass, framebuffer, and shader modules
[host] create a graphics pipeline with one viewport, one VkRect2D scissor, and the topology for the primitive
[host] submit a draw and copy the color image to a host-visible buffer
[host] repeat the draw with a full scissor and with the case scissor for direct cases
[device] rasterize the primitive and set coverage to zero for samples outside the selected scissor rectangle
[host] apply the case scissor in software to the full-scissor image
[host] compare the expected and rendered images with a per-channel threshold of 0.02
[host] pass when the images match; otherwise fail with "Rendered image is not correct"
```

The delegated `multi_viewport` flow is separate: its helper creates one to sixteen viewports and matching scissor rectangles, emits one fullscreen quad per viewport from a geometry shader, and compares the result with a software-colored grid.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The direct cases generate GLSL 4.50 vertex and fragment shaders. The vertex shader writes `gl_Position` and passes a color; for point cases it also writes `gl_PointSize = 1.0`. The fragment shader writes the interpolated color.
- The multi-viewport helper also generates a GLSL 4.50 geometry shader. It writes `gl_ViewportIndex = gl_PrimitiveIDIn`, emits four vertices for a fullscreen quad, and forwards the input color.
- The pipeline stores the scissor state in `VkPipelineViewportStateCreateInfo` through the CTS pipeline helper; the direct renderer creates a new pipeline for each scissor because it does not use dynamic state.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 128x128 `VK_FORMAT_R8G8B8A8_UNORM` color image and view | yes | yes, as a color attachment | written by the draw | copied to a buffer | Captures the scissor result. |
| Host-visible vertex buffer | yes | yes, as vertex input | read by vertex processing | no | Supplies generated positions and colors. |
| Host-visible color buffer | yes | yes, as transfer destination | written by image-to-buffer copy | yes | Supplies the image checked by the host. |
| Render pass and framebuffer | yes | yes | used by the draw | no | Define the color attachment used for rendering. |
| `gl_ViewportIndex` in the geometry shader | no, shader built-in | used by rasterization | written by the geometry shader | no | Selects the matching viewport and scissor in the delegated family; it is not a host-created resource. |

## What Is Checked

- Direct cases render once with a full scissor and once with the case scissor. The host applies the case rectangle to the full-scissor image, then compares it with the case-scissor image using `tcu::floatThresholdCompare()` and threshold `Vec4(0.02f)`.
- The direct test uses clear color `(0.5, 0.5, 1.0, 1.0)` and white primitive color. A mismatch returns `Rendered image is not correct`.
- Multi-viewport cases construct a gray-cleared reference image, fill each generated grid rectangle with its viewport color, and compare that image with the copied render result using the same threshold.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family or delegated test family
>
> **Candidate values:** `points`, `lines`, `triangles`, `multi_viewport`

The direct test family's case leaf adds a secondary coverage relation: `inside`, `partially_inside`, `outside`, or `crossing`. The primary page-level axis remains the four registered children because they select the implementation path and primitive behavior; `multi_viewport` is delegated to its own page.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `points` | Incorrect scissor coverage for point rasterization; direct image setup or comparison failure. |
| `lines` | Incorrect scissor coverage for line rasterization; direct image setup or comparison failure. |
| `triangles` | Incorrect scissor coverage for triangle rasterization; direct image setup or comparison failure. |
| `multi_viewport` | Incorrect association of `ViewportIndex`, viewport, and scissor rectangle; missing required multi-viewport support; delegated image setup or comparison failure. |

## Important Variations and Special Cases

- `points` registers `inside`, `partially_inside`, and `outside`. It generates 50 points with a deterministic random seed.
- `lines` adds `crossing`: the first three leaves generate 30 short lines, while `crossing` uses one line spanning the selected render area.
- `triangles` adds `crossing`: the first three leaves generate 20 small triangles, while `crossing` uses one triangle spanning the selected render area.
- Direct render and scissor areas use normalized `(origin-x, origin-y, width, height)` values. The registered areas are full, cropped `(0.2, 0.2, 0.6, 0.6)`, more-cropped `(0.4, 0.4, 0.2, 0.2)`, left half, and right half.
- `multi_viewport` registers `scissor_1` through `scissor_16`. It requires geometry shaders, `multiViewport`, and `maxViewports >= 16`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Direct registration and case matrix | [`createTestsInGroup()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L496-L576) | Defines the four direct children, leaves, areas, and primitive choices. |
| Direct generated vertices and topology | [`genVertices()` and `getTopology()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L183-L259) | Shows how points, lines, triangles, and crossing primitives are built. |
| Direct pipeline scissor state | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L114-L175) | Supplies one viewport and one pipeline scissor rectangle. |
| Direct host check | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L439-L491) | Defines the two renders, software masking, and image comparison. |
| Delegated registration and support | [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L450) | Defines `scissor_1` through `scissor_16` and feature/limit checks. |
| Delegated multi-viewport render/check | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L428) | Defines the grid reference image and result comparison. |
| Vulkan scissor semantics | [`Scissor Test`](../../../../vulkan-docs/src/chapters/fragops.adoc#L426-L445) | Defines rectangle membership and coverage-zero behavior. |
| Vulkan multi-viewport feature and limit | [`multiViewport`](../../../../vulkan-docs/src/chapters/features.adoc#L351-L359), [`maxViewports`](../../../../vulkan-docs/src/chapters/limits.adoc#L568-L579) | Grounds the delegated feature and limit requirements. |

## Questions / Risk Points for User Audit

- Is the distinction between the direct families and the delegated `multi_viewport` family clear?
- Is the two-render software-mask reference for direct cases clear enough to explain a failure?
- Should the final page include a representative generated shader walkthrough, or is the brief shader summary sufficient because the tested behavior is fixed-function scissor state?
- Is `test family` the right page-level behavior axis when direct case leaves also vary the coverage relation?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's `## Background Knowledge` limited to scissor coverage, pipeline state, and the multi-viewport association with `ViewportIndex`.
- Use the direct case matrix in `## Parameter Dimensions and Observed Values` and explain the four registered test families in `## Behavior Parameters`.
- Keep the direct image-reference procedure in `## Runtime Execution and Result Checking` and copy the failure mapping table unchanged.
- Link `multi_viewport` to [`ScissorMultiViewport.md`](ScissorMultiViewport.md) rather than duplicating its implementation.
- Keep source and Vulkan specification links in the final appendix.
