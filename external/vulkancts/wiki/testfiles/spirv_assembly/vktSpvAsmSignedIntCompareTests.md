# vktSpvAsmSignedIntCompareTests

## Overview

Tests signed integer comparison operations on unsigned scalar values in SPIR-V. The registered Amber cases cover
[`OpSGreaterThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L50),
[`OpSGreaterThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L51),
[`OpSLessThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L52), and
[`OpSLessThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L53) applied to
32-bit unsigned integer operands.

## Role

Implementation file

## Source

- [vktSpvAsmSignedIntCompareTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74)

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

The [`uint_sgreaterthanequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L50)
Amber case tests signed greater-than-or-equal comparison on unsigned 32-bit integer values.

### uint_sgreaterthan — Tests 32-bit unsigned int with OpSGreaterThan

The [`uint_sgreaterthan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L51)
Amber case tests signed greater-than comparison on unsigned 32-bit integer values.

### uint_slessthan — Tests 32-bit unsigned int with OpSLessThan

The [`uint_slessthan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L52)
Amber case tests signed less-than comparison on unsigned 32-bit integer values.

### uint_slessthanequal — Tests 32-bit unsigned int with OpSLessThanEqual

The [`uint_slessthanequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L53)
Amber case tests signed less-than-or-equal comparison on unsigned 32-bit integer values.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Comparison op | [`OpSGreaterThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L50), [`OpSGreaterThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L51), [`OpSLessThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L52), [`OpSLessThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L53) | The signed comparison instruction being tested |
| Operand type | [`uint` / 32-bit unsigned](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L50-L53) | The unsigned integer type used as operands |

## Support / Feature Requirements

No special Vulkan extensions or features are added in this source file. The test creation loop is compiled only for
non-VulkanSC builds through [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L38-L69).

## Verification Methods

Verification is handled by the Amber test framework. The source builds a file name from each case basename and calls
[`cts_amber::createAmberTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L58-L64)
using the [`spirv_assembly/instruction/compute/signed_int_compare`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L78)
data directory.

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and checks reside in external `.amber` files named from the
  registered case basenames by [`std::string(cases[i].basename) + ".amber"`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L58-L62).
- The file is non-VulkanSC only in the test-generation block.
- The source file's brief records the original Google bug [`b/73133282`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L20-L23).
