# vktYCbCrCopyTests.cpp

## Overview

Tests image-to-image copy operations involving YCbCr multi-planar formats. Validates that `vkCmdCopyImage` correctly copies data between YCbCr images and between YCbCr and non-YCbCr images, including support for intermediate buffer copies, disjoint images, and various tiling configurations. This file registers **three** test groups: `copy`, `single_plane_copy`, and `copy_dimensions`.

**Role:** Implementation (registers groups `ycbcr.copy`, `ycbcr.single_plane_copy`, `ycbcr.copy_dimensions`)

**Source:** [vktYCbCrCopyTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp)

## Registration Hierarchy

```text
ycbcr.copy
├── r4g4_unorm_pack8
├── r4g4b4a4_unorm_pack16
├── b4g4r4a4_unorm_pack16
├── r5g6b5_unorm_pack16
├── b5g6r5_unorm_pack16
├── r5g5b5a1_unorm_pack16
├── b5g5r5a1_unorm_pack16
├── a1r5g5b5_unorm_pack16
├── a1b5g5r5_unorm_pack16
├── r8_unorm
├── r8g8_unorm
├── r8g8b8a8_unorm
├── b8g8r8a8_unorm
├── a8b8g8r8_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a2b10g10r10_unorm_pack32
├── r16_unorm
├── r16g16_unorm
├── b10g11r11_ufloat_pack32
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
├── g16_b16r16_2plane_444_unorm
├── a4r4g4b4_unorm_pack16
└── a4b4g4r4_unorm_pack16
```

This file also registers two additional root-level groups:

```text
ycbcr.single_plane_copy
├── linear
└── optimal
```

```text
ycbcr.copy_dimensions
├── src4096x4_dst4096x4
├── src8192x4_dst8192x4
├── src16384x4_dst16384x4
├── src32768x4_dst32768x4
├── src4096x6_dst4096x6
├── src8192x6_dst8192x6
├── src16384x6_dst16384x6
├── src32768x6_dst32768x6
├── src4x4096_dst4x4096
├── src4x8192_dst4x8192
├── src4x16384_dst4x16384
├── src4x32768_dst4x32768
├── src6x4096_dst6x4096
├── src6x8192_dst6x8192
├── src6x16384_dst6x16384
└── src6x32768_dst6x32768
```

## Test Families

### copy

Default YCbCr copy tests. Tests `vkCmdCopyImage` between all YCbCr formats and compatible non-YCbCr formats from the `basicUnsignedFloatFormats` list. Generates 10 random copy regions per test, with each region copying between compatible plane pairs. Also tests copies through an intermediate buffer (`vkCmdCopyImageToBuffer` + `vkCmdCopyBufferToImage`).

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Source Format | All formats in `basicUnsignedFloatFormats` (YCbCr and non-YCbCr) | Only pairs with at least one YCbCr format and copy compatibility |
| Destination Format | All formats in `basicUnsignedFloatFormats` | Must be copy-compatible with source |
| Source Tiling | optimal, linear | `VK_IMAGE_TILING_OPTIMAL` and `VK_IMAGE_TILING_LINEAR` |
| Destination Tiling | optimal, linear | Independent of source tiling |
| Source Disjoint | false, true | `VK_IMAGE_CREATE_DISJOINT_BIT` |
| Destination Disjoint | false, true | Independent of source disjoint |
| Intermediate Buffer | false, true | Copy via buffer instead of direct image-to-image |

### single_plane_copy

Tests copying between single-planar non-YCbCr formats and single-planar YCbCr 422 formats (e.g., `VK_FORMAT_G8B8G8R8_422_UNORM`). Uses a fixed copy extent rather than random regions.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Source Format | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_G8B8G8R8_422_UNORM` | Two specific format pairs |
| Destination Format | Corresponding paired format | `R8G8B8A8 <-> G8B8G8R8_422` |
| Source Tiling | optimal, linear | |
| Destination Tiling | optimal, linear | |
| Copy Extent | Fixed per test pair | E.g., `{32,64}` or `{64,64}` |

### copy_dimensions

Tests YCbCr image copies with extreme image dimensions (very wide or very tall images). Uses a subset of representative YCbCr formats plus `VK_FORMAT_R8G8B8A8_UNORM` as a reference.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Image Dimensions | 16 combinations: wide (4096x4 through 32768x6) and tall (4x4096 through 6x32768) | Both POT and NPOT small dimensions |
| Source Format | `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, `VK_FORMAT_G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G12X4_B12X4_R12X4_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G16_B16_R16_3PLANE_420_UNORM`, `VK_FORMAT_R8G8B8A8_UNORM` | 8/10/12/16-bit YCbCr + reference |
| Destination Format | Same as source formats | Only copy-compatible pairs |
| Source/Destination Tiling | optimal, linear | |
| Source/Destination Disjoint | false, true | |

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension and `samplerYcbcrConversion` feature
- `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` or `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` for the format
- `VK_FORMAT_FEATURE_DISJOINT_BIT` for disjoint images
- Image dimensions within `maxImageDimension2D` limits

**Verification Method:**

After copying, the destination image is downloaded and compared byte-by-byte against a reference computed by copying the corresponding source data regions. For formats with padded bits (e.g., 10-bit and 12-bit packed formats), the comparison masks out don't-care LSBs (6 or 4 bits) in even-indexed bytes. A maximum of 30 byte-level errors are logged before truncation.

**Key Functions:**

- [imageCopyTest()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L477) - Main test implementation
- [genCopies()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L346) - Random copy region generation
- [initYcbcrDefaultCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807) - `copy` group population
- [initYcbcrSinglePlanarCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L870) - `single_plane_copy` group population
- [initYcbcrDimensionsCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L923) - `copy_dimensions` group population
- [createCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023) - Factory for `copy` group
- [createSinglePlanarCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1028) - Factory for `single_plane_copy` group
- [createDimensionsCopyTests()](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1033) - Factory for `copy_dimensions` group
