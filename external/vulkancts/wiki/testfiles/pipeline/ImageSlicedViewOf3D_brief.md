# Understanding Brief: ImageSlicedViewOf3D

## One-Sentence Test Purpose

This test checks whether `VK_EXT_image_sliced_view_of_3d` makes a storage-image view address the selected subset of slices from a 3D image, including mip levels and `VK_REMAINING_3D_SLICES_EXT`.

## Background Knowledge

### A sliced 3D image view

`VkImageViewSlicedCreateInfoEXT` adds `sliceOffset` and `sliceCount` to a 3D image view. Shader Z coordinate 0 refers to the first selected slice, and the view's depth is the selected count. The view covers one mip level. The extension feature applies when the view is used through a `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` descriptor. See [the Vulkan resource rules](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext) and [the feature description](../../../../vulkan-docs/src/chapters/features.adoc#_vk_physical_device_image_sliced_view_of_3d_features_ext).

`VK_REMAINING_3D_SLICES_EXT` means all slices from the offset to the end of the selected mip level. The CTS must therefore convert the sentinel to an actual depth when it sizes dispatches, copies, and checks `imageSize`.

## One Concrete Example

For `pipeline.monolithic.sliced_view_of_3d_image.basic.load.comp.offset_1`, the host creates an 8x8x2 `VK_FORMAT_R8G8B8A8_UINT` image and a view with offset 1 and count 1. It copies reference pixels into slice 1. A compute shader reads the storage view at local XY coordinates and writes the values to an auxiliary 8x8x1 image. The host compares the auxiliary image with the reference buffer.

For a store case, the auxiliary image supplies the reference pixels, the shader writes through the sliced view, and the host copies the corresponding parent-image slice back for comparison.

## End-to-End Test Flow

```text
[host] choose load/store, compute/fragment, depth, offset, range, mip level, and optional sampling
[host] create the full 3D image, sliced view, auxiliary image, descriptors, and reference/readback buffers
[host] initialize the source data and transition images to VK_IMAGE_LAYOUT_GENERAL
[host] submit compute dispatch or instanced full-screen triangle rendering
[device] read from or write to the storage image view; the shader checks imageSize(slicedImage).z
[host] copy the result region to a host-visible buffer and wait for completion
[host] compare reference and result with a zero threshold; optionally compare sampled full-level data
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates GLSL for compute or vertex/fragment execution. The main shader binds two `rgba8ui` storage images. An optional compute shader samples the selected view through a combined image sampler.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Full 3D image | yes | through sliced or sampling view | read or written | indirectly | Parent image whose Z range is restricted |
| Sliced image view | yes | storage image, and optionally sampled image | read or written | no | Carries slice offset, count, and mip level |
| Auxiliary image | yes | storage image | opposite side of load/store operation | copied to buffer | Provides reference input or receives load output |
| Reference/readback buffers | yes | transfer source or destination | copied by device | yes | Supplies expected pixels and captures results |

## What Is Checked

- The shader writes `goodColor` only when `imageSize(slicedImage).z` equals the computed effective range. Otherwise it writes zero.
- Load cases compare pixels read through the sliced view with the source data copied into the selected parent-image region.
- Store cases compare the selected parent-image region with the source data read from the auxiliary image.
- Optional sampling cases sample the full selected mip level and compare it with a direct copy from the parent image.
- All image comparisons use `tcu::intThresholdCompare` with `(0, 0, 0, 0)`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `load`, `store`

The `load` and `store` families reverse the data direction across the sliced view. Stage, depth, range, mip level, and sampling configure that operation but do not define a separate core operation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `load` | The sliced storage-image view may expose the wrong parent-image slices, mip level, or effective depth when shaders read it. |
| `store` | Writes through the sliced storage-image view may land in the wrong parent-image slices or mip level, or may not update the selected region. |
| Either family | Descriptor, image-layout, synchronization, copyback, or host-comparison handling may prevent the expected data from reaching the comparison. |

## Important Variations and Special Cases

- `basic` uses depth 2 and one-slice views at offsets 0 and 1.
- `full_slice` uses depth 4 and a view covering all slices.
- `random` generates five depths in the 10 to 32 range and five distinct offset/range cases per depth, including remaining-slice cases.
- `mip_level` uses an 8x8x8 image and samples two generated offset/range cases at each mip level from 0 through 3.
- Compute and fragment paths exercise the same storage-image operation with different invocation generation. Fragment cases require `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameter helpers | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L71-L188) | Defines effective mip depth, range, and slice extent |
| Shader generation | [`SlicedViewTestCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L283-L378) | Generates storage-image and sampling shaders |
| Load execution | [`SlicedViewLoadTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L742-L857) | Initializes, dispatches, copies, and compares load results |
| Store execution | [`SlicedViewStoreTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L859-L972) | Initializes, dispatches, copies, and compares store results |
| Registration | [`createImageSlicedViewOf3DTests`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L978-L1223) | Builds the four test families and generated leaves |
| Vulkan contract | [`VkImageViewSlicedCreateInfoEXT`](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext) | Defines offset, count, mip, and storage-image semantics |

## Questions / Risk Points for User Audit

- Does the load/store distinction make the data direction clear?
- Is the sentinel range conversion clear enough for mip-level cases?
- Should the optional sampling path receive a separate walkthrough in the final page?

## Conversion Notes for Final Wiki Rewrite

Use the test family as the primary behavior axis and carry the failure table directly into the Level-3 page. Keep the brief's concrete example as a compact load/store comparison. The final page should place generated shader details under `Shader Analysis`, host setup under runtime execution, and source links in the appendix.
