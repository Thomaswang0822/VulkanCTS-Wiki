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

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.pipeline_library.extended_dynamic_state.misc.dynamic_sample_shading_static_1_dynamic_16
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `pipeline_library` | Builds the same generated shader pair through the pipeline-library construction path. |
| `static_1` | Sets the pipeline's static `rasterizationSamples` to 1 and therefore sets `minSampleShading` to `1.0 / 1 = 1.0`. |
| `dynamic_16` | Creates a 16-sample color attachment and records `vkCmdSetRasterizationSamplesEXT(..., VK_SAMPLE_COUNT_16_BIT)` before drawing. |
| `static_1` + `dynamic_16` | Separates stale static evaluation (one invocation per pixel) from correct draw-time evaluation (at least 16 invocations per pixel). |

#### Purpose

The fragment shader turns sample-shading frequency into a host-visible atomic count while independently producing the expected blue image. For this leaf, the host requires at least 64 invocations across the 2 x 2 framebuffer, proving that the dynamic 16-sample state participates in minimum sample-shading evaluation.

#### Structural Design

| Phase | Shader-visible action | Validation signal |
|---|---|---|
| Full-screen input | The companion vertex shader forwards clip-space position and texture coordinates for a four-vertex triangle strip. | Every pixel in the 2 x 2 framebuffer is covered. |
| Color observation | `texture(tex, inCoords)` samples a 16 x 16 texture pre-cleared to blue. | The resolved single-sample image must be exactly blue. |
| Invocation observation | Every fragment invocation executes `atomicAdd(..., 1u)`. | The host-visible counter must be at least `4 pixels x floor(1.0 x 16) = 64`. |

#### Shader Code

```glsl
#version 460
/// Primary fragment-stage observer for the selected matrix leaf.
layout (location=0) out vec4 outColor;
/// Interpolated full-screen-quad texture coordinates from the fixed companion vertex shader.
layout (location=0) in vec2 inCoords;
/// Set 0, binding 0: a combined sampler over the 16 x 16 single-sample texture cleared to blue.
layout (set=0, binding=0) uniform sampler2D tex;
/// Set 0, binding 1: one host-visible uint in a std430 storage buffer; every fragment invocation increments it.
layout (set=0, binding=1, std430) buffer CounterBlock { uint counter; } atomicCounter;
void main (void) {
    /// Preserve the color oracle independently of the invocation-count oracle.
    outColor = texture(tex, inCoords);
    /// Count actual fragment invocations after dynamic sample-count state and minimum sample shading take effect.
    atomicAdd(atomicCounter.counter, 1u);
}
```

#### Additional Info

- The fixed companion vertex shader generated by [`dynamicSampleShadingPrograms()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L433) only forwards `inPos` and `inCoords`; it does not vary across the ten static/dynamic sample-count leaves and is omitted because the fragment atomic is the validation payload.
- The sampled texture is deliberately flat blue so color comparison remains a separate oracle from the atomic invocation count. The builder comment states that this avoids using a direct flat shader color in case that changes driver behavior.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Static sample count | The GLSL is unchanged. The host changes pipeline `rasterizationSamples` and computes `minSampleShading = 1.0 / staticCount`, which changes the counter lower bound. | [`dynamicSampleShadingTest()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L477) |
| Dynamic sample count | The GLSL is unchanged. The host changes the multisample attachment and draw-time rasterization sample count, so correct execution produces a different minimum number of atomic increments. | [`dynamicSampleShadingTest()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L477) |
| Construction path | Monolithic, pipeline-library, and fast-linked-library cases use this same generated pair; shader-object construction is excluded from this matrix. | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) |
| Test family leaf | `sample_shading_dynamic_sample_count` uses a different fragment builder: it reads `gl_SampleID`, writes blue directly, and binds only the invocation counter. | [`initBlueAndAtomicCounterFragmentProgram()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L92) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 31
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inCoords
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %tex "tex"
               OpName %inCoords "inCoords"
               OpName %CounterBlock "CounterBlock"
               OpMemberName %CounterBlock 0 "counter"
               OpName %atomicCounter "atomicCounter"
               OpDecorate %outColor Location 0
               OpDecorate %tex Binding 0
               OpDecorate %tex DescriptorSet 0
               OpDecorate %inCoords Location 0
               OpDecorate %CounterBlock BufferBlock
               OpMemberDecorate %CounterBlock 0 Offset 0
               OpDecorate %atomicCounter Binding 1
               OpDecorate %atomicCounter DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
        %tex = OpVariable %_ptr_UniformConstant_11 UniformConstant
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
   %inCoords = OpVariable %_ptr_Input_v2float Input
       %uint = OpTypeInt 32 0
%CounterBlock = OpTypeStruct %uint
%_ptr_Uniform_CounterBlock = OpTypePointer Uniform %CounterBlock
%atomicCounter = OpVariable %_ptr_Uniform_CounterBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %tex
         %18 = OpLoad %v2float %inCoords
         %19 = OpImageSampleImplicitLod %v4float %14 %18
               OpStore %outColor %19
         %27 = OpAccessChain %_ptr_Uniform_uint %atomicCounter %int_0
         %30 = OpAtomicIAdd %uint %27 %uint_1 %uint_0 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

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
