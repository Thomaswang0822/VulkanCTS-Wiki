# vktImageConcurrentCopyTests.cpp

## Overview

Tests that verify the correctness of multiple image copy operations without synchronization barriers between them. The file covers both device-side (queue-based) and host-side (VK_EXT_host_image_copy) copy operations, including single-command and multi-command scenarios with various image configurations.

## Role of File

This is an implementation-heavy file that provides test implementations and registration for concurrent image copy tests. It registers tests under `image.concurrent_copy`.

## Source Code

- Implementation: [vktImageConcurrentCopyTests.cpp](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp)
- Header: [vktImageConcurrentCopyTests.hpp](../../../modules/vulkan/image/vktImageConcurrentCopyTests.hpp)

## Registration Hierarchy

```text
image.concurrent_copy
├── r8g8b8a8_unorm
�?  └── ... (nested structure by tiling, type, command, data, copy, access, flags)
├── r8_unorm
�?  └── ... (same structure)
└── r32g32_sfloat
    └── ... (same structure)
```

Evidence:
- `concurrent_copy` group created by [`createImageConcurrentCopyTests()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L662-L664)
- Format groups created via loop at [lines 731-792](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L731-L792)

## Test Families

### Format-based groups �?r8g8b8a8_unorm, r8_unorm, r32g32_sfloat

Each format has a nested hierarchy testing various combinations.

### Nested structure under each format

The test hierarchy under each format follows this pattern:
- **Tiling**: `linear`, `optimal`
- **Image Type**: `type_2d`, `type_3d`
- **Command Type**: `single`, `multiple`
- **Data Type**: `random`, `gradient`
- **Copy Type**: `device`, `host` (host only, non-VulkanSC)
- **Access Type**: `write`, `read_and_write` (only when host copy is true)
- **Image Flags**: `none`, `2d_array_compatible`

### Single vs Multiple Commands

- **single**: Uses one `vkCmdCopyBufferToImage` or `copyMemoryToImage` command with all regions
- **multiple**: Uses multiple separate commands, each copying a subset of regions

### Host Copy Tests (non-VulkanSC)

When `hostCopy=true`, tests use `vkCopyMemoryToImageEXT` and optionally `vkCopyImageToMemoryEXT` from the VK_EXT_host_image_copy extension. Multiple concurrent copies are executed in separate threads.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Formats | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8_UNORM, VK_FORMAT_R32G32_SFLOAT | [lines 666-670](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L666-L670) |
| Tiling | VK_IMAGE_TILING_LINEAR, VK_IMAGE_TILING_OPTIMAL | [lines 672-675](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L672-L675) |
| Image Types | VK_IMAGE_TYPE_2D, VK_IMAGE_TYPE_3D | [lines 677-680](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L677-L680) |
| Image Dimensions | Width: 128, Height: 128, Depth: 1 (2D) or 32 (3D) | [lines 210-212](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L210-L212) |
| Copy Type | device (false), host (true) | [lines 682-691](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L682-L691) |
| Access Type | write (false), read_and_write (true) | [lines 693-702](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L693-L702) |
| Command Type | single (true), multiple (false) | [lines 704-711](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L704-L711) |
| Data Type | random (true), gradient (false) | [lines 713-720](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L713-L720) |
| Image Flags | none, 2d_array_compatible | [lines 722-729](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L722-L729) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_EXT_host_image_copy | Required for host copy tests | [line 607](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L607) |
| VK_KHR_maintenance9 | Required for 2d_array_compatible flag tests | [line 657](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L657) |
| VK_FORMAT_FEATURE_TRANSFER_SRC_BIT/DST_BIT | Format must support transfer operations | [lines 1130-1134](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L1130-L1134) |
| Host image copy layout support | Required layout must be in pCopyDstLayouts | [lines 639-652](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L639-L652) |

## Verification Methods

### Memory Comparison

The `iterate()` method at [line 196](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L196) verifies copy correctness by:

1. Copying data from source buffer to image using split regions
2. Reading back the image contents using `vkCmdCopyImageToBuffer`
3. Comparing source and destination buffer contents via `memcmp` at [line 547](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L547)
4. Logging mismatches and images on failure at [lines 548-576](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L548-L576)

### Host Read Verification

When `read=true`, the `HostCopyThread::run()` method at [lines 97-157](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L97-L157) uses `vkCopyImageToMemoryEXT` and compares the data against expected values.

## Test Principles Observed

- **No barriers between copies**: Tests verify that multiple copy operations to overlapping or adjacent regions work correctly without explicit synchronization
- **Region splitting**: Uses `splitRegion()` at [lines 181-194](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L181-L194) to divide images into random-sized subregions
- **Thread-based concurrent copies**: Host copy tests use `de::Thread` to execute multiple copies concurrently
- **Layout transitions**: Tests verify proper layout handling with `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and `VK_IMAGE_LAYOUT_GENERAL`
- **2D array compatible images**: Tests verify that 3D images with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` can have their array layers treated independently

## Notes / Uncertainties

- The `hostCopy` tests (using VK_EXT_host_image_copy) are wrapped in `#ifndef CTS_USES_VULKANSC` at [lines 75-179](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L75-L179) and [lines 342-440](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L342-L440), meaning these tests are only available for Vulkan (not VulkanSC)
- `read_and_write` access type is only available when `hostCopy=true`
- For 3D images, the `2d_array_compatible` flag creates 2D-compatible views of 3D slices
- The batch size for host copy threads is 256 at [line 393](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L393)
