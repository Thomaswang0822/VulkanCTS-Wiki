# Understanding Brief: `image.subresource_layout`

## One-Sentence Test Purpose

This test checks whether a driver reports usable linear-image subresource layouts and whether the layout-query entry points that describe the same subresource agree.

## Background Knowledge

### Linear-image subresource layout

`vkGetImageSubresourceLayout` returns a `VkSubresourceLayout` for a selected image aspect, mip level, and array layer. For a linear image, `offset` identifies the subresource's start, `size` covers its required storage, `rowPitch` advances between rows, `arrayPitch` advances between array layers, and `depthPitch` advances between 3D slices. Vulkan gives the uncompressed addressing rule as `offset + layer*arrayPitch + z*depthPitch + y*rowPitch + x*elementSize` ([layout definition](../../../../vulkan-docs/src/chapters/resources.adoc#L4495-L4552)).

Why it matters here:

- The test uses the returned pitches to find each uploaded texel in host-visible image memory.
- The checks allow zero row or depth pitch where Vulkan permits it for a one-row or one-slice subresource.

### Image aspect, mip level, layer, and 3D slice

A `VkImageSubresource` identifies an aspect, mip level, and array layer. A 2D array uses array layers, whereas a 3D image uses depth slices inside one subresource. The implementation preserves the 2D array layer count across mip levels and halves the 3D depth extent with the other dimensions ([`BufferLevels`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L84-L135)).

Why it matters here:

- `2d_array` checks the offset progression between independently queried layers.
- `3d` checks addressing through `depthPitch`, not through array layers.

### Equivalent layout-query forms

`VK_KHR_maintenance5` provides `vkGetDeviceImageSubresourceLayoutKHR`, which takes image-creation information instead of an image handle and otherwise behaves like the extended layout query. `vkGetImageSubresourceLayout2EXT` returns the same base layout through `VkSubresourceLayout2EXT` ([extended queries](../../../../vulkan-docs/src/chapters/resources.adoc#L4618-L4728), [device query](../../../../vulkan-docs/src/chapters/resources.adoc#L4759-L4784)).

Why it matters here:

- The non-VulkanSC `invariance` cases compare the complete base `VkSubresourceLayout` returned by these forms for the same first mip level and first layer.

## One Concrete Example

`dEQP-VKSC.image.subresource_layout.2d_array.2_levels.r8g8b8a8_unorm_offset` creates a linear 2D array image with a `32 x 48` extent, 56 layers, and up to two mip levels. It allocates extra image memory and binds the image at `alignment` bytes from the allocation base. The test uploads distinct pseudorandom bytes for each mip level and layer, queries the color layout for each layer, checks that the layer's offset is `baseOffset + layer * arrayPitch`, and uses `offset`, `rowPitch`, and the binding offset to compare the image-memory bytes with the upload buffer.

## End-to-End Test Flow

```text
[host] choose image class, mip-level configuration, basic color format, and optional binding-offset variant
[host] verify linear-tiling transfer features, image-format support, mip-level support, and array-layer support
[host] build tightly packed source-buffer regions for each realizable mip level and fill them with deterministic data
[host] create and bind a host-visible linear image, optionally at one alignment-sized offset into its allocation
[host] copy every mip level from the source buffer, then transition the image for host reads and wait for completion
[host] query each color subresource layout and check pitch, size, and offset relationships
[host] compute byte addresses from the returned pitches and compare each image texel with its source-buffer texel
[host] in non-VulkanSC invariance cases, compare the base layout from image-handle, device-create-info, and optional extended queries
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

This source generates no shader program. It builds Vulkan image, buffer, copy-region, and barrier objects directly in C++.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|---------------|----------------|
| Host-visible source buffer | Yes | Yes | Read by `vkCmdCopyBufferToImage` | Yes, as expected data | Holds tightly packed per-mip upload data. |
| Linear image allocation | Yes | Yes | Written by the buffer-to-image copy | Yes | Contains the layout-addressed bytes under test. |
| Linear image | Yes | Yes | Transfer destination | Yes, through its bound allocation | Supplies the subresources queried by the APIs. |
| Command buffer and barriers | Yes | Yes | Executes copy and synchronization | No | Makes transfer writes visible to host reads. |
| `VkImageCreateInfo` for invariance | Yes | No image handle needed by one query | Read by the driver | No | Lets `vkGetDeviceImageSubresourceLayoutKHR` describe the same configuration. |

## What Is Checked

- For each registered color-format case, the basic path checks that a multi-layer image reports the same `arrayPitch` for each layer and that each layer offset advances by `layer * arrayPitch` from the base layer ([layout checks](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L562-L647)).
- It checks that `size`, `rowPitch`, `arrayPitch`, and, for 3D images, `depthPitch` are large enough for the queried extent when the corresponding dimension has more than one element.
- It calculates each image byte address from `offset`, `rowPitch`, and `depthPitch`, compensates for the optional image-memory binding offset, and compares the stored bytes with the original buffer data ([byte comparison](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L649-L687)).
- The invariance path compares the raw `VkSubresourceLayout` bytes returned by `vkGetImageSubresourceLayout`, `vkGetDeviceImageSubresourceLayoutKHR`, and, when available, `vkGetImageSubresourceLayout2EXT` ([invariance loop](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L714-L786)).

## Behavior Parameter Identification

> **Behavior parameter:** registered image-layout path
>
> **Candidate values:** `2d`, `2d_array`, `3d`, `invariance` (non-VulkanSC only)

The image-layout path is the primary behavioral axis. `2d`, `2d_array`, and `3d` change the layout relationship being observed: ordinary rows, inter-layer spacing, or inter-slice spacing. `invariance` changes the property from addressability of stored data to agreement among layout-query APIs. Mip-level count, format, and `_offset` configure coverage within those behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | The reported offset, size, or row pitch does not support correct host addressing of a 2D linear-image subresource, or copied data is not visible at that address. |
| `2d_array` | The reported array pitch or per-layer offset is inconsistent, too small, or does not locate the copied layer data. |
| `3d` | The reported depth pitch, row pitch, offset, or size does not locate the copied 3D slice data. |
| `invariance` | The image-handle and image-create-info layout queries, or the optional extended query, return different base layouts for the same image configuration. |

## Important Variations and Special Cases

- **Mip configuration.** The registered `1_level`, `2_levels`, `4_levels`, and `all_levels` intermediate nodes request one, two, four, or as many realizable mip levels as the dimensions permit. The helper stops when it reaches the terminal extent, so `all_levels` is not an unbounded count ([level construction](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L113-L135), [registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L838-L851)).
- **Binding-offset variant.** Every ordinary-format leaf has a companion `_offset` leaf that binds the image at `req.alignment` rather than allocation offset zero ([registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L877-L889)).
- **Format scope.** Registration iterates `formats::basicColorFormats`; depth/stencil formats are excluded because the source cannot derive a known texel size for bytewise validation ([source rationale](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L864-L872)).
- **Maintenance5 formats and invariance.** `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` in non-VulkanSC builds. `invariance` also requires that extension and is not registered in VulkanSC ([support checks](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L237-L267), [guarded registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L897-L921)).
- **Optional extended comparison.** Invariance cases call `vkGetImageSubresourceLayout2EXT` only when `VK_EXT_image_compression_control` is supported; lack of that extension does not skip the baseline comparison ([conditional query](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L777-L784)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Mip data model and default dimensions | [`BufferLevels` and `getDefaultDimensions()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L61-L175) | Defines packed upload sizes, realizable levels, and the 2D, array, and 3D dimensions. |
| Baseline support gate | [`ImageSubresourceLayoutCase::checkSupport()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L237-L267) | Checks features, linear-image support, mip limits, layer limits, and named format requirements. |
| Basic execution and verification | [`iterateAspect()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L412-L692) | Uploads data, queries layouts, validates relations, and compares bytes. |
| Invariance execution | [`ImageSubresourceLayoutInvarianceInstance::iterate()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L714-L786) | Compares the base layout across query forms. |
| Case registration | [`createImageSubresourceLayoutTests()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L820-L924) | Creates the hierarchy, matrix, offset variants, and non-VulkanSC invariance group. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) | Adds `subresource_layout` to the `image` test category. |
| Vulkan layout semantics | [`vkGetImageSubresourceLayout` and `VkSubresourceLayout`](../../../../vulkan-docs/src/chapters/resources.adoc#L4389-L4614) | Defines legal linear-image query use and the returned address fields. |

## Questions / Risk Points for User Audit

- The source's generic aspect loop supports color, depth, and stencil aspects, but the registered matrix contains only `formats::basicColorFormats`. The final page must not claim that registered leaves test depth or stencil layouts.
- The source returns pass early for a VulkanSC parent-process run after the copy, so the final page should state the regular validation path without implying that every process mode performs the host-memory checks.
- The source compares raw `VkSubresourceLayout` bytes for invariance. The final page should describe that as base-structure equality, not as a comparison of extension-chain outputs.

## Conversion Notes for Final Wiki Rewrite

- Keep the image-layout path as the primary behavior parameter and copy the failure-cause table unchanged.
- Distill layout fields, addressing, and query equivalence into short background bullets.
- Use the 2D-array `_offset` case as the representative runtime walkthrough because it exposes array pitch, per-layer offsets, and the allocation-binding offset in one case.
- State that no shaders participate. Keep the detailed byte-address formula and resource roles in runtime execution, then move line-level evidence to the source appendix.
