## Overview

**Core question:** Does `textureWeightedQCOM` produce the expected weighted result across the registered image-processing paths?

- The family is implemented by [`vktImageProcessingWeightImageSamplingTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L70-L1600).

## Background Knowledge

Weighted sampling combines source texels using a weight image and sampler state. The test compares device output with a host reference.

## Registration Hierarchy

```text
image_processing.compute.weight_image_sampling
└── basic

image_processing.graphics.monolithic.weight_image_sampling
├── basic
├── weight_filter_params
├── address_modes
├── reduction_modes
├── tiling
├── swizzles
├── layouts
├── shader_stages
├── descriptors
└── normalized_coords

image_processing.graphics.fast_lib.weight_image_sampling
└── basic

image_processing.graphics.shader_objects.weight_image_sampling
└── basic
```

The compute tree contains only `basic`. The graphics construction variants each register the `basic` child; the additional parameter groups are only created for the monolithic construction.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning | Evidence |
|---|---|---|---|
| Pipeline path | compute, monolithic, fast-lib, shader-object graphics | Selects execution construction. Compute and all graphics paths register `basic`; only monolithic graphics additionally registers the parameter groups below. | [dispatcher](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L85), [common factory](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600) |
| Weight/input data | factory-generated supported combinations | Changes source and weight images used by the reference. | [factory](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600) |

## Behavior Parameters

Cases vary weight-image dimensions, formats, coordinates, and pipeline construction while respecting the implementation's advertised limits. The `basic` leaf is generated for both random-reference values and every supported format in each construction path. The monolithic-only groups isolate weight-filter parameters, sampler address and reduction modes, tiling, component swizzles, image layouts, shader stages, descriptor update-after-bind, and unnormalized coordinates; fast-linked and shader-object graphics intentionally do not duplicate those groups ([conditional registration](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image_processing.compute.weight_image_sampling.basic.r8g8b8a8_unorm_weight_r8_unorm
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `compute` | Executes the generated operation in a compute pipeline. |
| `basic` | Uses the baseline supported source and weight images. |

#### Purpose

Check that the generated weighted-sampling result matches the host reference.

#### Structural Design

- source image and weight image descriptors;
- sampler and generated coordinate parameters;
- storage-buffer result for host comparison.

#### Shader Code

This compute shader reconstructs the `r8g8b8a8_unorm_weight_r8_unorm` leaf: a 2D source texture, a non-separable 2D-array weight texture, and separate samplers feed `textureWeightedQCOM`. Binding 4 stores the numerical result and binding 5 stores a diagnostic color.

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
#extension GL_QCOM_image_processing : require
layout(set = 0, binding = 0) uniform highp texture2D sampledTexture;
layout(set = 0, binding = 1) uniform highp texture2DArray kernelTexture;
layout(set = 0, binding = 2) uniform highp sampler textureSampler;
layout(set = 0, binding = 3) uniform highp sampler kernelSampler;
layout(set = 0, binding = 4) writeonly buffer outputValue {
  vec4 avg;
} sbOut;
layout(push_constant, std430) uniform PushConstants
{
    vec2 textureCoord;
} pc;
layout(set = 0, binding = 5) uniform writeonly image2D outputImage;
void main() {
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    vec4 outColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    // Compute
    vec4 weightSampleVal = textureWeightedQCOM(
        sampler2D(sampledTexture, textureSampler),
        pc.textureCoord,
        sampler2DArray(kernelTexture, kernelSampler)
    );
    vec4 result = weightSampleVal;
    if (result != vec4(0.0f, 0.0f, 0.0f, 0.0f))
        outColor = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    else
        outColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    sbOut.avg = result;
    imageStore(outputImage, ivec2(gx, gy), outColor);
}
```

#### Additional Info

- [`initPrograms`](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1403-L1429) explicitly selects SPIR-V 1.4. This leaf uses a 3-by-3 weight image with one phase; the generated code uses `texture2DArray` and `sampler2DArray`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Pipeline path | Compute and graphics wrappers share the operation generator. | [`createImageProcessingWeightImageSamplingTests`](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600) |
| Weight/input data | Generated resource declarations and host reference vary with the registered image combinations. | [`createImageProcessingWeightImageSamplingTests`](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 86
; Schema: 0
               OpCapability Shader
               OpCapability StorageImageWriteWithoutFormat
               OpCapability TextureSampleWeightedQCOM
               OpExtension "SPV_QCOM_image_processing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %sampledTexture %textureSampler %pc %kernelTexture %kernelSampler %sbOut %outputImage
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_QCOM_image_processing"
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %outColor "outColor"
               OpName %weightSampleVal "weightSampleVal"
               OpName %sampledTexture "sampledTexture"
               OpName %textureSampler "textureSampler"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "textureCoord"
               OpName %pc "pc"
               OpName %kernelTexture "kernelTexture"
               OpName %kernelSampler "kernelSampler"
               OpName %result "result"
               OpName %outputValue "outputValue"
               OpMemberName %outputValue 0 "avg"
               OpName %sbOut "sbOut"
               OpName %outputImage "outputImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %sampledTexture Binding 0
               OpDecorate %sampledTexture DescriptorSet 0
               OpDecorate %textureSampler Binding 2
               OpDecorate %textureSampler DescriptorSet 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %kernelTexture Binding 1
               OpDecorate %kernelTexture DescriptorSet 0
               OpDecorate %kernelTexture WeightTextureQCOM
               OpDecorate %kernelSampler Binding 3
               OpDecorate %kernelSampler DescriptorSet 0
               OpDecorate %outputValue Block
               OpMemberDecorate %outputValue 0 NonReadable
               OpMemberDecorate %outputValue 0 Offset 0
               OpDecorate %sbOut NonReadable
               OpDecorate %sbOut Binding 4
               OpDecorate %sbOut DescriptorSet 0
               OpDecorate %outputImage NonReadable
               OpDecorate %outputImage Binding 5
               OpDecorate %outputImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
         %29 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %31 = OpTypeImage %float 2D 0 0 0 1 Unknown
%_ptr_UniformConstant_31 = OpTypePointer UniformConstant %31
%sampledTexture = OpVariable %_ptr_UniformConstant_31 UniformConstant
         %35 = OpTypeSampler
%_ptr_UniformConstant_35 = OpTypePointer UniformConstant %35
%textureSampler = OpVariable %_ptr_UniformConstant_35 UniformConstant
         %39 = OpTypeSampledImage %31
    %v2float = OpTypeVector %float 2
%PushConstants = OpTypeStruct %v2float
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v2float = OpTypePointer PushConstant %v2float
         %49 = OpTypeImage %float 2D 0 1 0 1 Unknown
%_ptr_UniformConstant_49 = OpTypePointer UniformConstant %49
%kernelTexture = OpVariable %_ptr_UniformConstant_49 UniformConstant
%kernelSampler = OpVariable %_ptr_UniformConstant_35 UniformConstant
         %55 = OpTypeSampledImage %49
         %61 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
       %bool = OpTypeBool
     %v4bool = OpTypeVector %bool 4
         %68 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
%outputValue = OpTypeStruct %v4float
%_ptr_StorageBuffer_outputValue = OpTypePointer StorageBuffer %outputValue
      %sbOut = OpVariable %_ptr_StorageBuffer_outputValue StorageBuffer
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
         %76 = OpTypeImage %float 2D 0 0 0 2 Unknown
%_ptr_UniformConstant_76 = OpTypePointer UniformConstant %76
%outputImage = OpVariable %_ptr_UniformConstant_76 UniformConstant
      %v2int = OpTypeVector %int 2
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
   %outColor = OpVariable %_ptr_Function_v4float Function
%weightSampleVal = OpVariable %_ptr_Function_v4float Function
     %result = OpVariable %_ptr_Function_v4float Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
               OpStore %outColor %29
         %34 = OpLoad %31 %sampledTexture
         %38 = OpLoad %35 %textureSampler
         %40 = OpSampledImage %39 %34 %38
         %47 = OpAccessChain %_ptr_PushConstant_v2float %pc %int_0
         %48 = OpLoad %v2float %47
         %52 = OpLoad %49 %kernelTexture
         %54 = OpLoad %35 %kernelSampler
         %56 = OpSampledImage %55 %52 %54
         %57 = OpImageSampleWeightedQCOM %v4float %40 %48 %56
               OpStore %weightSampleVal %57
         %59 = OpLoad %v4float %weightSampleVal
               OpStore %result %59
         %60 = OpLoad %v4float %result
         %64 = OpFUnordNotEqual %v4bool %60 %61
         %65 = OpAny %bool %64
               OpSelectionMerge %67 None
               OpBranchConditional %65 %66 %69
         %66 = OpLabel
               OpStore %outColor %68
               OpBranch %67
         %69 = OpLabel
               OpStore %outColor %29
               OpBranch %67
         %67 = OpLabel
         %73 = OpLoad %v4float %result
         %75 = OpAccessChain %_ptr_StorageBuffer_v4float %sbOut %int_0
               OpStore %75 %73
         %79 = OpLoad %76 %outputImage
         %80 = OpLoad %int %gx
         %81 = OpLoad %int %gy
         %83 = OpCompositeConstruct %v2int %80 %81
         %84 = OpLoad %v4float %outColor
               OpImageWrite %79 %83 %84
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

Support requires `VK_QCOM_image_processing`, `textureSampleWeighted`, supported formats, and valid weight-filter limits. The host compares device results with the CPU reference ([support](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L70-L150)).

## Failure Meaning

### Failure Cause Mapping

A failure indicates incorrect weighted sampling, resource setup, format interpretation, or synchronization.

### Cause Analysis

#### Weighted result or resource state

**Possible failure symptoms:** The weighted result differs from the CPU reference.

**Possible implementation causes:**

Investigate operation arithmetic, weight-image addressing, format conversion, descriptor setup, and output visibility.

## Case Pruning

### Requirement-based pruning

Unsupported extension, feature, format, or limit skips a case.

### Design-based pruning

Only supported combinations are registered.

## Key Takeaways

- The family tests functional weighted sampling, not merely property reporting.
- Compute and graphics paths share expected-value logic but differ in execution construction. The graphics `basic` family is present for monolithic, fast-linked-library, and shader-object construction; the additional graphics parameter groups are monolithic-only by source design.

## Source Reference Appendix

| Entry point | Link | Purpose |
|---|---|---|
| Factory | [weight-sampling factory](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L1280-L1600) | Registers cases. |
| Support/runtime | [weight-sampling implementation](../../../modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp#L70-L150) | Defines gates and checking. |
| Mustpass | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Lists coverage. |