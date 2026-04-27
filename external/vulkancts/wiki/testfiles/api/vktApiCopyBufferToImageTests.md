# vktApiCopyBufferToImageTests ([source](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp))

## Overview

Tests that verify the correctness of Vulkan copy commands that transfer data from buffers to images. The file covers two image dimensionality scenarios: 1D images and 2D images, each tested with a variety of buffer layouts, offsets, and array layer configurations. Three Vulkan command variants are exercised: `vkCmdCopyBufferToImage`, `vkCmdCopyBufferToImage2` (KHR_copy_commands2), and `vkCmdCopyMemoryToImageKHR` (VK_KHR_copy_memory_indirect with device-address commands).

## Role of File

This file provides the test implementation and registration for all buffer-to-image copy tests in the Vulkan CTS `api` test group. It contains one test instance class, one test case class, and three registration functions that populate the test tree under `buffer_to_image`.

## Source Code

- Implementation: [vktApiCopyBufferToImageTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp)
- Header: [vktApiCopyBufferToImageTests.hpp](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.hpp)

## Registration Path

```
api > copy_and_blit > buffer_to_image
```

The top-level registration function `addCopyBufferToImageTests` at [line 1147](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1147) creates two subgroups:

- `1d_images` -- populated by `add1dBufferToImageTests` at [line 358](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L358)
- `2d_images` -- populated by `add2dBufferToImageTests` at [line 625](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L625)

This function is also called from other registration contexts in [vktApiCopiesAndBlittingTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp):
- `buffer_to_image_transfer_queue` at [line 175](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L175) (TransferOnly queue)
- `buffer_to_image_compute_queue` at [line 187](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L187) (ComputeOnly queue)
- `buffer_to_image_general_layout` at [line 228](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L228) (VK_IMAGE_LAYOUT_GENERAL)
- `buffer_to_image` under `device_address` at [line 255](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L255) (DEVICE_ADDRESS_COMMANDS)

## Test Hierarchy

```
buffer_to_image
|-- 1d_images
|   |-- tightly_sized_buffer[_<suffix>]
|   |-- larger_buffer[_<suffix>]
|   |-- array_tightly_sized_buffer[_<suffix>]
|   |-- array_all_remaining_layers[_<suffix>]
|   |-- array_not_all_remaining_layers[_<suffix>]
|   |-- array_larger_buffer[_<suffix>]
|-- 2d_images
|   |-- whole[_<suffix>]
|   |-- whole_unaligned[_<suffix>]
|   |-- regions[_<suffix>]
|   |-- buffer_offset[_<suffix>]
|   |-- buffer_offset_relaxed[_<suffix>]
|   |-- tightly_sized_buffer[_<suffix>]
|   |-- larger_buffer[_<suffix>]
|   |-- tightly_sized_buffer_offset[_<suffix>]
|   |-- array[_<suffix>]
|   |-- array_larger_buffer[_<suffix>]
|   |-- array_tightly_sized_buffer[_<suffix>]
|   |-- array_all_remaining_layers[_<suffix>]
|   |-- array_not_all_remaining_layers[_<suffix>]
```

## Test Families

### 1D Families (CopyBufferToImage)

Registered in `add1dBufferToImageTests` at [line 358](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L358). Uses `CopyBufferToImageTestCase` at [line 269](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L269) and `CopyBufferToImage` instance at [line 35](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L35).

| Family | Description |
|--------|-------------|
| tightly_sized_buffer | 1D image copy with buffer sized exactly to the image extent |
| larger_buffer | 1D image copy with bufferImageHeight larger than image extent |
| array_tightly_sized_buffer | 16-layer 1D array image, one copy region per layer with per-layer buffer offsets |
| array_all_remaining_layers | 16-layer 1D array image using VK_REMAINING_ARRAY_LAYERS from base layer 0 |
| array_not_all_remaining_layers | 16-layer 1D array image using VK_REMAINING_ARRAY_LAYERS from base layer 2 |
| array_larger_buffer | 16-layer 1D array image with bufferImageHeight larger than image extent per layer |

### 2D Families (CopyBufferToImage)

Registered in `add2dBufferToImageTests` at [line 625](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L625). Uses `CopyBufferToImageTestCase` at [line 269](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L269) and `CopyBufferToImage` instance at [line 35](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L35).

| Family | Description |
|--------|-------------|
| whole | Copy entire 2D image from buffer with tightly packed rows |
| whole_unaligned | Copy with bufferRowLength and bufferImageHeight larger than image extent |
| regions | Multiple copy regions from different buffer offsets to different image subregions |
| buffer_offset | Copy with non-zero buffer offset and image subregion offset |
| buffer_offset_relaxed | Copy with relaxed buffer offset alignment (Universal queue only) |
| tightly_sized_buffer | Buffer sized exactly to the copied subregion with explicit row/image height |
| larger_buffer | Buffer larger than needed with explicit bufferImageHeight |
| tightly_sized_buffer_offset | Tightly sized buffer with non-zero buffer offset |
| array | 16-layer array image, one copy region per layer |
| array_larger_buffer | 16-layer array image with bufferImageHeight larger than image height |
| array_tightly_sized_buffer | 16-layer array image with explicit row/image height per layer |
| array_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 0 |
| array_not_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 2 |

## Parameter Dimensions

### 1D Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8G8B8A8_UINT, VK_FORMAT_R32G32B32_SFLOAT | [line 370](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L370) |
| Tiling | VK_IMAGE_TILING_OPTIMAL (default), VK_IMAGE_TILING_LINEAR (R32G32B32_SFLOAT only) | [line 370](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L370) |
| Allocation Kind | From TestGroupParams | [line 391](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L391) |
| Extension Flags | From TestGroupParams | [line 392](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L392) |
| Queue Selection | From TestGroupParams | [line 393](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L393) |
| Sparse Binding | From TestGroupParams | [line 394](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L394) |
| General Layout | From TestGroupParams | [line 395](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L395) |

### 2D Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8_UNORM, VK_FORMAT_R8G8B8A8_UINT, VK_FORMAT_R32G32B32_SFLOAT, VK_FORMAT_R64_UINT | [line 637](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L637) |
| Tiling | VK_IMAGE_TILING_OPTIMAL (default), VK_IMAGE_TILING_LINEAR (R8_UNORM and R32G32B32_SFLOAT) | [line 637](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L637) |
| Allocation Kind | From TestGroupParams | [line 663](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L663) |
| Extension Flags | From TestGroupParams | [line 664](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L664) |
| Queue Selection | From TestGroupParams | [line 665](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L665) |
| Sparse Binding | From TestGroupParams | [line 666](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L666) |
| General Layout | From TestGroupParams | [line 667](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L667) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_dedicated_allocation | When allocationKind == ALLOCATION_KIND_DEDICATED | [line 87](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L87) |
| VK_FORMAT_FEATURE_TRANSFER_DST_BIT | Destination image format must support transfer dst | [line 304](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L304) |
| maxArrayLayers | Must be >= requested array layers | [line 316](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L316) |
| Transfer queue granularity | When queueSelection == TransferOnly | [line 292](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L292) |
| COPY_COMMANDS_2 extension | Checked via checkExtensionSupport | [line 289](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L289) |
| DEVICE_ADDRESS_COMMANDS extension | Checked via checkExtensionSupport | [line 289](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L289) |
| MAINTENANCE_5 | For VK_REMAINING_ARRAY_LAYERS tests | [line 507](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L507), [line 552](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L552), [line 1071](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1071), [line 1116](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1116) |
| Sparse binding | Sparse image format properties must be supported | [line 126](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L126) |
| Image format properties | vkGetPhysicalDeviceImageFormatProperties must succeed for the requested format/tiling/usage/flags | [line 305](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L305) |

## Verification Methods

### CopyBufferToImage (uncompressed)

Uses CPU-side reference comparison. The `copyRegionToTextureLevel` method at [line 324](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L324) computes the expected image contents from the source buffer data, accounting for bufferRowLength, bufferImageHeight, bufferOffset, and baseArrayLayer. The result is validated via `checkTestResult` at [line 266](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L266), which compares the actual image data (read back via `readImage`) against the expected result using the inherited comparison logic from `CopiesAndBlittingTestInstance`.

## Test Principles Observed

- **Command variant coverage**: Three command paths are tested -- standard `vkCmdCopyBufferToImage` at [line 255](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L255), `vkCmdCopyBufferToImage2` at [line 245](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L245), and `vkCmdCopyMemoryToImageKHR` at [line 227](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L227).
- **Buffer offset alignment**: Tests both aligned and relaxed buffer offsets; the relaxed variant is restricted to Universal queue at [line 796](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L796).
- **Multi-region copies**: The `regions` family at [line 734](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L734) tests multiple copy regions in a single command, with increasing buffer offsets for DEVICE_ADDRESS_COMMANDS to avoid VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026 at [line 755](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L755).
- **Array layer handling**: Tests individual per-layer copies, VK_REMAINING_ARRAY_LAYERS from base 0 and base 2, and tightly/larger buffer sizing.
- **96-bit format coverage**: R32G32B32_SFLOAT is tested with both optimal and linear tiling because some implementations do not natively support these formats at [line 374](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L374).
- **64-bit format coverage**: R64_UINT is tested for 2D images at [line 646](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L646).
- **Sparse binding**: The `CopyBufferToImage` class inherits from `CopiesAndBlittingTestInstanceWithSparseSemaphore` and supports sparse image allocation at [line 124](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L124).
- **Image layout**: Tests both `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and `VK_IMAGE_LAYOUT_GENERAL` (via `useGeneralLayout` flag) at [line 201](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L201).

## Notes / Uncertainties

- The 1D tests use `VK_IMAGE_TYPE_1D` at [line 379](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L379) but represent array depth as `extent.depth` at [line 453](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L453), which maps to arrayLayers in the Vulkan image creation at [line 102](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L102) via `getArraySize`. This is consistent with the CTS convention but may be confusing.
- The `buffer_offset_relaxed` family at [line 796](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L796) is only added when `queueSelection == Universal`, matching the Vulkan spec requirement that relaxed buffer offset alignment is only guaranteed for universal queue families.
- The `regions` family for DEVICE_ADDRESS_COMMANDS at [line 755](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L755) increments buffer offsets for each region to avoid triggering VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026, which requires that address ranges for different regions do not overlap.
- The file does not include 3D image tests or compressed image tests for buffer-to-image copies; those are handled in separate test files.
