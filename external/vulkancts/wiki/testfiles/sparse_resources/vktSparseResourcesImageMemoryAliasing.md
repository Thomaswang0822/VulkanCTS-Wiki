# vktSparseResourcesImageMemoryAliasing.cpp

## Overview

[`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1-L22) implements the regular `sparse_resources.image_sparse_memory_aliasing` branch and the device-group `sparse_resources.device_group_image_sparse_memory_aliasing` branch registered by the sparse-resource dispatcher ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L60-L61), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104)). The Vulkan API test plan identifies memory aliasing and sparse resources as distinct memory-management concerns, and this source combines them by binding two sparse images to the same residency memory binds, then using one image as transfer input and the other as shader output ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L257-L276), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L460-L492)).

## Role

Implementation-heavy registration file shared by two top-level roots. The regular and device-group factories construct different root names but call the same common builder; the device-group path passes `useDeviceGroup=true` so sparse binds and submissions include device-group metadata where needed ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1091), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104)).

## Source Code

- Primary source: [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L73-L115)
- Shared queue/device-group base: [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L257-L276)

## Registration Hierarchy

```text
sparse_resources.image_sparse_memory_aliasing
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The inspected file also registers `sparse_resources.device_group_image_sparse_memory_aliasing` with the same direct children by passing a different root group into the common builder ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1091), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1100-L1104)).

## Test Families

### 2d — two-dimensional sparse image aliasing

This direct child is generated from `IMAGE_TYPE_2D` and registers four image sizes under each supported format from `getTestFormats(IMAGE_TYPE_2D)`, skipping sizes that do not satisfy format alignment for some YCbCr formats ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1084)). Runtime creates two sparse images with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, `VK_IMAGE_CREATE_SPARSE_ALIASED_BIT`, and `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`; both images use the same `imageResidencyMemoryBinds`, while mip-tail memory is tracked separately for read and write images ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L217-L245), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L347-L492)).

### 2d_array — two-dimensional array sparse image aliasing

This child is generated from `IMAGE_TYPE_2D_ARRAY` with image sizes that include array-layer counts in the `z` component, such as `512x256x6` and `128x128x8` ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1042-L1044)). The copy and shader paths use `arrayLayers = getNumLayers()` and process every layer in buffer/image copy regions ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L223-L224), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L531-L540)).

### cube — cube sparse image aliasing

This child is generated from `IMAGE_TYPE_CUBE`; cube-compatible images add `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` before sparse support checks and image creation ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1045-L1047), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L234-L235)).

### cube_array — cube-array sparse image aliasing

This child is generated from `IMAGE_TYPE_CUBE_ARRAY`; like cube images, it enables cube-compatible creation and processes array layers through the shared image-copy and shader-view setup ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1048-L1050), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L234-L245)).

### 3d — three-dimensional sparse image aliasing

This child is generated from `IMAGE_TYPE_3D` and includes depth-bearing sizes such as `256x256x16`, `128x128x8`, and `503x137x3` ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1051-L1054)). Shader dispatch dimensions come from `getShaderGridSize()` and are bounded by workgroup-size and workgroup-count checks before `cmdDispatch` ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L734-L759)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Registered roots | `image_sparse_memory_aliasing` and `device_group_image_sparse_memory_aliasing` are separate factory roots using the same common builder ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104)). |
| Direct children | `2d`, `2d_array`, `cube`, `cube_array`, and `3d` are produced from the `imageParameters` vector ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1060)). |
| Image sizes | Each direct child lists four sizes; YCbCr-incompatible odd sizes are skipped with `getImageSizeAlignment()` checks ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1054), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1064-L1079)). |
| Formats | Formats are sourced through `getTestFormats(imageType)`; R64 formats trigger additional 64-bit shader-image-atomic requirements ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1054), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L140-L153)). |

## Support / Feature Requirements

Each case requires `sparseResidencyAliased`, verifies image-size limits, checks sparse support for the image type, and requires `VK_EXT_shader_image_atomic_int64` plus both `shaderImageInt64Atomics` and `sparseImageInt64Atomics` for R64 formats ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154)). Runtime checks sparse format support, storage-image support or storage-compatible plane formats, `sparseAddressSpaceSize`, compatible memory type selection, and peer-memory copy/generic-destination features in cross-device cases ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L247-L277), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L307-L340)).

## Verification Methods

The test fills an input buffer with per-mip reference bytes, copies it into the read image, dispatches compute shaders that write deterministic per-channel values into the aliased write image, copies the read image back out, and validates both shader-written sparse blocks and mip-tail/reference data ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L564-L580), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L615-L759), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L929)). Generated compute programs store `index % 127`-based values, with fixed/floating formats compared using acceptable error and integer formats compared exactly ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L932-L1022), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L856-L907)).

## Test Principles Observed

- The central aliasing condition is that the read and write sparse images receive identical sparse image memory binds for regular residency blocks, while their mip-tail binds are distinct where needed ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L460-L488)).
- Device-group mode is parameterized at the same test-family level and changes sparse-bind `pNext` and submission behavior, not the registered image-type tree ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L438-L448), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L796-L798)).

## Notes / Uncertainties

- The canonical hierarchy tree is intentionally limited to the regular `sparse_resources.image_sparse_memory_aliasing` root to satisfy the one-root Level-3 hierarchy contract. The device-group root is documented in prose and parameter tables because the inspected source registers it from the same implementation file with the same direct children ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104)).
