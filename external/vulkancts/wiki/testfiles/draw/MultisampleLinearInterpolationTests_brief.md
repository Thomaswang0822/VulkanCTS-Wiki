## One-Sentence Test Purpose

This test checks whether multisample `noperspective` interpolation at explicit offsets and sample positions produces the same colors as a fragment-coordinate reference, including the boundary offsets allowed by the interpolation functions.

## Background Knowledge

### Linear interpolation and explicit positions

A fragment input normally uses perspective-correct interpolation. `noperspective` selects linear interpolation instead. `interpolateAtOffset` evaluates an input at an offset from the fragment position, while `interpolateAtSample` evaluates it at a selected sample. The test uses sample-rate shading because the shader reads `gl_SampleID` and `gl_SamplePosition`.

Why it matters here:

- The reference shader turns `gl_FragCoord` plus the selected offset into a color.
- The tested shader must produce the same value from a `noperspective` varying at that position.
- A sample-position conversion of `gl_SamplePosition - vec2(0.5)` provides a second, in-shader equivalence check.

### Multisample render and resolve

For a sample count above one, the test renders to a multisample color attachment and resolves it into a single-sample image. The host compares the resolved reference and tested images. For one sample, the single-sample attachment is written directly.

Why it matters here:

- The same image-comparison rule covers the one-sample and multisample cases.
- The selected sample count changes the positions at which the shader can observe interpolation.

## One Concrete Example

Consider `dEQP-VK.draw.renderpass.linear_interpolation.offset_min_4_samples`.

The case passes `vec2(-0.5)` to `interpolateAtOffset` and renders with four samples per pixel. The reference fragment shader computes a red/green color from `gl_FragCoord` shifted by the same offset. The tested fragment shader reads the `noperspective` color at that offset and at `gl_SampleID`, averages the two results, and divides by the interpolation range. Both draws use vertex positions and colors selected so that the result draw covers a square while the reference draw clips to the viewport. Their resolved 16 x 16 images must agree within the host threshold.

## End-to-End Test Flow

```text
[host] select one offset family and one supported sample-count test case leaf
[host] generate reference and noperspective vertex/fragment shader pairs
[host] create one single-sample color target per draw and, for MSAA, one multisample attachment per draw
[host] build the graphics pipeline and upload six position/color vertices
[host] record either render-pass or dynamic-rendering commands, optionally through a secondary command buffer
[device] render the fragment-coordinate reference image
[device] render the noperspective interpolation image and run the sample-position consistency check
[device] resolve multisample output when applicable
[host] read both single-sample images and compare them with a per-channel threshold of 0.005
```

## Generated Test Artifacts and Bound Resources

### Generated program artifacts

`initPrograms` builds two shader pairs. `vertRef` and `fragRef` pass an ordinary color varying and compute the expected color from `gl_FragCoord` plus the selected offset. `vertNoPer` decorates its output with `noperspective`; `fragNoPer` uses `interpolateAtOffset` and `interpolateAtSample` on the matching input. The source inserts the case-specific offset, render size, and interpolation range into the generated GLSL.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Position/color vertex buffer | yes | yes | read by the vertex shader | no | Supplies the two-triangle geometry and colors that expose interpolation position. |
| Single-sample color target, per draw | yes | color attachment | written by fragment output | yes | Holds the reference or tested image used for the final comparison. |
| Multisample color target, per draw | for sample counts above one | color attachment | written before resolve | no | Stores per-sample fragment results before average resolve. |
| Graphics pipeline and shader modules | yes | yes | executes vertex and fragment shaders | no | Selects the reference or `noperspective` path. |

## What Is Checked

- The host compares the two readback images with `tcu::floatThresholdCompare` and a `tcu::Vec4(0.005f)` threshold. A mismatch fails the test.
- The tested fragment shader compares `interpolateAtSample(in_color, gl_SampleID)` with `interpolateAtOffset(in_color, gl_SamplePosition - vec2(0.5))`. If all four component differences exceed `0.000001`, it sets the output blue component to `1.0`, causing the image comparison to expose the discrepancy.

## Behavior Parameter Identification

> **Behavior parameter:** interpolation position family
>
> **Candidate values:** `no_offset`, `offset_min`, `offset_max`

The sample-count test case leaf changes the multisample configuration used to observe the same interpolation-position behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_offset` | Incorrect `noperspective` interpolation at the fragment position, incorrect `interpolateAtSample` result, or a shared render/readback comparison defect. |
| `offset_min` | Incorrect handling of the `(-0.5, -0.5)` explicit interpolation offset, or a shared interpolation, resolve, or comparison defect. |
| `offset_max` | Incorrect handling of the `(0.4375, 0.4375)` explicit interpolation offset, or a shared interpolation, resolve, or comparison defect. |

## Important Variations and Special Cases

- Each position family registers `1_sample`, `2_samples`, `4_samples`, `8_samples`, `16_samples`, `32_samples`, and `64_samples` under render-pass and primary-command-buffer dynamic-rendering paths.
- Dynamic-rendering paths that use a secondary command buffer stop after `4_samples`; this is an intentional test-count reduction, not an unsupported interpolation rule.
- Every case requires `sampleRateShading` and a selected count in `framebufferColorSampleCounts`. Dynamic-rendering cases also require `VK_KHR_dynamic_rendering`. On a portability-subset implementation, the test skips when `shaderSampleRateInterpolationFunctions` is unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Generated reference and tested shaders | [initPrograms](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L550-L641) | Defines the two interpolation paths and the in-shader consistency check. |
| Attachment setup, rendering, readback, and comparison | [iterate](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L69-L516) | Creates the images and pipelines, selects render-pass or dynamic rendering, and decides pass or fail. |
| Support checks | [checkSupport](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L643-L662) | Defines feature, sample-count, dynamic-rendering, and portability-subset requirements. |
| Registered offsets and sample counts | [createTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L670-L704) | Defines the test matrix and secondary-command-buffer cutoff. |
| Registration entry point | [createMultisampleLinearInterpolationTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L708-L713) | Registers the `linear_interpolation` test family. |
| Vulkan interpolation decorations | [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2921) | Grounds the `NoPerspective` interpolation rule and interpolation-position context. |

## Questions / Risk Points for User Audit

- Does the distinction between the host image comparison and the shader's sample-position consistency check read clearly?
- Does the brief make clear that the offset family is the primary behavioral axis while sample count configures observation?
- Does the explanation of dynamic-rendering secondary-command-buffer pruning avoid implying a feature limitation?
- Is a generated-shader summary sufficient for the final page, or should a later shader-analysis workflow add a compiler-produced walkthrough and SPIR-V output?

## Conversion Notes for Final Wiki Rewrite

- Keep `no_offset`, `offset_min`, and `offset_max` as the behavior parameters and copy the failure-cause table unchanged.
- Retain the compact prerequisite list on `noperspective` interpolation and multisample resolve.
- Keep `## Shader Analysis` as a source-grounded generated-shader summary unless a separate shader-analysis workflow can provide a compiler-produced walkthrough with SPIR-V output.
- Preserve the two-layer validation explanation: image comparison provides the CTS result, and the blue-channel write makes the in-shader equivalence check observable.
