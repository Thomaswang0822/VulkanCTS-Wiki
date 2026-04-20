# vktGeometryEmitGeometryShaderTests.cpp

## Overview

Tests geometry shader emit operations (EmitVertex, EndPrimitive) with various configurations.

## Source Code

[vktGeometryEmitGeometryShaderTests.cpp](../../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp)

## Test Hierarchy

```
emit
├── emit_1_end_0
├── emit_1_end_1
├── emit_2_end_0
├── emit_2_end_1
├── emit_2_end_2
└── ... (various emit/end combinations)
```

## Test Families

### Emit Operations Tests

**Purpose**: Verify correct behavior of EmitVertex and EndPrimitive in geometry shaders.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Primitive Topology | POINT, LINE, TRIANGLE | Output primitive type |
| Emit Count A | Variable | First primitive emit count |
| End Count A | Variable | First primitive end count |
| Emit Count B | Variable | Second primitive emit count |
| End Count B | Variable | Second primitive end count |

## Verification Methods

- Rendering output comparison

## Test Principles

1. **Emit/End combinations**: Test all emit and end primitive combinations
2. **Multi-primitive output**: Test outputting multiple primitives
