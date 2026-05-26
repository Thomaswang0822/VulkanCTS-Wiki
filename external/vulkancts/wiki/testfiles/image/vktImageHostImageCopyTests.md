# vktImageHostImageCopyTests.cpp

## Overview

Tests that verify the correctness of the VK_EXT_host_image_copy extension, which enables direct memory-to-image and image-to-memory copy operations from the host without requiring command buffer submission. The file covers a comprehensive set of scenarios including format conversions, layout transitions, sparse images, large images, array images, preinitialized layouts, image-to-image copies, and various tiling modes.

## Role of File

This is an implementation-heavy file that provides test implementations and registration for host image copy tests. It registers tests under `image.host_image_copy`. Note: This group is only available when `CTS_USES_VULKANSC` is not defined (i.e., regular Vulkan, not VulkanSC), as enforced in the parent registration file [vktImageTests.cpp](../../../modules/vulkan/image/vktImageTests.cpp#L49-L51).

## Source Code

- Implementation: [vktImageHostImageCopyTests.cpp](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp)
- Header: [vktImageHostImageCopyTests.hpp](../../../modules/vulkan/image/vktImageHostImageCopyTests.hpp)

## Registration Hierarchy

```text
image.host_image_copy
├── draw_*_* (draw command format combinations)
├── dispatch_*_* (dispatch command format combinations)
├── large_images
├── array
├── linear (preinitialized/image-to-image tiling group)
├── optimal (preinitialized/image-to-image tiling group)
├── drm_format_modifier (preinitialized/image-to-image tiling group)
├── capture_replay
├── properties
├── query
├── identical_memory_layout
├── depth_stencil
└── simple
```

Evidence:
- `host_image_copy` group created by [`createImageHostImageCopyTests()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L5001-L5005)
- Test structure populated by `testGenerator()` at [line 4344](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4344)

## Test Families

### draw_*_* — Draw-based host image copy tests

Tests host image copy operations with images used in graphics draw commands. Format naming: `draw_<output_format>_<sampled_format>`. Covers format conversions like uncompressed to compressed and depth formats to color.

### dispatch_*_* — Dispatch-based host image copy tests

Tests host image copy operations with images used in compute dispatch commands. Similar format naming pattern.

### large_images — Large image copy tests

Tests copy operations on large images (128x128, 512x512, 4096x4096) at [lines 4617-4653](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4617-L4653).

### array — Array image copy tests

Tests copy operations on array images with various layer configurations. Covers:
- Array sizes: 1, 2, 6 layers with various offsets
- 2D array images
- Cube-compatible images
- Remaining layers handling

### preinitialized — Preinitialized image layout tests

Tests host image copy with images in preinitialized layout state. Organized by tiling (linear, optimal, drm_format_modifier) with src/dst layout combinations.

### capture_replay — Capture/replay test

Single test for verifying capture/replay scenarios using heap memory at [lines 4883-4889](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4883-L4889).

### properties — Device properties tests

Tests querying device properties for host image copy support at [lines 4891-4893](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4891-L4893).

### query — Format feature query tests

Tests querying supported layouts and features for host image copy at [lines 4906-4919](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4906-L4919).

### identical_memory_layout — Memory layout verification tests

Tests that host image copy works correctly with identical memory layouts at [lines 4921-4934](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4921-L4934).

### depth_stencil — Depth/stencil format tests

Tests host image copy with depth and stencil formats at [lines 4937-4948](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4937-L4948).

### simple — Simple copy tests

Basic host image copy tests with minimal parameter variation at [lines 4964-4997](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4964-L4997).

### Nested structure under draw/dispatch groups

Each draw/dispatch format group contains:
- **Copy tests**: `host_transition_host_copy`, `host_transition`, `barrier_transition_host_copy`
- **Action**: `memory_to_image`, `image_to_memory`, `memcpy`
- **Layouts**: `general_general`, `transfer_src_transfer_dst`
- **Intermediate layouts**: `general`, `color_attachment_optimal`, `depth_stencil_attachment_optimal`, `depth_stencil_read_only_optimal`, `shader_read_only_optimal`, `transfer_src_optimal`, `transfer_dst_optimal`
- **Tiling**: `linear`, `optimal`
- **Mip/region/padding**: `0_1_0`, `1_1_0`, `4_1_0`, `0_4_4`, `0_16_64`
- **Sizes**: `16x16`, `32x28`, `53x61`

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Sampled Formats | R8G8B8A8_UNORM, R8G8_UNORM, R32G32B32A32_SFLOAT, R8_UNORM, R32G32_SFLOAT, R16_UNORM, D16_UNORM, D32_SFLOAT, BC7_UNORM_BLOCK, ETC2_R8G8B8A8_UNORM_BLOCK, ASTC_4x4_UNORM_BLOCK, R10X6_UNORM_PACK16 | [lines 4388-4402](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4388-L4402) |
| Output Formats | Various format conversions supported | [lines 4388-4402](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4388-L4402) |
| Tiling | VK_IMAGE_TILING_LINEAR, VK_IMAGE_TILING_OPTIMAL, VK_IMAGE_TILING_DRM_FORMAT_MODIFIER_EXT | [lines 4373-4380](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4373-L4380), [4766-4774](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4766-L4774) |
| Commands | DRAW, DISPATCH | [lines 248-252](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L248-L252) |
| Copy Actions | MEMORY_TO_IMAGE, IMAGE_TO_MEMORY, MEMCPY | [lines 254-259](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L254-L259) |
| Image Sizes | 16x16, 32x28, 53x61, 128x128, 512x512, 4096x4096 | [lines 4410-4418](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4410-L4418), [lines 4602-4606](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4602-L4606) |
| Layout Transitions | Host transition, barrier transition | [lines 4346-4358](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4346-L4358) |
| Preinitialized Layouts | general, color_attachment_optimal, depth_stencil_attachment_optimal, depth_stencil_read_only_optimal, shader_read_only_optimal, transfer_src_optimal, transfer_dst_optimal, preinitialized, present_src, depth_read_only_stencil_attachment_optimal, depth_attachment_stencil_read_only_optimal, depth_read_only_optimal, stencil_attachment_optimal, stencil_read_only_optimal, read_only_optimal, attachment_optimal, attachment_feedback_loop_optimal | [lines 4776-4798](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4776-L4798) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_EXT_host_image_copy | Required for all tests | [lines 1222](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1222), [1781](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1781), [2076](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2076), [2200](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2200), [2602](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2602), [2746](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2746), [3455](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3455), [4241](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4241) |
| VK_FORMAT_FEATURE_2_HOST_IMAGE_TRANSFER_BIT_EXT | Format must support host image transfer | [lines 205-246](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L205-L246) |
| VK_KHR_maintenance9 | For cube-compatible and 2D array compatible tests | Verified in code |
| VK_KHR_sampler_ycbcr_conversion | For YCbCr format tests | Via format lists |

## Verification Methods

### HostImageCopyTestInstance

The main test instance at [line 281](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L281) verifies:
1. Generates test data via `generateData()` at [line 118](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L118)
2. Copies memory to image via `copyMemoryToImage()` at [line 335](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L335)
3. Performs draw/dispatch operations on the image
4. Copies image back to memory
5. Compares result against expected values

### PreinitializedTestCase

Tests preinitialized image layouts by verifying data integrity after various layout transitions.

### QueryTestCase

Verifies `VkPhysicalDeviceHostImageCopyPropertiesEXT` and format feature queries.

### IdenticalMemoryLayoutTestCase

Verifies that host image copy works correctly when source and destination have identical memory layouts.

### DepthStencilHostImageCopyTest

Specialized test for depth/stencil formats, handling aspect mask separation.

## Test Principles Observed

- **Format conversion**: Tests verify that data is correctly converted between formats during host image copy
- **Layout transitions**: Tests both host-initiated (`vkTransitionImageLayoutEXT`) and pipeline barrier transitions
- **Dynamic rendering**: Tests alternate between dynamic rendering and traditional render passes
- **Sparse images**: Tests verify sparse image support for host image copy operations. Current sparse-image setup can request a fence in addition to the bind semaphore; memory-to-image sparse sampled images and sparse copy targets wait for that fence before layout transition/use ([wait type selection](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L493-L510), [memory-to-image wait](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L761-L765), [copy-target wait](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L915-L916)).
- **Mip level support**: Tests various mip level configurations
- **Region count and padding**: Tests multiple regions with varying padding configurations
- **Image-to-image copies**: Tests direct image-to-image copy via `vkCopyImageToImageEXT`
- **DRM format modifiers**: Tests linear tiling via DRM format modifiers

## Notes / Uncertainties

- This file has no VulkanSC guards (`#ifndef CTS_USES_VULKANSC`) within the file itself
- However, the registration in `vktImageTests.cpp` wraps this file's inclusion and registration in `#ifndef CTS_USES_VULKANSC` at [lines 49-51](../../../modules/vulkan/image/vktImageTests.cpp#L49-L51) and [lines 92-94](../../../modules/vulkan/image/vktImageTests.cpp#L92-L94)
- The file is 5008+ lines and contains multiple test case classes and instance classes
- Test cases alternate between sparse and non-sparse images using a static_assert pattern at [line 4509](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4509) to ensure odd number of variations
- Some format combinations have restrictions based on when they were added to the specification
- Restricted format combinations are defined at [lines 4404-4408](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4404-L4408)
