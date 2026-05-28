# vktSpvAsmEmptyStructTests

## Overview

Tests empty structs in SPIR-V, covering copying structs that contain empty struct members, pointer comparisons of empty struct members, and empty structs as function arguments or return values. The three registered child groups are added in [`createEmptyStructComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L532-L542).

## Role

Implementation file

## Source

- [vktSpvAsmEmptyStructTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L532)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.empty_struct
├── copying
├── pointer_comparison
└── function
```

## Test Families

### copying — Tests copying structs containing empty struct members

Tests copying a `ContainerStruct` containing two empty struct members between two `i32` fields, as represented by [`%type_container_struct`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L89-L100). The source tests two methods, [`OpCopyObject`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L178-L181) plus load/store and [`OpCopyMemory`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L182-L184), across UBO and SSBO descriptor types. For UBO, relaxed uniform buffer layout rules use 16-byte member offsets; for SSBO, natural 4-byte offsets are used in the [`bufferTypes`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L141-L165) table. The custom [`verifyResult()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L61) function skips zero-valued expected words used to mark empty structure padding and compares non-zero values.

### pointer_comparison — Tests pointer comparisons of empty struct members

Uses [`OpPtrNotEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L288-L296) to compare pointers to two empty struct members within a container struct stored in an SSBO. Requires [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L217-L218) capability and SPIR-V 1.4 with [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L311-L315). The shader accesses the two empty struct members via [`OpAccessChain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L288-L292) and uses `OpPtrNotEqual` plus [`OpSelect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L293-L296) to output whether the pointers differ.

### function — Tests empty structs as function arguments and return values

Tests passing empty structs through function call/return using [`OpFunctionCall`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L412-L415) and [`OpReturnValue`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L450-L463). Uses [`OpCopyLogical`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L405-L415) to convert between the storage-buffer empty struct type and the function-scope empty struct type. Tests three variable storage scenarios from the [`variableDefinitions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L468-L502) table: global variable in `Private` storage class, global variable in `Workgroup` storage class, and local `Function` variable. Requires SPIR-V 1.4 and [`variablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L517-L525).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Buffer type | `ubo`, `ssbo` | Descriptor type for the input buffer in the `copying` family, defined in [`bufferTypes`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L141-L165) |
| Copy method | `copy_object`, `copy_memory` | SPIR-V instruction used to copy the struct in the `copying` family, defined in [`copyingMethods`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L167-L184) |
| Variable storage | `global_variable_private`, `global_variable_shared`, `local_variable` | Empty-struct variable storage in the `function` family, defined in [`variableDefinitions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L468-L502) |

## Support / Feature Requirements

- **copying**: [`SPV_KHR_storage_buffer_storage_class`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L66-L69) extension.
- **pointer_comparison**: SPIR-V 1.4, [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L311-L315), and [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L217-L218) capability with the Vulkan feature requested at [`spec.requestedVulkanFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L309-L315).
- **function**: SPIR-V 1.4, [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L520-L525), and [`variablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L517-L525).

## Verification Methods

- **copying**: Custom [`verifyResult()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L61) compares output words against expected values and skips zero-valued entries that represent empty-struct padding.
- **pointer_comparison**: Direct output comparison expects output value `1` after [`OpPtrNotEqual`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L293-L296), with expected output defined at [`expectedOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L304-L315).
- **function**: Direct output comparison against expected `uint32` values `{1, 0xffffffff, 1}` defined in [`expectedOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L504-L525).

## Notes

- The [`verifyResult()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L61) function in the copying family intentionally skips zero-valued expected words because zero marks empty structure content that may not be preserved during copy operations.
- The function family uses [`OpCopyLogical`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L405-L415) to bridge type compatibility between storage-buffer and function-scope empty struct types.
