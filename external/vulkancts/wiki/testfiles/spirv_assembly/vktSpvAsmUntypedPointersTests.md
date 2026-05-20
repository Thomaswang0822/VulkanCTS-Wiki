# vktSpvAsmUntypedPointersTests

## Overview

SPIR-V Assembly Tests for the SPV_KHR_shader_untyped_pointers extension. Tests untyped pointer operations including load, store, copy, type punning, atomics, descriptor arrays, memory reinterpretation, and interactions with variable pointers, physical storage buffers, workgroup memory explicit layout, cooperative matrices, and block arrays. Covers both Vulkan and GLSL memory models.

## Role

Implementation file

## Source

- [vktSpvAsmUntypedPointersTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.untyped_pointers (non-VulkanSC only)
├── vulkan_memory_model
└── glsl_memory_model
```

## Test Families

### vulkan_memory_model — Untyped pointers with Vulkan memory model

Tests untyped pointer operations using the Vulkan memory model (`vktSpvAsmUntypedPointersTests.cpp#L12679-L12689`). Contains the following sub-groups:

- **basic_usecase**: Core untyped pointer operations including load, store, copy (OpCopyObject/OpCopyMemory/OpCopyMemorySized), array_length, atomics, and descriptor_array (`vktSpvAsmUntypedPointersTests.cpp#L12604-L12612`)
- **type_punning**: Type punning operations including load, store, copy with mixed types, and data reinterpretation (struct_as_type, multiple_access_chains, memory_interpretation) (`vktSpvAsmUntypedPointersTests.cpp#L12627-L12633`)
- **variable_pointers**: Interaction with variable pointers — op_select, op_ptr_equal, op_ptr_not_equal, op_ptr_diff, op_phi, op_function_call, op_ptr_access_chain, function_variable, private_variable, multiple_access_chains, workgroup_memory (`vktSpvAsmUntypedPointersTests.cpp#L12644-L12657`)
- **physical_storage**: Interaction with physical storage buffers — op_bitcast, op_select, op_phi, op_function_call, op_ptr_access_chain (`vktSpvAsmUntypedPointersTests.cpp#L12635-L12642`)
- **workgroup_memory_explicit_layout**: Interaction with workgroup memory explicit layout — aliased and not_aliased variants (`vktSpvAsmUntypedPointersTests.cpp#L12659-L12665`)
- **cooperative_matrix**: Interaction with cooperative matrices — basic_usecase, type_punning, mixed (`vktSpvAsmUntypedPointersTests.cpp#L12667-L12672`)
- **block_array**: Block array operations (`vktSpvAsmUntypedPointersTests.cpp#L12674-L12677`)

### glsl_memory_model — Untyped pointers with GLSL memory model

Same test structure as vulkan_memory_model but using the GLSL memory model (`vktSpvAsmUntypedPointersTests.cpp#L12691-L12700`). Contains sub-groups: basic_usecase, type_punning, variable_pointers, physical_storage, workgroup_memory_explicit_layout, and block_array. Note: cooperative_matrix sub-group is not present in the GLSL memory model variant.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Memory model | VULKAN, GLSL | SPIR-V memory model type |
| Data type | UINT8, INT8, UINT16, INT16, FLOAT16, UINT32, INT32, FLOAT32, UINT64, INT64, FLOAT64 | Scalar data types for base operations |
| Composite data type | VEC2–VEC4 of each scalar type | Vector data types for type punning |
| Operation type | NORMAL, ATOMIC | Whether atomic operations are used |
| Container type | STORAGE_BUFFER, UNIFORM, PUSH_CONSTANT, WORKGROUP | Where untyped pointers reside |
| Copy operation | COPY_OBJECT, COPY_MEMORY, COPY_MEMORY_SIZED | Copy mechanism used |
| Base test case | LOAD, STORE, COPY_FROM, COPY_TO, ARRAY_LENGTH, DESCRIPTOR_ARRAY | Core operation under test |
| Type punning test case | LOAD/STORE/COPY with same-size/different-size types, scalar↔vector, multiple_access_chains, custom_struct | Type punning scenarios |
| Atomic test case | OP_ATOMIC_LOAD through OP_ATOMIC_XOR | All SPIR-V atomic operations |
| Pointer test case | OP_BITCAST, OP_SELECT, OP_PHI, OP_PTR_ACCESS_CHAIN, OP_FUNCTION_CALL, OP_PTR_EQUAL, OP_PTR_NOT_EQUAL, OP_PTR_DIFF, etc. | Pointer operation under test |
| Memory interpretation | LARGE_ARRAY_STRIDE, NON_ZERO_OFFSET, MIXED_OFFSETS, etc. | Memory layout scenarios |
| Block array test case | BASIC, REINTERPRET_BLOCK_*, SELECT_BLOCK_* | Block array access patterns |
| Workgroup test case | ALIASED, NOT_ALIASED | Workgroup memory aliasing |
| Cooperative matrix | BASIC_LOAD/STORE, TYPE_PUNNING, MIXED | Cooperative matrix operation type |
| Matrix layout | ROW_MAJOR, COL_MAJOR | Matrix storage layout |
| Matrix type | A, B, ACCUMULATOR | Cooperative matrix role |

## Support Requirements

- **SPV_KHR_shader_untyped_pointers** extension (core extension under test)
- **VK_KHR_variable_pointers** extension (for variable pointers interaction tests)
- **VK_KHR_physical_storage_buffer** / buffer device address (for physical storage interaction)
- **VK_KHR_workgroup_memory_explicit_layout** extension (for workgroup memory interaction)
- **VK_KHR_cooperative_matrix** extension (for cooperative matrix interaction)
- Various 8-bit, 16-bit, and 64-bit storage/int features depending on data types used
- Entire test group is non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`)

## Verification Methods

- Output buffers are compared against expected values computed on the CPU. The test framework uses `SpvAsmComputeShaderCase` and custom verification callbacks.
- For type punning tests, the same memory is accessed through pointers of different types and the reinterpreted results are compared against expected bit-patterns.
- For atomic tests, the result of each atomic operation is verified against the expected value based on the operation semantics.
- For pointer interaction tests (select, phi, function call, etc.), the selected pointer is dereferenced and the loaded value is compared against the expected input.

## Notes

- The file is very large (~12,700 lines) with extensive enum definitions for parameter dimensions (`vktSpvAsmUntypedPointersTests.cpp#L59-L280`).
- The entire `untyped_pointers` group is non-VulkanSC only, as the SPV_KHR_shader_untyped_pointers extension is not supported on Vulkan SC.
- The GLSL memory model variant does not include the cooperative_matrix sub-group observed in the Vulkan memory model variant.
