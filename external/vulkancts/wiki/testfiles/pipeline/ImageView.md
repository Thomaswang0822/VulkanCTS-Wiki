## Overview

**Core question:** Does sampling through each tested image view expose the selected channels, mip levels, and array layers for its view type and format?

- [`vktPipelineImageViewTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1) implements the `pipeline.*.image_view` test family.
- The source builds image views over initialized sampled images, samples them through graphics and compute work, and validates the output against format-aware software lookups.
- The two intermediate nodes under each view-type and format path test component remapping and subresource selection.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- An image view supplies the type and format used to interpret an image, a `VkComponentMapping`, and a `VkImageSubresourceRange`. The range selects the mipmap levels and array layers that the view exposes. [Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#L5788-L5809) defines these fields.
- A sampled-image shader accesses the view rather than the whole image. The suite uses nearest filtering and nearest mipmap selection, so its reference lookup can isolate view selection instead of filtering quality.
- `VK_REMAINING_MIP_LEVELS` and `VK_REMAINING_ARRAY_LAYERS` make a view range extend from the given base value to the available end of the image.

## Registration Hierarchy

```text
pipeline.monolithic.image_view
└── view_type
```

[`createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L760-L1000) builds the same hierarchy for monolithic and `shader_object_unlinked_spirv` construction variants. The direct `view_type` intermediate node contains the seven view-type groups; each then contains `format`, a concrete format, and the two property nodes documented below. The main Vulkan mustpass list contains 27,708 `pipeline.monolithic.image_view` leaves and 27,708 `pipeline.shader_object_unlinked_spirv.image_view` leaves. The Vulkan SC monolithic list contains 26,736 leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| View type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array` | Selects the image-view type, matching GLSL sampler type, image extent, layer count, coordinate components, and type-specific range cases. | [`imageViewTypes`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L762-L772), [`getGlslSamplerType()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L318-L363) |
| Format | Uncompressed, packed, floating-point, integer, ETC2, EAC, ASTC 2D, and BC5 formats; ASTC 3D formats for `3d` outside Vulkan SC | Selects texture data interpretation and lookup precision. | [format arrays](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L774-L938) |
| Intermediate node | `component_swizzle`, `subresource_range` | Selects the image-view property under test. | [factory assembly](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L940-L1000) |
| Component mapping | Four cyclic RGBA mappings: `r_g_b_a`, `g_b_a_r`, `b_a_r_g`, `a_r_g_b` | Remaps sampled color components in the image view. | [`getComponentMappingPermutations()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L658-L700) |
| Subresource range | Type-specific base mip level, mip count, base array layer, layer count, and `VK_REMAINING_*` combinations | Limits the visible subresources and drives explicit-LOD cases. | [`createSubresourceRangeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L425-L655) |
| Execution path | ordinary leaf and `_compute` counterpart | Samples the same view through graphics or compute execution. | [range leaf helper](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L444-L458), [swizzle leaf helper](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L741-L753) |

## Behavior Parameters

The primary behavioral axis is the intermediate node below each concrete view-type and format path. View type and format establish the object shape and data representation; the selected intermediate node decides whether the leaf checks component remapping or subresource visibility.

### `component_swizzle`: component remapping

This intermediate node creates a view over the complete valid range and changes only the four-component mapping. The source rotates the identity RGBA mapping four times. The generated shader samples the matching sampler type and applies a scale and bias that the host has remapped with the same mapping, so a channel-selection error changes the observed values.

### `subresource_range`: visible mip levels and array layers

This intermediate node retains identity component mapping and changes the view range. Cases select bounded mip ranges, bounded array-layer ranges, combinations of both, and `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS`. Some leaves call `textureLod()` with LOD 4.0. The other generated shaders call `texture()`: the fragment path uses implicit level-of-detail selection, while the compute path has no explicit LOD operand. The software reference uses LOD 0.0 for those no-explicit-LOD cases. The registered combinations differ by view type because arrays, cube faces, and 3D images have different legal layer models.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.image_view.view_type.1d.format.a1b5g5r5_unorm_pack16.component_swizzle.a_r_g_b
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` graphics path | Generates the vertex/fragment pair and samples into a color attachment through a monolithic graphics pipeline. |
| `view_type.1d` | Selects `sampler1D`; the fragment shader therefore consumes only the `x` component of the interpolated texture coordinate. |
| `a1b5g5r5_unorm_pack16` | Selects a normalized floating-point sampler and identity lookup scale/bias values. The format requires `VK_KHR_maintenance5` outside Vulkan SC. |
| `component_swizzle.a_r_g_b` | Makes the image view return source alpha, red, green, and blue as the sampled result's R, G, B, and A components, respectively. |
| No `_compute` suffix and sampler LOD `0.0` | Uses fragment sampling with implicit LOD rather than the compute shader or `textureLod()`. |

#### Purpose

This shader samples a 1D packed UNORM image through a view whose component mapping rotates ARGB into the shader-visible RGBA result. The rendered output lets the software reference detect an incorrect view swizzle, format interpretation, or sampler/view-type pairing.

#### Structural Design

| Shader element | Exact representative-case role |
|----------------|--------------------------------|
| `sampler1D texSampler` | Combined image sampler for the tested 1D image view at set 0, binding 0. |
| `vtxTexCoords.x` | One-dimensional coordinate selected from the vertex shader's interpolated mosaic coordinate. |
| `texture(...)` | Performs implicit-LOD sampling through the component-swizzled image view. |
| Scale `vec4(1.0)` and bias `vec4(0.0)` | Preserve the normalized A1B5G5R5 sample for color-attachment output. |
| `fragColor` | Carries the shader-visible swizzled sample to the host-side image validator. |

#### Shader Code

```glsl
#version 440
/// The combined sampler exposes the tested 1D view at descriptor set 0, binding 0.
layout(set = 0, binding = 0) uniform highp sampler1D texSampler;
/// The vertex stage supplies a vec4 mosaic coordinate; a 1D view consumes only x.
layout(location = 0) in highp vec4 vtxTexCoords;
/// The sampled and normalized value is written to the sole color attachment.
layout(location = 0) out highp vec4 fragColor;
void main (void)
{
    /// Sample through the A1B5G5R5 view; the view applies the A,R,G,B component mapping.
    fragColor = texture(texSampler, vtxTexCoords.x) * vec4(1.000000e+00, 1.000000e+00, 1.000000e+00, 1.000000e+00) + vec4(0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00);
}
```

#### Additional Info

- The graphics vertex shader is fixed for this leaf: it writes the input position to `gl_Position` and forwards the input texture-coordinate vector unchanged to location 0 ([generated graphics shaders](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L271-L307)).
- `createComponentSwizzleTests()` gives these leaves the complete mip and layer range and sampler LOD `0.0`, so this representative isolates component mapping rather than subresource selection ([component-swizzle construction](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L702-L753)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| View type | Changes the sampler declaration and selects `.x`, `.xy`, `.xyz`, or `.xyzw` coordinates. | [`getGlslSamplerType()` and coordinate selection](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L194-L214) |
| Format class | Adds `i` or `u` to the sampler for signed or unsigned integer formats; format normalization also changes the emitted scale and bias. | [`getGlslSamplerType()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L318-L363), [`initPrograms()` scale/bias setup](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L179-L193) |
| Subresource-range case | A positive sampler LOD replaces `texture()` with `textureLod()` and embeds that LOD as a fixed decimal value. | [sample-call generation](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L287-L304) |
| Graphics versus compute | The `_compute` leaf replaces the vertex/fragment pair with a compute shader that reconstructs mosaic coordinates from a storage buffer and writes a storage image. | [compute shader generation](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L216-L270) |
| Component mapping | Does not change the sample expression's coordinate or sampler type, but changes the image-view result and rotates the generated scale and bias to match it. | [mapping and scale/bias generation](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L169-L193) |

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
; Bound: 29
; Schema: 0
               OpCapability Shader
               OpCapability Sampled1D
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fragColor %vtxTexCoords
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 440
               OpName %main "main"
               OpName %fragColor "fragColor"
               OpName %texSampler "texSampler"
               OpName %vtxTexCoords "vtxTexCoords"
               OpDecorate %fragColor Location 0
               OpDecorate %texSampler Binding 0
               OpDecorate %texSampler DescriptorSet 0
               OpDecorate %vtxTexCoords Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %fragColor = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 1D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
 %texSampler = OpVariable %_ptr_UniformConstant_11 UniformConstant
%_ptr_Input_v4float = OpTypePointer Input %v4float
%vtxTexCoords = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
    %float_1 = OpConstant %float 1
         %24 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
    %float_0 = OpConstant %float 0
         %27 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %texSampler
         %20 = OpAccessChain %_ptr_Input_float %vtxTexCoords %uint_0
         %21 = OpLoad %float %20
         %22 = OpImageSampleImplicitLod %v4float %14 %21
         %25 = OpFMul %v4float %22 %24
         %28 = OpFAdd %v4float %25 %27
               OpStore %fragColor %28
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test case packages the selected view type, format, mapping, range, sampler LOD, and execution mode into `ImageSamplingInstanceParams`. It fixes nearest minification, magnification, and mipmap filtering, clamp-to-edge addressing, and a `maxLod` derived from the view's `levelCount`.
- `ImageSamplingInstance::setup()` creates the sampled source image, initializes a test texture for all available mip levels and layers, uploads it, and creates `VkImageViewCreateInfo` with the selected `viewType`, `format`, `components`, and `subresourceRange`. It binds the view with a sampler as a combined image sampler.
- The graphics path writes sampled colors to a color-attachment output image. The compute path writes them to a storage output image. `iterate()` records setup work, submits the command buffer, and waits for completion before validation.
- `verifyImage()` uses `ReferenceRenderer` to reproduce the texture coordinates, resolves the selected source-image range, computes the nearest-filter lookup bounds and precision threshold for the chosen format, and validates the output image with `tcu::isLookupResultValid`. All four result components are checked for this family; the shared validator's reduced component mask applies only to sampler reduction-mode cases, which these tests do not create. The validator also includes an sRGB tolerance adjustment.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `component_swizzle` | Image-view component remapping, format interpretation, sampler-type selection, or the graphics/compute sampling path returns channels different from the selected `VkComponentMapping`. |
| `subresource_range` | Image-view mip-level or array-layer selection, `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS` resolution, explicit-LOD sampling, or range-derived LOD clamping selects data outside the view. |

### Cause Analysis

#### Component mapping or format interpretation

**Possible failure symptoms:** Only `component_swizzle` leaves fail, often for one channel rotation, format class, or execution path. The observed sampled colors differ from the remapped reference values.

**Possible implementation causes:** The implementation may apply `VkComponentMapping` in the wrong component order, mishandle the selected view format, bind an incompatible sampler type, or execute the graphics and compute sampling paths differently. The image-view contract assigns component remapping to `VkImageViewCreateInfo::components`; source-level investigation is needed to distinguish sampling hardware from output or readback handling.

#### Mip-level or array-layer range selection

**Possible failure symptoms:** Only `subresource_range` leaves fail, especially explicit-LOD cases, a nonzero base mip level, a nonzero base array layer, or a remaining-range suffix.

**Possible implementation causes:** The implementation may resolve base/count fields or `VK_REMAINING_*` values incorrectly, expose subresources outside the view, clamp explicit LOD to the wrong interval, or select cube faces or array layers with the wrong unit. The specification defines `subresourceRange` as the set of accessible mipmap levels and array layers; the final output alone cannot separate view selection from shader sampling or transfer-readback faults.

#### View-type-specific image setup

**Possible failure symptoms:** Failures cluster by `1d`, array, `3d`, cube, or cube-array view type, while other types pass.

**Possible implementation causes:** The implementation may create an incompatible image type, extent, layer count, cube-compatible image, coordinate interpretation, or sampler declaration for the selected view type. The CTS setup derives those properties from the view type, so source-level investigation should compare image creation, view creation, descriptor binding, and the affected execution path.

## Case Pruning

### Requirement-based pruning

- Each leaf calls `checkSupportImageSamplingInstance()` for the derived image and sampling parameters. Graphics leaves require the selected pipeline-construction path; compute leaves require the corresponding shader-object construction path.
- ASTC 3D leaves occur only outside Vulkan SC and call `checkSupportAstcFormat()`. `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` outside Vulkan SC.
- The source stops adding compressed formats for `1d` and `1d_array`, and it adds ASTC 3D formats only to `3d`.

### Design-based pruning

- The four cyclic component mappings provide a bounded channel-order matrix instead of all possible `VkComponentMapping` values.
- Each property leaf has one graphics and one `_compute` path, allowing the suite to compare execution models without multiplying the view-property matrix further.
- Subresource-range cases target boundaries and representative combinations: nonzero base values, fixed counts, cube face groups, and remaining-range constants. They do not enumerate every valid range.

## Key Takeaways

- An image view controls both how a shader interprets texels and which mip levels and array layers it can access.
- `component_swizzle` isolates `VkComponentMapping`; `subresource_range` isolates the view's visible subresources and LOD boundaries.
- The suite samples one view matrix through graphics and compute paths, then uses a format-aware software lookup oracle rather than a raw pixel equality check.
- View type changes resource shape, coordinates, and sampler declaration, so type-specific range combinations are part of the intended coverage.

## Source Reference Appendix

| Entry point or contract | Link | Why it matters |
|-------------------------|------|----------------|
| Test parameters, program generation, and support checks | [`ImageViewTest`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L60-L315) | Defines selected parameters, generated graphics/compute source, and requirements. |
| Type helpers and range registration | [`getGlslSamplerType()` through `createSubresourceRangeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L318-L655) | Defines sampler choice, image shape, and type-specific subresource cases. |
| Component mappings and family registration | [`getComponentMappingPermutations()` through `createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L658-L1000) | Defines swizzle leaves, view types, formats, and hierarchy assembly. |
| Pipeline-category registration | [`createPipelineTests()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L100-L125) | Registers the family only for monolithic and shader-object-unlinked-SPIR-V variants. |
| Shared image setup and image-view creation | [`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L455-L560) | Creates images, uploads data, and creates the tested view. |
| Submission and result validation | [`ImageSamplingInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1029-L1039) and [`verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1640-L1704) | Waits for execution and performs the reference lookup validation. |
| Vulkan image-view contract | [`Image Views`](../../../../vulkan-docs/src/chapters/resources.adoc#L5733-L5859) | Defines image-view creation and the tested fields. |
