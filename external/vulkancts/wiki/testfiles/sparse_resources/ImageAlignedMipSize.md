## Overview

**Core question:** Does the implementation report a sparse image mip-tail boundary that agrees with the device's aligned-mip-size property and the image's sparse block granularity?

- This page covers the implementation in [`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L56-L73).
- The test registers `sparse_resources.aligned_mip_size` and checks five image-type families. Each family combines one fixed base extent with the formats returned by `getTestFormats()`.
- The test creates a sparse-residency, sparse-binding image, queries its sparse memory requirements, and compares the calculated first non-aligned mip level with `imageMipTailFirstLod` when `residencyAlignedMipSize` is enabled.

## Background Knowledge

- A sparse image divides its mip levels into individually bindable regions and a mip tail. For sparse residency, a mip level whose extent is not an integer multiple of the sparse image block dimensions, together with later levels, belongs to the mip tail. See [Vulkan sparse memory, Mip Tail Regions](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-miptail).
- `imageGranularity` gives the sparse image block dimensions for a format and image configuration. The `VK_SPARSE_IMAGE_FORMAT_ALIGNED_MIP_SIZE_BIT` format flag and the physical-device `residencyAlignedMipSize` property describe related parts of this layout rule; the test checks that they agree.

## Registration Hierarchy

```text
sparse_resources.aligned_mip_size
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

Each child contains format-named test cases. The source skips a format when the fixed extent is not compatible with that format's required image-size alignment.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects the Vulkan image type, layer mapping, and base extent used for the sparse layout query. | [`createImageAlignedMipSizeTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L250-L266) |
| Base extent | `512x256x1`, `512x256x6`, `256x256x1`, `256x256x6`, `512x256x16` | Supplies the dimensions from which the test derives mip levels. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L259) |
| Format | The entries from `getTestFormats()` for the selected image type | Changes format properties, sparse support, block granularity, and the generated test-case name. | [`getTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) |
| Format-alignment filter | Format-dependent `getImageSizeAlignment(format)` values | Removes 2D cases whose fixed width or height is not compatible with the format alignment. | [`getImageSizeAlignment` filtering](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L267-L280) |

## Behavior Parameters

The primary behavioral axis is the registered image-type test family. The format is a secondary dimension within each family and uses the same check.

### `2d` : 2D image

The test uses a `512x256x1` extent and one array layer. It creates a `VK_IMAGE_TYPE_2D` sparse image for each supported, alignment-compatible format.

### `2d_array` : 2D array image

The test uses a `512x256x1` image extent with six array layers. The six layers are represented by `arrayLayers`, while the sparse mip-tail check remains the same as for a 2D image.

### `cube` : cube image

The test uses `256x256x1` and adds `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`. The shared layer mapping represents the cube's six faces when the image is created and its sparse requirements are queried.

### `cube_array` : cube-array image

The test uses `256x256x6` and the cube-compatible flag. The helper maps the six cube faces for each array element before the test obtains sparse memory requirements.

### `3d` : 3D image

The test uses a `512x256x16` extent and `VK_IMAGE_TYPE_3D`. The depth dimension participates in both mip extent calculation and the granularity divisibility test.

## Shader Analysis

This test has no shader. It validates image metadata and physical-device sparse properties on the host side.

## Runtime Execution and Result Checking

- `checkSupport()` rejects an extent outside device limits or an image type without sparse residency support. For `VK_FORMAT_R64_SINT` and `VK_FORMAT_R64_UINT`, it also requires `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`.
- The instance configures `VkImageCreateInfo` with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT | VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, optimal tiling, one sample, and transfer-source plus storage usage. Cube types also receive `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`.
- The test checks sparse support for the concrete format and image configuration, queries image format properties, calculates the mip-level count, and creates a device with a `VK_QUEUE_SPARSE_BINDING_BIT` queue.
- After creating the image, it obtains `VkSparseImageMemoryRequirements` and selects the `VK_IMAGE_ASPECT_COLOR_BIT` requirement. It records `formatProperties.imageGranularity`.
- When `residencyAlignedMipSize` is `VK_TRUE`, the test starts at LOD 0, computes each mip extent with `mipLevelExtents()`, and stops at the first extent whose width, height, or depth is not divisible by the corresponding granularity component. It passes only when that LOD equals `imageMipTailFirstLod`.
- When `residencyAlignedMipSize` is `VK_FALSE`, the test passes only if the format properties do not contain `VK_SPARSE_IMAGE_FORMAT_ALIGNED_MIP_SIZE_BIT`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `2d` | The reported 2D sparse format properties, mip-tail boundary, granularity, or device property do not agree. |
| `2d_array` | The reported 2D-array sparse metadata or mip-tail boundary does not agree with the device property and calculated extents. |
| `cube` | The cube-compatible image's sparse metadata or mip-tail boundary is inconsistent. |
| `cube_array` | The cube-array sparse metadata or layer-aware mip-tail boundary is inconsistent. |
| `3d` | The 3D sparse metadata or depth-aware mip-tail boundary is inconsistent. |
| Any format within a family | The concrete format's sparse support, format flag, granularity, or returned mip-tail LOD is inconsistent with the device property. |

### Cause Analysis

#### Sparse property and format-flag mismatch

**Possible failure symptoms:** With `residencyAlignedMipSize` disabled, the test reports `Aligned mip size flag doesn't match in device and image properties.`

**Possible implementation causes:** The physical-device sparse property and the format's `VK_SPARSE_IMAGE_FORMAT_ALIGNED_MIP_SIZE_BIT` do not describe the same supported behavior. The exact implementation cause needs source-level investigation.

#### Incorrect first mip-tail LOD

**Possible failure symptoms:** With `residencyAlignedMipSize` enabled, the calculated first non-aligned LOD differs from `imageMipTailFirstLod`, producing `Unexpected first LOD for mip tail.`

**Possible implementation causes:** The implementation may return inconsistent sparse image granularity or mip-tail metadata, or may apply the aligned-mip-size rule incorrectly for the selected image type and format. The test does not identify whether the discrepancy originates in the device, driver, or host-side query handling.

## Case Pruning

### Requirement-based pruning

- The test skips unsupported image extents and image types through `isImageSizeSupported()` and `checkSparseSupportForImageType()`.
- It skips formats without sparse support for the complete image configuration and formats rejected by `vkGetPhysicalDeviceImageFormatProperties`.
- It skips `VK_FORMAT_R64_SINT` and `VK_FORMAT_R64_UINT` unless the required int64 sparse-image atomic functionality is available.
- It skips configurations for which the queried requirements do not include a color-aspect entry.

### Design-based pruning

- The registration table fixes one base extent for each image type instead of generating a size matrix.
- The source omits formats whose required width or height alignment does not divide the selected extent. This is especially relevant to the additional YCbCr formats used for 2D and 2D-array families.

## Key Takeaways

- The test checks the relationship between `residencyAlignedMipSize`, `VK_SPARSE_IMAGE_FORMAT_ALIGNED_MIP_SIZE_BIT`, sparse image granularity, and `imageMipTailFirstLod`.
- It does not bind memory, render, dispatch, or inspect image contents. The result comes from image creation metadata and sparse memory requirements.
- The same rule is exercised across 2D, array, cube, cube-array, and 3D image types; 3D cases also test the depth component of the mip extent.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `ImageAlignedMipSizeCase::checkSupport` | [`vktSparseResourcesImageAlignedMipSize.cpp#L85-L107`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L85-L107) | Device limits, sparse image-type support, and R64 requirements. |
| `ImageAlignedMipSizeInstance::iterate` image setup | [`vktSparseResourcesImageAlignedMipSize.cpp#L132-L186`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L132-L186) | Image creation parameters, format checks, mip count, and queue setup. |
| `ImageAlignedMipSizeInstance::iterate` validation | [`vktSparseResourcesImageAlignedMipSize.cpp#L188-L240`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L188-L240) | Sparse requirement query and pass/fail logic. |
| Test registration | [`vktSparseResourcesImageAlignedMipSize.cpp#L250-L285`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L250-L285) | Image-type, extent, format, and alignment-filter matrix. |
| Sparse format inventory | [`vktSparseResourcesTestsUtil.cpp#L52-L118`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Formats used by each image-type family. |
| Image layer mapping | [`vktSparseResourcesTestsUtil.cpp#L158-L205`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L158-L205) | Array and cube layer handling. |
| Sparse mip-tail rules | [Vulkan sparse memory, Mip Tail Regions](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-miptail) | Specification background for the aligned mip-size property and mip-tail boundary. |
