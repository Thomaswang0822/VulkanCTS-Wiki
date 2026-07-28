# Understanding Brief: `api.image_clearing` (and the `core` / `dedicated_allocation` variants)

## One-Sentence Test Purpose

This test checks whether `vkCmdClearColorImage`, `vkCmdClearDepthStencilImage`, and `vkCmdClearAttachments` write the requested clear value into the requested subresource range of the destination image across format, tiling, layer-configuration, dimension, separate depth/stencil layout, partial-clear, and multisample variations.

## Background Knowledge

### Three Vulkan clear commands with distinct scope

`vkCmdClearColorImage` operates on color images via a `VkImageSubresourceRange` and a `VkClearColorValue`. `vkCmdClearDepthStencilImage` operates on depth/stencil images via a `VkImageSubresourceRange` and a `VkClearDepthStencilValue`. Both require the destination image to be in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL` and require the `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` feature for the format. `vkCmdClearAttachments` operates inside a render pass via `VkClearAttachment` and `VkClearRect`, does not take a subresource range (the render pass already binds the attachment), and can clear a sub-rectangular region of the bound layers.

Why it matters here:

- The test organizes its six top-level subgroups by command, not by format family, so a failure localizes to the command being exercised.
- `vkCmdClearAttachments` shares the same expected-value logic as the image clears, but the layout, subresource, and partial-clear parameters come from the active render pass and `VkClearRect` rather than from a `VkImageSubresourceRange`.

### `VkImageSubresourceRange` and `VK_REMAINING_ARRAY_LAYERS`

`VkImageSubresourceRange` describes the mip levels and array layers affected by a clear-image command. `baseArrayLayer` and `layerCount` select the layer range; `levelCount` selects the mip range. `VK_REMAINING_ARRAY_LAYERS` and `VK_REMAINING_MIP_LEVELS` direct the implementation to resolve the count from the image's total layers or levels minus the base. The test's `remaining_array_layers` and `remaining_array_layers_twostep` layer configurations exercise the `VK_REMAINING_ARRAY_LAYERS` resolution path.

Why it matters here:

- A driver that resolves `VK_REMAINING_ARRAY_LAYERS` to the full image layer count rather than `arrayLayers - baseArrayLayer` will leave uncleared layers in the `remaining_array_layers` configuration.
- The `_twostep` variant splits the clear across two `vkCmdClearColorImage` calls with a pipeline barrier between them, exercising the interaction between `VK_REMAINING_ARRAY_LAYERS` and a partial first step.

### Separate depth/stencil layouts

For combined depth/stencil formats (`VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT`), `VK_EXT_separate_depth_stencil_layouts` allows the depth and stencil aspects to be in different layouts. The test's `separateDepthStencilLayoutMode` parameter selects `SEPARATE_DEPTH_STENCIL_LAYOUT_MODE_NONE`, `_DEPTH`, or `_STENCIL`. The `_DEPTH` mode clears only the depth aspect using `VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL`; the `_STENCIL` mode clears only the stencil aspect using `VK_IMAGE_LAYOUT_STENCIL_ATTACHMENT_OPTIMAL`.

Why it matters here:

- A driver that does not implement `VK_EXT_separate_depth_stencil_layouts` for clear commands will produce a layout-transition failure on the `_separate_layouts_depth` or `_separate_layouts_stencil` cases.
- The aspect mask passed to `vkCmdClearDepthStencilImage` or `vkCmdClearAttachments` is derived from the mode, so a driver that ignores the aspect mask and clears both aspects would be detected by the per-aspect verification.

### Clear-value clamping for unsigned fixed-point formats

The Vulkan spec requires implementations to clamp out-of-range clear values for unsigned fixed-point formats to `[0, 1]` before writing. The test's `_clamp_input` clear-color parameter set uses negative inputs (`-0.1f`, `-1e6f`, `-0.3f`, `-1.5f`) and expects the implementation to write zeros. The same clamping does not apply to signed fixed-point, integer, or floating-point formats.

Why it matters here:

- A driver that writes negative values directly to an unsigned fixed-point format, or that clamps signed formats when it should not, will fail the `_clamp_input` cases.
- The `ClearTestColorParams` struct carries `useSeparateExpectedColors` so the host reference can use the post-clamp expected values rather than the raw clear inputs.

## One Concrete Example

A representative case is `dEQP-VK.api.image_clearing.core.clear_color_image.2d.optimal.single_layer.256x256x1.r8g8b8a8_unorm`:

```text
Image:              VK_IMAGE_TYPE_2D, VK_FORMAT_R8G8B8A8_UNORM, 256x256x1, OPTIMAL tiling, arrayLayers=1
Allocation kind:    ALLOCATION_KIND_SUBALLOCATED (core)
Clear color:        {0.1f, 0.5f, 0.3f, 0.9f}
Subresource range:  mipLevels=0..1, baseArrayLayer=0, layerCount=1
```

The host creates the image with `VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, transitions it into `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, records `vkCmdClearColorImage` with the single subresource range, transitions the image into `VK_IMAGE_LAYOUT_GENERAL`, reads the image back, and compares every texel against the expected `VkClearColorValue`. The threshold for `R8G8B8A8_UNORM` is `1.0f / (2^8 - 1)` per channel, derived from the format's bit depth.

## End-to-End Test Flow

```text
[host] choose test parameters from the subgroup (clear_color_image, clear_depth_stencil_image, clear_color_attachment, clear_depth_stencil_attachment, partial_clear_color_attachment, partial_clear_depth_stencil_attachment)
[host] choose image type, tiling, layer configuration, dimensions, format, clear-color parameter set, separate-layout mode, multisample count, and 2D-array-compatible flag from the registered matrix
[host] create the destination VkImage with TRANSFER_DST|TRANSFER_SRC usage (or color/depth-stencil attachment usage for attachment clears); allocate and bind memory (suballocated or dedicated)
[host] pre-clear the image to a known initValue so uncleared texels are distinguishable
[host] record pipeline barrier: UNDEFINED -> TRANSFER_DST_OPTIMAL (or GENERAL when generalLayout is set)
[host] clear-color-image path: vkCmdClearColorImage with one or more VkImageSubresourceRanges
[host] clear-depth-stencil-image path: vkCmdClearDepthStencilImage with the aspect-masked subresource range
[host] attachment path: begin render pass, vkCmdClearAttachments with one or more VkClearRects, end render pass
[host] _twostep variants: insert a pipeline barrier between the first and second clear, with the second clear using VK_REMAINING_ARRAY_LAYERS
[host] _multiple_subresourcerange variants: clear one subresource range, then clear a second range that overlaps in mip but not in layers
[host] record pipeline barrier: TRANSFER_DST_OPTIMAL -> GENERAL (or current layout -> GENERAL for attachment clears)
[device] execute the clear command, writing the clear value into the requested subresource range
[host] readImage destination back into a TextureLevelPyramid per aspect
[host] verifyResultImage: compare each texel against the expected clear value or the initValue, with format-specific thresholds
[host] pass if every checked texel matches the expected value within threshold
```

For the multisample color-attachment path, the host also creates a multisample image, clears it, and resolves to a single-sample image via `vkCmdResolveImage` before readback.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- No GLSL, SPIR-V, HLSL, or Amber artifacts. All work is recorded through `vkCmdClearColorImage`, `vkCmdClearDepthStencilImage`, `vkCmdClearAttachments`, `vkCmdResolveImage`, or the pipeline barriers around them.
- The CPU reference is generated on the fly by `verifyResultImage`, which uses the same `clearValue` and `initValue` parameters that produced the device-side clear, with format-specific thresholds derived from `getTextureFormatBitDepth` or `getTextureFormatMantissaBitDepth`.
- The `_clamp_input` parameter set carries `useSeparateExpectedColors = true` and pre-clamped `expectedColors` so the host reference uses zeros rather than the negative clear inputs.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|---------------|-------------------------|--------------------|----------------|
| Destination `VkImage` | Yes | Yes (transfer destination or attachment) | Written by the clear command | Yes, via `readImage` | Receives the cleared texels; for multisample variants it owns multiple samples that are resolved before readback. |
| Multisample `VkImage` (color-attachment path only) | Yes, when `imageSampleCount != VK_SAMPLE_COUNT_1_BIT` | Yes (color attachment) | Written by `vkCmdClearAttachments`, then read by `vkCmdResolveImage` | No, the resolved single-sample image is read back | Holds the per-sample clear result; the resolve step produces a single-sample image for host verification. |
| Init-value pre-clear | Yes, recorded by `preClearImage` or `preClearMultisampleImage` | Yes | Written by `vkCmdClearColorImage` to `initValue` | No | Establishes a known baseline so uncleared texels are distinguishable from cleared texels. |
| Render pass and framebuffer (attachment paths only) | Yes | Yes | Drives the attachment layout and clears | No | Provides the attachment context required by `vkCmdClearAttachments`; for depth/stencil, the render pass also selects the aspect layout. |
| Expected `TextureLevelPyramid` | Yes, on the host | No | No | Yes, as the comparison reference | Host-computed oracle produced by `verifyResultImage` from the clear and init values. |

## What Is Checked

- The destination image is read back per aspect via `readImage`. The host iterates every `(x, y, z, arrayLayer)` texel and compares it against the expected value:
  - for color formats, the expected value is `clearValue[0].color` for texels inside the clear range and `initValue.color` for texels outside it (when the init pre-clear covered them);
  - for depth formats, the expected value is `clearValue[0].depthStencil.depth`;
  - for stencil formats, the expected value is `clearValue[0].depthStencil.stencil`;
  - for `_clamp_input` cases, the expected color is the pre-clamped `expectedColors[0]` (zeros for unsigned fixed-point formats).
- The threshold is derived from the format's bit depth:
  - unsigned fixed-point: `1.0f / (2^N - 1)` per channel;
  - signed fixed-point: `1.0f / (2^(N-1) - 1)` per channel;
  - unsigned integer: `1U` per channel;
  - signed integer: `1` per channel;
  - floating-point: `10 * (1 << (23 - mantissaBits))` per channel, matching the implicit ULP tolerance used by `tcu::floatThresholdCompare` for 32-bit float and 16-bit float formats.
- For partial-clear attachment cases, the host also passes `clearCoords` to `verifyResultImage` so only the texels inside the `VkClearRect` are compared against the clear value; texels outside the rect are compared against the init value.
- For `_multiple_subresourcerange` cases, the host checks that the second clear overwrote the first clear in the overlapping range, and that the non-overlapping range retains the first clear value.
- For `_twostep` cases, the host checks that the second clear (with `VK_REMAINING_ARRAY_LAYERS`) overwrote the layers not covered by the first clear.
- The pass condition is `tcu::TestStatus::pass(...)` only if every checked texel matches the expected value within threshold. A single failing texel produces `tcu::TestStatus::fail(...)` with a per-aspect message (`"Depth value mismatch!"`, `"Stencil value mismatch!"`, or a color mismatch message).

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node (the subgroup directly under `image_clearing.core` or `image_clearing.dedicated_allocation`)
>
> **Candidate values:** `clear_color_image`, `clear_depth_stencil_image`, `clear_color_attachment`, `clear_depth_stencil_attachment`, `partial_clear_color_attachment`, `partial_clear_depth_stencil_attachment`

A secondary behavioral axis is the parent context, which selects allocation strategy:

> **Secondary axis:** parent context
>
> **Candidate values:** `core` (`ALLOCATION_KIND_SUBALLOCATED`), `dedicated_allocation` (`ALLOCATION_KIND_DEDICATED`)

The primary axis is the subgroup because each subgroup exercises a distinct Vulkan clear command and a distinct aspect-layout interaction. The parent context only changes allocation strategy and produces the same deeper subgroup structure through the shared `createImageClearingTestsCommon()` generator.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_color_image.*` | `vkCmdClearColorImage` dispatch, `VkImageSubresourceRange` resolution (including `VK_REMAINING_ARRAY_LAYERS`), clear-value clamping for unsigned fixed-point formats, or transfer-layout transition for the destination image. |
| `clear_depth_stencil_image.*` | `vkCmdClearDepthStencilImage` dispatch, aspect-mask derivation for combined depth/stencil formats, separate depth/stencil layout handling (`_separate_layouts_depth` / `_separate_layouts_stencil`), or `VK_REMAINING_ARRAY_LAYERS` resolution for the depth/stencil aspect. |
| `clear_color_attachment.*` | `vkCmdClearAttachments` dispatch inside a render pass, `VkClearRect` layer-range handling, color-attachment layout transition, or render-pass clear-load-store action interaction. |
| `clear_depth_stencil_attachment.*` | `vkCmdClearAttachments` with `VK_IMAGE_ASPECT_DEPTH_BIT` / `VK_IMAGE_ASPECT_STENCIL_BIT`, depth/stencil attachment layout transition, or separate depth/stencil layout handling inside a render pass. |
| `partial_clear_color_attachment.*` | `VkClearRect` sub-rectangular region handling, partial-clear scissor interaction, or layer-range mismatch between the clear rect and the attachment. |
| `partial_clear_depth_stencil_attachment.*` | `VkClearRect` sub-rectangular region handling for depth/stencil aspects, partial-clear scissor interaction, or aspect-specific partial clear inside a render pass. |
| All leaves under `dedicated_allocation.*` | Dedicated-allocation memory binding for the destination image, or different format-property reporting under dedicated allocation. |
| All leaves with `_clamp_input` suffix | Clear-value clamping for unsigned fixed-point formats; negative inputs must be clamped to zero before writing. |
| All leaves with `_separate_layouts_depth` / `_separate_layouts_stencil` suffix | `VK_EXT_separate_depth_stencil_layouts` extension support for clear commands, or aspect-specific layout transition. |
| All leaves with `_multiple_subresourcerange` suffix | Multi-range clear dispatch, or overlapping-range overwrite semantics. |
| All leaves with `remaining_array_layers` or `remaining_array_layers_twostep` | `VK_REMAINING_ARRAY_LAYERS` resolution from a non-zero `baseArrayLayer`, or two-step clear interaction with `VK_REMAINING_ARRAY_LAYERS`. |
| All leaves with `_4_samples` / `_8_samples` / `_16_samples` / `_32_samples` / `_64_samples` suffix (color-attachment only) | Multisample color-attachment clear, multisample resolve, or per-sample clear-value write. |
| All leaves with `2d_array_compatible_3d` (3D color-image only) | `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` handling for 3D images used as 2D-array clear targets. |
| All leaves with `general_layout` (color-image and color-attachment only) | `VK_IMAGE_LAYOUT_GENERAL` as the clear layout instead of `TRANSFER_DST_OPTIMAL` or `COLOR_ATTACHMENT_OPTIMAL`. |

### Cause Analysis

Detailed `### Cause Analysis` is written fresh during the final Level-3 rewrite. The brief only names the causes above so the mapping can be carried directly into the final page.

## Important Variations and Special Cases

- **Cube-image attachment clears.** The `cube_layers` layer configuration is registered for attachment clears (`clear_color_attachment`, `partial_clear_color_attachment`) but not for image clears. The image is created with `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` and the attachment view uses `VK_IMAGE_VIEW_TYPE_CUBE`. Image clears do not exercise cube images because `vkCmdClearColorImage` operates on the whole subresource range, not on cube faces.
- **3D image array compatibility.** A subset of 3D `clear_color_image` cases set `create2DArrayCompatible = true`, which adds `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`. This requires `VK_KHR_maintenance1` semantics so the 3D image can be viewed and cleared as a 2D-array image. The case name suffix is `2d_array_compatible_3d`.
- **`generalLayout` mode.** A subset of 2D `clear_color_image` and `clear_color_attachment` cases set `generalLayout = true`, which substitutes `VK_IMAGE_LAYOUT_GENERAL` for `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (image clears) or `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` (attachment clears). This exercises the general-layout clear path, which is a separate driver path.
- **Multisample color-attachment clears.** The `clear_color_attachment` subgroup iterates `VK_SAMPLE_COUNT_2_BIT` through `VK_SAMPLE_COUNT_64_BIT` for selected 2D color formats. The case name suffix is `_N_samples` from `getSampleCountName()`. The multisample image is cleared via `vkCmdClearAttachments`, then resolved to a single-sample image via `vkCmdResolveImage` before readback. A failure on a specific sample count points to per-sample clear-value write or to the resolve step.
- **`_multiple_subresourcerange` cases.** The `ClearColorImageMultipleSubresourceRangeTestInstance` and `ClearDepthStencilImageMultipleSubresourceRangeTestInstance` subclasses clear two overlapping subresource ranges in one command buffer. The first range covers a subset of mip levels and layers; the second range covers a different subset that overlaps with the first. The host checks that the second clear overwrote the first in the overlapping range, and that the non-overlapping range retains the first clear value.
- **`_twostep` cases.** The `TwoStepClearColorImageTestInstance` and `TwoStepClearDepthStencilImageTestInstance` subclasses split the clear across two `vkCmdClearColorImage` / `vkCmdClearDepthStencilImage` calls. The first call clears a single layer; the second call clears `VK_REMAINING_ARRAY_LAYERS` from the same base. A pipeline barrier separates the two calls. A failure on `_twostep` while the single-step `remaining_array_layers` passes points to the inter-clear barrier or to the second call's range resolution.
- **Attachment-layer pruning.** `vkCmdClearAttachments` does not accept `VK_REMAINING_ARRAY_LAYERS`, so the `remaining_array_layers` and `remaining_array_layers_twostep` layer configurations are excluded from the attachment subgroups (`numOfAttachmentLayerParamsToTest = numOfImageLayerParamsToTest - 2`).
- **Compressed and large 64-bit formats.** Several compressed formats (BC, ETC, ASTC) and larger 64-bit float formats (`VK_FORMAT_R64_SFLOAT`, `VK_FORMAT_R64G64B64_*`, `VK_FORMAT_R64G64B64A64_*`) are commented out in the `colorImageFormatsToTest` array because `tcu::TextureFormat` does not support them. The test therefore does not exercise clear commands on those formats.
- **`VK_EXT_4444_formats`.** `VK_FORMAT_A4R4G4B4_UNORM_PACK16_EXT` and `VK_FORMAT_A4B4G4R4_UNORM_PACK16_EXT` are extension-only formats that require `VK_EXT_4444_formats` (promoted to Vulkan 1.3 core). The test registers them in the format list but does not explicitly gate the extension in `checkSupport`; the format-property check in `checkSupport` returns `NotSupportedError` if the format has no transfer feature.
- **Vulkan SC exclusions.** `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` are guarded by `#ifndef CTS_USES_VULKANSC` because they require `VK_KHR_maintenance5`, which is not in Vulkan SC.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `ImageClearingTestCase::checkSupport()` | [`vktApiImageClearingTests.cpp#L517-L543`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L517-L543) | Gates `VK_KHR_maintenance5`, `VK_KHR_dedicated_allocation`, `VK_KHR_separate_depth_stencil_layouts`, and `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT | VK_FORMAT_FEATURE_TRANSFER_DST_BIT` for the requested tiling. |
| `ImageClearingTestInstance::verifyResultImage()` | [`vktApiImageClearingTests.cpp#L1317-L1592`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1317-L1592) | Per-aspect per-texel comparison against `clearValue` or `initValue` with format-specific thresholds; entry point for color, depth, and stencil verification. |
| `ImageClearingTestInstance::readImage()` | (base class helper) | Reads the destination image back into a `TextureLevelPyramid` per aspect and array layer. |
| `ClearColorImageTestInstance::iterate()` | [`vktApiImageClearingTests.cpp#L1693-L1825`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1693-L1825) | Records the layout transition, the pre-clear, the `vkCmdClearColorImage` call(s), the optional multisample resolve, and the final transition into `VK_IMAGE_LAYOUT_GENERAL` for readback. |
| `ClearColorImageMultipleSubresourceRangeTestInstance::iterate()` | [`vktApiImageClearingTests.cpp#L1628-L1676`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1628-L1676) | Two-range clear variant: clears two overlapping subresource ranges in one command buffer. |
| `ClearDepthStencilImageTestInstance::iterate()` | [`vktApiImageClearingTests.cpp#L1912-L1976`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1912-L1976) | Records the layout transition, the pre-clear, the `vkCmdClearDepthStencilImage` call with the aspect-masked range, and the final transition into `VK_IMAGE_LAYOUT_GENERAL` for readback. |
| `ClearDepthStencilImageMultipleSubresourceRangeTestInstance::iterate()` | [`vktApiImageClearingTests.cpp#L1860-L1910`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1860-L1910) | Two-range depth/stencil clear variant. |
| `ClearAttachmentTestInstance::iterate()` | [`vktApiImageClearingTests.cpp#L1995-L2104`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1995-L2104) | Begins a render pass, records `vkCmdClearAttachments` with `VkClearRect`(s), ends the render pass, and reads back the attachment. |
| `PartialClearAttachmentTestInstance` | [`vktApiImageClearingTests.cpp#L2111`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2111) | Subclass that builds a sub-rectangular `VkClearRect` from `imageExtent / 8` to `imageExtent * 7 / 8` and passes `clearCoords` to `verifyResultImage`. |
| `createImageClearingTestsCommon()` | [`vktApiImageClearingTests.cpp#L2224-L3190`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L3190) | Shared generator that creates the six subgroups and expands the format, tiling, layer, dimension, clear-color, separate-layout, and multisample matrices. |
| Color format table | [`vktApiImageClearingTests.cpp#L2237-L2425`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2237-L2425) | Explicit list of color formats exercised by `clear_color_image` and the color-attachment subgroups; compressed and larger 64-bit float formats are commented out. |
| Depth/stencil format table | [`vktApiImageClearingTests.cpp#L2428-L2431`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2428-L2431) | Standard seven depth/stencil formats exercised by the depth/stencil subgroups. |
| `_clamp_input` clear-color table | [`vktApiImageClearingTests.cpp#L2433-L2465`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2433-L2465) | Two clear-color parameter sets: default values and negative-input clamp values with `useSeparateExpectedColors = true`. |
| Layer configuration table | [`vktApiImageClearingTests.cpp#L2471-L2519`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2471-L2519) | Five layer configurations: `single_layer`, `multiple_layers`, `cube_layers`, `remaining_array_layers`, `remaining_array_layers_twostep`. |
| Image dimensions table | [`vktApiImageClearingTests.cpp#L2527-L2529`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2527-L2529) | Twelve dimension combinations exercised by `clear_color_image` and depth/stencil image clears. |
| Sample-count suffix generator | [`vktApiImageClearingTests.cpp#L2199-L2222`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2199-L2222) | Generates `_N_samples` suffixes for multisample color-attachment clears. |
| `createCoreImageClearingTests()` | [`vktApiImageClearingTests.cpp#L3192-L3195`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3192-L3195) | Wraps `createImageClearingTestsCommon()` with `ALLOCATION_KIND_SUBALLOCATED`. |
| `createDedicatedAllocationImageClearingTests()` | [`vktApiImageClearingTests.cpp#L3197-L3200`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3197-L3200) | Wraps `createImageClearingTestsCommon()` with `ALLOCATION_KIND_DEDICATED`. |
| `createImageClearingTests()` (public entry) | [`vktApiImageClearingTests.cpp#L3204-L3214`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214) | Adds `core` and `dedicated_allocation` direct children under `image_clearing`. |
| Parent-category registration | [`vktApiTests.cpp#L110`](../../../modules/vulkan/api/vktApiTests.cpp#L110) | `image_clearing` group added under `api` by `createApiTests()`. |
| Mustpass evidence (`core`) | [`api.txt#L277512`](../../../mustpass/main/vk-default/api.txt#L277512) | Primary `core.clear_color_image` mustpass range start; `core.clear_color_attachment.cube_layers` starts at [`api.txt#L272367`](../../../mustpass/main/vk-default/api.txt#L272367). |
| Mustpass evidence (`dedicated_allocation`) | [`api.txt#L300330`](../../../mustpass/main/vk-default/api.txt#L300330) | `dedicated_allocation.clear_color_image` mustpass range start. |

## Questions / Risk Points for User Audit

- Is the primary behavioral axis (intermediate node / subgroup) the right choice, or should the parent context (`core` vs `dedicated_allocation`) be promoted to primary? The current identification reflects that each subgroup exercises a distinct Vulkan clear command, while the parent context only changes allocation strategy.
- Is the `generalLayout` mode correctly characterized as a separate driver path? The source code substitutes `VK_IMAGE_LAYOUT_GENERAL` for `TRANSFER_DST_OPTIMAL` or `COLOR_ATTACHMENT_OPTIMAL`, which exercises the implementation's acceptance of `GENERAL` as the clear layout.
- Is the `2d_array_compatible_3d` case correctly attributed to `VK_KHR_maintenance1`? The source sets `create2DArrayCompatible = true` for selected 3D `clear_color_image` cases, but `checkSupport` does not explicitly gate `VK_KHR_maintenance1`; the support is implicit in the `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` creation flag.
- Are the `_multiple_subresourcerange` cases correctly described as overlapping-range tests? The source code clears two subresource ranges with different mip-level and layer subsets, but the exact overlap pattern is set at instance construction time and was not fully inspected.
- Is the multisample color-attachment path correctly described as clear-then-resolve? The source records `vkCmdClearAttachments` on the multisample image, then `vkCmdResolveImage` to a single-sample image before readback. A failure on a multisample case could come from the clear, the resolve, or the readback of the resolved image.
- Are the `_clamp_input` thresholds correctly described for floating-point formats? The source applies the `_clamp_input` parameter set only when `matchTextureChannelClass` is true and `textureChannelClass == TEXTURECHANNELCLASS_UNSIGNED_FIXED_POINT`, so floating-point formats are not affected by the clamp-input cases.

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge section into a brief unordered list of necessary prerequisites: the three Vulkan clear commands and their scope differences, `VkImageSubresourceRange` and `VK_REMAINING_ARRAY_LAYERS`, separate depth/stencil layouts, and clear-value clamping for unsigned fixed-point formats.
- Preserve the three-command distinction in `## Behavior Parameters` because each subgroup maps directly to one of the three Vulkan clear commands.
- Carry the `### Failure Cause Mapping` table directly into the final page's `## Failure Meaning` -> `### Failure Cause Mapping`. Write `### Cause Analysis` fresh during the rewrite, expanding each cause with `**Possible failure symptoms:**` and `**Possible implementation causes:**` paragraphs grounded in Vulkan spec semantics and source inspection.
- Carry the `## Behavior Parameter Identification` conclusion (intermediate node as primary axis; parent context as secondary axis) into `## Behavior Parameters` with `### <subgroup name>` subsections for each subgroup.
- Move the Source Mapping table into `## Source Reference Appendix` with minimal edits.
- The brief's "Important Variations and Special Cases" section should be distributed across `## Behavior Parameters`, `## Case Pruning`, and `## Key Takeaways` in the final page rather than preserved as a standalone section.
- The brief's teaching material on thresholds should be condensed to a single paragraph in `## Runtime Execution and Result Checking`; the per-channel-class threshold formulas belong only in the Cause Analysis for threshold-related failures.
- Resolve the risk points above by treating the source code and the test's structural evidence as authoritative: keep `generalLayout` as a separate driver path, attribute `2d_array_compatible_3d` to `VK_KHR_maintenance1` implicitly via the creation flag, and characterize the multisample color-attachment path as clear-then-resolve.
