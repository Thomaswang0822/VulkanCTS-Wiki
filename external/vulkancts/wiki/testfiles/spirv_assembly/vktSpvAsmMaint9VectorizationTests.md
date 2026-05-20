# vktSpvAsmMaint9VectorizationTests

## Overview

Tests for VK_KHR_maintenance9 bitwise operation vectorization, verifying that SPIR-V bitwise operations work correctly with non-32-bit operand types and mixed scalar/vector configurations. Uses buffer device addresses to prevent shader compiler scalarization.

## Role

Implementation file

## Source

- [vktSpvAsmMaint9VectorizationTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.maint9_vectorization
├── bit_count
├── bit_reverse
├── bit_field_insert
├── bit_field_s_extract
└── bit_field_u_extract
```

## Test Families

### bit_count — Tests OpBitCount with various operand types

Tests `OpBitCount` across all combinations of: scalar vs. vec4, 8/16/32/64-bit base types, signed/unsigned, and result bit widths (8/16/32/64). The result type may differ from the base type. Source: `vktSpvAsmMaint9VectorizationTests.cpp#L1296-L1314`.

### bit_reverse — Tests OpBitReverse with various operand types

Tests `OpBitReverse` across all combinations of: scalar vs. vec4, 8/16/32/64-bit types, signed/unsigned. Result type must match base type. Source: `vktSpvAsmMaint9VectorizationTests.cpp#L1316-L1334`.

### bit_field_insert — Tests OpBitFieldInsert with various operand types

Tests `OpBitFieldInsert` across all combinations of: scalar vs. vec4 base, 8/16/32/64-bit base/insert types, 8/16/32/64-bit offset and count types, and signedness variations for each operand. Offset and count are always scalar. Source: `vktSpvAsmMaint9VectorizationTests.cpp#L1336-L1361`.

### bit_field_s_extract — Tests OpBitFieldSExtract with various operand types

Tests `OpBitFieldSExtract` (signed extraction) across all combinations of: scalar vs. vec4 base, 8/16/32/64-bit base types, 8/16/32/64-bit offset and count types, and signedness variations. Source: `vktSpvAsmMaint9VectorizationTests.cpp#L1363-L1387`.

### bit_field_u_extract — Tests OpBitFieldUExtract with various operand types

Tests `OpBitFieldUExtract` (unsigned extraction) with the same parameter space as bit_field_s_extract. Source: `vktSpvAsmMaint9VectorizationTests.cpp#L1389-L1413`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Bit operation | COUNT, REVERSE, INSERT, S_EXTRACT, U_EXTRACT | The SPIR-V bitwise operation |
| Vectorness | scalar, vec4 | Whether operands are scalar or 4-component vectors |
| Bit size | 8, 16, 32, 64 | Bit width of each operand type |
| Signedness | signed, unsigned | Whether each operand is signed or unsigned |
| Operand role | result, base, insert, offset, count | Role of each operand in the operation |

## Support Requirements

- Vulkan 1.3 (uses SPIR-V 1.6 features)
- `VK_KHR_maintenance9` when base operand bit size is not 32 (`vktSpvAsmMaint9VectorizationTests.cpp#L220-L223`)
- `bufferDeviceAddress` feature (Vulkan 1.2)
- `scalarBlockLayout` feature (Vulkan 1.2)
- `shaderInt64` for 64-bit types
- `shaderInt16` for 16-bit types
- `shaderInt8` + `storageBuffer8BitAccess` for 8-bit types
- `storageBuffer16BitAccess` for 16-bit types

## Verification Methods

The `M9V_Instance::iterate()` method (`vktSpvAsmMaint9VectorizationTests.cpp#L1137-L1285`):
1. Generates pseudorandom operand values for each workgroup invocation (64 invocations)
2. For INSERT/S_EXTRACT/U_EXTRACT, constrains offset and count to valid ranges
3. Computes expected results using CPU reference functions (`singleBitCount`, `singleBitReverse`, `singleBitFieldInsert`, `singleBitFieldExtract`)
4. Compares GPU output against CPU reference, reporting mismatches with operation details

## Notes

- Uses PhysicalStorageBufferAddresses (buffer device addresses) to pass operand buffers indirectly, preventing shader compiler scalarization on some implementations
- SPIR-V 1.6 assembly is generated at runtime using `SpirVAsmBuildOptions` with SPIRV_VERSION_1_6
- Test names encode operand types, e.g., `result_s32i-base_s32i` for signed 32-bit scalar OpBitCount
