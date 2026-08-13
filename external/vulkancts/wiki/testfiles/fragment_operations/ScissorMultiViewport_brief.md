# Understanding Brief: fragment_operations.scissor.multi_viewport

## One-Sentence Test Purpose

This test checks whether the scissor test correctly applies a separate scissor rectangle to each active viewport when multiple viewport-scissor pairs are bound at once.

## Background Knowledge

### Viewport-scissor pairing and the scissor test index

Vulkan binds viewports and scissor rectangles as parallel arrays. The pipeline's viewport state carries `viewportCount` viewports and an equal `scissorCount` scissor rectangles, and the spec requires the two counts to match when both are static ([VUID-VkPipelineViewportStateCreateInfo-scissorCount-04134](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#VUID-VkPipelineViewportStateCreateInfo-scissorCount-04134)).

The scissor test does not use a global rectangle. Each fragment is tested against the scissor rectangle indexed by that fragment's `ViewportIndex`. The relevant spec text in `fragops.adoc` states: "The scissor test compares the framebuffer coordinates (x_f, y_f) of each sample covered by a fragment against a scissor rectangle at the index equal to the fragment's `ViewportIndex`." Samples outside that rectangle have their coverage set to zero.

Why it matters here:
- The test's whole correctness question is whether per-fragment `ViewportIndex` selection drives per-rectangle clipping. A single global scissor, or an off-by-one index, would produce the wrong clipped region.
- The viewport transform selects its viewport the same way: when a geometry shader writes `ViewportIndex`, "the viewport transformation uses the viewport corresponding to the value assigned to `ViewportIndex`."

### Routing primitives to viewports with `gl_ViewportIndex`

Without the `VK_EXT_shader_viewport_index_layer` / `VK_NV_viewport_array2` extensions or Vulkan 1.2, only a geometry shader can set `ViewportIndex` to direct primitives to specific viewports. The spec says: "If a geometry shader is active and has an output variable decorated with `ViewportIndex`, the viewport transformation uses the viewport corresponding to the value assigned to `ViewportIndex`." A pre-rasterization stage must write the same `ViewportIndex` value to all vertices of a given primitive, or results are undefined.

Why it matters here:
- The test relies on this exact mechanism. It draws a point list, and the geometry shader expands each input point into a fullscreen quad, then writes `gl_ViewportIndex = gl_PrimitiveIDIn` so primitive `i` lands in viewport `i`.
- This is why the test requires the `geometryShader` feature, not because the test is "about" geometry shaders.

### The `multiViewport` feature and `maxViewports` floor

`multiViewport` gates whether more than one viewport is allowed. With it disabled, `viewportCount` and `scissorCount` must both be 1. When `multiViewport` is supported, `maxViewports` has a guaranteed minimum of 16 (the limits table lists `16` as the `min` required value for `maxViewports`).

Why it matters here:
- The test sweeps viewport counts from 1 up to `MIN_MAX_VIEWPORTS = 16`, exercising the full guaranteed range. `checkSupport()` rejects any device whose `maxViewports` is below 16, so every run case is legal.

## One Concrete Example

Take `scissor_4` (viewport count 4). The host creates a 128x128 color image, generates four scissor rectangles laid out in a 2x2 grid (each 64x64), and picks four distinct vertex colors. The pipeline binds four identical fullscreen viewports plus the four grid scissors. The draw issues four points. The geometry shader turns point `i` into a fullscreen quad (`gl_Position` covering all four corners from (-1,-1) to (1,1)) and sets `gl_ViewportIndex = gl_PrimitiveIDIn = i`, so quad 0 goes to viewport/scissor 0, quad 1 to pair 1, and so on.

Each quad tries to fill the entire framebuffer, but the scissor test at viewport index `i` clips it to rectangle `i`. The expected result is a 2x2 colored grid on a gray background, with no quad bleeding outside its own cell.

This is faithful to the source: [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L429) uses `renderSize(128,128)`, [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) tiles the grid, and the geometry shader at [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260) emits the fullscreen quad with `gl_ViewportIndex = gl_PrimitiveIDIn`.

## End-to-End Test Flow

```text
[host] checkSupport: require geometryShader + multiViewport features; reject maxViewports < 16
[host] pick numViewports (the case parameter, 1..16)
[host] generate numViewports scissor rectangles tiled into a grid over a 128x128 target
[host] pick numViewports distinct vertex colors from a fixed 16-entry palette
[host] build pipeline: numViewports identical fullscreen viewports + the tiled scissors
[host] create 128x128 color image (R8G8B8A8_UNORM), vertex buffer of numViewports colored points
[host] begin render pass, clear target to gray (0.5,0.5,0.5,1.0)
[device] draw numViewports points
[device] geometry shader: each point -> fullscreen quad, gl_ViewportIndex = gl_PrimitiveIDIn
[device] viewport transform uses viewport i; scissor test clips fragment coverage to scissor i
[host] copy color image to host-visible buffer
[host] build reference image: gray clear, then clear each scissor subregion to its expected color
[host] tcu::floatThresholdCompare(rendered, reference, threshold 0.02) -> pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL 450 vertex shader ([`initPrograms()` vertex block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L204-L217)): passes `in_color` through as `out_color`. Exists only because the geometry shader consumes a vertex-stage output.
- GLSL 450 geometry shader ([`initPrograms()` geometry block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260)): the tested property lives here. It declares `layout(points) in; layout(triangle_strip, max_vertices=4) out;`, sets `gl_ViewportIndex = gl_PrimitiveIDIn` before each `EmitVertex()`, and writes the four fullscreen corners. This routes primitive `i` to viewport-scissor pair `i`.
- GLSL 450 fragment shader ([`initPrograms()` fragment block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L262-L276)): writes `in_color` to `out_color`. No logic of its own.
- These shaders are identical across all 16 cases; `initPrograms()` ignores `numViewports`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 128x128 color image (`R8G8B8A8_UNORM`) | yes | yes (color attachment) | written by fragment shader | yes (via copy buffer) | The clipped render target whose pixels are checked |
| Vertex buffer of `numViewports` colored points | yes (host-visible, flushed) | yes (vertex buffer) | read by vertex/geometry shader | no | Supplies one color per viewport-scissor pair |
| Host-visible readback buffer | yes | yes (transfer dst) | written by image->buffer copy | yes | Delivers rendered pixels to the host compare |

## What Is Checked

The host builds a reference image with [`generateReferenceImage()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197): clear the whole 128x128 target to gray, then clear each scissor subregion to its expected color. Rendered output is compared to this reference with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L422-L425) at a per-channel threshold of `0.02`. The check runs on the host over the full framebuffer. Any pixel mismatch above tolerance fails the case.

Because each scissor rectangle is expected to contain exactly one color and the surrounding area is expected to stay gray, the compare detects three distinct failure modes at once: wrong viewport routing, wrong scissor clipping bounds, and color bleed between cells.

## Behavior Parameter Identification

> **Behavior parameter:** `numViewports` (the test case leaf, `scissor_1` through `scissor_16`)
>
> **Candidate values:** `scissor_1`, `scissor_2`, `scissor_3`, `scissor_4`, `scissor_5`, `scissor_6`, `scissor_7`, `scissor_8`, `scissor_9`, `scissor_10`, `scissor_11`, `scissor_12`, `scissor_13`, `scissor_14`, `scissor_15`, `scissor_16`

The only registered dimension is viewport count. Each leaf changes the number of active viewport-scissor pairs and the grid tiling derived from it, but the shader and validation logic are identical across all cases.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `scissor_1` | Scissor rectangle setup, clear, or image compare infrastructure (single-viewport baseline) |
| `scissor_2` through `scissor_16` | Per-viewport `ViewportIndex` routing, scissor-array indexing, or multi-viewport scissor clipping |

All cases share the same compare and reference-image path, so an infrastructure defect in the clear/compare would likely fail `scissor_1` too.

## Important Variations and Special Cases

- Grid tiling changes with count. [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) computes `numCols = ceil(sqrt(numScissors))` and `numRows = ceil(numScissors / numCols)`, then tiles equal-sized rectangles. For non-square counts the last row is partially filled, so some scissor cells are unused and remain gray. This is by design and is reproduced in the reference image.
- `scissor_1` is effectively a single-viewport baseline. With one viewport and one scissor covering the whole (or first cell of the) target, only the infrastructure path is exercised.
- The 16-entry color palette in [`generateColors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L163-L177) is fixed; each case takes the first `numViewports` colors.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration loop, leaf names | [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L451) | Confirms `scissor_1`..`scissor_16` and the `1..MIN_MAX_VIEWPORTS` sweep |
| Feature support gate | [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L438) | Requires geometryShader + multiViewport + maxViewports >= 16 |
| Geometry shader (tested property) | [`initPrograms()` geometry block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260) | Sets `gl_ViewportIndex = gl_PrimitiveIDIn`, emits fullscreen quad |
| Grid scissor generation | [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) | Tiles the render area into equal rectangles |
| Reference image | [`generateReferenceImage()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197) | Clears each scissor subregion to its expected color |
| Pass/fail compare | [`tcu::floatThresholdCompare()` in test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L422-L425) | Threshold 0.02 image compare |
| Viewport-scissor pipeline setup | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L129) | Binds one viewport + one scissor per requested count |

## Questions / Risk Points for User Audit

- Is the core test purpose (per-viewport scissor clipping, not geometry-shader correctness) stated clearly enough?
- Is the behavior parameter (`numViewports`) the right primary axis, given all cases share one shader?
- Does the failure cause mapping over-split `scissor_1` from the rest, or is the single-row form correct?
- Is the spec citation style (VUID + fragops/vertexpostproc text) acceptable in the brief, or should it be condensed for the final page?

## Conversion Notes for Final Wiki Rewrite

- Distill Background Knowledge into a short bullet list: viewport-scissor array pairing + per-fragment `ViewportIndex` indexing, geometry-shader `ViewportIndex` routing, and the `multiViewport` / `maxViewports >= 16` floor. Keep the spec grounding but cut the tutorial tone.
- Keep the concrete `scissor_4` example as the mental model anchor, referenced from Overview and the shader walkthrough.
- The geometry shader is the one representative walkthrough. The vertex and fragment shaders are pass-through and should appear only as brief notes, not separate walkthroughs.
- Copy the Failure Cause Mapping table directly into the final page. Write Cause Analysis fresh.
- Spec citations condense to short inline references; the full VUIDs and extended quotes are brief-only scaffolding.
