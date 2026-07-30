# Understanding Brief: `image_to_image` test family

## One-Sentence Test Purpose

This test checks whether `vkCmdCopyImage` and `vkCmdCopyImage2` copy texels between source and destination images with the exact bytes the Vulkan `VkImageCopy` layout specifies, across format-compatibility pairs, image dimensionalities (1D/2D/3D/cube/array), compressed-format block scaling, layout transitions, queue families, allocation kinds, and sparse binding.

## Background Knowledge

### Size-compatible format copying

Vulkan allows `vkCmdCopyImage` between formats that share the same texel block size in bytes (for example `VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R32_SFLOAT`, both 32 bits per texel). For compressed formats, the rule is the same: a compressed source may copy into an uncompressed destination whose texel size equals the compressed block size, or into another compressed format with an identical block footprint. The CTS source iterates over `formats::compatibleFormats8Bit` … `compatibleFormats256Bit` arrays to enumerate every legal pair ([`vktApiCopyImageToImageTests.cpp#L1525-L1536`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1525-L1536)).

Why it matters here:

- The test deliberately pairs formats that have the same byte width but different channel layouts (for example `R8G8B8A8_UNORM` with `R32_SFLOAT`). A driver that reinterprets the bytes rather than memcpying them will fail.
- The host reference computation uses `tcu::PixelBufferAccess` with the *source* format applied to the destination buffer, which is the host-side analogue of the spec's "CopyImage acts like a memcpy" rule ([`vktApiCopyImageToImageTests.cpp#L503-L513`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L503-L513)).

### Compressed-format block-size scaling

For compressed formats (BC, ETC2, ASTC, etc.), `VkExtent3D` and `VkOffset3D` in `VkImageCopy` are measured in texels, not blocks. The CTS test parameters are authored in block units, then `iterate()` multiplies offsets and extents by `getBlockWidth` / `getBlockHeight` / `getBlockDepth` before recording the copy, with 1D and 3D image-type exceptions matching VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152 ([`vktApiCopyImageToImageTests.cpp#L208-L247`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L208-L247)).

Why it matters here:

- The host reference also walks the destination in source-format texel units through `getSizeCompatibleTcuTextureFormat()`, which maps every compressed format to either `R16G16B16A16_UINT` (8-byte block) or `R32G32B32A32_UINT` (16-byte block) ([`vktApiCopiesAndBlittingUtil.cpp#L170-L177`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L170-L177)).
- A driver that interprets the extent in block units instead of texel units, or that mishandles the 1D/3D exceptions, will fail compressed-format copies while passing uncompressed ones.

### Image layout transitions around the copy

`vkCmdCopyImage` requires the source image to be in `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`, and the destination in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`. The test records a `VK_PIPELINE_STAGE_TRANSFER_BIT` → `VK_PIPELINE_STAGE_TRANSFER_BIT` pipeline barrier with `VK_ACCESS_TRANSFER_WRITE_BIT` → `VK_ACCESS_TRANSFER_READ_BIT` on the source and `VK_ACCESS_TRANSFER_WRITE_BIT` → `VK_ACCESS_TRANSFER_WRITE_BIT` on the destination, transitioning both images from `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (the layout `uploadImage` leaves them in) to `m_params.src.image.operationLayout` / `m_params.dst.image.operationLayout` ([`vktApiCopyImageToImageTests.cpp#L260-L304`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L260-L304)).

When `m_params.useGeneralLayout` is set, the test substitutes memory barriers for image-memory barriers and uses `VK_IMAGE_LAYOUT_GENERAL` everywhere, exercising the general-layout copy path. When `m_params.clearDestinationWithRed` is set, a `vkCmdClearColorImage` to red is inserted between two pipeline barriers so that out-of-bounds writes by the copy are detectable as surviving red texels.

Why it matters here:

- The `useGeneralLayout` variant is registered as a separate sibling family (`image_to_image_general_layout`) and exercises a separate driver path.
- The `clearDestinationWithRed` mechanism is only used in `simple_tests` `partial_image_*_clear` leaves; a driver that writes outside the requested region will leave red texels in the read-back image.

### Depth/stencil aspect separation

For combined depth/stencil formats (`VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT`, etc.), `vkCmdCopyImage` requires each `VkImageCopy` region to specify exactly one aspect through `imageSubresource.aspectMask` — either `VK_IMAGE_ASPECT_DEPTH_BIT` or `VK_IMAGE_ASPECT_STENCIL_BIT`. The test's `all_formats.depth_stencil` subgroup iterates over `formats::depthAndStencilFormats` and emits separate depth and stencil copy regions for combined formats, with optional `VK_KHR_separate_depth_stencil_layouts` (`SEPARATE_DEPTH_STENCIL_LAYOUT` extension flag) variants marked `_separate_layouts` ([`vktApiCopyImageToImageTests.cpp#L2300-L3158`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2300-L3158)).

Why it matters here:

- The host reference computation in `copyRegionToTextureLevel` walks depth and stencil aspects separately through `tcu::getEffectiveDepthStencilAccess` ([`vktApiCopyImageToImageTests.cpp#L470-L501`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L470-L501)).
- The result checker uses `tcu::floatThresholdCompare` for floating-point depth, `tcu::intThresholdCompare` for integer depth/stencil, and `tcu::bitwiseCompare` for non-depth/stencil formats, all with zero threshold ([`vktApiCopyImageToImageTests.cpp#L390-L447`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L390-L447)).

## One Concrete Example

Take `dEQP-VK.api.copy_and_blit.core.image_to_image.simple_tests.partial_image_pot_diff_format_clear` as a concrete case. Reconstructed from the registration loop in `addImageToImageSimpleTests`:

```text
Source image:       VK_IMAGE_TYPE_2D, VK_FORMAT_R32_UINT, 64x64, OPTIMAL tiling
Destination image:  VK_IMAGE_TYPE_2D, VK_FORMAT_R8G8B8A8_UNORM, 64x64, OPTIMAL tiling
Src layout:         VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL
Dst layout:         VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
clearDestinationWithRed: true
Single region:
    srcOffset = (16, 16, 0)
    dstOffset = (0, 0, 0)
    extent    = (32, 32, 1)
```

The host fills the source with a gradient and the destination with a different gradient, then `uploadImage` transitions both into `TRANSFER_DST_OPTIMAL`. The test then records: a pipeline barrier to move the source into `TRANSFER_SRC_OPTIMAL` and the destination into `TRANSFER_DST_OPTIMAL`; a `vkCmdClearColorImage` to clear the destination to vec4(1.0, 0.0, 0.0, 1.0); a second pipeline barrier to make that write visible to the next transfer; the `vkCmdCopyImage` with the single region; and a final implicit transition on submit. The host reads the destination back, computes the expected texture level by copying the source subregion into a destination-sized buffer with the source format applied to the destination, and bit-exactly compares. Any texel outside the (0,0)-(32,32) subregion must still be red; any texel inside must match the source's `R32_UINT` bytes reinterpreted as `R8G8B8A8_UNORM`.

## End-to-End Test Flow

```text
[host] choose test parameters from the subgroup (simple_tests, all_formats, 3d_images, dimensions, cube, array, or misc)
[host] create source VkImage (TRANSFER_SRC|TRANSFER_DST usage; sparse flags when useSparseBinding)
[host] create destination VkImage (TRANSFER_SRC|TRANSFER_DST usage; never sparse)
[host] fill host-side source TextureLevel via generateBuffer with the subgroup's fill mode
[host] fill host-side destination TextureLevel via generateBuffer (or FILL_MODE_RED when clearDestinationWithRed)
[host] generate expected TextureLevel by copying regions into the destination via copyRegionToTextureLevel
[host] uploadImage source and destination (transitions both to TRANSFER_DST_OPTIMAL, or GENERAL when useGeneralLayout)
[host] record pipeline barrier: src TRANSFER_DST_OPTIMAL -> operationLayout, dst TRANSFER_DST_OPTIMAL -> operationLayout
[host] if clearDestinationWithRed: vkCmdClearColorImage to red, then second pipeline barrier
[host] for each VkImageCopy region: scale offsets/extents by compressed block dimensions when src or dst is compressed
[host] dispatch vkCmdCopyImage (default) or vkCmdCopyImage2 (COPY_COMMANDS_2) with the regions
[host] end command buffer; if useSecondaryCmdBuffer, execute secondary inside primary
[host] submitCommandsAndWaitWithTransferSync (includes sparse semaphore when useSparseBinding)
[host] readImage destination back into a TextureLevel
[host] checkTestResult: bitwiseCompare for color, floatThresholdCompare for depth, intThresholdCompare for stencil, zero threshold
[host] report pass/fail
```

For the `misc.ms_then_ss*` leaves the flow is different: the host clears MS and SS image pairs on the universal queue, copies MS-src to MS-dst and SS-src to SS-dst on the transfer queue (with an optional barrier stage variant between the two copies), resolves MS-dst to an extra SS image on the universal queue, copies both SS images to buffers, and float-compares against the expected clear colors.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- No GLSL, SPIR-V, HLSL, or Amber artifacts. All work is recorded through `vkCmdCopyImage` / `vkCmdCopyImage2` / `vkCmdClearColorImage` / `vkCmdResolveImage2`.
- The randomized test case matrix is generated at registration time by the `addImageToImage*Tests` functions, enumerating format pairs, image types, extents, tilings, layouts, queue families, allocation kinds, and sparse flags.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source `VkImage` | Yes | Yes (transfer source) | Read by `vkCmdCopyImage` | No | Holds the source texels. Sparse-binding variant uses `VK_IMAGE_CREATE_SPARSE_BINDING_BIT \| VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and `allocateAndBindSparseImage`. |
| Destination `VkImage` | Yes | Yes (transfer destination) | Written by `vkCmdCopyImage` (and by `vkCmdClearColorImage` when `clearDestinationWithRed`) | Yes, via `readImage` | Receives the copied texels; compared against the expected texture level. |
| Expected `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the comparison reference | Host-computed oracle produced by `copyRegionToTextureLevel`. |
| Sparse semaphore | Yes, when `useSparseBinding` | Yes | No | No | Passed to `submitCommandsAndWaitWithTransferSync` so sparse memory binding completes before the copy executes. |
| Secondary command buffer | Yes, when `useSecondaryCmdBuffer` | Yes | No | No | Records the copy; executed by the primary command buffer via `vkCmdExecuteCommands`. |

## What Is Checked

- Bit-exact comparison for non-depth/stencil formats via `tcu::bitwiseCompare` with zero threshold. The host reference uses the source format applied to the destination buffer to mimic the spec's "memcpy" semantics for size-compatible formats.
- Float threshold comparison for depth components via `tcu::floatThresholdCompare` with zero threshold.
- Integer threshold comparison for stencil components via `tcu::intThresholdCompare` with zero threshold.
- For `clearDestinationWithRed` leaves, untouched destination texels must remain red; this is checked implicitly because the host reference also keeps the red fill outside the copied region.
- For `misc.ms_then_ss*` leaves, the MS-resolved extra image must match the MS source clear color, and the SS destination must match the SS source clear color, both via `tcu::floatThresholdCompare` with zero threshold.
- The check is per-case. Each test case leaf produces one pass/fail verdict.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node (the subgroup directly under `image_to_image`)
>
> **Candidate values:** `simple_tests`, `all_formats` (with `color` and `depth_stencil` sub-subgroups), `3d_images`, `dimensions`, `cube`, `array`, `misc` (TransferOnly only)

A secondary behavioral axis is the registration context (the parent group and sibling-family suffix), which varies queue family, allocation kind, command variant, sparse binding, secondary command buffer, and general-layout usage:

> **Secondary axis:** registration context
>
> **Candidate values:** `core.image_to_image`, `core.image_to_image_general_layout`, `dedicated_allocation.image_to_image`, `copy_commands2.image_to_image`, `copy_commands2.image_to_image_transfer_queue`, `copy_commands2.image_to_image_transfer_queue_secondary`, `copy_commands2.image_to_image_transfer_sparse`, `sparse.image_to_image`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `simple_tests` (whole/partial/depth/stencil/diff_format/clear leaves) | Basic `vkCmdCopyImage` mechanics, region offset/extent handling, depth/stencil aspect separation, or `clearDestinationWithRed` out-of-bounds detection. |
| `all_formats.color.*` | Size-compatible format pair handling, byte-reinterpretation for same-width different-channel-layout pairs, or compressed-format block-size scaling. |
| `all_formats.depth_stencil.*` | Depth/stencil aspect separation across image types, separate depth/stencil layout transitions (`_separate_layouts`), or per-aspect offset computation. |
| `3d_images` | 3D-slice ↔ 2D-layer mapping, `srcOffset.z` / `dstOffset.z` handling, or `VkImageSubresourceLayers.baseArrayLayer` ↔ 3D depth coordinate translation. |
| `dimensions` | Large or non-power-of-two image dimensions, dimension-dependent format-property reporting, or layout-pair iteration. |
| `cube` | `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` handling, cube-face ↔ array-layer mapping, or whole-cube vs per-face copy. |
| `array` | 2D-array layer copies, `VK_REMAINING_ARRAY_LAYERS` resolution (`VK_KHR_maintenance5`), or mipmap-level iteration (`CopyImageToImageMipmap`). |
| `misc` (TransferOnly only) | Multi-sample then single-sample copy interaction on the transfer queue, optional inter-copy barrier stage handling. |
| All subgroups under `copy_commands2.*` variants | `vkCmdCopyImage2KHR` struct conversion or dispatch. |
| All subgroups under `*_transfer_queue*` variants | Transfer-only queue execution, `minImageTransferGranularity` validation, or queue-family routing. |
| All subgroups under `core.image_to_image_general_layout` | `VK_IMAGE_LAYOUT_GENERAL` as the copy layout instead of `TRANSFER_*_OPTIMAL`, and memory-barrier substitution for image-memory barriers. |
| All subgroups under `dedicated_allocation.*` | Dedicated-allocation memory binding for source or destination image. |
| All subgroups under `sparse.image_to_image` and `copy_commands2.image_to_image_transfer_sparse` | Sparse image memory binding, sparse residency, or sparse semaphore synchronization. |

### Cause Analysis

Detailed `### Cause Analysis` is written fresh during the final Level-3 rewrite. The brief only names the causes above so the mapping can be carried directly into the final page.

## Important Variations and Special Cases

- **`simple_tests` depth and stencil leaves.** `depth` uses `VK_FORMAT_D32_SFLOAT` with `VK_IMAGE_ASPECT_DEPTH_BIT`; `stencil` uses `VK_FORMAT_S8_UINT` with `VK_IMAGE_ASPECT_STENCIL_BIT`. These are not combined depth/stencil formats — they are single-aspect formats that exercise the depth-only and stencil-only copy paths without the combined-format aspect separation logic.
- **`all_formats` sparse pruning.** `addCopyImageToImageTests` skips `all_formats` and `dimensions` when `useSparseBinding` is set ([`vktApiCopyImageToImageTests.cpp#L4443-L4447`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4443-L4447)). The sparse variants therefore exercise a smaller subgroup set.
- **`misc` registration gating.** `misc` is only registered when `queueSelection == TransferOnly` ([`vktApiCopyImageToImageTests.cpp#L4450-L4453`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4450-L4453)), and its mustpass paths live under `copy_commands2.image_to_image_transfer_queue.misc` rather than under `core.image_to_image.misc`.
- **`array_to_array_whole_mipmap_*` leaves.** These use the separate `CopyImageToImageMipmap` test instance and `CopyImageToImageMipmapTestCase`, not `CopyImageToImage`. The mipmap instance iterates over all mip levels in one command buffer, with one `VkImageCopy` region per mip level, and the destination is pre-filled with `FILL_MODE_RED` to detect missing mip writes.
- **`VK_REMAINING_ARRAY_LAYERS` in `array`.** `array_to_array_whole_remaining_layers` and `array_to_array_partial_remaining_layers` set `imageSubresource.layerCount = VK_REMAINING_ARRAY_LAYERS` and add `MAINTENANCE_5` to `extensionFlags`, gated by `VK_KHR_maintenance5` in `checkSupport`.
- **`useGeneralLayout` barrier substitution.** When `useGeneralLayout` is set, the test substitutes `VkMemoryBarrier` for `VkImageMemoryBarrier` and uses `VK_IMAGE_LAYOUT_GENERAL` for both the source and destination. This exercises a different driver path because the implementation must accept `GENERAL` as the copy layout.
- **`useSecondaryCmdBuffer` path.** Only registered for `copy_commands2.image_to_image_transfer_queue_secondary`. The copy is recorded into a secondary command buffer, which the primary command buffer executes via `vkCmdExecuteCommands`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CopyImageToImage` test instance class | [`vktApiCopyImageToImageTests.cpp#L59-L75`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L59-L75) | Owns source image, destination image, sparse allocations, and the `iterate()` entry point. |
| `CopyImageToImage::iterate()` | [`vktApiCopyImageToImageTests.cpp#L168-L388`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L168-L388) | Fills images, records barriers and copy command, submits, reads back, and checks the result. |
| `CopyImageToImage::checkTestResult()` | [`vktApiCopyImageToImageTests.cpp#L390-L447`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L390-L447) | Bit-exact, float-threshold, or int-threshold comparison with zero threshold. |
| `CopyImageToImage::copyRegionToTextureLevel()` | [`vktApiCopyImageToImageTests.cpp#L449-L514`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L449-L514) | Host-side reference computation; uses source format on destination buffer to mimic memcpy semantics. |
| `CopyImageToImageTestCase::checkSupport()` | [`vktApiCopyImageToImageTests.cpp#L530-L628`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L530-L628) | Gates extensions, transfer queue granularity, format support, and image dimension limits. |
| `CopyImageToImageMipmap` class | [`vktApiCopyImageToImageTests.cpp#L634-L1054`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L634-L1054) | Separate instance for `array_to_array_whole_mipmap_*` leaves; iterates over all mip levels. |
| `addImageToImageSimpleTests()` | [`vktApiCopyImageToImageTests.cpp#L1151-L1448`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1151-L1448) | Registers `simple_tests` leaves including depth, stencil, diff_format, and clear variants. |
| `addImageToImageAllFormatsColorTests()` | [`vktApiCopyImageToImageTests.cpp#L1580-L2140`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1580-L2140) | Registers `all_formats.color` leaves across all 1d/2d/3d ↔ 1d/2d/3d pairs. |
| `addImageToImageAllFormatsDepthStencilTests()` | [`vktApiCopyImageToImageTests.cpp#L2300-L3158`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2300-L3158) | Registers `all_formats.depth_stencil` leaves with optional `_separate_layouts` variants. |
| `addImageToImage3dImagesTests()` | [`vktApiCopyImageToImageTests.cpp#L3167-L3479`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3167-L3479) | Registers `3d_images` leaves: 3d_to_2d_by_slices, 2d_to_3d_by_layers, 3d_to_2d_whole, 2d_to_3d_whole, and regions variants. |
| `addImageToImageDimensionsTests()` | [`vktApiCopyImageToImageTests.cpp#L2141-L2298`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2141-L2298) | Registers `dimensions` leaves across large-POT/small-POT, large-POT/small-NPOT, etc. dimension combinations. |
| `addImageToImageCubeTests()` | [`vktApiCopyImageToImageTests.cpp#L3486-L3816`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3486-L3816) | Registers `cube` leaves: cube_to_array_layers, cube_to_array_whole, array_to_cube_layers, array_to_cube_whole, cube_to_cube_layers, cube_to_cube_whole. |
| `addImageToImageArrayTests()` | [`vktApiCopyImageToImageTests.cpp#L3818-L4115`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3818-L4115) | Registers `array` leaves including `array_to_array_whole_remaining_layers` (MAINTENANCE_5) and `array_to_array_whole_mipmap_*` (mipmap instance). |
| `addImageToImageMiscTests()` | [`vktApiCopyImageToImageTests.cpp#L4413-L4436`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4413-L4436) | Registers `misc.ms_then_ss*` leaves; TransferOnly only. |
| `multiSampleThenSingleSampleTest()` | [`vktApiCopyImageToImageTests.cpp#L4144-L4411`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4144-L4411) | The misc test body: clears MS+SS image pairs on universal queue, copies both on transfer queue, resolves MS to SS, copies SS to buffers, and compares. |
| `addCopyImageToImageTests()` | [`vktApiCopyImageToImageTests.cpp#L4440-L4454`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4440-L4454) | Public entry point that adds the six subgroups (plus conditional `misc`). |
| `addCopyImageToImageTestsSimpleOnly()` | [`vktApiCopyImageToImageTests.cpp#L4456-L4459`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4456-L4459) | Adds only `simple_tests`; used for `general_layout`, `transfer_queue_secondary`, and `transfer_sparse` variants. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L70-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L70-L230) | Routes `image_to_image` into `core`, `dedicated_allocation`, `copy_commands2`, and `sparse` parents; registers `image_to_image_general_layout`, `image_to_image_transfer_queue`, `image_to_image_transfer_queue_secondary`, and `image_to_image_transfer_sparse` siblings. |
| `getSizeCompatibleTcuTextureFormat()` | [`vktApiCopiesAndBlittingUtil.cpp#L170-L177`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L170-L177) | Maps compressed formats to size-compatible uncompressed tcu formats for host reference. |
| `checkExtensionSupport()` | [`vktApiCopiesAndBlittingUtil.cpp#L253-L281`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) | Gates `VK_KHR_copy_commands2`, `VK_KHR_separate_depth_stencil_layouts`, `VK_KHR_maintenance1`, `VK_KHR_maintenance5`, `VK_KHR_copy_memory_indirect`, etc. |
| `checkTransferQueueGranularity()` | [`vktApiCopiesAndBlittingUtil.cpp#L339-L381`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L339-L381) | Validates `minImageTransferGranularity` for transfer-only queue cases. |

## Questions / Risk Points for User Audit

- Is the primary behavioral axis (intermediate node / subgroup) the right choice, or should the secondary axis (registration context) be promoted to primary? The current identification reflects that each subgroup tests a distinct *property* of `vkCmdCopyImage`, while registration context varies the *execution environment*.
- Is the `misc` subgroup correctly described as a regression test for a Mesa driver issue? The source comment at [`vktApiCopyImageToImageTests.cpp#L4132-L4143`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4132-L4143) says so explicitly, but the test is still a valid conformance test regardless of its origin.
- Should the `array_to_array_whole_mipmap_*` leaves be described as a separate behavioral group, or are they adequately covered as a special case under `array`? They use a different test instance class (`CopyImageToImageMipmap` vs `CopyImageToImage`), which argues for separate treatment, but they are registered under the same `array` subgroup.
- Are the `clearDestinationWithRed` leaves correctly characterized as out-of-bounds write detectors? The source comment in `TestParams::clearDestinationWithRed` says "Used for CopyImageToImage tests to clear dst image with vec4(1.0, 0.0, 0.0, 1.0)" but does not explicitly state the out-of-bounds detection purpose; that interpretation is inferred from the test design.
- Is the `useGeneralLayout` barrier substitution correctly described? The test code substitutes `VkMemoryBarrier` for `VkImageMemoryBarrier` when `useGeneralLayout` is set, which is a non-obvious implementation choice that affects what driver path is exercised.

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge section into a brief unordered list of necessary prerequisites: size-compatible format copying, compressed-format block-size scaling, image layout transitions, depth/stencil aspect separation. Move detailed application into the appropriate later sections (Behavior Parameters, Runtime Execution).
- Preserve the concrete example only if it remains the most efficient way to build the required mental model; otherwise, distill it into a brief mention in `## Behavior Parameters` or `## Runtime Execution and Result Checking`.
- Carry the `### Failure Cause Mapping` table directly into the final page's `## Failure Meaning` → `### Failure Cause Mapping`. Write `### Cause Analysis` fresh during the rewrite, expanding each cause with `**Possible failure symptoms:**` and `**Possible implementation causes:**` paragraphs grounded in Vulkan spec semantics and source inspection.
- Carry the `## Behavior Parameter Identification` conclusion (intermediate node as primary axis; registration context as secondary axis) into `## Behavior Parameters` with `### <subgroup name>` subsections for each subgroup.
- Move the Source Mapping table into `## Source Reference Appendix` with minimal edits.
- The brief's "Important Variations and Special Cases" section should be distributed across `## Behavior Parameters`, `## Case Pruning`, and `## Key Takeaways` in the final page rather than preserved as a standalone section.
- The brief's teaching material about VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152 should be condensed to a one-line mention in `## Runtime Execution and Result Checking` or `## Behavior Parameters` rather than reproduced verbatim.
- Resolve the risk points above by treating the source comments and the test's structural evidence as authoritative: keep `misc` described as a regression test, treat `array_to_array_whole_mipmap_*` as a special case under `array`, and characterize `clearDestinationWithRed` as an out-of-bounds write detector based on the test design.
