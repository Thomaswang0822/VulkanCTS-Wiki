## Overview

**Core question:** Does the implementation correctly compute SPIR-V integer operations whose carried signedness intentionally mismatches the declared operand type's signedness?

- Source file: [`vktSpvAsmSignedOpTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp), a pure Amber dispatcher that registers 21 test case leaves under the `signed_op` test family.
- Registered path: `spirv_assembly.instruction.compute.signed_op`, parented by [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21419).
- The dispatcher and [`vk-default` mustpass span](../../../mustpass/main/vk-default/spirv-assembly.txt#L16178-L16198) enumerate the same 21 leaves. The data directory also contains unregistered `uint_umulextended.amber`; it is not a `signed_op` leaf and is absent from the mustpass span.
- The cases apply GLSL.std.450 extended instructions (`FindUMsb`, `FindSMsb`, `UClamp`, `UMax`, `UMin`, `SAbs`, `SClamp`, `SMax`, `SMin`, `SSign`, `SMulExtended`), core SPIR-V signed integer opcodes (`OpSDiv`, `OpSNegate`), atomic min/max opcodes (`OpAtomicUMax`, `OpAtomicUMin`, `OpAtomicSMax`, `OpAtomicSMin`), and unsigned comparison opcodes (`OpUGreaterThan`, `OpUGreaterThanEqual`, `OpULessThan`, `OpULessThanEqual`) to a 32-bit integer storage buffer whose declared element type carries the opposite signedness.
- The reader should expect: the registration hierarchy, the behavioral grouping of the 21 leaves, one representative shader walkthrough, the Amber pass/fail mechanic, and failure meaning per behavioral group.

## Background Knowledge

- **SPIR-V signedness lives on the type, not the value.** `OpTypeInt 32 0` declares a 32-bit unsigned integer; `OpTypeInt 32 1` declares a 32-bit signed integer. The 32 bits themselves are identical; only the interpreting opcode decides whether they are read as two's-complement or unsigned. This test family deliberately binds a signedness-carrying opcode to a value whose declared type carries the opposite signedness, so the implementation must follow the opcode's signedness for the arithmetic while storing the result back into the declared type.
- **GLSL.std.450 extended instructions and core opcodes carry signedness differently.** GLSL.std.450 instructions such as `SAbs`, `SMax`, `UMin`, `FindUMsb`, and `FindSMsb` encode the signed interpretation in the instruction name and take a result type from the caller. Core SPIR-V integer opcodes such as `OpSDiv`, `OpSNegate`, `OpAtomicSMax`, `OpAtomicUMax`, and `OpUGreaterThan` encode the signed interpretation directly in the opcode mnemonic. Both categories appear in this test family; in every case the operation's signedness is mismatched against the storage buffer's declared element type.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.signed_op
├── glsl_int_findumsb
├── glsl_int_uclamp
├── glsl_int_umax
├── glsl_int_umin
├── glsl_uint_findsmsb
├── glsl_uint_sabs
├── glsl_uint_sclamp
├── glsl_uint_smax
├── glsl_uint_smin
├── glsl_uint_ssign
├── int_atomicumax
├── int_atomicumin
├── int_ugreaterthan
├── int_ugreaterthanequal
├── int_ulessthan
├── int_ulessthanequal
├── uint_atomicsmax
├── uint_atomicsmin
├── uint_sdiv
├── uint_smulextended
└── uint_snegate
```

The `signed_op` test family is added to the `compute` intermediate node by [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21419). There are no intermediate nodes between the test family and the 21 test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation | `FindUMsb`, `FindSMsb`, `UClamp`, `UMax`, `UMin`, `SAbs`, `SClamp`, `SMax`, `SMin`, `SSign`, `SMulExtended`, `OpSDiv`, `OpSNegate`, `OpAtomicUMax`, `OpAtomicUMin`, `OpAtomicSMax`, `OpAtomicSMin`, `OpUGreaterThan`, `OpUGreaterThanEqual`, `OpULessThan`, `OpULessThanEqual` | The single SPIR-V instruction under test; each leaf exercises one instruction. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Operand declared type | 32-bit signed `int`, 32-bit unsigned `uint` | The element type of the storage buffer the operation reads from and writes to. The operation's carried signedness is intentionally opposite to this declared type. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Dispatch width | 2, 3, 5, 8, 15, or 16 invocations | The `RUN compute_pipeline <N> 1 1` width chosen by the leaf's hand-picked data set. | [Amber data directory](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/) |

The dispatch width is not an independent behavioral axis: it follows from the number of input values each leaf's Amber script hand-picks to exercise the operation. The dimension is listed only because it varies across leaves.

## Behavior Parameters

The primary behavioral axis is the **behavioral group**: each of the 21 test case leaves clusters into one of six groups by which signedness the operation carries and which signedness the storage buffer's declared element type carries. The group determines what a failure of any leaf in it would point to.

### GLSL.std.450 unsigned ops on signed `int`: `FindUMsb`, `UClamp`, `UMax`, `UMin`

Leaves: [`glsl_int_findumsb`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_findumsb.amber), [`glsl_int_uclamp`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_uclamp.amber), [`glsl_int_umax`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_umax.amber), [`glsl_int_umin`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_umin.amber).

The storage buffer element type is `OpTypeInt 32 1` (signed `int`), but the GLSL.std.450 instruction (`FindUMsb`, `UClamp`, `UMax`, `UMin`) interprets the operand bits as unsigned. A correct implementation reads the signed-typed value, applies the unsigned interpretation for the duration of the operation, and stores the result back into the signed-typed storage slot. `glsl_int_findumsb` is the representative walkthrough case below.

### GLSL.std.450 signed ops on `uint`: `FindSMsb`, `SAbs`, `SClamp`, `SMax`, `SMin`, `SSign`

Leaves: [`glsl_uint_findsmsb`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_findsmsb.amber), [`glsl_uint_sabs`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_sabs.amber), [`glsl_uint_sclamp`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_sclamp.amber), [`glsl_uint_smax`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_smax.amber), [`glsl_uint_smin`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_smin.amber), [`glsl_uint_ssign`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_ssign.amber).

The mirror of the previous group: the storage buffer element type is `OpTypeInt 32 0` (unsigned `uint`), but the GLSL.std.450 instruction (`SAbs`, `SClamp`, `SMax`, `SMin`, `SSign`, `FindSMsb`) interprets the operand bits as two's-complement signed. For example, [`glsl_uint_sabs`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_uint_sabs.amber) feeds the bit pattern of `-7` (declared as `uint`) into `SAbs` and expects `7` back, proving the instruction followed its own signed semantics rather than the unsigned declared type.

### Atomic unsigned ops on signed `int`: `OpAtomicUMax`, `OpAtomicUMin`

Leaves: [`int_atomicumax`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_atomicumax.amber), [`int_atomicumin`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_atomicumin.amber).

The storage buffer element type is signed `int`, but the atomic opcode (`OpAtomicUMax` or `OpAtomicUMin`) performs the comparison as unsigned. [`int_atomicumax`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_atomicumax.amber) supplies signed input values `-7` through `7` and initializes the corresponding output slots to `7` through `-7`, then atomically combines each input with its same-index output slot using unsigned comparison. Because `LocalSize 1 1 1` gives one element per workgroup, the atomicity itself is not stressed; the leaf is really checking that the unsigned comparison path is taken on a signed-typed pointer.

### Unsigned comparison ops on signed `int`: `OpUGreaterThan`, `OpUGreaterThanEqual`, `OpULessThan`, `OpULessThanEqual`

Leaves: [`int_ugreaterthan`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_ugreaterthan.amber), [`int_ugreaterthanequal`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_ugreaterthanequal.amber), [`int_ulessthan`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_ulessthan.amber), [`int_ulessthanequal`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_ulessthanequal.amber).

Both input buffers are typed as signed `int`, but the comparison opcode carries unsigned semantics. The result `bool` is converted to `int` (`0` or `1`) via `OpSelect` and stored. [`int_ugreaterthan`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/int_ugreaterthan.amber) compares `-65536` against `32768`; signed comparison would say `-65536 < 32768` (result `0`), but unsigned comparison of the same bits says `0xFFFF0000 > 0x00008000` (result `1`), which is the expected output.

### Atomic signed ops on `uint`: `OpAtomicSMax`, `OpAtomicSMin`

Leaves: [`uint_atomicsmax`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_atomicsmax.amber), [`uint_atomicsmin`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_atomicsmin.amber).

The storage buffer element type is `uint`, but the atomic opcode (`OpAtomicSMax` or `OpAtomicSMin`) performs the comparison as signed. As with the unsigned-atomic group, `LocalSize 1 1 1` means the leaf checks the signed comparison path on an unsigned-typed pointer rather than atomic contention.

### Other signed ops on `uint`: `OpSDiv`, `SMulExtended`, `OpSNegate`

Leaves: [`uint_sdiv`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_sdiv.amber), [`uint_smulextended`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_smulextended.amber), [`uint_snegate`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_snegate.amber).

The storage buffer element type is `uint`, but the opcode (`OpSDiv`, `OpSMulExtended`, `OpSNegate`) treats the bits as signed. [`uint_snegate`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_snegate.amber) negates the bit pattern of `-1` (declared as `uint`) and expects `1`; [`uint_sdiv`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/uint_sdiv.amber) divides `-2` by `-1` and expects `2`. Both confirm the signed opcode path overrides the unsigned declared type.

## Shader Analysis

The shaders in this family are authored directly as SPIR-V assembly inside Amber files; they are not generated from GLSL or HLSL. The representative module below is extracted from `glsl_int_findumsb.amber`. Its Amber assembly was assembled and validated, then disassembled, reassembled, and validated again with SPIR-V Tools for the Vulkan 1.0 target environment. The reassembled binary is byte-identical to the first binary. The final `SPIR-V` subsection publishes that complete fresh disassembly rather than duplicating the authored assembly.

The 21 registered leaves share a near-identical compute shader skeleton: one `GLCompute` entry point, `LocalSize 1 1 1`, an `Input` `GlobalInvocationId` builtin, and `BufferBlock` storage structures containing runtime arrays of the relevant scalar type. The operation line, operand count and bindings, output shape, and hand-picked data vary by leaf.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.signed_op.glsl_int_findumsb
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `glsl_int_findumsb` | Selects the Amber leaf that invokes `GLSL.std.450 FindUMsb`. |
| Declared operand type: signed `int` | `%int = OpTypeInt 32 1`; the input and output runtime arrays contain signed 32-bit integers. |
| Operation semantics: unsigned | `FindUMsb` interprets the operand bits as an unsigned integer when locating the most significant set bit. |
| `LocalSize 1 1 1`, dispatch `2 1 1` | Two invocations process the two input elements independently. |
| Input / expected output | `0, -1` / `-1, 31`. |

#### Purpose

This leaf checks that `FindUMsb` follows the instruction's unsigned interpretation even though its operand and result use the signed `%int` type. Zero must produce `-1`, while the signed value `-1` has the bit pattern `0xffffffff` and must produce bit index `31`.

#### Structural Design

| Phase | Direct SPIR-V behavior | Role in the check |
|-------|------------------------|-------------------|
| Invocation selection | Load `gl_GlobalInvocationId.x`. | Select the same element in the input and output arrays. |
| Input read | Load `%int` from descriptor set `0`, binding `0`. | Supplies a signed-typed 32-bit value. |
| Tested operation | `%outvalue = OpExtInst %int %glsl FindUMsb %invalue`. | Requires unsigned bit-search semantics despite the signed declared type. |
| Result write | Store `%outvalue` to descriptor set `0`, binding `1`. | Exposes the integer result to Amber. |
| Verification | `EXPECT data1 EQ_BUFFER expected0`. | Requires exact element-wise equality with `-1, 31`. |

`%gl_GlobalInvocationId` is an `Input` `vec3<uint>`. Its X component indexes `%input` and `%output`, which are legacy `Uniform` storage-buffer variables whose shared wrapper type is decorated `BufferBlock`. The runtime array has `ArrayStride 4`, and the wrapper's only member has offset `0`. The Amber pipeline binds `data0` to binding `0` and `data1` to binding `1`; the initial output sentinels are `8, 8`.

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the tested shader module directly as SPIR-V assembly between `SHADER compute test SPIRV-ASM` and `END` in [`glsl_int_findumsb.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_findumsb.amber). That Amber artifact is the authoritative shader source, and the complete validated assembly is presented only in the final `SPIR-V` subsection.

#### Additional Info

- `FindUMsb(0)` returns `-1` because no bit is set. For input `-1`, the stored 32-bit pattern is `0xffffffff`, so unsigned interpretation selects bit `31`.
- `%struct_int2` in the authored source is a generated name for a structure containing a runtime array; it is not a two-component vector. The separately declared `%int2` vector is unused.
- The module uses the SPIR-V 1.0 `Uniform` plus `BufferBlock` storage-buffer encoding used by the Amber artifact.
- Validation gate: `spirv-as --target-env vulkan1.0`, `spirv-val --target-env vulkan1.0`, `spirv-dis`, reassembly, and a second validation all succeed; the original and round-tripped binaries are byte-identical.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| GLSL.std.450 unsigned ops on signed `int` | Replaces `FindUMsb` with `UClamp`, `UMax`, or `UMin` and adds operands/bindings as needed; `%int` remains signed. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| GLSL.std.450 signed ops on `uint` | Uses `FindSMsb`, `SAbs`, `SClamp`, `SMax`, `SMin`, or `SSign`; storage elements become `%uint`. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Atomic unsigned ops on signed `int` | Replaces the extended instruction with `OpAtomicUMax` or `OpAtomicUMin` on a signed-typed output pointer. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Unsigned comparisons on signed `int` | Uses an `OpU*` comparison, then `OpSelect` converts the boolean result to `0` or `1`. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Atomic signed ops on `uint` | Uses `OpAtomicSMax` or `OpAtomicSMin` on an unsigned-typed output pointer. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |
| Other signed ops on `uint` | Uses `OpSDiv`, `OpSMulExtended`, or `OpSNegate` with unsigned declared storage types. | [`cases` table](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) |

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
; Bound: 28
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_GlobalInvocationID
               OpExecutionMode %2 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %_struct_5 BufferBlock
               OpMemberDecorate %_struct_5 0 Offset 0
               OpDecorate %6 DescriptorSet 0
               OpDecorate %6 Binding 0
               OpDecorate %7 DescriptorSet 0
               OpDecorate %7 Binding 1
       %uint = OpTypeInt 32 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%_ptr_Input_uint = OpTypePointer Input %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
       %void = OpTypeVoid
         %14 = OpTypeFunction %void
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
        %int = OpTypeInt 32 1
%_runtimearr_int = OpTypeRuntimeArray %int
      %v2int = OpTypeVector %int 2
%_ptr_Uniform_int = OpTypePointer Uniform %int
  %_struct_5 = OpTypeStruct %_runtimearr_int
%_ptr_Uniform__struct_5 = OpTypePointer Uniform %_struct_5
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %6 = OpVariable %_ptr_Uniform__struct_5 Uniform
          %7 = OpVariable %_ptr_Uniform__struct_5 Uniform
          %2 = OpFunction %void None %14
         %21 = OpLabel
         %22 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %23 = OpLoad %uint %22
         %24 = OpAccessChain %_ptr_Uniform_int %6 %uint_0 %23
         %25 = OpLoad %int %24
         %26 = OpExtInst %int %1 FindUMsb %25
         %27 = OpAccessChain %_ptr_Uniform_int %7 %uint_0 %23
               OpStore %27 %26
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The C++ dispatcher builds each leaf's file name from `std::string(cases[i].basename) + ".amber"` and calls [`cts_amber::createAmberTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L73-L79) with the [`spirv_assembly/instruction/compute/signed_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L92) data directory. The Amber framework, not C++ host code, owns pipeline creation, descriptor binding, dispatch, and result comparison.
- Each Amber script attaches the embedded SPIR-V assembly as the `test` compute shader, binds the declared storage buffers at descriptor set 0 (input(s) at the lowest binding numbers, output at the highest), and dispatches with `RUN compute_pipeline <N> 1 1` where `N` matches the element count.
- `LocalSize 1 1 1` means each workgroup processes one element; there is no workgroup-wide synchronization or shared memory.
- The atomic-leaf cases (`int_atomicumax`, `int_atomicumin`, `uint_atomicsmax`, `uint_atomicsmin`) use `OpAtomicUMax` / `OpAtomicUMin` / `OpAtomicSMax` / `OpAtomicSMin` with `scope` `%uint_1` (Device) and `semantics` `%uint_0` (none). Because each output slot is touched by one invocation, the atomicity is not contended; the opcode is used to select the signedness of the comparison, not to test atomic ordering.
- `EXPECT <output_buffer> EQ_BUFFER <expected_buffer>` decides pass/fail; it compares the output storage buffer element-wise against the expected buffer after dispatch. Any element mismatch fails the leaf.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| GLSL.std.450 unsigned ops on signed `int` | Signedness interpretation mismatch: the implementation computed `FindUMsb` / `UClamp` / `UMax` / `UMin` using signed semantics on the signed-typed operand instead of unsigned. |
| GLSL.std.450 signed ops on `uint` | Signedness interpretation mismatch: the implementation computed `SAbs` / `SClamp` / `SMax` / `SMin` / `SSign` / `FindSMsb` using unsigned semantics on the unsigned-typed operand instead of signed. |
| Atomic unsigned ops on signed `int` | Signedness interpretation mismatch in the atomic compare path, or atomic memory scope/semantics mishandling on the signed-typed pointer. |
| Unsigned comparison ops on signed `int` | Signedness interpretation mismatch: `OpUGreaterThan` / `OpUGreaterThanEqual` / `OpULessThan` / `OpULessThanEqual` compared using signed semantics on the signed-typed operands. |
| Atomic signed ops on `uint` | Signedness interpretation mismatch in the atomic compare path, or atomic memory scope/semantics mishandling on the unsigned-typed pointer. |
| Other signed ops on `uint` | Signedness interpretation mismatch: `OpSDiv` / `OpSMulExtended` / `OpSNegate` computed using unsigned semantics on the unsigned-typed operand instead of signed. |

The Amber harness is a common layer, so a pipeline, descriptor-binding, or `EQ_BUFFER` comparison defect can cause a cross-operation failure pattern. The distinct binding counts and output layouts mean that a failure pattern still needs to be compared with the individual script before assigning it to common infrastructure.

### Cause Analysis

#### Signedness interpretation mismatch

**Possible failure symptoms:** The output buffer element for at least one input value differs from the expected buffer. The direction of the error tracks the signedness mix-up: for example, `glsl_int_findumsb` would return `30` instead of `31` for input `-1` if a signed shift were used; `glsl_uint_sabs` would return a large positive value instead of `7` for the bit pattern of `-7` if `SAbs` were skipped; `int_ugreaterthan` would return `0` instead of `1` for `(-65536, 32768)` if signed comparison were used.

**Possible implementation causes:** The SPIR-V opcode or GLSL.std.450 instruction name is the sole carrier of the operation's signedness, and the operand type's signedness is the opposite. A driver or SPIR-V frontend that lowers the operation by trusting the operand type's signedness, or that folds the extended instruction into a native instruction with the wrong signed flavor, produces a bit-correct but interpretation-wrong result. This is the core defect class the test family is designed to catch.

#### Atomic memory scope and semantics handling

**Possible failure symptoms:** For `int_atomicumax`, `int_atomicumin`, `uint_atomicsmax`, and `uint_atomicsmin`, the output buffer element for at least one slot differs from the expected buffer. Because each slot is touched by one invocation, a pure ordering bug is unlikely to manifest; a wrong-result symptom on these leaves more likely indicates the wrong signed compare path than an atomic ordering defect.

**Possible implementation causes:** The atomic opcodes carry `scope = Device` and `semantics = None`. An implementation that mishandles `semantics = None` (for example, by inserting an unintended barrier or by ignoring the store half of the atomic) could produce a wrong output, but the single-invocation-per-slot design makes this a secondary suspect. The primary suspect remains the signedness of the embedded compare; source-level investigation is needed to confirm any atomic-specific defect beyond the signedness path.

#### Amber infrastructure / descriptor binding defect

**Possible failure symptoms:** Every leaf fails uniformly, or the output buffer retains its initial sentinel values (for example, `8 8 ...`) after dispatch, which means the shader never wrote to it.

**Possible implementation causes:** A defect in Amber's pipeline construction, storage-buffer descriptor binding at descriptor set 0, or the `EQ_BUFFER` comparison harness would affect all leaves regardless of the operation under test. Such a defect is not specific to this test family and would surface across many Amber-backed CTS categories at once.

## Case Pruning

### Requirement-based pruning

The entire `signed_op` test family is compiled only for non-VulkanSC builds: the registration loop is wrapped in [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L38-L84). On Vulkan SC targets the group is empty and no leaf is registered. No per-leaf device feature, extension, or limit gate is applied; the cases assume baseline Vulkan compute with storage buffers.

### Design-based pruning

No design-based pruning applies. The 21 leaves are a fixed hand-curated enumeration of one operation each, not a generated matrix. Each leaf's input buffer is a small hand-picked set of values chosen to expose the signedness mismatch (for example, `-1`, `-65536`, `0`); there is no generated parameter space to prune.

## Key Takeaways

- The test family's single tested property is signedness faithfulness: the SPIR-V opcode or GLSL.std.450 instruction name, not the declared operand type, must dictate the signed interpretation of the 32 bits.
- Every leaf is a one-instruction compute shader wrapped in Amber; the variation across leaves is the operation and the declared element type, not the infrastructure.
- The atomic leaves use `LocalSize 1 1 1` and one invocation per output slot, so they probe the atomic opcode's signed compare path rather than atomic contention.
- The C++ source description strings for `int_ugreaterthan`, `int_atomicumax`, and `uint_sdiv` do not match the operation performed by their Amber scripts; the Amber scripts are the source of truth for what each leaf tests.
- See `## Failure Meaning` for how a leaf's failure maps back to a signedness interpretation defect versus an Amber infrastructure defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createSignedOpTestsGroup` | [`vktSpvAsmSignedOpTests.cpp#L89`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89) | Top-level group factory; names the test family `signed_op` and the Amber data directory. |
| `cases` table | [`vktSpvAsmSignedOpTests.cpp#L49-L71`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L49-L71) | The 21-leaf enumeration with basenames and (sometimes mismatched) description strings. |
| Amber dispatch loop | [`vktSpvAsmSignedOpTests.cpp#L73-L80`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L73-L80) | Builds `<basename>.amber` file names and calls `createAmberTestCase`. |
| VulkanSC guard | [`vktSpvAsmSignedOpTests.cpp#L40-L84`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L40-L84) | Wraps the registration loop in `#ifndef CTS_USES_VULKANSC`. |
| Parent registration | [`vktSpvAsmInstructionTests.cpp#L21419`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21419) | Adds `signed_op` under `spirv_assembly.instruction.compute`. |
| Amber data directory | [`spirv_assembly/instruction/compute/signed_op/`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/) | Contains the 21 registered scripts plus unregistered `uint_umulextended.amber`; each registered script embeds SPIR-V assembly and `EQ_BUFFER` checks. |
| Representative case | [`glsl_int_findumsb.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_op/glsl_int_findumsb.amber) | Source of the `#### Source Code` SPIR-V assembly in the walkthrough above. |
