# image

## Overview

The [`image`](../../modules/vulkan/image/vktImageTests.cpp#L1) category documents Vulkan image tests registered by [`createTests()`](../../modules/vulkan/image/vktImageTests.cpp#L104). In the inspected files, this category covers a wide range of image functionality including load/store operations, sampling, compression/transcoding, format compatibility, layout management, atomic operations, and host image copy features.

The historical Vulkan API test plan provides useful high-level image background: image creation should cover supported parameter combinations, sizes, linear-layout CPU access, and nearest-sampling checks, while image views and render-target views should cover compatible views, swizzles, depth/stencil modes, partial mip or array ranges, and color/depth/stencil attachment writes ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L466-L515)). Treat that as category-purpose context only; the current source and mustpass files below define active registration, parameters, support gates, and verification behavior.

## Registration Entry Point

The category is rooted in [`createChildren()`](../../modules/vulkan/image/vktImageTests.cpp#L61), which adds thirty-one subgroups:

```text
image
├── store
├── load_store
├── load_store_multisample
├── mutable
├── swapchain_mutable
├── format_reinterpret
├── qualifiers
├── image_size
├── atomic_operations
├── texel_view_compatible
├── extended_usage_bit
├── extend_operands_spirv1p4
├── nontemporal_operand (non-VulkanSC only)
├── astc_decode_mode
├── misaligned_cube
├── load_store_lod
├── subresource_layout
├── mismatched_formats
├── mismatched_write_op
├── sample_cubemap
├── depth_stencil_descriptor
├── sample_texture
├── extended_usage_bit_compatibility
├── queue_transfer
├── concurrent_copy
├── host_image_copy (non-VulkanSC only)
├── depth_stencil_separate_access
├── non_uniform_offset_sample
├── device_scope_access
├── 2d_array_compatible
└── general_layout
```

Source: [`vktImageTests.cpp`](../../modules/vulkan/image/vktImageTests.cpp#L61).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktImageTests.cpp`](../../modules/vulkan/image/vktImageTests.cpp#L1) | Registration | Top-level image category registration |
| [`vktImageLoadStoreTests.cpp`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1) | Implementation | Store, load_store, format_reinterpret, extend_operands_spirv1p4, nontemporal_operand, device_scope_access, load_store_lod |
| [`vktImageMultisampleLoadStoreTests.cpp`](../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L1) | Implementation | Multisample load_store tests |
| [`vktImageMutableTests.cpp`](../../modules/vulkan/image/vktImageMutableTests.cpp#L1) | Implementation | Mutable format and swapchain mutable tests |
| [`vktImageMismatchedFormatsTests.cpp`](../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1) | Implementation | Mismatched format read operations |
| [`vktImageMismatchedWriteOpTests.cpp`](../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1) | Implementation | Mismatched write operations |
| [`vktImageQualifiersTests.cpp`](../../modules/vulkan/image/vktImageQualifiersTests.cpp#L1) | Implementation | Memory qualifier tests (coherent, volatile, restrict) |
| [`vktImageSizeTests.cpp`](../../modules/vulkan/image/vktImageSizeTests.cpp#L1) | Implementation | Image size query tests |
| [`vktImageAtomicOperationTests.cpp`](../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1) | Implementation | Atomic operations on images |
| [`vktImageCompressionTranscodingSupport.cpp`](../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1) | Implementation | Texel view compatible compression/transcoding |
| [`vktImageTranscodingSupportTests.cpp`](../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1) | Implementation | Extended usage bit tests |
| [`vktImageAstcDecodeModeTests.cpp`](../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1) | Implementation | ASTC decode mode override tests |
| [`vktImageMisalignedCubeTests.cpp`](../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1) | Implementation | Misaligned cube image tests |
| [`vktImageSubresourceLayoutTests.cpp`](../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L1) | Implementation | Subresource layout query and invariance |
| [`vktImageGeneralLayoutTests.cpp`](../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1) | Implementation | General layout tests (ASTC sample, memory barriers, input attachments, MSAA) |
| [`vktImageTransfer.cpp`](../../modules/vulkan/image/vktImageTransfer.cpp#L1) | Implementation | Queue transfer tests |
| [`vktImageConcurrentCopyTests.cpp`](../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L1) | Implementation | Concurrent copy tests |
| [`vktImageHostImageCopyTests.cpp`](../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1) | Implementation | Host image copy (VK_EXT_host_image_copy; non-VulkanSC only) |
| [`vktImageSampleCompressedTextureTests.cpp`](../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L1) | Implementation | Compressed texture sampling tests |
| [`vktImageSampleDrawnCubeFaceTests.cpp`](../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1) | Implementation | Cubemap face sampling tests |
| [`vktImageDepthStencilDescriptorTests.cpp`](../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1) | Implementation | Depth/stencil descriptor tests |
| [`vktImageDepthStencilSeparateTests.cpp`](../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1) | Implementation | Separate depth/stencil access tests |
| [`vktImageNonUniformOffsetSampleTests.cpp`](../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L1) | Implementation | Non-uniform offset sampling tests |
| [`vktImage2dArrayCompatibleTests.cpp`](../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L1) | Implementation | 2D array compatible 3D image tests |
| [`vktImageExtendedUsageBitTests.cpp`](../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L1) | Implementation | Extended usage bit compatibility tests |
| [`vktImageTestsUtil.hpp`](../../modules/vulkan/image/vktImageTestsUtil.hpp#L1) | Helper | Shared image test utilities |
| [`vktImageLoadStoreUtil.hpp`](../../modules/vulkan/image/vktImageLoadStoreUtil.hpp#L1) | Helper | Load/store specific utilities |
| [`vktImageTexture.hpp`](../../modules/vulkan/image/vktImageTexture.hpp#L1) | Helper | Texture helper definitions |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktImageLoadStoreTests.cpp`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1) | [`vktImageLoadStoreTests.md`](../testfiles/image/vktImageLoadStoreTests.md) |
| [`vktImageMultisampleLoadStoreTests.cpp`](../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L1) | [`vktImageMultisampleLoadStoreTests.md`](../testfiles/image/vktImageMultisampleLoadStoreTests.md) |
| [`vktImageMutableTests.cpp`](../../modules/vulkan/image/vktImageMutableTests.cpp#L1) | [`vktImageMutableTests.md`](../testfiles/image/vktImageMutableTests.md) |
| [`vktImageMismatchedFormatsTests.cpp`](../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1) | [`vktImageMismatchedFormatsTests.md`](../testfiles/image/vktImageMismatchedFormatsTests.md) |
| [`vktImageMismatchedWriteOpTests.cpp`](../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1) | [`vktImageMismatchedWriteOpTests.md`](../testfiles/image/vktImageMismatchedWriteOpTests.md) |
| [`vktImageQualifiersTests.cpp`](../../modules/vulkan/image/vktImageQualifiersTests.cpp#L1) | [`vktImageQualifiersTests.md`](../testfiles/image/vktImageQualifiersTests.md) |
| [`vktImageSizeTests.cpp`](../../modules/vulkan/image/vktImageSizeTests.cpp#L1) | [`vktImageSizeTests.md`](../testfiles/image/vktImageSizeTests.md) |
| [`vktImageAtomicOperationTests.cpp`](../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1) | [`vktImageAtomicOperationTests.md`](../testfiles/image/vktImageAtomicOperationTests.md) |
| [`vktImageCompressionTranscodingSupport.cpp`](../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1) | [`vktImageCompressionTranscodingSupport.md`](../testfiles/image/vktImageCompressionTranscodingSupport.md) |
| [`vktImageTranscodingSupportTests.cpp`](../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1) | [`vktImageTranscodingSupportTests.md`](../testfiles/image/vktImageTranscodingSupportTests.md) |
| [`vktImageAstcDecodeModeTests.cpp`](../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1) | [`vktImageAstcDecodeModeTests.md`](../testfiles/image/vktImageAstcDecodeModeTests.md) |
| [`vktImageMisalignedCubeTests.cpp`](../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L1) | [`vktImageMisalignedCubeTests.md`](../testfiles/image/vktImageMisalignedCubeTests.md) |
| [`vktImageSubresourceLayoutTests.cpp`](../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L1) | [`vktImageSubresourceLayoutTests.md`](../testfiles/image/vktImageSubresourceLayoutTests.md) |
| [`vktImageGeneralLayoutTests.cpp`](../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1) | [`vktImageGeneralLayoutTests.md`](../testfiles/image/vktImageGeneralLayoutTests.md) |
| [`vktImageTransfer.cpp`](../../modules/vulkan/image/vktImageTransfer.cpp#L1) | [`vktImageTransfer.md`](../testfiles/image/vktImageTransfer.md) |
| [`vktImageConcurrentCopyTests.cpp`](../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L1) | [`vktImageConcurrentCopyTests.md`](../testfiles/image/vktImageConcurrentCopyTests.md) |
| [`vktImageHostImageCopyTests.cpp`](../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1) | [`vktImageHostImageCopyTests.md`](../testfiles/image/vktImageHostImageCopyTests.md) |
| [`vktImageSampleCompressedTextureTests.cpp`](../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L1) | [`vktImageSampleCompressedTextureTests.md`](../testfiles/image/vktImageSampleCompressedTextureTests.md) |
| [`vktImageSampleDrawnCubeFaceTests.cpp`](../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1) | [`vktImageSampleDrawnCubeFaceTests.md`](../testfiles/image/vktImageSampleDrawnCubeFaceTests.md) |
| [`vktImageDepthStencilDescriptorTests.cpp`](../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1) | [`vktImageDepthStencilDescriptorTests.md`](../testfiles/image/vktImageDepthStencilDescriptorTests.md) |
| [`vktImageDepthStencilSeparateTests.cpp`](../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1) | [`vktImageDepthStencilSeparateTests.md`](../testfiles/image/vktImageDepthStencilSeparateTests.md) |
| [`vktImageNonUniformOffsetSampleTests.cpp`](../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L1) | [`vktImageNonUniformOffsetSampleTests.md`](../testfiles/image/vktImageNonUniformOffsetSampleTests.md) |
| [`vktImage2dArrayCompatibleTests.cpp`](../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L1) | [`vktImage2dArrayCompatibleTests.md`](../testfiles/image/vktImage2dArrayCompatibleTests.md) |
| [`vktImageExtendedUsageBitTests.cpp`](../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L1) | [`vktImageExtendedUsageBitTests.md`](../testfiles/image/vktImageExtendedUsageBitTests.md) |

## Major Themes

### Image Load/Store Operations

The image category includes extensive tests for shader image load/store operations:
- [`store`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408) - Plain imageStore() cases with and without format qualifiers
- [`load_store`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3511) - Combined load and store operations
- [`load_store_multisample`](../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L572) - Atomic and non-atomic multisample operations
- [`format_reinterpret`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3732) - Format reinterpretation in shaders
- [`extend_operands_spirv1p4`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3819) - SPIR-V 1.4 OpImage*Operands extended tests
- [`nontemporal_operand`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3897) - Nontemporal memory hints
- [`device_scope_access`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3936) - Device-scope memory access patterns
- [`load_store_lod`](../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3677) - LOD-based image load operations

### Format Compatibility and Mutation

Tests for mutable and mismatched format scenarios:
- [`mutable`](../../modules/vulkan/image/vktImageMutableTests.cpp#L1856) - Mutable image format tests with format lists
- [`swapchain_mutable`](../../modules/vulkan/image/vktImageMutableTests.cpp#L2372) - Swapchain image format mutation
- [`mismatched_formats`](../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L481) - Mismatched image/texel format read operations
- [`mismatched_write_op`](../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1082) - Mismatched vector sizes and signedness in OpImageWrite

### Compression and Transcoding

Tests for compressed format handling:
- [`texel_view_compatible`](../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3803) - Block texel view compatible compression
- [`extended_usage_bit`](../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1203) - Extended usage bit for transcoding
- [`astc_decode_mode`](../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L572) - ASTC decode mode override (UNORM vs SFLOAT)

### Image Sampling

Dedicated sampling tests:
- [`sample_texture`](../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L888) - Sampling compressed textures through views
- [`sample_cubemap`](../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L583) - Cubemap face sampling
- [`non_uniform_offset_sample`](../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L718) - Non-uniform offsets with texture*Offset
- [`qualifiers`](../../modules/vulkan/image/vktImageQualifiersTests.cpp#L698) - Memory qualifiers (coherent, volatile, restrict)
- [`image_size`](../../modules/vulkan/image/vktImageSizeTests.cpp#L579) - GLSL imageSize() builtin

### Layout and Transfer

Tests for image layouts and transfer operations:
- [`subresource_layout`](../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L822) - vkGetImageSubresourceLayout and invariance
- [`general_layout`](../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2306) - General layout tests (ASTC sample, memory barriers, input attachments, MSAA)
- [`queue_transfer`](../../modules/vulkan/image/vktImageTransfer.cpp#L311) - Buffer-image copy operations
- [`concurrent_copy`](../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L664) - Concurrent copy operations
- [`host_image_copy`](../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L5001) - Host-based image copy (VK_EXT_host_image_copy)

### Depth/Stencil

Depth and stencil image tests:
- [`depth_stencil_descriptor`](../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1622) - Depth/stencil as descriptors
- [`depth_stencil_separate_access`](../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1413) - Separate depth/stencil framebuffer access
- [`misaligned_cube`](../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L394) - Misaligned cube image base layer

### Atomic Operations

- [`atomic_operations`](../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2479) - Image atomic operations (add, sub, min, max, exchange, etc.)

### Compatibility and Maintenance

Tests for compatibility and maintenance extensions:
- [`2d_array_compatible`](../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L466) - 2D array compatible 3D images
- [`extended_usage_bit_compatibility`](../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L285) - Extended usage bit format compatibility

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Image types | 1D, 1D_array, 2D, 2D_array, 3D, cube, cube_array, buffer |
| Formats | Float (R32G32B32A32_SFLOAT), Uint (R32G32B32A32_UINT), Sint (R32G32B32A32_SINT), Unorm (R8G8B8A8_UNORM), Snorm (R8G8B8A8_SNORM), SRGB |
| Sample counts | 2, 4, 8, 16, 32, 64 |
| Tiling modes | Optimal, linear |
| Image layouts | General, transfer_src, transfer_dst, shader_read_only, shader_write |
| Upload methods | Clear, copy, store, draw |
| Download methods | Copy, load, texture |

## Recurring Support Requirements

- `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` for storage images
- `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` / `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` for transfer tests
- `VK_KHR_maintenance2` for mutable formats and extended usage
- `VK_KHR_maintenance6` for multi-layer views
- `VK_KHR_synchronization2` for synchronization tests
- `VK_EXT_host_image_copy` for host image copy tests
- `VK_EXT_astc_decode_mode` for ASTC decode mode tests
- `VK_AMD_shader_image_load_store_lod` for LOD-based image load tests

## Recurring Verification Methods

- Host-side buffer comparison with format-appropriate thresholds
- Per-sample checksum verification for multisample tests
- Byte-by-byte data comparison for transfer tests
- Fuzzy image comparison for rendered output
- Shader compilation verification for format compatibility

## Notes / Uncertainties

- [`host_image_copy`](../../modules/vulkan/image/vktImageTests.cpp#L92) is conditional on `!CTS_USES_VULKANSC`
- Some ASTC formats are commented out in source due to tcu::TextureFormat limitations
- Float formats are excluded from some uncompressed format tests due to NaN/INF/denorm handling
- 3D ASTC tests and multi-layer view tests are only available on non-VulkanSC builds
