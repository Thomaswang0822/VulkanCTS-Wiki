# vktSpvAsmSignedOpTests

## Overview

Tests signed SPIR-V operations applied to unsigned integer types and unsigned operations applied to signed integer types.
The registered Amber cases cover GLSL.std.450 extended instructions, atomic operations, comparison instructions, and
other integer operations with intentionally mismatched signedness as enumerated in the source
[`cases`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) table.

## Role

Implementation file

## Source

- [vktSpvAsmSignedOpTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89)

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

The file registers Amber cases in the
[`signed_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89-L93) group. Categories visible in
the source table include:

- **GLSL unsigned operations on signed `int` cases**:
  [`FindUMsb`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L50),
  [`UClamp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L51),
  [`UMax`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L52), and
  [`UMin`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L53).
- **GLSL signed operations on `uint` cases**:
  [`FindSMsb`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L54),
  [`SAbs`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L55),
  [`SClamp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L56),
  [`SMax`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L57),
  [`SMin`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L58), and
  [`SSign`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L59).
- **Atomic unsigned operations on signed `int` cases**:
  [`AtomicUMax`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L60) and
  [`AtomicUMin`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L61).
- **Unsigned comparison operations on signed `int` cases**:
  [`UGreaterThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L62),
  [`UGreaterThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L63),
  [`ULessThan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L64), and
  [`ULessThanEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L65).
- **Atomic signed operations on `uint` cases**:
  [`AtomicSMax`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L66) and
  [`AtomicSMin`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L67).
- **Other signed operations on `uint` cases**:
  [`SDiv`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L68),
  [`SMulExtended`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L69), and
  [`SNegate`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L70).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Operation | [`FindUMsb` through `SNegate`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) | The specific operation being tested |
| Operand type | [`32bit signed int`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L50-L53), [`32bit unsigned int`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L54-L70) | The integer type named in the source-case descriptions |

## Support / Feature Requirements

No special Vulkan extensions or features are added in this source file. The test creation loop is compiled only for
non-VulkanSC builds through [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L38-L84).

## Verification Methods

Verification is handled by the Amber test framework. The source builds a file name from each case basename and calls
[`cts_amber::createAmberTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L73-L79)
using the [`spirv_assembly/instruction/compute/signed_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89-L93)
data directory.

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and checks reside in external `.amber` files named from the
  registered case basenames by [`std::string(cases[i].basename) + ".amber"`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L73-L77).
- The file is non-VulkanSC only in the test-generation block.
- The source description for [`int_ugreaterthan`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L62)
  says `UGreaterThanEqual`; the registered basename still identifies the case as `int_ugreaterthan`.
