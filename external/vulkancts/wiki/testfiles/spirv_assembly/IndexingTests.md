## Overview

**Core question:** Do SPIR-V access-chain operations select the same nested-buffer elements and interface components that the CTS reference expects?

- `vktSpvAsmIndexingTests.cpp` implements the `spirv_assembly.instruction.compute.indexing` and `spirv_assembly.instruction.graphics.indexing` test families.
- Compute coverage includes `input.struct` and `input.non16basealignment`; graphics coverage includes `input.struct` and `output.component`.
- The tests keep the data and expected results explicit while varying access-chain opcode, index width, signedness, storage class, and graphics stage.
- The page explains the generated SPIR-V, the host-side reference checks, feature-gated variants, and the failure symptoms associated with each family.

## Background Knowledge

- **SPIR-V access-chain addressing:** `OpAccessChain` walks a composite object from a base pointer using index operands. `OpInBoundsAccessChain` is the in-bounds form. `OpPtrAccessChain` performs pointer arithmetic from an array element and, in these tests, uses the variable-pointers and storage-buffer storage-class capabilities.
- **Buffer layout decorations:** `ArrayStride`, member `Offset`, `Block`, and `BufferBlock` determine how nested arrays and structures map to buffer addresses. The non-16-base-alignment family uses an 18-float member array inside each runtime-array structure; each structure has a 72-byte stride, testing addressing beyond common 16-byte alignment assumptions.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.indexing.input
├── struct
└── non16basealignment

spirv_assembly.instruction.graphics.indexing.input
└── struct

spirv_assembly.instruction.graphics.indexing.output
├── component_frag
├── component_geom
├── component_tessc
├── component_tesse
└── component_vert
```

The source builders and mustpass paths place `struct` and `non16basealignment` beneath the `input` test family. The graphics `output` test family has the stage-specific leaves `component_frag`, `component_geom`, `component_tessc`, `component_tesse`, and `component_vert`; the implementation creates them from the shared `component` case name.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Access-chain operation | `opaccesschain`, `opinboundsaccesschain`, `opptraccesschain` | Selects the SPIR-V pointer-building instruction. | [`chainOpTestNames`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L60-L61) |
| Index width | `16`, `32`, `64` | Selects the integer type used by the nested indices. | [`idxSizes`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L60-L61) |
| Signedness | `_u`, `_s` | Selects the unsigned or signed index type and conversion path. | [`addComputeIndexingStructTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L87-L95) |
| 64-bit indexing | `_64bit_indexing` or absent | Enables the additional buffer-indexing variant outside VulkanSC. | [`addComputeIndexingStructTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L284-L288) |
| Non-16-base-alignment operation | `opaccesschain`, `opptraccesschain` | Covers the two operations selected for the 18-float stride case. | [`addComputeIndexingNon16BaseAlignmentTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L610-L612) |
| Graphics stage | `vert`, `frag`, `tessc`, `tesse`, `geom` | Applies nested input indexing to each graphics stage. | [`addGraphicsIndexingStructTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L517-L518) |

The `component` graphics family registers one test name and expands it through `createTestsForAllStages`; its stage-specific assembly differs in how it indexes the interface output.

## Behavior Parameters

The primary behavioral axis is the test family. Each family changes the object being addressed or the pipeline interface being tested.

### `struct`: nested composite indexing

The shader reads four selector values, converts them to the selected width and signedness, and uses them to address a 2D array of 4x4 matrices nested inside an input structure. The output stores the selected float. Compute and graphics builders use the same conceptual data layout, with graphics cases expanded across stages.

### `non16basealignment`: runtime-array stride indexing

Each invocation addresses one `struct1` instance containing `float f[18]`. It loads `f[0]` through `f[17]`, sums them, and writes one result. The runtime-array and pointer decorations specify a 72-byte stride, so the case tests the address calculation for a base alignment that is not 16 bytes.

### `component`: graphics output-component indexing

The graphics interface supplies an integer component selector and a four-component float output. Stage-specific fragments use `OpAccessChain` to select the output component and store `1.0` there. The expected vectors use the fixed pattern `{2, 0, 1, 3}`.

## Shader Analysis

This category uses CTS-authored SPIR-V assembly string templates rather than GLSL/HLSL reconstruction. The representative walkthrough below uses the compute `non16basealignment` path because it shows the unusual stride and the complete load, sum, and store sequence. The walkthrough contains the extracted assembly in its collapsible source-code block and omits a disassembly block because it would duplicate that assembly. For this audit, the embedded hand-authored assembly passed `spirv-as` → `spirv-val` → `spirv-dis`; this is audit-time semantic validation, not a generation-time gate or a claim of textual disassembly identity.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.indexing.input.non16basealignment.opaccesschain
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `non16basealignment` | Selects the nested runtime-array layout whose `float[18]` member has a 72-byte stride. |
| `opaccesschain` | Forms each element pointer directly from `%dataInput`. |
| `dEQP-VKSC` | Selects the VulkanSC mustpass variant, so no `_64bit_indexing` duplicate is generated. |

#### Purpose

Each invocation selects one runtime-array structure by `gl_GlobalInvocationID.x`, sums its 18 floats, and writes the sum to the corresponding output element. The case checks that `OpAccessChain` follows the declared nested layout rather than assuming a 16-byte base stride.

#### Structural Design

| Phase | Assembly behavior |
|-------|-------------------|
| Layout | `%struct0` contains a runtime array of `%struct1`; `%struct1` contains `%input_array` with 18 floats. `ArrayStride 72` describes each `%struct1`. |
| Selection | `%invid` comes from `gl_GlobalInvocationID.x` and selects one runtime-array instance. |
| Accumulation | `%dataPtr0` through `%dataPtr17` address the 18 floats; `%acc17` is the final scalar sum. |
| Result | `%outPtr` addresses output element `%invid`, then `OpStore` writes `%acc17`. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The host creates 32 input structures, each with 18 floats, and dispatches `numWorkGroups = IVec3(32, 1, 1)`.
- The implementation floor-rounds generated inputs before both buffer upload and CPU expected-value calculation, avoiding CPU/GPU rounding-mode differences.
- The sibling `opptraccesschain` case starts from `%base` and uses `OpPtrAccessChain`; it is the important variation for base-pointer arithmetic.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Access-chain operation | `non16basealignment` specializes either `OpAccessChain` or `OpPtrAccessChain`; it does not register `OpInBoundsAccessChain`. | [`addComputeIndexingNon16BaseAlignmentTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L729-L753) |
| Array stride | The input member remains `float[18]`, with `ArrayStride 72` for each runtime-array structure. | [`addComputeIndexingNon16BaseAlignmentTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L620-L626) |
| Invocation count | Each invocation selects one of 32 structures using its X coordinate. | [`addComputeIndexingNon16BaseAlignmentTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L747-L750) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 103
; Schema: 0
               OpCapability Shader
               OpCapability VariablePointersStorageBuffer
               OpExtension "SPV_KHR_variable_pointers"
               OpExtension "SPV_KHR_storage_buffer_storage_class"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_GlobalInvocationID
               OpExecutionMode %2 LocalSize 1 1 1
               OpSource GLSL 430
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_float_uint_18 ArrayStride 4
               OpDecorate %_arr_float_uint_32 ArrayStride 4
               OpDecorate %_runtimearr__struct_11 ArrayStride 72
               OpDecorate %_ptr_StorageBuffer__struct_11 ArrayStride 72
               OpMemberDecorate %_struct_8 0 Offset 0
               OpDecorate %_struct_8 Block
               OpDecorate %9 DescriptorSet 0
               OpDecorate %9 Binding 1
               OpMemberDecorate %_struct_10 0 Offset 0
               OpMemberDecorate %_struct_11 0 Offset 0
               OpDecorate %_struct_10 Block
               OpDecorate %12 DescriptorSet 0
               OpDecorate %12 Binding 0
       %void = OpTypeVoid
         %14 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
      %float = OpTypeFloat 32
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_4 = OpConstant %uint 4
     %uint_5 = OpConstant %uint 5
     %uint_6 = OpConstant %uint 6
     %uint_7 = OpConstant %uint 7
     %uint_8 = OpConstant %uint 8
     %uint_9 = OpConstant %uint 9
    %uint_10 = OpConstant %uint 10
    %uint_11 = OpConstant %uint 11
    %uint_12 = OpConstant %uint 12
    %uint_13 = OpConstant %uint 13
    %uint_14 = OpConstant %uint 14
    %uint_15 = OpConstant %uint 15
    %uint_16 = OpConstant %uint 16
    %uint_17 = OpConstant %uint 17
    %uint_18 = OpConstant %uint 18
    %uint_32 = OpConstant %uint 32
%_arr_float_uint_18 = OpTypeArray %float %uint_18
%_arr_float_uint_32 = OpTypeArray %float %uint_32
  %_struct_8 = OpTypeStruct %_arr_float_uint_32
%_ptr_StorageBuffer__struct_8 = OpTypePointer StorageBuffer %_struct_8
          %9 = OpVariable %_ptr_StorageBuffer__struct_8 StorageBuffer
 %_struct_11 = OpTypeStruct %_arr_float_uint_18
%_runtimearr__struct_11 = OpTypeRuntimeArray %_struct_11
 %_struct_10 = OpTypeStruct %_runtimearr__struct_11
%_ptr_StorageBuffer__struct_10 = OpTypePointer StorageBuffer %_struct_10
%_ptr_StorageBuffer__struct_11 = OpTypePointer StorageBuffer %_struct_11
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
         %12 = OpVariable %_ptr_StorageBuffer__struct_10 StorageBuffer
          %2 = OpFunction %void None %14
         %45 = OpLabel
         %46 = OpAccessChain %_ptr_StorageBuffer__struct_11 %12 %uint_0 %uint_0
         %47 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %48 = OpLoad %uint %47
         %49 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_0
         %50 = OpLoad %float %49
         %51 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_1
         %52 = OpLoad %float %51
         %53 = OpFAdd %float %52 %50
         %54 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_2
         %55 = OpLoad %float %54
         %56 = OpFAdd %float %55 %53
         %57 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_3
         %58 = OpLoad %float %57
         %59 = OpFAdd %float %58 %56
         %60 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_4
         %61 = OpLoad %float %60
         %62 = OpFAdd %float %61 %59
         %63 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_5
         %64 = OpLoad %float %63
         %65 = OpFAdd %float %64 %62
         %66 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_6
         %67 = OpLoad %float %66
         %68 = OpFAdd %float %67 %65
         %69 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_7
         %70 = OpLoad %float %69
         %71 = OpFAdd %float %70 %68
         %72 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_8
         %73 = OpLoad %float %72
         %74 = OpFAdd %float %73 %71
         %75 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_9
         %76 = OpLoad %float %75
         %77 = OpFAdd %float %76 %74
         %78 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_10
         %79 = OpLoad %float %78
         %80 = OpFAdd %float %79 %77
         %81 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_11
         %82 = OpLoad %float %81
         %83 = OpFAdd %float %82 %80
         %84 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_12
         %85 = OpLoad %float %84
         %86 = OpFAdd %float %85 %83
         %87 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_13
         %88 = OpLoad %float %87
         %89 = OpFAdd %float %88 %86
         %90 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_14
         %91 = OpLoad %float %90
         %92 = OpFAdd %float %91 %89
         %93 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_15
         %94 = OpLoad %float %93
         %95 = OpFAdd %float %94 %92
         %96 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_16
         %97 = OpLoad %float %96
         %98 = OpFAdd %float %97 %95
         %99 = OpAccessChain %_ptr_StorageBuffer_float %12 %uint_0 %48 %uint_0 %uint_17
        %100 = OpLoad %float %99
        %101 = OpFAdd %float %100 %98
        %102 = OpAccessChain %_ptr_StorageBuffer_float %9 %uint_0 %48
               OpStore %102 %101
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `addComputeIndexingStructTests()` generates 128 selector vectors with components bounded by `(31, 31, 3, 3)`. The CPU reference uses those components to select one float from the nested matrix layout.
- Struct cases bind the input buffer at descriptor binding `0`, the selector buffer at binding `1`, and the output buffer at binding `2`. The non-16-base-alignment case binds input at `0` and output at `1`.
- Struct compute cases dispatch 128 workgroups. Graphics struct cases use `createTestsForAllStages`, and the component case uses the graphics interface utility for all stages.
- The output buffer is copied or inspected by the CTS utility after execution. A mismatch between any observed and expected value fails the case.
- `shaderInt16` and `shaderInt64` are requested for the corresponding index widths. `VK_KHR_variable_pointers` and `variablePointersStorageBuffer` are requested for `OpPtrAccessChain` paths.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `struct` | Incorrect nested-composite pointer traversal, index conversion, storage-class handling, or selected value store. |
| `non16basealignment` | Incorrect handling of the declared 72-byte runtime-array stride or `OpPtrAccessChain` base-pointer arithmetic. |
| `component` | Incorrect access-chain addressing of a graphics output interface component in one or more stages. |

### Cause Analysis

#### Nested composite indexing (`struct`)

**Possible failure symptoms:** One or more of the 128 output elements differs from the CPU-selected input float. The failing registered case identifies the access-chain operation, index width, signedness, and possibly graphics stage.

**Possible implementation causes:** Source inspection grounds the failure in the pointer traversal, integer conversion, storage-class/decorations, or output store for the selected variant. The exact implementation cause requires investigation of the failing SPIR-V path and device behavior.

#### Non-16-byte stride addressing (`non16basealignment`)

**Possible failure symptoms:** An output sum differs from the CPU sum for the corresponding structure, indicating that one or more of the 18 floats came from the wrong address or that the result was written to the wrong output element.

**Possible implementation causes:** The source requires a 72-byte `ArrayStride` and uses storage-buffer pointers. A failure can therefore arise from incorrect handling of the runtime-array stride or `OpPtrAccessChain` base-pointer arithmetic. Further source-level investigation is needed to distinguish implementation causes.

#### Graphics output-component addressing (`component`)

**Possible failure symptoms:** A stage-specific output vector does not contain `1.0` in the selector-chosen component, or the mismatch appears only for one graphics stage.

**Possible implementation causes:** The relevant stage may lower the interface pointer or its index incorrectly. The CTS source establishes the stage-specific access-chain forms, but the driver or compiler cause of a mismatch needs investigation for the failing stage.

## Case Pruning

### Requirement-based pruning

- `shaderInt16` is required for 16-bit struct indices, and `shaderInt64` is required for 64-bit struct indices.
- `VK_KHR_variable_pointers` and `variablePointersStorageBuffer` are required for the `OpPtrAccessChain` struct and non-16-base-alignment cases.
- Graphics struct cases request `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`.
- The corresponding SPIR-V extensions are emitted for variable-pointer storage-buffer variants.
- `_64bit_indexing` cases are excluded when `CTS_USES_VULKANSC` is defined.

### Design-based pruning

- The `non16basealignment` family intentionally registers only `opaccesschain` and `opptraccesschain`; `opinboundsaccesschain` is not part of that family.
- The graphics `component` family uses a fixed selector pattern and one test name expanded across stages instead of generating the full struct parameter matrix.
- Ordinary index combinations are represented by parameterized test names, so the final page uses one representative assembly rather than duplicating equivalent shader templates.

## Key Takeaways

- The `struct` family checks nested composite addressing while varying opcode, index width, and signedness.
- The `non16basealignment` family exposes the 72-byte structure stride by summing all 18 elements of each selected structure.
- The graphics `component` family checks that output-interface component pointers use the stage-appropriate index shape.
- Host-side expected values are derived from the same selector or array layout used by the shader, so a mismatch directly indicates an addressing or result-transport problem.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `addComputeIndexingStructTests()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L68-L293) | Generates nested compute-buffer assembly, parameter variants, and expected values. |
| `addGraphicsIndexingStructTests()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L295-L532) | Generates graphics-stage nested indexing cases and feature requirements. |
| `addGraphicsOutputComponentIndexingTests()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L534-L595) | Generates the output-interface component case across stages. |
| `addComputeIndexingNon16BaseAlignmentTests()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L597-L757) | Generates the 18-float, 72-byte-stride assembly and CPU sum reference. |
| `createIndexingComputeGroup()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761-L773) | Registers compute `input.struct` and `input.non16basealignment`. |
| `createIndexingGraphicsGroup()` | [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L776-L788) | Registers graphics `input.struct` and `output.component`. |
| Mustpass inventory | [`spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt#L4906-L4925) | Confirms the VulkanSC compute registration names; graphics entries are listed later in the same file. |
