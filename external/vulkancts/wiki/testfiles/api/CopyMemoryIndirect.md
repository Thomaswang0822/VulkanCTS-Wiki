## Overview

**Core question:** does the implementation execute `vkCmdCopyMemoryIndirectKHR` correctly when copy parameters come from device memory, and does it advertise the indirect-copy format feature bit for every mandatory format?

This page covers the `api.copy_and_blit.copy_memory_indirect` test family, implemented in [`vktApiCopyMemoryIndirectTests.cpp`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp). The test family is non-VulkanSC only; `#ifndef CTS_USES_VULKANSC` guards the entire source file.

The family registers three behaviors at the intermediate-node level:

- buffer-to-buffer indirect copy through `vkCmdCopyMemoryIndirectKHR`, with copy size, copy count, stride, and queue family as the varied parameters (`size_4`, `size_12`, `size_full`);
- mandatory format feature compliance, querying `VkFormatProperties3` for every format mandated by `VK_KHR_copy_memory_indirect` (`mandatory_formats`);
- use-after-copy verification with indirect copy commands, delegated to [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp) (`use_after_copy`).

## Background Knowledge

- `VK_KHR_copy_memory_indirect` exposes two indirect copy commands: `vkCmdCopyMemoryIndirectKHR` (buffer-to-buffer) and `vkCmdCopyMemoryToImageIndirectKHR` (buffer-to-image). Their copy parameters come from device memory, not the command call site: the host writes `VkCopyMemoryIndirectCommandKHR` (or `VkCopyMemoryToImageIndirectCommandKHR`) records into a device-visible buffer, and the device reads them through a `VkStridedDeviceAddressRangeKHR` address range. This page tests the buffer-to-buffer command and the format feature compliance check.
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
```

`size_4`, `size_12`, and `size_full` each expand to a four-level tree of intermediate nodes ending in test case leaves: `<size>.<offset>.<count>.<stride>.<queue>`, where `<queue>` is `graphics`, `transfer`, or `compute` (see [parameter dimensions](#parameter-dimensions-and-observed-values)). `mandatory_formats` has a single test case leaf `memory_to_image`. `use_after_copy` is delegated to [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp); its child structure is documented in [`vktApiUseAfterCopyTests.md`](./vktApiUseAfterCopyTests.md).

Evidence: `copy_memory_indirect` group created by [`createCopyMemoryIndirectTests()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253); `size_*` groups added in the size loop at [line 2295 through line 2329](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2295-L2329); `mandatory_formats` added at [line 2332](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2332); `use_after_copy` added via [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) with `indirect=true`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Copy size | `size_4` (4 bytes), `size_12` (12 bytes), `size_full` (0, full buffer) | Bytes copied per indirect command. `0` signals a whole-buffer copy. Drives the parent intermediate node. | [L2269](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2269) |
| Copy count | `count_0`, `count_1`, `count_2`, `count_63` | Number of `VkCopyMemoryIndirectCommandKHR` records the device must walk. `count_0` is the no-op boundary. | [L2262](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2262) |
| Copy offset | `offset_0`, `offset_4` | Byte offset applied to both source and destination addresses. Pruned when `offset >= size`. | [L2276](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2276) |
| Stride | `normal_stride`, `long_stride` | Stride between consecutive indirect commands. `normal_stride` is `sizeof(VkCopyMemoryIndirectCommandKHR)`; `long_stride` is `sizeof(IndirectParams)`, a larger struct carrying dummy parameters. | [L2283](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2283) |
| Queue family | `graphics`, `transfer`, `compute` | Queue family that receives `vkCmdCopyMemoryIndirectKHR`. Selected from `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues`. | [L2291](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2291) |

The `mandatory_formats` intermediate node exposes one test case leaf, `memory_to_image`, whose matrix is the closed list of mandatory formats enumerated in [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199).

## Behavior Parameters

The primary behavioral axis is the intermediate node directly below `copy_memory_indirect`. Each value changes which property is being tested.

### size_4, size_12, size_full — Buffer-to-buffer indirect copy

These three intermediate nodes share one mechanism: build `VkCopyMemoryIndirectCommandKHR` records in a host-visible indirect buffer, dispatch `vkCmdCopyMemoryIndirectKHR`, then verify the destination bytes match the source. The behavior is the same for each; only the copy size differs. `size_full` uses `copySize = 0`, which the test interprets as "copy the whole buffer minus the offset". The implementation class is [`CopyMemoryIndirectTestInstance`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872); the case class is [`CopyMemoryIndirectTestCase`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2101).

The `long_stride` variant tests the `stride` field of `VkStridedDeviceAddressRangeKHR`: the device must read each `VkCopyMemoryIndirectCommandKHR` from a struct embedded in a larger `IndirectParams` layout, ignoring the trailing dummy fields.

### mandatory_formats — Mandatory format feature compliance

This single test case leaf queries `VkFormatProperties3` (chained through `VkFormatProperties2`) for every format mandated by `VK_KHR_copy_memory_indirect` and verifies that `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` is set in `optimalTilingFeatures`. The check is implemented as a function case in [`MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155). The case logs every non-compliant format before returning a single pass/fail verdict.

### use_after_copy — Use-after-copy verification (delegated)

This intermediate node is registered in this file via [`createUseAfterXferGroup(testCtx, true)`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) but the implementation lives in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). The delegated test verifies that image contents written by indirect copy commands can still be consumed correctly afterward (sampled as a texture or used as a depth/stencil attachment). The detailed behavior, parameters, and failure analysis are documented in [`vktApiUseAfterCopyTests.md`](./vktApiUseAfterCopyTests.md).

## Shader Analysis

No shader runs in any test case under `copy_memory_indirect`. The in-file behaviors use fixed-function copy commands (`vkCmdCopyMemoryIndirectKHR`) and host-side format property queries; the delegated `use_after_copy` consumes image data through sampling or attachment use but does not generate or analyze a shader for the indirect copy itself.

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

[host] For `count_0`, verify the device did not write to the destination by checking that the first destination byte does not equal the first source byte; if they match, the implementation performed a copy when `copyCount` was zero, violating the no-op contract ([line 2079 through line 2088](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079-L2088)).

Pass condition: every copied region matches the source bytes, and `count_0` leaves the destination untouched.

### Mandatory format support (`mandatory_formats.memory_to_image`)

[host] For each format in the mandatory list at [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199), query `VkFormatProperties3` chained through `VkFormatProperties2`.

[host] Check `optimalTilingFeatures & VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR`. Log every non-compliant format ([line 2215 through line 2222](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215-L2222)).

[host] Return `pass` only if every mandatory format advertises the bit; otherwise return `fail` with a single aggregated message ([line 2224](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2224)).

### Use-after-copy (`use_after_copy`)

Runtime execution lives in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). See [`vktApiUseAfterCopyTests.md`](./vktApiUseAfterCopyTests.md) for the host/device timeline and pass conditions.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `size_4`, `size_12`, `size_full` | Indirect buffer-to-buffer copy data mismatch; stride mishandling; `count_0` writes data when it should not; queue-family dispatch routing fault |
| `mandatory_formats` | Missing `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for one or more mandatory formats |
| `use_after_copy` | See [`vktApiUseAfterCopyTests.md`](./vktApiUseAfterCopyTests.md); analysis is owned by the delegated page |

### Cause Analysis

#### Indirect buffer-to-buffer copy data mismatch

**Possible failure symptoms:** the test logs `Copy <N> failed: source offset <S> and destination offset <D>` followed by hex dumps of the source and destination ranges, then returns `fail`. For `count_0`, the test logs `No copies but first char in source data is '\0', which should not happen` when the first destination byte equals the first source byte. Both checks come from the `memcmp` validation at [line 2059](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2059) and the `count_0` no-write check at [line 2079 through line 2088](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2079-L2088).

**Possible implementation causes:** the device read the wrong bytes from `indirectBuffer` because the `stride` field of `VkStridedDeviceAddressRangeKHR` was not applied when `stride > sizeof(VkCopyMemoryIndirectCommandKHR)`; the device computed a wrong `dstAddress` for `copyCount > 1` (each record's destination is `dstBufferAddress + copyOffset + i * copySize`); the device wrote data when `copyCount == 0`, violating the no-op contract; or the implementation advertised a queue family in `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues` but failed to dispatch the command on that queue family. Source-level investigation would be needed to confirm which path applies to a specific failing case.

#### Mandatory format feature bit missing

**Possible failure symptoms:** the test logs `Format <X> missing VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR in optimalTilingFeatures` for each non-compliant format and returns `fail` after checking every format. The symptom comes from the format feature check at [line 2215](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2215).

**Possible implementation causes:** the driver does not advertise `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` for one or more formats mandated by the `VK_KHR_copy_memory_indirect` specification. The mandatory list lives at [line 2159 through line 2199](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2159-L2199); any format missing the bit in `optimalTilingFeatures` after the extension is enabled is a spec compliance defect.

## Case Pruning

### Requirement-based pruning

- The whole test family is non-VulkanSC only. `#ifndef CTS_USES_VULKANSC` guards the entire source file, and the dispatcher in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) registers the family only on non-SC builds.
- `VK_KHR_copy_memory_indirect` is required for every test case in this family ([line 786](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L786), [line 2112](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2112)).
- The `indirectMemoryCopy` feature is required for buffer-to-buffer indirect copy cases ([line 2115](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2115)).
- The implementation must advertise the chosen queue family in `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR::supportedQueues`. Cases skip with `NotSupportedError` when the requested family bit is missing ([line 2122 through line 2127](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2122-L2127), mirrored for memory-to-image at [line 521 through line 547](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L521-L547)).
- `VK_KHR_format_feature_flags2` is required for the `mandatory_formats` case ([line 2149](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2149)).

### Design-based pruning

- For `size_4`, the registration loop skips `offset_4` because the offset (4 bytes) is not strictly less than the copy size (4 bytes). The pruning happens at [line 2313](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2313). `size_12` and `size_full` keep both `offset_0` and `offset_4`.

## Key Takeaways

- The `copy_memory_indirect` test family exercises one device-side command (`vkCmdCopyMemoryIndirectKHR`) and one host-side query path (`VkFormatProperties3` with `VK_KHR_format_feature_flags2`). The third sub-behavior delegates to `use_after_copy`.
- The `long_stride` matrix is the only path that exercises the `stride` field of `VkStridedDeviceAddressRangeKHR`; it wraps each command in a larger struct with dummy fields.
- `count_0` is a behavioral boundary: the implementation must perform no copy when `copyCount` is zero. The test detects a violation by checking that the first destination byte still differs from the first source byte after the `0xFF` clear.
- `mandatory_formats` aggregates all format failures into a single pass/fail verdict; the failure message lists every non-compliant format before returning.
- [`vktApiUseAfterCopyTests.md`](./vktApiUseAfterCopyTests.md) owns the failure analysis for `use_after_copy`; this page does not duplicate it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createCopyMemoryIndirectTests()` | [vktApiCopyMemoryIndirectTests.cpp#L2253](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2253) | Builds the `copy_memory_indirect` group tree. |
| Size/offset/count/stride/queue registration loop | [vktApiCopyMemoryIndirectTests.cpp#L2295-L2329](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2295-L2329) | Generates the `size_*` subtree and applies the `offset >= size` pruning. |
| `CopyMemoryIndirectTestInstance` | [vktApiCopyMemoryIndirectTests.cpp#L1872](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1872) | Buffer-to-buffer indirect copy instance, including `memcmp` and `count_0` checks. |
| `CopyMemoryIndirectTestCase::checkSupport` | [vktApiCopyMemoryIndirectTests.cpp#L2110-L2132](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2110-L2132) | Extension, feature, and queue-family support gates. |
| `MandatoryFormats::addIndirectCopyMandatoryFormatSupportTests` | [vktApiCopyMemoryIndirectTests.cpp#L2155](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2155) | Mandatory format feature query loop and aggregated verdict. |
| `createUseAfterXferGroup(testCtx, true)` | [vktApiCopyMemoryIndirectTests.cpp#L2338](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) | Registers `use_after_copy` with `indirect=true`; implementation is in [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp). |
| Cross-file registrations: `addCopyMemoryToImageTests`, `addCopyImageToBufferIndirectTests` | [vktApiCopyMemoryIndirectTests.cpp#L2243](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2243), [vktApiCopyMemoryIndirectTests.cpp#L2236](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2236) | Implementations live in this file but are called from [`addIndirectCopyTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74) and registered under `api.copy_and_blit.core` and `api.copy_and_blit.dedicated_allocation`. They are documented in [`vktApiCopiesAndBlittingTests.md`](./vktApiCopiesAndBlittingTests.md), not on this page. |
| Header | [vktApiCopyMemoryIndirectTests.hpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp) | Public entry points exported from this translation unit. |
