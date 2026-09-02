# Understanding Brief: EXT graphics draw-count tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` executes count-controlled graphics draw sequences with the right draw data, state selection, and rendered result.

## Background Knowledge

### Count draw tokens

A `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_COUNT_EXT` or `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_COUNT_EXT` token reads a `VkDrawIndirectCountIndirectCommandEXT` value from the generated-command stream. That value supplies a device address, a stride between ordinary indirect draw structures, and a command count. The structures at the address provide the per-draw arguments. The implementation limits the count used by the token to the `maxDrawCount` supplied for generated-command memory requirements and execution.

### Generated-command sequences

An EXT indirect-command layout processes one sequence per sequence index. The token inputs for a sequence are found at the sequence stride and token offset. State tokens, such as an execution-set token or an index-buffer token, precede the final action token. With `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`, the implementation may process sequences in an order that is not deterministic.

Why it matters here:
- The test puts four count records in four generated-command sequences and makes their ordinary indirect draw data use different strides.
- The same action token is exercised with and without preprocessing, execution-set state, and unordered sequence processing.

## One Concrete Example

Consider a non-indexed `token_draw_count` case with pipeline state, no execution set, no preprocessing, and no unordered flag. The host creates 16 pixel-sized triangle chunks, divides them among four sequences, and writes one `VkDrawIndirectCountIndirectCommandEXT` record per sequence. Each record points to a sequence buffer containing `VkDrawIndirectCommand` values, gives the stride including any padding, and sets `commandCount` to that sequence's chunk count. The final count token expands this data into the ordinary indirect draws.

For an indexed case, the action token reads `VkDrawIndexedIndirectCommand` values instead. The test can add an `VK_INDIRECT_COMMANDS_TOKEN_TYPE_INDEX_BUFFER_EXT` token, whose `VkBindIndexBufferIndirectCommandEXT` value selects a device-addressed `VK_INDEX_TYPE_UINT32` index buffer.

## End-to-End Test Flow

```text
[host] choose the registered TestParams combination and seed the pseudorandom generator
[host] create one triangle around each pixel of a 32 x 32 framebuffer
[host] assign the 1024 pixels to 16 chunks and divide the chunks among four sequences
[host] write ordinary draw structures, count-token records, and indexed data when selected
[host] generate vertex and fragment GLSL, then build pipelines or shader objects
[host] create an indirect-command layout with optional execution-set and index-buffer tokens followed by one count token
[host] optionally preprocess the generated commands in the same state command buffer or a separate state command buffer
[host] begin rendering, execute the generated commands, copy the color image to a host-visible buffer, and wait for completion
[host] build a reference image from the generated draw arguments and compare it with the copied image
[host] decide pass/fail from the color comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The host builds vertex and fragment GLSL strings in `initDrawCountPrograms`.
- Without an execution set, one vertex and one fragment program are generated. With an execution set, four variants are generated. Their interface sizes are 8, 12, 16, and 20 integer values, matching the four input storage buffers.
- Pipeline cases create graphics pipelines with `VK_PIPELINE_CREATE_2_INDIRECT_BINDABLE_BIT_EXT` when an execution set is used. Shader-object cases create `VkShaderEXT` objects and bind them through the EXT execution set.
- The generated-command stream contains execution-set indices when selected, an index-buffer record for the index-token cases, and one `VkDrawIndirectCountIndirectCommandEXT` record per sequence.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read by vertex input | no | Holds three vertices for each framebuffer pixel. |
| Per-sequence indirect buffers | yes | addressed by count records | read by count-token execution | no | Hold padded `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand` arrays. |
| Index buffers | yes, indexed cases | yes, directly or through the index-buffer token | read by indexed draws | no | Reverse traversal and per-chunk offsets test indexed arguments and `vertexOffset`. |
| Execution-set input buffers | yes, execution-set cases | descriptor set | read by the selected vertex shader | no | Supply variant-specific integer values for shader I/O and descriptor binding checks. |
| Expected accumulation buffer | yes, execution-set cases | descriptor set | read by the fragment shader | no | Stores the expected sum for every pixel in each sequence. |
| Expected draw-parameter buffer | yes, `check_draw_params` cases | descriptor set | read by the fragment shader | no | Stores expected `gl_DrawID`, base vertex or vertex offset, and base instance values. |
| Color image and readback buffer | yes | color attachment and transfer destination | color image written, then copied | yes | Carries the rendered red, green, and blue validation channels to the host. |
| Preprocess buffer | yes when preprocessing is selected | generated-command preprocessing state | written or consumed by preprocessing and execution | no | Holds implementation state required between preprocessing and execution. |

## What Is Checked

- Every framebuffer pixel has a small triangle as its expected draw coverage. Negative clip or cull distance on any vertex makes that pixel clear instead of covered.
- Red encodes `gl_InstanceIndex / 255.0`. The reference uses the selected `firstInstance` and `instanceCount` to compute the same value.
- With an execution set, the vertex and fragment variants pass and sum descriptor values. Green is zero when the sum matches the per-pixel expected value and one otherwise.
- With `check_draw_params`, blue stays one only when the shader-observed `gl_DrawID`, `gl_BaseVertex` or indexed `vertexOffset`, and `gl_BaseInstance` match the expected values for that draw.
- Indexed reference pixels are traversed in reverse order because the index buffer stores the vertices in reverse order. The color image is compared with a `0.005` per-channel threshold, which is between one and two 8-bit steps.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family and token form
>
> **Candidate values:** `token_draw_count`, `token_draw_indexed_count` with ordinary indexed data, `token_draw_indexed_count` with `_with_index_buffer_token`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `token_draw_count` | Count-token expansion of `VkDrawIndirectCommand` data, including command count, stride, and non-indexed draw arguments. |
| `token_draw_indexed_count` without `_with_index_buffer_token` | Count-token expansion of `VkDrawIndexedIndirectCommand` data, indexed traversal, `vertexOffset`, and the pre-bound index buffer. |
| `token_draw_indexed_count` with `_with_index_buffer_token` | Count-token expansion together with device-addressed index-buffer binding from `VkBindIndexBufferIndirectCommandEXT`. |

A failure in a suffix variant can also identify the selected execution-set binding, shader-object or pipeline path, preprocessing order, unordered sequence handling, or draw-parameter checks. The rendered comparison cannot by itself isolate which of those mechanisms failed.

## Important Variations and Special Cases

- `pipelines` and `shader_objects` select the graphics state representation. Adding `execution_set` makes the generated stream select one of four pipeline or shader variants per sequence.
- `preprocess_same_state_cmd_buffer` records preprocessing in the main command buffer. `preprocess_separate_state_cmd_buffer` records state in a separate command buffer, preprocesses there, inserts the extension's preprocess-to-execute barrier, and then executes on the main command buffer. The empty suffix means no explicit preprocessing.
- `_unordered` sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`. It changes sequence processing order, not the expected per-pixel result.
- `_check_draw_params` enables the `VK_KHR_shader_draw_parameters` requirement and adds shader checks for draw index, base vertex or vertex offset, and base instance.
- The registered index-token suffix is `_with_index_buffer_token`. It is present only for the indexed test family. The source's third test type, `DRAW_INDEXED_COUNT_INDEX_TOKEN`, shares that family and adds the token.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter types and support checks | [TestParams and checkDrawCountSupport](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L138-L210) | Defines the behavioral switches and feature gates. |
| Generated shader variants | [initDrawCountPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L276-L399) | Shows descriptor, shader I/O, and draw-parameter checks. |
| Draw and sequence construction | [testDrawCountRun chunk and sequence setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L447-L635) | Creates the 32 x 32 geometry, 16 chunks, and four padded sequences. |
| Indexed data and count records | [indexed buffers and token data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L638-L749) | Shows reverse indices, per-chunk offsets, strides, and command counts. |
| Command layout and stream data | [count-token layout and DGC stream](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1103-L1236) | Shows token order, execution-set selection, and `maxDrawCount`. |
| Preprocessing order | [state command buffer setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1237-L1310) | Distinguishes no preprocessing, same-state, and separate-state paths. |
| Rendering reference and comparison | [reference image and result check](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1410-L1464) | Defines coverage, colors, reversal, and pass/fail comparison. |
| Registered names | [createDGCGraphicsDrawCountTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1469-L1522) | Defines the complete registration matrix and exact suffix order. |
| EXT token semantics | [device-generated commands chapter](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L701-L723) | Defines count-record fields and their indirect command data. |
| EXT token processing and limits | [token processing and preprocessing requirements](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L929-L977) and [preprocess memory requirements](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L1827-L1872) | Grounds sequence processing, unordered order, and count clamping. |

## Questions / Risk Points for User Audit

- Does the distinction between `token_draw_indexed_count` and `_with_index_buffer_token` remain clear?
- Is the suffix order clear enough to identify a mustpass path without listing all 144 names?
- Should the page call the indexed base-vertex field `vertexOffset` whenever it discusses `gl_BaseVertex`?

## Conversion Notes for Final Wiki Rewrite

- Keep the registered hierarchy and the exact suffix grammar in the final page. State the verified total of 144 registered test cases: 48 under `token_draw_count` and 96 under `token_draw_indexed_count`.
- Distill the count-record explanation, indexed reversal, preprocessing timeline, rendered color channels, and feature pruning into the Level-3 sections.
- Use one representative generated-shader walkthrough only if the required shader-analysis tooling is run. The page should still explain the generated vertex and fragment roles without duplicating all four execution-set variants.
- Copy the `### Failure Cause Mapping` table into the final page and write fresh cause analysis there.
