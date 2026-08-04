# Understanding Brief: `amd_trinary_minmax`

## One-Sentence Test Purpose

This test checks whether `VK_AMD_shader_trinary_minmax` produces the minimum, maximum, or median of three signed, unsigned, or floating-point operands across supported scalar and vector widths.

## Background Knowledge

### AMD trinary min/max SPIR-V instructions

`SPV_AMD_shader_trinary_minmax` supplies `SMin3AMD`, `UMin3AMD`, `FMin3AMD`, and matching `Max3` and `Mid3` instructions. Each instruction consumes three values of one scalar or vector type and returns one value of that type. `mid3` returns the middle value after ordering the three operands, rather than their arithmetic average.

Why it matters here:
- The `min3`, `max3`, and `mid3` test families select the instruction operation.
- Signed integers, unsigned integers, and floating point values use distinct instruction names.

### Storage-buffer layout for scalar and vector cases

The assembly reads three same-typed operands from one storage buffer and writes one result to a second storage buffer. Array strides derive from the selected operand size. A `vec3` has three logical components but uses the size of four components when the host computes its storage footprint ([`effectiveComponents()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L106-L123)).

Why it matters here:
- Each shader invocation handles one operation index.
- The CPU reference and the shader must use identical component count and byte layout.

## One Concrete Example

For `dEQP-VK.spirv_assembly.instruction.amd_trinary_minmax.min3.f32.scalar`, the test uses 100 triplets of 32-bit floating-point operands. The generated SPIR-V reads `op1`, `op2`, and `op3` for `gl_GlobalInvocationID.x`, executes `FMin3AMD`, and stores one 32-bit result. The host applies `min3` to the same three input values before dispatch, then compares the output bytes with its reference ([assembly template](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L737-L835), [CPU reference](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L480-L533)).

## End-to-End Test Flow

```text
[host] select operation, base type, width, aggregation, and a per-case random seed
[host] specialize the SPIR-V assembly template and generate 100 input operand triplets
[host] compute 100 reference results with the matching CPU min3, max3, or mid3 helper
[host] create input and output storage buffers, bind them at set 0 bindings 0 and 1, and dispatch 100 compute invocations
[device] each invocation loads one operand triplet, runs the selected AMD trinary operation, and stores one result
[host] invalidate the output allocation, compare each output component with the reference, and report the first operation/component mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test specializes one CTS-authored SPIR-V assembly template. Substitutions select capabilities and storage extensions, the scalar or vector operand type, byte strides, one of `SMin3AMD`, `UMin3AMD`, or `FMin3AMD` and its `Max3` or `Mid3` counterpart, and the fixed array size `100` ([`getSpirVReplacements()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L632-L734), [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L737-L835)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input storage buffer | Yes | Yes, set `0` binding `0` | Read | No | Stores 100 records of three operands. |
| Output storage buffer | Yes | Yes, set `0` binding `1` | Written | Yes | Stores one computed value per input triplet. |
| Reference buffer | Yes | No | No | Yes | Holds CPU results for the byte-for-byte comparison. |

## What Is Checked

- The host generates random components from the selected type and evaluates each input triplet with the matching CPU helper.
- The compute dispatch contains `100` invocations with `LocalSize 1 1 1`, so each invocation handles one record.
- `OperationManager::compareResults()` compares each component byte-for-byte and returns the first `(operation, component)` mismatch; a mismatch fails the test ([comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L510-L533), [dispatch and status](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L843-L974)).

## Behavior Parameter Identification

> **Behavior parameter:** operation test family
>
> **Candidate values:** `min3`, `max3`, `mid3`

The operation family changes the trinary instruction and CPU reference function. Type width, signedness, and aggregation specialize the representation and feature requirements while retaining that operation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `min3` | Incorrect signed, unsigned, or floating-point minimum instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |
| `max3` | Incorrect signed, unsigned, or floating-point maximum instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |
| `mid3` | Incorrect signed, unsigned, or floating-point median instruction selection or evaluation; a type/layout specialization can also produce an incorrect result. |

## Important Variations and Special Cases

- The generated matrix contains `min3`, `max3`, and `mid3`; each operation has `i8`, `u8`, `f16`, `i16`, `u16`, `f32`, `u32`, `f64`, `i64`, and `u64` intermediate nodes, with `scalar`, `vec2`, `vec3`, and `vec4` leaves. There is no `f8` node because the registration loop skips 8-bit floats ([registration loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L1040)).
- 8-bit and 16-bit cases require storage-buffer extensions and access features. Integer widths additionally require `shaderInt8`, `shaderInt16`, or `shaderInt64`; floating-point 16-bit and 64-bit cases require `shaderFloat16` or `shaderFloat64` ([`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L630)).
- Floating-point input generation emits positive or negative infinity with a one-in-ten chance and otherwise rejects denormals. This tests ordered finite values plus infinities, but it does not generate NaNs ([`genFloat()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L195-L224)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| CPU operation and input generation | [`OperationManager`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L126-L533) | Defines the reference min/max/median operations, generated input values, and comparison. |
| Support requirements | [`TrinaryMinMaxCase::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L630) | Gates each width and base-type specialization. |
| Assembly specialization | [`getSpirVReplacements()` and `initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L632-L835) | Builds the typed assembly and selected AMD instruction. |
| Runtime and result check | [`TrinaryMinMaxInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L843-L974) | Creates resources, dispatches, and decides pass/fail. |
| Registration matrix | [`createTrinaryMinMaxGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L1043) | Registers operation, type, width, and aggregation paths. |

## Questions / Risk Points for User Audit

- Does `mid3` clearly read as the median of three values rather than an average?
- Does the explanation distinguish the operation-family behavioral axis from type and aggregation specializations?
- Is the storage-buffer explanation sufficient to connect byte layout with reference comparison?

## Conversion Notes for Final Wiki Rewrite

- Use `min3`, `max3`, and `mid3` as the final page's behavior parameters and copy the failure-cause mapping table unchanged.
- Use the `min3.f32.scalar` path as the representative assembly walkthrough; summarize the other operations and representation variants in a variation table.
- Distill the two background concepts into brief prerequisite bullets and move the detailed artifact/resource flow into the runtime and shader sections.
