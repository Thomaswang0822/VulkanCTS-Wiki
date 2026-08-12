## Overview

The `sparse_resources` test category collects tests that check sparse buffers and images across binding, residency, transfers, aliasing, rebinding, synchronization, and shader sparse-resource operations.

## Background Knowledge

- Sparse binding separates a resource's virtual address range from the physical memory ranges bound to it. A resource can therefore be fully backed, partially resident, or rebound while retaining the same Vulkan resource handle.
- `vkQueueBindSparse` submits sparse memory bindings and can wait on or signal semaphores and fences. Resource use must be ordered after the sparse bind has completed.
- Sparse images divide their memory requirements into opaque ranges, sparse image blocks, mip tails, and sometimes metadata or separate planes. The binding shape depends on the image type, format, extent, and reported sparse requirements.
- A nonresident read is governed by the device's sparse residency properties. Tests that require strict behavior check the specified zero result, while other tests focus on resident data and binding correctness.

## Category Structure

```text
sparse_resources
├── buffer
├── image_sparse_binding
├── device_group_image_sparse_binding
├── image_sparse_residency
├── aligned_mip_size
├── image_block_shapes
├── device_group_image_sparse_residency
├── mipmap_sparse_residency
├── device_group_mipmap_sparse_residency
├── multisampled_image_sparse_binding
├── multisampled_image_sparse_residency
├── image_sparse_memory_aliasing
├── device_group_image_sparse_memory_aliasing
├── shader_intrinsics
├── image_rebind
├── queue_bind
└── transfer_queue
```

The registration-only dispatcher [`vktSparseResourcesTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L45-L67) creates these direct families. The implementation-bearing families are grouped into the Level-3 pages below; the dispatcher itself has no separate technical page.

## How the Families Fit Together

The category follows the lifecycle of sparse resources from layout and binding through use and synchronization:

- **Resource layout and binding:** `aligned_mip_size`, `image_block_shapes`, `image_sparse_binding`, and `multisampled_image_sparse_binding` check reported sparse-image properties or fully bind resources before use.
- **Residency and mip coverage:** `image_sparse_residency`, `mipmap_sparse_residency`, and `multisampled_image_sparse_residency` leave selected regions unbound and check resident data plus the applicable nonresident behavior.
- **Resource identity and sharing:** `image_sparse_memory_aliasing` and `image_rebind` check shared bindings and replacement bindings, including the distinction between unchanged and rebound regions.
- **Operations and synchronization:** `buffer`, `shader_intrinsics`, `queue_bind`, and `transfer_queue` exercise sparse resources through buffer operations, shader instructions, sparse queue dependencies, and transfer round trips.
- **Device-group variants:** `device_group_image_sparse_binding`, `device_group_image_sparse_residency`, `device_group_mipmap_sparse_residency`, and `device_group_image_sparse_memory_aliasing` reuse the corresponding image behavior while adding device-group bind and peer-memory handling.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `buffer` and its transfer, descriptor, graphics, residency, aliasing, rebind, and indirect-operation families | [BufferTests.md](../testfiles/sparse_resources/BufferTests.md) | Sparse buffer behavior across data paths, partial residency, aliasing, rebinding, and indirect operations. |
| `image_sparse_binding`, `device_group_image_sparse_binding` | [ImageSparseBinding.md](../testfiles/sparse_resources/ImageSparseBinding.md) | Fully resident sparse-image opaque binds and regular versus device-group bind packaging. |
| `image_sparse_residency`, `device_group_image_sparse_residency` | [ImageSparseResidency.md](../testfiles/sparse_resources/ImageSparseResidency.md) | Partial image residency, compute verification, strict nonresident results, and mutable views. |
| `aligned_mip_size` | [ImageAlignedMipSize.md](../testfiles/sparse_resources/ImageAlignedMipSize.md) | Mip-tail alignment and consistency between sparse image properties. |
| `image_block_shapes` | [ImageBlockShapes.md](../testfiles/sparse_resources/ImageBlockShapes.md) | Standard sparse block-shape checks across image dimensions, samples, and formats. |
| `mipmap_sparse_residency`, `device_group_mipmap_sparse_residency` | [MipmapSparseResidency.md](../testfiles/sparse_resources/MipmapSparseResidency.md) | Residency binding and transfer validation across mip levels, tails, planes, and image types. |
| `multisampled_image_sparse_binding` | [MultisampledImageSparseBinding.md](../testfiles/sparse_resources/MultisampledImageSparseBinding.md) | Fully bound multisampled sparse storage images and sample-count validation. |
| `multisampled_image_sparse_residency` | [MultisampledImageSparseResidency.md](../testfiles/sparse_resources/MultisampledImageSparseResidency.md) | Partially resident multisampled images and strict nonresident results. |
| `image_sparse_memory_aliasing`, `device_group_image_sparse_memory_aliasing` | [ImageMemoryAliasing.md](../testfiles/sparse_resources/ImageMemoryAliasing.md) | Shared sparse image bindings, shader/transfer validation, and device-group aliasing. |
| `shader_intrinsics` | [ShaderIntrinsics.md](../testfiles/sparse_resources/ShaderIntrinsics.md) | Sparse fetch, read, sample, and gather instructions plus residency-status checking. |
| `image_rebind` | [ImageRebind.md](../testfiles/sparse_resources/ImageRebind.md) | Replacing one sparse image binding region and checking the resulting spatial boundary. |
| `queue_bind` | [QueueBindSparseTests.md](../testfiles/sparse_resources/QueueBindSparseTests.md) | Empty sparse-bind submissions and semaphore/fence dependency behavior. |
| `transfer_queue` | [TransferQueueTests.md](../testfiles/sparse_resources/TransferQueueTests.md) | Sparse image binding and transfer round trips on a combined sparse/transfer queue. |

## Category Notes

The category uses shared image and buffer helpers, so several Level-3 pages describe delegated implementation files rather than every helper as a separate page. Device-group roots are independently registered even when they reuse the regular implementation's resource matrix. Support checks and case pruning are part of the test contract: unsupported sparse formats, image types, queue capabilities, feature combinations, limits, and memory arrangements are excluded before execution.
