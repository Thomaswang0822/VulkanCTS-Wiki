# vktSpvAsmSignedIntCompareTests

## Overview

Tests for signed integer comparison operations on unsigned scalar values in SPIR-V, verifying that `OpSGreaterThanEqual`, `OpSGreaterThan`, `OpSLessThan`, and `OpSLessThanEqual` work correctly when applied to unsigned 32-bit integer types.

## Role

Implementation file

## Source

- [vktSpvAsmSignedIntCompareTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.signed_int_compare
├── uint_sgreaterthanequal
├── uint_sgreaterthan
├── uint_slessthan
└── uint_slessthanequal
```

## Test Families

### uint_sgreaterthanequal — Tests 32-bit unsigned int with OpSGreaterThanEqual

Tests signed greater-than-or-equal comparison on unsigned 32-bit integer values using Amber test framework.

### uint_sgreaterthan — Tests 32-bit unsigned int with OpSGreaterThan

Tests signed greater-than comparison on unsigned 32-bit integer values.

### uint_slessthan — Tests 32-bit unsigned int with OpSLessThan

Tests signed less-than comparison on unsigned 32-bit integer values.

### uint_slessthanequal — Tests 32-bit unsigned int with OpSLessThanEqual

Tests signed less-than-or-equal comparison on unsigned 32-bit integer values.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Comparison op | OpSGreaterThanEqual, OpSGreaterThan, OpSLessThan, OpSLessThanEqual | The signed comparison instruction being tested |
| Operand type | uint (32-bit unsigned) | The unsigned integer type used as operands |

## Support Requirements

No special Vulkan extensions or features required beyond baseline compute shader support. Non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`).

## Verification Methods

Verification is handled by the Amber test framework using `.amber` test files located in the `spirv_assembly/instruction/compute/signed_int_compare/` data subdirectory. Source: `vktSpvAsmSignedIntCompareTests.cpp#L38-L69`.

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in external `.amber` files
- Non-VulkanSC only
- Originally filed as Google bug b/73133282
