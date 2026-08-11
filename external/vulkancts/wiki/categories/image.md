## Overview

The `image` test category collects tests that check Vulkan image access, view compatibility, layout, copying, sampling, and depth/stencil behavior across shader, command-buffer, and host-image-copy paths.

[`createChildren()`](../../modules/vulkan/image/vktImageTests.cpp#L61-L100) attaches the direct families. `nontemporal_operand` and `host_image_copy` are not registered in Vulkan SC builds.

## Background Knowledge

- **Images, views, and formats.** An image owns storage and creation parameters; an image view selects an aspect, subresource range, type, and format through which shaders or attachments access that storage. Several families test when a compatible view format is legal, while others check that a declared shader format, view format, and underlying image format interact correctly.
- **Layouts and synchronization.** Vulkan uses image layouts to describe intended access. Commands, shader accesses, and host image-copy calls need the layouts, barriers, and queue or host ordering required by their particular path. `VK_IMAGE_LAYOUT_GENERAL` permits several access forms but does not remove synchronization requirements.
- **Subresources and copies.** Mip levels, array layers, cube faces, aspects, and sample indices identify portions of an image. Copy and readback tests use those selectors to make image contents observable to the host; sampling and storage-image tests use them through views and shader coordinates.

## Category Structure

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
├── nontemporal_operand
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
├── host_image_copy
├── depth_stencil_separate_access
├── non_uniform_offset_sample
├── device_scope_access
├── 2d_array_compatible
└── general_layout
```

One Level-3 page can cover several direct test families when one implementation source owns them. `LoadStore` covers seven storage-image families, `Mutable` covers `mutable` and `swapchain_mutable`, and the remaining pages cover one direct family each. `vktImageTests.cpp` is registration-only dispatcher code and is folded into this page.

## How the Families Fit Together

- **Storage-image behavior** begins with `store`, `load_store`, multisample load/store, format reinterpretation, SPIR-V operand variants, and device-scope access. These families vary declarations, formats, view types, sample indices, and synchronization while comparing results with a host reference.
- **Format and view compatibility** covers mutable images, mismatched declared formats, mismatched write operands, compressed block views, extended usage, ASTC decode mode, and 2D-array-compatible views of 3D images.
- **Sampling and shader-visible properties** covers compressed texture sampling, cubemap sampling, non-uniform offsets, `imageSize`, qualifiers, and atomics.
- **Layout, copying, and host access** covers subresource layout queries, `GENERAL`-layout operations, queue transfer, concurrent copy, and `VK_EXT_host_image_copy`.
- **Depth/stencil behavior** separates descriptor access under legal layouts from rendering paths that read one aspect while writing or resolving the other.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `store`, `load_store`, `format_reinterpret`, `extend_operands_spirv1p4`, `nontemporal_operand`, `device_scope_access`, `load_store_lod` | [LoadStore](../testfiles/image/LoadStore.md) | Storage-image declarations, format reinterpretation, SPIR-V operands, device scope, and explicit LOD |
| `load_store_multisample` | [MultisampleLoadStore](../testfiles/image/MultisampleLoadStore.md) | Per-sample storage-image load/store and checksum checking |
| `mutable`, `swapchain_mutable` | [Mutable](../testfiles/image/Mutable.md) | Mutable view formats, format lists, and mutable swapchains |
| `mismatched_formats` | [MismatchedFormats](../testfiles/image/MismatchedFormats.md) | Different bound-image and shader-declared format handling |
| `mismatched_write_op` | [MismatchedWriteOp](../testfiles/image/MismatchedWriteOp.md) | `OpImageWrite` value-width and signedness/type cases |
| `qualifiers` | [Qualifiers](../testfiles/image/Qualifiers.md) | `coherent`, `volatile`, and `restrict` image and texel-buffer declarations |
| `image_size` | [Size](../testfiles/image/Size.md) | `imageSize()` across image and buffer views |
| `atomic_operations` | [AtomicOperation](../testfiles/image/AtomicOperation.md) | Storage-image and texel-buffer atomic behavior |
| `texel_view_compatible` | [CompressionTranscodingSupport](../testfiles/image/CompressionTranscodingSupport.md) | Compressed blocks exposed through compatible uncompressed views |
| `extended_usage_bit` | [TranscodingSupport](../testfiles/image/TranscodingSupport.md) | Extended usage for compatible view formats in transcoding paths |
| `astc_decode_mode` | [AstcDecodeMode](../testfiles/image/AstcDecodeMode.md) | ASTC decode-mode intermediate formats and sampled results |
| `misaligned_cube` | [MisalignedCube](../testfiles/image/MisalignedCube.md) | Cube-view base-layer alignment behavior |
| `subresource_layout` | [SubresourceLayout](../testfiles/image/SubresourceLayout.md) | Linear-image layout queries and query invariance |
| `sample_cubemap` | [SampleDrawnCubeFace](../testfiles/image/SampleDrawnCubeFace.md) | Rendering and sampling cubemap face 0 |
| `depth_stencil_descriptor` | [DepthStencilDescriptor](../testfiles/image/DepthStencilDescriptor.md) | Descriptor reads of depth/stencil aspects under selected layouts |
| `sample_texture` | [SampleCompressedTexture](../testfiles/image/SampleCompressedTexture.md) | BC compressed texture sampling through compatible views |
| `extended_usage_bit_compatibility` | [ExtendedUsageBit](../testfiles/image/ExtendedUsageBit.md) | Image-format-properties compatibility queries |
| `queue_transfer` | [Transfer](../testfiles/image/Transfer.md) | Buffer-to-image-to-buffer transfers |
| `concurrent_copy` | [ConcurrentCopy](../testfiles/image/ConcurrentCopy.md) | Device and host concurrent-region copy submission |
| `host_image_copy` | [HostImageCopy](../testfiles/image/HostImageCopy.md) | `VK_EXT_host_image_copy` transitions, regions, and readback |
| `depth_stencil_separate_access` | [DepthStencilSeparate](../testfiles/image/DepthStencilSeparate.md) | Reading one depth/stencil aspect while writing the other |
| `non_uniform_offset_sample` | [NonUniformOffsetSample](../testfiles/image/NonUniformOffsetSample.md) | Per-invocation texture offset operations |
| `2d_array_compatible` | [2dArrayCompatible](../testfiles/image/2dArrayCompatible.md) | 2D-array-compatible views of 3D images |
| `general_layout` | [GeneralLayout](../testfiles/image/GeneralLayout.md) | `GENERAL`-layout shader, attachment, and multisample paths |

## Category Notes

- `vktImageTestsUtil.*`, `vktImageLoadStoreUtil.*`, and `vktImageTexture.*` provide shared infrastructure; they do not have standalone Level-3 pages.