# vktPipelineImage2DViewOf3DTests.cpp

## Overview

[`vktPipelineImage2DViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1) implements the [`image_2d_view_3d_image`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1017) topic group. It verifies VK_EXT_image_2d_view_of_3d functionality, testing 2D image views of 3D images via storage, sampler, and combined image sampler descriptors.

## Role

Implementation file. The [`createImage2DViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1014) factory function creates the `image_2d_view_3d_image` group, attached directly under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L123).

## Source Code

- Primary source: [`vktPipelineImage2DViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1)
- Header: [`vktPipelineImage2DViewOf3DTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.image_2d_view_3d_image
├── compute (monolithic only)
└── fragment
```

**Variant coverage**: All Vulkan variants; excluded from VulkanSC by the `#ifndef CTS_USES_VULKANSC` guard in the dispatcher. The `compute` subgroup is only populated for monolithic pipeline construction type.

## Test Families

### compute — Compute shader 2D view of 3D image (monolithic only)

Tests 2D image view of 3D image via compute shader dispatch. Contains three descriptor access type subgroups: `storage` (imageStore/imageLoad), `sampler` (separate sampled image + sampler), and `combined_image_sampler`. Each subgroup contains leaf test cases for mip levels {0, 2} and first/last layer per mip level, with normal and sparse binding variants.

### fragment — Fragment shader 2D view of 3D image

Tests 2D image view of 3D image via fragment shader in a graphics pipeline. Contains the same three descriptor access type subgroups as `compute`: `storage`, `sampler`, and `combined_image_sampler`, with the same mip/layer/sparse parameterization.

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
