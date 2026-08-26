## Overview

**Core question:** Can a Vulkan implementation execute SPIR-V modules that use an empty `OpTypeStruct` in copies, pointer comparison, and function calls without corrupting the observable nonempty data around it?

- This page documents the `empty_struct` test family in the `spirv_assembly` test category. [`createEmptyStructComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L532-L544) registers three intermediate nodes: `copying`, `pointer_comparison`, and `function`.
- The source defines empty structures with `OpTypeStruct` without member types, then embeds them between two `i32` members of a buffer block. The test cases make surrounding integer data, pointer inequality, or function results observable through storage-buffer output.
- The default Vulkan mustpass list contains eight executable leaves: four under `copying`, one under `pointer_comparison`, and three under `function`. The Vulkan SC list has the same eight registered paths. See [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L1484-L1491) and [`spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt#L1043-L1050).

## Background Knowledge

- `OpTypeStruct` takes zero or more member-type IDs. An empty operand list therefore declares a structure with no members. The [SPIR-V grammar entry for `OpTypeStruct`](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json) records this variable-length operand form.
- `OpAccessChain` derives a pointer to a selected composite member. `OpPtrNotEqual` compares two pointer values, and `OpSelect` converts its Boolean result to the integer signal checked by the host. See the [SPIR-V grammar](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json).
- `OpCopyMemory` copies memory through pointers, while `OpCopyLogical` and `OpCopyObject` produce values. A function call can pass and return an empty-struct value even though the value contains no data members. The test observes neighboring payload fields or an independent integer result instead of attempting to inspect an empty value directly.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.empty_struct
├── copying
├── pointer_comparison
└── function
```

[`createInstructionTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21422-L21428) adds `empty_struct` to the compute instruction branch. [`createEmptyStructComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L532-L544) supplies the three direct intermediate nodes shown above.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `copying`, `pointer_comparison`, `function` | Selects the operation shape used to exercise the empty struct. | [group registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L537-L542) |
| Copy instruction | `copy_object`, `copy_memory` | `copy_object` loads the container and stores the resulting value. `copy_memory` uses `OpCopyMemory` between the input and output pointers. | [copying method table](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L167-L184) |
| Copy input layout | `ubo`, `ssbo` | The UBO uses offsets `0, 16, 32, 48`; the SSBO uses `0, 4, 8, 12`. Both layouts place two empty members between the observable first and last `i32` members. | [buffer type table](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L141-L165) |
| Function empty-struct source variable | `global_variable_private`, `global_variable_shared`, `local_variable` | Selects the `Private`, `Workgroup`, or `Function` variable from which the caller loads one empty value before copying it into a function-scope parameter variable. | [variable definitions](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L468-L502), [caller setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L405-L415) |
| SPIR-V and feature requirement | SPIR-V 1.4 plus `VK_KHR_spirv_1_4` and `variablePointersStorageBuffer` | Required by the pointer comparison and function modules. | [pointer case setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L304-L316), [function case setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L517-L526) |

## Behavior Parameters

The behavioral axis is the **intermediate node**. Each direct child changes the SPIR-V operation that carries or addresses an empty-struct value.

### copying: copy a container with empty members

The `copying` node creates four test case leaves from the two copy instructions and two input-buffer layouts. The declared container is `OpTypeStruct %i32 %type_empty_struct %type_empty_struct %i32`. The UBO leaves use a uniform input and storage-buffer output; the SSBO leaves use storage buffers for both. The host checks only nonzero expected words; zero marks empty-member positions and, in the UBO representation, layout gaps that this oracle does not constrain.

### pointer_comparison: compare addresses of empty members

The sole `ssbo` leaf takes `OpAccessChain` pointers to member indices `1` and `2`, the two separate empty members in one container. `OpPtrNotEqual` must produce true, so `OpSelect` writes integer `1` to the output buffer. This module requests `VariablePointersStorageBuffer`, SPIR-V 1.4, and `VK_KHR_spirv_1_4`.

### function: pass and return an empty-struct value

The three leaves vary where the source empty-struct variable resides. Each of two workgroups has two local invocations; the local-ID branch routes each invocation through one of the two call sites. A call copies an empty value from `StorageBuffer` to the function type with `OpCopyLogical`, calls `%15`, copies the returned value back, and writes sentinel integer fields around the result. The repeated workgroups write the same expected values. The expected outputs for each output buffer are `{1, 0xffffffff, 1}`.

## Shader Analysis

The test modules are CTS-authored SPIR-V assembly strings. They are specialized directly in C++ and passed to the SPIR-V assembly source collection; there is no GLSL or HLSL shader to reconstruct. The walkthrough below uses the `copying.copy_memory_ssbo` leaf because it shows the empty type, the container layout, and the memory-copy instruction in the smallest complete module. The pointer-comparison and function leaves use separate assembly templates and are summarized as parameter variations.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.empty_struct.copying.copy_memory_ssbo
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `copying` | Exercises an empty structure embedded in a larger copied container. |
| `copy_memory` | Uses `OpCopyMemory` between the input and output container pointers. |
| `ssbo` | Uses `StorageBuffer` for both resources, with member offsets `0`, `4`, `8`, and `12`. |
| Empty type | `%type_empty_struct = OpTypeStruct`, with no member-type operands. |
| Container type | `%type_container_struct = OpTypeStruct %i32 %type_empty_struct %type_empty_struct %i32`. |
| Host data and check | Input `{2, 3, 5, 7}`; expected `{2, 0, 0, 7}`. The custom verifier compares only the nonzero expected words. |

#### Purpose

This module checks that a container containing two empty structure members can be copied through storage-buffer pointers without changing the observable integer members before and after them. The empty members are represented by zero marker positions in the expected vector; the host-side verifier deliberately ignores those positions.

#### Structural Design

```mermaid
flowchart TD
    A[Input SSBO: container {2, 3, 5, 7}] --> B[StorageBuffer pointer %var_input]
    B --> C[OpCopyMemory %var_outdata %var_input]
    C --> D[Output SSBO: container]
    D --> E[verifyResult checks expected nonzero words]
    E --> F[Word 0 must be 2; word 3 must be 7]
```

The module declares the empty structure and the four-member container, decorates each container member with an explicit offset, binds the input at set `0`, binding `0`, and the output at set `0`, binding `1`, and runs one invocation of `main`. `OpCopyObject` creates the pointer value used by the template even for this `copy_memory` specialization; the tested transfer is the following `OpCopyMemory` instruction.

#### Shader Code

This is direct CTS-authored SPIR-V assembly, not GLSL or HLSL generated from a source shader. The complete source-authored module is retained only in the final `#### SPIR-V` subsection; this section records the direct-SPIR-V fact without duplicating assembly.

#### Additional Info

- The explicit SSBO offsets are `0`, `4`, `8`, and `12`; the two empty members therefore occupy no observable payload words in the host input/output representation.
- The source provides input `{2, 3, 5, 7}` and expected output `{2, 0, 0, 7}`. `verifyResult()` skips expected words equal to zero, so this leaf constrains the first and final integer payloads only.
- The module assembles and validates as SPIR-V 1.0 with `spirv-as --target-env spv1.0` and `spirv-val --target-env spv1.0`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Copy instruction | `copy_object` replaces `OpCopyMemory` with `OpLoad %type_container_struct %input_copy` followed by `OpStore %var_outdata %result`; `copy_memory` retains the pointer-based memory copy. | [copying method table](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L167-L184) |
| Buffer layout | `ubo` changes the input descriptor to `Uniform`, uses offsets `0`, `16`, `32`, `48`, and supplies padded host data; `ssbo` uses compact offsets `0`, `4`, `8`, `12`. | [buffer type table](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L141-L165) |
| Pointer comparison | `pointer_comparison.ssbo` uses a separate module with `OpAccessChain` to empty members `1` and `2`, `OpPtrNotEqual`, and `OpSelect`; it requires SPIR-V 1.4, `VK_KHR_spirv_1_4`, and `variablePointersStorageBuffer`. | [pointer-comparison builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L213-L316) |
| Function variable placement | The three `function` leaves use a separate module and place the source empty value in `Private`, `Workgroup`, or `Function` storage; the call/return path uses `OpCopyLogical` and `%15`. | [function builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L319-L526) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: complete CTS-authored SPIR-V assembly for `copying.copy_memory_ssbo`
- Stage: `comp`
- Entry point: `GLCompute` (`main`)
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 23
; Schema: 0
               OpCapability Shader
               OpExtension "SPV_KHR_storage_buffer_storage_class"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %1 "main" %gl_GlobalInvocationID
               OpExecutionMode %1 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %3 Binding 0
               OpDecorate %3 DescriptorSet 0
               OpDecorate %4 Binding 1
               OpDecorate %4 DescriptorSet 0
               OpMemberDecorate %_struct_5 0 Offset 0
               OpMemberDecorate %_struct_5 1 Offset 4
               OpMemberDecorate %_struct_5 2 Offset 8
               OpMemberDecorate %_struct_5 3 Offset 12
               OpDecorate %_struct_5 Block
       %bool = OpTypeBool
       %void = OpTypeVoid
          %8 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
      %float = OpTypeFloat 32
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
%_runtimearr_int = OpTypeRuntimeArray %int
%_runtimearr_float = OpTypeRuntimeArray %float
 %_struct_18 = OpTypeStruct
  %_struct_5 = OpTypeStruct %int %_struct_18 %_struct_18 %int
%_ptr_Uniform__struct_5 = OpTypePointer Uniform %_struct_5
%_ptr_StorageBuffer__struct_5 = OpTypePointer StorageBuffer %_struct_5
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %3 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
          %4 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
          %1 = OpFunction %void None %8
         %21 = OpLabel
         %22 = OpCopyObject %_ptr_StorageBuffer__struct_5 %3
               OpCopyMemory %4 %3
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The copying builder specializes the assembly once for every buffer-layout and copy-method pair, gives each case one workgroup, and supplies the input and expected output buffers. [`verifyResult()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L61) reads every output word but skips every expected word of zero, including irrelevant UBO layout gaps. The leaf passes only if all nonzero expected words match.
2. The pointer-comparison builder creates one SSBO input `{2, 3, 5, 7}` and one expected output `{1}`. Its assembly selects the two empty-member pointers, compares them, converts the Boolean to an `i32`, and stores that value. The framework's normal output comparison checks the one-word result. See the [case construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L304-L316).
3. The function builder launches two workgroups with two local invocations each and creates two output resources with the same expected vector `{1, 0xffffffff, 1}`. Each local-ID branch invokes `%15` with two function-scope empty-struct pointers and a Boolean, copies the returned empty value into a storage-buffer object, and stores visible integer sentinels. Both workgroups make the same writes, so the output vectors do not distinguish workgroups. See the [template control flow](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L392-L465) and [expected-output setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L504-L526).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copying` | Empty-member handling during value or memory copy, member-offset/layout handling, or the copying oracle's storage-buffer readback path. |
| `pointer_comparison` | Address formation for distinct empty members, `OpPtrNotEqual` execution, requested variable-pointer support, or the one-word output path. |
| `function` | Empty-struct type conversion or call/return handling, the selected variable storage class, requested variable-pointer support, or either output comparison. |

The observed buffers classify failures by operation shape. They do not isolate a compiler defect from descriptor setup, memory layout, or result readback without inspecting the failing module and runtime trace.

### Cause Analysis

#### Container-copy handling

**Possible failure symptoms:** A copying leaf returns a nonzero expected payload word other than `2` or `7`. A UBO-only or SSBO-only pattern narrows the symptom to that layout variant, while a `copy_memory`-only or `copy_object`-only pattern narrows it to that operation form.

**Possible implementation causes:** An implementation may mishandle a container type that has no-data members when it calculates member locations, transfers a composite value, or performs a memory copy. A layout or descriptor path may also select the wrong input representation. The source intentionally accepts any values in expected-zero positions, including UBO layout gaps, so those words alone are not a test failure.

#### Empty-member pointer comparison

**Possible failure symptoms:** `pointer_comparison.ssbo` writes `0` instead of the expected `1`, or the case cannot run after requesting SPIR-V 1.4 and `variablePointersStorageBuffer`.

**Possible implementation causes:** The implementation may collapse the two access-chain results, mishandle pointer inequality for distinct empty members, or fail the required variable-pointer feature path. Source-level investigation is needed to separate those paths from storage-buffer output setup.

#### Function argument and return handling

**Possible failure symptoms:** One or more function leaves differs from `{1, 0xffffffff, 1}` in either output resource. A failure limited to `global_variable_private`, `global_variable_shared`, or `local_variable` follows the selected empty-struct variable storage class.

**Possible implementation causes:** A compiler or execution implementation may mishandle `OpCopyLogical`, function parameters, or `OpReturnValue` for an empty structure. A storage-class-specific failure can also originate in private, workgroup, or function-variable lowering. The integer sentinels make the call path observable, but they do not identify the exact instruction that produced the mismatch.

## Case Pruning

### Requirement-based pruning

- `pointer_comparison` has only an SSBO leaf because the source notes that this pointer comparison is possible only for the `StorageBuffer` storage class. See [the builder comment and capability declaration](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L213-L219).

### Design-based pruning

- The `copying` node tests two layouts rather than every possible buffer arrangement. The source supplies the UBO and SSBO forms needed to exercise their distinct member-offset tables.
- The function node uses three storage placements. It does not multiply those cases by the copying layouts because the function template has its own storage-buffer interface and varies only the empty variable definition.

## Key Takeaways

- `empty_struct` is one compute test family with three direct intermediate nodes and eight mustpass leaves.
- The tests make an otherwise data-free type observable through neighboring integers, pointer inequality, and call-side sentinel stores.
- `copying` accepts ignored zero marker positions by design; `pointer_comparison` requires output `1`; `function` requires `{1, 0xffffffff, 1}` from both outputs.
- `pointer_comparison` and `function` require SPIR-V 1.4, `VK_KHR_spirv_1_4`, and the requested `variablePointersStorageBuffer` feature.

## Source Reference Appendix

- [Obsolete navigation page: `vktSpvAsmEmptyStructTests.md`](vktSpvAsmEmptyStructTests.md)
- [Implementation: `vktSpvAsmEmptyStructTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L544)
- [Parent registration: `vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21422-L21428)
- [Default Vulkan mustpass entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L1484-L1491)
- [Vulkan SC mustpass entries](../../../mustpass/main/vksc-default/spirv-assembly.txt#L1043-L1050)
- [SPIR-V core grammar](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json)
