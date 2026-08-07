# Understanding Brief: Inverted depth ranges

## One-Sentence Test Purpose

This test checks whether the graphics pipeline maps interpolated depth correctly when `VkViewport::minDepth` is greater than `maxDepth`, with and without depth clamping and with selected depth-bias clamps.

## Background Knowledge

### Viewport depth mapping

After rasterization produces an interpolated depth value, Vulkan maps it through the viewport depth range. An inverted range reverses the ordering: the test's reference uses `depthClamped * maxDepth + (1.0 - depthClamped) * minDepth`. The viewport range is separate from the depth attachment's representable format range.

Why it matters here:
- `minDepth > maxDepth` is the behavior under test, including equal, small, full, and unrestricted spans.
- The pipeline's depth-clamp state changes whether out-of-range fragments are retained before depth testing and storage.

### Depth bias and attachment comparison

Depth bias is applied to the interpolated depth before the reference maps it through the viewport range. A depth-bias clamp limits the computed slope-based bias; for an inverted range the CTS reference reverses the bias sign. The color attachment receives `gl_FragCoord.z`, while the depth attachment stores the depth value used for the depth comparison.

## One Concrete Example

For `depthclamp_deltasmall`, the source computes `minDepth = 0.65` and `maxDepth = 0.35`. A triangle vertex or interpolated point with normalized depth `d = 0.25` maps to `0.25 * 0.35 + 0.75 * 0.65 = 0.575`. The color reference expects that mapped value in red, and the depth reference expects the corresponding value in the depth attachment. The `nodepthclamp_deltasmall` case uses the same range but discards fragments whose pre-range depth is outside the supported interval instead of retaining them through depth clamping.

## End-to-End Test Flow

```text
[host] select one depth-clamp mode and one registered depth parameter set
[host] create color and D16_UNORM depth targets, a framebuffer/render pass or dynamic-rendering setup, and a graphics pipeline
[host] build the inline vertex and fragment GLSL programs
[host] clear the attachments and issue the required transfer-to-attachment barriers
[host] set a viewport whose depth range is the selected inverted pair and draw one triangle
[device] run vertex processing, rasterization, fragment shading, depth operations, and attachment writes
[host] wait for submission, read back color and depth images, and generate matching reference images
[host] compare color with fuzzy threshold 0.02 and unmasked depth pixels with threshold 0.0064
[host] return failure if either comparison fails
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The test builds a GLSL 4.50 vertex shader named `vert`. It forwards `in_position` to `gl_Position`.
- It builds a GLSL 4.50 fragment shader named `frag`. It writes `vec4(gl_FragCoord.z, 0.5, 0.5, 1.0)` to the color attachment.
- The host creates a graphics pipeline with dynamic viewport state, depth testing and writing enabled, optional depth clamp and depth bias, and either a legacy render pass or dynamic rendering.
- The reference generator interpolates the three vertex depths, applies depth bias when enabled, clamps the normalized value to `[0,1]`, applies the inverted viewport range, and optionally clamps the final value to the range endpoints.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read | no | Supplies one triangle with controlled vertex `z` values. |
| Color target | yes | as color attachment | written | yes | Stores `gl_FragCoord.z` in red for an independent mapping check. |
| D16_UNORM depth target | yes | as depth attachment | read/written | yes | Stores and tests the mapped depth value. |
| Framebuffer/render-pass or dynamic-rendering state | yes | pipeline/command state | used | no | Selects the attachment path under test. |
| Stencil aspect of reference image | host-generated only | no | no | no | Masks boundary pixels in no-clamp depth comparisons. |

## What Is Checked

- The color image is compared with `tcu::fuzzyCompare` using a `0.02f` threshold.
- The depth image is compared per pixel against the generated reference with `kDepthThreshold = 0.0064f`.
- In no-clamp cases, reference pixels near normalized depth boundaries are marked with `kMaskedStencil` and skipped because coverage rounding can make those pixels ambiguous.
- A depth mismatch logs result, reference, and a green/red error mask. Any color or depth mismatch returns `Result images are incorrect`.

## Behavior Parameter Identification

> **Behavior parameter:** depth-clamp mode, the primary behavioral axis
>
> **Candidate values:** `depthclamp`, `nodepthclamp`

The six depth parameter leaves are orthogonal variations of the viewport span and bias treatment. The two depth-clamp values change the fragment-retention rule and therefore change what behavior the test is asking the implementation to handle.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `depthclamp` | Incorrect inverted viewport-depth mapping, depth clamping of out-of-range fragments, depth-bias handling, attachment writes, or image readback/comparison. |
| `nodepthclamp` | Incorrect inverted viewport-depth mapping, fragment discard at depth boundaries, depth-bias handling, attachment writes, or masked depth comparison. |

## Important Variations and Special Cases

- `deltazero` uses `minDepth = maxDepth = 0.5`; it checks the equal-endpoint case rather than an actual reversal.
- `deltasmall` uses `0.65` and `0.35`; `deltaone` uses `1.0` and `0.0`.
- `deltaone_bias_clamp_neg` and `deltasmall_bias_clamp_pos` enable depth bias with clamps `-0.003` and `0.003` respectively.
- `depth_range_unrestricted` uses `minDepth = 1.85` and `maxDepth = -0.85`, so it requires `VK_EXT_depth_range_unrestricted`.
- Dynamic-rendering and secondary-command-buffer forms come from the shared draw dispatcher. They exercise the same test logic with different command-recording paths.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameter generation and test registration | [`populateTestGroup`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L737-L782) | Defines both depth-clamp values, six depth leaves, exact depth values, and case names. |
| Feature checks | [`InvertedDepthRangesTest::checkSupport`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L712-L726) | Shows depth clamp, bias clamp, unrestricted range, and dynamic-rendering requirements. |
| Reference mapping | [`generateReferenceImage`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L363-L457) | Defines interpolation, bias, inverted mapping, clamping, and boundary masking. |
| Shader construction | [`InvertedDepthRangesTest::initPrograms`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L665-L710) | Defines `vert`, `frag`, and the `gl_FragCoord.z` color encoding. |
| Execution and result checks | [`InvertedDepthRangesTestInstance::iterate`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L502-L663) | Records, submits, reads back, compares, and reports results. |
| Vulkan pipeline and fragment context | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc) and [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc) | Grounds the graphics-pipeline and fragment-operation concepts used by the brief. |

## Questions / Risk Points for User Audit

- The source and mustpass evidence show the same six leaves under each of `depthclamp` and `nodepthclamp`; confirm that the page's compact hierarchy is sufficient for readers who need every leaf.
- The source supports legacy render-pass, dynamic-rendering, and secondary-command-buffer dispatcher variants, but this file's registration function itself supplies only the inverted-depth family. Confirm that describing those as shared-mode variants is clear.
- The color comparison observes `gl_FragCoord.z`, while the depth comparison observes stored depth. A failure does not by itself isolate shader, rasterization, depth-test, attachment, readback, or comparison code.

## Conversion Notes for Final Wiki Rewrite

- Keep `depthclamp` versus `nodepthclamp` as the primary behavior axis and copy the mapping table directly into the final page.
- Put the six exact depth leaves and their values in `Parameter Dimensions and Observed Values`, not in a deeply expanded registration tree.
- Distill the viewport mapping and the color/depth dual-observation model into `Background Knowledge`, `Shader Analysis`, and `Runtime Execution and Result Checking`.
- Explain dynamic rendering and secondary command buffers as dispatcher/shared-mode variants, not as invented registration roots.
- Write fresh cause analysis in the final page; do not copy this brief's risk wording as a failure diagnosis.
