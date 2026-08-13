# Understanding Brief: `tessellation.geometry_interaction.limits`

## One-Sentence Test Purpose

These tests check whether a tessellation-to-geometry pipeline can render a complete image while one selected stage property uses Vulkan's required minimum maximum value for tessellation generation, geometry output, or geometry shader invocations.

## Background Knowledge

### Required minimum maximum limits

Vulkan reports implementation limits through physical-device properties. For a maximum limit, the specification also sets a value that every conformant implementation must support. This test uses those required values directly: tessellation level 64, 32 geometry shader invocations, 256 geometry output vertices, and 1024 total geometry output components. It does not query and target a device's potentially larger values.

Why it matters here:
- A shader built at a required value must be accepted on every implementation that supports the required tessellation and geometry features.
- The three test cases select different pressure points while keeping the same rendered-grid pass condition.

### Primitive amplification through tessellation and geometry stages

A tessellation control shader writes subdivision levels for one patch. The fixed-function tessellator turns the patch into primitives, and the tessellation evaluation shader supplies each generated vertex position. A geometry shader then runs for each generated input primitive. Geometry shader instancing can run several invocations for each such primitive, and every invocation can emit a bounded triangle strip.

Why it matters here:
- Raising the tessellation level increases the number of triangles that reach the geometry stage.
- Raising the geometry invocation count multiplies work per input triangle.
- Raising the geometry output budget lets each invocation emit a longer strip. A successful image requires all of this amplified work to reach rasterization without leaving uncovered pixels.

## One Concrete Example

The representative test case is:

```text
dEQP-VK.tessellation.geometry_interaction.limits.output_required_max_geometry
```

The tessellation level stays at 5 and the geometry shader uses four invocations per input triangle. The selected flag changes the geometry limits used to build the shader: `max_vertices` becomes 112, and each invocation emits 112 vertices as 56 pairs. Those pairs form a strip containing 110 triangles. The calculation starts from the required values `maxGeometryOutputVertices = 256` and `maxGeometryTotalOutputComponents = 1024`; the generated shader chooses the total-component constraint and leaves enough room for its emitted position/color data.

Each geometry invocation receives one triangle from the tessellated quad, reconstructs the triangle's rectangular cell bounds, claims one horizontal slice, and fills that slice with alternating green and yellow strip segments. The host accepts either color, including their linear mixtures, by requiring high green and near-zero blue at every pixel.

## End-to-End Test Flow

```text
[host] select one of the three registered limit flags
[host] generate vertex, tessellation-control, tessellation-evaluation, geometry, and fragment shaders
[host] create a 256 x 256 R8G8B8A8_UNORM color attachment and host-visible readback buffer
[host] build one graphics pipeline with tessellation and geometry stages
[host] clear the attachment to black and issue vkCmdDraw for one patch
[device] tessellate the quad at level 64 or 5, according to the selected test case
[device] run 32 or 4 geometry invocations per tessellated triangle
[device] emit alternating green/yellow triangle-strip slices using the selected geometry output budget
[device] rasterize the slices into the color attachment
[host] copy the attachment to the readback buffer, wait, and invalidate the host allocation
[host] check every pixel for green >= 247 and blue <= 8; pass only if all pixels satisfy both conditions
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`GridRenderTestCase::initPrograms()` emits five GLSL ES 3.10 shaders through `SourceCollections`:

- The vertex shader writes a single origin position.
- The tessellation control shader uses one output control point and writes all inner and outer levels to either 64 or 5.
- The tessellation evaluation shader uses a quad domain, fills the viewport, and forwards an integer tessellation-grid coordinate.
- The geometry shader accepts triangles, declares either 32 or 4 invocations, and emits horizontal triangle-strip slices with a case-dependent `max_vertices` value.
- The fragment shader copies the geometry shader's flat green/yellow color to the attachment.

The source does not supply explicit `ShaderBuildOptions`, so `SourceCollections` uses the CTS baseline SPIR-V target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `R8G8B8A8_UNORM` color image | Yes | Color attachment | Geometry output is rasterized and fragment colors are written | Indirectly | Holds the observable coverage result. |
| 2D image view, render pass, and framebuffer | Yes | Graphics pipeline/render pass | Define the single-layer render target | No | Route rasterized fragments into the image under test. |
| Host-visible color buffer | Yes | Transfer destination | Receives the image-to-buffer copy | Yes | Supplies all pixels to `verifyResultLayer()`. |
| Generated shader modules | Yes | Five graphics stages | Execute the amplification and coloring path | No | Carry the selected required-limit values into the pipeline. |
| Descriptors, vertex buffers, and push constants | No | No | No | No | The draw uses no vertex attributes or descriptor-backed resources; behavior comes from generated shaders and built-ins. |

## What Is Checked

- `iterate()` requires both `FEATURE_TESSELLATION_SHADER` and `FEATURE_GEOMETRY_SHADER` before creating the graphics work.
- One draw must cover all 256 x 256 pixels with geometry-colored output. The black clear color cannot satisfy the predicate.
- `verifyResultLayer()` accepts a pixel only when its green byte is at least 247 and its blue byte is at most 8. Red and alpha do not decide pass or fail, so green, yellow, and their interpolated mixtures are valid.
- The family has one layer in all three limit cases; every pixel in that layer is checked.
- Any invalid pixel produces a red error-mask pixel and the case fails with `Image comparison failed`.

## Behavior Parameter Identification

> **Behavior parameter:** required limit target selected by the test case leaf
>
> **Candidate values:** `output_required_max_tessellation`, `output_required_max_geometry`, `output_required_max_invocations`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `output_required_max_tessellation` | Failure to compile, execute, or rasterize the tessellation-to-geometry workload at tessellation generation level 64; or a shared render/readback defect. |
| `output_required_max_geometry` | Failure to honor the required geometry output vertex/component budget while emitting the 112-vertex strip; or a shared render/readback defect. |
| `output_required_max_invocations` | Failure to compile or execute 32 geometry shader invocations per input primitive and assemble their output; or a shared render/readback defect. |

## Important Variations and Special Cases

- Only one pressure flag is enabled in each registered leaf. There is no case that combines level 64, maximum geometry output, and 32 invocations.
- `output_required_max_tessellation` uses tessellation level 64, four geometry invocations, and the default 16-vertex geometry output declaration.
- `output_required_max_geometry` uses tessellation level 5, four invocations, and a 112-vertex output strip derived from the required 256-vertex and 1024-component limits.
- `output_required_max_invocations` uses tessellation level 5, 32 invocations, and the default 16-vertex geometry output declaration.
- The source comments state that tests of implementation-defined, device-specific maxima were omitted because they would require runtime-dependent shader source generation, which conflicts with platforms that require precompiled shaders.
- The same implementation file also owns `tessellation.geometry_interaction.scatter`, but that family has separate registration and documentation because its behavioral axis is output placement rather than required limits.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Limit and scatter flags | [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L76) | Identifies the three flags used by this family and separates them from scatter behavior. |
| Required values and output-budget calculation | [`GridRenderTestCase` constructor](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L145) | Selects levels 64/5, invocations 32/4, required geometry values, and strip length. |
| Generated graphics shaders | [`GridRenderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L147-L430) | Emits all five stages and places the selected values in tessellation and geometry declarations. |
| Runtime resources and draw | [`GridRenderTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L712) | Requires features, creates the render/readback resources, records one draw, copies the result, and waits. |
| Exact image predicate | [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) | Checks every pixel's green and blue bytes and creates the error mask. |
| Host pass/fail decision | [`iterate()` result scan](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L713-L729) | Invalidates the allocation, checks the layer, and returns the CTS result. |
| Limit-family registration | [`createGeometryGridRenderLimitsTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L740-L761) | Registers the `limits` family and its three exact leaves. |
| Parent registration | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places `limits` under `tessellation.geometry_interaction`. |
| Tessellation stage semantics | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines patch subdivision and the tessellation stages used by the test. |
| Geometry output and invocation semantics | [Vulkan geometry chapter](../../../../vulkan-docs/src/chapters/geometry.adoc#geometry) | Defines input primitives, output strips, output-vertex declarations, and instanced invocations. |
| Required limit values | [Vulkan limit requirements](../../../../vulkan-docs/src/chapters/limits.adoc#limits-minmax) | Lists the required values targeted by the generated shaders. |

## Questions / Risk Points for User Audit

- Does the explanation make clear that these are required specification values, not values queried from the current device?
- Is the distinction between tessellation amplification, geometry invocation amplification, and geometry output length clear?
- Does the pass predicate clearly explain why both green and yellow output are accepted while black gaps fail?
- Is the `limits` page boundary clear despite sharing its C++ implementation with the separately registered `scatter` family?

## Conversion Notes for Final Wiki Rewrite

- Keep the three test case leaves as the behavior parameter values and copy the failure-cause table without changes.
- Use `output_required_max_geometry` for the representative geometry shader walkthrough because its longer emitted strip exposes the output-budget calculation and common slice-filling mechanism.
- Explain the other two leaves through the parameter table and behavior subsections rather than adding redundant shader walkthroughs.
- Retain the all-pixel green/blue predicate and the fact that red and alpha are not independent pass criteria.
- Move detailed source navigation to the appendix and keep the runtime section in draw order.
