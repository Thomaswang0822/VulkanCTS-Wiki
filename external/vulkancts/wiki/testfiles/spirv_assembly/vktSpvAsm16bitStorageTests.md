# vktSpvAsm16bitStorageTests

## Overview

Tests for the VK_KHR_16bit_storage extension, verifying that 16-bit float and integer types can be correctly stored in and loaded from storage buffers, uniform buffers, push constants, and input/output interfaces in SPIR-V assembly shaders. Covers conversion operations between 16-bit and 32/64-bit types, struct layout with mixed 16-bit and 32-bit members under std140 and std430 layouts, and chain access patterns.

## Role

Implementation file

## Source

- [vktSpvAsm16bitStorageTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8620)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.16bit_storage
├── uniform_64_to_16
├── uniform_32_to_16
├── uniform_16_to_32
├── uniform_16_to_64
├── push_constant_16_to_32
├── push_constant_16_to_64
├── uniform_16struct_to_32struct
├── uniform_32struct_to_16struct
├── struct_mixed_types
├── uniform_16_to_16
└── uniform_16_to_32_chainaccess

spirv_assembly.instruction.graphics.16bit_storage
├── uniform_float_64_to_16
├── uniform_float_32_to_16
├── uniform_float_16_to_32
├── uniform_float_16_to_64
├── uniform_int_32_to_16
├── uniform_int_16_to_32
├── input_output_float_64_to_16
├── input_output_float_32_to_16
├── input_output_float_16_to_32
├── input_output_float_16_to_16
├── input_output_float_16_to_64
├── input_output_float_16_to_16x2
├── input_output_int_16_to_16x2
├── input_output_int_32_to_16
├── input_output_int_16_to_32
├── input_output_int_16_to_16
├── push_constant_float_16_to_32
├── push_constant_float_16_to_64
├── push_constant_int_16_to_32
├── uniform_16struct_to_32struct
├── uniform_32struct_to_16struct
└── struct_mixed_types
```

## Test Families

### uniform_64_to_16 — 64-bit to 16-bit uniform buffer conversion tests (compute)

Tests conversion of 64-bit floats to 16-bit floats using `OpFConvert` under the [`StorageUniformBufferBlock16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8624-L8644) capability. Covers scalar, vector, and matrix types. Observed in [`addCompute16bitStorageUniform64To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L7476-L8625).

### uniform_32_to_16 — 32-bit to 16-bit uniform buffer conversion tests (compute)

Tests conversion of 32-bit floats/ints to 16-bit types under the `StorageUniform{|BufferBlock}16` capabilities. Covers float and integer scalar/vector types. Observed in [`addCompute16bitStorageUniform32To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2324-L8627).

### uniform_16_to_32 — 16-bit to 32-bit uniform buffer conversion tests (compute)

Tests conversion of 16-bit floats/ints to 32-bit types under the `StorageUniform{|BufferBlock}16` capabilities. Observed in [`addCompute16bitStorageUniform16To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1128-L8629).

### uniform_16_to_64 — 16-bit to 64-bit uniform buffer conversion tests (compute)

Tests conversion of 16-bit floats to 64-bit floats using `OpFConvert`. Observed in [`addCompute16bitStorageUniform16To64Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8205-L8631).

### push_constant_16_to_32 — 16-bit push constant to 32-bit tests (compute)

Tests loading 16-bit values from push constants and converting to 32-bit under the [`StoragePushConstant16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8632-L8635) capability. Observed in [`addCompute16bitStoragePushConstant16To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1703-L8633).

### push_constant_16_to_64 — 16-bit push constant to 64-bit tests (compute)

Tests loading 16-bit float values from push constants and converting to 64-bit floats. Observed in [`addCompute16bitStoragePushConstant16To64Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8455-L8635).

### uniform_16struct_to_32struct — 16-bit struct to 32-bit struct tests (compute)

Tests loading 16-bit float struct data from uniform buffers and converting to 32-bit struct representation. Observed in [`addCompute16bitStorageUniform16StructTo32StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2602-L8637).

### uniform_32struct_to_16struct — 32-bit struct to 16-bit struct tests (compute)

Tests converting 32-bit float struct data to 16-bit struct representation. Observed in [`addCompute16bitStorageUniform32StructTo16StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2826-L8639).

### struct_mixed_types — Mixed 16-bit and 32-bit struct layout tests (compute)

Tests structs containing both 16-bit and 32-bit members with mixed std140/std430 layouts. Observed in [`addCompute16bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3053-L8641).

### uniform_16_to_16 — 16-bit to 16-bit pass-through tests (compute)

Tests pass-through of 16-bit values under the [`StorageUniformBufferBlock16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8624-L8644) capability. Observed in [`addCompute16bitStorageUniform16To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2243-L8643).

### uniform_16_to_32_chainaccess — 16-bit to 32-bit chain access tests (compute)

Tests chain access patterns when loading 16-bit values and converting to 32-bit. Observed in [`addCompute16bitStorageUniform16To32ChainAccessGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1506-L8645).

### uniform_float_64_to_16 — 64-bit float to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 64-bit to 16-bit float conversion. Observed in [`addGraphics16BitStorageUniformFloat64To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L7673-L8656).

### uniform_float_32_to_16 — 32-bit float to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 32-bit to 16-bit float conversion. Observed in [`addGraphics16BitStorageUniformFloat32To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3277-L8658).

### uniform_float_16_to_32 — 16-bit float to 32-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 32-bit float conversion. Observed in [`addGraphics16BitStorageUniformFloat16To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L5623-L8660).

### uniform_float_16_to_64 — 16-bit float to 64-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 64-bit float conversion. Observed in [`addGraphics16BitStorageUniformFloat16To64Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L6879-L8662).

### uniform_int_32_to_16 — 32-bit int to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 32-bit to 16-bit integer conversion. Observed in [`addGraphics16BitStorageUniformInt32To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2001-L8664).

### uniform_int_16_to_32 — 16-bit int to 32-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 32-bit integer conversion. Observed in [`addGraphics16BitStorageUniformInt16To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L5354-L8666).

### input_output_float_* — 16-bit float input/output interface tests (graphics)

Tests 16-bit float data passed through shader input/output interfaces under the [`StorageInputOutput16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8667-L8686) capability. Includes 64-to-16, 32-to-16, 16-to-32, 16-to-16 pass-through, and 16-to-64 variants. Also tests dual-output pass-through (`16_to_16x2`). Observed in [`addGraphics16BitStorageInputOutputFloat*Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3637-L8678) functions.

### input_output_int_* — 16-bit int input/output interface tests (graphics)

Tests 16-bit integer data passed through shader input/output interfaces under the [`StorageInputOutput16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8667-L8686) capability. Includes 32-to-16, 16-to-32, 16-to-16, and dual-output (`16_to_16x2`) variants. Observed in [`addGraphics16BitStorageInputOutputInt*Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4298-L8686) functions.

### push_constant_float_16_to_32 / push_constant_float_16_to_64 / push_constant_int_16_to_32 — Push constant tests (graphics)

Graphics pipeline variants testing 16-bit push constant conversion. Observed in [`addGraphics16BitStoragePushConstant*Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4734-L8692) functions.

### uniform_16struct_to_32struct / uniform_32struct_to_16struct / struct_mixed_types — Struct tests (graphics)

Graphics pipeline variants of struct conversion and mixed-type layout tests. Observed in [`addGraphics16BitStorageUniformStruct*Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L6020-L8696) and [`addGraphics16bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L6525-L8698).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Capability | `uniform_buffer_block` (StorageUniformBufferBlock16), `uniform` (StorageUniform16) | SPIR-V capability for buffer access |
| CompositeType | `scalar`, `vector`, `matrix` | Data type variants for conversion tests |
| TestDefDataType | `DATATYPE_FLOAT`, `DATATYPE_VEC2`, `DATATYPE_INT`, `DATATYPE_UINT`, `DATATYPE_IVEC2`, `DATATYPE_UVEC2` | Data type for test definitions |
| ShaderTemplate | `TYPES`, `STRIDE32BIT_STD140`, `STRIDE32BIT_STD430`, `STRIDE16BIT_STD140`, `STRIDE16BIT_STD430`, `STRIDEMIX_STD140`, `STRIDEMIX_STD430` | Layout/packing mode for struct tests |
| Shader Stage | compute / vertex+fragment | Pipeline stage under test |

## Support / Feature Requirements

- **VK_KHR_16bit_storage** extension (observed in [vktSpvAsm16bitStorageTests.cpp#L8608](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8608))
- SPIR-V capabilities: [`StorageUniformBufferBlock16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8624-L8644), [`StorageUniform16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8626-L8644), [`StoragePushConstant16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8632-L8635), [`StorageInputOutput16`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8667-L8686)
- **shaderFloat64** core feature for 64-bit float tests (observed in [vktSpvAsm16bitStorageTests.cpp#L8610](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8610))
- For graphics: [`vertexPipelineStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2161-L2167) and [`fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L5040-L5047) core features

## Verification Methods

- **Compute 16-bit float comparison**: [`computeCheck16BitFloats<RoundingMode>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L262-L284) compares original float values against returned 16-bit values with rounding mode awareness ([vktSpvAsm16bitStorageTests.cpp#L262-L284](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L262-L284))
- **Compute 16-bit float from 64-bit**: [`computeCheck16BitFloats64<RoundingMode>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L287-L308) compares 64-bit originals against 16-bit results ([vktSpvAsm16bitStorageTests.cpp#L287-L308](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L287-L308))
- **Graphics 16-bit float comparison**: [`graphicsCheck16BitFloats<RoundingMode>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L190-L212) batch comparison with rounding mode awareness ([vktSpvAsm16bitStorageTests.cpp#L190-L212](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L190-L212))
- **64-bit float comparison**: [`check64BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L314-L335) compares expected outputs against returned 64-bit values ([vktSpvAsm16bitStorageTests.cpp#L314-L335](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L314-L335))
- **32-bit float comparison**: [`check32BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L341-L362) compares expected outputs against returned 32-bit values ([vktSpvAsm16bitStorageTests.cpp#L341-L362](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L341-L362))
- **Struct comparison**: Similar to 8-bit tests, uses info bitmasks to filter padding bytes

## Notes

- The struct test data uses [`structData = {7, 11}`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L131) (structArraySize=7, nestedArraySize=11) as defined at [vktSpvAsm16bitStorageTests.cpp#L131](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L131)
- 16-bit float comparisons handle both RTZ and RTE rounding modes via template parameter
- The graphics group has significantly more sub-groups than the compute group due to additional input/output interface tests and separate float/int push constant tests
