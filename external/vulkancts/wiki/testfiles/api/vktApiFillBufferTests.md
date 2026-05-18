# [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)

## Overview

Tests `vkCmdFillBuffer` and `vkCmdUpdateBuffer` commands with different allocation strategies, offsets, sizes, queue types, `VK_WHOLE_SIZE` behavior, and selected device-address-command variants.

## Role of File

Implementation-heavy test file for the `api.fill_and_update_buffer` subgroup. It contains the test logic, helper classes, and the local registration entry point [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L787).

## Source Code

- Implementation: [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1)
- Header: [vktApiFillBufferTests.hpp](../../../modules/vulkan/api/vktApiFillBufferTests.hpp#L1)
- Parent registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L111)
- Local subgroup registration: [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L787-L926)

## Registration Hierarchy

```text
api.fill_and_update_buffer
├── suballocation
├── suballocation_transfer_queue
└── dedicated_alloc
```

The Level-3 root is the `fill_and_update_buffer` subgroup added directly to `api` by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L111). Its exact direct child groups are `suballocation`, `suballocation_transfer_queue`, and `dedicated_alloc`, registered from the `testGroupData` array and loop in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L795-L923). Deeper generated leaves such as `fill_buffer_whole`, `update_buffer_second_part`, `fill_buffer_vk_whole_size_0_extra_bytes_offset_0`, and the limited device-address variants are intentionally described in prose rather than expanded in the canonical tree.

## Test Families

### suballocation — Suballocated-buffer coverage on a regular queue

The `suballocation` branch is created from the first `testGroupData` entry in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808). It uses [`BufferSuballocation`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L789-L791) with `QueueType::GRAPHICS_COMPUTE` and registers paired fill/update cases for `buffer_whole`, `buffer_first_one`, `buffer_second_one`, and `buffer_second_part` in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L888). It also adds generated `fill_buffer_vk_whole_size_<extra>_extra_bytes_offset_<offset>` cases plus `fill_buffer_vk_whole_size_device_address` through the `VK_WHOLE_SIZE` block in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L890-L920).

### suballocation_transfer_queue — Suballocated-buffer coverage on a transfer-only queue

The `suballocation_transfer_queue` branch comes from the second `testGroupData` entry in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808) and sets `QueueType::TRANSFER_ONLY` when building the same core fill/update case matrix in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L810-L920). Its `VK_WHOLE_SIZE` block also adds the dedicated `fill_buffer_vk_whole_size_device_address` case at [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L909-L919). The transfer-queue device setup is implemented through [`createCustomDevice()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L77-L188).

### dedicated_alloc — Dedicated-allocation coverage with additional device-address variants

The `dedicated_alloc` branch comes from the third `testGroupData` entry in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808) and switches the allocator to [`BufferDedicatedAllocation`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L789-L791). It registers the same base fill/update matrix as the other groups in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L888), adds `fill_buffer_whole_device_address` and `update_buffer_whole_device_address` when `useDedicatedAllocation` is true at [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L846), and adds `fill_buffer_second_part_device_address` plus `update_buffer_second_part_device_address` via the shared second-part device-address block in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L878-L888). Its `VK_WHOLE_SIZE` block also adds `fill_buffer_vk_whole_size_device_address`; for this dedicated-allocation branch the case is switched to `QueueType::COMPUTE_ONLY` before registration in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L909-L919).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered direct child groups | `suballocation`, `suballocation_transfer_queue`, `dedicated_alloc` from `testGroupData` in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L795-L808) |
| Buffer allocator | [`BufferSuballocation`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L789-L790) and [`BufferDedicatedAllocation`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L791) |
| Queue mode | `QueueType::GRAPHICS_COMPUTE`, `QueueType::TRANSFER_ONLY`, and `QueueType::COMPUTE_ONLY`; the first two come from `testGroupData`, while `COMPUTE_ONLY` is used for the dedicated-allocation device-address `VK_WHOLE_SIZE` case in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L819) and [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L914-L916) |
| Device-address-command mode | `useDeviceAddressCommands = false` by default, with selected `true` cases added in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L846), [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L878-L888), and [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L909-L919) |
| Destination offset | `0`, `4`, `dstSize / 2`, and `j * sizeof(uint32_t)` for `j = 0..3` in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L888) and [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L890-L907) |
| Operation size | `dstSize`, `4`, `dstSize / 2`, and `VK_WHOLE_SIZE` in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L888) and [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L890-L919) |
| `VK_WHOLE_SIZE` destination size variants | `TestParams::TEST_DATA_SIZE + i` for `i = 0..3` in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L893-L907) |
| Initial data pattern | `data[b] = (uint8_t)(b % 255)` across the destination contents in [vktApiFillBufferTests.cpp](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L820-L822) |

## Support / Feature Requirements

- Device-address-command variants require [`requireDeviceFunctionality("VK_KHR_device_address_commands")`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L769-L770) in [`UpdateBufferTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L767-L774).
- The transfer-only-queue branch relies on the custom-device path implemented by [`createCustomDevice()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L77-L188), which is used when `QueueType::TRANSFER_ONLY` is selected.
- Compute-only `VK_WHOLE_SIZE` device-address coverage requires an exclusive compute queue; [`checkSupport()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L772-L773) rejects the case when `context.getComputeQueueFamilyIndex() == -1`.
- The command-recording path uses synchronization2 when available for transfer-only queue or device-address-command cases, as selected in [`FillWholeBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L271-L274).

## Verification Methods

- Buffer results are read back after command submission by invalidating the allocation and copying the mapped contents into a texture level in [`UpdateBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L693-L711).
- Update-buffer expected contents are constructed by copying the original destination image and then overwriting the target range with `deMemcpy()` in [`UpdateBufferTestInstance::generateExpectedResult()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L714-L725).
- The final comparison is performed through [`checkTestResult()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L711), after the command buffer records the transfer operation and a transfer-to-host barrier in [`UpdateBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L685-L691).

## Test Principles Observed

- The file builds a shared fill/update matrix across three direct child groups that vary allocation mode and queue availability.
- It covers whole-buffer, first-word, second-word, and second-half writes, then adds a generated `VK_WHOLE_SIZE` sweep over extra trailing bytes and start offsets.
- Device-address-command coverage is intentionally selective rather than exhaustive: dedicated allocation adds whole-buffer variants; every group adds second-part device-address variants and a `VK_WHOLE_SIZE` device-address variant, with the dedicated-allocation `VK_WHOLE_SIZE` case forced onto a compute-only queue when available.
- The test design checks ordinary, transfer-only, and selected compute-only queue paths under the same registration root.

## Notes / Uncertainties

- The factory symbol [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L787) registers the displayed subgroup name `fill_and_update_buffer`, so the symbol name and path component are not identical.
- The legacy wiki page previously listed `update_buffer_vk_whole_size_*_extra_bytes_offset_*` leaves, but the current inspected registration loop adds only `fill_buffer_vk_whole_size_<extra>_extra_bytes_offset_<offset>` cases in [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L890-L907).
- The `fill_buffer_second_part_device_address` and `update_buffer_second_part_device_address` variants are created inside the shared group-building loop for every direct child group, while the `fill_buffer_whole_device_address` and `update_buffer_whole_device_address` variants remain dedicated-allocation-only.
