## Overview

**Core question:** Can a mutable image use a compatible view format to supply a selected image usage that the parent image format does not support when `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` is set?

- [`vktImageTranscodingSupportTests.cpp`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp) implements the `image.extended_usage_bit` test family.
- Each registered case selects a featured format that supports one tested usage, then looks for a compatible featureless format that lacks that usage. Both source and destination images are mutable. On the side that needs the selected usage, the parent image additionally has the extended-usage flag and its featured-format view chains `VkImageViewUsageCreateInfo`.
- The four direct test families cover input-attachment and color-attachment directions, then sampled-image and storage-image directions. Each uses a fullscreen graphics draw and checks that the destination bytes match the generated source bytes.
- This page explains the capability selection, the complementary image/view arrangements, the generated fragment shaders, the copyback oracle, and the cases the generator omits.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Extended image usage.** `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` permits an image to have a usage flag that its creation format does not support when at least one format usable by an image view supports that flag. Without the flag, the creation format itself must support every usage bit.
- **View-specific usage.** A `VkImageViewUsageCreateInfo` chained to `VkImageViewCreateInfo` overrides the usage inherited from image creation for image-view validation. Its usage may restrict the view relative to the parent image. In this test, the extended-side view explicitly receives the same tested-usage set used to create its parent image, including both transfer bits.

## Registration Hierarchy

```text
image.extended_usage_bit
├── attachment_read
├── attachment_write
├── texture_read
└── texture_write
```

[`createImageTranscodingSupportTests()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1180-L1261) registers the direct test families and their per-format test case leaves. The default Vulkan mustpass inventory contains leaves below all four families, including `dEQP-VK.image.extended_usage_bit.texture_write.r8g8b8a8_unorm`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test family | `attachment_read`, `attachment_write`, `texture_read`, `texture_write` | Selects the tested usage, its paired usage, the image that receives extended usage, and the fragment-shader access form. | [`createImageTranscodingSupportTests()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1180-L1261) |
| Featured format | Admitted formats from 8-bit, 16-bit, 24-bit, 32-bit, 48-bit, 64-bit, 96-bit, 128-bit, 192-bit, and 256-bit compatible-format lists | Supplies the view format, shader type, attachment format, and selected usage capability. | [Compatible-format lists and factory loop](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1173-L1253) |
| Featureless format | First compatible, framework-supported, uncompressed format that lacks the selected usage but supports the remaining image usages | Becomes the parent-image format on the extended-usage side. Its lack of the selected usage makes the case exercise the flag. | [`ImageTranscodingCase::createInstance()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1103-L1169) |
| Tested and paired usage | Input attachment/color attachment or sampled/storage, each with transfer source and transfer destination | Creates the complementary source and destination arrangements for the selected direct family. | [Usage arrays and parameter construction](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1188-L1250) |
| Image shape | `IMAGE_TYPE_2D`, `UVec3(16u, 16u, 1u)`, one mip level, one layer, optimal tiling | Fixes addressing and resource shape so the matrix varies formats and usage arrangements rather than geometry. | [Factory](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1241-L1250), [image construction](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L661-L689) |

## Behavior Parameters

The primary behavioral axis is the direct **test family**. The featured and featureless formats choose a test case leaf inside each mechanism.

### `attachment_read` - Read through an extended-usage input-attachment view

The source image uses the featureless format and includes `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. Its featured-format view chains `VkImageViewUsageCreateInfo` with the input-attachment and transfer usages. The destination uses the featured format and a normal color-attachment view. The fragment shader calls `subpassLoad()` on the source input attachment and writes the result to the destination attachment.

### `attachment_write` - Write through an extended-usage color-attachment view

This is the complementary attachment arrangement. The source uses the featured format through a normal input-attachment view. The featureless destination image has `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`, and its featured-format view has color-attachment and transfer usages. The same attachment shader copies the input attachment to the fragment output.

### `texture_read` - Read through an extended-usage sampled-image view

The source image has the featureless format and extended usage. Its featured-format view carries sampled and transfer usages. The destination uses the featured format through a normal storage-image view. The fragment shader samples the source and stores the returned value into the destination storage image. This family requires `fragmentStoresAndAtomics`.

### `texture_write` - Write through an extended-usage storage-image view

The source uses the featured format through a normal sampled-image view. The featureless destination image has extended usage, and its featured-format view carries storage and transfer usages. The fragment shader samples the source and stores it through that extended-usage storage-image view. This family also requires `fragmentStoresAndAtomics`.

## Shader Analysis

The source generates a fullscreen vertex shader and one fragment shader per direct-family class. The attachment shader reads an input attachment with `subpassLoad()` and writes `o_color`. The texture shader samples a combined image sampler and writes a storage image. The walkthrough uses the exact default-Vulkan path `texture_write.r8g8b8a8_unorm`; the source derives the `sampler2D`, `image2D`, and `rgba8` declarations from that featured format.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.extended_usage_bit.texture_write.r8g8b8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `texture_write` | The featureless destination image receives `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`; its featured-format view uses storage-image usage. |
| `r8g8b8a8_unorm` | The featured view format produces a floating `sampler2D`, a floating `image2D`, and the `rgba8` storage-image qualifier. |
| 16 by 16 2D image | Gives each fullscreen fragment one source sample and one integer destination texel coordinate. |

#### Purpose

This shader reads each featured-format source texel through a sampled-image view and writes it to a featured-format storage-image view whose featureless parent image relies on extended usage. The host verifies that the storage write preserves the source byte pattern after copyback.

#### Structural Design

| Phase | Fragment-shader behavior | Role in the test |
|-------|--------------------------|------------------|
| Source access | Samples `u_imageIn` at a coordinate derived from `gl_FragCoord.xy`. | Exercises sampled-image access through the source view. |
| Destination addressing | Converts `gl_FragCoord.xy` to `ivec2 out_pos`. | Selects the destination texel for this fragment. |
| Destination access | Calls `imageStore(u_imageOut, out_pos, ...)`. | Exercises storage-image access through the extended-usage destination view. |

#### Shader Code

```glsl
#version 450

/// The source image is sampled through a view with sampled usage.
layout (binding = 0) uniform sampler2D u_imageIn;
/// The destination view uses the featured format and storage-image usage.
layout (binding = 1, rgba8) writeonly uniform image2D u_imageOut;

void main (void)
{
    /// Each fragment writes the corresponding destination texel.
    const ivec2 out_pos = ivec2(gl_FragCoord.xy);
    const vec2 pixels_resolution = vec2(textureSize(u_imageIn, 0));
    const vec2 in_pos = vec2(gl_FragCoord.xy) / vec2(pixels_resolution);
    imageStore(u_imageOut, out_pos, texture(u_imageIn, in_pos));
}
```

#### Additional Info

- [`ImageTranscodingCase::initPrograms()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1038-L1063) selects the sampler type, storage-image type, and format qualifier from `featuredFormat`; the shown declarations are the `R8G8B8A8_UNORM` specialization.
- [`GraphicsTextureTestInstance::transcode()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L778-L867) creates the featureless destination image with extended usage for `texture_write`, then creates its featured-format view with `VkImageViewUsageCreateInfo`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Direct test family | Attachment families replace the sampler and storage image with an input attachment and fragment output. `texture_read` keeps the texture shader but moves extended usage to the source image view. | [Fragment generation](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1008-L1066), [image/view selection](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L485-L515), [texture selection](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L778-L808) |
| Featured format | Changes the generated sampler type, storage-image type, and format qualifier while leaving the sampling and `imageStore()` structure intact. | [Texture shader generation](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1043-L1063) |
| Image type | The factory registers only `IMAGE_TYPE_2D`; the array-image branch in shader generation is not used by this test factory. | [Image-type adjustment](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L987-L993), [factory parameters](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1241-L1250) |

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
; Bound: 42
; Schema: 0
               OpCapability Shader
               OpCapability ImageQuery
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %out_pos "out_pos"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %pixels_resolution "pixels_resolution"
               OpName %u_imageIn "u_imageIn"
               OpName %in_pos "in_pos"
               OpName %u_imageOut "u_imageOut"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %u_imageIn Binding 0
               OpDecorate %u_imageIn DescriptorSet 0
               OpDecorate %u_imageOut NonReadable
               OpDecorate %u_imageOut Binding 1
               OpDecorate %u_imageOut DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
         %20 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %21 = OpTypeSampledImage %20
%_ptr_UniformConstant_21 = OpTypePointer UniformConstant %21
  %u_imageIn = OpVariable %_ptr_UniformConstant_21 UniformConstant
      %int_0 = OpConstant %int 0
         %34 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_34 = OpTypePointer UniformConstant %34
 %u_imageOut = OpVariable %_ptr_UniformConstant_34 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
    %out_pos = OpVariable %_ptr_Function_v2int Function
%pixels_resolution = OpVariable %_ptr_Function_v2float Function
     %in_pos = OpVariable %_ptr_Function_v2float Function
         %15 = OpLoad %v4float %gl_FragCoord
         %16 = OpVectorShuffle %v2float %15 %15 0 1
         %17 = OpConvertFToS %v2int %16
               OpStore %out_pos %17
         %24 = OpLoad %21 %u_imageIn
         %26 = OpImage %20 %24
         %27 = OpImageQuerySizeLod %v2int %26 %int_0
         %28 = OpConvertSToF %v2float %27
               OpStore %pixels_resolution %28
         %30 = OpLoad %v4float %gl_FragCoord
         %31 = OpVectorShuffle %v2float %30 %30 0 1
         %32 = OpLoad %v2float %pixels_resolution
         %33 = OpFDiv %v2float %31 %32
               OpStore %in_pos %33
         %37 = OpLoad %34 %u_imageOut
         %38 = OpLoad %v2int %out_pos
         %39 = OpLoad %21 %u_imageIn
         %40 = OpLoad %v2float %in_pos
         %41 = OpImageSampleImplicitLod %v4float %39 %40
               OpImageWrite %37 %38 %41
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` requires `VK_KHR_maintenance2`. Texture families also require `fragmentStoresAndAtomics`. It asks `getPhysicalDeviceImageFormatProperties()` whether the featured format supports the selected usage and the combined tested and paired usage flags when `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` is supplied.
- `createInstance()` scans the compatible-format list for an uncompressed, framework-supported featureless format that lacks the selected usage but supports the other required usages. A missing candidate skips the test because the parent format would not demonstrate extended usage.
- The attachment path creates source and destination images, uploads generated bytes through a transfer buffer, transitions the source to fragment-read access, runs a render pass, and copies the destination image to a host-visible buffer. Its descriptor set binds the source as an input attachment.
- The texture path follows the same upload, draw, and copyback pattern. Its descriptor set binds a combined image sampler at binding 0 and a storage image at binding 1. It transitions the source for shader reads and the destination for shader writes before the fullscreen draw.
- `GraphicsAttachmentsTestInstance::iterate()` compares the copied destination and original source in 64-bit words. It logs the starting byte offset and values of the first differing 64-bit word and fails the test with `Output differs from input`; equal buffers pass. The texture instance inherits this same `iterate()` implementation and oracle.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `attachment_read` | Extended-usage input-attachment view validation, mutable-format view interpretation, input-attachment read, color-attachment write, or transfer/readback failure. |
| `attachment_write` | Extended-usage color-attachment view validation, mutable-format view interpretation, input-attachment read, color-attachment write, or transfer/readback failure. |
| `texture_read` | Extended-usage sampled-image view validation, sampled-image read, storage-image write, descriptor/pipeline setup, or transfer/readback failure. |
| `texture_write` | Extended-usage storage-image view validation, sampled-image read, storage-image write, descriptor/pipeline setup, or transfer/readback failure. |

### Cause Analysis

#### Extended-usage view validation or mutable-format interpretation

**Possible failure symptoms:** A supported case can fail during image or image-view creation, descriptor setup, render-pass or pipeline creation, or command submission. It may also complete the draw and then report `Output differs from input` after copyback.

**Possible implementation causes:** The test creates a parent image whose featureless format lacks the selected usage and a featured-format view that supplies it. A failure can result from rejecting that extended-usage relationship, applying the parent format instead of the view format while validating the view, or mishandling the compatible mutable-format interpretation. The runtime log is required to identify the failed API stage.

#### Attachment read/write or sampled/storage operation

**Possible failure symptoms:** The case reaches result checking but logs a first differing 64-bit word and fails with `Output differs from input`.

**Possible implementation causes:** Attachment families exercise `subpassLoad()` and fragment color output. Texture families exercise sampling and `imageStore()`. A mismatch can arise in the selected fragment operation, the descriptor/view binding used by it, the format-qualified storage-image path, or the destination write. The common byte comparison does not isolate one operation without the case log and further source-level investigation.

#### Synchronization, transfer, or readback

**Possible failure symptoms:** The destination bytes differ after a completed draw, even if the fragment operation ran. The log reports the first mismatch location and reference/result words.

**Possible implementation causes:** The test uses barriers between host writes, transfer copies, fragment reads or writes, transfer readback, and host reads. An incorrect access mask, pipeline-stage dependency, layout transition, image-to-buffer copy, or host-memory invalidation can produce a stale or corrupted result. The source-level oracle observes the final bytes, so it cannot distinguish these stages by itself.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_maintenance2` and successful extended-usage image-format-property queries for the featured format.
- `texture_read` and `texture_write` require `fragmentStoresAndAtomics`.
- The featureless candidate must be framework-supported, uncompressed, lack the selected usage, and support the remaining usages on the extended side (the two transfer bits). If no candidate exists, the case skips as impossible.
- When `VK_KHR_portability_subset` is enabled without `imageViewFormatReinterpretation`, the featureless and featured formats must have the same bit depth in each component.

### Design-based pruning

- The generator fixes the test to 16 by 16 single-layer 2D images and one sample. It does not vary image type, array layers, mip levels, tiling, or sample count.
- It skips compressed featured formats, sRGB formats, packed types, component-swizzled formats, and three-component formats. The source identifies shader layout-classifier limitations for all but the compressed-format exclusion.
- The factory iterates only the CTS compatible-format lists. It chooses the first candidate that creates the required featured-versus-featureless capability distinction.

## Key Takeaways

- `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` lets the test place the selected usage on a compatible image-view format even though the featureless parent format does not support that usage.
- The four direct test families cover both directions of two complementary usage pairs: input attachment/color attachment and sampled/storage image.
- The featureless-format search makes each executed case meaningful. A normal parent format that supported the selected usage would not test the extended-usage rule.
- The result oracle checks the entire copied byte sequence. It catches an invalid view-usage arrangement, a graphics operation error, or a transfer/readback error, but runtime diagnostics are needed to isolate the stage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Attachment transcode and byte comparison | [`GraphicsAttachmentsTestInstance::iterate()` and `transcode()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L455-L659) | Defines the attachment resource arrangement, upload/draw/copyback flow, and exact result oracle. |
| Image and view helpers | [`makeCreateImageInfo()` and `makeImageViewUsageCreateInfo()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L661-L702) | Shows mutable-format image creation, the optional extended-usage flag, and view-usage construction. |
| Texture transcode | [`GraphicsTextureTestInstance::transcode()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L764-L965) | Defines the sampled-image and storage-image view arrangements and descriptor bindings. |
| Generated shaders | [`ImageTranscodingCase::initPrograms()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L987-L1072) | Generates the fullscreen vertex shader and attachment or texture fragment shader. |
| Support and candidate selection | [`isFormatUsageFlagSupported()`, `checkSupport()`, and `createInstance()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1074-L1169) | Checks requirements and finds the featureless compatible format. |
| Test registration | [`createImageTranscodingSupportTests()`](../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1180-L1261) | Registers the direct test families and per-format leaves. |
| Default Vulkan inventory | [`extended-usage-bit.txt`](../../../mustpass/main/vk-default/image/extended-usage-bit.txt) | Confirms executable leaves under all four direct test families. |
| Extended-usage rule | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc#L1822-L1834) | Defines valid image usages with and without `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. |
| View-usage rule | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc#L6771-L6797) | Defines `VkImageViewUsageCreateInfo` and its override of inherited view usage. |
