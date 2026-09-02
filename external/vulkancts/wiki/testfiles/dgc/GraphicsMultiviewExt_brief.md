# Understanding Brief: GraphicsMultiviewExt

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` graphics execution respects `VK_KHR_multiview` view masks while producing the expected color and depth in each image layer.

## Background Knowledge

### Multiview and view masks

A multiview render executes the shader for the views selected by a mask. Bit `i` selects view `i`, and this test uses two image layers, so mask `1` selects layer 0, mask `2` selects layer 1, and mask `3` selects both. The fragment shader reads `gl_ViewIndex` through `GL_EXT_multiview` and writes it into the red channel.

Why it matters here:
- A selected layer must receive four quadrant draws.
- An unselected layer must retain the clear color and depth.
- The red channel exposes whether a fragment ran for view 0 or view 1.

### Device-generated graphics commands

The DGC stream describes four draw sequences. Depending on the case, each sequence can select a generated draw, bind a subsection of the vertex or index buffer with a token, and run after preprocessing. These variations must preserve the same multiview result.

## One Concrete Example

For `view_mask_2` with `regular_draw_buffer_tokens_dynamic_rendering`, the host creates a 2 by 2 image with two layers and four groups of four vertices. Each group covers one quadrant. The generated stream binds the group for a quadrant and issues a non-indexed draw. Dynamic rendering uses view mask `2`, so only layer 1 receives geometry. The fragment shader chooses a quadrant color and writes `1.0` to red through `gl_ViewIndex`; layer 0 remains at the clear values.

## End-to-End Test Flow

```text
[host] choose view mask and matrix flags
[host] create two-layer color and depth images, buffers, and pipeline state
[host] generate vertex and optional index data
[host] build the DGC layout and four quadrant command sequences
[host] clear attachments and insert image barriers
[host] begin render pass or dynamic rendering
[host] bind initial pipeline and push framebuffer extent
[host] preprocess generated commands when requested
[device] execute four generated draw sequences for the selected views
[device] write quadrant colors, gl_ViewIndex, and depth values
[host] end rendering, copy color and depth layers to host-visible buffers, and wait
[host] build reference layers and compare color and depth
[host] decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- One vertex shader passes `inPos` to `gl_Position`.
- One fragment shader uses `GL_EXT_multiview`, computes a quadrant index from `gl_FragCoord`, selects one of four colors, and writes `float(gl_ViewIndex)` to red.
- The implementation can generate a second fragment shader with the color table reversed for indirect execution sets. The registration skips that dimension.
- The host builds either a monolithic pipeline or a fast-linked graphics pipeline library. Dynamic-rendering cases add `VkPipelineRenderingCreateInfo` with the selected view mask.
- The DGC layout contains an optional vertex-buffer token, an optional index-buffer token, and either a draw or indexed-draw token. The implementation also contains an execution-set token path that registration excludes.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read | no | Holds four groups of four quadrant vertices. |
| Index buffer | yes, indexed cases | yes, indexed cases | read | no | Holds indices `0` through `15`. |
| Color image and readback buffer | yes | yes | written and copied | yes | Stores and returns per-view quadrant colors. |
| Depth image and readback buffer | yes | yes | written and copied | yes | Stores and returns the four quadrant depths. |
| DGC data buffer | yes | yes | read | no | Supplies four generated command sequences. |
| Push constant | yes | yes | read | no | Supplies the framebuffer extent used to calculate quadrant coordinates. |
| Render pass or dynamic-rendering state | yes | yes | controls execution | no | Carries the multiview view mask and attachment configuration. |

## What Is Checked

- For mask `1`, layer 0 contains the four quadrants and layer 1 remains clear.
- For mask `2`, layer 1 contains the four quadrants and layer 0 remains clear.
- For mask `3`, both layers contain the four quadrants.
- The red component equals the layer index from `gl_ViewIndex`; the remaining color components come from the quadrant table.
- The depth image contains `0.25`, `0.50`, `0.75`, and `1.00` in the four quadrants.
- The host compares each color layer with `tcu::floatThresholdCompare` using a zero threshold and each depth layer with `tcu::dsThresholdCompare` using `0.00002f`. Any mismatch fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** view-mask test family
>
> **Candidate values:** `view_mask_1`, `view_mask_2`, `view_mask_3`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `view_mask_1` | Incorrect selection or routing of view bit 0, or incorrect handling of inactive layer 1. |
| `view_mask_2` | Incorrect selection or routing of view bit 1, or incorrect handling of inactive layer 0. |
| `view_mask_3` | Incorrect handling of simultaneous views, view-to-layer mapping, or per-view `gl_ViewIndex` values. |
| Any view mask | Generated draw state, resource binding, synchronization, pipeline construction, or result copyback can produce a color or depth mismatch. |

## Important Variations and Special Cases

- `no_ies_monolithic` and `no_ies_gpl` compare monolithic construction with `VK_EXT_graphics_pipeline_library`.
- `regular_draw` and `indexed_draw` exercise separate DGC draw forms. When buffer tokens bind only a quadrant subsection, indexed draws set `firstIndex` to zero and use a negative `vertexOffset` to account for absolute indices.
- `_preprocess` adds `vkCmdPreprocessGeneratedCommandsEXT` and the preprocess-to-execute barrier.
- `_dynamic_rendering` uses `VK_KHR_dynamic_rendering` and supplies the view mask through `VkPipelineRenderingCreateInfo`.
- The source contains an indirect execution-set path, but registration skips `useIES` because the specification bans DGC combined with multiview and an indirect execution set.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and support | [`Params` and `checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L99-L175) | Defines the mask, feature gates, and matrix flags. |
| Shader generation | [`initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L177-L221) | Shows `GL_EXT_multiview`, quadrant selection, and `gl_ViewIndex`. |
| Multiview setup | [`iterate`, render-pass and pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L338-L467) | Propagates the view mask to render-pass or dynamic-rendering state. |
| DGC commands | [`iterate`, command layout and data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L483-L598) | Shows tokens, four sequences, and indexed offsets. |
| Result checking | [`iterate`, reference construction and comparison](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L679-L762) | Defines expected layers, thresholds, and failure status. |
| Specification background | [`renderpass.adoc`](../../../../vulkan-docs/src/chapters/renderpass.adoc) and [`generatedcommands.adoc`](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc) | Grounds multiview and DGC restrictions in the local Vulkan specification sources. |

## Questions / Risk Points for User Audit

- Is the distinction between a view mask and an image layer clear?
- Is the inactive-layer check clear enough to explain why a case can fail even when the selected layer looks correct?
- Is the indexed buffer-token offset correction understandable?
- Should the final page include a separate shader walkthrough if the category validator later requires one for this source?

## Conversion Notes for Final Wiki Rewrite

- Keep the three view-mask families as the primary behavior axis and place the remaining flags in the parameter matrix.
- Distill the multiview explanation into the final page's `## Background Knowledge` section.
- Preserve the layer-by-layer color and depth checking details in `## Runtime Execution and Result Checking`.
- Copy the `### Failure Cause Mapping` table into the final page unchanged, then write fresh cause analysis.
- Explain IES as implementation scaffolding that registration prunes, not as a registered test family.
