# vktGeometryInputGeometryShaderTests.cpp

## Overview

[`vktGeometryInputGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1) implements the [`input`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L262) subgroup of the geometry category. It exercises how geometry shaders consume different Vulkan primitive topologies, adjacency forms, and primitive-type conversions by expanding input primitives into rendered output.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryInputGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1)
- Shared base used by generated test instances: [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37)
- Shared primitive helpers: [`PrimitiveTestSpec`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L47), [`inputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306), [`outputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L331), [`calcOutputVertices()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L349)

## Registration Hierarchy

This file contributes the subgroup returned by [`createInputGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260), which is attached under the geometry category by [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L45).

```text
geometry.input
├── basic_primitive
├── triangle_strip_adjacency
└── conversion
```

Source: [`createInputGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260).

## Test Families

### basic_primitive — Basic primitive expansion

The [`basic_primitive`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L263) subgroup iterates over [`inputPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L267) and creates one [`GeometryExpanderRenderTest`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L112) per input topology.

Observed input families include:
- point list [`points`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L268)
- line list / line strip [`lines`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L269), [`line_strip`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L270)
- triangle list / strip / fan [`triangles`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L271), [`triangle_strip`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L272), [`triangle_fan`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L273)
- adjacency forms [`lines_adjacency`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L274), [`line_strip_adjacency`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L275), [`triangles_adjacency`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L276)

### triangle_strip_adjacency — Triangle-strip-adjacency vertex-count sweep

The [`triangle_strip_adjacency`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L264) subgroup creates [`vertex_count_0`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L286) through [`vertex_count_12`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L286) using [`TriangleStripAdjacencyVertexCountTest`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L234).

This family varies only the number of supplied input vertices while keeping the input topology fixed to [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L287).

### conversion — Primitive-type conversion

The [`conversion`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L265) subgroup iterates over [`conversionPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L295), covering conversions such as:
- [`triangles_to_points`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L296)
- [`lines_to_points`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L297)
- [`points_to_lines`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L298)
- [`triangles_to_lines`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L299)
- [`points_to_triangles`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L300)
- [`lines_to_triangles`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L301)

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Input primitive topology | [`PrimitiveTestSpec`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L47) values in [`inputPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L267) and [`conversionPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L295) |
| Output primitive topology | Chosen per [`PrimitiveTestSpec::outputType`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L51), e.g. point-list, line-strip, triangle-strip in [`conversionPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L295) |
| Number of input vertices | 0 through 12 in the adjacency sweep loop at [`createInputGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L284) |
| Point-size path | Optional point-size geometry program emitted only when output topology is point list in [`initPrograms()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L167) |

## Support / Feature Requirements

Support checking is implemented in [`GeometryExpanderRenderTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L134):
- requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L136)
- rejects unsupported triangle-fan input on portability-subset implementations when [`triangleFans`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L141) is false

## Verification Methods

This file relies on the shared [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37) execution path for rendering and verification. In the inspected helper code, shared geometry utilities expose:
- topology-to-GLSL translation via [`inputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306) and [`outputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L331)
- reference-image comparison through [`compareWithFileImage()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412), which uses both [`tcu::fuzzyCompare()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L418) and [`tcu::intThresholdPositionDeviationCompare()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L420)

From the inspected portion of this file itself, no file-local verifier is defined; verification is delegated to the shared render-test base and helper utilities.

## Test Principles Observed

- **Topology coverage through data-driven specs**: one common test class is reused over arrays of [`PrimitiveTestSpec`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L47)
- **Shader generation follows topology mapping**: geometry shader source is assembled from [`inputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L306), [`outputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L331), and [`calcOutputVertices()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L349)
- **Adjacency edge coverage**: the dedicated vertex-count sweep focuses on how strip-with-adjacency input behaves under varying vertex counts
- **Conversion coverage**: conversions are explicitly modeled by pairing one input topology with a different output topology in [`conversionPrimitives[]`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L295)

## Notes / Uncertainties

- The exact pixel/reference expectations are implemented through shared geometry helpers and the shared render-test base; those details are only partially visible from the inspected files.
- The file tests input primitive handling and conversion behavior through rendered output, but the current documentation avoids stronger statements about exhaustiveness beyond the explicitly registered topology list.
