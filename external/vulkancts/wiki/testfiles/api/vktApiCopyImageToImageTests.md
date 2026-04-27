# vktApiCopyImageToImageTests

## Overview

Tests for `vkCmdCopyImage` and `vkCmdCopyImage2` (via `VK_KHR_copy_commands2`). Verifies that image-to-image copy operations produce correct results across a wide range of formats, image types, and copy region configurations. This is the largest implementation file in the subtree (~4460 lines).

## Role

- **Implementation-heavy test file** �?contains test instance class, test case registration, and verification logic.

## Source Code

- [`vktApiCopyImageToImageTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp)
- [`vktApiCopyImageToImageTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.hpp)

## Registration Path

```
api �?copy_and_blit �?(core|dedicated_allocation|copy_commands2|...) �?image_to_image
```

Registered via [`addCopyImageToImageTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp:4440) and [`addCopyImageToImageTestsSimpleOnly()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp:4456).

## Test Hierarchy

```
image_to_image
├── simple_tests         (addImageToImageSimpleTests)
├── all_formats          (addImageToImageAllFormatsTests, skipped if useSparseBinding)
�?  ├── color            (addImageToImageAllFormatsColorTests)
�?  �?  └── (per src format �?per compatible dst format)
�?  └── depth_stencil    (addImageToImageAllFormatsDepthStencilTests)
├── 3d_images            (addImageToImage3dImagesTests)
├── dimensions           (addImageToImageDimensionsTests, skipped if useSparseBinding)
├── cube                 (addImageToImageCubeTests)
├── array                (addImageToImageArrayTests)
└── misc                 (addImageToImageMiscTests, TransferOnly queue only)
```

`addCopyImageToImageTestsSimpleOnly` creates only the `simple_tests` subgroup (used for `general_layout`, `transfer_queue_secondary`, and `transfer_sparse` variants).

## Test Families

### `CopyImageToImage` (class)

- Inherits [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:474)
- Creates source and destination `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`
- Supports sparse binding: when `useSparseBinding=true`, source image uses sparse flags
- Handles compressed format block-size scaling for copy regions
- Dispatches to `vkCmdCopyImage` or `vkCmdCopyImage2` depending on `extensionFlags`

### `CopyColorTestParams` (struct)

- Extends `TestParams` with `compatibleFormats` pointer for all-formats color tests
- [`isAllowedImageToImageAllFormatsColorSrcFormatTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp:44) filters formats for dedicated allocation tests

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Image type | `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TYPE_3D` |
| Formats | Wide range of color, depth/stencil, compressed formats |
| Image extent | `defaultExtent` (64x64x1), `defaultHalfExtent`, `defaultQuarterExtent`, `default3dExtent` |
| Copy regions | Whole, partial, multi-region, with offsets |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `SPARSE_BINDING` |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` |
| `queueSelection` | `Universal`, `TransferOnly` |
| `useSecondaryCmdBuffer` | `true` for `transfer_queue_secondary` |
| `useSparseBinding` | `true` for `sparse` subgroup |
| `useGeneralLayout` | `true` for `general_layout` subgroup |

## Support / Feature Requirements

- `COPY_COMMANDS_2` �?`VK_KHR_copy_commands2` or Vulkan 1.3
- `SPARSE_BINDING` �?sparse image support for the given format
- Non-universal queue tests require appropriate queue family
- Compressed format tests require format support on the device
- Checked via `checkExtensionSupport()` and `getPhysicalDeviceImageFormatProperties()`

## Verification Methods

- **Bit-exact comparison** for non-depth/stencil formats via `tcu::bitwiseCompare()`
- **Float threshold comparison** for depth components via `tcu::floatThresholdCompare()` with zero threshold
- **Integer threshold comparison** for stencil components via `tcu::intThresholdCompare()` with zero threshold
- CPU reference computed by `copyRegionToTextureLevel()` which handles array layer offsets and depth/stencil aspect separation

## Test Principles

- Verify `vkCmdCopyImage` produces bit-exact results for color formats
- Verify depth/stencil aspect separation in combined depth/stencil copies
- Verify compressed format copies with correct block-size alignment
- Verify 1D, 2D, 3D, cube, and array image types
- Verify compatible format pairs in all-formats tests
- Verify sparse image copies work correctly
- Verify secondary command buffer and general layout paths

## Notes / Uncertainties

- The `all_formats` and `dimensions` subgroups are skipped when `useSparseBinding` is set �?confirmed at [lines 4443�?447](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp:4443)
- The `misc` subgroup is only created for `TransferOnly` queue selection �?confirmed at [line 4450](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp:4450)
- The `clearDestinationWithRed` flag clears the destination with red before copying to detect out-of-bounds writes
- The full format list for all-formats tests was not exhaustively inspected
