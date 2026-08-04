# Understanding Brief: spirv_assembly.instruction.compute.float_controls_extensionless

## One-Sentence Test Purpose

This test checks that the five SPIR-V float-control execution modes (`DenormPreserve`, `DenormFlushToZero`, `SignedZeroInfNanPreserve`, `RoundingModeRTE`, `RoundingModeRTZ`) are accepted and run by the implementation **without** declaring the `VK_KHR_shader_float_controls` extension, by relying on either the `VK_KHR_spirv_1_4` extension or the Vulkan 1.2 core path.

## Background Knowledge

### SPIR-V float-control execution modes

SPIR-V defines five execution modes that control how the implementation handles floating-point edge cases for a given bit width:

- `DenormPreserve` — denormals must be preserved rather than flushed to zero.
- `DenormFlushToZero` — denormals must be flushed to zero.
- `SignedZeroInfNanPreserve` — the sign of zero and the encoding of infinities and NaNs must be preserved.
- `RoundingModeRTE` — round to nearest even.
- `RoundingModeRTZ` — round toward zero.

Each mode is declared per entry point with a target width (16, 32, or 64): `OpExecutionMode %main DenormPreserve 32`. The matching `OpCapability` (e.g., `OpCapability DenormPreserve`) must also be present.

Why it matters here:
- These are the exact tokens the test inserts into the SPIR-V assembly template.
- Each width/mode combination has a separate device-side property in `VkPhysicalDeviceFloatControlsProperties` that must be `VK_TRUE` for the case to run.

### Extensionless path: `VK_KHR_spirv_1_4` vs Vulkan 1.2

The `VK_KHR_shader_float_controls` extension was the original way to expose these capabilities on Vulkan 1.0/1.1. Vulkan 1.2 and `VK_KHR_spirv_1_4` promote the SPIR-V 1.4 surface (which includes the float-control execution modes as core) so that the extension is no longer required.

Why it matters here:
- The `spirv1p4` family enables SPIR-V 1.4 via `VK_KHR_spirv_1_4` on a Vulkan 1.1 device.
- The `vulkan1_2` family relies on Vulkan 1.2 core support.
- The test deliberately omits `VK_KHR_shader_float_controls` from the extension list to prove the extensionless path works.

### `VkPhysicalDeviceFloatControlsProperties` per-width gating

Even when the extensionless path is available, the implementation advertises per-width, per-mode support booleans (`shaderDenormPreserveFloat16`, ..., `shaderRoundingModeRTZFloat64`). The test queries these in `getFloatControlsProperty()` and throws `NotSupportedError` when the relevant boolean is false, so unsupported combinations are skipped rather than failing.

## One Concrete Example

Representative case: `dEQP-VK.spirv_assembly.instruction.compute.float_controls_extensionless.spirv1p4.fp32_denorm_preserve`.

The C++ builder in `getComputeSourceCode()` produces a compute SPIR-V module whose only float-control-specific lines are:

```llvm
OpCapability DenormPreserve
...
OpExecutionMode %main DenormPreserve 32
```

The shader body itself is width-agnostic: it loads a 32-bit float from an input SSBO, applies `OpFNegate`, and stores the result to an output SSBO. The `fpWideness` value (here `32`) only reaches the `OpCapability` and `OpExecutionMode` lines; the actual compute operations always use `%f32`. This makes the test a smoke test for acceptance of the execution mode, not a behavioral test of the float-control property.

## End-to-End Test Flow

```text
[host] createFloatControlsExtensionlessGroup() registers 30 cases: 2 version paths × 3 widths × 5 modes
[host] For each case, SpvAsmFloatControlsExtensionlessCase::initPrograms() builds the SPIR-V assembly string
       with OpCapability <featureName> and OpExecutionMode %main <featureName> <fpWideness>, and adds it to
       spirvAsmSources with SpirVAsmBuildOptions(..., SPIRV_VERSION_1_4, allowSpirv14=true)
[host] checkSupport(): if spirv14, require VK_KHR_spirv_1_4; else require Vulkan 1.2
[host] checkSupport(): if fpWideness==16, require VK_KHR_shader_float16_int8 + shaderFloat16 feature
[host] checkSupport(): if fpWideness==64, require shaderFloat64 core feature
[host] checkSupport(): getFloatControlsProperty() queries VkPhysicalDeviceFloatControlsProperties and throws
       NotSupportedError if the per-width/mode boolean is VK_FALSE
[host] SpvAsmFloatControlsExtensionlessInstance builds ComputeShaderSpec: 64 random floats in [1.0, 100.0]
       seeded by deStringHash(testCaseName) + baseSeed; expected outputs are the negated inputs
[host] Compute pipeline is created with the assembled SPIR-V; dispatch numWorkGroups = (64, 1, 1)
[device] Each invocation loads input[x], applies OpFNegate, stores to output[x]
[host] verifyOutput() compares output floats against expected (negated input) with epsilon 0.001
[host] Pass if every element matches within epsilon; otherwise fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly string built by `getComputeSourceCode()` in [`vktSpvAsmFloatControlsExtensionlessTests.cpp#L51-L84`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L51-L84). The template is parameterized by `featureName` (the SPIR-V capability/execution-mode name) and `fpWideness` (16, 32, or 64).
- `SpirVAsmBuildOptions(programCollection.usedVulkanVersion, SPIRV_VERSION_1_4, allowSpirv14=true)` applied in [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L195-L203). This tells the CTS shader builder to assemble and validate the text as SPIR-V 1.4.
- Helper fragments from `vktSpvAsmComputeShaderTestUtil.cpp` provide the preamble (`OpCapability Shader`, memory model, entry point), common types (`%f32`, `%uvec3`, etc.), and the input/output SSBO declarations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO (`%indata`) | Host, 64 random floats in [1.0, 100.0] | Descriptor set 0, binding 0, `StorageBuffer` | Read by compute shader | No (compared via output) | Provides the per-invocation float input. |
| Output SSBO (`%outdata`) | Host, zero-initialized | Descriptor set 0, binding 1, `StorageBuffer` | Written by compute shader | Yes, via `verifyOutput` | Receives the negated input; checked element-by-element. |
| `gl_GlobalInvocationID` built-in | Driver | Input | Read by compute shader | No | Selects the per-invocation array index. |

## What Is Checked

- The compute shader compiles and runs with the declared `OpCapability <featureName>` and `OpExecutionMode %main <featureName> <fpWideness>`.
- The output SSBO contains the negated input values within `epsilon = 0.001` (see `verifyOutput` in `vktSpvAsmComputeShaderTestUtil.cpp`).
- 64 elements are checked independently per case.
- The check is host-side; the device only writes results.

## Behavior Parameter Identification

> **Behavior parameter:** `execution mode` (the float-control feature under test)
>
> **Candidate values:** `denorm_preserve`, `denorm_flush_to_zero`, `signed_zero_inf_nan_preserve`, `rounding_mode_rte`, `rounding_mode_rtz`

Secondary axes:
- `spirv_version_path`: `spirv1p4`, `vulkan1_2` — selects the extensionless mechanism (VK_KHR_spirv_1_4 vs Vulkan 1.2 core).
- `float_width`: 16, 32, 64 — selects the target width for the execution mode.

The execution mode is the primary axis because it is the float-control property being accepted. The float width is a secondary axis that changes the `OpExecutionMode` target. The version path is a configuration dimension that changes the API entry point but not the SPIR-V behavior.

## What Failure Means

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

## Important Variations and Special Cases

- **Width-mode decoupling in the shader body.** The `fpWideness` value only reaches `OpCapability` and `OpExecutionMode`. The shader body always operates on `%f32`. This is intentional: the test verifies acceptance of the execution mode declaration, not that the mode changes the result of `OpFNegate` on a 32-bit float. For `fpWideness=16` and `fpWideness=64`, the execution mode targets a width that the shader body does not exercise arithmetically.
- **Two extensionless paths.** `spirv1p4` and `vulkan1_2` register the same 15 case names but differ in `checkSupport()`: the former requires `VK_KHR_spirv_1_4`, the latter requires Vulkan 1.2. The SPIR-V assembly and build options are identical.
- **Per-width feature gates layer on top.** `fp16` cases add `VK_KHR_shader_float16_int8` + `shaderFloat16`; `fp64` cases add `shaderFloat64`. `fp32` cases need no extra float feature.
- **Per-width/mode property query.** `getFloatControlsProperty()` reads `VkPhysicalDeviceFloatControlsProperties` and throws `NotSupportedError` when the specific boolean is false. This is the gate that prunes unsupported width/mode combinations before they can fail.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
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

## Questions / Risk Points for User Audit

- Is the smoke-test characterization correct? The shader body uses `%f32` regardless of `fpWideness`, so the test validates acceptance of the execution mode declaration rather than its behavioral effect on the target width.
- Is the primary behavioral axis (execution mode) the right choice, or should the float width be the primary axis instead?
- The `vulkan1_2` and `spirv1p4` families register identical case names. Is it clear that they differ only in the `checkSupport()` path?
- Are the per-width feature gates (`shaderFloat16`, `shaderFloat64`) correctly attributed to the `fp16` and `fp64` cases only?

## Conversion Notes for Final Wiki Rewrite

- The `## Background Knowledge` distillation should keep the SPIR-V float-control execution-mode overview (one bullet per mode is too dense; a compact list with the five mode names and a one-line characterization each is enough) and the extensionless-path concept (VK_KHR_spirv_1_4 vs Vulkan 1.2). The `VkPhysicalDeviceFloatControlsProperties` per-width gating belongs in `## Case Pruning`, not Background Knowledge.
- The concrete example becomes the representative walkthrough under `## Shader Analysis`. The extracted SPIR-V assembly goes under `#### Source Code` (unfoldable) per the TEMP-SPIRV-ASSEMBLY deviation. The `#### SPIR-V` subsection is omitted.
- The `### Failure Cause Mapping` table is copied directly into the final page.
- The width-mode decoupling point is important enough to surface in `## Behavior Parameters` and `## Key Takeaways`, not just here.
- The old wiki page misspells the registered name as `float_control_extensionless` (singular). The actual registered name is `float_controls_extensionless` (plural). The rewrite uses the exact registered identifier.
