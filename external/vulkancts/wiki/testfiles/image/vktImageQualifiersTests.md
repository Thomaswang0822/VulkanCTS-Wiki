# [vktImageQualifiersTests.cpp](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L1)

## Overview

[`vktImageQualifiersTests.cpp`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L1) implements the `image.qualifiers` subgroup registered by the image module. The file tests Vulkan memory qualifiers (coherent, volatile, restrict) on storage images and texel buffers in compute shaders, verifying correct memory synchronization behavior across work groups.

## Role of File

Implementation-heavy test file for the `image.qualifiers` subgroup.

## Source Code

- Primary source: [vktImageQualifiersTests.cpp](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L1)
- Header: [vktImageQualifiersTests.hpp](../../../../modules/vulkan/image/vktImageQualifiersTests.hpp#L1)
- Parent-category registration: `createImageQualifiersTests()` called from image module

## Registration Hierarchy

```text
image.qualifiers
├── coherent
├── volatile
└── restrict
```

Evidence:
- `qualifiers` group created at [`createImageQualifiersTests()`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L698)
- Three qualifier subgroups created: coherent, volatile, restrict at lines 726-767

## Test Families

### coherent �?Coherent memory qualifier tests

The `coherent` subgroup tests that the `coherent` memory qualifier properly synchronizes memory access across work groups. Tests write values using `imageStore`, perform `memoryBarrier()` and `barrier()`, then read values from other work items. Verification compares computed sums against expected values.

Tests all image types (1D, 1D array, 2D, 2D array, 3D, cube, cube array, buffer) with three formats (R32_FLOAT, R32_UINT, R32_SINT) at [`vktImageQualifiersTests.cpp#L753-759`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L753).

### volatile �?Volatile memory qualifier tests

The `volatile` subgroup tests that the `volatile` memory qualifier prevents caching of image values. Uses the same test pattern as coherent tests.

Tests all image types with three formats at [`vktImageQualifiersTests.cpp#L753-759`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L753).

### restrict �?Restrict memory qualifier tests

The `restrict` subgroup tests that the `restrict` qualifier properly isolates pointers. Uses `createImageQualifierRestrictCase` from `vktImageLoadStoreTests.hpp` at [`vktImageQualifiersTests.cpp#L744-746`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L744).

Tests all image types (1D, 1D array, 2D, 2D array, 3D, cube, cube array, buffer) at [`vktImageQualifiersTests.cpp#L737-747`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L737).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Image types | IMAGE_TYPE_1D, IMAGE_TYPE_1D_ARRAY, IMAGE_TYPE_2D, IMAGE_TYPE_2D_ARRAY, IMAGE_TYPE_3D, IMAGE_TYPE_CUBE, IMAGE_TYPE_CUBE_ARRAY, IMAGE_TYPE_BUFFER at [`vktImageQualifiersTests.cpp#L711-718`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L711) |
| Formats | R32G32B32A32_SFLOAT, R32_UINT, R32_SINT at [`vktImageQualifiersTests.cpp#L720-724`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L720) |
| Image sizes | 64x64x1 (2D/cube), 64x1x8 (1D array/3D), 64x1x1 (1D/buffer) at [`vktImageQualifiersTests.cpp#L711-718`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L711) |
| Work group size | (8, 8, 2) base with dynamic adjustment at [`vktImageQualifiersTests.cpp#L64`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L64) |
| Read offsets | X: {1,4,7,10}, Y: {2,5,8,11}, Z: {3,6,9,12} at [`vktImageQualifiersTests.cpp#L65-70`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L65) |

## Support / Feature Requirements

- `IMAGE_TYPE_CUBE_ARRAY` requires `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY` via [`MemoryQualifierTestCase::checkSupport()`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L238)

## Verification Methods

- Compute shader writes values using XOR operations: `gx^gy^gz`
- Memory barriers ensure visibility across work groups
- Tests read from 4 offset locations within the same work group
- Sum of read values is written back and compared against reference
- Float comparison uses 0.01 threshold at [`vktImageQualifiersTests.cpp#L156-157`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L156)
- Integer comparison uses zero threshold at [`vktImageQualifiersTests.cpp#L152-154`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L152)
- Per-layer/cube-face comparison at [`vktImageQualifiersTests.cpp#L126-163`](../../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L126)

## Test Principles Observed

- Test all combinations of image types and data formats
- Use memory barriers to validate coherent/volatile behavior
- Cross-validate results across all cube faces and array layers
- Separate test paths for images vs texel buffers

## Notes / Uncertainties

- The restrict qualifier tests delegate to `createImageQualifierRestrictCase` whose implementation is in `vktImageLoadStoreTests.hpp` and was not fully examined
- Test for 3D images sets z dimension to 8, which may affect coverage for very small images
- The restrict tests only have one test case per image type without format variations
