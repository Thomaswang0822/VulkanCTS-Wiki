# vktGeometryVaryingGeometryShaderTests.cpp

## Overview

[`vktGeometryVaryingGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:1) implements the [`varying`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:275) subgroup. It focuses on how varying data is produced by the vertex shader, consumed by the geometry shader, and forwarded to the fragment shader under a small set of explicitly enumerated output configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryVaryingGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:1)
- Shared base instance: [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37)
- Registration parent: [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp:49)

## Registration Path

This file contributes the subgroup returned by [`createVaryingGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:273), which is attached under geometry by [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:49).

## Test Hierarchy

```text
varying
├── vertex_no_op_geometry_out_1
├── vertex_out_0_geometry_out_1
├── vertex_out_0_geometry_out_2
├── vertex_out_1_geometry_out_0
└── vertex_out_1_geometry_out_2
```

Source: [`varyingTests[]`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:279).

## Test Families

### 1. Vertex output suppression vs geometry output presence

The file distinguishes vertex-stage output modes through [`VertexOutputs`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:57):
- [`VERTEXT_NO_OP`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:59)
- [`VERTEXT_ZERO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:60)
- [`VERTEXT_ONE`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:61)

These control whether the vertex shader writes nothing, only position, or position plus one varying in [`VaryingTest::initPrograms()`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:130).

### 2. Geometry output count variations

Geometry-stage outputs are modeled by [`GeometryOutputs`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:63):
- [`GEOMETRY_ZERO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:65)
- [`GEOMETRY_ONE`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:66)
- [`GEOMETRY_TWO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:67)

The geometry shader conditionally declares and writes fragment varyings at [`v_frag_0`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:175) and [`v_frag_1`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:177).

### 3. Cross-stage propagation combinations

Concrete cases are expressed as [`VaryingTestSpec`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:70) combinations in [`varyingTests[]`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:279). These cases verify selected combinations of:
- vertex shader writes none / position only / position plus one varying
- geometry shader writes zero / one / two varyings to the fragment stage

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Vertex output mode | [`VERTEXT_NO_OP`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:59), [`VERTEXT_ZERO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:60), [`VERTEXT_ONE`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:61) |
| Geometry output mode | [`GEOMETRY_ZERO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:65), [`GEOMETRY_ONE`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:66), [`GEOMETRY_TWO`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:67) |
| Input topology | Fixed to [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:86) in the test instance constructor |
| Draw vertex count | Fixed to [`3`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:93) in [`genVertexAttribData()`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:91) |

## Support / Feature Requirements

Support checking is explicit in [`VaryingTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:125), which requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:127).

## Verification Methods

This file does not define a local CPU-side verification routine in the inspected range. Instead, it relies on the shared geometry render-test path through [`GeometryVaryingTestInstance`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:77), which derives from [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37).

Within the inspected code, expected behavior is encoded into the generated shaders themselves:
- the geometry shader either forwards input color or synthesizes fallback red in [`inputColor`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:185) and [`inputColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:187)
- the fragment shader selects output based on geometry-output mode at [`fragColor = vec4(1.0, 0.0, 0.0, 1.0)`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:256), [`fragColor = v_frag_0`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:257), and [`fragColor = v_frag_0 + v_frag_1.yxzw`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:259)

Because the shared `iterate()` implementation was not inspected here, this document only claims the verification strategy visible from this file: shader-generated observable color differences interpreted by the common geometry render path.

## Test Principles Observed

- **Small explicit combinatorics**: the file uses a short, manually curated set of [`VaryingTestSpec`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:70) cases instead of exhaustive enumeration
- **Cross-stage interface focus**: tests are structured around whether data is produced at the vertex stage and how many outputs the geometry stage forwards
- **Shader-defined observability**: expected outcomes are turned into fragment colors directly in the generated shader code

## Notes / Uncertainties

- The earlier wiki example used different case names; this regenerated documentation follows the actual registered names in [`varyingTests[]`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:279).
- The exact pixel-comparison helper used at runtime is outside the inspected snippet set and is therefore not asserted here beyond the shared render-path dependency.
