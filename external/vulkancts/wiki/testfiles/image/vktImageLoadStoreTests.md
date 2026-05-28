# vktImageLoadStoreTests.cpp

## Overview

This file implements the core image load/store functionality tests for Vulkan storage images. It provides comprehensive coverage of imageStore and imageLoad operations across various image types, formats, tilings, and shader configurations.

## Role of File

**Implementation-heavy test file** - Contains the actual test implementations, shader programs, and verification logic for multiple test families.

## Source Code

[vktImageLoadStoreTests.cpp](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp)

## Related Files

- [vktImageTests.cpp](../../../modules/vulkan/image/vktImageTests.cpp) - Category root registration file
- [vktImageLoadStoreTests.hpp](../../../modules/vulkan/image/vktImageLoadStoreTests.hpp) - Header with factory declarations
- [vktImageLoadStoreUtil.hpp](../../../modules/vulkan/image/vktImageLoadStoreUtil.hpp) - Utility functions
- [vktImageTexture.hpp](../../../modules/vulkan/image/vktImageTexture.hpp) - Texture wrapper

## Registration Hierarchy

```text
image.store
├── with_format
└── without_format

image.load_store
├── with_format
├── without_format
└── without_any_format

image.format_reinterpret

image.extend_operands_spirv1p4

image.nontemporal_operand

image.device_scope_access
├── comp_comp
└── comp_draw

image.load_store_lod
├── with_format
└── without_format
```

## Test Families

### store — Image Store Operations

Tests basic `imageStore()` shader operations across image types and formats.

**Subgroups:**
- `with_format` - Tests with explicit format declaration in shader
- `without_format` - Tests without format declaration (format-less storage)

**Parameter Dimensions:**
- Image types: 1D, 1D_ARRAY, 2D, 2D_ARRAY, 3D, CUBE, CUBE_ARRAY, BUFFER
- Formats: ~80 formats including float, uint, sint, unorm, snorm, srgb variants
- Tilings: OPTIMAL, LINEAR
- Texture sizes: 64x64 for 2D, 64x1 for 1D, 64x64x8 for 3D, etc.
- Layer counts: 1 (non-array), 6 (cube), 8 (array), 12 (cube_array)

**Test Variations:**
- Standard store with declared format
- Store with constant value (`FLAG_STORE_CONSTANT_VALUE`)
- Single layer binding for layered images (`FLAG_SINGLE_LAYER_BIND`)
- Minimum alignment for buffer images (`FLAG_MINALIGN`)
- Depth format support (D16_UNORM, D32_SFLOAT, D24_UNORM_S8_UINT)

**Verification Methods:**
- Writes generated color pattern to image
- Copies image to host buffer via transfer
- Compares buffer contents against expected computed values

### load_store — Image Load and Store Operations

Tests combined `imageLoad()` and `imageStore()` operations, verifying round-trip data integrity.

**Subgroups:**
- `with_format` - Both read and write with format declaration
- `without_format` - Write with format, read without format
- `without_any_format` - Both operations without format declaration

**Parameter Dimensions:**
- Same image types, formats, and tilings as store tests
- Supports mipmap levels (up to 6 levels in some configurations)
- Additional variants for texel buffer minimum alignment

**Test Variations:**
- Standard load/store with format declarations
- Single layer binding for layered images
- Minimum alignment variants for buffer images
- Uniform texel buffer vs storage texel buffer
- Three-component format support for buffer images
- Depth format storage support

**Verification Methods:**
- Generates reference image data with computed color pattern
- Stores pattern to image
- Loads back from image
- Compares loaded values against reference using format-appropriate thresholding

### format_reinterpret — Format Reinterpretation

Tests storage image access with different format interpretations (write as one format, read as another).

**Parameter Dimensions:**
- Compatible format pairs from the 80+ format set
- 8 image types (excluding BUFFER)
- Format compatibility based on matching pixel size

**Verification Methods:**
- Writes image data in one format
- Reads back in a different but byte-size-compatible format
- Verifies bit-level reinterpretation produces expected results
- Handles special cases (denormalized values, NaN, infinity for float formats)

### extend_operands — SPIR-V 1.4 Extend Operands (SignExtend/ZeroExtend)

Tests SPIR-V 1.4 extension operand behavior for integer format widening operations.

**Subgroups (by format):**
- 32-bit and 64-bit signed/unsigned integer formats

**Test Variations:**
- `read` - Tests SignExtend/ZeroExtend on image load operations
- `write` - Tests SignExtend/ZeroExtend on image store operations
- `mismatched_sign` - Signed/unsigned mismatch cases
- `matched_sign` - Matching signedness cases
- `relaxed_precision` - Tests with relaxed precision qualifiers
- `normal_precision` - Tests with normal precision qualifiers

**Support Requirements:**
- `VK_KHR_spirv_1_4` device functionality
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` for formats

**Verification Methods:**
- Performs load or store with specified operand extension
- Compares results against expected values with appropriate precision thresholds

### nontemporal_operand — Non-Temporal Memory Hint

Tests `OpImageWrite` with non-temporal memory hint operand.

**Parameter Dimensions:**
- Uses integer formats only (compatible with extend operand test infrastructure)
- 2D images of size 8x8
- 64-bit and 32-bit signed/unsigned formats

**Support Requirements:**
- Vulkan 1.3+ (non-temporal support requirement)
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT`

**Verification Methods:**
- Stores values using non-temporal hint
- Loads back and verifies correctness

### device_scope_access — Device Scope Memory Access

Tests Vulkan memory model device-scope synchronization for image load/store operations.

**Subgroups:**
- `comp_comp` - Compute-to-compute synchronization
- `comp_draw` - Compute-to-graphics synchronization

**Parameter Dimensions:**
- Image types: 1D, 2D, 3D
- Formats: 80+ formats from standard set
- Tilings: OPTIMAL, LINEAR

**Support Requirements:**
- Vulkan 1.1+ (device memory model features)
- `vulkanMemoryModel` device feature
- `vulkanMemoryModelDeviceScope` device feature
- Vulkan 1.2+ equivalent SPIR-V version
- For `comp_draw`: Color attachment and transfer source image usage support

**Test Principle:**
- Pass 1: Compute shader writes to image with device-scope store
- Pass 2: Compute or graphics shader loads from same image with device-scope load
- Verifies memory visibility across shader invocations with device scope

**Verification Methods:**
- Writes known pattern in compute shader
- Reads pattern back in compute or draw shader
- Compares loaded values against expected

### load_store_lod — Mipmap Level-of-Detail Access (AMD)

Tests image load/store operations with explicit LOD specification using `VK_AMD_shader_image_load_store_lod` extension.

**Subgroups:**
- `with_format` - Tests with format declarations
- `without_format` - Tests without format on read, with format on write

**Parameter Dimensions:**
- Image types: 1D, 1D_ARRAY, 2D, 2D_ARRAY, 3D, CUBE, CUBE_ARRAY
- Texture size: 64x64 (or equivalent) with 6 mipmap levels
- Formats: 80+ formats (those with SPIR-V format support)
- Single tiling mode: OPTIMAL

**Test Variations:**
- Standard with LOD specification
- Single layer binding for layered images

**Support Requirements:**
- `VK_AMD_shader_image_load_store_lod` device functionality
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` for formats

**Verification Methods:**
- Writes to specific mipmap levels using explicit LOD
- Loads from those levels
- Compares against reference data computed for each level

## Parameter Dimensions Summary

| Parameter | Values |
|-----------|--------|
| Image Types | 1D, 1D_ARRAY, 2D, 2D_ARRAY, 3D, CUBE, CUBE_ARRAY, BUFFER |
| Formats | ~80 formats (float, uint, sint, unorm, snorm, srgb, packed) |
| Tilings | OPTIMAL, LINEAR |
| Texture Dimensions | 64x64 (2D), 64x1 (1D), 64x64x8 (3D), etc. |
| Mipmap Levels | 1-6 depending on texture type and test |
| Layer Counts | 1, 6 (cube), 8 (array), 12 (cube_array) |
| Sample Counts | N/A for non-multisample tests |

## Support / Feature Requirements

### Device Core Features
- `shaderStorageImageMultisample` - For multisample-capable storage images (indirect)
- `imageCubeArray` - For cube array image types
- `shaderInt64` - For 64-bit integer format support

### Format Features
- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` - Required for all storage image tests
- `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` - Required for buffer storage tests
- `VK_FORMAT_FEATURE_2_STORAGE_WRITE_WITHOUT_FORMAT_BIT` - For format-less writes
- `VK_FORMAT_FEATURE_2_STORAGE_READ_WITHOUT_FORMAT_BIT` - For format-less reads

### Device Extensions
- `VK_KHR_spirv_1_4` - For extend operand tests
- `VK_KHR_maintenance5` - For A8_UNORM and A1B5G5R5 formats
- `VK_AMD_shader_image_load_store_lod` - For LOD-specific load/store tests

### API Version Requirements
- Vulkan 1.1+ - For device scope access tests
- Vulkan 1.3+ - For non-temporal operand tests

## Test Flags

### StoreTest Flags
- `FLAG_SINGLE_LAYER_BIND` - Bind each layer separately
- `FLAG_DECLARE_IMAGE_FORMAT_IN_SHADER` - Include format qualifier in shader
- `FLAG_MINALIGN` - Use minimum alignment for buffer views
- `FLAG_STORE_CONSTANT_VALUE` - Store constant pattern instead of computed

### LoadStoreTest Flags
- `FLAG_SINGLE_LAYER_BIND` - Bind each layer separately
- `FLAG_RESTRICT_IMAGES` - Use restrict qualifier on images
- `FLAG_DECLARE_FORMAT_IN_SHADER_READS` - Format qualifier on read operations
- `FLAG_DECLARE_FORMAT_IN_SHADER_WRITES` - Format qualifier on write operations
- `FLAG_MINALIGN` - Use minimum alignment for buffer views
- `FLAG_UNIFORM_TEXEL_BUFFER` - Use uniform texel buffer instead of storage

## Verification Methods by Test Type

| Test Type | Verification Approach |
|-----------|----------------------|
| Store | Buffer copy + pixel comparison against expected pattern |
| Load/Store | Reference image generation + format-appropriate threshold comparison |
| Format Reinterpret | Bit-level comparison accounting for reinterpretation rules |
| Extend Operands | Signed/unsigned value comparison with precision thresholds |
| Device Scope | Cross-shader synchronization verification |
| LOD Access | Mipmap-level reference comparison |

## Notes

- Some depth formats are restricted to OPTIMAL tiling as per Vulkan spec
- A8_UNORM_KHR requires VK_KHR_maintenance5 (not supported in VulkanSC)
- Three-component formats only apply to BUFFER image type tests
- Format-less operations require corresponding format feature bits
- Device scope tests include both compute-only and compute-to-graphics configurations
