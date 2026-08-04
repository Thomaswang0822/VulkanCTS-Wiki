## Overview

**Core question:** does the implementation correctly accept and execute the full SPIR-V 1.4 surface area (composite `OpSelect`, pointer comparison and difference, `OpCopyLogical`, `OpCopyMemory` access operands, `UniformId`, `NonWritable` on Function/Private variables, expanded entry-point interface listing, HLSL functionality decorations, new loop controls, `UConvert` inside `OpSpecConstantOp`, and integer wrap decorations) when `VK_KHR_spirv_1_4` is enabled?

- Source file: [`vktSpvAsmSpirvVersion1p4Tests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp). The file is an Amber dispatcher: it registers 13 test families under `spirv_assembly.instruction.spirv1p4` and routes each case to a hand-authored script under `data/vulkan/amber/spirv_assembly/instruction/spirv1p4/<subgroup>/<basename>.amber`. The file builds no shaders itself.
- The 13 families contain 102 registered leaves: `opcopylogical`, `opptrdiff`, `opptrequal`, `opptrnotequal`, `opcopymemory`, `uniformid`, `nonwritable`, `entrypoint`, `hlsl_functionality1`, `loop_control`, `opselect`, `uconvert`, and `wrap`.
- Each case adds the `VK_KHR_spirv_1_4` requirement and selects SPIR-V 1.4 assembly build options. Per-case feature gates layer on top: variable pointers, 16-bit storage, 64-bit integers, geometry shader, tessellation shader, and `VK_KHR_workgroup_memory_explicit_layout` depending on the subgroup.
- The page covers the registration tree, the per-family tested behavior, a representative shader walkthrough extracted from `opselect/scalar_select.amber`, the Amber-driven runtime flow, and per-family failure meaning.

## Background Knowledge

- **SPIR-V 1.4 entry-point interface rule.** `OpEntryPoint` must list every module-scope variable the entry point statically uses, including non-I/O variables. Drivers that follow the older SPIR-V 1.0/1.3 rule may reject valid 1.4 modules or mis-bind descriptors. The `entrypoint` family verifies this across stages and resource kinds.
- **Pointer comparison and difference.** SPIR-V 1.4 promotes `OpPtrEqual`, `OpPtrNotEqual`, and `OpPtrDiff` from extensions into core. They operate on `StorageBuffer`, `Workgroup`, and (with variable pointers) cross-variable contexts. `OpPtrEqual`/`OpPtrNotEqual` return a boolean; `OpPtrDiff` returns the element count between two pointers into the same array. Variable-pointer features (`VariablePointerFeatures.variablePointersStorageBuffer`, `VariablePointerFeatures.variablePointers`) gate the broader use cases.
- **`OpSelect` extension to composites.** SPIR-V 1.0 allowed `OpSelect` only on scalar or vector values. SPIR-V 1.4 extends it to arrays, structs, nested composites, and pointers. Workgroup-pointer selection also requires `VK_KHR_workgroup_memory_explicit_layout`.
- **`OpCopyLogical` and `OpCopyMemory` access operands.** `OpCopyLogical` produces a value with a different logical layout. For example, it can copy a UBO-layout struct into an SSBO-layout struct with different offsets, array strides, or matrix strides. `OpCopyMemory` in SPIR-V 1.4 supports the `Aligned` access operand form on source and target.
- **Decorations folded in from extensions.** SPIR-V 1.4 folds `SPV_KHR_no_integer_wrap_decoration` (`NoSignedWrap`, `NoUnsignedWrap`) and `SPV_GOOGLE_hlsl_functionality1` (`CounterBuffer`, `OpDecorateString`, `OpMemberDecorateString`) into core without extra extension declarations. `UniformId` and the `NonWritable` relaxation to Function/Private variables are also SPIR-V 1.4 features. `SPV_KHR_workgroup_memory_explicit_layout` is *not* folded in and remains a separate extension requirement for the workgroup-pointer `OpSelect` cases.
- **`UConvert` in `OpSpecConstantOp`.** SPIR-V 1.4 permits `UConvert` inside `OpSpecConstantOp`, enabling specialization-constant-time unsigned integer conversions between 16-bit, 32-bit, and 64-bit widths.
- **Loop control hints.** SPIR-V 1.4 adds `MinIterations`, `MaxIterations`, `IterationMultiple`, `PeelCount`, and `PartialCount` loop controls. They are hints, not requirements. A conformant implementation may ignore them.

## Registration Hierarchy

```text
spirv_assembly.instruction.spirv1p4
├── opcopylogical
├── opptrdiff
├── opptrequal
├── opptrnotequal
├── opcopymemory
├── uniformid
├── nonwritable
├── entrypoint
├── hlsl_functionality1
├── loop_control
├── opselect
├── uconvert
└── wrap
```

All 13 direct children of `spirv1p4` are test families registered by [`createSpirvVersion1p4Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409). [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21538) attaches that group below the instruction root.

### Registered-leaf and mustpass reconciliation

| Subgroup | Registered leaves |
|----------|-----------------:|
| `opcopylogical` | 11 |
| `opptrdiff` | 5 |
| `opptrequal` | 12 |
| `opptrnotequal` | 12 |
| `opcopymemory` | 3 |
| `uniformid` | 5 |
| `nonwritable` | 5 |
| `entrypoint` | 19 |
| `hlsl_functionality1` | 3 |
| `loop_control` | 5 |
| `opselect` | 12 |
| `uconvert` | 8 |
| `wrap` | 2 |
| **Total** | **102** |

The 102 registered `<subgroup>.<basename>` leaves exactly match the 102 `dEQP-VK.spirv_assembly.instruction.spirv1p4.*` paths in [`vk-default/spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt). No corresponding leaves appear in [`vksc-default/spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt): `addTestsForAmberFiles()` is compiled out by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `opcopylogical`, `opptrdiff`, `opptrequal`, `opptrnotequal`, `opcopymemory`, `uniformid`, `nonwritable`, `entrypoint`, `hlsl_functionality1`, `loop_control`, `opselect`, `uconvert`, `wrap` | Selects the SPIR-V 1.4 feature under test. This is the primary behavioral axis. | [`createSpirvVersion1p4Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L407) |
| Shader stage | `comp`, `frag`, `geom`, `tess_con`, `tess_eval`, `vert` | Stage prefix used by the `entrypoint` family; selects the pipeline stage and the entry-point interface that must list its module-scope variables. | [`entrypoint` case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L325) |
| Resource kind | push constant, SSBO, UBO, workgroup | Resource kind attached to the entry-point variable in the `entrypoint` family; each kind exercises a different storage class in the interface list. | [`entrypoint` case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L325) |
| Variable-pointer tier | `Varptr_ssbo`, `Varptr_full`, `Varptr_full_explicitLayout` | Cumulative feature tiers used by the pointer families. `Varptr_ssbo` adds `variablePointersStorageBuffer`; `Varptr_full` adds `variablePointers`; `Varptr_full_explicitLayout` adds `VK_KHR_workgroup_memory_explicit_layout` (used only by the `opselect/wg_*` cases). | [Feature vectors](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L139-L147) |
| Integer width tier | `Int16`, `Int16_storage`, `Int64` | Cumulative feature tiers used by the `uconvert` family. `Int16` adds `Features.shaderInt16`; `Int16_storage` adds `VK_KHR_16bit_storage` + `Storage16BitFeatures.storageBuffer16BitAccess`; `Int64` adds `Features.shaderInt64`. | [Feature vectors](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L148-L156) |
| Pointer storage | SSBO, Workgroup, Function, Private, null | Where the compared/diffed pointer lives. Varies per case within `opptrequal`, `opptrnotequal`, `opptrdiff`. | [`opptrequal` cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223), [`opptrnotequal` cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250), [`opptrdiff` cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196) |
| OpSelect composite kind | scalar, vector (scalar selector), vector (vector selector), array, struct, nested array, nested struct, SSBO pointer, workgroup pointer | The composite type selected by `OpSelect`. Scalar and vector-with-vector-selector forms are SPIR-V 1.0 regression cases; the rest are SPIR-V 1.4 new cases. | [`opselect` case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379) |
| Loop control hint | `iteration_multiple`, `max_iterations`, `min_iterations`, `partial_count`, `peel_count` | The SPIR-V 1.4 loop control hint applied to `OpLoopMerge`. Each case verifies the hint is accepted and the loop body still produces the expected copy. | [`loop_control` case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351) |

## Behavior Parameters

The primary behavioral axis is the test family. Each family targets a different SPIR-V 1.4 feature; the embedded Amber scripts and the per-case feature gates differ per family. Secondary axes (stage, resource kind, variable-pointer tier, integer width tier, pointer storage, OpSelect composite kind, loop control hint) appear within families and are documented in `## Parameter Dimensions and Observed Values`.

### `opcopylogical`: `OpCopyLogical` between different logical layouts

Tests `OpCopyLogical` across layout conversions: different matrix layouts, different matrix strides, nested arrays with different inner/outer strides, two IDs pointing at the same array or struct, and UBO↔SSBO layout conversions. The 11 registered cases are listed in the [`opcopylogical`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L183) case group. No additional feature requirements beyond `VK_KHR_spirv_1_4`.

### `opptrdiff`: `OpPtrDiff` element-count computation

Tests `OpPtrDiff` within SSBO and Workgroup storage, including cases where the pointer is stored in a Private variable. Cases split across `Varptr_ssbo` (SSBO-only) and `Varptr_full` (Workgroup). The 5 registered cases are listed in the [`opptrdiff`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196) case group.

### `opptrequal`: `OpPtrEqual` boolean comparison

Tests `OpPtrEqual` against different SSBO variables, different Workgroup variables, null pointers, simple variable-pointer operands, and pointers stored in Function or Private variables. Cases split across `Varptr_ssbo` and `Varptr_full`. The 12 registered cases are listed in the [`opptrequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223) case group.

### `opptrnotequal`: `OpPtrNotEqual` boolean comparison

Mirrors `opptrequal` with `OpPtrNotEqual`. Same 12-case shape, same variable-pointer tiers, same storage and null-pointer coverage. The registered cases are listed in the [`opptrnotequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250) case group.

### `opcopymemory`: `OpCopyMemory` with access operands

Tests `OpCopyMemory` with different source/target alignments, no source access operands, and no target access operands. The `different_alignments` case issues four `OpCopyMemory` calls with `Aligned 16 Aligned 4`. The 3 registered cases are listed in the [`opcopymemory`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L252-L259) case group.

### `uniformid`: `OpDecorateId UniformId` propagation

Tests workgroup and subgroup uniform load (`OpDecorateId ... UniformId %workgroup` or `%subgroup`) and verifies the result is consistent across invocations, including under partially active control flow. The 5 registered cases are listed in the [`uniformid`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L261-L272) case group. The subgroup cases assume a subgroup size ≤ 8 because the compute dispatch uses `LocalSize 8 1 1`.

### `nonwritable`: `NonWritable` on Function/Private variables

Tests that `NonWritable` decorates Function variables (single and multiple) and Private variables (single and multiple), including a case where the decorated Function variable lives in a non-entry-point function. The 5 registered cases are listed in the [`nonwritable`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L274-L285) case group.

### `entrypoint`: entry-point interface lists all module-scope variables

Tests the SPIR-V 1.4 entry-point interface rule across 6 stages (`comp`, `frag`, `geom`, `tess_con`, `tess_eval`, `vert`). Compute covers push constant, SSBO, UBO, and Workgroup variables; each other stage covers push constant, SSBO, and UBO variables, for 19 cases. Geometry cases require `Features.geometryShader`; tessellation cases require `Features.tessellationShader`. The registered list is in the [`entrypoint`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L327) case group.

### `hlsl_functionality1`: `CounterBuffer`, `OpDecorateString`, `OpMemberDecorateString`

Tests the SPV_GOOGLE_hlsl_functionality1 features folded into SPIR-V 1.4. The `counter_buffer` case uses `OpDecorateId ... CounterBuffer ...` to associate a counter SSBO with a runtime-sized SSBO and verifies the increment/decrement counters update correctly. The 3 registered cases are listed in the [`hlsl_functionality1`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L329-L337) case group.

### `loop_control`: SPIR-V 1.4 loop control hints

Tests `IterationMultiple`, `MaxIterations`, `MinIterations`, `PartialCount`, and `PeelCount` loop controls on `OpLoopMerge`. Each case verifies the SPIR-V is accepted and the loop body still copies the expected input array to the output array. The 5 registered cases are listed in the [`loop_control`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351) case group.

### `opselect`: `OpSelect` on scalars, vectors, composites, and pointers

Tests `OpSelect` across scalar, vector (scalar and vector selectors), array, struct, nested array, nested struct, SSBO pointer, and workgroup pointer cases. The scalar, vector-element, and same-buffer pointer cases are SPIR-V 1.0 regression cases run under SPIR-V 1.4 build options; the array, struct, nested, and pointer-pair cases are SPIR-V 1.4 new behavior. The workgroup-pointer cases require `VK_KHR_workgroup_memory_explicit_layout`. The 12 registered cases are listed in the [`opselect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379) case group.

### `uconvert`: `UConvert` inside `OpSpecConstantOp`

Tests `UConvert` extend, truncate, and zero-extend cases inside `OpSpecConstantOp` across 16-bit, 32-bit, and 64-bit widths. Cases split across `Int16` (extend from 16-bit), `Int16_storage` (truncate to 16-bit), and `Int64` (extend to / truncate from 64-bit). The 8 registered cases are listed in the [`uconvert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L381-L399) case group.

### `wrap`: `NoSignedWrap` / `NoUnsignedWrap` decorations

Tests that `NoSignedWrap` and `NoUnsignedWrap` decorations on integer arithmetic are accepted and do not change the result for the test input. The 2 registered cases are listed in the [`wrap`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L401-L407) case group.

## Shader Analysis

This page covers 13 test families. A single representative walkthrough shows the common Amber mechanism: each script supplies literal SPIR-V assembly and a `[test]` block, while the C++ file registers the script and requirements. The walkthrough uses `spirv_assembly.instruction.spirv1p4.opselect.scalar_select` because it is the smallest case in the file and exercises the SPIR-V 1.0 scalar `OpSelect` form under SPIR-V 1.4 build options. It serves as a baseline for the composite-select cases that are the actual SPIR-V 1.4 surface.

Per the category-scoped convention for Amber-backed SPIR-V pages, the SPIR-V assembly is extracted from the Amber script and placed under `#### Source Code` (unfoldable). The `#### SPIR-V` collapsed subsection that the standard walkthrough template requires is omitted because it would duplicate the literal assembly already shown in `#### Source Code`. The assembly is hand-authored CTS test data, so disassembly byte identity is not required; this audit nevertheless validated the exact extracted fence with `spirv-as --target-env spv1.4`, `spirv-val --target-env vulkan1.2`, and `spirv-dis`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.spirv1p4.opselect.scalar_select
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Test family `opselect` | Selects the `OpSelect` family. |
| Case leaf `scalar_select` | Selects the SPIR-V 1.0 scalar form of `OpSelect` run under SPIR-V 1.4 build options. The composite-select cases in the same family are the actual SPIR-V 1.4 new behavior; this case is the smallest reference for the dispatch/probe pattern. |
| No extra feature requirements | Only `VK_KHR_spirv_1_4` is required. The variable-pointer and workgroup-memory-explicit-layout requirements apply to other `opselect` cases, not this one. |
| `SpirVAsmBuildOptions(VK_MAKE_API_VERSION(0, 1, 1, 0), vk::SPIRV_VERSION_1_4)` with `supports_VK_KHR_spirv_1_4 = true` | Build options applied by [`addTestsForAmberFiles()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L83-L84). |

#### Purpose

Verify that the scalar form of `OpSelect` (`%result = OpSelect %int %condition %true_value %false_value`) still produces the expected per-invocation result when the SPIR-V module is built and validated as SPIR-V 1.4. The shader selects `1` when the input element is `0` and `2` otherwise, and writes the selected value to the output SSBO at the same index. The host checks the full output array after a 2-invocation dispatch.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| Entry point declaration | `OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %_ %__0` lists the input built-in and both SSBO variables. | The SPIR-V 1.4 entry-point interface rule requires listing all module-scope variables, including non-I/O. This is the same rule the `entrypoint` family tests explicitly. |
| Decorations | `%_` (output SSBO) is decorated with `Block`, `DescriptorSet 0`, `Binding 1`, `ArrayStride 4` on the runtime array, and `Offset 0` on the single struct member. `%__0` (input SSBO) is decorated identically but with `Binding 0`. `gl_GlobalInvocationID` is decorated `BuiltIn GlobalInvocationId`. | The decorations bind the two SSBOs to descriptor set 0 bindings 0 and 1 with a 4-byte `int` runtime array. The host `[test]` block must match. |
| Body | Load `gl_GlobalInvocationID.z` (the dispatch index); load `input[z]`; compute `OpIEqual %bool %input %int_0`; `OpSelect %int %eq %int_1 %int_2`; store to `output[z]`. | The `OpSelect` is the tested instruction. The `OpIEqual` produces the scalar boolean selector; `OpSelect` returns `1` when the input is `0` and `2` otherwise. |
| Dispatch | `LocalSize 1 1 1`, dispatched as `compute 1 1 2`. | Two invocations along Z. The host writes `input = {0, 1}` and expects `output = {1, 2}`. |

#### Source Code

SPIR-V assembly extracted from [`opselect/scalar_select.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/opselect/scalar_select.amber). The text between `[compute shader spirv]` and `[test]` is the embedded SPIR-V assembly the Amber runner compiles for this case.

```llvm
; OpSelect among scalars. This is in SPIR-V 1.0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %_ %__0
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 430
               OpSourceExtension "GL_GOOGLE_cpp_style_line_directive"
               OpSourceExtension "GL_GOOGLE_include_directive"
               OpName %main "main"
               OpName %output_buffer "output_buffer"
               OpMemberName %output_buffer 0 "out_SSBO"
               OpName %_ ""
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %input_buffer "input_buffer"
               OpMemberName %input_buffer 0 "data_SSBO"
               OpName %__0 ""
               OpDecorate %_runtimearr_int ArrayStride 4
               OpMemberDecorate %output_buffer 0 Offset 0
               OpDecorate %output_buffer Block
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_ Binding 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_int_0 ArrayStride 4
               OpMemberDecorate %input_buffer 0 Offset 0
               OpDecorate %input_buffer Block
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %__0 Binding 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_runtimearr_int = OpTypeRuntimeArray %int
%output_buffer = OpTypeStruct %_runtimearr_int
%_ptr_StorageBuffer_output_buffer = OpTypePointer StorageBuffer %output_buffer
          %_ = OpVariable %_ptr_StorageBuffer_output_buffer StorageBuffer
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
%_runtimearr_int_0 = OpTypeRuntimeArray %int
%input_buffer = OpTypeStruct %_runtimearr_int_0
%_ptr_StorageBuffer_input_buffer = OpTypePointer StorageBuffer %input_buffer
        %__0 = OpVariable %_ptr_StorageBuffer_input_buffer StorageBuffer
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
       %bool = OpTypeBool
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %19 = OpLoad %uint %18
         %24 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %25 = OpLoad %uint %24
         %27 = OpAccessChain %_ptr_StorageBuffer_int %__0 %int_0 %25
         %28 = OpLoad %int %27
         %30 = OpIEqual %bool %28 %int_0
         %33 = OpSelect %int %30 %int_1 %int_2
         %34 = OpAccessChain %_ptr_StorageBuffer_int %_ %int_0 %19
               OpStore %34 %33
               OpReturn
               OpFunctionEnd
```

Notes on the assembly:

- The `OpEntryPoint` line lists `%gl_GlobalInvocationID`, `%_` (output SSBO), and `%__0` (input SSBO). All three are module-scope variables. SPIR-V 1.4 requires this complete listing.
- `%_ptr_StorageBuffer_int` is the pointer type used for both `OpAccessChain` results into the SSBOs. `StorageBuffer` storage class is available in SPIR-V 1.4 without `VK_KHR_storage_buffer_storage_class` because that extension was promoted into Vulkan 1.1.
- The body computes `%30 = OpIEqual %bool %28 %int_0` (input element equals zero), then `%33 = OpSelect %int %30 %int_1 %int_2`. When `%30` is true, `%33` is `1`; otherwise `%33` is `2`.
- The `[test]` block (not shown above; see the Amber script) writes `input = {0, 1}` to `ssbo 0:0`, dispatches `compute 1 1 2`, and asserts `probe ssbo int 0:1 0 == 1 2`. The pass condition reduces to: invocation 0 sees `input[0] = 0` and writes `1`; invocation 1 sees `input[1] = 1` and writes `2`.

#### Additional Info

- The SPIR-V carries `OpSource GLSL 430` and `GL_GOOGLE_*` source extensions as metadata only. The Amber runner does not recompile GLSL; it consumes the SPIR-V assembly directly.
- `%1 = OpExtInstImport "GLSL.std.450"` is present but unused in the body. It is harmless metadata left over from the original GLSL the assembly was generated from.
- The `OpCapability Shader` line is the only capability required for this case. Other families require additional capabilities (`VariablePointersStorageBuffer`, `Int16`, `Int64`) declared in their own Amber scripts.

#### Parameter Variation Summary

The 12 `opselect` cases vary the selected type and pointer requirements:

| Case leaf | Composite kind | Extra requirements |
|-----------|----------------|--------------------|
| `scalar_select` | scalar (`OpSelect %int`) | none |
| `vector_element_select` | vector with vector selector (SPIR-V 1.0) | none |
| `vector_select` | vector with scalar selector (SPIR-V 1.4) | none |
| `array_select` | array | none |
| `array_stride_select` | array with non-standard stride | none |
| `struct_select` | struct | none |
| `nested_array_select` | struct with nested arrays | none |
| `nested_struct_select` | struct with nested structs | none |
| `ssbo_pointers_select` | SSBO pointer to same buffer | `Varptr_ssbo` |
| `ssbo_pointers_2_select` | SSBO pointer to different buffers | `Varptr_full` |
| `wg_pointers_select` | Workgroup pointer to same buffer | `Varptr_full_explicitLayout` |
| `wg_pointers_2_select` | Workgroup pointer to different buffers | `Varptr_full_explicitLayout` |

The other 12 families use the same registration pattern but provide their own Amber assembly, `[test]` commands, and feature gates.

## Runtime Execution and Result Checking

[`addTestsForAmberFiles()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120) is the only runtime entry point for every case in this file:

- The helper is gated by `#ifndef CTS_USES_VULKANSC`, so all 13 families are non-VulkanSC only.
- For each `Case` in a `CaseGroup`, the helper builds the Amber script path as `spirv_assembly/instruction/spirv1p4/<subgroup>/<basename>.amber`, calls [`cts_amber::createAmberTestCase()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L86-L91) to construct the test case, and adds the `VK_KHR_spirv_1_4` requirement plus any per-case requirements from the `Case::requirements` vector.
- The helper sets `SpirVAsmBuildOptions(VK_MAKE_API_VERSION(0, 1, 1, 0), vk::SPIRV_VERSION_1_4)` with `supports_VK_KHR_spirv_1_4 = true` through [`testCase->setSpirVAsmBuildOptions(asm_options)`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L113). This tells the CTS shader builder to compile and validate the embedded assembly as SPIR-V 1.4 against a Vulkan 1.1 baseline.
- The Amber runner then takes over: it parses the `[require]` block, compiles the SPIR-V between `[compute shader spirv]` (or the matching stage block for non-compute cases) and the next `[...]` block, creates the pipeline, allocates the resources declared in `[test]`, dispatches/draws, and probes the output SSBO at the specified byte offsets.
- Pass condition: every `probe` assertion in the `[test]` block must match. A single mismatched probe fails the case.
- The pointer families encode boolean comparison results as `0`/`1` integers in the output SSBO. The `opptrdiff` cases encode element-count differences as integers. The `uniformid` cases probe that all invocations in a workgroup or subgroup consumed the same uniform value. The `entrypoint` cases reduce to "the descriptor was bound and the variable was reachable" because the shader body is a simple copy. The `loop_control` cases verify the loop body executed the expected number of times. The `wrap` cases verify the wrapped-arithmetic result for an input that does not overflow.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `opcopylogical` | SPIR-V `OpCopyLogical` layout conversion (UBO↔SSBO offsets, matrix/array strides, nested-array strides) is computed incorrectly or rejected by the shader compiler. |
| `opptrdiff` | `OpPtrDiff` element-count computation is wrong, or variable pointers in SSBO/Workgroup storage are not honored. |
| `opptrequal` | `OpPtrEqual` returns the wrong boolean, or null-pointer / cross-variable comparisons are mishandled. |
| `opptrnotequal` | `OpPtrNotEqual` returns the wrong boolean (mirror of `OpPtrEqual`); same root causes. |
| `opcopymemory` | `OpCopyMemory` with `Aligned` access operands reads or writes at the wrong offset, or the access operands are rejected. |
| `uniformid` | `OpDecorateId UniformId` does not propagate a uniform value across the workgroup/subgroup, especially under nonuniform control flow. |
| `nonwritable` | `NonWritable` on a Function or Private variable is rejected, or the variable is nonetheless mutated by the compiler. |
| `entrypoint` | The entry-point interface does not list a module-scope variable, the variable is unreachable, or the descriptor binding for the listed variable is wrong. |
| `hlsl_functionality1` | `CounterBuffer` decoration, `OpDecorateString`, or `OpMemberDecorateString` is rejected or ignored. |
| `loop_control` | A SPIR-V 1.4 loop control hint (`MinIterations`, `MaxIterations`, `IterationMultiple`, `PeelCount`, `PartialCount`) is rejected or alters the loop body's effect. |
| `opselect` | `OpSelect` on a composite type (array, struct, nested composite, SSBO/workgroup pointer) selects the wrong operand, or the SPIR-V 1.0 scalar/vector forms regress under SPIR-V 1.4. |
| `uconvert` | `UConvert` inside `OpSpecConstantOp` does not extend, truncate, or zero-extend correctly between 16/32/64-bit widths. |
| `wrap` | `NoSignedWrap` or `NoUnsignedWrap` decoration is rejected, or the decoration incorrectly changes the arithmetic result. |
| (all families) | Common infrastructure: SPIR-V 1.4 build options not applied, `VK_KHR_spirv_1_4` requirement not enforced, Amber runner failure, or descriptor/barrier setup issue. |

### Cause Analysis

#### `OpCopyLogical` layout conversion

**Possible failure symptoms:** the output SSBO contains values at the wrong offsets, or values from the wrong members, after a UBO→SSBO or SSBO→UBO copy. The probe assertions on the output SSBO fail at the member offsets.

**Possible implementation causes:** the shader compiler does not reconcile the source and target `Offset`, `ArrayStride`, or `MatrixStride` decorations when lowering `OpCopyLogical`. The `ubo_to_ssbo.amber` case, for example, declares two structs with the same member types but different offsets and strides; a compiler that ignores the target layout and copies member-by-member at the source offsets would produce the symptom. A compiler that rejects the SPIR-V would surface as a pipeline-creation error before any probe runs. Pinning the failure to a specific compiler path needs source-level investigation.

#### Pointer comparison and difference (`opptrequal`, `opptrnotequal`, `opptrdiff`)

**Possible failure symptoms:** the encoded boolean or element-count integers in the output SSBO do not match the expected pattern. For `opptrequal`/`opptrnotequal`, the expected pattern is `1` where two pointers are equal and `0` otherwise (or the inverse for `opptrnotequal`). For `opptrdiff`, the expected pattern is the element-index difference between the two pointers.

**Possible implementation causes:** the driver computes pointer equality by comparing byte addresses instead of logical SPIR-V pointer identity, or vice versa; or the driver does not honor `OpPtrDiff`'s element-count semantics and returns a byte difference instead. Cross-variable comparisons (`different_ssbos_*`, `different_wgs_*`) and null-pointer comparisons (`null_comparisons_*`) are the most likely to expose a mismatch because they cross the boundaries the simple same-variable cases do not. Variable-pointer storage in Function or Private variables (`variable_pointers_vars_*`) may expose a compiler that does not propagate pointer values through non-SSBO storage. Confirming a specific cause needs source-level investigation.

#### `OpCopyMemory` access operands

**Possible failure symptoms:** the output SSBO contains the source data at the wrong offset, or the source/target `Aligned` operands are rejected at shader-validation time.

**Possible implementation causes:** the driver's `OpCopyMemory` lowering ignores the `Aligned` operand and falls back to a default alignment that does not match the decorated offset, or the validator rejects the `Aligned` access operand form. The `different_alignments` case uses `Aligned 16 Aligned 4` on four consecutive copies; an implementation that applies only one of the two alignments would write to the wrong destination offset. Pinning the failure needs source-level investigation.

#### `UniformId` propagation

**Possible failure symptoms:** the output SSBO shows divergent values across invocations that should have consumed the same uniform load, especially in the `partially_active_uniform_id` and `subgroup_cfg_uniform_id` cases that exercise nonuniform control flow.

**Possible implementation causes:** the driver does not honor `OpDecorateId ... UniformId %workgroup` or `%subgroup` and treats the decorated load as a regular load, so each invocation reads a different value. The subgroup cases assume a subgroup size ≤ 8 (the `LocalSize 8 1 1` dispatch); on a device with a larger subgroup, the assumption may not hold, but that would be a test-design concern rather than a driver bug. Confirming the driver-level cause needs source-level investigation.

#### `NonWritable` on Function/Private variables

**Possible failure symptoms:** the SPIR-V is rejected at shader-module creation, or the decorated variable is mutated by the compiler and the output values reflect the mutation.

**Possible implementation causes:** the validator or compiler enforces the pre-SPIR-V 1.4 rule that `NonWritable` only applies to `Uniform` or `StorageBuffer` variables and rejects the decoration on `Function` or `Private` storage. The `non_main_function_nonwritable` case adds the further twist that the decorated variable lives in a non-entry-point function; a compiler that only checks decorations in the entry point would miss it. Confirming a specific compiler path needs source-level investigation.

#### Entry-point interface listing

**Possible failure symptoms:** the SPIR-V is rejected at shader-module creation with an interface-listing error, or the shader runs but the descriptor for the unlisted variable is not bound and the output contains uninitialized data.

**Possible implementation causes:** the validator enforces the SPIR-V 1.0/1.3 rule (only Input/Output variables must be listed) and rejects the 1.4 module, or the driver's descriptor binding logic does not match the variables listed in `OpEntryPoint`. Per-stage and per-resource-kind failures (`comp_pc_entry_point` vs `frag_ssbo_entry_point` vs `tess_con_ubo_entry_point`, etc.) narrow the failure to a specific stage or storage class. Pinning the cause needs source-level investigation.

#### HLSL functionality decorations

**Possible failure symptoms:** the SPIR-V is rejected at shader-module creation, or the `counter_buffer` case produces wrong counter or storage-buffer values because the `CounterBuffer` association was ignored.

**Possible implementation causes:** the validator does not accept `OpDecorateId ... CounterBuffer ...`, `OpDecorateString`, or `OpMemberDecorateString` even though SPIR-V 1.4 folds them in. For `counter_buffer`, the shader uses `OpAtomicIAdd` to increment and decrement the counter; a driver that ignores the `CounterBuffer` association but still binds the counter SSBO at the listed binding would produce the correct values, so a failure here more likely indicates a validator rejection than a runtime mismatch. Pinning the cause needs source-level investigation.

#### Loop control hints

**Possible failure symptoms:** the SPIR-V is rejected at shader-module creation, or the loop body produces the wrong output array because the hint changed the iteration count.

**Possible implementation causes:** the validator rejects one of the SPIR-V 1.4 loop controls (`MinIterations`, `MaxIterations`, `IterationMultiple`, `PeelCount`, `PartialCount`), or the compiler interprets a hint as a requirement and peels or unrolls the loop in a way that changes the visible side effects. The `iteration_multiple` case uses `OpLoopMerge %12 %13 IterationMultiple 3` on a loop that runs 6 times; if the compiler misinterprets the hint as "run a multiple of 3 times" and stops early, the output array would be incomplete. Pinning the cause needs source-level investigation.

#### `OpSelect` on composites and pointers

**Possible failure symptoms:** the output SSBO contains members from the wrong composite operand, or the SPIR-V is rejected for a composite or pointer `OpSelect` form.

**Possible implementation causes:** the compiler lowers `OpSelect` on an array, struct, or nested composite as an element-wise scalar select and picks the wrong operand for some elements, or the validator rejects the composite form even though SPIR-V 1.4 permits it. The pointer cases (`ssbo_pointers_*`, `wg_pointers_*`) may fail if the compiler does not support `OpSelect` on pointer types or if variable-pointer features are not properly enabled. The workgroup-pointer cases depend on `VK_KHR_workgroup_memory_explicit_layout`; a device that does not support the extension cannot run them. The scalar and vector-element cases are SPIR-V 1.0 regression cases; a failure there means the SPIR-V 1.4 build options regressed existing behavior. Pinning the cause needs source-level investigation.

#### `UConvert` in `OpSpecConstantOp`

**Possible failure symptoms:** the output SSBO contains the wrong constant value after specialization, or the SPIR-V is rejected for using `UConvert` inside `OpSpecConstantOp`.

**Possible implementation causes:** the compiler or specialization-constant evaluator applies `UConvert` with the wrong conversion semantics (sign-extend instead of zero-extend, or truncate instead of extend). The `spec_const_opt_zero_extend_n4096` case converts a 16-bit `-4096` bit pattern (`0xF000`) to a 32-bit unsigned value through `UConvert`; its probe expects `61440` (`0x0000F000`) followed by the untouched zero sentinel, so it distinguishes the sign-extended `0xFFFFF000`. The truncate cases (`spec_const_opt_truncate_*`) may fail if the evaluator retains rather than discards high bits. Pinning the cause needs source-level investigation.

#### Integer wrap decorations

**Possible failure symptoms:** the SPIR-V is rejected at shader-module creation, or the `OpIAdd` result differs from the unwrapped result for the test input.

**Possible implementation causes:** the validator rejects `NoSignedWrap` or `NoUnsignedWrap` even though SPIR-V 1.4 folds them in, or the compiler interprets the decoration as a hint to wrap the result for an input that does not overflow (which would be a misreading of the spec: the decorations promise the operation does not overflow, they do not request wrapping). The `no_signed_wrap.amber` case adds `10` to the input `0` and expects `10`; a correct implementation produces `10` regardless of the decoration. A failure more likely indicates a validator rejection than a runtime mismatch. Pinning the cause needs source-level investigation.

#### Common infrastructure

**Possible failure symptoms:** every case in the file fails at the same step (shader-module creation, pipeline creation, or first probe), regardless of test family.

**Possible implementation causes:** the SPIR-V 1.4 build options were not applied, the `VK_KHR_spirv_1_4` requirement was not enforced and the device does not support SPIR-V 1.4, the Amber runner itself failed, or the descriptor/barrier setup used by every case is broken. A whole-file failure should be investigated at the infrastructure level before looking at per-family causes.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_spirv_1_4`. Devices without the extension cannot run any case in this file. The C++ comment at [`vktSpvAsmSpirvVersion1p4Tests.cpp#L93-L106`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L93-L106) notes that `VK_KHR_spirv_1_4` requires Vulkan 1.1, so several promoted extensions (`VK_KHR_storage_buffer_storage_class`, `VK_KHR_variable_pointers`) do not need explicit test requirements because they are core in Vulkan 1.1. Feature bits may still be optional.
- The pointer families add `VariablePointerFeatures.variablePointersStorageBuffer` (`Varptr_ssbo`) and `VariablePointerFeatures.variablePointers` (`Varptr_full`). Devices without these features skip the corresponding cases.
- The `opselect/wg_*` cases add `VK_KHR_workgroup_memory_explicit_layout` (`Varptr_full_explicitLayout`). Devices without the extension skip those two cases.
- The `entrypoint/geom_*` cases add `Features.geometryShader`; the `entrypoint/tess_*` cases add `Features.tessellationShader`. Devices without those features skip the corresponding cases.
- The `uconvert` cases add `Features.shaderInt16` (extend from 16-bit), `Features.shaderInt16` + `VK_KHR_16bit_storage` + `Storage16BitFeatures.storageBuffer16BitAccess` (truncate to 16-bit), or `Features.shaderInt64` (extend to / truncate from 64-bit). Devices without the relevant feature skip the corresponding cases.
- All cases are non-VulkanSC only. The `addTestsForAmberFiles` helper is wrapped in `#ifndef CTS_USES_VULKANSC`, so VulkanSC builds register no cases from this file.

### Design-based pruning

- The `opselect` family does not include every composite combination. The case list covers scalar, vector (both selector forms), array, struct, nested array, nested struct, and SSBO/workgroup pointer pairs. Cross products like "array of structs with non-standard stride" are not present; the existing cases are sufficient to cover the SPIR-V 1.4 `OpSelect` surface.
- The `entrypoint` family does not include workgroup variables for non-compute stages. Workgroup storage is only legal in compute, so a non-compute workgroup case would be invalid.
- The `loop_control` family uses one loop body (copy `data_SSBO[i]` to `out_SSBO[i]`) for all five hints. The hint is the only variable; the body is fixed.
- The `wrap` family uses `OpIAdd` with a non-overflowing input. The cases verify the decoration is accepted and the result is unchanged; they do not attempt to verify wrap behavior on overflowing inputs because the decorations promise non-overflow, not wrapping.
- The `uconvert` family does not include signed conversions. `UConvert` is unsigned by spec; signed conversions use `SConvert`, which is not part of the SPIR-V 1.4 `OpSpecConstantOp` extension.

## Key Takeaways

- The file is an Amber dispatcher: 13 test families and 102 leaves, each routed to a hand-authored `<subgroup>/<basename>.amber` script. The C++ source builds no shaders.
- All cases require `VK_KHR_spirv_1_4` and select SPIR-V 1.4 assembly build options. Per-case feature gates (variable pointers, 16-bit storage, 64-bit integers, geometry, tessellation, workgroup memory explicit layout) layer on top.
- The 13 families cover the SPIR-V 1.4 surface area: composite `OpSelect`, pointer comparison/difference, `OpCopyLogical`/`OpCopyMemory` access operands, `UniformId`, `NonWritable` on Function/Private variables, expanded entry-point interface listing, HLSL functionality decorations, new loop controls, `UConvert` in `OpSpecConstantOp`, and integer wrap decorations.
- The `opselect/scalar_select` representative walkthrough is the smallest case in the file and exercises the SPIR-V 1.0 scalar `OpSelect` form under SPIR-V 1.4 build options. The composite-select cases in the same family are the actual SPIR-V 1.4 new behavior.
- See `## Failure Meaning` for per-family failure causes. The most common pattern is a validator rejection (the SPIR-V is rejected at shader-module creation) rather than a runtime mismatch, because the SPIR-V 1.4 surface area is mostly about accepting new instructions, decorations, and forms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Instruction-root registration | [`vktSpvAsmInstructionTests.cpp#L21538`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21538) | Attaches `spirv1p4` below the instruction root. |
| `createSpirvVersion1p4Group()` | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409) | Top-level group creation; defines all 13 subgroups and their case lists. |
| `addTestsForAmberFiles()` | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120) | Amber test factory: adds `VK_KHR_spirv_1_4`, sets SPIR-V 1.4 build options, registers each case. Wrapped in `#ifndef CTS_USES_VULKANSC`. |
| `Case` and `CaseGroup` structs | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L44-L73`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L44-L73) | Carrier for the per-subgroup basename list and per-case requirements. |
| Feature requirement vectors | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L133-L156`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L133-L156) | `Geom`, `Tess`, `Varptr_ssbo`, `Varptr_full`, `Varptr_full_explicitLayout`, `Int16`, `Int16_storage`, `Int64` definitions. |
| `opcopylogical` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L183`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L183) | 11 `OpCopyLogical` cases. |
| `opptrdiff` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196) | 5 `OpPtrDiff` cases. |
| `opptrequal` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223) | 12 `OpPtrEqual` cases. |
| `opptrnotequal` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250) | 12 `OpPtrNotEqual` cases. |
| `opcopymemory` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L252-L259`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L252-L259) | 3 `OpCopyMemory` access-operand cases. |
| `uniformid` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L261-L272`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L261-L272) | 5 `UniformId` cases. |
| `nonwritable` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L274-L285`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L274-L285) | 5 `NonWritable` on Function/Private cases. |
| `entrypoint` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L327`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L327) | 19 entry-point interface cases across 6 stages; Workgroup is compute-only. |
| `hlsl_functionality1` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L329-L337`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L329-L337) | 3 `CounterBuffer` / `OpDecorateString` / `OpMemberDecorateString` cases. |
| `loop_control` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351) | 5 SPIR-V 1.4 loop control hint cases. |
| `opselect` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379) | 12 `OpSelect` cases (scalar, vector, composite, pointer). |
| `uconvert` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L381-L399`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L381-L399) | 8 `UConvert` in `OpSpecConstantOp` cases. |
| `wrap` case list | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L401-L407`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L401-L407) | 2 `NoSignedWrap` / `NoUnsignedWrap` cases. |
| Representative Amber script | [`opselect/scalar_select.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/opselect/scalar_select.amber) | Smallest representative walkthrough; embeds SPIR-V assembly for `OpSelect` on scalars. |
| OpCopyLogical UBO→SSBO Amber | [`opcopylogical/ubo_to_ssbo.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/opcopylogical/ubo_to_ssbo.amber) | Demonstrates layout conversion through `OpCopyLogical`. |
| NoSignedWrap Amber | [`wrap/no_signed_wrap.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/wrap/no_signed_wrap.amber) | Demonstrates integer wrap decoration. |
