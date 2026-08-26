## Overview

**Core question:** When an input-attachment array of size 2*N* is filled so that exactly half of its entries are `VK_ATTACHMENT_UNUSED`, can a fragment shader still read the *N* active input attachments through the bindings that skip the unused slots?

[`vktRenderPassUnusedAttachmentSparseFillingTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1) implements the `attachment_sparse_filling` test family. Each test case registers *N* active input attachments, builds a descriptor and subpass layout whose total attachment count is 2*N*, places *N* `VK_ATTACHMENT_UNUSED` entries between the active ones, and lets a fragment shader walk the active bindings. The shader counts how many descriptors it iterates and how many of them return a nonzero value, then stores both counters to a storage image the host reads back.

- The family appears under three rendering variants that all share this one implementation: `renderpasses.renderpass1`, `renderpasses.renderpass2`, and `renderpasses.dynamic_rendering` (with the `primary_cmd_buff`, `complete_secondary_cmd_buff`, `partial_secondary_cmd_buff`, and `graphics_pipeline_library` sub-roots).
- The behavioral axis is the active attachment count *N*, registered as the seven test case leaves `input_attachment_1`, `input_attachment_3`, `input_attachment_7`, `input_attachment_15`, `input_attachment_31`, `input_attachment_63`, and `input_attachment_127`.
- Each leaf must pass on its own; there is no aggregate pass condition.

## Background Knowledge

- **`VK_ATTACHMENT_UNUSED` as a hole, not an end marker.** In a `VkSubpassDescription` input attachment array, or in the `pColorAttachmentInputIndices` list consumed by `VkRenderingInputAttachmentIndexInfo` under dynamic rendering local read, an entry equal to `VK_ATTACHMENT_UNUSED` means "no attachment at this position," not "the array ends here." Active entries can sit at indices before and after an unused one. The [spec text](../../../../vulkan-docs/src/chapters/renderpass.adoc) states that if `pInputAttachments[i].attachment` is `VK_ATTACHMENT_UNUSED`, the application must not read from input attachment index *i*, but it does not require the unused entries to be contiguous or trailing.
- **Input attachment descriptor must be present even when the subpass slot is unused.** A `subpassLoad` in GLSL reads through a descriptor bound at a specific `InputAttachmentIndex`. The implementation under test must keep the descriptor-array layout sparse: it must not compact the active bindings together and renumber the indices, or the test would no longer exercise the "skip the holes" path.
- **Sparse filling in dynamic rendering.** Under `VK_KHR_dynamic_rendering_local_read`, there is no `pInputAttachments` array; instead, `VkRenderingInputAttachmentIndexInfo` maps color attachment indices to input attachment indices. Unused entries in `pColorAttachmentInputIndices` play the same hole role, and the attachment index can be anywhere in the `[0, 2*N* - 1]` range rather than being contiguous from zero as in the render-pass cases.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.attachment_sparse_filling
├── input_attachment_1
├── input_attachment_3
├── input_attachment_7
├── input_attachment_15
├── input_attachment_31
├── input_attachment_63
└── input_attachment_127
```

The same seven test case leaves are also registered under `renderpass2.suballocation.attachment_sparse_filling` and under each `dynamic_rendering.<cmd_buff_variant>.suballocation.attachment_sparse_filling` root. [`createRenderPassUnusedAttachmentSparseFillingTests`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1047-L1064) constructs the family once for whichever `SharedGroupParams` the caller passes, so all six rendering roots reuse the identical implementation.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Active input attachment count *N* | `1`, `3`, `7`, `15`, `31`, `63`, `127` | Doubles to a total attachment count of `2`, `6`, `14`, `30`, `62`, `126`, `254`. The values follow the form `2^k - 1` for `k` from 1 to 7, so each step roughly doubles the descriptor array and the number of holes. | [`activeInputAttachmentCount` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053) |
| Total attachment count | `2 * N` | Fixed by the test: the input attachment array always has exactly as many unused slots as active slots. | [`generateInputAttachmentParams` call sites](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) |
| Rendering variant | `renderpass1`, `renderpass2`, `dynamic_rendering` | Selects the legacy `VkRenderPass` path, the `VK_KHR_create_renderpass2` path, or the `VK_KHR_dynamic_rendering_local_read` path. All three reuse the same test logic through `SharedGroupParams`. | [`SharedGroupParams` dispatch](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L513-L522) and [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) |

The seed for hole placement is fixed at `DEFAULT_SEED = 31`, so the shuffle order is deterministic across runs for a given *N* and rendering variant.

## Behavior Parameters

The primary behavioral axis is the active input attachment count *N*. Every value exercises the same mechanism at increasing scale; the interesting question is not "does each leaf test a different property" but "does the implementation keep skipping holes correctly as the array grows toward the device limits."

### input_attachment_1, smallest sparse array

One active input attachment sits in a two-slot array alongside one `VK_ATTACHMENT_UNUSED` entry. This is the minimal case: the shader iterates one descriptor and expects its `subpassLoad` to return the cleared `(1, 1, 1, 1)` value, so `result.x` and `result.y` must both equal `1`.

### input_attachment_3 through input_attachment_127, growing the holes

Each larger leaf keeps the same ratio of half active and half unused, but stretches the descriptor array and the subpass input attachment list. The larger leaves are the ones that approach the device limits `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, and (for dynamic rendering) `maxColorAttachments`, so they are the ones most likely to expose descriptor-indexing or input-attachment-routing bugs that only appear at scale. The `input_attachment_127` leaf binds 254 attachment slots, the largest configuration the test generates.

### Why the count values are `2^k - 1`

The sequence `1, 3, 7, 15, 31, 63, 127` is chosen so each step roughly doubles the array while staying one short of a power of two. This keeps the total `2*N*` within typical device limits for as many steps as possible and produces evenly spaced coverage from the trivial case up to the practical maximum.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.suballocation.attachment_sparse_filling.input_attachment_7
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass1` | Uses the legacy render-pass path, where a 14-entry `pInputAttachments` array carries seven active references and seven `VK_ATTACHMENT_UNUSED` holes. |
| `input_attachment_7` | Generates seven input-attachment declarations and seven unrolled load/count blocks, large enough to expose the sparse binding pattern without the repetition of the largest leaves. |
| `DEFAULT_SEED = 31` | Makes the legacy render-pass hole placement deterministic; the active `InputAttachmentIndex` values are `2`, `4`, `9`, `10`, `11`, `12`, and `13`. |

#### Purpose

The fragment shader distinguishes sparse-routing failures from bad attachment data: `result.x` counts the seven active descriptors visited, while `result.y` counts only loads whose red channel remains positive. The host requires both values to equal seven at every output pixel.

#### Structural Design

| Descriptor binding | `InputAttachmentIndex` | Shader action |
|---:|---:|---|
| `1` | `2` | Increment `result.x`; load `attach1`; conditionally increment `result.y`. |
| `2` | `4` | Increment `result.x`; load `attach2`; conditionally increment `result.y`. |
| `3` | `9` | Increment `result.x`; load `attach3`; conditionally increment `result.y`. |
| `4` | `10` | Increment `result.x`; load `attach4`; conditionally increment `result.y`. |
| `5` | `11` | Increment `result.x`; load `attach5`; conditionally increment `result.y`. |
| `6` | `12` | Increment `result.x`; load `attach6`; conditionally increment `result.y`. |
| `7` | `13` | Increment `result.x`; load `attach7`; conditionally increment `result.y`. |
| `0` (storage image) | — | Store the resulting `uvec4`; host verification reads its `x` and `y` channels. |

#### Shader Code

```glsl
#version 450
/// Interpolated fullscreen-triangle coordinates; the covered 8x8 viewport maps them to output texel coordinates.
layout(location = 0) in vec4 inUV;
/// Per-pixel oracle image: x counts visited active descriptors and y counts positive input loads.
/// Host resource: 8x8 VK_FORMAT_R32G32_UINT storage image at descriptor binding 0.
layout(binding = 0, rg32ui) uniform uimage2D resultImage;
/// Seven R8G8B8A8_UNORM input images occupy descriptor bindings 1-7, while their InputAttachmentIndex values retain holes in the 14-slot subpass array.
layout(binding = 1, input_attachment_index = 2) uniform subpassInput attach1;
layout(binding = 2, input_attachment_index = 4) uniform subpassInput attach2;
layout(binding = 3, input_attachment_index = 9) uniform subpassInput attach3;
layout(binding = 4, input_attachment_index = 10) uniform subpassInput attach4;
layout(binding = 5, input_attachment_index = 11) uniform subpassInput attach5;
layout(binding = 6, input_attachment_index = 12) uniform subpassInput attach6;
layout(binding = 7, input_attachment_index = 13) uniform subpassInput attach7;
void main (void)
{
    /// Start both independent counters at zero for this fragment.
    uvec4 result = uvec4(0);
    /// Visit every active descriptor exactly once; increment y only when the routed attachment preserves its positive clear value.
    result.x = result.x + 1;
    if(subpassLoad(attach1).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach2).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach3).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach4).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach5).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach6).x > 0.0)
        result.y = result.y + 1;
    result.x = result.x + 1;
    if(subpassLoad(attach7).x > 0.0)
        result.y = result.y + 1;
    /// Publish the two counts for host verification; every output pixel must become (7, 7).
    imageStore(resultImage, ivec2(imageSize(resultImage) * inUV.xy), result);
}
```

#### Additional Info

- [`generateInputAttachmentParams`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) initializes fourteen slots with `VK_ATTACHMENT_UNUSED`, fills seven with attachment indices, and applies the seed-31 Fisher-Yates shuffle; `initPrograms` then emits one declaration for each non-unused slot.
- Before the draw, [`preRenderCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L867-L905) clears every active `R8G8B8A8_UNORM` input image to `(1, 1, 1, 1)`, making every correctly routed `subpassLoad(...).x > 0.0` comparison true.
- [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043) checks every pixel of the copied `R32G32_UINT` output and fails independently when either count differs from seven.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Active input attachment count *N* | Changes the number of generated `subpassInput` declarations and unrolled count/load blocks from 1 through 127; the sparse index list is regenerated over `2*N*` slots. | [`initPrograms`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L301-L344) and [`activeInputAttachmentCount`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1060) |
| Rendering variant | `renderpass1` and `renderpass2` derive `InputAttachmentIndex` values from the positions of active entries in the shuffled subpass array. Dynamic rendering instead shuffles indices from the full `[0, 2*N*-1]` range, marks every other one unused, shuffles again, and emits the surviving index values. | [`generateInputAttachmentParams`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) |

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
; Bound: 144
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
               OpCapability StorageImageExtendedFormats
               OpCapability ImageQuery
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %inUV
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %result "result"
               OpName %attach1 "attach1"
               OpName %attach2 "attach2"
               OpName %attach3 "attach3"
               OpName %attach4 "attach4"
               OpName %attach5 "attach5"
               OpName %attach6 "attach6"
               OpName %attach7 "attach7"
               OpName %resultImage "resultImage"
               OpName %inUV "inUV"
               OpDecorate %attach1 Binding 1
               OpDecorate %attach1 DescriptorSet 0
               OpDecorate %attach1 InputAttachmentIndex 2
               OpDecorate %attach2 Binding 2
               OpDecorate %attach2 DescriptorSet 0
               OpDecorate %attach2 InputAttachmentIndex 4
               OpDecorate %attach3 Binding 3
               OpDecorate %attach3 DescriptorSet 0
               OpDecorate %attach3 InputAttachmentIndex 9
               OpDecorate %attach4 Binding 4
               OpDecorate %attach4 DescriptorSet 0
               OpDecorate %attach4 InputAttachmentIndex 10
               OpDecorate %attach5 Binding 5
               OpDecorate %attach5 DescriptorSet 0
               OpDecorate %attach5 InputAttachmentIndex 11
               OpDecorate %attach6 Binding 6
               OpDecorate %attach6 DescriptorSet 0
               OpDecorate %attach6 InputAttachmentIndex 12
               OpDecorate %attach7 Binding 7
               OpDecorate %attach7 DescriptorSet 0
               OpDecorate %attach7 InputAttachmentIndex 13
               OpDecorate %resultImage Binding 0
               OpDecorate %resultImage DescriptorSet 0
               OpDecorate %inUV Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_0 = OpConstant %uint 0
         %11 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
         %19 = OpTypeImage %float SubpassData 0 0 0 2 Unknown
%_ptr_UniformConstant_19 = OpTypePointer UniformConstant %19
    %attach1 = OpVariable %_ptr_UniformConstant_19 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
      %v2int = OpTypeVector %int 2
         %26 = OpConstantComposite %v2int %int_0 %int_0
    %v4float = OpTypeVector %float 4
    %float_0 = OpConstant %float 0
       %bool = OpTypeBool
    %attach2 = OpVariable %_ptr_UniformConstant_19 UniformConstant
    %attach3 = OpVariable %_ptr_UniformConstant_19 UniformConstant
    %attach4 = OpVariable %_ptr_UniformConstant_19 UniformConstant
    %attach5 = OpVariable %_ptr_UniformConstant_19 UniformConstant
    %attach6 = OpVariable %_ptr_UniformConstant_19 UniformConstant
    %attach7 = OpVariable %_ptr_UniformConstant_19 UniformConstant
        %129 = OpTypeImage %uint 2D 0 0 0 2 Rg32ui
%_ptr_UniformConstant_129 = OpTypePointer UniformConstant %129
%resultImage = OpVariable %_ptr_UniformConstant_129 UniformConstant
    %v2float = OpTypeVector %float 2
%_ptr_Input_v4float = OpTypePointer Input %v4float
       %inUV = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_v4uint Function
               OpStore %result %11
         %13 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %14 = OpLoad %uint %13
         %16 = OpIAdd %uint %14 %uint_1
         %17 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %17 %16
         %22 = OpLoad %19 %attach1
         %28 = OpImageRead %v4float %22 %26
         %29 = OpCompositeExtract %float %28 0
         %32 = OpFOrdGreaterThan %bool %29 %float_0
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
         %35 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %36 = OpLoad %uint %35
         %37 = OpIAdd %uint %36 %uint_1
         %38 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %38 %37
               OpBranch %34
         %34 = OpLabel
         %39 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %40 = OpLoad %uint %39
         %41 = OpIAdd %uint %40 %uint_1
         %42 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %42 %41
         %44 = OpLoad %19 %attach2
         %45 = OpImageRead %v4float %44 %26
         %46 = OpCompositeExtract %float %45 0
         %47 = OpFOrdGreaterThan %bool %46 %float_0
               OpSelectionMerge %49 None
               OpBranchConditional %47 %48 %49
         %48 = OpLabel
         %50 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %51 = OpLoad %uint %50
         %52 = OpIAdd %uint %51 %uint_1
         %53 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %53 %52
               OpBranch %49
         %49 = OpLabel
         %54 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %55 = OpLoad %uint %54
         %56 = OpIAdd %uint %55 %uint_1
         %57 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %57 %56
         %59 = OpLoad %19 %attach3
         %60 = OpImageRead %v4float %59 %26
         %61 = OpCompositeExtract %float %60 0
         %62 = OpFOrdGreaterThan %bool %61 %float_0
               OpSelectionMerge %64 None
               OpBranchConditional %62 %63 %64
         %63 = OpLabel
         %65 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %66 = OpLoad %uint %65
         %67 = OpIAdd %uint %66 %uint_1
         %68 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %68 %67
               OpBranch %64
         %64 = OpLabel
         %69 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %70 = OpLoad %uint %69
         %71 = OpIAdd %uint %70 %uint_1
         %72 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %72 %71
         %74 = OpLoad %19 %attach4
         %75 = OpImageRead %v4float %74 %26
         %76 = OpCompositeExtract %float %75 0
         %77 = OpFOrdGreaterThan %bool %76 %float_0
               OpSelectionMerge %79 None
               OpBranchConditional %77 %78 %79
         %78 = OpLabel
         %80 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %81 = OpLoad %uint %80
         %82 = OpIAdd %uint %81 %uint_1
         %83 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %83 %82
               OpBranch %79
         %79 = OpLabel
         %84 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %85 = OpLoad %uint %84
         %86 = OpIAdd %uint %85 %uint_1
         %87 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %87 %86
         %89 = OpLoad %19 %attach5
         %90 = OpImageRead %v4float %89 %26
         %91 = OpCompositeExtract %float %90 0
         %92 = OpFOrdGreaterThan %bool %91 %float_0
               OpSelectionMerge %94 None
               OpBranchConditional %92 %93 %94
         %93 = OpLabel
         %95 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %96 = OpLoad %uint %95
         %97 = OpIAdd %uint %96 %uint_1
         %98 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %98 %97
               OpBranch %94
         %94 = OpLabel
         %99 = OpAccessChain %_ptr_Function_uint %result %uint_0
        %100 = OpLoad %uint %99
        %101 = OpIAdd %uint %100 %uint_1
        %102 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %102 %101
        %104 = OpLoad %19 %attach6
        %105 = OpImageRead %v4float %104 %26
        %106 = OpCompositeExtract %float %105 0
        %107 = OpFOrdGreaterThan %bool %106 %float_0
               OpSelectionMerge %109 None
               OpBranchConditional %107 %108 %109
        %108 = OpLabel
        %110 = OpAccessChain %_ptr_Function_uint %result %uint_1
        %111 = OpLoad %uint %110
        %112 = OpIAdd %uint %111 %uint_1
        %113 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %113 %112
               OpBranch %109
        %109 = OpLabel
        %114 = OpAccessChain %_ptr_Function_uint %result %uint_0
        %115 = OpLoad %uint %114
        %116 = OpIAdd %uint %115 %uint_1
        %117 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %117 %116
        %119 = OpLoad %19 %attach7
        %120 = OpImageRead %v4float %119 %26
        %121 = OpCompositeExtract %float %120 0
        %122 = OpFOrdGreaterThan %bool %121 %float_0
               OpSelectionMerge %124 None
               OpBranchConditional %122 %123 %124
        %123 = OpLabel
        %125 = OpAccessChain %_ptr_Function_uint %result %uint_1
        %126 = OpLoad %uint %125
        %127 = OpIAdd %uint %126 %uint_1
        %128 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %128 %127
               OpBranch %124
        %124 = OpLabel
        %132 = OpLoad %129 %resultImage
        %133 = OpLoad %129 %resultImage
        %134 = OpImageQuerySize %v2int %133
        %136 = OpConvertSToF %v2float %134
        %139 = OpLoad %v4float %inUV
        %140 = OpVectorShuffle %v2float %139 %139 0 1
        %141 = OpFMul %v2float %136 %140
        %142 = OpConvertFToS %v2int %141
        %143 = OpLoad %v4uint %result
               OpImageWrite %132 %142 %143
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Resource setup.** The constructor at [`InputAttachmentSparseFillingTestInstance`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L376-L723) creates *N* `R8G8B8A8_UNORM` input images with views, one `R32G32_UINT` output image with a view, and one host-visible output buffer sized to the render extent.
- **Descriptor layout.** Binding 0 is the output storage image; bindings 1 through *N* are the active input attachments, declared in the sparse order produced by `generateInputAttachmentParams`. The layout never contains a binding for an unused slot. [`DescriptorSetLayoutBuilder`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L558-L568)
- **Render pass or dynamic rendering setup.** For the render-pass variants, the subpass lists `2*N*` input attachment references, half of them `VK_ATTACHMENT_UNUSED`. For dynamic rendering, the same sparse pattern is delivered through `VkRenderingInputAttachmentIndexInfo`. [`createRenderPass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L923-L1004) and [`createCommandBufferDynamicRendering`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L757-L865)
- **Pre-render commands.** [`preRenderCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L867-L905) clears the output image to `(0, 0)` and every input image to `(1, 1, 1, 1)`, then transitions each input image to the layout the fragment shader will read it through: `GENERAL` for the render-pass variants, or `RENDERING_LOCAL_READ_KHR` (or `GENERAL` for the `complete_secondary_cmd_buff` sub-variant) for dynamic rendering.
- **Draw.** A single fullscreen triangle draws the fragment shader once per pixel. [`drawCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L907-L915)
- **Copyback and check.** [`postRenderCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L917-L921) copies the output image to the host-visible buffer. [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043) scans every pixel and fails with `"Wrong attachment count"` if `result.x != N` or with `"Wrong active attachment count"` if `result.y != N`.

The pass condition is exact: both channels of every pixel must equal *N*. There is no tolerance and no aggregation across leaves.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `input_attachment_1` | Minimal sparse routing: a single `VK_ATTACHMENT_UNUSED` entry next to one active input attachment breaks descriptor binding, subpass input attachment routing, or the dynamic-rendering index map. |
| `input_attachment_3` through `input_attachment_127` | Any of the minimal causes, plus scale-sensitive descriptor indexing, input attachment routing, or limit handling that only appears as the array grows toward `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, or `maxColorAttachments`. |

All leaves share the same descriptor setup, shader, and verification path, so a failure that appears at every *N* points at the shared sparse-routing machinery rather than at a count-specific path.

### Cause Analysis

#### Incorrect descriptor or subpass routing of unused slots

**Possible failure symptoms:** `result.x` differs from *N*, meaning the shader iterated the wrong number of active bindings. Depending on the bug, `result.y` may differ as well.

**Possible implementation causes:** The driver may compact the descriptor array and renumber `InputAttachmentIndex` decorations, map a `VK_ATTACHMENT_UNUSED` subpass entry to a real attachment (or vice versa), or apply the `VkRenderingInputAttachmentIndexInfo` color-to-input map incorrectly. Any of these would let the shader load from the wrong texel or skip a binding, changing the iteration count. Source-level investigation of the selected leaf is needed to tell descriptor-set construction from subpass-description handling as the fault location.

#### Active input attachment returns the wrong data

**Possible failure symptoms:** `result.x == N` but `result.y != N`. The shader saw every active binding but at least one `subpassLoad` did not return the cleared `(1, 1, 1, 1)` value.

**Possible implementation causes:** The cleared input image contents may not have reached the fragment shader through the sparse routing, the input image layout transition may have discarded or aliased the cleared data, or the implementation may have routed an active binding to an uninitialized or wrong attachment. Because the shader only checks `.x > 0`, a partial or blended value would still pass or fail depending on whether the red channel survived. The host cannot tell from `result.y` alone which binding was wrong; source-level inspection of the descriptor update and image transition for the failing leaf is needed.

#### Limit or feature handling at large *N*

**Possible failure symptoms:** Only the larger leaves (`input_attachment_63`, `input_attachment_127`) fail, or a leaf fails during pipeline creation or draw submission rather than at verification.

**Possible implementation causes:** The implementation may misreport or mis-enforce `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, or `maxColorAttachments`, or may handle the dynamic-rendering local-read path differently at high attachment counts. [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) is supposed to skip leaves that exceed the device's reported limits, so a failure here after the support check passed suggests the reported limit and the actual handling disagree. Confirming this requires checking the device's reported limits against the failing leaf's `2*N*` total.

## Case Pruning

### Requirement-based pruning

- [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) requires `VK_KHR_create_renderpass2` for the `renderpass2` variant and `VK_KHR_dynamic_rendering_local_read` for the dynamic-rendering variant.
- The same function throws `NotSupportedError` when `2*N*` exceeds `maxColorAttachments` (dynamic rendering only), `maxPerStageDescriptorInputAttachments`, or `maxPerStageResources`. On devices with low limits, the larger leaves are skipped rather than failed.
- Unsupported variants cause a skip through the CTS support check, not a failed verification.

### Design-based pruning

- The active attachment counts are fixed at `1, 3, 7, 15, 31, 63, 127`. No other counts are generated, so there is no per-leaf configuration matrix beyond the rendering variant chosen by the parent group.
- The total attachment count is always exactly `2*N*`. The test does not cover other ratios of active-to-unused entries.

## Key Takeaways

- The family tests one property at seven scales: an input attachment array that mixes active entries with `VK_ATTACHMENT_UNUSED` holes must still let the shader read every active entry through its original descriptor binding.
- The fragment shader's two independent counts turn one run into three distinguishable outcomes: wrong descriptor count, right count but wrong data, or full pass.
- All three rendering variants (legacy render pass, `renderpass2`, and dynamic rendering with local read) share one implementation, so a failure scoped to one variant points at variant-specific routing (`pInputAttachments` versus `VkRenderingInputAttachmentIndexInfo`) rather than at the shared shader or verification logic.
- The larger leaves are deliberately sized to approach the device limits, so a failure that only appears at `input_attachment_63` or `input_attachment_127` is more likely a limit or scale-sensitive routing bug than a logic error in the minimal case.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Family registration | [`createRenderPassUnusedAttachmentSparseFillingTests`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1047-L1064) | Creates `attachment_sparse_filling` and adds the seven `input_attachment_*` test case leaves. |
| Sparse layout generator | [`generateInputAttachmentParams`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) | Produces the `VK_ATTACHMENT_UNUSED` hole pattern differently for render-pass and dynamic-rendering variants; drives the shader, descriptor, and subpass setup. |
| Shader generation | [`InputAttachmentSparseFillingTest::initPrograms`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L301-L344) | Builds the fragment shader whose `result.x` / `result.y` counts are the pass condition. |
| Support and limits | [`InputAttachmentSparseFillingTest::checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) | Gates the three rendering variants and skips leaves that exceed device limits. |
| Resource and pipeline setup | [`InputAttachmentSparseFillingTestInstance` constructor](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L376-L723) | Creates input/output images, descriptor set, render pass or dynamic-rendering state, and pipeline. |
| Render-pass construction | [`createRenderPass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L923-L1004) | Builds the subpass with `2*N*` input attachment references, half unused. |
| Dynamic-rendering construction | [`createCommandBufferDynamicRendering`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L757-L865) | Records the sparse `VkRenderingInputAttachmentIndexInfo` and the three secondary-command-buffer variants. |
| Verification | [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043) | Scans every output pixel and compares both channels against *N*. |
| `VK_ATTACHMENT_UNUSED` semantics | [`renderpass.adoc` input attachment rules](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Defines what an unused entry means in `pInputAttachments`. |
| Dynamic-rendering index mapping | [`VkRenderingInputAttachmentIndexInfo` and `vkCmdSetRenderingInputAttachmentIndices`](../../../../vulkan-docs/src/chapters/interfaces.adoc) | Defines the sparse color-to-input map used by the dynamic-rendering variant. |
