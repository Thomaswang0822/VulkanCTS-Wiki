# [vktApiFillBufferTests.cpp](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)

## Overview

Tests Vulkan vkCmdFillBuffer and vkCmdUpdateBuffer commands with various buffer offsets, sizes, allocation strategies, and queue types. Also tests VK_WHOLE_SIZE semantics for vkCmdFillBuffer and the VK_KHR_device_address_commands extension variants (cmdFillMemoryKHR, cmdUpdateMemoryKHR).

## Role of File

Implementation-heavy. Contains all test logic, test instance classes, and the registration function [createFillAndUpdateBufferTests()](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L764).

## Source Code

- Implementation: [vktApiFillBufferTests.cpp](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)
- Header: [vktApiFillBufferTests.hpp](../../modules/vulkan/api/vktApiFillBufferTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L111)

## Registration Path

```
api
  +-- fill_and_update_buffer
```

## Test Hierarchy

```
fill_and_update_buffer
  +-- suballocation
  |     +-- fill_buffer_whole
  |     +-- update_buffer_whole
  |     +-- fill_buffer_first_one
  |     +-- update_buffer_first_one
  |     +-- fill_buffer_second_one
  |     +-- update_buffer_second_one
  |     +-- fill_buffer_second_part
  |     +-- update_buffer_second_part
  |     +-- fill_buffer_vk_whole_size_*_extra_bytes_offset_*
  |     +-- fill_buffer_second_part_device_address
  |     +-- update_buffer_second_part_device_address
  +-- suballocation_transfer_queue
  |     +-- fill_buffer_whole
  |     +-- update_buffer_whole
  |     +-- fill_buffer_first_one
  |     +-- update_buffer_first_one
  |     +-- fill_buffer_second_one
  |     +-- update_buffer_second_one
  |     +-- fill_buffer_second_part
  |     +-- update_buffer_second_part
  |     +-- fill_buffer_vk_whole_size_*_extra_bytes_offset_*
  |     +-- fill_buffer_vk_whole_size_device_address
  +-- dedicated_alloc
        +-- fill_buffer_whole
        +-- update_buffer_whole
        +-- fill_buffer_whole_device_address
        +-- update_buffer_whole_device_address
        +-- fill_buffer_first_one
        +-- update_buffer_first_one
        +-- fill_buffer_second_one
        +-- update_buffer_second_one
        +-- fill_buffer_second_part
        +-- update_buffer_second_part
        +-- fill_buffer_second_part_device_address
        +-- update_buffer_second_part_device_address
        +-- fill_buffer_vk_whole_size_*_extra_bytes_offset_*
```

## Test Families

### Fill Buffer

[FillBufferTestInstance](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L416) tests vkCmdFillBuffer. Creates a destination buffer, fills it with initial data, then uses vkCmdFillBuffer to write a 32-bit value to a specified range. Verifies the result by comparing the buffer contents against an expected texture level. Uses tcu::intThresholdCompare with zero threshold at [line 597](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L597).

### Update Buffer

[UpdateBufferTestInstance](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L650) extends FillBufferTestInstance and tests vkCmdUpdateBuffer. Similar to fill but writes arbitrary data from a testData array instead of a repeating 32-bit value. Generates expected results by memcpy-ing the test data into the expected buffer at the specified offset at [line 735](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L735).

### Fill Whole Buffer (VK_WHOLE_SIZE)

[FillWholeBufferTestInstance](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L177) tests vkCmdFillBuffer with VK_WHOLE_SIZE as the size parameter. Pre-fills the buffer with 0xFF, then fills from dstOffset with VK_WHOLE_SIZE using value 0x01010101. Verifies each byte individually: bytes in the fill range should be 0x01, bytes outside should remain 0xFF at [line 379](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L379). Handles non-4-byte-aligned buffer sizes correctly. Supports synchronization2 for transfer-only queues at [line 263](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L263).

### Device Address Commands (VK_KHR_device_address_commands)

When useDeviceAddressCommands is true, FillBufferTestInstance uses vkCmdFillMemoryKHR instead of vkCmdFillBuffer at [line 550](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L550), and UpdateBufferTestInstance uses vkCmdUpdateMemoryKHR instead of vkCmdUpdateBuffer at [line 705](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L705). These variants set VkAddressCommandFlagsKHR based on offset and size parameters. Only available on non-SC builds.

### Transfer-Only Queue

The suballocation_transfer_queue group creates a custom device with a transfer-only queue family (VK_QUEUE_TRANSFER_BIT without graphics or compute) at [line 90](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L90). Tests verify that fill and update commands work correctly on transfer-only queues.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Buffer allocation strategy | BufferSuballocation, BufferDedicatedAllocation |
| Queue type | Universal, Transfer-only |
| dstSize | 256 (TEST_DATA_SIZE), 256+i for i in 0..3 |
| dstOffset | 0, 4, 128 (dstSize/2), sizeof(uint32_t) |
| size | 4, 128 (dstSize/2), 256 (dstSize), VK_WHOLE_SIZE |
| useDeviceAddressCommands | true, false |
| Fill value | 0x01010101 (for fill), sequential byte pattern (for update) |
| Extra bytes for VK_WHOLE_SIZE | 0, 1, 2, 3 (dstSize % sizeof(uint32_t)) |
| Synchronization2 | Used when transfer-only queue + VK_KHR_synchronization2 supported |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_device_address_commands | fill_buffer_*_device_address, update_buffer_*_device_address |
| VK_KHR_synchronization2 | FillWholeBuffer with transfer-only queue |
| VK_QUEUE_TRANSFER_BIT (without graphics/compute) | suballocation_transfer_queue group |
| Host-visible memory | All tests |
| Buffer device address | Device address command variants (MemoryRequirement::DeviceAddress) |

## Verification Methods

- **Byte-level comparison**: FillWholeBufferTestInstance checks each byte individually against expected values (0x01 in fill range, 0xFF outside) at [line 379](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L379)
- **Texture-level comparison**: FillBufferTestInstance and UpdateBufferTestInstance use tcu::intThresholdCompare with zero threshold at [line 597](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L597)
- **Memory invalidation**: All tests call invalidateAlloc before reading back results
- **Pipeline barriers**: All tests insert appropriate buffer memory barriers (TRANSFER_WRITE to HOST_READ) before reading

## Test Principles Observed

- Boundary testing: tests cover fill/update of the whole buffer, first uint32, second uint32, and second half
- VK_WHOLE_SIZE edge cases: tests buffer sizes that are not multiples of 4 bytes with various offsets
- Queue family coverage: transfer-only queue tests verify operation on non-universal queues
- Allocation strategy coverage: both suballocation and dedicated allocation are tested
- Extension coverage: VK_KHR_device_address_commands variants are tested where available
- Synchronization coverage: both legacy and synchronization2 barrier/submit paths are exercised

## Notes / Uncertainties

- The VK_WHOLE_SIZE tests generate test names like "fill_buffer_vk_whole_size_0_extra_bytes_offset_0" based on the extra bytes (dstSize % sizeof(uint32_t)) and offset values at [line 879](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L879)
- The device_address_commands variants are only added for dedicated_alloc and suballocation groups, not for all groups
- The fill_buffer_vk_whole_size_device_address test is only added for the transfer queue group at [line 892](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L892)
- The testData array in TestParams is 256 uint32_t values (TEST_DATA_SIZE at [line 61](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L61)), initialized with sequential byte values at [line 798](../../modules/vulkan/api/vktApiFillBufferTests.cpp#L798)
