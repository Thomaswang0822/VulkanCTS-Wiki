## Overview

**Core question:** Does the geometry shader receive each Vulkan input primitive topology with the expected input shape, vertex
count, and adjacency data, and does its emitted output render as expected?

- This page covers the `geometry.input` test family implemented by
  [vktGeometryInputGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1).
- The test family is about geometry-shader input handling: ordinary primitive topologies, adjacency topologies, a
  triangle-strip-adjacency vertex-count sweep, and deliberate input-to-output primitive conversion.
- Each test case generates a small graphics pipeline with vertex, geometry, and fragment shaders. The geometry shader
  expands each received `gl_in` entry into visible output, and the host compares the rendered image with a reference PNG.
- The central failure signal is visual: a wrong input topology, wrong adjacency interpretation, wrong `gl_in.length()`,
  or wrong output topology changes the rendered pattern.

## Background Knowledge

- A geometry shader declares its input primitive class separately from its output primitive class. The input side can use
  `points`, `lines`, `triangles`, `lines_adjacency`, or `triangles_adjacency`; the output side uses `points`,
  `line_strip`, or `triangle_strip`.
- Vulkan pipeline primitive topology and GLSL geometry-shader input layout must agree. For example,
  `VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY` maps to the geometry-shader input layout `lines_adjacency`.
- The test intentionally amplifies geometry for observability. It is not modeling-style mesh subdivision; it emits a
  small repeated shape so image comparison can reveal whether the shader received the expected input vertices.
- Validation is image-based. The test does not read back per-primitive records; it renders to a color attachment, copies
  the image to host-visible memory, and compares it against `vulkan/data/geometry/<test-name>.png`.

## Registration Hierarchy

```text
geometry.input
├── basic_primitive
├── triangle_strip_adjacency
└── conversion
```

The three intermediate nodes are created by
[createInputGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260). The
default mustpass list includes the corresponding `dEQP-VK.geometry.input.*` leaves in
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L43-L70). The concrete test case leaves are summarized in
[Parameter Dimensions and Observed Values](#parameter-dimensions-and-observed-values) instead of being expanded in this
canonical tree, because the registration validator expects this block to contain exact one-level prefixes under the
`geometry.input` test family.

## Intermediate Nodes

### `basic_primitive` — ordinary topology reception

`basic_primitive` verifies that the geometry shader receives ordinary point, line, triangle, and selected adjacency
inputs with the expected GLSL geometry input layout. Its output topology is not always textually identical to the input
topology: line-like inputs render as `line_strip`, triangle-like inputs render as `triangle_strip`, point inputs render
as `points`, and adjacency inputs emit non-adjacency output strips. This lets all cases use one common shader-expansion
mechanism while preserving the broad primitive class that should be visible in the image.

### `triangle_strip_adjacency` — adjacency input with varying draw vertex counts

`triangle_strip_adjacency` fixes the input topology to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY` and varies
the number of vertices submitted by the draw from 0 through 12. The purpose is to exercise edge cases where the draw
provides too few, exactly enough, or more than enough vertices to form triangle-strip-with-adjacency primitives.

### `conversion` — deliberate input/output topology changes

`conversion` keeps the same generated shader shape but pairs an input topology with a different output topology. Examples
include `triangles_to_points`, `lines_to_points`, and `points_to_triangles`. These cases check that the implementation
can feed one primitive class into the geometry shader and emit another primitive class from it.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Input topology for `basic_primitive` | `points`, `lines`, `line_strip`, `triangles`, `triangle_strip`, `triangle_fan`, `lines_adjacency`, `line_strip_adjacency`, `triangles_adjacency` | Selects both the Vulkan input assembly topology and the GLSL geometry input layout. | [inputPrimitives[]](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L267-L277) |
| Output topology for `basic_primitive` | `points`, `line_strip`, `triangle_strip` | Chooses the geometry-shader output stream used to render the visible expanded shape. | [inputPrimitives[]](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L267-L277) |
| Triangle-strip-adjacency draw vertex count | `0` through `12` | Exercises the fixed adjacency topology across small draw sizes. | [vertex-count loop](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L283-L290) |
| Conversion pairs | `triangles_to_points`, `lines_to_points`, `points_to_lines`, `triangles_to_lines`, `points_to_triangles`, `lines_to_triangles` | Deliberately separates input primitive class from output primitive class. | [conversionPrimitives[]](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L293-L305) |
| Generated maximum emitted vertices | input vertex count per primitive multiplied by 3 | Gives the shader enough output budget to emit three visible vertices for each `gl_in` entry. | [calcOutputVertices()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L349-L367) |

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.input.basic_primitive.lines_adjacency
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic_primitive.lines_adjacency` | Selects `VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY` as the input assembly topology and registers the leaf under the ordinary topology-reception group. |
| `layout(lines_adjacency) in` | The geometry shader receives four `gl_in` vertices per primitive: two line endpoints plus their adjacent vertices. |
| `layout(line_strip, max_vertices = 12) out` | The output remains a non-adjacency line strip, with enough budget for three emitted vertices for each of the four input vertices. |
| `pointSize = false` | This line-strip output path does not enable `GL_EXT_geometry_point_size` and does not write `gl_PointSize`. |

#### Purpose

This shader verifies that a line-list-with-adjacency draw is delivered to the geometry shader as a four-vertex
`lines_adjacency` primitive. It makes each received vertex visible by emitting three offset line-strip vertices carrying
the input color.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Input declaration | `layout(lines_adjacency) in` | Forces `gl_in.length()` to be four for each primitive. |
| Output declaration | `layout(line_strip, max_vertices = 12) out` | Allows four input vertices times three emitted vertices. |
| Primitive separation | `yoffset = float(gl_PrimitiveIDIn) * vec4(0.02, 0.1, 0.0, 0.0)` | Moves each assembled primitive slightly so separate primitives are visible in the rendered reference. |
| Per-input expansion | Loop over `gl_in.length()` and emit three vertices with fixed offsets. | Turns every received endpoint or adjacency vertex into visible line-strip geometry. |
| Color forwarding | Copy `v_geom_FragColor[ndx]` to `v_frag_FragColor` before each emission. | Preserves the alternating white/red vertex attribute pattern through the geometry stage. |

#### Shader Code

This representative path is primarily a geometry-shader topology test, but the vertex and fragment shaders are shown because
they carry the color used to make each received input vertex visible in the reference image.

##### Vertex Shader

```glsl
#version 310 es
/// Location 0 vertex input is the host-provided position consumed later through `gl_in[]`.
layout(location = 0) in highp vec4 a_position;
/// Location 1 vertex input is the host-provided color used to identify expanded input vertices.
layout(location = 1) in highp vec4 a_color;
/// Location 0 output is matched by the geometry shader's per-input color array.
layout(location = 0) out highp vec4 v_geom_FragColor;
void main (void)
{
    gl_Position = a_position;
    v_geom_FragColor = a_color;
}
```

##### Geometry Shader

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
/// Geometry-stage input layout for a line list with adjacency: each invocation receives four `gl_in` vertices.
layout(lines_adjacency) in;
/// The shader emits separate line-strip segments, with three output vertices available per received input vertex.
layout(line_strip, max_vertices = 12) out;
/// Location 0 input array is produced by the vertex shader from the host vertex color attribute.
layout(location = 0) in highp vec4 v_geom_FragColor[];
/// Location 0 output is consumed by the fragment shader as the final color source.
layout(location = 0) out highp vec4 v_frag_FragColor;

void main (void)
{
    /// Fixed shader-local offsets expand one received input vertex into a small visible line-strip segment.
    const highp vec4 offset0 = vec4(-0.07, -0.01, 0.0, 0.0);
    const highp vec4 offset1 = vec4( 0.03, -0.03, 0.0, 0.0);
    const highp vec4 offset2 = vec4(-0.01,  0.08, 0.0, 0.0);
    /// `gl_PrimitiveIDIn` separates assembled adjacency primitives in screen space.
    highp vec4 yoffset = float(gl_PrimitiveIDIn) * vec4(0.02, 0.1, 0.0, 0.0);

    /// For `lines_adjacency`, `gl_in.length()` is four: adjacent vertex, endpoint, endpoint, adjacent vertex.
    for (highp int ndx = 0; ndx < gl_in.length(); ndx++)
    {
        gl_Position = gl_in[ndx].gl_Position + offset0 + yoffset;
        v_frag_FragColor = v_geom_FragColor[ndx];
        EmitVertex();

        gl_Position = gl_in[ndx].gl_Position + offset1 + yoffset;
        v_frag_FragColor = v_geom_FragColor[ndx];
        EmitVertex();

        gl_Position = gl_in[ndx].gl_Position + offset2 + yoffset;
        v_frag_FragColor = v_geom_FragColor[ndx];
        EmitVertex();
        /// End after each three-vertex expansion so each input vertex becomes its own strip segment.
        EndPrimitive();
    }
}
```

##### Fragment Shader

```glsl
#version 310 es
layout(location = 0) out mediump vec4 fragColor;
/// Location 0 input is the color selected by the geometry shader for each emitted vertex.
layout(location = 0) in highp vec4 v_frag_FragColor;
void main (void)
{
    fragColor = v_frag_FragColor;
}
```

#### Additional Info

- The vertex shader is stable across this page's generated topology cases: it forwards position and color so the geometry
  shader can test primitive reception while preserving a visible per-vertex color signal.
- The fragment shader is stable across this representative line-output path: it writes the geometry shader's forwarded color
  directly, so image differences come from geometry input and emission behavior rather than fragment logic.
- The `lines_adjacency` input spelling comes from `inputTypeToGLString()` mapping both line adjacency Vulkan topologies
  to the same GLSL geometry input layout.
- The output spelling comes from `outputTypeToGLString()`: both line-list and line-strip output requests generate
  `line_strip`, because geometry-shader line output is declared as a strip.
- The primary geometry shader is added to `sourceCollections.glslSources` without explicit `vk::ShaderBuildOptions`, so the CTS GLSL
  source collection default target is used here as SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Input topology | Changes `layout(...) in` and `gl_in.length()` through `inputTypeToGLString()`; adjacency line input maps to `lines_adjacency`. | [inputTypeToGLString()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306-L329) |
| Output topology | Changes `layout(..., max_vertices = ...) out`; this representative case maps line output to `line_strip`. | [outputTypeToGLString()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L331-L347) |
| Maximum emitted vertices | Changes the numeric `max_vertices`; line adjacency input uses `4 * 3`, producing `12`. | [calcOutputVertices()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L349-L367) |
| Point-size variant | Only point-list output adds `GL_EXT_geometry_point_size` and writes `gl_PointSize`; this line-strip case omits both. | [GeometryExpanderRenderTest::shaderGeometry()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L189-L231) |

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
; Bound: 88
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_PrimitiveIDIn %_ %gl_in %v_frag_FragColor %v_geom_FragColor
               OpExecutionMode %main InputLinesAdjacency
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputLineStrip
               OpExecutionMode %main OutputVertices 12
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %yoffset "yoffset"
               OpName %gl_PrimitiveIDIn "gl_PrimitiveIDIn"
               OpName %ndx "ndx"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %v_frag_FragColor "v_frag_FragColor"
               OpName %v_geom_FragColor "v_geom_FragColor"
               OpDecorate %gl_PrimitiveIDIn BuiltIn PrimitiveId
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %v_frag_FragColor Location 0
               OpDecorate %v_geom_FragColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_PrimitiveIDIn = OpVariable %_ptr_Input_int Input
%float_0_0199999996 = OpConstant %float 0.0199999996
%float_0_100000001 = OpConstant %float 0.100000001
    %float_0 = OpConstant %float 0
         %18 = OpConstantComposite %v4float %float_0_0199999996 %float_0_100000001 %float_0 %float_0
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_gl_PerVertex_0_uint_4 = OpTypeArray %gl_PerVertex_0 %uint_4
%_ptr_Input__arr_gl_PerVertex_0_uint_4 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_4
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_4 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%float_n0_0700000003 = OpConstant %float -0.0700000003
%float_n0_00999999978 = OpConstant %float -0.00999999978
         %47 = OpConstantComposite %v4float %float_n0_0700000003 %float_n0_00999999978 %float_0 %float_0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%v_frag_FragColor = OpVariable %_ptr_Output_v4float Output
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_ptr_Input__arr_v4float_uint_4 = OpTypePointer Input %_arr_v4float_uint_4
%v_geom_FragColor = OpVariable %_ptr_Input__arr_v4float_uint_4 Input
%float_0_0299999993 = OpConstant %float 0.0299999993
%float_n0_0299999993 = OpConstant %float -0.0299999993
         %65 = OpConstantComposite %v4float %float_0_0299999993 %float_n0_0299999993 %float_0 %float_0
%float_0_0799999982 = OpConstant %float 0.0799999982
         %77 = OpConstantComposite %v4float %float_n0_00999999978 %float_0_0799999982 %float_0 %float_0
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %yoffset = OpVariable %_ptr_Function_v4float Function
        %ndx = OpVariable %_ptr_Function_int Function
         %13 = OpLoad %int %gl_PrimitiveIDIn
         %14 = OpConvertSToF %float %13
         %19 = OpVectorTimesScalar %v4float %18 %14
               OpStore %yoffset %19
               OpStore %ndx %int_0
               OpBranch %23
         %23 = OpLabel
               OpLoopMerge %25 %26 None
               OpBranch %27
         %27 = OpLabel
         %28 = OpLoad %int %ndx
         %31 = OpSLessThan %bool %28 %int_4
               OpBranchConditional %31 %24 %25
         %24 = OpLabel
         %41 = OpLoad %int %ndx
         %43 = OpAccessChain %_ptr_Input_v4float %gl_in %41 %int_0
         %44 = OpLoad %v4float %43
         %48 = OpFAdd %v4float %44 %47
         %49 = OpLoad %v4float %yoffset
         %50 = OpFAdd %v4float %48 %49
         %52 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %52 %50
         %57 = OpLoad %int %ndx
         %58 = OpAccessChain %_ptr_Input_v4float %v_geom_FragColor %57
         %59 = OpLoad %v4float %58
               OpStore %v_frag_FragColor %59
               OpEmitVertex
         %60 = OpLoad %int %ndx
         %61 = OpAccessChain %_ptr_Input_v4float %gl_in %60 %int_0
         %62 = OpLoad %v4float %61
         %66 = OpFAdd %v4float %62 %65
         %67 = OpLoad %v4float %yoffset
         %68 = OpFAdd %v4float %66 %67
         %69 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %69 %68
         %70 = OpLoad %int %ndx
         %71 = OpAccessChain %_ptr_Input_v4float %v_geom_FragColor %70
         %72 = OpLoad %v4float %71
               OpStore %v_frag_FragColor %72
               OpEmitVertex
         %73 = OpLoad %int %ndx
         %74 = OpAccessChain %_ptr_Input_v4float %gl_in %73 %int_0
         %75 = OpLoad %v4float %74
         %78 = OpFAdd %v4float %75 %77
         %79 = OpLoad %v4float %yoffset
         %80 = OpFAdd %v4float %78 %79
         %81 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %81 %80
         %82 = OpLoad %int %ndx
         %83 = OpAccessChain %_ptr_Input_v4float %v_geom_FragColor %82
         %84 = OpLoad %v4float %83
               OpStore %v_frag_FragColor %84
               OpEmitVertex
               OpEndPrimitive
               OpBranch %26
         %26 = OpLabel
         %85 = OpLoad %int %ndx
         %87 = OpIAdd %int %85 %int_1
               OpStore %ndx %87
               OpBranch %23
         %25 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support is checked before execution. Every case requires `geometryShader`; `triangle_fan` is rejected on
  portability-subset implementations that expose `VK_KHR_portability_subset` without `triangleFans` support.
- The test instance uploads fixed vertex positions and alternating white/red colors into one host-visible vertex buffer.
- The graphics pipeline uses the selected primitive topology, the generated shaders, and one RGBA8 color attachment.
- The command buffer transitions the color image for rendering, begins a render pass, binds the pipeline and vertex
  buffer, issues one draw, ends the render pass, and copies the rendered image to a host-visible buffer.
- Host validation invalidates the readback allocation and compares the result image with the reference PNG named after
  the test case leaf.
- Image comparison first uses `tcu::fuzzyCompare()` with threshold `0.0015f`; when that succeeds, it applies
  `tcu::intThresholdPositionDeviationCompare()` with per-channel threshold `(1, 1, 1, 1)` and position deviation
  `(2, 2, 2)`.

A failure means the final image no longer matches the expected topology-driven pattern. Depending on the leaf, that can
point to wrong primitive assembly, wrong adjacency handling, wrong `gl_in` length, wrong output primitive emission,
incorrect point-size handling for point output, or a shader-interface/rasterization issue that changes the colors or
positions.

## Case Pruning

### Requirement-based pruning

- All cases require the Vulkan `geometryShader` core feature.
- `triangle_fan` is not run on portability-subset implementations when `triangleFans` is unsupported.
- The point-list output path generates a `geometry_pointsize` variant and uses it only when the device supports the
  required point-size behavior. This is a point-output special case, not the main organizing principle of the test family.

### Design-based pruning

- `basic_primitive` does not attempt every possible input/output pair. It keeps the broad primitive class visible:
  points render as points, line-like inputs render as line strips, and triangle-like inputs render as triangle strips.
- `conversion` contains the deliberate cross-primitive pairs. This keeps ordinary topology reception separate from cases
  whose purpose is conversion.
- `triangle_strip_adjacency` fixes the topology and varies only draw vertex count, so failures can be attributed to small
  vertex-count handling for that adjacency topology rather than to a broader topology matrix.

## Key Takeaways

- `geometry.input` tests whether the geometry shader receives the right primitive shape and number of input vertices for
  the selected Vulkan topology.
- The 3x output amplification is a test-visibility technique. It turns each input vertex visible in the rendered image;
  it is not production mesh subdivision.
- `basic_primitive` preserves the broad output primitive class but often uses strip output forms, because geometry-shader
  output declarations are `points`, `line_strip`, or `triangle_strip`.
- `conversion` is where the page intentionally changes primitive class, such as triangles to points or points to
  triangles.
- The pass/fail decision is ultimately image comparison against reference PNGs, so geometry input mistakes become visible
  pixel differences.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Source implementation file | [vktGeometryInputGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1) | Primary source used as navigation evidence for the rewrite. |
| Input test instance data | [GeometryInputTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L85-L110) | Defines fixed positions and alternating colors. |
| Support checks | [GeometryExpanderRenderTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L134-L147) | Requires geometry shader support and handles triangle-fan portability-subset rejection. |
| Program generation | [GeometryExpanderRenderTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L149-L181) | Builds the generated vertex, geometry, optional point-size geometry, and fragment shaders. |
| Geometry shader body | [GeometryExpanderRenderTest::shaderGeometry()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L189-L231) | Shows generated layouts, offsets, `gl_in` loop, `EmitVertex()`, and `EndPrimitive()`. |
| Test registration | [createInputGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260-L310) | Defines the three intermediate nodes and all test case leaves. |
| Shared render path | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Creates pipeline/resources, draws, copies back, and compares the image. |
| Topology helpers | [inputTypeToGLString() and outputTypeToGLString()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306-L347) | Map Vulkan topologies to generated GLSL layout names. |
| Output-vertex helper | [calcOutputVertices()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L349-L367) | Computes the generated `max_vertices` budget. |
| Reference-image comparison | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Loads the PNG reference and applies fuzzy/position-deviation comparison. |
| Mustpass evidence | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L43-L70) | Shows default mustpass coverage for the `geometry.input` leaves. |
