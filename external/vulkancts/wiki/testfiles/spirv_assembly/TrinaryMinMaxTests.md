## Overview

**Core question:** Does `VK_AMD_shader_trinary_minmax` return the correct minimum, maximum, or median for three operands across the registered signed, unsigned, floating-point, scalar, and vector forms?

- This page covers the `amd_trinary_minmax` test family implemented by [`vktSpvAsmTrinaryMinMaxTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L1043).
- The family specializes one CTS-authored compute SPIR-V template for the selected operation and operand representation, then compares 100 shader results with CPU reference results.
- `min3`, `max3`, and `mid3` are the behavioral choices. Base type, width, and aggregation select the instruction form, storage layout, capabilities, and support gates.

## Background Knowledge

- `SPV_AMD_shader_trinary_minmax` provides three-operand integer and floating-point extended instructions. `SMin3AMD`, `UMin3AMD`, and `FMin3AMD` choose the lowest of three operands; the corresponding `Max3` instructions choose the highest; `Mid3` chooses the median. The test imports this instruction set as `%trinary` and selects an instruction name while specializing its assembly ([template and selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L728-L835)).
- Each invocation reads a record containing `op1`, `op2`, and `op3` from a storage buffer and writes one same-typed result to another. The host uses the selected type's component size and logical component count to generate and compare those records; `vec3` receives four-component storage sizing for its footprint ([layout helpers](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L106-L123), [reference calculation](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L480-L533)).

## Registration Hierarchy

```text
spirv_assembly.instruction.amd_trinary_minmax
├── min3
├── max3
└── mid3
```

Each operation family contains the type intermediate nodes `i8`, `u8`, `f16`, `i16`, `u16`, `f32`, `u32`, `f64`, `i64`, and `u64`; each node contains `scalar`, `vec2`, `vec3`, and `vec4` test case leaves. The source omits `f8` because it skips 8-bit floating-point registration ([`createTrinaryMinMaxGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L1043)). The main Vulkan mustpass list covers the generated paths ([entries](../../../mustpass/main/vk-default/spirv-assembly.txt)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation test family | `min3`, `max3`, `mid3` | Selects the AMD extended instruction and matching CPU reference operation. | [operation registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L988), [instruction substitution](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L728-L734) |
| Base type | `i`, `u`, `f` | Selects signed integer, unsigned integer, or floating-point instruction prefix and source-value generator. | [base types](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L990-L994), [function map](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L406-L442) |
| Type width | `8`, `16`, `32`, `64` | Selects component size, type declaration, capabilities, extensions, and support gates. `f8` is excluded. | [width registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L996-L1001), [specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L636-L724) |
| Aggregation | `scalar`, `vec2`, `vec3`, `vec4` | Selects the operand/result type and the number of independently checked components. | [aggregation registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1003-L1008), [case construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1025-L1035) |
| Operation count | `100` | Fixes the number of generated operand triplets, compute invocations, reference results, and output records. | [`kArraySize`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L551-L557), [dispatch](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L851-L858) |
| Random seed | incrementing `seed` from `0xFEE768FCu` | Gives each registered case a deterministic but distinct input sequence. | [registration loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L1035) |

## Behavior Parameters

The primary behavioral axis is the **operation test family**. Every family traverses the same representation matrix and dispatch path, but it changes the property the shader and CPU reference evaluate.

### `min3` - minimum of three operands

`min3` specializes the shader with `SMin3AMD`, `UMin3AMD`, or `FMin3AMD` according to the base type. The host uses `std::min` over the same three components when constructing the reference output ([CPU helper](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L126-L130), [instruction naming](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L728-L734)).

### `max3` - maximum of three operands

`max3` selects the corresponding `SMax3AMD`, `UMax3AMD`, or `FMax3AMD` instruction and the CPU `std::max` reference helper. It uses the same input records, storage buffers, and per-component comparison as `min3` ([CPU helper](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L132-L136), [operation registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L988)).

### `mid3` - median of three operands

`mid3` selects `SMid3AMD`, `UMid3AMD`, or `FMid3AMD`. The reference helper sorts a three-element array and returns element `1`, so this family tests the middle ordered value rather than a numerical average ([CPU helper](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L138-L144)).

## Shader Analysis

The `min3.f32.scalar` test case is a representative baseline path: it uses no narrow-width capability or storage extension, shows the common two-buffer layout, and invokes `FMin3AMD`. The code below is CTS-authored SPIR-V assembly from the shared template after the `min3.f32.scalar` substitutions. It was assembled, validated, and disassembled with `spirv-as`, `spirv-val`, and `spirv-dis` against SPIR-V 1.5; the disassembly is a generation-time validation gate and is not duplicated in this `spirv_assembly` page.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.amd_trinary_minmax.min3.f32.scalar
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `min3` | Selects the floating-point minimum instruction `FMin3AMD`. |
| `f32` | Uses `%float32_t = OpTypeFloat 32` with a 4-byte operand/result stride. |
| `scalar` | Loads and stores one component per operation record. |
| `100` operations | Dispatches `100 x 1 x 1` invocations, one per input triplet. |

#### Purpose

Each invocation loads one three-value record, applies the AMD floating-point minimum instruction, and stores the result at the matching index. The host has already calculated the expected minimum for every record, so each result can be compared directly.

#### Structural Design

| Phase | Instructions and data flow | Role |
|-------|----------------------------|------|
| Index | `OpAccessChain` and `OpLoad` read `gl_GlobalInvocationID.x` into `%idx`. | Assigns one input/output record to each invocation. |
| Input | Three `OpAccessChain` and `OpLoad` pairs read `%op1`, `%op2`, and `%op3` from `%input_buffer`. | Retrieves the operand triplet. |
| Operation | `OpExtInst ... FMin3AMD %op1 %op2 %op3` produces `%result`. | Exercises the extension instruction under test. |
| Output | `OpAccessChain` selects the output record, then `OpStore` writes `%result`. | Makes the result available for host comparison. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- `%input_buffer` uses descriptor set `0`, binding `0`; it holds 100 `Operands` records, each with three 4-byte fields. `%output_buffer` uses binding `1` and holds 100 results.
- `OpExecutionMode %main LocalSize 1 1 1` makes each workgroup contain one invocation. Dispatching 100 workgroups gives one shader execution per record.
- The template imports both `GLSL.std.450` and `SPV_AMD_shader_trinary_minmax`, but this path invokes the AMD set through `%trinary`. The `%std450` import is part of the common template and is not used by this operation.
- The source template fixes SPIR-V version `1.5` through `vk::SpirVAsmBuildOptions` ([assembly build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L759-L835)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-------------------------------------------|----------|
| Operation | Replaces `FMin3AMD` with the selected signed, unsigned, or floating-point `Min3AMD`, `Max3AMD`, or `Mid3AMD` instruction. | [operation-name construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L728-L734) |
| Base type and width | Changes `%float32_t`, and may add `Int8`, `Int16`, `Int64`, `Float16`, or `Float64` capabilities plus 8-bit or 16-bit storage extensions. | [capability and type substitutions](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L636-L724) |
| Aggregation | Replaces the scalar operand type with a vector type and changes record/result strides. The indexing and one-invocation-per-record structure remain fixed. | [operand type substitution](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L695-L724) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 42
; Schema: 0
               OpCapability Shader
               OpExtension "SPV_KHR_storage_buffer_storage_class"
               OpExtension "SPV_AMD_shader_trinary_minmax"
          %1 = OpExtInstImport "GLSL.std.450"
          %2 = OpExtInstImport "SPV_AMD_shader_trinary_minmax"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %3 "main" %gl_GlobalInvocationID %5 %6
               OpExecutionMode %3 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_float_uint_100 ArrayStride 4
               OpMemberDecorate %_struct_8 0 Offset 0
               OpDecorate %_struct_8 Block
               OpDecorate %5 DescriptorSet 0
               OpDecorate %5 Binding 1
               OpMemberDecorate %_struct_9 0 Offset 0
               OpMemberDecorate %_struct_9 1 Offset 4
               OpMemberDecorate %_struct_9 2 Offset 8
               OpDecorate %_arr__struct_9_uint_100 ArrayStride 12
               OpMemberDecorate %_struct_11 0 Offset 0
               OpDecorate %_struct_11 Block
               OpDecorate %6 DescriptorSet 0
               OpDecorate %6 Binding 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
         %14 = OpTypeFunction %void
        %int = OpTypeInt 32 1
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
      %float = OpTypeFloat 32
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
   %uint_100 = OpConstant %uint 100
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%_arr_float_uint_100 = OpTypeArray %float %uint_100
  %_struct_9 = OpTypeStruct %float %float %float
%_arr__struct_9_uint_100 = OpTypeArray %_struct_9 %uint_100
  %_struct_8 = OpTypeStruct %_arr_float_uint_100
 %_struct_11 = OpTypeStruct %_arr__struct_9_uint_100
%_ptr_StorageBuffer__struct_8 = OpTypePointer StorageBuffer %_struct_8
%_ptr_StorageBuffer__struct_11 = OpTypePointer StorageBuffer %_struct_11
          %5 = OpVariable %_ptr_StorageBuffer__struct_8 StorageBuffer
          %6 = OpVariable %_ptr_StorageBuffer__struct_11 StorageBuffer
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
          %3 = OpFunction %void None %14
         %31 = OpLabel
         %32 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %33 = OpLoad %uint %32
         %34 = OpAccessChain %_ptr_StorageBuffer_float %6 %int_0 %33 %int_0
         %35 = OpLoad %float %34
         %36 = OpAccessChain %_ptr_StorageBuffer_float %6 %int_0 %33 %int_1
         %37 = OpLoad %float %36
         %38 = OpAccessChain %_ptr_StorageBuffer_float %6 %int_0 %33 %int_2
         %39 = OpLoad %float %38
         %40 = OpExtInst %float %2 FMin3AMD %35 %37 %39
         %41 = OpAccessChain %_ptr_StorageBuffer_float %5 %int_0 %33
               OpStore %41 %40
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host allocates host-visible input and output storage buffers. The input holds three selected-type operands for each of 100 operations; the output holds one selected-type result per operation ([buffer sizing and allocation](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L851-L876)).
- `OperationManager` generates the input with the per-case seed and calculates the CPU reference before GPU execution. Integer generators fill exact-width values; floating-point generators produce infinities occasionally and otherwise select normal, non-denormal values ([input/reference preparation](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L161-L224), [generation and calculation](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L461-L508)).
- The test binds input and output at descriptor-set bindings `0` and `1`, makes host writes visible to the compute shader, dispatches `100 x 1 x 1`, then makes shader writes visible to the host ([descriptor setup and synchronization](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L887-L962)).
- After invalidating the output allocation, the host compares every result component byte-for-byte with the CPU reference. On the first mismatch, the failure message identifies its operation index and component index ([verification](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L964-L974)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `min3` | Incorrect signed, unsigned, or floating-point minimum instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |
| `max3` | Incorrect signed, unsigned, or floating-point maximum instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |
| `mid3` | Incorrect signed, unsigned, or floating-point median instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |

### Cause Analysis

#### Trinary instruction evaluation

**Possible failure symptoms:** one or more output components differ from the host-computed minimum, maximum, or median for the corresponding input triplet. A failure limited to one operation family is consistent with the selected operation, but it does not by itself exclude a type, vector-layout, or other specialization shared only by that family's failing cases.

**Possible implementation causes:** the shader uses a different AMD extended instruction name for each operation and base type, while the host selects a matching C++ helper. Investigate instruction decoding, lowering, or execution for the affected signed, unsigned, or floating-point trinary operation. The CTS source does not identify a more specific implementation location.

#### Type, vector, or storage-layout specialization

**Possible failure symptoms:** a subset of widths or aggregations fails while the same operation passes for the baseline scalar form. The reported component index can locate the first incorrect vector lane.

**Possible implementation causes:** specialization changes the operand type, component size, array stride, and potentially capabilities or storage extensions. `vec3` also uses an effective four-component storage footprint. Investigate the affected scalar/vector type's storage-buffer layout, component access, and capability or extension path; the source does not isolate a specific implementation layer.

#### CPU/GPU result mismatch at supported boundary types

**Possible failure symptoms:** a mismatch occurs for a generated floating-point case containing infinity, or only in values close to a representation boundary. The test reports raw component-byte inequality rather than applying an epsilon.

**Possible implementation causes:** the reference uses the selected `tcu::Float16`, `tcu::Float32`, or `tcu::Float64` operation helper, while the device executes the matching AMD instruction. Investigate the operation's supported floating-point handling and the selected representation path. This generator avoids denormals and does not generate NaNs, so those cases are outside this test's input coverage.

## Case Pruning

### Requirement-based pruning

The registration loop creates all integer 8-, 16-, 32-, and 64-bit forms plus floating-point 16-, 32-, and 64-bit forms for each operation and aggregation. `checkSupport()` skips unsupported leaves through their required extension and feature checks: every case requires `VK_KHR_get_physical_device_properties2`, `VK_KHR_storage_buffer_storage_class`, and `VK_AMD_shader_trinary_minmax`; narrow-width cases add their relevant storage and shader type requirements ([`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L630)).

### Design-based pruning

The source deliberately excludes floating-point 8-bit forms. It also keeps array size, local size, descriptor layout, dispatch shape, and comparison method fixed across the matrix, so the matrix isolates operation semantics and operand representation rather than scheduling or resource-topology changes.

## Key Takeaways

- The behavioral axis is `min3`, `max3`, or `mid3`; each one validates a different three-operand ordering result with the same host/device flow.
- The generated type matrix changes instruction prefix, SPIR-V declarations, buffer layout, and support requirements, while scalar and vector results use the same per-component reference comparison.
- A failure reports the first operation and component whose raw result bytes differ from the CPU reference. For interpretation, see [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| CPU operation, input, and comparison helpers | [`OperationManager`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L126-L533) | Defines the three CPU operations, deterministic random data, reference output, and byte comparison. |
| Support checks | [`TrinaryMinMaxCase::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L630) | Defines baseline and type-specific extension and feature gates. |
| SPIR-V substitutions | [`TrinaryMinMaxCase::getSpirVReplacements()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L632-L734) | Selects capabilities, types, strides, and AMD instruction name. |
| Assembly template | [`TrinaryMinMaxCase::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L737-L835) | Defines the compute entry point, buffers, loads, extended instruction, and store. |
| Runtime execution | [`TrinaryMinMaxInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L843-L974) | Builds resources, dispatches compute work, and reports mismatches. |
| Test registration | [`createTrinaryMinMaxGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L1043) | Registers the operation/type/aggregation hierarchy. |
| Parent registration | [`createInstructionTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21535-L21545) | Attaches `amd_trinary_minmax` under `spirv_assembly.instruction`. |
| Mustpass coverage | [AMD trinary min/max entries](../../../mustpass/main/vk-default/spirv-assembly.txt) | Lists the generated test case paths in the main Vulkan mustpass set. |
