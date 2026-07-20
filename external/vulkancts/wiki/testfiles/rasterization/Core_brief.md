# Understanding Brief: rasterization / vktRasterizationTests.cpp

This brief prepares a rewrite of the Level-3 page covering the `rasterization` category root file. The file both registers
the `rasterization` test category and implements most of its direct test families. The brief is explanation-first and uses
the source code as the primary authority.

## One-Sentence Test Purpose

This test checks whether Vulkan's fixed-function rasterizer produces fragment coverage and interpolated values that match a
host-side reference rasterizer across primitive topologies, line rasterization modes, polygon fill rules, culling, discard,
conservative rasterization, multisample rates, depth bias, and `VK_KHR_maintenance5` non-strict line behavior.

Core question: **does the implementation's rasterizer cover exactly the pixels (and only those pixels) that the Vulkan
rasterization rules permit, with the correct interpolation, fill rule, culling, conservative-rasterization mode, and depth
bias behavior for the configured pipeline state?**

## Background Knowledge

### Reference-rasterizer comparison

The implemented families compare the implementation's rendered image against a software reference rasterizer in
`tcuRasterizationVerifier`, not against a hand-curated image. The verifier computes per-pixel coverage from
floating-point vertex positions and selected subpixel precision, then flags pixels that are covered by the reference but
missing in the result, or present in the result but uncovered by the reference
[tcuRasterizationVerifier.hpp](../../../../../framework/common/tcuRasterizationVerifier.hpp#L183-L237).

Why it matters here:

- The verifier accepts an implementation that follows any valid Vulkan rasterization rule, not a single expected image.
  Strict modes narrow the accepted range; relaxed modes widen it.
- The test sends the same scene description to both the implementation and the verifier, so a failure usually means the
  implementation's coverage rule diverges from what the verifier's reference rule permits.
- For triangle, line, and point groups the verifier's `verifyTriangleGroupRasterization`,
  `verifyLineGroupRasterization`, `verifyRelaxedLineGroupRasterization`, `verifyPointGroupRasterization`, and
  `verifyTriangleGroupInterpolation` helpers are the single source of pass/fail truth.

### Line rasterization modes

Vulkan exposes multiple line rasterization algorithms through `VkLineRasterizationModeEXT`:

| Mode | Algorithm shape |
|------|-----------------|
| `VK_LINE_RASTERIZATION_MODE_DEFAULT_EXT` | Implementation default; usually matches either rectangular or Bresenham. |
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_EXT` | Filled parallelogram around the segment. |
| `VK_LINE_RASTERIZATION_MODE_BRESENHAM_EXT` | Bresenham-style, no antialiasing. |
| `VK_LINE_RASTERIZATION_MODE_RECTANGULAR_SMOOTH_EXT` | Rectangular with smooth (alpha-blended) edges. |

Strictness is a separate axis: `PRIMITIVESTRICTNESS_STRICT` follows the strict rasterization rules, `PRIMITIVESTRICTNESS_NONSTRICT`
follows the relaxed rules, and `PRIMITIVESTRICTNESS_IGNORE` defers to `limits.strictLines`
[vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L146-L153).

Why it matters here:

- The verifier switches between `verifyLineGroupRasterization` for Bresenham and `verifyRelaxedLineGroupRasterization` for
  other modes, with strict vs relaxed thresholds controlling the accepted pixel set
  [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1949-L1982).
- `VK_KHR_maintenance5` adds a property selecting whether non-strict lines use parallelogram or Bresenham rasterization;
  the maintenance5 family compares both algorithms and accepts the one the property selects
  [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8913-L8966).

### Conservative rasterization

`VK_EXT_conservative_rasterization` adds two modes:

- `OVERESTIMATE`: rasterize every pixel partially or fully covered by an expanded primitive. An extra overestimation size
  inflates the primitive further; `min` and `max` select implementation-supported extremes.
- `UNDERESTIMATE`: rasterize only pixels fully covered by the primitive.

The same `tcuRasterizationVerifier` reference helpers compute expected coverage for each mode; degenerate triangles and
lines are also tested because the spec allows implementations to rasterize or drop them under conservative rasterization.

### Polygon fill rules and overdraw

The Vulkan spec's fill rule determines which pixels on a shared edge or at a vertex belong to a triangle. The
`fill_rules` family draws gray triangles with shared edges using additive blending and scans the result for pixels
brighter than the triangle color (overdraw) or, in the clipped-full case, for black pixels (missing fragments)
[vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6129-L6192).

Why it matters here:

- Reference-rasterizer comparison cannot detect overdraw alone because the verifier checks per-triangle coverage, not
  fragment counting. The fill-rule test uses additive blending as a separate detector.
- The clipped-full case checks the inverse: that no pixel inside the viewport remains uncovered when a triangle fully
  covers it.

### Depth bias

Depth bias shifts fragment depth values to avoid z-fighting or to push wireframe geometry behind solid geometry. The
spec formula combines a constant factor, slope-scaled bias, and a clamp around the minimum resolvable difference. The
Amber `depth_bias` cases draw two overlapping quads with known depths and check that the resulting depth buffer matches
the spec formula within tolerance for `D16_UNORM`, `D32_SFLOAT`, and `D24_UNORM_S8_UINT`
[d16_unorm.amber](../../../data/vulkan/amber/rasterization/depth_bias/d16_unorm.amber#L17-L34).

## One Concrete Example

### `primitives.no_stipple.triangles` example

Representative test name from mustpass:

```text
dEQP-VK.rasterization.primitives.no_stipple.triangles
```

Simplified behavior for this case:

1. The host generates a grid of random triangles using `BaseTriangleTestInstance::generateTriangles`.
2. It draws them with the base vertex/fragment template shaders into a 256x256 `R8G8B8A8_UNORM` image.
3. It calls `verifyTriangleGroupRasterization` with a `TriangleSceneSpec` built from the same vertex data, the device's
   `subPixelPrecisionBits`, and the color channel bit depth of the result format.
4. The verifier flags any pixel covered by the reference triangle set but missing from the result, or any pixel present
   in the result but not covered by the reference.
5. The case iterates three times with different random seeds; any failed iteration fails the case.

Conceptual GLSL, reconstructed from the template:

```glsl
// vertex
#version 310 es
layout(location = 0) in highp vec4 a_position;
layout(location = 1) in highp vec4 a_color;
layout(location = 0) out highp vec4 v_color;
layout (set=0, binding=0) uniform PointSize { highp float u_pointSize; };
void main () {
    gl_Position = a_position;
    gl_PointSize = u_pointSize;
    v_color = a_color;
}

// fragment
#version 310 es
layout(location = 0) out highp vec4 fragColor;
layout(location = 0) in highp vec4 v_color;
void main () {
    fragColor = v_color;
}
```

The shader is intentionally minimal. The rasterizer is the device under test; the shader only transports position and
color. The pass/fail decision is host-side.

## End-to-End Test Flow

The implemented families share a common host timeline that diverges in the verifier call and pipeline state. Registration
and case construction happen in [`createRasterizationTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019-L10451),
runtime execution is spread across the test instance classes, and verification uses
[tcuRasterizationVerifier](../../../../../framework/common/tcuRasterizationVerifier.hpp#L183-L260).

```text
1. [host] register and generate case hierarchy
   1.1 create the `rasterization` root
   1.2 add direct implemented children: primitives, primitive_size, polygon_as_large_points, fill_rules, culling,
       discard, conservative, interpolation, flatshading, multisample repeats, line_continuity, depth_bias, maintenance5
   1.3 attach delegated children: provoking_vertex, depth_bias_control, frag_side_effects,
       rasterization_order_attachment_access, shader_tile_image

2. [host] prune unsupported cases in checkSupport()
   2.1 require large-points, wide-lines, tessellation, geometry, mesh-shader, or pipeline-statistics features per case
   2.2 require VK_EXT_conservative_rasterization, VK_KHR_line_rasterization, VK_KHR_maintenance5,
       VK_EXT_extended_dynamic_state, or VK_KHR_portability_subset features per case
   2.3 require depth/stencil format support for Amber depth_bias cases

3. [host] generate shader program artifacts
   3.1 use BaseRenderingTestCase::initPrograms for the default vertex/fragment template
   3.2 use PointDefaultSizeTestCase::initPrograms for default-size point stages
   3.3 use PolygonModeLargePointsCase::initPrograms for polygon-mode-as-points cases (vert/mesh/tesc/tese/geom/frag)
   3.4 use StrideZeroCase::initPrograms for stride-zero point cases
   3.5 use CullAndPrimitiveIdCase::initPrograms for culling primitive-ID cases
   3.6 load Amber scripts for line_continuity and depth_bias

4. [host] create and bind resources
   4.1 create a 256x256 or 258x258 color image (or larger render-size for explicit point-size cases)
   4.2 create a verification buffer for copyback; for multisample cases create a resolve image
   4.3 build a graphics pipeline with the selected topology, polygon mode, cull mode, line state, sample count,
       and conservative-rasterization state

5. [host] submit draw work
   5.1 clear the color image
   5.2 bind vertex and color buffers (or push constants for stride-zero and polygon-as-points cases)
   5.3 draw the generated primitive set; for double-draw stipple cases, draw twice with stipple enabled then disabled
   5.4 barrier shader writes toward transfer

6. [device] execute fixed-function rasterization with the configured pipeline state
   6.A triangle/line/point primitives: rasterize per Vulkan rules and write white or colored fragments
   6.B fill_rules: rasterize gray triangles with shared edges and additive blending
   6.C conservative: rasterize with overestimate or underestimate and the configured extra size
   6.D discard: enable rasterizer discard and verify nothing is written (with optional pipeline-statistics query)
   6.E interpolation/flatshading: rasterize colored triangles/lines and let the fragment shader interpolate via v_color
   6.F maintenance5: rasterize non-strict lines; the host compares both Bresenham and parallelogram reference images

7. [host] copy and inspect results
   7.1 copy the color image to the verification buffer
   7.2 for Amber cases, the Amber runner performs its own pipeline execution, copyback, and assertion evaluation
   7.3 call the appropriate verifier (triangle/line/point/interpolation) with the scene spec and rasterization arguments
   7.4 fail the case if the verifier reports any invalid pixel; for fill_rules, also scan for overdraw or missing fragments
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Default vertex template | [s_shaderVertexTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L83-L95) | Sets `gl_Position` from `a_position`, copies `a_color` to `v_color`, and reads `u_pointSize` from a uniform. |
| Default fragment template | [s_shaderFragmentTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L97-L103) | Outputs `v_color` to `fragColor`. The `flat` qualifier is added by `BaseRenderingTestCase::initPrograms` when the case is flatshading. |
| PointDefaultSize shaders | [PointDefaultSizeTestCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L3022-L3081) | Vertex, tessellation control/evaluation, geometry, and fragment shaders for default-size point tests across stages. |
| PolygonModeLargePointsCase shaders | [PolygonModeLargePointsCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8416-L8535) | Vertex or mesh shader plus optional tessellation/geometry shaders and a fragment shader that emits a fixed geometry color. |
| StrideZeroCase shaders | [StrideZeroCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7842-L7866) | Simple vertex/fragment pair used to draw points with a vertex-buffer stride of zero. |
| CullAndPrimitiveIdCase shaders | [CullAndPrimitiveIdCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8077-L8127) | Vertex shader generates one triangle per pixel with alternating winding; fragment shader colors pixels by `gl_PrimitiveID`. |
| Amber line_continuity scripts | [line-strip.amber](../../../data/vulkan/amber/rasterization/line_continuity/line-strip.amber), [polygon-mode-lines.amber](../../../data/vulkan/amber/rasterization/line_continuity/polygon-mode-lines.amber) | Draw a line strip or polygon-mode-lines geometry, then run a compute shader that flood-fills connected line pixels and verifies the framebuffer ends up empty. |
| Amber depth_bias scripts | [d16_unorm.amber](../../../data/vulkan/amber/rasterization/depth_bias/d16_unorm.amber) and siblings | Draw two depth-biased quads with known depths, copy the depth image to a storage image, and verify the resulting depth values match the spec formula within tolerance. |
| Pipeline state | Host pipeline setup | Encodes topology, polygon mode, cull mode, front face, line rasterization mode, line stipple, conservative rasterization, depth bias, sample count, and rasterizer discard. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment | Yes, `R8G8B8A8_UNORM` image (or larger size for point-size cases) | Yes, color attachment | Written by fragment shader | Copied to verification buffer | Captures the rasterized image for verifier comparison. |
| Resolve attachment | Yes, when multisample | Yes, color attachment | Resolved from the multisample image | Copied to verification buffer | Required to flatten multisample results before copyback. |
| Vertex buffer | Yes, position and color attributes | Yes, vertex buffer binding | Read by vertex shader | No | Provides the scene geometry. For stride-zero cases the binding stride is 0 to force the implementation to read only the first vertex. |
| PointSize uniform | Yes, push-constant-style UBO | Yes, descriptor set 0 binding 0 | Read by vertex shader | No | Drives `gl_PointSize` for explicit point-size cases. |
| Depth/stencil attachment | Yes, for Amber depth_bias cases | Yes, depth attachment | Written by depth test | No (Amber depth-dump pipeline reads it back into a storage image) | Holds the depth-biased depth values that Amber verifies. |
| Verification buffer | Yes, host-visible | Transfer destination only | Receives copied color image | Yes | Makes the rasterized image visible to the host for verifier input. |
| Pipeline-statistics query | Yes, for discard query cases | Yes, query pool | Counts rasterization-stage invocations | Yes, after query reset | Verifies that rasterizer discard actually suppresses rasterization work. |

## What Is Checked

### Device-side checks

The implemented families do not perform shader-side pass/fail decisions. The fragment shader only writes the
interpolated color. All pass/fail logic is host-side.

### Host-side checks

| Test family | Host-side pass condition |
|-------------|--------------------------|
| `primitives` (triangles/lines/points) | `verifyTriangleGroupRasterization`, `verifyLineGroupRasterization`, `verifyRelaxedLineGroupRasterization`, or `verifyPointGroupRasterization` reports no invalid pixels across all iterations. |
| `primitive_size` | Point rendering covers the expected square region for the configured point size; default-size cases render a single center pixel. |
| `polygon_as_large_points` | `tcu::floatThresholdCompare` matches the rendered image against a reference that borders the geometry color based on the maintenance5 `polygonModePointSize` property. |
| `fill_rules` | No pixel is brighter than the triangle color (no overdraw); for `clipped_full`, no pixel is black (no missing fragments). |
| `culling` | Rendered image matches an empty scene for culled configurations; `primitive_id` case matches the expected color pattern from `gl_PrimitiveID`. |
| `discard` | Rendered image is empty; for `query_pipeline_true`, pipeline-statistics query reports zero rasterization invocations. |
| `conservative` | Reference coverage for overestimate or underestimate matches the rendered pixels for the configured extra size and sample count. |
| `interpolation` | `verifyTriangleGroupInterpolation` reports no invalid color values; line interpolation uses triangulated-line reference comparison. |
| `flatshading` | Same as `interpolation`, but the reference uses flat color per primitive. |
| Multisample repeats | Same verifier as `primitives`, `fill_rules`, and `interpolation`, but with the configured `VkSampleCountFlagBits`. |
| `line_continuity` (Amber) | Amber compute shader flood-fills connected line pixels; framebuffer must end up empty (all line pixels consumed). |
| `depth_bias` (Amber) | Amber compute shader reads back the depth image and verifies the depth values match the spec formula within tolerance. |
| `maintenance5` | `verifyLineGroupRasterization` (Bresenham) and `verifyRelaxedLineGroupRasterization` (parallelogram) both run; the property selects which result is accepted. |

The case fails if any verifier iteration reports invalid pixels or if the host-side scan finds overdraw, missing
fragments, wrong primitive-ID colors, or a wrong pipeline-statistics count.

## Behavior Parameter Identification

> **Behavior parameter:** `test family`
>
> **Candidate values:** `primitives`, `primitive_size`, `polygon_as_large_points`, `fill_rules`, `culling`, `discard`,
> `conservative`, `interpolation`, `flatshading`, multisample repeats (`primitives_multisample_*_bit`,
> `fill_rules_multisample_*_bit`, `interpolation_multisample_*_bit`), `line_continuity`, `depth_bias`, `maintenance5`

Each test family selects a distinct rasterization property. Configuration dimensions such as primitive topology, line
width, sample count, strictness, line rasterization mode, conservative mode, extra overestimation size, depth format,
and stipple state belong in `## Parameter Dimensions and Observed Values`, not in the behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primitives` (triangle/line/point) | The implementation's coverage rule for the selected topology, wideness, strictness, line rasterization mode, or stipple state diverges from the reference rasterizer's accepted range. |
| `primitive_size` | Point size is not applied, is clamped wrong, or the default-size path emits a non-1.0 size from the wrong shader stage. |
| `polygon_as_large_points` | Polygon-mode large points do not cover the expected region, or `polygonModePointSize` maintenance5 property is not honored. |
| `fill_rules` | Shared edges or vertices produce overdraw (double coverage) or missing fragments (zero coverage). |
| `culling` | Cull mode or front-face winding is applied wrong, or `gl_PrimitiveID` is not stable across culled primitives. |
| `discard` | Rasterizer discard does not suppress all rasterization work, or pipeline-statistics query reports nonzero invocations when discard is enabled. |
| `conservative` | Overestimate or underestimate coverage diverges from the spec rule for the configured extra size, degenerate handling, or sample count. |
| `interpolation` | Perspective-correct or projected interpolation produces color values outside the verifier's accepted range. |
| `flatshading` | Flat-shaded color uses the wrong provoking vertex, or interpolation qualifiers are not honored. |
| Multisample repeats | Multisample rasterization coverage diverges from the reference at the configured sample count. |
| `line_continuity` (Amber) | Line strip or polygon-mode-lines rasterization leaves a gap that the compute-shader flood fill cannot bridge. |
| `depth_bias` (Amber) | Depth bias formula evaluation is wrong for the selected format, constant, slope, or clamp. |
| `maintenance5` | Non-strict lines are not rasterized using the algorithm selected by the `nonStrictSinglePixelWideLinesUseParallelogram` or `nonStrictWideLinesUseParallelogram` property. |

### Shared failure surface

All verifier-backed families share one host-side failure surface: if the verifier itself were called with the wrong
scene spec, subpixel bits, color bit depth, or verification mode, the case could fail without an implementation defect.
Source-level investigation should rule out such host-side parameter mismatches before attributing failure to the
rasterizer.

## Important Variations and Special Cases

### Strictness and line rasterization mode interaction

For Bresenham lines the verifier forces `numSamples = 0` because Bresenham lines are not antialiased. For smooth lines
the verifier first checks that the result image contains at least one pixel with fractional alpha before running the
relaxed line comparison. For stippled lines the verifier downgrades the verification mode from `STRICT` to `WEAKER`
because stippling loses precision across segments in a strip
[vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1942-L1982).

### Wide-line width selection

Wide-line cases pick three line widths: 5.0, 10.0, and the device's reported `lineWidthRange[1]`. When the upper range
ends in `.5`, the case subtracts `lineWidthGranularity` because the rounding direction for half-integer widths is
underspecified [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1650-L1675).

### Double-draw stipple cases

`static_stipple` also includes `*_double_draw` cases that draw once with stipple enabled and once with stipple disabled,
verifying that dynamic stipple state changes between draws take effect.

### Conservative rasterization degenerate handling

Degenerate triangles and lines have a separate, smaller overestimate size set (`0_00`, `0_25`, `min`, `max`) because
the spec gives implementations latitude over whether to rasterize degenerate primitives under conservative rasterization.

### Portability subset

Triangle-fan topologies and point-polygon modes are checked against `VK_KHR_portability_subset` features before
execution; portability-subset implementations that do not support those features skip the corresponding cases
[vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7452-L7465).

### Vulkan SC vs non-VulkanSC pruning

Several families (`polygon_as_large_points`, `provoking_vertex`, `line_continuity`, `depth_bias`,
`depth_bias_control`, `rasterization_order_attachment_access`, `shader_tile_image`, `maintenance5`, and the
`dynamic_stipple_and_topology` subfamily of `primitives`) are wrapped in `#ifndef CTS_USES_VULKANSC` because they use
extensions or features not present in the Vulkan SC baseline.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category entry point | [createTests](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10455-L10458) | Top-level factory exposed through the header. |
| Category registration | [createRasterizationTests](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019-L10451) | Adds all direct children and delegates the rest. |
| Default shaders | [s_shaderVertexTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L83-L95), [s_shaderFragmentTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L97-L103) | Minimal vertex/fragment templates used by most families. |
| Triangle verifier call | [BaseTriangleTestInstance::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1503-L1520) | Feeds scene spec to `verifyTriangleGroupRasterization`. |
| Line verifier call | [BaseLineTestInstance::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1907-L2006) | Switches between Bresenham, relaxed, smooth, and stippled verification modes. |
| Point verifier call | [verifyPointGroupRasterization](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2408-L2427) | Reference coverage check for point primitives. |
| Fill-rule host scan | [FillRuleTestInstance::iterate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6128-L6204) | Overdraw and missing-fragment checks. |
| Culling host compare | [CullingTestInstance](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6793-L6820) | Compares against an empty scene for culled configurations. |
| Discard query path | [DiscardTestCase::checkSupport](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7190-L7195) | Pipeline-statistics query gate for discard query variants. |
| Conservative rasterization config | [ConservativeTestConfig](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727) | Mode, extra size, primitive, degenerate flag, and resolution. |
| Interpolation verifier call | [verifyTriangleGroupInterpolation](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7266-L7292) | Reference color interpolation check. |
| Maintenance5 compare | [NonStrictLinesMaintenance5TestCase::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8913-L8966) | Selects Bresenham or parallelogram based on maintenance5 property. |
| Polygon-as-large-points reference | [PolygonModeLargePointsCase](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8845-L8877) | Builds the expected image based on `polygonModePointSize`. |
| Amber line_continuity data dir | `rasterization/line_continuity` | Source of `line-strip.amber` and `polygon-mode-lines.amber`. |
| Amber depth_bias data dir | `rasterization/depth_bias` | Source of D16/D32/D24 Amber scripts. |
| Mustpass evidence | [rasterization.txt](../../../mustpass/main/vk-default/rasterization.txt) | Concrete registered case names. |

## Questions / Risk Points for User Audit

- [x] Keep one shader walkthrough for the default vertex/fragment template pair. The shader is minimal but the
  harness requires `## Shader Analysis` to use `shader-analyzer` when shader code is part of the tested behavior; the
  template is what produces `v_color` and `gl_Position` that the verifier reads.
- [x] Use `dEQP-VK.rasterization.interpolation.basic.triangles` as the representative case. The same template covers
  `primitives`, `interpolation`, and `flatshading` with only the `flat` qualifier differing.
- [x] The behavioral axis is the test family, not the line rasterization mode or strictness. Those are configuration
  dimensions inside `primitives` and the multisample repeats.
- [ ] Audit whether the Amber depth_bias description should reference the spec formula by number; the Amber script
  itself cites "Vulkan spec 26.12.3" but spec numbering shifts over time.
- [ ] Verify mustpass line anchors before publishing a final wiki page, because generated lists may shift.

## Conversion Notes for Final Wiki Rewrite

- Keep the one-sentence purpose as the final page's short problem statement.
- Distill the background into a compact prerequisite list: reference-rasterizer comparison, line rasterization modes,
  conservative rasterization, fill rules, and depth bias.
- Preserve one shader walkthrough for the default vertex/fragment template pair, anchored at
  `dEQP-VK.rasterization.interpolation.basic.triangles`.
- Move the parameter dimension table into `## Parameter Dimensions and Observed Values` without bloating the narrative.
- Keep `## Behavior Parameters` organized by test family, with one short subsection per family.
- Preserve the resource table because it distinguishes the host-side verification buffer from the device-side color
  attachment.
- Move detailed pruning rules and feature gates into `## Case Pruning` rather than the main narrative.
- Do not copy the beginner-focused prose verbatim into the final page; convert it to the Level-3 wiki style.
- The `### Failure Cause Mapping` table from `## What Failure Means` should be copied directly into the final page's
  `## Failure Meaning` → `### Failure Cause Mapping`. The `### Cause Analysis` subsection is written fresh during the
  final rewrite, not carried from the brief.
