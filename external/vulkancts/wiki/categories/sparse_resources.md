# sparse_resources

## Overview

The [`sparse_resources`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L45-L67) category documents Vulkan CTS coverage for sparse buffers, sparse images, sparse residency, sparse aliasing, sparse rebind behavior, queue sparse-binding synchronization, and shader sparse-resource intrinsics. The top-level dispatcher registers seventeen verified subgroup roots in [`createTests()`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L45-L67). The Vulkan API test plan identifies sparse memory resources as separate from basic memory management but leaves detailed sparse-resource behavior as TBD, so this page relies primarily on inspected sparse-resource source files and generated Level-3 evidence ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L273-L276)).

## Registration Entry Point

The category is rooted in [`vktSparseResourcesTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L45-L67). It creates the category group and adds the following verified registered top-level children:

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

## Subgroup Structure and Major Themes

- [`buffer`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2813-L2816): sparse buffer coverage across transfer, SSBO/UBO, texel-buffer, vertex/index/indirect, transform-feedback, indirect-dispatch, null-address, indirect memory-copy, sparse binding, residency, aliasing, and rebind paths.
- [`image_sparse_binding`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L714) and [`device_group_image_sparse_binding`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L717-L720): fully bound sparse images, varying how opaque sparse binds are packaged for [`vkQueueBindSparse`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L417).
- [`image_sparse_residency`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2143) and [`device_group_image_sparse_residency`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2146-L2149): partially resident sparse images with resident/nonresident block checks; the regular root also registers [`mutable`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2135).
- [`aligned_mip_size`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L250-L285): consistency between sparse image format flags, image granularity, and [`imageMipTailFirstLod`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L188-L239).
- [`image_block_shapes`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L528-L579): standard sparse block-shape conformance for image dimensions, sample counts, compressed formats, bits-per-pixel classes, and YCbCr block extents.
- [`mipmap_sparse_residency`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L654) and [`device_group_mipmap_sparse_residency`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L657-L660): sparse image residency over all generated mip levels, mip tails, and metadata.
- [`multisampled_image_sparse_binding`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L710-L713): sparse-bound multisampled storage images verified by compute shader output.
- [`multisampled_image_sparse_residency`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L806-L809): partially resident multisampled images, leaving one sparse-tile row unbound and checking strict nonresident zero behavior.
- [`image_sparse_memory_aliasing`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1097) and [`device_group_image_sparse_memory_aliasing`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1100-L1104): two sparse images aliased to the same regular residency binds, with transfer/shader verification.
- [`shader_intrinsics`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L51-L160): SPIR-V sparse fetch/read/sample/gather operations across selected image types, checking texel values and residency-status outputs.
- [`image_rebind`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L900-L903): sparse image rebinding from one memory object to another, then rebinding one sparse block back to the first memory object.
- [`queue_bind`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L500-L505): sparse queue-binding edge cases for semaphore/fence synchronization, intentionally using empty resource bind counts.
- [`transfer_queue`](../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L465-L509): sparse image opaque binding and transfer round trips on a queue that supports both sparse binding and transfer.

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktSparseResourcesTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L1) | Registration | Top-level category dispatcher and verified root subgroup order |
| [`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1) | Implementation-heavy registration | Sparse-buffer usage tree plus calls into buffer sparse-binding, residency, aliasing, and rebind helpers |
| [`vktSparseResourcesBufferSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L1) | Helper implementation | Nested sparse-buffer binding cases used by [`buffer`](../testfiles/sparse_resources/vktSparseResourcesBufferTests.md) |
| [`vktSparseResourcesBufferSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1) | Helper implementation | Nested sparse-buffer residency and texel-buffer sparse-operation cases used by [`buffer`](../testfiles/sparse_resources/vktSparseResourcesBufferTests.md) |
| [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L1) | Helper implementation | Nested sparse-buffer memory aliasing cases used by [`buffer`](../testfiles/sparse_resources/vktSparseResourcesBufferTests.md) |
| [`vktSparseResourcesBufferRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L1) | Helper implementation | Nested sparse-buffer rebind cases used by [`buffer`](../testfiles/sparse_resources/vktSparseResourcesBufferTests.md) |
| [`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L1) | Implementation-heavy registration | Regular and device-group fully resident sparse-image binding roots |
| [`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1) | Implementation-heavy registration | Regular and device-group partially resident sparse-image roots plus regular-only mutable subtree |
| [`vktSparseResourcesImageAlignedMipSize.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L1) | Implementation | Sparse image mip-tail alignment/property consistency |
| [`vktSparseResourcesImageBlockShapes.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L1) | Implementation | Standard sparse image block-shape checks |
| [`vktSparseResourcesMipmapSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L1) | Implementation-heavy registration | Regular and device-group mipmapped sparse-image residency |
| [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L1) | Implementation | Multisampled sparse image binding |
| [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L1) | Implementation | Multisampled sparse image residency |
| [`vktSparseResourcesImageMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1) | Implementation-heavy registration | Regular and device-group sparse image memory aliasing |
| [`vktSparseResourcesShaderIntrinsics.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L1) | Registration / implementation hub | Registers sparse intrinsic operation/type roots and delegates to sampled, storage, and base helpers |
| [`vktSparseResourcesShaderIntrinsicsBase.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L549-L1238) | Helper implementation | Shared sparse image setup, bind pattern, and texel/residency verification for shader intrinsics |
| [`vktSparseResourcesShaderIntrinsicsSampled.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsSampled.cpp#L135-L984) | Helper implementation | Sampled sparse image operations through graphics rendering |
| [`vktSparseResourcesShaderIntrinsicsStorage.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L50-L802) | Helper implementation | Storage/fetch/read sparse image operations through compute dispatch |
| [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L1) | Implementation | Sparse image memory-object rebind behavior |
| [`vktSparseResourcesQueueBindSparseTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L1) | Implementation | Sparse queue-bind synchronization and empty submission cases |
| [`vktSparseResourcesTransferQueueTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L1) | Implementation | Sparse image transfer queue round-trip checks |
| [`vktSparseResourcesBase.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194) | Shared support helper | Device/queue construction for sparse, compute, graphics, transfer, and device-group paths |
| [`vktSparseResourcesTestsUtil.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Shared utility | Image type names, format lists, image-size helpers, and sparse support helpers |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1) | [`vktSparseResourcesBufferTests.md`](../testfiles/sparse_resources/vktSparseResourcesBufferTests.md) |
| [`vktSparseResourcesImageAlignedMipSize.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L1) | [`vktSparseResourcesImageAlignedMipSize.md`](../testfiles/sparse_resources/vktSparseResourcesImageAlignedMipSize.md) |
| [`vktSparseResourcesImageBlockShapes.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L1) | [`vktSparseResourcesImageBlockShapes.md`](../testfiles/sparse_resources/vktSparseResourcesImageBlockShapes.md) |
| [`vktSparseResourcesImageMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1) | [`vktSparseResourcesImageMemoryAliasing.md`](../testfiles/sparse_resources/vktSparseResourcesImageMemoryAliasing.md) |
| [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L1) | [`vktSparseResourcesImageRebind.md`](../testfiles/sparse_resources/vktSparseResourcesImageRebind.md) |
| [`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L1) | [`vktSparseResourcesImageSparseBinding.md`](../testfiles/sparse_resources/vktSparseResourcesImageSparseBinding.md) |
| [`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1) | [`vktSparseResourcesImageSparseResidency.md`](../testfiles/sparse_resources/vktSparseResourcesImageSparseResidency.md) |
| [`vktSparseResourcesMipmapSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L1) | [`vktSparseResourcesMipmapSparseResidency.md`](../testfiles/sparse_resources/vktSparseResourcesMipmapSparseResidency.md) |
| [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L1) | [`vktSparseResourcesMultisampledImageSparseBinding.md`](../testfiles/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.md) |
| [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L1) | [`vktSparseResourcesMultisampledImageSparseResidency.md`](../testfiles/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.md) |
| [`vktSparseResourcesQueueBindSparseTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L1) | [`vktSparseResourcesQueueBindSparseTests.md`](../testfiles/sparse_resources/vktSparseResourcesQueueBindSparseTests.md) |
| [`vktSparseResourcesShaderIntrinsics.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L1) | [`vktSparseResourcesShaderIntrinsics.md`](../testfiles/sparse_resources/vktSparseResourcesShaderIntrinsics.md) |
| [`vktSparseResourcesTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L1) | [`vktSparseResourcesTests.md`](../testfiles/sparse_resources/vktSparseResourcesTests.md) |
| [`vktSparseResourcesTransferQueueTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L1) | [`vktSparseResourcesTransferQueueTests.md`](../testfiles/sparse_resources/vktSparseResourcesTransferQueueTests.md) |

## Recurring Families and Themes

- Sparse binding is repeatedly exercised through [`vkQueueBindSparse`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L417), including opaque image binds, image residency binds, buffer binds, semaphore handoff, and empty submissions.
- Residency tests intentionally leave holes or alternating sparse blocks/mips unbound, then check resident data and, when strict behavior is required, zero-like nonresident results ([`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L531-L555), [`vktSparseResourcesShaderIntrinsicsBase.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L723-L845), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L383-L457)).
- Device-group variants are represented as separate top-level registered roots for image binding, image residency, mipmap residency, and image memory aliasing; those roots reuse common builders while enabling device-group sparse-bind metadata and peer-memory checks ([`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L279-L299), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L362-L382), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L438-L448)).
- Several image tests share an image-type matrix of 2D, 2D array, cube, cube array, and 3D, using shared helpers for layer counts, format IDs, and image type names ([`vktSparseResourcesTestsUtil.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118), [`vktSparseResourcesTestsUtil.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L182-L205)).
- Verification is usually data-path based rather than only API-success based: copies, shader writes/reads, compute outputs, rendered images, fence waits, or metadata comparisons determine pass/fail.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Resource class | Buffer branches cover transfer, descriptors, vertex/index/indirect, transform-feedback, indirect-dispatch, null-address, and indirect memory-copy uses in [`populateTestGroup()`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808); image branches cover sparse binding, residency, metadata, block shape, aliasing, rebind, multisample, transfer, and shader intrinsic uses. |
| Image type | 2D, 2D array, cube, cube array, and 3D recur in aligned-mip-size, block-shapes, residency, mipmap residency, aliasing, rebind, and shader-intrinsic matrices ([`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2045), [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L868)). |
| Format set | Shared formats come from [`getTestFormats()`](../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118); some branches append alpha-only or compressed formats, filter YCbCr formats, or require R64-specific features ([`vktSparseResourcesImageBlockShapes.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L488-L525), [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L870-L879)). |
| Image size | Most image branches use multiple power-of-two and odd-size extents, with per-format alignment skips for formats requiring larger image-size alignment ([`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L635-L688), [`vktSparseResourcesShaderIntrinsics.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L55-L117)). |
| Sample count | Block-shape and multisampled image branches cover sparse-residency sample-count features, including 2/4/8/16 in residency and 2/4/8/16/32/64 in multisampled binding where supported ([`vktSparseResourcesImageBlockShapes.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L539-L579), [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L682-L701)). |
| Bind/residency mode | Buffer and image tests vary sparse binding, sparse residency, aliased residency, nonresident strict behavior, full-vs-partial binding, and sparse rebind state ([`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2597), [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L307-L448)). |
| Queue and synchronization | Queue-bind tests vary queue count, wait/signal semaphore counts, empty submission, and bind-sparse fence use ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L337-L496)). |
| Shader sparse operation | Shader intrinsics combine image types with sparse fetch, sparse read, sparse sample explicit/implicit LOD, sparse gather, optional `Nontemporal`, formats, and sizes ([`vktSparseResourcesShaderIntrinsics.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L73-L157)). |

## Recurring Support / Feature Gates

Common sparse-resource support gates include core sparse binding, sparse residency for buffers or image dimensions, sparse residency aliasing, strict nonresident behavior, and sparse address-space limits ([`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2016-L2032), [`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L337), [`vktSparseResourcesTransferQueueTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L210-L229)). Image branches commonly check concrete sparse image-format support and image-size limits before creating sparse images ([`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L107-L129), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L137-L240)).

Observed feature or extension gates include sample-count sparse residency features, [`shaderStorageImageMultisample`](../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L159-L184), [`shaderResourceResidency`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.hpp#L116-L133), [`VK_EXT_shader_image_atomic_int64`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L140-L154), [`VK_KHR_maintenance5`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L107-L129), [`VK_EXT_transform_feedback`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2016-L2032), [`VK_KHR_copy_memory_indirect`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2509-L2520), and [`VK_KHR_buffer_device_address`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2509-L2520). Device-group paths require the shared base to create a device-group-capable environment and to find required peer-memory features ([`vktSparseResourcesBase.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L109-L131), [`vktSparseResourcesImageMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L307-L340)).

## Recurring Verification Methods

- Host-visible byte or value comparisons after copy-in/copy-out are used by sparse image binding, mipmap residency, transfer queue, sparse-buffer binding/residency, and related helpers ([`vktSparseResourcesImageSparseBinding.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L520-L604), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L508-L582), [`vktSparseResourcesTransferQueueTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp#L421-L455)).
- Shader or compute output checks validate storage-image writes, sparse intrinsic residency codes, multisampled image values, buffer aliasing, indirect dispatch, and null-address behavior ([`vktSparseResourcesImageSparseResidency.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L882-L1205), [`vktSparseResourcesShaderIntrinsicsBase.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L1160-L1238), [`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1970-L1980)).
- Rendered-image checks are used by several sparse-buffer graphics-resource paths, where error-colored pixels fail the case ([`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462), [`vktSparseResourcesBufferTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L702-L713)).
- Property and metadata tests compare reported sparse image granularity, standard block shapes, and mip-tail information against expected values or device-property rules ([`vktSparseResourcesImageAlignedMipSize.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageAlignedMipSize.cpp#L188-L239), [`vktSparseResourcesImageBlockShapes.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp#L221-L478)).
- Sparse queue synchronization tests wait on fences and semaphore-dependent submissions to prove [`vkQueueBindSparse`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L221-L232) signaling and waiting behavior ([`vktSparseResourcesQueueBindSparseTests.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesQueueBindSparseTests.cpp#L261-L304)).
- Rebind and aliasing tests use spatial or multi-resource expectations: aliasing verifies shared sparse binds and shader-written data, while rebind verifies one partially rebound block differs from the surrounding image ([`vktSparseResourcesImageMemoryAliasing.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L929), [`vktSparseResourcesImageRebind.cpp`](../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L723-L833)).

## Relationship to the Test Plan

[`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L273-L276) states that sparse memory resources are separate from basic memory management but does not specify detailed sparse-resource coverage. The implementation evidence therefore comes from [`modules/vulkan/sparse_resources/`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L24-L37) and the Level-3 pages listed above.

## Notes / Uncertainties

- This Level-2 summary is based on the inspected generated Level-3 pages and selected source links under [`modules/vulkan/sparse_resources/`](../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L24-L37).
- Level-3 hierarchy trees intentionally expand one parseable level below each documented root; many files generate deeper format, image-size, sample-count, operand, and helper-case leaves that are summarized in prose rather than fully enumerated here.
- Several helper implementation files materially affect behavior but do not register independent top-level category roots in the inspected dispatcher, so they are listed as helper inventory rather than separate Level-3 pages.
