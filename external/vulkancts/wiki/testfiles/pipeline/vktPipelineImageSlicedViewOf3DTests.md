# vktPipelineImageSlicedViewOf3DTests.cpp

## Overview

[`vktPipelineImageSlicedViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1) implements the [`sliced_view_of_3d_image`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L980) topic group. It verifies VK_EXT_image_sliced_view_of_3d functionality, testing sliced views of 3D images with various depth offsets, ranges, and mip levels.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineImageSlicedViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1)
- Header: [`vktPipelineImageSlicedViewOf3DTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.hpp#L1)

## Registration Path

[`createImageSlicedViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L978) returns the `sliced_view_of_3d_image` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Monolithic only (no PipelineConstructionType parameter).

## Test Hierarchy

```text
sliced_view_of_3d_image
├── basic
│   └── {load,store}/{comp,frag}/{offset_0[_with_sampling], offset_1[_with_sampling]}
├── full_slice
│   └── {load,store}/{comp,frag}[_with_sampling]
├── random
│   └── {load,store}/{comp,frag}/depth_N_offset_N_range_N
└── mip_level
    └── {load,store}/{comp,frag}/level_N/offset_N_range_N
```

## Test Families

### 1. basic

Depth=2, range=1, tests view of first or second slice individually.

### 2. full_slice

Depth=4, range=full depth, tests a sliced view covering the entire 3D image.

### 3. random

Pseudorandom depth (10-32), offset, and range values. Includes VK_REMAINING_3D_SLICES_EXT cases.

### 4. mip_level

Fixed 8x8x8 image with full mip chain. Tests sliced views at non-zero mip levels.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| TestType | [Enum](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L67) | LOAD, STORE |
| Stage | VkShaderStageFlagBits | COMPUTE_BIT, FRAGMENT_BIT |
| depth | Per family | 2 (basic), 4 (full_slice), 10-32 (random), 8 (mip_level) |
| offset | Per case | 0..depth-1 |
| range | Per case | 1..full depth, VK_REMAINING_3D_SLICES_EXT |
| mipLevel | tcu::Maybe | Nothing (no mip) or just(level) |
| sampleImg | bool | false/true (basic and full_slice only) |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_EXT_image_sliced_view_of_3d` | Always |
| `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` | Fragment stage |

## Verification Methods

Integer threshold comparison with zero threshold (exact match). LOAD: fills auxiliary buffer, copies to 3D image at slice offset, reads via sliced view, compares. STORE: writes to sliced view, copies full image slice region, compares. Shader also verifies `imageSize(slicedImage).z == actualRange` ([line 842](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L842)).
