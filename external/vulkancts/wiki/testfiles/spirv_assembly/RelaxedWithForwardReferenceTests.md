## Overview

**Core question:** Does `OpExtInstWithForwardRefsKHR` allow the non-semantic debug instructions in a SPIR-V 1.6 compute shader to refer to debug objects defined later in the module?

- `vktSpvAsmRelaxedWithForwardReferenceTests.cpp` implements one `relaxed_with_forward_reference` test family in the `spirv_assembly` test category.
- Its only test case leaf, `static_method_shader`, embeds SPIR-V produced from an HLSL class with a static method. The module's debug metadata contains mutually dependent function and composite-type records.
- The compute harness dispatches the module and byte-compares its output buffer with the expected ten-element buffer. A pass shows acceptance and execution of this module through that path; it does not show that an implementation retained, exposed, or otherwise consumed the non-semantic debug metadata correctly.

## Background Knowledge

- `OpExtInst` invokes an instruction from an imported instruction set. This module imports `NonSemantic.Shader.DebugInfo.100`, so its debug records do not change shader execution semantics.
- `OpExtInstWithForwardRefsKHR` is the relaxed-extended-instruction form used when selected non-semantic debug instructions need an ID before the module defines that ID. The extension permits these limited forward references, allowing cyclic debug metadata without changing the order of the referenced records.
- A compute shader invocation can use `GlobalInvocationId.x` to select one storage-buffer element. The test uses that index for its load and store, but every supplied and expected element is zero, so the result comparison does not prove per-element propagation of distinct input values.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.relaxed_with_forward_reference
└── static_method_shader
```

[`createRelaxedWithForwardReferenceGraphicsGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L280-L293) creates the `relaxed_with_forward_reference` test family and registers its sole test case leaf.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader variant | `static_method_shader` | The only registered case supplies the fixed `kStaticMethodShader` assembly. | [`testList`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L284-L292) |
| SPIR-V target version | `SPIRV_VERSION_1_6` | The program builder assembles the embedded module as SPIR-V 1.6. | [`initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L113-L117) |
| Required device functionality | `VK_KHR_shader_non_semantic_info`, `VK_KHR_shader_relaxed_extended_instruction` | Both extensions are required before the case runs. | [`checkSupport`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L107-L111) |
| Compute buffer length | `10` | The specification creates ten zero-valued input floats and ten expected output floats. | [`getComputeShaderSpec`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L45-L59) |

The current Vulkan and Vulkan SC default mustpass inventories each contain the one `static_method_shader` leaf: [Vulkan](../../../mustpass/main/vk-default/spirv-assembly.txt#L16125) and [Vulkan SC](../../../mustpass/main/vksc-default/spirv-assembly.txt#L5590).

## Behavior Parameters

This test family has one fixed test case leaf rather than a matrix of behavioral values. `static_method_shader` checks whether a compute module with mutually referring non-semantic debug records, including the permitted `%35`/`%38` forward uses of `%37`, can be assembled and run. The fixed all-zero copy oracle does not distinguish debug-metadata processing from the ordinary compute path.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.relaxed_with_forward_reference.static_method_shader
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `static_method_shader` | Selects the family's only CTS-authored module, derived from an HLSL class with a static method. |
| SPIR-V 1.6 | Matches the explicit `SPIRV_VERSION_1_6` build target used by `initPrograms()`. |
| `OpExtInstWithForwardRefsKHR` | Allows `%35` and `%38` to use `%37` before its definition in the non-semantic debug-record graph. |
| `GLCompute` entry point `main` | Runs with `LocalSize 10 1 1` and copies one storage-buffer element per invocation. |

#### Purpose

The original HLSL defines class `A` and calls `A::method()` after copying an input element to the output buffer. Its debug metadata describes the function and class with a cyclic dependency: the function-type and function records use the class record before it is defined, and the class record refers back to the function record.

#### Structural Design

| Record | Forward-reference relationship | Role |
|--------|--------------------------------|------|
| `%35` | `DebugTypeFunction` names `%37` before its definition. | Describes the static method's function type. |
| `%38` | `DebugFunction` names `%35` and `%37` before `%37` is defined. | Describes `A.method`. |
| `%37` | `DebugTypeComposite` names `%38`. | Describes class `A` and closes the cycle. |
| Executable path | `main` indexes `%input` and `%output` with `GlobalInvocationId.x`. | Copies one 32-bit element independently of the non-semantic debug records. |

#### Shader Code

This representative case does not use reconstructed GLSL or HLSL as the submitted shader source. CTS passes the complete [`kStaticMethodShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L147-L278) string directly to the SPIR-V assembly source collection with a SPIR-V 1.6 target. The module contains the `GLCompute` entry point `main`; the final `SPIR-V` subsection publishes the complete fresh SPIR-V Tools disassembly of that CTS-authored module rather than duplicating assembly here.

#### Additional Info

- The C++ source documents the HLSL input and its DXC command, while `kStaticMethodShader` is the authoritative shader artifact submitted by this test.
- The forward references occur only in `NonSemantic.Shader.DebugInfo.100` instructions. The executable path still loads from `%input` and stores the same 32-bit value to `%output`. In the fresh disassembly, SPIR-V Tools renumbers source IDs `%35`, `%38`, and `%37` to `%66`, `%68`, and `%67`; their dependency order is unchanged.
- `spirv-as --target-env spv1.6` assembles the authored module, and disassembly followed by reassembly produces a byte-identical binary. `spirv-val --target-env spv1.6` reports that `DebugFunction` uses source line 2 while the embedded `DebugSource` text has one line. That diagnostic is an authored debug-source inconsistency and an audit-time validator limitation, not a CTS runtime result.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Shader variant | None. The family registers only `static_method_shader`. | [`testList`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L284-L292) |
| Debug-record ordering | The fixed module defines `%35` and `%38` before `%37`; the relaxed opcode permits those forward uses. | [`kStaticMethodShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L235-L237) |
| Executable behavior | No variant changes the load/store path or workgroup size. | [`kStaticMethodShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L153-L154), [`main`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L256-L277) |

#### SPIR-V

- Status: assembled, disassembled, and binary-round-trip verified; semantic-validator diagnostic documented above
- Source: CTS-authored SPIR-V assembly from `kStaticMethodShader`
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.6`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 105
; Schema: 0
               OpCapability Shader
               OpExtension "SPV_KHR_non_semantic_info"
               OpExtension "SPV_KHR_relaxed_extended_instruction"
          %1 = OpExtInstImport "NonSemantic.Shader.DebugInfo.100"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %input %output
               OpExecutionMode %main LocalSize 10 1 1
          %6 = OpString "repro.hlsl"
          %7 = OpString "source"
          %8 = OpString "A.method"
          %9 = OpString ""
         %10 = OpString "A"
         %11 = OpString "a"
         %12 = OpString "uint"
         %13 = OpString "main"
         %14 = OpString "id"
         %15 = OpString "fb39af55"
         %16 = OpString " -E main -T cs_6_0 -fspv-target-env=vulkan1.3 -fspv-debug=vulkan-with-source -spirv -Qembed_debug"
         %17 = OpString "@type.RWStructuredBuffer.uint"
         %18 = OpString "type.RWStructuredBuffer.uint"
         %19 = OpString "TemplateParam"
         %20 = OpString "output"
         %21 = OpString "@type.StructuredBuffer.uint"
         %22 = OpString "type.StructuredBuffer.uint"
         %23 = OpString "input"
               OpName %type_StructuredBuffer_uint "type.StructuredBuffer.uint"
               OpName %input "input"
               OpName %type_RWStructuredBuffer_uint "type.RWStructuredBuffer.uint"
               OpName %output "output"
               OpName %main "main"
               OpName %A "A"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %input DescriptorSet 0
               OpDecorate %input Binding 0
               OpDecorate %output DescriptorSet 0
               OpDecorate %output Binding 1
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpMemberDecorate %type_StructuredBuffer_uint 0 Offset 0
               OpMemberDecorate %type_StructuredBuffer_uint 0 NonWritable
               OpDecorate %type_StructuredBuffer_uint Block
               OpMemberDecorate %type_RWStructuredBuffer_uint 0 Offset 0
               OpDecorate %type_RWStructuredBuffer_uint Block
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
    %uint_32 = OpConstant %uint 32
%_runtimearr_uint = OpTypeRuntimeArray %uint
%type_StructuredBuffer_uint = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_type_StructuredBuffer_uint = OpTypePointer StorageBuffer %type_StructuredBuffer_uint
%type_RWStructuredBuffer_uint = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_type_RWStructuredBuffer_uint = OpTypePointer StorageBuffer %type_RWStructuredBuffer_uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
       %void = OpTypeVoid
     %uint_1 = OpConstant %uint 1
     %uint_4 = OpConstant %uint 4
     %uint_5 = OpConstant %uint 5
     %uint_3 = OpConstant %uint 3
     %uint_2 = OpConstant %uint 2
     %uint_0 = OpConstant %uint 0
     %uint_7 = OpConstant %uint 7
    %uint_21 = OpConstant %uint 21
     %uint_6 = OpConstant %uint 6
    %uint_12 = OpConstant %uint 12
    %uint_43 = OpConstant %uint 43
    %uint_17 = OpConstant %uint 17
     %uint_9 = OpConstant %uint 9
    %uint_26 = OpConstant %uint 26
     %uint_8 = OpConstant %uint 8
    %uint_24 = OpConstant %uint 24
         %53 = OpTypeFunction %void
    %uint_15 = OpConstant %uint 15
    %uint_13 = OpConstant %uint 13
    %uint_27 = OpConstant %uint 27
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
    %uint_18 = OpConstant %uint 18
    %uint_28 = OpConstant %uint 28
          %A = OpTypeStruct
    %uint_14 = OpConstant %uint 14
%_ptr_Function_A = OpTypePointer Function %A
      %input = OpVariable %_ptr_StorageBuffer_type_StructuredBuffer_uint StorageBuffer
     %output = OpVariable %_ptr_StorageBuffer_type_RWStructuredBuffer_uint StorageBuffer
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
         %62 = OpExtInst %void %1 DebugInfoNone
         %63 = OpExtInst %void %1 DebugExpression
         %64 = OpExtInst %void %1 DebugSource %6 %7
         %65 = OpExtInst %void %1 DebugCompilationUnit %uint_1 %uint_4 %64 %uint_5
         %66 = OpExtInstWithForwardRefsKHR %void %1 DebugTypeFunction %uint_3 %67
         %68 = OpExtInstWithForwardRefsKHR %void %1 DebugFunction %8 %66 %64 %uint_2 %uint_3 %67 %9 %uint_3 %uint_2
         %67 = OpExtInst %void %1 DebugTypeComposite %10 %uint_0 %64 %uint_1 %uint_7 %65 %10 %uint_0 %uint_3 %68
         %69 = OpExtInst %void %1 DebugLexicalBlock %64 %uint_2 %uint_21 %68
         %70 = OpExtInst %void %1 DebugLocalVariable %11 %67 %64 %uint_3 %uint_7 %69 %uint_4
         %71 = OpExtInst %void %1 DebugTypeBasic %12 %uint_32 %uint_6 %uint_0
         %72 = OpExtInst %void %1 DebugTypeVector %71 %uint_3
         %73 = OpExtInst %void %1 DebugTypeFunction %uint_3 %void %72
         %74 = OpExtInst %void %1 DebugFunction %13 %73 %64 %uint_12 %uint_1 %65 %9 %uint_3 %uint_12
         %75 = OpExtInst %void %1 DebugLexicalBlock %64 %uint_12 %uint_43 %74
         %76 = OpExtInst %void %1 DebugLocalVariable %14 %72 %64 %uint_12 %uint_17 %74 %uint_4 %uint_1
         %77 = OpExtInst %void %1 DebugTypeComposite %17 %uint_0 %64 %uint_0 %uint_0 %65 %18 %62 %uint_3
         %78 = OpExtInst %void %1 DebugTypeTemplateParameter %19 %71 %62 %64 %uint_0 %uint_0
         %79 = OpExtInst %void %1 DebugTypeTemplate %77 %78
         %80 = OpExtInst %void %1 DebugGlobalVariable %20 %79 %64 %uint_9 %uint_26 %65 %20 %output %uint_8
         %81 = OpExtInst %void %1 DebugTypeComposite %21 %uint_0 %64 %uint_0 %uint_0 %65 %22 %62 %uint_3
         %82 = OpExtInst %void %1 DebugTypeTemplateParameter %19 %71 %62 %64 %uint_0 %uint_0
         %83 = OpExtInst %void %1 DebugTypeTemplate %81 %82
         %84 = OpExtInst %void %1 DebugGlobalVariable %23 %83 %64 %uint_8 %uint_24 %65 %23 %input %uint_8
         %85 = OpExtInst %void %1 DebugEntryPoint %74 %65 %15 %16
         %86 = OpExtInst %void %1 DebugInlinedAt %uint_14 %75
       %main = OpFunction %void None %53
         %87 = OpLabel
         %88 = OpVariable %_ptr_Function_A Function
         %89 = OpExtInst %void %1 DebugFunctionDefinition %74 %main
         %90 = OpLoad %v3uint %gl_GlobalInvocationID
         %91 = OpExtInst %void %1 DebugValue %76 %90 %63
         %92 = OpExtInst %void %1 DebugScope %75
         %93 = OpExtInst %void %1 DebugLine %64 %uint_13 %uint_13 %uint_24 %uint_27
         %94 = OpCompositeExtract %uint %90 0
         %95 = OpExtInst %void %1 DebugLine %64 %uint_13 %uint_13 %uint_18 %uint_28
         %96 = OpAccessChain %_ptr_StorageBuffer_uint %input %int_0 %94
         %97 = OpLoad %uint %96
         %98 = OpExtInst %void %1 DebugLine %64 %uint_13 %uint_13 %uint_3 %uint_28
         %99 = OpAccessChain %_ptr_StorageBuffer_uint %output %int_0 %94
               OpStore %99 %97
        %100 = OpExtInst %void %1 DebugScope %69 %86
        %101 = OpExtInst %void %1 DebugLine %64 %uint_3 %uint_3 %uint_5 %uint_7
        %102 = OpExtInst %void %1 DebugDeclare %70 %88 %63
        %103 = OpExtInst %void %1 DebugNoScope
        %104 = OpExtInst %void %1 DebugLine %64 %uint_15 %uint_15 %uint_1 %uint_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `getComputeShaderSpec()` creates ten zero-valued `Float32Buffer` input and expected-output payloads, uses one workgroup, and selects SPIR-V 1.6. The shader declares 32-bit unsigned storage-buffer elements, but zero has the same 32-bit representation in both views; the shared compute instance supplies these byte payloads to the shader.
- `checkSupport()` requires `VK_KHR_shader_non_semantic_info` and `VK_KHR_shader_relaxed_extended_instruction`. `initPrograms()` adds the embedded assembly as the `compute` SPIR-V source with `SPIRV_VERSION_1_6` build options.
- `SpvAsmSpirvRelaxedForwardReferenceBasicInstance::iterate()` delegates to `SpvAsmComputeShaderInstance::iterate()`. The module loads `%gl_GlobalInvocationID`, extracts its x component, reads `%input` at that index, and stores the value to `%output`.
- The shared compute harness creates the shader module and pipeline, dispatches, makes shader writes available to the host, invalidates output memory before reading, and byte-compares the output with the expected buffer. The source-specific observable is successful module build and this dispatch/readback path for a module containing forward-reference debug records. Because the debug records are non-semantic and every expected element is zero, the oracle neither observes metadata retention/consumption nor proves distinct-value or index-sensitive copying.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static_method_shader` | Rejection of the module/program that contains the permitted `OpExtInstWithForwardRefsKHR` records, or a failure anywhere in the shared compute dispatch/readback path. Absent required device functionality is reported as not supported, not a test failure. The all-zero buffer oracle cannot identify an error in retained or consumed debug metadata. |

### Cause Analysis

#### Forward-reference debug instruction handling

**Possible failure symptoms:** After support checks pass, the case can fail while CTS builds the program, creates the shader module or pipeline, or compares output after dispatch. The accepted all-zero output does not establish that debug records were retained, exposed, or consumed correctly.

**Possible implementation causes:** The case requires support for both named extensions; otherwise `checkSupport()` reports not supported. Once that gate passes, program-build or module/pipeline rejection can involve processing of the forward-reference opcode or of the cyclic non-semantic records. An output mismatch can instead arise anywhere in the shared compute path. The CTS result does not isolate parser, validator, compiler, or runtime handling, and because the records are non-semantic its output oracle cannot show that the metadata was consumed correctly.

#### Compute output path

**Possible failure symptoms:** The output buffer differs from the expected ten-element buffer after dispatch, even though the shader was accepted. The mismatch can affect one index or all indices.

**Possible implementation causes:** The source performs a global-invocation-ID extraction, a storage-buffer load, and a storage-buffer store. A failure can involve descriptor setup, address calculation, execution completion, or host readback as well as the forward-reference module. The single buffer comparison cannot distinguish those mechanisms without further investigation.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips the case unless both `VK_KHR_shader_non_semantic_info` and `VK_KHR_shader_relaxed_extended_instruction` are available.
- `initPrograms()` targets SPIR-V 1.6, so the module must be built for the selected Vulkan environment with that version supported by the CTS harness.

### Design-based pruning

The source defines one fixed shader and one registered test case. It does not generate variants for different debug-record orders, HLSL classes, buffer lengths, or shader stages. The ten-element buffer is part of the common compute specification rather than a registered parameter dimension.

## Key Takeaways

- `static_method_shader` is a single focused compute test for forward references in non-semantic shader debug metadata.
- `%35` and `%38` refer to `%37` before `%37` is defined, while `%37` refers back to `%38`, forming the debug-record dependency this test preserves.
- The executable shader path is simple: each invocation uses its global x index for one input load and corresponding output store, while the fixed zero-valued oracle does not discriminate index-sensitive copying.
- A failed case identifies a problem class spanning support-gated module/program processing and the shared compute/output path; the buffer oracle does not name one failing implementation layer or establish debug-metadata consumption.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Compute specification | [`getComputeShaderSpec`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L45-L59) | Defines SPIR-V 1.6, required input/output buffers, and the dispatch size. |
| Support and program setup | [`checkSupport` and `initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L107-L117) | Requires both extensions and submits the embedded assembly to the SPIR-V builder. |
| Execution | [`SpvAsmSpirvRelaxedForwardReferenceBasicInstance::iterate`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L81-L84) | Delegates execution to the common compute shader instance. |
| Forward-reference records | [`kStaticMethodShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L147-L278) | Contains the complete CTS-authored SPIR-V module and the `%35`/`%38` to `%37` references. |
| Family registration | [`createRelaxedWithForwardReferenceGraphicsGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L280-L293) | Registers `relaxed_with_forward_reference.static_method_shader`. |
| Mustpass coverage | [Vulkan](../../../mustpass/main/vk-default/spirv-assembly.txt#L16125) and [Vulkan SC](../../../mustpass/main/vksc-default/spirv-assembly.txt#L5590) | Confirms the single leaf in both default inventories. |
