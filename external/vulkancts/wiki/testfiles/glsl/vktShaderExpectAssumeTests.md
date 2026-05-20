# vktShaderExpectAssumeTests.cpp

## Overview

Tests for the VK_KHR_shader_expect_assume extension. Verifies correct operation of the `OpExpectKHR` and `OpAssumeTrueKHR` SPIR-V instructions across different data classes (constant, specialization constant, push constant, storage buffer), data types (bool, int8, int16, int32, int64), and shader stages (vertex, fragment, compute).

## Role

Combined registration and implementation file. Contains the `addShaderExpectAssumeTests()` function that builds the test hierarchy, as well as the `ShaderExpectAssumeCase` / `ShaderExpectAssumeTestInstance` test classes with full compute and graphics pipeline infrastructure.

## Source Code

- [vktShaderExpectAssumeTests.cpp](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1-L1522) (full file)
- Test instance class: [ShaderExpectAssumeTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L95-L1106)
- Test case class: [ShaderExpectAssumeCase](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1150)
- Registration function: [addShaderExpectAssumeTests()](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1420-L1512)
- Entry point: [createShaderExpectAssumeTests()](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1519)

## Registration Hierarchy

```text
glsl.shader_expect_assume
├── vertex
├── fragment
└── compute
```

Each stage group has 2 children: `expect`, `assume`

## Test Families

| Family | Class | Description |
|--------|-------|-------------|
| ShaderExpectAssumeCase | [ShaderExpectAssumeCase](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1150) | Test case that checks support and creates test instance |
| ShaderExpectAssumeTestInstance | [ShaderExpectAssumeTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L95-L1106) | Test instance that executes shader and validates results |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| OpType | Expect, Assume |
| DataClass | Constant, SpecializationConstant, PushConstant, StorageBuffer |
| DataType | Bool, Int8, Int16, Int32, Int64 |
| dataChannelCount | 1-4 (only for StorageBuffer + Expect combination) |
| ShaderStage | vertex, fragment, compute |
| wrongExpectation | true, false (only for StorageBuffer + Expect combination) |

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_shader_expect_assume | Always required |
| VK_KHR_16bit_storage | Required for Int16 data type |
| VK_KHR_shader_float16_int8 + VK_KHR_8bit_storage | Required for Int8 data type |
| shaderInt64 core feature | Required for Int64 data type |
| shaderInt16 core feature | Required for Int16 data type |
| shaderInt8 core feature | Required for Int8 data type |
| storageBuffer16BitAccess / uniformAndStorageBuffer16BitAccess | Required for Int16 data type |
| storageBuffer8BitAccess / uniformAndStorageBuffer8BitAccess | Required for Int8 data type |

## Verification Methods

1. Shader writes `(globalInvocationID.x, verification_result)` pairs to an output buffer
2. For `Expect`: the shader calls `OpExpectKHR` with a condition; if the expectation is violated and `wrongExpectation` is false, the result is `0`; if `wrongExpectation` is true, the result is `1`
3. For `Assume`: the shader calls `OpAssumeTrueKHR` with a condition; the result is `1` if the assumption holds
4. CPU validates each element in the output buffer: element at index `i` must equal `(i, 1)`; a value of `0` in the second component indicates a violated expectation/assumption
5. Uses `kNumElements = 32` elements per test

## Notes

- The `expect` sub-group includes additional test variants with `wrongExpectation=true` and vector widths (`_vec2`, `_vec3`, `_vec4`) that are only generated for the `StorageBuffer` data class with `OpType::Expect`
- The `assume` sub-group only tests with `wrongExpectation=false` and `dataChannelCount=1`
- Compute tests use dispatch; vertex/fragment tests use rendering with a color attachment of format `VK_FORMAT_R32G32_UINT`
- The output format uses `kColorAttachmentFormat = VK_FORMAT_R32G32_UINT` for graphics pipeline tests
