## Overview

**Core question:** Does the implementation copy image subregions into a host-visible buffer with the bytes laid out exactly as the `VkBufferImageCopy` region specifies, across image types, formats, tiling modes, queue families, allocation strategies, and the three command variants `vkCmdCopyImageToBuffer`, `vkCmdCopyImageToBuffer2`, and `vkCmdCopyImageToMemoryKHR`?

- Source file: [`vktApiCopyImageToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1).
- Test category: `api`. Test family: `image_to_buffer`, registered under `api.copy_and_blit` through several dispatcher intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`, `device_address`, plus the per-queue and per-layout siblings of `core`). The dispatcher entry is [`addCopyImageToBufferTests()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L2014-L2019), called from [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L131).
- Intermediate nodes inside the test family: `1d_images`, `2d_images`, `3d_images`, populated by [`add1dImageToBufferTests()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1691), [`add2dImageToBufferTests()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1098), and [`add3dImageToBufferTests()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1974).
- Test case leaves: uncompressed 1D/2D leaves named `whole`, `whole_unaligned`, `buffer_offset`, `buffer_offset_relaxed`, `regions`, `tightly_sized_buffer`, `larger_buffer`, `tightly_sized_buffer_offset`, `array`, `array_larger_buffer`, `array_tightly_sized_buffer`, `array_all_remaining_layers`, `array_not_all_remaining_layers`, `padding_bytes`, plus compressed `mip_copies_<format>_<W>x<H>[xD][_N_layers][_N_layersindirect]` leaves.
- Core test idea: upload a known image, record an image-to-buffer copy with one or more `VkBufferImageCopy` regions, read the buffer back, and compare against a host-computed reference that mirrors the region's `bufferOffset`, `bufferRowLength`, `bufferImageHeight`, `imageOffset`, `imageExtent`, and `imageSubresource` fields.
- The page explains which behavior each leaf exercises, how the host computes expected bytes for uncompressed and compressed sources, what the `INDIRECT_COPY` and `DEVICE_ADDRESS_COMMANDS` variants change, and what a failure localizes to.

## Background Knowledge

- `vkCmdCopyImageToBuffer` copies image texels into a buffer. Each region is described by a `VkBufferImageCopy` with `bufferOffset` (byte offset into the destination buffer), `bufferRowLength` and `bufferImageHeight` (the row stride and image height in texels, where `0` means "tightly packed against `imageExtent`"), `imageSubresource` (aspect, mip level, array layer range), `imageOffset`, and `imageExtent`. The destination buffer receives texel data laid out row by row using the row stride derived from `bufferRowLength` and the per-texel size.
- `vkCmdCopyImageToBuffer2` (from `VK_KHR_copy_commands2`) takes the same data through a `VkBufferImageCopy2KHR` and a `VkCopyImageToBufferInfo2KHR` struct so multiple regions can be passed in one call. The semantics match the original command.
- `vkCmdCopyImageToMemoryKHR` (from `VK_KHR_copy_memory_indirect`) writes to a device address plus a computed size instead of a `VkBuffer` handle, using `VkDeviceMemoryImageCopyKHR` regions. The destination buffer must be created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and allocated with `MemoryRequirement::DeviceAddress`.
- Compressed formats (BC, ETC2, EAC, ASTC) store texels in fixed-size compressed blocks. Image-to-buffer copies of compressed images transfer raw compressed block bytes; the implementation does not decompress. The destination layout follows `bufferRowLength` and `bufferImageHeight`, but in texel units that translate to whole blocks.
- `VK_REMAINING_ARRAY_LAYERS` as `imageSubresource.layerCount` means "from `baseArrayLayer` to the last layer of the image". `VK_KHR_maintenance5` is required to use this sentinel in copy regions.
- Sparse binding (`VK_IMAGE_CREATE_SPARSE_BINDING_BIT` plus `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`) lets an image be backed by multiple memory bindings through `vkQueueBindSparse`. The test exercises this path only when the dispatcher enables sparse binding; a sparse semaphore synchronizes the bind operation with the copy.
- `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` is the layout the spec requires for the source image of a transfer command. `VK_IMAGE_LAYOUT_GENERAL` is a valid alternative; the `useGeneralLayout` dispatcher flag selects it to verify the general-layout path is accepted.

## Registration Hierarchy

```text
api.copy_and_blit.core.image_to_buffer
├── 1d_images
├── 2d_images
└── 3d_images
```

The same `1d_images` / `2d_images` / `3d_images` subtree is registered under each dispatcher intermediate node by [`addCopyImageToBufferTests()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L2014-L2019). The dispatcher intermediate nodes that call into this test family are listed in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp):

- `api.copy_and_blit.core.image_to_buffer`: primary, suballocated, Universal queue, no extensions ([line 131](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L131)).
- `api.copy_and_blit.core.image_to_buffer_transfer_queue`: TransferOnly queue ([line 174](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L174)).
- `api.copy_and_blit.core.image_to_buffer_compute_queue`: ComputeOnly queue ([line 186](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L186)).
- `api.copy_and_blit.core.image_to_buffer_general_layout`: `VK_IMAGE_LAYOUT_GENERAL` ([line 227](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L227)).
- `api.copy_and_blit.dedicated_allocation.image_to_buffer`: dedicated allocation.
- `api.copy_and_blit.copy_commands2.image_to_buffer`: `VK_KHR_copy_commands2` extension.
- `api.copy_and_blit.device_address.image_to_buffer`: `VK_KHR_copy_memory_indirect` device-address commands, non-VulkanSC only ([line 254](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L254)).

This page uses the `core.image_to_buffer` path as the canonical registration root because that is the primary, no-extension configuration. The other dispatcher nodes reuse the same `1d_images` / `2d_images` / `3d_images` test case set with different `TestGroupParams` (allocation kind, extension flags, queue selection, sparse binding, general layout).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type | `1d_images`, `2d_images`, `3d_images` | Selects `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D`, or `VK_IMAGE_TYPE_3D` for the source image. Compressed 1D cases actually use `VK_IMAGE_TYPE_2D` because compressed formats require 2D image types. | [`vktApiCopyImageToBufferTests.cpp#L1691`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1691), [`vktApiCopyImageToBufferTests.cpp#L1098`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1098), [`vktApiCopyImageToBufferTests.cpp#L1974`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1974) |
| Uncompressed format (2D) | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R32G32B32_UINT`, `VK_FORMAT_R32G32B32_SFLOAT` | Varies texel size (1, 4, 12 bytes) and channel count to exercise byte-level layout. The 12-byte `R32G32B32` formats stress alignment because they have no 4-byte-channel padding. | [`vktApiCopyImageToBufferTests.cpp#L1102-L1103`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1102-L1103) |
| Uncompressed format (1D) | `VK_FORMAT_R8G8B8A8_UNORM` only | Holds format fixed so 1D cases can focus on extent, array layer, and buffer sizing behavior. | [`vktApiCopyImageToBufferTests.cpp#L1698`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1698) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_TILING_LINEAR` (2D uncompressed only) | Optimal tiling is the production path; linear tiling is required by the `padding_bytes` leaf and exercises row-pitch behavior. | [`vktApiCopyImageToBufferTests.cpp#L1104`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1104), [`vktApiCopyImageToBufferTests.cpp#L1595-L1596`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1595-L1596) |
| Compressed format | `formats::compressedFormatsFloats` (BC1-BC7, ETC2, EAC, ASTC 4x4 through 12x12) | Exercises every block-compressed format with a full mip chain. Each format has a distinct block size that interacts with mip extents smaller than the block. | [`vktApiCopyImageToBufferTests.cpp#L1674`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1674), [`vktApiCopyImageToBufferTests.cpp#L1963`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1963), [`vktApiCopyImageToBufferTests.cpp#L2005`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L2005) |
| Compressed extent (2D) | `{64,64,1}`, `{64,192,1}` | The first is a power-of-two chain where every mip is a multiple of the block size; the second produces two lowest y-axis mips with widths of 3 and 1, smaller than any block width, which is the tricky case. | [`vktApiCopyImageToBufferTests.cpp#L1641-L1646`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1641-L1646) |
| Compressed extent (3D) | `{16,16,16}`, `{16,8,24}` | One power-of-two volume and one non-power-of-two volume. | [`vktApiCopyImageToBufferTests.cpp#L1978-L1982`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1978-L1982) |
| Compressed array layers | `1`, `2`, `5` (2D only) | Varies layer count to exercise per-layer mip readback. 1D compressed tests reuse the same extent set with all layers indirectly uploaded. | [`vktApiCopyImageToBufferTests.cpp#L1648`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1648) |
| Array layer range | explicit per-layer regions, `VK_REMAINING_ARRAY_LAYERS` from base `0`, `VK_REMAINING_ARRAY_LAYERS` from base `2` | Tests both explicit layer iteration and the maintenance5 sentinel for the rest of the array. | [`vktApiCopyImageToBufferTests.cpp#L1504-L1547`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1504-L1547), [`vktApiCopyImageToBufferTests.cpp#L1549-L1592`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1549-L1592) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Suballocation backs the image with a shared `VkDeviceMemory`; dedicated allocation uses one memory object per image. | [`vktApiCopiesAndBlittingTests.cpp#L131`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L131), [`vktApiCopiesAndBlittingTests.cpp#L244`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L244) |
| Extension flag set | `NONE`, `COPY_COMMANDS_2`, `DEVICE_ADDRESS_COMMANDS`, `INDIRECT_COPY` | Selects `vkCmdCopyImageToBuffer`, `vkCmdCopyImageToBuffer2`, `vkCmdCopyImageToMemoryKHR`, or the indirect-upload path for compressed source images. | [`vktApiCopiesAndBlittingUtil.hpp#L135-L143`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L135-L143) |
| Queue family | `Universal`, `TransferOnly`, `ComputeOnly` | Selects the queue family that records and submits the copy command. | [`vktApiCopiesAndBlittingTests.cpp#L131-L186`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L131-L186) |
| Image layout | `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` | The `useGeneralLayout` dispatcher flag switches to `GENERAL` to verify the alternative layout is accepted. | [`vktApiCopyImageToBufferTests.cpp#L250-L251`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L250-L251) |
| Sparse binding | `false` (default), `true` (sparse dispatcher only) | When enabled, the source image is sparse and a semaphore synchronizes the bind with the copy. | [`vktApiCopyImageToBufferTests.cpp#L116-L145`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L116-L145) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Leaves cluster into behavioral groups by what the copy region exercises: buffer sizing, buffer offset, multi-region composition, array layer range, padding integrity, or compressed mip-level readback. The intermediate nodes `1d_images`, `2d_images`, and `3d_images` only change image type; the dispatcher intermediate nodes only change allocation, queue, layout, extension, or sparse configuration.

### `whole` and `whole_unaligned`: basic whole-image copies

Tests a single region covering the full image. `whole` uses `bufferRowLength = 0` and `bufferImageHeight = 0`, so the destination layout is tightly packed against `imageExtent`. `whole_unaligned` sets `bufferRowLength` and `bufferImageHeight` to `defaultSize + 1`, larger than the image extent, so the destination has stride padding the implementation must respect. Registered for 2D only at [`vktApiCopyImageToBufferTests.cpp#L1112-L1173`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1112-L1173); executed by [`CopyImageToBuffer::iterate()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L178-L323).

### `buffer_offset` and `buffer_offset_relaxed`: non-zero destination offset

Tests a copy where `bufferOffset` is non-zero and the image subregion is offset by `defaultQuarterSize`. `buffer_offset` aligns the offset to the texel size by rounding up `defaultSize * defaultHalfSize` to a multiple of `tcu::getPixelSize(tcuFormat)`. `buffer_offset_relaxed` uses a non-texel-aligned offset of `defaultSize * defaultHalfSize + 1` rounded up to the texel size; it is registered only when `queueSelection == Universal` because the relaxed alignment is checked against the universal queue's `optimalBufferCopyOffsetAlignment`. Registered at [`vktApiCopyImageToBufferTests.cpp#L1175-L1239`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1175-L1239).

### `regions`: multiple copy regions in one command

Tests a single `vkCmdCopyImageToBuffer` call with multiple `VkBufferImageCopy` regions. Each region writes to a different buffer offset, with progressively shrinking `imageExtent` width (`defaultQuarterSize / divisor` for divisor 1, 2, 3, ...) and the same `bufferRowLength = defaultQuarterSize` and `bufferImageHeight = defaultQuarterSize`. The leaf verifies that the implementation honors per-region offsets, extents, and stride without bleeding writes between regions. Registered at [`vktApiCopyImageToBufferTests.cpp#L1241-L1282`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1241-L1282).

### `tightly_sized_buffer`, `larger_buffer`, `tightly_sized_buffer_offset`: buffer sizing

Tests three sizing variants on the same subregion. `tightly_sized_buffer` allocates exactly the bytes needed for the subregion with explicit `bufferRowLength = defaultSize` and `bufferImageHeight = defaultSize`. `larger_buffer` makes the buffer larger than needed by setting `bufferImageHeight = defaultSize + 1`. `tightly_sized_buffer_offset` combines a tight buffer with a non-zero `bufferOffset` rounded to the texel size. Registered at [`vktApiCopyImageToBufferTests.cpp#L1284-L1377`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1284-L1377).

### `array`, `array_larger_buffer`, `array_tightly_sized_buffer`: per-layer array copies

Tests a 16-layer 2D array image (or 1D array image) with one copy region per layer, each writing to a different `bufferOffset`. `array` uses tight `bufferRowLength = 0`. `array_larger_buffer` sets `bufferImageHeight = defaultHalfSize + 1` so each layer's destination has stride padding. `array_tightly_sized_buffer` sets explicit `bufferRowLength = defaultHalfSize` and `bufferImageHeight = defaultHalfSize`. Registered for 2D at [`vktApiCopyImageToBufferTests.cpp#L1379-L1502`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1379-L1502) and for 1D at [`vktApiCopyImageToBufferTests.cpp#L1756-L1839`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1756-L1839).

### `array_all_remaining_layers` and `array_not_all_remaining_layers`: `VK_REMAINING_ARRAY_LAYERS`

Tests the `VK_REMAINING_ARRAY_LAYERS` sentinel as `imageSubresource.layerCount`. `array_all_remaining_layers` starts at `baseArrayLayer = 0` and copies all 16 layers in one region. `array_not_all_remaining_layers` starts at `baseArrayLayer = 2` and copies layers 2 through 15 in one region. Both require `VK_KHR_maintenance5` (added via `extensionFlags |= MAINTENANCE_5`) and use `FILL_MODE_RED` for both image and buffer to make the per-layer byte pattern predictable. Registered at [`vktApiCopyImageToBufferTests.cpp#L1504-L1592`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1504-L1592) for 2D and [`vktApiCopyImageToBufferTests.cpp#L1841-L1927`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1841-L1927) for 1D.

### `padding_bytes`: untouched padding bytes between rows

Tests that the implementation does not overwrite bytes between rows when `bufferRowLength` is larger than `imageExtent.width`. Registered only for 2D linear-tiling images, with `extent = {2,2,1}`, `bufferRowLength = 8`, and `bufferImageHeight = 8`. The destination buffer is pre-filled with `FILL_MODE_RANDOM_GRAY` and the image with `FILL_MODE_RED`, so any non-red byte in the result indicates the implementation wrote padding bytes it should have left untouched. Excluded when sparse binding or general layout is active. Registered at [`vktApiCopyImageToBufferTests.cpp#L1594-L1638`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1594-L1638).

### `tightly_sized_buffer`, `larger_buffer`, `array_*` (1D): 1D uncompressed variants

The 1D variants of `tightly_sized_buffer`, `larger_buffer`, `array_tightly_sized_buffer`, `array_larger_buffer`, `array_all_remaining_layers`, and `array_not_all_remaining_layers` mirror the 2D leaves with `VK_IMAGE_TYPE_1D` and `default1dExtent`. The `array_larger_buffer` 1D variant uses `bufferImageHeight = defaultSize + 1` even though the image is 1D, which exercises how the implementation treats `bufferImageHeight` for a 1D source. Registered at [`vktApiCopyImageToBufferTests.cpp#L1695-L1927`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1695-L1927).

### `mip_copies_<format>_<W>x<H>[xD][_N_layers][_N_layersindirect]`: compressed mip-level readback

Tests compressed image-to-buffer copies of every format in `formats::compressedFormatsFloats` with a full mip chain. For each `(mipLevel, arrayLayer)` pair, the test clears the destination buffer to zero, copies one mip level of one layer into the buffer with a single `VkBufferImageCopy` region, then compares the raw compressed block bytes against the reference compressed data using `deMemCmp`. The `_N_layers` suffix means an N-layer 2D array image (N in `{1, 2, 5}`). The `indirect` suffix means the source image was uploaded using `vkCmdCopyMemoryToImageIndirectKHR` from a device-address buffer rather than `vkCmdCopyBufferToImage`; the image-to-buffer copy itself still uses `vkCmdCopyImageToBuffer` or `vkCmdCopyImageToBuffer2`. 3D compressed tests use `VK_IMAGE_TYPE_3D` and the `{16,16,16}` or `{16,8,24}` extents. Registered for 2D at [`vktApiCopyImageToBufferTests.cpp#L1641-L1686`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1641-L1686), for 1D (which uses `VK_IMAGE_TYPE_2D`) at [`vktApiCopyImageToBufferTests.cpp#L1947-L1971`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1947-L1971), and for 3D at [`vktApiCopyImageToBufferTests.cpp#L1991-L2011`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1991-L2011). Executed by [`CopyCompressedImageToBuffer::iterate()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L446-L685).

## Shader Analysis

No shader is involved in this test family. All work is recorded by the host through `vkCmdCopyImageToBuffer`, `vkCmdCopyImageToBuffer2`, or `vkCmdCopyImageToMemoryKHR`, and validated by host-side byte comparison against a reference computed on the host. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

### Source image setup

- For uncompressed tests, [`CopyImageToBuffer::iterate()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L178-L323) creates a `tcu::TextureLevel` of the mapped format, fills it via `generateBuffer()` with the configured fill mode, and uploads it into the source image with `uploadImage()`. The source image is created with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT` so it can be both uploaded and copied from.
- For compressed tests, [`CopyCompressedImageToBuffer::iterate()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L446-L685) builds a `pipeline::TestTexture2DArray` (or 1D array, or 3D) of the mapped compressed format with a full mip chain, writes its compressed bytes into a host-visible source buffer, and uploads them into the source image with `copyBufferToImage()` (or `copyBufferToImageIndirect()` when `INDIRECT_COPY` is set).
- When sparse binding is enabled, the source image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, memory is bound through `allocateAndBindSparseImage()`, and a sparse semaphore synchronizes the bind with the copy submission. See [`vktApiCopyImageToBufferTests.cpp#L116-L145`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L116-L145).

### Destination buffer setup

- For uncompressed tests, the destination buffer is created with `VK_BUFFER_USAGE_TRANSFER_DST_BIT` (plus `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` when `DEVICE_ADDRESS_COMMANDS` is set), sized to `m_params.dst.buffer.size * tcu::getPixelSize(m_textureFormat)`, and allocated host-visible. See [`vktApiCopyImageToBufferTests.cpp#L149-L175`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L149-L175).
- For compressed tests, the destination buffer is sized to `level0BuferSize` (the compressed size of mip level 0) and reused for each `(mipLevel, arrayLayer)` check. The buffer is cleared to zero with `deMemset` before each per-level copy as a precaution against stale data. See [`vktApiCopyImageToBufferTests.cpp#L536-L554`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L536-L554).

### Command recording and submission

- The test acquires an active execution context (queue, command buffer, command pool) from `activeExecutionCtx()`, which selects the appropriate queue family for `Universal`, `TransferOnly`, or `ComputeOnly` configurations.
- A pipeline barrier transitions the source image from `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (after upload) to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` (or `VK_IMAGE_LAYOUT_GENERAL` when `useGeneralLayout` is set). When `useGeneralLayout` is set, a memory barrier is used instead of an image barrier.
- The copy command is recorded based on `extensionFlags`:
  - `DEVICE_ADDRESS_COMMANDS` records `vk.cmdCopyImageToMemoryKHR` with `VkDeviceMemoryImageCopyKHR` regions converted from the `VkBufferImageCopy` regions plus the destination buffer's device address and a per-region byte size. See [`vktApiCopyImageToBufferTests.cpp#L254-L275`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L254-L275).
  - `COPY_COMMANDS_2` records `vk.cmdCopyImageToBuffer2` with `VkBufferImageCopy2KHR` regions. See [`vktApiCopyImageToBufferTests.cpp#L277-L294`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L277-L294).
  - Otherwise `vk.cmdCopyImageToBuffer` is recorded with `VkBufferImageCopy` regions. See [`vktApiCopyImageToBufferTests.cpp#L295-L305`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L295-L305).
- A buffer memory barrier from `TRANSFER_WRITE` to `HOST_READ` is recorded after the copy, and the command buffer is submitted and waited on via `submitCommandsAndWaitWithTransferSync()` (uncompressed, with sparse semaphore support) or `submitCommandsAndWaitWithSync()` (compressed).

### Result checking

- For uncompressed tests, the host invalidates the destination allocation, copies the bytes into a `tcu::TextureLevel`, and calls `checkTestResult()` inherited from `CopiesAndBlittingTestInstance`. The expected result is computed by [`copyRegionToTextureLevel()`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L325-L357), which mirrors the `VkBufferImageCopy` region's row length, image height, offset, and array layer to write the source texels into the expected `TextureLevel` at the right positions. The inherited comparator compares the result and expected `TextureLevel`s.
- For compressed tests, each `(mipLevel, arrayLayer)` is compared individually using `deMemCmp(referenceData, resultData, bufferSize)` at [`vktApiCopyImageToBufferTests.cpp#L636`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L636). On mismatch, the reference and result are decompressed for logging as `tcu::TestLog::ImageSet`, and the raw block bytes are hex-dumped for inspection at [`vktApiCopyImageToBufferTests.cpp#L641-L671`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L641-L671).
- The pass condition is byte-exact: any byte mismatch fails the test. There is no tolerance.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `whole`, `whole_unaligned`, `tightly_sized_buffer`, `larger_buffer` (uncompressed) | Row stride or image-height handling in the copy region, or `bufferImageHeight` larger than `imageExtent.height` not respected. |
| `buffer_offset`, `buffer_offset_relaxed` | Destination `bufferOffset` handling, including alignment to `optimalBufferCopyOffsetAlignment` for the relaxed variant. |
| `regions` | Multi-region composition: per-region `bufferOffset`, `imageExtent`, or stride isolation. |
| `array`, `array_larger_buffer`, `array_tightly_sized_buffer` | Per-layer `baseArrayLayer` handling or stride between layer destinations. |
| `array_all_remaining_layers`, `array_not_all_remaining_layers` | `VK_REMAINING_ARRAY_LAYERS` resolution from `baseArrayLayer` 0 vs 2, or maintenance5 support. |
| `padding_bytes` | Row-stride padding overwrite: the implementation wrote bytes between rows that should have been left untouched. |
| 1D `array_larger_buffer` | `bufferImageHeight` handling for a 1D source image, where `bufferImageHeight > 1` is unusual. |
| `mip_copies_*` (compressed, single layer) | Per-mip-level block layout, with focus on mip extents smaller than the compressed block size. |
| `mip_copies_*_N_layers` (compressed, multi-layer) | Per-layer mip-level iteration or `imageSubresource.baseArrayLayer` handling. |
| `mip_copies_*indirect` (compressed, indirect upload) | Source upload path divergence between `copyBufferToImageIndirect` and `copyBufferToImage`. |
| `mip_copies_*` 3D | 3D image-to-buffer layout, including `imageExtent.depth` handling for compressed volumes. |
| All leaves under `core.image_to_buffer_transfer_queue` | Transfer-only queue selection or command execution on a non-graphics, non-compute queue. |
| All leaves under `core.image_to_buffer_compute_queue` | Compute-only queue selection or command execution on a non-graphics queue. |
| All leaves under `core.image_to_buffer_general_layout` | Source image in `VK_IMAGE_LAYOUT_GENERAL` instead of `TRANSFER_SRC_OPTIMAL`. |
| All leaves under `dedicated_allocation.image_to_buffer` | Dedicated-allocation memory binding for the source image or destination buffer. |
| All leaves under `copy_commands2.image_to_buffer` | `vkCmdCopyImageToBuffer2` / `VkBufferImageCopy2KHR` translation or region passing. |
| All leaves under `device_address.image_to_buffer` | `vkCmdCopyImageToMemoryKHR` device-address resolution or per-region size computation. |
| All sparse-binding leaves | Sparse image memory binding, sparse semaphore synchronization, or resident-page handling. |

### Cause Analysis

#### Row stride and image-height handling

**Possible failure symptoms:** For `whole_unaligned`, `larger_buffer`, `array_larger_buffer`, or `tightly_sized_buffer` leaves, bytes in the destination buffer are laid out as if `bufferRowLength` and `bufferImageHeight` were `0` (tightly packed), instead of the explicit values the test passed. The mismatch appears as correct row 0 followed by wrong offsets for rows 1 and onward.

**Possible implementation causes:** Per Vulkan spec, `vkCmdCopyImageToBuffer` uses `bufferRowLength` and `bufferImageHeight` to compute the byte offset of each row and each 2D plane of the source image within the destination buffer. A driver that ignores these fields when they are non-zero, or that computes the row stride as `imageExtent.width * texelSize` instead of `bufferRowLength * texelSize`, would produce this symptom. Confirm by inspecting the failing leaf's stride parameters against the destination byte layout.

#### Destination buffer offset handling

**Possible failure symptoms:** For `buffer_offset` or `tightly_sized_buffer_offset`, the bytes at the beginning of the destination buffer are written instead of skipped, or the bytes from `bufferOffset` onward are shifted by a small amount. For `buffer_offset_relaxed`, the failure is specific to the non-texel-aligned offset case.

**Possible implementation causes:** Per Vulkan spec, `bufferOffset` is the byte offset into the destination buffer where the first texel of the copied region is written. The implementation must respect `VkPhysicalDeviceLimits::optimalBufferCopyOffsetAlignment` for the relaxed case. A driver that rounds `bufferOffset` differently, or that writes from offset 0 ignoring the supplied value, would produce this symptom. For `buffer_offset_relaxed`, check whether the driver accepts the offset but writes to the wrong location, versus rejecting the case when it should accept it.

#### Multi-region composition

**Possible failure symptoms:** For `regions`, individual regions in the destination buffer overlap, are written in the wrong order, or each region's bytes are placed at the wrong offset. Some regions may be correct while others are not.

**Possible implementation causes:** `vkCmdCopyImageToBuffer` accepts an array of `VkBufferImageCopy` regions and must process each independently. A driver that uses a single shared stride for all regions, that computes per-region `bufferOffset` incorrectly, or that truncates the region list would produce this symptom. The CTS test uses regions with shrinking `imageExtent.width` and a fixed `bufferRowLength`, so a per-region stride bug would show as progressively misaligned writes.

#### Per-layer array handling

**Possible failure symptoms:** For `array`, `array_larger_buffer`, or `array_tightly_sized_buffer`, the bytes for layer N appear at the offset for layer N-1 or N+1, or only the first layer is correct. For `array_all_remaining_layers` or `array_not_all_remaining_layers`, the bytes for layers outside the requested `baseArrayLayer` range are written, or layers inside the range are missing.

**Possible implementation causes:** Each region's `imageSubresource.baseArrayLayer` selects the source layer. The implementation must read from that layer and write to the corresponding `bufferOffset`. A driver that ignores `baseArrayLayer`, or that always reads from layer 0, would produce this symptom. For `VK_REMAINING_ARRAY_LAYERS`, the implementation must resolve the sentinel to `arrayLayers - baseArrayLayer` per Vulkan spec; a driver that resolves it to the full layer count regardless of `baseArrayLayer` would write layers 0 through `baseArrayLayer - 1` when it should not.

#### Row-stride padding overwrite

**Possible failure symptoms:** For `padding_bytes`, bytes in the destination buffer between rows (where `bufferRowLength > imageExtent.width`) are overwritten with image data instead of retaining their pre-filled `FILL_MODE_RANDOM_GRAY` pattern. The overwritten bytes appear as red image texels instead of the random gray pattern.

**Possible implementation causes:** Per Vulkan spec, when `bufferRowLength` is larger than `imageExtent.width`, the bytes between the end of one row and the start of the next in the destination buffer are not written by the copy command. A driver that writes a full `bufferRowLength * texelSize` bytes per row, instead of `imageExtent.width * texelSize`, would overwrite the padding. This leaf is registered only for linear tiling because the bug is most likely to surface when the source image itself has a row pitch that matches the destination's.

#### Compressed mip-level block layout

**Possible failure symptoms:** For `mip_copies_*` leaves, the `deMemCmp` of the destination buffer against the reference compressed data fails for one or more `(mipLevel, arrayLayer)` pairs. The failure is most likely at the smallest mip levels where the extent is smaller than the compressed block size (for example, a 3x1 or 1x1 mip with a 4x4 or larger block).

**Possible implementation causes:** Compressed image-to-buffer copies transfer whole compressed blocks. When a mip extent is smaller than the block size, the implementation must still transfer a complete block and the destination buffer must be sized for the block, not the extent. A driver that truncates the copy at the extent boundary, or that pads the destination differently from the reference, would produce this symptom. Check the failing mip level's extent against the format's block size and inspect whether the mismatch is in the block bytes themselves or in the block count.

#### Indirect upload divergence

**Possible failure symptoms:** A `mip_copies_*indirect` leaf fails while the corresponding non-indirect leaf passes. The destination buffer bytes for one or more `(mipLevel, arrayLayer)` pairs differ between the two upload paths.

**Possible implementation causes:** The `indirect` variant uploads the source compressed image using `vkCmdCopyMemoryToImageIndirectKHR` from a device-address buffer instead of `vkCmdCopyBufferToImage`. The image-to-buffer copy itself is the same command in both variants. A divergence implies that the indirect upload path wrote different bytes into the source image than the direct upload path, or that it wrote to the wrong `(mipLevel, arrayLayer)` of the image. Per Vulkan spec, both upload commands must produce identical image contents. Confirm by inspecting the indirect upload's region conversion, especially for 3D images where the indirect path uses `baseArrayLayer`/`layerCount` instead of `imageExtent.depth`.

#### 3D compressed volume layout

**Possible failure symptoms:** A 3D `mip_copies_*` leaf fails the `deMemCmp` check at one or more mip levels. The failure may be specific to the non-power-of-two extent `{16,8,24}` where the mip chain produces unusual depth extents.

**Possible implementation causes:** 3D compressed images have a depth extent that the copy command must handle as additional 2D slices. Per Vulkan spec, `imageExtent.depth` for a 3D source specifies how many slices to copy. A driver that mishandles the depth stride, or that computes the compressed block count along the depth axis incorrectly, would produce this symptom. Confirm by checking whether the failure is at a mip level whose depth is not a multiple of the block depth (for 3D-compatible compressed formats).

#### Transfer-only queue execution

**Possible failure symptoms:** All leaves under `core.image_to_buffer_transfer_queue` fail (or a subset fails), while the corresponding `core.image_to_buffer` leaves pass. The failure is queue-specific rather than command- or region-specific.

**Possible implementation causes:** Per Vulkan spec, transfer commands including `vkCmdCopyImageToBuffer` must be supported on any queue with `VK_QUEUE_TRANSFER_BIT`. A driver that does not execute the command on a transfer-only queue, or that misroutes the command to a different queue, would produce this symptom. The transfer-only queue is selected by `QueueSelectionOptions::TransferOnly`; `checkSupport()` validates `minImageTransferGranularity` against the source extent and each region's `imageExtent` before execution.

#### General layout source image

**Possible failure symptoms:** All leaves under `core.image_to_buffer_general_layout` fail, while the corresponding `core.image_to_buffer` leaves pass. The copy command records a memory barrier instead of an image barrier because the source stays in `VK_IMAGE_LAYOUT_GENERAL` throughout.

**Possible implementation causes:** Per Vulkan spec, `vkCmdCopyImageToBuffer` accepts `VK_IMAGE_LAYOUT_GENERAL` as a source layout. A driver that rejects the layout, that fails to make the image's contents available from a general layout, or that requires the layout transition that the test deliberately omits would produce this symptom. Confirm by checking whether the failure is in the layout validation or in the actual copy execution.

#### Dedicated allocation binding

**Possible failure symptoms:** All leaves under `dedicated_allocation.image_to_buffer` fail (or a subset fails), while the corresponding `core.image_to_buffer` leaves pass. The failure may correlate with image size or with the destination buffer's host-visible requirement.

**Possible implementation causes:** Dedicated allocation creates one `VkDeviceMemory` object per resource. A driver that does not correctly bind memory for dedicated image allocations, or that returns a different host-visible mapping for the dedicated destination buffer, would produce this symptom. `checkSupport()` requires `VK_KHR_dedicated_allocation` for the dedicated path.

#### Copy commands2 translation

**Possible failure symptoms:** All leaves under `copy_commands2.image_to_buffer` fail, while the corresponding `core.image_to_buffer` leaves pass. The failure implies the `vkCmdCopyImageToBuffer2` path diverges from the `vkCmdCopyImageToBuffer` path.

**Possible implementation causes:** `vkCmdCopyImageToBuffer2` takes the same data through `VkBufferImageCopy2KHR` and `VkCopyImageToBufferInfo2KHR`. The CTS test converts each `VkBufferImageCopy` to a `VkBufferImageCopy2KHR` field-by-field via `convertvkBufferImageCopyTovkBufferImageCopy2KHR`. A driver that misreads one of the converted fields, or that processes the region array differently between the two command variants, would produce this symptom. Confirm by inspecting whether the conversion preserves all fields including `imageSubresource`.

#### Device-address command resolution

**Possible failure symptoms:** All leaves under `device_address.image_to_buffer` fail, while the corresponding `core.image_to_buffer` leaves pass. The destination buffer receives either no data or data at the wrong offset.

**Possible implementation causes:** `vkCmdCopyImageToMemoryKHR` resolves the destination from a `VkDeviceMemoryImageCopyKHR` containing the buffer's device address plus a per-region byte size. The CTS test computes the size as `max(bufferRowLength, imageExtent.width) * max(bufferImageHeight, imageExtent.height) * pixelSize`. A driver that miscomputes the destination address (for example, ignores the per-region offset added to the base address), or that uses the wrong size for the destination range, would produce this symptom. The destination buffer is created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and `MemoryRequirement::DeviceAddress`; a failure to surface the device address would also produce this symptom.

#### Sparse image binding

**Possible failure symptoms:** Sparse-binding leaves fail while non-sparse leaves pass. The failure may be intermittent if it depends on which pages are resident at copy time.

**Possible implementation causes:** Sparse images are backed by multiple memory bindings bound through `vkQueueBindSparse`. The test binds the source image via `allocateAndBindSparseImage` and synchronizes the bind with the copy using a sparse semaphore submitted with `submitCommandsAndWaitWithTransferSync`. A driver that does not correctly bind sparse pages, that does not honor the semaphore, or that copies from non-resident pages would produce this symptom. `checkSupport()` rejects sparse formats that do not support sparse residency via `getPhysicalDeviceImageFormatProperties`. If the failure is intermittent, source-level investigation of the sparse binding sequence is needed.

## Case Pruning

### Requirement-based pruning

- `device_address.image_to_buffer` requires `VK_KHR_copy_memory_indirect` (gated as `DEVICE_ADDRESS_COMMANDS`) and is non-VulkanSC only. `checkExtensionSupport()` throws `NotSupportedError` if the extension is missing. See [`vktApiCopyImageToBufferTests.cpp#L381`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L381) and [`vktApiCopiesAndBlittingTests.cpp#L248-L258`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L248-L258).
- `copy_commands2.image_to_buffer` requires `VK_KHR_copy_commands2` (gated as `COPY_COMMANDS_2`). Same `checkExtensionSupport()` path.
- `dedicated_allocation.image_to_buffer` requires `VK_KHR_dedicated_allocation`. See [`vktApiCopyImageToBufferTests.cpp#L375-L378`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L375-L378).
- `array_all_remaining_layers` and `array_not_all_remaining_layers` require `VK_KHR_maintenance5`, added via `extensionFlags |= MAINTENANCE_5`. See [`vktApiCopyImageToBufferTests.cpp#L1522`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1522) and [`vktApiCopyImageToBufferTests.cpp#L1567`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1567).
- The source image format must support `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT`. `checkSupport()` queries `getPhysicalDeviceImageFormatProperties` and throws `NotSupportedError` if the format is unsupported or lacks the bit. See [`vktApiCopyImageToBufferTests.cpp#L383-L391`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L383-L391) (uncompressed) and [`vktApiCopyImageToBufferTests.cpp#L706-L813`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L706-L813) (compressed).
- The device must support enough array layers and mip levels for the requested image. See [`vktApiCopyImageToBufferTests.cpp#L393-L394`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L393-L394) and [`vktApiCopyImageToBufferTests.cpp#L745-L749`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L745-L749).
- `TransferOnly` queue selection validates `minImageTransferGranularity` against the source image extent and each region's `imageExtent`. See [`vktApiCopyImageToBufferTests.cpp#L397-L405`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L397-L405).
- `INDIRECT_COPY` (compressed only, non-VulkanSC) requires `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for the source format and queue support in `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR.supportedQueues`. See [`vktApiCopyImageToBufferTests.cpp#L751-L809`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L751-L809).
- Sparse binding requires the source format to support `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`. The constructor queries `getPhysicalDeviceImageFormatProperties` with those flags and throws `NotSupportedError` on `VK_ERROR_FORMAT_NOT_SUPPORTED`. See [`vktApiCopyImageToBufferTests.cpp#L128-L137`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L128-L137).

### Design-based pruning

- `buffer_offset_relaxed` is registered only for the Universal queue because the relaxed alignment is only meaningful against the universal queue's `optimalBufferCopyOffsetAlignment`. See [`vktApiCopyImageToBufferTests.cpp#L1207`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1207).
- `padding_bytes` is registered only for linear tiling, non-sparse, non-general-layout images because the row-padding behavior it tests is specific to linear tiling and the pre-fill pattern would be overwritten by the general-layout memory barrier path. See [`vktApiCopyImageToBufferTests.cpp#L1594-L1597`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1594-L1597).
- 1D compressed tests use `VK_IMAGE_TYPE_2D` because the Vulkan spec requires compressed formats to use 2D image types. The naming reflects the dispatcher placement under `1d_images`, not the actual image type. See [`vktApiCopyImageToBufferTests.cpp#L1947-L1971`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1947-L1971) and the source comment at [`vktApiCopyImageToBufferTests.cpp#L1951`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1951).
- 1D uncompressed tests use only `VK_FORMAT_R8G8B8A8_UNORM` and `VK_IMAGE_TILING_OPTIMAL` to keep the 1D matrix small; the format and tiling axes are exercised by the 2D leaves.
- The `CopyMipmappedImageToBuffer` class is defined at [`vktApiCopyImageToBufferTests.cpp#L816-L1025`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L816-L1025) but is not registered by any `add*ImageToBufferTests` function in this file. It appears to be unused or registered elsewhere; source-level investigation is needed to confirm whether it is dead code.
- Compressed 1D tests use `INDIRECT_COPY` in every case (set at [`vktApiCopyImageToBufferTests.cpp#L1961`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1961)) and do not generate a non-indirect counterpart, unlike 2D which generates both. The reason is not documented in source comments.

## Key Takeaways

- The family tests three command paths (`vkCmdCopyImageToBuffer`, `vkCmdCopyImageToBuffer2`, `vkCmdCopyImageToMemoryKHR`) under seven dispatcher configurations, sharing the same `1d_images` / `2d_images` / `3d_images` test case set and the same host-side verification infrastructure.
- The uncompressed leaves exercise the `VkBufferImageCopy` region fields one at a time: `bufferOffset`, `bufferRowLength`, `bufferImageHeight`, `imageOffset`, `imageExtent`, and `imageSubresource`. The `padding_bytes` leaf is the only one that explicitly verifies untouched destination bytes.
- The compressed leaves verify byte-exact raw block transfer for every block-compressed format, with special attention to mip extents smaller than the block size (the `{64,192,1}` extent) and to 3D volumes with non-power-of-two depth.
- `VK_REMAINING_ARRAY_LAYERS` is tested from two distinct `baseArrayLayer` values (0 and 2) to confirm the sentinel resolves relative to the base, not as a fixed full-array count.
- The `indirect` compressed variants isolate the source upload path: a divergence between `indirect` and non-indirect leaves points to `vkCmdCopyMemoryToImageIndirectKHR`, not to the image-to-buffer copy command.
- Failures localize differently: a failure only in `device_address.image_to_buffer` points to `vkCmdCopyImageToMemoryKHR`; a failure only in `copy_commands2.image_to_buffer` points to `vkCmdCopyImageToBuffer2`; a failure only in `padding_bytes` points to row-stride padding overwrite; a failure only in `mip_copies_*indirect` points to the indirect upload path. See `## Failure Meaning` for details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `addCopyImageToBufferTests()` registration | [`vktApiCopyImageToBufferTests.cpp#L2014-L2019`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L2014-L2019) | Owns the test family tree and dispatches to the three `add*ImageToBufferTests` functions. |
| `add2dImageToBufferTests()` | [`vktApiCopyImageToBufferTests.cpp#L1098-L1687`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1098-L1687) | Registers the 2D uncompressed leaves and the 2D compressed `mip_copies_*` leaves. |
| `add1dImageToBufferTests()` | [`vktApiCopyImageToBufferTests.cpp#L1691-L1972`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1691-L1972) | Registers the 1D uncompressed leaves and the 1D compressed `mip_copies_*` leaves (using `VK_IMAGE_TYPE_2D`). |
| `add3dImageToBufferTests()` | [`vktApiCopyImageToBufferTests.cpp#L1974-L2012`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1974-L2012) | Registers the 3D compressed `mip_copies_*` leaves. |
| `CopyImageToBuffer` instance | [`vktApiCopyImageToBufferTests.cpp#L65-L357`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L65-L357) | Runs the uncompressed image-to-buffer copy and computes the expected `TextureLevel`. |
| `CopyCompressedImageToBuffer` instance | [`vktApiCopyImageToBufferTests.cpp#L412-L685`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L412-L685) | Runs the compressed per-mip-level readback and `deMemCmp` check. |
| `CopyMipmappedImageToBuffer` instance | [`vktApiCopyImageToBufferTests.cpp#L816-L1025`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L816-L1025) | Defined but not registered by this file; suspected dead code or registered elsewhere. |
| `CopyImageToBufferTestCase::checkSupport()` | [`vktApiCopyImageToBufferTests.cpp#L373-L406`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L373-L406) | Gates dedicated allocation, extensions, format support, array layers, and transfer-queue granularity. |
| `CopyCompressedImageToBufferTestCase::checkSupport()` | [`vktApiCopyImageToBufferTests.cpp#L706-L814`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L706-L814) | Gates compressed format support, mip levels, `INDIRECT_COPY` features, and queue support. |
| `copyRegionToTextureLevel()` | [`vktApiCopyImageToBufferTests.cpp#L325-L357`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L325-L357) | Mirrors the `VkBufferImageCopy` region to write expected texels into the host reference. |
| Test params and extension flags | [`vktApiCopiesAndBlittingUtil.hpp#L135-L143`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L135-L143), [`vktApiCopiesAndBlittingUtil.hpp#L334-L344`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L334-L344) | Defines `COPY_COMMANDS_2`, `INDIRECT_COPY`, `DEVICE_ADDRESS_COMMANDS`, `MAINTENANCE_5`, `SPARSE_BINDING` and the `TestGroupParams` struct. |
| Parent dispatcher | [`vktApiCopiesAndBlittingTests.cpp#L131`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L131) | Adds `image_to_buffer` to `core` under `copy_and_blit`. Other dispatcher registrations at lines [174](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L174), [186](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L186), [227](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L227), and [254](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L254). |
