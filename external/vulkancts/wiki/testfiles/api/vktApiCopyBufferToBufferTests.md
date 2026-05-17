# [vktApiCopyBufferToBufferTests.cpp](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L1)

## Overview

[`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L1) implements the `buffer_to_buffer` subgroup registered by [`addCopyBufferToBufferTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421), called from the dispatcher [`addCopiesAndBlittingTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L135). Tests for `vkCmdCopyBuffer` and its extensions (`vkCmdCopyBuffer2` via `VK_KHR_copy_commands2`, `vkCmdCopyMemoryKHR` via `VK_KHR_device_address_commands`). Verifies that buffer-to-buffer copy operations produce bit-exact results matching a CPU-side reference.

## Role of File

Implementation-heavy test file for the `buffer_to_buffer` subgroup. Contains test instance class, test case registration, and verification logic.

## Source Code

- Primary source: [vktApiCopyBufferToBufferTests.cpp](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L1)
- Header: [vktApiCopyBufferToBufferTests.hpp](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.hpp#L1)
- Parent-category registration: [`addCopiesAndBlittingTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L135)

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

The `buffer_to_buffer` group is registered by [`addCopyBufferToBufferTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421) and appears under multiple allocation/extension variant branches of `copy_and_blit`: `core`, `dedicated_allocation`, `copy_commands2`, and `device_address`. Each variant calls `addCopyBufferToBufferTests()` with different `allocationKind` and `extensionFlags` parameters, producing the same internal test case structure. The hierarchy tree above uses the `core` variant as the representative path.

A `buffer_to_buffer_transfer_queue` sibling subgroup is also registered under `core`, `dedicated_allocation`, and `copy_commands2` variants via [`addCopiesAndBlittingTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L176), using the same `addCopyBufferToBufferTests()` function with `TransferOnly` queue selection. It has the same internal test case structure.

The `regions`, `unaligned_regions`, and `unaligned_regions_large` test cases are not registered when `DEVICE_ADDRESS_COMMANDS` is set due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015.

Additionally, [`addCopyBufferToBufferOffsetTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L621) registers a `buffer_to_buffer_with_offset` sibling subgroup under `core` only.

Evidence:
- `buffer_to_buffer` group added at [`addCopiesAndBlittingTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L135)
- test cases added from [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L445) through [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L617)

## Test Families

### whole — Whole-buffer copy

Single region copy of the entire buffer (defaultSize=64 bytes), with srcOffset=0 and dstOffset=0. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L445).

### partial — Partial copy with offsets

Single region copy of 1 byte from a quarter-size buffer (defaultQuarterSize=16 bytes), with srcOffset=12 and dstOffset=4. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L469).

### regions — Multi-region copy

16 copy regions with sizes 1 through 16. Not registered when `DEVICE_ADDRESS_COMMANDS` is set. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L500).

### unaligned_regions — Unaligned multi-region copy

4 unaligned copy regions with varying offsets and sizes (srcOffset: 3,6,9,12; dstOffset: 1,6,11,16; size: 2,3,4,5). Not registered when `DEVICE_ADDRESS_COMMANDS` is set. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L520).

### whole_large — Large whole-buffer copy

Single region copy of a large buffer (defaultLargeSize=4096 bytes), with srcOffset=0 and dstOffset=0. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L543).

### partial_large — Large partial copy with offsets

Single region copy within a large buffer (defaultLargeSize=4096 bytes), with srcOffset=1024 and dstOffset=defaultLargeSize/2. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L566).

### partial_large_unaligned_size — Large partial copy with unaligned size

Single region copy within a double-large buffer (2*defaultLargeSize bytes), with srcOffset=1024, dstOffset=defaultLargeSize/2, and size=1+defaultLargeSize. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L589).

### unaligned_regions_large — Large unaligned multi-region copy

5 unaligned copy regions with varying offsets and sizes in a double-large buffer. Not registered when `DEVICE_ADDRESS_COMMANDS` is set. Registered at [`vktApiCopyBufferToBufferTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L617).

### buffer_to_buffer_with_offset — Offset combination tests (sibling subgroup, core only)

The `buffer_to_buffer_with_offset` subgroup is registered by [`addCopyBufferToBufferOffsetTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L621) as a sibling of `buffer_to_buffer` under `core` only. It contains test cases for all srcOffset/dstOffset combinations from 0 to kMaxOffset=8, using [`bufferOffsetTest()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L326). Each test case is named `{srcOffset}_{dstOffset}` and verifies that bytes before `dstOffset` and after the copy region remain zero, using [`checkZerosAt()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L311).

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Buffer sizes | `defaultSize` (64), `defaultQuarterSize` (16), `defaultLargeSize` (4096), 32 |
| Copy regions | Single whole, single partial, multiple regions (1..16), unaligned |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `DEVICE_ADDRESS_COMMANDS` |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` |
| `queueSelection` | `Universal`, `TransferOnly` |

## Support / Feature Requirements

- `COPY_COMMANDS_2` -- requires `VK_KHR_copy_commands2` or Vulkan 1.3
- `DEVICE_ADDRESS_COMMANDS` -- requires `VK_KHR_device_address_commands`
- Non-universal queue tests require appropriate queue family support
- Checked via [`checkExtensionSupport()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L356)

## Verification Methods

- **Bit-exact comparison**: The CPU reference is computed by [`copyRegionToTextureLevel()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L271) which performs `deMemcpy` of source region bytes to destination offsets
- Destination buffer is read back as `VK_FORMAT_R32_UINT` and compared via [`checkTestResult()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L454) from the base class
- Offset tests use direct byte-level comparison against expected data with [`checkZerosAt()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L311) for untouched bytes

## Test Principles

- Verify that `vkCmdCopyBuffer` copies the exact bytes specified by each region
- Verify that bytes outside the copy region in the destination are not modified
- Verify that multi-region copies with varying offsets and sizes work correctly
- Verify extension command variants (`cmdCopyBuffer2`, `cmdCopyMemoryKHR`) produce identical results
- Verify that transfer-queue submission works correctly for buffer copies

## Notes / Uncertainties

- The `regions` and `unaligned_regions` tests are skipped when `DEVICE_ADDRESS_COMMANDS` is set due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015 ([line 474](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L474))
- Only `addCopyBufferToBufferTests` and `addCopyBufferToBufferOffsetTests` are exported from the header; all other classes/functions are in the anonymous namespace
