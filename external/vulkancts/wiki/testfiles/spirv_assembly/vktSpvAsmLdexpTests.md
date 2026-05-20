# vktSpvAsmLdexpTests

## Overview

Tests for the SPIR-V `ldexp` operation using Amber test cases, covering various combinations of floating-point result types and integer exponent types.

## Role

Implementation file

## Source

- [vktSpvAsmLdexpTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp)

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

Each test case exercises the `ldexp` operation (multiply a floating-point value by 2 raised to an integer power) with a specific combination of floating-point result type (float16, float32, float64; scalar or vec2/vec4) and integer exponent type (int8, int16, int32, int64; scalar or matching vector). Tests are implemented as Amber test cases loaded from the `ldexp/` data subdirectory. Source: `vktSpvAsmLdexpTests.cpp#L39-L143`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Float type | float16, float32, float64 | Result floating-point type |
| Float width | scalar, vec2, vec4 | Scalar or vector result |
| Exponent type | int8, int16, int32, int64 | Integer exponent type |
| Exponent width | scalar, vec2, vec4 | Scalar or vector exponent (matches float width) |

## Support Requirements

Varies per test case. Common requirements observed in `vktSpvAsmLdexpTests.cpp#L46-L130`:
- `Float16Int8Features.shaderFloat16` for float16 results
- `Float16Int8Features.shaderInt8` for int8 exponents
- `Features.shaderInt16` for int16 exponents
- `Features.shaderInt64` for int64 exponents
- `Features.shaderFloat64` for float64 results
- `Storage16BitFeatures.storageBuffer16BitAccess` / `uniformAndStorageBuffer16BitAccess` for 16-bit storage
- `Storage8BitFeatures.uniformAndStorageBuffer8BitAccess` for 8-bit storage

## Verification Methods

Verification is handled by the Amber test framework using the `.amber` test files in the `ldexp/` data subdirectory.

## Notes

- Non-VulkanSC only
- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in external `.amber` files
- The `ldexp_float32_int32` and `ldexp_f32vec2_i32vec2` / `ldexp_f32vec4_i32vec4` cases have empty requirements lists (baseline Vulkan support)
