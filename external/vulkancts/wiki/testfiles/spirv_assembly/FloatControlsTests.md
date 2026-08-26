## Overview

**Core question:** does the implementation honor the `VK_KHR_shader_float_controls` execution modes (denorm preserve/flush, signed zero/inf/NaN preservation, and RTE/RTZ rounding) across FP16, FP32, and FP64 operations, and can different float widths be controlled independently within one shader?

- Source file: [`vktSpvAsmFloatControlsTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp). It builds SPIR-V assembly text directly from C++ string templates and registers operation tests, independence settings tests, and graphics pipeline tests under `spirv_assembly.instruction.compute.float_controls` and `spirv_assembly.instruction.graphics.float_controls`.
- The file groups structurally different behaviors under one implementation: per-width operation tests (`fp16`/`fp32`/`fp64`), cross-width independence settings tests (`independence_settings`, compute-only), and the same operation tests run through vertex/fragment pipelines (graphics `fp16`/`fp32`/`fp64`).
- The test does not compare against a host-computed reference float. Every argument and expected result is encoded as a `ValueId` enum token, and the host compares bit patterns with special-case handling for NaN, denorm, and multi-acceptable-result codes.
- The page covers the registration tree, the parameter matrix, the per-family behavior, two representative extracted SPIR-V walkthroughs (one operation test, one settings test), the runtime flow, failure meaning, and the per-width/per-mode pruning gates.

## Background Knowledge

- **SPIR-V float-control execution modes.** `VK_KHR_shader_float_controls` exposes SPIR-V execution modes that let a shader module dictate floating-point behavior the implementation must obey, instead of leaving it implementation-defined. The modes tested here are: `DenormPreserve` / `DenormFlushToZero` (whether subnormals are kept or flushed), `SignedZeroInfNanPreserve` (whether signs of zero, infinities, and NaN payloads are preserved), and `RoundingModeRTE` / `RoundingModeRTZ` (round-to-nearest-even versus round-toward-zero). Each mode is parameterized by a bit width (16, 32, or 64) and declared per entry point: `OpExecutionMode %main DenormPreserve 32`. The matching `OpCapability` must also be present.
- **Float-controls independence.** `VkPhysicalDeviceFloatControlsProperties` advertises which modes are supported per width and whether modes for different widths can be set independently (`VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_ALL`, `INDEPENDENCE_32_BIT_ONLY`, or `NONE`). The independence settings tests probe whether different widths can actually sustain different modes in one shader when the advertised independence level claims they can.
- **`ValueId` encoding.** Arguments and expected results are encoded as enum tokens (e.g. `V_DENORM`, `V_NAN`, `V_ZERO_OR_DENORM_TIMES_TWO`) rather than concrete floats. The host translates `ValueId`s into the bit pattern for the active width when filling buffers, and the verifier decodes the expected `ValueId` from the output buffer and compares bit patterns. A single token like `V_ZERO_OR_DENORM_TIMES_TWO` expresses "either zero (if the implementation flushed) or twice the denorm (if it preserved)" so one case validates both behaviors when only one is legal.

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

The three compute operation families (`fp16`/`fp32`/`fp64`) and the graphics operation families are registered by [`createFloatControlsTestGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383-L5410). Each operation family has `input_args` and `generated_args` children created by [`ComputeTestGroupBuilder::createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4102-L4128) (compute) and the graphics equivalent in [`GraphicsTestGroupBuilder::createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5371-L5374). The `independence_settings` family is compute-only; [`GraphicsTestGroupBuilder::createSettingsTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4973-L4978) is intentionally empty because the working group decided compute-only testing is sufficient for independence.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| VariableType | `FP16`, `FP32`, `FP64` | Float width under test. Selects per-width `TypeSnippets` (capability, array stride, type definitions, load/store snippets) and the per-width feature/property gates. | [`testGroups` loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5387-L5396) |
| Argument source | `input_args`, `generated_args` | `input_args` reads operands from the input SSBO; `generated_args` constructs operands as SPIR-V constants. For `input_args` `DenormPreserve` cases whose operations Vulkan already guarantees preserve denorms, the float-controls extension is not requested; generated-argument cases still request it. | [`isFloatControlsExtensionRequired()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3773-L3791) |
| BehaviorFlags | `B_DENORM_PRESERVE`, `B_DENORM_FLUSH`, `B_ZIN_PRESERVE`, `B_RTE_ROUNDING`, `B_RTZ_ROUNDING` | The float-control behavior under test. Maps to a SPIR-V capability + execution mode pair. | [`BehaviorFlags`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L109-L116) |
| OperationId | many (e.g. `OID_ADD`, `OID_SUB`, `OID_MUL`, `OID_FMA`, `OID_FREM`, `OID_FConvert`, ...) | The SPIR-V operation applied to the two operands. Each maps to a command snippet in the operation map. | [`createOperationMap()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650) |
| Shader stage | compute / vertex / fragment | Compute uses the compute template directly; graphics feeds per-operation snippets through the standard vertex/fragment pipeline. Vertex skips `FPRoundingMode`-decorated cases. | [`createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5371-L5374) |
| SettingsMode | `SM_ROUNDING`, `SM_DENORMS` | Independence settings mode: rounding combinations or denorm preserve/flush combinations across widths. | [`SettingsMode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3610-L3612) |
| Independence | `32_BIT_ONLY`, `ALL` | Advertised independence level probed by the settings tests. | [`createSettingsTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4136-L4138) |
| FP16 storage path | with `VK_KHR_16bit_storage`, without (`_nostorage`) | FP16 tests have a parallel set that drops 16-bit storage and uses `VK_KHR_shader_float16_int8`'s `shaderFloat16` feature, bitcasting FP16 through `u32` for SSBO transport. | [`OperationTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2055-L2064) |

## Behavior Parameters

The primary behavioral axis is the test family, because the file groups structurally different behaviors under one source file: per-width operation tests, cross-width independence settings, and graphics operation tests. A secondary axis within the operation families is the `BehaviorFlags` value, and a third axis is the argument source.

### Operation tests (`fp16` / `fp32` / `fp64`)

Each operation test picks a `VariableType`, an argument source, an `OperationId`, and a `BehaviorFlags` value, then specializes `m_operationShaderTemplate` into a single-invocation compute shader that loads (or generates) two operands, runs the operation, and stores the result. The execution mode declared in the SPIR-V module mirrors the `BehaviorFlags` value, and the host mirrors the same mode into `VkPhysicalDeviceFloatControlsProperties` so the CTS support check gates the case.

The `input_args` path reads operands from the input SSBO; the `generated_args` path constructs operands as SPIR-V constants via `valueIdToSnippetArgMap` (e.g. `V_DENORM` becomes `OpFSub %type_f32 %c_f32_denorm_base %c_f32_eps`). The argument source is the boolean parameter to [`createOperationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4102-L4128).

### `independence_settings` (compute only)

These tests verify that different float widths can have independent control settings within one shader. A single compute shader performs arithmetic on FP16, FP32, and FP64 values, with one execution mode declared per active width. The host picks per-width options (e.g. FP16 RTE + FP32 RTZ) and checks each width's result independently via `checkMixedFloats`. A separate property-only case calls `verifyIndependenceSettings`, which queries `VkPhysicalDeviceFloatControlsProperties` and checks that the reported per-width support bits are internally consistent with the advertised independence level. Created by [`ComputeTestGroupBuilder::createSettingsTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4140).

### Graphics operation tests (`fp16` / `fp32` / `fp64`)

Graphics tests feed the same per-operation snippets through `fragments["capability"]`, `fragments["decoration"]`, `fragments["pre_main"]`, `fragments["testfun"]` into the standard `vktSpvAsmGraphicsShaderTestUtil` vertex/fragment pipeline templates. The tested behavior is the same as the compute operation tests, but surfaced through the vertex or fragment stage. Vertex additionally skips `FPRoundingMode`-decorated cases because SSBO writes do not support `FPRoundingMode` in the required storage class. Built by [`GraphicsTestGroupBuilder::createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4979-L5379).

## Shader Analysis

The file uses two structurally different compute-shader templates. `m_operationShaderTemplate` is a single-invocation compute shader that loads (or generates) two float operands, runs one tested operation, and stores the result to an output SSBO. `m_settingsShaderTemplate` performs arithmetic on FP16, FP32, and FP64 values in one invocation to verify that different widths can be controlled independently. Two representative walkthroughs are warranted because the settings template is structurally different from the operation template (multi-width, separate template, separate verifier).

Per the category-scoped convention for `spirv_assembly` pages, the SPIR-V assembly is extracted from the C++ string templates and placed under `#### Source Code` (unfoldable). The `#### SPIR-V` collapsed subsection that the standard walkthrough template requires is omitted because it would duplicate the assembly already shown under `#### Source Code`. The `shader-disassembler` round-trip (`spirv-as` → `spirv-val` → `spirv-dis`) runs as a generation-time validation gate only; its output is not published. Both walkthroughs below passed that gate.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.float_controls.fp32.input_args.denorm_add_denorm_preserve
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| VariableType `FP32` | Targets `DenormPreserve 32`. FP32 needs no extra `shaderFloat16`/`shaderFloat64` feature, so this is the baseline width. |
| Argument source `input_args` | Operands are read from the input SSBO. The `generated_args` path would construct the denorm as a SPIR-V constant instead. |
| OperationId `OID_ADD` | The operation is `OpFAdd`. Adding a denorm to itself doubles it; under `DenormPreserve` the result stays denormal, under flush it becomes zero. |
| BehaviorFlags `B_DENORM_PRESERVE` | Declares `OpCapability DenormPreserve` and `OpExecutionMode %main DenormPreserve 32`. The expected result is `V_DENORM_TIMES_TWO`. |
| `LocalSize 1 1 1`, single dispatch | One invocation handles the one operand pair. |

#### Purpose

Verify that the implementation preserves a denormal FP32 operand through `OpFAdd` when the shader declares `DenormPreserve 32`. The pass condition is that the output bit pattern matches `V_DENORM_TIMES_TWO` (the denorm added to itself, still denormal). If the implementation had flushed, the result would be zero, which is a failure under `DenormPreserve`.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| Capability and execution mode | `OpCapability Shader` + `OpCapability DenormPreserve`; `OpExecutionMode %main LocalSize 1 1 1` + `OpExecutionMode %main DenormPreserve 32`. | `DenormPreserve 32` is the float-control declaration under test. The implementation must honor it for the `OpFAdd` result. |
| Decorations | `%ssbo_in` and `%ssbo_out` are `BufferBlock`-decorated SSBOs bound to descriptor set 0 bindings 0 and 1; arrays carry `ArrayStride 4`. | The input SSBO carries two FP32 operands; the output SSBO receives one FP32 result. ArrayStride is required by `spirv-val` for block layout. |
| Body | `OpAccessChain` into `%ssbo_in[0][0]` and `%ssbo_in[0][1]`; `OpLoad` both operands; `OpFAdd`; `OpAccessChain` into `%ssbo_out[0][0]`; `OpStore`. | `OpFAdd` is the only arithmetic operation. Under `DenormPreserve`, adding two denorms must yield twice the denorm, not zero. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- **`generated_args` path.** For the same `OperationId` and `BehaviorFlags`, the `generated_args` variant omits the input SSBO load and instead constructs the denorm operand as a SPIR-V constant via `valueIdToSnippetArgMap` (e.g. `OpFSub %type_f32 %c_f32_denorm_base %c_f32_eps`). The execution mode, capability, and `OpFAdd` are identical.
- **`ArrayStride` decorations.** The CTS template emits `ArrayStride` on the input and output arrays. `spirv-val` rejects `BufferBlock` structs whose runtime arrays lack an explicit stride, so these decorations are load-bearing for validation.
- **Per-width `TypeSnippets`.** FP16 swaps in `StorageUniform16` + `Float16` capabilities, 2-byte strides, and `%type_f16` types. FP64 swaps in `Float64`, 8-byte strides, and `%type_f64` types. The `_nostorage` FP16 variant drops `StorageUniform16` and bitcasts through `u32`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `BehaviorFlags` | Swaps `OpCapability` and `OpExecutionMode` lines (e.g. `DenormFlushToZero 32`, `SignedZeroInfNanPreserve 32`, `RoundingModeRTE 32`, `RoundingModeRTZ 32`). | [`getBehaviorCapabilityAndExecutionMode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3793-L3818) |
| `OperationId` | Replaces the `%result = OpFAdd ...` line with the operation's command snippet (e.g. `OpFSub`, `OpFMul`, `OpFma`, `OpFConvert`, `OpExtInst` for trig/log/sqrt). | [`createOperationMap()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650) |
| `VariableType` | Swaps the float type, array stride, capabilities, and load/store snippets for FP16 or FP64. | [source evidence](../../../modules/vulkan/spirv_assembly/) |
| Argument source | `input_args` keeps the SSBO load; `generated_args` replaces it with constant construction. | [`fillShaderSpec(OperationTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4271-L4460) |
| Rounding override | `rounding_rte_override_from_fp32_*` / `rounding_rtz_override_from_fp32_*` add `OpDecorate %result FPRoundingMode RTE|RTZ` on an `OpFConvert` from FP32 to FP16. | [`createOperationMap()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 41
; Schema: 0
               OpCapability Shader
               OpCapability DenormPreserve
               OpExtension "SPV_KHR_float_controls"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_GlobalInvocationID
               OpExecutionMode %2 LocalSize 1 1 1
               OpExecutionMode %2 DenormPreserve 32
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpMemberDecorate %_struct_4 0 Offset 0
               OpDecorate %_struct_4 BufferBlock
               OpDecorate %5 DescriptorSet 0
               OpDecorate %5 Binding 0
               OpDecorate %5 NonWritable
               OpMemberDecorate %_struct_6 0 Offset 0
               OpDecorate %_struct_6 BufferBlock
               OpDecorate %7 DescriptorSet 0
               OpDecorate %7 Binding 1
               OpDecorate %_arr_float_int_1 ArrayStride 4
               OpDecorate %_arr_float_int_2 ArrayStride 4
       %void = OpTypeVoid
         %11 = OpTypeFunction %void
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
     %v2uint = OpTypeVector %uint 2
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_ptr_Function_float = OpTypePointer Function %float
    %v2float = OpTypeVector %float 2
    %v3float = OpTypeVector %float 3
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
%mat2v2float = OpTypeMatrix %v2float 2
%_arr_float_int_1 = OpTypeArray %float %int_1
%_arr_float_int_2 = OpTypeArray %float %int_2
  %_struct_4 = OpTypeStruct %_arr_float_int_2
%_ptr_Uniform__struct_4 = OpTypePointer Uniform %_struct_4
          %5 = OpVariable %_ptr_Uniform__struct_4 Uniform
  %_struct_6 = OpTypeStruct %_arr_float_int_1
%_ptr_Uniform__struct_6 = OpTypePointer Uniform %_struct_6
          %7 = OpVariable %_ptr_Uniform__struct_6 Uniform
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %2 = OpFunction %void None %11
         %34 = OpLabel
         %35 = OpAccessChain %_ptr_Uniform_float %5 %int_0 %int_0
         %36 = OpLoad %float %35
         %37 = OpAccessChain %_ptr_Uniform_float %5 %int_0 %int_1
         %38 = OpLoad %float %37
         %39 = OpFAdd %float %36 %38
         %40 = OpAccessChain %_ptr_Uniform_float %7 %int_0 %int_0
               OpStore %40 %39
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.float_controls.independence_settings.rounding_ind_all_fp16_rte_fp32_rtz
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| SettingsMode `SM_ROUNDING` | Tests rounding-mode independence across widths (the alternative is `SM_DENORMS`). |
| Independence `ALL` | Probes `VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_ALL`: FP16 and FP32 must sustain different rounding modes in one shader. |
| FP16 rounding `RTE` | Declares `OpExecutionMode %main RoundingModeRTE 16`. |
| FP32 rounding `RTZ` | Declares `OpExecutionMode %main RoundingModeRTZ 32`. The two widths use different modes simultaneously. |
| FP64 unused | The third width is not exercised in this case; only FP16 and FP32 results are checked. |
| `LocalSize 1 1 1`, single dispatch | One invocation runs both width operations. |

#### Purpose

Verify that the implementation can sustain different rounding modes for FP16 and FP32 within a single shader when `VkPhysicalDeviceFloatControlsProperties` advertises `INDEPENDENCE_ALL`. The pass condition is that each width's `OpFAdd` result matches its `ValueId`-encoded expected result, checked independently via `checkMixedFloats`.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| Capabilities and execution modes | `OpCapability RoundingModeRTE` + `OpCapability RoundingModeRTZ` + `OpCapability StorageUniform16` + `OpCapability Float16`; two execution modes: `RoundingModeRTZ 32` and `RoundingModeRTE 16`. | Two widths, two modes, one shader. This is the independence probe: the implementation must apply each mode only to its width. |
| Decorations | Three SSBOs: `%ssbo_in` (binding 0, input), `%ssbo_f32_out` (binding 1), `%ssbo_f16_out` (binding 2). Input struct packs FP32 array then FP16 array, ordered 64 → 16 for storage layout. | One input buffer carries operands for all active widths; one output buffer per width so independence can be observed per width. |
| Body | Load FP32 operands from `%ssbo_in[0]`, `OpFAdd`, store to `%ssbo_f32_out`; load FP16 operands from `%ssbo_in[1]`, `OpFAdd`, store to `%ssbo_f16_out`. | The same `OpFAdd` runs on both widths. The expected result differs per width because the rounding modes differ. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- **FP64 slot.** When the case exercises FP64, the template adds a third output SSBO and a third `OpFAdd` path on `%type_f64`. The `rounding_ind_all_fp16_rte_fp32_rtz` case leaves FP64 unused, so the FP64 path and its execution mode are absent.
- **`SM_DENORMS` variant.** The denorms settings mode swaps `RoundingModeRTE`/`RoundingModeRTZ` for `DenormPreserve`/`DenormFlushToZero` per width. The template structure (one input SSBO, one output SSBO per active width, `OpFAdd` per width) is identical.
- **`_nostorage` settings variant.** Settings tests also have a `rounding_ind_32_bit_only_*` shape and a `_nostorage` variant that drops `VK_KHR_16bit_storage` and bitcasts FP16 through `u32`, mirroring the operation-test `_nostorage` path.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `SettingsMode` | `SM_DENORMS` swaps the rounding-mode capabilities and execution modes for `DenormPreserve`/`DenormFlushToZero` per width. | [`fillShaderSpec(SettingsTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4462-L4554) |
| `Independence` | `32_BIT_ONLY` restricts the probed combination so only 32-bit-only independence is required; `ALL` requires all widths to be independently controllable. | [`createSettingsTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4140) |
| Per-width option | Swaps which execution mode is declared per width (e.g. FP16 RTZ + FP32 RTE, or FP16 preserve + FP32 flush). | [`fillShaderSpec(SettingsTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4462-L4554) |
| FP64 active | Adds `%type_f64`, a third output SSBO, a third `OpFAdd` path, and the FP64 execution mode. | [source evidence](../../../modules/vulkan/spirv_assembly/) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 42
; Schema: 0
               OpCapability Shader
               OpCapability RoundingModeRTE
               OpCapability RoundingModeRTZ
               OpCapability UniformAndStorageBuffer16BitAccess
               OpCapability Float16
               OpExtension "SPV_KHR_float_controls"
               OpExtension "SPV_KHR_16bit_storage"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_GlobalInvocationID
               OpExecutionMode %2 LocalSize 1 1 1
               OpExecutionMode %2 RoundingModeRTZ 32
               OpExecutionMode %2 RoundingModeRTE 16
               OpDecorate %_struct_4 BufferBlock
               OpDecorate %5 DescriptorSet 0
               OpDecorate %5 Binding 0
               OpDecorate %5 NonWritable
               OpMemberDecorate %_struct_4 0 Offset 0
               OpMemberDecorate %_struct_6 0 Offset 0
               OpDecorate %_arr_float_int_2 ArrayStride 4
               OpDecorate %_struct_6 BufferBlock
               OpDecorate %8 DescriptorSet 0
               OpDecorate %8 Binding 1
               OpMemberDecorate %_struct_4 1 Offset 8
               OpMemberDecorate %_struct_9 0 Offset 0
               OpDecorate %_arr_half_int_2 ArrayStride 2
               OpDecorate %_struct_9 BufferBlock
               OpDecorate %11 DescriptorSet 0
               OpDecorate %11 Binding 2
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
       %void = OpTypeVoid
         %13 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %float = OpTypeFloat 32
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_arr_float_int_2 = OpTypeArray %float %int_2
       %half = OpTypeFloat 16
%_ptr_Uniform_half = OpTypePointer Uniform %half
%_arr_half_int_2 = OpTypeArray %half %int_2
  %_struct_4 = OpTypeStruct %_arr_float_int_2 %_arr_half_int_2
%_ptr_Uniform__struct_4 = OpTypePointer Uniform %_struct_4
          %5 = OpVariable %_ptr_Uniform__struct_4 Uniform
  %_struct_6 = OpTypeStruct %float
%_ptr_Uniform__struct_6 = OpTypePointer Uniform %_struct_6
          %8 = OpVariable %_ptr_Uniform__struct_6 Uniform
  %_struct_9 = OpTypeStruct %half
%_ptr_Uniform__struct_9 = OpTypePointer Uniform %_struct_9
         %11 = OpVariable %_ptr_Uniform__struct_9 Uniform
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %2 = OpFunction %void None %13
         %29 = OpLabel
         %30 = OpAccessChain %_ptr_Uniform_float %5 %int_0 %int_0
         %31 = OpAccessChain %_ptr_Uniform_float %5 %int_0 %int_1
         %32 = OpLoad %float %30
         %33 = OpLoad %float %31
         %34 = OpFAdd %float %32 %33
         %35 = OpAccessChain %_ptr_Uniform_half %5 %int_1 %int_0
         %36 = OpAccessChain %_ptr_Uniform_half %5 %int_1 %int_1
         %37 = OpLoad %half %35
         %38 = OpLoad %half %36
         %39 = OpFAdd %half %37 %38
         %40 = OpAccessChain %_ptr_Uniform_float %8 %int_0
               OpStore %40 %34
         %41 = OpAccessChain %_ptr_Uniform_half %11 %int_0
               OpStore %41 %39
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Operation tests.** [`fillShaderSpec(OperationTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4271-L4460) specializes `m_operationShaderTemplate`, constructs the input SSBO from `ValueId`-encoded arguments (for `input_args`) or leaves it empty (for `generated_args`), constructs the expected output SSBO from the `ValueId`-encoded expected result, and mirrors the requested execution mode into `VkPhysicalDeviceFloatControlsProperties` via [`setupFloatControlsProperties()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3820-L3849). The CTS compute framework dispatches one workgroup (`LocalSize 1 1 1`); the shader loads operands, runs the operation, and stores the result.
- **Settings tests.** [`fillShaderSpec(SettingsTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4462-L4554) specializes `m_settingsShaderTemplate`, picks per-width execution modes and expected results, and packs a single input SSBO carrying FP64+FP32+FP16 argument pairs (ordered 64 → 16 for storage layout). One workgroup runs `OpFAdd` per active width and stores each result to its own output SSBO.
- **Graphics tests.** [`GraphicsTestGroupBuilder::createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5379-L5379) feeds the same per-operation snippets through the standard vertex/fragment pipeline and compares rendered output via `checkFloatsLUT[]` dispatches.
- **Result comparison.** [`checkFloats<FloatType, UintType>`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3532-L3550) decodes the expected `ValueId` from the expected buffer and compares bit patterns. Comparison is bit-exact for normal values, with special-case handling for `V_NAN` (any NaN bit pattern passes), `V_DENORM` (any denormal bit pattern passes), and multi-acceptable-result codes like `V_ZERO_OR_DENORM_TIMES_TWO` (multiple acceptable bit patterns pass). Trig/log/sqrt result codes use a precision-aware helper that accepts results within a tolerance band. Settings tests use [`checkMixedFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3551-L3570), which dispatches per-width comparison based on a `BufferDataType` tag carried in each expected resource.
- **Property-only case.** [`verifyIndependenceSettings()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3878-L3960) queries `VkPhysicalDeviceFloatControlsProperties` and checks that the reported per-width support bits are internally consistent with the advertised `roundingModeIndependence` / `denormBehaviorIndependence` level. Under `INDEPENDENCE_NONE`, all three widths must report the same support for each mode.
- The check runs on the host; the device only produces the output buffer.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Operation input SSBO (`%ssbo_in`, binding 0) | Host, filled from `ValueId` arguments | Descriptor set 0, binding 0 | Read by shader (`input_args` only) | No | Carries the two operands for the tested operation; empty for `generated_args`. |
| Operation output SSBO (`%ssbo_out`, binding 1) | Host, allocated and filled with expected `ValueId` result | Descriptor set 0, binding 1 | Written by shader | Yes | Receives the operation result; host compares against the expected buffer. |
| Settings input SSBO (`%ssbo_in`, binding 0) | Host, packs FP64+FP32+FP16 argument pairs | Descriptor set 0, binding 0 | Read by shader | No | Single buffer carries operands for all active widths, ordered 64 → 16. |
| Settings output SSBOs (`%ssbo_*_out`, bindings 1-3) | Host, one per active width | Descriptor set 0, bindings 1-3 | Written by shader | Yes | One result slot per width so independence can be observed per width. |
| Graphics color attachments | Host | Yes | Read/written by fixed function + shader | Yes (compared) | Drive the vertex/fragment pipeline so the per-stage `testfun` runs once. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fp16` / `fp32` / `fp64` operation tests (denorm preserve/flush) | Implementation did not honor `DenormPreserve`/`DenormFlushToZero` for the tested width; denorms were flushed when they should be preserved or vice versa. |
| `fp16` / `fp32` / `fp64` operation tests (signed zero/inf/NaN preserve) | Implementation did not preserve the tested signed-zero or infinity result, or did not produce a NaN where the expected result is `V_NAN`. The verifier accepts any NaN bit pattern for `V_NAN`; it does not diagnose a NaN-payload change. |
| `fp16` / `fp32` / `fp64` operation tests (rounding RTE/RTZ) | Implementation used the wrong rounding mode for the tested arithmetic or conversion result, or ignored an `FPRoundingMode` decoration on an `OpFConvert` override case. |
| `independence_settings` (rounding or denorm) | Implementation applied one width's execution mode to another width, or could not sustain different modes per width when the advertised independence level claimed it could. |
| `independence_settings` (property-only case) | Reported `VkPhysicalDeviceFloatControlsProperties` are internally inconsistent with the advertised independence level. |
| Graphics `fp16` / `fp32` / `fp64` (`_vert` / `_frag`) | Same causes as compute, but surfaced through the vertex or fragment stage pipeline; vertex additionally skips `FPRoundingMode`-decorated cases that SSBO writes cannot express. |

### Cause Analysis

#### Denorm preserve/flush not honored

**Possible failure symptoms:** `checkFloats` reports a mismatch between the output bit pattern and the expected `ValueId`-encoded result. For example, an FP32/FP64 `B_DENORM_PRESERVE` add case expecting `V_DENORM_TIMES_TWO` can return zero if the result was flushed, while a flush case expecting `V_ZERO` can return a denormal if it was preserved. Some FP16 flush cases deliberately accept more than one result, such as `V_ZERO_OR_DENORM_TIMES_TWO`, so their failure meaning is determined by the case's encoded expected value rather than by a universal zero-versus-denormal rule.

**Possible implementation causes:** after the framework has accepted the requested per-width float-controls property, the implementation may fail to honor the declared execution mode for the relevant operation. For an arithmetic case this can leave the result governed by the implementation's other denorm behavior rather than the requested mode. Source-level investigation is needed to distinguish a dropped execution mode from a backend or hardware behavior issue.

#### Signed zero/inf/NaN preservation not honored

**Possible failure symptoms:** `checkFloats` reports a mismatch on a `B_ZIN_PRESERVE` case. The output can have the wrong signed-zero or infinity result, or a case expecting `V_NAN` can produce a non-NaN value. `checkValue()` accepts any NaN for `V_NAN`, so a NaN-payload difference alone is not a failure detected by this test.

**Possible implementation causes:** after the framework has accepted `shaderSignedZeroInfNanPreserveFloat*` for the requested width, the implementation may fail to apply the preservation requirement to the operation's lowering. The source identifies the failing operation and expected `ValueId`; it does not by itself localize the defect to a particular compiler pass or NaN-payload transformation.

#### Wrong rounding mode applied

**Possible failure symptoms:** `checkFloats` reports a mismatch on a `B_RTE_ROUNDING` or `B_RTZ_ROUNDING` case. The output differs from the expected `ValueId`-encoded result by one unit in the last place of the target width, in the direction consistent with the wrong rounding mode. Rounding-override cases (`rounding_rte_override_from_fp32_*` / `rounding_rtz_override_from_fp32_*`) fail when the per-instruction `FPRoundingMode` decoration is ignored.

**Possible implementation causes:** the implementation may not honor `OpExecutionMode RoundingModeRTE`/`RoundingModeRTZ` for the destination width, or an override case may ignore `FPRoundingMode` on its `OpFConvert`. Spec-constant conversion cases (`sconst_conv_from_fp32_*`) exercise whether `OpSpecConstantOp ... FConvert` applies the declared rounding mode. Source-level investigation is needed to localize the cause.

#### Cross-width independence not sustained

**Possible failure symptoms:** `checkMixedFloats` reports a mismatch on one width's output while the other width's output matches. For the `rounding_ind_all_fp16_rte_fp32_rtz` case, the FP16 result matches `RTE` expectations but the FP32 result matches `RTE` instead of `RTZ` (or vice versa), indicating one width's mode leaked into the other.

**Possible implementation causes:** after the framework has accepted the requested independence level, the implementation may fail to apply the separately declared modes to their respective widths. The source can show a width-specific result mismatch, but source-level investigation is needed to determine whether per-width modes were coalesced or another execution defect caused it.

#### Property consistency failure

**Possible failure symptoms:** the property-only `independence_settings` case fails with a mismatch reported by `verifyIndependenceSettings`, before any shader runs.

**Possible implementation causes:** the reported `VkPhysicalDeviceFloatControlsProperties` are internally inconsistent. For example, under `INDEPENDENCE_NONE` the three widths report different per-mode support bits, or under `INDEPENDENCE_32_BIT_ONLY` the 16-bit and 64-bit support bits differ. This is a driver reporting bug, not a shader-execution bug.

## Case Pruning

### Requirement-based pruning

- Mixed-settings cases always request `VK_KHR_shader_float_controls`; operation and graphics cases request it unless [`isFloatControlsExtensionRequired()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3773-L3791) recognizes an `input_args` `DenormPreserve` operation that Vulkan already guarantees will preserve denorms without that mode.
- Specialized operation cases request `shaderFloat16`, `shaderFloat64`, and `shaderInt64` only when their selected input/output types and generated capabilities require them; membership in the top-level `fp16` or `fp64` group alone is not a universal feature requirement. [`fillShaderSpec(OperationTestCaseInfo)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4414-L4459) computes those requests.
- Integer-to/from-64-bit conversion paths request `shaderInt64` when their selected input or output type is `INT64` or `UINT64`.
- FP16 `_nostorage` variants require `VK_KHR_shader_float16_int8`'s `shaderFloat16` feature instead of `VK_KHR_16bit_storage`.
- Settings tests with FP16 require `VK_KHR_16bit_storage` for the storage path, or `VK_KHR_shader_float16_int8` for the `_nostorage` path, checked in [`fillSettingsTestCase()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4641-L4665).
- Graphics contexts request `fragmentStoresAndAtomics` as part of their common feature set. [`GraphicsTestGroupBuilder::createInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5351-L5364) builds both vertex and fragment modules for the graphics pipeline.
- The shared support check compares requested per-width float-controls properties and requested independence against the device properties before execution. It reports the case as not supported when a requested property, independence level, extension, or other required feature is unavailable; operation cases that do not request float-controls properties are not pruned by those properties. [`isFloatControlsFeaturesSupported()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.cpp#L327-L399)

### Design-based pruning

- **`input_args` denorm extension omission.** For `input_args` `DenormPreserve` cases whose operations Vulkan already guarantees preserve denorms (`OpPhi`, `OpSelect`, `OpReturnValue`, `OpVectorExtractDynamic`, `OpVectorInsertDynamic`, `OpVectorShuffle`, `OpCompositeConstruct`, `OpCompositeInsert`, `OpTranspose`, `OpCopy`), the float-controls extension and execution mode are omitted because the behavior is already required. Generated-argument cases are not omitted by this rule.
- **Vertex rounding-override skip.** `rounding_rte_override_from_fp32_*` and `rounding_rtz_override_from_fp32_*` are skipped for the vertex stage because SSBO writes do not support `FPRoundingMode` in the required storage class.
- **Graphics settings no-op.** `GraphicsTestGroupBuilder::createSettingsTests` is intentionally empty; independence settings are tested compute-only by design decision.
- **`UnpackHalf2x16` width override.** `UnpackHalf2x16` forces the float-controls width to 16 even though the output is FP32, because the operation's denorm behavior is governed by the 16-bit width.

## Key Takeaways

- The file builds SPIR-V assembly text directly from two C++ string templates (`m_operationShaderTemplate` and `m_settingsShaderTemplate`); there is no GLSL or HLSL source. The assembly is the source of truth.
- The test does not compare against a host-computed reference float. `ValueId` tokens encode both arguments and expected results, with multi-acceptable-result codes like `V_ZERO_OR_DENORM_TIMES_TWO` expressing "either behavior is legal here" in one token.
- Operation tests probe one execution mode on one width with one operation; settings tests probe whether different widths can sustain different modes in one shader. The two templates are structurally different and use different verifiers (`checkFloats` versus `checkMixedFloats`).
- The `independence_settings` family is compute-only by design; the graphics builder's `createSettingsTests` is intentionally empty.
- The `_nostorage` FP16 variant drops `VK_KHR_16bit_storage` and bitcasts FP16 through `u32`, mirroring the operation-test path for devices that expose `shaderFloat16` without 16-bit storage.
- See `## Failure Meaning` for the failure interpretation: a denorm/rounding mismatch points to the execution mode not being honored; a width-specific settings mismatch points to cross-width mode leakage; a property-only case failure points to inconsistent `VkPhysicalDeviceFloatControlsProperties` reporting.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createFloatControlsTestGroup()` | [`vktSpvAsmFloatControlsTests.cpp#L5383-L5410`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383-L5410) | Creates `fp16`/`fp32`/`fp64` operation groups and calls `createSettingsTests`. |
| `m_operationShaderTemplate` | [`vktSpvAsmFloatControlsTests.cpp#L3978-L4044`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3978-L4044) | The compute shader string template for all operation tests. |
| `m_settingsShaderTemplate` | [`vktSpvAsmFloatControlsTests.cpp#L4046-L4099`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4046-L4099) | The compute shader string template for independence settings tests. |
| `ComputeTestGroupBuilder::createOperationTests()` | [`vktSpvAsmFloatControlsTests.cpp#L4102-L4128`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4102-L4128) | Builds per-operation compute cases for `input_args` / `generated_args`. |
| `ComputeTestGroupBuilder::createSettingsTests()` | [`vktSpvAsmFloatControlsTests.cpp#L4130-L4140`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4140) | Enumerates all independence_settings cases and the property-only case. |
| `ComputeTestGroupBuilder::fillShaderSpec(OperationTestCaseInfo)` | [`vktSpvAsmFloatControlsTests.cpp#L4271-L4460`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4271-L4460) | Specializes the operation template and sets up buffers/features. |
| `ComputeTestGroupBuilder::fillShaderSpec(SettingsTestCaseInfo)` | [`vktSpvAsmFloatControlsTests.cpp#L4462-L4554`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4462-L4554) | Specializes the settings template, picks per-width execution modes and expected results. |
| `getBehaviorCapabilityAndExecutionMode()` | [`vktSpvAsmFloatControlsTests.cpp#L3793-L3818`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3793-L3818) | Translates `BehaviorFlags` into `OpCapability` + `OpExecutionMode` strings. |
| `setupFloatControlsProperties()` | [`vktSpvAsmFloatControlsTests.cpp#L3820-L3849`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3820-L3849) | Mirrors requested execution modes into `VkPhysicalDeviceFloatControlsProperties`. |
| `verifyIndependenceSettings()` | [`vktSpvAsmFloatControlsTests.cpp#L3878-L3960`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3878-L3960) | Property-only case that validates reported support bits against the independence level. |
| `checkValue()` | [`vktSpvAsmFloatControlsTests.cpp#L3440-L3530`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3440-L3530) | `ValueId`-decoded bit comparison with NaN/denorm/multi-result handling. |
| `checkFloats()` | [`vktSpvAsmFloatControlsTests.cpp#L3532-L3549`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3532-L3549) | Wrapper around `checkValue` for single-width operation tests. |
| `checkMixedFloats()` | [`vktSpvAsmFloatControlsTests.cpp#L3551-L3570`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3551-L3570) | Per-width dispatch for settings tests. |
| `createOperationMap()` | [`vktSpvAsmFloatControlsTests.cpp#L2142-L2650`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650) | SPIR-V command snippets per `OperationId`. |
| `BehaviorFlags` enum | [`vktSpvAsmFloatControlsTests.cpp#L109-L116`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L109-L116) | The five tested float-control behaviors. |
| `ValueId` enum | [`vktSpvAsmFloatControlsTests.cpp#L122-L276`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L122-L276) | Encoded argument/result values. |
| `GraphicsTestGroupBuilder::createSettingsTests()` | [`vktSpvAsmFloatControlsTests.cpp#L4973-L4978`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4973-L4978) | Documents the compute-only decision for settings. |
| `GraphicsTestGroupBuilder::createInstanceContext()` | [`vktSpvAsmFloatControlsTests.cpp#L4979-L5379`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4979-L5379) | Builds the graphics pipeline context for vertex/fragment operation tests. |
