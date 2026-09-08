## Overview

**Core question:** Does a fragment shader use of `gl_SampleID`, `gl_SamplePosition`, or a `sample`-decorated input force implicit sample-rate shading when pipeline sample shading is disabled?

- The [`implicit_sample_shading`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L501-L553) test family contains three fragment-shader trigger mechanisms, each registered as one base leaf plus three `minSampleShadingValue_*` override leaves.
- Each case renders one full-screen triangle into a 4 × 4, four-sample color attachment and increments a fragment-storage atomic counter.
- Base leaves set `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0`; override leaves enable pipeline sample shading with `minSampleShading` 0.0, 0.25, or 0.5. The host verdict requires at least 64 counter increments for every leaf, demonstrating one invocation per covered sample even when the configured shading rate is below 1.0.
- The same implementation is registered under the render-pass path and the three non-nested dynamic-rendering paths; nested dynamic-rendering paths omit it because the draw dispatcher excludes this family for nested command buffers.

## Background Knowledge

- **Sample shading:** A multisample fragment can be shaded once per pixel or once for each covered sample. Vulkan permits implicit sample shading when a fragment shader statically uses `SampleID` or `SamplePosition`, and gives a `sample`-decorated input the corresponding sample-rate behavior. See [sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading).
- **Fragment shader interface decorations:** `SampleID` identifies the sample for a sample-rate invocation, `SamplePosition` provides that sample's position, and the `sample` decoration selects sample interpolation for an input. These are shader interface semantics, not additional host-created resources. See [fragment shader inputs](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput).

## Registration Hierarchy

The dispatcher adds this family whenever `nestedSecondaryCmdBuffer` is false. [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) creates the render-pass and dynamic-rendering modes, while [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) registers this family only in the four non-nested ownership roots shown below.

```text
draw.renderpass.implicit_sample_shading
├── sample_decoration_dynamic_use
├── minSampleShadingValue_zero_sample_decoration_dynamic_use
├── minSampleShadingValue_quarter_sample_decoration_dynamic_use
├── minSampleShadingValue_half_sample_decoration_dynamic_use
├── sample_id_static_use
├── minSampleShadingValue_zero_sample_id_static_use
├── minSampleShadingValue_quarter_sample_id_static_use
├── minSampleShadingValue_half_sample_id_static_use
├── sample_position_static_use
├── minSampleShadingValue_zero_sample_position_static_use
├── minSampleShadingValue_quarter_sample_position_static_use
└── minSampleShadingValue_half_sample_position_static_use

draw.dynamic_rendering.primary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── minSampleShadingValue_zero_sample_decoration_dynamic_use
├── minSampleShadingValue_quarter_sample_decoration_dynamic_use
├── minSampleShadingValue_half_sample_decoration_dynamic_use
├── sample_id_static_use
├── minSampleShadingValue_zero_sample_id_static_use
├── minSampleShadingValue_quarter_sample_id_static_use
├── minSampleShadingValue_half_sample_id_static_use
├── sample_position_static_use
├── minSampleShadingValue_zero_sample_position_static_use
├── minSampleShadingValue_quarter_sample_position_static_use
└── minSampleShadingValue_half_sample_position_static_use

draw.dynamic_rendering.partial_secondary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── minSampleShadingValue_zero_sample_decoration_dynamic_use
├── minSampleShadingValue_quarter_sample_decoration_dynamic_use
├── minSampleShadingValue_half_sample_decoration_dynamic_use
├── sample_id_static_use
├── minSampleShadingValue_zero_sample_id_static_use
├── minSampleShadingValue_quarter_sample_id_static_use
├── minSampleShadingValue_half_sample_id_static_use
├── sample_position_static_use
├── minSampleShadingValue_zero_sample_position_static_use
├── minSampleShadingValue_quarter_sample_position_static_use
└── minSampleShadingValue_half_sample_position_static_use

draw.dynamic_rendering.complete_secondary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use
```

Each rendering-path root owns the same three direct base leaves. The render-pass, primary-command-buffer, and partial-secondary roots additionally own the nine `minSampleShadingValue_{zero,quarter,half}_*` override leaves; the complete-secondary root omits them because registration of the override leaves is skipped when `secondaryCmdBufferCompletelyContainsDynamicRenderpass` is true ([registration gate](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L524-L527)).

The checked-in mustpass lists confirm the twelve leaves (three base leaves and nine `minSampleShadingValue_*` overrides) under `draw.renderpass`, `draw.dynamic_rendering.primary_cmd_buff`, and `draw.dynamic_rendering.partial_secondary_cmd_buff`, and the three base leaves alone under `draw.dynamic_rendering.complete_secondary_cmd_buff`, in `external/vulkancts/mustpass/main/vk-default/draw.txt` (39 entries total). The Vulkan SC list contains the three base render-pass leaves in `external/vulkancts/mustpass/main/vksc-default/draw.txt` (3 entries total), matching the `#ifndef CTS_USES_VULKANSC` guard around dynamic-rendering test-tree creation and execution. Neither list contains the two nested dynamic-rendering roots, matching the dispatcher's `nestedSecondaryCmdBuffer` guard. The mustpass files select registered paths; feature and extension availability still determines whether an individual case is supported at runtime.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Trigger mechanism | `sample_decoration_dynamic_use`, `sample_id_static_use`, `sample_position_static_use` | Selects the fragment-shader construct that must cause implicit sample shading. | [`triggerCases`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L503-L514) |
| Pipeline sample-shading override | Base leaves: `sampleShadingEnable = VK_FALSE`, `minSampleShading = 0.0`; `minSampleShadingValue_zero/quarter/half` leaves: `VK_TRUE` with `0.0`, `0.25`, `0.5` | Enables explicit pipeline sample shading at a configured rate below 1.0 to check that the implicit trigger still forces one invocation per covered sample. | [`TestParameters`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L74-L75), [`minSampleShadingCases`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L528-L536), [override registration](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L538-L549) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` | Provides four coverage samples per pixel for the invocation-count lower bound. | [`sampleCount`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L103-L106) |
| Render target | 4 × 4, `VK_FORMAT_R8G8B8A8_UNORM` | Covers 16 pixels; the color value is stored but is not the authoritative result. | [`imageFormat` and `imageExtent`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L210-L228) |
| Rendering path | `renderpass`; `dynamic_rendering.primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Changes command recording and attachment setup without changing the shader trigger or expected count. | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

## Behavior Parameters

Two behavioral axes are registered as test case names. The trigger mechanism changes the fragment-shader construct that must cause implicit sample shading; the `minSampleShadingValue_*` suffix changes the pipeline multisample state that the trigger must overcome. The host setup and counter check remain shared across both axes.

### `sample_decoration_dynamic_use`: dynamically used sample-qualified input

The vertex shader writes `verify` at location 0, and the fragment shader reads `layout (location = 0) sample in float verify`. It converts `ceil(verify)` to the increment value. The generated vertex values are between 0.75 and 1.0, so the increment is 1 while the `sample` decoration supplies the behavior under test. See [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L131-L172).

### `sample_id_static_use`: static use of `gl_SampleID`

The fragment shader contains the statement `gl_SampleID;` and increments the counter by 1. The value need not feed the color result: its static use is the trigger being tested.

### `sample_position_static_use`: static use of `gl_SamplePosition`

The fragment shader contains the statement `gl_SamplePosition;` and increments the counter by 1. As with `gl_SampleID`, the built-in's static use is the behavior under test rather than its numeric value.

### `minSampleShadingValue_{zero,quarter,half}_*`: explicit shading rate below 1.0

Each trigger mechanism is additionally registered with `sampleShadingEnable = VK_TRUE` and `minSampleShading` set to 0.0, 0.25, or 0.5 ([`minSampleShadingCases`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L528-L536), [override registration](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L538-L549)). These leaves reuse the same shaders and the same 64-increment lower bound; only the pipeline multisample state changes ([multisample state](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L352-L356)). The sample-interpolation and `SampleID`/`SamplePosition` usage must still force the shading rate to 1.0, so applying the configured rate instead of full sample shading produces a counter below 64 and fails the case.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.implicit_sample_shading.sample_decoration_dynamic_use
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `sample_decoration_dynamic_use` | Dynamically reads a `sample`-decorated fragment input, making that interface qualifier the implicit sample-shading trigger. |
| `renderpass` | Selects the canonical render-pass leaf; the dynamic-rendering leaves reuse the same generated shaders. |
| Four samples over 4 × 4 pixels | Makes the expected minimum counter value `4 * 4 * 4 = 64` when every covered sample runs a fragment invocation. |

#### Purpose

This fragment shader checks that dynamically using a `sample`-qualified input forces sample-rate execution even though pipeline sample shading is disabled. Every invocation atomically contributes one to the host-visible counter, so the draw must produce at least 64 increments.

#### Structural Design

| Shader element | Role in the proof |
|---|---|
| Vertex `verify` output | Produces values from 0.75 through 0.875 at the three full-screen-triangle vertices. |
| Fragment `sample in float verify` | Selects sample interpolation and is dynamically read by `ceil(verify)`. |
| `uint(ceil(verify))` | Converts every interpolated value to the increment value 1. |
| Binding 0 `invocationCount` | Accumulates one atomic addition per fragment invocation for host validation. |
| `outColor` | Satisfies the color-attachment output; it is not the pass/fail oracle. |

#### Shader Code

##### Fragment Shader

```glsl
#version 450

/// The color is stored in the multisample attachment, but the host verdict uses the counter below.
layout (location = 0) out vec4 outColor;
/// Dynamic use of this sample-qualified input is the selected implicit sample-shading trigger.
layout (location = 0) sample in float verify;
/// Binding 0 is one host-visible uint initialized to zero before the draw.
layout (std430, binding = 0) buffer Output {
    uint invocationCount;
} buf;
void main() {
    /// The producer's values lie in [0.75, 1.0), so every invocation contributes exactly one.
    uint one   = uint(ceil(verify));
    /// The returned old value is unused; the atomic side effect is the validation signal.
    uint index = atomicAdd(buf.invocationCount, one);
    outColor = vec4(float(one), 1.0, 0.0, 1.0);
}
```

##### Vertex Shader

```glsl
#version 450

/// These three clip-space vertices form one triangle that covers the 4 × 4 render area.
vec2 positions[3] = vec2[](
    vec2(-1.0, -1.0),
    vec2(3.0, -1.0),
    vec2(-1.0, 3.0)
);
/// Location 0 supplies the value dynamically consumed by the sample-qualified fragment input.
layout (location = 0) out float verify;
void main() {
    const uint triIdx     = gl_VertexIndex / 3u;
    const uint triVertIdx = gl_VertexIndex % 3u;
    gl_Position = vec4(positions[triVertIdx], 0.0, 1.0);
    /// For this three-vertex draw, the emitted values are 0.75, 0.8125, and 0.875.
    verify = float(triIdx) + float(triVertIdx) / 16.0 + 0.75;
}
```

#### Additional Info

- The vertex stage varies with the trigger: it declares and writes `verify` only for `sample_decoration_dynamic_use`; the two built-in trigger cases retain the same full-screen positions but omit this interface value ([generator branches](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L137-L153)).
- `index` preserves the return value of `atomicAdd` in generated GLSL but never participates in the verdict. The host reads only the final `invocationCount` and accepts any value at least 64 ([shader generation](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L155-L171), [result check](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L484-L496)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Trigger mechanism | `sample_id_static_use` removes `verify` from both interfaces, emits the bare expression `gl_SampleID;`, and uses constant increment 1. `sample_position_static_use` analogously emits `gl_SamplePosition;`. | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L131-L172) |
| Rendering path | Render-pass and dynamic-rendering registrations do not alter GLSL; `SharedGroupParams` changes only host rendering and command-buffer setup. | [`iterate()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L234-L475) |
| Sample count and target size | Both are fixed host constants, so no shader declaration or control-flow branch varies with them. | [`SampleShadingSampleAttributeTestInstance`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L94-L107) |

#### SPIR-V

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
; Bound: 35
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %verify %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %one "one"
               OpName %verify "verify"
               OpName %index "index"
               OpName %Output "Output"
               OpMemberName %Output 0 "invocationCount"
               OpName %buf "buf"
               OpName %outColor "outColor"
               OpDecorate %verify Sample
               OpDecorate %verify Location 0
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %buf Binding 0
               OpDecorate %buf DescriptorSet 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
      %float = OpTypeFloat 32
%_ptr_Input_float = OpTypePointer Input %float
     %verify = OpVariable %_ptr_Input_float Input
     %Output = OpTypeStruct %uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
        %buf = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
       %main = OpFunction %void None %3
          %5 = OpLabel
        %one = OpVariable %_ptr_Function_uint Function
      %index = OpVariable %_ptr_Function_uint Function
         %12 = OpLoad %float %verify
         %13 = OpExtInst %float %1 Ceil %12
         %14 = OpConvertFToU %uint %13
               OpStore %one %14
         %22 = OpAccessChain %_ptr_Uniform_uint %buf %int_0
         %23 = OpLoad %uint %one
         %26 = OpAtomicIAdd %uint %22 %uint_1 %uint_0 %23
               OpStore %index %26
         %30 = OpLoad %uint %one
         %31 = OpConvertUToF %float %30
         %34 = OpCompositeConstruct %v4float %31 %float_1 %float_0 %float_1
               OpStore %outColor %34
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 60
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_ %verify
               OpSource GLSL 450
               OpName %main "main"
               OpName %positions "positions"
               OpName %triIdx "triIdx"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %triVertIdx "triVertIdx"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %verify "verify"
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %verify Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_v2float_uint_3 = OpTypeArray %v2float %uint_3
%_ptr_Private__arr_v2float_uint_3 = OpTypePointer Private %_arr_v2float_uint_3
  %positions = OpVariable %_ptr_Private__arr_v2float_uint_3 Private
   %float_n1 = OpConstant %float -1
         %14 = OpConstantComposite %v2float %float_n1 %float_n1
    %float_3 = OpConstant %float 3
         %16 = OpConstantComposite %v2float %float_3 %float_n1
         %17 = OpConstantComposite %v2float %float_n1 %float_3
         %18 = OpConstantComposite %_arr_v2float_uint_3 %14 %16 %17
%_ptr_Function_uint = OpTypePointer Function %uint
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
    %v4float = OpTypeVector %float 4
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%_ptr_Private_v2float = OpTypePointer Private %v2float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_float = OpTypePointer Output %float
     %verify = OpVariable %_ptr_Output_float Output
   %float_16 = OpConstant %float 16
 %float_0_75 = OpConstant %float 0.75
       %main = OpFunction %void None %3
          %5 = OpLabel
     %triIdx = OpVariable %_ptr_Function_uint Function
 %triVertIdx = OpVariable %_ptr_Function_uint Function
               OpStore %positions %18
         %24 = OpLoad %int %gl_VertexIndex
         %25 = OpBitcast %uint %24
         %26 = OpUDiv %uint %25 %uint_3
               OpStore %triIdx %26
         %28 = OpLoad %int %gl_VertexIndex
         %29 = OpBitcast %uint %28
         %30 = OpUMod %uint %29 %uint_3
               OpStore %triVertIdx %30
         %38 = OpLoad %uint %triVertIdx
         %40 = OpAccessChain %_ptr_Private_v2float %positions %38
         %41 = OpLoad %v2float %40
         %44 = OpCompositeExtract %float %41 0
         %45 = OpCompositeExtract %float %41 1
         %46 = OpCompositeConstruct %v4float %44 %45 %float_0 %float_1
         %48 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %48 %46
         %51 = OpLoad %uint %triIdx
         %52 = OpConvertUToF %float %51
         %53 = OpLoad %uint %triVertIdx
         %54 = OpConvertUToF %float %53
         %56 = OpFDiv %float %54 %float_16
         %57 = OpFAdd %float %52 %56
         %59 = OpFAdd %float %57 %float_0_75
               OpStore %verify %59
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checking requires `fragmentStoresAndAtomics` for the storage-buffer atomic operation and `sampleRateShading` for all three trigger variants. Dynamic-rendering paths additionally require `VK_KHR_dynamic_rendering`. See [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L117-L129).
- The instance creates a host-visible one-`uint32_t` storage buffer, clears it to zero, binds it at fragment descriptor binding 0, and creates a four-sample 4 × 4 color attachment. See [`iterate()` resource setup](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L186-L344).
- A graphics pipeline uses triangle-list rasterization, and its multisample state comes from the test parameters: base leaves run with `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0`, while `minSampleShadingValue_*` leaves run with `VK_TRUE` and 0.0, 0.25, or 0.5; `rasterizationSamples` is always `VK_SAMPLE_COUNT_4_BIT`. See [`multisampling`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L350-L356). For dynamic rendering, `VkPipelineRenderingCreateInfoKHR` is chained into the pipeline creation pNext only when the selected path uses dynamic rendering, satisfying `VUID-VkGraphicsPipelineCreateInfo-pNext-12427` ([gpPNext](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L297-L298)).
- The command buffer records either a render pass or dynamic rendering, binds the descriptor set and pipeline, and draws three vertices. Secondary-buffer cases differ only in where rendering and draw commands are recorded. A fragment-to-host buffer barrier, submission wait, and allocation invalidation precede the readback. See [`iterate()` command and readback flow](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L395-L487).
- The host compares the counter against `sampleCount * width * height = 4 * 4 * 4 = 64`. Values below 64 fail; values at or above 64 pass. See [`expectedCounter` and verdict](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L103-L106) and [`iterate()` result check](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L477-L496).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_decoration_dynamic_use` | Failure to apply sample-qualified interpolation or implicit sample-rate execution; fragment input interface/lowering error; counter or synchronization problem. |
| `sample_id_static_use` | Failure to treat static `gl_SampleID` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| `sample_position_static_use` | Failure to treat static `gl_SamplePosition` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| Any `minSampleShadingValue_zero/quarter/half_*` leaf | The implementation applied the configured `minSampleShading` rate instead of the forced full shading rate for the implicit trigger; pipeline multisample state handling; counter or synchronization problem. |
| Any value | Multisample attachment, pipeline sample state, draw coverage, atomic storage, barrier, or host readback can produce a low counter. |

### Cause Analysis

#### Trigger does not produce sample-rate invocations

**Possible failure symptoms:** The counter is below 64 for one trigger leaf, showing fewer than one counted invocation per sample for the 16-pixel target.

**Possible implementation causes:** The implementation may fail to recognize the relevant built-in or `sample` decoration as an implicit sample-shading trigger, or may lower the fragment interface/built-in incorrectly. The Vulkan sample-shading rules and the case-specific shader source establish the expected behavior; source-level investigation is needed to locate the responsible implementation component.

#### Configured minSampleShading overrides the forced shading rate

**Possible failure symptoms:** A `minSampleShadingValue_*` leaf reports a counter below 64 while the corresponding base leaf passes, and the shortfall grows as the configured rate decreases.

**Possible implementation causes:** The implementation may treat the pipeline's `minSampleShading` as authoritative and shade only the configured fraction of covered samples, ignoring that sample-qualified inputs and static `SampleID`/`SamplePosition` use force the shading rate to 1.0. Pipeline multisample state handling and the interaction between explicit and implicit sample shading are the first places to investigate.

#### Multisample execution or coverage is incorrect

**Possible failure symptoms:** Multiple trigger leaves fail with a counter below 64, or the result varies with the rendering path despite identical shader behavior.

**Possible implementation causes:** The multisample attachment, rasterization sample state, draw coverage, render-pass/dynamic-rendering setup, or secondary-command-buffer execution may be incorrect. The source does not identify which implementation layer is responsible.

#### Atomic counter result is not visible to the host

**Possible failure symptoms:** Rendering completes but the host reads zero or a stale value, producing the explicit `Atomic counter value lower than expected` failure.

**Possible implementation causes:** The shader storage write, fragment-to-host memory dependency, mapped allocation visibility, or host invalidation/readback path may be incorrect. The test's barrier and allocation operations are visible in source; distinguishing an implementation fault from an environment issue requires further investigation.

## Case Pruning

### Requirement-based pruning

- A case is unsupported unless `fragmentStoresAndAtomics` and `sampleRateShading` are available. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L117-L129)).

### Design-based pruning

- The fixed 4 × 4 target and four-sample attachment keep the atomic-counter proof small; the test does not expand a sample-count or framebuffer-size matrix.
- Nested dynamic-rendering paths intentionally omit the family because [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) does not add it when `nestedSecondaryCmdBuffer` is true. This is a registration boundary, not a claim that the trigger semantics are invalid there.
- The nine `minSampleShadingValue_*` override leaves are additionally skipped whenever `secondaryCmdBufferCompletelyContainsDynamicRenderpass` is true, so the `complete_secondary_cmd_buff` root registers only the three base leaves ([registration gate](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L524-L527)). The override leaves add no new feature or extension requirements beyond the base leaves.

## Key Takeaways

- All three trigger mechanisms test implicit sample shading, each with a distinct fragment-shader trigger, and each appears as one base leaf plus three `minSampleShadingValue_*` override leaves.
- Base leaves keep pipeline sample shading disabled, so their counter is evidence of shader-triggered behavior; the override leaves enable explicit shading rates 0.0, 0.25, and 0.5 and check that the implicit trigger still forces one invocation per covered sample.
- The authoritative check is a host-visible atomic counter of at least 64 after a 4 × 4 draw with four samples per pixel.
- Render-pass and three non-nested dynamic-rendering paths share this family; nested paths preserve the dispatcher’s intentional omission.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test-family factory | [`createSampleAttributeTests()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L501-L553) | Registers the family with three base leaves and nine `minSampleShadingValue_*` override leaves. |
| Trigger enum and parameters | [`Trigger` and `TestParameters`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L59-L75) | Defines the behavioral variants and the sample-shading override fields. |
| Support gate | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L117-L129) | Defines feature and dynamic-rendering requirements. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L131-L172) | Generates the three fragment-shader trigger forms. |
| Pipeline sample-shading state | [`multisampling`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L350-L356) | Applies the per-leaf `sampleShadingEnable`/`minSampleShading` values. |
| Host execution and verdict | [`iterate()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L186-L496) | Creates resources, records rendering, reads the counter, and applies the 64 minimum. |
| Draw dispatcher | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) | Establishes non-nested registration and nested-path omission. |
| Rendering-path roots | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) | Creates render-pass and dynamic-rendering hierarchy roots. |
| Vulkan sample-shading semantics | [Sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading) | Defines implicit sample-shading triggers and rates. |
| Vulkan fragment interfaces | [Fragment shader interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput) | Defines sample-related input decorations and built-ins. |
| Understanding Brief | [SampleAttributeTests_brief.md](SampleAttributeTests_brief.md) | Learning-oriented analysis and source mapping. |
