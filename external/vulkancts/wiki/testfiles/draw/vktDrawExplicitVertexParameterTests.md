# Explicit Vertex Parameter Tests

## Overview

Tests for the `VK_AMD_shader_explicit_vertex_parameter` extension, which provides the `interpolateAtVertexAMD` GLSL built-in function and `__explicitInterpAMD` interpolation qualifier. These allow the fragment shader to directly fetch vertex attribute values at specific vertices of the primitive, enabling custom interpolation using barycentric coordinates.

## Role

Validates that Vulkan implementations correctly support the `VK_AMD_shader_explicit_vertex_parameter` extension by comparing the result of manual barycentric interpolation (using `interpolateAtVertexAMD` and `gl_BaryCoord*AMD` variables) against the result of standard interpolation qualifiers (smooth or noperspective, with optional centroid or sample auxiliary qualifiers). The fragment shader writes both the expected (standard interpolation) and actual (manual barycentric) values to a storage buffer, and the test compares them per-pixel with a tolerance threshold.

## Source Code

- [vktDrawExplicitVertexParameterTests.cpp](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.explicit_vertex_parameter
├── smooth_samples_1
├── noperspective_samples_1
├── smooth_samples_2
├── noperspective_samples_2
├── smooth_sample_samples_2
├── noperspective_sample_samples_2
├── smooth_centroid_samples_2
├── noperspective_centroid_samples_2
├── smooth_samples_4
├── noperspective_samples_4
├── smooth_sample_samples_4
├── noperspective_sample_samples_4
├── smooth_centroid_samples_4
├── noperspective_centroid_samples_4
├── smooth_samples_8
├── noperspective_samples_8
├── smooth_sample_samples_8
├── noperspective_sample_samples_8
├── smooth_centroid_samples_8
├── noperspective_centroid_samples_8
├── smooth_samples_16
├── noperspective_samples_16
├── smooth_sample_samples_16
├── noperspective_sample_samples_16
├── smooth_centroid_samples_16
├── noperspective_centroid_samples_16
├── smooth_samples_32
├── noperspective_samples_32
├── smooth_sample_samples_32
├── noperspective_sample_samples_32
├── smooth_centroid_samples_32
├── noperspective_centroid_samples_32
├── smooth_samples_64
├── noperspective_samples_64
├── smooth_sample_samples_64
├── noperspective_sample_samples_64
├── smooth_centroid_samples_64
└── noperspective_centroid_samples_64
```

## Test Families

### smooth_samples_* — Smooth interpolation with explicit vertex parameter

Tests the `gl_BaryCoordSmoothAMD` barycentric variable with smooth interpolation. The fragment shader manually computes the interpolated value using barycentric coordinates and `interpolateAtVertexAMD`, then compares it against the standard `smooth`-interpolated value. Tests vary the sample count from 1 to 64.

### noperspective_samples_* — Noperspective interpolation with explicit vertex parameter

Tests the `gl_BaryCoordNoPerspAMD` barycentric variable with noperspective interpolation. The manual barycentric interpolation result is compared against the standard `noperspective`-interpolated value. Tests vary the sample count.

### smooth_sample_samples_* — Smooth interpolation with sample auxiliary qualifier

Tests `gl_BaryCoordSmoothSampleAMD` with the `sample` auxiliary qualifier on the standard interpolation variable. Requires sample rate shading. Only available for sample counts >= 2.

### noperspective_sample_samples_* — Noperspective interpolation with sample auxiliary qualifier

Tests `gl_BaryCoordNoPerspSampleAMD` with the `sample` auxiliary qualifier. Requires sample rate shading. Only available for sample counts >= 2.

### smooth_centroid_samples_* — Smooth interpolation with centroid auxiliary qualifier

Tests `gl_BaryCoordSmoothCentroidAMD` with the `centroid` auxiliary qualifier on the standard interpolation variable. Only available for sample counts >= 2.

### noperspective_centroid_samples_* — Noperspective interpolation with centroid auxiliary qualifier

Tests `gl_BaryCoordNoPerspCentroidAMD` with the `centroid` auxiliary qualifier. Only available for sample counts >= 2.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Interpolation | smooth, noperspective | The interpolation mode for both the standard and barycentric-computed values |
| Sample count | 1, 2, 4, 8, 16, 32, 64 | Number of MSAA samples; reduced to 4 max when using secondary command buffers |
| Auxiliary qualifier | none, sample, centroid | Additional qualifier on the standard interpolation variable; `none` only for 1 sample, `sample`/`centroid` for >= 2 samples |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_AMD_shader_explicit_vertex_parameter` | Always required | [vktDrawExplicitVertexParameterTests.cpp#L246](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L246) |
| `framebufferColorSampleCounts` | Sample count must be supported | [vktDrawExplicitVertexParameterTests.cpp#L248-L249](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L248-L249) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawExplicitVertexParameterTests.cpp#L251-L252](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L251-L252) |
| `sampleRateShading` feature | Always required | [vktDrawExplicitVertexParameterTests.cpp#L254](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L254) |

## Verification Methods

- **Storage buffer value comparison**: The fragment shader writes both the expected value (from standard interpolation) and the computed value (from manual barycent interpolation using `interpolateAtVertexAMD`) to a storage buffer as `vec4(expected, res, 0, 0)` at [vktDrawExplicitVertexParameterTests.cpp#L312](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L312). The CPU-side test reads back the buffer and checks that `abs(expected - res) <= 0.0005` for every value at [vktDrawExplicitVertexParameterTests.cpp#L616-L624](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L616-L624).
- **Visual feedback**: The fragment shader also outputs green (pass) or red (fail) to the color attachment based on the per-fragment comparison at [vktDrawExplicitVertexParameterTests.cpp#L314-L318](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L314-L318), though the primary verification is via the storage buffer.

## Notes

- The render size is 16x16 pixels at [vktDrawExplicitVertexParameterTests.cpp#L76-L79](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L76-L79).
- The test draws a triangle strip (4 vertices forming 2 triangles) with varying depth values to ensure perspective-correct interpolation is exercised at [vktDrawExplicitVertexParameterTests.cpp#L429-L439](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L429-L439).
- The `__explicitInterpAMD` qualifier is used on the vertex output / fragment input that is fetched via `interpolateAtVertexAMD`, while the standard interpolation qualifier (smooth/noperspective with optional centroid/sample) is used on a separate variable for comparison.
- Auxiliary qualifiers (`centroid`, `sample`) are only tested with sample counts >= 2, since they have no effect with a single sample at [vktDrawExplicitVertexParameterTests.cpp#L753-L754](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L753-L754).
- When using secondary command buffers with dynamic rendering, only sample counts 1, 2, and 4 are tested to reduce test count at [vktDrawExplicitVertexParameterTests.cpp#L747-L748](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L747-L748).
