## Overview

**Core question:** Do linear-image layout queries provide enough correct information to address every uploaded texel, and do equivalent query APIs return the same base layout?

- This page covers [`vktImageSubresourceLayoutTests.cpp`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp), which implements the `image.subresource_layout` test family.
- The ordinary cases upload data to linear 2D, 2D-array, and 3D images, query each color subresource, and use the reported layout to validate its storage and data.
- The non-VulkanSC `invariance` cases compare `VkSubresourceLayout` results from the image-handle query with `VK_KHR_maintenance5` and optional extended-query forms.
- The page describes the case matrix, host execution, pass conditions, pruning, and failure interpretation.

## Background Knowledge

For the shared concepts image subresources and copies, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Linear image layout.** `VkSubresourceLayout` reports a subresource's byte `offset` and `size`, plus `rowPitch`, `arrayPitch`, and `depthPitch`. For an uncompressed linear image, a texel address is `offset + layer*arrayPitch + z*depthPitch + y*rowPitch + x*elementSize` ([Vulkan layout definition](../../../../vulkan-docs/src/chapters/resources.adoc#L4495-L4552)).
- **Subresource selection.** A query selects an image aspect, mip level, and array layer. A 2D array advances between layers through `arrayPitch`; a 3D image advances between depth slices through `depthPitch`.
- **Layout-query forms.** `vkGetDeviceImageSubresourceLayoutKHR` takes `VkImageCreateInfo` instead of an image handle, and `vkGetImageSubresourceLayout2EXT` returns the base layout inside `VkSubresourceLayout2EXT` ([extended queries](../../../../vulkan-docs/src/chapters/resources.adoc#L4618-L4728), [device query](../../../../vulkan-docs/src/chapters/resources.adoc#L4759-L4784)).

## Registration Hierarchy

```text
image.subresource_layout
├── 2d
├── 2d_array
├── 3d
└── invariance (non-VulkanSC only)
```

The ordinary paths contain the `1_level`, `2_levels`, `4_levels`, and `all_levels` intermediate nodes. Each contains one leaf per basic color format and a matching `_offset` leaf. `invariance` contains one leaf per basic color format and image class.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image-layout path | `2d`, `2d_array`, `3d`; `invariance` outside VulkanSC | Selects the layout relationship or API-agreement property under test. | [Image-class and invariance registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L824-L921) |
| Mip-level configuration | `1_level`, `2_levels`, `4_levels`, `all_levels` | Requests one, two, four, or all realizable mip levels for each ordinary path. The helper stops at the terminal extent. | [Level construction](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L113-L135), [registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L838-L851) |
| Image format | Each value in `formats::basicColorFormats` | Varies texel representation while retaining a known byte size for address-based comparison. | [Format loop](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L864-L889) |
| Memory-binding variant | `<format>`, `<format>_offset` | Binds the image at allocation offset zero or at `req.alignment`, checking that layout offsets remain usable with a nonzero binding offset. | [Binding and leaf creation](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L492-L501), [registration](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L877-L889) |
| Default dimensions | `2d`: `240 x 320 x 1`; `2d_array`: `32 x 48 x 56`; `3d`: `32 x 48 x 56` | For 2D images, the source interprets the third dimension as the layer count before creating the image. | [Default dimensions](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L160-L175), [image creation](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L467-L490) |
| Invariance width | Default width plus format index | Gives each invariance image a format-dependent width while keeping one mip level and binding offset zero. | [Invariance parameters](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L901-L918) |

## Behavior Parameters

The registered image-layout path is the primary behavioral axis. The first three paths test whether returned fields address real copied data. `invariance` instead tests agreement between APIs that describe the same base layout.

### 2d: row-addressed 2D subresources

The test uploads tightly packed data for each realizable mip level of a linear 2D image. For each level, it checks that `size` covers the subresource and that `rowPitch` can span its width when it has more than one row. It then uses `offset + y*rowPitch + x*pixelSize` to compare every image texel with the source buffer.

### 2d_array: layer offsets and array pitch

This path uses a linear 2D image with multiple array layers. It performs the same row-addressed validation as `2d`, then checks that each queried layer reports the same `arrayPitch` as layer zero and that its `offset` differs from the base offset by `layer * arrayPitch`. The byte comparison validates each layer independently.

### 3d: slice addressing through depth pitch

This path creates a linear 3D image. In addition to the size and row-pitch checks, it requires a sufficient `depthPitch` when the mip extent has more than one depth slice. The comparison uses `offset + z*depthPitch + y*rowPitch + x*pixelSize` to validate the copied volume.

### invariance: equivalent base layouts

Outside VulkanSC, this path creates one linear image and visits every aspect supported by its selected color format. It compares the complete `VkSubresourceLayout` for mip level zero and layer zero from `vkGetImageSubresourceLayout` with the layout embedded in `vkGetDeviceImageSubresourceLayoutKHR`. When `VK_EXT_image_compression_control` is present, it also compares the layout embedded in `vkGetImageSubresourceLayout2EXT` ([comparison sequence](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L759-L784)).

## Shader Analysis

This test has no shaders. It exercises image creation, transfer commands, host-visible memory, and layout-query APIs directly from the host.

## Runtime Execution and Result Checking

The ordinary paths run the following host-side sequence for each supported aspect. The registered matrix uses color formats, so registered leaves normally execute the color-aspect path.

1. [`BufferLevels`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L84-L157) calculates tightly packed source-buffer regions for each realizable mip level. The source fills the host-visible buffer with deterministic pseudorandom bytes; float formats avoid denormals, and the 24-bit depth special case masks unused high bits ([data initialization](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L443-L465)).
2. The test creates a `VK_IMAGE_TILING_LINEAR` image with transfer-source and transfer-destination usage. For 2D cases, it converts the supplied third dimension into `arrayLayers` and restores image extent depth to one. The `_offset` variant allocates one alignment unit of extra memory and binds the image at that alignment offset ([image setup](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L467-L501)).
3. One `VkBufferImageCopy` region transfers each mip level. The command buffer transitions the image from undefined to transfer-destination layout, copies the source buffer, then transitions it to general layout with host-read access and waits for completion ([copy and barriers](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L503-L560)).
4. After invalidating the image allocation, the test queries the base layer and every array layer of every mip level. It checks array-pitch consistency, layer-offset progression, minimum `size`, and the applicable minimum row, array, and depth pitches ([layout checks](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L562-L647)).
5. The test calculates each source and image byte address. It adds the allocation binding offset to the image pointer for `_offset` cases, applies the returned `rowPitch` and `depthPitch`, and compares each pixel with the original buffer bytes. A mismatch reports its mip level, layer, and coordinates ([comparison loop](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L649-L687)).
6. `invariance` does not upload or read back image data. It creates the image and performs the direct layout-structure comparisons for each supported aspect ([invariance execution](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L714-L786)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | The reported offset, size, or row pitch does not support correct host addressing of a 2D linear-image subresource, or copied data is not visible at that address. |
| `2d_array` | The reported array pitch or per-layer offset is inconsistent, too small, or does not locate the copied layer data. |
| `3d` | The reported depth pitch, row pitch, offset, or size does not locate the copied 3D slice data. |
| `invariance` | The image-handle and image-create-info layout queries, or the optional extended query, return different base layouts for the same image configuration. |

### Cause Analysis

#### 2D row layout or host visibility

**Possible failure symptoms:** The case reports an undersized `size` or `rowPitch`, or reports the first pixel whose bytes differ from the uploaded source at a particular mip level and coordinate.

**Possible implementation causes:** The driver may report an incorrect linear subresource offset, size, or row stride, or its transfer-to-host visibility path may leave the copied bytes unavailable through the bound host-visible allocation. The source waits for the transfer and invalidates that allocation before calculating addresses from the queried fields.

#### Array-layer layout

**Possible failure symptoms:** A `2d_array` case reports inconsistent `arrayPitch`, an offset that does not follow `layer * arrayPitch`, an undersized array pitch, or a mismatching pixel in one layer.

**Possible implementation causes:** The implementation may calculate array-layer spacing or per-layer offsets incorrectly for a linear image. A layer-specific data mismatch can also result if the reported layout addresses the wrong portion of the image allocation.

#### 3D slice layout

**Possible failure symptoms:** A `3d` case reports an undersized `depthPitch` or identifies a differing pixel at a particular z coordinate, often while shallower slices remain readable.

**Possible implementation causes:** The implementation may report an invalid spacing between depth slices, or may combine slice and row strides incorrectly when laying out or exposing a linear 3D image.

#### Layout-query invariance

**Possible failure symptoms:** An `invariance` case fails with the name of `vkGetDeviceImageSubresourceLayoutKHR` or `vkGetImageSubresourceLayout2KHR`, indicating that the raw base-layout structures differ.

**Possible implementation causes:** The image-handle query, the `VkImageCreateInfo`-based maintenance5 query, or the optional extended query may derive different `VkSubresourceLayout` fields for equivalent configuration. The test compares only the embedded base layout, so it does not diagnose extension-chain output differences.

## Case Pruning

### Requirement-based pruning

- [`ImageSubresourceLayoutCase::checkSupport()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L237-L267) requires `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` and `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` for linear tiling, then checks the selected image configuration, realizable mip-level count, and 2D array-layer count. Unsupported cases report `NotSupportedError`.
- In non-VulkanSC builds, `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` ([named format gate](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L242-L245)).
- `invariance` requires `VK_KHR_maintenance5`; its optional third comparison runs only if `VK_EXT_image_compression_control` is supported ([invariance support and condition](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L811-L815), [conditional query](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L777-L784)).

### Design-based pruning

- The test registers only `formats::basicColorFormats`. It excludes depth/stencil formats because their representation can prevent the source from deriving the texel size needed for bytewise data validation ([registration rationale](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L864-L872)).
- The ordinary matrix fixes the three default image dimensions and limits image classes to 2D, layered 2D, and 3D. It uses linear tiling and transfer usage because those choices expose layout-addressable storage after upload.
- `invariance` fixes one mip level, binding offset zero, and the base layer. It isolates equivalence among query forms rather than repeating the full data-addressability matrix.
- VulkanSC builds do not register `invariance` because its maintenance5 query path is guarded out of that build ([registration guard](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L897-L921)).

## Key Takeaways

- The ordinary cases validate returned layout fields by using them to locate and compare every uploaded texel in host-visible linear-image memory.
- `2d_array` adds inter-layer offset and `arrayPitch` checks, while `3d` adds inter-slice `depthPitch` checks.
- `_offset` leaves ensure the calculation remains correct when image memory begins at a nonzero allocation offset.
- The non-VulkanSC invariance path checks base-layout equality across the original, maintenance5, and optionally extended layout-query APIs.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Mip model and default dimensions | [`BufferLevels` and `getDefaultDimensions()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L61-L175) | Defines packed data regions, terminal mip behavior, and default extents. |
| Support gate | [`ImageSubresourceLayoutCase::checkSupport()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L237-L267) | Checks linear-tiling features, format support, mip limits, array limits, and named format requirements. |
| Ordinary runtime and checks | [`ImageSubresourceLayoutInstance::iterateAspect()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L412-L692) | Uploads data, queries layouts, checks field relationships, and compares bytes. |
| Invariance runtime | [`ImageSubresourceLayoutInvarianceInstance::iterate()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L714-L786) | Compares the embedded base layout from the available query forms. |
| Registration | [`createImageSubresourceLayoutTests()`](../../../modules/vulkan/image/vktImageSubresourceLayoutTests.cpp#L820-L924) | Defines paths, mip nodes, format leaves, `_offset` leaves, and the VulkanSC guard. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) | Adds `subresource_layout` to the `image` test category. |
| Mustpass evidence | [`subresource-layout.txt`](../../../mustpass/main/vksc-default/image/subresource-layout.txt) | Contains VulkanSC ordinary-path leaves such as `dEQP-VKSC.image.subresource_layout.2d.1_level.a1r5g5b5_unorm_pack16`. |
| Vulkan layout semantics | [`vkGetImageSubresourceLayout` and `VkSubresourceLayout`](../../../../vulkan-docs/src/chapters/resources.adoc#L4389-L4614) | Defines linear-image query use, returned fields, and the addressing rule. |
| Vulkan extended-query semantics | [`vkGetImageSubresourceLayout2` and `vkGetDeviceImageSubresourceLayout`](../../../../vulkan-docs/src/chapters/resources.adoc#L4618-L4784) | Defines the extended and device-create-info query forms used by `invariance`. |
