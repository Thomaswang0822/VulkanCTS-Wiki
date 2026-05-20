# vktSpvAsmTrinaryMinMaxTests

## Overview

Tests for the VK_AMD_shader_trinary_minmax extension, covering `FMin3AMD`/`SMin3AMD`/`UMin3AMD`, `FMax3AMD`/`SMax3AMD`/`UMax3AMD`, and `FMid3AMD`/`SMid3AMD`/`UMid3AMD` operations across various data types, bit sizes, and aggregation types.

## Role

Implementation file

## Source

- [vktSpvAsmTrinaryMinMaxTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.amd_trinary_minmax
├── min3
├── mid3
└── max3
```

## Test Families

### min3 — Tests FMin3AMD/SMin3AMD/UMin3AMD operations

Tests the trinary minimum operation across all base types (int, uint, float), bit sizes (8, 16, 32, 64), and aggregation types (scalar, vec2, vec3, vec4). For each type/size combination, a sub-group contains test cases for each aggregation type. 8-bit float combinations are skipped (no 8-bit floats). Source: `vktSpvAsmTrinaryMinMaxTests.cpp#L1010-L1041`.

### max3 — Tests FMax3AMD/SMax3AMD/UMax3AMD operations

Same structure as min3 but for the trinary maximum operation.

### mid3 — Tests FMid3AMD/SMid3AMD/UMid3AMD operations

Same structure as min3 but for the trinary mid-value operation.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Operation | MIN, MAX, MID | The trinary operation type (groups: min3, max3, mid3) |
| Base type | int, uint, float | The numeric base type |
| Type size | 8, 16, 32, 64 | Bit width (8-bit float skipped) |
| Aggregation | scalar, vec2, vec3, vec4 | Scalar or vector width |

## Support Requirements

- `VK_AMD_shader_trinary_minmax` extension
- `shaderInt8` / 8-bit storage features for 8-bit types
- `shaderInt16` / 16-bit storage features for 16-bit types
- `shaderFloat16` for 16-bit float types
- `shaderInt64` for 64-bit integer types
- `shaderFloat64` for 64-bit float types

## Verification Methods

The `TrinaryMinMaxInstance::iterate()` method generates pseudorandom input values, computes expected results using CPU reference implementations of min3/max3/mid3, dispatches the compute shader, and compares GPU output against CPU reference. Reports mismatches with operation index and component details. Source: `vktSpvAsmTrinaryMinMaxTests.cpp#L940-L975`.

## Notes

- Uses SPIR-V assembly generated at runtime with `OpCapability TrinaryMinMax` and `OpExtension "SPV_AMD_shader_trinary_minmax"`
- Each test uses a unique random seed derived from the operation type and type parameters
- The hierarchy is: `{min3,max3,mid3}` → `{i8,u8,f16,i16,u16,f32,u32,f64,i64,u64}` → `{scalar,vec2,vec3,vec4}`
