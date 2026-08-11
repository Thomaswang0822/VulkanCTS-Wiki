## Overview

**Core question:** Can a depth or stencil aspect remain in its selected depth/stencil layout and still be read correctly through the descriptor forms that layout permits?

- This page covers the `image.depth_stencil_descriptor` test family implemented by [`vktImageDepthStencilDescriptorTests.cpp`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp).
- Each case creates one 8×8 depth/stencil image and selects a legal layout and per-aspect access pattern. Descriptor-bearing cases expose depth or stencil through an aspect-only sampled-image or input-attachment descriptor; attachment-only leaves exercise read-only attachment access without creating a descriptor-read output.
- Generated shaders copy every descriptor read into an `R32_SFLOAT` depth or `R32_UINT` stencil storage image. Graphics cases produce a color result; cases whose parameters require depth/stencil attachment access also exercise the corresponding attachment state.
- The family varies layout, compatible format, legal access combination, and eligible graphics or compute execution. This page explains those dimensions, the descriptor-read oracle, and the additional attachment checks.

## Background Knowledge

For the shared concepts image views, subresources, and layouts, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Aspect-only descriptor views.** A depth/stencil image can contain depth, stencil, or both. A descriptor view of such an image selects one aspect: Vulkan requires a descriptor image view created from a depth/stencil image to include either depth or stencil, but not both ([descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3667-L3671)). This lets the test observe the selected aspect independently.
- **Descriptor image layout.** `VkDescriptorImageInfo::imageLayout` states the layout in which subresources reachable through the image view will be when the descriptor is accessed ([descriptor image information](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3618-L3629)). The selected layout therefore defines both the image transition and the descriptor declaration used by a case.
- **Input attachments.** A fragment shader reads an input attachment at its framebuffer position with `subpassLoad()`. The render pass selects the accessible attachment aspect, while the descriptor supplies the image view and layout. The test uses this form only in graphics cases; a compute pipeline has neither a render pass nor input attachments.

## Registration Hierarchy

```text
image.depth_stencil_descriptor
├── depth_read_only_stencil_attachment_optimal
├── depth_attachment_stencil_read_only_optimal
├── depth_read_only_optimal
└── stencil_read_only_optimal
```

[`createImageDepthStencilDescriptorTests()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1589-L1759) registers the four layout values. Each direct child contains compatible format intermediate nodes and generated executable leaves. The default Vulkan mustpass file contains representative paths under all four values ([mustpass coverage](../../../mustpass/main/vk-default/image/depth-stencil-descriptor.txt#L1-L42)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Layout | `depth_read_only_stencil_attachment_optimal`, `depth_attachment_stencil_read_only_optimal`, `depth_read_only_optimal`, `stencil_read_only_optimal` | Selects the legal per-aspect access and the layout recorded in every input descriptor. | [Layout list and access mapping](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L148-L164), [registration](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1598-L1604) |
| Format intermediate node | `d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`, `s8_uint`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Chooses a depth-only, stencil-only, or combined image. Registration retains it only if its actual aspects match the selected layout's legal accesses. | [Format list and filtering](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1593-L1596), [#L1640-L1652](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1640-L1652) |
| Read-only descriptor uses | `att`, `ia`, `sampled`, `att_sampled`, `ia_sampled` | Chooses attachment read, input-attachment descriptor, sampled-image descriptor, or a legal combination for an aspect. `att` creates no descriptor-read output; `ia` and `sampled` do. | [Access labels](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L126-L145), [descriptor derivation](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L292-L325) |
| Other aspect access | `none`, `rw`, or one of the read-only uses | Represents the aspect the selected layout omits, keeps as an attachment, or exposes read-only. | [Legal-access rules](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L148-L164) |
| Execution suffix | graphics leaves; `_compute` where registered | Compute runs only sampled-image cases. Graphics runs cases that need a render pass for input attachments or depth/stencil attachment tests. | [Eligibility](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L374-L395), [compute registration](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1654-L1662) |

## Behavior Parameters

The primary behavioral axis is **layout**. Each value changes which aspect can be descriptor-read and whether the other aspect remains a depth/stencil attachment that can participate in graphics testing.

### `depth_read_only_stencil_attachment_optimal`: read depth while stencil remains an attachment

This value permits read-only depth access and read/write stencil attachment access. In descriptor-bearing cases, combined formats expose depth through input-attachment or sampled-image descriptors, while graphics cases use stencil state to exercise the other aspect. The factory excludes formats that do not contain both required aspects.

### `depth_attachment_stencil_read_only_optimal`: read stencil while depth remains an attachment

This is the converse layout. In descriptor-bearing cases, the descriptor view selects stencil, with unsigned shader types and an `R32_UINT` output image; the graphics pipeline can exercise depth attachment behavior. Only combined depth/stencil formats survive registration.

### `depth_read_only_optimal`: descriptor-read a depth-only aspect

This layout supplies read-only depth and no legal stencil access. It registers the depth-only formats `d16_unorm`, `x8_d24_unorm_pack32`, and `d32_sfloat`. Read-only depth can be an attachment, input attachment, sampled image, or a legal combination. A sampled-only leaf also receives a `_compute` variant.

### `stencil_read_only_optimal`: descriptor-read a stencil-only aspect

This layout supplies read-only stencil and no legal depth access, so it retains only `s8_uint`. The generated shader uses unsigned texture, input-attachment, and storage-image forms for stencil values. Sampled-only leaves can also run on the compute queue.

## Shader Analysis

The generator emits graphics programs for graphics cases and a compute program for `_compute` leaves ([shader generator](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L522-L647)). The representative path uses the smallest descriptor-only route:

```text
dEQP-VK.image.depth_stencil_descriptor.depth_read_only_optimal.d32_sfloat.depth_sampled_stencil_none_compute
```

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.depth_stencil_descriptor.depth_read_only_optimal.d32_sfloat.depth_sampled_stencil_none_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `depth_read_only_optimal` | The descriptor accesses a read-only depth aspect. |
| `d32_sfloat` | The image contains depth only, so the descriptor view and copied output use floating-point depth values. |
| `depth_sampled_stencil_none` | A sampled-image descriptor reads depth; stencil is absent. |
| `_compute` | A local-size-one compute shader visits every texel and does not require a render pass. |

#### Purpose

The shader samples the depth-only view at the current invocation's texel center and stores that result in a float storage image. The host later compares each stored value with the depth clear value, `0.5`.

#### Structural Design

| Shader object | Binding and type | Action |
|---------------|------------------|--------|
| `sampledImage0` | Set 0, binding 0, `texture2D` | Exposes the depth-only image view without a sampler. |
| `globalSampler` | Set 2, binding 0, `sampler` | Supplies nearest filtering and unnormalized coordinates for the depth sample. |
| `storage0` | Set 1, binding 0, `r32f image2D` | Receives the sampled depth value at the matching integer coordinate. |
| `gl_GlobalInvocationID` | Compute built-in | Selects one of the 8×8 image texels. |

#### Shader Code

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// This block is emitted for compatibility with the shared graphics/compute pipeline layout.
/// The representative compute shader does not read its fields.
layout(push_constant, std430) uniform PushConstantBlock {
    float colorR;
    float colorG;
    float colorB;
    float colorA;
    float depth;
} pc;

/// Set 2 supplies separate float and unsigned samplers. This depth case uses globalSampler.
layout (set=2, binding=0) uniform sampler globalSampler;
layout (set=2, binding=1) uniform sampler uglobalSampler;

/// The host binds a depth-only view of the D32 image at set 0, binding 0.
layout (set=0, binding=0) uniform texture2D sampledImage0;

/// This R32 float image records the shader-visible depth value for host comparison.
layout (r32f, set=1, binding=0) uniform image2D storage0;

void main () {
    /// Unnormalized coordinates address the center of the texel owned by this invocation.
    imageStore(storage0, ivec2(gl_GlobalInvocationID.xy),
               texture(sampler2D(sampledImage0, globalSampler),
                       vec2(gl_GlobalInvocationID.xy) + vec2(0.5)));
}
```

#### Additional Info

- The source emits the push-constant block in compute programs only to keep the shared pipeline-layout structure compatible; this representative shader does not consume it ([compute generator](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L585-L604)).
- The runtime creates `globalSampler` with nearest filtering and unnormalized coordinates, matching the integer-grid-plus-`0.5` sampling expression ([sampler setup](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L814-L843)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Selected aspect | Stencil descriptors prepend `u` to the texture, sampler, and storage-image declarations, and use `r32ui` instead of `r32f`. | [Descriptor declaration generation](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L536-L570) |
| Descriptor kind | Input-attachment cases replace `texture()` with `subpassLoad()` and declare `subpassInput` or `usubpassInput`. | [Input-attachment branch](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L542-L550) |
| Execution mode | Graphics moves the load to a fragment shader, indexes with `gl_FragCoord.xy`, and uses a fullscreen vertex shader. | [Graphics generator](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L606-L646) |

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
; Bound: 47
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %storage0 "storage0"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %sampledImage0 "sampledImage0"
               OpName %globalSampler "globalSampler"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "colorR"
               OpMemberName %PushConstantBlock 1 "colorG"
               OpMemberName %PushConstantBlock 2 "colorB"
               OpMemberName %PushConstantBlock 3 "colorA"
               OpMemberName %PushConstantBlock 4 "depth"
               OpName %pc "pc"
               OpName %uglobalSampler "uglobalSampler"
               OpDecorate %storage0 Binding 0
               OpDecorate %storage0 DescriptorSet 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %sampledImage0 Binding 0
               OpDecorate %sampledImage0 DescriptorSet 0
               OpDecorate %globalSampler Binding 0
               OpDecorate %globalSampler DescriptorSet 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpMemberDecorate %PushConstantBlock 2 Offset 8
               OpMemberDecorate %PushConstantBlock 3 Offset 12
               OpMemberDecorate %PushConstantBlock 4 Offset 16
               OpDecorate %uglobalSampler Binding 1
               OpDecorate %uglobalSampler DescriptorSet 2
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
          %7 = OpTypeImage %float 2D 0 0 0 2 R32f
%_ptr_UniformConstant_7 = OpTypePointer UniformConstant %7
   %storage0 = OpVariable %_ptr_UniformConstant_7 UniformConstant
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
         %21 = OpTypeImage %float 2D 0 0 0 1 Unknown
%_ptr_UniformConstant_21 = OpTypePointer UniformConstant %21
%sampledImage0 = OpVariable %_ptr_UniformConstant_21 UniformConstant
         %25 = OpTypeSampler
%_ptr_UniformConstant_25 = OpTypePointer UniformConstant %25
%globalSampler = OpVariable %_ptr_UniformConstant_25 UniformConstant
         %29 = OpTypeSampledImage %21
    %v2float = OpTypeVector %float 2
  %float_0_5 = OpConstant %float 0.5
         %36 = OpConstantComposite %v2float %float_0_5 %float_0_5
    %v4float = OpTypeVector %float 4
    %float_0 = OpConstant %float 0
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
%PushConstantBlock = OpTypeStruct %float %float %float %float %float
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%uglobalSampler = OpVariable %_ptr_UniformConstant_25 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
         %10 = OpLoad %7 %storage0
         %16 = OpLoad %v3uint %gl_GlobalInvocationID
         %17 = OpVectorShuffle %v2uint %16 %16 0 1
         %20 = OpBitcast %v2int %17
         %24 = OpLoad %21 %sampledImage0
         %28 = OpLoad %25 %globalSampler
         %30 = OpSampledImage %29 %24 %28
         %31 = OpLoad %v3uint %gl_GlobalInvocationID
         %32 = OpVectorShuffle %v2uint %31 %31 0 1
         %34 = OpConvertUToF %v2float %32
         %37 = OpFAdd %v2float %34 %36
         %40 = OpImageSampleExplicitLod %v4float %30 %37 Lod %float_0
               OpImageWrite %10 %20 %40
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance creates one depth/stencil image with transfer usage plus the usage required by the selected access pattern. It creates a full aspect view for the framebuffer and separate depth-only and stencil-only views for descriptors ([resource setup](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L742-L811)).
- It builds an input descriptor set with zero or more `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` or `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` entries, an output set containing one storage image per descriptor read, and a separate set containing float and unsigned samplers. Each populated input `VkDescriptorImageInfo` records the selected layout ([descriptor setup](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L845-L958)).
- It clears depth to `0.5` and stencil to `100`. Graphics clears with `vkCmdClearDepthStencilImage`; compute uploads the independently prepared depth and stencil values with aspect-specific `vkCmdCopyBufferToImage` calls ([clear path](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1232-L1326)).
- A transfer-to-selected-layout barrier makes the image available to all graphics accesses or to compute shader reads. The compute path dispatches 8×8 local-size-one invocations. The graphics path renders a fullscreen triangle, using a second draw when depth/stencil attachment testing is required ([transition and execution](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1328-L1403)).
- The test barriers and copies the color attachment, the depth/stencil aspects, and every descriptor output image into host-visible buffers. Graphics must produce green. Depth compares against `0.5` if read-only or `0.0` after a depth write; stencil compares against `100` if read-only or `10` after a stencil write. Descriptor outputs must preserve the original clear value for their selected aspect ([readback and checks](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1405-L1584)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `depth_read_only_stencil_attachment_optimal` | Incorrect depth descriptor access while stencil acts as an attachment, aspect-view selection, layout transition, or descriptor/attachment coexistence. |
| `depth_attachment_stencil_read_only_optimal` | Incorrect stencil descriptor access while depth acts as an attachment, aspect-view selection, layout transition, or descriptor/attachment coexistence. |
| `depth_read_only_optimal` | Incorrect descriptor access to a depth-only format/aspect in the depth-read-only layout, sampled/input descriptor setup, or compute sampled path. |
| `stencil_read_only_optimal` | Incorrect descriptor access to a stencil-only format/aspect in the stencil-read-only layout, sampled/input descriptor setup, or compute sampled path. |

### Cause Analysis

#### Aspect view, descriptor layout, and descriptor load

**Possible failure symptoms:** A storage-image readback differs from `0.5` for a depth descriptor or `100` for a stencil descriptor. In graphics cases, color can still be green because the attachment path passed while the descriptor-copy oracle failed.

**Possible implementation causes:** The descriptor view selects a single depth or stencil aspect, and the descriptor reports the selected image layout. A failure can arise from incorrect aspect selection, descriptor image-view/layout handling, sampled-image or input-attachment loading, or the visibility transition from the clear to the shader read. The final comparison shows the affected descriptor output but does not identify which of those operations produced the wrong value.

#### Attachment access paired with a read-only descriptor aspect

**Possible failure symptoms:** A mixed-aspect layout produces red rather than green, or the depth/stencil aspect readback differs from the expected read-only clear value or expected attachment-written value.

**Possible implementation causes:** The graphics pipeline enables depth or stencil testing only when the selected parameters require an attachment. Its first draw intentionally fails the active test; a later draw must pass. A defect can therefore involve the selected layout's attachment access, depth comparison/write handling, stencil reference or replacement handling, or synchronization before aspect copyback. This oracle does not by itself distinguish attachment-state failure from a bad layout transition.

#### Compute sampled-image path

**Possible failure symptoms:** `_compute` leaves fail while equivalent graphics sampled-image leaves pass, with descriptor output readbacks differing from the clear value.

**Possible implementation causes:** Compute leaves exclude input-attachment and depth/stencil attachment uses. They clear each present aspect by buffer-to-image copy and require the format's depth or stencil copy-on-compute-queue feature. A failure isolated to these leaves can involve the compute-queue aspect copy, transfer-to-shader-read barrier, compute sampling, or storage-image write/readback rather than graphics attachment execution.

## Case Pruning

### Requirement-based pruning

- Graphics leaves require `VK_KHR_create_renderpass2`. Compute leaves require `VK_KHR_maintenance10` and `VK_KHR_format_feature_flags2`; for each present aspect, they also require the corresponding `DEPTH_COPY_ON_COMPUTE_QUEUE` or `STENCIL_COPY_ON_COMPUTE_QUEUE` optimal-tiling feature ([support checks](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L457-L515)).
- The two mixed read-only/attachment layouts require `VK_KHR_maintenance2`. `depth_read_only_optimal` and `stencil_read_only_optimal` require `VK_KHR_separate_depth_stencil_layouts` ([layout extension selection](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L79-L102)).
- Every case queries image-format support with its accumulated image usages and skips when the implementation cannot support the selected format, optimal tiling, and usage combination ([format gate](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L473-L486)).

### Design-based pruning

- Registration removes format/layout pairs when an actual format's depth/stencil components do not match the layout's legal aspect accesses. It therefore does not create a depth-only case under a layout that requires a stencil attachment, or a stencil-only case under a layout that requires read-only depth ([format filtering](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1640-L1652)).
- The source excludes combinations in which one aspect is a depth/stencil attachment and the other is an input attachment. Its stated reason is that an input attachment can access only one aspect of a two-aspect depth/stencil image in that arrangement ([compatibility check](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L175-L196)).
- `_compute` is generated only for sampled-image-only configurations: compute does not use input attachments or render-pass depth/stencil tests ([compute eligibility](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L374-L395)).

## Key Takeaways

- The selected layout is the behavior-defining parameter: it controls which aspect stays read-only for descriptors and which aspect, if any, remains usable as a depth/stencil attachment.
- The test uses aspect-only views and typed storage outputs to make descriptor reads independently observable: float for depth and unsigned integer for stencil.
- Descriptor-bearing graphics cases pair descriptor observation with a second oracle for attachment behavior when attachment access is selected; attachment-only leaves use only the attachment oracle. Compute leaves isolate sampled-image descriptor reads and compute-queue depth/stencil initialization.
- A pass requires both the expected attachment result where applicable and the original clear value in every descriptor-read output.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Layout and access helpers | [`layoutExtension()` and `getLegalAccess()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L79-L164) | Maps every tested layout to its required extension and legal depth/stencil access. |
| Parameter helpers | [`TestParams` resource and eligibility helpers](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L270-L395) | Derives image usage, descriptors, attachment requirements, and compute eligibility. |
| Support and shader generation | [`DepthStencilDescriptorCase`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L457-L647) | Checks prerequisites and generates the graphics or compute shaders. |
| Runtime and result checking | [`DepthStencilDescriptorInstance::iterate()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L667-L1585) | Creates resources, performs transitions and execution, then checks attachments and descriptor outputs. |
| Registration matrix | [`createImageDepthStencilDescriptorTests()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1589-L1759) | Registers layouts, formats, access combinations, exclusions, and compute variants. |
| Descriptor image semantics | [Descriptor image information](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3604-L3692) | Defines descriptor view/layout semantics and the aspect-only depth/stencil view rule. |
| Input attachment aspect semantics | [Input attachment aspect references](../../../../vulkan-docs/src/chapters/renderpass.adoc#L3053-L3104) | Defines how a render pass identifies the aspect readable through an input attachment. |
| Default mustpass paths | [`depth-stencil-descriptor.txt`](../../../mustpass/main/vk-default/image/depth-stencil-descriptor.txt#L1-L42) | Shows the default Vulkan executable coverage under the registered hierarchy. |
| Default SPIR-V target | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Supplies SPIR-V 1.0 for generated GLSL without explicit build options. |
