## Overview

**Core question:** Does Vulkan's fixed-function rasterizer produce fragment coverage and interpolated values that match a host-side reference rasterizer across primitive topologies, line rasterization modes, polygon fill rules, culling, discard, conservative rasterization, multisample rates, depth bias, and `VK_KHR_maintenance5` non-strict line behavior?

- [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp) is the root implementation file for the `rasterization` test category. `createTests()` is the header-exposed entry point and `createRasterizationTests()` registers all direct children, implementing most inline and delegating the rest to separate files.
- Implemented families: `primitives`, `primitive_size`, `polygon_as_large_points`, `fill_rules`, `culling`, `discard`, `conservative`, `interpolation`, `flatshading`, multisample repeats of `primitives`/`fill_rules`/`interpolation`, Amber `line_continuity` and `depth_bias`, and `maintenance5`.
- Delegated families (registration only): `provoking_vertex`, `depth_bias_control`, `frag_side_effects`, `rasterization_order_attachment_access`, `shader_tile_image`.
- The core test idea: send the same scene description to both the device rasterizer and a software reference rasterizer in `tcuRasterizationVerifier`, then flag any pixel covered by the reference but missing in the result, or present in the result but not covered by the reference.
- The page explains the shared host/device flow, the per-family behavior differences, the representative shader, the host-side verification, and what failure means per family.

## Background Knowledge

For the shared concept depth bias, see [Background Knowledge](../../categories/rasterization.md#background-knowledge) of the `rasterization` page.

- **Reference-rasterizer comparison.** The implemented families compare the device image against a software reference rasterizer in `tcuRasterizationVerifier`, not against a hand-curated image. The verifier computes per-pixel coverage from floating-point vertex positions and selected subpixel precision, then flags pixels covered by the reference but missing in the result, or present in the result but uncovered by the reference [tcuRasterizationVerifier.hpp](../../../../../framework/common/tcuRasterizationVerifier.hpp#L183-L237). Strict modes narrow the accepted range; relaxed modes widen it.
- **Line rasterization modes.** `VK_KHR_line_rasterization` exposes `DEFAULT`, `RECTANGULAR`, `BRESENHAM`, and `RECTANGULAR_SMOOTH` modes through `VkLineRasterizationModeEXT`. Strictness is a separate axis (`STRICT`, `NONSTRICT`, `IGNORE`) that selects whether the verifier applies strict or relaxed coverage thresholds [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L146-L153).
- **Conservative rasterization.** `VK_EXT_conservative_rasterization` adds `OVERESTIMATE` (rasterize every pixel partially or fully covered by an expanded primitive) and `UNDERESTIMATE` (rasterize only pixels fully covered). An extra overestimation size inflates the primitive further; degenerate primitives get a separate, smaller size set because the spec gives implementations latitude over whether to rasterize them.
- **Polygon fill rules and overdraw.** The Vulkan spec's fill rule determines which pixels on a shared edge or at a vertex belong to a triangle. Per-triangle coverage checking cannot detect double coverage on shared edges, so the `fill_rules` family uses additive blending as a separate overdraw detector and scans the result for pixels brighter than the triangle color [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6128-L6204).

## Registration Hierarchy

```text
rasterization
├── primitives
├── primitive_size
├── polygon_as_large_points
├── fill_rules
├── culling
├── discard
├── conservative
├── interpolation
├── flatshading
├── line_continuity
├── depth_bias
├── maintenance5
├── provoking_vertex (registration only)
├── depth_bias_control (registration only)
├── frag_side_effects (registration only)
├── rasterization_order_attachment_access (registration only)
└── shader_tile_image (registration only)
```

`primitives`, `fill_rules`, and `interpolation` are also registered as `*_multisample_<N>_bit` direct children for `N` = 2, 4, 8, 16, 32, 64; those variants repeat the same family logic at the configured `VkSampleCountFlagBits` and are covered as a parameter dimension below, not as distinct families.

## Parameter Dimensions and Observed Values

The matrix is built inside `createRasterizationTests()` and the multisample loop [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019-L10451). The table keeps the registered values and adds why each dimension matters.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Primitive topology | `triangles`, `triangle_strip`, `triangle_fan`, `points`, `lines`, `lines_with_adjacency`, `line_strip`, `line_strip_with_adjacency` | Selects the `VkPrimitiveTopology` fed to the rasterizer; each topology exercises a different coverage rule. | [nostippleTests registration](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9087-L9175) |
| Primitive wideness | `narrow`, `wide` | Narrow uses default point/line size; wide uses `pointSize` > 1 or `lineWidth` > 1 from device limits. | [WidenessTestCase](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9093-L9102) |
| Strictness | `strict`, `non_strict`, `ignore` | `STRICT` follows strict rasterization rules, `NONSTRICT` follows relaxed rules, `IGNORE` defers to `limits.strictLines`. | [PrimitiveStrictness](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L146-L153) |
| Line rasterization mode | `default`, `rectangular`, `bresenham`, `smooth` | Selects `VkLineRasterizationModeEXT`; the verifier switches between `verifyLineGroupRasterization` (Bresenham) and `verifyRelaxedLineGroupRasterization` (others). | [BaseLineTestInstance::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1907-L2006) |
| Line stipple | `no_stipple`, `static_stipple`, `dynamic_stipple`, `dynamic_stipple_and_topology` | Enables line stipple and selects static vs dynamic state; stipple downgrades verifier mode from `STRICT` to `WEAKER`. | [LineStipple](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L126-L134) |
| Sample count | `1_bit`, `2_bit`, `4_bit`, `8_bit`, `16_bit`, `32_bit`, `64_bit` | Repeats `primitives`, `fill_rules`, and `interpolation` at each `VkSampleCountFlagBits`; multisample cases use a resolve attachment before copyback. | [multisample loop](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10096-L10103) |
| Conservative mode | `overestimate`, `underestimate` | Selects `VkConservativeRasterizationModeEXT`; overestimate expands coverage, underestimate shrinks it. | [ConservativeTestConfig](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727) |
| Extra overestimation size | `0_00`, `0_25`, `0_50`, `0_75`, `1_00`, `2_00`, `4_00`, `min`, `max` | Inflates the primitive beyond the base overestimate; `min`/`max` select implementation-supported extremes. Degenerate primitives use a smaller set. | [ConservativeTestConfig](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727) |
| Depth format (Amber) | `d16_unorm`, `d32_sfloat`, `d24_unorm_s8_uint` | Amber `depth_bias` cases verify the bias formula at each depth format. | [depth_bias data dir](../../../data/vulkan/amber/rasterization/depth_bias) |
| Fill rule case | `basic_quad`, `basic_quad_reverse`, `clipped_full`, `clipped_partly`, `projected` | Selects shared-edge, reversed-winding, full-coverage, partial-clip, and projected-fill subcases. | [FillRuleTestCase](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9536-L9580) |
| Interpolation type | `basic`, `projected` | `basic` uses perspective-correct interpolation; `projected` uses projected line interpolation. | [interpolation registration](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9892-L9920) |

## Behavior Parameters

The primary behavioral axis for this page is the **test family** under `rasterization`. Each implemented family selects a distinct rasterization property; the remaining path components configure topology, wideness, strictness, line mode, stipple, sample count, conservative mode, extra size, depth format, or fill-rule subcase.

### primitives — Coverage per topology

`primitives` checks that the rasterizer covers exactly the pixels the Vulkan rules permit for the selected topology, wideness, strictness, line rasterization mode, and stipple state. Triangle, line, and point groups feed the same scene spec to `verifyTriangleGroupRasterization`, `verifyLineGroupRasterization`/`verifyRelaxedLineGroupRasterization`, or `verifyPointGroupRasterization` [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1503-L1520). The case iterates three times with different random seeds.

### primitive_size — Point size application

`primitive_size` checks that explicit point sizes cover the expected square region and that default-size points render a single center pixel. Default-size cases run across vertex, tessellation, and geometry stages to confirm the default-size path emits 1.0 from the correct stage [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9380-L9399).

### polygon_as_large_points — Polygon mode as large points

`polygon_as_large_points` draws triangles with `VK_POLYGON_MODE_POINT` and compares the result against a reference that borders the geometry color based on the `polygonModePointSize` maintenance5 property [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8416-L8535). This family is wrapped in `#ifndef CTS_USES_VULKANSC` because it depends on maintenance5.

### fill_rules — Shared-edge and full-coverage fill rules

`fill_rules` draws gray triangles with shared edges using additive blending. The host scans for pixels brighter than the triangle color (overdraw from double coverage) and, in the `clipped_full` case, for black pixels (missing fragments when a triangle fully covers the viewport) [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6128-L6204). Reference-rasterizer comparison alone cannot detect overdraw because it checks per-triangle coverage, not fragment counting.

### culling — Cull mode and front-face winding

`culling` verifies that culled configurations produce an empty image matching an empty scene, and that `gl_PrimitiveID` remains stable across culled primitives. The `primitive_id` case generates one triangle per pixel with alternating winding and colors pixels by `gl_PrimitiveID` [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8077-L8127).

### discard — Rasterizer discard suppression

`discard` enables `VK_CULL_MODE_NONE` with `rasterizerDiscardEnable = VK_TRUE` and verifies that nothing is written. The `query_pipeline_true` variant also checks a pipeline-statistics query reports zero fragment shader invocations [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7190-L7195).

### conservative — Overestimate and underestimate coverage

`conservative` rasterizes with `VK_EXT_conservative_rasterization` overestimate or underestimate and the configured extra size. Degenerate triangles and lines use a smaller size set because the spec gives implementations latitude over whether to rasterize them. The reference coverage helpers `calculateUnderestimateTriangleCoverage` and `calculateUnderestimateLineCoverage` compute the expected pixel set [tcuRasterizationVerifier.hpp](../../../../../framework/common/tcuRasterizationVerifier.hpp#L162-L171).

### interpolation — Perspective-correct color interpolation

`interpolation` checks that the rasterizer's interpolation of `v_color` across covered pixels matches the reference. Triangles use `verifyTriangleGroupInterpolation`; lines use triangulated-line reference comparison [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7266-L7292). The `projected` subcase uses projected line interpolation.

### flatshading — Flat per-primitive color

`flatshading` uses the same verifier as `interpolation`, but the reference uses flat color per primitive. The `flat` qualifier is added to `v_color` by `BaseRenderingTestCase::initPrograms` when `m_flatshade` is true [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L177-L187).

### Multisample repeats — Same families at higher sample counts

`primitives_multisample_<N>_bit`, `fill_rules_multisample_<N>_bit`, and `interpolation_multisample_<N>_bit` repeat the corresponding family logic at `VkSampleCountFlagBits` N. Multisample cases create a resolve attachment to flatten the multisample image before copyback. The `dynamic_stipple_and_topology` subfamily is pruned from multisample variants because it is not needed there [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10146-L10153).

### line_continuity — Amber line continuity check

`line_continuity` runs Amber scripts that draw a line strip or polygon-mode-lines geometry, then run a compute shader that flood-fills connected line pixels. The framebuffer must end up empty, meaning every line pixel was reachable and consumed by the flood fill [line-strip.amber](../../../data/vulkan/amber/rasterization/line_continuity/line-strip.amber). This family is wrapped in `#ifndef CTS_USES_VULKANSC`.

### depth_bias — Amber depth bias formula check

`depth_bias` runs Amber scripts that draw two depth-biased quads with known depths, copy the depth image to a storage image, and verify the resulting depth values match the spec formula within tolerance for `D16_UNORM`, `D32_SFLOAT`, and `D24_UNORM_S8_UINT` [d16_unorm.amber](../../../data/vulkan/amber/rasterization/depth_bias/d16_unorm.amber). This family is wrapped in `#ifndef CTS_USES_VULKANSC`.

### maintenance5 — Non-strict line algorithm selection

`maintenance5` rasterizes non-strict lines and compares both Bresenham and parallelogram reference images. The `nonStrictSinglePixelWideLinesUseParallelogram` or `nonStrictWideLinesUseParallelogram` property selects which result is accepted [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8913-L8966). This family is wrapped in `#ifndef CTS_USES_VULKANSC`.

## Shader Analysis

The shaders in this file are generated as GLSL strings from `s_shaderVertexTemplate` and `s_shaderFragmentTemplate` rather than stored as checked-in shader files [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L83-L103). The template is intentionally minimal: the rasterizer is the device under test, and the shader only transports position and color. One walkthrough covers the default vertex/fragment pair because the same template drives `primitives`, `interpolation`, and `flatshading` with only the `flat` qualifier differing.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.rasterization.interpolation.basic.triangles
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `interpolation` | Tests perspective-correct color interpolation across triangles. |
| `basic` | Uses standard perspective-correct interpolation (not projected line interpolation). |
| `triangles` | Renders `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`; the verifier compares interpolated `v_color` against the reference. |
| `m_flatshade = false` | `BaseRenderingTestCase::initPrograms` substitutes `${INTERPOLATION}` with `""`, so `v_color` is smooth-interpolated. |
| Sample count `1_bit` | Default single-sample rendering; no resolve attachment needed. |

#### Purpose

This shader pair transports vertex position and color through the pipeline so that the fixed-function rasterizer can interpolate `v_color` across covered pixels. The host-side `verifyTriangleGroupInterpolation` call compares the resulting image against a software reference rasterizer; the shader itself performs no pass/fail decision.

#### Structural Design

| Stage | Input | Operation | Output | Consumer |
|-------|-------|-----------|--------|----------|
| Vertex | `a_position` (location 0) | Copy to `gl_Position` | Clip-space position | Fixed-function rasterizer (coverage) |
| Vertex | `a_color` (location 1) | Copy to `v_color` | Per-vertex color | Rasterizer (interpolation) |
| Vertex | `u_pointSize` (UBO binding 0) | Copy to `gl_PointSize` | Point size | Rasterizer (point size; unused for triangles) |
| Rasterizer | `gl_Position` + `v_color` | Interpolate `v_color` across covered pixels | Interpolated `v_color` per fragment | Fragment shader |
| Fragment | `v_color` (interpolated) | Copy to `fragColor` | Pixel color | Color attachment → host verifier |

The rasterizer is the device under test. The shaders only set up the inputs the rasterizer consumes and capture the interpolated output the host verifier reads.

#### Shader Code

##### Vertex Shader

```glsl
#version 310 es
/// a_position: vertex position in clip space; drives rasterizer coverage.
layout(location = 0) in highp vec4 a_position;
/// a_color: per-vertex color; the rasterizer interpolates this across the primitive.
layout(location = 1) in highp vec4 a_color;
/// v_color: output color passed to the fragment shader; the rasterizer interpolates this between vertices.
layout(location = 0) out highp vec4 v_color;
/// PointSize UBO at set=0, binding=0; drives gl_PointSize for point primitives. Unused for triangle/line topologies but always present in the template.
layout (set=0, binding=0) uniform PointSize {
    highp float u_pointSize;
};
void main ()
{
    /// gl_Position feeds the fixed-function rasterizer; the verifier computes reference coverage from the same vertex positions.
    gl_Position = a_position;
    gl_PointSize = u_pointSize;
    v_color = a_color;
}
```

##### Fragment Shader

```glsl
#version 310 es
/// fragColor: write target; the host copies this image back and feeds it to tcuRasterizationVerifier.
layout(location = 0) out highp vec4 fragColor;
/// v_color: rasterizer-interpolated color; the interpolation test verifies this matches the reference rasterizer's interpolation.
layout(location = 0) in highp vec4 v_color;
void main ()
{
    fragColor = v_color;
}
```

#### Additional Info

- The fragment shader stays fixed across `primitives`, `interpolation`, and `flatshading` cases. For `flatshading`, `BaseRenderingTestCase::initPrograms` substitutes `${INTERPOLATION}` with `"flat "` in both shaders, making `v_color` flat-rated per primitive instead of smooth-interpolated.
- The vertex shader's `gl_PointSize` write is unused for `triangles` topology but is always emitted by the template because the same template drives `points` cases where point size matters.
- The `${INTERPOLATION}` substitution is the only branch in `BaseRenderingTestCase::initPrograms`; all other family-specific shader generation lives in separate `initPrograms` overrides (`PolygonModeLargePointsCase`, `CullAndPrimitiveIdCase`, `StrideZeroCase`, `PointDefaultSizeTestCase`).
- SPIR-V target is `spirv1.0` because `BaseRenderingTestCase::initPrograms` adds sources through `vk::SourceCollections` without an explicit `vk::ShaderBuildOptions`, so the baseline SPIR-V version applies.

#### Parameter Variation Summary

| Variation | Effect on shader | Coverage in this page |
|-----------|------------------|----------------------|
| `flatshading.*` | `${INTERPOLATION}` becomes `"flat "`, adding the `flat` qualifier to `v_color` in both shaders. | Same template; no separate walkthrough. |
| `primitives.*` | Same template; the host verifier switches between triangle/line/point coverage helpers. | Same template; no separate walkthrough. |
| `interpolation.projected.*` | Same template; the host uses projected line interpolation in the verifier. | Same template; no separate walkthrough. |
| Multisample variants | Same template; the host creates a multisample render area and resolve attachment. | Same template; no separate walkthrough. |
| `polygon_as_large_points` | Different `initPrograms` override emits vert/mesh/tesc/tese/geom/frag stages. | Not covered by this walkthrough; see `PolygonModeLargePointsCase::initPrograms`. |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %a_position %v_color %a_color
               OpSource ESSL 310
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %a_position "a_position"
               OpName %PointSize "PointSize"
               OpMemberName %PointSize 0 "u_pointSize"
               OpName %__0 ""
               OpName %v_color "v_color"
               OpName %a_color "a_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %a_position Location 0
               OpDecorate %PointSize Block
               OpMemberDecorate %PointSize 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %v_color Location 0
               OpDecorate %a_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %a_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
  %PointSize = OpTypeStruct %float
%_ptr_Uniform_PointSize = OpTypePointer Uniform %PointSize
        %__0 = OpVariable %_ptr_Uniform_PointSize Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_ptr_Output_float = OpTypePointer Output %float
    %v_color = OpVariable %_ptr_Output_v4float Output
    %a_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %a_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %23 = OpAccessChain %_ptr_Uniform_float %__0 %int_0
         %24 = OpLoad %float %23
         %26 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %26 %24
         %29 = OpLoad %v4float %a_color
               OpStore %v_color %29
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The implemented families share a common host timeline that diverges in the verifier call and pipeline state.

- **Resource setup.** The host creates a 256x256 (or 258x258 NPOT) `R8G8B8A8_UNORM` color image, a host-visible verification buffer, and for multisample cases a resolve image. Amber cases create their own resources inside the Amber script.
- **Pipeline state.** The host builds a graphics pipeline encoding topology, polygon mode, cull mode, front face, line rasterization mode, line stipple, conservative rasterization state, depth bias, sample count, and rasterizer discard. Wide-line cases pick three widths: 5.0, 10.0, and the device's `lineWidthRange[1]` minus `lineWidthGranularity` when the upper range ends in `.5` [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1650-L1675).
- **Draw.** The host clears the color image, binds vertex and color buffers (or push constants for stride-zero and polygon-as-points cases), and draws the generated primitive set. Double-draw stipple cases draw once with stipple enabled and once with stipple disabled to verify dynamic state changes take effect.
- **Copyback.** The host copies the color image to the verification buffer; for multisample cases it resolves first. Amber cases perform their own copyback through a depth-dump pipeline.
- **Verification.** The host calls the appropriate verifier with the scene spec and rasterization arguments. For Bresenham lines the verifier forces `numSamples = 0`; for smooth lines it first checks for fractional alpha; for stippled lines it downgrades from `STRICT` to `WEAKER` [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1942-L1982). `fill_rules` also scans for overdraw or missing fragments. `discard` scans for an empty image and checks pipeline-statistics query counts.
- **Pass/fail condition.** The case fails if any verifier iteration reports invalid pixels, if the host-side scan finds overdraw, missing fragments, wrong primitive-ID colors, or a wrong pipeline-statistics count.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primitives` (triangle/line/point) | The implementation's coverage rule for the selected topology, wideness, strictness, line rasterization mode, or stipple state diverges from the reference rasterizer's accepted range. |
| `primitive_size` | Point size is not applied, is clamped wrong, or the default-size path emits a non-1.0 size from the wrong shader stage. |
| `polygon_as_large_points` | Polygon-mode large points do not cover the expected region, or `polygonModePointSize` maintenance5 property is not honored. |
| `fill_rules` | Shared edges or vertices produce overdraw (double coverage) or missing fragments (zero coverage). |
| `culling` | Cull mode or front-face winding is applied wrong, or `gl_PrimitiveID` is not stable across culled primitives. |
| `discard` | Rasterizer discard does not suppress all rasterization work, or pipeline-statistics query reports nonzero fragment shader invocations when discard is enabled. |
| `conservative` | Overestimate or underestimate coverage diverges from the spec rule for the configured extra size, degenerate handling, or sample count. |
| `interpolation` | Perspective-correct or projected interpolation produces color values outside the verifier's accepted range. |
| `flatshading` | Flat-shaded color uses the wrong provoking vertex, or interpolation qualifiers are not honored. |
| Multisample repeats | Multisample rasterization coverage diverges from the reference at the configured sample count. |
| `line_continuity` (Amber) | Line strip or polygon-mode-lines rasterization leaves a gap that the compute-shader flood fill cannot bridge. |
| `depth_bias` (Amber) | Depth bias formula evaluation is wrong for the selected format, constant, slope, or clamp. |
| `maintenance5` | Non-strict lines are not rasterized using the algorithm selected by the `nonStrictSinglePixelWideLinesUseParallelogram` or `nonStrictWideLinesUseParallelogram` property. |

All verifier-backed families share one host-side failure surface: if the verifier itself were called with the wrong scene spec, subpixel bits, color bit depth, or verification mode, the case could fail without an implementation defect. Source-level investigation should rule out such host-side parameter mismatches before attributing failure to the rasterizer.

### Cause Analysis

#### Coverage rule divergence

**Possible failure symptoms:** The verifier reports pixels covered by the reference but missing in the result, or pixels present in the result but not covered by the reference, for `primitives`, `conservative`, or multisample variants.

**Possible implementation causes:** The device's coverage rule for the selected topology, line rasterization mode, strictness, or conservative mode differs from what the Vulkan spec permits. For lines, this includes Bresenham step selection, parallelogram width rounding, or rectangular-edge handling. For conservative rasterization, this includes overestimate expansion size or underestimate shrinkage. For multisample cases, this includes sample-mask coverage at the configured sample count. The Vulkan spec's rasterization chapters define the accepted range; the verifier accepts any implementation within that range, so a failure means the implementation falls outside the spec-permitted range.

#### Interpolation value divergence

**Possible failure symptoms:** `verifyTriangleGroupInterpolation` reports color values outside the accepted range for `interpolation` or `flatshading`.

**Possible implementation causes:** The rasterizer's perspective-correct interpolation weights are wrong, or the `flat` qualifier is not honored and the implementation smooth-interpolates a value that should be flat-rated per primitive. For `flatshading`, the wrong provoking vertex is selected, producing the wrong flat color. Source-level investigation is needed to distinguish a rasterizer interpolation bug from a provoking-vertex bug; the `provoking_vertex` delegated family covers the latter in more detail.

#### Fill rule overdraw or missing fragments

**Possible failure symptoms:** `fill_rules` scans find pixels brighter than the triangle color (overdraw from double coverage on shared edges) or, in the `clipped_full` case, black pixels (missing fragments where a triangle fully covers the viewport).

**Possible implementation causes:** The implementation's shared-edge rule assigns a pixel to two triangles that share an edge, producing double coverage under additive blending. Conversely, the rule drops a pixel that both triangles should leave uncovered. The Vulkan spec's fill rule determines edge ownership; a failure means the implementation's edge rule differs from the spec.

#### Cull mode or primitive ID instability

**Possible failure symptoms:** `culling` cases produce a non-empty image for culled configurations, or the `primitive_id` case produces colors that do not match the expected `gl_PrimitiveID` pattern.

**Possible implementation causes:** Cull mode or front-face winding is applied incorrectly, so culled primitives are still rasterized. For the `primitive_id` case, `gl_PrimitiveID` is not stable across culled primitives, producing wrong colors. The Vulkan spec defines cull mode and front-face behavior; a failure means the implementation does not follow those rules.

#### Rasterizer discard not suppressing work

**Possible failure symptoms:** `discard` cases produce a non-empty image, or the `query_pipeline_true` variant reports nonzero fragment shader invocations in the pipeline-statistics query.

**Possible implementation causes:** `rasterizerDiscardEnable = VK_TRUE` does not suppress all rasterization-stage work in the implementation. The Vulkan spec requires that rasterizer discard prevent all rasterization, fragment shading, and depth/stencil writes; a failure means the implementation continues rasterizing after discard is enabled.

#### Point size or polygon-mode-points failure

**Possible failure symptoms:** `primitive_size` cases render the wrong point size (too large, too small, or clamped wrong), or `polygon_as_large_points` does not cover the expected region.

**Possible implementation causes:** Explicit point size is not applied or is clamped to the wrong range. Default-size points emit a non-1.0 size from the wrong shader stage. For `polygon_as_large_points`, the `polygonModePointSize` maintenance5 property is not honored, so the reference image borders do not match. Source-level investigation is needed to distinguish a point-size clamp bug from a maintenance5 property bug.

#### Amber line continuity gap

**Possible failure symptoms:** The `line_continuity` Amber compute shader's flood fill leaves non-empty pixels in the framebuffer, meaning the line strip had a gap.

**Possible implementation causes:** Line strip or polygon-mode-lines rasterization skips a pixel that should be covered, creating a gap the flood fill cannot bridge. The Vulkan spec's line continuity rule requires that connected line segments share endpoints; a failure means the implementation drops a shared endpoint pixel.

#### Amber depth bias formula mismatch

**Possible failure symptoms:** The `depth_bias` Amber compute shader reads back depth values that do not match the spec formula within tolerance for the selected format.

**Possible implementation causes:** The depth bias formula evaluation is wrong for the selected format, constant factor, slope-scaled bias, or clamp. The Vulkan spec's depth bias section defines the formula; a failure means the implementation computes a different bias than the spec requires. Source-level investigation should confirm the Amber script's expected values match the spec formula before attributing failure to the implementation.

#### Maintenance5 line algorithm selection

**Possible failure symptoms:** `maintenance5` cases fail because neither the Bresenham nor the parallelogram reference image matches the result.

**Possible implementation causes:** The implementation does not use the line rasterization algorithm selected by the `nonStrictSinglePixelWideLinesUseParallelogram` or `nonStrictWideLinesUseParallelogram` maintenance5 property. The host compares against both algorithms and accepts the one the property selects; a failure means the implementation uses a third algorithm or ignores the property.

## Case Pruning

### Requirement-based pruning

- `largePoints` feature is required for `primitive_size` wide-point cases and `polygon_as_large_points`.
- `wideLines` feature is required for wide-line cases; the upper line width is read from `limits.lineWidthRange[1]`.
- `tessellationShader` and `geometryShader` features are required for `primitive_size` default-size cases that run across tessellation/geometry stages.
- `meshShader` features are required for mesh-shader variants of `polygon_as_large_points`.
- `VK_EXT_conservative_rasterization` is required for `conservative`.
- `VK_KHR_line_rasterization` is required for `bresenham_lines`, `rectangular_lines`, and `smooth_lines` cases, plus `lineContinuity` and `lineStipple` features as needed.
- `VK_KHR_maintenance5` is required for `maintenance5` and `polygon_as_large_points`.
- `VK_EXT_extended_dynamic_state` is required for `dynamic_stipple_and_topology` cases.
- `VK_KHR_portability_subset` features (`portabilitySubsetTriangleFans`, `portabilitySubsetPointPolygons`) gate triangle-fan topologies and point-polygon modes [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7452-L7465).
- `pipelineStatisticsQuery` feature is required for `discard.query_pipeline_true`.
- Depth/stencil format support is required for Amber `depth_bias` cases per format.
- Multisample cases are pruned when the device does not support the requested sample count for `R8G8B8A8_UNORM`.

### Design-based pruning

- `dynamic_stipple_and_topology` is pruned from multisample variants because it is not needed there [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10146-L10153).
- Several families (`polygon_as_large_points`, `provoking_vertex`, `line_continuity`, `depth_bias`, `depth_bias_control`, `rasterization_order_attachment_access`, `shader_tile_image`, `maintenance5`, and `dynamic_stipple_and_topology`) are wrapped in `#ifndef CTS_USES_VULKANSC` because they use extensions or features not present in the Vulkan SC baseline.
- Wide-line cases subtract `lineWidthGranularity` from the upper range when it ends in `.5` because the rounding direction for half-integer widths is underspecified [vktRasterizationTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1650-L1675).
- Conservative degenerate primitives use a smaller overestimate size set (`0_00`, `0_25`, `min`, `max`) because the spec gives implementations latitude over whether to rasterize them.

## Key Takeaways

- The implemented families share one pass/fail mechanism: host-side comparison against `tcuRasterizationVerifier`'s reference rasterizer. The shader only transports position and color; it performs no pass/fail decision.
- `fill_rules` is the exception: additive blending detects overdraw that per-triangle coverage checking cannot see, and the `clipped_full` case checks for missing fragments when a triangle fully covers the viewport.
- Strictness, line rasterization mode, and stipple state are configuration dimensions inside `primitives` and the multisample repeats, not distinct families. The behavioral axis is the test family itself.
- `maintenance5` compares against both Bresenham and parallelogram references and accepts the one the property selects, rather than checking a single expected image.
- Amber families (`line_continuity`, `depth_bias`) run their own pipeline and compute-shader verification inside the Amber runner; the host only loads the script and checks the Amber result.
- All verifier-backed families share a host-side failure surface: a wrong scene spec, subpixel bits, color bit depth, or verification mode could fail the case without an implementation defect. Source-level investigation should rule out host-side parameter mismatches before attributing failure to the rasterizer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category entry point | [createTests](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10455-L10458) | Top-level factory exposed through the header. |
| Category registration | [createRasterizationTests](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019-L10451) | Adds all direct children and delegates the rest. |
| Default shaders | [s_shaderVertexTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L83-L95), [s_shaderFragmentTemplate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L97-L103) | Minimal vertex/fragment templates used by most families. |
| Shader builder | [BaseRenderingTestCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L177-L187) | Substitutes `${INTERPOLATION}` with `flat ` or `""` based on `m_flatshade`. |
| Triangle verifier call | [BaseTriangleTestInstance::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1503-L1520) | Feeds scene spec to `verifyTriangleGroupRasterization`. |
| Line verifier call | [BaseLineTestInstance::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1907-L2006) | Switches between Bresenham, relaxed, smooth, and stippled verification modes. |
| Point verifier call | [verifyPointGroupRasterization](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2408-L2427) | Reference coverage check for point primitives. |
| Fill-rule host scan | [FillRuleTestInstance::iterate](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6128-L6204) | Overdraw and missing-fragment checks. |
| Culling host compare | [CullingTestInstance](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6793-L6820) | Compares against an empty scene for culled configurations. |
| Culling primitive-ID shaders | [CullAndPrimitiveIdCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8077-L8127) | Alternating winding, `gl_PrimitiveID` coloring. |
| Discard query path | [DiscardTestCase::checkSupport](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7190-L7195) | Pipeline-statistics query gate for discard query variants. |
| Conservative rasterization config | [ConservativeTestConfig](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727) | Mode, extra size, primitive, degenerate flag, and resolution. |
| Interpolation verifier call | [verifyTriangleGroupInterpolation](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7266-L7292) | Reference color interpolation check. |
| Polygon-as-large-points shaders | [PolygonModeLargePointsCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8416-L8535) | Vert/mesh/tesc/tese/geom/frag for polygon-mode-points cases. |
| Stride-zero shaders | [StrideZeroCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7842-L7866) | Vertex/fragment for stride-zero point cases. |
| Maintenance5 compare | [NonStrictLinesMaintenance5TestCase::compareAndVerify](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8913-L8966) | Selects Bresenham or parallelogram based on maintenance5 property. |
| Reference verifier helpers | [tcuRasterizationVerifier.hpp](../../../../../framework/common/tcuRasterizationVerifier.hpp#L150-L260) | Coverage, line, triangle, point, and interpolation verifier functions. |
| Amber line_continuity data dir | [line_continuity](../../../data/vulkan/amber/rasterization/line_continuity) | Source of `line-strip.amber` and `polygon-mode-lines.amber`. |
| Amber depth_bias data dir | [depth_bias](../../../data/vulkan/amber/rasterization/depth_bias) | Source of D16/D32/D24 Amber scripts. |
| Mustpass evidence | [rasterization.txt](../../../mustpass/main/vk-default/rasterization.txt) | Concrete registered case names. |
