## Overview

**Core question:** Does each EXT count token execute the intended number of graphics draws with the intended indexed or non-indexed arguments and state?

- [vktDGCGraphicsDrawCountTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L447-L1522) implements `dgc.ext.graphics.draw_count`.
- The test builds four generated-command sequences. Each sequence points to a padded array of ordinary draw structures through a `VkDrawIndirectCountIndirectCommandEXT` count record.
- `token_draw_count` tests `VkDrawIndirectCommand`; `token_draw_indexed_count` tests `VkDrawIndexedIndirectCommand`, with an optional index-buffer token.
- The cases cover pipeline and shader-object state, execution sets, explicit preprocessing, unordered sequences, and shader checks for draw parameters. The test validates a rendered 32 x 32 image rather than only checking command completion.

## Background Knowledge

- A count draw token consumes a `VkDrawIndirectCountIndirectCommandEXT` record. Its `bufferAddress` locates ordinary indirect draw structures, `stride` separates them, and `commandCount` states how many structures the implementation may execute. The ordinary structures supply the per-draw arguments.
- An EXT indirect-command layout processes the token inputs for each sequence at the sequence stride and token offset. The action token is last. An execution-set or index-buffer token therefore changes state before the count token runs.
- `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT` permits implementation-dependent sequence order. A correct case must therefore produce the same pixel result without relying on the order in which the four sequences run.

## Registration Hierarchy

```text
dgc.ext.graphics.draw_count
├── token_draw_count
└── token_draw_indexed_count
```

## Parameter Dimensions and Observed Values

The registration loop in [createDGCGraphicsDrawCountTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1469-L1522) combines three action forms, two state representations, two execution-set choices, three preprocessing choices, two sequence-order choices, and two draw-parameter choices. The resulting 144 registered test cases are listed below exactly as `dgc.txt` records them.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `token_draw_count`, `token_draw_indexed_count` | Selects non-indexed or indexed ordinary indirect draw structures for the count token. | [test type and group selection](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L138-L184), [group registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1487-L1515) |
| State representation | `pipelines`, `shader_objects` | Uses indirect-bindable graphics pipelines or `VkShaderEXT` shader objects. | [pipeline and shader creation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L979-L1100) |
| Execution set | absent, `_execution_set` | Keeps one state choice fixed or selects one of four pipeline or shader variants from the generated stream. | [execution-set construction](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1115-L1172) |
| Preprocessing | absent, `_preprocess_same_state_cmd_buffer`, `_preprocess_separate_state_cmd_buffer` | Chooses no explicit preprocessing, preprocessing in the main state command buffer, or preprocessing with a separate state command buffer. | [preprocessing cases](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1249-L1284) |
| Sequence order | absent, `_unordered` | Selects ordered or implementation-dependent sequence processing. | [layout usage flags](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1103-L1113) |
| Draw parameter checking | absent, `_check_draw_params` | Adds fragment-shader checks for `gl_DrawID`, `gl_BaseVertex` or indexed `vertexOffset`, and `gl_BaseInstance`. | [generated draw-parameter checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L347-L395) |
| Indexed state token | absent, `_with_index_buffer_token` | Only the indexed family adds an index-buffer token and supplies its buffer address through `VkBindIndexBufferIndirectCommandEXT`. | [index-buffer token setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L638-L749), [token layout](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1123-L1130) |

### Exact registered test cases

The following names are the exact registered suffix combinations under the two direct test families. The `dgc.` prefix is omitted only to keep the list readable; each line is the suffix after `dEQP-VK.`.

```text
dgc.ext.graphics.draw_count.token_draw_count.pipelines
dgc.ext.graphics.draw_count.token_draw_count.pipelines_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_execution_set_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.pipelines_unordered
dgc.ext.graphics.draw_count.token_draw_count.pipelines_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_execution_set_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_unordered
dgc.ext.graphics.draw_count.token_draw_count.shader_objects_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_same_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_preprocess_separate_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_execution_set_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_same_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_preprocess_separate_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.pipelines_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_same_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_preprocess_separate_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_execution_set_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_same_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_preprocess_separate_state_cmd_buffer_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_unordered
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_unordered_check_draw_params
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_unordered_check_draw_params_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_unordered_with_index_buffer_token
dgc.ext.graphics.draw_count.token_draw_indexed_count.shader_objects_with_index_buffer_token
```

## Behavior Parameters

The primary behavioral axis is the registered test family and its action token. The suffixes in the exact-case list configure the same draw-count mechanism and are covered as variation dimensions.

### token_draw_count: non-indexed count token

The layout ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_COUNT_EXT`. Each sequence's count record points to `VkDrawIndirectCommand` structures. The test compares the resulting coverage and instance-derived color against the host reference.

### token_draw_indexed_count: indexed count token

The layout ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_COUNT_EXT`. Each sequence's count record points to `VkDrawIndexedIndirectCommand` structures. The generated commands use `firstIndex` to select each chunk's index range, reverse the vertex traversal through the index buffer, and add a different `vertexOffset` to each chunk, so the test also checks `indexCount`, `firstIndex`, `vertexOffset`, `firstInstance`, and index-buffer selection.

### token_draw_indexed_count with `_with_index_buffer_token`: indirect index-buffer binding

This action form adds `VK_INDIRECT_COMMANDS_TOKEN_TYPE_INDEX_BUFFER_EXT` before the indexed count token. Each sequence receives a `VkBindIndexBufferIndirectCommandEXT` containing a device address, the index-buffer size, and `VK_INDEX_TYPE_UINT32`. The indexed draw then obtains its index-buffer state from the generated stream instead of only from the pre-bound command-buffer state.

## Shader Analysis

The vertex and fragment shaders are generated as GLSL strings by `initDrawCountPrograms` rather than loaded from standalone shader files. The vertex shader passes `gl_InstanceIndex` and, when requested, `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance`. Execution-set cases generate four shader pairs with 8, 12, 16, and 20 flat integer interface values. The fragment shader turns those values into the red, green, and blue validation channels described below.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.draw_count.token_draw_count.pipelines
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `token_draw_count` | The generated layout ends with the non-indexed draw-count token and expands `VkDrawIndirectCommand` records. |
| `pipelines` | A single indirect-bindable graphics pipeline supplies the vertex and fragment stages; no execution-set selection or shader-object state is used. |
| no preprocessing, ordered sequences, no draw-parameter check | This is the minimal path: generated execution consumes the four count records directly, and the shader validates instance-derived color and clipping/culling. |

#### Purpose

This shader pair makes the non-indexed count-token result visible in the framebuffer. The vertex stage forwards the per-instance value and clip/cull inputs, while the fragment stage encodes the instance value in red and emits the expected green and blue channels.

#### Structural Design

| Stage | Input | Operation | Output used by validation |
|-------|-------|-----------|---------------------------|
| Vertex | `inPos`, `inExtraData`, `gl_InstanceIndex` | Copy position; forward clip/cull distances and the instance index. | `gl_Position`, clip/cull filtering, flat `outInstanceIndex` |
| Fragment | flat `inInstanceIndex` | Normalize the instance index by `255.0`; keep the non-execution-set checks at their expected values. | `outColor = vec4(red, 0.0, 1.0, 1.0)` |

#### Shader Code

##### Vertex Shader

```glsl
#version 460
layout (location=0) in vec4 inPos;
layout (location=1) in vec4 inExtraData;
layout (location=0) out flat int outInstanceIndex;
out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
    float gl_ClipDistance[1];
    float gl_CullDistance[1];
};
void main (void) {
    /// The host supplies three vertices per pixel-centered triangle; the generated draw command selects the range.
    gl_Position = inPos;
    gl_PointSize = 1.0;
    /// Negative clip or cull distance values intentionally blank the corresponding reference pixel.
    gl_ClipDistance[0] = inExtraData.x;
    gl_CullDistance[0] = inExtraData.y;
    /// The fragment stage uses the flat instance value to expose each ordinary draw command's instance arguments.
    outInstanceIndex = gl_InstanceIndex;
}
```

##### Fragment Shader

```glsl
#version 460
layout (location=0) in flat int inInstanceIndex;
layout (location=0) out vec4 outColor;
void main (void) {
    /// This representative has no execution set, so the green channel's expected value is the constant zero.
    const float red   = float(inInstanceIndex) / 255.0;
    const float green = 0.0;
    /// Draw-parameter checking is disabled for this path; blue consequently remains the expected one.
    bool blueOK = true;
    const float blue  = (blueOK ? 1.0 : 0.0);
    outColor = vec4(red, green, blue, 1.0);
}
```

#### Additional Info

- The source generator emits this single vertex/fragment pair when both `useExecutionSet` and `checkDrawParams` are false; the other registered suffixes add declarations and checks rather than changing the basic non-indexed dataflow.
- `inExtraData` is a vertex attribute backed by the host-created `VertexData` array; its first two components become the built-in clip and cull distances.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `useExecutionSet` | Adds storage-buffer declarations, flat integer varyings, push-constant dimensions, and fragment accumulation for the green channel; it also generates four shader pairs. | [execution-set shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L281-L313) |
| `checkDrawParams` | Adds flat `drawIndex`, `baseVertex`, and `baseInstance` varyings plus an `ExpectedDrawParams` buffer and blue-channel comparisons. | [draw-parameter shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L315-L320), [built-in checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L342-L395) |
| `token_draw_indexed_count` | The host-side draw data changes to `VkDrawIndexedIndirectCommand`; this shader interface stays the same, while the selected vertex stream is supplied through indexed traversal. | [indexed command generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L569-L578) |

#### SPIR-V

##### Vertex Shader SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 41
; Schema: 0
               OpCapability Shader
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %inExtraData %outInstanceIndex %gl_InstanceIndex
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %inExtraData "inExtraData"
               OpName %outInstanceIndex "outInstanceIndex"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
               OpDecorate %inExtraData Location 1
               OpDecorate %outInstanceIndex Flat
               OpDecorate %outInstanceIndex Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_2 = OpConstant %int 2
%inExtraData = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
      %int_3 = OpConstant %int 3
%_ptr_Output_int = OpTypePointer Output %int
%outInstanceIndex = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %24 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %24 %float_1
         %29 = OpAccessChain %_ptr_Input_float %inExtraData %uint_0
         %30 = OpLoad %float %29
         %31 = OpAccessChain %_ptr_Output_float %_ %int_2 %int_0
               OpStore %31 %30
         %33 = OpAccessChain %_ptr_Input_float %inExtraData %uint_1
         %34 = OpLoad %float %33
         %35 = OpAccessChain %_ptr_Output_float %_ %int_3 %int_0
               OpStore %35 %34
         %40 = OpLoad %int %gl_InstanceIndex
               OpStore %outInstanceIndex %40
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 31
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %inInstanceIndex %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %red "red"
               OpName %inInstanceIndex "inInstanceIndex"
               OpName %blueOK "blueOK"
               OpName %blue "blue"
               OpName %outColor "outColor"
               OpDecorate %inInstanceIndex Flat
               OpDecorate %inInstanceIndex Location 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%inInstanceIndex = OpVariable %_ptr_Input_int Input
  %float_255 = OpConstant %float 255
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
        %red = OpVariable %_ptr_Function_float Function
     %blueOK = OpVariable %_ptr_Function_bool Function
       %blue = OpVariable %_ptr_Function_float Function
         %12 = OpLoad %int %inInstanceIndex
         %13 = OpConvertSToF %float %12
         %15 = OpFDiv %float %13 %float_255
               OpStore %red %15
               OpStore %blueOK %true
         %21 = OpLoad %bool %blueOK
         %24 = OpSelect %float %21 %float_1 %float_0
               OpStore %blue %24
         %28 = OpLoad %float %red
         %29 = OpLoad %float %blue
         %30 = OpCompositeConstruct %v4float %28 %float_0 %29 %float_1
               OpStore %outColor %30
               OpReturn
               OpFunctionEnd
```

</details>


- The host creates a 32 x 32 framebuffer and one triangle around the center of each of its 1024 pixels. It assigns the pixels to 16 pseudorandom chunks. The first 15 chunk sizes are chosen between 1 and 64 pixels, and the last chunk receives the remaining pixels.
- The host divides the chunks among four sequences. Each sequence gets a pseudorandom number of padding structures from 0 through 7. The resulting `stride` is `(padding + 1) * sizeof(VkDrawIndirectCommand)` or `(padding + 1) * sizeof(VkDrawIndexedIndirectCommand)`. `commandCount` is the number of real chunks in that sequence.
- For a non-indexed draw, each ordinary command uses three vertices per pixel, a pseudorandom instance count from 1 through 16, a `firstVertex` at the start of its chunk, and a `firstInstance` selected from multiples of 16 through 240. For an indexed draw, the command uses the same count and instance values, a chunk-specific negative `vertexOffset`, and the reversed index data.
- A count record stores the sequence buffer address, its stride, and its chunk count. The test passes the largest sequence count, sometimes doubled, to preprocessing memory requirements. The execution info uses the framebuffer pixel count as `maxDrawCount`, so the count record's `commandCount` remains the effective limit for these generated sequences.
- The layout adds an execution-set token first when selected, an index-buffer token for `_with_index_buffer_token`, and the count action token last. The pipeline path binds the first pipeline before generated execution. The shader-object path binds the initial shader objects and shader-object state.
- With explicit preprocessing, `vkCmdPreprocessGeneratedCommandsEXT` runs either in the main command buffer or in a separate state command buffer. The separate path uses a preprocess-to-execute barrier before the main command buffer executes the generated commands.
- The host clears the color image, begins a render pass or dynamic rendering, executes the generated commands, copies the image to a host-visible buffer, waits for the queue, and builds a reference image from the same draw structures.
- Red is `gl_InstanceIndex / 255.0`. Green is zero when the execution-set shader's accumulated descriptor value matches the expected value for that pixel. Blue is one when all enabled draw-parameter values match. Negative clip or cull distance leaves the corresponding pixel at the clear color.
- Indexed reference pixels use the reverse traversal used by the index buffer. The final image comparison uses a per-channel threshold of `0.005` and fails with `Unexpected result found in color buffer; check log for details` when the images differ.

## Runtime Execution and Result Checking

- `testDrawCountRun` creates the 32 x 32 color image and host-visible readback buffer, records the render-pass or dynamic-rendering commands, and executes the generated commands through `vkCmdExecuteGeneratedCommandsEXT`. The selected pipeline or shader-object state is bound before execution; explicit-preprocessing variants call `vkCmdPreprocessGeneratedCommandsEXT` first, using a separate state command buffer when selected. ([command-buffer flow](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1205-L1412))
- Before execution, the host clears the image and prepares the generated-command streams. Each stream contains the optional execution-set token, the optional indirect index-buffer token, and the draw-count action token. After execution, the image is copied to host-visible memory and the queue is waited on before validation. ([layout and execution setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1103-L1173), [command-buffer flow](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1205-L1412))
- The reference image is built from the same chunk and ordinary draw structures used to populate the count records. It accounts for indexed reverse traversal, clip and cull distances, instance-derived red values, execution-set descriptor values in green, and optional draw-parameter checks in blue. ([render validation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1415-L1464))
- The result check compares the readback and reference images per channel with a threshold of `0.005`. A mismatch throws `Unexpected result found in color buffer; check log for details`; unsupported feature, property, extension, or limit requirements are handled earlier as test-case skips. ([support checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L187-L210), [render validation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1415-L1464))

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `token_draw_count` | Count-token expansion of `VkDrawIndirectCommand` data, including command count, stride, and non-indexed draw arguments. |
| `token_draw_indexed_count` without `_with_index_buffer_token` | Count-token expansion of `VkDrawIndexedIndirectCommand` data, indexed traversal, `vertexOffset`, and the pre-bound index buffer. |
| `token_draw_indexed_count` with `_with_index_buffer_token` | Count-token expansion together with device-addressed index-buffer binding from `VkBindIndexBufferIndirectCommandEXT`. |

A suffix variant can also expose a failure in the selected pipeline or shader-object path, execution-set selection, preprocessing order, unordered sequence processing, or draw-parameter built-ins. The image comparison reports the visible consequence, so it does not identify one of those mechanisms by itself.

### Cause Analysis

#### Count record or draw argument processing

**Possible failure symptoms:** Pixels are missing or covered by the wrong chunk, red values do not match the selected instance arguments, or the image comparison fails in both indexed and non-indexed cases.

**Possible implementation causes:** The implementation may read the count record with the wrong address or stride, use the wrong number of ordinary draw structures, or misinterpret fields in `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand`. The source and Vulkan device-generated-command semantics support this mapping; the failing image region is needed to distinguish these cases.

#### Indexed state and vertex traversal

**Possible failure symptoms:** Indexed cases show reversed or shifted coverage, or the blue channel fails when `vertexOffset` is checked. Cases without the index-buffer token can also fail if the pre-bound index buffer is not used correctly.

**Possible implementation causes:** The implementation may apply `vertexOffset` incorrectly, read the reversed indices in the wrong order, or fail to bind the index buffer selected by `VkBindIndexBufferIndirectCommandEXT`. Further source or implementation investigation is needed to separate the indexed action from index-buffer state handling.

#### Execution-set shader state or descriptor data

**Possible failure symptoms:** The green channel becomes one in pixels belonging to an execution-set sequence, or the output changes when the sequence order is marked unordered.

**Possible implementation causes:** The generated execution-set index may select the wrong pipeline or shader pair, or the selected state may not use the sequence's descriptor bindings. The test source establishes the expected per-sequence sums and interface sizes; a precise driver or compiler cause requires implementation investigation.

#### Preprocessing and sequence ordering

**Possible failure symptoms:** A case fails only with one preprocessing suffix or only with `_unordered`, while the corresponding non-preprocessed or ordered case passes.

**Possible implementation causes:** The implementation may fail to preserve generated-command state between preprocessing and execution, mishandle the required synchronization for a separate state command buffer, or rely on a sequence order that the unordered layout does not guarantee. The source identifies these as distinct execution paths, but does not assign a failure to a specific implementation layer.

#### Draw-parameter built-ins

**Possible failure symptoms:** The blue channel is zero in `_check_draw_params` cases while the red coverage still matches.

**Possible implementation causes:** Generated execution may expose the wrong draw index, base vertex or vertex offset, or base instance to the vertex shader. The test requires `VK_KHR_shader_draw_parameters` for these cases. The source does not establish whether a mismatch originates in command generation, shader built-in handling, or compilation.

## Case Pruning

### Requirement-based pruning

- `checkDGCExtSupport` requires the EXT device-generated-command support used by the graphics stages and checks `deviceGeneratedCommandsMultiDrawIndirectCount`. A device without multi-draw indirect count support cannot run either count-token family.
- Shader-object cases require `VK_EXT_shader_object`. Execution-set shader-object cases also require a nonzero `maxIndirectShaderObjectCount`.
- `_check_draw_params` cases require `VK_KHR_shader_draw_parameters`.
- The indexed index-buffer-token cases allocate device-addressable indirect index buffers and use `VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT` together with index-buffer and shader-device-address usage. Unsupported required functionality causes the case to be skipped rather than counted as a rendering failure.

### Design-based pruning

- The registration matrix uses `DRAW_INDEXED_COUNT` for indexed draws with pre-bound index-buffer state and `DRAW_INDEXED_COUNT_INDEX_TOKEN` for the `_with_index_buffer_token` form. The index-buffer suffix is not generated for `token_draw_count`.
- The implementation always uses four sequences and 16 chunks. It does not add a separate zero-count family. The count values are the sequence chunk counts, while random padding changes the stride without adding executable draw structures.
- `unordered` changes the processing-order guarantee but does not change the reference image. The test therefore keeps it as a suffix variation instead of defining a different expected result.

## Key Takeaways

- A count token points to an array of ordinary draw commands through a device address, stride, and command count. It is not itself the per-draw command structure.
- The indexed family tests both indexed draw arguments and reverse index traversal. `_with_index_buffer_token` additionally tests generated index-buffer binding.
- Four padded sequences and the optional unordered flag make sequence addressing and order observable without changing the final image.
- The rendered image checks coverage, instance values, execution-set shader data, and optional draw-parameter built-ins in separate color channels.
- Feature and limit checks prune unsupported cases before rendering. A rendered mismatch is therefore evidence about one of the exercised command, state, shader, preprocessing, or validation paths, not an expected skip.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType`, `PreprocessType`, and `TestParams` | [parameter definitions](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L138-L185) | Defines the test family and suffix-controlled behavior. |
| `checkDrawCountSupport` | [support checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L187-L210) | Defines feature and property pruning. |
| `initDrawCountPrograms` | [generated GLSL](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L276-L399) | Defines shader interfaces and validation channels. |
| `testDrawCountRun` geometry and sequences | [draw data generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L447-L635) | Creates pixel triangles, chunks, padded sequence buffers, and ordinary draw data. |
| Indexed data and count records | [indexed and token data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L638-L749) | Defines reverse indices, index-buffer records, addresses, strides, and counts. |
| Command layout and execution set | [layout construction](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1103-L1173) | Defines token order and pipeline or shader selection. |
| Preprocess and execute | [command-buffer flow](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1205-L1412) | Defines preprocessing, synchronization, rendering, and generated execution. |
| Reference image and result check | [render validation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1415-L1464) | Defines the expected pixels and comparison threshold. |
| Registration function | [registered variants](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1469-L1522) | Defines the two direct children and all 144 generated names. |
| `VkDrawIndirectCountIndirectCommandEXT` | [count record semantics](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L701-L723) | Defines `bufferAddress`, `stride`, and `commandCount`. |
| EXT token processing | [sequence and token processing](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L929-L977) | Defines token offsets, sequence order, and stateless action processing. |
| Preprocess memory requirements | [count clamping](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L1827-L1872) | Defines `maxDrawCount` for count-type multi-draw tokens. |
