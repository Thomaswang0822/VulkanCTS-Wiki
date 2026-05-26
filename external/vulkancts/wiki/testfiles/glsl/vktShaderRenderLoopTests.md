# vktShaderRenderLoopTests.cpp

## Overview

[`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1) documents the ShaderRenderCase-based `glsl.loops` subtree. The file generates GLSL ES 310 vertex and fragment shader cases for `for`, `while`, and `do_while` loop syntax, with constant, uniform, and dynamic loop-count sources taken from the `LoopType` and `LoopCountType` name tables in [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L150-L173) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L158-L264).

## Role

Registration and implementation-heavy test file. The parent `glsl` group adds this file through [`createLoopTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1264). The local factory returns a [`ShaderLoopTests`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1513-L1527) group named `loops`, and [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1534-L1614) registers the `generic` and `special` children and their generated descendants.

## Source Code

- Primary source: [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1)
- Header declaration: [`vktShaderRenderLoopTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.hpp#L23-L35)
- Parent GLSL registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1264)
- Shared render harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633)

## Registration Hierarchy

```text
glsl.loops
├── generic
└── special
```

## Test Families

### generic — Basic loop-count and counter-type matrix

The `generic` child is created in [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1542-L1545). For every loop syntax and loop-count-source pair, the code creates a subgroup named `<loop_type>_<count_type>_iterations` using [`getLoopTypeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L158-L165), [`getLoopCountTypeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L258-L264), and the `groupName` builder at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1547-L1560).

Within each generated subgroup, the generic cases iterate over precisions from `mediump` through the last defined precision, counter data types `int` and `float`, and vertex/fragment shader stages at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1538-L1540) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1564-L1585). Each case name is built as `basic_<precision>_<data_type>_<shader_type>` before calling [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1579-L1584).

[`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L342-L560) emits a simple loop body, `res = res.yzwx + vec4(1.0)`, and subtracts the expected three iterations afterward at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L495-L528). Integer counters use `ndx++`; floating counters use thirds or uniform-provided fraction values according to the selected count source at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L450-L493).

### special — Loop-control, nesting, and control-flow patterns

The `special` child is also created directly under `loops` in [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1542-L1545). It uses the same `<loop_type>_<count_type>_iterations` subgroup naming loop as `generic` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1547-L1560), then iterates through the `LoopCase` enum and shader stages at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1591-L1610). The `no_iterations` loop case is skipped only when the selected syntax is `do_while` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1595-L1597).

The special case table contains 30 registered loop patterns, with names returned by [`getLoopCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L216-L255). The enum comments identify the intended patterns: empty bodies, unconditional and conditional exits from infinite loops, single/compound/sequence statements, zero and single iteration variants, conditional count selection, continue/break variants, pre/post increments, vector counters, 101-iteration loops, sequential loops, nested loops, tricky nested dataflow, switch fallthrough, a do-while trap, and loops placed in `if` or `else` blocks at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L178-L213).

[`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L565-L1510) has separate generation branches for `for`, `while`, and `do_while` syntax. The `for` branch emits the pattern bodies at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L675-L916), the `while` branch at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L917-L1168), and the `do_while` branch at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1169-L1432). Each branch computes `numIters`, substitutes it as `${NUM_ITERS}`, and uses [`getLoopEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L284-L300) to choose the reference evaluator at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1454-L1509).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct children | `generic` and `special` are allocated and added by [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1542-L1545). |
| Loop syntax | `for`, `while`, and `do_while` are the names for `LoopType` values at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L150-L165). |
| Loop-count source | `constant`, `uniform`, and `dynamic` are the names for `LoopCountType` values at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L167-L173) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L258-L264). |
| Generic precision | The registration loop starts at `glu::PRECISION_MEDIUMP` and stops before `glu::PRECISION_LAST` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1564-L1567). |
| Generic counter data type | Generic cases use `glu::TYPE_INT` and `glu::TYPE_FLOAT` from `s_countDataType` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1538-L1540). |
| Shader stage | Both generic and special cases use vertex and fragment stages from `s_shaderTypes` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1538-L1539), with case names built from `getShaderTypeName()` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1573-L1580) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1599-L1606). |
| Generic iteration count | Generic cases set `numLoopIters = 3`, select constant/uniform/dynamic bounds, and subtract `vec4(3)` before output at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L378-L379), [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L450-L493), and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L528-L560). |
| Special loop cases | The registered names are `empty_body`, `infinite_with_unconditional_break_first`, `infinite_with_unconditional_break_last`, `infinite_with_conditional_break`, `single_statement`, `compound_statement`, `sequence_statement`, `no_iterations`, `single_iteration`, `select_iteration_count`, `conditional_continue`, `unconditional_continue`, `only_continue`, `double_continue`, `conditional_break`, `unconditional_break`, `pre_increment`, `post_increment`, `mixed_break_continue`, `vector_counter`, `101_iterations`, `sequence`, `nested`, `nested_sequence`, `nested_tricky_dataflow_1`, `nested_tricky_dataflow_2`, `pre_fallthrough`, `post_fallthrough`, `dowhile_trap`, `ifblock`, and `elseblock` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L216-L255). |
| Special do-while exclusion | `LOOPCASE_NO_ITERATIONS` is not registered for `LOOPTYPE_DO_WHILE` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1595-L1597). |
| Uniform-backed constants | Special cases add uniform buffers for `ui_zero` through `ui_six`, add `ub_true` only for `select_iteration_count`, and add `ui_oneHundredOne` only for `101_iterations` at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L603-L638). |
| Dynamic-count input | Dynamic loop-count cases add `a_one` at vertex input location 3 and pass it to fragment cases as `v_one` at [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L358-L375) and [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L583-L600). |

## Support / Feature Requirements

No file-local feature gate or `checkSupport()` override was found in [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1). The generated shaders use `#version 310 es` in both the generic and special builders at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L351-L356) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L576-L581). Uniform data is installed through [`LoopUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L319-L338), which calls the shared harness uniform path [`ShaderRenderCaseInstance::useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L1058).

## Verification Methods

- Each loop case is a [`ShaderLoopCase`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L302-L315) derived from [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633). The case stores generated vertex and fragment shader source, and the shared harness adds them to the source collection as `vert` and `frag` at [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625).
- The shader body repeatedly transforms `res` with `res = res.yzwx + vec4(1.0)`, then subtracts the expected number of loop body executions before producing color output in generic cases at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L495-L538) and in special cases at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1434-L1449).
- Reference selection is based on the expected iteration count modulo four: [`getLoopEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L284-L300) dispatches to `evalLoop0Iters`, `evalLoop1Iters`, `evalLoop2Iters`, or `evalLoop3Iters`, whose coordinate swizzles are defined at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L267-L282).
- Generic cases always pass `numLoopIters = 3` into [`getLoopEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L378-L379) and [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L558-L560). Special cases compute `numIters` per pattern, substitute that count into the shader, and then use the same evaluator selection at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L640-L641), [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1454-L1509).

## Test Principles

- The file separates a compact cross-product of loop syntax, count source, counter precision, counter data type, and shader stage (`generic`) from named control-flow stress patterns (`special`) at [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1534-L1614).
- Constant, uniform, and dynamic count sources are reflected in the generated bounds and increments rather than in separate hand-written shaders: generic integer and float paths build the relevant expressions at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L450-L493), and special cases substitute `ITER_COUNT`, `ONE`, `TWO`, and `THREE` from either literals, uniform names, or `one*uniform` expressions at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1461-L1500).
- Vertex and fragment coverage is generated from the same builders by selecting `op` as either the vertex or fragment shader stream at [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L347-L349) and [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L569-L571).
- Correctness is expressed as rendered color matching the selected `ShaderEvalFunc`, not as API-return validation. The loop shaders normalize their result by subtracting the expected iteration count, and the evaluator checks the corresponding coordinate swizzle through the shared `ShaderRenderCase` path at [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L267-L300), [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L528-L560), [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1434-L1509), and [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L628-L633).

## Notes / Uncertainties

- No separate helper source file is used for the `loops` group; the public header only declares [`createLoopTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.hpp#L23-L35).
- The documented registration hierarchy intentionally stops at the direct children `generic` and `special`; deeper generated subgroup names and case-name patterns are described in the family and parameter sections above.
