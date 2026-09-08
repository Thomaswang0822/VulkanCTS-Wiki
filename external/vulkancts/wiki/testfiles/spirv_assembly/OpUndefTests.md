## Overview

**Core question:** Does the implementation execute `OpUndef` values safely when they are passed through buffer-based compute interfaces and used in dead or live code?

- This page covers the `op_undef` cases added to the instruction family by [`vktSpvAsmOpUndefTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp).
- The cases exercise uniform, storage, dynamic-uniform, and dynamic-storage descriptors; scalar and array forms; and dead-code versus live-code use.
- The test intentionally validates successful module creation and execution for undefined values rather than asserting a particular undefined payload.

## Background Knowledge

For the shared SPIR-V module and host-oracle concepts, see [Background Knowledge](../../categories/spirv_assembly.md#background-knowledge) of the `spirv_assembly` page.

- **Undefined values.** `OpUndef` produces an undefined value of a declared SPIR-V type. The operation does not provide a deterministic payload; later behavior must therefore not depend on a particular numeric value.
- **Composite extraction.** `OpCompositeExtract` selects a member from a composite value such as an array or structure. The array variants add this extra type-and-index operation before the helper call.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.opundef
├── buffer_storage
├── buffer_storage_array
├── buffer_storage_arraylivecode
├── buffer_storage_dynamic
├── buffer_storage_dynamic_array
├── buffer_storage_dynamic_arraylivecode
├── buffer_storage_dynamiclivecode
├── buffer_storagelivecode
├── buffer_uniform
├── buffer_uniform_array
├── buffer_uniform_arraylivecode
├── buffer_uniform_dynamic
├── buffer_uniform_dynamic_array
├── buffer_uniform_dynamic_arraylivecode
└── buffer_uniform_dynamiclivecode
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor type | `storage`, `uniform`, `storage_dynamic`, `uniform_dynamic` | Selects the Vulkan buffer descriptor used by the test. | [`appendOpUndefTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L285-L310) |
| Shape | scalar structure, `array` | Passes either one buffer structure or an array of structures to the helper function. | [`OpUndefBufferComputeTestCase::initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L91-L112) |
| Control-flow use | dead code or `livecode` | Places the helper call behind a false or true condition. | [`CONDITION_VAL`](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L81-L90) |

## Behavior Parameters

The primary behavioral axis is whether the undefined value is used in dead code or in live code, with descriptor and composite-shape variants changing the surrounding interface.

### Dead-code and live-code variants

The dead-code variants create the undefined value and retain the call in a branch that is not taken. The live-code variants execute the call and extract a member from the undefined composite. Both paths must compile, submit, and complete without relying on a deterministic undefined value.

### Descriptor and shape variants

The descriptor variants select uniform, storage, and dynamic bindings; array variants add one composite level before extraction.

## Shader Analysis

The test uses hand-authored SPIR-V assembly rather than GLSL or HLSL.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.opundef.buffer_storagelivecode
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `storage` | Uses a storage-buffer descriptor. |
| `livecode` | Executes the helper call that receives the undefined value. |
| non-array | Passes one `%Buffer` value rather than an array composite. |

#### Purpose

This case checks that a live helper call accepting an undefined composite does not cause invalid module handling or execution failure.

#### Structural Design

1. Declare the `%Buffer` composite type.
2. Create `%undef_res` with `OpUndef %Buffer`.
3. Call the helper with `%undef_res` on the live branch.
4. Extract a member and return without asserting an undefined numeric value.

#### Shader Code

The case uses direct SPIR-V assembly and does not use GLSL or HLSL source. The relevant assembly shape is:

```text
%undef_res = OpUndef %Buffer
%condition = OpConstantTrue %bool
%unused = OpFunctionCall %void %process_undef %undef_res
```

#### Additional Info

- Array variants use `OpCompositeExtract` with an additional index.
- Dynamic descriptor variants add the dynamic offset binding required by Vulkan.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Descriptor type | `storage` is representative; uniform and dynamic variants change the binding declaration. | [parameter construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L49-L71) |
| Control flow | `livecode` executes the helper; non-live variants use `OpConstantFalse`. | [condition specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L81-L90) |

#### SPIR-V

- Source: `vktSpvAsmOpUndefTests.cpp`, `OpUndefBufferComputeTestCase::initPrograms`
- Stage: Compute
- Status: Source-authored assembly validated by the CTS SPIR-V build path
- Target SPIRV version: 1.3

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
               OpCapability Shader
               OpMemoryModel Logical GLSL450
%undef_res = OpUndef %Buffer
```

</details>

## Runtime Execution and Result Checking

Each case creates the selected buffer descriptor, builds the SPIR-V module, dispatches one compute workgroup, and waits for completion. The test requires successful pipeline creation and execution; it does not compare an undefined value against a fixed numeric reference.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior | Possible cause |
|------------------|----------------|
| Dead-code case fails to build | Incorrect validation or handling of `OpUndef` in an unexecuted branch. |
| Live-code case fails | Invalid composite type, function parameter, descriptor declaration, or execution handling. |
| Dynamic case fails | Incorrect dynamic descriptor binding or offset handling. |

### Cause Analysis

#### Undefined composite handling

**Possible failure symptoms:** Pipeline creation or dispatch fails for a live-code or array variant.

**Possible implementation causes:** The implementation may reject a legal undefined composite, mishandle `OpCompositeExtract`, or incorrectly require a deterministic payload.

## Case Pruning

### Requirement-based pruning

Cases are subject to the descriptor and Vulkan feature requirements of their selected uniform or storage buffer type.

### Design-based pruning

The matrix uses one scalar structure and one array shape, plus live/dead control-flow variants, to cover the type and execution boundaries without enumerating every composite shape.

## Key Takeaways

- `OpUndef` cases test legal undefined-value handling, not a fixed undefined bit pattern.
- The matrix varies descriptor class, dynamic binding, composite shape, and live control flow.
- Successful module creation and execution are the primary result contract.

## Source Reference Appendix

- [OpUndef implementation and registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp#L49-L310)
- [Instruction-family integration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L7460-L7475)
- [SPIR-V MUSTPASS entries](../../../mustpass/main/vk-default/spirv-assembly.txt)
