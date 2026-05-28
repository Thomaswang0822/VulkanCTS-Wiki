# vktSpvAsmPointerParameterTests

## Overview

SPIR-V Assembly Tests for pointers as function parameters. Tests passing pointers in Function, Private, StorageBuffer, and Workgroup storage classes as function parameters, including aliased pointer semantics, buffer memory access through pointer parameters, and workgroup memory with variable pointers.

## Role

Implementation file

## Source

- [vktSpvAsmPointerParameterTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082)

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

Tests passing Function-storage-class pointers as function parameters where both parameters can alias the same variable. The source comments spell out the pseudo shader, and the SPIR-V decorates both function parameters with [`Aliased`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L52-L81). The compute shader calls the function once with the same pointer and once with different pointers, then expects [`7.0f`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L110-L140) for all 128 output elements.

### global_to_param — Pointer parameter to global/private variable (graphics only)

Graphics counterpart of [`param_to_param`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L692-L766), using function parameters and aliased decorations in graphics shader fragments. It registers stage-suffixed cases through [`createTestsForAllStages("global_to_param", ...)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L758-L766).

### param_to_global — Pointer parameter to global/private variable

Tests passing a Private-storage-class pointer and a Function-storage-class pointer as function parameters, where functions modify a global/private variable through both paths. The compute version uses the pseudo shader and `Aliased` decorations in [`addComputePointerParamToGlobalTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L143-L256), and the graphics version registers stage-suffixed cases through [`createTestsForAllStages("param_to_global", ...)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L769-L861). Both variants expect [`7.0f`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L247-L256) output values.

### buffer_memory — Buffer memory access through pointer parameters

Tests passing StorageBuffer array pointers as function parameters. The compute shader writes through fixed-size and runtime-array pointers to produce first-half `5.0f` and second-half `2.0f` output values, using [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L291-L385). The graphics version uses the same storage-buffer pattern and registers stage-suffixed cases through [`createTestsForAllStages("buffer_memory", ...)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L864-L969).

### buffer_memory_variable_pointers — Buffer memory with variable-pointer extension coverage

Similar to [`buffer_memory`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L259-L385), with a separately registered compute case and graphics stage-suffixed cases. In the inspected source, this family still emits [`OpCapability VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L420-L424) rather than `OpCapability VariablePointers`, and it requests the [`VK_KHR_variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L505-L513) extension/feature path.

### workgroup_memory_variable_pointers — Workgroup memory with variable pointers (compute only)

Tests passing Workgroup-storage-class array pointers as function parameters with [`VariablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L560-L565) and [`WorkgroupMemoryExplicitLayoutKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L560-L565) capabilities. The shader uses shared workgroup memory, calls functions to write local arrays, synchronizes with [`OpControlBarrier`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L622-L637), and compares against a shuffled expected-output pattern computed on the CPU.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pipeline | [`compute`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082-L1092), [`graphics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1095-L1104) | Shader pipeline under test |
| Pointer storage class | [`Function`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L85-L87), [`Private`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L193-L195), [`StorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L321-L329), [`Workgroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L596-L605) | Storage class of the pointer parameter |
| Aliasing | [`Aliased`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L80-L81), non-aliased call pair | Whether pointer parameters alias the same variable in the test shader |
| Variable pointer capability | [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L292-L295), [`VariablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L560-L565) | Level of variable-pointer support exercised |
| Buffer type | fixed array, runtime array | Storage-buffer arrays are represented by fixed-size and runtime array types in the generated assembly |

## Support / Feature Requirements

- [`VK_KHR_variable_pointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L383-L385) extension is requested by the storage-buffer pointer families.
- [`SPV_KHR_storage_buffer_storage_class`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L292-L295) SPIR-V extension is emitted in storage-buffer assembly.
- [`VariablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L376-L383) feature/capability is requested for storage-buffer pointer tests.
- [`VariablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L680-L687) feature is requested for the workgroup-memory variable-pointer test.
- [`WorkgroupMemoryExplicitLayoutKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L560-L565) capability/extension and [`VK_KHR_workgroup_memory_explicit_layout`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L680-L687) extension are used by the workgroup-memory test.
- [`vertexPipelineStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L758-L766) and [`fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L758-L766) are required by graphics tests that write storage-buffer outputs.

## Verification Methods

- Compute tests provide expected output buffers to [`SpvAsmComputeShaderCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L135-L140), including `7.0f` for aliasing/global tests and `5.0f`/`2.0f` patterns for buffer-memory tests.
- Graphics tests provide expected storage-buffer outputs through [`GraphicsResources`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L758-L766) and register stage-suffixed variants with `createTestsForAllStages`.
- Workgroup memory verification uses a CPU-generated shuffled expected-output sequence after the shader writes and reads shared arrays across invocations.

## Notes

- The compute group registers five cases through [`createPointerParameterComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082-L1092).
- The graphics group registers four base families through [`createPointerParameterGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1095-L1104), expanded by `createTestsForAllStages` into stage-suffixed cases.
- The compute [`param_to_param`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L140) test corresponds to graphics [`global_to_param`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L765-L766) naming.
- The `param_to_param` and `global_to_param` tests use the [`Aliased`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L80-L81) SPIR-V decoration on function parameters to indicate potential aliasing.
