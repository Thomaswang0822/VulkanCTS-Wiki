## Overview

**Core question:** Do fragment output locations route each Amber-produced value to the intended color attachment across the registered array and shuffle cases?

`output_location` is a render-pass-only draw-test group for fragment output locations. Its registration code creates two Amber-backed families: `array`, which covers output arrays across attachment formats, precision qualifiers, and output types, and `shuffle`, which covers the `inputs-outputs` and `inputs-outputs-mod` location-mapping cases. The C++ wrapper registers the cases and attaches one portability-subset support check; the rendering and expected-result details live in the Amber data named by the wrapper.

## Background Knowledge

Fragment output locations map shader outputs to color attachment locations. Output arrays and shuffled locations exercise the correspondence between shader declarations and framebuffer attachments.

## Registration Hierarchy

The complete path is:

```text
draw.renderpass.output_location
├── array
└── shuffle
```

`createOutputLocationTests()` creates the `output_location` group through `createTestGroup()` ([source](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L127-L131)). The draw dispatcher adds that group only while building the render-pass branch and only when `CTS_USES_VULKANSC` is not defined and `useDynamicRendering` is false ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)). Therefore this page describes neither a Vulkan SC registration nor a dynamic-rendering variant.

The public entry point is declared in [`vktDrawOutputLocationTests.hpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.hpp#L27-L40), and the wrapper implementation is [`vktDrawOutputLocationTests.cpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L25-L135).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning |
|---|---|---|
| Family | `array`, `shuffle` | Selects output-array or output-location-shuffle coverage. |
| Array cases | 28 exact Amber identifiers | Vary format, precision, and explicit output type. |
| Shuffle cases | `inputs-outputs`, `inputs-outputs-mod` | Vary output-location mapping scripts. |

## Behavior Parameters

The primary behavioral axis is the registered family and its exact Amber case. The wrapper preserves those identifiers and delegates shader behavior and expected results to Amber.

### `array`: output-array declarations

The 28 cases vary attachment format, precision, and output type.

### `shuffle`: output-location mapping

The two cases exercise the corresponding location-shuffle Amber scripts.

## Shader Analysis

The registered cases use Amber-provided GLSL rather than a C++ shader generator. The two families have distinct fragment interfaces: `array` declares one location-0 array of three outputs, while `shuffle` declares three scalar/vector outputs and deliberately writes them in a different order. The representative walkthroughs below use the exact Amber sources and the compiler-produced SPIR-V for the central fragment stage.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.output_location.array.b8g8r8a8-unorm-highp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `array` | Selects the three-element fragment-output-array family and three color attachments at locations 0, 1, and 2. |
| `b8g8r8a8-unorm` | Makes each array element a `vec4` and compares the rendered attachment against a same-format reference image. |
| `highp` | Selects `highp` precision on the fragment output array; the matching input is smooth-interpolated. |
| `output` omitted | Uses the full `vec4` value from each array element rather than the `.x`, `.xy`, or `.xyz` projections used by output-type variants. |

#### Purpose

The vertex shader forwards three per-vertex colors through one location-0 array, and the fragment shader copies each array element into the corresponding output-array element. Amber binds those elements to three color attachments, then renders one reference pipeline per attachment and verifies every result image is green.

#### Structural Design

| Stage | Interface | Core operation | Observable result |
|-------|-----------|----------------|-------------------|
| Vertex | `color_in[3]` at location 1 to `color_out[3]` at location 0 | Copy all three array elements in a bounded loop. | Three independent interpolated values reach the fragment stage. |
| Fragment | `color_in[3]` at location 0 to `frag_out[3]` at location 0 | Copy `color_in[i]` to `frag_out[i]` for `i = 0..2`. | Output-array element `i` routes to color attachment location `i`. |
| Host comparison | `framebuffer0..2` versus `ref0..2` | Verification pipelines sample each result/reference pair. | Any missing, reordered, or incorrectly typed output makes the corresponding result red instead of green. |

#### Shader Code

##### Vertex Shader

```glsl
#version 430
/// Vertex positions are supplied at location 0 and determine the full-screen triangle-strip coverage.
layout(location = 0) in vec2 position_in;
/// Three per-vertex colors arrive as one array at location 1; the loop preserves each element's identity.
layout(location = 1) in vec4 color_in[3];
/// The color array is passed smoothly to the fragment stage at location 0.
layout(location = 0) smooth out vec4 color_out[3];

void main()
{
    /// Place the four input vertices in clip space without changing their color-array payload.
    gl_Position = vec4(position_in, 0, 1);
    for (int i = 0; i < 3; i++)
        color_out[i] = color_in[i];
}
```

##### Fragment Shader

```glsl
#version 430
/// One smooth-interpolated vec4 array is supplied at location 0 by the vertex stage.
layout(location = 0) smooth in vec4 color_in[3];
/// The three array elements occupy consecutive fragment output locations and are bound to three B8G8R8A8_UNORM attachments.
layout(location = 0) out highp vec4 frag_out[3];
void main()
{
    /// Preserve array-element identity: element i must be written to output location i.
    for (int i = 0; i < 3; i++)
        frag_out[i] = color_in[i];
}
```

#### Additional Info

- The exact Amber source also defines `vert_shader`, which assigns `gl_Position = vec4(position_in, 0, 1)` and copies `color_in[i]` to `color_out[i]`; this producer remains fixed across the 28 array cases ([source](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp.amber#L16-L32)).
- The three draw pipelines bind `framebuffer0`, `framebuffer1`, and `framebuffer2` as color locations 0, 1, and 2. Separate reference and verification pipelines make attachment routing observable rather than relying on a single combined image ([pipeline setup](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp.amber#L95-L167)).
- The source comparison is exact (`result != ref`): a mismatch writes red, while equality writes green; the final `EXPECT` requires green for each 60x60 result image ([verification shader](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp.amber#L64-L82), [expectations](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp.amber#L212-L214)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Attachment format | Selects the input/output scalar or vector type: `float`, `vec2`, `vec3`, `vec4`, or `uvec2`, matching the format family. | [array Amber files](../../../data/vulkan/amber/draw/output_location/array/) |
| Precision | Changes the fragment output precision between `highp` and `mediump`; integer cases use the same array-copy structure with flat integer inputs. | [highp example](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp.amber#L29-L35), [mediump example](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-mediump.amber#L29-L35), [uint example](../../../data/vulkan/amber/draw/output_location/array/r8g8-uint-highp.amber#L16-L31) |
| Explicit output type | Replaces the full assignment with `color_in[i].x`, `.xy`, or `.xyz` and changes the declared output type accordingly. | [vec2 variant](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp-output-vec2.amber#L29-L35), [vec3 variant](../../../data/vulkan/amber/draw/output_location/array/b8g8r8a8-unorm-highp-output-vec3.amber#L29-L35) |

#### SPIR-V

##### Vertex Shader

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
; Bound: 53
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %position_in %color_out %color_in
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpName %_ ""
               OpName %position_in "position_in"
               OpName %i "i"
               OpName %color_out "color_out"
               OpName %color_in "color_in"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpDecorate %position_in Location 0
               OpDecorate %color_out Location 0
               OpDecorate %color_in Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
%position_in = OpVariable %_ptr_Input_v2float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Function_int = OpTypePointer Function %int
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Output__arr_v4float_uint_3 = OpTypePointer Output %_arr_v4float_uint_3
  %color_out = OpVariable %_ptr_Output__arr_v4float_uint_3 Output
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
   %color_in = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
         %19 = OpLoad %v2float %position_in
         %22 = OpCompositeExtract %float %19 0
         %23 = OpCompositeExtract %float %19 1
         %24 = OpCompositeConstruct %v4float %22 %23 %float_0 %float_1
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
               OpStore %i %int_0
               OpBranch %29
         %29 = OpLabel
               OpLoopMerge %31 %32 None
               OpBranch %33
         %33 = OpLabel
         %34 = OpLoad %int %i
         %37 = OpSLessThan %bool %34 %int_3
               OpBranchConditional %37 %30 %31
         %30 = OpLabel
         %42 = OpLoad %int %i
         %45 = OpLoad %int %i
         %47 = OpAccessChain %_ptr_Input_v4float %color_in %45
         %48 = OpLoad %v4float %47
         %49 = OpAccessChain %_ptr_Output_v4float %color_out %42
               OpStore %49 %48
               OpBranch %32
         %32 = OpLabel
         %50 = OpLoad %int %i
         %52 = OpIAdd %int %50 %int_1
               OpStore %i %52
               OpBranch %29
         %31 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

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
; Bound: 38
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %frag_out %color_in
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 430
               OpName %main "main"
               OpName %i "i"
               OpName %frag_out "frag_out"
               OpName %color_in "color_in"
               OpDecorate %frag_out Location 0
               OpDecorate %color_in Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Output__arr_v4float_uint_3 = OpTypePointer Output %_arr_v4float_uint_3
   %frag_out = OpVariable %_ptr_Output__arr_v4float_uint_3 Output
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
   %color_in = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %i
         %18 = OpSLessThan %bool %15 %int_3
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %26 = OpLoad %int %i
         %29 = OpLoad %int %i
         %31 = OpAccessChain %_ptr_Input_v4float %color_in %29
         %32 = OpLoad %v4float %31
         %34 = OpAccessChain %_ptr_Output_v4float %frag_out %26
               OpStore %34 %32
               OpBranch %13
         %13 = OpLabel
         %35 = OpLoad %int %i
         %37 = OpIAdd %int %35 %int_1
               OpStore %i %37
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The wrapper uses the Amber data directory `draw/output_location/array` and registers 28 case names. Each name becomes both the test-case identifier and the `.amber` filename passed to `createAmberTestCase()` ([registration](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L56-L100)). The names encode the attachment format, precision, and, where present, an explicit output type:

| Format encoded by case name | Precision | Registered cases |
|---|---|---|
| `b10g11r11-ufloat-pack32` | `highp` | `b10g11r11-ufloat-pack32-highp`, `b10g11r11-ufloat-pack32-highp-output-float`, `b10g11r11-ufloat-pack32-highp-output-vec2` |
| `b10g11r11-ufloat-pack32` | `mediump` | `b10g11r11-ufloat-pack32-mediump`, `b10g11r11-ufloat-pack32-mediump-output-float`, `b10g11r11-ufloat-pack32-mediump-output-vec2` |
| `b8g8r8a8-unorm` | `highp` | `b8g8r8a8-unorm-highp`, `b8g8r8a8-unorm-highp-output-vec2`, `b8g8r8a8-unorm-highp-output-vec3` |
| `b8g8r8a8-unorm` | `mediump` | `b8g8r8a8-unorm-mediump`, `b8g8r8a8-unorm-mediump-output-vec2`, `b8g8r8a8-unorm-mediump-output-vec3` |
| `r16g16-sfloat` | `highp` | `r16g16-sfloat-highp`, `r16g16-sfloat-highp-output-float` |
| `r16g16-sfloat` | `mediump` | `r16g16-sfloat-mediump`, `r16g16-sfloat-mediump-output-float` |
| `r32g32b32a32-sfloat` | `highp` | `r32g32b32a32-sfloat-highp`, `r32g32b32a32-sfloat-highp-output-vec2`, `r32g32b32a32-sfloat-highp-output-vec3` |
| `r32g32b32a32-sfloat` | `mediump` | `r32g32b32a32-sfloat-mediump`, `r32g32b32a32-sfloat-mediump-output-vec2`, `r32g32b32a32-sfloat-mediump-output-vec3` |
| `r32-sfloat` | `highp` | `r32-sfloat-highp` |
| `r32-sfloat` | `mediump` | `r32-sfloat-mediump` |
| `r8g8-uint` | `highp` | `r8g8-uint-highp`, `r8g8-uint-highp-output-uint` |
| `r8g8-uint` | `mediump` | `r8g8-uint-mediump`, `r8g8-uint-mediump-output-uint` |

The source supplies names rather than a C++ parameter object or generated case matrix. Consequently, the exact output declarations, draw commands, and expected pixels must be read from the corresponding Amber scripts; they should not be inferred from the filename alone.

### `shuffle` family

The wrapper uses `draw/output_location/shuffle` and registers exactly two Amber cases ([source](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L103-L118)):

| Case | Registered Amber file |
|---|---|
| `inputs-outputs` | `inputs-outputs.amber` |
| `inputs-outputs-mod` | `inputs-outputs-mod.amber` |

The family is intended by its registration name to exercise output-location shuffling. The C++ wrapper itself does not describe the shader interface or expected image; those details belong to the Amber inputs.

### End-to-end registration flow

1. The draw root creates a `renderpass` branch and several dynamic-rendering branches with `GroupParams` ([root setup](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L199)).
2. `createChildren()` reaches `createOutputLocationTests(testCtx)` only inside the non-VulkanSC block and the `!useDynamicRendering` condition ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)).
3. `createOutputLocationTests()` calls `createTestGroup(testCtx, "output_location", createTests)` ([wrapper](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L127-L131)).
4. `createTests()` creates `array` and `shuffle`, then calls `cts_amber::createAmberTestCase()` with the exact case name, data directory, and `<case>.amber` filename ([array](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L56-L100), [shuffle](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L103-L118)).
5. Every `array` case receives `checkSupport`; `shuffle` cases do not ([support assignment](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L92-L99), [shuffle loop](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L110-L117)). Amber owns execution and comparison after the wrapper has registered the test case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible implementation cause(s) |
|---|---|
| `array` case | Output declaration, format conversion, precision, Amber pipeline setup, or attachment mapping. |
| `shuffle` case | Location mapping, shader interface, Amber execution, or attachment validation. |

### Cause Analysis

#### Shader interface and attachment mapping

**Possible failure symptoms:** An Amber expected result comparison fails for one case family or format.

**Possible implementation causes:** Shader output declaration, location assignment, format conversion, pipeline interface, or attachment handling.

## Case Pruning

### Requirement-based pruning

Array cases can be skipped by the portability-subset and alignment gate in the wrapper.

### Design-based pruning

The dispatcher excludes the group for VulkanSC and dynamic-rendering paths.

Support and pruning details:

There are two independent registration gates:

- **Vulkan SC:** `createTests()` is compiled out under `CTS_USES_VULKANSC`; the fallback only marks the group parameter unused ([guard](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L51-L54), [fallback](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L120-L122)).
- **Dynamic rendering:** the dispatcher does not add this group when `useDynamicRendering` is true ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)). This is a registration limitation of the Amber group, not a per-case runtime failure.

For `array` cases, `checkSupport()` raises `NotSupportedError` when all of the following hold: `VK_KHR_portability_subset` is supported, `minVertexInputBindingStrideAlignment == 4`, and the case name contains `r8g8` or `inputs-outputs-mod` ([checkSupport](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L40-L48)). Because the callback is attached only in the `array` loop, the `inputs-outputs-mod` condition is present in the shared callback but is not applied to the `shuffle` case by this wrapper. The `shuffle` family has no support callback in this file.

A `NotSupportedError` from this callback means the case was pruned for the declared portability-subset stride constraint; it is not a rendering failure. Other Amber execution or image-comparison failures indicate a failure in the behavior encoded by the relevant Amber script or in the implementation path exercised by it.

Mustpass cross-check:

The default Vulkan draw mustpass lists the registered path under `draw.renderpass.output_location`, including the `array` and `shuffle` cases ([`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28946-L28975)). The mustpass names are the compatibility-sensitive identifiers; they should remain exactly as registered in the C++ arrays.

Source evidence:

- [`vktDrawOutputLocationTests.cpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L40-L131): support callback, family groups, exact case arrays, Amber registration, and public group creation.
- [`vktDrawOutputLocationTests.hpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.hpp#L27-L40): public declaration.
- [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121): dispatcher and render-pass/dynamic-rendering gating.
- [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28946-L28975): default mustpass registration evidence.

## Key Takeaways

- The exact hierarchy is `draw.renderpass.output_location.{array,shuffle}`.
- `array` contains 28 Amber cases; `shuffle` contains `inputs-outputs` and `inputs-outputs-mod`.

## Source Reference Appendix

The wrapper, dispatcher, Amber data, and mustpass references cited above form the source reference map for this registration-only family.
- The group is excluded from Vulkan SC and is not registered in dynamic-rendering branches.
- The portability-subset callback applies to every `array` case and can prune matching names under the stated stride condition; the wrapper does not attach it to `shuffle`.
- The C++ file is a registration and support-policy wrapper. Shader behavior and expected results are defined by the Amber data files named by each case.
