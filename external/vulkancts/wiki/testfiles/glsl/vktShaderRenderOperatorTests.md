# vktShaderRenderOperatorTests.cpp

## Overview

[`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1) implements the `glsl.operator` ShaderRenderCase-based tests. The GLSL category registers this file's factory with `sr::createOperatorTests(testCtx)` under the `glsl` root in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266), and the factory returns a `ShaderOperatorTests` group named `operator` in [`createOperatorTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2988-L2990).

The file covers generated unary operators, binary operators, selected common integer/unsigned built-ins, vector relational built-ins, the ternary selection operator, and comma-sequence expressions through the registration logic in [`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1988-L2984). Generated cases combine operation-specific value types and ranges, `mediump` / `highp` precision where applicable, and vertex / fragment shader execution; boolean-only cases use the mediump path without a precision prefix as implemented in the generation loop at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2666).

## Role

Registration and implementation-heavy test file. The source declares `ShaderOperatorTests` as a `tcu::TestCaseGroup` named `operator` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1967-L1981), registers all direct operation-family children in [`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2012-L2984), and implements each generated case with `ShaderOperatorCase` and `ShaderOperatorCaseInstance` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L829-L867) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L743-L821).

## Source Code

- Primary source: [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1)
- Public factory declaration: [`vktShaderRenderOperatorTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.hpp#L23-L35)
- GLSL category registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266)
- Shared ShaderRender execution and image comparison: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)

## Registration Hierarchy

```text
glsl.operator
├── unary_operator
├── binary_operator
├── common_functions
├── float_compare
├── int_compare
├── bool_compare
├── selection
└── sequence
```

## Test Families

### unary_operator — Unary and increment/decrement operators

The `unary_operator` family is a generated `BuiltinFuncGroup` registered under the `operator` root at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2011-L2077) and then materialized as an outer `TestCaseGroup` by the common registration loop at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2597-L2603).

Its operation entries include unary `-` for float, int, and uint generic types; logical `!` for scalar bool; bitwise `~` for int and uint generic types; and prefix/postfix `++` / `--` cases split into side-effect and result forms at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2013-L2077). The postfix helpers set `isUnaryPrefix=false` through `BuiltinPostOperInfo()` and `BuiltinPostSideEffOperInfo()` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L598-L633), which changes shader-expression generation for postfix operators at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2744-L2747) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2764-L2765).

### binary_operator — Arithmetic, bitwise, shift, comparison, and logical operators

The `binary_operator` family is built as `binaryOpGroup` and pushed into the generated group list at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2079-L2513). For arithmetic, bitwise, and shift operators, the code loops over three modes: normal operation, compound-assignment side-effect, and compound-assignment result at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2081-L2127). The generated names distinguish `add`, `add_assign_effect`, and `add_assign_result`-style cases; the same pattern is used for subtraction, multiplication, division, modulus, bitwise and/or/xor, and left/right shifts at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2093-L2122).

The normal binary path includes scalar/vector forms not used by assignment cases: the comments describe `gentype <op> gentype`, `vector <op> scalar`, and normal-only `scalar <op> vector` cases at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2131-L2136), and the `if (isNormalOp)` branches add scalar-vector cases for arithmetic and bitwise operations at, for example, [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2160-L2170) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2325-L2333). Shift operations additionally vary whether the shift amount is signed or unsigned and use vector-scalar shift forms at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2393-L2455).

The same direct family also includes scalar relational operators `<`, `<=`, `>`, `>=`, equality/inequality operators for float/int/uint/bool generic types, and scalar logical `&&`, `||`, and `^^` for bool at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2460-L2511). These comparison entries are part of `binary_operator`, while `float_compare`, `int_compare`, and `bool_compare` below document GLSL vector relational built-in functions.

### common_functions — Integer and unsigned `min()`, `max()`, and `clamp()`

The `common_functions` family registers `min`, `max`, and `clamp` built-in function tests at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2515-L2541). The observed source entries cover int generic types and int vector-scalar forms, plus uint generic types and uint vector-scalar forms; no float `min` / `max` / `clamp` entries are present in this family in the inspected file.

`clamp` uses three operands with bounded lower and upper ranges: int generic entries use input ranges `[-4, 4]`, `[-2, 2]`, and `[2, 4]`, while uint generic entries use `[0, 8]`, `[2, 6]`, and `[6, 8]` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2534-L2541). Function-style shader expressions are emitted by adding `shaderFuncName(`, comma-separated inputs, and `)` in the common generation path at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2694-L2695) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2733-L2776).

### float_compare — Floating-point vector relational built-ins

The `float_compare` family registers vector built-in functions `lessThan`, `lessThanEqual`, `greaterThan`, `greaterThanEqual`, `equal`, and `notEqual` for floating-point vector inputs at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2543-L2557). The entries use `BV` boolean-vector output, float-vector inputs in `[-1, 1]`, and `PRECMASK_ALL`, so generated cases cover `mediump` and `highp` precision where corresponding vector evaluator functions exist.

### int_compare — Integer vector relational built-ins

The `int_compare` family registers the same six vector relational built-ins for signed integer vectors at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2559-L2572). The input ranges are `[-5.2, 4.9]` and `[-5.0, 5.0]`, which are converted to integer typed shader inputs by `ShaderOperatorCase::setupShaderData()` when it emits casts for int and uint inputs at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L930-L969).

### bool_compare — Boolean vector relational and reduction built-ins

The `bool_compare` family registers boolean vector `equal`, `notEqual`, `any`, `all`, and `not` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2574-L2585). These entries use `PRECMASK_NA`; the generation loop treats that as a boolean case and only emits the mediump-iterator path, without adding a precision prefix to generated names at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2610-L2612) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2665).

### selection — Ternary `?:` operator

The `selection` family is registered as a direct child named `selection` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2790-L2806). It enumerates result/operand types for float, vec2, vec3, vec4, int, ivec2, ivec3, ivec4, uint, uvec2, uvec3, uvec4, bool, bvec2, bvec3, and bvec4 at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2792-L2803).

Each generated case has three inputs: a scalar boolean condition and two operands of the selected type, and the shader expression is `res = in0 ? in1 : in2;` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2837-L2854). Boolean selection cases are limited to the mediump iterator path, while non-boolean cases use both generated precision paths at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2821-L2828).

### sequence — Comma operator with and without side effects

The `sequence` family is registered as a direct child named `sequence` and contains the immediate subgroups `no_side_effects` and `side_effects` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2859-L2867). The `s_sequenceCases[]` table contains four no-side-effect expressions and four side-effect expressions, with per-case input types, result type, and C++ evaluator callback at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2869-L2934).

The no-side-effect expressions include cases such as `in0, in2 + in1, in1 + in0`, `in0 + in2, in1 + in1`, and `in0 && in1, in0, ivec2(vec2(in0) + in2)` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2878-L2905). The side-effect expressions include `in0++`, assignment, and increment operations within comma expressions at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2907-L2934). Generated sequence cases use both precision paths and both shader stages, with the selected table row added to either `no_side_effects` or `side_effects` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2936-L2980).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct registered families | `unary_operator`, `binary_operator`, `common_functions`, `float_compare`, `int_compare`, `bool_compare`, `selection`, and `sequence` from group construction in [`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2012-L2867) |
| Shader stages | `SHADERTYPE_VERTEX` and `SHADERTYPE_FRAGMENT` are the only shader types in `s_shaderTypes[]` and are used by the generated family loops at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2587-L2588) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2666-L2670) |
| Precision paths | `PRECMASK_MEDIUMP`, `PRECMASK_HIGHP`, and `PRECMASK_ALL` are defined at [`PrecisionMask`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L426-L433); generated loops iterate from `PRECISION_MEDIUMP` to `PRECISION_LAST` and include only masked precisions at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2665) |
| Boolean precision handling | `PRECMASK_NA` marks booleans; boolean generated cases use the mediump iterator path and omit precision prefixes at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2610-L2612) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2665) |
| Scalar/vector sizes | Common generated built-in/operator families iterate input scalar sizes 1 through 4 and skip sizes without evaluator callbacks at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2624-L2655) |
| Type sets | The generated loop maps float, int, uint, and bool scalar/vector arrays declared as `s_floatTypes`, `s_intTypes`, `s_uintTypes`, and `s_boolTypes` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2589-L2595) |
| Input ranges and output scaling | Each `BuiltinFuncInfo` stores per-input ranges, result scale/bias, reference scale/bias, and precision mask at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L516-L585); the generated loop copies these values into `ShaderDataSpec` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2679-L2688) |
| Shift amount signedness | Left and right shift registration each loop over unsigned and signed shift-amount types at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2393-L2423) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2425-L2455) |
| Selection types | Selection covers scalar and vector float/int/uint/bool operand/result types listed in `s_selectionInfo[]` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2792-L2803) |
| Sequence table | Sequence uses eight table rows split by `containsSideEffects`, each with up to `MAX_INPUTS = 3` inputs at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L421-L424) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2869-L2934) |

## Support / Feature Requirements

No file-local `checkSupport()` or extension/feature gate was observed in [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1). The generated shaders explicitly use `#version 310 es` in `ShaderOperatorCase::setupShaderData()` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L878-L881), and all documented operator cases are registered through the GLSL ShaderRenderCase path under the `glsl` package at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266).

Input precision is adjusted inside shader generation rather than by a feature check: boolean inputs use mediump, integer and unsigned inputs use highp, and floating inputs use the case precision at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L883-L894). Integer and unsigned source values are formed by casting interpolated `vec4` attributes in shader source at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L930-L969).

## Verification Methods

Each `ShaderOperatorCase` constructs an `OperatorShaderEvaluator` from the C++ `ShaderEvalFunc` callback and the reference scale/bias stored in `ShaderDataSpec` at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L849-L855). `OperatorShaderEvaluator::evaluate()` calls the operation-specific callback and applies scale/bias to the active output channels at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L665-L688).

The shader under test is generated from `ShaderDataSpec`: it declares typed inputs, emits the operator/function expression from `m_shaderOp`, converts the result to `vec4`, and applies the result scale/bias before writing either vertex-varying color or fragment output at [`ShaderOperatorCase::setupShaderData()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L869-L1035). Per-input attribute transforms use the source range in each `ShaderValue` to map grid coordinates into test inputs at [`ShaderOperatorCaseInstance::ShaderOperatorCaseInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L760-L821).

The shared ShaderRender execution path renders the shader result, computes a vertex or fragment reference image using the evaluator, and compares the result and reference images at [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805). The comparison uses `compareImages()` with an error threshold argument of `0.2f`; because `m_fuzzyCompare` defaults to false for this constructor path, the observed helper uses `tcu::pixelThresholdCompare()` with an RGBA threshold of `(1, 1, 1, 1)` unless a case enables fuzzy comparison elsewhere at [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L799-L800) and [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730).

## Test Principles

- The file centralizes most operator and built-in cases in `BuiltinFuncInfo` records, so operation names, GLSL spelling, value types, input ranges, scaling, precision masks, evaluator callbacks, and operator/function classification are registered from the same data structure at [`BuiltinFuncInfo`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L516-L585).
- The common registration loop avoids unsupported scalar sizes by skipping entries with a null evaluator callback, which is why vector-only built-ins do not generate scalar cases and scalar-only logical cases do not generate vector cases at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2634-L2655).
- Assignment and side-effect cases are explicit: side-effect operators initialize `res` from `in0` before applying the operator to `res`, while result cases evaluate the operator expression directly at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2689-L2697) and [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2749-L2766).
- The generated shader and C++ reference both apply matching scale/bias values, letting integer, unsigned, boolean, and floating results be compared as rendered colors through the shared ShaderRender image-comparison path at [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1003-L1015) and [`OperatorShaderEvaluator::evaluate()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L681-L688).

## Notes / Uncertainties

- The inspected source did not show file-local Vulkan feature or extension support checks for this page's cases; support requirements beyond the shared GLSL ShaderRenderCase infrastructure are therefore not documented here as factual requirements.
- Current source code is the evidence for the documented registration and generated-case semantics.
