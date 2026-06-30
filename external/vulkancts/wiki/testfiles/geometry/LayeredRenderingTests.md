## Overview

**Core question:** Does layered geometry-shader rendering put each generated primitive on the intended layer, face, or 3D slice,
and do the host checks observe the expected per-layer image contents?

- This page covers the `geometry.layered` test family implemented by
  [vktGeometryLayeredRenderingTests.cpp](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1).
- The family combines one image-shape prefix, one size prefix, and one behavior leaf. The behavior leaf is the main semantic
  axis: it changes shader logic, execution path, and validation expectations.
- The same ten behavior leaves repeat under 1D-array, 2D-array, cube, cube-array, and 3D image-view prefixes.
- Most leaves draw into a layered color attachment. The `readback` leaf adds depth/stencil and two-pass attachment-load checks,
  while the `secondary_cmd_buffer` leaves add secondary command buffer execution and storage-image feedback.

## Background Knowledge

- A layered framebuffer exposes multiple destinations through one framebuffer: array layers, cube faces, cube-array face slices,
  or 3D image z slices.
- A geometry shader selects the destination for emitted primitives by writing `gl_Layer` before `EmitVertex()`.
- The host validates all effective layers after rendering. A wrong `gl_Layer`, wrong cube-face mapping, or wrong 3D-slice mapping
  becomes a wrong image in one or more layers.
- `geometry.layered.2d_array.64_64_4.<leaf>` is the easiest concrete model: a 64x64 2D-array image with exactly four layers.

## Registration Hierarchy

```text
geometry.layered
├── 1d_array
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The direct children are image-view-type intermediate nodes registered by
[createLayeredRenderingTests()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1996-L2075). Each direct
child contains two size intermediate nodes, and each size intermediate node contains the same ten behavior leaves. The default
mustpass list confirms the generated `geometry.layered` leaves in
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L95-L194).

## Intermediate Nodes

The direct intermediate nodes say what a layer number means:

| Intermediate node | Layer interpretation | Registered sizes |
|-------------------|----------------------|------------------|
| `1d_array` | A 1D array layer. | `64_1_4`, `12_1_6` |
| `2d_array` | A 2D array layer. | `64_64_4`, `12_36_6` |
| `cube` | One cube face. | `64_64_6`, `36_36_6` |
| `cube_array` | One face of one cube in a cube array. | `64_64_12`, `36_36_12` |
| `3d` | One z slice of a 3D image. | `64_64_8`, `12_36_6` |

The size intermediate node encodes width, height, and layer count or 3D depth. For example, `2d_array.64_64_4` means a 64x64
2D-array image with four layers. The behavior leaf below the size is what changes the shader and validation rule.

## Behavior Leaves

Use this fixed prefix as the concrete mental model:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.<leaf>
```

All ten leaves below that prefix render to the same four-layer 64x64 2D-array image. Only the final leaf changes what happens.

### `render_to_default_layer` — implicit layer 0

The geometry shader emits one rectangle and does not write `gl_Layer`. The expected result is:

```text
layer 0: left half is white
layer 1: black
layer 2: black
layer 3: black
```

This checks the default rule: without explicit layer selection, rendering lands in layer 0.

### `render_to_one` — one explicit target layer

The geometry shader emits one rectangle and writes `gl_Layer = 2`, the middle target layer for four layers. The expected result
is:

```text
layer 0: black
layer 1: black
layer 2: left half is white
layer 3: black
```

This checks the simplest explicit `gl_Layer` assignment away from layer 0.

### `render_to_all` — one invocation targets every layer

One geometry shader invocation loops over all four layers. For each layer, it writes `gl_Layer = layerNdx`, emits one rectangle,
and assigns a layer-specific color. The expected result is:

```text
layer 0: left half is white
layer 1: left half is red
layer 2: left half is green
layer 3: left half is blue
```

This checks repeated layer selection from one geometry shader invocation.

### `render_different_content` — layers must keep independent contents

The geometry shader loops over layers but changes the rectangle width by layer. Layer 0 intentionally remains empty. The expected
result is:

```text
layer 0: black
layer 1: a narrow white bar, about 1/4 image width
layer 2: a wider white bar, about 1/2 image width
layer 3: a still wider white bar, about 3/4 image width
```

This checks that layers do not accidentally share, duplicate, or overwrite the same content.

### `fragment_layer` — fragment-stage `gl_Layer`

The geometry shader chooses the destination layer, and the fragment shader reads `gl_Layer` to compute color. The expected result
is one encoded color per layer:

```text
layer 0: left half has the color for fragment gl_Layer == 0
layer 1: left half has the color for fragment gl_Layer == 1
layer 2: left half has the color for fragment gl_Layer == 2
layer 3: left half has the color for fragment gl_Layer == 3
```

This checks that layer identity is preserved into the fragment stage, not only that pixels land in the right layer.

### `invocation_per_layer` — one geometry invocation per layer

The geometry shader runs with four invocations for one input point. Invocation 0 writes layer 0, invocation 1 writes layer 1,
invocation 2 writes layer 2, and invocation 3 writes layer 3, using `gl_InvocationID` as the layer number. The expected image
matches `render_to_all`:

```text
layer 0: left half is white
layer 1: left half is red
layer 2: left half is green
layer 3: left half is blue
```

This separates loop-based layer targeting from geometry-shader invocation handling.

### `multiple_layers_per_invocation` — one invocation writes multiple layers

The geometry shader again uses multiple invocations, but each invocation writes both its own layer and the next layer, wrapping
from layer 3 back to layer 0. The expected image is:

```text
layer 0: black
layer 1: a narrow white bar, about 1/4 image width
layer 2: a wider white bar, about 1/2 image width
layer 3: a still wider white bar, about 3/4 image width
```

This checks the harder case where one geometry shader invocation emits primitives for more than one layer.

### `readback` — layered rendering plus color/depth/stencil copyback

The host initializes color, depth, and stencil attachments, renders twice, and copies all three result images back to CPU-visible
buffers. A pass uniform tells the geometry shader whether it is pass 0 or pass 1. The expected per-layer shape is:

```text
left region: result from pass 1
middle region: result from pass 0
right region: original cleared content
```

This is a layered-rendering test plus an attachment-load and copyback test. It can expose issues in depth/stencil layered
rendering, image layouts, attachment load behavior, image copies, or CPU-visible result interpretation.

### `secondary_cmd_buffer` — layered rendering through a secondary command buffer

The rendering commands are recorded into a secondary command buffer that does not inherit a concrete framebuffer. The host also
pre-fills a layered storage image. During two draws, the fragment shader averages the geometry color with the storage-image color
and stores the result back. The expected color is:

```text
final color = average(average(initial storage-image color, geometry color), geometry color)
```

This checks layered rendering when execution goes through a secondary command buffer and when fragment shader image load/store
ordering matters.

### `secondary_cmd_buffer_inherit_framebuffer` — inherited-framebuffer variant

This leaf uses the same shader behavior and expected image as `secondary_cmd_buffer`. The difference is command-buffer setup:
`secondary_cmd_buffer` begins without an inherited framebuffer, while `secondary_cmd_buffer_inherit_framebuffer` provides the
actual framebuffer in the secondary command buffer inheritance info.

If only this leaf fails, the likely problem is framebuffer inheritance rather than basic `gl_Layer` routing.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image-view prefix | `1d_array`, `2d_array`, `cube`, `cube_array`, `3d` | Changes what a layer number names: array layer, cube face, cube-array face slice, or 3D z slice. | [imageParamGroups[]](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2023-L2036) |
| Size prefix | `64_1_4`, `12_1_6`, `64_64_4`, `12_36_6`, `64_64_6`, `36_36_6`, `64_64_12`, `36_36_12`, `64_64_8` | Changes width, height, and effective layer count or 3D depth. | [size-name generation](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2043-L2052) |
| Behavior leaf | `render_to_default_layer`, `render_to_one`, `render_to_all`, `render_different_content`, `fragment_layer`, `invocation_per_layer`, `multiple_layers_per_invocation`, `readback`, `secondary_cmd_buffer`, `secondary_cmd_buffer_inherit_framebuffer` | Changes shader logic, runtime path, and validation rule; this is the main semantic axis. | [behavior registration](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000-L2068) |
| Effective layer count | array layer count, cube face count, cube-array face-slice count, or 3D depth | Determines shader loop bounds and host validation count. | [numLayers calculation](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L870-L871) |
| Secondary-command-buffer inheritance | false or true | Splits `secondary_cmd_buffer` from `secondary_cmd_buffer_inherit_framebuffer`. | [inheritance info](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1871-L1889) |

## Shader Analysis

The representative walkthrough uses `dEQP-VK.geometry.layered.2d_array.64_64_4.render_to_all` because it shows the central
layer-routing mechanism without the extra readback or secondary-command-buffer machinery: one geometry shader invocation loops
over all four layers and writes `gl_Layer` before emitting each rectangle.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.render_to_all
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `2d_array` | Use a 2D-array render target. |
| `64_64_4` | Use four 64x64 layers. |
| `render_to_all` | Emit one colored left-half rectangle to every layer. |
| Primary shader | The geometry shader owns the tested `gl_Layer` writes. |

#### Purpose

This shader verifies that repeatedly assigning `gl_Layer` in one geometry shader invocation routes generated primitives to all
array layers, with different colors making layer swaps or missing layers visible.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Input primitive | Receives one point. | Keeps input geometry irrelevant; all visible rectangles are generated in the geometry shader. |
| Layer loop | Iterates `layerNdx` from 0 through 3. | Targets every layer in the selected 2D-array image. |
| Layer assignment | Writes `gl_Layer = layerNdx` before each emitted vertex. | This is the tested routing signal. |
| Per-layer color | Writes `colors[layerNdx % 6]` to `vert_color`. | Makes wrong destination layers visible as wrong colors. |
| Output primitive | Emits four vertices and calls `EndPrimitive()` for each layer. | Produces one left-half rectangle per layer. |

#### Shader Code

The vertex shader is empty and the fragment shader only writes `o_color = vert_color`; the geometry shader is the stage whose
logic matters for this representative case.

##### Geometry Shader

```glsl
#version 450
/// One point is enough because the geometry shader synthesizes all output rectangles.
layout(points) in;
/// Four layers times four vertices per rectangle gives a maximum of sixteen emitted vertices.
layout(triangle_strip, max_vertices = 16) out;
/// Fragment shader receives this per-layer color at location 0.
layout(location = 0) out vec4 vert_color;
out gl_PerVertex {
    vec4 gl_Position;
    float gl_PointSize;
};
void main(void)
{
    const vec4 colors[6] = vec4[6] (vec4(1.0, 1.0, 1.0, 1.0),
                                    vec4(1.0, 0.0, 0.0, 1.0),
                                    vec4(0.0, 1.0, 0.0, 1.0),
                                    vec4(0.0, 0.0, 1.0, 1.0),
                                    vec4(1.0, 1.0, 0.0, 1.0),
                                    vec4(1.0, 0.0, 1.0, 1.0));
    /// Loop bound comes from the `64_64_4` layer count.
    for (int layerNdx = 0; layerNdx < 4; ++layerNdx) {
        const int colorNdx = layerNdx % 6;

        /// Lower-left vertex of the left-half rectangle for this layer.
        gl_Position = vec4(-1.0, -1.0, 0.0, 1.0);
        gl_Layer    = layerNdx;
        vert_color  = colors[colorNdx];
        gl_PointSize = 1.0;
        EmitVertex();

        /// Upper-left vertex; `gl_Layer` is repeated before each emitted vertex.
        gl_Position = vec4(-1.0,  1.0, 0.0, 1.0);
        gl_Layer    = layerNdx;
        vert_color  = colors[colorNdx];
        gl_PointSize = 1.0;
        EmitVertex();

        /// Lower-middle vertex sets the rectangle width to half the image.
        gl_Position = vec4( 0.0, -1.0, 0.0, 1.0);
        gl_Layer    = layerNdx;
        vert_color  = colors[colorNdx];
        gl_PointSize = 1.0;
        EmitVertex();

        /// Upper-middle vertex completes the triangle strip for this layer.
        gl_Position = vec4( 0.0,  1.0, 0.0, 1.0);
        gl_Layer    = layerNdx;
        vert_color  = colors[colorNdx];
        gl_PointSize = 1.0;
        EmitVertex();
        EndPrimitive();
    };
}
```

#### Additional Info

- `render_to_all` uses one geometry shader invocation with a loop. `invocation_per_layer` produces a similar expected image but
  uses multiple geometry shader invocations and `gl_InvocationID` instead.
- The fragment shader is intentionally simple for this representative case; `fragment_layer` is the leaf where fragment-stage
  `gl_Layer` becomes the central behavior.
- The walkthrough disassembly was generated for Vulkan 1.0 / SPIR-V 1.0 from the reconstructed primary geometry shader.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Default and single-layer leaves | Emit one rectangle and either omit `gl_Layer` or write the middle target layer. | [default and single-layer branches](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L920-L960) |
| All-layer leaves | Loop over all layers and emit a colored rectangle per layer. | [all-layer branch](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L962-L992) |
| Fragment-layer leaf | Fragment shader computes color from fragment-stage `gl_Layer`. | [fragment `gl_Layer` branch](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1188-L1195) |
| Invocation leaves | Use `layout(points, invocations = numLayers) in` and `gl_InvocationID`. | [invocation layout](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L890-L892) |
| Readback leaf | Geometry shader reads a pass uniform and emits pass-dependent color and depth values. | [readback branch](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1107-L1142) |
| Secondary-command-buffer leaves | Fragment shader reads and writes an `rgba8` storage image and averages stored and incoming colors. | [secondary fragment branch](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1196-L1211) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 10
; Bound: 82
; Schema: 0
               OpCapability Geometry
               OpCapability GeometryPointSize
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_Layer %vert_color
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 16
               OpSource GLSL 450
               OpName %main "main"
               OpName %layerNdx "layerNdx"
               OpName %colorNdx "colorNdx"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_Layer "gl_Layer"
               OpName %vert_color "vert_color"
               OpName %indexable "indexable"
               OpName %indexable_0 "indexable"
               OpName %indexable_1 "indexable"
               OpName %indexable_2 "indexable"
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex Block
               OpDecorate %gl_Layer BuiltIn Layer
               OpDecorate %vert_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
      %int_6 = OpConstant %int 6
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %31 = OpConstantComposite %v4float %float_n1 %float_n1 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
   %gl_Layer = OpVariable %_ptr_Output_int Output
 %vert_color = OpVariable %_ptr_Output_v4float Output
       %uint = OpTypeInt 32 0
     %uint_6 = OpConstant %uint 6
%_arr_v4float_uint_6 = OpTypeArray %v4float %uint_6
         %41 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
         %42 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %43 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %44 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
         %45 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
         %46 = OpConstantComposite %v4float %float_1 %float_0 %float_1 %float_1
         %47 = OpConstantComposite %_arr_v4float_uint_6 %41 %42 %43 %44 %45 %46
%_ptr_Function__arr_v4float_uint_6 = OpTypePointer Function %_arr_v4float_uint_6
%_ptr_Function_v4float = OpTypePointer Function %v4float
      %int_1 = OpConstant %int 1
%_ptr_Output_float = OpTypePointer Output %float
         %57 = OpConstantComposite %v4float %float_n1 %float_1 %float_0 %float_1
         %65 = OpConstantComposite %v4float %float_0 %float_n1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
   %layerNdx = OpVariable %_ptr_Function_int Function
   %colorNdx = OpVariable %_ptr_Function_int Function
  %indexable = OpVariable %_ptr_Function__arr_v4float_uint_6 Function
%indexable_0 = OpVariable %_ptr_Function__arr_v4float_uint_6 Function
%indexable_1 = OpVariable %_ptr_Function__arr_v4float_uint_6 Function
%indexable_2 = OpVariable %_ptr_Function__arr_v4float_uint_6 Function
               OpStore %layerNdx %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %layerNdx
         %18 = OpSLessThan %bool %15 %int_4
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %20 = OpLoad %int %layerNdx
         %22 = OpSMod %int %20 %int_6
               OpStore %colorNdx %22
         %33 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %33 %31
         %36 = OpLoad %int %layerNdx
               OpStore %gl_Layer %36
         %48 = OpLoad %int %colorNdx
               OpStore %indexable %47
         %52 = OpAccessChain %_ptr_Function_v4float %indexable %48
         %53 = OpLoad %v4float %52
               OpStore %vert_color %53
         %56 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %56 %float_1
               OpEmitVertex
         %58 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %58 %57
         %59 = OpLoad %int %layerNdx
               OpStore %gl_Layer %59
         %60 = OpLoad %int %colorNdx
               OpStore %indexable_0 %47
         %62 = OpAccessChain %_ptr_Function_v4float %indexable_0 %60
         %63 = OpLoad %v4float %62
               OpStore %vert_color %63
         %64 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %64 %float_1
               OpEmitVertex
         %66 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %66 %65
         %67 = OpLoad %int %layerNdx
               OpStore %gl_Layer %67
         %68 = OpLoad %int %colorNdx
               OpStore %indexable_1 %47
         %70 = OpAccessChain %_ptr_Function_v4float %indexable_1 %68
         %71 = OpLoad %v4float %70
               OpStore %vert_color %71
         %72 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %72 %float_1
               OpEmitVertex
         %73 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %73 %43
         %74 = OpLoad %int %layerNdx
               OpStore %gl_Layer %74
         %75 = OpLoad %int %colorNdx
               OpStore %indexable_2 %47
         %77 = OpAccessChain %_ptr_Function_v4float %indexable_2 %75
         %78 = OpLoad %v4float %77
               OpStore %vert_color %78
         %79 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %79 %float_1
               OpEmitVertex
               OpEndPrimitive
               OpBranch %13
         %13 = OpLabel
         %80 = OpLoad %int %layerNdx
         %81 = OpIAdd %int %80 %int_1
               OpStore %layerNdx %81
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Simple color-rendering leaves

The seven simple leaves are `render_to_default_layer`, `render_to_one`, `render_to_all`, `render_different_content`,
`fragment_layer`, `invocation_per_layer`, and `multiple_layers_per_invocation`.

- The host creates one layered color image, a layered image view, a framebuffer exposing all effective layers, a graphics
  pipeline, and a host-visible copyback buffer.
- It clears all layers to black, draws one point, copies all layers to the buffer, and invalidates the host-visible memory.
- `verifyResults()` iterates every effective layer or slice through `LayeredImageAccess` and delegates the expected content rule
  to `verifyLayerContent()`.

### `readback`

- The host creates layered color and depth/stencil attachments, pre-fills them with known values, and runs two render passes.
- A geometry-stage uniform selects pass 0 or pass 1. Attachment load behavior must preserve earlier content where the second pass
  does not overwrite it.
- The host copies color, depth, and stencil results to CPU-visible buffers and validates the three-region bar pattern for every
  layer.

### Secondary command buffer leaves

- The host creates a layered color attachment and a layered storage image, then pre-fills the storage image with per-layer colors.
- It records clears, two draws, and a fragment-stage shader memory barrier into a secondary command buffer.
- `secondary_cmd_buffer` begins the secondary command buffer without a concrete inherited framebuffer;
  `secondary_cmd_buffer_inherit_framebuffer` supplies the framebuffer in inheritance info.
- The host executes the secondary command buffer inside a primary render pass, copies the color attachment, and validates the
  final blended per-layer result.

## Case Pruning

### Requirement-based pruning

- All leaves require geometry-shader support through
  [DEVICE_CORE_FEATURE_GEOMETRY_SHADER](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1965-L1968).
- `3d` prefixes require `VK_KHR_maintenance1` and, on portability-subset implementations, `imageView2DOn3DImage` support.
- Secondary-command-buffer leaves require fragment stores and atomics because their fragment shader accesses a storage image.
- Vulkan SC applies an additional restriction when a secondary command buffer would inherit a null framebuffer.
- The `readback` path checks depth/stencil image format properties before creating the depth/stencil attachment.

### Design-based pruning

- Each image-view prefix uses two representative sizes rather than exhaustive extents.
- The ten behavior leaves are repeated for every size prefix so the same behavior can be compared across image shapes.
- `secondary_cmd_buffer_inherit_framebuffer` exists only for the secondary-command-buffer behavior because ordinary leaves do not
  use secondary command buffer inheritance.

## Key Takeaways

- The behavior leaf is the most important part of a `geometry.layered` path; it determines the shader behavior, runtime path, and
  validation rule.
- The image-view and size prefixes still matter because they change what `gl_Layer` indexes and how many destinations are checked.
- The family separates similar-looking outcomes by mechanism: one loop to all layers, one invocation per layer, one invocation to
  multiple layers, fragment-stage layer reads, two-pass readback, and secondary command buffer execution.
- A failure usually identifies a specific class of bug: default layer routing, explicit `gl_Layer` writes, geometry shader
  invocations, fragment-stage `gl_Layer`, attachment load/copyback, or secondary command buffer inheritance.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shader generation | [initPrograms()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L850-L1220) | Generates all geometry and fragment shader behavior variants. |
| Per-layer validation | [verifyLayerContent()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L687-L800) | Defines the expected image for each behavior leaf. |
| Result iteration | [verifyResults()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L817-L837) | Iterates every effective layer or slice. |
| Simple execution path | [test()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1223-L1307) | Executes the seven simple color-rendering leaves. |
| Readback execution path | [testLayeredReadBack()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1309-L1692) | Executes two-pass color/depth/stencil readback. |
| Secondary command buffer path | [testSecondaryCmdBuffer()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1694-L1963) | Executes both secondary-command-buffer leaves. |
| Feature checks | [checkSupport()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1965-L1992) | Applies device capability requirements. |
| Registration matrix | [createLayeredRenderingTests()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1996-L2075) | Builds image prefix, size prefix, and behavior-leaf paths. |
| Category attachment | [createChildren()](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L41-L50) | Attaches `layered` under the `geometry` category. |
| Mustpass evidence | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L95-L194) | Confirms executable leaves in the default Vulkan CTS geometry mustpass list. |
