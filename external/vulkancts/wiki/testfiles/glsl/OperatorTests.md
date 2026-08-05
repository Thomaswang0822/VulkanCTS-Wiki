## Overview

`vktShaderRenderOperatorTests.cpp` implements `glsl.operator`, a generated shader-render family for GLSL ES 3.10 operators and a small set of closely related built-in functions. The factory `createOperatorTests()` returns the `operator` group, which the Vulkan test package adds directly under `glsl` ([`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1980-L1990), [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266)).

Each leaf generates a vertex/fragment shader pair, executes the expression in one selected stage, converts its typed result to a color, and compares that color with a C++ evaluator's result. This is an observable semantic test of generated shader execution and the shared rendering path; it is not a direct SPIR-V inspection test.

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

The first six children are described by `BuiltinFuncGroup`/`BuiltinFuncInfo` records and expanded by a common registration loop. `selection` and `sequence` are registered by their own loops ([`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1988-L2984)).

## Test Matrix

| Dimension | Registered behavior |
|---|---|
| Execution stage | `vertex` and `fragment` for every generated family ([`#L2587-L2588`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2587-L2588)). |
| Precision | Float and applicable integer cases use their record's `mediump`/`highp` mask. Boolean cases use mediump interpolation but omit a precision component from their names ([`#L2657-L2665`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2665)). |
| Scalar/vector shape | The common loop attempts scalar through four-component vectors, then skips a shape with no evaluator callback ([`#L2624-L2655`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2624-L2655)). |
| Core types | Float, signed integer, unsigned integer, and boolean scalar/vector type arrays drive generated data types ([`#L2589-L2595`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2589-L2595)). |
| Input values | Every record supplies typed input ranges and result/reference scale and bias; these become `ShaderDataSpec` values ([`BuiltinFuncInfo`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L516-L585), [`#L2679-L2688`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2679-L2688)). |

Generated leaves generally identify precision (except boolean cases), input type or types, and stage. Type names are added only when an input type changes, avoiding redundant names ([`#L2727-L2731`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2727-L2731)).

## Behavior Groups

### `unary_operator`

This group covers unary minus for float/int/uint generic types, logical `!` for scalar bool, and bitwise `~` for signed/unsigned generic types. It also tests prefix and postfix `++`/`--` as both observable side effects and expression results ([`#L2011-L2077`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2011-L2077)).

The distinction is material: side-effect variants first assign `in0` to `res` and apply the operator to `res`, while ordinary result variants evaluate the expression itself. Postfix record helpers mark the operator as non-prefix, causing generation to append the operator after its operand ([`#L598-L633`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L598-L633), [`#L2689-L2766`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2689-L2766)).

### `binary_operator`

The binary group registers normal, compound-assignment side-effect, and compound-assignment result variants for arithmetic, modulo, bitwise, and shift operators. Its naming pattern includes forms such as `add`, `add_assign_effect`, and `add_assign_result` ([`#L2081-L2127`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2081-L2127)).

Normal arithmetic/bitwise operators cover `gentype op gentype` and vector-scalar forms; they additionally cover scalar-vector forms, which compound assignments cannot express ([`#L2131-L2136`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2131-L2136)). Shift entries vary signed and unsigned shift-count types. The group also contains scalar `<`, `<=`, `>`, `>=`, `==`, `!=`, `&&`, `||`, and `^^` cases; vector relation functions are instead in the compare groups ([`#L2393-L2511`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2393-L2511)).

Input ranges deliberately avoid undefined or unhelpful arithmetic. For example, division entries use nonzero divisors, and signed/unsigned precision variants use different ranges and color scaling ([`#L2242-L2275`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2242-L2275)).

### `common_functions`

`common_functions` covers integer and unsigned `min()`, `max()`, and `clamp()`, including generic and vector-with-scalar argument forms. It does not register float forms in this file ([`#L2515-L2541`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2515-L2541)).

For `clamp`, signed inputs use ranges `[-4, 4]`, `[-2, 2]`, and `[2, 4]`; unsigned inputs use `[0, 8]`, `[2, 6]`, and `[6, 8]`. Function records generate `name(in0, in1, ...)`, unlike operator records, which place operator spelling between operands ([`#L2534-L2541`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2534-L2541), [`#L2689-L2776`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2689-L2776)).

### Vector comparison groups

- **`float_compare`** registers `lessThan`, `lessThanEqual`, `greaterThan`, `greaterThanEqual`, `equal`, and `notEqual` for float vectors. Outputs are boolean vectors ([`#L2543-L2557`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2543-L2557)).
- **`int_compare`** registers the same six functions for signed integer vectors ([`#L2559-L2572`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2559-L2572)).
- **`bool_compare`** registers boolean-vector `equal`, `notEqual`, `not`, plus the vector reductions `any` and `all`. These are `PRECMASK_NA` boolean cases rather than precision-qualified leaves ([`#L2574-L2585`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2574-L2585)).

### `selection`

`selection` tests the ternary expression `in0 ? in1 : in2`, where `in0` is scalar bool and the two alternatives share one selected type. The matrix includes scalar and `vec2`–`vec4` float, int, uint, and bool types ([`#L2790-L2855`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2790-L2855)).

Boolean alternatives generate only the mediump interpolation path and no precision prefix. Other alternatives are generated for each precision iterator value; their color scales differ by result category so typed results can be rendered and compared ([`#L2821-L2851`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2821-L2851)).

### `sequence`

`sequence` tests comma-expression ordering in `no_side_effects` and `side_effects` subgroups. Each has four fixed expressions, mixing scalar/vector float, int, uint, and bool values ([`#L2859-L2934`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2859-L2934)).

The side-effect rows use increments and assignments within the comma expression—for example `in0++, in1 = in0 + in2, in2 = in1`—whereas the no-side-effect rows test evaluation and final-value selection without mutations. Every row is instantiated for both precisions and both stages ([`#L2907-L2980`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2907-L2980)).

## Shader Generation and Oracle

`ShaderOperatorCase::setupShaderData()` emits GLSL ES 3.10 sources, declares typed inputs, emits `m_shaderOp`, converts the typed result to `vec4`, and applies result scale/bias before writing the selected-stage result ([`ShaderOperatorCase::setupShaderData()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L869-L1035)). Booleans use mediump declarations, integers and uints use highp declarations, and float declarations use the selected case precision ([`#L878-L894`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L878-L894)). Integer and unsigned inputs are derived by casts from interpolated `vec4` attributes ([`#L930-L969`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L930-L969)).

The matching `OperatorShaderEvaluator` invokes the record's C++ evaluation callback and applies the reference scale/bias to active output channels ([`#L665-L688`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L665-L688)). `ShaderOperatorCaseInstance` maps the case's source ranges onto grid attributes before rendering ([`#L743-L821`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L743-L821)).

The shared `ShaderRenderCaseInstance` renders the shader, builds vertex- or fragment-stage reference images, and compares them. This path passes `0.2f` as its comparison error threshold; with this case's default non-fuzzy setting, the helper uses `pixelThresholdCompare()` and an RGBA threshold of `(1, 1, 1, 1)` ([`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

## Failure Meaning

A failure can occur during shader compilation/pipeline setup or as a rendered-image mismatch. A post-render mismatch establishes that the generated expression's observable color differs from its C++ oracle, but it does not alone isolate the cause to operator lowering, stage interfaces, input conversion, rasterization, or the render harness.

Useful case-path clues include:

- `*_vertex` versus `*_fragment`: the selected execution stage and its handoff path.
- `mediump_*` versus `highp_*`: the generated precision-qualified variant.
- `*_assign_effect` versus `*_assign_result`: mutation semantics versus expression-result semantics.
- scalar/vector type portions: overload resolution, scalar-vector promotion, or vector-width handling.
- `sequence.side_effects`: sequencing and mutation ordering rather than a pure final-value expression.

## Case Pruning and Support

The common generator intentionally omits type widths that have no C++ evaluator callback. Consequently, vector-only relation functions do not gain scalar leaves, and scalar logical entries do not gain vector leaves ([`#L2634-L2655`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2634-L2655)). Compound-assignment records also omit normal-only scalar-vector forms by design ([`#L2131-L2136`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2131-L2136)).

No file-local `checkSupport()` override, extension gate, or Vulkan feature predicate is present. These tests emit `#version 310 es` shaders and rely on normal GLSL shader-render compilation and device support provided by the shared framework; this page therefore does not infer extra operator-specific feature requirements ([`#L878-L881`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L878-L881)).

## Key Takeaways

- `glsl.operator` centrally generates unary, binary, selected common-function, vector-relation, ternary, and comma-sequence tests from operation records and fixed tables.
- Its primary coverage axes are type/width, supported precision, vertex versus fragment execution, and—in applicable groups—normal versus side-effecting operator behavior.
- The same registered record supplies shader expression construction, input ranges, output normalization, and a software callback, keeping the rendered oracle aligned with the intended operation.
- A result mismatch diagnoses the complete generated-shader and rendering pipeline, not a uniquely identified compiler defect.

## Source Reference Appendix

| Source | Purpose |
|---|---|
| [`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L421-L1035) | Value records, evaluator, case wrapper, and generated shader source. |
| [`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1988-L2984) | All groups, operation tables, and generated leaves. |
| [`createOperatorTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2988-L2990) | Public factory returning `operator`. |
| [`vktShaderRenderOperatorTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.hpp#L23-L35) | Factory declaration. |
| [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266) | GLSL-package registration. |
| [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Shared rendering, reference-image generation, and comparison. |
