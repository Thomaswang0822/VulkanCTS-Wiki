# Understanding Brief: geometry.instanced

## One-Sentence Test Purpose

This test family checks whether draw instancing and geometry shader invocations combine correctly: every draw instance should
produce one input point, and every geometry shader invocation for that point should produce one colored rectangle at the matching
reference position.

## Concrete Mental Model: From Many Objects to Many Points

A common graphics use of instancing is “draw many copies of the same model.” For example, a renderer can keep one shared bunny
mesh and draw many bunny instances by pairing the same mesh vertices with different per-instance transform matrices.

This test uses the same API idea, but with the smallest possible shared object:

| Common scene example | This CTS test |
|----------------------|---------------|
| Shared model mesh, such as a bunny. | Shared input geometry is one point. |
| Per-instance transform chooses where one bunny copy appears. | Per-instance position chooses where one point instance appears. |
| Output is many object copies. | Geometry shader expands each point instance into visible rectangles. |

The single-point choice is test-specific. It avoids mesh complexity so the case can focus on whether per-instance input and
geometry shader invocations multiply correctly.

Use this representative case while reading the brief:

```text
dEQP-VK.geometry.instanced.draw_4_instances_8_geometry_invocations
```

This name has two important numbers:

| Name part | Meaning |
|-----------|---------|
| `draw_4_instances` | The draw call uses four draw instances, so the vertex shader runs once for each of four per-instance positions. |
| `8_geometry_invocations` | For each input point, the geometry shader runs eight invocations. |

Expected total visible rectangles:

```text
4 draw instances × 8 geometry invocations per instance = 32 rectangles
```

The test is not checking Vulkan draw instancing alone, and it is not checking geometry shader invocations alone. It checks their
product: instance index chooses the input point; invocation index chooses one generated rectangle along that point's local pattern.

## One Concrete Example

For the case `draw_4_instances_8_geometry_invocations`, separate two uses of “vertex”:

- the **vertex input record** is one `vec4` position stored in the host-created vertex buffer;
- the **geometry output vertices** are the four vertices emitted by one geometry shader invocation to form one rectangle.

Step by step:

1. The host generates four deterministic input positions using seed `1234`.
2. The vertex buffer contains those four positions as four per-instance input records.
3. The pipeline uses `VK_VERTEX_INPUT_RATE_INSTANCE`, so the draw consumes one input record per draw instance:
   - instance 0 reads input position 0;
   - instance 1 reads input position 1;
   - instance 2 reads input position 2;
   - instance 3 reads input position 3.
4. The draw call is effectively:

```text
vkCmdDraw(vertexCount = 1, instanceCount = 4, firstVertex = 0, firstInstance = 0)
```

5. The vertex shader runs once for each draw instance and forwards that instance's input position as one point.
6. For each of the four points, the geometry shader runs eight invocations.
7. Each geometry shader invocation emits four **output vertices**, forming one small rectangle.
8. The rectangle's color and position depend on:
   - the per-instance input position;
   - `gl_InvocationID` normalized to a `modifier` from 0.0 to 1.0.
9. The host independently draws the same 32 rectangles into a CPU reference image and compares the GPU result to that reference.

## End-to-End Test Flow

```text
[host] choose numDrawInstances and numInvocations from the registered case name
[host] generate deterministic per-instance positions using seed 1234
[host] create a 128x128 RGBA8 color target and host-visible copyback buffer
[host] create a vertex buffer with one vec4 position per draw instance
[host] compile shaders; numInvocations is baked into the geometry shader layout
[host] issue vkCmdDraw with vertexCount = 1 and instanceCount = numDrawInstances
[device] vertex shader forwards the per-instance position to gl_Position
[device] geometry shader runs numInvocations times for each input point
[device] each geometry invocation emits one colored rectangle
[device] fragment shader writes the geometry-provided color
[host] copy the rendered image to a CPU-visible buffer
[host] generate a CPU reference image using the same position/color/rectangle math
[host] fuzzy-compare rendered image and reference image with threshold 0.01
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader: reads `layout(location = 0) in vec4 in_position` and writes it to `gl_Position`.
- Geometry shader: uses `layout(points, invocations = N) in`, where `N` comes from the test case name.
- Fragment shader: writes the geometry shader's `out_color` directly to the color attachment.
- CPU reference image: generated with the same formula as the geometry shader.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Per-instance vertex buffer | yes | vertex input binding 0 | read by vertex shader | no | Supplies one deterministic position per draw instance. |
| Color attachment image | yes | framebuffer attachment | written by fragment shader | copied to buffer | Holds the rendered rectangles. |
| Color copyback buffer | yes | transfer destination | written by image copy | yes | Host compares this data with the CPU reference image. |
| CPU reference image | yes | no | no | yes | Independent expected result generated from the same math. |

There are no descriptors, storage buffers, storage images, or uniforms in this test family. The important runtime inputs are the
per-instance vertex attributes and the geometry shader invocation count baked into shader text.

## What Is Checked

For every case, the host checks whether the rendered image matches the CPU reference. A correct image means:

- the draw call produced exactly the requested number of draw instances;
- per-instance vertex input advanced once per instance, not once per vertex;
- the geometry shader ran the requested number of invocations for each input point;
- `gl_InvocationID` produced the expected modifier sequence;
- each invocation emitted a rectangle at the expected position, size, and color;
- the combined set of rectangles matched the CPU reference closely enough for fuzzy image comparison.

## Understanding the Two Parameters

The registered cases are a Cartesian product:

```text
draw instances:        1, 2, 4, 8
geometry invocations:  1, 2, 8, 32, 64, 127
```

A case name follows this pattern:

```text
draw_<D>_instances_<G>_geometry_invocations
```

| Parameter | What it changes | Example effect |
|-----------|-----------------|----------------|
| `<D>` draw instances | Number of input points generated by the draw call. | `draw_4_instances` means four independent per-instance positions. |
| `<G>` geometry invocations | Number of geometry shader invocations per input point. | `8_geometry_invocations` means eight rectangles per input point. |
| Product `<D> × <G>` | Total number of rectangles expected in the image. | `4 × 8 = 32` rectangles. |

The geometry invocation count is compiled into the shader, not supplied as a uniform. That is why the test registers separate
cases for each invocation count.

## What Failure Means

Use the failing dimension to narrow the likely issue:

| Failure pattern | Likely implementation problem |
|-----------------|-------------------------------|
| Cases with higher draw-instance counts fail | Draw instancing or per-instance vertex input rate may be wrong. |
| Cases with higher geometry invocation counts fail | `maxGeometryShaderInvocations`, geometry shader invocation launch, or `gl_InvocationID` handling may be wrong. |
| Rectangle positions differ from reference | Geometry shader invocation math, vertex input delivery, or position interpolation before rasterization may be wrong. |
| Rectangle colors differ from reference | `gl_InvocationID`-derived modifier or fragment color forwarding may be wrong. |
| Only high counts such as 64 or 127 are unsupported | The device limit may legitimately reject the case through `maxGeometryShaderInvocations`. |

## Important Variations and Special Cases

- The `1`, `2`, `8`, and `32` invocation cases are described in the source as required by the Vulkan specification.
- The `64` and `127` invocation cases are attempted when supported by the device limit.
- Every case uses the same 128x128 RGBA8 render target and the same fixed seed for per-instance positions.
- The rendered image may contain overlapping rectangles; the CPU reference uses the same order and math, so overlap is expected
  rather than an ambiguity.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters | [TestParams](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58-L62) | Stores draw-instance and geometry-invocation counts. |
| Vertex input rate | [makeGraphicsPipeline()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L94-L105) | Configures `VK_VERTEX_INPUT_RATE_INSTANCE`. |
| Draw call | [draw()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L135-L203) | Binds the per-instance buffer and issues the instanced draw. |
| Deterministic positions | [generatePerInstancePosition()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L205-L220) | Generates reproducible input points from seed `1234`. |
| CPU reference | [generateReferenceImage()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L245-L269) | Mirrors the geometry shader rectangle math. |
| Shader generation | [initPrograms()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271-L363) | Generates vertex, geometry, and fragment shaders. |
| Test execution and compare | [test()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365-L407) | Creates resources, renders, copies back, and fuzzy-compares. |
| Support check | [checkSupport()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409-L417) | Requires geometry shader support and enough invocation limit. |
| Registration matrix | [createInstancedRenderingTests()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423-L454) | Builds all `draw_<D>_instances_<G>_geometry_invocations` cases. |

## Questions / Risk Points for User Audit

Resolved by source inspection:

- The two numbers in the case name are independent multipliers: draw instances and geometry shader invocations.
- The expected visible count is their product.
- The geometry invocation count is shader layout state, so separate generated shaders are expected.
- Validation is image-based, not counter-based.

No open audit questions remain for the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Use `draw_4_instances_8_geometry_invocations` as the concrete mental model and representative shader walkthrough.
- Keep the parameter matrix compact: the two dimensions and their product are the important idea.
- Explain runtime validation through shader/reference lockstep and fuzzy image comparison.
- The final page can proceed because this brief has no open audit questions.
