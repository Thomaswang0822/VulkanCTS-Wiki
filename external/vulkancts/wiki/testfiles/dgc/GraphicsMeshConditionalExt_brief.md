# Understanding Brief: GraphicsMeshConditionalExt

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` executes mesh shader draws only when `VK_EXT_conditional_rendering` permits them, while explicit preprocessing remains independent of the conditional predicate.

## Background Knowledge

### Conditional rendering

A conditional rendering block reads a 32-bit predicate from a buffer. A zero predicate suppresses affected rendering commands, while a nonzero predicate permits them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision. The Vulkan specification describes the predicate and inversion rules in [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2090-L2167).

Why it matters here:
- The test places `vkCmdExecuteGeneratedCommandsEXT` inside the block, so the expected image depends on the effective predicate.
- The preprocess path places `vkCmdPreprocessGeneratedCommandsEXT` inside the block but expects preprocessing to complete for either predicate value.

### Mesh and task shader execution

A mesh shader workgroup emits primitives for later graphics stages. With a task shader, task invocations emit mesh workgroups and can pass payload data to them. Without a task shader, the draw directly launches mesh workgroups. The relevant execution model and `OpEmitMeshTasksEXT` / `OpSetMeshOutputsEXT` rules are in [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L8-L23).

Why it matters here:
- The generated graphics command is a `VkDrawMeshTasksIndirectCommandEXT`.
- The mesh shader writes one point per output pixel, which makes command suppression visible as an all-clear or all-blue image.

## One Concrete Example

Consider `dEQP-VK.dgc.ext.graphics.mesh.conditional_rendering.general.classic_bind_without_count_buffer_condition_true`. The host writes `1024` to the conditional-rendering buffer, does not invert the predicate, binds the ordinary graphics pipeline, and executes one generated mesh draw. The effective predicate is true, so the mesh shader runs and the fragment shader fills the 2 by 4 color image blue.

For the corresponding false condition, the host writes `0`. The conditional block suppresses the generated draw, and the image remains the cleared value. This example is conceptual but uses the exact source values and extent from the implementation.

## End-to-End Test Flow

```text
[host] choose general or preprocess parameters
[host] create the 2 by 4 color target, vertex storage buffer, descriptor set, push-constant layout, and predicate buffer
[host] generate mesh and fragment GLSL; add DGC push-constant and mesh-draw tokens
[host] write the predicate as 1024 or 0 and set the inverted flag when requested
[host] preprocess generated commands when the test family is preprocess
[host] record conditional rendering around preprocessing or generated-command execution
[device] evaluate the conditional predicate and, when permitted, run the generated mesh draw
[device] emit blue points or leave the color target cleared
[host] copy the image to a host-visible buffer and compare every pixel with the expected image
[host] return pass or fail from the exact image comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The common generator emits a fragment shader that copies a push-constant `vec4` to `outColor`.
- It emits a mesh shader with `layout(points)`, a fixed output budget, `SetMeshOutputsEXT`, and a storage-buffer lookup for each vertex position.
- The task-shader variant emits `EmitMeshTasksEXT(1, 1, 2)` and passes a row base through `taskPayloadSharedEXT`.
- The general DGC layout contains a push-constant token and a mesh-draw token. When `pipelineToken` is true it also contains an execution-set token.
- The preprocess layout sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` and is executed with `isPreprocessed = VK_TRUE`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| 2 by 4 `VK_FORMAT_R8G8B8A8_UNORM` color image and copy buffer | yes | yes | written by fragment output and transfer | yes | distinguishes blue execution from clear-color suppression |
| host-visible vertex storage buffer | yes | yes at set 0, binding 0 | read by mesh shader | no | supplies one clip-space point position per pixel |
| host-visible conditional-rendering buffer | yes | yes through `VkConditionalRenderingBeginInfoEXT` | read as predicate | no | controls the effective conditional decision |
| generated commands buffer | yes | yes through `DGCGenCmdsInfo` | read during preprocess or execute | no | carries push-constant data and `VkDrawMeshTasksIndirectCommandEXT` |
| preprocess buffer | yes | yes through `DGCGenCmdsInfo` | written/read by DGC preprocessing | no | stores the explicit-preprocess result |
| push constant | yes | yes through pipeline layout and DGC token | read by fragment shader | no | selects blue output |
| task payload `td` | no, shader-local | no host binding | written by task shader and read by mesh shader | no | transfers the row base only in task-shader variants |

## What Is Checked

The host constructs a reference image with either the blue push-constant value `(0, 0, 1, 1)` or the clear value `(0, 0, 0, 1)`. The choice is `conditionValue != inverted` in both runtime functions. The test copies the color image to a buffer and calls `tcu::floatThresholdCompare` with a zero threshold. Any pixel mismatch raises `TCU_FAIL`; an exact comparison returns `Pass`.

For the preprocess family, both the preprocess command and the later execution command use the same condition parameters. The source comment states that these tests check that conditional rendering does not affect preprocessing, and the final image still follows the predicate at execution.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `general`, `preprocess`

The test family is the primary behavioral axis because `general` asks whether conditional rendering suppresses generated mesh execution, whereas `preprocess` asks whether conditional rendering changes the preprocessing operation before the later execution.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `general` | Conditional rendering did not suppress or permit generated mesh execution according to `conditionValue` and `inverted`; DGC token execution, pipeline binding, mesh shader generation, descriptor access, or image checking may also be wrong. |
| `preprocess` | Conditional rendering incorrectly changed explicit preprocessing, the preprocess and execute predicates did not match, or the generated mesh execution/result path failed after preprocessing. |

## Important Variations and Special Cases

- `pipelineToken` selects classic binding or an indirect execution-set pipeline token. It changes the DGC layout and support query, but not the expected image.
- `indirectCountBuffer` selects a one-element sequence-count buffer. The test advertises 256 potential sequences to preprocessing while the count buffer limits execution to one sequence.
- `conditionValue` writes `1024` for true and `0` for false. The implementation avoids using the value `1` but relies only on zero versus nonzero semantics.
- `inverted` adds `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` and reverses the expected image choice.
- `hasTask` selects the task-plus-mesh path or the direct mesh path. It changes shader stages and vertex indexing, not the conditional-rendering rule.
- The preprocess family fixes the pipeline-token, count-buffer, and task-shader choices to the direct mesh path and varies only `conditionValue` and `inverted`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| parameter structs and support gates | [vktDGCGraphicsMeshConditionalTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L60-L117) | Defines the general and preprocess parameter dimensions and required extensions. |
| generated task, mesh, and fragment programs | [onePointPerPixelPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L119-L214) | Shows the shader text and task/no-task branches. |
| general runtime and expected image | [conditionalDispatchRun](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L281-L496) | Shows resource setup, conditional execution, DGC layout, and result comparison. |
| preprocess runtime and expected image | [conditionalPreprocessRun](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L499-L672) | Shows explicit preprocessing under conditional rendering and the execution-time check. |
| registration loops | [createDGCGraphicsMeshConditionalTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L676-L727) | Defines the registered children and exact generated test-name matrix. |
| DGC token and preprocessing semantics | [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L968-L1006) | Defines token input data and explicit preprocessing behavior. |

## Questions / Risk Points for User Audit

- Is `general` versus `preprocess` the clearest primary behavior axis for this page?
- Should the final page show one no-task mesh shader walkthrough, or should a task-shader case replace it as the representative?
- Is the distinction between the predicate controlling execution and the predicate being required to match across preprocess and execute clear?
- Are the pipeline-token and indirect-count variants described as configuration dimensions rather than separate behavioral claims?

## Conversion Notes for Final Wiki Rewrite

- Use `general` and `preprocess` as the behavior subsections and copy the failure mapping table into the final page.
- Keep the final Background Knowledge concise: conditional rendering, DGC explicit preprocessing, and the mesh/task execution distinction.
- Use the no-task `classic_bind_without_count_buffer_condition_true` case for the shader walkthrough because it exposes the common mesh and fragment dataflow without adding task payload code.
- Put the full parameter matrix in `Parameter Dimensions and Observed Values`; keep the walkthrough focused on the mesh shader.
- Write Cause Analysis fresh. Tie image symptoms to conditional suppression, DGC token/resource setup, and preprocess predicate agreement.
