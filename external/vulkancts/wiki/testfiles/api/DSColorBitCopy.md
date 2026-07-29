## Overview

**Core question:** Does `vkCmdCopyImage` preserve depth/stencil aspect data bit-for-bit when copying between depth/stencil images and color images of matching bit-size, as enabled by `VK_KHR_maintenance8`?

- This page covers the `api.ds_color_copy` test family, implemented entirely in [vktApiDSColorBitCopyTests.cpp](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1).
- The factory function `createDSColorBitCopyTests` is registered directly under the `api` test category from [vktApiTests.cpp#L109](../../../modules/vulkan/api/vktApiTests.cpp#L109), not via the `copy_and_blit` dispatcher.
- The registered group name in source is `ds_color_copy` ([vktApiDSColorBitCopyTests.cpp#L877](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L877)). The factory function name (`createDSColorBitCopyTests`) and the source filename (`vktApiDSColorBitCopyTests.cpp`) use the `DSColorBitCopy` form, but the registered identifier in mustpass is `ds_color_copy`.
- Core test idea: each test case uploads a pseudorandom source buffer to a source image, performs `vkCmdCopyImage` to a destination image of the paired format, reads the destination back, and verifies bit-exact equality per pixel.
- 1320 test case leaves are generated in mustpass under `dEQP-VK.api.ds_color_copy.*`.

## Background Knowledge

- `VK_KHR_maintenance8` extends `vkCmdCopyImage` to permit depth/stencil images as source or destination when paired with a color image whose element bit-size matches the selected aspect. Without this extension, such copies are not legal.
- Aspect-masked image copy: `vkCmdCopyImage` selects an aspect of a depth/stencil image via the `aspectMask` of the `VkImageSubresourceLayers` in the `VkImageCopy` region. The test uses `VK_IMAGE_ASPECT_DEPTH_BIT` or `VK_IMAGE_ASPECT_STENCIL_BIT` on the depth/stencil side and `VK_IMAGE_ASPECT_COLOR_BIT` on the color side.
- Bit-exact comparison: validation compares raw bytes between source and destination pixels without tolerance. For 24-bit depth formats stored in 32-bit words, only the low 24 bits are compared using `kDepth24Mask` (`0xFFFFFF`); the upper 8 bits of the destination word are ignored.
- Signed/float reinterpretation: paired color formats such as `R8_SNORM`, `R16_SNORM`, and `R16_SFLOAT` can hold bit patterns that the depth/stencil aspect does not natively represent. The test deliberately generates source values in the signed or float range to verify that the bit pattern is preserved across the copy regardless of how either format would interpret it.

## Registration Hierarchy

```text
api.ds_color_copy
└── d16_unorm_r16_sfloat_depth_level0_to_level0
```

The group `ds_color_copy` is created at [vktApiDSColorBitCopyTests.cpp#L877](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L877) and added directly under `api` from [vktApiTests.cpp#L109](../../../modules/vulkan/api/vktApiTests.cpp#L109). The 1320 generated test case leaves are added directly under `ds_color_copy` with no intermediate nodes; representative leaves appear in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format bit-count group | 32-bit depth, 24-bit depth, 16-bit depth, 8-bit stencil | Pairs depth/stencil formats with color formats of matching bit-size; controls comparison width and whether `unrestricted` applies | [getFormatGroups()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L67-L114) |
| Aspect | `VK_IMAGE_ASPECT_DEPTH_BIT`, `VK_IMAGE_ASPECT_STENCIL_BIT` | Selects which aspect of a depth/stencil image is the source or destination of the copy | [FormatGroup::aspect](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L57) |
| Direction | ds-to-color, color-to-ds | Each format pair is exercised in both directions | [vktApiDSColorBitCopyTests.cpp#L883](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L883) |
| Source mip level | 0, 3 | Base level or level 3; scales the source image extent | [TestParams::srcMipLevel](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L277) |
| Destination mip level | 0, 3 | Base level or level 3; scales the destination image extent | [TestParams::dstMipLevel](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L278) |
| Attachment usage | false, true | Adds `DEPTH_STENCIL_ATTACHMENT_BIT` or `COLOR_ATTACHMENT_BIT` to the image usage flags; skipped when either mip level is non-zero | [getImageUsage()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L327-L337) |
| Queue type | UNIVERSAL, COMPUTE_ONLY, TRANSFER_ONLY | Selects the queue family that performs the copy; non-universal variants are skipped on Vulkan SC | [QueueType](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L267-L272) |
| Unrestricted depth | false (all bit-counts), true (32-bit only) | When true, uses depth values up to `10.0f` instead of `1.0f`, requiring `VK_EXT_depth_range_unrestricted` | [getRandomDepth32()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L121-L129) |

Test case leaf names follow the pattern `<src_format>_<dst_format>_<aspect>_level<srcMip>_to_level<dstMip>[_unrestricted][_att_usage][_cq|_tq]`, constructed at [vktApiDSColorBitCopyTests.cpp#L939-L944](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L939-L944). For example, `d32_sfloat_s8_uint_r32_sfloat_depth_level0_to_level0_unrestricted_att_usage_tq`.

## Behavior Parameters

The primary behavioral axis is the format bit-count group. It determines which depth/stencil formats are paired with which color formats, the comparison width, and whether the `unrestricted` parameter applies. Each group is a distinct bit-preservation contract.

### 32-bit depth: D32_SFLOAT and D32_SFLOAT_S8_UINT depth aspect against R32 color formats

Pairs `VK_FORMAT_D32_SFLOAT` and `VK_FORMAT_D32_SFLOAT_S8_UINT` (depth aspect) with `VK_FORMAT_R32_SFLOAT`, `VK_FORMAT_R32_SINT`, and `VK_FORMAT_R32_UINT`. Source depth values are pseudorandom floats in `[0.125, 1.0]` for restricted cases or `[0.125, 10.0]` for unrestricted cases; roughly 1 in 16 values is forced to `0.0f`. The 32-bit word is compared verbatim as an integer, so the test verifies that the float bit pattern survives a round trip through any of the R32 color formats in either direction. This is the only group that emits `unrestricted` variants, and those cases require `VK_EXT_depth_range_unrestricted`.

### 24-bit depth: X8_D24_UNORM_PACK32 and D24_UNORM_S8_UINT depth aspect against R32 color formats

Pairs `VK_FORMAT_X8_D24_UNORM_PACK32` and `VK_FORMAT_D24_UNORM_S8_UINT` (depth aspect) with the same three R32 color formats. Source values are random 32-bit words masked to the low 24 bits via `kDepth24Mask` (`0xFFFFFF`). Comparison masks both sides to the same 24 bits, so the test verifies that the low 24 bits are preserved; the upper 8 bits of the destination word are allowed to differ.

### 16-bit depth: D16_UNORM and D16_UNORM_S8_UINT depth aspect against R16 color formats

Pairs `VK_FORMAT_D16_UNORM` and `VK_FORMAT_D16_UNORM_S8_UINT` (depth aspect) with `VK_FORMAT_R16_SFLOAT`, `VK_FORMAT_R16_UNORM`, `VK_FORMAT_R16_SNORM`, `VK_FORMAT_R16_UINT`, and `VK_FORMAT_R16_SINT`. Source values are 16-bit words chosen per color-format pair: floating-point values for `R16_SFLOAT` partners, signed values in `[-32767, 32767]` for `R16_SNORM` partners, and unsigned 16-bit values otherwise. The 16-bit word is compared verbatim, which exposes any signed or float reinterpretation by the implementation.

### 8-bit stencil: S8_UINT and combined formats' stencil aspect against R8 color formats

Pairs `VK_FORMAT_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D16_UNORM_S8_UINT` (stencil aspect) with `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R8_UNORM`, and `VK_FORMAT_R8_SNORM`. Source values are 8-bit bytes: signed values in `[-127, 127]` (reinterpreted as raw bytes) when paired with `R8_SNORM`, otherwise raw unsigned bytes. The 8-bit value is compared verbatim.

## Shader Analysis

No shader is involved. This test family exercises fixed-function `vkCmdCopyImage` behavior and host-side validation only.

## Runtime Execution and Result Checking

Each test case runs the same host-orchestrated round trip:

- Host generates a pseudorandom source buffer of 16x16 pixels using [getRandomSrcValues()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L214-L265), seeded from a deterministic combination of `srcFormat`, `dstFormat`, `aspect`, and mip levels ([seed construction](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L894-L898)).
- Host creates a 2D source image with `srcMipLevels = srcMipLevel + 1` and a destination image with `dstMipLevels = dstMipLevel + 1`. The base extent is 16x16; image level-0 extents are computed by left-shifting the base extent by the selected mip level, so the selected mip level has the base extent ([vktApiDSColorBitCopyTests.cpp#L607-L612](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L607-L612)).
- Host selects the queue family and queue via [getQueueFamilyIndex()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L572-L586) and [getQueue()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L588-L602).
- Transfer-queue workaround: when the source is a depth/stencil image and the queue type is `TRANSFER_ONLY`, host uploads the source buffer to a staging image using the universal queue, then transfers ownership of the staging image to the transfer queue and copies from the staging image to the source image inside the transfer queue. This avoids `VUID-vkCmdCopyBufferToImage-commandBuffer-07739`, which forbids `vkCmdCopyBufferToImage` with depth/stencil images on transfer queues ([vktApiDSColorBitCopyTests.cpp#L718-L774](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L718-L774)).
- The chosen queue records a command buffer that lays out the source image as `TRANSFER_DST_OPTIMAL` and copies the buffer (or staging image) into it; transitions both images for the image-to-image copy; calls `vkCmdCopyImage` with a single `VkImageCopy` region covering the 16x16 base extent; transitions the destination image to `TRANSFER_SRC_OPTIMAL`; copies the destination image back to a host-visible destination buffer; and emits a memory barrier making the destination buffer host-readable ([vktApiDSColorBitCopyTests.cpp#L752-L821](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L752-L821)).
- Host submits, waits, and invalidates the destination buffer allocation.
- Host scans every `(x, y)` of the 16x16 base extent and builds a [PixelValue](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L507-L551) for both source and destination pointers, then compares them. The 24-bit depth case masks both sides to `0xFFFFFF` before comparison; the other bit-counts compare the raw integer of the matching width.
- The case passes when every pixel compares equal. Each mismatch logs `Unexpected value at (x, y): expected 0x... but found 0x...`; after scanning all pixels, the case returns `fail` if any mismatch was found.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| 32-bit depth | Bit-pattern corruption during D32 to R32 copy, or unrestricted depth values clamped by the implementation |
| 24-bit depth | Low-24-bit data corruption, or upper 8 bits of the destination word leaking into the lower 24 bits |
| 16-bit depth | 16-bit value corruption, or format-specific signed/float reinterpretation not preserved |
| 8-bit stencil | Stencil byte corruption, or signed reinterpretation for `R8_SNORM` not preserved |

All four groups share a common cause: queue-family-specific copy feature mis-handling, because each group is exercised on universal, compute-only, and transfer-only queues.

### Cause Analysis

#### Bit-pattern corruption during D32 to R32 copy

**Possible failure symptoms:** Any `(x, y)` of the 16x16 base extent reports `expected 0x... but found 0x...` for a 32-bit pixel. The mismatch can be sporadic across the image or systematic across every pixel.

**Possible implementation causes:** The implementation may reinterpret a `D32_SFLOAT` value through format conversion instead of treating it as a raw 32-bit word during `vkCmdCopyImage`. Vulkan's copy rules require bit-exact preservation when the source and destination have matching element bit-size, so any conversion is a driver bug. For `unrestricted` variants, an implementation that clamps the source depth value to `[0.0, 1.0]` before copying would also fail. Source-level investigation of the driver's `vkCmdCopyImage` path is needed to confirm whether clamping or format reinterpretation is occurring.

#### Low-24-bit data corruption

**Possible failure symptoms:** A 24-bit depth pixel mismatch where the destination upper 8 bits appear in the lower 24 bits, or the lower 24 bits do not match the source after `kDepth24Mask` is applied.

**Possible implementation causes:** The implementation may treat `X8_D24_UNORM_PACK32` as a normalized depth value and re-quantize it during the copy, or store the 24-bit value with the high 8 bits populated by undefined data instead of preserving the source word's high byte. Vulkan requires bit-exact preservation for matching bit-size copies, so any re-quantization is a bug. Source-level investigation of the driver's 24-bit depth copy path is needed.

#### 16-bit value corruption

**Possible failure symptoms:** A 16-bit pixel mismatch in any of the R16-paired variants. The signed and float variants would fail specifically when the test generated source values outside the unsigned range.

**Possible implementation causes:** The implementation may convert `R16_SNORM` or `R16_SFLOAT` values to a normalized range or floating-point representation instead of treating them as raw 16-bit words. For `R16_SNORM` partners, source values are explicitly generated in `[-32767, 32767]` to detect such conversion; if the implementation clamps or reinterprets signed values, those cases fail. Source-level investigation of the driver's 16-bit copy path is needed.

#### Stencil byte corruption

**Possible failure symptoms:** An 8-bit pixel mismatch in any of the R8-paired variants. The `R8_SNORM` partner fails specifically when the test generated source bytes outside `[0, 127]`.

**Possible implementation causes:** The implementation may treat stencil values as unsigned integers and clamp signed reinterpretations, or may apply a format-specific conversion. Vulkan requires bit-exact preservation, so any conversion is a bug. Source-level investigation of the driver's stencil copy path is needed.

#### Queue-family-specific copy feature mis-handling

**Possible failure symptoms:** The same format pair passes on the universal queue but fails (or skips via `NotSupportedError`) on the compute-only or transfer-only queue variants, which carry the `_cq` or `_tq` suffix.

**Possible implementation causes:** The implementation may not expose or honor `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR`, `VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR`, `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_TRANSFER_QUEUE_BIT_KHR`, or `VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_TRANSFER_QUEUE_BIT_KHR` correctly, or may perform the copy on the wrong queue without proper ownership transfer. The transfer-queue staging path is the only host-side workaround present in the test; if the destination image is corrupted after that path, the issue is in the implementation's queue-family handling of `vkCmdCopyImage` and the staging image ownership transfer.

## Case Pruning

### Requirement-based pruning

- All cases require the `VK_KHR_maintenance8` device functionality ([checkSupport()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L501)). Cases skip via `NotSupportedError` if the extension is missing.
- Cases with `unrestricted=true` require `VK_EXT_depth_range_unrestricted` ([vktApiDSColorBitCopyTests.cpp#L503-L504](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L503-L504)). Only 32-bit depth cases use `unrestricted=true`.
- Compute-only and transfer-only queue cases require `VK_KHR_maintenance10` and `VK_KHR_format_feature_flags2` on non-Vulkan SC, and the source or destination format must report the matching `*_COPY_ON_*_QUEUE_BIT_KHR` feature flag ([vktApiDSColorBitCopyTests.cpp#L381-L499](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L381-L499)).
- Each format must support the requested mip level via `VkImageFormatProperties::maxMipLevels` ([isFormatSupported()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L339-L360)).
- On Vulkan SC, compute-only and transfer-only queue types are skipped due to VUs `*-10217` and `*-10218` ([vktApiDSColorBitCopyTests.cpp#L903-L907](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L903-L907)).

### Design-based pruning

- Attachment-usage variants (the `_att_usage` suffix) are generated only when both `srcMipLevel` and `dstMipLevel` are `0`. The `attUsage=true` case is skipped via `continue` for any non-zero mip combination ([vktApiDSColorBitCopyTests.cpp#L888-L889](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L888-L889)).
- The `unrestricted=true` value is generated only for 32-bit depth bit-count pairs; all other bit-counts use `unrestricted=false` exclusively ([vktApiDSColorBitCopyTests.cpp#L915-L923](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L915-L923)).
- The transfer-queue staging workaround is applied only when the source is depth/stencil and the queue is `TRANSFER_ONLY`; it is not used when the source is a color format or the queue is universal or compute.

## Key Takeaways

- `api.ds_color_copy` is a single test family with no intermediate nodes and 1320 generated test case leaves, registered directly under the `api` test category and not under `copy_and_blit`. The factory name (`createDSColorBitCopyTests`) and source filename (`vktApiDSColorBitCopyTests.cpp`) differ from the registered group name (`ds_color_copy`); readers tracing code by filename must use the registered name in mustpass as the source of truth.
- The test exercises one core property: bit-exact preservation of depth/stencil aspect data when round-tripped through a color format of matching bit-size via `vkCmdCopyImage`, as enabled by `VK_KHR_maintenance8`.
- The format bit-count group is the primary behavioral axis. The 32-bit group is the only one with `unrestricted` variants; the 24-bit group masks both sides to `0xFFFFFF` before comparison; the 16-bit and 8-bit groups use format-pair-specific source value generation to detect signed or float reinterpretation by the implementation.
- Validation is host-side bit-exact comparison; no shader runs. A single pixel mismatch fails the case.
- The transfer-queue plus depth/stencil source combination requires a staging image uploaded on the universal queue and ownership-transferred to the transfer queue, because `vkCmdCopyBufferToImage` cannot be used with depth/stencil images on a transfer queue (`VUID-vkCmdCopyBufferToImage-commandBuffer-07739`).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDSColorBitCopyTests()` | [vktApiDSColorBitCopyTests.cpp#L875-L952](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L875-L952) | Test family registration and leaf generation loop |
| Parent registration | [vktApiTests.cpp#L109](../../../modules/vulkan/api/vktApiTests.cpp#L109) | Where `createDSColorBitCopyTests` is added to `apiTests` |
| `getFormatGroups()` | [vktApiDSColorBitCopyTests.cpp#L67-L114](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L67-L114) | Defines the four format bit-count groups |
| `TestParams` | [vktApiDSColorBitCopyTests.cpp#L274-L283](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L274-L283) | Per-case parameter struct |
| `DSColorCopyCase::checkSupport()` | [vktApiDSColorBitCopyTests.cpp#L362-L505](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L362-L505) | Feature, queue, and mip-level support checks |
| `DSColorCopyInstance::iterate()` | [vktApiDSColorBitCopyTests.cpp#L604-L869](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L604-L869) | Runtime execution and bit-exact comparison |
| `PixelValue` | [vktApiDSColorBitCopyTests.cpp#L507-L551](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L507-L551) | Per-pixel value loader and comparator |
| `getImageUsage()` | [vktApiDSColorBitCopyTests.cpp#L327-L337](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L327-L337) | Image usage flag construction including attachment variants |
| `isFormatSupported()` | [vktApiDSColorBitCopyTests.cpp#L339-L360](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L339-L360) | Per-format image format properties check |
| Transfer-queue staging workaround | [vktApiDSColorBitCopyTests.cpp#L718-L774](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L718-L774) | Staging image upload and ownership transfer to transfer queue |
| Header | [vktApiDSColorBitCopyTests.hpp](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.hpp#L1) | Public factory declaration |
