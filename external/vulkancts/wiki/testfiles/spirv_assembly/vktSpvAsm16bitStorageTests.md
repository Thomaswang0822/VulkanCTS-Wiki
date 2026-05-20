# vktSpvAsm16bitStorageTests

## Overview

Tests for the VK_KHR_16bit_storage extension, verifying that 16-bit float and integer types can be correctly stored in and loaded from storage buffers, uniform buffers, push constants, and input/output interfaces in SPIR-V assembly shaders. Covers conversion operations between 16-bit and 32/64-bit types, struct layout with mixed 16-bit and 32-bit members under std140 and std430 layouts, and chain access patterns.

## Role

Implementation file

## Source

- [vktSpvAsm16bitStorageTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp)

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

Tests conversion of 64-bit floats to 16-bit floats using `OpFConvert` under the `StorageUniformBufferBlock16` capability. Covers scalar, vector, and matrix types. Observed in `addCompute16bitStorageUniform64To16Group`.

### uniform_32_to_16 — 32-bit to 16-bit uniform buffer conversion tests (compute)

Tests conversion of 32-bit floats/ints to 16-bit types under the `StorageUniform{|BufferBlock}16` capabilities. Covers float and integer scalar/vector types. Observed in `addCompute16bitStorageUniform32To16Group`.

### uniform_16_to_32 — 16-bit to 32-bit uniform buffer conversion tests (compute)

Tests conversion of 16-bit floats/ints to 32-bit types under the `StorageUniform{|BufferBlock}16` capabilities. Observed in `addCompute16bitStorageUniform16To32Group`.

### uniform_16_to_64 — 16-bit to 64-bit uniform buffer conversion tests (compute)

Tests conversion of 16-bit floats to 64-bit floats using `OpFConvert`. Observed in `addCompute16bitStorageUniform16To64Group`.

### push_constant_16_to_32 — 16-bit push constant to 32-bit tests (compute)

Tests loading 16-bit values from push constants and converting to 32-bit under the `StoragePushConstant16` capability. Observed in `addCompute16bitStoragePushConstant16To32Group`.

### push_constant_16_to_64 — 16-bit push constant to 64-bit tests (compute)

Tests loading 16-bit float values from push constants and converting to 64-bit floats. Observed in `addCompute16bitStoragePushConstant16To64Group`.

### uniform_16struct_to_32struct — 16-bit struct to 32-bit struct tests (compute)

Tests loading 16-bit float struct data from uniform buffers and converting to 32-bit struct representation. Observed in `addCompute16bitStorageUniform16StructTo32StructGroup`.

### uniform_32struct_to_16struct — 32-bit struct to 16-bit struct tests (compute)

Tests converting 32-bit float struct data to 16-bit struct representation. Observed in `addCompute16bitStorageUniform32StructTo16StructGroup`.

### struct_mixed_types — Mixed 16-bit and 32-bit struct layout tests (compute)

Tests structs containing both 16-bit and 32-bit members with mixed std140/std430 layouts. Observed in `addCompute16bitStructMixedTypesGroup`.

### uniform_16_to_16 — 16-bit to 16-bit pass-through tests (compute)

Tests pass-through of 16-bit values under the `StorageUniformBufferBlock16` capability. Observed in `addCompute16bitStorageUniform16To16Group`.

### uniform_16_to_32_chainaccess — 16-bit to 32-bit chain access tests (compute)

Tests chain access patterns when loading 16-bit values and converting to 32-bit. Observed in `addCompute16bitStorageUniform16To32ChainAccessGroup`.

### uniform_float_64_to_16 — 64-bit float to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 64-bit to 16-bit float conversion. Observed in `addGraphics16BitStorageUniformFloat64To16Group`.

### uniform_float_32_to_16 — 32-bit float to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 32-bit to 16-bit float conversion. Observed in `addGraphics16BitStorageUniformFloat32To16Group`.

### uniform_float_16_to_32 — 16-bit float to 32-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 32-bit float conversion. Observed in `addGraphics16BitStorageUniformFloat16To32Group`.

### uniform_float_16_to_64 — 16-bit float to 64-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 64-bit float conversion. Observed in `addGraphics16BitStorageUniformFloat16To64Group`.

### uniform_int_32_to_16 — 32-bit int to 16-bit uniform tests (graphics)

Graphics pipeline variant testing 32-bit to 16-bit integer conversion. Observed in `addGraphics16BitStorageUniformInt32To16Group`.

### uniform_int_16_to_32 — 16-bit int to 32-bit uniform tests (graphics)

Graphics pipeline variant testing 16-bit to 32-bit integer conversion. Observed in `addGraphics16BitStorageUniformInt16To32Group`.

### input_output_float_* — 16-bit float input/output interface tests (graphics)

Tests 16-bit float data passed through shader input/output interfaces under the `StorageInputOutput16` capability. Includes 64-to-16, 32-to-16, 16-to-32, 16-to-16 pass-through, and 16-to-64 variants. Also tests dual-output pass-through (`16_to_16x2`). Observed in `addGraphics16BitStorageInputOutputFloat*Group` functions.

### input_output_int_* — 16-bit int input/output interface tests (graphics)

Tests 16-bit integer data passed through shader input/output interfaces under the `StorageInputOutput16` capability. Includes 32-to-16, 16-to-32, 16-to-16, and dual-output (`16_to_16x2`) variants. Observed in `addGraphics16BitStorageInputOutputInt*Group` functions.

### push_constant_float_16_to_32 / push_constant_float_16_to_64 / push_constant_int_16_to_32 — Push constant tests (graphics)

Graphics pipeline variants testing 16-bit push constant conversion. Observed in `addGraphics16BitStoragePushConstant*Group` functions.

### uniform_16struct_to_32struct / uniform_32struct_to_16struct / struct_mixed_types — Struct tests (graphics)

Graphics pipeline variants of struct conversion and mixed-type layout tests. Observed in `addGraphics16BitStorageUniformStruct*Group` and `addGraphics16bitStructMixedTypesGroup`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Capability | `uniform_buffer_block` (StorageUniformBufferBlock16), `uniform` (StorageUniform16) | SPIR-V capability for buffer access |
| CompositeType | `scalar`, `vector`, `matrix` | Data type variants for conversion tests |
| TestDefDataType | `DATATYPE_FLOAT`, `DATATYPE_VEC2`, `DATATYPE_INT`, `DATATYPE_UINT`, `DATATYPE_IVEC2`, `DATATYPE_UVEC2` | Data type for test definitions |
| ShaderTemplate | `TYPES`, `STRIDE32BIT_STD140`, `STRIDE32BIT_STD430`, `STRIDE16BIT_STD140`, `STRIDE16BIT_STD430`, `STRIDEMIX_STD140`, `STRIDEMIX_STD430` | Layout/packing mode for struct tests |
| Shader Stage | compute / vertex+fragment | Pipeline stage under test |

## Support Requirements

- **VK_KHR_16bit_storage** extension (observed in vktSpvAsm16bitStorageTests.cpp#L8608)
- SPIR-V capabilities: `StorageUniformBufferBlock16`, `StorageUniform16`, `StoragePushConstant16`, `StorageInputOutput16`
- **shaderFloat64** core feature for 64-bit float tests (observed in vktSpvAsm16bitStorageTests.cpp#L8610)
- For graphics: `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` core features

## Verification Methods

- **Compute 16-bit float comparison**: `computeCheck16BitFloats<RoundingMode>` compares original float values against returned 16-bit values with rounding mode awareness (vktSpvAsm16bitStorageTests.cpp#L262-L284)
- **Compute 16-bit float from 64-bit**: `computeCheck16BitFloats64<RoundingMode>` compares 64-bit originals against 16-bit results (vktSpvAsm16bitStorageTests.cpp#L287-L308)
- **Graphics 16-bit float comparison**: `graphicsCheck16BitFloats<RoundingMode>` batch comparison with rounding mode awareness (vktSpvAsm16bitStorageTests.cpp#L190-L212)
- **64-bit float comparison**: `check64BitFloats` compares expected outputs against returned 64-bit values (vktSpvAsm16bitStorageTests.cpp#L314-L335)
- **32-bit float comparison**: `check32BitFloats` compares expected outputs against returned 32-bit values (vktSpvAsm16bitStorageTests.cpp#L341-L362)
- **Struct comparison**: Similar to 8-bit tests, uses info bitmasks to filter padding bytes

## Notes

- The struct test data uses `structData = {7, 11}` (structArraySize=7, nestedArraySize=11) as defined at vktSpvAsm16bitStorageTests.cpp#L131
- 16-bit float comparisons handle both RTZ and RTE rounding modes via template parameter
- The graphics group has significantly more sub-groups than the compute group due to additional input/output interface tests and separate float/int push constant tests
