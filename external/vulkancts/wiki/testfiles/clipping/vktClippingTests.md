# vktClippingTests.cpp

## Overview

[`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1) is the root registration and implementation file for the `clipping` category. The category is attached to the Vulkan and Vulkan SC root package as `clipping` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1369-L1370) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1436-L1437), and its category factory returns a `createTestGroup()` wrapper around [`addClippingTests()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1958).


## Role

Registration / dispatcher file and implementation-heavy test file.

## Source Code

- Primary source: [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1)
- Root header: [`vktClippingTests.hpp`](../../../modules/vulkan/clipping/vktClippingTests.hpp#L29-L35)
- Build inventory: [`CMakeLists.txt`](../../../modules/vulkan/clipping/CMakeLists.txt#L7-L16)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1369-L1370) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1436-L1437)
- Mustpass evidence: [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L1-L308)

## Registration Hierarchy

```text
clipping
├── clip_volume
├── user_defined
├── complementarity
└── misc
```

## Test Families

### clip_volume — Default clip-volume clipping, depth clamp, depth clip, large points, and wide lines

The `clip_volume` group is constructed in [`addClippingTests()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1762-L1848). It contains direct children `inside`, `outside`, `depth_clamp`, `depth_clip`, and `clipped`, registered by explicit `TestCaseGroup` construction and `addChild()` calls at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1779-L1847).

The `inside`, `outside`, `depth_clamp`, and `depth_clip` children share a topology table containing point list, line list, line-list adjacency, line strip, line-strip adjacency, triangle list, triangle-list adjacency, triangle strip, triangle-strip adjacency, and triangle fan at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1777). The case names are derived with `getPrimitiveTopologyShortName()` while registering the four families at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1785-L1824), and the resulting mustpass paths are visible in [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L4-L43).

`inside` draws primitives at `z = 0.0`, `0.5`, and `1.0` and expects enough non-black pixels for the selected topology at [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L451-L527). `outside` draws at `z = -0.5` and `1.5` and requires every pixel to remain black at [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L530-L576). `depth_clamp` toggles `depthClampEnable` for near/far intersections and counts expected colored regions at [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L585-L673). `depth_clip` toggles explicit `depthClipEnable`, first with depth clamp disabled and then, when supported, with depth clamp enabled at [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L684-L815).

The `clipped` child registers `large_points`, `wide_lines_axis_aligned`, and `wide_lines_diagonal` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1829-L1844). `large_points` evaluates point clipping behavior, including `VK_KHR_maintenance2` point-clipping properties when available, and accepts either all-black output or all expected points according to the reported behavior at [`testLargePoints()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L823-L904). `wide_lines_axis_aligned` and `wide_lines_diagonal` draw wide lines just outside the clip volume and either accept all-black output or compare against a reference draw of expanded line quads at [`testWideLines()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L961-L1081).

### user_defined — ClipDistance and combined ClipDistance/CullDistance matrices

The `user_defined` group is created as `clipDistanceGroup` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1850-L1926). It registers four direct families from two binary dimensions: `clip_distance`, `clip_distance_dynamic_index`, `clip_cull_distance`, and `clip_cull_distance_dynamic_index` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1858-L1885).

Each of those direct families contains shader-stage groups named from vertex-only, tessellation, geometry, and tessellation-plus-geometry combinations: `vert`, `vert_tess`, `vert_geom`, and `vert_tess_geom` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1887-L1895). For each shader group, clip-plane counts range from 1 through `MAX_CLIP_DISTANCES` (`8`), and combined cull-plane counts are generated as `min(MAX_CULL_DISTANCES, MAX_COMBINED_CLIP_AND_CULL_DISTANCES - numClipPlanes)` when the family uses cull distance at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1919). Each generated case is duplicated with and without `_fragmentshader_read` according to `fragmentShaderReads[]` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1867-L1874), producing the mustpass matrix shown in [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L53-L308).

The generated shaders declare `gl_ClipDistance[]` and `gl_CullDistance[]` in `gl_PerVertex` according to the selected counts at [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1113-L1128). The vertex, tessellation-control, tessellation-evaluation, and geometry shader paths either assign statically indexed built-ins or loop over them when dynamic indexing is selected at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1130-L1408). Fragment-shader-read cases explicitly read midpoint `gl_ClipDistance[]` and `gl_CullDistance[]` values into output color channels at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1410-L1447).

### complementarity — Complementary ClipDistance signs should fill exactly once

The `complementarity` group is added directly under `clipping`, not under `user_defined`, at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1928-L1939). It registers case names `1` through `8`, one for each enabled clip-distance count at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1932-L1936), matching mustpass entries in [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L44-L51).

The shader writes only the last enabled `gl_ClipDistance[]` component from the input `w` coordinate and sets earlier components to zero at [`ClipDistanceComplementarity::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1561-L1587). The test builds two identical sets of primitives whose clip-distance signs differ, enables blending, and expects the complete render area to be uniformly gray with no missing or double-blended pixels at [`testComplementarity()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679).

### misc — Negative and non-negative cull-distance interaction

The `misc` group is added directly under `clipping` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1941-L1950). It registers `negative_and_non_negative_cull_distance`, matching [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L52).

The vertex shader assigns three `gl_CullDistance[]` values so each vertex has one negative distance, but no single half-space is negative for all vertices at [`CullDistance::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1694-L1724). The test draws a large triangle strip and expects exactly half of the 16x16 framebuffer to be filled red, failing if the triangle is culled incorrectly at [`testCullDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Render size | `RENDER_SIZE = 16`, `RENDER_SIZE_LARGE = 128`, and derived pixel counts at [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L51-L60) |
| Default clip-volume topologies | Point, line, adjacency line, strip line, adjacency strip line, triangle, adjacency triangle, triangle strip, adjacency triangle strip, and triangle fan from `cases[]` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1777) |
| Default clip-volume z positions | Inside cases use `0.0`, `0.5`, `1.0` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L488-L505); outside cases use `-0.5` and `1.5` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L537-L550) |
| Depth clamp / depth clip toggles | Four near/far and enabled/disabled cases for each feature path at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L595-L611) and [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L694-L710) |
| Wide-line orientation | `LINE_ORIENTATION_AXIS_ALIGNED` and `LINE_ORIENTATION_DIAGONAL` at [`LineOrientation`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L330-L335), registered as two cases at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1839-L1842) |
| Clip and cull distance counts | `MAX_CLIP_DISTANCES = 8`, `MAX_CULL_DISTANCES = 8`, `MAX_COMBINED_CLIP_AND_CULL_DISTANCES = 8` at [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L56-L60); generated clip counts 1..8 and computed cull counts at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910) |
| Indexing mode | Static indexing and dynamic loop indexing selected by `indexingMode` and the `_dynamic_index` suffix at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1878-L1885) |
| Shader-stage path | `vert`, `vert_tess`, `vert_geom`, and `vert_tess_geom` group names generated from `shaderMask` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1887-L1895) |
| Fragment shader readback | Empty suffix and `_fragmentshader_read` suffix at [`fragmentShaderReads[]`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1867-L1874) |
| Complementarity clip-distance count | Case names `1` through `8` generated in [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1932-L1936) |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Feature gate helper | `requireFeatures()` maps local feature flags to physical-device feature checks for tessellation shader, geometry shader, float64, shader stores/atomics, depth clamp, large points, wide lines, shader clip distance, and shader cull distance at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L62-L115) |
| Portability subset triangle fan | `checkTopologySupport()` rejects triangle fans when `VK_KHR_portability_subset` is present without `triangleFans` support at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430) |
| Geometry shader for adjacency topologies | `primitivesInsideOutsideCheckSupport()` requires geometry shader for adjacency line/triangle topologies at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L432-L448); depth clamp/depth clip paths also require it for adjacency cases at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L623-L638) and [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L722-L737) |
| Depth clamp | `primitivesDepthClampCheckSupport()` requires `FEATURE_DEPTH_CLAMP` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L579-L583) |
| Explicit depth clip | `primitivesDepthClipCheckSupport()` requires `context.getDepthClipEnableFeaturesEXT().depthClipEnable` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L676-L682) |
| Large points / wide lines | `largePointsCheckSupport()` and `wideLinesCheckSupport()` require `FEATURE_LARGE_POINTS` and `FEATURE_WIDE_LINES` at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L818-L821) and [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L956-L959) |
| Shader clip/cull distances | Clip-distance cases derive requirements from selected counts at [`ClipDistance::checkSupport()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1450-L1467); complementarity requires shader clip distance at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1605-L1611); misc cull-distance requires shader cull distance at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1686-L1692) |
| Device limits for clip/cull distances | `testClipDistance()` fails when reported limits are below the required minimum constants at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1469-L1485) |

## Verification Methods

- Pixel-count checks are shared through `countPixels()` and color-range matching at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L238-L272).
- Default inside/outside clip-volume cases decide pass/fail by black-pixel counts after drawing through `VulkanDrawContext` at [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L507-L527) and [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L555-L576).
- Depth clamp and explicit depth clip compare colored-pixel counts in selected half-frame regions against topology-specific thresholds at [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L613-L673) and [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L712-L815).
- Large points validate all-black output or presence of all point colors according to point-clipping behavior at [`testLargePoints()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L828-L904).
- Wide lines accept all-black output or compare against a reference rasterization of expanded triangles using `tcu::intThresholdCompare()` at [`testWideLines()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1022-L1081).
- Clip/cull distance tests count expected black pixels, guard against unwanted lower-half black pixels, and optionally check fragment-read clip/cull distance interpolation with `checkFragColors()` at [`testClipDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1535-L1553) and [`checkFragColors()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319).
- Complementarity uses blending and requires every pixel in the 128x128 image to match gray within threshold at [`testComplementarity()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1664-L1679).
- The misc cull-distance case requires a red-pixel count equal to half the 16x16 framebuffer at [`testCullDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1745-L1753).

## Test Principles

- The file separates fixed clip-volume behavior from user-defined clip/cull-distance behavior through `clip_volume`, `user_defined`, `complementarity`, and `misc` registration branches at [`addClippingTests()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1950).
- Primitive topology is used as a cross-cutting dimension for default clip-volume cases, including adjacency topologies that require geometry shader support at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1824).
- User-defined distance cases exercise static versus dynamic indexing, optional tessellation and geometry stages, optional fragment shader reads, and bounded clip/cull distance counts in a generated registration matrix at [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1858-L1924).
- The tests rely on rendered image evidence rather than API return values for correctness: black-pixel counts, colored-region counts, reference-image comparison, and thresholded color checks are the observed pass criteria.

## Notes / Uncertainties

- No separate implementation files are included by the clipping root file; the only source file in this category that registers tests is [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1958).
