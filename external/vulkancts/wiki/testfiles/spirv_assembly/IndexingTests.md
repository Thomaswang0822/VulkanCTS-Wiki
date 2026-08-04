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
dEQP-VKSC.spirv_assembly.instruction.compute.indexing.input.non16basealignment.opaccesschain
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

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly</summary>

```llvm
OpCapability Shader
OpCapability VariablePointersStorageBuffer
OpExtension "SPV_KHR_variable_pointers"
OpExtension "SPV_KHR_storage_buffer_storage_class"
%1 = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
OpExecutionMode %main LocalSize 1 1 1
OpSource GLSL 430
OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
OpDecorate %input_array ArrayStride 4
OpDecorate %output_array ArrayStride 4
OpDecorate %runtimearr_struct1 ArrayStride 72
OpDecorate %_ptr_struct1_sb ArrayStride 72
OpMemberDecorate %Output 0 Offset 0
OpDecorate %Output Block
OpDecorate %dataOutput DescriptorSet 0
OpDecorate %dataOutput Binding 1
OpMemberDecorate %struct0 0 Offset 0
OpMemberDecorate %struct1 0 Offset 0
OpDecorate %struct0 Block
OpDecorate %dataInput DescriptorSet 0
OpDecorate %dataInput Binding 0
%void = OpTypeVoid
%3 = OpTypeFunction %void
%u32 = OpTypeInt 32 0
%i32 = OpTypeInt 32 1
%_ptr_Function_uint32 = OpTypePointer Function %u32
%v3uint32 = OpTypeVector %u32 3
%_ptr_Input_v3uint32 = OpTypePointer Input %v3uint32
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint32 Input
%_ptr_Input_uint32 = OpTypePointer Input %u32
%float = OpTypeFloat 32
%uint_0 = OpConstant %u32 0
%uint_1 = OpConstant %u32 1
%uint_2 = OpConstant %u32 2
%uint_3 = OpConstant %u32 3
%uint_4 = OpConstant %u32 4
%uint_5 = OpConstant %u32 5
%uint_6 = OpConstant %u32 6
%uint_7 = OpConstant %u32 7
%uint_8 = OpConstant %u32 8
%uint_9 = OpConstant %u32 9
%uint_10 = OpConstant %u32 10
%uint_11 = OpConstant %u32 11
%uint_12 = OpConstant %u32 12
%uint_13 = OpConstant %u32 13
%uint_14 = OpConstant %u32 14
%uint_15 = OpConstant %u32 15
%uint_16 = OpConstant %u32 16
%uint_17 = OpConstant %u32 17
%uint_18 = OpConstant %u32 18
%uint_32 = OpConstant %u32 32
%input_array = OpTypeArray %float %uint_18
%output_array = OpTypeArray %float %uint_32
%Output = OpTypeStruct %output_array
%_ptr_sb_Output = OpTypePointer StorageBuffer %Output
%dataOutput = OpVariable %_ptr_sb_Output StorageBuffer
%struct1 = OpTypeStruct %input_array
%runtimearr_struct1 = OpTypeRuntimeArray %struct1
%struct0 = OpTypeStruct %runtimearr_struct1
%_ptr_struct0_sb = OpTypePointer StorageBuffer %struct0
%_ptr_struct1_sb = OpTypePointer StorageBuffer %struct1
%_ptr_float_sb = OpTypePointer StorageBuffer %float
%dataInput = OpVariable %_ptr_struct0_sb StorageBuffer
%main = OpFunction %void None %3
%entry = OpLabel
%base = OpAccessChain %_ptr_struct1_sb %dataInput %uint_0 %uint_0
%invid_ptr = OpAccessChain %_ptr_Input_uint32 %gl_GlobalInvocationID %uint_0
%invid = OpLoad %u32 %invid_ptr
%dataPtr0 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_0
%acc0 = OpLoad %float %dataPtr0
%dataPtr1 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_1
%tmp1 = OpLoad %float %dataPtr1
%acc1 = OpFAdd %float %tmp1 %acc0
%dataPtr2 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_2
%tmp2 = OpLoad %float %dataPtr2
%acc2 = OpFAdd %float %tmp2 %acc1
%dataPtr3 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_3
%tmp3 = OpLoad %float %dataPtr3
%acc3 = OpFAdd %float %tmp3 %acc2
%dataPtr4 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_4
%tmp4 = OpLoad %float %dataPtr4
%acc4 = OpFAdd %float %tmp4 %acc3
%dataPtr5 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_5
%tmp5 = OpLoad %float %dataPtr5
%acc5 = OpFAdd %float %tmp5 %acc4
%dataPtr6 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_6
%tmp6 = OpLoad %float %dataPtr6
%acc6 = OpFAdd %float %tmp6 %acc5
%dataPtr7 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_7
%tmp7 = OpLoad %float %dataPtr7
%acc7 = OpFAdd %float %tmp7 %acc6
%dataPtr8 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_8
%tmp8 = OpLoad %float %dataPtr8
%acc8 = OpFAdd %float %tmp8 %acc7
%dataPtr9 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_9
%tmp9 = OpLoad %float %dataPtr9
%acc9 = OpFAdd %float %tmp9 %acc8
%dataPtr10 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_10
%tmp10 = OpLoad %float %dataPtr10
%acc10 = OpFAdd %float %tmp10 %acc9
%dataPtr11 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_11
%tmp11 = OpLoad %float %dataPtr11
%acc11 = OpFAdd %float %tmp11 %acc10
%dataPtr12 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_12
%tmp12 = OpLoad %float %dataPtr12
%acc12 = OpFAdd %float %tmp12 %acc11
%dataPtr13 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_13
%tmp13 = OpLoad %float %dataPtr13
%acc13 = OpFAdd %float %tmp13 %acc12
%dataPtr14 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_14
%tmp14 = OpLoad %float %dataPtr14
%acc14 = OpFAdd %float %tmp14 %acc13
%dataPtr15 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_15
%tmp15 = OpLoad %float %dataPtr15
%acc15 = OpFAdd %float %tmp15 %acc14
%dataPtr16 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_16
%tmp16 = OpLoad %float %dataPtr16
%acc16 = OpFAdd %float %tmp16 %acc15
%dataPtr17 = OpAccessChain %_ptr_float_sb %dataInput %uint_0 %invid %uint_0 %uint_17
%tmp17 = OpLoad %float %dataPtr17
%acc17 = OpFAdd %float %tmp17 %acc16
%outPtr = OpAccessChain %_ptr_float_sb %dataOutput %uint_0 %invid
OpStore %outPtr %acc17
OpReturn
OpFunctionEnd
```

</details>

The checked-in C++ template emits the variable-pointer capability and both SPIR-V extensions for the non-16-base-alignment variants; the representative `opaccesschain` assembly therefore retains those declarations even though its selected operation is `OpAccessChain`.

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
