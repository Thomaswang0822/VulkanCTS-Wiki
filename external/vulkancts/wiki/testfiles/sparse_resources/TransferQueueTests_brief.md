# Understanding Brief: TransferQueueTests

## One-Sentence Test Purpose

This test checks whether a sparse 2D image can be bound with opaque sparse memory and survive a buffer-to-image-to-buffer transfer round trip on a queue that supports both sparse binding and transfer operations.

## Background Knowledge

### Opaque sparse image binding

A sparse image does not use one ordinary allocation for its complete backing memory. The implementation supplies opaque memory binds that cover the image's sparse memory requirements, then uses the image like a normal transfer resource after the bind completes.

Why it matters here:
- The test binds every required opaque memory slot before recording image transfers.
- A successful image creation alone does not prove that the queue bind and subsequent accesses use the intended backing memory.

### Transfer layouts and visibility

Vulkan copy commands require layouts that match the direction of the copy. A barrier changes the sparse image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` for upload, then to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` for readback. Host writes and reads also need memory barriers and host-cache flush or invalidate operations.

Why it matters here:
- The result is meaningful only after the bind semaphore, transfer submission, and host visibility steps complete.
- The test covers all image planes and mip levels returned for the selected format.

## One Concrete Example

For the `VK_FORMAT_R8G8B8A8_UNORM` case, the registered `2d` test family creates a `512_256_1` image. The host fills a transfer-source buffer with a deterministic byte pattern. The transfer queue binds the image's opaque sparse memory, copies the buffer into every plane and mip level, changes the image to transfer-source layout, and copies the image into a host-visible destination buffer. The host compares the returned bytes with the original pattern.

The format-specific comparison allows low bits to differ for formats whose helpers identify those bits as don't-care. That mask is part of the expected result, not a general tolerance for transfer errors.

## End-to-End Test Flow

```text
[host] select `IMAGE_TYPE_2D`, `512_256_1`, and one basic format
[host] require sparse binding support and check image-size support
[host] create an optimal-tiled sparse image with transfer source and destination usage
[host] query image memory requirements and allocate opaque sparse binds
[host] submit `vkQueueBindSparse` on the queue with sparse-binding and transfer capability
[host] create copy regions for every image plane and mip level
[host] fill and flush a host-visible input buffer
[host] record barriers, copy the input buffer to the image, transition the image, and copy it to a host-visible output buffer
[host] submit the command buffer waiting on the sparse-bind semaphore
[host] wait for completion, invalidate the output allocation, and compare returned bytes with the reference pattern
[host] report pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test does not generate shaders or other program artifacts. It builds `VkBufferImageCopy` regions from the selected format's plane count, mip count, plane extents, and aligned buffer offsets.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Sparse `VkImage` | yes | through opaque sparse binds | written by `cmdCopyBufferToImage`, then read by `cmdCopyImageToBuffer` | no | The image is the sparse resource under test. |
| Opaque sparse `VkDeviceMemory` allocations | yes | yes, through `VkSparseImageOpaqueMemoryBindInfo` | backs the image | no | They provide the image's sparse backing. |
| Host-visible input `VkBuffer` | yes | yes | read by the transfer operation | host writes it | Supplies the reference bytes. |
| Host-visible output `VkBuffer` | yes | yes | written by the transfer operation | host reads it | Captures the image data for validation. |
| Bind semaphore | yes | used by queue submission | orders the copy after sparse binding | no | Connects `vkQueueBindSparse` to the transfer submission. |

## What Is Checked

- The output buffer contains the input pattern for each plane and mip level.
- The comparison checks each byte in each copied mip level.
- For eligible formats, the comparison preserves only the significant high bits on even byte positions by applying the format-specific `0xC0` or `0xF0` mask.
- A mismatch returns `tcu::TestStatus::fail("Failed")`; a complete match returns `tcu::TestStatus::pass("Passed")`.

## Behavior Parameter Identification

> **Behavior parameter:** registered format
>
> **Candidate values:** `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT`, `VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R8G8B8A8_UNORM`, and `VK_FORMAT_R8G8B8A8_SNORM`.

The image type and extent stay fixed in the registration matrix, while the format changes the image representation, plane and mip calculations, and any comparison mask.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for floating-point formats. |
| `VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32_UINT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for unsigned integer formats. |
| `VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, `VK_FORMAT_R32_SINT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for signed integer formats. |
| `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8G8B8A8_SNORM` | Sparse binding, normalized-format transfer, copy-region calculation, or readback mismatch after the permitted low-bit mask. |

## Important Variations and Special Cases

- Registration fixes the image type to `2d` and the extent to `512_256_1`. A format's alignment can skip that size, which matters for formats requiring aligned dimensions.
- The runtime derives mip levels from image format properties and handles every reported plane. The registered basic list currently contains single-plane formats, but the implementation retains the plane-aware path.
- The support check contains an R64 feature path for `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`, although no R64 format appears in this file's basic list.
- The case is unsupported if the image format, image size, sparse address-space limit, or required sparse-plus-transfer queue is unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Basic format list and registration | [`getBasicTestFormats` and `createTransferQueueTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89) | Defines the `transfer_queue.2d` matrix. |
| Support checks | [`SparseResourceTransferQueueCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L117-L133) | Checks sparse binding, image size, and the R64 feature path. |
| Image creation and sparse memory requirements | [`SparseResourceTransferQueueInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L169-L229) | Selects the queue, creates the sparse image, and checks format and address-space support. |
| Opaque sparse binding | [`vkQueueBindSparse` setup](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L233-L276) | Allocates and submits the image's opaque memory binds. |
| Copy-region construction and transfers | [`bufferImageCopy` and copy commands](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L417) | Covers planes, mip levels, barriers, upload, readback, and host visibility. |
| Result comparison | [`Validate results`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L455) | Defines masks and the pass/fail condition. |
| Sparse memory semantics | [`Sparse memory`](../../../../vulkan-docs/src/chapters/sparsemem.adoc) | Spec background for sparse resource binding and sparse address space. |

## Questions / Risk Points for User Audit

- Is the format grouping the right primary behavioral axis, given that image type and size are fixed?
- Is the distinction between unsupported cases and transfer mismatches clear?
- Does the plane-aware explanation make clear that the current registered basic formats are single-plane?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to opaque sparse binding and transfer-layout visibility concepts.
- Present `transfer_queue.2d` as the one-level registration tree and put format and size details in the parameter sections.
- Keep the host-side transfer timeline and resource table, but omit shader walkthroughs because this test has no shader code.
- Copy the `### Failure Cause Mapping` table into the final page and write fresh cause analysis for binding, layout, copy-region, synchronization, and comparison-mask failures.
