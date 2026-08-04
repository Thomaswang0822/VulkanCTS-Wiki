# Understanding Brief: pipeline render to image

## One-sentence test purpose

This test family checks whether graphics rendering writes the expected color pattern to image attachments across view types, attachment sizes, formats, mip levels, and allocation modes.

## Background knowledge

### Image views and attachment slices

A Vulkan image stores texels; an image view selects how commands interpret a range of that image. Array layers, cube faces, and 3D slices need distinct views when a render pass uses them as separate attachments. Render-pass attachment references also carry the layout used while the subpass writes the attachment.

Why it matters here:

- Each view-type branch creates a matching image type and creates one color attachment view per checked slice.
- The core path uses one render-pass subpass for each slice so each draw targets its own layer or slice.

### Layout transitions and host readback

Color attachment writes must become available to the transfer operation that copies the image into a host-visible buffer. The host must then invalidate non-coherent memory before it reads the copied bytes. Image layout and synchronization requirements are defined in [Image Layouts](../../../../vulkan-docs/src/chapters/resources.adoc#L5229-L5518) and [Pipeline Barriers](../../../../vulkan-docs/src/chapters/synchronization.adoc#L6509-L6738).

Why it matters here:

- The test transitions color attachments from `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` before `vkCmdCopyImageToBuffer`.
- A correct draw can still fail the final comparison if the transition, copy, or host-read path is wrong.

## One concrete example

Consider `dEQP-VK.pipeline.fast_linked_library.render_to_image.core.2d.small.r8g8b8a8_unorm`. The CTS creates a 44 by 23 `VK_IMAGE_VIEW_TYPE_2D` color image, clears it, and draws a four-vertex triangle strip. Its vertex shader passes the supplied vertex color through. Its fragment shader writes that color to location 0. After the render pass, the CTS transitions the color image for transfer, copies it to a host-visible buffer, generates the expected four-colored pattern, and compares the pixels with a float threshold of `0.01f`.

## End-to-end test flow

```text
[host] select construction type, allocation kind, image view type, size class, color format, and optional depth/stencil format
[host] require supported image properties, view-type features, and any dedicated-allocation or maintenance extension
[host] create images, image views, buffers, render pass, framebuffer, shaders, and graphics pipelines
[device] clear each attachment, draw a colored triangle strip in each subpass, and store color output
[device] transition color output for transfer, copy the checked image region or all mip levels to a host-visible buffer
[host] wait, invalidate the buffer allocation, generate expected pixels, and compare the copied image data
```

## Generated test artifacts and bound resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| Color image and image views | yes | render target and transfer source | indirectly | Exercises each image-view shape, format, size, and mip range. |
| Optional depth/stencil image and views | yes | attachment during draw | no | Adds supported depth/stencil attachment combinations to the render-pass setup. |
| Per-slice render-pass subpasses and graphics pipelines | yes | one draw per subpass | no | Direct each slice's draw to its matching attachment view. |
| Vertex and fragment programs | yes | draw uses them | no | Produce a known color pattern without sampling the destination image. |
| Host-visible color buffer | yes | transfer destination | yes | Supplies the bytes used by the image comparison. |

## What is checked

- The attachment-size path compares a checked color region against `generateExpectedImage()`. Float formats use `tcu::floatThresholdCompare` with `tcu::Vec4(0.01f)`; integer formats use `tcu::intThresholdCompare` with `tcu::UVec4(2)`.
- Huge-image cases copy only a region no larger than 32 by 32 by 8, so they exercise maximum supported dimensions without reading an entire maximum-size allocation.
- The mipmap path renders and compares every mip level separately. It keeps checking remaining levels after one comparison fails.

## Behavior parameter identification

> **Behavior parameter:** direct intermediate node under `pipeline.<construction_type>.render_to_image`
>
> **Candidate values:** `core` and `dedicated_allocation`.

The `core` intermediate node varies baseline versus huge attachment sizes and mipmap rendering. `dedicated_allocation` repeats the baseline and mipmap shapes after selecting dedicated image allocation; it deliberately omits huge sizes.

## What failure means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Incorrect image/view or framebuffer attachment setup, slice or subpass selection, color attachment write, image layout/synchronization transition, transfer copy/readback, or expected-image comparison. A `huge` failure can also involve maximum-dimension allocation or the bounded verification region. A `mipmap` failure can involve a mip-level-specific view, render, copy offset, or comparison. |
| `dedicated_allocation` | A `core`-path cause, or incorrect use of the dedicated-allocation path for image memory. The final image does not isolate allocation from rendering or readback without source-level investigation. |

## Important variations and special cases

- The implementation registers `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, and `cube_array` below each direct intermediate node.
- Baseline and mipmap cases combine eight color formats with five depth/stencil choices, including `VK_FORMAT_UNDEFINED` for no depth/stencil attachment.
- Only suballocated `core` cases register `huge` sizes, and those cases use `VK_FORMAT_R8G8B8A8_UNORM` to limit permutations.
- The 3D baseline path adds `_2d_compatible` leaves with `VK_KHR_maintenance9`. VulkanSC removes generated sizes whose width and height would both be maximum values.
- The inspected split mustpass files contain 6,625 `render_to_image` leaves: 1,325 each in `fast-linked-library.txt`, `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-unlinked-binary.txt`.

## Source mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Case definition and constants | [`CaseDef` and limits](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L80-L116) | Defines the configuration carried by each generated case and the bounded huge-image check region. |
| Render pass and image creation | [`makeRenderPass()` and `makeImage()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L322-L431) | Creates per-slice attachments, subpasses, and images. |
| Program generation | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L692-L745) | Generates the pass-through vertex and known-color fragment shaders. |
| Attachment runtime and oracle | [`testAttachmentSize()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1125-L1292) | Draws, transitions, copies, invalidates, generates the oracle, and compares the image. |
| Mipmap runtime and oracle | [`testRenderToMipMaps()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1610-L1787) | Transitions, copies, and compares each mip level. |
| Case generation and registration | [`addTestCasesWithFunctions()` and `createRenderToImageTests()`](../../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1842-L2039) | Defines the matrix and registers `core` plus `dedicated_allocation`. |
