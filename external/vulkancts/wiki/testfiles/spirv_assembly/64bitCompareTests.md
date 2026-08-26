## Overview

**Core question:** Do 64-bit floating-point, signed-integer, and unsigned-integer SPIR-V comparison instructions produce correct Boolean results across compute, vertex, and fragment stages?

`64bit_compare` is a SPIR-V-assembly test family for 64-bit comparison instructions. It runs the same type-specific comparison matrix in one compute stage and in vertex and fragment graphics stages. The device reads two storage buffers, writes an integer `0` or `1` for each relation, and the host checks that result against the corresponding C++ comparison operation.

The authoritative implementation is [`vktSpvAsm64bitCompareTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp). The older [`vktSpvAsm64bitCompareTests.md`](vktSpvAsm64bitCompareTests.md) remains intact as the obsolete source document; this page is the rewrite.

## Background Knowledge

### Relations over three 64-bit domains

The `double` group uses `OpFOrd*` and `OpFUnord*` instructions. An ordered instruction returns false if either operand is NaN; an unordered instruction returns true if either operand is NaN. When neither is NaN, both apply their selected relation: equal, not-equal, less-than, less-than-or-equal, greater-than, or greater-than-or-equal.

The integer groups use the shared `OpIEqual` and `OpINotEqual` operations plus a signed or unsigned ordering family:

- `int64`: `OpSLessThan`, `OpSLessThanEqual`, `OpSGreaterThan`, `OpSGreaterThanEqual`.
- `uint64`: `OpULessThan`, `OpULessThanEqual`, `OpUGreaterThan`, `OpUGreaterThanEqual`.

Thus, the group tests both the data-width capability and the type interpretation selected by the opcode.

### Authored assembly and Boolean transport

The C++ source holds CTS-authored SPIR-V assembly in `tcu::StringTemplate` instances; that assembly, not the disabled illustrative GLSL comments, is the shader source. The templates bind two operand SSBOs at descriptor set 0 bindings 0 and 1 and an integer-result SSBO at binding 2. Each comparison produces a Boolean or Boolean vector; `OpSelect` translates it to integer `1` or `0`, which the host can read back.

Scalar modules load one 64-bit value per loop iteration. Vector modules load `vec4` of the 64-bit base type, produce a Boolean vector, select an `ivec4`, and execute one fourth as many loop iterations. The host output remains a flat integer array with one element per input pair.

### FP64 NaN preservation mode

All FP64 cases use the same 20-pair table, including three pairs involving NaN. The `withnan` cases add `OpCapability SignedZeroInfNanPreserve`, `OpExtension "SPV_KHR_float_controls"`, and `OpExecutionMode %main SignedZeroInfNanPreserve 64`. They require the corresponding float-controls property and verify every output. The `nonan` cases omit those declarations and do not report a mismatch at a NaN-containing position; they still verify all non-NaN input pairs.

## Registration Hierarchy

[`create64bitCompareComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1918-L1931) registers a single compute stage; [`create64bitCompareGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1901-L1916) registers vertex and fragment stages. Both are added by the instruction-test root outside `CTS_USES_VULKANSC` conditional sections, so the source registers both roots for Vulkan and Vulkan SC ([registration calls](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21428-L21519)).

```text
spirv_assembly.instruction.compute.64bit_compare
├── double
├── int64
└── uint64

spirv_assembly.instruction.graphics.64bit_compare
├── double
├── int64
└── uint64
```

## Parameter Dimensions and Observed Values

The leaf generators directly encode the following products:

| Type group | Operations | Shapes | FP64 modes | Leaves/stage | Compute leaves | Graphics leaves |
|------------|-----------:|-------:|-----------:|-------------:|---------------:|----------------:|
| `double` | 12 | 2 | 2 | 48 | 48 | 96 |
| `int64` | 6 | 2 | n/a | 12 | 12 | 24 |
| `uint64` | 6 | 2 | n/a | 12 | 12 | 24 |
| **Total** | | | | **72** | **72** | **144** |

The complete standard `vk-default/spirv-assembly.txt` list and the Vulkan SC `vksc-default/spirv-assembly.txt` list each contain the 216 paths formed by the 72 compute leaves plus the 144 graphics leaves, with their respective `dEQP-VK` or `dEQP-VKSC` prefixes. The standard list is not a separate construction mode; it is the same registration matrix under a different test-prefix and profile list.

## Behavior Parameters

### Primary behavior: type family

| Value | Operand semantics | Capability | Comparison families |
|-------|-------------------|------------|---------------------|
| `double` | IEEE-style FP64 relations with ordered/unordered NaN rules | `Float64` | 12 `OpFOrd*` / `OpFUnord*` operations |
| `int64` | Signed 64-bit integers | `Int64` | `OpIEqual`, `OpINotEqual`, four `OpS*` ordering operations |
| `uint64` | Unsigned 64-bit integers | `Int64` | `OpIEqual`, `OpINotEqual`, four `OpU*` ordering operations |

The type family is the primary behavior axis because it changes the operand representation, capability, opcode set, and comparison semantics. Stage, scalar/vector representation, selected relation, and FP64 mode are secondary axes.

### Secondary dimensions

| Dimension | Values | Effect |
|-----------|--------|--------|
| Stage | `comp`; graphics `vert`, `frag` | Selects compute, vertex, or fragment assembly and pipeline execution. |
| Representation | `single`, `vector` | Selects scalar 64-bit values or four-wide vectors; preserves the same flat operand set. |
| Relation | 12 FP64 / 6 per integer group | Substitutes `${OPNAME}` with the selected comparison instruction. |
| FP64 mode | `nonan`, `withnan` | Selects whether float-controls NaN preservation declarations and NaN-position verification apply. |

## Shader Analysis

The source has six CTS-authored SPIR-V assembly templates: scalar and vector forms for compute, vertex, and fragment stages ([template selector](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L996-L1022)). The representative case below specializes the scalar compute template directly; there is no GLSL or HLSL compilation step. The fragment stage's separately supplied GLSL passthrough vertex shader is pipeline plumbing rather than the comparison shader ([`VertShaderPassThrough`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L753-L765)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.64bit_compare.double.comp_opfordequal_withnan_single
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `comp` | Selects `CompShaderSingle`, with `GLCompute` entry point `main` and `LocalSize 1 1 1`. |
| `double` | Specializes `${OPCAPABILITY}` to `OpCapability Float64` and `${OPTYPE}` to `OpTypeFloat 64`. |
| `OpFOrdEqual` | Ordered equality returns false whenever either FP64 operand is NaN. |
| `withnan` | Adds `SignedZeroInfNanPreserve`, `SPV_KHR_float_controls`, and the 64-bit preservation execution mode. |
| `single` | Sets `${ITERS}` to `20`, processing every fixed operand pair as an individual scalar. |

#### Purpose

This case makes ordered FP64 NaN behavior observable while requiring signed-zero, infinity, and NaN preservation. It checks that `OpFOrdEqual` yields `0` for the three NaN-containing pairs and correctly encodes equality for the other 17 pairs.

#### Structural Design

| Phase | Authored assembly behavior | Role in the check |
|-------|----------------------------|-------------------|
| Declarations | Enables `Shader`, `Float64`, and `SignedZeroInfNanPreserve`, imports the float-controls extension, and applies its 64-bit execution mode. | Establishes the FP64 behavior required by this leaf. |
| Resources | Binds FP64 runtime-array inputs at set `0`, bindings `0` and `1`, and a 32-bit signed result array at binding `2`. | Carries the two operand streams and host-readable results. |
| Loop | A function-local integer index runs from `0` while it is less than `20`. | Visits all fixed operand pairs in one invocation. |
| Compare and encode | Loads both doubles, executes `OpFOrdEqual`, and uses `OpSelect` to map the Boolean to integer `1` or `0`. | Makes the relation result storable and directly checkable. |
| Store | Writes the selected integer to the result array at the same index. | Preserves one-to-one correspondence with the host operand table. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the module directly as SPIR-V assembly by specializing [`CompShaderSingle`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L258-L350) in [`T64bitCompareTest::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1728-L1757). The selected module has compute stage entry point `main`; its complete fresh disassembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The selected substitutions are `ITERS=20`, `OPNAME=OpFOrdEqual`, `OPCAPABILITY=OpCapability Float64`, `OPTYPE=OpTypeFloat 64`, plus all three enabled NaN-preservation fragments ([specialization map](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1734-L1742)).
- The two FP64 runtime arrays use an 8-byte `ArrayStride`; the 32-bit integer result array uses a 4-byte stride. The templates use the pre-SPIR-V-1.4 `Uniform`/`BufferBlock` SSBO representation.
- The fixed 20-pair table ends with `(0, NaN)`, `(NaN, 0)`, and `(NaN, NaN)`, so this ordered operation must encode false at all three positions ([`DOUBLE_OPERANDS`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1133-L1138)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| FP64 mode | `nonan` removes the preservation capability, extension, and execution mode; the rest of the module is unchanged. | [`getNanCapability()`, `getNanExtension()`, and `getNanExeMode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1070-L1083) |
| Relation | Another floating relation replaces only `${OPNAME}` with its selected `OpFOrd*` or `OpFUnord*` instruction. | [`DoubleCompareOperation::spirvName()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L79-L88) |
| Shape | `vector` selects `CompShaderVector`, changes operands and results to four-wide vectors, and sets the loop count to `5`. | [`CompShaderVector`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L352-L466) |
| Type family | `int64` and `uint64` select signed or unsigned `OpTypeInt 64`, use `Int64`, omit FP64 preservation fragments, and use integer comparison opcodes. | [`SpirvTemplateManager` type specializations](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1038-L1068) |
| Stage | `vert` or `frag` selects the corresponding graphics-stage scalar template; fragment also declares `OriginUpperLeft`. | [`SpirvTemplateManager::getTemplate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L996-L1022) |

#### SPIR-V

- Status: assembled, validated, disassembled, and round-trip verified
- Source: CTS-authored SPIR-V assembly specialized from `CompShaderSingle`
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 47
; Schema: 0
               OpCapability Shader
               OpCapability Float64
               OpCapability SignedZeroInfNanPreserve
               OpExtension "SPV_KHR_float_controls"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main SignedZeroInfNanPreserve 64
               OpExecutionMode %main LocalSize 1 1 1
               OpName %main "main"
               OpName %i "i"
               OpName %Output1 "Output1"
               OpMemberName %Output1 0 "values"
               OpName %output1 "output1"
               OpName %Input1 "Input1"
               OpMemberName %Input1 0 "values"
               OpName %input1 "input1"
               OpName %Input2 "Input2"
               OpMemberName %Input2 0 "values"
               OpName %input2 "input2"
               OpDecorate %_runtimearr_int ArrayStride 4
               OpMemberDecorate %Output1 0 Offset 0
               OpDecorate %Output1 BufferBlock
               OpDecorate %output1 DescriptorSet 0
               OpDecorate %output1 Binding 2
               OpDecorate %_runtimearr_double ArrayStride 8
               OpMemberDecorate %Input1 0 Offset 0
               OpDecorate %Input1 BufferBlock
               OpDecorate %input1 DescriptorSet 0
               OpDecorate %input1 Binding 0
               OpDecorate %_runtimearr_double_0 ArrayStride 8
               OpMemberDecorate %Input2 0 Offset 0
               OpDecorate %Input2 BufferBlock
               OpDecorate %input2 DescriptorSet 0
               OpDecorate %input2 Binding 1
       %void = OpTypeVoid
         %14 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
     %int_20 = OpConstant %int 20
       %bool = OpTypeBool
%_runtimearr_int = OpTypeRuntimeArray %int
    %Output1 = OpTypeStruct %_runtimearr_int
%_ptr_Uniform_Output1 = OpTypePointer Uniform %Output1
    %output1 = OpVariable %_ptr_Uniform_Output1 Uniform
     %double = OpTypeFloat 64
%_runtimearr_double = OpTypeRuntimeArray %double
     %Input1 = OpTypeStruct %_runtimearr_double
%_ptr_Uniform_Input1 = OpTypePointer Uniform %Input1
     %input1 = OpVariable %_ptr_Uniform_Input1 Uniform
%_ptr_Uniform_double = OpTypePointer Uniform %double
%_runtimearr_double_0 = OpTypeRuntimeArray %double
     %Input2 = OpTypeStruct %_runtimearr_double_0
%_ptr_Uniform_Input2 = OpTypePointer Uniform %Input2
     %input2 = OpVariable %_ptr_Uniform_Input2 Uniform
      %int_1 = OpConstant %int 1
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %main = OpFunction %void None %14
         %27 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %28
         %28 = OpLabel
               OpLoopMerge %29 %30 None
               OpBranch %31
         %31 = OpLabel
         %32 = OpLoad %int %i
         %33 = OpSLessThan %bool %32 %int_20
               OpBranchConditional %33 %34 %29
         %34 = OpLabel
         %35 = OpLoad %int %i
         %36 = OpLoad %int %i
         %37 = OpAccessChain %_ptr_Uniform_double %input1 %int_0 %36
         %38 = OpLoad %double %37
         %39 = OpLoad %int %i
         %40 = OpAccessChain %_ptr_Uniform_double %input2 %int_0 %39
         %41 = OpLoad %double %40
         %42 = OpFOrdEqual %bool %38 %41
         %43 = OpSelect %int %42 %int_1 %int_0
         %44 = OpAccessChain %_ptr_Uniform_int %output1 %int_0 %35
               OpStore %44 %43
               OpBranch %30
         %30 = OpLabel
         %45 = OpLoad %int %i
         %46 = OpIAdd %int %45 %int_1
               OpStore %i %46
               OpBranch %28
         %29 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

[`T64bitCompareTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1197-L1638) owns execution rather than using the generic `SpvAsmComputeShaderCase` harness.

1. It creates three host-visible `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` buffers sized for the selected operand list and output integers ([buffer helper](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1106-L1130)).
2. It writes left operands to binding 0, right operands to binding 1, and `-9` sentinels to the binding-2 output buffer, then flushes all three allocations ([initialization](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1291-L1306)).
3. It uses host-to-shader and shader-to-host buffer barriers. Compute binds a compute pipeline and dispatches one workgroup; graphics binds a graphics pipeline and issues a single point draw ([command recording](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1372-L1615)).
4. After queue completion it invalidates allocations, copies the output into `std::vector<int>`, and calls `CompareOperation::run()` for every pair ([verification loop](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1617-L1638)).
5. A checked mismatch returns failure with its flat output position and expected/actual integer values. There is no tolerance or aggregate score.

The three fixed input tables are intentional coverage, not randomized data:

- `DOUBLE_OPERANDS`: 20 pairs, including ordinary ordering/equality combinations plus `(0, NaN)`, `(NaN, 0)`, and `(NaN, NaN)`.
- `INT64_OPERANDS`: 16 signed pairs spanning negative, zero, and positive comparisons.
- `UINT64_OPERANDS`: 12 unsigned pairs including zero, one, and `UINT64_MAX` / `UINT64_MAX - 1` boundaries.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `double` ordered comparisons | Incorrect FP64 relation lowering, or failure to return false when either operand is NaN. |
| `double` unordered comparisons | Incorrect FP64 relation lowering, or failure to return true when either operand is NaN. |
| `double` `withnan` | `SignedZeroInfNanPreserve 64` capability/extension/execution-mode handling, NaN transport through the SSBO, or ordered/unordered NaN semantics. |
| `int64` | Signed 64-bit comparison lowering or signed operand transport, especially around negative values. |
| `uint64` | Unsigned 64-bit comparison lowering or unsigned operand transport, especially around `UINT64_MAX`. |
| Any family only in `vert` or `frag` | Stage-specific storage-buffer writes, graphics pipeline setup, or the relevant stores-and-atomics feature path. |
| Any family across stages | Shared descriptor binding, synchronization/readback, generated-template specialization, or host oracle setup. |

### Cause Analysis

#### Ordered versus unordered NaN interpretation

**Possible failure symptoms:** the non-NaN pairs pass, but FP64 cases disagree at `(0, NaN)`, `(NaN, 0)`, or `(NaN, NaN)`; ordered and unordered cases may show complementary failures.

**Possible implementation causes:** the implementation may lower `OpFOrd*` as though it were unordered, lower `OpFUnord*` as though it were ordered, or feed an invalid compare result into `OpSelect`. A `withnan` failure focused on those indices can also indicate that the requested FP64 preservation mode was not honored. The test establishes a mismatch in this path; assigning it to a specific compiler, memory, or hardware layer requires separate evidence.

#### Signedness-specific integer comparison

**Possible failure symptoms:** `int64` failures cluster on negative pairs while `uint64` passes, or `uint64` failures cluster on values near `UINT64_MAX` while signed cases pass.

**Possible implementation causes:** a signed relation may use an unsigned comparison internally, or the reverse; alternatively, 64-bit SSBO loads could be sign-extended, truncated, or otherwise mishandled before the comparison. The operand tables make those interpretations distinguishable, but a single failed leaf alone does not identify which internal path is at fault.

#### Scalar/vector representation mismatch

**Possible failure symptoms:** scalar leaves pass but vector leaves fail for the same operation and stage, often in four-result patterns.

**Possible implementation causes:** the vector instruction, vector load/store layout, Boolean-vector `OpSelect`, or `ivec4` output stride can differ from the scalar lowering path. Both forms cover the same base operands, so their failure split is useful localization evidence rather than proof of one particular driver defect.

#### Graphics-stage storage write

**Possible failure symptoms:** compute passes, while only vertex or only fragment leaves fail.

**Possible implementation causes:** the stage-specific SSBO store capability, template entry point, graphics pipeline construction, or synchronization path may be at issue. Fragment cases include a passthrough vertex shader and execute a point draw; vertex cases use rasterizer discard. This test's observation is the SSBO result, not a color attachment, so a failure does not by itself diagnose rasterization.

#### Shared result transport or oracle setup

**Possible failure symptoms:** many types, operations, and stages fail with similar stale (`-9`) or shifted values.

**Possible implementation causes:** descriptor binding order, host/device visibility barriers, readback copying, or the C++ expected-result calculation could be wrong. These paths are shared across the family. A localized semantic failure is less likely to originate here, but the test itself does not prove the source of a broad pattern.

## Case Pruning

### Requirement-based pruning

| Scope | Requirement | Result if unavailable |
|-------|-------------|-----------------------|
| `double` | `VkPhysicalDeviceFeatures::shaderFloat64` | All FP64 leaves are not supported. |
| `int64`, `uint64` | `VkPhysicalDeviceFeatures::shaderInt64` | The respective integer leaves are not supported. |
| `vert` | `vertexPipelineStoresAndAtomics` | Vertex leaves are not supported. |
| `frag` | `fragmentStoresAndAtomics` | Fragment leaves are not supported. |
| FP64 `withnan` | Float-controls support query must satisfy `shaderSignedZeroInfNanPreserveFloat64` | `withnan` leaves are not supported; this does not downgrade them to `nonan`. |

The support implementation is at [`checkTypeSupport()` and `T64bitCompareTest::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1664-L1726).

### Design-based pruning

No cases are removed by test design. In particular, no `#ifndef CTS_USES_VULKANSC` surrounds the two registration calls, and the Vulkan SC mustpass list includes the same compute and graphics matrix; this family is therefore not compile-time pruned for Vulkan SC.

## Key Takeaways

- The family cleanly separates FP64 ordered/unordered NaN semantics from signed and unsigned 64-bit integer ordering, while reusing one SSBO-to-integer-result mechanism.
- `withnan` is a genuine capability-and-execution-mode path with full NaN-position validation; it is skipped, not weakened, when the FP64 preservation property is missing.
- The 216 mustpass paths are mechanically explained by 72 compute leaves plus the same 72-leaf matrix for each of the two graphics stages.
- Scalar and vector paths cover identical flat operand tables, making a scalar/vector failure split informative for comparison, data-layout, or Boolean-vector lowering investigation.
- See `## Failure Meaning` for the ordered/unordered, signedness, representation, graphics-stage, and shared-transport diagnostic map.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root registration | [`vktSpvAsmInstructionTests.cpp#L21428-L21519`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21428-L21519) | Adds compute and graphics groups without a Vulkan SC compile-time exclusion. |
| SPIR-V templates | [`CompShaderSingle` through `FragShaderVector`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L258-L994) | Defines the authored scalar/vector and compute/graphics modules. |
| Template selection and fragments | [`SpirvTemplateManager`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L996-L1083) | Maps type and stage to templates, capabilities/types, and optional NaN declarations. |
| Operand tables | [`DOUBLE_OPERANDS`, `INT64_OPERANDS`, `UINT64_OPERANDS`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1133-L1159) | Defines all fixed operand pairs. |
| Execution / verifier | [`T64bitCompareTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1197-L1638) | Creates buffers and pipelines, submits work, and checks every output. |
| Support gates | [`checkTypeSupport()` and `T64bitCompareTest::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1664-L1726) | Enforces type, graphics-store, and NaN-preservation support. |
| Program initialization | [`T64bitCompareTest::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1729-L1757) | Specializes assembly and attaches the fragment passthrough vertex shader. |
| Matrix generators | [`createDoubleCompareTestsInGroup()`, `createInt64CompareTestsInGroup()`, `createUint64CompareTestsInGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1777-L1845) | Defines operations, naming, and Cartesian products. |
| Root builders | [`create64bitCompareGraphicsGroup()` and `create64bitCompareComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1901-L1931) | Instantiates `double`, `int64`, and `uint64` beneath each root. |
