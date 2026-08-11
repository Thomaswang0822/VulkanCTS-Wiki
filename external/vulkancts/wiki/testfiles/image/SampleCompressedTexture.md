## Overview

**Core question:** Can a BC1 or BC3 image accept compressed blocks through a size-compatible unsigned-integer storage view and later decode those blocks correctly through a compressed sampled view?

- [`vktImageSampleCompressedTextureTests.cpp`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L20-L30) implements the `image.sample_texture` test family.
- Each test case creates an 80 x 80 BC1 or BC3 image, writes literal compressed blocks in a compute shader, then samples the same image in a full-screen draw.
- The page covers the compatible-view mapping, the ordinary and `two_samplers` execution paths, cubemap handling, and the host result checks.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Block-texel view compatibility.** A block-compressed format stores one encoded block for several decoded texels. When compatible formats have different block extents, Vulkan scales the view extent by the block-extents ratio. `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` permits size-compatible views with that scaled extent ([format size compatibility](../../../../vulkan-docs/src/chapters/formats.adoc#L1998-L2033)).
- **View format controls interpretation.** The storage view exposes each BC block as unsigned integer components. The compressed sampled view interprets the same bytes as BC1 or BC3 data and returns decoded color. A sample through the integer view therefore is not a decoded-color sample.

## Registration Hierarchy

```text
image.sample_texture
├── 128_bit_compressed_format_cubemap
├── 64_bit_compressed_format_cubemap
├── 64_bit_compressed_format_two_samplers_cubemap
├── 128_bit_compressed_format_two_samplers_cubemap
├── 64_bit_compressed_format
├── 64_bit_compressed_format_two_samplers
├── 128_bit_compressed_format
└── 128_bit_compressed_format_two_samplers
```

[`createImageSampleDrawnTextureTests()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L845-L915) registers all eight test case leaves. The `image` test category adds this test family through [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Compressed block class | `64_bit_compressed_format`, `128_bit_compressed_format` | Selects BC1 with a two-component unsigned-integer view, or BC3 with a four-component unsigned-integer view. | [Registration](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L890-L912) |
| Sampler configuration | ordinary, `two_samplers` | Ordinary leaves render after each of two compute writes. `two_samplers` leaves first render the raw integer-view sample, then overwrite it with the compressed-view sample. | [Pass description](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L847-L872) |
| Image topology | ordinary 2D, `cubemap` | Cubemap leaves allocate six array layers and bind separate 2D views for each face. | [View setup](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L313-L346), [per-face commands](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L556-L609) |
| Decoded extent | fixed 80 x 80 | Sets the backing image and color-target dimensions. The compute dispatch instead uses the compressed block-grid extent. | [Constants and dispatch extent](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L76-L79), [#L286-L301](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L286-L301) |

## Behavior Parameters

The primary behavior parameter is the compressed block class. The remaining dimensions exercise the same compatible-view mechanism with different sampling and layer arrangements.

### 64_bit_compressed_format - BC1 blocks

These leaves use `VK_FORMAT_BC1_RGB_UNORM_BLOCK` as the backing image and `VK_FORMAT_R32G32_UINT` as the compatible view. One integer-view texel represents one 64-bit BC1 block, whose decoded footprint is 4 x 4 texels. The compute shader writes known BC1 block values, and the compressed sampled view must decode the blue block in the final draw.

### 128_bit_compressed_format - BC3 blocks

These leaves use `VK_FORMAT_BC3_UNORM_BLOCK` and `VK_FORMAT_R32G32B32A32_UINT`. The larger integer format carries one 128-bit BC3 block. Apart from the format pair and literal block values, the case follows the same write, sample, and compare sequence as the BC1 path.

## Shader Analysis

The representative case is the ordinary BC1 2D leaf. Its compute shader contains the test's data producer: each invocation stores one literal BC block through the compatible storage-image view. The vertex shader only passes full-screen-quad positions and UVs, while the fragment shader samples the compressed view.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.sample_texture.64_bit_compressed_format
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `64_bit_compressed_format` | Selects BC1 backing storage and the `R32G32_UINT` compatible storage view. |
| ordinary sampler configuration | The compute shader writes red for pass 0 and blue for pass 1; both draws use the compressed sampled view. |
| ordinary 2D topology | Uses one storage view and one compressed sampled view rather than six per-face views. |

#### Purpose

The compute shader writes a known BC1 block stream through an integer storage view. The graphics pipeline then tests whether a compressed-format view of the same image decodes that stream as the expected color.

#### Structural Design

| Shader element | Role in the representative case |
|---|---|
| `img` | `rgba32ui` storage image at set 0, binding 0. It addresses the BC1 block grid through the compatible `R32G32_UINT` view. |
| `pc.pass` | Selects the source-generated red BC1 literal for pass 0 or blue literal for pass 1. |
| `gl_GlobalInvocationID.xy` | Selects one compatible-view texel, and therefore one compressed block. |
| `imageStore` | Writes the chosen four unsigned components to the compatible storage view. |

#### Shader Code

```glsl
#version 450

/// The compatible `R32G32_UINT` view is bound as an `rgba32ui` storage image.
layout(set = 0, binding = 0, rgba32ui) uniform highp uimage2D img;
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// The host sets pass 0 for red blocks and pass 1 for blue blocks.
layout(push_constant) uniform constants {
    int pass;
} pc;

void main() {
    /// Literal BC1 data for a decoded red block.
    uvec4 color = uvec4(4160813056u, 0u, 4160813056u, 0u);
    if (pc.pass == 1)
        /// Literal BC1 data for a decoded blue block.
        color = uvec4(2031647u, 0u, 2031647u, 0u);

    /// One invocation writes one compressed block through the compatible view.
    imageStore(img, ivec2(gl_GlobalInvocationID.xy), color);
}
```

#### Additional Info

- [`initPrograms()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L755-L836) emits this shader shape. The two-sampler branch removes the compute push constant and writes the blue literal on its only compute pass.
- The fragment shader always binds `compTexSampler` at binding 0. In ordinary leaves it writes `texture(compTexSampler, fragTexCoord)` directly; in `two_samplers` leaves pass 0 instead samples binding 1, the raw integer view.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Compressed block class | BC3 replaces the BC1 red and blue block literals. The storage declaration remains `rgba32ui`; the compatible view has four 32-bit components. | [Generated literals](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L757-L764) |
| Sampler configuration | `two_samplers` removes `pc` from the compute shader, writes blue once, and makes the fragment shader select raw or compressed sampling by its own push constant. | [Generator branches](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L773-L789), [#L813-L831](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L813-L831) |
| Image topology | Cubemap leaves reuse the same generated shader text; the host changes the bound 2D view and descriptor set for each face. | [Cubemap descriptor and command loops](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L319-L334), [#L556-L609](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L556-L609) |

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
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %color "color"
               OpName %constants "constants"
               OpMemberName %constants 0 "pass"
               OpName %pc "pc"
               OpName %img "img"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpDecorate %constants Block
               OpMemberDecorate %constants 0 Offset 0
               OpDecorate %img Binding 0
               OpDecorate %img DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%uint_4160813056 = OpConstant %uint 4160813056
     %uint_0 = OpConstant %uint 0
         %12 = OpConstantComposite %v4uint %uint_4160813056 %uint_0 %uint_4160813056 %uint_0
        %int = OpTypeInt 32 1
  %constants = OpTypeStruct %int
%_ptr_PushConstant_constants = OpTypePointer PushConstant %constants
         %pc = OpVariable %_ptr_PushConstant_constants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
      %int_1 = OpConstant %int 1
       %bool = OpTypeBool
%uint_2031647 = OpConstant %uint 2031647
         %27 = OpConstantComposite %v4uint %uint_2031647 %uint_0 %uint_2031647 %uint_0
         %28 = OpTypeImage %uint 2D 0 0 0 2 Rgba32ui
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
        %img = OpVariable %_ptr_UniformConstant_28 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %color = OpVariable %_ptr_Function_v4uint Function
               OpStore %color %12
         %19 = OpAccessChain %_ptr_PushConstant_int %pc %int_0
         %20 = OpLoad %int %19
         %23 = OpIEqual %bool %20 %int_1
               OpSelectionMerge %25 None
               OpBranchConditional %23 %24 %25
         %24 = OpLabel
               OpStore %color %27
               OpBranch %25
         %25 = OpLabel
         %31 = OpLoad %28 %img
         %36 = OpLoad %v3uint %gl_GlobalInvocationID
         %37 = OpVectorShuffle %v2uint %36 %36 0 1
         %39 = OpBitcast %v2int %37
         %40 = OpLoad %v4uint %color
               OpImageWrite %31 %39 %40
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates the BC1 or BC3 backing image with `MUTABLE_FORMAT`, `EXTENDED_USAGE`, and `BLOCK_TEXEL_VIEW_COMPATIBLE` flags. It creates an uncompressed compatible storage view for compute and a compressed sampled view for the graphics pipeline ([image creation](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L86-L120), [view setup](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L303-L453)).
- The compressed sampled view chains `VkImageViewUsageCreateInfo` with `TRANSFER_SRC | SAMPLED`. That drops `STORAGE`, which the backing image has but the compressed sampled format does not need in this view ([view usage setup](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L369-L376)).
- For ordinary leaves, pass 0 writes red blocks, synchronizes compute writes to fragment reads, and draws red. A fragment-to-compute barrier then permits pass 1 to write blue blocks and draw blue. `two_samplers` leaves write blue in pass 0, render the raw integer-view sample, then overwrite it with the compressed-view sample in pass 1 ([command sequence](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L544-L639)).
- Cubemap leaves repeat the compute dispatch and draw with a separate 2D view and descriptor set for each of six array layers. The target image is shared, so the host keeps only its final contents rather than a readback for each face.
- The host copies the target to a host-visible buffer and invalidates the allocation. Ordinary leaves compare every pixel with opaque blue using `tcu::floatThresholdCompare` and an RGBA threshold of `0.01`. Cubemap leaves require zero red plus positive blue and alpha bytes in every final-target pixel ([result checks](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L641-L688)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `64_bit_compressed_format` | BC1 block-texel compatible view creation, BC1 storage write, compressed-view sampling/decoding, synchronization, or RGBA8 result comparison is incorrect. |
| `128_bit_compressed_format` | Equivalent failure in the 128-bit BC3 path, including the `R32G32B32A32_UINT` compatible view. |

The `two_samplers` and `cubemap` suffixes are execution variations on these two behavior values. They can narrow the investigation to raw-view coverage or per-face resource binding, but they do not define a third compressed-block class.

### Cause Analysis

#### Compatible-view mapping or storage-image write

**Possible failure symptoms:** The final ordinary result differs from opaque blue. A BC1-only failure points to the 64-bit mapping or its literal block data; a BC3-only failure points to the 128-bit mapping or its literal block data. The cubemap check can instead report nonzero red or zero blue or alpha bytes.

**Possible implementation causes:** The format pair may be rejected or interpreted with the wrong scaled extent, a storage-image write may address the wrong block-grid coordinate, or the integer components may not reach the backing image as the intended compressed block. The Vulkan compatible-view rule requires a block-texel-compatible image and a view sized for the differing block extents ([format rule](../../../../vulkan-docs/src/chapters/formats.adoc#L2009-L2033)).

#### Compressed sampled-view decode or descriptor binding

**Possible failure symptoms:** A raw integer-view first draw may differ from blue by design, but the final compressed-view draw must be blue. A `two_samplers` failure after its second draw therefore implicates the final compressed-view path rather than treating the first draw as an expected-color assertion.

**Possible implementation causes:** The graphics descriptor may bind the wrong view format, the compressed view may use an incompatible usage set, or sampling may fail to decode the block representation written through the compatible view. The source restricts the compressed sampled view to transfer-source and sampled usage because it removes the incompatible storage usage ([view setup](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L369-L453)).

#### Synchronization, per-face binding, or readback comparison

**Possible failure symptoms:** A failure can appear as stale red output, missing blue output, or a mismatch only in cubemap leaves. The ordinary comparison logs the pixel mismatch; cubemap leaves log the shared target image but do not preserve one result per face.

**Possible implementation causes:** The compute-to-fragment or fragment-to-compute barriers may not make the required writes visible, a cubemap loop may bind an incorrect face view or descriptor set, or the target copy and host-visible readback may not contain the final draw. The source records separate synchronization barriers and per-face loops before the final copy ([barriers and draws](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L544-L646)).

## Case Pruning

### Requirement-based pruning

`checkSupport()` requires `VK_KHR_maintenance2` and asks for the selected BC image format with transfer, sampled, and storage usages plus mutable-format, extended-usage, and block-texel-view-compatible flags. Cubemap leaves add `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` to that query. If the device does not support the requested configuration, CTS reports the test case as not supported rather than failed ([support check](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L719-L753)).

### Design-based pruning

The registration intentionally contains only BC1 and BC3, one fixed 80 x 80 decoded extent, nearest filtering, one mip level, and 2D or six-layer cubemap arrangements. It does not form a general compressed-format matrix for BC2, BC4 through BC7, ETC/EAC, ASTC, sRGB formats, mip chains, or cube-view sampling.

## Key Takeaways

- The test distinguishes a compatible integer storage view, which exposes encoded blocks, from the compressed sampled view, which decodes them.
- BC1 and BC3 are the primary behavior values. Their compatible views map one texel to one 64-bit or 128-bit compressed block.
- The final verdict concerns the compressed-view sample. In `two_samplers` leaves, the earlier raw integer-view draw is deliberate coverage and is overwritten.
- Cubemap leaves exercise all six faces through separate 2D views, while one reused color target supplies the host verdict.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test purpose and image creation | [`vktImageSampleCompressedTextureTests.cpp#L20-L30`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L20-L30), [`makeImageCreateInfo()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L86-L120) | Defines the stated purpose, fixed dimensions, usages, and image-create flags. |
| Resource setup and execution | [`SampleDrawnTextureTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L259-L689) | Creates views and descriptors, records barriers and passes, copies results, and performs the verdict. |
| Support requirements | [`SampleDrawnTextureTest::checkSupport()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L719-L753) | Defines maintenance2 and image-format support gating. |
| Generated GLSL | [`SampleDrawnTextureTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L755-L836) | Generates the compute, vertex, and fragment shaders. |
| Registered test case leaves | [`createImageSampleDrawnTextureTests()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L845-L915) | Registers the eight exact leaf identifiers and documents their pass behavior. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) | Adds `sample_texture` to the `image` test category. |
| Compatible-view semantics | [Vulkan format size compatibility](../../../../vulkan-docs/src/chapters/formats.adoc#L1998-L2033) | Defines size-compatible formats and block-texel-compatible image views. |
