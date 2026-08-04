## Overview

**Core question:** Does `VK_DYNAMIC_STATE_RASTERIZATION_SAMPLES_EXT` make sample shading use the sample count recorded at draw time?

- [`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1) implements the `misc` intermediate node under the `extended_dynamic_state` test family.
- The source registers eleven test case leaves: one two-draw state-interaction case and ten static/dynamic sample-count pairs.
- Both mechanisms render a small multisample image, resolve it for host comparison, and use a fragment-shader atomic counter to observe invocation frequency.
- The implementation requires `extendedDynamicState3RasterizationSamples`; the pair matrix is excluded for Vulkan SC and shader-object construction.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Rasterization samples and sample shading.** `rasterizationSamples` controls the number of samples used by rasterization; the attachment's sample count is specified separately when the image is created. In these tests the dynamic rasterization count matches the multisample attachment count. When `sampleShadingEnable` is true, `minSampleShading` establishes the minimum fraction of covered samples at which the fragment shader must run. The relevant multisample-state rules are in [the rasterization chapter](../../../../vulkan-docs/src/chapters/primsrast.adoc#L176).
- **Dynamic rasterization samples.** Declaring `VK_DYNAMIC_STATE_RASTERIZATION_SAMPLES_EXT` lets command recording set the sample count with `vkCmdSetRasterizationSamplesEXT` before the draw. The dynamic value, rather than the pipeline's static field, is the state whose interaction with sample shading is under test.

## Registration Hierarchy

```text
pipeline.monolithic.extended_dynamic_state.misc
├── sample_shading_dynamic_sample_count
├── dynamic_sample_shading_static_1_dynamic_2
├── dynamic_sample_shading_static_1_dynamic_4
├── dynamic_sample_shading_static_1_dynamic_8
├── dynamic_sample_shading_static_1_dynamic_16
├── dynamic_sample_shading_static_2_dynamic_4
├── dynamic_sample_shading_static_2_dynamic_8
├── dynamic_sample_shading_static_2_dynamic_16
├── dynamic_sample_shading_static_4_dynamic_8
├── dynamic_sample_shading_static_4_dynamic_16
└── dynamic_sample_shading_static_8_dynamic_16
```

[`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) registers this concrete monolithic root. The same 11 leaves occur in `monolithic.txt`, `pipeline-library.txt`, and `fast-linked-library.txt`; only `sample_shading_dynamic_sample_count` occurs in `shader-object-unlinked-spirv.txt` and Vulkan SC `monolithic.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `sample_shading_dynamic_sample_count` plus ten `dynamic_sample_shading_static_<static>_dynamic_<dynamic>` leaves | Selects the two-draw state interaction or the static/dynamic count threshold experiment. | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) |
| Static sample count | 1, 2, 4, 8 for the pair matrix | Supplies the pipeline's `rasterizationSamples` value and determines `minSampleShading = 1/staticCount`. | [`dynamicSampleShadingTest()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L477) |
| Dynamic sample count | 2, 4, 8, 16, always greater than the static count | Selects the multisample attachment count and the value passed to `vkCmdSetRasterizationSamplesEXT`. | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) |
| Construction path | monolithic, pipeline library, fast linked library; shader-object only for the first leaf | Exercises the same behavior through supported pipeline construction forms. | mustpass files named above |

The ten ordered pairs from 1, 2, 4, 8, and 16 with `dynamic > static` form the complete matrix. This construction makes `minSampleShading * staticCount` no greater than 1 while the dynamic count makes the corresponding product greater than 1.

## Behavior Parameters

The primary behavioral axis is the test case leaf. The first leaf separates sample-shading-disabled and sample-shading-enabled draws. Each remaining leaf changes the static/dynamic count relationship that must drive the sample-shading minimum.

### sample_shading_dynamic_sample_count: two draws with different sample-shading enablement

The test dynamically selects four rasterization samples, then draws one half of the 2 x 2 framebuffer with sample shading disabled and the other with it enabled. Both halves must resolve to blue; only the enabled half must have exactly four fragment invocations per pixel.

### dynamic_sample_shading_static_1_dynamic_2: one static sample, two dynamic samples

This smallest matrix pair checks that a dynamic count of two activates the required sample-shading frequency even though the static count of one does not make the chosen threshold meaningful.

### dynamic_sample_shading_static_1_dynamic_4: one static sample, four dynamic samples

The pipeline state starts at one sample and the draw uses four. The atomic counter must meet the minimum derived from the dynamic count.

### dynamic_sample_shading_static_1_dynamic_8: one static sample, eight dynamic samples

This leaf increases the draw-time count to eight while retaining the one-sample static pipeline state.

### dynamic_sample_shading_static_1_dynamic_16: one static sample, sixteen dynamic samples

This leaf applies the widest dynamic increase from the one-sample static baseline.

### dynamic_sample_shading_static_2_dynamic_4: two static samples, four dynamic samples

The test checks that the larger draw-time count, not the two-sample pipeline value, controls the minimum invocation requirement.

### dynamic_sample_shading_static_2_dynamic_8: two static samples, eight dynamic samples

This leaf extends the same threshold interaction to an eight-sample attachment.

### dynamic_sample_shading_static_2_dynamic_16: two static samples, sixteen dynamic samples

This leaf uses the largest dynamic count from the two-sample static baseline.

### dynamic_sample_shading_static_4_dynamic_8: four static samples, eight dynamic samples

The test requires the count produced by the eight-sample dynamic state to satisfy the sample-shading lower bound.

### dynamic_sample_shading_static_4_dynamic_16: four static samples, sixteen dynamic samples

This leaf quadruples the sample count from the static value of four to a dynamic value of sixteen and checks the same relationship.

### dynamic_sample_shading_static_8_dynamic_16: eight static samples, sixteen dynamic samples

This final matrix leaf verifies the largest adjacent power-of-two transition in the generated pairs.

## Shader Analysis

The generated shaders are instrumentation rather than the behavior under test. The vertex shaders produce a fullscreen quad. The fragment shaders write blue output and use `atomicAdd` on a storage-buffer counter; the first family also reads `gl_SampleID` to enable sample shading for shader-object use. The host interprets the counters together with the resolved image, so no shader walkthrough or embedded SPIR-V is needed here.

## Runtime Execution and Result Checking

- The first family creates a four-sample color image, a single-sample resolve image, and one host-visible counter buffer per draw. It builds two otherwise matching pipelines, one with `sampleShadingEnable = VK_FALSE` and one with it true.
- It records both draws in separate viewport and scissor halves, calls `vkCmdSetRasterizationSamplesEXT` with four samples before the first draw, resolves the image, submits, and waits. Exact blue-image comparison confirms rendering; the first counter may range from one through four invocations per pixel and the second must equal four per pixel.
- The matrix family creates a multisample image with `params.dynamicCount`, a single-sample resolve image, a flat blue sampled texture, and one host-visible atomic counter. Its pipeline instead receives `params.staticCount` and `minSampleShading = 1/staticCount`.
- Before drawing, it sets `params.dynamicCount` dynamically. After submission, the source verifies exact resolved blue output and checks that the atomic count is at least `pixelCount * floor(minSampleShading * dynamicCount)`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_shading_dynamic_sample_count` | Incorrect dynamic rasterization-sample state, sample-shading execution, image resolve, or counter visibility. |
| `dynamic_sample_shading_static_<static>_dynamic_<dynamic>` | The dynamic count is not used for sample-shading evaluation, `minSampleShading` is mishandled, or the multisample image/counter result is incorrect. |

### Cause Analysis

#### Dynamic sample-state or sample-shading execution

**Possible failure symptoms:** the resolved output is not exactly blue, the enabled-draw counter misses its required count, or a matrix leaf reports fewer fragment invocations than its dynamic-count lower bound.

**Possible implementation causes:** the driver may not apply `vkCmdSetRasterizationSamplesEXT` to rasterization, may retain the pipeline's static `rasterizationSamples` when evaluating `minSampleShading`, or may lower fragment sample shading with an incorrect frequency. The source deliberately chooses pairs that separate static and dynamic evaluation.

#### Resolve, atomic, or host-visible result handling

**Possible failure symptoms:** an image comparison fails despite expected invocation counts, or an invocation counter is stale or too small while the command sequence otherwise completes.

**Possible implementation causes:** the implementation may mishandle multisample color output or resolve, fragment storage-buffer atomic writes, or visibility of shader writes to the host. The CTS commands include image copyback and a fragment-to-host memory barrier for the matrix counter; source-level investigation is needed to localize a failure beyond those observed outputs.

## Case Pruning

### Requirement-based pruning

All leaves require `extendedDynamicState3RasterizationSamples` and fragment stores and atomics. The two-draw leaf additionally requires `sampleRateShading`. The pair matrix checks that its format supports both selected sample counts, and unsupported combinations are reported as not supported rather than failed. Its code is disabled for Vulkan SC.

### Design-based pruning

The pair matrix includes only `dynamicCount > staticCount`. This is the intended threshold shape: `minSampleShading` is derived from the static count so that the static product does not exceed one, while the dynamic product does. Shader-object construction is excluded from this matrix; only the two-draw leaf has the shader-object path.

## Key Takeaways

- `misc` tests whether the draw-time `VK_DYNAMIC_STATE_RASTERIZATION_SAMPLES_EXT` value controls sample-shading behavior.
- The two-draw leaf distinguishes disabled from enabled sample shading, while the ten matrix leaves expose implementations that evaluate the minimum using stale static pipeline state.
- Exact resolved-color comparison and atomic invocation counts jointly observe rendering correctness and fragment execution frequency.
- The failure mapping distinguishes dynamic-state/sample-shading defects from output, atomic, and readback handling; see [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Misc registration | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) | Registers the two behavior groups and all leaf names. |
| Basic state interaction | [`sampleShadingWithDynamicSampleCount()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L133) | Creates the two pipelines, records two draws, and validates image and counter ranges. |
| Matrix program generation | [`dynamicSampleShadingPrograms()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L433) | Generates the counter-instrumented vertex and fragment shaders. |
| Matrix support checks | [`dynamicSampleShadingSupport()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L460) | Requires the feature and both format sample counts. |
| Matrix execution | [`dynamicSampleShadingTest()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L477) | Uses the dynamic count at draw time and checks color and invocation count. |
| Vulkan multisample rules | [`primsrast.adoc`](../../../../vulkan-docs/src/chapters/primsrast.adoc#L176) | Documents dynamic rasterization samples and sample-shading state. |
