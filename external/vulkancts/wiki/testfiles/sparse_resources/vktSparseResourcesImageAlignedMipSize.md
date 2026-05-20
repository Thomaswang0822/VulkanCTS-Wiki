# vktSparseResourcesImageAlignedMipSize.cpp

## Overview

[`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L1-L23) registers `sparse_resources.aligned_mip_size` and verifies the relationship between device sparse properties, sparse image format flags, image granularity, and the first mip-tail LOD ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L211-L239), [`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L250-L285)). The Vulkan API test plan only identifies sparse resources as a separate area; this file provides the concrete aligned-mip-size check ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)).

## Role

Implementation file for an image sparse-residency property/metadata consistency test.

## Source Code

- Primary source: [`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L78-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)

## Registration Hierarchy

```text
sparse_resources.aligned_mip_size
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

## Test Families

### 2d — 2D sparse image mip-tail alignment

The `2d` child is generated from `IMAGE_TYPE_2D` with a single registered base size `512x256x1` and all formats returned by `getTestFormats(IMAGE_TYPE_2D)` after YCbCr size-alignment filtering ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L280)). The instance creates a sparse-residency sparse-binding image, queries sparse memory requirements, and checks the color-aspect granularity and first mip-tail LOD ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L143-L209)).

### 2d_array — 2D array sparse image mip-tail alignment

The `2d_array` child uses `512x256x6`, array-layer mapping from shared helpers, and the same format loop and alignment skip as the `2d` family ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L280), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L182-L205)).

### cube — cube sparse image mip-tail alignment

The `cube` child uses `256x256x1`, sets `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` for cube-compatible image types, and then applies the same sparse-memory requirement check ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L257-L258), [`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L158-L165)).

### cube_array — cube-array sparse image mip-tail alignment

The `cube_array` child uses `256x256x6` and relies on shared layer-count logic where cube arrays map to `imageSize.z() * 6` layers ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L258-L280), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L196-L200)).

### 3d — 3D sparse image mip-tail alignment

The `3d` child uses `512x256x16`, maps to `VK_IMAGE_TYPE_3D`, and requires device sparse residency support for 3D images through shared support helpers ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L259-L280), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L390-L407), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L1186-L1203)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct children | `2d`, `2d_array`, `cube`, `cube_array`, and `3d` are registered by the `imageParameters` vector and image-type group creation ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L266)). |
| Image sizes | One base size per image type: `512x256x1`, `512x256x6`, `256x256x1`, `256x256x6`, and `512x256x16` ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L259)). |
| Formats | All shared sparse test formats for the image type, including extra YCbCr formats only for 2D and 2D array in `getTestFormats()` ([`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)). |
| Generated leaves | Leaves are named by `getImageFormatID(format)` and are skipped when the image size is not compatible with format alignment ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L267-L280)). |

## Support / Feature Requirements

The case checks image size limits, sparse support for the image type, and R64 sparse-image int64 atomic support when the format is `VK_FORMAT_R64_SINT` or `VK_FORMAT_R64_UINT` ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L85-L107), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L40-L50)). During iteration, it checks sparse support for the concrete image format, queries image format properties, computes mip levels, and creates a device with a sparse-binding queue ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L163-L186)).

## Verification Methods

The test queries `VkSparseImageMemoryRequirements` for the color aspect, records `formatProperties.imageGranularity`, and compares the calculated first non-aligned LOD with `imageMipTailFirstLod` when `residencyAlignedMipSize` is enabled ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L188-L229)). When `residencyAlignedMipSize` is disabled, the test fails if the image format still reports `VK_SPARSE_IMAGE_FORMAT_ALIGNED_MIP_SIZE_BIT`; otherwise it passes with the property disabled ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L233-L239)).

## Test Principles Observed

- This file verifies sparse-image metadata and device-property consistency rather than rendering or copying image contents ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L211-L239)).
- Registration uses a compact image-type × format matrix with one image size per type ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L283)).

## Notes / Uncertainties

- No nested registered source files were discovered for `aligned_mip_size`; shared helpers provide image names, format lists, and sparse support checks but do not register this root independently ([`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L95-L115)).
