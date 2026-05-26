# vktSpvAsm64bitCompareTests

## Overview

Tests for 64-bit data type comparison operations in SPIR-V assembly shaders. Verifies ordered and unordered floating-point comparison operations on `double` types, and signed/unsigned integer comparison operations on `int64_t` and `uint64_t` types. Tests run in both compute and graphics (vertex + fragment) pipeline stages, with scalar and vector data types.

## Role

Implementation file

## Source

- [vktSpvAsm64bitCompareTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1901)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.64bit_compare
├── double
├── int64
└── uint64

spirv_assembly.instruction.graphics.64bit_compare
├── double
├── int64
└── uint64
```

## Test Families

### double — 64-bit floating-point comparison tests

Tests ordered and unordered floating-point comparison operations on `double` type. Operations include: `OpFOrdEqual`, `OpFOrdNotEqual`, `OpFOrdLessThan`, `OpFOrdLessThanEqual`, `OpFOrdGreaterThan`, `OpFOrdGreaterThanEqual`, `OpFUnordEqual`, `OpFUnordNotEqual`, `OpFUnordLessThan`, `OpFUnordLessThanEqual`, `OpFUnordGreaterThan`, `OpFUnordGreaterThanEqual`. Each operation is tested with both single scalar and vec4 data types, and with/without NaN preservation (`nonan`/`withnan` variants). Test names follow the pattern `{stage}_{opname}_{nanmode}_{datatype}`. Created by [`createDoubleCompareTestsInGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1777-L1807) at [vktSpvAsm64bitCompareTests.cpp#L1777-L1807](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1777-L1807).

### int64 — 64-bit signed integer comparison tests

Tests signed integer comparison operations on `int64_t` type. Operations include: `OpIEqual`, `OpINotEqual`, `OpSLessThan`, `OpSLessThanEqual`, `OpSGreaterThan`, `OpSGreaterThanEqual`. Each operation is tested with both single scalar and vec4 data types. Test names follow the pattern `{stage}_{opname}_{datatype}`. Created by [`createInt64CompareTestsInGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1809-L1826) at [vktSpvAsm64bitCompareTests.cpp#L1809-L1826](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1809-L1826).

### uint64 — 64-bit unsigned integer comparison tests

Tests unsigned integer comparison operations on `uint64_t` type. Operations include: `OpIEqual`, `OpINotEqual`, `OpULessThan`, `OpULessThanEqual`, `OpUGreaterThan`, `OpUGreaterThanEqual`. Each operation is tested with both single scalar and vec4 data types. Test names follow the pattern `{stage}_{opname}_{datatype}`. Created by [`createUint64CompareTestsInGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1828-L1845) at [vktSpvAsm64bitCompareTests.cpp#L1828-L1845](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1828-L1845).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Data type | `double`, `int64_t`, `uint64_t` | 64-bit type under test |
| DataType | `DATA_TYPE_SINGLE`, `DATA_TYPE_VECTOR` | Scalar vs vec4 comparison mode |
| Shader Stage | compute: `comp`; graphics: `vert`, `frag` | Pipeline stage under test |
| NaN preservation | `nonan`, `withnan` (double only) | Whether SignedZeroInfNanPreserve is enabled |
| Comparison operation | 12 float ops / 6 int ops per type | SPIR-V comparison instruction |

## Support Requirements

- **shaderFloat64** core feature for double tests (checked in [`checkTypeSupport<double>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1670-L1674) at [vktSpvAsm64bitCompareTests.cpp#L1670-L1674](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1670-L1674))
- **shaderInt64** core feature for int64/uint64 tests (checked in [`check64bitIntegers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1676-L1680) at [vktSpvAsm64bitCompareTests.cpp#L1676-L1680](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1676-L1680))
- **vertexPipelineStoresAndAtomics** for vertex shader tests (checked at [vktSpvAsm64bitCompareTests.cpp#L1708-L1710](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1708-L1710))
- **fragmentStoresAndAtomics** for fragment shader tests (checked at [vktSpvAsm64bitCompareTests.cpp#L1712-L1714](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1712-L1714))
- **VK_KHR_shader_float_controls** extension and [`shaderSignedZeroInfNanPreserveFloat64`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1719-L1725) property for NaN preservation tests (checked at [vktSpvAsm64bitCompareTests.cpp#L1724-L1725](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1724-L1725))
- SPIR-V capabilities: `Float64` (double), `Int64` (int64/uint64), `SignedZeroInfNanPreserve` (withnan)

## Verification Methods

- **CPU-side comparison**: The [`T64bitCompareTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1618-L1638) method runs the shader, reads back the output buffer, and compares each result against the expected value computed by the C++ [`CompareOperation::run()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1627-L1628) method ([vktSpvAsm64bitCompareTests.cpp#L1622-L1638](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1622-L1638))
- For NaN preservation tests, mismatches are only reported when `requireNanPreserve` is true or when neither operand is NaN ([vktSpvAsm64bitCompareTests.cpp#L1629-L1630](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1629-L1630))
- Shader output is `int` (0 or 1) representing boolean comparison result, selected via [`OpSelect`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1740-L1755)

## Notes

- Double operands include NaN values (20 pairs, with 4 containing NaN), while integer operands do not (16 pairs each)
- The compute group uses `VK_SHADER_STAGE_COMPUTE_BIT` and the graphics group uses `VK_SHADER_STAGE_VERTEX_BIT` + `VK_SHADER_STAGE_FRAGMENT_BIT`
- Fragment shader tests use a passthrough GLSL vertex shader ([vktSpvAsm64bitCompareTests.cpp#L754-L765](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L754-L765))
- The [`TestMgr`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1847-L1897) struct provides the parent group name `64bit_compare` and type-specific child group names
