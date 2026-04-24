# vktApiCopyImageToBufferTests ([source](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp))

## Overview

Tests that verify the correctness of Vulkan copy commands that transfer data from images to buffers. The file covers three distinct copy scenarios: standard uncompressed image-to-buffer copies, compressed image-to-buffer copies with per-mip-level verification, and mipmapped image-to-buffer copies with per-mip-level verification. Three Vulkan command variants are exercised: `vkCmdCopyImageToBuffer`, `vkCmdCopyImageToBuffer2` (KHR_copy_commands2), and `vkCmdCopyImageToMemoryKHR` (VK_KHR_copy_memory_indirect with device-address commands).

## Role of File

This file provides the test implementation and registration for all image-to-buffer copy tests in the Vulkan CTS `api` test group. It contains three test instance classes, three test case classes, and four registration functions that populate the test tree under `image_to_buffer`.

## Source Code

- Implementation: [vktApiCopyImageToBufferTests.cpp](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp)
- Header: [vktApiCopyImageToBufferTests.hpp](../../modules/vulkan/api/vktApiCopyImageToBufferTests.hpp)

## Registration Path

```
api > copy_and_blit > image_to_buffer
```

The top-level registration function `addCopyImageToBufferTests` at [line 2014](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L2014) creates three subgroups:

- `1d_images` -- populated by `add1dImageToBufferTests` at [line 1691](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1691)
- `2d_images` -- populated by `add2dImageToBufferTests` at [line 1098](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1098)
- `3d_images` -- populated by `add3dImageToBufferTests` at [line 1974](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1974)

## Test Hierarchy

```
image_to_buffer
|-- 1d_images
|   |-- tightly_sized_buffer
|   |-- larger_buffer
|   |-- array_tightly_sized_buffer
|   |-- array_larger_buffer
|   |-- array_all_remaining_layers
|   |-- array_not_all_remaining_layers
|   |-- mip_copies_<format>_<W>x<H>
|   |-- mip_copies_<format>_<W>x<H>_<N>_layers
|-- 2d_images
|   |-- whole[_<format>][_linear]
|   |-- whole_unaligned[_<format>][_linear]
|   |-- buffer_offset[_<format>][_linear]
|   |-- buffer_offset_relaxed[_<format>][_linear]
|   |-- regions[_<format>][_linear]
|   |-- tightly_sized_buffer[_<format>][_linear]
|   |-- larger_buffer[_<format>][_linear]
|   |-- tightly_sized_buffer_offset[_<format>][_linear]
|   |-- array[_<format>][_linear]
|   |-- array_larger_buffer[_<format>][_linear]
|   |-- array_tightly_sized_buffer[_<format>][_linear]
|   |-- array_all_remaining_layers[_<format>][_linear]
|   |-- array_not_all_remaining_layers[_<format>][_linear]
|   |-- padding_bytes[_<format>][_linear]
|   |-- mip_copies_<format>_<W>x<H>
|   |-- mip_copies_<format>_<W>x<H>_<N>_layers
|   |-- mip_copies_<format>_<W>x<H>_<N>_layersindirect
|-- 3d_images
|   |-- mip_copies_<format>_<W>x<H>xD
```

## Test Families

### 2D Uncompressed Families (CopyImageToBuffer)

Registered in `add2dImageToBufferTests` at [line 1098](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1098). Uses `CopyImageToBufferTestCase` at [line 359](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L359) and `CopyImageToBuffer` instance at [line 65](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L65).

| Family | Description |
|--------|-------------|
| whole | Copy entire 2D image to buffer with tightly packed rows |
| whole_unaligned | Copy with bufferRowLength and bufferImageHeight larger than image extent |
| buffer_offset | Copy with non-zero buffer offset and image subregion offset |
| buffer_offset_relaxed | Copy with relaxed buffer offset alignment (Universal queue only) |
| regions | Multiple copy regions from different image subregions to different buffer offsets |
| tightly_sized_buffer | Buffer sized exactly to the copied subregion with explicit row/image height |
| larger_buffer | Buffer larger than needed with explicit bufferImageHeight |
| tightly_sized_buffer_offset | Tightly sized buffer with non-zero buffer offset |
| array | 16-layer array image, one copy region per layer |
| array_larger_buffer | 16-layer array image with bufferImageHeight larger than image height |
| array_tightly_sized_buffer | 16-layer array image with explicit row/image height per layer |
| array_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 0 |
| array_not_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 2 |
| padding_bytes | Verifies padding bytes between rows are not overwritten (linear tiling only) |

### 2D Compressed Families (CopyCompressedImageToBuffer)

Registered in `add2dImageToBufferTests` at [line 1659](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1659). Uses `CopyCompressedImageToBufferTestCase` at [line 687](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L687) and `CopyCompressedImageToBuffer` instance at [line 412](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L412).

| Family | Description |
|--------|-------------|
| mip_copies_<format>_<W>x<H> | Compressed 2D image with full mip chain, verify each mip level readback |
| mip_copies_<format>_<W>x<H>_<N>_layers | Compressed 2D array image with N layers, verify each mip/layer |
| mip_copies_<format>_<W>x<H>_<N>_layersindirect | Same as above using vkCmdCopyMemoryToImageIndirectKHR for upload |

### 1D Families (CopyImageToBuffer / CopyCompressedImageToBuffer)

Registered in `add1dImageToBufferTests` at [line 1691](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1691).

| Family | Instance Class | Description |
|--------|---------------|-------------|
| tightly_sized_buffer | CopyImageToBuffer | 1D image copy with tightly packed buffer |
| larger_buffer | CopyImageToBuffer | 1D image copy with larger buffer |
| array_tightly_sized_buffer | CopyImageToBuffer | 16-layer 1D array, one region per layer |
| array_larger_buffer | CopyImageToBuffer | 16-layer 1D array with larger buffer |
| array_all_remaining_layers | CopyImageToBuffer | VK_REMAINING_ARRAY_LAYERS from layer 0 |
| array_not_all_remaining_layers | CopyImageToBuffer | VK_REMAINING_ARRAY_LAYERS from layer 2 |
| mip_copies_<format>_<W>x<H> | CopyCompressedImageToBuffer | Compressed 1D/2D image mip chain readback (uses INDIRECT_COPY) |

### 3D Families (CopyCompressedImageToBuffer)

Registered in `add3dImageToBufferTests` at [line 1974](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1974).

| Family | Description |
|--------|-------------|
| mip_copies_<format>_<W>x<H>xD | Compressed 3D image with full mip chain, verify each mip level readback |

## Parameter Dimensions

### 2D Uncompressed Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8_UNORM, VK_FORMAT_R32G32B32_UINT, VK_FORMAT_R32G32B32_SFLOAT | [line 1103](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1103) |
| Tiling | VK_IMAGE_TILING_OPTIMAL, VK_IMAGE_TILING_LINEAR | [line 1104](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1104) |
| Allocation Kind | From TestGroupParams | [line 1121](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1121) |
| Extension Flags | From TestGroupParams | [line 1122](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1122) |
| Queue Selection | From TestGroupParams | [line 1123](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1123) |
| Sparse Binding | From TestGroupParams | [line 1124](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1124) |
| General Layout | From TestGroupParams | [line 1125](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1125) |

### 2D/3D Compressed Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | formats::compressedFormatsFloats (BC1-BC7, ETC2, EAC, ASTC 4x4 through 12x12) | [line 1674](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1674) |
| Extent | {64,64,1}, {64,192,1} for 2D; {16,16,16}, {16,8,24} for 3D | [line 1641](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1641), [line 1978](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1978) |
| Array Layers | 1, 2, 5 | [line 1648](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1648) |
| Indirect | Standard and INDIRECT_COPY variants (non-VulkanSC only) | [line 1680](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1680) |

### 1D Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM | [line 1698](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1698) |
| Tiling | VK_IMAGE_TILING_OPTIMAL | [line 1700](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1700) |
| Compressed Format | formats::compressedFormatsFloats | [line 1963](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1963) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_dedicated_allocation | When allocationKind == ALLOCATION_KIND_DEDICATED | [line 376](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L376) |
| VK_FORMAT_FEATURE_TRANSFER_SRC_BIT | Source image format must support transfer src | [line 385](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L385), [line 812](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L812) |
| maxArrayLayers | Must be >= requested array layers | [line 393](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L393) |
| Transfer queue granularity | When queueSelection == TransferOnly | [line 397](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L397) |
| COPY_COMMANDS_2 extension | Checked via checkExtensionSupport | [line 381](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L381) |
| DEVICE_ADDRESS_COMMANDS extension | Checked via checkExtensionSupport | [line 381](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L381) |
| VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR | When INDIRECT_COPY flag is set | [line 766](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L766) |
| Copy memory indirect queue support | When INDIRECT_COPY, checks supportedQueues for the selected queue type | [line 782](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L782) |
| MAINTENANCE_5 | For VK_REMAINING_ARRAY_LAYERS tests | [line 1522](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1522) |
| Sparse binding | Sparse image format properties must be supported | [line 128](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L128) |
| maxMipLevels | Must support the required number of mip levels for compressed tests | [line 745](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L745) |

## Verification Methods

### CopyImageToBuffer (uncompressed)

Uses CPU-side reference comparison. The `copyRegionToTextureLevel` method at [line 325](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L325) computes the expected buffer contents from the source image data. The result is validated via `checkTestResult` at [line 322](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L322), which compares the actual buffer data against the expected result using the inherited comparison logic from `CopiesAndBlittingTestInstance`.

### CopyCompressedImageToBuffer (compressed)

Performs per-mip-level, per-array-layer byte-by-byte comparison using `deMemCmp` at [line 636](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L636). Each mip level of the compressed image is copied individually to a buffer, then the raw bytes are compared against the reference compressed data. On failure, both reference and result are decompressed and logged as images at [line 659](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L659), along with hex dumps of the raw block data at [line 666](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L666).

### CopyMipmappedImageToBuffer (mipmapped uncompressed)

Performs per-mip-level, per-array-layer byte-by-byte comparison using `deMemCmp` at [line 1013](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1013). Each mip level is copied individually to a buffer and compared against the reference texture data.

## Test Principles Observed

- **Command variant coverage**: Three command paths are tested -- standard `vkCmdCopyImageToBuffer` at [line 303](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L303), `vkCmdCopyImageToBuffer2` at [line 293](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L293), and `vkCmdCopyImageToMemoryKHR` at [line 274](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L274).
- **Buffer offset alignment**: Tests both aligned and relaxed buffer offsets; the relaxed variant is restricted to Universal queue at [line 1207](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1207).
- **Multi-region copies**: The `regions` family at [line 1281](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1281) tests multiple copy regions in a single command.
- **Array layer handling**: Tests individual per-layer copies, VK_REMAINING_ARRAY_LAYERS from base 0 and base 2, and tightly/larger buffer sizing.
- **Compressed format coverage**: All BC, ETC2, EAC, and ASTC formats in `formats::compressedFormatsFloats` are tested with full mip chains.
- **Padding byte integrity**: The `padding_bytes` family at [line 1637](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1637) verifies that padding bytes between rows are not overwritten during copies with linear tiling.
- **Sparse binding**: The `CopyImageToBuffer` class inherits from `CopiesAndBlittingTestInstanceWithSparseSemaphore` and supports sparse image allocation at [line 127](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L127).
- **Image layout**: Tests both `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and `VK_IMAGE_LAYOUT_GENERAL` (via `useGeneralLayout` flag) at [line 250](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L250).

## Notes / Uncertainties

- The 1D compressed tests at [line 1947](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1947) use `VK_IMAGE_TYPE_2D` despite being registered under the `1d_images` subgroup; this appears intentional because compressed formats require 2D image types, but the naming may be confusing.
- The `CopyMipmappedImageToBuffer` class at [line 816](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L816) is defined but not directly registered in any of the `add*ImageToBufferTests` functions visible in this file. It may be registered elsewhere or may be unused in the current configuration.
- The `INDIRECT_COPY` flag used in compressed tests at [line 1680](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1680) and [line 1961](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1961) controls the upload path (using `copyBufferToImageIndirect`), not the image-to-buffer copy path itself. The actual image-to-buffer copy in compressed tests always uses `vkCmdCopyImageToBuffer` or `vkCmdCopyImageToBuffer2`.
- The `CopyCompressedImageToBuffer` test clears the destination buffer to zero before each mip-level copy at [line 553](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L553) as a precaution against stale data.
