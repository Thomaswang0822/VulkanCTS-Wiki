# vktSpvAsmEmptyStructTests

## Overview

Tests for empty structs in SPIR-V, covering copying structs that contain empty struct members, pointer comparisons of empty struct members, and empty structs as function arguments or return values.

## Role

Implementation file

## Source

- [vktSpvAsmEmptyStructTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.empty_struct
├── copying
├── pointer_comparison
└── function
```

## Test Families

### copying — Tests copying structs containing empty struct members

Tests copying a `ContainerStruct` (containing two empty struct members between two `i32` fields) using two methods: `OpCopyObject` + `OpLoad`/`OpStore`, and `OpCopyMemory`. Tests both UBO (uniform buffer) and SSBO (storage buffer) descriptor types with different offset layouts. For UBO, relaxed uniform buffer layout rules apply with 16-byte alignment; for SSBO, natural 4-byte offsets are used. The custom `verifyResult` function skips zero-valued expected bytes (used to mark empty structure padding) and compares non-zero values. Source: `vktSpvAsmEmptyStructTests.cpp#L63-L211`.

### pointer_comparison — Tests pointer comparisons of empty struct members

Uses `OpPtrNotEqual` to compare pointers to two empty struct members within a container struct stored in an SSBO. Requires `VariablePointersStorageBuffer` capability and SPIR-V 1.4 (via `VK_KHR_spirv_1_4` extension). The shader accesses the two empty struct members via `OpAccessChain` and uses `OpPtrNotEqual` + `OpSelect` to output whether the pointers differ. Source: `vktSpvAsmEmptyStructTests.cpp#L213-L317`.

### function — Tests empty structs as function arguments and return values

Tests passing empty structs through function call/return using `OpFunctionCall` and `OpReturnValue`. Uses `OpCopyLogical` to convert between the storage-buffer empty struct type and the function-scope empty struct type. Tests three variable storage scenarios: global variable in `Private` storage class, global variable in `Workgroup` storage class, and local `Function` variable. Requires SPIR-V 1.4 and `variablePointersStorageBuffer`. Source: `vktSpvAsmEmptyStructTests.cpp#L319-L528`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Buffer type | `ubo`, `ssbo` | Descriptor type for the input buffer (copying family only) |
| Copy method | `copy_object`, `copy_memory` | SPIR-V instruction used to copy the struct (copying family only) |
| Variable storage | `global_variable_private`, `global_variable_shared`, `local_variable` | Where the empty struct variable is stored (function family only) |

## Support Requirements

- **copying**: `SPV_KHR_storage_buffer_storage_class` extension
- **pointer_comparison**: SPIR-V 1.4, `VK_KHR_spirv_1_4` extension, `VariablePointersStorageBuffer` capability
- **function**: SPIR-V 1.4, `VK_KHR_spirv_1_4` extension, `VariablePointersStorageBuffer` capability

## Verification Methods

- **copying**: Custom `verifyResult` function that compares output bytes against expected values, skipping zero-valued entries that represent empty struct padding (`vktSpvAsmEmptyStructTests.cpp#L39-L61`)
- **pointer_comparison**: Direct output comparison — expects output value of 1 (pointers not equal)
- **function**: Direct output comparison against expected uint32 values `{1, 0xffffffff, 1}`

## Notes

- The `verifyResult` function in the copying family intentionally skips zero-valued expected bytes since zero marks empty structure content that may not be preserved during copy operations
- The function family uses `OpCopyLogical` to bridge type compatibility between storage-buffer and function-scope empty struct types
