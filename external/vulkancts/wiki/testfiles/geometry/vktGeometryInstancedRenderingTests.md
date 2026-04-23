# vktGeometryInstancedRenderingTests.cpp

## Overview

[`vktGeometryInstancedRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1) implements the [`instanced`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L425) subgroup for geometry shaders. It combines draw instancing with geometry-shader invocation counts and validates the rendered image against a CPU-generated reference.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryInstancedRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1)
- Related helper concepts used in this file:
  - [`TestParams`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58)
  - [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271)
  - [`test()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365)
  - [`checkSupport()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409)

## Registration Path

This file contributes the subgroup returned by [`createInstancedRenderingTests()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423), which is attached under geometry by [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L48).

Each concrete case is registered with [`addFunctionCaseWithPrograms()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L451), using file-local [`checkSupport()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409), [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271), and [`test()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365).

## Test Hierarchy

```text
instanced
├── draw_1_instances_1_geometry_invocations
├── draw_1_instances_2_geometry_invocations
├── draw_1_instances_8_geometry_invocations
├── draw_1_instances_32_geometry_invocations
├── draw_1_instances_64_geometry_invocations
├── draw_1_instances_127_geometry_invocations
├── draw_2_instances_1_geometry_invocations
├── ...
└── draw_8_instances_127_geometry_invocations
```

The names are constructed in [`createInstancedRenderingTests()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L443) from Cartesian products of draw-instance and invocation-count arrays.

## Test Families

### 1. Draw-instance count sweep

The outer loop iterates over [`drawInstanceCases[]`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L427), covering:
- 1 instance
- 2 instances
- 4 instances
- 8 instances

These values determine how many input points are drawn in [`vk.cmdDraw(..., numDrawInstances, ...)`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L196).

### 2. Geometry-shader invocation count sweep

The inner loop iterates over [`invocationCases[]`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433), covering:
- 1
- 2
- 8
- 32
- 64
- 127

The geometry shader declaration embeds the invocation count in [`layout(points, invocations = params.numInvocations) in;`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L299).

### 3. Combined instancing + GS invocation coverage

Each registered case exercises one combination of:
- draw-instance count from [`TestParams::numDrawInstances`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L60)
- geometry-shader invocation count from [`TestParams::numInvocations`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L61)

The intended visible behavior is that each drawn instance produces multiple quads, one per geometry-shader invocation, with position and color derived from shader logic mirrored by the CPU reference generator in [`generateReferenceImage()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L246).

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Draw instances | [`{1, 2, 4, 8}`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L427) |
| Geometry invocations | [`{1, 2, 8, 32, 64, 127}`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433) |
| Render size | [`128 x 128`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L371) |
| Color format | [`VK_FORMAT_R8G8B8A8_UNORM`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L372) |
| Per-instance input positions | Randomized but deterministic positions produced by [`generatePerInstancePosition()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L205) using seed [`1234`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L207) |

## Support / Feature Requirements

The file-local support check in [`checkSupport()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409) requires:
- [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L411)
- sufficient [`maxGeometryShaderInvocations`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L413) for the requested invocation count

The comment in [`createInstancedRenderingTests()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L421) also explains why shaders are generated for fixed invocation counts ahead of execution rather than from a runtime-queried limit.

## Verification Methods

This file contains explicit file-local reference generation and image comparison.

### 1. CPU reference generation

[`generateReferenceImage()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L246) mirrors the geometry shader by drawing colored rectangles into a software image, using the same positional and color logic described in the shader comment at [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L294).

### 2. Fuzzy image comparison

[`test()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365) compares rendered output against the generated reference using [`tcu::fuzzyCompare()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L401) with threshold [`0.01f`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L402).

### 3. Deterministic randomization

The rendered reference remains reproducible because per-instance positions come from a fixed-seed RNG in [`generatePerInstancePosition()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L207).

## Test Principles Observed

- **Cartesian combination coverage**: the file systematically combines instance counts with GS invocation counts in nested loops at [`createInstancedRenderingTests()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L438)
- **Shader/reference lockstep**: the shader is explicitly intended to stay synchronized with the CPU reference path, noted in [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L294)
- **Limit-sensitive coverage**: invocation counts include both required values and larger opportunistic values, documented in [`invocationCases[]`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L434)
- **Visual verification over counts alone**: correctness is determined from rendered quads and colors, not just API success

## Notes / Uncertainties

- The file comment states that values 32 are required by the Vulkan spec and 64/127 are attempted opportunistically in the current code comment at [`invocationCases[]`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L434); this document preserves that wording without expanding it beyond the comment.
