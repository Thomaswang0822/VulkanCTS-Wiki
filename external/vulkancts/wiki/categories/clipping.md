# clipping

## Overview

The [`clipping`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1956-L1959) category verifies fixed clip-volume behavior, depth clamp and explicit depth clip behavior, large-point and wide-line clipping behavior, shader-defined `gl_ClipDistance[]` and `gl_CullDistance[]` behavior, and selected complementarity/cull-distance corner cases. The category is registered as a Vulkan and Vulkan SC root child named `clipping` in [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1369-L1370) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1436-L1437).

The inspected Vulkan API test plan provides general Vulkan CTS test framework context for `TestCase`, `TestInstance`, and shader program setup at [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L20-L54), but it does not contain clipping-specific coverage text. Clipping-specific claims in this page are therefore derived from the inspected clipping implementation and mustpass registration file.

## Registration Entry Point

The category entry point is [`createTests()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1956-L1959), which returns a `createTestGroup()` wrapper around [`addClippingTests()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952). The direct children registered under `clipping` are:

```text
clipping
├── clip_volume
├── user_defined
├── complementarity
└── misc
```

Source: [`addClippingTests()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952), with mustpass coverage in [`clipping.txt`](../../mustpass/main/vk-default/clipping.txt#L1-L308).

## File Inventory

| File | Role | Registered group(s) / notes |
|---|---|---|
| [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1) | Root registration + implementation | Registers the complete `clipping` category: `clip_volume`, `user_defined`, `complementarity`, and `misc` |
| [`vktClippingTests.hpp`](../../modules/vulkan/clipping/vktClippingTests.hpp#L29-L35) | Category header | Declares the category factory used by root package registration |
| [`CMakeLists.txt`](../../modules/vulkan/clipping/CMakeLists.txt#L7-L16) | Build file | Lists only [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1) and [`vktClippingTests.hpp`](../../modules/vulkan/clipping/vktClippingTests.hpp#L1) for this category library |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1) | [`vktClippingTests.md`](../testfiles/clipping/vktClippingTests.md) |

## Subgroup Structure and Major Themes

### `clip_volume` — Fixed clip-volume, depth clamp/clip, and clipped primitives

The `clip_volume` group is built in [`addClippingTests()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1762-L1848). It registers `inside`, `outside`, `depth_clamp`, and `depth_clip` over a shared topology table containing point, line, adjacency-line, strip-line, adjacency-strip-line, triangle, adjacency-triangle, triangle-strip, adjacency-triangle-strip, and triangle-fan topologies at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1827). The `clipped` subfamily registers `large_points`, `wide_lines_axis_aligned`, and `wide_lines_diagonal` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1829-L1845).

### `user_defined` — Shader clip/cull distance matrix

The `user_defined` group is created at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1850-L1926). It contains `clip_distance`, `clip_distance_dynamic_index`, `clip_cull_distance`, and `clip_cull_distance_dynamic_index`, then expands each into `vert`, `vert_tess`, `vert_geom`, and `vert_tess_geom` shader-stage combinations with clip-count, cull-count, and optional fragment-shader-read suffixes at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1858-L1924).

### `complementarity` — Complementary clip-distance signs

The `complementarity` group is registered directly under `clipping` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1928-L1939). It generates case names `1` through `8`, one per enabled clip-distance count, and tests that two blended primitive sets with opposite clip-distance signs fill the render area exactly once at [`testComplementarity()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679).

### `misc` — Cull-distance half-space corner case

The `misc` group registers `negative_and_non_negative_cull_distance` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1941-L1950). The shader gives each triangle vertex one negative cull-distance component, but not the same component for every vertex, and the test expects half the framebuffer to be drawn red rather than culling the triangle at [`CullDistance::initPrograms()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1694-L1724) and [`testCullDistance()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Primitive topology | Ten fixed clip-volume topologies in `cases[]` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1777) |
| Clip-space depth | Inside cases use `z = 0.0`, `0.5`, and `1.0` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L488-L505); outside cases use `-0.5` and `1.5` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L537-L550) |
| Depth clamp / depth clip state | Four near/far and enabled/disabled combinations for each family at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L595-L611) and [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L694-L710) |
| Clip and cull distance counts | Constants set clip, cull, and combined maxima to `8` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L56-L60); generated cases use clip counts 1 through 8 and computed cull counts at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910) |
| Shader stages | User-defined distance groups combine vertex-only, tessellation, geometry, and tessellation-plus-geometry stage paths at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1887-L1895) |
| Indexing and readback mode | Static versus dynamic indexing is encoded in `_dynamic_index` names at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1878-L1885), while `_fragmentshader_read` cases are generated from `fragmentShaderReads[]` at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1867-L1874) |
| Large point / wide line variants | `large_points`, `wide_lines_axis_aligned`, and `wide_lines_diagonal` are registered in the `clipped` group at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1834-L1844) |

## Recurring Support Requirements

Observed support gates include geometry shader for adjacency topologies, triangle-fan portability-subset checks, depth clamp, explicit `VK_EXT_depth_clip_enable` feature support, large points, wide lines, shader clip distance, shader cull distance, tessellation shader, and geometry shader for selected user-defined distance paths. The shared feature helper maps local feature flags to `VkPhysicalDeviceFeatures` at [`requireFeatures()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L78-L115). Representative call sites are [`checkTopologySupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430), [`primitivesInsideOutsideCheckSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L432-L448), [`primitivesDepthClampCheckSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L579-L583), [`primitivesDepthClipCheckSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L676-L682), [`largePointsCheckSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L818-L821), [`wideLinesCheckSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L956-L959), and [`ClipDistance::checkSupport()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1450-L1467).

`testClipDistance()` also validates reported clip/cull distance limits against the minimum constants used by this file and fails if `maxClipDistances`, `maxCullDistances`, or `maxCombinedClipAndCullDistances` are below the expected values at [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1469-L1485).

## Recurring Verification Methods

The clipping category primarily verifies rendered image contents. Shared helpers count pixels within exact or thresholded color ranges at [`countPixels()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L247-L272). Fixed clip-volume tests compare black-pixel or colored-region counts at [`testPrimitivesInside()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L507-L527), [`testPrimitivesOutside()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L555-L576), [`testPrimitivesDepthClamp()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L613-L673), and [`testPrimitivesDepthClip()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L712-L815). Wide-line cases either accept an all-black result or compare against a reference draw with `tcu::intThresholdCompare()` at [`testWideLines()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1022-L1081).

User-defined distance tests compare expected black pixels, guard pixels, and optional fragment-read interpolation values at [`testClipDistance()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1535-L1553), with the fragment-read helper checking expected `gl_ClipDistance[]` and `gl_CullDistance[]` color channels at [`checkFragColors()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319). Complementarity uses blending and requires every pixel in a 128x128 framebuffer to match gray at [`testComplementarity()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1664-L1679), while the misc cull-distance case counts red pixels and expects half of the 16x16 framebuffer at [`testCullDistance()`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1745-L1753).

## Notes and Scope

- The clipping category has no sibling implementation files in the inspected directory; [`CMakeLists.txt`](../../modules/vulkan/clipping/CMakeLists.txt#L7-L16) lists only [`vktClippingTests.cpp`](../../modules/vulkan/clipping/vktClippingTests.cpp#L1) and [`vktClippingTests.hpp`](../../modules/vulkan/clipping/vktClippingTests.hpp#L1).
- The only required Level-3 page for source files that register clipping tests is [`vktClippingTests.md`](../testfiles/clipping/vktClippingTests.md).
- No clipping-specific objectives were found in the inspected [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L1-L13); source code and mustpass entries are the evidence base for category-specific coverage.
