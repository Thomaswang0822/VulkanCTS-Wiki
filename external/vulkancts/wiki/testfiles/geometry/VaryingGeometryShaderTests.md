## Overview

**Core question:** Do vertex-to-geometry and geometry-to-fragment varying interfaces preserve the expected values when stages
produce different numbers of user varyings?

- This page covers the `geometry.varying` test family implemented by
  [vktGeometryVaryingGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L1).
- The test family is a small explicit matrix over vertex-stage output behavior and geometry-stage output behavior.
- Each case renders a triangle through generated vertex, geometry, and fragment shaders. The final fragment color encodes
  whether the expected cross-stage data path was present, absent, split, or recombined correctly.
- Failures point to shader-interface matching problems, geometry-shader input array handling, geometry-to-fragment location
  handling, or incorrect compilation of simple swizzles and arithmetic across stages.

## Background Knowledge

- A **varying** is a shader user-defined value passed from one pipeline stage to the next, such as a color produced by the
  vertex shader and consumed by the geometry shader, or a value produced by the geometry shader and consumed by the fragment
  shader. In modern GLSL the old `varying` keyword is replaced by matching `out` and `in` declarations, but CTS still uses
  “varying” as the test-family name for this cross-stage data path.
- User varyings are matched between shader stages by declared location. This test uses location `0` from vertex to geometry
  and locations `0` and `1` from geometry to fragment.
- Geometry-shader inputs for user varyings are arrays, with one element per input primitive vertex. In the representative
  case, `v_geom_0[0]`, `v_geom_0[1]`, and `v_geom_0[2]` correspond to the three triangle input vertices.
- The geometry shader always emits three vertices for a triangle-strip output. The tested variable is not topology expansion;
  it is whether data moves correctly through the stage interfaces.
- Missing user varyings are handled by generated fallback paths. For example, when the vertex shader does not
  write a color varying, the geometry shader uses constant red.
- Validation is image-based: shader-interface behavior is converted into a rendered color pattern and compared with a
  reference PNG.

## Registration Hierarchy

```text
geometry.varying
├── vertex_no_op_geometry_out_1
├── vertex_out_0_geometry_out_1
├── vertex_out_0_geometry_out_2
├── vertex_out_1_geometry_out_0
└── vertex_out_1_geometry_out_2
```

The leaves are registered by
[createVaryingGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L273-L291)
and appear in the default geometry mustpass list at
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L195-L199). This test family has no intermediate nodes below
`geometry.varying`; every child in the tree is an executable test case leaf.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Vertex output mode | `VERTEXT_NO_OP`, `VERTEXT_ZERO`, `VERTEXT_ONE` | Selects whether the vertex shader writes nothing, writes only `gl_Position`, or writes `gl_Position` plus `v_geom_0`. | [VertexOutputs](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L57-L62) |
| Geometry output mode | `GEOMETRY_ZERO`, `GEOMETRY_ONE`, `GEOMETRY_TWO` | Selects whether the geometry shader writes no fragment varying, one fragment varying, or two fragment varyings. | [GeometryOutputs](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L63-L68) |
| Registered combinations | five explicit leaves | Covers representative absent, one-output, and two-output interface cases without exhaustive enumeration. | [varyingTests[]](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L279-L285) |
| Input topology | triangle strip with three vertices | Provides one triangle input for the geometry shader. | [GeometryVaryingTestInstance](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L85-L103) |
| Validation observable | final fragment color in reference image | Converts varying-interface behavior into image comparison. | [fragment shader generation](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L244-L262) |

## Behavior Parameters

The primary behavioral axis is the executable test case leaf. Each leaf selects one explicit combination of vertex-stage output
mode and geometry-stage output mode, so the leaf name directly determines which stage interface is under test.

### `vertex_no_op_geometry_out_1` — geometry-owned position and one fragment varying

The vertex shader has an empty body, so the geometry shader does not receive `gl_in[]` positions from a meaningful vertex-stage
write and does not receive a user varying. The geometry shader uses hard-coded positions, uses fallback red as its input color,
and writes one geometry-to-fragment varying at location `0`. The fragment shader writes that single varying.

### `vertex_out_0_geometry_out_1` — position-only vertex output and one fragment varying

The vertex shader writes `gl_Position` but no user varying. The geometry shader must read the three `gl_in[]` positions, use
fallback red for color, and forward that color through one location-`0` geometry-to-fragment varying. This separates built-in
position flow from user-varying flow.

### `vertex_out_0_geometry_out_2` — position-only vertex output and two fragment varyings

The vertex shader still writes only `gl_Position`, so color comes from the geometry shader's fallback red path. The geometry
shader splits that color across `v_frag_0` and `v_frag_1`, and the fragment shader recombines the two locations with a swizzle.
This checks two-location geometry-to-fragment output without depending on vertex-to-geometry user varyings.

### `vertex_out_1_geometry_out_0` — vertex color input with no geometry fragment varying

The vertex shader writes both `gl_Position` and the location-`0` color varying. The fragment shader, however, uses constant red
because the geometry shader declares no geometry-to-fragment user varying. This leaf checks that a vertex-to-geometry varying can
exist without forcing a fragment-stage varying path in this case.

### `vertex_out_1_geometry_out_2` — vertex color input split across two fragment varyings

This is the richest leaf. The geometry shader reads `v_geom_0[]`, preserving the per-vertex association from the vertex shader,
then splits each input color across two geometry-to-fragment varyings. The fragment shader recombines those varyings, so the final
image depends on both the vertex-to-geometry input array and the two-location geometry-to-fragment interface.

## Shader Analysis

The representative walkthrough uses `dEQP-VK.geometry.varying.vertex_out_1_geometry_out_2` because it exercises both major
interfaces in the page: the vertex shader supplies a location-0 color varying to the geometry shader, and the geometry shader
splits that color across two fragment-stage varyings.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.varying.vertex_out_1_geometry_out_2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `VERTEXT_ONE` | The vertex shader writes both `gl_Position` and `layout(location = 0) out highp vec4 v_geom_0`. |
| `GEOMETRY_TWO` | The geometry shader writes both `layout(location = 0) out v_frag_0` and `layout(location = 1) out v_frag_1`. |
| Fragment recombination | The fragment shader writes `v_frag_0 + v_frag_1.yxzw`. |
| Input triangle | The host provides three vertices and three distinct colors. |

#### Purpose

This shader verifies that per-vertex user varyings are available to the geometry shader as an input array and that the
geometry shader can write two separate fragment-stage varyings whose values are recombined into the expected color.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Input interface | Reads `v_geom_0[]` at location 0. | Confirms vertex-to-geometry user varying transport. |
| Geometry shape | Receives `triangles` and emits one `triangle_strip` with `max_vertices = 3`. | Keeps topology simple so color-interface behavior is the focus. |
| Per-vertex processing | For each of three input vertices, uses matching `gl_in[i]` and `v_geom_0[i]`. | Checks that geometry input arrays preserve per-vertex association. |
| Split outputs | Writes half the color to `v_frag_0` and a swizzled half to `v_frag_1`. | Forces two geometry-to-fragment locations to carry meaningful data. |
| Fragment expectation | Fragment shader adds `v_frag_0 + v_frag_1.yxzw`. | Reconstructs the original color only if both outputs are correct. |

#### Shader Code

This representative path is a multi-shader interface test. The geometry shader is still the primary shader for SPIR-V
analysis, but the vertex and fragment shaders are shown because they create and consume the varyings being tested.

##### Vertex Shader

```glsl
#version 310 es
/// Location 0 vertex input is the position used for both `gl_Position` and later geometry-stage `gl_in[]` positions.
layout(location = 0) in highp vec4 a_position;
/// Location 1 vertex input is the host-provided color that becomes the user varying under test.
layout(location = 1) in highp vec4 a_color;
/// Location 0 output is matched by the geometry shader's `v_geom_0[]` input array.
layout(location = 0) out highp vec4 v_geom_0;
void main (void)
{
    gl_Position = a_position;
    v_geom_0 = a_color;
}
```

##### Geometry Shader

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
/// Geometry shader receives a full triangle: three `gl_in[]` positions and three user-varying array entries.
layout(triangles) in;
/// The shader emits exactly one triangle as a triangle strip.
layout(triangle_strip, max_vertices = 3) out;
/// Location 0 input array is produced by the vertex shader from the host color attribute.
layout(location = 0) in highp vec4 v_geom_0[];
/// Location 0 output carries half of the input color to the fragment shader.
layout(location = 0) out highp vec4 v_frag_0;
/// Location 1 output carries a swizzled half of the input color to the fragment shader.
layout(location = 1) out highp vec4 v_frag_1;
void main (void)
{
    /// Fixed offset moves the rendered triangle into the reference-image position.
    highp vec4 offset = vec4(-0.2, -0.2, 0.0, 0.0);
    highp vec4 inputColor;

    /// Vertex 0: keep position and color index aligned across `gl_in[]` and `v_geom_0[]`.
    inputColor = v_geom_0[0];
    gl_Position = gl_in[0].gl_Position + offset;
    v_frag_0 = inputColor * 0.5;
    v_frag_1 = inputColor.yxzw * 0.5;
    EmitVertex();

    /// Vertex 1: repeat the same interface transform for the second triangle vertex.
    inputColor = v_geom_0[1];
    gl_Position = gl_in[1].gl_Position + offset;
    v_frag_0 = inputColor * 0.5;
    v_frag_1 = inputColor.yxzw * 0.5;
    EmitVertex();

    /// Vertex 2: the three emitted vertices complete one triangle-strip triangle.
    inputColor = v_geom_0[2];
    gl_Position = gl_in[2].gl_Position + offset;
    v_frag_0 = inputColor * 0.5;
    v_frag_1 = inputColor.yxzw * 0.5;
    EmitVertex();

    EndPrimitive();
}
```

##### Fragment Shader

```glsl
#version 310 es
/// Location 0 receives the non-swizzled half-color from the geometry shader.
layout(location = 0) in highp vec4 v_frag_0;
/// Location 1 receives the swizzled half-color from the geometry shader.
layout(location = 1) in highp vec4 v_frag_1;
layout(location = 0) out highp vec4 fragColor;
void main (void)
{
    /// Applying the same `yxzw` swizzle to `v_frag_1` reconstructs the original input color.
    fragColor = v_frag_0 + v_frag_1.yxzw;
}
```

#### Additional Info

- The vertex shader varies across this page: this representative case uses the `VERTEXT_ONE` form, so it writes both
  `gl_Position` and `v_geom_0 = a_color`; other leaves may write only position or have an empty vertex shader body.
- The fragment shader varies across this page: this representative case uses the `GEOMETRY_TWO` form and recombines two
  varyings; other leaves use constant red or directly write `v_frag_0`.
- The source collection uses the default shader-build options for this GLSL source path; the walkthrough disassembly was
  generated for the primary geometry shader as Vulkan 1.0 / SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Vertex output mode | `VERTEXT_NO_OP` has an empty vertex shader; `VERTEXT_ZERO` writes only `gl_Position`; `VERTEXT_ONE` also writes `v_geom_0`. | [vertex shader generation](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L132-L161) |
| Geometry input color | `VERTEXT_ONE` reads `v_geom_0[i]`; other modes use fallback red. | [inputColor selection](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L184-L224) |
| Geometry output mode | `GEOMETRY_ZERO` writes no fragment varyings; `GEOMETRY_ONE` writes `v_frag_0`; `GEOMETRY_TWO` writes `v_frag_0` and `v_frag_1`. | [geometry output generation](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L174-L198) |
| Fragment output mode | Fragment output is constant red, direct `v_frag_0`, or `v_frag_0 + v_frag_1.yxzw`. | [fragment shader generation](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L244-L262) |

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
; Bound: 71
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %v_geom_0 %_ %gl_in %v_frag_0 %v_frag_1
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %offset "offset"
               OpName %inputColor "inputColor"
               OpName %v_geom_0 "v_geom_0"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %v_frag_0 "v_frag_0"
               OpName %v_frag_1 "v_frag_1"
               OpDecorate %v_geom_0 Location 0
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %v_frag_0 Location 0
               OpDecorate %v_frag_1 Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
%float_n0_200000003 = OpConstant %float -0.200000003
    %float_0 = OpConstant %float 0
         %12 = OpConstantComposite %v4float %float_n0_200000003 %float_n0_200000003 %float_0 %float_0
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
   %v_geom_0 = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %v_frag_0 = OpVariable %_ptr_Output_v4float Output
  %float_0_5 = OpConstant %float 0.5
   %v_frag_1 = OpVariable %_ptr_Output_v4float Output
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
     %offset = OpVariable %_ptr_Function_v4float Function
 %inputColor = OpVariable %_ptr_Function_v4float Function
               OpStore %offset %12
         %22 = OpAccessChain %_ptr_Input_v4float %v_geom_0 %int_0
         %23 = OpLoad %v4float %22
               OpStore %inputColor %23
         %31 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %32 = OpLoad %v4float %31
         %33 = OpLoad %v4float %offset
         %34 = OpFAdd %v4float %32 %33
         %36 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %36 %34
         %38 = OpLoad %v4float %inputColor
         %40 = OpVectorTimesScalar %v4float %38 %float_0_5
               OpStore %v_frag_0 %40
         %42 = OpLoad %v4float %inputColor
         %43 = OpVectorShuffle %v4float %42 %42 1 0 2 3
         %44 = OpVectorTimesScalar %v4float %43 %float_0_5
               OpStore %v_frag_1 %44
               OpEmitVertex
         %46 = OpAccessChain %_ptr_Input_v4float %v_geom_0 %int_1
         %47 = OpLoad %v4float %46
               OpStore %inputColor %47
         %48 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %49 = OpLoad %v4float %48
         %50 = OpLoad %v4float %offset
         %51 = OpFAdd %v4float %49 %50
         %52 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %52 %51
         %53 = OpLoad %v4float %inputColor
         %54 = OpVectorTimesScalar %v4float %53 %float_0_5
               OpStore %v_frag_0 %54
         %55 = OpLoad %v4float %inputColor
         %56 = OpVectorShuffle %v4float %55 %55 1 0 2 3
         %57 = OpVectorTimesScalar %v4float %56 %float_0_5
               OpStore %v_frag_1 %57
               OpEmitVertex
         %59 = OpAccessChain %_ptr_Input_v4float %v_geom_0 %int_2
         %60 = OpLoad %v4float %59
               OpStore %inputColor %60
         %61 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %62 = OpLoad %v4float %61
         %63 = OpLoad %v4float %offset
         %64 = OpFAdd %v4float %62 %63
         %65 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %65 %64
         %66 = OpLoad %v4float %inputColor
         %67 = OpVectorTimesScalar %v4float %66 %float_0_5
               OpStore %v_frag_0 %67
         %68 = OpLoad %v4float %inputColor
         %69 = OpVectorShuffle %v4float %68 %68 1 0 2 3
         %70 = OpVectorTimesScalar %v4float %69 %float_0_5
               OpStore %v_frag_1 %70
               OpEmitVertex
               OpEndPrimitive
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checking requires the Vulkan `geometryShader` core feature.
- The shared render instance creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color target, vertex buffer, graphics pipeline,
  and framebuffer.
- The vertex buffer contains three positions and three distinct color attributes. The selected vertex shader decides whether
  those colors enter the shader interface.
- The pipeline input topology is `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`, so the geometry shader receives one triangle.
- The command buffer draws three vertices, copies the rendered color image to a host-visible buffer, and waits for completion.
- Host validation compares the copied image with `vulkan/data/geometry/<test-name>.png` through the shared image comparison
  helper.

## Failure Meaning

A failure means the final image no longer matches the expected interface-driven color pattern for the selected leaf.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_no_op_geometry_out_1` | Fallback geometry generation or one-location geometry-to-fragment forwarding failure. |
| `vertex_out_0_geometry_out_1` | Built-in position handoff through `gl_in[]`, fallback color, or one-location geometry-to-fragment forwarding failure. |
| `vertex_out_0_geometry_out_2` | Built-in position handoff through `gl_in[]`, fallback color, two-location geometry-to-fragment forwarding, or fragment recombination failure. |
| `vertex_out_1_geometry_out_0` | Vertex-stage position/color interface handling with intentionally absent geometry-to-fragment varying path, or constant-fragment-output failure. |
| `vertex_out_1_geometry_out_2` | Vertex-to-geometry user-varying array handling, two-location geometry-to-fragment forwarding, or fragment recombination failure. |

All leaves also share the rendered-image comparison path. If shader interface behavior is correct but the copied image differs
from the reference PNG, the shared render, copyback, or image-comparison path would need source-level investigation.

### Cause Analysis

#### Fallback geometry generation or fallback color failure

**Possible failure symptoms:** leaves that do not receive a vertex-stage color varying should use the generated fallback
red color in the geometry shader. In `vertex_no_op_geometry_out_1`, the geometry shader also uses hard-coded positions because
the vertex shader body is empty. A failure can therefore mean the generated fallback path produced the wrong position, the wrong
red color, or a color pattern that no longer matches the reference image.

**Possible implementation causes:** this path is grounded in the generated GLSL, where the geometry shader chooses
`vec4(1.0, 0.0, 0.0, 1.0)` unless `VERTEXT_ONE` is selected and uses hard-coded positions only for `VERTEXT_NO_OP`. An
implementation issue could be incorrect compilation of that geometry shader control path, incorrect handling of a vertex shader
that writes no `gl_Position` while a following geometry shader provides positions, or incorrect propagation of the single
geometry-to-fragment output carrying the fallback color.

#### Built-in position handoff through `gl_in[]` failure

**Possible failure symptoms:** leaves with `VERTEXT_ZERO` or `VERTEXT_ONE` expect the geometry shader to read the three
vertex positions through `gl_in[0]`, `gl_in[1]`, and `gl_in[2]`. If those positions are not preserved, are associated with the
wrong input vertex, or are offset from the wrong source value, the rendered triangle no longer matches the reference image even
when color values are correct.

**Possible implementation causes:** the source uses triangle input, triangle-strip output, and per-vertex reads from
`gl_in[]`. A grounded implementation cause is incorrect geometry-shader lowering or execution for built-in per-vertex input
arrays, including wrong indexing of `gl_in[]` or wrong association between the vertex shader's `gl_Position` outputs and the
geometry shader's input primitive.

#### Vertex-to-geometry user-varying array handling failure

**Possible failure symptoms:** `vertex_out_1_geometry_out_2` expects the location-`0` vertex color to arrive in
`v_geom_0[0]`, `v_geom_0[1]`, and `v_geom_0[2]`, aligned with the corresponding `gl_in[]` positions. A failure can mean the color
varying is missing, matched to the wrong location, indexed as the wrong per-vertex element, or associated with the wrong emitted
vertex.

**Possible implementation causes:** geometry-shader user inputs are declared as arrays in this test. A grounded
implementation cause is incorrect shader-interface matching for location-`0` vertex outputs to geometry inputs, or incorrect
compiler/runtime handling of user-varying input arrays for geometry shaders.

#### Geometry-to-fragment varying forwarding failure

**Possible failure symptoms:** `geometry_out_1` leaves expect the geometry shader's `v_frag_0` value to reach the fragment
shader at location `0`. `geometry_out_2` leaves expect both `v_frag_0` at location `0` and `v_frag_1` at location `1` to arrive
with their per-vertex values intact. If one location is missing, swapped, stale, or interpolated from the wrong emitted vertex,
the final image differs from the reference.

**Possible implementation causes:** this is grounded in the generated geometry and fragment declarations. A possible
implementation cause is incorrect cross-stage interface matching between geometry shader outputs and fragment shader inputs,
especially when two explicit locations are declared, or incorrect interpolation/primitive assembly after the geometry shader emits
the triangle-strip vertices.

#### Fragment recombination or swizzle/arithmetic failure

**Possible failure symptoms:** the two-output leaves rely on `v_frag_0 = inputColor * 0.5`,
`v_frag_1 = inputColor.yxzw * 0.5`, and fragment-side `v_frag_0 + v_frag_1.yxzw`. A failure can mean the split values are correct
at the geometry output but the fragment shader reconstructs the wrong color because the swizzle, multiplication, addition, or
location use is wrong.

**Possible implementation causes:** the operations are simple floating-point vector operations and swizzles in GLSL.
A grounded implementation cause is shader compiler lowering that mishandles vector swizzles or arithmetic across the
geometry/fragment boundary, or an interface-location issue that causes the fragment shader to recombine the wrong inputs.

#### Intentionally absent geometry-to-fragment varying path failure

**Possible failure symptoms:** `vertex_out_1_geometry_out_0` intentionally has a vertex color varying but no
geometry-to-fragment varying declarations. The fragment shader should write constant red. A failure can mean the pipeline did not
handle the unused vertex-to-geometry color path correctly, the absence of geometry-to-fragment varyings affected pipeline linking,
or the constant fragment output did not produce the expected image.

**Possible implementation causes:** the generated shaders form a legal pipeline shape where one stage may produce or
consume user varyings differently from another as long as declared interfaces match between adjacent stages. A grounded cause is
incorrect pipeline compilation or cross-stage interface validation/lowering when a user varying exists before the geometry stage
but no user varying is consumed by the fragment stage.

#### Shared render, copyback, or reference-image comparison failure

**Possible failure symptoms:** the final pass/fail decision is image-based. A failure can occur even when the generated
shader logic is correct if the draw does not render into the expected attachment, the rendered image is copied back incorrectly,
or the reference comparison sees pixel values outside its tolerance and position-deviation thresholds.

**Possible implementation causes:** the shared render path creates the color attachment, records the draw, copies the
image to a host-visible buffer, invalidates the allocation, and compares against `vulkan/data/geometry/<test-name>.png`. If the
failure does not line up with one of the leaf-specific shader-interface mechanisms above, source-level investigation should focus
on that shared path and the logged image-comparison output rather than assuming a specific shader-interface bug.

## Case Pruning

### Requirement-based pruning

- All leaves require the `geometryShader` core feature.

### Design-based pruning

- The source uses five selected combinations rather than all nine possible `VertexOutputs` × `GeometryOutputs` pairs.
- The selected cases cover absence of vertex outputs, position-only vertex output, vertex color output, no geometry fragment
  output, one geometry fragment output, and two geometry fragment outputs.
- This keeps the page focused on representative interface behavior instead of exhaustive combinatorics.

## Key Takeaways

- `geometry.varying` is a compact cross-stage interface test: it changes which varyings exist at each stage.
- The representative `vertex_out_1_geometry_out_2` case proves both arrayed vertex-to-geometry input and two-location
  geometry-to-fragment output.
- Fallback red paths are deliberate: they make absent varyings produce defined, image-comparable behavior.
- For detailed failure interpretation, use `## Failure Meaning`; the important first step is to identify which behavior-parameter
  leaf failed, then map that leaf to the relevant interface, shader-generation, or shared render path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test spec structure | [VaryingTestSpec](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L70-L75) | Defines vertex-output and geometry-output modes. |
| Input data | [GeometryVaryingTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L91-L103) | Creates the three positions and three colors. |
| Support check | [VaryingTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L125-L128) | Requires geometry-shader support. |
| Program generation | [VaryingTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L130-L264) | Generates vertex, geometry, and fragment shader variants. |
| Registration | [createVaryingGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L273-L291) | Defines the exact `geometry.varying` leaves. |
| Shared render execution | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Provides render, copyback, and reference-image validation. |
| Reference-image comparison helper | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Defines reference file naming and comparison tolerances. |
