# Understanding Brief: NegativeViewportHeightTests

## One-Sentence Test Purpose

This test family checks whether Vulkan rasterization honors negative and zero viewport heights, face culling after the Y-flip, and viewports placed wholly outside a framebuffer.

## Background Knowledge

### Viewport transformation and face orientation

A `VkViewport` maps the post-vertex coordinate space to the framebuffer. A negative `height` reverses the Y direction. That reversal also changes the sign of a triangle's screen-space area, so the effective front-facing orientation changes unless the pipeline's `frontFace` and `cullMode` produce the corresponding result.

A zero viewport height has a different result: it has no rasterizable vertical extent, so the draw should contribute no fragments. The off-screen cases use the same viewport rules but place at least one viewport axis entirely outside a 32x32 framebuffer.

Why it matters here:
- The first two test families separate negative-height winding behavior from zero-height empty output.
- The off-screen family checks that a draw cannot modify the attachment when its viewport misses the framebuffer, including selected negative-height cases.

## One Concrete Example

For `draw.renderpass.negative_viewport_height.front_ccw_cull_none`, the host creates a 256x128 `VK_FORMAT_R8G8B8A8_UNORM` color target, clears it to `(0.125, 0.25, 0.5, 1.0)`, and draws two triangles from six fixed `Vec4` vertices. The viewport is `{0, 128, 256, -128, 0, 1}`. The left source triangle is CCW and the right source triangle is CW; after the Y-flip their effective orientations are CW and CCW. With `front_ccw` and no culling, the left triangle is gray and the right triangle is white in the reference image.

The zero-height counterpart keeps the same geometry and pipeline combinations but changes the viewport height to `0.0` and the Y origin to half the original viewport Y. Its reference image stays at the clear color.

## End-to-End Test Flow

```text
[host] select a registered front-face/cull-mode combination, or an off-screen axis combination and height sign
[host] create the color attachment, render-pass or dynamic-rendering state, framebuffer, pipeline, and vertex data
[host] compile the small inline vertex and fragment GLSL programs when the case is created
[host] clear the color target and insert the transfer-to-color-attachment barrier
[host] set the viewport and submit the draw, using the selected render-pass/dynamic-rendering and secondary-command-buffer variant
[device] transform vertices through the viewport, apply winding/culling, rasterize fragments, and run the fragment shader
[host] wait for completion and read the color image or buffer back
[host] compare the result with the generated reference or the clear color
```

The source includes shared dynamic-rendering and secondary-command-buffer paths through `DynRenderHelper`; those paths change command recording, not the viewport condition being tested.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `NegativeViewportHeightTest::initPrograms` builds `vert` from GLSL 4.50. It copies the input position to `gl_Position`.
- The same function builds `frag`, which writes white for `gl_FrontFacing` and gray otherwise.
- `OffScreenViewportCase::initPrograms` builds `vert` from GLSL 4.60 using `gl_VertexIndex` to select four full-screen-quad positions, and `frag` writes blue.
- The host creates fixed-function pipeline state with dynamic viewport state, the selected cull mode and front-face value, triangle-list topology for the first two families, and triangle-strip topology for the off-screen family.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 256x128 color image | yes | as color attachment | cleared and rendered | yes | reference image for the negative/zero-height families |
| 32x32 color image and backing buffer | yes | image as color attachment, buffer for copyback | cleared and rendered/copyied | yes | exact clear-color check for off-screen cases |
| Host-visible vertex buffer | yes | vertex binding 0 | read by the first-family draw | no | holds the two fixed triangles |
| Inline GLSL programs | yes | shader modules in graphics pipeline | executed by device | no | exposes front/back classification or supplies geometry/color |

The render target is a real image resource. `gl_FrontFacing` is shader state, not a host-created resource.

## What Is Checked

- Negative-height cases compare the 256x128 result against a reference image with a blue clear color, gray back-facing regions, and white front-facing regions. `tcu::fuzzyCompare` uses a `0.02f` threshold.
- Zero-height cases compare against the same clear color because no fragments should be generated.
- Off-screen cases compare the 32x32 readback buffer with black using `tcu::floatThresholdCompare` and a zero threshold.
- A failure is reported as an incorrect rendered image or an unexpected color result; the source does not independently identify which pipeline stage caused the mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** viewport/culling scenario
>
> **Candidate values:** negative viewport height with `front_ccw` or `front_cw` and four cull modes; zero viewport height with the same eight combinations; off-screen viewport with each registered X/Y placement and optional `_negative_height`.

The primary behavioral axis is the viewport condition and its directly coupled rasterization state. The source implements three registered roots in one file, while the `frontFace` and `cullMode` dimensions expose the winding result within the first two roots.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| negative height + front-face/cull combination | Incorrect viewport Y inversion, front-face classification, cull-mode application, rasterization, or image comparison/reference construction |
| zero viewport height + front-face/cull combination | Fragments produced despite zero vertical extent, or an attachment clear, transition, draw, or readback error |
| off-screen viewport without negative height | Viewport clipping or rasterization produced pixels outside the intended framebuffer, or clear/copyback handling is wrong |
| off-screen viewport with `_negative_height` | Negative-height viewport transformation combined incorrectly with clipping, or a shared attachment/command-path error |

## Important Variations and Special Cases

- `negative_viewport_height` and `zero_viewport_height` each register eight test cases: two front-face values crossed with four cull modes.
- `offscreen_viewport` registers 16 test cases. It crosses the six valid X/Y placements where at least one axis is off-screen with positive and negative viewport-height forms.
- Off-screen coordinates use `de::Random` with seeds beginning at `1674229780`; the seed increments for each registered case. The generated ranges are bounded by `-1024` and `1024`.
- `VK_KHR_maintenance1` is required for the first two roots and for off-screen cases whose `negativeHeight` is true. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Fixed vertices, viewport draw, reference image, and fuzzy comparison | [NegativeViewportHeightTestInstance](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L104-L595) | Defines the negative/zero-height behavior and expected pixels |
| Front-face and cull-mode matrix | [populateTestGroup](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L632-L663) | Registers the eight combinations per root |
| Feature checks | [NegativeViewportHeightTest::checkSupport](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L665-L690) | Shows maintenance and dynamic-rendering requirements |
| Off-screen generator and execution | [OffScreenViewportCase](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L692-L1006) | Defines axis ranges, seeds, viewport sign, clear, and readback |
| Root registration | [create...Tests](../../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L1009-L1059) | Defines the three direct test-family roots |
| Draw dispatcher | [vktDrawTests.cpp](../../../modules/vulkan/draw/vktDrawTests.cpp#L75-L88) | Adds the three roots under `draw.renderpass` |
| Viewport and rasterization semantics | [primsrast.adoc](../../../../vulkan-docs/src/chapters/primsrast.adoc) | Vulkan specification background for viewport mapping and culling |

## Questions / Risk Points for User Audit

- The repository has no checked-in mustpass file containing these paths in the inspected `external/vulkancts` tree; registration is therefore grounded in the dispatcher and implementation source.
- The source defines `createZeroViewportHeightTests` with `SubGroupParams subGroupParams{false, groupParams}`, so the shared `populateTestGroup` receives `zeroViewportHeight == false`. This appears inconsistent with the intended zero-height behavior in `draw()`. The page must describe the source's registered root and intended branch separately, or this should be confirmed against the current build/source revision.
- The source's `NegativeViewportHeightTestInstance` constructs `PipelineCreateInfo` with `*m_renderPass` even when dynamic rendering is selected; this may be an existing implementation-path concern and was not runtime-tested here.
- No shader analyzer or SPIR-V disassembler output was generated. The shader code is short and not the behavior axis; the final page therefore summarizes it without claiming generated analyzer artifacts.

## Conversion Notes for Final Wiki Rewrite

- Keep the three source-registered roots in one parseable hierarchy block and expand only their direct test-case level.
- Treat viewport condition as the primary behavior parameter, with front-face and cull mode as explicit dimensions for the first two roots.
- Distill the concrete triangle example into `Background Knowledge`, `Behavior Parameters`, and `Runtime Execution and Result Checking`; keep the beginner scaffolding here only.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` separately.
- Preserve the zero-root source inconsistency as an unresolved risk instead of silently correcting the source-derived claim.
