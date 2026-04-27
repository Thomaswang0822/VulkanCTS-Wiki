# [vktApiFillBufferTests.cpp](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)

## Overview

Tests vkCmdFillBuffer and vkCmdUpdateBuffer commands with various buffer offsets, sizes, allocation strategies, and queue types. Also tests VK_WHOLE_SIZE fill behavior and device address command variants.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function [createFillAndUpdateBufferTests()](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L764).

## Source Code

- Implementation: [vktApiFillBufferTests.cpp](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)
- Header: [vktApiFillBufferTests.hpp](../../../../../modules/vulkan/api/vktApiFillBufferTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L111)

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
  |     +-- update_buffer_vk_whole_size_*_extra_bytes_offset_*
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
  |     +-- update_buffer_vk_whole_size_*_extra_bytes_offset_*
  |     +-- fill_buffer_vk_whole_size_device_address
  |     +-- fill_buffer_second_part_device_address
  |     +-- update_buffer_second_part_device_address
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

[FillBufferTestCase](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L764) tests vkCmdFillBuffer with various offsets and sizes. [FillWholeBufferTestCase](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L177) specifically tests VK_WHOLE_SIZE with different buffer sizes and offsets.

### Update Buffer

[UpdateBufferTestCase](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L764) tests vkCmdUpdateBuffer with the same offset/size parameterization as fill.

### VK_WHOLE_SIZE Tests

[FillWholeBufferTestCase](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L177) tests vkCmdFillBuffer with VK_WHOLE_SIZE, varying the buffer size by adding extra bytes (0-3) and using different offsets. This verifies that VK_WHOLE_SIZE correctly fills from the offset to the end of the buffer.

### Transfer Queue Tests

The `suballocation_transfer_queue` group runs the same tests on a transfer-only queue by creating a custom device with a dedicated transfer queue family, implemented via [createCustomDevice()](../../../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L74).

### Device Address Commands

Some tests use device address commands (VK_KHR_buffer_device_address) instead of regular buffer handles, gated by the `useDeviceAddressCommands` parameter.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Buffer allocator | BufferSuballocation, BufferDedicatedAllocation |
| Queue type | Universal, transfer-only |
| Use device address commands | true, false |
| Fill offset | 0, 4, dstSize/2 |
| Fill size | TEST_DATA_SIZE (256), 4, dstSize/2, VK_WHOLE_SIZE |
| Extra bytes for VK_WHOLE_SIZE | 0, 1, 2, 3 |
| VK_WHOLE_SIZE offset | 0, 4 |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_buffer_device_address | Device address command variants |
| Transfer-only queue | suballocation_transfer_queue group |
| VK_KHR_synchronization2 | Custom device creation for transfer queue |

## Verification Methods

- **Memory comparison**: After fill/update, buffer contents are mapped and compared against expected values
- **VK_CHECK**: API calls are verified for success
- **Byte-level verification**: Fill value is checked at every 4-byte boundary; update data is checked byte-by-byte

## Test Principles Observed

- Offset and size coverage: tests cover whole buffer, first element, second element, and partial buffer
- VK_WHOLE_SIZE edge cases: tests with non-aligned buffer sizes and non-zero offsets
- Queue coverage: transfer-only queue is tested separately
- Allocation strategy coverage: both suballocated and dedicated allocation are tested
- Device address variant: some tests use device address commands for additional coverage

## Notes / Uncertainties

- The factory function is named `createFillAndUpdateBufferTests` but the group name is `fill_and_update_buffer`
- The TEST_DATA_SIZE constant is 256 uint32_t values (1024 bytes)
- Device address command tests are only generated for dedicated allocation and transfer queue groups
- The VK_WHOLE_SIZE tests generate multiple test cases per offset/extra-bytes combination
