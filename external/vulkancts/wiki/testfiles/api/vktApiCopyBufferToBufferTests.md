# vktApiCopyBufferToBufferTests



## Overview



Tests for `vkCmdCopyBuffer` and its extensions (`vkCmdCopyBuffer2` via `VK_KHR_copy_commands2`, `vkCmdCopyMemoryKHR` via `VK_KHR_device_address_commands`). Verifies that buffer-to-buffer copy operations produce bit-exact results matching a CPU-side reference.



## Role



- **Implementation-heavy test file** �?contains test instance classes, test case registration, and verification logic.



## Source Code



- [`vktApiCopyBufferToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp)

- [`vktApiCopyBufferToBufferTests.hpp`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.hpp)



## Registration Path



```

api �?copy_and_blit �?(core|dedicated_allocation|copy_commands2|device_address) �?buffer_to_buffer[_transfer_queue]

```



Registered via [`addCopyBufferToBufferTests()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L421), called from the dispatcher [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L135).



Additionally, [`addCopyBufferToBufferOffsetTests()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L621) is called only in the `core` subgroup.



## Test Hierarchy



```

buffer_to_buffer

├── whole                (defaultSize=64, single region, offset 0�?)

├── partial              (quarterSize=16, srcOffset=12, dstOffset=4, size=1)

├── regions              (16 regions of sizes 1..16, not for DEVICE_ADDRESS_COMMANDS)

├── unaligned_regions    (4 unaligned regions, not for DEVICE_ADDRESS_COMMANDS)

├── whole_large          (4096 bytes, single region)

├── partial_large        (4096 bytes, srcOffset=1024, dstOffset=2048)

└── partial_large_unaligned_size  (observed in code, not fully inspected)

```



Offset tests subgroup (core only):

```

buffer_offset_tests

└── (tests for srcOffset/dstOffset combinations up to kMaxOffset=8)

```



## Test Families



### `CopyBufferToBuffer` (class)



- Inherits [`CopiesAndBlittingTestInstance`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L420)

- Creates source and destination `VkBuffer` with `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` / `VK_BUFFER_USAGE_TRANSFER_DST_BIT`

- When `DEVICE_ADDRESS_COMMANDS` flag is set, also adds `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`

- Records copy commands via `vkCmdCopyBuffer`, `vkCmdCopyBuffer2`, or `vkCmdCopyMemoryKHR` depending on `extensionFlags`



### `BufferToBufferTestCase` (class)



- Inherits `vkt::TestCase`

- [`checkSupport()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L294) delegates to `checkExtensionSupport()` from the utility



### Offset Tests



- [`bufferOffsetTest()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L326) �?standalone function-case test

- Verifies that bytes before `dstOffset` and after the copy region remain zero

- Uses [`BufferOffsetParams`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L303) with `kMaxOffset=8`



## Parameter Dimensions



| Parameter | Observed Values |

|-----------|----------------|

| Buffer sizes | `defaultSize` (64), `defaultQuarterSize` (16), `defaultLargeSize` (4096), 32 |

| Copy regions | Single whole, single partial, multiple regions (1..16), unaligned |

| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `DEVICE_ADDRESS_COMMANDS` |

| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` |

| `queueSelection` | `Universal`, `TransferOnly` |



## Support / Feature Requirements



- `COPY_COMMANDS_2` �?requires `VK_KHR_copy_commands2` or Vulkan 1.3

- `DEVICE_ADDRESS_COMMANDS` �?requires `VK_KHR_device_address_commands`

- Non-universal queue tests require appropriate queue family support

- Checked via [`checkExtensionSupport()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L356)



## Verification Methods



- **Bit-exact comparison**: The CPU reference is computed by [`copyRegionToTextureLevel()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L271) which performs `deMemcpy` of source region bytes to destination offsets

- Destination buffer is read back as `VK_FORMAT_R32_UINT` and compared via [`checkTestResult()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L454) from the base class

- Offset tests use direct byte-level comparison against expected data with [`checkZerosAt()`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L311) for untouched bytes



## Test Principles



- Verify that `vkCmdCopyBuffer` copies the exact bytes specified by each region

- Verify that bytes outside the copy region in the destination are not modified

- Verify that multi-region copies with varying offsets and sizes work correctly

- Verify extension command variants (`cmdCopyBuffer2`, `cmdCopyMemoryKHR`) produce identical results

- Verify that transfer-queue submission works correctly for buffer copies



## Notes / Uncertainties



- The `regions` and `unaligned_regions` tests are skipped when `DEVICE_ADDRESS_COMMANDS` is set due to VUID-VkCopyDeviceMemoryInfoKHR-srcRange-13015 ([line 474](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L474))

- Only `addCopyBufferToBufferTests` and `addCopyBufferToBufferOffsetTests` are exported from the header; all other classes/functions are in the anonymous namespace