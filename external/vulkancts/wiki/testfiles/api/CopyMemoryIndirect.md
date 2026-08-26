## Overview

**Core question:** does the implementation correctly execute indirect memory-to-memory and memory-to-image copies whose parameters come from device memory, and advertise the required destination-format support?

This page covers the indirect-copy implementations in [`vktApiCopyMemoryIndirectTests.cpp`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp). They are registered both as the standalone `api.copy_and_blit.copy_memory_indirect` family and as the `memory_to_image_indirect*` families below the `core` and `dedicated_allocation` copy dispatchers. The source is non-VulkanSC only; `#ifndef CTS_USES_VULKANSC` guards the entire file.

The source implements four behavior areas:

- buffer-to-buffer indirect copy through `vkCmdCopyMemoryIndirectKHR`, with copy size, copy count, stride, and queue family as the varied parameters (`size_4`, `size_12`, `size_full`);
- buffer-to-image indirect copy through `vkCmdCopyMemoryToImageIndirectKHR`, with image dimensionality, format, region layout, mip and array shape, allocation strategy, and queue family varied by the `memory_to_image_indirect*` families;
- mandatory format feature compliance, querying `VkFormatProperties3` for every format mandated by `VK_KHR_copy_memory_indirect` (`mandatory_formats`);
- use-after-copy verification with indirect copy commands, delegated to [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp) (`use_after_copy`).

## Background Knowledge

- `VK_KHR_copy_memory_indirect` exposes two indirect copy commands: `vkCmdCopyMemoryIndirectKHR` (buffer-to-buffer) and `vkCmdCopyMemoryToImageIndirectKHR` (buffer-to-image). Their copy parameters come from device memory, not the command call site: the host writes `VkCopyMemoryIndirectCommandKHR` or `VkCopyMemoryToImageIndirectCommandKHR` records into a device-visible buffer, and the device reads them through a `VkStridedDeviceAddressRangeKHR` address range. This page tests both commands.
- The extension advertises two feature bits: `indirectMemoryCopy` gates `vkCmdCopyMemoryIndirectKHR`, and `indirectMemoryToImageCopy` gates `vkCmdCopyMemoryToImageIndirectKHR`. Queue-family support is queried through `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues`, which is the authoritative source for which queue families may receive these commands.
- `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` (requires `VK_KHR_format_feature_flags2`) is the format feature bit that licenses a format as a destination for `vkCmdCopyMemoryToImageIndirectKHR`. The extension spec lists a closed set of mandatory formats that must advertise this bit when the implementation enables the extension.

## Registration Hierarchy

```text
api.copy_and_blit.copy_memory_indirect
├── size_4
├── size_12
├── size_full
├── mandatory_formats
└── use_after_copy

api.copy_and_blit.core
├── memory_to_image_indirect
├── memory_to_image_indirect_transfer_queue
└── memory_to_image_indirect_compute_queue

api.copy_and_blit.dedicated_allocation
├── memory_to_image_indirect
├── memory_to_image_indirect_transfer_queue
└── memory_to_image_indirect_compute_queue
```

`size_4`, `size_12`, and `size_full` each expand to a four-level tree of intermediate nodes ending in test case leaves: `<size>.<offset>.<count>.<stride>.<queue>`, where `<queue>` is `graphics`, `transfer`, or `compute`. `mandatory_formats` has one test case leaf, `memory_to_image`; `use_after_copy` delegates to [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp).

Each `memory_to_image_indirect*` family has the same six direct children: `1d_images`, `1d_additional_formats`, `2d_images`, `2d_mipmap_images`, `2d_additional_formats`, and `3d_images`. The family suffix selects the universal, transfer-only, or compute-only queue; the parent root selects suballocated or dedicated image memory. [`addIndirectCopyTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74-L116) registers these six families, and [`addCopyMemoryToImageTests()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243-L2251) creates their common child structure.

The standalone group is created by [`createCopyMemoryIndirectTests()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253): the `size_*` matrix is added at [lines 2295–2329](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2295-L2329), `mandatory_formats` at [lines 2331–2336](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2331-L2336), and `use_after_copy` via [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Copy size | `size_4` (4 bytes), `size_12` (12 bytes), `size_full` (0, full buffer) | Bytes copied per indirect command. `0` signals a whole-buffer copy. Drives the parent intermediate node. | [L2269](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2269) |
| Copy count | `count_0`, `count_1`, `count_2`, `count_63` | Number of `VkCopyMemoryIndirectCommandKHR` records the device must walk. `count_0` is the no-op boundary. | [L2262](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) |
| Copy offset | `offset_0`, `offset_4` | Byte offset applied to both source and destination addresses. Pruned when `offset >= size`. | [L2276](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2276) |
| Stride | `normal_stride`, `long_stride` | Stride between consecutive indirect commands. `normal_stride` is `sizeof(VkCopyMemoryIndirectCommandKHR)`; `long_stride` is `sizeof(IndirectParams)`, a larger struct carrying dummy parameters. | [L2283](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283) |
| Queue family | `graphics`, `transfer`, `compute` | Queue family that receives `vkCmdCopyMemoryIndirectKHR`. Selected from `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues`. | [L2291](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291) |
| Memory-to-image family | `memory_to_image_indirect`, `memory_to_image_indirect_transfer_queue`, `memory_to_image_indirect_compute_queue` | Selects the universal, transfer-only, or compute-only queue for `vkCmdCopyMemoryToImageIndirectKHR`. | [`addIndirectCopyTests`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74-L116) |
| Image allocation kind | `core` (suballocated), `dedicated_allocation` | Changes how the destination image is backed without changing the six direct child families. | [`addCoreCopiesAndBlittingTests`, `addDedicatedAllocationCopiesAndBlittingTests`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L246) |
| Memory-to-image child | `1d_images`, `1d_additional_formats`, `2d_images`, `2d_mipmap_images`, `2d_additional_formats`, `3d_images` | Selects dimensionality and the image/region/format matrix generated below each family. | [`addCopyMemoryToImageTests`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243-L2251) |

The `mandatory_formats` intermediate node exposes one test case leaf, `memory_to_image`, whose matrix is the closed list of mandatory formats enumerated in [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199).

## Behavior Parameters

The primary behavioral axis is the registered behavior family: indirect buffer copy, indirect memory-to-image copy, mandatory format support, or delegated use-after-copy.

### size_4, size_12, size_full — Buffer-to-buffer indirect copy

These three intermediate nodes share one mechanism: build `VkCopyMemoryIndirectCommandKHR` records in a host-visible indirect buffer, dispatch `vkCmdCopyMemoryIndirectKHR`, then verify the destination bytes match the source. The behavior is the same for each; only the copy size differs. `size_full` uses `copySize = 0`, which the test interprets as "copy the whole buffer minus the offset". The implementation class is [`CopyMemoryIndirectTestInstance`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872); the case class is [`CopyMemoryIndirectTestCase`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2101).

The `long_stride` variant tests the `stride` field of `VkStridedDeviceAddressRangeKHR`: the device must read each `VkCopyMemoryIndirectCommandKHR` from a struct embedded in a larger `IndirectParams` layout, ignoring the trailing dummy fields.

### mandatory_formats — Mandatory format feature compliance

This single test case leaf queries `VkFormatProperties3` (chained through `VkFormatProperties2`) for every format mandated by `VK_KHR_copy_memory_indirect` and verifies that `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` is set in `optimalTilingFeatures`. The check is implemented as a function case in [`MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155). The case logs every non-compliant format before returning a single pass/fail verdict.

### memory_to_image_indirect* — Indirect buffer-to-image copy

These six registered families share `CopyMemoryToImageIndirect`. The host converts each `VkBufferImageCopy` region into a `VkCopyMemoryToImageIndirectCommandKHR`, stores the records with a stride larger than the command structure, and passes their device-address range to `vkCmdCopyMemoryToImageIndirectKHR`. The test then reads the destination image and compares it with a host-generated texture reference. The `core` versus `dedicated_allocation` parent changes image allocation; the family suffix changes queue selection; the six direct children vary image dimensionality, mip/array layout, formats, and region shapes.

### use_after_copy — Use-after-copy verification (delegated)

This intermediate node is registered in this file via [`createUseAfterXferGroup(testCtx, true)`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) but the implementation lives in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). The delegated test verifies that image contents written by indirect copy commands can still be consumed correctly afterward (sampled as a texture or used as a depth/stencil attachment). The detailed behavior, parameters, and failure analysis are documented in [UseAfterCopy.md](UseAfterCopy.md).

## Shader Analysis

No shader runs in the in-file indirect-copy or mandatory-format cases. They use fixed-function copy commands and host-side property or result checks. The delegated `use_after_copy` cases may consume copied image data through sampling or attachment use, but shader behavior is owned by the delegated page rather than the indirect-copy operation itself.

## Runtime Execution and Result Checking

### Buffer-to-buffer indirect copy (`size_*`)

[host] Load sample text from `vulkan/data/copy_memory_indirect/sample_text.txt` and pad to 64-byte alignment ([line 1899](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1899), [line 1903](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1903)).

[host] Allocate `srcBuffer`, `dstBuffer`, and `indirectBuffer`. All three require `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`; `indirectBuffer` also requires `VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT`. Memory must be host-visible and expose a device address ([line 1926 through line 1949](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1926-L1949)).

[host] Resolve device addresses for all three buffers; build `copyCount` `VkCopyMemoryIndirectCommandKHR` records where each `dstAddress = dstBufferAddress + copyOffset + i * copySize` ([line 1965 through line 1971](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1965-L1971)).

[host] Write the command records into `indirectBuffer` with the configured stride. For `long_stride`, the test wraps each command in an `IndirectParams` struct that carries three dummy `uint32_t` fields after the command, exercising the stride handling path ([line 1986 through line 1997](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1986-L1997)).

[host] Clear `dstBuffer` to `0xFF` so that any byte left untouched is distinguishable from copied data ([line 2006](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2006)).

[host] Begin command buffer; build `VkStridedDeviceAddressRangeKHR` over `indirectBuffer` and a `VkCopyMemoryIndirectInfoKHR` with both `srcCopyFlags` and `dstCopyFlags` set to `VK_ADDRESS_COPY_DEVICE_LOCAL_BIT_KHR`; call `vkCmdCopyMemoryIndirectKHR` ([line 2015 through line 2023](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2015-L2023)).

[host] Insert a `VkBufferMemoryBarrier` on `dstBuffer` from `TRANSFER_WRITE` to `TRANSFER_READ`, end the command buffer, and submit with `submitCommandsAndWaitWithTransferSync` ([line 2025 through line 2038](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2025-L2038)).

[host] Invalidate the destination allocation and, for each `copyNum` in `[0, copyCount)`, `memcpy` `copySize` bytes from `dstBuffer + copyOffset + copyNum * copySize` and `memcmp` against the corresponding source bytes ([line 2052 through line 2077](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2052-L2077)). On mismatch, log source offset, destination offset, and hex dumps of source and destination data.

[host] For `count_0`, sanity-check that the source data's first byte is not `'\0'`; if it is, the test logs `No copies but first char in source data is '\0', which should not happen` and fails ([line 2079 through line 2088](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079-L2088)). `copiedData` is zero-initialized and the per-copy loop does not run when `copyCount` is zero, so the check fires on the source byte rather than the destination buffer; the destination's no-write state is not directly checked.

Pass condition: every copied region matches the source bytes, and the `count_0` source-data sanity check passes (first source byte is not `'\0'`).

### Mandatory format support (`mandatory_formats.memory_to_image`)

[host] For each format in the mandatory list at [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199), query `VkFormatProperties3` chained through `VkFormatProperties2`.

[host] Check `optimalTilingFeatures & VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR`. Log every non-compliant format ([line 2215 through line 2222](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215-L2222)).

[host] Return `pass` only if every mandatory format advertises the bit; otherwise return `fail` with a single aggregated message ([line 2224](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2224)).

### Memory-to-image indirect copy (`memory_to_image_indirect*`)

[host] Generate source texels and the expected destination image from the selected regions, then upload the source buffer and initialize the destination image ([`CopyMemoryToImageIndirect::iterate`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L461-L500)).

[host] Convert every `VkBufferImageCopy` region into one `VkCopyMemoryToImageIndirectCommandKHR`. Store the records in an `IndirectImageParams` array so the address-range stride is larger than `sizeof(VkCopyMemoryToImageIndirectCommandKHR)` ([lines 625–681](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L625-L681)).

[host] Record `vkCmdCopyMemoryToImageIndirectKHR` for the destination image and submit it on the selected universal, transfer-only, or compute-only queue ([lines 682–719](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L682-L719)).

[host] Read the destination image and compare it with the expected texture level. The case passes only when the image comparison succeeds ([lines 721–724](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L721-L724)).

### Use-after-copy (`use_after_copy`)

Runtime execution lives in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). See [UseAfterCopy.md](UseAfterCopy.md) for the host/device timeline and pass conditions.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `size_4`, `size_12`, `size_full` | Indirect buffer-to-buffer copy data mismatch; stride mishandling; `count_0` writes data when it should not; queue-family dispatch routing fault |
| `memory_to_image_indirect*` | Indirect command decoding, image-region addressing, destination format/layout handling, stride handling, queue routing, or destination image content mismatch |
| `mandatory_formats` | Missing `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for one or more mandatory formats |
| `use_after_copy` | See [UseAfterCopy.md](UseAfterCopy.md); analysis is owned by the delegated page |

### Cause Analysis

#### Indirect buffer-to-buffer copy data mismatch

**Possible failure symptoms:** the test logs `Copy <N> failed: source offset <S> and destination offset <D>` followed by hex dumps of the source and destination ranges, then returns `fail`. For `count_0`, the test logs `No copies but first char in source data is '\0', which should not happen` when the source data's first byte is `'\0'` (a test-data sanity check; the destination buffer is not directly checked). Both checks come from the `memcmp` validation at [line 2059](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2059) and the `count_0` source-data sanity check at [line 2079 through line 2088](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079-L2088).

**Possible implementation causes:** the device read the wrong bytes from `indirectBuffer` because the `stride` field of `VkStridedDeviceAddressRangeKHR` was not applied when `stride > sizeof(VkCopyMemoryIndirectCommandKHR)`; the device computed a wrong `dstAddress` for `copyCount > 1` (each record's destination is `dstBufferAddress + copyOffset + i * copySize`); or the implementation advertised a queue family in `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues` but failed to dispatch the command on that queue family. Source-level investigation would be needed to confirm which path applies to a specific failing case.

#### Mandatory format feature bit missing

**Possible failure symptoms:** the test logs `Format <X> missing VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR in optimalTilingFeatures` for each non-compliant format and returns `fail` after checking every format. The symptom comes from the format feature check at [line 2215](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215).

**Possible implementation causes:** the driver does not advertise `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for one or more formats mandated by the `VK_KHR_copy_memory_indirect` specification. The mandatory list lives at [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199); any format missing the bit in `optimalTilingFeatures` after the extension is enabled is a spec compliance defect.

#### Indirect memory-to-image result mismatch

**Possible failure symptoms:** after `vkCmdCopyMemoryToImageIndirectKHR`, the readback image differs from the texture reference generated from the selected buffer-image regions. The failure is reported by the common image comparison returned from [`CopyMemoryToImageIndirect::iterate`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L721-L724).

**Possible implementation causes:** the implementation may have decoded the strided `VkCopyMemoryToImageIndirectCommandKHR` records incorrectly, mishandled row length, image height, subresource, offset, extent, mip or array selection, or executed the command incorrectly on an advertised queue family. A format-specific failure may instead indicate incorrect support for `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` on the selected tiling path.

## Case Pruning

### Requirement-based pruning

- The whole test family is non-VulkanSC only. `#ifndef CTS_USES_VULKANSC` guards the entire source file, and the dispatcher in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) registers the family only on non-SC builds.
- `VK_KHR_copy_memory_indirect` is required for every test case in this family ([line 786](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L786), [line 2112](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2112)).
- The `indirectMemoryCopy` feature is required for buffer-to-buffer indirect copy cases ([line 2115](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2115)).
- The `indirectMemoryToImageCopy` feature is required for every `memory_to_image_indirect*` case ([lines 784–805](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L784-L805)).
- The implementation must advertise the chosen queue family in `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues`. Cases skip with `NotSupportedError` when the requested family bit is missing ([line 2122 through line 2127](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2122-L2127), mirrored for memory-to-image at [line 521 through line 547](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L521-L547)).
- `VK_KHR_format_feature_flags2` is required for the `mandatory_formats` case ([line 2149](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2149)).
- Each memory-to-image case checks `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for the selected format and tiling; transfer-only cases also check transfer granularity ([lines 745–805](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L745-L805)).

### Design-based pruning

- For `size_4`, the registration loop skips `offset_4` because the offset (4 bytes) is not strictly less than the copy size (4 bytes). The pruning happens at [line 2313](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2313). `size_12` and `size_full` keep both `offset_0` and `offset_4`.

## Key Takeaways

- The source exercises both indirect extension commands: `vkCmdCopyMemoryIndirectKHR` for buffer-to-buffer copies and `vkCmdCopyMemoryToImageIndirectKHR` for buffer-to-image copies, plus the mandatory-format query path.
- The `long_stride` matrix is the only path that exercises the `stride` field of `VkStridedDeviceAddressRangeKHR`; it wraps each command in a larger struct with dummy fields.
- `count_0` is a behavioral boundary: the implementation must perform no copy when `copyCount` is zero. The test only sanity-checks that the source data's first byte is not `'\0'` so the no-op case is testable; the destination buffer's no-write state is not directly checked.
- `mandatory_formats` aggregates all format failures into a single pass/fail verdict; the failure message lists every non-compliant format before returning.
- The `memory_to_image_indirect*` families reuse one implementation across allocation kinds and queue families while varying image dimensionality, format, mip/array structure, and copy-region layout.
- [UseAfterCopy.md](UseAfterCopy.md) owns the failure analysis for `use_after_copy`; this page does not duplicate it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createCopyMemoryIndirectTests()` | [vktApiCopyMemoryIndirectTests.cpp#L2253](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253) | Builds the `copy_memory_indirect` group tree. |
| `addIndirectCopyTests()` | [vktApiCopiesAndBlittingTests.cpp#L74-L116](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74-L116) | Registers the six `memory_to_image_indirect*` families under `core` and `dedicated_allocation`. |
| `addCopyMemoryToImageTests()` | [vktApiCopyMemoryIndirectTests.cpp#L2243-L2251](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243-L2251) | Builds the six common direct children below every memory-to-image family. |
| `CopyMemoryToImageIndirect::iterate()` | [vktApiCopyMemoryIndirectTests.cpp#L461-L724](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L461-L724) | Generates indirect records, executes the image copy, reads the destination, and validates it. |
| Size/offset/count/stride/queue registration loop | [vktApiCopyMemoryIndirectTests.cpp#L2295-L2329](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2295-L2329) | Generates the `size_*` subtree and applies the `offset >= size` pruning. |
| `CopyMemoryIndirectTestInstance` | [vktApiCopyMemoryIndirectTests.cpp#L1872](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872) | Buffer-to-buffer indirect copy instance, including `memcmp` and `count_0` checks. |
| `CopyMemoryIndirectTestCase::checkSupport` | [vktApiCopyMemoryIndirectTests.cpp#L2110-L2132](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2110-L2132) | Extension, feature, and queue-family support gates. |
| `MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests` | [vktApiCopyMemoryIndirectTests.cpp#L2155](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155) | Mandatory format feature query loop and aggregated verdict. |
| `createUseAfterXferGroup(testCtx, true)` | [vktApiCopyMemoryIndirectTests.cpp#L2338](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) | Registers `use_after_copy` with `indirect=true`; implementation is in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). |
| `addCopyImageToBufferIndirectTests()` | [vktApiCopyMemoryIndirectTests.cpp#L2236-L2241](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236-L2241) | Implements the sibling indirect image-to-buffer registrations documented by `CopyImageToBuffer.md`; it is not part of this page's ownership tree. |
| Header | [vktApiCopyMemoryIndirectTests.hpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp) | Public entry points exported from this translation unit. |
