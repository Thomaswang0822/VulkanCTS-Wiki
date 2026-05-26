# Shader Discard and Demote Tests

## Overview

[`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L1) registers and implements two ShaderRenderCase-based GLSL groups: `glsl.discard` and, outside Vulkan SC builds, `glsl.demote`. The Vulkan package attaches `discard` unconditionally and `demote` under `#ifndef CTS_USES_VULKANSC` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). Both groups are built by the same `ShaderDiscardTests` class, which is constructed with group name `"discard"` or `"demote"` and generates fragment-shader cases from template and mode loops in [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435).

The ordinary discard/demote cases render a quad and compare the rendered image against a CPU reference that marks discarded fragments as the shared clear color. The shared harness renders, computes a fragment reference, and compares images in [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805); fragment reference generation selects the clear color when `ShaderEvalContext::isDiscarded` is set at [`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718).

## Role

Registration and implementation file. The public header declares `createDiscardTests()` and `createDemoteTests()` at [`vktShaderRenderDiscardTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.hpp#L35-L36). The source factories return `ShaderDiscardTests(testCtx, "discard")` and `ShaderDiscardTests(testCtx, "demote")` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L441-L449), and the class constructor uses the supplied group name as the registered group name at [`ShaderDiscardTests::ShaderDiscardTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L416-L419).

## Source Code

- Primary source: [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L1)
- Public factory declaration: [`vktShaderRenderDiscardTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.hpp#L35-L36)
- GLSL category registration site: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259)
- Shared ShaderRender harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)
- Build inventory: [`CMakeLists.txt`](../../../modules/vulkan/shaderrender/CMakeLists.txt#L7-L16)

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

### Generated template × mode cases

`ShaderDiscardTests::init()` nests `tmpl < DISCARDTEMPLATE_LAST` and `mode < DISCARDMODE_LAST`, then creates each child with `makeDiscardCase()` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435). Child names are composed as `getTemplateName(tmpl) + "_" + getModeName(mode)` at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L393-L399), with template names `basic`, `function`, `static_loop`, `dynamic_loop`, and `function_static_loop` defined at [`getTemplateName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L302-L320) and mode names `always`, `never`, `uniform`, `dynamic`, `texture`, and `deriv` defined at [`getModeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L322-L342).

The `discard` root receives the five non-derivative modes for each of the five templates because `init()` skips `DISCARDMODE_DERIV` when `m_groupName == "discard"` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435). The `demote` root receives the same 25 ordinary cases plus the five `*_deriv` cases because the group name passed to `makeDiscardCase()` is also the shader statement string, so the generated fragment source uses either `discard` or `demote` at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399).

### Fragment-shader control-flow templates

The five templates vary where the generated statement is placed: directly in `main`, inside `myfunc()`, inside a static two-iteration loop in `main`, inside a loop bounded by uniform `ui_two`, or inside a static loop in `myfunc()` at [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300). Every template starts from the same fragment-shader header, which enables `GL_EXT_demote_to_helper_invocation`, declares `v_color`, `v_coords`, `a_one`, output `o_color`, sampler `ut_brick`, and uniform block `ui_one` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L231). The dynamic-loop template adds uniform block `ui_two` before looping with `i < ui_two` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L265-L276).

### Ordinary condition modes

`makeDiscardCase()` expands the ordinary modes as an unconditional statement, `if (false)`, `if (ui_one > 0)`, `if (v_coords.x+v_coords.y > 0.0)`, or a brick-texture threshold `texture(ut_brick, v_coords.xy*0.25+0.5).x < 0.7` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L351-L367). Their CPU reference functions either discard all fragments, never discard, discard based on coordinate sum, or sample the same texture coordinate and threshold at [`evalDiscardAlways()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L176-L197) and [`getEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L199-L219). The uniform mode intentionally uses the always-discard reference because `SamplerUniformSetup` binds `ui_one` through `UI_ONE` at [`SamplerUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L55).

### demote derivative-helper mode

The `deriv` mode is generated only under `glsl.demote`; the source comment states it would not work for discard because derivatives become undefined at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L369-L386). The injected shader demotes pixels whose fragment-coordinate low bits are not both zero, checks `helperInvocationEXT()`, computes `dFdx` and `dFdy` of `a_one.xy + gl_FragCoord.xy`, then demotes the remaining pixel if the derivative and helper-invocation checks are valid; otherwise it writes red at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L376-L386). Because `makeDiscardCase()` sets `fuzzyCompare` to false only for `DISCARDMODE_DERIV`, this family uses the exact pixel-threshold comparison path rather than fuzzy comparison at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L395-L399) and [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered roots | `discard` is registered unconditionally and `demote` is registered only outside Vulkan SC builds at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). |
| Template dimension | Five `DiscardTemplate` values are enumerated at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L165-L174), named at [`getTemplateName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L302-L320), and implemented at [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300). |
| Mode dimension | Six `DiscardMode` values are enumerated at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L153-L163) and named at [`getModeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L322-L342). |
| `discard` mode filter | `DISCARDMODE_DERIV` is skipped only when the root group name is `discard`, producing 25 direct children for `glsl.discard` at [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435). |
| `demote` extra mode | `glsl.demote` includes the `deriv` mode for each template, producing 30 direct children from the same loops at [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435). |
| Statement spelling | The group name is passed as `discardStr`, inserted into the shader source, and also used to set the per-case `m_demote` flag when it equals `"demote"` at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399). |
| Texture input | Texture-mode cases bind `vulkan/data/brick.png` as a 2D texture with clamp-to-edge addressing and linear filtering at [`ShaderDiscardCaseInstance::ShaderDiscardCaseInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L69-L83); the sampler is bound only when `m_useSampler` is true at [`SamplerUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L49-L55). |
| Render grid and comparison style | Cases use `GRID_SIZE_DEFAULTS`; ordinary cases request fuzzy comparison and `deriv` requests non-fuzzy comparison at [`ShaderDiscardCaseInstance::ShaderDiscardCaseInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L69-L73) and [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L395-L399). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Demote feature gate | For non-Vulkan SC builds, `ShaderDiscardCase::checkSupport()` throws `NotSupportedError` when a demote case lacks `shaderDemoteToHelperInvocation` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150). |
| Vulkan SC registration guard | The `demote` root is not registered in Vulkan SC builds because `createDemoteTests()` is called only inside `#ifndef CTS_USES_VULKANSC` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). |
| Discard root | The inspected source shows no discard-specific feature check in `ShaderDiscardCase::checkSupport()`; the method only gates demote cases outside Vulkan SC builds at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150). |
| Texture setup | Texture cases rely on the shared ShaderRender texture upload/sampler path after `useSampler(2u, 0u)` is requested by the uniform setup at [`SamplerUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L49-L55) and handled by [`ShaderRenderCaseInstance::useSampler()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1459-L1475). |

## Verification Methods

- Each case is a fragment-only `ShaderRenderCase`: the constructor passes `false` for `isVertexCase`, assigns the generated fragment shader, and supplies a fixed vertex shader that forwards position, coordinates, and `a_one` at [`ShaderDiscardCase::ShaderDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L113-L140).
- The shared harness renders the quad grid, copies the rendered image, computes a vertex or fragment reference, and calls `compareImages()` with threshold `0.2f` at [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805).
- Fragment reference generation evaluates the selected `ShaderEvalFunc` per pixel and uses the clear color instead of the evaluator color when the evaluator calls `c.discard()` at [`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718).
- Ordinary modes use fuzzy image comparison because `makeDiscardCase()` sets `fuzzyCompare` to true for every mode except `DISCARDMODE_DERIV`, and `compareImages()` maps that flag to `tcu::fuzzyCompare()` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L395-L399) and [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2727).
- The `deriv` mode uses exact pixel-threshold comparison because it sets `fuzzyCompare` to false and expects successful shader-side checks to demote all output-producing fragments, while failed checks write red at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L369-L386) and [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730).

## Test Principles

- One implementation matrix covers both GLSL `discard` and `demote` by using the registered group name as the shader statement string and as the demote-support flag input at [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399).
- The ordinary matrix separates control-flow placement from discard condition: templates define where the statement appears, while modes define when it executes at [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300) and [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L351-L367).
- The CPU reference models discard by setting `ShaderEvalContext::isDiscarded`, which the shared fragment-reference path converts to the clear color at [`evalDiscardAlways()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L176-L180), [`evalDiscardDynamic()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L185-L190), [`evalDiscardTexture()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L192-L197), and [`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2709-L2718).
- The derivative-helper cases are demote-specific because they depend on helper invocations continuing to participate in derivatives after demotion, as described by the source comments and shader text in [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L369-L386).

## Notes / Uncertainties

- This page documents the two roots implemented by one source file. The `demote` root is conditionally registered outside Vulkan SC builds, while the `discard` root is unconditional in the inspected package registration code at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259).
- The fragment shader header enables `GL_EXT_demote_to_helper_invocation` for all generated templates at [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L231), but the source-level runtime feature gate is applied only when `m_demote` is true at [`ShaderDiscardCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150).
- No source evidence was found in the inspected files for additional discard-specific feature requirements beyond the shared ShaderRender rendering and comparison path.
