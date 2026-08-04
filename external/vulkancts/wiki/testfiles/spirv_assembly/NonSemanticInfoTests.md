## Overview

**Core question:** Can a compute shader carry non-semantic `OpExtInst` instructions through CTS SPIR-V assembly, shader-module/pipeline creation, and execution without changing its semantic pass-through result?

- `vktSpvAsmNonSemanticInfoTests.cpp` implements the `spirv_assembly.instruction.compute.non_semantic_info` test family and registers eight direct test case leaves.
- Each leaf enables `VK_KHR_shader_non_semantic_info`, emits `SPV_KHR_non_semantic_info`, and varies one way that a non-semantic instruction set, instruction, operand, or placement can appear in an authored SPIR-V module.
- The common compute setup dispatches ten invocations, supplies floats `0.0` through `9.0`, and expects the shader to write the same values back after the selected non-semantic instructions.
- This page covers the parameterized assembly, the shared runtime oracle, feature gate, and the limited failure localization available from a pass-through result.

## Background Knowledge

- **Non-semantic extended instructions:** `OpExtInstImport` names an extended instruction set and `OpExtInst` applies an instruction from that set. The tests use the SPIR-V extension `SPV_KHR_non_semantic_info`, which Vulkan exposes through `VK_KHR_shader_non_semantic_info` or core Vulkan 1.3.
- **Semantic result:** An instruction that affects values, control flow, memory, or observable execution participates in shader semantics. These tests insert non-semantic instructions around an otherwise ordinary compute path, so the output comparison detects whether their presence disrupts module processing or execution.
- **SPIR-V IDs and operands:** An extended instruction can reference IDs for strings, constants, variables, operations, functions, and loads. The IDs must remain valid module operands even when the instruction that consumes them is non-semantic.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.non_semantic_info
├── basic
├── dummy_instruction_set
├── large_instruction_number
├── many_parameters
├── any_constant_type
├── any_constant_type_used
├── any_non_constant_type
└── placement
```

The default Vulkan and Vulkan SC mustpass files each list these eight direct leaves. The source registers the same names in one test family.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Non-semantic test case | `basic`, `dummy_instruction_set`, `large_instruction_number`, `many_parameters`, `any_constant_type`, `any_constant_type_used`, `any_non_constant_type`, `placement` | Selects the generated instruction-set, operand, or placement form. | [`TestType` and registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L40-L50) |
| Imported instruction set | `NonSemantic.KHR.DebugInfo`, `NonSemantic.P.B.NonexistingSet` | Uses the standard debug-information name for `basic`; the dummy leaf instead uses a nonexisting name. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L120-L150) |
| Instruction number | `1`, `55`, `99`, `1234`, `999`, `486`, `963`, `4294967294`, `4294967290` | Exercises ordinary, arbitrary, and near-`UINT32_MAX` instruction-number encodings. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L131-L174) |
| Operand class | strings, constants, semantic result IDs | Selects strings, multiple constant forms, or IDs produced by semantic declarations and operations. The non-constant case uses an image-object load (`OpLoad` of the image variable), not an image sampling/read instruction. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L176-L257) |
| Instruction placement | module scope, between function definitions, function block | Changes where a non-semantic `OpExtInst` occurs in the assembled module. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L259-L275) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each leaf changes the form of non-semantic metadata while the final compute path retains its common input-to-output copy.

### `basic`: import and use standard debug information

The module imports `NonSemantic.KHR.DebugInfo`, creates `%fileStr` with `OpString`, records it with `OpSource`, and passes `%main` plus `%fileStr` to non-semantic instruction `1`. This is the minimal extension-enabled use of a non-semantic instruction set.

### `dummy_instruction_set`: use an unknown instruction-set name

This leaf imports `NonSemantic.P.B.NonexistingSet`, then emits instructions `55` and `99` with strings, `%id`, and `%main`. The surrounding `OpLine` and `OpNoLine` instructions ensure that the module also carries ordinary source-location state around the dummy calls.

### `large_instruction_number`: encode near-maximum instruction numbers

The generated calls use `4294967294` and `4294967290`, both near `UINT32_MAX`. The leaf checks that the assembly path accepts these instruction-number operands for the non-semantic set.

### `many_parameters`: retain a long operand list

The generator emits `%testStr0` through `%testStr99` and supplies all 100 string IDs to one non-semantic instruction `1234`. The test focuses on instruction-operand handling rather than string contents.

### `any_constant_type`: reference constant IDs

This leaf passes an undefined integer, scalar integer and float constants, a struct, vector, array, string, and matrix to instruction `999`. The constants do not have an additional semantic use in this generated module.

### `any_constant_type_used`: reference and semantically use constant IDs

This leaf begins with the same non-semantic constant operands as `any_constant_type`, then consumes those constants through extracts, arithmetic, conversion, and a store. It therefore tests the same IDs in both non-semantic and semantic uses.

### `any_non_constant_type`: reference semantic result IDs

This leaf passes IDs from variables, the entry point, a semantic `GLSL.std.450` instruction, arithmetic, a logical operation, and an image-object load (`OpLoad` of `%image`) to non-semantic instructions `486` and `963`. It checks that these existing semantic IDs remain legal non-semantic operands; it does not perform an image sampling or image-read operation.

### `placement`: emit instructions in three module locations

The module places `OpExtInst` at module scope, between two function definitions, and in `%main` after `OpFunctionCall`. The leaf tests placement rather than a distinct output calculation.

## Shader Analysis

The source constructs CTS-authored SPIR-V assembly in `initPrograms()` rather than GLSL or HLSL. The representative `basic` leaf exposes the common compute scaffold, its non-semantic extension and import, and the final semantic pass-through store. The displayed assembly is a representative reconstruction of the generator's specialized source, published once under `#### Source Code` (there is no duplicate `#### SPIR-V` subsection). The exact final fence was audit-validated with `spirv-as --target-env spv1.0`, `spirv-val --target-env spv1.0`, and `spirv-dis`; this is audit-time semantic validation, not evidence of a separate generation-time CTS gate.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.non_semantic_info.basic
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` | Imports `NonSemantic.KHR.DebugInfo` and emits instruction `1` with `%main` and `%fileStr`. |
| `VK_KHR_shader_non_semantic_info` | The compute specification requires the Vulkan extension that permits `SPV_KHR_non_semantic_info` in shader modules. |
| `10 x 1 x 1` | Executes one invocation for each float in the common ten-element input and output buffers. |

#### Purpose

This module checks that a basic non-semantic extended instruction can coexist with `OpSource`, a string ID, the compute entry point, and an ordinary input-to-output load/store sequence. The host oracle observes only the pass-through floats, so success requires the module to assemble and execute without the non-semantic information changing that semantic path.

#### Structural Design

| Assembly area | Role |
|---------------|------|
| Extension and import | Enables `SPV_KHR_non_semantic_info` and imports `NonSemantic.KHR.DebugInfo` as `%extInstSet`. |
| Input and output buffers | Bind `%indata` at set `0`, binding `0`, and `%outdata` at set `0`, binding `2`; both hold a runtime float array. |
| Invocation index | `%id` supplies `GlobalInvocationId`; `%x` selects the corresponding float slot. |
| Non-semantic use | `%tmp = OpExtInst %void %extInstSet 1 %main %fileStr` records the debug-information instruction without producing an observed data value. |
| Semantic oracle path | `OpLoad` reads `%inval`, and the final `OpStore` writes it unchanged to `%outloc`. |

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly</summary>

```llvm
OpCapability Shader
OpExtension "SPV_KHR_non_semantic_info"
%extInstSet = OpExtInstImport "NonSemantic.KHR.DebugInfo"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %id
OpExecutionMode %main LocalSize 1 1 1
%fileStr = OpString "path\\to\\source.file"
OpSource GLSL 430 %fileStr
OpDecorate %id BuiltIn GlobalInvocationId
OpDecorate %buf BufferBlock
OpDecorate %indata DescriptorSet 0
OpDecorate %indata Binding 0
OpDecorate %image DescriptorSet 0
OpDecorate %image Binding 1
OpDecorate %image NonWritable
OpDecorate %outdata DescriptorSet 0
OpDecorate %outdata Binding 2
OpDecorate %f32arr ArrayStride 4
OpMemberDecorate %buf 0 Offset 0
%bool      = OpTypeBool
%void      = OpTypeVoid
%voidf     = OpTypeFunction %void
%u32       = OpTypeInt 32 0
%i32       = OpTypeInt 32 1
%f32       = OpTypeFloat 32
%uvec3     = OpTypeVector %u32 3
%fvec3     = OpTypeVector %f32 3
%uvec3ptr  = OpTypePointer Input %uvec3
%i32ptr    = OpTypePointer Uniform %i32
%f32ptr    = OpTypePointer Uniform %f32
%i32arr    = OpTypeRuntimeArray %i32
%f32arr    = OpTypeRuntimeArray %f32
%buf     = OpTypeStruct %f32arr
%bufptr  = OpTypePointer Uniform %buf
%indata    = OpVariable %bufptr Uniform
%outdata   = OpVariable %bufptr Uniform
%id         = OpVariable %uvec3ptr Input
%image_type = OpTypeImage %f32 2D 0 0 0 2 Rgba8
%image_ptr  = OpTypePointer UniformConstant %image_type
%image      = OpVariable %image_ptr UniformConstant
%zero       = OpConstant %i32 0
%main       = OpFunction %void None %voidf
%label      = OpLabel
%idval      = OpLoad %uvec3 %id
%x          = OpCompositeExtract %u32 %idval 0
%inloc      = OpAccessChain %f32ptr %indata %zero %x
%outloc     = OpAccessChain %f32ptr %outdata %zero %x
%inval      = OpLoad %f32 %inloc
%tmp = OpExtInst %void %extInstSet 1 %main %fileStr
             OpStore %outloc %inval
             OpReturn
             OpFunctionEnd
```

</details>

#### Additional Info

- The basic-only additions are `%fileStr`, `OpSource`, and `%tmp`. The common scaffold comes from `getComputeAsmShaderPreamble()`, `getComputeAsmCommonTypes()`, and `getComputeAsmInputOutputBuffer()`.
- The default source collection has no explicit shader build option here, so the CTS baseline SPIR-V target is 1.0. The legacy `Uniform` plus `BufferBlock` layout in the authored assembly requires `spv1.0` validation.

#### Parameter Variation Summary

| Parameter dimension | Assembly-level variation from this shader | Evidence |
|---------------------|-------------------------------------------|----------|
| Instruction set | `dummy_instruction_set` replaces the import string with `NonSemantic.P.B.NonexistingSet`. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L139-L150) |
| Instruction number and operands | Other leaves replace `%tmp` with large-number calls, a 100-string call, constant operands, or semantic result IDs. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L152-L257) |
| Placement | `placement` moves calls to module scope and between function definitions in addition to the function body. | [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L259-L275) |

## Runtime Execution and Result Checking

- `getComputeShaderSpec()` creates matching ten-element input and expected-output float arrays with values `0.0` through `9.0`. It also creates a zero-filled integer-backed storage-image resource because one leaf needs an image-object-load ID as a non-semantic operand.
- The specification binds the float input at descriptor set `0`, binding `0`, the storage image at binding `1`, and the float output at binding `2`. It dispatches `IVec3(10, 1, 1)`, so each invocation uses its `GlobalInvocationId.x` as a float-array index.
- The generated `%main` loads `%inval` from `%indata`, inserts the leaf-specific non-semantic instructions, then stores `%inval` to `%outdata`. The selected instruction does not produce the value written by the common final store.
- `SpvAsmSpirvNonSemanticInfoBasicInstance::iterate()` delegates to `SpvAsmComputeShaderInstance::iterate()`. This specification does not install `verifyIO`, so the runner's default verifier byte-compares the one output allocation with the expected float buffer and returns failure on a mismatch (logging up to 16 differing bytes).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Failure to accept the standard extension/import form or process its non-semantic instruction and operands. |
| `dummy_instruction_set` | Failure to process a non-semantic instruction with the selected nonexisting import name and operands. |
| `large_instruction_number` | Failure to represent the selected near-maximum instruction numbers. |
| `many_parameters` | Failure to retain the 100-string non-semantic operand list. |
| `any_constant_type` | Failure to accept the listed constant IDs as non-semantic operands. |
| `any_constant_type_used` | Failure to accept the listed constant IDs as non-semantic operands, or incorrect interaction when they also feed semantic instructions. |
| `any_non_constant_type` | Failure to accept IDs produced by declarations and semantic operations as non-semantic operands. |
| `placement` | Failure to process a non-semantic instruction at module scope, between function definitions, or inside a function block. |

All leaves share assembly, pipeline creation, dispatch, descriptor binding, synchronization, and float-buffer comparison. A final output mismatch alone cannot isolate a non-semantic-information implementation fault from this common compute path.

### Cause Analysis

#### Import and instruction-form processing

**Possible failure symptoms:** `basic` or `dummy_instruction_set` fails to build or execute, or the readback differs from the matching input float sequence.

**Possible implementation causes:** The source exercises `OpExtInstImport`, `OpString`, `OpSource`, and `OpExtInst` under `SPV_KHR_non_semantic_info`. A failure may arise while an assembler, validator, compiler, or runtime processes this form. The final float comparison cannot distinguish an extension-processing failure from shared shader setup without further diagnostics.

#### Instruction-number and operand-list handling

**Possible failure symptoms:** only `large_instruction_number` or `many_parameters` fails, while the ordinary `basic` leaf passes.

**Possible implementation causes:** These leaves differ by the encoded near-maximum instruction number or by 100 string operands. A failure may involve parsing, storing, or forwarding the relevant operand words. Source-level behavior identifies the differing module form; implementation investigation is needed to identify the faulty processing stage.

#### Constant and semantic-ID references

**Possible failure symptoms:** a constant-ID or semantic-ID leaf fails, with `any_constant_type_used` potentially differing from `any_constant_type` because it also evaluates the constants semantically.

**Possible implementation causes:** The module references constants, variables, entry points, loads, arithmetic, a `GLSL.std.450` result, and a logical result in non-semantic calls. A defect may involve ID classification, def-use handling, or the semantic operations that remain in the `any_constant_type_used` path. In that leaf, the intermediate `%tmp11` store is subsequently overwritten by the common pass-through store, so the output oracle does not validate `%tmp11`; it only observes disruptions that prevent the completed path from producing the expected final buffer.

#### Module placement handling

**Possible failure symptoms:** `placement` fails while the leaves that emit their non-semantic instruction in `%main` pass.

**Possible implementation causes:** This leaf is the only one to place `OpExtInst` at module scope and between function definitions as well as within the entry-point function. A failure may involve handling those module locations. The test's pass-through oracle does not distinguish that condition from pipeline or readback failure.

#### Shared compute execution and oracle

**Possible failure symptoms:** several or all leaves produce incorrect float values, compilation fails before a leaf-specific distinction is observable, or a failure is not confined to one generated assembly form.

**Possible implementation causes:** Every leaf uses the same descriptor layout, ten-invocation dispatch, load/store path, and common float comparison. Investigate resource setup, descriptor routing, command execution, synchronization, and readback before attributing a broad failure to non-semantic information.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` requires `VK_KHR_shader_non_semantic_info`. Devices without that functionality cannot run these leaves through this CTS path.
- The extension specification states that its functionality is part of core Vulkan 1.3, but the test source explicitly requests the extension name through `requireDeviceFunctionality` and adds it to the compute shader specification.
- The default Vulkan and Vulkan SC mustpass inventories each contain the eight registered leaves. The source has no leaf-specific feature branch beyond the shared support check.

### Design-based pruning

- The source fixes the dispatch to ten one-dimensional invocations and uses a common float pass-through oracle. It varies one non-semantic instruction form at a time instead of combining every operand class, number, and placement.
- `many_parameters` uses exactly 100 strings, and `large_instruction_number` uses two selected values near the unsigned 32-bit maximum. These are targeted boundary forms, not a complete combinatorial range.
- The page shows only the `basic` assembly because all leaves share the same scaffold. The variation table identifies the leaf-specific fragments without repeating nearly identical modules.

## Key Takeaways

- The test family checks that `SPV_KHR_non_semantic_info` forms coexist with an ordinary compute shader without altering its pass-through output.
- Its eight direct test case leaves independently vary import naming, instruction numbers, operand classes, and module placement.
- `any_constant_type_used` separates the use of constants as non-semantic operands from the case where the same constants also remain semantically active.
- The float oracle detects compilation or execution disruption, but a mismatch by itself cannot localize a fault to non-semantic instruction processing.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Compute specification | [`getComputeShaderSpec()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L52-L70) | Creates the extension request, resources, expected floats, and dispatch dimensions. |
| Support check | [`SpvAsmSpirvNonSemanticInfoBasicCase::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L115-L118) | Requires `VK_KHR_shader_non_semantic_info`. |
| Assembly generator | [`SpvAsmSpirvNonSemanticInfoBasicCase::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L120-L312) | Builds all leaf-specific fragments and the common authored SPIR-V module. |
| Runtime instance | [`SpvAsmSpirvNonSemanticInfoBasicInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L72-L93) | Delegates execution and result checking to the shared compute-shader instance. |
| Family registration | [`createNonSemanticInfoGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L319-L344) | Registers the exact eight direct leaves. |
| Common assembly helpers | [`vktSpvAsmComputeShaderTestUtil.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L65-L132) | Defines the common preamble, types, descriptors, and input/output buffers used by the generated module. |
| Default result comparator | [`SpvAsmComputeShaderInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L945-L998) | Because this specification leaves `verifyIO` null, byte-compares the expected and actual output allocation and fails on a mismatch. |
| Default mustpass inventory | [`spirv-assembly.txt#L7493-L7500`](../../../mustpass/main/vk-default/spirv-assembly.txt#L7493-L7500) | Lists the eight Vulkan executable paths. |
| Extension semantics | [`VK_KHR_shader_non_semantic_info.adoc`](../../../../vulkan-docs/src/appendices/VK_KHR_shader_non_semantic_info.adoc#L16-L28) | States that the Vulkan extension permits `SPV_KHR_non_semantic_info` and notes core Vulkan 1.3 inclusion. |
