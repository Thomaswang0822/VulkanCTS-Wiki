# Understanding Brief: geometry.builtin_variable

## One-Sentence Test Purpose

This test family checks whether selected geometry-shader built-in variables carry the correct values across the vertex, geometry,
and fragment stages, including point size, input primitive ID, output primitive ID, and an HLSL geometry-stage position path.

## Background Knowledge

### Built-in variables as stage contracts

The test is about variables whose meaning is defined by the shader interface rather than by ordinary user attributes:

| Built-in | Direction in this test | What the implementation must preserve |
|----------|------------------------|----------------------------------------|
| `gl_PointSize` | geometry shader output | The geometry stage can set the rasterized point size when the feature is enabled. |
| `gl_PrimitiveIDIn` | geometry shader input | The geometry stage sees the correct ID for the input primitive being processed. |
| `gl_PrimitiveID` | geometry shader output, fragment shader input | A value written by the geometry shader becomes the primitive ID observed during fragment shading. |
| `gl_Position` / `SV_POSITION` | vertex-to-geometry position field | The geometry shader can read input positions and append equivalent output positions. |

Why it matters here:

- The images are small and deterministic, so a wrong built-in value becomes a visible difference in size, color, or shape.
- The `in_block` and `outside_block` names describe interface style: most cases explicitly declare built-ins inside GLSL
  `gl_PerVertex` interface blocks, while the `position` case uses an HLSL `SV_POSITION` structure rather than GLSL block syntax.
- Validation is image-based against reference PNG files, not by reading back built-in values directly.

### The fixed input data

All five leaves use the same host-side input positions and secondary attribute values:

```text
positions:  (0.5, 0.0), (0.0, 0.5), (-0.7, -0.1), (-0.1, -0.7), (0.5, 0.0)
attribute:  0,          1,          2,           3,           0
```

The test changes topology, shader text, and sometimes indexed drawing, but the base data stays deliberately simple. The secondary
attribute is used as the source for `gl_PointSize` or for the value that becomes `gl_PrimitiveID`.

## One Concrete Example

Use this test case while reading the brief:

```text
dEQP-VK.geometry.builtin_variable.in_block.primitive_id
```

This is the clearest value-transfer path:

1. The host writes five point-list vertices. Each vertex has an attribute value `0`, `1`, `2`, `3`, or `0`.
2. The vertex shader forwards that attribute as `v_geom_primitiveID`.
3. The geometry shader receives one point at a time, emits a triangle, and writes:

```glsl
gl_PrimitiveID = int(floor(v_geom_primitiveID[0].x)) + 3;
```

4. The fragment shader chooses a color from `colors[gl_PrimitiveID % 4]`.
5. The host compares the rendered image with `vulkan/data/geometry/primitive_id.png`.

The important property is that the value written to `gl_PrimitiveID` in the geometry shader is not only accepted by the compiler; it
also affects the fragment shader's built-in `gl_PrimitiveID` exactly as expected.

## End-to-End Test Flow

```text
[host] select one registered leaf under geometry.builtin_variable
[host] require geometryShader; require shaderTessellationAndGeometryPointSize for point_size only
[host] generate vertex, geometry, and fragment shaders for the selected built-in variable
[host] create a 256x256 RGBA8 color attachment and a host-visible copyback buffer
[host] create a vertex buffer containing five vec4 positions and five vec4 secondary attributes
[host] for primitive_id_in_restarted only, create a uint16 index buffer containing 1, 4, 0xFFFF, 2, 1
[host] build a graphics pipeline with the topology chosen for the selected leaf
[host] clear the color attachment to opaque black and bind the pipeline and vertex buffer
[host] issue vkCmdDraw for non-indexed leaves, or vkCmdDrawIndexed for primitive_id_in_restarted
[device] vertex shader forwards positions and any leaf-specific secondary data
[device] geometry shader consumes points, lines, or triangles and exercises the selected built-in variable
[device] fragment shader writes either a forwarded color, a primitive-ID-derived color, or fixed yellow
[host] copy the rendered image into the host-visible buffer
[host] compare the result with the matching reference PNG using fuzzy and position-deviation image comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader: always GLSL. It forwards `a_position` to `gl_Position`; some leaves also forward the secondary attribute.
- Geometry shader:
  - GLSL for `point_size`, `primitive_id_in`, and `primitive_id`;
  - HLSL for `position`, using `SV_POSITION` and `TriangleStream<VSOut>`.
- Fragment shader: always GLSL. It either forwards a geometry-stage color, maps `gl_PrimitiveID` to a color table, or writes fixed
  yellow for the HLSL position leaf.
- Reference image: a preloaded PNG named after the test leaf, such as `primitive_id.png`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | vertex binding 0 | read by vertex shader | no | Supplies fixed positions and the secondary attribute used by some leaves. |
| Index buffer | only for `primitive_id_in_restarted` | index buffer | read by input assembly | no | Inserts a primitive-restart marker before the second line segment. |
| Color attachment image | yes | framebuffer attachment | written by fragment shader | copied to buffer | Makes built-in-variable behavior visible as pixels. |
| Color copyback buffer | yes | transfer destination | written by image copy | yes | Provides the rendered pixels for host-side comparison. |
| Reference PNG | loaded by host | no | no | yes | Defines the expected image for the selected leaf. |

There are no descriptors, uniforms, storage buffers, storage images, sampled images, or push constants in this test family. The
observable inputs are vertex attributes, index data for one leaf, shader built-ins, and fixed pipeline topology.

## What Is Checked

| Test case leaf | Built-in focus | Topology / draw style | Observable pass condition |
|----------------|----------------|-----------------------|---------------------------|
| `in_block.point_size` | `gl_PointSize` output from geometry shader | point list, non-indexed | Each input point is rasterized with the expected shader-written point size and white color. |
| `in_block.primitive_id_in` | `gl_PrimitiveIDIn` input to geometry shader | line strip, non-indexed | Each generated strip is colored from `gl_PrimitiveIDIn % 4`. |
| `in_block.primitive_id_in_restarted` | `gl_PrimitiveIDIn` with primitive restart | line strip, indexed with `0xFFFF` restart | Primitive IDs remain correct when an index-buffer restart splits the strip. |
| `in_block.primitive_id` | `gl_PrimitiveID` written by geometry shader and read by fragment shader | point list, non-indexed | Triangles are colored by the fragment shader using the geometry-written primitive ID. |
| `outside_block.position` | position transfer through HLSL `SV_POSITION` | triangle strip, non-indexed | The HLSL geometry shader appends the expected triangle positions, rendered as fixed yellow. |

For every leaf, the final pass/fail decision is made by comparing the rendered image with the corresponding reference PNG through
`compareWithFileImage()`.

## What Failure Means

| Failure pattern | Likely implementation problem |
|-----------------|-------------------------------|
| Only `point_size` fails | Geometry-stage point-size writes, `GL_EXT_geometry_point_size`, or the point-size feature path may be mishandled. |
| Only `primitive_id_in` fails | The geometry shader may receive incorrect `gl_PrimitiveIDIn` values for line-strip input primitives. |
| Only `primitive_id_in_restarted` fails | Primitive restart may reset, split, or number line-strip primitives incorrectly for geometry input. |
| Only `primitive_id` fails | Geometry-to-fragment propagation of `gl_PrimitiveID` may be wrong, or the compiler may mishandle writes to the built-in. |
| Only `outside_block.position` fails | The HLSL geometry shader path, `SV_POSITION` mapping, or triangle stream emission may be wrong. |
| All leaves fail | Common geometry-shader pipeline setup, vertex input, render/copyback, or image-comparison setup is suspect. |

## Important Variations and Special Cases

- `in_block` contains four executable leaves and uses GLSL geometry shaders. The name reflects explicit GLSL `gl_PerVertex`
  interface-block declarations in generated shader text.
- `outside_block` contains only `position`. It is special because the geometry shader is generated as HLSL and expresses position
  with `SV_POSITION` rather than GLSL `gl_PerVertex` syntax.
- `primitive_id_in_restarted` reuses the `primitive_id_in` shader logic but changes the draw path to indexed drawing with a
  `0xFFFF` restart index. This isolates primitive-ID behavior across a primitive-restart boundary.
- The point-size leaf has an extra feature gate: `shaderTessellationAndGeometryPointSize` is required in addition to
  `geometryShader`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Built-in test enum | [VariableTest](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L64-L70) | Enumerates the implemented built-in-variable modes. |
| Fixed positions and attributes | [genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L103-L132) | Defines the five shared inputs and the restart index data. |
| Indexed draw path | [drawCommand()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L161-L170) | Switches only the restarted leaf to `vkCmdDrawIndexed`. |
| Feature gates | [checkSupport()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L194-L200) | Requires geometry shaders and point-size support when needed. |
| Shader generation | [BuiltinVariableRenderTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L202-L419) | Generates the GLSL/HLSL stages for each leaf. |
| Shared render/compare path | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L202) | Creates the render target, draws, copies back, and calls the file-image comparator. |
| Reference PNG comparison | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Loads `vulkan/data/geometry/<testName>.png` and performs image comparison. |
| Registration | [createBuiltinVariableGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L428-L448) | Registers `in_block` and `outside_block` leaves. |
| Default mustpass evidence | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L15-L19) | Confirms the five executable default-list paths. |

## Questions / Risk Points for User Audit

Resolved by source inspection:

- The shared render-path uncertainty from the old page is resolved: `GeometryExpanderRenderTestInstance::iterate()` renders to a
  256x256 RGBA8 image, copies it to a host-visible buffer, and calls `compareWithFileImage()`.
- Validation uses reference PNGs named after the leaf, not a CPU formula generated inside this source file.
- The HLSL case is limited to `outside_block.position`; the other leaves use GLSL geometry shader source.
- The primitive-restart leaf changes only the draw/index path and still uses the `TEST_PRIMITIVE_ID_IN` shader behavior.

No open audit questions remain for the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Use `primitive_id` as the primary representative walkthrough because it demonstrates geometry-shader output built-in propagation
  into the fragment stage.
- Include a shorter secondary HLSL-position walkthrough or compact subsection only if the final page needs to highlight mixed
  GLSL/HLSL generation; do not over-expand it because the shader body is a simple position pass-through.
- Keep the final `Registration Hierarchy` tree at `geometry.builtin_variable` with only `in_block` and `outside_block` as direct
  children, then explain the five leaves in `## Intermediate Nodes` or a leaf-behavior table.
- Emphasize image-based reference PNG validation and the one special indexed primitive-restart path.
- The final page can proceed because this brief has no open audit questions.
