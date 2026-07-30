# Understanding Brief: `use_after_copy` test family

## One-Sentence Test Purpose

This test checks whether an image that has just received data via a copy command can be consumed correctly through a later graphics pass, validating that the copy, layout transition, queue ownership handoff, and post-copy usage path together preserve the intended pixel or depth values.

## Background Knowledge

The `external/vulkan-docs/src/chapters/` directory is not present in this checkout, so the conceptual grounding below relies on the Vulkan 1.x spec semantics summarized in the source comments and on standard Vulkan copy/queue-ownership rules.

### Image layout transitions around copies

A Vulkan image must sit in a layout compatible with the operation that accesses it. Copy commands that write to an image require `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`; sampling the same image later requires `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`, and using it as a depth/stencil attachment requires `VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL`. The transition between layouts is recorded as a `VkImageMemoryBarrier` with matching src/dst access masks and pipeline stages, and the implementation must ensure prior writes are made available before later reads occur. This test exercises that transition explicitly after every copy, so a missing or mistimed barrier is observable as stale or corrupted data in the consuming pass.

### Queue family ownership transfer

When the queue that performs the copy differs from the queue that consumes the image, the image's queue family ownership must be transferred with a barrier pair: a release barrier on the source queue and an acquire barrier on the destination queue. Both barriers carry `srcQueueFamilyIndex` and `dstQueueFamilyIndex`. Without a correct release/acquire pair, the destination queue may observe uninitialized memory, stale cache lines, or a layout mismatch. This test deliberately uses universal, compute-only, and transfer-only queue selections in [`AfterUsageParams::getQueueFamilyIndex()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L181-L192) so that queue-switch paths are first-class coverage.

### Copy command variants exercised

Three copy entry points reach the destination image: `vkCmdCopyBufferToImage` for the classic buffer-to-image path, `vkCmdCopyImage` for the image-to-image path that first stages data into an auxiliary image, and `vkCmdCopyMemoryToImageIndirectKHR` for the `VK_KHR_copy_memory_indirect` path used by the `copy_memory_indirect.use_after_copy` sibling root. All three must leave the destination image with byte-equivalent contents for the same source data; the test consumes the result identically regardless of which copy command produced it.

### sRGB semantics in copy-then-sample

When an sRGB-format image receives data via `vkCmdCopyBufferToImage`, the bytes are copied with memcpy semantics and the implementation treats them as already-encoded sRGB. Sampling that image in a shader returns linear-space values because the sampler decodes sRGB on read. When the multisample fill path is used instead (a fragment shader writes the auxiliary attachment from a storage buffer), the source values are interpreted as linear and converted to sRGB on store. The host reference must replicate these conversions or the comparison fails for non-bug reasons.

## One Concrete Example

Take `dEQP-VK.api.copy_and_blit.core.use_after_copy.r8g8b8a8_unorm.transfer_dst_optimal.32x32x1`. The host creates a 32×32 `VK_FORMAT_R8G8B8A8_UNORM` image with `TRANSFER_SRC_BIT | TRANSFER_DST_BIT | SAMPLED_BIT` usage, fills a host-visible buffer with random `tcu::Vec4` color values, and records `vkCmdCopyBufferToImage` into the image at `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`. A release barrier transitions the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` and submits on the universal queue. A second command buffer binds the image as a `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER` with nearest filtering, runs a fragment shader that performs `texelFetch(tex, ivec2(gl_FragCoord.xy), 0)` into a `VK_FORMAT_R32G32B32A32_SFLOAT` color attachment, and copies the attachment back to a buffer. The host maps the buffer and compares it against the original color texture with a small UNORM-derived threshold via `tcu::floatThresholdCompare()`. The test passes only if the sampled framebuffer matches the source colors within tolerance.

## End-to-End Test Flow

```text
[host] choose format, transfer layout, queue, copy coverage, 3D image/view,
       color attachment flag, image-to-image flag, linear tiling, sample count
[host] create destination image with usage bits covering both transfer and
       post-copy consumption (sampled or depth/stencil attachment)
[host] create color attachment image (R32G32B32A32_SFLOAT) used as verification target
[host] generate source data: depth values (16-bit, format-converted) for DS cases
       or random colors for color cases
[host] fill vertex buffer with one point per pixel per layer, depth set per point
[host] fill source memory buffer with depth bytes or color texels
[host] record clear command buffer (when partial copies or colorAttFlag)
[host] record transfer command buffer: initial layout barrier, optional clear,
       copy command (classic / image-to-image / indirect)
[host] record release barrier if queue switch, transitioning to useLayout
[host] record graphics command buffer: acquire barrier if queue switch,
       clear color attachment, begin render pass, draw points per layer,
       end render pass, copy color attachment to host-visible buffer
[host] submit clear, transfer, graphics command buffers in order with semaphores
[host] wait on fence, invalidate color buffer allocation
[host] synthesize reference image: clear color outside copied regions,
       depth-derived blue/black for DS, source texels (with sRGB conversion
       for non-MSAA sRGB color) inside copied regions
[host] compare reference vs. result per layer with format-aware threshold
[host] pass only if all layers match within threshold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL vertex shader (`vert-spv10` / `vert-spv15`) that places one point per pixel and uses `gl_InstanceIndex` for layer selection; the SPV_1_5 variant enables `GL_ARB_shader_viewport_layer_array` so `gl_Layer` can be set in the vertex shader for multi-slice cases.
- Inline GLSL fill vertex shader (`vert-fill-spv10` / `vert-fill-spv15`) that emits a full-screen triangle strip for the multisample fill pass.
- Inline GLSL fragment shader (`frag`) that either `texelFetch`es from the copied texture (color cases) or writes a constant blue color (DS cases). The sampler type is chosen dynamically from `viewIs3D`, `multiSlice`, and `isMS`: `sampler2D`, `sampler2DArray`, `sampler3D`, `sampler2DMS`, or `sampler2DMSArray`.
- Inline GLSL fill fragment shader (`frag-fill`) that reads per-pixel-per-sample values from a storage buffer and writes them to a color or depth attachment, used to populate the auxiliary multisample image.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Destination image (copied-then-consumed) | yes, via `AfterUsageParams::getImageCreateInfo()` | yes, image view bound as sampled or DS attachment | written by copy command, read by later graphics pass | no | the central object under test |
| Source memory buffer | yes, host-filled with depth bytes or color texels | yes, transfer src + device address | read by copy command | no | provides the ground-truth data |
| Vertex buffer | yes, host-filled with per-pixel point positions and depths | yes, vertex buffer binding | read by vertex shader | no | drives point rendering |
| Color attachment image (`R32G32B32A32_SFLOAT`) | yes, via `AfterUsageParams::getColorAttCreateInfo()` | yes, color attachment in render pass | written by fragment shader, may be resolve target | yes, via `ImageWithBuffer` | records the consumed copy result for verification |
| Multisample color attachment (when `sampleCount > 1`) | yes, only in MSAA paths | yes, color attachment | written by fill pipeline, read by resolve | no | holds per-sample values before resolve |
| Auxiliary image (when `imageToImage`) | yes, via `AfterUsageParams::getAuxiliarImageCreateInfo()` | yes, transfer src | written by buffer-to-image copy or fill pipeline, read by image-to-image copy | no | stages source data so it can be `vkCmdCopyImage`'d into the destination |
| Indirect command buffer (when `indirect`) | yes, host-filled `VkCopyMemoryToImageIndirectCommandKHR` records | yes, indirect buffer + device address | read by `vkCmdCopyMemoryToImageIndirectKHR` | no | drives the indirect copy path |
| Descriptor set with combined image sampler | yes, only for color cases | yes, fragment shader binding | read by fragment shader | no | connects copied image to the consuming shader |
| Fill descriptor set with storage buffer | yes, only for MSAA fill pass | yes, fragment shader binding | read by fill fragment shader | no | provides per-sample source values during auxiliary image fill |
| Push constants for fill pipeline | yes, width/height as `tcu::Vec2` | yes, push constant range | read by fill fragment shader | no | lets the fill shader compute per-layer pixel indices |

## What Is Checked

- The framebuffer color attachment is the only host-read-back verification target. It is compared per layer against a CPU-synthesized reference using `tcu::floatThresholdCompare()`.
- For depth/stencil cases, the reference encodes `geomColor` (blue) where the point depth is less than the copied depth-buffer value, and `clearColor` (black) elsewhere. The threshold is zero because the result is exact blue or black.
- For color cases, the reference encodes the original source texel for each pixel inside the copied region and `clearColor` outside it. The threshold is format-aware via `getColorFormatThreshold()` for UNORM and SFLOAT color formats, with extra slack for sRGB.
- Outside partial-copy regions, the reference stays at `clearColor`, so preserved clear values are checked alongside copied values.
- Each layer is compared independently. Any failing layer fails the whole test.

## Behavior Parameter Identification

> **Behavior parameter:** post-copy consumption route (behavioral group derived from the format child)
>
> **Candidate values:** `color-sampled`, `depth/stencil-attachment`

The direct children under `use_after_copy` are format names. Those formats cluster into two behavioral groups with distinct validation oracles: color formats are sampled in a fragment shader and compared against the source texture, while depth/stencil formats are bound as a depth/stencil attachment and validated indirectly through which pixels pass the depth test. All other parameter dimensions (transfer layout, queue, copy coverage, 3D image/view, color attachment flag, image-to-image, linear tiling, sample count) are secondary axes that modify execution within each behavioral group.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color-sampled` | Copied texel bytes do not match source (copy corruption, region translation, sRGB mishandling, linear-tiling layout mismatch); post-copy layout transition missing or wrong (transfer_dst/general → shader_read_only); queue ownership release/acquire missing or mistimed; sampler or descriptor view mismatch; color compression artifacts after copy when `colorAttFlag` is set; sRGB-to-linear host reference does not match device-side sampling semantics (especially non-MSAA vs MSAA paths). |
| `depth/stencil-attachment` | Copied depth value does not match source (16→24→32 format conversion error, depth aspect layout mismatch, stencil aspect ignored); post-copy layout transition missing or wrong (transfer_dst/general → depth_stencil_attachment); queue ownership release/acquire missing or mistimed; depth test compare op or depth bounds misconfigured; depth written but not made available to early/late fragment tests; classic buffer-to-image depth copy on compute or transfer queue missing `VK_KHR_maintenance10` or required `VK_FORMAT_FEATURE_2_DEPTH_COPY_*` flag. |
| shared (both groups) | Indirect-copy stride or device address wrong; image-to-image auxiliary image layout or region translation wrong; 3D image / 2D-array-compatible view / 3D view layout or aspect mismatch; partial-copy region construction produces wrong offset or extent; transfer queue granularity check rejected a case that should have run; multisample fill pipeline writes wrong sample indices; host reference synthesis uses wrong pixel-to-layer mapping. |

## Important Variations and Special Cases

- **`indirect` flag** distinguishes the two registered roots: `core.use_after_copy` uses `indirect=false` (classic `vkCmdCopyBufferToImage` and `vkCmdCopyImage`), while `copy_memory_indirect.use_after_copy` uses `indirect=true` (`vkCmdCopyMemoryToImageIndirectKHR` from `VK_KHR_copy_memory_indirect`). Indirect DS copies are constrained to the universal queue per the cited VUID.
- **`colorAttFlag`** adds `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` to the copied color image and scales the image to 1024×1024 to make some drivers enable color compression, which can expose post-copy decompression problems. This flag is only kept for color formats with `transfer_dst_optimal` layout and non-3D views.
- **`imageToImage`** stages source data in an auxiliary image and then uses `vkCmdCopyImage` instead of `vkCmdCopyBufferToImage`. For multisample cases, the auxiliary image is filled by a fragment-shader pipeline because direct buffer-to-multisample-image copies are not available. `imageToImage` requires `layerCount > 1` and is incompatible with `indirect` and `use3DImage`.
- **`linear` tiling** is limited to `VK_FORMAT_R32G32B32_SFLOAT` in the generator, since some implementations only support that format for linear tiling.
- **3D image / 3D view** uses `VK_IMAGE_TYPE_3D` for the destination image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` or `VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT`, and is only exercised for color formats. DS cases skip 3D images entirely because depth/stencil attachments cannot be 3D.
- **Multisample (`_msaa`)** is only generated when `imageToImage` is true, and the comparison logic skips sRGB-to-linear conversion in that case because the fill pipeline already stored values as linear.
- **Transfer queue** uses a 64×64 base extent (instead of 32×32) to help partial-copy regions meet transfer queue granularity requirements on more implementations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `AfterUsageParams` struct and image create info | [`vktApiUseAfterCopyTests.cpp#L39-L216`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L39-L216) | Defines every parameter axis and the destination image usage bits that bind copy and post-copy consumption. |
| `AfterUsageCase::checkSupport()` | [`vktApiUseAfterCopyTests.cpp#L253-L397`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L253-L397) | Runtime support gate: indirect copy features, maintenance1/10, image 2D view of 3D, transfer queue granularity, format properties. |
| `AfterUsageCase::initPrograms()` | [`vktApiUseAfterCopyTests.cpp#L399-L496`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L399-L496) | Generates the vertex, fill vertex, fragment, and fill fragment shaders; sampler type is chosen here. |
| `getColorFormatThreshold()` and `bitWidthToThreshold()` | [`vktApiUseAfterCopyTests.cpp#L498-L540`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L498-L540) | Format-aware comparison threshold for color cases. |
| `AfterUsageInstance::iterate()` copy and queue setup | [`vktApiUseAfterCopyTests.cpp#L636-L1379`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L636-L1379) | Host-side flow: barriers, copy command selection, queue ownership transfer, render pass, draw, copyback. |
| Reference image synthesis and thresholded compare | [`vktApiUseAfterCopyTests.cpp#L1622-L1711`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1622-L1711) | CPU oracle for color and DS cases, including sRGB handling notes and per-layer `tcu::floatThresholdCompare()`. |
| `createUseAfterXferGroup()` generator | [`vktApiUseAfterCopyTests.cpp#L1716-L1958`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1716-L1958) | Test matrix generation: format list, layout loop, queue loop, copy coverage, 3D image/view, color attachment flag, image-to-image, linear tiling, multisample, name suffixes. |
| Parent registration under `core` | [`vktApiCopiesAndBlittingTests.cpp#L232-L239`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L239) | Registers `use_after_copy` under `api.copy_and_blit.core` with `indirect=false`. |
| Parent registration under `copy_memory_indirect` | [`vktApiCopyMemoryIndirectTests.cpp#L2338`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) | Registers `use_after_copy` under `api.copy_and_blit.copy_memory_indirect` with `indirect=true`. |

## Questions / Risk Points for User Audit

- Is the dual-root scope (`core` and `copy_memory_indirect`) correct for this single Level-3 page, or should the page only cover `core` and leave `copy_memory_indirect` to a separate page?
- Is "post-copy consumption route" (color-sampled vs. depth/stencil-attachment) the right primary behavioral axis, or should the format dimension itself be treated as the axis?
- Are the failure causes for depth/stencil cases specific enough? The depth-test-driven oracle makes symptoms indirect; source-level investigation may be needed for any cause that is not directly observable in the source.
- Are there parameter dimensions missing from the failure cause mapping that should be elevated (for example, queue selection as a separate axis rather than a modifier)?

## Conversion Notes for Final Wiki Rewrite

- Carry `## Behavior Parameter Identification` and `### Failure Cause Mapping` directly into the final page's `## Behavior Parameters` and `### Failure Cause Mapping`.
- Distill the BGK into a short bullet list: layout transitions, queue ownership transfer, copy command variants, and sRGB semantics. The full teaching scaffolding stays in the brief only.
- Keep the dual-root registration tree visible in `## Registration Hierarchy` with a one-line structural note explaining the shared implementation entry point.
- Move the source-mapping table to the Source Reference Appendix unchanged.
- Write `### Cause Analysis` fresh, with `####` subsections per cause named in the mapping table, using the bold `**Possible failure symptoms:**` and `**Possible implementation causes:**` lead-in labels.
- Treat shaders as test infrastructure in `## Shader Analysis` and skip walkthroughs per Phase 5 of the wiki-rewriter workflow.
