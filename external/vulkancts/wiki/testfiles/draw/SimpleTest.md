## Overview

**Core question:** Does a basic non-indexed graphics draw produce the expected rectangle for both triangle topologies, including a non-zero `firstInstance` in instanced draws?

- This page covers the four direct test case leaves registered by `SimpleDrawTests` in `vktDrawSimpleTest.cpp`.
- The cases bind a vertex buffer, render into a 256×256 `VK_FORMAT_R8G8B8A8_UNORM` color target, and compare the result with a host-built blue-on-black reference image.
- The same leaves are registered under the render-pass path and the three non-nested dynamic-rendering command-buffer modes. VulkanSC contains only the render-pass path in the mustpass inventory.
- The implementation uses `VertexFetch.vert`/`VertexFetch.frag` for non-instanced cases and `VertexFetchInstancedFirstInstance.vert` with the same fragment shader for instanced cases ([case registration](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L412-L444)).

## Background Knowledge

- Vulkan primitive topology determines how fetched vertices are assembled into primitives. A triangle list consumes groups of three vertices; a triangle strip reuses adjacent vertices to form subsequent triangles.
- `firstVertex` and `firstInstance` are draw parameters visible to the vertex-processing stage. These tests deliberately use non-zero offsets so that fetching and instance-ID handling are exercised rather than only the default-zero path.
- A render pass instance may be recorded with a traditional `VkRenderPass`, or with dynamic rendering when the required feature is enabled. In both forms, draw commands are recorded inside the active render pass instance ([render-pass specification](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7-L10)).

## Registration Hierarchy

The category dispatcher creates `simple_draw` under `draw.renderpass` and, when VulkanSC is not being built, under the three non-nested dynamic-rendering modes. `createChildren` does not add it to either nested-secondary mode because those modes set `nestedSecondaryCmdBuffer` and skip the simple-draw registration ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100), [dynamic-rendering groups](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L198)). Each `simple_draw` family has the same four direct leaves:

```text
draw.renderpass.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.primary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.partial_secondary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.complete_secondary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip
```

The nested dynamic-rendering roots are intentionally absent from this tree: their `nestedSecondaryCmdBuffer` setting prevents `createChildren` from adding `SimpleDrawTests`. The four leaves are created directly by `SimpleDrawTests::init` ([group construction](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L401-L445)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Selects the primitive assembly path and vertex count | [`SimpleDraw::draw`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249) |
| Draw mode | non-instanced, instanced | Selects the ordinary or `firstInstance`-sensitive execution path | [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L273-L345) |
| Vertex range | `vertexCount=6` (list), `vertexCount=4` (strip); `firstVertex=2` | Skips two leading degenerate entries and exercises non-zero vertex offset | [`SimpleDraw::draw`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249) |
| Instance range | `instanceCount=1`, `firstInstance=0`; or `instanceCount=4`, `firstInstance=2` | Adds four instances and a non-zero first-instance offset in the instanced leaves | [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L293-L325) |
| Rendering command path | render pass; dynamic rendering with primary, partial secondary, or complete secondary command buffers | Reuses the draw behavior across supported recording arrangements | [`SimpleDraw::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L131-L193), [dispatcher parameters](../../../modules/vulkan/draw/vktDrawTests.cpp#L157-L191) |

The source creates four leaves, and the mustpass inventory expands them to 4 render-pass leaves plus 12 dynamic-rendering leaves in `vk-default` (16 total). `vksc-default` contains the 4 render-pass leaves only. The dynamic-rendering branches are compiled out for VulkanSC ([conditional registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L199)).

## Behavior Parameters

The primary behavioral axis is the test case leaf: topology and instancing jointly determine the draw command and expected rectangle.

### `simple_draw_triangle_list` : Six-vertex list draw

The case uses six vertices starting at `firstVertex=2`, forming two triangles that cover the square from −0.3 to 0.3 in both axes ([vertex data](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L71-L88)).

### `simple_draw_triangle_strip` : Four-vertex strip draw

The case uses four vertices starting at `firstVertex=2`; the strip assembles the same rectangular coverage with fewer submitted vertices ([vertex data](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L89-L100)).

### `simple_draw_instanced_triangle_list` : Four-instance list draw

This uses the list topology with `vkCmdDraw(..., 6, 4, 2, 2)`. The non-zero `firstInstance=2` is part of the behavior under test ([draw command](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249), [instanced call](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L293-L295)).

### `simple_draw_instanced_triangle_strip` : Four-instance strip draw

This uses the strip topology with `vkCmdDraw(..., 4, 4, 2, 2)`, combining strip assembly with four instances and `firstInstance=2` ([draw command](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249), [instanced call](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L321-L325)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.simple_draw.simple_draw_instanced_triangle_list
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `simple_draw_instanced_triangle_list` | Selects the instanced vertex shader and triangle-list assembly, using six fetched vertices for each instance. |
| `firstVertex=2` | Makes the effective vertex indices start at 2, which the shader checks against the reference index stored in each vertex record. |
| `instanceCount=4`, `firstInstance=2` | Makes `gl_InstanceIndex` select offsets 2 through 5 from the shader-local array, producing four translated copies of the rectangle. |
| `renderpass` | Uses the legacy render-pass recording path; the dynamic-rendering command-buffer variants use the same shaders and draw arguments. |

#### Purpose

The vertex shader checks non-zero `firstVertex` handling by comparing `gl_VertexIndex` with vertex-buffer reference data, and checks non-zero `firstInstance` handling by indexing four instance offsets with `gl_InstanceIndex`. Correct indices produce four blue rectangles whose union matches the host reference; an incorrect vertex index changes the affected primitive to red.

#### Structural Design

| Shader element | Role in the selected case |
|----------------|---------------------------|
| Vertex locations 0-2 | Fetch position, blue color, and the expected effective vertex index from one interleaved vertex record. |
| `perInstance[gl_InstanceIndex]` | Uses effective instance indices 2-5 to translate the base rectangle to four adjacent positions. |
| Vertex-index comparison | Forwards blue only when `gl_VertexIndex` equals `in_refVertexIndex`; otherwise emits diagnostic red. |
| Fragment location 0 | Passes the interpolated diagnostic color unchanged to the color attachment. |

#### Shader Code

##### Vertex Shader

```glsl
#version 430

/// Locations 0-2 consume one interleaved, per-vertex record from binding 0: a vec4 position, a vec4
/// color, and an R32_SINT reference index at byte offsets 0, 16, and 32 respectively.
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 2) in int in_refVertexIndex;

/// Location 0 carries the selected blue-or-red diagnostic color to the fixed fragment shader.
layout(location = 0) out vec4 out_color;

/// The built-in output block exports the instance-translated clip-space position to rasterization.
out gl_PerVertex {
    vec4 gl_Position;
};

void main() {
	/// Keep the fetched x/y coordinates and select one of six shader-local offsets by the effective
	/// instance index. With firstInstance=2 and instanceCount=4, only entries 2 through 5 are used.
	vec2 perVertex = vec2(in_position.x, in_position.y);
	vec2 perInstance[6]	= vec2[6] (vec2(0.7, -0.7), vec2(-0.75, 0.8), vec2(0.0, 0.0), vec2(0.3, 0.0), vec2(0.0, -0.3),vec2(0.3, -0.3) );

	gl_Position = vec4(perVertex + perInstance[gl_InstanceIndex], 0.0, 1.0);

	/// A correct non-zero firstVertex still makes gl_VertexIndex match the stored values 2 through 7;
	/// any mismatch turns the primitive red instead of forwarding the expected blue.
	if (gl_VertexIndex == in_refVertexIndex)
		out_color = in_color;
	else
		out_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

##### Fragment Shader

```glsl
#version 430
/// Location 0 receives the interpolated blue-or-red diagnostic color from the vertex shader.
layout(location = 0) in vec4 in_color;
/// Location 0 writes that color directly to the R8G8B8A8_UNORM color attachment.
layout(location = 0) out vec4 out_color;
void main()
{
  out_color = in_color;
}
```

#### Additional Info

- The fragment shader stays fixed across every case on this page; it matters because it preserves the vertex shader's blue success color or red vertex-index diagnostic in the image checked by the host.
- The selected `vkCmdDraw` call is `vkCmdDraw(..., 6, 4, 2, 2)`. The four offsets actually selected by indices 2-5 make the base `[-0.3, 0.3]` square cover the union `x=[-0.3, 0.6]`, `y=[-0.6, 0.3]`, matching `ReferenceImageInstancedCoordinates`. The added space between `vec2[6]` and its constructor parentheses only prevents the wiki link checker from parsing the GLSL as a Markdown link; it does not change the shader.
- Both shader stages are loaded unchanged from CTS data files by `InstanceFactory::initPrograms`; no explicit `ShaderBuildOptions` are appended, so the source collection's baseline SPIR-V 1.0 target applies.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw mode | Non-instanced leaves replace this vertex shader with `VertexFetch.vert`, which omits the offset array and `gl_InstanceIndex` access; the vertex-index diagnostic remains. | [shader selection](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L414-L434), [non-instanced shader](../../../data/vulkan/draw/VertexFetch.vert#L1-L19) |
| Primitive topology | Triangle-strip leaves use four vertices instead of six, but do not change either shader. | [`SimpleDraw::draw`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L250) |
| Rendering command path | Render-pass and dynamic-rendering variants compile and execute the same selected shader files; only command-buffer/rendering setup changes. | [case registration](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L412-L445), [pipeline loading](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L155-L170) |

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
; Bound: 71
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %in_position %_ %gl_InstanceIndex %gl_VertexIndex %in_refVertexIndex %out_color %in_color
               OpSource GLSL 430
               OpName %main "main"
               OpName %perVertex "perVertex"
               OpName %in_position "in_position"
               OpName %perInstance "perInstance"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %in_refVertexIndex "in_refVertexIndex"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %in_position Location 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %in_refVertexIndex Location 2
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
     %uint_6 = OpConstant %uint 6
%_arr_v2float_uint_6 = OpTypeArray %v2float %uint_6
%_ptr_Function__arr_v2float_uint_6 = OpTypePointer Function %_arr_v2float_uint_6
%float_0_699999988 = OpConstant %float 0.699999988
%float_n0_699999988 = OpConstant %float -0.699999988
         %28 = OpConstantComposite %v2float %float_0_699999988 %float_n0_699999988
%float_n0_75 = OpConstant %float -0.75
%float_0_800000012 = OpConstant %float 0.800000012
         %31 = OpConstantComposite %v2float %float_n0_75 %float_0_800000012
    %float_0 = OpConstant %float 0
         %33 = OpConstantComposite %v2float %float_0 %float_0
%float_0_300000012 = OpConstant %float 0.300000012
         %35 = OpConstantComposite %v2float %float_0_300000012 %float_0
%float_n0_300000012 = OpConstant %float -0.300000012
         %37 = OpConstantComposite %v2float %float_0 %float_n0_300000012
         %38 = OpConstantComposite %v2float %float_0_300000012 %float_n0_300000012
         %39 = OpConstantComposite %_arr_v2float_uint_6 %28 %31 %33 %35 %37 %38
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
%in_refVertexIndex = OpVariable %_ptr_Input_int Input
       %bool = OpTypeBool
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
         %70 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %perVertex = OpVariable %_ptr_Function_v2float Function
%perInstance = OpVariable %_ptr_Function__arr_v2float_uint_6 Function
         %16 = OpAccessChain %_ptr_Input_float %in_position %uint_0
         %17 = OpLoad %float %16
         %19 = OpAccessChain %_ptr_Input_float %in_position %uint_1
         %20 = OpLoad %float %19
         %21 = OpCompositeConstruct %v2float %17 %20
               OpStore %perVertex %21
               OpStore %perInstance %39
         %45 = OpLoad %v2float %perVertex
         %48 = OpLoad %int %gl_InstanceIndex
         %49 = OpAccessChain %_ptr_Function_v2float %perInstance %48
         %50 = OpLoad %v2float %49
         %51 = OpFAdd %v2float %45 %50
         %53 = OpCompositeExtract %float %51 0
         %54 = OpCompositeExtract %float %51 1
         %55 = OpCompositeConstruct %v4float %53 %54 %float_0 %float_1
         %57 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %57 %55
         %59 = OpLoad %int %gl_VertexIndex
         %61 = OpLoad %int %in_refVertexIndex
         %63 = OpIEqual %bool %59 %61
               OpSelectionMerge %65 None
               OpBranchConditional %63 %64 %69
         %64 = OpLabel
         %68 = OpLoad %v4float %in_color
               OpStore %out_color %68
               OpBranch %65
         %69 = OpLabel
               OpStore %out_color %70
               OpBranch %65
         %65 = OpLabel
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

- `DrawTestsBaseClass::initialize` creates the color target and view, a host-visible vertex buffer, the vertex-input descriptions, command buffers, and graphics pipeline. The target is 256×256, single-sampled, and uses `VK_FORMAT_R8G8B8A8_UNORM` ([base initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L35-L50), [resources](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L152)).
- Before drawing, the color image is transitioned and cleared to opaque black, followed by a transfer-to-color-attachment pipeline barrier ([pre-render barriers](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L198-L215)).
- The command buffer path is selected from `SharedGroupParams`: legacy render pass, primary dynamic rendering, or secondary command-buffer recording with the render pass either outside or completely inside the secondary buffer ([non-instanced recording](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L131-L195)).
- The submitted command buffer is waited on. The rendered color image is read back in `VK_IMAGE_LAYOUT_GENERAL`, and the host compares it against the generated reference with `tcu::fuzzyCompare` and threshold `0.05` ([comparison](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L225-L238)).
- The instanced path follows the same flow, using the instanced reference bounds and an explicit queue-idle check before constructing the reference ([instanced validation](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L345-L390)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `simple_draw_triangle_list` | Incorrect non-indexed vertex fetch, triangle-list assembly, rasterization, render-target setup, synchronization, or image comparison behavior. |
| `simple_draw_triangle_strip` | Incorrect non-indexed vertex fetch, triangle-strip assembly, rasterization, render-target setup, synchronization, or image comparison behavior. |
| `simple_draw_instanced_triangle_list` | Incorrect instance iteration or `firstInstance` handling in addition to the list-draw causes. |
| `simple_draw_instanced_triangle_strip` | Incorrect instance iteration or `firstInstance` handling in addition to the strip-draw causes. |

### Cause Analysis

#### Generated vertex data and vertex fetch

**Possible failure symptoms:** Pixels outside the expected blue rectangle differ, or the rectangle is displaced or missing in all variants.

**Possible implementation causes:** The vertex-input binding, attribute formats, shader module, or vertex-fetch behavior may not deliver the positions and colors described by the test's `VertexElementData`. The source creates two leading entries with `refVertexIndex=-1`, visible entries beginning at index 2, and a trailing degenerate entry ([vertex buffer setup](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L64-L120)).

#### Primitive assembly and draw parameters

**Possible failure symptoms:** Only list or strip cases fail, or one topology produces a shape different from the expected rectangle.

**Possible implementation causes:** The topology state, vertex count, or `firstVertex` argument may be mishandled. Instanced failures may additionally indicate incorrect `instanceCount` or `firstInstance` processing. The test does not isolate a single layer: a mismatch can involve pipeline state, generated shader behavior, resources, or host validation.

#### Render-pass and command-buffer execution

**Possible failure symptoms:** Failures correlate with legacy render-pass, primary dynamic-rendering, or secondary-command-buffer leaves while the other recording modes pass.

**Possible implementation causes:** The implementation may mishandle render-pass attachment state, dynamic-rendering setup, secondary command-buffer inheritance, command execution, or the required synchronization. Dynamic-rendering cases require `VK_KHR_dynamic_rendering` ([support check](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L393-L397)).

#### Image result comparison

**Possible failure symptoms:** The rendered image differs from the reference by more than the fuzzy threshold, producing a failed test status ([pass/fail assignment](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L230-L238)).

**Possible implementation causes:** The rasterized output, image transition/readback path, format conversion, or comparison implementation may be responsible. The comparison result alone does not identify which layer caused the difference.

## Case Pruning

### Requirement-based pruning

- Unsupported dynamic rendering is rejected by `checkSupport` when `useDynamicRendering` is true; the render-pass leaves do not require `VK_KHR_dynamic_rendering` ([support gate](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L393-L397)).

### Design-based pruning

- Under `CTS_USES_VULKANSC`, dynamic-rendering registration and recording are excluded by preprocessor guards, leaving the render-pass cases in the VulkanSC mustpass set ([dispatcher guard](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L199)).
- Nested secondary-command-buffer modes do not register `simple_draw` because `createChildren` skips the simple-draw family when `nestedSecondaryCmdBuffer` is true ([selection guard](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L82)).

## Key Takeaways

- The four leaves cover two primitive topologies crossed with ordinary and instanced non-indexed draws.
- Every case uses `firstVertex=2`; instanced cases also use `instanceCount=4` and `firstInstance=2`.
- The oracle is a fuzzy comparison of a host-generated blue rectangle against the rendered color attachment, not a direct shader-output scalar check.
- The leaves are repeated across render-pass and three non-nested dynamic-rendering modes; nested dynamic-rendering modes intentionally have no simple-draw leaves.

## Source Reference Appendix

- [Assigned implementation: `vktDrawSimpleTest.cpp`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L47-L120) : test classes and vertex data.
- [`SimpleDraw::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L123-L239) : non-instanced recording and image oracle.
- [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L273-L391) : instanced recording and image oracle.
- [`SimpleDrawTests::init`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L401-L446) : exact leaf registration.
- [`DrawTestsBaseClass`](../../../modules/vulkan/draw/vktDrawBaseClass.hpp#L73-L160) and [initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L35-L195) : shared resources and pipeline.
- [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L122) and [category roots](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) : category-qualified registration scope.
- [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt#L2093-L2096) and [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L1642-L1645) : mustpass evidence for representative paths.
- [Vulkan render-pass chapter](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7-L10) : render pass instance requirement for draw commands.
