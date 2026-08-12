# ImageSparseResidency understanding brief

- **What it tests:** Sparse image residency for 2D, array, cube, cube-array, and 3D images, plus regular-group tests for mutable-format image views.
- **How residency is exercised:** The test binds alternating sparse blocks, writes coordinate-derived values with compute shaders, reads each image plane back, and checks resident data. Strict devices must return zeroes for nonresident blocks.
- **Group difference:** `image_sparse_residency` has six children, including `mutable`; `device_group_image_sparse_residency` has the five image-type children and uses device-group sparse-bind metadata.
- **Main parameters:** Image dimensions vary by image type. Formats come from the shared sparse test format list, with an applicable `VK_FORMAT_A8_UNORM_KHR` case outside device-group mode.
- **Feature gates:** Cases need sparse image support, sparse binding, a compute queue, storage-image support, suitable memory, and enough sparse address space. Extra feature checks cover A8 write-without-format support and R64 shader and atomic support.
- **Validation:** Regular cases use format-aware channel checks. Mutable cases compare copied regions against generated integer or floating-point reference images.

## Behavior Parameter Identification

The primary behavioral axis is the registered direct child under each root. The five image-type values select the image type and its layer or depth interpretation. `mutable` selects the separate mutable-format view mechanism and exists only under the regular root.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d`, `2d_array`, `cube`, `cube_array`, or `3d` | Sparse image binding, compute image stores, image-plane readback, or format-aware validation does not preserve the expected values. |
| `mutable` | Sparse mutable-format image creation, view-based writes, copyback, or integer/floating-point reference comparison does not preserve the two written portions. |
| Any device-group image-type value | Device-group sparse-bind metadata or peer-memory handling fails in addition to the regular residency path. |

Primary source: [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1-L22)
