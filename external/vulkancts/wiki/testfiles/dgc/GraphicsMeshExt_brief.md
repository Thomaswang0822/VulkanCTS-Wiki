# Understanding Brief: GraphicsMeshExt

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` executes generated mesh-task draws and produces the pixels or buffer values that those draws should produce across pipeline, preprocessing, ordering, and execution-set variants.

## Background Knowledge

### Mesh and task shader execution

A mesh shader workgroup emits vertices and primitives directly. An optional task shader runs first and calls `EmitMeshTasksEXT` to create mesh workgroups. With no task shader, the draw launches mesh workgroups directly. The mesh-shader execution model is described in [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc).

Why it matters here:

- `VkDrawMeshTasksIndirectCommandEXT` supplies three workgroup counts. The test varies which one carries the row count.
- The test maps mesh workgroups to image rows and columns, so an incorrect count or workgroup index changes the rendered image.
- In task-shader cases, `taskPayloadSharedEXT` carries a row index and the column chosen by each mesh workgroup. The payload is shader-local shared data, not a host-created buffer.

### Generated command layout

A `VkIndirectCommandsLayoutEXT` describes state tokens followed by an action token. These cases use an optional execution-set token, a push-constant or sequence-index token, and one mesh draw token. `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` consumes `VkDrawMeshTasksIndirectCommandEXT`; the count form consumes `VkDrawIndirectCountIndirectCommandEXT` together with mesh draw records. Explicit preprocessing calls `vkCmdPreprocessGeneratedCommandsEXT` before `vkCmdExecuteGeneratedCommandsEXT`. A separate preprocessing command buffer needs an explicit barrier before execution. See [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout).

## One Concrete Example

In `dEQP-VK.dgc.ext.graphics.mesh.token_draw.monolithic`, the host creates a 32 by 32 color target and three vertices around the center of every pixel. It divides the 32 rows into eight direct sequences. Each generated sequence supplies a push-constant value and one mesh draw record. The mesh shader finds its row, emits the matching triangles, and passes red and green values to the fragment shader. The fragment shader adds the selected blue value and writes the color target.

With a task shader, one task workgroup has 16 invocations. Each invocation writes two column indices to `TaskData`, and the task shader launches the number of mesh workgroups selected by the row's coverage value. Each mesh workgroup emits one triangle for its selected column.

## End-to-End Test Flow

```text
[host] choose draw form, pipeline construction, preprocessing, task-shader, execution-set, and sequence-order values
[host] create the 32 by 32 color target and storage, generated-command, and optional preprocess buffers
[host] generate fragment, mesh, and optional task GLSL programs
[host] build pipeline or shader-object state and the DGC layout
[host] fill push-constant and mesh-draw token data, including group counts
[host] optionally preprocess the stream in the selected command-buffer arrangement
[host] begin rendering and execute the generated mesh commands
[device] run the task shader when selected, then run mesh workgroups and the fragment shader
[device] write rendered colors or no-fragment output values
[host] copy or invalidate the result allocation and construct the expected values
[host] compare the result and decide pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `DGCMeshDrawCase::initPrograms` generates fragment, mesh, and optional task GLSL programs. Execution-set cases generate alternate shader programs for the red, green, and blue values and for task column order.
- The regular DGC layout contains an optional `VK_INDIRECT_COMMANDS_TOKEN_TYPE_EXECUTION_SET_EXT` token, a push-constant or sequence-index token, and either `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` or `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_COUNT_EXT`.
- Explicit-preprocess variants set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` and execute with preprocessing enabled.
- `NoFragCase` generates mesh and optional task programs that write integer values to storage buffers while emitting no rasterized primitives.
- `manySequencesRun` generates one mesh program and an optional task program for sequence counts `64`, `1024`, `8192`, and `131072`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| 32 by 32 `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | yes | fragment shader writes it | yes, through a copy buffer | Carries the regular rendered result. |
| Vertex storage buffer | yes | yes, set `0`, binding `0` | mesh shader reads it | no | Supplies three vertices plus clip and cull distances for each pixel triangle. |
| Base-row storage buffer | yes | yes, set `0`, binding `1` | mesh and task shaders read it | no | Maps each sequence or indirect draw to its first image row. |
| Coverage storage buffer | yes, for task-shader cases | yes, set `0`, binding `2` | task shader reads it | no | Selects the number of columns covered by each row. |
| Generated-command buffer | yes | yes through DGC | DGC reads it | no | Holds execution-set, push-constant, sequence, and mesh-draw token data. |
| Preprocess buffer | yes, for preprocess cases | yes through DGC | DGC writes and reads it | no | Carries generated state from preprocessing to execution. |
| Output storage buffer | yes, for `misc` no-fragment and many-sequence cases | yes | task or mesh shader writes it | yes | Records integer results when no color attachment is used. |
| `TaskData` payload | no, shader-local | no host binding | task shader writes it and mesh shader reads it | no | Carries row and column mapping between task and mesh workgroups. |

## What Is Checked

The regular cases clear the color target, build a reference image from the generated row and column mapping, copy the rendered image to host-visible memory, invalidate the allocation, and compare the images with `tcu::floatThresholdCompare`. The threshold is `0.005` for RGB and `0.0` for alpha. A mismatch calls `TCU_FAIL("Unexpected results in color buffer; check log for details")`.

The reference accounts for clip and cull distances, task coverage, reversed task column order, and the execution-set color selected for the sequence. Count-form cases resolve the direct draw index through the grouped indirect records and their strides.

The no-fragment cases compare each storage-buffer element with the value derived from the sequence's push constant, workgroup index, and local invocation index. The many-sequence cases require one count of `64` per sequence entry. A mismatch calls `TCU_FAIL` after logging the first-class buffer differences.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `token_draw`, `token_draw_count`, `misc`, `conditional_rendering`

The test family is the primary behavioral axis. `token_draw` checks `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT`, `token_draw_count` checks the count form and grouped indirect records, `misc` checks no-fragment and many-sequence paths, and `conditional_rendering` is registered here but implemented by the related conditional-rendering source file.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `token_draw` | Incorrect `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` decoding, push-constant or execution-set selection, mesh/task workgroup mapping, preprocessing, sequence ordering, rasterization, or image checking. |
| `token_draw_count` | Incorrect `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_COUNT_EXT` decoding, indirect count or stride handling, grouped draw mapping, mesh/task execution, preprocessing, rasterization, or image checking. |
| `misc` | Incorrect no-fragment pipeline path, large sequence handling, mesh/task storage-buffer writes, or related DGC execution. |
| `conditional_rendering` | Conditional rendering incorrectly controls the delegated generated mesh draw or preprocessing path. |

## Important Variations and Special Cases

- `drawType` registers direct `token_draw` cases and indirect `token_draw_count` cases. Direct cases use eight sequences. Indirect cases group those eight direct draws into four indirect draws and vary each indirect buffer's stride.
- `pipelineType` registers `monolithic`, `shader_objects`, `gpl_fast`, `gpl_optimized`, `gpl_mix_base_fast`, and `gpl_mix_base_opt`. The two GPL mix forms are registered only with an execution set.
- `preprocessType` registers no preprocessing, `_preprocess_same_state_cmd_buffer`, and `_preprocess_separate_state_cmd_buffer`.
- `taskShader` adds `_with_task_shader`. Task variants choose coverage per row and can reverse column order when an execution set selects the alternate task shader.
- `useExecutionSet` adds `_with_execution_set`. It selects pipeline or shader-object state per sequence and changes the expected colors.
- `unorderedSequences` adds `_unordered` and sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`. The reference derives colors from sequence data instead of assuming processing order.
- `misc` registers `no_frag_shader_` cases for `monolithic`, `shader_objects`, and `gpl_fast`, with `_with_task`, `_with_ies`, and `_preprocess` combinations, plus `many_sequences_64`, `many_sequences_1024`, `many_sequences_8192`, and `many_sequences_131072`, each with an optional `_task` suffix.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test mechanism and mesh/task design | [test mechanism](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L61-L149) | Defines the row, pixel, workgroup, task payload, and count-token model. |
| Parameters and support checks | [TestParams and support](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L218-L369) | Defines execution dimensions and required `VK_EXT_mesh_shader`, shader-object, and multi-draw support. |
| Generated programs | [`DGCMeshDrawCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L376-L561) | Generates the fragment, mesh, and task programs. |
| Main runtime and image check | [`DGCMeshDrawInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L610-L1547) | Creates resources, executes DGC, builds the reference image, and compares copyback. |
| No-fragment path | [`NoFragCase` and `NoFragInstance`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1549-L2088) | Covers storage-buffer output with optional task shaders, execution sets, and preprocessing. |
| Many-sequence path | [`manySequencesRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2090-L2316) | Covers sequence counts from `64` through `131072` and checks one counter per sequence. |
| Registration | [`createDGCGraphicsMeshTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2320-L2424) | Registers the four direct children and exact variant loops. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L1806-L2113) | Lists the 308 registered mesh paths. |
| Mesh shader execution model | [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | Defines task and mesh workgroup execution and emitted primitives. |
| DGC token and preprocessing rules | [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout) | Defines mesh action tokens, explicit preprocessing, and sequence ordering. |

## Questions / Risk Points for User Audit

- Is the distinction between `token_draw` and `token_draw_count` clear without enumerating all 120 leaves in each family?
- Is the task payload, coverage, and reversed-column mapping clear enough to explain missing pixels?
- Does the reference-image description explain execution-set colors and unordered sequence handling?
- Should the no-fragment and many-sequence `misc` cases receive separate final-page subsections?

## Conversion Notes for Final Wiki Rewrite

- Use the four direct registered children in the hierarchy, marking `conditional_rendering` as registration-only because its implementation is delegated.
- Keep all execution dimensions and exact suffixes in the final parameter table. Use `token_draw` as the representative shader path.
- Copy the failure mapping table directly into the final page. Write fresh cause analysis for token decoding, mesh/task execution, preprocessing and ordering, and host-side result checking.
- Distill the mesh/task execution model into concise Background Knowledge and Shader Analysis prose. Keep the complete source links in the appendix.
