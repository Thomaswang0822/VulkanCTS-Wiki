## Overview

**Core question:** Does the implementation copy depth and stencil aspects out of a depth/stencil image into a host-visible buffer with bytes laid out exactly as each `VkBufferImageCopy` region specifies, across aspect selections and orderings, single-command and per-region batching, queue families, and the `vkCmdCopyImageToBuffer` / `vkCmdCopyImageToBuffer2` command variants?

- Source file: [`vktApiCopyDepthStencilToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L1). Header: [`vktApiCopyDepthStencilToBufferTests.hpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.hpp#L1).
- Test category: `api`. Composite family: `copy_and_blit`. Test families covered by this page: `depthstencil_to_buffer`, `depthstencil_to_buffer_compute_queue`, and `depthstencil_to_buffer_transfer_queue`, all implemented by the same source file. They are registered through the dispatcher in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) under three dispatcher intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`). The implementation entry is [`addCopyDepthStencilToBufferTests()`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L577-L719).
- Test case leaves: per-format aspect-pattern names like `d24_unorm_s8_uint_DS`, `d32_sfloat_s8_uint_D_S`, `s8_uint_S`, `x8_d24_unorm_pack32_D`, plus the `buffer_offset_<format>_<suffix>` family.
- Core test idea: upload known depth and stencil data into a source image, record image-to-buffer copy commands selecting specific aspect masks and orderings, read back the buffer, and compare against a host-computed reference that packs depth and stencil data at tracked offsets.
- The page explains which aspect ordering each leaf exercises, how the host packs and verifies data, what the queue and dispatcher variants change, and what a failure localizes to.

## Background Knowledge

- `vkCmdCopyImageToBuffer` copies image texels into a buffer. Each region is described by a `VkBufferImageCopy` with `bufferOffset`, `bufferRowLength`, `bufferImageHeight`, `imageSubresource` (aspect, mip level, array layer range), `imageOffset`, and `imageExtent`. For depth/stencil images the `aspectMask` selects which aspect is copied.
- `vkCmdCopyImageToBuffer2` (from `VK_KHR_copy_commands2`) takes the same data through `VkBufferImageCopy2KHR` and a `VkCopyImageToBufferInfo2KHR` struct so multiple regions can be passed in one call. The semantics match the original command.
- Combined depth/stencil formats (`VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT`) pack depth and stencil into one image, but the two aspects are copied independently. A region with `aspectMask == VK_IMAGE_ASPECT_DEPTH_BIT` reads only depth; `VK_IMAGE_ASPECT_STENCIL_BIT` reads only stencil. Depth-only formats (`VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`) and the stencil-only format (`VK_FORMAT_S8_UINT`) expose a single aspect.
- `VK_KHR_maintenance10` (with `VK_KHR_format_feature_flags2`) introduces per-queue-family copy-on-queue feature bits: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR`, `VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR`, and the corresponding `..._TRANSFER_QUEUE_BIT_KHR` bits. These advertise whether depth or stencil copies are permitted on compute-only or transfer-only queues.
- Sparse binding (`VK_IMAGE_CREATE_SPARSE_BINDING_BIT` plus `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`) lets an image be backed by multiple memory bindings through `vkQueueBindSparse`. The dispatcher's sparse flag selects this path; a sparse semaphore synchronizes the bind with the copy.
- `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` is the layout the spec requires for the source image of a transfer command. The test transitions the source image to this layout before recording copy commands.

## Registration Hierarchy

```text
api.copy_and_blit.core
├── depthstencil_to_buffer
├── depthstencil_to_buffer_compute_queue
└── depthstencil_to_buffer_transfer_queue
```

The tree shows the three test families under the canonical `core` dispatcher intermediate node because that is the primary, no-extension, Universal-queue configuration. The same three test families are also registered under `api.copy_and_blit.dedicated_allocation` and `api.copy_and_blit.copy_commands2` with different `TestGroupParams` (allocation kind, extension flags, queue selection). The compute and transfer queue variants require `VK_KHR_format_feature_flags2` plus the corresponding maintenance10 per-queue copy feature bits, and are skipped when those features are not advertised.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `s8_uint`, `d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Selects the source image format and determines which aspect combinations are possible. Depth-only formats only generate `_D` leaves; stencil-only only `_S`; combined formats generate all six aspect patterns. `d32_sfloat_s8_uint` exercises the case where depth and stencil texel sizes differ and must be packed separately. | [`vktApiCopyDepthStencilToBufferTests.cpp#L585-L591`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L585-L591) |
| Aspect pattern | `DS`, `D_S`, `SD`, `SD_combined`, `D`, `S` | The primary behavioral axis. Each pattern changes which regions are pushed into the test, the order they appear, and whether `singleCommand` is true or false. | [`vktApiCopyDepthStencilToBufferTests.cpp#L680-L716`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L680-L716) |
| Offset mode | `false` (whole image), `true` (sub-image) | When true, the leaf name is prefixed with `buffer_offset_`, the source sub-region starts at `(quarterSize, quarterSize)`, and the stencil region uses `bufferOffset=32` to exercise non-zero byte offsets. | [`vktApiCopyDepthStencilToBufferTests.cpp#L643-L669`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L643-L669) |
| singleCommand | `true`, `false` | Driven by the aspect pattern. `DS` and `SD_combined` use a single `vkCmdCopyImageToBuffer` call with both regions; `D_S` and `SD` issue one call per region with a pipeline barrier between calls. | [`vktApiCopyDepthStencilToBufferTests.cpp#L366-L385`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L366-L385) |
| extensionFlags | `NONE`, `COPY_COMMANDS_2` | Set by the dispatcher root. `NONE` records `vkCmdCopyImageToBuffer`; `COPY_COMMANDS_2` records `vkCmdCopyImageToBuffer2` through `VkCopyImageToBufferInfo2KHR`. `INDIRECT_COPY` and `DEVICE_ADDRESS_COMMANDS` are not exercised by this source file. | [`vktApiCopyDepthStencilToBufferTests.cpp#L298-L306`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L298-L306) |
| allocationKind | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` | Set by the dispatcher root. Selects suballocated or dedicated allocation for the source image and destination buffer. | [`vktApiCopiesAndBlittingTests.cpp#L232-L246`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L246) |
| queueSelection | `Universal`, `ComputeOnly`, `TransferOnly` | Selects the queue family that records and submits the copy. Compute and transfer selections add `MAINTENANCE_10` and require per-queue copy feature bits. | [`vktApiCopiesAndBlittingTests.cpp#L140-L165`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L140-L165) |
| useSparseBinding | `false` | The constructor has a sparse-binding code path (`VK_IMAGE_CREATE_SPARSE_BINDING_BIT` plus `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, bound through `vkQueueBindSparse` and synchronized with a sparse semaphore), but `addCopyDepthStencilToBufferTests` never propagates `testGroupParams->useSparseBinding` into `TestParams` and no dispatcher call site sets it to `true`, so every registered leaf runs with `useSparseBinding = false`. Sparse image-to-image tests under `copy_and_blit.sparse` use a separate registration function. | [`vktApiCopyDepthStencilToBufferTests.cpp#L137-L166`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L137-L166) |

## Behavior Parameters

The primary behavioral axis is the **aspect selection and ordering** encoded in the test case leaf suffix. Each value below changes which regions are pushed into `params.regions`, the order they appear, and whether the copy is issued as one command or several. The format dimension only restricts which of these values are applicable; it does not introduce a separate behavioral axis.

### `DS`: depth then stencil, single command

Tests a single `vkCmdCopyImageToBuffer` call that copies both depth and stencil aspects of a combined depth/stencil image into the same buffer when the regions are passed together. `params.regions` contains the depth region first and the stencil region second, with `singleCommand = true` ([lines 685-687](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L685-L687)). The host packs depth data at offset 0 and stencil data immediately after; both offsets are computed before the copy command is recorded. Contrasts with `_D_S`, which issues the same regions as separate commands. Only generated for combined depth/stencil formats.

### `D_S`: depth then stencil, separate commands

Tests depth and stencil aspects copied by separate `vkCmdCopyImageToBuffer` calls in depth-then-stencil order, with a pipeline barrier between calls. The region order matches `_DS`, but `singleCommand = false` ([lines 690-691](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L690-L691)). The recording loop issues one `vkCmdCopyImageToBuffer` per region and inserts an image memory barrier between calls so the source image stays in `TRANSFER_SRC_OPTIMAL` layout ([lines 374-383](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L374-L383)). Contrasts with `_SD`, which inverts the region order while keeping separate commands.

### `SD`: stencil then depth, separate commands

Tests depth and stencil aspects copied by separate `vkCmdCopyImageToBuffer` calls in stencil-then-depth order, with a pipeline barrier between calls. `params.regions` is rebuilt with the stencil region first and the depth region second; `singleCommand = false` ([lines 694-697](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L694-L697)). The per-region recording path is the same as `_D_S`; only the region order differs. Contrasts with `_D_S` to verify that region ordering does not affect the final buffer layout when each aspect is copied independently.

### `SD_combined`: stencil then depth, single command

Tests a single `vkCmdCopyImageToBuffer` call that accepts the stencil region before the depth region in the `pRegions` array, and verifies that the buffer layout still matches the order in which the host packed the data. The region order matches `_SD`, but `singleCommand = true` ([lines 700-701](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L700-L701)). Both regions are passed to one `vkCmdCopyImageToBuffer` call. Contrasts with `_DS` to verify that region order inside a single command does not corrupt the per-aspect byte offsets.

### `D`: depth only

Tests a single aspect copy of the depth aspect and verifies the expected packed depth bytes in the destination buffer. `params.regions` contains only the depth region ([lines 706-708](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L706-L708)). For combined depth/stencil formats the stencil aspect is cleared to 0 in both the result and the reference before comparison ([lines 466-470](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L466-L470)). Generated for any format with a depth aspect, including depth-only formats that have no `_S` variant.

### `S`: stencil only

Tests a single aspect copy of the stencil aspect and verifies the expected packed stencil bytes in the destination buffer. `params.regions` contains only the stencil region ([lines 712-715](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L712-L715)). For combined depth/stencil formats the depth aspect is cleared to 0 in both the result and the reference before comparison ([lines 461-465](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L461-L465)). Generated for any format with a stencil aspect, including the stencil-only `VK_FORMAT_S8_UINT` format that has no `_D` variant.

## Shader Analysis

No shader is involved in this test family. The source image is uploaded with known data through `vkCmdCopyBufferToImage` in the host-side `uploadImage` helper, the copy under test is `vkCmdCopyImageToBuffer` (or its `2` variant), and result verification happens entirely on the host. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

[host] The constructor checks that the source format is supported ([lines 112-115](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L112-L115)), creates the source image (regular or sparse-bound depending on `useSparseBinding`), and creates a host-visible destination buffer sized for the depth and stencil packed data of the active aspects ([lines 169-187](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L169-L187)).

[host] `iterate()` generates a `tcu::TextureLevel` with gradient depth/stencil content for the source image, and a second `tcu::TextureLevel` for the destination buffer treated as a 1D texture ([lines 213-225](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L213-L225)). `generateExpectedResult()` runs `copyRegionToTextureLevel` once per region to build a software reference that mirrors the same `VkBufferImageCopy` parameters ([line 230](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L230)).

[host] The host walks the regions in order, packs packed depth-only data and packed stencil-only data into the destination buffer at tracked offsets (`depthOffset`, `stencilOffset`), and computes the per-region `bufferOffset` that the copy command will use ([lines 249-307](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L249-L307)). When `COPY_COMMANDS_2` is set, the regions are converted to `VkBufferImageCopy2KHR`; otherwise they stay as `VkBufferImageCopy`.

[host] `uploadImage` issues `vkCmdCopyBufferToImage` to load the known depth/stencil data into the source image ([line 315](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L315)).

[host] The test acquires a queue, command buffer, and command pool from `activeExecutionCtx()` based on `queueSelection` ([lines 355-358](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L355-L358)), transitions the source image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` ([lines 317-362](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L317-L362)), and records the copy. When `singleCommand` is true, one `vkCmdCopyImageToBuffer` (or `vkCmdCopyImageToBuffer2`) call receives all regions; when false, one call per region is issued with a pipeline barrier between calls so the source image remains in `TRANSFER_SRC_OPTIMAL` layout ([lines 364-426](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L364-L426)).

[host] `submitCommandsAndWaitWithTransferSync` submits the command buffer and waits; the sparse semaphore is included when the source image is sparse-bound ([line 430](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L430)).

[host] `invalidateAlloc` fetches the destination buffer contents. The host reconstructs a combined `tcu::TextureLevel` by copying depth bytes from `depthOffset` into the depth aspect and stencil bytes from `stencilOffset` into the stencil aspect ([lines 437-457](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L437-L457)).

[host] For combined depth/stencil formats where only one aspect was loaded, the uncopied aspect is cleared to 0 in both the result and the reference before comparison ([lines 461-470](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L461-L470)).

[host] `checkTestResult` compares the reconstructed GPU result against the software reference. For depth/stencil formats it uses `tcu::dsThresholdCompare` with a 0.1 tolerance, which compares depth with floating-point tolerance and stencil exactly ([lines 1456-1485](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485)). Any mismatch returns `TestStatus::fail`; otherwise the case passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `_DS` | Combined-region single-command copy or per-aspect byte packing at the depth-then-stencil offsets. |
| `_D_S` | Depth-then-stencil separate-command copy, or pipeline barrier handling between per-region calls. |
| `_SD` | Stencil-then-depth separate-command copy, or pipeline barrier handling between per-region calls. |
| `_SD_combined` | Single-command copy with reversed region order, or per-aspect byte packing when stencil precedes depth. |
| `_D` | Depth aspect copy alone, including depth-only formats and combined formats with stencil cleared. |
| `_S` | Stencil aspect copy alone, including `VK_FORMAT_S8_UINT` and combined formats with depth cleared. |

A shared infrastructure cause affects all six values: incorrect `bufferOffset`, `bufferRowLength`, or `bufferImageHeight` interpretation in any leaf; wrong source image layout transition; wrong sparse binding synchronization; or wrong compute/transfer queue execution when those variants are exercised.

### Cause Analysis

#### Combined-region single-command copy

**Possible failure symptoms:** The `_DS` or `_SD_combined` case fails `dsThresholdCompare` for one or both aspects while the corresponding separate-command case (`_D_S` or `_SD`) passes. The mismatch is localized to the bytes the host expects for the depth or stencil aspect at the tracked offset.

**Possible implementation causes:** The driver or hardware mis-handles a `vkCmdCopyImageToBuffer` call that receives more than one `VkBufferImageCopy` region with different `aspectMask` values. Vulkan requires the implementation to honor each region's `aspectMask` independently when copying from a depth/stencil image; a driver that processes regions as if they shared a single aspect, or that miscalculates the per-region destination offset, would produce this symptom. Source-level investigation of the driver's region-loop handling is needed if the symptom is reproducible only with multiple regions in one call.

#### Separate-command copy and pipeline barrier handling

**Possible failure symptoms:** The `_D_S` or `_SD` case fails while the corresponding single-command case (`_DS` or `_SD_combined`) passes. The mismatch is on the aspect copied in the second command.

**Possible implementation causes:** The pipeline barrier inserted between per-region calls uses `srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT` and `dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT` with `TRANSFER_SRC_OPTIMAL` as both old and new layout ([lines 335-352](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L335-L352)). A driver that does not correctly honor the barrier between back-to-back transfer reads of the same source image, or that re-reads the image before the previous transfer write is complete, would produce this symptom. The symptom can also appear if the implementation loses the source image layout transition that occurs before the first region.

#### Aspect data integrity

**Possible failure symptoms:** A `_D` or `_S` leaf fails `dsThresholdCompare` for the copied aspect. For combined depth/stencil formats the uncopied aspect is cleared to 0 in both result and reference, so the failure is isolated to the aspect that was copied.

**Possible implementation causes:** The implementation writes incorrect bytes for the requested aspect. Vulkan requires that a region with `aspectMask == VK_IMAGE_ASPECT_DEPTH_BIT` reads only the depth component of a combined depth/stencil image and writes packed depth texels into the buffer; the same applies to `VK_IMAGE_ASPECT_STENCIL_BIT`. A driver that copies interleaved depth/stencil bytes instead of packed aspect bytes, or that picks the wrong packed format (for example, treating `D32_SFLOAT_S8_UINT` depth as 64-bit instead of 32-bit), would produce this symptom. The `d32_sfloat_s8_uint` format is the most sensitive because its depth and stencil texel sizes differ and must be packed separately ([lines 169-187](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L169-L187)).

#### Buffer offset and layout handling

**Possible failure symptoms:** Only the `buffer_offset_<format>_<suffix>` leaves fail; the corresponding whole-image leaves pass. The mismatch is in the bytes that the host expects at `bufferOffset=32` for the stencil region, or in the sub-region selected by `imageOffset = (quarterSize, quarterSize)`.

**Possible implementation causes:** The implementation does not honor `bufferOffset`, `bufferRowLength`, or `bufferImageHeight` as Vulkan specifies them. For the offset variant the stencil region uses `bufferOffset = 32`, `bufferRowLength = bufferImageHeight = defaultHalfSize + defaultQuarterSize`, `imageOffset = (defaultQuarterSize, defaultQuarterSize, 0)`, and `imageExtent = defaultHalfExtent` ([lines 634-641](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L634-L641)). A driver that ignores `bufferOffset`, that computes the row pitch from `imageExtent.width` instead of `bufferRowLength`, or that reads the wrong sub-region of the source image would produce this symptom. Source-level investigation is needed to distinguish an offset-handling bug from a sub-region selection bug.

#### Non-universal queue execution

**Possible failure symptoms:** A `depthstencil_to_buffer_compute_queue` or `depthstencil_to_buffer_transfer_queue` leaf fails while the corresponding Universal-queue leaf passes, even though `checkSupport` advertised the required `VK_FORMAT_FEATURE_2_*_COPY_ON_*_QUEUE_BIT_KHR` bit.

**Possible implementation causes:** Vulkan with `VK_KHR_maintenance10` allows depth and stencil copies on compute-only or transfer-only queues only when the corresponding format feature bits are advertised. A driver that reports the feature bit but does not actually perform the copy on the requested queue, or that performs it with different bytes than the same copy on a Universal queue, would produce this symptom. Source-level investigation is needed to confirm whether the implementation routes the copy to the wrong queue family or mishandles the per-queue format feature.

#### Sparse source image binding

**Possible failure symptoms:** A leaf running with `useSparseBinding = true` fails `dsThresholdCompare` while the same leaf with `useSparseBinding = false` passes. The mismatch can affect either aspect.

**Possible implementation causes:** The sparse source image is bound through `vkQueueBindSparse` and a sparse semaphore is signaled before the copy command is submitted ([lines 161-164](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L161-L164), [line 430](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L430)). A driver that does not correctly wait on the sparse semaphore before reading the source image, or that does not fully bind the sparse image before the copy, would produce this symptom. The sparse path is currently routed through the dispatcher's `sparse` root for image-to-image variants; this family does not register sparse leaves directly under `core`, so this cause applies only when a future dispatcher routes sparse binding through this source file.

## Case Pruning

### Requirement-based pruning

- The source depth/stencil format must be supported by the physical device. `checkSupport` throws `NotSupportedError` when `isSupportedDepthStencilFormat` returns false ([lines 112-115](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L112-L115)).
- Non-Universal queue variants require `VK_KHR_format_feature_flags2`. `checkSupport` requires the extension and reads `VkFormatProperties3` to inspect the per-queue copy feature bits ([lines 493-504](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L493-L504)).
- The compute queue variant requires `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` for depth regions and `VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` for stencil regions. If the required bit is missing, the case is skipped with `NotSupportedError` ([lines 511-537](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L511-L537)).
- The transfer queue variant requires the corresponding `..._TRANSFER_QUEUE_BIT_KHR` bits and an available transfer queue. `context.getTransferQueue()` throws `NotSupportedError` if no transfer queue is exposed ([lines 539-566](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L539-L566)).
- The sparse path requires `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` and `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` to be supported for the format, plus a sparse-capable queue. The constructor queries `getPhysicalDeviceImageFormatProperties` with the sparse flags and skips with `NotSupportedError` if the format is not supported ([lines 152-159](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L152-L159)).
- The `COPY_COMMANDS_2` extension flag requires `VK_KHR_copy_commands2`, validated by `checkExtensionSupport` in `checkSupport` ([line 491](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L491)).
- Sparse binding and compute/transfer queue paths are disabled on Vulkan SC builds through `#ifndef CTS_USES_VULKANSC` guards.

### Design-based pruning

- Aspect patterns are generated only for aspects the format exposes. Depth-only formats produce only `_D`; stencil-only produces only `_S`; combined formats produce all six patterns (`_DS`, `_D_S`, `_SD`, `_SD_combined`, `_D`, `_S`) ([lines 680-716](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L680-L716)).
- The offset dimension is fixed at two values: `false` (whole image, `bufferOffset=0` for both aspects) and `true` (sub-image, `bufferOffset=32` for stencil). The depth region always uses `bufferOffset=0` so that the depth-only and stencil-only leaves are directly comparable to the whole-image case ([lines 600-641](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L600-L641)).
- `INDIRECT_COPY` and `DEVICE_ADDRESS_COMMANDS` are not exercised by this source file. The command recording path only branches on `COPY_COMMANDS_2` ([lines 298-306](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L298-L306)).
- The image is always 2D with `defaultExtent` (64×64×1) and a single mip level and array layer. The source tiling is always `VK_IMAGE_TILING_OPTIMAL`.

## Key Takeaways

- This family isolates depth/stencil aspect handling in image-to-buffer copies. A failure on a single-aspect leaf (`_D` or `_S`) points to per-aspect byte integrity; a failure only on combined-aspect leaves points to multi-region command handling.
- `_DS` versus `_SD_combined` and `_D_S` versus `_SD` exist to verify that region order inside a `vkCmdCopyImageToBuffer` call (and across separate calls) does not change the final buffer layout. The host packs data based on the region order it pushed, so a mismatch on only one of these patterns indicates a driver that depends on region order when the spec does not.
- The host packs depth and stencil data into separate byte ranges of the destination buffer and tracks `depthOffset` and `stencilOffset` independently. The implementation must write each aspect's bytes at the `bufferOffset` carried by its region, not at a host-side packed offset.
- The `buffer_offset_` variants are the only leaves that exercise a non-zero `bufferOffset` (32 for stencil) and a sub-region `imageOffset`. They verify that the implementation respects region geometry.
- The compute and transfer queue variants exercise maintenance10 per-queue copy feature advertisement. A pass means the implementation both reports the feature bit and produces correct bytes on that queue.
- See `## Failure Meaning` for the full cause analysis, including which symptoms point to single-command batching, separate-command barriers, aspect integrity, buffer offsets, queue execution, or sparse binding.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CopyDepthStencilToBuffer` class | [`vktApiCopyDepthStencilToBufferTests.cpp#L37-L55`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L37-L55) | Test instance deriving from `CopiesAndBlittingTestInstanceWithSparseSemaphore`. Owns the source image, destination buffer, and software reference path. |
| Constructor (resource setup) | [`vktApiCopyDepthStencilToBufferTests.cpp#L99-L208`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L99-L208) | Creates the source image (regular or sparse), sizes the destination buffer from the active aspects, and binds host-visible memory for readback. |
| `iterate()` (host-side flow) | [`vktApiCopyDepthStencilToBufferTests.cpp#L210-L473`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L210-L473) | Generates source data, packs reference bytes, records the copy command, reads back, reconstructs the result level, and runs `checkTestResult`. |
| `copyRegionToTextureLevel` (software reference) | [`vktApiCopyDepthStencilToBufferTests.cpp#L57-L97`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L57-L97) | Mirrors `VkBufferImageCopy` layout to build the expected buffer bytes, selecting depth or stencil via `tcu::Sampler::MODE_DEPTH` or `MODE_STENCIL`. |
| Per-region data packing | [`vktApiCopyDepthStencilToBufferTests.cpp#L249-L307`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L249-L307) | Walks `params.regions`, packs packed depth-only and stencil-only data, and tracks `depthOffset` / `stencilOffset` for readback. |
| Command recording (NONE vs COPY_COMMANDS_2, single vs per-region) | [`vktApiCopyDepthStencilToBufferTests.cpp#L364-L426`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L364-L426) | Records `vkCmdCopyImageToBuffer` or `vkCmdCopyImageToBuffer2` with the right region count and pipeline barriers between per-region calls. |
| Result readback and aspect clear | [`vktApiCopyDepthStencilToBufferTests.cpp#L439-L470`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L439-L470) | Reads depth and stencil bytes back at tracked offsets and clears uncopied aspects to 0 for combined-format comparisons. |
| `CopyDepthStencilToBufferTestCase::checkSupport` | [`vktApiCopyDepthStencilToBufferTests.cpp#L489-L569`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L489-L569) | Validates extension, format, queue, and per-queue copy feature support before instance creation. |
| `addCopyDepthStencilToBufferTests` (registration) | [`vktApiCopyDepthStencilToBufferTests.cpp#L577-L719`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L577-L719) | Iterates the seven formats and the offset dimension, builds `CopyRegion` and `TestParams` for each aspect pattern, and adds the test case leaves. |
| Format and offset constants | [`vktApiCopyDepthStencilToBufferTests.cpp#L585-L643`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L585-L643) | The seven depth/stencil formats, the `bufferDepthCopy` / `bufferStencilCopy` regions, and the offset variants with `bufferOffset=32` for stencil. |
| Dispatcher entry points | [`vktApiCopiesAndBlittingTests.cpp#L134-L164`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L134-L164) | Three call sites that register `depthstencil_to_buffer`, `depthstencil_to_buffer_compute_queue`, and `depthstencil_to_buffer_transfer_queue` under each dispatcher root. |
| `checkTestResult` (inherited comparison) | [`vktApiCopiesAndBlittingUtil.cpp#L1456-L1485`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1456-L1485) | Runs `tcu::dsThresholdCompare` with 0.1 tolerance for depth/stencil formats and returns pass or fail. |
| `TestGroupParams` and `QueueSelectionOptions` | [`vktApiCopiesAndBlittingUtil.hpp#L244-L344`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L244-L344) | Defines the dispatcher-level parameters (allocation kind, extension flags, queue selection) that flow into each test case. |
| Default geometry constants | [`vktApiCopiesAndBlittingUtil.hpp#L161-L174`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L161-L174) | `defaultSize = 64`, `defaultHalfSize`, `defaultQuarterSize`, and the `defaultExtent` / `defaultHalfExtent` used for source image and sub-region sizes. |
