# vktYCbCrStorageImageWriteTests.cpp

## Overview

[`vktYCbCrStorageImageWriteTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp) implements the `ycbcr.storage_image_write` subgroup returned by [`createStorageImageWriteTests()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939-L942). It writes to each plane of a YCbCr image through compute storage-image descriptors, copies the result to a host-visible buffer, and verifies per-channel expected data in [`testStorageImageWrite()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L240-L470).

## Registration Hierarchy

```text
ycbcr.storage_image_write
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── b16g16r16g16_422_unorm
├── b8g8r8g8_422_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g16b16g16r16_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8r8_2plane_444_unorm
├── g8b8g8r8_422_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
└── r12x4g12x4b12x4a12x4_unorm_4pack16
```

[`populateStorageImageWriteFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L884-L934) iterates the YCbCr base range and 2-plane 444 EXT range, creates one direct child per format, then creates size subgroups and `joint`/`disjoint` cases below each format.

## Test Families

### storage_image_write

Each plane gets its own storage image view, descriptor set, compute pipeline, dispatch, and transfer-to-buffer path in [`testStorageImageWrite()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L313-L441). Disjoint multi-planar cases use plane views for transfer, while joint cases use the whole image storage capability where supported by [`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L191-L214).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Formats | `VK_YCBCR_FORMAT_FIRST` to `VK_YCBCR_FORMAT_LAST`, plus `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM_EXT` to `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT`, in [`populateStorageImageWriteFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L923-L932). |
| Sizes | `{512,512,1}`, `{1024,128,1}`, and `{66,32,1}` are generated and skipped when not aligned to `getImageSizeAlignment(format)` in [`populateStorageImageWriteFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L887-L905). |
| Joint/disjoint | `joint` uses no create flags; `disjoint` uses `VK_IMAGE_CREATE_DISJOINT_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` in [`populateStorageImageWriteFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L911-L916). |
| Compatible plane format | Plane-compatible formats may be remapped for storage-image writing by [`getPlaneCompatibleFormatForWriting()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L67-L84). |

## Support / Feature Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L89-L215) requires bind-memory extensions for disjoint cases when they are not core, checks image-format and plane-compatible image-format support, adds `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` when the writable plane format differs from the image format, requires whole-format storage-image support for joint cases, requires disjoint format support for disjoint cases, and requires plane-compatible storage-image support when disjoint plane views are used.

## Verification Method

[`testStorageImageWrite()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L407-L470) computes per-plane buffer offsets, copies image planes to a buffer with `vkCmdCopyImageToBuffer`, invalidates host memory, and then verifies channel data from the copied buffer. Fixed-point tolerances and exact integer comparisons are handled later in the same function after the per-channel plane pointers are established.

## Notes / Uncertainties

The page describes the generator and verification path; actual case availability depends on storage-image and disjoint support reported by the device.
