# vktSpvAsmRawAccessChainTests

## Overview

SPIR-V Assembly Tests for the OpRawAccessChainNV instruction (VK_NV_raw_access_chains). Tests raw access chain operations with various data sizes, component counts, alignments, padding, strides, bounds checking, memory qualifiers, and interactions with variable pointers, descriptor indexing, and physical storage buffers.

## Role

Implementation file

## Source

- [vktSpvAsmRawAccessChainTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.raw_access_chain
└── (flat test cases, no sub-groups)
```

## Test Families

### raw_access_chain — OpRawAccessChainNV compute tests

Tests the `OpRawAccessChainNV` instruction in compute shaders. Each test case generates a SPIR-V assembly shader that performs a load from an input buffer and a store to an output buffer using `OpRawAccessChainNV`, then verifies the output matches expected results (`vktSpvAsmRawAccessChainTests.cpp#L610-L1196`).

The test generates a shader that:
1. Reads input components via `OpRawAccessChainNV` load
2. Sums the input components
3. Stores the result (plus incrementing values) to output via `OpRawAccessChainNV` store

Test names encode all parameter dimensions, e.g.: `load_store_4b_1c_0pad_0align_stride_no_bounds_load_non_writable_store_non_readable_64b_indexing`

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Operation | load, store, load_store | Whether testing load, store, or both |
| Data size | 1, 2, 4, 8 bytes | Size of each component in bytes (int8/int16/int32/int64) |
| Components | 1, 2, 3, 4 | Number of vector components |
| Alignment | 0, 4, 8, 16, 32 | Alignment in bytes (0 = default) |
| Pre-padding | 0, 4 | Bytes of padding before data |
| Stride | true, false | Whether to use explicit stride |
| Variable pointers | true, false | Whether variable pointers are used |
| Descriptor indexing | true, false | Whether runtime descriptor array indexing is used |
| Physical buffers | true, false | Whether PhysicalStorageBuffer is used |
| Bounds check | NO_BOUNDS_CHECK, BOUNDS_CHECK_PER_COMPONENT, BOUNDS_CHECK_PER_ELEMENT | Robustness bounds checking mode |
| Qualifiers | NonWritable, Volatile, Coherent (load/store) | Memory decoration qualifiers |
| 64-bit indexing | true, false | Whether VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT is used |

The `Parameters` struct (`vktSpvAsmRawAccessChainTests.cpp#L91-L121`) encodes all these dimensions. The `addTests` function iterates through combinations and generates test cases.

## Support Requirements

- **VK_NV_raw_access_chains** extension and `shaderRawAccessChains` feature (`vktSpvAsmRawAccessChainTests.cpp#L450-L453`)
- **VK_KHR_variable_pointers** extension and `variablePointers` + `variablePointersStorageBuffer` features (when `usesVariablePointers` is true) (`vktSpvAsmRawAccessChainTests.cpp#L455-L464`)
- **VK_KHR_buffer_device_address** extension and `bufferDeviceAddress` feature (when `usesPhysicalBuffers` is true) (`vktSpvAsmRawAccessChainTests.cpp#L466-L472`)
- **VK_KHR_shader_float16_int8** and `shaderInt8` feature (when `usesInt8` is true) (`vktSpvAsmRawAccessChainTests.cpp#L474-L479`)
- **shaderInt16** core feature (when `usesInt16` is true) (`vktSpvAsmRawAccessChainTests.cpp#L482-L483`)
- **shaderInt64** core feature (when `usesInt64` is true) (`vktSpvAsmRawAccessChainTests.cpp#L485-L486`)
- **shader64BitIndexing** feature (when `uses64BitIndexing` is true, non-VulkanSC) (`vktSpvAsmRawAccessChainTests.cpp#L488-L491`)
- **SPIR-V 1.6** assembly target (`vktSpvAsmRawAccessChainTests.cpp#L498-L501`)

## Verification Methods

- Input data is filled with random values (`vktSpvAsmRawAccessChainTests.cpp#L619-L626`).
- Expected output is computed on the CPU: each output component is the sum of all input components (truncated to the data type size), incremented by the component index (`vktSpvAsmRawAccessChainTests.cpp#L630-L676`).
- After shader execution, the output buffer is compared byte-by-byte against expected output using `deMemCmp` (`vktSpvAsmRawAccessChainTests.cpp#L402`).
- On mismatch, up to 16 differing bytes are logged with their positions and values (`vktSpvAsmRawAccessChainTests.cpp#L404-L436`).

## Notes

- The `Spec` struct (`vktSpvAsmRawAccessChainTests.cpp#L56-L71`) holds the complete shader specification including assembly body, input/output data, and feature flags.
- The `CodeGen` class (`vktSpvAsmRawAccessChainTests.cpp#L516-L573`) helps build SPIR-V assembly strings by accumulating capabilities, extensions, decorations, declarations, and body sections.
- Bounds checking modes map to `RobustnessPerComponentNV` and `RobustnessPerElementNV` operands on `OpRawAccessChainNV` (`vktSpvAsmRawAccessChainTests.cpp#L575-L587`).
- The entire test group is non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC` in the test case class and support check).
