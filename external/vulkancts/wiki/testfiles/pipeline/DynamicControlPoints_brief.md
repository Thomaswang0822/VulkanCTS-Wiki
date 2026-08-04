# Understanding Brief: DynamicControlPoints

## One-Sentence Test Purpose

This test checks whether a graphics pipeline uses the command-buffer value from `vkCmdSetPatchControlPointsEXT` when switching between tessellation pipelines and changing patch output or winding behavior.

## Background Knowledge

### Dynamic tessellation patch state

Tessellation control shaders process an input patch, and `patchControlPoints` determines the number of control points in that input patch. With `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT`, the pipeline does not supply this state statically for drawing. The command buffer must set it before drawing. The Vulkan specification requires a value greater than zero and no greater than `maxTessellationPatchSize`.

### Tessellation winding and culling

The tessellation evaluation shader declares a triangle winding order. Rasterization culling then determines whether the generated triangle is discarded. This test changes winding between two pipeline draws while keeping the dynamic patch state command in the same command buffer.

## One Concrete Example

A representative `change_output_winding` case creates two pipelines with dynamic patch control points. The first uses a three-vertex tessellation-control output and counter-clockwise evaluation; the second uses four output vertices and clockwise evaluation. The command buffer sets three patch control points, draws with the first pipeline, switches to the second pipeline, and draws again. The two pipelines render into left and right halves of a 4 x 4 color image.

## End-to-End Test Flow

```text
[host] choose a pipeline construction type and one registered behavior configuration
[host] create a 4 x 4 color attachment, framebuffer, host-visible readback buffer, and two graphics pipelines
[host] compile the generated vertex, tessellation-control, tessellation-evaluation, and fragment programs
[host] record a render pass, set patch control points to 3, bind pipeline 1, draw, bind pipeline 2, and draw
[device] execute tessellation and rasterization for both draws
[host] copy the color image to the readback buffer, wait for completion, and compare the image with the expected halves
[host] return failure if any pixel differs; otherwise return pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The implementation generates six GLSL programs. The vertex shader supplies six fullscreen-quad vertices. The first tessellation-control shader outputs three vertices. The optional second tessellation-control shader outputs four and gives its fourth vertex a sentinel position. The evaluation shaders use `gl_TessCoord` to combine the input positions and select the configured winding. The fragment shader writes magenta. These programs isolate dynamic patch state and culling; the test does not inspect shader-generated data directly.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| 4 x 4 color attachment | yes | yes | written by both draws | yes, through a copy | Contains the observable result. |
| Image view and framebuffer | yes | yes | used by the render pass | no | Define the color target. |
| Host-visible output buffer | yes | as transfer destination | written by the image copy | yes | Supplies pixels for CTS comparison. |
| Graphics pipeline 1 and pipeline 2 | yes | bound in turn | execute tessellation and fragment stages | no | Differ in output count and/or winding according to the leaf. |

## What Is Checked

- The expected image contains `expectedFirst` in the left half and `expectedSecond` in the right half.
- The host invalidates the readback allocation and calls `tcu::floatThresholdCompare` with zero tolerance.
- A mismatch returns `Color output does not match reference, image added to log`; a matching image returns `Pass`.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `change_output`, `change_winding`, `change_output_winding`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `change_output` | Dynamic patch-control-point state is not applied when the pipeline changes, or tessellation output and image validation are incorrect. |
| `change_winding` | Dynamic patch state, tessellation winding, culling, or image validation is incorrect. |
| `change_output_winding` | The combined patch-output and winding transition is handled incorrectly, or the rendered image validation is incorrect. |

## Important Variations and Special Cases

- `change_output` sets `changeOutput` and uses no culling. The second pipeline emits four control points and its evaluation shader uses the fourth point's sentinel position to produce the expected right half.
- `change_winding` keeps three control points but changes evaluation-shader winding and enables front-face culling.
- `change_output_winding` combines both changes.
- Every construction variant uses the same three behavior leaves. Device support is checked for tessellation shaders, the selected pipeline construction type, and `extendedDynamicState2PatchControlPoints`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test registration | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) | Registers the three leaves and their configurations. |
| Support checks | [`DynamicControlPointsTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L116-L126) | Defines feature and construction prerequisites. |
| Program generation | [`DynamicControlPointsTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L235) | Defines the tessellation and fragment behavior. |
| Execution and comparison | [`DynamicControlPointsTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L263-L426) | Records both draws and compares the copied image. |
| Dynamic-state contract | [`vkCmdSetPatchControlPointsEXT`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2588-L2630) | Defines command timing, pipeline dynamic-state use, and valid values. |

## Questions / Risk Points for User Audit

- The final page treats the test case leaf as the primary behavioral axis. Confirm that this is preferable to treating the three leaves as a combined output/winding matrix.
- The final image comparison observes the rendered result, not the internal tessellation-control invocation count. Failure localization is therefore limited to the operation shape described by each leaf.

## Conversion Notes for Final Wiki Rewrite

Use the three leaf names as `Behavior Parameters` subsections and copy the failure-cause table directly. Keep shader discussion concise because the generated programs support the fixed-function transition but the pass/fail result is the host-side color-image comparison. Preserve the exact construction roots and per-file mustpass evidence in the final page.
