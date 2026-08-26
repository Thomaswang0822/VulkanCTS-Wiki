## Overview

**Core question:** Do supported vertex-input and draw-command paths advance instance-rate attributes at the selected divisor and first-instance origin?

`vertex_attribute_divisor` checks instance-rate vertex input with the `VK_EXT_vertex_attribute_divisor` and `VK_KHR_vertex_attribute_divisor` extensions. It makes divisor behavior visible in a rendered image: a per-vertex quad-grid position/color stream is combined with a second, instance-rate color stream, and the GPU result is compared with an equivalent reference-renderer draw.

The implementation is one parameterized test family, not an Amber wrapper. Each leaf selects an extension spelling, pipeline construction method, draw command, first-instance mode, and divisor value.

## Background Knowledge

Vertex input rate controls whether an attribute advances per vertex or per instance. A vertex attribute divisor changes the instance-rate advancement interval. A divisor of zero reuses one element, while a nonzero divisor advances after the corresponding number of instances.

## Registration Hierarchy

- Implementation: [vktDrawVertexAttribDivisorTests.cpp](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp)
- Category dispatcher: [vktDrawTests.cpp](../../../modules/vulkan/draw/vktDrawTests.cpp)

The dispatcher registers this family through `createVertexAttributeDivisorTests()` for the ordinary draw groups. The direct render-pass path is:

```text
draw.renderpass.vertex_attribute_divisor
├── ext
└── khr

draw.dynamic_rendering.primary_cmd_buff.vertex_attribute_divisor
├── ext
└── khr

draw.dynamic_rendering.partial_secondary_cmd_buff.vertex_attribute_divisor
├── ext
└── khr

draw.dynamic_rendering.complete_secondary_cmd_buff.vertex_attribute_divisor
├── ext
└── khr
```

Each extension child expands into the pipeline, draw-command, first-instance, and divisor dimensions described below. The deeper generated leaves are intentionally flattened because the registration validator accepts only direct children in these trees. The dynamic-rendering trees correspond to the three non-nested command-buffer modes created by the dispatcher.

The dispatcher also creates `nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` modes, but `createChildren()` does not register `vertex_attribute_divisor` when `nestedSecondaryCmdBuffer` is true. `shader_objects` is emitted only when `useDynamicRendering` is true, so it is absent from the render-pass tree and present in the three dynamic-rendering trees. The source dispatcher omits the whole dynamic-rendering hierarchy in Vulkan SC builds.

## Parameter Dimensions and Observed Values

The source loops over these dimensions in this order:

| Dimension | Registered values |
|---|---|
| Extension | `ext`, `khr` |
| Pipeline | `static_pipeline`, `dynamic_pipeline`, `shader_objects` (dynamic rendering only) |
| Draw command | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_multi_ext`, `draw_multi_indexed_ext`, `draw_indirect_byte_count`, `draw_indirect_count`, `draw_indexed_indirect_count` |
| First instance | `zero`, `non_zero` |
| Divisor leaf | `0`, `1`, `2`, `16` |

`draw_indirect_byte_count` is excluded when `CTS_USES_VULKANSC` is defined. The command names map directly to the calls in `VertexAttributeDivisorInstance::draw()`. The `draw_multi_*` leaves require `VK_EXT_multi_draw`; indirect leaves require `VK_KHR_draw_indirect_count` according to the implementation's support check.

## Behavior Parameters

The primary behavior axes are extension spelling, pipeline delivery, draw command, first instance, and divisor. The same divisor contract is exercised across these delivery and command variants.

### Extension and pipeline delivery

`ext` and `khr` select the extension spelling. `static_pipeline` supplies divisor state at pipeline creation, while `dynamic_pipeline` sets vertex input immediately before the draw. `shader_objects` uses shader objects and dynamic vertex input and is limited to dynamic rendering.

### Draw command and instance origin

The direct, indexed, indirect, multi-draw, byte-count, and count-draw commands expose the divisor under different command-recording paths. `zero` and `non_zero` first-instance leaves test whether the instance origin is applied consistently.

### Divisor values

The registered divisor values are `0`, `1`, `2`, and `16`. The zero value reuses the same instance-rate attribute, while the nonzero values advance the attribute stream at different rates.

## Shader Analysis

### Shader inventory and representative selection

`initPrograms()` emits exactly two GLSL programs for every leaf: `vert`, a generated vertex shader, and `frag`, a generated pass-through fragment shader. None of the extension, pipeline, draw-command, first-instance, or divisor parameters changes either shader string. Static pipelines, dynamic-vertex-input pipelines, and shader objects all consume the same compiled binaries; the tested divisor is vertex-input state and therefore does not appear as a SPIR-V constant or decoration ([shader generation](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1033-L1065), [pipeline and shader-object binary use](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L379-L426)).

The vertex stage is the primary shader because it observes `gl_InstanceIndex` and the divisor-controlled location 2 attribute. The fragment stage only copies location 0 to the color attachment. Consequently, one vertex-shader walkthrough covers the complete shader inventory.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.vertex_attribute_divisor.ext.static_pipeline.draw.zero.2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ext` | Uses the `VK_EXT_vertex_attribute_divisor` spelling and its support gates. |
| `static_pipeline` | Supplies the divisor in pipeline vertex-input state. |
| `draw` | Records a direct, non-indexed draw. |
| `zero` | Starts the absolute instance index at zero. |
| `2` | Repeats each binding-1 element for two consecutive relative instances. |

This path is present in the `vk-default` mustpass inventory ([mustpass entry](../../../mustpass/main/vk-default/draw.txt#L29176)). It chooses divisor 2 as an easy-to-observe advancement interval, but its shader binary is identical to every other leaf's. At runtime, the host iterates instance counts `0`, `1`, `2`, `4`, and `20`; this walkthrough describes the non-empty draws, for which the shader arithmetic is observable ([runtime loop](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L505)).

#### Purpose

The shader turns instance-rate attribute fetch into image-visible position and color. It removes `firstInstance` from the horizontal position so the same relative instance sequence occupies the same geometry locations, while retaining the absolute `gl_InstanceIndex` in the red channel. Adding `in_color_2` then exposes which binding-1 element Vulkan fetched under the selected divisor.

#### Structural Design

| Shader value | Source | Observable role |
|---|---|---|
| `in_position` | Binding 0, location 0, per vertex | Base quad-grid position. |
| `in_color` | Binding 0, location 1, per vertex | Base quad color. |
| `in_color_2` | Binding 1, location 2, per instance | Divisor-controlled color whose repetition/advancement is under test. |
| `params.firstInstance` | Push constant offset 0 | Converts the absolute instance index into a relative horizontal offset. |
| `params.instanceCount` | Push constant offset 4 | Normalizes position and red-channel changes over the draw. |
| `gl_InstanceIndex` | Vulkan vertex built-in | Carries the draw's absolute instance number, including `firstInstance`. |
| `out_color` | Vertex output location 0 | Sum consumed by the pass-through fragment shader and image comparison. |

The host maps locations 0 and 1 to binding 0 and location 2 to instance-rate binding 1; the selected `VkVertexInputBindingDivisorDescription` applies to binding 1 ([vertex-input setup](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L334-L371)). For the representative divisor-2 path, pairs of consecutive relative instances receive the same binding-1 element. This repetition comes from vertex-input fetch, not shader instructions.

#### Shader Code

##### Vertex Shader

```glsl
#version 430
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 2) in vec4 in_color_2;
layout(push_constant) uniform TestParams {
    float firstInstance;
    float instanceCount;
} params;
layout(location = 0) out vec4 out_color;
out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
};
void main() {
    gl_PointSize = 1.0;
    gl_Position  = in_position + vec4(float(gl_InstanceIndex - params.firstInstance) * 2.0 / params.instanceCount, 0.0, 0.0, 0.0);
    out_color    = in_color + vec4(float(gl_InstanceIndex) / params.instanceCount, 0.0, 0.0, 1.0) + in_color_2;
}
```

##### Fragment Shader

```glsl
#version 430
layout(location = 0) in vec4 in_color;
layout(location = 0) out vec4 out_color;
void main()
{
    out_color = in_color;
}
```

#### Additional Info

- `gl_InstanceIndex` is signed in SPIR-V (`OpTypeInt 32 1`). The generated module converts it to float before subtracting the float push constant, matching GLSL's mixed expression.
- The push-constant block members are decorated at offsets 0 and 4, matching the host's two-float range ([pipeline layout](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L287-L294)).
- The final SPIR-V contains location decorations 0, 1, and 2 and the `InstanceIndex` built-in, but no vertex-rate or divisor metadata. Those semantics belong to pipeline vertex-input state.
- The fragment shader cannot distinguish divisor behavior on its own; it only preserves the interpolated vertex result for readback.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `ext` / `khr` | No shader change. Selects the extension spelling and support gates. | [support checks](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L971-L1000) |
| `static_pipeline` / `dynamic_pipeline` / `shader_objects` | No shader or binary change. Delivers the same vertex-input description and binaries through different state paths. | [pipeline and shader-object binary use](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L379-L426) |
| Draw-command family | No shader change. Changes direct, indexed, indirect, count, multi-draw, or byte-count command encoding. | [draw dispatch](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L700-L911) |
| `zero` / `non_zero` first instance | No source or binary change; push-constant and built-in values change. Exercises absolute instance origin while preserving relative horizontal placement. | [runtime loop](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L505) |
| Divisor `0`, `1`, `2`, or `16` | No source or binary change; no divisor opcode or decoration exists in SPIR-V. Changes how binding 1 supplies `in_color_2`; divisor 0 reuses one element. | [vertex-input setup](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L334-L371) |
| Runtime instance count | No source or binary change; `params.instanceCount` changes. Controls draw count and normalizes instance-dependent outputs; a zero-count draw invokes no shader. | [runtime loop](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L505) |

#### SPIR-V

##### Vertex Shader

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
; Bound: 54
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %gl_InstanceIndex %out_color %in_color %in_color_2
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %TestParams "TestParams"
               OpMemberName %TestParams 0 "firstInstance"
               OpMemberName %TestParams 1 "instanceCount"
               OpName %params "params"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpName %in_color_2 "in_color_2"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %in_position Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %TestParams Block
               OpMemberDecorate %TestParams 0 Offset 0
               OpMemberDecorate %TestParams 1 Offset 4
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
               OpDecorate %in_color_2 Location 2
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
 %TestParams = OpTypeStruct %float %float
%_ptr_PushConstant_TestParams = OpTypePointer PushConstant %TestParams
     %params = OpVariable %_ptr_PushConstant_TestParams PushConstant
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
    %float_2 = OpConstant %float 2
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
 %in_color_2 = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %15 %float_1
         %19 = OpLoad %v4float %in_position
         %22 = OpLoad %int %gl_InstanceIndex
         %23 = OpConvertSToF %float %22
         %28 = OpAccessChain %_ptr_PushConstant_float %params %int_0
         %29 = OpLoad %float %28
         %30 = OpFSub %float %23 %29
         %32 = OpFMul %float %30 %float_2
         %33 = OpAccessChain %_ptr_PushConstant_float %params %int_1
         %34 = OpLoad %float %33
         %35 = OpFDiv %float %32 %34
         %37 = OpCompositeConstruct %v4float %35 %float_0 %float_0 %float_0
         %38 = OpFAdd %v4float %19 %37
         %40 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %40 %38
         %43 = OpLoad %v4float %in_color
         %44 = OpLoad %int %gl_InstanceIndex
         %45 = OpConvertSToF %float %44
         %46 = OpAccessChain %_ptr_PushConstant_float %params %int_1
         %47 = OpLoad %float %46
         %48 = OpFDiv %float %45 %47
         %49 = OpCompositeConstruct %v4float %48 %float_0 %float_0 %float_1
         %50 = OpFAdd %v4float %43 %49
         %52 = OpLoad %v4float %in_color_2
         %53 = OpFAdd %v4float %50 %52
               OpStore %out_color %53
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_color %in_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 430
               OpName %main "main"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %in_color
               OpStore %out_color %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The generated vertex shader and reference renderer consume the same position, base-color, and divisor-controlled color streams. The GPU image is read back after the selected render path and compared with the reference image using the source fuzzy threshold.

### Pipeline variants

- `static_pipeline` puts the two binding descriptions, three attributes, and `VkVertexInputBindingDivisorDescription` into pipeline creation.
- `dynamic_pipeline` makes `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` dynamic and calls `vkCmdSetVertexInputEXT` immediately before the draw with the selected divisor.
- `shader_objects` creates vertex and fragment shader objects from the `vert` and `frag` binaries, binds them at draw time, sets the required default viewport/scissor state, and uses dynamic vertex input. This variant is only registered for dynamic rendering and is not compiled into Vulkan SC.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior axis | Possible implementation cause |
|---|---|
| Divisor `0`, `1`, `2`, or `16` | Incorrect instance-rate advancement, divisor state, or attribute fetch. |
| Nonzero first instance | Incorrect first-instance handling or indirect command interpretation. |
| Static versus dynamic pipeline | Incorrect pipeline vertex-input state or dynamic vertex-input command. |
| Direct, indexed, indirect, multi-draw, or count command | Command-record encoding, count-buffer handling, index handling, or divisor state propagation. |
| Shader-object path | Shader-object binding, dynamic vertex input, or dynamic-rendering setup. |

### Cause Analysis

#### Attribute advancement

**Possible failure symptoms:** The rendered image differs from the reference in instance-dependent position or color.

**Possible implementation causes:** The implementation may advance the instance-rate binding at the wrong interval, ignore divisor zero semantics, apply the wrong first-instance base, or use an incorrect attribute offset.

#### Command and pipeline delivery

**Possible failure symptoms:** Only one pipeline or draw-command family fails while the same divisor values pass elsewhere.

**Possible implementation causes:** The selected pipeline state, dynamic vertex-input command, indirect record, count buffer, multi-draw record, or shader-object binding may not carry the divisor configuration correctly.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the selected extension, dynamic state, shader-object, multi-draw, indirect-count, transform-feedback, or dynamic-rendering requirement is unavailable.

### Design-based pruning

Vulkan SC excludes the byte-count and dispatcher paths that are guarded out by the source.

Support-gate details are retained below as prose:

`checkSupport()` requires the selected divisor extension (`VK_EXT_vertex_attribute_divisor` or `VK_KHR_vertex_attribute_divisor`). It checks `supportsNonZeroFirstInstance` for non-zero first-instance cases, `drawIndirectFirstInstance` for non-zero indirect cases, `vertexAttributeInstanceRateDivisor` for divisor 1, and `vertexAttributeInstanceRateZeroDivisor` for divisor 0. It also gates dynamic vertex input, shader objects, multi-draw, indirect-count functionality, and dynamic rendering according to the selected dimensions. The byte-count command additionally requires transform feedback, `transformFeedback`, and `transformFeedbackDraw`, and is not available in Vulkan SC.

Verification:

For every `(instanceCount, firstInstance)` pair, the implementation constructs an `rr::Renderer` reference using the same vertex data, colors, indices when applicable, and divisor-controlled attribute stream. The reference uses `INT_MAX` for the divisor-0 input because of the reference renderer's divisor convention; this is an implementation detail of the reference setup, while the Vulkan divisor remains 0.

The rendered GPU image is read back from the color target and compared to the reference with `tcu::fuzzyCompare(..., 0.05f, ...)`. Any mismatch across the loop is recorded and causes the leaf to fail with `Unexpected results in output buffers`; otherwise the leaf returns `Pass`.

## Key Takeaways

- The family varies extension spelling, pipeline delivery, draw command, first instance, and divisor value.
- The shader exposes divisor behavior through instance-dependent position and color, and the host compares the result with a reference renderer.
- Support skips are distinct from image-comparison failures and reflect the selected command or feature requirements.

## Source Reference Appendix

- Parameters and helper classification: [lines 48-132](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L48-L132)
- Pipeline and vertex-input setup: [lines 279-475](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L279-L475)
- Iteration, command recording, and image comparison: [lines 478-698](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L698)
- Test data and draw-command dispatch: [lines 700-911](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L700-L911)
- Support checks and GLSL binaries: [lines 953-1065](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L953-L1065)
- Family registration loops: [lines 1070-1198](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1070-L1198)

### Scope boundary

Shared render-pass, dynamic-rendering, and secondary-command-buffer placement belongs to the draw category dispatcher and shared draw infrastructure. This page documents how the divisor family uses those modes; it does not duplicate their category-wide registration policy.
