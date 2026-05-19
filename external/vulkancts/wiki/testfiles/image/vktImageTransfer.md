# vktImageTransfer.cpp

## Overview

Tests for image transfer operations (copying data between buffers and images) using optimal tiling. The tests verify that data integrity is maintained when transferring pixel data between host buffers and device images across various image types, extents, and formats.

## Role of File

This is a registration and implementation file that:
- Registers the `queue_transfer` test group
- Provides test cases for buffer-to-image and image-to-buffer copy operations
- Tests multiple image types, extents, and basic color formats
- Uses optimal tiling images with general layout

## Source Code Link

[vktImageTransfer.cpp](../../../modules/vulkan/image/vktImageTransfer.cpp)

## Registration Hierarchy

```text
image.queue_transfer
├── 2d
�?  ├── 4x3x1
�?  ├── 16x15x1
�?  ├── 64x31x1
�?  ├── 4x3x2
�?  └── 16x15x16
├── 2d_array
�?  ├── 4x3x1
�?  ├── 16x15x1
�?  ├── 64x31x1
�?  ├── 4x3x2
�?  └── 16x15x16
└── 3d
    ├── 4x3x1
    ├── 16x15x1
    ├── 64x31x1
    ├── 4x3x2
    └── 16x15x16
```

## Test Families

### basic_transfer �?Buffer-Image Transfer Tests

Tests the round-trip transfer of image data through host-visible buffers:

**Test approach** ([vktImageTransfer.cpp#L157-L293](../../../modules/vulkan/image/vktImageTransfer.cpp#L157-L293)):

1. **Data generation**: Generate random data appropriate to the image format using `fillRandomNoNaN()`
2. **Source buffer fill**: Copy generated data to host-visible source buffer
3. **Buffer to image copy**: Transfer data from source buffer to image using `vkCmdCopyBufferToImage`
4. **Image to buffer copy**: Transfer data from image to destination buffer using `vkCmdCopyImageToBuffer`
5. **Verification**: Compare destination buffer data byte-by-byte with original generated data

**Key implementation details**:
- Uses `VK_IMAGE_LAYOUT_GENERAL` for all image operations
- Creates optimal tiling images with transfer usage flags
- Calculates buffer size based on pixel format, dimensions, and aspect
- Handles compressed formats by adjusting image height to block boundaries

**Test flow** ([vktImageTransfer.cpp#L221-L273](../../../modules/vulkan/image/vktImageTransfer.cpp#L221-L273)):
```
Begin command buffer
  -> Pipeline barrier (UNDEFINED -> GENERAL)
  -> CmdCopyBufferToImage (srcBuffer -> image)
  -> Pipeline barrier (WRITE -> READ)
  -> CmdCopyImageToBuffer (image -> dstBuffer)
End command buffer
Submit and wait
Verify dstBuffer == srcBuffer
```

## Parameter Dimensions

| Parameter | Values |
|-----------|--------|
| Image Types | VK_IMAGE_TYPE_2D, VK_IMAGE_TYPE_3D |
| Image Classes | 2D, 2D_array, 3D |
| Formats | formats::basicColorFormats |
| Extents | 5 predefined extents (see below) |
| Mip Levels | 1 |
| Array Layers | For 2D_array: extent.depth; For 2D: 1; For 3D: 1 |
| Depth | For 3D: extent.depth; For 2D/2D_array: 1 |
| Sample Count | 1 |

**Extent configurations** ([vktImageTransfer.cpp#L332-L336](../../../modules/vulkan/image/vktImageTransfer.cpp#L332-L336)):

| Extent Name | Dimensions | Description |
|-------------|------------|-------------|
| 4x3x1 | 4 x 3 x 1 | Small 2D |
| 16x15x1 | 16 x 15 x 1 | Medium 2D |
| 64x31x1 | 64 x 31 x 1 | Larger 2D |
| 4x3x2 | 4 x 3 x 2 | 2D with depth/layers |
| 16x15x16 | 16 x 15 x 16 | 3D or 2D array |

**Buffer size calculation** ([vktImageTransfer.cpp#L172](../../../modules/vulkan/image/vktImageTransfer.cpp#L172)):
```cpp
const uint32_t pixelDataSize = tcuFormat.getPixelSize() * width * height * layers * depth;
```

## Support Requirements

- **Format properties check** ([vktImageTransfer.cpp#L119-L130](../../../modules/vulkan/image/vktImageTransfer.cpp#L119-L130)):
  - `vkGetPhysicalDeviceImageFormatProperties` must return VK_SUCCESS
  - VK_ERROR_FORMAT_NOT_SUPPORTED results in NotSupportedError

- **Format features** ([vktImageTransfer.cpp#L133-L139](../../../modules/vulkan/image/vktImageTransfer.cpp#L133-L139)):
  - `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT`
  - `VK_FORMAT_FEATURE_TRANSFER_DST_BIT`
  - For optimal tiling

- **Image tiling**: `VK_IMAGE_TILING_OPTIMAL`

- **Image usage**: `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`

- **Conditional requirements**:
  - `VK_KHR_maintenance5` for formats VK_FORMAT_A8_UNORM_KHR and VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR

## Verification Methods

1. **Byte-by-byte comparison** ([vktImageTransfer.cpp#L283-L289](../../../modules/vulkan/image/vktImageTransfer.cpp#L283-L289)):
   ```cpp
   for (uint32_t i = 0; i < pixelDataSize; ++i)
   {
       if (resultData[i] != generatedData[i])
       {
           return tcu::TestStatus::fail("Transfer queue test");
       }
   }
   ```

2. **Return on first mismatch**: Test fails immediately upon detecting any byte difference

3. **Data integrity verification**:
   - Uses same random seed generation based on format, type, and dimensions
   - `fillRandomNoNaN()` ensures no invalid values for the format type

## Test Principles Observed

- Round-trip testing: buffer -> image -> buffer
- Single mip level (1) to simplify testing
- All array layers and 3D depth tested as part of the extent
- Optimal tiling used for realistic device memory handling
- General layout provides maximum flexibility for transfer operations
- Random data generation with format-appropriate constraints
- Uses exclusive sharing mode for simplicity

## Notes

- Tests use `VK_SHARING_MODE_EXCLUSIVE` with single queue family
- Compressed formats handled by calculating block-aligned image heights
- BufferImageCopy uses 0 for bufferRowLength and calculated bufferImageHeight for packed data
- 2D array images interpret extent.depth as the number of array layers
- 3D images interpret extent.depth as the actual 3D depth dimension
