## Overview

**Core question:** Does the implementation's `vkCmdBlitImage` (and `vkCmdBlitImage2` via `VK_KHR_copy_commands2`) produce texel results consistent with a CPU-side reference blit across scaling, mirroring, format conversion, and `VK_FILTER_NEAREST` / `VK_FILTER_LINEAR` / `VK_FILTER_CUBIC_EXT` filtering?

- Source file: [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp). Header: [`vktApiBlittingTests.hpp`](../../../modules/vulkan/api/vktApiBlittingTests.hpp).
- Test category: `api`. Test family: `blit_image`, registered under three `copy_and_blit` parent contexts: `core`, `dedicated_allocation`, and `copy_commands2`. Each parent calls [`addBlittingImageTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4117-L4121) with a different `allocationKind` and `extensionFlags` and produces the same `simple_tests` / `all_formats` subtree.
- The `blit_image` group is registered by [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136) for the `core`, `dedicated_allocation`, and `copy_commands2` parent contexts. The same subtree shape appears under each parent; the parent context selects allocation kind and command variant.
- Two Vulkan command variants are exercised: `vkCmdBlitImage` (default and `dedicated_allocation`) and `vkCmdBlitImage2` (`copy_commands2`, requires `VK_KHR_copy_commands2`).
- Verification is a CPU-side reference comparison. The host computes the expected image with `tcu::scale` / `tcu::blit` and compares the read-back image with format-specific thresholds; `VK_FILTER_LINEAR` and `VK_FILTER_CUBIC_EXT` accept an unclamped reference computed from the whole source image.

## Background Knowledge

- **`vkCmdBlitImage` versus `vkCmdCopyImage`.** A blit samples the source subregion described by two `VkOffset3D` corners and writes the resampled texels into the destination subregion. The `VkFilter` argument selects how source texels are combined: `VK_FILTER_NEAREST` (exact texel match), `VK_FILTER_LINEAR` (linear blend), or `VK_FILTER_CUBIC_EXT` (cubic blend, requires `VK_EXT_filter_cubic`).
- **Format compatibility.** `vkCmdBlitImage` requires source and destination formats to be in the same class: both signed or unsigned integer for integer formats, or both sampled as floats for float, unorm, snorm, uscaled, sscaled, and srgb classes. The `all_formats.color` matrix iterates source formats against a per-class compatible destination list.
- **Mirror mode.** A blit region's mirror mode is derived from the offset pairs: if the destination offsets are reversed relative to the source offsets along an axis, that axis is mirrored. The host reference calls `getMirrorMode()` and `flipCoordinates()` before `tcu::scale` so the CPU reference matches the implementation's flipped image.
- **Compressed source and destination.** Compressed formats (ASTC, BC, ETC, EAC) are decompressed on the host into a `tcu::PixelBufferAccess` and compared as decompressed images. `CompressedTextureForBlit` ensures every block is valid so the framework's decompression does not assert: ASTC uses `generateRandomValidBlocks`, BC6H uses predefined valid blocks in `<-1; 1>` or `<0; 1>`, BC7 forces every block's mode byte to be non-zero, and ETC1 skips random data.
- **Mipmap generation via blits.** The `generate_mipmaps` intermediate node blits between mip levels of the same image. `from_base_level` blits from level 0 to every other level in a single command; `from_previous_level` blits each level from the previous one with a pipeline barrier between levels, so the verification recomputes the expected result for level N from the verified result of level N-1.

## Registration Hierarchy

```text
api.copy_and_blit.core
└── blit_image
api.copy_and_blit.dedicated_allocation
└── blit_image
api.copy_and_blit.copy_commands2
└── blit_image
```

Each parent calls `addBlittingImageTests()` with a different `allocationKind` and `extensionFlags` and produces the same `simple_tests` / `all_formats` subtree. The parent context only changes allocation kind and command variant: `core` uses `ALLOCATION_KIND_SUBALLOCATED` with `vkCmdBlitImage`; `dedicated_allocation` uses `ALLOCATION_KIND_DEDICATED` with `vkCmdBlitImage`; `copy_commands2` uses `ALLOCATION_KIND_SUBALLOCATED` with `vkCmdBlitImage2` (requires `VK_KHR_copy_commands2`). Mustpass evidence for the `core` variant starts at [`api.txt#L44916`](../../../mustpass/main/vk-default/api.txt#L44916) for `all_formats.color.1d` and at [`api.txt#L174079`](../../../mustpass/main/vk-default/api.txt#L174079) for `simple_tests.whole`. The `dedicated_allocation` variant starts at [`api.txt#L234705`](../../../mustpass/main/vk-default/api.txt#L234705) and the `copy_commands2` variant starts at [`api.txt#L4606`](../../../mustpass/main/vk-default/api.txt#L4606).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Parent context | `core`, `dedicated_allocation`, `copy_commands2` | Selects `ALLOCATION_KIND_SUBALLOCATED` (core, copy_commands2) or `ALLOCATION_KIND_DEDICATED` (dedicated_allocation), and the default `vkCmdBlitImage` path or `vkCmdBlitImage2` (`COPY_COMMANDS_2`). | [`vktApiCopiesAndBlittingTests.cpp#L136`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136) |
| Top-level subgroup | `simple_tests`, `all_formats` | `simple_tests` uses a fixed `VK_FORMAT_R8G8B8A8_UNORM` source and varies the region geometry. `all_formats` varies the source and destination formats across color, depth/stencil, and mipmap matrices. | [`vktApiBlittingTests.cpp#L4119-L4120`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4119-L4120) |
| Image type (simple_tests) | 2D (`whole`, `array`, `mirror_xy`, `mirror_x`, `mirror_y`, `mirror_subregions`, `scaling_whole1`, `scaling_whole2`, `scaling_and_offset`, `without_scaling_partial`), 3D (`*_3d` variants plus `mirror_z_3d`), 3D-to-2D-array (`3d_to_2d_array`) | Selects `VK_IMAGE_TYPE_2D` or `VK_IMAGE_TYPE_3D`; `3d_to_2d_array` uses a 3D source and a 2D-array destination. | [`vktApiBlittingTests.cpp#L2755-L2786`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2755-L2786) |
| Filter | `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR`, `VK_FILTER_CUBIC_EXT` | Nearest uses exact-with-threshold comparison. Linear and cubic use clamped and unclamped references with thresholds multiplied by 1.5 for cubic. Cubic is restricted to 2D images. | [`vktApiBlittingTests.cpp#L2197-L2241`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2197-L2241) |
| Format class (all_formats.color) | `compatibleFormatsUInts`, `compatibleFormatsSInts`, `compatibleFormatsFloats`, `compatibleFormatsSrgb`, `compressedFormatsFloats`, `compressedFormatsSrgb` | Iterates source formats per class and pairs each with every compatible destination format. Integer classes are tested with `onlyNearest = true`; float and srgb classes also test linear and cubic. | [`vktApiBlittingTests.cpp#L3205-L3217`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3205-L3217) |
| Image dimensionality (all_formats.color) | `1d`, `2d`, `3d` | 2D uses `defaultExtent`; 1D uses `default1dExtent`; 3D uses `default3dExtent` and adds the ASTC 3D format list when `VK_EXT_texture_compression_astc_3d` is available. | [`vktApiBlittingTests.cpp#L3228-L3432`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3228-L3432) |
| Tiling (all_formats.color) | `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_TILING_LINEAR` | Both source and destination tilings are iterated. Linear tiling is restricted to a subset of formats and skips `LINEAR + TRANSFER_*_OPTIMAL` combinations. | [`vktApiBlittingTests.cpp#L2900-L2941`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2900-L2941) |
| Layout (all_formats.color, depth_stencil, mipmaps) | `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` / `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` | Both source and destination layouts are iterated; the leaf name encodes the pair as `<src>_<dst>_<filter>`, where each side is `general` or `optimal` (the layout name, for `VK_IMAGE_TILING_OPTIMAL`) or `linear` (for `VK_IMAGE_TILING_LINEAR`, ignoring the layout); for example, `general_general_linear`. | [`vktApiBlittingTests.cpp#L2904-L2909`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2904-L2909) |
| Format (all_formats.depth_stencil) | `VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_S8_UINT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` | Iterates the standard depth/stencil format list. Depth-only and stencil-only formats use a single aspect; combined formats also register a `_separate_layouts` leaf that uses `SEPARATE_DEPTH_STENCIL_LAYOUT`. | [`vktApiBlittingTests.cpp#L3470-L3497`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3470-L3497) |
| Mipmap variant (generate_mipmaps) | `from_base_level` (single command, all levels), `from_previous_level` (per-level command with barriers) | `from_base_level` sets `singleCommand = true`; `from_previous_level` sets `singleCommand = false` and registers `mipbarriercount_*` and `layerbarriercount_*` subgroups that vary `barrierCount`. | [`vktApiBlittingTests.cpp#L3849-L4050`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3849-L4050) |
| Layer count (mipmaps) | `1`, `6` | Mipmap tests register both single-layer and 6-layer (`cube`) variants. | [`vktApiBlittingTests.cpp#L3863`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3863) |
| Extension flags | `NONE`, `COPY_COMMANDS_2`, `MAINTENANCE_5` (array leaves), `MAINTENANCE_8` (3d_to_2d_array), `SEPARATE_DEPTH_STENCIL_LAYOUT` (combined depth/stencil) | Gates the corresponding Vulkan extension in `checkSupport`. | [`vktApiBlittingTests.cpp#L2287`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2287), [`vktApiBlittingTests.cpp#L2366`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2366), [`vktApiBlittingTests.cpp#L3683`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3683) |

## Behavior Parameters

The primary behavioral axis is the leaf cluster under `simple_tests` and the intermediate node under `all_formats`. Each cluster stresses a different field of `VkImageBlit` or a different format/filter dimension.

### `simple_tests` clusters: region geometry

The `simple_tests` subgroup uses a fixed `VK_FORMAT_R8G8B8A8_UNORM` source and varies the blit region geometry across 2D, 3D, and 3D-to-2D-array image types. Each cluster registers `nearest`, `linear`, and (for 2D only) `cubic` leaves, plus `b8g8r8a8_unorm_*` and `r32_sfloat_*` destination-format variants. Source: [`vktApiBlittingTests.cpp#L2193-L2242`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2193-L2242).

### `whole`: whole-image blit, no scaling, no mirroring

The simplest blit: one region covering the entire source mapped to the entire destination with `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR`, or `VK_FILTER_CUBIC_EXT`. Registered for 2D (`whole`) and 3D (`whole_3d`). A failure here points to basic `vkCmdBlitImage` dispatch or filter implementation, before any geometry handling is exercised. Source: [`vktApiBlittingTests.cpp#L2244-L2269`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2244-L2269).

### `array`: `VK_REMAINING_ARRAY_LAYERS` resolution

Blits a 16-layer array image with `imageSubresource.layerCount = VK_REMAINING_ARRAY_LAYERS`. `all_remaining_layers` starts at base layer 0; `not_all_remaining_layers` starts at base layer 2. Both add `MAINTENANCE_5` to the extension flags so `checkSupport` gates `VK_KHR_maintenance5`. A failure on `not_all_remaining_layers` while `all_remaining_layers` passes indicates a base-layer-dependent resolution bug. Source: [`vktApiBlittingTests.cpp#L2271-L2347`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2271-L2347).

### `mirror_x`, `mirror_y`, `mirror_xy`, `mirror_subregions`: 2D mirroring

Reverses the destination offsets along one or both axes so the implementation must flip the image. `mirror_subregions` blits multiple smaller mirrored subregions rather than the whole image. A failure points to mirror-axis handling or to the host reference's `flipCoordinates` path. The `*_3d` variants exercise the same flips on 3D images. Source: [`vktApiBlittingTests.cpp#L2441-L2620`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2441-L2620).

### `mirror_z_3d`: 3D-only Z-axis mirroring

Reverses the destination Z offsets so the implementation must flip the image along Z. This leaf exists only for 3D images because 2D images have no Z axis. A failure points to Z-axis mirror handling. Source: [`vktApiBlittingTests.cpp#L2522-L2548`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2522-L2548).

### `scaling_whole1`, `scaling_whole2`: 2x downscale and upscale

`scaling_whole1` maps a `defaultSize` source to a `defaultHalfSize` destination (downscale 2x). `scaling_whole2` maps a `defaultHalfSize` source to a `defaultSize` destination (upscale 2x). Both exercise the sample-position computation when source and destination extents differ. The `*_3d` variants do the same for 3D images. A failure points to sample-position arithmetic for the chosen filter. Source: [`vktApiBlittingTests.cpp#L2622-L2676`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2622-L2676).

### `scaling_and_offset`: scaling with non-zero offsets

Maps a source subregion with non-zero offsets to a destination subregion covering the whole destination. Combines sample-position computation with non-zero `srcOffset`. A failure points to offset-aware sample-position arithmetic. Source: [`vktApiBlittingTests.cpp#L2678-L2706`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2678-L2706).

### `without_scaling_partial`: multiple non-overlapping subregions, no scaling

Blits several shrinking-square subregions with no scaling. A failure points to multi-region dispatch or per-region offset handling. Source: [`vktApiBlittingTests.cpp#L2708-L2743`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2708-L2743).

### `3d_to_2d_array`: 3D-to-2D-array slice mapping

Blits slices of a 3D source into layers of a 2D-array destination. `cube_slice` blits a single slice into a 6-layer cube; `single_slices` blits four slices into four layers; `complex_blit` blits a slice into a smaller subregion of a cube layer. Adds `MAINTENANCE_8` and requires `VK_KHR_maintenance8`. A failure points to 3D-Z-to-array-layer mapping. Source: [`vktApiBlittingTests.cpp#L2355-L2439`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2355-L2439).

### `all_formats.color`: color format conversion

Iterates source formats across six format classes (uint, sint, float, srgb, compressed float, compressed srgb) and pairs each with every compatible destination format. Tests 1D, 2D, and 3D images with both optimal and linear tilings and both `TRANSFER_*_OPTIMAL` and `GENERAL` layouts. 3D non-compressed sources also register `_linear_stripes_x/y/z` and `_nearest_stripes_x/y/z` leaves that use `FILL_MODE_BLUE_RED_X/Y/Z` to expose axis-dependent scaling bugs. A failure points to format conversion, tiling, or layout handling for the failing src×dst pair. Source: [`vktApiBlittingTests.cpp#L3202-L3433`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3202-L3433).

### `all_formats.depth_stencil`: depth/stencil aspect separation

Iterates the standard depth/stencil format list for 1D, 2D, and 3D images. Depth-only and stencil-only formats use a single aspect; combined formats register an extra `_separate_layouts` leaf that uses `SEPARATE_DEPTH_STENCIL_LAYOUT` and `VK_EXT_separate_depth_stencil_layouts`-style barriers. A failure points to depth/stencil aspect separation, separate layout handling, or depth/stencil blit support for the failing format. Source: [`vktApiBlittingTests.cpp#L3458-L3815`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3458-L3815).

### `all_formats.generate_mipmaps`: mipmap generation via blits

Blits between mip levels of the same image. `from_base_level` blits from level 0 to every other level in a single command; `from_previous_level` blits each level from the previous one with a pipeline barrier between levels. Both register `layercount_1` and `layercount_6` subgroups. `from_previous_level` registers the extra `mipbarriercount_*` and `layerbarriercount_*` subgroups that vary `barrierCount`. A failure on `from_previous_level` while `from_base_level` passes can indicate a per-level barrier or layout transition bug. Source: [`vktApiBlittingTests.cpp#L3849-L4050`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3849-L4050), [`vktApiBlittingTests.cpp#L4099-L4106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4099-L4106).

## Shader Analysis

No shader is involved in this test family. All work is recorded by the host through `vkCmdBlitImage` or `vkCmdBlitImage2`, and the result is validated by host-side reference comparison. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

- The host creates the source `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, the requested format, tiling, and image type. When `useSparseBinding` is set, the image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and bound through `allocateAndBindSparseImage` with a sparse semaphore; otherwise it is bound through the regular allocator. The dispatcher does not set `useSparseBinding` for the `blit_image` subgroup, so the sparse path is supported by the class but not exercised by registered cases. See [`vktApiBlittingTests.cpp#L243-L335`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L243-L335).
- The host creates the destination `VkImage` with the same usage flags. For the mipmap variant, the destination owns `m_params.mipLevels` levels. See [`vktApiBlittingTests.cpp#L1436-L1463`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1436-L1463).
- The host fills the source with a deterministic pattern via `generateBuffer` and uploads it. For compressed sources, `CompressedTextureForBlit` generates valid-block compressed data and uploads the compressed bytes through a staging buffer; the host also decompresses the data into a `tcu::PixelBufferAccess` for the reference. See [`vktApiBlittingTests.cpp#L372-L409`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L372-L409), [`vktApiBlittingTests.cpp#L1135-L1255`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1135-L1255).
- The host fills the destination with a different pattern so untouched texels are distinguishable, then uploads it. See [`vktApiBlittingTests.cpp#L400-L409`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L400-L409).
- The expected image is computed on the host by `generateExpectedResult`, which calls `copyRegionToTextureLevel` for each region. `copyRegionToTextureLevel` derives the mirror mode with `getMirrorMode`, calls `flipCoordinates`, then invokes `tcu::scale` (for depth) or `tcu::blit` (for stencil and color) with the chosen filter. For non-nearest filters it computes an unclamped reference via `scaleFromWholeSrcBuffer` that samples from the whole source buffer rather than the subregion. See [`vktApiBlittingTests.cpp#L990-L1133`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L990-L1133).
- A command buffer records pipeline barriers into the requested operation layouts (`TRANSFER_SRC_OPTIMAL` / `TRANSFER_DST_OPTIMAL` or `GENERAL`), then one of the two blit commands:
  - `vk.cmdBlitImage` for the default and `dedicated_allocation` paths, [`vktApiBlittingTests.cpp#L454-L458`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L454-L458);
  - `vk.cmdBlitImage2` with a `VkBlitImageInfo2KHR` for `copy_commands2`, [`vktApiBlittingTests.cpp#L459-L474`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L459-L474).
- For the mipmap variant, the host records either a single multi-region blit (`singleCommand = true`, `from_base_level`) or one blit per mip level with a pipeline barrier between levels (`singleCommand = false`, `from_previous_level`). The per-level barrier uses `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS` depending on whether the image is single-layer or multi-layer. See [`vktApiBlittingTests.cpp#L1508-L1726`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1508-L1726).
- The command buffer is submitted and the host waits. For sparse cases the sparse semaphore is included in the wait; otherwise the standard submit-and-wait path is used. See [`vktApiBlittingTests.cpp#L476-L478`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L476-L478).
- The host reads the destination back via `readImage`. If the destination is compressed, the host decompresses the result before comparison. See [`vktApiBlittingTests.cpp#L482-L498`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L482-L498).
- `checkTestResult` dispatches to one of four checks based on filter and source format:
  - `checkNearestFilteredResult` for `VK_FILTER_NEAREST` with non-compressed sources, [`vktApiBlittingTests.cpp#L688-L744`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L688-L744);
  - `checkNonNearestFilteredResult` for `VK_FILTER_LINEAR` / `VK_FILTER_CUBIC_EXT` with non-compressed sources, [`vktApiBlittingTests.cpp#L501-L580`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L501-L580);
  - `checkCompressedNearestFilteredResult` for `VK_FILTER_NEAREST` with compressed sources, [`vktApiBlittingTests.cpp#L746-L873`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L746-L873);
  - `checkCompressedNonNearestFilteredResult` for `VK_FILTER_LINEAR` / `VK_FILTER_CUBIC_EXT` with compressed sources, [`vktApiBlittingTests.cpp#L582-L686`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L582-L686).
- For depth/stencil formats, the result is split into depth and stencil aspects via `getEffectiveDepthStencilAccess` before each check. See [`vktApiBlittingTests.cpp#L900-L985`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L900-L985).
- For the mipmap variant, each mip level is read back and compared independently. In `from_previous_level`, the expected result for level N is recomputed from the verified result of level N-1 so accumulated error does not exceed the fixed threshold. See [`vktApiBlittingTests.cpp#L1737-L1800`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1737-L1800).
- The pass condition is `tcu::TestStatus::pass("Pass")` only if every aspect and every level is within threshold. A single failing texel produces `tcu::TestStatus::fail("Result image is incorrect")`.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|------------------------------|----------------|---------------|---------------|------|
| Source `VkImage` | Yes | Yes (transfer source) | Read by the blit command | No | Holds the source texels; supports sparse binding through `m_sparseSemaphore`. |
| Destination `VkImage` | Yes | Yes (transfer destination) | Written by the blit command | Yes, via `readImage` | Receives the blitted texels; for the mipmap variant it owns multiple mip levels. |
| Source `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the reference source | Host-side source used by `copyRegionToTextureLevel` to compute the expected result. |
| Expected `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the comparison reference | Host-computed oracle produced by `generateExpectedResult`. |
| Unclamped expected `tcu::TextureLevel` | Yes, on the host (LINEAR/CUBIC only) | No | No | Yes, as the fallback reference | Computed by `scaleFromWholeSrcBuffer` from the whole source buffer; used when the clamped reference fails. |
| Compressed source `CompressedTextureForBlit` | Yes, on the host | No | No | Yes, decompressed for comparison | Provides valid-block compressed data and its host decompression for the reference. |
| Sparse semaphore | Yes, when `useSparseBinding` is set | Yes | No | No | Synchronizes sparse memory binding with the blit submission. Not exercised by registered cases. |

## Failure Meaning

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
| `3d_to_2d_array` (`cube_slice`, `single_slices`, `complex_blit`) | 3D-to-2D-array slice mapping with `MAINTENANCE_8`; requires `VK_KHR_maintenance8`. |
| `all_formats.color.*` | Format conversion between source and destination color formats; integer/float/srgb/compressed class handling and tiling/layout combinations. |
| `all_formats.depth_stencil.*` | Depth/stencil aspect separation, separate depth/stencil layouts (`SEPARATE_DEPTH_STENCIL_LAYOUT`), and 1D/2D/3D depth/stencil blits. |
| `all_formats.generate_mipmaps.from_base_level` | Single-command mipmap generation from level 0 to all levels. |
| `all_formats.generate_mipmaps.from_previous_level` | Per-level mipmap generation with pipeline barriers between levels; accumulated error across levels. |
| All leaves under `dedicated_allocation.blit_image.*` | Dedicated-allocation memory binding for source or destination image. |
| All leaves under `copy_commands2.blit_image.*` | `vkCmdBlitImage2KHR` / `VkImageBlit2KHR` struct conversion or dispatch. |
| All leaves with `_linear` or `_cubic` suffix | Linear or cubic filter implementation, including `VK_EXT_filter_cubic` for cubic. |
| All leaves with `_stripes_*` suffix (3D color only) | Stripe fill patterns (`FILL_MODE_BLUE_RED_X/Y/Z`) used to expose axis-dependent scaling bugs in 3D. |

### Cause Analysis

#### Whole-image blit dispatch

**Possible failure symptoms:** The `whole` (2D) or `whole_3d` leaf fails: one or more texels in the read-back image differ from the expected texture level, even though the region covers the entire source mapped to the entire destination with no scaling and no mirroring. The mismatch may affect every texel or appear as a shifted stripe. See [`vktApiBlittingTests.cpp#L990-L1106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L990-L1106) for the host reference and [`vktApiBlittingTests.cpp#L688-L744`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L688-L744) for the nearest check.

**Possible implementation causes:** Per Vulkan spec, `vkCmdBlitImage` samples the source subregion and writes the resampled texels into the destination subregion. With `VK_FILTER_NEAREST` and identical source/destination extents, the implementation must copy each source texel to the corresponding destination texel. A driver that miscomputes the sample position even for the identity scaling, or that mishandles the source/destination image layout transition in the pipeline barrier, would produce this symptom. A failure only on `_linear` or `_cubic` variants of `whole` points to the linear or cubic filter implementation rather than the dispatch. Source-level investigation is needed to pinpoint whether the failure is in sample-position arithmetic, filter weighting, or layout transition.

#### VK_REMAINING_ARRAY_LAYERS resolution

**Possible failure symptoms:** `all_remaining_layers` or `not_all_remaining_layers` fails: the layers covered by `VK_REMAINING_ARRAY_LAYERS` are not all blitted, or the blitted range starts at the wrong base layer. `not_all_remaining_layers` may fail while `all_remaining_layers` passes, indicating a base-layer-dependent resolution bug.

**Possible implementation causes:** Per `VK_KHR_maintenance5`, `VK_REMAINING_ARRAY_LAYERS` resolves to `arrayLayers - baseArrayLayer`. A driver that resolves the value to the full `arrayLayers` count regardless of `baseArrayLayer`, or that does not implement the maintenance5 resolution at all, would produce this symptom. The test sets `MAINTENANCE_5` in `extensionFlags` for these leaves so `checkSupport` gates the extension. Source-level investigation is needed to confirm whether the failure is in the resolution arithmetic or in the extension wiring.

#### Mirror-axis handling

**Possible failure symptoms:** A `mirror_*` leaf fails while the corresponding non-mirrored `whole` leaf passes: the read-back image is not flipped along the expected axis or axes. The mismatch may be a complete copy of the unflipped source, a partial flip, or a flip along the wrong axis. For `mirror_z_3d`, the failure is specific to the Z axis.

**Possible implementation causes:** Per Vulkan spec, when the destination offsets are reversed relative to the source offsets along an axis, the implementation must mirror the source along that axis. The host reference calls `getMirrorMode` and `flipCoordinates` before `tcu::scale` so the CPU reference produces the same flipped image. A driver that ignores the reversed offsets, mirrors along the wrong axis, or applies the mirror only to a subset of the region would produce this symptom. The host reference path is shared between 2D and 3D, so a 2D-only failure points to the implementation rather than the reference. Source-level investigation is needed to confirm which axis is mishandled.

#### Scaling sample-position computation

**Possible failure symptoms:** `scaling_whole1` (downscale), `scaling_whole2` (upscale), or `scaling_and_offset` fails: the resampled destination texels differ from the CPU reference. For `VK_FILTER_NEAREST`, the mismatch is a wrong source texel picked per destination texel; for `VK_FILTER_LINEAR` or `VK_FILTER_CUBIC_EXT`, the mismatch is a wrong blend of source texels. `scaling_and_offset` may fail while `scaling_whole1` and `scaling_whole2` pass, indicating an offset-aware bug.

**Possible implementation causes:** Per Vulkan spec, when source and destination extents differ, the implementation must compute source sample positions from the destination texel coordinates using the formula `(dst + 0.5) * (srcExtent / dstExtent) - 0.5` (or an equivalent form). A driver that uses a different rounding for `VK_FILTER_NEAREST`, that uses a wrong origin for `VK_FILTER_LINEAR`, or that ignores `srcOffset` when computing sample positions would produce this symptom. The `_linear_stripes_*` and `_nearest_stripes_*` leaves for 3D color use stripe fill patterns to expose axis-dependent sample-position bugs; a failure on `_stripes_x` but not `_stripes_y` points to an X-axis-specific scaling bug. Source-level investigation is needed to pinpoint the failing axis and filter combination.

#### Multi-region dispatch

**Possible failure symptoms:** `without_scaling_partial` or `mirror_subregions` fails: one or more of the shrinking-square subregions in the destination image does not match the expected texels, while single-region leaves with the same filter pass. The mismatch may affect only some of the regions in the command.

**Possible implementation causes:** The test records one blit command with multiple `VkImageBlit` regions. The implementation must dispatch each region independently using its own `srcOffsets`, `dstOffsets`, and `srcSubresource` / `dstSubresource`. A driver that reuses a single region's parameters for multiple regions, or that miscomputes the per-region offset, would produce this symptom. For the `copy_commands2` variant, the regions are converted to `VkImageBlit2KHR` before dispatch; a struct-conversion bug that drops or reorders a region would also produce this symptom. Source-level investigation is needed to confirm whether the failure is in region iteration or in struct conversion.

#### 3D-to-2D-array slice mapping

**Possible failure symptoms:** Any `3d_to_2d_array` leaf (`cube_slice`, `single_slices`, `complex_blit`) fails: the destination array layers do not contain the expected slices of the 3D source. The mismatch may affect a single layer, a subset of layers, or all layers.

**Possible implementation causes:** The test uses a 3D source and a 2D-array destination, blitting Z slices of the source into array layers of the destination via `make3Dto2DArrayBlit`. Per `VK_KHR_maintenance8`, the implementation must map the source Z range to the destination `baseArrayLayer` / `layerCount`. A driver that miscomputes the slice-to-layer mapping, ignores `dstSubresource.baseArrayLayer`, or applies the source Z range to the destination Z axis instead of the array layers would produce this symptom. The test adds `MAINTENANCE_8` to the extension flags so `checkSupport` gates the extension. Source-level investigation is needed to confirm whether the failure is in slice-to-layer mapping or in the maintenance8 wiring.

#### Color format conversion

**Possible failure symptoms:** An `all_formats.color.*` leaf fails: the destination texels differ from the CPU reference for a specific src×dst format pair. The mismatch may be a value-conversion error (for example, UNORM-to-SRGB) or a class-mismatch error (for example, integer source sampled as float).

**Possible implementation causes:** Per Vulkan spec, `vkCmdBlitImage` requires source and destination formats to be in the same compatibility class. The test iterates source formats against a per-class compatible destination list, so an incompatible pair should not be registered; if it is registered, the framework's `isSupportedByFramework` check skips it. A driver that miscomputes the value conversion between two compatible formats (for example, rounding UNORM to UNORM_SRGB incorrectly), or that accepts an incompatible pair that the framework should have skipped, would produce this symptom. For compressed sources, the comparison uses decompressed references with an `acceptedError` of 0.04 (nearest) or 0.06 (non-nearest) plus `getCompressedFormatThreshold`; a failure just outside that threshold may indicate the decompression reference is slightly off rather than the blit. BC6H and ASTC SFLOAT sources may be clamped to `<-1; 1>` or `<0; 1>` for non-float destinations to match what the device produces. Source-level investigation is needed to confirm whether the failure is in the value conversion, in the compatibility check, or in the decompression reference.

#### Depth/stencil aspect separation

**Possible failure symptoms:** An `all_formats.depth_stencil.*` leaf fails: the depth aspect, the stencil aspect, or both differ from the CPU reference. The `_separate_layouts` variant may fail while the combined-layout variant passes, indicating a separate-depth-stencil-layout bug.

**Possible implementation causes:** For combined depth/stencil formats, the test splits the result into depth and stencil aspects via `getEffectiveDepthStencilAccess` before each check. A driver that blits only one aspect, that blits the wrong aspect, or that mishandles `VK_IMAGE_ASPECT_DEPTH_BIT | VK_IMAGE_ASPECT_STENCIL_BIT` as a combined aspect when the test expects separate aspects would produce this symptom. The `_separate_layouts` leaves add `SEPARATE_DEPTH_STENCIL_LAYOUT` and use separate depth and stencil layouts in the pipeline barrier; a driver that does not support `VK_EXT_separate_depth_stencil_layouts` for blits would produce this symptom. Source-level investigation is needed to confirm whether the failure is in aspect separation, in separate layout handling, or in depth/stencil blit support for the failing format.

#### Mipmap generation

**Possible failure symptoms:** An `all_formats.generate_mipmaps.*` leaf fails: one or more mip levels differ from the CPU reference. `from_previous_level` may fail while `from_base_level` passes, indicating a per-level barrier or accumulated-error issue.

**Possible implementation causes:** For `from_base_level`, the test records a single blit command with one region per mip level. A driver that does not dispatch all regions in a single command, or that miscomputes the per-level destination extent, would produce this symptom. For `from_previous_level`, the test records one blit per level with a pipeline barrier between levels; the verification recomputes the expected result for level N from the verified result of level N-1 so accumulated error does not exceed the fixed threshold. A driver that does not insert the correct barrier between levels, that reads level N-1 before it is written, or that accumulates error beyond the threshold would produce this symptom. The `mipbarriercount_*` and `layerbarriercount_*` subgroups vary `barrierCount` to exercise different barrier subresource ranges; a failure on a specific `barrierCount` points to the barrier subresource-range computation. Source-level investigation is needed to confirm whether the failure is in multi-region dispatch, in per-level barriers, or in accumulated error handling.

#### Dedicated allocation memory binding

**Possible failure symptoms:** All leaves under `dedicated_allocation.blit_image.*` fail (or a subset fails), while the corresponding `core.blit_image.*` leaves pass.

**Possible implementation causes:** The dispatcher uses `ALLOCATION_KIND_DEDICATED` for this parent context, which creates a dedicated `VkDeviceMemory` object for the source and destination images. A driver that does not correctly bind memory for dedicated allocations, or that exposes different image format properties under dedicated allocation, would produce this symptom. The `dedicatedAllocationBlittingFormatsToTest` list restricts the format set for the dedicated-allocation variant to a representative subset, so a format-specific failure under `core` may not appear under `dedicated_allocation` because the format is not in the subset. Source-level investigation is needed to confirm whether the failure is in allocation, binding, or format-property reporting.

#### vkCmdBlitImage2KHR struct conversion

**Possible failure symptoms:** All leaves under `copy_commands2.blit_image.*` fail (or a subset fails), while the corresponding `core.blit_image.*` leaves pass. The failure is specific to the `COPY_COMMANDS_2` command path.

**Possible implementation causes:** The test converts each `VkImageBlit` to a `VkImageBlit2KHR` and dispatches via `vk.cmdBlitImage2` with a `VkBlitImageInfo2KHR`. Per `VK_KHR_copy_commands2`, the two command forms must produce identical results. A driver that mishandles the struct conversion, drops a region, or applies the wrong layout in the `VkBlitImageInfo2KHR` would produce this symptom. Source-level investigation is needed to confirm whether the failure is in struct conversion or in the driver's `vkCmdBlitImage2KHR` implementation.

#### Linear and cubic filter implementation

**Possible failure symptoms:** All `_linear` or `_cubic` variants of a leaf fail while the `_nearest` variant passes. For cubic, the failure is specific to 2D images because cubic is restricted to 2D.

**Possible implementation causes:** Per Vulkan spec, `VK_FILTER_LINEAR` blends source texels with linear weights, and `VK_FILTER_CUBIC_EXT` blends with cubic weights. The test accepts either a clamped reference (subregion only) or an unclamped reference (whole source buffer) to tolerate edge-clamp sampling. A driver that uses the wrong filter weights, that does not clamp edges correctly, or that does not support `VK_EXT_filter_cubic` for the source format would produce this symptom. For cubic, `checkSupport` gates `VK_EXT_filter_cubic` and the `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_CUBIC_BIT_EXT` format feature. Source-level investigation is needed to confirm whether the failure is in filter weighting, in edge clamping, or in extension support.

## Case Pruning

### Requirement-based pruning

- `COPY_COMMANDS_2` cases require `VK_KHR_copy_commands2`. `MAINTENANCE_5` cases require `VK_KHR_maintenance5`. `MAINTENANCE_8` cases require `VK_KHR_maintenance8`. `SEPARATE_DEPTH_STENCIL_LAYOUT` cases require `VK_EXT_separate_depth_stencil_layouts`. `checkExtensionSupport` throws `NotSupportedError` when an extension is missing. See [`vktApiBlittingTests.cpp#L1301`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1301), [`vktApiBlittingTests.cpp#L1341`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1341).
- `VK_FILTER_CUBIC_EXT` cases require `VK_EXT_filter_cubic` and `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_CUBIC_BIT_EXT` on the source format. See [`vktApiBlittingTests.cpp#L1331-L1339`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1331-L1339).
- `VK_FILTER_LINEAR` cases require `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` on the source format. See [`vktApiBlittingTests.cpp#L1325-L1329`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1325-L1329).
- The source and destination formats must support `VK_FORMAT_FEATURE_BLIT_SRC_BIT` and `VK_FORMAT_FEATURE_BLIT_DST_BIT` respectively, for the requested tiling. See [`vktApiBlittingTests.cpp#L1303-L1323`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1303-L1323).
- `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` cases require `VK_KHR_maintenance5`. ASTC 3D formats require `VK_EXT_texture_compression_astc_3d`. See [`vktApiBlittingTests.cpp#L1274-L1283`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1274-L1283).
- The destination image's `maxMipLevels` must be greater than or equal to the requested `mipLevels` for mipmap cases. See [`vktApiBlittingTests.cpp#L2152-L2155`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2152-L2155).
- The mipmap variant's `from_previous_level` `mipbarriercount_*` and `layerbarriercount_*` subgroups are registered only for a few common `compatibleFormatsUInts` formats (indices 2-5). See [`vktApiBlittingTests.cpp#L4067-L4093`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4067-L4093).

### Design-based pruning

- Cubic filtering is restricted to 2D images. The `addBlittingImageSimpleTests` registrar gates cubic on `params.dst.image.imageType == VK_IMAGE_TYPE_2D`, and the 1D and 3D color registrations force `onlyNearestAndLinear = true`. See [`vktApiBlittingTests.cpp#L2229`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2229), [`vktApiBlittingTests.cpp#L3335`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3335), [`vktApiBlittingTests.cpp#L3405`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3405).
- Linear tiling is restricted to a subset of formats (`linearOtherImageFormatsToTest`) and skips `LINEAR + TRANSFER_*_OPTIMAL` combinations because they are assumed to behave like `LINEAR + GENERAL`. See [`vktApiBlittingTests.cpp#L2834-L2848`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2834-L2848), [`vktApiBlittingTests.cpp#L2919-L2941`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2919-L2941).
- The `dedicated_allocation` variant restricts the format set to `dedicatedAllocationBlittingFormatsToTest` (a representative subset) to keep the dedicated-allocation matrix manageable. See [`vktApiBlittingTests.cpp#L2819-L2832`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2819-L2832), [`vktApiBlittingTests.cpp#L3048-L3064`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3048-L3064).
- ASTC HDR source formats are skipped in the `all_formats.color` destination iteration because they would be added as a consequence of `isCompressedFormat`; the comment notes that the check can be removed if those combinations are desired. See [`vktApiBlittingTests.cpp#L3031-L3045`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3031-L3045).
- The `_stripes_*` leaves are registered only for 3D non-compressed sources, because 2D stripe patterns do not expose axis-dependent scaling bugs. See [`vktApiBlittingTests.cpp#L2964-L2992`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2964-L2992).
- Sparse binding is supported by the `BlittingImages` class through its base `CopiesAndBlittingTestInstanceWithSparseSemaphore`, but the dispatcher never sets `useSparseBinding = true` for the `blit_image` subgroup. No sparse blit cases are registered.

## Key Takeaways

- The family exercises two Vulkan command variants (`vkCmdBlitImage` and `vkCmdBlitImage2`) under three parent contexts (`core`, `dedicated_allocation`, `copy_commands2`), all sharing the same `simple_tests` / `all_formats` subtree and the same host-side reference comparison.
- The behavioral axis is the leaf cluster: `simple_tests` clusters vary the region geometry (whole, mirror, scaling, partial, 3D-to-2D-array), while `all_formats` clusters vary the format class (color, depth/stencil, mipmaps).
- The family exercises three filters: `VK_FILTER_NEAREST` (exact with format-specific thresholds), `VK_FILTER_LINEAR` (clamped and unclamped references), and `VK_FILTER_CUBIC_EXT` (cubic weights, 2D only, requires `VK_EXT_filter_cubic`).
- LINEAR and CUBIC compare against both clamped and unclamped references. A failure on the clamped reference can still pass on the unclamped reference, which means the implementation used edge-clamp sampling rather than sampling outside the source subregion.
- The `generate_mipmaps.from_previous_level` variant recomputes the expected result for level N from the verified result of level N-1, so accumulated error does not exceed the fixed threshold; a failure on `from_previous_level` while `from_base_level` passes points to per-level barriers or layout transitions rather than scaling.
- Failures localize differently: a failure only under `copy_commands2.*` points to the `vkCmdBlitImage2KHR` struct conversion; a failure only under `dedicated_allocation.*` points to dedicated-allocation memory binding; a failure only on `not_all_remaining_layers` points to `VK_REMAINING_ARRAY_LAYERS` resolution from a non-zero base; a failure only on `_cubic` variants points to the cubic filter implementation or `VK_EXT_filter_cubic` support; a failure only on `_stripes_x` (3D color) points to an X-axis-specific scaling bug. See `## Failure Meaning` for details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `BlittingImages` test instance class | [`vktApiBlittingTests.cpp#L171-L212`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L171-L212) | Owns source/destination images, sparse semaphore, expected texture level, and compressed texture helpers. |
| `BlittingImages` constructor | [`vktApiBlittingTests.cpp#L243-L335`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L243-L335) | Creates source and destination images; selects sparse or regular allocation path. |
| `BlittingImages::iterate()` | [`vktApiBlittingTests.cpp#L337-L499`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L337-L499) | Fills images, records the blit command variant, submits, reads back, and dispatches the check. |
| `BlittingImages::checkTestResult()` | [`vktApiBlittingTests.cpp#L892-L988`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L892-L988) | Selects nearest/non-nearest/compressed check based on filter and source format. |
| `checkNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L688-L744`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L688-L744) | Exact-with-threshold comparison for NEAREST. |
| `checkNonNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L501-L580`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L501-L580) | Threshold comparison against clamped and unclamped references for LINEAR/CUBIC. |
| `checkCompressedNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L746-L873`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L746-L873) | Nearest comparison with compressed-format thresholds and clamp ranges. |
| `checkCompressedNonNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L582-L686`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L582-L686) | Non-nearest comparison with compressed-format thresholds and clamp ranges. |
| `copyRegionToTextureLevel()` | [`vktApiBlittingTests.cpp#L990-L1106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L990-L1106) | Host reference computation; uses `getMirrorMode`, `flipCoordinates`, `tcu::scale`, `tcu::blit`, `scaleFromWholeSrcBuffer`. |
| `generateExpectedResult()` | [`vktApiBlittingTests.cpp#L1108-L1133`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1108-L1133) | Builds the expected and unclamped expected texture levels. |
| `uploadCompressedImage()` | [`vktApiBlittingTests.cpp#L1135-L1255`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1135-L1255) | Uploads compressed bytes through a staging buffer. |
| `CompressedTextureForBlit` constructor | [`vktApiBlittingTests.cpp#L56-L157`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L56-L157) | Generates valid-block compressed data for ASTC, BC6H, BC7, ETC. |
| `BlitImageTestCase::checkSupport()` | [`vktApiBlittingTests.cpp#L1271-L1342`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1271-L1342) | Gates `VK_KHR_maintenance5`, `VK_EXT_texture_compression_astc_3d`, `VK_EXT_filter_cubic`, format features, and `BLIT_SRC`/`BLIT_DST` support. |
| `BlittingMipmaps` class | [`vktApiBlittingTests.cpp#L1348-L1371`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1348-L1371) | Mipmap variant: owns a 16-level expected texture array and per-level unclamped references. |
| `BlittingMipmaps::iterate()` | [`vktApiBlittingTests.cpp#L1464-L1735`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1464-L1735) | Records either a single multi-region blit or one blit per level with barriers. |
| `BlittingMipmaps::checkNonNearestFilteredResult()` | [`vktApiBlittingTests.cpp#L1737-L1800`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1737-L1800) | Per-level recomputation of the expected result from the verified previous level. |
| `BlitMipmapTestCase::checkSupport()` | [`vktApiBlittingTests.cpp#L2118-L2187`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2118-L2187) | Gates mipmap-specific format support and `maxMipLevels`. |
| `addBlittingImageSimpleTests()` (registrar) | [`vktApiBlittingTests.cpp#L2745-L2787`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2745-L2787) | Registers the `simple_tests` subgroup tree (2D, 3D, 3D-to-2D-array). |
| `addBlittingImageAllFormatsColorTests()` | [`vktApiBlittingTests.cpp#L3202-L3433`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3202-L3433) | Registers the `all_formats.color` subgroup tree (1D, 2D, 3D, ASTC 3D). |
| `addBlittingImageAllFormatsDepthStencilTests()` | [`vktApiBlittingTests.cpp#L3458-L3815`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3458-L3815) | Registers the `all_formats.depth_stencil` subgroup tree (1D, 2D, 3D, separate layouts). |
| `addBlittingImageAllFormatsBaseLevelMipmapTests()` | [`vktApiBlittingTests.cpp#L3849-L3947`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3849-L3947) | Registers `from_base_level` with `singleCommand = true`. |
| `addBlittingImageAllFormatsPreviousLevelMipmapTests()` | [`vktApiBlittingTests.cpp#L3949-L4050`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L3949-L4050) | Registers `from_previous_level` with `singleCommand = false` and `barrierCount` variants. |
| `addBlittingImageAllFormatsMipmapTests()` | [`vktApiBlittingTests.cpp#L4099-L4106`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4099-L4106) | Adds `from_base_level` and `from_previous_level` under `generate_mipmaps`. |
| `addBlittingImageAllFormatsTests()` | [`vktApiBlittingTests.cpp#L4108-L4113`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4108-L4113) | Adds `color`, `depth_stencil`, and `generate_mipmaps` under `all_formats`. |
| `addBlittingImageTests()` (public entry) | [`vktApiBlittingTests.cpp#L4117-L4121`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4117-L4121) | Adds `simple_tests` and `all_formats` under `blit_image`. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L136`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136) | `blit_image` is added under `core`, `dedicated_allocation`, and `copy_commands2` parent contexts. |
| Top-level dispatcher | [`vktApiCopiesAndBlittingTests.cpp#L267-L293`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L267-L293) | Creates the `core`, `dedicated_allocation`, `copy_commands2`, `sparse`, and other groups under `copy_and_blit`. |
| Helper: `blit` and `scale` | [`vktApiCopiesAndBlittingUtil.hpp#L392-L397`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L392-L397) | CPU reference scaling and blitting used by `copyRegionToTextureLevel`. |
| Helper: `getMirrorMode` and `flipCoordinates` | [`vktApiCopiesAndBlittingUtil.hpp#L399-L405`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L399-L405) | Mirror-mode derivation and coordinate flipping for the host reference. |
| Mustpass evidence (`core`) | [`api.txt#L44916`](../../../mustpass/main/vk-default/api.txt#L44916) | Primary `core.blit_image` mustpass range; `simple_tests.whole` starts at [`api.txt#L174079`](../../../mustpass/main/vk-default/api.txt#L174079). |
| Mustpass evidence (`dedicated_allocation`) | [`api.txt#L234705`](../../../mustpass/main/vk-default/api.txt#L234705) | `dedicated_allocation.blit_image` mustpass range start. |
| Mustpass evidence (`copy_commands2`) | [`api.txt#L4606`](../../../mustpass/main/vk-default/api.txt#L4606) | `copy_commands2.blit_image` mustpass range start. |
