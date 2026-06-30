# Understanding Brief: geometry.varying

## One-Sentence Test Purpose

This test checks whether vertex-to-geometry and geometry-to-fragment varying interfaces behave correctly when the vertex
stage produces no varying, position only, or one color varying, and when the geometry stage forwards zero, one, or two
fragment varyings.

## Background Knowledge

### What “varying” means here

A **varying** is a shader user-defined value passed from one pipeline stage to the next. In this page, examples are a color
written by the vertex shader and read by the geometry shader, then values written by the geometry shader and read by the
fragment shader. Modern GLSL expresses this with matching `out` and `in` declarations rather than the old `varying` keyword,
but the CTS test family keeps the established “varying” name for this cross-stage interface behavior.

Why it matters here:

- The test is checking whether those `out` / `in` interfaces match correctly by location.
- Geometry-shader inputs for user varyings are arrays, with one entry per input primitive vertex.
- The rendered color is the observable proof that the varying values arrived at the expected stage.

### This test is about stage interfaces, not complex geometry generation

The geometry shader always emits one triangle from a triangle input. The varying configuration changes which cross-stage
values exist and how those values are transformed into the final fragment color.

Why it matters here:

- `vertex_out_1_*` cases test data carried from the vertex shader into the geometry shader.
- `geometry_out_1` and `geometry_out_2` cases test data carried from the geometry shader into the fragment shader.
- Fallback colors make missing varyings observable instead of undefined in the generated shader logic.

### The fragment color is the observable contract

The host does not inspect varyings directly. The shaders turn interface behavior into a rendered color, and the shared render
path compares the final image against a reference PNG.

Why it matters here:

- Incorrect location matching or array handling changes the fragment color.
- Incorrect geometry-stage forwarding changes the final image even when positions are correct.
- `geometry_out_0` intentionally has no geometry-to-fragment varying and uses a constant red fragment color.

## One Concrete Example

Representative path:

```text
dEQP-VK.geometry.varying.vertex_out_1_geometry_out_2
```

This is the richest case. The vertex shader writes a color varying at location 0. The geometry shader receives that value as
an array, one entry per input triangle vertex, and writes two fragment-stage varyings:

```glsl
layout(location = 0) in highp vec4 v_geom_0[];
layout(location = 0) out highp vec4 v_frag_0;
layout(location = 1) out highp vec4 v_frag_1;

inputColor = v_geom_0[0];
v_frag_0 = inputColor * 0.5;
v_frag_1 = inputColor.yxzw * 0.5;
```

The fragment shader later reconstructs the visible color with `fragColor = v_frag_0 + v_frag_1.yxzw`. Because `v_frag_1`
was written with a `yxzw` swizzle and then read with the same swizzle, the final sum recovers the original input color.

## End-to-End Test Flow

```text
[host] register one varying test family with five explicit vertex-output / geometry-output combinations
[host] choose one VaryingTestSpec
[host] require geometryShader support
[host] generate vertex, geometry, and fragment GLSL for the selected interface combination
[host] create the shared render target, vertex buffer, graphics pipeline, and framebuffer
[host] upload three triangle-strip vertices and three distinct color attributes
[host] record one triangle-strip draw
[device] vertex shader optionally writes gl_Position and optionally writes a location-0 varying
[device] geometry shader receives a triangle, chooses input color from the varying or fallback red, and emits three vertices
[device] geometry shader optionally writes one or two fragment-stage varyings
[device] fragment shader chooses constant red, v_frag_0, or v_frag_0 + v_frag_1.yxzw
[host] copy the rendered color image to a host-visible buffer
[host] compare the image with vulkan/data/geometry/<test-name>.png
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader: generated in three forms: no-op, position-only, or position plus `layout(location = 0) out` color varying.
- Geometry shader: generated from the vertex-output and geometry-output modes; it always emits three vertices and may read
  `v_geom_0[]`, write `v_frag_0`, and write `v_frag_1`.
- Fragment shader: generated in three forms: constant red, direct `v_frag_0`, or combined `v_frag_0 + v_frag_1.yxzw`.
- Reference image: loaded by the shared render path from `vulkan/data/geometry/<test-name>.png`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer positions | yes | yes | read by vertex input | no | Supplies the triangle-strip positions for the generated triangle. |
| Vertex buffer colors | yes | yes | read by vertex input | no | Supplies distinct per-vertex colors when the vertex shader writes `v_geom_0`. |
| Color attachment image | yes | yes | written by fragment shader | copied | Holds the visible result of interface passing. |
| Host-visible color buffer | yes | copy destination | written by transfer copy | yes | Gives the host the rendered image for comparison. |
| Reference PNG | loaded by host | no | no | host-read | Defines the expected color pattern for each interface combination. |

## What Is Checked

| Case | Main check |
|------|------------|
| `vertex_no_op_geometry_out_1` | Geometry shader can synthesize fallback red and forward one fragment varying even when the vertex shader writes no outputs. |
| `vertex_out_0_geometry_out_1` | Position forwarding through `gl_in[]` works while color still comes from fallback red. |
| `vertex_out_0_geometry_out_2` | Geometry shader can write two fragment varyings even when color comes from fallback red. |
| `vertex_out_1_geometry_out_0` | Vertex-stage color varying may exist even when geometry-to-fragment varyings are absent; fragment output is constant red. |
| `vertex_out_1_geometry_out_2` | Vertex color is carried into the geometry shader, split across two fragment varyings, and recombined by the fragment shader. |

## What Failure Means

A failure suggests one of the following implementation problems:

- incorrect vertex-to-geometry interface matching for `layout(location = 0)` varyings;
- incorrect geometry-shader input array indexing for per-vertex varyings;
- incorrect geometry-to-fragment interface matching at locations 0 or 1;
- incorrect handling of shaders with absent varyings in one stage;
- incorrect swizzle or arithmetic lowering across geometry and fragment stages;
- incorrect shared render output despite correct interface declarations.

## Important Variations and Special Cases

- `VERTEXT_NO_OP` emits an intentionally empty vertex shader body. The geometry shader therefore uses hard-coded positions and
  fallback red input color.
- `VERTEXT_ZERO` writes `gl_Position` but no user varying. The geometry shader uses `gl_in[]` positions and fallback red color.
- `VERTEXT_ONE` writes both `gl_Position` and `v_geom_0`; the geometry shader uses the per-vertex color from `v_geom_0[]`.
- `GEOMETRY_ZERO` declares no fragment-stage varyings and relies on a constant red fragment shader.
- `GEOMETRY_TWO` splits color into two varyings and uses swizzles so the fragment shader can recombine the original color.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test spec structure | [VaryingTestSpec](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L70-L75) | Defines vertex-output and geometry-output modes. |
| Input data | [GeometryVaryingTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L91-L103) | Creates three positions and three color attributes. |
| Support check | [VaryingTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L125-L128) | Requires geometry-shader support. |
| Program generation | [VaryingTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L130-L264) | Generates vertex, geometry, and fragment shader variants. |
| Registration | [createVaryingGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L273-L291) | Defines the five exact `geometry.varying` leaves. |
| Shared render path | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Renders, copies back, and invokes image comparison. |
| Reference comparison | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) | Loads and compares the expected reference PNG. |
| Mustpass leaves | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L195-L199) | Confirms default mustpass coverage for `geometry.varying`. |

## Questions / Risk Points for User Audit

- No unresolved semantic question blocks the rewrite: the five-case matrix is small and directly encoded in source.
- The representative shader walkthrough should use `vertex_out_1_geometry_out_2` because it exercises both vertex-to-geometry
  and geometry-to-fragment user varyings.
- The final page should explain the vertex and fragment shader variants in prose, but the full walkthrough can focus on the
  geometry shader because that is the Level-3 family's central stage.

## Conversion Notes for Final Wiki Rewrite

- Preserve the direct-leaf registration tree because `geometry.varying` has no intermediate nodes.
- Summarize the five cases in a table rather than writing one subsection per leaf.
- Use `vertex_out_1_geometry_out_2` for the representative geometry-shader walkthrough.
- Keep runtime execution short and refer to the shared image-reference path.
