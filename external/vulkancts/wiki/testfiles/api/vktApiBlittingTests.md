# vktApiBlittingTests



## Overview



Tests for `vkCmdBlitImage` and `vkCmdBlitImage2` (via `VK_KHR_copy_commands2`). Blitting differs from copying in that it supports scaling and filtering (nearest or linear). This file (~4107 lines) verifies that scaled image-to-image transfers via blit commands produce results consistent with CPU-side reference blitting.



## Role



- **Implementation-heavy test file** �?contains test instance class, test case registration, and verification logic.



## Source Code



- [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp)

- [`vktApiBlittingTests.hpp`](../../../modules/vulkan/api/vktApiBlittingTests.hpp)



## Registration Path



```

api �?copy_and_blit �?(core|dedicated_allocation|copy_commands2|...) �?blit_image

```



Registered via [`addBlittingImageTests()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L4100), called from the dispatcher [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L136).



## Test Hierarchy



```

blit_image

├── simple_tests         (addBlittingImageSimpleTests)

�?  ├── whole_1          (whole image blit, set 1)

�?  ├── whole_2          (whole image blit, set 2)

�?  ├── scaling_and_offset

�?  ├── without_scaling_partial

�?  ├── mirror_xy, mirror_x, mirror_y, mirror_z

�?  ├── mirror_subregions

�?  ├── scaling_whole_1, scaling_whole_2

�?  └── array, 3d_to_2d_array

└── all_formats          (addBlittingImageAllFormatsTests)

    ├── color            (addBlittingImageAllFormatsColorTests)

    �?  └── (per src format �?per dst format)

    ├── depth_stencil    (addBlittingImageAllFormatsDepthStencilTests)

    └── mipmap           (addBlittingImageAllFormatsMipmapTests)

        ├── base_level

        └── previous_level

```



## Test Families



### `BlittingImages` (class)



- Inherits [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L474)

- Creates source and destination images with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`

- Supports sparse binding via `m_sparseSemaphore`

- Dispatches to `vkCmdBlitImage` or `vkCmdBlitImage2` depending on `extensionFlags`

- Handles compressed texture sources via [`CompressedTextureForBlit`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L42) helper class



### `CompressedTextureForBlit` (class)



- Helper that generates compressed texture data (ASTC, BC6H, ETC, etc.) with valid blocks

- Decompresses to a `tcu::PixelBufferAccess` for CPU-side reference comparison

- Special-cases ASTC LDR/HDR, BC6H float formats with predefined valid blocks



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



- `COPY_COMMANDS_2` �?`VK_KHR_copy_commands2` or Vulkan 1.3

- Linear filtering requires `VK_FORMAT_FEATURE_BLIT_SRC_BIT` / `VK_FORMAT_FEATURE_BLIT_DST_BIT` with linear filter support

- Compressed format blits require format support on the device

- Depth/stencil blits may require `VK_FORMAT_FEATURE_BLIT_DST_BIT` for the specific format



## Verification Methods



- **Nearest-filtered**: [`checkNearestFilteredResult()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L175) �?exact comparison against source

- **Non-nearest-filtered**: [`checkNonNearestFilteredResult()`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L171) �?threshold comparison with clamped and unclamped references

- **Compressed nearest**: `checkCompressedNearestFilteredResult()` �?with compressed format thresholds

- **Compressed non-nearest**: `checkCompressedNonNearestFilteredResult()` �?with compressed format thresholds

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



- The `CompressedTextureForBlit` class uses random data with special valid-block generation for BC6H and ASTC formats to avoid decompression errors �?confirmed at [lines 56�?43](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L56)

- The all-formats color tests use `BlitColorTestParams` (extends `TestParams` with `compatibleFormats`) for format compatibility filtering

- The all-formats depth/stencil and mipmap test registration functions were not fully inspected beyond their signatures

