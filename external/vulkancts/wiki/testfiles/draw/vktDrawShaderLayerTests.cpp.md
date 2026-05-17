# vktDrawShaderLayerTests.cpp

## Overview

Tests for the use of `gl_Layer` in vertex and tessellation shaders, as enabled by the `VK_EXT_shader_viewport_index_layer` extension. The tests render colored rectangles into multiple framebuffer layers using `gl_Layer` to direct geometry to specific layers, then verify each layer's contents against a per-layer reference image.

## Role

Validates that implementations correctly support writing to `gl_Layer` from vertex and tessellation evaluation shaders. The `gl_Layer` built-in allows a shader to specify which layer of a layered framebuffer a primitive should be rendered to. The tests render a grid of colored rectangles, one per layer, and verify that each layer contains only its expected rectangle.

## Source Code

- [vktDrawShaderLayerTests.cpp](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.shader_layer
├── vertex_shader_1
├── vertex_shader_2
├── vertex_shader_3
├── vertex_shader_4
├── vertex_shader_5
├── vertex_shader_6
├── vertex_shader_7
├── vertex_shader_8
├── vertex_shader_256
├── tessellation_shader_1
├── tessellation_shader_2
├── tessellation_shader_3
├── tessellation_shader_4
├── tessellation_shader_5
├── tessellation_shader_6
├── tessellation_shader_7
├── tessellation_shader_8
└── tessellation_shader_256
```

Note: When the dynamic rendering variant uses secondary command buffers, the number of test cases is reduced (odd-indexed entries from the layer count list are skipped).

## Test Families

### vertex_shader_N — gl_Layer written from vertex shader

Renders `N` colored rectangles into `N` framebuffer layers using a vertex shader that sets `gl_Layer = gl_VertexIndex / 6`. Each layer should contain exactly one rectangle with a unique color, while the rest of the layer is filled with a gray clear color. The number of layers `N` is drawn from the set {1, 2, 3, 4, 5, 6, 7, 8, 256}.

**Shader**: Vertex shader uses `#extension GL_ARB_shader_viewport_layer_array : require` and writes `gl_Layer`. Fragment shader passes through the interpolated color.

**Test function**: [testVertexShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L883)

**Programs**: [initVertexTestPrograms](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L349)

### tessellation_shader_N — gl_Layer written from tessellation evaluation shader

Renders `N` colored rectangles into `N` framebuffer layers using a tessellation evaluation shader that sets `gl_Layer = gl_PrimitiveID / 2`. The vertex shader passes data through, the tessellation control shader sets all tessellation levels to 1.0 (pass-through), and the evaluation shader writes `gl_Layer` and interpolates position and color.

**Shader**: Tessellation evaluation shader uses `#extension GL_ARB_shader_viewport_layer_array : require` and writes `gl_Layer`. Requires tessellationShader feature.

**Test function**: [testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L948)

**Programs**: [initTessellationTestPrograms](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393)

**Registration**: [createShaderLayerTests](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| numLayers | 1, 2, 3, 4, 5, 6, 7, 8, 256 | Number of framebuffer layers to render into |
| shaderStage | vertex, tessellation | Which shader stage writes gl_Layer |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `DEVICE_CORE_FEATURE_MULTI_VIEWPORT` | Always | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L864-L865) |
| `VK_EXT_shader_viewport_index_layer` | Always | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L866) |
| `tessellationShader` feature | For tessellation_shader_* tests | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L871-L872) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L868-L869) |
| `maxFramebufferLayers >= 256` | Always (validated at test time) | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L875-L877) |
| `maxViewports >= 16` | Always (validated at test time) | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L879-L880) |

## Verification Methods

| Method | Description | Source |
|--------|-------------|--------|
| Per-layer float threshold comparison | For each layer, `tcu::floatThresholdCompare` with `Vec4(0.02f)` threshold against a reference image containing a single colored rectangle on a gray background | [testVertexShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L932-L942), [testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L994-L1006) |

## Notes

- The render size is 256x256 with `VK_FORMAT_R8G8B8A8_UNORM` color format.
- The layered framebuffer uses `VK_IMAGE_VIEW_TYPE_2D_ARRAY` for the color attachment.
- When the Vulkan 1.2 context is available, shaders are compiled with SPIR-V 1.5 (`vert_1_2`, `tese_1_2`); otherwise SPIR-V 1.0 is used.
- The `Renderer` helper class manages the layered framebuffer, pipeline, and command buffer recording for both renderpass and dynamic rendering variants.
- The `generateGrid` function divides the render area into a grid of cells, one per layer, and `generateVertices` creates two triangles per cell.
