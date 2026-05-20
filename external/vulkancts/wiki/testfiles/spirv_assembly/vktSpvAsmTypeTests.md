# vktSpvAsmTypeTests

## Overview

Tests SPIR-V integer type operations across all integer widths (8, 16, 32, 64 bit) and signedness (signed/unsigned), with scalar and vector forms. Covers arithmetic, bitwise, comparison, shift, bit-field, and constant operations using a templated test framework.

## Role

Registration file and implementation file. Creates the `type` group with `scalar` and vector-width subgroups, and defines all test cases inline through a templated `SpvAsmTypeTests<T>` class hierarchy.

## Source

- [vktSpvAsmTypeTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.type
├── scalar
├── vec1 (non-VulkanSC only)
├── vec2
├── vec3
├── vec4
├── vec8 (non-VulkanSC only)
└── vec12 (non-VulkanSC only)
```

## Test Families

### scalar — Scalar integer type operations

Contains 8 subgroups (i8, u8, i16, u16, i32, u32, i64, u64), each testing all applicable operations at scalar width.

### vec1 through vec12 — Vector integer type operations

Each vector-width subgroup contains the same 8 signedness/width subgroups as scalar, but tests operations in vector form. `vec1` and `vec12` also exercise `OpTypeVectorIdEXT` (non-VulkanSC only).

### Per-type test operations

Within each type subgroup (e.g., `scalar.i32`), the following operations are tested via the `MAKE_TEST_SV_I_*` / `MAKE_TEST_SV_U_*` macro system:

**Arithmetic operations:**

| Test Name | SPIR-V Op | GLSL.std.450 | Description |
|-----------|-----------|-------------|-------------|
| `negate` | OpSNegate | — | Signed negation |
| `add` | OpIAdd | — | Integer addition |
| `sub` | OpISub | — | Integer subtraction |
| `mul` | OpIMul | — | Integer multiplication |
| `div` | OpSDiv / OpUDiv | — | Signed/unsigned division |
| `rem` | OpSRem | — | Signed remainder (sign of dividend) |
| `mod` | OpSMod / OpUMod | — | Signed/unsigned modulo |
| `abs` | — | GLSLstd450SAbs | Absolute value |
| `sign` | — | GLSLstd450SSign | Sign extraction |
| `min` | — | GLSLstd450SMin/UMin | Minimum |
| `max` | — | GLSLstd450SMax/UMax | Maximum |
| `clamp` | — | GLSLstd450SClamp/UClamp | Clamping |

**Bit-field operations** (non-VulkanSC: 8/16/32/64-bit; VulkanSC: 32-bit only):

| Test Name | SPIR-V Op | Description |
|-----------|-----------|-------------|
| `bit_field_insert` | OpBitFieldInsert | Insert bits from one value into another |
| `bit_field_s_extract` | OpBitFieldSExtract | Signed bit-field extraction |
| `bit_field_u_extract` | OpBitFieldUExtract | Unsigned bit-field extraction |
| `bit_reverse` | OpBitReverse | Reverse bits |
| `bit_count` | OpBitCount | Count set bits |

**Find MSB/LSB:**

| Test Name | GLSL.std.450 | Description |
|-----------|-------------|-------------|
| `find_lsb` | GLSLstd450FindILsb | Find least significant set bit |
| `find_msb` | GLSLstd450FindSMsb/FindUMsb | Find most significant set bit (signed/unsigned) |

**Shift operations:**

| Test Name | SPIR-V Op | Description |
|-----------|-----------|-------------|
| `shift_right_logical` | OpShiftRightLogical | Logical right shift |
| `shift_right_arithmetic` | OpShiftRightArithmetic | Arithmetic right shift (sign-extending) |
| `shift_left_logical` | OpShiftLeftLogical | Left shift |

**Bitwise logical operations:**

| Test Name | SPIR-V Op | Description |
|-----------|-----------|-------------|
| `bitwise_or` | OpBitwiseOr | Bitwise OR |
| `bitwise_xor` | OpBitwiseXor | Bitwise XOR |
| `bitwise_and` | OpBitwiseAnd | Bitwise AND |
| `not` | OpNot | Bitwise NOT |

**Comparison operations** (result is boolean):

| Test Name | SPIR-V Op | Description |
|-----------|-----------|-------------|
| `iequal` | OpIEqual | Integer equality |
| `inotequal` | OpINotEqual | Integer inequality |
| `ugreaterthan` | OpUGreaterThan | Unsigned greater-than |
| `sgreaterthan` | OpSGreaterThan | Signed greater-than |
| `ugreaterthanequal` | OpUGreaterThanEqual | Unsigned greater-than-or-equal |
| `sgreaterthanequal` | OpSGreaterThanEqual | Signed greater-than-or-equal |
| `ulessthan` | OpULessThan | Unsigned less-than |
| `slessthan` | OpSLessThan | Signed less-than |
| `ulessthanequal` | OpULessThanEqual | Unsigned less-than-or-equal |
| `slessthanequal` | OpSLessThanEqual | Signed less-than-or-equal |

**Constant operations:**

| Test Name | SPIR-V Op | Description |
|-----------|-----------|-------------|
| `constant` | OpConstant | Normal constant |
| `constant_composite` | OpConstantComposite | Composite constant |
| `constant_null` | OpConstantNull | Null constant |
| `variable_initializer` | OpVariable | Variable with initializer |
| `spec_constant_initializer` | OpSpecConstant | Spec constant with initializer |
| `spec_constant_composite_initializer` | OpSpecConstantComposite | Spec constant composite with initializer |

**Multiplication-division combined:**

| Test Name | Description |
|-----------|-------------|
| `mul_sdiv` | Multiply then signed-divide |
| `mul_udiv` | Multiply then unsigned-divide |

## Parameter Dimensions

| Dimension | Values | Notes |
|-----------|--------|-------|
| Signedness | signed, unsigned | i8/i16/i32/i64 vs u8/u16/u32/u64 |
| Bit width | 8, 16, 32, 64 | Each width requires corresponding shaderInt* feature |
| Vector size | scalar, vec2, vec3, vec4, vec8, vec12, vec1 | vec1/vec8/vec12 are non-VulkanSC only |
| Input range | RANGE_FULL, RANGE_BIT_WIDTH, RANGE_BIT_WIDTH_SUM | Controls test data generation range |
| Input width | WIDTH_8 through WIDTH_64_64 | Cross-width operations for shifts and bit-field ops |
| Filter | FILTER_NONE, FILTER_ZERO, FILTER_SIGNED_DIV, etc. | Excludes problematic input combinations |

## Support Requirements

| Requirement | Types Affected |
|-------------|----------------|
| `shaderInt8` | i8, u8 types |
| `shaderInt16` | i16, u16 types |
| `shaderInt64` | i64, u64 types |
| `VK_KHR_8bit_storage` | Some 8-bit storage tests |
| `VK_KHR_16bit_storage` | Some 16-bit storage tests |
| `VK_KHR_storage_buffer_storage_class` | Storage buffer access |

## Verification Methods

- **Compute shader comparison**: Each test generates input data, runs a compute shader that performs the SPIR-V operation, and compares the output buffer against a CPU-computed reference
- **Input filtering**: Filters exclude problematic input combinations (e.g., division by zero, signed overflow) using `FILTER_ZERO`, `FILTER_SIGNED_DIV`, `FILTER_NEGATIVES_AND_ZERO`, `FILTER_MIN_GT_MAX`
- **Dataset size**: `TEST_DATASET_SIZE` (10) random input values per scalar test; vector tests scale by vector width

## Notes

- The test framework uses a template class `SpvAsmTypeTests<T>` with specializations for int8_t, uint8_t, int16_t, uint16_t, int32_t, uint32_t, int64_t, uint64_t
- `vec1` and `vec12` use `OpTypeVectorIdEXT` from SPV_KHR_integer_dot_product (non-VulkanSC only)
- The `MAKE_TEST_SV_I_*` / `MAKE_TEST_SV_U_*` macros generate test cases across all vector sizes for signed/unsigned types respectively
- VulkanSC uses a reduced test matrix (3 vector sizes instead of 7, 32-bit only for bit-field operations)
