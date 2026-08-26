## Overview

**Core question:** Does each GLSL `return` path terminate the intended function or shader invocation and leave the expected color output?

- [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L40-L135) implements the `glsl.return` test family with `ShaderRenderCase` instances and CPU evaluators.
- The registered cases cover returns from helper functions, `main()`, output-write sequences, finite loops, and a loop whose increment is zero. Each behavior has vertex and fragment variants.
- The shaders use the input coordinate vector to make the selected path visible. The page explains the registered matrix, generated GLSL, host-side rendering and comparison, and the meaning of failures.

## Background Knowledge

- In GLSL, `return` leaves the current function. A value-returning function passes its value to the caller; a `void` function returns control without producing a value.
- A return from the shader entry point ends that invocation. Vulkan describes execution of `OpReturn` in an entry point as terminating the invocation ([Shader Termination](../../../vulkan-docs/src/chapters/shaders.adoc#shaders-termination)).
- Vertex and fragment shaders receive coordinates differently in this test. Vertex cases read the `a_coords` vertex attribute. Fragment cases read the interpolated `v_coords` input produced by the pass-through vertex shader.

## Registration Hierarchy

`createReturnTests()` adds one test family named `return` below the `glsl` test category in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1268). The implementation registers all leaves directly under that family.

```text
glsl.return
├── single_return_vertex
├── single_return_fragment
├── conditional_return_always_vertex
├── conditional_return_always_fragment
├── conditional_return_never_vertex
├── conditional_return_never_fragment
├── conditional_return_dynamic_vertex
├── conditional_return_dynamic_fragment
├── double_return_vertex
├── double_return_fragment
├── last_statement_in_main_vertex
├── last_statement_in_main_fragment
├── output_write_in_func_always_vertex
├── output_write_in_func_always_fragment
├── output_write_in_func_never_vertex
├── output_write_in_func_never_fragment
├── output_write_in_func_dynamic_vertex
├── output_write_in_func_dynamic_fragment
├── output_write_always_vertex
├── output_write_always_fragment
├── output_write_never_vertex
├── output_write_never_fragment
├── output_write_dynamic_vertex
├── output_write_dynamic_fragment
├── return_in_static_loop_always_vertex
├── return_in_static_loop_always_fragment
├── return_in_static_loop_never_vertex
├── return_in_static_loop_never_fragment
├── return_in_static_loop_dynamic_vertex
├── return_in_static_loop_dynamic_fragment
├── return_in_dynamic_loop_always_vertex
├── return_in_dynamic_loop_always_fragment
├── return_in_dynamic_loop_never_vertex
├── return_in_dynamic_loop_never_fragment
├── return_in_dynamic_loop_dynamic_vertex
├── return_in_dynamic_loop_dynamic_fragment
├── return_in_infinite_loop_vertex
└── return_in_infinite_loop_fragment
```

The default Vulkan and Vulkan SC GLSL mustpass files each list the same 38 `glsl.return` test case leaves ([Vulkan](../../../mustpass/main/vk-default/glsl.txt#L14608-L14645), [Vulkan SC](../../../mustpass/main/vksc-default/glsl.txt#L13687-L13724)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Return behavior | `single`, `conditional`, `double`, `last_statement_in_main`, `output_write`, `return_in_static_loop`, `return_in_dynamic_loop`, `return_in_infinite_loop` | Selects the control-flow shape that contains the return statement. These names describe source patterns; the exact leaves are listed in the registration tree. | [`ShaderReturnTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L344-L518) |
| Return mode | `always`, `never`, `dynamic` | Selects the condition used by conditional returns, output-write returns, and finite-loop returns. | [`getReturnModeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L308-L322), [case builders](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L306) |
| Shader stage | `vertex`, `fragment` | Places the tested GLSL in the vertex or fragment stage and changes the coordinate input and output interface. | [`ShaderReturnCase`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L79-L116) |
| Output-write placement | `main`, `myfunc` | Tests the same write, conditional return, and second write sequence in the entry point or a helper function. | [`makeOutputWriteReturnCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249) |
| Loop bound | Literal `1`, uniform `ui_one` with value `1` | Compares a statically expressed finite loop with a runtime uniform loop. | [`makeReturnInLoopCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306) |
| Loop increment in special cases | Uniform `ui_zero` with value `0` | Makes the loop increment zero. The loop body returns on its first execution, so the executed shader path terminates before a second iteration. | [`ShaderReturnTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L481-L518), [`useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L965) |

Vertex shaders read high-precision `a_coords` at location 1 and write `v_color`. Fragment shaders read mediump `v_coords` at location 0 and write `o_color`. The non-tested stage comes from the pass-through shader installed by `ShaderReturnCase`.

## Behavior Parameters

The primary behavioral axis is the test behavior group. Each group changes the return control flow that the generated shader executes. Stage and return mode vary within the groups and do not replace the control-flow behavior itself.

### `single` return: return a value from a helper function

`single_return_vertex` and `single_return_fragment` call `getColor()`, which returns `coords.xyz` as a `vec4` with alpha 1. The test checks that the caller uses the value returned by the helper in both shader stages ([registration and sources](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L346-L375)).

### `conditional` return: select one of two values

The `conditional_return_<mode>_<stage>` cases return `coords.xyz` when the condition is true and `coords.wzy` when execution falls through. `always` uses `true`, `never` uses `false`, and `dynamic` uses `coords.x+coords.y >= 0.0` ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L187)).

### `double` return: ignore an unreachable second return

The `double_return_<stage>` cases put two unconditional value returns in `getColor()`. The first return produces `coords.xyz`; the second `coords.wzy` is unreachable ([registration and sources](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L390-L421)).

### `last_statement_in_main` return: finish the entry point after a write

The `last_statement_in_main_<stage>` cases write `coords.xyz` to the stage output and then execute `return;`. The return has no value and follows the output write ([registration and sources](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L423-L447)).

### `output_write` return: preserve or replace an earlier output write

The `output_write_<mode>_<stage>` cases write `coords.xyz`, conditionally return, and otherwise write `coords.wzy`. The `output_write_in_func_<mode>_<stage>` cases put the same sequence in `myfunc()`. An executed return preserves the first write; fall-through reaches the second write ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249)).

### `return_in_static_loop` and `return_in_dynamic_loop`: return from a finite loop

The loop builder initializes `coords`, enters a loop, and returns `coords` when the selected condition holds. Otherwise it applies `coords = coords.wzyx` and returns after the loop. The static form uses the literal bound `1`; the dynamic form uses the `ui_one` uniform, which the harness sets to 1 ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306)).

### `return_in_infinite_loop`: return before a zero increment can repeat

The two special cases use `for (int i = 1; i < 10; i += ui_zero)` with `ui_zero` set to 0. The loop body immediately returns the input coordinates, so the executed path terminates on its first iteration. The fallback `coords.wzyx` return is not reached in this configuration ([sources](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L481-L518)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.return.conditional_return_dynamic_vertex
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `return` → `conditional` | Selects `makeConditionalReturnInFuncCase()`, whose generated `getColor()` returns `coords.xyz` when the condition is true and `coords.wzy` after fall-through. |
| `dynamic` | Substitutes the exact condition `a_coords.x+a_coords.y >= 0.0`; the CPU evaluator uses the same comparison to select the reference color. |
| `vertex` | Uses `a_coords` at location 1 with `highp` precision, writes `v_color` at location 0, and includes `gl_Position = a_position`; the fragment stage is the fixed pass-through shader installed by `ShaderReturnCase`. |

#### Purpose

This case checks that a dynamically selected return from a value-returning helper propagates the selected `vec4` to the vertex output. The two coordinate swizzles make return-versus-fall-through behavior visible to the image comparison.

#### Structural Design

```mermaid
flowchart TD
    A[vertex main] --> B[gl_Position = a_position]
    B --> C[getColor()]
    C --> D{a_coords.x + a_coords.y >= 0.0?}
    D -->|true| E[return vec4(a_coords.xyz, 1.0)]
    D -->|false| F[return vec4(a_coords.wzy, 1.0)]
    E --> G[v_color = getColor()]
    F --> G
    G --> H[fixed fragment pass-through writes o_color = v_color]
```

#### Shader Code

```glsl
#version 310 es
/// The selected vertex variant reads coordinates at location 1 and exposes the helper result at location 0.
layout(location = 1) in highp vec4 a_coords;
layout(location = 0) in highp vec4 a_position;
layout(location = 0) out mediump vec4 v_color;

/// The helper owns the tested value-return control flow; the caller stores its returned color.
highp vec4 getColor (void)
{
    if (a_coords.x+a_coords.y >= 0.0)
        return vec4(a_coords.xyz, 1.0);
    return vec4(a_coords.wzy, 1.0);
}

void main (void)
{
    gl_Position = a_position;
    v_color = getColor();
}
```

#### Additional Info

- `ShaderReturnCase` installs this generated source as the vertex shader and pairs it with a fixed fragment pass-through that declares `v_color` as a mediump location-0 input and assigns it to `o_color` ([stage setup](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L87-L116)).
- The source generator has no explicit shader build options for this case; `ShaderRenderCase::initPrograms()` therefore inserts the GLSL through the default `ShaderBuildOptions` path ([program setup](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625)).
- The selected `dynamic` evaluator writes `coords.xyz` when `x+y >= 0` and `coords.wzy` otherwise, matching the two generated helper returns ([evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L49-L77)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Return behavior | `single` removes the conditional and keeps one `getColor()` return; `double` adds an unreachable second return; output-write and loop behaviors move the return into different control-flow shapes. | [registration and builders](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L346-L475) |
| Return mode | `always` substitutes `true`, `never` substitutes `false`, and `dynamic` substitutes `<coords>.x+<coords>.y >= 0.0` in the conditional helper. | [conditional builder](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L187) |
| Shader stage | Vertex uses `a_coords`/`a_position` and `v_color`; fragment uses `v_coords` and `o_color`, while the non-selected stage is pass-through. | [stage setup](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L87-L116) |
| Output-write placement | Only `output_write_in_func_*` wraps the write/return/write sequence in `myfunc()`; this representative keeps the tested return in `getColor()` and the output assignment in `main()`. | [output-write builder](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249) |
| Loop bound | Finite-loop variants use literal `1` or uniform `ui_one`; the separate infinite-loop cases use `ui_zero` and return on the first body execution. | [loop builder and special cases](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306), [special cases](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L481-L529) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 55
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %a_coords %_ %a_position %v_color
               OpSource ESSL 310
               OpName %main "main"
               OpName %getColor_ "getColor("
               OpName %a_coords "a_coords"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %a_position "a_position"
               OpName %v_color "v_color"
               OpDecorate %a_coords Location 1
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %a_position Location 0
               OpDecorate %v_color RelaxedPrecision
               OpDecorate %v_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
          %8 = OpTypeFunction %v4float
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %a_coords = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
    %float_0 = OpConstant %float 0
       %bool = OpTypeBool
    %v3float = OpTypeVector %float 3
    %float_1 = OpConstant %float 1
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
 %a_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
         %50 = OpLoad %v4float %a_position
         %52 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %52 %50
         %54 = OpFunctionCall %v4float %getColor_
               OpStore %v_color %54
               OpReturn
               OpFunctionEnd
  %getColor_ = OpFunction %v4float None %8
         %10 = OpLabel
         %16 = OpAccessChain %_ptr_Input_float %a_coords %uint_0
         %17 = OpLoad %float %16
         %19 = OpAccessChain %_ptr_Input_float %a_coords %uint_1
         %20 = OpLoad %float %19
         %21 = OpFAdd %float %17 %20
         %24 = OpFOrdGreaterThanEqual %bool %21 %float_0
               OpSelectionMerge %26 None
               OpBranchConditional %24 %25 %26
         %25 = OpLabel
         %28 = OpLoad %v4float %a_coords
         %29 = OpVectorShuffle %v3float %28 %28 0 1 2
         %31 = OpCompositeExtract %float %29 0
         %32 = OpCompositeExtract %float %29 1
         %33 = OpCompositeExtract %float %29 2
         %34 = OpCompositeConstruct %v4float %31 %32 %33 %float_1
               OpReturnValue %34
         %26 = OpLabel
         %36 = OpLoad %v4float %a_coords
         %37 = OpVectorShuffle %v3float %36 %36 3 2 1
         %38 = OpCompositeExtract %float %37 0
         %39 = OpCompositeExtract %float %37 1
         %40 = OpCompositeExtract %float %37 2
         %41 = OpCompositeConstruct %v4float %38 %39 %40 %float_1
               OpReturnValue %41
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The shared `ShaderRenderCase` creates a `ShaderRenderCaseInstance` with the selected stage, evaluator, and optional uniform setup ([case construction](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L577-L633)).
- The instance prepares the render resources, creates a quad grid, renders the generated program, and copies the resulting image into a host-visible result surface ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L800), [image copy](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2580-L2600)).
- Uniform-backed loop cases bind one uniform buffer at binding 0. `UI_ONE` supplies 1 for the dynamic finite loop, and `UI_ZERO` supplies 0 for the special zero-increment loop ([uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L122-L135), [uniform values](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L965)).
- The host computes a reference image with the selected evaluator. Vertex cases evaluate at grid vertices and interpolate across the rendered quads. Fragment cases evaluate at pixel centers ([vertex reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2690), [fragment reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2719)).
- The harness compares the rendered and reference images with fuzzy error threshold `0.2`. It returns `pass("Result image matches reference")` when the comparison succeeds and `fail("Image mismatch")` otherwise ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L792-L805), [comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `single` | A returned value is not propagated from the helper to the caller, or the shared render path produces a different image. |
| `conditional` | The return condition or fall-through value does not match the evaluator, or the shared render path produces a different image. |
| `double` | The implementation does not preserve the first reachable return, or the shared render path produces a different image. |
| `last_statement_in_main` | The output written before the entry-point return is not preserved, or the shared render path produces a different image. |
| `output_write` | The return does not stop the second output write when selected, or the shared render path produces a different image. |
| `return_in_static_loop` or `return_in_dynamic_loop` | The loop return, fall-through coordinate update, or uniform-backed loop bound does not match the evaluator, or the shared render path produces a different image. |
| `return_in_infinite_loop` | The zero-increment loop does not terminate through its first body return, or the shared render path produces a different image. |

The stage suffix and the `always`, `never`, and `dynamic` values identify the concrete path within each behavior group. They do not change the common image-based pass condition.

### Cause Analysis

#### Return control flow or value propagation

**Possible failure symptoms:** The rendered pixels differ from the evaluator's `coords.xyz`, `coords.wzy`, or loop-transformed result. The symptom can occur in a helper return, an entry-point return, an output-write sequence, or a loop return, depending on the failing test case.

**Possible implementation causes:** The source builders and evaluators define the expected branch and value choices. A failure can therefore indicate a mismatch in shader compilation or execution of `OpReturn`, conditional control flow, function return values, or output writes. The Vulkan specification requires `OpReturn` in an entry point to terminate the invocation, but this source inspection does not identify which implementation component caused a particular mismatch.

#### Loop termination and uniform setup

**Possible failure symptoms:** A finite-loop case produces the wrong transformed coordinates, or a `return_in_infinite_loop` case fails to produce the input coordinates expected from the first loop-body return.

**Possible implementation causes:** The generated loop uses either the literal `1`, `ui_one`, or `ui_zero`, and the harness writes the corresponding value through a uniform buffer. A failure can indicate incorrect uniform data visibility, loop-condition or increment handling, or return execution inside the loop. The inspected CTS code does not establish a more specific cause for an individual image mismatch, so source-level investigation is needed.

#### Shared render and comparison path

**Possible failure symptoms:** The rendered image differs from the CPU reference even when the return-specific control flow is correct. The reported result is `Image mismatch`.

**Possible implementation causes:** The common path includes shader compilation and linking, stage-interface passing, rasterization or interpolation, image copyback, reference generation, and fuzzy comparison. The return test source does not isolate those mechanisms, so a failure may require investigation across the complete generated-shader and render path.

## Case Pruning

### Requirement-based pruning

The inspected return test source has no return-specific `checkSupport()` override, extension gate, or device-feature check. The cases use the common `ShaderRenderCase` requirements. A device or test configuration can still reject the test through shared Vulkan CTS setup, but this page does not assign an additional return-family requirement.

### Design-based pruning

- Every behavior that has a meaningful return condition uses `always`, `never`, and `dynamic`. The single-return, double-return, final-entry-point-return, and zero-increment-loop cases have fixed control flow, so adding those modes would duplicate the source pattern.
- Each behavior has vertex and fragment leaves because the same return construct must be compiled and checked in both stages.
- The output-write sequence has two placements, directly in `main()` and inside `myfunc()`, because function scope changes the return target while the visible writes remain comparable.
- The finite-loop matrix uses a literal bound and the `ui_one` uniform. The special zero-increment loop keeps only the `ui_zero` value needed to exercise return-before-repeat behavior.

## Key Takeaways

- The family makes return control flow visible through color values, so a return-path error becomes an image mismatch rather than an internal control-flow observation.
- The `output_write` cases distinguish an early return from fall-through by placing different coordinate swizzles before and after the return.
- The zero-increment loop is safe in the executed configuration because the first loop-body instruction path returns before the increment can repeat.
- Vertex and fragment cases share the evaluator contract but use different reference-image construction: vertex results are interpolated from evaluated vertices, while fragment results are evaluated at pixel centers.
- Failure interpretation depends on the complete render and comparison path described in `## Failure Meaning`, not on the return statement alone.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createReturnTests()` | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L523-L526) | Creates the `return` test family. |
| `ShaderReturnTests::init()` | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L344-L518) | Registers all 38 test case leaves and fixed special cases. |
| Return evaluators | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L49-L77) | Defines the CPU reference values for the three return modes. |
| Conditional return builder | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L187) | Generates helper-function conditional returns. |
| Output-write return builder | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249) | Generates the early-return and fall-through output sequence. |
| Loop return builder | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306) | Generates static and uniform-bound finite loops. |
| Stage and uniform setup | [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L79-L135) | Connects selected GLSL, pass-through stage code, and uniform values to `ShaderRenderCase`. |
| `ShaderRenderCase::initPrograms()` | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625) | Adds the generated GLSL sources to the program collection. |
| `ShaderRenderCaseInstance::iterate()` | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Renders, builds the reference image, compares images, and returns the test status. |
| Reference image generation | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2719) | Defines vertex and fragment CPU reference construction. |
| Image comparison | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730) | Defines fuzzy image comparison and its threshold path. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1268) | Places `return` below the `glsl` test category. |
| Mustpass registration | [Vulkan](../../../mustpass/main/vk-default/glsl.txt#L14608-L14645), [Vulkan SC](../../../mustpass/main/vksc-default/glsl.txt#L13687-L13724) | Confirms the 38 registered leaves in both default lists. |
| Shader termination rule | [Vulkan Shaders chapter](../../../vulkan-docs/src/chapters/shaders.adoc#shaders-termination) | Provides the spec statement for `OpReturn` termination. |
