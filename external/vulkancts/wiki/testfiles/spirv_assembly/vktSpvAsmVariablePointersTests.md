# vktSpvAsmVariablePointersTests

## Overview

SPIR-V assembly tests for the [`SPV_KHR_variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L212-L215) and [`SPV_KHR_physical_storage_buffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L212-L218) paths. The file registers variable-pointer operations such as [`OpSelect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L357-L384), [`OpPhi`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L415-L450), [`OpFunctionCall`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L386-L413), and [`OpPtrAccessChain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L523-L561), plus nullptr and 64-bit-indexing variants.

## Role

Implementation file for compute and graphics `variable_pointers` groups and the compute `physical_pointers` group registered by [`createVariablePointersComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2747), [`createPhysicalPointersComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2778), and [`createVariablePointersGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2803).

## Source

- [vktSpvAsmVariablePointersTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2747)

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

- **reads_opselect**: Select between two pointers using `OpSelect` ([`reads_opselect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L357-L384) and [`reads_opfunctioncall`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L386-L413))
- **reads_opphi**: Select between two pointers using `OpPhi` ([`reads_opphi`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L415-L450))
- **reads_opcopyobject**: Copy pointers with `OpCopyObject` then select ([`reads_opcopyobject`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L452-L484))
- **stores_private / stores_function**: Store variable pointers into Private/Function storage class variables ([`stores_private` / `stores_function`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L486-L520))
- **reads_opptraccesschain**: Use `OpPtrAccessChain` to compute pointer offsets, then select ([`reads_opptraccesschain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L523-L561))
- **writes**: Write through a variable pointer (load, increment, store back) ([`writes`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L563-L593))
- **workgroup_two_buffers**: Variable pointers on Workgroup storage class (two-buffer variant only) ([`workgroup_two_buffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L596-L639))

Each test is parameterized by buffer type: [`single_buffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L335-L345) uses `VariablePointersStorageBuffer`, while [`two_buffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L339-L354) uses `VariablePointers`. Physical pointer variants use [`PhysicalStorageBufferAddressesEXT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L339-L341) instead.

### complex_types_compute — Variable/physical pointers into nested structures

Tests variable pointers and physical storage buffer pointers pointing into various levels of nested data structures in compute shaders ([`addComplexTypesPhysicalOrVariablePointersComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L643-L1255)). The data structure is:

```
struct inner_struct { vec4 x[2]; vec4 y[2]; };
struct outer_struct { inner_struct r[2][2]; };
struct input_buffer { outer_struct a; outer_struct b; };
```

Tests exercise 7 levels of pointer indirection (outer_struct → matrices → arrays → inner_structs → vec4arr → vec4 → float), using:
- `OpSelect` to choose between pointers at each level
- `OpFunctionCall` returning a variable pointer
- `OpPtrAccessChain` for pointer arithmetic at each level

Parameterized by [`single_buffer` vs `two_buffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L938-L963), [`first_input` vs `second_input`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L949-L962), and [`7` index levels](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L716-L716).

### nullptr_compute — Nullptr usage with variable pointers

Tests usage of `OpConstantNull` with variable pointers in compute shaders ([`addNullptrVariablePointersComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1257-L1386)):
- **opvariable_initialized_null**: Initialize a pointer variable to null, then store a valid pointer and load through it ([`opvariable_initialized_null`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1347-L1365))
- **opselect_null_or_valid_ptr**: Use `OpSelect` to choose between nullptr and a valid pointer; forced to choose valid ([`opselect_null_or_valid_ptr`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1367-L1384))

Requires the [`VariablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1312-L1316) capability and [`variablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1265-L1267) feature (not just `VariablePointersStorageBuffer`).

### 64b_indexing — 64-bit indexing variants (non-VulkanSC only)

Repeats the compute, complex_types_compute, and nullptr_compute tests with 64-bit indexing enabled ([`64b_indexing` registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2760-L2773)). Only available inside the [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2760-L2773) block.

### graphics — Basic variable pointer graphics tests

Tests variable pointer operations in graphics pipeline stages (vertex, tessellation, geometry, fragment) ([`addVariablePointersGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1408-L1807)). Same mux pattern as compute but using [`createTestsForAllStages()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1602-L1603) to generate tests for all graphics stages. Covers:
- reads_opselect, reads_opfunctioncall, reads_opphi, reads_opcopyobject
- stores_private / stores_function
- reads_opptraccesschain
- writes

Requires [`vertexPipelineStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1574-L1576) and [`fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1574-L1576) features.

### multi_buffer_read_only_graphics — Read-only variable pointers across two input buffers (graphics)

Tests variable pointers pointing into two separate read-only input buffers in graphics pipeline ([`addTwoInputBufferReadOnlyVariablePointersGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1827-L2228)). Uses the [`VariablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1882-L1884) capability. Tests [`7` levels](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1868-L1880) of nested structure indirection with OpSelect, OpCopyObject, OpPhi, OpFunctionCall, and OpPtrAccessChain. Results are written to the red channel of the output color via [`OpCompositeInsert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1987-L1994).

### single_buffer_read_only_graphics — Read-only variable pointers within a single buffer (graphics)

Tests variable pointers confined to a single input buffer in graphics pipeline ([`addSingleInputBufferReadOnlyVariablePointersGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2230-L2641)). Uses the [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2290-L2292) capability. Same [`7`-level](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2276-L2288) nested structure pattern as the multi-buffer variant.

### nullptr_graphics — Nullptr usage with variable pointers (graphics)

Tests nullptr usage with variable pointers in graphics pipeline ([`addNullptrVariablePointersGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2643-L2743)):
- **opvariable_initialized_null**: Initialize pointer to null, store valid pointer, and load through it in the graphics path ([`graphics null variable case`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2714-L2727)).
- **opselect_null_or_valid_ptr**: `OpSelect` between nullptr and valid pointer in the graphics path ([`graphics null select case`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2729-L2741)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pointer type | [`variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2747-L2759), [`physical_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2778-L2786) | Whether testing SPV_KHR_variable_pointers or SPV_KHR_physical_storage_buffer |
| Buffer type | [`single_buffer`, `two_buffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L335-L345) | Single buffer (VariablePointersStorageBuffer) or two buffers (VariablePointers) |
| Selection strategy | [`opselect`, `opphi`, `opcopyobject`, `opfunctioncall`, `opptraccesschain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1051-L1250) | How the variable pointer is obtained |
| Storage class for stores | [`Private`, `Function`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L486-L498) | Where variable pointer variables are stored |
| Index level | [`0–6`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L716-L716) | Depth of nested structure indirection (outer_struct → float) |
| Input selection | [`first_input`, `second_input`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L949-L963) | Which input buffer member is selected |
| 64-bit indexing | [`true`, `false`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2747-L2773) | Whether 64-bit indexing is enabled in the generated `ComputeShaderSpec` (non-VulkanSC only) |
| Pipeline type | compute, graphics | Shader pipeline under test |

## Support / Feature Requirements

- [`VK_KHR_variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L382-L384) extension (for variable pointer tests)
- [`SPV_KHR_storage_buffer_storage_class`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L215-L218) SPIR-V extension
- [`SPV_KHR_physical_storage_buffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L212-L218) extension (for physical pointer tests)
- [`VariablePointers` or `VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L339-L354) SPIR-V capability
- [`PhysicalStorageBufferAddressesEXT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L339-L341) SPIR-V capability (for physical pointer tests)
- [`vertexPipelineStoresAndAtomics` + `fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1574-L1576) features (graphics tests that write SSBOs)
- 64-bit indexing is enabled by setting [`spec.uses64BitIndexing`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L370-L372) in the `64b_indexing` sub-group (non-VulkanSC only).

## Verification Methods

- **Compute tests**: Output buffer values are compared against expected vectors computed on the CPU using the same mux logic for [`single_buffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L187-L205) and [`two_buffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L200-L205); `SpvAsmComputeShaderCase` receives those expected buffers in [`spec.outputs`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L381-L384).
- **Graphics tests**: Output image red-channel values are compared against expected colors produced by [`getExpectedOutputColor()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1809-L1825) and passed to [`createTestsForAllStages()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2106-L2108).
- **Nullptr tests**: Output is compared against a known valid input value (`78` for compute, `78/255.f` for graphics) to confirm the valid pointer path was taken ([compute](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1259-L1263), [graphics](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2643-L2655)).

## Notes

- [`addVariablePointersComputeCustomTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1388-L1406) adds additional tests from [`vktSpvAsmOpSelectDifferentStridesTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpSelectDifferentStridesTests.cpp) into the `compute` sub-group (non-VulkanSC only).
- Physical pointer tests use the [`PhysicalStorageBuffer64EXT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L212-L218) memory model and pass buffer addresses through a StorageBuffer struct, while variable pointer tests use [`Logical`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L215-L218) memory model with separate descriptor bindings.
- The `64b_indexing` sub-group is conditionally compiled under [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2760-L2773).
