## Overview

**Core question:** When a dynamic render pass instance clears an attachment under a multiview view mask, does the implementation apply the clear only to the view layers selected by the mask and leave all other layers at their pre-render contents?

- This page covers the `multiview_clear` test family in [`vktDynamicRenderingMultiviewClearTests.cpp`](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp). The family is created by [`createDynamicRenderingMultiviewClearTests()`](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L456) and attached under `renderpasses.dynamic_rendering.primary_cmd_buff` ([dispatcher attach](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8539)).
- It registers 75 test case leaves that combine five attachment formats with five view masks and three clear mechanisms: render-pass clear, `vkCmdClearAttachments` over two sub-regions, and `vkCmdClearAttachments` over one full-region rectangle.
- The core idea is to seed every layer of a multiview image with a known initial value, then clear only the layers selected by the view mask using either the render pass load operation or `vkCmdClearAttachments`, and read back every layer to confirm that in-view layers received the clear value while out-of-view layers retained the initial value.
- The test is monolithic pipeline only and is registered under `primary_cmd_buff` because it does not exercise secondary command buffer or graphics pipeline library paths.

## Background Knowledge

- **Multiview.** Multiview lets one render pass instance write to multiple layers of an attachment array by broadcasting fragment work across the views selected by a view mask. Each bit in the mask selects one view, and view index `i` corresponds to array layer `i`. The dynamic rendering API carries the view mask in `VkRenderingInfo::viewMask` instead of in a subpass description.
- **Dynamic rendering.** `VK_KHR_dynamic_rendering` replaces render pass objects with `vkCmdBeginRendering` / `vkCmdEndRendering`. The render pass load operation becomes the `loadOp` of `VkRenderingAttachmentInfo`, and `vkCmdClearAttachments` remains available inside a dynamic render pass instance to clear sub-regions of the framebuffer.
- **`vkCmdClearAttachments` base array layer.** `VkClearRect::baseArrayLayer` and `layerCount` select which layers a `vkCmdClearAttachments` call affects. For multiview, the clear applies to view indices in the view mask whose corresponding array layer falls inside the `[baseArrayLayer, baseArrayLayer + layerCount)` range. This test uses `baseArrayLayer = 0` and `layerCount = 1`, matching the view-at-a-time semantics documented for multiview clears.

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.multiview_clear
├── r8g8b8a8_unorm
├── d16_unorm
├── d24_unorm_s8_uint
├── d32_sfloat_s8_uint
└── s8_uint
```

The tree shows the five format intermediate nodes. Each format node expands into five view-mask subgroups (`view_mask_0x1`, `view_mask_0x2`, `view_mask_0x4`, `view_mask_0x8`, `view_mask_0xf`), and each view-mask subgroup holds three leaves (`_render_pass`, `_clear_regions`, `_clear_full`), for 15 leaves per format and 75 total ([registration loop](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L462-L496)). The family is registered only under `primary_cmd_buff` and does not appear under `renderpass1` or `renderpass2` because it tests a dynamic-rendering-specific interaction with multiview.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Attachment format | `R8G8B8A8_UNORM`, `D16_UNORM`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT`, `S8_UINT` | Selects color-only, depth-only, combined depth/stencil, or stencil-only attachment. Stencil-only uses a separate aspect and is verified against a stencil-only buffer. | [formatList](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L460-L463) |
| View mask | `1`, `2`, `4`, `8`, `15` | The bitmask selecting which view layers the render pass clears. The first four clear exactly one layer; `15` clears all four layers. | [viewMask loop](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L468) |
| Clear mechanism | `_render_pass`, `_clear_regions`, `_clear_full` | `_render_pass` uses the attachment load operation (`LOAD_OP_CLEAR`); the other two seed the image with `LOAD` then call `vkCmdClearAttachments` with either two quadrant rectangles or one full-image rectangle. | [test name construction](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L477-L493) |

## Behavior Parameters

The primary behavioral axis is the interaction between the view mask and the clear mechanism. The pass/fail condition is identical across formats: in-view layers receive the clear value and out-of-view layers retain the seeded value.

### View mask selects which layers receive the clear

For single-bit masks (`1`, `2`, `4`, `8`), exactly one layer should change to the clear value and the other three layers should keep the seeded value. For mask `15`, all four layers should change. This isolates the view-mask filtering from the clear operation itself.

### Clear mechanism varies the application path

The `_render_pass` leaf uses the `VkRenderingAttachmentInfo` load operation, which applies the clear to every in-view layer at render pass begin. The `_clear_regions` and `_clear_full` leaves load the seeded contents (`LOAD_OP_LOAD`), then issue `vkCmdClearAttachments` inside the dynamic render pass instance with two quadrant rectangles or one full rectangle respectively ([clear rectangle construction](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L475-L489)). This distinguishes render-pass-side clears from command-side clears that must also respect the view mask.

## Shader Analysis

No shaders are used. The test records no draw and no pipeline is bound, so there is no shader content to analyze. The `## Shader Analysis` section is present for template completeness and documents this explicitly.

## Runtime Execution and Result Checking

Each test case creates a multiview image with four array layers in the selected format, seeds every layer to a known initial value via `vkCmdClearColorImage` or `vkCmdClearDepthStencilImage` ([seeding](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L207-L221)), transitions to the rendering layout, and begins a dynamic render pass instance with `viewMask` set to the test parameter ([rendering info](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L245-L265)).

For `_render_pass` leaves, the attachment load operation is `LOAD_OP_CLEAR` and the clear value is white (`1.0, 1.0, 1.0, 1.0`) for color or `depth=1.0, stencil=255` for depth/stencil. For `_clear_regions` and `_clear_full` leaves, the load operation is `LOAD_OP_LOAD` and `vkCmdClearAttachments` is issued with the test's clear rectangles ([cmdClearAttachments](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L274-L286)).

After the render pass, the image is copied to host-visible buffers and each layer is compared against a host-built reference. The reference seeds every layer with the initial value, then applies the clear value to in-view layers (and, for the command-clear leaves, only within the clear rectangles) ([reference construction](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L345-L412)). Color and depth layers are compared with `tcu::floatThresholdCompare`; depth and stencil layers are compared with `tcu::dsThresholdCompare` ([comparators](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L413-L443)). A mismatch on any layer fails the test.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Single-bit view mask leaves | The clear applied to a layer not selected by the view mask, or did not apply to the selected layer, meaning the view-mask filtering was wrong. |
| `view_mask_0xf` leaves | The clear missed one or more of the four selected layers, meaning multi-view broadcasting did not reach every in-view layer. |
| `_render_pass` leaves | The dynamic render pass load operation (`LOAD_OP_CLEAR`) did not honor the view mask, so the clear affected the wrong set of layers. |
| `_clear_regions` / `_clear_full` leaves | `vkCmdClearAttachments` did not respect the view mask or the `VkClearRect` layer range inside a dynamic render pass instance. |
| Depth/stencil-only formats (`D16_UNORM`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT`, `S8_UINT`) | The depth or stencil aspect was cleared against the wrong layer set, independent of the color path. |
| Any leaf (common cause) | Image layout transition, format support, array layer allocation, or copyback produced wrong contents independent of the clear. |

### Cause Analysis

#### View-mask filtering applied the clear to the wrong layers

**Possible failure symptoms:** For a single-bit mask, an out-of-view layer shows the clear value or the in-view layer retains the seeded value. For mask `15`, one or more of the four in-view layers retain the seeded value.

**Possible implementation causes:** Dynamic rendering carries the view mask in `VkRenderingInfo::viewMask`, and both the render pass load operation and `vkCmdClearAttachments` must apply their effects only to views selected by that mask. A driver that ignores the view mask when applying `LOAD_OP_CLEAR`, or that applies `vkCmdClearAttachments` to array layers outside the selected views, produces this symptom. The single-bit masks isolate which view index was mishandled.

#### `vkCmdClearAttachments` layer range mishandled under multiview

**Possible failure symptoms:** The `_clear_regions` or `_clear_full` leaf fails while the `_render_pass` leaf for the same format and view mask passes, meaning the render-pass-side clear honored the view mask but the command-side clear did not.

**Possible implementation causes:** `vkCmdClearAttachments` takes a `VkClearRect` whose `baseArrayLayer` and `layerCount` select the target layers. This test uses `baseArrayLayer = 0` and `layerCount = 1`, which under multiview means the clear applies to the current view only. A driver that interprets the clear rect layer range against the full attachment array instead of against the view-mask-selected views clears the wrong layers. Source-level investigation is needed to distinguish a clear-rect layer-mapping bug from a view-mask propagation bug.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_KHR_dynamic_rendering` and `VK_KHR_multiview` ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L102-L103)).
- Each format is checked via `getPhysicalDeviceImageFormatProperties` for the selected format with the required usage, and the test throws `NotSupportedError` if the format, the required array layer count, or the required extent is unsupported ([format and extent checks](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L105-L123)).

### Design-based pruning

- The family is registered only under `primary_cmd_buff` and only with the monolithic pipeline. It does not route through the secondary command buffer or graphics pipeline library sub-variants because those paths do not change the view-mask filtering behavior under test.
- The `S8_UINT` stencil-only format has no depth or color aspect, so it is verified against a separate stencil buffer and exercises the stencil clear path independently of depth.

## Key Takeaways

- The test isolates one property: a clear applied during a dynamic render pass instance must respect the multiview view mask and affect only the selected view layers.
- Five view masks (four single-bit, one four-bit) make a per-view regression visible and confirm that the all-views case broadcasts correctly.
- Three clear mechanisms (render-pass load operation, `vkCmdClearAttachments` over two sub-regions, `vkCmdClearAttachments` over one full region) distinguish render-pass-side clears from command-side clears.
- Five formats cover color, depth-only, combined depth/stencil, and stencil-only aspects, confirming that the view-mask filtering holds for every attachment type.
- See [Failure Meaning](#failure-meaning) for how each view mask and clear mechanism maps to a distinct failure symptom.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [`createDynamicRenderingMultiviewClearTests`](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L456-L497) | Creates the group and generates all 75 leaves from the format, view mask, and clear mechanism matrix. |
| Dispatcher attach | [`vktRenderPassTests.cpp#L8539`](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8539) | Attaches the group under `renderpasses.dynamic_rendering.primary_cmd_buff`. |
| Test execution | [`runTest`](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L136-L335) | Seeds the image, records the dynamic render pass with the view mask and clear, and copies results back. |
| Verification | [reference construction and comparators](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L345-L445) | Builds the per-layer expected image and compares color with `tcu::floatThresholdCompare` and depth/stencil with `tcu::dsThresholdCompare`. |
| Support checks | [`checkSupport`](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L100-L124) | Requires `VK_KHR_dynamic_rendering` and `VK_KHR_multiview`, plus format, array layer, and extent support. |
| Clear rectangle construction | [clear rect setup](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L475-L489) | Builds the two quadrant rectangles for `_clear_regions` and the single full rectangle for `_clear_full`. |
| Dynamic rendering begin | [rendering info](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L245-L265) | Sets `viewMask`, attachment load operation, and clear value for the dynamic render pass instance. |
