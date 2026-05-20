# vktSpvAsmFloatControlsExtensionlessTests

## Overview

Tests that SPIR-V float control execution modes (DenormPreserve, DenormFlushToZero, SignedZeroInfNanPreserve, RoundingModeRTE, RoundingModeRTZ) can be used without requiring the VK_KHR_shader_float_controls extension. Verifies that these capabilities work correctly when enabled through SPIR-V 1.4 (via VK_KHR_spirv_1_4) or Vulkan 1.2. Tests run in compute pipeline only.

## Role

Implementation file

## Source

- [vktSpvAsmFloatControlsExtensionlessTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.float_controls_extensionless
├── spirv1p4
└── vulkan1_2
```

## Test Families

### spirv1p4 — SPIR-V 1.4 float controls tests

Tests float control execution modes enabled through SPIR-V 1.4 (requiring VK_KHR_spirv_1_4). Contains 15 test cases covering all 5 execution modes × 3 float widths. Test names follow the pattern `fp{width}_{featureName}`. Created at vktSpvAsmFloatControlsExtensionlessTests.cpp#L258-L276.

### vulkan1_2 — Vulkan 1.2 float controls tests

Tests float control execution modes enabled through Vulkan 1.2 (without VK_KHR_spirv_1_4). Contains the same 15 test cases as spirv1p4. Created at vktSpvAsmFloatControlsExtensionlessTests.cpp#L258-L276.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| SPIR-V version | `spirv1p4`, `vulkan1_2` | How float controls are enabled (VK_KHR_spirv_1_4 vs Vulkan 1.2) |
| Float width | 16, 32, 64 | Bit width of the float type |
| Execution mode | `denorm_preserve`, `denorm_flush_to_zero`, `signed_zero_inf_nan_preserve`, `rounding_mode_rte`, `rounding_mode_rtz` | Float control feature being tested |

## Support Requirements

- **VK_KHR_spirv_1_4** extension (for spirv1p4 group, checked at vktSpvAsmFloatControlsExtensionlessTests.cpp#L209-L211)
- **Vulkan 1.2** (for vulkan1_2 group, checked at vktSpvAsmFloatControlsExtensionlessTests.cpp#L214-L216)
- **VK_KHR_shader_float16_int8** extension with `shaderFloat16` feature (for fp16 tests, checked at vktSpvAsmFloatControlsExtensionlessTests.cpp#L218-L223)
- **shaderFloat64** core feature (for fp64 tests, checked at vktSpvAsmFloatControlsExtensionlessTests.cpp#L226-L229)
- Corresponding `VkPhysicalDeviceFloatControlsProperties` property must be true for each tested feature/width combination (checked via `getFloatControlsProperty` at vktSpvAsmFloatControlsExtensionlessTests.cpp#L231-L232)
- SPIR-V version 1.4 build options (vktSpvAsmFloatControlsExtensionlessTests.cpp#L203)

## Verification Methods

- **Compute IO verification**: Uses `verifyOutput` from `SpvAsmComputeShaderInstance` which compares output buffer against expected output buffer byte-by-byte
- The shader performs `OpFNegate` on random float inputs; expected outputs are simply the negated inputs (vktSpvAsmFloatControlsExtensionlessTests.cpp#L96-L100)
- 64 random float elements per test (range 1.0 to 100.0), seeded by test name hash (vktSpvAsmFloatControlsExtensionlessTests.cpp#L88-L97)

## Notes

- This file tests that float control capabilities work without the VK_KHR_shader_float_controls extension, using only SPIR-V 1.4 or Vulkan 1.2
- The shader is minimal: it only performs `OpFNegate` on input data, serving as a smoke test that the execution mode is accepted and the shader compiles/runs correctly
- The `SpvAsmFloatControlsExtensionlessCase` class handles both `initPrograms` (generating SPIR-V assembly) and `checkSupport` (verifying device capabilities) at vktSpvAsmFloatControlsExtensionlessTests.cpp#L185-L233
- Compute-only tests (no graphics pipeline variant)
