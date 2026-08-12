# Understanding Brief: sparse image rebind

## One-Sentence Test Purpose

This test checks whether Vulkan can replace all sparse image bindings and then rebind one sparse image block from the first memory object while the rest of the image still contains data from the second object.

## Background Knowledge

### Sparse image blocks and rebinding

A sparse-residency image divides each non-mip-tail subresource into rectangular sparse image blocks. `vkQueueBindSparse` associates those blocks with ranges of `VkDeviceMemory`; a later bind for an overlapping image region replaces the earlier association.

Why it matters here:
- The test compares two complete bindings and then one partial binding in the selected array layer.
- The image granularity reported by `VkSparseImageMemoryRequirements` defines the region that should change after the partial bind.

### Aliased sparse memory

The test requires `sparseResidencyAliased`. The feature permits sparse resources to access physical memory through multiple bindings, but writes to aliases still need appropriate memory dependencies. The test serializes its sparse-bind and transfer operations with semaphores and queue ordering before it reads the image back.

## One Concrete Example

Consider a 2D image with more than one sparse block in each available dimension. The host allocates two equal memory objects and prepares complete binding arrays for both. It binds memory object 0 and clears the image with the first format-dependent color. It then binds memory object 1 over the whole image and clears it with a second color. Finally, it binds one block in the last array layer back to memory object 0. A copy of that layer should contain the first color inside that block and the second color elsewhere.

## End-to-End Test Flow

```text
[host] select an image type, format, and image size
[host] require sparse residency aliasing and support for the image type and format
[host] create a sparse-residency image and allocate two backing memory objects
[host] build complete sparse-image binding arrays and one offset partial bind
[host] bind memory object 0 and clear the image with its reference color
[host] bind memory object 1 over the full image and clear it with its reference color
[host] bind the selected block from memory object 0
[host] copy the selected layer to a host-visible buffer
[host] compare every texel with the color expected inside or outside the partial-bind extent
[host] return pass only if every channel comparison succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test does not generate shaders or pipelines. It uses transfer commands to clear and copy the image.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Sparse `VkImage` | yes | yes, through sparse binds | cleared and copied | indirectly, through the copy | The resource whose bindings are replaced. |
| Two `VkDeviceMemory` objects | yes | yes, through complete and partial image binds | provide the two physical backing contents | no | They produce the two reference colors and exercise rebinding. |
| Host-visible readback buffer | yes | yes | receives the selected image layer | yes | Supplies texels for the final host-side comparison. |
| Bind and transfer semaphores | yes | yes | order sparse binding and transfer work | no | Prevent the readback sequence from racing the preceding operations. |

## What Is Checked

- The copied layer is inspected at every texel and for every channel present in the format.
- Texels inside `imagePartialBind.offset` and `imagePartialBind.extent` must match the clear color for memory object 0.
- Texels outside that extent must match the clear color for memory object 1.
- Signed and unsigned integer formats use exact comparisons. Fixed-point and floating-point formats use `1e-5` plus the format's fixed-point error where applicable.
- A mismatch returns `tcu::TestStatus::fail("Failed")`; a complete match returns `tcu::TestStatus::pass("Passed")`.

## Behavior Parameter Identification

> **Behavior parameter:** image type test family
>
> **Candidate values:** `2d`, `2d_array`, `cube`, `cube_array`, `3d`

The format and image-size dimensions change the sparse-block geometry and data representation, but the five image-type test families select the primary resource shape being exercised.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect sparse binding replacement or spatial result checking for a two-dimensional image. |
| `2d_array` | Incorrect sparse binding replacement or selected-layer handling for a two-dimensional array image. |
| `cube` | Incorrect sparse binding replacement or cube-compatible image handling. |
| `cube_array` | Incorrect sparse binding replacement or cube-array layer handling. |
| `3d` | Incorrect sparse binding replacement or three-dimensional block offset and extent handling. |

## Important Variations and Special Cases

- The factory registers three sizes per image type. The registered sizes are `512_256_1`, `128_128_1`, and `503_137_1` for `2d`; `512_256_6`, `128_128_8`, and `503_137_3` for `2d_array`; `256_256_1`, `128_128_1`, and `137_137_1` for `cube`; `256_256_6`, `128_128_8`, and `137_137_3` for `cube_array`; and `256_256_16`, `128_128_8`, and `503_137_3` for `3d`.
- YCbCr formats are skipped. The remaining formats come from `getTestFormats` for each image type.
- The selected layer is `arrayLayers - 1`. The partial offset advances by one sparse-block granularity in each dimension that has more than one block, and the extent is clamped at the image boundary.
- Cases with fewer than two sparse blocks or with mip level 0 already in the mip tail are reported as unsupported because they cannot exercise the partial bind.
- The implementation contains a device-group parameter, but the registered `image_rebind` factory invokes the common builder with `useDeviceGroup` set to `false`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support checks and image creation | [`ImageSparseRebindCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L103-L132), [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L194-L258) | Establishes feature, queue, image-type, and format requirements. |
| Sparse-block matrix and partial bind | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L307-L419) | Calculates complete bindings, the selected layer, and the partial extent. |
| Rebind and clear sequence | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L455-L626) | Shows the two full binds followed by the partial bind. |
| Copyback and validation | [`ImageSparseRebindInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L629-L833) | Defines the readback and pass/fail comparisons. |
| Registration matrix | [`createImageSparseRebindTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L843-L897) | Defines image types, sizes, formats, and test-case names. |
| Sparse block and aliasing semantics | [`Sparse Partially-Resident Images`](../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-partially-resident-images), [`Sparse image memory aliasing`](../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-sparse-image-memory-aliasing) | Grounds the block layout and aliasing prerequisites. |

## Questions / Risk Points for User Audit

- Is the distinction between replacing a full image binding and restoring one block clear?
- Is the selected last layer and the image-granularity-based partial extent explained well enough for array, cube, and 3D cases?
- Should the final page say more about the transfer semaphore sequence, or is the host-side execution summary sufficient?

## Conversion Notes for Final Wiki Rewrite

Keep the final page focused on the full-bind, clear, partial-rebind, copyback sequence. Distill the sparse-block and aliasing explanations into `## Background Knowledge`. Use the image type as the behavior parameter, retain the brief's failure mapping table unchanged, and explain format and size as matrix dimensions rather than separate walkthroughs.
