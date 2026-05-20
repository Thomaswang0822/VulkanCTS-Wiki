# vktShaderBuiltinTests.cpp

## Overview

Pure registration and aggregation file for Vulkan CTS built-in shader tests. This file does not contain any test implementation logic; it creates the top-level `"builtin"` test group and delegates to sub-files for precision, common function, integer function, packing function, and FConvert tests.

## Role

Pure registration/aggregation file. The `createBuiltinTests()` function constructs the `builtin` test group hierarchy by instantiating child groups from included headers. No test cases are implemented directly in this file.

## Source Code

- [vktShaderBuiltinTests.cpp](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L1-L63) (full file)
- Registration function: [createBuiltinTests()](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L60)

## Registration Hierarchy

```text
glsl.builtin
├── function
├── precision
├── precision_fp16_storage16b
├── precision_fp16_storage32b
├── precision_double
└── precision_fconvert
```

## Test Families

| Family | Source File | Description |
|--------|-----------|-------------|
| ShaderCommonFunctionTests | vktShaderCommonFunctionTests.cpp | Common built-in functions (abs, sign, clamp, mix, etc.) |
| ShaderIntegerFunctionTests | vktShaderIntegerFunctionTests.cpp | Integer built-in functions (uaddCarry, umulExtended, etc.) |
| ShaderPackingFunctionTests | vktShaderPackingFunctionTests.cpp | Pack/unpack functions (packHalf2x16, unpackSnorm4x8, etc.) |
| BuiltinPrecisionTests | vktShaderBuiltinPrecisionTests.cpp | Float32 precision and range tests for builtins |
| BuiltinPrecision16BitTests | vktShaderBuiltinPrecisionTests.cpp | Float16 precision tests (16-bit storage + 16-bit arithmetic) |
| BuiltinPrecision16Storage32BitTests | vktShaderBuiltinPrecisionTests.cpp | Float16 precision tests (32-bit storage + 16-bit arithmetic) |
| BuiltinPrecisionDoubleTests | vktShaderBuiltinPrecisionTests.cpp | Float64 precision and range tests for builtins |
| createPrecisionFconvertGroup | vktShaderFConvertTests.cpp | FConvert precision tests (type conversion between float widths) |

The `function` sub-group contains three children: `common`, `integer`, and `pack_unpack`.

## Parameter Dimensions

Varies by sub-file. Key dimensions include:
- Shader stage (vertex, fragment, geometry, tessellation control/evaluation, compute)
- Data type (float, vec2, vec3, vec4, int, ivec2, etc.)
- Precision qualifier (mediump, highp)
- Function type (specific built-in function under test)

## Support/Feature Requirements

Varies by sub-file. Key requirements include:
- `shaderFloat16` / `VK_KHR_shader_float16_int8` (for precision_fp16_storage16b, precision_fp16_storage32b)
- `storageBuffer16BitAccess` / `VK_KHR_16bit_storage` (for 16-bit storage)
- `shaderFloat64` (for precision_double)
- Core feature support varies per precision test group

## Verification Methods

Varies by sub-file. Key methods include:
- Precision threshold comparison: GPU output compared against reference computed at specified precision with ULP-based tolerance
- Exact value comparison: For integer and packing functions where results are deterministic

## Notes

- This file serves as the single entry point for all built-in shader tests under `dEQP-VK.glsl.builtin.*`
- The `function` sub-group is itself an aggregation of three TestCaseGroup subclasses: `common`, `integer`, `pack_unpack`
- The `precision` sub-group name `precision_fp16_storage16b` indicates 16-bit float precision with 16-bit storage; `precision_fp16_storage32b` indicates 16-bit float precision with 32-bit storage
