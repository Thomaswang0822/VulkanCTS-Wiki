# vktShaderRenderSwitchTests.cpp

## Overview

[`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L1) registers and implements the `glsl.switch` shader-render tests. The file documents GLSL `switch` selector forms, default-label placement, missing-default behavior, fall-through, scoped case blocks, switches nested in `if`/loop constructs, control-flow constructs nested in switch cases, and nested switches, as described by the source-file comment at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L21-L30) and the registered switch-body templates in [`ShaderSwitchTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L498).

## Role

Registration and implementation file. The Vulkan GLSL package adds this group with [`sr::createSwitchTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270), the factory returns a [`ShaderSwitchTests`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L505), and that group is constructed with the registered name `switch` at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L182-L198). Each child case is a [`ShaderSwitchCase`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L51-L70) derived from the shared [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L360-L392) framework.

## Source Code

- Primary source: [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L1)
- Header: [`vktShaderRenderSwitchTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.hpp#L30-L36)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270)
- Shared shader-render harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) and [`vktShaderRender.hpp`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L360-L392)

## Registration Hierarchy

```text
glsl.switch
├── basic_static_vertex
├── basic_static_fragment
├── basic_uniform_vertex
├── basic_uniform_fragment
├── basic_dynamic_vertex
├── basic_dynamic_fragment
├── const_expr_in_label_static_vertex
├── const_expr_in_label_static_fragment
├── const_expr_in_label_uniform_vertex
├── const_expr_in_label_uniform_fragment
├── const_expr_in_label_dynamic_vertex
├── const_expr_in_label_dynamic_fragment
├── default_label_static_vertex
├── default_label_static_fragment
├── default_label_uniform_vertex
├── default_label_uniform_fragment
├── default_label_dynamic_vertex
├── default_label_dynamic_fragment
├── default_not_last_static_vertex
├── default_not_last_static_fragment
├── default_not_last_uniform_vertex
├── default_not_last_uniform_fragment
├── default_not_last_dynamic_vertex
├── default_not_last_dynamic_fragment
├── no_default_label_static_vertex
├── no_default_label_static_fragment
├── no_default_label_uniform_vertex
├── no_default_label_uniform_fragment
├── no_default_label_dynamic_vertex
├── no_default_label_dynamic_fragment
├── default_only_static_vertex
├── default_only_static_fragment
├── default_only_uniform_vertex
├── default_only_uniform_fragment
├── empty_case_default_static_vertex
├── empty_case_default_static_fragment
├── empty_case_default_uniform_vertex
├── empty_case_default_uniform_fragment
├── fall_through_static_vertex
├── fall_through_static_fragment
├── fall_through_uniform_vertex
├── fall_through_uniform_fragment
├── fall_through_dynamic_vertex
├── fall_through_dynamic_fragment
├── fall_through_default_static_vertex
├── fall_through_default_static_fragment
├── fall_through_default_uniform_vertex
├── fall_through_default_uniform_fragment
├── fall_through_default_dynamic_vertex
├── fall_through_default_dynamic_fragment
├── conditional_fall_through_static_vertex
├── conditional_fall_through_static_fragment
├── conditional_fall_through_uniform_vertex
├── conditional_fall_through_uniform_fragment
├── conditional_fall_through_dynamic_vertex
├── conditional_fall_through_dynamic_fragment
├── conditional_fall_through_2_static_vertex
├── conditional_fall_through_2_static_fragment
├── conditional_fall_through_2_uniform_vertex
├── conditional_fall_through_2_uniform_fragment
├── conditional_fall_through_2_dynamic_vertex
├── conditional_fall_through_2_dynamic_fragment
├── scope_static_vertex
├── scope_static_fragment
├── scope_uniform_vertex
├── scope_uniform_fragment
├── scope_dynamic_vertex
├── scope_dynamic_fragment
├── switch_in_if_static_vertex
├── switch_in_if_static_fragment
├── switch_in_if_uniform_vertex
├── switch_in_if_uniform_fragment
├── switch_in_if_dynamic_vertex
├── switch_in_if_dynamic_fragment
├── switch_in_for_loop_static_vertex
├── switch_in_for_loop_static_fragment
├── switch_in_for_loop_uniform_vertex
├── switch_in_for_loop_uniform_fragment
├── switch_in_for_loop_dynamic_vertex
├── switch_in_for_loop_dynamic_fragment
├── switch_in_while_loop_static_vertex
├── switch_in_while_loop_static_fragment
├── switch_in_while_loop_uniform_vertex
├── switch_in_while_loop_uniform_fragment
├── switch_in_while_loop_dynamic_vertex
├── switch_in_while_loop_dynamic_fragment
├── switch_in_do_while_loop_static_vertex
├── switch_in_do_while_loop_static_fragment
├── switch_in_do_while_loop_uniform_vertex
├── switch_in_do_while_loop_uniform_fragment
├── switch_in_do_while_loop_dynamic_vertex
├── switch_in_do_while_loop_dynamic_fragment
├── if_in_switch_static_vertex
├── if_in_switch_static_fragment
├── if_in_switch_uniform_vertex
├── if_in_switch_uniform_fragment
├── if_in_switch_dynamic_vertex
├── if_in_switch_dynamic_fragment
├── for_loop_in_switch_static_vertex
├── for_loop_in_switch_static_fragment
├── for_loop_in_switch_uniform_vertex
├── for_loop_in_switch_uniform_fragment
├── for_loop_in_switch_dynamic_vertex
├── for_loop_in_switch_dynamic_fragment
├── while_loop_in_switch_static_vertex
├── while_loop_in_switch_static_fragment
├── while_loop_in_switch_uniform_vertex
├── while_loop_in_switch_uniform_fragment
├── while_loop_in_switch_dynamic_vertex
├── while_loop_in_switch_dynamic_fragment
├── do_while_loop_in_switch_static_vertex
├── do_while_loop_in_switch_static_fragment
├── do_while_loop_in_switch_uniform_vertex
├── do_while_loop_in_switch_uniform_fragment
├── do_while_loop_in_switch_dynamic_vertex
├── do_while_loop_in_switch_dynamic_fragment
├── switch_in_switch_static_vertex
├── switch_in_switch_static_fragment
├── switch_in_switch_uniform_vertex
├── switch_in_switch_uniform_fragment
├── switch_in_switch_dynamic_vertex
└── switch_in_switch_dynamic_fragment
```

## Test Families

### Common case generator

[`ShaderSwitchTests::makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222) creates the direct children listed above. For each switch-body family, it combines the family name with `static`, `uniform`, or `dynamic` from `switchTypeNames[]` and with `vertex` and `fragment` stage suffixes, then calls [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L111-L180). The `default_only` and `empty_case_default` families pass `skipDynamicType = true`, so they register only static and uniform vertex/fragment cases at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L278-L295).

### basic — Direct switch selection

The `basic_*` cases register a switch with cases `0`, `1`, `2`, and `3`, each assigning a distinct coordinate swizzle and breaking explicitly at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L232-L239).

### const_expr_in_label — Constant-expression labels

The `const_expr_in_label_*` cases use labels written as constant expressions, including `int(0.0)`, `2-1`, `3&(1<<1)`, and `t+1`, to select the same swizzle mapping as the basic family at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L241-L249).

### default_label, default_not_last, no_default_label, default_only, empty_case_default — Default-label placement and absence

`default_label_*` puts the default label after explicit cases and maps unmatched selector value `2` to `coords.yzw` at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L251-L258). `default_not_last_*` places the default label between explicit cases while still breaking from it at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L260-L267). `no_default_label_*` initializes `res` before a switch without a matching `case 2`, so the expected `coords.yzw` value comes from the pre-switch assignment at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L269-L276). `default_only_*` and `empty_case_default_*` cover default-only behavior and an empty `case 2` that falls into default, with dynamic cases intentionally skipped by the registration call at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L278-L295).

### fall_through, fall_through_default, conditional_fall_through, conditional_fall_through_2 — Fall-through behavior

`fall_through_*` mutates `coords` in `case 2` and falls through into `case 4`, which assigns `vec3(coords)` at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L297-L305). `fall_through_default_*` performs the same kind of `case 2` fall-through into the default label at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L307-L315). `conditional_fall_through_*` and `conditional_fall_through_2_*` add a temporary value and conditional `break` logic so fall-through depends on the selected condition or on a modified local selector at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L317-L347).

### scope — Scoped case block

The `scope_*` cases wrap `case 2` in braces, declare a local `mediump vec3 t`, assign it to `res`, and break inside the block at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L349-L361).

### switch_in_if, switch_in_for_loop, switch_in_while_loop, switch_in_do_while_loop — Switch nested inside surrounding control flow

These families place the switch inside an `if`, `for`, `while`, or `do while` construct. The loop variants iterate `i` from zero through the selected condition and switch on `i`, so later iterations overwrite `res` until the selector-equivalent value is reached at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L363-L413).

### if_in_switch, for_loop_in_switch, while_loop_in_switch, do_while_loop_in_switch — Control flow nested inside switch cases

These families put an `if`, `for`, `while`, or `do while` construct inside a switch case or default branch. The loop-in-switch families share `case 1` and `case 2`, initialize `t` from `coords.yzw`, repeatedly swizzle `t.zyx` while the loop condition holds, and assign `res` before breaking at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L415-L482).

### switch_in_switch — Nested switch

The `switch_in_switch_*` cases share `case 1` and `case 2`, then run an inner switch over `${CONDITION} - 1` to select `coords.wzy` or `coords.yzw` before breaking from the outer switch at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L484-L497).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Switch selector type | `static`, `uniform`, and `dynamic` are the three [`SwitchType`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L72-L79) values used by [`makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222). |
| Selector expression | The `${CONDITION}` shader-template placeholder is specialized to literal `2`, uniform `ui_two`, or `int(floor(coords.z*1.5 + 2.0))` at [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L150-L157). |
| Shader stage | Each generated selector-type case is registered once as a vertex case and once as a fragment case at [`ShaderSwitchTests::makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L215-L220). |
| Switch-body families | Twenty-one family names are registered by calls to [`makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L232-L497). Nineteen families produce six direct children each; `default_only` and `empty_case_default` produce four direct children each because dynamic type is skipped at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L278-L295). |
| Uniform data | Uniform selector cases declare a `std140` uniform block containing `highp int ui_two` at [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L135-L137), and [`setUniforms()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L47) binds `UI_TWO`, whose value is `2` in [`ShaderRenderCaseInstance::useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L962-L966). |
| Reference selector mapping | Static and uniform references always produce `coords.yzw` at [`evalSwitchStatic()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L88). Dynamic references switch on `floor(coords.z * 1.5 + 2.0)` and map cases `0`..`3` plus default to specific swizzles at [`evalSwitchDynamic()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L89-L109). |

## Support / Feature Requirements

- The inspected switch file does not define a file-local `checkSupport()` override or extension/feature guard; registration is unconditional within the GLSL package entry list at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270) and the file-local factory simply returns the switch group at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L505).
- Generated shaders use `#version 310 es` in both vertex and fragment sources at [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L118-L122). Uniform-selector cases add the single uniform block only for `SWITCHTYPE_UNIFORM` at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L135-L137).
- Execution support and resource setup are inherited from the shared [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L360-L392) / [`ShaderRenderCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L637-L683) harness rather than from switch-specific support code.

## Verification Methods

- [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L111-L180) inserts the specialized switch body into either the vertex shader or the fragment shader, writes `res` to `v_color` for vertex cases or directly to `o_color` for fragment cases, and attaches the matching evaluator callback.
- Static and uniform cases use evaluator functions that set the expected color to `coords.yzw`, matching selector value `2` at [`evalSwitchStatic()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L88). Dynamic cases compute the reference with the same selector formula and switch mapping at [`evalSwitchDynamic()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L89-L109).
- The shared harness renders a quad grid, computes a vertex or fragment reference image with the evaluator, and compares result and reference images with an error threshold of `0.2f` in [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805).
- Image comparison uses fuzzy comparison when the instance is constructed through the switch tests' `ShaderRenderCase` path, because that constructor sets `m_fuzzyCompare` to `true` at [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683), and [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730) dispatches to `tcu::fuzzyCompare()` in that mode.

## Test Principles

- The file keeps the registration hierarchy flat: every generated case is added directly to the `switch` group by [`ShaderSwitchTests::makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222).
- The generated names encode three tested dimensions: switch-body family, selector type, and shader stage, using the concatenation implemented at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L215-L220).
- Static and uniform selector cases intentionally use selector value `2`, while dynamic cases vary over `coords.z`; the reference code mirrors those choices at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L109) and the shader-template substitution mirrors them at [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L150-L157).
- The switch-body templates isolate specific GLSL control-flow semantics while preserving a common expected swizzle mapping documented in comments at [`ShaderSwitchTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L230).

## Notes / Uncertainties

- The word `placeholder` in this page refers only to the technical `${CONDITION}` shader-template placeholder passed through [`tcu::StringTemplate`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L150-L157); it is not workflow placeholder text.
- No separate switch-specific helper file was observed. The related helper behavior inspected for this page is in the shared shader-render harness files listed in the source section.
