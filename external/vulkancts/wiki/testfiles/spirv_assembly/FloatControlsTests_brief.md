# Understanding Brief: `spirv_assembly.instruction.compute.float_controls` and `spirv_assembly.instruction.graphics.float_controls`

## One-Sentence Test Purpose

This test checks whether the implementation correctly honors the `VK_KHR_shader_float_controls` execution modes — denorm preserve/flush-to-zero, signed zero/inf/NaN preservation, and RTE/RTZ rounding modes — across FP16, FP32, and FP64 operations, and whether different float widths can be controlled independently within a single shader.

## Background Knowledge

### `VK_KHR_shader_float_controls` execution modes

The extension exposes SPIR-V execution modes that let a shader module dictate floating-point behavior the implementation must obey, instead of leaving it implementation-defined. The modes tested here are:

- `DenormPreserve` / `DenormFlushToZero`: whether subnormal (denormalized) operands and results are kept or flushed to zero.
- `SignedZeroInfNanPreserve`: whether the signs of zero, infinities, and NaN payloads are preserved through operations.
- `RoundingModeRTE` / `RoundingModeRTZ`: round-to-nearest-even versus round-toward-zero for operations whose precision is narrower than the source.

Each mode is parameterized by a bit width (16, 32, or 64). The implementation advertises, via `VkPhysicalDeviceFloatControlsProperties`, which modes it supports per width, and whether the modes for different widths can be set independently (`VK_SHADER_FLOAT_CONTROLS_INDEPENDENCE_ALL`, `INDEPENDENCE_32_BIT_ONLY`, or `NONE`).

Why it matters here:
- The test sets the execution mode in the SPIR-V module *and* mirrors the expected property in `VkPhysicalDeviceFloatControlsProperties` so the CTS support check gates the case.
- The pass/fail logic depends on the mode actually taking effect at the precision the mode targets, not on a generic epsilon.

### SPIR-V assembly authored in C++ string templates

Like the rest of the `spirv_assembly` category, this file builds shader modules from SPIR-V assembly text concatenated from C++ string fragments via `tcu::StringTemplate`. There is no GLSL or HLSL source; the assembly is the source of truth. Two top-level templates exist:

- `m_operationShaderTemplate`: a single-invocation compute shader that loads (or generates) two float operands, runs one tested operation, and stores the result to an output SSBO.
- `m_settingsShaderTemplate`: a compute shader that performs arithmetic on FP16, FP32, and FP64 values in one invocation, used to verify that different widths can be controlled independently.

Why it matters here:
- The reader should audit the execution-mode declaration and the operand/result types directly in the assembly, not reverse-engineer a GLSL frontend.
- The `${capabilities}`, `${execution_mode}`, `${types}`, `${commands}`, and `${save_result}` template slots are where per-case behavior is injected.

### `ValueId` encoding for expected results

The test does not compare against a host-computed reference float. Instead, every argument and expected result is encoded as a `ValueId` enum token (e.g. `V_DENORM`, `V_NAN`, `V_ZERO_OR_DENORM_TIMES_TWO`). The host constructs the input buffer and the expected output buffer by translating `ValueId`s into the concrete bit pattern for the active float width, and the verifier (`checkFloats`/`checkValue`) decodes the expected `ValueId` from the output buffer and compares bit patterns — with special-case handling for NaN, denorm, and multi-acceptable-result codes.

Why it matters here:
- A single `ValueId` like `V_ZERO_OR_DENORM_TIMES_TWO` expresses "either zero (if the implementation flushed) or twice the denorm (if it preserved)" in one token, so the same case validates both behaviors when only one is legal.
- Failure meaning is tied to which `ValueId` branch mismatched, not to a numeric tolerance.

## One Concrete Example

Consider `dEQP-VK.spirv_assembly.instruction.compute.float_controls.fp32.input_args.add_denorm_preserve`.

The host fills the input SSBO with two copies of the FP32 denorm value encoded by `V_DENORM` (a value just below the smallest normal, constructed as `denormBase - epsilon`). The shader declares `OpCapability DenormPreserve` and `OpExecutionMode %main DenormPreserve 32`, loads both operands, runs `OpFAdd`, and stores the result. Because denorms are preserved, the expected result is `V_DENORM_TIMES_TWO` (the denorm added to itself, still denormal). If the implementation had flushed, the result would be zero — but under `DenormPreserve` that would be a failure.

The output buffer holds the `ValueId`-encoded expected result; `checkFloats<Float32, float>` compares the shader's output bits against the expected bits, with `V_DENORM_TIMES_TWO` resolving to the concrete FP32 bit pattern for twice the denorm.

## End-to-End Test Flow

```text
[host] select VariableType (FP16/FP32/FP64), argument source (input_args/generated_args), OperationId, and BehaviorFlags
[host] look up the Operation's SPIR-V command snippet and the TypeSnippets for the active width
[host] specialize m_operationShaderTemplate: inject capabilities, execution mode, types, SSBO layout, commands, save_result
[host] construct input SSBO from ValueId-encoded arguments (input_args) or leave empty (generated_args)
[host] construct expected output SSBO from the ValueId-encoded expected result
[host] set VkPhysicalDeviceFloatControlsProperties to mirror the requested execution mode
[device] dispatch one workgroup (LocalSize 1 1 1): load operands, run operation, store result
[host] read back output SSBO
[host] checkFloats: decode expected ValueId from expected buffer, compare bit patterns (NaN/denorm/multi-result special cases)
[host] pass/fail
```

For the settings tests the flow is the same, except:

```text
[host] select SettingsMode (SM_ROUNDING or SM_DENORMS), independenceSetting (32_BIT_ONLY or ALL), and per-width options (RTE/RTZ or PRESERVE/FLUSH)
[host] specialize m_settingsShaderTemplate: inject one execution mode per active width, three output SSBOs (one per width)
[host] construct a single input SSBO carrying FP64+FP32+FP16 argument pairs (ordered 64 -> 16 for layout)
[device] dispatch one workgroup: run OpFAdd per width, store each result to its own output SSBO
[host] checkMixedFloats: compare each width's output against its ValueId-encoded expected result
[host] additional property-only case (verifyIndependenceSettings) checks that reported float-controls properties are internally consistent with the advertised independence level
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- **Specialized SPIR-V assembly text** from `m_operationShaderTemplate` (operation tests) or `m_settingsShaderTemplate` (settings tests). Specialization replaces `${capabilities}`, `${extensions}`, `${execution_mode}`, `${annotations}`, `${types}`, `${io_definitions}`, `${constants}`, `${functions}`, `${variables}`, `${arguments}`, `${commands}`, and `${save_result}` slots with per-width and per-operation snippets. No GLSL or HLSL source exists.
- **Per-width `TypeSnippets`**: FP16/FP32/FP64 each contribute their own capability (`StorageUniform16`/`Float64`/none), array stride (2/4/8), type definitions, constant definitions, and load/store snippets. FP16 has a `_nostorage` variant that swaps `StorageUniform16` for `Float16` and bitcasts through `u32` to avoid `VK_KHR_16bit_storage`.
- **`Operation` snippets**: one SPIR-V command string per `OperationId` (e.g. `%result = OpFAdd %type_valueType %arg1 %arg2` for `OID_ADD`), plus annotations/types/constants/functions slots for operations that need extra declarations.
- **Graphics fragment maps**: graphics tests feed the same per-operation snippets through `fragments["capability"]`, `fragments["decoration"]`, `fragments["pre_main"]`, `fragments["testfun"]` into the standard `vktSpvAsmGraphicsShaderTestUtil` vertex/fragment pipeline templates.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO (`%ssbo_in`, binding 0) | yes, filled from `ValueId` arguments | yes, descriptor set 0 binding 0 | read by shader (input_args only) | no | Carries the two operands for the tested operation; empty for generated_args. |
| Output SSBO (`%ssbo_out`, binding 1) | yes, allocated and filled with expected `ValueId` result | yes, descriptor set 0 binding 1 | written by shader | yes | Receives the operation result; the host compares its contents against the expected buffer. |
| Settings input SSBO (`%ssbo_in`, binding 0) | yes, packs FP64+FP32+FP16 argument pairs | yes, descriptor set 0 binding 0 | read by shader | no | Single buffer carries operands for all three widths, ordered 64 -> 16 for storage layout rules. |
| Settings output SSBOs (`%ssbo_*_out`, bindings 1-3) | yes, one per active width | yes, descriptor set 0 bindings 1-3 | written by shader | yes | One result slot per width so independence can be observed per width. |
| Graphics color attachments | yes | yes | read/written by fixed function + shader | yes (compared) | Drive the vertex/fragment pipeline so the per-stage `testfun` runs once. |

## What Is Checked

- The output SSBO byte pattern is compared against the `ValueId`-encoded expected buffer via `checkFloats<FloatType, UintType>`. Comparison is bit-exact for normal values, with special-case handling for:
  - `V_NAN`: any NaN bit pattern passes;
  - `V_DENORM`: any denormal bit pattern passes;
  - `V_ZERO_OR_MINUS_ZERO`, `V_ZERO_OR_ONE`, `V_ZERO_OR_DENORM_TIMES_TWO`, etc.: multiple acceptable bit patterns pass (these encode "either behavior is legal here");
  - trig/log/sqrt result codes: a precision-aware helper accepts results within a tolerance band.
- Settings tests use `checkMixedFloats`, which dispatches per-width comparison based on a `BufferDataType` tag carried in each expected resource.
- A separate property-only case `independence_settings` (no shader) calls `verifyIndependenceSettings`, which queries `VkPhysicalDeviceFloatControlsProperties` and checks that the reported per-width support bits are internally consistent with the advertised `roundingModeIndependence` / `denormBehaviorIndependence` level (e.g. under `INDEPENDENCE_NONE`, all three widths must report the same support for each mode).
- The check runs on the host; the device only produces the output buffer.

## Behavior Parameter Identification

> **Behavior parameter:** the test family / behavioral group, because the file groups structurally different behaviors under one source file.
>
> **Candidate values:** `fp16` / `fp32` / `fp64` operation tests (per-width operation matrix), `independence_settings` (cross-width independence), graphics `fp16` / `fp32` / `fp64` (same operations through vertex/fragment pipelines).

A secondary axis within the operation families is the `BehaviorFlags` value: `denorm_preserve`, `denorm_flush_to_zero`, `signed_zero_preserve` / `inf_preserve` / `nan_preserve` / `signed_inf_preserve` (all under `B_ZIN_PRESERVE`), and `rte_rounding` / `rtz_rounding`. A third axis is the argument source: `input_args` versus `generated_args`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fp16` / `fp32` / `fp64` operation tests (denorm preserve/flush) | Implementation did not honor `DenormPreserve`/`DenormFlushToZero` for the tested width; denorms were flushed when they should be preserved or vice versa. |
| `fp16` / `fp32` / `fp64` operation tests (signed zero/inf/NaN preserve) | Implementation did not preserve sign of zero, infinity, or NaN payload through the tested operation. |
| `fp16` / `fp32` / `fp64` operation tests (rounding RTE/RTZ) | Implementation used the wrong rounding mode for a narrowing conversion or spec-constant op, or ignored `FPRoundingMode` decoration on `OpFConvert`/`OpStore`. |
| `independence_settings` (rounding or denorm) | Implementation applied one width's execution mode to another width, or could not sustain different modes per width when the advertised independence level claimed it could. |
| `independence_settings` (property-only case) | Reported `VkPhysicalDeviceFloatControlsProperties` are internally inconsistent with the advertised independence level. |
| Graphics `fp16` / `fp32` / `fp64` (`_vert` / `_frag`) | Same causes as compute, but surfaced through the vertex or fragment stage pipeline; vertex additionally skips `FPRoundingMode`-decorated cases that SSBO writes cannot express. |

## Important Variations and Special Cases

- **`input_args` vs `generated_args`**: `input_args` reads operands from the input SSBO; `generated_args` constructs operands as SPIR-V constants via `valueIdToSnippetArgMap` (e.g. `V_DENORM` becomes `OpFSub %type_f32 %c_f32_denorm_base %c_f32_eps`). The `generated_args` path cannot exercise `DenormPreserve` for operations Vulkan already guarantees preserve denorms (`OpPhi`, `OpSelect`, `OpReturnValue`, `OpVectorExtractDynamic`, `OpVectorInsertDynamic`, `OpVectorShuffle`, `OpCompositeConstruct`, `OpCompositeInsert`, `OpTranspose`, `OpCopy`), so the extension is skipped for those.
- **`_nostorage` FP16 variant**: FP16 tests have a parallel set that drops `VK_KHR_16bit_storage` and uses `VK_KHR_shader_float16_int8`'s `shaderFloat16` feature instead, bitcasting FP16 through `u32` for SSBO transport. The test name appends `_nostorage`.
- **Rounding override tests**: `rounding_rte_override_from_fp32_*` and `rounding_rtz_override_from_fp32_*` use `OpDecorate %result FPRoundingMode RTE|RTZ` on an `OpFConvert` from FP32 to FP16 to check that the per-instruction decoration overrides the module-wide execution mode. These are skipped for the vertex stage because SSBO writes do not support `FPRoundingMode` in the required storage class.
- **Spec-constant conversion tests**: `sconst_conv_from_fp32_*` use `OpSpecConstantOp ... FConvert` with raw integer literal words (`!` injection) to verify rounding on spec-constant operations.
- **Graphics settings are a no-op**: the working group decided compute-only testing is sufficient for independence settings, so `GraphicsTestGroupBuilder::createSettingsTests` is intentionally empty.
- **Pack/Unpack operations**: `PackHalf2x16`, `UnpackHalf2x16`, `PackDouble2x32`, `UnpackDouble2x32` have special-case result codes and, for `UnpackHalf2x16`, the float-controls width is forced to 16 even though the output is FP32.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main registration | [createFloatControlsTestGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383-L5410) | Creates `fp16`/`fp32`/`fp64` operation groups and calls `createSettingsTests`. |
| Operation compute template | [m_operationShaderTemplate](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3978-L4044) | The compute shader string template for all operation tests. |
| Settings compute template | [m_settingsShaderTemplate](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4046-L4099) | The compute shader string template for independence settings tests. |
| Settings test case list | [ComputeTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4130-L4269) | Enumerates all independence_settings cases and the property-only case. |
| Operation test creation | [ComputeTestGroupBuilder::createOperationTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4102-L4128) | Builds per-operation compute cases. |
| Operation shader spec fill | [ComputeTestGroupBuilder::fillShaderSpec(OperationTestCaseInfo)](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4271-L4460) | Specializes the operation template and sets up buffers/features. |
| Settings shader spec fill | [ComputeTestGroupBuilder::fillShaderSpec(SettingsTestCaseInfo)](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4462-L4554) | Specializes the settings template, picks per-width execution modes and expected results. |
| Behavior to capability map | [getBehaviorCapabilityAndExecutionMode()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3793-L3818) | Translates `BehaviorFlags` into `OpCapability` + `OpExecutionMode` strings. |
| Float-controls property setup | [setupFloatControlsProperties()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3820-L3849) | Mirrors requested execution modes into `VkPhysicalDeviceFloatControlsProperties`. |
| Property consistency check | [verifyIndependenceSettings()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3878-L3960) | Property-only case that validates reported support bits against the independence level. |
| Result verification | [checkValue()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3440-L3530), [checkFloats()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3532-L3549) | `ValueId`-decoded bit comparison with NaN/denorm/multi-result handling. |
| Mixed-width verification | [checkMixedFloats()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3551-L3570) | Per-width dispatch for settings tests. |
| Operation map | [createOperationMap()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L2142-L2650) | SPIR-V command snippets per `OperationId`. |
| BehaviorFlags enum | [BehaviorFlagBits](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L109-L116) | The five tested float-control behaviors. |
| ValueId enum | [ValueId](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L122-L276) | Encoded argument/result values. |
| Graphics builder no-op settings | [GraphicsTestGroupBuilder::createSettingsTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4972-L4977) | Documents the compute-only decision for settings. |
| Graphics instance context | [GraphicsTestGroupBuilder::createInstanceContext()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4979-L5379) | Builds the graphics pipeline context for vertex/fragment operation tests. |

## Questions / Risk Points for User Audit

- Is the three-family behavioral grouping (per-width operation tests, independence settings, graphics operation tests) the right primary axis, or should the `BehaviorFlags` dimension lead instead?
- Is one operation-test walkthrough (FP32 `input_args` `add_denorm_preserve`) sufficient, or should a second walkthrough cover an `independence_settings` case to expose the multi-width template?
- Are the graphics-only pruning rules (vertex skips `FPRoundingMode`-decorated cases; settings are compute-only) clearly separated from the compute behavior?
- Is the `ValueId` multi-acceptable-result handling (e.g. `V_ZERO_OR_DENORM_TIMES_TWO`) explained at the right depth, or does it need a dedicated table?

## Conversion Notes for Final Wiki Rewrite

- The `VK_KHR_shader_float_controls` execution-mode explanation should be distilled to a short `## Background Knowledge` bullet list; the full teaching scaffolding stays in the brief.
- The `ValueId` encoding concept is page-local prerequisite and should appear in `## Background Knowledge` condensed to one bullet.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`.
- The representative walkthrough should be the FP32 `input_args` `add_denorm_preserve` operation case; a second walkthrough for an `independence_settings` rounding case is justified because the settings template is structurally different (multi-width, separate template, separate verifier).
- The concrete example above should become the operation-test walkthrough; the settings-test walkthrough should be drawn from the `rounding_ind_all_fp16_rte_fp32_rtz` case (simplest two-width rounding case).
- Source-mapping table becomes the `## Source Reference Appendix`.
