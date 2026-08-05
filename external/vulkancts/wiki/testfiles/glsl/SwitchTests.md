## Overview

`vktShaderRenderSwitchTests.cpp` implements `glsl.switch`, a shader-render family for GLSL ES 3.10 `switch` statements. It generates vertex and fragment variants of 21 switch-body patterns, then checks their rendered color against a CPU evaluator. The patterns cover literal, uniform, and coordinate-derived selectors; labels written as constant expressions; `default` placement or omission; fall-through; local scope; and switches combined with `if`, loops, and another switch.

The group is registered below `glsl` by [`createSwitchTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270). The factory creates a `ShaderSwitchTests` group named `switch` ([`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L182-L205), [`#L502-L505`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L505)).

## Registration Hierarchy

```text
glsl.switch
```

The displayed names are behavior families rather than intermediate CTS groups: all leaves are added directly to `glsl.switch`. For a normal family, the leaf grammar is:

```text
<family>_<selector_type>_<stage>
```

`selector_type` is `static`, `uniform`, or `dynamic`; `stage` is `vertex` or `fragment`. [`ShaderSwitchTests::makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222)

There are 122 leaves: 19 families × 3 selector types × 2 stages = 114, plus four leaves each for `default_only` and `empty_case_default`. Those two families intentionally omit dynamic selectors. The Vulkan and Vulkan SC default mustpass lists each contain 122 `glsl.switch` leaves ([Vulkan](../../../mustpass/main/vk-default/glsl.txt#L14913-L15034), [Vulkan SC](../../../mustpass/main/vksc-default/glsl.txt#L13851-L13972)).

## Parameters and Generated Shaders

| Dimension | Values | Effect |
|---|---|---|
| Selector source | `static`, `uniform`, `dynamic` | Substitutes `${CONDITION}` with `2`, `ui_two`, or `int(floor(coords.z*1.5 + 2.0))`. |
| Execution stage | `vertex`, `fragment` | Places the generated switch body in the selected shader stage. |
| Behavior family | 21 named templates | Changes the switch layout and/or surrounding control flow. |
| Uniform data | `ui_two = 2` | Used only by `uniform` variants through a `std140`, set 0, binding 0 block. |

[`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L111-L180) emits `#version 310 es` vertex and fragment shaders. Vertex cases evaluate the switch from `a_coords`, write `res` to `v_color`, and have the fragment shader forward it. Fragment cases forward `a_coords` as `v_coords` and evaluate the switch in the fragment shader. Uniform cases declare `ui_two`; [`setUniforms()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L47) installs the shared `UI_TWO` value.

The common switch mapping is coordinate swizzles: selector values 0, 1, 2, and 3 correspond to `xyz`, `wzy`, `yzw`, and `zyx` respectively ([`ShaderSwitchTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L239)).

## Behavior Families

### Basic syntax and labels

- `basic` uses four ordinary `case` labels and explicit `break`s.
- `const_expr_in_label` uses `int(0.0)`, `2-1`, `3&(1<<1)`, and `t+1` as labels.
- `default_label` handles the selected value through a final `default`; `default_not_last` places `default` between ordinary labels.
- `no_default_label` initializes `res` before the switch, then deliberately has no matching `case 2` and no `default`.
- `default_only` contains only a default label. `empty_case_default` leaves `case 2` empty so it falls into default. Both skip dynamic cases. [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L241-L295)

### Fall-through and local scope

- `fall_through` and `fall_through_default` modify `coords` in `case 2` and rely on execution continuing into a later case or `default`.
- `conditional_fall_through` conditionally breaks after reaching a shared body; `conditional_fall_through_2` also changes a local selector before that decision.
- `scope` wraps `case 2` in braces, declares a local vector, assigns it to `res`, and breaks inside the scoped block. [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L297-L361)

### Nesting combinations

`switch_in_if`, `switch_in_for_loop`, `switch_in_while_loop`, and `switch_in_do_while_loop` put a switch inside the named construct. The loop variants switch on their loop index and overwrite `res` on successive iterations.

`if_in_switch`, `for_loop_in_switch`, `while_loop_in_switch`, and `do_while_loop_in_switch` put the named construct inside an outer switch. The loop-in-switch cases share `case 1` and `case 2`, start from `coords.yzw`, and repeatedly reverse the three components. `switch_in_switch` performs an inner switch on `${CONDITION} - 1` from shared outer cases. [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L363-L497)

## Runtime Execution and Result Checking

Each leaf is a `ShaderSwitchCase`, derived from the shared `ShaderRenderCase` framework ([`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L51-L70), [`vktShaderRender.hpp`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L360-L392)). The case supplies generated GLSL, an evaluator, and—only for uniform variants—a uniform setup callback.

Static and uniform evaluators expect `coords.yzw`, because their selector is always 2. The dynamic evaluator applies the same floor expression as the generated shader and maps values 0–3 to the corresponding swizzles; any other value maps to `xxx`. [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L109)

The shared runner renders a quad grid, produces a CPU reference image from the evaluator, and compares result and reference with error threshold `0.2f` ([`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)). This `ShaderRenderCase` path uses fuzzy comparison ([`ShaderRenderCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

## Support and Failure Interpretation

The switch file has no switch-specific `checkSupport()` override or feature guard. It relies on the normal shared shader-render setup and GLSL ES 3.10 shader compilation path. `glsl.switch` is registered unconditionally in the GLSL package for both Vulkan and Vulkan SC builds.

A failed leaf establishes that the generated shader/render path produced a different observable color than its evaluator. Its name narrows the behavior under test—for example, selector delivery, default/fall-through semantics, lexical scope, stage placement, or a particular nesting shape—but does not independently prove a compiler, interface, rasterization, uniform-binding, or harness defect.

## Source Reference Appendix

| Entry point | Why it matters |
|---|---|
| [`vktShaderRenderSwitchTests.cpp#L44-L180`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L180) | Uniform setup, reference evaluators, and generated shader construction. |
| [`vktShaderRenderSwitchTests.cpp#L205-L222`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222) | Leaf naming and selector/stage matrix generation. |
| [`vktShaderRenderSwitchTests.cpp#L224-L498`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L498) | All 21 switch-body templates. |
| [`vktShaderRenderSwitchTests.hpp#L30-L36`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.hpp#L30-L36) | Public factory declaration. |
| [`vktTestPackage.cpp#L1267-L1270`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270) | GLSL-package registration. |
| [`vktShaderRender.cpp#L773-L805`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Shared render/reference comparison. |
| [`vk-default/glsl.txt#L14913-L15034`](../../../mustpass/main/vk-default/glsl.txt#L14913-L15034) | Vulkan default mustpass coverage. |
| [`vksc-default/glsl.txt#L13851-L13972`](../../../mustpass/main/vksc-default/glsl.txt#L13851-L13972) | Vulkan SC default mustpass coverage. |
