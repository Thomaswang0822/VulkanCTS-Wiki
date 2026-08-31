## Overview

**Core question:** Does a plane view produce the same selected-plane sample as the corresponding data in a multi-planar YCbCr image?

- [`vktYCbCrViewTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp) implements the `ycbcr.plane_view` test family created by [`createViewTests()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1075-L1078).
- The `image_view` family selects a plane from the original multi-planar image with `VK_IMAGE_ASPECT_PLANE_N_BIT`. The `memory_alias` family samples a separate compatible image bound to the selected plane's disjoint allocation.
- Every case samples the whole image through a `VkSamplerYcbcrConversion` and samples the selected plane directly. The host compares both results with software references at 500 generated texel-center coordinates.
- The page explains the registered matrix, the generated shader, resource setup, result checking, and what a failure says about plane views, compatible formats, or alias binding.

## Background Knowledge

- **Multi-planar images and plane views.** A multi-planar image stores components in separate planes. A single-plane view selects one plane with `VK_IMAGE_ASPECT_PLANE_0_BIT`, `VK_IMAGE_ASPECT_PLANE_1_BIT`, or `VK_IMAGE_ASPECT_PLANE_2_BIT` and uses that plane's compatible single-plane format. Plane-derived dimensions matter for subsampled formats.
- **Compatible formats.** Compatible views use the same mapping between texel coordinates and memory locations, while the format changes how the bit pattern is interpreted. The test compares plane results through a common format when padding bits make direct comparison unsafe.
- **Disjoint aliasing.** A disjoint multi-planar image can bind planes separately. A compatible single-plane image can alias one plane when Vulkan's disjoint, alias, format, binding, and dimension requirements hold. The alias is another image object over the same allocation, not a second uploaded copy.

## Registration Hierarchy

```text
ycbcr.plane_view
├── image_view
└── memory_alias
```

The two direct children are expanded by [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L1063) into format, plane, shader-stage, descriptor-mode, flag, and compatible-format cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| View family | `image_view`, `memory_alias` | Chooses an aspect-qualified view of the original image or a compatible image over one disjoint plane allocation. | [`populateViewGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1065-L1070) |
| Format | `VK_YCBCR_FORMAT_FIRST` up to but not including `VK_YCBCR_FORMAT_LAST`, plus the `VK_EXT_ycbcr_2plane_444_formats` range | Selects the multi-planar layout and its plane count and extents. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1003-L1009), [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1053-L1062) |
| Plane | `0` through `getPlaneCount(format) - 1` | Selects the plane sampled without YCbCr conversion. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1005-L1020) |
| Plane-compatible format | Native plane format and accepted entries from `s_compatible_formats` | Tests both the native interpretation and compatible reinterpretations of the plane bits. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1028-L1046) |
| Image flags | `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, with `VK_IMAGE_CREATE_DISJOINT_BIT` varied and `VK_IMAGE_CREATE_ALIAS_BIT` added for `memory_alias` | Controls mutable views, separate plane allocations, and alias-image creation. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L986-L1017) |
| Shader stage | Fragment and compute | Runs the same two-sampler comparison through graphics or compute execution. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L985) |
| Descriptor mode | `descriptor`, `descriptor_buffer`, `descriptor_heap` where supported | Changes how the plane and whole-image combined samplers reach the generated shader. | [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L991-L1026) |

## Behavior Parameters

The primary behavioral axis is the registered **view family**. Its values change how the selected plane reaches the shader; the remaining dimensions configure the image format, plane, execution stage, descriptor transport, and comparison format.

### `image_view`: Aspect-qualified view of the original image

The plane view uses the original multi-planar image and the selected `VK_IMAGE_ASPECT_PLANE_N_BIT`. The whole-image view and plane view therefore refer to two views over the same image object, with only the plane view omitting YCbCr conversion.

### `memory_alias`: Compatible image over a plane allocation

The test creates a plane-sized image with the selected plane-compatible format, then binds it to the selected allocation from the disjoint multi-planar image. The shader compares the alias image's sample with the selected plane's software reference.

## Shader Analysis

The test generates a small shader specification rather than storing shader source in a file. The following walkthrough uses the mustpass case `dEQP-VK.ycbcr.plane_view.image_view.g8_b8r8_2plane_444_unorm_disjoint_plane_0_compute`. The compute and fragment paths use the same `getShaderSpec()` operations; `ShaderExecutor` supplies stage-specific I/O wrappers.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ycbcr.plane_view.image_view.g8_b8r8_2plane_444_unorm_disjoint_plane_0_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `image_view` | The plane view selects plane `0` from the original image. |
| `g8_b8r8_2plane_444_unorm` | The image has two planes with 4:4:4 extents. Plane `0` uses an 8-bit single-channel compatible format. |
| `disjoint` + `plane_0` | The image uses separate plane allocations and the shader reads plane `0`. |
| `compute` | `ShaderExecutor` wraps the specification in a compute shader. |
| `descriptor` | The default descriptor-set path supplies the two combined image samplers. |

#### Purpose

The shader reads the same coordinate through the converted whole-image view and the direct plane view. The host later checks each result against the corresponding software sample.

#### Structural Design

| Stage | Operation | Meaning |
|-------|-----------|---------|
| Input | Read `texCoord` from the executor input buffer | Selects one of the 500 host-generated sample coordinates. |
| Whole image | `texture(u_image, texCoord)` | Samples the multi-planar image through YCbCr conversion. |
| Plane view | `texture(u_planeView, texCoord)` | Samples the selected plane without conversion. |
| Output | Store `result0` and `result1` | Returns both values to the host for independent reference checks. |

#### Shader Code

The following is the generated compute wrapper for the selected `vec4` plane-compatible result type. The `///` comments identify the test-specific resources and operations.

```glsl
#version 450 core
#extension GL_EXT_long_vector : enable
/// Binding 1 holds the whole-image sampler with the immutable YCbCr conversion.
layout(binding = 1, set = 1) uniform highp sampler2D u_image;
/// Binding 0 holds the selected plane view without a sampler conversion.
layout(binding = 0, set = 1) uniform highp sampler2D u_planeView;
layout(local_size_x = 1) in;

struct Inputs
{
    vec2 texCoord;
};

struct Outputs
{
    vec4 result0;
    vec4 result1;
};

/// Set 0 carries executor input coordinates and the two returned shader values.
layout(set = 0, binding = 0, std430) buffer InBuffer
{
    Inputs inputs[];
};
layout(set = 0, binding = 1, std430) buffer OutBuffer
{
    Outputs outputs[];
};

void main (void)
{
    uint invocationNdx = gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z
                       + gl_NumWorkGroups.x * gl_WorkGroupID.y + gl_WorkGroupID.x;
    vec2 texCoord = inputs[invocationNdx].texCoord;
    vec4 result0;
    vec4 result1;

    /// The two texture operations use the same coordinate but different views.
    result0 = texture(u_image, texCoord);
    result1 = vec4(texture(u_planeView, texCoord));

    outputs[invocationNdx].result0 = result0;
    outputs[invocationNdx].result1 = result1;
}
```

#### Additional Info

- The selected `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM` plane `0` uses a single-channel compatible format, so this representative shader uses `sampler2D` and `vec4`; integer compatible formats change both declarations and the output conversion.
- `ShaderExecutor` adds the input and output storage-buffer wrapper around the two operations. Its compute path uses set `0`, bindings `0` and `1`, while the test's image samplers use set `1`, bindings `0` and `1`.
- The fragment path adds passthrough vertex and fragment plumbing, but the two sampled values and their host-side comparison remain the same.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Plane-compatible format | `getSamplerDecl()` selects `sampler2D`, `isampler2D`, or `usampler2D`; `getVecType()` selects the matching `vec4`, `ivec4`, or `uvec4` result. | [`getSamplerDecl()` and `getVecType()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L421-L439) |
| Shader stage | Compute wraps the specification in one generated compute stage; fragment execution uses a generated fragment stage and passthrough vertex stage. | [`initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L946-L951), [`FragmentShaderExecutor::generateSources()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1834-L1843) |
| Descriptor mode | The shader declarations stay the same while descriptor-set, descriptor-buffer, and descriptor-heap transport changes. | [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L757-L842) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 79
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_long_vector"
               OpName %main "main"
               OpName %invocationNdx "invocationNdx"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %texCoord "texCoord"
               OpName %Inputs "Inputs"
               OpMemberName %Inputs 0 "texCoord"
               OpName %InBuffer "InBuffer"
               OpMemberName %InBuffer 0 "inputs"
               OpName %_ ""
               OpName %result0 "result0"
               OpName %u_image "u_image"
               OpName %result1 "result1"
               OpName %u_planeView "u_planeView"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "result0"
               OpMemberName %Outputs 1 "result1"
               OpName %OutBuffer "OutBuffer"
               OpMemberName %OutBuffer 0 "outputs"
               OpName %__0 ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpMemberDecorate %Inputs 0 Offset 0
               OpDecorate %_runtimearr_Inputs ArrayStride 8
               OpDecorate %InBuffer BufferBlock
               OpMemberDecorate %InBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %u_image Binding 1
               OpDecorate %u_image DescriptorSet 1
               OpDecorate %u_planeView Binding 0
               OpDecorate %u_planeView DescriptorSet 1
               OpMemberDecorate %Outputs 0 Offset 0
               OpMemberDecorate %Outputs 1 Offset 16
               OpDecorate %_runtimearr_Outputs ArrayStride 32
               OpDecorate %OutBuffer BufferBlock
               OpMemberDecorate %OutBuffer 0 Offset 0
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
     %Inputs = OpTypeStruct %v2float
%_runtimearr_Inputs = OpTypeRuntimeArray %Inputs
   %InBuffer = OpTypeStruct %_runtimearr_Inputs
%_ptr_Uniform_InBuffer = OpTypePointer Uniform %InBuffer
          %_ = OpVariable %_ptr_Uniform_InBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v2float = OpTypePointer Uniform %v2float
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %52 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %53 = OpTypeSampledImage %52
%_ptr_UniformConstant_53 = OpTypePointer UniformConstant %53
    %u_image = OpVariable %_ptr_UniformConstant_53 UniformConstant
    %float_0 = OpConstant %float 0
%u_planeView = OpVariable %_ptr_UniformConstant_53 UniformConstant
    %Outputs = OpTypeStruct %v4float %v4float
%_runtimearr_Outputs = OpTypeRuntimeArray %Outputs
  %OutBuffer = OpTypeStruct %_runtimearr_Outputs
%_ptr_Uniform_OutBuffer = OpTypePointer Uniform %OutBuffer
        %__0 = OpVariable %_ptr_Uniform_OutBuffer Uniform
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
      %int_1 = OpConstant %int 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationNdx = OpVariable %_ptr_Function_uint Function
   %texCoord = OpVariable %_ptr_Function_v2float Function
    %result0 = OpVariable %_ptr_Function_v4float Function
    %result1 = OpVariable %_ptr_Function_v4float Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIMul %uint %15 %18
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %19 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %invocationNdx %33
         %45 = OpLoad %uint %invocationNdx
         %47 = OpAccessChain %_ptr_Uniform_v2float %_ %int_0 %45 %int_0
         %48 = OpLoad %v2float %47
               OpStore %texCoord %48
         %56 = OpLoad %53 %u_image
         %57 = OpLoad %v2float %texCoord
         %59 = OpImageSampleExplicitLod %v4float %56 %57 Lod %float_0
               OpStore %result0 %59
         %62 = OpLoad %53 %u_planeView
         %63 = OpLoad %v2float %texCoord
         %64 = OpImageSampleExplicitLod %v4float %62 %63 Lod %float_0
               OpStore %result1 %64
         %70 = OpLoad %uint %invocationNdx
         %71 = OpLoad %v4float %result0
         %73 = OpAccessChain %_ptr_Uniform_v4float %__0 %int_0 %70 %int_0
               OpStore %73 %71
         %74 = OpLoad %uint %invocationNdx
         %76 = OpLoad %v4float %result1
         %77 = OpAccessChain %_ptr_Uniform_v4float %__0 %int_0 %74 %int_1
               OpStore %77 %76
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `testPlaneView()` chooses the universal queue for fragment cases and the compute queue for compute cases. It creates a 32 by 58 optimal-tiled image with sampled-image and transfer-destination usage.
- The host creates a whole-image view with `VkSamplerYcbcrConversionCreateInfo` using `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY`, `VK_SAMPLER_YCBCR_RANGE_ITU_FULL`, midpoint chroma locations, nearest filtering, and no forced explicit reconstruction.
- The plane view uses the native or compatible plane format and either `VK_IMAGE_ASPECT_PLANE_N_BIT` on the original image or `VK_IMAGE_ASPECT_COLOR_BIT` on the alias image. The alias path binds the selected disjoint allocation to the plane-sized image.
- `uploadImage()` fills the multi-planar image with seeded random channel data and transitions it to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`. The alias image receives a matching read-only layout barrier.
- `ShaderExecutor` runs 500 generated texel-center coordinates. Descriptor sets, descriptor buffers, and descriptor heaps select alternate transport paths without changing the shader's two sampled values.
- The host samples software references with `tcu::Texture2DView::sample()`. It compares whole-image channels separately, then repacks plane outputs through the compatible format and compares them in the selected comparison format.
- A component difference greater than or equal to `0.02f` marks the case as invalid. The test returns `pass("All samples passed")` only when all whole-image and plane samples satisfy the threshold.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `image_view` | Incorrect single-plane aspect view, plane-compatible format reinterpretation, or whole-image versus plane sampling behavior. |
| `memory_alias` | Incorrect disjoint plane binding or image-alias consistency, in addition to the plane-view and sampling causes covered by `image_view`. |

### Cause Analysis

#### Plane view or sampling mismatch

**Possible failure symptoms:** One or more of the 500 whole-image or plane samples differs from its software reference by at least `0.02f`; the log identifies the coordinate, obtained value, and expected value.

**Possible implementation causes:** A device may mishandle the aspect-qualified single-plane view, the compatible format's bit interpretation, the sampler conversion, or the mapping from normalized coordinates to plane memory. The source and Vulkan image-view rules support these as areas for implementation investigation, but the test does not identify a single component as the fault.

#### Disjoint image alias mismatch

**Possible failure symptoms:** A `memory_alias` case reports a plane sample that differs from the selected plane reference, while the alias path has passed its image creation and binding calls.

**Possible implementation causes:** Source inspection and the Vulkan plane-aliasing requirements point to investigation of disjoint plane binding, compatible-format interpretation, matching memory offsets, or plane-derived dimensions. The failure alone does not distinguish among those mechanisms.

## Case Pruning

### Requirement-based pruning

- Formats with one plane are skipped because no plane view can be created.
- The support check requires sampled-image and transfer-destination support for the multi-planar format, midpoint chroma samples for that format, sampled-image and transfer-destination support for the plane-compatible format, and support for the selected shader stage.
- Descriptor-buffer cases require `VK_EXT_descriptor_buffer`; descriptor-heap cases require `VK_EXT_descriptor_heap`. Unsupported executor combinations are skipped.
- The implementation generates `memory_alias` cases only with `VK_IMAGE_CREATE_DISJOINT_BIT`, because the plane allocation must be bound separately.

### Design-based pruning

- `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is present in every case because a compatible image-view format is part of the test design.
- The native plane-compatible format is always included. The additional list is filtered by `formatsAreCompatible()`, which accepts equal pixel sizes in addition to the identical format.
- The format loop includes the core YCbCr range and the 2-plane 4:4:4 extension range, but stops before `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT`.

## Key Takeaways

- `image_view` checks an aspect-qualified view of the original multi-planar image; `memory_alias` checks a compatible image over one disjoint plane allocation.
- The shader keeps the comparison simple: sample the whole image and the selected plane at the same coordinate, then let the host apply format-aware references.
- Compatible-format cases test bit-pattern reinterpretation, so the comparison format must account for padding bits that Vulkan does not require to survive.
- A passing case covers the selected format, plane, stage, descriptor transport, flags, and compatible format. It does not prove unsupported combinations that the generator prunes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createViewTests()` | [factory](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1075-L1078) | Creates the `plane_view` test family. |
| `populateViewGroup()` | [direct registration](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1065-L1071) | Registers `image_view` and `memory_alias`. |
| `populateViewTypeGroup()` | [matrix generation](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L1063) | Generates formats, planes, flags, stages, descriptor modes, and compatible formats. |
| `getShaderSpec()` | [shader specification](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L441-L459) | Defines sampler declarations and the two texture operations. |
| `checkSupport()` | [feature checks](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L486-L501) | Checks image, format, stage, and descriptor-mode requirements. |
| `testPlaneView()` setup | [image and view creation](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L595-L675) | Creates the image, optional alias, conversion, and views. |
| `testPlaneView()` execution | [descriptors and executor](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L718-L842) | Builds descriptor resources and runs the selected shader path. |
| `testPlaneView()` checking | [references and pass/fail](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L845-L943) | Compares whole-image and plane samples and returns the test result. |
| `VkImageView` plane rules | [Vulkan image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L5848-L5865) | Defines compatible formats and plane-derived dimensions. |
| Plane alias rules | [Vulkan plane-alias rules](../../../../vulkan-docs/src/chapters/resources.adoc#L11994-L12015) | Defines the conditions for a single-plane image to alias a multi-planar plane. |
