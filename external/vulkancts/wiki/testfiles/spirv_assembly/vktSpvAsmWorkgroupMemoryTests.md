# vktSpvAsmWorkgroupMemoryTests

## Overview

SPIR-V Assembly Tests for workgroup memory operations in compute shaders. Tests reading from an input buffer into workgroup (shared) memory, synchronizing with barriers, and writing to an output buffer in reversed order. Covers multiple data types including float16, float32, float64, int8, int16, int32, int64, uint8, uint16, uint32, and uint64.

## Role

Implementation file

## Source

- [vktSpvAsmWorkgroupMemoryTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.workgroup_memory
├── float64
├── float32
├── float16
├── int64
├── int32
├── int16
├── int8
├── uint64
├── uint32
├── uint16
└── uint8
```

## Test Families

### float64 — Workgroup memory with 64-bit floating point

Tests workgroup memory read/write with `OpTypeFloat 64` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L263-L292`). Requires `shaderFloat64` core feature and `Float64` SPIR-V capability.

### float32 — Workgroup memory with 32-bit floating point

Tests workgroup memory read/write with `OpTypeFloat 32` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L294-L318`). No additional features required beyond baseline.

### float16 — Workgroup memory with 16-bit floating point

Tests workgroup memory read/write with `OpTypeFloat 16` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L320-L353`). Requires `VK_KHR_16bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `storageBuffer16BitAccess` feature, and `shaderFloat16` feature.

### int64 — Workgroup memory with 64-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 64 1` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L355-L383`). Requires `shaderInt64` core feature and `Int64` SPIR-V capability.

### int32 — Workgroup memory with 32-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 32 1` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L385-L408`). No additional features required.

### int16 — Workgroup memory with 16-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 16 1` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L410-L441`). Requires `VK_KHR_16bit_storage` extension, `shaderInt16` core feature, and `storageBuffer16BitAccess` feature.

### int8 — Workgroup memory with 8-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 8 1` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L443-L475`). Requires `VK_KHR_8bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `uniformAndStorageBuffer8BitAccess` feature, and `shaderInt8` feature.

### uint64 — Workgroup memory with 64-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 64 0` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L477-L509`). Requires `shaderInt64` core feature and `Int64` SPIR-V capability.

### uint32 — Workgroup memory with 32-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 32 0` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L511-L538`). No additional features required.

### uint16 — Workgroup memory with 16-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 16 0` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L540-L575`). Requires `VK_KHR_16bit_storage` extension, `shaderInt16` core feature, and `storageBuffer16BitAccess` feature.

### uint8 — Workgroup memory with 8-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 8 0` data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L577-L613`). Requires `VK_KHR_8bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `uniformAndStorageBuffer8BitAccess` feature, and `shaderInt8` feature.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Data type | float64, float32, float16, int64, int32, int16, int8, uint64, uint32, uint16, uint8 | Scalar data type for workgroup memory |
| Array size | 128 | Number of elements in workgroup array (fixed) |
| Workgroup size | 16×4×2 = 128 | Local size matches array size |

## Support Requirements

- **Float64** SPIR-V capability + `shaderFloat64` feature (float64)
- **Int64** SPIR-V capability + `shaderInt64` feature (int64, uint64)
- **Int16** SPIR-V capability + `shaderInt16` feature + `VK_KHR_16bit_storage` + `storageBuffer16BitAccess` (int16, uint16)
- **Float16** SPIR-V capability + `shaderFloat16` feature + `VK_KHR_16bit_storage` + `VK_KHR_shader_float16_int8` + `storageBuffer16BitAccess` (float16)
- **Int8** SPIR-V capability + `shaderInt8` feature + `VK_KHR_8bit_storage` + `VK_KHR_shader_float16_int8` + `uniformAndStorageBuffer8BitAccess` (int8, uint8)
- **SPV_KHR_16bit_storage** SPIR-V extension (int16, uint16, float16)
- **SPV_KHR_8bit_storage** SPIR-V extension (int8, uint8)

## Verification Methods

- All tests use the same shader pattern: each invocation reads `inputData[idx]` into `sharedData[idx]`, synchronizes with `OpMemoryBarrier` + `OpControlBarrier`, then writes `sharedData[127-idx]` to `outputData[idx]` (`vktSpvAsmWorkgroupMemoryTests.cpp#L147-L174`).
- Expected output is the input array in reversed order: `outputData[i] = inputData[127-i]`.
- Custom verification functions handle NaN comparison for floating-point types:
  - `checkResultsFloat16` (`vktSpvAsmWorkgroupMemoryTests.cpp#L55-L79`): Compares uint16 values, treating NaN as equal.
  - `checkResultsFloat32` (`vktSpvAsmWorkgroupMemoryTests.cpp#L81-L105`): Compares uint32 values, treating NaN as equal.
  - `checkResultsFloat64` (`vktSpvAsmWorkgroupMemoryTests.cpp#L115-L139`): Compares uint64 values, treating NaN as equal.
- Integer types use default verification (exact byte comparison).

## Notes

- The shader template uses `StringTemplate` with `${dataType}`, `${dataTypeDecl}`, `${sizeBytes}`, `${capabilities}`, and `${extensions}` placeholders to specialize for each data type (`vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261`).
- The workgroup size (16×4×2 = 128 invocations) exactly matches the array size of 128 elements, ensuring each invocation handles one element.
- The `DataType` struct (`vktSpvAsmWorkgroupMemoryTests.cpp#L48-L53`) is defined but not directly used in the current test registration; the test uses inline specialization instead.
