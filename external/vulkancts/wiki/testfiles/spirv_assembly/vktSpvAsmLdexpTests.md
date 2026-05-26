# vktSpvAsmLdexpTests

## Overview

Tests for the SPIR-V `ldexp` operation using Amber test cases, covering the case list registered by [`createLdexpGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L35-L143) with combinations of floating-point result types and integer exponent types.

## Role

Implementation file

## Source

- [vktSpvAsmLdexpTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L35)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ldexp
├── ldexp_f16vec2_i16vec2
├── ldexp_f16vec2_i32vec2
├── ldexp_f16vec2_i64vec2
├── ldexp_f16vec2_i8vec2
├── ldexp_f16vec4_i16vec4
├── ldexp_f16vec4_i32vec4
├── ldexp_f16vec4_i64vec4
├── ldexp_f16vec4_i8vec4
├── ldexp_f32vec2_i16vec2
├── ldexp_f32vec2_i32vec2
├── ldexp_f32vec2_i64vec2
├── ldexp_f32vec2_i8vec2
├── ldexp_f32vec4_i16vec4
├── ldexp_f32vec4_i32vec4
├── ldexp_f32vec4_i64vec4
├── ldexp_f32vec4_i8vec4
├── ldexp_f64vec2_i16vec2
├── ldexp_f64vec2_i32vec2
├── ldexp_f64vec2_i64vec2
├── ldexp_f64vec2_i8vec2
├── ldexp_f64vec4_i16vec4
├── ldexp_f64vec4_i32vec4
├── ldexp_f64vec4_i64vec4
├── ldexp_f64vec4_i8vec4
├── ldexp_float16_int16
├── ldexp_float16_int32
├── ldexp_float16_int64
├── ldexp_float16_int8
├── ldexp_float32_int16
├── ldexp_float32_int32
├── ldexp_float32_int64
├── ldexp_float32_int8
├── ldexp_float64_int16
├── ldexp_float64_int32
├── ldexp_float64_int64
└── ldexp_float64_int8
```

## Test Families

### Individual ldexp test cases — Tests ldexp with specific float/exponent type combinations

Each test case exercises the `ldexp` operation (multiply a floating-point value by 2 raised to an integer power) with a specific combination of floating-point result type (`float16`, `float32`, `float64`; scalar or `vec2`/`vec4`) and integer exponent type (`int8`, `int16`, `int32`, `int64`; scalar or matching vector), as shown by the registered [`LdexpCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L39-L130) names. Tests are implemented as Amber test cases loaded from the [`ldexp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L132-L140) data subdirectory.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Float type | float16, float32, float64 | Result floating-point type |
| Float width | scalar, vec2, vec4 | Scalar or vector result |
| Exponent type | int8, int16, int32, int64 | Integer exponent type |
| Exponent width | scalar, vec2, vec4 | Scalar or vector exponent (matches float width) |

## Support Requirements

Varies per test case. Common requirements observed in [`caseList`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130):
- [`Float16Int8Features.shaderFloat16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L46-L58) for float16 results
- [`Float16Int8Features.shaderInt8`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L55-L58) for int8 exponents
- [`Features.shaderInt16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L46-L48) for int16 exponents
- [`Features.shaderInt64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L52-L54) for int64 exponents
- [`Features.shaderFloat64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L86-L90) for float64 results
- [`Storage16BitFeatures.storageBuffer16BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L46-L48) / [`uniformAndStorageBuffer16BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L46-L48) for 16-bit storage
- [`Storage8BitFeatures.uniformAndStorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L55-L58) for 8-bit storage

## Verification Methods

Verification is handled by the Amber test framework using `.amber` test files selected from the [`ldexp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L132-L140) data subdirectory.

## Notes

- Non-VulkanSC only
- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in external `.amber` files
- The [`ldexp_float32_int32`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L118), [`ldexp_f32vec2_i32vec2`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L75), and [`ldexp_f32vec4_i32vec4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L82) cases have empty requirements lists (baseline Vulkan support).
