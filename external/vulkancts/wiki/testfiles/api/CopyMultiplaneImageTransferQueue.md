## Overview

**Core question:** does a dedicated Vulkan transfer queue reproduce the exact bytes the `VkImageCopy` layout specifies when copying planes of multiplane (YCbCr) images, across the 19 multiplane YCbCr formats, disjoint and non-disjoint allocations, and both the direct `vkCmdCopyImage` path and the indirect `vkCmdCopyImageToBuffer` → `vkCmdCopyBufferToImage` path?

- Covers the implementation-bearing `multiplanar_xfer` test family under `api.copy_and_blit`, registered through the `copy_and_blit` dispatcher in `vktApiCopiesAndBlittingTests.cpp`.
- The single implementation file `vktApiCopyMultiplaneImageTransferQueueTests.cpp` (~870 lines) owns the `testCopies` test function, the `checkSupport` gate, the `genCopies` random-region generator, and one registration function.
- Uses `addFunctionCase` rather than the class-based pattern used by sibling copy test files. The 19 source-format groups under `multiplanar_xfer` enumerate copy-compatible destination-format subgroups, and each subgroup generates 8 standard test case leaves by iterating source disjoint, destination disjoint, and intermediate-buffer flags.
- The page explains how plane-pair matching works, why disjoint and non-disjoint allocations exercise different driver paths, what the LSB don't-care tolerance covers for 10-bit and 12-bit format pairs, and what a failure of each behavioral group points to.

## Background Knowledge

- **Multiplane YCbCr image formats.** A multiplane format stores luma (Y) and chroma (Cb/Cr) in separate memory planes within a single `VkImage`. `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` has three 8-bit planes; `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM` (NV12-style) interleaves Cb and Cr into a single 2-channel plane 1. Each plane is exposed through its own `VkImageAspectFlagBits` (`VK_IMAGE_ASPECT_PLANE_0_BIT`, `_PLANE_1_BIT`, `_PLANE_2_BIT`) and behaves as a single-plane image in a plane-compatible format such as `R8_UNORM`, `R10X6_UNORM_PACK16`, `R12X4_UNORM_PACK16`, or `R16_UNORM`.
- **Chroma subsampling and plane extents.** 4:2:0 halves chroma width and height relative to luma; 4:2:2 halves width only; 4:4:4 has no subsampling. For a 64×64 4:2:0 image the Y plane is 64×64 and each chroma plane is 32×32. Copy regions are aligned to plane block units through `getBlockExtent` so that offsets and extents stay valid across subsamplings.
- **Disjoint image allocation.** `VK_IMAGE_CREATE_DISJOINT_BIT` binds each plane to a separate `VkDeviceMemory` allocation. Without it, all planes share one allocation. Disjoint is gated by `VK_FORMAT_FEATURE_DISJOINT_BIT` and additionally requires each plane-compatible format to be supported.
- **Transfer queue and `minImageTransferGranularity`.** A dedicated transfer queue family exposes only `VK_QUEUE_TRANSFER_BIT`. Its `VkQueueFamilyProperties::minImageTransferGranularity` constrains copy region offsets and extents to multiples of the granularity. The test aligns every generated region to this granularity.
- **LSB don't-care tolerance for 10-bit and 12-bit planes.** `R10X6_UNORM_PACK16` stores 10 meaningful bits in a 16-bit container; `R12X4_UNORM_PACK16` stores 12. When such plane-compatible formats are copied between plane layouts, the lower 6 bits (10-bit) or 4 bits (12-bit) of each even byte are implementation-defined. The comparison masks those bits: `0xC0` for 10-bit pairs and `0xF0` for 12-bit pairs.

## Registration Hierarchy

```text
api.copy_and_blit.multiplanar_xfer
├── g8_b8_r8_3plane_420_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
└── g16_b16r16_2plane_422_unorm
```

Each source-format group contains destination-format subgroups for every copy-compatible format from the same 19-format list, and each destination-format subgroup generates 8 standard test case leaves. The 16-bit format set omits 4:4:4 because the Vulkan core spec does not define `VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Source format | 19 multiplane YCbCr formats (8-bit, 10-bit, 12-bit, 16-bit; 4:2:0, 4:2:2, 4:4:4; 2-plane and 3-plane) | Selects plane count, plane-compatible formats, chroma subsampling, and bit depth; affects LSB tolerance and which plane pairs are valid | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L777-L795`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L777-L795) |
| Destination format | Same 19 formats (only copy-compatible pairs are generated) | Pairs with the source format to determine plane-pair matches; cross-subsampling and cross-plane-count pairs are exercised when at least one plane pair is compatible | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L817-L825`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L817-L825) |
| Source tiling | `VK_IMAGE_TILING_OPTIMAL` only | Linear is enumerated but skipped; multiplane linear images are rarely supported | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L828-L839`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L828-L839) |
| Destination tiling | `VK_IMAGE_TILING_OPTIMAL` only | Same skip rule as source tiling | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L828-L839`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L828-L839) |
| Source disjoint | `true`, `false` | When true, `VK_IMAGE_CREATE_DISJOINT_BIT` is set and each plane is bound to a separate allocation | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L841`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L841) |
| Destination disjoint | `true`, `false` | Same as source disjoint, applied to the destination image | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L842`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L842) |
| Intermediate buffer | `true`, `false` | When true, copies go through `vkCmdCopyImageToBuffer` → `vkCmdCopyBufferToImage`; when false, `vkCmdCopyImage` is used directly | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L843`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L843) |
| Copy count per test case | 10 | Number of random copy regions generated per test case; affects region diversity but not pass/fail threshold | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L496`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L496) |
| Image size | 64×64 | Fixed for every YCbCr format; non-YCbCr fallback (23×17) is unreachable because every format in the list is YCbCr | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L814`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L814) |
| Error log cap | 30 | Comparison stops after 30 mismatches; the failure message reports either the exact count or `30+` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L674`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L674) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group** formed by clustering the 8 standard test case leaves. Each leaf name encodes source tiling, source disjoint flag, optional `buffer` indicator, destination tiling, and destination disjoint flag. Leaves cluster into two groups by the recorded command path; the disjoint flag combination varies within each group as a secondary axis.

A tertiary axis (source/destination format bit depth) is relevant only to LSB tolerance application: 10-bit format pairs trigger the `0xC0` mask and 12-bit format pairs trigger the `0xF0` mask on even bytes.

The 8 standard leaves generated per source×destination format pair are:

| Test case leaf | Source disjoint | Destination disjoint | Path |
|----------------|-----------------|----------------------|------|
| `optimal_optimal` | false | false | direct `vkCmdCopyImage` |
| `optimal_optimal_disjoint` | false | true | direct `vkCmdCopyImage` |
| `optimal_disjoint_optimal` | true | false | direct `vkCmdCopyImage` |
| `optimal_disjoint_optimal_disjoint` | true | true | direct `vkCmdCopyImage` |
| `optimal_buffer_optimal` | false | false | indirect via `vkCmdCopyImageToBuffer` → `vkCmdCopyBufferToImage` |
| `optimal_buffer_optimal_disjoint` | false | true | indirect via buffer |
| `optimal_disjoint_buffer_optimal` | true | false | indirect via buffer |
| `optimal_disjoint_buffer_optimal_disjoint` | true | true | indirect via buffer |

### `direct_copy` group — `vkCmdCopyImage` plane-to-plane copy

Records a single `vkCmdCopyImage` per generated region with `srcImage` in `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and `dstImage` in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`. The region's `srcSubresource.aspectMask` and `dstSubresource.aspectMask` select one plane each (for example `VK_IMAGE_ASPECT_PLANE_0_BIT`), and the offset/extent are aligned to the transfer queue's `minImageTransferGranularity`. A `VkImageMemoryBarrier` on the destination (layout stays `TRANSFER_DST_OPTIMAL`, `TRANSFER_WRITE` → `TRANSFER_READ|TRANSFER_WRITE`) separates consecutive copies so each copy's write is visible to the next. This group exercises the implementation's direct plane-to-plane copy path on the transfer queue.

### `indirect_buffer_copy` group — image → buffer → image plane copy

Records `vkCmdCopyImageToBuffer` from the source plane into a per-region intermediate `VkBuffer`, followed by a `VkBufferMemoryBarrier` with `TRANSFER_WRITE` → `TRANSFER_READ` and `VK_QUEUE_FAMILY_IGNORED` for both queue family indices, followed by `vkCmdCopyBufferToImage` from the buffer into the destination plane. The intermediate buffer is sized to `srcSize.x() * srcSize.y() * blockSizeBytes` where `blockSizeBytes` comes from the source plane-compatible format. This group exercises the implementation's image-to-buffer and buffer-to-image plane handling and the inter-copy buffer barrier.

## Shader Analysis

This test family does not use shaders. All work is recorded through `vkCmdCopyImage`, `vkCmdCopyImageToBuffer`, and `vkCmdCopyBufferToImage`. No `### Representative Shader Walkthrough` subsection is needed.

## Runtime Execution and Result Checking

- `checkSupport` first verifies that `context.getTransferQueueFamilyIndex() != -1`, throwing `NotSupportedError` if the device has no dedicated transfer queue family. It then checks `limits.maxImageDimension2D` against the 64×64 size and calls `checkFormatSupport` for both source and destination.
- `checkFormatSupport` queries `vkGetPhysicalDeviceImageFormatProperties2` for the multiplane format with `TRANSFER_DST | SAMPLED` usage. When the disjoint flag is set, it additionally queries each plane-compatible format. It then verifies `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` or `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` is present, and `VK_FORMAT_FEATURE_DISJOINT_BIT` is present when disjoint is requested.
- `testCopies` queries the transfer queue family's `minImageTransferGranularity`, seeds a `de::Random` from `6792903u` plus the source and destination `ImageConfig`, and generates 10 `VkImageCopy` regions via `genCopies`. Each region picks a `(srcPlaneNdx, dstPlaneNdx)` pair from the compatible pairs and aligns offsets and extent to the granularity.
- Source and destination `MultiPlaneImageData` are filled with random bytes via `fillRandom`, avoiding NaN patterns for float-looking plane formats (`chooseFloatFormat` picks the float format if either source or destination is float).
- Source and destination `VkImage` objects are created with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, `VK_IMAGE_TILING_OPTIMAL`, and `VK_IMAGE_CREATE_DISJOINT_BIT` when disjoint is set. Memory is allocated and bound per-plane when disjoint, or as a single allocation otherwise.
- `uploadImage` transitions both images from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and copies the host-side random fill into device memory via the universal queue. The image memory barriers use `VK_QUEUE_FAMILY_IGNORED` for both source and destination queue family indices, so no explicit queue-family ownership transfer is recorded between universal upload and transfer copy. The test relies on `submitCommandsAndWait` on the universal queue to provide the host-level synchronization point.
- A transfer-queue command pool and primary command buffer are allocated. For each of the 10 copies, an intermediate `VkBuffer` is allocated (always, even on the direct path where it is unused). The recorded commands follow the `direct_copy` or `indirect_buffer_copy` path described above. A `VkImageMemoryBarrier` on the destination ends each copy.
- The command buffer is submitted on the dedicated transfer queue via `submitCommandsAndWaitWithSync`.
- The destination image is downloaded via `downloadImage` on the transfer queue family into a host-side `MultiPlaneImageData` result.
- The host computes a reference by starting from the destination's initial random fill and `deMemcpy`-ing each `VkImageCopy` region's source plane bytes into the corresponding destination plane at the block-aligned offset.
- Byte-by-byte comparison with optional LSB masking:
  - `0xFF` mask for 8-bit and 16-bit format pairs (every bit must match);
  - `0xC0` mask on even bytes for 10-bit (`R10X6*`) format pairs;
  - `0xF0` mask on even bytes for 12-bit (`R12X4*`) format pairs.
- Up to 30 mismatches are logged before the comparison stops. The test returns `pass` if zero errors are found, or `fail("Failed, found N incorrect bytes")` otherwise.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `direct_copy` group (4 `optimal_*_optimal[_disjoint]` leaves) | `vkCmdCopyImage` per-plane copy mechanics: aspect/plane selection, plane offset/extent math, or per-plane layout handling on the transfer queue. |
| `indirect_buffer_copy` group (4 `optimal_*_buffer_*` leaves) | `vkCmdCopyImageToBuffer` + `vkCmdCopyBufferToImage` plane handling, the inter-copy buffer barrier (`TRANSFER_WRITE`→`TRANSFER_READ`), or buffer size/offset computation. |
| Any `_disjoint_` leaf (source or destination disjoint) | `VK_IMAGE_CREATE_DISJOINT_BIT` per-plane memory binding, plane-compatible format support queries, or per-plane memory offset computation. |
| All leaves under 10-bit source formats (`g10x6_*`) | LSB6 don't-care tolerance: implementation-defined low 6 bits of even bytes produce values outside the `0xC0` mask. |
| All leaves under 12-bit source formats (`g12x4_*`) | LSB4 don't-care tolerance: implementation-defined low 4 bits of even bytes produce values outside the `0xF0` mask. |
| All leaves under cross-plane-count pairs (e.g., 3-plane → 2-plane) | Plane-pair matching in `genCopies`: implementation rejects or mishandles cross-plane-count copies that the spec permits because each plane is independent. |
| All leaves under cross-subsampling pairs (e.g., 4:2:0 → 4:2:2) | Chroma plane extent computation or block-vs-texel scaling when source and destination chroma resolutions differ. |
| All leaves (regardless of group or format) | Transfer-queue-specific: `minImageTransferGranularity` alignment, queue synchronization between universal upload and transfer copy, or transfer-queue submission. |

### Cause Analysis

#### Direct plane-to-plane copy failures

**Possible failure symptoms:** bytes within the requested plane region of the destination do not bit-exactly match the source plane's bytes (after LSB masking when applicable); bytes outside the requested region match the destination's initial random fill, indicating no over-write.

**Possible implementation causes:** the driver selects the wrong plane when `aspectMask` is `VK_IMAGE_ASPECT_PLANE_1_BIT` or `_PLANE_2_BIT`; per-region `srcOffset` / `dstOffset` / `extent` arithmetic is off for chroma planes whose block extent differs from luma; the implementation reads or writes outside the requested plane region; or the transfer-queue copy path produces different bytes than the universal-queue copy path would.

#### Indirect image-buffer-image copy failures

**Possible failure symptoms:** only `optimal_*_buffer_*` leaves fail while `optimal_*_optimal[_disjoint]` leaves pass; bytes within the requested region mismatch; or specific plane pairs (typically the larger Y plane) fail while smaller chroma planes pass.

**Possible implementation causes:** `vkCmdCopyImageToBuffer` writes the wrong byte count or row pitch for the plane (the test sets `bufferRowLength` and `bufferImageHeight` to 0, meaning tight packing); the `VkBufferMemoryBarrier` between write and read does not correctly synchronize on the transfer queue; `vkCmdCopyBufferToImage` reads from the wrong buffer offset; or the buffer size computation (`srcSize.x() * srcSize.y() * blockSizeBytes`) overflows or underflows for specific plane-compatible formats.

#### Disjoint allocation failures

**Possible failure symptoms:** only leaves with `srcDisjoint` or `dstDisjoint` set fail; non-disjoint leaves pass; or failures are isolated to one specific plane in a disjoint image, suggesting the wrong allocation was read or written.

**Possible implementation causes:** the driver reports `VK_FORMAT_FEATURE_DISJOINT_BIT` but cannot actually bind planes separately; per-plane memory binding in `allocateAndBindImageMemory` produces wrong offsets for one plane; the copy path reads from a default allocation rather than the per-plane allocation; or the plane-compatible format support query in `checkFormatSupport` passes but the driver rejects the plane-compatible format at copy time.

#### LSB don't-care tolerance failures

**Possible failure symptoms:** only `g10x6_*` source format pairs fail (LSB6) or only `g12x4_*` source format pairs fail (LSB4); mismatches are confined to even bytes (the high byte of the 16-bit container) and the low 6 or 4 bits differ; 8-bit and 16-bit format pairs pass.

**Possible implementation causes:** the implementation writes nonzero low bits where the reference expects zero, or writes high bits that differ from the canonical value the host reference computes. Whether the LSB values are spec-legal is implementation-defined; the test only requires the masked high bits to match. If failures persist outside the masked bits, the cause is in the copy mechanics rather than the LSB tolerance.

#### Cross-plane-count copy failures

**Possible failure symptoms:** only leaves where source and destination have different plane counts fail (for example 3-plane `g8_b8_r8_3plane_420_unorm` source to 2-plane `g8_b8r8_2plane_420_unorm` destination); same-plane-count pairs pass.

**Possible implementation causes:** the driver rejects cross-plane-count copies that the spec permits because each plane is independent; or `genCopies` selects a plane pair that the driver mishandles (for example, source plane 2 of a 3-plane format mapping to destination plane 1 of a 2-plane format). The Vulkan spec allows `vkCmdCopyImage` between any plane pair whose plane-compatible formats are size-compatible, so a driver that errors out on cross-plane-count copies is non-conformant.

#### Cross-subsampling copy failures

**Possible failure symptoms:** only leaves where source and destination have different subsampling (for example 4:2:0 source to 4:2:2 destination) fail; same-subsampling pairs pass.

**Possible implementation causes:** the driver miscalculates chroma plane extents when source and destination chroma resolutions differ; or the block-vs-texel scaling in the copy region extent arithmetic differs from what `genCopies` computes. The host reference uses `getPlaneExtent` per plane, so a driver that uses a single extent for both source and destination chroma planes will mismatch.

#### Transfer-queue-specific failures

**Possible failure symptoms:** all leaves fail regardless of format or disjoint combination; or failures are intermittent and timing-dependent.

**Possible implementation causes:** the transfer queue's `minImageTransferGranularity` is reported coarser than the implementation actually requires, causing `genCopies` to generate regions that violate the implementation's real granularity; the implementation does not correctly synchronize the universal-queue upload with the transfer-queue copy when `VK_QUEUE_FAMILY_IGNORED` is used (the test relies on `submitCommandsAndWait` providing a host-level synchronization point); or the transfer-queue submission in `submitCommandsAndWaitWithSync` does not correctly wait for completion before the download. Whether the test exercises explicit queue-family ownership transfer is unclear from source inspection alone — `VK_QUEUE_FAMILY_IGNORED` is used for all image and buffer memory barriers, so no explicit ownership transfer is recorded; source-level investigation is needed to confirm whether `submitCommandsAndWaitWithSync` provides additional synchronization beyond `vkQueueWaitIdle`.

## Case Pruning

### Requirement-based pruning

- A dedicated transfer queue family is required. `checkSupport` throws `NotSupportedError` when `context.getTransferQueueFamilyIndex() == -1`, so the entire test family is skipped on devices without a transfer-only queue family.
- The 64×64 image size must fit within `limits.maxImageDimension2D`; otherwise `checkSupport` throws `NotSupportedError`.
- The format must support `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` or `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` for the requested tiling. `checkFormatSupport` skips the case otherwise.
- When the disjoint flag is set, the format must support `VK_FORMAT_FEATURE_DISJOINT_BIT` and each plane-compatible format must be supported via `vkGetPhysicalDeviceImageFormatProperties2`. The case is skipped otherwise.
- `vkGetPhysicalDeviceImageFormatProperties2` must succeed for the multiplane format; `VK_ERROR_FORMAT_NOT_SUPPORTED` skips the case.

### Design-based pruning

- Linear tiling is enumerated in the `tilings` array but skipped by the `if (srcTiling == VK_IMAGE_TILING_LINEAR || dstTiling == VK_IMAGE_TILING_LINEAR) continue;` guard. Multiplane linear images are rarely supported, and the test never exercises them.
- Destination formats are filtered by `isCopyCompatible(srcFormat, dstFormat)` so only format pairs with at least one compatible plane pair are generated. This avoids invalid configurations.
- The 16-bit format set intentionally omits 4:4:4 because `VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM` is not defined by the Vulkan core spec.
- The `createFlags` vector at line 797 declares `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, `CUBE_COMPATIBLE_BIT`, `ALIAS_BIT`, `2D_ARRAY_COMPATIBLE_BIT`, `EXTENDED_USAGE_BIT`, and `SAMPLE_LOCATIONS_COMPATIBLE_DEPTH_BIT_EXT`, but these flags are never iterated. Only `VK_IMAGE_CREATE_DISJOINT_BIT` is conditionally applied. The declared flags appear to be inherited boilerplate from sibling copy test files and have no effect on test behavior.

## Key Takeaways

- The test exercises two different copy paths, clustered as the primary behavioral axis: direct `vkCmdCopyImage` and indirect `vkCmdCopyImageToBuffer` → `vkCmdCopyBufferToImage`. The disjoint flag combination varies memory binding but not the recorded commands.
- All copy regions are aligned to the transfer queue's `minImageTransferGranularity`, so a driver whose real granularity is coarser than reported will fail even when universal-queue copies pass.
- The comparison is byte-by-byte with LSB masking only on even bytes of 10-bit (`0xC0`) and 12-bit (`0xF0`) format pairs. Failures outside the masked bits point to copy mechanics, not LSB tolerance.
- Cross-plane-count and cross-subsampling copies are generated whenever at least one plane pair is size-compatible. A driver that rejects these copies is non-conformant because the Vulkan spec treats each plane as an independent single-plane image.
- Disjoint-only failures isolate the cause to `VK_IMAGE_CREATE_DISJOINT_BIT` per-plane memory binding or plane-compatible format support; non-disjoint leaves exercise the shared-allocation path.
- The test uses `VK_QUEUE_FAMILY_IGNORED` for all image and buffer memory barriers and relies on `submitCommandsAndWait` for host-level synchronization; no explicit queue-family ownership transfer is recorded.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ImageConfig` / `TestConfig` structs | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L39-L67`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L39-L67) | Carry source/destination format, tiling, disjoint flag, size, and the `intermediateBuffer` switch. |
| `checkFormatSupport` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L69-L140`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L69-L140) | Validates multiplane format support, transfer features, and per-plane disjoint support. |
| `checkSupport` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L142-L157`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L142-L157) | Validates dedicated transfer queue family existence and image dimension limits. |
| `isCompatible` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L159-L209`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L159-L209) | Per-plane copy compatibility by texel block size class (8/16/24/32/48/64/96/128/192/256-bit). |
| `genCopies` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221-L295`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221-L295) | Generates 10 random plane-pair copy regions aligned to the transfer queue's `minImageTransferGranularity`. |
| `createImage` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L350-L373`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L350-L373) | Creates a `VkImage` with optional `VK_IMAGE_CREATE_DISJOINT_BIT` and `TRANSFER_SRC | TRANSFER_DST` usage. |
| `getBlockByteSize` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375-L434`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375-L434) | Returns byte size for plane-compatible formats; fatal-exits on multiplane formats. |
| `isCopyCompatible` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436-L483`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436-L483) | Format-pair filter used by the registration loop. |
| `testCopies` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485-L765`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485-L765) | Test body: creates images, allocates memory, uploads, records copies, submits on transfer queue, downloads, compares. |
| Reference computation and comparison | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L672-L755`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L672-L755) | Host-side reference memcpy and byte-by-byte comparison with LSB masking. |
| `createCopyMultiplaneImageTransferQueueTests` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769-L867`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769-L867) | Registration loop: 19 source formats × compatible destinations × 8 leaves per pair. |
| Test header | [`vktApiCopyMultiplaneImageTransferQueueTests.hpp`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.hpp) | Declares the public `createCopyMultiplaneImageTransferQueueTests` entry point. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L283`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283) | Adds `multiplanar_xfer` directly under `copy_and_blit`. |
| LSB tolerance helpers | [`vktYCbCrUtil.cpp#L1023-L1077`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1023-L1077) | `areLsb6BitsDontCare` and `areLsb4BitsDontCare` define which format pairs trigger LSB masking. |
| `MultiPlaneImageData` and upload/download helpers | [`vktYCbCrUtil.hpp#L58-L191`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.hpp#L58-L191) | Planar host-side data structure and the upload/download/fill helpers used by the test. |
| `uploadImage` | [`vktYCbCrUtil.cpp#L420-L491`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L420-L491) | Universal-queue upload path; uses `VK_QUEUE_FAMILY_IGNORED` for all image memory barriers. |
