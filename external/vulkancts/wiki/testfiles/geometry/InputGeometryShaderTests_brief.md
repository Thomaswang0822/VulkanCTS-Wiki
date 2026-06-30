# Understanding Brief: geometry.input

## One-Sentence Test Purpose

This test checks whether geometry shaders correctly receive Vulkan input primitive topologies, including adjacency and
primitive-conversion cases, and whether the resulting emitted geometry matches the expected rendered image.

## Background Knowledge

### Geometry shader input and output topology are separate choices

A geometry shader declares the primitive shape it receives with an input layout such as `points`, `lines`,
`triangles`, `lines_adjacency`, or `triangles_adjacency`. It separately declares the primitive stream it emits with an
output layout such as `points`, `line_strip`, or `triangle_strip`.

Why it matters here:

- The input assembly topology selected in the graphics pipeline must match the geometry shader's declared input layout.
- The test family deliberately pairs some input topologies with different output topologies to test primitive conversion.
- The shader loops over `gl_in.length()`, so adjacency forms expose more input vertices per primitive than non-adjacency
  forms.

### The rendered image is the observable result

These tests do not read back a buffer containing per-primitive records. Instead, they draw a small colored primitive
pattern into a color attachment and compare the resulting image with a reference PNG.

Why it matters here:

- A wrong input topology, wrong `gl_in` length, wrong adjacency handling, or wrong emit count changes the rendered shape.
- The pass/fail signal is image-based, with fuzzy and position-deviation tolerance in the shared comparison helper.

## One Concrete Example

A representative case is the `geometry.input.basic_primitive.lines_adjacency` test case leaf. Conceptually, it uses a
pipeline input topology of `VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY`, generates a geometry shader with:

```glsl
// Conceptual reconstruction from the generated shader.
#extension GL_EXT_geometry_shader : require
layout(lines_adjacency) in;
layout(line_strip, max_vertices = 12) out;

void main(void)
{
    for (int ndx = 0; ndx < gl_in.length(); ndx++)
    {
        gl_Position = gl_in[ndx].gl_Position + offset0 + yoffset;
        EmitVertex();
        gl_Position = gl_in[ndx].gl_Position + offset1 + yoffset;
        EmitVertex();
        gl_Position = gl_in[ndx].gl_Position + offset2 + yoffset;
        EmitVertex();
        EndPrimitive();
    }
}
```

The important behavior is not the exact offsets; it is that every geometry-shader input vertex is expanded into three
emitted vertices. For `lines_adjacency`, `gl_in.length()` is four, so `max_vertices` is `4 * 3`.

## End-to-End Test Flow

```text
[host] register one input test family with basic_primitive, triangle_strip_adjacency, and conversion children
[host] choose one PrimitiveTestSpec containing pipeline input topology, registered leaf name, and GS output topology
[host] require geometryShader support; reject triangle_fan on portability-subset devices without triangleFans support
[host] generate vertex, geometry, and fragment GLSL; add a point-size geometry variant for point-list output
[host] create a 256x256 RGBA8 color attachment, render pass, framebuffer, vertex buffer, and graphics pipeline
[host] upload fixed vertex positions and alternating white/red vertex colors
[host] record a render pass, bind pipeline and vertex buffer, and issue one draw using the selected vertex count
[device] vertex shader forwards position and color
[device] geometry shader receives primitives through gl_in, emits offset copies, and ends each generated primitive
[device] fragment shader writes the forwarded color into the color attachment
[host] copy the color attachment to a host-visible buffer and invalidate it
[host] compare the image against vulkan/data/geometry/<test-name>.png with fuzzy and position-deviation checks
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader: forwards `a_position` to `gl_Position` and `a_color` to the geometry shader.
- Geometry shader: generated per input/output topology pair; it declares the geometry input layout with
  `inputTypeToGLString()`, declares the output layout with `outputTypeToGLString()`, sets `max_vertices` from
  `calcOutputVertices()`, then emits three offset vertices for each `gl_in` entry.
- Optional geometry shader variant: `geometry_pointsize` is generated when output topology is point list, so devices that
  support geometry point size can write `gl_PointSize`.
- Fragment shader: writes the color forwarded by the geometry shader.
- Reference image: loaded from `vulkan/data/geometry/<test-name>.png` during validation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read | no | Supplies fixed positions and alternating colors used to reveal topology handling. |
| Color attachment image | yes | yes | written | copied | Holds the rendered observable output. |
| Host-visible color buffer | yes | no | copy destination | yes | Receives the color attachment contents for image comparison. |
| Reference PNG | loaded by host | no | no | host-read | Defines expected rendered output for each registered leaf. |

## What Is Checked

- The rendered image must match the per-test reference image.
- The comparison first uses `tcu::fuzzyCompare()` with threshold `0.0015f`.
- If fuzzy comparison succeeds, `tcu::intThresholdPositionDeviationCompare()` allows a per-channel threshold of
  `(1, 1, 1, 1)` and position deviation `(2, 2, 2)`.
- Mustpass coverage includes:
  - 9 `basic_primitive` leaves;
  - 13 `triangle_strip_adjacency.vertex_count_*` leaves;
  - 6 `conversion` leaves.

## What Failure Means

A failure suggests that the implementation may mishandle one of the geometry-shader input paths exercised by the leaf:

- incorrect mapping from Vulkan primitive topology to geometry-shader input layout;
- wrong adjacency vertex availability or `gl_in.length()` behavior;
- incorrect geometry shader emission for point, line-strip, or triangle-strip output;
- wrong primitive-conversion behavior between input topology and emitted output topology;
- incorrect point-size behavior for point-list output when the point-size variant is selected;
- rasterization or shader-interface behavior that changes the expected color pattern.

## Important Variations and Special Cases

- `basic_primitive` covers the ordinary topology set: points, lines, line strips, triangles, triangle strips, triangle
  fans, and selected adjacency forms.
- `triangle_strip_adjacency` sweeps input vertex counts from `0` through `12` while keeping the input topology fixed to
  `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY`.
- `conversion` pairs one input topology with a different output topology, such as `triangles_to_points` or
  `points_to_triangles`.
- Triangle fans have a portability-subset support caveat: devices exposing `VK_KHR_portability_subset` can reject the
  relevant leaf if `triangleFans` is not supported.
- Point-list output has an optional `geometry_pointsize` shader variant, selected at runtime only if the binary exists
  and point-size support is available.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Old source-navigation page | [vktGeometryInputGeometryShaderTests.md](vktGeometryInputGeometryShaderTests.md) | Inventory of registered groups, parameters, support checks, and delegated helpers. |
| Input test instance data | [GeometryInputTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L85) | Defines the fixed position/color pattern rendered by all leaves. |
| Support gating | [GeometryExpanderRenderTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L134) | Requires geometry shader support and handles triangle-fan portability-subset rejection. |
| Shader generation | [GeometryExpanderRenderTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L149) | Emits the vertex, geometry, optional point-size geometry, and fragment programs. |
| Generated geometry shader body | [GeometryExpanderRenderTest::shaderGeometry()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L189) | Shows layout selection, `max_vertices`, `gl_in` iteration, `EmitVertex()`, and `EndPrimitive()`. |
| Registration arrays | [createInputGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260) | Defines `basic_primitive`, `triangle_strip_adjacency`, and `conversion` leaves. |
| Shared render/verification flow | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71) | Builds the pipeline, draws, copies the color image back, and invokes image comparison. |
| Topology and max-vertex helpers | [inputTypeToGLString()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306) | Converts Vulkan topologies into GLSL geometry input declarations. |
| Image comparison | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412) | Loads the reference PNG and applies fuzzy/position-deviation comparison. |
| Mustpass leaves | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L43) | Confirms the registered leaves included in the default mustpass list. |

## Questions / Risk Points for User Audit

- Is it acceptable to describe the validation as primarily image-based, with shader/topology errors inferred through image
  mismatch rather than direct buffer inspection?
- Should the final rewrite include one compact shader walkthrough for `lines_adjacency`, or would a `triangles_to_points`
  conversion case be more representative?
- The point-size variant is generated conditionally for point-list output and selected only when point-size support is
  present; confirm whether this should be highlighted in the final page or kept as a short special case.
