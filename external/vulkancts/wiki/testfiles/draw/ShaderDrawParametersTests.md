## Overview

**Core question:** Do Vulkan draw commands expose the correct base vertex, base instance, and draw index to the vertex shader?

- This page covers the implementation in [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L25-L62), registered below `draw.renderpass.shader_draw_parameters`.
- The test keeps the graphics pipeline and `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` fixed while changing direct, indexed, indirect, instanced, first-instance, and multi-draw command parameters.
- The vertex shader uses `gl_BaseVertexARB`, `gl_BaseInstanceARB`, and `gl_DrawIDARB` to select vertex data, instance offsets, and per-draw colors. The resulting color image is compared with a host-built reference image.

## Background Knowledge

- `gl_BaseVertexARB` is the signed vertex offset applied by an indexed draw; it is zero for non-indexed draws. The shader can combine it with `gl_VertexIndex` to recover the index within the intended vertex data.
- `gl_BaseInstanceARB` is the first-instance value for a draw. Subtracting it from `gl_InstanceIndex` gives a zero-based instance slot even when the command starts at a nonzero instance.
- `gl_DrawIDARB` identifies the current draw within a multi-draw indirect command. It is distinct from the instance index and is meaningful here only because the command is indirect and has multiple records.
- A triangle strip consumes four consecutive vertices for the test's rectangle. The source deliberately places valid and junk records at different buffer indices so incorrect built-in values change the rendered image.

## Registration Hierarchy

```text
draw.renderpass.shader_draw_parameters
├── base_vertex
├── base_vertex_only
├── base_instance
├── base_instance_only
└── draw_index
```

The `base_vertex_only` and `base_instance_only` test families are registered only when secondary command-buffer recording is disabled. The source's dispatcher creates this test category through `ShaderDrawParametersTests` in [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L389-L465).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `base_vertex`, `base_vertex_only`, `base_instance`, `base_instance_only`, `draw_index` | Selects which shader draw parameter is checked and whether the check is isolated. | [`ShaderDrawParametersTests::init`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L467-L538) |
| Command form | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect` | Moves command parameters between direct API arguments, index data, and indirect records. | [`addDrawCase`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L357-L387) |
| Instancing | absent or `_instanced` | Uses one instance or `MAX_INSTANCE_COUNT` (3) instances and exercises base-instance addressing. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L281-L355) |
| First instance | absent or `_first_instance` | Uses nonzero `firstInstance` values in indirect commands. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L301-L328) |
| Multi-draw | absent or `draw_index`'s three-record indirect call | Uses `MAX_INDIRECT_DRAW_COUNT` (3) records so `gl_DrawIDARB` selects three draw positions and colors. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L301-L348) |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Keeps primitive assembly constant while shader-visible draw parameters vary. | [`FlagsTestSpec`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L45-L62) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family uses the same draw harness but asks a different question about shader-visible command state.

### `base_vertex`: combined base-vertex behavior

The four leaves `draw`, `draw_indexed`, `draw_indirect`, and `draw_indexed_indirect` compare non-indexed zero behavior with indexed `vertexOffset` behavior. The shader tests `(gl_VertexIndex - gl_BaseVertexARB)` against the reference index and colors only the intended vertices with the selected instance color.

### `base_vertex_only`: isolated base-vertex behavior

This family uses `VertexFetchShaderDrawParametersBaseVert.vert` and removes the instance-offset part of the combined shader. It retains the same four command forms and is restricted to primary command buffers to avoid repeating the same isolation check in secondary paths.

### `base_instance`: combined base-instance behavior

The six leaves are `draw`, `draw_indexed`, `draw_indirect`, `draw_indirect_first_instance`, `draw_indexed_indirect`, and `draw_indexed_indirect_first_instance`. The shader computes `gl_InstanceIndex - gl_BaseInstanceARB`; nonzero `firstInstance` values therefore test that both built-ins describe the same command invocation.

### `base_instance_only`: isolated base-instance behavior

This family uses `VertexFetchShaderDrawParametersBaseInst.vert` and keeps the expected vertex reference anchored at index 2. It covers the same six command forms as `base_instance`, again only for primary command buffers.

### `draw_index`: multi-draw draw-index behavior

The four leaves are `draw`, `draw_instanced`, `draw_indexed`, and `draw_indexed_instanced`. Every leaf is indirect and multi-draw: three records are submitted in one `vkCmdDrawIndirect` or `vkCmdDrawIndexedIndirect` call. `VertexFetchShaderDrawParametersDrawIndex.vert` uses `gl_DrawIDARB` to select a per-draw offset and color, while instance addressing remains independent.

## Shader Analysis

The vertex shader is central to this family: it turns `gl_BaseVertexARB`, `gl_BaseInstanceARB`, and `gl_DrawIDARB` into visible position and color changes. The representative combined case below exercises base vertex and base instance together; the draw-index-specific shader is covered in the variation summary because it keeps the same inputs and verdict but adds per-draw array indexing.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.shader_draw_parameters.base_instance.draw_indexed_indirect_first_instance
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass` | Uses the legacy render-pass recording path; rendering delivery does not change the shader. |
| `base_instance` | Selects the combined `VertexFetchShaderDrawParameters.vert` shader and three instances. |
| `draw_indexed_indirect` | Supplies `firstIndex` and `vertexOffset` through a `VkDrawIndexedIndirectCommand`, exercising `gl_BaseVertexARB` together with indexed fetch. |
| `first_instance` | Sets the indirect record's `firstInstance` to 2, while the shader subtracts `gl_BaseInstanceARB` from `gl_InstanceIndex` to recover a zero-based instance slot. |
| One indirect record | `gl_DrawIDARB` must be zero, so the combined shader's guard also checks the draw-index baseline. |

#### Purpose

The vertex shader verifies that an indexed indirect draw exposes mutually consistent base-vertex and base-instance values, and that its single indirect record reports draw index zero. It converts any mismatch into red output or an incorrect rectangle position, which the host image comparison detects.

#### Structural Design

| Shader phase | Operation | Observable effect |
|--------------|-----------|-------------------|
| Instance normalization | `gl_InstanceIndex - gl_BaseInstanceARB` selects `perInstance[]` and `colors[]`. | A wrong base instance moves or recolors an instance. |
| Vertex normalization | `gl_VertexIndex - gl_BaseVertexARB` is compared with `in_refVertexIndex`. | A wrong base vertex sends the affected vertex to the red failure path. |
| Draw-index baseline | The validity guard also requires `gl_DrawIDARB == 0`. | A wrong draw ID makes otherwise valid vertices red. |
| Fragment handoff | `out_color` is passed through unchanged by `VertexFetch.frag`. | The attachment directly exposes the vertex-stage verdict. |

#### Shader Code

```glsl
#version 450 core
#extension GL_ARB_shader_draw_parameters : require

layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 2) in int  in_refVertexIndex;

layout(location = 0) out vec4 out_color;

out gl_PerVertex {
    vec4 gl_Position;
};

void main() {
    vec2 perVertex         = vec2(in_position.x, in_position.y);
    vec2 perInstance[5]    = vec2[5](vec2(0.0, 0.0), vec2(-0.3, 0.0), vec2(0.0, 0.3), vec2(0.5, 0.5), vec2(0.75, -0.8));
    vec4 colors[4]         = vec4[4](vec4(1.0), vec4(0.0, 0.0, 1.0, 1.0), vec4(0.0, 1.0, 0.0, 1.0), vec4(0.0, 1.0, 1.0, 1.0));
    int  baseInstanceIndex = gl_InstanceIndex - gl_BaseInstanceARB;

    /// The normalized instance index controls both rectangle position and color.
    gl_Position = vec4(perVertex + perInstance[baseInstanceIndex], 0.0, 1.0);

    /// The expected vertex index and the single-record draw ID form the shader verdict.
    if ((gl_VertexIndex - gl_BaseVertexARB) == in_refVertexIndex && gl_DrawIDARB == 0)
        out_color = in_color * colors[baseInstanceIndex];
    else
        out_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The fixed fragment shader only copies `in_color` to the attachment. It does not vary across this family, so its SPIR-V is not needed to audit the built-ins under test.
- The host reference uses the same three instance offsets and colors in [`DrawTest::drawReferenceImage()`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `base_vertex_only` | Uses `VertexFetchShaderDrawParametersBaseVert.vert`, removes instance positioning and color selection, and isolates `gl_BaseVertexARB`. | [`ShaderDrawParametersTests::init()`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L484-L512) |
| `base_instance_only` | Uses `VertexFetchShaderDrawParametersBaseInst.vert`, fixes the expected vertex-index expression, and isolates `gl_BaseInstanceARB`. | [`ShaderDrawParametersTests::init()`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L513-L541) |
| `draw_index` | Uses `VertexFetchShaderDrawParametersDrawIndex.vert`; `gl_DrawIDARB` indexes per-draw offsets and colors for three indirect records. | [`ShaderDrawParametersTests::init()`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L542-L555) |
| Direct versus indirect and indexed versus non-indexed | The combined GLSL is unchanged; command parameters determine the built-in values observed by the shader. | [`DrawTest::draw()`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L374-L431) |

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
; Bound: 98
; Schema: 0
               OpCapability Shader
               OpCapability DrawParameters
               OpExtension "SPV_KHR_shader_draw_parameters"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %in_position %gl_InstanceIndex %gl_BaseInstanceARB %_ %gl_VertexIndex %gl_BaseVertexARB %in_refVertexIndex %gl_DrawIDARB %out_color %in_color
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_shader_draw_parameters"
               OpName %main "main"
               OpName %perVertex "perVertex"
               OpName %in_position "in_position"
               OpName %perInstance "perInstance"
               OpName %colors "colors"
               OpName %baseInstanceIndex "baseInstanceIndex"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %gl_BaseInstanceARB "gl_BaseInstanceARB"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_BaseVertexARB "gl_BaseVertexARB"
               OpName %in_refVertexIndex "in_refVertexIndex"
               OpName %gl_DrawIDARB "gl_DrawIDARB"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %in_position Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %gl_BaseInstanceARB BuiltIn BaseInstance
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_BaseVertexARB BuiltIn BaseVertex
               OpDecorate %in_refVertexIndex Location 2
               OpDecorate %gl_DrawIDARB BuiltIn DrawIndex
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
     %uint_5 = OpConstant %uint 5
%_arr_v2float_uint_5 = OpTypeArray %v2float %uint_5
%_ptr_Function__arr_v2float_uint_5 = OpTypePointer Function %_arr_v2float_uint_5
    %float_0 = OpConstant %float 0
         %27 = OpConstantComposite %v2float %float_0 %float_0
%float_n0_300000012 = OpConstant %float -0.300000012
         %29 = OpConstantComposite %v2float %float_n0_300000012 %float_0
%float_0_300000012 = OpConstant %float 0.300000012
         %31 = OpConstantComposite %v2float %float_0 %float_0_300000012
  %float_0_5 = OpConstant %float 0.5
         %33 = OpConstantComposite %v2float %float_0_5 %float_0_5
 %float_0_75 = OpConstant %float 0.75
%float_n0_800000012 = OpConstant %float -0.800000012
         %36 = OpConstantComposite %v2float %float_0_75 %float_n0_800000012
         %37 = OpConstantComposite %_arr_v2float_uint_5 %27 %29 %31 %33 %36
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_ptr_Function__arr_v4float_uint_4 = OpTypePointer Function %_arr_v4float_uint_4
    %float_1 = OpConstant %float 1
         %43 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
         %44 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
         %45 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %46 = OpConstantComposite %v4float %float_0 %float_1 %float_1 %float_1
         %47 = OpConstantComposite %_arr_v4float_uint_4 %43 %44 %45 %46
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
%gl_BaseInstanceARB = OpVariable %_ptr_Input_int Input
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %bool = OpTypeBool
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
%gl_BaseVertexARB = OpVariable %_ptr_Input_int Input
%in_refVertexIndex = OpVariable %_ptr_Input_int Input
%gl_DrawIDARB = OpVariable %_ptr_Input_int Input
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %97 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %perVertex = OpVariable %_ptr_Function_v2float Function
%perInstance = OpVariable %_ptr_Function__arr_v2float_uint_5 Function
     %colors = OpVariable %_ptr_Function__arr_v4float_uint_4 Function
%baseInstanceIndex = OpVariable %_ptr_Function_int Function
         %16 = OpAccessChain %_ptr_Input_float %in_position %uint_0
         %17 = OpLoad %float %16
         %19 = OpAccessChain %_ptr_Input_float %in_position %uint_1
         %20 = OpLoad %float %19
         %21 = OpCompositeConstruct %v2float %17 %20
               OpStore %perVertex %21
               OpStore %perInstance %37
               OpStore %colors %47
         %53 = OpLoad %int %gl_InstanceIndex
         %55 = OpLoad %int %gl_BaseInstanceARB
         %56 = OpISub %int %53 %55
               OpStore %baseInstanceIndex %56
         %61 = OpLoad %v2float %perVertex
         %62 = OpLoad %int %baseInstanceIndex
         %63 = OpAccessChain %_ptr_Function_v2float %perInstance %62
         %64 = OpLoad %v2float %63
         %65 = OpFAdd %v2float %61 %64
         %66 = OpCompositeExtract %float %65 0
         %67 = OpCompositeExtract %float %65 1
         %68 = OpCompositeConstruct %v4float %66 %67 %float_0 %float_1
         %70 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %70 %68
         %73 = OpLoad %int %gl_VertexIndex
         %75 = OpLoad %int %gl_BaseVertexARB
         %76 = OpISub %int %73 %75
         %78 = OpLoad %int %in_refVertexIndex
         %79 = OpIEqual %bool %76 %78
               OpSelectionMerge %81 None
               OpBranchConditional %79 %80 %81
         %80 = OpLabel
         %83 = OpLoad %int %gl_DrawIDARB
         %84 = OpIEqual %bool %83 %int_0
               OpBranch %81
         %81 = OpLabel
         %85 = OpPhi %bool %79 %5 %84 %80
               OpSelectionMerge %87 None
               OpBranchConditional %85 %86 %96
         %86 = OpLabel
         %90 = OpLoad %v4float %in_color
         %91 = OpLoad %int %baseInstanceIndex
         %93 = OpAccessChain %_ptr_Function_v4float %colors %91
         %94 = OpLoad %v4float %93
         %95 = OpFMul %v4float %90 %94
               OpStore %out_color %95
               OpBranch %87
         %96 = OpLabel
               OpStore %out_color %97
               OpBranch %87
         %87 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance creates vertex data containing four valid rectangle vertices separated by junk data. Indexed cases additionally create a `VK_INDEX_TYPE_UINT32` index buffer; indirect cases create a host-visible indirect buffer with room for three command records.
- Direct commands use `vkCmdDraw` or `vkCmdDrawIndexed`. Indirect commands populate `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand` with the selected offsets, instance count, and optional nonzero `firstInstance`, then issue one indirect call with `drawCount` equal to one or three.
- Depending on shared draw parameters, the command is recorded through a legacy render pass, dynamic rendering, or a secondary command buffer path. The test submits the primary command buffer and waits for completion.
- The color target is read back and compared with the 0.05 threshold in [`DrawTest::iterate`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L257-L279). A mismatch returns `Rendered image is incorrect`; otherwise the case passes with `OK`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `base_vertex` | Incorrect `gl_BaseVertexARB` exposure or indexed vertex-offset handling, vertex fetch, command recording, or image comparison path. |
| `base_vertex_only` | Incorrect isolated base-vertex built-in exposure, indexed/non-indexed command handling, or shader/pipeline setup. |
| `base_instance` | Incorrect `gl_BaseInstanceARB` exposure, instance-index calculation, `firstInstance` handling, or command execution. |
| `base_instance_only` | Incorrect isolated base-instance exposure or instanced command handling. |
| `draw_index` | Incorrect `gl_DrawIDARB` exposure or multi-draw indirect record selection, including interaction with indexed or instanced execution. |

### Cause Analysis

#### Shader-visible base vertex

**Possible failure symptoms:** The intended rectangle is missing or the attachment contains red output when an indexed command uses a nonzero vertex offset.

**Possible implementation causes:** The implementation may expose the wrong base vertex to the vertex shader or apply `vertexOffset` incorrectly when fetching indexed vertices. The exact fault location requires source-level investigation; the image alone does not distinguish shader lowering, command interpretation, and vertex fetch.

#### Shader-visible base instance and first instance

**Possible failure symptoms:** Instanced rectangles appear at the wrong offsets or with the wrong colors, especially in `_first_instance` leaves.

**Possible implementation causes:** The implementation may report an incorrect `gl_BaseInstanceARB`, mishandle `firstInstance` in an indirect record, or compute instance indexing inconsistently. The feature gate requires `drawIndirectFirstInstance` for the nonzero indirect cases.

#### Shader-visible draw index and multi-draw records

**Possible failure symptoms:** The three rectangles overlap, use the wrong colors, or appear at the wrong per-draw offsets in `draw_index`.

**Possible implementation causes:** The implementation may fail to advance indirect records correctly, report the wrong draw index, or mishandle the interaction between multi-draw execution and indexed/instanced commands. The test requires multi-draw indirect support before execution.

#### Shared rendering and image validation

**Possible failure symptoms:** Broad image differences occur across otherwise unrelated families or recording modes.

**Possible implementation causes:** The mismatch may be in pipeline setup, attachment rendering, command-buffer inheritance, image readback, or the host reference comparison. Investigation is needed before attributing such a failure to a shader built-in.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_shader_draw_parameters`; on Vulkan 1.1 and later the optional `shaderDrawParameters` feature must be enabled.
- Dynamic-rendering variants require `VK_KHR_dynamic_rendering`.
- `TEST_FLAG_MULTIDRAW` requires `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT`.
- `TEST_FLAG_FIRST_INSTANCE` requires `DEVICE_CORE_FEATURE_DRAW_INDIRECT_FIRST_INSTANCE`.
- The isolated families are not registered when `useSecondaryCmdBuffer` is enabled; this is intentional duplication control rather than a device-support failure.

### Design-based pruning

- `base_vertex` and `base_vertex_only` use four command forms; `base_instance` and `base_instance_only` add the two `_first_instance` forms because nonzero first-instance behavior is their additional axis.
- `draw_index` always uses indirect multi-draw and therefore has only four combinations of indexed and instanced execution.
- The topology is fixed to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`; topology variation is outside this test family's purpose.
- Buffer padding and junk records are deliberate: they prevent a zero-based or accidentally contiguous fetch from passing by coincidence.

## Key Takeaways

- The test validates shader-visible command state through rendered geometry and color rather than through a separate scalar result buffer.
- Indexed and non-indexed paths distinguish base-vertex behavior; instanced and `_first_instance` paths distinguish base-instance behavior; three-record indirect calls distinguish draw-index behavior.
- The same implementation-bearing test family covers direct, indexed, indirect, and indexed-indirect forms, while isolated families reduce ambiguity when diagnosing a failure.
- A failing image comparison identifies a mismatch in the complete draw path. See `## Failure Meaning` before assigning the failure to a particular built-in.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `ShaderDrawParametersTests::init` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L467-L538) | Registers the exact test families, shader files, flags, and leaves. |
| `addDrawCase` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L357-L387) | Builds exact leaf identifiers from command flags. |
| `DrawTest::draw` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L281-L355) | Writes direct and indirect command parameters and issues draw calls. |
| `drawReferenceImage` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255) | Defines expected instance/draw offsets and colors. |
| `DrawTest::iterate` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L257-L279) | Submits, reads back, and compares the rendered image. |
| Combined shader | [`VertexFetchShaderDrawParameters.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParameters.vert) | Exercises all three shader draw-parameter built-ins. |
| Isolated shaders | [`VertexFetchShaderDrawParametersBaseVert.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersBaseVert.vert), [`VertexFetchShaderDrawParametersBaseInst.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersBaseInst.vert) | Separate base-vertex and base-instance checks. |
| Draw-index shader | [`VertexFetchShaderDrawParametersDrawIndex.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersDrawIndex.vert) | Uses draw ID to select per-draw offsets and colors. |
| Mustpass registration | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28999-L29022) | Confirms the `draw.renderpass.shader_draw_parameters` hierarchy and leaves. |
| Vulkan feature requirements | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L1795-L1805) | Defines the relevant shader-draw-parameter and draw-command feature context. |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L1540-L1580) | Defines direct and indirect draw parameter behavior. |
