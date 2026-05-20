# vktSpvAsmFloatControlsTests

## Overview

Tests for the VK_KHR_shader_float_controls extension, verifying that SPIR-V execution modes controlling floating-point behavior (denorm preservation/flush-to-zero, signed zero/inf/NaN preservation, rounding modes RTE/RTZ) work correctly across FP16, FP32, and FP64 types. Covers a wide range of SPIR-V and GLSL operations, conversion operations with rounding, and settings independence tests. Tests run in both compute and graphics (vertex + fragment) pipeline stages.

## Role

Implementation file

## Source

- [vktSpvAsmFloatControlsTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.float_controls
├── fp16
├── fp32
├── fp64
└── independence_settings

spirv_assembly.instruction.graphics.float_controls
├── fp16
├── fp32
└── fp64
```

## Test Families

### fp16 — FP16 float control tests

Tests floating-point control behaviors for 16-bit float type. Includes both `input_args` (arguments read from input SSBO) and `generated_args` (arguments generated as SPIR-V constants) sub-groups. Covers denorm preserve/flush, signed zero/inf/NaN preserve, and rounding mode behaviors for FP16 operations. Created via `groupBuilder->createOperationTests(typeGroup, "input_args", FP16, true)` and `groupBuilder->createOperationTests(typeGroup, "generated_args", FP16, false)` at vktSpvAsmFloatControlsTests.cpp#L5403-L5404.

### fp32 — FP32 float control tests

Tests floating-point control behaviors for 32-bit float type. Same structure as fp16 with `input_args` and `generated_args` sub-groups. Created at vktSpvAsmFloatControlsTests.cpp#L5403-L5404.

### fp64 — FP64 float control tests

Tests floating-point control behaviors for 64-bit float type. Same structure as fp16 with `input_args` and `generated_args` sub-groups. Created at vktSpvAsmFloatControlsTests.cpp#L5403-L5404.

### independence_settings — Float control independence settings tests (compute only)

Tests that different float widths can have independent control settings (rounding modes and denorm behaviors). Verifies `VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_32_BIT_ONLY` vs `VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_ALL` independence settings. Includes tests for rounding combinations, denorm preserve/flush combinations, and variants with/without VK_KHR_16bit_storage. Created by `ComputeTestGroupBuilder::createSettingsTests` at vktSpvAsmFloatControlsTests.cpp#L4130. Not present in graphics group (WG decided compute-only testing is sufficient, per vktSpvAsmFloatControlsTests.cpp#L4973-L4978).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| VariableType | `FP16`, `FP32`, `FP64` | Float width under test |
| Argument source | `input_args` (from SSBO), `generated_args` (SPIR-V constants) | How operation arguments are provided |
| BehaviorFlags | `B_DENORM_PRESERVE`, `B_DENORM_FLUSH`, `B_ZIN_PRESERVE`, `B_RTE_ROUNDING`, `B_RTZ_ROUNDING` | Float control behavior being tested |
| OperationId | ~100+ operations | SPIR-V and GLSL operations tested (unary, binary, conversion, trigonometric, etc.) |
| FloatUsage | `FLOAT_STORAGE_ONLY`, `FLOAT_ARITHMETIC` | Whether FP16 use goes beyond storage |
| Shader Stage | compute / vertex / fragment | Pipeline stage under test |
| SettingsMode | `SM_ROUNDING`, `SM_DENORMS` | Independence settings test mode |
| Independence | `32_BIT_ONLY`, `ALL` | Float controls independence level |

## Support Requirements

- **VK_KHR_shader_float_controls** extension (conditionally required, observed in vktSpvAsmFloatControlsTests.cpp#L5363-L5364)
- **VK_KHR_16bit_storage** extension (for FP16 with storage, observed in vktSpvAsmFloatControlsTests.cpp#L4664)
- **VK_KHR_shader_float16_int8** extension (for FP16 without 16-bit storage, observed in vktSpvAsmFloatControlsTests.cpp#L4645)
- **shaderFloat64** core feature for FP64 tests (vktSpvAsmFloatControlsTests.cpp#L5356)
- **shaderInt64** core feature for int64 conversion tests (vktSpvAsmFloatControlsTests.cpp#L5357)
- **shaderFloat16** feature for FP16 arithmetic tests (vktSpvAsmFloatControlsTests.cpp#L5358)
- **fragmentStoresAndAtomics** for graphics tests (vktSpvAsmFloatControlsTests.cpp#L5355)
- SPIR-V extension: `SPV_KHR_float_controls`
- Various `VkPhysicalDeviceFloatControlsProperties` properties queried at runtime

## Verification Methods

- **Compute verification**: `checkFloats<FloatType, UintType>` template compares output buffer values against expected ValueId-encoded results, handling NaN and denorm special cases
- **Graphics verification**: Uses `runAndVerifyDefaultPipeline` which renders and compares output; `checkFloatsLUT[]` dispatches to type-specific comparison (vktSpvAsmFloatControlsTests.cpp#L4983-L4984)
- **Settings tests**: `checkMixedFloats` verifies multiple float-width results in a single shader invocation (vktSpvAsmFloatControlsTests.cpp#L4688)
- ValueId system encodes expected results as integer tags in the output buffer, which are decoded and compared against CPU-computed reference values

## Notes

- The OperationId enum defines ~100+ operations including SPIR-V unary (Negate, Composite, Copy, etc.), SPIR-V binary (Add, Sub, Mul, Div, etc.), GLSL unary (Round, Sin, Cos, Sqrt, etc.), GLSL binary (Atan2, Pow, Fma, etc.), and conversion operations
- The `input_args` vs `generated_args` distinction tests whether the float control mode affects values read from buffers vs values computed from SPIR-V constants
- The `independence_settings` group is compute-only; the graphics builder's `createSettingsTests` is a no-op (vktSpvAsmFloatControlsTests.cpp#L4973-L4978)
- FP16 tests have a `fp16Without16BitStorage` variant that uses `VK_KHR_shader_float16_int8` instead of `VK_KHR_16bit_storage`
