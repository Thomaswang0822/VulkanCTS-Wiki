# Understanding Brief: `multiplanar_xfer` test family

## One-Sentence Test Purpose

This test checks whether multiplane (YCbCr) image copies executed on a dedicated transfer queue reproduce the exact bytes the Vulkan `VkImageCopy` layout specifies, across 19 multiplane YCbCr source formats, copy-compatible destination formats, disjoint and non-disjoint allocations, and both the direct `vkCmdCopyImage` path and the indirect `vkCmdCopyImageToBuffer` → `vkCmdCopyBufferToImage` path.

## Background Knowledge

### Multiplane YCbCr image formats

A multiplane (planar) YCbCr format stores luma (Y) and chroma (Cb/Cr) in separate memory planes within a single `VkImage`. The Vulkan `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` format, for example, has three 8-bit single-channel planes: plane 0 is Y, plane 1 is Cb, plane 2 is Cr. Two-plane formats such as `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM` (NV12-style) interleave Cb and Cr into a single 2-channel plane 1. The CTS source enumerates 19 multiplane formats at [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L777-L795`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L777-L795), covering 8-bit, 10-bit (`_3PACK16`), 12-bit (`_3PACK16`), and 16-bit texel sizes, with 4:2:0, 4:2:2, and 4:4:4 chroma subsampling.

Why it matters here:

- A multiplane image exposes one `VkImageAspectFlagBits` per plane (`VK_IMAGE_ASPECT_PLANE_0_BIT`, `_PLANE_1_BIT`, `_PLANE_2_BIT`). Each `VkImageCopy` region copies exactly one plane, identified by `aspectMask`. The test chooses a plane pair per region in [`genCopies`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221-L295).
- Each plane behaves as a single-plane image in a "plane-compatible" format: `R8_UNORM` for 8-bit planes, `R10X6_UNORM_PACK16` for 10-bit, `R12X4_UNORM_PACK16` for 12-bit, `R16_UNORM` for 16-bit, and `R10X6G10X6_UNORM_2PACK16` (etc.) for 2-channel 2-plane chroma planes. Copy compatibility between planes is decided by these plane-compatible formats through [`isCompatible`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L159-L209) and [`isCopyCompatible`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436-L483).

### Chroma subsampling and plane extents

4:2:0 subsampling means chroma samples are half the width and half the height of luma; 4:2:2 means half the width only; 4:4:4 means no subsampling. Plane extents therefore differ: for a 64×64 4:2:0 image, the Y plane is 64×64, but each chroma plane is 32×32. The test computes plane extents through `vk::getPlaneExtent` and uses block units (texels divided by `getBlockExtent`) when generating copy regions.

Why it matters here:

- A driver that miscalculates chroma plane extents, or that mishandles the block-vs-texel scaling for the copy region extent, will fail the byte-level comparison even when the copy command itself runs.
- Cross-subsampling copies (e.g., 4:2:0 source to 4:2:2 destination) are legal as long as plane-compatible formats match. The test exercises them because `genCopies` matches planes by compatibility, not by subsampling equality.

### Disjoint image allocation

`VK_IMAGE_CREATE_DISJOINT_BIT` allows each plane of a multiplane image to be bound to a separate `VkDeviceMemory` allocation. Without this flag, all planes share one allocation. Disjoint support is gated by `VK_FORMAT_FEATURE_DISJOINT_BIT` for the format, and the test additionally verifies each plane-compatible format is supported via [`checkFormatSupport`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L69-L140) before using the disjoint flag.

Why it matters here:

- A driver that reports `VK_FORMAT_FEATURE_DISJOINT_BIT` but cannot actually bind planes separately, or whose copy path reads from the wrong allocation, will fail only the `_disjoint` leaves.
- Disjoint and non-disjoint allocations exercise different memory binding paths in the driver, so a disjoint-only failure isolates the cause to per-plane binding or per-plane format support.

### Transfer queue and `minImageTransferGranularity`

A dedicated transfer queue family exposes only `VK_QUEUE_TRANSFER_BIT` (no graphics or compute). Its `VkQueueFamilyProperties::minImageTransferGranularity` defines the alignment that copy region offsets and extents must respect: `(offset, extent)` must be multiples of the granularity. The test queries the transfer queue family at [`testCopies`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L487-L494) and aligns every generated copy region to the granularity in [`genCopies`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L262-L269).

Why it matters here:

- The test uploads source and destination image data on the universal queue, then performs the copies on the transfer queue, then downloads the destination. This exercises queue-family ownership transfer of the image (the universal queue writes, the transfer queue reads and writes, then the transfer queue is read back).
- A driver that mishandles transfer-queue granularity validation, or whose transfer queue produces different bytes than the universal queue would, will fail this test even when universal-queue copy tests pass.

### LSB don't-care tolerance for 10-bit and 12-bit planes

`R10X6_UNORM_PACK16` stores 10 meaningful bits in a 16-bit container; `R12X4_UNORM_PACK16` stores 12 meaningful bits in a 16-bit container. When a multiplane image with such plane-compatible formats is copied between plane layouts that reinterpret the container differently (e.g., 3-plane to 2-plane), the lower 6 bits (for 10-bit) or 4 bits (for 12-bit) of each even byte are implementation-defined. The test masks those bits during comparison via [`areLsb6BitsDontCare`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L724) and [`areLsb4BitsDontCare`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L725), defined in [`vktYCbCrUtil.cpp#L1023-L1049`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1023-L1049) and [`vktYCbCrUtil.cpp#L1051-L1077`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1051-L1077).

Why it matters here:

- The comparison mask is `0xFF` (every bit must match) except on even bytes of 10-bit/12-bit format pairs, where the mask is `0xC0` (top 2 bits must match) or `0xF0` (top 4 bits must match) respectively.
- A driver that does not reproduce the canonical high bits, or that writes nonzero low bits where the reference expects zero, will fail. A driver that writes random low bits that happen to fall outside the mask will still pass.

## One Concrete Example

Take `dEQP-VK.api.copy_and_blit.multiplanar_xfer.g8_b8_r8_3plane_420_unorm.g8_b8_r8_3plane_420_unorm.optimal_disjoint_buffer_optimal_disjoint` as a concrete case. Reconstructed from the registration loop in [`createCopyMultiplaneImageTransferQueueTests`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769-L867):

```text
Source image:       VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM, 64x64, OPTIMAL tiling, DISJOINT (3 separate allocations)
Destination image:  VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM, 64x64, OPTIMAL tiling, DISJOINT (3 separate allocations)
Path:               image -> buffer -> image (intermediateBuffer = true)
Transfer queue:     dedicated transfer queue family, minImageTransferGranularity aligned
Copy regions:       10 random regions, each picking one of (Y->Y, Cb->Cb, Cr->Cr) plane pairs
Tolerance:          0xFF mask (8-bit format, no LSB don't-care)
```

The host seeds an RNG with the source/destination format and tiling, generates 10 random copy regions per the transfer queue's granularity, fills the source and destination `MultiPlaneImageData` with random bytes (avoiding NaN patterns), creates the disjoint images, allocates and binds per-plane memory, and uploads both images via the universal queue. For each of the 10 copies, the test allocates an intermediate buffer of `64 * 64 * 1` bytes (the Y plane size), records `vkCmdCopyImageToBuffer` src→buffer, a `VkBufferMemoryBarrier` with `TRANSFER_WRITE`→`TRANSFER_READ`, and `vkCmdCopyBufferToImage` buffer→dst. A `VkImageMemoryBarrier` on the destination (layout stays `TRANSFER_DST_OPTIMAL`) separates consecutive copies. The command buffer is submitted on the transfer queue. After completion, the destination is downloaded and compared byte-by-byte against a host reference computed by memcpying each source plane region into the corresponding destination plane region.

## End-to-End Test Flow

```text
[host] checkSupport: transfer queue family exists, image dims within maxImageDimension2D,
                   format supports TRANSFER_SRC or TRANSFER_DST, DISJOINT supported when needed,
                   plane-compatible formats supported when disjoint
[host] query transfer queue family's minImageTransferGranularity
[host] seed RNG (6792903u, src config, dst config); generate 10 random VkImageCopy regions
       aligned to granularity; each region picks a (srcPlane, dstPlane) pair from compatible pairs
[host] fill src and dst MultiPlaneImageData with random bytes (NaN-avoiding for float-looking planes)
[host] create src VkImage (TRANSFER_SRC|TRANSFER_DST usage, OPTIMAL tiling, optional DISJOINT)
[host] create dst VkImage (same usage, OPTIMAL tiling, optional DISJOINT)
[host] allocate and bind image memory (per-plane when disjoint; otherwise single allocation)
[host] uploadImage src and dst via universal queue, leaving both in TRANSFER_*_OPTIMAL layout
[host] begin transfer-queue command buffer
[host] for each of 10 copy regions:
       [host] allocate intermediate buffer of plane extent * block byte size (always allocated)
       [host] if intermediateBuffer:
              [cmd]  vkCmdCopyImageToBuffer(src -> buffer, srcSubresource, srcOffset, extent)
              [cmd]  VkBufferMemoryBarrier(TRANSFER_WRITE -> TRANSFER_READ) on buffer
              [cmd]  vkCmdCopyBufferToImage(buffer -> dst, dstSubresource, dstOffset, extent)
       [host] else:
              [cmd]  vkCmdCopyImage(src -> dst, single region)
       [cmd]  VkImageMemoryBarrier on dst (TRANSFER_WRITE -> TRANSFER_READ|WRITE, layout unchanged)
[host] end command buffer; submit on dedicated transfer queue; wait
[host] downloadImage dst via transfer queue
[host] compute reference: for each region, memcpy src plane bytes into dst plane at computed offset
[host] byte-by-byte compare result vs reference, with mask 0xFF (or 0xC0 / 0xF0 on even bytes
       for 10-bit / 12-bit format pairs); stop after 30 errors
[host] report pass / fail("Failed, found N incorrect bytes")
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- No GLSL, SPIR-V, HLSL, or Amber artifacts. All work is recorded through `vkCmdCopyImage`, `vkCmdCopyImageToBuffer`, and `vkCmdCopyBufferToImage`.
- The randomized copy region matrix is generated per test case by `genCopies`, seeded deterministically from the source/destination `ImageConfig` so failures are reproducible.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source `VkImage` | Yes | Yes (universal queue uploads, transfer queue reads) | Read by `vkCmdCopyImage` or `vkCmdCopyImageToBuffer` | No | Holds source plane bytes; disjoint means 2 or 3 separate allocations |
| Destination `VkImage` | Yes | Yes (universal queue uploads, transfer queue writes and reads back) | Written by `vkCmdCopyImage` or `vkCmdCopyBufferToImage` | Yes, via `downloadImage` | Receives copied plane bytes; compared against host reference |
| Intermediate `VkBuffer` (one per copy region) | Yes, when `intermediateBuffer=true` | Yes | Written by `vkCmdCopyImageToBuffer`, read by `vkCmdCopyBufferToImage` | No | Bridges image-to-image copies when the test exercises the buffer path; sized to source plane extent * block bytes |
| Host-side `MultiPlaneImageData` for source | Yes | No | No | Yes, as reference input | Filled with random bytes; feeds both `uploadImage` and the reference computation |
| Host-side `MultiPlaneImageData` for destination initial state | Yes | No | No | No | Filled with random bytes and uploaded; the reference computation starts from this so untouched bytes are expected to match |
| Host-side `MultiPlaneImageData` for result | Yes | No | No | Yes, as comparison input | Receives downloaded destination bytes |
| Host-side `MultiPlaneImageData` for reference | Yes, derived from dst initial state | No | No | Yes, as comparison oracle | Built by memcpying each copy region's source plane bytes into the destination plane |
| Transfer-queue command buffer | Yes | Yes | No | No | Records all copy commands and pipeline barriers |

## What Is Checked

- Byte-by-byte comparison of destination plane bytes against a host-computed reference, with optional LSB masking:
  - mask `0xFF` for 8-bit and 16-bit format pairs (every bit must match);
  - mask `0xC0` on even bytes for 10-bit (`R10X6*`) format pairs (top 2 bits must match);
  - mask `0xF0` on even bytes for 12-bit (`R12X4*`) format pairs (top 4 bits must match).
- The reference is computed by memcpying each `VkImageCopy` region's source plane bytes into the destination plane at the corresponding block-aligned offset. Bytes outside any copy region are expected to match the destination's initial random fill.
- The check is per test case leaf. Each leaf produces one pass/fail verdict.
- Up to 30 byte mismatches are logged before the comparison stops; the failure message reports either the exact count or `30+` if exceeded.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group (test case leaf clustering)
>
> **Candidate values:** `direct_copy` (`optimal_optimal`, `optimal_optimal_disjoint`, `optimal_disjoint_optimal`, `optimal_disjoint_optimal_disjoint`), `indirect_buffer_copy` (`optimal_buffer_optimal`, `optimal_buffer_optimal_disjoint`, `optimal_disjoint_buffer_optimal`, `optimal_disjoint_buffer_optimal_disjoint`)

A secondary axis cuts across both groups:

> **Secondary axis:** disjoint flag combination
>
> **Candidate values:** neither disjoint, source only, destination only, both disjoint

A third axis (source format bit depth) is relevant only to the LSB tolerance application:

> **Tertiary axis:** source/destination format bit depth
>
> **Candidate values:** 8-bit (`g8_*`), 10-bit (`g10x6_*`, LSB6 don't-care), 12-bit (`g12x4_*`, LSB4 don't-care), 16-bit (`g16_*`)

## What Failure Means

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
| All leaves (regardless of group or format) | Transfer-queue-specific: `minImageTransferGranularity` alignment, queue-family ownership transfer between universal upload and transfer copy, or transfer-queue submission synchronization. |

### Cause Analysis

Detailed `### Cause Analysis` is written fresh during the final Level-3 rewrite. The brief only names the causes above so the mapping can be carried directly into the final page.

## Important Variations and Special Cases

- **Linear tiling is skipped by design.** The registration loop iterates over `optimal` and `linear` tilings but `continue`s when either src or dst is linear ([`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838-L839`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838-L839)). Multiplane linear images are rarely supported, so the test never exercises them.
- **`createFlags` vector is defined but unused.** A vector of `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, `CUBE_COMPATIBLE_BIT`, `ALIAS_BIT`, `2D_ARRAY_COMPATIBLE_BIT`, `EXTENDED_USAGE_BIT`, and `SAMPLE_LOCATIONS_COMPATIBLE_DEPTH_BIT_EXT` is declared at [`line 797`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L797) but never iterated. Only `VK_IMAGE_CREATE_DISJOINT_BIT` (when disjoint) is actually applied. The declared flags appear to be inherited boilerplate from sibling copy test files.
- **Intermediate buffer is always allocated.** Even when `intermediateBuffer=false`, a `VkBuffer` is allocated per copy region ([`line 580`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L580)). Only the recorded commands differ; the buffer is unused on the direct path.
- **`getBlockByteSize` fatal-exits on multiplane formats.** [`getBlockByteSize`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375-L434) returns `DE_FATAL` for the multiplane formats listed in the switch, because it is only meaningful for the plane-compatible single-plane formats. The intermediate buffer path computes buffer size from the plane-compatible format, never the multiplane format itself.
- **`areLsb6BitsDontCare` / `areLsb4BitsDontCare` are symmetric.** Either source or destination being a 10-bit (`R10X6*`) or 12-bit (`R12X4*`) plane-compatible format triggers the mask; both do not need to be. This means cross-bit-depth copies between 8-bit and 10-bit formats are also masked, but such pairs are not generated because `isCompatible` only matches within the same bit width.
- **Source format 444 is missing for 16-bit.** The 19-format list includes `g16_b16_r16_3plane_444_unorm` is absent; only 420 and 422 are present for 16-bit. This is consistent with the Vulkan core spec, which does not define `VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM`.
- **Image size is fixed at 64×64 for all YCbCr formats.** Non-YCbCr formats would use 23×17, but every format in the `multiplaneFormats` array is YCbCr, so the size is always 64×64.
- **Copy compatibility is per-plane, not per-format.** `isCopyCompatible` returns true if any plane pair between source and destination is `isCompatible`. This means 3-plane → 2-plane copies are generated when at least one plane pair matches (typically Y→Y).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `ImageConfig` / `TestConfig` structs | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L39-L67`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L39-L67) | Carry source/destination format, tiling, disjoint flag, size, and the `intermediateBuffer` switch. |
| `checkFormatSupport` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L69-L140`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L69-L140) | Validates format support, transfer features, and per-plane disjoint support. |
| `checkSupport` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L142-L157`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L142-L157) | Validates transfer queue family existence and image dimension limits. |
| `isCompatible` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L159-L209`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L159-L209) | Per-plane copy compatibility by texel block size class (8/16/24/32/48/64/96/128/192/256-bit). |
| `genCopies` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221-L295`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221-L295) | Generates 10 random plane-pair copy regions aligned to transfer queue granularity. |
| `getBlockByteSize` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375-L434`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375-L434) | Returns byte size for plane-compatible formats; fatal-exits on multiplane formats. |
| `isCopyCompatible` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436-L483`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436-L483) | Format-pair filter used by the registration loop. |
| `testCopies` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485-L765`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485-L765) | Test body: creates images, allocates memory, uploads, records copies, submits on transfer queue, downloads, compares. |
| Reference computation | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L672-L755`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L672-L755) | Host-side reference memcpy and byte-by-byte comparison with LSB masking. |
| `createCopyMultiplaneImageTransferQueueTests` | [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769-L867`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769-L867) | Registration loop: 19 source formats × compatible destinations × 8 leaves per pair. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L283`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283) | Adds `multiplanar_xfer` directly under `copy_and_blit`. |
| LSB tolerance helpers | [`vktYCbCrUtil.cpp#L1023-L1077`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1023-L1077) | `areLsb6BitsDontCare` and `areLsb4BitsDontCare` define which format pairs trigger LSB masking. |
| `MultiPlaneImageData` and upload/download helpers | [`vktYCbCrUtil.hpp#L58-L191`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.hpp#L58-L191) | Planar host-side data structure and the upload/download/fill helpers used by the test. |

## Questions / Risk Points for User Audit

- Is the behavioral-group framing (direct copy vs indirect buffer copy) the right primary axis, or should the 8 leaves be enumerated individually? The grouping reflects the two genuinely different code paths recorded into the command buffer; the disjoint flags vary memory binding but not the recorded commands.
- Is the LSB tolerance description accurate? The mask is applied only to even bytes (`!(byteNdx & 0x01)`) of 10-bit and 12-bit format pairs, which corresponds to the high byte of the 16-bit container. This matches the source at [`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L736-L739`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L736-L739).
- Is the queue-family ownership transfer description correct? The source is uploaded and the destination is initialized on the universal queue, then both are read/written on the transfer queue, and the destination is read back on the transfer queue. The test uses `VK_SHARING_MODE_EXCLUSIVE` and `VK_QUEUE_FAMILY_IGNORED` for the buffer memory barrier, but does not record an explicit image ownership-transfer barrier between universal upload and transfer copy. This may rely on `submitCommandsAndWait` providing an implicit barrier, or on the implementation handling the transition. Source-level investigation may be needed to confirm whether the test intends to exercise explicit ownership transfer.
- Are the unused `createFlags` correctly characterized as boilerplate? They are declared but never iterated in the registration loop, which only applies `VK_IMAGE_CREATE_DISJOINT_BIT` conditionally.
- Should the page document that `getTransferQueueFamilyIndex() == -1` causes a `NotSupportedError` skip rather than a failure? This affects how the test reports on devices without a dedicated transfer queue.

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge section into a brief unordered list of necessary prerequisites: multiplane YCbCr image formats, chroma subsampling and plane extents, disjoint allocation, transfer queue and `minImageTransferGranularity`, LSB don't-care tolerance. Move detailed application into the appropriate later sections (Behavior Parameters, Runtime Execution).
- Preserve the concrete example only as a brief mention in `## Behavior Parameters` or `## Runtime Execution and Result Checking`; the brief's full example is teaching scaffolding.
- Carry the `### Failure Cause Mapping` table directly into the final page's `## Failure Meaning` → `### Failure Cause Mapping`. Write `### Cause Analysis` fresh during the rewrite, expanding each cause with `**Possible failure symptoms:**` and `**Possible implementation causes:**` paragraphs grounded in Vulkan spec semantics and source inspection.
- Carry the `## Behavior Parameter Identification` conclusion (behavioral group as primary axis; disjoint flags and format bit depth as secondary axes) into `## Behavior Parameters` with `### <group name>` subsections for each behavioral group, plus a short paragraph covering the secondary axes.
- Move the Source Mapping table into `## Source Reference Appendix` with minimal edits.
- Resolve the queue-family ownership transfer question by inspecting `submitCommandsAndWaitWithSync` if needed; otherwise state in `### Cause Analysis` that source-level investigation is needed for the queue-ownership-transfer claim.
- The Vulkan spec chapters at `external/vulkan-docs/src/chapters/` are not present in this repository; the brief's Background Knowledge and Failure Cause Mapping are grounded in source inspection and Vulkan spec semantics from the source file itself.
