## Overview

**Core question:** Does each pipeline bind point retain its own pipeline or shader-object state and descriptor state when two types of work are recorded and executed in different orders?

- `vktPipelineBindPointTests.cpp` implements the `pipeline.bind_point` test family and registers the `graphics_compute`, `graphics_raytracing`, and `compute_raytracing` intermediate nodes ([registration](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083)).
- Each test case selects two bind points, one descriptor update route for each, a permutation of four setup operations, and a permutation of two execution operations. For shader-object construction variants, the graphics setup operation binds graphics shader objects and dynamic state instead of a `VkPipeline`; compute and ray tracing still use pipelines.
- The selected shaders write distinct values to separate storage buffers. Graphics cases also write a known color to a 1×1 attachment, so a wrong bind-point association reaches host-visible checks.
- The `compute_raytracing` family is present only for monolithic pipeline construction. Non-monolithic construction types retain the two pairs that include graphics.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A pipeline bind point associates a pipeline with the command class that uses it. Vulkan maps graphics shader stages to `VK_PIPELINE_BIND_POINT_GRAPHICS` and draw commands, compute to `VK_PIPELINE_BIND_POINT_COMPUTE` and dispatch commands, and ray-tracing stages to `VK_PIPELINE_BIND_POINT_RAY_TRACING_KHR` and trace-rays commands ([Vulkan shader binding](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800)).
- Descriptor commands use a pipeline bind point and pipeline layout to establish the descriptor state consumed by that pipeline. Push-descriptor update templates also store the intended bind point, layout, and set number ([descriptor update template fields](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4174-L4209)).

## Registration Hierarchy

```text
pipeline.monolithic.bind_point
├── graphics_compute
├── graphics_raytracing
└── compute_raytracing
```

The source registers the same `bind_point` family under the monolithic, pipeline-library, fast-linked-library, and shader-object construction variants. Only the monolithic variant includes `compute_raytracing`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Bind-point pair | `graphics_compute`, `graphics_raytracing`, `compute_raytracing` | Selects the two independent pipeline or shader-object and descriptor-state paths tested together. | [`testPairs`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L961-L966) |
| Descriptor update route for each selected bind point | `write`, `push`, `template_push` | Selects allocated descriptor-set binding, direct push descriptors, or push descriptors populated through a template. | [`SetUpdateType` conversion](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L854-L869), [registration loops](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1032-L1045) |
| Setup order | 24 permutations of pipeline or graphics-shader-object setup and descriptor binds | Checks whether setup order changes the state later consumed at each bind point. | [`setupSequence`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1047-L1075) |
| Execution order | Two permutations of the selected operations | Checks both orders of draw, dispatch, and trace-rays work. | [`dispatchSequence`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1060-L1070) |
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_linked_binary`, `shader_object_linked_spirv`, `shader_object_unlinked_binary`, `shader_object_unlinked_spirv` | Reuses the same bind-point behavior through supported pipeline construction paths. | [`createBindPointTests` parameter](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L973) |

Each pair has 9 ordered descriptor-route combinations, 24 setup orders, and 2 execution orders, for 432 test case leaves. The monolithic family has 1,296 leaves. Each inspected non-monolithic mustpass list has 864 leaves because it contains only the two graphics-containing pairs.

## Behavior Parameters

The primary behavioral axis is the registered bind-point pair. It changes the pipeline stages, command types, resources, feature requirements, and failure localization, while the update routes and order permutations exercise the same state-separation question within each pair.

### `graphics_compute`: graphics and compute state separation

The test prepares graphics state and binds a compute pipeline, supplies one descriptor path for each, then records a draw and a dispatch in both possible orders. The graphics state comes from a graphics pipeline in pipeline-based construction variants and graphics shader objects plus dynamic state in shader-object variants. The fragment shader writes `1` to the graphics buffer and green to the attachment; the compute shader writes `2` to the compute buffer.

### `graphics_raytracing`: graphics and ray-tracing state separation

The test combines a graphics draw with one ray-tracing dispatch. The fragment shader writes `1` and green, while the ray-generation shader writes `3` to its separate buffer. This value also exercises the graphics pipeline or shader-object path and the ray-tracing pipeline and shader binding table setup.

### `compute_raytracing`: compute and ray-tracing state separation

The test combines a compute dispatch with one ray-tracing dispatch. The shaders write `2` and `3` to their separate buffers. The source intentionally excludes this pair from non-monolithic construction variants because those variants skip pairs without graphics.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.bind_point.graphics_compute.push_push.setup_cp_cs_gp_gs.cmd_dispatch_draw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `graphics_compute` | Pairs a graphics draw with a compute dispatch so their independently bound descriptor and executable state can be observed through distinct sentinel writes. |
| `push_push` | Both bind points receive binding 0 through direct push descriptors, but each push targets its own pipeline bind point and layout. |
| `setup_cp_cs_gp_gs` | Records compute pipeline, compute descriptor, graphics shader objects/state, and graphics descriptor setup in that order. |
| `cmd_dispatch_draw` | Executes the compute dispatch before the graphics draw, testing that the later draw still consumes the graphics state rather than the compute state. |
| `shader_object_linked_binary` | Uses linked binary shader objects for graphics while compute remains a compute pipeline; the generated GLSL is shared with the other construction variants. |

#### Purpose

The fragment and compute shaders turn bind-point-specific state into separate host-visible sentinels. The case passes only if the dispatch writes `2` through the compute descriptor path and the later draw writes `1` plus green through the graphics path.

#### Structural Design

| Bind-point path | Shader-visible resource or output | Shader action | Host observation |
|-----------------|-----------------------------------|---------------|------------------|
| Compute | Set 0, binding 0 storage buffer | One invocation writes `2u` to `flag[0]` | Compute buffer equals `2` |
| Graphics | Set 0, binding 0 storage buffer | The sole fragment writes `1u` to `flag[0]` | Graphics buffer equals `1` |
| Graphics | Location 0 color output | The sole fragment writes `(0, 1, 0, 1)` | The 1×1 attachment is green |

#### Shader Code

##### Fragment Shader

```glsl
#version 450
/// Binding 0 is a four-byte, host-visible storage buffer selected through the graphics bind point;
/// this fragment invocation writes the graphics sentinel to its only uint element.
layout(set=0, binding=0, std430) buffer BufferBlock { uint flag[]; } outBuffer;
/// The 1x1 R8G8B8A8_UNORM color attachment provides a second graphics-path observation.
layout(location=0) out vec4 outColor;

void main()
{
  /// The sole fragment has gl_FragCoord.xy equal to (0.5, 0.5), so both truncations are zero.
  const uint xCoord = uint(trunc(gl_FragCoord.x));
  const uint yCoord = uint(trunc(gl_FragCoord.y));
  outBuffer.flag[xCoord + yCoord] = 1u;
  outColor = vec4(0.0, 1.0, 0.0, 1.0);
}
```

##### Compute Shader

```glsl
#version 450
/// Binding 0 is the compute bind point's separate four-byte, host-visible storage buffer.
layout(set=0, binding=0, std430) buffer BufferBlock { uint flag[]; } outBuffer;
/// The host dispatches one 1x1x1 workgroup, so exactly one invocation executes.
layout(local_size_x=1, local_size_y=1, local_size_z=1) in;

void main()
{
  /// The sole global invocation has ID (0, 0, 0), selecting the buffer's only uint element.
  const uint index = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y + gl_GlobalInvocationID.z;
  outBuffer.flag[index] = 2u;
}
```

#### Additional Info

- The compute shader stays fixed across the `graphics_compute` cases. It is shown because its `2u` write is the independent observation paired with the primary fragment shader's `1u` write.
- The fixed vertex shader is omitted: it only synthesizes a full-screen four-vertex triangle strip and does not consume descriptor state. Its coverage causes the single fragment invocation in the 1×1 attachment.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Bind-point pair | Replacing compute with ray tracing replaces the compute shader's `2u` write with a ray-generation shader's `3u` write; the compute/ray-tracing pair omits the graphics stages entirely. | [`BindPointTest::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L212-L280) |
| Descriptor update route | `write`, `push`, and `template_push` do not change shader text or binding numbers; they change how the host populates set 0, binding 0 for each bind point. | [descriptor setup](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L627-L669) |
| Setup and execution order | The 24 setup permutations and two execution orders reuse the same shaders and sentinels; only command-state ordering changes. | [setup and execution loops](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L671-L799) |
| Pipeline construction type | The GLSL remains unchanged. Construction type selects whether graphics uses a pipeline or graphics shader objects and controls whether the `compute_raytracing` pair is registered. | [registration and pruning](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083) |
| Ray-generation target | Ray-tracing variants explicitly compile the generated ray-generation shader for SPIR-V 1.4; this graphics fragment uses the default baseline SPIR-V 1.0 target. | [ray-generation build options](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L264-L279) |

#### SPIR-V

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 41
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %xCoord "xCoord"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %yCoord "yCoord"
               OpName %BufferBlock "BufferBlock"
               OpMemberName %BufferBlock 0 "flag"
               OpName %outBuffer "outBuffer"
               OpName %outColor "outColor"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %BufferBlock BufferBlock
               OpMemberDecorate %BufferBlock 0 Offset 0
               OpDecorate %outBuffer Binding 0
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
%_runtimearr_uint = OpTypeRuntimeArray %uint
%BufferBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_BufferBlock = OpTypePointer Uniform %BufferBlock
  %outBuffer = OpVariable %_ptr_Uniform_BufferBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %40 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %xCoord = OpVariable %_ptr_Function_uint Function
     %yCoord = OpVariable %_ptr_Function_uint Function
         %15 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %16 = OpLoad %float %15
         %17 = OpExtInst %float %1 Trunc %16
         %18 = OpConvertFToU %uint %17
               OpStore %xCoord %18
         %21 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %22 = OpLoad %float %21
         %23 = OpExtInst %float %1 Trunc %22
         %24 = OpConvertFToU %uint %23
               OpStore %yCoord %24
         %31 = OpLoad %uint %xCoord
         %32 = OpLoad %uint %yCoord
         %33 = OpIAdd %uint %31 %32
         %35 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0 %33
               OpStore %35 %uint_1
               OpStore %outColor %40
               OpReturn
               OpFunctionEnd
```

</details>

##### Compute Shader

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
; Bound: 34
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %index "index"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %BufferBlock "BufferBlock"
               OpMemberName %BufferBlock 0 "flag"
               OpName %outBuffer "outBuffer"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %BufferBlock BufferBlock
               OpMemberDecorate %BufferBlock 0 Offset 0
               OpDecorate %outBuffer Binding 0
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
%_runtimearr_uint = OpTypeRuntimeArray %uint
%BufferBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_BufferBlock = OpTypePointer Uniform %BufferBlock
  %outBuffer = OpVariable %_ptr_Uniform_BufferBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIAdd %uint %15 %18
         %21 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %22 = OpLoad %uint %21
         %23 = OpIAdd %uint %19 %22
               OpStore %index %23
         %30 = OpLoad %uint %index
         %32 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0 %30
               OpStore %32 %uint_2
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `iterate()` creates one host-visible storage buffer for each selected bind point and clears each buffer before recording ([buffer setup](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L428-L454)). Graphics cases additionally create a 1×1 `VK_FORMAT_R8G8B8A8_UNORM` color attachment and framebuffer ([graphics attachment](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L456-L485)).
- The test creates a descriptor-set layout with one `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` binding and a separate pipeline layout for each selected bind point ([set layouts](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L492-L519)). Depending on the route, it allocates and writes a descriptor set, pushes a descriptor, or pushes through a `VkDescriptorUpdateTemplate` configured for the matching bind point and layout ([descriptor setup](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L627-L669)).
- The four setup operations are recorded in the selected order. Each operation binds pipeline state, graphics shader-object state, or descriptor state for the corresponding command class. In shader-object construction variants, `GraphicsPipelineWrapper::bind()` uses `vkCmdBindShadersEXT` and sets the required dynamic graphics state rather than calling `vkCmdBindPipeline` ([graphics wrapper binding](../../../framework/vulkan/vkPipelineConstructionUtil.cpp#L4721-L4761)). The test tracks the setup operations and asserts that both required operations precede the matching draw, dispatch, or trace-rays command ([setup loop](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L671-L769)).
- The selected execution operations are recorded in one of two orders. Graphics begins and ends a render pass around `vkCmdDraw`; compute uses `vkCmdDispatch`; ray tracing uses `cmdTraceRays` with a one-entry ray-generation shader binding table ([execution loop](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L771-L799)).
- After the selected shader stages write their buffers, the test records shader-write to host-read buffer barriers, ends the command buffer, submits it to the universal queue, and waits ([barriers and submission](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L801-L818)).
- The host invalidates and checks each selected storage buffer. Graphics cases also read the attachment and compare every pixel with `(0.0, 1.0, 0.0, 1.0)` ([result checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L820-L849)). Every selected observation must pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_compute` | Graphics and compute pipeline or shader-object and descriptor state is not kept independent across the selected setup and execution orders. |
| `graphics_raytracing` | Graphics and ray-tracing pipeline or shader-object and descriptor state is not kept independent, or the ray-tracing path is handled incorrectly. |
| `compute_raytracing` | Compute and ray-tracing pipeline or descriptor state is not kept independent. This pair is registered only for monolithic construction. |

### Cause Analysis

#### Graphics and compute state association

**Possible failure symptoms:** The graphics buffer does not contain `1`, the compute buffer does not contain `2`, or a graphics attachment pixel differs from the expected green value. A failure limited to one execution order or descriptor-route combination narrows the failing state transition, but does not by itself identify one API call.

**Possible implementation causes:** The implementation may associate pipeline, shader-object, or descriptor state with the wrong command class or `VkPipelineBindPoint`, fail to preserve bind-point-specific state across later binds, or mishandle a descriptor-set, push-descriptor, or update-template command. The source binds each descriptor route with the selected bind point and layout, while Vulkan defines the relationship between shader stages, bind points, and commands in the shader-binding table ([Vulkan bind-point contract](../../../../vulkan-docs/src/chapters/shaders.adoc#L1750-L1800)). Source-level investigation is needed to localize a particular failure.

#### Graphics and ray-tracing state association

**Possible failure symptoms:** The graphics buffer or green attachment check fails, the ray-tracing buffer does not contain `3`, or only one of the two execution orders fails. A failure in the ray-tracing path can also indicate that the required ray-generation dispatch did not use the expected pipeline state.

**Possible implementation causes:** The implementation may mix graphics pipeline or shader-object state with ray-tracing state, use the wrong bind point for a descriptor route, mishandle the ray-tracing pipeline or shader binding table, or lower the ray-generation shader incorrectly. Vulkan requires a ray-tracing pipeline to be bound before ray-tracing commands are recorded ([ray-tracing commands](../../../../vulkan-docs/src/chapters/raytracing.adoc#L222-L239)). The test source and specification identify the contract, but source-level investigation is needed to locate a specific defect.

#### Compute and ray-tracing state association

**Possible failure symptoms:** The compute buffer does not contain `2`, the ray-tracing buffer does not contain `3`, or the failure depends on setup or execution order. There is no graphics attachment in this pair, so the two buffer checks are the observable result.

**Possible implementation causes:** The implementation may confuse compute and ray-tracing pipeline state, apply a descriptor binding to the wrong bind point, mishandle `vkCmdDispatch` or `vkCmdTraceRaysKHR`, or use an incorrect ray-tracing pipeline or shader binding table. The test intentionally registers this pair only for monolithic construction, so a failure in that scope remains a monolithic bind-point or shared resource-path issue until source-level investigation narrows it further.

#### Shared descriptor and result-transport paths

**Possible failure symptoms:** Several bind-point pairs or descriptor-route combinations fail with incorrect sentinel values, or buffer checks fail after the device work completes. Graphics-only color failures leave the storage-buffer path passing, while failures across all selected buffers keep the shared setup, barriers, submission, and host invalidation path in scope.

**Possible implementation causes:** The implementation may mishandle storage-buffer descriptor contents, shader-write to host-read availability or visibility, command submission completion, or host-memory invalidation. The CTS records a stage-specific shader-write to host-read barrier and waits for queue completion before invalidating each allocation ([barrier and readback code](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L393-L402), [submission and checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L801-L826)). The observed pattern can narrow the investigation, but it cannot prove a unique fault location.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` requires `VK_KHR_push_descriptor` when either selected route is `push` or `template_push`.
- It also requires `VK_KHR_descriptor_update_template` when a selected route is `template_push` ([support checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L203)).
- Any pair containing ray tracing requires `VK_KHR_ray_tracing_pipeline` ([ray-tracing requirement](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L205-L206)).
- `checkPipelineConstructionRequirements()` enforces the requirements of the selected construction type ([construction check](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L208-L210)).

These checks remove cases that the current device or construction path cannot support. They do not indicate a passing result.

### Design-based pruning

The factory keeps `compute_raytracing` only for monolithic construction. For every other construction type it skips a pair when neither selected bind point is graphics ([pair pruning](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L972-L987)). This avoids repeating a pair outside the construction coverage chosen by the test design; it is separate from extension-based support checks.

## Key Takeaways

- The primary behavior is independence of pipeline or shader-object state and descriptor state between the two selected command classes.
- The nine ordered descriptor-route combinations, 24 setup orders, and two execution orders vary how state is established and consumed without changing the sentinel contract.
- Separate buffers make graphics, compute, and ray-tracing writes independently observable. Graphics adds a second observation through the green attachment.
- The result pattern can narrow whether a failure affects one bind-point path, graphics output, ray tracing, or shared descriptor and readback infrastructure. It does not identify a unique implementation fault without further investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support checks and generated programs | [`BindPointTest::checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L280) | Defines feature gates and shader fixtures. |
| Descriptor helpers and barriers | [`makeSetLayout`, update helpers, and `recordBufferBarrier`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L294-L402) | Defines storage-buffer descriptors, update routes, and readback synchronization. |
| Runtime implementation | [`BindPointInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L404-L851) | Creates resources, records commands, submits work, and checks results. |
| Registration matrix | [`createBindPointTests`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083) | Defines bind-point pairs, route combinations, permutations, and pruning. |
| Parent registration guard | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L174-L178) and [bind-point include](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L65-L69) | Places the family in the pipeline category and excludes it from Vulkan SC. |
| Graphics state binding | [`GraphicsPipelineWrapper::bind`](../../../framework/vulkan/vkPipelineConstructionUtil.cpp#L4721-L4761) | Shows that shader-object variants bind graphics shader objects and dynamic state instead of a graphics pipeline. |
| Bind-point and command relationship | [Vulkan shader binding](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800) | Defines the shader-stage to bind-point mapping used by the test. |
| Push-descriptor template contract | [Vulkan descriptor update template](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4174-L4209) | Defines bind point, layout, and set fields for push templates. |
