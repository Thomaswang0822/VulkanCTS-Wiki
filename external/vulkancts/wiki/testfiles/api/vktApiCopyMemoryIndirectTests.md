# vktApiCopyMemoryIndirectTests ([source](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp))

## Overview

Tests that verify the correctness of the VK_KHR_copy_memory_indirect extension, which provides indirect copy commands where copy parameters are sourced from device memory rather than being directly specified by the host. The file covers three distinct indirect copy scenarios: buffer-to-buffer copies via `vkCmdCopyMemoryIndirectKHR`, memory-to-image copies via `vkCmdCopyMemoryToImageIndirectKHR`, and image-to-buffer indirect readback verification. Additionally, the file includes mandatory format support checks and conditional rendering integration tests.

## Role of File

This file provides the test implementation and registration for all VK_KHR_copy_memory_indirect tests in the Vulkan CTS `api` test group. It contains four test instance classes, four test case classes, and multiple registration functions. The file is conditionally compiled out for Vulkan SC builds (guarded by `CTS_USES_VULKANSC`).

## Source Code

- Implementation: [vktApiCopyMemoryIndirectTests.cpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp)
- Header: [vktApiCopyMemoryIndirectTests.hpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp)

## Registration Hierarchy

```text
api.copy_and_blit.copy_memory_indirect
├── size_4
├── size_12
├── size_full
├── mandatory_formats
└── use_after_copy
```

Evidence:
- `copy_memory_indirect` group created by [`createCopyMemoryIndirectTests()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253)
- `size_4`, `size_12`, `size_full` subgroups added in the copy-size loop at [line 2295](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2295) through [line 2329](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2329)
- `mandatory_formats` subgroup added at [line 2332](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2332)
- `use_after_copy` subgroup added via [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) with `indirect=true`

This file also provides `addCopyMemoryToImageTests()` at [line 2243](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243) and `addCopyImageToBufferIndirectTests()` at [line 2236](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236), which register indirect copy tests under `api.copy_and_blit.core` and `api.copy_and_blit.dedicated_allocation` (via [`addIndirectCopyTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74) in [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp)). Those registrations are documented in [vktApiCopiesAndBlittingTests.md](./vktApiCopiesAndBlittingTests.md).

## Test Families

### size_4 -- Buffer-to-buffer indirect copy (4 bytes)

Registered in [`createCopyMemoryIndirectTests()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253). Uses `CopyMemoryIndirectTestCase` at [line 2101](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2101) and `CopyMemoryIndirectTestInstance` at [line 1872](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872).

The `size_4` subgroup contains buffer-to-buffer indirect copy tests with a 4-byte copy size. Each test is organized into a hierarchy of offset, count, stride, and queue subgroups:

- `offset_0` / `offset_4` -- copy offset in bytes ([line 2276](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2276))
  - `count_0` / `count_1` / `count_2` / `count_63` -- number of indirect copy commands ([line 2262](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262))
    - `normal_stride` / `long_stride` -- stride between indirect commands ([line 2283](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283))
      - `graphics` / `transfer` / `compute` -- target queue family ([line 2291](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291))

Note: combinations where `offset >= size` are skipped at [line 2313](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2313), so `offset_4` does not appear under `size_4`.

### size_12 -- Buffer-to-buffer indirect copy (12 bytes)

Same test structure as `size_4` but with a 12-byte copy size. The `offset_4` subgroup is present here (since 4 < 12), adding additional offset/count/stride/queue combinations.

### size_full -- Buffer-to-buffer indirect copy (full buffer)

Same test structure as `size_4` and `size_12` but with `copySize = 0`, which signals a full-buffer copy. Both `offset_0` and `offset_4` subgroups are present.

### mandatory_formats -- Mandatory format support verification

Registered at [line 2332](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2332). Uses function case with `MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests` at [line 2155](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155).

Contains a single child `memory_to_image` that verifies all mandatory formats support `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR`.

### use_after_copy -- Use-after-copy verification (indirect)

Added via [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) with `indirect=true`. Implementation is delegated to [vktApiUseAfterCopyTests.cpp](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp), which verifies that image contents copied via indirect commands can still be consumed correctly afterward (sampled as texture or used as depth/stencil attachment). See [vktApiUseAfterCopyTests.md](./vktApiUseAfterCopyTests.md) for full documentation of the `use_after_copy` test structure.

## Cross-File Registrations

This file provides implementation functions that are called from [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) to register indirect copy tests under `api.copy_and_blit.core` and `api.copy_and_blit.dedicated_allocation`. These are not children of `copy_memory_indirect` but are documented here because their implementation resides in this file.

### addCopyMemoryToImageTests -- Memory-to-image indirect copy

Called from [`addIndirectCopyTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74) to register under `memory_to_image_indirect`, `memory_to_image_indirect_transfer_queue`, and `memory_to_image_indirect_compute_queue`. Uses `CopyMemoryToImageIndirectTestCase` at [line 727](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L727) and `CopyMemoryToImageIndirect` instance at [line 322](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L322).

Direct children of each `memory_to_image_indirect` group:

- `1d_images` -- 1D image indirect copy tests (tightly_sized_buffer, larger_buffer, array variants)
- `1d_additional_formats` -- Additional format coverage for 1D images
- `2d_images` -- 2D image indirect copy tests (whole, conditional_off/on, regions, buffer_offset, tightly_sized_buffer, array variants)
- `2d_mipmap_images` -- Mipmapped 2D image indirect copy tests
- `2d_additional_formats` -- Additional format coverage for 2D images
- `3d_images` -- 3D image indirect copy tests

### addCopyImageToBufferIndirectTests -- Image-to-buffer indirect copy

Called from [`addIndirectCopyTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74) to register under `image_to_buffer_indirect`, `image_to_buffer_indirect_transfer_queue`, and `image_to_buffer_indirect_compute_queue`. Delegates to `add1dImageToBufferTests` and `add3dImageToBufferTests` from [vktApiCopyImageToBufferTests.cpp](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp).

Direct children of each `image_to_buffer_indirect` group:

- `1d_images` -- 1D image-to-buffer indirect tests
- `3d_images` -- 3D image-to-buffer indirect tests

## Parameter Dimensions

### Buffer-to-Buffer Indirect Copy

| Dimension | Values | Source |
|-----------|--------|--------|
| Copy Count | 0, 1, 2, 63 | [line 2262](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) |
| Copy Size | 4 bytes, 12 bytes, 0 (full buffer) | [line 2269](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2269) |
| Copy Offset | 0, 4 | [line 2276](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2276) |
| Stride | sizeof(VkCopyMemoryIndirectCommandKHR), sizeof(IndirectParams) (larger) | [line 2283](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283) |
| Queue | Universal, TransferOnly, ComputeOnly | [line 2291](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291) |

### 1D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UINT (default), VK_FORMAT_R8G8B8A8_UNORM (array tests) | [line 825](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L825), [line 885](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L885) |
| Additional 1D Formats | R8G8_UNORM, R8G8_UINT, A2R10G10B10_UNORM, R16_UINT, R16_SFLOAT, R16G16_UNORM, R16G16B16A16_SNORM, R32G32_UINT, R32G32_SFLOAT, R32G32B32_UINT/SINT/SFLOAT, R32G32B32A32_UINT | [line 1081](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1081) |
| Tiling | VK_IMAGE_TILING_OPTIMAL | [line 827](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L827) |

### 2D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UINT (whole/conditional), VK_FORMAT_R8G8B8A8_UNORM (most), VK_FORMAT_R8_UNORM (buffer_offset_relaxed) | [line 1164](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1164), [line 1201](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1201), [line 1264](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1264) |
| Additional 2D Formats | R8G8_UNORM, R8G8_UINT, A2R10G10B10_UNORM, R16_UINT, R16_SFLOAT, R16G16_UNORM, R16G16B16A16_SNORM, R32G32_UINT, R32G32_SFLOAT, R32G32B32_UINT/SINT/SFLOAT (optimal + linear), R32G32B32A32_UINT | [line 1617](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1617) |
| Conditional Rendering | Off (predicate=0), On (predicate=1) | [line 1189](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1189), [line 1193](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1193) |

### 2D Mipmap Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8_UINT, VK_FORMAT_R8G8_UNORM, VK_FORMAT_R16G16_UNORM, VK_FORMAT_R32G32_UINT | [line 1105](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1105) |
| Extent | {64,64,1}, {64,192,1} | [line 1108](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1108) |
| Array Layers | 1, 2, 5 | [line 1113](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1113) |

### 3D Memory-to-Image Tests

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R32G32_SFLOAT, VK_FORMAT_R8G8_SINT | [line 1651](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1651), [line 1750](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1750), [line 1822](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1822) |
| Depth Layers | 16 | [line 1648](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1648) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_copy_memory_indirect | Required for all tests in this file | [line 786](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L786), [line 2112](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2112) |
| indirectMemoryCopy feature | Required for buffer-to-buffer indirect copy | [line 2115](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2115) |
| indirectMemoryToImageCopy feature | Required for memory-to-image indirect copy | [line 791](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L791) |
| VK_KHR_format_feature_flags2 | Required for mandatory format tests | [line 2149](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2149) |
| VK_FORMAT_FEATURE_TRANSFER_DST_BIT | Destination image format must support transfer dst | [line 754](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L754) |
| VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR | Required for indirect copy destination formats | [line 310](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L310), [line 772](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L772) |
| Copy memory indirect queue support | Checks supportedQueues for the selected queue type | [line 521](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L521), [line 2122](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2122) |
| VK_EXT_conditional_rendering | Required for conditional rendering tests | [line 809](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L809) |
| MAINTENANCE_5 | For VK_REMAINING_ARRAY_LAYERS tests | [line 938](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L938), [line 981](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L981), [line 1515](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1515), [line 1558](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1558) |
| Sparse binding | Sparse image format properties must be supported | [line 407](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L407) |
| Transfer queue granularity | When queueSelection == TransferOnly | [line 796](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L796) |

## Verification Methods

### CopyMemoryIndirectTestInstance (buffer-to-buffer)

Uses direct byte-by-byte comparison with `memcmp` at [line 2059](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2059). Source data is loaded from a test asset file at [line 1899](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1899). On failure, hex dumps of source and destination data are logged at [line 2071](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2071). The count_0 case verifies that no data was written when copyCount is 0 at [line 2079](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079).

### CopyMemoryToImageIndirect (memory-to-image)

Uses CPU-side reference comparison. The `copyRegionToTextureLevel` method at [line 427](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L427) computes the expected image contents from the source buffer data. The result is validated via `checkTestResult` at [line 724](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L724), which compares the actual image data against the expected result.

### CopyMipmappedImageToBuffer (mipmapped image indirect)

Performs per-mip-level, per-array-layer byte-by-byte comparison using `deMemCmp` at [line 237](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L237). Each mip level of the uploaded image is copied individually to a buffer and compared against the reference texture data. The destination buffer is cleared to zero before each copy at [line 160](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L160) as a precaution.

### MandatoryFormats (format feature check)

Queries `VkFormatProperties3` for each mandatory format and verifies `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` is present at [line 2215](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215). Reports all non-compliant formats before returning a pass/fail result at [line 2224](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2224).

## Test Principles Observed

- **Indirect command dispatch**: All tests exercise the indirect command path where copy parameters reside in device memory, accessed via device addresses rather than host-specified structures.
- **Stride validation**: Buffer-to-buffer tests verify both normal stride (sizeof(VkCopyMemoryIndirectCommandKHR)) and long stride (larger struct with dummy parameters) at [line 2283](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283), testing the stride field of `VkStridedDeviceAddressRangeKHR`.
- **Zero-copy count**: The count_0 test at [line 2262](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) verifies that no data is written when copyCount is 0.
- **Conditional rendering integration**: The `conditional_off` and `conditional_on` tests at [line 1189](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1189) verify that `vkCmdCopyMemoryToImageIndirectKHR` respects conditional rendering predicates.
- **Queue family coverage**: Buffer-to-buffer tests cover Universal, TransferOnly, and ComputeOnly queue families at [line 2291](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291), with queue support checked via `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR` at [line 512](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L512).
- **Mandatory format compliance**: The mandatory_formats test at [line 2155](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155) verifies that all formats mandated by the VK_KHR_copy_memory_indirect spec support the required indirect copy feature bit.
- **3D image depth handling**: For 3D images, `cmdCopyMemoryToImageIndirectKHR` uses `baseArrayLayer/layerCount` instead of `image.extent.depth` at [line 1809](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1809), which is tested explicitly.
- **Sparse binding support**: The `CopyMemoryToImageIndirect` class supports sparse image allocation at [line 405](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L405).
- **VK_ADDRESS_COPY_DEVICE_LOCAL_BIT_KHR**: Both srcCopyFlags and dstCopyFlags are set to `VK_ADDRESS_COPY_DEVICE_LOCAL_BIT_KHR` at [line 679](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L679) and [line 2020](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2020).

## Notes / Uncertainties

- The `CopyMipmappedImageToBuffer` class at [line 40](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L40) tests the round-trip path: upload image data via indirect copy, then read back via direct `vkCmdCopyImageToBuffer` and verify. The indirect path is used only for the upload step.
- The 1D additional formats tests at [line 1081](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1081) only test the `tightly_sized_buffer` scenario for each format, not the full set of buffer layout configurations.
- The `addCopyImageToBufferIndirectTests` function at [line 2236](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236) delegates to `add1dImageToBufferTests` and `add3dImageToBufferTests` from [vktApiCopyImageToBufferTests.cpp](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp), which are not defined in this file.
- The `createUseAfterXferGroup` call at [line 2338](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) delegates to [vktApiUseAfterCopyTests.cpp](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp) with `indirect=true`.
- The source data for buffer-to-buffer tests is loaded from an external file `vulkan/data/copy_memory_indirect/sample_text.txt` at [line 1899](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1899), padded to 64-byte alignment at [line 1903](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1903).
