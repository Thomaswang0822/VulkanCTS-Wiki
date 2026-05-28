# vktSpvAsmRawAccessChainTests

## Overview

SPIR-V Assembly Tests for the [`OpRawAccessChainNV`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L902-L904) instruction from `VK_NV_raw_access_chains`. Tests raw access chain operations with generated combinations of scalar size, vector component count, alignment, padding, stride, robustness operands, memory qualifiers, variable pointers, descriptor indexing, physical storage buffers, and 64-bit indexing.

## Role

Implementation file

## Source

- [vktSpvAsmRawAccessChainTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1200)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.raw_access_chain
```

The source creates [`raw_access_chain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1200-L1206) as a flat test group and adds generated test cases directly under that root; it does not create a named subgroup below `raw_access_chain`.

## Test Families

### raw_access_chain — OpRawAccessChainNV compute tests

Tests the [`OpRawAccessChainNV`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L902-L904) instruction in compute shaders. Each generated case performs either load-oriented or store-oriented raw access-chain addressing, computes the expected output on the CPU, then verifies the shader output matches expected bytes with [`deMemCmp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L402-L438).

The generated shader path:
1. Reads input components via [`OpRawAccessChainNV`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L902-L904) load.
2. Sums the input components in generated SPIR-V arithmetic.
3. Stores the result, plus incrementing component values for vector outputs, through a generated [`OpRawAccessChainNV`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L938-L973) store path.

Test names are generated in [`addTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1000-L1196) by prefixing `load_` or `store_`, adding optional `physical_buffers_`, `variable_pointers_`, or `descriptor_indexing_`, encoding vector width/type such as `v4int32`, and appending stride, bounds-check, qualifier, and optional `64b_indexing` suffixes.

## Parameter Dimensions

| Dimension | Values observed in generation | Description |
|-----------|-------------------------------|-------------|
| Operation orientation | [`load_`, `store_`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1013-L1075) | The `testingStore` loop selects whether bounds, stride, and alignment setup is load-oriented or store-oriented. |
| Data size | [`1`, `2`, `4`, `8` bytes](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1021-L1024) | Size of each scalar component in bytes. |
| Components | [`1`, `2`, `3`, `4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1021-L1024) | Number of vector components; vector prefixes are emitted only when components > 1. |
| Alignment | Derived from component count, byte size, and alignment divisor | The code iterates divisors [`{1, 4, 2, 3}`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1021-L1024), skips incompatible divisors, and computes nonzero alignment as `(components * size) / alignmentDiv`. |
| Pre/post padding | Computed per generated case | Padding is computed to align structures to powers of two, with extra misalignment padding when alignment is nonzero. |
| Stride | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1021-L1028) | Whether explicit stride is used; per-element bounds checks are skipped when stride is false. |
| Variable pointers | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1013-L1016) | Whether variable pointers are used; skipped when physical buffers are enabled. |
| Descriptor indexing | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1013-L1016) | Whether runtime descriptor array indexing is used; skipped when physical buffers are enabled. |
| Physical buffers | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1013-L1045) | Whether PhysicalStorageBuffer is used; only generated with no variable pointers, no descriptor indexing, and no bounds checks. |
| Bounds check | [`NO_BOUNDS_CHECK`, `BOUNDS_CHECK_PER_COMPONENT`, `BOUNDS_CHECK_PER_ELEMENT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L73-L78) | Robustness bounds checking mode, subject to skip rules. |
| Qualifiers | none, load NonWritable/Volatile/Coherent combinations, store NonReadable/Volatile/Coherent combinations | Qualifier combinations are declared in [`qualifiersCombinations`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1000-L1011), and complex qualifiers are restricted to 4-byte, four-component, default-alignment cases. |
| 64-bit indexing | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1013-L1018) | Whether the test requests the 64-bit indexing path and adds the `64b_indexing` name suffix. |

The [`Parameters`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L91-L121) struct stores the generated case specification. The [`addTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1000-L1196) function iterates through combinations, applies skip rules, builds each case name, and registers each generated test directly under `raw_access_chain`.

## Support / Feature Requirements

- [`VK_NV_raw_access_chains`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L448-L453) extension and `shaderRawAccessChains` feature.
- [`VK_KHR_variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L455-L464) extension and `variablePointers` plus `variablePointersStorageBuffer` features when `usesVariablePointers` is true.
- [`VK_KHR_buffer_device_address`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L466-L472) extension and `bufferDeviceAddress` feature when `usesPhysicalBuffers` is true.
- [`VK_KHR_shader_float16_int8`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L474-L479) and `shaderInt8` feature when `usesInt8` is true.
- [`shaderInt16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L482-L483) core feature when `usesInt16` is true.
- [`shaderInt64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L485-L486) core feature when `usesInt64` is true.
- [`shader64BitIndexing`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L488-L491) feature when `uses64BitIndexing` is true outside Vulkan SC builds.
- [`SPIR-V 1.6`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L494-L500) assembly target.

## Verification Methods

- Input data is filled with random bytes from a fixed seed in [`addTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L619-L626).
- Expected output is computed on the CPU: each output component is derived from the sum of input components, truncated to the input type size, then incremented per output component when writing vector outputs.
- Bounds-check modes zero or suppress out-of-range components according to [`BOUNDS_CHECK_PER_ELEMENT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L639-L647) and [`BOUNDS_CHECK_PER_COMPONENT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L663-L670) handling.
- After shader execution, the output buffer is compared byte-by-byte against expected output using [`deMemCmp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L402-L438).
- On mismatch, up to 16 differing bytes are logged with their positions and values.

## Notes

- The [`Spec`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L56-L71) struct holds the complete shader specification, including assembly body, input/output data, expected output, descriptor ranges, and feature flags.
- The [`CodeGen`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L516-L573) class helps build SPIR-V assembly strings by accumulating capabilities, extensions, decorations, declarations, and body sections.
- Bounds checking modes map to [`RobustnessPerComponentNV`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L575-L586) and `RobustnessPerElementNV` operands on `OpRawAccessChainNV`.
- The test classes and generated cases are non-VulkanSC only, guarded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L123-L140) and corresponding guards in the generator.
