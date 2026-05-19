# [vktImageMisalignedCubeTests.cpp](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1)

## Overview

[`vktImageMisalignedCubeTests.cpp`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.misaligned_cube` subtree. It tests cube image views created with misaligned `baseArrayLayer` values. The tests verify that cube images can be created from non-zero array layer offsets within a larger array, allowing multiple cube maps to be stored in a single image allocation.

## Role of File

- **Role:** implementation-heavy test file
- **Primary source:** [`vktImageMisalignedCubeTests.cpp`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1)
- **Header:** [`vktImageMisalignedCubeTests.hpp`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.hpp#L1)
- **Registration context:** registered under `image` in [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp) as `misaligned_cube` group via [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406)

## Source Code

- Implementation: [vktImageMisalignedCubeTests.cpp](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1)
- Header: [vktImageMisalignedCubeTests.hpp](../../../modules/vulkan/image/vktImageMisalignedCubeTests.hpp#L1)

## Registration Hierarchy

```text
image.misaligned_cube
├── 7
├── 8
├── 9
├── 10
└── 11
```

## Test Families

### 7 �?Seven-layer cube image test

Covers the `7` direct child registered by [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406). Creates a cube-compatible image with 7 array layers. Cube 0 starts at layer 0, Cube 1 starts at layer 1 (misaligned - only 1 layer remaining).

### 8 �?Eight-layer cube image test

Covers the `8` direct child registered by [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406). Creates a cube-compatible image with 8 array layers. Cube 0 starts at layer 0, Cube 1 starts at layer 2 (misaligned).

### 9 �?Nine-layer cube image test

Covers the `9` direct child registered by [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406). Creates a cube-compatible image with 9 array layers. Cube 0 starts at layer 0, Cube 1 starts at layer 3 (misaligned).

### 10 �?Ten-layer cube image test

Covers the `10` direct child registered by [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406). Creates a cube-compatible image with 10 array layers. Cube 0 starts at layer 0, Cube 1 starts at layer 4 (misaligned).

### 11 �?Eleven-layer cube image test

Covers the `11` direct child registered by [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L406). Creates a cube-compatible image with 11 array layers. Cube 0 starts at layer 0, Cube 1 starts at layer 5 (misaligned).

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Image type | `VK_IMAGE_TYPE_2D` with `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` | [Lines 66-67](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L66-L67) |
| Cube dimensions | 16x16 pixels per cube face | [Line 386](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L386) |
| Array layers | 7, 8, 9, 10, 11 layers | [Lines 385-387](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L385-L387) |
| Format | `VK_FORMAT_R8G8B8A8_UNORM` (fixed) | [Line 396](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L396) |
| Image usage | `VK_IMAGE_USAGE_STORAGE_BIT \| VK_IMAGE_USAGE_SAMPLED_BIT \| VK_IMAGE_USAGE_TRANSFER_SRC_BIT \| VK_IMAGE_USAGE_TRANSFER_DST_BIT` | [Lines 61-62](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L61-L62) |
| Cube 0 base layer | Layer 0 (always aligned) | [Line 157](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L157) |
| Cube 1 base layer | `numLayers - 6` (misaligned) | [Line 158](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L158) |

## Support / Feature Requirements

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` | All misaligned cube tests | Image creation flags at [Line 66](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L66) |

## Verification Methods

- **Compute shader sampling:** Each cube face is sampled at position (1,1,n) using `imageLoad` to extract a single texel value
- **Expected value comparison:** Extracted values are compared against expected grayscale values derived from layer indices
- **Per-pixel tolerance:** Uses epsilon of 1.0/(2*256) for floating-point comparison
- **Two-cube validation:** Both cube 0 (aligned) and cube 1 (misaligned) are verified

## Test Principles Observed

- **Misaligned base layer:** Second cube view starts at `numLayers - 6`, which is misaligned from the expected 6-layer cube boundary
- **Dual cube views:** Two `imageCube` views are created from the same underlying image with different base array layers
- **Grayscale encoding:** Each layer is filled with a unique grayscale value (16*layerIndex/255) to identify which layer data came from
- **Compute pipeline:** Uses compute shader with `imageLoad` on `imageCube` views

## Notes / Uncertainties

- Tests use a fixed format of `VK_FORMAT_R8G8B8A8_UNORM`
- Tests use a fixed cube size of 16x16 pixels per face
- Array layer count is constrained to range [6, 16] to ensure both cubes fit and misalignment is tested
- The test verifies that data written to specific array layers is correctly accessible through cube views with misaligned base layers
