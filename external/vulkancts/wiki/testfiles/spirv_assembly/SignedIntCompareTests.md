## Overview

**Core question:** does the implementation treat SPIR-V `OpS*` comparison instructions as signed comparisons even when the operand type is declared unsigned?

The `signed_int_compare` test family is a small Amber-backed family registered under `spirv_assembly.instruction.compute.signed_int_compare`. It exercises four signed comparison opcodes (`OpSGreaterThan`, `OpSGreaterThanEqual`, `OpSLessThan`, and `OpSLessThanEqual`) applied to operands whose SPIR-V type is `%uint = OpTypeInt 32 0` (32-bit unsigned).

- The family targets the regression reported in [Google bug `b/73133282`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L20-L23): implementations that performed unsigned comparison when the operand type was unsigned, ignoring the `S` in the opcode name.
- The C++ source is a pure Amber dispatcher: it registers four test case leaves, each delegating the actual shader, resources, and pass/fail logic to an `.amber` file under [`spirv_assembly/instruction/compute/signed_int_compare/`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare).
- All four Amber cases share an identical SPIR-V compute shader skeleton, the same 16-element input arrays, and the same SSBO layout; only the comparison opcode and the expected probe values differ.
- A representative shader walkthrough, the per-opcode pass/fail matrix, and a focused failure analysis tied to signed/unsigned reinterpretation.

## Background Knowledge

- **SPIR-V opcode signedness is in the opcode, not the type.** `OpSGreaterThan`, `OpSGreaterThanEqual`, `OpSLessThan`, and `OpSLessThanEqual` perform signed integer comparison on the bit patterns of their operands. The signedness of the operand's `OpTypeInt` (the third operand to `OpTypeInt`, `0` for unsigned, `1` for signed) does not change the comparison semantics. The unsigned counterparts are `OpUGreaterThan`, `OpUGreaterThanEqual`, `OpULessThan`, and `OpULessThanEqual`. This separation is what the family audits.
- **Amber test pipeline.** Each test case leaf is an Amber script that bundles a SPIR-V compute shader, host-side SSBO initialization, dispatch dimensions, and result probes. The CTS C++ side merely loads the script via `cts_amber::createAmberTestCase` and lets the Amber runner compile the SPIR-V, allocate the SSBOs, dispatch the compute work, and read back the result buffer.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.signed_int_compare
├── uint_sgreaterthanequal
├── uint_sgreaterthan
├── uint_slessthan
└── uint_slessthanequal
```

The four test case leaves are flat under the test family; there are no intermediate nodes. The intermediate path components `instruction` and `compute` sit above the test family and locate it within the broader `spirv_assembly` test category.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Comparison opcode | `OpSGreaterThanEqual`, `OpSGreaterThan`, `OpSLessThan`, `OpSLessThanEqual` | The signed comparison instruction under test; selects which `OpS*` opcode the compute shader issues and which expected probe vector Amber checks | [`cases[]` array](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L49-L56) |
| Operand type | `%uint` (`OpTypeInt 32 0`) | Fixed across the family. Operands are declared unsigned 32-bit integers; the test asserts that `OpS*` still compares them as signed | [`uint_sgreaterthan.amber` SPIR-V](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber#L27) |
| Per-invocation input pair | 16 fixed `(A[i], B[i])` pairs | Same 16-element `A` and `B` arrays across all four cases; chosen to include negative and positive values whose bit patterns diverge sharply between signed and unsigned reading | [`uint_sgreaterthan.amber` test block](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber#L60-L65) |

The fixed 16-element input vectors are:

```
A[] = [-8, -7, -6, -5, -4, -3, -2,  0,  0,  1,  2,  3,  4,  5,  6,  7]
B[] = [-9, -7, -5,  2, -1,  1,  0,  0,  1,  0,  2, -2,  4,  8,  4, -4]
```

These values are written into the SSBOs through Amber's `ssbo ... subdata int` directive, which stores them as 32-bit two's-complement bit patterns. Loaded into `uint`-typed SSBOs, the negative values become large unsigned integers (for example, `-8` reads back as `0xFFFFFFF8`); the test asserts that `OpS*` opcodes still see them as `-8`.

## Behavior Parameters

The primary behavioral axis is the test case leaf: each leaf swaps the comparison opcode and the expected result vector, while everything else in the Amber script is identical.

### `uint_sgreaterthanequal` (`OpSGreaterThanEqual` on unsigned operands)

Tests `A[i] >= B[i]` with signed semantics on `%uint` operands. The expected result vector is `[1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1]`. The four `1`s at indices 1, 7, 10, and 12 distinguish `>=` from `>`: at those indices the operands are equal, so the equal-or-greater case is true while the strict-greater case is false.

### `uint_sgreaterthan` (`OpSGreaterThan` on unsigned operands)

Tests `A[i] > B[i]` with signed semantics on `%uint` operands. The expected result vector is `[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]`. This is the representative case walked through in `## Shader Analysis` below.

### `uint_slessthan` (`OpSLessThan` on unsigned operands)

Tests `A[i] < B[i]` with signed semantics on `%uint` operands. The expected result vector is `[0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0]`. It is the bitwise complement of the `uint_sgreaterthanequal` vector, since `A < B` holds exactly when `A >= B` does not.

### `uint_slessthanequal` (`OpSLessThanEqual` on unsigned operands)

Tests `A[i] <= B[i]` with signed semantics on `%uint` operands. The expected result vector is `[0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0]`. The four `1`s at indices 1, 7, 10, and 12 again mark the equality case where `<=` is true but `<` is false.

## Shader Analysis

The four cases share one shader skeleton. Only line `%26 = OpSGreaterThan %bool %23 %25` differs: each case substitutes the matching `OpS*` opcode. The walkthrough below uses `uint_sgreaterthan.amber` as the representative case; the structural description applies unchanged to the other three.

### Representative Shader Walkthrough 1 (`uint_sgreaterthan.amber`)

This case tests that `OpSGreaterThan` produces a signed comparison result on operands declared as `%uint`. The compute shader is declared directly in SPIR-V; no GLSL or HLSL source exists in CTS for this family, and Amber embeds the assembly verbatim.

#### Decorations and Resource Bindings

The shader declares one runtime array of `%uint` wrapped in a `BufferBlock` struct, used three times for SSBOs `A`, `B`, and `C`:

- `%_runtimearr_uint` has `ArrayStride 4` (one 32-bit integer per element).
- `%_struct_3` is decorated `BufferBlock` with its single member at `Offset 0`, the standard SSBO layout.
- `%gl_GlobalInvocationID` is decorated `BuiltIn GlobalInvocationId` and used as the per-invocation index into the arrays.
- Three descriptor bindings, all in `DescriptorSet 0`: `%15` → `Binding 0` (input `A`), `%16` → `Binding 1` (input `B`), `%17` → `Binding 2` (output `C`).

#### Types and Constants

- `%uint = OpTypeInt 32 0`: 32-bit unsigned integer. This is the operand type for the comparison, and the crux of the test. Although the type is unsigned, `OpSGreaterThan` must still compare the bits as signed.
- `%bool = OpTypeBool`: the result type of the comparison.
- `%uint_0` and `%uint_1`: constants used both as the `OpAccessChain` index for `.x` of `gl_GlobalInvocationID` and as the `OpSelect` outcomes (false → `0`, true → `1`).
- `LocalSize 1 1 1`: the workgroup is a single invocation; Amber dispatches `16 1 1` to cover all 16 array elements in 16 separate workgroups.

#### Control Flow

The shader is straight-line, with no branching:

1. Load `gl_GlobalInvocationID.x` into `%21`: the array index `i` for this invocation.
2. `OpAccessChain` into `A[i]` (`%22`), `OpLoad` into `%23`.
3. `OpAccessChain` into `B[i]` (`%24`), `OpLoad` into `%25`.
4. `%26 = OpSGreaterThan %bool %23 %25`: the operation under test. The result is a boolean.
5. `%27 = OpSelect %uint %26 %uint_1 %uint_0`: materialize the boolean as a `uint` (`1` when true, `0` when false) so it can be stored into the `uint`-typed `C[]`.
6. `OpStore %28 %27`: write the result to `C[i]`.
7. `OpReturn`.

#### Pass/Fail Logic

The Amber `[test]` block:

- Initializes `A[]` and `B[]` with the 16 fixed input values via `ssbo 0:0 subdata int` and `ssbo 0:1 subdata int`.
- Pre-fills `C[]` with `8`s via `ssbo 0:2 subdata int` so that any invocation the shader fails to write leaves a non-result sentinel.
- Dispatches `compute 16 1 1`, which is 16 invocations, one per array element.
- Probes `probe ssbo int 0:2 0 == <16 expected values>`. The probe reads `C[]` back as 32-bit signed integers and compares element-by-element against the expected vector. A single mismatched element fails the case.

For `uint_sgreaterthan`, the expected vector is `[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]`, which is exactly `A[i] > B[i]` evaluated with signed semantics on the input bit patterns. Indices where both operands share sign (both negative or both non-negative) agree between signed and unsigned reading, so they cannot distinguish a misreading. The diagnostic indices are the mixed-sign pairs: at index 3 (`-5` vs `2`), signed `-5 > 2` is false (expected `0`), but unsigned `0xFFFFFFFB > 0x00000002` is true. An implementation that performs unsigned comparison would write `1` at index 3 and fail the probe.

#### Source Code

The SPIR-V assembly below is the literal contents of `[compute shader spirv]` in `uint_sgreaterthan.amber`. The other three cases differ only at the `%26 = OpSGreaterThan ...` line: `uint_sgreaterthanequal.amber` substitutes `OpSGreaterThanEqual`, `uint_slessthan.amber` substitutes `OpSLessThan`, and `uint_slessthanequal.amber` substitutes `OpSLessThanEqual`. Everything else in the assembly is byte-for-byte identical across the four cases.

```text
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

## Runtime Execution and Result Checking

The CTS host side does not run any shader or check any buffer directly. The full runtime flow lives inside the Amber script and is executed by the Amber runner:

- The Amber runner parses the script, compiles the embedded SPIR-V through the Vulkan driver, and creates a Vulkan pipeline with the declared descriptor set layout.
- Three SSBOs are created and populated as `int` arrays via `ssbo 0:0 subdata int`, `ssbo 0:1 subdata int`, and `ssbo 0:2 subdata int`. The `int` keyword in Amber's `subdata` directive refers to the host-side interpretation of the bytes being written; the SSBOs are byte-identical regardless of how the shader types them.
- `compute 16 1 1` issues a single dispatch of 16 invocations. With `LocalSize 1 1 1`, that is 16 workgroups of one invocation each, so invocation `i` handles array index `i`.
- Each invocation reads `A[i]` and `B[i]`, applies the `OpS*` opcode, and writes `0` or `1` to `C[i]`.
- `probe ssbo int 0:2 0 == <expected>` reads `C[]` back to the host as 32-bit signed integers and compares all 16 elements against the expected vector. The probe fails the case on any mismatch.
- The C++ side reports the Amber case result through `cts_amber::createAmberTestCase`; CTS sees only pass or fail per leaf.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uint_sgreaterthanequal` | Signed/unsigned comparison mismatch on `OpSGreaterThanEqual`; equality handling differs from `OpSGreaterThan` |
| `uint_sgreaterthan` | Signed/unsigned comparison mismatch on `OpSGreaterThan` |
| `uint_slessthan` | Signed/unsigned comparison mismatch on `OpSLessThan` |
| `uint_slessthanequal` | Signed/unsigned comparison mismatch on `OpSLessThanEqual`; equality handling differs from `OpSLessThan` |

All four cases share one root mechanism: the implementation ignores the `S` in the opcode name and performs an unsigned comparison because the operand type is `OpTypeInt 32 0`. The equality variants also exercise the boundary where `>=` and `<=` differ from `>` and `<`, so an implementation that mishandles the equal-input case (for example by treating `>=` as `>`) would fail `uint_sgreaterthanequal` or `uint_slessthanequal` while passing their strict counterparts.

### Cause Analysis

#### Signed comparison opcode treated as unsigned

**Possible failure symptoms:** the `probe ssbo int 0:2 0 == <expected>` directive reports a mismatch on one or more array elements. The mismatch pattern is diagnostic: divergences appear at indices where one of `A[i]` or `B[i]` is negative and the other is non-negative (indices 3, 5, 6, 11, 15 in the fixed input vector). Indices where both operands share sign (both negative or both non-negative) agree between signed and unsigned reading, so they would pass even under an unsigned misreading. A failure localized to the mixed-sign indices is the fingerprint of this cause.

**Possible implementation causes:** the SPIR-V opcode name carries the signedness contract (`S` means signed, `U` means unsigned) independently of the `OpTypeInt` signedness bit. A driver or shader compiler that lowers `OpSGreaterThan` (and the other `OpS*` opcodes) to a backend unsigned comparison instruction because the operand type is `OpTypeInt 32 0` is the implementation defect that bug `b/73133282` reported. A correct implementation must look at the opcode, not the operand type, when selecting signed versus unsigned comparison at the ISA level.

#### Equality boundary mishandled on `>=` / `<=`

**Possible failure symptoms:** the case fails only on indices where `A[i] == B[i]` (indices 1, 7, 10, and 12 in the fixed input vector), and only for `uint_sgreaterthanequal` or `uint_slessthanequal`. The strict-inequality counterparts `uint_sgreaterthan` and `uint_slessthan` pass on the same indices. The symptom is a result vector where the equal-input indices read `0` instead of the expected `1`.

**Possible implementation causes:** the backend lowering for `OpSGreaterThanEqual` or `OpSLessThanEqual` may collapse the equality branch into the strict inequality, effectively evaluating `>` instead of `>=` or `<` instead of `<=`. This is a distinct lowering bug from the signed/unsigned mismatch above, and would only surface on the equal-input indices. Source-level investigation in the driver's SPIR-V-to-backend comparison lowering would be needed to confirm this cause for a specific implementation.

## Case Pruning

### Requirement-based pruning

No special Vulkan features or extensions are required by the source file. The test creation loop is compiled only for non-VulkanSC builds through [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L38-L69); on VulkanSC builds the registration function is a no-op and the four cases are absent. Beyond that, the family requires only core Vulkan compute support and a `Logical GLSL450` memory model, which any Vulkan 1.0-conformant implementation provides.

### Design-based pruning

The family is intentionally minimal. There is no parameter sweep over operand bit width, signedness of the `OpTypeInt`, vector versus scalar, or input magnitude. The four opcodes are the only behavioral axis, the input vectors are fixed across all cases, and no `OpU*` counterpart family is registered alongside this one. Bug `b/73133282` was about signed comparison, so the unsigned `OpU*` opcodes are out of scope. A commented-out `{ "foo", "Amber syntax error" }` entry in the source acts as a debug hook for fail-to-parse testing and is not registered.

## Key Takeaways

- The `S` in `OpSGreaterThan`, `OpSGreaterThanEqual`, `OpSLessThan`, and `OpSLessThanEqual` is the contract: comparison is signed regardless of whether the operand `OpTypeInt` declares signedness `0` or `1`.
- The family uses `%uint = OpTypeInt 32 0` operands on purpose. Requiring unsigned-typed operands is what makes the test catch implementations that lower the opcode based on the type's signedness bit instead of the opcode name.
- All four cases share one shader skeleton, one SSBO layout, one 16-element input vector pair, and one dispatch shape. Only the `OpS*` line and the expected probe vector change per case.
- The equality variants (`uint_sgreaterthanequal`, `uint_slessthanequal`) are not redundant with the strict variants: they cover the equality boundary where `>=` and `<=` diverge from `>` and `<`, exposing lowering bugs that drop the equality branch.
- See `## Failure Meaning` for the diagnostic patterns that distinguish a signed/unsigned misreading from an equality-boundary lowering bug.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createSignedIntCompareGroup`: top-level registration entry | [vktSpvAsmSignedIntCompareTests.cpp#L74-L79](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L79) | Creates the `signed_int_compare` test family and forwards the Amber data directory |
| `createSignedIntCompareTests`: case loop | [vktSpvAsmSignedIntCompareTests.cpp#L38-L70](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L38-L70) | Iterates the four `cases[]` entries and dispatches each to `cts_amber::createAmberTestCase` |
| `cases[]` array: opcode-to-basename mapping | [vktSpvAsmSignedIntCompareTests.cpp#L49-L56](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L49-L56) | Authoritative list of the four test case leaves and their descriptions |
| File header comment with bug reference | [vktSpvAsmSignedIntCompareTests.cpp#L20-L23](../../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L20-L23) | Records Google bug `b/73133282` as the origin of the family |
| `uint_sgreaterthan.amber`: representative Amber script | [uint_sgreaterthan.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthan.amber) | Source of the embedded SPIR-V, the input vectors, and the probe used in the walkthrough |
| `uint_sgreaterthanequal.amber` | [uint_sgreaterthanequal.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_sgreaterthanequal.amber) | Equal-or-greater variant; differs only in the `OpS*` opcode and expected probe |
| `uint_slessthan.amber` | [uint_slessthan.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthan.amber) | Strict less-than variant |
| `uint_slessthanequal.amber` | [uint_slessthanequal.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/signed_int_compare/uint_slessthanequal.amber) | Equal-or-less variant |
