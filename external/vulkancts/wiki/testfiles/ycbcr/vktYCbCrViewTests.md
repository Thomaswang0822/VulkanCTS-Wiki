# vktYCbCrViewTests.cpp

## Overview

[`vktYCbCrViewTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp) implements the `ycbcr.plane_view` subgroup returned by [`createViewTests()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1075-L1078). It compares whole-image YCbCr sampling with plane-level sampling through either plane image views or memory-alias images in [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L595-L860).

## Registration Hierarchy

```text
ycbcr.plane_view
├── image_view
└── memory_alias
```

[`populateViewGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1065-L1070) creates the direct `image_view` and `memory_alias` children. [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L1062) then expands each child into format, plane, shader, descriptor, and compatible-format cases.

## Test Families

### image_view

`image_view` cases create a `VkImageView` with `VK_IMAGE_ASPECT_PLANE_N_BIT` on the original multi-planar image in [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L613-L642).

### memory_alias

`memory_alias` cases create a separate image for the plane-compatible format and bind it to the plane memory in [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L613-L642). Both view families create a whole-image view with a `VkSamplerYcbcrConversion` and a plane view without conversion in [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L645-L675).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Formats | The generator iterates `VK_YCBCR_FORMAT_FIRST` to `VK_YCBCR_FORMAT_LAST` and the 2-plane 444 EXT range up to but not including `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT` in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1053-L1062). |
| Plane index | All planes from `0` to `getPlaneCount(format)-1` are generated in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1005-L1020). |
| Compatible format | The native plane-compatible format is always tested, and additional formats are added when `formatsAreCompatible()` accepts them in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1028-L1046). |
| Descriptor mode | Descriptor-set, descriptor-buffer, and descriptor-heap variants are generated where executor-supported in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L991-L1026) and executed in [`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L757-L842). |
| View flags | `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is always included, `VK_IMAGE_CREATE_ALIAS_BIT` is added for memory aliases, and `VK_IMAGE_CREATE_DISJOINT_BIT` is varied in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L987-L1017). |

## Support / Feature Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L486-L500) delegates YCbCr image support to shared [`checkImageSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L176-L201), requires sampled-image/transfer-destination/midpoint features for the YCbCr format, sampled-image/transfer-destination features for the plane-compatible format, shader support, and `VK_EXT_descriptor_buffer` or `VK_EXT_descriptor_heap` for those descriptor modes.

## Verification Method

[`testPlaneView()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L806-L860) samples 500 generated coordinates, produces whole-image and plane-view shader outputs, builds software references from `tcu::Texture2DView::sample()`, and uses a `0.02f` threshold; the descriptor path can use descriptor sets, `executeBuffer()`, or `executeHeap()` depending on the generated mode.

## Notes / Uncertainties

Memory-alias tests are source-filtered to disjoint images only, as shown by the generator's `continue` for non-disjoint memory-alias cases in [`populateViewTypeGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1016-L1017).
