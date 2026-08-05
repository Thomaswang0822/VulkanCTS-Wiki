## Overview

**Core question:** When a render pass begins, can the implementation clear only the attachments whose `loadOp` is `VK_ATTACHMENT_LOAD_OP_CLEAR`, while preserving the contents of attachments whose `loadOp` is `VK_ATTACHMENT_LOAD_OP_LOAD`?

- This page covers the `clear_some_attachments` test family implemented in [vktRenderPassClearSomeAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp) and attached to the `renderpasses` test category's `suballocation` subgroup under every supported rendering type.
- The family registers two test case leaves, `clear_only_color` and `clear_only_depth`, that share one mechanism: a render pass that clears exactly one of two attachments and loads the other.
- Each case seeds both attachments with known values before the render pass, then checks that the cleared attachment took the render-pass clear value while the loaded attachment kept its pre-render-pass value.
- Passing requires both attachments to retain the values implied by their `loadOp` after the render pass ends.

## Background Knowledge

- **Render pass load operations.** A render pass attachment's `loadOp` controls how its contents are treated at the beginning of the render area. `VK_ATTACHMENT_LOAD_OP_CLEAR` writes a uniform clear value across the render area before any drawing; `VK_ATTACHMENT_LOAD_OP_LOAD` preserves the attachment's previous contents as the initial values. The two operations are mutually exclusive per attachment, so a render pass can intentionally clear some attachments and load others in the same instance (see the Vulkan spec section *Render Pass Load Operations*).
- **Clear value source.** For `VK_ATTACHMENT_LOAD_OP_CLEAR`, the uniform value is supplied in `VkClearValue` through `VkRenderPassBeginInfo` (legacy/RenderPass2) or `VkRenderingAttachmentInfo::clearValue` (dynamic rendering). For `VK_ATTACHMENT_LOAD_OP_LOAD`, no clear value is consumed; the pre-existing image contents are what matters.
- **Pre-render-pass seeding via `vkCmdClearColorImage` / `vkCmdClearDepthStencilImage`.** These transfer-stage commands clear an image outside any render pass. The test uses them to write a known starting value into every attachment before the render pass, which is what makes a `LOAD` attachment's value observable on readback.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.clear_some_attachments
├── clear_only_color
└── clear_only_depth
```

The representative root shows the `renderpass1` rendering type. The same `clear_some_attachments` group is also registered under `renderpass2` and `dynamic_rendering`, each within the `suballocation` subgroup, monolithic pipeline only. Registered group name: `"clear_some_attachments"` at [vktRenderPassClearSomeAttachmentsTests.cpp#L429](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L429). Each of the two test case leaves is registered by the same loop at [vktRenderPassClearSomeAttachmentsTests.cpp#L436-L447](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L436-L447).

## Parameter Dimensions and Observed Values

The family has a small fixed matrix. Only one dimension selects tested behavior; the rest are fixed setup.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `TestMode` (test case leaf) | `clear_only_color`, `clear_only_depth` | Selects which attachment gets `loadOp = CLEAR` and which gets `loadOp = LOAD`; flips which clear value the host expects after the render pass. | [enum](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L38-L42), [case registration](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L436-L447) |
| Rendering type | `renderpass1`, `renderpass2`, `dynamic_rendering` | Same logic executed through three different begin/end paths. Changes the load-op plumbing path, not the correctness contract. | [mustpass](../../../mustpass/main/vk-default/renderpasses.txt#L37646-L37647) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` (fixed) | Fixed color attachment format for both cases. | [iterate()](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L91) |
| Depth/stencil format | `D24_UNORM_S8_UINT`, else `D32_SFLOAT_S8_UINT` (auto-selected) | One of the two must be supported; selected by querying image format properties. Only the depth aspect is checked. | [format selection](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L113-L117) |
| Image size | `8x8` (fixed) | Small render target; only four sample pixels are verified. | [size](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L88-L89) |

## Behavior Parameters

The primary behavioral axis is the test case leaf, because each leaf changes which attachment is cleared and what value the host expects on readback. The two values share the same render-pass structure; they differ in the `loadOp` assignment and the expected result.

### `clear_only_color`: clear the color attachment, load the depth attachment

- The color attachment has `loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR` and `storeOp = VK_ATTACHMENT_STORE_OP_STORE`.
- The depth attachment has `loadOp = VK_ATTACHMENT_LOAD_OP_LOAD` and `storeOp = VK_ATTACHMENT_STORE_OP_STORE`.
- After the render pass, the host expects the color image to equal the render-pass color clear value `(0.7, 0.1, 0.5, 0.3)` and the depth image to equal its pre-render-pass seeded value `0.2`.
- Mechanism: the `loadOp` assignment is selected by `TestMode::CLEAR_ONLY_COLOR` at [createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L288-L294) for legacy/RenderPass2 and by the default `VkRenderingAttachmentInfo` block for dynamic rendering.

### `clear_only_depth`: clear the depth attachment, load the color attachment

- The depth attachment has `loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR` and `storeOp = VK_ATTACHMENT_STORE_OP_STORE`.
- The color attachment has `loadOp = VK_ATTACHMENT_LOAD_OP_LOAD` and `storeOp = VK_ATTACHMENT_STORE_OP_STORE`.
- After the render pass, the host expects the depth image to equal the render-pass depth clear value `0.7` and the color image to equal its pre-render-pass seeded value `(0.2, 0.8, 0.4, 0.6)`.
- Mechanism: the `loadOp` assignment is inverted by `TestMode::CLEAR_ONLY_DEPTH` at [createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L290-L294) and by the dynamic-rendering swap at [iterate()](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L157-L161).

## Shader Analysis

This test has no shaders. No graphics pipeline is bound; the render pass instance is begun and ended with no draw recorded. The tested behavior is the fixed-function render-pass load operation on the attachments, not any programmable stage. A representative shader walkthrough is therefore not applicable.

## Runtime Execution and Result Checking

The execution flow is the same for both leaves; only the `loadOp` assignment and the expected values differ.

- **Image creation.** A color image (`VK_FORMAT_R8G8B8A8_UNORM`) and a depth/stencil image (`D24_UNORM_S8_UINT`, or `D32_SFLOAT_S8_UINT` if the former is unsupported) are created with `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` / `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT` plus transfer usage, each backed by a host-visible buffer for readback via `ImageWithBuffer` [vktRenderPassClearSomeAttachmentsTests.cpp#L93-L121](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L93-L121).
- **Pre-render-pass seeding.** Both images are transitioned from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, then cleared outside any render pass: the color image to `(0.2, 0.8, 0.4, 0.6)` via `vkCmdClearColorImage`, and the depth image to depth `0.2`, stencil `0` via `vkCmdClearDepthStencilImage`. These are the values a `LOAD` attachment must preserve [vktRenderPassClearSomeAttachmentsTests.cpp#L182-L204](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L182-L204).
- **Layout transition before render pass.** Two barriers transition the images from transfer-dst layout to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` and `VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL`, with src access `VK_ACCESS_TRANSFER_WRITE_BIT` and dst access `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` / `VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT` [vktRenderPassClearSomeAttachmentsTests.cpp#L190-L208](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L190-L208).
- **Render pass instance.** `VkRenderPassBeginInfo` carries clear values for both attachments (color clear `(0.7, 0.1, 0.5, 0.3)`, depth clear `0.7`, stencil clear `2`), but only the attachment whose `loadOp` is `CLEAR` consumes its clear value; the `LOAD` attachment ignores its clear value and preserves its seeded contents. No draw is recorded; the instance is immediately ended. This isolates the load operation as the only thing that writes the attachments [vktRenderPassClearSomeAttachmentsTests.cpp#L210-L228](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L210-L228).
- **Dynamic-rendering variant.** When no render-pass handle is created (dynamic rendering), the same `loadOp` and clear values are expressed through `VkRenderingAttachmentInfo`. If the `SharedGroupParams` flag is set, the begin/end rendering is recorded into a secondary command buffer that the primary buffer executes [vktRenderPassClearSomeAttachmentsTests.cpp#L143-L178](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L143-L178).
- **Readback.** Both images are copied to their backing buffers with layout/access transitions to `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` and `VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT`; only the depth aspect is copied for the depth/stencil image [vktRenderPassClearSomeAttachmentsTests.cpp#L230-L234](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L230-L234).
- **Host validation.** After invalidating both allocations, the host computes expected values based on `TestMode`: the `CLEAR` attachment is expected at the render-pass clear value and the `LOAD` attachment at the pre-render-pass seeded value [vktRenderPassClearSomeAttachmentsTests.cpp#L254-L262](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L254-L262). Four sample pixels at `(0,0)`, `(2,2)`, `(4,4)`, `(6,6)` are compared against the expected color and depth with epsilon `0.05f`. Any mismatch fails the case [vktRenderPassClearSomeAttachmentsTests.cpp#L264-L278](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L264-L278).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Color image + backing buffer | Yes | Framebuffer / `VkRenderingAttachmentInfo` | Read or cleared by render-pass load op; stored by store op | Yes, through `ImageWithBuffer` backing allocation | Carries the color attachment value checked against the expected color. |
| Depth/stencil image + backing buffer | Yes | Framebuffer / `VkRenderingAttachmentInfo` (depth aspect) | Read or cleared by render-pass load op; stored by store op | Yes, depth aspect only | Carries the depth attachment value checked against the expected depth. |
| Render pass / dynamic rendering info | Yes | Pipeline state | Begin/end render-pass instance | No | Declares the `loadOp`/`storeOp` pair per attachment and supplies the clear value for the `CLEAR` attachment. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_only_color` | Wrong attachment was cleared/loaded; the cleared color value or the loaded depth value was not preserved. |
| `clear_only_depth` | Wrong attachment was cleared/loaded; the cleared depth value or the loaded color value was not preserved. |

Both leaves share a common infrastructure cause: incorrect image layout, access-mask, or copyback path would also fail either case, because the same barriers and copy commands serve both attachments.

### Cause Analysis

#### Wrong attachment was cleared/loaded

**Possible failure symptoms:** At one of the four sample pixels, either the attachment that should have been cleared does not equal the render-pass clear value, or the attachment that should have been loaded does not equal its pre-render-pass seeded value. The color channel difference exceeds epsilon `0.05f` in any component, or the depth difference exceeds `0.05f` [vktRenderPassClearSomeAttachmentsTests.cpp#L264-L278](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L264-L278).

**Possible implementation causes:** Per the Vulkan spec, `VK_ATTACHMENT_LOAD_OP_CLEAR` must write the supplied clear value across the render area before drawing, and `VK_ATTACHMENT_LOAD_OP_LOAD` must preserve the previous contents as the initial values; load operations execute in `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT` for color and `VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT` for depth/stencil. A failure here therefore points at the driver's handling of per-attachment `loadOp` selection, clear-value plumbing from `VkRenderPassBeginInfo` or `VkRenderingAttachmentInfo::clearValue`, or the load/store execution order relative to the pre-render-pass seeded contents. Specific suspect areas include applying the clear to the wrong attachment, consuming the wrong clear value, or treating a `LOAD` attachment as if it were cleared (or vice versa).

#### Incorrect image layout, access-mask, or copyback path

**Possible failure symptoms:** The same sample-pixel comparison fails, but the wrong value is not attributable to a single `loadOp`. It may instead look like stale, garbage, or partially seeded contents on either attachment.

**Possible implementation causes:** The test relies on three layout transitions being honored: `UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` before seeding, transfer-dst to the attachment-optimal layout before the render pass, and the attachment-optimal layout to copyback. The corresponding src/dst access masks are `VK_ACCESS_TRANSFER_WRITE_BIT`, `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT`, and `VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT`. If the driver does not honor a layout transition, drops a write-before-read dependency, or returns stale backing-buffer contents, the host-visible pixels will not match the expected values. A host-side `invalidateAlloc` miss would also produce stale reads, though that is a CTS host-side concern rather than an implementation defect.

## Case Pruning

### Requirement-based pruning

- The case requires `VK_KHR_create_renderpass2` when the rendering type is `RENDERPASS2`, and `VK_KHR_dynamic_rendering` when the rendering type is `RENDERING_TYPE_DYNAMIC_RENDERING`, checked in `AttachmentTest::checkSupport` [vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417).
- Pipeline construction requirements are checked through `checkPipelineConstructionRequirements`, which gates the monolithic-only registration.
- The depth/stencil format is chosen at runtime: if `D24_UNORM_S8_UINT` is not supported with the required usage, `D32_SFLOAT_S8_UINT` is used instead. The case does not run if neither is supported [vktRenderPassClearSomeAttachmentsTests.cpp#L113-L117](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L113-L117).

### Design-based pruning

- The family is registered only for the monolithic pipeline construction type and only when `useSecondaryCmdBuffer` matches `secondaryCmdBufferCompletelyContainsDynamicRenderpass`, as gated at the attachment site [vktRenderPassTests.cpp#L8571-L8577](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8577). Graphics pipeline library and other construction types are intentionally excluded.
- The image is fixed at `8x8` and only four diagonal sample pixels are compared. Full-image verification is outside the test's scope.
- Stencil is seeded and a stencil clear value is supplied, but only the depth aspect is copied back and checked. Stencil readback is intentionally not part of the validation.

## Key Takeaways

- The family exercises one property: a render pass must clear only the attachment whose `loadOp` is `CLEAR` and must preserve the attachment whose `loadOp` is `LOAD`. The two leaves are mirror images of that property across color and depth.
- Both attachments are seeded before the render pass and no draw is recorded, so the only thing that can change either attachment inside the render pass is the load operation itself. This isolates the load op as the unit under test.
- Because both leaves share the same barriers, copyback, and host validation, a failure that is not explained by a wrong clear/loaded value on one attachment points at the shared layout-transition or readback path. See `## Failure Meaning` for the case-by-case breakdown.
- The dynamic-rendering variant additionally covers the secondary-command-buffer path, where begin/end rendering are recorded into a secondary command buffer that the primary buffer executes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestMode` enum | [vktRenderPassClearSomeAttachmentsTests.cpp#L38-L42](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L38-L42) | Defines the two behavior-parameter values. |
| `iterate()` execution | [vktRenderPassClearSomeAttachmentsTests.cpp#L80-L281](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L80-L281) | Image creation, seeding, barriers, render-pass begin/end, copyback, and four-pixel validation. |
| `createRenderPass()` | [vktRenderPassClearSomeAttachmentsTests.cpp#L283-L369](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L283-L369) | Builds the render-pass object for legacy and RenderPass2, choosing per-attachment `loadOp` by `TestMode`. |
| Dynamic-rendering attachment setup | [vktRenderPassClearSomeAttachmentsTests.cpp#L143-L178](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L143-L178) | Defines `VkRenderingAttachmentInfo` and the secondary-command-buffer begin/end rendering path. |
| `checkSupport()` | [vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417) | Requirement checks for RenderPass2 and dynamic rendering extensions. |
| Test family registration | [vktRenderPassClearSomeAttachmentsTests.cpp#L426-L450](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L426-L450) | Creates the `clear_some_attachments` group and adds the two test case leaves. |
| Attachment to `suballocation` subgroup | [vktRenderPassTests.cpp#L8571-L8577](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8577) | Gates monolithic-only registration and the secondary-command-buffer condition. |
| Mustpass entry (renderpass1) | [renderpasses.txt#L37646-L37647](../../../mustpass/main/vk-default/renderpasses.txt#L37646-L37647) | Confirms the two `dEQP-VK.renderpasses.renderpass1.suballocation.clear_some_attachments.*` leaves. |
