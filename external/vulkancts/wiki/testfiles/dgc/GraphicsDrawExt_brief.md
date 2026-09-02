# Understanding Brief: graphics draw tokens

## One-Sentence Test Purpose

This test checks whether `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` and `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT` execute generated graphics draws with the selected vertex or index state, shader stages, pipeline construction, execution-set, preprocessing, ordering, and draw-parameter variants.

## Background Knowledge

### EXT device-generated graphics draw tokens

A `VkIndirectCommandsLayoutEXT` describes one generated command sequence. State tokens provide values such as push constants and buffer bindings, and the final action token performs the draw. The EXT rules require one action token at the end of the layout. `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` consumes a `VkDrawIndirectCommand`; the indexed action consumes a `VkDrawIndexedIndirectCommand` and uses an index-buffer token when the case selects per-sequence index state.

Why it matters here:
- The test changes every draw record field that can affect the rendered result, including counts, instance values, starting positions, and, for indexed draws, `firstIndex` and `vertexOffset`.
- The layout can supply vertex or index buffer bindings through generated state, or omit those binding tokens in the simple and supplemental indexed paths.
- An indexed DX variant uses `VK_INDIRECT_COMMANDS_INPUT_MODE_DXGI_INDEX_BUFFER_EXT` and stores an `IndexBufferViewD3D12` representation in the generated stream.

### Execution sets and preprocessing

An execution set lets a generated sequence select a pipeline or shader object. With pipelines, the sequence index selects one of three pipeline shader combinations. With shader objects, the stream supplies one index per active shader stage. Explicit preprocessing runs `vkCmdPreprocessGeneratedCommandsEXT` before execution; a separate command buffer needs an explicit synchronization barrier before the generated draw. The unordered-sequences flag permits implementation-dependent sequence order.

Why it matters here:
- The rendered reference image distinguishes the selected shader and sequence, so an implementation cannot silently use one state for all sequences.
- The expected image remains valid when sequence processing is unordered because each sequence writes a defined region and the test accounts for its state.
- The same-state and separate-state preprocess cases exercise the two host command-buffer arrangements.

## One Concrete Example

A representative `token_draw` case renders four triangles into a 2x2 color attachment using three generated sequences. The first sequence uses three vertices, the second uses six vertices with a wider vertex stride, and the third uses three vertices with a nonzero `firstVertex` and two instances. The stream contains an execution-set token when requested, a push-constant token, a vertex-buffer token, and the final `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` action. The fragment shader encodes push-constant data in red and instance data in green.

The indexed counterpart uses one vertex buffer and three index buffers. Its records vary `indexCount`, `instanceCount`, `firstIndex`, `vertexOffset`, and `firstInstance`; the final index buffer uses `VK_INDEX_TYPE_UINT16`. The stream replaces the vertex-buffer token with an index-buffer token and ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT`.

## End-to-End Test Flow

```text
[host] choose TestType, pipeline construction, extra stages, execution-set, preprocessing, draw-parameter, and ordering values
[host] create the 2x2 color image and host-visible copy buffer
[host] create per-sequence vertex buffers for token_draw or index buffers for indexed cases
[host] generate the vertex, fragment, and optional tessellation or geometry shader variants
[host] build the indirect-command layout with optional execution-set, push-constant, vertex-buffer, or index-buffer tokens and one draw action token
[host] fill the generated-command buffer with three sequence records and the selected state indices
[host] create pipeline, shader objects, execution set, and preprocess storage as selected
[host] record bindings, push constants, preprocessing, barriers when needed, and a graphics render pass
[device] process each sequence and execute the generated non-indexed or indexed draw
[device] rasterize triangles and write encoded state to the color attachment
[host] copy the color attachment to a host-visible buffer after submission completes
[host] construct the reference pixels and compare them with the rendered result
[host] return pass or fail from the image comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` generates normal and execution-set shader variants. The vertex shader can report `gl_InstanceIndex`, `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance`; the fragment shader writes the corresponding checks to alpha.
- Tessellation cases add tessellation-control and tessellation-evaluation shaders. Geometry cases add geometry shaders. The extra stage carries the execution-set flip choice from the vertex shader.
- The generated-command layout can carry `VK_INDIRECT_COMMANDS_TOKEN_TYPE_EXECUTION_SET_EXT`, `VK_INDIRECT_COMMANDS_TOKEN_TYPE_PUSH_CONSTANT_EXT`, `VK_INDIRECT_COMMANDS_TOKEN_TYPE_VERTEX_BUFFER_EXT`, or `VK_INDIRECT_COMMANDS_TOKEN_TYPE_INDEX_BUFFER_EXT`, followed by the draw action token.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 2x2 color image and copy buffer | yes | color attachment and transfer source | written by fragment stage, then copied | yes | Carries the rendered result into the comparison. |
| Vertex buffers | yes, `token_draw` cases | referenced by vertex-buffer tokens | read by vertex stage | no | Vary size, stride, and starting data across sequences. |
| Index buffers | yes, indexed cases | referenced by index-buffer tokens | read by indexed draws | no | Vary index type, size, and vertex offset across sequences. |
| Push constants | yes | bound through the pipeline layout | read by fragment stage and optional vertex stage | no | Encode sequence identity and supply draw-parameter expectations. |
| Generated-command buffer | yes | referenced by generated execution | read by DGC processing | no | Holds token data and the three draw records. |
| Preprocess buffer | yes, explicit-preprocess cases | referenced by generated execution | written by preprocessing and read by execution | no | Carries implementation-generated state between DGC operations. |
| Pipeline, shader objects, or execution set | yes, selected variants | bound directly or through execution-set token | used by graphics stages | no | Selects the state that each sequence must execute. |

## What Is Checked

- The host computes the expected four-pixel image from the three generated records. The 2x2 layout lets the test observe counts, instances, vertex or index starts, and buffer strides without a large render target.
- The fragment shader writes red from the push constant plus a vertex-shader offset, green from `gl_InstanceIndex`, and blue from the selected fragment shader. With `_check_draw_params`, alpha is one only when the shader observes the expected `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance`.
- Execution-set variants flip selected triangle positions and select an alternate fragment shader, producing a different reference image. Tessellation and geometry variants pass the flip choice through the extra stage.
- The main draw path compares the copied color buffer with `tcu::floatThresholdCompare` using a `0.005` threshold for the color channels. A mismatch reports `Unexpected results in color buffer; check log for details`.
- `indexed_draw_without_index_buffer_token` cases use a 4x4 point render. They check the supplemental indexed action path with fixed index-buffer binding and optional push-constant token, and compare the generated blue gradient or fixed color with the reference using the source-selected threshold.

## Behavior Parameter Identification

> **Behavior parameter:** draw action test family
>
> **Candidate values:** `token_draw`, `token_draw_indexed`

`token_draw` tests `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` with generated vertex-buffer state, with a simple form that omits the vertex-buffer token. `token_draw_indexed` tests `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT` with Vulkan or DXGI index-buffer input modes, plus the separately registered `indexed_draw_without_index_buffer_token` cases. Pipeline construction, shader stages, execution sets, preprocessing, ordering, and draw-parameter checking vary how each action executes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `token_draw` | The implementation may consume the wrong `VkDrawIndirectCommand` fields, apply the wrong generated vertex-buffer binding, select the wrong graphics state, or produce incorrect rasterization or color-buffer data. |
| `token_draw_indexed` | The implementation may consume the wrong `VkDrawIndexedIndirectCommand` fields, apply the wrong index-buffer address, size, type, or vertex offset, mishandle the Vulkan or DXGI index mode, or produce incorrect rasterization or color-buffer data. |

## Important Variations and Special Cases

- `monolithic` creates one ordinary graphics pipeline. `shader_objects` creates `VkShaderEXT` objects and binds stage state through shader-object commands. The four GPL names select fast-linked, link-time-optimized, or mixed-base pipeline-library construction. GPL cases require an execution set.
- `_with_tess` adds tessellation control and evaluation stages. `_with_geom` adds a geometry stage. The feature checks require tessellation or geometry support for those cases.
- `_with_execution_set` adds `VK_INDIRECT_COMMANDS_TOKEN_TYPE_EXECUTION_SET_EXT`. Pipeline cases select one pipeline per sequence. Shader-object cases select stage objects with per-stage indices.
- `_preprocess_same_state_cmd_buffer` preprocesses and executes with the same state command buffer. `_preprocess_separate_state_cmd_buffer` uses a separate state command buffer and synchronizes it before execution.
- `_unordered` sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`.
- `_check_draw_params` requires `VK_KHR_shader_draw_parameters` and checks the draw built-ins in shader output.
- `_simple` selects `DRAW_SIMPLE`, which omits the generated vertex-buffer or index-buffer binding token and uses a single pre-bound buffer. `_dx_index` selects `DRAW_INDEXED_DX` and `VK_INDIRECT_COMMANDS_INPUT_MODE_DXGI_INDEX_BUFFER_EXT`.
- The supplemental `indexed_draw_without_index_buffer_token` family runs both with and without `_with_pc_token`; it tests an indexed draw action while the host binds the index buffer directly.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters and feature gates | [`DrawTestParams` and `DGCDrawCase::checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L212-L412) | Defines draw type, extra stages, pipeline type, preprocessing, draw-parameter checks, execution sets, and support requirements. |
| Generated shaders | [`DGCDrawCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L414-L652) | Generates vertex, fragment, tessellation, and geometry variants and encodes observed values in color. |
| Vertex and index data | [`makeVertexBuffers` and `makeIndexBuffers`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L728-L956) | Creates per-sequence buffer layouts, index types, and vertex offsets. |
| Main draw setup and DGC stream | [`DGCDrawInstance::iterate` layout and command data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L959-L1290) | Builds the render target, token layout, draw records, bindings, and execution-set indices. |
| Execution and result checking | [`DGCDrawInstance::iterate` execution and comparison](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1302-L1827) | Records state, preprocessing, generated execution, copyback, reference image, and pass/fail comparison. |
| Supplemental indexed path | [`indexedDrawWithoutIndexTokenRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1860-L2067) | Covers direct index-buffer binding and the optional push-constant token. |
| Registration | [`createDGCGraphicsDrawTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2071-L2157) | Registers the two draw action test families and the full generated matrix. |
| EXT command-layout rules | [device-generated command layout](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout) | Defines action-token placement, explicit preprocessing, and unordered sequence semantics. |

## Questions / Risk Points for User Audit

- Is the distinction between `token_draw`, `token_draw_indexed`, and `indexed_draw_without_index_buffer_token` clear?
- Does the page explain why execution-set cases change both shader selection and the rendered reference?
- Are the Vulkan and DXGI indexed input modes distinguished without treating them as separate test families?
- Is the separate-state preprocessing synchronization clear enough?
- Should a representative generated shader walkthrough be added if the page can use the shader-analyzer and shader-disassembler workflow?

## Conversion Notes for Final Wiki Rewrite

- Keep the action-token mental model in `## Background Knowledge` and describe the full registration matrix in `## Parameter Dimensions and Observed Values`.
- Use one `## Behavior Parameters` axis with `token_draw` and `token_draw_indexed`; keep the supplemental direct-binding cases as a special variation.
- Distill the host/device timeline into `## Runtime Execution and Result Checking` and keep the exact failure mapping table.
- Put source-navigation links in the final appendix. Do not make the opening a source inventory.
