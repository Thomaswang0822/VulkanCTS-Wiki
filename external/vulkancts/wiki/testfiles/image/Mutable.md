## Overview

**Core question:** Can an image created in one color format be accessed through a distinct mutable-format view and still produce the expected pixels after transfer, storage-image, sampled-image, or color-attachment operations?

[`vktImageMutableTests.cpp`](../../../modules/vulkan/image/vktImageMutableTests.cpp) implements two sibling `image` families:

- `image.mutable` allocates an ordinary optimal-tiled image with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`.
- `image.swapchain_mutable` acquires an image from a mutable-format swapchain and exercises the same upload/download routes.

Each leaf selects an image/view format pair, an upload route, and a download route. Ordinary-image leaves additionally cover an optional image-format list, three resolve-attachment arrangements, and a one-layer load-op-clear case. The test writes a layer-dependent reference color, reads it through the selected route, copies the observation to host-visible memory, and compares every pixel with a generated reference.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` permits an image view whose format differs from the image format, but the view format must satisfy Vulkan's format-compatibility rules. `VkImageFormatListCreateInfo`, when chained to image creation, restricts the allowed view formats to its list. The CTS generator uses **distinct pairs having equal mapped pixel size** as its pair-selection predicate; that source-level predicate is not a replacement for the Vulkan compatibility rules. See [mutable image creation and image views](../../../../vulkan-docs/src/chapters/resources.adoc#L4148-L4154) and [format-list validity](../../../../vulkan-docs/src/chapters/resources.adoc#L2752-L2762).
- `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` (from Vulkan 1.1 / `VK_KHR_maintenance2`) permits an image usage supported by a view format even when the creation format does not support it. The test uses it when maintenance2 is available, and chains `VkImageViewUsageCreateInfo` to storage, sampled, or color-attachment views as appropriate. See [extended usage](../../../../vulkan-docs/src/chapters/resources.adoc#L1822-L1832).
- `VK_SWAPCHAIN_CREATE_MUTABLE_FORMAT_BIT_KHR` makes swapchain images mutable-format images and requires a nonempty `VkImageFormatListCreateInfo` that includes the swapchain image format; every listed view format must be compatible. The swapchain test always supplies its two-format list. See [swapchain requirements](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6203-L6224).

## Registration Hierarchy

```text
image.mutable
├── 2d
└── 2d_array

image.swapchain_mutable
├── xlib
├── xcb
├── wayland
├── android
├── win32
├── metal
├── headless
├── direct_drm
└── direct
```

Both roots are added under `image` by [`createImageTests()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100). The ordinary factory creates generated leaves directly below `2d` and `2d_array`. The swapchain factory iterates every `vk::wsi::Type` before `TYPE_LAST`, then adds the same two image-type groups and generated leaves below each WSI group ([`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2380-L2446)).

The checked-in default mustpass inventory is split by family: [`image/mutable.txt`](../../../mustpass/main/vk-default/image/mutable.txt) contains **10,118 `image.mutable` leaves**, while [`image/swapchain-mutable.txt`](../../../mustpass/main/vk-default/image/swapchain-mutable.txt) contains **3,240 `image.swapchain_mutable` leaves**. The latter includes the nine WSI paths shown above; platform availability can still prune individual executions.

## Parameter Dimensions and Observed Values

| Dimension | Values observed in source | Effect |
|---|---|---|
| Family | `image.mutable`; `image.swapchain_mutable` | Selects an allocated image or an acquired swapchain image. |
| Image type | `2d`, `2d_array` | Both use a 32×32 extent; `2d` has one layer and `2d_array` has four. |
| Ordinary format set | 23 formats: 32/16-bit float; 32/16/8-bit uint and sint; 8-bit RGBA/BGRA UNORM, SNORM, and sRGB | Supplies both ordered members of the ordinary format pair. |
| Swapchain format set | Six 8-bit RGBA/BGRA UNORM, SNORM, and sRGB formats | Supplies both members of the swapchain pair. |
| Pair filter | Ordered, distinct pairs with equal mapped pixel size | Selects candidate reinterpretation pairs; it does not itself prove spec compatibility. |
| Upload | `clear`, `copy`, `store`, `draw` | Writes through transfer clear, buffer-to-image copy, compute `imageStore`, or color attachment rendering. |
| Download | `copy`, `load`, `texture` | Reads through image-to-buffer copy, compute `imageLoad`, or sampled `texelFetch`. |
| Ordinary format-list variant | no suffix; `_format_list` | Omits or chains `VkImageFormatListCreateInfo` with the image and view formats. |
| Resolve variant | `_resolve`, `_resolve_mutable_resolve_att`, `_resolve_mutable_color_att` | Uses draw/copy only; chooses whether both attachments, only the resolve attachment, or only the multisampled color attachment is mutable. |
| Load-op-clear variant | `_load_op_clear` | A 2D draw/copy case only; draws a smaller quad so the render pass's `VK_ATTACHMENT_LOAD_OP_CLEAR` result remains observable outside it. |

The normal route matrix is generated for every permitted pair. `store` is skipped when the view format is not image-load/store capable; `load` and `texture` are likewise skipped for such a view format. The support callback then checks route-specific optimal-tiling feature bits ([`checkSupport()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1774-L1856)).

## Behavior Parameters

### `image.mutable`: allocated mutable image

The executor creates an optimal-tiled image in `imageFormat`, sets `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, and, when maintenance2 is supported, also sets `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. It creates the access view in `viewFormat`. In the resolve variants it creates a multisampled color image and a single-sample resolve image; the variant determines which one has mutable-format creation flags. The normal routes add both no-list and `_format_list` leaves.

### `image.swapchain_mutable`: acquired swapchain image

The test creates a surface, finds both selected formats in that surface's format list, checks the requested usage and array-layer limit, then creates a swapchain with `VK_SWAPCHAIN_CREATE_MUTABLE_FORMAT_BIT_KHR` and a two-entry format list. It acquires one image, runs the selected route, reads it back, and does **not** present it. Swapchain leaves always use `_format_list`; they have no resolve or `_load_op_clear` variants.

## Shader Analysis

Example leaf:

```text
dEQP-VK.image.mutable.2d.b8g8r8a8_snorm_r8g8b8a8_unorm_store_load
```

This case creates the image in `B8G8R8A8_SNORM`, makes an `R8G8B8A8_UNORM` storage-image view, writes through a generated compute shader, then reads that view through a second generated compute shader.

The source generator emits the following shape for the upload program (the qualifier, image type, scalar/vector type, and constants vary with `viewFormat` and image type):

```glsl
#version 450
layout(local_size_x = 1) in;
layout(binding = 0, rgba8) writeonly uniform image2D u_image;

const vec4 colorTable[] = vec4[](
    vec4(0.0, 0.4, 0.8, 0.1),
    vec4(0.5, 0.1, 0.9, 0.2),
    vec4(0.2, 0.6, 1.0, 0.3),
    vec4(0.3, 0.7, 0.0, 0.4));

void main()
{
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    imageStore(u_image, pos, colorTable[gl_GlobalInvocationID.z]);
}
```

For this 2D leaf the dispatch is 32×32×1, so every texel receives `colorTable[0]`. For `2d_array`, the generator uses `image2DArray` and an `ivec3` coordinate; the z invocation selects the layer's reference color. Integer view formats generate `ivec4` or `uvec4` tables. The `load` reader emits `imageStore(out_image, pos, imageLoad(in_image, pos))`; the `texture` reader instead binds a sampler and uses `texelFetch` ([`initPrograms()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L363-L536)).

## Runtime Execution and Result Checking

```text
select pair + route
        │
        ├─ ordinary: create/bind mutable image
        └─ swapchain: create mutable-format swapchain, acquire image
        │
write one reference color per layer
  clear | buffer copy | compute imageStore | draw
        │
read selected view
  image→buffer copy | compute imageLoad→output image | texelFetch→output image
        │
copy result to host-visible buffer → invalidate mapping → compare every pixel
```

- The reference tables contain four float colors and four integer colors. Layer `z` uses entry `z % 4`; the 2D case uses entry zero. Integer values are masked to the channel width used by the writer to avoid problematic reinterpretations ([`getClearValueInt()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L170-L217)).
- `clear` and `copy` write in the image's creation-format interpretation. `store` and `draw` access the alternate view format. The comparison similarly interprets readback in `imageFormat` for `clear`/`copy` and `viewFormat` for `store`/`draw` ([`testMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1724-L1771)).
- `load` and `texture` first write a separate, non-mutable output image in `viewFormat`, then copy that image to the host buffer. The executor records layout/access barriers between the upload, shader access, transfer copy, and host read.
- If the selected writing interpretation is sRGB, `generateExpectedImage()` applies the source's linear-to-sRGB conversion rule. Integer comparison permits one unit per component; other formats use a `0.01` float threshold ([`generateExpectedImage()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L819-L846)).

## Failure Meaning

| Failing dimension | Investigate first |
|---|---|
| One ordered format pair across routes | Mutable image/view legality, format-list contents, view-format interpretation, or format-specific feature support. Verify the pair against the Vulkan compatibility table; equal pixel size is only this generator's filter. |
| `clear` or `copy` upload | Creation-format transfer write, buffer contents/region, layout transition, or expected-image interpretation. |
| `store` upload | Storage-image view usage, generated image qualifier/type, descriptor binding, compute dispatch, or shader-write synchronization. |
| `draw` upload | Color-attachment view, fragment output type, render pass/framebuffer, vertex data, resolve setup, or attachment transition. |
| `copy` download | Transfer-source layout/access, copy region, or host-read synchronization. |
| `load` / `texture` download | Input view usage/layout, image load or sampled fetch, output storage image, compute dispatch, or output copyback. |
| `_format_list` only | `VK_KHR_image_format_list` enablement or `VkImageFormatListCreateInfo` chain/list handling. |
| Resolve suffix only | Multisample support, which attachment is mutable, render-pass resolve descriptions, framebuffer attachment ordering, or resolve execution. |
| `_load_op_clear` only | Render pass clear/load behavior or the intentionally smaller draw quad that exposes the clear outside the quad. |
| Swapchain family only | WSI extension/device setup, surface format or usage selection, mutable swapchain list, acquire synchronization, or platform surface setup. |

A pixel mismatch is reported as `Fail`; a missing format feature, extension, sample count, surface capability, or platform facility is normally reported as `NotSupported`. These have different diagnostic meanings.

## Case Pruning

| Condition | Outcome in this test |
|---|---|
| `_format_list` ordinary leaf | Requires `VK_KHR_image_format_list`. |
| Selected route | The view format must support the route's optimal-tiling feature bits; `texture` also needs storage support because its output image is written by a shader. |
| Base-format feature mismatch | Without maintenance2, the base image format must support the view-required features. With maintenance2, extended usage plus per-view usage can permit the view's supported usage. |
| Ordinary sample count | The shared ordinary support check rejects a case if the maximum available sample count is only `VK_SAMPLE_COUNT_1_BIT`, even when that leaf is not a resolve leaf. |
| Swapchain | Requires `VK_KHR_surface`, the selected WSI surface extension, `VK_KHR_swapchain`, `VK_KHR_swapchain_mutable_format`, both formats supported by the surface, requested surface usage, and sufficient image array layers. |
| WSI environment | Unsupported extensions, native display/window facilities, or surface properties produce `NotSupported`/environment-dependent outcomes rather than a pixel-comparison failure. |

Identical formats are deliberately excluded. Resolve and load-op-clear leaves are ordinary-image-only design variants; the resolve matrix is fixed to `draw_copy`, and `_load_op_clear` is fixed to the one-layer texture. The Vulkan test-plan's broader image-view objective is to create valid views from compatible images and verify differing formats ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L483-L504)).

## Key Takeaways

- The family is a mutable-view data-path test, not a same-format-view test: all generated pairs are distinct.
- It exercises transfer, storage-image, sampled-image, color-attachment, resolve, and mutable swapchain paths against one layer-dependent color contract.
- The source's equal-pixel-size predicate generates candidate pairs; Vulkan's compatibility and format-list requirements remain authoritative.
- The default mustpass inventory is split into ordinary `image.mutable` and WSI `image.swapchain_mutable` files; the source registers the latter for all WSI types.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Case definitions, colors, formats, pair filter | [`vktImageMutableTests.cpp#L78-L303`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L78-L303) |
| Generated draw/store/load/texture shaders | [`initPrograms()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L363-L536) |
| Image creation and optional format list | [`makeImage()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L540-L572) |
| Expected-image generation and route usage | [`generateExpectedImage()` / `getImageUsageForTestCase()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L819-L895) |
| Ordinary executor and comparison | [`run()` / `testMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1081-L1175) and [`testMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1724-L1771) |
| Support and ordinary registration | [`checkSupport()` / `createImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1774-L1987) |
| Mutable swapchain setup, execution, registration | [`makeSwapchain()` / `testSwapchainMutable()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2208-L2377) and [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2380-L2446) |
| Parent registration | [`vktImageTests.cpp#L61-L100`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) |
| Default mustpass inventory | [`image/mutable.txt`](../../../mustpass/main/vk-default/image/mutable.txt) |
