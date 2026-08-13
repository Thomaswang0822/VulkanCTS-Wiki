# Understanding Brief: `tessellation.misc_draw`

## One-Sentence Test Purpose

This test family checks whether tessellation produces the expected draw results across coverage, overlap, isoline, instancing, incomplete-patch, state-switch, and control-barrier cases.

## Background Knowledge

### Tessellation domains, levels, and patch discard

A patch enters the tessellation control shader as a fixed number of control points. The control shader writes inner and outer levels. The fixed-function tessellator converts those levels into coordinates in a triangle, quad, or isoline domain, and the tessellation evaluation shader maps each coordinate to a position. The spacing mode controls how floating-point levels become segment counts and positions. Vulkan requires triangle and quad domains to be covered without overlap, and discards a patch when any relevant outer level is zero or negative.

Why it matters here:

- Fill cases use rendered images to detect gaps or overlap in the generated domain.
- No-patch cases submit too few vertices for one patch and expect no fragments.
- State-switch cases make a second draw depend on newly bound tessellation state instead of state from an earlier draw.

Specification basis: [domain coordinates and origin](../../../../vulkan-docs/src/chapters/tessellation.adoc#L121-L159), [patch discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178), [spacing](../../../../vulkan-docs/src/chapters/tessellation.adoc#L181-L220), and the [triangle and quad coverage guarantees](../../../../vulkan-docs/src/chapters/tessellation.adoc#L355-L389).

### Draw state and reference images

A graphics draw uses the pipeline or shader state bound at that point in the command buffer. Two images can expose stale state: render one image directly with the intended second state, then render another after an offscreen draw with different state and switch to the intended state. The images should match.

Why it matters here:

- Switch cases compare an independent reference against the second draw after changing primitive mode, spacing, domain origin, or tessellation-control output count.
- Monolithic pipelines, fast-linked pipeline libraries, and shader objects exercise different state construction or binding paths while keeping the expected image unchanged.

## One Concrete Example

Consider `dEQP-VK.tessellation.misc_draw.fill_overlap_quads_equal_spacing_draw`.

The host uploads one quad and one set of tessellation levels. The control shader forwards four control points and writes those levels. The evaluation shader bilinearly maps `gl_TessCoord` into the quad. It gives successive bands of the domain red, green, or blue colors based on the two inner levels. If generated triangles overlap incorrectly, rasterization can replace a band with a neighboring band's color. The host compares the 256 by 256 result against the matching PNG at a fuzzy threshold of `0.002`.

This color pattern converts an overlap error into a visible image mismatch without depending on the implementation-defined order of generated primitives.

## End-to-End Test Flow

```text
1. Fill, overlap, and isoline cases
[host] choose primitive type, spacing mode, and direct or indirect draw
[host] upload patch positions and one of three rounded tessellation-level sets
[host] load generated shaders and a PNG reference for that level set
[host] submit one patch draw and copy the color attachment to a host-visible buffer
[device] tessellate the selected domain and render the generated primitives or isolines
[host] compare every rendered level set with its reference; all three must match

2. Instancing and no-patch cases
[host] bind per-vertex and per-instance position buffers
[host] submit either four instances of a complete patch or two vertices, which cannot form a patch
[device] render four translated patches or produce no tessellated primitive
[host] copy the image and compare it with a software reference or a cleared image

3. Tessellation-state switch cases
[host] build two state variants and an independent monolithic reference pipeline for the second variant
[host] render the reference with the second variant
[host] draw the first variant offscreen, bind the second variant, then draw onscreen
[device] use the second primitive mode, spacing, domain origin, or output count for the visible draw
[host] compare reference and result images with a per-channel threshold

4. Tessellation-factor barrier regression
[host] load the Amber program and submit many instanced quad patches
[device] delay selected vertex work, execute a tessellation-control barrier, discard most patches with zero outer levels, and retain the final wave's patches
[host] require every framebuffer pixel to equal the expected green value
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initCommonPrograms()` generates a vertex shader, a tessellation control shader that reads levels from an SSBO, and a pass-through fragment shader. Three evaluation-shader builders provide fill-cover, fill-overlap, and isoline behavior.
- `TessStateSwitchCase::initPrograms()` generates two tessellation control and two tessellation evaluation modules so the first and second draw can use different state. It can add a geometry shader.
- `TessInstancedDrawTestCase::initPrograms()` generates a four-stage pipeline for complete-patch instancing and incomplete-patch draws.
- `tess_factor_barrier_bug.amber` supplies a separate regression program with a tessellation-control `barrier()` and a large instanced draw.
- The ordinary generated GLSL uses the `vk::SourceCollections` default target, so the selected shader walkthrough targets SPIR-V 1.0.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Patch vertex buffer | yes | yes | read | no | Defines triangle, quad, or isoline control points. |
| Tessellation-level SSBO | yes | yes, set 0 binding 0 | read | no | Supplies each of three level sets used by fill and isoline cases. |
| Indirect-command buffer | yes | yes for `_draw_indirect` | read | no | Makes indirect and direct submission describe the same patch. |
| Per-instance position buffer | yes | yes, vertex binding 1 | read | no | Places four patch instances at four image locations. |
| Color attachment | yes | yes | written | copied out | Holds the observable draw result. |
| Host-visible pixel buffer | yes | yes as transfer destination | written by copy | yes | Supplies pixels to CTS image comparators. |
| State-switch push constant | yes | yes | read | no | Moves the first result draw offscreen and leaves the second onscreen. |
| Amber storage buffer | yes | yes, set 0 binding 0 | atomically updated | no | Delays selected work to increase exposure of the barrier regression. |

## What Is Checked

- Fill-cover, fill-overlap, and isoline cases render three tessellation-level sets. Each image must match its PNG reference through `tcu::fuzzyCompare()` with threshold `0.002`; all three must pass.
- Instanced cases must match a software reference containing four magenta patches. No-patch cases must match the black clear image. Their fuzzy threshold is `0.05`.
- State-switch cases compare the second draw after a state change with a direct reference draw. `tcu::floatThresholdCompare()` permits `0.005` for RGB and no alpha difference.
- The Amber regression requires every pixel in its 128 by 128 framebuffer to equal RGBA `(128, 255, 128, 255)`.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group
>
> **Candidate values:** `fill_cover`, `fill_overlap`, `isolines`, `no_patches`, `instances`, `state_switch`, `tess_factor_barrier_bug`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fill_cover` | Incomplete triangle or quad domain coverage, incorrect tessellation coordinates, or a direct/indirect draw mismatch. |
| `fill_overlap` | Overlapping generated triangles, incorrect band coordinates, or a direct/indirect draw mismatch. |
| `isolines` | Incorrect isoline count, segmentation, coordinate generation, spacing behavior, or direct/indirect draw handling. |
| `no_patches` | An incomplete patch incorrectly reaches tessellation or rasterization. |
| `instances` | Per-instance input or instance count is applied incorrectly before tessellation. |
| `state_switch` | The visible draw uses stale or incorrect tessellation state after the first draw. |
| `tess_factor_barrier_bug` | Tessellation-control synchronization or zero/nonzero tessellation-factor handling discards patches that should render. |

## Important Variations and Special Cases

- Fill and isoline cases cover `equal_spacing`, `fractional_even_spacing`, and `fractional_odd_spacing`, with direct and indirect draws. Triangles and quads apply to fill cases; isolines have their own six leaves.
- State-switch cases change one of four axes in both directions: triangle versus quad primitive mode, lower-left versus upper-left domain origin, the three spacing modes, or three versus four tessellation-control outputs. Each switch runs with and without a geometry shader and under monolithic, fast-linked-library, and shader-object construction.
- The generator excludes same-to-same state pairs because they do not test a change. It also excludes isolines from the state-switch matrix.
- Non-default domain origin requires `VK_KHR_maintenance2`; geometry variants require `geometryShader`; construction variants use their specific support checks.
- `tess_factor_barrier_bug` is absent from Vulkan SC builds and requires `tessellationShader` and `vertexPipelineStoresAndAtomics`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Fill and isoline runtime | [`runTest()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L138-L361) | Uploads levels, issues draws, reads images, and applies the `0.002` comparison. |
| Fill and isoline shaders | [`initCommonPrograms()` and evaluation builders](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L363-L594) | Defines generated behavior for coverage, overlap, and isolines. |
| State-switch path | [`TessStateSwitchCase` and `iterate()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L636-L1100) | Builds paired programs, draws the independent reference, and compares images. |
| Instanced and no-patch path | [`TessInstancedDrawTestCase` and `iterate()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1224-L1481) | Generates shaders, chooses complete or incomplete patch draws, and compares output. |
| Registration matrix | [`createMiscDrawTests()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2084) | Generates leaves and delegates the barrier regression to Amber. |
| Barrier regression | [`tess_factor_barrier_bug.amber`](../../../data/vulkan/amber/tessellation/tess_factor_barrier_bug.amber#L1-L132) | Defines the barrier, discard pattern, draw size, and expected framebuffer. |
| Mustpass coverage | [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L237-L343) | Confirms all 107 `misc_draw` leaves in the default Vulkan mustpass list. |

## Questions / Risk Points for User Audit

- Does `behavioral group` capture the useful failure axis despite being encoded as test-name prefixes rather than intermediate registered nodes?
- Is one fill-overlap shader walkthrough enough when runtime prose separately explains state switching and the Amber barrier path?
- Are the three image comparison tolerances distinguished clearly?

The inspected source, specification, Amber program, registration function, and mustpass list resolve these questions for the rewrite. No semantic blocker remains.

## Conversion Notes for Final Wiki Rewrite

- Keep only tessellation-domain and state-binding prerequisites in final Background Knowledge.
- Use `fill_overlap_quads_equal_spacing_draw` for the representative walkthrough because its color bands turn overlap into a readable image signal.
- Preserve the behavior parameter as seven `###` subsections.
- Copy the Failure Cause Mapping table unchanged.
- Keep state-switch and Amber mechanics in runtime and failure sections instead of adding walkthroughs.
- Move source navigation to the final appendix.
