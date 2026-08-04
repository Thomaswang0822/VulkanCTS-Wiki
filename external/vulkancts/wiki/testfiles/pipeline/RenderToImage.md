## Overview

**Core question:** Can a graphics pipeline render the expected color pattern into supported image attachments and make that result available for host comparison?

- This page covers the `render_to_image` test family implemented by [`vktPipelineRenderToImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1).
- The family tests color attachment rendering through 1D, array, 2D, 3D, cube, and cube-array image views; it varies image size, mip levels, color formats, optional depth/stencil attachments, and image-memory allocation mode.
- Its direct intermediate nodes are `core` and `dedicated_allocation`. They share the rendering and comparison design, while the latter selects dedicated image allocation and excludes huge-image leaves.
- [RenderToImage_brief.md](RenderToImage_brief.md) supplies a worked 2D case and the same failure-cause mapping used below.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- An image view describes the image subresources and view type used by an attachment. A render pass associates each subpass attachment with an image layout; see [Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#L5692-L6048) and [Render Pass](../../../../vulkan-docs/src/chapters/renderpass.adoc#L2194-L2415).
- To read rendered pixels on the host, the test makes color-attachment writes available to a transfer read, changes the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, copies it to a buffer, and makes transfer writes available to host reads. The relevant contracts are [Image Layouts](../../../../vulkan-docs/src/chapters/resources.adoc#L5229-L5518) and [Pipeline Barriers](../../../../vulkan-docs/src/chapters/synchronization.adoc#L6509-L6738).

## Registration Hierarchy

```text
pipeline.fast_linked_library.render_to_image
├── core
└── dedicated_allocation
```

The source registers the same two direct intermediate nodes for each supported pipeline construction path. The fenced tree uses `pipeline.fast_linked_library.render_to_image` as one concrete mustpass root. The five split construction files named below contain 1,325 leaves each, or 6,625 leaves: `fast-linked-library.txt`, `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-unlinked-binary.txt`. `monolithic/monolithic.txt` and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt` contribute another 1,325 leaves each, for 9,275 `vk-default` leaves across all seven construction roots.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct intermediate node | `core`, `dedicated_allocation` | Selects suballocated or dedicated allocation for the test's images and buffers. | [`createRenderToImageTests()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L2012-L2039), [resource allocation](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1022-L1079) |
| Image view type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array` | Changes image type, layers or slices, view construction, and the number of subpass attachments. | [case matrix](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1863-L1879) |
| Size class | `small`, `huge`, `mipmap` | Selects a baseline image, generated maximum-dimension variants, or drawing and checking all mip levels. | [case generation](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1902-L2005) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R16G16_SINT`, `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_A1R5G5B5_UNORM_PACK16`, `VK_FORMAT_R5G6B5_UNORM_PACK16`, `VK_FORMAT_A2B10G10R10_UINT_PACK32`, `VK_FORMAT_A2B10G10R10_UNORM_PACK32` | Selects the fragment output type and comparison mode. Huge leaves use only `VK_FORMAT_R8G8B8A8_UNORM`. | [format arrays](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1881-L1895), [huge cases](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1953-L1978) |
| Depth/stencil format | `VK_FORMAT_UNDEFINED`, `VK_FORMAT_D16_UNORM`, `VK_FORMAT_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` | Adds no depth/stencil attachment or one supported depth, stencil, or combined attachment per slice. | [format arrays](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1890-L1895) |
| 3D compatibility variant | ordinary 3D leaf, `_2d_compatible` | The extra 3D leaves set the `maintenance9` case flag. | [3D generation](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1941-L1950) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node under the test family. It changes the allocation path for the test's images and buffers; `core` also owns the huge-size coverage.

### core: Suballocated rendering matrix

`core` renders a known color pattern through every registered view type. Its `small` leaves use baseline dimensions and all color/depth-stencil combinations. Its `huge` leaves replace selected dimensions with runtime maximum values, use only `VK_FORMAT_R8G8B8A8_UNORM`, and compare a bounded region. Its `mipmap` leaves render and validate every mip level.

### dedicated_allocation: Dedicated image-memory matrix

`dedicated_allocation` calls the same case generator with `ALLOCATION_KIND_DEDICATED`. The allocator receives that mode for the color and depth/stencil images, vertex buffer, and host-visible readback buffer. Support checks require `VK_KHR_dedicated_allocation`; baseline and mipmap cases remain, while the generator suppresses huge cases for this allocation kind.

## Shader Analysis

The shaders provide a known attachment value rather than the behavior under test. `initPrograms()` emits a vertex shader that passes position and color through and a fragment shader that writes the selected color-format type to location 0. Image-view construction, render-pass attachment selection, transitions, copyback, and comparison determine the tested behavior, so this page does not include a representative shader walkthrough or embedded SPIR-V assembly.

## Runtime Execution and Result Checking

- The support path checks image-view requirements. For non-VulkanSC builds, a 3D view requires `VK_KHR_maintenance1` and passes the portability-subset check for 2D views of 3D images; VulkanSC omits that `VK_KHR_maintenance1` gate. Cube arrays require `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY`; dedicated leaves require `VK_KHR_dedicated_allocation`; `_2d_compatible` leaves require `VK_KHR_maintenance9`. It also verifies image-format properties and depth/stencil attachment support for attachment-size cases ([support checks](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1295-L1368)).
- The attachment-size path creates a color image, optional depth/stencil image, views, a framebuffer, and one render-pass subpass per image slice. It clears the attachments, binds the matching graphics pipeline in each subpass, and draws a four-vertex triangle strip ([draw setup](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1122-L1203)). The later copy selects only the checked region.
- It transitions color output from `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, copies the checked region to a host-visible buffer, then makes transfer writes visible to host reads ([copy barriers and copy](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1205-L1266)).
- After waiting, the host invalidates the allocation, generates the expected image, and compares it with `tcu::floatThresholdCompare` at `0.01f` for floating-point formats or `tcu::intThresholdCompare` at `UVec4(2)` for the other formats ([oracle](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1269-L1292)).
- Mipmap cases first transition the full mip range for attachment writes, draw each level, then copy all mip levels to one buffer. The host compares each level and retains a failure if any comparison fails ([mipmap path](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1610-L1787)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Incorrect image/view or framebuffer attachment setup, slice or subpass selection, color attachment write, image layout/synchronization transition, transfer copy/readback, or expected-image comparison. A `huge` failure can also involve maximum-dimension allocation or the bounded verification region. A `mipmap` failure can involve a mip-level-specific view, render, copy offset, or comparison. |
| `dedicated_allocation` | A `core`-path cause, or incorrect use of the dedicated-allocation path for image or buffer memory. The final image does not isolate allocation from rendering or readback without source-level investigation. |

### Cause Analysis

#### Attachment, view, or rendering errors

**Possible failure symptoms:** A `core` leaf produces an image mismatch for one view type, slice, format, or depth/stencil combination. Mismatches may be restricted to array layers, cube faces, or 3D slices.

**Possible implementation causes:** The implementation may select the wrong image subresource for an attachment view, associate a framebuffer attachment with the wrong subpass, mishandle the view type, or fail to store fragment output to the color attachment. The final comparison covers the complete rendering path, so source-level investigation is needed to separate those mechanisms.

#### Size or mip-level handling errors

**Possible failure symptoms:** `huge` cases fail while baseline cases pass, or a `mipmap` leaf reports a mismatch for one named mip level. A failure can be limited to the checked 32 by 32 by 8 huge-image region.

**Possible implementation causes:** A maximum-dimension image may fail creation or allocation, a view or framebuffer may use the wrong extent, or a mip-specific render/copy region or buffer offset may be wrong. The source deliberately bounds huge-image readback and records each mip level separately, which helps identify the affected shape but does not assign a unique fault location.

#### Layout, synchronization, transfer, or host-readback errors

**Possible failure symptoms:** Rendering may appear correct in a device capture, yet host comparison fails across several view types or formats. A mismatch can affect every pixel after the copy.

**Possible implementation causes:** The implementation may not make color-attachment writes available to the transfer read, may mishandle the transition to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, may copy the wrong subresource, or may expose stale bytes to the host. The test records image and buffer barriers before copying and invalidates the host-visible allocation, so this class includes the required visibility path as well as the copy itself.

#### Dedicated-allocation errors

**Possible failure symptoms:** `dedicated_allocation` leaves fail while matching `core` baseline or mipmap leaves pass.

**Possible implementation causes:** The implementation may mishandle dedicated allocation or binding for an image or buffer, or its interaction with the resource requirements. The same final image also depends on rendering and readback, so the source provides an operation-shape classification rather than proof that allocation alone caused the failure.

## Case Pruning

### Requirement-based pruning

- The source rejects unsupported image formats through image-format property checks and requires depth/stencil attachment support for selected depth/stencil formats.
- In non-VulkanSC builds, 3D views require `VK_KHR_maintenance1` and are subject to the portability-subset check for 2D views of 3D images. That block is compiled out for VulkanSC. Cube-array views require `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY` in both builds.
- Dedicated leaves require `VK_KHR_dedicated_allocation`, and `_2d_compatible` leaves require `VK_KHR_maintenance9`.
- Image creation can be treated as unsupported when memory requirements exceed the implementation's maximum resource size.

### Design-based pruning

- Huge cases use only `VK_FORMAT_R8G8B8A8_UNORM` to limit format permutations, and dedicated allocation suppresses them altogether.
- Huge-image comparison copies a restricted region rather than the complete maximum-size image.
- Cube images force width and height to change together because cube faces are square.
- VulkanSC removes generated cases where both width and height would be maximum values.

## Key Takeaways

- `render_to_image` combines attachment rendering, image-view interpretation, layout transitions, transfer copyback, and host comparison in one image-result test.
- The `core` intermediate node tests baseline, huge-size, and mipmap shapes. `dedicated_allocation` preserves baseline and mipmap behavior while changing resource-memory allocation for the images and buffers.
- The source makes each slice a distinct subpass attachment and checks a known color pattern after readback.
- A final mismatch locates a failure in the tested rendering-to-host-observation path, but the image result alone cannot uniquely distinguish attachment setup, rendering, synchronization, transfer, or allocation defects.

## Source Reference Appendix

| Entry point or contract | Link | Why it matters |
|-------------------------|------|----------------|
| Case configuration | [`CaseDef` and shared constants](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L80-L116) | Defines view type, size hint, formats, allocation mode, maintenance flag, and huge-image check limits. |
| Render-pass and image construction | [`makeRenderPass()` and `makeImage()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L322-L431) | Builds per-slice attachments/subpasses and Vulkan images. |
| Program generation | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L692-L745) | Emits the pass-through vertex and known-color fragment programs. |
| Attachment-size execution and oracle | [`testAttachmentSize()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1125-L1292) | Records draws, barriers, copyback, and pixel comparison. |
| Support gates | [`checkImageViewTypeRequirements()` and `checkSupportAttachmentSize()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1295-L1368) | Enforces feature, extension, image, and format requirements. |
| Mipmap execution and oracle | [`testRenderToMipMaps()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1610-L1787) | Renders, copies, and compares all mip levels. |
| Matrix and registration | [`addTestCasesWithFunctions()` and `createRenderToImageTests()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1842-L2039) | Generates leaves and registers `core` plus `dedicated_allocation`. |
| Vulkan image layout contract | [Image Layouts](../../../../vulkan-docs/src/chapters/resources.adoc#L5229-L5518) | Defines image layouts and their use by commands. |
| Vulkan synchronization contract | [Pipeline Barriers](../../../../vulkan-docs/src/chapters/synchronization.adoc#L6509-L6738) | Defines execution and memory dependencies used before transfer and host access. |
