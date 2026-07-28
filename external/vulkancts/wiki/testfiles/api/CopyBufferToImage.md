## Overview

**Core question:** Does the implementation copy buffer data into a destination image with the exact texels the Vulkan `VkBufferImageCopy` layout specifies, across the three copy command variants, both 1D and 2D image dimensionalities, and the array-layer, buffer-offset, and buffer-stride combinations registered under `buffer_to_image`?

- Source file: [`vktApiCopyBufferToImageTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp). Header: [`vktApiCopyBufferToImageTests.hpp`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.hpp).
- Test category: `api`. Registered group name: `buffer_to_image` (the source file and entry function `addCopyBufferToImageTests()` use the longer `CopyBufferToImage` spelling, but the test tree uses `buffer_to_image`). The group is attached to the `copy_and_blit` dispatcher by [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) and [`addDeviceAddressTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249-L258).
- The same `1d_images` / `2d_images` subgroup structure is registered under eleven `buffer_to_image` variant contexts across four parent groups inside `copy_and_blit`: `core` (4 variants), `dedicated_allocation` (3 variants), `copy_commands2` (3 variants), and `device_address` (1 variant).
- Three Vulkan command variants are exercised: `vkCmdCopyBufferToImage` (default), `vkCmdCopyBufferToImage2` (`VK_KHR_copy_commands2`), and `vkCmdCopyMemoryToImageKHR` (`VK_KHR_copy_memory_indirect` / `DEVICE_ADDRESS_COMMANDS`).
- Verification is a CPU-side reference comparison. The host computes the expected image contents from the source buffer using the same `VkBufferImageCopy` parameters and compares the read-back image with a zero threshold.

## Background Knowledge

- **`VkBufferImageCopy` buffer layout.** A buffer-to-image copy region is described by `VkBufferImageCopy` with `bufferOffset`, `bufferRowLength`, `bufferImageHeight`, `imageSubresource`, `imageOffset`, and `imageExtent`. When `bufferRowLength` is zero, the row length matches `imageExtent.width`; when `bufferImageHeight` is zero, it matches `imageExtent.height`. Non-zero values describe a buffer that is wider or taller than the image subregion, so source texels are picked with explicit strides.
- **`VK_REMAINING_ARRAY_LAYERS`.** `VK_KHR_maintenance5` lets `imageSubresource.layerCount` be `VK_REMAINING_ARRAY_LAYERS`, which the implementation resolves to `arrayLayers - baseArrayLayer`. Copies that start at a non-zero base layer then resolve to a different layer count than copies that start at layer zero.
- **Linear versus optimal tiling.** `VK_IMAGE_TILING_LINEAR` exposes the image as a host-visible row-major layout. `VK_IMAGE_TILING_OPTIMAL` is the implementation-preferred layout. The 96-bit `VK_FORMAT_R32G32B32_SFLOAT` format is tested with both tilings because some implementations do not natively support it; linear tiling can exercise a separate path.
- **Transfer queue granularity.** When a copy is submitted on a transfer-only queue, the queue family's `minImageTransferGranularity` must be at least as fine as the image extent and each region's `imageExtent`. The test gates this in `checkSupport` before registration proceeds.
- **Relaxed buffer offset alignment.** Vulkan only guarantees that `bufferOffset` is a multiple of the texel block size. On a universal queue family, implementations may also accept smaller alignments; the `buffer_offset_relaxed` leaf probes that case and is therefore registered only for the universal queue.

## Registration Hierarchy

```text
api.copy_and_blit.core
├── buffer_to_image
├── buffer_to_image_transfer_queue
├── buffer_to_image_compute_queue
└── buffer_to_image_general_layout
api.copy_and_blit.dedicated_allocation
├── buffer_to_image
├── buffer_to_image_transfer_queue
└── buffer_to_image_compute_queue
api.copy_and_blit.copy_commands2
├── buffer_to_image
├── buffer_to_image_transfer_queue
└── buffer_to_image_compute_queue
api.copy_and_blit.device_address
└── buffer_to_image
```

The registered group name is `buffer_to_image` under every parent context; the source file name `vktApiCopyBufferToImageTests` and the entry function `addCopyBufferToImageTests()` use the longer `CopyBufferToImage` spelling, but the test tree uses `buffer_to_image`. Each `buffer_to_image` variant registers the same `1d_images` / `2d_images` subtree and the same set of test case leaves. The variant suffix identifies what changes: queue family (`_transfer_queue`, `_compute_queue`), destination layout (`_general_layout`), allocation strategy (`dedicated_allocation`), command extension (`copy_commands2`), or device-address command path (`device_address`). The `_general_layout` variant appears only under `core` because the dispatcher gates it on `allocationKind == ALLOCATION_KIND_SUBALLOCATED && extensionFlags == 0`. The `device_address` parent registers only the universal-queue `buffer_to_image` variant. Mustpass evidence starts at [`api.txt#L174321`](../../../mustpass/main/vk-default/api.txt#L174321) for `core.buffer_to_image`; the other ten ranges follow in the same file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Registration context | `core` (universal, transfer_queue, compute_queue, general_layout), `dedicated_allocation` (universal, transfer_queue, compute_queue), `copy_commands2` (universal, transfer_queue, compute_queue), `device_address` (universal only) | Varies queue family, allocation kind, destination image layout, and the copy command variant dispatched. Eleven `buffer_to_image` variant contexts across four parent groups. | [`vktApiCopiesAndBlittingTests.cpp#L132`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L132), [`vktApiCopiesAndBlittingTests.cpp#L175`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L175), [`vktApiCopiesAndBlittingTests.cpp#L187`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L187), [`vktApiCopiesAndBlittingTests.cpp#L228`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L228), [`vktApiCopiesAndBlittingTests.cpp#L255`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L255) |
| Image dimensionality | `1d_images`, `2d_images` | Selects `VK_IMAGE_TYPE_1D` or `VK_IMAGE_TYPE_2D` for the destination image and changes which leaf set is registered. | [`vktApiCopyBufferToImageTests.cpp#L1149-L1150`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1149-L1150) |
| Format (1D) | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32G32B32_SFLOAT` (optimal and linear) | Covers a default 32-bit color format, a uint variant, and a 96-bit format that some implementations do not support natively. | [`vktApiCopyBufferToImageTests.cpp#L370-L375`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L370-L375) |
| Format (2D) | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8_UNORM` (optimal and linear), `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32G32B32_SFLOAT` (optimal and linear), `VK_FORMAT_R64_UINT` | Adds an 8-bit single-channel format and a 64-bit format on top of the 1D format list. | [`vktApiCopyBufferToImageTests.cpp#L637-L646`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L637-L646) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL` (default), `VK_IMAGE_TILING_LINEAR` (for selected formats) | Exercises both image memory layouts; linear tiling is paired with `R8_UNORM` and `R32G32B32_SFLOAT`. | [`vktApiCopyBufferToImageTests.cpp#L370-L375`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L370-L375), [`vktApiCopyBufferToImageTests.cpp#L637-L646`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L637-L646) |
| Array layers | `1` (non-array leaves), `16` (array leaves) | Array leaves copy 16 layers in one command, either one region per layer or one region covering all remaining layers. | [`vktApiCopyBufferToImageTests.cpp#L448`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L448), [`vktApiCopyBufferToImageTests.cpp#L928`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L928) |
| `VK_REMAINING_ARRAY_LAYERS` | `array_all_remaining_layers` (base 0), `array_not_all_remaining_layers` (base 2) | Tests `VK_REMAINING_ARRAY_LAYERS` resolution from two different base layers; requires `VK_KHR_maintenance5`. | [`vktApiCopyBufferToImageTests.cpp#L491-L514`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L491-L514), [`vktApiCopyBufferToImageTests.cpp#L536-L559`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L536-L559) |
| Buffer row/height stride | `0` (tightly packed), `defaultSize + 1` or `defaultHalfSize + 1` (larger) | `0` makes the implementation use the image extent as the stride; non-zero values describe a buffer that is wider or taller than the image subregion. | [`vktApiCopyBufferToImageTests.cpp#L396-L403`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L396-L403), [`vktApiCopyBufferToImageTests.cpp#L429-L436`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L429-L436) |
| Buffer offset | `0` (default), `defaultQuarterSize * pixelSize` (aligned), `defaultQuarterSize + 1` (relaxed) | Tests aligned and relaxed `bufferOffset` values; the relaxed variant is universal-queue only. | [`vktApiCopyBufferToImageTests.cpp#L777-L786`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L777-L786), [`vktApiCopyBufferToImageTests.cpp#L811-L820`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L811-L820) |
| Destination image layout | `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (default), `VK_IMAGE_LAYOUT_GENERAL` (`_general_layout` context only) | The `useGeneralLayout` flag switches the layout passed to the copy command and the pipeline barrier. | [`vktApiCopyBufferToImageTests.cpp#L200-L201`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L200-L201) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED` (core, device_address), `ALLOCATION_KIND_DEDICATED` (dedicated_allocation, copy_commands2) | Changes how the destination image memory is bound. | [`vktApiCopiesAndBlittingTests.cpp#L235`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L235), [`vktApiCopiesAndBlittingTests.cpp#L244`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L244), [`vktApiCopiesAndBlittingTests.cpp#L275-L277`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L275-L277) |
| Command variant | `vkCmdCopyBufferToImage` (default), `vkCmdCopyBufferToImage2` (`COPY_COMMANDS_2`), `vkCmdCopyMemoryToImageKHR` (`DEVICE_ADDRESS_COMMANDS`) | Three dispatch paths selected from `m_params.extensionFlags` inside `iterate()`. | [`vktApiCopyBufferToImageTests.cpp#L203-L256`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L203-L256) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Leaves cluster into behavioral groups by what aspect of `VkBufferImageCopy` they stress. Both image dimensionalities register the same groups where the dimensionality allows; the 1D set is a subset of the 2D set because 1D images have no row stride variation in the same shape.

### Whole-image and tightly-packed copies: `whole`, `whole_unaligned`, `tightly_sized_buffer`

Copy a single region covering the whole image with `bufferOffset = 0` and either zero or non-zero `bufferRowLength` / `bufferImageHeight`. `whole` (2D only) uses tightly packed rows; `whole_unaligned` (2D only) sets both strides larger than the image extent; `tightly_sized_buffer` registers the buffer at the exact byte count of the copied subregion. Registered for every format suffix. Source: [`vktApiCopyBufferToImageTests.cpp#L655-L684`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L655-L684) (`whole`), [`vktApiCopyBufferToImageTests.cpp#L686-L718`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L686-L718) (`whole_unaligned`), [`vktApiCopyBufferToImageTests.cpp#L830-L859`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L830-L859) (2D `tightly_sized_buffer`), [`vktApiCopyBufferToImageTests.cpp#L382-L411`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L382-L411) (1D `tightly_sized_buffer`).

### Larger buffer copies: `larger_buffer`

Copy a single region with `bufferImageHeight` (and for 2D, `bufferRowLength`) larger than the image extent. The buffer is sized to the larger stride so the implementation must read with explicit strides and skip trailing bytes per row. Registered for every format suffix. Source: [`vktApiCopyBufferToImageTests.cpp#L414-L443`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L414-L443) (1D), [`vktApiCopyBufferToImageTests.cpp#L861-L891`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L861-L891) (2D).

### Multi-region copies: `regions` (2D only)

Record one copy command with several `VkBufferImageCopy` regions. Each region copies a shrinking square into a different image subregion at increasing x offsets. For `DEVICE_ADDRESS_COMMANDS`, the per-region `bufferOffset` is incremented so that the device-memory ranges do not overlap, satisfying VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026. Source: [`vktApiCopyBufferToImageTests.cpp#L720-L761`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L720-L761).

### Buffer offset copies: `buffer_offset`, `buffer_offset_relaxed`, `tightly_sized_buffer_offset` (2D only)

Copy a subregion with a non-zero `bufferOffset` and explicit row/image-height strides. `buffer_offset` uses an offset rounded up to the texel block size; `buffer_offset_relaxed` uses an offset that is not a multiple of the texel block size and is registered only for the universal queue; `tightly_sized_buffer_offset` combines a tightly sized buffer with a non-zero offset. Source: [`vktApiCopyBufferToImageTests.cpp#L763-L794`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L763-L794) (`buffer_offset`), [`vktApiCopyBufferToImageTests.cpp#L796-L828`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L796-L828) (`buffer_offset_relaxed`), [`vktApiCopyBufferToImageTests.cpp#L893-L924`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L893-L924) (`tightly_sized_buffer_offset`).

### Per-layer array copies: `array`, `array_tightly_sized_buffer`, `array_larger_buffer`

Copy a 16-layer array image with one `VkBufferImageCopy` region per layer. Each region has a per-layer `bufferOffset` so the source buffer is laid out as 16 concatenated images. `array` (2D only) uses zero row/image-height strides; `array_tightly_sized_buffer` sets both strides to the image extent; `array_larger_buffer` sets `bufferImageHeight` larger than the image height. The 1D variants use `extent.depth` to carry the array layer count. Source: [`vktApiCopyBufferToImageTests.cpp#L446-L487`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L446-L487) (1D `array_tightly_sized_buffer`), [`vktApiCopyBufferToImageTests.cpp#L579-L621`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L579-L621) (1D `array_larger_buffer`), [`vktApiCopyBufferToImageTests.cpp#L926-L966`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L926-L966) (2D `array`), [`vktApiCopyBufferToImageTests.cpp#L968-L1009`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L968-L1009) (2D `array_larger_buffer`), [`vktApiCopyBufferToImageTests.cpp#L1011-L1051`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1011-L1051) (2D `array_tightly_sized_buffer`).

### `VK_REMAINING_ARRAY_LAYERS` copies: `array_all_remaining_layers`, `array_not_all_remaining_layers`

Copy multiple array layers in a single `VkBufferImageCopy` region with `imageSubresource.layerCount = VK_REMAINING_ARRAY_LAYERS`. `array_all_remaining_layers` starts at base layer 0; `array_not_all_remaining_layers` starts at base layer 2. Both add `MAINTENANCE_5` to the extension flags so `checkSupport` gates the `VK_KHR_maintenance5` requirement. Source: [`vktApiCopyBufferToImageTests.cpp#L489-L532`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L489-L532) (1D `array_all_remaining_layers`), [`vktApiCopyBufferToImageTests.cpp#L534-L577`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L534-L577) (1D `array_not_all_remaining_layers`), [`vktApiCopyBufferToImageTests.cpp#L1053-L1096`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1053-L1096) (2D `array_all_remaining_layers`), [`vktApiCopyBufferToImageTests.cpp#L1098-L1141`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1098-L1141) (2D `array_not_all_remaining_layers`).

## Shader Analysis

No shader is involved in this test family. All work is recorded by the host through `vkCmdCopyBufferToImage`, `vkCmdCopyBufferToImage2`, or `vkCmdCopyMemoryToImageKHR`, and the result is validated by host-side reference comparison. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

- The host creates a source `VkBuffer` with `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` (and `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` when `DEVICE_ADDRESS_COMMANDS` is set), backed by host-visible memory (or host-visible plus `DeviceAddress` for device-address cases) so the source data can be uploaded directly. See [`vktApiCopyBufferToImageTests.cpp#L64-L90`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L64-L90).
- The host creates the destination `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, the requested format, tiling, and array layers. When `useSparseBinding` is set the image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and bound through `allocateAndBindSparseImage`; otherwise it is bound through the regular allocator. The dispatcher never sets `useSparseBinding` for buffer-to-image cases, so the sparse path is supported by the class but not exercised by the registered cases. See [`vktApiCopyBufferToImageTests.cpp#L92-L142`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L92-L142).
- The host fills the source buffer with a deterministic pixel pattern via `generateBuffer` and uploads it; the destination image is pre-initialized via `uploadImage` with a different pattern so untouched texels are distinguishable. See [`vktApiCopyBufferToImageTests.cpp#L147-L161`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L147-L161).
- The expected image is computed on the host by `copyRegionToTextureLevel`, which walks the destination extent and reads source texels using `bufferRowLength`, `bufferImageHeight`, `bufferOffset`, and `baseArrayLayer`. See [`vktApiCopyBufferToImageTests.cpp#L323-L355`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L323-L355).
- A command buffer records a pipeline barrier into `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (or `VK_IMAGE_LAYOUT_GENERAL` when `useGeneralLayout` is set), then one of the three copy commands:
  - `vk.cmdCopyBufferToImage` for the default path, [`vktApiCopyBufferToImageTests.cpp#L246-L256`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L246-L256);
  - `vk.cmdCopyBufferToImage2` with a `VkCopyBufferToImageInfo2KHR` for `COPY_COMMANDS_2`, [`vktApiCopyBufferToImageTests.cpp#L229-L245`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L229-L245);
  - `vk.cmdCopyMemoryToImageKHR` with a `VkCopyDeviceMemoryImageInfoKHR` for `DEVICE_ADDRESS_COMMANDS`, after querying the source buffer's device address and computing each region's memory size, [`vktApiCopyBufferToImageTests.cpp#L203-L228`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L203-L228).
- The command buffer is submitted and the host waits. For sparse cases the sparse semaphore is included in the wait; otherwise the standard submit-and-wait path is used. See [`vktApiCopyBufferToImageTests.cpp#L258-L262`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L258-L262).
- The host reads the destination image back via `readImage` and calls `checkTestResult`, which compares the result against the expected texture level with a zero threshold: `tcu::floatThresholdCompare` for floating-point formats and `tcu::intThresholdCompare` for integer formats. See [`vktApiCopyBufferToImageTests.cpp#L264-L266`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L264-L266) and the inherited comparison logic in [`vktApiCopiesAndBlittingUtil.cpp#L1456-L1485`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Source `VkBuffer` | Yes | Yes (transfer source) | Read by the copy command | Yes, for upload | Holds the source texels in the `VkBufferImageCopy` layout. |
| Destination `VkImage` | Yes | Yes (transfer destination) | Written by the copy command | Yes, via `readImage` | Receives the copied texels; compared against the expected texture level. |
| Expected `tcu::TextureLevel` | Yes, on the host | No | No | Yes, as the comparison reference | Host-computed oracle produced by `copyRegionToTextureLevel`. |
| Source buffer device address | Yes, queried when `DEVICE_ADDRESS_COMMANDS` is set | Yes | Read by `vkCmdCopyMemoryToImageKHR` | No | Replaces the `VkBuffer` handle in the device-address command path. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Whole-image and tightly-packed copies (`whole`, `whole_unaligned`, `tightly_sized_buffer`) | Texel layout conversion or buffer-to-image row/height stride handling for the destination format. |
| Larger buffer copies (`larger_buffer`) | Non-zero `bufferRowLength` / `bufferImageHeight` stride computation. |
| Multi-region copies (`regions`, 2D only) | Multi-region dispatch, per-region buffer offset, or image subregion handling; for `DEVICE_ADDRESS_COMMANDS`, region overlap handling per VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026. |
| Buffer offset copies (`buffer_offset`, `buffer_offset_relaxed`, `tightly_sized_buffer_offset`, 2D only) | `bufferOffset` alignment handling, especially relaxed alignment on a non-universal queue. |
| Per-layer array copies (`array`, `array_tightly_sized_buffer`, `array_larger_buffer`) | Per-layer `bufferOffset` computation and layer-count dispatch. |
| `VK_REMAINING_ARRAY_LAYERS` copies (`array_all_remaining_layers`, `array_not_all_remaining_layers`) | `VK_REMAINING_ARRAY_LAYERS` resolution from a non-zero base layer (requires `VK_KHR_maintenance5`). |
| All leaves under `*_transfer_queue` variants (`core`, `dedicated_allocation`, `copy_commands2`) | Transfer-only queue selection, granularity, or command execution. |
| All leaves under `*_compute_queue` variants (`core`, `dedicated_allocation`, `copy_commands2`) | Compute-only queue execution of a transfer command. |
| All leaves under `core.buffer_to_image_general_layout` | `VK_IMAGE_LAYOUT_GENERAL` as the destination layout instead of `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`. |
| All leaves under `dedicated_allocation.*` variants | Dedicated-allocation memory binding for the destination image. |
| All leaves under `copy_commands2.*` variants | `vkCmdCopyBufferToImage2KHR` struct conversion or dispatch. |
| All leaves under `device_address.buffer_to_image` | `vkCmdCopyMemoryToImageKHR` device-address resolution, per-region memory sizing, or device-address allocation requirement. |

### Cause Analysis

#### Texel layout conversion and buffer stride handling

**Possible failure symptoms:** The host-side `checkTestResult` comparison fails for `whole`, `whole_unaligned`, `tightly_sized_buffer`, or `larger_buffer` leaves: one or more texels in the read-back image differ from the expected texture level. The mismatch may appear as a shifted row, a stripe, or a partial copy. See [`vktApiCopyBufferToImageTests.cpp#L323-L355`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L323-L355) for the host reference computation and [`vktApiCopiesAndBlittingUtil.cpp#L1456-L1485`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485) for the comparison.

**Possible implementation causes:** Per Vulkan spec, `vkCmdCopyBufferToImage` reads source texels from the buffer using `bufferOffset`, `bufferRowLength`, and `bufferImageHeight`, and writes them into the image subregion described by `imageSubresource`, `imageOffset`, and `imageExtent`. When `bufferRowLength` or `bufferImageHeight` is zero, the implementation must substitute the corresponding image extent dimension. A driver that miscomputes the source stride, mishandles the zero-to-extent substitution, or performs the wrong texel-size multiplication for the destination format would produce this symptom. The 96-bit `R32G32B32_SFLOAT` format is a likely candidate because its 12-byte texel size is not a power of two. Source-level investigation is needed to pinpoint whether the failure is in stride arithmetic, texel-size lookup, or the linear-to-optimal tiling conversion.

#### Multi-region dispatch and device-address region overlap

**Possible failure symptoms:** The `regions` leaf fails: one or more of the shrinking-square subregions in the destination image does not match the expected texels, while single-region leaves pass. The mismatch may affect only some of the regions in the command.

**Possible implementation causes:** For the default and `COPY_COMMANDS_2` paths, the implementation must dispatch each `VkBufferImageCopy` region independently using its own `bufferOffset`, `imageOffset`, and `imageExtent`. A driver that reuses a single region's parameters for multiple regions, or that miscomputes the per-region buffer stride, would produce this symptom. For the `DEVICE_ADDRESS_COMMANDS` path, the test increments per-region `bufferOffset` so the device-memory ranges do not overlap; the implementation must respect each region's `VkDeviceMemoryImageCopyKHR` address and size separately. Per VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026, overlapping address ranges are invalid; a driver that does not detect or correctly handle non-overlapping ranges would produce this symptom. Source-level investigation is needed to confirm whether the failure is in region iteration or in address-range resolution.

#### Buffer offset alignment handling

**Possible failure symptoms:** The `buffer_offset`, `buffer_offset_relaxed`, or `tightly_sized_buffer_offset` leaf fails: the copied subregion is shifted, truncated, or filled with the wrong texels, while whole-buffer copies with `bufferOffset = 0` pass. The `buffer_offset_relaxed` leaf may fail on a non-universal queue while passing on the universal queue.

**Possible implementation causes:** Per Vulkan spec, `bufferOffset` must be a multiple of the texel block size, except that on a universal queue family the implementation may accept a smaller alignment. A driver that rejects a valid relaxed alignment, rounds `bufferOffset` in the wrong direction, or applies a queue-family-specific alignment rule to the universal queue would produce this symptom. The test gates `buffer_offset_relaxed` to the universal queue specifically because relaxed alignment is only guaranteed there. Source-level investigation is needed to determine whether the failure is in alignment validation or in offset application during the copy.

#### Per-layer array offset computation

**Possible failure symptoms:** Any of `array`, `array_tightly_sized_buffer`, or `array_larger_buffer` fails: texels in one or more array layers are wrong, while non-array leaves with the same format and strides pass. The failure may affect a contiguous range of layers or appear as a stride that grows with layer index.

**Possible implementation causes:** For per-layer copies, the host emits one `VkBufferImageCopy` region per layer with `bufferOffset = pixelSize * rowLength * height * layerIndex`. The implementation must read each region's source texels from the correct offset and write them to the correct `baseArrayLayer`. A driver that miscomputes the per-layer buffer stride, ignores `baseArrayLayer`, or applies a single layer's stride to all regions would produce this symptom. The 1D path uses `extent.depth` to carry the array layer count, so a driver that mishandles the 1D-array extent mapping would also produce this symptom. Source-level investigation is needed to confirm whether the failure is in layer iteration or in extent interpretation.

#### VK_REMAINING_ARRAY_LAYERS resolution

**Possible failure symptoms:** `array_all_remaining_layers` or `array_not_all_remaining_layers` fails: the layers covered by `VK_REMAINING_ARRAY_LAYERS` are not all copied, or the copied range starts at the wrong base layer. `array_not_all_remaining_layers` may fail while `array_all_remaining_layers` passes, indicating a base-layer-dependent resolution bug.

**Possible implementation causes:** Per `VK_KHR_maintenance5`, `VK_REMAINING_ARRAY_LAYERS` resolves to `arrayLayers - baseArrayLayer`. A driver that resolves the value to the full `arrayLayers` count regardless of `baseArrayLayer`, or that does not implement the maintenance5 resolution at all, would produce this symptom. The test sets `MAINTENANCE_5` in `extensionFlags` for these leaves so `checkSupport` gates the extension. Source-level investigation is needed to confirm whether the failure is in the resolution arithmetic or in the extension wiring.

#### Transfer-only queue execution

**Possible failure symptoms:** All leaves under `*_transfer_queue` variants (`core.buffer_to_image_transfer_queue`, `dedicated_allocation.buffer_to_image_transfer_queue`, `copy_commands2.buffer_to_image_transfer_queue`) fail (or a subset fails), while the corresponding universal-queue `buffer_to_image` leaves pass. The failure is queue-specific rather than leaf-specific.

**Possible implementation causes:** The dispatcher passes `QueueSelectionOptions::TransferOnly` for these contexts. `checkSupport` calls `checkTransferQueueGranularity` for the image extent and each region's `imageExtent` before execution. A driver that does not support `vkCmdCopyBufferToImage` on a transfer-only queue, that misroutes the command to a different queue, or that violates the queue family's `minImageTransferGranularity` would produce this symptom. Vulkan spec requires transfer commands to be supported on any queue with `VK_QUEUE_TRANSFER_BIT`. Source-level investigation is needed to determine whether the failure is in queue selection, granularity validation, or command execution on the transfer queue.

#### Compute-only queue execution

**Possible failure symptoms:** All leaves under `*_compute_queue` variants (`core.buffer_to_image_compute_queue`, `dedicated_allocation.buffer_to_image_compute_queue`, `copy_commands2.buffer_to_image_compute_queue`) fail (or a subset fails), while the corresponding universal-queue `buffer_to_image` leaves pass.

**Possible implementation causes:** The dispatcher passes `QueueSelectionOptions::ComputeOnly` for these contexts. Vulkan allows transfer commands on queues exposing `VK_QUEUE_COMPUTE_BIT`. A driver that does not support `vkCmdCopyBufferToImage` on a compute-only queue, or that misroutes the command, would produce this symptom. Source-level investigation is needed to confirm whether the failure is in queue selection or in command execution on the compute queue.

#### General-layout destination

**Possible failure symptoms:** All leaves under `core.buffer_to_image_general_layout` fail (or a subset fails), while the corresponding `core.buffer_to_image` leaves pass. The copy command is recorded with `VK_IMAGE_LAYOUT_GENERAL` instead of `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`.

**Possible implementation causes:** The `useGeneralLayout` flag switches the layout passed to the copy command and the pipeline barrier. Per Vulkan spec, `vkCmdCopyBufferToImage` accepts `VK_IMAGE_LAYOUT_GENERAL` or `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` as the destination layout. A driver that handles the transfer-dst-optimal path but not the general-layout path, or that records the wrong layout in the pipeline barrier, would produce this symptom. Source-level investigation is needed to confirm whether the failure is in layout validation or in barrier recording.

#### Dedicated allocation memory binding

**Possible failure symptoms:** All leaves under `dedicated_allocation.*` variants (`buffer_to_image`, `buffer_to_image_transfer_queue`, `buffer_to_image_compute_queue`) fail (or a subset fails), while the corresponding `core.*` leaves pass.

**Possible implementation causes:** The dispatcher uses `ALLOCATION_KIND_DEDICATED` for this parent context, which creates a dedicated `VkDeviceMemory` object for the destination image. A driver that does not correctly bind memory for dedicated allocations, or that exposes different image format properties under dedicated allocation, would produce this symptom. Source-level investigation is needed to confirm whether the failure is in allocation, binding, or format-property reporting.

#### vkCmdCopyBufferToImage2KHR struct conversion

**Possible failure symptoms:** All leaves under `copy_commands2.*` variants (`buffer_to_image`, `buffer_to_image_transfer_queue`, `buffer_to_image_compute_queue`) fail (or a subset fails), while the corresponding `core.*` leaves pass. The failure is specific to the `COPY_COMMANDS_2` command path.

**Possible implementation causes:** The test converts each `VkBufferImageCopy` to a `VkBufferImageCopy2KHR` and dispatches via `vk.cmdCopyBufferToImage2` with a `VkCopyBufferToImageInfo2KHR`. Per `VK_KHR_copy_commands2`, the two command forms must produce identical results. A driver that mishandles the struct conversion, drops a region, or applies the wrong layout in the `VkCopyBufferToImageInfo2KHR` would produce this symptom. Source-level investigation is needed to confirm whether the failure is in struct conversion or in the driver's `vkCmdCopyBufferToImage2KHR` implementation.

#### vkCmdCopyMemoryToImageKHR device-address resolution

**Possible failure symptoms:** All leaves under `device_address.buffer_to_image` fail (or a subset fails), while the corresponding `core.buffer_to_image` leaves pass. The failure is specific to the `DEVICE_ADDRESS_COMMANDS` command path.

**Possible implementation causes:** The test queries the source buffer's device address, computes each region's memory size from `bufferRowLength`, `bufferImageHeight`, `imageExtent`, and (for `VK_REMAINING_ARRAY_LAYERS`) the resolved layer count, then dispatches via `vk.cmdCopyMemoryToImageKHR` with a `VkCopyDeviceMemoryImageInfoKHR`. Per `VK_KHR_copy_memory_indirect`, the device-address command must produce identical results to the buffer-handle command. A driver that miscomputes the resolved address, mishandles the per-region memory size, or does not correctly translate the `VkDeviceMemoryImageCopyKHR` fields would produce this symptom. The source buffer must also be created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and the allocation must satisfy `MemoryRequirement::DeviceAddress`; a failure in either requirement would surface as a setup error rather than a copy-result mismatch. Source-level investigation is needed to confirm whether the failure is in address resolution, region sizing, or the driver's `vkCmdCopyMemoryToImageKHR` implementation.

## Case Pruning

### Requirement-based pruning

- `COPY_COMMANDS_2` cases require `VK_KHR_copy_commands2`. `DEVICE_ADDRESS_COMMANDS` cases require `VK_KHR_copy_memory_indirect` (and on Vulkan SC are not registered at all). `MAINTENANCE_5` cases require `VK_KHR_maintenance5`. `checkExtensionSupport` throws `NotSupportedError` when an extension is missing. See [`vktApiCopyBufferToImageTests.cpp#L286-L289`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L286-L289).
- The destination image format must support `VK_IMAGE_USAGE_TRANSFER_DST_BIT` for the requested tiling and create flags. `checkSupport` calls `vkGetPhysicalDeviceImageFormatProperties` and throws `NotSupportedError` on `VK_ERROR_FORMAT_NOT_SUPPORTED`. See [`vktApiCopyBufferToImageTests.cpp#L301-L313`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L301-L313).
- The device must report `formatProperties.maxArrayLayers` greater than or equal to the requested array size (16 for array leaves). See [`vktApiCopyBufferToImageTests.cpp#L315-L316`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L315-L316).
- For the `*_transfer_queue` variants (`core`, `dedicated_allocation`, `copy_commands2`), `checkTransferQueueGranularity` validates that the queue family's `minImageTransferGranularity` is at least as fine as the image extent and each region's `imageExtent`. See [`vktApiCopyBufferToImageTests.cpp#L291-L299`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L291-L299).
- The `core.buffer_to_image_general_layout` context is registered only when `allocationKind == ALLOCATION_KIND_SUBALLOCATED && extensionFlags == 0`. See [`vktApiCopiesAndBlittingTests.cpp#L215-L229`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L215-L229).
- The `device_address.buffer_to_image` context is registered only when `CTS_USES_VULKANSC` is not defined. See [`vktApiCopiesAndBlittingTests.cpp#L248-L259`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L248-L259).

### Design-based pruning

- The format list is intentionally restricted to avoid a combinatorial explosion. The 1D set covers a default 32-bit color format, a uint variant, and a 96-bit format that some implementations do not support natively. The 2D set adds an 8-bit single-channel format and a 64-bit format. See the source comments at [`vktApiCopyBufferToImageTests.cpp#L361-L367`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L361-L367) and [`vktApiCopyBufferToImageTests.cpp#L629-L635`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L629-L635).
- The `buffer_offset_relaxed` leaf is registered only for the universal queue because relaxed buffer offset alignment is only guaranteed on a universal queue family. See [`vktApiCopyBufferToImageTests.cpp#L796-L828`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L796-L828).
- For the `regions` leaf under `DEVICE_ADDRESS_COMMANDS`, the per-region `bufferOffset` is incremented so that the device-memory ranges do not overlap, avoiding VUID-VkCopyDeviceMemoryImageInfoKHR-addressRange-13026. The non-device-address paths keep `bufferOffset = 0` for all regions. See [`vktApiCopyBufferToImageTests.cpp#L751-L756`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L751-L756).
- The array leaf count is fixed at 16 layers across all array leaves. Other array depths are not registered.
- The 1D leaves are a subset of the 2D leaves: 1D images have no `whole`, `whole_unaligned`, `regions`, `buffer_offset`, `buffer_offset_relaxed`, or `tightly_sized_buffer_offset` variants because the corresponding 2D-only subregion shapes do not apply to a 1D extent.
- Sparse binding is supported by the `CopyBufferToImage` class through its base `CopiesAndBlittingTestInstanceWithSparseSemaphore`, but the dispatcher never sets `useSparseBinding = true` for buffer-to-image cases. No sparse buffer-to-image cases are registered.

## Key Takeaways

- The family exercises three Vulkan command variants (`vkCmdCopyBufferToImage`, `vkCmdCopyBufferToImage2`, `vkCmdCopyMemoryToImageKHR`) under eleven registration contexts across four parent groups (`core`, `dedicated_allocation`, `copy_commands2`, `device_address`), all sharing the same `1d_images` / `2d_images` leaf set and the same host-side reference comparison.
- The behavioral axis is the test case leaf; leaves cluster into whole-image, larger-buffer, multi-region, buffer-offset, per-layer-array, and `VK_REMAINING_ARRAY_LAYERS` groups. Each group stresses a different field of `VkBufferImageCopy`.
- The 96-bit `R32G32B32_SFLOAT` format and the 64-bit `R64_UINT` format are deliberately included because their non-power-of-two texel sizes can exercise separate driver paths.
- `VK_REMAINING_ARRAY_LAYERS` is tested from both base layer 0 and base layer 2, with `VK_KHR_maintenance5` gated in `checkSupport`.
- Failures localize differently: a failure only under `device_address.buffer_to_image` points to the `vkCmdCopyMemoryToImageKHR` path; a failure only under `copy_commands2.*` variants points to the `vkCmdCopyBufferToImage2KHR` struct conversion; a failure only under `*_transfer_queue` variants points to transfer-only queue support; a failure only on `array_not_all_remaining_layers` points to `VK_REMAINING_ARRAY_LAYERS` resolution from a non-zero base. See `## Failure Meaning` for details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CopyBufferToImage` test instance class | [`vktApiCopyBufferToImageTests.cpp#L35-L53`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L35-L53) | Owns source buffer, destination image, and the `iterate()` entry point. |
| `CopyBufferToImage` constructor | [`vktApiCopyBufferToImageTests.cpp#L55-L143`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L55-L143) | Creates source buffer and destination image; selects sparse or regular allocation path. |
| `iterate()` | [`vktApiCopyBufferToImageTests.cpp#L145-L266`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L145-L266) | Fills buffers, records the copy command variant, submits, reads back, and checks the result. |
| `copyRegionToTextureLevel()` | [`vktApiCopyBufferToImageTests.cpp#L323-L355`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L323-L355) | Host-side reference computation using `bufferRowLength`, `bufferImageHeight`, `bufferOffset`, and `baseArrayLayer`. |
| `CopyBufferToImageTestCase::checkSupport()` | [`vktApiCopyBufferToImageTests.cpp#L286-L317`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L286-L317) | Gates extensions, transfer queue granularity, format support, and `maxArrayLayers`. |
| `add1dBufferToImageTests()` | [`vktApiCopyBufferToImageTests.cpp#L357-L623`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L357-L623) | Registers the 1D leaves across the format list. |
| `add2dBufferToImageTests()` | [`vktApiCopyBufferToImageTests.cpp#L625-L1143`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L625-L1143) | Registers the 2D leaves across the format list. |
| `addCopyBufferToImageTests()` | [`vktApiCopyBufferToImageTests.cpp#L1147-L1151`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1147-L1151) | Public entry point that adds the `1d_images` and `2d_images` subgroups. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L119-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) | Calls `addCopyBufferToImageTests()` from the `core`, `dedicated_allocation`, and `copy_commands2` parent contexts. |
| Device-address registration | [`vktApiCopiesAndBlittingTests.cpp#L249-L258`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249-L258) | Registers the `device_address.buffer_to_image` context (non-VulkanSC only). |
| Top-level dispatcher | [`vktApiCopiesAndBlittingTests.cpp#L267-L293`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L267-L293) | Creates the `core`, `dedicated_allocation`, `copy_commands2`, `sparse`, and `device_address` groups under `copy_and_blit`. |
| Inherited result comparison | [`vktApiCopiesAndBlittingUtil.cpp#L1456-L1485`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485) | `checkTestResult` with zero-threshold float or int comparison. |
| Mustpass evidence | [`api.txt#L174321`](../../../mustpass/main/vk-default/api.txt#L174321) | Primary `core.buffer_to_image` mustpass range; the other ten `buffer_to_image` variant ranges follow in the same file. |
