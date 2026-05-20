# vktSpvAsmSignedOpTests

## Overview

Tests for signed SPIR-V operations applied to unsigned integer types and vice versa, covering a wide range of GLSL.std.450 extended instructions and atomic operations with mismatched signedness.

## Role

Implementation file

## Source

- [vktSpvAsmSignedOpTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.signed_op
├── glsl_int_findumsb
├── glsl_int_uclamp
├── glsl_int_umax
├── glsl_int_umin
├── glsl_uint_findsmsb
├── glsl_uint_sabs
├── glsl_uint_sclamp
├── glsl_uint_smax
├── glsl_uint_smin
├── glsl_uint_ssign
├── int_atomicumax
├── int_atomicumin
├── int_ugreaterthan
├── int_ugreaterthanequal
├── int_ulessthan
├── int_ulessthanequal
├── uint_atomicsmax
├── uint_atomicsmin
├── uint_sdiv
├── uint_smulextended
└── uint_snegate
```

## Test Families

### Signed operations on unsigned types — Various GLSL.std.450 and atomic ops with mismatched signedness

Tests signed operations applied to unsigned types and unsigned operations applied to signed types. Categories include:
- **GLSL signed ops on int**: `FindUMsb`, `UClamp`, `UMax`, `UMin`
- **GLSL unsigned ops on uint**: `FindSMsb`, `SAbs`, `SClamp`, `SMax`, `SMin`, `SSign`
- **Atomic unsigned ops on int**: `AtomicUMax`, `AtomicUMin`
- **Comparison unsigned ops on int**: `UGreaterThan`, `UGreaterThanEqual`, `ULessThan`, `ULessThanEqual`
- **Atomic signed ops on uint**: `AtomicSMax`, `AtomicSMin`
- **Other signed ops on uint**: `SDiv`, `SMulExtended`, `SNegate`

Source: `vktSpvAsmSignedOpTests.cpp#L38-L85`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Operation | FindUMsb, UClamp, UMax, UMin, FindSMsb, SAbs, SClamp, SMax, SMin, SSign, AtomicUMax, AtomicUMin, UGreaterThan, UGreaterThanEqual, ULessThan, ULessThanEqual, AtomicSMax, AtomicSMin, SDiv, SMulExtended, SNegate | The specific operation being tested |
| Operand type | int (32-bit signed), uint (32-bit unsigned) | The integer type with mismatched signedness |

## Support Requirements

No special Vulkan extensions or features required beyond baseline compute shader support. Non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`).

## Verification Methods

Verification is handled by the Amber test framework using `.amber` test files located in the `spirv_assembly/instruction/compute/signed_op/` data subdirectory. Source: `vktSpvAsmSignedOpTests.cpp#L38-L85`.

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in external `.amber` files
- Non-VulkanSC only
