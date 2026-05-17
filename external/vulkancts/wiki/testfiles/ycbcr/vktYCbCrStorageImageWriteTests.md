# vktYCbCrStorageImageWriteTests.cpp

## Overview

Tests compute shader writing to multi-planar YCbCr images via storage image descriptors (`VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`). Validates that `imageStore` operations on individual planes of a multi-planar image produce correct data. Supports both joint and disjoint image creation, with plane views used for disjoint multi-planar images.

**Role:** Implementation (registers group `ycbcr.storage_image_write`)

**Source:** [vktYCbCrStorageImageWriteTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp)

## Registration Hierarchy

```text
ycbcr.storage_image_write
├── g8b8g8r8_422_unorm
├── b8g8r8g8_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
├── r12x4g12x4b12x4a12x4_unorm_4pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g16b16g16r16_422_unorm
├── b16g16r16g16_422_unorm
├── g16_b16_r16_3plane_420_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g8_b8r8_2plane_444_unorm
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
└── g16_b16r16_2plane_444_unorm
```

## Test Families

### storage_image_write

Verifies that compute shaders can write to individual planes of multi-planar YCbCr images via `imageStore`. Each plane is written by a separate compute dispatch with a plane-specific shader. After writing, the image data is read back and compared against the expected pattern (X-coordinate for R channel, Y-coordinate for G channel, Z-coordinate for B channel, 1.0 for alpha).

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | All YCbCr formats (`VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST`, plus 444 EXT formats) | Each format gets its own subgroup |
| Image Size | `{512, 512, 1}`, `{1024, 128, 1}`, `{66, 32, 1}` | Skipped if not aligned to format's block size |
| Disjoint | joint, disjoint | Joint = single memory; Disjoint = per-plane memory with `VK_IMAGE_CREATE_DISJOINT_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` |

**Support Requirements:**

- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` for the format (joint mode)
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` for plane compatible formats (disjoint mode)
- `VK_FORMAT_FEATURE_DISJOINT_BIT` for disjoint tests
- `VK_KHR_bind_memory2` and `VK_KHR_get_memory_requirements2` for disjoint (if not core)
- `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is automatically added when the plane compatible format differs from the image format

**Verification Method:**

After compute shader execution, the image data is read back via `vkCmdCopyImageToBuffer`. Each channel is verified against the expected value pattern:
- R channel: `offsetX % 127` (integer) or `float(offsetX % 127) / 127.0` (float)
- G channel: `offsetY % 127` / 127.0
- B channel: `offsetZ % 127` / 127.0
- A channel: 1.0

For fixed-point formats, an additional fixed-point error tolerance is added via `tcu::TexVerifierUtil::computeFixedPointError()`. For integer formats, exact matching is used.

**Key Functions:**

- [testStorageImageWrite()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L240) - Main test implementation
- [getPlaneCompatibleFormatForWriting()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L67) - Maps plane formats to storage-compatible formats (e.g., `G8B8G8R8_422` -> `R8G8B8A8_UNORM`)
- [populateStorageImageWriteFormatGroup()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L884) - Test case generation
- [createStorageImageWriteTests()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939) - Factory function returning the `storage_image_write` group
