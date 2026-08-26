## Overview

**Core question:** Do Vulkan graphics and compute paths produce correct SAD/SSD block-match results across the image and pipeline states registered by CTS?

- This page covers the `image_processing.graphics.*.block_matching` and `image_processing.compute.block_matching` test family implemented by [`vktImageProcessingBlockMatchingTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L104-L2268).
- The family exercises `textureBlockMatchSADQCOM` and `textureBlockMatchSSDQCOM` with host-generated target/reference image data, generated shaders, and a CPU-built reference result.
- Graphics cases write a red/green result image through a draw; compute cases write the result through an output storage image. Both paths also return the block-match metric through a storage buffer.

## Background Knowledge

- A block-match operation compares corresponding texels in a rectangular target block and reference block. SAD sums absolute channel differences; SSD sums their squares. The returned metric is separate from the diagnostic result image used by these tests.
- A Vulkan image view supplies the format and component mapping seen by shader image operations, while a sampler supplies address and reduction behavior. Those view/sampler states can change the values consumed by block matching even when the underlying image data is unchanged.
- A Vulkan descriptor set binds shader-visible resources to numbered bindings. The test's block-match image descriptors, samplers, metric buffer, and compute output image must agree with the generated shader interface.

## Registration Hierarchy

```text
image_processing.graphics.monolithic.block_matching
├── sad
└── ssd
```

The same `block_matching` test family is also registered below `graphics.fast_lib`, `graphics.shader_objects`, and `compute`. The category dispatcher selects the graphics construction type and compute path in [`createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78); the common factory creates the `sad` and `ssd` operation families in [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L1898).

## Parameter Dimensions and Observed Values

The registered scope is a matrix. The table lists the dimensions that change the resources, shader stage, execution path, or expected-result calculation; unsupported cases may be pruned before execution.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Operation family | `sad`, `ssd` | Selects the QCOM built-in and the host metric calculation. | [`imageProcessingOps[]`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1887-L1898), [`getImageProcGLSLStr()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255) |
| Graphics construction | `monolithic`, `fast_lib`, `shader_objects` | Selects the graphics pipeline-construction path. | [`constructionTypes[]`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L50-L63) |
| Basic formats | `r8_unorm`, `r8g8_unorm`, `r8g8b8_unorm`, `r8g8b8a8_unorm`, `a8b8g8r8_unorm_pack32`, `a2b10g10r10_unorm_pack32` | Changes image storage, component widths, and the tolerance calculation. | [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435) |
| Basic match mode | `same`, `diff` | Controls whether the target block is copied from the reference block or generated independently. | [`basic` registration](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1958-L2001) |
| Basic data variation | optional `_random`, optional `_constdiff` | Selects random versus uniform generated values; `_constdiff` adds a constant difference for applicable `diff` cases. | [`populateColorBuffer()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L523-L605) |
| Default geometry | 2D `64x64` images, coordinates `(0,0)`, block size `32x32` | Defines the baseline target/reference regions. | [`getCommonTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1657-L1695) |
| Graphics-only variation groups | `block_sizes`, `address_modes`, `reduction_modes`, `tiling`, `swizzles`, `layouts`, `shader_stages`, `descriptors` | Isolates block geometry, sampler state, image state, component mapping, stage, or descriptor update behavior. | [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2217) |
| Compute-only variation | `self` with `same`, `diff`, optional `_random` | Compares two non-overlapping regions of one image using the compute path. | [`self` registration](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248) |

## Behavior Parameters

The primary behavioral axis is the operation and the execution/variation group. `sad` and `ssd` change the value being computed; the remaining groups change the conditions under which that operation must remain correct.

### `sad` — sum of absolute differences

The generated shader calls `textureBlockMatchSADQCOM`. The CPU reference accumulates absolute differences over the selected target and reference blocks. A `same` case should therefore produce a zero metric when the compared values remain equal after the selected view/sampler interpretation ([operation mapping](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255); [reference construction](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773)).

### `ssd` — sum of squared differences

The generated shader calls `textureBlockMatchSSDQCOM`. The CPU reference squares the per-channel differences before accumulation. This changes the magnitude of the expected metric and its error tolerance, while the resource and execution structure remains shared with `sad` ([operation selection](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L747-L768)).

### Graphics condition groups

- `basic` covers the default image setup for all three graphics construction types and both operations.
- `block_sizes` changes coordinates and block extents, including `1x1`, `64x64`, and `1x64` cases.
- `address_modes` uses `clamp_to_edge` and `clamp_to_border` with oversized blocks, a smaller target image, and an out-of-range target coordinate.
- `reduction_modes` combines three reference reductions (`weighted_average`, `min`, `max`) with target reduction values from `NONE` through `MAX`.
- `tiling` combines linear and optimal target/reference images while avoiding the optimal/optimal combination already covered by `basic`.
- `swizzles` applies `bgra`, `g01a`, or `rbg1` component mappings to the reference view.
- `layouts` combines `rdonly_optimal` and `general` layouts while avoiding the read-only/read-only combination already covered by `basic`.
- `shader_stages` adds a `vertex` case; fragment-stage execution is already represented by `basic`.
- `descriptors` enables update-after-bind and varies `same`/`diff` plus random/non-random data.

The exact generator tables and case names are in [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1900-L2217), with coordinate/size generators in [`getBlockSizeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1817-L1877), [`getSamplerAddressModeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1699-L1741), [`getSamplerReductionModeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1743-L1764), [`getTilingTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1766-L1789), and [`getLayoutTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1791-L1815).

### Compute condition groups

Compute `basic` uses a compute shader with the same operation and baseline matrix. `self` binds one image as both target and reference and compares `(0,0)` with `(32,32)`; the implementation deliberately avoids overlapping regions ([self setup](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image_processing.graphics.monolithic.block_matching.sad.basic.r8_unorm_same
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `graphics.monolithic` | Uses the monolithic graphics pipeline path; the block-match operation is generated in the fragment stage for the baseline graphics case. |
| `sad` | Selects `textureBlockMatchSADQCOM`, returning the per-channel sum of absolute differences in a `vec4`. |
| `basic.r8_unorm_same` | Uses 64x64 target/reference `r8_unorm` images, compares `(0,0)` blocks of size `32x32`, and copies the reference block into the target block, so the expected metric is zero. |
| `randomReference = false`, no `_constdiff` suffix | Selects the uniform baseline input and leaves the matching blocks equal without an intentional constant difference. |

#### Purpose

This fragment shader computes the QCOM SAD block-match metric for the selected target and reference image regions. It writes the metric to a storage buffer and produces a green diagnostic pixel for an exact zero result, otherwise red.

#### Structural Design

| Phase | Shader-visible action | Observable role |
|-------|-----------------------|-----------------|
| Inputs | Combine separate `texture2D` images with separate samplers; load coordinates and block extent from push constants. | Supplies the two sampled block regions and their addressing/reduction state. |
| Operation | Call `textureBlockMatchSADQCOM` with target sampler, target coordinate, reference sampler, reference coordinate, and `blockSize`. | Produces the SAD result as a four-component value. |
| Validation signal | Compare the result with `vec4(0.0)`; select green for equality and red otherwise. | Encodes match/mismatch in the graphics output. |
| Metric export | Store the result in `sbOut.outError`. | Makes the device result available for host-side tolerance checking. |

#### Shader Code

```glsl
#version 450

/// The QCOM image-processing extension exposes the block-match operation.
#extension GL_QCOM_image_processing : require

/// Target block-match image descriptor; binding 0 is a sampled-image resource.
layout(set = 0, binding = 0) uniform highp texture2D targetTexture;
/// Reference block-match image descriptor; binding 1 is a sampled-image resource.
layout(set = 0, binding = 1) uniform highp texture2D referenceTexture;
/// Target sampler descriptor; binding 2 supplies target addressing and reduction state.
layout(set = 0, binding = 2) uniform highp sampler targetSampler;
/// Reference sampler descriptor; binding 3 supplies reference addressing and reduction state.
layout(set = 0, binding = 3) uniform highp sampler referenceSampler;
/// The returned metric is written to this storage-buffer member for host readback.
layout(set = 0, binding = 4) writeonly buffer outputError {
  vec4 outError;
} sbOut;
/// Push constants transport both block origins and the common block extent.
layout(push_constant, std430) uniform PushConstants
{
    uvec2 targetCoord;
    uvec2 referenceCoord;
    uvec2 blockSize;
} pc;

/// Monolithic graphics fragment output; the render target receives the diagnostic color.
layout(location = 0) out vec4 outColor;

void main() {
    // Compute
    /// Combine each image with its sampler before invoking the SAD block-match operation.
    vec4 blkMatchVal = textureBlockMatchSADQCOM(
        sampler2D(targetTexture, targetSampler),
        pc.targetCoord,  
        sampler2D(referenceTexture, referenceSampler),
        pc.referenceCoord,
        pc.blockSize
    );

    /// Preserve the returned four-component metric for both validation signals.
    vec4 err = blkMatchVal;
    if (err == vec4(0.0f, 0.0f, 0.0f, 0.0f))
        outColor = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    else
        outColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    sbOut.outError = err;
}
```

#### Additional Info

- For this exact `same` case, `getCommonTestParams()` supplies 64x64 images, `(0,0)` coordinates, and a `32x32` block; the host setup copies the reference region into the target region before the draw ([`getCommonTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1657-L1696), [`ImageProcessingBlockMatchGraphicsTestInstance::iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1024-L1036)).
- The graphics test creates the fragment module from the same generated source and draws the full-screen vertex buffer through the render pass ([`initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L318-L369), [`executeProgram()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L923-L958)).
- The explicit `ShaderBuildOptions` requests SPIR-V 1.4, which is the target used for the disassembly below ([`initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L318-L321)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation family | `sad` emits `textureBlockMatchSADQCOM`; the sibling `ssd` case emits `textureBlockMatchSSDQCOM`, while the interface and result-color logic remain shared. | [`getImageProcGLSLStr()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255) |
| Basic format | `r8_unorm` selects the image format and host tolerance/quantization behavior; other registered formats change the underlying block-match image component representation, not this generator structure. | [`getCommonTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1657-L1696), [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435) |
| Match/data suffix | `same` causes equal target/reference blocks; `diff`, `_random`, and `_constdiff` change host-generated inputs and expected metric, but do not alter this graphics shader text. | [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1958-L1998), [`populateColorBuffer()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L523-L605) |
| Graphics variant | `basic` uses fragment-stage generation; `shader_stages.vertex` puts the shared operation body in the vertex shader, while extended graphics groups vary image/sampler state and keep the monolithic generator path. | [`initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L318-L369), [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2189) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 65
; Schema: 0
               OpCapability Shader
               OpCapability TextureBlockMatchQCOM
               OpExtension "SPV_QCOM_image_processing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %targetTexture %targetSampler %pc %referenceTexture %referenceSampler %outColor %sbOut
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_QCOM_image_processing"
               OpName %main "main"
               OpName %blkMatchVal "blkMatchVal"
               OpName %targetTexture "targetTexture"
               OpName %targetSampler "targetSampler"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "targetCoord"
               OpMemberName %PushConstants 1 "referenceCoord"
               OpMemberName %PushConstants 2 "blockSize"
               OpName %pc "pc"
               OpName %referenceTexture "referenceTexture"
               OpName %referenceSampler "referenceSampler"
               OpName %err "err"
               OpName %outColor "outColor"
               OpName %outputError "outputError"
               OpMemberName %outputError 0 "outError"
               OpName %sbOut "sbOut"
               OpDecorate %targetTexture Binding 0
               OpDecorate %targetTexture DescriptorSet 0
               OpDecorate %targetTexture BlockMatchTextureQCOM
               OpDecorate %targetSampler Binding 2
               OpDecorate %targetSampler DescriptorSet 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpMemberDecorate %PushConstants 1 Offset 8
               OpMemberDecorate %PushConstants 2 Offset 16
               OpDecorate %referenceTexture Binding 1
               OpDecorate %referenceTexture DescriptorSet 0
               OpDecorate %referenceTexture BlockMatchTextureQCOM
               OpDecorate %referenceSampler Binding 3
               OpDecorate %referenceSampler DescriptorSet 0
               OpDecorate %outColor Location 0
               OpDecorate %outputError Block
               OpMemberDecorate %outputError 0 NonReadable
               OpMemberDecorate %outputError 0 Offset 0
               OpDecorate %sbOut NonReadable
               OpDecorate %sbOut Binding 4
               OpDecorate %sbOut DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
%targetTexture = OpVariable %_ptr_UniformConstant_10 UniformConstant
         %14 = OpTypeSampler
%_ptr_UniformConstant_14 = OpTypePointer UniformConstant %14
%targetSampler = OpVariable %_ptr_UniformConstant_14 UniformConstant
         %18 = OpTypeSampledImage %10
       %uint = OpTypeInt 32 0
     %v2uint = OpTypeVector %uint 2
%PushConstants = OpTypeStruct %v2uint %v2uint %v2uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v2uint = OpTypePointer PushConstant %v2uint
%referenceTexture = OpVariable %_ptr_UniformConstant_10 UniformConstant
%referenceSampler = OpVariable %_ptr_UniformConstant_14 UniformConstant
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
    %float_0 = OpConstant %float 0
         %46 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
       %bool = OpTypeBool
     %v4bool = OpTypeVector %bool 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
         %56 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %58 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
%outputError = OpTypeStruct %v4float
%_ptr_StorageBuffer_outputError = OpTypePointer StorageBuffer %outputError
      %sbOut = OpVariable %_ptr_StorageBuffer_outputError StorageBuffer
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
%blkMatchVal = OpVariable %_ptr_Function_v4float Function
        %err = OpVariable %_ptr_Function_v4float Function
         %13 = OpLoad %10 %targetTexture
         %17 = OpLoad %14 %targetSampler
         %19 = OpSampledImage %18 %13 %17
         %28 = OpAccessChain %_ptr_PushConstant_v2uint %pc %int_0
         %29 = OpLoad %v2uint %28
         %31 = OpLoad %10 %referenceTexture
         %33 = OpLoad %14 %referenceSampler
         %34 = OpSampledImage %18 %31 %33
         %36 = OpAccessChain %_ptr_PushConstant_v2uint %pc %int_1
         %37 = OpLoad %v2uint %36
         %39 = OpAccessChain %_ptr_PushConstant_v2uint %pc %int_2
         %40 = OpLoad %v2uint %39
         %41 = OpImageBlockMatchSADQCOM %v4float %19 %29 %34 %37 %40
               OpStore %blkMatchVal %41
         %43 = OpLoad %v4float %blkMatchVal
               OpStore %err %43
         %44 = OpLoad %v4float %err
         %49 = OpFOrdEqual %v4bool %44 %46
         %50 = OpAll %bool %49
               OpSelectionMerge %52 None
               OpBranchConditional %50 %51 %57
         %51 = OpLabel
               OpStore %outColor %56
               OpBranch %52
         %57 = OpLabel
               OpStore %outColor %58
               OpBranch %52
         %52 = OpLabel
         %62 = OpLoad %v4float %err
         %64 = OpAccessChain %_ptr_StorageBuffer_v4float %sbOut %int_0
               OpStore %64 %62
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [host] The shared support path requires `VK_QCOM_image_processing`, and below Vulkan 1.3 also requires `VK_KHR_format_feature_flags2` ([base support](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L100)). For SAD/SSD it requires `textureBlockMatch` and `VK_FORMAT_FEATURE_2_BLOCK_MATCHING_BIT_QCOM` for the selected sampled-image tiling ([operation support](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L102-L123)).
- [host] The block-match support path checks the target format feature, both target/reference image usages, and the device's `maxBlockMatchRegion` against the generated block size ([block-match support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L141-L213)). Graphics additionally checks color-attachment output support and pipeline-construction requirements ([graphics support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L240-L272)); compute checks storage-image output support and workgroup-count limits ([compute support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1157-L1193)).
- [host] The instance fills host-visible color buffers, creates target/reference images and views, creates samplers, writes descriptors, and copies the buffers into the images. `same` cases copy the reference region into the target; `diff` cases generate a separate target region ([buffer generation](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L523-L605); [descriptor setup](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L460-L521)).
- [device] Graphics submits a draw through the selected pipeline construction; compute dispatches over the output extent. Both paths write one `vec4` metric to a storage buffer and a diagnostic result image ([shared command path](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L642-L738)).
- [host] The test reads back the output image and metric, computes the CPU reference with [`buildStandardResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773), then calls [`verifyResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L237-L272). The image comparison uses an exact zero threshold; the metric comparison uses `calculateErrorThreshold()`, which scales floating-point and format quantization allowances by block element count and component width ([threshold](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L82-L102)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sad` | SAD built-in execution, input setup, or SAD reference calculation mismatch. |
| `ssd` | SSD built-in execution, input setup, or SSD reference calculation mismatch. |
| `basic` | Baseline image, descriptor, shader, output-transfer, or comparison failure. |
| `block_sizes` | Block coordinate, extent, or boundary handling failure. |
| `address_modes` | Address handling for out-of-range coordinates or blocks. |
| `reduction_modes` | Interaction between target and reference reduction modes. |
| `tiling` | Linear/optimal image-tiling handling. |
| `swizzles` | Reference-view component mapping or metric interpretation. |
| `layouts` | Target/reference image-layout handling. |
| `shader_stages` | Block matching in the vertex stage rather than the baseline fragment stage. |
| `descriptors` | Update-after-bind descriptor update or consumption. |
| `self` | Two non-overlapping regions of one image and the single-image descriptor path. |

### Cause Analysis

#### Operation or input-data mismatch

**Possible failure symptoms:** The returned metric exceeds the calculated tolerance, or the diagnostic image differs from the CPU result image.

**Possible implementation causes:** The selected QCOM operation may be executed incorrectly, or the device path may interpret image data, coordinates, component mapping, or format values differently from the host reference. The test does not isolate those causes further.

#### Resource-state or variant-handling mismatch

**Possible failure symptoms:** A resource-state or specialized group fails while the corresponding baseline group passes.

**Possible implementation causes:** The implementation may mishandle the selected image tiling/layout, sampler address/reduction state, component swizzle, shader stage, or descriptor update. Source-level investigation is needed to distinguish API-state handling from the block-matching operation.

#### Output or copyback mismatch

**Possible failure symptoms:** The metric is within tolerance but the exact output-image comparison fails, or the host reads back an unexpected metric.

**Possible implementation causes:** The output image write, layout transition, image-to-buffer copy, storage-buffer visibility, or host readback path may be incorrect. The test reports the mismatch but does not localize the responsible stage.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the required extension, feature, format feature, image usage, output usage, descriptor feature, pipeline construction capability, device limit, or compute workgroup-count limit is unavailable. Relevant gates include [`ImageProcessingTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L168), block-match checks ([`ImageProcessingBlockMatchTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L141-L213)), graphics checks ([`ImageProcessingBlockMatchGraphicsTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L240-L272)), and compute checks ([`ImageProcessingBlockMatchComputeTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1157-L1193)).

### Design-based pruning

- Extended graphics groups are intentionally generated only for monolithic pipelines. `fast_lib` and `shader_objects` cover `basic`; compute covers `basic` and `self` ([branch](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2251)).
- `constdiff` is not generated for `same` cases because a matching case cannot simultaneously apply an intentional constant difference ([basic generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1967-L1975)).
- The both-optimal tiling and both-read-only-optimal layout combinations are omitted from their extended groups because `basic` already covers them ([tiling generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1766-L1789); [layout generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1791-L1815)).
- The compute `self` generator fixes two non-overlapping regions and does not generate overlapping cases because the implementation does not support them ([self generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248)).

## Key Takeaways

- `sad` and `ssd` share the resource and execution framework but test different block-match metrics.
- The family validates both the returned metric and a diagnostic output image, so a passing case requires agreement in two observable results.
- The large graphics matrix is monolithic-only by design; the alternative pipeline-construction paths and compute path focus on their baseline or self-specific coverage.
- Runtime support checks prune unsupported cases before execution; a skipped case is not a failed block-match result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category dispatch | [`vktImageProcessingTests.cpp#createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78) | Selects graphics construction branches, API, and compute. |
| Common registration | [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L2257) | Registers operation families and all variation groups. |
| Operation mapping and formats | [`vktImageProcessingTestsUtil.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255), [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435) | Maps `sad`/`ssd` to GLSL built-ins and supplies candidate formats. |
| Generated graphics source | [`initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L275-L369) | Builds vertex and fragment GLSL for graphics cases. |
| Generated compute source | [`ImageProcessingBlockMatchComputeTest::initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1195-L1218) | Builds the compute shader and output-image path. |
| Host reference and tolerance | [`buildStandardResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773), [`calculateErrorThreshold()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L82-L102) | Produces the CPU metric and accepted error threshold. |
| Final comparison | [`verifyResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L237-L272) | Compares the output image exactly and the metric within tolerance. |
| Mustpass inventory | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Records the category's current executable case scope. |
