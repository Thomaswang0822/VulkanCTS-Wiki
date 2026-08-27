## Overview

**Core question:** Does using `VK_EXT_shader_object` add more CPU-visible command-recording, binding, or creation time than the selected reference path?

- [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L47-L77) implements the `shader_object.performance` test family. It measures graphics draws, compute dispatches, shader-object binary creation, and copying shader binary data.
- The graphics cases compare unlinked shader objects with static pipelines, dynamic pipelines, linked shader objects, or shader objects recreated from binary data. The dispatch cases compare shader-object dispatch with compute-pipeline dispatch. The binary cases compare binary shader creation with SPIR-V shader creation or a host memory copy.
- Each comparison uses elapsed CPU time around the relevant command or API call. The test uses relative thresholds, not an absolute timing target, and reports selected draw slowdowns as quality warnings.
- The page covers the registered `performance` branch, its six draw command forms, three dispatch forms, two binary operations, and the feature-dependent graphics setup used by the implementation.

## Background Knowledge

For the shared concepts shader objects, pipelines, and shader binaries, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- A graphics draw reaches the vertex stage first and may continue through tessellation, geometry, and fragment stages. The test uses this ordinary graphics-stage order, while its reference may use a pipeline or linked shader objects for the same draw command.
- Indirect draw and dispatch commands record references to parameter buffers that the device reads during execution. Direct forms receive counts as command arguments; the timers in this family still surround only the host-side command call, not the later device-side reads.

## Registration Hierarchy

```text
shader_object.performance
├── draw_static_pipeline
├── draw_dynamic_pipeline
├── draw_linked_shaders
├── draw_binary_shaders
├── draw_indexed_static_pipeline
├── draw_indexed_dynamic_pipeline
├── draw_indexed_linked_shaders
├── draw_indexed_binary_shaders
├── draw_indexed_indirect_static_pipeline
├── draw_indexed_indirect_dynamic_pipeline
├── draw_indexed_indirect_linked_shaders
├── draw_indexed_indirect_binary_shaders
├── draw_indexed_indirect_count_static_pipeline
├── draw_indexed_indirect_count_dynamic_pipeline
├── draw_indexed_indirect_count_linked_shaders
├── draw_indexed_indirect_count_binary_shaders
├── draw_indirect_static_pipeline
├── draw_indirect_dynamic_pipeline
├── draw_indirect_linked_shaders
├── draw_indirect_binary_shaders
├── draw_indirect_count_static_pipeline
├── draw_indirect_count_dynamic_pipeline
├── draw_indirect_count_linked_shaders
├── draw_indirect_count_binary_shaders
├── binary_bind_shaders
├── dispatch
├── dispatch_base
├── dispatch_indirect
├── binary_shader_create
└── binary_memcpy
```

The `performance` test family is attached directly below the `shader_object` test category by [createTests](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L60). The draw names are the cross product of six `DrawType` values and four comparison types, followed by `binary_bind_shaders`; the dispatch and binary names are added separately by [createShaderObjectPerformanceTests](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1262-L1308).

The source registers this family, but the mustpass configuration excludes every path matching `dEQP-VK.shader_object.performance.*` in [`excluded-tests.txt`](../../../mustpass/main/src/excluded-tests.txt). No performance mustpass file is present under the shader-object mustpass directory. The timing cases therefore document source registration and intentional exclusion rather than conformance-run coverage.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw command form | `draw`, `draw_indexed`, `draw_indexed_indirect`, `draw_indexed_indirect_count`, `draw_indirect`, `draw_indirect_count` | Selects the graphics command measured inside the rendering pass. Indexed forms use a 16-byte buffer initialized through four `uint32_t` writes but bind it as `VK_INDEX_TYPE_UINT16`. Indirect forms reference one command in an indirect buffer, and count forms also reference a count value. | [`DrawType` and `draw`](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L62-L70), [`ShaderObjectPerformanceInstance::draw`](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L300-L345) |
| Draw comparison mode | `static_pipeline`, `dynamic_pipeline`, `linked_shaders`, `binary_shaders`, `binary_bind_shaders` | Selects the reference implementation and the operation included in the timing comparison. The first four modes run a draw; `binary_bind_shaders` times only shader binding. | [`TestType` and registration](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L47-L54), [draw registration](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1279-L1299) |
| Dispatch mode | `dispatch`, `dispatch_base`, `dispatch_indirect` | Selects `vkCmdDispatch`, `vkCmdDispatchBase`, or `vkCmdDispatchIndirect` for both the shader-object and compute-pipeline paths. | [`DispatchType`](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L72-L77), [dispatch loop](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1017-L1067) |
| Binary operation | `binary_shader_create`, `binary_memcpy` | Selects whether binary shader creation is compared with SPIR-V shader creation or with copying the same binary size into host-visible memory. | [`BinaryType`](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L56-L60), [binary loop](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1145-L1208) |
| Graphics stage availability | vertex and fragment always; tessellation and geometry when their core features are enabled | Changes the shader-object list, linked reference list, pipeline topology, and `nextStage` chain. | [graphics stage assembly](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L407-L462) |
| Dynamic-state availability | core baseline states plus states exposed by extended-dynamic-state features and supported extensions | Changes which states the dynamic reference pipeline declares and which defaults the command buffer sets before the draw. | [`getDynamicStates`](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L108-L266), [dynamic pipeline setup](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L577-L639) |

## Behavior Parameters

The page has four behavioral axes. The draw command form and comparison mode jointly select each graphics case. Dispatch mode selects the compute command, and binary operation selects the non-rendering comparison. For graphics and compute, the timer surrounds only the selected `vkCmd*` call; shader or pipeline binding, submission, waiting, and device execution are outside the timed interval.

### Draw command form: direct draw

`draw` measures `vk.cmdDraw(cmdBuffer, 4, 1, 0, 0)`. The reference path records the same command after setting up its pipeline or reference shader objects, so the comparison measures the command-recording call under the two state configurations; the setup and binding calls themselves are not timed.

### Draw command form: indexed draw

`draw_indexed` binds an index buffer and measures `vk.cmdDrawIndexed(cmdBuffer, 4, 1, 0, 0, 0)`. The source allocates 16 bytes and writes four `uint32_t` values, then binds the buffer with `VK_INDEX_TYPE_UINT16`; both sides use the same buffer and command arguments.

### Draw command form: indirect draw

`draw_indirect` measures `vk.cmdDrawIndirect` with one `VkDrawIndirectCommand` at offset zero. The host initializes the command with `vertexCount = 4`, `instanceCount = 1`, `firstVertex = 0`, and `firstInstance = 0`.

### Draw command form: indirect count draw

`draw_indirect_count` measures `vk.cmdDrawIndirectCount` with the same indirect command and a count buffer containing `1`. The test keeps the indirect command and count buffer identical for the shader-object and reference runs.

### Draw command form: indexed indirect draw

`draw_indexed_indirect` measures `vk.cmdDrawIndexedIndirect` after binding the index buffer. The indirect command describes four indices and one instance.

### Draw command form: indexed indirect count draw

`draw_indexed_indirect_count` measures `vk.cmdDrawIndexedIndirectCount` after binding the index buffer. The indirect command describes four indices, and the count buffer permits one draw.

### Comparison mode: static pipeline

The shader-object path binds the separately created graphics shader objects and sets default dynamic states before the draw. The reference binds a graphics pipeline with the same basic shader stages and mostly static viewport and scissor state. The case fails when the maximum shader-object iteration exceeds the maximum static-pipeline iteration by more than 50 percent. It reports a quality warning when either the accumulated time or the maximum iteration is more than 25 percent slower.

### Comparison mode: dynamic pipeline

The shader-object path is the same as in the static comparison. The reference pipeline declares the available dynamic states and sets the same defaults before binding the pipeline. The case fails when the maximum shader-object iteration is more than 20 percent slower. It reports a quality warning when the accumulated time or maximum iteration is more than 10 percent slower.

### Comparison mode: linked shaders

The current path binds independently created, unlinked shader objects. The reference path creates the graphics stages together with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` and binds the resulting linked shader objects. The test applies a 5 percent limit to maximum samples in both directions and to accumulated linked time versus accumulated unlinked time. It does not apply the reverse accumulated-time check.

### Comparison mode: binary shaders

The current path binds shader objects created from the SPIR-V binaries in the test's binary collection. The reference path extracts binary data from those objects and recreates equivalent shader objects with `VK_SHADER_CODE_TYPE_BINARY_EXT`. The test applies a 5 percent limit to maximum samples in both directions and to accumulated binary-reference time versus accumulated current-path time, but not to accumulated current-path time in the reverse direction.

### Comparison mode: binary shader binding

`binary_bind_shaders` uses the direct draw form but measures only `vk::bindGraphicsShaders` for the original shader objects and the binary-recreated reference objects. It records each command buffer and ends it without submitting a render. Its 5 percent checks have the same asymmetry as `binary_shaders`: maxima are checked both ways, while accumulated time is checked only when the binary reference is slower.

### Dispatch mode: dispatch

`dispatch` measures `vk.cmdDispatch(cmdBuffer, 1, 1, 1)` first with the compute shader object and then with the compute pipeline. The case compares the accumulated times after discarding the first iteration.

### Dispatch mode: dispatch base

`dispatch_base` sets `VK_SHADER_CREATE_DISPATCH_BASE_BIT_EXT` on the compute shader create info. The source calls `vk.cmdDispatchBase(cmdBuffer, 1, 1, 1, 0, 0, 0)`, whose argument order gives base group `(1, 1, 1)` and group count `(0, 0, 0)`. The compute pipeline receives `VK_PIPELINE_CREATE_DISPATCH_BASE_BIT`, so both paths record the same zero-workgroup dispatch-base command.

### Dispatch mode: dispatch indirect

`dispatch_indirect` measures `vk.cmdDispatchIndirect` from a host-visible indirect buffer initialized to `x = 1`, `y = 1`, and `z = 1`. The compute shader-object and compute-pipeline paths read the same buffer.

### Binary operation: binary shader creation

`binary_shader_create` times `vk.createShadersEXT` for one shader created from the binary returned by `vk.getShaderBinaryDataEXT`. The reference time is the creation of the same vertex shader from SPIR-V. The case uses a 5 percent upper limit for binary creation time.

### Binary operation: binary memory copy

`binary_memcpy` uses the same timed binary shader creation as the other binary case, but its reference is `memcpy` of the binary data into a host-visible, local buffer followed by `flushAlloc`. The allocation and buffer setup happen before the timed copy interval. The case allows binary shader creation to take up to 50 percent more time than that copy reference.

## Shader Analysis

The performance family uses simple generated shaders for commands whose host recording calls are timed. The selected representative case uses the vertex stage from `addBasicShaderObjectShaders`. The stage converts `gl_VertexIndex` into one of four positions, and the host issues a four-vertex draw; shader execution occurs after the timed `vkCmdDraw` call, and the pass/fail rule does not inspect pixel output.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.shader_object.performance.draw_static_pipeline
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw` | The host calls `vkCmdDraw` with four vertices and one instance. |
| `static_pipeline` | The shader-object draw is compared with a graphics pipeline that contains the same basic stage set and static viewport/scissor state. |
| Vertex stage | The vertex shader supplies positions from `gl_VertexIndex`; it has no descriptors or host-created shader-visible resources. |

#### Purpose

The shader maps the low two bits of `gl_VertexIndex` to a four-corner position. The test uses it as the vertex work while comparing the time to record `vkCmdDraw` after shader-object setup versus static-pipeline setup.

#### Structural Design

| Phase | Shader operation | Result |
|------|------------------|--------|
| Index decode | Mask bit 0 and arithmetic-shift bit 1 from `gl_VertexIndex` | Two floating-point coordinates in the range 0 to 1 |
| Position transform | Subtract `(0.5, 0.5)` and append `z = 0`, `w = 1` | A clip-space vertex position |
| Stage output | Store the vector in `gl_Position` | The graphics pipeline receives the vertex position |

#### Shader Code

```glsl
#version 450

/// This vertex shader has no descriptor resources. The host supplies the vertex identity through gl_VertexIndex.
void main() {
    /// The two low index bits choose one of four positions for the four-vertex draw.
    vec2 pos = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1));
    /// Center the four positions around the origin and write a clip-space position.
    gl_Position = vec4(pos - 0.5f, 0.0f, 1.0f);
}
```

#### Additional Info

- The vertex source is shared by the graphics comparison modes. `static_pipeline` changes the reference state packaging, not the generated vertex source.
- The selected case uses the default SPIR-V target from the source collection. The SPIR-V artifact below was generated from this GLSL reconstruction with target `spirv1.0`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw command form | All six draw forms use the same vertex shader. The command form changes how the host supplies the four-vertex work, not the vertex source. | [draw implementation](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L300-L345) |
| Draw comparison mode | `static_pipeline`, `dynamic_pipeline`, `linked_shaders`, `binary_shaders`, and `binary_bind_shaders` use the same basic vertex shader; they change creation, binding, or pipeline state around it. | [graphics setup](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L407-L496) |
| Graphics stage availability | Tessellation and geometry stages may be added around this vertex stage when their device features are enabled. The vertex source remains unchanged. | [stage assembly](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L416-L446) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
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
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_1 = OpConstant %int 1
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
  %float_0_5 = OpConstant %float 0.5
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v2float Function
         %13 = OpLoad %int %gl_VertexIndex
         %15 = OpBitwiseAnd %int %13 %int_1
         %16 = OpConvertSToF %float %15
         %17 = OpLoad %int %gl_VertexIndex
         %18 = OpShiftRightArithmetic %int %17 %int_1
         %19 = OpBitwiseAnd %int %18 %int_1
         %20 = OpConvertSToF %float %19
         %21 = OpCompositeConstruct %v2float %16 %20
               OpStore %pos %21
         %30 = OpLoad %v2float %pos
         %32 = OpCompositeConstruct %v2float %float_0_5 %float_0_5
         %33 = OpFSub %v2float %30 %32
         %36 = OpCompositeExtract %float %33 0
         %37 = OpCompositeExtract %float %33 1
         %38 = OpCompositeConstruct %v4float %36 %37 %float_0 %float_1
         %40 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %40 %38
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Graphics resources.** Each draw case creates a 32 by 32 `VK_FORMAT_R8G8B8A8_UNORM` color image with color-attachment and transfer-source usage, a view, a host-visible output buffer, an index buffer, an indirect buffer, and a count buffer. The output buffer is not read back for a correctness comparison; it makes the rendering setup complete for the timed draw.
- **Graphics shader setup.** Vertex and fragment shader objects always exist. Tessellation control, tessellation evaluation, and geometry objects are created when the corresponding device features are enabled. The `nextStage` chain follows the available graphics stages. The helper also binds null task and mesh stages when those feature bits are reported.
- **Reference setup.** Static and dynamic cases create a graphics pipeline from the same basic shader modules. Linked cases create all available graphics shader stages in one linked batch. Binary cases query each original shader's binary and recreate the reference objects with `VK_SHADER_CODE_TYPE_BINARY_EXT`.
- **Draw command setup.** The host fills the indirect command and count buffers with one four-vertex or four-index draw, then runs one dummy draw through `dummyPipeline` before measuring. That dummy run performs the initial image layout transition and lets the implementation complete the first allocation work outside the measured loop.
- **Graphics measurement.** The implementation records and submits each shader-object and reference command buffer separately, but only the selected draw-command call is between the `high_resolution_clock::now()` calls. Binding, dynamic-state setup, submission, waiting, and device execution are outside the timed interval. The test accumulates command-call time and tracks the maximum single-iteration sample across 100 iterations.
- **Binding-only measurement.** `binary_bind_shaders` times `bindGraphicsShaders` for the original and binary-recreated shader objects without submitting the command buffers. This case does not include rendering time.
- **Compute setup.** Dispatch cases create a 16-element storage buffer, a descriptor set at binding 0, a compute pipeline layout, a compute shader object, a compute pipeline, and an indirect dispatch buffer. The compute shader writes each invocation ID into the storage buffer, but the test does not scan the buffer because the result under test is dispatch timing.
- **Compute measurement.** Each iteration records and submits a shader-object dispatch and a pipeline dispatch, but only the selected dispatch-command call is timed. The first iteration is discarded because the source identifies a first-call penalty. The remaining 99 command-call samples contribute to the two accumulated times.
- **Binary measurement.** Binary cases run 100 iterations. Each iteration creates a vertex shader from SPIR-V, queries its binary, creates a binary shader, and times that binary creation. `binary_shader_create` uses SPIR-V creation as the reference. `binary_memcpy` allocates a host-visible local buffer and times copying the same binary bytes followed by `flushAlloc`.
- **Pass and warning rules.** Draw cases use the mode-specific thresholds in `## Behavior Parameters`. Dispatch fails when shader-object dispatch exceeds compute-pipeline dispatch by more than 5 percent. Binary shader creation fails above 5 percent relative to SPIR-V creation, and binary memory-copy comparison fails above 50 percent.

## Failure Meaning

### Failure Cause Mapping

Draw command form axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | The direct draw path records or submits shader-object work outside the comparison's timing tolerance. |
| `draw_indexed` | The indexed draw path, including index-buffer binding, exceeds the comparison's timing tolerance. |
| `draw_indexed_indirect` | The indexed indirect path, including indirect-parameter access, exceeds the comparison's timing tolerance. |
| `draw_indexed_indirect_count` | The indexed indirect count path exceeds the comparison's timing tolerance. |
| `draw_indirect` | The indirect draw path exceeds the comparison's timing tolerance. |
| `draw_indirect_count` | The indirect count draw path exceeds the comparison's timing tolerance. |

Draw comparison mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static_pipeline` | Shader-object rendering is slower than the static-pipeline reference under the mode's 25 percent warning and 50 percent maximum-time failure rules. |
| `dynamic_pipeline` | Shader-object rendering is slower than the dynamic-pipeline reference under the mode's 10 percent warning and 20 percent maximum-time failure rules. |
| `linked_shaders` | Maximum unlinked and linked draw-command samples differ by more than 5 percent in either direction, or accumulated linked time is more than 5 percent slower than accumulated unlinked time. |
| `binary_shaders` | Maximum SPIR-V-created and binary-recreated draw-command samples differ by more than 5 percent in either direction, or accumulated binary-reference time is more than 5 percent slower than accumulated current-path time. |
| `binary_bind_shaders` | Maximum original and binary-recreated binding samples differ by more than 5 percent in either direction, or accumulated binary-reference binding time is more than 5 percent slower than accumulated original binding time. |

Dispatch mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dispatch` | Shader-object `vkCmdDispatch` is more than 5 percent slower than compute-pipeline `vkCmdDispatch`. |
| `dispatch_base` | Shader-object `vkCmdDispatchBase` is more than 5 percent slower than compute-pipeline `vkCmdDispatchBase`. |
| `dispatch_indirect` | Shader-object `vkCmdDispatchIndirect` is more than 5 percent slower than compute-pipeline `vkCmdDispatchIndirect`. |

Binary operation axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `binary_shader_create` | Creating a shader from an implementation-defined binary is more than 5 percent slower than creating the same shader from SPIR-V. |
| `binary_memcpy` | Creating a shader from an implementation-defined binary is more than 50 percent slower than copying the same number of bytes and flushing the host-visible allocation. |

### Cause Analysis

#### Graphics timing comparison

**Possible failure symptoms:** A draw case returns a failure or quality warning with a message naming shader-object rendering, the selected reference, and the relevant percentage threshold. The failing sample may be the accumulated total, the maximum iteration, or both, depending on the comparison mode.

**Possible implementation causes:** The measured interval contains only the selected draw-command call. A failure can therefore reflect the implementation's host-side processing of that command under the shader-object, pipeline, linked-shader, or binary-recreated state active in the command buffer. Binding, submission, waiting, and device execution are not timed, and the source does not isolate work performed inside the command call further.

#### Dispatch timing comparison

**Possible failure symptoms:** `dispatch`, `dispatch_base`, or `dispatch_indirect` returns a failure because accumulated shader-object dispatch time exceeds the compute-pipeline reference by more than 5 percent after the first iteration is discarded.

**Possible implementation causes:** The difference can arise in the host-side processing of the dispatch command under shader-object versus compute-pipeline state. Binding, submission, waiting, and device execution are outside the timing interval. The test does not separate work performed inside the command call, so implementation-level investigation is needed to identify the cause for a particular device.

#### Binary shader creation timing

**Possible failure symptoms:** `binary_shader_create` reports that binary shader-object creation is more than 5 percent slower than SPIR-V shader-object creation, or `binary_memcpy` reports that it is more than 50 percent slower than copying the same binary size.

**Possible implementation causes:** Binary decoding, validation, or internal shader-object construction may take longer than the SPIR-V creation path or the host copy path. The test measures the API call for binary creation, while the copy reference measures `memcpy` and `flushAlloc`; it does not identify which internal step accounts for a difference. Further implementation investigation is needed.

#### Reference-path asymmetry

**Possible failure symptoms:** A linked-shader or binary-shader draw case fails because the reference is more than 5 percent slower than the current shader-object path. The source reports both directions as failures even though the page's main question compares shader-object timing with a reference.

**Possible implementation causes:** The selected reference path may have a slower binding or draw path for the device, or the current path may be faster by more than the allowed tolerance. This result is a relative comparison, not proof that one implementation path is intrinsically defective. Investigate the two recorded paths and the affected draw form before assigning a fault.

## Case Pruning

### Requirement-based pruning

- Every draw, dispatch, and binary case requires `VK_EXT_shader_object` through its `checkSupport` method. The extension requirement appears in [the draw case](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L868-L897), [the dispatch case](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1082-L1114), and [the binary case](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1227-L1258).
- Tessellation shader objects and the patch-list topology are used only when `tessellationShader` is enabled. Geometry shader objects are used only when `geometryShader` is enabled. Without those features, the graphics stage list and `nextStage` chain are shorter, and the draw uses triangle-strip topology [graphics stage assembly](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L359-L446).
- Dynamic-state setup adds states only when the corresponding core feature or extension is available. The dynamic pipeline therefore has a device-dependent state list, while unsupported extension-specific states are omitted [getDynamicStates](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L108-L266).
- The dispatch cases use a storage buffer and an indirect buffer. The source does not add a separate case-specific feature check for the indirect form; device support is handled by the normal Vulkan command requirements and test framework.

### Design-based pruning

- The family does not compare every possible pipeline state or shader source. It uses the shared basic shader set and changes the operation being timed.
- The six draw command forms are paired with four draw comparison modes, while `binary_bind_shaders` covers only the direct draw form because it measures binding rather than rendering.
- The graphics image and output buffer provide valid render-target setup, but the test does not copy the image back or compare pixels. Timing is the behavior under test.
- The first compute iteration is discarded because the source documents a first-call penalty. Draw timing keeps all 100 measured iterations after a separate dummy run, and binary timing uses all 100 iterations.
- The binary memory-copy baseline times only the copy and allocation flush. Buffer creation and allocation are outside that interval, so the comparison is against the source's defined copy operation rather than total buffer setup.

## Key Takeaways

- The `performance` test family measures relative CPU-visible cost for shader-object creation, binding, draw, and dispatch paths. It does not establish an absolute performance requirement.
- Graphics coverage spans direct, indexed, indirect, and indirect-count commands. The comparison modes distinguish pipeline packaging, linked shader creation, binary recreation, and binding-only behavior.
- Draw thresholds intentionally differ by reference. Static-pipeline cases allow the largest maximum-time margin, dynamic-pipeline cases use tighter limits, and linked or binary shader-object comparisons use 5 percent limits with bidirectional maximum checks but only a reference-slower accumulated-time check.
- Dispatch cases discard the first iteration before comparing 99 accumulated samples. Binary cases use 100 iterations and compare binary creation either with SPIR-V creation or with a defined host copy operation.
- The family is source-registered but excluded from mustpass by `dEQP-VK.shader_object.performance.*`, so its timing checks are not part of the default conformance selection.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test enums and `ShaderObjectPerformanceInstance::draw` | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L47-L345) | Defines the draw and comparison dimensions and the six timed draw commands. |
| `ShaderObjectPerformanceInstance::iterate` graphics setup | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L348-L462) | Creates graphics shader objects, feature-dependent stages, and render targets. |
| Graphics reference setup | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L464-L647) | Builds linked, binary, static-pipeline, and dynamic-pipeline references. |
| Graphics timing loop and thresholds | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L697-L866) | Runs the warm-up and 100-iteration timing loop and applies pass, warning, and failure rules. |
| Shared basic shader generation | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211) | Supplies the vertex, tessellation, geometry, fragment, and compute shader sources. |
| Shader-object creation helper | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L213-L237) | Builds SPIR-V `VkShaderCreateInfoEXT` structures and their `nextStage` values. |
| Dynamic-state helper | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L108-L266) | Collects supported dynamic states for the dynamic pipeline comparison. |
| Graphics shader binding helper | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L420-L447) | Binds the five graphics stages and clears optional task and mesh stages. |
| Dispatch timing loop | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L944-L1080) | Measures direct, base, and indirect compute dispatches and discards the first iteration. |
| Binary timing loop | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1132-L1225) | Compares binary shader creation with SPIR-V creation or an equal-size memory copy. |
| Performance registration | [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1262-L1310) | Creates all 30 registered performance test cases. |
| Parent category registration | [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L60) | Attaches the performance test family to `shader_object`. |
| Performance exclusion | [`excluded-tests.txt`](../../../mustpass/main/src/excluded-tests.txt) | Excludes `dEQP-VK.shader_object.performance.*` from mustpass selection. |
| Shader object creation and binary semantics | [Shader Object Creation](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-objects-creation) | Defines the shader-object creation, binary-code, and result-handle semantics behind the tested API paths. |
