## Overview

**Core question:** Do the signed SPIR-V integer comparison instructions interpret the bit patterns in 32-bit `uint` storage buffers as signed two's-complement integers?

- This page covers the `signed_int_compare` test family implemented by [`vktSpvAsmSignedIntCompareTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L38-L79).
- The family registers four Amber-backed compute leaves. Each loads two values declared as `OpTypeInt 32 0`, applies one `OpS*` comparison, converts the Boolean result to `0` or `1` with `OpSelect`, and checks the output buffer against a literal expected vector.
- Negative decimal inputs in the Amber `ssbo ... subdata int` declarations provide the decisive bit patterns. The shader declaration remains unsigned; the comparison opcode must instead apply signed interpretation.

## Background Knowledge

- **The signedness flag is attached to the integer type.** `OpTypeInt 32 0` declares a 32-bit unsigned integer type. It does not change the 32 stored bits. When those bits originated from a negative signed decimal, a signed operation reads the same two's-complement representation as a negative value, whereas an unsigned operation reads it as a large positive value.
- **`OpS*` controls comparison interpretation.** `OpSGreaterThan`, `OpSGreaterThanEqual`, `OpSLessThan`, and `OpSLessThanEqual` take the signed-comparison path. In these Amber modules, `%uint` is still `OpTypeInt 32 0`; the test is specifically whether the opcode's `S` interpretation wins over that declared type.
- **The result is made observable as an integer.** Each comparison produces `%bool`. `OpSelect %uint %26 %uint_1 %uint_0` encodes true as `1` and false as `0`, then stores it in the output storage buffer. Amber probes that buffer after dispatch.
- **Amber is the host-side test description.** Its `[compute shader spirv]` block supplies literal SPIR-V assembly; its `[test]` block initializes three SSBOs, dispatches 16 invocations, and states the expected result vector. The C++ file only maps registered names to those artifacts.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.signed_int_compare
├── uint_sgreaterthanequal
├── uint_sgreaterthan
├── uint_slessthan
└── uint_slessthanequal
```

[`createSignedIntCompareGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L79) registers `signed_int_compare` below the compute instruction node. Its four leaves come directly from the `cases` array ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L43-L64)), and the main Vulkan mustpass inventory contains the same four paths ([mustpass entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L16174-L16177)). The parent registration is enclosed by `#ifndef CTS_USES_VULKANSC`, so this family is absent from Vulkan SC builds ([parent registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21415-L21420)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Signed comparison opcode | `OpSGreaterThanEqual`, `OpSGreaterThan`, `OpSLessThan`, `OpSLessThanEqual` | Selects the relation applied to the two unsigned-declared operand buffers. | [four Amber artifacts](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/) |
| Declared operand / result type | `OpTypeInt 32 0` (`uint`) | Keeps both inputs and the `0`/`1` output declared unsigned even though the comparison is signed. | [`uint_sgreaterthan.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber) |
| Input vectors | 16 fixed 32-bit values in each input buffer | Include negative bit patterns, zero, equal values, and positive values to distinguish signed relation behavior. | [Amber input data](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber#L60-L65) |
| Dispatch geometry | `compute 16 1 1`; shader `LocalSize 1 1 1` | Produces one invocation per array element, indexed through `GlobalInvocationId.x`. | [representative Amber script](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber#L14-L15) |

The opcode is the behavioral parameter. The declared type, fixed input vectors, descriptor layout, and dispatch geometry remain the same across all four scripts.

## Behavior Parameters

### `uint_sgreaterthanequal`: `OpSGreaterThanEqual`

[`uint_sgreaterthanequal.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthanequal.amber) emits `OpSGreaterThanEqual`. Its expected vector contains `1` when the first bit pattern is signed-greater-than or signed-equal to the second and `0` otherwise. Equality is visible at indices such as `-7` versus `-7` and `0` versus `0`, where this leaf differs from strict greater-than.

### `uint_sgreaterthan`: `OpSGreaterThan`

[`uint_sgreaterthan.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber) emits `OpSGreaterThan`. This representative leaf expects `1` at five of the 16 positions. At index 3, the stored bits for `-5` compare less than `2` when signed but greater when unsigned, so the expected `0` distinguishes the signed operation from `OpUGreaterThan`.

### `uint_slessthan`: `OpSLessThan`

[`uint_slessthan.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthan.amber) emits `OpSLessThan`. It is the strict complementary relation to `uint_sgreaterthanequal` for these operand pairs: the expected vector has `1` at seven positions and `0` at equal pairs.

### `uint_slessthanequal`: `OpSLessThanEqual`

[`uint_slessthanequal.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthanequal.amber) emits `OpSLessThanEqual`. It accepts both lower and equal signed values; accordingly, its expected vector has `1` at eleven positions. The script's surrounding illustrative OpenCL comment is not the oracle; the `OpSLessThanEqual` instruction and final `probe` line define the test.

## Shader Analysis

The Amber artifacts contain literal CTS-authored SPIR-V, not a C++ `StringTemplate` or reconstructed GLSL/HLSL. The representative `uint_sgreaterthan` module is reproduced once below from its `[compute shader spirv]` block. It was assembled, validated, and disassembled with `spirv-as`, `spirv-val`, and `spirv-dis` using the SPIR-V 1.0 target environment; the disassembly is validation evidence and is intentionally not duplicated on this page.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.signed_int_compare.uint_sgreaterthan
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `uint_sgreaterthan` | Selects `OpSGreaterThan` while all three SSBO element arrays remain `%uint = OpTypeInt 32 0`. |
| `%uint` operands | Both input arrays use unsigned-declared 32-bit scalar storage; negative Amber decimal values still supply their two's-complement bit patterns. |
| `compute 16 1 1` | Starts 16 one-invocation workgroups, so `GlobalInvocationId.x` selects one element per invocation. |
| Expected results | The final Amber probe expects `1 0 0 0 0 0 0 0 0 1 0 1 0 0 1 1`. |

#### Purpose

This shader proves that `OpSGreaterThan` uses signed ordering even when its operands have the unsigned `%uint` type. At index 3, the bit patterns for `-5` and `2` produce false under signed comparison but true under unsigned comparison, so the expected `0` distinguishes the signed opcode.

#### Structural Design

| Phase | Assembly behavior | Role in the check |
|-------|-------------------|-------------------|
| Index | Loads the x component of `%gl_GlobalInvocationID`. | Selects one corresponding element in every runtime array. |
| Operand loads | Accesses `%15` and `%16` at that index and loads `%23` and `%25` as `%uint`. | Retains the deliberately unsigned-declared operand type. |
| Comparison | Executes `OpSGreaterThan %bool %23 %25`. | Forces signed interpretation of those 32-bit values. |
| Encoding and store | `OpSelect` changes the Boolean to `%uint_1` or `%uint_0`, then stores through `%17`. | Produces a buffer value that Amber can compare directly. |

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for <code>uint_sgreaterthan</code></summary>

```llvm
               OpCapability Shader
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %18 "main" %gl_GlobalInvocationID
               OpExecutionMode %18 LocalSize 1 1 1
               OpSource OpenCL_C 120
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpMemberDecorate %_struct_3 0 Offset 0
               OpDecorate %_struct_3 BufferBlock
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %15 DescriptorSet 0
               OpDecorate %15 Binding 0
               OpDecorate %16 DescriptorSet 0
               OpDecorate %16 Binding 1
               OpDecorate %17 DescriptorSet 0
               OpDecorate %17 Binding 2
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
  %_struct_3 = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform__struct_3 = OpTypePointer Uniform %_struct_3
       %void = OpTypeVoid
          %6 = OpTypeFunction %void
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
       %bool = OpTypeBool
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
         %15 = OpVariable %_ptr_Uniform__struct_3 Uniform
         %16 = OpVariable %_ptr_Uniform__struct_3 Uniform
         %17 = OpVariable %_ptr_Uniform__struct_3 Uniform
         %18 = OpFunction %void None %6
         %19 = OpLabel
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %21 = OpLoad %uint %20
         %22 = OpAccessChain %_ptr_Uniform_uint %15 %uint_0 %21
         %23 = OpLoad %uint %22
         %24 = OpAccessChain %_ptr_Uniform_uint %16 %uint_0 %21
         %25 = OpLoad %uint %24
         %26 = OpSGreaterThan %bool %23 %25
         %27 = OpSelect %uint %26 %uint_1 %uint_0
         %28 = OpAccessChain %_ptr_Uniform_uint %17 %uint_0 %21
               OpStore %28 %27
               OpReturn
               OpFunctionEnd
```

</details>

#### Additional Info

- `%15`, `%16`, and `%17` are `Uniform` variables of the same `BufferBlock` wrapper type and are bound to descriptor set `0`, bindings `0`, `1`, and `2`.
- The runtime-array `ArrayStride` is `4`, matching one 32-bit element. No conversion changes either operand before `OpSGreaterThan`; the semantic distinction is only the opcode.
- `OpSource OpenCL_C 120` documents the source language metadata in this CTS test artifact. It does not replace the literal SPIR-V module or change Amber's probe-based oracle.

#### Parameter Variation Summary

| Parameter dimension | Change from the representative | Amber result effect |
|---------------------|--------------------------------|---------------------|
| Relation | Replaces `OpSGreaterThan` with `OpSGreaterThanEqual`, `OpSLessThan`, or `OpSLessThanEqual`. | Changes only which signed relation maps each pair to `0` or `1`. |
| Equality handling | The two `Equal` opcodes accept equal input values; strict opcodes reject them. | Alters expected results at equal pairs such as `-7`/`-7` and `0`/`0`. |
| SSBO layout and dispatch | Unchanged across all four files. | Every script has two input buffers, one output buffer, 16 elements, and `compute 16 1 1`. |

## Runtime Execution and Result Checking

- The C++ dispatcher iterates over the four `cases`, forms `<basename>.amber`, and calls [`cts_amber::createAmberTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L58-L64) with the `spirv_assembly/instruction/compute/signed_int_compare` data directory. It does not construct a Vulkan pipeline or calculate expected values itself.
- Amber creates the compute pipeline from the embedded SPIR-V, binds SSBOs at set `0`, bindings `0`, `1`, and `2`, and runs `compute 16 1 1`. The shader's `LocalSize 1 1 1` makes each invocation handle one input index.
- The two input buffers contain the same 16-element sequence in every leaf: `-8 -7 -6 -5 -4 -3 -2 0 0 1 2 3 4 5 6 7` and `-9 -7 -5 2 -1 1 0 0 1 0 2 -2 4 8 4 -4`. The output buffer starts with `8` values as a visible sentinel.
- `probe ssbo int 0:2 0 == ...` compares all 16 output elements with the literal expected vector. Any mismatch fails the Amber case; there is no tolerance or alternate host oracle.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uint_sgreaterthanequal` | Incorrect signed-greater-or-equal lowering for an unsigned-declared 32-bit operand, or a failure in the corresponding Amber SSBO read/write path. |
| `uint_sgreaterthan` | Incorrect signed-greater-than lowering or incorrect interpretation of negative two's-complement bit patterns. |
| `uint_slessthan` | Incorrect signed-less-than lowering, especially at negative/positive and equal-value boundaries. |
| `uint_slessthanequal` | Incorrect signed-less-than-or-equal lowering or mishandling of equality in the unsigned-declared storage path. |
| All four leaves | Shared SPIR-V integer comparison handling, descriptor binding, dispatch/index calculation, Amber pipeline setup, or output-buffer probing. |

### Cause Analysis

#### Signedness-specific comparison lowering

**Possible failure symptoms:** Failures cluster around pairs containing negative values, while equal or small positive pairs pass. A result may match an unsigned comparison instead of the signed expected vector.

**Possible implementation causes:** The implementation may select an unsigned comparison because the operands are `%uint`, or may lose the opcode's signed interpretation while lowering `OpSGreaterThan`, `OpSGreaterThanEqual`, `OpSLessThan`, or `OpSLessThanEqual`. The test establishes the semantic mismatch; it does not identify a particular compiler or hardware stage.

#### Equality boundary handling

**Possible failure symptoms:** Strict relations fail only at equal pairs, or the `Equal` variants disagree with their strict counterparts at `-7`/`-7` or `0`/`0`.

**Possible implementation causes:** The lowering may use the wrong strictness, or may mishandle the Boolean result before `OpSelect` encodes it. Comparing the four leaves together helps separate relation-specific errors from shared comparison errors.

#### Buffer transport or Amber execution

**Possible failure symptoms:** Many or all output positions contain the initial sentinel `8`, shifted values, or unrelated failures across all four leaves.

**Possible implementation causes:** Investigate descriptor bindings `0` through `2`, SSBO layout and `ArrayStride 4`, `GlobalInvocationId.x` indexing, compute dispatch, and output visibility/probing before attributing the result to signed comparison semantics.

## Case Pruning

- The source wraps test creation in `#ifndef CTS_USES_VULKANSC`; these four leaves are therefore registered only in non-VulkanSC builds.
- No special Vulkan extension or feature request is added by `vktSpvAsmSignedIntCompareTests.cpp`.
- The commented-out `foo` case in the C++ `cases` array is intentionally not a registered leaf and is not part of this page's hierarchy.
- The Amber files use 32-bit storage and `LocalSize 1 1 1`; there are no width, vector, graphics-stage, or multi-workgroup variants in this family.

## Key Takeaways

- `signed_int_compare` isolates four `OpS*` relations on values declared with the unsigned `OpTypeInt 32 0` type.
- Negative inputs make the signed-versus-unsigned distinction observable, while equal pairs separate strict from non-strict relations.
- Amber owns the pipeline setup and exact output oracle; the C++ source registers the four `.amber` files.
- A failure in one relation points first to that opcode's signedness or strictness handling; failures across all four also implicate shared SSBO or Amber execution paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Group creation | [`createSignedIntCompareGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L79) | Registers the `signed_int_compare` group and its data directory. |
| Case table and Amber dispatch | [`createSignedIntCompareTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L38-L69) | Defines the four leaves, descriptions, filenames, and non-VulkanSC guard. |
| Representative Amber artifact | [`uint_sgreaterthan.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber) | Contains the complete representative SPIR-V module, buffers, dispatch, and probe. |
| Other Amber artifacts | [`uint_sgreaterthanequal.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthanequal.amber), [`uint_slessthan.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthan.amber), [`uint_slessthanequal.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthanequal.amber) | Supply the three sibling signed relations and their exact expected vectors. |
| Parent registration | [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21415-L21420) | Shows where the family is attached and why it is omitted for Vulkan SC. |
| Mustpass inventory | [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L16174-L16177) | Confirms the four executable Vulkan test paths. |
