# [vktImageSizeTests.cpp](../../../modules/vulkan/image/vktImageSizeTests.cpp#L1)

## Overview

[`vktImageSizeTests.cpp`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L1) implements the `image.image_size` subgroup registered by the image module. The file tests the GLSL `imageSize()` builtin function for various image types and access qualifiers, verifying that it returns correct dimensions according to the Vulkan specification.

## Role of File

Implementation-heavy test file for the `image.image_size` subgroup.

## Source Code

- Primary source: [vktImageSizeTests.cpp](../../../modules/vulkan/image/vktImageSizeTests.cpp#L1)
- Header: [vktImageSizeTests.hpp](../../../modules/vulkan/image/vktImageSizeTests.hpp#L1)
- Parent-category registration: `createImageSizeTests()` called from image module

## Registration Hierarchy

```text
image.image_size
├── 1d
├── 1d_array
├── 2d
├── 2d_array
├── 3d
├── cube
├── cube_array
└── buffer
```

Evidence:
- `image_size` group created at [`createImageSizeTests()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L579)
- Image type subgroups created at lines 583-609

## Test Families

### 1d, 1d_array, 2d, 2d_array, 3d, cube, cube_array, buffer — imageSize() for all image types

Each image type subgroup tests `imageSize()` with multiple configurations:
- Access qualifier combinations: readonly, writeonly, readonly_writeonly
- Base image sizes: 32x32x32, 12x34x56, 1x1x1, 7x1x1
- 2D view of 3D (where applicable)

Test case naming format: `{qualifier}_{2d_view_}{WIDTH}x{HEIGHT}x{DEPTH}`

### 2d_view variants — 2D view of 3D image tests

When the image type is 3D and the `is2DViewOf3D` flag is set, tests use `VK_EXT_image_2d_view_of_3d` to create a 2D view of the 3D image. The `imageSize()` should return ivec2 with z=0 for these views.

Enabled unless `CTS_USES_VULKANSC` is defined (VulkanSC does not support this extension).

## Expected imageSize() Results

From [`getExpectedImageSizeResult()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L131-168):

| Image Type | Return value |
|---|---|
| 1D, Buffer | ivec3(width, 0, 0) |
| 1D Array, 2D, Cube | ivec3(width, height, 0) |
| 2D Array, 3D (normal) | ivec3(width, height, depth/layers) |
| 2D Array, 3D (2D view) | ivec3(width, height, 0) |
| Cube Array | ivec3(width, height, numCubes) |

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Image types | IMAGE_TYPE_1D, IMAGE_TYPE_1D_ARRAY, IMAGE_TYPE_2D, IMAGE_TYPE_2D_ARRAY, IMAGE_TYPE_3D, IMAGE_TYPE_CUBE, IMAGE_TYPE_CUBE_ARRAY, IMAGE_TYPE_BUFFER at [`vktImageSizeTests.cpp#L560-563`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L560) |
| Format | VK_FORMAT_R32G32B32A32_SFLOAT at [`vktImageSizeTests.cpp#L581`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L581) |
| Base image sizes | 32x32x32, 12x34x56, 1x1x1, 7x1x1 at [`vktImageSizeTests.cpp#L566-571`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L566) |
| Access qualifiers | FLAG_READONLY_IMAGE, FLAG_WRITEONLY_IMAGE, FLAG_READONLY_IMAGE|FLAG_WRITEONLY_IMAGE at [`vktImageSizeTests.cpp#L573-577`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L573) |
| Texture dimensions | Derived from base sizes: 1D (1D/buffer: X), 1D array (X x Y), 2D (X x Y), 2D array (X x Y x layers), Cube (X x X x 6), Cube array (X x X x 12), 3D (X x Y x Z) at [`getTexture()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L58-88) |

## Support / Feature Requirements

- `IMAGE_TYPE_CUBE_ARRAY` requires `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY` via [`SizeTest::checkSupport()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L214-215)
- 2D view of 3D requires `VK_EXT_image_2d_view_of_3d` via [`SizeTest::checkSupport()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L233)
- Format must be supported for the specified image usage flags via [`SizeTest::checkSupport()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L224-229)

## Verification Methods

- Compute shader calls `imageSize()` and writes result to SSBO
- Result is read back to host memory and compared against expected value
- [`tcu::IVec3 readIVec3()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L125-129) interprets buffer as ivec3
- Single dispatch with work group size (1,1,1) at [`vktImageSizeTests.cpp#L366`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L366)
- No data is read from or written to the image itself; only the size query is tested

## Test Principles Observed

- Test all image types including texel buffers
- Cover all combinations of access qualifiers (readonly, writeonly, both)
- Test boundary sizes including minimum (1x1x1) and asymmetric dimensions
- Verify 2D views of 3D images return correct reduced dimensions
- Verify cube arrays report number of cubes, not total layers

## Notes / Uncertainties

- The test uses a single dispatch (1,1,1) rather than testing across the image dimensions
- Only one format (R32G32B32A32_SFLOAT) is tested for all image types
- 2D view of 3D tests are skipped for VulkanSC due to lack of `VK_EXT_image_2d_view_of_3d` support
- The actual image data is uninitialized and never read; only the size metadata is verified
