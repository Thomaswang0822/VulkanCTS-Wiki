# Understanding Brief: `image.texel_view_compatible`

## One-Sentence Test Purpose

This test checks whether a compressed image created for block-texel-compatible views can be accessed through a size-compatible uncompressed view and retain the expected compressed representation after the selected shader operation.

## Background Knowledge

### Block-texel-compatible image views

A compressed image stores a block of texels in each compressed-format unit. With `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, Vulkan permits an uncompressed, size-compatible view in which one view texel corresponds to one compressed block. The view extent follows the block-count mapping rather than the original texel extent.

Why it matters here:
- The shader sees `r16g16b16a16*` or `r32g32*`/`r32g32b32a32*` values, while the storage image remains compressed.
- The test must choose compressed and uncompressed formats from the same 64-bit or 128-bit size group.

### Transcoding through a view is not color-quality testing

The uncompressed view exposes the bits of a compressed block for the selected access operation. The test later samples compressed result and reference images into `VK_FORMAT_R8G8B8A8_UNORM` images so it can compare their decoded contents. That final comparison checks whether the operation preserved the compressed result in the way the test expects; it does not require a raw byte comparison for every path.

Why it matters here:
- The test excludes floating-point view formats because NaN, infinity, and denormal values cannot reliably survive the required value handling.
- ASTC has a defined error-color exception in the test comparison helper. An error-color-only discrepancy produces a quality warning instead of a normal failure.

## One Concrete Example

Consider the registered compute case:

```text
dEQP-VK.image.texel_view_compatible.compute.basic.2d_image.image_load.bc1_rgb_unorm_block.r16g16b16a16_uint
```

The test creates a BC1 RGB compressed image with mutable, block-texel-compatible, and extended-usage flags. It uploads generated compressed blocks, then makes an `R16G16B16A16_UINT` image view over the compressed image. The view has one unsigned-integer `uimage2D` texel per BC1 block. A compute shader loads each view texel and stores it to an ordinary uncompressed `R16G16B16A16_UINT` image. The host checks that intermediate output, then samples both the resulting compressed representation and a reference into comparable RGBA8 images.

## End-to-End Test Flow

```text
[host] select pipeline, mipmap mode, image type, operation, and a matched compressed/view-format pair
[host] check maintenance2, image-format support, relevant compression feature, and storage-image support when needed
[host] create compressed images with mutable, block-texel-compatible, and extended-usage flags; create uncompressed images and views
[host] generate deterministic input data and upload it to the compressed source or uncompressed source, according to the operation
[host] generate the selected compute or fragment shader, bind views, and submit dispatch or draw work
[device] access the compressed storage through its uncompressed view and write the operation result
[host] copy intermediate data where applicable, then run a decompression/verification pass for result and reference images
[device] sample the compressed images into `VK_FORMAT_R8G8B8A8_UNORM` verification images
[host] copy verification images to host-visible buffers, compare them, and report pass, failure, or an ASTC quality warning
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `TexelViewCompatibleCase::initPrograms()` emits GLSL 4.50 for the selected compute or fragment operation, plus a verification shader.
- Compute operations use `imageLoad`, `texelFetch`, `texture`, or `imageStore`; graphics operations use input attachments or sampled/storage-image paths.
- The generated shader type and image-format qualifier come from the selected uncompressed view format and image type.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Compressed image | Yes | Yes, through an uncompressed view | Read or written according to the operation | Indirectly, through verification | It is the object whose block-texel view compatibility is under test. |
| Uncompressed source/result image | Yes | Yes | Read or written by shader | Yes for compute intermediate checks | It supplies or receives the values visible through the compatible view. |
| Image views | Yes | Yes, in descriptors or framebuffer attachments | Shader-visible | No | The compressed image uses an uncompressed view format. |
| Verification images and buffers | Yes | Yes | Verification shader writes images | Yes | They make decoded compressed results comparable on the host. |
| Descriptor sets, sampler, pipeline, and render pass where needed | Yes | Yes | Used by selected shader path | No | They select the access mechanism being tested. |

## What Is Checked

- Compute read operations first compare the uncompressed output against the expected generated data before decompression.
- The verification pass samples a result compressed image and a reference compressed image into matching `VK_FORMAT_R8G8B8A8_UNORM` images. The host compares those images.
- Graphics paths use the same decoded-result comparison after their draw work.
- Any ordinary mismatch fails the case. ASTC error-color-only differences set a quality-warning result rather than a normal pass or failure.

## Behavior Parameter Identification

> **Behavior parameter:** `operation`
>
> **Candidate values:** `image_load`, `texel_fetch`, `texture`, `image_store`, `attachment_read`, `attachment_write`, `texture_read`, `texture_write`

The operation is the primary behavioral axis because it changes the access mechanism used with the uncompressed view. Pipeline type limits which operations are registered: compute has the first four, graphics has the last four, and 3D graphics omits attachment operations.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `image_load` | A storage-image load or store through a block-texel-compatible view does not preserve the expected block value. |
| `texel_fetch` | A sampled texel fetch through the compatible view addresses or interprets a compressed block incorrectly. |
| `texture` | Filtered-coordinate sampling through the compatible view or the associated view sizing is incorrect. |
| `image_store` | Writing through the compatible view does not produce the expected compressed representation. |
| `attachment_read` | An input-attachment read through the compatible view does not transfer the expected value. |
| `attachment_write` | A color-attachment write through the compatible view does not produce the expected compressed representation. |
| `texture_read` | A fragment sampled-texture read through the compatible view does not transfer the expected value. |
| `texture_write` | A fragment storage-image write through the compatible view does not produce the expected compressed representation. |

## Important Variations and Special Cases

- `basic` uses a 64×64 base size. `extended` uses deliberately non-aligned dimensions derived from the compressed block extent, multiple mip levels, and three layers for non-3D images.
- `multi_layer_views` exists only outside Vulkan SC. It uses a 2D-array compatible view with three layers and requires the Maintenance 6 `blockTexelViewCompatibleMultipleLayers` property.
- The support check skips unsupported image-format/usage combinations and checks BC, ETC2, or ASTC LDR compression features according to the selected compressed format.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case parameters and comparison behavior | [test parameters and comparison helper](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L108-L218) | Defines formats, operation choices, and ASTC error-color handling. |
| Compute setup and intermediate checks | [BasicComputeTestInstance::iterate](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L730-L915) | Creates resources, dispatches work, and reports compute-path outcomes. |
| Graphics execution and decoded comparison | [GraphicsAttachmentsTestInstance::iterate](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1887-L1935) | Shows the graphics-path pass/fail decision. |
| Generated shaders | [TexelViewCompatibleCase::initPrograms](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3147-L3520) | Emits operation and verification shaders. |
| Support gates and instance routing | [checkSupport and createInstance](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3517-L3625) | Maps legal cases to implementations. |
| Registered matrix | [createImageCompressionTranscodingTests](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3651-L3975) | Registers exact paths and format sets. |
| Vulkan block-texel-view rules | [format size compatibility](../../../../vulkan-docs/src/chapters/formats.adoc#L2009-L2034) and [image-view validity](../../../../vulkan-docs/src/chapters/resources.adoc#L6231-L6287) | Grounds the compatible-view and multi-layer semantics. |

## Questions / Risk Points for User Audit

- Does the distinction between reading/writing compressed storage through an uncompressed view and final decoded-result comparison read clearly?
- Is `operation` the right primary behavioral axis for grouping the failure analysis?
- Does the representative `image_load` case provide enough shader detail without duplicating every generated variant?
- Are the ASTC quality-warning semantics clear enough to distinguish them from a pass or failure?

## Conversion Notes for Final Wiki Rewrite

- Keep the two background bullets short and move the concrete BC1 example into the shader walkthrough.
- Preserve the `### Failure Cause Mapping` table unchanged in the Level-3 page.
- Use `operation` as `## Behavior Parameters`; retain the full registered matrix in the preceding parameter table.
- Include one compute `image_load` walkthrough and its generated SPIR-V because it shows the core compatible-view data path. Explain other operations in the variation table rather than reconstructing more shaders.
