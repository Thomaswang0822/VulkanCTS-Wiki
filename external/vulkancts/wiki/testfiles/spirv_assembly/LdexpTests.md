## Overview

**Core question:** Does `OpExtInst Ldexp` from `GLSL.std.450` correctly compute `x * 2^e` for every registered combination of floating-point significand type and integer exponent type, including near-minimum signed exponents that can expose truncation or sign-handling errors?

- This page covers the `spirv_assembly.instruction.compute.ldexp` test family registered by [`createLdexpGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L35-L143) in [`vktSpvAsmLdexpTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp).
- All 36 test case leaves are pure Amber-dispatched cases. The C++ file maps each case name to a same-named `.amber` script and supplies its feature requirements through `cts_amber::createAmberTestCase`; the literal SPIR-V assembly, host buffers, descriptor bindings, dispatch, and `EXPECT` checks are in [`data/vulkan/amber/ldexp/`](../../../data/vulkan/amber/ldexp/). This is an Amber-backed Batch 9 page: the assembly below is manually extracted from that CTS data rather than reconstructed or generated for this document.
- Each case exercises one combination of float significand type (`float16`, `float32`, `float64`; scalar or `vec2`/`vec4`) and integer exponent type (`int8`, `int16`, `int32`, `int64`; matching scalar or vector shape), giving `3 × 3 × 4 = 36` registered cases.
- The page explains the dispatcher, the shared Amber shader/buffer/expectation pattern, the type-width feature gates, and what a failing result points to.

## Background Knowledge

- **`OpExtInst Ldexp` (GLSL.std.450).** The `Ldexp` extended instruction builds a floating-point value from a significand `x` and an integer exponent `e`, equivalent to `x * 2^e`. It is the SPIR-V / GLSL.std.450 counterpart of the GLSL `ldexp` builtin and returns a value of the same float type as `x`.
- **Amber test framework.** Each `.amber` file is a self-contained recipe that declares a SPIR-V compute shader as text, host-side buffers, descriptor bindings, a push constant, a single dispatch, and per-element `EXPECT` checks. CTS loads the file through `cts_amber::createAmberTestCase` and runs the recipe on the device; the C++ side never sees shader source.
- **`BufferBlock` decoration (legacy storage-buffer form).** The embedded SPIR-V uses `OpDecorate ... BufferBlock` with the `Uniform` storage class, the pre-SPIR-V 1.3 spelling of storage buffers, paired with the `GLSL450` memory model. SPIR-V 1.0 is sufficient for every case in this family.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ldexp
├── ldexp_f16vec2_i16vec2
├── ldexp_f16vec2_i32vec2
├── ldexp_f16vec2_i64vec2
├── ldexp_f16vec2_i8vec2
├── ldexp_f16vec4_i16vec4
├── ldexp_f16vec4_i32vec4
├── ldexp_f16vec4_i64vec4
├── ldexp_f16vec4_i8vec4
├── ldexp_f32vec2_i16vec2
├── ldexp_f32vec2_i32vec2
├── ldexp_f32vec2_i64vec2
├── ldexp_f32vec2_i8vec2
├── ldexp_f32vec4_i16vec4
├── ldexp_f32vec4_i32vec4
├── ldexp_f32vec4_i64vec4
├── ldexp_f32vec4_i8vec4
├── ldexp_f64vec2_i16vec2
├── ldexp_f64vec2_i32vec2
├── ldexp_f64vec2_i64vec2
├── ldexp_f64vec2_i8vec2
├── ldexp_f64vec4_i16vec4
├── ldexp_f64vec4_i32vec4
├── ldexp_f64vec4_i64vec4
├── ldexp_f64vec4_i8vec4
├── ldexp_float16_int16
├── ldexp_float16_int32
├── ldexp_float16_int64
├── ldexp_float16_int8
├── ldexp_float32_int16
├── ldexp_float32_int32
├── ldexp_float32_int64
├── ldexp_float32_int8
├── ldexp_float64_int16
├── ldexp_float64_int32
├── ldexp_float64_int64
└── ldexp_float64_int8
```

All 36 children are direct test case leaves of the `ldexp` test family; there are no intermediate nodes between the family and its leaves. The full registration is mirrored at [spirv-assembly.txt#L7370-L7405](../../../mustpass/main/vk-default/spirv-assembly.txt#L7370-L7405).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Float significand type | `float16`, `float32`, `float64` | Selects the SPIR-V `OpTypeFloat` width used for the significand input and result. `float16` requires `shaderFloat16`; `float64` requires `shaderFloat64`. | [caseList](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130) |
| Vector shape | scalar, `vec2`, `vec4` | Selects scalar `OpTypeFloat`/`OpTypeInt` or `OpTypeVector ... 2|4`. The exponent vector width always matches the significand vector width. | [caseList](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130) |
| Integer exponent type | `int8`, `int16`, `int32`, `int64` | Selects the signed integer width passed as the second operand to `OpExtInst Ldexp`. `int8` requires `shaderInt8`; `int16` requires `shaderInt16`; `int64` requires `shaderInt64`. | [caseList](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130) |
| Storage width features | `storageBuffer16BitAccess`, `uniformAndStorageBuffer16BitAccess`, `uniformAndStorageBuffer8BitAccess` | Required when significand or exponent data is narrower than 32 bits, so the storage buffer can hold 8- or 16-bit elements. | [caseList](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130) |
| Push constant `count` | `32`, `16`, `8` | The 64-lane compute shader applies `Ldexp` to one scalar, `vec2`, or `vec4` per active invocation. The Amber generator therefore sets `count = 32` for scalars, `16` for `vec2`, and `8` for `vec4`; every script still checks 32 scalar result components. | [generator](../../../data/vulkan/amber/ldexp/gen_amber.py#L111-L113), [representative script](../../../data/vulkan/amber/ldexp/ldexp_float32_int32.amber#L250-L252) |
| Exponent values | `1`, `0`, `-1`, `-2`, plus float-width-relevant boundary values and very negative width-dependent values | The generator selects `-14`, `-126`, and/or `-1022` only when they are representable by both the chosen integer type and relevant to the selected float width. It fills the remaining positions with values near that integer type's minimum, exposing accidental exponent truncation or sign mishandling. | [generation logic](../../../data/vulkan/amber/ldexp/gen_amber.py#L121-L152) |

## Behavior Parameters

The primary behavioral axis is the float significand type, because it controls the precision of the `Ldexp` result and the dominant feature gate. The integer exponent type and vector shape are secondary axes that change SPIR-V capabilities and the storage layout, but the per-invocation computation is always a single `OpExtInst Ldexp` over the loaded significand and exponent.

### `float16`: half-precision significand

Each case uses `OpTypeFloat 16` for `s` and `r`. `Ldexp` returns a `float16` value, so half-precision rounding and range are exercised directly. Required feature: `Float16Int8Features.shaderFloat16`. The 16-bit storage buffer features (`storageBuffer16BitAccess` and `uniformAndStorageBuffer16BitAccess`) are required because significand and result elements are 16 bits wide.

### `float32`: single-precision significand

Each case uses `OpTypeFloat 32`. This is the baseline significand width: cases whose exponent is `int32` and whose vector shape is scalar or `vec2`/`vec4` of `int32` need no optional Vulkan feature, so they run on baseline Vulkan 1.0 implementations. Other exponent widths still pull in the matching `shaderInt*` and storage-width features.

### `float64`: double-precision significand

Each case uses `OpTypeFloat 64`. Required feature: `Features.shaderFloat64`. The wider significand exercises 64-bit rounding and the `Ldexp` precision across a larger dynamic range. The 64-bit significand stride forces `ArrayStride 8` on the significand and result runtime arrays.

For every float type, the four exponent widths (`int8`, `int16`, `int32`, `int64`) and three vector shapes (scalar, `vec2`, `vec4`) are independently registered, giving `3 × 3 × 4 = 36` cases.

## Shader Analysis

This is an Amber-backed Batch 9 page. The representative assembly is literal CTS test data manually extracted from the Amber script; it is not reconstructed from the GLSL generator input, and no `shader-analyzer` or `shader-disassembler` step applies. Per the category workflow, the page presents the assembly once under `#### Source Code` and intentionally has no `#### SPIR-V` subsection.

All 36 Amber scripts use the same generated compute-shader control-flow template. Across scripts, the declared float and integer types, resulting `OpTypeVector` shapes, `OpCapability`/extension set, runtime-array `ArrayStride` values, active-operation count, generated exponent data, and expected values vary. The representative walkthrough uses the baseline case `ldexp_float32_int32`, which needs no optional feature and exposes the shared control flow and pass/fail logic most cleanly.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
spirv_assembly.instruction.compute.ldexp.ldexp_float32_int32
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ldexp_float32_int32` | Scalar `float32` significand with scalar `int32` exponent; the baseline combination requiring only the `Shader` capability. |
| `LocalSize 64 1 1` | One workgroup of 64 invocations; only invocations with `idx < count` execute the Ldexp operation. |
| `count = 32` | Push constant value; 32 of the 64 invocations perform a real Ldexp and store a result. |
| Significand buffer values | Repeated groups of `-1.0`, `0.5`, `1.25`, `2.0` so both negative and positive significands are covered across the 32 active invocations. |
| Exponent buffer values | Repeated pattern `1, 0, -1, -2, -14, -2147483643, -2147483644, -2147483645` to exercise ordinary exponents, the `float32` minimum normal exponent, and very negative exponents. |
| `EXPECT ... TOLERANCE .0001` | Each scalar result component is checked with an absolute tolerance of `0.0001`. The script writes `-0.0` for the negative-significand underflow expectations, but this numeric tolerance comparison does not distinguish `-0.0` from `0.0`. |

#### Purpose

This shader applies `OpExtInst Ldexp` to one `(significand, exponent)` pair per active invocation, writes the result to a storage buffer, and lets the Amber `EXPECT` block compare 32 result entries against precomputed reference values. The pass condition is that every computed result is within the script's absolute `0.0001` tolerance of its reference.

#### Structural Design

```mermaid
flowchart TD
    A[Host: significands, exponents,<br/>results, pc buffers] --> B[Bind buffers as<br/>set 0 binding 0/1/2 + pc]
    B --> C[Dispatch 1 1 1<br/>= 64 invocations]
    C --> D{idx < count?}
    D -- no --> E[Skip; do not write results]
    D -- yes --> F[Load significand s<br/>and exponent e]
    F --> G[r = OpExtInst Ldexp s, e]
    G --> H[Store r to results[idx]]
    H --> I[Host: EXPECT 32 entries<br/>with tolerance .0001]
    E --> I
```

#### Source Code

The SPIR-V assembly below is the literal contents of `ldexp_float32_int32.amber` between `SHADER compute compute_shader SPIRV-ASM` and `END`. It is test data, not reconstructed source, so it is shown verbatim.

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 61
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationIndex
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %idx "idx"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "count"
               OpName %_ ""
               OpName %s "s"
               OpName %SignificandBlock "SignificandBlock"
               OpMemberName %SignificandBlock 0 "significands"
               OpName %__0 ""
               OpName %e "e"
               OpName %ExponentsBlock "ExponentsBlock"
               OpMemberName %ExponentsBlock 0 "exponents"
               OpName %__1 ""
               OpName %r "r"
               OpName %ResultsBlock "ResultsBlock"
               OpMemberName %ResultsBlock 0 "results"
               OpName %__2 ""
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %SignificandBlock BufferBlock
               OpMemberDecorate %SignificandBlock 0 NonWritable
               OpMemberDecorate %SignificandBlock 0 Offset 0
               OpDecorate %__0 NonWritable
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %ExponentsBlock BufferBlock
               OpMemberDecorate %ExponentsBlock 0 NonWritable
               OpMemberDecorate %ExponentsBlock 0 Offset 0
               OpDecorate %__1 NonWritable
               OpDecorate %__1 Binding 1
               OpDecorate %__1 DescriptorSet 0
               OpDecorate %_runtimearr_float_0 ArrayStride 4
               OpDecorate %ResultsBlock BufferBlock
               OpMemberDecorate %ResultsBlock 0 Offset 0
               OpDecorate %__2 Binding 2
               OpDecorate %__2 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
%PushConstantBlock = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
          %_ = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
       %bool = OpTypeBool
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%_runtimearr_float = OpTypeRuntimeArray %float
%SignificandBlock = OpTypeStruct %_runtimearr_float
%_ptr_Uniform_SignificandBlock = OpTypePointer Uniform %SignificandBlock
        %__0 = OpVariable %_ptr_Uniform_SignificandBlock Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_ptr_Function_int = OpTypePointer Function %int
%_runtimearr_int = OpTypeRuntimeArray %int
%ExponentsBlock = OpTypeStruct %_runtimearr_int
%_ptr_Uniform_ExponentsBlock = OpTypePointer Uniform %ExponentsBlock
        %__1 = OpVariable %_ptr_Uniform_ExponentsBlock Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
%_runtimearr_float_0 = OpTypeRuntimeArray %float
%ResultsBlock = OpTypeStruct %_runtimearr_float_0
%_ptr_Uniform_ResultsBlock = OpTypePointer Uniform %ResultsBlock
        %__2 = OpVariable %_ptr_Uniform_ResultsBlock Uniform
     %v3uint = OpTypeVector %uint 3
    %uint_64 = OpConstant %uint 64
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %idx = OpVariable %_ptr_Function_uint Function
          %s = OpVariable %_ptr_Function_float Function
          %e = OpVariable %_ptr_Function_int Function
          %r = OpVariable %_ptr_Function_float Function
         %11 = OpLoad %uint %gl_LocalInvocationIndex
               OpStore %idx %11
         %12 = OpLoad %uint %idx
         %19 = OpAccessChain %_ptr_PushConstant_uint %_ %int_0
         %20 = OpLoad %uint %19
         %22 = OpULessThan %bool %12 %20
               OpSelectionMerge %24 None
               OpBranchConditional %22 %23 %24
         %23 = OpLabel
         %32 = OpLoad %uint %idx
         %34 = OpAccessChain %_ptr_Uniform_float %__0 %int_0 %32
         %35 = OpLoad %float %34
               OpStore %s %35
         %42 = OpLoad %uint %idx
         %44 = OpAccessChain %_ptr_Uniform_int %__1 %int_0 %42
         %45 = OpLoad %int %44
               OpStore %e %45
         %47 = OpLoad %float %s
         %48 = OpLoad %int %e
         %49 = OpExtInst %float %1 Ldexp %47 %48
               OpStore %r %49
         %54 = OpLoad %uint %idx
         %55 = OpLoad %float %r
         %56 = OpAccessChain %_ptr_Uniform_float %__2 %int_0 %54
               OpStore %56 %55
               OpBranch %24
         %24 = OpLabel
               OpReturn
               OpFunctionEnd

```

#### Additional Info

- **Capabilities and entry point.** The shader declares only `OpCapability Shader`; no `Float16`/`Float64`/`Int8`/`Int16`/`Int64` capability is needed because the significand is `float32` and the exponent is `int32`. The entry point is `%main` with `LocalSize 64 1 1`; `gl_WorkGroupSize` is a constant composite `(64, 1, 1)`.
- **Memory model and ext-instr import.** `OpMemoryModel Logical GLSL450` is paired with `%1 = OpExtInstImport "GLSL.std.450"`. The `Ldexp` opcode is therefore the GLSL.std.450 extended instruction, invoked as `%49 = OpExtInst %float %1 Ldexp %47 %48` with `%1` as the instruction set and `Ldexp` as the opcode.
- **Descriptor bindings.** `SignificandBlock` is bound to descriptor set `0`, binding `0`, marked `NonWritable` so it is the read-only significand input. `ExponentsBlock` is bound to set `0`, binding `1`, also `NonWritable`, and holds the integer exponents. `ResultsBlock` is bound to set `0`, binding `2`, with no `NonWritable` decoration, so it is the writable output. All three use the legacy `BufferBlock` decoration plus `Uniform` storage class.
- **Push constant.** `PushConstantBlock` wraps a single `uint count` at offset `0`. It is read once per invocation through `OpAccessChain %_ptr_PushConstant_uint %_ %int_0` and compared against `idx` to decide whether the invocation should run the Ldexp operation.
- **Built-in input.** `gl_LocalInvocationIndex` is decorated `BuiltIn LocalInvocationIndex` and stored in the function-local `idx` so the per-invocation index is reused for input and output array access.
- **Pass/fail logic.** Each active invocation reads `significands[idx]` and `exponents[idx]`, computes `Ldexp`, and stores to `results[idx]`. Inactive invocations write nothing. The Amber `EXPECT results IDX <offset> ...` checks then read back the `results` buffer at byte offsets `0, 4, 8, ..., 124` (one `float` element every 4 bytes) and compare each against a precomputed reference with absolute tolerance `0.0001`. The expected values cover ordinary results (for example, `-1.0 * 2^1 = -2.0` and `-1.0 * 2^-14 ≈ -6.103515625e-05`) and numerically zero results for the very negative exponents. Although the generated expected text uses `-0.0` for negative inputs, the tolerance oracle does not observe the zero sign.

#### Parameter Variation Summary

The other 35 cases use the same `main` control flow and four logical buffers (significands, exponents, results, push constant), with the same per-element `EXPECT` form. They also vary in:

- `OpTypeFloat` width (`16`, `32`, `64`) and the matching `OpCapability` (`Float16` or `Float64`; `32` needs none).
- `OpTypeInt` width for the exponent (`8`, `16`, `32`, `64`) and the matching `OpCapability` (`Int8`, `Int16`, `Int64`; `32` needs none).
- Whether scalar types are replaced with `OpTypeVector ... 2` or `OpTypeVector ... 4` for both significand and exponent; vector cases also change `ArrayStride` accordingly (e.g., `8` for `v2float`, `16` for `v4float`).
- The `OpCapability`, extension declarations, and storage-feature requirements reported to CTS by the dispatcher so unsupported cases are skipped rather than run on devices lacking the feature.
- The active vector count (`pc.count` = `32`, `16`, or `8`), exponent sequence, expected values, and scalar byte offsets derived from the selected type and shape.

## Runtime Execution and Result Checking

- The Amber framework, not CTS host code, owns the runtime. Each `.amber` file declares the `significands`, `exponents`, `results`, and `pc` host buffers, the compute pipeline, the descriptor-set bindings, and the dispatch dimensions.
- The compute pipeline attaches the embedded SPIR-V compute shader and binds `significands` to set `0` binding `0`, `exponents` to set `0` binding `1`, `results` to set `0` binding `2`, and `pc` as the push constant.
- The dispatch is `RUN pipeline 1 1 1`, producing one workgroup of 64 invocations. `pc.count` is `32`, `16`, or `8` for scalar, `vec2`, or `vec4` operands respectively, so every script processes 32 scalar components; the remaining invocations write nothing.
- After the dispatch, the Amber `EXPECT` block checks 32 scalar result components: offsets `0, 4, 8, ..., 124` in the representative scalar case and the matching byte layout for vector cases. Each comparison has absolute `TOLERANCE .0001`.
- The test passes only when every `EXPECT` clause succeeds. There is no host-side aggregation: each case is independent and reports its own pass/fail status.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| `significands` buffer | Amber host | Descriptor set `0` binding `0`, `NonWritable` | Read by compute shader | No | Provides the Ldexp significand `x`. |
| `exponents` buffer | Amber host | Descriptor set `0` binding `1`, `NonWritable` | Read by compute shader | No | Provides the Ldexp integer exponent `e`. |
| `results` buffer | Amber host, zero-initialized | Descriptor set `0` binding `2`, writable | Written by compute shader | Yes, via `EXPECT` | Receives `Ldexp(s, e)` per active invocation; checked entry-by-entry. |
| `pc` push constant | Amber host, value `32` | Push constant | Read by compute shader | No | Bounds the active invocation count to 32 of 64. |
| Compute pipeline | Amber host | Pipeline state | Executes SPIR-V compute shader | No | Runs the embedded SPIR-V assembly. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `float16` significand cases | Wrong `Ldexp` result for half-precision significand, or `shaderFloat16` / 16-bit storage path lowering the operation incorrectly. |
| `float32` significand cases | Wrong `Ldexp` result for single-precision significand, including failures on the no-feature baseline cases (`ldexp_float32_int32`, `ldexp_f32vec2_i32vec2`, `ldexp_f32vec4_i32vec4`). |
| `float64` significand cases | Wrong `Ldexp` result for double-precision significand, or `shaderFloat64` lowering producing wrong precision or range. |
| Any case with `int8` exponent | Wrong exponent handling when the integer is 8-bit, or `shaderInt8` / 8-bit storage path mis-extracting the exponent. |
| Any case with `int16` exponent | Wrong exponent handling when the integer is 16-bit, or `shaderInt16` / 16-bit storage path mis-extracting the exponent. |
| Any case with `int64` exponent | Wrong exponent handling when the integer is 64-bit, or `shaderInt64` path mishandling the wide exponent; large negative exponents are sensitive to sign extension. |
| Vector (`vec2` / `vec4`) cases of any float type | Per-component `Ldexp` produces wrong component, wrong swizzle, or wrong stride in the runtime array. |
| All cases include near-minimum signed-exponent probes | A result that exceeds the `0.0001` absolute tolerance for the script's generated reference can indicate bad exponent handling. Some combinations legitimately retain tiny nonzero references (for example, `float64` with `int8`); other generated references are numerical zero. The current Amber oracle does not distinguish the sign bit of zero. |

### Cause Analysis

#### Wrong `Ldexp` result for the active significand width

**Possible failure symptoms:** An `EXPECT results IDX <offset> ... EQ <reference>` clause fails within `0.0001` tolerance for one of the normal-exponent entries (e.g., `IDX 0` expected `-2.0`, `IDX 16` expected `-6.103515625e-05`). The mismatch is on a result whose exponent is `1`, `0`, `-1`, `-2`, or `-14`, where underflow is not in play.

**Possible implementation causes:** The driver's lowering of `OpExtInst Ldexp` for the declared float width produces a value outside the tolerance. For `float16`, the result may have been computed in `float32` and then narrowed, or vice versa. For `float64`, the result may have been demoted to `float32` before rounding. For `float32`, a wrong operation, wrong exponent operand, or wrong significand sign extension would all produce such a mismatch. Source-level investigation of the driver's `Ldexp` lowering is needed to pin the exact cause when the failure is reproducible.

#### Near-minimum signed-exponent behavior

**Possible failure symptoms:** An `EXPECT` clause for a near-minimum exponent fails by more than `0.0001`, or produces NaN. The representative `int32` case uses `-2147483643`, `-2147483644`, and `-2147483645`, whose references are numerical zero; other type pairs use their own near-minimum values and may retain tiny nonzero references. For example, the scalar `float64`/`int8` script expects nonzero values for exponents `-122` through `-125`. The test accepts either sign of a zero result because it uses a numeric tolerance comparison.

**Possible implementation causes:** The generator intentionally chooses values near the minimum of each integer width because truncating the high bits can turn a large negative exponent into a small or positive one. A compiler or device path that truncates, zero-extends, or otherwise misinterprets `int8`, `int16`, or `int64` exponents can therefore produce a visible mismatch. Pinning a particular lowering defect requires investigation of the implementation that fails.

#### Wrong vector component or stride handling

**Possible failure symptoms:** A `vec2` or `vec4` case fails on one or more components while the scalar counterpart passes. The mismatched components are not the first one; the first component matches the scalar reference.

**Possible implementation causes:** The shader loads the significand and exponent as vectors with `OpTypeVector %float N` and `OpTypeVector %int N`, applies `OpExtInst %vNfloat %1 Ldexp %s %e`, and stores the vector result. A driver that lowers the vector `Ldexp` to scalar operations but mishandles the component indexing, swizzle, or `ArrayStride` (e.g., `8` for `v2float`, `16` for `v4float`) can produce per-component mismatches. The runtime-array `ArrayStride` is decorated in the SPIR-V; a driver that ignores the stride when computing the access offset would store or read components from the wrong byte offset.

#### Missing or incorrectly advertised feature support

**Possible failure symptoms:** A case that should be skipped on a feature-limited device is instead run and crashes, times out, or produces wrong results. Or a device advertises the feature but its storage access path mishandles the narrower data width, so the `EXPECT` clauses on `int8` / `int16` / `float16` cases fail.

**Possible implementation causes:** The CTS dispatcher reports the per-case feature requirements to the framework, which skips unsupported cases. If a device advertises `shaderFloat16`, `shaderInt8`, `shaderInt16`, `shaderInt64`, or `shaderFloat64` but the implementation does not actually support the declared storage access path (`storageBuffer16BitAccess`, `uniformAndStorageBuffer16BitAccess`, `uniformAndStorageBuffer8BitAccess`), the shader may read or write the wrong bytes for the narrow types. Source-level investigation of the device's feature advertisement and storage lowering is needed when this pattern appears.

## Case Pruning

### Requirement-based pruning

Per-case feature requirements are listed in [`caseList`](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L45-L130) and routed through `cts_amber::createAmberTestCase`. The framework skips a case when the device lacks any advertised feature:

- `Float16Int8Features.shaderFloat16` for every `float16` significand case.
- `Float16Int8Features.shaderInt8` for every `int8` exponent case.
- `Features.shaderInt16` for every `int16` exponent case.
- `Features.shaderInt64` for every `int64` exponent case.
- `Features.shaderFloat64` for every `float64` significand case.
- `Storage16BitFeatures.storageBuffer16BitAccess` and `uniformAndStorageBuffer16BitAccess` for `float16` significand cases and `int16` exponent cases.
- `Storage8BitFeatures.uniformAndStorageBuffer8BitAccess` for `int8` exponent cases.

Three cases have empty requirement lists and run on baseline Vulkan 1.0 implementations: `ldexp_float32_int32`, `ldexp_f32vec2_i32vec2`, and `ldexp_f32vec4_i32vec4`. The whole `ldexp` test family is non-VulkanSC only.

### Design-based pruning

No design-based pruning is applied. Every combination of three float significand widths, three vector shapes (scalar, `vec2`, `vec4`), and four integer exponent widths is registered as a distinct case, giving the full `3 × 3 × 4 = 36` matrix. No redundant or excluded combinations are present.

## Key Takeaways

- The `ldexp` test family is a pure Amber dispatcher: the C++ source registers 36 case names and their feature requirements, and each case's SPIR-V, buffers, dispatch, and `EXPECT` checks live in a matching `.amber` file.
- Every case uses the same generated compute-shader control flow to load one significand and one exponent per active invocation, apply `OpExtInst Ldexp`, and store the result; declared types, capabilities/extensions, strides, active counts, input exponents, and expected values vary by case.
- The `float32`/`int32` combinations need no optional Vulkan feature and run on baseline Vulkan 1.0; every other case is gated by the matching `shaderFloat*` or `shaderInt*` feature plus the storage-width features for narrow element types.
- The `EXPECT` block checks 32 scalar result components per script with absolute `0.0001` tolerance. Near-minimum signed exponents are deliberately included to expose exponent-width truncation and signedness mistakes; depending on the float/int pair, their generated references may be numerical zero or tiny nonzero values. Although negative inputs are generated with `-0.0` expectations, this oracle does not observe zero sign.
- See `## Failure Meaning` for the failure interpretation: a failing result points to wrong `Ldexp` lowering for the active float or integer width, near-minimum exponent handling, wrong vector component or stride handling, or a feature advertisement that does not match the storage access path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createLdexpGroup` factory | [vktSpvAsmLdexpTests.cpp#L35-L143](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L35-L143) | Defines the `ldexp` test family and registers all 36 Amber cases. |
| Parent registration and Vulkan SC guard | [vktSpvAsmInstructionTests.cpp#L21437-L21449](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21437-L21449) | Adds `ldexp` below `instruction.compute` only in the `#ifndef CTS_USES_VULKANSC` block. |
| `LdexpCase` list | [vktSpvAsmLdexpTests.cpp#L39-L130](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L39-L130) | Per-case test name and feature requirements passed to `cts_amber::createAmberTestCase`. |
| Amber dispatcher call | [vktSpvAsmLdexpTests.cpp#L132-L141](../../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L132-L141) | Routes each case to its `.amber` file in the `ldexp` data subdirectory. |
| Amber generator | [gen_amber.py#L111-L167](../../../data/vulkan/amber/ldexp/gen_amber.py#L111-L167) | Derives active-operation counts, boundary and near-minimum exponents, expected values, and the final per-case `EXPECT` clauses. |
| Representative Amber script | [ldexp_float32_int32.amber](../../../data/vulkan/amber/ldexp/ldexp_float32_int32.amber) | Baseline case carrying the embedded SPIR-V assembly, host buffers, dispatch, and `EXPECT` checks analyzed in this page. |
| Amber script directory | [ldexp/](../../../data/vulkan/amber/ldexp/) | Holds all 36 `.amber` files plus generator scripts (`gen_shaders.py`, `gen_amber.py`, `gen_spv.sh`, `gen_spvasm.sh`) and the README documenting the generation pipeline. |
| Mustpass entry range | [spirv-assembly.txt#L7370-L7405](../../../mustpass/main/vk-default/spirv-assembly.txt#L7370-L7405) | Mirrors the 36 registered `dEQP-VK.spirv_assembly.instruction.compute.ldexp.*` case paths. |
