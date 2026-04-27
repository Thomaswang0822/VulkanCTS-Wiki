# [vktApiCopyDepthStencilToBufferTests.cpp](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L1)

## Overview

Tests Vulkan copy operations from a depth/stencil image to a buffer. The file validates `vkCmdCopyImageToBuffer` and its `vkCmdCopyImageToBuffer2` variant when the source is a depth/stencil format, exercising separate and combined depth/stencil aspect reads with different command ordering.

## Role of File

Implementation-heavy. Contains the `CopyDepthStencilToBuffer` test instance with full resource setup, data packing, command recording, and result verification, plus the `CopyDepthStencilToBufferTestCase` with support checks. The `addCopyDepthStencilToBufferTests` registration function iterates a fixed set of depth/stencil formats and offset modes.

## Source Code

- Implementation: [vktApiCopyDepthStencilToBufferTests.cpp](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L1)
- Header: [vktApiCopyDepthStencilToBufferTests.hpp](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.hpp#L1)
- Parent registration: [vktApiCopiesAndBlittingTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Registration Path

```
api
  copy_and_blit
    core / dedicated_allocation
      depthstencil_to_buffer
      depthstencil_to_buffer_compute_queue
      depthstencil_to_buffer_transfer_queue
```

## Test Hierarchy

```
depthstencil_to_buffer (and variants)
  +-- <format>_DS              (depth+stencil, single command, depth then stencil regions)
  +-- <format>_D_S             (depth then stencil, separate commands)
  +-- <format>_SD              (stencil then depth, separate commands)
  +-- <format>_SD_combined     (stencil+depth, single command, reversed region order)
  +-- <format>_D               (depth only)
  +-- <format>_S               (stencil only)
  +-- buffer_offset_<format>_DS
  +-- buffer_offset_<format>_D_S
  +-- buffer_offset_<format>_SD
  +-- buffer_offset_<format>_SD_combined
  +-- buffer_offset_<format>_D
  +-- buffer_offset_<format>_S
```

## Test Families

### CopyDepthStencilToBuffer (instance)

Test instance inheriting from `CopiesAndBlittingTestInstanceWithSparseSemaphore` ([line 37](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L37)). Creates a source depth/stencil image and destination buffer, uploads known depth/stencil data to the source image, issues copy commands, reads back the buffer, and verifies against a software reference.

Key behaviors:
- Packs depth and stencil data separately into the destination buffer, tracking offsets for each aspect ([line 249](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L249))
- Supports sparse binding for the source image ([line 148](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L148))
- Supports two command paths: standard `vkCmdCopyImageToBuffer` and `vkCmdCopyImageToBuffer2` (COPY_COMMANDS_2) ([line 364](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L364))
- Tests single-command (all regions in one call) and per-region (one region per call with pipeline barriers) modes ([line 366](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L366))
- After copy, reads back depth and stencil data from the buffer using tracked offsets and reconstructs a combined texture level for comparison ([line 439](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L439))

### CopyDepthStencilToBufferTestCase (case)

TestCase subclass ([line 475](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L475)) with `checkSupport` that validates:
- Extension support via `checkExtensionSupport` ([line 491](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L491))
- `VK_KHR_format_feature_flags2` for non-universal queue selections ([line 496](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L496))
- Queue-specific format features: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` and corresponding transfer queue bits ([line 511](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L511))
- Queue availability via `context.getComputeQueue()` / `context.getTransferQueue()` ([line 513](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L513))

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Format | VK_FORMAT_S8_UINT, VK_FORMAT_D16_UNORM, VK_FORMAT_X8_D24_UNORM_PACK32, VK_FORMAT_D32_SFLOAT, VK_FORMAT_D16_UNORM_S8_UINT, VK_FORMAT_D24_UNORM_S8_UINT, VK_FORMAT_D32_SFLOAT_S8_UINT ([line 585](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L585)) |
| Offset mode | `false` (whole image, bufferOffset=0), `true` (sub-image with bufferOffset=32 for stencil, rowLength/imageHeight offset) |
| Aspect ordering | `_DS` (depth+stencil single cmd), `_D_S` (depth then stencil separate), `_SD` (stencil then depth separate), `_SD_combined` (stencil+depth single cmd), `_D` (depth only), `_S` (stencil only) |
| singleCommand | `true` (all regions in one vkCmdCopyImageToBuffer), `false` (one region per command with barriers) |
| extensionFlags | From `testGroupParams`: NONE, COPY_COMMANDS_2 |
| allocationKind | From `testGroupParams`: ALLOCATION_KIND_SUBALLOCATION, ALLOCATION_KIND_DEDICATED |
| queueSelection | From `testGroupParams`: Universal, ComputeOnly, TransferOnly |
| useSparseBinding | From `testGroupParams` |

## Support / Feature Requirements

- Depth/stencil format must be supported by the physical device ([line 112](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L112))
- `VK_KHR_format_feature_flags2` required for non-universal queue selections ([line 496](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L496))
- Compute queue: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` ([line 519](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L519))
- Transfer queue: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_TRANSFER_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_TRANSFER_QUEUE_BIT_KHR` ([line 547](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L547))
- Sparse binding: `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` | `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and sparse queue availability ([line 150](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L150))

## Verification Methods

- Software reference: `copyRegionToTextureLevel` computes expected result by copying source image data to expected buffer using the same buffer-image copy parameters ([line 57](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L57))
- Buffer readback: After copy, depth and stencil data are read from the buffer at their tracked offsets and reconstructed into a combined texture level ([line 439](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L439))
- Result comparison: `checkTestResult` (inherited from base class) compares the reconstructed GPU result against the software reference
- Uncopied aspects: For combined depth/stencil formats where only one aspect was copied, the uncopied aspect is cleared to 0 in both result and reference before comparison ([line 461](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L461))

## Test Principles Observed

- Aspect separation: Tests that depth and stencil can be read independently and in different orders
- Command batching: Tests both single-command and per-region submission patterns
- Extension coverage: Validates standard and copy_commands2 command variants
- Queue family coverage: Tests universal, compute-only, and transfer-only queue families
- Sparse resource support: Validates sparse binding for the source image

## Notes / Uncertainties

- Unlike the buffer-to-depth/stencil file, this file does NOT support INDIRECT_COPY or DEVICE_ADDRESS_COMMANDS extension flags; only NONE and COPY_COMMANDS_2 are exercised in the command recording path ([line 298](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L298))
- The `buffer_offset` variant uses bufferOffset=0 for depth copies but bufferOffset=32 for stencil copies in the offset case ([line 609](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L609))
- The file is wrapped in a header guard `#ifndef _VKTAPICOPYIMAGETOBUFFERTESTS_HPP` which appears to be a copy-paste artifact from a different file; the actual guard should be `_VKTAPICOPYDEPTHSTENCILTOBUFFERTESTS_HPP` as declared in the .hpp file ([line 1](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L1))
