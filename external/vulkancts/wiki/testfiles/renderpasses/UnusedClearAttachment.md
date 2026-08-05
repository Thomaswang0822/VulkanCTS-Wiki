## Overview

**Core question:** When `vkCmdClearAttachments` targets an attachment that the subpass marks `VK_ATTACHMENT_UNUSED`, does the implementation leave that image's contents untouched?

- This page covers the `unused_clear_attachments` test family registered under the `renderpasses` test category and implemented in [vktRenderPassUnusedClearAttachmentTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp).
- Each test case builds a render pass (or dynamic rendering instance) with up to four color attachments and an optional depth/stencil attachment. Some of those attachments are referenced by the subpass; the rest are marked `VK_ATTACHMENT_UNUSED`.
- Inside the render pass instance the test records `vkCmdClearAttachments` against every attachment index, including the unused ones, without issuing any draw.
- Passing requires the used attachments to take the clear value and the unused attachments to keep their initial contents.

## Background Knowledge

- **`VK_ATTACHMENT_UNUSED`.** A subpass attachment reference may point at a real attachment index or carry the sentinel `VK_ATTACHMENT_UNUSED`. The sentinel tells the implementation that this reference slot is not bound to an image view for this subpass. For color references the slot at `pColorAttachments[i]` may be unused even when the framebuffer still attaches an image at that index.
- **`vkCmdClearAttachments` and unbacked aspects.** The Vulkan specification states that if an attachment's `aspectMask` is not backed by an image view, the clear has no effect on that aspect
  [clears.adoc](../../../../vulkan-docs/src/chapters/clears.adoc#L294-L295). This is the property the test family exercises.
- **`VK_ATTACHMENT_LOAD_OP_LOAD`.** All attachments in this test use `VK_ATTACHMENT_LOAD_OP_LOAD`, so each image must already contain a defined value before the render pass instance begins. The test pre-clears every image to that initial value, which makes an illegal overwrite of an unused attachment observable on readback.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.unused_clear_attachments
```

The test family is attached to the `suballocation` group under five rendering variants of the `renderpasses` test category: `renderpass1`, `renderpass2`, and the `dynamic_rendering` sub-variants `primary_cmd_buff`, `partial_secondary_cmd_buff`, and `complete_secondary_cmd_buff`. Only the monolithic pipeline construction type registers this group; the `graphics_pipeline_library` dynamic-rendering sub-variant is gated off at the dispatcher because it uses fast-linked libraries instead
[vktRenderPassTests.cpp#L8571-L8574](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8574). The group itself is flat: it holds leaf test cases directly with no intermediate nodes
[vktRenderPassUnusedClearAttachmentTests.cpp#L1276](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1276).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Depth/stencil type | `DEPTH_STENCIL_NONE`, `DEPTH_STENCIL_DEPTH_ONLY`, `DEPTH_STENCIL_STENCIL_ONLY`, `DEPTH_STENCIL_BOTH` | Selects which depth/stencil aspect, if any, the framebuffer and clear cover. Drives the depth-only, stencil-only, both, and no-depth-stencil subfamilies. | [DepthStencilType enum](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L55-L62) |
| Depth/stencil format | `d32`, `s8`, `d32s8` | Depth-only tries `D32_SFLOAT` and `D32_SFLOAT_S8_UINT`; stencil-only tries `S8_UINT` and `D32_SFLOAT_S8_UINT`; both uses only `D32_SFLOAT_S8_UINT`. Each format becomes a token in the case name. | [getFormats](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L134-L151) |
| Color attachment count | `0`, `1`, `4` | Sizes the color attachment array. `0` is only used together with a depth/stencil attachment; `4` matches the guaranteed minimum `maxColorAttachments`. | [COLOR_ATTACHMENTS_NUMBER](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L48), [registration loop](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1306-L1312) |
| Per-attachment used flag | all subsets of used/unused | For the `1` and `4` color attachment counts, `runCallbackOnCombination` enumerates every used/unused assignment. Names encode the subset as `colorused`/`colorunused` tokens. | [runCallbackOnCombination](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1239-L1255), [getCombName](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1262-L1268) |
| Depth/stencil used flag | `false`, `true` | When a depth/stencil attachment exists, this flag decides whether the subpass references it or marks it `VK_ATTACHMENT_UNUSED`. Names append `_used`/`_unused`. | [DE_BOOL_VALUES](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L53), [registration loop](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1285-L1287) |

## Behavior Parameters

The behavioral axis is the used/unused state of each attachment slot, recorded as case-name tokens. The depth/stencil type and format dimensions configure which aspect the clear targets but do not change the core mechanism.

### `colorused` / `colorunused` per slot

Each color slot is either referenced by the subpass (`colorused`) or marked `VK_ATTACHMENT_UNUSED` (`colorunused`). The test always records a `vkCmdClearAttachments` entry for every color index. A used slot must end up holding the clear color; an unused slot must keep its initial color. With four color attachments the test enumerates all sixteen used/unused combinations, so each slot gets exercised in both roles across the matrix.

### `depthonly` / `stencilonly` / `depthstencil` / `nods`

This dimension chooses the depth/stencil shape. `nods` means no depth/stencil attachment at all. `depthonly`, `stencilonly`, and `depthstencil` attach a depth/stencil image and clear the matching aspect (`VK_IMAGE_ASPECT_DEPTH_BIT`, `VK_IMAGE_ASPECT_STENCIL_BIT`, or both) via `getClearAspectMask`
[vktRenderPassUnusedClearAttachmentTests.cpp#L104-L115](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L104-L115).

### `_used` / `_unused` for the depth/stencil slot

When a depth/stencil attachment exists, the same used/unused choice applies to it. `_used` means the subpass references the depth/stencil image; `_unused` means the reference is `VK_ATTACHMENT_UNUSED`. The clear entry for the depth/stencil aspect is always recorded, so the unused case checks that clearing an unbacked depth/stencil aspect leaves the image untouched.

## Shader Analysis

This test family has no shader-level behavior to analyze. The vertex and fragment shaders exist only to satisfy graphics pipeline creation; the test records no draw and never runs them. Source comments state this directly
[vktRenderPassUnusedClearAttachmentTests.cpp#L294-L333](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L294-L333).

## Runtime Execution and Result Checking

- Each test creates up to four `R8G8B8A8_UNORM` color images and, when the case has a depth/stencil type, one depth/stencil image in the case's format. Every image is pre-cleared to a known initial value: color `(0, 0, 0, 1)`, depth `1.0`, stencil `0`
  [vktRenderPassUnusedClearAttachmentTests.cpp#L449-L466](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L449-L466).
- The pre-clear uses `vkCmdClearColorImage` / `vkCmdClearDepthStencilImage` with layout transitions into `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` / `VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL` so the render pass can begin with `VK_ATTACHMENT_LOAD_OP_LOAD`
  [vktRenderPassUnusedClearAttachmentTests.cpp#L541-L710](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L541-L710).
- The render pass or dynamic rendering instance is begun, the graphics pipeline is bound, and `vkCmdClearAttachments` is recorded with one entry per attachment index (color and depth/stencil) using clear values `(1, 1, 1, 1)`, depth `0.0`, stencil `255`. No draw is issued
  [vktRenderPassUnusedClearAttachmentTests.cpp#L887-L935](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L887-L935).
- After submission, each color image is read back and compared against the expected reference: the clear color for used slots, the initial color for unused slots, with tolerance `0.01f`
  [vktRenderPassUnusedClearAttachmentTests.cpp#L1124-L1164](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1124-L1164).
- Depth is read back (tolerance `0.001f`) and stencil is read back (exact match) against the same used/unused reference rule
  [vktRenderPassUnusedClearAttachmentTests.cpp#L1166-L1232](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1166-L1232).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Color images (up to 4) | Yes | Framebuffer / rendering attachment | Cleared by `vkCmdClearAttachments` | Yes | Holds initial color; used slots take the clear, unused slots must not. |
| Depth/stencil image | Yes, when the case has a D/S type | Subpass D/S attachment | Cleared by `vkCmdClearAttachments` on the case's aspect | Yes (depth and/or stencil) | Holds initial D/S values; same used/unused rule. |
| Graphics pipeline | Yes | Pipeline state | Bound but never drives a draw | No | Required to record `vkCmdClearAttachments` inside a render pass instance. |
| Vertex / fragment shaders | Yes | Shader modules in the pipeline | Never executed | No | Exist only to create a valid graphics pipeline. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any `colorunused` slot | The clear wrote to a color attachment the subpass marks `VK_ATTACHMENT_UNUSED`. |
| Any `colorused` slot | The clear did not apply to a color attachment the subpass references. |
| Depth/stencil `_unused` | The clear wrote to a depth/stencil aspect the subpass marks `VK_ATTACHMENT_UNUSED`. |
| Depth/stencil `_used` | The clear did not apply to a depth/stencil aspect the subpass references. |
| Any case | Shared infrastructure failure: image pre-clear, layout transition, or readback comparison. |

### Cause Analysis

#### Clear wrote to an attachment marked `VK_ATTACHMENT_UNUSED`

**Possible failure symptoms:** The readback for an unused color or depth/stencil slot does not match the initial value. For color, a pixel differs from `(0, 0, 0, 1)` by more than `0.01f`; for depth it differs from `1.0` by more than `0.001f`; for stencil it is not exactly `0`
[vktRenderPassUnusedClearAttachmentTests.cpp#L1131-L1162](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1131-L1162),
[vktRenderPassUnusedClearAttachmentTests.cpp#L1166-L1231](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1166-L1231).

**Possible implementation causes:** The Vulkan specification requires that a clear on an aspect not backed by an image view has no effect
[clears.adoc#L294-L295](../../../../vulkan-docs/src/chapters/clears.adoc#L294-L295). A failure here points at driver or hardware handling of `vkCmdClearAttachments` that routes the clear to the framebuffer image at the cleared index even though the subpass reference is `VK_ATTACHMENT_UNUSED`, or at render pass / dynamic rendering setup that fails to record the unused reference correctly.

#### Clear did not apply to a referenced attachment

**Possible failure symptoms:** The readback for a used slot does not match the clear value: color other than `(1, 1, 1, 1)` within tolerance, depth other than `0.0` within tolerance, or stencil other than `255`.

**Possible implementation causes:** The subpass references the image, so the clear must take effect. A failure suggests the clear was dropped or misrouted for a referenced attachment, or that the layout transition around the clear did not make the write visible at readback time. Distinguishing a clear-routing bug from a synchronization or layout-transition bug requires source-level investigation of the specific attachment index and aspect.

#### Shared infrastructure failure

**Possible failure symptoms:** Mismatches appear across both used and unused slots, or the readback image is in the wrong layout, preventing a clean comparison.

**Possible implementation causes:** The pre-clear step, the layout barriers into and out of the render pass instance, or the readback copy could fail independent of the unused-attachment rule. These affect every case using the affected image or format rather than only the unused slots.

## Case Pruning

### Requirement-based pruning

- Render pass 2 cases require `VK_KHR_create_renderpass2`; dynamic rendering cases require `VK_KHR_dynamic_rendering`
  [vktRenderPassUnusedClearAttachmentTests.cpp#L271-L279](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L271-L279).
- Every color, depth, and stencil format is checked with `getPhysicalDeviceImageFormatProperties` for the relevant usage flag before the case runs; unsupported formats raise `NotSupportedError` rather than failing
  [vktRenderPassUnusedClearAttachmentTests.cpp#L253-L287](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L253-L287).
- One dynamic-rendering secondary-command-buffer combination is skipped at registration because the spec forbids declaring a depth/stencil format in the inheritance info when the primary command buffer's rendering info supplies no depth/stencil image view
  [vktRenderPassUnusedClearAttachmentTests.cpp#L1289-L1303](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1289-L1303).

### Design-based pruning

- The zero-color-attachment case is only generated when a depth/stencil attachment exists; a case with no attachments at all would have nothing to clear
  [vktRenderPassUnusedClearAttachmentTests.cpp#L1308-L1312](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1308-L1312).
- The `DEPTH_STENCIL_NONE` type has a single format (`VK_FORMAT_UNDEFINED`) and skips the inner depth/stencil-used loop, so it generates one format pass instead of two
  [vktRenderPassUnusedClearAttachmentTests.cpp#L1335-L1336](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1335-L1336).
- Color attachment counts other than `0`, `1`, and `4` are not registered; `4` already covers the guaranteed minimum `maxColorAttachments`.

## Key Takeaways

- The whole test family probes one spec sentence: a clear on an aspect not backed by an image view must have no effect
  [clears.adoc#L294-L295](../../../../vulkan-docs/src/chapters/clears.adoc#L294-L295).
- Used and unused attachments are exercised in the same render pass instance and cleared through the same `vkCmdClearAttachments` call, so a single case checks both that used slots take the clear and that unused slots do not.
- The depth/stencil type and format dimensions vary which aspect the clear targets but do not change the core used/unused mechanism.
- No shader runs; the shaders exist only so a graphics pipeline can be created and `vkCmdClearAttachments` can be recorded inside a render pass instance.
- See `## Failure Meaning` for how a failing pixel is interpreted depending on whether its slot was used or unused.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Dispatcher attachment (monolithic gate) | [vktRenderPassTests.cpp#L8571-L8574](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8574) | Adds the `unused_clear_attachments` group only under the monolithic pipeline construction type. |
| Test family registration | [vktRenderPassUnusedClearAttachmentTests.cpp#L1272-L1342](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1272-L1342) | Builds the flat leaf matrix over depth/stencil type, format, color count, and used/unused flags. |
| Depth/stencil type and format mapping | [vktRenderPassUnusedClearAttachmentTests.cpp#L55-L151](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L55-L151) | Defines the `DepthStencilType` enum, aspect masks, and per-type format lists. |
| Render pass creation | [vktRenderPassUnusedClearAttachmentTests.cpp#L336-L443](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L336-L443) | Builds attachment descriptions and references, marking unused slots with `VK_ATTACHMENT_UNUSED`. |
| Clear recording | [vktRenderPassUnusedClearAttachmentTests.cpp#L869-L936](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L869-L936) | Records `vkCmdClearAttachments` for every attachment index inside the render pass instance. |
| Dynamic rendering clear recording | [vktRenderPassUnusedClearAttachmentTests.cpp#L939-L1110](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L939-L1110) | Same clear logic for the dynamic rendering path. |
| Result checking | [vktRenderPassUnusedClearAttachmentTests.cpp#L1112-L1235](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1112-L1235) | Reads back color, depth, and stencil and compares against the used/unused reference values. |
| Support checks | [vktRenderPassUnusedClearAttachmentTests.cpp#L271-L287](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L271-L287) | Requires the render pass 2 / dynamic rendering extensions and checks format support. |
| Mustpass entries (renderpass1) | [renderpasses.txt#L47272-L47479](../../../mustpass/main/vk-default/renderpasses.txt#L47272-L47479) | 208 leaf cases under `renderpass1.suballocation.unused_clear_attachments`. |
| Mustpass entries (renderpass2) | [renderpasses.txt#L79610-L79817](../../../mustpass/main/vk-default/renderpasses.txt#L79610-L79817) | 208 leaf cases under `renderpass2.suballocation.unused_clear_attachments`. |
| Mustpass entries (dynamic_rendering, primary) | [renderpasses.txt#L26404-L26611](../../../mustpass/main/vk-default/renderpasses.txt#L26404-L26611) | 208 leaf cases under `dynamic_rendering.primary_cmd_buff.suballocation.unused_clear_attachments`. |
| Mustpass entries (dynamic_rendering, partial secondary) | [renderpasses.txt#L12248-L12360](../../../mustpass/main/vk-default/renderpasses.txt#L12248-L12360) | 113 leaf cases under `dynamic_rendering.partial_secondary_cmd_buff.suballocation.unused_clear_attachments`; fewer than the others due to the registration-loop skip for the unsupported secondary-command-buffer D/S combination. |
| Mustpass entries (dynamic_rendering, complete secondary) | [renderpasses.txt#L3139-L3346](../../../mustpass/main/vk-default/renderpasses.txt#L3139-L3346) | 208 leaf cases under `dynamic_rendering.complete_secondary_cmd_buff.suballocation.unused_clear_attachments`. |
