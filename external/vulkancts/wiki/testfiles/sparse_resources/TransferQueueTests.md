## Overview

**Core question:** Can a sparsely bound 2D image complete a transfer round trip on a queue that supports both sparse binding and transfer operations?

- This page covers `vktSparseResourcesTransferQueueTests.cpp` and the `sparse_resources.transfer_queue.2d` test family.
- Each case binds an optimal-tiled sparse image, copies deterministic buffer data into every image plane and mip level, copies it back, and compares the result with the reference bytes.
- The registered matrix fixes the image type and extent, then varies the basic image format. The page explains the registration, resource flow, validation masks, and failure meaning.

## Background Knowledge

- Sparse image memory uses opaque binds instead of one ordinary allocation for the whole image. The test must submit those binds before it uses the image for transfer operations.
- Vulkan copy commands require matching image layouts. The test changes the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` for upload and then to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` for readback. Host-visible buffers also need cache flush or invalidate operations and memory barriers before the host consumes their contents.

## Registration Hierarchy

```text
sparse_resources.transfer_queue
└── 2d
```

The `2d` test family expands into one format group per registered basic format and a `512_256_1` size case under each format, unless format alignment rules skip that size.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type | `2d` | Selects the 2D sparse image path and fixes the direct test family. | [`createTransferQueueTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L479) |
| Image size | `512_256_1` | Sets the image extent and the amount of data copied through the image. | [`createTransferQueueTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L467-L499) |
| Format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT`, `VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8G8B8A8_SNORM` | Changes the image representation, memory layout, mip-level calculation, and possible comparison mask. | [`getBasicTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89) |
| Planes and mip levels | Runtime-derived | Determines the copy-region count and the byte ranges checked after readback. | [`getMipmapCount` and copy-region construction](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L185-L220), [`bufferImageCopy`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L312) |

## Behavior Parameters

The primary behavioral axis is the registered **format**. The image type and extent remain fixed, while each format exercises the same sparse-transfer contract with its own representation and comparison rules.

### Floating-point formats

`VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, and `VK_FORMAT_R32_SFLOAT` test the round trip for floating-point texel layouts. The runtime derives the mip count and copy sizes from the selected format's image properties.

### Unsigned integer formats

`VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, and `VK_FORMAT_R32_UINT` use the same bind and copy sequence with unsigned integer texel layouts.

### Signed integer formats

`VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, and `VK_FORMAT_R32_SINT` exercise signed integer texel layouts through the sparse image and transfer queue.

### Normalized formats

`VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R8G8B8A8_SNORM` test normalized texel layouts. The validator can ignore designated low bits on even byte positions when the format helpers mark them as don't-care.

## Shader Analysis

This test has no shader code. Its behavior comes from host-created images and buffers, sparse binding, transfer commands, barriers, and host-side byte comparison.

## Runtime Execution and Result Checking

1. The test requests one queue with `VK_QUEUE_SPARSE_BINDING_BIT | VK_QUEUE_TRANSFER_BIT` and creates the logical device around that requirement.
2. It creates an optimal-tiled image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, and `VK_IMAGE_USAGE_TRANSFER_DST_BIT`. It queries format properties and derives the mip count.
3. It allocates one device-memory object for each sparse memory slot, packages them in `VkSparseImageOpaqueMemoryBindInfo`, and submits `vkQueueBindSparse` with a signal semaphore.
4. It computes aligned `VkBufferImageCopy` regions for every plane and mip level. The input buffer receives the deterministic pattern `(byte index % image memory alignment) + 1` and the host flushes that allocation.
5. A command buffer makes the input buffer visible to transfer reads, changes the image to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, and executes `vkCmdCopyBufferToImage`.
6. The command buffer changes the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, executes `vkCmdCopyImageToBuffer` into a host-visible output buffer, and makes transfer writes visible to host reads.
7. The submission waits on the sparse-bind semaphore. After completion, the host invalidates the output allocation, waits for the queue to become idle, and compares each returned byte with the reference data.

A mismatch returns `tcu::TestStatus::fail("Failed")`. If every checked byte matches, the test returns `tcu::TestStatus::pass("Passed")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for floating-point formats. |
| `VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32_UINT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for unsigned integer formats. |
| `VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, `VK_FORMAT_R32_SINT` | Sparse binding, format-specific image layout, copy-region calculation, transfer, or readback mismatch for signed integer formats. |
| `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8G8B8A8_SNORM` | Sparse binding, normalized-format transfer, copy-region calculation, or readback mismatch after the permitted low-bit mask. |

### Cause Analysis

#### Sparse binding or queue ordering failures

**Possible failure symptoms:** The case reports `NotSupportedError` when no matching sparse-plus-transfer queue or memory type exists. If setup succeeds but the image data is wrong, the mismatch can affect one or more planes or mip levels.

**Possible implementation causes:** The implementation may reject the requested sparse image format or size, exceed `sparseAddressSpaceSize`, fail to provide a matching memory type, or fail to make the `vkQueueBindSparse` result visible before the transfer submission. The source establishes the semaphore ordering, but a more specific fault location requires investigation.

#### Image layout or transfer synchronization failures

**Possible failure symptoms:** The output buffer differs from the reference even though the test records the expected copy regions. A mismatch may appear across a complete image or only in ranges affected by one layout transition.

**Possible implementation causes:** The image may not support the requested transfer usage, or an implementation may mishandle the transition from undefined layout to transfer destination and then to transfer source. Incorrect visibility between host writes, transfer reads, transfer writes, and host reads is another possible cause. The test's source shows the required barriers; the failing implementation stage requires investigation.

#### Copy-region, plane, or mip calculation failures

**Possible failure symptoms:** Bytes at a consistent offset, plane, or mip level differ while other ranges match. The host checks the same calculated offsets and sizes that it used for the copies.

**Possible implementation causes:** Format properties, plane extents, mip dimensions, row or buffer alignment, or `VkBufferImageCopy` interpretation may disagree with the test's calculated layout. The current registered formats are single-plane, but the implementation builds plane-aware regions. The exact cause requires investigation if only a subset of ranges fails.

#### Format comparison or readback failures

**Possible failure symptoms:** The test fails on a format whose output differs only in bits that the format helper does not mark as don't-care, or it passes only when the expected mask is applied correctly.

**Possible implementation causes:** The transfer path may alter significant bits, or the comparison may expose a format-specific conversion or readback problem. For eligible formats the source masks low six or low four bits on even byte positions, so differences outside those masked bits remain failures. A fault in format handling or comparison assumptions requires investigation.

## Case Pruning

### Requirement-based pruning

- The support check requires the sparse binding device feature.
- The `512_256_1` extent must satisfy device image-size support and the format's alignment requirements. Registration skips a size when either the width or height is not aligned.
- The image format must support the requested sparse binding and transfer usage.
- The image's required memory size must fit within `sparseAddressSpaceSize`.
- The shared sparse base must find a queue supporting both `VK_QUEUE_SPARSE_BINDING_BIT` and `VK_QUEUE_TRANSFER_BIT`.
- The R64 support branch requires `VK_EXT_shader_image_atomic_int64` and `sparseImageInt64Atomics`, although this file's registered basic format list contains no R64 format.

### Design-based pruning

The registration fixes the image type to `2d` and uses one extent, `512_256_1`. It does not generate other image types or sizes in this test family. The basic format list also limits coverage to the listed floating-point, integer, and normalized formats.

## Key Takeaways

- The test checks a complete sparse-image transfer path, not just image creation or sparse-memory binding.
- The queue used for both `vkQueueBindSparse` and the transfer command must support sparse binding and transfer operations.
- Copy regions cover every runtime-derived plane and mip level, and the host validates the returned bytes after explicit visibility operations.
- Format-specific low-bit masks prevent designated don't-care bits from causing false failures, but significant-bit differences still fail the case.

## Source Reference Appendix

| Entry point or range | Link | Why it matters |
|----------------------|------|----------------|
| `getBasicTestFormats` | [`vktSparseResourcesTransferQueueTests.cpp#L61-L89`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89) | Lists the registered formats. |
| `SparseResourceTransferQueueCase::checkSupport` | [`vktSparseResourcesTransferQueueTests.cpp#L117-L133`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L117-L133) | Checks sparse binding, image size, and the R64 feature path. |
| Image and queue setup | [`vktSparseResourcesTransferQueueTests.cpp#L169-L229`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L169-L229) | Creates the queue and sparse image and checks image limits. |
| Opaque sparse bind submission | [`vktSparseResourcesTransferQueueTests.cpp#L233-L276`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L233-L276) | Allocates sparse memory and calls `vkQueueBindSparse`. |
| Copy regions and transfer commands | [`vktSparseResourcesTransferQueueTests.cpp#L278-L417`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L417) | Defines upload, layout transitions, readback, and host visibility. |
| Result validation | [`vktSparseResourcesTransferQueueTests.cpp#L421-L455`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L455) | Applies format masks and returns the test status. |
| Shared queue creation | [`vktSparseResourcesBase.cpp#L88-L194`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194) | Provides the sparse base queue and device setup used by the instance. |
| Vulkan sparse memory reference | [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc) | Provides the specification background for sparse resource memory. |
