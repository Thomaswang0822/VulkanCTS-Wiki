# vktSpvAsmFmaTests

## Overview

Functional tests for the `OpFmaKHR` instruction (`VK_KHR_shader_fma`), covering 16/32/64-bit floating-point groups, scalar/vec2/vec3/vec4 vector sizes, RTZ/RTE/undefined rounding modes, preserve/flush/undefined denorm modes, and random/directed/float-control input modes registered by [createOpFmaComputeGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1191-L1225).

## Role

Implementation file

## Source

- [vktSpvAsmFmaTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1191)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.opfma
├── fp16
├── fp32
└── fp64
```

## Test Families

### fp16 — Tests OpFmaKHR with 16-bit floats

Tests `OpFmaKHR` with `deFloat16` operands across scalar and vector sizes (1–4), with all registered rounding, denorm, and signed-zero/inf/NaN-preserve variants. The SPIR-V generator emits `FMAKHR` and `SPV_KHR_fma`, and the test spec requests `shaderFmaFloat16` plus `shaderFloat16` for 16-bit cases ([getFmaCode()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L134-L140), [createFmaTestSpec()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L983-L990)).

### fp32 — Tests OpFmaKHR with 32-bit floats

Tests `OpFmaKHR` with `float` operands across scalar and vector sizes (1–4), with all registered rounding, denorm, and signed-zero/inf/NaN-preserve variants; 32-bit cases request `shaderFmaFloat32` ([createFmaTestSpec()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L983-L992)).

### fp64 — Tests OpFmaKHR with 64-bit floats

Tests `OpFmaKHR` with `double` operands across scalar and vector sizes (1–4), with all registered rounding, denorm, and signed-zero/inf/NaN-preserve variants; 64-bit cases request `shaderFmaFloat64` and `shaderFloat64` ([createFmaTestSpec()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L983-L990)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Bit depth | 16, 32, 64 | Floating-point bit width (groups: fp16, fp32, fp64) |
| Vector size | 1 (scalar), 2 (vec2), 3 (vec3), 4 (vec4) | Component count of operands |
| Rounding mode | `rtz`, `rte`, `undef` | RoundingModeRTZ, RoundingModeRTE, or undefined |
| Denorm mode | `denorm_preserve`, `denorm_flush`, `undef` | DenormPreserve, DenormFlushToZero, or undefined |
| Input mode | `random`, `directed`, `float_controls` | Random inputs, directed special-value inputs, or directed with SignedZeroInfNanPreserve |

## Support Requirements

- `VK_KHR_shader_fma` / FMA feature coverage is reflected by the file comment and per-bit-depth `shaderFmaFloat16`, `shaderFmaFloat32`, and `shaderFmaFloat64` feature requests ([file comment](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L41), [createFmaTestSpec()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L983-L985))
- `SPV_KHR_fma` SPIR-V extension ([getFmaCode()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L134-L136))
- `SPV_KHR_float_controls` when rounding, denorm, or signed-zero/inf/NaN-preserve modes are specified ([getFmaCode()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L138-L140))
- `shaderFloat16` for 16-bit cases and `shaderFloat64` for 64-bit cases ([createFmaTestSpec()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L987-L990))
- Corresponding float-control properties for each bit depth and mode combination ([FillFloatControlsProps()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L939-L972))

## Verification Methods

Custom [`verifyResult<T>()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L505-L570) template function that:
1. Computes reference FMA values with the specified rounding mode via the reference-value path ([getRefValues()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L368-L489))
2. Accounts for denorm flushing by generating all valid input combinations when denorms may be flushed ([getFlushCombinations()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L368-L382))
3. Handles underflow detection by comparing results from different rounding directions ([getRefValues()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L433-L471))
4. Allows both flushed and non-flushed denorm results when denorm behavior is undefined ([getFlushCombinations()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L368-L382))
5. Skips inf/nan checks when `SignedZeroInfNanPreserve` is not enabled ([verifyResult()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L524-L531))
6. Reports up to 16 mismatches with hexfloat formatting ([verifyResult()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L521-L564))

## Notes

- The test hierarchy is registered as `fp{16,32,64}` → `{scalar,vec2,vec3,vec4}` → `{rtz,rte,undef}` → `{denorm_preserve,denorm_flush,undef}` → `{random,directed,float_controls}` ([createOpFmaComputeGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1195-L1225))
- Directed tests include cancellation cases of the form `a * b - (a*b)` to exercise true FMA behavior ([DirectedBuffer::getBytes()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L796-L804))
- Non-VulkanSC only (compute only)
