# Understanding Brief: BasicDrawTests

## One-Sentence Test Purpose

This test checks whether Vulkan direct, indexed, indirect, and indexed-indirect draw commands assemble and rasterize generated primitives correctly across topology, offset, and command-recording variants.

## Background Knowledge

- A Vulkan draw command supplies vertex or index data to the graphics pipeline. Direct commands carry parameters in the command call; indirect commands read command structures from a buffer.
- Primitive topology controls how fetched vertices form points, lines, triangles, strips, fans, or adjacency primitives. The number of fetched vertices therefore depends on both topology and primitive count.
- A software reference renderer can rasterize the same generated positions and colors independently. Comparing its image with the Vulkan image checks the complete draw-to-raster result rather than one host-side parameter.
- Render passes and dynamic rendering provide two attachment-scoping mechanisms. Secondary command buffers move draw recording into another command buffer, while nested secondary command buffers add another level.

## One Concrete Example

For `draw_indirect.triangle_strip.17_multi_command_multi_draw`, the source creates a triangle-strip command for 17 primitives, adds a second command with a randomized `firstVertex`, and submits both records through one indirect draw call with `drawCount = 2`. The reference renderer receives the generated vertex sequence and the same topology. The comparison therefore checks both indirect-record interpretation and triangle-strip assembly in one case.

## End-to-End Test Flow

1. Registration creates the `draw.renderpass.basic_draw` root and four command-family groups. Each family expands over ten primitive topologies and primitive counts `1`, `3`, `17`, and `45`, subject to mode-specific pruning.
2. `populateSubGroup` computes a topology-specific vertex count. For example, a triangle list uses three vertices per primitive, a triangle fan adds one leading vertex, and adjacency topologies use their Vulkan-defined consumption rules.
3. The case stores direct, indexed, or indirect parameters. Randomized offsets make the implementation address data beyond the simplest zero-based range. Indexed cases use `VK_INDEX_TYPE_UINT32`.
4. Support checks run. Adjacency requires the core geometry-shader feature; multi-draw indirect requires the core multi-draw-indirect feature; dynamic rendering and nested command buffers require their named functionality and features. Triangle fans also honor the portability-subset `triangleFans` feature when that subset is exposed.
5. The case creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` target, view, graphics pipeline, vertex buffer, command pool, and command buffers. It selects a render pass or dynamic rendering and records the selected primary/secondary/nested path.
6. The specialized instance generates the draw data, records the corresponding Vulkan command, submits it, and reads back the color target.
7. `rr::Renderer` rasterizes the generated positions and colors with matching topology. The test compares the reference and result images. Point lists use integer threshold and position-deviation comparison; other topologies use fuzzy comparison with threshold `0.053`.
8. A failed comparison returns a failing CTS status and records the comparison result in the test log.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | How it is produced | Role |
|----------|--------------------|------|
| Vertex GLSL | `DrawTestCase<T>::initShaderSources` creates a GLSL 430 pass-through vertex shader. | Writes position, point size, and color. |
| Fragment GLSL | `DrawTestCase<T>::initShaderSources` creates a GLSL 430 pass-through fragment shader. | Writes interpolated color to the color attachment. |
| Vulkan graphics pipeline | `DrawTestInstanceBase::initialize` creates pipeline state using the two shader stages and vertex input. | Executes the draw through Vulkan. |
| Software reference program | `PassthruVertShader` and `PassthruFragShader` are combined into `rr::Program`. | Produces the independent expected image. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read by vertex input | no | Holds generated positions and colors, including offset prefixes. |
| Index buffer/data | yes for indexed cases | yes through indexed draw setup | read by indexed commands | no | Exercises index fetch, `firstIndex`, and `vertexOffset`. |
| Indirect buffer/data | yes for indirect cases | yes | read by indirect commands | no | Holds one or two draw command structures. |
| Color target image | yes | yes as color attachment | written by rasterization; copied for inspection | yes | Carries the rendered result being compared. |
| Color image view and framebuffer/rendering scope | yes | used by graphics commands | selects the color attachment | indirectly | Connects the pipeline output to the target image. |

## What Is Checked

The test checks the final color image against an independently generated software image. The reference uses the same generated vertex positions and colors and maps the Vulkan topology before rasterizing. The Vulkan path must therefore agree on parameter fetch, primitive assembly, vertex processing, rasterization, attachment writes, and readback within the comparison tolerance.

The source does not compare shader output values through a storage buffer or a per-vertex sentinel. It checks the color attachment image. The comparison rules are explicit in `imageCompare`: point lists use color threshold 4 and position tolerance `(1, 1, 0)`; other topologies use fuzzy threshold `0.053f`.

## Behavior Parameter Identification

The primary behavioral axis is the registered draw command family:

- `draw`: direct non-indexed command arguments.
- `draw_indexed`: direct indexed command arguments with generated `uint32_t` indices.
- `draw_indirect`: one or two `VkDrawIndirectCommand` records, including a one-call multi-draw form.
- `draw_indexed_indirect`: one or two `VkDrawIndexedIndirectCommand` records, including indexed offsets and a one-call multi-draw form.
- `misc`: separate maintenance5 and Amber cases in the non-VulkanSC, non-dynamic-rendering path.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Direct parameter handling, vertex fetch, topology assembly, rendering mode, or image transfer mismatch. |
| `draw_indexed` | Index fetch, `firstIndex`, `vertexOffset`, multi-command accumulation, topology assembly, or image transfer mismatch. |
| `draw_indirect` | Indirect buffer fetch, record stride/addressing, `firstVertex`, `drawCount`, topology assembly, or image transfer mismatch. |
| `draw_indexed_indirect` | Indexed indirect record fetch, index/vertex offsets, `drawCount`, topology assembly, or image transfer mismatch. |
| `misc` | Maintenance5 buffer/pipeline flag behavior or the Amber case's tested behavior. |

The image comparison localizes symptoms only at image level. Source inspection is needed to distinguish a command-parameter bug from a topology, attachment, readback, or implementation issue.

## Important Variations and Special Cases

- Dynamic-rendering variants reduce primitive counts to `1` and `45` because the source avoids duplicating the intermediate counts.
- Secondary-command-buffer variants keep only even-indexed topology values. Nested secondary-command-buffer variants keep only the `draw` family.
- Indexed `_multi_command` cases are limited to simple list topologies: point list, line list, and triangle list.
- `maintenance5` is registered only without VulkanSC and only when dynamic rendering is disabled. `flat_b_sat_error` is an Amber case in the same `misc` group.
- The topology loop excludes `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and generated names | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1725-L1905) | Defines hierarchy, values, pruning, and case construction. |
| Parameter structures | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L119-L289) | Shows direct, indexed, and indirect command fields. |
| Runtime setup and modes | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L365-L706) | Creates target resources and records render-pass/dynamic/secondary paths. |
| Shaders | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L809-L888) | Generates the pass-through GLSL stages. |
| Result comparison | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L349-L363) | Defines topology-specific thresholds. |
| Mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L17477-L17807) | Confirms the category-qualified registration and leaf variants. |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) | Defines draw-command parameter behavior. |
| Primitive assembly | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc) | Defines topology and vertex-processing context. |

## Questions / Risk Points for User Audit

- The current `vk-default/draw.txt` evidence confirms the render-pass path and the full `basic_draw` family leaves. The exact set of dynamic-rendering and secondary-command-buffer mustpass files should be checked separately if those variants are being audited as a release-specific coverage claim.
- The reference image uses `rr::Renderer`, while Vulkan uses the generated GLSL pair. The implementation relies on matching generated inputs and topology mapping; it does not require identical internal rasterization algorithms.
- `firstVertex`, `firstIndex`, and `vertexOffset` are randomized from source-controlled limits. Their exact per-case values depend on the deterministic group-name seed and should not be documented as fixed constants.

## Conversion Notes for Final Wiki Rewrite

- Preserve the exact registration identifiers and the one-level `draw.renderpass.basic_draw` tree.
- Keep the generated shader code and SPIR-V assembly unchanged when moving this material into the final page.
- Carry the Behavior Parameter Identification and Failure Cause Mapping into the final `BasicDrawTests.md` page, then write Cause Analysis against the implementation and Vulkan semantics.
