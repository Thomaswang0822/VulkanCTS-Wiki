## Overview

**Core question:** Do sparse image binds make resident image data visible to compute shaders and readback while unbound blocks follow the device's nonresident residency contract?

- `vktSparseResourcesImageSparseResidency.cpp` implements both sparse image residency roots and the regular root's mutable-format branch.
- The regular root covers 2D, 2D-array, cube, cube-array, and 3D images. The device-group root covers the same five image types and supplies device-group sparse-bind metadata.
- The test binds alternating sparse blocks, writes coordinate-derived values with compute shaders, copies image planes back, and checks the results. When `residencyNonResidentStrict` is enabled, unbound blocks must read as zero.
- The regular root also tests compatible mutable-format image views by writing separate image portions through two views and comparing the copied portions with generated references.

## Background Knowledge

- Sparse image residency lets an image exist with only selected memory regions bound. Operations that touch an unbound region therefore have device-defined behavior unless the device advertises strict nonresident residency.
- A sparse image can have separate memory requirements for image blocks, mip tails, and metadata. Multi-planar images also expose planes whose compatible storage formats can differ from the image's external format.
- A mutable-format image can use views with compatible formats. The view format controls the storage-image access used for a write, while the image and view format compatibility rules constrain which combinations are legal.

## Registration Hierarchy

```text
sparse_resources.image_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
├── 3d
└── mutable

sparse_resources.device_group_image_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The tree shows only direct children. Beneath the image-type groups, registration expands through format identifiers and image-size leaves. The mutable group expands through image type and compatible image/view format triples.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Root | `image_sparse_residency`, `device_group_image_sparse_residency` | Selects regular sparse binds or device-group sparse-bind metadata. | [`createImageSparseResidencyTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149) |
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects image dimensionality and layer or depth interpretation. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2045) |
| Regular image size | `512_256_1`, `1024_128_1`, `11_137_1` for `2d`; `512_256_6`, `1024_128_8`, `11_137_3` for `2d_array`; `256_256_1`, `128_128_1`, `137_137_1` for `cube`; `256_256_6`, `128_128_8`, `137_137_3` for `cube_array`; `512_256_16`, `1024_128_8`, `11_137_3` for `3d` | Varies sparse block counts, image extent, array layers, or 3D depth. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2030-L2045) |
| Format | Formats from `getSparseResidencyTestFormats`; applicable regular non-device-group cases also include `VK_FORMAT_A8_UNORM_KHR` | Selects channel class, plane layout, storage compatibility, and format-specific feature checks. | [`ImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L336) |
| Mutable image size | `512_256_1` for `2d`, `512_512_2` for `2d_array`, `512_512_3` for `3d` | Fixes the image extent while the format triple varies. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2091) |

## Behavior Parameters

The primary behavioral axis is the direct child under the registered root. The regular root has six values; the device-group root has five because the mutable branch is excluded when `useDeviceGroup` is true.

### `2d`, `2d_array`, `cube`, `cube_array`, and `3d` | sparse residency by image type

Each image-type group creates cases for its registered formats and supported sizes. The case creates a sparse storage image, binds every other sparse block in resident mip levels, and uses the image type's coordinate mapping for shader writes and readback validation. Cube and cube-array cases use cube-compatible layer arrangements; array and 3D cases preserve their respective layer or depth interpretation.

### `mutable` | sparse mutable-format image views

The regular-only mutable group creates compatible triples of image, first-view, and second-view formats, with all three formats distinct. It allocates only the left half of the image, writes the upper and lower portions through separate storage-image views, copies both portions out, and compares each portion with a generated integer or floating-point reference image.

## Shader Analysis

The regular residency path generates one compute shader per image plane. Each invocation stores values derived from its global coordinates. The shader uses a plane-compatible storage format when the external image format needs one. Mutable-format cases use the corresponding generated shaders for their two storage-image views. This page does not include a representative shader walkthrough because the source builds the shader text from format and plane parameters rather than exposing one stable handwritten case.

## Runtime Execution and Result Checking

- The instance creates a logical device with both sparse-binding and compute queues. It checks image limits, sparse support for the selected image type, storage-image support, and format-specific R64 or A8 requirements before execution.
- It creates the sparse image, queries sparse memory requirements, and binds alternating image blocks. It binds mip tails and metadata when required. Device-group cases attach `VkDeviceGroupBindSparseInfo` to the sparse bind.
- After the sparse bind completes, the test transitions the image for shader access, dispatches the generated compute shader for each plane, then copies each plane to host-visible memory.
- Resident blocks must contain coordinate-derived channel values. Integer channels use exact comparisons; fixed-point and floating-point channels use format-aware tolerances. If `residencyNonResidentStrict` is true, nonresident blocks must contain zeroes within the same channel rules.
- Mutable cases copy the two written portions and compare them with `tcu::intThresholdCompare` for integer formats or `tcu::floatThresholdCompare` with a `0.01` threshold for floating-point formats.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d`, `2d_array`, `cube`, `cube_array`, or `3d` | Sparse image binding, compute image stores, image-plane readback, or format-aware validation does not preserve the expected values. |
| `mutable` | Sparse mutable-format image creation, view-based writes, copyback, or integer/floating-point reference comparison does not preserve the two written portions. |
| Any device-group image-type value | Device-group sparse-bind metadata or peer-memory handling fails in addition to the regular residency path. |

### Cause Analysis

#### Sparse residency data or strict nonresident results

**Possible failure symptoms:** A resident block differs from its coordinate-derived reference, or a nonresident block is nonzero when strict nonresident residency requires zero.

**Possible implementation causes:** The sparse bind may cover the wrong subresource, offset, extent, layer, mip tail, or metadata region. The compute image store, image layout transition, sparse queue synchronization, or copyback path may also expose the wrong data. The exact failing layer requires the test log and source-level investigation.

#### Mutable-format view writes and comparisons

**Possible failure symptoms:** Either copied image portion fails its integer comparison or exceeds the floating-point threshold against the reference generated for its view format.

**Possible implementation causes:** The image and view format combination may be handled incorrectly, one view may address the wrong portion, or sparse memory coverage may not match the view access. Source inspection grounds these as the relevant mechanisms; the precise defect location requires the failing format triple and test log.

#### Device-group sparse binding

**Possible failure symptoms:** A device-group case fails the same resident-data checks as a regular case, with the failure limited to device-group execution or peer-memory arrangements.

**Possible implementation causes:** The device-group bind metadata may select the wrong resource or memory device, or peer-memory features may not support the requested mapping. The failing device indices and sparse-bind trace are needed to distinguish these cases.

## Case Pruning

### Requirement-based pruning

Cases are skipped when image limits, sparse residency support for the image type, storage-image support, queue requirements, memory types, sparse address-space limits, or sparse image-format properties are unavailable. Device-group cases additionally require suitable peer-memory features. R64 formats require `VK_EXT_shader_image_atomic_int64` with both shader-image and sparse-image 64-bit atomic support. `VK_FORMAT_A8_UNORM_KHR` requires `VK_KHR_maintenance5` and storage writes without a format where that branch is applicable. Mutable cases require sparse and mutable image-format properties for the image and its views.

### Design-based pruning

The regular matrix adds `mutable` only to the non-device-group root because the mutable implementation does not support device-group mode. Mutable cases retain only triples in which all three formats differ and the image format is compatible with both view formats. The regular image matrix uses one registered set of sizes per image type, while format alignment checks remove sizes that cannot represent a selected format, including certain odd-sized YCbCr cases.

## Key Takeaways

- The test deliberately leaves alternating sparse blocks unbound, so resident data and strict nonresident behavior are checked separately.
- Image type changes the layer, face, or depth mapping used by both sparse binds and validation; it is the page's main behavioral axis.
- Multi-planar formats use per-plane storage-compatible operations and readback checks.
- Mutable-format coverage tests two view-driven writes into separate image portions and compares each portion in the view's format.
- Device-group coverage reuses the residency matrix but adds device-group sparse-bind metadata and omits mutable-format cases.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createImageSparseResidencyTests` and `createDeviceGroupImageSparseResidencyTests` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149) | Registers the two category-qualified roots. |
| `createImageSparseResidencyTestsCommon` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2025-L2137) | Defines image types, sizes, formats, and the regular-only mutable branch. |
| `ImageSparseResidencyCase::checkSupport` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L337) | Defines image, format, and feature support gates. |
| `ImageSparseResidencyInstance::iterate` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L365-L1205) | Creates resources, binds sparse memory, dispatches shaders, copies planes, and validates resident and nonresident data. |
| `ImageMutableSparseTestInstance::verifyImage` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1508-L1575) | Compares copied mutable-view portions with generated references. |
| Sparse image helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L43-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies image-type, plane, format, and sparse-support helpers. |
