# vktGeometryInputGeometryShaderTests.cpp

## Overview

[`vktGeometryInputGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:1) implements the [`input`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:262) subgroup of the geometry category. It exercises how geometry shaders consume different Vulkan primitive topologies, adjacency forms, and primitive-type conversions by expanding input primitives into rendered output.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryInputGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:1)
- Shared base used by generated test instances: [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37)
- Shared primitive helpers: [`PrimitiveTestSpec`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:47), [`inputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:306), [`outputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:331), [`calcOutputVertices()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:349)

## Registration Path

This file contributes the subgroup returned by [`createInputGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:260), which is attached under the geometry category by [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:45).

## Test Hierarchy

```text
input
├── basic_primitive
│   ├── points
│   ├── lines
│   ├── line_strip
│   ├── triangles
│   ├── triangle_strip
│   ├── triangle_fan
│   ├── lines_adjacency
│   ├── line_strip_adjacency
│   └── triangles_adjacency
├── triangle_strip_adjacency
│   ├── vertex_count_0
│   ├── vertex_count_1
│   ├── ...
│   └── vertex_count_12
└── conversion
    ├── triangles_to_points
    ├── lines_to_points
    ├── points_to_lines
    ├── triangles_to_lines
    ├── points_to_triangles
    └── lines_to_triangles
```

Source: [`createInputGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:260).

## Test Families

### 1. Basic primitive expansion

The [`basic_primitive`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:263) subgroup iterates over [`inputPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:267) and creates one [`GeometryExpanderRenderTest`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:112) per input topology.

Observed input families include:
- point list [`points`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:268)
- line list / line strip [`lines`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:269), [`line_strip`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:270)
- triangle list / strip / fan [`triangles`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:271), [`triangle_strip`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:272), [`triangle_fan`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:273)
- adjacency forms [`lines_adjacency`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:274), [`line_strip_adjacency`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:275), [`triangles_adjacency`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:276)

### 2. Triangle-strip-adjacency vertex-count sweep

The [`triangle_strip_adjacency`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:264) subgroup creates [`vertex_count_0`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:286) through [`vertex_count_12`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:284) using [`TriangleStripAdjacencyVertexCountTest`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:234).

This family varies only the number of supplied input vertices while keeping the input topology fixed to [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:287).

### 3. Primitive-type conversion

The [`conversion`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:265) subgroup iterates over [`conversionPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:295), covering conversions such as:
- [`triangles_to_points`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:296)
- [`lines_to_points`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:297)
- [`points_to_lines`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:298)
- [`triangles_to_lines`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:299)
- [`points_to_triangles`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:300)
- [`lines_to_triangles`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:301)

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Input primitive topology | [`PrimitiveTestSpec`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:47) values in [`inputPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:267) and [`conversionPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:295) |
| Output primitive topology | Chosen per [`PrimitiveTestSpec::outputType`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:51), e.g. point-list, line-strip, triangle-strip in [`conversionPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:295) |
| Number of input vertices | 0 through 12 in the adjacency sweep loop at [`createInputGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:284) |
| Point-size path | Optional point-size geometry program emitted only when output topology is point list in [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:167) |

## Support / Feature Requirements

Support checking is implemented in [`GeometryExpanderRenderTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:134):
- requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:136)
- rejects unsupported triangle-fan input on portability-subset implementations when [`triangleFans`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:141) is false

## Verification Methods

This file relies on the shared [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37) execution path for rendering and verification. In the inspected helper code, shared geometry utilities expose:
- topology-to-GLSL translation via [`inputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:306) and [`outputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:331)
- reference-image comparison through [`compareWithFileImage()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:412), which uses both [`tcu::fuzzyCompare()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:418) and [`tcu::intThresholdPositionDeviationCompare()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:420)

From the inspected portion of this file itself, no file-local verifier is defined; verification is delegated to the shared render-test base and helper utilities.

## Test Principles Observed

- **Topology coverage through data-driven specs**: one common test class is reused over arrays of [`PrimitiveTestSpec`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:47)
- **Shader generation follows topology mapping**: geometry shader source is assembled from [`inputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:306), [`outputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:331), and [`calcOutputVertices()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:349)
- **Adjacency edge coverage**: the dedicated vertex-count sweep focuses on how strip-with-adjacency input behaves under varying vertex counts
- **Conversion coverage**: conversions are explicitly modeled by pairing one input topology with a different output topology in [`conversionPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:295)

## Notes / Uncertainties

- The exact pixel/reference expectations are implemented through shared geometry helpers and the shared render-test base; those details are only partially visible from the inspected files.
- The file tests input primitive handling and conversion behavior through rendered output, but the current documentation avoids stronger statements about exhaustiveness beyond the explicitly registered topology list.
