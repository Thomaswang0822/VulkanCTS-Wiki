# Understanding Brief: ImageSparseBinding

## One-Sentence Test Purpose

This test checks whether Vulkan can bind all opaque memory ranges of fully resident sparse images and preserve image data across transfer operations for several `vkQueueBindSparse` submission layouts.

## Background Knowledge

### Opaque sparse-image binding

An image created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` exposes a linear opaque binding range through its memory requirements. `VkSparseMemoryBind` entries map aligned portions of that range to `VkDeviceMemory`; `VkSparseImageOpaqueMemoryBindInfo` associates those entries with the image. This differs from `VkSparseImageMemoryBind`, which addresses individual sparse image blocks and is used with sparse residency.

Why it matters here:
- Every tested image is fully backed through opaque binds, so later transfer commands can access all mip levels and planes.
- `vkQueueBindSparse` accepts either one batch containing many binds, many opaque-bind records in one batch, or many batches.

### Sparse binding submission and device groups

`vkQueueBindSparse` submits sparse binding batches to a queue and can signal a fence when the binding work completes. In a device group, `VkDeviceGroupBindSparseInfo` selects the physical-device instance for the resource and memory. The test keeps the image and memory indices explicit when it exercises the device-group root.

## One Concrete Example

For a representative 2D image, the test obtains the image memory requirement and allocates one aligned memory object for each sparse range. It then creates opaque bind records covering those ranges. In `multiple_sparse_memory_bind`, all `VkSparseMemoryBind` entries are placed in one `VkSparseImageOpaqueMemoryBindInfo`, which is submitted in one `VkBindSparseInfo`. The other two test families change only how those records are packaged.

## End-to-End Test Flow

```text
[host] select image type, format, size, and bind packaging
[host] check sparse-binding support, limits, memory type, and queue availability
[host] create a fully resident sparse image and allocate aligned memory for its opaque ranges
[host] package the opaque binds as one record, many records in one batch, or many batches
[host] submit vkQueueBindSparse and wait for its fence
[host] fill a host-visible input buffer with the deterministic reference pattern
[host] copy the buffer into every image plane and mip level
[host] copy the image back into a host-visible output buffer
[host] invalidate and compare the output bytes with the reference, applying format-specific masks
[host] decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

No shader or generated program artifact participates in this test. The device work uses transfer commands.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse `VkImage` | yes | yes, through opaque sparse binds | written by buffer-to-image and read by image-to-buffer | indirectly | The resource whose complete opaque address range is tested |
| Per-range `VkDeviceMemory` allocations | yes | yes, through `VkSparseMemoryBind` | supplies image backing | no | Tests alignment and coverage of the opaque binding range |
| Host-visible input buffer | yes | yes | read by buffer-to-image | no | Carries the deterministic reference bytes |
| Host-visible output buffer | yes | yes | written by image-to-buffer | yes | Supplies bytes for host-side validation |

## What Is Checked

- The test waits for sparse binding to complete before issuing transfer commands.
- It copies every plane and mip level using extents and offsets derived from the image format description.
- The reference buffer uses `(byteIndex % imageMemoryRequirements.alignment) + 1`.
- Each returned byte must match the reference under a full-byte mask, except formats whose low six or four bits are defined as don't-care. A mismatch returns `Failed`; otherwise the case returns `Passed`.

## Behavior Parameter Identification

> **Behavior parameter:** bind packaging test family
>
> **Candidate values:** `multiple_sparse_memory_bind`, `multiple_sparse_image_opaque_memory_bind_info`, `multiple_bind_sparse_info`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `multiple_sparse_memory_bind` | Incorrect handling of one opaque-bind record containing many aligned memory binds; sparse image binding or transfer/copyback failure |
| `multiple_sparse_image_opaque_memory_bind_info` | Incorrect handling of multiple opaque-bind records in one `VkBindSparseInfo`; sparse submission packaging or image backing failure |
| `multiple_bind_sparse_info` | Incorrect handling of multiple `VkBindSparseInfo` batches in one `vkQueueBindSparse` call; batch execution, binding, or transfer/copyback failure |

## Important Variations and Special Cases

- Both `image_sparse_binding` and `device_group_image_sparse_binding` use the same generated matrix. The latter adds `VkDeviceGroupBindSparseInfo` to the bind submission and uses device indices for the resource and memory.
- Image types are 1D, 1D array, 2D, 2D array, 3D, cube, and cube array. 2D and 2D-array cases also cover planar YCbCr formats.
- Regular cases add `VK_FORMAT_A8_UNORM_KHR` when `VK_KHR_maintenance5` is available. R64 formats require `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`.
- Odd dimensions are skipped when they violate a format's image-size alignment, particularly for some YCbCr formats.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Bind-family registration and matrix | [`createImageSparseBindingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L631-L705) | Defines roots, bind families, image types, formats, and sizes |
| Support checks | [`ImageSparseBindingCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L107-L163) | Establishes feature, limit, and queue requirements |
| Bind packaging | [`ImageSparseBindingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L427) | Implements the three submission layouts and device-group extension |
| Transfer and comparison | [`ImageSparseBindingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L429-L611) | Defines the data path and pass/fail check |
| Opaque bind semantics | [`VkSparseImageOpaqueMemoryBindInfo`](../../../vulkan-docs/src/chapters/sparsemem.adoc#L1516-L1568) | Specifies the Vulkan structure used by the test |
| Submission semantics | [`vkQueueBindSparse`](../../../vulkan-docs/src/chapters/sparsemem.adoc#L1691-L1758) | Defines batch submission and completion behavior |
| Device-group indices | [`VkDeviceGroupBindSparseInfo`](../../../vulkan-docs/src/chapters/sparsemem.adoc#L1877-L1921) | Defines resource and memory device selection |

## Questions / Risk Points for User Audit

- Does the distinction between opaque binding and sparse residency remain clear?
- Is bind packaging correctly identified as the primary behavior axis rather than image type or format?
- Is the device-group path described as a routing variation rather than a separate binding algorithm?
- Are the format-specific masks and feature gates stated narrowly enough?

## Conversion Notes for Final Wiki Rewrite

- Keep `Background Knowledge` to short prerequisites about opaque ranges and `vkQueueBindSparse` batches.
- Carry the behavior axis and the failure mapping table directly into the final Level-3 page.
- Explain the three packaging families in `Behavior Parameters`, then use the runtime section for the common transfer and comparison flow.
- Include the relevant spec-backed semantics in failure analysis without claiming a particular driver or hardware defect.
- No shader walkthrough is needed because this test has no shader code.
