# Understanding Brief: `tessellation.geometry_interaction.scatter`

## One-Sentence Test Purpose

These tests check whether geometry shader output from many tessellated input triangles, invocations, and emitted primitives can be scattered so that it collectively covers a complete grid, including every layer of an eight-layer target.

## Background Knowledge

### Geometry shader instancing and emitted primitives

A geometry shader receives one assembled input primitive and can emit zero or more output primitives. Geometry shader instancing runs several invocations for the same input primitive; `gl_InvocationID` distinguishes them. A triangle strip continues until the shader calls `EndPrimitive()` or the invocation ends.

Why it matters here:
- All three cases use four invocations for each tessellated triangle, so each input triangle produces output from four independent executions.
- The instances case emits one continuous strip per invocation, while the primitives and layers cases call `EndPrimitive()` after each four-vertex quad.
- The destination formulas combine tessellation-grid coordinates, triangle-half identity, invocation ID, and emitted-primitive index. Correct output depends on preserving each of those identities.

### Layered rendering

A geometry shader can write `gl_Layer` to direct an output primitive to one layer of a multi-layer framebuffer attachment. Every vertex of one primitive must select the same valid layer.

Why it matters here:
- The layers case creates an eight-layer 2D-array attachment and assigns each emitted quad to a computed layer.
- The host reads and verifies every layer separately, so output routed to the wrong layer leaves a gap in one layer even if another layer receives extra geometry.

## One Concrete Example

The representative test case is:

```text
dEQP-VK.tessellation.geometry_interaction.scatter.geometry_scatter_primitives
```

One patch is tessellated at level 5 into 25 rectangular cells and 50 triangles. Each triangle launches four geometry invocations. The geometry shader identifies the original grid cell, which half of that cell supplied the triangle, and the invocation ID. Each invocation then emits four independent four-vertex quads into a 20 x 40 destination grid.

The destination mapping is a permutation of all 800 grid cells: 50 input triangles x 4 invocations x 4 emitted quads. The shader uses `EndPrimitive()` after every quad, so no strip can bridge the distant destination cells. A correct implementation fills the entire color attachment with green and yellow cells even though the tessellation evaluation shader placed the original tessellated patch in only the lower-left 0.3 x 0.3 region.

## End-to-End Test Flow

```text
[host] select instances, primitives, or layers scatter behavior from the registered test case leaf
[host] generate vertex, tessellation-control, tessellation-evaluation, geometry, and fragment shaders
[host] create a 256 x 256 R8G8B8A8_UNORM attachment with one layer or eight layers, plus a host-visible readback buffer
[host] build one graphics pipeline with tessellation and geometry stages and no descriptors or vertex attributes
[host] clear all attachment layers to black and issue one draw for one patch
[device] tessellate the patch at level 5 into a 5 x 5 grid split into 50 triangles in a small corner
[device] run four geometry invocations for every input triangle
[device] remap each invocation strip, each emitted quad, or each layered quad to its computed destination
[device] rasterize green/yellow output across the complete destination grid or every destination layer
[host] copy all image layers to the readback buffer, wait for completion, and invalidate the host allocation
[host] verify every pixel of every layer; pass only if all pixels have green >= 247 and blue <= 8
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`GridRenderTestCase::initPrograms()` generates five GLSL ES 3.10 stages:

- The vertex shader writes one position at the origin.
- The tessellation control shader uses one output control point and writes level 5 to both inner and all four outer tessellation levels.
- The tessellation evaluation shader uses a quad domain, maps the tessellated patch into the lower-left 0.3 x 0.3 clip-space region, and forwards a rounded 2D coordinate in the 5 x 5 tessellation grid.
- The geometry shader accepts triangles with four invocations. Its case-selected branch emits either one relocated 16-vertex strip, four separate relocated quads, or four separate quads with computed `gl_Layer` values.
- The fragment shader writes the geometry shader's flat green/yellow color.

No explicit `ShaderBuildOptions` are supplied, so `SourceCollections` uses the CTS baseline SPIR-V target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `R8G8B8A8_UNORM` color image | Yes | Color attachment | Rasterization and fragment shading write it | Indirectly | Contains the coverage and layer-routing result. It has one layer for instances/primitives and eight for layers. |
| 2D or 2D-array image view, render pass, and framebuffer | Yes | Graphics render target | Select the complete attachment layer range | No | The array view exposes all eight layers to layered rendering. |
| Host-visible color buffer | Yes | Transfer destination | Receives the image-to-buffer copy | Yes | Supplies every pixel and layer to `verifyResultLayer()`. |
| Generated shader modules | Yes | Five graphics stages | Execute tessellation, remapping, layer selection, and color output | No | Carry all tested scatter formulas and output topology. |
| Descriptors, vertex buffers, and push constants | No | No | No | No | The test derives all behavior from generated constants and shader built-ins. |

## What Is Checked

- `iterate()` requires both tessellation shader and geometry shader features before it creates the draw workload.
- The one-layer cases must cover all 256 x 256 pixels. The layers case must cover all pixels in each of eight layers.
- `verifyResultLayer()` accepts a pixel when its green byte is at least 247 and its blue byte is at most 8. Red and alpha are not independent pass criteria, so green, yellow, and their linear mixtures pass.
- The attachment starts black. Any uncovered destination cell therefore fails the green threshold.
- Layer misrouting fails when it leaves required coverage missing from any layer, even if another layer receives extra geometry.
- A rejected pixel is marked red in the logged error mask, and any rejected pixel makes the test case return `Image comparison failed`.
- The host does not compare exact cell ownership, checkerboard parity, red, or alpha. A placement error that preserves complete accepted-color coverage in every checked layer can escape this predicate.

## Behavior Parameter Identification

> **Behavior parameter:** scatter target selected by the test case leaf
>
> **Candidate values:** `geometry_scatter_instances`, `geometry_scatter_primitives`, `geometry_scatter_layers`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `geometry_scatter_instances` | Geometry shader invocations, `gl_InvocationID`, or continuous triangle-strip output may be misplaced or lost while each invocation writes to a distant destination slot; or the shared render/readback path may be faulty. |
| `geometry_scatter_primitives` | Separate output primitives, `EndPrimitive()`, or per-primitive destination arithmetic may be handled incorrectly while one invocation scatters four quads; or the shared render/readback path may be faulty. |
| `geometry_scatter_layers` | Separate output primitives or `gl_Layer` routing into the eight-layer framebuffer may be handled incorrectly; or the shared render/readback path may be faulty. |

## Important Variations and Special Cases

- All cases use tessellation level 5, four geometry invocations, and the same five-stage graphics pipeline.
- `geometry_scatter_instances` does not set the separate-primitives flag. Each geometry invocation emits one 16-vertex strip containing 14 triangles. The 50 input triangles and four invocations map to all 200 slots in a 5 x 40 destination grid.
- `geometry_scatter_primitives` sets the separate-primitives flag. Every invocation emits four quads, with four vertices and two triangles per quad, into all 800 cells of a 20 x 40 grid.
- `geometry_scatter_layers` uses the same four-quad emission form but creates eight image layers. Across all invocations and primitive indices, each layer receives all 100 cells in a 20 x 5 grid.
- The arithmetic multipliers and modulo operations permute source identities into distant destinations. The small `gapOffset` expands each destination rectangle to hide rasterization seams between neighboring cells.
- Only the layers case changes attachment layer count and writes `gl_Layer`. The fragment shader and host pixel predicate remain unchanged.
- The family does not register combinations of scatter modes. Each leaf selects one output-placement mechanism.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Scatter and separate-primitive flags | [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L76) | Defines the three scatter choices and the topology-changing helper flag. |
| Fixed levels, invocations, layers, and output counts | [`GridRenderTestCase` constructor](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L95-L145) | Selects level 5, four invocations, one/eight layers, 14 strip triangles, or four separate quads. |
| Generated tessellation stages | [`GridRenderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L147-L238) | Generates the small source patch and its integer grid coordinates. |
| Instances scatter branch | [`initPrograms()` instances branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L369-L390) | Relocates one continuous strip from each invocation. |
| Primitives scatter branch | [`initPrograms()` primitives branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L285-L323) | Emits and terminates four independently positioned quads per invocation. |
| Layers scatter branch | [`initPrograms()` layers branch](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L324-L368) | Computes destination cells and `gl_Layer` for eight-layer output. |
| Runtime resources, draw, and copyback | [`GridRenderTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L618-L729) | Requires features, creates one/eight-layer resources, draws, copies, and verifies. |
| Exact image predicate | [`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L616) | Checks every pixel's green and blue bytes and logs the error mask. |
| Scatter-family registration | [`createGeometryGridRenderScatterTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L764-L782) | Registers the three exact test case leaves and flag combinations. |
| Parent registration | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places `scatter` under `tessellation.geometry_interaction`. |
| Mustpass paths | [Vulkan default mustpass list](../../../mustpass/main/vk-default/tessellation.txt#L32-L34) | Confirms all three Vulkan paths; the Vulkan SC list contains the corresponding leaves. |
| Tessellation semantics | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines patch subdivision and tessellation-generated primitives. |
| Geometry invocation and output semantics | [Vulkan geometry chapter](../../../../vulkan-docs/src/chapters/geometry.adoc#geometry) | Defines multiple invocations, output strips, and emitted primitive assembly. |
| Layer selection semantics | [Vulkan `Layer` built-in](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-layer) | Defines geometry-stage routing to framebuffer layers. |

## Questions / Risk Points for User Audit

- Is it clear that "scatter" means deterministic relocation into a complete output grid, not random placement?
- Does the distinction between one strip per invocation and four separately terminated quads per invocation read clearly?
- Is the eight-layer result explained as complete coverage in every layer rather than coverage divided among layers?
- Does the pixel predicate make clear why green/yellow mixtures pass and black gaps fail?

## Conversion Notes for Final Wiki Rewrite

- Use `geometry_scatter_primitives` for the representative shader walkthrough because it exposes destination remapping and `EndPrimitive()` without adding the layers branch's extra routing dimension.
- Explain the instances and layers branches through behavior subsections and the parameter-variation table.
- Copy the failure-cause mapping table directly into the final page.
- Keep only geometry instancing, separate primitive termination, and layered output as final-page prerequisites.
- Move detailed source navigation to the appendix and keep the runtime section in draw order.
