# vktApiCopiesAndBlittingDynamicStateMetaOpsTests ([source](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp))

## Overview

Tests that verify the correctness of copy and blit meta-operations when interleaved with graphics draws that use dynamic rasterization sample counts (VK_EXT_extended_dynamic_state3). The file exercises the scenario where a multisampled image is drawn to, then a copy or blit operation is performed on separate source/destination images, then the multisampled image is drawn to again -- all within a single command buffer. This verifies that the meta-operations (copy/blit) do not corrupt the dynamic state or the multisampled image's contents.

## Role of File

This file provides the test implementation and registration for dynamic state meta-operation tests in the Vulkan CTS `api` test group. It contains one test instance class, one test case class, and one registration function. The file is conditionally compiled out for Vulkan SC builds (guarded by `CTS_USES_VULKANSC`).

## Source Code

- Implementation: [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp)
- Header: [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp)

## Registration Path

```
api > copy_and_blit > dynamic_state
```

The top-level registration function `createDynamicStateMetaOperationsTests` at [line 1402](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1402) creates the `dynamic_state` group. This is registered directly under `copy_and_blit` in [vktApiCopiesAndBlittingTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) at [line 286](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L286).

## Test Hierarchy

```
dynamic_state
|-- copy
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_2
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_4
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_8
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_16
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_32
|   |-- draw_multisampled_image_r8g8b8a8_unorm_samples_64
|-- blit
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_2
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_4
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_8
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_16
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_32
    |-- draw_multisampled_image_r8g8b8a8_unorm_samples_64
```

## Test Families

### Copy Meta-Operation (DynamicStateMetaOpsInstance)

Registered in `createDynamicStateMetaOperationsTests` at [line 1402](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1402). Uses `DynamicStateMetaOpsTestCase` at [line 1187](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1187) and `DynamicStateMetaOpsInstance` at [line 55](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L55) with `MetaOperation::META_OP_COPY`.

| Family | Description |
|--------|-------------|
| draw_multisampled_image_r8g8b8a8_unorm_samples_N | Draw to multisampled image, perform whole-image copy, draw again; verify both copy result and multisampled image integrity |

### Blit Meta-Operation (DynamicStateMetaOpsInstance)

Same registration as above, with `MetaOperation::META_OP_BLIT`.

| Family | Description |
|--------|-------------|
| draw_multisampled_image_r8g8b8a8_unorm_samples_N | Draw to multisampled image, perform whole-image blit, draw again; verify both blit result and multisampled image integrity |

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Meta Operation | Copy, Blit | [line 1475](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1475) |
| Multisampled Image Format | VK_FORMAT_R8G8B8A8_UNORM | [line 1476](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1476) |
| Sample Count | 2, 4, 8, 16, 32, 64 | [line 1478](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1478) |
| Copy/Blit Image Format | VK_FORMAT_R8G8B8A8_UNORM | [line 1409](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1409) |
| Copy/Blit Image Type | VK_IMAGE_TYPE_2D | [line 1408](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1408) |
| Copy/Blit Image Tiling | VK_IMAGE_TILING_OPTIMAL | [line 1411](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1411) |
| Copy/Blit Image Extent | defaultExtent (64x64x1) | [line 1410](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1410) |
| Allocation Kind | ALLOCATION_KIND_SUBALLOCATED | [line 1420](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1420) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_EXT_extended_dynamic_state3 | Required for dynamic rasterization samples | [line 1217](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1217) |
| extendedDynamicState3RasterizationSamples | Feature must be supported | [line 1217](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1217) |
| VK_KHR_dynamic_rendering | Required for dynamic rendering | [line 1224](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1224) |
| VK_FORMAT_FEATURE_TRANSFER_SRC_BIT | Source image format must support transfer src | [line 1227](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1227) |
| VK_FORMAT_FEATURE_TRANSFER_DST_BIT | Destination image format must support transfer dst | [line 1235](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1235) |
| VK_FORMAT_FEATURE_BLIT_SRC_BIT | Source format must support blit src (blit tests only) | [line 1251](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1251) |
| VK_FORMAT_FEATURE_BLIT_DST_BIT | Destination format must support blit dst (blit tests only) | [line 1262](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1262) |
| Sample count support | Multisampled image must support the requested sample count | [line 1308](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1308) |
| maxImageDimension2D | Image dimensions must not exceed limits | [line 1272](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1272) |

## Verification Methods

### Meta-Operation Verification (Copy)

Uses CPU-side reference comparison via `tcu::bitwiseCompare` at [line 235](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L235). The `copyRegionToTextureLevel` method at [line 248](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L248) computes the expected destination image contents from the source image data, treating the copy as a memcpy operation (replacing destination format with source format for comparison).

### Meta-Operation Verification (Blit)

Uses nearest-filtered blit comparison via `checkNearestFilteredResult` at [line 173](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L173). For integer formats, uses `intNearestBlitCompare`; for float/fixed-point formats, uses `floatNearestBlitCompare` with format-specific thresholds. Error masks are logged on failure at [line 218](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L218).

### Multisampled Draw Verification

Uses a second render pass with a verification fragment shader at [line 622](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L622). The shader reads the multisampled image as an input attachment, computes expected values per sample, and writes both actual and expected values to storage buffers. The CPU then compares them with a tolerance of 0.01 at [line 891](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L891).

## Test Principles Observed

- **Meta-operation interleaving**: The core test sequence at [line 1141](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1141) is: draw to multisampled image -> copy/blit -> draw to multisampled image again. This verifies that copy/blit operations do not interfere with the dynamic rasterization state or the multisampled image's contents.
- **Dynamic rasterization samples**: Uses `vkCmdSetRasterizationSamplesEXT` at [line 604](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L604) to set the sample count dynamically rather than through pipeline creation.
- **Dual verification**: Both the meta-operation result (copy/blit destination) and the multisampled image integrity are verified independently at [line 1176](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1176) and [line 1180](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1180).
- **Sample-specific draw patterns**: The fragment shader at [line 1342](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1342) writes different values to even/odd samples on the first vs. second draw, making it possible to detect if the meta-operation corrupted sample-specific data.
- **Command variants**: Both `vkCmdCopyImage`/`vkCmdBlitImage` and `vkCmdCopyImage2`/`vkCmdBlitImage2` (COPY_COMMANDS_2) are supported at [line 1019](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1019) and [line 1110](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1110).
- **VK_ATTACHMENT_LOAD_OP_LOAD**: The render pass uses load op LOAD at [line 378](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L378) to preserve multisampled image contents between draws, which is critical for detecting corruption.

## Notes / Uncertainties

- The test only uses VK_FORMAT_R8G8B8A8_UNORM for both the copy/blit images and the multisampled image at [line 1476](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1476). Other formats are not tested in this file.
- The test constrains several parameters via DE_ASSERT at [line 1196](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1196): source and destination formats must match, image type must be 2D, tiling must be optimal, allocation must be suballocated, and various other flags must be at their defaults.
- The copy test uses a whole-image copy region at [line 1424](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1424); partial copies or multi-region copies are not tested.
- The blit test uses a whole-image 1:1 blit at [line 1456](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1456); scaling or mirroring blits are not tested.
- The multisampled image is separate from the copy/blit source/destination images. The test verifies that the meta-operation does not corrupt the multisampled image, but does not test copying from/to the multisampled image itself.
- The fragment shader uses `gl_SampleID` at [line 1341](../../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1341), which requires the `sampleShadingEnable` feature or sample shading support.
