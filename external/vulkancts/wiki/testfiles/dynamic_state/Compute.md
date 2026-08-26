## Overview

**Core question:** Do graphics dynamic state commands, recorded before or after a compute dispatch or a buffer transfer, leave the compute or transfer result untouched?

- [vktDynamicStateComputeTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1) implements the `compute_transfer` test family of the `dynamic_state` test category.
- For each known dynamic graphics state, the file records the `vkCmdSet*` command either before or after a compute dispatch or a `vkCmdCopyBuffer`, then checks that the compute output or the copied data is correct. The dynamic state must not interfere with the non-graphics operation.
- The `single` intermediate node tests one dynamic state at a time across every state in [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474-L509). The `multi` intermediate node tests the first nine basic states together.
- **This test family is registered only for the `monolithic` and `shader_object_unlinked_spirv` pipeline construction types.** The category dispatcher guards the registration with that condition ([dispatcher](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66)).

## Background Knowledge

- **Graphics and compute/transfer isolation.** Vulkan graphics dynamic state commands (for example `vkCmdSetViewport`, `vkCmdSetLineWidth`) are meaningful only inside a render pass and only for graphics draws. A compute dispatch and a transfer copy are not graphics operations. Recording a graphics dynamic state command next to them must not change their result.
- **Pipeline construction type.** The test uses the pipeline construction type passed from the parent group. For shader-object construction, `VK_DYNAMIC_STATE_VIEWPORT` is replaced by `VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT_EXT` and `VK_DYNAMIC_STATE_SCISSOR` by `VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT_EXT` when recording state ([shader-object substitution](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1124-L1131)).

## Registration Hierarchy

```text
dynamic_state.monolithic.compute_transfer
├── single
└── multi
```

The `single` and `multi` intermediate nodes each contain nested `compute` and `transfer` groups, and each of those contains a per-state group (under `single`) with `before` and `after` leaves. The registration is conditional: only `monolithic` and `shader_object_unlinked_spirv` construction types receive this family ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1187-L1284), [dispatcher guard](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation type | `compute`, `transfer` from [`OperType`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L767-L771) | Selects a compute dispatch or a buffer copy as the operation that must remain unaffected. | [operations table](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1195-L1202) |
| When to set | `before`, `after` from [`WhenToSet`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L772-L776) | Records the dynamic state command before or after the operation. | [moments table](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1204-L1211) |
| Dynamic state | 30 states (non-VulkanSC) or 25 states (VulkanSC) from [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474-L509) | The graphics dynamic state recorded next to the operation. The `multi` intermediate node uses only the first nine basic states. | [dynamicStateList](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474-L509) |
| Pipeline construction type | `monolithic` or `shader_object_unlinked_spirv` only | This family is not registered for the other five construction types. | [dispatcher guard](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66) |

### Dynamic state list with extension requirements

| Dynamic state | Extension requirement |
|---------------|-----------------------|
| `viewport`, `scissor`, `line_width`, `depth_bias`, `blend_constants`, `depth_bounds`, `stencil_compare_mask`, `stencil_write_mask`, `stencil_reference` | None (the nine basic states) |
| `discard_rectangle_ext` | `VK_EXT_discard_rectangles` |
| `sample_locations_ext` | `VK_EXT_sample_locations` |
| `ray_tracing_pipeline_stack_size_khr` (non-VulkanSC) | `VK_KHR_ray_tracing_pipeline` |
| `fragment_shading_rate_khr` | `VK_KHR_fragment_shading_rate` |
| `line_stipple_ext` | `VK_KHR_line_rasterization` or `VK_EXT_line_rasterization` |
| `cull_mode_ext` through `stencil_op_ext` (12 states) | `VK_EXT_extended_dynamic_state` |
| `viewport_w_scaling_nv` (non-VulkanSC) | `VK_NV_clip_space_w_scaling` |
| `viewport_shading_rate_palette_nv`, `viewport_coarse_sample_order_nv` (non-VulkanSC) | `VK_NV_shading_rate_image` |
| `exclusive_scissor_nv` (non-VulkanSC) | `VK_NV_scissor_exclusive` |

Source: [`getDynamicStateInfo()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L519-L567).

## Behavior Parameters

The primary behavioral axis is the dynamic state. The `single` intermediate node tests each state in isolation; the `multi` intermediate node tests the nine basic states together. The operation type and the when-to-set value are secondary axes applied to every state.

### `single`: one dynamic state at a time

For each state in [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474-L509), the intermediate node creates four leaves: `compute.before`, `compute.after`, `transfer.before`, and `transfer.after`. Each leaf records the state's `vkCmdSet*` command once, on the same side of every dispatch or copy, and checks that the operation's result is correct. On non-VulkanSC builds this yields 30 states times 4 leaves; the Vulkan SC guards remove the five ray-tracing and NV-specific states ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1214-L1247)).

### `multi`: nine basic states together

This intermediate node takes the first nine basic states (those with no extension requirement, from `viewport` through `stencil_reference`) and places all of them in one test case leaf. Unlike `single`, where each state is a separate leaf, the `multi` leaf interleaves all nine state commands with nine operations in a single command buffer: one `vkCmdDispatch` (compute) or one `vkCmdCopyBuffer` (transfer) per state, each writing to its own output slot. The four leaves are `compute.before`, `compute.after`, `transfer.before`, and `transfer.after`. This stresses the implementation with a burst of graphics state commands interleaved with non-graphics operations in one command buffer ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1249-L1281), [compute loop](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1120-L1150), [transfer loop](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L975-L994)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dynamic_state.monolithic.compute_transfer.single.compute.viewport.before
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` | Uses the ordinary monolithic pipeline construction path; the compute shader is compiled into the compute pipeline created by `iterateCompute()`. |
| `compute` | Selects the dispatch path, so `initPrograms()` emits `comp` and the runtime validates shader-written storage-buffer values rather than copied transfer values. |
| `single.viewport` | Tests one graphics dynamic state in isolation: the viewport command is recorded next to the dispatch, while the shader itself has no viewport-dependent behavior. |
| `before` | Records the viewport state command before the bind/push-constant/dispatch sequence, testing that command ordering does not affect the compute result. |

#### Purpose

This shader is the validation producer for the compute-transfer isolation test: every one-invocation dispatch writes `1u` to the output-buffer slot selected by the host. The test passes only when the graphics dynamic-state command recorded before the dispatch leaves that shader write intact.

#### Structural Design

| Phase | Shader operation | Validation consequence |
|-------|------------------|------------------------|
| Invocation setup | One workgroup of size `1 × 1 × 1` is dispatched. | Each dispatch performs exactly one store, avoiding an invocation-count ambiguity. |
| Index transport | Load `pc.valueIndex` from the compute-stage push-constant block. | The host routes each dynamic-state case to a distinct output slot. |
| Result write | Store the constant `1u` through the runtime-array access `ob.value[pc.valueIndex]`. | After the queue completes, the host expects every slot to contain `1u`; an unchanged zero identifies a missing or corrupted dispatch write. |

#### Shader Code

```glsl
#version 450

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// The host pushes one output-buffer slot per dispatch through this 32-bit field.
layout (push_constant, std430) uniform PushConstants {
    uint valueIndex;
} pc;

/// Binding 0 is the host-visible storage buffer whose slots are checked after submission.
layout (set=0, binding=0, std430) buffer OutputBlock {
    uint value[];
} ob;

/// Each one-invocation dispatch marks only the slot selected by the current push constant.
void main ()
{
    ob.value[pc.valueIndex] = 1u;
}
```

#### Additional Info

- `DynamicStateComputeCase::initPrograms()` emits this `comp` module only when `operationType` is `COMPUTE`; the transfer variants do not create or execute a shader.
- The host allocates one `uint32_t` output slot per state, pushes the loop index before each dispatch, and inserts a compute-write-to-host-read barrier before checking the slots. The shader therefore supplies the device-side signal, while command ordering and dynamic-state isolation remain the tested behavior.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Operation type | `compute` emits the fixed `comp` shader; `transfer` emits no compute shader and instead validates `vkCmdCopyBuffer`. | [`DynamicStateComputeCase::initPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L874-L897) |
| Dynamic-state set | `single` changes only which host recorder runs around the same dispatch; `multi` supplies the first nine basic states but leaves this shader unchanged. | [`createDynamicStateComputeTests()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1213-L1281) |
| When to set | `before` versus `after` changes command-buffer ordering around the same bind, push-constant update, and dispatch; shader declarations and instructions are unchanged. | [`iterateCompute()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1114-L1149) |
| Output routing | Each dispatch receives a different `valueIndex`, changing the addressed runtime-array element but not the store value or control flow. | [`iterateCompute()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1141-L1146) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 24
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "value"
               OpName %ob "ob"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "valueIndex"
               OpName %pc "pc"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %ob Binding 0
               OpDecorate %ob DescriptorSet 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
         %ob = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstants = OpTypeStruct %uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_1 = OpConstant %uint 1
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %18 = OpLoad %uint %17
         %21 = OpAccessChain %_ptr_Uniform_uint %ob %int_0 %18
               OpStore %21 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` checks pipeline construction requirements, then walks each state's extension requirements through `getDynamicStateInfo()`. The `line_stipple_ext` state accepts either `VK_KHR_line_rasterization` or `VK_EXT_line_rasterization`. The `depth_bounds_test_enable_ext` state also requires the `depthBounds` core feature ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L840-L872)).
- A device helper is selected per state. States requiring `VK_NV_shading_rate_image` use a custom device with the extension and its `VkPhysicalDeviceShadingRateImageFeaturesNV` feature enabled; all other states use the default context device ([getDeviceHelper](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L738-L753)).
- **Transfer path:** creates a source and destination buffer with one element per dynamic state. For each state, it records the state command (before or after) around a one-element `vkCmdCopyBuffer`. After submit, it invalidates the destination allocation and requires every element to match the source ([iterateTransfer](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L935-L1025)).
- **Compute path:** creates a zeroed storage buffer with one slot per state, a compute pipeline that writes `1u` to the slot named by a push constant, and a descriptor set. For each state, it records the state command (before or after) around a `vkCmdDispatch`, pushing a different slot index each time. After submit, it requires every slot to equal `1u` ([iterateCompute](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1027-L1175)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any `single` state leaf | The recorded graphics dynamic state command interfered with the compute dispatch or buffer copy for that state. |
| `multi` leaves only | Recording several basic states together interfered, even though each one alone did not. |
| All `compute` leaves | The compute dispatch result is wrong, independent of which dynamic state was recorded. |
| All `transfer` leaves | The buffer copy result is wrong, independent of which dynamic state was recorded. |
| `before` leaves only or `after` leaves only | The interference depends on command ordering relative to the operation. |
| All leaves | Shared infrastructure: the buffer verification logic, the device helper, or the compute shader is wrong. |

### Cause Analysis

#### Graphics dynamic state interfered with a non-graphics operation

**Possible failure symptoms:** A destination buffer element does not match its source value (transfer), or a compute output slot is not `1u` (compute), for one or more states.

**Possible implementation causes:** The implementation may let a graphics dynamic state command corrupt transfer or compute state, execute the copy or dispatch with the wrong parameters, or fail to isolate command categories. Because each leaf records exactly one state (under `single`) or a fixed group (under `multi`) around the operation, a state-specific failure points at that state's recording path. Whether the defect is in the command-buffer recording, the scheduler, or the compute/transfer unit requires inspection against the Vulkan command isolation rules.

#### Device-helper or extension-setup failure

**Possible failure symptoms:** Only states that require `VK_NV_shading_rate_image` fail, or only states that need a custom device fail.

**Possible implementation causes:** The custom device created for shading-rate-image states may not expose the feature correctly, or the default context device may lack an extension that `checkSupport` did not gate. These failures are infrastructure failures rather than evidence of command interference.

#### Verification logic mismatch

**Possible failure symptoms:** Every leaf fails with the same buffer pattern, or the failure message names a buffer position that does not correspond to a recorded state.

**Possible implementation causes:** The source values, the push-constant slot mapping, or the invalidate/flush sequence may be wrong. These are host-side causes and should be ruled out before attributing the failure to the device.

## Case Pruning

### Requirement-based pruning

- Each state's extension requirements are checked in `checkSupport`. Unsupported extensions raise `NotSupportedError`.
- The `depth_bounds_test_enable_ext` state requires the `depthBounds` core feature.
- The `line_stipple_ext` state requires either `VK_KHR_line_rasterization` or `VK_EXT_line_rasterization`.
- Five states (`ray_tracing_pipeline_stack_size_khr`, `viewport_w_scaling_nv`, `viewport_shading_rate_palette_nv`, `viewport_coarse_sample_order_nv`, `exclusive_scissor_nv`) are conditionally compiled out under `CTS_USES_VULKANSC`.

### Design-based pruning

- This family is registered only for `monolithic` and `shader_object_unlinked_spirv`. The other five construction types do not receive `compute_transfer` at all.
- The `multi` intermediate node uses only the nine basic states to avoid introducing extra extension requirements on top of the single-state coverage.

## Key Takeaways

- The dynamic state is the behavioral axis under `single`; the `multi` intermediate node adds a combined burst of basic states.
- Every leaf tests the same property: a graphics dynamic state command must not change the result of a compute dispatch or a buffer copy.
- This family is the only one in the category whose registration is conditional on pipeline construction type. It appears only under `monolithic` and `shader_object_unlinked_spirv`.
- A state-specific failure points at that state's recording path; a uniform failure across states points at shared infrastructure or the operation itself.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration (factory) | [`createDynamicStateComputeTests()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1187-L1284) | Builds the `single` and `multi` nodes and their nested groups. |
| Dispatcher guard | [vktDynamicStateTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66) | Restricts registration to `monolithic` and `shader_object_unlinked_spirv`. |
| Dynamic state list | [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474-L509) | The full set of graphics dynamic states tested. |
| State info and requirements | [`getDynamicStateInfo()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L519-L567) | Extension requirements and recorder function per state. |
| Support checks | [`DynamicStateComputeCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L840-L872) | Per-state extension and feature gating. |
| Transfer verification | [`iterateTransfer()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L935-L1025) | Buffer-copy result check. |
| Compute verification | [`iterateCompute()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1027-L1175) | Compute output buffer check and shader-object state substitution. |
| Shaders | [initPrograms](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L874-L911) | One-line compute store and stand-in vertex shader. |
