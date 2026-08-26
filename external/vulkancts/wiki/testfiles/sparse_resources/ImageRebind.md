## Overview

**Core question:** Does sparse image rebinding replace the expected image region while preserving the contents supplied by the newer full binding elsewhere?

- This page covers the implementation and registration of `sparse_resources.image_rebind` in [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L1-L44).
- Each case creates a sparse-residency image, fills it through two complete sparse bindings, then rebinds one sparse block from the first memory object into the last layer.
- The test copies that layer to a host-visible buffer and checks the exact spatial boundary between the two expected clear colors.
- Registered cases vary image type, format, and size. The implementation skips YCbCr formats and does not register the device-group variant.

## Background Knowledge

- Sparse-residency images divide each non-mip-tail image subresource into rectangular sparse image blocks. `vkQueueBindSparse` maps those blocks to memory ranges, and a later bind for an overlapping region replaces the previous mapping.
- The test requires `sparseResidencyAliased`, which permits sparse resources to access physical memory through multiple bindings. The test orders its sparse-binding and transfer operations with semaphores before reading the result back.

## Registration Hierarchy

```text
sparse_resources.image_rebind
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

`vktSparseResourcesImageRebind.cpp` implements all five registered test families. Each family expands to a format intermediate node and then to image-size test cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type test family | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects the image shape, layer count, and dimensionality of sparse-block offsets. | [`createImageSparseRebindTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L868) |
| Image sizes | `2d`: `512_256_1`, `128_128_1`, `503_137_1`; `2d_array`: `512_256_6`, `128_128_8`, `503_137_3`; `cube`: `256_256_1`, `128_128_1`, `137_137_1`; `cube_array`: `256_256_6`, `128_128_8`, `137_137_3`; `3d`: `256_256_16`, `128_128_8`, `503_137_3` | Produces different sparse-block counts, including odd extents that exercise boundary clamping. The third component is layer count for array and cube-array images, and depth for 3D images. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L862) |
| Format | Values returned by `getTestFormats(imageType)`, excluding YCbCr formats | Selects channel type and format-specific comparison behavior. | [`createImageSparseRebindTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L870-L879) |
| Memory objects | Two, `kMemoryObjectCount = 2` | Supplies the two clear colors used to detect which binding backs each texel. | [`kMemoryObjectCount`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L89), [`getColorClearValue`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L156-L185) |

## Behavior Parameters

The primary behavioral axis is the image type test family. Format and size alter representation and sparse geometry, but the image type selects the resource shape whose rebinding rules are exercised.

### `2d` — two-dimensional image

The test uses one layer and computes a two-dimensional partial-bind region. The later bind must restore one block from memory object 0 while the rest of the image retains memory object 1's clear color.

### `2d_array` — array image

The implementation selects the last array layer, `arrayLayers - 1`, for the partial bind. Other layers remain fully covered by the second memory object's binding and color.

### `cube` — cube-compatible image

The image receives `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` in addition to the sparse-binding and sparse-residency flags. The rebinding check still treats the image's layers as the spatial target of the partial bind.

### `cube_array` — cube-array image

This family uses cube-compatible images with multiple cube layers. It follows the selected-last-layer rule used by array images while retaining the cube-compatible creation flag.

### `3d` — three-dimensional image

The partial bind can advance in x, y, and z when the image has more than one sparse block along those axes. The expected color boundary therefore covers a genuine 3D extent rather than an array layer alone.

## Shader Analysis

This test has no shaders. It uses image clear and copy transfer commands, followed by host-side texel comparisons.

## Runtime Execution and Result Checking

- `checkSupport` requires the core `sparseResidencyAliased` feature, device image-size limits, and sparse support for the selected image type. Runtime also requires separate sparse-binding and transfer queues.
- The image uses `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, one mip level, optimal tiling, and transfer source/destination usage. Cube and cube-array cases also use `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`.
- The implementation queries sparse image memory requirements and image granularity for each plane. It rejects an image with fewer than two sparse blocks or with mip level 0 in the mip tail, because neither case can exercise a partial block rebind.
- The host allocates two device-memory objects of the same calculated size. It constructs complete binding arrays for every layer and block, then assigns one array to each memory object. The partial bind targets memory object 0 and uses the block offset one granularity step from the origin wherever another block exists.
- The test binds all blocks to memory object 0 and clears the image with memory object 0's format-dependent color. It then binds every block to memory object 1 and clears the image with memory object 1's color. Finally, it submits the one-block bind back to memory object 0.
- The last layer is copied to a host-visible buffer. The host scans every texel and channel. Inside the partial-bind extent it expects memory object 0's color; outside it expects memory object 1's color.
- Integer channels use exact comparisons. Fixed-point and floating-point channels use the source's `1e-5` tolerance, with the fixed-point error added for fixed-point formats. Any mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect sparse binding replacement or spatial result checking for a two-dimensional image. |
| `2d_array` | Incorrect sparse binding replacement or selected-layer handling for a two-dimensional array image. |
| `cube` | Incorrect sparse binding replacement or cube-compatible image handling. |
| `cube_array` | Incorrect sparse binding replacement or cube-array layer handling. |
| `3d` | Incorrect sparse binding replacement or three-dimensional block offset and extent handling. |

### Cause Analysis

#### Sparse binding replacement

**Possible failure symptoms:** Texels outside the partial-bind extent do not contain memory object 1's clear color, or texels inside it do not contain memory object 0's color.

**Possible implementation causes:** The implementation may apply a later `VkSparseImageMemoryBind` to the wrong image subresource or region, retain an earlier mapping for an overlapping block, or fail to make the newly bound memory visible to the subsequent transfer. The exact driver or hardware cause requires investigation if the source and synchronization sequence are otherwise correct.

#### Image-shape handling

**Possible failure symptoms:** Only array, cube, cube-array, or 3D cases fail, with mismatches at layer boundaries or along one spatial axis.

**Possible implementation causes:** The implementation may interpret array layers, cube-compatible layers, or 3D offsets incorrectly when translating sparse image block coordinates. It may also mishandle the clamped extent for an odd-sized image. The failing case and validation output are needed to distinguish image creation, sparse binding, transfer, and comparison issues.

#### Format conversion or comparison

**Possible failure symptoms:** Mismatches appear only for signed integer, unsigned integer, fixed-point, or floating-point formats, even though the spatial boundary is in the expected location.

**Possible implementation causes:** The image clear, format conversion, copy operation, or format-specific readback interpretation may produce a value outside the comparison rule used by the test. Further source and Vulkan format-semantics investigation is needed before assigning the fault to a particular implementation stage.

## Case Pruning

### Requirement-based pruning

The test skips YCbCr formats during registration. At runtime it reports unsupported cases when the device lacks sparse residency aliasing, the image type or format lacks sparse support, the image exceeds device limits, no suitable memory type exists, or peer-memory capabilities are insufficient for an internal device-group iteration. It also skips configurations that cannot provide at least two sparse blocks outside the mip tail.

### Design-based pruning

The registration excludes YCbCr formats and does not create a device-group variant. The runtime geometry check retains only images with at least two sparse blocks outside the mip tail, because a smaller or tail-only image cannot exercise partial rebinding.

## Key Takeaways

- The test detects sparse rebinding errors by giving two complete bindings different clear colors, then restoring one block from the first memory object.
- The expected result is spatial: the partial sparse-block extent must contain the first color, and the rest of the selected layer must contain the second.
- Image type, format, and size affect the sparse geometry and comparison rules, while the core rebind sequence remains the same.

## Source Reference Appendix

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Feature and type support | [`ImageSparseRebindCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L103-L132) | Defines the feature and image-type prerequisites. |
| Image and queue setup | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L194-L301) | Creates the sparse image and checks format, memory, and queue requirements. |
| Complete and partial bind construction | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L307-L448) | Computes block coordinates, memory offsets, and the selected partial extent. |
| Bind, clear, and rebind sequence | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L455-L714) | Shows how the two colors and final readback are produced. |
| Validation | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L723-L833) | Defines the per-texel pass/fail rule. |
| Registration | [`createImageSparseRebindTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L843-L903) | Defines the hierarchy and generated case names. |
| Sparse image semantics | [`Sparse Partially-Resident Images`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-partially-resident-images), [`Mip Tail Regions`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-miptail) | Grounds sparse block and mip-tail behavior. |
| Aliased sparse memory | [`Sparse image memory aliasing`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-sparse-image-memory-aliasing) | Grounds the `sparseResidencyAliased` requirement and aliasing rules. |
