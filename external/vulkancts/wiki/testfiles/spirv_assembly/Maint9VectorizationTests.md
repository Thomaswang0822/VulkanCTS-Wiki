## Overview

**Core question:** Does the implementation execute the five `OpBit*` integer operations correctly across scalar and `vec4` operands, 8-, 16-, 32-, and 64-bit widths, and the registered signedness combinations?

- Source file: [`vktSpvAsmMaint9VectorizationTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp), which implements the `maint9_vectorization` test family under `spirv_assembly.instruction`.
- The file registers `bit_count`, `bit_reverse`, `bit_field_insert`, `bit_field_s_extract`, and `bit_field_u_extract`. Each family expands into executable leaves from an operand matrix.
- Each case generates a SPIR-V 1.6 compute module, passes separate operand buffers through physical storage-buffer addresses, dispatches 64 invocations, and compares GPU results with a CPU reference.
- The page explains the operation families, generated module, feature-based pruning, runtime data flow, and failure localization.

## Background Knowledge

- Integer vector operations apply their scalar operation independently to corresponding components. This page uses scalar values or four-component vectors for data operands. `offset` and `count` remain scalar for bit-field operations.
- Physical storage-buffer addressing lets the shader load and store through device addresses kept in a storage buffer. This test uses that indirection to keep operand buffers separate and to reduce the chance that a compiler scalarizes the tested vector operation.
- In a bit-field operation, `offset` selects the first bit and `count` selects the field width. Signed extraction sign-extends the selected field; unsigned extraction leaves the upper bits clear.

## Registration Hierarchy

```text
spirv_assembly.instruction.maint9_vectorization
├── bit_count
├── bit_reverse
├── bit_field_insert
├── bit_field_s_extract
└── bit_field_u_extract
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation family | `bit_count`, `bit_reverse`, `bit_field_insert`, `bit_field_s_extract`, `bit_field_u_extract` | Selects the SPIR-V instruction and the number and roles of its operands. | [`BitOp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L57-L64), [`createMaint9VectorizationTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1415) |
| Data shape | scalar, `vec4` | Selects one value or four independently checked components. | [`OperandType`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L105-L142) |
| Bit width | 8, 16, 32, 64 | Selects integer types, storage strides, alignment, and width-dependent capabilities. | [`BitSize`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L96-L103), [`initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L325-L717) |
| Signedness | signed, unsigned | Selects signed or unsigned SPIR-V integer types and, for extraction, the interpretation of the selected field. | [`OperandType::getSpvAsmTypePrefix`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L121-L130) |
| Operand roles | `result`, `base`, `insert`, `offset`, `count` | Identifies the result buffer and the arguments used by each instruction. | [`BitOp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L57-L64), [`TestParams`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L155-L188) |
| Workload | 64 invocations | Gives each invocation one independently generated operation. | [`getWorkGroupSize`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L241-L245) |

The mustpass file contains 3,152 executable leaves: 64 `bit_count`, 16 `bit_reverse`, and 1,024 each for `bit_field_insert`, `bit_field_s_extract`, and `bit_field_u_extract` ([mustpass range](../../../mustpass/main/vk-default/spirv-assembly.txt#L39903-L43054)).

## Behavior Parameters

The primary behavior axis is the direct operation-family child of `maint9_vectorization`.

### `bit_count`: count set bits

`OpBitCount` counts the one bits in each base scalar or vector component. The result can use a different width from the base, so this family checks both width conversion at the instruction boundary and per-component vector behavior.

### `bit_reverse`: reverse bits within each component

`OpBitReverse` reverses the bit order within each base component. The registration requires result and base types to match, then varies width, signedness, and scalar versus `vec4` shape.

### `bit_field_insert`: replace a bit range

`OpBitFieldInsert` preserves the base value outside the selected range and inserts the low `count` bits of `insert` at `offset`. The test uses matching result, base, and insert types, while the scalar `offset` and `count` types vary independently.

### `bit_field_s_extract`: signed bit-field extraction

`OpBitFieldSExtract` selects a field from each base component and sign-extends it to the result type. The generated input constraints keep `offset + count` within the base width, including the zero-count case.

### `bit_field_u_extract`: unsigned bit-field extraction

`OpBitFieldUExtract` selects the same bounded field shape as signed extraction but leaves the extracted value unsigned. The cases are registered and checked independently, so their separate CPU oracles cover the zero-extension and sign-extension rules rather than comparing the two variants' GPU results.

## Shader Analysis

These cases author SPIR-V assembly directly in `M9V_Case::initPrograms()` rather than compiling GLSL or HLSL. The representative path specializes that generator for a `vec4` signed 16-bit base and result with scalar signed 32-bit `offset` and `count`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.maint9_vectorization.bit_field_s_extract.result_v16i-base_v16i-offset_s32i-count_s32i
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `bit_field_s_extract` | Emits `OpBitFieldSExtract`. |
| `result_v16i` | Stores four signed 16-bit result components. |
| `base_v16i` | Loads four signed 16-bit base components. |
| `offset_s32i` | Loads one signed 32-bit scalar bit offset. |
| `count_s32i` | Loads one signed 32-bit scalar field width. |
| 64 invocations | Each invocation reads one element from each physical operand buffer. |

#### Purpose

This case checks signed extraction on a vector of narrow integer components while the field-control operands use a wider scalar type. It exercises vector component handling, narrow storage layout, physical-buffer pointer loads, and sign extension in one generated module.

#### Structural Design

| Generated assembly phase | Representative specialization | Why it matters |
|--------------------------|-------------------------------|----------------|
| Capabilities and extensions | `Shader`, `Int16`, `StorageBuffer16BitAccess`, `PhysicalStorageBufferAddresses`, `SPV_KHR_16bit_storage`, `SPV_KHR_physical_storage_buffer`, and `SPV_KHR_storage_buffer_storage_class` | Declares the instruction's arithmetic and storage requirements. |
| References block | Four physical-storage-buffer pointers with 8-byte members at offsets `0`, `8`, `16`, and `24` | Gives the shader the addresses of the result and three input buffers. |
| Data layout | `OpTypeVector` of four 16-bit integers and runtime arrays with `ArrayStride 8` | Matches the four-component host buffer element size. |
| Main operation | Load the invocation index, follow each address, load `base`, `offset`, and `count`, execute `OpBitFieldSExtract`, and store `result` | Performs one independent field extraction per invocation. |

**Instruction Walkthrough**

- `%idx` loads `gl_LocalInvocationIndex`, which ranges over the 64 invocations in the local workgroup.
- For each operand role, the generated code accesses the corresponding member of `%references`, loads its physical buffer pointer, and indexes element `%idx`.
- The shader loads a `v4` 16-bit `base` value and scalar 32-bit `offset` and `count` values. It executes `OpBitFieldSExtract` with the vector result type, so each component uses the same scalar field range.
- The result is stored in the result buffer at the current invocation index. The host later compares all four components against its signed extraction reference.

#### Shader Code

This representative case does not use GLSL or HLSL. CTS constructs the complete compute module directly as SPIR-V assembly in `M9V_Case::initPrograms()`, specialized by the selected `TestParams` and `OperandType`. The complete validated module is shown in the final `SPIR-V` subsection.

#### Additional Info

- `bit_field_insert` adds the `insert` input and keeps result, base, and insert type-identical.
- `bit_field_u_extract` uses the same pointer and load shape as this walkthrough but emits `OpBitFieldUExtract`, changing the interpretation of the extracted field.
- The 8-bit and 16-bit paths add their matching storage capabilities and extensions. The 64-bit path adds `Int64` and uses 8-byte scalar or 32-byte `vec4` array strides.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------------|----------|
| Operation family | Changes the opcode and the number of loaded operand buffers. | [`getSpvOpName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L66-L81), [`getOperandCount`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L83-L94) |
| Scalar versus `vec4` | Changes the selected `OpTypeInt` or `OpTypeVector` type and the array stride. | [`OperandType::getSpvAsmTypePrefix`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L121-L140) |
| Width | Adds or removes width-specific capabilities, changes integer types, storage strides, and load alignment. | [`initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L327-L345), [`getSpvAlignment`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L137-L141) |
| Signedness | Chooses `%iN` versus `%uN` types and, for extraction, signed versus unsigned semantics. | [`OperandType`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L105-L130) |
| `offset` and `count` widths | Changes only the scalar control operand types for bit-field families; host generation still bounds their values to the base width. | [`genValuesForOp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L927-L949) |

The representative module is CTS-authored SPIR-V assembly generated from the source template, not reconstructed GLSL or HLSL. This page does not publish a specialized assembly fence because the complete operand list controls the generated capabilities, layouts, types, and operation; [`M9V_Case::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L325-L717) is the authoritative source for that conditional text.

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V generated by `M9V_Case::initPrograms()` for this walkthrough
- Stage: `comp`
- Entry point: `main`
- Target SPIRV version: `spirv1.6`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 83
; Schema: 0
               OpCapability Shader
               OpCapability Int16
               OpCapability StorageBuffer16BitAccess
               OpCapability PhysicalStorageBufferAddresses
               OpExtension "SPV_KHR_16bit_storage"
               OpExtension "SPV_KHR_physical_storage_buffer"
               OpExtension "SPV_KHR_storage_buffer_storage_class"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel PhysicalStorageBuffer64 GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_LocalInvocationIndex %4
               OpExecutionMode %2 LocalSize 64 1 1
               OpSource GLSL 460
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_struct_5 Block
               OpMemberDecorate %_struct_5 0 Offset 0
               OpMemberDecorate %_struct_5 1 Offset 8
               OpMemberDecorate %_struct_5 2 Offset 16
               OpMemberDecorate %_struct_5 3 Offset 24
               OpDecorate %_runtimearr_ushort ArrayStride 2
               OpDecorate %_struct_7 Block
               OpMemberDecorate %_struct_7 0 Offset 0
               OpDecorate %_runtimearr_short ArrayStride 2
               OpDecorate %_struct_9 Block
               OpMemberDecorate %_struct_9 0 Offset 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %_struct_11 Block
               OpMemberDecorate %_struct_11 0 Offset 0
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %_struct_13 Block
               OpMemberDecorate %_struct_13 0 Offset 0
               OpDecorate %_runtimearr_v4ushort ArrayStride 8
               OpDecorate %_struct_15 Block
               OpMemberDecorate %_struct_15 0 Offset 0
               OpDecorate %_runtimearr_v4short ArrayStride 8
               OpDecorate %_struct_17 Block
               OpMemberDecorate %_struct_17 0 Offset 0
               OpDecorate %_runtimearr_v4uint ArrayStride 16
               OpDecorate %_struct_19 Block
               OpMemberDecorate %_struct_19 0 Offset 0
               OpDecorate %_runtimearr_v4int ArrayStride 16
               OpDecorate %_struct_21 Block
               OpMemberDecorate %_struct_21 0 Offset 0
               OpDecorate %4 Binding 0
               OpDecorate %4 DescriptorSet 0
       %void = OpTypeVoid
         %23 = OpTypeFunction %void
     %ushort = OpTypeInt 16 0
      %short = OpTypeInt 16 1
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
   %v4ushort = OpTypeVector %ushort 4
     %v4uint = OpTypeVector %uint 4
    %v4short = OpTypeVector %short 4
      %v4int = OpTypeVector %int 4
%_runtimearr_ushort = OpTypeRuntimeArray %ushort
%_runtimearr_uint = OpTypeRuntimeArray %uint
%_runtimearr_short = OpTypeRuntimeArray %short
%_runtimearr_int = OpTypeRuntimeArray %int
%_runtimearr_v4ushort = OpTypeRuntimeArray %v4ushort
%_runtimearr_v4uint = OpTypeRuntimeArray %v4uint
%_runtimearr_v4short = OpTypeRuntimeArray %v4short
%_runtimearr_v4int = OpTypeRuntimeArray %v4int
  %_struct_7 = OpTypeStruct %_runtimearr_ushort
 %_struct_11 = OpTypeStruct %_runtimearr_uint
  %_struct_9 = OpTypeStruct %_runtimearr_short
 %_struct_13 = OpTypeStruct %_runtimearr_int
 %_struct_15 = OpTypeStruct %_runtimearr_v4ushort
 %_struct_19 = OpTypeStruct %_runtimearr_v4uint
 %_struct_17 = OpTypeStruct %_runtimearr_v4short
 %_struct_21 = OpTypeStruct %_runtimearr_v4int
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_7 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_11 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_15 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_19 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_9 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_13 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_17 PhysicalStorageBuffer
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer__struct_21 PhysicalStorageBuffer
%_ptr_PhysicalStorageBuffer__struct_7 = OpTypePointer PhysicalStorageBuffer %_struct_7
%_ptr_PhysicalStorageBuffer__struct_11 = OpTypePointer PhysicalStorageBuffer %_struct_11
%_ptr_PhysicalStorageBuffer__struct_15 = OpTypePointer PhysicalStorageBuffer %_struct_15
%_ptr_PhysicalStorageBuffer__struct_19 = OpTypePointer PhysicalStorageBuffer %_struct_19
%_ptr_PhysicalStorageBuffer__struct_9 = OpTypePointer PhysicalStorageBuffer %_struct_9
%_ptr_PhysicalStorageBuffer__struct_13 = OpTypePointer PhysicalStorageBuffer %_struct_13
%_ptr_PhysicalStorageBuffer__struct_17 = OpTypePointer PhysicalStorageBuffer %_struct_17
%_ptr_PhysicalStorageBuffer__struct_21 = OpTypePointer PhysicalStorageBuffer %_struct_21
%_ptr_PhysicalStorageBuffer_ushort = OpTypePointer PhysicalStorageBuffer %ushort
%_ptr_PhysicalStorageBuffer_uint = OpTypePointer PhysicalStorageBuffer %uint
%_ptr_PhysicalStorageBuffer_short = OpTypePointer PhysicalStorageBuffer %short
%_ptr_PhysicalStorageBuffer_int = OpTypePointer PhysicalStorageBuffer %int
%_ptr_PhysicalStorageBuffer_v4ushort = OpTypePointer PhysicalStorageBuffer %v4ushort
%_ptr_PhysicalStorageBuffer_v4uint = OpTypePointer PhysicalStorageBuffer %v4uint
%_ptr_PhysicalStorageBuffer_v4short = OpTypePointer PhysicalStorageBuffer %v4short
%_ptr_PhysicalStorageBuffer_v4int = OpTypePointer PhysicalStorageBuffer %v4int
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Function_int = OpTypePointer Function %int
%_ptr_Input_int = OpTypePointer Input %int
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
  %_struct_5 = OpTypeStruct %_ptr_PhysicalStorageBuffer__struct_17 %_ptr_PhysicalStorageBuffer__struct_17 %_ptr_PhysicalStorageBuffer__struct_13 %_ptr_PhysicalStorageBuffer__struct_13
%_ptr_StorageBuffer__struct_5 = OpTypePointer StorageBuffer %_struct_5
          %4 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_7 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_7
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_11 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_11
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_9 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_9
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_13 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_13
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_15 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_15
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_19 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_19
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_17 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_17
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_21 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__struct_21
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
          %2 = OpFunction %void None %23
         %65 = OpLabel
         %66 = OpLoad %uint %gl_LocalInvocationIndex
         %67 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_17 %4 %int_0
         %68 = OpLoad %_ptr_PhysicalStorageBuffer__struct_17 %67
         %69 = OpAccessChain %_ptr_PhysicalStorageBuffer_v4short %68 %int_0 %66
         %70 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_17 %4 %int_1
         %71 = OpLoad %_ptr_PhysicalStorageBuffer__struct_17 %70
         %72 = OpAccessChain %_ptr_PhysicalStorageBuffer_v4short %71 %int_0 %66
         %73 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_13 %4 %int_2
         %74 = OpLoad %_ptr_PhysicalStorageBuffer__struct_13 %73
         %75 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %74 %int_0 %66
         %76 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__struct_13 %4 %int_3
         %77 = OpLoad %_ptr_PhysicalStorageBuffer__struct_13 %76
         %78 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %77 %int_0 %66
         %79 = OpLoad %v4short %72 Aligned 8
         %80 = OpLoad %int %75 Aligned 4
         %81 = OpLoad %int %78 Aligned 4
         %82 = OpBitFieldSExtract %v4short %79 %80 %81
               OpStore %69 %82 Aligned 8
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Feature checks.** In normal Vulkan builds, [`M9V_Case::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L282-L323) requires Vulkan 1.3, `bufferDeviceAddress`, and `scalarBlockLayout`. It requires `VK_KHR_maintenance9` when the base width is not 32 bits, plus `shaderInt64`, `shaderInt16`, `shaderInt8`, and matching storage-buffer access features when those widths occur.
- **Input buffers.** The host creates one host-visible, device-addressable storage buffer for every result and input role. It writes 64 generated operand values to the corresponding buffers.
- **Address transport.** A separate host-visible storage buffer stores the `VkDeviceAddress` of every operand buffer. The descriptor set has one storage-buffer binding for this references buffer.
- **Dispatch and synchronization.** The shader runs as a compute pipeline with `LocalSize 64` and one dispatch of `(1, 1, 1)`. A compute-to-host memory barrier follows the dispatch before the host reads the result allocation.
- **Reference comparison.** The host computes the selected operation with `calcOp()`. If any result differs, the test logs the invocation index, operand expression, expected value, and observed value, then fails with `Some results differ from the expected values`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `bit_count` | `OpBitCount` lowering is wrong for a selected width or scalar/vector form, or a differing result width is handled incorrectly. |
| `bit_reverse` | `OpBitReverse` reverses the wrong component width, mishandles signed or unsigned integer representation, or fails to preserve vector components. |
| `bit_field_insert` | `OpBitFieldInsert` applies `offset` or `count` incorrectly, places the inserted bits incorrectly, or mishandles scalar field arguments with a vector base. |
| `bit_field_s_extract` | `OpBitFieldSExtract` selects the wrong field or sign-extends it incorrectly for the selected base width. |
| `bit_field_u_extract` | `OpBitFieldUExtract` selects the wrong field or introduces signed-extension behavior where zero extension is required. |

### Cause Analysis

#### `OpBitCount` result or component errors

**Possible failure symptoms:** One or more scalar or vector result values differ from the number of set bits in the base value. A result-width variant can fail while same-width cases pass.

**Possible implementation causes:** The implementation can lower the count operation with the wrong source width, apply the operation to the whole vector instead of each component, or mishandle the result type when it differs from the base type. Further source-level investigation is needed if the failures do not isolate one width or shape.

#### `OpBitReverse` width or vector errors

**Possible failure symptoms:** A result component contains a bit-reversed value for the wrong width, or only some components of a `vec4` result are wrong.

**Possible implementation causes:** The compiler or device can reverse a fixed 32-bit width instead of the selected 8-, 16-, 32-, or 64-bit component, or can use an incorrect vector component mapping. The source matrix and component-wise CPU reference make those patterns distinguishable.

#### `OpBitFieldInsert` range placement errors

**Possible failure symptoms:** The output differs in or around the selected bit range, while bits outside the range may still match the base value.

**Possible implementation causes:** The implementation can shift by the wrong `offset`, use the unmasked insert value, interpret `count` incorrectly, or apply scalar control values inconsistently across vector components. The host constrains the field to the base width, so an out-of-range input is not the expected cause.

#### Signed extraction errors

**Possible failure symptoms:** `bit_field_s_extract` differs when the selected field's top bit is set, especially for narrow base widths. Failures can appear as incorrect high bits in the result.

**Possible implementation causes:** The implementation can select the wrong field or fail to sign-extend the selected field to the result representation. If only fields with a set sign bit fail, the sign-extension path is the likely area for source-level investigation.

#### Unsigned extraction errors

**Possible failure symptoms:** `bit_field_u_extract` produces high bits that should be zero, or selects a different field from the base. The failure pattern can contrast with the signed-extraction family for the same width and field range.

**Possible implementation causes:** The implementation can reuse signed extraction lowering, extend the selected field with ones, or calculate the field mask or shift incorrectly. The case's bounded `offset` and `count` values rule out invalid field ranges as the normal explanation.

#### Shared physical-buffer and result-checking failures

**Possible failure symptoms:** Many or all operation families fail with values that do not correspond to their operand expressions, or fail during shader module creation or dispatch before a result comparison.

**Possible implementation causes:** The generated shader may mishandle `PhysicalStorageBufferAddresses`, the references-buffer layout, device-address loads, narrow storage-buffer strides, or the compute-to-host visibility barrier. These shared failures require source-level investigation across generated assembly and host setup rather than attributing them to one opcode.

## Case Pruning

### Requirement-based pruning

- In normal Vulkan builds, cases require Vulkan 1.3 because the source emits SPIR-V 1.6 assembly and the test's support check rejects older API versions. In Vulkan SC builds, the same registration remains present but `checkSupport()` unconditionally reports the Vulkan 1.3 functionality as unsupported.
- Cases with non-32-bit base operands require `VK_KHR_maintenance9`; 32-bit base cases do not take that extension requirement through `requiresMaint9()`.
- Every case requires `bufferDeviceAddress` and `scalarBlockLayout` because the test uses physical addresses and scalar buffer layouts.
- Cases using 64-bit, 16-bit, or 8-bit operands require the corresponding arithmetic features. 8-bit and 16-bit cases also require their matching storage-buffer access features.

### Design-based pruning

- `bit_count` permits a different result width, but `bit_reverse` requires result and base types to match.
- `bit_field_insert` requires result, base, and insert types to match. Both extraction families require result and base types to match.
- `offset` and `count` are always scalar by design. Vector control operands would test a different instruction shape and are not registered.
- The generator uses four components for every vector case. It does not create matrices or other vector lengths.

## Key Takeaways

- The page covers five operation families and 3,152 executable leaves, with most leaves coming from the three bit-field families.
- Physical storage-buffer addresses keep result and operand data in separate buffers while the shader still receives one descriptor binding.
- The host constrains bit-field ranges and computes a component-wise reference, so a failure identifies a mismatch in instruction semantics, type width, vector handling, or shared address/data transport.
- `bit_field_s_extract` and `bit_field_u_extract` share the same generated field-selection shape but run as independently registered cases. Their separate CPU references cover sign extension versus zero extension; their GPU outputs are not compared with one another.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `M9V_Case::checkSupport()` | [`vktSpvAsmMaint9VectorizationTests.cpp#L282-L323`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L282-L323) | Defines Vulkan version, extension, feature, and storage requirements. |
| `M9V_Case::initPrograms()` | [`vktSpvAsmMaint9VectorizationTests.cpp#L325-L717`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L325-L717) | Generates the conditional SPIR-V module and selects the `OpBit*` instruction. |
| `genValuesForOp()` | [`vktSpvAsmMaint9VectorizationTests.cpp#L907-L951`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L907-L951) | Generates operands and valid bit-field ranges. |
| `singleBit*` reference helpers | [`vktSpvAsmMaint9VectorizationTests.cpp#L953-L999`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L953-L999) | Implements bit count, reversal, insertion, and extraction rules for the host oracle. |
| `calcOp*` reference dispatch | [`vktSpvAsmMaint9VectorizationTests.cpp#L1001-L1126`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1001-L1126) | Applies the selected reference operation to scalar or vector components. |
| `M9V_Instance::iterate()` | [`vktSpvAsmMaint9VectorizationTests.cpp#L1137-L1285`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1137-L1285) | Allocates resources, dispatches the compute shader, and compares results. |
| `createMaint9VectorizationTests()` | [`vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1415`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1415) | Registers the five operation families and their parameter loops. |
| Mustpass cases | [`spirv-assembly.txt#L39903-L43054`](../../../mustpass/main/vk-default/spirv-assembly.txt#L39903-L43054) | Provides the executable leaf range for `maint9_vectorization`. |
