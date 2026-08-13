## Overview

**Core question:** Do fractional-even and fractional-odd tessellation produce the required segment count, length pattern, symmetry, and consistency across tessellation levels?

- `vktTessellationFractionalSpacingTests.cpp` implements the `tessellation.fractional_spacing` test family.
- Four test case leaves pair GLSL or HLSL with fractional-even or fractional-odd spacing.
- Each leaf draws a single isoline at 93 tessellation levels and captures every generated along-line coordinate in a storage buffer.
- Host verification checks each generated line and then compares observations across levels. This avoids assuming the implementation-dependent location of the two fractional segments.

## Background Knowledge

For the shared concepts primitive domains and spacing modes, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Fractional spacing.** Fractional-even spacing clamps a level `f` to `[2, maxTessellationGenerationLevel]` and rounds up to an even segment count `n`. Fractional-odd spacing clamps `f` to `[1, maxTessellationGenerationLevel - 1]` and rounds up to an odd `n`. For `n > 1`, Vulkan requires `n - 2` regular segments and two equal-length additional segments. The additional pair must be symmetric, and its relative length decreases as `n - f` grows.
- **Isoline coordinates.** An isoline evaluation invocation receives a normalized coordinate along the generated line. Capturing and sorting `TessCoord.x` reconstructs the endpoints and segment lengths without relying on invocation order or rasterized pixels.

## Registration Hierarchy

```text
tessellation.fractional_spacing
├── glsl_odd
├── glsl_even
├── hlsl_odd
└── hlsl_even
```

These are the four leaves registered directly under `tessellation.fractional_spacing`; the Vulkan default mustpass list includes all four paths.

## Parameter Dimensions and Observed Values

| Dimension | Values in this family | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader language | `glsl`, `hlsl` | Selects equivalent GLSL and HLSL program-generation and compiler paths. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L427-L559) |
| Spacing mode | `even`, `odd` | Selects fractional-even or fractional-odd clamping, parity rounding, and segment placement. | [`createFractionalSpacingTests()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L763-L777) |
| Runtime tessellation level | 30 generated values from `7.0` through `9.9`; 63 generated values from `0.3` through `62.3` | Exercises dense changes within nearby rounded levels, low-level clamping, and transitions across a wide level range. | [`genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L392-L411) |
| Point-size program | base TES, `tese_point_size` | In the GLSL path, `tese_point_size` adds `gl_PointSize = 1.0f` when `shaderTessellationAndGeometryPointSize` is enabled; the HLSL pair uses identical evaluation source for both binary names. Neither changes captured coordinates. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L464-L557), [`pipeline selection`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L645-L652) |

## Behavior Parameters

The primary behavioral axis is the spacing-mode suffix. It changes the legal input range, final segment-count parity, and low-level behavior. The language prefix checks a second source path for the same tessellator rules.

### `*_even`: fractional-even spacing

The test clamps `f` to at least `2` and rounds upward to an even `n`. Each capture must contain `n + 1` points. Single-line checks cover the length, symmetry, and endpoint rules; cross-level checks cover monotonicity and location consistency for determinable observations.

### `*_odd`: fractional-odd spacing

The test clamps `f` to at least `1` and rounds upward to an odd `n`. This group includes the `n = 1` case, where the line has one segment and no additional pair. Larger odd levels use the same structural and cross-level checks as the even group.

## Shader Analysis

The representative GLSL fractional-even case shows the observation stage. The control shader supplies one isoline and the current along-line tessellation level. The evaluation shader records each generated `gl_TessCoord.x`; the host derives spacing properties from those values.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.fractional_spacing.glsl_even
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `glsl` | Uses the GLSL program-generation path. |
| `even` | Emits `fractional_even_spacing`, so the tessellator rounds the along-line level upward to an even count. |
| base TES | Omits the optional point-size write because it does not affect the spacing observation. |

#### Purpose

The evaluation shader captures the coordinate of every point generated along one fractionally spaced isoline. An atomic counter assigns slots because the test does not assume invocation order.

#### Structural Design

| Stage | Operation | Observable effect |
|-------|-----------|-------------------|
| TCS | Writes `1.0` to the isoline-count outer level and the host-selected value to the along-line outer level. | Requests one line split by fractional-even spacing. |
| Tessellator | Generates point-mode positions along the isoline. | Supplies one `gl_TessCoord.x` per generated point. |
| TES | Atomically reserves an index and stores the coordinate. | Produces an unordered coordinate array and an invocation count for host verification. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(isolines, fractional_even_spacing, point_mode) in;

layout(set = 0, binding = 1, std430) restrict buffer Results {
    float data[];
} sb_out_tessCoord;
layout(set = 0, binding = 2, std430) coherent restrict buffer Counter {
    int data;
} sb_out_numInvocations;

void main (void)
{
    /// Reserve one result slot per tessellation evaluation invocation.
    int index = atomicAdd(sb_out_numInvocations.data, 1);
    /// Record the position along the single generated isoline.
    sb_out_tessCoord.data[index] = gl_TessCoord.x;
}
```

#### Additional Info

- The tessellation control shader reads binding 0, writes `gl_TessLevelOuter[0] = 1.0`, and copies the current level to `gl_TessLevelOuter[1]`.
- The attachmentless render pass makes storage-buffer data, rather than pixel output, the test result.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Spacing mode | Changes the GLSL layout qualifier between `fractional_even_spacing` and `fractional_odd_spacing`. | [`initPrograms()` GLSL TES branch](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L464-L494) |
| Shader language | Replaces GLSL built-ins and storage blocks with HLSL `SV_TessFactor`, `SV_DOMAINLOCATION`, `RWStructuredBuffer`, and `InterlockedAdd`. | [`initPrograms()` HLSL branch](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L496-L557) |
| Point-size requirement | Adds `GL_EXT_tessellation_point_size` and writes `gl_PointSize`; the HLSL collection selects a corresponding binary name without changing the shown HLSL source. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L464-L557) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 34
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord
               OpExecutionMode %main Isolines
               OpExecutionMode %main SpacingFractionalEven
               OpExecutionMode %main VertexOrderCcw
               OpExecutionMode %main PointMode
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %index "index"
               OpName %Counter "Counter"
               OpMemberName %Counter 0 "data"
               OpName %sb_out_numInvocations "sb_out_numInvocations"
               OpName %Results "Results"
               OpMemberName %Results 0 "data"
               OpName %sb_out_tessCoord "sb_out_tessCoord"
               OpName %gl_TessCoord "gl_TessCoord"
               OpDecorate %Counter BufferBlock
               OpMemberDecorate %Counter 0 Restrict
               OpMemberDecorate %Counter 0 Coherent
               OpMemberDecorate %Counter 0 Offset 0
               OpDecorate %sb_out_numInvocations Restrict
               OpDecorate %sb_out_numInvocations Coherent
               OpDecorate %sb_out_numInvocations Binding 2
               OpDecorate %sb_out_numInvocations DescriptorSet 0
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %Results BufferBlock
               OpMemberDecorate %Results 0 Restrict
               OpMemberDecorate %Results 0 Offset 0
               OpDecorate %sb_out_tessCoord Restrict
               OpDecorate %sb_out_tessCoord Binding 1
               OpDecorate %sb_out_tessCoord DescriptorSet 0
               OpDecorate %gl_TessCoord BuiltIn TessCoord
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
    %Counter = OpTypeStruct %int
%_ptr_Uniform_Counter = OpTypePointer Uniform %Counter
%sb_out_numInvocations = OpVariable %_ptr_Uniform_Counter Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %int_1 = OpConstant %int 1
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
      %float = OpTypeFloat 32
%_runtimearr_float = OpTypeRuntimeArray %float
    %Results = OpTypeStruct %_runtimearr_float
%_ptr_Uniform_Results = OpTypePointer Uniform %Results
%sb_out_tessCoord = OpVariable %_ptr_Uniform_Results Uniform
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
%_ptr_Input_float = OpTypePointer Input %float
%_ptr_Uniform_float = OpTypePointer Uniform %float
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_int Function
         %14 = OpAccessChain %_ptr_Uniform_int %sb_out_numInvocations %int_0
         %19 = OpAtomicIAdd %int %14 %uint_1 %uint_0 %int_1
               OpStore %index %19
         %25 = OpLoad %int %index
         %30 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %31 = OpLoad %float %30
         %33 = OpAccessChain %_ptr_Uniform_float %sb_out_tessCoord %int_0 %25
               OpStore %33 %31
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates three host-visible storage buffers: one float for the current level, a coordinate array sized for the largest final level, and one atomic counter.
- For each of 93 levels, the host uploads the level, clears the result and counter buffers, draws one patch, inserts a shader-write-to-host-read barrier for the result buffer, waits for completion, and invalidates the result and counter allocations.
- The host reads the counter as the coordinate count, sorts the captured floats, and runs [`verifyFractionalSpacingSingle()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L153-L294). It checks count, endpoints, at most two length groups using a `0.001` grouping tolerance, equal lengths at integral clamped levels, and symmetric placement of an identifiable additional pair.
- The verifier records the observed additional-segment length and location for every successful level. Negative values represent a one-segment line or a location that cannot be identified reliably.
- After all 93 draws pass, [`verifyFractionalSpacingMultiple()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L303-L390) compares determinable observations. Equal clamped levels must use equal locations, and additional-segment length must follow the required monotonic relation to `n - f` within one final rounded level.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `*_even` | Incorrect fractional-even level clamping or even rounding; wrong point count; invalid additional-segment lengths, symmetry, or cross-level consistency; or a failure in the selected GLSL/HLSL capture path. |
| `*_odd` | Incorrect fractional-odd level clamping or odd rounding, including the one-segment case; wrong point count; invalid additional-segment lengths, symmetry, or cross-level consistency; or a failure in the selected GLSL/HLSL capture path. |

### Cause Analysis

#### Fractional level interpretation and point generation

**Possible failure symptoms:** The captured point count differs from `n + 1`, endpoints are not `0.0` and `1.0`, or only the even or odd group fails near its clamping and parity boundaries.

**Possible implementation causes:** The tessellator may clamp the input against the wrong lower bound, round to the wrong parity, or generate a point count inconsistent with the final level. Fractional-even and fractional-odd rules come from the Vulkan tessellator-spacing requirements.

#### Additional-segment structure and cross-level behavior

**Possible failure symptoms:** A line has more than two segment-length classes, the additional pair is longer than the regular segments, its positions are not symmetric, identical clamped levels choose different determinable locations, or lengths violate the monotonic `n - f` relation.

**Possible implementation causes:** The tessellator may construct the fractional pair incorrectly or vary an implementation-dependent location where Vulkan requires consistency. A failure can also result from unstable coordinate generation across equivalent levels.

#### Shader-language capture or host readback

**Possible failure symptoms:** One language prefix fails for both spacing suffixes, or the host reads corrupt counts or coordinates across the level sequence.

**Possible implementation causes:** GLSL or HLSL compilation may lower the spacing mode, tessellation built-ins, storage-buffer writes, or atomic increment incorrectly. Descriptor binding, shader-write visibility, or host invalidation can also corrupt the observation path. The captured data alone does not localize those shared causes further.

## Case Pruning

### Requirement-based pruning

- The runtime requires tessellation shaders and vertex-pipeline storage-buffer stores and atomics.
- Portability-subset implementations must support isolines and point mode. Unsupported functionality yields a not-supported result instead of a spacing failure.

### Design-based pruning

- The family uses one isoline because it needs only a normalized edge whose subdivisions can be reconstructed from `TessCoord.x`.
- Shader language does not create separate behavior subsections because both languages capture the same spacing result.
- The 93 levels run inside each registered leaf instead of becoming separate test case leaves.
- Cross-level checks skip unknown locations and one-segment lengths rather than guessing which segments form the additional pair.

## Key Takeaways

- The family verifies specification properties instead of comparing against one fixed coordinate layout, because the exact symmetric location of the additional pair is implementation-dependent.
- Even and odd spacing differ in clamping, final parity, and the odd mode's one-segment case.
- Single-line checks cover count, endpoints, length classes, and symmetry. Cross-level checks cover monotonic length changes and location consistency.
- GLSL and HLSL cases apply the same host oracle to separate shader-language paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Single-line verification | [`verifyFractionalSpacingSingle()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L153-L294) | Defines point-count, endpoint, length-group, and symmetry checks. |
| Cross-level verification | [`verifyFractionalSpacingMultiple()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L303-L390) | Defines location-consistency and monotonic-length checks. |
| Runtime level generation | [`genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L392-L411) | Generates the 93 tested levels. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L427-L559) | Emits GLSL and HLSL programs for both spacing modes. |
| Runtime and readback | [`test()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L561-L744) | Creates resources, draws every level, and runs both verification phases. |
| Registration | [`createFractionalSpacingTests()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L763-L777) | Registers the four leaves. |
| CTS clamping and rounding helpers | [`vktTessellationUtil.cpp#L364-L407`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L364-L407) | Implements the reference lower bounds and parity rounding. |
| Mustpass coverage | [`tessellation.txt#L13-L16`](../../../mustpass/main/vk-default/tessellation.txt#L13-L16) | Lists all four registered paths. |
| Tessellator spacing rules | [`tessellation.adoc#tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing) | Specifies fractional clamping, rounding, segment lengths, symmetry, and consistency. |
