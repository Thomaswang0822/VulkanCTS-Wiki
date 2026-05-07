# vktPipelineImageViewTests.cpp

## Overview

[`vktPipelineImageViewTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1) implements the [`image_view`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L941) topic group. It verifies image view parameters including component swizzle and subresource range selection across all view types and formats.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineImageViewTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1)
- Header: [`vktPipelineImageViewTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.hpp#L1)
- Shared instance: [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1)

## Registration Path

[`createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L760) returns the `image_view` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Monolithic or base ESO only.

## Test Hierarchy

```text
image_view
└── view_type
    └── {1d,1d_array,2d,2d_array,3d,cube,cube_array}
        └── format/<format>
            ├── component_swizzle/<4 channel rotation permutations>
            └── subresource_range/<mip/array/combined/remaining range cases>
```

## Test Families

### 1. component_swizzle

Tests 4 channel rotation permutations of VkComponentMapping (RGBA identity rotated). The shader applies the swizzle to lookup scale/bias values; reference comparison accounts for swizzle.

### 2. subresource_range

Tests VkImageSubresourceRange parameters: baseMipLevel, mipLevels, baseArrayLayer, arraySize, VK_REMAINING_*. Uses `textureLod()` with specific LOD values to verify correct mip level selection. Cases vary by view type (3D has no array-only; cube uses 6-face granularity).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkImageViewType | Array | 7 types |
| VkFormat | Array | ~90 formats (packed, 8/16/32-bit, compressed, ASTC 3D for 3D only) |
| ComponentMapping | Permutation array | 4 rotations of identity |
| SubresourceRange | Per view type | Mip ranges, array ranges, combined, VK_REMAINING_* |

## Verification Methods

Same rendering-based verification as Image tests via `ImageSamplingInstance`, with format-aware thresholds. Each leaf test has a `_compute` variant.

## Notes / Uncertainties

- Subresource range test cases vary significantly by view type
- ASTC 3D formats only for VK_IMAGE_VIEW_TYPE_3D (non-VulkanSC)
