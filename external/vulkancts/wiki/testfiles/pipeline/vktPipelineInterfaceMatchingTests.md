# vktPipelineInterfaceMatchingTests.cpp

## Overview

[`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1) implements the [`interface_matching`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1284) topic group. It verifies shader interface matching across pipeline stages, including vector length differences, decoration mismatches, component-decorated layout matching, and skipped output variables.

## Role

Implementation file. Also dispatches to [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1) for the `shader_layout_component_matching` nested subgroup.

## Source Code

- Primary source: [`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1)
- Header: [`vktPipelineInterfaceMatchingTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.hpp#L1)
- Nested subgroup: [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.interface_matching
├── vector_length
├── decoration_mismatch
├── shader_layout_component_matching (non-VulkanSC only)
└── misc
```

## Test Families

### vector_length — Vector length interface matching

Tests interface matching when output vector length differs from input vector length (e.g., vec4 output matched with vec2 input). Requires `VK_KHR_maintenance4` when lengths differ.

Generated leaves follow the pattern `<pipelineType>_<definitionType>_<vecFormats>`, iterating over 9 pipeline types, 6 definition types, and all valid out/in vector size combinations.

### decoration_mismatch — Decoration mismatch interface matching

Tests interface matching when interpolation decorations (flat, no_perspective, component) differ between output and input. Requires `graphicsPipelineLibraryIndependentInterpolationDecoration` for pipeline library variant.

Generated leaves follow the pattern `<decorationPair>_<definitionType>_<pipelineType>`, iterating over 8 decoration pairs filtered by definition type.

### shader_layout_component_matching — Component-decorated layout matching

Tests shader component decoration layout matching across pipeline stages. Parameterized by flow, mode, bit width, location count, and component packing. Non-VulkanSC only. Delegated to [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1).

Nested hierarchy: flow variants (vert_frag, vert_geom_frag, vert_tesc_tese_frag, vert_tesc_tese_geom_frag) containing mode (loose_var, in_block), width (float16, float32, float64), location count (single_location, multiple_locations), and component patterns.

### misc — Miscellaneous interface matching tests

Vertex shader outputs v0, v1, v2 but fragment shader only inputs v0, v2 (skipping v1). Verifies that v2 correctly receives the value from location 2.

Contains the `skip_output_variable` test case.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineType | [Enum](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L87) (9 values) | VERT_OUT_FRAG_IN through VERT_TESC_TESE_GEOM_OUT_FRAG_IN |
| DefinitionType | [Enum](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L108) (6 values) | LOOSE_VARIABLE through MEMBER_OF_ARRAY_OF_STRUCTURES_IN_BLOCK |
| VecType | [Enum](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L66) | VEC2-4, IVEC2-4, UVEC2-4 |
| DecorationType | [Enum](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L79) | NONE, FLAT, NO_PERSPECTIVE, COMPONENT0 |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_maintenance4` | When vector lengths differ |
| `graphicsPipelineLibraryIndependentInterpolationDecoration` | Decoration mismatch with pipeline library |
| `tessellationShader` / `geometryShader` | When stages used |
| `shaderFloat16` + `storageInputOutput16` | Width 16 (component matching) |
| `shaderFloat64` | Width 64 (component matching) |

## Verification Methods

- **vector_length / decoration_mismatch**: GLSL-based verification: output stage assigns known values, input stage computes epsilon comparison, fragment outputs result as color. Host reads two texels; passes if both R channels > 254 ([line 388](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L388))
- **shader_layout_component_matching**: Exact pixel comparison against reference color Vec4(0.125, 0.25, 0.5, 1.0)
- **skip_output_variable**: Host-side pixel verification against expected color (0, 255, 255, 255) with tolerance ([line 1163](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1163))
