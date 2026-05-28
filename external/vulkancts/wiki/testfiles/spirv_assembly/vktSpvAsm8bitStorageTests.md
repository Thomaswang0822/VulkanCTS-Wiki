# vktSpvAsm8bitStorageTests

## Overview

Tests for the VK_KHR_8bit_storage extension, verifying that 8-bit integer types can be correctly stored in and loaded from storage buffers, uniform buffers, and push constants in SPIR-V assembly shaders. Covers conversion operations between 8-bit and 16/32-bit types, as well as struct layout with mixed 8-bit and 32-bit members under both std140 and std430 layouts.

## Role

Implementation file

## Source

- [vktSpvAsm8bitStorageTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5087)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.8bit_storage
├── storagebuffer_32_to_8
├── uniform_8_to_32
├── push_constant_8_to_32
├── storagebuffer_16_to_8
├── uniform_8_to_16
├── push_constant_8_to_16
├── uniform_8_to_8
├── uniform_8struct_to_32struct
├── storagebuffer_32struct_to_8struct
└── struct_mixed_types

spirv_assembly.instruction.graphics.8bit_storage
├── storagebuffer_int_32_to_8
├── uniform_int_8_to_32
├── push_constant_int_8_to_32
├── storagebuffer_int_16_to_8
├── uniform_int_8_to_16
├── push_constant_int_8_to_16
├── 8struct_to_32struct
├── 32struct_to_8struct
└── struct_mixed_types
```

## Test Families

### storagebuffer_32_to_8 — 32-bit to 8-bit storage buffer conversion tests (compute)

Tests conversion of 32-bit integers to 8-bit integers using `OpSConvert`/`OpUConvert` under the [`StorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5092-L5093) capability. Covers scalar and vector types (scalar_sint, scalar_uint, vector_sint, vector_uint). Observed in [`addCompute8bitStorage32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084) at [vktSpvAsm8bitStorageTests.cpp#L928-L1084](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084).

### uniform_8_to_32 — 8-bit to 32-bit uniform buffer conversion tests (compute)

Tests conversion of 8-bit integers to 32-bit integers loaded from uniform buffers under the [`UniformAndStorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5094-L5107) capability. Covers scalar and vector signed/unsigned types. Observed in [`addCompute8bitUniform8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1086-L1200) at [vktSpvAsm8bitStorageTests.cpp#L1086-L1200](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1086-L1200).

### push_constant_8_to_32 — 8-bit push constant to 32-bit conversion tests (compute)

Tests loading 8-bit values from push constants and converting them to 32-bit under the [`StoragePushConstant8`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5096-L5104) capability. Observed in [`addCompute8bitStoragePushConstant8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1243-L1403).

### storagebuffer_16_to_8 — 16-bit to 8-bit storage buffer conversion tests (compute)

Tests conversion of 16-bit integers to 8-bit integers under the [`StorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5092-L5093) capability. Observed in [`addCompute8bitStorage16To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1405-L1560).

### uniform_8_to_16 — 8-bit to 16-bit uniform buffer conversion tests (compute)

Tests conversion of 8-bit integers to 16-bit integers loaded from uniform buffers under the [`UniformAndStorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5094-L5107) capability. Observed in [`addCompute8bitUniform8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1562-L1722).

### push_constant_8_to_16 — 8-bit push constant to 16-bit conversion tests (compute)

Tests loading 8-bit values from push constants and converting them to 16-bit under the [`StoragePushConstant8`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5096-L5104) capability. Observed in [`addCompute8bitStoragePushConstant8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1724-L1889).

### uniform_8_to_8 — 8-bit to 8-bit uniform buffer pass-through tests (compute)

Tests pass-through of 8-bit values loaded from and stored to uniform buffers under the [`UniformAndStorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5094-L5107) capability. Observed in [`addCompute8bitStorageBuffer8To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1891-L1972).

### uniform_8struct_to_32struct — 8-bit struct to 32-bit struct conversion tests (compute)

Tests loading 8-bit struct data from uniform buffers and converting to 32-bit struct representation. Observed in [`addCompute8bitStorageUniform8StructTo32StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1974-L2194).

### storagebuffer_32struct_to_8struct — 32-bit struct to 8-bit struct conversion tests (compute)

Tests converting 32-bit struct data to 8-bit struct representation and storing to storage buffers. Observed in [`addCompute8bitStorageUniform32StructTo8StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2196-L2422).

### struct_mixed_types — Mixed 8-bit and 32-bit struct layout tests (compute)

Tests structs containing both 8-bit and 32-bit members with mixed std140/std430 layouts. Uses [`checkStruct`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L655-L670) verification comparing data bytes while accounting for padding offsets. Observed in [`addCompute8bitStorage8bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2424-L2654).

### storagebuffer_int_32_to_8 — 32-bit to 8-bit integer storage buffer tests (graphics)

Graphics pipeline variant of 32-to-8 conversion, testing vertex and fragment stages. Observed in [`addGraphics8BitStorageUniformInt32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2663-L2873).

### uniform_int_8_to_32 — 8-bit to 32-bit integer uniform buffer tests (graphics)

Graphics pipeline variant of 8-to-32 conversion. Observed in [`addGraphics8BitStorageUniformInt8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2875-L3137).

### push_constant_int_8_to_32 — 8-bit push constant to 32-bit tests (graphics)

Graphics pipeline variant of push constant 8-to-32 conversion. Observed in [`addGraphics8BitStoragePushConstantInt8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3139-L3458).

### storagebuffer_int_16_to_8 — 16-bit to 8-bit integer storage buffer tests (graphics)

Graphics pipeline variant of 16-to-8 conversion. Observed in [`addGraphics8BitStorageUniformInt16To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3460-L3681).

### uniform_int_8_to_16 — 8-bit to 16-bit integer uniform buffer tests (graphics)

Graphics pipeline variant of 8-to-16 conversion. Observed in [`addGraphics8BitStorageUniformInt8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3683-L3952).

### push_constant_int_8_to_16 — 8-bit push constant to 16-bit tests (graphics)

Graphics pipeline variant of push constant 8-to-16 conversion. Observed in [`addGraphics8BitStoragePushConstantInt8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3954-L4282).

### 8struct_to_32struct — 8-bit struct to 32-bit struct tests (graphics)

Graphics pipeline variant of 8-bit struct to 32-bit struct conversion. Observed in [`addGraphics8BitStorageUniformStruct8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4284-L4562).

### 32struct_to_8struct — 32-bit struct to 8-bit struct tests (graphics)

Graphics pipeline variant of 32-bit struct to 8-bit struct conversion. Observed in [`addGraphics8BitStorageUniformStruct32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4564-L4842).

### struct_mixed_types — Mixed type struct tests (graphics)

Graphics pipeline variant of mixed 8-bit/32-bit struct layout tests. Observed in [`addGraphics8bitStorage8bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4844-L5082).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Capability | `storage_buffer`, `uniform`, `push_constant` | SPIR-V capability controlling buffer access mode |
| CompositeType | `scalar_sint`, `scalar_uint`, `vector_sint`, `vector_uint` | Data type variants for scalar/vector conversion tests |
| ShaderTemplate | `STRIDE8BIT_STD140`, `STRIDE32BIT_STD140`, `STRIDEMIX_STD140`, `STRIDE8BIT_STD430`, `STRIDE32BIT_STD430`, `STRIDEMIX_STD430` | Layout/packing mode for struct tests |
| Shader Stage | compute / vertex+fragment | Pipeline stage under test |

## Support / Feature Requirements

- **VK_KHR_8bit_storage** extension (observed in [vktSpvAsm8bitStorageTests.cpp#L1077](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1077))
- **VK_KHR_storage_buffer_storage_class** extension (observed in [vktSpvAsm8bitStorageTests.cpp#L1078](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1078))
- **SPV_KHR_8bit_storage** SPIR-V extension
- SPIR-V capabilities: [`StorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5092-L5093), [`UniformAndStorageBuffer8BitAccess`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5094-L5107), [`StoragePushConstant8`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5096-L5104)
- For graphics: [`vertexPipelineStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5076-L5078) and [`fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5076-L5078) core features (observed in [vktSpvAsm8bitStorageTests.cpp#L5077-L5078](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5077-L5078))

## Verification Methods

- **Compute buffer comparison**: [`computeCheckBuffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161) performs byte-level memory comparison of original input data against output allocation ([vktSpvAsm8bitStorageTests.cpp#L155-L161](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161))
- **Struct comparison**: [`checkStruct<originType, resultType, funcOrigin, funcResult>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L655-L670) template compares data bytes while filtering out padding/offset bytes using info bitmasks ([vktSpvAsm8bitStorageTests.cpp#L575-L670](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L575-L670))
- **Uniform array comparison**: [`checkUniformsArray`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L673-L704) and [`checkUniformsArrayConstNdx`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L706-L736) handle std140 array stride padding ([vktSpvAsm8bitStorageTests.cpp#L672-L736](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L672-L736))
- **Graphics verification**: Uses [`createTestsForAllStages`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5080-L5081) which renders and compares against expected color output

## Notes

- The struct test data uses [`structData = {7, 11}`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L116) (structArraySize=7, nestedArraySize=11) as defined at [vktSpvAsm8bitStorageTests.cpp#L116](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L116)
- The [`arrayStrideInBytesUniform = 16u`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L80) constant ([vktSpvAsm8bitStorageTests.cpp#L80](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L80)) reflects the std140 minimum array stride requirement
- Graphics and compute groups have slightly different child names (e.g., `storagebuffer_32_to_8` vs `storagebuffer_int_32_to_8`)
