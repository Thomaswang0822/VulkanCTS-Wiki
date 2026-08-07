# Understanding Brief: IndirectInstancedTests

## One-Sentence Test Purpose

This test checks that `vkCmdDrawIndirect` fetches one or more `VkDrawIndirectCommand` records correctly while instanced vertex input, `instanceCount`, and `firstInstance` produce the expected image.

## Background Knowledge

- An indirect draw reads `vertexCount`, `instanceCount`, `firstVertex`, and `firstInstance` from a device-visible `VkDrawIndirectCommand`; `drawCount` selects how many records are consumed and `stride` separates them.
- Instancing repeats the vertex sequence. `firstInstance` is the starting instance index visible to instance-rate attribute fetches; it is not a vertex offset.
- A secondary command buffer records draw commands separately from the primary buffer. Dynamic rendering may be wholly inside the secondary buffer or may be begun and ended by the primary buffer around `vkCmdExecuteCommands`.
- The test uses an independent `rr::Renderer` image as its oracle, so command-record interpretation and instance addressing are checked through their rasterized result.

## One Concrete Example

For `draw.renderpass.indirect_instanced.2`, the case creates two records with the same `vertexCount`, `instanceCount`, and `firstInstance`, but with `firstVertex` set to `vertexCount * i`. It uploads both records, binds the position and instance-color buffers, and calls `vkCmdDrawIndirect(..., drawCount = 2, stride = sizeof(VkDrawIndirectCommand))`.

## End-to-End Test Flow

```text
[registration] choose drawCount = 1, 2, 4, or 16
[iterate] choose instanceCount and firstInstance from fixed arrays
[host] create position, instance-color, indirect-command, image, and pipeline resources
[host] record render-pass or dynamic-rendering commands; optionally record the draw in a secondary buffer
[device] fetch drawCount command records, repeat vertices for instanceCount, and rasterize
[host] wait, read the 128x128 color image, and fuzzy-compare with rr::Renderer
```

For each of 20 `(instanceCount, firstInstance)` combinations, vertex data is regenerated. The zero-instance case still allocates at least one instance-color entry, avoiding an empty upload while checking that no instances are rendered.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Creation and role |
|---|---|
| `vert` / `frag` GLSL | Generated GLSL 430 pass-through shaders. The vertex stage forwards position and instance-rate color; the fragment stage writes that color. |
| Graphics pipeline | Uses two vertex bindings: binding 0 is per-vertex position and binding 1 is `VK_VERTEX_INPUT_RATE_INSTANCE` color. |
| Position buffer | Holds an 8x8 grid of lower-left triangles. Positions are narrowed horizontally by `instanceCount` so the instances tile the target. |
| Instance-color buffer | Holds colors for indices from zero through `firstInstance + instanceCount - 1`; the vertex fetch uses the instance index. |
| Indirect buffer | Holds `drawCount` consecutive `VkDrawIndirectCommand` records with a fixed `sizeof(VkDrawIndirectCommand)` stride. |
| Color target | A 128x128 `VK_FORMAT_R8G8B8A8_UNORM` image, used as attachment and read back for comparison. |
| Command buffers | A primary buffer is always submitted. Non-VulkanSC secondary variants also record the rendering/draw sequence in a secondary buffer and execute it from the primary. |

## What Is Checked

The GPU image is compared with an `rr::Renderer` image using `tcu::fuzzyCompare` and threshold `0.05`. The reference uses the same generated positions and colors and is rendered with the selected `instanceCount`; its vertex shader reads instance attributes with the selected `firstInstance`. A mismatch can therefore reflect indirect record fetch, multi-draw sequencing, instance addressing, vertex-input rate, rendering scope, or ordinary rasterization rather than merely a host-side record value.

## Behavior Parameter Identification

> **Behavior parameter:** registered indirect command count
>
> **Candidate values:** `1`, `2`, `4`, `16`
>
> The internal loop is also a behavioral dimension: `instanceCount` is `0`, `1`, `2`, `4`, or `20`, and `firstInstance` is `1`, `3`, `4`, or `20`. These values are not additional registration identifiers.

## What Failure Means

| Failing registration value | Likely area to investigate |
|---|---|
| `1` | Basic indirect parameter fetch, instanced vertex repetition, or first-instance handling. |
| `2` | Multiple records, `firstVertex` separation, or multi-draw sequencing in addition to the basic path. |
| `4` | Multi-draw indirect support and record addressing at a larger command count. |
| `16` | Large multi-draw sequencing, indirect-buffer stride/addressing, or the `maxDrawIndirectCount` limit. |

The image comparison cannot by itself distinguish command-fetch, vertex-input, shader, rasterization, or readback defects; correlate the failing internal instance pair and command-buffer mode with validation output and implementation traces.

## Important Variations and Special Cases

- `drawCount > 1` requires `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` and `limits.maxDrawIndirectCount >= drawCount`. All four leaves require `DEVICE_CORE_FEATURE_DRAW_INDIRECT_FIRST_INSTANCE`.
- Render-pass leaves are under `draw.renderpass.indirect_instanced`. Outside VulkanSC, dynamic-rendering leaves are under `draw.dynamic_rendering.primary_cmd_buff`, `partial_secondary_cmd_buff`, and `complete_secondary_cmd_buff`.
- The dispatcher excludes `nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` for this family because registration is guarded by `!groupParams->nestedSecondaryCmdBuffer`.
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`. Secondary command-buffer recording uses rendering inheritance information; when the secondary completely contains the dynamic render pass, it begins and ends rendering itself.
- The source's `#ifndef CTS_USES_VULKANSC` guard removes the secondary/dynamic-rendering recording branch for VulkanSC. The VulkanSC mustpass therefore contains only the render-pass leaves.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test implementation | [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L292-L444) | Iteration, command creation, recording, submission, reference rendering, and comparison. |
| Public factory | [`vktDrawIndirectInstancedTests.hpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.hpp#L35) | Declares `createIndirectInstancedTests`. |
| Registration identifiers | [`createIndirectInstancedTests`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L607-L624) | Preserves group `indirect_instanced` and leaves `1`, `2`, `4`, `16`. |
| Support checks | [`DrawIndirectInstancedCase::checkSupport`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L566-L580) | Defines feature and limit prerequisites. |
| Indirect command issue | [`DrawIndirectInstancedInstance::draw`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L492-L504) | Shows the exact `vkCmdDrawIndirect` count and stride. |
| Dispatcher | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100) | Shows render-pass/dynamic-rendering attachment and nested-secondary registration. |
| Mustpass evidence | [`vk-default draw.txt`](../../../mustpass/main/vk-default/draw.txt#L793-L796) and [`vksc-default draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L959-L962) | Confirms exact Vulkan and VulkanSC identifiers. |
| Draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) | Defines indirect draw parameters and instanced execution semantics. |
| Feature semantics | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc) | Defines feature-dependent behavior referenced by support checks. |

## Questions / Risk Points for User Audit

- The reference renderer draws one primitive list with `instanceCount`, whereas Vulkan executes `drawCount` records whose `firstVertex` offsets partition the position buffer. Confirm that the generated partition and reference geometry remain equivalent for every registered count.
- `instanceCount = 0` is intentionally included. It tests no rasterized instances while still exercising command recording, resource transitions, submission, and readback.
- Dynamic rendering and secondary-command-buffer claims apply to non-VulkanSC builds only; the `vksc-default` evidence must not be generalized to those modes.

## Conversion Notes for Final Wiki Rewrite

Preserve the obsolete `vktDrawIndirectInstancedTests.md` page unchanged. Preserve the exact group and leaf identifiers: `indirect_instanced`, `1`, `2`, `4`, and `16`. Keep the command-buffer model, feature gates, mustpass boundaries, and image-validation details in the final `IndirectInstancedTests.md` page.
