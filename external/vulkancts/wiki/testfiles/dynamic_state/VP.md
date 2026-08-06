## Overview

**Core question:** When viewport and scissor state are recorded dynamically through `vkCmdSetViewport` and `vkCmdSetScissor`, does the rendered output match a software reference that applies the same viewport transform and scissor clip, including multi-viewport routing?

- [vktDynamicStateVPTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L1) implements the `vp_state` test family of the `dynamic_state` test category.
- Three logical tests, `viewport`, `scissor`, and `viewport_array`, are each registered in a vertex/fragment (plus geometry) variant and a mesh-shader variant, giving six test families. The mesh variants are excluded from Vulkan SC builds.
- `viewport` sets a viewport twice the framebuffer size and a full-size scissor; `scissor` sets a normal viewport and a half-size scissor; `viewport_array` sets four viewports and four matching scissors in a 2x2 grid and selects among them with `gl_ViewportIndex`.
- Each instance renders a green quad, builds a software reference frame that encodes the expected clipped region, and compares the two with `tcu::fuzzyCompare()`.

## Background Knowledge

- **Dynamic viewport and scissor state.** A Vulkan graphics pipeline carries viewport and scissor state statically when it is not marked dynamic. When `VK_DYNAMIC_STATE_VIEWPORT` (and the `VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT` multi-viewport form) and `VK_DYNAMIC_STATE_SCISSOR` (and `VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT`) are recorded, the pipeline is created with placeholder values and the real values are supplied per command buffer through `vkCmdSetViewport` and `vkCmdSetScissor`. The tests verify that the recorded values, not the pipeline placeholders, drive rasterization.
- **Viewport transform and scissor clip.** A viewport maps normalized device coordinates (NDC) to window coordinates by scaling and offsetting the X and Y range. A scissor further clips rasterized fragments to a rectangular region of the framebuffer. The `viewport` test exploits a viewport larger than the framebuffer to check the scaling half of the transform; the `scissor` test exploits a smaller scissor to check the clipping half; together they separate the two effects.
- **Multi-viewport and viewport index.** With the `multiViewport` core feature, an implementation supports more than one active viewport and scissor. A geometry or mesh shader writes `gl_ViewportIndex` per primitive to choose which viewport transforms that primitive. The `viewport_array` tests use four viewports arranged in a 2x2 grid and a geometry shader (vertex path) or mesh shader (mesh path) that derives `gl_ViewportIndex` from the vertex Z coordinate.

## Registration Hierarchy

```text
dynamic_state.monolithic.vp_state
├── viewport
├── scissor
├── viewport_array
├── viewport_mesh
├── scissor_mesh
└── viewport_array_mesh
```

The `vp_state` test family is registered once per pipeline construction type. The top-level `dynamic_state` dispatcher creates one child group per construction type (`monolithic`, `pipeline_library`, `fast_linked_library`, and the shader object variants), and each construction type group instantiates the same six leaves through [`DynamicStateVPTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L460-L521). The three `_mesh` leaves are generated only on non-Vulkan SC builds behind `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_*` | Top-level group above `vp_state`; selects how the pipeline is built. Does not change the dynamic-state logic. | [dispatcher](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L74-L103) |
| Shader path | vertex+fragment (no suffix), mesh (`_mesh` suffix) | Selects vertex/fragment (plus geometry for the array case) versus mesh+fragment pipeline. The mesh path requires `VK_EXT_mesh_shader`. | [init loop](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L472-L520) |
| Test logical group | `viewport`, `scissor`, `viewport_array` | The three properties under test: oversized viewport transform, half-size scissor clip, and four-viewport array routing. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L502-L518) |
| Viewport count | 1 (`viewport`, `scissor`), 4 (`viewport_array`) | Single viewport exercises the basic transform; four viewports exercise multi-viewport routing through `gl_ViewportIndex`. | [instances](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L151-L152) |
| Render dimensions | 128x128 | Fixed `WIDTH` and `HEIGHT` from the shared base class. | [base class](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L90-L91) |

The construction type is a parent of `vp_state`, so within this page the six leaves are the behavior axis and the construction type is treated as configuration.

## Behavior Parameters

The primary behavioral axis is the test logical group combined with the shader path. Each of the three logical groups appears once in the vertex path and once in the mesh path. The mesh path repeats the same dynamic-state exercise through a different pipeline, so the subsections below group the six leaves into the three logical groups and note the mesh variant where relevant.

### `viewport` and `viewport_mesh`: oversized dynamic viewport

A single viewport is set dynamically to `{0, 0, 2*WIDTH, 2*HEIGHT}` with depth range `0..0`, and the scissor is set to the full framebuffer ([setDynamicStates](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L148-L158)). The quad geometry spans NDC `-0.5..0.5` in both axes. With the doubled viewport, that NDC range maps to framebuffer coordinates `64..192`, so only the `64..127` portion lands inside the 128x128 framebuffer and survives the implicit render-area clip. The reference frame is green exactly in the top-right quadrant (NDC `0..1`) and black elsewhere ([buildReferenceFrame](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L160-L187)). The test therefore isolates the dynamic viewport scaling: if the recorded viewport is ignored, the quad fills the whole framebuffer and the comparison fails.

The `viewport_mesh` leaf repeats the same logic with a mesh-shader pipeline. Geometry is fetched from a device buffer by [`VertexFetch.mesh`](../../../data/vulkan/dynamic_state/VertexFetch.mesh) using a push-constant vertex offset, but the dynamic-state behavior under test is identical.

### `scissor` and `scissor_mesh`: half-size dynamic scissor

A single viewport is set to the full framebuffer `{0, 0, WIDTH, HEIGHT}`, and the scissor is set to `{0, 0, WIDTH/2, HEIGHT/2}` ([setDynamicStates](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L195-L205)). The quad spans NDC `-0.5..0.5`, which under the full viewport covers the central `64x64` region of the framebuffer (pixels `32..96`), but the half-size scissor (the `64x64` rectangle at the top-left framebuffer corner, since the framebuffer origin is top-left) further clips it to the `32..64` overlap on each axis. The reference frame is green in NDC `-0.5..0` on both axes and black elsewhere ([buildReferenceFrame](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L207-L234)). This isolates the dynamic scissor clip independently of viewport scaling. The `scissor_mesh` leaf repeats the same setup with a mesh-shader pipeline.

### `viewport_array` and `viewport_array_mesh`: four-viewport array with index routing

Four viewports are set dynamically in a 2x2 grid covering the framebuffer, each `WIDTH/2 x HEIGHT/2`, and four matching scissors are set to a quarter-size rectangle centered inside each viewport quadrant ([iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L316-L341)). Four quads, one per viewport, are drawn in sequence. The geometry shader ([ViewportArray.geom](../../../data/vulkan/dynamic_state/ViewportArray.geom)) or the mesh shader ([VertexFetchViewportArray.mesh](../../../data/vulkan/dynamic_state/VertexFetchViewportArray.mesh)) writes `gl_ViewportIndex = int(round(gl_Position.z * 3.0))`, deriving the viewport index from the per-quad Z coordinate packed into the vertex data (`i/3.0` for viewport `i`).

The reference frame is green across the centered square NDC `-0.5..0.5` on both axes, which is the union of the four clipped quadrant regions ([reference computation](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L375-L398)). This variant checks both `vkCmdSetViewport` with four viewports and the shader-driven `gl_ViewportIndex` selection together. The `viewport_array_mesh` leaf uses the mesh-shader pipeline and writes `gl_ViewportIndex` through `gl_MeshPrimitivesEXT[0].gl_ViewportIndex`.

## Shader Analysis

The shaders support the test rather than implement the tested property for the single-viewport cases. The vertex shader ([VertexFetch.vert](../../../data/vulkan/dynamic_state/VertexFetch.vert)) copies position and color; the fragment shader ([VertexFetch.frag](../../../data/vulkan/dynamic_state/VertexFetch.frag)) copies the interpolated color to the attachment. The dynamic viewport and scissor behavior under test is applied by fixed-function rasterization, not by the shader.

For the `viewport_array` cases the shader is part of the tested property, because `gl_ViewportIndex` selection is what routes each quad to its viewport. The geometry shader derives the index from `gl_Position.z` and emits one triangle-strip per input triangle:

```glsl
gl_ViewportIndex = int(round(gl_in[i].gl_Position.z * 3.0));
```

The mesh variant does the equivalent through `gl_MeshPrimitivesEXT[0].gl_ViewportIndex`. The Z packing (`i/3.0` for viewport `i`, rounded and multiplied back by 3) is the contract between the host vertex data and the shader that makes each quad land in its intended viewport.

No representative shader walkthrough is included. The shaders are short passthrough programs, and the behavior under test is fixed-function dynamic state plus, for the array case, a one-line index derivation that is already shown above.

## Runtime Execution and Result Checking

- Each instance constructs a pipeline with all relevant dynamic states recorded (`VK_DYNAMIC_STATE_VIEWPORT`, `VK_DYNAMIC_STATE_SCISSOR`, plus rasterization, blend, and depth-stencil states from the shared base). The pipeline is created with placeholder viewport and scissor values that the dynamic commands override ([ViewportArrayTestInstance::initPipeline](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L269-L313)).
- `iterate()` begins the render pass, calls `setDynamicStates()` to record the viewport and scissor values described above (and the other dynamic states from the base class), binds the pipeline, and records the draw. The vertex path issues one `cmdDraw` (`viewport`, `scissor`) or four `cmdDraw` calls, one per viewport (`viewport_array`); the mesh path issues `cmdDrawMeshTasksEXT` with matching counts and push-constant vertex offsets ([iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L108-L134), [array iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L343-L373)).
- After submit and wait, the rendered color image is read back and compared against a software reference frame using `tcu::fuzzyCompare()` with threshold `0.05f` ([fuzzy compare](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L125-L131)). A mismatch returns `Image verification failed`; a match returns `Image verification passed`.
- Each reference frame encodes the expected clipped region for its logical group: green in the NDC `0..1` region (`viewport`), green in the NDC `-0.5..0` region (`scissor`), or green across the centered square (`viewport_array`).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `viewport`, `viewport_mesh` | The dynamic viewport scaling was not applied, so the oversized viewport did not push most of the quad out of the framebuffer. |
| `scissor`, `scissor_mesh` | The dynamic scissor clip was not applied, so the quad was not confined to the half-size scissor. |
| `viewport_array`, `viewport_array_mesh` | The dynamic multi-viewport setup or the `gl_ViewportIndex` routing is wrong, so the four quads did not land in their intended quadrants. |
| Any `_mesh` leaf only | The mesh-shader pipeline path for the same dynamic state differs from the vertex path. |
| All leaves of one logical group | A shared dynamic-state command (`vkCmdSetViewport` or `vkCmdSetScissor`) is mishandled, or the fixed-function viewport/scissor logic is wrong. |

### Cause Analysis

#### Dynamic viewport not applied

**Possible failure symptoms:** The `viewport` (or `viewport_mesh`) comparison fails because the rendered green area extends beyond the expected NDC `0..1` region (for example, the quad's full `NDC -0.5..0.5` range becomes visible instead of just the positive-NDC half).

**Possible implementation causes:** The implementation may ignore the recorded `vkCmdSetViewport` value and fall back to the placeholder viewport baked into the pipeline, or apply a 1:1 mapping that leaves the `NDC -0.5..0.5` quad covering the whole framebuffer. Whether the defect is in command recording or in fixed-function viewport transform requires inspection against the Vulkan viewport transform contract; source-level investigation is needed to locate it precisely.

#### Dynamic scissor not applied

**Possible failure symptoms:** The `scissor` (or `scissor_mesh`) comparison fails because the rendered green area extends beyond the expected NDC `-0.5..0` region (for example, the quad's full `NDC -0.5..0.5` range becomes visible instead of just the lower half).

**Possible implementation causes:** The implementation may ignore the recorded `vkCmdSetScissor` and use the pipeline placeholder scissor, or apply the scissor at the wrong coordinate origin. The viewport is correct in this case (the quad is positioned by the viewport), so a scissor-only mismatch isolates the defect to the scissor path. Precise location requires source-level investigation.

#### Multi-viewport routing wrong

**Possible failure symptoms:** The `viewport_array` (or `viewport_array_mesh`) comparison fails because one or more of the four quadrants is empty, the wrong color, or drawn into the wrong viewport.

**Possible implementation causes:** Several distinct mechanisms can produce this. `vkCmdSetViewport` may accept four viewports but only honor the first, so all quads route to one quadrant. The `multiViewport` core feature may be advertised but not correctly wired. The shader-side `gl_ViewportIndex` derivation may be miscompiled, so the Z-to-index mapping does not match the host packing. Distinguishing these requires checking which quadrants are wrong: all-same-quadrant points at the viewport command, scrambled quadrants point at the index routing, and a single wrong quadrant may point at one viewport entry. Source-level investigation is needed to confirm which.

#### Mesh-only divergence

**Possible failure symptoms:** A `*_mesh` leaf fails while the corresponding vertex-path leaf passes.

**Possible implementation causes:** The mesh-shader pipeline may bind dynamic viewport or scissor state differently from the vertex pipeline, or the `VK_EXT_mesh_shader` primitive path may not propagate `gl_ViewportIndex` through `gl_MeshPrimitivesEXT` the same way the geometry shader path does. Because the vertex and mesh leaves share the same dynamic-state commands and reference frames, a mesh-only failure isolates the defect to the mesh-shader pipeline path. Source-level investigation is needed to locate the divergence.

## Case Pruning

### Requirement-based pruning

- The three `_mesh` leaves are excluded from Vulkan SC builds behind `#ifndef CTS_USES_VULKANSC`; they do not appear in the VKSC mustpass lists ([init guard](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L483-L490)).
- `viewport` and `scissor` (and their mesh counterparts) require no extra features beyond dynamic viewport and scissor support; their support check is a no-op ([checkNothing](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L453-L455)).
- `viewport_array` requires the `geometryShader` and `multiViewport` core features ([checkGeometryAndMultiViewportSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L436-L440)).
- `viewport_mesh` and `scissor_mesh` require `VK_EXT_mesh_shader` ([checkMeshShaderSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L442-L445)).
- `viewport_array_mesh` requires `multiViewport` plus `VK_EXT_mesh_shader` ([checkMeshAndMultiViewportSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L447-L451)). The geometry shader is not required for the mesh path because the mesh shader writes the viewport index directly.

### Design-based pruning

- The mesh path is a deliberate parity variant of the vertex path: the same dynamic-state exercise is repeated through a different pipeline to confirm the dynamic commands behave identically. It is not a separate property.
- The three logical groups are kept separate rather than combined because each isolates one effect: `viewport` isolates viewport scaling with a full scissor, `scissor` isolates scissor clipping with a neutral viewport, and `viewport_array` combines viewport count with index routing.

## Key Takeaways

- The six leaves reduce to three logical tests of dynamic state: viewport scaling (`viewport`), scissor clipping (`scissor`), and multi-viewport routing with index selection (`viewport_array`), each repeated through a mesh-shader pipeline for parity.
- Each logical group is designed so that ignoring the recorded dynamic value produces a visibly different image: the oversized viewport pushes most of the quad out of the framebuffer, the half-size scissor confines it to one quadrant, and the four-viewport array distributes four quads across four quadrants.
- Validation is a single fuzzy image comparison against a software reference frame; the reference encodes the expected clipped region, so the comparison simultaneously exercises the viewport transform, the scissor clip, and (for the array case) the viewport index routing.
- A failure that is specific to one logical group isolates the corresponding dynamic command; a mesh-only failure isolates the mesh-shader pipeline path. See `## Failure Meaning` for the cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateVPTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L460-L521) | Builds the six leaves from the vertex and mesh shader-path loop and assigns support checks. |
| Shared iterate | [`ViewportStateBaseCase::iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L83-L136) | Common render, submit, readback, and fuzzy-compare flow for the single-viewport instances. |
| Viewport instance | [`ViewportParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L138-L188) | Oversized dynamic viewport and full-size scissor setup plus top-right-quadrant reference. |
| Scissor instance | [`ScissorParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L189-L238) | Full viewport and half-size dynamic scissor setup plus bottom-left-quadrant reference. |
| Array instance | [`ViewportArrayTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L239-L435) | Four-viewport grid, matching scissors, per-viewport draws, and centered-square reference. |
| Support checks | [check functions](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L436-L455) | Feature requirements per leaf: nothing, geometry+multiViewport, mesh shader, multiViewport+mesh shader. |
| Shaders | [VertexFetch.vert](../../../data/vulkan/dynamic_state/VertexFetch.vert), [VertexFetch.frag](../../../data/vulkan/dynamic_state/VertexFetch.frag), [ViewportArray.geom](../../../data/vulkan/dynamic_state/ViewportArray.geom), [VertexFetch.mesh](../../../data/vulkan/dynamic_state/VertexFetch.mesh), [VertexFetchViewportArray.mesh](../../../data/vulkan/dynamic_state/VertexFetchViewportArray.mesh) | Passthrough vertex/fragment, viewport-index-writing geometry and mesh shaders. |
| Shared base | [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Provides `WIDTH`/`HEIGHT`, pipeline scaffolding, and the `setDynamic*State` helpers. |
