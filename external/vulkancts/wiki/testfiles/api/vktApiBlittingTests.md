# [vktApiBlittingTests.cpp](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1)

## Overview

Tests for `vkCmdBlitImage` and `vkCmdBlitImage2` (via `VK_KHR_copy_commands2`). Blitting differs from copying in that it supports scaling and filtering (nearest or linear). This file (~4107 lines) verifies that scaled image-to-image transfers via blit commands produce results consistent with CPU-side reference blitting.

## Role of File

Implementation-heavy test file for the `blit_image` subgroup. Contains test instance class, test case registration, and verification logic.

## Source Code

- Primary source: [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1)
- Header: [`vktApiBlittingTests.hpp`](../../../modules/vulkan/api/vktApiBlittingTests.hpp#L1)
- Parent-category registration: [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136)

## Registration Hierarchy

```text
api.copy_and_blit.core.blit_image
├── simple_tests
└── all_formats
```

The `blit_image` group is registered by [`addBlittingImageTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4100) and appears under multiple allocation/extension variant branches of `copy_and_blit`: `core`, `dedicated_allocation`, and `copy_commands2`. Each variant calls `addBlittingImageTests()` with different `allocationKind` and `extensionFlags` parameters, producing the same internal subgroup structure. The hierarchy tree above uses the `core` variant as the representative path.

Evidence:
- `blit_image` group added at [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136)
- subgroups added from [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4102) through [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4103)

## Test Families

### simple_tests — Simple blitting scenarios

The `simple_tests` subgroup at [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4102) is registered by [`addBlittingImageSimpleTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L2767). It tests blitting with a fixed format (`VK_FORMAT_R8G8B8A8_UNORM`) across various image types and blit configurations.

Direct children of `simple_tests`:

- **2D image blits**: `whole`, `array`, `mirror_xy`, `mirror_x`, `mirror_y`, `mirror_subregions`, `scaling_whole1`, `scaling_whole2`, `scaling_and_offset`, `without_scaling_partial`
- **3D image blits**: `whole_3d`, `mirror_xy_3d`, `mirror_x_3d`, `mirror_y_3d`, `mirror_z_3d`, `mirror_subregions_3d`, `scaling_whole1_3d`, `scaling_whole2_3d`, `scaling_and_offset_3d`, `without_scaling_partial_3d`
- **Cross-type blits**: `3d_to_2d_array`

Implementation: The [`BlittingImages`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L42) test instance class inherits [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L474), creates source and destination images with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, supports sparse binding via `m_sparseSemaphore`, and dispatches to `vkCmdBlitImage` or `vkCmdBlitImage2` depending on `extensionFlags`.

### all_formats — Format-specific blitting tests

The `all_formats` subgroup at [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4103) is registered by [`addBlittingImageAllFormatsTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4091). It tests blitting across a wide range of source and destination format combinations.

Direct children of `all_formats`:

- **color** — registered by [`addBlittingImageAllFormatsColorTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4093). Tests blitting across a wide range of color formats, iterating per source format and per compatible destination format. Uses `BlitColorTestParams` (extends `TestParams` with `compatibleFormats`) for format compatibility filtering.
- **depth_stencil** — registered by [`addBlittingImageAllFormatsDepthStencilTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4094). Tests blitting for depth/stencil formats.
- **generate_mipmaps** — registered by [`addBlittingImageAllFormatsMipmapTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4095). Tests mipmap level blitting with subgroups `from_base_level` and `from_previous_level`.

Compressed format handling: The [`CompressedTextureForBlit`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L42) helper class generates compressed texture data (ASTC, BC6H, ETC, etc.) with valid blocks, decompresses to a `tcu::PixelBufferAccess` for CPU-side reference comparison, and special-cases ASTC LDR/HDR and BC6H float formats with predefined valid blocks.

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Filter | `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR` |
| Mirror mode | X, Y, Z, XY combined, subregions |
| Scaling | Whole-to-whole, partial, with offsets, up-scaling, down-scaling |
| Image type | 2D, 3D-to-2D-array, array |
| Formats | Color formats (wide range), depth/stencil formats, compressed formats |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2` |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` |

## Support / Feature Requirements

- `COPY_COMMANDS_2` requires `VK_KHR_copy_commands2` or Vulkan 1.3
- Linear filtering requires `VK_FORMAT_FEATURE_BLIT_SRC_BIT` / `VK_FORMAT_FEATURE_BLIT_DST_BIT` with linear filter support
- Compressed format blits require format support on the device
- Depth/stencil blits may require `VK_FORMAT_FEATURE_BLIT_DST_BIT` for the specific format

## Verification Methods

- **Nearest-filtered**: [`checkNearestFilteredResult()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L175) performs exact comparison against source
- **Non-nearest-filtered**: [`checkNonNearestFilteredResult()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L171) performs threshold comparison with clamped and unclamped references
- **Compressed nearest**: `checkCompressedNearestFilteredResult()` with compressed format thresholds
- **Compressed non-nearest**: `checkCompressedNonNearestFilteredResult()` with compressed format thresholds
- CPU reference generated via [`blit()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L396) and [`scaleFromWholeSrcBuffer()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L392)
- Mirror mode handled by [`getMirrorMode()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L402) and [`flipCoordinates()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L399)
- Unclamped reference stored in `m_unclampedExpectedTextureLevel` for linear filter threshold comparison

## Test Principles

- Verify that blit operations with `VK_FILTER_NEAREST` produce exact pixel-level matches
- Verify that blit operations with `VK_FILTER_LINEAR` produce results within format-specific thresholds
- Verify mirroring (X, Y, Z) produces correctly flipped images
- Verify scaling (up and down) with both filter modes
- Verify compressed format blitting works correctly (decompressed comparison)
- Verify depth/stencil format blitting
- Verify mipmap level blitting (base level and previous level)

## Notes / Uncertainties

- The `CompressedTextureForBlit` class uses random data with special valid-block generation for BC6H and ASTC formats to avoid decompression errors, confirmed at [lines 56-143](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L56)
- The all-formats color tests use `BlitColorTestParams` (extends `TestParams` with `compatibleFormats`) for format compatibility filtering
- The all-formats depth/stencil and mipmap test registration functions were not fully inspected beyond their signatures
