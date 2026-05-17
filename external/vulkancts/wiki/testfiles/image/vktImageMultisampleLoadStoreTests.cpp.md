# vktImageMultisampleLoadStoreTests.cpp

## Overview

This file implements tests for multisampled storage image operations in Vulkan. It verifies that `imageStore()` and `imageLoad()` operations work correctly on multisampled images, including per-sample access patterns.

## Role of File

**Implementation-heavy test file** - Contains the actual test implementations, compute shaders, and verification logic for multisample load/store operations.

## Source Code

[vktImageMultisampleLoadStoreTests.cpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp)

## Related Files

- [vktImageTests.cpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTests.cpp) - Category root registration file
- [vktImageMultisampleLoadStoreTests.hpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageMultisampleLoadStoreTests.hpp) - Header with factory declaration
- [vktImageLoadStoreUtil.hpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageLoadStoreUtil.hpp) - Utility functions
- [vktImageTexture.hpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTexture.hpp) - Texture wrapper

## Registration Hierarchy

```text
image.load_store_multisample
```

## Test Families

### load_store_multisample â€?Multisampled Image Load/Store

Tests per-sample load and store operations on multisampled storage images.

**Subgroups (by image type):**
- `2d` - 2D images
- `2d_array` - 2D array images

**Test Structure:**
Each image type contains format groups, which contain sample count variants.

**Parameter Dimensions:**

| Parameter | Values |
|-----------|--------|
| Image Types | 2D, 2D_ARRAY |
| Formats | 13 formats (see below) |
| Sample Counts | 2, 4, 8, 16, 32, 64 |
| Layer Binding Modes | single_layer, all_layers (for array types) |
| Texture Size | 32x32 |

**Format Coverage:**

| Format Category | Formats |
|----------------|---------|
| Float | R32G32B32A32_SFLOAT, R16G16B16A16_SFLOAT, R32_SFLOAT |
| Uint | R32G32B32A32_UINT, R16G16B16A16_UINT, R8G8B8A8_UINT, R32_UINT |
| Sint | R32G32B32A32_SINT, R16G16B16A16_SINT, R8G8B8A8_SINT, R32_SINT |
| Unorm | R8G8B8A8_UNORM, R8G8B8A8_SNORM |
| Special | A8_UNORM_KHR (non-VulkanSC only) |

**Test Variations:**

Each format group contains variants for:
- `samples_2` through `samples_64` - Each supported sample count
- `_single_layer` suffix - Per-layer binding mode (array images only)

**Total Test Cases:**
- 2D images: 13 formats x 6 sample counts = 78 cases
- 2D_ARRAY images: 13 formats x 6 sample counts x 2 layer modes = 156 cases
- Total: ~234 test cases

## Test Principle

### Pass 1: Store Per-Sample Data

A compute shader writes a unique color pattern for each sample in each texel:
- Each sample receives a color based on its coordinates and sample index
- Color components computed as XOR combinations of coordinates
- Colors are scaled/bias according to format requirements

```glsl
// Per-sample store pattern
for (int sampleNdx = 0; sampleNdx < numSamples; ++sampleNdx) {
    vec4 color = vec4(
        gx ^ gy ^ gz ^ (sampleNdx >> 5) ^ (sampleNdx & 31),
        (xMax - gx) ^ gy ^ gz,
        gx ^ (yMax - gy) ^ gz,
        (xMax - gx) ^ (yMax - gy) ^ gz
    ) * scale + bias;
    imageStore(u_msImage, coord, sampleNdx, color);
}
```

### Pass 2: Load and Verify

A second compute shader loads each sample and verifies the values match expected:
- For integer formats: exact comparison
- For float/unorm formats: comparison with 0.02 threshold

If all samples match, writes checksum value (equal to sample count) to checksum image.

## Support/Feature Requirements

### Device Core Features
- `shaderStorageImageMultisample` - **Required** - Core feature for multisample storage images

### Format Features
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` - Format must support storage image usage

### Device Extensions (conditional)
- `VK_KHR_maintenance5` - Required only for `VK_FORMAT_A8_UNORM_KHR` format

### Format Support Checks
The test verifies:
1. `shaderStorageImageMultisample` feature is supported
2. Format is supported for the requested sample count
3. For A8_UNORM_KHR: storage read/write without format features are required

## Verification Methods

### Per-Sample Verification
1. Generate expected color values for each (x, y, z, sample) coordinate
2. Store colors to multisampled image
3. Load colors back and compare against expected
4. Each successful sample contributes to checksum

### Checksum Verification
1. Compute shader writes checksum count to separate checksum image
2. Checksum image is copied to host buffer
3. Host verifies each texel contains integer value equal to sample count
4. Failure indicates any sample color mismatch

### Format-Specific Thresholds

| Format Class | Comparison Method |
|--------------|------------------|
| Integer (uint/sint) | Exact equality |
| Float | 0.02 absolute difference threshold |
| Unorm/Snorm | 0.02 absolute difference threshold |

## Test Case Structure

```
load_store_multisample
â”œâ”€â”€ 2d
â”?  â”œâ”€â”€ r32g32b32a32_sfloat
â”?  â”?  â”œâ”€â”€ samples_2
â”?  â”?  â”œâ”€â”€ samples_4
â”?  â”?  â”œâ”€â”€ samples_8
â”?  â”?  â”œâ”€â”€ samples_16
â”?  â”?  â”œâ”€â”€ samples_32
â”?  â”?  â””â”€â”€ samples_64
â”?  â”œâ”€â”€ r16g16b16a16_sfloat
â”?  â”?  â””â”€â”€ ... (same sample variants)
â”?  â””â”€â”€ ... (other formats)
â”œâ”€â”€ 2d_array
â”?  â”œâ”€â”€ r32g32b32a32_sfloat
â”?  â”?  â”œâ”€â”€ samples_2
â”?  â”?  â”œâ”€â”€ samples_2_single_layer
â”?  â”?  â”œâ”€â”€ samples_4
â”?  â”?  â”œâ”€â”€ samples_4_single_layer
â”?  â”?  â””â”€â”€ ... (all sample counts x layer modes)
â”?  â””â”€â”€ ... (other formats)
```

## Implementation Notes

### Alpha-Only Format Handling
The `A8_UNORM_KHR` format receives special handling:
- Uses `GL_EXT_shader_image_load_formatted` extension in shaders
- Red channel used for alpha value storage
- Format qualifier not explicitly declared in shader

### Layer Binding Modes
- `all_layers` (default): Single image view covering all layers, single dispatch
- `single_layer`: Separate view per layer, dispatch loop over layers

### Color Computation
- Colors designed to produce values in range [0, 31] for typical dimensions
- Sample index split across two XOR terms to handle 64 samples case
- Scale and bias applied per format to match expected value ranges

## Dependencies

### Internal Dependencies
- `Texture` class - Image wrapper with type/size/layer management
- `Image` class - Vulkan image resource management
- `BufferWithMemory` - GPU buffer with host memory mapping
- `vk::SourceCollection` - Shader source program collection

### External Dependencies
- `VK_FORMAT_R32_SINT` - Checksum image format (constant)
- Vulkan memory allocator
- Vulkan compute pipeline utilities

## Uncertainties and Notes

1. **Sample Count Support**: Not all sample counts are guaranteed to be supported for every format/device combination. The test uses `vkGetPhysicalDeviceImageFormatProperties` to verify support.

2. **A8_UNORM_KHR**: Only available on non-VulkanSC builds due to VK_KHR_maintenance5 requirement.

3. **Host Verification**: The checksum approach allows efficient host-side verification by only checking integer counts rather than full pixel comparison.

4. **Texture Size**: Fixed at 32x32 for all configurations to ensure consistent color ranges across different sample counts.
