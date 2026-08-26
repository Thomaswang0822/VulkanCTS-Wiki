## Overview

**Core question:** Do multisample shader built-ins identify, locate, mask, and write individual samples as required across the CTS pipeline variants?

- This page documents the `multisample_shader_builtin` test family implemented by [`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L56-L2326).
- Its direct intermediate nodes test `gl_SampleID`, `gl_SamplePosition`, input and output sample masks, coordinate-derived per-sample storage-image writes, and a two-subpass output-mask path.
- The tests use generated graphics or compute programs, multisampled images, resolve images where appropriate, and host-side readback to make each built-in observable.
- `image_write_sample` exists only under the monolithic construction root. The other direct nodes appear under monolithic, pipeline-library, and fast-linked-library roots in the default mustpass scope.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A multisampled image stores a separate value for each sample in a pixel. `gl_SampleID` identifies the current sample and `gl_SamplePosition` gives its position within the pixel. Vulkan defines the corresponding built-ins in [SampleId](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-sampleid) and [SamplePosition](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-sampleposition).
- A `SampleMask` input exposes coverage for a fragment invocation. A `SampleMask` output contributes a mask that Vulkan combines with generated coverage. The [SampleMask](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-samplemask) rules define its array form and bit-to-sample mapping.
- `VkPipelineMultisampleStateCreateInfo::pSampleMask` supplies pipeline sample coverage. The [Sample Mask](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-samplemask) section defines the state and its default all-bits-set behavior.
- A resolve produces one value per pixel, while an explicit per-sample fetch preserves the sample dimension for host comparison. The test uses each observation method according to the built-in contract it needs to inspect.

## Registration Hierarchy

```text
pipeline.monolithic.multisample_shader_builtin
├── sample_id
├── sample_position
├── sample_mask
├── image_write_sample
└── write_sample_mask
```

[`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2228-L2326) registers these five direct intermediate nodes. `image_write_sample` is conditional on `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`; `write_sample_mask` is registered for every construction type passed to the factory. Default-mustpass coverage contains 95 monolithic leaves, including four `image_write_sample` leaves, and 91 leaves each under `pipeline_library` and `fast_linked_library`. The latter two roots have no `image_write_sample` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Intermediate node | `sample_id`, `sample_position`, `sample_mask`, `image_write_sample`, `write_sample_mask` | Selects the built-in contract and result-checking path. | [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2248-L2323) |
| Test case leaf | `sample_position.{distribution,correctness}`; `sample_mask.{pattern,bit_count,bit_count_0_5,correct_bit,write}` | Separates sample-location checks and distinct sample-mask contracts. | [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2252-L2288) |
| Image extent | `128x128`, `137x191` | Exercises a square and a non-square raster target in the common graphics cases. | [`imageSizes`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2233-L2238) |
| Sample count, full set | 2, 4, 8, 16, 32, 64 | Used by `sample_id` and the sample-position leaves. | [`samplesSetFull`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2240-L2259) |
| Sample count, reduced set | 2, 4, 8, 16, 32 | Used by the `sample_mask` leaves. | [`samplesSetReduced`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2263-L2286) |
| Storage-image sample count | 2, 4, 8, 16 | Used by monolithic `image_write_sample`; the factory omits one sample. | [`image_write_sample` loop](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2290-L2308) |
| Output-mask sample count | 1, 2, 4, 8, 16 | Used by `write_sample_mask`. | [`write_sample_mask` loop](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2310-L2323) |
| Pipeline construction type | monolithic, pipeline-library, fast-linked-library | Selects the construction root; the storage-image node only accepts monolithic construction. | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L130-L143) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. Each node selects a different built-in, multisample-image, or resource-observation contract and its corresponding result comparison.

### sample_id: sample-index identity

The fragment shader encodes `gl_SampleID` in the red channel. The host fetches each sample from the multisampled image and requires the value at sample index N to equal N.

### sample_position: sample-location validity and use

`distribution` encodes `gl_SamplePosition`, then checks that positions are in the unit square, unique within a pixel, and sufficiently centered for sample counts of four or more. `correctness` uses a sample-qualified screen-space varying and accepts the result when, for one of the neighboring pixel origins, the varying lies within a `0.15625` per-component tolerance of that origin plus `gl_SamplePosition`.

### sample_mask: coverage input and output behavior

`pattern`, `bit_count`, `bit_count_0_5`, and `correct_bit` inspect `gl_SampleMaskIn` against coverage and the selected minimum sample-shading rate. `write` assigns an output mask and checks the resulting resolved intensity.

### image_write_sample: compute storage-image writes

The monolithic-only node dispatches compute work that writes selected sample indices of a multisample storage image, then verifies that the readback records the expected value for each pixel/sample pair.

### write_sample_mask: two-subpass output-mask readback

The first subpass writes `gl_SampleMask` while rendering to a multisampled attachment. A second subpass reads that attachment as an input attachment and writes the observed sample state to a host-visible buffer for exact comparison.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.pipeline_library.multisample_shader_builtin.sample_id.128_128_1.samples_16
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `pipeline_library` | Selects the pipeline-library construction root; the selected `sample_id` case is registered for this root and uses the common graphics multisample path. |
| `sample_id` | Selects `MSCaseSampleID`, whose fragment shader reads `gl_SampleID` and encodes it into the red color channel. |
| `128_128_1` | Selects a 128 x 128 x 1 raster target. The multisampled color attachment uses `VK_FORMAT_R8G8B8A8_UNORM`; a single-sample resolve image is also created by the shared base path. |
| `samples_16` | Selects 16 samples per pixel. The host fetches every sample and requires sample N to contain the encoded value N. |

#### Purpose

This fragment shader checks that `gl_SampleID` identifies the actual sample invocation. It writes the sample index as an 8-bit-normalized red value so host-side per-sample readback can compare every sample against its fetch index.

#### Structural Design

| Phase | Exact generated behavior |
|---|---|
| Invocation identity | The fragment invocation reads the built-in `gl_SampleID`, which is represented as an integer sample index. |
| Encoding | The index is converted to `float` and divided by `255`, preserving each possible sample index in the red channel for the registered maximum of 64 samples. |
| Output | The shader writes `(sampleID / 255, 0, 0, 1)` to color location 0. |
| Validation | `MSInstanceSampleID::verifyImageData` fetches each multisample image sample independently and requires the decoded red channel to equal that sample's index. |

#### Shader Code

```glsl
#version 440

/// The only fragment output is the RGBA8 color attachment used to transport the sample index to readback.
layout(location = 0) out vec4 fs_out_color;

void main (void)
{
    /// Each invocation encodes its built-in sample index in the red channel; the host later reads this value per sample.
    fs_out_color = vec4(float(gl_SampleID) / float(255), 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The selected case's companion vertex shader only forwards the full-screen NDC position to `gl_Position`; it is fixed boilerplate and does not participate in the sample-ID oracle.
- `sampleRateShading` is required for this built-in case, ensuring the fragment execution path exposes sample-qualified behavior; image-size, color-attachment, multisample, and resolve support are checked before execution.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `sample_id` versus `sample_position` / `sample_mask` | Selects a different specialized fragment builder and verification oracle; the shown shader specifically emits `gl_SampleID`, while the neighboring families encode sample positions or inspect/write sample masks. | [`MSCaseSampleID::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L342-L375) |
| Image size | Does not change the generated fragment declarations or instructions; it changes the raster target and host iteration bounds. | [`imageSizes`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2233-L2238) |
| Sample count | Does not change this GLSL source; it changes the number of samples rendered and the number of per-sample results checked. | [`samplesSetFull`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2240-L2250) |
| Pipeline construction type | Does not change this shader source; it selects the pipeline construction root. `sample_id` is registered for monolithic, pipeline-library, and fast-linked-library roots. | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L130-L143) |

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
; Bound: 20
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fs_out_color %gl_SampleID
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 440
               OpName %main "main"
               OpName %fs_out_color "fs_out_color"
               OpName %gl_SampleID "gl_SampleID"
               OpDecorate %fs_out_color Location 0
               OpDecorate %gl_SampleID BuiltIn SampleId
               OpDecorate %gl_SampleID Flat
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%fs_out_color = OpVariable %_ptr_Output_v4float Output
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_SampleID = OpVariable %_ptr_Input_int Input
  %float_255 = OpConstant %float 255
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %int %gl_SampleID
         %14 = OpConvertSToF %float %13
         %16 = OpFDiv %float %14 %float_255
         %19 = OpCompositeConstruct %v4float %16 %float_0 %float_0 %float_1
               OpStore %fs_out_color %19
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The common `MSCase` support path validates image size, color-attachment format support, multisampled-image support, and resolve-image support. The fragment-shader built-in cases request `sampleRateShading`, while common graphics cases check pipeline-library support. The storage-image case instead checks `shaderStorageImageMultisample` and the required storage-image and transfer format features. See [`MSCase::checkImagesSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L213-L249), [`MSCaseSampleID::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L323-L340), and [`WriteSampleTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1302-L1324).
- Common graphics cases create multisampled and resolve images, render a full-screen triangle strip, then retrieve the multisample samples and, when needed, resolved pixels through the shared multisample base. Each specialized `verifyImageData` function owns the case-specific pass condition.
- `sample_id` compares every fetched sample channel with its sample index ([`MSInstanceSampleID::verifyImageData`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L295-L319)). `sample_position.distribution` checks bounds, duplicate positions, and its average-position threshold ([`MSInstanceSamplePosDistribution::verifyImageData`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L400-L480)).
- `image_write_sample` creates multisample storage images, clears and dispatches them, transfers output for host access, invalidates the allocation, and requires every output pixel to be green ([`WriteSampleTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1392-L1634)).
- `write_sample_mask` records a two-subpass render pass, copies the result to a host-visible buffer, invalidates it, and checks each stored value is exactly the expected zero or one for its pixel/sample address ([`WriteSampleMaskTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1804-L2224)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sample_id` | Incorrect sample invocation identity or per-sample fetch/index handling. |
| `sample_position` | Incorrect sample coordinates, interpolation at sample locations, or resolve/readback handling. |
| `sample_mask` | Incorrect input coverage mask, sample-count interpretation, shading-rate handling, or output-mask application. |
| `image_write_sample` | Incorrect storage-image sample addressing or multisample image write behavior. |
| `write_sample_mask` | Incorrect shader output mask combination, subpass input-attachment visibility, or per-sample readback. |

### Cause Analysis

#### Sample identity or position observation

**Possible failure symptoms:** `sample_id` reports a fetched sample value different from its index. `sample_position` reports an out-of-range value, duplicate location, excessive average offset, or a mismatch between an interpolated value and `gl_SamplePosition`.

**Possible implementation causes:** The implementation may assign a wrong invocation sample index, produce a wrong sample location, interpolate the varying at the wrong location, or corrupt a per-sample fetch or resolve path. The final observation includes rendering, image retrieval, and host comparison, so source-level investigation is needed to localize the fault to rasterization, image operations, or readback.

#### Input or output sample-mask behavior

**Possible failure symptoms:** A sample-mask leaf finds a coverage bit that should be absent or missing, observes an incorrect bit count, or produces a resolved/output value inconsistent with the expected mask.

**Possible implementation causes:** The implementation may apply `pSampleMask` incorrectly, expose the wrong `gl_SampleMaskIn` bits, mishandle the configured sample-shading rate, or combine `gl_SampleMaskOut` incorrectly with generated coverage. The specification's [SampleMask](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-samplemask) rules define the mask relation, while the generated shaders and verification functions define the test's concrete observation path.

#### Storage-image or input-attachment per-sample access

**Possible failure symptoms:** `image_write_sample` finds a non-green image result, or `write_sample_mask` finds a buffer value other than the expected zero or one at a particular pixel/sample position.

**Possible implementation causes:** The failure may involve multisample storage-image addressing or the coordinate-derived sample-selection mask, shader output-mask application, subpass input-attachment reads, required image-layout or visibility handling, or buffer copyback. These paths contain multiple operations, so the final host value classifies the failing operation chain rather than proving a single implementation component caused it.

## Case Pruning

### Requirement-based pruning

- Common graphics cases require supported 2D image extents, `VK_FORMAT_R8G8B8A8_UNORM` color-attachment use, multisampled color attachment and input-attachment use, and a single-sample resolve image. [`MSCase::checkImagesSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L213-L240) enforces these checks.
- Built-in graphics cases request `DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING`, as shown by [`MSCaseSampleID::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L323-L329) and analogous case specializations.
- `image_write_sample` requires `shaderStorageImageMultisample` and only registers for monolithic pipeline construction ([`WriteSampleTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1302-L1321), [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2290-L2308)).

### Design-based pruning

- The source uses full and reduced sample-count sets to keep each family focused on the contract it observes instead of applying one universal matrix.
- `image_write_sample` omits one-sample images because a sample-indexed multisample-image test needs more than one sample to distinguish the indexed behavior.
- `write_sample_mask` uses a separate two-subpass path because its test needs to observe a fragment output mask through a per-sample input-attachment read.
- Shader-object roots are absent because `write_sample_mask` relies on input attachments, which do not fit the dynamic-rendering/shader-object path used by that construction mode.

## Key Takeaways

- The five direct nodes test separate multisample built-in, image-access, and output-observation contracts rather than one generic multisampling result.
- The common graphics cases use generated shaders and multisample fetch or resolve readback; the specialized nodes add storage-image compute access or input-attachment subpass access.
- `image_write_sample` is deliberately monolithic-only, while `write_sample_mask` remains available under the graphics pipeline-library construction roots.
- A failing output identifies the tested operation chain, but source-level investigation is needed to isolate a specific rasterization, shader, image, synchronization, or readback component.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Common resource-support checks | [`MSCase::checkImagesSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L213-L249) | Validates image limits, format features, multisampled attachment support, and resolve-image support. |
| Sample ID generation and comparison | [`MSCaseSampleID` and `MSInstanceSampleID`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L295-L381) | Encodes `gl_SampleID` and checks every sample. |
| Sample-position distribution | [`MSInstanceSamplePosDistribution`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L400-L480) | Defines range, uniqueness, and average-position checks. |
| Sample-mask test implementations | [`MSCaseSampleMaskPattern` through `MSCaseSampleMaskWrite`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L799-L1181) | Builds the input-mask and output-mask shader cases. |
| Storage-image sample writes | [`WriteSampleTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1244-L1634) | Implements coordinate-derived per-sample compute writes and green-image validation. |
| Two-subpass output-mask test | [`WriteSampleMaskTestCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1638-L2224) | Implements mask output, input-attachment observation, and exact buffer validation. |
| Family registration | [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2228-L2326) | Defines direct nodes, leaf matrices, and the monolithic-only branch. |
| Category registration | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L130-L143) | Registers the family under the applicable construction roots. |
| Built-in semantics | [SampleId](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-sampleid), [SampleMask](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-samplemask), and [SamplePosition](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-sampleposition) | Defines the shader built-ins used by this family. |
| Pipeline sample-mask state | [Sample Mask](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-samplemask) | Defines `pSampleMask` pipeline coverage state. |
