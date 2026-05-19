# vktAtomicOperationTests.cpp

## Overview

Tests for SPIR-V atomic operations (OpAtomic*) across various data types, shader stages, and memory types. Verifies correctness of atomic exchange, compare-swap, add, min, max, and/or/xor operations on buffer memory, shared memory, reference-based buffer memory, and task payload memory.

## Role

Combined registration and implementation file. Contains the `addAtomicOperationTests()` function that builds the flat test case hierarchy, as well as the `AtomicOperationCase` / `AtomicOperationInstance` test classes and supporting infrastructure (buffer helpers, reference computation, result checking).

## Source Code

- [vktAtomicOperationTests.cpp](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1-L1595) (full file)
- Test case class: [AtomicOperationCase](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1010-L1060)
- Test instance class: [AtomicOperationInstance](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L874-L1008)
- Registration function: [addAtomicOperationTests()](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1468-L1585)
- Entry point: [createAtomicOperationTests()](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1589-L1592)

## Registration Hierarchy

```text
glsl.atomic_operations
├── {operation}_{data_type}_{shader_stage}{memory_suffix}  (flat test cases)
```

Test cases are named using the pattern `{operation}_{data_type}_{shader_stage}{memory_suffix}` where:
- `operation`: exchange, comp_swap, add, min, max, and, or, xor
- `data_type`: float16, f16vec2, f16vec4, signed, unsigned, float32, signed64bit, unsigned64bit, float64
- `shader_stage`: vertex, fragment, geometry, tess_ctrl, tess_eval, compute, task, mesh
- `memory_suffix`: "" (buffer), "_shared", "_reference", "_payload"

## Test Families

| Family | Class | Description |
|--------|-------|-------------|
| AtomicOperationCase | [AtomicOperationCase](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1010-L1060) | Test case that configures shader spec and checks support |
| AtomicOperationInstance | [AtomicOperationInstance](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L874-L1008) | Test instance that executes shader and validates results |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| AtomicOperation | exchange, comp_swap, add, min, max, and, or, xor (8 operations) |
| DataType | float16, f16vec2, f16vec4, signed (int32), unsigned (uint32), float32, signed64bit (int64), unsigned64bit (uint64), float64 (9 types) |
| ShaderType | vertex, fragment, geometry, tess_ctrl, tess_eval, compute, task, mesh (8 stages) |
| AtomicMemoryType | BUFFER, SHARED, REFERENCE, PAYLOAD (4 types) |

Not all combinations are valid:
- Float types (float16, f16vec2, f16vec4, float32, float64) only support add, exchange, min, max operations
- SHARED memory is only available in compute, task, and mesh shaders
- PAYLOAD memory is only available in task shaders

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_shader_atomic_int64 | Required for 64-bit integer types (signed64bit, unsigned64bit) |
| VK_EXT_shader_atomic_float | Required for float32 atomic operations |
| VK_EXT_shader_atomic_float2 | Required for float16/f16vec2/f16vec4 and float64 atomic operations |
| VK_NV_shader_atomic_float16_vector | Required for f16vec2/f16vec4 atomic operations |
| VK_KHR_buffer_device_address | Required for REFERENCE memory type tests |
| shaderInt64 core feature | Required for 64-bit integer operations |
| shaderFloat16 | Required for float16 operations |
| shaderFloat64 | Required for float64 operations |

## Verification Methods

- CPU-side reference computation via `TestBuffer::checkResults()` using `tcu::ResultCollector`
- Integer types: bitwise comparison using `deMemCmp()` for exact match
- Floating-point types: `sloppyFPCompare()` with tolerance of 0.00001 for float32/float64, 0.01 for float16
- NaN-safe comparison via `nanSafeSloppyEquals()` which treats two NaN values as equal

## Notes

- The test uses a serial execution model: each invocation performs the atomic operation sequentially on a shared memory location, enabling deterministic reference computation
- The `AtomicShaderType` helper class encapsulates both the shader stage and memory type, with assertions enforcing valid combinations (e.g., SHARED only with compute/task/mesh, PAYLOAD only with task)
- Reference-based buffer tests (`_reference` suffix) pass buffer addresses via `VK_KHR_buffer_device_address` and use pointer dereference in the shader
