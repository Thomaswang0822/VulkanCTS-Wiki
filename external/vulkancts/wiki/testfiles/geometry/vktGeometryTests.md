# vktGeometryTests.cpp

## Overview

Main test file for geometry shader tests. Includes and registers all geometry shader test sub-groups.

## Source Code

[vktGeometryTests.cpp](../../../../modules/vulkan/geometry/vktGeometryTests.cpp)

## Test Hierarchy

```
geometry
├── input                    # Input primitive tests
├── basic                    # Basic geometry shader functionality
├── layered                  # Layered rendering tests
├── instanced                # Instanced rendering tests
├── varying                  # Varying output tests
├── emit                     # Emit operations tests
└── builtin                  # Built-in variable tests
```

## Test Families

### 1. input

**Purpose**: Tests for geometry shader input primitives.

**Source**: [vktGeometryInputGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp)

### 2. basic

**Purpose**: Tests for basic geometry shader output count and varying output.

**Source**: [vktGeometryBasicGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp)

### 3. layered

**Purpose**: Tests for layered rendering with geometry shaders.

**Source**: [vktGeometryLayeredRenderingTests.cpp](../../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp)

### 4. instanced

**Purpose**: Tests for instanced rendering with geometry shaders.

**Source**: [vktGeometryInstancedRenderingTests.cpp](../../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp)

### 5. varying

**Purpose**: Tests for varying geometry shader outputs.

**Source**: [vktGeometryVaryingGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp)

### 6. emit

**Purpose**: Tests for geometry shader emit operations.

**Source**: [vktGeometryEmitGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp)

### 7. builtin

**Purpose**: Tests for geometry shader built-in variables.

**Source**: [vktGeometryBuiltinVariableGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp)

## Key Source Files

| File | Purpose |
|------|---------|
| [vktGeometryTests.cpp](../../../../modules/vulkan/geometry/vktGeometryTests.cpp) | Main test registration |
| [vktGeometryTestsUtil.cpp](../../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp) | Utility functions |

## Test Principles

1. **Geometry shader feature coverage**: Test all geometry shader features
2. **Primitive type coverage**: Test all input primitive types
3. **Output verification**: Verify correct output vertex counts
