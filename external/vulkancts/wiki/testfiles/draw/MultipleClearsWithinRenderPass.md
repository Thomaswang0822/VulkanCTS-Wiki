## Overview

**Core question:** Do ordered load, draw, and clear operations preserve the expected color and depth attachment values within one render pass?

`draw.renderpass.multiple_clears_within_render_pass` checks that a color attachment, depth attachment, or color/depth pair keeps the value established by a sequence of render-pass load, draw, and `vkCmdClearAttachments` operations. Every case records the sequence in one render pass and validates the complete 400 × 300 result image.

The implementation is `MultipleClearsWithinRenderPassTests`, a `TestCaseGroup` whose literal group name is `multiple_clears_within_render_pass` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L818-L823)). The legacy page is retained as historical material; this page is the normalized replacement.

## Background Knowledge

A render-pass load operation initializes an attachment at the start of a render pass. `vkCmdClearAttachments` changes attachment contents during the pass, while a draw writes fragments subject to blending and depth testing.

## Registration Hierarchy

The parent draw hierarchy is:

```text
draw.renderpass.multiple_clears_within_render_pass
```

The group adds six families for each format/topology suffix ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L829-L949)). They are presented in prose rather than as tree children because each generated registration leaf includes further format and topology suffixes:

| Family | Exact child prefix | Steps | Blend |
|---|---|---|---|
| Load, clear, draw | `load_clear_draw` | `LOAD → CLEAR → DRAW` | enabled |
| Draw, clear, draw | `draw_clear_draw` | `DRAW → CLEAR → DRAW` | enabled |
| Clear, clear, draw | `clear_clear_draw` | `CLEAR → CLEAR → DRAW` | enabled |
| Load, clear | `load_clear` | `LOAD → CLEAR` | disabled |
| Draw, clear | `draw_clear` | `DRAW → CLEAR` | disabled |
| Clear, clear | `clear_clear` | `CLEAR → CLEAR` | disabled |

A generated leaf is a family prefix followed by a format suffix and topology suffix. For example, the source creates `load_clear_draw_c_r8g8b8a8_unorm_d_d16_unorm_triangle_strip`, `draw_clear_c_r8g8b8a8_snorm_big_triangle`, and `clear_clear_d_d32_sfloat_triangles`. The topology suffixes are exactly `_triangle_strip`, `_triangles`, and `_big_triangle`; the format set is eight pairs: color-only `R8G8B8A8_UNORM` and `R8G8B8A8_SNORM`, depth-only `D32_SFLOAT` and `D16_UNORM`, and all four color/depth combinations ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L67-L87), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L120-L125)).

The standard mustpass materializes the group under `dEQP-VK.draw.renderpass.multiple_clears_within_render_pass`; dynamic-rendering primary, partial-secondary, and complete-secondary scopes are also listed in `external/vulkancts/mustpass/main/vk-default/draw.txt`. VulkanSC lists the render-pass group under `dEQP-VKSC.draw.renderpass.multiple_clears_within_render_pass` in `external/vulkancts/mustpass/main/vksc-default/draw.txt`.

For secondary-command-buffer configurations, initialization deliberately keeps only `TRIANGLE_STRIP` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L838-L844)). The mustpass scopes determine which shared draw configuration reaches the group.

## Parameter Dimensions and Observed Values

The test uses a 400 × 300 single-sample image. Color formats are `VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R8G8B8A8_SNORM`; depth formats are `VK_FORMAT_D32_SFLOAT` and `VK_FORMAT_D16_UNORM`; `VK_FORMAT_UNDEFINED` means that attachment is absent ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L64-L87)). Color and depth images also have transfer-source and transfer-destination usage so the result can be read back ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L221-L247)).

The pipeline uses a position-only vertex shader, a fragment shader that writes a push-constant color, and a depth-only fragment shader when there is no color attachment ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L720-L770)). The three-step families enable source-alpha blending with `SRC_ALPHA` and `ONE_MINUS_SRC_ALPHA`; two-step families disable blending ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L336-L345), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L846-L949)).

The vertex data covers the framebuffer with one triangle strip, two triangles, or an oversized “big triangle.” Each step has its own copied vertex block, with the step depth written into the vertex z coordinate ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L89-L125), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L196-L219)).

## Behavior Parameters

All cases run once (`repeatCount = 1`). The configured values are:

| Family | Initial/load or first operation | Clear operation | Draw operation | Expected color | Expected depth |
|---|---|---|---|---|---|
| `load_clear_draw` | load red `(1,0,0,1)`, depth `0.7` | green `(0,1,0,1)`, depth `0.3` | blue `(0,0,1,0.5)`, depth `0.9` | `(0,0.5,0.5,1)` | `0.9` |
| `draw_clear_draw` | draw red, depth `0.7` | green, depth `0.3` | blue with alpha `0.5`, depth `0.9` | `(0,0.5,0.5,1)` | `0.9` |
| `clear_clear_draw` | clear red, depth `0.7` | clear green, depth `0.3` | blue with alpha `0.5`, depth `0.9` | `(0,0.5,0.5,1)` | `0.9` |
| `load_clear` | load red, depth `0.3` | green, depth `0.9` | none | `(0,1,0,1)` | `0.9` |
| `draw_clear` | draw red, depth `0.3` | green, depth `0.9` | none | `(0,1,0,1)` | `0.9` |
| `clear_clear` | clear red, depth `0.3` | clear green, depth `0.9` | none | `(0,1,0,1)` | `0.9` |

The first `LOAD` is implemented as the render-pass attachment load operation (and as `VK_ATTACHMENT_LOAD_OP_LOAD` for dynamic rendering); later `CLEAR` steps call `vkCmdClearAttachments`, and `DRAW` steps push the step color then issue `vkCmdDraw` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L390-L400), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L402-L470), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L504-L559)).

## Shader Analysis

The generated shaders provide position and fragment color. The central behavioral axis is the ordered load, clear, and draw sequence, not shader control flow.

## Runtime Execution and Result Checking

The shared group parameters select legacy render-pass, dynamic-rendering, primary-command-buffer, or secondary-command-buffer recording. Legacy mode creates a render pass whose attachments load and store in attachment-optimal layouts ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L250-L303)). Dynamic rendering builds matching attachment descriptions and requires `VK_KHR_dynamic_rendering` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L504-L559), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L774-L804)). Secondary mode records the draw sequence in a secondary buffer and executes it from a primary buffer; the complete-secondary variant contains the dynamic-rendering scope, while the partial variant begins it in the primary ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L579-L629)).

Before rendering, each present attachment is transitioned to its attachment layout. After rendering, the command buffer inserts transfer-write-to-attachment-read/write memory barriers, transitions attachments to `TRANSFER_SRC_OPTIMAL`, submits to the universal queue, and waits for queue idle ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L377-L388), [source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L631-L661)). These barriers and image transitions make the subsequent host readback observe the completed attachment writes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible implementation cause(s) |
|---|---|
| `load_clear_draw`, `draw_clear_draw`, `clear_clear_draw` | Render-pass load, clear, draw ordering, blending, depth, or attachment handling. |
| `load_clear`, `draw_clear`, `clear_clear` | Clear ordering, attachment load, or copyback behavior. |

### Cause Analysis

#### Ordered attachment operations

**Possible failure symptoms:** Color or depth readback differs from the expected final attachment value.

**Possible implementation causes:** Incorrect render-pass load operation, clear command, draw ordering, blending, depth test, layout transition, or readback.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the selected color/depth format lacks the required attachment or transfer features.

### Design-based pruning

Dynamic-rendering and secondary-command-buffer combinations are reduced by the source's registration rules.

## Key Takeaways

- The family checks ordered render-pass load, draw, and clear operations.
- Color and depth results expose ordering, blending, depth, and attachment-transition errors.
- A mismatch is not by itself evidence of a shader-only defect.

## Source Reference Appendix

A color case is unsupported when the requested color format cannot support the required color-attachment/transfer usages or lacks `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT`. A depth case is unsupported when its depth-attachment/transfer usages are unavailable. Dynamic-rendering cases additionally require `VK_KHR_dynamic_rendering` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L774-L804)). These are support skips, not rendering failures.

When a color attachment exists, every read-back pixel is compared with the expected color; any RGB channel difference at or above `0.01` fails. When depth exists, every depth pixel is compared with expected `0.9`; a difference at or above `0.01` fails. A successful instance returns `Pass` ([source](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L663-L717)).

### Source map

- Test declaration: [vktDrawMultipleClearsWithinRenderPass.hpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.hpp#L34-L47)
- Formats, topologies, and parameters: [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L64-L154)
- Resource and pipeline construction: [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L186-L375)
- Command recording: [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L377-L559)
- Execution/readback: [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L563-L717)
- Registration: [vktDrawMultipleClearsWithinRenderPass.cpp](../../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L818-L949)

### Key takeaways

- The observable contract is ordering inside one render pass, not interaction between separate passes.
- `LOAD` is only the first step; subsequent clears are explicit `vkCmdClearAttachments` calls.
- Three-step cases verify blended draw output; two-step cases verify that the final clear replaces prior content.
- Color-only, depth-only, and combined attachments exercise the same operation sequences with format-specific support checks.
- Validation is exhaustive over the read-back image, with `0.01` color/depth tolerances.
