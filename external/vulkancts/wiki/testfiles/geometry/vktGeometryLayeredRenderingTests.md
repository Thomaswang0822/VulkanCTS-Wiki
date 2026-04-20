# vktGeometryLayeredRenderingTests.cpp

## Overview

Tests geometry shader layered rendering functionality including multi-layer rendering and layer-specific operations.

## Source Code

[vktGeometryLayeredRenderingTests.cpp](../../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp)

## Test Hierarchy

```
layered
├── default_layer              # Draw to default layer
├── single_layer               # Draw to single layer
├── all_layers                 # Draw to all layers
├── different_content          # Different content per layer
├── layer_id                   # Verify gl_Layer fragment input
├── invocation_per_layer       # One invocation per layer
├── multiple_layers_per_invocation  # Multiple layers per invocation
├── layered_readback           # Draw to two layers multiple times
└── secondary_cmd_buffer       # Layered rendering with secondary cmd buffer
```

## Test Families

### 1. Default Layer Tests

**Purpose**: Test rendering to default layer.

### 2. Single/Multi-Layer Tests

**Purpose**: Test rendering to single or all layers.

### 3. Layer ID Tests

**Purpose**: Verify gl_Layer built-in variable in fragment shader.

### 4. Invocation Tests

**Purpose**: Test geometry shader invocations per layer.

### 5. Secondary Command Buffer Tests

**Purpose**: Test layered rendering with secondary command buffers.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| Test Type | 9 types | TEST_TYPE_* enum |
| View Type | 1D, 2D, 3D, CUBE | VkImageViewType |
| Num Layers | Variable | Number of array layers |
| Inherit Framebuffer | true/false | Framebuffer inheritance |

## Verification Methods

- Layer-specific image comparison
- gl_Layer value verification

## Test Principles

1. **Layer coverage**: Test all layer configurations
2. **Invocation distribution**: Test invocation-to-layer mapping
3. **Command buffer support**: Test with secondary command buffers
