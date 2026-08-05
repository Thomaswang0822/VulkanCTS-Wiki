## Overview

**Core question:** Can an implementation correctly execute a render pass that has three subpasses over the same single color attachment when the subpasses are split across two primary command buffers, each with its own framebuffer and target image?

- This page covers the `renderpasses.renderpass1.multiple_subpasses_multiple_command_buffers` test family implemented in [vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp).
- The test family registers two test case leaves, `test` and `test_general_layout`, that differ only in the image layout assigned to the color attachment across all subpasses ([L906-L907](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L906-L907)).
- The test renders two independent color images through the same three-subpass render pass. One instance of the render pass lives entirely in command buffer A and writes image A; another lives entirely in command buffer B and writes image B. Both command buffers are submitted together in a single `vkQueueSubmit` call ([L826-L843](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L826-L843)).
- The core property under test is that the implementation can run the same multi-subpass render pass twice in parallel primary command buffers within one submit, respecting the subpass dependencies inside each command buffer, and produce two independently correct rendered images.

## Background Knowledge

- **Subpass dependencies inside a render pass.** A render pass can declare dependencies between its subpasses. A dependency between subpass 0 and subpass 1 means the work of subpass 1 must not start before the specified source stage and access writes of subpass 0 are made available. This is how the test orders color-attachment writes across its three subpasses without using external barriers.
- **Color attachment load and store.** The test uses `VK_ATTACHMENT_LOAD_OP_LOAD` on its single attachment. Each subpass reads what the previous subpass wrote to that attachment and then writes back to it. Because all three subpasses reference the same attachment, the final content depends on the order enforced by the subpass dependencies.
- **`VK_IMAGE_LAYOUT_GENERAL` versus `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`.** `COLOR_ATTACHMENT_OPTIMAL` is the layout tailored for color-attachment writes inside a render pass. `GENERAL` is the more permissive layout that also allows the image to stay usable for transfers and shader reads without extra transitions. The two test case leaves swap which of these two layouts the attachment uses across initial layout, subpass references, and final layout.

## Registration Hierarchy

```text
renderpasses.renderpass1.multiple_subpasses_multiple_command_buffers
├── test
└── test_general_layout
```

The test family is available under `renderpass1` only. It is registered into the legacy render-pass subtree by the internal dispatcher in [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8501) under the `RENDERING_TYPE_RENDERPASS_LEGACY` branch, and is compiled out for Vulkan SC. The factory group is created at [vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L901-L910](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L901-L910).

## Parameter Dimensions and Observed Values

This test family has a small fixed configuration. The only dimension that changes between the two test case leaves is the attachment image layout.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Attachment image layout | `COLOR_ATTACHMENT_OPTIMAL`, `GENERAL` | The two leaves select which layout the color attachment uses for its initial layout, all three subpass references, and the final layout. `test` uses `COLOR_ATTACHMENT_OPTIMAL`; `test_general_layout` uses `GENERAL`. | [createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L189-L264), [registration](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L906-L907) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT` | Fixed across both leaves. A floating-point format keeps the per-channel color comparison meaningful and avoids format-quantization noise. | [attachment description](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L195-L205) |
| Image size | 32 x 32 | Fixed. Small enough to keep the test fast, large enough to exercise tiled and per-subpass rendering paths. | [constants](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L104-L106) |
| Subpass count | 3 | Fixed. Each render pass instance advances through three subpasses that all reference the same single color attachment. | [subpass descriptions](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L214-L231) |
| Command buffer count | 2 (A and B), both primary | Fixed. Both command buffers are primary and are submitted in one `vkQueueSubmit`. | [createCommandBuffer](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L751-L752), [submit](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L826-L843) |

## Behavior Parameters

The primary behavioral axis is the attachment image layout, expressed as the two test case leaves. Both leaves run the same render-pass shape and the same two-command-buffer submission; only the layout assigned to the color attachment differs.

### test: color-attachment-optimal layout

The `test` leaf uses `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` for the attachment's initial layout, the three subpass attachment references, and the final layout ([L192](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L192)). This is the conventional, narrowly-scoped layout for a color attachment inside a render pass. It exercises the implementation's handling of the render pass using the layout that a normal application would choose.

### test_general_layout: general layout

The `test_general_layout` leaf uses `VK_IMAGE_LAYOUT_GENERAL` for the same attachment across the same three subpasses and for the initial and final layout ([L191-L192](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L191-L192)). `GENERAL` is the layout the spec allows for simultaneous color-attachment and other access. This leaf checks that the multi-subpass, multi-command-buffer behavior is also correct when the attachment stays in `GENERAL` rather than being constrained to `COLOR_ATTACHMENT_OPTIMAL`.

## Shader Analysis

The test uses a single vertex shader and a single fragment shader, both trivial passthrough shaders. The shader is not part of the behavior under test; it only paints the vertex color into the color attachment so that the per-subpass draw steps produce an observable, position-dependent result.

```glsl
// Vertex shader (reconstructed from initPrograms).
#version 450
layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 0) out vec4 vtxColor;
void main (void)
{
    gl_Position = position;
    vtxColor = color;
}
```

```glsl
// Fragment shader (reconstructed from initPrograms).
#version 450
layout(location = 0) in vec4 vtxColor;
layout(location = 0) out vec4 fragColor;
void main (void)
{
    fragColor = vtxColor;
}
```

The vertex shader copies `position` to `gl_Position` and passes `color` through as `vtxColor`. The fragment shader writes `vtxColor` to the color attachment unchanged. The actual color content comes from the host-defined vertex data and the per-subpass clear, not from any shader computation. The shader source is registered at [initPrograms](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L161-L186). Because the shader does not contribute to the property under test, no SPIR-V walkthrough is included.

## Runtime Execution and Result Checking

The host sets up two independent color images, builds two identical render-pass pipelines, records two primary command buffers, submits them together, and compares each image against an expected reference.

### Render pass shape

- The render pass has one attachment description with `loadOp = LOAD`, `storeOp = STORE`, format `R32G32B32A32_SFLOAT`, and a layout chosen by the test leaf ([L195-L205](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L195-L205)).
- There are three subpass descriptions, identical except for their index. Each subpass binds the same single color attachment reference and uses the graphics pipeline bind point ([L214-L231](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L214-L231)).
- There are two subpass dependencies: one from subpass 0 to 1, and one from subpass 1 to 2. Both source from `COLOR_ATTACHMENT_OUTPUT` with `COLOR_ATTACHMENT_WRITE`, and both destination mask combines `COLOR_ATTACHMENT_READ | COLOR_ATTACHMENT_WRITE` ([L233-L249](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L233-L249)). These dependencies order the subpass writes so that each subpass reads the result of the previous one.

### Image setup

- The host creates two color images, A and B, with `OPTIMAL` tiling and `COLOR_ATTACHMENT_BIT | TRANSFER_SRC_BIT | TRANSFER_DST_BIT` usage ([L294-L323](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L294-L323)).
- Both images are cleared to `(0, 0, 0, 1)` before the render pass begins. The clear is done by transitioning each image to `TRANSFER_DST_OPTIMAL` (or `GENERAL`, for the `test_general_layout` leaf) and calling `cmdClearColorImage`, then transitioning to the render-pass initial layout ([L353-L497](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L353-L497)).

### Per-subpass drawing

Each command buffer independently begins its render pass, clears the attachment to white in subpass 0, then draws in subpasses 1 and 2 using different vertex ranges, and ends the render pass. The drawing pattern is the same for A and B; the color output differs because each command buffer draws from a different range of the shared vertex buffer.

- Both command buffers begin their render pass on subpass 0 and issue `cmdClearAttachments` with a clear color of `(1, 1, 1, 1)` white ([L781](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L781), [L785](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L785)). Neither command buffer draws in subpass 0; command buffer A additionally binds its vertex buffer at offset 0 here, which persists into subpass 1 ([L778-L791](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L778-L791)).
- Both command buffers advance to subpass 1. A draws the first 4 vertices (offset 0), producing red on the left half; B draws the next 4 vertices (offset 8), producing blue on the left half ([L788-L797](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L788-L797)).
- Both command buffers advance to subpass 2. A draws 4 vertices starting at vertex 4, producing green on the right half; B draws 4 vertices starting at vertex 4, producing yellow on the right half ([L799-L808](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L799-L808)).
- Both command buffers end their render pass and are finished recording ([L808-L811](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L808-L811)).

### Submission and checking

- The host builds a single `VkSubmitInfo` that contains both primary command buffers, submits it to the universal queue, and waits on a fence ([L825-L843](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L825-L843)).
- After the submit completes, the host reads both color images back into host memory at the render-pass attachment layout using `pipeline::readColorAttachment` ([L856-L861](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L856-L861)).
- The host builds two reference images: image A is expected to be red on the left half and green on the right half; image B is expected to be blue on the left half and yellow on the right half ([L848-L889](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L848-L889)).
- Each image is compared with `tcu::floatThresholdCompare` against its reference, using a per-channel threshold of `tcu::Vec4(0.02f)` ([L879-L894](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L879-L894)). The test fails if either image does not match its reference within tolerance.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Color image A | Yes | Color attachment in framebuffer A | Written by subpasses in command buffer A | Yes, via `readColorAttachment` | Target image for the command-buffer-A render-pass instance; expected red-left, green-right. |
| Color image B | Yes | Color attachment in framebuffer B | Written by subpasses in command buffer B | Yes, via `readColorAttachment` | Target image for the command-buffer-B render-pass instance; expected blue-left, yellow-right. |
| Vertex buffer | Yes | Vertex buffer binding in command buffer A | Read by vertex shader | No | Provides position and color pairs for the per-subpass draws. |
| Framebuffer A | Yes | Backs command buffer A's render pass | Attachment backing for image A | No | Binds image view A to the render pass. |
| Framebuffer B | Yes | Backs command buffer B's render pass | Attachment backing for image B | No | Binds image view B to the render pass. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `test` | Multi-subpass render-pass execution or subpass-dependency ordering across two primary command buffers, using `COLOR_ATTACHMENT_OPTIMAL`. |
| `test_general_layout` | Multi-subpass render-pass execution or subpass-dependency ordering across two primary command buffers, using `GENERAL`, including image-layout handling for a `GENERAL` attachment inside a render pass. |

Both leaves share the same two-command-buffer submission and the same three-subpass render pass. A failure in either leaf points to the same render-pass or submission machinery; the difference is which attachment layout was in use when the failure occurred.

### Cause Analysis

#### Multi-subpass render-pass execution or subpass-dependency ordering across two primary command buffers

**Possible failure symptoms:** `tcu::floatThresholdCompare` fails for image A, image B, or both. The rendered image does not match its reference: a half is the wrong color, the clear color leaks through where a draw should have written, or a later subpass's draw result is missing because an earlier subpass's content was not preserved into the next subpass ([L879-L894](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L879-L894)).

**Possible implementation causes:** The render pass declares two subpass dependencies that order `COLOR_ATTACHMENT_OUTPUT` writes between consecutive subpasses ([L233-L249](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L233-L249)). A driver that does not enforce those dependencies, or that schedules subpass work out of order, could let a later subpass read stale attachment content or overwrite an earlier subpass's result. The test also relies on the implementation accepting and correctly executing two primary command buffers, each of which independently begins, advances, and ends the same multi-subpass render pass, within a single `vkQueueSubmit`. If the implementation does not handle this split cleanly, one or both images can come out wrong.

#### Image-layout handling for a `GENERAL` attachment inside a render pass

**Possible failure symptoms:** Only the `test_general_layout` leaf fails. The rendered image does not match the reference even though the `test` leaf passes with the same render-pass shape and submission.

**Possible implementation causes:** This leaf sets the attachment's initial layout, all three subpass references, and the final layout to `VK_IMAGE_LAYOUT_GENERAL` instead of `COLOR_ATTACHMENT_OPTIMAL` ([L191-L204](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L191-L204)). A driver that handles the optimal layout correctly but mishandles `GENERAL` for an attachment used across three subpasses, for the pre-render-pass `cmdClearColorImage` and layout transition, or for the post-render-pass `readColorAttachment` readback, could produce a mismatch. Source-level investigation would be needed to pin the exact stage if this leaf fails in isolation.

## Case Pruning

### Requirement-based pruning

- The test family is available under `renderpass1` only and is compiled out for Vulkan SC through the `CTS_USES_VULKANSC` guard in the dispatcher ([vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8501)).
- No device feature or extension beyond base Vulkan is required. The test uses only core render-pass and color-attachment functionality.

### Design-based pruning

- There is no generated parameter matrix. The test family registers exactly two test case leaves, `test` and `test_general_layout`, covering the two attachment layouts that matter for this render-pass shape ([L906-L907](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L906-L907)).
- The subpass count, image size, format, vertex data, and command-buffer split are fixed by design. They are not exposed as separate test cases.

## Key Takeaways

- The test checks that a three-subpass render pass over one color attachment works correctly when split across two primary command buffers that are submitted together in one `vkQueueSubmit`.
- Each command buffer owns its own framebuffer and target image and runs a complete instance of the same render pass, so the two images are independent and checked separately.
- The two test case leaves differ only in whether the attachment uses `COLOR_ATTACHMENT_OPTIMAL` or `GENERAL` across the whole render pass; everything else is identical.
- A failure means the implementation did not order the subpass work correctly, or did not handle the attachment layout used by the failing leaf. See `## Failure Meaning` for the failure interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Vertex data generation | [genVertices()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L60-L89) | Defines the red, green, blue, and yellow quad vertex pairs used by the per-subpass draws. |
| Shader registration | [initPrograms()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L161-L186) | Registers the passthrough vertex and fragment shaders. |
| Render pass creation | [createRenderPass()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L189-L264) | Builds the one-attachment, three-subpass render pass with two subpass dependencies, using the layout selected by the test leaf. |
| Image and framebuffer setup | [constructor](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L266-L538) | Creates images A and B, clears them, creates framebuffers A and B, and creates the pipeline layout. |
| Pipeline creation | [constructor](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L631-L720) | Creates three graphics pipelines, one per subpass, all sharing the same vertex and fragment shaders. |
| Command buffer recording | [createCommandBuffer()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L729-L812) | Records the two primary command buffers, each beginning, advancing, and ending the render pass. |
| Submission and result checking | [iterate()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L814-L898) | Submits both command buffers, reads both images back, and compares each against its reference with `tcu::floatThresholdCompare`. |
| Test family registration | [createRenderPassMultipleSubpassesMultipleCommandBuffersTests()](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L901-L910) | Registers the `test` and `test_general_layout` test case leaves under `renderpass1`. |
| Dispatcher attachment | [vktRenderPassTests.cpp#L8501](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8501) | Attaches the test family under `renderpass1` via the legacy render-pass branch. |
| Mustpass entry | [vk-main-2026-03-01/renderpasses.txt](../../../../../android/cts/main/vk-main-2026-03-01/renderpasses.txt) | Shows the `test_general_layout` leaf in the current main mustpass set. |
