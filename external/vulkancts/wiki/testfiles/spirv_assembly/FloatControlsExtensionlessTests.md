## Overview

**Core question:** does the implementation accept and execute the five SPIR-V float-control execution modes (`DenormPreserve`, `DenormFlushToZero`, `SignedZeroInfNanPreserve`, `RoundingModeRTE`, `RoundingModeRTZ`) without the `VK_KHR_shader_float_controls` extension, by relying on either `VK_KHR_spirv_1_4` or the Vulkan 1.2 core path?

- Source file: [`vktSpvAsmFloatControlsExtensionlessTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp). It builds SPIR-V assembly text directly in a C++ string template and registers 30 compute test case leaves under `spirv_assembly.instruction.compute.float_controls_extensionless`.
- 30 case leaves span 2 version-path families (`spirv1p4`, `vulkan1_2`) × 3 float widths (16, 32, 64) × 5 execution modes. The case-name pattern is `fp<width>_<mode>`, built in [`createFloatControlsExtensionlessGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L280).
- The shader body is a smoke test: it loads a 32-bit float from an input SSBO, applies `OpFNegate`, and stores the result. The `fpWideness` value only reaches `OpExecutionMode`; `OpCapability` receives only `featureName`. The body always uses `%f32`. The test proves the execution-mode declaration is accepted, not that the mode changes arithmetic behavior.
- The page covers the registration tree, the parameter matrix, the per-mode behavior, a representative extracted SPIR-V walkthrough, the runtime flow, failure meaning, and the per-width/per-mode pruning gates.

## Background Knowledge

- **SPIR-V float-control execution modes.** SPIR-V defines five execution modes that control how the implementation handles floating-point edge cases for a target bit width: `DenormPreserve` (preserve denormals), `DenormFlushToZero` (flush denormals to zero), `SignedZeroInfNanPreserve` (preserve sign of zero and encoding of infinities/NaNs), `RoundingModeRTE` (round to nearest even), and `RoundingModeRTZ` (round toward zero). Each is declared per entry point with a width: `OpExecutionMode %main DenormPreserve 32`. The matching `OpCapability` must also be present.
- **Extensionless path.** `VK_KHR_shader_float_controls` was the original way to expose these capabilities. Vulkan 1.2 and `VK_KHR_spirv_1_4` promote the SPIR-V 1.4 surface (which includes the float-control execution modes as core), so the extension is no longer required. The `spirv1p4` family enables SPIR-V 1.4 via `VK_KHR_spirv_1_4` on a Vulkan 1.1 device; the `vulkan1_2` family relies on Vulkan 1.2 core support. The test deliberately omits `VK_KHR_shader_float_controls` from the extension list.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.float_controls_extensionless
├── spirv1p4
└── vulkan1_2
```

Both direct children are intermediate nodes registered by [`createFloatControlsExtensionlessGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L280). Each intermediate node holds the same 15 test case leaves (`fp16_denorm_preserve`, `fp16_denorm_flush_to_zero`, ..., `fp64_rounding_mode_rtz`). The `spirv_assembly.instruction.compute` ancestor is registered by a separate file; this page does not expand it.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Version path | `spirv1p4`, `vulkan1_2` | Selects the extensionless mechanism. `spirv1p4` requires `VK_KHR_spirv_1_4`; `vulkan1_2` requires Vulkan 1.2. The SPIR-V assembly and build options are identical for both paths. | [`spirVersions` array](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L243) |
| Float width | 16, 32, 64 | Target width passed to `OpExecutionMode`. The shader body always operates on `%f32`; this width only changes the declared execution-mode target and the per-width feature/property gates. | [`floatingPointWideness` array](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L242-L244) |
| Execution mode | `denorm_preserve`, `denorm_flush_to_zero`, `signed_zero_inf_nan_preserve`, `rounding_mode_rte`, `rounding_mode_rtz` | The float-control feature under test. Each value maps to a SPIR-V capability and execution-mode name. This is the primary behavioral axis. | [`fpFeatures` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L244-L254) |

## Behavior Parameters

The primary behavioral axis is the execution mode. Each mode is a different float-control property being accepted by the implementation on the extensionless path. The float width is a secondary axis that changes the declared `OpExecutionMode` target; the version path is a configuration dimension that changes the API entry point but not the SPIR-V behavior.

A design choice shared by every value: the `fpWideness` value only reaches the `OpExecutionMode` line; the `OpCapability` line receives only the feature name. The shader body always loads, negates, and stores a 32-bit float (`%f32`). The test therefore validates that the execution-mode declaration is accepted and the shader compiles/runs, not that the mode changes the result of `OpFNegate` on the target width. For `fpWideness=16` and `fpWideness=64`, the execution mode targets a width that the shader body does not exercise arithmetically.

### `denorm_preserve`: `DenormPreserve`

Declares `OpCapability DenormPreserve` and `OpExecutionMode %main DenormPreserve <width>`. The implementation must accept the declaration and run the shader. The corresponding `VkPhysicalDeviceFloatControlsProperties` boolean (`shaderDenormPreserveFloat16`/`Float32`/`Float64`) must be `VK_TRUE` for the case to run.

### `denorm_flush_to_zero`: `DenormFlushToZero`

Declares `OpCapability DenormFlushToZero` and `OpExecutionMode %main DenormFlushToZero <width>`. Same smoke-test shape; the per-width `shaderDenormFlushToZeroFloat*` property gates the case.

### `signed_zero_inf_nan_preserve`: `SignedZeroInfNanPreserve`

Declares `OpCapability SignedZeroInfNanPreserve` and `OpExecutionMode %main SignedZeroInfNanPreserve <width>`. Same smoke-test shape; the per-width `shaderSignedZeroInfNanPreserveFloat*` property gates the case.

### `rounding_mode_rte`: `RoundingModeRTE`

Declares `OpCapability RoundingModeRTE` and `OpExecutionMode %main RoundingModeRTE <width>`. Same smoke-test shape; the per-width `shaderRoundingModeRTEFloat*` property gates the case.

### `rounding_mode_rtz`: `RoundingModeRTZ`

Declares `OpCapability RoundingModeRTZ` and `OpExecutionMode %main RoundingModeRTZ <width>`. Same smoke-test shape; the per-width `shaderRoundingModeRTZFloat*` property gates the case.

For every mode, the three widths (16, 32, 64) and two version paths (`spirv1p4`, `vulkan1_2`) are independently registered, giving `5 × 3 × 2 = 30` cases.

## Shader Analysis

All 30 cases share one compute-shader template built by [`getComputeSourceCode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L51-L84). The template is parameterized by `featureName` (the SPIR-V capability/execution-mode name) and `fpWideness` (16, 32, or 64). Only two lines vary across cases: the `OpCapability <featureName>` line and the `OpExecutionMode %main <featureName> <fpWideness>` line. A single representative walkthrough is sufficient.

Per the category-scoped convention for `spirv_assembly` pages, the SPIR-V assembly is extracted from the C++ string template and placed under `#### Source Code` (unfoldable). The `#### SPIR-V` collapsed subsection that the standard walkthrough template requires is omitted because it would duplicate the assembly already shown under `#### Source Code`. The `shader-disassembler` round-trip (`spirv-as` → `spirv-val` → `spirv-dis`) runs as a generation-time validation gate only; its output is not published.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.float_controls_extensionless.spirv1p4.fp32_denorm_preserve
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Version path `spirv1p4` | Selects the `VK_KHR_spirv_1_4` extensionless path. The `vulkan1_2` path produces identical SPIR-V and differs only in `checkSupport()`. |
| Float width `32` | Targets `DenormPreserve 32` in `OpExecutionMode`. `fp32` needs no extra `shaderFloat16`/`shaderFloat64` feature, so this is the baseline combination. |
| Execution mode `denorm_preserve` | Declares `OpCapability DenormPreserve` and `OpExecutionMode %main DenormPreserve 32`. Any of the five modes would exercise the same template; this one is representative. |
| `SpirVAsmBuildOptions(usedVulkanVersion, SPIRV_VERSION_1_4, allowSpirv14=true)` | Build options applied in [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L195-L203). |
| `numWorkGroups = (64, 1, 1)` | 64 invocations, one per input float element. |
| 64 random floats in [1.0, 100.0] | Input data; expected outputs are the negated inputs. |

#### Purpose

Verify that the implementation accepts a SPIR-V 1.4 compute module declaring `OpCapability DenormPreserve` and `OpExecutionMode %main DenormPreserve 32` on the `VK_KHR_spirv_1_4` extensionless path, and that the shader runs and produces the expected negated outputs. The pass condition is that every output element matches `-input[element]` within `epsilon = 0.001`.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| Capability and execution mode | `OpCapability Shader` + `OpCapability DenormPreserve`; `OpExecutionMode %main LocalSize 1 1 1` + `OpExecutionMode %main DenormPreserve 32`. | The two float-control-specific lines are the only SPIR-V that varies across the 30 cases. The implementation must accept them on the extensionless path. |
| Entry point and memory model | `OpEntryPoint GLCompute %main "main" %id %indata %outdata`; `OpMemoryModel Logical GLSL450`; `OpSource GLSL 430`. | Lists the built-in `gl_GlobalInvocationID` and both SSBO variables in the interface. SPIR-V 1.4 requires module-scope variables to be listed. |
| Decorations | `%id` is `BuiltIn GlobalInvocationId`; `%buf` is `Block`; `%indata` is `DescriptorSet 0 Binding 0`; `%outdata` is `DescriptorSet 0 Binding 1`; `%f32arr ArrayStride 4`; `%buf member 0 Offset 0`. | Binds the two SSBOs to descriptor set 0 bindings 0 and 1 with a 4-byte `float` runtime array. The host buffer setup must match. |
| Type declarations | `%f32 = OpTypeFloat 32`; `%uvec3 = OpTypeVector %u32 3`; `%f32arr = OpTypeRuntimeArray %f32`; `%buf = OpTypeStruct %f32arr`; `%f32ptr = OpTypePointer StorageBuffer %f32`. | The shader body uses `%f32` regardless of `fpWideness`. The width reaches only `OpExecutionMode`; `OpCapability` receives only the feature name. |
| Body | Load `gl_GlobalInvocationID.x`; `OpAccessChain` into `%indata[0][x]`; `OpLoad %f32`; `OpFNegate %f32`; `OpAccessChain` into `%outdata[0][x]`; `OpStore`. | `OpFNegate` is the only arithmetic operation. The result is `-input[x]`, which the host compares against the expected negated input. |
| Dispatch | `LocalSize 1 1 1`, dispatched as `(64, 1, 1)`. | One invocation per input element. The host writes 64 random floats and expects 64 negated outputs. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- **Width-mode decoupling.** The `fpWideness` parameter only reaches `OpExecutionMode %main <featureName> <fpWideness>`; `OpCapability <featureName>` receives only the feature name. The shader body uses `%f32` for every case. For `fpWideness=16` and `fpWideness=64`, the execution mode targets a width that the shader body does not exercise arithmetically. This is intentional: the test is a smoke test for acceptance of the execution-mode declaration.
- **`OpNop` inside the function body.** The template includes a single `OpNop` between the index extraction and the SSBO access. It carries no semantic meaning; it is a placeholder.
- **`OpSource GLSL 430`.** The shader is assembled from text, not compiled from GLSL. The `OpSource` line is metadata only.
- **`vulkan1_2` path produces identical assembly.** The `spirv1p4` and `vulkan1_2` families differ only in `checkSupport()`; the SPIR-V text and build options are identical.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Variation 1 | `OpCapability <featureName>`: one of `DenormPreserve`, `DenormFlushToZero`, `SignedZeroInfNanPreserve`, `RoundingModeRTE`, `RoundingModeRTZ`. | [source evidence](../../../modules/vulkan/spirv_assembly/) |
| Variation 2 | `OpExecutionMode %main <featureName> <fpWideness>`: the width is 16, 32, or 64. | [source evidence](../../../modules/vulkan/spirv_assembly/) |
| Variation 3 | The `checkSupport()` path: `VK_KHR_spirv_1_4` for `spirv1p4`, Vulkan 1.2 for `vulkan1_2`. | [source evidence](../../../modules/vulkan/spirv_assembly/) |
| Variation 4 | The per-width feature gates: `shaderFloat16` + `VK_KHR_shader_float16_int8` for `fp16`; `shaderFloat64` for `fp64`; none for `fp32`. | [source evidence](../../../modules/vulkan/spirv_assembly/) |
| Variation 5 | The per-width/mode property gate in `getFloatControlsProperty()`. | [source evidence](../../../modules/vulkan/spirv_assembly/) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 28
; Schema: 0
               OpCapability Shader
               OpCapability DenormPreserve
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %3 %4
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main DenormPreserve 32
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_struct_5 Block
               OpDecorate %3 DescriptorSet 0
               OpDecorate %3 Binding 0
               OpDecorate %4 DescriptorSet 0
               OpDecorate %4 Binding 1
               OpDecorate %_runtimearr_float ArrayStride 4
               OpMemberDecorate %_struct_5 0 Offset 0
       %bool = OpTypeBool
       %void = OpTypeVoid
          %9 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
      %float = OpTypeFloat 32
     %v3uint = OpTypeVector %uint 3
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
%_runtimearr_int = OpTypeRuntimeArray %int
%_runtimearr_float = OpTypeRuntimeArray %float
  %_struct_5 = OpTypeStruct %_runtimearr_float
%_ptr_StorageBuffer__struct_5 = OpTypePointer StorageBuffer %_struct_5
          %3 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
          %4 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
      %int_0 = OpConstant %int 0
       %main = OpFunction %void None %9
         %21 = OpLabel
         %22 = OpLoad %v3uint %gl_GlobalInvocationID
         %23 = OpCompositeExtract %uint %22 0
               OpNop
         %24 = OpAccessChain %_ptr_StorageBuffer_float %3 %int_0 %23
         %25 = OpLoad %float %24
         %26 = OpFNegate %float %25
         %27 = OpAccessChain %_ptr_StorageBuffer_float %4 %int_0 %23
               OpStore %27 %26
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`SpvAsmFloatControlsExtensionlessInstance`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L172-L183) constructs the `ComputeShaderSpec` via [`getComputeShaderSpec()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L86-L112):
  - 64 random floats in `[1.0, 100.0]` seeded by `deStringHash(testCaseName) + baseSeed` form the input buffer.
  - The expected output buffer is the negated input.
  - `spec.numWorkGroups = tcu::IVec3(64, 1, 1)` matches `LocalSize 1 1 1` so each invocation handles one element.
  - `spec.verifyIO = &verifyOutput` wires the host-side check.
- The CTS compute-shader framework compiles the assembled SPIR-V, creates the pipeline, binds the input SSBO to descriptor set 0 binding 0 and the output SSBO to binding 1, and dispatches `(64, 1, 1)`.
- Each invocation loads `input[x]`, applies `OpFNegate`, and stores to `output[x]`.
- [`verifyOutput()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L135-L140) compares every output element against the expected negated input with `epsilon = 0.001`. The case passes only when all 64 elements match.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Input SSBO (`%indata`) | Host, 64 random floats in [1.0, 100.0] | Descriptor set 0, binding 0, `StorageBuffer` | Read by compute shader | No (compared via output) | Provides the per-invocation float input. |
| Output SSBO (`%outdata`) | Host, zero-initialized | Descriptor set 0, binding 1, `StorageBuffer` | Written by compute shader | Yes, via `verifyOutput` | Receives the negated input; checked element-by-element. |
| `gl_GlobalInvocationID` built-in | Driver | Input | Read by compute shader | No | Selects the per-invocation array index. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `denorm_preserve` | Implementation rejects `OpCapability DenormPreserve` / `OpExecutionMode DenormPreserve <width>` on the extensionless path, or the property is advertised but not honored. |
| `denorm_flush_to_zero` | Implementation rejects `DenormFlushToZero` on the extensionless path, or the property is advertised but not honored. |
| `signed_zero_inf_nan_preserve` | Implementation rejects `SignedZeroInfNanPreserve` on the extensionless path, or the property is advertised but not honored. |
| `rounding_mode_rte` | Implementation rejects `RoundingModeRTE` on the extensionless path, or the property is advertised but not honored. |
| `rounding_mode_rtz` | Implementation rejects `RoundingModeRTZ` on the extensionless path, or the property is advertised but not honored. |
| (all modes, `fp16` cases) | `shaderFloat16` feature or `VK_KHR_shader_float16_int8` not supported; the 16-bit path is misconfigured. |
| (all modes, `fp64` cases) | `shaderFloat64` core feature not supported; the 64-bit path is misconfigured. |
| (all modes, `spirv1p4` family) | `VK_KHR_spirv_1_4` not supported; the SPIR-V 1.4 extensionless path is unavailable. |
| (all modes, `vulkan1_2` family) | Device is not Vulkan 1.2; the core extensionless path is unavailable. |
| (all cases) | Common infrastructure: SPIR-V 1.4 build options not applied, SSBO descriptor binding broken, or `verifyOutput` epsilon too tight. |

### Cause Analysis

#### Extensionless-path rejection of the execution mode

**Possible failure symptoms:** the SPIR-V module is rejected at shader-module creation or pipeline creation with a validation error naming the capability or execution mode (e.g., `DenormPreserve`, `RoundingModeRTZ`). The shader never runs, so `verifyOutput` either reports a zero output buffer or is never reached.

**Possible implementation causes:** the driver or validator does not accept the float-control capability or execution mode on the extensionless path. For the `spirv1p4` family, this means the SPIR-V 1.4 surface is not properly enabled even though `VK_KHR_spirv_1_4` is advertised. For the `vulkan1_2` family, the device may report Vulkan 1.2 but not actually promote the SPIR-V 1.4 float-control tokens. A failure that is specific to one mode (e.g., only `RoundingModeRTZ` is rejected) points to a per-mode validator gap; a failure across all five modes points to a missing SPIR-V 1.4 enablement. Pinning the exact cause needs source-level investigation of the driver's SPIR-V 1.4 handling.

#### Advertised-property observability limitation

**Possible failure symptoms:** the shader compiles and runs, but `verifyOutput` reports mismatches between the output and the negated input. The test's input range and sole arithmetic instruction (`OpFNegate` on `%f32`) do not provide a result oracle for any declared float-control mode, so such a mismatch does not demonstrate that the advertised property was not honored.

**Possible implementation causes:** the device advertises the per-width/mode boolean in `VkPhysicalDeviceFloatControlsProperties` as `VK_TRUE`, so `getFloatControlsProperty()` lets the case run, but the compiler lowers the execution mode as a no-op. This test cannot detect that condition through `verifyOutput`: the body uses `%f32` for every case, the `fp16`/`fp64` execution modes target widths the body does not exercise, and `OpFNegate` on normal floats in [1.0, 100.0] should produce the same negated result for all five modes. A value mismatch instead indicates a separate issue in the simple compute path (for example, code generation, storage access, dispatch, or result checking); source-level investigation is needed to localize it.

#### Per-width feature gate failure

**Possible failure symptoms:** every `fp16` case (or every `fp64` case) across all five modes and both version paths is skipped with `NotSupportedError`, while `fp32` cases run. These feature gates are prerequisites for declaring the corresponding execution-mode width; the shader's SSBO data path remains `%f32` in every case.

**Possible implementation causes:** the device does not support `shaderFloat16` + `VK_KHR_shader_float16_int8` (for `fp16`) or `shaderFloat64` (for `fp64`), so `checkSupport()` correctly skips them. Because all arithmetic and SSBO accesses use `%f32`, a `verifyOutput` mismatch is not evidence of a 16-bit or 64-bit storage-lowering defect; it indicates a separate issue in the common compute path. The `fp32` cases need no extra float feature, so they isolate the extensionless-path question from the per-width feature question.

#### Common infrastructure failure

**Possible failure symptoms:** every case in the file fails at the same step (shader-module creation, pipeline creation, or `verifyOutput`), regardless of mode, width, or version path.

**Possible implementation causes:** the SPIR-V 1.4 build options were not applied, the SSBO descriptor binding is broken, the `verifyOutput` epsilon is too tight for the input range, or the compute-shader framework itself misconfigured the dispatch. A whole-file failure should be investigated at the infrastructure level before looking at per-mode or per-width causes.

## Case Pruning

### Requirement-based pruning

- All cases require either `VK_KHR_spirv_1_4` (the `spirv1p4` family) or Vulkan 1.2 (the `vulkan1_2` family), checked in [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L206-L216). Devices without either path skip every case in the corresponding family.
- `fp16` cases require `VK_KHR_shader_float16_int8` plus the `shaderFloat16` feature bit, checked in [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L218-L224). Devices without 16-bit float support skip the 15 `fp16_*` cases in each family.
- `fp64` cases require the `shaderFloat64` core feature, checked in [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L226-L229). Devices without 64-bit float support skip the 15 `fp64_*` cases in each family.
- `fp32` cases need no extra float feature; they run whenever the extensionless path is available.
- Every case queries the matching per-width/mode boolean in `VkPhysicalDeviceFloatControlsProperties` through [`getFloatControlsProperty()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L231-L232) and throws `NotSupportedError` when the boolean is `VK_FALSE`. This prunes unsupported width/mode combinations before they can fail.

### Design-based pruning

- The matrix is the full cross product of 2 version paths × 3 widths × 5 modes = 30 cases. No combinations are excluded by design.
- The shader body is fixed across all cases; only `OpCapability <featureName>` and `OpExecutionMode %main <featureName> <fpWideness>` vary. There is no separate shader for `fp16` or `fp64`; the width only changes the declared execution-mode target.

## Key Takeaways

- The file builds SPIR-V assembly text directly in a C++ string template; it is not an Amber dispatcher. The template is parameterized by `featureName` and `fpWideness`; only `OpCapability <featureName>` and `OpExecutionMode %main <featureName> <fpWideness>` vary across the 30 cases.
- The test is a smoke test for acceptance of the five float-control execution modes on the extensionless path (`VK_KHR_spirv_1_4` or Vulkan 1.2), without declaring `VK_KHR_shader_float_controls`.
- The shader body always uses `%f32`; the `fpWideness` value only reaches `OpExecutionMode`, while `OpCapability` receives only the feature name. For `fp16` and `fp64` cases, the execution mode targets a width the shader body does not exercise arithmetically.
- `fp32` cases need no extra float feature and isolate the extensionless-path question; `fp16` and `fp64` cases layer additional feature gates on top.
- See `## Failure Meaning` for the failure interpretation: a rejection at shader-module creation points to the extensionless path not being enabled; a `verifyOutput` mismatch indicates a separate issue in the common `%f32` compute path and does not establish a float-control or 16-bit/64-bit storage defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `getComputeSourceCode()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L51-L84`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L51-L84) | Builds the SPIR-V assembly string template parameterized by feature name and width. |
| `getComputeShaderSpec()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L86-L112`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L86-L112) | Builds the 64-element random input/output buffers and wires `verifyOutput`. |
| `getFloatControlsProperty()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L114-L170`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L114-L170) | Per-width/mode property query used to prune unsupported combinations. |
| `SpvAsmFloatControlsExtensionlessCase::initPrograms()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L195-L203`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L195-L203) | Adds the assembly with `SpirVAsmBuildOptions(..., SPIRV_VERSION_1_4, allowSpirv14=true)`. |
| `SpvAsmFloatControlsExtensionlessCase::checkSupport()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L206-L233`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L206-L233) | The two extensionless-path gates plus per-width feature gates. |
| `createFloatControlsExtensionlessGroup()` | [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L280`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L280) | Registers the 30 cases (2 paths × 3 widths × 5 modes). |
| `getComputeAsmShaderPreamble()` | [`vktSpvAsmComputeShaderTestUtil.cpp#L65-L73`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L65-L73) | Provides the SPIR-V preamble (capabilities, memory model, entry point, local size). |
| `getComputeAsmCommonTypes()` | [`vktSpvAsmComputeShaderTestUtil.cpp#L82-L100`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L82-L100) | Provides the common type declarations (`%f32`, `%uvec3`, etc.). |
| `getComputeAsmInputOutputBuffer()` | [`vktSpvAsmComputeShaderTestUtil.cpp#L109-L121`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L109-L121) | Provides the input/output SSBO variable declarations. |
| `getComputeAsmInputOutputBufferTraits()` | [`vktSpvAsmComputeShaderTestUtil.cpp#L123-L133`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L123-L133) | Provides the SSBO decorations (Block, DescriptorSet, Binding, ArrayStride, Offset). |
| `verifyOutput()` | [`vktSpvAsmComputeShaderTestUtil.cpp#L135-L140`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L135-L140) | Host-side pass/fail check with `epsilon = 0.001`. |
| Mustpass entry range | [`spirv-assembly.txt#L6476-L6505`](../../../mustpass/main/vk-default/spirv-assembly.txt#L6476-L6505) | Mirrors the 30 registered `dEQP-VK.spirv_assembly.instruction.compute.float_controls_extensionless.*` case paths. |
