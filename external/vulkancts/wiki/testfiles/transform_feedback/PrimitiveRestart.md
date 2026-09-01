## Overview

**Core question:** Do static and dynamic primitive-restart and topology states produce the same transform-feedback capture for one indexed draw sequence?

- This page covers the implementation of the `transform_feedback.primitive_restart` test family in [`vktTransformFeedbackPrimitiveRestartTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L99).
- The family registers four executable cases. Two booleans choose whether primitive restart and primitive topology come from pipeline state or dynamic commands ([registration](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440), [mustpass](../../../mustpass/main/vk-default/transform-feedback.txt#L2169-L2172)).
- Each case uses one `VK_INDEX_TYPE_UINT16` index buffer, transform feedback, and a vertex shader that exposes the `0xFFFF` restart marker as a known position.
- The host checks the transform-feedback counter and captured positions across three draws. It accepts implementation-discarded degenerate triangles as a quality warning, but every non-degenerate triangle must match.

## Background Knowledge

- **Indexed primitive restart.** An indexed draw groups fetched indices according to `VkPrimitiveTopology`. When primitive restart is enabled for a `VK_INDEX_TYPE_UINT16` draw, `0xFFFF` ends the current primitive assembly and starts the next sequence. Vulkan compares the index with the restart value before adding `vertexOffset` ([primitive restart](../../../../vulkan-docs/src/chapters/drawing.adoc#L48-L89)).
- **Transform-feedback capture.** While transform feedback is active, the last pre-rasterization shader's selected outputs are assembled into primitives and appended to bound buffers. Vulkan allows an implementation to discard a primitive whose vertices contain equal positions, so a captured vertex count can be lower for a degenerate primitive ([transform feedback](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L42-L78)).
- **Counter-based resumption.** `vkCmdEndTransformFeedbackEXT` records the byte position of the next captured vertex in the counter buffer. A counter write-to-read barrier is required before `vkCmdBeginTransformFeedbackEXT` resumes from that position ([begin](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L433-L487), [synchronization](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1140-L1160)).

## Registration Hierarchy

```text
transform_feedback.primitive_restart
├── dynamic_primitive_restart_dynamic_primitive_topology
├── dynamic_primitive_restart_static_primitive_topology
├── static_primitive_restart_dynamic_primitive_topology
└── static_primitive_restart_static_primitive_topology
```

## Parameter Dimensions and Observed Values

The four test case leaves form the complete Cartesian product of the two boolean parameters. The values below are exact registered names and the corresponding state sources.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Primitive-restart state source | `dynamic_primitive_restart`, `static_primitive_restart` | Selects `vkCmdSetPrimitiveRestartEnable` or `VkPipelineInputAssemblyStateCreateInfo::primitiveRestartEnable`. | [`Params` and dynamic-state setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L55), [pipeline state](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L188-L211) |
| Primitive-topology state source | `dynamic_primitive_topology`, `static_primitive_topology` | Selects `vkCmdSetPrimitiveTopology` or `VkPipelineInputAssemblyStateCreateInfo::topology`. | [`Params` and dynamic-state setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L55), [pipeline state](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L188-L211) |
| Indexed input | `VK_INDEX_TYPE_UINT16` | Makes `0xFFFF` the restart marker used in the index buffer. | [index buffer binding](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L127-L144), [indexed draw](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L290-L301) |
| Index sequence | `0, 1, 65535, 9, 65535, 65535, 2000, 3000, 4000` | Provides incomplete runs, adjacent restart markers, and one complete non-degenerate triangle when restart is enabled. | [index data](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L101-L137) |
| Capture output | `gl_Position` as one `vec4` per vertex | Supplies the host-visible value used to distinguish index interpretation and draw ordering. | [shader generation](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L103-L116), [expected results](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L240-L261) |

## Behavior Parameters

The primary behavioral axis is the registered four-leaf state-source matrix. Each leaf tests the same index sequence and shader while changing where the two input-assembly states come from.

### dynamic_primitive_restart_dynamic_primitive_topology: both states dynamic

The pipeline is created with placeholder input-assembly values and lists both `VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE` and `VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY_EXT`. The command buffer sets strip/restart-enabled state for the first and third draws, then list/restart-disabled state for the second draw.

### dynamic_primitive_restart_static_primitive_topology: dynamic restart, static topology

The pipeline topology changes between pipeline A's triangle strip and pipeline B's triangle list. The restart enable is dynamic, so each draw sets it explicitly. Transform feedback stops and resumes around the pipeline change.

### static_primitive_restart_dynamic_primitive_topology: static restart, dynamic topology

The pipeline pair supplies restart enabled for pipeline A and disabled for pipeline B. The command buffer changes the topology between triangle strip and triangle list while capture runs.

### static_primitive_restart_static_primitive_topology: both states static

Pipeline A supplies triangle-strip assembly with restart enabled, and pipeline B supplies triangle-list assembly with restart disabled. This leaf exercises the pipeline-state path without dynamic input-assembly commands.

## Shader Analysis

The vertex shader is the only generated shader in this test family. One representative walkthrough covers all four leaves because the source-generated shader does not vary with either state-source parameter.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.transform_feedback.primitive_restart.static_primitive_restart_static_primitive_topology
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `static_primitive_restart_static_primitive_topology` | Selects the leaf in which pipeline A and pipeline B provide the restart and topology values. |
| `VK_INDEX_TYPE_UINT16` | Makes `65535` the primitive-restart comparison value when restart is enabled. |
| `max16 = 65535` | Makes the shader emit a safe sentinel position for the marker index in the list draw. |
| `xfb_buffer = 0`, `xfb_offset = 0` | Captures `gl_Position` into transform-feedback binding 0, starting at byte offset zero. |

#### Purpose

The vertex shader maps each fetched vertex index to a four-component position and maps the 16-bit restart marker to `(-1.0, -1.0, -1.0, -1.0)`. The host can then compare the capture stream while the input assembler alternates between restart-enabled strip assembly and restart-disabled list assembly.

#### Structural Design

| Shader phase | Operation | Result used by the test |
|--------------|-----------|-------------------------|
| Input | Read `gl_VertexIndex` into `vid`. | The value identifies either an ordinary index or the marker. |
| Marker branch | If `vid == 65535`, produce four `-1.0` components. | The list draw can capture the marker as data without an invalid position. |
| Ordinary branch | Convert `vid` to four floating-point components. | The host recognizes indices `0`, `1`, `9`, `2000`, `3000`, and `4000`. |
| Capture | Store the selected `gl_Position` output in XFB buffer 0. | The host compares positions and the counter after all three draws. |

#### Shader Code

```glsl
#version 460
layout(xfb_buffer = 0, xfb_offset = 0) out gl_PerVertex {
    /// The only captured shader output. XFB stride is derived from this vec4 output.
    vec4 gl_Position;
};
void main(void) {
    /// This is the post-indexing vertex index. The host binds the index buffer as uint16.
    const int vid = gl_VertexIndex;
    /// 65535 is the special uint16 index used for primitive restart.
    const int max16 = 65535; // 16-bit indices.
    /// Keep the marker observable when the same index buffer is drawn with restart disabled.
    gl_Position = ((vid == max16) ? vec4(-1.0, -1.0, -1.0, -1.0) : vec4(vid, vid, vid, vid));
}
```

#### Additional Info

- The shader source is identical for all four registered leaves. The leaf changes pipeline or dynamic input-assembly state, not shader code ([`initPrograms`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L101-L116), [matrix construction](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L432-L438)).
- The `xfb_buffer` and `xfb_offset` layout qualifiers cause the vertex output to use transform-feedback buffer 0 at offset zero. The host binds the corresponding buffer before beginning capture ([shader setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L103-L115), [buffer binding](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L284-L296)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `dynamicPrimitiveRestart` | No variation. The same shader runs with pipeline restart state or `vkCmdSetPrimitiveRestartEnable`. | [`Params`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L65), [dynamic restart command](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L297-L301) |
| `dynamicPrimitiveTopology` | No variation. The same shader runs with pipeline topology or `vkCmdSetPrimitiveTopology`. | [`Params`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L65), [dynamic topology command](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L314-L318) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
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
               OpCapability TransformFeedback
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_
               OpExecutionMode %main Xfb
               OpSource GLSL 460
               OpName %main "main"
               OpName %vid "vid"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 0 Offset 0
               OpDecorate %_ XfbBuffer 0
               OpDecorate %_ XfbStride 16
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
  %int_65535 = OpConstant %int 65535
       %bool = OpTypeBool
%_ptr_Function_v4float = OpTypePointer Function %v4float
   %float_n1 = OpConstant %float -1
         %27 = OpConstantComposite %v4float %float_n1 %float_n1 %float_n1 %float_n1
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
        %vid = OpVariable %_ptr_Function_int Function
         %23 = OpVariable %_ptr_Function_v4float Function
         %11 = OpLoad %int %gl_VertexIndex
               OpStore %vid %11
         %18 = OpLoad %int %vid
         %21 = OpIEqual %bool %18 %int_65535
               OpSelectionMerge %25 None
               OpBranchConditional %21 %24 %28
         %24 = OpLabel
               OpStore %23 %27
               OpBranch %25
         %28 = OpLabel
         %29 = OpLoad %int %vid
         %30 = OpConvertSToF %float %29
         %31 = OpLoad %int %vid
         %32 = OpConvertSToF %float %31
         %33 = OpLoad %int %vid
         %34 = OpConvertSToF %float %33
         %35 = OpLoad %int %vid
         %36 = OpConvertSToF %float %35
         %37 = OpCompositeConstruct %v4float %30 %32 %34 %36
               OpStore %23 %37
               OpBranch %25
         %25 = OpLabel
         %38 = OpLoad %v4float %23
         %40 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %40 %38
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `PrimitiveRestartCase::checkSupport()` requires `VK_EXT_transform_feedback`. The dynamic-restart leaf also requires `VK_EXT_extended_dynamic_state2`, and the dynamic-topology leaf requires `VK_EXT_extended_dynamic_state` ([support checks](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L90-L99)).
- The host creates a host-visible `uint16_t` index buffer with nine indices, a host-visible transform-feedback buffer initialized to zero, and a host-visible 4-byte counter buffer initialized to zero ([resource setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L127-L144), [XFB resources](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L264-L282)).
- Pipeline A uses `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` with restart enabled. Pipeline B uses `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` with restart disabled. When both dimensions are dynamic, the test creates only pipeline A and changes both states by command ([pipeline construction](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L146-L237)).
- The command buffer binds the XFB and index buffers, begins capture, and issues three indexed draws. The first and third use strip/restart-enabled state. The second uses list/restart-disabled state. In the three two-pipeline leaves, the host ends and resumes transform feedback around the pipeline bind and inserts a counter write-to-read barrier ([draw sequence](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L284-L347)).
- The host waits for submission completion, invalidates both allocations, and reads the counter and captured positions. It rejects a counter larger than the expected maximum before copying the capture buffer ([readback](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L346-L368)).
- The expected stream contains three positions from the first draw, nine from the second, and three from the third. An expected triangle with equal positions may be skipped because Vulkan permits degenerate primitive discard. The final counter must equal the expected byte count after those skips, and every other position must match exactly ([expected stream](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L240-L261), [comparison](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L370-L413)).
- The result is `pass` when no degenerate triangle is skipped, `quality_warning` when the implementation skips one or more degenerate triangles without another mismatch, and failure for an unexpected position or counter value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dynamic_primitive_restart_dynamic_primitive_topology` | Incorrect interaction between `vkCmdSetPrimitiveRestartEnable`, `vkCmdSetPrimitiveTopology`, indexed primitive assembly, and transform-feedback capture. |
| `dynamic_primitive_restart_static_primitive_topology` | Dynamic primitive-restart state is not applied to the indexed draw or does not agree with the statically selected topology. |
| `static_primitive_restart_dynamic_primitive_topology` | Dynamic topology state is not applied to the indexed draw or does not agree with the pipeline's restart state. |
| `static_primitive_restart_static_primitive_topology` | Pipeline input-assembly primitive-restart or topology state is not honored during transform-feedback capture. |

A counter or position failure in any leaf can also indicate a common transform-feedback resource, counter-resume, synchronization, or host readback problem. The test records those effects through the same counter and position checks.

### Cause Analysis

#### Dynamic input-assembly state application

**Possible failure symptoms:** In a leaf with a dynamic dimension, the marker is assembled as ordinary data when restart should be enabled, or it splits assembly when restart should be disabled. The captured positions then differ from the expected stream, or the counter records a different number of captured vertices.

**Possible implementation causes:** The relevant dynamic-state command may not affect the subsequent indexed draw, or the implementation may combine the dynamic topology and restart values incorrectly. The Vulkan specification defines `vkCmdSetPrimitiveRestartEnable` as equivalent in behavior to pipeline `primitiveRestartEnable` and applies it to subsequent drawing commands when the state is dynamic ([dynamic restart](../../../../vulkan-docs/src/chapters/drawing.adoc#L144-L178)). Source inspection is needed to distinguish a driver state-tracking issue from an assembly issue.

#### Static input-assembly state application

**Possible failure symptoms:** A static/static leaf, or the static dimension of another leaf, captures the sequence expected for the other pipeline. The host reports a position mismatch or a counter that does not equal the expected number of captured `vec4` values.

**Possible implementation causes:** The active graphics pipeline may not apply its `VkPipelineInputAssemblyStateCreateInfo` topology or restart value to indexed assembly. Vulkan requires the restart state to control special-index handling for indexed draws and restricts restart for list topologies unless the applicable feature is enabled ([input assembly](../../../../vulkan-docs/src/chapters/drawing.adoc#L48-L112)). The exact failing state path needs source- and implementation-level investigation.

#### Transform-feedback capture and counter resumption

**Possible failure symptoms:** Captured positions are shifted between the three draw segments, the counter is too large or too small, or the final counter disagrees with the number of non-skipped expected vertices. A counter larger than the maximum expected value fails before the host copies the result buffer.

**Possible implementation causes:** The implementation may capture the wrong assembled primitives, update the transform-feedback counter incorrectly, or fail to make the counter write visible before resumption. The source inserts `VK_ACCESS_TRANSFORM_FEEDBACK_COUNTER_WRITE_BIT_EXT` to `VK_ACCESS_TRANSFORM_FEEDBACK_COUNTER_READ_BIT_EXT` barriers between the end and restart calls, matching the specification's counter-resume requirement ([command recording](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L303-L328), [specification](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L447-L467)). A persistent mismatch requires investigation of the implementation's transform-feedback and synchronization paths.

#### Degenerate primitive handling

**Possible failure symptoms:** The host finds fewer captured vertices than the full expected stream but all remaining non-degenerate positions match. The test returns a quality warning. If the host skips a degenerate expected triangle and then finds a mismatch or an inconsistent counter, the case fails.

**Possible implementation causes:** Vulkan allows a primitive with equal-position vertices to be discarded before primitive assembly, so the lower count can be conformant ([degenerate discard](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L65-L78)). A failure beyond that allowance needs investigation of the captured primitive sequence, counter update, or host comparison rather than assuming a particular hardware fault.

## Case Pruning

### Requirement-based pruning

- The entire family is unavailable unless `VK_EXT_transform_feedback` is supported.
- Cases with dynamic primitive restart require `VK_EXT_extended_dynamic_state2`.
- Cases with dynamic primitive topology require `VK_EXT_extended_dynamic_state`.
- The source does not add cases for unsupported feature combinations. `checkSupport()` reports them before the instance runs ([support checks](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L90-L99)).

### Design-based pruning

- The source keeps exactly the 2x2 matrix of state sources. It does not add separate shader variants because the shader does not depend on how the input-assembly state was supplied.
- The second pipeline is omitted when both dimensions are dynamic. One pipeline is sufficient because both relevant states can change between draws. The other leaves use two pipelines to compare pipeline A and pipeline B state ([pipeline selection](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L146-L149), [dynamic-state commands](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L293-L334)).
- The test does not treat the three adjacent or isolated restart markers as independent registered cases. They are fixed positions in one index sequence, chosen to create incomplete and complete assembly runs for the three draws ([index sequence](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L127-L137)).

## Key Takeaways

- The four leaves isolate the source of primitive-restart and topology state without changing the shader or index buffer.
- With restart enabled, `0xFFFF` separates indexed primitive runs. With restart disabled, the shader turns that value into a known `gl_Position` so the same data remains safe to capture.
- The test resumes one transform-feedback stream across pipeline changes by carrying the byte position through a counter buffer and synchronizing its write before the next begin call.
- A lower capture count is allowed only for degenerate triangles. All non-degenerate positions and the final counter must still match.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter and support model | [`PrimitiveRestartInstance::Params`, `PrimitiveRestartCase::checkSupport`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L99) | Defines the two state-source dimensions and feature requirements. |
| Generated vertex shader | [`PrimitiveRestartCase::initPrograms`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L101-L116) | Defines transform-feedback output and the marker-position mapping. |
| Index and pipeline setup | [`PrimitiveRestartInstance::iterate`, setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L118-L237) | Defines the uint16 index sequence, pipeline state, dynamic states, and resources. |
| Command recording | [`PrimitiveRestartInstance::iterate`, draws and barriers](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L284-L347) | Defines binding, three-draw ordering, capture transitions, and synchronization. |
| Result checking | [`PrimitiveRestartInstance::iterate`, readback and status](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L349-L413) | Defines counter bounds, degenerate handling, position comparison, and result status. |
| Registration | [`createTransformFeedbackPrimitiveRestartTests`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440) | Defines the exact four test case leaves. |
| Mustpass coverage | [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L2169-L2172) | Confirms all four leaves are present in the default mustpass list. |
| Primitive restart rules | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L48-L89) | Defines marker comparison and indexed primitive assembly. |
| Transform-feedback rules | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L42-L78) | Defines active capture and the degenerate-primitive discard allowance. |
| Counter synchronization | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1140-L1160) | Defines the transform-feedback counter access transition used during resumption. |
