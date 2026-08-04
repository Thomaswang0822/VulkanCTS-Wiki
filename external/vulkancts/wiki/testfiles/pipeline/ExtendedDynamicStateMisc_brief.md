# Understanding Brief: pipeline.extended_dynamic_state.misc

## One-Sentence Test Purpose

This test checks whether dynamic rasterization sample counts preserve sample-shading behavior when the count is supplied by `vkCmdSetRasterizationSamplesEXT`.

## Background Knowledge

### Rasterization samples and sample shading

`rasterizationSamples` selects the number of samples in the multisample color attachment. With `sampleShadingEnable` set, the fragment shader can execute per sample rather than only once per covered fragment. `minSampleShading` supplies the minimum fraction of samples that must be shaded.

Why it matters here:
- The test deliberately gives the pipeline a static sample-count value and then replaces it with a larger dynamic value.
- The fragment shader reads or increments observable data per invocation, allowing the host to distinguish fragment shading from sample shading.

### Dynamic pipeline state

`VK_DYNAMIC_STATE_RASTERIZATION_SAMPLES_EXT` moves the rasterization sample-count choice from pipeline creation to command recording. The command must set the state before the draw that depends on it. The test uses this state both with sample shading disabled and with a `minSampleShading` threshold that only requires multiple invocations after the dynamic value is applied.

## One Concrete Example

For `dynamic_sample_shading_static_1_dynamic_4`, the pipeline is created with `rasterizationSamples = VK_SAMPLE_COUNT_1_BIT`, `sampleShadingEnable = VK_TRUE`, and `minSampleShading = 1.0`. The command buffer then calls `vkCmdSetRasterizationSamplesEXT(..., VK_SAMPLE_COUNT_4_BIT)` before drawing. The fragment shader samples a flat-color texture and performs `atomicAdd` on a storage-buffer counter for every invocation. Four pixels must produce at least 16 counted invocations.

The `sample_shading_dynamic_sample_count` case uses two draws in a 2 x 2 render area. It dynamically selects four samples, renders one half without sample shading and the other half with sample shading, and checks both the resolved blue image and the two invocation counters.

## End-to-End Test Flow

```text
[host] select a pipeline construction type and, for the matrix family, a static/dynamic sample-count pair
[host] require extendedDynamicState3RasterizationSamples, fragment stores and atomics, and supported image sample counts
[host] create multisample and single-sample resolve images, buffers, descriptors, render pass, framebuffer, and pipeline
[host] generate vertex and fragment GLSL programs; the fragment program writes blue output and increments a storage-buffer counter
[host] record the draw and call vkCmdSetRasterizationSamplesEXT with the dynamic count before it
[device] rasterize the fullscreen quad and execute the fragment shader at the required sample frequency
[host] wait for completion, copy the resolve image to a host-visible buffer, invalidate allocations, and read counters
[host] compare the image with the exact blue reference and check the invocation-count lower bound or range
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `vert`: a generated fullscreen-quad vertex shader.
- `frag`: a generated fragment shader that either reads `gl_SampleID` and increments a counter or samples a flat-color texture and increments a counter.
- Pipeline state: a graphics pipeline whose static multisample state and dynamic-state list are selected by the test family.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Multisample color image | yes | framebuffer | written by color output | indirectly through resolve | Receives the dynamically selected sample count. |
| Single-sample resolve image | yes | framebuffer | written by resolve | yes | Supplies the exact blue-image comparison. |
| Storage-buffer counters | yes | descriptor set | atomically written by fragment invocations | yes | Exposes the number of fragment shader executions. |
| Flat-color sampled image | yes, matrix family | descriptor set | read by fragment shader | no | Keeps the color result independent of a direct shader constant. |

## What Is Checked

- The resolved color image must match the exact blue reference.
- In `sample_shading_dynamic_sample_count`, the no-sample-shading counter must remain within the allowed range, while the sample-shaded counter must reach the four-sample maximum for the tested half of the image.
- In each static/dynamic pair, the atomic counter must reach at least `pixelCount * floor(minSampleShading * dynamicCount)`. With the selected pairs, the dynamic count makes the minimum meaningful even when the static count would not.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `sample_shading_dynamic_sample_count`; `dynamic_sample_shading_static_1_dynamic_2`; `dynamic_sample_shading_static_1_dynamic_4`; `dynamic_sample_shading_static_1_dynamic_8`; `dynamic_sample_shading_static_1_dynamic_16`; `dynamic_sample_shading_static_2_dynamic_4`; `dynamic_sample_shading_static_2_dynamic_8`; `dynamic_sample_shading_static_2_dynamic_16`; `dynamic_sample_shading_static_4_dynamic_8`; `dynamic_sample_shading_static_4_dynamic_16`; `dynamic_sample_shading_static_8_dynamic_16`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_shading_dynamic_sample_count` | Incorrect dynamic rasterization-sample state, sample-shading execution, image resolve, or counter visibility. |
| `dynamic_sample_shading_static_<static>_dynamic_<dynamic>` | The dynamic count is not used for sample-shading evaluation, `minSampleShading` is mishandled, or the multisample image/counter result is incorrect. |

## Important Variations and Special Cases

- The first family is registered for monolithic, pipeline-library, fast-linked-library, and shader-object-unlinked-SPIR-V construction paths. It is also present in Vulkan SC's monolithic mustpass file, but the implementation reports unsupported there because the required dynamic state is excluded by `CTS_USES_VULKANSC`.
- The static/dynamic matrix is VK-only and excludes shader-object construction. It enumerates every ordered pair from sample counts 1, 2, 4, 8, and 16 where the dynamic count is larger, producing ten leaves.
- The source requires `VK_EXT_extended_dynamic_state3` feature `extendedDynamicState3RasterizationSamples`; the matrix additionally checks the format's supported sample counts.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Registration and matrix generation | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) | Defines both test families and all ten static/dynamic leaves. |
| Basic dynamic-count test | [`sampleShadingWithDynamicSampleCount()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L91) | Builds the two-draw sample-shading check and validates image and counters. |
| Matrix test | [`dynamicSampleShadingTest()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L496) | Applies the static/dynamic pair and checks image output and invocation count. |
| Dynamic-state support | [`dynamicSampleShadingSupport()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L482) | Checks feature and format sample-count support. |
| Vulkan sample-shading rules | [`primsrast.adoc`](../../../../vulkan-docs/src/chapters/primsrast.adoc#L176) | Defines dynamic rasterization samples and sample-shading behavior. |

## Questions / Risk Points for User Audit

- Is the distinction between the two-draw family and the ten-leaf static/dynamic matrix clear?
- Is the invocation-counter check sufficiently explained without implying that every sample must always produce a separate invocation?
- Should the final page retain the flat-color texture detail, or is the counter and resolved-image relationship sufficient?

## Conversion Notes for Final Wiki Rewrite

- Keep `Background Knowledge` to dynamic rasterization sample state and sample shading.
- Use the test case leaf as the primary behavioral axis because each leaf selects a different sample-shading experiment.
- Carry the `### Failure Cause Mapping` table into the final page unchanged in substance and keep fresh cause analysis there.
- Keep shader analysis concise: the generated shaders are simple instrumentation, while the tested behavior is the interaction between dynamic rasterization samples and multisample shading.
