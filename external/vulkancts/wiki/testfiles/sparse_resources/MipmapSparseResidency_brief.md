# Understanding Brief: MipmapSparseResidency

## One-Sentence Test Purpose

This test checks whether sparse, mipmapped images can bind their resident mip levels, mip tails, and metadata and preserve data through transfers for each supported image type.

## Background Knowledge

### Sparse image residency and mip tails

A sparse image reserves virtual address space while the application binds physical memory only for the regions it needs. For a mipmapped image, the larger mip levels use sparse image blocks until `imageMipTailFirstLod`; smaller levels are packed into a mip tail. The implementation reports whether the tail is shared by array layers and reports a separate metadata aspect when needed.

Why it matters here:
- The test must bind non-tail levels with `VkSparseImageMemoryBind` and tail regions with opaque binds.
- Metadata has its own sparse requirements and must be bound before the image is used.

### Image aspects and planes

A format can expose one color aspect or several planes. Each plane can have its own sparse requirements and copy regions. The test therefore repeats its binding and transfer bookkeeping per plane instead of assuming one contiguous color allocation.

## One Concrete Example

Consider a 2D image with one selected format and the registered extent `512x256x1`. The test queries the supported mip count and sparse requirements. It binds every block of each mip before the reported tail, then binds the tail and any metadata. A host-visible buffer contains deterministic bytes. Transfer commands copy each plane and mip level from the buffer into the image and back into an output buffer. The host compares the returned bytes with the original pattern.

## End-to-End Test Flow

```text
[host] select an image type, format, and registered extent
[host] check image limits, sparse image support, and R64 atomic support when required
[host] create a single-sampled optimal-tiled sparse image with transfer source and destination usage
[host] query sparse requirements and the runtime mip count
[host] allocate and bind every non-tail mip block, each mip tail, and required metadata
[host] submit the sparse bind and signal the bind semaphore
[host] fill a host-visible input buffer with deterministic bytes
[host] submit buffer-to-image copies for every plane and mip, then image-to-buffer copies
[host] wait for completion and invalidate the output allocation
[host] compare every copied byte range with the reference pattern
[host] pass if all planes and mip levels match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test does not generate shader or program artifacts. Its observable work uses transfer commands.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse `VkImage` | yes | sparse memory per plane, mip, tail, and metadata | copied to and from | indirectly through output buffer | Target resource whose mip residency is tested |
| Input `VkBuffer` | yes | host-visible allocation | transfer source | no | Supplies the reference bytes |
| Output `VkBuffer` | yes | host-visible allocation | transfer destination | yes | Carries image data back for comparison |
| Sparse image bind semaphore | yes | no | orders transfer work after sparse binding | no | Makes the bind-to-transfer dependency explicit |

## What Is Checked

- The host fills the input buffer with `(offset % imageMemoryRequirements.alignment) + 1` for each byte.
- The copy list covers every format plane and every mip level, with array layers included in each image subresource.
- The host compares the output with the reference using `deMemCmp`. Any mismatch fails the test; a complete match returns `Passed`.

## Behavior Parameter Identification

> **Behavior parameter:** image type
>
> **Candidate values:** `2d`, `2d_array`, `cube`, `cube_array`, `3d`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect sparse block, mip-tail, plane, or transfer handling for a 2D image |
| `2d_array` | Incorrect layer addressing or per-layer sparse binding for a 2D array |
| `cube` | Incorrect cube-compatible image setup, layer handling, or mip binding |
| `cube_array` | Incorrect cube-array layer and tail handling |
| `3d` | Incorrect 3D extent, depth reduction across mips, or sparse binding handling |

## Important Variations and Special Cases

- Regular and `device_group_mipmap_sparse_residency` roots use the same image-type, format, and extent matrix. Device-group mode changes device targeting for binds and submissions.
- The registered extents include odd dimensions such as `11x137x1` and `11x137x3`. The generator skips a case when a format's alignment rejects an extent.
- `getTestFormats()` supplies the format matrix. YCbCr formats are included only for the image types supported by the shared helper.
- R64 formats require `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`, although this transfer-only test uses that support gate consistently with the sparse-resource format matrix.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support checks | [`checkSupport()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L85-L107) | Image limits, sparse support, and R64 feature gate |
| Image creation and mip count | [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L135-L201) | Queue requirements, image flags, format support, and mip count |
| Residency and metadata binds | [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L242-L409) | Non-tail blocks, mip tails, metadata, and sparse submission |
| Transfer comparison | [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L411-L582) | All-plane/all-mip copies and byte comparison |
| Parameter generation | [`createMipmapSparseResidencyTestsCommon()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L592-L649) | Image types, extents, formats, and pruning |
| Sparse semantics | [`sparsemem.adoc`](../../../../../vulkan-docs/src/chapters/sparsemem.adoc#L867-L914) | Sparse format properties, mip-tail flags, and aspects |
| Registered mustpass roots | [`sparse-resources.txt`](../../../mustpass/main/vk-default/sparse-resources.txt) | Default mustpass coverage |

## Questions / Risk Points for User Audit

- Should the final page call the five direct children "image types" or "test case groups"? The source names them with `getImageTypeName()`.
- The source requires the R64 image-atomic feature even though the observed operation is transfer-based. Preserve this as a support requirement unless the implementation changes.
- Device-group execution details are shared with the base class. The final page should describe only the source-confirmed device-targeting difference.

## Conversion Notes for Final Wiki Rewrite

- Use `image type` as the primary behavioral axis and carry the five-value failure table into the final page.
- Keep the final Background Knowledge to sparse image mip tails and aspects/planes.
- State that shader analysis is not applicable because this implementation uses transfer commands, not shader-generated results.
- Explain the host-side copy and comparison as the main runtime behavior. Keep helper names in the source appendix.
