# Understanding Brief: geometry.emit

## One-Sentence Test Purpose

This test checks whether `EmitVertex()` and `EndPrimitive()` calls in a geometry shader produce the expected visible output
for point, line-strip, and triangle-strip output topologies, including no-output and multi-segment sequences.

## Background Knowledge

### `EmitVertex()` appends, `EndPrimitive()` terminates

In a geometry shader, `EmitVertex()` emits the current output values into the active output primitive. `EndPrimitive()` ends
the current strip or primitive sequence so later emitted vertices start a separate primitive. A final `EndPrimitive()` is not
required for the last emitted primitive or strip segment to exist; reaching the end of the geometry-shader invocation finishes
any remaining output stream.

Why it matters here:

- Zero `EmitVertex()` calls should produce no output even if `EndPrimitive()` is called.
- Too few emitted vertices for a line or triangle strip should not accidentally rasterize a complete primitive.
- Multiple `EndPrimitive()` calls should not create extra visible output by themselves.

### Output topology changes the minimum useful emit count

The generated shader always receives one point input, but it declares the output topology as `points`, `line_strip`, or
`triangle_strip`. The same emit/end sequence has different visibility depending on that output topology.

Why it matters here:

- One emitted vertex is enough for point output.
- Two emitted vertices are enough for a line-strip segment.
- Three emitted vertices are enough for a triangle-strip triangle.
- The two-segment cases check that a terminated first segment does not merge incorrectly with a later segment.

## One Concrete Example

Representative path:

```text
dEQP-VK.geometry.emit.triangle_strip_emit_3_end_2_emit_3_end_0
```

This case generates a geometry shader with triangle-strip output. It emits three vertices, calls `EndPrimitive()` twice, then
emits three more vertices without a final `EndPrimitive()` call. Conceptually:

```glsl
layout(points) in;
layout(triangle_strip, max_vertices = 7) out;

void main(void)
{
    emit(position0);
    emit(position1);
    emit(position2);
    EndPrimitive();
    EndPrimitive();
    emit(position3);
    emit(position4);
    emit(position5);
}
```

The important behavior is not the exact coordinates; it is that the first three vertices form one triangle, the repeated
`EndPrimitive()` does not create extra geometry, and the final three vertices form a second triangle rather than being joined
with the first segment.

## End-to-End Test Flow

```text
[host] register one emit test family with case names derived from output topology and emit/end counts
[host] choose one EmitTestSpec with output topology, segment A emit/end counts, and segment B emit/end counts
[host] require geometryShader support
[host] generate vertex, geometry, optional point-size geometry, and fragment GLSL
[host] create the shared 256x256 RGBA8 render target, vertex buffer, graphics pipeline, and framebuffer
[host] upload one point at the origin with white color
[host] record one point-list draw
[device] vertex shader forwards the point position and color
[device] geometry shader emits the requested number of fixed-position vertices and calls EndPrimitive as requested
[device] fragment shader writes the forwarded color for any rasterized output
[host] copy the rendered color image to a host-visible buffer
[host] compare the image with vulkan/data/geometry/<test-name>.png
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader: forwards the single point position and color to the geometry shader.
- Geometry shader: generated from `EmitTestSpec`; it declares `layout(points) in`, declares the requested output topology,
  sets `max_vertices` from both emit segments, emits fixed positions, and inserts the requested `EndPrimitive()` calls.
- Optional point-size geometry shader: generated only for point-output cases and writes `gl_PointSize` before emitted points.
- Fragment shader: writes the geometry shader's forwarded color.
- Reference image: loaded by the shared render path from `vulkan/data/geometry/<test-name>.png`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read by vertex input | no | Supplies the one input point and white color. |
| Color attachment image | yes | yes | written by fragment shader | copied | Holds the visible result of the emit/end sequence. |
| Host-visible color buffer | yes | copy destination | written by transfer copy | yes | Gives the host the rendered image for comparison. |
| Reference PNG | loaded by host | no | no | host-read | Defines the expected effect of each emit/end sequence. |

## What Is Checked

- Every test case leaf renders exactly the pattern expected for its topology and emit/end counts.
- Zero-emission leaves must keep the rendered image at the expected no-output reference.
- One-vertex and two-vertex leaves must not accidentally create line or triangle output where the selected topology lacks
  enough vertices.
- Two-segment leaves must show separate primitives instead of a single joined strip.
- Image comparison is performed by the shared geometry render-test path and `compareWithFileImage()`.

## What Failure Means

A failure suggests one of the following implementation problems:

- `EmitVertex()` does not append output values correctly;
- `EndPrimitive()` terminates strips incorrectly or creates extra primitives;
- repeated `EndPrimitive()` calls are mishandled;
- point, line-strip, or triangle-strip minimum vertex counts are handled incorrectly;
- strips are incorrectly joined across an `EndPrimitive()` boundary;
- `gl_PrimitiveID` or color forwarding through the geometry shader changes the visible result.

## Important Variations and Special Cases

- Point-output cases cover zero or one emitted vertex, with zero, one, or two `EndPrimitive()` calls.
- Line-strip cases cover zero, one, or two emitted vertices and include one two-segment case with `2+2` emitted vertices.
- Triangle-strip cases cover zero through three emitted vertices and include one two-segment case with `3+3` emitted vertices.
- The generated `max_vertices` value is `emitCountA + emitCountB + 1`, which gives the shader sufficient output budget for
  the selected emitted vertices.
- Point-output cases may use the optional `geometry_pointsize` variant when point-size support is available in the shared
  base class.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test spec structure | [EmitTestSpec](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L71-L80) | Defines topology and emit/end counts for both segments. |
| Input data | [GeometryEmitTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L95-L103) | Creates the single input point and white color. |
| Support check | [EmitTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L126-L129) | Requires geometry-shader support. |
| Shader generation | [EmitTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L131-L164) | Generates vertex, geometry, optional point-size geometry, and fragment shaders. |
| Geometry shader body | [EmitTest::shaderGeometry()](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L171-L221) | Emits fixed positions and inserts `EndPrimitive()` calls. |
| Registration and name generation | [createEmitGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L226-L280) | Defines the exact test case leaves and names. |
| Shared render path | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Renders, copies back, and invokes image comparison. |
| Reference comparison | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Loads and compares the expected reference PNG. |
| Mustpass leaves | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L20-L42) | Confirms default mustpass coverage for `geometry.emit`. |

## Questions / Risk Points for User Audit

- No unresolved semantic questions block the rewrite: the source directly encodes the emit/end matrix and validation uses the
  shared image-comparison path.
- The representative shader walkthrough should use `triangle_strip_emit_3_end_2_emit_3_end_0` because it covers the largest
  single-segment count, repeated `EndPrimitive()`, and a second emitted segment.
- The final page should not over-explain every leaf individually; the case-name matrix is enough when paired with topology
  and emit/end semantics.

## Conversion Notes for Final Wiki Rewrite

- Preserve the direct-leaf registration tree because `geometry.emit` has no intermediate nodes.
- Summarize leaves by output topology and sequence shape instead of writing one subsection per leaf.
- Use the representative triangle-strip two-segment shader as the only full walkthrough.
- Keep runtime execution concise because it is the same shared image-reference path as other simple geometry render tests.
