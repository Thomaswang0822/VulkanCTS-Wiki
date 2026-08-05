## Overview

**Core question:** When a render pass declares an attachment that no subpass references, do the implementation's load and store operations leave that attachment's contents alone?

- This page covers the `renderpasses.<renderpass variant>.suballocation.unused_attachment` test family in [`vktRenderPassUnusedAttachmentTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp).
- The test family builds a two-subpass render pass with three attachments: a result color attachment, an attachment that no subpass references, and an input attachment. Each registered case varies the load and store operations applied to that unreferenced attachment.
- The core idea: clear the unused attachment to a known sentinel color before the render pass, run the render pass, then read the unused attachment back and confirm no load or store operation touched it.
- The same logic runs under three rendering variants, legacy render pass (`renderpass1`), render pass 2 (`renderpass2`), and dynamic rendering (`dynamic_rendering`), with the last one applying a documented exception.

## Background Knowledge

- **Unused attachment.** A render pass attachment description is part of the render pass object, but a subpass references attachments through its color, input, depth/stencil, and resolve attachment reference lists. An attachment can be declared in the render pass yet appear in no subpass reference list. The Vulkan specification states that for such an attachment, `loadOp`, `storeOp`, `stencilLoadOp`, and `stencilStoreOp` are ignored and no load or store operations are performed, though the `initialLayout` to `finalLayout` transition still runs ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)).
- **Load and store operations.** `loadOp` defines how attachment contents are initialized at the start of a render pass instance: `VK_ATTACHMENT_LOAD_OP_LOAD` preserves previous contents, `VK_ATTACHMENT_LOAD_OP_CLEAR` fills the render area with a clear value, and `VK_ATTACHMENT_LOAD_OP_DONT_CARE` makes contents undefined. `storeOp` defines how values written during the render pass are stored to memory at the end: `VK_ATTACHMENT_STORE_OP_STORE` writes them back, `VK_ATTACHMENT_STORE_OP_DONT_CARE` makes them undefined. For color formats, `loadOp` and `storeOp` apply directly; `stencilLoadOp` and `stencilStoreOp` are separate stencil counterparts relevant for depth/stencil formats.
- **Dynamic rendering exception.** Dynamic rendering (`vkCmdBeginRendering`) has no render pass object that statically associates attachments with subpasses. The implementation performs load and store operations for all specified color attachments because it cannot know which ones will be left unused. This test documents and checks that exception.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.unused_attachment
├── loadopclear
├── loadopdontcare
└── loadopload
```

The tree uses the `renderpass1` variant as one concrete parseable hierarchy. The same `unused_attachment` test family also appears under `renderpass2.suballocation` and under each `dynamic_rendering.*.suballocation` path. The test family is created by [`createRenderPassUnusedAttachmentTests()`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1219-L1289) and attached under `suballocation` for every supported rendering variant.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Load op | `VK_ATTACHMENT_LOAD_OP_LOAD`, `VK_ATTACHMENT_LOAD_OP_CLEAR`, `VK_ATTACHMENT_LOAD_OP_DONT_CARE` | Applied to the unused attachment. The specification requires these to be ignored for an unreferenced attachment, so the test verifies contents are unchanged regardless of this value. | [`loadOps` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1225-L1226) |
| Store op | `VK_ATTACHMENT_STORE_OP_STORE`, `VK_ATTACHMENT_STORE_OP_DONT_CARE` | Applied to the unused attachment. Like the load op, these must be ignored for an unreferenced attachment. | [`storeOps` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1228) |
| Stencil load op | `VK_ATTACHMENT_LOAD_OP_LOAD`, `VK_ATTACHMENT_LOAD_OP_CLEAR`, `VK_ATTACHMENT_LOAD_OP_DONT_CARE` | Applied to the unused attachment's stencil component. The attachment uses a color format, so stencil ops are not meaningful for device execution but are still exercised to confirm they do not corrupt the color attachment. | [`loadOps` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1225-L1226) |
| Stencil store op | `VK_ATTACHMENT_STORE_OP_STORE`, `VK_ATTACHMENT_STORE_OP_DONT_CARE` | Applied to the unused attachment's stencil component, with the same rationale as the stencil load op. | [`storeOps` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1228) |

## Behavior Parameters

The primary behavioral axis is the load operation applied to the unused attachment, which forms the three direct child groups under the test family. Each child group then nests store-op, stencil-load-op, and stencil-store-op intermediate nodes to produce the full registered matrix.

### `loadopclear`: unused attachment with `VK_ATTACHMENT_LOAD_OP_CLEAR`

This group sets the unused attachment's load operation to `VK_ATTACHMENT_LOAD_OP_CLEAR`. For a render pass object, the clear must be ignored because no subpass references the attachment, so the pre-initialized sentinel color must survive intact. For dynamic rendering, the clear runs on all specified color attachments regardless of subpass reference, so the test adjusts its expected value for that path (see [Runtime Execution and Result Checking](#runtime-execution-and-result-checking)).

### `loadopdontcare`: unused attachment with `VK_ATTACHMENT_LOAD_OP_DONT_CARE`

This group sets the unused attachment's load operation to `VK_ATTACHMENT_LOAD_OP_DONT_CARE`. Because the attachment is unreferenced and the load op is ignored, the pre-initialized sentinel must remain unchanged. This group is not registered for the dynamic rendering variant, where `DONT_CARE` load and store operations are skipped entirely.

### `loadopload`: unused attachment with `VK_ATTACHMENT_LOAD_OP_LOAD`

This group sets the unused attachment's load operation to `VK_ATTACHMENT_LOAD_OP_LOAD`. The load is ignored for an unreferenced render pass attachment, so the pre-initialized sentinel must survive. For dynamic rendering, the load preserves the attachment's previous contents, the same sentinel value, so the expected result is consistent across rendering variants.

## Shader Analysis

The shaders are simple vertex/fragment passthrough that write a fixed color to the result attachment. They are not part of the tested behavior, the test checks attachment load/store handling, not shader correctness. The two fragment shaders:

- Subpass 0 fragment shader ([`color_frag_sb0`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L392-L399)) outputs the interpolated vertex color directly.
- Subpass 1 fragment shader ([`color_frag_sb1`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L401-L409)) loads the input attachment and adds the vertex color.

No representative shader walkthrough is needed because shader code does not interact with the unused attachment.

## Runtime Execution and Result Checking

The test instance creates three `R8G8B8A8_UNORM` images and records a two-subpass render pass. The key host-side steps:

- **Unused image pre-initialization.** Before the render pass, the unused image is transitioned to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and cleared with `vkCmdClearColorImage` to the sentinel color `(0.1, 0.2, 0.3, 0.4)`, then transitioned to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` ([clear setup](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L493-L566)).
- **Render pass structure.** The render pass declares three attachments: the result attachment (attachment 0), the unused attachment (attachment 1), and the input attachment (attachment 2). Subpass 0 renders a quad to the input attachment. Subpass 1 reads the input attachment and renders the sum of input and vertex color to the result attachment. The unused attachment is never referenced by any subpass ([attachment descriptions](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L107-L143), [subpass descriptions](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L167-L193)).
- **Rendering.** Subpass 0 draws a quad with vertex color `(0.2, 0.3, 0.1, 1.0)`, producing `(0.2, 0.3, 0.1, 1.0)` on the input attachment. Subpass 1 loads that input and adds the same vertex color, producing `(0.4, 0.6, 0.2, 1.0)` at the center of the result attachment ([`drawFirstSubpass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1103-L1109), [`drawSecondSubpass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1111-L1119)).
- **Result verification.** After the render pass completes, the host reads back both the result image and the unused image. It checks every pixel of the unused image against a reference color with a tolerance of `0.01`, and checks the center pixel of the result image against `(0.4, 0.6, 0.2, 1.0)` with the same tolerance ([`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1132-L1185)).
- **Dynamic rendering exception.** When the rendering variant is dynamic rendering, the load operation is `VK_ATTACHMENT_LOAD_OP_CLEAR`, and the store operation is `VK_ATTACHMENT_STORE_OP_STORE`, the expected reference color for the unused image becomes `(0.5, 0.5, 0.5, 1.0)`. This is the clear value supplied at `vkCmdBeginRendering`, and dynamic rendering applies it to all specified color attachments because it cannot determine which are unused ([exception logic](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1163-L1169)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Result image | Yes | Framebuffer attachment 0 | Written by subpass 1 | Yes | Validates that normal rendering works correctly alongside the unused attachment. |
| Unused image | Yes | Framebuffer attachment 1 | Never read or written by any subpass | Yes | The core oracle: its contents must match the pre-initialized sentinel. |
| Input attachment image | Yes | Framebuffer attachment 2 | Written by subpass 0, read by subpass 1 | No | Carries the subpass 0 output into subpass 1 via `subpassLoad`. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `loadopclear` | The unused attachment was cleared when it should have been ignored (render pass object path), or was not cleared when dynamic rendering expected it. |
| `loadopdontcare` | The unused attachment contents were modified despite `DONT_CARE` being ignored for an unreferenced attachment. |
| `loadopload` | The unused attachment contents were corrupted despite the load operation being ignored. |
| Any group (common cause) | The result image center pixel is wrong, indicating a separate rendering or input-attachment pipeline failure unrelated to unused-attachment handling. |

### Cause Analysis

#### Unused attachment load/store operations not ignored

**Possible failure symptoms:** The host readback of the unused image shows pixels that differ from the expected reference color `(0.1, 0.2, 0.3, 0.4)` (or `(0.5, 0.5, 0.5, 1.0)` for the dynamic rendering clear exception) by more than the `0.01` tolerance ([`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1132-L1185)).

**Possible implementation causes:** For a render pass object, the Vulkan specification requires that an attachment not used by any subpass has its `loadOp`, `storeOp`, `stencilLoadOp`, and `stencilStoreOp` ignored ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)). A failure in the render pass object variants (`renderpass1`, `renderpass2`) suggests the driver applied a load or store operation to an unreferenced attachment when it should not have. A failure in the dynamic rendering variant with `LOAD_OP_CLEAR` and `STORE_OP_STORE` where the unused image does not match `(0.5, 0.5, 0.5, 1.0)` suggests the implementation failed to apply the clear it must perform for all color attachments in dynamic rendering. The layout transition from `initialLayout` to `finalLayout` still runs for an unused attachment and could also change contents on some implementations.

#### Result image mismatch

**Possible failure symptoms:** The center pixel of the result image does not match `(0.4, 0.6, 0.2, 1.0)` within the `0.01` tolerance ([result check](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1179-L1182)).

**Possible implementation causes:** This is independent of unused-attachment handling. The two-subpass pipeline draws a quad, feeds the output through an input attachment into a second subpass, and sums the colors. A mismatch can come from rasterization, input-attachment descriptor binding, `subpassLoad`, or the subpass dependency between subpass 0 and subpass 1. Source-level investigation is needed to isolate which stage produced the wrong result.

## Case Pruning

### Requirement-based pruning

- `renderpass2` requires the `VK_KHR_create_renderpass2` extension ([`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L371-L372)).
- `dynamic_rendering` requires the `VK_KHR_dynamic_rendering_local_read` extension ([`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L373-L374)).
- All variants call the pipeline construction requirement checker for their selected construction type ([`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L369-L370)).

### Design-based pruning

- The dynamic rendering variant skips all `LOAD_OP_DONT_CARE` and `STORE_OP_DONT_CARE` cases. In dynamic rendering, load and store operations are not affected by attachment remapping, so `DONT_CARE` permits the implementation to initialize or store arbitrary data to the unused attachment, particularly on tiling GPUs. These cases are therefore not testable and are excluded from registration ([pruning logic](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1246-L1254)).
- The dynamic rendering variant fixes the stencil load and store operations to `VK_ATTACHMENT_LOAD_OP_DONT_CARE` and `VK_ATTACHMENT_STORE_OP_DONT_CARE`, since the attachment uses a color format and stencil operations are not meaningful in that path ([stencil start index](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1230-L1237)).

## Key Takeaways

- The test proves that a render pass attachment not referenced by any subpass must have its load and store operations ignored, leaving the pre-initialized contents intact.
- The sentinel color `(0.1, 0.2, 0.3, 0.4)` distinguishes a preserved attachment from one that was cleared, loaded, or corrupted, because it differs from every clear value the render pass uses.
- Dynamic rendering is the documented exception: because `vkCmdBeginRendering` cannot know which color attachments will be unused, it applies load and store operations to all of them, and the test adjusts its expected value for the `LOAD_OP_CLEAR` + `STORE_OP_STORE` case.
- The `DONT_CARE` load and store cases are absent from dynamic rendering because they are not testable on tiling GPUs.
- See [Failure Meaning](#failure-meaning) for the distinction between unused-attachment corruption and an unrelated result-image pipeline failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [`createRenderPassUnusedAttachmentTests`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1219-L1289) | Creates the `unused_attachment` group and generates the load-op, store-op, and stencil-op matrix. |
| Render pass construction | [`createRenderPass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L103-L220) | Declares the three attachments and two subpasses, with attachment 1 never referenced. |
| Unused image pre-initialization | [clear setup](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L493-L566) | Clears the unused image to the sentinel color before the render pass. |
| Shader generation | [`initPrograms`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L377-L410) | Emits the vertex shader and two fragment shaders for the two subpasses. |
| Result verification | [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1132-L1185) | Reads back both images and applies the dynamic rendering clear exception. |
| Support checks | [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L367-L375) | Requires `VK_KHR_create_renderpass2` or `VK_KHR_dynamic_rendering_local_read` per variant. |
| Attachment under `suballocation` | [`vktRenderPassTests.cpp#L8561`](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8561) | Attaches the test family below the `suballocation` group for every rendering variant. |
| Vulkan spec: unused attachments | [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc) | States that load/store ops are ignored for attachments not used by any subpass. |
