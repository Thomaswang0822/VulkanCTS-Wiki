# vktSparseResourcesTransferQueueTests.cpp

## Overview

[`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L1) registers the [`sparse_resources.transfer_queue`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L509) branch for sparse image operations on a queue that supports both sparse binding and transfer operations. The file creates sparse images, binds opaque sparse memory, copies buffer data into and back out of the image on the transfer queue, and byte-compares the result with format-specific masks ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L169-L455)).

## Role

Implementation file for sparse image transfer-queue cases.

## Source Code

- Primary source: [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L1)
- Parent dispatcher registration: [`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L65)
- Shared sparse base inspected for queue/device creation: [`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194)

## Registration Hierarchy

```text
sparse_resources.transfer_queue
└── 2d
```

## Test Families

### 2d — 2D sparse image transfer round-trip

The only direct child is the `2d` image-type group, created from an `imageParameters` entry with `IMAGE_TYPE_2D`, one image size `512_256_1`, and the basic format list returned by `getBasicTestFormats()` ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L479)). Under that direct child, the file creates one format group per basic format and one size-named case under each format group, after checking the image size alignment for formats that need aligned dimensions ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L480-L507)).

The implementation requests a queue with both `VK_QUEUE_SPARSE_BINDING_BIT` and `VK_QUEUE_TRANSFER_BIT`, creates an optimal-tiled sparse image with transfer source/destination usage, queries format properties, computes mip levels, and binds every opaque sparse-memory slot through `vkQueueBindSparse` on the transfer queue ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L169-L220), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L222-L276)). It then builds buffer-image-copy regions for every plane and mip level, uploads patterned bytes from a host-visible input buffer into the sparse image, transitions the image for transfer source use, copies back into a host-visible output buffer, and compares every byte against the reference data with low-bit masks for formats whose low bits are don't-care ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L455)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct child | Only `2d` is created as a direct child of `transfer_queue` in the inspected `imageParameters` list ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L479)). |
| Image size | The sole registered size is `512_256_1`, subject to per-format alignment skips ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L467-L499)). |
| Formats | Basic formats include R32G32B32A32/R16G16B16A16/R32 float, uint, and sint subsets plus R8G8B8A8 UNORM/SNORM as listed by `getBasicTestFormats()` ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89)). |
| Mip levels and planes | The runtime computes mip levels from image format properties and creates copy regions for every plane and mip level ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L218-L220), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L312)). |

## Support / Feature Requirements

Each case requires sparse binding support ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L117-L120)). The support check rejects unsupported image sizes, and R64 formats require `VK_EXT_shader_image_atomic_int64` plus `sparseImageInt64Atomics`, although the current basic format list shown in this file contains no R64 format ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L121-L133), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L61-L89)). At runtime, unsupported sparse image formats are rejected through `getPhysicalDeviceImageFormatProperties`, and required memory size is checked against `sparseAddressSpaceSize` ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L210-L216), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L225-L229)). The shared sparse base reports `NotSupportedError` if the requested sparse+transfer queue cannot be found ([`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L158-L194)).

## Verification Methods

The test writes deterministic byte values to the input buffer, flushes it, copies into the sparse image, copies back to the output buffer, invalidates output memory, and checks each byte against the reference data ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L323-L343), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L365-L417), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L455)). For formats with don't-care low bits, the comparison masks the low six or four bits for even byte positions before comparing ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L449)).

## Test Principles Observed

- The branch verifies that sparse image opaque binding and transfer operations work on the same transfer-capable sparse queue, not merely that image creation succeeds ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L174-L183), [`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L274-L276)).
- Copy coverage is generated over all planes and mip levels for the runtime-created sparse image ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L278-L312)).
- Pass/fail is based on host-visible output data, with format-specific masking where the helper functions identify don't-care low bits ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L455)).

## Notes / Uncertainties

- Only one direct child, `2d`, is visible in the inspected registration tree; deeper format and size groups are documented in `## Test Families` rather than expanded in the parseable one-level hierarchy ([`vktSparseResourcesTransferQueueTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L507)).
