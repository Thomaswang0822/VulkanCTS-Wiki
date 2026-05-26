# vktShaderBuiltinTests.cpp

## Overview

[`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L1) is the GLSL
`builtin` registration/aggregation file for ShaderExecutor-based built-in shader tests. The GLSL root adds this group
through [`createBuiltinTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1276), and the file itself constructs
`builtin`, creates a nested `function` subgroup, and delegates implementation to common-function, integer-function,
packing-function, precision, and FConvert sources in
[`createBuiltinTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59).

## Role

Registration / aggregation file. The file registers the Level-3 root and its direct children, while verification logic,
parameter generation, and feature gates live in the delegated implementation files included at
[`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L30-L34) and instantiated at
[`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L48-L57).

## Source Code

- Primary source: [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L1)
- Root header: [`vktShaderBuiltinTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.hpp#L22-L35)
- GLSL package attachment: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1276)
- Common-function delegate: [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1091-L1134)
- Integer-function delegate: [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1273-L1305)
- Packing-function delegate: [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1494)
- Precision delegate: [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8418-L8823)
- FConvert delegate: [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1464)

## Registration Hierarchy

```text
glsl.builtin
├── function
├── precision
├── precision_fp16_storage16b
├── precision_fp16_storage32b
├── precision_double
└── precision_fconvert
```

## Test Families

### function — Common, integer, and pack/unpack built-in functions

The `function` group is created explicitly as a `TestCaseGroup` named `"function"`, receives the `common`, `integer`,
and `pack_unpack` delegate groups, and is then added under `builtin` at
[`createBuiltinTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L45-L52). The displayed names of
those delegates come from `ShaderCommonFunctionTests(testCtx, "common")`,
`ShaderIntegerFunctionTests(testCtx, "integer")`, and `ShaderPackingFunctionTests(testCtx, "pack_unpack")` at
[`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1091-L1093),
[`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1273-L1276),
and [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1419).

Within `function.common`, the observed initialized families are `abs`, `sign`, `isnan`, `isinf`, `floatbitstoint`,
`floatbitstouint`, `intbitstofloat`, and `uintbitstofloat` at
[`ShaderCommonFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1134).
Within `function.integer`, the inspected registration table includes unsigned carry/borrow, multiply-extended,
bitfield, bitcount, and find-LSB operations at
[`ShaderIntegerFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1282-L1305).
Within `function.pack_unpack`, the inspected code registers `packSnorm4x8`, `unpackSnorm4x8`, `packUnorm4x8`,
`unpackUnorm4x8`, `packSnorm2x16`, `unpackSnorm2x16`, `packUnorm2x16`, `unpackUnorm2x16`, `packHalf2x16`, and
`unpackHalf2x16` cases across selected shader-stage sets at
[`ShaderPackingFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1426-L1494).

### precision — 32-bit built-in precision and range cases

The `precision` direct child is `BuiltinPrecisionTests`, constructed with group name `"precision"` and initialized by
`addBuiltinPrecisionTests(m_testCtx, *this)` at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8770-L8781).
Its factory set is created by `createBuiltinCases()`, which covers arithmetic, trigonometric, exponential/logarithmic,
common, geometric, matrix, `frexp`, `ldexp`, and `fma`-style built-ins observed in the factory list at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8421-L8511).
Each generated function group uses compute shader execution and creates `mediump` and `highp` precision cases using
32-bit-oriented `FloatFormat` definitions at
[`createFuncGroup()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8701).

### precision_fp16_storage16b — 16-bit floating-point precision with 16-bit storage requirements

The `precision_fp16_storage16b` direct child is `BuiltinPrecision16BitTests`, whose constructor sets that registered name
and whose `init()` passes `test16Bit = true` to `addBuiltinPrecisionTests()` at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8797-L8809).
For this non-`storage32Bit` path, `addBuiltinPrecisionTests()` chooses `createBuiltinCases16Bit()` and
`createFuncGroup16Bit()`, so the factories use `deFloat16` signatures and 16-bit precision context at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8586-L8678)
and [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8735).

### precision_fp16_storage32b — 16-bit floating-point precision with 32-bit storage path

The `precision_fp16_storage32b` direct child is `BuiltinPrecision16Storage32BitTests`, whose constructor sets that
registered name and whose `init()` passes both `test16Bit = true` and `storage32Bit = true` at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8811-L8823).
In this path, `addBuiltinPrecisionTests()` uses the regular `createBuiltinCases()` factory set but still creates 16-bit
precision cases through `createFuncGroup16Bit(..., storage32Bit)` at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8741-L8755),
which means the inspected code proves a 16-bit precision execution context with the `storage32` flag rather than the
same factory set as the storage16b path.

### precision_double — 64-bit floating-point precision and range cases

The `precision_double` direct child is `BuiltinPrecisionDoubleTests`, whose constructor registers that name and whose
`init()` calls `addBuiltinPrecisionDoubleTests()` at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8783-L8795).
The double factory set is built by `createBuiltinDoubleCases()`, covering the inspected subset of 64-bit arithmetic,
common, geometric, matrix, `frexp`, `ldexp`, and `fma` families at
[`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8514-L8583),
and each case uses a 64-bit `FloatFormat` plus `PRECISION_TEST_FEATURES_64BIT_SHADER_FLOAT` in
[`createFuncGroupDouble()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8704-L8718).

### precision_fconvert — Compute-shader conversion matrix

The `precision_fconvert` direct child is returned by `createPrecisionFconvertGroup(testCtx)` and added under `builtin` at
[`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L56-L57). The FConvert group
constructor names the group `"precision_fconvert"` and generates vector-length conversion cases in
[`createPrecisionFconvertGroup()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1464). For
regular Vulkan builds, the observed floating-point type list includes E5M2, E4M3, bfloat16, 16-bit, 32-bit, and 64-bit
floating types; for Vulkan SC builds it is restricted to 16-bit, 32-bit, and 64-bit floating types at
[`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1405-L1412). The generator
skips same-type conversions, skips conversions rejected by `TestParams::isConversionDoable()`, adds saturated conversion
cases only for eligible FP8 destinations, and also registers scalar int-to/from-float conversion cases at
[`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1414-L1461).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct `builtin` children | `function`, `precision`, `precision_fp16_storage16b`, `precision_fp16_storage32b`, `precision_double`, and `precision_fconvert` are added by [`createBuiltinTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L45-L57). |
| `function` nested groups | `common`, `integer`, and `pack_unpack` are added to the `function` group at [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L48-L50), with registered group names confirmed in their constructors at [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1091-L1093), [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1273-L1276), and [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1419). |
| Common-function data types | `abs` and `sign` use integer-only input, `isnan` and `isinf` use float and double input, and float/int bitcast functions use float or integer vector families at [`ShaderCommonFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1134). |
| Integer-function vector and precision sweep | Integer cases iterate signed/unsigned scalar bases, vector sizes 1..5 for non-VulkanSC or 1..4 for Vulkan SC, `mediump` through `highp` when `allPrec` is true, and only `highp` otherwise at [`addFunctionCases()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L225-L265). Vec5 integer cases are generated only for compute shader at [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L253-L260). |
| Integer-function shader stages | The inspected integer table defines vertex, fragment, compute, geometry, tessellation-control, and tessellation-evaluation bits and uses `ALL_SHADERS` for the listed functions at [`ShaderIntegerFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1282-L1305). |
| Packing-function shader stages | 4x8 pack/unpack cases use vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute stages, while 2x16 and half2x16 cases are generated for geometry and compute only at [`ShaderPackingFunctionTests::init()`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1426-L1494). |
| Packing-function precision | Pack cases with normalized floating inputs iterate `mediump` through `highp`; unpack and half2x16 cases in the inspected registration do not add a precision loop at [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1437-L1492). |
| 32-bit precision cases | `createFuncGroup()` creates `mediump` and `highp` cases for each factory using compute shader execution and the 32-bit `highp`/`mediump` formats defined at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8701). |
| 16-bit precision cases | `createFuncGroup16Bit()` uses a `deFloat16`-style float format, `PRECISION_TEST_FEATURES_16BIT_SHADER_FLOAT`, and conditionally adds `PRECISION_TEST_FEATURES_16BIT_UNIFORM_AND_STORAGE_BUFFER_ACCESS` when `storage32` is false at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8735). |
| 64-bit precision cases | `createFuncGroupDouble()` creates compute cases with the 64-bit `FloatFormat` and `PRECISION_TEST_FEATURES_64BIT_SHADER_FLOAT` at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8704-L8718). |
| Precision sample count | Precision groups use `ctx.getCommandLine().getTestIterationCount()` when positive, otherwise `defRandoms = 16384` at [`addBuiltinPrecisionTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8739-L8755) and [`addBuiltinPrecisionDoubleTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8758-L8767). |
| FConvert type matrix | Regular Vulkan builds generate over E5M2, E4M3, bfloat16, float16, float32, and float64; Vulkan SC builds generate over float16, float32, and float64 at [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1405-L1412). |
| FConvert vector lengths and names | Cases iterate `kMinVectorLength` through `kMaxVectorLength` and name cases as `<from>_to_<to>_size_<k>` with optional `_sat` at [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1414-L1441), plus int-to/from-float names at [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1445-L1461). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| This aggregation file has no local `checkSupport()` | [`createBuiltinTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59) only constructs groups and children; support gates are in delegated test cases. |
| Double types in common functions | Common `isnan`/`isinf` double inputs call `checkTypeSupport()`, which requires `shaderFloat64` for double or dvec data types at [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L247-L257), and the overrides call it at [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L831-L834) and [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L919-L923). |
| Long-vector support | Common, integer, and precision cases reject vec5/long-vector usage when `VK_EXT_shader_long_vector` support is absent in non-VulkanSC builds at [`CommonFunctionCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L444-L463), [`IntegerFunctionCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L329), and [`PrecisionCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7736-L7745). |
| Shader-stage support for integer and packing cases | Integer and packing function cases call `checkSupportShader(context, m_shaderType)` at [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L312) and [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L106-L109). |
| Precision feature bits | `areFeaturesSupported()` checks 16-bit storage feature bits, 16-bit shader float, and 64-bit shader float according to `PrecisionTestFeatureBits` at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L129-L171), and precision test instances call it before generating/executing inputs at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7444-L7457). |
| 16-bit precision storage distinction | The 16-bit precision helper always requires `shaderFloat16`; it requires uniform-and-storage-buffer 16-bit access only when `storage32` is false at [`createFuncGroup16Bit()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8735). |
| FConvert float64, float16, bfloat16, and FP8 gates | `FConvertTestCase::checkSupport()` requires `shaderFloat64` for 64-bit operands, `shaderFloat16` plus 16-bit storage features for 16-bit operands, bfloat16 support for bfloat16 operands outside Vulkan SC, and shader-float8 support for FP8 operands outside Vulkan SC at [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L973-L1019). |
| FConvert shader extensions | Generated FConvert compute shaders request 16-bit storage and explicit arithmetic types for float16, `GL_EXT_bfloat16` for bfloat16, and FP8 extensions for FP8 paths at [`FConvertTestCase::initPrograms()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L890-L970). |

## Verification Methods

- `function.common` cases execute a ShaderExecutor program, compare each output tuple with the case-specific `compare()`
  function, log mismatches, and fail on any mismatch at
  [`CommonFunctionTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L495-L563).
  Observed comparisons include exact or thresholded bit/ULP checks for bitcast-related functions and conditional NaN/Inf
  expectations according to precision at
  [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L773-L810),
  [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L856-L899),
  [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L955-L980), and
  [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1043-L1060).
- `function.integer` cases execute generated shader code for initialized integer data, invoke per-operation `compare()`
  implementations for each value, log failing inputs/outputs, and return failure when any value mismatches at
  [`IntegerFunctionTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L366-L430).
- `function.pack_unpack` cases perform per-case host reference comparisons after shader execution; for example,
  `packSnorm2x16` clamps and rounds reference components and compares packed 16-bit fields with a precision-dependent
  maximum difference at [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L148-L232), while unpack paths use helper validation and fail on any mismatched value at
  [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L815-L843).
- Precision cases generate input samples, execute the shader, compute reference intervals by evaluating the same built-in
  expression in the host-side precision model, and require shader outputs to be contained in those intervals; failures are
  logged and any nonzero error count fails the case at
  [`BuiltinPrecisionCaseTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7444-L7693).
- FConvert cases pack generated input values into host-visible storage buffers, run a compute shader that either performs a
  type constructor or `saturatedConvertEXT`, copy the output buffer back to the host, and call `verifyConversion()` /
  `validConversion()` before returning pass or fail at
  [`FConvertTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1068-L1397) and
  [`verifyConversion()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L782-L845).

## Test Principles

- The file keeps registration separate from implementation: `vktShaderBuiltinTests.cpp` creates only the `builtin` and
  `function` aggregation structure, while included delegate sources own generated cases, support checks, and pass/fail
  logic at [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L30-L57).
- The direct hierarchy separates exact/functional built-in behavior under `function` from generated precision/range
  families and conversion families under `precision*` and `precision_fconvert` at
  [`createBuiltinTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L45-L57).
- Functional built-in tests emphasize per-value host reference comparisons after ShaderExecutor execution, as shown by the
  common and integer shared iterate loops at
  [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L495-L563) and
  [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L366-L430).
- Precision tests model acceptable output as intervals derived from host-side floating-point formats and precision flags,
  not as a single exact value for every operation, at
  [`BuiltinPrecisionCaseTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7539-L7588).
- FConvert tests use compute shaders and storage-buffer readback to verify conversion matrices across scalar/vector widths
  and available floating/integer types, with unsupported type combinations filtered during registration and unsupported
  device features rejected during `checkSupport()` at
  [`createPrecisionFconvertGroup()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1414-L1461) and
  [`FConvertTestCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L973-L1019).

## Notes / Uncertainties

- Registration and behavior statements on this page are based on inspected source files.
- The parseable tree intentionally expands only one level below `glsl.builtin`; nested children such as
  `function.common` and generated precision function names are described in `## Test Families` and `## Parameter Dimensions`
  rather than added to the tree.
- The source file is an aggregation file, so broad implementation claims are limited to the inspected delegate files listed
  in `## Source Code`.
