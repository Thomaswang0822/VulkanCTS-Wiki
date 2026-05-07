# vktPipelineSpecConstantTests.cpp

## Overview

[`vktPipelineSpecConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1) implements the [`spec_constant`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2934) topic group. It verifies specialization constant behavior across all shader stages, including default values, explicit specialization, built-in overrides, expressions, composite types, and compute-specific features (work group size, unaligned data, same-ID constants).

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineSpecConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1)
- Header: [`vktPipelineSpecConstantTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.hpp#L1)
- Shared utilities: [`vktPipelineSpecConstantUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantUtil.cpp#L1)

## Registration Path

[`createSpecConstantTests()`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2932) returns the `spec_constant` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants. Compute sub-group is monolithic only.

## Test Hierarchy

```text
spec_constant
├── graphics
│   ├── vertex / fragment / tess_control / tess_eval / geometry
│   │   ├── default_value                (no specialization, uses shader defaults)
│   │   │   └── bool / int8 / uint8 / int16 / uint16 / int / uint / int64 / uint64 / float / float16 / double
│   │   ├── basic                        (explicit specialization)
│   │   │   └── <type>[_2]
│   │   ├── builtin                      (override gl_MaxImageUnits etc.)
│   │   │   └── default / specialized
│   │   ├── expression                   (spec constants in expressions)
│   │   │   └── spec_const_expression / array_size / array_size_expression / ...
│   │   └── composite                    (composite type specialization)
│   │       ├── vector / matrix / array / struct
└── compute                              (monolithic only)
    ├── (same subgroups as graphics)
    ├── local_size                       (work group size specialization)
    │   └── x / y / z / xy / xz / yz / xyz
    ├── unaligned_spec_constant
    └── same_id
```

## Test Families

### 1. default_value

Declares specialization constants but does NOT provide specialized values via the API. Verifies that the default values declared in the shader are used.

### 2. basic

Specializes constants with explicit values via `VkSpecializationInfo`. Verifies the specialized values override the defaults.

### 3. builtin

Tests overriding built-in constants (e.g., `gl_MaxImageUnits`) with specialization constants.

### 4. expression

Tests specialization constants used in expressions: constant expressions, array sizes, and array size expressions.

### 5. composite

Tests specialization of composite types: vectors, matrices, arrays, and structs.

### 6. local_size (compute only)

Tests specialization of `local_size_x_id`, `local_size_y_id`, `local_size_z_id` and their combinations.

### 7. unaligned_spec_constant (compute only)

Tests unaligned specialization constant data using hand-crafted SPIR-V.

### 8. same_id (compute only)

Tests multiple specialization constants sharing the same `constant_id` value.

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
