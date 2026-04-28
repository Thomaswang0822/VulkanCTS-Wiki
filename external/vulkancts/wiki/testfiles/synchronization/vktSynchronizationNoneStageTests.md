# vktSynchronizationNoneStageTests

## Overview

Tests for `VK_PIPELINE_STAGE_NONE` and `VK_PIPELINE_STAGE_2_NONE_KHR` stage masks introduced by the `VK_KHR_synchronization2` extension. The tests iterate over writable image layouts and readable image layouts, writing data to a test image using a method appropriate for the writable layout and reading via a method appropriate for the readable layout. Between the read and write operations, barriers use the NONE stage mask. Tests also cover generalized layouts (`VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL_KHR`, `VK_IMAGE_LAYOUT_ATTACHMENT_OPTIMAL_KHR`) and access flags (`VK_ACCESS_2_MEMORY_READ_BIT`, `VK_ACCESS_2_MEMORY_WRITE_BIT`) to test contextual synchronization.

This is a **sync2-only** test file (non-SC). It is registered under the `synchronization2` category only.

## Role of File

Provides the `none_stage` test group, which validates that pipeline barriers using `VK_PIPELINE_STAGE_2_NONE_KHR` as a destination stage correctly establish execution dependencies without specifying a particular pipeline stage, and that `VK_ACCESS_2_NONE_KHR` can be used as an access mask. This tests a core feature of the `VK_KHR_synchronization2` extension.

## Source Code

- [vktSynchronizationNoneStageTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp)

## Registration Path

```
synchronization2.none_stage
```

Registered in the sync2 path via `createNoneStageTests()` added to the `synchronization2` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp) (line 129).

## Test Hierarchy

```
none_stage
+-- <syncPrefix><writeLayout>_to_<readLayout>
```

### Layout Names

**Writable layouts** (10 total):
- `transfer_dst` (TRANSFER_DST_OPTIMAL, all aspects)
- `general` (GENERAL, all aspects)
- `color_attachment` (COLOR_ATTACHMENT_OPTIMAL, color aspect)
- `depth_stencil_attachment` (DEPTH_STENCIL_ATTACHMENT_OPTIMAL, depth+stencil)
- `depth_attachment` (DEPTH_ATTACHMENT_OPTIMAL, depth aspect)
- `stencil_attachment` (STENCIL_ATTACHMENT_OPTIMAL, stencil aspect)
- `generic_color_attachment` (ATTACHMENT_OPTIMAL_KHR, color aspect)
- `generic_depth_attachment` (ATTACHMENT_OPTIMAL_KHR, depth aspect)
- `generic_stencil_attachment` (ATTACHMENT_OPTIMAL_KHR, stencil aspect)
- `generic_depth_stencil_attachment` (ATTACHMENT_OPTIMAL_KHR, depth+stencil)

**Readable layouts** (12 total):
- `transfer_src` (TRANSFER_SRC_OPTIMAL, all aspects)
- `general` (GENERAL, all aspects)
- `shader_read` (SHADER_READ_ONLY_OPTIMAL, all aspects)
- `depth_stencil_read` (DEPTH_STENCIL_READ_ONLY_OPTIMAL, depth+stencil)
- `depth_read_stencil_attachment` (DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL, depth+stencil)
- `depth_attachment_stencil_read` (DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL, depth+stencil)
- `depth_read` (DEPTH_READ_ONLY_OPTIMAL, depth aspect)
- `stencil_read` (STENCIL_READ_ONLY_OPTIMAL, stencil aspect)
- `generic_color_read` (READ_ONLY_OPTIMAL_KHR, all aspects)
- `generic_depth_read` (READ_ONLY_OPTIMAL_KHR, depth aspect)
- `generic_stencil_read` (READ_ONLY_OPTIMAL_KHR, stencil aspect)
- `generic_depth_stencil_read` (READ_ONLY_OPTIMAL_KHR, depth+stencil)

**Sync prefixes** (3 variants):
- (empty) -- sync2 with generic access flags
- `old_access_` -- sync2 with specific access flags
- `legacy_` -- LEGACY synchronization structures with NONE_STAGE

## Test Families

| Family | Description |
|--------|-------------|
| NoneStageTestCase | Individual test case per write-layout/read-layout/sync-type combination. Writes gradient data to an image, uses a barrier with NONE stage between write and read, transitions layout, reads back data, and verifies correctness. |

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Synchronization Type | SYNCHRONIZATION2 (generic access), SYNCHRONIZATION2 (specific access), LEGACY | `synchronizationData` in `createNoneStageTests()` |
| Write Layout | 10 writable layout/aspect combinations | `writableLayoutsData` |
| Read Layout | 12 readable layout/aspect combinations | `readableLayoutsData` |
| Use Generic Access Flags | true, false | `SynchronizationData::useGenericAccessFlags` |

Incompatible write/read aspect combinations are skipped (e.g., color write with depth-only read).

## Support/Feature Requirements

| Requirement | Type | Notes |
|-------------|------|-------|
| VK_KHR_synchronization2 | Device Extension | Required for all tests |
| VK_KHR_create_renderpass2 | Device Extension | Required when graphics pipeline is used for write or read |
| separateDepthStencilLayouts | Device Feature | Required when testing separate depth or stencil aspects |
| Format support | Format Properties | Per-format image format properties checked for required usage flags |

## Verification Methods

1. **Pixel comparison for float formats**: Uses `tcu::floatThresholdCompare` with a threshold of 0.01 to compare reference gradient data against the result read back from the image.
2. **Integer comparison for uint/int formats**: Compares pixel values directly using `getPixelInt()`, generating an error mask image showing mismatches. Diagonal texels are skipped for stencil tests due to gradient/stencil operation differences.
3. **Gradient reference**: A component gradient from (0,0,0,0) to (1,1,1,1) is generated as the reference image, written to the test image, and compared against the readback.

## Test Principles

1. **NONE stage barrier**: The core test places a barrier with `VK_PIPELINE_STAGE_2_NONE_KHR` as the destination stage mask and `VK_ACCESS_2_NONE_KHR` as the destination access mask between the write and read operations. This verifies that the NONE stage correctly establishes a dependency without specifying a pipeline stage.
2. **Layout transition via barrier**: After the NONE-stage barrier, a second barrier with `VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT_KHR` transitions the image from the write layout to the read layout, ensuring the data is visible for the subsequent read operation.
3. **Generic access flags**: Tests using `VK_ACCESS_2_MEMORY_READ_BIT_KHR` / `VK_ACCESS_2_MEMORY_WRITE_BIT_KHR` instead of specific access flags validate the contextual synchronization feature of `VK_KHR_synchronization2`.
4. **Comprehensive layout coverage**: Tests cover all standard and generalized (attachment_optimal, read_only_optimal) layouts for color, depth, stencil, and combined depth-stencil aspects.
5. **LEGACY compatibility**: A subset of tests uses LEGACY synchronization structures with `VK_PIPELINE_STAGE_NONE_KHR` to verify backward compatibility.

## Notes/Uncertainties

- **sync2-only**: The `none_stage` group is only added to the `synchronization2` test tree, not to the LEGACY `synchronization` tree. However, some test cases within the group use `SynchronizationType::LEGACY` to test NONE stage with legacy barrier structures.
- **Non-SC only**: The test is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`).
- **Stencil gradient limitation**: For stencil attachment tests, only a 1-bit gradient is possible. The test draws a single triangle and skips verification on the diagonal where the stencil operation does not produce a clean gradient.
- **Image extent**: All tests use a fixed 32x32 image extent.
- **Aspect filtering**: When write and read aspects differ (e.g., write is depth+stencil but read is depth-only), the test focuses on the overlapping aspect. The `IMAGE_ASPECT_ALL` (0u) value is used for color/transfer layouts and matches any aspect.
