# vktSpvAsmPointerParameterTests

## Overview

SPIR-V Assembly Tests for pointers as function parameters. Tests passing pointers in Function, Private, and StorageBuffer storage classes as function parameters, including aliased pointer semantics, buffer memory access through pointer parameters, and workgroup memory with variable pointers.

## Role

Implementation file

## Source

- [vktSpvAsmPointerParameterTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.pointer_parameter
├── param_to_param
├── param_to_global
├── buffer_memory
├── buffer_memory_variable_pointers
└── workgroup_memory_variable_pointers

spirv_assembly.instruction.graphics.pointer_parameter
├── global_to_param_frag
├── global_to_param_geom
├── global_to_param_tessc
├── global_to_param_tesse
├── global_to_param_vert
├── param_to_global_frag
├── param_to_global_geom
├── param_to_global_tessc
├── param_to_global_tesse
├── param_to_global_vert
├── buffer_memory_frag
├── buffer_memory_geom
├── buffer_memory_tessc
├── buffer_memory_tesse
├── buffer_memory_vert
├── buffer_memory_variable_pointers_frag
├── buffer_memory_variable_pointers_geom
├── buffer_memory_variable_pointers_tessc
├── buffer_memory_variable_pointers_tesse
└── buffer_memory_variable_pointers_vert
```

## Test Families

### param_to_param — Pointer-to-pointer parameter aliasing (compute only)

Tests passing Function-storage-class pointers as function parameters where both parameters alias the same variable (`vktSpvAsmPointerParameterTests.cpp#L45-L141`). The shader implements:

```
float func(alias float* f, alias float* g) {
    *g = 5.0; *f = 2.0; return *g;
}
void main() {
    float a = 0.0;
    o = func(&a, &a);  // should return 2.0 (aliased)
    float b = 0.0;
    o += func(&a, &b); // should return 5.0 (not aliased)
}
```

Expected output: 7.0 for all 128 elements. Uses `Aliased` decoration on function parameters. Compute-only test.

### global_to_param — Pointer parameter to global (Private) variable (graphics only)

Graphics counterpart of param_to_param, passing a Private-storage-class pointer and a Function-storage-class pointer as function parameters (`vktSpvAsmPointerParameterTests.cpp#L692-L767`). Uses `createTestsForAllStages` to generate stage-suffixed test cases (`global_to_param_vert`, `global_to_param_frag`, etc.).

### param_to_global — Pointer parameter to global (Private) variable

Tests passing a Private-storage-class pointer and a Function-storage-class pointer as function parameters, where the function modifies a global variable through both paths (`vktSpvAsmPointerParameterTests.cpp#L143-L257`). Compute version uses `SpvAsmComputeShaderCase`; graphics version (`vktSpvAsmPointerParameterTests.cpp#L769-L864`) uses `createTestsForAllStages` with stage-suffixed names. The shader implements:

```
alias float a = 0.0; // Private storage class
float func0(alias float* f0) { *a = 5.0; *f0 = 2.0; return *a; } // f0 is Private
float func1(alias float* f1) { *a = 5.0; *f1 = 2.0; return *a; } // f1 is Function
void main() {
    o = func0(&a);  // should return 2.0
    float b = 0.0;
    o += func1(&b); // should return 5.0
}
```

Expected output: 7.0 for all 128 elements.

### buffer_memory — Buffer memory access through pointer parameters

Tests passing StorageBuffer array pointers as function parameters (`vktSpvAsmPointerParameterTests.cpp#L259-L386`). The shader passes pointers to fixed-size and runtime arrays in a StorageBuffer to functions that write through those pointers. Uses `VariablePointersStorageBuffer` capability. Expected output: first half = 5.0, second half = 2.0. Graphics version (`vktSpvAsmPointerParameterTests.cpp#L864-L972`) uses `createTestsForAllStages` with stage-suffixed names.

### buffer_memory_variable_pointers — Buffer memory with full variable pointers

Similar to buffer_memory but uses the full `VariablePointers` capability (not just `VariablePointersStorageBuffer`) (`vktSpvAsmPointerParameterTests.cpp#L388-L514`). Requires `VK_KHR_variable_pointers` extension. Same expected output pattern. Graphics version (`vktSpvAsmPointerParameterTests.cpp#L972-L1082`) uses `createTestsForAllStages` with stage-suffixed names.

### workgroup_memory_variable_pointers — Workgroup memory with variable pointers (compute only)

Tests passing Workgroup-storage-class array pointers as function parameters with `VariablePointers` and `WorkgroupMemoryExplicitLayoutKHR` capabilities (`vktSpvAsmPointerParameterTests.cpp#L516-L660`). The shader uses shared workgroup memory with explicit layout, passes pointers to workgroup arrays to functions, and verifies cross-invocation data exchange. Compute-only test.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pipeline | compute, graphics | Shader pipeline under test |
| Pointer storage class | Function, Private, StorageBuffer, Workgroup | Storage class of the pointer parameter |
| Aliasing | aliased, not_aliased | Whether pointer parameters alias the same variable |
| Variable pointers capability | VariablePointersStorageBuffer, VariablePointers | Level of variable pointers support required |
| Buffer type | fixed_array, runtime_array | Array type in StorageBuffer |

## Support Requirements

- **VK_KHR_variable_pointers** extension (for buffer_memory_variable_pointers and workgroup_memory_variable_pointers)
- **VK_KHR_storage_buffer_storage_class** extension (SPV extension)
- **VariablePointersStorageBuffer** SPIR-V capability (for buffer_memory tests)
- **VariablePointers** SPIR-V capability (for variable pointers and workgroup tests)
- **WorkgroupMemoryExplicitLayoutKHR** SPIR-V capability (for workgroup_memory_variable_pointers)
- **VK_KHR_workgroup_memory_explicit_layout** extension (for workgroup_memory_variable_pointers)
- **vertexPipelineStoresAndAtomics** + **fragmentStoresAndAtomics** features (graphics tests)

## Verification Methods

- **Compute tests**: Output buffer values are compared against expected float values (7.0 for aliasing tests, 5.0/2.0 for buffer tests). The `SpvAsmComputeShaderCase` framework handles execution and comparison.
- **Graphics tests**: Output buffer values are compared against expected float values using `createTestsForAllStages` which runs the test across vertex, tessellation, geometry, and fragment stages.

## Notes

- The compute group has 5 test cases while the graphics group has 20 (4 test families × 5 shader stages, with stage-suffixed names).
- The compute `param_to_param` test is named `global_to_param` in the graphics pipeline (same test logic, different registered name).
- The `param_to_param` and `global_to_param` tests use the `Aliased` SPIR-V decoration on function parameters to indicate potential aliasing (`vktSpvAsmPointerParameterTests.cpp#L80-L81`).
- The workgroup_memory_variable_pointers test uses `OpControlBarrier` and `OpMemoryBarrier` for synchronization between invocations (`vktSpvAsmPointerParameterTests.cpp#L516-L660`).
