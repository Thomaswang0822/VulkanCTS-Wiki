## Overview

**Core question:** Do GLSL ES 3.10 vertex and fragment shaders execute each generated `switch` form with the expected selection, fall-through, scope, and nested-control-flow behavior?

- [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L505) implements the `glsl.switch` test family with 21 switch-body templates.
- Each template varies the selector source and shader stage. The shader converts the selected path into a coordinate swizzle, and the shared `ShaderRenderCase` harness compares the rendered color with a CPU reference.
- The templates cover ordinary labels, constant-expression labels, `default` placement or omission, fall-through, local scope, and combinations of switches with conditionals, loops, and another switch.
- The family registers 122 test case leaves in both the Vulkan and Vulkan SC default mustpass lists.

## Background Knowledge

- A GLSL `switch` selects a matching `case` label from an integral selector. If no label matches, execution starts at `default` when one exists; otherwise the switch body performs no selected statement.
- A `case` or `default` label does not end execution. Statements continue into later labeled sections until a `break` exits the switch or another control-flow statement changes execution. Several templates depend on this fall-through rule.
- Vertex variants compute a color before rasterization and pass it to the fragment shader. Fragment variants pass coordinates through the vertex shader and execute the tested switch for each fragment. This stage placement changes where the control flow runs without changing the expected color contract.

## Registration Hierarchy

`createSwitchTests()` creates the `switch` test family, and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1267-L1270) places it under the `glsl` test category. `ShaderSwitchTests::init()` adds every executable leaf directly below `glsl.switch`; there are no intermediate nodes.

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

The Vulkan and Vulkan SC default mustpass lists contain the same 122 normalized leaves ([Vulkan](../../../mustpass/main/vk-default/glsl.txt#L14913-L15034), [Vulkan SC](../../../mustpass/main/vksc-default/glsl.txt#L13851-L13972)).

## Parameter Dimensions and Observed Values

A test case name follows `<behavior>_<selector_source>_<stage>`. The first dimension chooses the switch-body template; the remaining two dimensions select the condition expression and the stage that executes it.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Behavior family | `basic`, `const_expr_in_label`, `default_label`, `default_not_last`, `no_default_label`, `default_only`, `empty_case_default`, `fall_through`, `fall_through_default`, `conditional_fall_through`, `conditional_fall_through_2`, `scope`, `switch_in_if`, `switch_in_for_loop`, `switch_in_while_loop`, `switch_in_do_while_loop`, `if_in_switch`, `for_loop_in_switch`, `while_loop_in_switch`, `do_while_loop_in_switch`, `switch_in_switch` | Selects the switch layout or the surrounding control-flow structure. | [`ShaderSwitchTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L498) |
| Selector source | `static`, `uniform`, `dynamic` | Substitutes `${CONDITION}` with literal `2`, uniform `ui_two`, or `int(floor(coords.z*1.5 + 2.0))`. | [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L150-L179), [`makeSwitchCases()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L221) |
| Shader stage | `vertex`, `fragment` | Executes the generated switch body in the selected stage. The other stage forwards either the computed color or the input coordinates. | [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L114-L172) |
| Uniform value | `ui_two = 2` for `uniform` selectors | Delivers the same selector value as the static form through a `std140` uniform block at set 0, binding 0. | [`setUniforms()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L47), [uniform declaration](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L135-L136) |

Nineteen behavior families use all three selector sources and both stages, which produces 19 × 3 × 2 = 114 leaves. `default_only` and `empty_case_default` use only static and uniform selectors, adding 2 × 2 × 2 = 8 leaves. The complete matrix therefore contains 122 leaves.

## Behavior Parameters

The primary behavioral axis is the behavior family at the start of each test case name. Selector source and shader stage repeat that behavior under different condition delivery and execution placement.

### `basic`: ordinary labels and breaks

Four literal labels map selector values 0 through 3 to `xyz`, `wzy`, `yzw`, and `zyx`. Every selected body ends with `break`, giving the baseline switch behavior ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L232-L239)).

### `const_expr_in_label`: constant-expression labels

The labels use `int(0.0)`, `2-1`, `3&(1<<1)`, and `t+1` instead of plain literals. They evaluate to 0 through 3 and must select the same swizzles as `basic` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L241-L249)).

### `default_label`: matching through a final default

The switch omits `case 2`. Selector value 2 reaches the final `default` body and writes `coords.yzw` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L251-L258)).

### `default_not_last`: default between ordinary labels

The `default` label appears after `case 0` and before `case 1` and `case 3`. Its position must not change selection for selector value 2 ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L260-L267)).

### `no_default_label`: no matching label

The template initializes `res` to `coords.yzw`, omits both `case 2` and `default`, and checks that a selector value of 2 leaves the initialized result unchanged ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L269-L276)).

### `default_only`: switch with only a default label

The body has no ordinary cases. Static and uniform selector values must enter `default` and write `coords.yzw` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L278-L285)).

### `empty_case_default`: empty case falling into default

`case 2` contains no statements or `break`, so execution continues into `default` and writes `coords.yzw` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L287-L295)).

### `fall_through`: case falling into a later ordinary case

`case 2` rotates `coords` to `yzwx` and then falls through to `case 4`, which copies the first three components into `res`. The result remains the expected original `yzw` swizzle ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L297-L305)).

### `fall_through_default`: case falling into default

`case 2` rotates `coords` and falls into a trailing `default` body. The template checks fall-through into `default`, rather than selection of `default` because no case matched ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L307-L315)).

### `conditional_fall_through`: conditional break after shared work

`case 2` prepares `tmp`, falls into `case 3`, writes `res`, and takes a conditional `break` when the selector is not 3. If that break is not taken, execution continues into `default` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L317-L330)).

### `conditional_fall_through_2`: fall-through after changing a local selector

This form stores the selector in local integer `c`. On `case 2`, it adds the original condition to `c`, falls through, and breaks when `c == 4`, checking data flow across labeled sections as well as conditional fall-through ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L332-L347)).

### `scope`: case-local block scope

`case 2` opens a block, declares local vector `t`, assigns it to `res`, and breaks inside the block. The case checks declarations and control flow inside a scoped labeled section ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L349-L361)).

### `switch_in_if`: switch nested in a conditional

A nonnegative-condition `if` encloses the baseline four-case switch. The generated selector values satisfy the outer condition, so the selected switch case determines the color ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L363-L373)).

### `switch_in_for_loop`: switch executed across for-loop iterations

A `for` loop advances `i` from 0 through the selected condition. Each iteration switches on `i` and overwrites `res`; the final executed iteration determines the expected swizzle ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L375-L385)).

### `switch_in_while_loop`: switch executed across while-loop iterations

This template implements the same repeated switch with an explicit `while` condition and increment. It checks the loop's condition, increment, and switch execution together ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L387-L399)).

### `switch_in_do_while_loop`: switch executed across do-while iterations

The body switches on `i`, increments it, and tests the loop condition afterward. For the generated selector range, the last iteration still determines the expected swizzle ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L401-L413)).

### `if_in_switch`: conditional selection inside default

Cases 0 and 1 handle their selectors directly. Other selector values enter `default`, where an `if` distinguishes selector 2 from the remaining values and chooses `yzw` or `zyx` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L415-L426)).

### `for_loop_in_switch`: for loop inside shared cases

Cases 1 and 2 share a scoped body. A `for` loop reverses local vector `t` once per selector count, and the body then writes the resulting value and breaks ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L428-L442)).

### `while_loop_in_switch`: while loop inside shared cases

This form uses an explicit counter and `while` loop in the shared body for cases 1 and 2. Repeated reversal must produce the same selector-dependent result as the corresponding `for` form ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L444-L462)).

### `do_while_loop_in_switch`: do-while loop inside shared cases

The shared case body reverses `t` before checking `i < ${CONDITION}`. The registered selectors entering this body are 1 and 2, so each executes the intended positive number of reversals ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L464-L482)).

### `switch_in_switch`: nested switch selection

Cases 1 and 2 of the outer switch enter an inner switch on `${CONDITION} - 1`. The inner labels distinguish those two outer selector values and write `wzy` or `yzw` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L484-L497)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.switch.basic_dynamic_fragment
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` | Selects the baseline four-label switch body. Labels 0 through 3 each write a distinct coordinate swizzle and end with `break`, directly exposing ordinary label selection and non-fall-through behavior ([registration body](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L232-L239)). |
| `dynamic` | Specializes `${CONDITION}` to `int(floor(coords.z*1.5 + 2.0))`, so the switch selector is computed from the per-fragment interpolated coordinate rather than fixed source text or a uniform ([specialization](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L150-L157)). |
| `fragment` | Makes the fragment shader the selected execution stage. The vertex shader only forwards `a_coords` through `v_coords`, while the fragment shader owns `coords`, `res`, the switch, and `o_color` ([stage branches](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L114-L172)). |

#### Purpose

This case checks that a dynamically computed fragment-stage integer selects the correct ordinary GLSL switch label and that each `break` preserves the selected coordinate swizzle in the rendered color.

#### Structural Design

| Dataflow step | Exact representative behavior |
|---------------|-------------------------------|
| Vertex inputs | Location 0 `a_position` becomes `gl_Position`; location 1 `a_coords` is forwarded unchanged. |
| Stage transport | The fixed vertex shader writes high-precision `v_coords` at location 0, which the rasterizer interpolates for the fragment shader. |
| Dynamic selection | The fragment shader computes `int(floor(coords.z*1.5 + 2.0))`. |
| Switch result | Labels `0`, `1`, `2`, and `3` select `xyz`, `wzy`, `yzw`, and `zyx`; every labeled body breaks. An unmatched value leaves initialized `res` at zero. |
| Observable result | `o_color = vec4(res, 1.0)` writes the selected RGB swizzle with opaque alpha for comparison against `evalSwitchDynamic()`. |

#### Shader Code

##### Fragment Shader (primary)

```glsl
#version 310 es
layout(location = 0) out mediump vec4 o_color;
/// High-precision coordinates arrive from the fixed pass-through vertex shader at location 0; the shared
/// fragment-case harness interpolates them across its quad grid.
layout(location = 0) in highp vec4 v_coords;

void main (void)
{
    /// The generated setup copies the stage input into a local and initializes the observable RGB result.
    highp vec4 coords = v_coords;
    mediump vec3 res = vec3(0.0);

    /// The dynamic selector is computed per fragment from interpolated coords.z. Each matched label writes
    /// a distinct swizzle, and break prevents fall-through in this basic behavior family.
    switch (int(floor(coords.z*1.5 + 2.0)))
    {
        case 0: res = coords.xyz;    break;
        case 1: res = coords.wzy;    break;
        case 2: res = coords.yzw;    break;
        case 3: res = coords.zyx;    break;
    }

    /// RGB exposes the selected branch; alpha is fixed to 1.0 for image comparison.
    o_color = vec4(res, 1.0);
}
```

##### Vertex Shader (secondary)

```glsl
#version 310 es
/// Location 0 supplies clip-space position and location 1 supplies the test coordinates from the shared quad grid.
layout(location = 0) in highp vec4 a_position;
layout(location = 1) in highp vec4 a_coords;

/// The fragment variant's fixed vertex stage transports coordinates at location 0 without applying test logic.
layout(location = 0) out highp vec4 v_coords;

void main (void)
{
    gl_Position = a_position;
    v_coords = a_coords;
}
```

#### Additional Info

- The secondary vertex shader stays fixed across all fragment-stage leaves: it only supplies position and forwards coordinates, but it is shown because its location-0 varying is the fragment shader's dynamic-selector input ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L118-L132), [fragment-stage epilogue](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L165-L169)).
- `makeSwitchCases()` registers this exact leaf by combining `basic`, the `dynamic` selector name, and the `fragment` stage; `createSwitchTests()` contributes the `switch` group under the package's `glsl` group ([leaf construction](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L220), [group factory](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L505), [package registration](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1270)). `initPrograms()` submits the generated pair with default `ShaderBuildOptions`, whose `targetVersion` is SPIR-V 1.0 ([program insertion](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625), [default options](../../../framework/vulkan/vkShaderProgram.hpp#L67-L73)).
- This dynamic case installs `evalSwitchDynamic()` and no uniform setup callback, so the selector has no descriptor-backed resource. The shared runner supplies quad-grid position and coordinate inputs at locations 0 and 1 as `VK_FORMAT_R32G32B32A32_SFLOAT`, renders to its default `VK_FORMAT_R8G8B8A8_UNORM` color target, evaluates the same mapping at fragment-reference pixel centers, and compares the images with threshold `0.2f` ([case factory](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L174-L179), [default instance state](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683), [vertex inputs](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1837-L1856), [fragment reference and comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2730)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Behavior family | Replaces the baseline switch body with another registered label, fall-through, scope, loop, conditional, or nested-switch template while retaining the common stage wrapper. | [`ShaderSwitchTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L498) |
| Selector source | `static` substitutes literal `2`; `uniform` substitutes `ui_two` and adds a set 0, binding 0 `std140` uniform block to the selected stage; `dynamic` uses the coordinate-derived expression shown here. | [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L135-L157) |
| Shader stage | A vertex variant executes the generated body from `a_coords`, writes `v_color`, and uses a pass-through fragment shader; this fragment variant forwards `a_coords` as `v_coords` and executes the body per fragment. | [`makeSwitchCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L114-L172) |

#### SPIR-V

##### Fragment Shader (primary)

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
; Bound: 56
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %v_coords %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %coords "coords"
               OpName %v_coords "v_coords"
               OpName %res "res"
               OpName %o_color "o_color"
               OpDecorate %v_coords Location 0
               OpDecorate %res RelaxedPrecision
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %50 RelaxedPrecision
               OpDecorate %52 RelaxedPrecision
               OpDecorate %53 RelaxedPrecision
               OpDecorate %54 RelaxedPrecision
               OpDecorate %55 RelaxedPrecision
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %v_coords = OpVariable %_ptr_Input_v4float Input
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %float_0 = OpConstant %float 0
         %17 = OpConstantComposite %v3float %float_0 %float_0 %float_0
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_ptr_Function_float = OpTypePointer Function %float
  %float_1_5 = OpConstant %float 1.5
    %float_2 = OpConstant %float 2
        %int = OpTypeInt 32 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %coords = OpVariable %_ptr_Function_v4float Function
        %res = OpVariable %_ptr_Function_v3float Function
         %12 = OpLoad %v4float %v_coords
               OpStore %coords %12
               OpStore %res %17
         %21 = OpAccessChain %_ptr_Function_float %coords %uint_2
         %22 = OpLoad %float %21
         %24 = OpFMul %float %22 %float_1_5
         %26 = OpFAdd %float %24 %float_2
         %27 = OpExtInst %float %1 Floor %26
         %29 = OpConvertFToS %int %27
               OpSelectionMerge %34 None
               OpSwitch %29 %34 0 %30 1 %31 2 %32 3 %33
         %30 = OpLabel
         %35 = OpLoad %v4float %coords
         %36 = OpVectorShuffle %v3float %35 %35 0 1 2
               OpStore %res %36
               OpBranch %34
         %31 = OpLabel
         %38 = OpLoad %v4float %coords
         %39 = OpVectorShuffle %v3float %38 %38 3 2 1
               OpStore %res %39
               OpBranch %34
         %32 = OpLabel
         %41 = OpLoad %v4float %coords
         %42 = OpVectorShuffle %v3float %41 %41 1 2 3
               OpStore %res %42
               OpBranch %34
         %33 = OpLabel
         %44 = OpLoad %v4float %coords
         %45 = OpVectorShuffle %v3float %44 %44 2 1 0
               OpStore %res %45
               OpBranch %34
         %34 = OpLabel
         %50 = OpLoad %v3float %res
         %52 = OpCompositeExtract %float %50 0
         %53 = OpCompositeExtract %float %50 1
         %54 = OpCompositeExtract %float %50 2
         %55 = OpCompositeConstruct %v4float %52 %53 %54 %float_1
               OpStore %o_color %55
               OpReturn
               OpFunctionEnd
```

</details>

##### Vertex Shader (secondary)

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
; Bound: 21
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %a_position %v_coords %a_coords
               OpSource ESSL 310
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %a_position "a_position"
               OpName %v_coords "v_coords"
               OpName %a_coords "a_coords"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %a_position Location 0
               OpDecorate %v_coords Location 0
               OpDecorate %a_coords Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %a_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %v_coords = OpVariable %_ptr_Output_v4float Output
   %a_coords = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %a_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %20 = OpLoad %v4float %a_coords
               OpStore %v_coords %20
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each leaf is a `ShaderSwitchCase` derived from the shared `ShaderRenderCase`. The case stores the generated vertex and fragment source, selects the CPU evaluator, and installs a uniform callback only for uniform variants ([case construction](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L51-L70), [case factory](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L174-L179)).
- Static and uniform evaluators expect `coords.yzw` because their selector is always 2. The dynamic evaluator applies the shader's floor expression and maps values 0, 1, 2, and 3 to `xyz`, `wzy`, `yzw`, and `zyx`; its fallback is `xxx` ([evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L81-L109)).
- The shared runner creates a quad grid, renders the generated program, copies the result image to host-visible storage, and builds a CPU reference. Vertex references evaluate grid vertices and interpolate their colors; fragment references evaluate pixel centers ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [vertex reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2690), [fragment reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2719)).
- The default `ShaderRenderCaseInstance` path uses fuzzy comparison. `iterate()` compares the rendered and reference images with error threshold `0.2f`, returning `pass("Result image matches reference")` or `fail("Image mismatch")` ([comparison selection](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683), [image comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L799-L805), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `basic` | Ordinary case selection, `break`, selector delivery, stage execution, or the shared render path differs from the reference. |
| `const_expr_in_label` | A constant-expression label is evaluated or matched incorrectly, or the shared render path differs from the reference. |
| `default_label` | Unmatched selection does not execute the final `default` body as expected. |
| `default_not_last` | `default` placement incorrectly changes label selection or subsequent control flow. |
| `no_default_label` | An unmatched switch changes the initialized result when no `default` exists. |
| `default_only` | A switch containing only `default` does not execute its body for the fixed selector. |
| `empty_case_default` | The empty `case 2` body does not fall through into `default`. |
| `fall_through` | Execution does not continue from `case 2` into the later ordinary case with the expected data. |
| `fall_through_default` | Execution does not continue from `case 2` into `default` with the expected data. |
| `conditional_fall_through` | Shared labeled work or the conditionally executed `break` produces the wrong path. |
| `conditional_fall_through_2` | Local selector updates, shared labeled work, or the conditional `break` produces the wrong path. |
| `scope` | Case-local declaration, assignment, or `break` handling produces the wrong result. |
| `switch_in_if` | The outer conditional or nested switch produces the wrong selection. |
| `switch_in_for_loop` | Repeated switch execution or final for-loop iteration produces the wrong swizzle. |
| `switch_in_while_loop` | Repeated switch execution, while condition, or increment produces the wrong swizzle. |
| `switch_in_do_while_loop` | Repeated switch execution or do-while condition ordering produces the wrong swizzle. |
| `if_in_switch` | The conditional inside `default` distinguishes selector values incorrectly. |
| `for_loop_in_switch` | Shared case entry or the nested for loop performs the wrong number of reversals. |
| `while_loop_in_switch` | Shared case entry or the nested while loop performs the wrong number of reversals. |
| `do_while_loop_in_switch` | Shared case entry or the nested do-while loop performs the wrong number of reversals. |
| `switch_in_switch` | The outer shared cases or inner selector mapping produces the wrong swizzle. |

Every row also depends on the selected `static`, `uniform`, or `dynamic` condition path, the selected shader stage, and the common image-based harness.

### Cause Analysis

#### Switch selection and label control flow

**Possible failure symptoms:** The rendered pixels contain a coordinate swizzle from the wrong labeled section, preserve the initial zero or `yzw` value when a body should run, or apply an unexpected fall-through body.

**Possible implementation causes:** The generated sources isolate label matching, `default`, `break`, fall-through, constant-expression labels, and case-local scope in separate behavior families. A mismatch can indicate incorrect GLSL compilation or execution of the specific switch form. The image result identifies the observable wrong path but does not identify the compiler or execution component responsible.

#### Nested conditional and loop control flow

**Possible failure symptoms:** A nesting case returns the swizzle for the wrong iteration, performs the wrong number of vector reversals, or follows the wrong inner conditional or switch branch.

**Possible implementation causes:** The templates combine switches with `if`, `for`, `while`, `do-while`, or another switch. The failing leaf narrows the affected source shape, but the final color can result from more than one control-flow error inside that shape. Source-level investigation is needed to separate switch lowering from surrounding loop or conditional behavior.

#### Selector and stage delivery

**Possible failure symptoms:** Failures cluster by `uniform` or `dynamic` suffix, or occur only in the vertex or fragment variants of otherwise identical behavior families.

**Possible implementation causes:** A uniform-only cluster can involve the set 0, binding 0 value or its use as the selector. A dynamic-only cluster can involve the floor expression or coordinate delivery. A stage-only cluster can involve selected-stage execution or the vertex-to-fragment interface. The shared oracle does not isolate these paths from shader compilation and rendering.

#### Shared rendering and comparison

**Possible failure symptoms:** The case reports `Image mismatch`, potentially across unrelated switch behaviors or selector sources.

**Possible implementation causes:** The common path includes shader compilation, graphics pipeline setup, vertex input, varying interpolation, rasterization, image copyback, CPU reference construction, and fuzzy comparison. The switch source does not independently validate those mechanisms, so a failure across many behavior families may require investigation of the complete `ShaderRenderCase` path.

## Case Pruning

### Requirement-based pruning

The switch implementation has no switch-specific `checkSupport()` override, extension predicate, feature query, or device-limit filter. It registers the family unconditionally for the GLSL package and relies on the common shader-render setup and GLSL ES 3.10 compilation path. Shared CTS setup can still reject an unsupported configuration, but the source defines no additional switch-family requirement.

### Design-based pruning

`default_only` and `empty_case_default` pass `skipDynamicType = true` to `makeSwitchCases()`, so neither family registers dynamic vertex or fragment leaves ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L278-L295), [pruning condition](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L220)). All other behavior families register all three selector sources in both stages. The source does not state why those two dynamic combinations are omitted, so the omission should be treated as an explicit matrix-design choice rather than a support restriction.

## Key Takeaways

- The family turns switch control flow into visible coordinate swizzles, allowing the shared render harness to compare each generated path with a CPU evaluator.
- The 21 behavior families separate ordinary selection, label forms, `default`, fall-through, scope, and nested control-flow structures. Selector source and stage then repeat each applicable behavior under a different delivery or execution path.
- Static and uniform selectors both resolve to 2; the dynamic shader and evaluator use the same floor expression and map selector values 0 through 3 to the four expected swizzles.
- The 122-leaf matrix is complete in both default mustpass lists. The only design-based omission is the dynamic selector for `default_only` and `empty_case_default`.
- A failure establishes an observable mismatch in the generated shader and render path. The behavior, selector, and stage suffixes narrow investigation, but they do not prove a specific compiler, interface, rasterization, uniform, or harness defect; see `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Uniform setup and CPU evaluators | [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L44-L109) | Defines the fixed uniform and expected static, uniform, and dynamic colors. |
| `makeSwitchCase()` | [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L111-L180) | Generates the stage interfaces, condition expression, switch body, and color output. |
| `ShaderSwitchTests::makeSwitchCases()` | [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L205-L222) | Defines leaf naming, selector iteration, stage iteration, and dynamic pruning. |
| `ShaderSwitchTests::init()` | [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L224-L498) | Defines all 21 switch-body templates and registers their leaves. |
| `createSwitchTests()` | [`vktShaderRenderSwitchTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L505) | Creates the `switch` test family. |
| Public factory declaration | [`vktShaderRenderSwitchTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.hpp#L23-L36) | Declares `createSwitchTests()`. |
| GLSL test category registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1270) | Adds `glsl.switch` to the test package without a switch-specific build guard. |
| Shared shader and instance setup | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L577-L633) | Installs the generated programs and creates the common render instance. |
| Shared render and image comparison | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) | Renders, builds the CPU reference, compares images, and reports pass or failure. |
| Reference-image construction | [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2719) | Shows the distinct vertex and fragment reference paths. |
| Vulkan default coverage | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L14913-L15034) | Lists all 122 `dEQP-VK.glsl.switch` leaves. |
| Vulkan SC default coverage | [`glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L13851-L13972) | Lists all 122 `dEQP-VKSC.glsl.switch` leaves. |
