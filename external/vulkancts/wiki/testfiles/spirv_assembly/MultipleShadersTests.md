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

The test has no GLSL or HLSL source. `Programs::init` constructs CTS-authored SPIR-V assembly strings. The two leaves need separate walkthroughs because their execution-mode and interface declarations differ. The source records explicit SPIR-V 1.5 build options only for the first leaf and does not document a separate generation-time `spirv-as`/`spirv-val`/`spirv-dis` gate. This `spirv_assembly` page deliberately does not publish a separate disassembly block.

### Representative Shader Walkthrough 1: `two_entry_points_execution_mode_id`

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

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for <code>two_entry_points_execution_mode_id</code></summary>

```llvm
OpCapability Shader
%1 = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %mainA "mainA" %inOutVar %gl_LocalInvocationIndex
OpEntryPoint GLCompute %mainB "mainB" %inOutVar %gl_LocalInvocationIndex
OpExecutionModeId %mainA LocalSizeId %uint_2 %uint_3 %uint_1
OpExecutionModeId %mainB LocalSizeId %uint_2 %uint_3 %uint_1
OpDecorate %runtimearr_int ArrayStride 4
OpMemberDecorate %InOut 0 Offset 0
OpDecorate %InOut Block
OpDecorate %inOutVar DescriptorSet 0
OpDecorate %inOutVar Binding 0
OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
%void = OpTypeVoid
%int = OpTypeInt 32 1
%uint = OpTypeInt 32 0
%v3uint = OpTypeVector %uint 3
%void_fun = OpTypeFunction %void
%uint_fun = OpTypeFunction %uint
%runtimearr_int = OpTypeRuntimeArray %int
%InOut = OpTypeStruct %runtimearr_int
%ptr_Uniform_InOut = OpTypePointer StorageBuffer %InOut
%ptr_Uniform_int = OpTypePointer StorageBuffer %int
%ptr_uint_fun = OpTypePointer Function %uint
%ptr_v3uint_input = OpTypePointer Input %v3uint
%ptr_uint_input = OpTypePointer Input %uint
%int_0 = OpConstant %int 0
%uint_1 = OpConstant %uint 1
%uint_2 = OpConstant %uint 2
%uint_3 = OpConstant %uint 3
%uint_6 = OpConstant %uint 6
%uint_12 = OpConstant %uint 12
%uint_18 = OpConstant %uint 18
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_2 %uint_3 %uint_1
%gl_LocalInvocationIndex = OpVariable %ptr_uint_input Input
%inOutVar = OpVariable %ptr_Uniform_InOut StorageBuffer
%mainA = OpFunction %void None %void_fun
%labelA = OpLabel
%idxA = OpLoad %uint %gl_LocalInvocationIndex
%30 = OpIAdd %uint %uint_12 %idxA
%33 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %idxA
%34 = OpLoad %int %33
%37 = OpIAdd %uint %uint_6 %idxA
%38 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %37
%39 = OpLoad %int %38
%40 = OpISub %int %34 %39
%41 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %30
OpStore %41 %40
OpReturn
OpFunctionEnd
%mainB = OpFunction %void None %void_fun
%labelB = OpLabel
%idxB = OpLoad %uint %gl_LocalInvocationIndex
%60 = OpIAdd %uint %uint_18 %idxB
%63 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %idxB
%64 = OpLoad %int %63
%67 = OpIAdd %uint %uint_6 %idxB
%68 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %67
%69 = OpLoad %int %68
%70 = OpIMul %int %64 %69
%71 = OpAccessChain %ptr_Uniform_int %inOutVar %int_0 %60
OpStore %71 %70
OpReturn
OpFunctionEnd
```

</details>

#### Additional Info

- `%gl_LocalInvocationIndex` gives each of the six local invocations its scalar index; `%gl_WorkGroupSize` contains the `2 x 3 x 1` constant composite.
- `mainA` and `mainB` list the same storage-buffer variable and built-in in their `OpEntryPoint` instructions. This leaf does not test descriptor separation.
- The source attaches `SpirVAsmBuildOptions` with SPIR-V 1.5 to this assembly ([builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L237-L329)).

#### Parameter Variation Summary

| Parameter dimension | Assembly-level variation from this assembly | Evidence |
|---------------------|---------------------------------------------|----------|
| Test case leaf | Replaces `LocalSizeId`, the shared `%inOutVar` interface, and result-range arithmetic with literal `LocalSize`, distinct interface lists, and two storage-buffer declarations. | [second builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L331-L436) |
| Pipeline selection | The module remains shared, but `pName` changes from `mainB` to `mainA` when the host creates the second pipeline. | [pipeline creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L148-L178) |

### Representative Shader Walkthrough 2: `two_entry_points_different_interfaces`

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

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for <code>two_entry_points_different_interfaces</code></summary>

```llvm
OpCapability Shader
%1 = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %mainA "mainA" %gl_LocalInvocationIndex
OpEntryPoint GLCompute %mainB "mainB" %gl_NumWorkGroups %gl_LocalInvocationId
OpExecutionMode %mainA LocalSize 3 2 1
OpExecutionMode %mainB LocalSize 3 2 1
OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
OpDecorate %gl_LocalInvocationId BuiltIn LocalInvocationId
OpDecorate %int_runtime_array ArrayStride 4
OpMemberDecorate %struct_type 0 Offset 0
OpDecorate %struct_type BufferBlock
OpDecorate %var_BufferA DescriptorSet 0
OpDecorate %var_BufferA Binding 0
OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
OpDecorate %var_BufferB DescriptorSet 0
OpDecorate %var_BufferB Binding 1
%void = OpTypeVoid
%void_fun = OpTypeFunction %void
%uint = OpTypeInt 32 0
%int = OpTypeInt 32 1
%ptr_uint_fun = OpTypePointer Function %uint
%v3uint = OpTypeVector %uint 3
%ptr_uint_input = OpTypePointer Input %uint
%ptr_v3uint_input = OpTypePointer Input %v3uint
%int_runtime_array = OpTypeRuntimeArray %int
%struct_type = OpTypeStruct %int_runtime_array
%25 = OpTypePointer Uniform %struct_type
%ptr_uniform_int = OpTypePointer Uniform %int
%int_0 = OpConstant %int 0
%uint_0 = OpConstant %uint 0
%uint_1 = OpConstant %uint 1
%uint_2 = OpConstant %uint 2
%uint_3 = OpConstant %uint 3
%uint_6 = OpConstant %uint 6
%uint_12 = OpConstant %uint 12
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_3 %uint_2 %uint_1
%gl_LocalInvocationIndex = OpVariable %ptr_uint_input Input
%gl_NumWorkGroups = OpVariable %ptr_v3uint_input Input
%gl_LocalInvocationId = OpVariable %ptr_v3uint_input Input
%var_BufferA = OpVariable %25 Uniform
%var_BufferB = OpVariable %25 Uniform
%mainA = OpFunction %void None %void_fun
%labelA = OpLabel
%idxA = OpLoad %uint %gl_LocalInvocationIndex
%inA1_location = OpAccessChain %ptr_uniform_int %var_BufferA %int_0 %idxA
%inA1 = OpLoad %int %inA1_location
%inA2_index = OpIAdd %uint %uint_6 %idxA
%inA2_location = OpAccessChain %ptr_uniform_int %var_BufferA %int_0 %inA2_index
%inA2 = OpLoad %int %inA2_location
%outA_index = OpIAdd %uint %uint_12 %idxA
%add_result = OpIAdd %int %inA1 %inA2
%outA_location = OpAccessChain %ptr_uniform_int %var_BufferA %int_0 %outA_index
OpStore %outA_location %add_result
OpReturn
OpFunctionEnd
%mainB = OpFunction %void None %void_fun
%labelB = OpLabel
%local_x_location = OpAccessChain %ptr_uint_input %gl_LocalInvocationId %uint_0
%local_x = OpLoad %uint %local_x_location
%local_x_times_2 = OpIMul %uint %local_x %uint_2
%local_y_location = OpAccessChain %ptr_uint_input %gl_LocalInvocationId %uint_1
%local_y = OpLoad %uint %local_y_location
%idxOut = OpIAdd %int %local_x_times_2 %local_y
%group_count_location = OpAccessChain %ptr_uint_input %gl_NumWorkGroups %uint_0
%group_count = OpLoad %uint %group_count_location
%sub_result = OpISub %int %uint_6 %group_count
%idxIn = OpISub %int %sub_result %idxOut
%inB1_location = OpAccessChain %ptr_uniform_int %var_BufferB %int_0 %idxIn
%inB1 = OpLoad %int %inB1_location
%inB2_index = OpIAdd %uint %uint_6 %idxIn
%inB2_location = OpAccessChain %ptr_uniform_int %var_BufferB %int_0 %inB2_index
%inB2 = OpLoad %int %inB2_location
%outB_index = OpIAdd %uint %uint_12 %idxOut
%mul_result = OpIMul %int %inB1 %inB2
%outB_location = OpAccessChain %ptr_uniform_int %var_BufferB %int_0 %outB_index
OpStore %outB_location %mul_result
OpReturn
OpFunctionEnd
```

</details>

#### Additional Info

- This builder does not append the explicit `SpirVAsmBuildOptions` object used by the first leaf; the page does not infer a target version beyond the source evidence.
- The assembly uses the legacy `BufferBlock` plus `Uniform` storage-buffer form. `%var_BufferA` and `%var_BufferB` differ only in their binding decorations and their entry-point use.
- The host still binds one descriptor set containing both bindings before each dispatch ([descriptor and dispatch setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L118-L199)).

#### Parameter Variation Summary

| Parameter dimension | Assembly-level variation from this assembly | Evidence |
|---------------------|---------------------------------------------|----------|
| Test case leaf | Replaces literal `LocalSize` and separate buffer interfaces with `LocalSizeId` and one shared binding. | [first builder branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L244-L329) |
| Entry point | `mainA` loads the flat local index; `mainB` reads the local-ID vector and number of workgroups to calculate reversed input positions. | [function bodies](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L393-L434) |

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
