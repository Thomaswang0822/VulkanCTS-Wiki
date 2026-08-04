## Overview

**Core question:** Does a two-pipeline tessellation sequence render the expected image when one dynamic patch-control-point value is set before both draws?

- [`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1) implements the `dynamic_control_points` test family for each supported pipeline construction path.
- Each test case records one `vkCmdSetPatchControlPointsEXT(..., 3)` command, then draws with two tessellation pipelines into separate halves of a color image.
- The three test case leaves vary whether the second pipeline changes tessellation-control output, tessellation-evaluation winding, or both. The copied image is compared with a two-color reference.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Dynamic patch-control-point state.** A tessellation-control invocation consumes an input patch and produces one output control point. The patch's input-control-point count can be supplied by [`vkCmdSetPatchControlPointsEXT`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2588-L2630) for subsequent draws when the pipeline declares `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT`. The command value must be greater than zero and at most `maxTessellationPatchSize`.
- **Dynamic-state precedence.** When `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` is in the pipeline dynamic-state list, the static `VkPipelineTessellationStateCreateInfo::patchControlPoints` value is ignored and the command buffer must set the state before drawing, as specified in [the graphics-pipeline dynamic-state rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6148).
- **Winding and culling.** A tessellation-evaluation shader can declare clockwise or counter-clockwise triangle winding. With front-face culling enabled, changing that declaration can make one draw disappear while the opposite winding remains visible.

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_control_points
├── change_output
├── change_winding
└── change_output_winding
```

[`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) registers this concrete monolithic root. The same three leaves occur in seven Vulkan-default mustpass construction files: `monolithic/monolithic.txt`, `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-spirv.txt`, `shader-object-linked-binary.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`, for 21 entries total.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `change_output`, `change_winding`, `change_output_winding` | Selects the output-count transition, winding transition, or their combination. | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) |
| Pipeline construction path | monolithic, pipeline library, fast linked library, and four shader-object paths represented in Vulkan-default mustpass | Reuses the same leaf configurations through each supported construction form. | mustpass files named above |
| Second tessellation-control output | three or four vertices | Four vertices add a sentinel fourth output point; the second evaluation shader reads it only when `changeOutput` is true. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L193-L234) |
| Evaluation-shader winding | `ccw` or `cw` | Controls the orientation used by rasterization and therefore the culling result. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L176-L191) |
| Cull mode | `VK_CULL_MODE_NONE` or `VK_CULL_MODE_FRONT_BIT` | Leaves that change winding use front-face culling to make the orientation observable in the color target. | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L435-L457) |
| Dynamic patch control points | 3 | The command buffer sets the input patch size once before both draws. | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L389-L408) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf selects a different transition between the two pipeline draws while preserving the same command-buffer dynamic patch-control-point setting.

### change_output: change tessellation-control output count

The first pipeline emits three output control points and the second emits four. The second evaluation shader reads its fourth control point, which the control shader assigns a sentinel position. Both halves should be magenta because culling is disabled.

### change_winding: change tessellation-evaluation winding

Both pipelines keep three control points, but their evaluation shaders use opposite winding declarations. Front-face culling should remove the first draw and retain the second, producing white on the left and magenta on the right.

### change_output_winding: change output count and winding

This leaf combines the four-output second pipeline with the winding reversal and front-face culling. It checks the transition in which both tessellation output and culling-visible orientation differ between the draws.

## Shader Analysis

The source generates vertex, tessellation-control, tessellation-evaluation, and fragment GLSL programs, but the shader text is supporting instrumentation rather than an independently varied behavior. The host changes no shader input after program creation. It records one dynamic patch-control-point command and observes the effect through a color-image comparison, so a representative shader walkthrough and embedded SPIR-V disassembly would not clarify the tested contract.

## Runtime Execution and Result Checking

- The test requires `tessellationShader`, the selected pipeline construction requirements, and `extendedDynamicState2PatchControlPoints` before execution.
- It creates a 4 x 4 `VK_FORMAT_R8G8B8A8_UNORM` color attachment, render pass, framebuffer, and a host-visible transfer-destination buffer. Two graphics pipeline wrappers use patch-list topology and `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT`.
- The first pipeline writes the left half and the second writes the right half. The command buffer begins the render pass, calls `cmdSetPatchControlPointsEXT` with 3, binds and draws the first pipeline, then binds and draws the second pipeline.
- After the render pass, the command buffer copies the color image to the buffer, submits, and waits. The host invalidates the allocation and compares all pixels against a reference whose left and right halves come from `expectedFirst` and `expectedSecond`.
- `tcu::floatThresholdCompare` uses a zero threshold. Any mismatch fails the leaf; otherwise it passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `change_output` | Dynamic patch-control-point state is not applied when the pipeline changes, or tessellation output and image validation are incorrect. |
| `change_winding` | Dynamic patch state, tessellation winding, culling, or image validation is incorrect. |
| `change_output_winding` | The combined patch-output and winding transition is handled incorrectly, or the rendered image validation is incorrect. |

### Cause Analysis

#### Dynamic patch state or tessellation-output transition

**Possible failure symptoms:** `change_output` or `change_output_winding` produces pixels that differ from its expected magenta or white/magenta halves. The comparison log includes the failed image.

**Possible implementation causes:** the implementation may fail to apply the recorded dynamic patch-control-point count to a later draw, retain incompatible patch state across the pipeline bind, or execute the tessellation-control and evaluation stages inconsistently when the second pipeline uses four output vertices. The image result cannot distinguish these paths from a downstream rasterization or copyback defect without source-level investigation.

#### Winding and culling transition

**Possible failure symptoms:** `change_winding` or `change_output_winding` renders the wrong half, culls the wrong draw, or returns colors different from the expected white-left and magenta-right image.

**Possible implementation causes:** the implementation may apply the tessellation-evaluation winding declaration incorrectly, classify front faces incorrectly after tessellation, or fail to preserve the selected dynamic patch state while binding the second pipeline. The test observes the combined result of tessellation, rasterization, and color copyback, so it does not isolate one stage.

#### Image copyback or comparison handling

**Possible failure symptoms:** any leaf reports a mismatch even when the command sequence completes.

**Possible implementation causes:** the implementation may mishandle color-attachment writes, the image-to-buffer copy, or visibility of copied pixels to the host. The CTS code invalidates the host-visible allocation before comparison; source-level investigation is needed to separate readback handling from rendering when only the final image differs.

## Case Pruning

### Requirement-based pruning

The source reports the case as not supported unless the device exposes `tessellationShader` and `extendedDynamicState2PatchControlPoints`, and unless the selected pipeline construction type meets its requirements. The command's valid patch-control-point range is constrained by the Vulkan limit described in [the tessellation command rules](../../../../vulkan-docs/src/chapters/shaders.adoc#L2619-L2628).

### Design-based pruning

The family fixes the dynamic count at three and uses exactly two draws. The pipeline wrapper's default static tessellation state also contains three patch control points, although that field must be ignored for these dynamically configured pipelines. Consequently, the image oracle checks the two-draw sequence with dynamic state set, but it cannot distinguish correct dynamic-state precedence from an implementation that incorrectly uses the same-valued static field. The family does not enumerate other legal patch sizes or cull modes; its three leaves cover output change, winding change, and their combination.

## Key Takeaways

- `dynamic_control_points` tests draw-time patch-control-point state across a two-pipeline tessellation sequence.
- Because both the dynamic command and the otherwise ignored static field contain three, passing does not independently prove dynamic-over-static precedence.
- `change_output` makes the second pipeline's fourth control point visible through a sentinel-derived magenta result.
- `change_winding` and `change_output_winding` make the transition observable through front-face culling and the white-left, magenta-right reference image.
- A failure proves that the final rendered image does not match the configured transition, but it does not by itself isolate tessellation, rasterization, transfer, or host-readback handling. See [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Pipeline-category registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L113) | Adds this family for each pipeline construction path. |
| Family registration | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) | Defines all leaf configurations and expected colors. |
| Support checks | [`DynamicControlPointsTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L116-L126) | Requires tessellation and dynamic patch-control-point support. |
| Program generation | [`DynamicControlPointsTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L235) | Builds the tessellation programs and the output/winding variants. |
| Command recording and validation | [`DynamicControlPointsTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L263-L426) | Creates both pipelines, records the dynamic state and draws, and compares the copied image. |
| Vulkan dynamic-state contract | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2588-L2630) | Specifies command behavior, required feature, and valid range. |
| Pipeline-state precedence | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6148) | Specifies that dynamic patch-control-point state replaces the static field. |
