## Overview

**Core question:** Does `textureBoxFilterQCOM` produce the expected filtered values in the registered compute and graphics paths?

- The family is implemented by [`vktImageProcessingBoxFilterSamplingTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L71-L1670).
- It creates sampled images, runs the QCOM operation, and compares device output with a CPU reference.

## Background Knowledge

Box filtering combines texels in a selected rectangular region. The test uses sampled images and a storage buffer for result readback; graphics cases additionally render a diagnostic color.

## Registration Hierarchy

```text
image_processing.compute.box_filter_sampling
└── basic

image_processing.graphics.monolithic.box_filter_sampling
├── basic
├── box_filter_params
├── address_modes
├── reduction_modes
├── tiling
├── swizzles
├── layouts
├── shader_stages
├── descriptors
└── normalized_coords

image_processing.graphics.fast_lib.box_filter_sampling
└── basic

image_processing.graphics.shader_objects.box_filter_sampling
└── basic
```

The compute tree contains only `basic`. The graphics construction variants each register the `basic` child; the additional parameter groups are only created for the monolithic construction.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning | Evidence |
|---|---|---|---|
| Input variation | `basic`, random variants | Selects generated image data. | [factory](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1430-L1670) |
| Pipeline path | compute, monolithic, fast-lib, shader-object graphics | Selects execution construction. Compute and all graphics paths register `basic`; only monolithic graphics additionally registers the parameter groups below. | [dispatcher](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L85), [common factory](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1400-L1655) |

## Behavior Parameters

Each case varies image format, input data, coordinates, and box size within the supported property limits. The `basic` leaf is generated for both random-reference values and every supported format in each construction path. The monolithic-only groups isolate box parameters, sampler address and reduction modes, tiling, component swizzles, image layouts, shader stages, descriptor update-after-bind, and unnormalized coordinates; fast-linked and shader-object graphics intentionally do not duplicate those groups ([conditional registration](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1448-L1654)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image_processing.compute.box_filter_sampling.basic.r8g8b8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `compute` | Executes the generated operation in a compute pipeline. |
| `basic` | Uses the baseline supported image and box-size setup. |

#### Purpose

Check that the generated shader's `textureBoxFilterQCOM` result matches the host reference.

#### Structural Design

- sampled input image and sampler;
- push constants for coordinates and box size;
- storage-buffer result for host comparison.

#### Shader Code

For the `r8g8b8a8_unorm` baseline leaf, the following compute shader reconstructs `ImageProcessingBoxFilterComputeTest::initPrograms` and its `getProgPreMain` / `getProgMainBlock` helpers. Binding 2 receives the numerical result; binding 3 receives a diagnostic color.

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
#extension GL_QCOM_image_processing : require
layout(set = 0, binding = 0) uniform highp texture2D sampledTexture;
layout(set = 0, binding = 1) uniform highp sampler textureSampler;
layout(set = 0, binding = 2) writeonly buffer outputValue {
  vec4 avg;
} sbOut;
layout(push_constant, std430) uniform PushConstants
{
    vec2 textureCoord;
    vec2 boxSize;
} pc;
layout(set = 0, binding = 3) uniform writeonly image2D outputImage;
void main() {
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    vec4 outColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    // Compute
    vec4 boxfilterVal = textureBoxFilterQCOM(
        sampler2D(sampledTexture, textureSampler),
        pc.textureCoord,
        pc.boxSize
    );
    vec4 result = boxfilterVal;
    if (result != vec4(0.0f, 0.0f, 0.0f, 0.0f))
        outColor = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    else
        outColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    sbOut.avg = result;
    imageStore(outputImage, ivec2(gx, gy), outColor);
}
```

#### Additional Info

- [`initPrograms`](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L987-L1010) selects SPIR-V 1.4 explicitly. Coordinates and box size arrive through push constants; the module below is the complete compiled artifact for this compute shader.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Pipeline path | Compute and graphics wrappers use the same operation-specific generator. | [`createImageProcessingBoxFilterSamplingTests`](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1430-L1670) |
| Input and format | Generated declarations and host reference change with supported format and input variant. | [`createImageProcessingBoxFilterSamplingTests`](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1430-L1670) |

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
; Bound: 81
; Schema: 0
               OpCapability Shader
               OpCapability StorageImageWriteWithoutFormat
               OpCapability TextureBoxFilterQCOM
               OpExtension "SPV_QCOM_image_processing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %sampledTexture %textureSampler %pc %sbOut %outputImage
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_QCOM_image_processing"
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %outColor "outColor"
               OpName %boxfilterVal "boxfilterVal"
               OpName %sampledTexture "sampledTexture"
               OpName %textureSampler "textureSampler"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "textureCoord"
               OpMemberName %PushConstants 1 "boxSize"
               OpName %pc "pc"
               OpName %result "result"
               OpName %outputValue "outputValue"
               OpMemberName %outputValue 0 "avg"
               OpName %sbOut "sbOut"
               OpName %outputImage "outputImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %sampledTexture Binding 0
               OpDecorate %sampledTexture DescriptorSet 0
               OpDecorate %textureSampler Binding 1
               OpDecorate %textureSampler DescriptorSet 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpMemberDecorate %PushConstants 1 Offset 8
               OpDecorate %outputValue Block
               OpMemberDecorate %outputValue 0 NonReadable
               OpMemberDecorate %outputValue 0 Offset 0
               OpDecorate %sbOut NonReadable
               OpDecorate %sbOut Binding 2
               OpDecorate %sbOut DescriptorSet 0
               OpDecorate %outputImage NonReadable
               OpDecorate %outputImage Binding 3
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
%PushConstants = OpTypeStruct %v2float %v2float
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v2float = OpTypePointer PushConstant %v2float
      %int_1 = OpConstant %int 1
         %56 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
       %bool = OpTypeBool
     %v4bool = OpTypeVector %bool 4
         %63 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
%outputValue = OpTypeStruct %v4float
%_ptr_StorageBuffer_outputValue = OpTypePointer StorageBuffer %outputValue
      %sbOut = OpVariable %_ptr_StorageBuffer_outputValue StorageBuffer
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
         %71 = OpTypeImage %float 2D 0 0 0 2 Unknown
%_ptr_UniformConstant_71 = OpTypePointer UniformConstant %71
%outputImage = OpVariable %_ptr_UniformConstant_71 UniformConstant
      %v2int = OpTypeVector %int 2
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
   %outColor = OpVariable %_ptr_Function_v4float Function
%boxfilterVal = OpVariable %_ptr_Function_v4float Function
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
         %50 = OpAccessChain %_ptr_PushConstant_v2float %pc %int_1
         %51 = OpLoad %v2float %50
         %52 = OpImageBoxFilterQCOM %v4float %40 %48 %51
               OpStore %boxfilterVal %52
         %54 = OpLoad %v4float %boxfilterVal
               OpStore %result %54
         %55 = OpLoad %v4float %result
         %59 = OpFUnordNotEqual %v4bool %55 %56
         %60 = OpAny %bool %59
               OpSelectionMerge %62 None
               OpBranchConditional %60 %61 %64
         %61 = OpLabel
               OpStore %outColor %63
               OpBranch %62
         %64 = OpLabel
               OpStore %outColor %29
               OpBranch %62
         %62 = OpLabel
         %68 = OpLoad %v4float %result
         %70 = OpAccessChain %_ptr_StorageBuffer_v4float %sbOut %int_0
               OpStore %70 %68
         %74 = OpLoad %71 %outputImage
         %75 = OpLoad %int %gx
         %76 = OpLoad %int %gy
         %78 = OpCompositeConstruct %v2int %75 %76
         %79 = OpLoad %v4float %outColor
               OpImageWrite %74 %78 %79
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The host checks extension, feature, format, and `maxBoxFilterBlockSize` support, executes the selected path, and compares output with the CPU reference ([support](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L71-L125)).

## Failure Meaning

### Failure Cause Mapping

A failure indicates incorrect box-filter execution, resource setup, support handling, or synchronization.

### Cause Analysis

#### Filter result or resource state

**Possible failure symptoms:** The output differs from the CPU reference.

**Possible implementation causes:**

A mismatch can result from incorrect filter arithmetic, coordinate interpretation, image format handling, descriptor setup, or output synchronization.

## Case Pruning

### Requirement-based pruning

Unsupported extension, feature, format, or block size skips a case.

### Design-based pruning

Only supported format and parameter combinations are registered.

## Key Takeaways

- The family validates functional box filtering rather than only advertised limits.
- Compute and graphics paths share the reference calculation but use different execution plumbing. The graphics `basic` family is present for monolithic, fast-linked-library, and shader-object construction; the additional graphics parameter groups are monolithic-only by source design.

## Source Reference Appendix

| Entry point | Link | Purpose |
|---|---|---|
| Factory | [box-filter factory](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L1430-L1670) | Registers cases. |
| Runtime | [support and execution](../../../modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp#L71-L125) | Implements gates and checking. |
| Mustpass | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Lists coverage. |