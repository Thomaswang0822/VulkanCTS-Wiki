# vktImageGeneralLayoutTests.cpp

## Overview

Tests for general image layout scenarios including ASTC compressed texture sampling and copies, memory barriers with various access patterns, input attachments with dynamic rendering, and MSAA multi-attachment rendering. All tests use `VK_IMAGE_LAYOUT_GENERAL` to validate behavior under the most flexible image layout.

## Role of File

This is a registration and implementation file that:
- Registers the `general_layout` test group
- Provides test cases for ASTC texture operations
- Tests memory barrier synchronization with images
- Tests input attachment and MSAA rendering scenarios
- Uses general layout for all image operations

## Source Code Link

[vktImageGeneralLayoutTests.cpp](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp)

## Registration Hierarchy

```text
image.general_layout
├── astc_sample
├── memory_barrier (non-VulkanSC)
├── input_attachment
└── msaa

image.general_layout.astc_sample
├── copy_into_image
├── copy_from_image
├── host_copy_into_image (non-VulkanSC)
├── host_copy_from_image (non-VulkanSC)
└── sample_alias

image.general_layout.memory_barrier
├── compute
└── fragment
image.general_layout.memory_barrier.compute
├── write_read
└── read_write
image.general_layout.memory_barrier.compute.write_read
├── shader_read_write
├── sampled_read_storage_write
└── storage_read_storage_write
image.general_layout.memory_barrier.compute.read_write
├── shader_read_write
├── sampled_read_storage_write
└── storage_read_storage_write
image.general_layout.memory_barrier.fragment
├── write_read
└── read_write
image.general_layout.memory_barrier.fragment.write_read
├── shader_read_write
├── sampled_read_storage_write
└── storage_read_storage_write
image.general_layout.memory_barrier.fragment.read_write
├── shader_read_write
├── sampled_read_storage_write
└── storage_read_storage_write

image.general_layout.input_attachment
├── input_attachment
└── sampled
image.general_layout.input_attachment.input_attachment
├── execution
├── memory
└── image
image.general_layout.input_attachment.input_attachment.execution
├── render_pass
└── dynamic_rendering
image.general_layout.input_attachment.input_attachment.memory
├── render_pass
└── dynamic_rendering
image.general_layout.input_attachment.input_attachment.image
├── render_pass
└── dynamic_rendering
image.general_layout.input_attachment.sampled
├── execution
├── memory
└── image
image.general_layout.input_attachment.sampled.execution
├── render_pass
└── dynamic_rendering
image.general_layout.input_attachment.sampled.memory
├── render_pass
└── dynamic_rendering
image.general_layout.input_attachment.sampled.image
├── render_pass
└── dynamic_rendering

image.general_layout.msaa
├── same
└── different
image.general_layout.msaa.same
├── 4
└── 8
image.general_layout.msaa.different
├── 4
└── 8
```

## Test Families

### astc_sample — ASTC Compressed Texture Operations

Tests ASTC compressed texture sampling and copy operations with `VK_IMAGE_LAYOUT_GENERAL`:

**Test variants** ([vktImageGeneralLayoutTests.cpp#L2314-L2322](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2314-L2322)):
- `copy_into_image`: Transfer data into ASTC image, sample, verify output
- `copy_from_image`: Sample ASTC image, transfer out, verify data
- `host_copy_into_image`: Use host image copy for data transfer (non-VulkanSC)
- `host_copy_from_image`: Use host image copy for data retrieval (non-VulkanSC)
- `sample_alias`: Test with mutable format aliasing (ASTC_8x8_UNORM vs ASTC_8x8_SRGB)

**Test approach** ([vktImageGeneralLayoutTests.cpp#L239-L599](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L239-L599)):
- Creates 128x128x1 ASTC_8x8_UNORM_BLOCK image
- Generates block-level test data using tcu::astc::generateBlockCaseTestData
- Decompresses reference data for verification
- Performs copy/sampling operations
- Compares output buffer data against expected decompressed values

### memory_barrier — Image Memory Barrier Synchronization (non-VulkanSC)

Tests synchronization2 memory barriers with images in general layout:

**Structure** ([vktImageGeneralLayoutTests.cpp#L2333-L2377](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2333-L2377)):
- 2 shader stages: compute, fragment
- 2 orderings: write-read, read-write
- 3 access patterns: shader read/write, sampled read + storage write, storage read/write

**Test approach** ([vktImageGeneralLayoutTests.cpp#L690-L1063](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L690-L1063)):
- Creates 128x128x1 R32_SFLOAT image
- Copies initial data to image
- Uses VkMemoryBarrier2 for synchronization
- Performs shader operations (storage image or sampler)
- Copies result back and verifies data matches expected values

### input_attachment — Input Attachment Rendering

Tests input attachments with subpass dependencies and various barrier types:

**Barrier types** ([vktImageGeneralLayoutTests.cpp#L2380-L2388](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2380-L2388)):
- `execution`: Only execution dependency (no memory/image barrier)
- `memory`: Memory barrier between subpasses
- `image`: Image memory barrier between subpasses

**Variants**:
- Input attachment type: actual input attachment vs sampled
- Rendering method: render pass vs dynamic rendering (non-VulkanSC)

**Test approach** ([vktImageGeneralLayoutTests.cpp#L1197-L1719](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1197-L1719)):
- Creates 128x128x1 R8G8B8A8_UNORM images
- Two-subpass render with data flow between passes
- First pass writes/transforms data
- Second pass reads as input attachment and applies additional transformation
- Verifies final output matches expected transformation

### msaa — MSAA Multi-Attachment Rendering

Tests rendering with multiple color attachments using general layout:

**Parameters** ([vktImageGeneralLayoutTests.cpp#L2418-L2433](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2418-L2433)):
- Attachment counts: 4, 8 (limited by maxColorAttachments)
- Attachment modes: same (MSAA targets used as color attachments) vs different (separate targets)
- Sample count: 4x MSAA

**Test approach** ([vktImageGeneralLayoutTests.cpp#L1812-L2237](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1812-L2237)):
- Creates multiple 128x128x1 color attachments
- Renders to all attachments in sequence
- Resolves MSAA if using different attachments
- Copies result and verifies UV coordinate mapping in fragment shader output

## Parameter Dimensions

| Parameter | Values |
|-----------|--------|
| Image Format | ASTC_8x8_UNORM_BLOCK (astc_sample), R32_SFLOAT (memory_barrier), R8G8B8A8_UNORM (others) |
| Image Dimensions | 128 x 128 x 1 (all tests) |
| Sample Count | 1 (most), 4 (MSAA tests) |
| Mip Levels | 1 (all tests) |
| Array Layers | 1 (all tests) |
| Color Attachment Counts | 4, 8 (MSAA tests) |
| Buffer Count | width x height (128 x 128 = 16384 elements) |

## Support / Feature Requirements

- **astc_sample** ([vktImageGeneralLayoutTests.cpp#L617-L635](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L617-L635)):
  - `VK_EXT_astc_decode_mode`
  - `textureCompressionASTC_LDR` feature
  - `VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT` for optimal tiling
  - `VK_EXT_host_image_copy` for host copy variants (non-VulkanSC)

- **memory_barrier** ([vktImageGeneralLayoutTests.cpp#L1081-L1084](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1081-L1084)):
  - `VK_KHR_synchronization2`

- **input_attachment** ([vktImageGeneralLayoutTests.cpp#L1737-L1745](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1737-L1745)):
  - `VK_KHR_synchronization2`
  - `VK_KHR_dynamic_rendering` for dynamic rendering variants (non-VulkanSC)
  - `VK_KHR_dynamic_rendering_local_read` for dynamic rendering (non-VulkanSC)

- **msaa** ([vktImageGeneralLayoutTests.cpp#L2255-L2259](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2255-L2259)):
  - `maxColorAttachments` >= requested attachment count

## Verification Methods

1. **Data comparison with epsilon tolerance**:
   - Float values compared with epsilon (0.04 for textures, 1e-6 for storage)
   - Integer values compared with epsilon of 1 or 2

2. **ASTC decompression verification**:
   - Reference data decompressed using tcu::TexDecompressionParams::AstcMode::ASTCMODE_LDR
   - Output compared against decompressed expected values

3. **Transform pipeline verification**:
   - Known transformation functions (e.g., value / 2.0, 1.0 - value)
   - Expected result calculated and compared byte-by-byte

4. **Shader output verification**:
   - UV coordinate mapping (u = x/windowWidth, v = y/windowHeight)
   - Fragment shader writes coord.x to R, coord.y to G channels
   - Expected values: expectedR = (pixel_index % width) + 1, expectedG = (pixel_index / height) + 1

## Test Principles Observed

- All images use `VK_IMAGE_LAYOUT_GENERAL` for maximum flexibility testing
- ASTC tests use block-level test data generation for controlled verification
- Memory barrier tests cover all common access flag combinations
- Input attachment tests cover execution, memory, and image barrier types
- MSAA tests verify correct rendering to multiple attachments with varying configurations
- Dynamic rendering variants tested alongside traditional render pass approach

## Notes

- Non-VulkanSC guards on memory_barrier and host_copy tests due to VK_KHR_synchronization2 and VK_EXT_host_image_copy requirements
- ASTC tests use fixed 128x128x1 dimensions with ASTC_8x8 block size
- MSAA attachment counts limited to 4 and 8 to ensure test compatibility across devices
- Dynamic rendering tests require both VK_KHR_dynamic_rendering and VK_KHR_dynamic_rendering_local_read
