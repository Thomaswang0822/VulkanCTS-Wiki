## Overview

**Core question:** Can an implementation correctly execute a render pass that mixes inline draw commands and `vkCmdExecuteCommands` calls inside one subpass, when `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS` is advertised through `VK_EXT_nested_command_buffer` or `VK_KHR_maintenance7`?

- This page covers the `renderpasses.renderpass1.nested_command_buffers` test family implemented in [vktRenderPassNestedCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp).
- The test family registers two test case leaves under each of two extension subtrees, `ext` and `khr`, for eight cases total. The leaves vary whether the boundary inline draws at the start and end of a fixed inline/secondary sequence come before or after their neighboring secondary command buffer executions ([registration](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L667-L714)).
- The core property under test is that when a subpass is begun with `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS`, the implementation honors inline draws and secondary execution in any order within that one subpass, so the final per-region color of the attachment matches what strict command order predicts.
- The reader should expect an explanation of why this subpass contents value is non-trivial, what the test draws, and how a wrong per-region color localizes the failure.

## Background Knowledge

- **`VK_SUBPASS_CONTENTS` values inside a render pass.** Core Vulkan offers two contents values when a subpass begins: `INLINE`, meaning all commands are recorded directly into the primary command buffer, and `SECONDARY_COMMAND_BUFFERS`, meaning only `vkCmdExecuteCommands` is legal and inline recording is forbidden. Mixing the two in the same subpass is not allowed with either value.
- **`VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS`.** Introduced by `VK_EXT_nested_command_buffer` and promoted to KHR by `VK_KHR_maintenance7`, this contents value lets a subpass record commands both inline and through `vkCmdExecuteCommands`. The test exists to exercise exactly this mixed mode; without it, the inline-or-secondary split of core Vulkan would make the test's command sequence invalid.
- **Secondary command buffers with render-pass continue.** A secondary command buffer recorded with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` inherits the render pass and framebuffer context from its `VkCommandBufferInheritanceInfo` and runs as if its commands were inlined at the `vkCmdExecuteCommands` call site. The test's secondary command buffers are all recorded with this bit, and the EXT subtree also requires the `nestedCommandBufferRendering` feature for that usage.

## Registration Hierarchy

```text
renderpasses.renderpass1.nested_command_buffers
├── ext
└── khr
```

The group is registered by the internal dispatcher in [vktRenderPassTests.cpp#L8571-L8592](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8592), and only when `useSecondaryCmdBuffer == false` inside the monolithic-pipeline block, so each leaf uses a primary command buffer with no CTS-level secondary-command-buffer wrapper. The factory group is created at [vktRenderPassNestedCommandBuffersTests.cpp#L667-L714](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L667-L714). The same eight leaves also appear under `renderpass2` and `dynamic_rendering.primary_cmd_buff`; the `renderpass1` root is shown as the representative subtree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Extension | `ext`, `khr` | Selects the feature path that authorizes `INLINE_AND_SECONDARY_COMMAND_BUFFERS`. `ext` requires `VK_EXT_nested_command_buffer` with `nestedCommandBuffer` and `nestedCommandBufferRendering`; `khr` requires `VK_KHR_maintenance7` with `maintenance7`. | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L633-L663), [registration](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L672-L679) |
| First command location | `inline_secondary`, `secondary_inline` | The first-command intermediate node picks whether the opening inline draw comes before or after the first `vkCmdExecuteCommands`. | [registration](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L681-L688) |
| Last command location | `inline_secondary`, `secondary_inline` | The test case leaf picks whether the closing inline draw comes before or after the last `vkCmdExecuteCommands`. | [registration](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L698-L706) |
| Rendering type | `RENDERING_TYPE_RENDERPASS_LEGACY`, `RENDERING_TYPE_RENDERPASS2`, `RENDERING_TYPE_DYNAMIC_RENDERING` | Selected by the dispatcher, not by a registered path token. It controls which begin/end render pass API path is used and which extra extension (`VK_KHR_create_renderpass2` or `VK_KHR_dynamic_rendering`) is required. | [group params](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L137-L244), [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L635-L642) |

The full registered matrix is 2 extensions x 2 first-command x 2 last-command, for eight test case leaves per rendering-type subtree.

## Behavior Parameters

The primary behavioral axis is the pair of nesting-pattern dimensions (first command location and last command location). The extension dimension only gates feature availability; it does not change the recorded command sequence or the contents token. The same `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS_KHR` token is used for both the `ext` and `khr` paths, and the same draws run in the same order under both extensions.

### inline_secondary: boundary draw inline, neighbor secondary

The first-command intermediate node `inline_secondary` sets `beginInline = true`, so the opening inline draw (instance 1) is recorded before the first `vkCmdExecuteCommands` (secondary instance 0) ([L484-L488](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L484-L488)). The test case leaf of the same name sets `endInline = true`, so the closing inline draw (instance 5) is recorded after the last `vkCmdExecuteCommands` (secondary instance 4) ([L503-L508](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L503-L508)). This combination places the boundary inline draws outside their neighboring secondary executions.

### secondary_inline: boundary draw secondary-side, neighbor inline

The first-command intermediate node `secondary_inline` sets `beginInline = false`, so the first `vkCmdExecuteCommands` (secondary instance 0) runs before the opening inline draw (instance 1) ([L488-L493](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L488-L493)). The test case leaf of the same name sets `endInline = false`, so the closing inline draw (instance 5) is recorded before the last `vkCmdExecuteCommands` (secondary instance 4) ([L499-L503](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L499-L503)). This is the mirror of `inline_secondary` and confirms that the mixed mode is symmetric: whichever side starts or ends the sequence, the final per-region color must be identical.

### Cross product

Each of the two intermediate nodes carries both test case leaves, so the full matrix is `inline_secondary.inline_secondary`, `inline_secondary.secondary_inline`, `secondary_inline.inline_secondary`, and `secondary_inline.secondary_inline` per extension. The first token names the first-command location; the second names the last-command location. The middle of the sequence is a fixed alternation of inline draws and `vkCmdExecuteCommands` calls that does not vary across leaves ([L494-L497](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L494-L497)).

## Shader Analysis

The test uses one trivial vertex shader and one trivial fragment shader, both generated inline by `initPrograms` ([L604-L631](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L604-L631)). The shader is not part of the behavior under test. It only converts `gl_InstanceIndex` into a per-instance screen position and a per-instance color, so each of the draws paints a distinct colored quad whose final position is fully determined by the instance index. Because the shader does not contribute to the property under test, no SPIR-V walkthrough is included.

The vertex shader derives a unit-square corner from `gl_VertexIndex`, offsets it down by half a cell per `gl_InstanceIndex % 3` and left by one cell per `gl_InstanceIndex / 3`, and writes `gl_InstanceIndex + 1` to a flat output ([L609-L617](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L609-L617)). The fragment shader unpacks that index into red, green, and blue bits, giving each instance index a unique stable color ([L619-L627](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L619-L627)). The six colors used by the host-side checker match this encoding.

## Runtime Execution and Result Checking

The host creates one color attachment, records a single primary command buffer plus three secondary command buffers, runs the draw sequence inside one subpass, copies the attachment back, and compares every pixel to an expected color.

### Attachment and pipeline setup

- One 32 x 32 `VK_FORMAT_R8G8B8A8_UNORM` color image with `COLOR_ATTACHMENT_BIT | TRANSFER_SRC_BIT` usage, plus a matching image view and framebuffer (or dynamic-rendering attachment info) ([L104-L135](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L104-L135), [L137-L244](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L137-L244)).
- One graphics pipeline built monolithically with `TRIANGLE_STRIP` topology, no vertex input, and the trivial vertex and fragment shaders ([L414-L427](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L414-L427)).
- One host-visible readback buffer sized for the full 32 x 32 attachment ([L429-L432](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L429-L432)).

### Secondary command buffer recording

Three secondary command buffers are recorded, each with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` and an inheritance info that matches the active rendering type. Secondary `i` binds the pipeline and draws 4 vertices with `firstInstance = i * 2`, so it paints the quad for instance index `i * 2` ([L434-L478](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L434-L478)). The three secondaries therefore paint instance indices 0, 2, and 4.

### The draw sequence

Inside the single subpass, the primary command buffer records a fixed backbone plus two flag-gated boundary draws ([L480-L510](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L480-L510)). The backbone is the same in every leaf:

1. `vkCmdExecuteCommands(secondaries[0])` paints instance 0.
2. Inline draw paints instance 3.
3. `vkCmdExecuteCommands(secondaries[1])` paints instance 2.
4. Inline draw paints instance 3 again (same region, same color).

Around this backbone, two boundary inline draws are placed by the flags:

- The opening inline draw (instance 1) is recorded before step 1 when `beginInline` is true, and after step 1 when `beginInline` is false.
- The closing inline draw (instance 5) is recorded after `vkCmdExecuteCommands(secondaries[2])` (instance 4) when `endInline` is true, and before it when `endInline` is false.

Per leaf, seven operations execute: four inline draws and three `vkCmdExecuteCommands` calls. They paint six distinct colored quads (instances 0 through 5); instance 3 is painted twice in its own region. The four middle operations are identical across all leaves. Only the relative order of each boundary inline draw and its adjacent secondary execution changes, and that order is what determines which color wins in the regions where the boundary quads overlap their neighbors.

### Result checking

After `endRenderPass`, the host inserts a layout barrier and copies the attachment into the readback buffer ([L349-L355](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L349-L355), [L511-L522](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L511-L522)). It then walks all 32 x 32 pixels and compares each to an expected color derived from the pixel's region and the two `beginInline` / `endInline` flags ([L529-L582](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L529-L582)). The expected colors are the six host-side constants `blue, green, cyan, red, magenta, yellow` ([L529-L532](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L529-L532)). The comparison is exact: any single mismatched pixel fails the test.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Color image | Yes | Color attachment in the render pass | Written by the draw sequence | Yes, via `cmdCopyImageToBuffer` | Single 32 x 32 target whose per-region color encodes the submission order. |
| Secondary command buffers (x3) | Yes | Executed by `vkCmdExecuteCommands` | Bind pipeline and draw once each | No | Provide the secondary half of the mixed inline/secondary sequence. |
| Primary command buffer | Yes | Submitted to the universal queue | Begins and ends the render pass and records the inline draws | No | Owns the single subpass and the `INLINE_AND_SECONDARY_COMMAND_BUFFERS` contents value. |
| Readback buffer | Yes | Transfer destination | Written by `cmdCopyImageToBuffer` | Yes, host-visible | Lets the host scan every pixel of the attachment. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any `ext` leaf (`inline_secondary.*` or `secondary_inline.*`) | Mixed inline/secondary execution under `VK_EXT_nested_command_buffer`, or the shared render and draw machinery. |
| Any `khr` leaf (`inline_secondary.*` or `secondary_inline.*`) | Mixed inline/secondary execution under `VK_KHR_maintenance7`, or the shared render and draw machinery. |
| `inline_secondary` first-command node versus `secondary_inline` first-command node (same extension, same leaf) | Asymmetric handling of the boundary draw: the implementation treats an inline first draw differently from a secondary first draw, or vice versa. |
| `inline_secondary` leaf versus `secondary_inline` leaf (same extension, same first-command node) | Asymmetric handling of the closing draw, same mechanism as above but at the end of the sequence. |

All leaves share the same attachment, pipeline, and draw sequence. A failure that hits every leaf of both extensions points at the shared render or draw machinery rather than at the extension-specific contents token.

### Cause Analysis

#### Mixed inline/secondary execution under `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS`

**Possible failure symptoms:** One or more pixels do not match the expected color for their region ([L534-L580](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L534-L580)). The mismatch typically appears as the wrong instance color in a region where two quads overlap, because the boundary draw is the one whose location (inline versus secondary) changes between leaves and therefore changes which color lands on top.

**Possible implementation causes:** The contents value `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS` is only legal when the corresponding feature is enabled ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L633-L663)). An implementation that accepts the begin-render-pass call but does not actually interleave inline recording with `vkCmdExecuteCommands` could drop, reorder, or double-execute one of the boundary draws, shifting the per-region color. The EXT path additionally requires `nestedCommandBufferRendering` for the secondary command buffers that use `RENDER_PASS_CONTINUE_BIT` ([L648-L653](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L648-L653)); if that feature is reported but not honored, the secondary draws can be skipped or misrouted.

#### Asymmetric handling of the boundary draw

**Possible failure symptoms:** Only one half of a mirrored pair fails. For example, `inline_secondary.inline_secondary` fails while `secondary_inline.inline_secondary` passes, even though both leaves paint the same six quads and differ only in whether the opening draw is inline or secondary.

**Possible implementation causes:** The middle of the sequence is identical across leaves, so an isolated failure of one leaf in a mirrored pair localizes the defect to the boundary draw that differs. If the implementation executes a secondary command buffer at the wrong point relative to surrounding inline draws, the quad for the boundary instance lands in the wrong region and the per-pixel check fails. Source-level investigation would be needed to pin whether the defect is in inline-to-secondary or secondary-to-inline transition handling.

#### Shared render and draw machinery

**Possible failure symptoms:** All eight leaves, across both extensions and all rendering types, fail with the same wrong per-region color pattern.

**Possible implementation causes:** A defect this broad would not be specific to the contents token. It would point at the common path: the render pass or dynamic-rendering begin/end, the monolithic pipeline, the trivial vertex and fragment shaders, or the `cmdCopyImageToBuffer` readback. Because every leaf shares that path, a single breakage there surfaces uniformly. The test's shader and geometry are deliberately simple, so a uniform failure should be traced through those common pieces first.

## Case Pruning

### Requirement-based pruning

- The `ext` subtree requires `VK_EXT_nested_command_buffer` with both the `nestedCommandBuffer` and `nestedCommandBufferRendering` features enabled; if either is missing, `checkSupport` throws `NotSupportedError` and the leaves are skipped ([L644-L653](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L644-L653)).
- The `khr` subtree requires `VK_KHR_maintenance7` with the `maintenance7` feature enabled; if missing, `checkSupport` throws `NotSupportedError` ([L657-L661](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L657-L661)).
- The `renderpass2` rendering type requires `VK_KHR_create_renderpass2`, and the `dynamic_rendering` rendering type requires `VK_KHR_dynamic_rendering` ([L635-L642](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L635-L642)).
- The whole group is compiled out for Vulkan SC through the `CTS_USES_VULKANSC` guard in the dispatcher ([vktRenderPassTests.cpp#L8579-L8592](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8579-L8592)).
- The group is registered only for the monolithic pipeline construction type and only when `useSecondaryCmdBuffer == false`, so no graphics-pipeline-library or CTS-secondary-command-buffer variants exist ([vktRenderPassTests.cpp#L8571-L8592](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8592)).

### Design-based pruning

- There is no generated parameter matrix beyond the 2 x 2 x 2 extension, first-command, last-command cross product. The rendering type is a dispatcher-selected dimension, not a registered path token.
- The middle of the draw sequence is fixed by design. Only the boundary draws vary between leaves, because those are the positions where the inline-versus-secondary choice is meaningful for exercising the mixed contents value.
- The shader, geometry, attachment format, and image size are fixed. They are not exposed as separate test cases because they are not part of the behavior under test.

## Key Takeaways

- The test exercises `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS`, the only core-forbidden contents value that permits mixing inline draws and `vkCmdExecuteCommands` inside one subpass.
- Both `VK_EXT_nested_command_buffer` and `VK_KHR_maintenance7` advertise this contents value; the test runs the identical command sequence under each so a defect can be attributed to one promotion path or the other, or to the shared machinery.
- The draw sequence is identical in every leaf except for the placement of its boundary inline draws relative to their neighboring secondary executions. A failure that changes only when a boundary draw moves localizes the defect to inline-to-secondary or secondary-to-inline transition handling.
- The per-pixel check is exact and region-based, so any dropped, reordered, or duplicated draw surfaces as a wrong color in the region that draw should have painted. See `## Failure Meaning` for the interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and extension enum | [TestParams, Extension](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L51-L63) | Defines the `ext` / `khr` choice and the two boundary-draw flags `beginInline`, `endInline`. |
| Attachment and framebuffer setup | [createRenderPass()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L98-L245) | Creates the color image, view, render pass (legacy, renderpass2, or dynamic-rendering), and framebuffer. |
| Render pass begin with mixed contents | [beginRenderPass()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L247-L325) | Begins the subpass with `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS` for all three rendering types. |
| Render pass end and readback barrier | [endRenderPass()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L327-L356) | Ends the subpass and transitions the attachment to `TRANSFER_SRC_OPTIMAL`. |
| Secondary command buffer recording | [iterate(), secondaries loop](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L434-L478) | Records the three secondary command buffers, one draw each, with `RENDER_PASS_CONTINUE_BIT`. |
| Draw sequence | [iterate(), primary recording](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L480-L510) | The flag-gated inline/secondary boundary draws that are the core of the test. |
| Pixel comparison | [iterate(), result check](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L529-L582) | Exact per-pixel comparison against region- and flag-dependent expected colors. |
| Shader registration | [initPrograms()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L604-L631) | Generates the trivial vertex and fragment shaders. |
| Feature checks | [checkSupport()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L633-L663) | Gates the `ext` and `khr` subtrees on their respective features and rendering-type extensions. |
| Test family registration | [createNestedCommandBufferTests()](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L667-L714) | Registers the `ext` and `khr` subtrees and the four leaves under each. |
| Dispatcher attachment | [vktRenderPassTests.cpp#L8571-L8592](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8592) | Attaches the group under `renderpass1`, `renderpass2`, and `dynamic_rendering.primary_cmd_buff`, monolithic only, no CTS secondary command buffer. |
