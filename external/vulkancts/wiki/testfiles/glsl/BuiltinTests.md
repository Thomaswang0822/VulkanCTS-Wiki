## Overview

[`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59) registers the GLSL ShaderExecutor built-in test group, `glsl.builtin`. It is attached to the GLSL package by [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1276). The registration file is an aggregator: the delegated common-function, integer-function, packing, precision, and floating-point-conversion sources generate cases, check support, execute shaders, and verify results.

## Source Code

- Registration and aggregation: [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59)
- Public factory declaration: [`vktShaderBuiltinTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.hpp#L22-L35)
- Common built-ins: [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1091-L1134)
- Integer built-ins: [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1273-L1305)
- Pack/unpack built-ins: [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1494)
- Precision built-ins: [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8418-L8823)
- Floating-point conversion: [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1464)

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

`function` directly contains the three delegate groups; the precision and conversion groups are direct children of `builtin`. Generated function names and leaves are described below rather than expanded into the tree.

## Test Families

### `function`

The common group initializes `abs`, `sign`, `isnan`, `isinf`, and the float/integer bitcast families ([initialization table](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1134)). Double inputs for `isnan` and `isinf` are checked for `shaderFloat64` support ([type support](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L247-L257)).

The integer group covers unsigned carry/borrow and extended-multiply operations, bitfield operations, bit counts, and find-LSB operations ([registration table](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1282-L1305)). Cases sweep signed and unsigned scalar bases, vector lengths 1–5 (or 1–4 for Vulkan SC), and precision according to the `allPrec` setting; vec5 cases are generated only for compute shaders ([case generation](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L225-L265)).

The pack/unpack group registers the 4×8 normalized conversions, 2×16 normalized conversions, and `packHalf2x16`/`unpackHalf2x16` ([registration table](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1426-L1494)). The 4×8 cases cover all shader stages in the source table, while the 2×16 and half-precision cases are restricted to geometry and compute. Normalized pack cases sweep `mediump` through `highp` ([case setup](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1437-L1492)).

### Precision groups

`precision` uses the arithmetic, trigonometric, exponential/logarithmic, common, geometric, matrix, `frexp`, `ldexp`, and `fma` factory families ([factory list](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8421-L8511)). Each family creates compute-shader `mediump` and `highp` cases with 32-bit floating formats ([case construction](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8701)). The default sample count is 16,384 when the command-line iteration count is not positive ([registration](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8739-L8767)).

`precision_fp16_storage16b` uses the 16-bit factory and a `deFloat16` precision model. `precision_fp16_storage32b` also tests 16-bit precision but uses the regular factory set with the `storage32Bit` path ([16-bit registration](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8586-L8678), [constructors](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8797-L8823)). The distinction is storage behavior, not a claim that both groups instantiate identical case lists.

`precision_double` uses the double factory families and a 64-bit floating format with the 64-bit shader-float feature bit ([factory](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8514-L8583), [case construction](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8704-L8718)).

### `precision_fconvert`

The conversion group generates vector-length cases over E5M2, E4M3, bfloat16, float16, float32, and float64 in regular Vulkan builds; Vulkan SC restricts the list to float16, float32, and float64 ([type list](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1412)). Same-type and non-doable conversions are skipped. Eligible FP8 destinations additionally receive saturated cases, and scalar integer-to/from-float conversions are registered ([generation](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1414-L1461)). Names follow `<from>_to_<to>_size_<k>` with an optional `_sat` suffix.

## Support / Feature Requirements

| Requirement | Scope and source evidence |
|---|---|
| Shader-stage availability | Integer and packing cases call `checkSupportShader(context, m_shaderType)` ([integer](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L312), [packing](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L106-L109)). |
| Long vectors | Common, integer, and precision cases reject long-vector/vec5 use when `VK_EXT_shader_long_vector` is unavailable ([common](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L444-L463), [integer](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L329), [precision](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7736-L7745)). |
| 16-bit precision | The 16-bit precision path requires `shaderFloat16`; the storage16b path additionally requires 16-bit uniform/storage-buffer access ([feature mapping](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L129-L171), [format setup](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8735)). |
| 64-bit precision | Double precision and double-operand common/conversion cases require `shaderFloat64` ([double setup](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8704-L8718)). |
| FConvert types | `FConvertTestCase::checkSupport()` gates float64, float16, bfloat16, and FP8 operands on their corresponding Vulkan features and storage requirements ([support](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L973-L1019)). Generated shaders request the required GLSL extensions ([program setup](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L890-L970)). |

The aggregation factory itself has no local support check ([factory](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59)); unsupported cases are filtered or reported by their delegated implementations. A support failure is distinct from an executed case whose output fails verification.

## Verification Methods

- Common-function cases execute ShaderExecutor programs and compare output tuples with operation-specific exact, bit/ULP, NaN, or infinity expectations ([iteration](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L495-L563), [comparisons](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L773-L810)).
- Integer cases execute generated shaders over initialized values and invoke per-operation host `compare()` functions, failing when any value mismatches ([iteration](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L366-L430)).
- Pack/unpack cases compare shader results against host references; normalized packing applies clamping/rounding and precision-dependent tolerances ([pack reference](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L148-L232), [unpack validation](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L815-L843)).
- Precision cases generate samples, evaluate host-side reference intervals for the selected format and precision, and require shader outputs to lie within those intervals ([iteration and oracle](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7444-L7693)).
- FConvert cases run compute shaders using constructors or `saturatedConvertEXT`, read storage-buffer results back, and validate conversions with `verifyConversion()`/`validConversion()` ([execution](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1068-L1397), [conversion oracle](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L782-L845)).

A failed comparison demonstrates disagreement among the generated shader, pipeline/resources, execution and synchronization, readback, and host oracle; it does not isolate one GLSL builtin without further diagnosis.

## Test Principles

- Registration is intentionally separate from implementation: `vktShaderBuiltinTests.cpp` defines the stable hierarchy, while delegate files own case generation, support checks, and verification.
- The source does not define an unrestricted Cartesian product. Stage sets, vector lengths, precision loops, storage modes, and conversion-doability checks deliberately trim coverage.
- Precision tests use intervals derived from host floating-point models rather than requiring one exact result for every operation.
- FConvert uses storage-buffer readback to exercise conversions across available floating-point and integer types.
- This page documents inspected source behavior. It does not claim that the cases were executed on the current machine.
