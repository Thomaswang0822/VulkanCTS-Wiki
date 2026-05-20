# vktSpvAsmVariableInitTests

## Overview

Tests for OpVariable initialization in SPIR-V, covering initialization of Private storage class variables from constants and from Workgroup global variables, as well as initialization of Output storage class variables in graphics shaders.

## Role

Implementation file

## Source

- [vktSpvAsmVariableInitTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.variable_init
└── private

spirv_assembly.instruction.graphics.variable_init
├── private
└── output
```

## Test Families

### private (compute) — Tests OpVariable initialization in Private storage class (compute)

Tests that Private variables initialized with a constant value (all 1.0s) are correctly loaded and stored to an output SSBO. Covers five data types: float, vec4, matrix (mat2x4), floatArray (8 floats), and struct. Additionally tests initialization from Workgroup global variables (float_from_workgroup, vec4_from_workgroup, floatarray_from_workgroup, struct_from_workgroup), which requires VariablePointers and WorkgroupMemoryExplicitLayout for some types. Source: `vktSpvAsmVariableInitTests.cpp#L113-L229`.

### private (graphics) — Tests OpVariable initialization in Private storage class (graphics)

Same as compute private tests but running across all graphics shader stages. Only tests constant initialization source (not Workgroup globals). Source: `vktSpvAsmVariableInitTests.cpp#L231-L317`.

### output (graphics) — Tests OpVariable initialization in Output storage class

Tests that Output variables in vertex shaders can be initialized with a constant value. The initialized output is then read by the fragment shader and stored to an SSBO for verification. Covers float, vec4, matrix, floatArray, and struct types. Source: `vktSpvAsmVariableInitTests.cpp#L602-L654`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Data type | float, vec4, matrix, floatarray, struct | The type of the initialized variable |
| Initialization source | CONSTANT, GLOBAL | Whether the variable is initialized from a constant or a Workgroup global |
| Storage class | Private, Output | The SPIR-V storage class of the variable |
| Shader stage | compute, vertex, fragment, geometry, tess_ctrl, tess_eval | The pipeline stage (graphics only) |

## Support Requirements

- `VK_KHR_storage_buffer_storage_class` extension (all tests)
- `VK_KHR_variable_pointers` extension / `variablePointers` feature (Workgroup global init tests only)
- `VK_KHR_workgroup_memory_explicit_layout` extension (struct_from_workgroup, floatarray_from_workgroup only)
- SPIR-V 1.4 for WorkgroupMemoryExplicitLayout tests
- `vertexPipelineStoresAndAtomics` / `fragmentStoresAndAtomics` (graphics tests)

## Verification Methods

All tests verify that the output buffer contains all 1.0 float values (matching the constant initializer). The expected output is pre-filled with 1.0f values and compared against the shader output. Source: `vktSpvAsmVariableInitTests.cpp#L118-L119` (compute), `vktSpvAsmVariableInitTests.cpp#L239` (graphics).

## Notes

- The `struct` type contains: floatArray (8 floats), vec4, and 4 individual floats — all initialized to 1.0
- Graphics output tests use a custom vertex+fragment shader pair where the vertex shader initializes an Output variable and the fragment shader reads it
- Workgroup global initialization tests store the constant to the Workgroup variable before loading it, testing the pointer indirection path
