## Overview

**Core question:** Do GLSL texture-gather forms return a valid four-texel component or depth-comparison vector for the configured texture view, coordinates, offsets, sampler state, mip selection, execution pipeline, and sparse-residency mode?

- [`vktShaderRenderTextureGatherTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1) implements `glsl.texture_gather`, the generated GLSL family for ordinary, single-offset, dynamic-offset, and four-offset texture gathers. [`createTextureGatherTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3139-L3142) returns the family, and the GLSL package registers it directly below `glsl` ([package registration](../../../modules/vulkan/vktTestPackage.cpp#L1270-L1272)).
- Each test case leaf owns several gather iterations. A graphics leaf renders a two-triangle `64 × 64` quad; a compute leaf dispatches an `8 × 8` workgroup grid over the same `64 × 64` image. Both paths gather from generated 2D, 2D-array, or cube texture data and compare every output pixel with the texture-library reference ([instance setup](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1240-L1268), [iteration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1459-L1513)).
- The Vulkan default mustpass lists 3,174 leaves under `dEQP-VK.glsl.texture_gather`; the Vulkan SC default mustpass lists 1,455 corresponding leaves. The 1,719 additional Vulkan leaves are the source-guarded sparse and AMD gather-bias/LOD variants ([Vulkan list](../../../mustpass/main/vk-default/glsl.txt#L23590-L26763), [Vulkan SC list](../../../mustpass/main/vksc-default/glsl.txt#L20569-L22023)).
- This page describes source-defined behavior and mustpass coverage. It does not claim that the cases were run on the current host.

## Background Knowledge

- A texture gather returns one selected component from each of four neighboring texels. Non-depth samplers can select components `0`–`3`, while omitting the component argument selects component `0`; depth samplers instead gather comparison results using a reference value ([iteration generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L996-L1014), [call construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1960-L2038)).
- `textureGatherOffset` applies one two-dimensional offset. The `offset_dynamic` family uses the same GLSL function but derives the offset from pixel position. `textureGatherOffsets` supplies four compile-time offsets, one per returned component ([function selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1922-L1935), [offset expressions](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1973-L2016)).
- Offset limits have two meanings in this family. `min_required_offset` uses the guaranteed range `[-8, 7]`; `implementation_offset` uses the device's `minTexelGatherOffset` and `maxTexelGatherOffset`, except that four-offset leaves embed `[-32, 31]` constants and require the device to accept that wider range ([constants and range selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L71-L79), [range helpers](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1164-L1203)).
- Gather filtering differs from ordinary filtered sampling: the source explicitly logs that minification and magnification filter modes should not affect the gathered values. Filter cases vary sampler state to check that invariant ([sampler logging](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1420-L1426)).
- The software oracle accepts implementation-permitted sampling uncertainty. It first compares against an ideal gather, then calls `isGatherResultValid()` or `isGatherCompareResultValid()` before marking the pixel invalid ([color verification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L682-L736), [comparison verification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L765-L815)).

## Registration Hierarchy

```text
glsl.texture_gather
├── graphics
└── compute
```

These pipeline intermediate nodes both contain `basic`, `offset`, `offset_dynamic`, and `offsets`. `basic` leads directly to texture-type nodes; each offset form first splits into `min_required_offset` and `implementation_offset` ([pipeline and operation loops](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2852-L2879)). Below those levels, [`TextureGatherTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2821-L3135) adds texture type, format, optional `no_corners`, size, optional comparison mode, and wrap-pair levels. Selected combinations also add `texture_swizzle`, `filter_mode`, and `base_level` branches. Regular leaves have `sparse_` siblings outside Vulkan SC.

## Parameter Dimensions and Observed Values

| Dimension | Source-defined values and restrictions |
|---|---|
| Pipeline | `graphics`, `compute` ([pipeline loop](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2852-L2862)). |
| Gather form | `basic`, `offset`, `offset_dynamic`, `offsets` ([name mapping](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L818-L858)). |
| Offset range | No range group for `basic`; `min_required_offset` and `implementation_offset` for the other forms ([range grouping](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2864-L2879)). |
| Texture type | `2d`, `2d_array`, and `cube`; cube is retained only for `basic` ([texture loop](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2823-L2827), [cube filter](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2881-L2890)). |
| Format | `rgba8`, `rgba8ui`, `rgba8i`, `depth32f` ([format table](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2829-L2836)). |
| Size | `size_pot` = `64 × 64 × 3`; `size_npot` = `17 × 23 × 3` ([size table](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2838-L2842)). |
| Comparison | Non-depth formats have no comparison intermediate node. Depth uses `compare_less` and `compare_greater` ([comparison filter](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2917-L2938)). |
| Wrap pair | `clamp_to_edge_repeat`, `repeat_mirrored_repeat`, `mirrored_repeat_clamp_to_edge` ([wrap table and pairing](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2844-L2850), [pair loop](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2940-L2956)). |
| Gather component | Explicit components `0`–`3` plus an implicit component-0 call for non-depth; one implicit case for depth. AMD bias skips the implicit non-depth call ([iteration generator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L996-L1008)). |
| View behavior | Cube `no_corners`; six cyclic swizzles over `R`, `G`, `B`, `A`, `ZERO`, and `ONE`; filter pairs; base levels `1` and `2` ([cube groups](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2898-L2907), [additional branches](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2975-L3127)). |
| Backing and LOD mode | Regular and sparse backing outside Vulkan SC; normal base-level mode plus non-depth `_amd_bias` and `_amd_lod` leaves outside Vulkan SC ([sparse registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2957-L2965), [level modes](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3077-L3125)). |

## Behavior Parameters

### Gather form and offset source

`basic` emits `textureGather`. `offset` emits `textureGatherOffset` with either a literal minimum-range offset or an implementation-range offset uploaded through a uniform. `offset_dynamic` computes a per-pixel offset by taking the transposed pixel coordinates modulo the active range. `offsets` emits `textureGatherOffsets` with four literal vectors ([call generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1869-L2040)).

The per-leaf iteration generator varies component selection and representative offset vectors. For single offsets, all component forms get one extreme pair while only the first component form gets the remaining corners, half-range points, and zero. Four-offset cases similarly retain one corner set for every component and one extra mixed set only for the first component form ([iteration matrix](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L996-L1080)).

### Texture shape, layer, and cube-face behavior

2D cases interpolate coordinates from `(-0.3, -0.4)` to `(1.5, 1.6)` in normal mode, deliberately reaching beyond normalized image bounds so the wrap pair is observable. 2D-array cases add a layer coordinate. Layer `0` receives every basic iteration; layers `-1`, `1`, `2`, and `3` receive one selected component/offset iteration, including out-of-bounds layer coverage ([2D coordinates](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2163-L2170), [array iteration selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2302-L2339)).

Cube cases exist only for `basic`. Face zero receives every component iteration, and each remaining face receives one selected iteration. Normal cube coordinates reach beyond face edges; the `no_corners` branch narrows one axis so samples do not cover cube corners ([cube iteration selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2528-L2565), [cube coordinates](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2610-L2618)).

### Format, comparison, and texture-view behavior

Normalized color gathers return `vec4`; signed and unsigned integer gathers return `ivec4` and `uvec4`; depth gathers return comparison `vec4` values ([result typing](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L945-L970)). Textures are filled with base-seed-derived random color tiles, then optionally copied into a swizzled reference texture. Verification uses the same selected base-level subview as the Vulkan image view ([2D texture creation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2173-L2198), [array verification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2433-L2439)).

`filter_mode` varies minification and magnification state while expecting gather values to remain unaffected. `base_level` selects mip levels `1` or `2`. `_amd_bias` and `_amd_lod` call the AMD gather forms with the numeric level value as bias or explicit LOD, respectively ([level-call construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1869-L1971), [base-level registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3077-L3127)).

### Sparse-residency behavior

Sparse leaves replace ordinary gather calls with `sparseTextureGather*ARB` or sparse AMD LOD forms. The shader checks `sparseTexelsResidentARB`; a resident result is written normally, while a nonresident result becomes `(0, 0, 0, 1)` in the gather result type ([sparse call selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1881-L1918), [fragment result handling](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1744-L1759)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.texture_gather.graphics.basic.2d.rgba8.size_pot.repeat_mirrored_repeat
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `graphics.basic` | Selects the graphics path and ordinary `textureGather`; `offsetSize` is `none`, so no offset extension or offset uniform is generated. |
| `2d.rgba8.size_pot` | Selects `sampler2D`, a floating-point `vec4` gather result, and a 64 × 64 × 3 host texture with normalized 2D coordinates. |
| `repeat_mirrored_repeat`, nearest filters, normal level 0, regular backing | Selects the registered S/T wrap pair and default sampler/view state; these affect sampling setup but not the shader's resource shape. |
| First generated iteration (`frag_0`, implicit component 0) | `generateBasic2DCaseIterations()` begins with `componentNdx = -1`, so the call omits the component argument and uses GLSL's implicit component 0. |

#### Purpose

This representative tests the baseline 2D floating-point gather path: four neighboring texels selected by `textureGather` are returned as one `vec4` and written to the color attachment. The host then compares the 64 × 64 image against the corresponding gather oracle.

#### Structural Design

| Phase | Shader-visible structure | Role |
|---|---|---|
| Interface | `v_texCoord` at location 0 and `o_color` at location 0 | Carries interpolated 2D coordinates from the shared pass-through vertex stage and returns the gather result. |
| Resource | `sampler2D u_sampler` at binding 0 | Reads the regular RGBA8 texture created by the test instance. |
| Main operation | `textureGather(u_sampler, v_texCoord)` | Performs the baseline gather with implicit component 0 and no explicit LOD or offset. |
| Output | `o_color = ...` | Exposes the four gathered values to the graphics result image. |

#### Shader Code

The fragment source is emitted by `genFragmentShaderSource()` for `sampler2D`, normal level mode, regular backing, and the first basic iteration ([`vktShaderRenderTextureGatherTests.cpp#L1691-L1763`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1691-L1763), [`genGatherFuncCall()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1869-L2041)).

```glsl
#version 450

/// Location 0 receives interpolated 2D texture coordinates from `vert`.
layout(location = 0) in highp vec2 v_texCoord;

/// The baseline RGBA8 case maps to a floating-point sampler2D.
layout(binding = 0) uniform highp sampler2D u_sampler;

/// The four-component gather result is written to the graphics color attachment.
layout(location = 0) out mediump vec4 o_color;

void main(void)
{
    /// With the implicit component argument, textureGather samples component 0.
    o_color = textureGather(u_sampler, v_texCoord);
}
```

#### Additional Info

- `genGatherPrograms()` also emits a shared GLSL ES 3.10 pass-through vertex shader for this graphics case; it forwards position and `vec2` texture coordinates without changing the gather expression ([`vktShaderRenderTextureGatherTests.cpp#L1650-L1688`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2045-L2099)).
- The instance renders a quad with four vertices and six indices into a fixed 64 × 64 result; the selected `repeat`/`mirrored_repeat` sampler state is configured host-side ([`setupDefaultInputs()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1433-L1457), [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1459-L1497)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Pipeline | `compute` replaces the fragment output with an 8 × 8 local-size compute shader, explicit quad-coordinate interpolation, and a typed storage image; graphics keeps the fragment color output. | [`genGatherPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2045-L2117), [`genComputeShaderSource()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1766-L1867) |
| Gather type and offset size | `offset`, `offset_dynamic`, and `offsets` change the function name and add literal, dynamic, or four-constant offsets; implementation-range variants add `u_offset` where applicable and require `GL_EXT_gpu_shader5`. | [`genGatherFuncCall()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1920-L2016), [`genFragmentShaderSource()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1710-L1735) |
| Texture type and format | Array/cube types change coordinate dimensionality and sampler type; integer formats change the sampler and output to `isampler*`/`u sampler*` with `ivec4`/`uvec4` results, while depth uses shadow samplers and a reference coordinate. | [`getSamplerType()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L911-L943), [`getSamplerGatherResultType()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L945-L971) |
| Sparse backing | Sparse cases use `sparseTextureGather*ARB`, return a residency status, and select the gathered `texel` only when resident; regular cases assign the gather expression directly. | [`genGatherFuncCall()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1881-L1925), [`genFragmentShaderSource()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1744-L1759) |
| Level mode and view/sampler options | AMD bias/LOD adds the AMD extension and level argument; swizzle, filtering, wrap, and base-level variants primarily alter host image/sampler/view setup, with base-level and AMD mode affecting generated call inputs where applicable. | [`genGatherFuncCall()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1876-L1971), [`TextureGatherTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2971-L3125) |

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
; Bound: 22
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %v_texCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %u_sampler "u_sampler"
               OpName %v_texCoord "v_texCoord"
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %u_sampler Binding 0
               OpDecorate %u_sampler DescriptorSet 0
               OpDecorate %v_texCoord Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
  %u_sampler = OpVariable %_ptr_UniformConstant_11 UniformConstant
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
 %v_texCoord = OpVariable %_ptr_Input_v2float Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %u_sampler
         %18 = OpLoad %v2float %v_texCoord
         %21 = OpImageGather %v4float %14 %18 %int_0
               OpStore %o_color %21
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. Instance initialization checks required limits and extensions, creates and fills the texture, configures swizzle and base-mip view parameters, and binds the sampler ([initialization](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1282-L1431)).
2. For each internal iteration, the instance selects `frag_N` or `comp_N`, supplies quad coordinates and any dynamic range data, calls the shared setup, and renders or dispatches the `64 × 64` output ([iteration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1459-L1497), [uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1516-L1561)).
3. The shared path draws six indices for graphics or dispatches `8 × 8 × 1` compute workgroups, waits, and copies the result image to host-visible memory ([graphics/compute commands](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2506-L2556), [readback](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2558-L2587)).
4. Verification reconstructs per-pixel coordinates and offsets. Depth uses comparison precision; UNORM uses fixed-point thresholds plus validity checks; integer formats require exact component values unless the texture utility accepts another valid gather result ([verification dispatch](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1564-L1648)).
5. A failed iteration logs the rendered image and, when invalid pixels exist, a reference and error mask, then returns `Result verification failed`. Passing all internal iterations returns `Pass` ([verification logging](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L725-L736), [status path](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1499-L1513)).

## Failure Meaning

### Failure Cause Mapping

| Observable result or failing parameter | Meaning in the source-defined test |
|---|---|
| `NotSupportedError` | A required feature, extension, offset range, sparse capability, portability feature, or AMD format property is unavailable. This is not a gather-result mismatch. |
| Shader compilation or pipeline/setup failure | The generated GLSL form or its graphics/compute resource path could not execute; pixel verification was not reached. |
| `Result verification failed` | At least one pixel was neither the ideal gather value nor another result accepted by the texture-library validity rules. |
| Only `offset` / `offset_dynamic` / `offsets` fails | The corresponding single uniform/literal offset, per-pixel dynamic offset, or four-constant-offset path is implicated, together with the shared sampling and output path. |
| Only a format or compare branch fails | Sampler/result typing, component selection, integer handling, or depth comparison may be implicated. |
| Only `texture_swizzle`, `filter_mode`, `base_level`, sparse, or AMD leaves fail | The named image-view, sampler-state, mip-selection, residency, or AMD call path narrows the investigation but does not isolate a driver component. |
| Only `graphics` or `compute` fails | Stage-specific interpolation, descriptor/output setup, pipeline execution, or synchronization may differ; the common texture and oracle code still participates. |

### Cause Analysis

#### Gather operation or offset mismatch

**Possible failure symptoms:** Ordinary gathers pass while one offset family fails, or only extreme and dynamic offset iterations produce red error-mask pixels.

**Possible implementation causes:** The generated function overload, literal or uniform offset, pixel-to-offset expression, implementation limit, returned component order, or host-side offset functor may disagree. The failure result alone cannot distinguish shader lowering from test setup or reference reconstruction ([shader offsets](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1973-L2016), [oracle offset selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L889-L909)).

#### Texture, sampler, comparison, or view mismatch

**Possible failure symptoms:** Failures cluster by texture shape, wrap pair, component, signedness, depth compare mode, swizzle, filter mode, or base level.

**Possible implementation causes:** Coordinate interpolation, array-layer or cube-face selection, wrap handling, sampler/result typing, depth reference generation, image-view swizzle, or base-mip selection may be involved. A filter-only failure is especially relevant to the source's expectation that filtering state not change a gather, but still includes texture creation and oracle code.

#### Pipeline, sparse, or transfer mismatch

**Possible failure symptoms:** Unrelated operations fail only in graphics, compute, or sparse siblings, or output appears stale or uniformly replaced by the sparse fallback value.

**Possible implementation causes:** Stage interfaces, compute interpolation, storage-image typing, sparse residency reporting, descriptor binding, image barriers, dispatch/draw execution, or host readback may be involved. The final pixel comparison does not identify which layer caused the unexpected image.

## Case Pruning

### Requirement-based pruning

- Every concrete 2D, 2D-array, and cube case calls `requireDeviceCoreFeature(DEVICE_CORE_FEATURE_SHADER_IMAGE_GATHER_EXTENDED)` ([2D check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2275-L2287), [array check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2501-L2513), [cube check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2735-L2739)).
- Dynamic offsets, four-offset calls, and implementation-range calls require the extended gather syntax and emit `GL_EXT_gpu_shader5`; initialization checks `shaderImageGatherExtended` before execution ([requirement helper](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L860-L865), [runtime gate](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1288-L1294)).
- Implementation-range leaves check that device limits include at least `[-8, 7]`. Four-offset implementation leaves additionally require `[-32, 31]` because those values are compile-time constants ([limit checks](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1302-L1314), [four-offset case check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2280-L2286)).
- Depth-comparison cases skip on a portability-subset device without `mutableComparisonSamplers` ([portability check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1145-L1162)).
- AMD bias/LOD leaves require `VK_AMD_texture_gather_bias_lod` and a successful image-format query with `supportsTextureGatherLODBiasAMD` ([AMD checks](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1296-L1361)).
- Sparse leaves rely on the shared shader-render checks for `shaderResourceResidency`, `sparseBinding`, the applicable sparse residency image feature, and sparse format support ([shared sparse checks](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1328-L1345)). Sparse and AMD leaves are not registered in Vulkan SC builds.

A capability-based skip is distinct from `Result verification failed`: the former means that the source-defined prerequisite prevented execution; the latter means that an executed iteration produced an unacceptable image.

### Design-based pruning

- Cube is limited to `basic` because offset gather forms are not generated for cube samplers ([factory filter](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2881-L2886), [cube case note](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2675-L2684)).
- Extra swizzle, filter, and base-level branches are generally omitted for `min_required_offset`; `offsets.min_required_offset` retains them. The source treats feature dimensions and offset-range dimensions as largely orthogonal ([registration condition](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2971-L2974)).
- Swizzle is non-depth and graphics-only. The compute loop exits that format's additional-branch block before adding swizzle cases ([swizzle selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2975-L3013)).
- Filter registration omits nearest combinations already covered by ordinary leaves. Integer formats retain only `min_nearest_mipmap_nearest_mag_nearest` because other filtering is illegal or irrelevant for those formats ([filter pruning](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3015-L3075)).
- AMD modes are omitted for depth formats. Base levels are fixed to `1` and `2`, rather than enumerating every mip level ([level pruning](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3081-L3127)).
- Component selection and extreme offset vectors are not fully crossed. Array layer `0` and cube face zero receive all iterations; other layers/faces receive one representative iteration ([basic iteration pruning](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1023-L1070), [array pruning](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2310-L2336), [cube pruning](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2535-L2562)).

These are registration and iteration-design choices, not runtime skips.

## Key Takeaways

- `glsl.texture_gather` covers ordinary, single-offset, dynamic-offset, and four-offset gather behavior through both graphics and compute execution.
- Texture shape, color/depth format, comparison mode, wrap pair, component, offset range, size, swizzle, filtering state, base mip, sparse backing, and AMD bias/LOD form the source-defined behavior matrix.
- A leaf is not one shader invocation: it runs multiple generated component, offset, layer, or face iterations and stops at the first unacceptable image.
- The oracle evaluates every pixel with the matching texture view and sampler, accepting implementation-permitted gather uncertainty rather than requiring only one ideal value.
- Vulkan SC excludes sparse and AMD variants; the default mustpass therefore has 3,174 leaves versus 1,455 for Vulkan SC.
- A not-supported result identifies an unavailable prerequisite. `Result verification failed` proves that an executed complete path produced at least one invalid pixel, but does not isolate shader compilation, sampling hardware, pipeline state, sparse handling, transfer, or reference code.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Gather enums, result types, and iteration generation | [`vktShaderRenderTextureGatherTests.cpp#L818-L1080`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L818-L1080) | Defines the four operations, offset-range policy, sampler/result typing, component cases, and representative offsets. |
| Instance initialization and runtime loop | [`vktShaderRenderTextureGatherTests.cpp#L1205-L1562`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1205-L1562) | Checks prerequisites, creates resources, runs each iteration, binds uniforms, and returns status. |
| Software gather verification | [`vktShaderRenderTextureGatherTests.cpp#L618-L815`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L618-L815), [`#L1564-L1648`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1564-L1648) | Reconstructs per-pixel gathers, comparison results, precision, ideal images, and error masks. |
| Shader and function-call generation | [`vktShaderRenderTextureGatherTests.cpp#L1650-L2117`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1650-L2117) | Generates graphics/compute GLSL, ordinary/sparse/AMD calls, offsets, and output writes. |
| 2D, array, and cube implementations | [`vktShaderRenderTextureGatherTests.cpp#L2119-L2739`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2119-L2739) | Defines texture data, coordinates, layer/face iteration pruning, reference views, and per-shape support checks. |
| Family registration matrix | [`TextureGatherTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2821-L3135) | Creates pipeline, operation, range, texture, sampler, swizzle, filter, base-level, sparse, and AMD branches. |
| Public factory declaration and definition | [`vktShaderRenderTextureGatherTests.hpp#L23-L36`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.hpp#L23-L36), [`vktShaderRenderTextureGatherTests.cpp#L3139-L3142`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3139-L3142) | Exposes and constructs the `texture_gather` family. |
| GLSL package registration | [`vktTestPackage.cpp#L1253-L1272`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272) | Places `texture_gather` directly below `glsl`. |
| Shared graphics/compute execution | [`vktShaderRender.cpp#L2506-L2587`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2506-L2587) | Records draw or dispatch commands, submits work, and copies the image for verification. |
| Shared sparse-image support | [`vktShaderRender.cpp#L1328-L1345`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1328-L1345), [`#L1747-L1770`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1747-L1770) | Checks sparse prerequisites and selects sparse upload behavior. |
| Vulkan default mustpass coverage | [`vk-default/glsl.txt#L23590-L26763`](../../../mustpass/main/vk-default/glsl.txt#L23590-L26763) | Lists all 3,174 `dEQP-VK.glsl.texture_gather` leaves. |
| Vulkan SC default mustpass coverage | [`vksc-default/glsl.txt#L20569-L22023`](../../../mustpass/main/vksc-default/glsl.txt#L20569-L22023) | Lists all 1,455 `dEQP-VKSC.glsl.texture_gather` leaves. |
