## Overview

**Core question:** Does EXT generated compute execution obey the effective conditional predicate without letting conditional rendering suppress preprocessing?

- This page covers `dgc.ext.compute.conditional_rendering`, implemented by `vktDGCComputeConditionalTestsExt.cpp`.
- `general` places one generated dispatch inside conditional rendering and varies pipeline binding, indirect sequence count, predicate, inversion, and queue.
- `preprocess` separates explicit preprocessing from execution and varies where state and conditional rendering are recorded.
- Every executing dispatch copies push constant `777` to a one-word output buffer. Suppressed execution leaves its initial value of `0` unchanged.

## Background Knowledge

- `vkCmdBeginConditionalRenderingEXT` reads a 32-bit predicate. Zero suppresses affected commands and nonzero permits them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision.
- An indirect commands layout with `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` requires preprocessing followed by execution with `isPreprocessed = VK_TRUE`. The execution call must use state and inputs that match preprocessing.
- A state command buffer supplies compute state to `vkCmdPreprocessGeneratedCommandsEXT`. It may be the preprocessing command buffer itself or a separate execution command buffer.

## Registration Hierarchy

```text
dgc.ext.compute.conditional_rendering
├── general
└── preprocess
```

## Parameter Dimensions and Observed Values

The source registers 56 test case leaves: 32 under `general` and 24 under `preprocess`.

### `general`

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline binding | `classic_bind`, `pipeline_token` | Uses an ordinary bound pipeline or prepends a generated compute-pipeline token backed by an indirect execution set. | [pipeline and layout construction](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L208-L223) |
| Sequence count | `with_count_buffer`, `without_count_buffer` | Reads the actual count of `1` from a buffer with a maximum of 256, or passes the count `1` directly. | [sequence-count setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L270-L297) |
| Predicate | `condition_false`, `condition_true` | Stores `0` or `2` in the conditional-rendering buffer. | [predicate buffer](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L244-L256) |
| Inversion | no suffix, `inverted_flag` | Uses normal zero versus nonzero semantics or reverses them. | [conditional begin helper](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L127-L142) |
| Queue | `_cq`, `_uq` | Submits the complete command buffer on the compute queue or universal queue. | [queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L158-L165) |

The exact registered leaf grammar is:

```text
{classic_bind|pipeline_token}_{with_count_buffer|without_count_buffer}_{condition_false|condition_true}[_inverted_flag]_{cq|uq}
```

All choices in that grammar are combined, including the optional `inverted_flag`, for 32 leaves.

### `preprocess`

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Predicate | `condition_false`, `condition_true` | Stores `0` or `256` in the conditional-rendering buffer. | [preprocess predicate buffer](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L419-L430) |
| Inversion | no suffix, `inverted_flag` | Uses the predicate directly or inverts it. | [registration loop](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L617-L643) |
| Conditional-block placement | no suffix, `preprocess_only` | Applies conditional rendering to execution, or only to the preprocessing command buffer. | [conditional recording and expected result](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L513-L577) |
| State command buffer | no suffix, `separate_state` | Uses the preprocessing command buffer as state or supplies the execution command buffer as separate state. | [state command buffer selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L503-L539) |
| Execution queue | no suffix, `exec_on_compute` | Executes on the universal queue or a compute queue after preprocessing on the universal queue. | [queue switch and ownership barriers](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L441-L500) |

The exact registered leaf grammar, in suffix order, is:

```text
{condition_false|condition_true}[_inverted_flag][_preprocess_only][_separate_state][_exec_on_compute]
```

The generator removes every combination containing `preprocess_only` without `separate_state`. The remaining 24 leaves comprise eight without separate state, eight with `separate_state`, and eight with both `preprocess_only` and `separate_state`.

## Behavior Parameters

The primary behavioral axis is the conditional execution outcome. The predicate and optional inversion produce effective true or false execution. `preprocess_only` adds a third behavior because conditional rendering surrounds preprocessing but not execution.

### `effective condition true` - generated dispatch executes

A nonzero predicate without inversion or a zero predicate with `inverted_flag` permits execution. The generated dispatch runs once and writes `777` to the output word.

### `effective condition false` - generated dispatch is suppressed

A zero predicate without inversion or a nonzero predicate with `inverted_flag` suppresses execution. The shader does not run, so the output word remains `0`.

### `preprocess_only` - preprocessing ignores the conditional block

Conditional rendering begins and ends in the preprocessing command buffer only. The later execution command buffer has no active conditional block, so all `preprocess_only` variants must dispatch and produce `777`, regardless of predicate or inversion. Separate state is mandatory for this registered behavior.

Pipeline binding, count input, queue selection, and state-command-buffer placement carry these outcomes through different EXT DGC paths without changing the shader result.

## Shader Analysis

The compute shader does not read the predicate. It only turns the execution decision into a visible value. One walkthrough covers all variants because their differences lie in generated-command and command-buffer setup.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.conditional_rendering.general.classic_bind_without_count_buffer_condition_true_uq
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `classic_bind` | The host binds an ordinary compute pipeline. |
| `without_count_buffer` | `sequencesCount` directly specifies one sequence. |
| `condition_true` | The predicate buffer contains nonzero value `2`. |
| no `inverted_flag` | Nonzero permits the generated dispatch. |
| `_uq` | The universal queue executes the command buffer. |

#### Purpose

Show the direct path from an effective true predicate to the host-visible value `777`.

#### Structural Design

| Stage | Input | Operation | Observable result |
|-------|-------|-----------|-------------------|
| Conditional rendering | predicate `2`, no inversion | Permits the generated dispatch. | The compute shader is invoked. |
| Generated command stream | push constant `777`, dispatch `(1, 1, 1)` | Sets the push constant and launches one invocation. | One shader invocation can write the output. |
| Compute shader | `pc.value` | Stores the push constant in `outputBuffer.value`. | The output word becomes `777`. |
| Host check | mapped output word | Compares the word with the expected value. | This case passes when the value is `777`. |

#### Shader Code

##### Compute Shader

```glsl
#version 460
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (set=0, binding=0, std430) buffer OutputBlock { uint value; } outputBuffer;
layout (push_constant, std430) uniform PushConstantBlock { uint value; } pc;
void main (void) { outputBuffer.value = pc.value; }
```

#### Additional Info

- The source registers the shader as `comp` for both `general` and `preprocess`.
- Conditional rendering decides whether execution reaches this shader. No shader instruction evaluates the predicate or inversion flag.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `classic_bind` or `pipeline_token` | No shader change. The pipeline is bound directly or selected by a generated pipeline token. | [pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L208-L223) |
| Count-buffer choice | No shader change. Both paths execute one sequence when the effective condition permits it. | [count setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L270-L297) |
| Predicate and inversion | No shader change. Conditional rendering either invokes or suppresses the dispatch. | [general command recording](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L303-L323) |
| Queue | No shader change. The selected queue executes the same generated stream. | [queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L158-L165) |
| `preprocess` variants | No shader change. They alter preprocessing state, conditional-block placement, synchronization, and execution queue. | [preprocess runtime](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L503-L577) |

#### SPIR-V

##### Compute Shader SPIR-V

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
; Bound: 23
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "value"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "value"
               OpName %pc "pc"
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
%OutputBlock = OpTypeStruct %uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %17 = OpLoad %uint %16
         %19 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0
               OpStore %19 %17
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checks require `VK_EXT_device_generated_commands`, EXT DGC support for compute stages, and `VK_EXT_conditional_rendering`. `pipeline_token` also requires generated compute-pipeline binding support. Compute-queue variants require an available compute queue.
- Both families create a host-visible output buffer initialized to `0`, a descriptor set for that buffer, a push-constant range, a compute pipeline, a generated-command buffer, a conditional-rendering buffer, and a preprocess buffer.
- General cases build a command stream with optional pipeline index `0`, push constant `777`, and dispatch dimensions `(1, 1, 1)`. The preprocess buffer allows 256 sequences, but execution uses one. With `with_count_buffer`, the command info advertises 256 as the maximum and the count buffer supplies `1`; without it, the command info directly supplies `1`.
- The general command buffer begins conditional rendering, binds descriptors and the selected pipeline path, calls `vkCmdExecuteGeneratedCommandsEXT` with `isPreprocessed = VK_FALSE`, ends conditional rendering, and inserts a shader-write to host-read barrier.
- Preprocess cases use a normal pipeline and an explicit-preprocess layout for one sequence. Without `separate_state`, the universal-queue preprocessing command buffer records pipeline, descriptors, and conditional state and also acts as its own state command buffer. The execution command buffer records matching state later.
- With `separate_state`, the execution command buffer records compute state first and serves as the state command buffer for preprocessing. Unless `preprocess_only` is selected, it also records conditional rendering for later execution.
- Preprocessing always runs on the universal queue. The source inserts a preprocess-write to indirect-command-read barrier. `exec_on_compute` cases add queue-family release and acquire barriers for the output, generated-command, and preprocess buffers before execution on the compute queue.
- Execution calls `vkCmdExecuteGeneratedCommandsEXT` with `isPreprocessed = VK_TRUE`. For ordinary preprocess cases, conditional rendering surrounds execution. For `preprocess_only`, only preprocessing was inside a conditional block, so execution proceeds unconditionally.
- After submission completes, the host invalidates the output allocation and reads one word. General and ordinary preprocess cases expect `777` when `conditionValue != inverted` and `0` otherwise. Every `preprocess_only` case expects `777`. A mismatch reports the expected and observed words.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `effective condition true` | The permitted dispatch did not write `777`; predicate evaluation, generated-command decoding, pipeline or shader execution, synchronization, queue ownership, or host readback may be wrong. |
| `effective condition false` | A suppressed dispatch changed the output, or output initialization and host readback did not preserve the expected `0`. |
| `preprocess_only` | Conditional rendering incorrectly affected preprocessing, or the separate-state, preprocessed execution, queue-transfer, or result path failed to produce `777`. |

### Cause Analysis

#### Conditional predicate or inversion

**Possible failure symptoms:** An effective true case leaves `0`, or an effective false case writes `777` or another value.

**Possible implementation causes:** The implementation may apply the zero versus nonzero test or `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` incorrectly. The output mismatch alone cannot separate predicate evaluation from generated execution or host visibility, so further investigation must compare nearby variants.

#### Generated pipeline, tokens, or shader execution

**Possible failure symptoms:** Executing cases fail only with `pipeline_token`, a count-buffer choice, or both, or they produce a value other than `777`.

**Possible implementation causes:** Pipeline-token selection through the indirect execution set, sequence-count handling, push-constant decoding, dispatch decoding, descriptor state, or shader execution may be wrong. Comparing `classic_bind` with `pipeline_token` and count-buffer pairs can narrow the affected path.

#### Explicit preprocessing and state matching

**Possible failure symptoms:** Direct general cases pass, but equivalent preprocess cases return the wrong value. Failures may track `separate_state` or `preprocess_only`.

**Possible implementation causes:** The implementation may mishandle explicit preprocessing, the state command buffer, matching compute or conditional state, or the rule that conditional rendering around preprocessing alone does not suppress the later execution. The source follows the required matching-state flow; isolating a specific implementation defect needs command validation and source-level investigation.

#### Cross-queue synchronization or host visibility

**Possible failure symptoms:** Universal-queue variants pass while `_cq` or `exec_on_compute` variants fail, or the host reads stale `0` after an expected dispatch.

**Possible implementation causes:** Queue selection, queue-family ownership transfer, preprocess-to-execute visibility, shader-write to host-read visibility, allocation invalidation, or completion waiting may be wrong. A failure tied to `exec_on_compute` points to the separated preprocess and execution path but does not identify one barrier without further investigation.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_device_generated_commands`, EXT generated-command support for compute stages, and `VK_EXT_conditional_rendering`.
- `pipeline_token` cases require compute in `supportedIndirectCommandsShaderStagesPipelineBinding`.
- `_cq` and `exec_on_compute` cases require an available compute queue. The support check requests that queue and reports the case unsupported if it is unavailable.

### Design-based pruning

- `general` registers the full Cartesian product of five binary dimensions, producing 32 leaves.
- The preprocess generator starts from five binary dimensions but skips `preprocess_only && !separateState`. Such a combination would tell preprocessing that conditional rendering is active through its state command buffer while leaving execution outside conditional rendering. The remaining matrix contains 24 leaves.
- `preprocess` fixes the pipeline to an ordinary bind, uses one sequence, and always performs explicit preprocessing. Those are setup choices rather than omitted registered dimensions.
- General count-buffer cases store `1` in the count buffer while allowing up to 256 sequences. The larger number is capacity and an upper bound, not another executed count or case variant.
- True predicates use `2` in `general` and `256` in `preprocess`. Both choices confirm zero versus nonzero semantics without relying on value `1`.

## Key Takeaways

- The effective execution decision is the predicate combined with `inverted_flag`: true writes `777`, while false preserves `0`.
- Pipeline-token and count-buffer variants change how EXT DGC reaches the same one-dispatch result. Queue variants change where it executes.
- Explicit preprocessing must preserve matching state for later execution. Conditional rendering around preprocessing alone must not suppress that execution.
- The test reports one output mismatch. Its variant name helps map that symptom to predicate handling, generated-command transport, preprocessing, synchronization, or readback, but the mismatch does not prove a unique cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` and `ConditionalPreprocessParams` | [parameter structures](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L54-L70) | Define all generated registration dimensions. |
| Support checks | [conditional DGC compute support](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L72-L96) | Apply extension, generated pipeline-binding, and queue requirements. |
| Shader and predicate helpers | [program and conditional begin](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L98-L156) | Build the observable shader and apply inversion. |
| `conditionalDispatchRun` | [general runtime](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L158-L331) | Covers direct generated execution, count behavior, queue choice, and checking. |
| `conditionalPreprocessRun` | [preprocess runtime](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L343-L584) | Covers state command buffers, conditional placement, queue transfer, and preprocessed execution. |
| `createDGCComputeConditionalTestsExt` | [registration and design pruning](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L589-L647) | Registers all 56 leaves and skips the invalid `preprocess_only` combination. |
| EXT support helper | [checkDGCExtComputeSupport](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L44-L75) | Checks EXT DGC stage and pipeline-binding properties. |
| Conditional rendering rules | [Conditional Rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#L2086-L2184) | Defines affected commands, predicate values, and inversion. |
| Explicit-preprocess rules | [generated-command execution validity](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L3037-L3089) | Requires preprocessing and execution to use matching inputs and state. |
| Exact registered paths | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L1-L56) | Lists the 32 general and 24 preprocess test cases. |
