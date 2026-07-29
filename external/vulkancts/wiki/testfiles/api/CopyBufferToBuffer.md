## Overview

**Core question:** Does `vkCmdCopyBuffer` (and its extension variants `vkCmdCopyBuffer2` and `vkCmdCopyMemoryKHR`) copy the exact bytes specified by each region while leaving every other destination byte untouched?

- This page covers the `buffer_to_buffer` test family implemented in [vktApiCopyBufferToBufferTests.cpp](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp) and registered under the `copy_and_blit` composite family via [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421).
- The test family is registered under four variant intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`, and `device_address`), each producing the same internal test case structure with different allocation, extension, and queue parameters.
- The same source file also registers a `buffer_to_buffer_with_offset` sibling test family under `core` only, which tests all `srcOffset`/`dstOffset` combinations.
- The test issues a buffer-to-buffer copy command and compares the destination bytes against a CPU-computed reference built by `deMemcpy` of the same regions.
- Passing requires every copied byte to match the reference and every non-copied destination byte to remain at its initial value.

## Background Knowledge

- **`vkCmdCopyBuffer` and its extension variants.** The Vulkan core command `vkCmdCopyBuffer` copies bytes between buffer regions. The `VK_KHR_copy_commands2` extension provides `vkCmdCopyBuffer2`, which takes the same parameters through a `VkCopyBufferInfo2KHR` structure. The `VK_KHR_device_address_commands` extension provides `vkCmdCopyMemoryKHR`, which copies between device addresses instead of buffer handles. All three should produce identical byte-level results for the same regions.
- **Bit-exact CPU reference.** The test builds its expected destination by `deMemcpy`-ing each source region into the destination at the recorded offset. There is no format conversion, swizzling, or tolerance. The comparison threshold is zero.
- **Host-visible allocation.** Both source and destination buffers are allocated as host-visible so the test can upload source bytes and invalidate/read back destination bytes without a staging copy.

## Registration Hierarchy

```text
api.copy_and_blit.core.buffer_to_buffer
├── whole
├── partial
├── regions
├── unaligned_regions
├── whole_large
├── partial_large
├── partial_large_unaligned_size
└── unaligned_regions_large
```

The tree uses the `core` variant as the representative path. The same `buffer_to_buffer` family is registered under three additional variant intermediate nodes, each calling [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421) with different `testGroupParams`:

- `dedicated_allocation`: uses `ALLOCATION_KIND_DEDICATED` instead of suballocated memory ([addDedicatedAllocationCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L241)).
- `copy_commands2`: requires `VK_KHR_copy_commands2` and routes through `vkCmdCopyBuffer2` ([copy_commands2 lambda](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L275)).
- `device_address`: requires `VK_KHR_device_address_commands` and routes through `vkCmdCopyMemoryKHR` ([addDeviceAddressTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249)). This variant omits `regions`, `unaligned_regions`, and `unaligned_regions_large` due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015 ([pruning](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L474)).

A `buffer_to_buffer_transfer_queue` sibling is registered under `core`, `dedicated_allocation`, and `copy_commands2` with `TransferOnly` queue selection ([addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L176)). It has the same internal test case structure.

A `buffer_to_buffer_with_offset` sibling is registered under `core` only by [addCopyBufferToBufferOffsetTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L621). It generates 64 test case leaves (`0_0` through `7_7`) covering all `srcOffset`/`dstOffset` combinations from 0 to `kMaxOffset - 1 = 7`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Buffer size | `defaultSize` (64), `defaultQuarterSize` (16), `defaultLargeSize` (4096), `2 * defaultLargeSize` (8192), 32 | Tests copy behavior across small and large buffers. Large sizes exercise wider copy ranges and unaligned sizes. | [vktApiCopiesAndBlittingUtil.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L161-L166) |
| Copy region count | single region, 4 regions, 5 regions, 16 regions | Single-region tests isolate offset/size handling. Multi-region tests exercise region iteration and inter-region byte preservation. | [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421-L619) |
| Region offsets | aligned (0, 1024, 2048) and unaligned (1, 3, 6, 9, 11) | Aligned offsets test the basic path. Unaligned offsets test that the driver handles non-4-byte boundaries. | [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421-L619) |
| Region sizes | aligned and unaligned (1, 2, 3, 4, 5, 1..16, 2048, 4097) | Unaligned sizes test that the driver copies the exact byte count without over-reading or over-writing. | [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421-L619) |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `DEVICE_ADDRESS_COMMANDS` | Selects which copy command variant is recorded: `vkCmdCopyBuffer`, `vkCmdCopyBuffer2`, or `vkCmdCopyMemoryKHR`. | [vktApiCopiesAndBlittingUtil.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L132-L144) |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Tests that copy behavior is identical whether buffers share a memory allocation or each has a dedicated allocation. | [vktApiCopiesAndBlittingUtil.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L124-L128) |
| `queueSelection` | `Universal`, `TransferOnly` | Tests that copy submission works on both universal and transfer-only queue families. | [vktApiCopiesAndBlittingUtil.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L244-L249) |

## Behavior Parameters

The primary behavioral axis is the copy region shape, which clusters the 8 test case leaves into three groups with distinct mechanisms.

### Single whole-buffer region: copy an entire buffer with no offsets

The `whole` and `whole_large` leaves issue a single region covering the entire buffer with `srcOffset = 0`, `dstOffset = 0`, and `size = buffer.size`. This is the simplest copy path: there is no offset arithmetic or region iteration, and the destination is fully overwritten. The `whole` leaf uses a 64-byte buffer ([defaultSize](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L161)); `whole_large` uses a 4096-byte buffer ([defaultLargeSize](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L166)) to test the same path at a larger scale. Registered at [vktApiCopyBufferToBufferTests.cpp#L445](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L445) and [vktApiCopyBufferToBufferTests.cpp#L543](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L543).

### Single partial region with offsets: copy a sub-range at non-zero offsets

The `partial`, `partial_large`, and `partial_large_unaligned_size` leaves issue a single region with non-zero `srcOffset` and `dstOffset`. This tests that the driver reads from and writes to the correct byte positions, and that bytes before `dstOffset` and after the copy region in the destination remain untouched. `partial` uses a 16-byte buffer with a 1-byte copy at `srcOffset=12`, `dstOffset=4` ([vktApiCopyBufferToBufferTests.cpp#L469](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L469)). `partial_large` uses a 4096-byte buffer with a 2048-byte copy at `srcOffset=1024`, `dstOffset=2048` ([vktApiCopyBufferToBufferTests.cpp#L566](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L566)). `partial_large_unaligned_size` uses an 8192-byte buffer with a 4097-byte copy (size is `1 + defaultLargeSize`), testing an unaligned size at large scale ([vktApiCopyBufferToBufferTests.cpp#L589](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L589)).

### Multiple regions: copy several regions in one command

The `regions`, `unaligned_regions`, and `unaligned_regions_large` leaves issue multiple regions in a single `vkCmdCopyBuffer` call. This tests that the driver iterates regions, applies each region's offsets and sizes independently, and does not corrupt bytes between regions. `regions` issues 16 regions with sizes 1 through 16 into a 272-byte destination ([vktApiCopyBufferToBufferTests.cpp#L500](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L500)). `unaligned_regions` issues 4 regions with offsets including non-4-byte-aligned values (srcOffset: 3, 6, 9, 12; dstOffset: 1, 6, 11, 16) and sizes 2 through 5 ([vktApiCopyBufferToBufferTests.cpp#L520](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L520)). `unaligned_regions_large` issues 5 regions with large unaligned offsets in an 8192-byte buffer ([vktApiCopyBufferToBufferTests.cpp#L617](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L617)).

## Shader Analysis

No shader is involved in this test family. The copy is performed by fixed-function transfer hardware or driver-internal copy logic, and all verification happens on the host.

## Runtime Execution and Result Checking

- The host creates source and destination buffers with `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` and `VK_BUFFER_USAGE_TRANSFER_DST_BIT` respectively, both allocated as host-visible ([constructBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L142), [bindBufferMemory()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L159)).
- The source buffer is filled with `FILL_MODE_RED` and the destination with `FILL_MODE_BLACK` using [generateFilledBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L176). These fill modes produce deterministic byte patterns that make any unintended copy or corruption visible.
- The host builds a CPU reference by [copyRegionToTextureLevel()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L271), which `deMemcpy`s each region's source bytes into the destination at the recorded offset. This reference is bit-exact: no format conversion, no tolerance.
- The host uploads the source and destination patterns, records a pipeline barrier from `HOST` to `TRANSFER` for the source, records the copy command, records a barrier from `TRANSFER` to `HOST` for the destination, and submits ([recordAndSubmitCommandBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L188)).
- The copy command is selected by `extensionFlags`: `vkCmdCopyBuffer` for `NONE`, `vkCmdCopyBuffer2` for `COPY_COMMANDS_2`, `vkCmdCopyMemoryKHR` for `DEVICE_ADDRESS_COMMANDS` ([recordAndSubmitCommandBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L212-L263)).
- After submission, the host invalidates the destination allocation and reads it back as `VK_FORMAT_R32_UINT` ([iterate()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L131-L139)).
- The result is checked by [checkTestResult()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485) from the base class, which performs `intThresholdCompare` with a zero threshold against the CPU reference.
- The `buffer_to_buffer_with_offset` sibling uses a separate flow in [bufferOffsetTest()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L326): it zeroes the destination, fills the source with nonzero bytes, copies `kMaxOffset` blocks of increasing size (1 through 8), and verifies with [checkZerosAt()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L311) that bytes before `dstOffset` and after the copy region remain zero, while copied bytes match the source exactly.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Single whole-buffer region (`whole`, `whole_large`) | Basic copy path failure or host/device visibility failure. |
| Single partial region with offsets (`partial`, `partial_large`, `partial_large_unaligned_size`) | Offset handling failure or out-of-region destination corruption. |
| Multiple regions (`regions`, `unaligned_regions`, `unaligned_regions_large`) | Region iteration failure, per-region offset/size handling failure, or inter-region byte corruption. |
| All leaves under one variant (e.g., `copy_commands2` or `device_address`) | Extension command variant mismatch or extension-specific parameter conversion failure. |
| All leaves under `buffer_to_buffer_transfer_queue` | Transfer-queue submission or queue-family ownership failure. |

### Cause Analysis

#### Basic copy path failure or host/device visibility failure

**Possible failure symptoms:** The destination buffer does not match the CPU reference after a whole-buffer copy. `checkTestResult` reports `intThresholdCompare` failure with a zero threshold, meaning at least one byte differs from the expected value ([checkTestResult()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485)).

**Possible implementation causes:** The source bytes were not visible to the device at copy time, or the destination bytes were not visible to the host at readback time, due to missing or incorrectly scoped memory barriers ([recordAndSubmitCommandBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L196-L210)). Alternatively, the driver's copy implementation did not transfer the exact bytes for the whole-buffer region. Distinguishing between visibility and copy-logic failures requires source-level investigation of the barrier setup and the driver's `vkCmdCopyBuffer` path.

#### Offset handling failure or out-of-region destination corruption

**Possible failure symptoms:** For partial-region leaves, copied bytes are wrong (offset by the wrong amount, or read from/written to the wrong position), or bytes outside the destination region changed from their initial `FILL_MODE_BLACK` value. `checkTestResult` reports a mismatch at the copied region boundary or in the untouched prefix/suffix.

**Possible implementation causes:** The driver applied `srcOffset` or `dstOffset` incorrectly, computed the wrong source or destination address, or copied more bytes than `region.size` specified. For `partial_large_unaligned_size`, the unaligned size (`1 + defaultLargeSize`) may expose a driver path that rounds the copy size up to a wider internal granularity. Source-level investigation is needed to determine whether the failure is in address computation or size handling.

#### Region iteration failure, per-region offset/size handling failure, or inter-region byte corruption

**Possible failure symptoms:** For multi-region leaves, some regions are copied correctly while others are missing, duplicated, or written to the wrong destination offset. Bytes between regions in the destination are corrupted. `checkTestResult` reports mismatches at multiple region boundaries.

**Possible implementation causes:** The driver's region loop did not advance to the next region, applied the wrong region's offsets, or overwrote adjacent regions due to incorrect size or boundary handling. For `unaligned_regions` and `unaligned_regions_large`, the unaligned offsets and sizes may expose a driver path that aligns internally and corrupts neighboring bytes. Source-level investigation is needed to determine whether the failure is in region iteration or per-region address/size handling.

#### Extension command variant mismatch or extension-specific parameter conversion failure

**Possible failure symptoms:** The `core` variant passes but the `copy_commands2` or `device_address` variant fails for the same test case leaf, even though the regions are identical. The destination differs from the CPU reference only under the extension command path.

**Possible implementation causes:** The extension command path converts `VkBufferCopy` regions to `VkBufferCopy2KHR` ([convertvkBufferCopyTovkBufferCopy2KHR()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L241)) or to `VkDeviceMemoryCopyKHR` ranges ([recordAndSubmitCommandBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L219-L234)) incorrectly, or the driver's `vkCmdCopyBuffer2` or `vkCmdCopyMemoryKHR` implementation takes a different code path from `vkCmdCopyBuffer` and produces different bytes. Source-level investigation is needed to confirm whether the conversion is lossless and whether the driver's extension path matches the core path.

#### Transfer-queue submission or queue-family ownership failure

**Possible failure symptoms:** The `buffer_to_buffer_transfer_queue` sibling fails while the universal-queue `buffer_to_buffer` variant passes for the same test case leaf. The destination is empty, partially copied, or contains stale data.

**Possible implementation causes:** The transfer-only queue family does not support the copy command, the queue family ownership transfer for the source or destination buffer was not performed correctly, or the submission waited on the wrong synchronization primitive. The buffers are created with `VK_SHARING_MODE_EXCLUSIVE` ([constructBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L142-L157)), so concurrent access from a different queue family without explicit ownership transfer would produce undefined behavior. Source-level investigation is needed to confirm whether the failure is in queue family selection, ownership transfer, or synchronization.

## Case Pruning

### Requirement-based pruning

- `copy_commands2` variant requires `VK_KHR_copy_commands2` (or Vulkan 1.3), checked by [checkExtensionSupport()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) via `context.requireDeviceFunctionality("VK_KHR_copy_commands2")` ([vktApiCopiesAndBlittingUtil.cpp#L255-L256](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L255-L256)).
- `device_address` variant requires `VK_KHR_device_address_commands`, checked by [checkExtensionSupport()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) via `context.requireDeviceFunctionality("VK_KHR_device_address_commands")` ([vktApiCopiesAndBlittingUtil.cpp#L279-L280](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L279-L280)).
- `buffer_to_buffer_transfer_queue` requires a transfer-only queue family with appropriate queue family support.
- The `device_address` variant additionally prunes `regions`, `unaligned_regions`, and `unaligned_regions_large` due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015 ([vktApiCopyBufferToBufferTests.cpp#L474](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L474), [vktApiCopyBufferToBufferTests.cpp#L594](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L594)). This VUID disallows multiple overlapping address ranges in `vkCmdCopyMemoryKHR`.

### Design-based pruning

- The `buffer_to_buffer_with_offset` sibling is registered under `core` only. It is not duplicated under `dedicated_allocation`, `copy_commands2`, or `device_address` because its purpose is to test offset combinations, not allocation or extension behavior.
- The `buffer_to_buffer_transfer_queue` sibling is not registered under `device_address` because the device-address copy command is not exercised on a transfer-only queue in this test family.
- Buffer sizes and region shapes are fixed per test case leaf. There is no generated matrix of size × region × offset combinations; each leaf covers one deliberately chosen shape.

## Key Takeaways

- The `buffer_to_buffer` test family verifies bit-exact byte copy through `vkCmdCopyBuffer`, `vkCmdCopyBuffer2`, and `vkCmdCopyMemoryKHR`, with a zero-threshold CPU reference built by `deMemcpy`.
- The 8 test case leaves cluster into three behavioral groups: whole-buffer copy, partial copy with offsets, and multi-region copy. Each group isolates a distinct copy mechanism.
- The same test case structure is registered under four variant intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`, `device_address`) to test allocation kind, extension command, and queue selection independently.
- The `device_address` variant prunes multi-region cases due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015, which disallows overlapping address ranges in `vkCmdCopyMemoryKHR`.
- The `buffer_to_buffer_with_offset` sibling under `core` tests all `srcOffset`/`dstOffset` combinations from 0 to 7, verifying that bytes outside the copy region remain zero.
- See `## Failure Meaning` for the failure interpretation: failures point to basic copy logic, offset/size handling, region iteration, extension variant mismatch, or transfer-queue submission issues.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [addCopyBufferToBufferTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421) | Registers the 8 test case leaves under the `buffer_to_buffer` group for each variant. |
| Offset sibling registration | [addCopyBufferToBufferOffsetTests()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L621) | Registers the `buffer_to_buffer_with_offset` group with 64 offset-combination cases. |
| Test instance | [CopyBufferToBuffer::iterate()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L108) | Creates buffers, fills them, records the copy, reads back, and checks the result. |
| Copy command recording | [recordAndSubmitCommandBuffer()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L188) | Selects between `vkCmdCopyBuffer`, `vkCmdCopyBuffer2`, and `vkCmdCopyMemoryKHR` based on `extensionFlags`. |
| CPU reference builder | [copyRegionToTextureLevel()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L271) | `deMemcpy`s each region's source bytes into the destination at the recorded offset. |
| Offset test verification | [checkZerosAt()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L311) | Verifies bytes before `dstOffset` and after the copy region remain zero in the offset sibling. |
| Offset test flow | [bufferOffsetTest()](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L326) | Separate test flow for the `buffer_to_buffer_with_offset` sibling. |
| DAC pruning | [vktApiCopyBufferToBufferTests.cpp#L474](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L474) | Skips `regions` and `unaligned_regions` under `DEVICE_ADDRESS_COMMANDS` due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015. |
| DAC pruning (large) | [vktApiCopyBufferToBufferTests.cpp#L594](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L594) | Skips `unaligned_regions_large` under `DEVICE_ADDRESS_COMMANDS` for the same VUID. |
| Parent dispatcher | [addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) | Registers `buffer_to_buffer` and `buffer_to_buffer_transfer_queue` under each variant. |
| Core variant entry | [addCoreCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232) | Adds the `core` variant and calls `addCopyBufferToBufferOffsetTests()`. |
| Device-address variant entry | [addDeviceAddressTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249) | Adds the `device_address` variant with `DEVICE_ADDRESS_COMMANDS`. |
| Extension support check | [checkExtensionSupport()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L253-L281) | Gates each variant on its required extension. |
| Result comparison | [checkTestResult()](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485) | `intThresholdCompare` with zero threshold against the CPU reference. |
| Test params and constants | [vktApiCopiesAndBlittingUtil.hpp#L161-L166](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L161-L166) | Defines `defaultSize`, `defaultQuarterSize`, and `defaultLargeSize`. |
| Mustpass evidence | [api.txt](../../../mustpass/main/vk-default/api.txt) | Contains the registered `dEQP-VK.api.copy_and_blit.*.buffer_to_buffer.*` paths. |
