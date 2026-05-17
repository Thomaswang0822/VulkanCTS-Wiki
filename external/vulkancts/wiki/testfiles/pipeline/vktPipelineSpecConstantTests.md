# vktPipelineSpecConstantTests.cpp

## Overview

[`vktPipelineSpecConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1) implements the [`spec_constant`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2934) topic group. It verifies specialization constant behavior across all shader stages, including default values, explicit specialization, built-in overrides, expressions, composite types, and compute-specific features (work group size, unaligned data, same-ID constants).

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineSpecConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1)
- Header: [`vktPipelineSpecConstantTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.hpp#L1)
- Shared utilities: [`vktPipelineSpecConstantUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantUtil.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.spec_constant
├── graphics
└── compute (monolithic only)
```

**Variant coverage**: All variants. The `compute` subgroup is monolithic only.

## Test Families

### graphics — Graphics pipeline specialization constants

Tests specialization constants across graphics shader stages (vertex, fragment, tess_control, tess_eval, geometry). Each stage subgroup contains five common subgroups:

- **default_value**: Declares specialization constants but does NOT provide specialized values via the API. Verifies that the default values declared in the shader are used. Covers types: bool, int8, uint8, int16, uint16, int, uint, int64, uint64, float, float16, double.
- **basic**: Specializes constants with explicit values via `VkSpecializationInfo`. Verifies the specialized values override the defaults.
- **builtin**: Tests overriding built-in constants (e.g., `gl_MaxImageUnits`) with specialization constants. Contains `default` and `specialized` leaf tests.
- **expression**: Tests specialization constants used in expressions: constant expressions, array sizes, and array size expressions.
- **composite**: Tests specialization of composite types: vectors (15 types), matrices (18 types), arrays, and structs.

### compute — Compute pipeline specialization constants (monolithic only)

Tests specialization constants in the compute shader stage. Contains the same five subgroups as `graphics` (default_value, basic, builtin, expression, composite), plus three compute-specific subgroups:

- **local_size**: Tests specialization of `local_size_x_id`, `local_size_y_id`, `local_size_z_id` and their combinations (x, y, z, xy, xz, yz, xyz).
- **unaligned_spec_constant**: Tests unaligned specialization constant data using hand-crafted SPIR-V.
- **same_id**: Tests multiple specialization constants sharing the same `constant_id` value.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Shader stage | Loop | vertex, fragment, tess_control, tess_eval, geometry, compute |
| Data type | Per family | bool, int8, uint8, int16, uint16, int, uint, int64, uint64, float, float16, double |
| Composite type | Per family | vector (15 types), matrix (18 types), array, struct |
| FeatureFlags | [Enum](../../../modules/vulkan/pipeline/vktPipelineSpecConstantUtil.hpp#L39) | TESSELLATION_SHADER, GEOMETRY_SHADER, SHADER_FLOAT_64, SHADER_INT_64, SHADER_INT_16, SHADER_FLOAT_16, SHADER_INT_8, etc. |

## Support / Feature Requirements

Feature requirements are encoded as `FeatureFlags` bitmask per test case, checked in [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L855). Key features: `shaderFloat64`, `shaderInt64`, `shaderInt16`, `shaderFloat16` + 16-bit storage, `shaderInt8` + 8-bit storage, `tessellationShader`, `geometryShader`.

## Verification Methods

All test families write specialization constant values to an SSBO, then verify the SSBO contents against `expectedValues` using [`verifyValues()`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L218) which compares raw bytes at specified offsets. Compute instances dispatch and read SSBO; graphics instances render a fullscreen quad and read SSBO.
