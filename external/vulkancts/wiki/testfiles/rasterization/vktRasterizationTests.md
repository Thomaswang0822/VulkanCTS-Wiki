# vktRasterizationTests.cpp

## Overview

[`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1) is the root registration and main implementation file for the `rasterization` category. It registers direct rasterization families in [`createRasterizationTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019), delegates extension-heavy registered groups to sibling files at [`createDepthBiasControlTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10411), [`createFragSideEffectsTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10416), [`createRasterizationOrderAttachmentAccessTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10422), and [`createShaderTileImageTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10427), and exposes the category entry point through [`createTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10455).

## Role

Registration / dispatcher file and implementation-heavy test file.

## Source Code

- Primary source: [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1)
- Root header: [`vktRasterizationTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.hpp#L36)
- Included registered sibling groups: [`vktRasterizationFragShaderSideEffectsTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L29), [`vktRasterizationProvokingVertexTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L31), [`vktRasterizationOrderAttachmentAccessTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L60), [`vktRasterizationDepthBiasControlTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L61), and [`vktShaderTileImageTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L62)

## Registration Hierarchy

```text
rasterization
├── primitives
├── primitive_size
├── polygon_as_large_points (non-VulkanSC only)
├── fill_rules
├── culling
├── discard
├── conservative
├── interpolation
├── flatshading
├── primitives_multisample_2_bit
├── fill_rules_multisample_2_bit
├── interpolation_multisample_2_bit
├── primitives_multisample_4_bit
├── fill_rules_multisample_4_bit
├── interpolation_multisample_4_bit
├── primitives_multisample_8_bit
├── fill_rules_multisample_8_bit
├── interpolation_multisample_8_bit
├── primitives_multisample_16_bit
├── fill_rules_multisample_16_bit
├── interpolation_multisample_16_bit
├── primitives_multisample_32_bit
├── fill_rules_multisample_32_bit
├── interpolation_multisample_32_bit
├── primitives_multisample_64_bit
├── fill_rules_multisample_64_bit
├── interpolation_multisample_64_bit
├── provoking_vertex (non-VulkanSC only)
├── line_continuity (non-VulkanSC only)
├── depth_bias (non-VulkanSC only)
├── depth_bias_control (non-VulkanSC only)
├── frag_side_effects
├── rasterization_order_attachment_access (non-VulkanSC only)
├── shader_tile_image (non-VulkanSC only)
└── maintenance5 (non-VulkanSC only)
```

## Test Families

### primitives — Primitive rasterization and line modes

The `primitives` group creates `no_stipple`, `static_stipple`, `dynamic_stipple`, non-VulkanSC `dynamic_stipple_and_topology`, and `stride_zero` children at [`createRasterizationTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9035-L9056). It registers triangle, triangle-strip, triangle-fan, point, line, line-with-adjacency, line-strip, and line-strip-with-adjacency cases with strict, non-strict, wide-line, line-stipple, rectangular-line, Bresenham-line, and smooth-line variants at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9086-L9372). The `stride_zero` subfamily adds `single_point`, `four_points`, and `many_points` using vertex-buffer stride zero at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9058-L9083).

### primitive_size — Point-size behavior

The `primitive_size` group contains explicit large point sizes from 128.0 through 10000.0 at [`testCombinations[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9386-L9400), default point-size tests across vertex, tessellation, geometry, and combined stages at [`pointDefaultSizeCombinations[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9414-L9439), and non-VulkanSC polygon-as-points default-size variants over mesh, tessellation, geometry, and dynamic polygon mode dimensions at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9445-L9484).

### polygon_as_large_points — Polygon mode as large points

The non-VulkanSC `polygon_as_large_points` group registers the same mesh/tessellation/geometry/dynamic-polygon-mode matrix with point size 2.0 at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9491-L9527).

### fill_rules — Polygon fill rules

The `fill_rules` group registers `basic_quad`, `basic_quad_reverse`, `clipped_full`, `clipped_partly`, and `projected` cases at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9530-L9544).

### culling — Face culling and primitive ID

The `culling` group combines front/back/both cull modes, triangle-list/strip/fan topologies, front-face order, and fill/line/point polygon modes in nested loops at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9546-L9600), then adds a `primitive_id` case at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9604-L9605).

### discard — Rasterizer discard

The `discard` group has direct children for triangle-list, triangle-strip, triangle-fan, line-list, line-strip, and point-list topologies and creates `query_pipeline_false` and `query_pipeline_true` cases under each topology at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9608-L9647).

### conservative — Conservative rasterization

The `conservative` group splits into `overestimate` and `underestimate`, then sample-count groups for 1, 2, 4, 8, 16, 32, and 64 samples, primitive groups for triangles, lines, and points, and `normal` / `degenerate` cases at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9650-L9886). Overestimate extra sizes include 0.00, 0.25, 0.50, 0.75, 1.00, 2.00, 4.00, min, and max for normal cases, with a smaller degenerate set at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9658-L9667); underestimate varies line widths 0.50, 1.00, 1.50 and point sizes 1.00 through 8.00 at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9668-L9675).

### interpolation — Perspective and projected interpolation

The `interpolation` group contains `basic` and `projected` children at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9888-L9966). Each registers triangle, triangle-strip, triangle-fan, line, line-strip, wide-line, strict-line, and non-strict-line interpolation cases using `INTERPOLATIONFLAGS_NONE` or `INTERPOLATIONFLAGS_PROJECTED` at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9900-L10025).

### flatshading — Flat interpolation

The `flatshading` group uses `INTERPOLATIONFLAGS_FLATSHADE` and registers triangle, triangle-strip, triangle-fan, line, line-strip, wide-line, strict-line, and non-strict-line cases at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10029-L10094).

### primitives_multisample_2_bit through interpolation_multisample_64_bit — Multisample repeats

For sample counts 2, 4, 8, 16, 32, and 64, the file registers `primitives_multisample_*_bit`, `fill_rules_multisample_*_bit`, and `interpolation_multisample_*_bit` groups at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10096-L10292). These groups repeat selected primitive, fill-rule, and interpolation coverage with `VkSampleCountFlagBits` values from `samples[]`.

### provoking_vertex — Provoking vertex

The non-VulkanSC `provoking_vertex` group is delegated to [`createProvokingVertexTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10294-L10298); see [`vktRasterizationProvokingVertexTests.md`](vktRasterizationProvokingVertexTests.md).

### line_continuity — Amber line continuity

The non-VulkanSC `line_continuity` group registers Amber files `line-strip.amber` and `polygon-mode-lines.amber`; the polygon-mode case adds `Features.fillModeNonSolid` at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10301-L10332).

### depth_bias — Amber depth bias

The non-VulkanSC `depth_bias` group registers Amber cases for D16, D32, and D24/S8 depth formats and constant/slope variants at [`cases[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10336-L10405).

### depth_bias_control — Extension depth-bias control

The non-VulkanSC `depth_bias_control` group is delegated to [`createDepthBiasControlTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10409-L10412); see [`vktRasterizationDepthBiasControlTests.md`](vktRasterizationDepthBiasControlTests.md).

### frag_side_effects — Fragment shader side effects

The `frag_side_effects` group is delegated to [`createFragSideEffectsTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10414-L10417); see [`vktRasterizationFragShaderSideEffectsTests.md`](vktRasterizationFragShaderSideEffectsTests.md).

### rasterization_order_attachment_access — Attachment access ordering

The non-VulkanSC `rasterization_order_attachment_access` group is delegated to [`createRasterizationOrderAttachmentAccessTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10419-L10423); see [`vktRasterizationOrderAttachmentAccessTests.md`](vktRasterizationOrderAttachmentAccessTests.md).

### shader_tile_image — Shader tile image

The non-VulkanSC `shader_tile_image` group is delegated to [`createShaderTileImageTests()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10425-L10428); see [`vktShaderTileImageTests.md`](vktShaderTileImageTests.md).

### maintenance5 — Maintenance5 non-strict line rasterization

The non-VulkanSC `maintenance5` group registers four cases: `non_strict_lines_narrow`, `non_strict_lines_wide`, `non_strict_line_strip_narrow`, and `non_strict_line_strip_wide` at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10431-L10449).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Resolution | 256 and 258 from [`ResolutionValues`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L112-L116), plus explicit point-size render sizes 1024 through 10240 in [`testCombinations[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9386-L9391) |
| Primitive width | `PRIMITIVEWIDENESS_NARROW` and `PRIMITIVEWIDENESS_WIDE` at [`PrimitiveWideness`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L118-L124) |
| Line stipple | disabled, static, dynamic, and dynamic-with-topology at [`LineStipple`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L126-L134), with factors default, zero, and large at [`stippleFactorCases[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9023-L9033) |
| Strictness | strict, non-strict, and ignore at [`PrimitiveStrictness`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L146-L153) |
| Sample counts | 2, 4, 8, 16, 32, and 64 in multisample repeats at [`samples[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10096-L10097), with conservative rasterization also using 1 sample at [`samples[]`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9683-L9685) |
| Conservative rasterization mode | overestimate and underestimate in [`ConservativeTestConfig`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727) and [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9808-L9815) |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Large points | Required by explicit point-size cases at [`PointSizeTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2512-L2516) and some polygon-as-points cases at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8391-L8393) |
| Tessellation / geometry point size | Required by point-default-size stage combinations at [`PointDefaultSizeTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L3096-L3115) |
| `VK_EXT_conservative_rasterization` | Required by conservative cases at [`ConservativeTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L3446-L3450) |
| Wide lines | Required by wide line families at [`WidenessTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L5575-L5579) and maintenance5 wide cases at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8891-L8900) |
| Geometry shader | Required for adjacency-line paths at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L5565-L5571) and cull/primitive-ID at [`CullAndPrimitiveIdCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8071-L8075) |
| `VK_EXT_extended_dynamic_state` | Required only for dynamic line stipple with topology at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L5575-L5577) |
| Pipeline statistics query | Required for discard query variants at [`DiscardTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7190-L7195) |
| `VK_KHR_maintenance5` | Required by polygon-as-large-points and maintenance5 paths at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8351-L8355) and [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8891-L8895) |
| Portability subset triangle-fan / point-polygon limits | Checked in culling and polygon-as-points support paths at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6695-L6707) and [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8361-L8369) |

## Verification Methods

- Triangle, line, and point primitive results use `tcuRasterizationVerifier` helpers such as [`verifyTriangleGroupRasterization()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1503-L1520), [`verifyLineGroupRasterization()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1907-L1954), and [`verifyPointGroupRasterization()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2408-L2427).
- Relaxed and strict line verification paths call [`verifyRelaxedLineGroupRasterization()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1971-L1978) and compare multiple accepted algorithms for maintenance5 at [`NonStrictLinesMaintenance5TestCase::compareAndVerify()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8913-L8944).
- Fill rules verify invalid pixels and overdraw / missing fragments at [`FillRuleTestInstance::iterate()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6128-L6204).
- Culling and discard compare against empty or expected rasterization scenes at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6793-L6820) and [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L6446-L6489).
- Interpolation cases use [`verifyTriangleGroupInterpolation()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7266-L7292) and triangulated-line interpolation checks at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7573-L7627).
- Polygon-as-points and maintenance5 exact color/reference comparisons use [`tcu::floatThresholdCompare()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8272-L8274) and [`tcu::floatThresholdCompare()`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8871-L8874).

## Test Principles Observed

- **Reference-rasterizer comparison**: primitive coverage is validated against `tcuRasterizationVerifier` reference scenes rather than only checking that draws complete.
- **Matrix generation**: registration loops combine primitive topology, line width, strictness, line-stipple state, line rasterization mode, sample count, and extension-specific modes.
- **Extension isolation**: non-core and non-VulkanSC paths are separated by support checks and `CTS_USES_VULKANSC` guards.

## Notes / Uncertainties

- The root file includes helper headers such as [`tcuRasterizationVerifier.hpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L33), but pure helpers do not get separate Level-3 pages under this scope.
- Some direct children are non-VulkanSC only because they are registered inside `#ifndef CTS_USES_VULKANSC` blocks at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10294-L10450).
