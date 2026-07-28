## Overview

**Core question:** Does the implementation write the expected byte pattern into a destination buffer when `vkCmdFillBuffer`, `vkCmdUpdateBuffer`, and their `VK_KHR_device_address_commands` counterparts target whole, partial, or `VK_WHOLE_SIZE` ranges under different allocation strategies and queue types?

- Source file: [`vktApiFillBufferTests.cpp`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1).
- Test category: `api`. Test family: `fill_and_update_buffer`, registered by [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L787-L926) and added to `api` by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L111).
- Intermediate nodes: `suballocation`, `suballocation_transfer_queue`, `dedicated_alloc`. Each varies the buffer allocator and the queue family.
- Test case leaves: `fill_buffer_*` and `update_buffer_*` variants covering whole-buffer, first-word, second-word, second-half, `VK_WHOLE_SIZE`, and selected `*_device_address` cases.
- Core test idea: pre-fill a destination buffer with a known pattern, record a fill or update command targeting a specific range, submit, read back, and compare bytes against an expected pattern computed on the host.
- The page explains which command each leaf exercises, how the expected bytes are computed, what the `VK_WHOLE_SIZE` alignment rule verifies, and what a failure localizes to.

## Background Knowledge

- `vkCmdFillBuffer` writes a 32-bit fill word repeatedly into a buffer region. The `size` must be a multiple of 4 bytes (or `VK_WHOLE_SIZE`); non-4-byte-aligned trailing bytes are not touched when `VK_WHOLE_SIZE` is used. This alignment rule is central to the `fill_buffer_vk_whole_size_*` leaves.
- `vkCmdUpdateBuffer` copies an arbitrary host-supplied byte sequence into a buffer region. Unlike fill, the written content is not limited to a repeated word.
- `VK_WHOLE_SIZE` as the `size` argument means "from `dstOffset` to the end of the buffer". For `vkCmdFillBuffer`, the effective write range is clamped to a 4-byte-aligned boundary.
- `VK_KHR_device_address_commands` provides `vkCmdFillMemoryKHR` and `vkCmdUpdateMemoryKHR`, which take a `VkDeviceAddressRangeKHR` (base address plus size) and `VkAddressCommandFlagsKHR` instead of a `VkBuffer` handle. The destination buffer must be created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and the allocation must be `MemoryRequirement::DeviceAddress`.
- Suballocation vs dedicated allocation: Vulkan allows one `VkDeviceMemory` object to back multiple buffers (suballocation) or one object per buffer (dedicated allocation). The test exercises both paths because driver memory-binding and tracking behavior can differ.
- Transfer-only queue family: a queue family exposing `VK_QUEUE_TRANSFER_BIT` but not graphics or compute. Compute-only queue family: exposes `VK_QUEUE_COMPUTE_BIT` but not graphics. The test uses a custom device to access a transfer-only queue, and uses the universal compute queue index for the compute-only case.

## Registration Hierarchy

```text
api.fill_and_update_buffer
├── suballocation
├── suballocation_transfer_queue
└── dedicated_alloc
```

The three intermediate nodes are defined in the `testGroupData` array in [`vktApiFillBufferTests.cpp#L801-L808`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808) and iterated by the loop in [`vktApiFillBufferTests.cpp#L811-L922`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L811-L922). Each intermediate node registers the same base set of `fill_buffer_*` and `update_buffer_*` leaves, with device-address variants added selectively.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `suballocation`, `suballocation_transfer_queue`, `dedicated_alloc` | Varies allocation strategy and queue family. | [`vktApiFillBufferTests.cpp#L801-L808`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808) |
| Buffer allocator | `BufferSuballocation`, `BufferDedicatedAllocation` | Backs the destination buffer with suballocated or dedicated memory. | [`vktApiFillBufferTests.cpp#L789-L791`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L789-L791) |
| Queue type | `GRAPHICS_COMPUTE`, `TRANSFER_ONLY`, `COMPUTE_ONLY` | Selects the queue family that records and submits the command. `COMPUTE_ONLY` is used only for the `dedicated_alloc` `fill_buffer_vk_whole_size_device_address` leaf. | [`vktApiFillBufferTests.cpp#L56-L61`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L56-L61), [`vktApiFillBufferTests.cpp#L914-L916`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L914-L916) |
| Device-address commands | `false` (default), `true` (selected leaves) | Switches between `vkCmdFillBuffer`/`vkCmdUpdateBuffer` and `vkCmdFillMemoryKHR`/`vkCmdUpdateMemoryKHR`. | [`vktApiFillBufferTests.cpp#L834-L888`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L888), [`vktApiFillBufferTests.cpp#L909-L919`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L909-L919) |
| Destination offset | `0`, `4`, `dstSize / 2`, `j * sizeof(uint32_t)` for `j = 0..3` | Where in the buffer the write starts. | [`vktApiFillBufferTests.cpp#L824-L907`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L907) |
| Operation size | `dstSize`, `4`, `dstSize / 2`, `VK_WHOLE_SIZE` | How many bytes the command writes. | [`vktApiFillBufferTests.cpp#L824-L919`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L919) |
| `dstSize` for `VK_WHOLE_SIZE` leaves | `TEST_DATA_SIZE + i` for `i = 0..3` (`TEST_DATA_SIZE = 256`) | Varies the trailing-byte count (0 to 3) to exercise alignment handling. | [`vktApiFillBufferTests.cpp#L67`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L67), [`vktApiFillBufferTests.cpp#L893-L907`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L893-L907) |
| Initial destination pattern | `data[b] = (uint8_t)(b % 255)` for explicit-size leaves; `0xff` memset for `VK_WHOLE_SIZE` leaves | Pre-fills the buffer so untouched bytes can be distinguished from written bytes. | [`vktApiFillBufferTests.cpp#L820-L822`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L820-L822), [`vktApiFillBufferTests.cpp#L286`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L286) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Leaves cluster into behavioral groups by (command, range mode, device-address mode). Each intermediate node registers the same set of leaves; the intermediate node only changes allocation and queue configuration.

### `fill_buffer_*`: `vkCmdFillBuffer` with explicit sizes

Tests `vkCmdFillBuffer` with a 32-bit fill word (`testData[0]`) and explicit `dstOffset`/`size`. Variants: `fill_buffer_whole` (offset=0, size=dstSize), `fill_buffer_first_one` (offset=0, size=4), `fill_buffer_second_one` (offset=4, size=4), `fill_buffer_second_part` (offset=dstSize/2, size=dstSize/2). Expected: bytes in `[dstOffset, dstOffset + size)` become `testData[0]` repeated; untouched bytes retain the initial pattern. Registered in [`vktApiFillBufferTests.cpp#L824-L876`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L876); executed by [`FillBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L524-L585).

### `fill_buffer_vk_whole_size_*`: `vkCmdFillBuffer` with `VK_WHOLE_SIZE`

Tests `vkCmdFillBuffer` with `size = VK_WHOLE_SIZE` and a fill word of `0x01010101`. The destination is pre-filled with `0xff` so untouched trailing bytes can be detected. Variants: `fill_buffer_vk_whole_size_<extra>_extra_bytes_offset_<offset>` for `extra` in `{0,1,2,3}` and `offset` in `{0,4,8,12}` (16 leaves per intermediate node). Expected: bytes in `[dstOffset, startOfExtra)` become `0x01`, where `startOfExtra = (dstSize / 4) * 4` is the largest 4-byte-aligned boundary less than or equal to `dstSize`; bytes in `[startOfExtra, dstSize)` remain `0xff`. This group verifies that `VK_WHOLE_SIZE` does not write trailing non-aligned bytes. Registered in [`vktApiFillBufferTests.cpp#L890-L907`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L890-L907); executed by [`FillWholeBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L269-L397).

### `fill_buffer_*_device_address`: `vkCmdFillMemoryKHR` with explicit sizes

Tests `vkCmdFillMemoryKHR` (from `VK_KHR_device_address_commands`) with the same target ranges as the first group but using a `VkDeviceAddressRangeKHR` instead of a `VkBuffer` handle. Variants: `fill_buffer_whole_device_address` (only in `dedicated_alloc`), `fill_buffer_second_part_device_address` (in every intermediate node). Sets `VK_ADDRESS_COMMAND_FULLY_BOUND_BIT_KHR` when `dstOffset != 0` and `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` when `size < VK_WHOLE_SIZE`. Registered in [`vktApiFillBufferTests.cpp#L834-L888`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L888); device-address command recorded in [`vktApiFillBufferTests.cpp#L556-L568`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L556-L568).

### `fill_buffer_vk_whole_size_device_address`: `vkCmdFillMemoryKHR` with `VK_WHOLE_SIZE`

A single leaf per intermediate node that combines `VK_WHOLE_SIZE` with device-address commands. Uses `vkCmdFillMemoryKHR` with `size = VK_WHOLE_SIZE` and a `VkMemoryRangeBarrierKHR` (keyed on the buffer's device address) for the post-write barrier, requiring `synchronization2`. For `dedicated_alloc`, the queue type is switched to `COMPUTE_ONLY` to exercise a non-graphics queue path. Registered in [`vktApiFillBufferTests.cpp#L909-L919`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L909-L919); memory-range barrier built in [`vktApiFillBufferTests.cpp#L323-L343`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L323-L343).

### `update_buffer_*`: `vkCmdUpdateBuffer` with explicit sizes

Tests `vkCmdUpdateBuffer` with host-supplied data (`params.testData`) and explicit `dstOffset`/`size`. Same target ranges as the first group (`buffer_whole`, `buffer_first_one`, `buffer_second_one`, `buffer_second_part`). Expected: bytes in `[dstOffset, dstOffset + size)` are overwritten with the corresponding slice of `testData`; untouched bytes retain the initial pattern. Registered in [`vktApiFillBufferTests.cpp#L824-L876`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L824-L876); executed by [`UpdateBufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L682-L743).

### `update_buffer_*_device_address`: `vkCmdUpdateMemoryKHR` with explicit sizes

Tests `vkCmdUpdateMemoryKHR` with the same target ranges as the update group but using a `VkDeviceAddressRangeKHR`. Variants: `update_buffer_whole_device_address` (only in `dedicated_alloc`), `update_buffer_second_part_device_address` (in every intermediate node). Sets `VK_ADDRESS_COMMAND_FULLY_BOUND_BIT_KHR` plus `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` when `size < TEST_DATA_SIZE`; clears all flags to `0` for the transfer-only queue case. Registered in [`vktApiFillBufferTests.cpp#L834-L888`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L888); device-address command recorded in [`vktApiFillBufferTests.cpp#L714-L727`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L714-L727).

## Shader Analysis

No shader is involved in this test family. All work is recorded by the host via `vkCmdFillBuffer`, `vkCmdUpdateBuffer`, `vkCmdFillMemoryKHR`, or `vkCmdUpdateMemoryKHR`, and validated by host-side byte comparison. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

### Buffer setup

- Destination buffer is created with `VK_BUFFER_USAGE_TRANSFER_DST_BIT` (and `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` when device-address commands are used), backed by either `BufferSuballocation` or `BufferDedicatedAllocation`, and host-visible so the result can be read back without a staging copy. See [`vktApiFillBufferTests.cpp#L255-L266`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L255-L266) and [`vktApiFillBufferTests.cpp#L504-L518`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L504-L518).
- For transfer-only queue cases, a custom device is created by [`createCustomDevice()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L77-L184) that exposes a queue family with `VK_QUEUE_TRANSFER_BIT` but not graphics or compute. See [`vktApiFillBufferTests.cpp#L231-L243`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L231-L243).
- For compute-only queue cases (only the `dedicated_alloc` `fill_buffer_vk_whole_size_device_address` leaf), the universal compute queue family index is used and [`checkSupport()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L408-L418) rejects the case if no exclusive compute queue exists.

### Initial pattern

- For `fill_buffer_*` and `update_buffer_*` (explicit-size leaves), the destination is filled with a pixel pattern: pixel `(x, y, z, 255)` for `x` in `[0, dstSize/4)`, viewed as `VK_FORMAT_R8G8B8A8_UINT`. See [`generateBuffer()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L587-L597).
- For `fill_buffer_vk_whole_size_*`, the destination is filled with `0xff` via `deMemset` so that untouched trailing bytes can be detected. See [`vktApiFillBufferTests.cpp#L286`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L286).

### Command recording and submission

- Host records the fill or update command with `dstOffset`, `size`, and the fill word or data pointer. See [`vktApiFillBufferTests.cpp#L348`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L348) (fill with `VK_WHOLE_SIZE`), [`vktApiFillBufferTests.cpp#L554`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L554) (fill with explicit size), [`vktApiFillBufferTests.cpp#L567`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L567) (`cmdFillMemoryKHR`), [`vktApiFillBufferTests.cpp#L712`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L712) (`cmdUpdateBuffer`), [`vktApiFillBufferTests.cpp#L725`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L725) (`cmdUpdateMemoryKHR`).
- A buffer memory barrier from `TRANSFER_WRITE` to `HOST_READ` is recorded after the command. For `VK_WHOLE_SIZE` device-address cases, `synchronization2` is used and the barrier is a `VkMemoryRangeBarrierKHR` keyed on the buffer's device address. See [`vktApiFillBufferTests.cpp#L289-L344`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L289-L344) and [`vktApiFillBufferTests.cpp#L539-L549`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L539-L549).
- `synchronization2` is used when available and the leaf is on a transfer-only queue or uses device-address commands. See [`vktApiFillBufferTests.cpp#L275-L277`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L275-L277).
- Command buffer is submitted and the host waits on a fence. See [`vktApiFillBufferTests.cpp#L358-L378`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L358-L378) and [`vktApiFillBufferTests.cpp#L575`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L575).

### Result checking

- For `fill_buffer_*` and `update_buffer_*` leaves, the host invalidates the allocation, copies the bytes into a `tcu::TextureLevel`, and compares against an expected `TextureLevel` using `tcu::intThresholdCompare` with a zero threshold. See [`checkTestResult()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L609-L621) and [`vktApiFillBufferTests.cpp#L578-L584`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L578-L584).
- For `fill_buffer_vk_whole_size_*` leaves, the host invalidates the allocation and checks each byte individually: bytes in `[dstOffset, startOfExtra)` must equal `0x01`; all others must equal `0xff`. The first mismatch returns `fail` with the byte index and observed/expected values. See [`vktApiFillBufferTests.cpp#L381-L396`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L381-L396).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fill_buffer_*` (explicit size, non-device-address) | Fill-word replication, range/offset handling, or post-fill barrier visibility. |
| `fill_buffer_vk_whole_size_*` (non-device-address) | `VK_WHOLE_SIZE` alignment handling: writing trailing non-4-byte bytes, or skipping a 4-byte-aligned prefix that should have been written. |
| `fill_buffer_*_device_address` (non-VK_WHOLE_SIZE) | `vkCmdFillMemoryKHR` address-range resolution, address-flag handling, or device-address barrier synchronization. |
| `fill_buffer_vk_whole_size_device_address` | `vkCmdFillMemoryKHR` with `VK_WHOLE_SIZE` address-range sizing, `VkMemoryRangeBarrierKHR` propagation, or compute-only queue execution. |
| `update_buffer_*` (explicit size, non-device-address) | Incorrect host-data copy, partial write, or stale barrier. |
| `update_buffer_*_device_address` | `vkCmdUpdateMemoryKHR` address-range resolution, address-flag handling, or transfer-only queue flag clearing. |
| All leaves under `suballocation_transfer_queue` | Transfer-only queue selection or command execution on a non-graphics, non-compute queue. |
| All leaves under `dedicated_alloc` | Dedicated-allocation memory binding or `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` allocation requirement. |

### Cause Analysis

#### Fill-word replication and range/offset handling

**Possible failure symptoms:** Bytes in `[dstOffset, dstOffset + size)` do not all equal `testData[0]`. The mismatch may appear at the start, end, or as a stripe inside the written range. Bytes outside the written range retain the initial pattern.

**Possible implementation causes:** The driver's `vkCmdFillBuffer` implementation may miscompute the write range from `dstOffset` and `size`, may use the wrong fill word, or may replicate the word with the wrong byte order. Per Vulkan spec, `vkCmdFillBuffer` writes `size` bytes starting at `dstOffset`, replicating the 32-bit `data` word. A driver that interprets `size` as a count of `uint32` values rather than bytes, or that mishandles `dstOffset` alignment, would produce this symptom.

#### VK_WHOLE_SIZE alignment handling

**Possible failure symptoms:** In `fill_buffer_vk_whole_size_<extra>_extra_bytes_offset_<offset>` leaves, bytes in `[dstOffset, startOfExtra)` are not all `0x01`, or bytes in `[startOfExtra, dstSize)` are not `0xff`: trailing 1 to 3 bytes were modified when they should have been left untouched, or the aligned prefix was not fully written.

**Possible implementation causes:** Per Vulkan spec, when `vkCmdFillBuffer` is called with `size = VK_WHOLE_SIZE`, the implementation writes from `dstOffset` toward the end of the buffer, but the written range is clamped to a multiple of 4 bytes. A driver that writes the trailing non-aligned bytes, or that rounds the write range in the wrong direction, would produce this symptom. Confirm by inspecting the driver's clamping logic against `startOfExtra`.

#### vkCmdFillMemoryKHR / vkCmdUpdateMemoryKHR address-range and flag handling

**Possible failure symptoms:** For `fill_buffer_*_device_address` and `update_buffer_*_device_address` leaves, the expected bytes in `[dstOffset, dstOffset + size)` are wrong while the corresponding non-device-address leaf passes. The mismatch implies the device-address command path diverges from the buffer-handle path.

**Possible implementation causes:** `vkCmdFillMemoryKHR` and `vkCmdUpdateMemoryKHR` resolve the target from a `VkDeviceAddressRangeKHR` (base address plus size) and `VkAddressCommandFlagsKHR`. A driver that miscomputes the resolved address (for example, ignores `dstOffset` added to the base address), or that mishandles `VK_ADDRESS_COMMAND_FULLY_BOUND_BIT_KHR` or `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR`, would produce this symptom. Check whether a specific flag combination triggers the divergence.

#### Device-address memory-range barrier propagation

**Possible failure symptoms:** The `fill_buffer_vk_whole_size_device_address` leaf fails: the host reads stale or uninitialized bytes after the fence is signaled, even though the corresponding non-device-address `fill_buffer_vk_whole_size_*` leaf passes. The failure may be intermittent or order-dependent.

**Possible implementation causes:** For device-address cases, the post-write barrier uses `VkMemoryRangeBarrierKHR` keyed on the buffer's device address (queried via `getBufferDeviceAddress`) rather than a `VkBufferMemoryBarrier`. A driver that does not correctly propagate availability/visibility for a memory-range barrier, or that does not include the buffer's address range in the barrier, would produce stale reads. `synchronization2` is mandatory for these leaves. Verify the barrier is recorded with the correct address range.

#### Transfer-only queue execution

**Possible failure symptoms:** All leaves under `suballocation_transfer_queue` fail (or a subset fails), while the corresponding `suballocation` leaves pass. The failure is queue-specific rather than command-specific.

**Possible implementation causes:** The custom device created by [`createCustomDevice()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L77-L184) selects a queue family with `VK_QUEUE_TRANSFER_BIT` but not graphics or compute. A driver that does not support `vkCmdFillBuffer` or `vkCmdUpdateBuffer` on a transfer-only queue, or that misroutes the command to a different queue, would produce this symptom. Vulkan spec requires transfer commands to be supported on any queue with `VK_QUEUE_TRANSFER_BIT`. Determine whether the failure is in queue selection or in command execution on the transfer queue.

#### Dedicated allocation memory binding

**Possible failure symptoms:** All leaves under `dedicated_alloc` fail (or a subset that includes the `*_device_address` variants fails), while the corresponding `suballocation` leaves pass.

**Possible implementation causes:** `BufferDedicatedAllocation` creates a dedicated `VkDeviceMemory` object per buffer. For device-address leaves, the buffer also requires `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and the allocation must be `MemoryRequirement::DeviceAddress`. A driver that does not correctly bind memory for dedicated allocations, or that does not surface a device address for the allocation, would produce this symptom. Pinpoint whether the failure is in allocation, binding, or device-address query.

#### Update buffer data copy

**Possible failure symptoms:** For `update_buffer_*` leaves, the bytes in `[dstOffset, dstOffset + size)` do not match the expected slice of `testData`. The mismatch may be a partial write, a stale previous value, or an off-by-one in the copied range.

**Possible implementation causes:** `vkCmdUpdateBuffer` copies `size` bytes from the host-supplied pointer into the buffer. A driver that truncates the copy, reads from the wrong source offset, or enforces an incorrect alignment on `size` or `dstOffset` would produce this symptom. The CTS leaves here use `size` up to 256 bytes. Confirm the exact failure mode by inspecting the driver's copy path.

## Case Pruning

### Requirement-based pruning

- `*_device_address` variants require `VK_KHR_device_address_commands`. The `fill_buffer_vk_whole_size_device_address` leaf also requires `VK_KHR_synchronization2`. `checkSupport()` throws `NotSupportedError` if the extension is missing. See [`vktApiFillBufferTests.cpp#L410-L414`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L410-L414), [`vktApiFillBufferTests.cpp#L652-L653`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L652-L653), and [`vktApiFillBufferTests.cpp#L769-L770`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L769-L770).
- The `fill_buffer_vk_whole_size_device_address` leaf under `dedicated_alloc` is switched to `COMPUTE_ONLY` queue before registration. `checkSupport()` throws `NotSupportedError` if `context.getComputeQueueFamilyIndex() == -1`. See [`vktApiFillBufferTests.cpp#L416-L417`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L416-L417) and [`vktApiFillBufferTests.cpp#L914-L916`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L914-L916).
- The `suballocation_transfer_queue` intermediate node relies on a transfer-only queue family existing on the device. `findQueueFamilyIndexWithCaps()` in [`createCustomDevice()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L96-L97) throws `NotSupportedError` if no queue family has `VK_QUEUE_TRANSFER_BIT` without graphics or compute.

### Design-based pruning

- `fill_buffer_whole_device_address` and `update_buffer_whole_device_address` are registered only for `dedicated_alloc`. The source comment `// limit number of tests repeated for device_address_commands` documents the intent to avoid repeating every combination under device-address commands. See [`vktApiFillBufferTests.cpp#L834-L846`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L834-L846).
- `fill_buffer_second_part_device_address` and `update_buffer_second_part_device_address` are registered for every intermediate node, providing one shared device-address range case per node without exploding the matrix. See [`vktApiFillBufferTests.cpp#L878-L888`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L878-L888).
- The `VK_WHOLE_SIZE` sweep is limited to `dstSize = 256 + i` for `i = 0..3` and `dstOffset = j * 4` for `j = 0..3`. This covers 0 to 3 trailing bytes and four start offsets, enough to exercise the alignment rule without enumerating every size. See [`vktApiFillBufferTests.cpp#L893-L907`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L893-L907).
- No `update_buffer_vk_whole_size_*` leaves are generated. `vkCmdUpdateBuffer` requires an explicit byte count and a data pointer, so `VK_WHOLE_SIZE` is not a meaningful input for update.

## Key Takeaways

- The family tests four command paths (`vkCmdFillBuffer`, `vkCmdUpdateBuffer`, `vkCmdFillMemoryKHR`, `vkCmdUpdateMemoryKHR`) under three allocation/queue configurations, sharing the same destination-buffer and result-checking infrastructure.
- The `VK_WHOLE_SIZE` sweep verifies the alignment rule: when the buffer size is not a multiple of 4, `vkCmdFillBuffer` with `VK_WHOLE_SIZE` writes only the 4-byte-aligned prefix and leaves the trailing 1 to 3 bytes untouched.
- Device-address coverage is selective by design: one whole-buffer case (dedicated-allocation only) and one second-part case (every intermediate node) per command, plus the `VK_WHOLE_SIZE` device-address case. This bounds runtime while still exercising `VkAddressCommandFlagsKHR` and `VkMemoryRangeBarrierKHR`.
- The `dedicated_alloc` `fill_buffer_vk_whole_size_device_address` leaf is the only one forced onto a compute-only queue, validating that the device-address command path works on a non-graphics queue when an exclusive compute queue is available.
- Failures localize differently: a failure only in `*_device_address` leaves points to the device-address command or memory-range barrier path; a failure only in `suballocation_transfer_queue` points to transfer-only queue support; a failure only in `fill_buffer_vk_whole_size_*` points to `VK_WHOLE_SIZE` alignment handling. See `## Failure Meaning` for details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createFillAndUpdateBufferTests()` registration | [`vktApiFillBufferTests.cpp#L787-L926`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L787-L926) | Owns the test family tree, intermediate-node loop, and leaf registration. |
| `testGroupData` array | [`vktApiFillBufferTests.cpp#L801-L808`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L801-L808) | Defines the three intermediate nodes with their allocator and queue type. |
| `TestParams` struct | [`vktApiFillBufferTests.cpp#L63-L77`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L63-L77) | Carries `dstSize`, `dstOffset`, `size`, `testData`, allocator, queue type, and device-address flag. |
| `FillWholeBufferTestInstance::iterate()` | [`vktApiFillBufferTests.cpp#L269-L397`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L269-L397) | Runs `vkCmdFillBuffer` with `VK_WHOLE_SIZE` and byte-wise verification. |
| `FillBufferTestInstance::iterate()` | [`vktApiFillBufferTests.cpp#L524-L585`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L524-L585) | Runs `vkCmdFillBuffer` (or `vkCmdFillMemoryKHR`) with explicit sizes and texture-level comparison. |
| `UpdateBufferTestInstance::iterate()` | [`vktApiFillBufferTests.cpp#L682-L743`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L682-L743) | Runs `vkCmdUpdateBuffer` (or `vkCmdUpdateMemoryKHR`) with explicit sizes. |
| `FillWholeBufferTestCase::checkSupport()` | [`vktApiFillBufferTests.cpp#L408-L418`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L408-L418) | Gates device-address extension and compute-queue requirements. |
| `createCustomDevice()` | [`vktApiFillBufferTests.cpp#L77-L184`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L77-L184) | Creates a device with a transfer-only queue family for `suballocation_transfer_queue`. |
| Parent registration | [`vktApiTests.cpp#L111`](../../../modules/vulkan/api/vktApiTests.cpp#L111) | Adds `fill_and_update_buffer` to the `api` test category. |
