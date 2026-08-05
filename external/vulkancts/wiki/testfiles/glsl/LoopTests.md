## Overview

**Core question:** Do Vulkan GLSL ES 3.10 vertex and fragment shaders execute `for`, `while`, and `do-while` loops with the intended iteration count and control flow?

- [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L150-L264) implements the `glsl.loops` family registered by `createLoopTests()`.
- The family has two behavior groups: `generic` checks a common loop body across count sources, counter types, precisions, and stages; `special` checks named control-flow and nesting patterns.
- Each case generates vertex and fragment GLSL ES 310 sources, executes the loop in one selected stage, and compares rendered color against the expected coordinate swizzle.
- This page explains the registered matrix, generated shader behavior, host-side rendering path, and what a mismatch does and does not establish.

## Background Knowledge

- A `for`, `while`, and `do-while` loop differ in where initialization, the condition, and the first body execution occur. In particular, a `do-while` body executes before its condition is tested, so a zero-iteration `do-while` is not equivalent to a zero-trip `for` or `while` loop.
- Vertex-stage output reaches the fragment stage through shader interface variables. The vertex variants therefore test loop execution before rasterization, while fragment variants preserve the input coordinates and execute the loop in the fragment shader.
- The shared shader-render harness uses a callback to evaluate the expected rendered color. The loop tests encode the expected number of body executions as a modulo-four coordinate rotation, making iteration-count errors visible in the output color.

## Registration Hierarchy

```text
glsl.loops
├── generic
└── special
```

`ShaderLoopTests::init()` creates both direct children and then creates the nine syntax/count subgroups below each child (`for|while|do_while` × `constant|uniform|dynamic`). [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1264) places the group under the GLSL category.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test group | `generic`, `special` | Separates the common loop-body matrix from named control-flow patterns. | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1542-L1545) |
| Loop syntax | `for`, `while`, `do_while` | Selects the GLSL loop construct emitted around the same or specialized body. | [`getLoopTypeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L150-L165) |
| Count source | `constant`, `uniform`, `dynamic` | Supplies loop bounds as literals, uniform values, or a uniform value multiplied by a vertex input. | [`getLoopCountTypeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L167-L173), [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L358-L375) |
| Generic precision | `mediump`, and each later value before `PRECISION_LAST` | Varies the precision of the loop counter and generated local expressions. | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1564-L1567) |
| Generic counter type | `int`, `float` | Exercises integer incrementing and fractional floating-point increments. | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1538-L1540) |
| Shader stage | `vertex`, `fragment` | Places the loop in the selected stage; the other stage forwards the relevant value. | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1538-L1539) |
| Generic leaf | `basic_<precision>_<data_type>_<shader_type>` | Identifies the precision, counter type, and execution stage. | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1573-L1584) |
| Special behavior | 31 named loop cases | Covers empty bodies, exits, continues, increments, multiple/nested loops, switch fallthrough, and conditional blocks. | [`getLoopCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L216-L256) |

The expected registration count is 72 `generic` leaves: 3 syntaxes × 3 count sources × 2 counter types × 2 stages × 2 generic precisions (`mediump` and `highp`). `special` contributes 552 leaves: six `for`/`while` syntax/count combinations have 31 cases × 2 stages = 372, while the three `do_while` combinations omit `no_iterations`, giving 3 × 30 × 2 = 180, for a total of 372 + 180 = 552. Both `vk-default` and `vksc-default` mustpass lists contain exactly 624 normalized `glsl.loops` leaves (72 + 552), with the `for`/`while` subgroups containing 62 leaves each and the `do_while` subgroups containing 60 leaves each.

## Behavior Parameters

The primary behavioral axis is the registered group and its generated loop pattern. Syntax and count source are orthogonal variations of each pattern.

### `generic` — Common loop body and count handling

The generic builder initializes `res` from the coordinate input and executes `res = res.yzwx + vec4(1.0)` for each iteration. Integer counters start at zero and increment with `ndx++`; floating counters use a fractional increment. Constant, uniform, and dynamic forms select the corresponding bound and increment expressions. The shader subtracts `vec4(3)` afterward because the generic reference count is three. [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L378-L528)

### `special` — Control-flow and nesting patterns

The 31 names represent distinct loop structures, including empty and single-statement bodies, unconditional and conditional `break`, several `continue` forms, pre- and post-increment, vector counters, 101 iterations, sequential and nested loops, tricky nested data flow, switch fallthrough, a do-while trap, and loops in `if`/`else` blocks. The builder computes the actual iteration count for each pattern and specializes `${NUM_ITERS}` before selecting the evaluator. [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L565-L1510)

### Loop syntax and count-source variations

Each behavior pattern is instantiated as `for`, `while`, and `do_while`, and with constant, uniform, or dynamic count inputs. Dynamic cases read `a_one` at vertex input location 3 and, for fragment execution, forward it as `v_one`; special cases use the same value to scale their integer uniform constants. [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L583-L638) [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1461-L1483)

## Shader Analysis

The tested behavior is shader-based, but the source is generated at runtime rather than stored as a standalone shader file. Both builders emit `#version 310 es`, position/coordinate inputs, a fragment color output, and either vertex-stage varyings or fragment-stage coordinate inputs. The selected stage receives the loop body through the `op` stream; the other stage forwards the result or original coordinates. [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L342-L375) [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L565-L600)

For generic cases, the common operation is a four-component rotation plus one, followed by subtraction of the expected three iterations. Special cases use the same result normalization but vary the loop skeleton and substitute constants or uniform names. No fixed representative shader fence is published here because the exact GLSL source depends on the selected syntax, count source, precision, counter type, stage, and special case.

## Runtime Execution and Result Checking

- Each leaf is a `ShaderLoopCase`, derived from the shared [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633). The generated vertex and fragment sources are installed in the shared source collection as `vert` and `frag`. [`ShaderLoopCase`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L302-L315) [`ShaderRenderCase::init()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625)
- `LoopUniformSetup::setup()` installs the uniform values selected by the builder through `ShaderRenderCaseInstance::useUniform()`. Generic uniform/dynamic cases use the three-iteration integer or fractional value; special cases allocate the `ui_zero` through `ui_six` set and add `ub_true` or `ui_oneHundredOne` only where their pattern needs them. [`LoopUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L319-L338) [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L603-L638)
- Vertex cases execute the loop before writing `v_color`; fragment cases execute it before writing `o_color`. Dynamic count inputs are forwarded only when required by the selected count source.
- The evaluator is chosen from `numIters % 4`: zero, one, two, and three iterations map to coordinate swizzles `(0,1,2)`, `(1,2,3)`, `(2,3,0)`, and `(3,0,1)`. [`getLoopEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L267-L300)
- The shared render runner compares the rendered result with that evaluator. A mismatch means the observable rendered color was not the expected swizzle; it does not by itself localize the problem to loop lowering, interface passing, rasterization, or the host harness.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `generic` | Incorrect loop iteration, counter precision/type handling, count-source routing, stage interface, shader compilation, or rendered-result checking. |
| `special` | Incorrect control-flow, nesting, increment, fallthrough, dynamic-count handling, shader compilation, or rendered-result checking. |
| Any syntax (`for`, `while`, `do_while`) | Syntax-specific lowering or first-body/condition ordering, subject to the shared output oracle. |
| Any count source (`constant`, `uniform`, `dynamic`) | Incorrect bound delivery or arithmetic, uniform setup, input forwarding, or shader use of the selected source. |
| Any stage (`vertex`, `fragment`) | Failure in the selected stage's loop execution or in the corresponding varying/interface path. |

### Cause Analysis

#### Loop behavior and count handling

**Possible failure symptoms:** The rendered color differs from the evaluator's coordinate swizzle after the case subtracts its expected iteration count.

**Possible implementation causes:** The implementation may execute the wrong number of iterations, mishandle `break`/`continue` or loop ordering, lower integer and floating counters incorrectly, or fail to apply a constant, uniform, or dynamic bound as generated. Source inspection supports these as possible mechanisms, but the shared color oracle does not uniquely identify one.

#### Stage interface and rendering path

**Possible failure symptoms:** A vertex case can produce an incorrect color after forwarding `v_color`, while a fragment case can produce an incorrect color after forwarding coordinates and executing the loop in the fragment stage.

**Possible implementation causes:** The mismatch may arise from shader compilation, stage-interface linking, interpolation/rasterization, execution in the selected stage, or shared render-case setup. The test does not independently probe each step.

#### Support and harness failures

**Possible failure symptoms:** The case can fail before a meaningful color comparison if shader compilation, pipeline setup, or the shared rendering harness rejects the generated sources; an executed case can instead report a rendered-color mismatch.

**Possible implementation causes:** Source-generation assumptions, GLSL ES 310 support, pipeline creation, or framework behavior may be involved. This file has no local `checkSupport()` override or feature gate, so a device-specific skip or rejection must be attributed to the surrounding harness rather than invented as a loop-specific requirement.

## Case Pruning

### Requirement-based pruning

No file-local feature predicate or explicit case-level support filter is present. The generated cases use GLSL ES 310 and rely on the common shader-render framework and the device's normal support for the selected graphics stage.

### Design-based pruning

The `no_iterations` pattern is intentionally not registered for `do_while`, because the generated construct executes its body before testing the condition. Generic cases use a fixed three-iteration body and do not duplicate the named special patterns. The commented `multi_declaration` enum entry is not registered. [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1591-L1597) [`getLoopCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L245-L253)

## Key Takeaways

- The family tests both ordinary loop syntax and control-flow structures that are easy for shader compilers to lower incorrectly.
- The generic matrix varies count source, counter type, precision, and execution stage without changing the core loop body; special cases vary the control-flow shape itself.
- Expected colors encode the actual iteration count modulo four, so a pass checks the generated loop's observable effect through the selected shader stage and render path.
- The 624-leaf registration is present in both `vk-default` and `vksc-default` mustpass lists; the only intentional matrix reduction is the missing `special.*.do_while...no_iterations_*` cases.
- A color mismatch is diagnostic evidence for the complete generated-shader/render path, not proof of a particular compiler, hardware, interface, or rasterization defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Loop type/count and special-case names | [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L150-L264) | Defines exact syntax, count-source, and behavior identifiers. |
| Reference evaluators | [`vktShaderRenderLoopTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L267-L300) | Maps iteration count modulo four to expected coordinate swizzles. |
| Generic shader builder | [`createGenericLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L342-L563) | Generates the common loop-body matrix and stage interfaces. |
| Special shader builder | [`createSpecialLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L565-L1510) | Generates named control-flow patterns and computes expected counts. |
| Registration | [`ShaderLoopTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1534-L1614) | Builds the two direct children and all generated leaves. |
| Public factory | [`createLoopTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1618-L1621) | Returns the `glsl.loops` test group. |
| Parent category | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1264) | Adds the group to the GLSL test category. |
| Shared render harness | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633) | Supplies shader installation and rendered-result execution. |
| Uniform installation | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L1058) | Shows how generated uniform values reach the case instance. |
| Vulkan default coverage | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L8101-L8724) | Contains the 624 `dEQP-VK.glsl.loops` leaves. |
| Vulkan SC coverage | [`glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L7180-L7803) | Contains the 624 `dEQP-VKSC.glsl.loops` leaves. |
| Header declaration | [`vktShaderRenderLoopTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.hpp#L23-L35) | Declares the public loop-test factory. |
