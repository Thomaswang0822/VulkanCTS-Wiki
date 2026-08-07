## Overview

**Core question:** Does the graphics pipeline preserve the specified depth mapping when a viewport has `minDepth >= maxDepth`, including the equal-endpoint case?

- This page covers [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L93-L792), whose `inverted_depth_ranges` test family is registered below the draw category's render-pass path and three non-nested dynamic-rendering command paths.
- Each case draws one triangle through a pipeline with dynamic viewport state, depth testing, and depth writes. The viewport depth range is inverted, equal, or outside `[0,1]` according to the selected leaf.
- The primary behavior values are `depthclamp` and `nodepthclamp`. They select depth clamping with z clipping disabled or z clipping with depth clamping disabled, respectively.
- The fragment shader writes `gl_FragCoord.z` to the red channel. The host checks that color result separately from the `VK_FORMAT_D16_UNORM` depth attachment.

## Background Knowledge

For the shared concepts of viewport/depth-range rasterization state and attachment readback, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- Viewport depth mapping converts the normalized depth from rasterization into the viewport range. For this test, the reference uses `d * maxDepth + (1 - d) * minDepth`, so `minDepth > maxDepth` reverses the ordering.
- `depthClampEnable` couples two distinct operations in the pipeline. Enabling it disables z clipping and later clamps fragment depth to the sorted viewport endpoint range; disabling it leaves z clipping enabled. Thus `nodepthclamp` represents clipping at the clip-volume depth boundaries, not post-rasterization fragment discard.
- A fragment shader can read the interpolated depth through `gl_FragCoord.z`. Writing that value to color lets a test observe shader-visible depth separately from the depth value later compared with and written to the depth attachment.

## Registration Hierarchy

```text
draw.renderpass.inverted_depth_ranges
├── depthclamp_deltaone
├── depthclamp_deltaone_bias_clamp_neg
├── depthclamp_deltasmall
├── depthclamp_deltasmall_bias_clamp_pos
├── depthclamp_deltazero
├── depthclamp_depth_range_unrestricted
├── nodepthclamp_deltaone
├── nodepthclamp_deltaone_bias_clamp_neg
├── nodepthclamp_deltasmall
├── nodepthclamp_deltasmall_bias_clamp_pos
├── nodepthclamp_deltazero
└── nodepthclamp_depth_range_unrestricted

draw.dynamic_rendering.primary_cmd_buff.inverted_depth_ranges
├── depthclamp_deltaone
├── depthclamp_deltaone_bias_clamp_neg
├── depthclamp_deltasmall
├── depthclamp_deltasmall_bias_clamp_pos
├── depthclamp_deltazero
├── depthclamp_depth_range_unrestricted
├── nodepthclamp_deltaone
├── nodepthclamp_deltaone_bias_clamp_neg
├── nodepthclamp_deltasmall
├── nodepthclamp_deltasmall_bias_clamp_pos
├── nodepthclamp_deltazero
└── nodepthclamp_depth_range_unrestricted

draw.dynamic_rendering.partial_secondary_cmd_buff.inverted_depth_ranges
├── depthclamp_deltaone
├── depthclamp_deltaone_bias_clamp_neg
├── depthclamp_deltasmall
├── depthclamp_deltasmall_bias_clamp_pos
├── depthclamp_deltazero
├── depthclamp_depth_range_unrestricted
├── nodepthclamp_deltaone
├── nodepthclamp_deltaone_bias_clamp_neg
├── nodepthclamp_deltasmall
├── nodepthclamp_deltasmall_bias_clamp_pos
├── nodepthclamp_deltazero
└── nodepthclamp_depth_range_unrestricted

draw.dynamic_rendering.complete_secondary_cmd_buff.inverted_depth_ranges
├── depthclamp_deltaone
├── depthclamp_deltaone_bias_clamp_neg
├── depthclamp_deltasmall
├── depthclamp_deltasmall_bias_clamp_pos
├── depthclamp_deltazero
├── depthclamp_depth_range_unrestricted
├── nodepthclamp_deltaone
├── nodepthclamp_deltaone_bias_clamp_neg
├── nodepthclamp_deltasmall
├── nodepthclamp_deltasmall_bias_clamp_pos
├── nodepthclamp_deltazero
└── nodepthclamp_depth_range_unrestricted
```

Each root directly contains twelve test case leaves: the Cartesian product of the `depthclamp`/`nodepthclamp` behavior values with `deltazero`, `deltasmall`, `deltaone`, `deltaone_bias_clamp_neg`, `deltasmall_bias_clamp_pos`, and `depth_range_unrestricted`. The shared draw dispatcher registers the render-pass root plus primary, partial-secondary, and complete-secondary dynamic-rendering roots; it deliberately omits this family from the nested-secondary roots.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Depth-clamp behavior | `depthclamp`, `nodepthclamp` | Selects depth clamping with z clipping disabled or z clipping with depth clamping disabled. | [`populateTestGroup`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L737-L782) |
| Depth leaf | `deltazero`, `deltasmall`, `deltaone`, `deltaone_bias_clamp_neg`, `deltasmall_bias_clamp_pos`, `depth_range_unrestricted` | Selects viewport span and, for two leaves, depth-bias state. | [`depthParams`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L750-L765) |
| Viewport depth range | `(0.5, 0.5)`, `(0.65, 0.35)`, `(1.0, 0.0)`, `(1.85, -0.85)` | Defines the mapping applied after normalized depth interpolation. | [`populateTestGroup`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L767-L781) |
| Depth bias | disabled; enabled with clamp `-0.003` or `0.003` | Adds the slope-based bias before the reference applies the viewport mapping. | [`generateReferenceImage`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L391-L409) |
| Rendering mode | render pass; dynamic rendering in primary, partial-secondary, or complete-secondary command buffers | Exercises the same test logic through the four paths supplied by the draw dispatcher. | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

The exact leaf values are:

| Test case leaf | Delta | Depth bias | Bias clamp | `minDepth` | `maxDepth` |
|---|---:|---|---:|---:|---:|
| `deltazero` | 0.0 | disabled | 0.0 | 0.5 | 0.5 |
| `deltasmall` | 0.3 | disabled | 0.0 | 0.65 | 0.35 |
| `deltaone` | 1.0 | disabled | 0.0 | 1.0 | 0.0 |
| `deltaone_bias_clamp_neg` | 1.0 | enabled | -0.003 | 1.0 | 0.0 |
| `deltasmall_bias_clamp_pos` | 0.3 | enabled | 0.003 | 0.65 | 0.35 |
| `depth_range_unrestricted` | 2.7 | disabled | 0.0 | 1.85 | -0.85 |

The `depth_range_unrestricted` depth oracle has an unresolved source-level limitation. `VK_EXT_depth_range_unrestricted` removes the `[0,1]` restriction from the viewport endpoints, but the specification still makes a fragment depth outside `[0,1]` undefined after depth clamping and range adjustment when the attachment is fixed-point. This test nevertheless uses `VK_FORMAT_D16_UNORM` and compares a deterministically saturated depth reference for such pixels. The color observation remains useful, but a depth-only mismatch on those outside-range pixels cannot by itself establish a conformance failure.

## Behavior Parameters

The primary behavioral axis is the `depthclamp`/`nodepthclamp` prefix of each test case leaf. The remaining suffix selects the range and bias variation without changing whether z clipping or depth clamping handles out-of-range depth.

### `depthclamp`: disable z clipping and clamp fragment depth

The pipeline sets `depthClampEnable = VK_TRUE`, which disables z clipping for this pipeline. Triangle regions with clip-space z outside the clip volume can therefore reach rasterization, and the later depth operation clamps mapped fragment depth to the smaller and larger viewport endpoints. This value requires `DEVICE_CORE_FEATURE_DEPTH_CLAMP`.

### `nodepthclamp`: retain z clipping and disable depth clamping

The pipeline sets `depthClampEnable = VK_FALSE`, so z clipping remains enabled and portions of the triangle beyond the clip-volume depth boundaries do not reach rasterization. The reference includes only in-range triangle samples and masks depth comparisons near `0.0` and `1.0`, where rasterization rounding can make boundary coverage ambiguous.

## Shader Analysis

The test uses two small inline GLSL 4.50 shaders. No shader-side buffer or generated SPIR-V artifact is checked into the repository; the CTS compiles the source strings during test setup.

### Vertex shader

The vertex shader declares `layout(location = 0) in highp vec4 in_position` and assigns it directly to `gl_Position`. The three vertices therefore provide controlled clip-space positions and depth values. It does not perform a depth-range calculation; viewport mapping remains fixed-function state.

### Fragment shader

The fragment shader writes:

```glsl
out_color = vec4(gl_FragCoord.z, 0.5, 0.5, 1.0);
```

The red component records the mapped, interpolated fragment depth visible to fragment shading before the later depth-bias and depth-attachment operations. The host compares this color image with a reference made from barycentric interpolation and the selected viewport range. A separate depth reference applies the depth-only bias and storage rules, so the two checks cover different points in the graphics path.

## Runtime Execution and Result Checking

- The instance creates color and depth images, image views, a `VK_FORMAT_D16_UNORM` depth attachment, a framebuffer/render pass when required, and a graphics pipeline. The pipeline enables depth testing and writing, dynamic viewport state, and the selected rasterizer depth-clamp and depth-bias state. Its depth comparison is `VK_COMPARE_OP_ALWAYS`, so every fragment that reaches depth comparison passes and writes its depth.
- It clears both targets, inserts transfer-to-attachment memory barriers, sets a viewport with the selected `minDepth` and `maxDepth`, binds the vertex buffer and pipeline, and issues `vkCmdDraw(cmdBuffer, 3, 1, 0, 0)`.
- Render-pass and dynamic-rendering recording are selected by shared group parameters. In the partial-secondary path the primary command buffer owns the rendering scope; in the complete-secondary path the secondary command buffer owns it. Both secondary paths record the draw in the secondary command buffer and execute it from the primary command buffer.
- After submission and a wait, the test reads both attachments back to the host. For color, `generateReferenceImage` interpolates the three vertex depths, clamps to `[0,1]`, and applies the viewport mapping without depth bias. For depth, it first applies the selected bias, then performs that clamp and mapping, optionally clamps to the viewport endpoint range, and converts the reference through a saturating unsigned-normalized depth format.
- Color uses `tcu::fuzzyCompare` with threshold `0.02f`. Depth compares every unmasked pixel against `kDepthThreshold = 0.0064f`; a failure logs result, reference, and an error mask. Either aspect failing returns `Result images are incorrect`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `depthclamp` | Incorrect inverted viewport-depth mapping, depth clamping of out-of-range fragments, depth-bias handling, attachment writes, or image readback/comparison. |
| `nodepthclamp` | Incorrect inverted viewport-depth mapping, z clipping at the clip-volume boundaries, depth-bias handling, attachment writes, or masked depth comparison. |

### Cause Analysis

#### Inverted viewport-depth mapping

**Possible failure symptoms:** The red channel and depth attachment disagree with the reference across the triangle, especially when `deltasmall` or `deltaone` reverses the expected depth ordering.

**Possible implementation causes:** The implementation may apply `minDepth` and `maxDepth` in the wrong order, use the wrong normalized-depth value, or mishandle endpoint values. The observed image cannot distinguish viewport-state interpretation from later rasterization or attachment behavior, so the exact fault requires source-level investigation.

#### Depth-clamp and boundary handling

**Possible failure symptoms:** A `depthclamp` result is missing triangle regions outside the clip volume or stores values inconsistent with endpoint clamping, or a `nodepthclamp` result has extra or missing coverage near normalized depth boundaries. Boundary masking applies only to the depth comparison; the color comparison can still report coverage differences there.

**Possible implementation causes:** The implementation may incorrectly couple `depthClampEnable` to z clipping, apply fragment-depth clamping at the wrong stage, or make an incorrect boundary-coverage decision. These symptoms involve primitive clipping, rasterization, and fragment operations as well as depth storage; they are not proof of a shader defect.

#### Depth bias and inverted ranges

**Possible failure symptoms:** Only `deltaone_bias_clamp_neg` or `deltasmall_bias_clamp_pos` fails, with the depth attachment consistently offset while the color result remains correct, or with both independently generated comparisons failing.

**Possible implementation causes:** The implementation may use the wrong depth-bias slope or clamp rule, or mishandle the sign conversion needed to express a post-viewport depth offset in the reference's pre-viewport coordinate. A failing comparison still requires investigation across rasterizer state, depth mapping, and stored attachment values.

#### Unrestricted depth range

**Possible failure symptoms:** `depth_range_unrestricted` fails while in-range leaves pass, with errors associated with mapped values outside the ordinary `[0,1]` viewport endpoints.

**Possible implementation causes:** A color mismatch, or a depth mismatch where the mapped fragment depth remains in `[0,1]`, may indicate incorrect viewport transformation or fragment-depth handling on the `VK_EXT_depth_range_unrestricted` path. A depth-only mismatch for mapped values outside `[0,1]` cannot be assigned to the implementation: with the fixed-point `VK_FORMAT_D16_UNORM` attachment, the specification makes those fragment depths undefined while the CTS reference assumes saturating conversion.

#### Shared rendering and result checking

**Possible failure symptoms:** Several leaves fail in the same recording mode, or both color and depth comparisons show broad differences unrelated to one depth parameter.

**Possible implementation causes:** The problem may be in command-buffer recording, dynamic-rendering or render-pass setup, attachment transitions, readback, or the host comparison path. Investigation is needed before assigning such a failure to inverted-depth arithmetic.

## Case Pruning

### Requirement-based pruning

- `depthclamp` requires `DEVICE_CORE_FEATURE_DEPTH_CLAMP`.
- Bias leaves with nonzero `depthBiasClamp` require `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP`.
- `depth_range_unrestricted` requires `VK_EXT_depth_range_unrestricted` because its viewport endpoints are outside `[0,1]`; that extension does not make outside-`[0,1]` fragment depth defined for this fixed-point depth attachment.
- Dynamic-rendering variants require `VK_KHR_dynamic_rendering`.

### Design-based pruning

- The source uses six depth leaves for each of the two depth-clamp families. It does not generate every possible combination of depth span, bias factor, and clamp value.
- The triangle, target formats, depth compare state, and draw count remain fixed so the comparisons isolate viewport depth-range behavior.
- The no-clamp reference masks only boundary pixels that may differ because of coverage rounding; this is a comparison design choice, not a skipped test case.

## Key Takeaways

- The test checks inverted viewport mapping twice: `gl_FragCoord.z` in color and the stored value in the depth attachment.
- `depthclamp` and `nodepthclamp` are the primary behavior values; the six suffixes add equal, small, full, unrestricted, and bias-clamped range variants.
- A rendered-image failure covers the complete path from command interpretation and vertex/rasterization through fragment operations, attachment writes, readback, and comparison. It does not by itself identify a shader-only fault.
- `depth_range_unrestricted` is feature-gated, but its fixed-point depth oracle is not defined by the specification for mapped fragment depths outside `[0,1]`; only its defined-domain results can support a conformance conclusion.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `InvertedDepthRangesTestInstance::createPipeline` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L237-L310) | Defines dynamic viewport, depth testing, depth clamp, bias, attachments, and rendering-mode state. |
| `InvertedDepthRangesTestInstance::generateReferenceImage` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L363-L457) | Defines interpolation, bias, inverted mapping, endpoint clamping, fragment inclusion, and masking. |
| `InvertedDepthRangesTest::initPrograms` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L665-L710) | Defines the inline vertex and `gl_FragCoord.z` fragment shaders. |
| `InvertedDepthRangesTestInstance::iterate` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L502-L663) | Records commands, submits work, reads attachments, compares results, and reports pass/fail. |
| `InvertedDepthRangesTest::checkSupport` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L712-L726) | Defines feature and extension requirements. |
| `populateTestGroup` | [`vktDrawInvertedDepthRangesTests.cpp`](../../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L737-L782) | Defines the exact registered family and leaf identifiers. |
| Draw dispatcher | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) | Registers render-pass and non-nested dynamic-rendering paths and omits this family from nested-secondary paths. |
| Mustpass leaves | [`complete_secondary_cmd_buff`](../../../mustpass/main/vk-default/draw.txt#L1109-L1120), [`partial_secondary_cmd_buff`](../../../mustpass/main/vk-default/draw.txt#L3523-L3534), [`primary_cmd_buff`](../../../mustpass/main/vk-default/draw.txt#L7146-L7157), [`renderpass`](../../../mustpass/main/vk-default/draw.txt#L19633-L19644) | Confirms all four registered roots and their twelve leaves. |
| Unsigned-normalized reference conversion | [`tcuTexture.cpp`](../../../../../framework/common/tcuTexture.cpp#L2225-L2258) | Shows that the host depth reference conversion saturates fixed-point values. |
| `VK_FORMAT_D16_UNORM` representation | [`formats.adoc`](../../../../vulkan-docs/src/chapters/formats.adoc#L478-L479) | Defines the attachment as a 16-bit unsigned-normalized depth format. |
| Viewport transform and endpoint validity | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L1899-L1946) | Defines inverted endpoint ordering and the viewport depth transform. |
| Depth clipping and depth-clamp coupling | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L957-L1003) | Defines how `depthClampEnable` controls depth clipping for this pipeline. |
| Depth clamping and fixed-point range adjustment | [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L1859-L1903) | Defines endpoint clamping and makes outside-`[0,1]` fixed-point fragment depth undefined. |
| Unrestricted-depth extension scope | [`VK_EXT_depth_range_unrestricted.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_depth_range_unrestricted.adoc#L15-L49) | Removes viewport endpoint restrictions but preserves fragment-depth rules. |
