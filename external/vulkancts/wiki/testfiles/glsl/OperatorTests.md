## Overview

**Core question:** Do the generated GLSL ES 3.10 operator expressions produce the expected rendered values in both shader stages?

- `vktShaderRenderOperatorTests.cpp` implements `glsl.operator`, a generated shader-render family for GLSL ES 3.10 operators and a small set of related built-in functions.
- The factory `createOperatorTests()` returns the `operator` test family, which the Vulkan test package registers directly under the `glsl` test category ([`vktShaderRenderOperatorTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1980-L1990), [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266)).
- Each test case generates vertex and fragment shader sources, evaluates an expression in the selected stage, converts its typed result to a color, and compares the rendered image with a C++ evaluator.
- The page describes the registered hierarchy, generated parameters, shader construction, runtime comparison, pruning, and what a failure can establish.

## Background Knowledge

- GLSL operators and built-in functions are overloaded by operand type and shape. A scalar, vector, signed integer, unsigned integer, or boolean operand can select a different legal expression and result type.
- Vertex and fragment shaders observe interpolated inputs differently. This test family therefore runs equivalent expressions in both stages and compares each stage's result through the shared shader-render path.
- A rendered-image comparison checks the complete observable path from shader compilation and execution through stage interfaces, rasterization, and result comparison. A mismatch does not identify one compiler or hardware component by itself.

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

The first six children are described by `BuiltinFuncGroup` and `BuiltinFuncInfo` records and expanded by a common registration loop. `selection` and `sequence` are registered by their own loops ([`ShaderOperatorTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1988-L2984)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Execution stage | `vertex`, `fragment` | Selects the shader stage in which the expression result is observed. | [`#L2587-L2588`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2587-L2588) |
| Precision | `mediump`, `highp` where applicable | Selects the precision-qualified float or integer variant. Boolean cases use mediump interpolation and omit a precision component from their names. | [`#L2657-L2665`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2657-L2665) |
| Scalar/vector shape | Scalar through four-component vectors where an evaluator exists | Selects operand and result width. The generator skips a shape without a C++ evaluator callback. | [`#L2624-L2655`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2624-L2655) |
| Core type | Float, signed integer, unsigned integer, boolean | Selects the GLSL data type arrays used for generated inputs and expressions. | [`#L2589-L2595`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2589-L2595) |
| Input values and normalization | Record-specific input ranges, result scale, and bias | Supplies `ShaderDataSpec` values and maps typed results into renderable color channels. | [`BuiltinFuncInfo`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L516-L585), [`#L2679-L2688`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2679-L2688) |

Generated leaves generally identify precision, input type or types, and stage. Type names are added only when an input type changes, which avoids redundant names ([`#L2727-L2731`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2727-L2731)).

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family changes the expression form or evaluation mechanism; stage, precision, type, and shape then provide the matrix around that behavior.

### `unary_operator` — unary and increment/decrement expressions

This family covers unary minus for float, signed integer, and unsigned integer generic types; logical `!` for scalar booleans; bitwise `~` for signed and unsigned generic types; and prefix and postfix `++` and `--` ([`#L2011-L2077`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2011-L2077)). Side-effect variants assign `in0` to `res` before applying the operator, while ordinary variants evaluate the expression directly. Postfix records mark the operator as non-prefix so generation places it after its operand ([`#L598-L633`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L598-L633), [`#L2689-L2766`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2689-L2766)).

### `binary_operator` — binary, compound-assignment, and scalar logical expressions

This family registers normal, compound-assignment side-effect, and compound-assignment result variants for arithmetic, modulo, bitwise, and shift operators. Names include forms such as `add`, `add_assign_effect`, and `add_assign_result` ([`#L2081-L2127`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2081-L2127)). Normal arithmetic and bitwise operators cover generic and vector-scalar forms, including scalar-vector forms that compound assignments cannot express. Shift entries vary signed and unsigned shift-count types. Scalar relational operators and `&&`, `||`, and `^^` are also included; vector relation functions belong to the compare families ([`#L2131-L2136`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2131-L2136), [`#L2393-L2511`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2393-L2511)). Input ranges avoid undefined or unhelpful arithmetic, including zero divisors in division cases and distinct signed and unsigned ranges and color scales ([`#L2242-L2275`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2242-L2275)).

### `common_functions` — integer and unsigned min, max, and clamp

This family covers `min()`, `max()`, and `clamp()` for signed and unsigned integer inputs, including generic and vector-with-scalar argument forms. This file does not register float forms ([`#L2515-L2541`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2515-L2541)). Signed `clamp` inputs use `[-4, 4]`, `[-2, 2]`, and `[2, 4]`; unsigned inputs use `[0, 8]`, `[2, 6]`, and `[6, 8]`. Function records generate `name(in0, in1, ...)`, unlike operator records, which place the operator spelling between operands ([`#L2534-L2541`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2534-L2541), [`#L2689-L2776`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2689-L2776)).

### `float_compare` — vector comparisons on float values

This family registers `lessThan`, `lessThanEqual`, `greaterThan`, `greaterThanEqual`, `equal`, and `notEqual` for float vectors. The expression result is a boolean vector ([`#L2543-L2557`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2543-L2557)).

### `int_compare` — vector comparisons on signed integers

This family registers the same six comparison functions for signed integer vectors ([`#L2559-L2572`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2559-L2572)).

### `bool_compare` — boolean comparisons and reductions

This family registers boolean-vector `equal`, `notEqual`, and `not`, plus the vector reductions `any` and `all`. These cases use `PRECMASK_NA` and therefore do not receive precision-qualified leaf names ([`#L2574-L2585`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2574-L2585)).

### `selection` — ternary selection

This family tests `in0 ? in1 : in2`, with scalar boolean `in0` and two alternatives of one selected type. It covers scalar and `vec2` through `vec4` float, signed integer, unsigned integer, and boolean types ([`#L2790-L2855`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2790-L2855)). Boolean alternatives use only the mediump interpolation path and no precision prefix. Other alternatives use each precision iterator value, with result-category-specific color scales ([`#L2821-L2851`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2821-L2851)).

### `sequence` — comma-expression ordering

This family tests comma-expression ordering in `no_side_effects` and `side_effects` subgroups. Each subgroup has four fixed expressions using scalar or vector float, signed integer, unsigned integer, and boolean values ([`#L2859-L2934`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2859-L2934)). Side-effect rows use increments and assignments such as `in0++, in1 = in0 + in2, in2 = in1`; no-side-effect rows test evaluation and final-value selection without mutations. Every row is instantiated for both precisions and both stages ([`#L2907-L2980`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2907-L2980)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.operator.binary_operator.add.highp_vec3_fragment
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `binary_operator.add` | Selects the ordinary binary `+` record, rather than either compound-assignment variant. |
| `highp` | Selects the high-precision floating-point specialization for operands and result. |
| `vec3` | Both operands and the result are three-component floating-point vectors. |
| `fragment` | The addition, result-to-color conversion, and final color write execute in the fragment shader. |
| Input ranges `[-1.0, 1.0]`, scale `1.0`, bias `0.0` | The generated values need no post-operation normalization before being written to RGB. |

#### Purpose

This specialization checks that fragment-stage `highp vec3 + highp vec3` produces the same three component values as the C++ evaluator after the generator's input swizzles and RGB result mapping.

#### Structural Design

| Phase | Exact generated behavior |
|---|---|
| Input transport | The companion vertex shader forwards attributes at locations 4 and 5 to fragment inputs `v_in0` and `v_in1` at locations 1 and 2. |
| Operand construction | `v_in0.zxy` and `v_in1.yzx` become the two `highp vec3` operands. |
| Operation under test | `res = in0 + in1;` performs component-wise vector addition. |
| Observable result | `res` is copied to `color.xyz`, alpha remains `1.0`, and `o_color` receives the result at location 0. |

#### Shader Code

```glsl
#version 310 es
/// The selected fragment case writes its observable result to the render target.
layout(location = 0) out mediump vec4 o_color;
/// High-precision carriers forwarded by the generated companion vertex shader.
layout(location = 1) in highp vec4 v_in0;
layout(location = 2) in highp vec4 v_in1;

void main()
{
	/// Select the generator-defined components for this vec3 specialization.
	highp vec3 in0 = v_in0.zxy;
	highp vec3 in1 = v_in1.yzx;
	highp vec3 res = vec3(0.0);

	/// This is the exact binary expression under test.
	res = in0 + in1;

	/// Map the three result components to RGB; alpha remains one.
	highp vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
	color.xyz = res;
	o_color = color;
}
```

#### Additional Info

- `ShaderOperatorTests::init()` constructs this exact leaf from the ordinary-add record `GT + GT`, the `highp` precision branch, scalar size 3, and `SHADERTYPE_FRAGMENT`; the registered path is also present in the default mustpass list ([`#L2083-L2148`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2083-L2148), [`#L2624-L2782`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2624-L2782), [`glsl.txt#L10915`](../../../mustpass/main/vk-default/glsl.txt#L10915)).
- `ShaderOperatorCase::setupShaderData()` emits the shown fragment source. For a fragment case it selects the `v_` prefix, applies `s_inSwizzles[0][2] = "zxy"` and `s_inSwizzles[1][2] = "yzx"`, and emits no scale/bias statement because this record uses `1.0` and `0.0` ([`#L869-L1035`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L869-L1035)).
- The runtime maps the two user inputs to vertex attributes at locations 4 and 5, renders to `VK_FORMAT_R8G8B8A8_UNORM`, and uses default shader build options; therefore the primary shader below targets baseline SPIR-V 1.0 ([`#L754-L820`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L754-L820), [`vktShaderRender.cpp#L607-L625`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625), [`vktShaderRender.cpp#L658-L683`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation record | Other records replace `+` with another operator or function syntax; compound-assignment effect cases first copy `in0` to `res` and mutate `res`. | [`#L2676-L2776`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2676-L2776) |
| Precision | `mediump` float specializations change the operand and result qualifiers; integer and unsigned carriers remain `highp` even when the operation precision is `mediump`. | [`#L883-L894`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L883-L894) |
| Type and shape | Scalar through four-component specializations change typed locals, input swizzles, output swizzles, and the result-to-color conversion; integer, unsigned, and boolean values add casts or comparisons. | [`#L930-L1001`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L930-L1001) |
| Execution stage | A vertex case evaluates the same generated operation from `a_in*` attributes and forwards only `v_color`; a fragment case forwards each `a_in*` value through `v_in*` and evaluates here. | [`#L896-L931`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L896-L931), [`#L1017-L1028`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1017-L1028) |
| Result normalization | Records with non-identity scale or bias append a component-aware `color = color * ... + ...` statement after result conversion. | [`#L1003-L1015`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1003-L1015) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 44
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %v_in0 %v_in1 %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %in0 "in0"
               OpName %v_in0 "v_in0"
               OpName %in1 "in1"
               OpName %v_in1 "v_in1"
               OpName %res "res"
               OpName %color "color"
               OpName %o_color "o_color"
               OpDecorate %v_in0 Location 1
               OpDecorate %v_in1 Location 2
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %v_in0 = OpVariable %_ptr_Input_v4float Input
      %v_in1 = OpVariable %_ptr_Input_v4float Input
    %float_0 = OpConstant %float 0
         %21 = OpConstantComposite %v3float %float_0 %float_0 %float_0
%_ptr_Function_v4float = OpTypePointer Function %v4float
    %float_1 = OpConstant %float 1
         %28 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
        %in0 = OpVariable %_ptr_Function_v3float Function
        %in1 = OpVariable %_ptr_Function_v3float Function
        %res = OpVariable %_ptr_Function_v3float Function
      %color = OpVariable %_ptr_Function_v4float Function
         %13 = OpLoad %v4float %v_in0
         %14 = OpVectorShuffle %v3float %13 %13 2 0 1
               OpStore %in0 %14
         %17 = OpLoad %v4float %v_in1
         %18 = OpVectorShuffle %v3float %17 %17 1 2 0
               OpStore %in1 %18
               OpStore %res %21
         %22 = OpLoad %v3float %in0
         %23 = OpLoad %v3float %in1
         %24 = OpFAdd %v3float %22 %23
               OpStore %res %24
               OpStore %color %28
         %29 = OpLoad %v3float %res
         %33 = OpAccessChain %_ptr_Function_float %color %uint_0
         %34 = OpCompositeExtract %float %29 0
               OpStore %33 %34
         %36 = OpAccessChain %_ptr_Function_float %color %uint_1
         %37 = OpCompositeExtract %float %29 1
               OpStore %36 %37
         %39 = OpAccessChain %_ptr_Function_float %color %uint_2
         %40 = OpCompositeExtract %float %29 2
               OpStore %39 %40
         %43 = OpLoad %v4float %color
               OpStore %o_color %43
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `ShaderOperatorCaseInstance` maps each case's source ranges onto grid attributes before rendering ([`#L743-L821`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L743-L821)).
- The shared `ShaderRenderCaseInstance` creates the render setup, compiles the vertex and fragment shader modules, renders the selected case, and copies the result image ([`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)).
- The evaluator computes a reference image for the same grid. Vertex cases use `computeVertexReference()` and fragment cases use `computeFragmentReference()` before comparison ([`#L793-L800`](../../../modules/vulkan/vktShaderRender.cpp#L793-L800)).
- `iterate()` passes `0.2f` to `compareImages()`. With the case's non-fuzzy setting, the helper uses `pixelThresholdCompare()` with an RGBA threshold of `(1, 1, 1, 1)` ([`#L2721-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).
- A matching image returns `TestStatus::pass("Result image matches reference")`; otherwise the case returns `TestStatus::fail("Image mismatch")` ([`#L799-L805`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L799-L805)). Shader compilation or pipeline setup errors can fail before this image comparison.

## Failure Meaning

A failure means that the generated case could not produce the expected result through the tested shader-render path. A compilation or setup error points to an earlier stage; an image mismatch means the rendered result differs from the C++ reference. The mismatch does not, by itself, isolate operator lowering, stage interfaces, input conversion, rasterization, or the render harness.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `unary_operator` | Unary expression generation or unary result/side-effect evaluation. |
| `binary_operator` | Binary expression generation, operand typing, or compound-assignment evaluation. |
| `common_functions` | Integer or unsigned built-in function generation or callback evaluation. |
| `float_compare` | Float-vector comparison generation or boolean-vector result handling. |
| `int_compare` | Signed-integer-vector comparison generation or boolean-vector result handling. |
| `bool_compare` | Boolean comparison, logical-not, or reduction generation. |
| `selection` | Ternary condition or selected-alternative evaluation. |
| `sequence` | Comma-expression ordering or side-effect evaluation. |

All rows also depend on shared shader compilation, pipeline setup, stage interfaces, input conversion, rendering, reference-image generation, and image comparison.

### Cause Analysis

#### Operation-specific expression or callback failures

**Possible failure symptoms:** A case in `unary_operator`, `binary_operator`, or `common_functions` fails to compile, or its rendered channels differ from the reference for the corresponding typed expression.

**Possible implementation causes:** The generated GLSL expression, operand types, casts, prefix/postfix placement, compound-assignment setup, built-in call, input range, or C++ evaluator callback may disagree. The source links show the separate record data, expression generation, and evaluator paths; a concrete cause requires inspecting the failing case and generated shader.

#### Comparison and boolean-result failures

**Possible failure symptoms:** A `float_compare`, `int_compare`, or `bool_compare` case produces a rendered boolean vector that differs from the reference image, or fails during shader compilation.

**Possible implementation causes:** The comparison or reduction expression, vector width, boolean result conversion, or `PRECMASK_NA` handling may be wrong. The failure can also come from shared shader compilation or rendering, so source-level investigation is needed to separate the expression from the common path.

#### Selection and sequencing failures

**Possible failure symptoms:** A `selection` case renders the wrong alternative, or a `sequence` case renders a final value inconsistent with comma-expression ordering or its side effects.

**Possible implementation causes:** The ternary condition, alternative typing, comma-expression order, increment, or assignment may be generated or evaluated inconsistently. The exact case path distinguishes selection from `no_side_effects` and `side_effects`, but the source does not establish a specific implementation defect without examining the failing shader and stage.

#### Shared shader-render or comparison failures

**Possible failure symptoms:** Compilation or pipeline setup fails before rendering, or many otherwise unrelated operation families show image mismatches, including stage-specific or precision-specific clusters.

**Possible implementation causes:** The common shader-render setup, stage interface, interpolated input conversion, rasterization, reference-image generation, image transfer, or threshold comparison may be involved. The shared path calls the C++ evaluator and compares the rendered image, so a failure requires case-by-case investigation rather than a fixed driver, hardware, or host attribution.

## Case Pruning

### Requirement-based pruning

No file-local `checkSupport()` override, extension gate, or Vulkan feature predicate is present. The cases emit `#version 310 es` shaders and rely on normal GLSL shader-render compilation and device support supplied by the shared framework; this page therefore does not infer extra operator-specific feature requirements ([`#L878-L881`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L878-L881)). Shared framework failures can still prevent execution before a case reaches image comparison.

### Design-based pruning

- The common generator skips scalar or vector shapes without a C++ evaluator callback. Vector-only relation functions therefore do not gain scalar leaves, and scalar logical entries do not gain vector leaves ([`#L2634-L2655`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2634-L2655)).
- Compound-assignment records omit normal-only scalar-vector forms because those forms cannot be expressed as compound assignments ([`#L2131-L2136`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2131-L2136)).
- Input ranges avoid undefined or unhelpful arithmetic, such as zero divisors, and special families use fixed rows rather than the full common matrix ([`#L2242-L2275`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2242-L2275), [`#L2859-L2934`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2859-L2934)).

## Key Takeaways

- `glsl.operator` generates unary, binary, selected common-function, vector-comparison, ternary, and comma-sequence cases from operation records and fixed tables.
- Type and width, supported precision, vertex versus fragment execution, and normal versus side-effecting behavior define the main coverage dimensions.
- Each registered record supplies the shader expression, input ranges, output normalization, and software callback used to build the rendered reference.
- An image mismatch diagnoses the complete generated-shader and rendering path. It does not uniquely identify a compiler, GPU, or host defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Value records, evaluator, case wrapper, generated shader source | [`vktShaderRenderOperatorTests.cpp#L421-L1035`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L421-L1035) | Defines operation data, C++ evaluation, case setup, and shader generation. |
| `ShaderOperatorTests::init()` | [`vktShaderRenderOperatorTests.cpp#L1988-L2984`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L1988-L2984) | Registers all operator families, operation tables, and generated leaves. |
| `createOperatorTests()` | [`vktShaderRenderOperatorTests.cpp#L2988-L2990`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2988-L2990) | Returns the public `operator` test family. |
| Factory declaration | [`vktShaderRenderOperatorTests.hpp#L23-L35`](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.hpp#L23-L35) | Declares the operator-test factory. |
| GLSL-package registration | [`vktTestPackage.cpp#L1253-L1266`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1266) | Places `operator` under the `glsl` test category. |
| Shared rendering and comparison | [`vktShaderRender.cpp#L773-L805`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Renders, builds the reference image, and returns pass or failure. |
