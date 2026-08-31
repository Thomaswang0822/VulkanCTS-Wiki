## Overview

The `protected_memory` test category collects tests that check protected-memory access through attachments, image and buffer transfers, shader resources, and protected WSI interaction.

## Background Knowledge

- **Protected memory and protected queues.** Vulkan separates protected and unprotected device memory. A protected resource must be accessed by protected queue operations, while protected command buffers come from protected command pools. These rules are shared by the rendering, transfer, shader, and interaction families.
- **Protected submission.** A submission identifies protected execution through `VkProtectedSubmitInfo`. The tests use this boundary to exercise device work that reads or writes protected resources, then use an appropriate validation path for the result.
- **Resource validation boundaries.** Some tests validate a protected image through a compute shader, while others copy data into a buffer or validate presentation. The validator is part of the observation path and does not necessarily implement the operation being tested.

## Category Structure

```text
protected_memory
├── attachment
├── image
├── buffer
├── ssbo
├── interaction
├── workgroupstorage
└── stack
```

The registration-only dispatcher `vktProtectedMemTests.cpp` routes these direct children to the implementation-bearing families. `interaction.wsi` is registered only outside Vulkan SC; `interaction.ycbcr` remains available through its separate conversion implementation.

## How the Families Fit Together

The families exercise the same protected-execution boundary through different resource operations.

- **Attachments** test render-pass load and clear behavior, with separate cases for primary and secondary command-buffer recording.
- **Images and buffers** test fixed-function clears, copies, fills, updates, and copyback paths. The transfer direction determines whether the final observation is an image comparison or a buffer comparison.
- **Shader resources** test protected image access, storage-buffer reads/writes/atomics, workgroup storage, and shader stack storage. These pages vary shader stage, access mode, data type, or storage size.
- **Interaction** covers protected swapchain creation/render/presentation and protected YCbCr sampling and conversion. WSI coverage is platform-specific and unavailable on Vulkan SC.

The category therefore compares both protected resource handling and the command or shader path that observes the resource.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `attachment.clear_op` | [AttachmentClear](../testfiles/protected_memory/AttachmentClear.md) | Primary versus secondary `vkCmdClearAttachments` recording, protected render-pass setup, and four-sample image validation. |
| `attachment.load_op` | [AttachmentLoad](../testfiles/protected_memory/AttachmentLoad.md) | Static and seeded-random render-pass load values, protected attachment initialization, and copyback checking. |
| `image.blit` | [BlitImage](../testfiles/protected_memory/BlitImage.md) | Protected `vkCmdBlitImage` source/destination images, layout transitions, filtering, and image validation. |
| `image.copy` | [CopyImage](../testfiles/protected_memory/CopyImage.md) | Protected `vkCmdCopyImage` transfer direction, primary/secondary recording, and destination checks. |
| `image.clear_color` | [ClearColorImage](../testfiles/protected_memory/ClearColorImage.md) | Protected `vkCmdClearColorImage` cases and the image-validation path. |
| `image.copy_buffer_to_image` | [CopyBufferToImage](../testfiles/protected_memory/CopyBufferToImage.md) | Protected buffer initialization, `vkCmdCopyBufferToImage`, layout synchronization, and image validation. |
| `image.access` | [ShaderImageAccess](../testfiles/protected_memory/ShaderImageAccess.md) | Shader sampling, fetch, image load/store, atomic access, protection modes, and generated shader walkthroughs. |
| `buffer.fill`, `buffer.update`, `buffer.copy` | [FillUpdateCopyBuffer](../testfiles/protected_memory/FillUpdateCopyBuffer.md) | Buffer fill, update, and copy operations across numeric types, command-buffer modes, and device-address variants. |
| `buffer.copy_image_to_float_buffer` | [CopyImageToBuffer](../testfiles/protected_memory/CopyImageToBuffer.md) | Protected image-to-buffer transfer, pipeline-protected-access variants, and buffer validation. |
| `ssbo.ssbo_read`, `ssbo.ssbo_write`, `ssbo.ssbo_atomic` | [StorageBuffer](../testfiles/protected_memory/StorageBuffer.md) | Shader-stage storage-buffer reads, writes, atomics, pipeline protection modes, and generated shader behavior. |
| `interaction.wsi` | [WsiSwapchain](../testfiles/protected_memory/WsiSwapchain.md) | Platform-specific protected swapchain creation, acquire/render/present flow, and non-VulkanSC scope. |
| `interaction.ycbcr` | [YCbCrConversion](../testfiles/protected_memory/YCbCrConversion.md) | Format and conversion matrices, protected multi-plane images, sampler conversion, and shader validation. |
| `workgroupstorage` | [WorkgroupStorage](../testfiles/protected_memory/WorkgroupStorage.md) | Generated compute shaders that vary workgroup storage size and report results through an image. |
| `stack` | [Stack](../testfiles/protected_memory/Stack.md) | Generated compute shaders that vary stack-array size and validate protected output through an image. |

## Category Notes

The visible Level-3 page count is fourteen because the dispatcher itself is registration-only and the direct `buffer` and `interaction` children each route to multiple implementation pages. The legacy `vkt*.md` pages remain source-navigation records; the links above point to the rewritten pages.
