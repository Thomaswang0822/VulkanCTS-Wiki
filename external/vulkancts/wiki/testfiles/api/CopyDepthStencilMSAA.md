## Overview

**Core question:** Does the implementation preserve every individual sample of a multisampled depth/stencil image when copying between two multisampled depth/stencil images of the same format and sample count, across whole-image, subregion, and per-array-layer copies, with the depth and stencil aspects exercised independently?

- Source file: [`vktApiCopyDepthStencilMSAATests.cpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp). Header: [`vktApiCopyDepthStencilMSAATests.hpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp).
- Test category: `api`. Composite family: `copy_and_blit`. Test family covered by this page: `depth_stencil_msaa_copy`, registered under three dispatcher intermediate nodes (`core`, `dedicated_allocation`, and `copy_commands2`) by [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L138). Implementation entry: [`addCopyDepthStencilMSAATests()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1275).
- Test case leaves: format-suffixed names such as `d32_sfloat_general_general_D_4_bit` (whole, with layout pair) and `d16_unorm_s8_uint_D_16_bit_bind_offset` (partial or array_to_array, with bind offset). Layout-pair leaves are emitted only for `whole`; bind-offset leaves are emitted only when allocation kind is not `ALLOCATION_KIND_DEDICATED`.
- Three copy-option subtrees are exercised: `whole` (single full-extent region, with layout variation), `partial` (two half-extent subregions with a host-side clear-value check on the uncopied area), and `array_to_array` (single region between layer 2 and layer 3 of a 5-layer image, with an in-shader empty-layer check).
- The test uses a shader-based verification path. A fullscreen-quad fragment shader reads every sample of the source and destination images through multisampled input attachments, writes per-sample `.r` values into two host-visible storage buffers, and the host compares them sample-by-sample.
- The page explains what each copy option changes about the regions, the verification logic, and the failure surface; the verification shader itself is summarized rather than walked through, per the harness scope for this page.

## Background Knowledge

- **Multisampled depth/stencil image copy.** `vkCmdCopyImage` and `vkCmdCopyImage2` copy every sample of a multisampled source to the corresponding sample of a multisampled destination when both images share the same format and sample count. There is no resolve, averaging, or sample masking: the per-sample depth or stencil value at `(x, y, s)` in the source must appear verbatim at `(x, y, s)` in the destination. This differs from `vkCmdResolveImage`, which produces a single-sample image; this test never resolves.
- **Per-aspect `VkImageCopy` regions.** A `VkImageCopy` region names one aspect through `srcSubresource.aspectMask` and `dstSubresource.aspectMask`, and the masks must match. Combined depth/stencil formats (`VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`) copy depth and stencil in separate regions; depth-only (`VK_FORMAT_D32_SFLOAT`) and stencil-only (`VK_FORMAT_S8_UINT`) formats expose a single aspect. This test never combines aspects in a single region; each leaf targets either `_D` or `_S`.
- **Multisampled input attachments and `subpassInputMS`/`usubpassInputMS`.** GLSL `subpassInputMS` (and its unsigned counterpart `usubpassInputMS`) declares a multisampled input attachment. The `subpassLoad(attachment, sampleID)` form loads the value of a specific sample at the current fragment coordinate. The verification shader uses this form to iterate `sampleID` in a loop, which avoids requiring the `sampleRateShading` feature even though the pipeline is created with `VK_SAMPLE_COUNT_1_BIT` rasterizationSamples.
- **`fragmentStoresAndAtomics`.** The verification fragment shader writes per-sample values into two SSBOs. The `fragmentStoresAndAtomics` device feature gates this path; the test is skipped when the feature is not supported. This is a verification-only dependency: the Vulkan copy command itself does not require it, but the test framework needs it because multisampled optimal-tiled depth/stencil images have no direct host-readable layout.
- **Layout transitions around transfer commands.** The Vulkan spec accepts `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL` for the source image of a transfer, and `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL` for the destination. This test exercises all four combinations but only for the `whole` copy option, to limit test count; `partial` and `array_to_array` use only the optimal layouts.

## Registration Hierarchy

```text
api.copy_and_blit.core.depth_stencil_msaa_copy
├── whole
├── partial
└── array_to_array
```

The same `depth_stencil_msaa_copy` test family with the same `whole` / `partial` / `array_to_array` subtree is also registered under `api.copy_and_blit.dedicated_allocation.depth_stencil_msaa_copy` and `api.copy_and_blit.copy_commands2.depth_stencil_msaa_copy`. The `core` path uses `ALLOCATION_KIND_SUBALLOCATED` and records `vkCmdCopyImage` (`extensionFlags = NONE`); the `dedicated_allocation` path uses `ALLOCATION_KIND_DEDICATED` and records `vkCmdCopyImage` (`extensionFlags = NONE`); the `copy_commands2` path uses `ALLOCATION_KIND_DEDICATED` and records `vkCmdCopyImage2` (`extensionFlags = COPY_COMMANDS_2`). The `dedicated_allocation` and `copy_commands2` paths share the same parameter matrix (both dedicated, so no `_bind_offset` variants); `core` differs in allocation kind and emits the additional `_bind_offset` leaves. Mustpass evidence starts at [`api.txt#L174767`](../../../mustpass/main/vk-default/api.txt#L174767) for `core.depth_stencil_msaa_copy`, [`api.txt#L253715`](../../../mustpass/main/vk-default/api.txt#L253715) for `dedicated_allocation.depth_stencil_msaa_copy`, and [`api.txt#L23616`](../../../mustpass/main/vk-default/api.txt#L23616) for `copy_commands2.depth_stencil_msaa_copy`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Copy option | `whole`, `partial`, `array_to_array` | The primary behavioral axis. Selects the region shape, the array layer count, and the verification scope. | [`vktApiCopyDepthStencilMSAATests.cpp#L1267-L1274`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1267-L1274) |
| Format | `d32_sfloat`, `s8_uint`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint` | One bare depth format, one bare stencil format, and the two mandatory combined depth/stencil formats. Selects which aspects are testable: `d32_sfloat` only generates `_D` leaves; `s8_uint` only generates `_S` leaves; the combined formats generate both. | [`vktApiCopyDepthStencilMSAATests.cpp#L1179-L1184`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1179-L1184) |
| Copy aspect | `VK_IMAGE_ASPECT_DEPTH_BIT` (`_D`), `VK_IMAGE_ASPECT_STENCIL_BIT` (`_S`) | Selects which aspect is the target of the copy and which verification shader is generated (`subpassInputMS` for depth, `usubpassInputMS` for stencil). | [`vktApiCopyDepthStencilMSAATests.cpp#L1208-L1248`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1208-L1248) |
| Sample count | 2, 4, 8, 16, 32, 64 | The number of samples per texel. The host queries `framebufferDepthSampleCounts` (and, due to a CTS-side oversight, also for stencil) and skips unsupported sample counts. | [`vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170) |
| Source image layout | `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` (`whole` only) | Layout passed to `vkCmdCopyImage` for the source. `GENERAL` exercises the implementation's transfer-read path on a layout not specialized for transfers. | [`vktApiCopyDepthStencilMSAATests.cpp#L1187`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1187) |
| Destination image layout | `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` (`whole` only) | Layout passed to `vkCmdCopyImage` for the destination. `GENERAL` exercises the implementation's transfer-write path on a layout not specialized for transfers. | [`vktApiCopyDepthStencilMSAATests.cpp#L1188`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1188) |
| Bind offset | `false` (default), `true` (`_bind_offset` suffix) | When true, the source image memory is bound at an offset equal to `VkMemoryRequirements::alignment`. Skipped for `ALLOCATION_KIND_DEDICATED` because dedicated allocations cannot have a nonzero offset. | [`vktApiCopyDepthStencilMSAATests.cpp#L1213-L1225`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1213-L1225) |
| Command extension | `NONE` (`core` parent), `COPY_COMMANDS_2` (`copy_commands2` parent) | Selects `vkCmdCopyImage` or `vkCmdCopyImage2`. Set by the dispatcher root, not the leaf. | [`vktApiCopiesAndBlittingTests.cpp#L138`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L138) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATION` (`core`), `ALLOCATION_KIND_DEDICATED` (`dedicated_allocation` and `copy_commands2` parents) | Selects how source and destination image memory is bound. The dedicated path skips the `_bind_offset` variant. | [`vktApiCopiesAndBlittingTests.cpp#L232-L246`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L246), [`vktApiCopiesAndBlittingTests.cpp#L274-L277`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L274-L277) |

## Behavior Parameters

The primary behavioral axis is the **copy option**, encoded as the `whole` / `partial` / `array_to_array` intermediate node directly below the `depth_stencil_msaa_copy` test family. Each value changes the region shape, the array layer count, and the verification scope. The `copyAspect` dimension (depth vs. stencil, encoded as the `_D` / `_S` leaf suffix) is a parameter dimension rather than a behavioral axis: it changes which aspect is the target of the copy and which verification shader is generated, but the region structure and failure mechanisms stay the same.

### `whole`: full-image copy with layout variation

Copies a single full-extent `VkImageCopy` region with `srcOffset = dstOffset = (0, 0, 0)` and `extent = defaultExtent`. The source and destination images are single-layer. This is the only copy option that varies the source and destination layouts across the four combinations of `TRANSFER_OPTIMAL` and `GENERAL`, generating the `<format>_<srcLayout>_<dstLayout>_D_<samples>` and `<format>_<srcLayout>_<dstLayout>_S_<samples>` leaves. Verification compares per-sample values across the entire destination image. Source: [`vktApiCopyDepthStencilMSAATests.cpp#L178-L189`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L178-L189), [`vktApiCopyDepthStencilMSAATests.cpp#L1186-L1189`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1186-L1189).

### `partial`: two subregion copies with an uncopied-area check

Copies two half-extent regions into the bottom half of the destination: one from the bottom-right of the source to the bottom-left of the destination, and one from the top-right of the source to the bottom-right of the destination. The image is single-layer. Only the optimal layouts are tested, so leaves use the shorter `<format>_D_<samples>` and `<format>_S_<samples>` naming. Verification compares per-sample values across the copied regions and checks that the upper half of the destination image (every `(x, y, s)` with `y < extent.height / 2`) still holds the clear value `0.0f`. Source: [`vktApiCopyDepthStencilMSAATests.cpp#L151-L177`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L151-L177), [`vktApiCopyDepthStencilMSAATests.cpp#L979-L997`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979-L997).

### `array_to_array`: per-layer copy on a 5-layer image

Copies a single full-extent region from `srcBaseArrayLayer = 2` to `dstBaseArrayLayer = 3` of a 5-layer image. The constructor sets `m_srcImage.extent.depth = 5u` and the framebuffer view targets layer 2 for rendering. Only the optimal layouts are tested. The verification shader also checks that every non-target layer (layers 0, 1, 2, and 4 of the destination) holds the clear value, and forces a mismatch by decrementing `outputCopied[bufferPos]` if any non-target layer is nonzero. Source: [`vktApiCopyDepthStencilMSAATests.cpp#L134-L141`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L134-L141), [`vktApiCopyDepthStencilMSAATests.cpp#L1113-L1128`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1113-L1128).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.api.copy_and_blit.core.depth_stencil_msaa_copy.whole.d16_unorm_s8_uint_general_general_D_4_bit
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `whole` | Selects one full-extent, single-layer copy region and the one-destination-layer verification shader shape. |
| `d16_unorm_s8_uint` + `_D` | Selects the combined depth/stencil format while verifying only its depth aspect, so the generated shader uses floating-point `subpassInputMS` and stores `.r` values. |
| `general_general_D_4_bit` | Uses `VK_IMAGE_LAYOUT_GENERAL` for both transfer source and destination, and explicitly iterates four samples in the verification fragment shader. |

#### Purpose

The verification fragment shader makes the multisampled copy observable: for every framebuffer pixel and sample, it reads the source and copied depth values and writes their red components to host-visible SSBOs. The host then compares the two streams at matching `(x, y, sample)` indices, so a resolve-like, first-sample-only, or otherwise incorrect copy is exposed.

#### Structural Design

| Shader phase | Shader operation | Validation signal |
|--------------|------------------|-------------------|
| Inputs | Read `width`, `height`, and `samples` from push constants; bind source attachment 0 and copied destination attachment 1. | The shader has the same dimensions and sample count as the host verification pass. |
| Per-sample traversal | Loop `sampleID` from `0` through `samples - 1`; combine integer `gl_FragCoord` and `sampleID` into `bufferPos`. | Every sample is checked even though the verification pipeline rasterizes with `VK_SAMPLE_COUNT_1_BIT`. |
| Two-stream capture | `subpassLoad(attachment0, sampleID).r` goes to `outputOriginal`; attachment 1 goes to `outputCopied`. | The host can compare source and destination values without direct host reads from optimal-tiled depth/stencil images. |

#### Shader Code

```glsl
#version 450

// The shader copies the sample values from the source and destination image to output buffers OriginalValue and
// CopiedValues, respectively. If the dst image contains multiple array layers, only one layer has the copied data
// and the rest should be filled with the clear value (0). This is also verified in this shader.
// Array layer cases need an image view per layer in the copied image.
// Set 0 contains the output buffers.
// Set 1 contains the input attachments.

layout (push_constant, std430) uniform PushConstants {
    /// Host-pushed framebuffer dimensions and the selected sample count drive indexing and the per-sample loop.
    int width;
    int height;
    int samples;
};
layout (set=0, binding=0) buffer OriginalValues {
    /// SSBO binding 0 receives the source attachment's red component for every framebuffer sample.
    float outputOriginal[];
};
layout (set=0, binding=1) buffer CopiedValues {
    /// SSBO binding 1 receives the destination attachment's corresponding sample for host comparison.
    float outputCopied[];
};
/// Input attachment 0 is the source image; whole uses one destination layer at attachment 1.
layout (input_attachment_index=0, set=1, binding=0) uniform subpassInputMS attachment0;
layout (input_attachment_index=1, set=1, binding=1) uniform subpassInputMS attachment1;

void main() {
    // Using a loop to iterate over each sample avoids the need for the sampleRateShading feature. The pipeline needs to be
    // created with a single sample.
    /// The fullscreen draw invokes this fragment shader at every pixel; this loop explicitly visits each sample.
    for (int sampleID = 0; sampleID < samples; ++sampleID) {
        /// Integer framebuffer coordinates plus sampleID form the flat SSBO index: ((y * width + x) * samples + s).
        ivec3 coords  = ivec3(int(gl_FragCoord.x), int(gl_FragCoord.y), sampleID);
        int bufferPos = (coords.y * width + coords.x) * samples + coords.z;
        vec4 orig = subpassLoad(attachment0, sampleID);
        outputOriginal[bufferPos] = orig.r;
        vec4 copy1 = subpassLoad(attachment1, sampleID);

        /// The host later compares this copied stream with outputOriginal sample by sample.
        outputCopied[bufferPos] = copy1.r; 
    }
}
```

#### Additional Info

- `createVerificationShader()` is the exact generator for this fragment stage: the `attachmentAspect == VK_IMAGE_ASPECT_DEPTH_BIT` branch leaves `inputAttachmentPrefix` empty, producing `subpassInputMS` and floating-point `.r` values for this `_D` case. [`vktApiCopyDepthStencilMSAATests.cpp#L1055-L1105`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1055-L1105)
- The host binds two storage buffers at set 0, bindings 0 and 1, one source input attachment plus one destination-layer attachment, pushes `fbWidth`, `fbHeight`, and `m_params.samples`, and draws a fullscreen quad with `VK_SAMPLE_COUNT_1_BIT`; the host-side loop then compares the two buffers sample by sample. [`vktApiCopyDepthStencilMSAATests.cpp#L661-L725`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L725), [`vktApiCopyDepthStencilMSAATests.cpp#L821-L942`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L821-L942), [`vktApiCopyDepthStencilMSAATests.cpp#L944-L977`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L944-L977)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Copy option | `whole` emits one destination-layer attachment and verifies `copy1`; `array_to_array` emits five destination attachments, selects `copy4`, and adds an empty-layer check; `partial` keeps the one-layer shader shape while the host checks the untouched upper half. | [`vktApiCopyDepthStencilMSAATests.cpp#L1050-L1053`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1050-L1053), [`vktApiCopyDepthStencilMSAATests.cpp#L1108-L1128`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1108-L1128) |
| Copy aspect | Depth uses `subpassInputMS` and floating-point zero comparisons; stencil uses `usubpassInputMS` and integer zero comparisons, while both write the `.r` component into float SSBOs. | [`vktApiCopyDepthStencilMSAATests.cpp#L1065-L1089`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1065-L1089), [`vktApiCopyDepthStencilMSAATests.cpp#L1113-L1127`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1113-L1127) |
| Sample count | The generated GLSL keeps the runtime `samples` push constant and the same loop; the selected 2/4/8/16/32/64 case changes the loop trip count and host buffer indexing, not the declarations. | [`vktApiCopyDepthStencilMSAATests.cpp#L721-L725`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L721-L725), [`vktApiCopyDepthStencilMSAATests.cpp#L1091-L1099`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1091-L1099), [`vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170) |

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
; Bound: 96
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %sampleID "sampleID"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "width"
               OpMemberName %PushConstants 1 "height"
               OpMemberName %PushConstants 2 "samples"
               OpName %_ ""
               OpName %coords "coords"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %bufferPos "bufferPos"
               OpName %orig "orig"
               OpName %attachment0 "attachment0"
               OpName %OriginalValues "OriginalValues"
               OpMemberName %OriginalValues 0 "outputOriginal"
               OpName %__0 ""
               OpName %copy1 "copy1"
               OpName %attachment1 "attachment1"
               OpName %CopiedValues "CopiedValues"
               OpMemberName %CopiedValues 0 "outputCopied"
               OpName %__1 ""
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpMemberDecorate %PushConstants 1 Offset 4
               OpMemberDecorate %PushConstants 2 Offset 8
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %attachment0 Binding 0
               OpDecorate %attachment0 DescriptorSet 1
               OpDecorate %attachment0 InputAttachmentIndex 0
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %OriginalValues BufferBlock
               OpMemberDecorate %OriginalValues 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %attachment1 Binding 1
               OpDecorate %attachment1 DescriptorSet 1
               OpDecorate %attachment1 InputAttachmentIndex 1
               OpDecorate %_runtimearr_float_0 ArrayStride 4
               OpDecorate %CopiedValues BufferBlock
               OpMemberDecorate %CopiedValues 0 Offset 0
               OpDecorate %__1 Binding 1
               OpDecorate %__1 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
%PushConstants = OpTypeStruct %int %int %int
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
          %_ = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_2 = OpConstant %int 2
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
       %bool = OpTypeBool
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %62 = OpTypeImage %float SubpassData 0 0 1 2 Unknown
%_ptr_UniformConstant_62 = OpTypePointer UniformConstant %62
%attachment0 = OpVariable %_ptr_UniformConstant_62 UniformConstant
      %v2int = OpTypeVector %int 2
         %68 = OpConstantComposite %v2int %int_0 %int_0
%_runtimearr_float = OpTypeRuntimeArray %float
%OriginalValues = OpTypeStruct %_runtimearr_float
%_ptr_Uniform_OriginalValues = OpTypePointer Uniform %OriginalValues
        %__0 = OpVariable %_ptr_Uniform_OriginalValues Uniform
%_ptr_Function_float = OpTypePointer Function %float
%_ptr_Uniform_float = OpTypePointer Uniform %float
%attachment1 = OpVariable %_ptr_UniformConstant_62 UniformConstant
%_runtimearr_float_0 = OpTypeRuntimeArray %float
%CopiedValues = OpTypeStruct %_runtimearr_float_0
%_ptr_Uniform_CopiedValues = OpTypePointer Uniform %CopiedValues
        %__1 = OpVariable %_ptr_Uniform_CopiedValues Uniform
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
   %sampleID = OpVariable %_ptr_Function_int Function
     %coords = OpVariable %_ptr_Function_v3int Function
  %bufferPos = OpVariable %_ptr_Function_int Function
       %orig = OpVariable %_ptr_Function_v4float Function
      %copy1 = OpVariable %_ptr_Function_v4float Function
               OpStore %sampleID %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %sampleID
         %21 = OpAccessChain %_ptr_PushConstant_int %_ %int_2
         %22 = OpLoad %int %21
         %24 = OpSLessThan %bool %15 %22
               OpBranchConditional %24 %11 %12
         %11 = OpLabel
         %35 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %36 = OpLoad %float %35
         %37 = OpConvertFToS %int %36
         %39 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %40 = OpLoad %float %39
         %41 = OpConvertFToS %int %40
         %42 = OpLoad %int %sampleID
         %43 = OpCompositeConstruct %v3int %37 %41 %42
               OpStore %coords %43
         %45 = OpAccessChain %_ptr_Function_int %coords %uint_1
         %46 = OpLoad %int %45
         %47 = OpAccessChain %_ptr_PushConstant_int %_ %int_0
         %48 = OpLoad %int %47
         %49 = OpIMul %int %46 %48
         %50 = OpAccessChain %_ptr_Function_int %coords %uint_0
         %51 = OpLoad %int %50
         %52 = OpIAdd %int %49 %51
         %53 = OpAccessChain %_ptr_PushConstant_int %_ %int_2
         %54 = OpLoad %int %53
         %55 = OpIMul %int %52 %54
         %57 = OpAccessChain %_ptr_Function_int %coords %uint_2
         %58 = OpLoad %int %57
         %59 = OpIAdd %int %55 %58
               OpStore %bufferPos %59
         %65 = OpLoad %62 %attachment0
         %66 = OpLoad %int %sampleID
         %69 = OpImageRead %v4float %65 %68 Sample %66
               OpStore %orig %69
         %74 = OpLoad %int %bufferPos
         %76 = OpAccessChain %_ptr_Function_float %orig %uint_0
         %77 = OpLoad %float %76
         %79 = OpAccessChain %_ptr_Uniform_float %__0 %int_0 %74
               OpStore %79 %77
         %82 = OpLoad %62 %attachment1
         %83 = OpLoad %int %sampleID
         %84 = OpImageRead %v4float %82 %68 Sample %83
               OpStore %copy1 %84
         %89 = OpLoad %int %bufferPos
         %90 = OpAccessChain %_ptr_Function_float %copy1 %uint_0
         %91 = OpLoad %float %90
         %92 = OpAccessChain %_ptr_Uniform_float %__1 %int_0 %89
               OpStore %92 %91
               OpBranch %13
         %13 = OpLabel
         %93 = OpLoad %int %sampleID
         %95 = OpIAdd %int %93 %int_1
               OpStore %sampleID %95
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates two multisampled `VK_IMAGE_TYPE_2D` images of the same format, sample count, and extent (`defaultExtent` for `whole`/`partial`; `defaultExtent` width and height with `extent.depth = 5` for `array_to_array`). Both images carry `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_OPTIMAL | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT`. See [`vktApiCopyDepthStencilMSAATests.cpp#L242-L277`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L242-L277).
- When `imageOffset` is true, the source image is bound with `bindImageMemory` at `srcImageAlloc->getOffset() + req.alignment`; otherwise it is bound at the allocator's natural offset. See [`vktApiCopyDepthStencilMSAATests.cpp#L264-L270`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L264-L270).
- The host clears both images to known values: source to depth `0.1f` and stencil `0x10`, destination to depth `0.0f` and stencil `0`. See [`vktApiCopyDepthStencilMSAATests.cpp#L487-L525`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L487-L525).
- The host transitions the source image to `VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL` and renders a single triangle (upper-right half) into it with `depthTestEnable = VK_TRUE`, `depthWriteEnable = VK_TRUE`, `depthCompareOp = VK_COMPARE_OP_ALWAYS`, and `stencilOpState.passOp = VK_STENCIL_OP_REPLACE`. The render pass uses `m_params.samples` rasterizationSamples. See [`vktApiCopyDepthStencilMSAATests.cpp#L414-L555`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L414-L555).
- The host transitions the source to `m_srcImage.operationLayout` and the destination to `m_dstImage.operationLayout`, then records one of two copy commands: `vkCmdCopyImage` for `extensionFlags == NONE` or `vkCmdCopyImage2` for `extensionFlags == COPY_COMMANDS_2`. The regions are built from `m_regions` in the constructor. See [`vktApiCopyDepthStencilMSAATests.cpp#L564-L641`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564-L641).
- For each used aspect (depth and/or stencil, in that order), the host runs the verification pass: builds a render pass with `numInputAttachments = layerCount + 1` attachments (one source plus one per destination layer), binds two SSBOs and the input attachment descriptors, pushes `width`, `height`, and `samples` as push constants, and draws a fullscreen quad. See [`vktApiCopyDepthStencilMSAATests.cpp#L661-L942`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L942).
- The host invalidates the SSBO allocations and reads both buffers back. It walks every `(x, y, s)` in every copied region and compares `outputOriginal[srcIndex]` against `outputCopied[dstIndex]`. The first mismatch fails the case, logging the coordinate, sample, expected, and actual values. See [`vktApiCopyDepthStencilMSAATests.cpp#L944-L977`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L944-L977).
- For `partial` only, the host also walks the upper half of the destination image and verifies `outputCopied[bufferIndex] == m_clearValue` (`0.0f`). This guarantees the copy did not touch any texel outside the requested regions. See [`vktApiCopyDepthStencilMSAATests.cpp#L979-L997`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979-L997).
- For `array_to_array`, the in-shader `equalEmptyLayers` check already enforces that the four non-target layers are zero; if a non-target layer is nonzero, the shader decrements `outputCopied[bufferPos]`, which surfaces as a mismatch on the target layer during the host-side walk. The host does not re-walk the non-target layers.
- The case passes only if all per-sample comparisons succeed (and, for `partial`, the upper-half clear-value check also succeeds) for every used aspect. There is no tolerance.

## Failure Meaning

A failure of this test family means the implementation did not preserve the per-sample depth or stencil value at one or more copied texels during `vkCmdCopyImage` or `vkCmdCopyImage2`, or that it wrote outside the requested regions or array layers. The verification path is shared infrastructure; failures caused by the verification shader, the SSBO write path, or host-side index arithmetic would surface uniformly across many leaves and are not specific to a copy option.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `whole` | Per-sample depth/stencil value not preserved by `vkCmdCopyImage`/`vkCmdCopyImage2` for a full-extent, single-region, same-format, same-sample-count copy. Includes incorrect layout handling when the `GENERAL` layout variants fail but the optimal-layout variants pass. |
| `partial` | Same per-sample preservation failure as `whole`, or the implementation writes outside the requested regions (the upper-half clear-value check fails). |
| `array_to_array` | Per-sample preservation failure on the target layer, or the implementation writes to non-target array layers (the in-shader `equalEmptyLayers` check fails and surfaces as a forced mismatch). |

A shared infrastructure cause affects all three values: incorrect source-image rendering that produces unknown sample values, incorrect verification-shader `subpassLoad`/SSBO-write behavior, or incorrect host-side index arithmetic. These would produce failures across multiple cases uniformly.

### Cause Analysis

#### Per-sample value not preserved

**Possible failure symptoms:** A `whole` (or `partial`, or `array_to_array`) case fails the host-side per-sample comparison at one or more `(x, y, s)` coordinates. The logged `result` and `expected` values differ. The mismatch may appear at all samples of a texel, at a subset of samples, or only at specific coordinates (such as texels at the edge of the rendered triangle).

**Possible implementation causes:** The Vulkan spec requires the implementation to copy every sample of a multisampled depth/stencil source to the corresponding sample of the destination when format and sample count match. A driver that confuses a copy with a resolve (writing only one sample or an averaged value), that copies only the first sample, that drops samples at coverage boundaries, or that mishandles the per-sample memory layout of optimal-tiled multisampled depth/stencil images would produce this symptom. If the symptom is reproducible only for specific formats or sample counts, investigate the driver's multisampled copy path at the spec level.

#### Layout handling for `GENERAL`

**Possible failure symptoms:** A `whole` case with `general` in its leaf name (for example `d32_sfloat_general_general_D_4_bit`) fails, while the corresponding `optimal_optimal` case passes. The mismatch is in the per-sample comparison, not in the clear-value check.

**Possible implementation causes:** The Vulkan spec accepts `VK_IMAGE_LAYOUT_GENERAL` for both source and destination of transfer commands, but the implementation may take a different code path than for `TRANSFER_SRC_OPTIMAL` or `TRANSFER_DST_OPTIMAL`. A driver that handles the optimal transfer layouts correctly but mishandles `GENERAL` for transfer reads or writes would produce this symptom. This cause applies only to `whole` because `partial` and `array_to_array` do not vary the layout.

#### Out-of-region writes for `partial`

**Possible failure symptoms:** A `partial` case fails the upper-half clear-value check: the host detects `outputCopied[bufferIndex] != 0.0f` at one or more `(x, y, s)` with `y < extent.height / 2`. The per-sample equality check on the copied regions may also fail or may pass.

**Possible implementation causes:** The two `VkImageCopy` regions in the `partial` case both target the bottom half of the destination image. The Vulkan spec requires the implementation to honor `dstOffset` and `extent` and leave every other texel untouched. A driver that ignores the destination offset, that writes a full image instead of the requested subregion, or that miscomputes the destination pitch would write into the upper half and produce this symptom. A symptom isolated to specific sample counts or region shapes suggests a driver bug in region handling; examine the source.

#### Out-of-layer writes for `array_to_array`

**Possible failure symptoms:** An `array_to_array` case fails the per-sample comparison on the target layer (layer 3) at coordinates where the in-shader `equalEmptyLayers` check fired. The logged `result` value is one less than the expected source value, because the verification shader decremented `outputCopied[bufferPos]` to signal that a non-target layer was nonzero.

**Possible implementation causes:** The `VkImageCopy` region in the `array_to_array` case names `dstSubresource.baseArrayLayer = 3` and `layerCount = 1`. The Vulkan spec requires the implementation to write only that layer. A driver that copies into multiple layers, that ignores `baseArrayLayer`, or that miscomputes the layer stride would write into layers 0, 1, 2, or 4 and trigger the in-shader empty-layer check. When the failure appears only for specific formats or layer counts, look at the driver's array-layer copy handling in source.

## Case Pruning

### Requirement-based pruning

- `fragmentStoresAndAtomics` must be supported; otherwise the case throws `NotSupportedError` and is skipped. See [`vktApiCopyDepthStencilMSAATests.cpp#L1026-L1028`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1026-L1028).
- For depth aspects, the requested sample count must be reported by `framebufferDepthSampleCounts`; otherwise the case is skipped. See [`vktApiCopyDepthStencilMSAATests.cpp#L1029-L1031`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1029-L1031).
- For stencil aspects, the requested sample count is checked against `framebufferDepthSampleCounts` rather than the spec-separate `framebufferStencilSampleCounts`. This appears to be a CTS-side oversight: the Vulkan spec exposes `framebufferStencilSampleCounts` separately. In practice many implementations report the same sample count support for depth and stencil attachments, so the gate is usually equivalent. This is a CTS implementation detail, not a Vulkan implementation issue, and does not change the failure analysis. See [`vktApiCopyDepthStencilMSAATests.cpp#L1033-L1035`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1033-L1035).
- The image format must support `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_OPTIMAL | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` with optimal tiling; otherwise `vkGetPhysicalDeviceImageFormatProperties` returns `VK_ERROR_FORMAT_NOT_SUPPORTED` and the case is skipped. See [`vktApiCopyDepthStencilMSAATests.cpp#L1037-L1046`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1037-L1046).
- The `copy_commands2` path requires `VK_KHR_copy_commands2` and is gated by `checkExtensionSupport()`. See [`vktApiCopyDepthStencilMSAATests.cpp#L1022`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1022).

### Design-based pruning

- Layout variation (`TRANSFER_OPTIMAL` vs. `GENERAL`) is emitted only for the `whole` copy option, to limit test count. The `partial` and `array_to_array` options emit only the optimal-layout leaves. See [`vktApiCopyDepthStencilMSAATests.cpp#L1186-L1255`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1186-L1255).
- The `_bind_offset` variant is emitted only when `allocationKind != ALLOCATION_KIND_DEDICATED`, because dedicated allocations cannot have a nonzero memory offset. See [`vktApiCopyDepthStencilMSAATests.cpp#L1219-L1225`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1219-L1225).
- The format matrix is intentionally small: one bare depth format, one bare stencil format, and the two mandatory combined depth/stencil formats. Other depth/stencil formats are covered by the broader `copy_and_blit` family.
- The `array_to_array` option uses a fixed 5-layer image with source layer 2 and destination layer 3; other layer configurations are not exercised.

## Key Takeaways

- The tested property is per-sample preservation: every sample at `(x, y, s)` in the source must appear verbatim at `(x, y, s)` in the destination for every copied texel. A driver that confuses a copy with a resolve, or that only copies one sample, fails this test.
- The three copy options are not interchangeable: `whole` covers full-image copies with layout variation, `partial` adds an out-of-region write check on the destination's upper half, and `array_to_array` adds an in-shader empty-layer check on the four non-target layers of a 5-layer image. Each surfaces a different class of bug.
- Layout variation is exclusive to `whole`; a failure that appears only on `general_*` or `*_general` leaves points to a `VK_IMAGE_LAYOUT_GENERAL` transfer-path issue, not a per-sample copy issue.
- The `_bind_offset` variant exercises non-zero `vkBindImageMemory` offsets; a failure specific to this variant points to a memory-binding alignment issue rather than a copy-command issue.
- The `dedicated_allocation` and `copy_commands2` registrations share one source implementation and the same dedicated-allocation parameter matrix; a failure on one path but not the other at the same parameter combination points to a `vkCmdCopyImage` vs. `vkCmdCopyImage2` divergence rather than a generic copy bug. The `core` registration uses suballocated memory and adds `_bind_offset` leaves, so it is not a direct matrix match for `copy_commands2`.
- The `framebufferDepthSampleCounts` check applied to stencil aspects is a CTS-side observation, not a Vulkan implementation issue; see `## Failure Meaning` for the failure analysis and `## Case Pruning` for the gate details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `DepthStencilMSAA` class declaration and `TestParameters` struct | [`vktApiCopyDepthStencilMSAATests.cpp#L35-L82`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L35-L82) | Defines the test instance, the `CopyOptions` enum, and the parameter struct that drives region construction. |
| Constructor: region construction | [`vktApiCopyDepthStencilMSAATests.cpp#L84-L200`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L84-L200) | Builds `VkImageCopy` regions for `whole`, `partial`, and `array_to_array`. |
| Render phase: image creation, render pass, pipeline, draw | [`vktApiCopyDepthStencilMSAATests.cpp#L226-L558`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L226-L558) | Creates the multisampled source image, draws the initializing triangle, and clears both images. |
| Copy phase: layout transition and `vkCmdCopyImage`/`vkCmdCopyImage2` | [`vktApiCopyDepthStencilMSAATests.cpp#L564-L641`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564-L641) | Records the copy command under test. |
| `checkCopyResults()`: verify phase | [`vktApiCopyDepthStencilMSAATests.cpp#L661-L1001`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L1001) | Builds the verification render pass, SSBOs, descriptor sets, fullscreen-quad pipeline, and host-side per-sample comparison. |
| Host-side partial-copy clear-value check | [`vktApiCopyDepthStencilMSAATests.cpp#L979-L997`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979-L997) | Verifies the upper half of the destination image remains at the clear value for `COPY_PARTIAL`. |
| `DepthStencilMSAATestCase` class | [`vktApiCopyDepthStencilMSAATests.cpp#L1003-L1135`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1003-L1135) | Holds `checkSupport()` and `initPrograms()`. |
| `checkSupport()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1020-L1047`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1020-L1047) | Feature and format support gates. |
| `createVerificationShader()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132) | Emits the depth/stencil verification GLSL with `subpassInputMS`/`usubpassInputMS` and the `equalEmptyLayers` check. |
| `initPrograms()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1137-L1167`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1137-L1167) | Registers the triangle vertex/fragment shaders and the verification shader for each used aspect. |
| Sample count list | [`vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170) | The 2/4/8/16/32/64 sample count matrix. |
| `addDepthStencilCopyMSAATest()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1172-L1256`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1172-L1256) | Generates the format x aspect x sample x layout x bind-offset leaf matrix for one copy option. |
| `addCopyDepthStencilMSAATests()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1260-L1275`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1275) | Registers `whole`, `partial`, and `array_to_array` intermediate nodes under the parent test group. |
| Header declaration | [`vktApiCopyDepthStencilMSAATests.hpp#L34`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp#L34) | Public entry `addCopyDepthStencilMSAATests(group, allocationKind, extensionFlags)`. |
| Parent registration | [`vktApiCopiesAndBlittingTests.cpp#L138`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L138) | Routes `depth_stencil_msaa_copy` to `addCopyDepthStencilMSAATests()` under both `core` and `copy_commands2` parents. |
| Mustpass evidence (core path) | [`api.txt#L174767`](../../../mustpass/main/vk-default/api.txt#L174767) | Concrete `dEQP-VK.api.copy_and_blit.core.depth_stencil_msaa_copy.*` entries. |
| Mustpass evidence (copy_commands2 path) | [`api.txt#L23616`](../../../mustpass/main/vk-default/api.txt#L23616) | Concrete `dEQP-VK.api.copy_and_blit.copy_commands2.depth_stencil_msaa_copy.*` entries. |
