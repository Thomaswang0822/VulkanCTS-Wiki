# Understanding Brief: `api.copy_and_blit.reinterpret`

## One-Sentence Test Purpose

This test checks whether implementations correctly treat `vkCmdCopyImage` as a byte-exact memcpy and correctly honor format-mutable, block-texel-view-compatible image views when an image is copied and then sampled through a view of a different but size-compatible format.

## Background Knowledge

### Size-compatible format reinterpretation

Vulkan permits `vkCmdCopyImage` between formats whose texel block size in bytes is identical. The spec models the operation as a byte-for-byte memcpy; the implementation must not reinterpret channels or convert between formats. A `VkImage` created with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` may be viewed through a `VkImageView` of a different format from the image format, provided the view format is size-compatible with the image format.

Why it matters here:

- The test exercises the simplest case where source and destination images share the same format and the view format differs from both, isolating the reinterpretation behavior from cross-format copy questions.
- For the uncompressed pair (`VK_FORMAT_B10G11R11_UFLOAT_PACK32` image viewed as `VK_FORMAT_R16G16_SFLOAT`), `formatsAreCompatible()` confirms equal texel size (32 bits) before registration, so the case is legal under `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` alone.

### Block-texel-view-compatible compressed images

For compressed formats (BC, ETC2, ASTC, etc.), Vulkan normally forbids creating an uncompressed-format view. `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` relaxes this restriction: an uncompressed view of a compressed image is allowed when the view format's texel size matches the compressed block size in bytes. `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` is also required so that the image can be created with usage flags (transfer, storage, sampled) that are legal for the view format but not always for the compressed image format. Both flags are gated on `VK_KHR_maintenance2` (Vulkan 1.1+).

Why it matters here:

- The BC1 case uses a 64-bit block and an `VK_FORMAT_R32G32_UINT` view (64-bit texel). The BC3 case uses a 128-bit block and an `VK_FORMAT_R32G32B32A32_UINT` view (128-bit texel). Both are legal block-texel-view-compatible reinterpretations.
- The view format's texel size matching the compressed block size is what makes the reinterpretation well-defined: one view texel corresponds exactly to one compressed block in memory.

### 1D exception for compressed-format copy regions

VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152 require that for `VK_IMAGE_TYPE_1D` compressed images, only the x-dimensions of `srcOffset` / `dstOffset` / `extent` are scaled by the block width; the y-dimensions are effectively ignored because the image height is 1. For `VK_IMAGE_TYPE_2D`, both x and y are scaled by block width and height respectively.

Why it matters here:

- The 1D and 2D intermediate nodes exercise this distinction directly. A driver that scales y for 1D images, or fails to scale y for 2D images, produces wrong region bounds.

## One Concrete Example

Consider the `2d.copy_bc1_rgb_unorm_block_sample_r32g32_uint` leaf:

- Source and destination images are `VK_IMAGE_TYPE_2D`, format `VK_FORMAT_BC1_RGB_UNORM_BLOCK`, extent `defaultExtent` (64×64×1). Each 4×4 block of texels occupies 64 bits (8 bytes) in memory.
- Both images are created with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT | VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`.
- A `VkImageView` of format `VK_FORMAT_R32G32_UINT` (64-bit texel = 8 bytes) is created on the source image. One view texel corresponds exactly to one BC1 block.
- A compute shader `compFill` writes a known 64-bit pattern (mnemonic "blue": `2031647u, 0u`) into the source image and a different pattern (mnemonic "red": `4160813056u, 0u`) into the destination image, via `imageStore` through the view format.
- `vkCmdCopyImage` copies the source to the destination as a byte-exact memcpy. After the copy, the destination must hold the "blue" pattern in every block.
- A second compute shader `compVerify` reads each destination texel through the view format and compares it against the expected "blue" pattern; it writes green to an `R8G8B8A8_UNORM` output image on match and red on mismatch.
- The host reads the output image back and compares against an all-green reference. Any non-green pixel means the copy did not preserve the bytes for that block.

The same image is also sampled through the view format by a fragment shader `texelFetch`, with the sampling result verified by the same compute-shader green/red mechanism against the rendered output image.

## End-to-End Test Flow

```text
[host] choose image type (1D or 2D) and format pair (image format + view format)
[host] create source and destination VkImage with MUTABLE_FORMAT_BIT, plus BLOCK_TEXEL_VIEW_COMPATIBLE_BIT and EXTENDED_USAGE_BIT when the format is compressed
[host] checkSupport: query vkGetPhysicalDeviceImageFormatProperties for image format and view format; check VK_KHR_maintenance2 for compressed cases; check dimension limits; check COPY_COMMANDS_2 if requested
[host] bind memory (suballocated, universal queue, optimal tiling)

[host] for uncompressed: fill host-side source/dest tcu::TextureLevel via generateBuffer (FILL_MODE_RED source, FILL_MODE_BLACK dest), compute expected via copyRegionToTextureLevel (memcpy reference), upload via uploadImage
[host] for compressed: dispatch compFill compute shader that imageStore's "blue" into source and "red" into destination through the view format, then barrier to TRANSFER_DST_OPTIMAL

[host] record pipeline barriers moving source to TRANSFER_SRC_OPTIMAL and destination to TRANSFER_DST_OPTIMAL (or GENERAL if useGeneralLayout, which this family forbids by DE_ASSERT)
[host] record vkCmdCopyImage (or vkCmdCopyImage2 with COPY_COMMANDS_2) with a single whole-image region; for compressed, x is scaled by blockWidth and y by blockHeight (2D only)
[host] record pipeline barrier moving source to SHADER_READ_ONLY_OPTIMAL

[host] for sampling: build a graphics pipeline (vertex + fragment shader), descriptor set with combined image sampler on the source view; begin renderpass, draw 6 vertices (full-screen triangle strip), texelFetch the source through the view format, write to color attachment
[host] for uncompressed sampling: copyImageToBuffer the color attachment to a host-visible buffer
[host] for compressed sampling: dispatch compVerify against the rendered output image; copyImageToBuffer the compVerify output image to a host-visible buffer

[device] fragment shader reads texelFetch through the reinterpreted view
[device] compute shader (compVerify) imageLoads the destination or output image through the view format and writes green/red to an R8G8B8A8_UNORM output

[host] for uncompressed copy: readImage the destination, compare via tcu::floatThresholdCompare (threshold 0.01) against the host-computed memcpy reference
[host] for compressed copy: dispatch compVerify against the destination, read back the compVerify output, compare against an all-green reference via tcu::floatThresholdCompare (threshold 0.01)
[host] decide pass/fail: any mismatch in either the copy check or the sampling check fails the test
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `vert` GLSL 450 vertex shader: emits a full-screen triangle strip and a texture coordinate used by `texelFetch`. For 1D, the coordinate is a single `float`; for 2D, a `vec2`.
- `frag` GLSL 450 fragment shader: declares a `sampler1D` or `sampler2D` (with `u`/`i` prefix when the view format is unsigned/signed integer), calls `texelFetch(tex, ivec*(texCoord * renderSize), 0)`, swizzles the components matching the view format's used channels, and writes the result to `outColor`.
- `compFill` GLSL 450 compute shader (compressed cases only): declares two `image1D`/`image2D` storage images in the view format with layout qualifier, writes the hardcoded "blue" pattern into the source and "red" pattern into the destination via `imageStore`, with workgroup size (1,1,1) dispatched over `getSizeInBlocks(...)`.
- `compVerify` GLSL 450 compute shader (compressed cases only): declares the destination/output image as `image1D`/`image2D` in the view format and an `rgba8` output image, calls `imageLoad` on the test image, compares against the expected "blue" pattern, and `imageStore`s green on match or red on mismatch.
- Hardcoded bit pattern constants per format pair (e.g. `bc1Blue2 = "2031647, 0u"`, `bc1Red4 = "4160813056u, 0u, 4160813056u, 0u"`, `bc3Blue4`, `bc3Red4`). These are the literal byte patterns written to memory and compared after the copy; the "blue"/"red" labels are mnemonic only.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `m_source` (VkImage, image format) | yes | yes (memory bound) | yes (compFill write or uploadImage; copy reads; texelFetch reads) | no | The image whose bytes are copied and reinterpreted through the view. |
| `m_destination` (VkImage, image format) | yes | yes (memory bound) | yes (compFill write or uploadImage; copy writes; compVerify reads) | for uncompressed, readImage | The image that receives the copy and is verified through the view format. |
| `imageView` (VkImageView, view format) | yes | yes | yes (fragment shader `texelFetch`, `compFill`/`compVerify` storage image) | no | The reinterpretation lens: same memory, different format. |
| `outputImage` (VkImage, view format for sampling output; R8G8B8A8_UNORM for compVerify output) | yes | yes | yes (color attachment write or compVerify storage write) | yes via copyImageToBuffer | Captures the sampling result (uncompressed) or the green/red verdict (compressed). |
| `resultBuffer` (VkBuffer, host-visible) | yes | yes | yes (transfer dst) | yes (invalidateAlloc) | Host-side readback target for the per-pixel verification result. |
| Descriptor set with combined image sampler (binding 0) | yes | yes | yes (fragment shader reads) | no | Wires the source view to the fragment shader's `texelFetch`. |
| Descriptor set with two storage images (bindings 0, 1) | yes | yes | yes (compute shader read/write) | no | Wires source/destination (compFill) or test image/output image (compVerify) to the compute shaders. |
| Host-side `tcu::TextureLevel` for source/dest/expected | yes | no (host only) | no | n/a | Used to compute the memcpy reference for uncompressed cases. |

## What Is Checked

Two independent checks per test case leaf; either failing causes the case to fail:

- **Copy check.** After `vkCmdCopyImage`, the destination must hold the same bytes as the source.
  - Uncompressed: `tcu::floatThresholdCompare` with threshold `0.01` between `readImage(destination)` and the host-computed reference `m_expectedTextureLevel[0]`. The reference uses `copyRegionToTextureLevel`, which applies the source format to the destination buffer to mimic the spec's memcpy semantics.
  - Compressed: `compVerify` compute shader `imageLoad`s each destination texel through the view format and compares against the expected pattern; writes green (match) or red (mismatch) to an `R8G8B8A8_UNORM` output image. The host reads the output back and `tcu::floatThresholdCompare`s against an all-green reference (threshold `0.01`).
- **Sampling check.** Sampling the source image through the view-format `imageView` via `texelFetch` must produce the reinterpreted bytes.
  - Uncompressed: the rendered color attachment is read back and `tcu::floatThresholdCompare`d (threshold `0.01`) against `outputTexureLevelPixels`, which is the source texture data reinterpreted through the view format.
  - Compressed: `compVerify` runs against the rendered output image (rather than the destination) and uses the same green/red mechanism.

The check is per-texel (or per-block for compressed); any single mismatch fails the case. There is no aggregation or tolerance beyond the fixed `0.01` float threshold used purely to absorb floating-point rounding in the host reference, not to forgive byte differences.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf — the format pair (image format ↔ view format)
>
> **Candidate values:** `copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat`, `copy_bc1_rgb_unorm_block_sample_r32g32_uint`, `copy_bc3_unorm_block_sample_r32g32b32a32_uint`

A secondary axis is the intermediate node `1d` / `2d`, which changes image type and exercises the 1D exception for compressed-format copy regions. The format pair is the primary axis because it changes which Vulkan feature is exercised (`MUTABLE_FORMAT_BIT` alone vs. `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` + `EXTENDED_USAGE_BIT`), which verification mechanism is used (host-side float compare vs. compute-shader green/red), and which block size class is covered (uncompressed 32-bit, compressed 64-bit, compressed 128-bit).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat` (uncompressed 32-bit pair) | `vkCmdCopyImage` not byte-exact across size-compatible uncompressed pairs; `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` not honored by the sampling path; view-format sampling reads wrong channels; host-side memcpy reference mismatch. |
| `copy_bc1_rgb_unorm_block_sample_r32g32_uint` (compressed 64-bit block) | `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` not honored for 64-bit blocks; `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` not honored; storage-image `imageStore`/`imageLoad` through the view does not access the underlying block bytes; copy does not memcpy the 64-bit block; 1D vs 2D block-size scaling wrong. |
| `copy_bc3_unorm_block_sample_r32g32b32a32_uint` (compressed 128-bit block) | Same as BC1 case but for 128-bit blocks; view texel size to compressed block size mapping wrong; `R32G32B32A32_UINT` view of a BC3 image misaligned. |
| All leaves under `1d` (secondary axis) | 1D-specific block-size scaling: y-dimensions of `srcOffset`/`dstOffset`/`extent` mishandled per VUID-vkCmdCopyImage-srcImage-00146 / VUID-vkCmdCopyImage-dstImage-00152. |
| All leaves under `2d` (secondary axis) | 2D block-size scaling: x and y both must be scaled by block width and height; image type routing wrong. |

## Important Variations and Special Cases

- **Uncompressed vs. compressed verification asymmetry.** Uncompressed cases use host-side `tcu::floatThresholdCompare` against a host-computed memcpy reference. Compressed cases cannot use `uploadImage` to seed the image (compressed texels are not directly writable from host staging in a portable way), so a compute shader `compFill` writes known bit patterns via storage image writes, and `compVerify` reads back through the view format and emits a green/red verdict image. The verification mechanism difference is a test-design consequence of compressed format semantics, not a separate tested property.
- **Hardcoded bit pattern constants.** The "blue" and "red" labels in `compFill` and `compVerify` are mnemonic; what matters is that the same 64-bit or 128-bit pattern is written, copied, and compared. The constants differ between BC1 (64-bit, 2 `uint` components) and BC3 (128-bit, 4 `uint` components).
- **`COPY_COMMANDS_2` variant support.** The test instance supports both `vkCmdCopyImage` and `vkCmdCopyImage2` via the `extensionFlags` parameter, but the registration in `createReinterpretationTests()` does not set `COPY_COMMANDS_2`, so all registered mustpass leaves use `vkCmdCopyImage`. The `compVerify` and `compFill` shaders are uploaded only when the source format is compressed.
- **`VK_KHR_maintenance2` requirement.** Compressed cases require `VK_KHR_maintenance2` (or Vulkan 1.1+) for `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. Devices without it throw `NotSupportedError` in `checkSupport()` and the case is skipped, not failed.
- **DE_ASSERT constraints.** The test case constructor asserts that source and destination formats are identical, tiling is optimal, allocation is suballocated, queue is universal, no red clear, no secondary command buffer, no sparse binding, no general layout. These constraints reduce the parameter space to the format reinterpretation scenario only.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `ReinterpretTestInstance` class | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L35-L57`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L35-L57) | Owns source/destination images, view format, and overrides `iterate()`, `checkTestResult()`, `copyRegionToTextureLevel()`. |
| Constructor: image creation with `MUTABLE_FORMAT_BIT` and `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L59-L140`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L59-L140) | Shows when each flag is added based on whether the format differs from the view and whether the format is compressed. |
| `copyRegionToTextureLevel` memcpy reference | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L152-L216`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L152-L216) | Host-side reference for uncompressed copy verification; replaces destination format with source format to mimic memcpy. |
| `fillCompressedImages` (compFill dispatch) | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L218-L311`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L218-L311) | Computes dispatch over `getSizeInBlocks`, binds storage image descriptors, records pre/post barriers around `compFill`. |
| `checkTestResult(testImage, ...)` (compVerify dispatch) | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L316-L466`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L316-L466) | Dispatches `compVerify` against a test image, reads back the green/red output, and compares against an all-green reference. |
| `iterate()` end-to-end | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L468-L863`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L468-L863) | Wires upload/fill, copy, sampling renderpass, and verification; gates per-branch on `srcCompressed`. |
| `ReinterpretTestCase` constructor with `DE_ASSERT` constraints | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L886-L905`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L886-L905) | Documents the constrained parameter space. |
| `checkSupport()` | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L912-L979`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L912-L979) | Gates `VK_KHR_maintenance2`, queries image format properties for both image and view formats, and validates 1D/2D dimension limits. |
| `initPrograms()` shader generation | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L981-L1110`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L981-L1110) | Generates `vert`, `frag`, and (compressed only) `compFill` + `compVerify`. |
| `createReinterpretationTests()` registration | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L1119-L1198`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1119-L1198) | Defines the three format pairs and two image types, and registers leaves under `1d` and `2d`. |
| `formatsAreCompatible()` size check | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L881-L884`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L881-L884) | Used to admit the uncompressed pair; compressed cases bypass this check. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L290`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L290) | Adds `createReinterpretationTests()` directly under `copy_and_blit`. |
| `getSizeCompatibleTcuTextureFormat()` helper | [`vktApiCopiesAndBlittingUtil.cpp#L170-L177`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L170-L177) | Maps compressed formats to size-compatible uncompressed tcu formats for host-side texture levels. |

## Questions / Risk Points for User Audit

- Is the core test purpose clear: byte-exact memcpy through `vkCmdCopyImage` plus correct sampling through a format-mutable view?
- Is the asymmetric verification (host float compare for uncompressed, compute green/red for compressed) understandable as a consequence of compressed-format semantics rather than a separate tested property?
- Are the hardcoded bit pattern constants (`bc1Blue2`, `bc1Red4`, `bc3Blue4`, `bc3Red4`) described accurately as byte patterns, not as colors that the test verifies?
- Is the 1D vs 2D secondary axis described at the right depth, or does it need its own behavior-parameter subsection?
- Is the `MUTABLE_FORMAT_BIT` for the uncompressed pair correctly attributed to the format-difference check at line 91, given that `formatsAreCompatible()` returns true (same texel size) but the format strings differ?

All audit questions above are resolved by direct source inspection:

- The core purpose is confirmed by `iterate()` recording `vkCmdCopyImage` and then sampling via `texelFetch` through the view.
- The asymmetric verification is confirmed by the `srcCompressed` branch in `iterate()` and the dispatch of `compVerify` for compressed cases.
- The bit patterns are confirmed by the constants in `initPrograms()` and the `imageStore`/`imageLoad` calls.
- The 1D/2D secondary axis is confirmed by the `imageTypes` array and the `if (m_params.src.image.imageType != vk::VK_IMAGE_TYPE_1D)` block scaling `srcOffset.y` and `extent.height`.
- The `MUTABLE_FORMAT_BIT` attribution is confirmed by line 91 (`if (m_params.src.image.format != m_viewFormat)`), which fires for the uncompressed pair because the format strings differ even though texel sizes match.

No unresolved risk points remain that affect final page semantics, representative walkthrough selection, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- The brief's `Background Knowledge` should distill into a concise Level-3 BGK list with three bullets: size-compatible format copying, block-texel-view-compatible compressed images, and the 1D exception for compressed-format copy regions. The "why it matters here" notes are scaffolding and should be removed.
- The concrete example of `2d.copy_bc1_rgb_unorm_block_sample_r32g32_uint` is the most efficient mental model and should be referenced briefly in `## Behavior Parameters` for the BC1 leaf rather than reproduced as a long example.
- The end-to-end flow can be condensed into `## Runtime Execution and Result Checking` prose without the `[host]`/`[device]` markers, since the Level-3 template prefers unordered lists there.
- The resource table should be preserved in `## Runtime Execution and Result Checking` or `## Parameter Dimensions and Observed Values` as a compact reference; only the most important resources need to be listed.
- The `### Failure Cause Mapping` table from `## What Failure Means` is copied directly into the final page's `### Failure Cause Mapping`. The `### Cause Analysis` is written fresh during the rewrite.
- The `## Behavior Parameter Identification` conclusion (test case leaf = format pair, three values, with 1d/2d as secondary axis) is carried into `## Behavior Parameters` with one `###` subsection per format pair leaf.
- No shader walkthrough is needed; shaders are verification infrastructure and not the tested behavior.
- The Vulkan spec concepts grounding the failure causes (memcpy semantics, `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT`, `EXTENDED_USAGE_BIT`, 1D VUIDs) should be referenced concisely in `### Cause Analysis` rather than re-explained as background.
