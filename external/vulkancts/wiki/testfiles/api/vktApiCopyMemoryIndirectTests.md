# vktApiCopyMemoryIndirectTests ([source](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp))

## Overview

Tests that verify the correctness of the VK_KHR_copy_memory_indirect extension, which provides indirect copy commands where copy parameters are sourced from device memory rather than being directly specified by the host. The file covers three distinct indirect copy scenarios: buffer-to-buffer copies via `vkCmdCopyMemoryIndirectKHR`, memory-to-image copies via `vkCmdCopyMemoryToImageIndirectKHR`, and image-to-buffer indirect readback verification. Additionally, the file includes mandatory format support checks and conditional rendering integration tests.

## Role of File

This file provides the test implementation and registration for all VK_KHR_copy_memory_indirect tests in the Vulkan CTS `api` test group. It contains four test instance classes, four test case classes, and multiple registration functions. The file is conditionally compiled out for Vulkan SC builds (guarded by `CTS_USES_VULKANSC`).

## Source Code

- Implementation: [vktApiCopyMemoryIndirectTests.cpp](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp)
- Header: [vktApiCopyMemoryIndirectTests.hpp](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp)

## Registration Path

```
api > copy_and_blit > copy_memory_indirect
```

The top-level registration function `createCopyMemoryIndirectTests` at [line 2253](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253) creates the `copy_memory_indirect` group containing:

- Buffer-to-buffer indirect copy tests organized by size/offset/count/stride/queue
- `mandatory_formats` subgroup for format feature bit verification
- `use_after_copy` subgroup (delegated to `createUseAfterXferGroup`)

Additionally, `addCopyMemoryToImageTests` at [line 2243](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243) is called from [vktApiCopiesAndBlittingTests.cpp](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) to register memory-to-image indirect tests under:
- `memory_to_image_indirect` at [line 87](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L87)
- `memory_to_image_indirect_transfer_queue` at [line 99](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L99)
- `memory_to_image_indirect_compute_queue` at [line 111](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L111)

And `addCopyImageToBufferIndirectTests` at [line 2236](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236) registers image-to-buffer indirect tests under:
- `image_to_buffer_indirect` at [line 89](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L89)
- `image_to_buffer_indirect_transfer_queue` at [line 100](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L100)
- `image_to_buffer_indirect_compute_queue` at [line 112](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L112)

## Test Hierarchy

```
copy_memory_indirect
|-- size_4
|   |-- offset_0
|   |   |-- count_0
|   |   |   |-- normal_stride
|   |   |   |   |-- graphics
|   |   |   |   |-- transfer
|   |   |   |   |-- compute
|   |   |   |-- long_stride
|   |   |       |-- graphics / transfer / compute
|   |   |-- count_1 / count_2 / count_63
|   |-- offset_4
|       |-- count_0 / count_1 / count_2 / count_63
|-- size_12 / size_full
|-- mandatory_formats
|   |-- memory_to_image
|-- use_after_copy

memory_to_image_indirect
|-- 1d_images
|   |-- tightly_sized_buffer
|   |-- larger_buffer
|   |-- array_tightly_sized_buffer
|   |-- array_all_remaining_layers
|   |-- array_not_all_remaining_layers
|   |-- array_larger_buffer
|-- 1d_additional_formats
|   |-- r8g8_unorm / r8g8_uint / a2r10g10b10_unorm / ...
|-- 2d_images
|   |-- whole / conditional_off / conditional_on
|   |-- regions
|   |-- buffer_offset / buffer_offset_relaxed
|   |-- tightly_sized_buffer / larger_buffer / tightly_sized_buffer_offset
|   |-- array / array_larger_buffer / array_tightly_sized_buffer
|   |-- array_all_remaining_layers / array_not_all_remaining_layers
|-- 2d_mipmap_images
|   |-- mip_copies_<format>_<W>x<H>
|   |-- mip_copies_<format>_<W>x<H>_<N>_layers
|-- 2d_additional_formats
|   |-- r8g8_unorm / r8g8_uint / ... / r32g32b32a32_uint
|-- 3d_images
|   |-- r8g8b8a8_copy_per_slice
|   |-- r8g8b8a8_quadrant_copies
|   |-- r32g32_sfloat_copy_per_slice
|   |-- r8g8b8a8_all_slices_at_once
|   |-- r8g8_sint_all_slices_at_once
|   |-- r32g32_sfloat_all_slices_at_once

image_to_buffer_indirect
|-- 1d_images
|-- 3d_images
```

## Test Families

### Buffer-to-Buffer Indirect Copy (CopyMemoryIndirectTestInstance)

Registered in `createCopyMemoryIndirectTests` at [line 2253](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253). Uses `CopyMemoryIndirectTestCase` at [line 2101](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2101) and `CopyMemoryIndirectTestInstance` at [line 1872](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872).

| Family | Description |
|--------|-------------|
| size_4 / offset_0 / count_0 / normal_stride / graphics | 0-copy buffer indirect with normal stride on graphics queue |
| size_4 / offset_0 / count_1 / normal_stride / graphics | 1-copy buffer indirect, 4 bytes, no offset |
| size_4 / offset_0 / count_2 / normal_stride / graphics | 2-copy buffer indirect, 4 bytes each |
| size_4 / offset_0 / count_63 / normal_stride / graphics | 63-copy buffer indirect |
| size_4 / offset_0 / count_1 / long_stride / graphics | 1-copy with stride > sizeof(VkCopyMemoryIndirectCommandKHR) |
| size_full / offset_4 / ... | Full buffer size copy with 4-byte offset |

### Memory-to-Image Indirect Copy (CopyMemoryToImageIndirect)

Registered in `addCopyMemoryToImageTests` at [line 2243](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243). Uses `CopyMemoryToImageIndirectTestCase` at [line 727](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L727) and `CopyMemoryToImageIndirect` instance at [line 322](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L322).

| Family | Description |
|--------|-------------|
| whole | Copy entire 2D image from device memory via indirect command |
| conditional_off | Same as whole but with conditional rendering predicate = 0 (copy should be skipped) |
| conditional_on | Same as whole but with conditional rendering predicate = 1 (copy should execute) |
| regions | Multiple copy regions from different buffer offsets to different image subregions |
| buffer_offset | Copy with non-zero buffer offset and image subregion offset |
| buffer_offset_relaxed | Copy with relaxed buffer offset alignment (Universal queue only) |
| tightly_sized_buffer | Buffer sized exactly to the copied subregion |
| larger_buffer | Buffer larger than needed with explicit bufferImageHeight |
| tightly_sized_buffer_offset | Tightly sized buffer with non-zero buffer offset |
| array | 16-layer array image, one copy region per layer |
| array_larger_buffer | 16-layer array with bufferImageHeight larger than image height |
| array_tightly_sized_buffer | 16-layer array with explicit row/image height per layer |
| array_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 0 |
| array_not_all_remaining_layers | Uses VK_REMAINING_ARRAY_LAYERS starting at layer 2 |

### Mipmapped Image Indirect (CopyMipmappedImageToBuffer)

Registered in `addMemoryTo2DMipImageTests` at [line 1100](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1100). Uses `CopyMipmappedImageToBufferTestCase` at [line 251](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L251) and `CopyMipmappedImageToBuffer` instance at [line 40](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L40).

| Family | Description |
|--------|-------------|
| mip_copies_<format>_<W>x<H> | 2D image with full mip chain, uploaded indirectly, verified per mip level |
| mip_copies_<format>_<W>x<H>_<N>_layers | 2D array image with N layers, uploaded indirectly, verified per mip/layer |

### 3D Image Indirect Copy

Registered in `add3dMemoryToImageTests` at [line 1642](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1642).

| Family | Description |
|--------|-------------|
| r8g8b8a8_copy_per_slice | 3D image with 16 depth slices, one copy region per slice |
| r8g8b8a8_quadrant_copies | 3D image with quadrant-based regions per depth slice |
| r32g32_sfloat_copy_per_slice | 3D image with R32G32_SFLOAT format, one region per slice |
| r8g8b8a8_all_slices_at_once | 3D image, all slices in a single region using layerCount |
| r8g8_sint_all_slices_at_once | 3D image with R8G8_SINT format, all slices at once |
| r32g32_sfloat_all_slices_at_once | 3D image with R32G32_SFLOAT format, all slices at once |

### Mandatory Format Support

Registered in `createCopyMemoryIndirectTests` at [line 2332](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2332). Uses function case with `MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests` at [line 2155](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155).

| Family | Description |
|--------|-------------|
| memory_to_image | Verifies all mandatory formats support VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR |

## Parameter Dimensions

### Buffer-to-Buffer Indirect Copy

| Dimension | Values | Source |
|-----------|--------|--------|
| Copy Count | 0, 1, 2, 63 | [line 2262](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) |
| Copy Size | 4 bytes, 12 bytes, 0 (full buffer) | [line 2269](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2269) |
| Copy Offset | 0, 4 | [line 2276](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2276) |
| Stride | sizeof(VkCopyMemoryIndirectCommandKHR), sizeof(IndirectParams) (larger) | [line 2283](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283) |
| Queue | Universal, TransferOnly, ComputeOnly | [line 2291](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291) |

### 1D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UINT (default), VK_FORMAT_R8G8B8A8_UNORM (array tests) | [line 825](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L825), [line 885](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L885) |
| Additional 1D Formats | R8G8_UNORM, R8G8_UINT, A2R10G10B10_UNORM, R16_UINT, R16_SFLOAT, R16G16_UNORM, R16G16B16A16_SNORM, R32G32_UINT, R32G32_SFLOAT, R32G32B32_UINT/SINT/SFLOAT, R32G32B32A32_UINT | [line 1081](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1081) |
| Tiling | VK_IMAGE_TILING_OPTIMAL | [line 827](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L827) |

### 2D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UINT (whole/conditional), VK_FORMAT_R8G8B8A8_UNORM (most), VK_FORMAT_R8_UNORM (buffer_offset_relaxed) | [line 1164](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1164), [line 1201](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1201), [line 1264](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1264) |
| Additional 2D Formats | R8G8_UNORM, R8G8_UINT, A2R10G10B10_UNORM, R16_UINT, R16_SFLOAT, R16G16_UNORM, R16G16B16A16_SNORM, R32G32_UINT, R32G32_SFLOAT, R32G32B32_UINT/SINT/SFLOAT (optimal + linear), R32G32B32A32_UINT | [line 1617](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1617) |
| Conditional Rendering | Off (predicate=0), On (predicate=1) | [line 1189](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1189), [line 1193](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1193) |

### 2D Mipmap Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8_UINT, VK_FORMAT_R8G8_UNORM, VK_FORMAT_R16G16_UNORM, VK_FORMAT_R32G32_UINT | [line 1105](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1105) |
| Extent | {64,64,1}, {64,192,1} | [line 1108](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1108) |
| Array Layers | 1, 2, 5 | [line 1113](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1113) |

### 3D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R32G32_SFLOAT, VK_FORMAT_R8G8_SINT | [line 1651](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1651), [line 1750](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1750), [line 1822](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1822) |
| Depth Layers | 16 | [line 1648](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1648) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_copy_memory_indirect | Required for all tests in this file | [line 786](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L786), [line 2112](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2112) |
| indirectMemoryCopy feature | Required for buffer-to-buffer indirect copy | [line 2115](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2115) |
| indirectMemoryToImageCopy feature | Required for memory-to-image indirect copy | [line 791](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L791) |
| VK_KHR_format_feature_flags2 | Required for mandatory format tests | [line 2149](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2149) |
| VK_FORMAT_FEATURE_TRANSFER_DST_BIT | Destination image format must support transfer dst | [line 754](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L754) |
| VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR | Required for indirect copy destination formats | [line 310](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L310), [line 772](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L772) |
| Copy memory indirect queue support | Checks supportedQueues for the selected queue type | [line 521](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L521), [line 2122](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2122) |
| VK_EXT_conditional_rendering | Required for conditional rendering tests | [line 809](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L809) |
| MAINTENANCE_5 | For VK_REMAINING_ARRAY_LAYERS tests | [line 938](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L938), [line 981](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L981), [line 1515](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1515), [line 1558](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1558) |
| Sparse binding | Sparse image format properties must be supported | [line 407](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L407) |
| Transfer queue granularity | When queueSelection == TransferOnly | [line 796](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L796) |

## Verification Methods

### CopyMemoryIndirectTestInstance (buffer-to-buffer)

Uses direct byte-by-byte comparison with `memcmp` at [line 2059](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2059). Source data is loaded from a test asset file at [line 1899](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1899). On failure, hex dumps of source and destination data are logged at [line 2071](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2071). The count_0 case verifies that no data was written when copyCount is 0 at [line 2079](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079).

### CopyMemoryToImageIndirect (memory-to-image)

Uses CPU-side reference comparison. The `copyRegionToTextureLevel` method at [line 427](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L427) computes the expected image contents from the source buffer data. The result is validated via `checkTestResult` at [line 724](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L724), which compares the actual image data against the expected result.

### CopyMipmappedImageToBuffer (mipmapped image indirect)

Performs per-mip-level, per-array-layer byte-by-byte comparison using `deMemCmp` at [line 237](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L237). Each mip level of the uploaded image is copied individually to a buffer and compared against the reference texture data. The destination buffer is cleared to zero before each copy at [line 160](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L160) as a precaution.

### MandatoryFormats (format feature check)

Queries `VkFormatProperties3` for each mandatory format and verifies `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` is present at [line 2215](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215). Reports all non-compliant formats before returning a pass/fail result at [line 2224](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2224).

## Test Principles Observed

- **Indirect command dispatch**: All tests exercise the indirect command path where copy parameters reside in device memory, accessed via device addresses rather than host-specified structures.
- **Stride validation**: Buffer-to-buffer tests verify both normal stride (sizeof(VkCopyMemoryIndirectCommandKHR)) and long stride (larger struct with dummy parameters) at [line 2283](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283), testing the stride field of `VkStridedDeviceAddressRangeKHR`.
- **Zero-copy count**: The count_0 test at [line 2262](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) verifies that no data is written when copyCount is 0.
- **Conditional rendering integration**: The `conditional_off` and `conditional_on` tests at [line 1189](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1189) verify that `vkCmdCopyMemoryToImageIndirectKHR` respects conditional rendering predicates.
- **Queue family coverage**: Buffer-to-buffer tests cover Universal, TransferOnly, and ComputeOnly queue families at [line 2291](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291), with queue support checked via `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR` at [line 512](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L512).
- **Mandatory format compliance**: The mandatory_formats test at [line 2155](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155) verifies that all formats mandated by the VK_KHR_copy_memory_indirect spec support the required indirect copy feature bit.
- **3D image depth handling**: For 3D images, `cmdCopyMemoryToImageIndirectKHR` uses `baseArrayLayer/layerCount` instead of `image.extent.depth` at [line 1809](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1809), which is tested explicitly.
- **Sparse binding support**: The `CopyMemoryToImageIndirect` class supports sparse image allocation at [line 405](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L405).
- **VK_ADDRESS_COPY_DEVICE_LOCAL_BIT_KHR**: Both srcCopyFlags and dstCopyFlags are set to `VK_ADDRESS_COPY_DEVICE_LOCAL_BIT_KHR` at [line 679](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L679) and [line 2020](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2020).

## Notes / Uncertainties

- The `CopyMipmappedImageToBuffer` class at [line 40](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L40) tests the round-trip path: upload image data via indirect copy, then read back via direct `vkCmdCopyImageToBuffer` and verify. The indirect path is used only for the upload step.
- The 1D additional formats tests at [line 1081](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1081) only test the `tightly_sized_buffer` scenario for each format, not the full set of buffer layout configurations.
- The `addCopyImageToBufferIndirectTests` function at [line 2236](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236) delegates to `add1dImageToBufferTests` and `add3dImageToBufferTests` from [vktApiCopyImageToBufferTests.cpp](../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp), which are not defined in this file.
- The `createUseAfterXferGroup` call at [line 2338](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) delegates to [vktApiUseAfterCopyTests.cpp](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp) with `indirect=true`.
- The source data for buffer-to-buffer tests is loaded from an external file `vulkan/data/copy_memory_indirect/sample_text.txt` at [line 1899](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1899), padded to 64-byte alignment at [line 1903](../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1903).
