# vktPipelineRenderToImageTests.cpp

## Overview

[`vktPipelineRenderToImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1) implements the [`render_to_image`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L2029) topic group. It verifies rendering to image attachments across all view types, formats, and sizes, including maximum-dimension images and mipmap rendering.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineRenderToImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1)
- Header: [`vktPipelineRenderToImageTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.hpp#L1)

## Registration Path

[`createRenderToImageTests()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L2026) returns the `render_to_image` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
render_to_image
├── core
│   └── {1d,1d_array,2d,2d_array,3d,cube,cube_array}
│       ├── small/<colorFormat>_<dsFormat>
│       ├── huge/<sizeDescription>/<colorFormat>_<dsFormat>
│       └── mipmap/<colorFormat>_<dsFormat>
└── dedicated_allocation
    └── (same structure, no huge tests)
```

## Test Families

### 1. core / small

Baseline image sizes with all color/DS format combinations. For 3D, includes `_2d_compatible` variants (VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT + VK_KHR_maintenance9).

### 2. core / huge

Maximum-dimension images. Only R8G8B8A8_UNORM color format. Verification region capped to 32x8.

### 3. core / mipmap

Renders to each mip level sequentially, verifies all levels.

### 4. dedicated_allocation

Same as core but using VK_KHR_dedicated_allocation. No huge tests.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkImageViewType | Array | 7 types |
| colorFormat | Array | 8 formats (R8G8B8A8_UNORM, R32_UINT, R16G16_SINT, etc.) |
| depthStencilFormat | Array | 5 formats (UNDEFINED, D16_UNORM, S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT) |
| AllocationKind | [Enum](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L94) | SUBALLOCATED, DEDICATED |
| maintenance9 | bool | false/true (3D 2d_compatible only) |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_maintenance1` | 3D view type |
| `VK_KHR_dedicated_allocation` | Dedicated allocation |
| `VK_KHR_maintenance9` | 3D 2d_compatible tests |
| `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY` | CUBE_ARRAY view type |
| Format support | Verified via getPhysicalDeviceImageFormatProperties |

## Verification Methods

- **Small/huge**: Renders colored geometry to each layer via multi-subpass render pass, copies result, compares against expected image using `tcu::floatThresholdCompare` (threshold 0.01f for float) or `tcu::intThresholdCompare` (threshold UVec4(2) for integer) ([line 1285](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1285))
- **Mipmap**: Same comparison per mip level ([line 1774](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1774))
- **Huge**: Size reduction retry on allocation failure; verification region capped

## Notes / Uncertainties

- 3D view type gets extra `_2d_compatible` tests with VK_KHR_maintenance9
- VulkanSC filters out huge sizes where both width and height are MAX_SIZE
