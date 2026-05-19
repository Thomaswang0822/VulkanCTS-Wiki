# Shader Switch Statement Tests

## Overview

Tests GLSL `switch` statement semantics in vertex and fragment shaders. Covers basic switch usage, default label handling, fall-through behavior, constant expressions in labels, scoping within switch blocks, and nesting of switch statements inside control flow constructs (if, for, while, do-while) as well as control flow constructs nested inside switch statements.

## Role

Both registration and implementation. The `ShaderSwitchTests` class (a `tcu::TestCaseGroup` named `"switch"`) registers all test cases in its `init()` method, and the `ShaderSwitchCase` class provides the full test implementation via the `ShaderRenderCase` framework.

## Source Code

[vktShaderRenderSwitchTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L1-L507)

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

- **ShaderSwitchCase** ([L51-L70](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L51-L70)): Extends `ShaderRenderCase`. Each instance is parameterized by a switch body template, a `SwitchType` (static/uniform/dynamic), and a shader stage (vertex/fragment). The `makeSwitchCases` helper ([L205-L222](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222)) generates the cross-product of switch type and shader stage for each switch pattern.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| SwitchType | `static`, `uniform`, `dynamic` | How the switch selector expression is determined: compile-time constant, uniform value, or varying input ([L72-L79](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L72-L79)) |
| Switch pattern | 22 variants | Basic, const_expr_in_label, default_label, default_not_last, no_default_label, default_only, empty_case_default, fall_through, fall_through_default, conditional_fall_through, conditional_fall_through_2, scope, switch_in_if, switch_in_for_loop, switch_in_while_loop, switch_in_do_while_loop, if_in_switch, for_loop_in_switch, while_loop_in_switch, do_while_loop_in_switch, switch_in_switch |
| Shader stage | `vertex`, `fragment` | Whether the switch logic runs in the vertex or fragment shader |

Note: `default_only` and `empty_case_default` patterns skip the `dynamic` switch type (`skipDynamicType = true`), producing only 4 test cases each instead of 6.

## Support/Feature Requirements

- No additional Vulkan features or extensions beyond core Vulkan 1.0 are required.

## Verification Methods

All tests use `ShaderRenderCase`-based reference comparison. Each test case provides a `ShaderEvalFunc` callback that computes the expected output color from the shader evaluation context:

- **Static/Uniform evaluation** ([L81-L88](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L88)): The switch selector resolves to a known value (2), so the expected result is always `coords.yzw`.
- **Dynamic evaluation** ([L89-L108](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L89-L108)): The switch selector depends on `coords.z`, so the evaluation function mirrors the shader's switch logic to compute the expected swizzle.

The rendered output is compared against the reference image computed by the evaluation function using the `ShaderRenderCase` framework's built-in threshold comparison.

## Notes

- The switch body templates use `${CONDITION}` placeholders that are substituted at test creation time based on the `SwitchType`: `"2"` for static, `"ui_two"` for uniform, or `"int(coords.z * 1.5 + 2.0)"` for dynamic.
- Uniform setup uses `UI_TWO` (uniform value 2) for the uniform switch type ([L44-L47](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L47)).
- The test hierarchy is flat: all test cases are direct children of the `glsl.switch` group, with names encoding the switch pattern, switch type, and shader stage (e.g., `basic_static_vertex`).
