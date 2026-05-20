# vktShaderBFloat16Tests.cpp

## Overview

Pure registration and aggregation file for BFloat16 shader tests. This file creates the top-level `"bfloat16"` test group and delegates to three sub-files for dot product tests, specialization constant tests, and various composite/access chain/function call/swizzling operation tests.

## Role

Pure registration/aggregation file. The `createBFloat16Tests()` function constructs the `bfloat16` test group hierarchy by calling into three external factory functions from separate source files. No test cases are implemented directly in this file.

## Source Code

- [vktShaderBFloat16Tests.cpp](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L1-L215) (full file)
- Registration function: [createBFloat16Tests()](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L204-L212)

## Registration Hierarchy

```text
glsl.bfloat16
├── dot
├── constant
└── various
```

Sub-group children:
- `dot`: vec2, vec3, vec4
- `constant`: computebf16, vertexbf16, fragmentbf16, computefe5m2, vertexfe5m2, fragmentfe5m2, computefe4m3, vertexfe4m3, fragmentfe4m3
- `various`: composites, access_chains, function_call, swizzling

## Test Families

| Family | Source File | Description |
|--------|-----------|-------------|
| BFloat16OpDotCase | vktShaderBFloat16DotTests.cpp | BFloat16 dot product tests for vec2/vec3/vec4 |
| BFloat16ConstantCaseT | vktShaderBFloat16ConstantTests.cpp | BFloat16/FloatE5M2/FloatE4M3 specialization constant (constant_id) tests |
| BFloat16ComboCase | vktShaderBFloat16ComboTests.cpp | BFloat16 composite, access chain, function call, and swizzling operation tests |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Float type | BrainFloat16, FloatE5M2, FloatE4M3, Float16 |
| Shader stage | compute, vertex, fragment |
| Vector width | vec2, vec3, vec4 (for dot sub-group) |
| Operation type | composites, access_chains, function_call, swizzling (for various sub-group) |

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_shader_bfloat16 / shaderBFloat16Type | Always required |
| shaderBFloat16DotProduct | Required for dot sub-group tests |
| storageBuffer16BitAccess | Required for buffer access with 16-bit types |
| shaderFloat16 / VK_KHR_shader_float16_int8 | Required for Float16 type tests |
| shaderFloat8 / VK_EXT_shader_float8 | Required for FloatE5M2/FloatE4M3 type tests |

## Verification Methods

- **Dot**: CPU computes reference dot product using the same BFloat16 type, compares against GPU output
- **Constant**: `verifyResult()` compares GPU output buffer values against expected specialization constant values
- **Various**: `verifyResult()` with operation-specific validation for composites, access chains, function calls, and swizzling operations

## Notes

- The GLSL extension `GL_EXT_bfloat16` is used for BrainFloat16 types, `GL_EXT_shader_explicit_arithmetic_types_float16` for Float16 types
- Vector type names follow the pattern: `bfloat16_t`, `bf16vec2`, `bf16vec3`, `bf16vec4` for BrainFloat16; `float16_t`, `f16vec2`, `f16vec3`, `f16vec4` for Float16
- The `constant` sub-group tests specialization constants (`constant_id`) with three float formats (bf16, fe5m2, fe4m3) across three shader stages (compute, vertex, fragment), yielding 9 test cases
