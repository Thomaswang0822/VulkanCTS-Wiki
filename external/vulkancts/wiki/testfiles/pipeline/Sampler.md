## Overview

**Core question:** Do Vulkan samplers produce the reference image or selected mip level when their sampling state changes?

- This page documents the implementation in [`vktPipelineSamplerTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1) for the `pipeline.sampler` test family.
- Its direct intermediate nodes cover broad sampler-state sampling, exact nearest sampling, an intended separate-stencil-usage variant, delegated border-color swizzling, and the `maxSamplerLodBias` limit.
- The broad sampling cases run an image-sampling reference comparison; the LOD-limit cases make the selected mip level visible with per-level colors.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A combined image sampler pairs an image view with sampler state. The view selects image data and component mapping, while [`VkSamplerCreateInfo`](../../../../vulkan-docs/src/chapters/samplers.adoc#L67-L140) supplies filtering, address modes, border color, and LOD controls.
- Texture LOD derives from shader input plus sampler bias and clamps, and can also be constrained by an image-view minimum LOD ([texture LOD operation](../../../../vulkan-docs/src/chapters/textures.adoc#L1638-L1782)). `maxSamplerLodBias` bounds the sampler and shader bias terms ([limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L554-L566)).

## Registration Hierarchy

```text
pipeline.monolithic.sampler
├── view_type
├── exact_sampling
├── separate_stencil_usage
├── border_swizzle
└── max_sampler_lod_bias
```

[`createSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3174-L3202) registers `view_type` and `border_swizzle` only for monolithic and `shader_object_unlinked_spirv` construction. It registers the other three intermediate nodes for all construction roots. The mustpass files contain 182035 leaves each for monolithic and `shader_object_unlinked_spirv`, and 1526 leaves each for `shader_object_linked_spirv`, `shader_object_unlinked_binary`, `shader_object_linked_binary`, `pipeline_library`, and `fast_linked_library`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Image view | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, plus unnormalized 1D/2D | Selects coordinate dimensionality, subresource arrangement, and applicable sampler state. | [`SamplerViewType`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L77-L99) |
| Format | Color, integer, depth/stencil, and compressed formats | Changes sampling type, reference conversion, and supported combinations. | [`createFormatsSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2790-L3038) |
| Filter and reduction | `NEAREST`, `LINEAR`; `WEIGHTED_AVERAGE`, `MIN`, `MAX` | Changes how texel samples become a result. | [filter generators](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L907-L1163) |
| Mipmap and LOD | `NEAREST`, `LINEAR`; sampler and shader LOD/bias forms | Changes the sampled mip level or interpolation between levels. | [`SamplerLodTest`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L208-L238) |
| Address configuration | U/V/W modes, standard and custom border colors | Determines results outside image coordinates. | [address-mode generator](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1267-L1523) |
| Exact sampling | `gradient`/`solid_color`, normalized/unnormalized, `centered`/`edge_left`/`edge_right` | Narrows nearest sampling to positions with a known exact texel result. | [`createExactSamplingTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3040-L3139) |
| LOD-limit mechanism | `sampler_bias`, `sampler_minlod`, `shader_lod`, `shader_bias`, `view_minlod` | Places maximum bias or a minimum level at a different point in LOD selection. | [LOD-limit registration](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3141-L3171) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below the `sampler` test family.

### view_type: broad sampler-state sampling

This intermediate node varies image-view type, format, filtering, reduction, mipmapping, LOD, and address mode. It renders or dispatches a textured mosaic and compares the output with the reference expected for that configuration.

### exact_sampling: exact nearest-texel selection

This intermediate node uses nearest sampling at texel centers and near selected edges. It checks the resulting pixels exactly rather than accepting a format-aware threshold.

### separate_stencil_usage: depth sampling with separate stencil usage

This intermediate node restricts the broad sampler-state matrix to depth/stencil formats and samples the **depth** aspect. `checkSupportImageSamplingInstance()` queries support with a chained `VkImageStencilUsageCreateInfo` whose stencil usage is `VK_IMAGE_USAGE_TRANSFER_DST_BIT` ([parameter construction](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L299-L325), [support query](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L302-L343)). However, `ImageSamplingInstance` does not retain `separateStencilUsage`, and its runtime `VkImageCreateInfo::pNext` is `nullptr` ([instance construction](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L428-L453), [image creation](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L501-L540)). The executable path therefore samples depth from a normally created depth/stencil image; it neither creates an image with separate stencil usage nor samples stencil values.

### border_swizzle: delegated border color transformation

This intermediate node is registered here but implemented in [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1). It covers `VK_EXT_border_color_swizzle` outside Vulkan SC.

### max_sampler_lod_bias: selected mip level at the device limit

This intermediate node uses nearest filtering and a one-pixel output. It puts `maxSamplerLodBias` in the sampler bias, sampler minimum LOD, shader explicit LOD, shader bias, or image-view minimum LOD position, then identifies the selected level by its color.

## Shader Analysis

### Representative Shader Walkthrough 1

**Representative case:** `dEQP-VK.pipeline.monolithic.sampler.max_sampler_lod_bias.shader_lod_compute`

#### Purpose

The shader requests the LOD supplied in push constants and writes the sampled color to a storage image. This isolates the `SHADER_LOD` branch while the host makes each mip level a distinct color.

#### Parameter Values Chosen

| Parameter | Value | Effect |
|---|---|---|
| Intermediate node | `max_sampler_lod_bias` | Uses the dedicated LOD-limit mechanism. |
| LOD-limit mechanism | `shader_lod` | Emits `textureLod(..., pc.lodLevel)`. |
| Execution path | compute | Uses one 1-by-1 invocation and an output storage image. |
| Construction type | `monolithic` | One of the roots that registers the compute variant. |

#### Structural Design

| Phase | Shader action |
|---|---|
| Coordinate | Converts the global invocation's pixel center to normalized coordinates. |
| Sample | Uses `textureLod` with the requested explicit LOD. |
| Observe | Writes the sampled color to `outImage` for host comparison. |

#### Shader Code

```glsl
#version 460
layout(local_size_x = 1, local_size_y = 1) in;
/// The combined image sampler is descriptor set 0, binding 0.
layout(set = 0, binding = 0) uniform sampler2D texSampler;
/// The output image records the color selected by the explicit LOD.
layout(set = 0, binding = 1, rgba8) uniform writeonly image2D outImage;
layout(push_constant, std430) uniform PushConstantBlock {
    float lodLevel;
    float fbWidth;
    float fbHeight;
} pc;
void main (void) {
    vec2 sampleCoords = vec2((vec2(gl_GlobalInvocationID.xy) + 0.5) / vec2(pc.fbWidth, pc.fbHeight));
    vec4 color = textureLod(texSampler, sampleCoords, pc.lodLevel);
    imageStore(outImage, ivec2(gl_GlobalInvocationID.xy), color);
}
```

#### Parameter Variation Summary

`SAMPLER_BIAS` sets `mipLodBias`, `SAMPLER_MINLOD` sets `minLod`, `SHADER_BIAS` uses the shader bias form in graphics and an equivalent explicit LOD in compute, and `VIEW_MINLOD` chains `VkImageViewMinLodCreateInfoEXT` into the image-view create info. The source requires `VK_EXT_image_view_min_lod` for the last form ([`MaxSamplerLodBiasCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2364-L2383)).

#### SPIR-V

<details>
<summary>SPIR-V assembly</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 58
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %sampleCoords "sampleCoords"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "lodLevel"
               OpMemberName %PushConstantBlock 1 "fbWidth"
               OpMemberName %PushConstantBlock 2 "fbHeight"
               OpName %pc "pc"
               OpName %color "color"
               OpName %texSampler "texSampler"
               OpName %outImage "outImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpMemberDecorate %PushConstantBlock 2 Offset 8
               OpDecorate %texSampler Binding 0
               OpDecorate %texSampler DescriptorSet 0
               OpDecorate %outImage NonReadable
               OpDecorate %outImage Binding 1
               OpDecorate %outImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
  %float_0_5 = OpConstant %float 0.5
%PushConstantBlock = OpTypeStruct %float %float %float
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
      %int_2 = OpConstant %int 2
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %37 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %38 = OpTypeSampledImage %37
%_ptr_UniformConstant_38 = OpTypePointer UniformConstant %38
 %texSampler = OpVariable %_ptr_UniformConstant_38 UniformConstant
      %int_0 = OpConstant %int 0
         %47 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_47 = OpTypePointer UniformConstant %47
   %outImage = OpVariable %_ptr_UniformConstant_47 UniformConstant
      %v2int = OpTypeVector %int 2
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%sampleCoords = OpVariable %_ptr_Function_v2float Function
      %color = OpVariable %_ptr_Function_v4float Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpConvertUToF %v2float %16
         %19 = OpCompositeConstruct %v2float %float_0_5 %float_0_5
         %20 = OpFAdd %v2float %17 %19
         %27 = OpAccessChain %_ptr_PushConstant_float %pc %int_1
         %28 = OpLoad %float %27
         %30 = OpAccessChain %_ptr_PushConstant_float %pc %int_2
         %31 = OpLoad %float %30
         %32 = OpCompositeConstruct %v2float %28 %31
         %33 = OpFDiv %v2float %20 %32
               OpStore %sampleCoords %33
         %41 = OpLoad %38 %texSampler
         %42 = OpLoad %v2float %sampleCoords
         %44 = OpAccessChain %_ptr_PushConstant_float %pc %int_0
         %45 = OpLoad %float %44
         %46 = OpImageSampleExplicitLod %v4float %41 %42 Lod %45
               OpStore %color %46
         %50 = OpLoad %47 %outImage
         %51 = OpLoad %v3uint %gl_GlobalInvocationID
         %52 = OpVectorShuffle %v2uint %51 %51 0 1
         %54 = OpBitcast %v2int %52
         %55 = OpLoad %v4float %color
               OpImageWrite %50 %54 %55
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Generic cases construct `ImageSamplingInstanceParams` with a combined image-sampler descriptor, a view-specific subresource range, generated vertices, sampler create info, and graphics or compute execution ([source](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L289-L353)).
- `SamplerTest::initPrograms()` emits a graphics pair or compute shader. Both sample at coordinates appropriate to the image-view type and transform sampled values into the comparison representation ([source](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L375-L508)).
- `exact_sampling` enumerates the selected formats, input content, coordinate convention, and edge offsets. A compute leaf is added only when the format is storage-compatible and the construction type permits it.
- The LOD-limit runtime reads `maxSamplerLodBias`, creates an image with all available mip levels, clears each level to a deterministic distinct color, samples it, copies the result, and compares the one-pixel result against the expected level with threshold `0.005` ([runtime](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2462-L2783)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `view_type` | Filter, reduction, mipmap, address, image-view, coordinate, or format conversion behavior differs from the reference. |
| `exact_sampling` | Nearest texel selection or edge-coordinate handling differs from the exact expected texel. |
| `separate_stencil_usage` | The format-support query accepts the intended separate-usage configuration, but the subsequently executed ordinary depth-sampling comparison fails. The current runtime does not isolate separate-stencil-usage behavior. |
| `border_swizzle` | `VK_EXT_border_color_swizzle` handling differs from its delegated test's expected border result. |
| `max_sampler_lod_bias` | A sampler, shader, or image-view LOD contribution does not select the expected mip level. |

### Cause Analysis

#### Sampler-state or reference mismatch

**Possible failure symptoms:** A broad `view_type` result differs from the format-aware reference, potentially only for one filter, reduction mode, LOD configuration, address mode, view type, or format.

**Possible implementation causes:** The sampled result may not apply the configured state or image-view component mapping correctly. The source combines these dimensions in one image-sampling comparison, so this symptom localizes the problem to that operation shape rather than proving one isolated sampler field is defective.

#### Nearest-coordinate selection mismatch

**Possible failure symptoms:** An `exact_sampling` leaf returns a neighboring or otherwise wrong texel at `centered`, `edge_left`, or `edge_right`.

**Possible implementation causes:** The nearest-sample coordinate interpretation or edge handling can disagree with the tested coordinate convention. The exact comparison makes this family more localized than the broad reference comparisons.

#### Separate-stencil view usage mismatch

**Possible failure symptoms:** A `separate_stencil_usage` leaf is skipped because the separate-usage format query is unsupported, or its ordinary depth-sampling image comparison differs.

**Possible implementation causes:** A skip can reflect lack of support for the queried separate depth/stencil usage combination. An executed-case mismatch points to the ordinary depth-sampling, format-conversion, or reference-comparison path, not to runtime handling of `VkImageStencilUsageCreateInfo`: the runtime image is created without that structure. These cases do not read or compare stencil values.

#### Border-color swizzle mismatch

**Possible failure symptoms:** A delegated `border_swizzle` leaf returns an unexpected border component ordering or constant.

**Possible implementation causes:** The delegated implementation owns detailed diagnosis. A failure indicates that its extension-specific border-color result did not match its expected transformed value.

#### LOD contribution or clamp mismatch

**Possible failure symptoms:** A `max_sampler_lod_bias` leaf returns the color assigned to a mip level other than the expected accessible level.

**Possible implementation causes:** The implementation may apply sampler bias, shader LOD or bias, sampler minimum LOD, or image-view minimum LOD at the wrong point in level selection. The LOD-limit runtime holds the image and nearest filter fixed and changes the mechanism, so failures can be compared by mechanism. The specification constrains `mipLodBias` by `maxSamplerLodBias` ([sampler validity](../../../../vulkan-docs/src/chapters/samplers.adoc#L223-L225)).

## Case Pruning

### Requirement-based pruning

- `VIEW_MINLOD` requires `VK_EXT_image_view_min_lod`; it is omitted in Vulkan SC builds.
- `separate_stencil_usage` requires `VK_EXT_separate_stencil_usage` and a successful format-support query for sampled depth usage with transfer-only stencil usage. The queried chain is not carried into runtime image creation.
- ASTC 3D formats, selected maintenance functionality, image sampling support, construction-type requirements, and an exclusive compute queue are checked before affected cases run.
- Unnormalized-coordinate samplers must satisfy Vulkan's state restrictions, including no minification filtering or mipmapping ([valid usage](../../../../vulkan-docs/src/chapters/samplers.adoc#L250-L268)).

### Design-based pruning

- `view_type` and `border_swizzle` are intentionally generated only for monolithic and `shader_object_unlinked_spirv` construction.
- Cube and cube-array cases omit address-mode coverage, and compressed formats omit selected minification and reduction cases to avoid unsuitable noisy comparisons.
- Compute variants are emitted only when the construction path and format are compatible.

## Key Takeaways

- The `sampler` test family tests sampler-visible results, not only object creation.
- Broad cases establish behavior across a large state matrix, while `exact_sampling` and `max_sampler_lod_bias` sharpen two specific observables.
- The LOD-limit cases distinguish where LOD control enters the calculation by making the selected mip color observable.
- `border_swizzle` remains an accurately marked delegated intermediate node rather than being attributed to this implementation file.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Sampler parameters and generated shaders | [`SamplerTest`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L289-L508) | Builds the common resource, sampler, and graphics/compute sampling paths. |
| Matrix registration | [`createFormatsSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2790-L3038) | Generates `view_type` combinations. |
| Exact-sampling registration | [`createExactSamplingTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3040-L3139) | Defines exact input and coordinate variations. |
| LOD-limit shaders and runtime | [`MaxSamplerLodBiasCase`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2364-L2783) | Generates mechanism-specific shaders and checks the selected mip color. |
| Family registration | [`createSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3174-L3202) | Registers the five direct intermediate nodes. |
| Delegated border swizzle | [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1) | Implements the delegated extension-specific intermediate node. |
