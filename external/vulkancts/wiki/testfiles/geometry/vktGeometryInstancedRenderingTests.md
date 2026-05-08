# vktGeometryInstancedRenderingTests.cpp

## Overview

[`vktGeometryInstancedRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1) implements the [`instanced`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L425) subgroup for geometry shaders. It combines draw instancing with geometry-shader invocation counts and validates the rendered image against a CPU-generated reference.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryInstancedRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1)
- Related helper concepts used in this file:
  - [`TestParams`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58)
  - [`initPrograms()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271)
  - [`test()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365)
  - [`checkSupport()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409)

## Registration Hierarchy

This file contributes the subgroup returned by [`createInstancedRenderingTests()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423), which is attached under geometry by [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L48).

```text
geometry.instanced
├── draw_1_instances_1_geometry_invocations
├── draw_1_instances_2_geometry_invocations
├── draw_1_instances_8_geometry_invocations
├── draw_1_instances_32_geometry_invocations
├── draw_1_instances_64_geometry_invocations
├── draw_1_instances_127_geometry_invocations
├── draw_2_instances_1_geometry_invocations
├── draw_2_instances_2_geometry_invocations
├── draw_2_instances_8_geometry_invocations
├── draw_2_instances_32_geometry_invocations
├── draw_2_instances_64_geometry_invocations
├── draw_2_instances_127_geometry_invocations
├── draw_4_instances_1_geometry_invocations
├── draw_4_instances_2_geometry_invocations
├── draw_4_instances_8_geometry_invocations
├── draw_4_instances_32_geometry_invocations
├── draw_4_instances_64_geometry_invocations
├── draw_4_instances_127_geometry_invocations
├── draw_8_instances_1_geometry_invocations
├── draw_8_instances_2_geometry_invocations
├── draw_8_instances_8_geometry_invocations
├── draw_8_instances_32_geometry_invocations
├── draw_8_instances_64_geometry_invocations
└── draw_8_instances_127_geometry_invocations
```

Each concrete case is registered with [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L451), using file-local [`checkSupport()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409), [`initPrograms()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271), and [`test()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365). The names are constructed in [`createInstancedRenderingTests()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L443) from Cartesian products of draw-instance and invocation-count arrays.

## Test Families

### draw_1_instances_1_geometry_invocations — Single-instance baseline

[`draw_1_instances_1_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) is the smallest observed combination: one drawn instance and one geometry-shader invocation. It serves as the minimal baseline for the shared program and reference-generation path.

### draw_1_instances_2_geometry_invocations — Invocation-count increase without draw-instance increase

[`draw_1_instances_2_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) keeps draw instancing fixed at one instance while increasing the geometry-shader invocation count. The invocation count is embedded directly in [`layout(points, invocations = ... ) in;`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L299).

### draw_1_instances_8_geometry_invocations — Larger single-instance invocation sweep

[`draw_1_instances_8_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) exercises the same single-instance path with a higher invocation count, expanding the number of quads generated from the same input point.

### draw_1_instances_32_geometry_invocations — Spec-required higher invocation count

[`draw_1_instances_32_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) belongs to the set described in the source comment as required by the Vulkan spec in [`invocationCases[]`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433).

### draw_1_instances_64_geometry_invocations — Opportunistic high invocation count

[`draw_1_instances_64_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) extends beyond the minimum required values. The source comment in [`invocationCases[]`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433) describes this as an opportunistic larger value tried when implementations support it.

### draw_1_instances_127_geometry_invocations — Highest single-instance invocation count in the file

[`draw_1_instances_127_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) is the highest observed invocation count paired with a single drawn instance.

### draw_2_instances_1_geometry_invocations — Draw-instance count increase at minimal invocation count

[`draw_2_instances_1_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) increases draw instancing to two while keeping geometry-shader invocations at one. These values determine how many input points are issued in [`vk.cmdDraw(..., numDrawInstances, ...)`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L196).

### draw_2_instances_2_geometry_invocations — Two-by-two combination

[`draw_2_instances_2_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) combines two draw instances with two geometry-shader invocations.

### draw_2_instances_8_geometry_invocations — Two instances with mid-range invocation count

[`draw_2_instances_8_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) expands the same draw-instance count with a larger invocation factor.

### draw_2_instances_32_geometry_invocations — Two instances with higher required invocation count

[`draw_2_instances_32_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) combines two instances with one of the required higher invocation counts.

### draw_2_instances_64_geometry_invocations — Two instances with opportunistic high invocation count

[`draw_2_instances_64_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) uses the opportunistic 64-invocation path with two draw instances.

### draw_2_instances_127_geometry_invocations — Two instances with maximal invocation count

[`draw_2_instances_127_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) pairs two input instances with the highest observed invocation count.

### draw_4_instances_1_geometry_invocations — Mid-range draw-instance count baseline

[`draw_4_instances_1_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) increases the draw-instance dimension to four while preserving the minimal geometry-shader invocation count.

### draw_4_instances_2_geometry_invocations — Four instances with low invocation count

[`draw_4_instances_2_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) combines four draw instances with two geometry-shader invocations.

### draw_4_instances_8_geometry_invocations — Four instances with mid-range invocation count

[`draw_4_instances_8_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) covers a larger combined output space from four input instances and eight geometry-shader invocations per instance.

### draw_4_instances_32_geometry_invocations — Four instances with required high invocation count

[`draw_4_instances_32_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) uses four draw instances and the required 32-invocation geometry path.

### draw_4_instances_64_geometry_invocations — Four instances with opportunistic high invocation count

[`draw_4_instances_64_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) extends the four-instance path to the 64-invocation configuration.

### draw_4_instances_127_geometry_invocations — Four instances with maximal invocation count

[`draw_4_instances_127_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) is the maximal invocation variant for the four-instance draw count.

### draw_8_instances_1_geometry_invocations — Highest draw-instance count baseline

[`draw_8_instances_1_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) uses the largest observed draw-instance count with the minimal invocation count.

### draw_8_instances_2_geometry_invocations — Highest draw-instance count with low invocation count

[`draw_8_instances_2_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) scales the number of input instances while keeping geometry-shader invocations low.

### draw_8_instances_8_geometry_invocations — Highest draw-instance count with mid-range invocation count

[`draw_8_instances_8_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) exercises a larger combined case using eight input instances and eight geometry-shader invocations per instance.

### draw_8_instances_32_geometry_invocations — Highest draw-instance count with required high invocation count

[`draw_8_instances_32_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) combines the largest draw-instance count with the required 32-invocation path.

### draw_8_instances_64_geometry_invocations — Highest draw-instance count with opportunistic high invocation count

[`draw_8_instances_64_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) uses the largest draw-instance count with the opportunistic 64-invocation configuration.

### draw_8_instances_127_geometry_invocations — Maximal Cartesian combination

[`draw_8_instances_127_geometry_invocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L444) is the largest observed Cartesian combination of the file: eight draw instances and 127 geometry-shader invocations.

Across all registered cases, the intended visible behavior is that each drawn instance produces multiple quads, one per geometry-shader invocation, with position and color derived from shader logic mirrored by the CPU reference generator in [`generateReferenceImage()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L246).

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Draw instances | [`{1, 2, 4, 8}`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L427) |
| Geometry invocations | [`{1, 2, 8, 32, 64, 127}`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433) |
| Render size | [`128 x 128`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L371) |
| Color format | [`VK_FORMAT_R8G8B8A8_UNORM`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L372) |
| Per-instance input positions | Randomized but deterministic positions produced by [`generatePerInstancePosition()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L205) using seed [`1234`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L207) |

## Support / Feature Requirements

The file-local support check in [`checkSupport()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409) requires:
- [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L411)
- sufficient [`maxGeometryShaderInvocations`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L413) for the requested invocation count

The comment in [`createInstancedRenderingTests()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L421) also explains why shaders are generated for fixed invocation counts ahead of execution rather than from a runtime-queried limit.

## Verification Methods

This file contains explicit file-local reference generation and image comparison.

### CPU reference generation

[`generateReferenceImage()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L246) mirrors the geometry shader by drawing colored rectangles into a software image, using the same positional and color logic described in the shader comment at [`initPrograms()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L294).

### Fuzzy image comparison

[`test()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365) compares rendered output against the generated reference using [`tcu::fuzzyCompare()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L401) with threshold [`0.01f`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L402).

### Deterministic randomization

The rendered reference remains reproducible because per-instance positions come from a fixed-seed RNG in [`generatePerInstancePosition()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L207).

## Test Principles Observed

- **Cartesian combination coverage**: the file systematically combines instance counts with GS invocation counts in nested loops at [`createInstancedRenderingTests()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L438)
- **Shader/reference lockstep**: the shader is explicitly intended to stay synchronized with the CPU reference path, noted in [`initPrograms()`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L294)
- **Limit-sensitive coverage**: invocation counts include both required values and larger opportunistic values, documented in [`invocationCases[]`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L434)
- **Visual verification over counts alone**: correctness is determined from rendered quads and colors, not just API success

## Notes / Uncertainties

- The file comment states that values 32 are required by the Vulkan spec and 64/127 are attempted opportunistically in the current code comment at [`invocationCases[]`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L434); this document preserves that wording without expanding it beyond the comment.
