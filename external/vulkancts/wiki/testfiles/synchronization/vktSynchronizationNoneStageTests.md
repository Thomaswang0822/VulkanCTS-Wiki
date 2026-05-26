# vktSynchronizationNoneStageTests

## Overview

Tests for `VK_PIPELINE_STAGE_NONE` and `VK_PIPELINE_STAGE_2_NONE_KHR` stage masks introduced by the `VK_KHR_synchronization2` extension. The tests iterate over writable image layouts and readable image layouts, writing data to a test image using a method appropriate for the writable layout and reading via a method appropriate for the readable layout. Between the read and write operations, barriers use the NONE stage mask. Tests also cover generalized layouts (`VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL_KHR`, `VK_IMAGE_LAYOUT_ATTACHMENT_OPTIMAL_KHR`) and access flags (`VK_ACCESS_2_MEMORY_READ_BIT`, `VK_ACCESS_2_MEMORY_WRITE_BIT`) to test contextual synchronization.

This is a **sync2-only** test file (non-SC). It is registered under the `synchronization2` category only.

## Role of File

Provides the `none_stage` test group, which validates that pipeline barriers using `VK_PIPELINE_STAGE_2_NONE_KHR` as a destination stage correctly establish execution dependencies without specifying a particular pipeline stage, and that `VK_ACCESS_2_NONE_KHR` can be used as an access mask. This tests a core feature of the `VK_KHR_synchronization2` extension.

## Source Code

- [vktSynchronizationNoneStageTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp)

## Registration Hierarchy

```text
synchronization2.none_stage
├── color_attachment_to_general
├── color_attachment_to_generic_color_read
├── color_attachment_to_shader_read
├── color_attachment_to_transfer_src
├── depth_attachment_to_depth_read
├── depth_attachment_to_general
├── depth_attachment_to_generic_color_read
├── depth_attachment_to_generic_depth_read
├── depth_attachment_to_shader_read
├── depth_attachment_to_transfer_src
├── depth_stencil_attachment_to_depth_attachment_stencil_read
├── depth_stencil_attachment_to_depth_read_stencil_attachment
├── depth_stencil_attachment_to_depth_stencil_read
├── depth_stencil_attachment_to_general
├── depth_stencil_attachment_to_generic_color_read
├── depth_stencil_attachment_to_generic_depth_stencil_read
├── depth_stencil_attachment_to_shader_read
├── depth_stencil_attachment_to_transfer_src
├── general_to_depth_attachment_stencil_read
├── general_to_depth_read
├── general_to_depth_read_stencil_attachment
├── general_to_depth_stencil_read
├── general_to_general
├── general_to_generic_color_read
├── general_to_generic_depth_read
├── general_to_generic_depth_stencil_read
├── general_to_generic_stencil_read
├── general_to_shader_read
├── general_to_stencil_read
├── general_to_transfer_src
├── generic_color_attachment_to_general
├── generic_color_attachment_to_generic_color_read
├── generic_color_attachment_to_shader_read
├── generic_color_attachment_to_transfer_src
├── generic_depth_attachment_to_depth_read
├── generic_depth_attachment_to_general
├── generic_depth_attachment_to_generic_color_read
├── generic_depth_attachment_to_generic_depth_read
├── generic_depth_attachment_to_shader_read
├── generic_depth_attachment_to_transfer_src
├── generic_depth_stencil_attachment_to_depth_attachment_stencil_read
├── generic_depth_stencil_attachment_to_depth_read_stencil_attachment
├── generic_depth_stencil_attachment_to_depth_stencil_read
├── generic_depth_stencil_attachment_to_general
├── generic_depth_stencil_attachment_to_generic_color_read
├── generic_depth_stencil_attachment_to_generic_depth_stencil_read
├── generic_depth_stencil_attachment_to_shader_read
├── generic_depth_stencil_attachment_to_transfer_src
├── generic_stencil_attachment_to_general
├── generic_stencil_attachment_to_generic_color_read
├── generic_stencil_attachment_to_generic_stencil_read
├── generic_stencil_attachment_to_shader_read
├── generic_stencil_attachment_to_stencil_read
├── generic_stencil_attachment_to_transfer_src
├── legacy_color_attachment_to_general
├── legacy_color_attachment_to_generic_color_read
├── legacy_color_attachment_to_shader_read
├── legacy_color_attachment_to_transfer_src
├── legacy_depth_attachment_to_depth_read
├── legacy_depth_attachment_to_general
├── legacy_depth_attachment_to_generic_color_read
├── legacy_depth_attachment_to_generic_depth_read
├── legacy_depth_attachment_to_shader_read
├── legacy_depth_attachment_to_transfer_src
├── legacy_depth_stencil_attachment_to_depth_attachment_stencil_read
├── legacy_depth_stencil_attachment_to_depth_read_stencil_attachment
├── legacy_depth_stencil_attachment_to_depth_stencil_read
├── legacy_depth_stencil_attachment_to_general
├── legacy_depth_stencil_attachment_to_generic_color_read
├── legacy_depth_stencil_attachment_to_generic_depth_stencil_read
├── legacy_depth_stencil_attachment_to_shader_read
├── legacy_depth_stencil_attachment_to_transfer_src
├── legacy_general_to_depth_attachment_stencil_read
├── legacy_general_to_depth_read
├── legacy_general_to_depth_read_stencil_attachment
├── legacy_general_to_depth_stencil_read
├── legacy_general_to_general
├── legacy_general_to_generic_color_read
├── legacy_general_to_generic_depth_read
├── legacy_general_to_generic_depth_stencil_read
├── legacy_general_to_generic_stencil_read
├── legacy_general_to_shader_read
├── legacy_general_to_stencil_read
├── legacy_general_to_transfer_src
├── legacy_generic_color_attachment_to_general
├── legacy_generic_color_attachment_to_generic_color_read
├── legacy_generic_color_attachment_to_shader_read
├── legacy_generic_color_attachment_to_transfer_src
├── legacy_generic_depth_attachment_to_depth_read
├── legacy_generic_depth_attachment_to_general
├── legacy_generic_depth_attachment_to_generic_color_read
├── legacy_generic_depth_attachment_to_generic_depth_read
├── legacy_generic_depth_attachment_to_shader_read
├── legacy_generic_depth_attachment_to_transfer_src
├── legacy_generic_depth_stencil_attachment_to_depth_attachment_stencil_read
├── legacy_generic_depth_stencil_attachment_to_depth_read_stencil_attachment
├── legacy_generic_depth_stencil_attachment_to_depth_stencil_read
├── legacy_generic_depth_stencil_attachment_to_general
├── legacy_generic_depth_stencil_attachment_to_generic_color_read
├── legacy_generic_depth_stencil_attachment_to_generic_depth_stencil_read
├── legacy_generic_depth_stencil_attachment_to_shader_read
├── legacy_generic_depth_stencil_attachment_to_transfer_src
├── legacy_generic_stencil_attachment_to_general
├── legacy_generic_stencil_attachment_to_generic_color_read
├── legacy_generic_stencil_attachment_to_generic_stencil_read
├── legacy_generic_stencil_attachment_to_shader_read
├── legacy_generic_stencil_attachment_to_stencil_read
├── legacy_generic_stencil_attachment_to_transfer_src
├── legacy_stencil_attachment_to_general
├── legacy_stencil_attachment_to_generic_color_read
├── legacy_stencil_attachment_to_generic_stencil_read
├── legacy_stencil_attachment_to_shader_read
├── legacy_stencil_attachment_to_stencil_read
├── legacy_stencil_attachment_to_transfer_src
├── legacy_transfer_dst_to_depth_attachment_stencil_read
├── legacy_transfer_dst_to_depth_read
├── legacy_transfer_dst_to_depth_read_stencil_attachment
├── legacy_transfer_dst_to_depth_stencil_read
├── legacy_transfer_dst_to_general
├── legacy_transfer_dst_to_generic_color_read
├── legacy_transfer_dst_to_generic_depth_read
├── legacy_transfer_dst_to_generic_depth_stencil_read
├── legacy_transfer_dst_to_generic_stencil_read
├── legacy_transfer_dst_to_shader_read
├── legacy_transfer_dst_to_stencil_read
├── legacy_transfer_dst_to_transfer_src
├── old_access_color_attachment_to_general
├── old_access_color_attachment_to_generic_color_read
├── old_access_color_attachment_to_shader_read
├── old_access_color_attachment_to_transfer_src
├── old_access_depth_attachment_to_depth_read
├── old_access_depth_attachment_to_general
├── old_access_depth_attachment_to_generic_color_read
├── old_access_depth_attachment_to_generic_depth_read
├── old_access_depth_attachment_to_shader_read
├── old_access_depth_attachment_to_transfer_src
├── old_access_depth_stencil_attachment_to_depth_attachment_stencil_read
├── old_access_depth_stencil_attachment_to_depth_read_stencil_attachment
├── old_access_depth_stencil_attachment_to_depth_stencil_read
├── old_access_depth_stencil_attachment_to_general
├── old_access_depth_stencil_attachment_to_generic_color_read
├── old_access_depth_stencil_attachment_to_generic_depth_stencil_read
├── old_access_depth_stencil_attachment_to_shader_read
├── old_access_depth_stencil_attachment_to_transfer_src
├── old_access_general_to_depth_attachment_stencil_read
├── old_access_general_to_depth_read
├── old_access_general_to_depth_read_stencil_attachment
├── old_access_general_to_depth_stencil_read
├── old_access_general_to_general
├── old_access_general_to_generic_color_read
├── old_access_general_to_generic_depth_read
├── old_access_general_to_generic_depth_stencil_read
├── old_access_general_to_generic_stencil_read
├── old_access_general_to_shader_read
├── old_access_general_to_stencil_read
├── old_access_general_to_transfer_src
├── old_access_generic_color_attachment_to_general
├── old_access_generic_color_attachment_to_generic_color_read
├── old_access_generic_color_attachment_to_shader_read
├── old_access_generic_color_attachment_to_transfer_src
├── old_access_generic_depth_attachment_to_depth_read
├── old_access_generic_depth_attachment_to_general
├── old_access_generic_depth_attachment_to_generic_color_read
├── old_access_generic_depth_attachment_to_generic_depth_read
├── old_access_generic_depth_attachment_to_shader_read
├── old_access_generic_depth_attachment_to_transfer_src
├── old_access_generic_depth_stencil_attachment_to_depth_attachment_stencil_read
├── old_access_generic_depth_stencil_attachment_to_depth_read_stencil_attachment
├── old_access_generic_depth_stencil_attachment_to_depth_stencil_read
├── old_access_generic_depth_stencil_attachment_to_general
├── old_access_generic_depth_stencil_attachment_to_generic_color_read
├── old_access_generic_depth_stencil_attachment_to_generic_depth_stencil_read
├── old_access_generic_depth_stencil_attachment_to_shader_read
├── old_access_generic_depth_stencil_attachment_to_transfer_src
├── old_access_generic_stencil_attachment_to_general
├── old_access_generic_stencil_attachment_to_generic_color_read
├── old_access_generic_stencil_attachment_to_generic_stencil_read
├── old_access_generic_stencil_attachment_to_shader_read
├── old_access_generic_stencil_attachment_to_stencil_read
├── old_access_generic_stencil_attachment_to_transfer_src
├── old_access_stencil_attachment_to_general
├── old_access_stencil_attachment_to_generic_color_read
├── old_access_stencil_attachment_to_generic_stencil_read
├── old_access_stencil_attachment_to_shader_read
├── old_access_stencil_attachment_to_stencil_read
├── old_access_stencil_attachment_to_transfer_src
├── old_access_transfer_dst_to_depth_attachment_stencil_read
├── old_access_transfer_dst_to_depth_read
├── old_access_transfer_dst_to_depth_read_stencil_attachment
├── old_access_transfer_dst_to_depth_stencil_read
├── old_access_transfer_dst_to_general
├── old_access_transfer_dst_to_generic_color_read
├── old_access_transfer_dst_to_generic_depth_read
├── old_access_transfer_dst_to_generic_depth_stencil_read
├── old_access_transfer_dst_to_generic_stencil_read
├── old_access_transfer_dst_to_shader_read
├── old_access_transfer_dst_to_stencil_read
├── old_access_transfer_dst_to_transfer_src
├── stencil_attachment_to_general
├── stencil_attachment_to_generic_color_read
├── stencil_attachment_to_generic_stencil_read
├── stencil_attachment_to_shader_read
├── stencil_attachment_to_stencil_read
├── stencil_attachment_to_transfer_src
├── transfer_dst_to_depth_attachment_stencil_read
├── transfer_dst_to_depth_read
├── transfer_dst_to_depth_read_stencil_attachment
├── transfer_dst_to_depth_stencil_read
├── transfer_dst_to_general
├── transfer_dst_to_generic_color_read
├── transfer_dst_to_generic_depth_read
├── transfer_dst_to_generic_depth_stencil_read
├── transfer_dst_to_generic_stencil_read
├── transfer_dst_to_shader_read
├── transfer_dst_to_stencil_read
└── transfer_dst_to_transfer_src
```

Registered in the sync2 path via [`createNoneStageTests()`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L1375), added to the `synchronization2` group in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L129). This group is **NOT** registered under the LEGACY `synchronization` category.

## Test Families

Each direct child is an individual test case following the naming pattern `<syncPrefix><writeLayout>_to_<readLayout>`. The 216 test cases are organized into three groups by synchronization type and access flag strategy.

### color_attachment_to_general — sync2 with generic access flags (72 tests)

Test cases with no name prefix. These use `SynchronizationType::SYNCHRONIZATION2` with generic access flags (`VK_ACCESS_2_MEMORY_READ_BIT_KHR` / `VK_ACCESS_2_MEMORY_WRITE_BIT_KHR`) instead of specific access flags.

Each test writes gradient data to an image via a method appropriate for the writable layout, uses a barrier with `VK_PIPELINE_STAGE_2_NONE_KHR` destination stage and `VK_ACCESS_2_NONE_KHR` destination access mask between write and read, transitions layout, reads back data, and verifies correctness.

**Writable layouts** (10 total):

| Name | Layout | Aspect |
|------|--------|--------|
| `transfer_dst` | TRANSFER_DST_OPTIMAL | all |
| `general` | GENERAL | all |
| `color_attachment` | COLOR_ATTACHMENT_OPTIMAL | color |
| `depth_stencil_attachment` | DEPTH_STENCIL_ATTACHMENT_OPTIMAL | depth+stencil |
| `depth_attachment` | DEPTH_ATTACHMENT_OPTIMAL | depth |
| `stencil_attachment` | STENCIL_ATTACHMENT_OPTIMAL | stencil |
| `generic_color_attachment` | ATTACHMENT_OPTIMAL_KHR | color |
| `generic_depth_attachment` | ATTACHMENT_OPTIMAL_KHR | depth |
| `generic_stencil_attachment` | ATTACHMENT_OPTIMAL_KHR | stencil |
| `generic_depth_stencil_attachment` | ATTACHMENT_OPTIMAL_KHR | depth+stencil |

**Readable layouts** (12 total):

| Name | Layout | Aspect |
|------|--------|--------|
| `transfer_src` | TRANSFER_SRC_OPTIMAL | all |
| `general` | GENERAL | all |
| `shader_read` | SHADER_READ_ONLY_OPTIMAL | all |
| `depth_stencil_read` | DEPTH_STENCIL_READ_ONLY_OPTIMAL | depth+stencil |
| `depth_read_stencil_attachment` | DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL | depth+stencil |
| `depth_attachment_stencil_read` | DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL | depth+stencil |
| `depth_read` | DEPTH_READ_ONLY_OPTIMAL | depth |
| `stencil_read` | STENCIL_READ_ONLY_OPTIMAL | stencil |
| `generic_color_read` | READ_ONLY_OPTIMAL_KHR | all |
| `generic_depth_read` | READ_ONLY_OPTIMAL_KHR | depth |
| `generic_stencil_read` | READ_ONLY_OPTIMAL_KHR | stencil |
| `generic_depth_stencil_read` | READ_ONLY_OPTIMAL_KHR | depth+stencil |

Incompatible write/read aspect combinations are skipped (e.g., color write with depth-only read).

### old_access_color_attachment_to_general — sync2 with specific access flags (72 tests)

Test cases with the `old_access_` name prefix. These use `SynchronizationType::SYNCHRONIZATION2` with specific access flags (e.g., `VK_ACCESS_2_TRANSFER_WRITE_BIT_KHR`, `VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT_KHR`) instead of the generic `MEMORY_READ`/`MEMORY_WRITE` flags. The write layout, read layout, and aspect filtering are identical to the no-prefix group.

### legacy_color_attachment_to_general — LEGACY synchronization with NONE stage (72 tests)

Test cases with the `legacy_` name prefix. These use `SynchronizationType::LEGACY` synchronization structures (e.g., `vkCmdPipelineBarrier` instead of `vkCmdPipelineBarrier2`) with `VK_PIPELINE_STAGE_NONE_KHR` to verify backward compatibility. The write layout, read layout, and aspect filtering are identical to the no-prefix group. Despite using LEGACY structures, these tests are still registered under `synchronization2.none_stage` because the `none_stage` group is only added to the `synchronization2` test tree.

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
