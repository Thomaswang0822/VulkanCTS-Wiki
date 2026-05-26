# vktSpvAsmFloatControls2Tests

## Overview

Tests for the `VK_KHR_shader_float_controls2` extension (non-VulkanSC only), verifying that SPIR-V [`FPFastMathMode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2329-L2331) decorations on operations control floating-point behavior. Tests FP16, FP32, and FP64 groups registered by [`createFloatControls2TestGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3333-L3356) with fast-math mode flags such as `NotNaN`, `NotInf`, `NSZ`, `AllowRecip`, `AllowContract`, `AllowReassoc`, and `AllowTransform`. Covers SPIR-V and GLSL.std.450 operations in both compute and graphics (vertex + fragment) pipeline stages.

## Role

Implementation file

## Source

- [vktSpvAsmFloatControls2Tests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3333)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.float_controls2
├── fp16
├── fp32
└── fp64

spirv_assembly.instruction.graphics.float_controls2
├── fp16
├── fp32
└── fp64
```

## Test Families

### fp16 — FP16 float controls2 tests

Tests `FPFastMathMode` decorations for 16-bit float operations. The registered FP16 group contains an `input_args` sub-group created by [`groupBuilder->createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3343-L3355). Generated operation tests are built by the compute and graphics builders in [`createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2470-L2495) and [`GraphicsTestGroupBuilder::createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2901-L2930).

### fp32 — FP32 float controls2 tests

Tests `FPFastMathMode` decorations for 32-bit float operations. Same registration structure as `fp16`, with the `FP32` entry listed in the shared [`testGroups`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3338-L3347) table.

### fp64 — FP64 float controls2 tests

Tests `FPFastMathMode` decorations for 64-bit float operations. Same registration structure as `fp16`, with the `FP64` entry listed in the shared [`testGroups`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3338-L3347) table and the shaderFloat64 feature requested when needed in compute and graphics resource setup.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| FloatType | `FP16`, `FP32`, `FP64` | Float width under test, registered in [`testGroups`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3338-L3347) |
| Argument source | `input_args` only | Arguments read from input SSBO; created at [`groupBuilder->createOperationTests(typeGroup, "input_args", ...)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3355) |
| FPFastMathMode flags | `NotNaN`, `NotInf`, `NSZ`, `AllowRecip`, `AllowContract`, `AllowReassoc`, `AllowTransform` | Fast-math mode bits from [`behaviorToName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L109-L120) |
| OperationId | Operation enum entries and builder-generated cases | SPIR-V and GLSL operations from [`OperationId`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L256-L364) and [`TestCasesBuilder`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L1559-L1560) |
| FloatUsage | `FLOAT_STORAGE_ONLY`, `FLOAT_ARITHMETIC` | Operation usage classification used by operation metadata, for example [`add_sub_reassociable`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L1655-L1657) |
| Shader Stage | compute / vertex+fragment | Compute uses `VK_SHADER_STAGE_COMPUTE_BIT` in [`ComputeTestGroupBuilder::createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2486-L2487); graphics iterates vertex and fragment stages in [`GraphicsTestGroupBuilder::createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2918-L2929) |

## Support Requirements

- **VK_KHR_shader_float_controls2** / SPIR-V extension `SPV_KHR_float_controls2` — observed in the compute shader template at [`OpExtension "SPV_KHR_float_controls2"`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2396-L2402) and in graphics resource features at [`vulkanFeatures.extFloatControls2.shaderFloatControls2`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3300-L3304).
- **VK_KHR_16bit_storage** / **VK_KHR_shader_float16_int8** related features — requested for FP16 storage/arithmetic through compute feature setup at [`csSpec.requestedVulkanFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2656-L2663) and graphics feature setup at [`vulkanFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3300-L3305).
- **shaderFloat64** core feature — requested for FP64 paths in compute at [`csSpec.requestedVulkanFeatures.coreFeatures.shaderFloat64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2656-L2658) and graphics at [`vulkanFeatures.coreFeatures.shaderFloat64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3300-L3302).
- **fragmentStoresAndAtomics** — required for graphics tests via [`vulkanFeatures.coreFeatures.fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3300-L3303).
- SPIR-V version 1.2 is requested for compute at [`csSpec.spirvVersion`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2652-L2656) and for graphics at [`ctx.resources.spirvVersion`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3325-L3326).
- Non-VulkanSC only, as these groups are conditionally registered by the instruction dispatcher under `#ifndef CTS_USES_VULKANSC` for compute and graphics.

## Verification Methods

- **Compute verification**: The [`checkFloats()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2169-L2186) template compares output buffer values against expected ValueId-encoded results through `compareBytes`, and compute test cases select it through [`checkFloatsLUT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2498-L2502) and [`csSpec.verifyIO`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2648-L2655).
- **Graphics verification**: Uses `runAndVerifyDefaultPipeline` when adding graphics cases in [`GraphicsTestGroupBuilder::createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2925-L2929), with `checkFloatsLUT[]` dispatching to type-specific comparison in [`createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2934-L2938) and [`resources.verifyIO`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3288-L3294).
- ValueId-based expected results are generated into operation test cases and skipped when undefined in compute and graphics loops at [`expectedOutput == V_UNUSED`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2480-L2484) and [`expectedOutput == V_UNUSED`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2912-L2916).
- Special value handling for NaN, denorms, and fast-math relaxed results is encoded in generated `ValueId` expectations, including entries such as `V_ONE_OR_NAN`, `V_SIGN_NAN`, and `V_ZERO_OR_MINUS_ZERO` in the inspected operation case tables.

## Notes

- Unlike FloatControls (v1), this file only registers `input_args` and does not add a `generated_args` sub-group, as shown by the single [`createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3355) call per float type.
- The [`behaviorToName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L109-L117) map converts `spv::FPFastMathModeMask` values to test name strings.
- The [`allBits`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L119-L120) constant defines the full set of testable fast-math mode bits.
- `AllowTransform` requires `AllowReassoc` and `AllowContract` to also be set, as enforced by [`invert()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L122-L128).
- The [`OperationId`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L256-L364) enum includes operations such as `OID_FMA2PT58`, `OID_SZ_FMA`, `OID_LDEXP`, `OID_FREXP`, `OID_FREXP_ST`, and `OID_ADD_SUB_REASSOCIABLE`.
