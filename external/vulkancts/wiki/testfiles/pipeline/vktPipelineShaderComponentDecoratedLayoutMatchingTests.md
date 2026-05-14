# vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp

## Overview

[`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1) implements the [`shader_layout_component_matching`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1194) nested subgroup under `interface_matching`. It verifies that component-decorated shader interface variables (using `Component` decoration in SPIR-V) are correctly matched across pipeline stages with various type widths and packing patterns.

## Role

Implementation file. Nested subgroup under [`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1).

## Source Code

- Primary source: [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1)
- Header: [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.interface_matching.shader_layout_component_matching
├── vert_frag
├── vert_geom_frag
├── vert_tesc_tese_frag
└── vert_tesc_tese_geom_frag
```

## Test Families

### vert_frag — Vertex-to-fragment component matching

Tests component-decorated layout matching across a vertex-to-fragment pipeline. Each flow variant contains mode subgroups (loose_var, in_block), width subgroups (float16, float32, float64), location count subgroups (single_location, multiple_locations), and component pattern leaves.

### vert_geom_frag — Vertex-geometry-fragment component matching

Tests component-decorated layout matching across a vertex-geometry-fragment pipeline. Geometry stage passes values through verbatim. Same nested structure as vert_frag.

### vert_tesc_tese_frag — Tessellation component matching

Tests component-decorated layout matching across a vertex-tessellation control-tessellation evaluation-fragment pipeline. Tessellation stages pass values through verbatim. Same nested structure as vert_frag.

### vert_tesc_tese_geom_frag — Full pipeline component matching

Tests component-decorated layout matching across a vertex-tessellation control-tessellation evaluation-geometry-fragment pipeline. Both tessellation and geometry stages pass values through verbatim. Same nested structure as vert_frag.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Flow | [Array](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1158) | 4 pipeline configurations |
| Mode | [Enum](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L91) | LooseVariable (active), VariableInBlock (defined but not iterated) |
| Width | [Loop](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1179) | 16, 32, 64 |
| Location count | [Loop](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1190) | 0 (single), 3 (multiple) |
| Component pattern | [Array](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1148) | 9 patterns (filtered by width) |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| `shaderFloat16` + `storageInputOutput16` | Width 16 | [348](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L348) |
| `shaderFloat64` | Width 64 | [355](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L355) |
| `tessellationShader` | Tessellation flows | [338](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L338) |
| `geometryShader` | Geometry flows | [345](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L345) |
| Color attachment format support | R32G32B32A32_SFLOAT | [330](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L330) |

## Verification Methods

**Exact pixel comparison** via [`verifyResult()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L943): compares every pixel against expected reference color Vec4(0.125, 0.25, 0.5, 1.0) using exact equality. On mismatch, reports first differing pixel.

## Notes / Uncertainties

- The `VariableInStruct` mode is commented out at [line 1177](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1177); only `LooseVariable` is active
- Starting location cycles through 1-4 to provide coverage of non-zero location offsets
- When tessellation/geometry is present, values are halved to compensate for interpolation across amplified primitives
