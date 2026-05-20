# vktSparseResourcesTests.cpp

## Overview

[`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L24-L67) is the top-level dispatcher for the `sparse_resources` Vulkan CTS category. The Vulkan API test plan identifies sparse resources as a feature area separate from basic memory management, but leaves its details as TBD ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)). The dispatcher includes sparse-resource subgroup headers and registers top-level children in [`createTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L45-L67).

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L1)
- Category header: [`vktSparseResourcesTests.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.hpp#L29-L35)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)

## Registration Hierarchy

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

## Test Families

### buffer — Sparse buffer umbrella

[`buffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2813-L2816) is registered first by the dispatcher through [`createSparseBufferTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L49). The implementation file creates a nested buffer test tree rather than a single flat case list; this page does not summarize those nested buffer branches because they require separate implementation inspection.

### image_sparse_binding — Image sparse binding

[`image_sparse_binding`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L714) is registered by [`createImageSparseBindingTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L50).

### device_group_image_sparse_binding — Device-group image sparse binding

[`device_group_image_sparse_binding`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L717-L720) is registered by [`createDeviceGroupImageSparseBindingTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L51), using the same common image sparse binding builder with its device-group mode enabled.

### image_sparse_residency — Image sparse residency

[`image_sparse_residency`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2143) is registered by [`createImageSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L52).

### aligned_mip_size — Aligned mip size

[`aligned_mip_size`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L250-L253) is registered by [`createImageAlignedMipSizeTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L53).

### image_block_shapes — Image block shapes

[`image_block_shapes`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L528-L531) is registered by [`createImageBlockShapesTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L54).

### device_group_image_sparse_residency — Device-group image sparse residency

[`device_group_image_sparse_residency`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2146-L2149) is registered by [`createDeviceGroupImageSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L55), using the same common image sparse residency builder with its device-group mode enabled.

### mipmap_sparse_residency — Mipmap sparse residency

[`mipmap_sparse_residency`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L654) is registered by [`createMipmapSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L56).

### device_group_mipmap_sparse_residency — Device-group mipmap sparse residency

[`device_group_mipmap_sparse_residency`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L657-L660) is registered by [`createDeviceGroupMipmapSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L57), using the same common mipmap sparse residency builder with its device-group mode enabled.

### multisampled_image_sparse_binding — Multisampled image sparse binding

[`multisampled_image_sparse_binding`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L710-L713) is registered by [`createSparseResourcesMultisampledImageSparseBindingTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L58).

### multisampled_image_sparse_residency — Multisampled image sparse residency

[`multisampled_image_sparse_residency`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L806-L809) is registered by [`createSparseResourcesMultisampledImageSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L59).

### image_sparse_memory_aliasing — Image sparse memory aliasing

[`image_sparse_memory_aliasing`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1097) is registered by [`createImageSparseMemoryAliasingTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L60).

### device_group_image_sparse_memory_aliasing — Device-group image sparse memory aliasing

[`device_group_image_sparse_memory_aliasing`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1100-L1104) is registered by [`createDeviceGroupImageSparseMemoryAliasingTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L61), using the same common image sparse memory aliasing builder with its device-group mode enabled.

### shader_intrinsics — Shader sparse intrinsics

[`shader_intrinsics`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L51-L54) is registered by [`createSparseResourcesShaderIntrinsicsTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L62).

### image_rebind — Image sparse rebind

[`image_rebind`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L900-L903) is registered by [`createImageSparseRebindTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L63).

### queue_bind — Sparse queue binding

[`queue_bind`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L502-L505) is registered by [`createQueueBindSparseTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L64). The implementation comment states that it covers sparse queue binding edge cases and synchronization with semaphores/fences while other test groups cover actual sparse binding and usage ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L501)).

### transfer_queue — Sparse resources on transfer queues

[`transfer_queue`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L473) is registered by [`createTransferQueueTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L65).

## Parameter Dimensions

This dispatcher does not define the implementation parameter matrices. It establishes the category root and delegates to included subgroup factories in a fixed order ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L24-L37), [`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L49-L65)). Some child files expose parameter arrays, such as image type, image size, and format vectors in `aligned_mip_size` ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L254-L259)), but their full matrices are outside this root-dispatcher page.

## Support / Feature Requirements

No device support checks are implemented directly in this dispatcher. Feature and capability requirements are delegated to the registered implementation files.

## Verification Methods

No pass/fail verification logic is implemented directly in this dispatcher. Verification is performed by the registered implementation files.

## Test Principles Observed

- The category root separates registration from implementation by including subgroup headers and forwarding to factory functions ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L24-L37), [`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L49-L65)).
- Device-group variants are represented as separate top-level registered branches where their implementation files construct distinct group names and pass device-group mode into common builders ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L717-L720), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2146-L2149), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L657-L660), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1100-L1104)).

## Notes / Uncertainties

- This page documents the root dispatcher and verified top-level registered group names. Detailed child behavior is covered by the implementation Level-3 pages in this category.
- The category Level-2 summary is available at [`sparse_resources.md`](../../categories/sparse_resources.md).
