# vktSpvAsmFloatControlsTests

## Overview

Tests for the `VK_KHR_shader_float_controls` extension, verifying SPIR-V execution modes controlling floating-point behavior (denorm preservation/flush-to-zero, signed zero/inf/NaN preservation, rounding modes RTE/RTZ) across FP16, FP32, and FP64 types. The group registers FP16/FP32/FP64 operation subgroups with `input_args` and `generated_args` children, then adds compute-only independence settings tests ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383-L5408), [ComputeTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4140)). Graphics cases are registered for vertex and fragment stages by the graphics context builder ([createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5371-L5374)).

## Role

Implementation file

## Source

- [vktSpvAsmFloatControlsTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383)

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

Tests floating-point control behaviors for 16-bit float type. Includes both `input_args` (arguments read from input SSBO) and `generated_args` (arguments generated as SPIR-V constants) sub-groups. Covers denorm preserve/flush, signed zero/inf/NaN preserve, and rounding mode behaviors for FP16 operations. Created via `groupBuilder->createOperationTests(typeGroup, "input_args", FP16, true)` and `groupBuilder->createOperationTests(typeGroup, "generated_args", FP16, false)` ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5392-L5404)).

### fp32 — FP32 float control tests

Tests floating-point control behaviors for 32-bit float type. Same structure as fp16 with `input_args` and `generated_args` sub-groups. Created in the same `testGroups` loop ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5392-L5404)).

### fp64 — FP64 float control tests

Tests floating-point control behaviors for 64-bit float type. Same structure as fp16 with `input_args` and `generated_args` sub-groups. Created in the same `testGroups` loop ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5392-L5404)).

### independence_settings — Float control independence settings tests (compute only)

Tests that different float widths can have independent control settings (rounding modes and denorm behaviors). Verifies `VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_32_BIT_ONLY` vs `VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_ALL` independence settings. Includes tests for rounding combinations, denorm preserve/flush combinations, and variants with/without VK_KHR_16bit_storage. Created by [ComputeTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4140). Not present in graphics group; the graphics builder leaves settings registration empty because the source comment says compute-only testing is sufficient ([GraphicsTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4973-L4978)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| VariableType | `FP16`, `FP32`, `FP64` | Float width groups registered by `testGroups` ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5387-L5396)) |
| Argument source | `input_args` (from SSBO), `generated_args` (SPIR-V constants) | Child groups passed to `createOperationTests()` ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5400-L5404)) |
| BehaviorFlags | `B_DENORM_PRESERVE`, `B_DENORM_FLUSH`, `B_ZIN_PRESERVE`, `B_RTE_ROUNDING`, `B_RTZ_ROUNDING` | Float-control behavior flags ([BehaviorFlags](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L110-L117)) |
| OperationId | many operation IDs | SPIR-V and GLSL operations built from `OperationId` and the operation map ([OperationId](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L280-L404), [createOperationMap()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650)) |
| FloatUsage | `FLOAT_STORAGE_ONLY`, `FLOAT_ARITHMETIC` | Whether FP16 use goes beyond storage ([FloatUsage](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L74-L80)) |
| Shader Stage | compute / vertex / fragment | Pipeline stage under test |
| SettingsMode | `SM_ROUNDING`, `SM_DENORMS` | Independence settings modes ([SettingsMode](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3610-L3612)) |
| Independence | `32_BIT_ONLY`, `ALL` | Independence values used by settings tests ([ComputeTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4136-L4138)) |

## Support Requirements

- **`VK_KHR_shader_float_controls`** extension (conditionally requested in [createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5362-L5364) and always requested for mixed-settings tests in [fillSettingsTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4686-L4690))
- **`VK_KHR_16bit_storage`** extension for the FP16 storage path in settings tests ([fillSettingsTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4650-L4665))
- **`VK_KHR_shader_float16_int8`** extension for the FP16-without-16-bit-storage path in settings tests ([fillSettingsTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4641-L4646))
- **`shaderFloat64`** core feature for FP64 tests ([createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5351-L5358))
- **`shaderInt64`** core feature for int64 conversion tests ([createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5351-L5358))
- **`shaderFloat16`** feature for FP16 arithmetic tests ([createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5351-L5358))
- **`fragmentStoresAndAtomics`** for graphics tests ([createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5351-L5356))
- SPIR-V extension: `SPV_KHR_float_controls`
- Various `VkPhysicalDeviceFloatControlsProperties` properties queried at runtime

## Verification Methods

- **Compute verification**: `checkFloats<FloatType, UintType>` compares output buffer values against expected `ValueId`-encoded results, including NaN, denorm, and multiple-acceptable-result handling ([checkValue()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3440-L3524), [checkFloats()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3532-L3550))
- **Graphics verification**: Uses `runAndVerifyDefaultPipeline` for rendered output and `checkFloatsLUT[]` dispatches type-specific comparisons ([GraphicsTestGroupBuilder::createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4968-L4984))
- **Settings tests**: `checkMixedFloats` verifies multiple float-width results in a single shader invocation ([fillSettingsTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4683-L4689))
- The `ValueId` system encodes expected results as typed values in output buffers, then decodes them during verification ([ValueId](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L121-L189), [TypeValues::constructOutputBuffer()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L518-L532), [checkValue()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3440-L3524))

## Notes

- The `OperationId` enum and operation map define SPIR-V operations, GLSL extended instructions, and conversion operations ([OperationId](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L280-L404), [createOperationMap()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650))
- The `input_args` vs `generated_args` distinction is the boolean argument to `createOperationTests()` and affects input-buffer construction versus generated constants in operation-test creation ([createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5400-L5404), [ComputeTestGroupBuilder::createOperationTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3749-L3760))
- The `independence_settings` group is compute-only; the graphics builder's `createSettingsTests` is a no-op ([GraphicsTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4973-L4978))
- FP16 tests have a `fp16Without16BitStorage` variant that appends `_nostorage` to the name and uses the `VK_KHR_shader_float16_int8` feature path instead of 16-bit storage ([OperationTestCase](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2055-L2064), [fillSettingsTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4627-L4665))
