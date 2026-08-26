## Overview

**Core question:** Does a fragment shader use of `gl_SampleID`, `gl_SamplePosition`, or a `sample`-decorated input force implicit sample-rate shading when pipeline sample shading is disabled?

- The [`implicit_sample_shading`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L496-L517) test family contains three fragment-shader trigger variants.
- Each case renders one full-screen triangle into a 4 × 4, four-sample color attachment and increments a fragment-storage atomic counter.
- The pipeline sets `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0`; the host verdict requires at least 64 counter increments, demonstrating one invocation per covered sample.
- The same implementation is registered under the render-pass path and the three non-nested dynamic-rendering paths; nested dynamic-rendering paths omit it because the draw dispatcher excludes this family for nested command buffers.

## Background Knowledge

- **Sample shading:** A multisample fragment can be shaded once per pixel or once for each covered sample. Vulkan permits implicit sample shading when a fragment shader statically uses `SampleID` or `SamplePosition`, and gives a `sample`-decorated input the corresponding sample-rate behavior. See [sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading).
- **Fragment shader interface decorations:** `SampleID` identifies the sample for a sample-rate invocation, `SamplePosition` provides that sample's position, and the `sample` decoration selects sample interpolation for an input. These are shader interface semantics, not additional host-created resources. See [fragment shader inputs](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput).

## Registration Hierarchy

The dispatcher adds this family whenever `nestedSecondaryCmdBuffer` is false. [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) creates the render-pass and dynamic-rendering modes, while [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) registers this family only in the four non-nested ownership roots shown below.

```text
draw.renderpass.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use

draw.dynamic_rendering.primary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use

draw.dynamic_rendering.partial_secondary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use

draw.dynamic_rendering.complete_secondary_cmd_buff.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use
```

Each rendering-path root owns the same three direct test case leaves.

The checked-in mustpass lists confirm all three leaves under `draw.renderpass`, `draw.dynamic_rendering.primary_cmd_buff`, `draw.dynamic_rendering.partial_secondary_cmd_buff`, and `draw.dynamic_rendering.complete_secondary_cmd_buff` in `external/vulkancts/mustpass/main/vk-default/draw.txt` (12 entries total). The Vulkan SC list contains the three render-pass leaves in `external/vulkancts/mustpass/main/vksc-default/draw.txt` (3 entries total), matching the `#ifndef CTS_USES_VULKANSC` guard around dynamic-rendering test-tree creation and execution. Neither list contains the two nested dynamic-rendering roots, matching the dispatcher's `nestedSecondaryCmdBuffer` guard. The mustpass files select registered paths; feature and extension availability still determines whether an individual case is supported at runtime.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Trigger mechanism | `sample_decoration_dynamic_use`, `sample_id_static_use`, `sample_position_static_use` | Selects the fragment-shader construct that must cause implicit sample shading. | [`triggerCases`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L498-L509) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` | Provides four coverage samples per pixel for the invocation-count lower bound. | [`sampleCount`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L99-L102) |
| Render target | 4 × 4, `VK_FORMAT_R8G8B8A8_UNORM` | Covers 16 pixels; the color value is stored but is not the authoritative result. | [`imageFormat` and `imageExtent`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L206-L224) |
| Rendering path | `renderpass`; `dynamic_rendering.primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Changes command recording and attachment setup without changing the shader trigger or expected count. | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf, because each leaf changes the fragment-shader trigger while the host setup and counter check remain shared.

### `sample_decoration_dynamic_use`: dynamically used sample-qualified input

The vertex shader writes `verify` at location 0, and the fragment shader reads `layout (location = 0) sample in float verify`. It converts `ceil(verify)` to the increment value. The generated vertex values are between 0.75 and 1.0, so the increment is 1 while the `sample` decoration supplies the behavior under test. See [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168).

### `sample_id_static_use`: static use of `gl_SampleID`

The fragment shader contains the statement `gl_SampleID;` and increments the counter by 1. The value need not feed the color result: its static use is the trigger being tested.

### `sample_position_static_use`: static use of `gl_SamplePosition`

The fragment shader contains the statement `gl_SamplePosition;` and increments the counter by 1. As with `gl_SampleID`, the built-in's static use is the behavior under test rather than its numeric value.

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

- The vertex stage varies with the trigger: it declares and writes `verify` only for `sample_decoration_dynamic_use`; the two built-in trigger cases retain the same full-screen positions but omit this interface value ([generator branches](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L133-L149)).
- `index` preserves the return value of `atomicAdd` in generated GLSL but never participates in the verdict. The host reads only the final `invocationCount` and accepts any value at least 64 ([shader generation](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L151-L167), [result check](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L479-L491)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Trigger mechanism | `sample_id_static_use` removes `verify` from both interfaces, emits the bare expression `gl_SampleID;`, and uses constant increment 1. `sample_position_static_use` analogously emits `gl_SamplePosition;`. | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168) |
| Rendering path | Render-pass and dynamic-rendering registrations do not alter GLSL; `SharedGroupParams` changes only host rendering and command-buffer setup. | [`iterate()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L230-L470) |
| Sample count and target size | Both are fixed host constants, so no shader declaration or control-flow branch varies with them. | [`SampleShadingSampleAttributeTestInstance`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L90-L103) |

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

- Support checking requires `fragmentStoresAndAtomics` for the storage-buffer atomic operation and `sampleRateShading` for all three trigger variants. Dynamic-rendering paths additionally require `VK_KHR_dynamic_rendering`. See [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125).
- The instance creates a host-visible one-`uint32_t` storage buffer, clears it to zero, binds it at fragment descriptor binding 0, and creates a four-sample 4 × 4 color attachment. See [`iterate()` resource setup](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L182-L340).
- A graphics pipeline uses triangle-list rasterization and explicitly disables pipeline sample shading with `sampleShadingEnable = VK_FALSE`, `minSampleShading = 0.0`, and `rasterizationSamples = VK_SAMPLE_COUNT_4_BIT`. See [`multisampling`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L345-L365).
- The command buffer records either a render pass or dynamic rendering, binds the descriptor set and pipeline, and draws three vertices. Secondary-buffer cases differ only in where rendering and draw commands are recorded. A fragment-to-host buffer barrier, submission wait, and allocation invalidation precede the readback. See [`iterate()` command and readback flow](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L390-L482).
- The host compares the counter against `sampleCount * width * height = 4 * 4 * 4 = 64`. Values below 64 fail; values at or above 64 pass. See [`expectedCounter` and verdict](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L99-L102) and [`iterate()` result check](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L472-L491).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_decoration_dynamic_use` | Failure to apply sample-qualified interpolation or implicit sample-rate execution; fragment input interface/lowering error; counter or synchronization problem. |
| `sample_id_static_use` | Failure to treat static `gl_SampleID` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| `sample_position_static_use` | Failure to treat static `gl_SamplePosition` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| Any value | Multisample attachment, pipeline sample state, draw coverage, atomic storage, barrier, or host readback can produce a low counter. |

### Cause Analysis

#### Trigger does not produce sample-rate invocations

**Possible failure symptoms:** The counter is below 64 for one trigger leaf, showing fewer than one counted invocation per sample for the 16-pixel target.

**Possible implementation causes:** The implementation may fail to recognize the relevant built-in or `sample` decoration as an implicit sample-shading trigger, or may lower the fragment interface/built-in incorrectly. The Vulkan sample-shading rules and the case-specific shader source establish the expected behavior; source-level investigation is needed to locate the responsible implementation component.

#### Multisample execution or coverage is incorrect

**Possible failure symptoms:** Multiple trigger leaves fail with a counter below 64, or the result varies with the rendering path despite identical shader behavior.

**Possible implementation causes:** The multisample attachment, rasterization sample state, draw coverage, render-pass/dynamic-rendering setup, or secondary-command-buffer execution may be incorrect. The source does not identify which implementation layer is responsible.

#### Atomic counter result is not visible to the host

**Possible failure symptoms:** Rendering completes but the host reads zero or a stale value, producing the explicit `Atomic counter value lower than expected` failure.

**Possible implementation causes:** The shader storage write, fragment-to-host memory dependency, mapped allocation visibility, or host invalidation/readback path may be incorrect. The test's barrier and allocation operations are visible in source; distinguishing an implementation fault from an environment issue requires further investigation.

## Case Pruning

### Requirement-based pruning

- A case is unsupported unless `fragmentStoresAndAtomics` and `sampleRateShading` are available. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125)).

### Design-based pruning

- The fixed 4 × 4 target and four-sample attachment keep the atomic-counter proof small; the test does not expand a sample-count or framebuffer-size matrix.
- Nested dynamic-rendering paths intentionally omit the family because [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) does not add it when `nestedSecondaryCmdBuffer` is true. This is a registration boundary, not a claim that the trigger semantics are invalid there.

## Key Takeaways

- All three leaves test implicit sample shading, but each uses a distinct fragment-shader trigger.
- Pipeline sample shading remains disabled, so the counter is evidence of shader-triggered behavior rather than explicit `minSampleShading` configuration.
- The authoritative check is a host-visible atomic counter of at least 64 after a 4 × 4 draw with four samples per pixel.
- Render-pass and three non-nested dynamic-rendering paths share this family; nested paths preserve the dispatcher’s intentional omission.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test-family factory | [`createSampleAttributeTests()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L496-L519) | Registers the family and its three test case leaves. |
| Trigger enum and parameters | [`Trigger`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L59-L72) | Defines the behavioral variants. |
| Support gate | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125) | Defines feature and dynamic-rendering requirements. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168) | Generates the three fragment-shader trigger forms. |
| Host execution and verdict | [`iterate()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L182-L491) | Creates resources, records rendering, reads the counter, and applies the 64 minimum. |
| Draw dispatcher | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) | Establishes non-nested registration and nested-path omission. |
| Rendering-path roots | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) | Creates render-pass and dynamic-rendering hierarchy roots. |
| Vulkan sample-shading semantics | [Sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading) | Defines implicit sample-shading triggers and rates. |
| Vulkan fragment interfaces | [Fragment shader interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput) | Defines sample-related input decorations and built-ins. |
| Understanding Brief | [SampleAttributeTests_brief.md](SampleAttributeTests_brief.md) | Learning-oriented analysis and source mapping. |
