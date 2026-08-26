## Overview

**Core question:** Can two compute pipelines select and execute different entry points from one CTS-authored SPIR-V module, including entry-point-specific execution modes and interfaces?

- [`vktSpvAsmMultipleShadersTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L78-L463) implements the `multiple_shaders_extended` test family beneath `spirv_assembly.instruction.compute`.
- Each executable test case leaf creates one `VkShaderModule`, creates a compute pipeline for `mainB` and another for `mainA`, dispatches both pipelines, and checks their integer stores on the host.
- The first leaf exercises two `OpExecutionModeId ... LocalSizeId` instructions in one module. The second leaf gives the two entry points different declared interfaces and routes them to different storage-buffer bindings.
- This page documents the authored assembly, host execution order, result oracle, and the limits of diagnosing a failure from the final buffer contents.

## Background Knowledge

- A SPIR-V module can declare several `OpEntryPoint` instructions. A compute pipeline selects one with `VkPipelineShaderStageCreateInfo::pName`; the name must identify an entry point with the compute execution model ([pipeline validity rule](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1183-L1186)).
- `OpExecutionMode LocalSize` records literal workgroup dimensions. `OpExecutionModeId LocalSizeId` names IDs that provide those dimensions; `VK_KHR_maintenance4` enables Vulkan support for `LocalSizeId` ([extension appendix](../../../../vulkan-docs/src/appendices/VK_KHR_maintenance4.adoc#L38-L40)).
- An `OpEntryPoint` interface list identifies the module-scope variables used by that entry point. The module can still declare other variables for another entry point.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.multiple_shaders_extended
├── two_entry_points_execution_mode_id
└── two_entry_points_different_interfaces
```

The parent compute registration adds this test family under `spirv_assembly.instruction.compute` ([parent registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21425)). The default Vulkan mustpass list contains the same two executable leaves ([mustpass entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L7488-L7489)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `two_entry_points_execution_mode_id`, `two_entry_points_different_interfaces` | Selects the multi-entry-point module form and the property under test. | [case construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L449-L460) |
| Entry-point name | `mainA`, `mainB` | Selects the function used when the host creates each compute pipeline from the shared module. | [pipeline stages](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L148-L178) |
| Buffer interface | binding `0` only, or bindings `0` and `1` | The first leaf shares one buffer; the second leaf gives `mainA` and `mainB` distinct storage buffers. | [descriptor setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L118-L141) |
| Workgroup size | `2 x 3 x 1` with `LocalSizeId`, `3 x 2 x 1` with `LocalSize` | Both forms produce six local invocations for a `1 x 1 x 1` dispatch. | [assembly builders](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L260-L329) and [#L349-L436](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L349-L436) |

## Behavior Parameters

The primary behavioral axis is the registered **test case leaf**. Each leaf selects a different module shape, while the common host flow still creates two pipelines from one module and dispatches `mainB` before `mainA`.

### `two_entry_points_execution_mode_id`: entry-point-specific `LocalSizeId`

This leaf gives both compute entry points their own `OpExecutionModeId ... LocalSizeId %uint_2 %uint_3 %uint_1` instruction. They share binding `0`, but `mainB` writes products to elements `18` through `23` and `mainA` writes differences to `12` through `17`. The support check requires `VK_KHR_maintenance4` ([support gate](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L445)).

### `two_entry_points_different_interfaces`: different entry-point interface lists

This leaf uses literal `LocalSize 3 2 1` execution modes. `mainA` declares `gl_LocalInvocationIndex` in its entry-point interface and accesses binding `0`; `mainB` declares `gl_NumWorkGroups` and `gl_LocalInvocationId` and accesses binding `1`. It writes a reversed-index product to `bufferB[12..17]` while `mainA` writes sums to `bufferA[12..17]`.

## Shader Analysis

The test has no GLSL or HLSL source. [`Programs::init`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L235-L436) constructs each shader module directly as CTS-authored SPIR-V assembly, so the assembly is the authoritative shader source rather than a reconstruction from a higher-level language. Each representative module below was assembled with `spirv-as`, validated with `spirv-val`, disassembled with `spirv-dis`, then round-trip checked by reassembling and revalidating the complete disassembly in the same SPIR-V environment.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.multiple_shaders_extended.two_entry_points_execution_mode_id
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `OpExecutionModeId ... LocalSizeId` | Associates a `2 x 3 x 1` local size with each selected entry point through constant IDs. |
| binding `0` | Both functions load and store through `%inOutVar`. |
| `mainB` then `mainA` | Preserves both operations because their output ranges do not overlap. |

#### Purpose

Check that pipeline creation by `pName` preserves the two entry points and their `LocalSizeId` execution-mode declarations in one module. Six invocations of each function read the same input range and store different arithmetic results.

#### Structural Design

| Function | Inputs | Operation | Output |
|----------|--------|-----------|--------|
| `mainA` | `%inOutVar[id]`, `%inOutVar[6 + id]` | `OpISub` | `%inOutVar[12 + id]` |
| `mainB` | `%inOutVar[id]`, `%inOutVar[6 + id]` | `OpIMul` | `%inOutVar[18 + id]` |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies one shader module directly as SPIR-V assembly with the `GLCompute` entry points `mainA` and `mainB`. The C++ assembly builder is the authoritative shader source, and the complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- `%gl_LocalInvocationIndex` gives each of the six local invocations its scalar index; `%gl_WorkGroupSize` contains the `2 x 3 x 1` constant composite.
- `mainA` and `mainB` list the same storage-buffer variable and built-in in their `OpEntryPoint` instructions. This leaf does not test descriptor separation.
- The source attaches `SpirVAsmBuildOptions` with SPIR-V 1.5 to this assembly ([builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L237-L329)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------------|----------|
| Test case leaf | Replaces `LocalSizeId`, the shared `%inOutVar` interface, and result-range arithmetic with literal `LocalSize`, distinct interface lists, and two storage-buffer declarations. | [second builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L331-L436) |
| Pipeline selection | The module remains shared, but `pName` changes from `mainB` to `mainA` when the host creates the second pipeline. | [pipeline creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L148-L178) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`mainA`, `mainB`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 47
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "mainA" %3 %gl_LocalInvocationIndex
               OpEntryPoint GLCompute %5 "mainB" %3 %gl_LocalInvocationIndex
               OpExecutionModeId %2 LocalSizeId %uint_2 %uint_3 %uint_1
               OpExecutionModeId %5 LocalSizeId %uint_2 %uint_3 %uint_1
               OpDecorate %_runtimearr_int ArrayStride 4
               OpMemberDecorate %_struct_10 0 Offset 0
               OpDecorate %_struct_10 Block
               OpDecorate %3 DescriptorSet 0
               OpDecorate %3 Binding 0
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
        %int = OpTypeInt 32 1
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
         %16 = OpTypeFunction %void
         %17 = OpTypeFunction %uint
%_runtimearr_int = OpTypeRuntimeArray %int
 %_struct_10 = OpTypeStruct %_runtimearr_int
%_ptr_StorageBuffer__struct_10 = OpTypePointer StorageBuffer %_struct_10
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_Input_uint = OpTypePointer Input %uint
      %int_0 = OpConstant %int 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_6 = OpConstant %uint 6
    %uint_12 = OpConstant %uint 12
    %uint_18 = OpConstant %uint 18
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_2 %uint_3 %uint_1
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
          %3 = OpVariable %_ptr_StorageBuffer__struct_10 StorageBuffer
          %2 = OpFunction %void None %16
         %27 = OpLabel
         %28 = OpLoad %uint %gl_LocalInvocationIndex
         %29 = OpIAdd %uint %uint_12 %28
         %30 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %28
         %31 = OpLoad %int %30
         %32 = OpIAdd %uint %uint_6 %28
         %33 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %32
         %34 = OpLoad %int %33
         %35 = OpISub %int %31 %34
         %36 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %29
               OpStore %36 %35
               OpReturn
               OpFunctionEnd
          %5 = OpFunction %void None %16
         %37 = OpLabel
         %38 = OpLoad %uint %gl_LocalInvocationIndex
         %39 = OpIAdd %uint %uint_18 %38
         %40 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %38
         %41 = OpLoad %int %40
         %42 = OpIAdd %uint %uint_6 %38
         %43 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %42
         %44 = OpLoad %int %43
         %45 = OpIMul %int %41 %44
         %46 = OpAccessChain %_ptr_StorageBuffer_int %3 %int_0 %39
               OpStore %46 %45
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.multiple_shaders_extended.two_entry_points_different_interfaces
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `mainA` interface | Lists `%gl_LocalInvocationIndex` and uses `%var_BufferA` at binding `0`. |
| `mainB` interface | Lists `%gl_NumWorkGroups` and `%gl_LocalInvocationId` and uses `%var_BufferB` at binding `1`. |
| `LocalSize 3 2 1` | Produces six local invocation positions used to form output and reversed input indices. |

#### Purpose

Check that two entry points in one module can retain different interfaces. `mainA` performs addition through binding `0`, while `mainB` derives a reversed input index from built-ins and performs multiplication through binding `1`.

#### Structural Design

| Function | Interface and indexing | Operation | Output |
|----------|------------------------|-----------|--------|
| `mainA` | `%gl_LocalInvocationIndex` | `bufferA[idx] + bufferA[6 + idx]` | `bufferA[12 + idx]` |
| `mainB` | `%gl_LocalInvocationId`, `%gl_NumWorkGroups`; `idxOut = 2 * local_x + local_y`, `idxIn = 6 - group_count.x - idxOut` | `bufferB[idxIn] * bufferB[6 + idxIn]` | `bufferB[12 + idxOut]` |

For the recorded `1 x 1 x 1` dispatch, `group_count.x` is `1`, so `idxIn` is `5 - idxOut`.

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies one shader module directly as SPIR-V assembly with the `GLCompute` entry points `mainA` and `mainB`. The C++ assembly builder is the authoritative shader source, and the complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- This builder uses the `vk::SourceCollections` default SPIR-V target because it does not append the explicit `SpirVAsmBuildOptions` object used by the first leaf; the baseline target is SPIR-V 1.0.
- The assembly uses the legacy `BufferBlock` plus `Uniform` storage-buffer form. `%var_BufferA` and `%var_BufferB` differ in their binding decorations and in which entry point uses them.
- The host still binds one descriptor set containing both bindings before each dispatch ([descriptor and dispatch setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L118-L199)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------------|----------|
| Test case leaf | Replaces literal `LocalSize` and separate buffer interfaces with `LocalSizeId` and one shared binding. | [first builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L244-L329) |
| Entry point | `mainA` loads the flat local index; `mainB` reads the local-ID vector and number of workgroups to calculate reversed input positions. | [function bodies](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L393-L434) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`mainA`, `mainB`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 58
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "mainA" %gl_LocalInvocationIndex
               OpEntryPoint GLCompute %4 "mainB" %gl_NumWorkGroups %gl_LocalInvocationID
               OpExecutionMode %2 LocalSize 3 2 1
               OpExecutionMode %4 LocalSize 3 2 1
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %_runtimearr_int ArrayStride 4
               OpMemberDecorate %_struct_8 0 Offset 0
               OpDecorate %_struct_8 BufferBlock
               OpDecorate %9 DescriptorSet 0
               OpDecorate %9 Binding 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %11 DescriptorSet 0
               OpDecorate %11 Binding 1
       %void = OpTypeVoid
         %13 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_runtimearr_int = OpTypeRuntimeArray %int
  %_struct_8 = OpTypeStruct %_runtimearr_int
%_ptr_Uniform__struct_8 = OpTypePointer Uniform %_struct_8
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_6 = OpConstant %uint 6
    %uint_12 = OpConstant %uint 12
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_3 %uint_2 %uint_1
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %9 = OpVariable %_ptr_Uniform__struct_8 Uniform
         %11 = OpVariable %_ptr_Uniform__struct_8 Uniform
          %2 = OpFunction %void None %13
         %29 = OpLabel
         %30 = OpLoad %uint %gl_LocalInvocationIndex
         %31 = OpAccessChain %_ptr_Uniform_int %9 %int_0 %30
         %32 = OpLoad %int %31
         %33 = OpIAdd %uint %uint_6 %30
         %34 = OpAccessChain %_ptr_Uniform_int %9 %int_0 %33
         %35 = OpLoad %int %34
         %36 = OpIAdd %uint %uint_12 %30
         %37 = OpIAdd %int %32 %35
         %38 = OpAccessChain %_ptr_Uniform_int %9 %int_0 %36
               OpStore %38 %37
               OpReturn
               OpFunctionEnd
          %4 = OpFunction %void None %13
         %39 = OpLabel
         %40 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %41 = OpLoad %uint %40
         %42 = OpIMul %uint %41 %uint_2
         %43 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_1
         %44 = OpLoad %uint %43
         %45 = OpIAdd %int %42 %44
         %46 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %47 = OpLoad %uint %46
         %48 = OpISub %int %uint_6 %47
         %49 = OpISub %int %48 %45
         %50 = OpAccessChain %_ptr_Uniform_int %11 %int_0 %49
         %51 = OpLoad %int %50
         %52 = OpIAdd %uint %uint_6 %49
         %53 = OpAccessChain %_ptr_Uniform_int %11 %int_0 %52
         %54 = OpLoad %int %53
         %55 = OpIAdd %uint %uint_12 %45
         %56 = OpIMul %int %51 %54
         %57 = OpAccessChain %_ptr_Uniform_int %11 %int_0 %55
               OpStore %57 %56
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates two 24-element, host-visible storage buffers and fills `bufferA` with `dataASrc` and `bufferB` with `dataBSrc`. It only adds binding `1` to the descriptor-set layout for `two_entry_points_different_interfaces` ([resource and descriptor setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L86-L141)).
- It creates one shader module from the selected assembly, then creates `pipelineB` with `pName = "mainB"` and `pipelineA` with `pName = "mainA"` ([module and pipeline creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L143-L178)).
- The command buffer records a host-write to compute-shader-read memory barrier, binds `pipelineB`, binds the descriptor set, and dispatches `1 x 1 x 1`. It then binds `pipelineA` and dispatches the same dimensions ([command sequence](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L180-L201)).
- After `submitCommandsAndWait`, the host invalidates `bufferA`; the different-interface leaf also invalidates `bufferB`. The first mismatch in the exact integer comparisons fails the test case ([result checks](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L203-L232)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `two_entry_points_execution_mode_id` | Selection of `mainA` or `mainB` by `pName` is wrong; `LocalSizeId` execution-mode handling is wrong; the shared binding-0 storage-buffer accesses or result stores are wrong. |
| `two_entry_points_different_interfaces` | Selection of an entry point is wrong; the per-entry-point interface or binding-0/binding-1 routing is wrong; `mainB` computes its local-ID-based reversed index incorrectly. |

Both leaves also depend on the recorded host-write-to-compute-read barrier and ordered dispatches. Their readback cannot isolate a shared setup or synchronization fault from entry-point handling when both leaves fail.

### Cause Analysis

#### Entry-point selection

**Possible failure symptoms:** either leaf produces wrong result slots after the host builds pipelines with `pName = "mainA"` and `pName = "mainB"`, or pipeline creation fails for a named entry point.

**Possible implementation causes:** the implementation may resolve `pName` to the wrong `OpEntryPoint`, fail to retain one entry point while creating the shared shader module, or associate the pipeline with the wrong function. The final oracle cannot distinguish this from a wrong arithmetic instruction or storage access without additional implementation investigation.

#### Execution-mode and built-in handling

**Possible failure symptoms:** `two_entry_points_execution_mode_id` has incorrect or incomplete stores in its two result ranges, or only `two_entry_points_different_interfaces` has wrong reversed products.

**Possible implementation causes:** the first leaf depends on the `LocalSizeId` declarations and the `VK_KHR_maintenance4` support path. The second depends on `gl_LocalInvocationId` and `gl_NumWorkGroups` values used in the index calculation. Source-level investigation is needed to separate execution-mode lowering from built-in delivery or integer-arithmetic faults.

#### Interface, descriptor, and storage-buffer access

**Possible failure symptoms:** the different-interface leaf can have correct `bufferA` additions but incorrect `bufferB` products, while the shared-interface leaf can fail one or both output ranges in `bufferA`.

**Possible implementation causes:** descriptor binding resolution, entry-point interface processing, access-chain addressing, or integer load/store handling can produce these results. Because a result mismatch records only the final buffer value, it cannot localize the fault to one of those implementation layers.

#### Shared host setup and ordering

**Possible failure symptoms:** both leaves fail, with values that suggest stale input data or missing results after the two recorded dispatches.

**Possible implementation causes:** the same host-write-to-compute-read barrier, descriptor binding sequence, command submission, and readback path serve both leaves. Investigate those shared paths before treating a paired failure as proof of a multi-entry-point defect.

## Case Pruning

### Requirement-based pruning

`two_entry_points_execution_mode_id` requests `VK_KHR_maintenance4` through `checkSupport`; an implementation without that functionality cannot run that supported configuration. The different-interface leaf has no source-level extension or feature request ([support check](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L445)).

### Design-based pruning

The source registers exactly two leaves. It holds the module count, pipeline count, descriptor set count, and dispatch count fixed so each leaf isolates one multi-entry-point form rather than constructing a wider matrix of local sizes or buffer layouts.

## Key Takeaways

- One `VkShaderModule` supplies both `mainA` and `mainB`; two compute pipelines select them with different `pName` values.
- The first test case leaf checks `LocalSizeId` declarations for both entry points. The second checks distinct entry-point interface lists and binding routes.
- Both leaves use exact host-side integer comparisons. A shared failure can originate in setup, synchronization, submission, or readback, so the final values alone do not isolate entry-point handling.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `EntryPointsTest::iterate` | [runtime and oracle](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L78-L233) | Creates resources and pipelines, records both dispatches, and checks the results. |
| `Programs::init` | [assembly builders](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L235-L436) | Provides both CTS-authored SPIR-V assembly strings. |
| `checkSupport` | [support gate](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L445) | Requires `VK_KHR_maintenance4` for the `LocalSizeId` leaf. |
| `createMultipleShaderExtendedGroup` | [family registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L449-L463) | Registers the two executable leaves. |
| Default mustpass entries | [spirv-assembly.txt#L7488-L7489](../../../mustpass/main/vk-default/spirv-assembly.txt#L7488-L7489) | Lists both Vulkan executable paths. |
| Pipeline entry-point rule | [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1183-L1186) | Grounds the `pName` and execution-model claim. |
| `LocalSizeId` support | [VK_KHR_maintenance4 appendix](../../../../vulkan-docs/src/appendices/VK_KHR_maintenance4.adoc#L38-L40) | Grounds the extension's relation to `LocalSizeId`. |
