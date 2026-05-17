# vktGeometryVaryingGeometryShaderTests.cpp

## Overview

[`vktGeometryVaryingGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L1) implements the [`varying`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L275) subgroup. It focuses on how varying data is produced by the vertex shader, consumed by the geometry shader, and forwarded to the fragment shader under a small set of explicitly enumerated output configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryVaryingGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L1)
- Shared base instance: [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37)
- Registration parent: [`vktGeometryTests.cpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L49)

## Registration Hierarchy

This file contributes the subgroup returned by [`createVaryingGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L273), which is attached under geometry by [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L49).

```text
geometry.varying
├── vertex_no_op_geometry_out_1
├── vertex_out_0_geometry_out_1
├── vertex_out_0_geometry_out_2
├── vertex_out_1_geometry_out_0
└── vertex_out_1_geometry_out_2
```

Source: [`varyingTests[]`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L279).

## Test Families

### vertex_no_op_geometry_out_1 — No vertex-stage outputs, one geometry-stage output

[`vertex_no_op_geometry_out_1`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L280) uses [`VERTEXT_NO_OP`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L59) together with [`GEOMETRY_ONE`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L66). In this configuration, the geometry shader synthesizes fallback input color at [`inputColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L187) and forwards one varying to the fragment stage via [`v_frag_0`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L175).

### vertex_out_0_geometry_out_1 — Position-only vertex output, one geometry-stage output

[`vertex_out_0_geometry_out_1`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L281) uses [`VERTEXT_ZERO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L60) with [`GEOMETRY_ONE`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L66). The vertex shader writes only [`gl_Position`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L147), while the geometry shader still forwards one fragment-stage varying.

### vertex_out_0_geometry_out_2 — Position-only vertex output, two geometry-stage outputs

[`vertex_out_0_geometry_out_2`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L282) keeps the same position-only vertex stage but upgrades the geometry output mode to [`GEOMETRY_TWO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L67), causing the geometry shader to write both [`v_frag_0`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L175) and [`v_frag_1`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L177).

### vertex_out_1_geometry_out_0 — Vertex-stage varying present, no geometry-stage varying outputs

[`vertex_out_1_geometry_out_0`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L283) combines [`VERTEXT_ONE`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L61) with [`GEOMETRY_ZERO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L65). The vertex shader writes [`v_geom_0`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L151), but the geometry stage does not declare fragment varyings, so the fragment shader falls back to [`fragColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L256).

### vertex_out_1_geometry_out_2 — Vertex-stage varying present, two geometry-stage outputs

[`vertex_out_1_geometry_out_2`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L284) combines vertex-produced varying data with the richest geometry-stage output mode. The geometry shader reads vertex input color from [`v_geom_0[]`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L172) and writes the split outputs combined later in the fragment shader at [`fragColor = v_frag_0 + v_frag_1.yxzw`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L260).

Collectively, these cases are expressed as [`VaryingTestSpec`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L70) combinations in [`varyingTests[]`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L279). They verify selected combinations of vertex-stage output production and geometry-stage forwarding behavior.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Vertex output mode | [`VERTEXT_NO_OP`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L59), [`VERTEXT_ZERO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L60), [`VERTEXT_ONE`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L61) |
| Geometry output mode | [`GEOMETRY_ZERO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L65), [`GEOMETRY_ONE`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L66), [`GEOMETRY_TWO`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L67) |
| Input topology | Fixed to [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L86) in the test instance constructor |
| Draw vertex count | Fixed to [`3`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L93) in [`genVertexAttribData()`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L91) |

## Support / Feature Requirements

Support checking is explicit in [`VaryingTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L125), which requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L127).

## Verification Methods

This file does not define a local CPU-side verification routine in the inspected range. Instead, it relies on the shared geometry render-test path through [`GeometryVaryingTestInstance`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L77), which derives from [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37).

Within the inspected code, expected behavior is encoded into the generated shaders themselves:
- the geometry shader either forwards input color or synthesizes fallback red in [`inputColor`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L185) and [`inputColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L187)
- the fragment shader selects output based on geometry-output mode at [`fragColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L256), [`fragColor = v_frag_0`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L258), and [`fragColor = v_frag_0 + v_frag_1.yxzw`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L260)

Because the shared `iterate()` implementation was not inspected here, this document only claims the verification strategy visible from this file: shader-generated observable color differences interpreted by the common geometry render path.

## Test Principles Observed

- **Small explicit combinatorics**: the file uses a short, manually curated set of [`VaryingTestSpec`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L70) cases instead of exhaustive enumeration
- **Cross-stage interface focus**: tests are structured around whether data is produced at the vertex stage and how many outputs the geometry stage forwards
- **Shader-defined observability**: expected outcomes are turned into fragment colors directly in the generated shader code

## Notes / Uncertainties

- The earlier wiki example used different case names; this regenerated documentation follows the actual registered names in [`varyingTests[]`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L279).
- The exact pixel-comparison helper used at runtime is outside the inspected snippet set and is therefore not asserted here beyond the shared render-path dependency.
