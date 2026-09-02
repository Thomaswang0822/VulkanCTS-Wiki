# Understanding Brief: ComputeLayoutExt

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` correctly applies compute command-layout tokens to push constants, execution-set selection, sequence indices, and dispatch parameters across pipeline, shader-object, dynamic-layout, descriptor-heap, and queue variants.

## Background Knowledge

### Device-generated command layouts

A `VkIndirectCommandsLayoutEXT` describes one generated-command sequence as ordered tokens. Each sequence reads token data at `offset` values separated by `indirectStride`; the action token must be last. In this page's cases, `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH_EXT` is the action token, while push-constant, sequence-index, and execution-set tokens establish the compute state it consumes.

Why it matters here:
- The test changes token order, token offsets, and token data transport while keeping the final action a dispatch.
- A token's layout-time push-constant range determines where generated data updates shader-visible state.

### Compute dispatch and shader-visible state

A compute dispatch runs `local_size_x = 64` invocations per workgroup. `VkDispatchIndirectCommand` supplies the workgroup counts, while the generated push-constant or execution-set tokens supply per-dispatch values. An execution set selects a pipeline or shader object by index; specialization constants bake some per-dispatch values into those objects.

Why it matters here:
- The shader computes an output index from dispatch, workgroup, and invocation coordinates, so each generated sequence can be checked independently.
- Pipeline and shader-object paths carry equivalent compute behavior through different Vulkan objects.

## One Concrete Example

Consider the registered case `dEQP-VK.dgc.ext.compute.layout.push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap`. It uses shader objects, a compute queue, a dynamically supplied pipeline layout, and `VK_EXT_descriptor_heap`, but no execution-set token. One generated sequence supplies three `uint` values through a push-data token followed by a dispatch token:

```glsl
// Conceptual excerpt; the CTS constructs the complete source string.
layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0, std430) buffer StorageBlock { uint values[]; } storageBuffer;
layout(push_constant, std430) uniform PushConstantBlock {
    uint dispatchOffset;
    uint skipIndex;
    uint valueOffset;
} pc;
```

For each invocation, the shader writes `valueOffset + (workGroupIndex << 10) + gl_LocalInvocationIndex` to `dispatchOffset + workGroupIndex * 64 + gl_LocalInvocationIndex`, except for the selected `skipIndex`. The host later compares every output element with the same formula.

## End-to-End Test Flow

```text
[host] select one of nine TestType values and four Boolean feature/transport dimensions
[host] generate four workgroup counts in the inclusive range 1..16 using a TestType-derived deterministic seed
[host] generate one SpecializationData record per dispatch: dispatchOffset, skipIndex, and valueOffset
[host] create a zeroed host-visible output buffer and bind it through a descriptor set or descriptor heap
[host] generate the compute GLSL program and create one pipeline/shader or one per-dispatch execution-set entry
[host] build an indirect commands layout with state tokens followed by VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH_EXT
[host] write the per-dispatch token data and allocate a preprocess buffer from vkGetGeneratedCommandsMemoryRequirementsEXT
[host] update any indirect execution set after its memory requirements are queried
[host] bind the descriptor state and an initial compute pipeline or shader object
[host] execute vkCmdExecuteGeneratedCommandsEXT with four sequences
[device] process each sequence's tokens and run 64-invocation workgroups for its indirect dispatch dimensions
[device] write expected-value encoding into the output storage buffer, leaving one selected invocation at zero
[host] apply a shader-write-to-host-read barrier, invalidate the allocation, and read back the output buffer
[host] compare every element and return pass only when all values match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` emits one GLSL compute source named `comp`. The source always uses three per-dispatch values and conditionally adds a complementary value or sequence index according to `TestType`.
- `SpecializationData` supplies `dispatchOffset`, `skipIndex`, and `valueOffset`. Execution-set cases specialize pipeline or shader-object entries; push-only cases transport the record through generated push tokens.
- `makeCommandsLayout()` builds the token sequence. It always appends the dispatch token last, and it selects push-constant versus push-data tokens, sequence-index tokens, pipeline tokens, or shader-object tokens from the case dimensions.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible output buffer | yes | yes, through descriptor set or descriptor heap | written by compute shader | yes | Stores one `uint` per invocation for validation. |
| Descriptor set | yes, non-heap variants | yes | used to locate output buffer | no | Supplies set 0, binding 0 in ordinary descriptor mode. |
| Descriptor heap and resource descriptor | yes, heap variants | yes | used to locate output buffer | no | Supplies the same storage-buffer binding through `VK_EXT_descriptor_heap`. |
| Indirect commands buffer | yes | read by generated-command processing | read during preprocessing/execution | no | Contains token payloads and `VkDispatchIndirectCommand` values. |
| Preprocess buffer | yes when memory requirements are nonzero | read by generated-command execution | written/read by DGC processing | no | Holds implementation-generated preprocessing data. |
| Pipeline layout or dynamic layout info | yes, except heap-only layout path | used by layout and shader/pipeline creation | controls push-constant ranges | no | Defines the state ranges addressed by generated tokens. |

## What Is Checked

- The shader writes one output value per invocation, except when `gl_LocalInvocationIndex == skipIndex`; those locations remain zero.
- For dispatch `i`, the host expects `valueOffset + (workGroupIndex << 10) + invocationIndex`, plus `valueOffset2` for complementary cases and `i` for sequence-index cases.
- The host checks all `totalNumWorkGroups * 64` output elements. Any mismatch logs its flat index, expected and actual values, dispatch index, workgroup index, invocation index, and relevant offsets, then fails the test.
- A successful run returns `tcu::TestStatus::pass("Pass")`.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` test family
>
> **Candidate values:** `push_dispatch`, `complementary_push_dispatch`, `complementary_push_index_dispatch`, `multi_push_dispatch`, `offset_execution_set_dispatch`, `execution_set_dispatch`, `execution_set_push_dispatch`, `execution_set_index_push_dispatch`, `execution_set_complementary_push_dispatch`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `push_dispatch` | Push-constant token range or per-dispatch payload was applied incorrectly; dispatch data was decoded incorrectly. |
| `complementary_push_dispatch` | Generated push data was combined with the externally pushed `valueOffset2` at the wrong offset; dispatch data was decoded incorrectly. |
| `complementary_push_index_dispatch` | Sequence-index token or complementary push range was applied at the wrong offset; dispatch data was decoded incorrectly. |
| `multi_push_dispatch` | Multiple push tokens failed to update the intended ranges or update ordering was mishandled. |
| `offset_execution_set_dispatch` | Nonzero execution-set token offset was decoded incorrectly, or the selected pipeline/shader entry was wrong. |
| `execution_set_dispatch` | Execution-set selection or per-entry specialization data was wrong. |
| `execution_set_push_dispatch` | Execution-set selection and generated push-constant updates were combined incorrectly. |
| `execution_set_index_push_dispatch` | Execution-set selection, push-constant updates, or sequence-index transport was wrong. |
| `execution_set_complementary_push_dispatch` | Execution-set selection, generated push constants, or the externally pushed complementary value was wrong. |

## Important Variations and Special Cases

- `shader_objects` changes execution-set entries from compute pipelines to `VkShaderEXT` objects and requires `VK_EXT_shader_object`; execution-set shader-object cases also require a nonzero `maxIndirectShaderObjectCount`.
- `computeQueue` selects the device's compute queue family instead of the default queue family. The generated-command sequence remains compute-only.
- `dynamicPipelineLayout` passes `VK_NULL_HANDLE` as the layout handle and chains `VkPipelineLayoutCreateInfo` into the commands-layout creation path; it requires `dynamicGeneratedPipelineLayout`.
- `destroySetLayout` is generated only for shader-object execution-set cases. The test creates a replacement layout for `VkIndirectExecutionSetShaderLayoutInfoEXT`, then destroys the original layout to exercise the lifetime rule.
- `useDescriptorHeap` replaces descriptor-set binding with `vkCmdBindResourceHeapEXT`, `VK_INDIRECT_COMMANDS_TOKEN_TYPE_PUSH_DATA_EXT`, or `VK_INDIRECT_COMMANDS_TOKEN_TYPE_PUSH_DATA_SEQUENCE_INDEX_EXT`; it requires `VK_EXT_descriptor_heap`.
- The generator skips `destroySetLayout` when no execution set exists, because that option targets execution-set shader-layout information. It also skips it for pipeline execution sets.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test types and Boolean dimensions | [TestType and TestParams](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L54-L124) | Defines the primary behavior families and matrix dimensions. |
| Generated compute shader | [initPrograms()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L253-L331) | Emits the shader declarations, index formula, and skip condition. |
| Token construction | [makeCommandsLayout()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L552-L672) | Maps each test family to token types, ranges, offsets, and final dispatch action. |
| Indirect payload encoding | [makeIndirectCommands()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L674-L780) | Encodes push data, execution-set indices, sequence-index placeholders, and dispatch dimensions. |
| Runtime and resources | [LayoutTestInstance::iterate()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L835-L1102) | Creates resources, layouts, execution sets, preprocess storage, and the generated-command call. |
| Output validation | [result checking](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1108-L1152) | Defines expected values, diagnostics, and pass/fail behavior. |
| Shared DGC helpers | [vktDGCUtilExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L68-L75) and [layout builder](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L661-L721) | Grounds support checks, token sizing, and layout creation rules. |
| DGC registration | [createDGCComputeLayoutTestsExt()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1157-L1207) | Builds the `dgc.ext.compute.layout` registration matrix. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L62-L245) | Lists the registered EXT compute layout prefixes. |
| Vulkan DGC semantics | [Device-Generated Commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines token processing, layout requirements, preprocessing, and execution semantics. |
| Vulkan dispatch semantics | [Dispatching Commands](../../../../vulkan-docs/src/chapters/dispatch.adoc#dispatching-commands) | Defines indirect dispatch dimensions and compute workgroup behavior. |

## Questions / Risk Points for User Audit

- Does the distinction between the `TestType` behavior axis and the four Boolean matrix dimensions remain clear?
- Is the descriptor-set versus descriptor-heap resource path explained without implying that the shader source changes its storage-buffer declaration?
- Does the token ordering explanation make the final dispatch action and state-update tokens clear?
- Is the output formula sufficient to explain why every generated dispatch can be checked independently?
- Should the final page show one push-only shader walkthrough, or would an execution-set case add enough contrast to justify a second walkthrough?

## Conversion Notes for Final Wiki Rewrite

- Keep `TestType` as the primary behavior axis and condense its nine values into short concept-first subsections.
- Retain the resource table's descriptor, indirect-command, preprocess, and output-buffer roles in the final page.
- Use the `push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap` case for the representative shader walkthrough because it exercises shader-object creation, descriptor-heap mapping, and dynamic layout handling without adding execution-set selection to the shader code.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write fresh cause-analysis subsections there.
- Distill the DGC layout and compute-dispatch concepts into brief `Background Knowledge` bullets rather than copying this brief's teaching scaffolding verbatim.
