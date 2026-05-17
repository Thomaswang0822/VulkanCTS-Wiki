# vktDrawShaderViewportIndexTests.cpp

## Overview

Tests for the use of `gl_ViewportIndex` in vertex, fragment, and tessellation shaders, as enabled by the `VK_EXT_shader_viewport_index_layer` extension. The tests render colored rectangles into multiple viewports using `gl_ViewportIndex` to direct geometry to specific viewports, then verify the composite image against a reference grid.

## Role

Validates that implementations correctly support writing to `gl_ViewportIndex` from vertex, fragment, and tessellation evaluation shaders. The `gl_ViewportIndex` built-in allows a shader to specify which viewport a primitive should be rendered to. The tests render a grid of colored rectangles, one per viewport, and verify that each viewport contains its expected rectangle.

## Source Code

- [vktDrawShaderViewportIndexTests.cpp](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.shader_viewport_index
├── vertex_shader_1
├── vertex_shader_2
├── vertex_shader_3
├── vertex_shader_4
├── vertex_shader_5
├── vertex_shader_6
├── vertex_shader_7
├── vertex_shader_8
├── vertex_shader_9
├── vertex_shader_10
├── vertex_shader_11
├── vertex_shader_12
├── vertex_shader_13
├── vertex_shader_14
├── vertex_shader_15
├── vertex_shader_16
├── fragment_shader_implicit
├── fragment_shader_1
├── fragment_shader_2
├── fragment_shader_3
├── fragment_shader_4
├── fragment_shader_5
├── fragment_shader_6
├── fragment_shader_7
├── fragment_shader_8
├── fragment_shader_9
├── fragment_shader_10
├── fragment_shader_11
├── fragment_shader_12
├── fragment_shader_13
├── fragment_shader_14
├── fragment_shader_15
├── fragment_shader_16
├── tessellation_shader_1
├── tessellation_shader_2
├── tessellation_shader_3
├── tessellation_shader_4
├── tessellation_shader_5
├── tessellation_shader_6
├── tessellation_shader_7
├── tessellation_shader_8
├── tessellation_shader_9
├── tessellation_shader_10
├── tessellation_shader_11
├── tessellation_shader_12
├── tessellation_shader_13
├── tessellation_shader_14
├── tessellation_shader_15
└── tessellation_shader_16
```

## Test Families

### vertex_shader_N — gl_ViewportIndex written from vertex shader

Renders `N` colored rectangles into `N` viewports using a vertex shader that sets `gl_ViewportIndex = gl_VertexIndex / 6`. The viewports are arranged in a grid pattern covering the render area. Each viewport should contain a full-viewport quad with a unique color. The number of viewports `N` ranges from 1 to 16.

**Shader**: Vertex shader uses `#extension GL_ARB_shader_viewport_layer_array : require` and writes `gl_ViewportIndex`. Fragment shader passes through the interpolated color.

**Test function**: [testVertexShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1002)

**Programs**: [initVertexTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418)

### fragment_shader_implicit — gl_ViewportIndex read implicitly in fragment shader

Tests a single viewport (N=1) where the fragment shader reads `gl_ViewportIndex` via a uniform buffer lookup (`color[gl_ViewportIndex]`). The vertex shader does not write `gl_ViewportIndex` (`writeFromVertex = false`), so the implicit viewport index from the pipeline state is used.

**Shader**: Fragment shader uses a uniform buffer of colors indexed by `gl_ViewportIndex`. Vertex shader does not write `gl_ViewportIndex`.

**Test function**: [testFragmentShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1007)

**Programs**: [initFragmentTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L460)

### fragment_shader_N — gl_ViewportIndex written from vertex, read in fragment

Renders `N` colored rectangles into `N` viewports. The vertex shader writes `gl_ViewportIndex = gl_VertexIndex / 6` (`writeFromVertex = true`), and the fragment shader reads `gl_ViewportIndex` to select a color from a uniform buffer. This tests the interaction between vertex-written viewport index and fragment shader consumption.

**Shader**: Vertex shader writes `gl_ViewportIndex`. Fragment shader reads `gl_ViewportIndex` from a uniform buffer color array.

**Test function**: [testFragmentShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1007)

**Programs**: [initFragmentTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L460)

### tessellation_shader_N — gl_ViewportIndex written from tessellation evaluation shader

Renders `N` colored rectangles into `N` viewports using a tessellation evaluation shader that sets `gl_ViewportIndex = gl_PrimitiveID / 2`. The vertex shader passes data through, the tessellation control shader sets all tessellation levels to 1.0 (pass-through), and the evaluation shader writes `gl_ViewportIndex` and interpolates position and color.

**Shader**: Tessellation evaluation shader uses `#extension GL_ARB_shader_viewport_layer_array : require` and writes `gl_ViewportIndex`. Requires `tessellationShader` feature.

**Test function**: [testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1012)

**Programs**: [initTessellationTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L506)

**Registration**: [createShaderViewportIndexTests](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1087)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| numViewports | 1..16 | Number of viewports to render into |
| shaderStage | vertex, fragment, tessellation | Which shader stage writes/reads gl_ViewportIndex |
| writeFromVertex | false, true | Whether the vertex shader also writes gl_ViewportIndex (fragment tests only) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `DEVICE_CORE_FEATURE_MULTI_VIEWPORT` | Always | [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1071-L1072) |
| `VK_EXT_shader_viewport_index_layer` | Always | [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1073) |
| `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` | For tessellation_shader_* tests | [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1078-L1079) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1081-L1082) |
| `maxViewports >= 16` | Always (validated at test time) | [checkSupport](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1075-L1076) |

## Verification Methods

| Method | Description | Source |
|--------|-------------|--------|
| Float threshold comparison | `tcu::floatThresholdCompare` with `Vec4(0.02f)` threshold against a reference image containing a colored grid of rectangles on a gray background | [testVertexFragmentShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L994-L996), [testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1062-L1064) |

## Notes

- The render size is 128x128 with `VK_FORMAT_R8G8B8A8_UNORM` color format.
- Unlike the shader_layer tests which use layered framebuffers, these tests use a single-layer framebuffer with multiple viewports arranged in a grid.
- The `fragment_shader_implicit` test is a special case with a single viewport where the fragment shader reads `gl_ViewportIndex` without the vertex shader writing it, testing the implicit viewport index assignment.
- The fragment shader tests use a uniform buffer bound via a descriptor set to provide per-viewport colors, while the vertex and tessellation tests pass colors as vertex attributes.
- When the Vulkan 1.2 context is available, shaders are compiled with SPIR-V 1.5 (`vert_1_2`, `tese_1_2`); otherwise SPIR-V 1.0 is used.
