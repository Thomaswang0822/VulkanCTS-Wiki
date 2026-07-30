# Understanding Brief: `api.copy_and_blit.core.blit_image` (and the `dedicated_allocation` / `copy_commands2` variants)

## One-Sentence Test Purpose

This test checks whether the implementation's `vkCmdBlitImage` (and `vkCmdBlitImage2` via `VK_KHR_copy_commands2`) produces texel results consistent with a CPU-side reference blit across scaling, mirroring, format conversion, and filtering with `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR`, and `VK_FILTER_CUBIC_EXT`.

## Background Knowledge

### `vkCmdBlitImage` versus `vkCmdCopyImage`

`vkCmdBlitImage` differs from `vkCmdCopyImage` in two ways that this test exercises:

- **Scaling.** Source and destination regions are described by two `VkOffset3D` corners each. The implementation must sample the source subregion to fill the destination subregion, including upscaling and downscaling.
- **Filtering.** A `VkFilter` argument selects how source texels are combined: `VK_FILTER_NEAREST` (exact texel match), `VK_FILTER_LINEAR` (linear blend), or `VK_FILTER_CUBIC_EXT` (cubic blend, requires `VK_EXT_filter_cubic`).

Why it matters here:

- `VK_FILTER_NEAREST` is verified by exact comparison against the source, with format-specific thresholds.
- `VK_FILTER_LINEAR` and `VK_FILTER_CUBIC_EXT` are verified by threshold comparison against two CPU references: a clamped reference (using only the source subregion) and an unclamped reference (using the whole source image), so that edge-clamp sampling is accepted.

### Format compatibility for blits

`vkCmdBlitImage` requires the source and destination formats to be compatible: same class of signed/unsigned integer for integer formats, or both sampled as floats for float, unorm, snorm, uscaled, sscaled, srgb classes. The test iterates source formats and a list of compatible destination formats per source class, and skips combinations that the framework does not support.

Why it matters here:

- The `all_formats.color` matrix produces leaves for many src×dst format pairs, including integer-to-float and float-to-integer pairs that are filtered out by the compatibility list.
- The `BlitColorTestParams::compatibleFormats` field carries the per-source-class destination list used by the iteration.

### Compressed source and destination formats

Compressed formats (ASTC, BC, ETC, EAC) are decompressed on the host into a `tcu::PixelBufferAccess` and compared as decompressed images. Random compressed data would generate invalid blocks, so `CompressedTextureForBlit` ensures every block is valid for ASTC (LDR/HDR), BC6H (predefined valid blocks in `<-1; 1>` or `<0; 1>` range), BC7 (every block's mode byte has at least one bit set), and ETC.

Why it matters here:

- A failure on a compressed leaf could come from the blit, the implementation's compressed-format blit support, or the framework's decompression of the result image.
- BC6H and ASTC SFLOAT sources can produce large color values that the test clamps during comparison for non-float destination formats.

### Mirror mode and coordinate flipping

A blit region's mirror mode is computed from the offset pairs: if the destination offsets are reversed relative to the source offsets along an axis, that axis is mirrored. The host reference (`copyRegionToTextureLevel`) calls `getMirrorMode()` and `flipCoordinates()` before invoking `tcu::scale` or `tcu::blit`, so the CPU reference produces a flipped image to match the implementation.

Why it matters here:

- A failure on a `mirror_*` leaf could come from the implementation's mirror handling or from the host reference producing the wrong orientation.
- The `mirror_z_3d` leaf only exists for 3D images because 2D images have no Z axis.

### Mipmap generation via blits

The `generate_mipmaps` intermediate node blits between mip levels of the same image. The `from_base_level` variant blits from level 0 to every other level in a single command; the `from_previous_level` variant blits each level from the previous one in separate commands, with pipeline barriers between levels.

Why it matters here:

- `from_previous_level` accumulates error across levels, so the verification recomputes the expected result for level N from the verified result of level N-1.
- A failure on `from_previous_level` while `from_base_level` passes can indicate a per-level barrier or layout transition bug rather than a scaling bug.

## One Concrete Example

A representative case is `dEQP-VK.api.copy_and_blit.core.blit_image.simple_tests.scaling_whole1.nearest`:

```text
[host] Create a 64x64 source VkImage (VK_FORMAT_R8G8B8A8_UNORM, optimal tiling, TRANSFER_SRC|TRANSFER_DST usage).
[host] Create a 32x32 destination VkImage (same format, same tiling, same usage).
[host] Fill the source with a deterministic gradient via generateBuffer.
[host] Build one VkImageBlit region: srcOffsets [{0,0,0}, {64,64,1}], dstOffsets [{0,0,0}, {32,32,1}].
[host] Compute the expected destination via copyRegionToTextureLevel using tcu::scale with NEAREST filter.
[host] Record a pipeline barrier to TRANSFER_SRC_OPTIMAL/TRANSFER_DST_OPTIMAL, then vkCmdBlitImage with VK_FILTER_NEAREST.
[device] Downscale the 64x64 source to the 32x32 destination using nearest-neighbor sampling.
[host] Read back the destination via readImage.
[host] Compare the result against the expected texture level using floatNearestBlitCompare with format-specific thresholds.
[host] Pass if every texel is within threshold.
```

## End-to-End Test Flow

```text
[host] Choose filter (NEAREST/LINEAR/CUBIC), mirror mode, scaling mode, image type, and src/dst formats from the registered leaf parameters.
[host] Create source VkImage (TRANSFER_SRC|TRANSFER_DST usage; sparse flags when useSparseBinding is set).
[host] Create destination VkImage (TRANSFER_SRC|TRANSFER_DST usage; mipLevels for the mipmap variant).
[host] Generate source texture level (gradient or compressed texture decompressed on host); upload to source image.
[host] Generate destination texture level (gradient); upload to destination image (one mip level at a time for the mipmap variant).
[host] Compute expected result via generateExpectedResult: copyRegionToTextureLevel for each region, with NEAREST using tcu::scale/blit on the subregion and LINEAR/CUBIC additionally computing an unclamped reference from the whole source buffer.
[host] Record pipeline barriers to the requested operation layouts (TRANSFER_SRC_OPTIMAL/TRANSFER_DST_OPTIMAL or GENERAL).
[host] Record vkCmdBlitImage or vkCmdBlitImage2 with the VkImageBlit / VkImageBlit2KHR regions and the chosen filter.
[device] Execute the blit: sample the source subregion, apply mirror/scaling/filtering, write to the destination subregion.
[host] For the mipmap variant: optionally record one blit per mip level with a pipeline barrier between levels.
[host] Submit and wait; include the sparse semaphore for sparse cases.
[host] Read back the destination via readImage. If destination is compressed, decompress the result on the host before comparison.
[host] checkTestResult dispatches to checkNearestFilteredResult, checkNonNearestFilteredResult, checkCompressedNearestFilteredResult, or checkCompressedNonNearestFilteredResult based on filter and source format.
[host] Pass if every texel is within threshold; fail with "Result image is incorrect" otherwise.
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- No shader source, SPIR-V, HLSL, or Amber artifacts are generated. All work is recorded by the host through `vkCmdBlitImage` or `vkCmdBlitImage2`.
- The CPU reference is generated on the fly by `BlittingImages::generateExpectedResult` and `BlittingMipmaps::generateExpectedResult`, which call `tcu::scale` and `tcu::blit` from the framework.
- The `CompressedTextureForBlit` helper generates compressed texture data with valid blocks (ASTC LDR/HDR, BC6H, BC7, ETC) at runtime.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|----------------|--------------------------|----------------------|----------------|
| Source `VkImage` | Yes | Yes (transfer source) | Read by the blit command | No | Holds the source texels; supports sparse binding through `m_sparseSemaphore`. |
| Destination `VkImage` | Yes | Yes (transfer destination) | Written by the blit command | Yes, via `readImage` | Receives the blitted texels; for the mipmap variant it owns multiple mip levels. |
| Source `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the reference source | Host-side source used by `copyRegionToTextureLevel` to compute the expected result. |
| Expected `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the comparison reference | Host-computed oracle produced by `generateExpectedResult`. |
| Unclamped expected `tcu::TextureLevel` | Yes, on the host (LINEAR/CUBIC only) | No | No | Yes, as the fallback reference | Computed by `scaleFromWholeSrcBuffer` using the whole source buffer rather than the subregion; used when the clamped reference fails. |
| Compressed source `CompressedTextureForBlit` | Yes, on the host | No | No | Yes, decompressed for comparison | Provides valid-block compressed data and its host decompression for the reference. |
| Sparse semaphore | Yes, when `useSparseBinding` is set | Yes | No | No | Synchronizes sparse memory binding with the blit submission. |

## What Is Checked

- The destination image, read back by the host, is compared against the expected `tcu::TextureLevel`. For compressed destination formats, the destination is decompressed on the host before comparison.
- For `VK_FILTER_NEAREST`: `checkNearestFilteredResult` (or `checkCompressedNearestFilteredResult`) compares against the source with format-specific thresholds derived from `getFloatOrFixedPointFormatThreshold` or `getCompressedFormatThreshold`. Integer sources use `intNearestBlitCompare`; float and fixed-point sources use `floatNearestBlitCompare`.
- For `VK_FILTER_LINEAR` and `VK_FILTER_CUBIC_EXT`: `checkNonNearestFilteredResult` (or `checkCompressedNonNearestFilteredResult`) compares against both the clamped reference (subregion only) and the unclamped reference (whole source buffer), accepting either. The threshold is the sum of source and destination format thresholds, multiplied by 1.5 for CUBIC.
- For depth/stencil formats: the result is split into depth and stencil aspects via `getEffectiveDepthStencilAccess` before each check.
- For the mipmap variant: each mip level is read back and compared independently, with the expected result for level N recomputed from the verified result of level N-1 in the `from_previous_level` case.
- The pass condition is `tcu::TestStatus::pass("Pass")` only if every aspect and every level is within threshold. A single failing texel produces `tcu::TestStatus::fail("Result image is incorrect")`.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group (the leaf cluster under `simple_tests` and the intermediate node under `all_formats`)
>
> **Candidate values:** `whole` / `array` / `mirror_*` / `scaling_*` / `without_scaling_partial` / `3d_to_2d_array` (simple_tests); `color` / `depth_stencil` / `generate_mipmaps` (all_formats)

The primary behavioral axis is the registered leaf cluster. Each cluster stresses a different field of `VkImageBlit` or a different format/filter dimension. The `simple_tests` clusters vary the region geometry (whole, mirror, scaling, partial, 3D-to-2D-array). The `all_formats` clusters vary the format class (color, depth/stencil, mipmaps).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `whole` (2D and 3D) | Whole-image blit with no scaling and no mirroring; basic `vkCmdBlitImage` dispatch with the chosen filter. |
| `array` (`all_remaining_layers`, `not_all_remaining_layers`) | `VK_REMAINING_ARRAY_LAYERS` resolution or array-layer dispatch; requires `VK_KHR_maintenance5`. |
| `mirror_x` / `mirror_y` / `mirror_xy` / `mirror_subregions` (2D) | X/Y mirror-axis handling and the host reference's `flipCoordinates` path. |
| `mirror_x_3d` / `mirror_y_3d` / `mirror_z_3d` / `mirror_xy_3d` / `mirror_subregions_3d` | 3D mirror handling, including Z-axis mirroring which only applies to 3D images. |
| `scaling_whole1` (downscale 2x) | Downscaling with NEAREST/LINEAR/CUBIC; sample-position computation when the destination is smaller than the source. |
| `scaling_whole2` (upscale 2x) | Upscaling with NEAREST/LINEAR/CUBIC; sample-position computation when the destination is larger than the source. |
| `scaling_and_offset` | Source and destination subregions with non-zero offsets combined with scaling. |
| `without_scaling_partial` | Multiple non-overlapping subregions with no scaling; multi-region dispatch. |
| `3d_to_2d_array` (`cube_slice`, `single_slices`, `complex_blit`) | 3D-to-2D-array slice mapping with `MAINTENANCE_8`; requires the `VK_KHR_maintenance8` extension. |
| `all_formats.color.*` | Format conversion between source and destination color formats; integer/float/srgb/compressed class handling and tiling/layout combinations. |
| `all_formats.depth_stencil.*` | Depth/stencil aspect separation, separate depth/stencil layouts (`SEPARATE_DEPTH_STENCIL_LAYOUT`), and 1D/2D/3D depth/stencil blits. |
| `all_formats.generate_mipmaps.from_base_level` | Single-command mipmap generation from level 0 to all levels. |
| `all_formats.generate_mipmaps.from_previous_level` | Per-level mipmap generation with pipeline barriers between levels; accumulated error across levels. |
| All leaves under `dedicated_allocation.blit_image.*` | Dedicated-allocation memory binding for source or destination image. |
| All leaves under `copy_commands2.blit_image.*` | `vkCmdBlitImage2KHR` / `VkImageBlit2KHR` struct conversion or dispatch. |
| All leaves with `_linear` or `_cubic` suffix | Linear or cubic filter implementation, including `VK_EXT_filter_cubic` for cubic. |
| All leaves with `_stripes_*` suffix (3D color only) | Stripe fill patterns (`FILL_MODE_BLUE_RED_X/Y/Z`) used to expose axis-dependent scaling bugs in 3D. |

## Important Variations and Special Cases

- **Cubic filtering.** Only 2D images support `VK_FILTER_CUBIC_EXT`. The 1D and 3D color test registrations force `onlyNearestAndLinear = true` to skip cubic. The `simple_tests` registration gates cubic on `params.dst.image.imageType == VK_IMAGE_TYPE_2D`.
- **Linear tiling.** The `all_formats.color` matrix iterates both `VK_IMAGE_TILING_OPTIMAL` and `VK_IMAGE_TILING_LINEAR` for source and destination, but skips `LINEAR + TRANSFER_*_OPTIMAL` because it is assumed to behave like `LINEAR + GENERAL`. Linear tiling is restricted to a subset of formats (`linearOtherImageFormatsToTest`).
- **`SEPARATE_DEPTH_STENCIL_LAYOUT`.** Depth/stencil formats with both aspects register an extra `_separate_layouts` leaf that uses `VK_EXT_separate_depth_stencil_layouts`-style barriers.
- **`MAINTENANCE_5` and `MAINTENANCE_8`.** The `array` leaves set `MAINTENANCE_5` for `VK_REMAINING_ARRAY_LAYERS`; the `3d_to_2d_array` leaves set `MAINTENANCE_8` for 3D-to-2D-array slice mapping.
- **Sparse binding.** The `BlittingImages` class supports sparse binding through `m_sparseSemaphore` and `allocateAndBindSparseImage`, but the dispatcher does not set `useSparseBinding = true` for the `blit_image` subgroup. The sparse path is supported by the class but not exercised by registered cases.
- **`singleCommand` versus per-level barriers.** `from_base_level` sets `singleCommand = true` and blits all mip levels in one command; `from_previous_level` sets `singleCommand = false` and blits one level per command with a pipeline barrier between levels. The `from_previous_level` variant also registers `mipbarriercount_*` and `layerbarriercount_*` subgroups that vary `barrierCount`.
- **Compressed format thresholds.** Compressed source formats use `getCompressedFormatThreshold` plus an `acceptedError` of 0.04 (nearest) or 0.06 (non-nearest) to tolerate rare per-pixel differences from the decompression reference. BC6H and ASTC SFLOAT sources may be clamped to `<-1; 1>` or `<0; 1>` for non-float destinations to match what the device would produce.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `BlittingImages` test instance class | [`vktApiBlittingTests.cpp#L171-L212`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L171-L212) | Owns source/destination images, sparse semaphore, expected texture level, and compressed texture helpers. |
| `BlittingImages::iterate()` | [`vktApiBlittingTests.cpp#L337-L499`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L337-L499) | Fills images, records the blit command, submits, reads back, and dispatches the check. |
| `BlittingImages::checkTestResult()` | [`vktApiBlittingTests.cpp#L892-L988`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L892-L988) | Selects nearest/non-nearest/compressed check based on filter and source format. |
| `checkNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L688-L744`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L688-L744) | Exact-with-threshold comparison for NEAREST. |
| `checkNonNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L501-L580`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L501-L580) | Threshold comparison against clamped and unclamped references for LINEAR/CUBIC. |
| `copyRegionToTextureLevel()` | [`vktApiBlittingTests.cpp#L990-L1106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L990-L1106) | Host reference computation; uses `getMirrorMode`, `flipCoordinates`, `tcu::scale`, `tcu::blit`, `scaleFromWholeSrcBuffer`. |
| `CompressedTextureForBlit` constructor | [`vktApiBlittingTests.cpp#L56-L157`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L56-L157) | Generates valid-block compressed data for ASTC, BC6H, BC7, ETC. |
| `BlitImageTestCase::checkSupport()` | [`vktApiBlittingTests.cpp#L1271-L1342`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1271-L1342) | Gates `VK_KHR_maintenance5`, `VK_EXT_texture_compression_astc_3d`, `VK_EXT_filter_cubic`, format features, and `BLIT_SRC`/`BLIT_DST` support. |
| `BlittingMipmaps` class | [`vktApiBlittingTests.cpp#L1348-L1371`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1348-L1371) | Mipmap variant: owns a 16-level expected texture array and per-level unclamped references. |
| `BlittingMipmaps::iterate()` | [`vktApiBlittingTests.cpp#L1464-L1735`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1464-L1735) | Records either a single multi-region blit (`singleCommand`) or one blit per level with barriers. |
| `addBlittingImageSimpleTests()` (registrar) | [`vktApiBlittingTests.cpp#L2745-L2787`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2745-L2787) | Registers the `simple_tests` subgroup tree (2D, 3D, 3D-to-2D-array). |
| `addBlittingImageAllFormatsColorTests()` | [`vktApiBlittingTests.cpp#L3202-L3433`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3202-L3433) | Registers the `all_formats.color` subgroup tree (1D, 2D, 3D, ASTC 3D). |
| `addBlittingImageAllFormatsDepthStencilTests()` | [`vktApiBlittingTests.cpp#L3458-L3815`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3458-L3815) | Registers the `all_formats.depth_stencil` subgroup tree (1D, 2D, 3D, separate layouts). |
| `addBlittingImageAllFormatsMipmapTests()` | [`vktApiBlittingTests.cpp#L4099-L4106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4099-L4106) | Registers the `all_formats.generate_mipmaps.from_base_level` and `from_previous_level` subgroups. |
| `addBlittingImageTests()` (public entry) | [`vktApiBlittingTests.cpp#L4117-L4121`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4117-L4121) | Adds `simple_tests` and `all_formats` under `blit_image`. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L136`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136) | `blit_image` is added under `core`, `dedicated_allocation`, and `copy_commands2` parent contexts. |

## Questions / Risk Points for User Audit

- Is the core test purpose (verify `vkCmdBlitImage` scaling, mirroring, filtering, and format conversion against a CPU reference) clearly stated?
- Is the host/device timeline understandable, including the dual clamped/unclamped reference for LINEAR/CUBIC?
- Are compressed format special cases (BC6H/BC7/ASTC valid-block generation, threshold tolerance, clamp ranges) explained at the right depth?
- Is the mipmap variant's `from_base_level` versus `from_previous_level` distinction clear, including the per-level reference recomputation for `from_previous_level`?
- Is the behavioral axis (leaf cluster) the right choice, or should the filter (`NEAREST`/`LINEAR`/`CUBIC`) be a separate axis?
- Are the `MAINTENANCE_5`, `MAINTENANCE_8`, `SEPARATE_DEPTH_STENCIL_LAYOUT`, and `COPY_COMMANDS_2` extension gates correctly attributed to the leaves that require them?
- Is the sparse-binding caveat (supported by the class but not exercised by registered cases) clearly stated?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a short bullet list: `vkCmdBlitImage` versus copy (scaling + filtering), format compatibility classes, compressed format decompression reference, mirror mode and `flipCoordinates`, and the mipmap `singleCommand` versus per-level-barrier distinction.
- Preserve the clamped/unclamped reference contrast in `Runtime Execution and Result Checking` because it is essential to understanding why a LINEAR/CUBIC failure can still pass on the unclamped reference.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`. The `### Cause Analysis` subsections will be written fresh during the rewrite, grounded in the source and the Vulkan spec.
- The concrete example can be omitted from the final page; the `Runtime Execution and Result Checking` section will cover the same flow more formally.
- The source mapping table becomes the Source Reference Appendix, with row labels matching function/range names.
- The `Behavior Parameter Identification` conclusion (behavioral group as the primary axis, with `simple_tests` clusters and `all_formats` intermediate nodes as candidate values) is carried into `## Behavior Parameters`.
- The brief's teaching material on compressed format block generation should be condensed to a single paragraph in the final page's `Runtime Execution and Result Checking` section; the per-format valid-block details belong only in the Cause Analysis for compressed-format failures.
