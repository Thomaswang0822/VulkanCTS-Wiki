# vktSpvAsmFmaTests

## Overview

Functional tests for the `OpFmaKHR` instruction (VK_KHR_shader_fma), covering multiple floating-point bit depths, vector sizes, rounding modes, denorm modes, and signed-zero/inf/nan preservation settings.

## Role

Implementation file

## Source

- [vktSpvAsmFmaTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.opfma
├── fp16
├── fp32
└── fp64
```

## Test Families

### fp16 — Tests OpFmaKHR with 16-bit floats

Tests `OpFmaKHR` with `deFloat16` operands across scalar and vector sizes (1–4), with all rounding/denorm/signed-zero combinations. Uses `FMAKHR` and `Float16` SPIR-V capabilities.

### fp32 — Tests OpFmaKHR with 32-bit floats

Tests `OpFmaKHR` with `float` operands across scalar and vector sizes (1–4), with all rounding/denorm/signed-zero combinations.

### fp64 — Tests OpFmaKHR with 64-bit floats

Tests `OpFmaKHR` with `double` operands across scalar and vector sizes (1–4), with all rounding/denorm/signed-zero combinations. Requires `shaderFloat64` feature.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Bit depth | 16, 32, 64 | Floating-point bit width (groups: fp16, fp32, fp64) |
| Vector size | 1 (scalar), 2 (vec2), 3 (vec3), 4 (vec4) | Component count of operands |
| Rounding mode | `rtz`, `rte`, `undef` | RoundingModeRTZ, RoundingModeRTE, or undefined |
| Denorm mode | `denorm_preserve`, `denorm_flush`, `undef` | DenormPreserve, DenormFlushToZero, or undefined |
| Input mode | `random`, `directed`, `float_controls` | Random inputs, directed special-value inputs, or directed with SignedZeroInfNanPreserve |

## Support Requirements

- `VK_KHR_shader_fma` extension / `shaderFmaFloat16`, `shaderFmaFloat32`, `shaderFmaFloat64` features
- `SPV_KHR_fma` SPIR-V extension
- `SPV_KHR_float_controls` when rounding/denorm/signed-zero modes are specified
- `shaderFloat16` for 16-bit, `shaderFloat64` for 64-bit
- Corresponding float control properties for each bit depth and mode combination

## Verification Methods

Custom `verifyResult<T>` template function (`vktSpvAsmFmaTests.cpp#L505-L570`) that:
1. Computes reference FMA values using CPU `std::fma` with the specified rounding mode
2. Accounts for denorm flushing by generating all valid input combinations when denorms may be flushed
3. Handles underflow detection by comparing results from different rounding directions
4. Allows both flushed and non-flushed denorm results when denorm behavior is undefined
5. Skips inf/nan checks when `SignedZeroInfNanPreserve` is not enabled
6. Reports up to 16 mismatches with hexfloat formatting

## Notes

- The test hierarchy is: `fp{16,32,64}` → `{scalar,vec2,vec3,vec4}` → `{rtz,rte,undef}` → `{denorm_preserve,denorm_flush,undef}` → `{random,directed,float_controls}`
- Directed tests include cancellation cases of the form `a * b - (a*b)` which should return non-zero results with true FMA
- Non-VulkanSC only (compute only)
