# vktApiCopyImageToImageTests

## Overview

Tests for `vkCmdCopyImage` and `vkCmdCopyImage2` (via `VK_KHR_copy_commands2`). Verifies that image-to-image copy operations produce correct results across a wide range of formats, image types, and copy region configurations. This is the largest implementation file in the subtree (~4460 lines).

## Role

- **Implementation-heavy test file** -- contains test instance class, test case registration, and verification logic.

## Source Code

- [`vktApiCopyImageToImageTests.cpp`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp)
- [`vktApiCopyImageToImageTests.hpp`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.hpp)

## Registration Hierarchy

```text
api.copy_and_blit.core.image_to_image
├── simple_tests
├── all_formats (skipped if useSparseBinding)
├── 3d_images
├── dimensions (skipped if useSparseBinding)
├── cube
└── array
```

Evidence:
- The `image_to_image` group is registered under multiple parent groups within `api.copy_and_blit`: `core`, `dedicated_allocation`, `copy_commands2`, and `sparse` -- see [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L70). The canonical root path uses `core` as the primary variant (suballocated, no extensions).
- Direct children added by [`addCopyImageToImageTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4440)
- The `misc` subgroup is conditionally added only when `queueSelection == TransferOnly` ([line 4450](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4450)); it appears under `api.copy_and_blit.copy_commands2.image_to_image_transfer_queue.misc` rather than under `core.image_to_image`
- `addCopyImageToImageTestsSimpleOnly()` at [line 4456](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4456) creates only the `simple_tests` subgroup (used for `general_layout`, `transfer_queue_secondary`, and `transfer_sparse` variants)

## Test Families

### simple_tests -- Basic image-to-image copy tests

Added by [`addImageToImageSimpleTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1152). Tests basic whole-image and partial-region copies for a small set of formats (`VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32G32B32_UINT`, `VK_FORMAT_R32G32B32_SFLOAT`) with both optimal and linear tiling. Covers single-region and multi-region copy scenarios with various offset and extent configurations. Linear tiling is skipped when sparse binding is active (VUID-VkImageCreateInfo-tiling-04121).

### all_formats -- Comprehensive format coverage (skipped if useSparseBinding)

Added by [`addImageToImageAllFormatsTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3161). Tests image-to-image copies across a wide range of formats, organized into two subgroups:

- **color** -- added by `addImageToImageAllFormatsColorTests()`. Iterates over source color formats and their compatible destination formats, generating test cases for each compatible pair. `CopyColorTestParams` extends `TestParams` with a `compatibleFormats` pointer for format-pair iteration. [`isAllowedImageToImageAllFormatsColorSrcFormatTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L44) filters formats for dedicated allocation tests.
- **depth_stencil** -- added by `addImageToImageAllFormatsDepthStencilTests()`. Tests depth/stencil format copies with proper aspect separation.

This subgroup is skipped when `useSparseBinding` is set -- confirmed at [lines 4443-4444](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4443).

### 3d_images -- 3D image copy tests

Added by [`addImageToImage3dImagesTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3167). Tests copies involving `VK_IMAGE_TYPE_3D` images, including 3D-to-2D slice copies and 2D-to-3D slice assembly, with per-slice copy regions.

### dimensions -- Large-dimension copy tests (skipped if useSparseBinding)

Added by [`addImageToImageDimensionsTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L2141). Tests image copies with large and non-power-of-two dimensions using compatible format pairs across various bit widths (8-bit through 256-bit). Exercises large pot x small pot, large pot x small npot, small pot x large pot, and similar dimension combinations. This subgroup is skipped when `useSparseBinding` is set -- confirmed at [lines 4446-4447](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4446).

### cube -- Cube map copy tests

Added by [`addImageToImageCubeTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3486). Tests copies involving cube-compatible images (`VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`), including cube-to-array and array-to-cube copy scenarios with per-face copy regions.

### array -- Array image copy tests

Added by [`addImageToImageArrayTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L3818). Tests copies involving 2D array images with multiple array layers, including per-layer copy regions and gradient fill modes.

### misc -- Miscellaneous copy tests (TransferOnly queue only, under image_to_image_transfer_queue)

Added by [`addImageToImageMiscTests()`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4413). Contains multi-sample-then-single-sample tests that exercise pipeline barrier stage options (`bottom_of_pipe`, `transfer`, `all_commands`) on transfer-only queues. Only created when `queueSelection == TransferOnly` -- confirmed at [line 4450](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4450). In the mustpass files, this subgroup appears under `api.copy_and_blit.copy_commands2.image_to_image_transfer_queue.misc` rather than under `core.image_to_image`.

### Implementation Details

The test instance class `CopyImageToImage` inherits [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L474). It creates source and destination `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, supports sparse binding (when `useSparseBinding=true`, source image uses sparse flags), handles compressed format block-size scaling for copy regions, and dispatches to `vkCmdCopyImage` or `vkCmdCopyImage2` depending on `extensionFlags`.

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

- `COPY_COMMANDS_2` -- `VK_KHR_copy_commands2` or Vulkan 1.3
- `SPARSE_BINDING` -- sparse image support for the given format
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

- The `all_formats` and `dimensions` subgroups are skipped when `useSparseBinding` is set -- confirmed at [lines 4443-4447](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4443)
- The `misc` subgroup is only created for `TransferOnly` queue selection -- confirmed at [line 4450](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L4450)
- The `clearDestinationWithRed` flag clears the destination with red before copying to detect out-of-bounds writes
- The full format list for all-formats tests was not exhaustively inspected
