## Overview

**Core question:** Can independent compute and graphics submissions on separate logical devices and queues both complete correctly while they are in flight in the same test?

This page documents `vktDrawConcurrentTests.cpp`. The implementation registers one fixed test case, `compute_and_triangle_list`, under the render-pass path and three non-nested dynamic-rendering command-buffer paths. It creates a second logical device and queue for compute work, uses the normal context device and universal queue for graphics work, submits the two workloads separately, waits for both fences, and validates the rendered image. Normal Vulkan execution, and Vulkan SC subprocess execution, also validate the storage-buffer result.

The workloads do not share resources and have no producer-consumer dependency: the compute shader modifies a storage buffer, while the graphics pipeline renders to a separate color target. The intended contract is that each independent submission remains correct while both may be in flight. The current source has a device-interface mismatch in the draw fence and submission path; this source-level issue is described under `Submission and ordering` and `Failure Meaning`.

## Background Knowledge

For the shared concepts of render passes, dynamic rendering, and result readback, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- Different Vulkan queues may be scheduled independently. Submission to one queue does not implicitly order work on another queue, and independent resources need no cross-queue memory dependency.
- A logical device owns its queues and device-level objects. A device-level function pointer obtained for one device must be called only with that device or one of its child objects; this ownership rule is necessary to understand the source-level mismatch discussed later.
- Host writes to mapped memory must be made available to the device, and shader writes must be made available and visible before host readback. Flush/invalidate operations and buffer memory barriers provide the relevant host/device transitions.
- A fence is a device object associated with a queue submission. Waiting for it lets the host observe completion of that submission; it does not create a dependency on an independent submission to another queue.

Relevant Vulkan specification topics are [device queues](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#devsandqueues), [fences](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#synchronization-fences), [host access types](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#synchronization-host-access-types), [`vkGetDeviceProcAddr`](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkGetDeviceProcAddr.html), and [`vkWaitForFences`](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkWaitForFences.html).

## Registration Hierarchy

```text
draw.renderpass.concurrent
└── compute_and_triangle_list

draw.dynamic_rendering.primary_cmd_buff.concurrent
└── compute_and_triangle_list

draw.dynamic_rendering.partial_secondary_cmd_buff.concurrent
└── compute_and_triangle_list

draw.dynamic_rendering.complete_secondary_cmd_buff.concurrent
└── compute_and_triangle_list
```

`concurrent` and `compute_and_triangle_list` are the exact identifiers registered by `ConcurrentDrawTests`. The shared draw dispatcher instantiates the family once for the render-pass path and once for each non-nested dynamic-rendering command-buffer path. It deliberately omits `concurrent` from the two nested secondary-command-buffer paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Rendering path | `renderpass`; `dynamic_rendering.primary_cmd_buff`; `dynamic_rendering.partial_secondary_cmd_buff`; `dynamic_rendering.complete_secondary_cmd_buff` | Selects legacy render-pass recording or one of the supported primary/secondary dynamic-rendering arrangements. | [`createTests` and `createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) |
| Test case | `compute_and_triangle_list` | Selects the one fixed pair of independent compute and graphics workloads. | [`ConcurrentDrawTests::init`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L535-L546) |
| Graphics shaders | `vulkan/draw/VertexFetch.vert`, `vulkan/draw/VertexFetch.frag` | Produces a blue rectangle only when the fetched reference vertex indices match `gl_VertexIndex`. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541) |
| Compute shader | `vulkan/draw/ConcurrentPayload.comp` | Replaces every storage-buffer value with its bitwise complement. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541), [`ConcurrentPayload.comp`](../../../data/vulkan/draw/ConcurrentPayload.comp) |
| Graphics topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` | Interprets the six drawn vertices as two triangles. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541) |
| Compute input and dispatch | 1024 `uint32_t` values; `vkCmdDispatch(1, 1, 1)` | One compute invocation loops over all 1024 elements. | [`numValues`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L117), [`dispatch`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L303-L312) |
| Graphics draw call | `vkCmdDraw(..., 6, 1, 2, 0)` | Draws six vertices beginning at vertex 2; only the first stored rectangle is consumed. | [`graphics recording`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L333-L395) |

## Behavior Parameters

This test family has no varying behavioral axis. Its sole test case always runs one storage-buffer compute workload and one triangle-list graphics workload, then checks their outputs independently. The rendering path changes command-buffer and rendering setup, not the property checked by the fixed case.

## Shader Analysis

The fixed case has two independent shader contracts and therefore uses two walkthroughs. The compute walkthrough covers the storage-buffer result, while the graphics walkthrough covers the vertex-index signal that reaches the color attachment. There is no shader dataflow between them.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.concurrent.compute_and_triangle_list
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute_and_triangle_list` | Registers `ConcurrentPayload.comp` alongside the separate vertex/fragment graphics pipeline. |
| `vkCmdDispatch(1, 1, 1)` with `local_size = (1, 1, 1)` | Creates one invocation, which processes all 1024 storage-buffer elements. |
| Storage buffer binding `0` | Exposes the host-initialized `uint[1024]` array as the compute result resource. |

#### Purpose

The compute shader independently proves that the compute submission ran to completion by replacing every input word with its bitwise complement for host validation.

#### Structural Design

| Phase | Exact-case operation | Observable contract |
|-------|----------------------|---------------------|
| Work partition | Multiply `gl_NumWorkGroups` by `gl_WorkGroupSize`, then derive a per-invocation slice. | One dispatched invocation obtains offset 0 and length 1024. |
| Payload update | Apply unary bitwise NOT to every word in that slice. | `values[i]` becomes `~inputData[i]` for every index. |
| Independent validation | The host invalidates and reads the storage-buffer allocation after the compute fence. | A single unequal word fails the compute result independently of image comparison. |

#### Shader Code

```glsl
#version 310 es

/// One 1x1x1 workgroup is dispatched, so one global invocation owns all 1024 elements.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Descriptor set 0, binding 0 is the host-visible 4096-byte storage buffer checked after completion.
layout(binding = 0) buffer InOut {
    uint values[1024];
} sb_inout;

void main (void) {
    /// Derive a contiguous slice per invocation; this case has size=(1,1,1), groupNdx=0, and a 1024-value slice.
    uvec3 size           = gl_NumWorkGroups * gl_WorkGroupSize;
    uint numValuesPerInv = uint(sb_inout.values.length()) / (size.x*size.y*size.z);
    uint groupNdx        = size.x*size.y*gl_GlobalInvocationID.z + size.x*gl_GlobalInvocationID.y + gl_GlobalInvocationID.x;
    uint offset          = numValuesPerInv*groupNdx;

    /// Complement each assigned value in place; the host later compares every element with ~inputData[ndx].
    for (uint ndx = 0u; ndx < numValuesPerInv; ndx++)
        sb_inout.values[offset + ndx] = ~sb_inout.values[offset + ndx];
}
```

#### Additional Info

- The host binds exactly 4096 bytes (`1024 * sizeof(uint32_t)`) to descriptor set 0, binding 0, and records host-to-compute and compute-to-host buffer barriers around the dispatch ([compute setup and recording](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L234-L312)).
- No explicit `ShaderBuildOptions` accompanies the data-file shader registration, so the CTS baseline target is SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Rendering path | None. Render-pass versus dynamic-rendering selection changes only graphics command recording; the same compute module, descriptor, and `1 x 1 x 1` dispatch are used. | [`ConcurrentDraw::iterate`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L286-L395) |
| Registered case | None. The family registers only `compute_and_triangle_list`, with this fixed compute shader. | [`ConcurrentDrawTests::init`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L535-L546) |

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
; Bound: 84
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource ESSL 310
               OpName %main "main"
               OpName %size "size"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %numValuesPerInv "numValuesPerInv"
               OpName %groupNdx "groupNdx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %offset "offset"
               OpName %ndx "ndx"
               OpName %InOut "InOut"
               OpMemberName %InOut 0 "values"
               OpName %sb_inout "sb_inout"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_uint_uint_1024 ArrayStride 4
               OpDecorate %InOut BufferBlock
               OpMemberDecorate %InOut 0 Offset 0
               OpDecorate %sb_inout Binding 0
               OpDecorate %sb_inout DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
%_ptr_Function_uint = OpTypePointer Function %uint
  %uint_1024 = OpConstant %uint 1024
     %uint_0 = OpConstant %uint 0
     %uint_2 = OpConstant %uint 2
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
       %bool = OpTypeBool
%_arr_uint_uint_1024 = OpTypeArray %uint %uint_1024
      %InOut = OpTypeStruct %_arr_uint_uint_1024
%_ptr_Uniform_InOut = OpTypePointer Uniform %InOut
   %sb_inout = OpVariable %_ptr_Uniform_InOut Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %size = OpVariable %_ptr_Function_v3uint Function
%numValuesPerInv = OpVariable %_ptr_Function_uint Function
   %groupNdx = OpVariable %_ptr_Function_uint Function
     %offset = OpVariable %_ptr_Function_uint Function
        %ndx = OpVariable %_ptr_Function_uint Function
         %12 = OpLoad %v3uint %gl_NumWorkGroups
         %15 = OpIMul %v3uint %12 %gl_WorkGroupSize
               OpStore %size %15
         %20 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %21 = OpLoad %uint %20
         %22 = OpAccessChain %_ptr_Function_uint %size %uint_1
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %21 %23
         %26 = OpAccessChain %_ptr_Function_uint %size %uint_2
         %27 = OpLoad %uint %26
         %28 = OpIMul %uint %24 %27
         %29 = OpUDiv %uint %uint_1024 %28
               OpStore %numValuesPerInv %29
         %31 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %32 = OpLoad %uint %31
         %33 = OpAccessChain %_ptr_Function_uint %size %uint_1
         %34 = OpLoad %uint %33
         %35 = OpIMul %uint %32 %34
         %38 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %39 = OpLoad %uint %38
         %40 = OpIMul %uint %35 %39
         %41 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %42 = OpLoad %uint %41
         %43 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %44 = OpLoad %uint %43
         %45 = OpIMul %uint %42 %44
         %46 = OpIAdd %uint %40 %45
         %47 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %48 = OpLoad %uint %47
         %49 = OpIAdd %uint %46 %48
               OpStore %groupNdx %49
         %51 = OpLoad %uint %numValuesPerInv
         %52 = OpLoad %uint %groupNdx
         %53 = OpIMul %uint %51 %52
               OpStore %offset %53
               OpStore %ndx %uint_0
               OpBranch %55
         %55 = OpLabel
               OpLoopMerge %57 %58 None
               OpBranch %59
         %59 = OpLabel
         %60 = OpLoad %uint %ndx
         %61 = OpLoad %uint %numValuesPerInv
         %63 = OpULessThan %bool %60 %61
               OpBranchConditional %63 %56 %57
         %56 = OpLabel
         %70 = OpLoad %uint %offset
         %71 = OpLoad %uint %ndx
         %72 = OpIAdd %uint %70 %71
         %73 = OpLoad %uint %offset
         %74 = OpLoad %uint %ndx
         %75 = OpIAdd %uint %73 %74
         %77 = OpAccessChain %_ptr_Uniform_uint %sb_inout %int_0 %75
         %78 = OpLoad %uint %77
         %79 = OpNot %uint %78
         %80 = OpAccessChain %_ptr_Uniform_uint %sb_inout %int_0 %72
               OpStore %80 %79
               OpBranch %58
         %58 = OpLabel
         %81 = OpLoad %uint %ndx
         %83 = OpIAdd %uint %81 %int_1
               OpStore %ndx %83
               OpBranch %55
         %57 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

```text
Choose physical device and compute queue family
  -> create custom compute device and queue
  -> allocate host-visible storage buffer and fill 1024 random uint32 values
  -> bind buffer to ConcurrentPayload.comp and record barriers + dispatch
  -> prepare shared graphics draw and record the selected rendering path
  -> submit compute and graphics to their queues with separate fences
  -> wait for both fences
  -> validate bitwise-NOT buffer result and fuzzy image result
```

### Compute workload

The implementation searches physical-device queue families for the first family advertising `VK_QUEUE_COMPUTE_BIT`. If none is found, it throws `NotSupportedError` with `Compute queue couldn't be created`. A custom device is created with that family and one queue. The buffer is host-visible, contains 1024 values generated from deterministic seed `0x82ce7f`, and is bound as one storage-buffer descriptor.

The compute command buffer binds `ConcurrentPayload.comp`, inserts the host-write/compute-read buffer barrier, dispatches one workgroup (`vkCmdDispatch(1, 1, 1)`), and inserts the compute-write/host-read barrier. The shader's result contract is one bitwise complement per input value.

### Graphics workload

`ConcurrentDraw` derives from `DrawTestsBaseClass`. Its vertex data contains two setup vertices, 1000 repetitions of the same six-vertex blue rectangle, and one trailing vertex. The draw starts at vertex 2 and consumes only six vertices, so only the first repeated rectangle reaches the graphics pipeline. The remaining repetitions enlarge the allocated and uploaded vertex buffer but do not increase the GPU draw count.

The base class handles graphics pipeline and attachment setup. Depending on `SharedGroupParams`, the source records legacy rendering, primary-command-buffer dynamic rendering, or one of two secondary-command-buffer dynamic-rendering arrangements. The graphics queue is `m_context.getUniversalQueue()` on the normal context device.

### Submission and ordering

The compute submission has no wait or signal semaphores and is sent to the custom compute queue with `computeFence`. The intended graphics submission likewise has no semaphores and targets the universal draw queue with `drawFence`. This lack of cross-queue synchronization is deliberate because the workloads are independent. Both fence waits are attempted before a wait error is returned.

The current source does not consistently use the two devices' dispatch interfaces. It constructs `vk` as a `DeviceDriver` for the custom compute device, then passes the context device and its universal queue through that compute-device interface when creating `drawFence`, submitting the graphics command buffer, and waiting for `drawFence` ([source](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L217-L230), [draw path](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L397-L437)). The Vulkan requirement for a device-specific function pointer is that its first dispatchable object be that device or one of its children. The page therefore documents the intended draw submission and the observed mismatch, rather than claiming that this source path is valid.

### Result checking

After both waits, normal Vulkan builds invalidate the compute allocation and require every element to equal `~inputData[ndx]`. A mismatch reports the index, reference, result, and input value. In Vulkan SC, both the wait-result checks and the compute-buffer comparison are inside the subprocess-only block, so a non-subprocess run proceeds directly to graphics validation.

The graphics reference is opaque black with an opaque blue rectangle inside `ReferenceImageCoordinates`. The color attachment is read in `VK_IMAGE_LAYOUT_GENERAL` and compared with `tcu::fuzzyCompare` at threshold `0.05`; an image mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

The fixed case can fail through a fence wait, a compute-buffer mismatch, or an image mismatch. These observations localize the failure to completion of one submission or to the corresponding independent workload; an image mismatch is not evidence that graphics failed to consume compute output, because no such data flow exists.

### Cause Analysis

The source-level mismatch below can invalidate both submission observations. If that path is corrected, the remaining checks localize failures as follows.

#### Device-interface mismatch in the source

**Possible failure symptoms:** Device/queue validation errors, a draw submission or fence wait that does not complete successfully, or inability to reach reliable output validation.

**Possible implementation causes:** This is an unresolved CTS source-level issue, not an inferred implementation defect. `vk` is constructed for `computeDevice` at lines 217-230, but it is used with `drawDevice` and `drawQueue` at lines 400 and 428-437. The Vulkan [`vkGetDeviceProcAddr` requirement](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkGetDeviceProcAddr.html) restricts a returned device function pointer to its device and that device's children.

#### Compute completion or output

**Possible failure symptoms:** The compute fence wait fails, or at least one of the 1024 elements differs from the bitwise complement of its saved input.

**Possible implementation causes:** On a valid submission path, investigate compute command execution, descriptor or pipeline binding, shader execution, mapped-memory flush/invalidate handling, and the host/compute buffer barriers.

#### Graphics completion or output

**Possible failure symptoms:** The draw fence wait fails, or the captured image differs from the black-and-blue reference beyond the fuzzy comparison threshold.

**Possible implementation causes:** On a valid submission path, investigate graphics command recording and execution, vertex fetching and `gl_VertexIndex`, primitive assembly and rasterization, color attachment handling, and image readback.

## Case Pruning

### Requirement-based pruning

- A queue family with `VK_QUEUE_COMPUTE_BIT` is required; otherwise the test throws `NotSupportedError` rather than reporting a conformance failure.
- A dynamic-rendering path requires `VK_KHR_dynamic_rendering` through `context.requireDeviceFunctionality`.
- Dynamic rendering is excluded from Vulkan SC by the dispatcher build guard.

### Design-based pruning

- The dispatcher omits `concurrent` from the nested partial and nested complete secondary-command-buffer paths because `createChildren` adds it only when `nestedSecondaryCmdBuffer` is false.
- The family has one fixed case. Shared-resource, semaphore, queue-family ownership-transfer, and compute-to-graphics producer-consumer variants are outside its design.

## Key Takeaways

- `compute_and_triangle_list` runs independent compute and graphics workloads on separate logical devices and queues; the graphics shader does not consume the compute buffer.
- The Vulkan mustpass contains the render-pass path and three non-nested dynamic-rendering paths, while nested secondary-command-buffer paths are intentionally omitted.
- A passing result requires the 1024-element bitwise-NOT buffer check and the fuzzy blue-rectangle image check to succeed after the fence waits.
- The current source routes draw-device operations through the compute device's `DeviceDriver`; this remains an unresolved source-level defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test implementation | [`ConcurrentDraw::iterate`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L101-L518) | Creates both workloads, submits them, and checks their results. |
| Compute setup and recording | [queue, device, buffer, pipeline, barriers, and dispatch](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L117-L324) | Defines the custom compute path and its output contract. |
| Graphics recording | [rendering-path branches and draw](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L326-L395) | Defines the supported graphics command-buffer arrangements. |
| Submission and validation | [fences, submissions, waits, and checks](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L397-L518) | Exposes the device-interface mismatch and both result oracles. |
| Family registration | [`ConcurrentDrawTests`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L528-L546) | Supplies the exact `concurrent.compute_and_triangle_list` identifiers. |
| Draw dispatcher | [`createChildren` and `createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) | Places the family under render-pass and non-nested dynamic-rendering paths. |
| Shared draw base | [`DrawTestsBaseClass`](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L216) | Creates the graphics resources, pipeline, vertex buffer, and attachment barriers. |
| Shader inputs | [`ConcurrentPayload.comp`](../../../data/vulkan/draw/ConcurrentPayload.comp), [`VertexFetch.vert`](../../../data/vulkan/draw/VertexFetch.vert), [`VertexFetch.frag`](../../../data/vulkan/draw/VertexFetch.frag) | Defines the compute complement and blue-rectangle shader outputs. |
| Vulkan mustpass | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L346), [`renderpass entry`](../../../mustpass/main/vk-default/draw.txt#L17808), [`Vulkan SC entry`](../../../mustpass/main/vksc-default/draw.txt#L330) | Confirms the registered Vulkan variants and Vulkan SC render-pass path. |
| Class declaration | [`vktDrawConcurrentTests.hpp`](../../../modules/vulkan/draw/vktDrawConcurrentTests.hpp) | Declares the family and its shared group parameters. |
