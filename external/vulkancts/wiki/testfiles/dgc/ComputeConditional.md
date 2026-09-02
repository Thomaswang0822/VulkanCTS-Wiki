## Overview

**Core question:** Does conditional rendering select the expected execution result for NV device-generated compute commands, including explicit preprocessing?

- This page covers the `dgc.nv.compute.conditional_rendering` test family implemented in [`vktDGCComputeConditionalTests.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L615-L677).
- The `general` family combines ordinary or generated pipeline binding, an optional sequence-count buffer, predicate values, inversion, command-buffer scope, and queue choice.
- The `preprocess` family checks conditional rendering around preprocessing and later execution, including execution on a compute queue.
- The observable result is a one-word storage buffer. An effective true condition must produce `777`; an effective false condition must leave the initialized value at `0`.

## Background Knowledge

- **Conditional rendering predicate:** `vkCmdBeginConditionalRenderingEXT` reads a 32-bit value from a buffer. A zero value suppresses affected conditional commands, while a nonzero value permits them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision. The predicate buffer uses `VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT`.
- **Generated commands and preprocessing:** A `VkIndirectCommandsLayoutNV` describes how the device interprets a generated command stream, while `VkGeneratedCommandsInfoNV` supplies that layout with the stream, sequence count, and preprocessing state. Explicit preprocessing produces generated state before a later execution call consumes it. Conditional rendering can surround commands in either operation, so the predicate state must have the expected effect at each boundary.

## Registration Hierarchy

```text
dgc.nv.compute.conditional_rendering
├── general
└── preprocess
```

The `general` family expands each binding choice into the registered count-buffer, condition, inversion, command-buffer, and queue suffixes. The `preprocess` family expands each condition choice into inversion and optional `_exec_on_compute` cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline binding | `classic_bind`, `pipeline_token` | Selects a host-bound compute pipeline or a pipeline token in the generated stream. | [`createDGCComputeConditionalTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L623-L653) |
| Sequence count | `with_count_buffer`, `without_count_buffer` | Selects an indirect count buffer while the generated-command description can still advertise 256 potential sequences, or executes one sequence directly. | [`conditionalDispatchRun`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L276-L321) |
| Predicate and inversion | `condition_true`, `condition_false`, optional `inverted_flag` | Supplies `2` or `0` and optionally reverses the conditional result. | [`beginConditionalRendering`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L138-L153) and [`conditionalDispatchRun`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L262-L274) |
| Command-buffer scope | `primary`, `secondary`, `secondary_with_inheritance` | Places conditional rendering and generated execution in a primary or secondary command buffer, with optional inherited conditional state. | [`conditionalDispatchRun`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L323-L383) |
| Queue selection | `_uq`, `_cq`, or `_exec_on_compute` | Uses the universal queue or a compute queue for the relevant operation. | [`checkConditionalDGCComputeSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L84-L98) and [`conditionalPreprocessRun`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L406-L611) |
| Preprocessing mode | `general`, `preprocess` | Chooses direct generated execution or explicit preprocessing followed by preprocessed execution. | [`createDGCComputeConditionalTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L615-L672) |

The source registers 96 `general` cases and 8 `preprocess` cases. The exact executable leaves are listed in [the DGC mustpass file](../../../mustpass/main/vk-default/dgc.txt#L4350-L4453).

## Behavior Parameters

The primary behavioral axis is the effective conditional outcome. `condition_true` and `condition_false` combine with `inverted_flag`; the other dimensions carry the same one-dispatch operation through different NV DGC paths.

### `condition_true` without `inverted_flag`: execute

`condition_true` writes `2`, a nonzero predicate. Without inversion, conditional rendering permits the generated dispatch, so the compute shader writes `777` to `outputBuffer`.

### `condition_true` with `inverted_flag`: suppress

Inversion changes the nonzero predicate to an effective false condition. The generated dispatch is suppressed and the initialized output remains `0`.

### `condition_false` without `inverted_flag`: suppress

`condition_false` writes `0`. Without inversion, conditional rendering suppresses the generated dispatch and the output remains `0`.

### `condition_false` with `inverted_flag`: execute

Inversion changes the zero predicate to an effective true condition. The generated dispatch runs and the output becomes `777`.

The `general` family also varies `classic_bind` versus `pipeline_token`, count-buffer choice, command-buffer scope, and queue. The `preprocess` family uses the same four predicate outcomes and adds `_exec_on_compute` to select the execution queue. These dimensions do not change the shader source.

## Shader Analysis

The test uses one small compute shader. It does not evaluate the predicate. Conditional rendering decides whether the dispatch reaches the shader, and the shader makes that decision observable by copying the push constant to the storage buffer.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.conditional_rendering.general.classic_bind_without_count_buffer_condition_true_primary_uq
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `classic_bind` | The ordinary compute pipeline is bound instead of being supplied by a pipeline token. |
| `without_count_buffer` | The generated command description executes one sequence without an indirect count buffer. |
| `condition_true` | The host writes `2`, a nonzero predicate, to `conditionBuffer`. |
| `primary` | Conditional rendering and generated execution are recorded in the primary command buffer. |
| `_uq` | Submission uses the universal queue. |

#### Purpose

This path checks that an effective true condition permits the generated dispatch and produces the expected visible value.

#### Structural Design

| Stage | Input | Operation | Observable result |
|---|---|---|---|
| Conditional rendering | `conditionBuffer.value = 2` | Permit the command block because the predicate is nonzero. | The dispatch can execute. |
| Compute shader | push constant `pc.value = 777` | Store the push constant in `outputBuffer.value`. | The output word becomes `777`. |
| Host check | mapped `outputBuffer` | Compare the read value with the expected value. | The case passes when they match. |

#### Shader Code

```glsl
#version 460
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (set=0, binding=0, std430) buffer OutputBlock { uint value; } outputBuffer;
layout (push_constant, std430) uniform PushConstantBlock { uint value; } pc;
void main (void) { outputBuffer.value = pc.value; }
```

#### Additional Info

- The source adds the shader as `comp` and uses one `uint32_t` push constant with the value `777`.
- The shader is shared by `general` and `preprocess`. Those families differ in command timing and synchronization, not shader code.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `pipelineToken` | No shader change. The generated pipeline token supplies the pipeline instead of a host bind. | [pipeline selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L221-L239) |
| `indirectCountBuffer` | No shader change. The optional count buffer controls the sequence count supplied to generated execution. | [sequence count buffer](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L284-L302) |
| `conditionValue` and `inverted` | No shader change. Conditional rendering controls whether the shader is invoked. | [conditional begin](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L138-L153) |
| `useSecondaries` and `computeQueue` | No shader change. They alter command-buffer nesting and queue submission. | [general command recording](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L323-L383) |
| `preprocess` and `executeOnCompute` | No shader change. They separate preprocessing from execution and may move execution to a compute queue. | [preprocess execution](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L543-L594) |

#### SPIR-V

- Status: generated and validated
- Source: exact generated `GLSL` emitted for this test family
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

- Support checks require NV compute DGC support and `VK_EXT_conditional_rendering`. `secondary_with_inheritance` additionally requires `inheritedConditionalRendering`. Cases with `_cq` or `_exec_on_compute` require an available compute queue. Unsupported cases are pruned before execution.
- The host allocates a host-visible one-word storage buffer and initializes it to zero. It creates the descriptor set, a one-word push-constant range, the ordinary or DGC pipeline, the generated command layout, and the host-visible command stream.
- The command layout contains a push-constant token followed by a dispatch token. `pipeline_token` cases prepend a pipeline token. The stream contains the optional pipeline address, `777`, and `VkDispatchIndirectCommand` dimensions `1, 1, 1`.
- `general` creates a one-word predicate buffer containing `0` or `2`. When `with_count_buffer` is selected, it creates a one-word indirect count buffer containing `1`; `VkGeneratedCommandsInfoNV` still advertises 256 potential sequences for that path. The preprocess buffer is sized for 256 potential sequences, although one sequence executes.
- In `primary` cases, the primary command buffer begins conditional rendering with the optional inverted flag, binds the descriptor set and pipeline, executes the generated command, ends conditional rendering, and inserts a shader-write to host-read barrier. In secondary cases, descriptor and pipeline binding plus generated execution are recorded in the secondary; conditional rendering is recorded in the secondary for `secondary`, or in the primary around `vkCmdExecuteCommands` for `secondary_with_inheritance`.
- `preprocess` surrounds `vkCmdPreprocessGeneratedCommandsNV` with conditional rendering, applies the preprocess-to-execute barrier, and then calls `vkCmdExecuteGeneratedCommandsNV` with `isPreprocessed = VK_TRUE`. `_exec_on_compute` cases add queue-family ownership barriers for the output, command, and preprocess buffers.
- The host waits for the selected queue, invalidates `outputBuffer`, and reads `outputValue`. The expected value is `777` when `conditionValue != inverted`; otherwise it is `0`. Any mismatch returns `tcu::TestStatus::fail` with the observed and expected values.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `condition_true` without `inverted_flag` | The permitted generated dispatch did not produce `777`. The failure can involve conditional evaluation, generated commands, shader execution, synchronization, or readback. |
| `condition_true` with `inverted_flag` | The inverted predicate did not suppress the dispatch, or the host read stale output data. |
| `condition_false` without `inverted_flag` | The zero predicate did not suppress the dispatch, or the output was not initialized or read correctly. |
| `condition_false` with `inverted_flag` | The inverted predicate should permit the dispatch, but the output was not `777`. The failure can involve conditional evaluation or the generated compute path. |

For `preprocess` cases, the corresponding failure may additionally involve conditional rendering around preprocessing and execution, preprocess-to-execute synchronization, preprocessed generated state, or queue-family ownership transfer.

### Cause Analysis

#### Predicate and inversion result

**Possible failure symptoms:** A case returns `777` when suppression was expected, returns `0` when execution was expected, or produces another value.

**Possible implementation causes:** The implementation may evaluate the zero/nonzero predicate or `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` incorrectly. The output comparison cannot distinguish predicate evaluation from later command execution or readback without further investigation.

#### Generated command and shader result

**Possible failure symptoms:** The predicate outcome is correct in principle, but an executing case does not write `777` to `outputBuffer`.

**Possible implementation causes:** The generated pipeline token, push-constant token, dispatch token, descriptor binding, compute shader execution, or shader-to-host visibility may be wrong. Source-level investigation is needed to isolate the failing part.

#### Preprocessing or queue transfer

**Possible failure symptoms:** A `preprocess` or `_exec_on_compute` case produces a different result from the equivalent direct universal-queue case.

**Possible implementation causes:** The implementation may mishandle conditional rendering around preprocessing, the preprocess-to-execute barrier, or queue-family ownership transfer. Further source and validation investigation is needed to identify the specific mechanism.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_conditional_rendering` and NV compute DGC support.
- `secondary_with_inheritance` requires `inheritedConditionalRendering`.
- `_cq` and `_exec_on_compute` cases require a compute queue. The source calls `context.getComputeQueue()`, which reports unsupported when no such queue is available.

### Design-based pruning

- `general` varies six dimensions: `pipelineToken`, `indirectCountBuffer`, `conditionValue`, `inverted`, `useSecondaries`, and `computeQueue`. It registers 96 cases from two pipeline choices, two count-buffer choices, two predicate values, two inversion choices, three command-buffer modes, and two queue choices.
- `preprocess` fixes pipeline binding, a sequence count of one, and one generated sequence; it has no indirect count-buffer dimension. It varies `conditionValue`, `inverted`, and `executeOnCompute`, producing the eight exact test case leaves listed in mustpass.
- The predicate writes `2` rather than `1` for the true value. Both are nonzero, so this choice checks the zero/nonzero rule rather than one particular nonzero value.
- The `general` preprocess buffer reserves space for 256 potential sequences even though the test executes one; `preprocess` allocates its preprocess buffer for one sequence. These capacities are setup details, not registered case dimensions.

## Key Takeaways

- Conditional rendering changes whether the generated compute dispatch writes the output word. It does not change the shader program.
- `with_count_buffer`, `pipeline_token`, secondary command buffers, and queue selection exercise different NV DGC paths around the same predicate decision.
- `preprocess` checks that conditional state does not corrupt preprocessing and that later preprocessed execution sees the matching state.
- A passing result is `777` for an effective true condition and `0` for an effective false condition. A failure reports the output mismatch, not a unique implementation layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `TestParams` and `ConditionalPreprocessParams` | [parameter structures](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L55-L77) | Define the behavioral dimensions used by the registered cases. |
| `checkConditionalDGCComputeSupport` and `checkConditionalPreprocessSupport` | [support checks](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L79-L107) | Apply extension, DGC, inheritance, and queue requirements. |
| `conditionalDispatchRun` | [general runtime](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L171-L404) | Builds resources, records generated commands, and checks the output word. |
| `conditionalPreprocessRun` | [preprocess runtime](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L406-L611) | Separates preprocessing and execution and checks the same predicate contract. |
| `createDGCComputeConditionalTests` | [registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L615-L677) | Registers `general`, `preprocess`, and their exact case names. |
| Conditional rendering semantics | [VK_EXT_conditional_rendering](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L45) | Defines conditional execution and secondary-command-buffer inheritance semantics. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4350-L4453) | Lists the exact NV registered identifiers. |
