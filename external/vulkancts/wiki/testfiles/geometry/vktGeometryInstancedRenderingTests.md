# vktGeometryInstancedRenderingTests.cpp

## Overview

Tests geometry shader with instanced rendering, combining draw instancing with geometry shader invocations.

## Source Code

[vktGeometryInstancedRenderingTests.cpp](../../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp)

## Test Hierarchy

```
instanced
├── draw_1_instances_1_geometry_invocations
├── draw_1_instances_2_geometry_invocations
├── draw_1_instances_8_geometry_invocations
├── draw_1_instances_32_geometry_invocations
├── draw_1_instances_64_geometry_invocations
├── draw_1_instances_127_geometry_invocations
├── draw_2_instances_1_geometry_invocations
├── ... (all combinations)
└── draw_8_instances_127_geometry_invocations
```

## Test Families

### Instanced Rendering Tests

**Purpose**: Verify correct behavior when combining draw instancing with geometry shader invocations.

**Test naming**: `draw_{N}_instances_{M}_geometry_invocations`

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Draw Instances | 1, 2, 4, 8 | Number of draw instances |
| GS Invocations | 1, 2, 8, 32, 64, 127 | Geometry shader invocations |

## Verification Methods

- Image comparison with reference
- Fuzzy comparison (0.01f threshold)

## Test Principles

1. **Instancing combination**: Test draw instancing with GS invocations
2. **Limit coverage**: Test minimum required (32) and extended (64, 127) invocations
3. **Feature requirement**: Requires geometry shader feature
