## Overview

**Core question:** Does the implementation report the standard sparse image block shape for each tested image format and sample count?

- The `image_block_shapes` test family creates sparse images for 2D, 2D array, cube, cube array, and 3D image types.
- It queries `VkSparseImageMemoryRequirements` and compares each reported `imageGranularity` with the standard block-shape table selected by image type, sample count, and format size.
- The matrix includes shared sparse test formats plus BC, ETC2/EAC, and ASTC compressed formats. YCbCr 4:2:2 formats receive their format block extent adjustment.
- This page describes the registered hierarchy, the generated matrix, support checks, comparison rules, and the meaning of a mismatch.

## Background Knowledge

- A sparse image divides its storage into implementation-defined granularity units. The standard sparse block-shape properties in `VkPhysicalDeviceSparseProperties` require specific granularity tables when enabled.
- Compressed and multi-plane formats describe data in blocks or planes rather than as one uncompressed texel stream. The test converts the applicable standard shape to image-space extents before comparing it with the queried requirement.

## Registration Hierarchy

```text
sparse_resources.image_block_shapes
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

Each image-type test family contains a format intermediate node and `samples_<count>` test case leaves. The source registers all five sample-count values, then omits multisample leaves for image types other than `2d` and `2d_array`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type test family | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects the standard block-shape table and image geometry. | [`createImageBlockShapesTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L528-L545) |
| Image size | `512x256x1`, `512x256x6`, `256x256x1`, `256x256x6`, `512x256x16` | Supplies the extent and, for array or cube types, the layer count. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L532-L537) |
| Format | Shared sparse formats plus BC, ETC2/EAC, and ASTC block-compressed formats | Determines plane size, compressed block dimensions, and YCbCr block extent adjustments. | [`getImageTestFormats()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L488-L525) |
| Sample count | `1`, `2`, `4`, `8`, `16` | Selects the single-sample or multisample 2D table. | [`sampleCounts`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L539-L579) |
| Image format alignment | Format-dependent | Removes YCbCr cases whose fixed image size does not satisfy the format's width or height alignment. | [`createImageBlockShapesTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L561-L569) |

The image sizes are fixed per image type. Cube and cube-array images set `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`. The source still creates `samples_2`, `samples_4`, `samples_8`, and `samples_16` during the generic loop, but skips them for `cube`, `cube_array`, and `3d`.

## Behavior Parameters

The primary behavioral axis is the image type and sample-count combination because it selects which standard sparse property and granularity table the test applies. Format changes the pixel-size and block-extent inputs to that table.

### `2d`, one sample: standard 2D block shape

The test uses `residencyStandard2DBlockShape` and selects a width and height from the uncompressed pixel-size class. It then applies compressed-format or YCbCr block extents before comparing the queried granularity.

### `2d` and `2d_array`, multiple samples: standard multisample block shape

For sample counts `2`, `4`, `8`, and `16`, the test uses `residencyStandard2DMultisampleBlockShape`. Each sample count has its own table for the 8, 16, 32, 64, and 128 bits-per-pixel classes. The depth is one for these 2D cases.

### `cube` and `cube_array`, one sample: standard 2D block shape

These image types use the single-sample 2D table. The cube-compatible creation flag and layer expansion affect image creation, but the source does not generate multisample cube cases.

### `3d`, one sample: standard 3D block shape

The test uses `residencyStandard3DBlockShape`. The table supplies width, height, and depth for the same pixel-size classes, so the depth comparison checks the 3D sparse granularity as well.

## Shader Analysis

No shader code participates in this test. The implementation checks image metadata and does not inspect shader-visible image contents.

## Runtime Execution and Result Checking

- The host checks the image size, sparse support for the image type, and the feature bit associated with the requested sample count. For R64 formats it also requires `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`.
- The host builds an optimal-tiled image with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, and adds the cube-compatible flag for cube image types. It checks image-format support, sample-count support, sparse-format support, and availability of a queue with `VK_QUEUE_SPARSE_BINDING_BIT`.
- The test creates the image and obtains its `VkSparseImageMemoryRequirements`. It selects the color aspect for single-plane formats or the matching plane aspect for multi-plane formats.
- It computes the expected granularity from the image type, sample count, and plane or format element size. Compressed formats multiply the width and height by their block dimensions. YCbCr 4:2:2 formats multiply them by the format block extent.
- The case passes when the reported width, height, and depth exactly match the expected values. If the relevant standard block-shape property is disabled, the case returns pass without enforcing that table.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d`, one sample | The reported 2D sparse granularity does not match the standard table after format adjustments. |
| `2d` or `2d_array`, samples `2`, `4`, `8`, or `16` | The reported multisample sparse granularity does not match the table for the requested sample count and pixel-size class. |
| `cube` or `cube_array`, one sample | The cube-compatible image reports a non-standard single-sample 2D granularity. |
| `3d`, one sample | The reported 3D sparse granularity, including depth, does not match the standard table. |

### Cause Analysis

#### Reported granularity differs from the standard shape

**Possible failure symptoms:** The case returns `Non-standard block shape used` because one of the reported width, height, or depth values differs from the computed expectation.

**Possible implementation causes:** The implementation may expose an incorrect sparse block shape for the selected image type, sample count, format plane size, compressed block dimensions, or YCbCr block extent. The exact driver or hardware cause requires source-level investigation.

#### Unsupported case

**Possible failure symptoms:** The case is reported as not supported during image-size, feature, format, sparse-support, or queue checks rather than reaching the comparison.

**Possible implementation causes:** The device may lack the required sparse residency feature, image-format/sample-count combination, sparse image support, queue capability, or R64 sparse-image atomic functionality. These checks define the legal execution set and do not indicate a block-shape mismatch.

## Case Pruning

### Requirement-based pruning

- The test rejects image sizes that exceed device limits.
- It skips or reports unsupported image types, formats, sample counts, sparse operations, and queue capabilities through the support checks.
- R64 formats require `VK_EXT_shader_image_atomic_int64` with `sparseImageInt64Atomics` enabled.
- YCbCr cases whose fixed width or height does not satisfy the format alignment are skipped.

### Design-based pruning

- The source tests multisample images only for `2d` and `2d_array`; cube, cube-array, and 3D cases use one sample.
- Each image type uses one fixed extent, so the matrix focuses on standard block-shape selection rather than image-size variation.
- The format list adds block-compressed formats because their block dimensions affect the image-space granularity comparison.

## Key Takeaways

- The test validates the metadata returned by `VkSparseImageMemoryRequirements`, not sparse image contents.
- Sample count selects the multisample table only for 2D image types. Image type selects between the standard 2D and 3D tables.
- Compressed and YCbCr formats are compared after converting the table result to their format block extents.
- A pass with a disabled standard block-shape property means the test did not enforce that property, not that the implementation matched the table.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|------------|------|----------------|
| Test registration and matrix generation | [`createImageBlockShapesTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L528-L587) | Defines image types, extents, formats, sample counts, alignment filtering, and registered test case leaves. |
| Device support checks | [`ImageBlockShapesCase::checkSupport()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L87-L137) | Checks image limits, sparse features, sample-count support, and R64 atomic requirements. |
| Image creation and sparse requirement query | [`ImageBlockShapesInstance::iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L165-L248) | Creates the sparse image, checks format support, and selects image aspects for comparison. |
| Standard granularity tables and comparison | [`ImageBlockShapesInstance::iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L259-L478) | Computes expected 2D, multisample, and 3D shapes, applies format extents, and returns the result. |
| Shared image and format helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L78-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies shared sparse image types, formats, layer handling, and format information. |
| Vulkan API test-plan entry | [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276) | Places sparse resources in the Vulkan API test plan. |
