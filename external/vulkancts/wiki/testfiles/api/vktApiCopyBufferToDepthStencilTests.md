# [vktApiCopyBufferToDepthStencilTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L1)

## Overview

Tests Vulkan copy operations from a buffer to a depth/stencil image. The file validates `vkCmdCopyBufferToImage` and its variants (`vkCmdCopyBufferToImage2`, `vkCmdCopyMemoryToImageIndirectKHR`, `vkCmdCopyMemoryToImageKHR`) when the destination is a depth/stencil format, exercising separate and combined depth/stencil aspect copies with different command ordering.

## Role of File

Implementation-heavy. Contains the `CopyBufferToDepthStencil` test instance with full resource setup, data packing, command recording, and result verification, plus the `CopyBufferToDepthStencilTestCase` with support checks. The `addCopyBufferToDepthStencilTests` registration function iterates formats and offset modes to populate the group.

## Source Code

- Implementation: [vktApiCopyBufferToDepthStencilTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L1)
- Header: [vktApiCopyBufferToDepthStencilTests.hpp](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.hpp#L1)
- Parent registration: [vktApiCopiesAndBlittingTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Registration Path

```
api
  copy_and_blit
    core / dedicated_allocation / copy_commands2 / device_address
      buffer_to_depthstencil
      buffer_to_depthstencil_compute_queue
      buffer_to_depthstencil_transfer_queue
      memory_to_depthstencil_indirect
```

## Test Hierarchy

```
buffer_to_depthstencil (and variants)
  +-- <format>_DS            (depth+stencil, single command, both regions)
  +-- <format>_D_S           (depth then stencil, separate commands)
  +-- <format>_S_D           (stencil then depth, separate commands)
  +-- <format>_SD            (stencil+depth, single command, reversed region order)
  +-- <format>_D             (depth only)
  +-- <format>_S             (stencil only)
  +-- buffer_offset_<format>_DS
  +-- buffer_offset_<format>_D_S
  +-- buffer_offset_<format>_S_D
  +-- buffer_offset_<format>_SD
  +-- buffer_offset_<format>_D
  +-- buffer_offset_<format>_S
```

## Test Families

### CopyBufferToDepthStencil (instance)

Test instance inheriting from `CopiesAndBlittingTestInstanceWithSparseSemaphore` ([line 32](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L32)). Creates a source buffer and destination depth/stencil image, packs depth and stencil data separately into the buffer, issues copy commands, and verifies the result against a software reference.

Key behaviors:
- Separates depth and stencil data into non-interleaved buffer regions before issuing copy commands ([line 323](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L323))
- Supports sparse binding for the destination image ([line 237](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L237))
- Supports four command paths: standard `vkCmdCopyBufferToImage`, `vkCmdCopyBufferToImage2` (COPY_COMMANDS_2), `vkCmdCopyMemoryToImageIndirectKHR` (INDIRECT_COPY), and `vkCmdCopyMemoryToImageKHR` (DEVICE_ADDRESS_COMMANDS) ([line 526](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L526))
- Tests single-command (all regions in one call) and per-region (one region per call with pipeline barriers) modes ([line 528](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L528))

### CopyBufferToDepthStencilTestCase (case)

TestCase subclass ([line 616](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L616)) with `checkSupport` that validates:
- `VK_KHR_format_feature_flags2` extension ([line 635](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L635))
- Queue-specific format features: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `TRANSFER_QUEUE_BIT_KHR` and corresponding stencil bits ([line 653](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L653))
- Indirect copy feature: `indirectMemoryToImageCopy` and `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` ([line 710](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L710))

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Format | `formats::depthAndStencilFormats` (all depth/stencil formats enumerated in the util header) |
| Offset mode | `false` (whole image, bufferOffset=0), `true` (sub-image with bufferOffset=32, rowLength/imageHeight offset) |
| Aspect ordering | `_DS` (depth+stencil single cmd), `_D_S` (depth then stencil separate), `_S_D` (stencil then depth separate), `_SD` (stencil+depth single cmd), `_D` (depth only), `_S` (stencil only) |
| singleCommand | `true` (all regions in one vkCmdCopyBufferToImage), `false` (one region per command with barriers) |
| extensionFlags | From `testGroupParams`: NONE, COPY_COMMANDS_2, INDIRECT_COPY, DEVICE_ADDRESS_COMMANDS |
| allocationKind | From `testGroupParams`: ALLOCATION_KIND_SUBALLOCATION, ALLOCATION_KIND_DEDICATED |
| queueSelection | From `testGroupParams`: Universal, ComputeOnly, TransferOnly |
| useSparseBinding | From `testGroupParams` |

## Support / Feature Requirements

- `VK_KHR_format_feature_flags2` required unconditionally ([line 635](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L635))
- Depth/stencil format must be supported by the physical device ([line 109](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L109))
- Compute queue: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` ([line 660](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L660))
- Transfer queue: `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_TRANSFER_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_TRANSFER_QUEUE_BIT_KHR` ([line 688](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L688))
- Indirect copy: `indirectMemoryToImageCopy` feature and queue support from `VkPhysicalDeviceCopyMemoryIndirectPropertiesKHR` ([line 117](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L117))
- Indirect copy: `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` ([line 724](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L724))
- Sparse binding: `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` | `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and sparse queue availability ([line 239](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L239))

## Verification Methods

- Software reference: `copyRegionToTextureLevel` computes expected result by copying source buffer data to expected image using the same buffer-image copy parameters ([line 53](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L53))
- Result comparison: `checkTestResult` (inherited from base class) compares the GPU result against the software reference
- Uncopied aspects: For combined depth/stencil formats where only one aspect was copied, the uncopied aspect is cleared to 0 in both result and reference before comparison ([line 602](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L602))

## Test Principles Observed

- Aspect separation: Tests that depth and stencil can be copied independently and in different orders
- Command batching: Tests both single-command (all regions) and per-region (barrier-separated) submission patterns
- Extension coverage: Validates standard, copy_commands2, indirect, and device_address command variants
- Queue family coverage: Tests universal, compute-only, and transfer-only queue families
- Sparse resource support: Validates sparse binding for the destination image

## Notes / Uncertainties

- The exact set of formats in `formats::depthAndStencilFormats` is defined in the shared utility header, not in this file; the observed iteration is at [line 805](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L805)
- The `_SD` suffix test uses `singleCommand = true` with stencil region first, depth region second; the `_DS` suffix test uses the same but with depth first, stencil second ([line 846](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L846))
- The `INDIRECT_COPY` and `DEVICE_ADDRESS_COMMANDS` paths are guarded by `#ifndef CTS_USES_VULKANSC` ([line 295](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L295))
