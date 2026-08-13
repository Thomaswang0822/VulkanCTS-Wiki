# Understanding Brief: clipping

## One-Sentence Test Purpose

This test file verifies fixed clip-volume behavior (inside, outside, depth clamp, depth clip, large points, wide lines), shader-defined `gl_ClipDistance[]` and `gl_CullDistance[]` behavior across stage and indexing combinations, clip-distance complementarity through blending, and a cull-distance half-space corner case.

## Background Knowledge

### Clip volume and primitive clipping

After vertex processing, the GPU clips each primitive against the half-space clip volume defined by the viewport and depth range. Primitives fully inside are drawn; primitives fully outside are discarded; primitives intersecting a clip boundary are cut so only the inside portion remains. The depth range defines near and far clip planes at `z=0` and `z=1` in clip-space depth.

Why it matters here:
- The `clip_volume.inside` cases draw primitives at `z` values inside the depth range and expect rendered output.
- The `clip_volume.outside` cases draw primitives beyond the depth range and expect a completely black framebuffer.

### Depth clamp

When `depthClampEnable` is set in pipeline state, fragments whose depth would fall outside `[0,1]` are clamped to the nearest bound instead of being clipped. This lets primitives that straddle the near or far plane still render in the region that would otherwise be empty.

Why it matters here:
- The `depth_clamp` cases toggle `depthClampEnable` on and off for primitives intersecting near (`z=-0.5`) or far (`z=0.5` with slope) clip planes.
- With clamp disabled, the intersecting portion is clipped away; with clamp enabled, the intersecting portion is clamped and rendered in a distinct color.

### Explicit depth clip control

`VK_EXT_depth_clip_enable` allows decoupling depth clamp from depth clipping. `depthClipEnable=true` clips primitives outside the depth range even when depth clamp is also enabled. This separates the two behaviors that are normally linked.

Why it matters here:
- The `depth_clip` cases test with `depthClipEnable` explicitly set, including the combination where depth clamp is enabled but depth clip is also enabled.

### User-defined clip and cull distances

Shaders can declare `gl_ClipDistance[]` and `gl_CullDistance[]` arrays as `gl_PerVertex` built-ins. Each component defines a half-space: a negative value means the vertex is outside that half-space. If all vertices of a primitive have negative `gl_ClipDistance[i]`, the primitive is clipped. If all vertices have negative `gl_CullDistance[i]`, the primitive is culled entirely (no rasterization). Values can be read back in the fragment shader.

Why it matters here:
- The `user_defined` family generates shaders that write these arrays with clip-plane counts 1 through 8, optionally combined with cull-plane counts.
- Static versus dynamic indexing changes how the shader accesses array elements.
- Fragment-shader-read cases verify that `gl_ClipDistance[]` and `gl_CullDistance[]` values are correctly interpolated and readable.

### Complementarity

If two identical primitive sets have opposite `gl_ClipDistance` signs, the clipped regions of one set should exactly fill the gaps left by the other. With additive blending, both sets together should produce a uniform half-intensity image with no gaps or overlaps.

Why it matters here:
- The `complementarity` cases generate two primitive sets with random clip distances and flipped signs, blend them, and require every pixel in the framebuffer to be gray (0.5).

## One Concrete Example

Consider `clip_volume.depth_clamp.triangle_list`. The test draws a triangle strip that straddles the near clip plane at `z=-0.5`. In one sub-case, `depthClampEnable` is false: the clipped portion vanishes, leaving black pixels in the left half. In the next sub-case, `depthClampEnable` is true: the straddling portion is clamped to the near plane and drawn in red. The test counts red pixels in the expected region and requires enough to pass.

This is conceptual shorthand; the actual vertices and expected counts depend on the topology.

## End-to-End Test Flow

[host] Select the test family, topology, clip/cull counts, indexing mode, and shader-stage combination.

[host] Check device features: geometry shader for adjacency topologies, depth clamp, depth clip enable, large points, wide lines, shader clip/cull distance, tessellation, and triangle-fan portability-subset.

[host] Generate GLSL 4.50 shaders for the selected stages. For user-defined cases, declare `gl_ClipDistance[]` and `gl_CullDistance[]` in `gl_PerVertex` with the selected counts and assign values using static or dynamic indexing.

[host] Build the pipeline with the selected state (depth clamp, depth clip, blend, point size, line width), draw the primitives, and read back the framebuffer.

[device] Execute the vertex (and optionally tessellation, geometry) shader to compute positions and clip/cull distances. Rasterize with the clip volume applied. For user-defined cases, the fixed-function clipper clips primitives against the shader-defined half-spaces.

[host] Count pixels in color ranges within specific framebuffer regions. Compare against topology-dependent expected minimums or exact counts.

## Generated Test Artifacts and Bound Resources

### Generated shaders

- `clip_volume` cases use a simple vertex shader (`v_color.vert`) that transforms position and assigns color, plus a fragment shader that outputs `v_color`.
- `user_defined` cases generate vertex, optional tessellation-control, optional tessellation-evaluation, optional geometry, and fragment shaders. The vertex shader writes `gl_ClipDistance[]` from `v_position.y` per clip-plane bar and optionally writes `gl_CullDistance[]` from position thresholds. Fragment-shader-read cases write interpolated distance values to color channels.
- `complementarity` cases generate a vertex shader that writes the last enabled `gl_ClipDistance` from `v_position.w`, leaving earlier components at zero.
- `misc` cases generate a vertex shader with hardcoded cull-distance values where each vertex has one negative cull component but no shared negative half-space.

### Bound resources

- Vertex buffer with generated vertices.
- Color attachment for rendered output (16×16 for most cases, 128×128 for complementarity).

## What Is Checked

- `inside`: expects enough non-black pixels for the topology at three depth values.
- `outside`: expects all pixels black at two out-of-range depth values.
- `depth_clamp`: expects topology-dependent minimum colored pixels per near/far and clamp/no-clamp sub-case.
- `depth_clip`: expects pixel counts consistent with explicit `depthClipEnable` state.
- `large_points`: accepts either all-black or all-expected-points depending on reported point-clipping behavior from `VK_KHR_maintenance2`.
- `wide_lines`: accepts all-black or compares against a reference draw using `tcu::intThresholdCompare()`.
- `user_defined`: expects exact black-pixel count from clip and cull regions, zero guard pixels in bottom half, and correct fragment-read color channels.
- `complementarity`: expects every pixel in the 128×128 framebuffer to be gray within a small tolerance.
- `misc`: expects exactly half (128 out of 256) pixels red in the 16×16 framebuffer.

## Behavior Parameter Identification

The primary behavioral axes are the test family and its parameter dimensions:

- `clip_volume` varies topology and depth position (inside, outside, depth clamp, depth clip, large points, wide lines).
- `user_defined` varies clip count (1–8), cull count, indexing mode (static/dynamic), shader stages (vert, vert_tess, vert_geom, vert_tess_geom), and fragment-read mode.
- `complementarity` varies clip-distance count (1–8).
- `misc` is a single case testing cull-distance half-space interaction.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `inside` | Incorrect clip-volume computation for the selected topology or depth value. |
| `outside` | Primitives not fully clipped outside the depth range. |
| `depth_clamp` | Depth clamp not applied or applied incorrectly for the selected depth/clamp combination. |
| `depth_clip` | Explicit depth clip enable/disable not handled correctly. |
| `large_points` | Point clipping behavior inconsistent with reported maintenance2 properties. |
| `wide_lines` | Wide-line clipping or expansion incorrect compared to reference. |
| `user_defined` | Shader clip/cull distance incorrectly written, interpolated, or applied by the clipper. |
| `complementarity` | Clip-distance complementarity violated: gaps or overlaps in blended output. |
| `misc` | Cull-distance culling incorrectly applied when no half-space is negative for all vertices. |

### Cause Analysis

#### Clip-volume or depth handling mismatch

**Possible failure symptoms:** Wrong pixel count in inside, outside, depth clamp, or depth clip cases.

**Possible implementation causes:** The implementation may compute the clip volume incorrectly, handle depth clamp/clip state improperly, or apply topology-specific clipping rules incorrectly. The test localizes the failure to a topology-depth combination but not to a specific pipeline stage.

#### User-defined distance mismatch

**Possible failure symptoms:** Wrong black-pixel count, guard pixels in the bottom half, or incorrect fragment-read color channels.

**Possible implementation causes:** The shader may write incorrect distance values, the fixed-function clipper may apply half-space clipping incorrectly, or fragment-stage distance interpolation may be wrong. Dynamic indexing cases isolate indexing-related issues from static ones.

#### Complementarity violation

**Possible failure symptoms:** Non-gray pixels in the blended framebuffer: black pixels (gaps) or white pixels (overlaps).

**Possible implementation causes:** The clipper may handle signed clip distances asymmetrically, or the blend configuration may interact with clipped primitives incorrectly.

#### Cull-distance half-space error

**Possible failure symptoms:** The triangle is culled when it should be drawn, or vice versa.

**Possible implementation causes:** The implementation may cull based on individual vertex cull distances rather than requiring all vertices to share a negative half-space. The test catches this specific cull-distance corner case.

## Important Variations and Special Cases

- `clip_volume.depth_clip` uses `VK_EXT_depth_clip_enable` when supported. The extension is optional; cases requiring it are pruned when absent.
- `large_points` queries `VK_KHR_maintenance2` point-clipping properties when available and accepts either all-black or all-points output depending on the reported behavior.
- `wide_lines` generates reference draws with expanded quads for pixel-level comparison using integer threshold comparison.
- `user_defined` cases with tessellation use `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`; others use `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`.
- `complementarity` uses a 128×128 framebuffer with blending enabled, while all other families use 16×16.
- `clip_distance` cases produce case names like `vert.1`, `vert.2`, ..., `vert.8` (clip-only, no cull suffix). `clip_cull_distance` cases produce `vert.1_7`, `vert.2_6`, etc., where the suffix is the cull count.
- `_dynamic_index` variants use loop-based array indexing; `_fragmentshader_read` variants read interpolated distance values in the fragment shader.

## Source Mapping

- Registration and category dispatch: `vktClippingTests.cpp#L1758-L1959`.
- Feature support: `vktClippingTests.cpp#L78-L115`, `#L416-L448`, `#L579-L583`, `#L676-L682`, `#L818-L821`, `#L956-L959`, `#L1450-L1485`.
- Vertex generation: `vktClippingTests.cpp#L117-L243`.
- Pixel counting helpers: `vktClippingTests.cpp#L247-L319`.
- Test instances: `#L451-L527` (inside), `#L530-L576` (outside), `#L585-L673` (depth_clamp), `#L684-L815` (depth_clip), `#L823-L904` (large_points), `#L961-L1081` (wide_lines), `#L1486-L1553` (user_defined), `#L1613-L1679` (complementarity), `#L1726-L1753` (misc).
- Generated shaders for user-defined: `#L1113-L1447`.
- Generated shaders for complementarity: `#L1561-L1587`.
- Generated shaders for misc cull-distance: `#L1694-L1724`.

## Conversion Notes for Final Wiki Rewrite

- Keep exact registration identifiers and preserve the distinction between test families and their intermediate nodes.
- The `user_defined` family has the richest shader generation; a representative shader walkthrough should focus on its vertex shader writing `gl_ClipDistance[]` with bar-based assignment.
- The `clip_volume` family uses no generated shaders beyond the simple position/color vertex shader; its behavior is driven by pipeline state and vertex positions.
- If a shader walkthrough is included, its complete generated `#### SPIR-V` subsection must remain the final subsection of the walkthrough.
