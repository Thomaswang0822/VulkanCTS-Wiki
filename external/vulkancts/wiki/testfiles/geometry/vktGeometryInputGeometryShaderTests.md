# vktGeometryInputGeometryShaderTests.cpp

## Overview

Tests geometry shader input primitive handling including basic primitives, adjacency, and primitive conversion.

## Source Code

[vktGeometryInputGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp)

## Test Hierarchy

```
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
│   ├── vertex_count_0 through vertex_count_12
└── conversion
    ├── triangles_to_points
    ├── lines_to_points
    ├── points_to_lines
    ├── triangles_to_lines
    ├── points_to_triangles
    └── lines_to_triangles
```

## Test Families

### 1. basic_primitive

**Purpose**: Test all basic input primitive types.

**Primitives**: points, lines, line_strip, triangles, triangle_strip, triangle_fan, lines_adjacency, line_strip_adjacency, triangles_adjacency

### 2. triangle_strip_adjacency

**Purpose**: Test triangle strip with adjacency for different vertex counts.

**Tests**: vertex_count_0 through vertex_count_12

### 3. conversion

**Purpose**: Test primitive type conversion in geometry shader.

**Conversions**: triangles→points, lines→points, points→lines, triangles→lines, points→triangles, lines→triangles

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Primitive Type | 9 types | VK_PRIMITIVE_TOPOLOGY_* |
| Vertex Count | 0-12 | For adjacency tests |
| Output Type | POINT, LINE, TRIANGLE | Conversion output type |

## Verification Methods

- Rendering output comparison
- Primitive count verification

## Test Principles

1. **Complete primitive coverage**: Test all input primitive types
2. **Adjacency handling**: Test adjacency primitives with various vertex counts
3. **Type conversion**: Verify primitive type conversion works correctly
