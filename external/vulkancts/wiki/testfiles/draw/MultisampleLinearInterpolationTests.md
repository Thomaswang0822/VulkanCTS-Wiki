## Overview

**Core question:** Does a `noperspective` fragment input produce the expected linear value when `interpolateAtOffset` and `interpolateAtSample` select positions in a multisample fragment?

- This page covers the `linear_interpolation` test family implemented by [vktDrawMultisampleLinearInterpolationTests.cpp](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp).
- Each test case draws a `gl_FragCoord`-based reference and a `noperspective` result, then compares their single-sample images.
- The family varies explicit interpolation position and multisample count. The result shader also attempts to check whether the selected sample can be expressed as an offset from the pixel center.
- The source registers this family under the render-pass path and under supported dynamic-rendering command-buffer paths through the draw dispatcher.

## Background Knowledge

- A fragment input with `noperspective` uses linear rather than perspective-correct interpolation. The Vulkan specification describes this as the `NoPerspective` decoration for line and triangle interpolation.
- `interpolateAtOffset` selects an input value at an offset from the pixel center. `interpolateAtSample` selects it at a sample identified by `gl_SampleID`; `gl_SamplePosition - vec2(0.5)` expresses that sample position as an offset from the pixel center.
- A multisample color attachment stores values per sample. The test resolves it to a single-sample image before host readback, so each result can use one image-comparison path.

## Registration Hierarchy

```text
draw.renderpass.linear_interpolation
├── no_offset_1_sample
├── no_offset_2_samples
├── no_offset_4_samples
├── no_offset_8_samples
├── no_offset_16_samples
├── no_offset_32_samples
├── no_offset_64_samples
├── offset_min_1_sample
├── offset_min_2_samples
├── offset_min_4_samples
├── offset_min_8_samples
├── offset_min_16_samples
├── offset_min_32_samples
├── offset_min_64_samples
├── offset_max_1_sample
├── offset_max_2_samples
├── offset_max_4_samples
├── offset_max_8_samples
├── offset_max_16_samples
├── offset_max_32_samples
└── offset_max_64_samples
```

The same offset/sample matrix appears under `draw.dynamic_rendering.primary_cmd_buff.linear_interpolation` and the supported partial and complete secondary-command-buffer paths. Render-pass and primary-command-buffer dynamic-rendering paths register all seven sample counts. Dynamic-rendering secondary-command-buffer paths register only `1_sample`, `2_samples`, and `4_samples`. The dispatcher deliberately does not add this family to the nested-secondary groups.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interpolation position | `no_offset`, `offset_min`, `offset_max` | Selects `(0.0, 0.0)`, `(-0.5, -0.5)`, or `(0.4375, 0.4375)` for `interpolateAtOffset` and changes the reference calculation by the same offset. | [createTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L670-L704) |
| Sample count | `1_sample`, `2_samples`, `4_samples`, `8_samples`, `16_samples`, `32_samples`, `64_samples` | Selects the rasterization sample count and whether the result uses a multisample attachment plus resolve. | [createTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L682-L701) |
| Recording path | render pass; dynamic rendering through primary, partial-secondary, or complete-secondary command buffers | Exercises the same image result through the draw category's supported recording configurations. Secondary dynamic-rendering paths reduce the registered sample-count range. | [iterate](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L156-L223), [dynamic-rendering recording](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L341-L501) |

## Behavior Parameters

The interpolation-position family is the primary behavioral axis. Sample count changes the multisample observation configuration but does not change the property under test.

### no_offset: Pixel-center interpolation

`no_offset` passes `(0.0, 0.0)` to `interpolateAtOffset`. It checks the baseline relation between the linearly interpolated varying, the current sample value, and the reference color produced from unshifted `gl_FragCoord`.

### offset_min: Required negative endpoint

`offset_min` passes `(-0.5, -0.5)`, the minimum endpoint every conformant implementation supporting the feature must accept. The reference shader applies the same shift to `gl_FragCoord`, so the expected image is shifted by the same amount. The test does not query the device's actual `minInterpolationOffset`, which may support a wider range.

### offset_max: Conservatively portable positive endpoint

`offset_max` passes `(0.4375, 0.4375)`. This is the largest positive endpoint implied by Vulkan's minimum guaranteed four fractional interpolation-offset bits (`0.5 - 1/16`), so it is valid on every conformant implementation supporting the feature. It is not necessarily the device's actual `maxInterpolationOffset`, which the test does not query.

## Shader Analysis

`initPrograms` generates two GLSL shader pairs rather than storing fixed shader files.

- `vertRef` writes an ordinary color varying. `fragRef` computes its output from `gl_FragCoord`, the selected offset, and the 16 x 16 render size.
- `vertNoPer` declares `noperspective out vec4 out_color`; `fragNoPer` receives the matching `noperspective` input and averages `interpolateAtOffset(in_color, offset)` with `interpolateAtSample(in_color, gl_SampleID)`.
- The result shader attempts an additional consistency check by subtracting `interpolateAtOffset(in_color, gl_SamplePosition - vec2(0.5))` from the sample result. It writes `1.0` to blue only if **all four signed component differences** are greater than `0.000001`; it does not take absolute values or test components independently.
- In the generated color field, blue is zero and alpha is constant, so the blue and alpha differences are expected to be zero. Consequently, the conjunction cannot normally fire. The host image comparison, not this attempted blue-channel signal, is the effective pass/fail check.

## Runtime Execution and Result Checking

- The test creates two `VK_FORMAT_R8G8B8A8_UNORM` single-sample color targets, one for the reference draw and one for the `noperspective` draw. When the selected count exceeds one, each draw also gets a multisample color attachment that resolves into its single-sample target.
- A host-visible vertex buffer supplies six position/color vertices. Both draws cover the same normalized-device-coordinate square. For the tested draw, the two lower vertices use doubled clip-space `x`, `y`, and `w`; this preserves their NDC positions while making the clip-space setup different from the reference.
- For each draw, the test builds a graphics pipeline with the selected sample count, records the draw through a render pass or dynamic rendering, submits it, waits, and reads the single-sample target.
- `tcu::floatThresholdCompare` compares the two readback images with a per-channel threshold of `0.005`. CTS reports `Rendered color image is not correct` on a mismatch.
- Every case requires `sampleRateShading`. The selected count must appear in `framebufferColorSampleCounts`; dynamic-rendering paths require `VK_KHR_dynamic_rendering`. A portability-subset device also needs `shaderSampleRateInterpolationFunctions` when it advertises `VK_KHR_portability_subset`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_offset` | Incorrect `noperspective` interpolation at the explicit zero offset, incorrect `interpolateAtSample` result, or a shared render/readback comparison defect. |
| `offset_min` | Incorrect handling of the `(-0.5, -0.5)` explicit interpolation offset, or a shared interpolation, resolve, or comparison defect. |
| `offset_max` | Incorrect handling of the `(0.4375, 0.4375)` explicit interpolation offset, or a shared interpolation, resolve, or comparison defect. |

### Cause Analysis

#### Linear interpolation or sample-position evaluation

**Possible failure symptoms:** The reference and result images differ by more than the `0.005` threshold. Although the shader contains a blue-channel consistency branch, its four-component signed conjunction cannot normally trigger for this color field because blue and alpha differences are zero.

**Possible implementation causes:** The generated shaders require the implementation to apply `NoPerspective` linear interpolation to the fragment input and to evaluate the explicit offset or selected sample at the intended position. A defect in either evaluation can change the rendered color. The source-based test result does not identify a narrower implementation layer.

#### Portable endpoint handling

**Possible failure symptoms:** Only `offset_min` or `offset_max` cases fail, while `no_offset` succeeds; the mismatch occurs in the corresponding shifted color gradient.

**Possible implementation causes:** The result can indicate incorrect treatment of one of the portable endpoint offsets supplied to `interpolateAtOffset`. Source-level investigation is needed to distinguish offset-coordinate handling from other interpolation behavior.

#### Shared rendering, resolve, or comparison path

**Possible failure symptoms:** Multiple position families fail for the same sample-count or recording configuration, or their images differ without a position-specific pattern.

**Possible implementation causes:** The test shares attachment setup, pipeline configuration, command recording, resolve, readback, and float-threshold comparison across behavior families. A failure pattern shared by those families can require investigation of that common path as well as interpolation.

## Case Pruning

### Requirement-based pruning

The test skips a case when `sampleRateShading` is unavailable or when the selected count is absent from `framebufferColorSampleCounts`. Dynamic-rendering cases require `VK_KHR_dynamic_rendering`. A portability-subset implementation skips the test when it lacks `shaderSampleRateInterpolationFunctions`.

### Design-based pruning

When dynamic rendering records through a secondary command buffer, `createTests` stops after `4_samples`. The source makes this reduction to limit the number of secondary-command-buffer cases; it does not define a different interpolation behavior for higher counts.

## Key Takeaways

- The test checks `noperspective` explicit-position interpolation by comparing it with a `gl_FragCoord` reference that uses the same offset.
- `no_offset`, `offset_min`, and `offset_max` exercise zero and two conservatively portable endpoint offsets while sample count controls the multisample setting.
- The shader contains an attempted blue-channel comparison between `interpolateAtSample` and the equivalent sample-position offset, but its signed all-component condition cannot normally fire for the generated colors. The host image comparison determines the CTS result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Draw setup, render/resolve path, readback, and result comparison | [MultisampleLinearInterpolationTestInstance::iterate](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L69-L516) | Creates attachments and pipelines, records both draws, reads the images, and applies the final threshold. |
| Generated reference and result shaders | [MultisampleLinearInterpolationTestCase::initPrograms](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L550-L641) | Defines the `noperspective` input, explicit interpolation calls, reference color, and attempted blue-channel consistency check. |
| Support gates | [MultisampleLinearInterpolationTestCase::checkSupport](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L643-L662) | Checks feature, sample-count, dynamic-rendering, and portability-subset support. |
| Registered parameter matrix | [createTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L670-L704) | Defines names, offsets, sample counts, and secondary-command-buffer pruning. |
| Test-family registration | [createMultisampleLinearInterpolationTests](../../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L708-L713) | Registers `linear_interpolation`. |
| Draw dispatcher integration | [createChildren](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100) | Attaches this implementation family to eligible draw registration paths. |
| Vulkan interpolation semantics | [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2921) | Defines fragment-input interpolation and the `NoPerspective` linear-interpolation rule. |
| Vulkan interpolation-offset limits | [Interpolation offset limit definitions](../../../../vulkan-docs/src/chapters/limits.adoc#L685-L694), [minimum required values](../../../../vulkan-docs/src/chapters/limits.adoc#L6707-L6713), [range example](../../../../vulkan-docs/src/chapters/limits.adoc#L7274-L7280) | Establishes why `-0.5` and `0.4375` are portable without implying they equal every device's reported endpoints. |
| Vulkan mustpass membership | [draw.txt](../../../mustpass/main/vk-default/draw.txt#L1121-L1129) | Confirms the dynamic-rendering secondary leaves; the same file also lists primary and render-pass leaves. |
