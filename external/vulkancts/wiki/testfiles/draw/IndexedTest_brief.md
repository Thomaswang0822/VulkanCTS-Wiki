# Understanding Brief: indexed draw tests

## One-Sentence Test Purpose

This test checks whether Vulkan indexed drawing uses the correct index data, base vertex, instance state, command variant, and index-buffer update ordering.

## Background Knowledge

### Indexed vertex fetch

An indexed draw reads an element from the bound index buffer and adds `vertexOffset` before fetching vertex attributes. The bind offset locates the first index byte; an allocation offset changes the buffer's memory placement. These are independent adjustments.

### Instances and indirect parameters

Each instance repeats the indexed primitive sequence. `firstInstance` supplies the starting instance ID. Indirect commands move draw parameters into a device-visible buffer, and count commands obtain the number of draws from another value, so the test can fail before the vertex shader if parameter fetch is wrong.

## One Concrete Example

For `draw.renderpass.indexed_draw.draw_indexed_triangle_list`, the test binds `VertexFetch.vert` inputs, selects six indices, and calls `vkCmdDrawIndexed` with `vertexOffset = 13`. The vertex shader compares `gl_VertexIndex` with `in_refVertexIndex`; matching vertices retain their expected color, while a mismatch becomes red.

## End-to-End Test Flow

```text
[host] choose topology, offsets, draw family, and feature-gated switches
[host] create vertex/index buffers, target image, pipeline, and optional SSBO
[host] write index data at the selected bind and allocation offsets
[host] record direct, indirect, multi-draw, or update-before-draw commands
[device] fetch indices, add the base vertex, run the graphics pipeline, and optionally increment the fragment counter
[host] wait, read the color result and optional counter, and compare with the reference
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The ordinary path loads `VertexFetch.vert` and `VertexFetch.frag`. Count cases load `VertexFetchCount.vert` and `VertexFetchCount.frag`. The test also generates render-pass/framebuffer or dynamic-rendering state and, for indirect paths, indexed draw parameter buffers.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read | no | Provides positions, colors, and reference indices. |
| Index buffer | yes | yes, or `VK_NULL_HANDLE` in maintenance6 cases | read | no | Supplies `VK_INDEX_TYPE_UINT32`, `VK_INDEX_TYPE_UINT16`, or `VK_INDEX_TYPE_UINT8` indices. |
| Color target | yes | yes | written | yes | Compared with the blue reference image. |
| Counter SSBO | yes, count cases only | yes | atomically written | yes | Compared with `indexCount`. |
| Staging buffer | yes, update-before-draw only | yes for copy | read by transfer | no | Supplies index bytes copied after the index buffer is bound. |

## What Is Checked

- Ordinary and instanced paths use a fuzzy image comparison with threshold `0.05`.
- Null-descriptor paths without count validation use a software-rasterized reference and position-deviation comparison.
- Count paths require both an exact image comparison and `ssboCounter == indexCount`.
- 8-bit multi-bind and update-before-draw paths use an exact all-blue image comparison.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `draw_indexed_*`, `draw_instanced_indexed_*`, `draw_indexed*_*maintenance6`, `multibind_8bit_case_*`, `update_index_buffer_before_draw_*`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `draw_indexed_*` | Indexed address calculation, base-vertex addition, or primitive assembly. |
| `draw_instanced_indexed_*` | Instance repetition, `firstInstance`, or inherited indexed fetch. |
| `draw_indexed*_*maintenance6` | Maintenance6 descriptor, command, indirect parameter, multi-draw, or counter behavior. |
| `multibind_8bit_case_*` | 8-bit index decoding or repeated bind state. |
| `update_index_buffer_before_draw_*` | Transfer-to-vertex-input visibility or index decoding. |

## Important Variations and Special Cases

- Maintenance6 combines direct, indirect, indirect-count, and multi-indexed commands with bind2, null-descriptor, and counter switches.
- Specialized 8-bit and update-before-draw cases are omitted from dynamic-rendering and secondary-command-buffer variants.
- The source generates the standard matrix twice outside VulkanSC: once with ordinary binding and once with the `_maintenance_5` suffix.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Generated registration matrix | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1614-L1885) | Exact families and identifiers. |
| Ordinary execution | [`DrawIndexed::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L367-L511) | Buffer setup and indexed draw. |
| Maintenance6 execution | [`DrawIndexedMaintenance6::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L711-L957) | Null and command variants. |
| Copy-before-draw execution | [`UpdateBeforeDrawInstance::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1455-L1598) | Transfer and barrier sequence. |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L37-L89) | Indexed and topology rules. |

## Questions / Risk Points for User Audit

- Does the family-based behavior axis make the failure table useful enough for all generated leaves?
- Should the final page include more detail for indirect parameter buffers, or is the current family-level explanation sufficient?
- Are the distinction between allocation offset, bind offset, and `vertexOffset` clear?

## Conversion Notes for Final Wiki Rewrite

Keep the concrete `VertexFetch.vert` example as one representative shader walkthrough. Distill the indexed-fetch and instance concepts into `Background Knowledge`; keep generated names, full registration tree, feature gates, and comparison methods in the page body. Copy the failure mapping table into the final page and write fresh cause analysis.
