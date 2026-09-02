## Overview

**Core question:** Does conditional rendering control execution of a generated mesh draw while leaving explicit preprocessing unaffected?

- [`vktDGCGraphicsMeshConditionalTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L1) implements the `dgc.ext.graphics.mesh.conditional_rendering` test family.
- The test has two registered children, `general` and `preprocess`.
- `general` wraps `vkCmdExecuteGeneratedCommandsEXT` in conditional rendering. It covers classic pipeline binding and an indirect execution-set pipeline, optional sequence-count buffering, true and false predicates, inversion, and direct mesh or task-plus-mesh execution.
- `preprocess` wraps `vkCmdPreprocessGeneratedCommandsEXT` in conditional rendering, then executes the preprocessed commands under the same predicate. It checks both the preprocessing rule and the rendered result.
- The device writes a 2 by 4 `VK_FORMAT_R8G8B8A8_UNORM` target blue when the generated draw executes. A suppressed draw leaves the clear color in place.

## Background Knowledge

- Conditional rendering reads a 32-bit predicate from a buffer. A zero value suppresses affected rendering commands and a nonzero value permits them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision. See [conditional rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#L2090-L2167).
- A task shader can call `EmitMeshTasksEXT` to launch mesh workgroups and pass data through `taskPayloadSharedEXT`. Without a task shader, the draw launches mesh workgroups directly. A mesh shader calls `SetMeshOutputsEXT` and emits vertices and primitives for the graphics pipeline. See [mesh and task shader execution](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L8-L23).
- A DGC layout describes tokens and an action token. Here the action is a `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_MESH_TASKS_EXT` operation using `VkDrawMeshTasksIndirectCommandEXT`. Explicit preprocessing produces state consumed later by execution; conditional rendering has distinct rules for preprocessing and execution. See [DGC preprocessing](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L3394-L3483).

## Registration Hierarchy

```text
dgc.ext.graphics.mesh.conditional_rendering
├── general
└── preprocess
```

The complete test-name matrix appears in `## Parameter Dimensions and Observed Values`; the two direct children above are the only registered intermediate nodes for this page.

## Parameter Dimensions and Observed Values

The registration loops at [`createDGCGraphicsMeshConditionalTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L676-L727) create 32 `general` cases and 4 `preprocess` cases.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `general`, `preprocess` | Selects execution-only conditional rendering or the preprocessing-plus-execution check. | [registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L680-L722) |
| Pipeline selection | `classic_bind`, `pipeline_token` | Uses an ordinary bound graphics pipeline or an indirect execution-set pipeline token. | [general registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L684-L706) |
| Sequence-count source | `with_count_buffer`, `without_count_buffer` | Supplies a one-sequence count buffer or uses the fixed sequence count. | [sequence-count setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L427-L454) |
| Predicate value | `condition_false`, `condition_true` | Writes `0` or `1024` to the conditional-rendering buffer. Both are zero/nonzero predicate cases. | [predicate setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L401-L413) |
| Inversion | no suffix, `_inverted_flag` | Adds `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` and reverses the effective predicate. | [conditional begin](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L216-L230) |
| Mesh stages | no suffix, `_with_task_shader` | Uses direct mesh workgroups or a task shader followed by mesh workgroups. | [shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L166-L203) |

The `general` registration concatenates these exact components in this order: pipeline selection, sequence-count source, predicate value, optional `_inverted_flag`, and optional `_with_task_shader`. The resulting registered variants are:

- `general.classic_bind_with_count_buffer_condition_false`
- `general.classic_bind_with_count_buffer_condition_false_inverted_flag`
- `general.classic_bind_with_count_buffer_condition_false_inverted_flag_with_task_shader`
- `general.classic_bind_with_count_buffer_condition_false_with_task_shader`
- `general.classic_bind_with_count_buffer_condition_true`
- `general.classic_bind_with_count_buffer_condition_true_inverted_flag`
- `general.classic_bind_with_count_buffer_condition_true_inverted_flag_with_task_shader`
- `general.classic_bind_with_count_buffer_condition_true_with_task_shader`
- `general.classic_bind_without_count_buffer_condition_false`
- `general.classic_bind_without_count_buffer_condition_false_inverted_flag`
- `general.classic_bind_without_count_buffer_condition_false_inverted_flag_with_task_shader`
- `general.classic_bind_without_count_buffer_condition_false_with_task_shader`
- `general.classic_bind_without_count_buffer_condition_true`
- `general.classic_bind_without_count_buffer_condition_true_inverted_flag`
- `general.classic_bind_without_count_buffer_condition_true_inverted_flag_with_task_shader`
- `general.classic_bind_without_count_buffer_condition_true_with_task_shader`
- `general.pipeline_token_with_count_buffer_condition_false`
- `general.pipeline_token_with_count_buffer_condition_false_inverted_flag`
- `general.pipeline_token_with_count_buffer_condition_false_inverted_flag_with_task_shader`
- `general.pipeline_token_with_count_buffer_condition_false_with_task_shader`
- `general.pipeline_token_with_count_buffer_condition_true`
- `general.pipeline_token_with_count_buffer_condition_true_inverted_flag`
- `general.pipeline_token_with_count_buffer_condition_true_inverted_flag_with_task_shader`
- `general.pipeline_token_with_count_buffer_condition_true_with_task_shader`
- `general.pipeline_token_without_count_buffer_condition_false`
- `general.pipeline_token_without_count_buffer_condition_false_inverted_flag`
- `general.pipeline_token_without_count_buffer_condition_false_inverted_flag_with_task_shader`
- `general.pipeline_token_without_count_buffer_condition_false_with_task_shader`
- `general.pipeline_token_without_count_buffer_condition_true`
- `general.pipeline_token_without_count_buffer_condition_true_inverted_flag`
- `general.pipeline_token_without_count_buffer_condition_true_inverted_flag_with_task_shader`
- `general.pipeline_token_without_count_buffer_condition_true_with_task_shader`

The `preprocess` registration fixes the pipeline, count-buffer, and task-shader choices to the ordinary mesh path and registers exactly:

- `preprocess.condition_false`
- `preprocess.condition_false_inverted_flag`
- `preprocess.condition_true`
- `preprocess.condition_true_inverted_flag`

All cases require `VK_EXT_mesh_shader` and `VK_EXT_conditional_rendering`; DGC support is checked for the selected mesh and task stages. These are support gates, not expected failure outcomes. See [support checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L94-L117).

## Behavior Parameters

The primary behavioral axis is the registered test family. The other dimensions change command representation or shader stages without changing the conditional-rendering rule.

### `general` | Conditional execution of a generated mesh draw

The host builds a DGC layout containing an optional execution-set token, a push-constant token, and a mesh-draw token. The generated stream contains the blue push-constant value `(0, 0, 1, 1)` and `VkDrawMeshTasksIndirectCommandEXT{1, kHeight, 1}`. The host begins conditional rendering, binds the selected pipeline and descriptor set, and calls `vkCmdExecuteGeneratedCommandsEXT`.

The effective predicate is true when `conditionValue != inverted`. A true effective predicate lets the generated mesh draw run and produces a blue 2 by 4 image. A false effective predicate suppresses the draw, so the image remains the clear value `(0, 0, 0, 1)`. `pipeline_token` changes how the pipeline is selected in the DGC stream. `with_count_buffer` advertises 256 possible sequences while a count buffer limits execution to one. Neither changes the expected image.

### `preprocess` | Conditional preprocessing and later execution

The host creates an explicit-preprocess DGC layout with a push-constant token followed by a mesh-draw token. In one command buffer it binds the normal pipeline and descriptor set, begins conditional rendering, calls `vkCmdPreprocessGeneratedCommandsEXT`, ends the conditional block, inserts `preprocessToExecuteBarrierExt`, and submits. A second command buffer executes the preprocessed sequence with `isPreprocessed = VK_TRUE` inside a conditional rendering block.

The predicate must not suppress preprocessing. The later execute command still follows the effective predicate, so the final image is blue when `conditionValue != inverted` and clear otherwise. The barrier makes the preprocessed state available before the second submission uses it.

## Shader Analysis

The generated fragment shader copies the push-constant `vec4 color` to `outColor`. The generated mesh shader reads one clip-space position per output point from the storage buffer, calls `SetMeshOutputsEXT`, writes `gl_MeshVerticesEXT`, and assigns `gl_PrimitivePointIndicesEXT`. The 2 by 4 vertex positions place one point at each pixel center, so a permitted draw changes every pixel to blue and a suppressed draw changes none of them.

With no task shader, `local_size_x` is `kWidth` and each mesh workgroup emits one row of two points. With a task shader, the task stage uses `local_size_x=1`, stores a row base in `taskPayloadSharedEXT`, and calls `EmitMeshTasksEXT(1, 1, kWidth)`. Each resulting mesh workgroup emits one point. Both paths cover the same 2 by 4 target and expose the same conditional-rendering decision.

The shader source and build options are generated by [`onePointPerPixelPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L119-L214). This page does not add a separate shader walkthrough because the generated shaders have one fixed data flow; the task-shader difference is captured above and in the parameter matrix.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.mesh.conditional_rendering.general.classic_bind_without_count_buffer_condition_true
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `general` | Tests conditional rendering around generated-command execution. |
| `classic_bind` | Uses the ordinary graphics pipeline binding path. |
| `without_count_buffer` | Uses the fixed one-sequence count rather than an indirect count buffer. |
| `condition_true` | Writes `1024` to the predicate buffer and leaves inversion disabled. |
| no `_with_task_shader` | The generated mesh shader launches directly without a task stage. |

#### Purpose

The mesh stage maps each local invocation to one of two points in a row. The fragment stage copies the blue push constant to the color attachment. If conditional rendering permits the generated draw, the eight points cover the 2 by 4 target. If it suppresses the draw, the clear color remains.

#### Structural Design

| Step | Shader or generated-command action | Observable result |
|---|---|---|
| 1 | The generated stream supplies the blue push constant and `VkDrawMeshTasksIndirectCommandEXT{1, 4, 1}`. | One mesh workgroup runs for each of four rows. |
| 2 | `getWorkGroupIndex` flattens the mesh workgroup ID. | Each workgroup selects its row in the vertex storage buffer. |
| 3 | Each of two local invocations reads one clip-space position and writes one point primitive. | The mesh stage supplies one point for each pixel in the row. |
| 4 | The fragment shader writes `pc.color`. | A permitted draw produces an all-blue image. |

#### Shader Code


The generated mesh stage is the primary shader for this walkthrough. It maps each local invocation to one point in a row; the common fragment stage copies the blue push constant to the color attachment, as described in the page-level shader analysis. This walkthrough keeps only the mesh stage because it owns the per-pixel data path being reconstructed; the fragment stage is fixed across the page's cases.

```glsl
#version 460
#extension GL_EXT_mesh_shader : enable
/// Two local invocations process one row of the 2 by 4 target.
layout(local_size_x=2) in;
/// The mesh emits point primitives, with one output vertex per pixel in the row.
layout(points) out;
layout(max_vertices=2, max_primitives=2) out;
/// Set 0, binding 0 is a host-filled std430 storage buffer containing one clip-space
/// vec4 per target pixel. The mesh shader reads the position selected by vertIndex.
layout(set=0, binding=0, std430) readonly buffer VertexDataBlock {
    vec4 positions[];
} vertices;
/// Flatten the three-dimensional mesh workgroup ID so consecutive workgroups select
/// consecutive rows in the position buffer.
uint getWorkGroupIndex (void) {
    const uint workGroupIndex = gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z +
                                gl_NumWorkGroups.x * gl_WorkGroupID.y +
                                gl_WorkGroupID.x;
    return workGroupIndex;
}
void main() {
    /// Declare two mesh outputs, then map each invocation to one position and point.
    SetMeshOutputsEXT(2, 2);
    const uint vertIndex = getWorkGroupIndex() * 2u + gl_LocalInvocationIndex;
    gl_MeshVerticesEXT[gl_LocalInvocationIndex].gl_Position = vertices.positions[vertIndex];
    gl_MeshVerticesEXT[gl_LocalInvocationIndex].gl_PointSize = 1.0;
    gl_PrimitivePointIndicesEXT[gl_LocalInvocationIndex] = gl_LocalInvocationIndex;
}
```

#### Additional Info

- The task variant adds a task stage with `EmitMeshTasksEXT(1, 1, 2)`, stores a row base in `taskPayloadSharedEXT`, and changes the mesh workgroup size to one invocation. It must produce the same image.
- `pipeline_token` adds an execution-set token to the DGC stream. `with_count_buffer` advertises 256 potential sequences while a one-element count buffer limits execution to one sequence.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Task shader | Adds task payload data, a task stage, and one-invocation mesh workgroups. | [task and mesh generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L147-L203) |
| Pipeline selection | `pipeline_token` adds an execution-set token and uses an indirect-bindable pipeline. | [DGC pipeline token](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L344-L379) |
| Predicate and inversion | Changes whether the graphics command executes, not the shader data flow. | [conditional execution](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L401-L468) |

#### SPIR-V


- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 79
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %gl_NumWorkGroups %gl_WorkGroupID %gl_LocalInvocationIndex %gl_MeshVerticesEXT %vertices %gl_PrimitivePointIndicesEXT
               OpExecutionMode %main LocalSize 2 1 1
               OpExecutionMode %main OutputVertices 2
               OpExecutionMode %main OutputPrimitivesEXT 2
               OpExecutionMode %main OutputPoints
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %getWorkGroupIndex_ "getWorkGroupIndex("
               OpName %workGroupIndex "workGroupIndex"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %vertIndex "vertIndex"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %VertexDataBlock "VertexDataBlock"
               OpMemberName %VertexDataBlock 0 "positions"
               OpName %vertices "vertices"
               OpName %gl_PrimitivePointIndicesEXT "gl_PrimitivePointIndicesEXT"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %_runtimearr_v4float ArrayStride 16
               OpDecorate %VertexDataBlock Block
               OpMemberDecorate %VertexDataBlock 0 NonWritable
               OpMemberDecorate %VertexDataBlock 0 Offset 0
               OpDecorate %vertices NonWritable
               OpDecorate %vertices Binding 0
               OpDecorate %vertices DescriptorSet 0
               OpDecorate %gl_PrimitivePointIndicesEXT BuiltIn PrimitivePointIndicesEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
          %7 = OpTypeFunction %uint
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_2 = OpTypeArray %gl_MeshPerVertexEXT %uint_2
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_2 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_2
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_2 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_runtimearr_v4float = OpTypeRuntimeArray %v4float
%VertexDataBlock = OpTypeStruct %_runtimearr_v4float
%_ptr_StorageBuffer_VertexDataBlock = OpTypePointer StorageBuffer %VertexDataBlock
   %vertices = OpVariable %_ptr_StorageBuffer_VertexDataBlock StorageBuffer
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
%_arr_uint_uint_2 = OpTypeArray %uint %uint_2
%_ptr_Output__arr_uint_uint_2 = OpTypePointer Output %_arr_uint_uint_2
%gl_PrimitivePointIndicesEXT = OpVariable %_ptr_Output__arr_uint_uint_2 Output
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_2 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %vertIndex = OpVariable %_ptr_Function_uint Function
               OpSetMeshOutputsEXT %uint_2 %uint_2
         %41 = OpFunctionCall %uint %getWorkGroupIndex_
         %42 = OpIMul %uint %41 %uint_2
         %44 = OpLoad %uint %gl_LocalInvocationIndex
         %45 = OpIAdd %uint %42 %44
               OpStore %vertIndex %45
         %53 = OpLoad %uint %gl_LocalInvocationIndex
         %60 = OpLoad %uint %vertIndex
         %62 = OpAccessChain %_ptr_StorageBuffer_v4float %vertices %int_0 %60
         %63 = OpLoad %v4float %62
         %65 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %53 %int_0
               OpStore %65 %63
         %66 = OpLoad %uint %gl_LocalInvocationIndex
         %70 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %66 %int_1
               OpStore %70 %float_1
         %74 = OpLoad %uint %gl_LocalInvocationIndex
         %75 = OpLoad %uint %gl_LocalInvocationIndex
         %77 = OpAccessChain %_ptr_Output_uint %gl_PrimitivePointIndicesEXT %74
               OpStore %77 %75
               OpReturn
               OpFunctionEnd
%getWorkGroupIndex_ = OpFunction %uint None %7
          %9 = OpLabel
%workGroupIndex = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %21 = OpLoad %uint %20
         %22 = OpIMul %uint %18 %21
         %25 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %26 = OpLoad %uint %25
         %27 = OpIMul %uint %22 %26
         %28 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %29 = OpLoad %uint %28
         %30 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %31 = OpLoad %uint %30
         %32 = OpIMul %uint %29 %31
         %33 = OpIAdd %uint %27 %32
         %34 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %35 = OpLoad %uint %34
         %36 = OpIAdd %uint %33 %35
               OpStore %workGroupIndex %36
         %37 = OpLoad %uint %workGroupIndex
               OpReturnValue %37
               OpFunctionEnd
```
</details>

## Runtime Execution and Result Checking

- The host creates a 2 by 4 color image and framebuffer, a host-visible copy buffer, and a host-visible storage buffer containing one clip-space position per pixel.
- The descriptor set binds that position buffer at set `0`, binding `0`, for the mesh stage. The push-constant range is visible to the fragment stage and carries blue `(0, 0, 1, 1)` through the generated command stream.
- The condition buffer has `VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT` and contains `1024` for `condition_true` or `0` for `condition_false`.
- `general` records render-pass setup, conditional rendering, the selected pipeline state, descriptor binding, and `vkCmdExecuteGeneratedCommandsEXT` in one primary command buffer. It then copies the image to the host-visible buffer.
- `preprocess` records preprocessing and its barrier in one command buffer, waits for that submission, then records preprocessed execution and the image copy in a second command buffer.
- The host constructs an all-blue reference when `conditionValue != inverted` and an all-clear reference otherwise. It invalidates the copy-buffer allocation and compares every pixel with `tcu::floatThresholdCompare` using a zero threshold. A mismatch raises `TCU_FAIL`; an exact comparison returns `Pass`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `general` | Conditional rendering did not suppress or permit generated mesh execution according to `conditionValue` and `inverted`; DGC token execution, pipeline binding, mesh or task shader generation, descriptor access, or image checking may also be wrong. |
| `preprocess` | Conditional rendering incorrectly changed explicit preprocessing, the preprocessing and execution predicates did not match, the required synchronization was ineffective, or generated mesh execution or result checking failed after preprocessing. |

### Cause Analysis

#### Conditional predicate handling

**Possible failure symptoms:** A `general` case renders blue when its effective predicate is false, or leaves the clear image when the effective predicate is true. A `preprocess` case can show the same final-image mismatch, or can fail because later execution cannot use the preprocessed sequence.

**Possible implementation causes:** The implementation may apply the zero/nonzero rule incorrectly, ignore `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`, or apply conditional rendering to a command that the specification says preprocessing must execute regardless of the predicate. Source-level investigation is needed to distinguish predicate evaluation from command execution errors.

#### DGC state or mesh/task execution

**Possible failure symptoms:** A permitted `general` draw does not turn all eight pixels blue, or it produces an unexpected image even though the predicate decision is correct. The same symptom can occur after `preprocess` succeeds but execution consumes incorrect generated state.

**Possible implementation causes:** The DGC implementation may decode the execution-set, push-constant, or mesh-draw token incorrectly; bind the wrong pipeline or descriptor state; calculate mesh or task workgroup indices incorrectly; mishandle task payload data; or fail to read the position storage buffer. The source and specification define the expected state flow, but a particular failure location requires investigation of the implementation and validation log.

#### Preprocess-to-execute handoff

**Possible failure symptoms:** A `preprocess` case fails even though direct execution with the same predicate passes. The final image can be clear or partially incorrect, and the command may consume stale or incomplete preprocessed state.

**Possible implementation causes:** The preprocessing command may be incorrectly skipped or may produce unusable state under conditional rendering, or the required barrier may not make that state available to the second submission. Source-level investigation is needed to separate conditional-rendering behavior from synchronization or DGC state handling.

#### Host result comparison

**Possible failure symptoms:** The copied image differs from the all-blue or all-clear reference, causing `tcu::floatThresholdCompare` to fail.

**Possible implementation causes:** The rendering path may have written incorrect pixels, the image-to-buffer copy or memory visibility may be incorrect, or the host may have observed stale allocation contents. The exact cause depends on which pixels differ and the validation log; the test does not identify a single implementation layer in advance.

## Case Pruning

### Requirement-based pruning

- The test requires `VK_EXT_mesh_shader` and `VK_EXT_conditional_rendering`.
- `general` also requires the DGC support reported for mesh and fragment stages, plus task-stage support when `_with_task_shader` is selected.
- `pipeline_token` uses the DGC support query for indirect pipeline binding. Unsupported feature combinations are skipped by the support checks rather than reported as rendering failures.

### Design-based pruning

- `preprocess` fixes pipeline selection to ordinary binding, omits an indirect count buffer, and uses the direct mesh path without a task shader. It varies only the predicate value and inversion because those are the dimensions needed to test preprocessing independence and execution-time conditional behavior.
- The condition buffer uses `1024` instead of `1` for the true case. Conditional rendering only needs zero versus nonzero, so the larger nonzero value does not add another behavioral case.
- Each generated command stream contains one actual sequence. The count-buffer general cases advertise 256 potential sequences to preprocessing but use a count buffer containing `1` to limit execution to one sequence.

## Key Takeaways

- `general` tests whether conditional rendering suppresses or permits `vkCmdExecuteGeneratedCommandsEXT` for a generated mesh draw.
- `preprocess` separates the two operations: preprocessing must complete under either predicate, while later execution follows the effective predicate.
- Task-plus-mesh and direct-mesh cases use different workgroup paths but must produce the same blue-versus-clear result.
- `pipeline_token` and the optional count buffer change DGC state and sequence handling, not the expected predicate result.
- The final pass condition is an exact comparison of the copied 2 by 4 image with the reference selected by `conditionValue != inverted`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Support gates and parameter structs | [`TestParams`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L60-L117) | Defines task, pipeline-token, count-buffer, predicate, inversion, and preprocess parameters. |
| Generated task, mesh, and fragment programs | [`onePointPerPixelPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L119-L214) | Defines the blue fragment output, point-per-pixel mesh output, and task payload path. |
| Conditional rendering helper | [`beginConditionalRendering`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L216-L230) | Sets the predicate buffer and optional inversion flag. |
| General execution | [`conditionalDispatchRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L281-L496) | Builds resources and DGC state, executes the draw, and compares the image. |
| Preprocess execution | [`conditionalPreprocessRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L499-L672) | Runs preprocessing and later execution with the required barrier and result check. |
| Registration | [`createDGCGraphicsMeshConditionalTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L676-L727) | Registers the exact `general` and `preprocess` variant names. |
| Conditional rendering semantics | [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2090-L2167) | Defines predicate and inversion behavior. |
| Mesh and task shader semantics | [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L8-L23) | Defines task-to-mesh workgroup creation and emitted primitives. |
| DGC preprocessing semantics | [generatedcommands.adoc](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L3394-L3483) | Defines explicit preprocessing and conditional-rendering interaction. |
