## Overview

**Core question:** does the implementation correctly copy depth and stencil aspects from a packed source buffer into a depth/stencil image, when the aspects are copied separately, together in one command, or in two commands in either order?

This page covers the `buffer_to_depthstencil` test family implemented in [`vktApiCopyBufferToDepthStencilTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L1). The family is registered under the `api.copy_and_blit` composite family and is exercised by four sibling test families under `core` (`buffer_to_depthstencil`, `buffer_to_depthstencil_compute_queue`, `buffer_to_depthstencil_transfer_queue`, `memory_to_depthstencil_indirect`) plus three intermediate-node variants under `dedicated_allocation`, `copy_commands2`, and `device_address`. All variants share one test instance class, `CopyBufferToDepthStencil`.

The family packs source depth and stencil data into a single `VkBuffer` with depth-only bytes followed by stencil-only bytes, then issues `vkCmdCopyBufferToImage` (or an extension variant) with per-region `imageSubresource.aspectMask` selecting depth, stencil, or both in turn. The test verifies that the destination image matches a software-computed reference pixel-for-pixel, with the uncopied aspect cleared to zero for combined depth/stencil formats when only one aspect was loaded.

## Background Knowledge

- **Aspect separation in copy commands.** A combined depth/stencil Vulkan image (for example `VK_FORMAT_D24_UNORM_S8_UINT`) holds two logical aspects in one resource. Each `VkBufferImageCopy` region of `vkCmdCopyBufferToImage` selects exactly one aspect through `imageSubresource.aspectMask`, either `VK_IMAGE_ASPECT_DEPTH_BIT` or `VK_IMAGE_ASPECT_STENCIL_BIT`. The Vulkan spec does not allow a single region to write both aspects of a combined depth/stencil format. This page's tests exercise every meaningful combination of which aspect and in what order.
- **Stencil is always 8 bits per texel.** Regardless of the depth aspect's texel size, the stencil aspect of every combined depth/stencil format is one byte per texel. The source buffer is sized as `depthBytes + stencilBytes`, where `stencilBytes = width * height`. For `VK_FORMAT_D32_SFLOAT_S8_UINT` the depth portion is sized as `sizeof(float)` per texel, not the full 5-byte combined texel; see [vktApiCopyBufferToDepthStencilTests.cpp#L158-L176](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L158-L176).
- **`VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and inter-command barriers.** `vkCmdCopyBufferToImage` requires the destination to be in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (or `VK_IMAGE_LAYOUT_GENERAL` / `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` in restricted cases). The destination image starts in `VK_IMAGE_LAYOUT_UNDEFINED`, is transitioned to `TRANSFER_DST_OPTIMAL` by the inherited `uploadImage` helper while seeding both aspects with a known gradient, and stays in `TRANSFER_DST_OPTIMAL` for the copy commands. When the test issues one copy command per region, it inserts a `VK_PIPELINE_STAGE_TRANSFER_BIT` → `VK_PIPELINE_STAGE_TRANSFER_BIT` pipeline barrier with `TRANSFER_WRITE` → `TRANSFER_WRITE` access masks and `TRANSFER_DST_OPTIMAL` → `TRANSFER_DST_OPTIMAL` layout between consecutive commands.
- **Sibling test families and queue variants.** The same `CopyBufferToDepthStencil` instance is registered four ways under `core`: standard `buffer_to_depthstencil` (universal queue), `buffer_to_depthstencil_compute_queue` (compute-only queue with `VK_KHR_maintenance10`), `buffer_to_depthstencil_transfer_queue` (transfer-only queue with `VK_KHR_maintenance10`), and `memory_to_depthstencil_indirect` (uses `vkCmdCopyMemoryToImageIndirectKHR`, non-VulkanSC only).

## Registration Hierarchy

```text
api.copy_and_blit.core
├── buffer_to_depthstencil
├── buffer_to_depthstencil_compute_queue
├── buffer_to_depthstencil_transfer_queue
└── memory_to_depthstencil_indirect (non-VulkanSC only)
```

The same `buffer_to_depthstencil` family also appears under `dedicated_allocation` (dedicated memory allocation), `copy_commands2` (uses `vkCmdCopyBufferToImage2KHR`), and `device_address` (uses `vkCmdCopyMemoryToImageKHR` with `VkCopyDeviceMemoryImageInfoKHR`, non-VulkanSC only). The `buffer_to_depthstencil_compute_queue` and `buffer_to_depthstencil_transfer_queue` siblings also appear under `copy_commands2`. The canonical `core` tree above is the authoritative root for naming the page's scope; the intermediate-node variants re-run the same case matrix against a different command path or allocation mode.

Evidence:

- `addCopyBufferToDepthStencilTests` at [vktApiCopyBufferToDepthStencilTests.cpp#L742](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L742) is the single registration function for every variant.
- The four siblings under `core` are registered by `addCopiesAndBlittingTests` at [vktApiCopiesAndBlittingTests.cpp#L133](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L133), [vktApiCopiesAndBlittingTests.cpp#L148](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L148), and [vktApiCopiesAndBlittingTests.cpp#L161](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L161); `memory_to_depthstencil_indirect` is registered by `addIndirectCopyTests` at [vktApiCopiesAndBlittingTests.cpp#L88](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L88).
- The `device_address` branch is registered at [vktApiCopiesAndBlittingTests.cpp#L256](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L256) (non-VulkanSC only).
- Mustpass evidence: every `dEQP-VK.api.copy_and_blit.{core,dedicated_allocation,copy_commands2,device_address}.buffer_to_depthstencil.*` and `dEQP-VK.api.copy_and_blit.core.memory_to_depthstencil_indirect.*` leaf appears in `external/vulkancts/mustpass/main/vk-default/api.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Aspect ordering (test name suffix) | `_DS`, `_D_S`, `_S_D`, `_SD`, `_D`, `_S` | Selects which aspect(s) are copied, in what order, and whether one or two commands are used. This is the primary behavioral axis. | [vktApiCopyBufferToDepthStencilTests.cpp#L846-L876](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L846-L876) |
| Format | `formats::depthAndStencilFormats` (D16, D24S8, D32FS8, S8, X8D24, etc.) | Drives depth texel size, buffer sizing, and combined-vs-single aspect pruning. | [vktApiCopyBufferToDepthStencilTests.cpp#L805](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L805) |
| Offset mode | `false` (whole image, `bufferOffset=0`), `true` (sub-image, `bufferOffset=32`, non-zero `bufferRowLength`/`bufferImageHeight`) | Exercises tightly packed versus row-padded source buffer layout and sub-image `imageOffset`. The `true` mode prefixes every test name with `buffer_offset_`. | [vktApiCopyBufferToDepthStencilTests.cpp#L796-L828](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L796-L828) |
| `singleCommand` | `true` (all regions in one `vkCmdCopyBufferToImage`), `false` (one region per command with a transfer-stage barrier between commands) | Switches between the batched-region path and the per-region path. Driven by the suffix: `_DS`/`_SD` use `true`, `_D_S`/`_S_D` use `false`, `_D`/`_S` use `true` with one region. | [vktApiCopyBufferToDepthStencilTests.cpp#L841-L868](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L841-L868) |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `INDIRECT_COPY`, `DEVICE_ADDRESS_COMMANDS` | Selects the recorded command: `vkCmdCopyBufferToImage`, `vkCmdCopyBufferToImage2KHR`, `vkCmdCopyMemoryToImageIndirectKHR`, or `vkCmdCopyMemoryToImageKHR`. Set by the parent dispatcher. | [vktApiCopiesAndBlittingTests.cpp#L119-L230](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` | Suballocated versus dedicated memory for source buffer and destination image. | [vktApiCopiesAndBlittingTests.cpp#L232-L246](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L246) |
| `queueSelection` | `Universal`, `ComputeOnly`, `TransferOnly` | Picks the queue family that records and submits the copy. Compute and transfer queues require `VK_KHR_maintenance10` and corresponding format feature bits. | [vktApiCopiesAndBlittingTests.cpp#L140-L164](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L140-L164) |

## Behavior Parameters

The primary behavioral axis is the test-name suffix, which encodes aspect selection and command batching. Every other dimension above is a configuration axis that re-runs the same six-case matrix against a different command path, queue family, allocation mode, or extension variant.

### `_DS`: both aspects, single command, depth region first

Both depth and stencil regions are issued in one `vkCmdCopyBufferToImage` call, with the depth region first in the `VkBufferImageCopy` array. This exercises the batched-region path where the driver walks multiple aspect regions in a single command. The source buffer holds depth-only bytes at offset 0 and stencil-only bytes at `depthOffset`; each region's `bufferOffset` is rewritten to point at the correct packed bytes by the host re-pack loop at [vktApiCopyBufferToDepthStencilTests.cpp#L329-L370](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L329-L370).

### `_D_S`: depth then stencil, per-region commands with barrier

Two copy commands are issued sequentially: depth first, then stencil. A transfer-stage pipeline barrier is inserted between the two commands to serialize writes to the same destination image. This path is generated when `singleCommand = false` at [vktApiCopyBufferToDepthStencilTests.cpp#L535-L547](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L535-L547). The pair with `_S_D` isolates barrier behavior that depends on aspect order.

### `_S_D`: stencil then depth, per-region commands with barrier

Same as `_D_S` but with stencil copied first and depth second. The region list is rebuilt with stencil first at [vktApiCopyBufferToDepthStencilTests.cpp#L852-L856](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L852-L856) before `singleCommand = false` is applied. A failure that appears here but not in `_D_S` points to ordering-sensitive interaction between depth and stencil writes inside the implementation.

### `_SD`: both aspects, single command, stencil region first

Same batched path as `_DS` but with the stencil region placed first in the `VkBufferImageCopy` array. The pair with `_DS` isolates region-order sensitivity inside the batched single-command path. Generated at [vktApiCopyBufferToDepthStencilTests.cpp#L858-L859](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L858-L859) with `singleCommand = true` and the stencil-first region list from the `_S_D` branch.

### `_D`: depth only

Only the depth aspect is copied, with `singleCommand = true` and one region. For combined depth/stencil formats, the uncopied stencil aspect is cleared to 0 in both the GPU result and the software reference before comparison at [vktApiCopyBufferToDepthStencilTests.cpp#L607-L611](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L607-L611). A nonzero stencil after a `_D` case exposes aspect leakage. For depth-only formats (no stencil component), the case is just the depth-only copy.

### `_S`: stencil only

Only the stencil aspect is copied, with `singleCommand = true` and one region. For combined depth/stencil formats, the uncopied depth aspect is cleared to 0.0 in both the GPU result and the software reference at [vktApiCopyBufferToDepthStencilTests.cpp#L602-L606](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L602-L606). A nonzero depth after an `_S` case exposes aspect leakage. For stencil-only formats (no depth component), the case is just the stencil-only copy.

## Shader Analysis

No shader is involved in this test family. The test records only copy commands and pipeline barriers into a primary command buffer; no pipeline, shader module, or compute pass is created. Failures here cannot be attributed to shader compilation or execution.

## Runtime Execution and Result Checking

Runtime execution proceeds as follows:

1. **Resource setup.** The constructor validates that the depth/stencil format is supported, computes `m_bufferSize` as `depthBytes + stencilBytes` with the stencil byte count fixed at one byte per texel, creates the source `VkBuffer` (with `TRANSFER_SRC` plus `DEVICE_ADDRESS` when an extension requires it), and creates the destination `VkImage` with `OPTIMAL` tiling and `TRANSFER_DST` usage. See [vktApiCopyBufferToDepthStencilTests.cpp#L95-L257](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L95-L257).
2. **Host-side pattern generation.** A 1-D linear gradient fills `m_sourceTextureLevel`; a 2-D gradient fills `m_destinationTextureLevel`. `generateExpectedResult` (inherited from the base class) copies the source regions into the expected image using the per-aspect software reference implementation at [vktApiCopyBufferToDepthStencilTests.cpp#L53-L93](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L53-L93). See [vktApiCopyBufferToDepthStencilTests.cpp#L259-L279](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L259-L279).
3. **Source re-pack.** The host walks the region list in declared order and re-packs source bytes into the source buffer: depth-only bytes first, then stencil-only bytes. `depthOffset` and `stencilOffset` are recorded; each region's `bufferOffset` is rewritten to point at the correct packed bytes. For the indirect and device-address variants, the per-region `VkBufferImageCopy` is converted to `VkCopyMemoryToImageIndirectCommandKHR` or `VkDeviceMemoryImageCopyKHR` and the source buffer's device address is queried. See [vktApiCopyBufferToDepthStencilTests.cpp#L281-L395](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L281-L395).
4. **Image initialization.** `uploadImage` transitions the destination image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and seeds both aspects with the 2-D gradient via separate per-aspect copy commands. See [vktApiCopyBufferToDepthStencilTests.cpp#L401](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L401).
5. **Copy command recording.** A transfer-stage image barrier is inserted first, then one of four command paths is taken based on `extensionFlags` and `singleCommand`:
   - `NONE` + `singleCommand = true`: one `vkCmdCopyBufferToImage` with all regions.
   - `NONE` + `singleCommand = false`: one `vkCmdCopyBufferToImage` per region, with a transfer-stage barrier between consecutive commands.
   - `COPY_COMMANDS_2`: same shape but uses `vkCmdCopyBufferToImage2KHR` and `VkCopyBufferToImageInfo2KHR`.
   - `INDIRECT_COPY` (non-VulkanSC): one or more `vkCmdCopyMemoryToImageIndirectKHR` calls reading `VkCopyMemoryToImageIndirectCommandKHR` records from the indirect buffer.
   - `DEVICE_ADDRESS_COMMANDS` (non-VulkanSC): one or more `vkCmdCopyMemoryToImageKHR` calls using `VkCopyDeviceMemoryImageInfoKHR` and `VkDeviceMemoryImageCopyKHR`.
   See [vktApiCopyBufferToDepthStencilTests.cpp#L421-L591](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L421-L591).
6. **Submission and readback.** `submitCommandsAndWaitWithTransferSync` submits the command buffer. `readImage` reads the destination image back into a host-side `tcu::TextureLevel`. See [vktApiCopyBufferToDepthStencilTests.cpp#L593-L598](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L593-L598).
7. **Uncopied-aspect clearing.** For combined depth/stencil formats where only one aspect was loaded, the other aspect is cleared to 0 in both the GPU result and the software reference. This makes the comparison insensitive to whatever the implementation does to the uncopied aspect, while still detecting writes that leak across aspects. See [vktApiCopyBufferToDepthStencilTests.cpp#L600-L611](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L600-L611).
8. **Pass/fail.** `checkTestResult` (inherited from the base class) compares the GPU result against the software reference pixel-by-pixel. No tolerance is applied. The case passes only if every depth value and every stencil byte matches exactly.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `_DS` (single command, depth region first then stencil) | Single-command batched path mishandles multiple aspect regions in one `vkCmdCopyBufferToImage` call, or packed-buffer offset routing is wrong for the second region in a batched command. |
| `_D_S` (per-command, depth then stencil, with inter-command barrier) | Per-region path mishandles the transfer-stage pipeline barrier between two writes to the same depth/stencil image, or the second command overwrites the first aspect. |
| `_S_D` (per-command, stencil then depth, with inter-command barrier) | Same as `_D_S` but with reversed order, exposing asymmetric aspect ordering dependencies. A failure that only appears here but not in `_D_S` points to ordering-sensitive aspect interaction. |
| `_SD` (single command, stencil region first then depth) | Same batched path as `_DS` but with reversed region order in the command. A failure that only appears here but not in `_DS` points to ordering sensitivity in the batched-command region walker. |
| `_D` (depth only) | Depth-only aspect selection, depth format packing, or `bufferOffset` arithmetic for the depth bytes. For combined D/S formats, the uncopied stencil aspect must be zero in both result and reference; a nonzero stencil after a `_D` case exposes aspect leakage. |
| `_S` (stencil only) | Stencil-only aspect selection, stencil byte packing (always 8-bit per texel), or stencil `bufferOffset` arithmetic. For combined D/S formats, the uncopied depth aspect must be zero in both result and reference; a nonzero depth after an `_S` case exposes aspect leakage. |

Shared infrastructure failure causes that affect every value:

- **Extension-variant dispatch failure**: `COPY_COMMANDS_2`, `INDIRECT_COPY`, or `DEVICE_ADDRESS_COMMANDS` region conversion or command dispatch is wrong.
- **Non-universal queue failure**: missing or incorrectly reported `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `_TRANSFER_QUEUE_` bits, or wrong queue family ownership transfer for the destination image.
- **Source buffer offset arithmetic failure**: wrong `depthOffset`/`stencilOffset` computation, wrong per-region `bufferOffset` rewrite, or wrong indirect-buffer stride for the indirect variant.

### Cause Analysis

#### Single-command batched path (`_DS`, `_SD`)

**Possible failure symptoms:** Both aspects are copied in one `vkCmdCopyBufferToImage` call, but the GPU result mismatches the software reference on the second region in the array. Symptoms are typically confined to the second region's aspect (for `_DS`, stencil mismatches while depth matches; for `_SD`, depth mismatches while stencil matches).

**Possible implementation causes:** A driver that processes only the first region of a batched command, or that overwrites the second region's aspect with the first region's data, would produce this symptom. A wrong `bufferOffset` for the second region (for example, ignoring the per-region `bufferOffset` rewrite done by the host at [vktApiCopyBufferToDepthStencilTests.cpp#L329-L370](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L329-L370) and always reading from offset 0) would also produce it. The contrast between `_DS` and `_SD` localizes the cause: a failure that follows region order (fails on whichever aspect is second) points to a region-walker defect; a failure that follows aspect identity (always fails on stencil, never on depth) points to aspect routing. If the symptom cannot be reproduced against the spec's `vkCmdCopyBufferToImage` region-walking rules, source-level investigation is needed.

#### Per-region path with inter-command barrier (`_D_S`, `_S_D`)

**Possible failure symptoms:** Two single-region `vkCmdCopyBufferToImage` commands are issued with a transfer-stage barrier between them, and the GPU result mismatches the software reference on the second aspect written. Symptoms are usually confined to the second command's aspect.

**Possible implementation causes:** A barrier that does not correctly serialize the two writes (for example, a barrier that does not wait for `TRANSFER_WRITE` to complete before issuing the next `TRANSFER_WRITE`) could let the second command overwrite the first aspect before the first write is observable. A barrier that transitions the layout away from `TRANSFER_DST_OPTIMAL` between commands would also produce a mismatch. The contrast between `_D_S` and `_S_D` localizes the cause: a failure that follows command order points to a barrier or serialization defect; a failure that follows aspect identity points to per-aspect write handling. If the symptom cannot be reproduced against the spec's `VkImageMemoryBarrier` semantics for self-layout transitions, source-level investigation is needed.

#### Single-aspect copy with uncopied-aspect clearing (`_D`, `_S`)

**Possible failure symptoms:** Only one aspect is copied, and either the copied aspect mismatches the software reference, or the uncopied aspect (cleared to 0 in both result and reference before comparison) is nonzero in the GPU result. The first symptom points to a copy defect; the second points to aspect leakage.

**Possible implementation causes:** A wrong `bufferOffset` for the single region (for example, computing depth bytes from the full combined texel size instead of the depth-only texel size) would produce the first symptom. A driver that writes both aspects when only one is selected by `imageSubresource.aspectMask` would produce the second symptom. The stencil-only case is more sensitive to byte-packing arithmetic than the depth-only case, because stencil is always 8 bits per texel regardless of the depth format. If the symptom cannot be reproduced against the spec's aspect-mask rules for `vkCmdCopyBufferToImage`, source-level investigation is needed.

#### Extension-variant dispatch failure

**Possible failure symptoms:** The standard `NONE` path passes, but the `COPY_COMMANDS_2`, `INDIRECT_COPY`, or `DEVICE_ADDRESS_COMMANDS` variant fails on the same case matrix.

**Possible implementation causes:** A wrong region conversion in `convertvkBufferImageCopyTovkBufferImageCopy2KHR`, `convertvkBufferImageCopyTovkMemoryImageCopyKHR`, or `convertvkBufferImageCopyTovkDeviceMemoryImageCopyKHR` would produce the symptom. For the indirect variant, a wrong `indirectBufferAddress` or wrong stride in `VkStridedDeviceAddressRangeKHR` would also produce it. For the device-address variant, a wrong `pHostPointer`/`pMemoryImage` layout in `VkDeviceMemoryImageCopyKHR` would produce it. Source-level investigation is needed if the failure cannot be reproduced against the spec for the corresponding command.

#### Non-universal queue failure

**Possible failure symptoms:** The universal-queue `buffer_to_depthstencil` case passes, but `buffer_to_depthstencil_compute_queue` or `buffer_to_depthstencil_transfer_queue` fails on the same format and suffix.

**Possible implementation causes:** The `VK_KHR_maintenance10` extension exposes `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `_TRANSFER_QUEUE_` bits. A driver that reports the bit but does not actually perform the copy on the requested queue, or that performs the copy with wrong aspect routing on the non-universal queue, would produce the symptom. A wrong queue family ownership transfer for the destination image between the universal-queue `uploadImage` and the compute/transfer-queue copy would also produce it. If the failure cannot be reproduced against the `VK_KHR_maintenance10` spec, source-level investigation is needed.

#### Source buffer offset arithmetic failure

**Possible failure symptoms:** The whole-image (`bufferOffset = 0`) cases pass, but the `buffer_offset_*` cases (with `bufferOffset = 32`, non-zero `bufferRowLength` and `bufferImageHeight`, and a sub-image `imageOffset`) fail. Symptoms can also appear in the indirect variant when the indirect buffer's stride or address arithmetic is wrong.

**Possible implementation causes:** A driver that ignores `bufferRowLength` and `bufferImageHeight` and treats the source as tightly packed would produce the symptom. A driver that mishandles `bufferOffset` for the second region in a batched command would also produce it. For the indirect variant, a wrong stride in `VkStridedDeviceAddressRangeKHR` or a wrong base address for the indirect buffer would produce it. Source-level investigation is needed if the failure cannot be reproduced against the spec's `VkBufferImageCopy` buffer-layout rules.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_format_feature_flags2` is required unconditionally for every case at [vktApiCopyBufferToDepthStencilTests.cpp#L635](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L635).
- The destination depth/stencil format must be supported by the physical device at [vktApiCopyBufferToDepthStencilTests.cpp#L109-L112](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L109-L112); unsupported formats throw `NotSupportedError` and are skipped.
- Compute-queue cases require `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` for the depth aspect and `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` for the stencil aspect at [vktApiCopyBufferToDepthStencilTests.cpp#L660-L678](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L660-L678).
- Transfer-queue cases require the corresponding `_TRANSFER_QUEUE_` bits at [vktApiCopyBufferToDepthStencilTests.cpp#L688-L706](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L688-L706).
- Indirect-copy cases require the `indirectMemoryToImageCopy` feature, queue support reported through `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR`, and `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` at [vktApiCopyBufferToDepthStencilTests.cpp#L114-L155](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L114-L155) and [vktApiCopyBufferToDepthStencilTests.cpp#L710-L732](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L710-L732).
- `INDIRECT_COPY` and `DEVICE_ADDRESS_COMMANDS` paths are guarded by `#ifndef CTS_USES_VULKANSC` at [vktApiCopyBufferToDepthStencilTests.cpp#L295](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L295) and are not registered for VulkanSC builds.

### Design-based pruning

- The `_DS`, `_D_S`, `_S_D`, `_SD` suffixes are only generated when the format has *both* depth and stencil components, at [vktApiCopyBufferToDepthStencilTests.cpp#L839-L860](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L839-L860). Depth-only formats get only `_D`; stencil-only formats get only `_S`.
- The `_D` and `_S` cases are skipped when the format lacks the corresponding component, at [vktApiCopyBufferToDepthStencilTests.cpp#L862-L876](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L862-L876).
- The `_DS` and `_SD` cases both use `singleCommand = true` with two regions in one command; they differ only in region order. The pair is intentionally generated to isolate region-order sensitivity inside the batched path.
- The `_D_S` and `_S_D` cases both use `singleCommand = false` with one region per command; they differ only in command order. The pair is intentionally generated to isolate barrier/serialization sensitivity to aspect order.

## Key Takeaways

- The test family's primary behavioral axis is the test-name suffix: aspect selection (`_D`, `_S`) versus both aspects (`_DS`, `_SD`, `_D_S`, `_S_D`), crossed with command batching (single command for `_DS`/`_SD`, per-region with barrier for `_D_S`/`_S_D`).
- The source buffer is not a packed depth/stencil image. The host re-packs source data into depth-only bytes followed by stencil-only bytes, then rewrites each region's `bufferOffset` to point at the correct packed bytes. Per-region `bufferOffset` arithmetic is therefore part of what is being tested, alongside aspect routing.
- For combined depth/stencil formats where only one aspect is loaded, the test clears the uncopied aspect to 0 in both the GPU result and the software reference before comparison. This isolates aspect leakage as a distinct failure mode.
- The four sibling test families under `core` and the three intermediate-node variants under `dedicated_allocation`, `copy_commands2`, and `device_address` re-run the same six-case matrix against a different command path, queue family, or allocation mode. A failure scoped to one variant points to that variant's command path; a failure across all variants points to the shared buffer layout, image setup, or aspect routing.
- No shader is involved. Failures here cannot be attributed to shader compilation or execution; they must lie in the copy command, the barrier, the queue family handling, or the buffer layout arithmetic.
- See `## Failure Meaning` for the full per-value and shared-infrastructure failure analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test instance class declaration | [vktApiCopyBufferToDepthStencilTests.cpp#L32-L51](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L32-L51) | Owns source buffer, destination image, sparse allocations; declares `iterate` and `copyRegionToTextureLevel` |
| `copyRegionToTextureLevel` (software reference) | [vktApiCopyBufferToDepthStencilTests.cpp#L53-L93](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L53-L93) | Computes expected image; uses `tcu::getEffectiveDepthStencilAccess` to select aspect per region |
| Constructor: format/buffer/image setup | [vktApiCopyBufferToDepthStencilTests.cpp#L95-L257](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L95-L257) | Validates format support, computes `m_bufferSize`, handles indirect-copy feature check and sparse binding |
| `iterate`: host pattern generation and source re-pack | [vktApiCopyBufferToDepthStencilTests.cpp#L259-L395](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L259-L395) | Re-packs source into depth-only then stencil-only bytes; computes `depthOffset` and `stencilOffset`; converts to indirect/2KHR/device-memory forms per extension flag |
| `iterate`: command recording and per-region barriers | [vktApiCopyBufferToDepthStencilTests.cpp#L403-L591](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L403-L591) | Records the transfer-stage image barrier and dispatches to one of four command variants |
| Uncopied-aspect clearing and final check | [vktApiCopyBufferToDepthStencilTests.cpp#L598-L613](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L598-L613) | Clears depth/stencil to 0 in result and reference when only one aspect was loaded, then calls `checkTestResult` |
| `checkSupport`: feature and queue requirements | [vktApiCopyBufferToDepthStencilTests.cpp#L632-L734](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L632-L734) | Validates `VK_KHR_format_feature_flags2`, compute/transfer queue copy bits, indirect copy feature and queue support |
| `addCopyBufferToDepthStencilTests`: registration loop | [vktApiCopyBufferToDepthStencilTests.cpp#L742-L878](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L742-L878) | Generates the six `_DS`/`_D_S`/`_S_D`/`_SD`/`_D`/`_S` leaves for every depth/stencil format and offset mode |
| Header | [vktApiCopyBufferToDepthStencilTests.hpp](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.hpp#L1) | Declares `addCopyBufferToDepthStencilTests` registration entry point |
| Parent dispatcher: `addCopiesAndBlittingTests` | [vktApiCopiesAndBlittingTests.cpp#L119-L230](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) | Routes `buffer_to_depthstencil` and its queue-family siblings under `core`, `dedicated_allocation`, `copy_commands2` |
| Parent dispatcher: `addIndirectCopyTests` | [vktApiCopiesAndBlittingTests.cpp#L74-L117](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74-L117) | Registers `memory_to_depthstencil_indirect` under `core` with `INDIRECT_COPY` (non-VulkanSC) |
| Parent dispatcher: `addDeviceAddressTests` | [vktApiCopiesAndBlittingTests.cpp#L249-L259](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249-L259) | Registers `buffer_to_depthstencil` under `device_address` with `DEVICE_ADDRESS_COMMANDS` (non-VulkanSC) |
| Mustpass evidence | [external/vulkancts/mustpass/main/vk-default/api.txt](../../../mustpass/main/vk-default/api.txt) | Lists every `dEQP-VK.api.copy_and_blit.{core,dedicated_allocation,copy_commands2,device_address}.buffer_to_depthstencil.*` and `dEQP-VK.api.copy_and_blit.core.memory_to_depthstencil_indirect.*` leaf |
