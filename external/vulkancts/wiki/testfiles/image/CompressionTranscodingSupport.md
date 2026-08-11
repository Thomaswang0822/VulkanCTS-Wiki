## Overview

**Core question:** Can a compressed image expose each compressed block through a legal size-compatible uncompressed view, and do the selected shader accesses preserve the expected result?

- This page documents the implementation in [`vktImageCompressionTranscodingSupport.cpp`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1) for the `image.texel_view_compatible` test family.
- The tests create compressed images with `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT`, `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, and extended usage, then access them through matched uncompressed views.
- Compute and graphics paths cover distinct read and write mechanisms. A separate non-Vulkan-SC family checks a compatible view spanning multiple array layers.
- The page explains the registered matrix, a representative generated compute shader, host-side execution and comparison, support gates, and the meaning of a mismatch.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Block-texel-compatible image view.** A compressed image stores a block of texels in one compressed-format unit. `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT`, together with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, permits a size-compatible uncompressed image view where one view texel maps to one compressed block. The view extent follows the compressed block count, not the image's original texel dimensions.
- **Decoded comparison.** The test does not reduce every path to a raw compressed-byte comparison. It samples result and reference compressed images into `VK_FORMAT_R8G8B8A8_UNORM` verification images and compares the decoded results. ASTC error-color-only differences have a dedicated quality-warning outcome.

## Registration Hierarchy

```text
image.texel_view_compatible
├── compute
├── graphic
└── multi_layer_views
```

`compute` and `graphic` each expand through `basic` or `extended`, image type, operation, compressed format, and uncompressed view format. `multi_layer_views` is compiled only outside Vulkan SC and is compute-only. The test category registration calls [`createImageCompressionTranscodingTests()`](../../../modules/vulkan/image/vktImageTests.cpp#L74).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline | `compute`, `graphic` | Selects compute descriptors/dispatch or graphics render-pass/draw execution. | [registration loop](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3805-L3902) |
| Mipmap mode | `basic`, `extended` | `basic` uses one level; `extended` uses multiple mip levels, deliberately non-aligned sizes, and three layers for non-3D images. | [mipmap parameters](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3659-L3672), [case construction](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3864-L3883) |
| Image type | `1d_image`, `2d_image`, `3d_image` | Changes view type, shader coordinates, and valid operation combinations. | [image type list and pruning](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3674-L3682), [registration conditions](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3820-L3836) |
| Operation | `image_load`, `texel_fetch`, `texture`, `image_store`, `attachment_read`, `attachment_write`, `texture_read`, `texture_write` | This is the primary behavior axis. It selects the shader access mechanism and the associated resource usages. | [operation names and usage flags](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3665-L3733) |
| Compressed format | 12 64-bit BC1/BC4/ETC2/EAC formats; 42 128-bit BC2/BC3/BC5/BC6H/BC7, ETC2/EAC, and ASTC formats | Supplies the compressed backing storage. The format determines block extent, required compression feature, and ASTC warning behavior. | [format sets](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3737-L3766) |
| Uncompressed view format | Eight 64-bit normalized, scaled, or integer `R16G16B16A16`/`R32G32` formats; two 128-bit `R32G32B32A32` integer formats | Gives the shader a size-compatible typed view of each compressed block. Floating-point alternatives are intentionally absent. | [view-format sets and exclusions](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3768-L3799) |
| Multi-layer mode | ordinary single-layer views; `multi_layer_views` | The special family uses a 2D-array view spanning three layers. | [multi-layer registration](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3905-L3971) |

The compressed and uncompressed format arrays are paired by total block size, producing 180 compressed/view-format pairs per operation. The current Vulkan mustpass lists contain 4,320 compute cases, 3,600 graphics cases, and 720 non-SC multi-layer cases; the Vulkan SC list omits those 720 multi-layer cases. See the [Vulkan list](../../../mustpass/main/vk-default/image/texel-view-compatible.txt#L1) and [Vulkan SC list](../../../mustpass/main/vksc-default/image/texel-view-compatible.txt#L1). Vulkan defines the size-compatible-view rule and block-extent mapping in [the format chapter](../../../../vulkan-docs/src/chapters/formats.adoc#L2009-L2034).

## Behavior Parameters

The primary behavioral axis is `operation`. Its values change the shader interface and the way the compatible view is read or written.

### `image_load`: storage-image load and store

A compute shader uses `imageLoad` on the uncompressed view of compressed storage, then writes the returned value through `imageStore` to an uncompressed result image. It directly tests storage-image access to a compressed block through the compatible view.

### `texel_fetch`: sampled integer-coordinate read

A compute shader reads the compatible view with `texelFetch` and writes the fetched value to a storage image. This isolates the sampler path that uses integer texel coordinates and an explicit mip level.

### `texture`: sampled normalized-coordinate read

A compute shader samples the compatible view with `texture` at coordinates derived from the invocation position. It checks the sampled-image path and coordinate/view-extent interpretation rather than `imageLoad` semantics.

### `image_store`: read, write, and read-back through compatible storage

A compute shader reads an uncompressed source image, writes the value through a compatible view of compressed storage, then reads that view and writes a final uncompressed result. This is the compute write path.

### `attachment_read`: fragment input-attachment read

A graphics pipeline makes the compatible view available as an input attachment. The fragment shader uses `subpassLoad` and writes the value to its color output.

### `attachment_write`: fragment color-attachment write

A graphics pipeline uses the compatible view as the color attachment. The fragment shader writes to it, exercising the graphics write path into compressed storage.

### `texture_read`: fragment sampled-texture read

A fragment shader samples the compatible view and writes the value into an uncompressed storage-image output. It is the graphics equivalent of a sampled read.

### `texture_write`: fragment storage-image write

A fragment shader samples an uncompressed source and writes through the compatible view of compressed storage. It is the graphics sampled-read plus compressed-storage-write path.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.texel_view_compatible.compute.basic.2d_image.image_load.bc1_rgb_unorm_block.r16g16b16a16_uint
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute.basic.2d_image` | Uses the compute implementation, one mip level, one layer, and 2D integer coordinates. |
| `image_load` | Loads each compatible-view texel as a storage image and stores it to an ordinary uncompressed image. |
| `bc1_rgb_unorm_block.r16g16b16a16_uint` | Pairs a 64-bit BC1 block with a 64-bit unsigned-integer view format. |

#### Purpose

The shader copies each block-sized `R16G16B16A16_UINT` view texel from the compressed BC1 image into an ordinary uncompressed result image. The surrounding test then checks this intermediate output and compares decoded compressed result/reference images.

#### Structural Design

| Phase | Shader action | Tested relationship |
|-------|---------------|---------------------|
| Address | Convert `gl_GlobalInvocationID.xy` to `ivec2 pos`. | One compute invocation addresses one uncompressed-view texel, which represents one compressed block. |
| Load | `imageLoad(u_image0, pos)` reads the compatible view. | The compressed backing image must expose the expected block value through the size-compatible view. |
| Store | `imageStore(u_image1, pos, ...)` writes the observed value. | The host can inspect an ordinary uncompressed result before decoded verification. |

#### Shader Code

```glsl
#version 450
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// Binding 0 is an `R16G16B16A16_UINT` view of the BC1 compressed source image.
/// Each view texel corresponds to one 64-bit compressed block.
layout (binding = 0, rgba16ui) readonly uniform uimage2D u_image0;

/// Binding 1 is an ordinary uncompressed result image with the same block-grid extent.
layout (binding = 1, rgba16ui) writeonly uniform uimage2D u_image1;

void main (void)
{
    /// The basic 2D case uses one invocation for each compatible-view texel.
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    imageStore(u_image1, pos, imageLoad(u_image0, pos));
}
```

#### Additional Info

- `initPrograms()` derives `uimage2D` and `rgba16ui` from the selected unsigned-integer view format; the same generator changes the type, qualifier, coordinate form, and access expression for other image types and operations.
- The CTS source creates the compressed image with mutable-format, block-texel-compatible, and extended-usage flags before making this uncompressed view.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image type | `1d_image` uses an integer coordinate; `3d_image` uses `ivec3`; multi-layer views add `Array` and use the invocation Z coordinate as the layer. | [compute coordinate branches](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3175-L3200) |
| View format | The generated image type gains an `i` or `u` prefix for signed or unsigned formats, and the layout qualifier changes with the selected format. | [type/qualifier derivation](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3158-L3167), [helper implementation](../../../modules/vulkan/image/vktImageTestsUtil.cpp#L551-L608) |
| Compute operation | `texel_fetch` declares a sampler and uses `texelFetch`; `texture` samples normalized coordinates; `image_store` declares three storage images and writes through the compatible image. | [operation generators](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3204-L3290) |
| Graphics operation | Attachment cases use `subpassLoad`; texture cases sample a compatible view and write a storage image. | [fragment generators](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3368-L3430) |

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
; Bound: 30
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %u_image1 "u_image1"
               OpName %u_image0 "u_image0"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_image1 NonReadable
               OpDecorate %u_image1 Binding 1
               OpDecorate %u_image1 DescriptorSet 0
               OpDecorate %u_image0 NonWritable
               OpDecorate %u_image0 Binding 0
               OpDecorate %u_image0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
         %18 = OpTypeImage %uint 2D 0 0 0 2 Rgba16ui
%_ptr_UniformConstant_18 = OpTypePointer UniformConstant %18
   %u_image1 = OpVariable %_ptr_UniformConstant_18 UniformConstant
   %u_image0 = OpVariable %_ptr_UniformConstant_18 UniformConstant
     %v4uint = OpTypeVector %uint 4
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v2int Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %pos %17
         %21 = OpLoad %18 %u_image1
         %22 = OpLoad %v2int %pos
         %24 = OpLoad %18 %u_image0
         %25 = OpLoad %v2int %pos
         %27 = OpImageRead %v4uint %24 %25
               OpImageWrite %21 %22 %27
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The support check requires `VK_KHR_maintenance2`, queries format/usage support for both image forms, checks the relevant BC, ETC2, or ASTC LDR compression feature, and requires storage-image support for the uncompressed format when the operation uses it. Multi-layer cases also require `blockTexelViewCompatibleMultipleLayers`.
- Compute cases create one compressed image and one or two uncompressed images. The compressed image is created with the three required flags; the uncompressed image extent is the compressed block-grid extent. The test uploads generated input to compressed storage for read operations and to uncompressed storage for `image_store`.
- The compute implementation binds storage-image or combined-image-sampler descriptors based on the operation, dispatches the generated shader, and checks the ordinary uncompressed output before the verification pass.
- Graphics cases prepare data and vertex input, create the render pass and pipeline, transfer source data, draw, and copy the output to host-visible memory. `attachment_write` and `texture_write` direct the write into compressed storage; the corresponding read cases reverse the transfer direction.
- The verification path samples a result compressed image and a reference compressed image into two `VK_FORMAT_R8G8B8A8_UNORM` images, copies those images to host buffers, and runs `BinaryCompare`. A normal mismatch falls back to a per-layer fuzzy comparison for logging. An ASTC error-color-only result records a quality warning.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `image_load` | A storage-image load or store through a block-texel-compatible view does not preserve the expected block value. |
| `texel_fetch` | A sampled texel fetch through the compatible view addresses or interprets a compressed block incorrectly. |
| `texture` | Normalized-coordinate sampling through the nearest-filtered compatible view or the associated view sizing is incorrect. |
| `image_store` | Writing through the compatible view does not produce the expected compressed representation. |
| `attachment_read` | An input-attachment read through the compatible view does not transfer the expected value. |
| `attachment_write` | A color-attachment write through the compatible view does not produce the expected compressed representation. |
| `texture_read` | A fragment sampled-texture read through the compatible view does not transfer the expected value. |
| `texture_write` | A fragment storage-image write through the compatible view does not produce the expected compressed representation. |

### Cause Analysis

#### Compatible-view read failures

**Possible failure symptoms:** `image_load`, `texel_fetch`, `texture`, `attachment_read`, or `texture_read` reports an uncompressed-output mismatch or an image-difference failure after decoded comparison.

**Possible implementation causes:** Image-view creation may fail to apply the compressed block-to-uncompressed texel mapping required by `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT`. The sampled or storage-image access path may also use the wrong block-grid extent, coordinate mapping, or selected view format. The relevant rules require the uncompressed view format to be size-compatible with the compressed image format and define how its extent maps to compressed blocks.

#### Compatible-view write failures

**Possible failure symptoms:** `image_store`, `attachment_write`, or `texture_write` fails the intermediate comparison or produces a decoded compressed result different from the reference.

**Possible implementation causes:** The implementation may not preserve the expected compressed representation when a storage image or color attachment writes through the uncompressed compatible view. An error can also occur in synchronization or layout transitions between the shader write, image-to-buffer copy, and host readback. The source inserts pipeline barriers before these transfers; a failure requires source-level investigation to distinguish an access-semantics defect from a transition or visibility defect.

#### ASTC error-color handling discrepancy

**Possible failure symptoms:** The case returns a quality warning instead of `Pass`, or an ASTC mismatch that is not limited to permitted error colors fails.

**Possible implementation causes:** The comparison helper treats ASTC error-color differences separately from ordinary mismatches. If the observed difference is not classified as the permitted error-color case, the normal result/reference comparison fails. This outcome describes the CTS comparison policy; it does not, by itself, identify a driver or hardware fault.

## Case Pruning

### Requirement-based pruning

- The test skips a case when `VK_KHR_maintenance2`, selected image format/usage support, the relevant BC/ETC2/ASTC compression feature, or the checked uncompressed storage-image support is unavailable. In the current source, the storage-feature guard tests `uncompressedImageUsage` against `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT`; because that bit value overlaps the always-present transfer-destination usage bit, the guard runs for every registered case, not only operations whose primary access uses a storage image.
- `multi_layer_views` skips when `VkPhysicalDeviceMaintenance6Properties::blockTexelViewCompatibleMultipleLayers` is false. Vulkan SC excludes this family at compile time.
- Graphics attachment operations are not registered for `3d_image`.

### Design-based pruning

- Compute registers only `image_load`, `texel_fetch`, `texture`, and `image_store`; graphics registers only attachment and texture read/write operations. This keeps each operation under an implementation that can exercise it.
- Floating-point compatible-view formats are excluded because values such as NaNs, infinities, and denormals cannot be relied on to preserve the underlying texture data for this test.
- Basic cases use one layer and one mip level. Extended cases add mipmaps and layers where meaningful; 3D images retain one layer.

## Key Takeaways

- The test checks the special Vulkan relationship in which a compressed image exposes each compressed block as one uncompressed view texel.
- Format pairs share a 64-bit or 128-bit block size; the test varies the access mechanism, image dimensionality, mipmap shape, and compressed codec independently around that constraint.
- The intermediate compute check catches direct compatible-view transfer errors, while final decoded comparison checks the resulting compressed representation across compute and graphics paths.
- `multi_layer_views` extends the same model to a single compatible 2D-array view, subject to the Maintenance 6 property.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and ASTC comparison helper | [source lines 108 to 218](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L108-L218) | Defines parameters and special ASTC error-color treatment. |
| Compute execution | [BasicComputeTestInstance::iterate](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L730-L915) | Allocates compute resources, uploads data, dispatches work, and checks outcomes. |
| Compressed/uncompressed image setup | [BasicComputeTestInstance::createImageInfos](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1201-L1285) | Shows image flags, view formats, and block-grid extents. |
| Graphics execution | [GraphicsAttachmentsTestInstance::iterate](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1887-L1935) | Shows graphics-path validation. |
| Generated shader source | [TexelViewCompatibleCase::initPrograms](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3147-L3520) | Builds operation and verification shaders. |
| Support gates and instance selection | [checkSupport and createInstance](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3517-L3625) | Defines required features and implementation routing. |
| Matrix registration | [createImageCompressionTranscodingTests](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3651-L3975) | Registers exact hierarchy, operations, and format pairs. |
| Vulkan mustpass matrix | [texel-view-compatible.txt](../../../mustpass/main/vk-default/image/texel-view-compatible.txt#L1) | Confirms the registered Vulkan case paths and counts. |
| Vulkan SC mustpass matrix | [texel-view-compatible.txt](../../../mustpass/main/vksc-default/image/texel-view-compatible.txt#L1) | Confirms that Vulkan SC excludes `multi_layer_views`. |
| Vulkan format rule | [format size compatibility](../../../../vulkan-docs/src/chapters/formats.adoc#L2009-L2034) | Defines compatible compressed/uncompressed view sizing. |
| Vulkan image-view validity | [block-texel image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L6231-L6287) | Defines required image flags, legal view formats, and multi-layer restriction. |
