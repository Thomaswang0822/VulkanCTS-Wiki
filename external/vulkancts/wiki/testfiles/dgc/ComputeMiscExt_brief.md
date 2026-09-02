## One-Sentence Test Purpose

This test family checks whether `VK_EXT_device_generated_commands` compute execution handles large command streams, push constants, descriptor layouts, execution sets, preprocessing, and queue selection while producing the expected buffer values.

## Background Knowledge

### Generated commands and execution sets

Device-generated commands let a command buffer execute a layout of command data stored in a buffer. The layout describes tokens such as a dispatch, push constants, a sequence index, or a pipeline selection. An indirect execution set supplies pipelines or shader objects that a generated command can select.

### Descriptor paths

A compute shader reaches storage buffers through a descriptor set layout and its bound descriptor sets. The tests also use `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` with `VK_EXT_descriptor_buffer`: the application can push descriptors directly, and may bind a descriptor buffer for the push-descriptor path. `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` stores small uniform data in the descriptor set instead of in a separate buffer.

## One Concrete Example

The `max_pc_range_256_partial_preprocess_with_execution_set_push_descriptor_cq` case uses a 256-byte push-constant range. The generated command stream selects a pipeline, supplies the first and last push-constant values, and dispatches one workgroup for each array element. The host pushes the middle range before execution, preprocesses the stream, and submits it to the compute queue. The shader copies each push-constant value to a storage buffer, so the host can compare every element with its expected value.

The `iubs_with_ies_multiset` case uses two 128-byte inline uniform blocks and two storage-buffer outputs. Its two generated sequences select two pipelines from an execution set. The first shader copies its inline values in order; the second copies them in reverse order. With `multiset`, the blocks occupy separate descriptor sets. Without it, both blocks share one set at different bindings.

## End-to-End Test Flow

```text
[host] select a registered parameter combination
[host] check DGC support, queue availability, required features, and relevant device limits
[host] create host-visible input and output buffers, descriptor set layouts or descriptor-buffer state, and pipeline layouts
[host] generate GLSL or load the scratch-space SPIR-V artifact, then create normal pipelines, DGC pipelines, or shader objects
[host] build an indirect commands layout and fill a DGC buffer with token data
[host] allocate a preprocess buffer when the path uses preprocessing
[host] bind descriptors and a pipeline or shader object, then execute generated commands on the selected queue
[device] run one or more compute workgroups and write the result buffer
[host] wait for completion, invalidate host allocations, and read the result buffer
[host] compare each result with the case-specific expected value and return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The large-dispatch shaders use `local_size_x=64` and an atomic increment. A push constant selects one output element, and one workgroup raises that element to `64`.
- The sequence tests use a push constant or sequence-index token followed by a `(1, 1, 1)` dispatch. The sequence-index form lets the implementation supply the sequence number to the shader.
- The push-constant-range shader uses a `local_size_x=1` workgroup. Its dispatch count equals `pcBytes / DE_SIZEOF32(uint32_t)`, and the shader copies the value indexed by `gl_WorkGroupID`.
- The multiple-set shader reads set `0`, binding `0`, and writes set `1`, binding `0`. It processes `1024` values with local size `32` and `32` workgroups.
- The inline-uniform-block shaders each process eight `uvec4` values from a 128-byte block. The second shader reverses its source index.
- The null-set-layout case loads `comp1` and `comp2` as shader objects. One copies 64 values in order and the other copies 64 values in reverse order. Its execution set is created with `pSetLayoutsInfo = nullptr`.
- The scratch-space case loads `vulkan/device_generated_commands/ScratchSpace.comp.spvasm`. The source is designed to create register pressure and non-uniform control flow that require scratch space.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Output storage buffers | Yes | Yes | Written | Yes | Hold counters, copied values, or scratch-space results. |
| Input storage buffers | Yes in `null_set_layouts_info`, `iubs`, and `descriptor_buffer_push_descriptor` | Yes | Read | No | Supply values for copy and descriptor tests. |
| Descriptor sets | Yes for ordinary descriptor paths | Yes | Used by compute shaders | No | Bind storage buffers, inline uniform blocks, or both. |
| Inline uniform blocks | Yes in `iubs` paths | Yes through descriptor sets | Read | No | Store two 128-byte shader inputs. |
| Descriptor buffer and push descriptors | Conditional in `descriptor_buffer_push_descriptor` | Yes unless `bufferlessPushDescriptors` is true | Used by compute shaders | No | Exercise the `VK_EXT_descriptor_buffer` push-descriptor path. |
| DGC buffer | Yes | Yes through device address | Read by generated-command execution | No | Stores token values for pipelines, push constants, sequence indices, and dispatches. |
| Preprocess buffer | Yes when the execution path needs it | Yes through device address | Written and consumed by DGC | No | Stores implementation-generated command state before execution. |
| Push constants | Yes through command recording or generated tokens | Yes through the pipeline layout | Read by compute shaders | No | Select output indices or carry the large push-constant array. |

## What Is Checked

- The many-dispatch and many-sequence cases expect every output element to equal `kTypicalWorkingGroupSize`, which is `64`.
- `two_cmd_buffers` checks four output elements. One ordinary dispatch handles index `0`; three generated-command sequences handle indices `1` through `3`. Every value must equal `64`.
- `null_set_layouts_info` expects the first 64 output values to copy the input in order and the second 64 to copy it in reverse order.
- `scratch_space` compares four signed output values with the fixed references `-256`, `-46`, `-327`, and `-722`.
- `max_pc_range` compares every output element with the host-built expected push-constant array. In a full case, DGC supplies the whole range. In a partial case, the host pushes the middle range and DGC supplies the first and last values.
- `multiple_sets` expects all `1024` output values to equal the corresponding input values.
- `iubs` checks two output buffers. The first preserves its input order and the second reverses it.
- `descriptor_buffer_push_descriptor` checks two 64-element regions. The output equals the initial value plus the selected pipeline's specialization-constant offset, `0` or `10000`.
- Any mismatch logs its index and expected and observed values, then returns a failing `tcu::TestStatus`.

## Behavior Parameter Identification

> **Behavior parameter:** implemented test family
>
> **Candidate values:** `execute_many`, `many_sequences`, `two_cmd_buffers`, `scratch_space`, `max_pc_range`, `multiple_sets`, `iubs`, `descriptor_buffer_push_descriptor`, `null_set_layouts_info`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `execute_many` | Incorrect handling of repeated single-sequence execution, per-execution indirect offsets, or preprocess-buffer regions. |
| `many_sequences` | Incorrect sequence-index handling or generated dispatch execution across a large sequence count. |
| `two_cmd_buffers` | Incorrect interaction between ordinary and generated dispatches, command-buffer submission, or the optional pipeline execution set. |
| `scratch_space` | Incorrect allocation or use of implementation scratch space for a register-pressure-heavy compute pipeline. |
| `max_pc_range` | Incorrect push-constant token coverage, partial host/DGC updates, pipeline selection, preprocessing, push descriptors, or dispatch dimensions. |
| `multiple_sets` | Incorrect binding or access across two descriptor sets during generated compute execution, including preprocessing. |
| `iubs` | Incorrect inline uniform block binding, descriptor-set placement, pipeline selection, or forward/reverse shader access. |
| `descriptor_buffer_push_descriptor` | Incorrect descriptor-buffer push-descriptor state or execution-set pipeline selection. |
| `null_set_layouts_info` | Incorrect shader-object execution-set handling when `pSetLayoutsInfo` is null, or incorrect shader-object token execution. |

## Important Variations and Special Cases

- Queue suffixes `_compute_queue`, `_universal_queue`, and `_cq` select a compute-capable queue family or the test context's universal queue. The source requests the compute queue with `context.getComputeQueue()` and creates the command pool for the matching family.
- `preprocess` cases set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`, call `cmdPreprocessGeneratedCommandsEXT`, insert `preprocessToExecuteBarrierExt`, and execute with `isPreprocessed = VK_TRUE`. Other cases execute without that explicit preprocess step.
- `with_execution_set` cases use a DGC pipeline or shader-object execution set. Non-execution-set paths bind ordinary pipelines and pass the pipeline to the generated-command information.
- `push_descriptor` changes the descriptor path. The host creates a push-descriptor layout and calls `cmdPushDescriptorSet`; the descriptor-buffer case also binds a descriptor buffer unless `bufferlessPushDescriptors` is supported.
- `multiset` gives the two inline uniform blocks separate descriptor sets. Without that suffix, both blocks share one set and use bindings `0` and `2`, leaving binding `1` for the corresponding output buffer.
- `full` updates the entire middle push-constant range with DGC. `partial` leaves the middle range to a normal `cmdPushConstants` call and uses DGC for the first and last elements.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test registration and matrix construction | [createDGCComputeMiscTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2519-L2617) | Defines every registered identifier and its parameter loops. |
| Repeated executions | [manyExecutesRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L346-L541) | Shows per-execution command and preprocess offsets and the `64` result check. |
| Sequence-index execution | [manySequencesRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L543-L682) | Shows the sequence-index token and large sequence-count path. |
| Null layout information | [nullSetLayoutsInfoRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L684-L890) | Shows shader-object execution with `pSetLayoutsInfo = nullptr`. |
| Scratch-space execution | [ScratchSpaceInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L892-L1147) | Loads the scratch-space shader and compares four fixed outputs. |
| Push-constant range | [MaxPushConstantRangeInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1261-L1452) | Defines full and partial token coverage, preprocess, descriptor, queue, and execution-set variants. |
| Multiple descriptor sets | [MultipleSetsInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1561-L1702) | Defines two set layouts, dispatch dimensions, preprocess, and copy checking. |
| Inline uniform blocks | [IUBUsageCase and IUBUsageInstance](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1752-L2147) | Defines `iubs`, `multiset`, execution-set, queue, and forward/reverse cases. |
| Descriptor-buffer push descriptors | [DBPDCase and DBPDInstance](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2192-L2515) | Defines descriptor-buffer and push-descriptor setup and output checking. |
| Descriptor-set semantics | [Vulkan descriptor set layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-setlayout) | Defines descriptor bindings and shader-resource interfaces. |
| Descriptor-buffer semantics | [Vulkan descriptor buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc) | Defines descriptor-buffer binding and push-descriptor behavior. |

## Questions / Risk Points for User Audit

- Does the distinction between `execute_many` and `many_sequences` make the different DGC tokens clear?
- Is the difference between ordinary descriptor sets, push descriptors, and descriptor buffers clear?
- Should the scratch-space explanation include a generated shader walkthrough in a later pass?
- Are the queue suffixes and explicit preprocess steps easy to map to the registered names?
- Is the `null_set_layouts_info` failure mapping sufficiently explicit about shader-object layout information?

## Conversion Notes for Final Wiki Rewrite

- Keep the matrix grouped by implemented test family, then show the exact direct child names in the registration tree.
- Carry the family axis and failure mapping into the final page.
- Keep the resource table focused on descriptor paths, DGC buffers, preprocess buffers, and readback buffers.
- Explain queue and preprocess suffixes in one variation subsection instead of repeating them for every generated identifier.
- Preserve the fixed output values and source links. Add shader walkthrough artifacts only if the required shader-analysis workflow is available.
