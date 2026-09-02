## Overview

**Core question:** Does EXT device-generated execution preserve the tessellation state selected for each layer, including primitive type, spacing, patch size, preprocessing, and dynamic patch-control points?

- This page covers `dgc.ext.graphics.tess_state`, implemented by `vktDGCGraphicsTessStateTestsExt.cpp`.
- The regular cases draw two tessellated layers through two pipelines. Each layer has its own primitive type, spacing mode, and patch size, so the framebuffer records whether the selected state reached the tessellation stages.
- The regular matrix uses `monolithic`, `fast_lib`, and `shader_objects` construction types. `dynamic_states` adds cases that set `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` before generated draws.
- The test compares the read-back color against exact reference images for regular cases, and compares a DGC result image with an ordinary reference draw for dynamic patch-control-points cases.

## Background Knowledge

- **Tessellation patch state.** A patch is the input unit for tessellation. Its control-point count comes from the pipeline tessellation state, or from `vkCmdSetPatchControlPointsEXT` when `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` is enabled. The tessellation control shader sees this count as `gl_PatchVerticesIn`.
- **Tessellation primitive and spacing.** The tessellation evaluation shader interprets `gl_TessCoord` according to the output primitive (`triangles`, `quads`, or `isolines`) and spacing mode (`equal_spacing`, `fractional_odd_spacing`, or `fractional_even_spacing`). The test uses point mode and maps those generated points into a known framebuffer region.
- **Device-generated commands.** `VK_EXT_device_generated_commands` lets the command stream select an execution-set entry and issue a draw from buffer data. Explicit preprocessing adds a preprocessing command buffer and a barrier before execution. These mechanisms change how state reaches the draw, not the tessellation rules themselves.

## Registration Hierarchy

```text
dgc.ext.graphics.tess_state
├── dynamic_states
├── fast_lib
├── monolithic
└── shader_objects
```

The three construction-type children under the regular path are registered directly by the factory. `dynamic_states` contains `monolithic` and `fast_lib` children; it omits `shader_objects` because shader objects already expose the relevant state dynamically.

## Parameter Dimensions and Observed Values

The factory forms a cross-product for the regular construction-type children, then adds a separate dynamic-state family.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Regular construction type | `monolithic`, `fast_lib`, `shader_objects` | Selects how the two pipelines or shader objects are constructed while keeping the tessellation comparison the same. | [construction types and registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1164-L1173) |
| First and second primitive type | `triangles`, `isolines`, `quads` | Selects the tessellation output primitive for layer 0 and layer 1. | [primitive enumeration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L85-L110), [regular case loops](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1178-L1182) |
| First and second spacing mode | `equal_spacing`, `fractional_odd_spacing`, `fractional_even_spacing` | Selects how tessellation levels are interpreted independently for the two layers. | [spacing enumeration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L57-L83), [regular case loops](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1184-L1188) |
| First and second patch size | `3`, `4` | Selects the `vertices` output count in each tessellation control shader and the corresponding coordinate calculation. | [patch-size assertion and shader specialization](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L139-L158), [patch-size loops](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1190-L1192) |
| Preprocessing | absent from the case name, `preprocess` | Selects whether the EXT command stream is preprocessed in a separate command buffer before execution. | [preprocess loop and case naming](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1190-L1214) |
| Dynamic patch-control-points mode | `pcp`, `pcp_ies`, `pcp_preprocess`, `pcp_ies_preprocess` | Selects direct or execution-set pipeline selection and whether the generated commands use explicit preprocessing. | [dynamic-state registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1225-L1249) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group**. The regular group changes tessellation state independently on two framebuffer layers. The dynamic group checks whether a dynamic patch-control-points value overrides the pipeline's static value when generated draws run.

### Regular tessellation-state pairs | Independent layer state

Each regular case creates two pipelines. Both use patch-list topology and the same vertex and fragment shaders, but their tessellation control and evaluation shaders are specialized from the two `LayerParams` values. The first evaluation shader writes layer `0`; the second writes layer `1`. The factory skips combinations where primitive type, spacing, and patch size are identical on both layers, because such a pair cannot show whether the two selected states remain distinct.

The evaluation shader uses `point_mode`. For three control points, the triangle path reconstructs a position from barycentric coordinates. For four control points, it uses the last two input positions as the midpoint of a triangle for triangles, or the four corners for quads and four-point isolines. The selected reference image contains the expected blue point pattern for each `(primitive type, spacing, patch size)` value.

The generated command stream selects pipeline 0 for layer 0 and pipeline 1 for layer 1, then issues one `VkDrawIndirectCommand` per layer. With shader objects, the execution set selects the four stage shader objects for each layer instead of whole pipelines.

### Dynamic patch-control-points | Dynamic state override

The dynamic cases use quads in the tessellation shaders. Each result pipeline declares `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` but has a static patch-control-points value of `3`. The command buffer records `vkCmdSetPatchControlPointsEXT` with `4` before generated draws. The tessellation control and evaluation shaders add a large position offset when `gl_PatchVerticesIn` is not `4`, so using the stale static value moves the result away from the expected quadrant.

The four generated draws use push-constant offsets to place four colored sections at `(-1,-1)`, `(0,-1)`, `(-1,0)`, and `(0,0)`. With an indirect execution set, each sequence selects its matching color pipeline. Without one, the generated draw stream still exercises the dynamic patch-control-points state but uses the initial pipeline. The reference pass sets the patch count statically to `4` and draws the same offsets with ordinary commands.

## Shader Analysis

The source generates vertex, tessellation-control, tessellation-evaluation, and fragment GLSL strings. The representative walkthrough below follows one regular two-layer case. The shader code is the mechanism that makes a wrong tessellation state visible as a different point pattern; the host-side image comparison decides the result.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.tess_state.monolithic.triangles_quads.equal_spacing_fractional_odd_spacing.3_4_preprocess
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` | Builds two ordinary graphics pipelines. |
| `triangles_quads` | Layer 0 uses triangular output; layer 1 uses quadrilateral output. |
| `equal_spacing_fractional_odd_spacing` | Layer 0 uses equal spacing; layer 1 uses fractional odd spacing. |
| `3_4` | The first tessellation control shader outputs three control points and the second outputs four. |
| `preprocess` | The generated command stream is preprocessed before execution. |

#### Purpose

The two evaluation shaders convert their tessellation coordinates into known point positions and write to different layers. A mismatch in primitive type, spacing, or patch size changes the point pattern and causes the corresponding layer comparison to fail.

#### Structural Design

| Stage | Layer 0 | Layer 1 | State under test |
|-------|---------|---------|------------------|
| Vertex | Supplies four corner positions and point size. | Supplies the same four corner positions and point size. | Shared input to both pipelines. |
| Tessellation control | Uses `layout (vertices=3) out` and forwards the first three inputs. | Uses `layout (vertices=4) out` and forwards all four inputs. | Patch size. |
| Tessellation evaluation | Uses `layout(triangles, equal_spacing, point_mode) in` and barycentric coordinates. | Uses `layout(quads, fractional_odd_spacing, point_mode) in` and two-dimensional coordinates. | Primitive type and spacing. |
| Fragment | Writes opaque blue. | Writes opaque blue. | Makes generated points easy to compare with the reference image. |

#### Shader Code

The source specializes one common shader template for each layer. The following is the complete generated tessellation-evaluation shader for layer 0 of the representative case. The tessellation-control stage is shown separately to explain the patch-size input, while the embedded artifact corresponds exactly to this evaluation-stage source.

##### Tessellation control stage

```glsl
#version 460
layout (vertices=3) out;
void main() {
    if (gl_InvocationID < gl_PatchVerticesIn) {
        gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
        gl_out[gl_InvocationID].gl_PointSize = gl_in[gl_InvocationID].gl_PointSize;
    }
}
```

##### Tessellation evaluation stage

```glsl
#version 460
#extension GL_ARB_shader_viewport_layer_array : enable
layout(triangles, equal_spacing, point_mode) in;
void main() {
    const float u = gl_TessCoord.x;
    const float v = gl_TessCoord.y;
    const float w = gl_TessCoord.z;
    gl_Position = (u * gl_in[0].gl_Position) +
                  (v * gl_in[1].gl_Position) +
                  (w * gl_in[2].gl_Position);
    gl_PointSize = 1.0;
    gl_Layer = 0;
}
```

The second evaluation shader substitutes `quads`, `fractional_odd_spacing`, a four-control-point coordinate calculation, and `gl_Layer = 1`. The source also builds SPIR-V 1.0 and SPIR-V 1.5 versions because the layer built-in uses the shader viewport/layer extension path on older API versions.

#### Additional Info

- The fragment shader writes `vec4(0.0, 0.0, 1.0, 1.0)`.
- Regular reference data is included in `vktDGCGraphicsTessStateRefImages.hpp` and indexed by `(primitive type, spacing, patch size)`.
- The dynamic-state shaders use `gl_PatchVerticesIn` as the observable check for the dynamic patch-control-points value.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Primitive type | The evaluation layout and coordinate mapping change between `triangles`, `isolines`, and `quads`. | [evaluation shader templates](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L317-L361) |
| Spacing | The evaluation layout changes between `equal_spacing`, `fractional_odd_spacing`, and `fractional_even_spacing`. | [spacing specialization](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L363-L387) |
| Patch size | The control shader's `vertices` layout changes between `3` and `4`. | [control shader specialization](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L279-L310) |

#### SPIR-V

##### Tessellation evaluation stage

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 61
; Schema: 0
               OpCapability Tessellation
               OpCapability TessellationPointSize
               OpCapability ShaderViewportIndexLayerEXT
               OpExtension "SPV_EXT_shader_viewport_index_layer"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord %_ %gl_in %gl_Layer
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpExecutionMode %main PointMode
               OpSource GLSL 460
               OpSourceExtension "GL_ARB_shader_viewport_layer_array"
               OpName %main "main"
               OpName %u "u"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %v "v"
               OpName %w "w"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %gl_Layer "gl_Layer"
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
               OpDecorate %gl_Layer BuiltIn Layer
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
%_ptr_Output_int = OpTypePointer Output %int
   %gl_Layer = OpVariable %_ptr_Output_int Output
       %main = OpFunction %void None %3
          %5 = OpLabel
          %u = OpVariable %_ptr_Function_float Function
          %v = OpVariable %_ptr_Function_float Function
          %w = OpVariable %_ptr_Function_float Function
         %15 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %16 = OpLoad %float %15
               OpStore %u %16
         %19 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %20 = OpLoad %float %19
               OpStore %v %20
         %23 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
         %24 = OpLoad %float %23
               OpStore %w %24
         %32 = OpLoad %float %u
         %39 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %40 = OpLoad %v4float %39
         %41 = OpVectorTimesScalar %v4float %40 %32
         %42 = OpLoad %float %v
         %44 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %45 = OpLoad %v4float %44
         %46 = OpVectorTimesScalar %v4float %45 %42
         %47 = OpFAdd %v4float %41 %46
         %48 = OpLoad %float %w
         %50 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %51 = OpLoad %v4float %50
         %52 = OpVectorTimesScalar %v4float %51 %48
         %53 = OpFAdd %v4float %47 %52
         %55 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %55 %53
         %58 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %58 %float_1
               OpStore %gl_Layer %int_0
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Every regular case requires the core tessellation-shader feature. It also requires `VK_EXT_shader_viewport_index_layer` when the API version is below 1.2; on Vulkan 1.2 and later, the `shaderOutputLayer` feature must be enabled. Pipeline construction requirements and the DGC stage bindings are checked before execution.
- Each regular case creates a two-layer `VK_FORMAT_R8G8B8A8_UNORM` color image with a transfer source and a host-visible readback buffer. The framebuffer extent is `32 x 32 x 2`, and the clear color is black.
- The host builds two pipelines with patch-list topology. The generated command layout contains an execution-set token followed by a draw token. `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` is set for `_preprocess` cases. The stream selects one pipeline or four shader objects per layer and supplies a three-vertex, one-instance indirect draw.
- The command buffer begins the render pass, binds the initial pipeline state, executes the generated commands, ends the render pass, copies both layers to the readback buffer, and waits for completion. Preprocess cases record `vkCmdPreprocessGeneratedCommandsEXT` in a separate command buffer and use `preprocessToExecuteBarrierExt` before execution.
- The host selects the reference image for each layer from the exact `(primitive type, spacing, patch size)` key. It compares every pixel with a zero threshold. Any mismatch sets `fail` and returns `Unexpected color in result buffer; check log for details`; matching layers return `pass("Pass")`.
- Dynamic-state cases require `extendedDynamicState2PatchControlPoints`. They render a result image through DGC and a reference image through ordinary pipeline binds, push constants, and draws. The host compares the two images with a zero threshold. A mismatch returns `Unexpected color in result buffer; check log for details`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `Regular tessellation-state pairs` | A selected primitive type, spacing mode, patch size, layer assignment, generated pipeline, or reference image did not produce the expected per-layer point pattern. |
| `Dynamic patch-control-points` | `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` did not use the value recorded by `vkCmdSetPatchControlPointsEXT`, or the generated draw path differed from the ordinary reference path. |
| Both groups | Shared pipeline construction, DGC layout, command execution, synchronization, image copyback, or comparison setup failed. |

### Cause Analysis

#### Regular tessellation state not preserved

**Possible failure symptoms:** One or both layer comparisons report unexpected color, and the log identifies `Layer0` or `Layer1`. The mismatch means that the rendered point pattern differs from the reference selected for that layer's primitive, spacing, and patch-size key.

**Possible implementation causes:** The tessellation stages may receive the wrong patch size, primitive mode, spacing mode, or execution-set entry. The result also depends on correct layer output from `gl_Layer`. The comparison cannot locate the failing stage, so source-level investigation is needed.

#### Dynamic patch-control-points state not applied

**Possible failure symptoms:** The DGC result image differs from the ordinary reference image. The generated tessellation shaders can move points by the `10.0` offset when `gl_PatchVerticesIn` is not `4`, which makes a stale patch count visible in the quadrant comparison.

**Possible implementation causes:** The implementation may ignore `vkCmdSetPatchControlPointsEXT`, retain the static value `3`, or fail to carry the dynamic state into a generated draw. The same symptom can result from incorrect execution-set selection or push-constant data, so source-level investigation is needed.

#### Generated command execution or copyback failure

**Possible failure symptoms:** Both layers or all dynamic quadrants differ, regardless of the selected tessellation parameters. The test returns the common unexpected-color failure after the readback comparison.

**Possible implementation causes:** The generated command layout, execution-set token, preprocess-to-execute synchronization, draw token, render-pass execution, image-to-buffer copy, or host invalidation may not match the command sequence. The test does not isolate these mechanisms from one another.

## Case Pruning

### Requirement-based pruning

- All regular cases require `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` and the layer-output support described in the support check. Unsupported devices raise a support error rather than failing an image comparison. See [regular support checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L214-L237).
- Regular cases require the relevant pipeline-construction and DGC support for vertex, tessellation-control, tessellation-evaluation, and fragment stages. Dynamic cases require `extendedDynamicState2PatchControlPoints` and do not register shader-object variants. See [dynamic support check](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L776-L789).
- The code asserts patch sizes of `3` or `4`; other patch sizes are not legal values for this registered matrix.

### Design-based pruning

- Regular registration skips identical layer tuples where primitive type, spacing, and patch size match. Those cases would render the same tessellation state on both layers and would not test state differentiation.
- The regular matrix keeps preprocessing as a boolean variant and uses one generated draw per layer. It does not vary draw count, framebuffer extent, color format, or tessellation levels.
- Dynamic registration skips shader objects because the source treats their relevant state as already dynamic. It varies only execution-set use and preprocessing, producing the exact `pcp`, `pcp_ies`, `pcp_preprocess`, and `pcp_ies_preprocess` leaves.
- The reference image map contains all 18 primitive, spacing, and patch-size combinations for one layer. The regular test uses two different keys per case rather than registering a separate test leaf for every key.

## Key Takeaways

- The regular cases put different tessellation state on two framebuffer layers and use exact reference images to detect state mix-ups.
- The main regular behavioral dimensions are output primitive, spacing mode, and patch size. Construction type and preprocessing test how the state travels through EXT generated execution.
- Dynamic patch-control-points cases set `4` dynamically while pipelines carry static value `3`. The shaders make the distinction visible through `gl_PatchVerticesIn` and an offset.
- A support rejection means the device lacks a required tessellation, layer-output, DGC, or dynamic-state capability. An unexpected-color failure means the executed result differed from the reference; it does not identify a particular implementation component.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Regular registration | [createDGCGraphicsTessStateTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1159-L1223) | Registers the exact construction-type, primitive, spacing, patch-size, and preprocess matrix. |
| Dynamic registration | [dynamic state registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1225-L1251) | Registers the exact dynamic patch-control-points leaves and their construction-type coverage. |
| Regular parameters and shader generation | [TessStateParams and initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L57-L400) | Defines spacing, primitive, patch-size, layer, and shader-stage behavior. |
| Regular execution and comparison | [TessStateInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L403-L662) | Builds the DGC draw stream, renders both layers, and compares reference images. |
| Dynamic parameters and shaders | [DynamicPCPInstance and initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L664-L867) | Defines the static-versus-dynamic patch-control-points check and colored result variants. |
| Dynamic execution and reference comparison | [DynamicPCPInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L869-L1155) | Renders the DGC result, renders the ordinary reference, and compares both images. |
| EXT support checks | [TessStateCase::checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L214-L237) and [DynamicPCPCase::checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L776-L789) | Applies feature, extension, construction, and DGC support gates. |
| Registration evidence | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L2468-L2667) | Lists the registered `dgc.ext.graphics.tess_state` paths, including regular matrix leaves. |
| Tessellation state specification | [tessellation.adoc](../../../../vulkan-docs/src/chapters/tessellation.adoc#L570-L592) | Defines pipeline patch-control-points state. |
| Dynamic patch-control-points specification | [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6147) and [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L2585-L2614) | Defines when `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` ignores static state and how `vkCmdSetPatchControlPointsEXT` applies. |
