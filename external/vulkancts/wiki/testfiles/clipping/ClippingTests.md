## Overview

**Core question:** does the implementation clip primitives correctly against the fixed clip volume, apply depth clamp and explicit depth clip as configured, honor shader-written `gl_ClipDistance[]` and `gl_CullDistance[]` half-spaces across shader stages, and preserve clip-distance complementarity?

This page covers the entire `clipping` test category, implemented in one source file: [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1). That file registers four test families under the `clipping` test category:

- `clip_volume`: fixed clip-volume behavior for 10 primitive topologies at depth positions inside, outside, straddling (depth clamp), and with explicit depth clip control. Also covers large-point and wide-line clipping.
- `user_defined`: shader-defined `gl_ClipDistance[]` and `gl_CullDistance[]` across clip/cull counts (1-8), static versus dynamic indexing, four shader-stage combinations (vert, vert_tess, vert_geom, vert_tess_geom), and optional fragment-shader readback.
- `complementarity`: complementary clip-distance signs verified through additive blending on a 128x128 framebuffer.
- `misc`: a single cull-distance half-space corner case where no shared negative half-space exists.

The tests rely entirely on rendered image evidence. Pass/fail decisions come from pixel counting, color-range matching, reference-image comparison, and threshold checks, not API return values.

## Background Knowledge

- **Clip volume and primitive clipping.** After vertex processing, the GPU clips each primitive against the half-space clip volume defined by the viewport and depth range. Primitives fully inside are drawn; primitives fully outside are discarded; primitives intersecting a boundary are cut so only the inside portion remains. The depth range defines near and far clip planes at `z=0` and `z=1` in clip-space depth. The `clip_volume` family tests this fixed-function behavior with controlled vertex depth values.

- **Depth clamp.** When `depthClampEnable` is set in pipeline state, fragments whose depth would fall outside `[0,1]` are clamped to the nearest bound instead of being clipped. This lets primitives that straddle the near or far plane still render in the region that would otherwise be empty. The `depth_clamp` cases toggle this state for primitives intersecting near (`z=-0.5`) and far (`z=0.5` with slope) clip planes.

- **Explicit depth clip control (`VK_EXT_depth_clip_enable`).** This extension decouples depth clamp from depth clipping. `depthClipEnable=true` clips primitives outside the depth range even when depth clamp is also enabled. The `depth_clip` cases test both with depth clamp disabled and with depth clamp enabled, isolating the two behaviors that are normally linked.

- **User-defined clip and cull distances.** Shaders declare `gl_ClipDistance[]` and `gl_CullDistance[]` arrays as `gl_PerVertex` built-ins. Each component defines a half-space: a negative value means the vertex is outside that half-space. If all vertices of a primitive have negative `gl_ClipDistance[i]`, the primitive is clipped (cut) against that plane. If all vertices have negative `gl_CullDistance[i]`, the primitive is culled entirely (no rasterization). Fragment shaders can read interpolated distance values. The `user_defined` family exercises these arrays across indexing modes, shader stages, and counts.

- **Clip-distance complementarity.** If two identical primitive sets have opposite `gl_ClipDistance` signs, the clipped regions of one set should exactly fill the gaps left by the other. With additive blending, both sets together should produce a uniform half-intensity image with no gaps (black pixels) or overlaps (white pixels). The `complementarity` family tests this property.

## Registration Hierarchy

```text
clipping
├── clip_volume
├── user_defined
├── complementarity
└── misc
```

All four test families are implemented in [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952). There are no delegated registration-only families.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Render size | `RENDER_SIZE = 16` (16x16), `RENDER_SIZE_LARGE = 128` (128x128) | Most families use 16x16. Complementarity uses 128x128 to accommodate its blending pattern across 16 sections. | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L51-L60) |
| Clip-volume topologies | `point_list`, `line_list`, `line_list_with_adjacency`, `line_strip`, `line_strip_with_adjacency`, `triangle_list`, `triangle_list_with_adjacency`, `triangle_strip`, `triangle_strip_with_adjacency`, `triangle_fan` | Cross-cutting dimension for inside, outside, depth_clamp, and depth_clip. Adjacency topologies require geometry shader support. | [`cases[]`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1777) |
| Clip-volume z positions | Inside: `0.0`, `0.5`, `1.0`. Outside: `-0.5`, `1.5`. Depth clamp/clip: `-0.5` (near) and `0.5` with slope=1.0 (far). | Controls whether primitives are fully inside, fully outside, or straddling a clip plane. | [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L488-L505), [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L537-L550) |
| Depth clamp toggle | `depthClampEnable = false/true` | Disabled: straddling portion is clipped away. Enabled: straddling portion is clamped and rendered in a distinct color. | [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L595-L611) |
| Depth clip toggle | `depthClipEnable = false/true`, tested with depth clamp both disabled and enabled | Separates depth clip from depth clamp using `VK_EXT_depth_clip_enable`. | [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L694-L810) |
| Wide-line orientation | `LINE_ORIENTATION_AXIS_ALIGNED`, `LINE_ORIENTATION_DIAGONAL` | Lines placed just outside the clip volume in axis-aligned or diagonal directions. | [`LineOrientation`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L330-L335) |
| Clip/cull distance counts | Clip: 1-8. Cull: `min(8, 8 - numClipPlanes)`. Combined max: 8. | Controls how many half-spaces the shader writes. Cull count decreases as clip count increases. | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L56-L60), [registration](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910) |
| Indexing mode | Static indexing, dynamic loop indexing | Static: each `gl_ClipDistance[i]` assigned individually. Dynamic: loop with runtime index. Selected by `_dynamic_index` suffix. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1146-L1186) |
| Shader-stage path | `vert`, `vert_tess`, `vert_geom`, `vert_tess_geom` | Tests clip/cull distance propagation through optional tessellation and geometry stages. | [`shaderMask`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1887-L1895) |
| Fragment shader readback | Empty suffix, `_fragmentshader_read` | Without: fragment shader ignores distance arrays. With: fragment shader reads interpolated midpoint distance values into color channels. | [`fragmentShaderReads[]`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1867-L1874) |
| Complementarity clip count | Case names `1` through `8` | Number of enabled `gl_ClipDistance[]` components; only the last is assigned from `v_position.w`. | [registration](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1932-L1936) |

## Behavior Parameters

The primary behavioral axis is the test family. Each family tests a distinct clipping property.

### clip_volume: fixed clip-volume behavior

Tests whether the fixed-function clipper handles primitives correctly for each topology at controlled depth positions. The family has five intermediate nodes:

- **inside:** draws primitives at three depth values (`z=0.0`, `0.5`, `1.0`) and requires enough non-black pixels for the topology. Triangle topologies must fill the entire render area; line topologies allow some error margin; points require their specific pixel count ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L451-L527)).
- **outside:** draws primitives at `z=-0.5` and `z=1.5` and requires every pixel to remain black, confirming that primitives fully outside the clip volume are completely discarded ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L530-L576)).
- **depth_clamp:** draws primitives straddling near and far clip planes with `depthClampEnable` toggled on and off. With clamp disabled, the straddling portion is clipped (black); with clamp enabled, the straddling portion is clamped and rendered in red (near) or yellow (far). Each sub-case checks colored-pixel counts in half-frame regions against topology-specific minimums ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L585-L673)).
- **depth_clip:** uses `VK_EXT_depth_clip_enable` to explicitly enable or disable depth clipping, independent of depth clamp. Tests two passes: first with depth clamp disabled, then with depth clamp enabled. When `depthClipEnable=true`, straddling portions are clipped even if depth clamp is on ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L684-L815)).
- **clipped:** contains three test case leaves. `large_points` draws points just outside the clip volume with a point size nearly the size of the framebuffer and accepts either all-black output or all points rendered, depending on the reported `VK_KHR_maintenance2` point clipping behavior ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L823-L904)). `wide_lines_axis_aligned` and `wide_lines_diagonal` draw wide lines just outside the clip volume and either accept all-black output or compare against a reference rasterization of expanded line quads using `tcu::intThresholdCompare()` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L961-L1081)).

### user_defined: shader clip and cull distances

Tests shader-written `gl_ClipDistance[]` and `gl_CullDistance[]` across a generated matrix. The vertex shader assigns clip distances from `v_position.y` using a bar-based scheme: 8 vertical bars are drawn, and `gl_ClipDistance[barNdx]` receives `v_position.y` for bar `barNdx`, making the upper half of each bar negative (clipped). Cull distances are assigned from position thresholds ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1130-L1186)).

The test instance draws all 8 bars, counts black pixels, and checks three conditions: (1) the exact expected black-pixel count from clip and cull regions, (2) zero black guard pixels in the bottom half (detecting corruption), and (3) for `_fragmentshader_read` cases, correct interpolated distance values read back through color channels ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1486-L1553)).

The fragment-shader-readback variant uses sentinel values (0.1f, 0.2f, 0.3f, 0.4f) in the cull distance to detect whether each shader stage correctly passes the value forward or overrides it. The `checkFragColors()` helper verifies the expected sentinel chain: vertex writes 0.1f, tessellation control transforms it to 0.2f or 0.3f, and geometry transforms it to 0.4f if the chain is broken ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319)).

### complementarity: complementary clip-distance signs

Generates two identical primitive sets on a 128x128 framebuffer. The first set uses random clip distances from `v_position.w`; the second uses the negated signs. With additive blending enabled, each pixel should receive exactly one contribution from one set, producing uniform gray (0.5 intensity). The test requires every pixel to match gray within a 0.02 tolerance ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679)).

### misc: cull-distance half-space corner case

Tests a triangle strip where each of three vertices has one negative `gl_CullDistance` component, but no single half-space is negative for all vertices. Per the Vulkan specification, a primitive is culled only when all vertices share a negative `gl_CullDistance[i]` for some `i`. The test expects the triangle to be drawn and fill exactly half (128 out of 256) of the 16x16 framebuffer with red ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753)).

## Shader Analysis

The clipping category uses two distinct shader generation strategies.

**Clip-volume family.** The `clip_volume` intermediate nodes (inside, outside, depth_clamp, depth_clip, wide_lines) share a trivial vertex shader that copies `v_position` to `gl_Position` and a fragment shader that outputs `vec4(1.0, gl_FragCoord.z, 0.0, 1.0)`. The large_points variant adds `gl_PointSize` to the `gl_PerVertex` block. These shaders contain no clip-distance logic; the tested behavior is driven entirely by pipeline state and vertex positions ([`addSimplePrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L360-L397)).

**User-defined, complementarity, and misc families.** These use generated GLSL 4.50 shaders with varying complexity. The `user_defined` family has the richest generation, producing up to five shader stages per case.

The vertex shader for `user_defined` cases declares `gl_ClipDistance[]` and optionally `gl_CullDistance[]` in `gl_PerVertex`. It assigns each clip distance component using a bar index derived from `gl_VertexIndex / 6`, where bar `i` writes `v_position.y` to `gl_ClipDistance[i]` and all other components get 0.0. This creates a horizontal clip at `y=0` for the upper half of each bar. Cull distances use position thresholds: when fragment readback is disabled, `gl_CullDistance[i]` is `-0.5` for `x >= 0.75` and `0.5` otherwise. When readback is enabled and no tessellation or geometry is present, the cull distance is `-0.5` for `y < 0` and `0.5` otherwise. With tessellation or geometry present, the vertex shader writes a sentinel `0.1f` to each cull component, allowing downstream stages to detect whether the value was correctly forwarded ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1130-L1190)).

The tessellation control shader passes through positions and clip distances, and either recomputes cull distances from position thresholds or transforms the sentinel value (0.1f becomes 0.3f if geometry follows, or the correct threshold value otherwise; any other input becomes 0.2f, indicating the vertex value was wrong). The tessellation evaluation shader interpolates clip and cull distances using barycentric tessellation coordinates ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1192-L1327)). The geometry shader passes through positions and clip distances, and applies the final sentinel transformation for cull distances (0.3f or 0.1f becomes the correct threshold value; anything else becomes 0.4f) ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1329-L1408)).

The complementarity vertex shader writes only the last enabled `gl_ClipDistance` component from `v_position.w`, leaving earlier components at zero. The fragment shader outputs `vec4(1.0, 1.0, 1.0, 0.5)` for additive blending ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1561-L1602)).

The misc cull-distance vertex shader uses `gl_VertexIndex` to assign one negative cull component per vertex: `gl_CullDistance[0]` is -1.0 for vertex 2, `gl_CullDistance[1]` is -1.0 for vertex 1, `gl_CullDistance[2]` is -1.0 for vertex 0. The fragment shader outputs solid red ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1694-L1724)).

Representative shader walkthroughs are not included here because the `shader-analyzer` tool is not available in this environment. The shader generation logic described above is derived from direct source inspection of [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1113-L1448).

## Runtime Execution and Result Checking

### Resource setup and draw

- All families use `VulkanDrawContext` for rendering. The host creates a framebuffer (16x16 for most cases, 128x128 for complementarity), builds a pipeline with the selected state, and submits draw calls with generated vertices ([`genVertices()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L117-L236) for clip_volume, inline vertex construction for user_defined, complementarity, and misc).
- For `user_defined` cases with tessellation, the pipeline sets `numPatchControlPoints = 3` and uses `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`. Other cases use `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1526-L1528)).
- The `clip_volume` family generates vertices with an optional `slope` parameter. For depth_clamp and depth_clip, slope=1.0 creates a depth gradient across each primitive so it straddles the clip plane ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L654)).

### Result checking

- **inside/outside:** `countPixels()` counts black pixels and compares against topology-specific minimums (inside) or exact full-framebuffer count (outside) ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L507-L527), [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L555-L576)).
- **depth_clamp/depth_clip:** `countPixels()` with a region offset and size checks colored-pixel counts in the left half (near plane) or right half (far plane) of the framebuffer against topology-specific thresholds ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L613-L673), [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L712-L815)).
- **large_points:** accepts either all-black or all-points-rendered depending on `VK_KHR_maintenance2` point clipping behavior. When `pointClippingOutside` is true (default or `ALL_CLIP_PLANES`), both outcomes pass. When false (`USER_CLIP_PLANES_ONLY`), all points must be rendered ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L894-L904)).
- **wide_lines:** first checks for all-black output (pass). If not all-black, builds a reference image from expanded line quads using the software rasterizer (`ReferenceDrawContext`) and compares with `tcu::intThresholdCompare()` at threshold `UVec4(1)` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1022-L1081)).
- **user_defined:** checks three conditions: exact black-pixel count matching clip plus cull regions, zero guard pixels in the bottom half of the clip region, and for fragment-read cases, `checkFragColors()` verifying interpolated distance values within 0.01 tolerance ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1535-L1553)).
- **complementarity:** counts gray pixels (0.5 +/- 0.02) and requires the full 128x128 framebuffer to match ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1674-L1679)).
- **misc:** counts red pixels (1.0 +/- 0.02) and requires exactly half (128 out of 256) to match ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1745-L1753)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
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

**Possible failure symptoms:** Wrong pixel count in inside, outside, depth clamp, or depth clip cases. For inside, not enough non-black pixels are present. For outside, non-black pixels appear where the framebuffer should be entirely black. For depth clamp/clip, the colored-pixel count in the expected region falls below the topology-specific minimum.

**Possible implementation causes:** The implementation may compute the clip volume incorrectly, handle depth clamp/clip state improperly, or apply topology-specific clipping rules incorrectly. The depth_clip cases with depth clamp enabled specifically test whether `VK_EXT_depth_clip_enable` correctly overrides depth clamp. Source-level investigation is needed to determine whether the failure originates in the fixed-function clipper, the pipeline state configuration, or the rasterizer.

#### Large point or wide line clipping mismatch

**Possible failure symptoms:** For large_points, the output is neither all-black nor all-points-rendered when `pointClippingOutside` is true, or not all points are rendered when `pointClippingOutside` is false. For wide_lines, the output is not all-black and the integer threshold comparison against the reference image fails.

**Possible implementation causes:** The point clipping behavior may be inconsistent with the `VkPointClippingBehavior` reported through `VK_KHR_maintenance2`. For wide lines, the implementation may expand or clip wide lines differently from the reference rasterizer, particularly when `strictLines` is false and the implementation uses a non-perpendicular line expansion algorithm.

#### User-defined distance mismatch

**Possible failure symptoms:** Wrong black-pixel count, non-zero guard pixels in the bottom half of the clip region, or incorrect fragment-read color channels (distance values outside the 0.01 tolerance).

**Possible implementation causes:** The shader may write incorrect distance values, the fixed-function clipper may apply half-space clipping incorrectly, or fragment-stage distance interpolation may be wrong. Dynamic indexing cases isolate indexing-related issues from static ones. The sentinel-value chain in fragment-read cases (0.1f from vertex, 0.2f/0.3f from tessellation control, 0.4f from geometry) pinpoints which shader stage failed to forward the cull distance correctly. Source-level investigation is needed to determine whether the failure is in shader compilation, the clipper, or the interpolator.

#### Complementarity violation

**Possible failure symptoms:** Non-gray pixels in the blended framebuffer. Black pixels indicate gaps where neither primitive set contributed. White pixels indicate overlaps where both sets contributed.

**Possible implementation causes:** The clipper may handle signed clip distances asymmetrically, clipping more or less than expected for one sign. The blend configuration may also interact with clipped primitives incorrectly, though this is less likely since blending is a well-established fixed-function stage.

#### Cull-distance half-space error

**Possible failure symptoms:** The triangle is culled when it should be drawn (all black or too few red pixels), or the triangle is drawn but fills the wrong area (red-pixel count differs from 128).

**Possible implementation causes:** The implementation may cull based on individual vertex cull distances rather than requiring all vertices to share a negative `gl_CullDistance[i]` for some component `i`. This is a specific interpretation error of the cull-distance specification rule. Source-level investigation is needed to confirm whether the implementation applies culling per-vertex or per-half-space.

## Case Pruning

### Requirement-based pruning

- **Depth clamp feature:** `depth_clamp` cases require `features.depthClamp`. Cases are pruned via `NotSupportedError` when the feature is absent ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L579-L583)).
- **`VK_EXT_depth_clip_enable`:** `depth_clip` cases require the extension's `depthClipEnable` feature. The entire `depth_clip` family is pruned when the extension is absent ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L676-L682)).
- **Large points feature:** `large_points` requires `features.largePoints` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L818-L821)).
- **Wide lines feature:** `wide_lines_axis_aligned` and `wide_lines_diagonal` require `features.wideLines` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L956-L959)).
- **Geometry shader for adjacency topologies:** All four clip-volume sub-families (inside, outside, depth_clamp, depth_clip) require geometry shader support for adjacency topologies (`*_with_adjacency`). Cases are pruned via `NotSupportedError` when geometry shaders are unavailable ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L432-L448)).
- **Triangle fan portability subset:** Triangle fan cases are pruned when `VK_KHR_portability_subset` is present without `triangleFans` support ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430)).
- **Shader clip/cull distance features:** `user_defined` clip-distance cases require `shaderClipDistance`; cull-distance cases additionally require `shaderCullDistance`. Complementarity requires `shaderClipDistance`. Misc requires `shaderCullDistance` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1450-L1467), [complementarity](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1605-L1611), [misc](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1686-L1692)).
- **Tessellation and geometry shader features:** `user_defined` cases with `_tess` require `tessellationShader`; cases with `_geom` require `geometryShader` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1461-L1464)).
- **Device limits:** `testClipDistance()` fails (not prunes) if reported `maxClipDistances`, `maxCullDistances`, or `maxCombinedClipAndCullDistances` are below the spec minimum of 8 ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1469-L1485)).

### Design-based pruning

- **Combined clip and cull count limit:** For `clip_cull_distance` families, the cull count is computed as `min(MAX_CULL_DISTANCES, MAX_COMBINED_CLIP_AND_CULL_DISTANCES - numClipPlanes)`. When `numClipPlanes = 8`, cull count is 0, so the case name has no cull suffix (e.g., `vert.8` instead of `vert.8_0`). This is a spec-mandated constraint, not an arbitrary exclusion ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910)).

## Key Takeaways

- The `clip_volume` family separates five distinct fixed-function clipping behaviors (inside, outside, depth clamp, depth clip, clipped primitives) across 10 topologies, localizing failures to a topology-depth combination.
- The `depth_clip` cases uniquely test the decoupling of depth clamp from depth clipping via `VK_EXT_depth_clip_enable`, including the combination where both are enabled simultaneously.
- The `user_defined` family uses a bar-based vertex shader scheme to create predictable clip regions, and a sentinel-value chain through tessellation and geometry stages to detect which stage fails to forward cull distances.
- The `complementarity` family provides a strong correctness check: any asymmetry in clip-distance sign handling produces visible gaps or overlaps in the blended output.
- The `misc` case catches a specific cull-distance misinterpretation where an implementation culls based on per-vertex negative values instead of requiring a shared negative half-space across all vertices.
- All pass/fail decisions rely on rendered image evidence (pixel counts, color ranges, reference comparison, thresholds), not API return values.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and dispatch | [`addClippingTests()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952) | Registers all four test families and their parameter matrices. |
| Feature support helper | [`requireFeatures()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L78-L115) | Maps local feature flags to physical-device feature checks. |
| Test constants | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L51-L60) | Render sizes, max clip/cull distances, patch control points. |
| Vertex generation | [`genVertices()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L117-L236) | Generates topology-specific vertices for clip-volume cases. |
| Pixel counting | [`countPixels()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L247-L272) | Shared helper for color-range pixel counting. |
| Fragment color checking | [`checkFragColors()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319) | Verifies interpolated clip/cull distance values in fragment-read cases. |
| Clip-volume shaders | [`addSimplePrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L360-L397) | Trivial vert/frag shaders used by inside, outside, depth_clamp, depth_clip, wide_lines. |
| Topology support check | [`checkTopologySupport()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430) | Prunes triangle fans on portability subset without triangleFans. |
| Inside test instance | [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L451-L527) | Draws primitives at three depths, checks minimum non-black pixels. |
| Outside test instance | [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L530-L576) | Draws primitives outside clip volume, requires all-black output. |
| Depth clamp test instance | [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L585-L673) | Toggles depthClampEnable for near/far straddling primitives. |
| Depth clip test instance | [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L684-L815) | Tests explicit depthClipEnable with and without depth clamp. |
| Large points test instance | [`testLargePoints()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L823-L904) | Point clipping with maintenance2 behavior query. |
| Wide lines test instance | [`testWideLines()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L961-L1081) | Wide-line clipping with reference image comparison. |
| User-defined shader generation | [`ClipDistance::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1113-L1448) | Generates vert, tesc, tese, geom, frag shaders for clip/cull distance cases. |
| User-defined test instance | [`testClipDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1486-L1553) | Draws bars, checks black-pixel counts and fragment-read colors. |
| Complementarity shaders | [`ClipDistanceComplementarity::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1561-L1602) | Vertex shader writes last clip distance from w; fragment outputs blend color. |
| Complementarity test instance | [`testComplementarity()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679) | Two primitive sets with flipped signs, blended, expects uniform gray. |
| Misc cull-distance shaders | [`CullDistance::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1694-L1724) | Per-vertex negative cull component without shared negative half-space. |
| Misc test instance | [`testCullDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753) | Expects triangle drawn with half framebuffer red. |
| Mustpass evidence | [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L1-L308) | 308 mustpass entries across all four families. |
