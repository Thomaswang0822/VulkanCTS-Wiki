## Overview

**Core question:** Does `gl_ViewportIndex` route each primitive to the selected viewport, and does a fragment shader receive that selected index?

- This page covers the `draw.renderpass.shader_viewport_index` test family implemented in [vktDrawShaderViewportIndexTests.cpp](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp).
- The tests draw two triangles per viewport into a 128 by 128 color attachment. The host builds a grid of viewport rectangles and a matching reference image.
- `vertex_shader_N` writes the viewport index in the vertex shader. `tessellation_shader_N` writes it in the tessellation evaluation shader. `fragment_shader_N` writes it in the vertex shader and reads it in the fragment shader to select a uniform-buffer color. `fragment_shader_implicit` reads the implicit index for the first viewport.
- `N` runs from 1 through 16. It changes the number of viewports, grid cells, colors, and vertices, while the behavioral group selects the tested shader-stage path.

## Background Knowledge

- A pre-rasterization shader that writes `gl_ViewportIndex` selects the viewport used for the primitive. The final active pre-rasterization stage controls selection; if that stage does not declare `ViewportIndex`, the first viewport is used and outputs from earlier stages are ignored. When a stage declares the built-in, every output vertex of a primitive must use the same value. See [the Vulkan `ViewportIndex` interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5662-L5748).
- In a fragment shader, `gl_ViewportIndex` is an input: it identifies the viewport used by the primitive that produced the fragment. It does not select a viewport at that stage.

## Registration Hierarchy

```text
draw.renderpass.shader_viewport_index
├── vertex_shader_1
├── fragment_shader_implicit
├── fragment_shader_1
└── tessellation_shader_1
```

The registration loop creates `vertex_shader_1` through `vertex_shader_16`, `fragment_shader_1` through `fragment_shader_16`, and `tessellation_shader_1` through `tessellation_shader_16`; `fragment_shader_implicit` is a separate one-viewport case. [Registration](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1087-L1117) uses these exact leaf names.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavioral group | `vertex_shader_N`, `fragment_shader_implicit`, `fragment_shader_N`, `tessellation_shader_N` | Selects the stage that exports or consumes `gl_ViewportIndex`. | [Program builders and registration](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418-L600) |
| `N` | `1` through `16` | Sets viewport count, grid-cell count, color count, and the draw's `N * 6` vertices. | [Grid and vertices](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L353-L396), [draw call](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L860-L907) |
| `writeFromVertex` | `false`, `true` | Fragment cases use `false` only for `fragment_shader_implicit`; numbered fragment cases use `true`. | [Fragment programs](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L460-L504), [registration](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1102-L1109) |
| Rendering path | render pass; dynamic rendering; eligible secondary command-buffer forms | Exercises the same draw and readback behavior through the shared draw group parameters. | [Renderer::draw](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L732-L809) |

## Behavior Parameters

The primary behavioral axis is the behavioral group. It determines whether the test checks a producer of `gl_ViewportIndex`, a fragment-stage consumer, or both.

### vertex_shader_N - vertex-stage viewport selection

The vertex shader assigns `gl_ViewportIndex = gl_VertexIndex / 6`. Six vertices make two triangles, so every vertex of one quad receives one index. Rasterization must place that full-viewport quad into the matching grid cell and preserve its vertex color.

### fragment_shader_implicit - implicit first-viewport input

This case uses one viewport and does not write `gl_ViewportIndex` in the vertex shader. The fragment shader indexes `color[gl_ViewportIndex]`; it must read the first viewport's index and select the only supplied color.

### fragment_shader_N - vertex export and fragment input

The vertex shader selects the viewport as in `vertex_shader_N`. The fragment shader ignores interpolated color and reads `color[gl_ViewportIndex]` from a uniform buffer. The image therefore checks both routing and fragment-stage consumption of the selected index.

### tessellation_shader_N - tessellation-evaluation viewport selection

The tessellation control shader keeps tessellation levels at 1.0. The tessellation evaluation shader assigns `gl_ViewportIndex = gl_PrimitiveID / 2`, so the two input triangles for each quad select one viewport. It also interpolates position and color before rasterization.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.shader_viewport_index.vertex_shader_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `vertex_shader_N` | The vertex stage exports `gl_ViewportIndex`; the fragment stage only passes through the interpolated color. |
| `N = 4` | The draw contains 24 vertices, arranged as four six-vertex quads for four viewport rectangles. |

#### Purpose

The vertex shader assigns one viewport index to each pair of triangles. The four-cell case exposes the division rule without the larger grids used by later leaves.

#### Structural Design

| Vertex range | `gl_VertexIndex / 6` | Primitive destination |
|--------------|----------------------|-----------------------|
| 0 through 5 | 0 | viewport 0 |
| 6 through 11 | 1 | viewport 1 |
| 12 through 17 | 2 | viewport 2 |
| 18 through 23 | 3 | viewport 3 |

#### Shader Code

```glsl
#version 450
#extension GL_ARB_shader_viewport_layer_array : require

/// Per-vertex clip-space position from the host vertex buffer.
layout(location = 0) in vec4 in_position;
/// Per-vertex color. The host repeats one color for all six vertices of a quad.
layout(location = 1) in vec4 in_color;
/// Color passed unchanged to the fragment shader.
layout(location = 0) out vec4 out_color;

void main(void)
{
    /// Six vertices form two triangles for one viewport-sized quad.
    gl_ViewportIndex = gl_VertexIndex / 6;
    gl_Position = in_position;
    out_color = in_color;
}
```

#### Additional Info

- [generateVertices](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L602-L642) emits six vertices with the same color for each viewport; [generateGrid](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L353-L381) supplies the matching viewport rectangles.
- The source builds `vert` with the default SPIR-V target and `vert_1_2` with SPIR-V 1.5; the renderer selects `vert_1_2` for a Vulkan 1.2 context. This walkthrough disassembles the default `vert` source target. [Vertex program setup](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418-L441), [module selection](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L701-L704)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `N` | The vertex source is unchanged. `N` changes the number of repeated six-vertex groups, viewports, and colors supplied by the host. | [Vertex program builder](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418-L458), [renderer setup](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L656-L730) |
| Behavioral group | Fragment cases conditionally keep the vertex assignment and add a uniform-buffer read in the fragment shader. Tessellation cases move the assignment to tessellation evaluation. | [Fragment and tessellation builders](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L460-L600) |

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
; Bound: 31
; Schema: 0
               OpCapability Shader
               OpCapability ShaderViewportIndexLayerEXT
               OpExtension "SPV_EXT_shader_viewport_index_layer"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_ViewportIndex %gl_VertexIndex %_ %in_position %out_color %in_color
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_shader_viewport_layer_array"
               OpName %main "main"
               OpName %gl_ViewportIndex "gl_ViewportIndex"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_ViewportIndex BuiltIn ViewportIndex
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %in_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Output_int = OpTypePointer Output %int
%gl_ViewportIndex = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_6 = OpConstant %int 6
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %11 = OpLoad %int %gl_VertexIndex
         %13 = OpSDiv %int %11 %int_6
               OpStore %gl_ViewportIndex %13
         %25 = OpLoad %v4float %in_position
         %27 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %27 %25
         %30 = OpLoad %v4float %in_color
               OpStore %out_color %30
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host generates `N` colors, `N` grid rectangles, and six vertices per rectangle. It creates a `VK_FORMAT_R8G8B8A8_UNORM` color attachment plus a host-visible transfer-destination readback buffer. [Test setup](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L945-L981)
- For fragment cases, `Renderer::drawCommands` allocates a host-visible uniform buffer containing the colors, writes it to descriptor set 0 binding 0, and binds that set before drawing. [Fragment resource binding](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L860-L907)
- The renderer records either a render pass or dynamic-rendering sequence, draws `N * 6` vertices, copies the color image to the readback buffer, submits, and waits. [Draw and copyback](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L732-L809)
- The host invalidates the readback allocation, generates the expected gray-backed colored grid, and compares it with `tcu::floatThresholdCompare` using `Vec4(0.02f)`. A mismatch fails with "Rendered image is not correct." [Validation](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L983-L999), [tessellation validation](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1051-L1067)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_shader_N` | Vertex-stage `ViewportIndex` export, primitive viewport selection, or multi-viewport rasterization is incorrect. |
| `fragment_shader_implicit` | The default viewport index supplied to fragment invocations is incorrect. |
| `fragment_shader_N` | Vertex-stage viewport selection or fragment-stage `ViewportIndex` input and uniform-array indexing is incorrect. |
| `tessellation_shader_N` | Tessellation-evaluation `ViewportIndex` export, primitive indexing, or multi-viewport rasterization is incorrect. |

### Cause Analysis

#### Pre-rasterization viewport-index export or selection

**Possible failure symptoms:** One or more expected grid cells have the wrong color, remain gray, or receive another cell's quad. The image comparison reports a mismatch.

**Possible implementation causes:** The implementation may mishandle the `ViewportIndex` output from the vertex or tessellation evaluation stage, or apply the wrong viewport transform. Vulkan requires the final active pre-rasterization writer to control the viewport and requires a common value for all output vertices of a primitive. [Vulkan interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5676-L5713)

#### Fragment-stage viewport-index input

**Possible failure symptoms:** A numbered fragment case can place quads in the correct cells while displaying colors selected from the wrong uniform-buffer elements. `fragment_shader_implicit` can fail its only cell when the input does not identify the first viewport.

**Possible implementation causes:** The implementation may fail to provide the rasterized viewport index to the fragment stage, or the fragment-stage interface may not preserve it for the uniform-array access. Vulkan defines fragment `ViewportIndex` as the viewport index of the primitive that produced the invocation. [Vulkan interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5711-L5713)

#### Tessellation-stage routing

**Possible failure symptoms:** Only `tessellation_shader_N` leaves fail, often with quads routed to incorrect cells or with missing expected colors.

**Possible implementation causes:** The implementation may mishandle `ViewportIndex` output from tessellation evaluation or associate `gl_PrimitiveID / 2` with the wrong triangle pair. The test keeps tessellation levels at 1.0, so its image result directly exposes routing after the evaluation stage. [Tessellation programs](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L529-L600)

## Case Pruning

### Requirement-based pruning

- Every case requires `multiViewport`, `VK_EXT_shader_viewport_index_layer`, and `maxViewports` of at least 16. [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1070-L1076)
- Tessellation leaves also require `tessellationShader`. [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1078-L1079)
- Dynamic-rendering variants require `VK_KHR_dynamic_rendering`. [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1081-L1082)

### Design-based pruning

The test uses one case per viewport count and behavioral group. It does not create combinations with different grid layouts or colors because `generateGrid` and `generateColors` are deterministic witnesses for the selected viewport count, not independent behavior axes.

## Key Takeaways

- The numbered vertex and tessellation leaves verify shader-produced viewport selection across one through sixteen viewports.
- The numbered fragment leaves verify the full path from vertex-produced index to fragment input and uniform-buffer color selection.
- `fragment_shader_implicit` isolates the default first-viewport input path.
- A whole-image comparison detects both placement failures and fragment-color selection failures.

## Source Reference Appendix

| Source area | Purpose |
|-------------|---------|
| [Grid, colors, and reference image](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L353-L416) | Defines the expected colored-cell image. |
| [Shader program builders](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418-L600) | Generates vertex, fragment, tessellation control, and tessellation evaluation shaders. |
| [Renderer and draw commands](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L646-L943) | Creates resources, sets viewports, binds the fragment uniform buffer, records work, and copies the image. |
| [Test functions and comparison](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L945-L1068) | Generates test data and decides pass or fail. |
| [Support checks and registration](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1070-L1117) | Defines feature gates and registered leaves. |
| [Draw category registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L80-L93) | Adds this test family to the draw test-category setup. |
| [Vulkan `ViewportIndex` rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5662-L5748) | Defines legal stage use, output selection, and fragment input semantics. |
