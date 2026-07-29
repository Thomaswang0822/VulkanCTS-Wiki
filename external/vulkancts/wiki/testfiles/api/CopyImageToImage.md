## Overview

**Core question:** does `vkCmdCopyImage` (and its `vkCmdCopyImage2` extension form) copy the exact bytes specified by `VkImageCopy` regions across size-compatible format pairs, image dimensionalities, compressed-format block scaling, layout transitions, queue families, allocation kinds, and sparse binding?

- Covers the implementation-bearing `image_to_image` test family under `api.copy_and_blit`, registered through the `copy_and_blit` dispatcher in `vktApiCopiesAndBlittingTests.cpp`.
- The single implementation file `vktApiCopyImageToImageTests.cpp` (~4460 lines) hosts the `CopyImageToImage` test instance and one registration function per intermediate node.
- Direct intermediate nodes under `image_to_image`: `simple_tests`, `all_formats` (with `color` and `depth_stencil` sub-subgroups), `3d_images`, `dimensions`, `cube`, `array`, and `misc` (TransferOnly only, registered under `copy_commands2.image_to_image_transfer_queue.misc`).
- Sibling variants reuse the same test instance under different parents: `core`, `dedicated_allocation`, `copy_commands2`, `sparse`, plus `image_to_image_general_layout`, `image_to_image_transfer_queue`, `image_to_image_transfer_queue_secondary`, and `image_to_image_transfer_sparse`.
- The page explains what each intermediate node exercises, what the host reference computes, how validation chooses between bitwise, float, and int comparison, and what a failure of each node points to.

## Background Knowledge

- **Size-compatible format copying.** Vulkan permits `vkCmdCopyImage` between formats whose texel block size in bytes is identical (for example `R8G8B8A8_UNORM` and `R32_SFLOAT`, both 32 bits per texel). The copy is a byte-for-byte memcpy; the implementation must not reinterpret channels. The test enumerates every legal pair through `formats::compatibleFormats8Bit` … `compatibleFormats256Bit`.
- **Compressed-format block-size scaling.** `VkExtent3D` and `VkOffset3D` in `VkImageCopy` are measured in texels, not blocks, for compressed formats (BC, ETC2, ASTC, etc.). The test authors parameters in block units, then `iterate()` multiplies by `getBlockWidth` / `getBlockHeight` / `getBlockDepth` before recording the copy, with 1D and 3D exceptions matching VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152.
- **Image layout transitions around the copy.** `vkCmdCopyImage` requires the source in `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`, and the destination in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`. The test records a transfer-stage pipeline barrier moving both images from the `TRANSFER_DST_OPTIMAL` layout left by `uploadImage` into the configured `operationLayout`.
- **Depth/stencil aspect separation.** For combined depth/stencil formats, each `VkImageCopy` region's `imageSubresource.aspectMask` selects exactly one aspect: `VK_IMAGE_ASPECT_DEPTH_BIT` or `VK_IMAGE_ASPECT_STENCIL_BIT`. The host reference walks each aspect separately through `tcu::getEffectiveDepthStencilAccess`. The `_separate_layouts` variants add `VK_KHR_separate_depth_stencil_layouts` and use per-aspect layouts.

## Registration Hierarchy

```text
api.copy_and_blit.core.image_to_image
├── simple_tests
├── all_formats
├── 3d_images
├── dimensions
├── cube
└── array
```

`misc` is gated on `queueSelection == TransferOnly` and only registered under `copy_commands2.image_to_image_transfer_queue.misc`; it does not appear under `core.image_to_image`. The sparse variant prunes `all_formats` and `dimensions`. Sibling families `image_to_image_general_layout`, `image_to_image_transfer_queue_secondary`, and `image_to_image_transfer_sparse` are registered by the dispatcher in `vktApiCopiesAndBlittingTests.cpp` and exercise only `simple_tests` (via `addCopyImageToImageTestsSimpleOnly`); `image_to_image_transfer_queue` runs the full set plus `misc`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type | `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TYPE_3D` | Selects 1D, 2D, 3D, cube, or array image; controls whether 1D/3D compressed-format exceptions apply | [`iterate()` block](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L208-L247) |
| Source/destination format | Color, depth/stencil, compressed formats from `formats::compatibleFormats8Bit` … `compatibleFormats256Bit` and `formats::depthAndStencilFormats` | Determines size-compatible pair, byte-reinterpretation, depth/stencil aspect separation, or compressed block-size scaling | [`vktApiCopyImageToImageTests.cpp#L1525-L1536`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1525-L1536) |
| Image extent | `defaultExtent` (64×64×1), `defaultHalfExtent`, `defaultQuarterExtent`, `default3dExtent`, large/small POT/NPOT | Varies region size, exercises large dimensions, and (for compressed) interacts with block-size alignment | [`addImageToImageDimensionsTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2141-L2298) |
| Copy regions | Whole, partial, multi-region, with offsets | Single or multi-region; partial regions test offset/extent handling; `clearDestinationWithRed` leaves detect out-of-bounds writes | [`addImageToImageSimpleTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1151-L1448) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_TILING_LINEAR` | Linear is skipped when sparse binding is active (VUID-VkImageCreateInfo-tiling-04121) | [`vktApiCopyImageToImageTests.cpp#L1151-L1448`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1151-L1448) |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `SPARSE_BINDING`, `MAINTENANCE_5` (array only), `SEPARATE_DEPTH_STENCIL_LAYOUT` (D/S only) | Selects `vkCmdCopyImage` vs `vkCmdCopyImage2`, sparse binding, `VK_REMAINING_ARRAY_LAYERS`, or separate depth/stencil layouts | [`checkExtensionSupport()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Suballocated for `core` / `copy_commands2` / `sparse`; dedicated for `dedicated_allocation` parent | [`vktApiCopiesAndBlittingTests.cpp#L70-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L70-L230) |
| `queueSelection` | `Universal`, `TransferOnly` | Universal for `core` / `dedicated_allocation` / `copy_commands2`; TransferOnly for `image_to_image_transfer_queue*` and `misc` | [`vktApiCopiesAndBlittingTests.cpp#L70-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L70-L230) |
| `useSecondaryCmdBuffer` | `true` only for `image_to_image_transfer_queue_secondary` | Records the copy into a secondary command buffer executed via `vkCmdExecuteCommands` | [`vktApiCopiesAndBlittingTests.cpp#L193-L202`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L193-L202) |
| `useSparseBinding` | `true` for `sparse.image_to_image` and `image_to_image_transfer_sparse` | Source image uses `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`; sparse semaphore coordinates binding | [`vktApiCopiesAndBlittingTests.cpp#L204-L212`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L204-L212) |
| `useGeneralLayout` | `true` only for `image_to_image_general_layout` | Substitutes `VkMemoryBarrier` for `VkImageMemoryBarrier` and uses `VK_IMAGE_LAYOUT_GENERAL` for both images | [`vktApiCopiesAndBlittingTests.cpp#L215-L229`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L215-L229) |
| `clearDestinationWithRed` | `true` only for `simple_tests.partial_image_*_clear` leaves | Inserts `vkCmdClearColorImage` to red before the copy so out-of-bounds writes survive as red texels | [`vktApiCopyImageToImageTests.cpp#L1151-L1448`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1151-L1448) |

## Behavior Parameters

The primary behavioral axis is the **intermediate node** directly under `image_to_image`. Each intermediate node tests a distinct property of `vkCmdCopyImage`. The secondary axis (registration context) varies the execution environment: queue family, allocation kind, command variant, sparse binding, secondary command buffer, and general-layout usage. Registration context is covered in `### Cause Analysis` rather than as separate subsections here.

### `simple_tests` — basic whole/partial image copy mechanics

Exercises basic `vkCmdCopyImage` for a small set of formats (`R8G8B8A8_UINT`, `R32G32B32_UINT`, `R32G32B32_SFLOAT`) with both optimal and linear tiling. Leaves include `whole_image*`, `partial_image*`, `depth` (using `VK_FORMAT_D32_SFLOAT` with `VK_IMAGE_ASPECT_DEPTH_BIT`), `stencil` (using `VK_FORMAT_S8_UINT` with `VK_IMAGE_ASPECT_STENCIL_BIT`), `whole_image_diff_format` (size-compatible cross-format copy), and `partial_image_*_clear` (clears destination to red before the copy to detect out-of-bounds writes). `depth` and `stencil` leaves use single-aspect formats, not combined depth/stencil; they exercise the depth-only and stencil-only copy paths without the combined-format aspect separation logic.

### `all_formats` — comprehensive size-compatible format coverage

Iterates over `formats::compatibleFormats8Bit` … `compatibleFormats256Bit` for color and `formats::depthAndStencilFormats` for depth/stencil. Two sub-subgroups:

- **`color`** generates test cases for each size-compatible format pair across 1d↔1d, 1d↔2d, 2d↔2d, 2d↔3d, 3d↔3d source/destination type combinations, with optimal/optimal, optimal/general, general/optimal, general/general tiling-layout pairs. The host reference uses the source format applied to the destination buffer to mimic the spec's memcpy semantics.
- **`depth_stencil`** iterates combined depth/stencil formats and emits separate depth and stencil copy regions per case. The `_separate_layouts` variants add `VK_KHR_separate_depth_stencil_layouts` and use per-aspect layouts.

This intermediate node is pruned when `useSparseBinding` is set.

### `3d_images` — 3D ↔ 2D slice and layer mapping

Tests copies between `VK_IMAGE_TYPE_3D` and `VK_IMAGE_TYPE_2D` images, including `3d_to_2d_by_slices` (per-slice regions), `2d_to_3d_by_layers` (per-layer regions assembled into a 3D image), `3d_to_2d_whole`, `2d_to_3d_whole`, and `*_regions` variants with multiple non-whole regions. Exercises the `srcOffset.z` / `dstOffset.z` ↔ `VkImageSubresourceLayers.baseArrayLayer` translation required by the spec.

### `dimensions` — large and non-power-of-two dimension coverage

Tests image copies with large power-of-two and non-power-of-two dimensions across compatible format pairs at 8-bit through 256-bit widths. Leaves include `large_pot_x_small_pot`, `large_pot_x_small_npot`, `small_pot_x_large_pot`, and similar combinations. This intermediate node is pruned when `useSparseBinding` is set.

### `cube` — cube-compatible image copies

Tests copies involving `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` images: `cube_to_array_layers`, `cube_to_array_whole`, `array_to_cube_layers`, `array_to_cube_whole`, `cube_to_cube_layers`, `cube_to_cube_whole`. Exercises cube-face ↔ array-layer mapping for both per-face and whole-cube copies.

### `array` — 2D-array image copies

Tests copies between 2D-array images: `array_to_array_layers`, `array_to_array_whole`, `array_to_array_whole_remaining_layers` and `array_to_array_partial_remaining_layers` (which set `imageSubresource.layerCount = VK_REMAINING_ARRAY_LAYERS` and require `VK_KHR_maintenance5`), and `array_to_array_whole_mipmap_*` (which use the separate `CopyImageToImageMipmap` test instance to iterate over all mip levels in one command buffer with one `VkImageCopy` region per level).

### `misc` — multi-sample then single-sample copy regression (TransferOnly only)

Contains `ms_then_ss*` leaves that clear MS and SS image pairs on the universal queue, copy MS-src→MS-dst and SS-src→SS-dst on the transfer queue (with optional `bottom_of_pipe` / `transfer` / `all_commands` inter-copy barrier stage), resolve MS-dst to an extra SS image on the universal queue, copy both SS images to buffers, and float-compare against expected clear colors. Registered only when `queueSelection == TransferOnly`; appears in mustpass under `copy_commands2.image_to_image_transfer_queue.misc`.

## Shader Analysis

This test family does not use shaders. All work is recorded through `vkCmdCopyImage`, `vkCmdCopyImage2`, `vkCmdClearColorImage`, and `vkCmdResolveImage2`. No `### Representative Shader Walkthrough` subsection is needed.

## Runtime Execution and Result Checking

- The host creates source and destination `VkImage` objects with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`. When `useSparseBinding` is set, the source image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and bound through `allocateAndBindSparseImage`.
- Host-side source and destination `tcu::TextureLevel` objects are filled by `generateBuffer` with the subgroup's fill mode. When `clearDestinationWithRed` is set, the destination is filled with `FILL_MODE_RED` (`vec4(1.0, 0.0, 0.0, 1.0)`).
- The expected `tcu::TextureLevel` is produced by `copyRegionToTextureLevel`, which for non-depth/stencil formats applies the source format to the destination buffer to mimic the spec's "CopyImage acts like a memcpy" rule, and for combined depth/stencil formats walks each aspect separately through `tcu::getEffectiveDepthStencilAccess`.
- `uploadImage` transitions both images into `TRANSFER_DST_OPTIMAL` (or `GENERAL` when `useGeneralLayout` is set), seeding them with the host-side fill data.
- `iterate()` records a transfer-stage pipeline barrier moving the source from `TRANSFER_DST_OPTIMAL` to `m_params.src.image.operationLayout` and the destination to `m_params.dst.image.operationLayout`. When `clearDestinationWithRed` is set, a `vkCmdClearColorImage` to red is inserted between two pipeline barriers so that out-of-bounds writes by the subsequent copy survive as red texels in the read-back.
- For compressed source or destination formats, the per-region `srcOffset` / `dstOffset` / `extent` are multiplied by `getBlockWidth` / `getBlockHeight` / `getBlockDepth` before recording, with 1D and 3D exceptions per VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152.
- The copy is dispatched as `vkCmdCopyImage` (default) or `vkCmdCopyImage2` (`COPY_COMMANDS_2` flag). When `useSecondaryCmdBuffer` is set, the copy is recorded into a secondary command buffer executed by the primary via `vkCmdExecuteCommands`.
- Submission uses `submitCommandsAndWaitWithTransferSync`, which includes the sparse semaphore when `useSparseBinding` is set so sparse memory binding completes before the copy executes.
- The destination is read back via `readImage`, then `checkTestResult` compares:
  - color formats with `tcu::bitwiseCompare` and zero threshold;
  - depth components with `tcu::floatThresholdCompare` and zero threshold (or `tcu::intThresholdCompare` for integer depth);
  - stencil components with `tcu::intThresholdCompare` and zero threshold (or `tcu::floatThresholdCompare` when the result format is float).
- For `misc.ms_then_ss*` leaves, the MS-resolved extra image must match the MS source clear color and the SS destination must match the SS source clear color, both via `tcu::floatThresholdCompare` with zero threshold.

## Failure Meaning

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

#### Basic `vkCmdCopyImage` mechanics failures

**Possible failure symptoms:** read-back destination texels within the requested region do not bit-exactly match the source's bytes (reinterpreted through the size-compatible destination format); depth or stencil values within the region mismatch; texels outside a `clearDestinationWithRed` region are not red, indicating the copy wrote outside the requested offset/extent.

**Possible implementation causes:** the driver reinterprets bytes instead of memcpying for size-compatible format pairs; per-region `srcOffset` / `dstOffset` / `extent` arithmetic is off; the depth-only or stencil-only aspect routing for `VK_FORMAT_D32_SFLOAT` or `VK_FORMAT_S8_UINT` writes to the wrong aspect; or the implementation writes outside the requested region (visible only when `clearDestinationWithRed` masks the surrounding texels with red).

#### Size-compatible format pair handling failures

**Possible failure symptoms:** mismatched bytes for same-width different-channel-layout pairs (for example `R8G8B8A8_UNORM` ↔ `R32_SFLOAT`), or for compressed-to-uncompressed pairs.

**Possible implementation causes:** the driver reinterprets channels instead of treating the copy as a memcpy; or the compressed-format block-size scaling in the implementation differs from the texel-unit extent semantics the spec requires.

#### Depth/stencil aspect separation failures

**Possible failure symptoms:** depth aspect written correctly but stencil aspect mismatched (or vice versa); one aspect corrupts the other when both are loaded; `_separate_layouts` variants fail while non-separate-layout variants pass.

**Possible implementation causes:** the driver writes both aspects when only one is requested; per-aspect offset computation is wrong for combined depth/stencil formats; or the implementation does not correctly honor `VK_KHR_separate_depth_stencil_layouts` per-aspect layouts.

#### 3D-slice ↔ 2D-layer mapping failures

**Possible failure symptoms:** 3D-to-2D copies produce slices in the wrong order, or 2D-to-3D copies assemble layers into the wrong depth coordinates.

**Possible implementation causes:** the driver mishandles `srcOffset.z` / `dstOffset.z` ↔ `VkImageSubresourceLayers.baseArrayLayer` translation, or the `srcSubresource.layerCount` ↔ `extent.depth` interaction for whole-slice copies.

#### Dimension-dependent failures

**Possible failure symptoms:** large-POT copies succeed but small-NPOT copies fail; or specific bit-width format pairs fail.

**Possible implementation causes:** the implementation reports support for a format at the requested dimension but cannot actually copy at that size; or `minImageTransferGranularity` is violated on transfer-only queue variants.

#### Cube-compatible image failures

**Possible failure symptoms:** per-face copies land on the wrong face, or whole-cube copies drop or duplicate a face.

**Possible implementation causes:** the driver maps cube-face indices to array layers incorrectly, or `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` is not honored for the copy path.

#### 2D-array image failures

**Possible failure symptoms:** per-layer copies land on the wrong layer; `VK_REMAINING_ARRAY_LAYERS` copies copy too few or too many layers; mipmap copies miss levels or write to the wrong level.

**Possible implementation causes:** the driver does not correctly resolve `VK_REMAINING_ARRAY_LAYERS` (MAINTENANCE_5); or the mipmap iteration in `CopyImageToImageMipmap` exposes a per-level layout transition bug.

#### Multi-sample then single-sample copy failures

**Possible failure symptoms:** the MS-resolved image does not match the MS source clear color, or the SS destination does not match the SS source clear color.

**Possible implementation causes:** the inter-copy barrier stage (`bottom_of_pipe`, `transfer`, `all_commands`) does not correctly serialize the two copies on the transfer queue; or MS resolve on the universal queue observes stale data because the transfer-queue copy was not made visible.

#### Command variant and queue family failures

**Possible failure symptoms:** all leaves under `copy_commands2.*` fail while `core.*` pass; all leaves under `*_transfer_queue*` fail while universal-queue variants pass; all leaves under `*_transfer_queue_secondary` fail while primary-cmdbuffer variants pass; all leaves under `core.image_to_image_general_layout` fail while non-general-layout variants pass.

**Possible implementation causes:** `vkCmdCopyImage2KHR` struct conversion or dispatch differs from `vkCmdCopyImage`; transfer-only queue execution violates `minImageTransferGranularity`; secondary command buffer execution does not inherit the transfer-queue state correctly; or the implementation rejects `VK_IMAGE_LAYOUT_GENERAL` as the copy layout.

#### Allocation kind failures

**Possible failure symptoms:** all leaves under `dedicated_allocation.*` fail while `core.*` pass.

**Possible implementation causes:** dedicated-allocation memory binding for the source or destination image exposes a copy path that depends on suballocated memory layout assumptions.

#### Sparse binding failures

**Possible failure symptoms:** all sparse-variant leaves fail while non-sparse equivalents pass; or failures are intermittent because the sparse semaphore did not wait on the correct queue.

**Possible implementation causes:** sparse image memory binding does not complete before the copy executes; sparse residency is not correctly honored for the copy path; or the sparse semaphore synchronization in `submitCommandsAndWaitWithTransferSync` is incorrect.

## Case Pruning

### Requirement-based pruning

- `copy_commands2` variants require `VK_KHR_copy_commands2` or Vulkan 1.3, gated by `checkExtensionSupport()`.
- `SEPARATE_DEPTH_STENCIL_LAYOUT` variants require `VK_KHR_separate_depth_stencil_layouts`.
- `array_to_array_whole_remaining_layers` and `array_to_array_partial_remaining_layers` require `VK_KHR_maintenance5`, gated in `checkSupport()`.
- Transfer-only queue variants require a transfer-only queue family and that `minImageTransferGranularity` is not violated, validated by `checkTransferQueueGranularity()`.
- Sparse variants require sparse image support for the requested format, plus `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` and `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` support.
- Compressed-format cases require the device to support the compressed format at the requested tiling and usage.
- All format/image-type combinations are validated against `getPhysicalDeviceImageFormatProperties()` in `checkSupport()`.

### Design-based pruning

- `all_formats` and `dimensions` are skipped when `useSparseBinding` is set, leaving sparse variants with a smaller subgroup set.
- `misc` is only registered when `queueSelection == TransferOnly`; its mustpass paths live under `copy_commands2.image_to_image_transfer_queue.misc` rather than under `core.image_to_image`.
- Linear tiling is skipped when `useSparseBinding` is set (VUID-VkImageCreateInfo-tiling-04121).
- `image_to_image_general_layout`, `image_to_image_transfer_queue_secondary`, and `image_to_image_transfer_sparse` use `addCopyImageToImageTestsSimpleOnly` and exercise only `simple_tests`; they exist as separate sibling families to isolate the general-layout, secondary-command-buffer, and sparse-on-transfer-queue execution paths from the full matrix.
- `dedicated_allocation.image_to_image` filters the color format set through `isAllowedImageToImageAllFormatsColorSrcFormatTests()` to keep the dedicated-allocation matrix manageable.

## Key Takeaways

- The test treats `vkCmdCopyImage` as a byte-exact memcpy across size-compatible format pairs; any driver reinterpretation of channels fails the bit-exact comparison.
- Compressed-format regions are authored in block units and scaled to texels before recording, with 1D and 3D exceptions matching VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152.
- Depth and stencil aspects of combined formats are copied separately; the `_separate_layouts` variants add coverage for `VK_KHR_separate_depth_stencil_layouts`.
- The `clearDestinationWithRed` mechanism in `simple_tests.partial_image_*_clear` leaves is the test's out-of-bounds write detector: untouched destination texels must remain red.
- Sibling families `image_to_image_general_layout`, `image_to_image_transfer_queue_secondary`, and `image_to_image_transfer_sparse` restrict to `simple_tests` to isolate one execution-environment variable at a time.
- The `array_to_array_whole_mipmap_*` leaves use a different test instance (`CopyImageToImageMipmap`) that iterates over all mip levels in one command buffer, distinct from the single-mip `CopyImageToImage` instance used elsewhere.
- See `## Failure Meaning` for the per-intermediate-node failure cause mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CopyImageToImage` test instance class | [`vktApiCopyImageToImageTests.cpp#L59-L75`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L59-L75) | Owns source image, destination image, sparse allocations, and the `iterate()` entry point. |
| `CopyImageToImage::iterate()` | [`vktApiCopyImageToImageTests.cpp#L168-L388`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L168-L388) | Fills images, records barriers and copy command, submits, reads back, and checks the result. |
| `CopyImageToImage::checkTestResult()` | [`vktApiCopyImageToImageTests.cpp#L390-L447`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L390-L447) | Bit-exact, float-threshold, or int-threshold comparison with zero threshold. |
| `CopyImageToImage::copyRegionToTextureLevel()` | [`vktApiCopyImageToImageTests.cpp#L449-L513`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L449-L513) | Host-side reference computation; uses source format on destination buffer to mimic memcpy semantics. |
| `CopyImageToImageTestCase::checkSupport()` | [`vktApiCopyImageToImageTests.cpp#L530-L628`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L530-L628) | Gates extensions, transfer queue granularity, format support, and image dimension limits. |
| `CopyImageToImageMipmap` class | [`vktApiCopyImageToImageTests.cpp#L634-L1054`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L634-L1054) | Separate instance for `array_to_array_whole_mipmap_*` leaves; iterates over all mip levels. |
| `addImageToImageSimpleTests()` | [`vktApiCopyImageToImageTests.cpp#L1151-L1448`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1151-L1448) | Registers `simple_tests` leaves including depth, stencil, diff_format, and clear variants. |
| `addImageToImageAllFormatsColorTests()` | [`vktApiCopyImageToImageTests.cpp#L1580-L2140`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1580-L2140) | Registers `all_formats.color` leaves across all 1d/2d/3d ↔ 1d/2d/3d pairs. |
| `addImageToImageAllFormatsDepthStencilTests()` | [`vktApiCopyImageToImageTests.cpp#L2300-L3158`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2300-L3158) | Registers `all_formats.depth_stencil` leaves with optional `_separate_layouts` variants. |
| `addImageToImage3dImagesTests()` | [`vktApiCopyImageToImageTests.cpp#L3167-L3479`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3167-L3479) | Registers `3d_images` leaves. |
| `addImageToImageDimensionsTests()` | [`vktApiCopyImageToImageTests.cpp#L2141-L2298`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2141-L2298) | Registers `dimensions` leaves across large-POT/small-POT, large-POT/small-NPOT, etc. |
| `addImageToImageCubeTests()` | [`vktApiCopyImageToImageTests.cpp#L3486-L3816`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3486-L3816) | Registers `cube` leaves. |
| `addImageToImageArrayTests()` | [`vktApiCopyImageToImageTests.cpp#L3818-L4115`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3818-L4115) | Registers `array` leaves including MAINTENANCE_5 and mipmap variants. |
| `addImageToImageMiscTests()` | [`vktApiCopyImageToImageTests.cpp#L4413-L4436`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4413-L4436) | Registers `misc.ms_then_ss*` leaves; TransferOnly only. |
| `multiSampleThenSingleSampleTest()` | [`vktApiCopyImageToImageTests.cpp#L4144-L4411`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4144-L4411) | The misc test body. |
| `addCopyImageToImageTests()` | [`vktApiCopyImageToImageTests.cpp#L4440-L4454`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4440-L4454) | Public entry point that adds the six subgroups (plus conditional `misc`). |
| `addCopyImageToImageTestsSimpleOnly()` | [`vktApiCopyImageToImageTests.cpp#L4456-L4459`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4456-L4459) | Adds only `simple_tests`; used for `general_layout`, `transfer_queue_secondary`, and `transfer_sparse` variants. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L70-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L70-L230) | Routes `image_to_image` into `core`, `dedicated_allocation`, `copy_commands2`, and `sparse` parents; registers sibling families. |
| `getSizeCompatibleTcuTextureFormat()` | [`vktApiCopiesAndBlittingUtil.cpp#L170-L177`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L170-L177) | Maps compressed formats to size-compatible uncompressed tcu formats for host reference. |
| `checkExtensionSupport()` | [`vktApiCopiesAndBlittingUtil.cpp#L253-L281`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) | Gates `VK_KHR_copy_commands2`, `VK_KHR_separate_depth_stencil_layouts`, `VK_KHR_maintenance1`, `VK_KHR_maintenance5`, etc. |
| `checkTransferQueueGranularity()` | [`vktApiCopiesAndBlittingUtil.cpp#L339-L381`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L339-L381) | Validates `minImageTransferGranularity` for transfer-only queue cases. |
