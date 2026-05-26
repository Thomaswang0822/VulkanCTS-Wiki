# vktSparseResourcesImageBlockShapes.cpp

## Overview

[`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L1-L23) registers `sparse_resources.image_block_shapes` and checks whether reported sparse image granularity matches standard Vulkan sparse residency block-shape tables for sampled image dimensions, sample counts, bits-per-pixel classes, compressed formats, and YCbCr 4:2:2 block extents ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L165-L179), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L259-L478)). The Vulkan API test plan identifies sparse resources as a separate feature area; this file supplies the standard-block-shape implementation detail ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)).

## Role

Implementation file for sparse-image block-shape conformance.

## Source Code

- Primary source: [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L78-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)

## Registration Hierarchy

```text
sparse_resources.image_block_shapes
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

## Test Families

### 2d — 2D standard and multisample block shapes

The `2d` child is generated with size `512x256x1`, the shared format list plus many compressed formats, and sample counts `1`, `2`, `4`, `8`, and `16` ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L488-L539), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L541-L579)). Verification uses `residencyStandard2DBlockShape` for single-sample 2D images and `residencyStandard2DMultisampleBlockShape` for multisampled images before comparing reported granularity to expected values ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L294-L455)).

### 2d_array — 2D array standard and multisample block shapes

The `2d_array` child uses size `512x256x6` and the same format/sample loop as `2d`, with array layers provided by shared image helpers ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L532-L545), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L182-L205)).

### cube — cube standard block shapes

The `cube` child uses size `256x256x1`; multisample cases are skipped because the registration loop only keeps `sampleCount > 1` for `IMAGE_TYPE_2D` and `IMAGE_TYPE_2D_ARRAY` ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L535-L539), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L571-L579)). Cube-compatible images add `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` before support checks ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L192-L195)).

### cube_array — cube-array standard block shapes

The `cube_array` child uses size `256x256x6`, cube-compatible image creation, shared cube-array layer expansion, and only single-sample cases because multisample non-2D image types are skipped ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L536-L579), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L196-L200)).

### 3d — 3D standard block shapes

The `3d` child uses size `512x256x16`; it verifies standard 3D sparse block shapes when `residencyStandard3DBlockShape` is enabled and skips multisample variants through the same image-type/sample-count guard ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L537-L579), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L259-L293)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct children | `2d`, `2d_array`, `cube`, `cube_array`, and `3d` are registered from `imageParameters` ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L532-L545)). |
| Image sizes | One size per type: `512x256x1`, `512x256x6`, `256x256x1`, `256x256x6`, and `512x256x16` ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L532-L537)). |
| Formats | `getImageTestFormats()` appends BC, ETC2/EAC, and ASTC compressed formats to the shared sparse test formats ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L488-L525)). |
| Sample counts | Registered sample-count leaves are `samples_1`, `samples_2`, `samples_4`, `samples_8`, and `samples_16`; non-2D image types keep only `samples_1` ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L539-L579)). |
| Expected block-shape inputs | Expected granularity depends on image type, sample count, compressed-vs-uncompressed format, bits per pixel, and YCbCr 4:2:2 block extent ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L233-L257), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L457-L468)). |

## Support / Feature Requirements

The case checks image-size limits, sparse support for the image type, sample-count feature bits (`sparseResidencyImage2D`, `sparseResidency2Samples`, `sparseResidency4Samples`, `sparseResidency8Samples`, and `sparseResidency16Samples`), and R64 sparse-image int64 atomic support where relevant ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L87-L137)). Iteration also rejects unsupported image format/sample-count combinations and image formats without sparse support ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L197-L212)).

## Verification Methods

The test creates the sparse image, queries `VkSparseImageMemoryRequirements`, selects each color or plane aspect, computes expected granularity from the standard sparse block-shape rules encoded in switch tables, adjusts for compressed and YCbCr block extents, and fails if the reported `imageGranularity` differs ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L221-L248), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L259-L478)). If the relevant standard-block-shape sparse property is disabled, the test returns pass for that case rather than enforcing the table ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L259-L263), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L294-L297), [`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L426-L427)).

## Test Principles Observed

- This page's tests verify reported sparse-image format properties directly, not shader-visible image contents ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L470-L478)).
- The parameter matrix deliberately extends the shared format set with compressed formats because block dimensions affect expected sparse block shapes ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L488-L525)).
- Multisample sparse residency is only generated for 2D and 2D array image types in this file ([`vktSparseResourcesImageBlockShapes.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L571-L579)).

## Notes / Uncertainties

- No nested registered source files were discovered under `image_block_shapes`; shared utilities supply formats and image naming but do not register this branch independently.
