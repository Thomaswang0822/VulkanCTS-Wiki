# vktGeometryBasicGeometryShaderTests.cpp

## Overview

Tests basic geometry shader functionality including output vertex count and varying output count.

## Source Code

[vktGeometryBasicGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp)

## Test Hierarchy

```
basic
├── output_10                      # Output 10 vertices
├── output_128                     # Output 128 vertices
├── output_10_and_100              # Output 10, then 100 vertices
├── output_100_and_10              # Output 100, then 10 vertices
├── output_0_and_128               # Output 0, then 128 vertices
├── output_128_and_0               # Output 128, then 0 vertices
├── output_vary_by_attribute       # Varying output from attribute
├── output_vary_by_uniform         # Varying output from uniform
├── output_vary_by_texture         # Varying output from texture
├── output_vary_by_attribute_instancing    # With instancing
├── output_vary_by_uniform_instancing      # With instancing
├── output_vary_by_texture_instancing      # With instancing
├── side_effect_with_condition     # Side effects with condition
└── side_effect_with_degenerate    # Side effects with degenerate
```

## Test Families

### 1. Output Count Tests

**Purpose**: Verify geometry shader can output specific number of vertices.

**Tests**: output_10, output_128, output_10_and_100, etc.

### 2. Varying Output Count Tests

**Purpose**: Verify geometry shader can output varying number of vertices based on input.

**Modes**:
- READ_ATTRIBUTE: Output count from vertex attribute
- READ_UNIFORM: Output count from uniform
- READ_TEXTURE: Output count from texture

### 3. Side Effect Tests

**Purpose**: Test side effects in geometry shaders.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Output Count | 0, 10, 100, 128 | Number of vertices to output |
| Varying Source | ATTRIBUTE, UNIFORM, TEXTURE | How output count is determined |
| Instancing Mode | WITH, WITHOUT | Shader instancing mode |
| Side Effect Type | CONDITION, DEGENERATE | Side effect test type |

## Verification Methods

- Image comparison against reference
- Vertex count verification

## Test Principles

1. **Output limits**: Test minimum and maximum output counts
2. **Dynamic output**: Test runtime-determined output counts
3. **Edge cases**: Test zero output and maximum output
