# vktSpvAsmFloatControls2Tests

## Overview

Tests for the VK_KHR_shader_float_controls2 extension (non-VulkanSC only), verifying that SPIR-V FPFastMathMode decorations on operations correctly control floating-point behavior. Tests FP16, FP32, and FP64 types with various fast-math mode combinations (NotNaN, NotInf, NSZ, AllowRecip, AllowContract, AllowReassoc, AllowTransform). Covers a range of SPIR-V and GLSL operations. Tests run in both compute and graphics (vertex + fragment) pipeline stages.

## Role

Implementation file

## Source

- [vktSpvAsmFloatControls2Tests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.float_controls2 (non-VulkanSC only)
├── fp16
│   └── input_args
├── fp32
│   └── input_args
└── fp64
    └── input_args

spirv_assembly.instruction.graphics.float_controls2 (non-VulkanSC only)
├── fp16
│   └── input_args
├── fp32
│   └── input_args
└── fp64
    └── input_args
```

## Test Families

### fp16 — FP16 float controls2 tests

Tests FPFastMathMode decorations for 16-bit float operations. Only `input_args` sub-group (arguments read from input SSBO). Covers fast-math mode combinations applied to FP16 SPIR-V and GLSL operations. Created via `groupBuilder->createOperationTests(typeGroup, "input_args", FP16, true)` at vktSpvAsmFloatControls2Tests.cpp#L3355.

### fp32 — FP32 float controls2 tests

Tests FPFastMathMode decorations for 32-bit float operations. Same structure as fp16. Created at vktSpvAsmFloatControls2Tests.cpp#L3355.

### fp64 — FP64 float controls2 tests

Tests FPFastMathMode decorations for 64-bit float operations. Same structure as fp16. Created at vktSpvAsmFloatControls2Tests.cpp#L3355.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| FloatType | `FP16`, `FP32`, `FP64` | Float width under test |
| Argument source | `input_args` only | Arguments read from input SSBO |
| FPFastMathMode flags | `NotNaN`, `NotInf`, `NSZ`, `AllowRecip`, `AllowContract`, `AllowReassoc`, `AllowTransform` | Fast-math mode bits tested individually and in combination |
| OperationId | ~70+ operations | SPIR-V and GLSL operations tested |
| FloatUsage | `FLOAT_STORAGE_ONLY`, `FLOAT_ARITHMETIC` | Whether FP16 use goes beyond storage |
| Shader Stage | compute / vertex+fragment | Pipeline stage under test |

## Support Requirements

- **VK_KHR_shader_float_controls2** extension (SPIR-V extension `SPV_KHR_float_controls2`, observed in shader templates at vktSpvAsmFloatControls2Tests.cpp#L2401 and vktSpvAsmFloatControls2Tests.cpp#L2785)
- **VK_KHR_16bit_storage** extension (for FP16 with storage)
- **VK_KHR_shader_float16_int8** extension (for FP16 without 16-bit storage)
- **shaderFloat64** core feature for FP64 tests
- **shaderFloat16** feature for FP16 arithmetic tests
- **fragmentStoresAndAtomics** for graphics tests
- SPIR-V version 1.2 required (observed in vktSpvAsmFloatControls2Tests.cpp#L3326)
- Non-VulkanSC only (per task description)

## Verification Methods

- **Compute verification**: `checkFloats<FloatType, UintType>` template compares output buffer values against expected ValueId-encoded results
- **Graphics verification**: Uses `runAndVerifyDefaultPipeline` with `checkFloatsLUT[]` dispatching to type-specific comparison (vktSpvAsmFloatControls2Tests.cpp#L2937-L2938)
- ValueId system encodes expected results as integer tags in the output buffer, decoded and compared against CPU-computed reference values
- Special value handling for NaN, denorms, and fast-math relaxed results (e.g., `V_ONE_OR_NAN`, `V_SIGN_NAN`, `V_ZERO_OR_MINUS_ZERO`)

## Notes

- Unlike FloatControls (v1), this file only uses `input_args` (no `generated_args` sub-group) and has no `independence_settings` group
- The `behaviorToName` map at vktSpvAsmFloatControls2Tests.cpp#L110-L117 maps `spv::FPFastMathModeMask` values to test name strings
- The `allBits` constant at vktSpvAsmFloatControls2Tests.cpp#L119-L120 defines the full set of testable fast-math mode bits
- `AllowTransform` requires `AllowReassoc` and `AllowContract` to also be set (observed in `invert()` at vktSpvAsmFloatControls2Tests.cpp#L122-L129)
- The OperationId enum includes additional operations not in FloatControls v1: `OID_FMA2PT58`, `OID_SZ_FMA`, `OID_LDEXP`, `OID_FREXP`, `OID_FREXP_ST`, `OID_ADD_SUB_REASSOCIABLE`
