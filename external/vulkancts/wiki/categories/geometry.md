# geometry

## Overview

The geometry category tests geometry shader functionality in Vulkan. Geometry shaders allow manipulation of geometric data between vertex and fragment shaders, enabling operations like geometry amplification, transformation, and layered rendering.

## Test Files

This category contains 8 CPP test files:

| # | File | Description |
|---|------|-------------|
| 1 | [vktGeometryTests.md](testfiles/geometry/vktGeometryTests.md) | Main test registration file |
| 2 | [vktGeometryBasicGeometryShaderTests.md](testfiles/geometry/vktGeometryBasicGeometryShaderTests.md) | Basic GS functionality tests |
| 3 | [vktGeometryInputGeometryShaderTests.md](testfiles/geometry/vktGeometryInputGeometryShaderTests.md) | Input primitive tests |
| 4 | [vktGeometryLayeredRenderingTests.md](testfiles/geometry/vktGeometryLayeredRenderingTests.md) | Layered rendering tests |
| 5 | [vktGeometryInstancedRenderingTests.md](testfiles/geometry/vktGeometryInstancedRenderingTests.md) | Instanced rendering tests |
| 6 | [vktGeometryVaryingGeometryShaderTests.md](testfiles/geometry/vktGeometryVaryingGeometryShaderTests.md) | Varying data tests |
| 7 | [vktGeometryEmitGeometryShaderTests.md](testfiles/geometry/vktGeometryEmitGeometryShaderTests.md) | Emit operation tests |
| 8 | [vktGeometryBuiltinVariableGeometryShaderTests.md](testfiles/geometry/vktGeometryBuiltinVariableGeometryShaderTests.md) | Built-in variable tests |

## Key Test Families

### 1. Input Primitive Tests

**File**: [vktGeometryInputGeometryShaderTests.md](testfiles/geometry/vktGeometryInputGeometryShaderTests.md)

Tests geometry shader input handling including:
- Basic primitives (points, lines, triangles)
- Adjacency primitives
- Primitive type conversion

### 2. Output Count Tests

**File**: [vktGeometryBasicGeometryShaderTests.md](testfiles/geometry/vktGeometryBasicGeometryShaderTests.md)

Tests geometry shader output vertex counts including:
- Fixed output counts (10, 128 vertices)
- Dynamic output via attribute, uniform, or texture
- Side effects handling

### 3. Layered Rendering

**File**: [vktGeometryLayeredRenderingTests.md](testfiles/geometry/vktGeometryLayeredRenderingTests.md)

Tests rendering to multiple layers using geometry shaders:
- Single/multi-layer rendering
- gl_Layer verification
- Per-layer content
- Secondary command buffer support

### 4. Instanced Rendering

**File**: [vktGeometryInstancedRenderingTests.md](testfiles/geometry/vktGeometryInstancedRenderingTests.md)

Tests combining draw instancing with geometry shader invocations:
- Various instance counts (1, 2, 4, 8)
- Various GS invocation counts (1-127)

### 5. Built-in Variables

**File**: [vktGeometryBuiltinVariableGeometryShaderTests.md](testfiles/geometry/vktGeometryBuiltinVariableGeometryShaderTests.md)

Tests geometry shader built-in variables:
- gl_PointSize
- gl_PrimitiveID, gl_PrimitiveIDIn
- gl_Position

## Common Parameters

| Parameter | Values |
|-----------|--------|
| Primitive Topology | POINT_LIST, LINE_LIST, TRIANGLE_LIST, etc. |
| View Type | 1D, 2D, 3D, CUBE |
| Output Vertices | 0, 1, 10, 128, etc. |

## Verification Methods

- Image comparison against reference
- Fuzzy comparison
- Vertex count verification

## Test Principles

1. **Feature coverage**: All geometry shader features tested
2. **Limit testing**: Test minimum and extended limits
3. **Edge cases**: Zero output, maximum output, degenerate primitives

## Statistics

- **CPP Test Files**: 8
- **Test Families**: ~7 major families
- **Individual Tests**: Multiple (parameter explosion within each file)
