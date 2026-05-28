# vktSpvAsmWorkgroupMemoryTests

## Overview

SPIR-V assembly tests for workgroup memory operations in compute shaders. The shader template reads from an input buffer into [`sharedData`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L214-L217), synchronizes with [`OpMemoryBarrier` and `OpControlBarrier`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L251-L252), and writes the reversed element to the output buffer. The registration covers float16, float32, float64, int8, int16, int32, int64, uint8, uint16, uint32, and uint64 cases.

## Role

Implementation file for the compute `workgroup_memory` group registered by [`createWorkgroupMemoryComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L618).

## Source

- [vktSpvAsmWorkgroupMemoryTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L618)

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

Tests workgroup memory read/write with `OpTypeFloat 64` data type ([`float64` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L292)). Requires `shaderFloat64` core feature and `Float64` SPIR-V capability.

### float32 — Workgroup memory with 32-bit floating point

Tests workgroup memory read/write with `OpTypeFloat 32` data type ([`float32` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L294-L318)). No additional features required beyond baseline.

### float16 — Workgroup memory with 16-bit floating point

Tests workgroup memory read/write with `OpTypeFloat 16` data type ([`float16` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L320-L353)). Requires `VK_KHR_16bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `storageBuffer16BitAccess` feature, and `shaderFloat16` feature.

### int64 — Workgroup memory with 64-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 64 1` data type ([`int64` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L355-L383)). Requires `shaderInt64` core feature and `Int64` SPIR-V capability.

### int32 — Workgroup memory with 32-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 32 1` data type ([`int32` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L385-L408)). No additional features required.

### int16 — Workgroup memory with 16-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 16 1` data type ([`int16` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L410-L441)). Requires `VK_KHR_16bit_storage` extension, `shaderInt16` core feature, and `storageBuffer16BitAccess` feature.

### int8 — Workgroup memory with 8-bit signed integer

Tests workgroup memory read/write with `OpTypeInt 8 1` data type ([`int8` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L443-L475)). Requires `VK_KHR_8bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `uniformAndStorageBuffer8BitAccess` feature, and `shaderInt8` feature.

### uint64 — Workgroup memory with 64-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 64 0` data type ([`uint64` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L477-L509)). Requires `shaderInt64` core feature and `Int64` SPIR-V capability.

### uint32 — Workgroup memory with 32-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 32 0` data type ([`uint32` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L511-L538)). No additional features required.

### uint16 — Workgroup memory with 16-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 16 0` data type ([`uint16` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L540-L575)). Requires `VK_KHR_16bit_storage` extension, `shaderInt16` core feature, and `storageBuffer16BitAccess` feature.

### uint8 — Workgroup memory with 8-bit unsigned integer

Tests workgroup memory read/write with `OpTypeInt 8 0` data type ([`uint8` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L577-L613)). Requires `VK_KHR_8bit_storage` extension, `VK_KHR_shader_float16_int8` extension, `uniformAndStorageBuffer8BitAccess` feature, and `shaderInt8` feature.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Data type | [`float64` through `uint8`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L613) | Scalar data type for workgroup memory |
| Array size | [`128`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L145-L156) | Number of elements in workgroup array (fixed) |
| Workgroup size | [`16×4×2 = 128`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L152-L168) | Local size matches array size |

## Support / Feature Requirements

- [`Float64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L268-L273) SPIR-V capability + `shaderFloat64` feature (float64)
- [`Int64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L360-L365) SPIR-V capability + `shaderInt64` feature (int64, uint64)
- [`Int16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L415-L434) SPIR-V capability + `shaderInt16` feature + `VK_KHR_16bit_storage` + `storageBuffer16BitAccess` (int16, uint16)
- [`Float16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L325-L345) SPIR-V capability + `shaderFloat16` feature + `VK_KHR_16bit_storage` + `VK_KHR_shader_float16_int8` + `storageBuffer16BitAccess` (float16)
- [`Int8`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L448-L468) SPIR-V capability + `shaderInt8` feature + `VK_KHR_8bit_storage` + `VK_KHR_shader_float16_int8` + `uniformAndStorageBuffer8BitAccess` (int8, uint8)
- [`SPV_KHR_16bit_storage`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L328-L329) SPIR-V extension (int16, uint16, float16)
- [`SPV_KHR_8bit_storage`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L451-L468) SPIR-V extension (int8, uint8)

## Verification Methods

- All tests use the same shader pattern: each invocation reads `inputData[idx]` into `sharedData[idx]`, synchronizes with `OpMemoryBarrier` + `OpControlBarrier`, then writes `sharedData[127-idx]` to `outputData[idx]` ([shader-pattern comment](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L147-L174)).
- Expected output is the input array in reversed order, built with [`inputData[numElements - numIdx - 1]`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L279-L289) for each case.
- Custom verification functions handle NaN comparison for floating-point types:
  - `checkResultsFloat16` ([`checkResultsFloat16()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L55-L79)): Compares uint16 values, treating NaN as equal.
  - `checkResultsFloat32` ([`checkResultsFloat32()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L81-L105)): Compares uint32 values, treating NaN as equal.
  - `checkResultsFloat64` ([`checkResultsFloat64()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L115-L139)): Compares uint64 values, treating NaN as equal.
- Integer types use the default `SpvAsmComputeShaderCase` output verification because no custom [`spec.verifyIO`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L283-L286) callback is assigned for integer cases.

## Notes

- The shader template uses `StringTemplate` with `${dataType}`, `${dataTypeDecl}`, `${sizeBytes}`, `${capabilities}`, and `${extensions}` placeholders to specialize for each data type ([`StringTemplate` shader](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261)).
- The workgroup size (16×4×2 = 128 invocations) matches the [`numElements = 128`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L141-L145) array size, so each local invocation handles one element.
- The `DataType` struct ([`DataType`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L48-L53)) is defined but not directly used in the current test registration; the test uses inline specialization instead.
