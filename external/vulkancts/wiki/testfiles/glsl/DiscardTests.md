## Overview

**Core question:** Do fragment `discard` and `demote` produce the expected coverage and helper-invocation behavior across different predicates and control-flow placements?

- This page covers the `glsl.discard` and `glsl.demote` test families implemented by [`vktShaderRenderDiscardTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L449).
- Both families use the same generator. Five shader templates place the tested statement in `main`, a function, or a loop. Five ordinary modes change the condition that reaches the statement, and `demote` adds a sixth derivative mode.
- Each test case renders a fragment-shader quad. The shared render harness builds a CPU reference image, substitutes the clear color for fragments marked as discarded, and compares the rendered and reference images.
- The main behavioral distinction is the mode (`always`, `never`, `uniform`, `dynamic`, `texture`, or `deriv`). Template placement is a separate structural dimension that checks whether the same behavior survives function and loop control flow.

## Background Knowledge

- Fragment termination and demotion remove the invocation's covered samples by setting their coverage mask bits to zero. `discard` terminates or converts the fragment invocation according to the shader instruction used by the implementation. `demote` explicitly converts it to a helper invocation, so later shader instructions can still execute without contributing to the framebuffer. See the Vulkan specification's [Shader Termination and Demotion](../../../../vulkan-docs/src/chapters/fragops.adoc#L850-L857) rules.
- Fragment shaders may use helper invocations to supply neighboring values for derivative operations. Helper invocations can participate in derivatives, but their output stores do not affect the framebuffer. The `deriv` mode depends on this distinction; the ordinary modes need only the coverage effect. See [Helper Invocations](../../../../vulkan-docs/src/chapters/shaders.adoc#L3728-L3752).

## Registration Hierarchy

```text
glsl
├── discard
└── demote
```

[`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) registers `discard` in all builds and registers `demote` only when `CTS_USES_VULKANSC` is not defined. Each test family contains direct test case leaves named `<template>_<mode>`. The default Vulkan mustpass lists contain all [25 `discard` leaves](../../../mustpass/main/vk-default/glsl.txt#L6954-L6978) and all [30 `demote` leaves](../../../mustpass/main/vk-default/glsl.txt#L5250-L5279).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `discard`, `demote` | Selects the fragment statement. `demote` also enables the helper-invocation-specific `deriv` mode. | [`createDiscardTests()` and `createDemoteTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L441-L449) |
| Template | `basic`, `function`, `static_loop`, `dynamic_loop`, `function_static_loop` | Moves the generated statement between `main`, a called function, a fixed two-iteration loop, a uniform-bounded loop, and a fixed loop inside a function. | [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300), [`getTemplateName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L302-L320) |
| Mode | `always`, `never`, `uniform`, `dynamic`, `texture`; plus `deriv` for `demote` | Changes the condition and data path that control whether the fragment loses coverage. This is the primary behavioral axis. | [`DiscardMode`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L153-L163), [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399) |
| Test case leaf | `<template>_<mode>` | Combines one control-flow placement with one behavior mode. | [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L436) |
| Matrix size | 25 `discard` leaves; 30 `demote` leaves | `discard` uses five templates by five ordinary modes. `demote` uses the same templates and adds `deriv`. | [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L436) |
| Image comparison | Fuzzy for ordinary modes; pixel threshold for `deriv` | Ordinary rendered images use tolerance `0.2f`. The expected-clear derivative cases use a per-channel threshold of one integer color unit. | [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L393-L399), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730) |

## Behavior Parameters

The mode suffix is the primary behavioral axis. It changes the predicate, the shader inputs used by that predicate, and the expected image. The template prefix changes where that behavior appears in control flow without changing its intended result.

### `always`: unconditional coverage removal

The shader executes `discard` or `demote` for every fragment. The CPU evaluator marks every reference fragment as discarded, so the expected image contains only the clear color.

### `never`: dead conditional path

The statement appears behind `if (false)`. No fragment executes it, and the shader output remains the interpolated vertex color. This mode catches an implementation that executes or mishandles a syntactically present but unreachable statement.

### `uniform`: uniform-controlled coverage removal

The shader executes the statement when `ui_one > 0`. [`SamplerUniformSetup`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L59) binds `UI_ONE`, whose shared uniform setup resolves to the integer value 1, so every fragment should lose coverage. This mode routes the decision through a uniform load rather than a literal condition.

### `dynamic`: interpolated coordinate predicate

The shader executes the statement when `v_coords.x + v_coords.y > 0.0`. The CPU evaluator applies the same predicate to interpolated coordinates, producing a spatial boundary between clear pixels and color output.

### `texture`: sampled predicate

The shader samples `vulkan/data/brick.png` at `v_coords.xy * 0.25 + 0.5` and executes the statement when the sampled red component is below `0.7`. The test instance creates a 2D texture with clamp-to-edge addressing and linear filtering, and the CPU evaluator samples the same texture through the shared quad-grid model.

### `deriv`: demotion, helper state, and derivatives

This mode exists only under `demote`. Within each fragment quad, the shader first demotes invocations whose fragment-coordinate low bits are not both zero. The remaining invocation reads `helperInvocationEXT()`, calculates `dFdx` and `dFdy`, and checks both the derivative values and helper-state variation. A valid result causes the remaining invocation to demote, leaving the image clear. Failed shader-side checks write red.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.discard.dynamic_loop_dynamic
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `discard` | Selects the ordinary fragment-termination family; the generated case passes `discard` as `discardStr`. |
| `dynamic_loop` | Places the selected statement in the second iteration of a loop in `main`, with the loop bound read from `ui_two`. |
| `dynamic` | Guards the statement with `if (v_coords.x+v_coords.y > 0.0)`, producing coordinate-dependent coverage removal. |
| `dynamic_loop_dynamic` | Combines the runtime uniform loop bound and interpolated-coordinate predicate, exercising both control-flow placement and the primary behavioral condition. |

#### Purpose

This fragment shader checks that `discard` removes coverage for the coordinate-selected fragments even when the statement is reached through a uniform-bounded loop. Fragments that do not satisfy the predicate retain the interpolated color.

#### Structural Design

| Phase | Source-generated behavior | Shader-visible inputs/resources |
|-------|---------------------------|----------------------------------|
| Initialize output | Copy `v_color` to `o_color`. | Location 0 input/output vectors. |
| Iterate | Start `i` at zero and continue while `i < ui_two`; the host setup binds `ui_two` to `2`. | Set 0, binding 1 uniform block `block1.ui_two`. |
| Select statement | Only the second iteration (`i > 0`) reaches the substituted statement. | Function-local integer loop counter. |
| Apply mode | Evaluate `v_coords.x + v_coords.y > 0.0`; execute `discard` when true. | Location 1 `v_coords`; no sampled data is used by this mode. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_demote_to_helper_invocation : enable
/// Interpolated vertex color; fragments that survive discard write this value.
layout(location = 0) in mediump vec4 v_color;
/// Interpolated coordinates shared with the CPU evaluator for the dynamic predicate.
layout(location = 1) in mediump vec4 v_coords;
/// Fixed generator interface input; this representative mode does not read it.
layout(location = 2) in mediump vec4 a_one;
/// The render harness compares this fragment output with its CPU reference image.
layout(location = 0) out mediump vec4 o_color;
/// Fixed template declaration; only texture mode samples this binding.
layout(set = 0, binding = 2) uniform sampler2D    ut_brick;
/// Shared template uniform; this mode does not read ui_one.
layout(set = 0, binding = 0) uniform block0 { mediump int  ui_one; };
/// SamplerUniformSetup binds UI_TWO (value 2) at binding 1, selecting two loop iterations.
layout(set = 0, binding = 1) uniform block1 { mediump int  ui_two; };

void main (void)
{
    /// Preserve the interpolated color unless the selected fragment is discarded.
    o_color = v_color;
    for (int i = 0; i < ui_two; i++)
    {
        if (i > 0) {
            if (v_coords.x+v_coords.y > 0.0) discard;
        }
    }
}
```

#### Additional Info

- The exact substitution is emitted by `makeDiscardCase()` for `DISCARDMODE_DYNAMIC`; `getTemplate(DISCARDTEMPLATE_MAIN_DYNAMIC_LOOP)` supplies the surrounding loop and binding-1 declaration ([`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L265-L276), [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L351-L364)).
- `SamplerUniformSetup::setup()` binds `UI_TWO`; the shared setup supplies the value `2`, so the fragment source has a runtime loop bound rather than a reconstructed literal ([`SamplerUniformSetup`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L55)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Test family | `discard` emits the selected `discardStr`; `demote` uses the same templates but emits `demote` and adds the `deriv` mode. | [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L399) |
| Template | `basic`, `function`, `static_loop`, `dynamic_loop`, and `function_static_loop` move the same substitution among direct, function, and loop control flow; `dynamic_loop` adds `ui_two`. | [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300) |
| Mode | `always`, `never`, `uniform`, `dynamic`, and `texture` change the substituted predicate; `texture` additionally uses the brick sampler, while `deriv` is demote-only and emits helper/derivative checks. | [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L351-L386) |
| Uniform/resource setup | `ui_one` and `ui_two` remain in the shared template; binding 2 is host-bound only for `texture`, and this selected mode has no texture read. | [`SamplerUniformSetup`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L59) |

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
; Bound: 61
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %v_color %v_coords %a_one
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_demote_to_helper_invocation"
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %v_color "v_color"
               OpName %i "i"
               OpName %block1 "block1"
               OpMemberName %block1 0 "ui_two"
               OpName %_ ""
               OpName %v_coords "v_coords"
               OpName %a_one "a_one"
               OpName %ut_brick "ut_brick"
               OpName %block0 "block0"
               OpMemberName %block0 0 "ui_one"
               OpName %__0 ""
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %v_color RelaxedPrecision
               OpDecorate %v_color Location 0
               OpDecorate %12 RelaxedPrecision
               OpDecorate %i RelaxedPrecision
               OpDecorate %22 RelaxedPrecision
               OpDecorate %block1 Block
               OpMemberDecorate %block1 0 RelaxedPrecision
               OpMemberDecorate %block1 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %28 RelaxedPrecision
               OpDecorate %31 RelaxedPrecision
               OpDecorate %v_coords RelaxedPrecision
               OpDecorate %v_coords Location 1
               OpDecorate %40 RelaxedPrecision
               OpDecorate %43 RelaxedPrecision
               OpDecorate %44 RelaxedPrecision
               OpDecorate %50 RelaxedPrecision
               OpDecorate %52 RelaxedPrecision
               OpDecorate %a_one RelaxedPrecision
               OpDecorate %a_one Location 2
               OpDecorate %ut_brick RelaxedPrecision
               OpDecorate %ut_brick Binding 2
               OpDecorate %ut_brick DescriptorSet 0
               OpDecorate %block0 Block
               OpMemberDecorate %block0 0 RelaxedPrecision
               OpMemberDecorate %block0 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %v_color = OpVariable %_ptr_Input_v4float Input
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
     %block1 = OpTypeStruct %int
%_ptr_Uniform_block1 = OpTypePointer Uniform %block1
          %_ = OpVariable %_ptr_Uniform_block1 Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %bool = OpTypeBool
   %v_coords = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
    %float_0 = OpConstant %float 0
      %int_1 = OpConstant %int 1
      %a_one = OpVariable %_ptr_Input_v4float Input
         %54 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %55 = OpTypeSampledImage %54
%_ptr_UniformConstant_55 = OpTypePointer UniformConstant %55
   %ut_brick = OpVariable %_ptr_UniformConstant_55 UniformConstant
     %block0 = OpTypeStruct %int
%_ptr_Uniform_block0 = OpTypePointer Uniform %block0
        %__0 = OpVariable %_ptr_Uniform_block0 Uniform
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
         %12 = OpLoad %v4float %v_color
               OpStore %o_color %12
               OpStore %i %int_0
               OpBranch %17
         %17 = OpLabel
               OpLoopMerge %19 %20 None
               OpBranch %21
         %21 = OpLabel
         %22 = OpLoad %int %i
         %27 = OpAccessChain %_ptr_Uniform_int %_ %int_0
         %28 = OpLoad %int %27
         %30 = OpSLessThan %bool %22 %28
               OpBranchConditional %30 %18 %19
         %18 = OpLabel
         %31 = OpLoad %int %i
         %32 = OpSGreaterThan %bool %31 %int_0
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
         %39 = OpAccessChain %_ptr_Input_float %v_coords %uint_0
         %40 = OpLoad %float %39
         %42 = OpAccessChain %_ptr_Input_float %v_coords %uint_1
         %43 = OpLoad %float %42
         %44 = OpFAdd %float %40 %43
         %46 = OpFOrdGreaterThan %bool %44 %float_0
               OpSelectionMerge %48 None
               OpBranchConditional %46 %47 %48
         %47 = OpLabel
               OpKill
         %48 = OpLabel
               OpBranch %34
         %34 = OpLabel
               OpBranch %20
         %20 = OpLabel
         %50 = OpLoad %int %i
         %52 = OpIAdd %int %50 %int_1
               OpStore %i %52
               OpBranch %17
         %19 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`ShaderDiscardCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L61-L83) configures the shared fragment render case with regular image backing and the default grid size. Texture cases also load `vulkan/data/brick.png` with clamp-to-edge addressing and linear filtering.
- [`SamplerUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L49-L55) binds `ui_one = 1` and `ui_two = 2`. It binds the brick sampler only for `texture` leaves.
- The shared [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) creates a quad grid, renders it, copies the result image, computes a CPU fragment reference, and compares both images.
- For ordinary modes, the CPU evaluator reproduces the condition and output color. [`computeFragmentReference()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718) replaces evaluator-marked discarded fragments with the render target clear color.
- `always`, `never`, `uniform`, `dynamic`, and `texture` use fuzzy comparison with error threshold `0.2f`. `deriv` uses `pixelThresholdCompare` with `tcu::RGBA(1, 1, 1, 1)` because its expected image is clear and any red fallback must remain visible.
- The test passes with `Result image matches reference`. Any comparison failure returns `Image mismatch`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `always` | Unconditional fragment termination or demotion does not remove coverage as expected. |
| `never` | Dead conditional control flow executes or changes the fragment output. |
| `uniform` | The uniform-controlled predicate or the resulting fragment termination/demotion is incorrect. |
| `dynamic` | Coordinate interpolation, predicate evaluation, or fragment termination/demotion disagrees with the CPU reference. |
| `texture` | Texture setup or sampling, sampled predicate evaluation, or fragment termination/demotion disagrees with the CPU reference. |
| `deriv` | Demoted helper state, derivative evaluation, or the final coverage result fails the shader's checks. |

A failure confined to one template prefix also points to the function or loop placement used by that prefix. A mismatch does not identify one implementation layer by itself because shader compilation, drawing, copyback, and comparison share the same observed image.

### Cause Analysis

#### Incorrect unconditional or dead-path control flow

**Possible failure symptoms:** `always` leaves non-clear pixels, or `never` loses pixels or changes their interpolated color. The same mode may fail under one template placement and pass under another.

**Possible implementation causes:** Shader compilation or execution may lower unconditional termination/demotion, dead conditionals, function calls, or loop-contained statements incorrectly. If failures occur across all templates, the common statement semantics are the stronger lead. If only a function or loop template fails, its control-flow placement is the distinguishing evidence.

#### Incorrect uniform-controlled behavior

**Possible failure symptoms:** A `uniform` leaf contains non-clear pixels even though the harness binds `ui_one` to 1. A `dynamic_loop_uniform` leaf may differ from other `uniform` leaves if the loop bound or second iteration is mishandled.

**Possible implementation causes:** The uniform value may be loaded or compared incorrectly, or the selected statement may be lowered incorrectly after uniform control flow. A failure limited to `dynamic_loop` also makes the `ui_two = 2` loop bound and loop execution relevant. The rendered image alone cannot distinguish descriptor/uniform setup from shader-side use.

#### Incorrect coordinate-dependent behavior

**Possible failure symptoms:** `dynamic` leaves show a boundary or pixel colors that differ from the CPU image. The mismatch follows interpolated coordinates rather than covering the whole render target.

**Possible implementation causes:** Fragment input interpolation, floating-point predicate evaluation, or the termination/demotion instruction may disagree with the evaluator. The shared comparison permits normal tolerance, so a reported mismatch exceeds that path's accepted image error.

#### Incorrect sampled behavior

**Possible failure symptoms:** `texture` leaves differ in the regions selected by the brick sample and its `0.7` red-channel threshold.

**Possible implementation causes:** Texture upload or binding, coordinate interpolation, clamp-to-edge and linear sampling, predicate evaluation, or termination/demotion may differ from the CPU model. Comparing `texture` with the corresponding `dynamic` and unconditional leaves can separate texture-specific evidence from failures common to the statement.

#### Incorrect demotion, helper state, or derivatives

**Possible failure symptoms:** A `deriv` leaf contains red or other non-clear pixels. The pixel-threshold comparison reports the mismatch without fuzzy tolerance.

**Possible implementation causes:** The implementation may lower `demote` incorrectly, report `helperInvocationEXT()` state incorrectly, compute the expected quad derivatives incorrectly, or retain framebuffer coverage for invocations that the shader demotes. The shader combines these checks before producing the image, so the result cannot isolate one of them without source-level or shader-level investigation.

#### Shared render or reference-path mismatch

**Possible failure symptoms:** Many unrelated modes and template placements fail with `Image mismatch`, including cases whose expected images differ.

**Possible implementation causes:** Common pipeline setup, rendering, synchronization, result copyback, CPU reference generation, or image comparison may be responsible. Such a pattern gives broader evidence than a failure limited to one mode, but still requires logs and source-level investigation before assigning the fault.

## Case Pruning

### Requirement-based pruning

- `demote` test cases call [`ShaderDiscardCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L143-L150). Devices without `shaderDemoteToHelperInvocation` receive `NotSupportedError` instead of executing the case.
- Vulkan SC builds do not register the `demote` test family because [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259) places its factory call under `#ifndef CTS_USES_VULKANSC`. This is a compile-time registration exclusion, not an image-comparison failure.
- The implementation adds no file-local feature check for `discard`; those cases still use the shared ShaderRender setup and its general Vulkan requirements.

### Design-based pruning

- The generator skips `deriv` when the test family name is `discard` ([`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L426-L435)). Its shader sequence needs invocations to continue as helpers while derivatives remain meaningful, which the source says does not work with `discard` because the derivatives become undefined.
- The matrix fixes the statement to fragment shaders and uses the same five template placements for both families. It does not generate separate vertex, tessellation, geometry, or compute cases because discard/demotion and the image oracle here are designed around fragment coverage.

## Key Takeaways

- `discard` has 25 direct leaves. `demote` has 30 because it adds the helper-invocation and derivative `deriv` mode.
- Mode suffixes define the tested behavior; template prefixes repeat that behavior through direct, function, and loop control flow.
- Ordinary modes compare the rendered coverage and color against a CPU evaluator. `deriv` performs helper-state and derivative checks in the shader and exposes failure as red output.
- The clear color is part of the oracle: the reference renderer uses it wherever the evaluator marks a fragment as discarded.
- See `Failure Meaning` when interpreting an image mismatch; one failed leaf narrows the relevant behavior but does not identify a single faulty implementation layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test instance, resource setup, and feature check | [`ShaderDiscardCaseInstance` and `ShaderDiscardCase`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L42-L151) | Defines uniforms, optional texture setup, image comparison mode, and `demote` support gating. |
| CPU evaluators | [`evalDiscardAlways()` through `getEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L176-L219) | Builds the ordinary reference behavior for each mode. |
| Shader templates | [`getTemplate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L221-L300) | Places the generated statement in direct, function, and loop control flow. |
| Mode substitution and test case construction | [`makeDiscardCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L344-L400) | Defines each mode's GLSL, expected evaluator, texture use, comparison choice, and leaf name. |
| Matrix registration | [`ShaderDiscardTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L402-L449) | Generates the direct leaves and omits `discard` derivative cases. |
| GLSL parent registration | [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) | Places both test families under `glsl` and excludes `demote` from Vulkan SC. |
| Shared render and compare path | [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Renders, computes the reference, compares images, and returns pass or fail. |
| Discarded-fragment reference and comparison | [`computeFragmentReference()` and `compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2730) | Converts discarded reference fragments to clear color and selects fuzzy or pixel-threshold comparison. |
| Default Vulkan mustpass coverage | [`glsl.discard`](../../../mustpass/main/vk-default/glsl.txt#L6954-L6978), [`glsl.demote`](../../../mustpass/main/vk-default/glsl.txt#L5250-L5279) | Confirms the 25 and 30 registered test case leaves. |
