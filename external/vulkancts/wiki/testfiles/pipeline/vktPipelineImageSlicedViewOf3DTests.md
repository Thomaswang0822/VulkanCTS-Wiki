# vktPipelineImageSlicedViewOf3DTests.cpp

## Overview

[`vktPipelineImageSlicedViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1) implements the [`sliced_view_of_3d_image`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L980) topic group. It verifies VK_EXT_image_sliced_view_of_3d functionality, testing sliced views of 3D images with various depth offsets, ranges, and mip levels.

## Role

Implementation file. The [`createImageSlicedViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L978) factory function creates the `sliced_view_of_3d_image` group, attached directly under the monolithic variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L208).

## Source Code

- Primary source: [`vktPipelineImageSlicedViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1)
- Header: [`vktPipelineImageSlicedViewOf3DTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.sliced_view_of_3d_image
├── basic
├── full_slice
├── random
└── mip_level
```

**Variant coverage**: Monolithic only (no PipelineConstructionType parameter).

## Test Families

### basic — Basic sliced view tests

Depth=2, range=1, tests view of first or second slice individually. Contains `load` and `store` test type subgroups, each with `comp` and `frag` stage subgroups. Leaf test cases vary offset (0 or 1) and optional sampling suffix.

### full_slice — Full-depth sliced view tests

Depth=4, range=full depth, tests a sliced view covering the entire 3D image. Contains `load` and `store` test type subgroups, each with `comp` and `frag` stage subgroups. Leaf test cases include optional sampling suffix.

### random — Random parameter sliced view tests

Pseudorandom depth (10-32), offset, and range values. Includes VK_REMAINING_3D_SLICES_EXT cases. Contains `load` and `store` test type subgroups, each with `comp` and `frag` stage subgroups. Leaf test cases have names encoding depth, offset, and range values.

### mip_level — Mip-level sliced view tests

Fixed 8x8x8 image with full mip chain. Tests sliced views at non-zero mip levels. Contains `load` and `store` test type subgroups, each with `comp` and `frag` stage subgroups. Leaf test cases vary mip level, offset, and range.

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
