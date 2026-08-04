# Understanding Brief: `float_controls2` test family in `spirv_assembly`

## One-Sentence Test Purpose

This test family checks whether a Vulkan implementation honors `SPV_KHR_float_controls2` `FPFastMathMode` decorations and `OpExecutionModeId FPFastMathDefault` execution modes by producing the IEEE-correct result for whichever fast-math bits are *absent* from a given test case.

## Background Knowledge

### `VK_KHR_shader_float_controls2` and `SPV_KHR_float_controls2`

`VK_KHR_shader_float_controls2` exposes the SPIR-V `SPV_KHR_float_controls2` extension. It lets a shader author attach an `FPFastMathMode` mask to either an entire function (via `OpExecutionModeId ... FPFastMathDefault`) or to a single result ID (via `OpDecorate %id FPFastMathMode <bits>`). The mask tells the compiler which IEEE-754 guarantees it may relax: `NotNaN` (operands are not NaN), `NotInf` (operands are not Inf), `NSZ` (signed zeros may be flushed), `AllowRecip` (reciprocal may be approximate), `AllowContract` (FMA contraction allowed), `AllowReassoc` (reassociation allowed), and `AllowTransform` (further transforms allowed; requires `AllowReassoc | AllowContract`).

Why it matters here:

- Every test in this family applies an `FPFastMathMode` mask that is the **inverse** of one or more "tested flag bits" so that the case actually exercises the absence of those bits.
- A test named `testedWithout_NSZ` therefore applies `allBits & ~NSZ` — i.e. everything is allowed *except* flushing signed zeros, so signed zeros must be preserved.

### Two application points: execution mode vs. per-result decoration

Each `(operation, flag, args)` row in the test matrix is generated twice:

- `_exec` variant: the mask is applied as the function-wide `OpExecutionModeId %main FPFastMathDefault %type_fN %bc_u32_fp_exec_mode`. No per-result `FPFastMathMode` decoration is emitted.
- `_deco` variant: the function-wide default is set to `allBits` (everything allowed) and the same mask is attached with `OpDecorate %result FPFastMathMode <bits>` to the result ID of the tested operation.

Why it matters here:

- Both variants must produce identical results for the test to pass. A divergence between `_exec` and `_deco` for the same logical mask isolates a bug in the decoration handling rather than in the fast-math semantic itself.

## One Concrete Example

Consider the registered case `dEQP-VK.spirv_assembly.instruction.compute.float_controls2.fp32.input_args.add_testedWithout_NSZ_arg1_minusZero_arg2_one_res_one_deco`:

- Float type: `FP32` (no extra features needed beyond `shaderFloatControls2`).
- Operation: `OID_ADD` — `%result = OpFAdd %type_f32 %arg1 %arg2`.
- Inputs: `arg1 = -0.0`, `arg2 = 1.0`, read from a 2-element SSBO at descriptor set 0, binding 0.
- Tested flag bits: `FP::NSZ` — the case is named `testedWithout_NSZ` because the actual mask applied is `allBits & ~NSZ = 127 & ~4 = 123 = 0x7B`.
- Application point: `_deco` — function-wide default is `allBits` (127), and `OpDecorate %result FPFastMathMode NotNaN|NotInf|AllowRecip|AllowContract|AllowReassoc|AllowTransform` is attached to `%result`.
- Expected output: `+1.0` stored into a 1-element output SSBO at binding 1.

The expectation is `+1.0` regardless of NSZ, but the test exists to confirm that the absence of `NSZ` does not cause the implementation to produce a sign-flipped result, drop the operation, or reject the shader.

## End-to-End Test Flow

```text
[host] choose FloatType (FP16/FP32/FP64), OperationId, and testedFlagBits from thetestCaseInputs table
[host] compute behaviorFlagsExecMode and behaviorFlagsDecoration via invert(testedFlagBits) and useDecorationFlags
[host] specialize the compute (or vertex+fragment) SPIR-V template with capabilities, decorations, types, arguments, commands, and save_result snippets
[host] construct input SSBO with two ValueId-encoded floats and output SSBO sized to hold the ValueId-encoded expected result
[host] request SPIR-V 1.2 and VK_KHR_shader_float_controls2 plus per-type features (shaderFloat64 for FP64, shaderFloat16 / 16bit_storage for FP16, fragmentStoresAndAtomics for graphics)
[device] compute shader: load %arg1, %arg2 from input SSBO, run operation, store %result to output SSBO
[host] read back output SSBO and call checkFloats<Float16/Float32/Float64>() to compare against the ValueId-encoded expected result
[host] pass if the returned bits match the expected ValueId (or fall within the multi-acceptable-result / ULP tolerance rules)
```

Graphics tests add a vertex+fragment pipeline stage: the tested operation runs in either vertex or fragment, the vertex stage passes its result to fragment via a bitcast varying (because the design forbids SSBO writes from the vertex stage), and the fragment stage writes the result to the output SSBO.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- A compute SPIR-V assembly string built by `StringTemplate::specialize()` over the `m_operationShaderTemplate` skeleton in `ComputeTestGroupBuilder::init()`.
- For graphics, a vertex and a fragment SPIR-V assembly string built from `vertexTemplate` and `fragmentTemplate` in `getGraphicsShaderCode()`.
- Both shaders always carry `OpCapability FloatControls2`, `OpExtension "SPV_KHR_float_controls2"`, `OpExecutionModeId %main FPFastMathDefault %type_fN %bc_u32_fp_exec_mode`, and (in `_deco` cases only) `OpDecorate %result FPFastMathMode <bits>`.
- `RoundingModeRTE` capability + `SPV_KHR_float_controls` extension + `OpExecutionMode %main RoundingModeRTE <width>` are appended when a case sets `requireRte = true`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO (`%ssbo_in`, binding 0) | yes — `TypeValues::constructInputBuffer()` fills 2 floats | yes — `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` | yes — `OpLoad %arg1/%arg2` | no | Carries the two ValueId-encoded operands to the shader |
| Output SSBO (`%ssbo_out`, binding 1) | yes — `TypeValues::constructOutputBuffer()` stores the ValueId-encoded expected result as raw bytes | yes — `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` | yes — `OpStore %result` | yes — host compares bytes | Carries the result back; the host reads the ValueId back out and resolves it against `expectedOutput` |
| `%bc_u32_fp_exec_mode` constant | generated in SPIR-V | n/a (compile-time constant) | n/a | n/a | The function-wide `FPFastMathDefault` mask, always present |
| Vertex↔fragment varying (`%BP_vertex_result`) | yes — for graphics cases | yes — vertex output / fragment input | yes — vertex bitcasts and stores, fragment bitcasts and loads | no | Required because SSBO writes are forbidden in the vertex stage; carries the result across stages |

## What Is Checked

- The output SSBO is read back byte-for-byte and compared by `compareBytes<TYPE, FLOAT_TYPE>()` against a buffer that holds the `ValueId` of the expected result reinterpreted as the float type's raw bits.
- Special expected values resolve multiple acceptable results:
  - `V_SIGN_NAN`: any of `-1, -0, +0, +1` passes.
  - `V_ZERO_OR_MINUS_ZERO`: either signed zero passes.
  - `V_ZERO_OR_ONE`: either `0` or `1` passes.
  - `V_ONE_OR_NAN`: either `1` or any NaN passes.
  - `V_TRIG_ONE`: absolute-error tolerance `2^-11` (FP32) or `2^-7` (FP16) around `1.0`.
  - `V_PI`, `V_MINUS_PI`, `V_PI_DIV_2`, `V_MINUS_PI_DIV_2`, `V_PI_DIV_4`, `V_MINUS_PI_DIV_4`, `V_3_PI_DIV_4`, `V_MINUS_3_PI_DIV_4`: ULP-bounded tolerance around the trig constant (4096 ULP for FP32, 5 ULP for FP16).
- Cases with `expectedOutput == V_UNUSED` are skipped at registration time and never produce a test case.
- Graphics tests additionally require `fragmentStoresAndAtomics` so the fragment shader can write the output SSBO.

## Behavior Parameter Identification

> **Behavior parameter:** `testedFlagBits` — the `spv::FPFastMathModeMask` value whose absence is being verified by the test case.
>
> **Candidate values:** `None`, `NSZ`, `NotInf`, `NotNaN`, `AllowRecip`, `AllowContract`, `AllowReassoc`, `AllowTransform`, plus the combined masks used by `OID_FMA2PT58` (`AllowContract`), `OID_SZ_FMA` (`AllowContract | NSZ`), `OID_ADD_SUB_REASSOCIABLE` (`AllowReassoc | NotInf`), and the combined `NotNaN | NotInf` rows used by ops where both must be absent.

The float type (FP16/FP32/FP64), the operation, and the application point (`_exec` vs `_deco`) are parameter dimensions that change the assembly and resources but do not change *which fast-math property is being tested*. They are covered under `## Parameter Dimensions and Observed Values`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `NSZ` (testedWithout_NSZ) | Signed-zero preservation: implementation flushes `-0`/`+0` to a single sign when `NSZ` is not allowed. |
| `NotNaN` (testedWithout_NotNaN) | NaN preservation: implementation drops or canonicalizes NaNs when `NotNaN` is not allowed. |
| `NotInf` (testedWithout_NotInf) | Inf preservation: implementation drops or substitutes infinities when `NotInf` is not allowed. |
| `AllowContract` (testedWithout_AllowContract, e.g. `OID_FMA2PT58`, `OID_SZ_FMA`) | Contraction control: implementation contracts `OpFMul`+`OpFAdd` into a single FMA when `AllowContract` is not allowed, changing the bit-exact result. |
| `AllowReassoc` (testedWithout_AllowReassoc, e.g. `OID_ADD_SUB_REASSOCIABLE`) | Reassociation control: implementation rewrites `(a+b)-a` to `(a-a)+b` (or vice versa) when `AllowReassoc` is not allowed, hiding or exposing overflow. |
| `AllowRecip` (grammar test `op_AllowRecip_exec_grammar_test`) | Grammar rejection: implementation rejects a valid `FPFastMathMode AllowRecip` decoration. |
| `AllowTransform | AllowReassoc | AllowContract` (grammar test) | Grammar rejection: implementation rejects the `AllowTransform` bit even though its required `AllowReassoc | AllowContract` companions are set. |
| `None` (grammar test `op_None_exec_grammar_test`) | Grammar rejection: implementation rejects `FPFastMathMode None` as a mask value. |
| `_deco` variant only (per-result `OpDecorate`) | Decoration plumbing: per-result `FPFastMathMode` decoration is parsed but not applied to the result ID, diverging from the function-wide `_exec` variant. |
| Graphics `_vert` only or `_frag` only | Stage routing: the tested stage's variant of the operation does not see the fast-math mask, or the vertex↔fragment varying bitcast loses the result. |

## Important Variations and Special Cases

- **FP16 without `VK_KHR_16bit_storage`**: a parallel set of FP16 cases (`fp16Without16BitStorage = true`) replaces the standard 16-bit SSBO load/store with a `uint32`-backed bitcast path (`%inval = OpLoad %type_u32 ...` → `OpBitcast %type_f16_vec2`). This isolates fast-math behavior from 16-bit storage support.
- **`AllowTransform` requires `AllowReassoc | AllowContract`**: enforced by `invert()` in `vktSpvAsmFloatControls2Tests.cpp#L122-L128`. When either companion is set, the inverted mask uses `allBitsExceptTransform` so the resulting mask stays legal.
- **`requireRte = true`**: certain overflow/underflow cases (e.g., `add(huge, huge)`, `mul(huge, huge)`, `add_sub_reassociable(max, huge)`) request `RoundingModeRTE` so the implementation must use round-to-nearest-even when computing the intermediate result; this is enforced with `OpCapability RoundingModeRTE`, `OpExtension "SPV_KHR_float_controls"`, and `OpExecutionMode %main RoundingModeRTE <width>`.
- **Conversion operations** (`OID_CONV_FROM_FP16/32/64`) use `isInputTypeRestricted = true` so input and output types may differ; they pull in the input type's capabilities, extensions, and snippet set in addition to the output type's.
- **No `generated_args` subgroup**: unlike the v1 `float_controls` tests, this file only registers `input_args` and never generates arguments inline in the shader body, simplifying the SPIR-V templates.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration entrypoint | [createFloatControls2TestGroup](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3332-L3358) | Builds the `fp16/fp32/fp64` children and the single `input_args` subgroup per float type |
| Compute shader SPIR-V template | [ComputeTestGroupBuilder::init](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2392-L2468) | The StringTemplate skeleton that every compute case specializes |
| Compute test creation loop | [ComputeTestGroupBuilder::createOperationTests](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2470-L2496) | Iterates `testCaseInputs`, skips `V_UNUSED`, dispatches to `fillShaderSpec` |
| Compute shader specialization | [ComputeTestGroupBuilder::fillShaderSpec](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2498-L2669) | Builds the SPIR-V string, input/output buffers, feature requests, and `verifyIO` callback |
| Graphics vertex+fragment templates | [getGraphicsShaderCode](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2671-L2870) | The two StringTemplate skeletons for graphics cases |
| Graphics instance context | [GraphicsTestGroupBuilder::createInstanceContext](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2934-L3328) | Builds per-case specializations, resources, features, and stages |
| FPFastMathMode bits to name map | [behaviorToName](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L109-L117) | Drives both the test name suffix and the `OpDecorate ... FPFastMathMode <name|name>` string |
| `invert()` — the mask inversion rule | [invert](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L122-L129) | Turns "tested flag bits" into the actual applied mask |
| Capability + execution mode + decoration emit | [getBehaviorCapabilityAndExecutionModeDecoration](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2319-L2336) | Emits `OpCapability FloatControls2`, `%bc_u32_fp_exec_mode`, `OpExecutionModeId ... FPFastMathDefault`, and (when `useDecorationFlags`) `OpDecorate %id FPFastMathMode ...` |
| Float controls property fill | [FillFloatControlsProperties](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2338-L2371) | Sets `shaderSignedZeroInfNanPreserveFloatN` and `shaderRoundingModeRTEFloatN` so the underlying v1 properties also match the case's needs |
| Host-side result check | [checkFloats / compareBytes](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L2090-L2186) | Byte-exact comparison with multi-acceptable-result and ULP tolerance rules |
| Operation definitions | [TestCasesBuilder::init](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L1575-L1979) | Per-OperationId SPIR-V command snippets and the IDsToDecorate list |
| Test case matrix | [OperationTestCaseInputs table](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L1180-L1293) | The full `(operation, args, expected, testedFlagBits, requireRte)` matrix shared across FP16/FP32/FP64 |
| Grammar-only sanity cases | [TestCasesBuilder::build](external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L1981-L2006) | Adds `None`, `AllowTransform|AllowReassoc|AllowContract`, and `AllowRecip` grammar tests |

## Questions / Risk Points for User Audit

- Is the framing of "testedWithout_<flag>" as "the absence of <flag> is being verified" correct, given the `invert()` mask inversion rule?
- Is the choice of `dEQP-VK.spirv_assembly.instruction.compute.float_controls2.fp32.input_args.add_testedWithout_NSZ_arg1_minusZero_arg2_one_res_one_deco` as the representative walkthrough acceptable? It exercises both the function-wide `FPFastMathDefault` execution mode (set to `allBits` = 127) and the per-result `OpDecorate %result FPFastMathMode` decoration (set to `~NSZ & allBits` = 123), and reads arguments from the input SSBO.
- Are the multi-acceptable-result and ULP tolerance rules (`V_SIGN_NAN`, `V_ZERO_OR_MINUS_ZERO`, `V_TRIG_ONE`, `V_PI`-family) described at the right depth for the final page, or should they be summarized more briefly?
- The graphics pipeline forbids SSBO writes from the vertex stage and routes the result through a bitcast varying — is this worth a dedicated subsection in `Runtime Execution`, or is one paragraph enough?

## Conversion Notes for Final Wiki Rewrite

- The brief's `## Background Knowledge` should be distilled to a short bullet list covering: (1) what `FPFastMathMode` decorations and `OpExecutionModeId FPFastMathDefault` do, (2) the meaning of each fast-math bit, (3) the `_exec` vs `_deco` distinction. The `AllowTransform requires AllowReassoc|AllowContract` constraint belongs in `Important Variations` of the page, not in Background Knowledge.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`. The `### Cause Analysis` should be written fresh during the rewrite, with one `####` subsection per cause family.
- The concrete example becomes the `Representative Shader Walkthrough 1` in `## Shader Analysis`. The extracted SPIR-V assembly is the compute shader specialized for the chosen case; it goes under `#### Source Code` (unfoldable) per the spirv_assembly deviation. No `#### SPIR-V` subsection is emitted.
- The resource table can be condensed in the final page since `Runtime Execution` already explains the SSBO + varying story.
- The page should keep the `testedFlagBits` axis as the primary behavioral axis; the float type, operation, and `_exec`/`_deco` are parameter dimensions.
- The Vulkan spec chapters at `external/vulkan-docs/src/chapters/` are not present in this repository, so any implementation-level claim that is not directly backed by the source must be flagged as needing further investigation.
