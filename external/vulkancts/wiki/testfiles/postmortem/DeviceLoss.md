## Overview

**Core question:** After a compute submission causes the device to become lost, do subsequent Vulkan entry points consistently report `VK_ERROR_DEVICE_LOST`?

- This page explains the implementation of the experimental `postmortem.device_loss.maintenance5` case in [`vktPostmortemDeviceLossTests.cpp`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L93-L104).
- The case creates a custom device requiring `VK_KHR_maintenance5`, submits a one-workgroup compute workload designed to keep executing, and probes a defined sequence of device and queue operations.
- The test is about post-loss result propagation. It does not require the shader's output buffer to contain a particular value.
- If no operation reports `VK_ERROR_DEVICE_LOST`, the case passes. Once one operation reports device loss, the applicable operations are called again with fresh synchronization objects and must all report the same result.
- This is experimental-only coverage. `createChildrenExperimental` attaches the group to the experimental postmortem root ([registration](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L47-L65)); the standard `vk-default` postmortem mustpass lists device-fault cases, not `postmortem.device_loss` ([mustpass](../../../mustpass/main/vk-default/postmortem.txt#L1-L24)).

## Background Knowledge

For the shared concept of device loss, see [Background Knowledge](../../categories/postmortem.md#background-knowledge) of the `postmortem` page.

- A Vulkan device-loss result means that the logical device can no longer perform ordinary work. This test therefore examines the results of later API calls, not recovery, data preservation, or reconstruction of the device.
- A compute pipeline connects a compute shader to a command buffer. The command buffer records the dispatch, while the host later observes completion and device state through queue, fence, event, semaphore, idle, and query calls.
- A storage buffer is shader-writable memory exposed through a descriptor. Here it makes the dispatch a real resource-using workload; its value is not the oracle for the test.
- A timeline semaphore carries a monotonically increasing counter and can be waited on by value. This case probes it only when `VK_KHR_timeline_semaphore` is available, so its absence does not prune the whole test.

## Registration Hierarchy

```text
postmortem.device_loss
└── maintenance5
```

The `device_loss` group is created by [`createDeviceLossTests`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L336) and is attached through the experimental root rather than the standard postmortem root ([experimental registration](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L47-L65)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| test case | `maintenance5` | The only registered leaf; it selects the device-loss propagation scenario and the `VK_KHR_maintenance5` requirement. | [`createDeviceLossTests`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L336) |
| timeline-semaphore functionality | supported or unsupported | When supported, the device enables `VK_KHR_timeline_semaphore` and the operation list includes `waitSemaphores`; otherwise that operation returns the sentinel `VK_RESULT_MAX_ENUM` and is skipped. | [`createPostmortemDevice`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L61-L75), [`operation list`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L224-L245) |
| `pipelineStatisticsQuery` feature | enabled or unavailable | When enabled, the command buffer surrounds the dispatch with a compute-invocation query and the operation list includes `getQueryPoolResults`. | [`query setup`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L113-L125), [`query recording`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L171-L184) |
| first-pass observation | loss observed or never observed | The first pass stops at the first `VK_ERROR_DEVICE_LOST`; if it reaches the end without one, the test passes. | [`first pass`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L247-L263) |

## Behavior Parameters

The primary behavioral axis is the fixed `maintenance5` leaf. There is no generated matrix of loss triggers or workload sizes. Optional device functionality changes which probes are meaningful, but not the property being checked.

### `maintenance5` — probe post-loss result propagation

The case requires `VK_KHR_maintenance5`, creates a universal queue, prepares a compute submission, and stores the operations under test as callable entries. Their order is significant: `queueSubmit`, optional `waitSemaphores`, `getEventStatus`, `waitForFences`, `getFenceStatus`, `deviceWaitIdle`, and optional `getQueryPoolResults` ([operation list](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L220-L245)).

The first pass uses the first fence, event, and optional timeline semaphore. It stops at the first `VK_ERROR_DEVICE_LOST`. A `VK_TIMEOUT` is reported as a quality warning, because the test did not establish the device-loss result within its five-second wait. If no operation returns device loss, the result is a pass with `DEVICE_LOST was never returned` ([result handling](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L247-L263)).

After loss is observed, the second pass switches to the second fence and event. Every applicable operation must return `VK_ERROR_DEVICE_LOST`; the sentinel result skips the optional semaphore and query operations when those facilities were not enabled. Any other result produces a quality warning naming the operation ([second pass](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L265-L280)).

## Shader Analysis

The compute shader is part of the workload that the test submits; it is not a shader-free exception. The following walkthrough reconstructs the exact source emitted by `DeviceLossCase::initPrograms` for the registered `dEQP-VK.postmortem.device_loss.maintenance5` case. The host dispatches one workgroup and pushes `{4, 0}` ([command recording](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L164-L184)); the source generator is at [`initPrograms`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L302-L320).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.postmortem.device_loss.maintenance5
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `local_size_x/y/z = 1/1/1` | The dispatch launches exactly one compute invocation for its single `(1, 1, 1)` workgroup. |
| push constants `{4, 0}` | `inp.x` starts the unsigned loop counter at 4 and `inp.y` is the lower comparison bound 0. |
| set 0, binding 0 storage buffer | The shader has one write-only storage-buffer destination, matching the host descriptor set and output buffer. |

#### Purpose

The shader creates a long-running unsigned loop before writing its counter to the storage buffer. With `{4, 0}`, incrementing eventually wraps to zero and resets the counter to 4, so the `i > 0` condition remains true. The resulting workload is submitted so later Vulkan calls can expose device-loss behavior.

#### Structural Design

```mermaid
flowchart TD
    A[Load pc.inp.x into i] --> B{i > pc.inp.y?}
    B -- no --> E[Store i to data.outp[0]]
    B -- yes --> C[i = i + 1]
    C --> D{i == 0 after wrap?}
    D -- yes --> F[Reset i to pc.inp.x]
    D -- no --> G[Keep incremented i]
    F --> B
    G --> B
```

The loop is unsigned. For the selected constants, `i` increases from 4 through the representable `uint` range; when the increment wraps to zero, the explicit reset returns it to 4. The shader therefore does not reach the final store during normal execution of this case.

#### Shader Code

```glsl
#version 320 es
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1)
layout(push_constant) uniform Constants { uvec2 inp; } pc;
layout(std430, set = 0, binding = 0) writeonly buffer Data { uint outp[]; } data;
void main()
{
  /// The host pushes {4, 0}; inp.x is the starting counter and inp.y is the loop bound.
  uint i = pc.inp.x;
  /// For the selected values, the loop remains active through unsigned wraparound.
  while (i > pc.inp.y)
  {
    i = i + uint(1);
    /// Resetting after wrap avoids terminating at zero and keeps the submitted workload running.
    if (i == uint(0))
      i = pc.inp.x;
  }
  /// This store is the normal loop exit, not the host-side pass/fail oracle.
  data.outp[0] = i;
}
```

#### Additional Info

- The shader has one invocation because both the local size and dispatch dimensions are one; there is no inter-invocation synchronization or race to analyze.
- The host allocates a one-`uint32_t` host-visible storage buffer and binds it at set 0, binding 0 ([buffer and descriptor setup](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L127-L153)).
- The shader's output is not read to decide pass or fail. The observable result is the `VkResult` returned by the operation sequence, so a driver may report device loss before the final store is reached.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| registered case | No shader branch varies: `maintenance5` is the only leaf and always emits this compute source. | [`case registration`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L336) |
| push constants | The source reads two unsigned values, but this test always pushes `{4, 0}`; no registered parameter selects another pair. | [`push and dispatch`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L169-L181) |
| optional pipeline statistics | Query recording surrounds the dispatch when supported, but it does not change the shader source or invocation count. | [`conditional query recording`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L171-L183) |

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
; Bound: 45
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource ESSL 320
               OpName %main "main"
               OpName %i "i"
               OpName %Constants "Constants"
               OpMemberName %Constants 0 "inp"
               OpName %pc "pc"
               OpName %Data "Data"
               OpMemberName %Data 0 "outp"
               OpName %data "data"
               OpDecorate %Constants Block
               OpMemberDecorate %Constants 0 Offset 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Data BufferBlock
               OpMemberDecorate %Data 0 NonReadable
               OpMemberDecorate %Data 0 Offset 0
               OpDecorate %data NonReadable
               OpDecorate %data Binding 0
               OpDecorate %data DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v2uint = OpTypeVector %uint 2
  %Constants = OpTypeStruct %v2uint
%_ptr_PushConstant_Constants = OpTypePointer PushConstant %Constants
         %pc = OpVariable %_ptr_PushConstant_Constants PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
%_runtimearr_uint = OpTypeRuntimeArray %uint
       %Data = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Data = OpTypePointer Uniform %Data
       %data = OpVariable %_ptr_Uniform_Data Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0 %uint_0
         %18 = OpLoad %uint %17
               OpStore %i %18
               OpBranch %19
         %19 = OpLabel
               OpLoopMerge %21 %22 None
               OpBranch %23
         %23 = OpLabel
         %24 = OpLoad %uint %i
         %26 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0 %uint_1
         %27 = OpLoad %uint %26
         %29 = OpUGreaterThan %bool %24 %27
               OpBranchConditional %29 %20 %21
         %20 = OpLabel
         %30 = OpLoad %uint %i
         %31 = OpIAdd %uint %30 %uint_1
               OpStore %i %31
         %32 = OpLoad %uint %i
         %33 = OpIEqual %bool %32 %uint_0
               OpSelectionMerge %35 None
               OpBranchConditional %33 %34 %35
         %34 = OpLabel
         %36 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0 %uint_0
         %37 = OpLoad %uint %36
               OpStore %i %37
               OpBranch %35
         %35 = OpLabel
               OpBranch %22
         %22 = OpLabel
               OpBranch %19
         %21 = OpLabel
         %42 = OpLoad %uint %i
         %44 = OpAccessChain %_ptr_Uniform_uint %data %int_0 %int_0
               OpStore %44 %42
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. `createPostmortemDevice` creates one universal queue and enables `VK_KHR_maintenance5`. It enables `pipelineStatisticsQuery` when the physical-device feature is available and adds the timeline-semaphore extension and feature only when supported ([device creation](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L47-L90)).
2. The instance creates the optional query pool, a host-visible storage buffer, descriptor set layout and descriptor set, shader module, pipeline layout, compute pipeline, command pool, and command buffer ([resource and pipeline setup](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L113-L167)).
3. The command buffer binds the compute pipeline and descriptor set, pushes `{4, 0}`, dispatches one workgroup, and optionally records compute-shader invocation statistics ([recording](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L169-L184)).
4. The first probe submits the command buffer and invokes the operations in source order. `VK_ERROR_DEVICE_LOST` ends the first pass successfully as evidence that loss was observed; `VK_TIMEOUT` returns a quality warning ([first pass](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L247-L259)).
5. If no operation reports device loss, the case passes with `DEVICE_LOST was never returned`. This is intentional: the workload is a trigger attempt, not a requirement that every implementation must lose the device ([no-loss result](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L261-L263)).
6. If loss was observed, the second pass uses the second fence and event and checks every applicable operation. A non-`VK_ERROR_DEVICE_LOST` result causes `Wrong VkResult for <operation>`; unavailable optional operations return `VK_RESULT_MAX_ENUM` and are skipped ([second-pass check](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L265-L280)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Observable symptom | Possible cause(s) |
|---|---|---|
| `maintenance5` during setup | The case is unsupported or cannot create the required device, resources, or pipeline. | `VK_KHR_maintenance5` is absent, or device/resource setup failed. The source does not localize the failing implementation layer. |
| `maintenance5` during the first pass | `Timeout exceeded`. | The submission or a wait did not complete within five seconds; this is a quality warning, not proof of inconsistent loss propagation. |
| `maintenance5` during the second pass | `Wrong VkResult for <operation>`. | After one operation reported loss, another applicable operation returned a different result. |

### Cause Analysis

#### Unsupported or incomplete setup

**Possible failure symptoms:** The case is skipped or setup fails before the operation sequence runs.

**Possible implementation causes:** The required extension or a resource needed to submit the workload is unavailable.

The support check requires `VK_KHR_maintenance5` before the test instance runs ([support check](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L297-L300)). Later setup also depends on ordinary device creation, memory allocation, descriptor binding, shader-module creation, and compute-pipeline creation. A setup problem means the propagation sequence was never tested; the source cannot by itself identify whether the root cause is a driver subsystem, hardware, or test environment.

#### Workload or wait timeout

**Possible failure symptoms:** The result is `Timeout exceeded`.

**Possible implementation causes:** The submission or a wait did not complete within five seconds.

The first pass uses a five-second timeout for waits. A `VK_TIMEOUT` is converted to `QP_TEST_RESULT_QUALITY_WARNING` with `Timeout exceeded` ([timeout constant and handling](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L186-L188), [first-pass handling](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L247-L259)). The result indicates that the test did not reach a definitive device-loss observation in the allotted time; it does not distinguish a slow implementation from a workload that completed without loss.

#### Inconsistent post-loss result

**Possible failure symptoms:** The warning is `Wrong VkResult for <operation>`.

**Possible implementation causes:** An applicable operation returned a result other than `VK_ERROR_DEVICE_LOST` after loss had already been observed.

The strongest failure signal is a second-pass operation returning something other than `VK_ERROR_DEVICE_LOST`, except for an unavailable optional probe marked by `VK_RESULT_MAX_ENUM`. The warning names the operation, which identifies the observed API boundary but does not prove whether the defect is in host-side dispatch, driver state propagation, or lower-level hardware behavior ([result check](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L265-L280)).

## Case Pruning

### Requirement-based pruning

- Implementations without `VK_KHR_maintenance5` are skipped by `checkSupport` ([requirement](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L297-L300)).
- Timeline-semaphore creation and `waitSemaphores` probing are conditional on `VK_KHR_timeline_semaphore` support ([device feature setup](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L61-L75), [conditional operation](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L224-L233)).
- Pipeline-statistics query creation, recording, and result probing are conditional on `pipelineStatisticsQuery` ([query setup](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L113-L125), [query operation](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L239-L245)).

### Design-based pruning

- The registration exposes one leaf, `maintenance5`; there is no source-defined matrix of loop bounds, dispatch sizes, or loss-trigger variants ([registration](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L336)).
- The second pass skips `waitSemaphores` and `getQueryPoolResults` when their first-pass entries are unavailable, represented by `VK_RESULT_MAX_ENUM` ([sentinel handling](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L269-L275)).
- The standard `vk-default` profile does not contain this experimental group. It must not be described as default-profile coverage ([mustpass](../../../mustpass/main/vk-default/postmortem.txt#L1-L24)).

## Key Takeaways

- `postmortem.device_loss.maintenance5` is one experimental leaf, not a standard `vk-default` mustpass entry.
- Its compute shader is a deliberate long-running workload with one invocation, a two-value push-constant interface, and a storage-buffer store that normally follows loop termination.
- The shader output is not the correctness oracle. The test observes `VkResult` values from a fixed sequence of operations.
- A device that never reports `VK_ERROR_DEVICE_LOST` passes. After loss is observed, every applicable later probe must report `VK_ERROR_DEVICE_LOST`.
- Optional timeline-semaphore and pipeline-statistics probes extend the operation list only when supported.
- A failure identifies a timeout or an inconsistent result at a named API boundary; it does not, by itself, identify the responsible implementation layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Experimental postmortem registration | [`createChildrenExperimental`](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L47-L65) | Shows why the group is experimental and outside the standard root. |
| Device construction | [`createPostmortemDevice`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L47-L90) | Defines queue, required extension, and optional functionality. |
| Test execution | [`DeviceLossInstance::iterate`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L104-L280) | Creates resources, records and submits the workload, probes operations, and checks results. |
| Support and shader generation | [`checkSupport` and `initPrograms`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L297-L320) | Defines the required extension and exact compute shader. |
| Case registration | [`createDeviceLossTests`](../../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L336) | Registers `device_loss.maintenance5`. |
| Standard mustpass boundary | [`postmortem.txt`](../../../mustpass/main/vk-default/postmortem.txt#L1-L24) | Confirms that default coverage contains device-fault cases, not this experimental group. |
