# Understanding Brief: mutable image formats

## One-Sentence Test Purpose

This test checks whether Vulkan preserves known color values when an image is accessed through a distinct, equal-size compatible view format across transfer, storage-image, sampled-image, color-attachment, and mutable-format swapchain paths.

## Background Knowledge

### Mutable image and view formats

`VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` allows a `VkImageView` to expose compatible image storage through a format different from the image's creation format. A `VkImageFormatListCreateInfo` can enumerate the formats intended for an image. For swapchains, `VK_SWAPCHAIN_CREATE_MUTABLE_FORMAT_BIT_KHR` applies the same idea to acquired swapchain images and requires a format list.

The implementation's generator first selects distinct pairs with equal mapped pixel size. That is a test-matrix filter, not a complete substitute for the Vulkan format-compatibility rules. The support callback also checks the format features needed by the selected route. With `VK_KHR_maintenance2`, extended usage and `VkImageViewUsageCreateInfo` allow a view usage supported by the view format when the base image format lacks it.

## One Concrete Example

The case `dEQP-VK.image.mutable.2d.b8g8r8a8_snorm_r8g8b8a8_unorm_store_load` creates a 32×32 image in `B8G8R8A8_SNORM`, then uses an `R8G8B8A8_UNORM` storage-image view. The generated compute upload shader stores one four-channel color per invocation. A second compute shader loads through the same view and stores into a separate output image. The host copies the output to a host-visible buffer and compares it with the expected color image.

## End-to-End Test Flow

```text
[host] choose a test family, image type, distinct format pair, upload route, and download route
[host] check format features and create either a mutable image or mutable-format swapchain
[host] create views, descriptors, render-pass resources, samplers, and generated shader programs as required
[host] record barriers and submit the selected upload and download commands
[device] write a layer-dependent reference color through clear, copy, storage-image store, or rendering
[device] read through image-to-buffer copy, storage-image load, or sampled texel fetch
[host] wait for completion, invalidate the mapped buffer, generate the expected image, and compare pixels
```

For swapchain cases, the host acquires an image and passes the acquire semaphore to submission with a top-of-pipe wait. The test reads the image back and does not present it.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` emits a vertex/fragment pair for `draw` and compute programs for `store`, `load`, and `texture`.
- The generated image shader qualifier, image type, sampler type, and scalar/vector color type follow `viewFormat` and the 2D versus 2D-array choice.
- The `store` shader contains the four-entry float or integer color table and indexes it with `gl_GlobalInvocationID.z`. The `load` shader copies `imageLoad` to `imageStore`; the `texture` shader uses `texelFetch` and stores to an output image.
- The image-format-list and resolve variants change generated image creation or attachment resources rather than creating a different correctness contract.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Mutable ordinary image | yes | yes, with device-local allocation | written and read by selected route | indirectly | Its creation format and mutable flag define the storage being reinterpreted. |
| Mutable-format image view | yes | yes, through descriptors or attachments | read/written using `viewFormat` | indirectly | It is the object that exercises alternate-format access. |
| Swapchain image/view | provided by WSI and created by the test | yes | written/read after acquire | indirectly | It tests the same view behavior on acquired WSI storage. |
| Output image for `load`/`texture` | yes | yes | receives shader-read results | yes, through copy | Separates view read behavior from the final transfer to the host buffer. |
| Host-visible color buffer | yes | yes | written by transfer | yes | Carries the observed pixels to host comparison. |
| Storage-image descriptors | yes | yes | shaders use them | no | Bind the mutable view and output image at the generated bindings. |
| Combined image sampler | yes for `texture` | yes | shader samples the mutable view | no | Supplies sampled-image access and nearest `texelFetch`. |
| Render-pass/framebuffer attachments | yes for `draw` and resolve leaves | yes | fragment shader writes them | indirectly | Tests mutable color and resolve attachment combinations. |

The color table in generated GLSL is a constant array, not a host-created or bound GPU buffer. Image barriers and the host-read barrier provide the layout/access transitions that connect these resources.

## What Is Checked

- The host creates an expected image with the format used to interpret the upload result. It cycles four reference colors across array layers and accounts for the source's sRGB conversion rule.
- Integer formats use `tcu::intThresholdCompare` with `tcu::UVec4(1)`. Other formats use `tcu::floatThresholdCompare` with `tcu::Vec4(0.01f)`.
- Every generated case is compared independently. The test returns `Pass` only when the compared image meets the selected threshold; otherwise it returns `Fail`.
- A `NotSupported` result means a feature, format, usage, sample-count, surface, or platform prerequisite prevented legal execution. It is not a pixel mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** test family and path selector
>
> **Candidate values:** `image.mutable`, `image.swapchain_mutable`; upload `clear`, `copy`, `store`, `draw`; download `copy`, `load`, `texture`; format-list, resolve, and load-op-clear variants.

The test family is the primary behavioral axis because it changes the resource origin. Upload and download routes are secondary axes because they change the Vulkan access mechanism applied to the same mutable-view idea.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `image.mutable` | Mutable image/view creation, image-format-list chaining, optimal-tiling feature checks, image barriers, upload/download commands, or host reference generation. |
| `image.swapchain_mutable` | WSI extension and surface setup, surface format/usage selection, mutable swapchain format list, acquire semaphore wait, image access, or host reference generation. |

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `clear` or `copy` upload | Transfer destination setup, creation-format interpretation, upload buffer contents, or the corresponding layout/access transition. |
| `store` upload | Storage-image view usage, typed image declaration, descriptor binding, compute dispatch, or `imageStore` behavior. |
| `draw` upload | Color-attachment view, fragment output type, render pass, vertex data, or attachment transition. |
| `copy` download | Transfer-source layout/access or image-to-buffer region. |
| `load` download | Storage-image input/output views, `imageLoad`, `imageStore`, compute dispatch, or output-image transition. |
| `texture` download | Sampled-image view, sampler, shader-read layout, `texelFetch`, or output-image store. |

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `_format_list` | `VK_KHR_image_format_list` support or `VkImageFormatListCreateInfo` contents and pNext handling. |
| `_resolve`, `_resolve_mutable_resolve_att`, or `_resolve_mutable_color_att` | Multisample support, attachment format/flags, render-pass resolve setup, or resolve operation. |
| `_load_op_clear` | Attachment load operation, clear value, render-pass setup, or the 2D-only case construction. |

## Important Variations and Special Cases

- Ordinary images have both format-list and no-format-list leaves. Swapchain leaves always carry the two-format list.
- The ordinary factory adds resolve leaves only for `draw` plus `copy`, and it adds load-op-clear only for one-layer 2D textures. These are design choices in addition to support-based pruning.
- `store`, `load`, and `texture` require the view format to be image-load/store capable in the registration loops. The support callback separately checks route-specific optimal-tiling feature bits.
- The shared ordinary support callback rejects a family when the maximum available sample count is one, even for leaves that do not request a resolve attachment. Interpret such NotSupported results as a shared gate.
- WSI support can remove leaves because a platform surface, display/window, surface format, usage bit, extension, or array-layer limit is unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Case definitions and format predicate | [`case definitions`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L78-L303) | Defines formats, routes, reference colors, and pair filtering. |
| Generated shader programs | [`initPrograms()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L363-L536) | Shows the exact draw, storage, load, and texture shader branches. |
| Mutable image creation | [`makeImage()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L540-L572) | Shows optional `VkImageFormatListCreateInfo` chaining. |
| Ordinary execution and comparison | [`run()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1081-L1175), [`testMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1724-L1771) | Connects resource setup, barriers, copyback, and thresholds. |
| Support and ordinary registration | [`checkSupport()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1774-L1987) | Shows feature gates and generated ordinary leaves. |
| Mutable swapchain setup | [`makeSwapchain()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2208-L2256), [`testSwapchainMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2258-L2377) | Shows WSI format checks, acquire, submission, and comparison. |
| Swapchain registration | [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2380-L2446) | Shows WSI/image-type loops and route pruning. |
| Vulkan mutable-image rules | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc#L2480-L2790) | Grounds mutable flags, format lists, view formats, and usage semantics. |
| Vulkan mutable-format swapchains | [`wsi.adoc`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6200-L6225) | Grounds swapchain format-list and mutable-format requirements. |

## Questions / Risk Points for User Audit

- Does the distinction between the primary test-family axis and the upload/download route axes make the failure tables easy to use?
- Is it clear that equal pixel size is the source's pair-generation filter, while Vulkan's full compatibility rules still govern legal image views?
- Should the final page keep the single compute walkthrough, or add a separate rendering walkthrough for the `draw` path?
- Are the host-visible readback buffer and the generated shader-local color table clearly distinguished?
- Are the shared sample-count gate and WSI NotSupported paths clear enough to avoid treating skipped cases as pixel failures?

## Conversion Notes for Final Wiki Rewrite

- Distill the mutable-image and mutable-swapchain concepts into three short page-local Background Knowledge bullets; keep the spec caveat about equal pixel size versus complete compatibility.
- Keep the canonical registration tree at one level below each root. Explain the swapchain image-type expansion in prose rather than nesting it in the parseable tree.
- Carry the three `Failure Cause Mapping` tables directly into `## Failure Meaning`. Write the detailed `Cause Analysis` fresh on the final page.
- Use the `store_load` case as the one representative shader walkthrough. Put ordinary render and texture differences in the parameter variation summary and runtime section.
- Keep the resource table's distinction between real GPU resources and the generated shader-local color table.
- Move source navigation to a compact appendix and preserve the relevant Vulkan spec links for audit.
