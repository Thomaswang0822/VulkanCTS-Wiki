# vktGeometryBuiltinVariableGeometryShaderTests.cpp

## Overview

Tests geometry shader built-in variables including gl_PointSize, gl_PrimitiveID, and gl_Position.

## Source Code

[vktGeometryBuiltinVariableGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp)

## Test Hierarchy

```
builtin
├── point_size
├── primitive_id_in
├── primitive_id
└── position
```

## Test Families

### 1. point_size

**Purpose**: Test gl_PointSize built-in variable in geometry shader.

### 2. primitive_id_in

**Purpose**: Test gl_PrimitiveIDIn built-in input variable.

### 3. primitive_id

**Purpose**: Test gl_PrimitiveID built-in output variable.

### 4. position

**Purpose**: Test gl_Position built-in variable.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Variable Test | POINT_SIZE, PRIMITIVE_ID_IN, PRIMITIVE_ID, POSITION | Built-in to test |
| Indices Test | true/false | Use indexed drawing |

## Verification Methods

- Image comparison
- Built-in value verification

## Test Principles

1. **Built-in coverage**: Test all geometry shader built-in variables
2. **Input/output verification**: Verify both input and output built-ins
