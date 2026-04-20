# vktGeometryVaryingGeometryShaderTests.cpp

## Overview

Tests varying data passing through geometry shaders from vertex shader to fragment shader.

## Source Code

[vktGeometryVaryingGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp)

## Test Hierarchy

```
varying
├── vertex_zero_geometry_zero
├── vertex_zero_geometry_one
├── vertex_zero_geometry_two
├── vertex_one_geometry_zero
├── vertex_one_geometry_one
└── vertex_one_geometry_two
```

## Test Families

### Varying Output Tests

**Purpose**: Verify correct passing of varying data through geometry shader stages.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Vertex Outputs | ZERO, ONE | Number of vertex outputs |
| Geometry Outputs | ZERO, ONE, TWO | Number of geometry outputs |

## Verification Methods

- Image comparison against reference

## Test Principles

1. **Data passing**: Verify varying data passes correctly through all stages
2. **Output combination**: Test all combinations of vertex and geometry outputs
