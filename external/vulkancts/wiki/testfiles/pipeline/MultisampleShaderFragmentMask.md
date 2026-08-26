## Overview

**Core question:** Does the implementation use `fragmentMaskFetchAMD` to recover the correct fragment for every multisample value?

- `vktPipelineMultisampleShaderFragmentMaskTests.cpp` implements the `shader_fragment_mask` test family under `multisample`.
- Each direct intermediate node selects 2, 4, 8, or 16 color samples. Leaves vary the source form, format, and pipeline construction type.
- The test renders a multisampled image, reads it through the AMD fragment-mask operations, reads it again with ordinary multisample texel fetches, and compares every packed sample value.
- The page focuses on extension shader behavior, resource flow, and the limits of failure localization.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VK_AMD_shader_fragment_mask` provides shader access to a fragment mask associated with a compressed multisampled color surface. [`fragmentMaskFetchAMD`](../../../../vulkan-docs/src/appendices/VK_AMD_shader_fragment_mask.adoc#L21-L38) returns a `uint` whose four-bit fields identify the fragment corresponding to each color sample; `fragmentFetchAMD` then reads that fragment.
- `VkPipelineMultisampleStateCreateInfo::rasterizationSamples` defines the rasterization sample count. For the render-pass paths used here, Vulkan requires that value to match the color attachment sample count. See [multisample state](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2201) and [attachment compatibility](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3016-L3020).

## Registration Hierarchy

The source function [`createMultisampleShaderFragmentMaskTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1393-L1401) creates the `shader_fragment_mask` test family. The parent [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7727-L7728) attaches it below `multisample`.

```text
pipeline.monolithic.multisample.shader_fragment_mask
├── samples_2
├── samples_4
├── samples_8
└── samples_16
```

The same family is registered below the other pipeline construction roots. The `shader-object-*` mustpass files exclude `subpass_input`; the ordinary render-pass construction files include it.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16` | Selects the number of four-bit fragment-mask fields and the attachment's `VkSampleCountFlagBits`. | [`createShaderFragmentMaskTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1336-L1341) |
| Source form | `image_2d`, `image_2d_array`, `subpass_input` | Chooses a multisampled image, a layered multisampled image, or a multisampled input attachment. | [`SourceCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1343-L1352) |
| Color format | `r8g8b8a8_unorm`, `r32_uint`, `r32_sint` | Selects GLSL image type, buffer representation, packing, and integer or UNORM comparison data. | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L365-L400) |
| Pipeline construction | `monolithic`, `pipeline_library`, `fast_linked_library`, and shader-object variants | Exercises the same behavior through supported CTS pipeline construction paths. | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L292-L301) |
| Image extent | `32 x 32` | Gives the compute path one workgroup per pixel and fixes the packed output indexing. | [`createShaderFragmentMaskTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1374-L1379) |
| Layer count | `1` for `image_2d` and `subpass_input`, `3` for `image_2d_array` | Tests both a single image layer and layer-aware sample extraction. | [`SourceCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1343-L1352) |

The default mustpass files contain 36 leaves for monolithic, pipeline-library, and fast-linked-library construction, and 24 leaves for each shader-object construction file. The 12-leaf difference comes from omitting the three `subpass_input` format leaves for each of the four sample counts.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node under the `shader_fragment_mask` test family. Each node changes the attachment sample count and the number of sample indices visited by the shaders.

### `samples_2`: two-sample access

The shaders decode two four-bit mask fields and compare two samples per pixel. This is the smallest supported matrix value and checks the basic mask-to-fragment mapping.

### `samples_4`: four-sample access

The shaders decode four fields and compare four samples per pixel. The representative shader below uses this value.

### `samples_8`: eight-sample access

The shaders decode eight fields, including fields through bits 28 to 31 of the returned mask. This exercises the wider mask representation described by the extension.

### `samples_16`: sixteen-sample access

The shaders launch or iterate over sixteen sample indices and the host compares sixteen values per pixel. This case needs a source-level caveat: the extension returns one 32-bit `uint`, so it contains only eight four-bit fields. The generated expression still evaluates `mask >> (4 * sampleNdx)` for indices 8 through 15, where the shift count is at least 32. The page therefore does not describe this case as decoding sixteen distinct mask fields; the registered source would need separate analysis to establish meaningful behavior for those upper indices.

## Shader Analysis

The source generates a draw vertex/fragment pair and then either a compute comparison pair or a subpass-input fragment shader. The central shader operation is the same in both access paths: obtain the mask, select the four-bit field for one sample, fetch the referenced fragment, and store the value for host comparison.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.multisample.shader_fragment_mask.samples_4.image_2d.r32_uint
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Sample count | `samples_4` |
| Source form | `image_2d` |
| Format | `r32_uint`, so the shader uses `usampler2DMS` and `uint` storage |
| Extent | `32 x 32` |

#### Purpose

This compute shader creates the extension-based result used by the `image_2d` and `image_2d_array` paths. The host later runs the same image through ordinary `texelFetch` and compares the packed values.

#### Structural Design

| Shader phase | Operation |
|---|---|
| Workgroup mapping | One compute workgroup covers one pixel. Its four local invocations identify sample indices `0` through `3`. |
| Mask lookup | `fragmentMaskFetchAMD` returns the packed fragment-index table for the pixel. |
| Sample lookup | A right shift and `& 0xf` select the four-bit fragment index for the invocation's sample. |
| Result write | `fragmentFetchAMD` reads the selected `uvec4`; the first component is written to the packed storage buffer. |

#### Shader Code

```glsl
#version 450
#extension GL_AMD_shader_fragment_mask : enable
#define NUM_SAMPLES 4
layout(local_size_x = NUM_SAMPLES) in;
layout(set = 0, binding = 0) uniform usampler2DMS u_image;
layout(set = 0, binding = 1, std430) writeonly buffer ColorOutput {
    uint color[];
} sb_out;

void main(void)
{
    int sampleNdx = int(gl_LocalInvocationID.x);
    int colorOutNdx = NUM_SAMPLES * int(gl_WorkGroupID.x +
        gl_WorkGroupID.y * gl_NumWorkGroups.x +
        gl_WorkGroupID.z * gl_NumWorkGroups.x * gl_NumWorkGroups.y);

    uint mask = fragmentMaskFetchAMD(u_image, ivec2(gl_WorkGroupID.xy));
    int fragNdx = int((mask >> (4 * sampleNdx)) & 0xf);
    uvec4 color = fragmentFetchAMD(u_image, ivec2(gl_WorkGroupID.xy), fragNdx);
    sb_out.color[colorOutNdx + sampleNdx] = uint(color);
}
```

#### Additional Info

- The source emits `comp_fmask_fetch` only for image source cases. `subpass_input` uses `frag_fmask_fetch` because input attachments are read inside a render pass.
- The ordinary reference shader uses the same resource layout but calls `texelFetch(u_image, samplingPos, sampleNdx)` instead of the AMD operations.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Sample count | `samples_2`, `samples_8`, and `samples_16` change `NUM_SAMPLES`, the local workgroup size, and the number of mask fields visited. | [`createShaderFragmentMaskTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1336-L1341) |
| Color format | `r8g8b8a8_unorm` changes the sampled value to `vec4` and packs it with `packUnorm4x8`; `r32_sint` uses signed image and buffer types. | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L365-L400) |
| Source form: `image_2d_array` | `image_2d_array` changes the coordinate to `ivec3` and includes the layer in the workgroup and output-buffer index. | [`SourceCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1343-L1352) |
| Source form: `subpass_input` | `subpass_input` moves the mask and fragment fetches into a fragment shader and writes the buffer during a second render-pass subpass. | [`SourceCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1343-L1352) |

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
; Bound: 90
; Schema: 0
               OpCapability Shader
               OpCapability FragmentMaskAMD
               OpExtension "SPV_AMD_shader_fragment_mask"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID %gl_WorkGroupID %gl_NumWorkGroups
               OpExecutionMode %main LocalSize 4 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_AMD_shader_fragment_mask"
               OpName %main "main"
               OpName %sampleNdx "sampleNdx"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %colorOutNdx "colorOutNdx"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %mask "mask"
               OpName %u_image "u_image"
               OpName %fragNdx "fragNdx"
               OpName %color "color"
               OpName %ColorOutput "ColorOutput"
               OpMemberName %ColorOutput 0 "color"
               OpName %sb_out "sb_out"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %u_image Binding 0
               OpDecorate %u_image DescriptorSet 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %ColorOutput BufferBlock
               OpMemberDecorate %ColorOutput 0 NonReadable
               OpMemberDecorate %ColorOutput 0 Offset 0
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 1
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
      %int_4 = OpConstant %int 4
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Function_uint = OpTypePointer Function %uint
         %45 = OpTypeImage %uint 2D 0 0 1 1 Unknown
         %46 = OpTypeSampledImage %45
%_ptr_UniformConstant_46 = OpTypePointer UniformConstant %46
    %u_image = OpVariable %_ptr_UniformConstant_46 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
    %uint_15 = OpConstant %uint 15
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
%ColorOutput = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_ColorOutput = OpTypePointer Uniform %ColorOutput
     %sb_out = OpVariable %_ptr_Uniform_ColorOutput Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_4 = OpConstant %uint 4
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_4 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %sampleNdx = OpVariable %_ptr_Function_int Function
%colorOutNdx = OpVariable %_ptr_Function_int Function
       %mask = OpVariable %_ptr_Function_uint Function
    %fragNdx = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4uint Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %sampleNdx %17
         %21 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %22 = OpLoad %uint %21
         %24 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %25 = OpLoad %uint %24
         %27 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %25 %28
         %30 = OpIAdd %uint %22 %29
         %32 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %33 = OpLoad %uint %32
         %34 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %35 = OpLoad %uint %34
         %36 = OpIMul %uint %33 %35
         %37 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %38 = OpLoad %uint %37
         %39 = OpIMul %uint %36 %38
         %40 = OpIAdd %uint %30 %39
         %41 = OpBitcast %int %40
         %42 = OpIMul %int %int_4 %41
               OpStore %colorOutNdx %42
         %49 = OpLoad %46 %u_image
         %51 = OpLoad %v3uint %gl_WorkGroupID
         %52 = OpVectorShuffle %v2uint %51 %51 0 1
         %54 = OpBitcast %v2int %52
         %55 = OpImage %45 %49
         %56 = OpFragmentMaskFetchAMD %uint %55 %54
               OpStore %mask %56
         %58 = OpLoad %uint %mask
         %59 = OpLoad %int %sampleNdx
         %60 = OpIMul %int %int_4 %59
         %61 = OpShiftRightLogical %uint %58 %60
         %63 = OpBitwiseAnd %uint %61 %uint_15
         %64 = OpBitcast %int %63
               OpStore %fragNdx %64
         %68 = OpLoad %46 %u_image
         %69 = OpLoad %v3uint %gl_WorkGroupID
         %70 = OpVectorShuffle %v2uint %69 %69 0 1
         %71 = OpBitcast %v2int %70
         %72 = OpLoad %int %fragNdx
         %73 = OpBitcast %uint %72
         %74 = OpImage %45 %68
         %75 = OpFragmentFetchAMD %v4uint %74 %71 %73
               OpStore %color %75
         %81 = OpLoad %int %colorOutNdx
         %82 = OpLoad %int %sampleNdx
         %83 = OpIAdd %int %81 %82
         %84 = OpLoad %v4uint %color
         %85 = OpCompositeExtract %uint %84 0
         %87 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %83
               OpStore %87 %85
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. `test()` allocates a multisampled color image with `COLOR_ATTACHMENT` and `SAMPLED` usage. `subpass_input` additionally requires `INPUT_ATTACHMENT` usage. The color buffer is host visible and stores samples contiguously per pixel, then per layer.
2. `draw()` renders the image for `image_2d` and `image_2d_array`. `drawAndSampleInputAttachment()` performs a color-attachment subpass followed by an input-attachment subpass for `subpass_input`.
3. The extension path writes one value per sample to the result buffer. The compute path uses a compute-to-host buffer barrier; the subpass path uses a fragment-to-host barrier before submission completes.
4. The host saves and clears the extension result, dispatches `comp_fetch`, invalidates mapped memory, and compares every layer/sample view with `tcu::intThresholdCompare` and a zero threshold. Any mismatch returns `Some texels were incorrect`; otherwise the case passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `samples_2` | Incorrect two-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_4` | Incorrect four-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_8` | Incorrect eight-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_16` | A mismatch in the sixteen-sample path, including the source's upper-index shift behavior, or a shared render, image-access, synchronization, or comparison defect. This result alone does not establish incorrect decoding of sixteen distinct fields because the returned mask is only 32 bits. |

The final comparison identifies the sample-count behavior and mismatching layer/sample views, but it cannot isolate one exclusive fault location.

### Cause Analysis

#### Fragment-mask mapping or fragment fetch

**Possible failure symptoms:** One or more packed sample values differ between the AMD extension path and ordinary `texelFetch`; the log names the affected layer and sample.

**Possible implementation causes:** The implementation may return an incorrect four-bit mapping, lower `fragmentMaskFetchAMD` or `fragmentFetchAMD` incorrectly, or read the wrong compressed-surface fragment for the selected sample. The extension specification describes the mask as the sample-to-fragment lookup table, so a mismatch in this path is consistent with a mapping or fetch defect. The final image cannot distinguish those two operations.

#### Render, resource, or synchronization path

**Possible failure symptoms:** Mismatches appear across many samples, layers, formats, or source forms, or the reference and extension buffers disagree after the dispatch/subpass completes.

**Possible implementation causes:** Rasterization may produce different source data, an image view or descriptor may select the wrong layer, or the buffer visibility chain may expose stale writes. The host waits for submission completion and invalidates mapped memory, while the command buffer inserts shader-write to host-read barriers. Source-level investigation is needed to separate these possibilities from an extension implementation defect.

#### Format or pipeline-construction variation

**Possible failure symptoms:** Only `r8g8b8a8_unorm`, `r32_uint`, `r32_sint`, or one pipeline construction type fails.

**Possible implementation causes:** The failure may involve format-specific image access or packing, signed versus unsigned lowering, or a pipeline construction path that does not preserve the fragment shader interface and multisample state. The CTS selects the corresponding format and construction requirements before execution, so a narrow failure pattern is evidence for that variant boundary rather than a universal cause.

## Case Pruning

### Requirement-based pruning

- `checkRequirements()` requires `VK_KHR_get_physical_device_properties2` and `VK_AMD_shader_fragment_mask`.
- The device must support the selected count in `framebufferColorSampleCounts` and the relevant sampled-image count limit, integer or color.
- `subpass_input` requires `fragmentStoresAndAtomics` because its fragment shader writes the result buffer.
- Unsupported pipeline construction requirements cause the case to be skipped.

### Design-based pruning

- The format list is fixed to `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R32_UINT`, and `VK_FORMAT_R32_SINT`, the formats selected by the source matrix.
- `subpass_input` is omitted for shader-object construction types because input attachments cannot be used with dynamic rendering.
- The sample counts are fixed to 2, 4, 8, and 16 by the source matrix. Counts through 8 exercise the fields available in the 32-bit packed mask; the 16-sample case also executes the upper-index shift behavior noted above.

## Key Takeaways

- The test compares two reads of the same multisampled image: the AMD fragment-mask route and ordinary per-sample texel fetch.
- A four-bit mask field maps one color sample to a stored fragment index; the test must apply that mapping before fetching the color.
- `image_2d`, `image_2d_array`, and `subpass_input` cover different shader-visible access forms, while the sample-count intermediate nodes control the attachment sample count and number of shader sample accesses.
- Exact packed-buffer comparison makes even one incorrect layer/sample value a failure, but the result does not prove which internal stage produced it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `checkRequirements` | [`vktPipelineMultisampleShaderFragmentMaskTests.cpp#L307-L344`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L307-L344) | Extension, sample-count, feature, and construction checks. |
| Shader generation | [`initPrograms#L365-L570`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L365-L570) | Emits draw, FMASK, and ordinary-fetch shaders. |
| Input-attachment path | [`drawAndSampleInputAttachment#L599-L912`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L599-L912) | Runs draw and FMASK fetch in dependent subpasses. |
| Compute and comparison flow | [`test#L1214-L1318`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1214-L1318) | Creates resources, runs both paths, and compares samples. |
| Matrix registration | [`createShaderFragmentMaskTestsInGroup#L1326-L1389`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1326-L1389) | Defines sample, source, format, and extent values. |
| Extension registration | [`createMultisampleShaderFragmentMaskTests#L1393-L1401`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1393-L1401) | Creates the `shader_fragment_mask` test family. |
| Extension semantics | [`VK_AMD_shader_fragment_mask.adoc#L21-L38`](../../../../vulkan-docs/src/appendices/VK_AMD_shader_fragment_mask.adoc#L21-L38) | Defines mask fields and fragment fetch operations. |
| Extension example | [`VK_AMD_shader_fragment_mask.adoc#L46-L82`](../../../../vulkan-docs/src/appendices/VK_AMD_shader_fragment_mask.adoc#L46-L82) | Shows image, array, and subpass-input forms. |
