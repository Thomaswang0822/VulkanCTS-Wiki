# vktPipelineImage2DViewOf3DTests.cpp

## Overview

[`vktPipelineImage2DViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1) implements the [`image_2d_view_3d_image`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1017) topic group. It verifies VK_EXT_image_2d_view_of_3d functionality, testing 2D image views of 3D images via storage, sampler, and combined image sampler descriptors.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineImage2DViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1)
- Header: [`vktPipelineImage2DViewOf3DTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.hpp#L1)

## Registration Path

[`createImage2DViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1014) returns the `image_2d_view_3d_image` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants (VulkanSC only). Compute sub-group is monolithic only.

## Test Hierarchy

```text
image_2d_view_3d_image
├── compute                              (monolithic only)
│   ├── storage
│   │   └── {mip0_layer0, mip0_layer0_sparse, mip0_layer63, ...}
│   ├── sampler
│   └── combined_image_sampler
└── fragment
    ├── storage
    ├── sampler
    └── combined_image_sampler
```

## Test Families

### 1. compute (monolithic only)

Tests 2D image view of 3D image via compute shader dispatch.

### 2. fragment

Tests 2D image view of 3D image via fragment shader in a graphics pipeline.

### 3. storage / sampler / combined_image_sampler

Three descriptor access types: storage image (imageStore/imageLoad), separate sampled image + sampler, and combined image sampler.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| ImageAccessType | [Enum](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L59) | StorageImage, Sampler, CombinedImageSampler |
| ImageBindingType | [Enum](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L66) | Normal, Sparse |
| mipLevel | Loop | {0, 2} |
| layerNdx | Loop | First and last layer per mip level |
| imageSize | Constant | (64, 64, 64) |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_EXT_image_2d_view_of_3d` + `image2DViewOf3D` | Always |
| `sampler2DViewOf3D` | When not StorageImage |
| `fragmentStoresAndAtomics` | Fragment tests |
| `DEVICE_CORE_FEATURE_SPARSE_BINDING` + `VK_KHR_maintenance9` | Sparse binding |

## Verification Methods

Chess pattern comparison: writes/uploads chess pattern to 3D image, accesses via 2D view, compares result against reference using `tcu::floatThresholdCompare` with threshold 0.01f ([line 796](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L796)).
