# Shader Discard and Demote Tests

## Overview

Tests for the GLSL `discard` statement and `demote` functionality (`VK_EXT_shader_demote_to_helper_invocation`) in fragment shaders. Verifies correct rendering behavior when fragments are discarded or demoted under various control flow patterns and conditions.

## Role

Both registration and implementation. The `ShaderDiscardTests` class (derived from `tcu::TestCaseGroup`) is parameterized by group name (`"discard"` or `"demote"`) and populates child test cases in its `init()` method. The same class serves both registration paths, with the `demote` group including an additional `DISCARDMODE_DERIV` mode.

## Source Code

[../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L1-L452)

## Registration Hierarchy

### glsl.discard

```text
glsl.discard
├── basic_always
├── basic_never
├── basic_uniform
├── basic_dynamic
├── basic_texture
├── function_always
├── function_never
├── function_uniform
├── function_dynamic
├── function_texture
├── static_loop_always
├── static_loop_never
├── static_loop_uniform
├── static_loop_dynamic
├── static_loop_texture
├── dynamic_loop_always
├── dynamic_loop_never
├── dynamic_loop_uniform
├── dynamic_loop_dynamic
├── dynamic_loop_texture
├── function_static_loop_always
├── function_static_loop_never
├── function_static_loop_uniform
├── function_static_loop_dynamic
└── function_static_loop_texture
```

### glsl.demote

```text
glsl.demote
├── basic_always
├── basic_never
├── basic_uniform
├── basic_dynamic
├── basic_texture
├── basic_deriv
├── function_always
├── function_never
├── function_uniform
├── function_dynamic
├── function_texture
├── function_deriv
├── static_loop_always
├── static_loop_never
├── static_loop_uniform
├── static_loop_dynamic
├── static_loop_texture
├── static_loop_deriv
├── dynamic_loop_always
├── dynamic_loop_never
├── dynamic_loop_uniform
├── dynamic_loop_dynamic
├── dynamic_loop_texture
├── dynamic_loop_deriv
├── function_static_loop_always
├── function_static_loop_never
├── function_static_loop_uniform
├── function_static_loop_dynamic
├── function_static_loop_texture
└── function_static_loop_deriv
```

## Test Families

- **ShaderDiscardCase** - Single test case class for both discard and demote tests. Each case is a `ShaderRenderCase` that renders a quad with a fragment shader containing a `discard` or `demote` statement under a specific template and mode combination.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| DiscardTemplate | MAIN_BASIC, FUNCTION_BASIC, MAIN_STATIC_LOOP, MAIN_DYNAMIC_LOOP, FUNCTION_STATIC_LOOP | Structural template for where the discard/demote appears in the shader |
| DiscardMode | ALWAYS, NEVER, UNIFORM, DYNAMIC, TEXTURE, DERIV (demote only) | Condition under which discard/demote is triggered |

### DiscardTemplate Details

- **MAIN_BASIC**: Discard/demote in main() with a simple if statement
- **FUNCTION_BASIC**: Discard/demote inside a called function
- **MAIN_STATIC_LOOP**: Discard/demote inside a static loop in main()
- **MAIN_DYNAMIC_LOOP**: Discard/demote inside a dynamic (data-dependent) loop in main()
- **FUNCTION_STATIC_LOOP**: Discard/demote inside a static loop within a called function

### DiscardMode Details

- **ALWAYS**: Unconditionally discards/demotes every fragment
- **NEVER**: Discard/demote is never reached (`if (false)`)
- **UNIFORM**: Discard/demote based on a uniform value (`if (ui_one > 0)`)
- **DYNAMIC**: Discard/demote based on varying coordinates (`if (v_coords.x+v_coords.y > 0.0)`)
- **TEXTURE**: Discard/demote based on a texture lookup result
- **DERIV**: Demote-specific mode that verifies derivative and helperInvocationEXT behavior after demotion

## Support/Feature Requirements

- **Demote tests** (entire `glsl.demote` group): Require `VK_EXT_shader_demote_to_helper_invocation`. The `checkSupport()` method checks `shaderDemoteToHelperInvocation` feature bit.
- **Discard tests** (`glsl.discard` group): No additional requirements beyond core Vulkan.

## Verification Methods

- **Fuzzy image comparison**: Used for all modes except DERIV. The `ShaderEvaluator`-based reference rendering produces the expected image, and fuzzy comparison accounts for discard-related rendering differences at triangle edges.
- **Non-fuzzy comparison**: Used for the DERIV mode. The DERIV test demotes all but one pixel per 2x2 quad, then verifies that derivatives of `a_one.xy + gl_FragCoord.xy` produce the expected values (1.0 in the appropriate axis, 0.0 in the other), and that `helperInvocationEXT()` returns correct values. If all checks pass, the pixel is demoted; otherwise it outputs red. The final image should match the clear color.
- **ShaderEvaluator reference**: Each mode has a corresponding evaluation function (`evalDiscardAlways`, `evalDiscardNever`, `evalDiscardDynamic`, `evalDiscardTexture`) that computes the expected fragment color, with `c.discard()` called for fragments that should be discarded.

## Notes

- The `DISCARDMODE_DERIV` mode is exclusive to the `demote` group. When the group name is `"discard"`, the DERIV mode is skipped during test case creation.
- Texture-based discard cases use a brick texture (`vulkan/data/brick.png`) sampled with clamp-to-edge and linear filtering.
- The discard statement in GLSL terminates the fragment and discards all outputs, while demote converts the invocation to a helper invocation that still participates in derivative computation.
