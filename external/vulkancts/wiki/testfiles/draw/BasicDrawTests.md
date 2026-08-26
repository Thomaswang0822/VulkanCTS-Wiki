## Overview

**Core question:** Do direct, indexed, indirect, and indexed-indirect draw commands produce the same image as the software reference across Vulkan primitive topologies and command-recording modes?

- This page covers `vktBasicDrawTests.cpp`, which registers `draw.renderpass.basic_draw`.
- The implementation exercises `vkCmdDraw`, `vkCmdDrawIndexed`, `vkCmdDrawIndirect`, and `vkCmdDrawIndexedIndirect` with generated vertex/index data, randomized offset fields, and one-instance draws.
- The same test logic can run with render-pass or dynamic-rendering setup and with secondary or nested secondary command buffers, subject to the selected `SharedGroupParams`.
- The test renders to a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color target, reads the image back, and compares it with an `rr::Renderer` software-rendered reference.

## Background Knowledge

- Vulkan primitive topology determines how the vertex stream becomes points, lines, triangles, or adjacency primitives. List, strip, fan, and adjacency topologies consume different numbers of vertices per primitive.
- Direct draw commands receive their draw parameters as command arguments. Indexed commands additionally fetch indices and apply `firstIndex` and `vertexOffset`. Indirect commands read one or more `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand` structures from a buffer.
- A render pass supplies the legacy render-pass/framebuffer scope for a graphics draw. Dynamic rendering supplies the attachment scope through `vkCmdBeginRendering` and `vkCmdEndRendering`; both paths still execute the same graphics pipeline and draw operation.
- A secondary command buffer records graphics commands for execution by a primary command buffer. Nested secondary command buffers add another command-buffer level and require the corresponding nested-command-buffer features.

## Registration Hierarchy

```text
draw.renderpass.basic_draw
├── draw
├── draw_indexed
├── draw_indirect
├── draw_indexed_indirect
└── misc
```

The four draw families are implemented by the parameterized cases in `vktBasicDrawTests.cpp`. `misc` is present in non-VulkanSC builds; its children are created only for the non-dynamic-rendering path.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw command family | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect` | Selects the command API and the parameter structure used to build and execute the case. | [`createDrawTests`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1853-L1880) |
| Primitive topology | `point_list`, `line_list`, `line_strip`, `triangle_list`, `triangle_strip`, `triangle_fan`, `line_list_with_adjacency`, `line_strip_with_adjacency`, `triangle_list_with_adjacency`, `triangle_strip_with_adjacency` | Selects primitive assembly and the vertex-count formula. `patch_list` is excluded by the registration loop. | [`createDrawTests`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1862-L1869), [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1743-L1780) |
| Primitive count | `1`, `3`, `17`, `45` | Controls the number of logical primitives. Dynamic-rendering cases retain only `1` and `45`. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1732-L1741) |
| Direct/indexed offsets | Randomized `firstVertex`, `firstIndex`, and `vertexOffset` | Exercises nonzero source offsets while the reference uses the generated logical vertex/index data. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1787-L1806) |
| Indirect command shape | `_single_command`, `_multi_command`, `_multi_command_multi_draw` | Distinguishes one indirect structure, two structures issued separately, and two structures consumed by one multi-draw call. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1811-L1844) |
| Indexed direct command count | Base case and `_multi_command` for list topologies with more than one primitive | Splits a simple list into multiple `vkCmdDrawIndexed` calls and checks the accumulated image. | [`isSimpleListTopology`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L174-L187), [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1802-L1806) |
| Rendering and command-buffer mode | Render pass, dynamic rendering, secondary command buffer, nested secondary command buffer | Changes command recording and attachment setup without changing the core draw-family comparison. | [`DrawParamsBase`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L119-L145), [`DrawTestInstanceBase`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L365-L414) |

## Behavior Parameters

The primary behavioral axis is the registered draw command family. Each family uses the same generated geometry and reference-image contract, but reaches the rasterizer through a different Vulkan command and parameter transport.

### `draw`: Direct non-indexed drawing

`vkCmdDraw` receives `vertexCount`, `instanceCount`, `firstVertex`, and `firstInstance` directly. The generated vertex buffer includes the randomized `firstVertex` prefix, and the case uses one instance. [`DrawTestInstance<DrawParams>::draw`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L920-L925) records the command.

### `draw_indexed`: Direct indexed drawing

`vkCmdDrawIndexed` reads generated `uint32_t` indices and applies randomized `firstIndex` and `vertexOffset`. For `point_list`, `line_list`, and `triangle_list` with more than one primitive, the `_multi_command` case divides the work into multiple indexed draw commands; other topologies use the single command form. [`DrawTestInstance<DrawIndexedParams>::iterate`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1047-L1233) contains the indexed execution and reference comparison.

### `draw_indirect`: Non-indexed indirect drawing

The test writes `VkDrawIndirectCommand` records to an indirect buffer. `_single_command` contains one command with `firstVertex = 0`; `_multi_command` adds a second command with a randomized `firstVertex` and submits the commands separately; `_multi_command_multi_draw` submits the two records through one `vkCmdDrawIndirect` call with `drawCount > 1`. [`DrawTestInstance<DrawIndirectParams>::iterate`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1295-L1433) validates the result.

### `draw_indexed_indirect`: Indexed indirect drawing

The indexed indirect family writes `VkDrawIndexedIndirectCommand` records, including randomized `firstIndex` and `vertexOffset` in the second command. It uses the same single, separate-multi-command, and one-call multi-draw variants as `draw_indirect`. [`DrawTestInstance<DrawIndexedIndirectParams>::iterate`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1515-L1702) performs execution and image comparison.

### `misc`: Non-matrix cases

In non-VulkanSC builds and without dynamic rendering, `maintenance5` checks indexed indirect drawing with `VkBufferUsageFlags2CreateInfoKHR` and `VK_BUFFER_USAGE_2_*_BIT_KHR` flags while the legacy usage field is deliberately set to `0xBAD00000`; it also creates a pipeline library through the maintenance5 path. `flat_b_sat_error` loads the Amber case `draw/misc/flat_b_sat_error.amber`. [`createDrawTests`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1882-L1899)

## Shader Analysis

The Vulkan cases use the following generated GLSL pair. The shaders only pass position and color through the graphics pipeline; draw-command behavior is therefore observed in primitive assembly and rasterization, not in shader-side branching.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.basic_draw.draw.line_list.1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass` | Uses the ordinary render-pass/framebuffer path rather than dynamic rendering. |
| `draw` | Records a direct, non-indexed `vkCmdDraw` command. |
| `line_list` | Assembles each pair of vertices as an independent line. |
| `1` | Draws one logical primitive. |
| `GLSL` | Both shown stages are generated as GLSL sources. |
| `vert` and `frag` | The program collection contains one vertex shader and one fragment shader. |
| `#version 430` | Both generated shader sources declare GLSL version 4.30. |

#### Purpose

The minimal pass-through shaders keep the expected image determined by the host-generated vertices, colors, topology, and draw parameters. That makes a mismatch attributable to command execution, primitive assembly, buffer addressing, rendering mode, or image handling rather than application shader logic.

#### Structural Design

| Stage | Inputs | Outputs | Role |
|-------|--------|---------|------|
| Vertex | `in_position`, `in_color` | `gl_Position`, `gl_PointSize`, `out_color` | Preserve generated vertex attributes and set point size to 1.0. |
| Fragment | `in_color` | `out_color` | Store the interpolated color without a test-specific calculation. |

#### Shader Code

##### Vertex Shader

```glsl
#version 430
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 0) out vec4 out_color;
out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
};
void main() {
    gl_PointSize = 1.0;
    gl_Position  = in_position;
    out_color    = in_color;
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

- The software reference uses matching pass-through vertex and fragment behavior through `rr::Program`.
- The vertex shader declares `gl_PerVertex` explicitly so it writes position and point size for every topology.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw command family | None. Direct, indexed, indirect, and indexed-indirect cases use the same vertex and fragment shader bodies; the host changes command recording and parameter transport. | [`createDrawTests`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1853-L1880) |
| Primitive topology | None in shader source. The selected topology changes primitive assembly and the host-generated vertex count. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1743-L1780) |
| Primitive count | None. The count changes generated geometry and draw parameters without changing either stage. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1732-L1741) |
| Direct and indexed offsets | None. Randomized `firstVertex`, `firstIndex`, and `vertexOffset` values affect host-side buffer addressing only. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1787-L1806) |
| Indirect command shape | None. Single-command, separate multi-command, and one-call multi-draw variants retain the same shader pair. | [`populateSubGroup`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1811-L1844) |
| Rendering and command-buffer mode | None. Render-pass, dynamic-rendering, secondary, and nested-secondary variants change setup and recording rather than generated GLSL. | [`DrawTestInstanceBase`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L365-L414) |
| Adjacency topology | The shader bodies remain unchanged, but selecting an adjacency topology requires the geometry-shader device feature because of the pipeline topology. | [`DrawTestCase<T>::checkSupport`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L816-L824) |

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
; Bound: 25
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_color %in_color
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %in_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
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
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %15 %float_1
         %19 = OpLoad %v4float %in_position
         %21 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %21 %19
         %24 = OpLoad %v4float %in_color
               OpStore %out_color %24
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

- Each instance generates deterministic random data. `populateSubGroup` seeds its random generator with `SEED ^ deStringHash(testGroup->getName())`; draw-specific generation also incorporates command parameters where applicable.
- The instance creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color image, view, graphics pipeline, vertex buffer, command pool, and primary command buffer. It creates a render pass/framebuffer unless dynamic rendering is selected.
- The selected mode records the draw in a primary command buffer, a secondary command buffer, or a nested secondary command buffer. The command-buffer mode and dynamic-rendering flags come from the shared draw-group parameters.
- The implementation copies the rendered color target back for host inspection. It separately renders the generated vertex/color data with `rr::Renderer`, using the Vulkan topology mapping, and compares the two pixel buffers.
- `point_list` uses `tcu::intThresholdPositionDeviationCompare` with color threshold 4 and position tolerance `(1, 1, 0)`. Other topologies use `tcu::fuzzyCompare` with threshold `0.053f`. A failed comparison returns a failing CTS status.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Incorrect direct non-indexed parameter handling, vertex fetch, primitive assembly, rendering mode, or image copyback. |
| `draw_indexed` | Incorrect index fetch or `firstIndex`/`vertexOffset` handling, repeated-command accumulation, primitive assembly, rendering mode, or image copyback. |
| `draw_indirect` | Incorrect indirect-buffer address/record handling, `drawCount` execution, `firstVertex` handling, primitive assembly, rendering mode, or image copyback. |
| `draw_indexed_indirect` | Incorrect indexed indirect record handling, index/vertex offsets, `drawCount` execution, primitive assembly, rendering mode, or image copyback. |
| `misc` | Incorrect maintenance5 buffer/pipeline flag handling or the behavior exercised by the Amber case. |

### Cause Analysis

#### Draw command parameter and buffer interpretation

**Possible failure symptoms:** The result image differs where a nonzero first or base parameter selects a different vertex or index range, or where the second indirect record should add another primitive batch.

**Possible implementation causes:** The implementation may read the wrong indirect structure, apply `vertexOffset` with the wrong signedness, ignore `firstIndex` or `firstVertex`, use the wrong `drawCount`, or advance an indirect stride incorrectly. The source varies these fields specifically in `populateSubGroup`, while Vulkan defines the command structures and draw parameters in the drawing chapter.

#### Primitive assembly and rasterization

**Possible failure symptoms:** Point, line, triangle, fan, strip, or adjacency coverage differs from the software reference even when the fetched attributes are correct.

**Possible implementation causes:** The driver or hardware may assemble the selected topology incorrectly, mishandle adjacency input requirements, or produce different rasterized coverage. The point comparison allows a small position deviation; the other topologies use the fuzzy image threshold shown in `imageCompare`.

#### Rendering and command-buffer mode

**Possible failure symptoms:** A case passes in the ordinary render-pass path but fails with dynamic rendering or secondary/nested command-buffer recording.

**Possible implementation causes:** The implementation may mishandle attachment scope, command-buffer inheritance/continuation state, nested rendering state, or synchronization between rendering and readback. The test's support gate rejects unavailable dynamic-rendering or nested-command-buffer functionality before execution; a failure after that gate indicates a result mismatch in a supported path.

#### Reference generation or result readback

**Possible failure symptoms:** The Vulkan image differs from the reference across broad regions, including cases whose draw parameters should select equivalent data.

**Possible implementation causes:** The issue may occur in vertex-buffer initialization, image layout transitions, color attachment operations, transfer/readback, or the comparison path. The software renderer maps the same Vulkan topology and uses the generated position/color arrays, so a broad mismatch is not evidence of a shader algorithm failure.

## Case Pruning

### Requirement-based pruning

- Adjacency topologies require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.
- Multi-draw indirect cases with more than one command require `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT`.
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`.
- Nested secondary-command-buffer cases require `VK_EXT_nested_command_buffer`, `nestedCommandBuffer`, and `nestedCommandBufferRendering`.
- On an implementation exposing `VK_KHR_portability_subset`, `triangle_fan` requires the `triangleFans` portability feature.
- `maintenance5` requires `VK_KHR_maintenance5` and is not registered in VulkanSC builds.

### Design-based pruning

- The registration loop stops before `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`, so patch-list cases are outside this family.
- Dynamic-rendering variants keep primitive counts `1` and `45` instead of duplicating the intermediate counts.
- Secondary-command-buffer variants keep only even-indexed topology values.
- Nested secondary-command-buffer variants keep only `draw`, reducing the cross-product of command families and recording modes.
- Indexed `_multi_command` cases are limited to point, line, and triangle list topologies, where the source can split the primitive sequence into independent commands.
- The `misc` cases are disabled for dynamic rendering and are absent from VulkanSC builds.

## Key Takeaways

- The four primary families hold shader behavior constant and vary how Vulkan receives and executes draw parameters.
- The generated topology-specific vertex counts include the correct list, strip, fan, and adjacency formulas; nonzero offsets then test addressing beyond the simplest zero-based draw.
- Indirect multi-draw cases distinguish multiple records from multiple API calls, so both buffer interpretation and `drawCount` execution matter.
- Result checking compares the complete rendered image with a software reference, with a topology-specific point tolerance and a fuzzy threshold for other primitives. See `## Failure Meaning` for failure interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createBasicDrawTests` / `createDrawTests` | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1853-L1905) | Registers the page root, four command families, topology groups, and `misc`. |
| `populateSubGroup` | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1725-L1851) | Generates primitive counts, offsets, indirect variants, and concrete case names. |
| `DrawParamsBase` and parameter structs | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L119-L289) | Defines the data carried by direct, indexed, and indirect cases. |
| `DrawTestInstanceBase::initialize` | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L428-L706) | Creates the target, pipeline, render-pass/dynamic-rendering, and command-buffer infrastructure. |
| `imageCompare` | [`vktBasicDrawTests.cpp`](../../../modules/vulkan/draw/vktBasicDrawTests.cpp#L349-L363) | Defines the point-list and non-point image comparison rules. |
| Vulkan drawing commands and primitive assembly | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) | Specification semantics for direct, indexed, indirect, and multi-draw parameters. |
| Vertex post-processing and primitive assembly | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc) | Specification context for topology-dependent assembly and vertex processing. |
| Render-pass and dynamic-rendering setup | [`renderpass.adoc`](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Specification context for the attachment/rendering scope used by the cases. |
| Mustpass registration | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L17477-L17807) | Evidence for the `draw.renderpass.basic_draw` hierarchy and generated leaves. |
