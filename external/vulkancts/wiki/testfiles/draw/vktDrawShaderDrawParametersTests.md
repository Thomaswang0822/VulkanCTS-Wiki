# Shader Draw Parameters Tests

## Overview

Tests for the `VK_KHR_shader_draw_parameters` extension, verifying that the built-in shader variables `gl_BaseVertex`, `gl_BaseInstance`, and `gl_DrawID` return correct values in various draw scenarios including direct draws, indexed draws, instanced draws, indirect draws, and multi-draw indirect calls.

## Role

Validates that the shader draw parameters built-ins are correctly populated by the Vulkan implementation. `gl_BaseVertex` must reflect the vertex offset for indexed draws and zero for non-indexed draws. `gl_BaseInstance` must reflect the first instance value for instanced draws. `gl_DrawID` must reflect the index of the current draw within a multi-draw indirect call. The tests use a vertex shader that encodes these values into the rendered output position and color, then verifies the resulting image against a software reference.

## Source Code

- [vktDrawShaderDrawParametersTests.cpp](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.shader_draw_parameters
├── base_vertex
├── base_vertex_only
├── base_instance
├── base_instance_only
└── draw_index
```

## Test Families

### base_vertex — gl_BaseVertex validation across draw types

Tests that `gl_BaseVertex` returns the correct value for direct, indexed, indirect, and indexed-indirect draws. Contains four leaf test cases: `draw`, `draw_indexed`, `draw_indirect`, and `draw_indexed_indirect`. For indexed draws, `gl_BaseVertex` should equal the `vertexOffset` parameter; for non-indexed draws, it should be zero. Uses the `VertexFetchShaderDrawParameters.vert` shader which encodes `gl_BaseVertex` into the rendered output. The test spec has no additional flags set (flags = 0).

### base_vertex_only — gl_BaseVertex-only validation (primary command buffer only)

Similar to `base_vertex` but uses the `VertexFetchShaderDrawParametersBaseVert.vert` shader and sets the `TEST_FLAG_BASE_VERT_ONLY` flag. This variant isolates `gl_BaseVertex` testing without the influence of other draw parameters. Only registered when not using secondary command buffers (`!useSecondaryCmdBuffer`) to limit test repetition. Contains the same four leaf test cases as `base_vertex`.

### base_instance — gl_BaseInstance validation across draw types

Tests that `gl_BaseInstance` returns the correct value for instanced draws. Contains six leaf test cases: `draw`, `draw_indexed`, `draw_indirect`, `draw_indirect_first_instance`, `draw_indexed_indirect`, and `draw_indexed_indirect_first_instance`. The `first_instance` variants test non-zero `firstInstance` values, requiring the `drawIndirectFirstInstance` feature. Uses the `VertexFetchShaderDrawParameters.vert` shader with `TEST_FLAG_INSTANCED` set.

### base_instance_only — gl_BaseInstance-only validation (primary command buffer only)

Similar to `base_instance` but uses the `VertexFetchShaderDrawParametersBaseInst.vert` shader and sets the `TEST_FLAG_BASE_INST_ONLY` flag. This variant isolates `gl_BaseInstance` testing. Only registered when not using secondary command buffers (`!useSecondaryCmdBuffer`) to limit test repetition. Contains the same six leaf test cases as `base_instance`: `draw`, `draw_indexed`, `draw_indirect`, `draw_indirect_first_instance`, `draw_indexed_indirect`, and `draw_indexed_indirect_first_instance`.

### draw_index — gl_DrawID validation in multi-draw indirect

Tests that `gl_DrawID` returns the correct draw index (0, 1, 2) within a multi-draw indirect call. Uses the `VertexFetchShaderDrawParametersDrawIndex.vert` shader with `TEST_FLAG_INDIRECT | TEST_FLAG_MULTIDRAW` flags. Contains four leaf test cases: `draw`, `draw_instanced`, `draw_indexed`, and `draw_indexed_instanced`. The multi-draw count is `MAX_INDIRECT_DRAW_COUNT = 3`, and each draw is offset to produce a distinct rendered rectangle.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Draw mode | direct, indexed, indirect, indexed-indirect | The Vulkan draw command type |
| Instanced | false, true | Whether instancing is used (instanceCount > 1) |
| First instance | false, true | Whether non-zero `firstInstance` is tested (requires `drawIndirectFirstInstance` feature) |
| Multi-draw | false, true | Whether multi-draw indirect is used (drawCount > 1) |
| Base vertex only | false, true | Whether only `gl_BaseVertex` is tested in isolation |
| Base instance only | false, true | Whether only `gl_BaseInstance` is tested in isolation |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Fixed topology for all tests in this file |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_KHR_shader_draw_parameters` | Always required | [vktDrawShaderDrawParametersTests.cpp#L435](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L435) |
| `shaderDrawParameters` feature | When Vulkan 1.1+ is supported | [vktDrawShaderDrawParametersTests.cpp#L438-L443](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L438-L443) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawShaderDrawParametersTests.cpp#L445-L446](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L445-L446) |
| `multiDrawIndirect` feature | When `TEST_FLAG_MULTIDRAW` is set | [vktDrawShaderDrawParametersTests.cpp#L448-L449](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L448-L449) |
| `drawIndirectFirstInstance` feature | When `TEST_FLAG_FIRST_INSTANCE` is set | [vktDrawShaderDrawParametersTests.cpp#L451-L452](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L451-L452) |

## Verification Methods

- **Fuzzy image comparison against software reference**: A reference image is generated by the `drawReferenceImage()` method at [vktDrawShaderDrawParametersTests.cpp#L225-L255](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255), which draws colored rectangles at specific offsets based on the expected draw parameter values. The rendered output is compared using `tcu::fuzzyCompare` with a threshold of 0.05 at [vktDrawShaderDrawParametersTests.cpp#L336-L338](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L336-L338). Each draw and instance combination produces a distinct rectangle at a known position with a known color, allowing precise verification of `gl_BaseVertex`, `gl_BaseInstance`, and `gl_DrawID` values.

## Notes

- All tests use `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` as the fixed topology at [vktDrawShaderDrawParametersTests.cpp#L490](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L490).
- The `base_vertex_only` and `base_instance_only` groups are only registered when `!useSecondaryCmdBuffer` at [vktDrawShaderDrawParametersTests.cpp#L506](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L506) and [vktDrawShaderDrawParametersTests.cpp#L535](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L535) to reduce test duplication.
- The `DrawTest` class uses the `FlagsTestSpec` struct at [vktDrawShaderDrawParametersTests.cpp#L54-L62](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L54-L62) which extends `TestSpecBase` with a `TestFlags` bitmask controlling which draw parameters are exercised.
- Vertex data is carefully laid out with junk vertices interspersed with good vertices at specific indices (`NDX_FIRST_VERTEX = 2`, `NDX_SECOND_VERTEX = 9`) to ensure the shader correctly reads `gl_BaseVertex` and `gl_BaseInstance` values from the right locations at [vktDrawShaderDrawParametersTests.cpp#L66-L77](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L66-L77).
- The `addDrawCase` helper at [vktDrawShaderDrawParametersTests.cpp#L455-L474](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L455-L474) constructs test names from the flag combination (e.g., `draw_indexed_indirect_instanced_first_instance`).
- Four different vertex shaders are used: `VertexFetchShaderDrawParameters.vert` (base_vertex and base_instance), `VertexFetchShaderDrawParametersBaseVert.vert` (base_vertex_only), `VertexFetchShaderDrawParametersBaseInst.vert` (base_instance_only), and `VertexFetchShaderDrawParametersDrawIndex.vert` (draw_index).
