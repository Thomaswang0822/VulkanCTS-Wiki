## Overview

**Core question:** Do conditional rendering predicates correctly enable or suppress transform-feedback draw commands?

- This page covers `vktConditionalTransformFeedbackTests.cpp`, which implements the `conditional_rendering.transform_feedback` test family.
- The family registers nine direct children for direct, indexed, indirect, multi-draw, indirect-byte-count, and indirect-count commands.
- Each case produces two occlusion-query predicates, uses them to control transform-feedback sections, and checks the captured buffer on the host.
- The page explains the command matrix, the four-stream geometry shader, command recording order, result checking, and the feature gates for each child.

## Background Knowledge

- Conditional rendering reads a 32-bit predicate from a buffer. A zero value discards affected rendering commands; a nonzero value executes them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that interpretation. See [Conditional Rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#drawing-conditional-rendering).
- Transform feedback writes selected shader outputs to bound buffers while it is active. This test uses geometry streams so that each stream writes to a separate six-float range. The transform-feedback stage writes require synchronization before the host reads the buffer. See [transform-feedback synchronization](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-stages).

## Registration Hierarchy

```text
conditional_rendering.transform_feedback
├── draw
├── draw_indexed
├── draw_indexed_indirect
├── draw_indexed_indirect_count
├── draw_indirect
├── draw_indirect_byte_count_ext
├── draw_indirect_count
├── draw_multi_ext
└── draw_multi_indexed_ext
```

The nine children are the values returned by `getDrawCommandTypeName()`. The deeper generated test cases are fixed at the child level for this implementation, so the tree stops at the direct children.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw command | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_multi_ext`, `draw_multi_indexed_ext`, `draw_indirect_byte_count_ext`, `draw_indirect_count`, `draw_indexed_indirect_count` | Selects the Vulkan command used inside each conditional transform-feedback section. | [`DrawCommandType` and `getDrawCommandTypeName()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L49-L90) |
| Shader variant | `VertexFetch.geom`, `VertexFetchWritePoint.geom` | Selects the geometry shader. The second variant adds `gl_PointSize` when the device supports geometry point size. | [`AddProgramsDraw::init()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L657-L700) |
| Stream index | `0`, `1`, `2`, `3` | Pushes the selected geometry stream and selects its six-float transform-feedback range. | [`iterate()` stream loop](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L578-L594) |
| Predicate source | Query result 0 or query result 1 | Alternates between a predicate expected to suppress work and one expected to allow work. | [`iterate()` query and conditional setup](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L550-L590) |

## Behavior Parameters

The primary behavioral axis is the `transform_feedback` test family child: the draw command variant. All values use the same shader and predicate sequence; they change how the draw is sourced and executed.

### `draw`: direct non-indexed draw

`vkCmdDraw` supplies six vertices directly from the vertex buffer. This is the simplest path and the representative case for the shared transform-feedback and conditional-rendering logic.

### `draw_indexed`: direct indexed draw

`vkCmdDrawIndexed` reads six indices from a host-visible index buffer. The index buffer is bound before the query-producing and transform-feedback draws.

### `draw_indirect`: indirect non-indexed draw

`vkCmdDrawIndirect` reads one command from a host-visible indirect buffer. The command at the selected offset describes six vertices and one instance.

### `draw_indexed_indirect`: indexed indirect draw

`vkCmdDrawIndexedIndirect` combines the index buffer with an indirect command buffer. The selected command describes six indexed vertices.

### `draw_multi_ext`: multi-draw non-indexed command

`vkCmdDrawMultiEXT` receives one `VkMultiDrawInfoEXT` record for the selected six-vertex range. This value requires `VK_EXT_multi_draw`.

### `draw_multi_indexed_ext`: multi-draw indexed command

`vkCmdDrawMultiIndexedEXT` receives one `VkMultiDrawIndexedInfoEXT` record and the bound index buffer. This value requires `VK_EXT_multi_draw`.

### `draw_indirect_byte_count_ext`: transform-feedback byte-count draw

`vkCmdDrawIndirectByteCountEXT` obtains its vertex count from a count buffer. The implementation sets the count entries to `24` and `0`, and this value requires the `transformFeedbackDraw` property.

### `draw_indirect_count`: indirect draw with a count buffer

`vkCmdDrawIndirectCount` reads the draw command and a count of available commands. The count buffer contains `1`, so one indirect command is eligible when the predicate allows execution. This value requires `VK_KHR_draw_indirect_count`.

### `draw_indexed_indirect_count`: indexed indirect draw with a count buffer

`vkCmdDrawIndexedIndirectCount` combines the indexed indirect command with the count buffer. This value requires `VK_KHR_draw_indirect_count` and the index buffer setup used by the indexed variants.

## Shader Analysis

The geometry shader is the central shader for this page because it chooses a transform-feedback stream and emits the captured value. The vertex and fragment shaders provide the input and render-pass plumbing; they do not vary across command children. The representative case is the direct `draw` child.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.conditional_rendering.transform_feedback.draw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw` | Uses `vkCmdDraw` without index or indirect buffers, isolating the shared conditional and transform-feedback behavior. |
| `stream = 0..3` | The host repeats the draw for four streams and pushes the stream index before each conditional section. |
| `VertexFetch.geom` | Uses the geometry shader variant without the optional `gl_PointSize` assignment. |

#### Purpose

The shader emits one point on exactly the stream selected by the push constant. Its stream-specific output value makes each transform-feedback range identify which conditional section executed.

#### Structural Design

| Shader phase | Operation | Observable result |
|--------------|-----------|-------------------|
| Input | Accept one point and prepare one output point. | The geometry stage can emit one point. |
| Selection | Compare `pushConst.stream` with `0`, `1`, `2`, and `3`. | Only one stream branch writes an output. |
| Capture | Assign `1.0`, `2.0`, `3.0`, or `4.0`, then call `EmitStreamVertex` and `EndStreamPrimitive`. | The selected transform-feedback range receives the stream value. |

#### Shader Code

```glsl
#version 450

layout (points) in;
layout(points, max_vertices = 1) out;

/// Each output maps one geometry stream to one transform-feedback buffer.
layout(location = 0, stream = 0, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 0) out float output1;
layout(location = 1, stream = 1, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 1) out float output2;
layout(location = 2, stream = 2, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 2) out float output3;
layout(location = 3, stream = 3, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 3) out float output4;

/// The host changes this value before each stream draw.
layout(push_constant) uniform PushConst {
    int stream;
} pushConst;

void main() {
    if (pushConst.stream == 0) {
        output1 = 1.0;
        EmitStreamVertex(0);
        EndStreamPrimitive(0);
    }
    if (pushConst.stream == 1) {
        output2 = 2.0;
        EmitStreamVertex(1);
        EndStreamPrimitive(1);
    }
    if (pushConst.stream == 2) {
        output3 = 3.0;
        EmitStreamVertex(2);
        EndStreamPrimitive(2);
    }
    if (pushConst.stream == 3) {
        output4 = 4.0;
        EmitStreamVertex(3);
        EndStreamPrimitive(3);
    }
}
```

#### Additional Info

- The source generator chooses `VertexFetchWritePoint.geom` instead when `shaderTessellationAndGeometryPointSize` is supported; that variant adds `gl_PointSize = 1.0f` without changing the captured stream values.
- The vertex shader reads position and color attributes and forwards them to the geometry and fragment stages. The fragment shader writes the forwarded color, but the page's correctness check uses the transform-feedback buffer and query results.
- The four output declarations require four transform-feedback buffer bindings and four transform-feedback streams. This implementation binds four six-float ranges of the single transform-feedback buffer, one range at each binding index; `checkSupport()` rejects devices whose corresponding limits are below four.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw command | The shader text remains the same. The host changes the draw command used to invoke it. | [`recordDraw()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L386-L455) |
| Geometry point-size support | The selected geometry source adds `gl_PointSize = 1.0f` when the device exposes geometry point size. | [`AddProgramsDraw::init()` point-size branch](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L657-L700) |
| Stream index | The shader branches on the push constant and emits only the matching stream output. | [`AddProgramsDraw::init()` geometry source](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L659-L697) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 46
; Schema: 0
               OpCapability Geometry
               OpCapability TransformFeedback
               OpCapability GeometryStreams
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %output1 %output2 %output3 %output4
               OpExecutionMode %main Xfb
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputPoints
               OpExecutionMode %main OutputVertices 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %PushConst "PushConst"
               OpMemberName %PushConst 0 "stream"
               OpName %pushConst "pushConst"
               OpName %output1 "output1"
               OpName %output2 "output2"
               OpName %output3 "output3"
               OpName %output4 "output4"
               OpDecorate %PushConst Block
               OpMemberDecorate %PushConst 0 Offset 0
               OpDecorate %output1 Stream 0
               OpDecorate %output1 Location 0
               OpDecorate %output1 Offset 0
               OpDecorate %output1 XfbBuffer 0
               OpDecorate %output1 XfbStride 4
               OpDecorate %output2 Stream 1
               OpDecorate %output2 Location 1
               OpDecorate %output2 Offset 0
               OpDecorate %output2 XfbBuffer 1
               OpDecorate %output2 XfbStride 4
               OpDecorate %output3 Stream 2
               OpDecorate %output3 Location 2
               OpDecorate %output3 Offset 0
               OpDecorate %output3 XfbBuffer 2
               OpDecorate %output3 XfbStride 4
               OpDecorate %output4 Stream 3
               OpDecorate %output4 Location 3
               OpDecorate %output4 Offset 0
               OpDecorate %output4 XfbBuffer 3
               OpDecorate %output4 XfbStride 4
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
  %PushConst = OpTypeStruct %int
%_ptr_PushConstant_PushConst = OpTypePointer PushConstant %PushConst
  %pushConst = OpVariable %_ptr_PushConstant_PushConst PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
       %bool = OpTypeBool
      %float = OpTypeFloat 32
%_ptr_Output_float = OpTypePointer Output %float
    %output1 = OpVariable %_ptr_Output_float Output
    %float_1 = OpConstant %float 1
      %int_1 = OpConstant %int 1
    %output2 = OpVariable %_ptr_Output_float Output
    %float_2 = OpConstant %float 2
      %int_2 = OpConstant %int 2
    %output3 = OpVariable %_ptr_Output_float Output
    %float_3 = OpConstant %float 3
      %int_3 = OpConstant %int 3
    %output4 = OpVariable %_ptr_Output_float Output
    %float_4 = OpConstant %float 4
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpAccessChain %_ptr_PushConstant_int %pushConst %int_0
         %13 = OpLoad %int %12
         %15 = OpIEqual %bool %13 %int_0
               OpSelectionMerge %17 None
               OpBranchConditional %15 %16 %17
         %16 = OpLabel
               OpStore %output1 %float_1
               OpEmitStreamVertex %int_0
               OpEndStreamPrimitive %int_0
               OpBranch %17
         %17 = OpLabel
         %22 = OpAccessChain %_ptr_PushConstant_int %pushConst %int_0
         %23 = OpLoad %int %22
         %25 = OpIEqual %bool %23 %int_1
               OpSelectionMerge %27 None
               OpBranchConditional %25 %26 %27
         %26 = OpLabel
               OpStore %output2 %float_2
               OpEmitStreamVertex %int_1
               OpEndStreamPrimitive %int_1
               OpBranch %27
         %27 = OpLabel
         %30 = OpAccessChain %_ptr_PushConstant_int %pushConst %int_0
         %31 = OpLoad %int %30
         %33 = OpIEqual %bool %31 %int_2
               OpSelectionMerge %35 None
               OpBranchConditional %33 %34 %35
         %34 = OpLabel
               OpStore %output3 %float_3
               OpEmitStreamVertex %int_2
               OpEndStreamPrimitive %int_2
               OpBranch %35
         %35 = OpLabel
         %38 = OpAccessChain %_ptr_PushConstant_int %pushConst %int_0
         %39 = OpLoad %int %38
         %41 = OpIEqual %bool %39 %int_3
               OpSelectionMerge %43 None
               OpBranchConditional %41 %42 %43
         %42 = OpLabel
               OpStore %output4 %float_4
               OpEmitStreamVertex %int_3
               OpEndStreamPrimitive %int_3
               OpBranch %43
         %43 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` requires `VK_EXT_conditional_rendering`, `VK_EXT_transform_feedback`, the `conditionalRendering` feature, and the `geometryStreams` feature. It also requires `maxTransformFeedbackBuffers >= 4` and `maxTransformFeedbackStreams >= 4`.
- The indirect-count children require `VK_KHR_draw_indirect_count`. The multi-draw children require `VK_EXT_multi_draw`. `draw_indirect_byte_count_ext` requires the `transformFeedbackDraw` property.
- The test creates an occlusion query pool with two queries and a host-visible query buffer with two 32-bit entries. It creates a host-visible transform-feedback buffer containing 24 floats, initialized to `0.0f`.
- The first command sequence binds the ordinary draw pipeline, prepares any index, indirect, or count buffers required by the selected child, and records `recordDraw(..., 2)` inside query 0 and `recordDraw(..., 1)` inside query 1.
- The test copies both query results into the query buffer, then inserts a transfer-to-conditional-rendering barrier. A second render section binds the stream pipeline and repeats four times:
  - bind the six-float range for the current stream;
  - push the stream index to the geometry shader;
  - select query buffer offset `0` for even streams and offset `4` for odd streams;
  - begin conditional rendering, begin transform feedback, issue the selected draw command, then end transform feedback and conditional rendering.
- A transform-feedback-write-to-host-read barrier precedes command completion. After the queue submission finishes, the host invalidates the transform-feedback allocation and logs whether query 0 is zero and query 1 is nonzero. It then checks all 24 floats; a transform-feedback mismatch returns failure, while a query mismatch is logged but is not returned directly as a failure by this source. The expected transform-feedback values are `0.0` for indices `0..5` and `12..17`, `2.0` for indices `6..11`, and `4.0` for indices `18..23`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Conditional execution or transform-feedback handling for direct draws. |
| `draw_indexed` | Conditional execution or index-buffer handling for indexed draws. |
| `draw_indirect` | Conditional execution or indirect-parameter fetch for indirect draws. |
| `draw_indexed_indirect` | Conditional execution, index-buffer handling, or indexed indirect-parameter fetch. |
| `draw_multi_ext` | Conditional execution or `VK_EXT_multi_draw` handling. |
| `draw_multi_indexed_ext` | Conditional execution, index-buffer handling, or multi-indexed draw handling. |
| `draw_indirect_byte_count_ext` | Conditional execution or transform-feedback byte-count draw handling. |
| `draw_indirect_count` | Conditional execution or indirect-count draw handling. |
| `draw_indexed_indirect_count` | Conditional execution, index-buffer handling, or indexed indirect-count draw handling. |

### Cause Analysis

#### Predicate production or consumption

**Possible failure symptoms:** Query result 0 is nonzero, query result 1 is zero, or a transform-feedback range receives a value when its predicate should suppress the draw.

**Possible implementation causes:** The query result copy, predicate buffer access, conditional-rendering interpretation, or the transfer-to-conditional-rendering synchronization could produce an unexpected predicate. The Vulkan specification defines the conditional-rendering stage as the point where the predicate is consumed and permits implementations to latch or reread the predicate while the block is active. The test does not identify one specific faulty layer.

#### Transform-feedback capture and stream selection

**Possible failure symptoms:** A selected stream range does not contain its expected value, or a range that should remain zero contains a captured value.

**Possible implementation causes:** The implementation may mishandle geometry-stream selection, transform-feedback output decorations, transform-feedback activation, buffer binding, or visibility of transform-feedback writes to the host. The source binds one range per stream and synchronizes transform-feedback writes before host inspection, so source-level investigation is needed to distinguish these causes.

#### Command-specific draw path

**Possible failure symptoms:** Only one command child fails while the common query and transform-feedback checks pass for other children. Indexed variants may fail when direct non-indexed drawing passes; indirect, multi-draw, count, or byte-count variants may fail according to their command-specific input.

**Possible implementation causes:** The corresponding draw-command implementation, index fetch, indirect-parameter fetch, extension path, or count interpretation may differ from the direct path. The test covers these paths separately but does not assume whether a failure originates in command recording, command execution, or input-buffer handling.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips cases without `VK_EXT_conditional_rendering` or `VK_EXT_transform_feedback`, without the `conditionalRendering` or `geometryStreams` features, or with fewer than four transform-feedback buffers or streams.
- `draw_indirect_count` and `draw_indexed_indirect_count` require `VK_KHR_draw_indirect_count`.
- `draw_multi_ext` and `draw_multi_indexed_ext` require `VK_EXT_multi_draw`.
- `draw_indirect_byte_count_ext` requires `transformFeedbackDraw`.

### Design-based pruning

- The test registers one child per draw-command variant but does not multiply the tree by shader variant or stream index. The implementation exercises those choices inside each child.
- The geometry shader writes one value per stream and the host runs four conditional sections. The source does not generate a separate registration leaf for each stream or query predicate.

## Key Takeaways

- The test checks conditional rendering at the point where it controls transform-feedback draw commands, then verifies the captured buffer rather than relying on command submission success.
- Four stream-specific output values make suppression visible: the predicate-controlled sections leave some six-float ranges at zero and write `2.0` or `4.0` to the ranges whose predicates allow execution.
- The nine registered children reuse the same shader and result contract while covering direct, indexed, indirect, multi-draw, byte-count, and count-based draw paths.
- A failure identifies an observable mismatch in a predicate result or captured stream range. The page does not assume whether the cause is hardware, a driver, shader compilation, or host-side setup.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Command enum and names | [`DrawCommandType`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L49-L90) | Defines the nine behavior values. |
| Capability checks | [`checkSupport()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L131-L160) | Defines extension, feature, and transform-feedback property requirements. |
| Buffer preparation | [`createIndirectBuffer()` and related helpers](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L219-L314) | Shows the indexed, indirect, count, and transform-feedback buffer data. |
| Stream pipeline | [`createStreamPipeline()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L316-L384) | Creates the geometry-stream pipeline and push-constant layout. |
| Command selection | [`recordDraw()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L386-L455) | Records the command associated with each child. |
| End-to-end execution | [`iterate()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L457-L601) | Records queries, barriers, conditional rendering, transform feedback, and submission. |
| Result validation | [`iterate()` result checks](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L603-L634) | Checks query values and all 24 captured floats. |
| Shader generation | [`AddProgramsDraw::init()`](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L636-L714) | Defines the generated vertex, geometry, and fragment stages. |
| Shared conditional buffer utility | [`createConditionalRenderingBuffer()`](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Creates host-visible or device-local predicate buffers for related conditional-rendering tests. |
| Mustpass registration | [`conditional-rendering.txt`](../../../mustpass/main/vk-default/conditional-rendering.txt#L1022-L1030) | Lists the nine registered `transform_feedback` test paths. |
| Conditional-rendering specification | [Conditional Rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#drawing-conditional-rendering) | Defines predicate interpretation, active scope, and affected command classes. |
| Synchronization specification | [Pipeline stages and access masks](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-stages) | Defines conditional-rendering predicate reads and transform-feedback writes. |
