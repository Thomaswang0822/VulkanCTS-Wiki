## Overview

[`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L1) implements two `ShaderRenderCase`-based GLSL test roots. `glsl.discard` exercises the fragment `discard` statement; `glsl.demote` exercises `demote` and is registered only in non-Vulkan SC builds. Both roots are instances of the same `ShaderDiscardTests` class and use a five-template × six-mode generator, with the derivative mode excluded from `discard`.

The cases render a fragment-shader quad and compare the resulting image with a CPU evaluator through the shared [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) path. Evaluators mark discarded fragments through `ShaderEvalContext::isDiscarded`; [`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718) represents those fragments with the render target's clear color. Thus ordinary cases test the observable rendered image, not a direct API return value.

## Role

Registration and implementation-heavy test file. The public header declares [`createDiscardTests()` and `createDemoteTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.hpp#L35-L36). The GLSL parent adds discard unconditionally and demote under `#ifndef CTS_USES_VULKANSC` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). The factories construct [`ShaderDiscardTests`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L416-L419) with group names `discard` and `demote` at [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L441-L449).

## Source Code

- Primary implementation: [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L1)
- Public declarations: [`vktShaderRenderDiscardTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.hpp#L23-L36)
- GLSL parent registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259)
- Shared render harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)
- Build inventory: [`CMakeLists.txt`](../../../modules/vulkan/shaderrender/CMakeLists.txt#L7-L16)

## Registration Hierarchy

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

`ShaderDiscardTests::init()` directly creates the Cartesian product of `DiscardTemplate` and `DiscardMode`, skipping `DISCARDMODE_DERIV` when the group is `discard` ([`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435)). The canonical roots above therefore contain 25 and 30 direct leaves respectively. The detailed leaf grammar is `<template>_<mode>`; the source name tables are [`getTemplateName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L302-L320) and [`getModeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L322-L342).

## Test Families

### Template placement matrix

The five templates vary the control-flow location of the generated statement ([`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300)):

- `basic`: statement directly in `main`, after initializing `o_color`.
- `function`: statement in `myfunc()`, called from `main`.
- `static_loop`: statement in the second iteration of a two-iteration loop in `main`.
- `dynamic_loop`: same loop shape, with the bound supplied by uniform `ui_two`.
- `function_static_loop`: the static loop is inside `myfunc()`.

All templates use GLSL ES 3.10 and enable `GL_EXT_demote_to_helper_invocation`. The fragment header declares the interpolated color and coordinates, `a_one`, the color output, the brick sampler, and uniform `ui_one`. The fixed vertex shader writes position, color, coordinates, and `a_one` ([`ShaderDiscardCase::ShaderDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L113-L140)).

### Ordinary discard-condition modes

`makeDiscardCase()` substitutes the following statement forms ([`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L367)):

| Mode | Generated condition | CPU reference |
|---|---|---|
| `always` | unconditional `discard` or `demote` | discard every fragment |
| `never` | `if (false) discard/demote` | never discard; output interpolated coordinates |
| `uniform` | `if (ui_one > 0) discard/demote` | the always-discard evaluator; `ui_one` is installed through `SamplerUniformSetup` ([`L42-L55`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L55)) |
| `dynamic` | `if (v_coords.x+v_coords.y > 0.0) discard/demote` | same coordinate-sum predicate |
| `texture` | brick sample at `v_coords.xy*0.25+0.5`, discard/demote when `.x < 0.7` | same texture sample and threshold |

Texture cases allocate `vulkan/data/brick.png` with clamp-to-edge addressing and linear filtering in [`ShaderDiscardCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L69-L83); the sampler is bound only for the texture mode.

### `demote` derivative/helper-invocation mode

`deriv` is registered only under `glsl.demote`. It is deliberately not generated for `discard`: the source notes that derivatives become undefined for that use ([`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L369-L386)). The generated fragment code first demotes fragments whose `gl_FragCoord` low bits are not both zero. For the remaining fragment it queries `helperInvocationEXT()`, computes `dFdx`/`dFdy` of `a_one.xy + gl_FragCoord.xy`, computes a derivative of the helper flag, and demotes when the expected derivative and helper conditions hold; otherwise it writes red. This mode is intended to leave the image at the clear color when the helper-invocation and derivative behavior is accepted by the shader.

## Parameter Dimensions and Observed Values

| Dimension | Values / evidence |
|---|---|
| Registered roots | `discard` always; `demote` only outside `CTS_USES_VULKANSC` ([`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259)) |
| Templates | `basic`, `function`, `static_loop`, `dynamic_loop`, `function_static_loop` ([`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L165-L174), [`L302-L320`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L302-L320)) |
| Modes | `always`, `never`, `uniform`, `dynamic`, `texture`, `deriv` ([`L153-L163`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L153-L163), [`L322-L342`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L322-L342)) |
| Leaf counts | 5 × 5 = 25 under `discard`; 5 × 6 = 30 under `demote` |
| Texture | 2D `vulkan/data/brick.png`, clamp-to-edge, linear filtering ([`L69-L83`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L69-L83)) |
| Render grid | `GRID_SIZE_DEFAULTS`; regular image backing ([`L69-L73`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L69-L73)) |
| Comparison | Fuzzy for all modes except `deriv`; `deriv` uses the non-fuzzy threshold path ([`L395-L399`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L395-L399), [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)) |

## Support / Feature Requirements

- `discard` has no file-local discard-specific support check in [`ShaderDiscardCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150); it still runs through the shared ShaderRender prerequisites.
- Non-SC `demote` cases require the device feature `shaderDemoteToHelperInvocation`; otherwise `checkSupport()` throws `NotSupportedError` ([`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150)).
- The `demote` factory call is compile-time excluded from Vulkan SC by the parent package guard. Consequently Vulkan SC mustpass contains `discard` but not `demote`; this is a registration exclusion, not a runtime failure.
- Texture support is setup performed by the shared render harness after `useSampler(2u, 0u)` is requested ([`SamplerUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L55), [`ShaderRenderCaseInstance::useSampler()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1459-L1475)).

## Verification Methods

Each leaf is a fragment-only `ShaderRenderCase`. The shared runner renders the quad grid, computes the CPU fragment reference, and compares the image using threshold `0.2f` ([`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)). When an evaluator calls `c.discard()`, the reference path substitutes the clear color ([`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2709-L2718)).

Ordinary modes use fuzzy image comparison, allowing the normal image tolerance path. `deriv` sets `fuzzyCompare` false and therefore uses the exact pixel-threshold comparison path ([`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L395-L399), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)). A derivative-case mismatch can establish that the rendered image differs from the expected clear/red outcome; it does not by itself localize the cause to derivative computation, helper-invocation tracking, demote lowering, or the shared rendering harness.

## Mustpass Coverage

The registration Cartesian products reconcile with the inspected default lists:

| Profile / root | Expected | Observed | Evidence |
|---|---:|---:|---|
| Vulkan default `glsl.discard` | 25 | 25 | [`glsl.txt#L6954-L6978`](../../../mustpass/main/vk-default/glsl.txt#L6954-L6978) |
| Vulkan default `glsl.demote` | 30 | 30 | [`glsl.txt#L5250-L5279`](../../../mustpass/main/vk-default/glsl.txt#L5250-L5279) |
| Vulkan SC default `glsl.discard` | 25 | 25 | [`glsl.txt#L6035-L6059`](../../../mustpass/main/vksc-default/glsl.txt#L6035-L6059) |
| Vulkan SC default `glsl.demote` | not registered | 0 | The parent call is under `#ifndef CTS_USES_VULKANSC` ([`vktTestPackage.cpp#L1253-L1259`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259)). |

The mustpass lines are sorted by case name, while registration order follows the nested template-then-mode loops; the order difference does not change the exact leaf set.

## Test Principles

- The implementation shares one generator between `discard` and `demote`; the root name is passed both as the emitted statement spelling and as the demote flag ([`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399)).
- Templates vary statement placement; ordinary modes vary the condition that controls execution. This separates control-flow placement from the discard predicate.
- The CPU reference models ordinary discard/demote output through `isDiscarded` and clear-color substitution rather than comparing an intermediate shader value.
- The derivative family is demote-only because it relies on helper invocations and defined derivatives after demotion; its red fallback makes failed shader-side checks visible in the image.

## Failure Cause Mapping

| Observed symptom | Behavior group | Plausible causes and limits |
|---|---|---|
| Whole-image mismatch in `always`, `never`, `uniform`, `dynamic`, or `texture` | Ordinary discard/demote matrix | Fragment control flow, condition evaluation, interpolation, texture/sampler setup, shader compilation, rendering, synchronization, readback, or image comparison. The image oracle does not uniquely identify one layer. |
| Mismatch limited to coordinate-dependent output | Ordinary `dynamic` or `texture` cases | Coordinate interpolation, predicate evaluation, texture contents/sampling, or the CPU/GPU reference disagreement; it is not proof of a particular compiler or rasterizer defect. |
| `glsl.demote` reports unsupported | All demote modes | Missing `shaderDemoteToHelperInvocation` causes `NotSupportedError`; this is a skip/support result, not an executed-case image failure. |
| Red output or non-clear pixels in `*_deriv` | `demote` derivative/helper-invocation mode | Helper-invocation state, derivative behavior, demote semantics, shader lowering, or render-path handling. A mismatch does not isolate the responsible mechanism. |
| Only one template placement fails | Template placement dimension | Function-call or loop control-flow lowering, uniform loop bounds, or interaction with the shared condition; compare the corresponding mode across templates before narrowing diagnosis. |

## Notes / Uncertainties
- This page covers only the two roots created by `vktShaderRenderDiscardTests.cpp`; similarly named discard tests in other Vulkan CTS subsystems are separate pages and are not part of this registration path.
- The fragment shader header enables the demote extension for every generated template, but the source-level feature check is applied only to cases whose root is `demote`.
- No shader disassembly or standalone artifact is published by this test file; the authoritative generated shader source is the GLSL template specialized by `makeDiscardCase()`.
