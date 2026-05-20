# vktSpvAsmVariablePointersTests

## Overview

SPIR-V Assembly Tests for the SPV_KHR_variable_pointers and SPV_KHR_physical_storage_buffer extensions. Tests variable pointers (OpSelect on pointers, OpPhi with pointers, OpFunctionCall returning pointers, OpPtrAccessChain) and physical storage buffer pointers in both compute and graphics pipelines. Also covers nullptr usage with variable pointers and 64-bit indexing variants.

## Role

Implementation file

## Source

- [vktSpvAsmVariablePointersTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.variable_pointers
├── compute
├── complex_types_compute
├── nullptr_compute
└── 64b_indexing (non-VulkanSC only)

spirv_assembly.instruction.graphics.variable_pointers
├── graphics
├── multi_buffer_read_only_graphics
├── single_buffer_read_only_graphics
└── nullptr_graphics

spirv_assembly.instruction.compute.physical_pointers
├── compute
├── complex_types_compute
└── 64b_indexing (non-VulkanSC only)
```

## Test Families

### compute — Basic variable/physical pointer compute tests

Tests variable pointer and physical storage buffer pointer operations in compute shaders. Uses a "mux" pattern: a selector value determines which of two input pointers is chosen, then the value at that pointer is loaded and stored to output. Covers:

- **reads_opselect**: Select between two pointers using `OpSelect` (`vktSpvAsmVariablePointersTests.cpp#L370-L414`)
- **reads_opphi**: Select between two pointers using `OpPhi` (`vktSpvAsmVariablePointersTests.cpp#L415-L451`)
- **reads_opcopyobject**: Copy pointers with `OpCopyObject` then select (`vktSpvAsmVariablePointersTests.cpp#L452-L485`)
- **stores_private / stores_function**: Store variable pointers into Private/Function storage class variables (`vktSpvAsmVariablePointersTests.cpp#L486-L522`)
- **reads_opptraccesschain**: Use `OpPtrAccessChain` to compute pointer offsets, then select (`vktSpvAsmVariablePointersTests.cpp#L523-L562`)
- **writes**: Write through a variable pointer (load, increment, store back) (`vktSpvAsmVariablePointersTests.cpp#L563-L594`)
- **workgroup_two_buffers**: Variable pointers on Workgroup storage class (two-buffer variant only) (`vktSpvAsmVariablePointersTests.cpp#L598-L640`)

Each test is parameterized by buffer type: `single_buffer` (VariablePointersStorageBuffer capability) or `two_buffers` (VariablePointers capability). Physical pointer variants use `PhysicalStorageBufferAddressesEXT` instead.

### complex_types_compute — Variable/physical pointers into nested structures

Tests variable pointers and physical storage buffer pointers pointing into various levels of nested data structures in compute shaders (`vktSpvAsmVariablePointersTests.cpp#L643-L1255`). The data structure is:

```
struct inner_struct { vec4 x[2]; vec4 y[2]; };
struct outer_struct { inner_struct r[2][2]; };
struct input_buffer { outer_struct a; outer_struct b; };
```

Tests exercise 7 levels of pointer indirection (outer_struct → matrices → arrays → inner_structs → vec4arr → vec4 → float), using:
- `OpSelect` to choose between pointers at each level
- `OpFunctionCall` returning a variable pointer
- `OpPtrAccessChain` for pointer arithmetic at each level

Parameterized by: single_buffer vs two_buffers, first_input vs second_input selection, and 7 index levels.

### nullptr_compute — Nullptr usage with variable pointers

Tests usage of `OpConstantNull` with variable pointers in compute shaders (`vktSpvAsmVariablePointersTests.cpp#L1257-L1386`):
- **opvariable_initialized_null**: Initialize a pointer variable to null, then store a valid pointer and load through it (`vktSpvAsmVariablePointersTests.cpp#L1349-L1366`)
- **opselect_null_or_valid_ptr**: Use `OpSelect` to choose between nullptr and a valid pointer; forced to choose valid (`vktSpvAsmVariablePointersTests.cpp#L1367-L1385`)

Requires `VariablePointers` capability (not just `VariablePointersStorageBuffer`).

### 64b_indexing — 64-bit indexing variants (non-VulkanSC only)

Repeats the compute, complex_types_compute, and nullptr_compute tests with 64-bit indexing enabled (`vktSpvAsmVariablePointersTests.cpp#L2760-L2773`). Only available when `CTS_USES_VULKANSC` is not defined.

### graphics — Basic variable pointer graphics tests

Tests variable pointer operations in graphics pipeline stages (vertex, tessellation, geometry, fragment) (`vktSpvAsmVariablePointersTests.cpp#L1408-L1807`). Same mux pattern as compute but using `createTestsForAllStages` to generate tests for all graphics stages. Covers:
- reads_opselect, reads_opfunctioncall, reads_opphi, reads_opcopyobject
- stores_private / stores_function
- reads_opptraccesschain
- writes

Requires `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` features.

### multi_buffer_read_only_graphics — Read-only variable pointers across two input buffers (graphics)

Tests variable pointers pointing into two separate read-only input buffers in graphics pipeline (`vktSpvAsmVariablePointersTests.cpp#L1827-L2228`). Uses `VariablePointers` capability. Tests 7 levels of nested structure indirection with OpSelect, OpCopyObject, OpPhi, OpFunctionCall, and OpPtrAccessChain. Results are written to the red channel of the output color.

### single_buffer_read_only_graphics — Read-only variable pointers within a single buffer (graphics)

Tests variable pointers confined to a single input buffer in graphics pipeline (`vktSpvAsmVariablePointersTests.cpp#L2230-L2600`). Uses `VariablePointersStorageBuffer` capability. Same 7-level nested structure pattern as multi_buffer variant.

### nullptr_graphics — Nullptr usage with variable pointers (graphics)

Tests nullptr usage with variable pointers in graphics pipeline (`vktSpvAsmVariablePointersTests.cpp#L2602-L2743`):
- **opvariable_initialized_null**: Initialize pointer to null, store valid pointer, load through it
- **opselect_null_or_valid_ptr**: OpSelect between nullptr and valid pointer

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pointer type | variable_pointers, physical_pointers | Whether testing SPV_KHR_variable_pointers or SPV_KHR_physical_storage_buffer |
| Buffer type | single_buffer, two_buffers | Single buffer (VariablePointersStorageBuffer) or two buffers (VariablePointers) |
| Selection strategy | opselect, opphi, opcopyobject, opfunctioncall, opptraccesschain | How the variable pointer is obtained |
| Storage class for stores | Private, Function | Where variable pointer variables are stored |
| Index level | 0–6 | Depth of nested structure indirection (outer_struct → float) |
| Input selection | first_input, second_input | Which input buffer member is selected |
| 64-bit indexing | true, false | Whether VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT is used (non-VulkanSC only) |
| Pipeline type | compute, graphics | Shader pipeline under test |

## Support Requirements

- **VK_KHR_variable_pointers** extension (for variable pointer tests)
- **VK_KHR_storage_buffer_storage_class** extension (SPV extension)
- **SPV_KHR_physical_storage_buffer** extension (for physical pointer tests)
- **VariablePointers** or **VariablePointersStorageBuffer** SPIR-V capability
- **PhysicalStorageBufferAddressesEXT** SPIR-V capability (for physical pointer tests)
- **vertexPipelineStoresAndAtomics** + **fragmentStoresAndAtomics** features (graphics tests)
- **VK_EXT_64_bit_indexing** extension and `shader64BitIndexing` feature (64b_indexing sub-group, non-VulkanSC only)

## Verification Methods

- **Compute tests**: Output buffer values are compared against expected values computed on the CPU using the same mux logic (`output[i] = (s[i] < 0) ? A[i] : B[i]`). The `SpvAsmComputeShaderCase` framework handles buffer allocation, shader execution, and result comparison.
- **Graphics tests**: Output image pixel red channel values are compared against expected colors derived from the selected input value. The `createTestsForAllStages` framework handles multi-stage pipeline setup and image verification.
- **Nullptr tests**: Output is compared against a known valid input value to confirm the valid pointer path was taken.

## Notes

- The `addVariablePointersComputeCustomTests` function (`vktSpvAsmVariablePointersTests.cpp#L1388-L1406`) adds additional tests from `vktSpvAsmOpSelectDifferentStridesTests.cpp` into the `compute` sub-group (non-VulkanSC only).
- Physical pointer tests use `PhysicalStorageBuffer64EXT` memory model and pass buffer addresses through a struct in StorageBuffer, while variable pointer tests use `Logical` memory model with separate descriptor bindings.
- The `64b_indexing` sub-group is conditionally compiled under `#ifndef CTS_USES_VULKANSC`.
