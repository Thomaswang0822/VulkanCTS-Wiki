## Overview

**Core question:** Does the EXT compute miscellaneous coverage execute each generated-command variant and produce the values its shader and host setup require?

This page covers the implementation behind `dgc.ext.compute.misc` in [vktDGCComputeMiscTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2519-L2617). It tests repeated generated dispatches, sequence indices, push-constant ranges, multiple descriptor sets, inline uniform blocks, descriptor-buffer push descriptors, pipeline and shader-object execution sets, and scratch-space use.

The registered cases form one implementation-bearing test family with several focused case groups. The suffixes and prefixes encode the matrix, so a reader can distinguish queue selection, preprocessing, descriptor layout, execution-set use, and the behavior under test without treating every leaf as a separate mechanism.

## Background Knowledge

- A generated-command layout maps fields in a device-addressed command stream to operations such as dispatch, push constants, sequence indices, pipeline selection, or shader-object selection. Preprocessing converts that stream into implementation-defined executable state before a later execution call.
- A descriptor set layout defines the binding interface between a compute shader and storage buffers or inline uniform blocks. `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` stores uniform bytes in the descriptor set. `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` lets the command buffer push descriptors instead of allocating a descriptor set.
- An indirect execution set supplies pipelines or shader objects that generated commands can select. The selected object changes the shader or specialization-dependent behavior while the command layout remains shared.

## Registration Hierarchy

```text
dgc.ext.compute.misc
├── execute_many_64_universal_queue
├── many_sequences_64_universal_queue
├── scratch_space
├── max_pc_range_128_full
├── multiple_sets
├── iubs
├── two_cmd_buffers
├── descriptor_buffer_push_descriptor
└── null_set_layouts_info
```

The tree shows one direct child for each implementation group. The source creates 130 executable leaves in nine implementation groups: repeated executes, many sequences, scratch space, maximum push-constant ranges, multiple sets, inline uniform blocks, two command buffers, descriptor-buffer push descriptors, and null set-layout information.

## Parameter Dimensions and Observed Values

The source constructs the matrix with these dimensions. The names in the last column are the exact registered identifiers produced by the loops.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Repeated execute count | `64`, `1024`, `8192` | Number of separate one-sequence `cmdExecuteGeneratedCommandsEXT` calls. | [repeated execute registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2525-L2533) |
| Sequence count | `64`, `1024`, `8192`, `131072` | Number of sequences executed in one generated-command call using a sequence-index token. | [sequence registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2535-L2543) |
| Push-constant range size | `128`, `256`, `4096` bytes | Size of the generated push-constant array and the resulting dispatch count. | [push-constant matrix](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2547-L2564) |
| Push-constant update coverage | `full`, `partial` | Whether DGC supplies the middle range or the host supplies it with `cmdPushConstants`. | [MaxPushConstantRangeParams](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1150-L1169) |
| Preprocessing | no suffix, `_preprocess` | Whether the case records explicit preprocessing and executes with `isPreprocessed = VK_TRUE`. | [preprocess matrix](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2547-L2564) |
| Pipeline execution set | no suffix, `_with_execution_set` | Whether generated commands select a DGC pipeline from an indirect execution set. | [execution-set matrix](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2547-L2564) |
| Descriptor path | no suffix, `_push_descriptor` | Whether the maximum push-constant case uses a push-descriptor layout and command. | [push-descriptor matrix](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2547-L2564) |
| Queue | `_cq` or `_compute_queue` versus the universal form | Selects the compute queue family or the test context queue and creates the command pool for that family. | [queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1374-L1377) |
| Inline uniform block layout | no suffix, `_multiset` | Places both blocks in one descriptor set or in separate sets. | [IUB registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2580-L2594) |
| Pipeline execution set | no suffix, `_with_ies` | Selects whether `iubs`, `two_cmd_buffers`, or `descriptor_buffer_push_descriptor` uses an indirect execution set containing DGC pipelines. | [`_with_ies` registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2580-L2612) |

The matrix has 130 leaves: 6 `execute_many`, 8 `many_sequences`, 1 `scratch_space`, 96 `max_pc_range`, 4 `multiple_sets`, 8 `iubs`, 4 `two_cmd_buffers`, 2 `descriptor_buffer_push_descriptor`, and 1 `null_set_layouts_info`.

## Behavior Parameters

The primary behavioral axis is the implemented test family. The suffixes are configuration dimensions described above; these family values change the operation being checked.

### `execute_many` family: separate generated executions

The source creates one command stream containing a push-constant token and a `(1, 1, 1)` dispatch. It then calls `cmdExecuteGeneratedCommandsEXT` once per requested execution, using a different command-buffer offset and preprocess-buffer region for each call. Each shader invocation atomically increments the output element selected by the push constant.

### `many_sequences` family: sequence-index token

This family puts a sequence-index token and a dispatch token in one stream, then executes up to `131072` sequences in one call. Each sequence targets one output element. The sequence-index token supplies the index that the shader uses for its atomic increment.

### `two_cmd_buffers` family: ordinary and generated dispatches

The source records one ordinary dispatch in one command buffer and three generated sequences in a separate command buffer, then submits both buffers together. The ordinary dispatch uses the default push-constant index `0`; generated sequences use indices `1` through `3`. Each workgroup contributes 64 atomic increments to its selected output element, so every element must contain `64`. The optional `_with_ies` form adds a pipeline token and selects a DGC pipeline through an execution set.

### `scratch_space` family: register-spill support

The case loads `ScratchSpace.comp.spvasm`, a four-invocation shader with high register pressure and non-uniform control flow. The generated stream selects the pipeline and dispatches one workgroup. The fixed signed output values provide the reference for the shader computation while the pipeline uses implementation scratch space.

### `max_pc_range` family: generated and host push-constant ranges

The shader reads a push-constant array and writes the value indexed by its workgroup. The range sizes `128`, `256`, and `4096` bytes produce corresponding dispatch sizes of `32`, `64`, and `1024` workgroups. In a `full` case, DGC writes the first, last, and middle portions. In a `partial` case, the host writes the middle portion and DGC writes the endpoints. The other suffixes combine this behavior with preprocessing, an execution set, push descriptors, and the compute queue.

### `multiple_sets` family: two descriptor sets

The pipeline layout contains two sets with the same single storage-buffer binding. Set `0` supplies the input and set `1` receives the output. The shader uses local size `32` and dispatches `32` workgroups to copy `1024` values. The `_preprocess` and `_cq` forms change execution mode and queue, not the copy rule.

### `iubs` family: inline uniform blocks

Each of two shaders reads one 128-byte inline uniform block and writes its associated storage buffer. The first shader reads its eight `uvec4` values in order; the second reads them in reverse order. `_multiset` uses set `0`, binding `0`, and set `1`, binding `0`. Without `_multiset`, both blocks share set `0`, with bindings `0` and `2` so each output storage buffer occupies the following binding. `_with_ies` adds two pipelines to an execution set.

### `descriptor_buffer_push_descriptor` family: descriptor-buffer push path

The case uses two storage-buffer bindings in a descriptor-buffer layout that also has the push-descriptor flag. It pushes the input and output descriptors with `cmdPushDescriptorSet`. If `bufferlessPushDescriptors` is false, it also binds a descriptor buffer and sets the descriptor-buffer offset. The execution-set form selects two pipelines whose specialization constants add `0` and `10000` to the two output regions.

### `null_set_layouts_info` family: shader objects with null layout metadata

The case creates an indirect execution set for shader objects with `pSetLayoutsInfo = nullptr`, then updates its second shader object. The generated layout selects a shader object, a push-constant offset, and a dispatch. The first sequence copies 64 input values in order; the second copies the next 64 in reverse order.

## Shader Analysis

The source generates most compute shaders as GLSL strings and loads the scratch-space shader from `vulkan/device_generated_commands/ScratchSpace.comp.spvasm`. The walkthrough selects `execute_many_64_universal_queue` because its shader exposes the push-constant and dispatch-token interaction shared by the repeated-execute and many-sequence cases. The other generated shaders perform indexed copies, push-constant reads, inline-uniform-block reads, or shader-object-selected copies; their implementation links are in the source appendix.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.misc.execute_many_64_universal_queue
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `execute_many_64` | `manyExecutesRun` performs 64 separate generated-command executions. Each command record carries one push-constant index and dispatch dimensions `(1, 1, 1)`. |
| `universal_queue` | The case uses the context's ordinary queue and queue-family index instead of `context.getComputeQueue()`. |

#### Purpose

The generated compute shader increments one output element per local invocation. Each separate generated execution supplies a different element index through a push constant, so the host expects every one of the 64 elements to contain `64`.

#### Structural Design

| Phase | Source-generated operation | Result checked by the host |
|-------|----------------------------|-----------------------------|
| Index selection | Load `pc.valueIndex` from the push-constant block. | Select the output element for this execution. |
| Atomic update | Execute `atomicAdd(outputBuffer.values[pc.valueIndex], 1u)` for each of 64 local invocations. | Add 64 to the selected element. |
| Repeated execution | Supply indices `0` through `63` in separate command records and execute one sequence at a time. | Every output element must equal `64`. |

#### Shader Code

```glsl
#version 460
/// The source generator sets one workgroup dimension to 64 local invocations.
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
/// Binding 0 is the host-visible output storage buffer.
layout (set=0, binding=0, std430) buffer OutputBlock { uint values[]; } outputBuffer;
/// DGC writes the output element index before the dispatch token runs the workgroup.
layout (push_constant, std430) uniform PushConstantBlock { uint valueIndex; } pc;
/// All invocations atomically increment the selected output element.
void main (void) { atomicAdd(outputBuffer.values[pc.valueIndex], 1u); }
```

#### Additional Info

- `increaseValueByIndexPrograms` emits this same compute source for the `execute_many` and `many_sequences` implementations [shader generator](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L91-L103).
- `manyExecutesRun` writes the loop index followed by `(1, 1, 1)` into each command record [generated command data](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L398-L415).
- The loop passes one command record and one corresponding preprocess-buffer region to each `cmdExecuteGeneratedCommandsEXT` call [per-execution offsets](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L426-L509).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Execute count | The shader text stays fixed while the host changes the number of command records to `64`, `1024`, or `8192`. | [execute-count registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2525-L2533) |
| Queue | The shader text stays fixed; the queue variant changes queue-family selection and submission. | [queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L346-L353) |
| Command token data | The push-constant token supplies `valueIndex`; the dispatch token supplies `(1, 1, 1)` for this family. | [token layout and data](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L398-L415) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "values"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "valueIndex"
               OpName %pc "pc"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %outputBuffer Binding 0
               OpDecorate %outputBuffer DescriptorSet 0
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
     %v3uint = OpTypeVector %uint 3
    %uint_64 = OpConstant %uint 64
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0 %18
         %23 = OpAtomicIAdd %uint %20 %uint_1 %uint_0 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case performs its support checks before creating resources. General cases call `checkDGCExtComputeSupport`; cases using a compute queue request `context.getComputeQueue()`. Feature-specific cases require `VK_EXT_shader_object`, `VK_KHR_push_descriptor`, `VK_EXT_inline_uniform_block`, or `VK_EXT_descriptor_buffer` as applicable.
- The host creates host-visible output storage buffers for every family and creates input buffers where a copy or descriptor test needs them. It initializes input data, clears output data, and flushes or invalidates allocations around GPU access. It creates descriptor sets for ordinary paths, inline uniform-block descriptors for `iubs`, or descriptor-buffer and push-descriptor state for the descriptor-buffer case.
- The host creates a DGC buffer containing exact token fields. Depending on the family, those fields hold a pipeline or shader-object index, push-constant data, a sequence index placeholder, and dispatch dimensions. The dispatch dimensions are usually `(1, 1, 1)`; `max_pc_range` dispatches one workgroup per push-constant element, and `multiple_sets` dispatches `32` workgroups.
- Explicit preprocess variants set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`, call `cmdPreprocessGeneratedCommandsEXT`, insert `preprocessToExecuteBarrierExt`, and call `cmdExecuteGeneratedCommandsEXT` with `VK_TRUE`. Other paths use the preprocess buffer through the normal generated-command call.
- The host binds the ordinary or DGC pipeline and descriptor state, records generated execution, inserts a shader-write to host-read barrier, submits to the selected queue, and waits for completion.
- The host invalidates each output allocation and compares every element against the case-specific reference. A mismatch logs its position and values and returns `tcu::TestStatus::fail`; matching output returns `tcu::TestStatus::pass("Pass")`.

## Failure Meaning

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

### Cause Analysis

#### Generated command stream and preprocessing

**Possible failure symptoms:** Output elements remain at their cleared value, receive the wrong increment, or differ only for cases with multiple sequences or explicit preprocessing.

**Possible implementation causes:** The source shows that each family maps command-stream fields to DGC tokens and that explicit preprocessing requires a preprocess-to-execute barrier. A failure can therefore indicate incorrect token decoding, sequence indexing, command or preprocess buffer addressing, or synchronization between preprocessing and execution. The source does not identify which implementation component is at fault, so source-level investigation is needed.

#### Push constants and pipeline selection

**Possible failure symptoms:** `max_pc_range` reports wrong values at the first, last, or middle array positions, or the descriptor-buffer execution-set case reports the wrong specialization-constant offset.

**Possible implementation causes:** The test separates push-constant ranges and, where requested, selects pipelines from an execution set. A mismatch can indicate incorrect push-constant token writes, host-pushed range handling, execution-set selection, or pipeline state used by generated commands. The source does not establish a particular driver, compiler, or hardware cause.

#### Descriptor binding and resource access

**Possible failure symptoms:** Copy tests report mismatches across all elements or one descriptor path, such as `multiple_sets`, `iubs`, or push descriptors, fails while another path passes.

**Possible implementation causes:** The relevant shader reads a storage buffer or inline uniform block through the layout recorded by the host. The failure can indicate a mismatch between descriptor-set layout and shader interface, an incorrect set or binding selection, or incorrect descriptor-buffer push-descriptor handling. The source supports these possible mechanisms but does not isolate the failing implementation layer.

#### Scratch-space execution

**Possible failure symptoms:** One or more of the four signed outputs from `scratch_space` differs from `-256`, `-46`, `-327`, or `-722`.

**Possible implementation causes:** The case deliberately creates register pressure and non-uniform control flow and then checks the resulting shader values. The mismatch can indicate incorrect generated-pipeline scratch-space allocation or use, shader compilation, or another execution error. The source does not prove which cause applies, so source-level investigation is needed.

#### Queue and command-buffer submission

**Possible failure symptoms:** A case passes on the universal queue but fails with `_compute_queue`, or the two-command-buffer case does not include all four expected increments.

**Possible implementation causes:** The source changes both the queue family used for the command pool and the queue submitted to. The symptom can indicate queue-family resource handling, command-buffer recording, or submission synchronization. The test evidence does not justify assuming a host, driver, or hardware location.

## Case Pruning

### Requirement-based pruning

- General cases call `checkDGCExtComputeSupport` with the support type required by their pipeline, shader-object, or basic path. Unsupported DGC compute support stops the case before execution.
- Queue variants and `scratch_space` call `context.getComputeQueue()` and are unavailable when a suitable compute queue is absent.
- `max_pc_range` requires `maxPushConstantsSize >= pcBytes` and `maxComputeWorkGroupCount[0] >= pcBytes / DE_SIZEOF32(uint32_t)`. Its push-descriptor variants require `VK_KHR_push_descriptor`.
- `multiple_sets` requires `maxComputeWorkGroupSize[0] >= 32` and `maxComputeWorkGroupCount[0] >= 32`.
- `iubs` requires `VK_EXT_inline_uniform_block`; its execution-set variants require the DGC pipeline support checked by `checkDGCExtComputeSupport(context, DGCComputeSupportType::BIND_PIPELINE)`. `null_set_layouts_info` requires `VK_EXT_shader_object` and DGC shader-object binding support. The descriptor-buffer case requires `VK_EXT_descriptor_buffer`, `VK_KHR_push_descriptor`, and `descriptorBufferPushDescriptors`.

These checks mean that the implementation does not support the selected legal test path or its required resource and queue limits. They are not expected-output failures.

### Design-based pruning

- The source fixes all generated dispatches except the `max_pc_range` and `multiple_sets` dimensions to `(1, 1, 1)`, because those families test command sequencing or push-constant indexing rather than dispatch-shape variation.
- The many-dispatch family uses `64`, `1024`, and `8192`; the sequence family adds `131072` because it tests a single large sequence array rather than repeated execute calls.
- The inline uniform block family fixes the number of blocks at `2`, each block at `128` bytes, and the item count at `8` `uvec4` values. It varies only set placement, execution-set use, and queue.
- The descriptor-buffer push-descriptor family fixes two sequences and 64 invocations per sequence. It varies execution-set use to isolate pipeline selection from the descriptor path.
- `two_cmd_buffers` fixes one ordinary dispatch plus three generated dispatches. Its parameters vary only execution-set use and queue.

## Key Takeaways

- The page tests several independent DGC mechanisms under one EXT compute miscellaneous family. The registered name identifies the selected mechanism and its configuration.
- `execute_many` repeats one-sequence execution with distinct command and preprocess-buffer offsets, while `many_sequences` sends many sequence records through one generated execution call.
- Descriptor correctness covers ordinary sets, two-set layouts, inline uniform blocks, push descriptors, and descriptor buffers. The shader result checks make these resource paths observable.
- Explicit preprocessing is a real execution variant. The source records the preprocess call, inserts the required barrier, and passes the preprocessed flag to execution.
- Queue suffixes change the queue family and command-pool path. A failure in one queue variant does not by itself identify whether the problem lies in submission or generated-command processing.
- All value mismatches are host-side comparisons after a shader-write to host-read barrier. The result identifies the affected family and data position, not a unique implementation bug.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration and matrix construction | [createDGCComputeMiscTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2519-L2617) | Creates all exact EXT registered identifiers. |
| Repeated executes | [manyExecutesRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L346-L541) | Builds per-execution command and preprocess regions and checks `64`. |
| Many sequences | [manySequencesRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L543-L682) | Uses the sequence-index token for large sequence counts. |
| Null set-layout information | [nullSetLayoutsInfoRun](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L684-L890) | Creates a shader-object execution set with null layout metadata and checks ordered and reversed copies. |
| Scratch space | [ScratchSpaceInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L892-L1147) | Loads the SPIR-V artifact and checks four fixed signed results. |
| Maximum push-constant range | [MaxPushConstantRangeInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1261-L1452) | Defines full and partial range updates and all configuration variants. |
| Multiple sets | [MultipleSetsInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1561-L1702) | Binds input and output through two descriptor sets and checks 1024 copied values. |
| Inline uniform blocks | [IUBUsageCase and IUBUsageInstance](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1752-L2147) | Defines set placement, forward and reverse shaders, execution sets, and checks. |
| Descriptor-buffer push descriptors | [DBPDCase and DBPDInstance](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2192-L2515) | Combines descriptor buffers, push descriptors, execution sets, and specialization constants. |
| Descriptor set semantics | [Descriptor set layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-setlayout) | Defines binding interfaces and inline uniform block rules. |
| Descriptor-buffer semantics | [Descriptor buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc) | Defines descriptor-buffer binding and push-descriptor behavior. |
| DGC support helpers | [vktDGCUtilExt.hpp](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.hpp) | Supplies the DGC support and resource helpers used by the implementation. |
