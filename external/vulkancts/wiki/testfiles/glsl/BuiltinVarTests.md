## Overview

**Core question:** Do fragment-stage built-in variables and mixed shader input paths produce the values required by the draw that generated each fragment?

- [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1) registers and implements `glsl.builtin_var`.
- The six test families cover `gl_FrontFacing`, fragment depth output, multisample `gl_FragCoord`, basic `gl_FragCoord` and `gl_PointCoord` use, and combinations of a built-in, an interpolated varying, and a push constant.
- Cases either compare a rendered image with a CPU reference or copy shader-recorded values to host memory and inspect them.
- The factory generates 111 leaves. Both the Vulkan and Vulkan SC default GLSL mustpass lists contain the same 111 normalized `glsl.builtin_var` paths, with only the profile prefix changed.

## Background Knowledge

- Fragment built-ins connect rasterization to the fragment shader. `gl_FrontFacing` reports the facing selected for a fragment, `gl_FragCoord` carries window-relative coordinates, and `gl_PointCoord` carries coordinates within a rasterized point. A shader can write `gl_FragDepth` to replace the fragment's depth value.
- Multisampling gives a pixel several sample locations. Sample shading can run a fragment invocation for an individual sample, while centroid interpolation requires a value chosen inside the covered samples of the pixel.
- An image oracle predicts final colors or depths. A recording oracle instead stores a built-in value in an image, copies that image to host memory, and checks the recorded components and locations.

## Registration Hierarchy

```text
glsl.builtin_var
├── frontfacing
├── fragdepth
├── fragcoord_msaa
├── fragcoord_msaa_input
├── simple
└── input_variations
```

[`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690) creates these six direct children, and [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1272) attaches `builtin_var` under `glsl`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `frontfacing`, `fragdepth`, `fragcoord_msaa`, `fragcoord_msaa_input`, `simple`, `input_variations` | Selects the built-in property and the validation method. | [factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690) |
| `frontfacing` input mode | `none`, `add_ubo_load` | Chooses a direct red/green result or a path that combines `gl_FrontFacing` with a fragment uniform load. | [registration loops](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2568-L2622), [shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L318-L364) |
| `frontfacing` topology | `point_list`, `line_list`, `triangle_list`, `triangle_strip`, `triangle_fan` | Changes the primitive type that supplies facing. | [topology table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2570-L2585) |
| `frontfacing` cull mode | `none`, `front`, `back`, `front_and_back` under `add_ubo_load`; `simple` under `none` | Checks facing together with primitive culling. The `none` input mode has one `simple` leaf per topology. | [cull table and expansion](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2587-L2618) |
| `fragdepth` topology prefix | `point_list`, `line_list`, `triangle_list` | Runs the depth-writing path with three registered primitive choices. The source maps the registered `triangle_list` prefix to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`. | [topology table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2627-L2638) |
| `fragdepth` depth row | `d16_unorm_no_depth_clamp`, `x8_d24_unorm_pack32_no_depth_clamp`, `d32_sfloat_no_depth_clamp`, `d16_unorm_s8_uint_no_depth_clamp`, `d24_unorm_s8_uint_no_depth_clamp`, `d32_sfloat_s8_uint_no_depth_clamp`, `d32_sfloat_large_depth`, `d32_sfloat`, `d32_sfloat_s8_uint`, `d32_sfloat_multisample_2`, `d32_sfloat_multisample_4`, `d32_sfloat_multisample_8`, `d32_sfloat_multisample_16`, `d32_sfloat_multisample_32`, `d32_sfloat_multisample_64` | Selects depth format, unrestricted depth, depth clamping, or sample count. | [depth case table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2640-L2663) |
| MSAA sample count | `1_bit`, `2_bit`, `4_bit`, `8_bit`, `16_bit`, `32_bit`, `64_bit` | Selects the rasterization sample count for both `fragcoord_msaa` families. | [sample-count table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2522-L2545) |
| `fragcoord_msaa_input` mode | base name, `_no_sample_shading`, `_no_sample_shading_centroid_interpolation` | Chooses sample shading, pixel-frequency shading, or pixel-frequency shading with a `Centroid` decoration on `gl_FragCoord`. | [mode expansion](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2537-L2565), [shader builders](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1568-L1685) |
| `simple` leaf | `fragcoord_xyz`, `fragcoord_w`, `pointcoord`, `pointcoord_uniform_frag`, `pointcoord_uniform_vert` | Selects the coordinate components and whether a scale uniform is absent, read in the fragment stage, or read in the vertex stage. | [direct registration](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2509-L2520) |
| `input_variations` bits | `input_none`, `input_builtin`, `input_varying`, `input_builtin_varying`, `input_constant`, `input_builtin_constant`, `input_varying_constant`, `input_builtin_varying_constant` | Selects all eight combinations of `gl_FrontFacing`, an interpolated color, and a fragment push constant. | [name construction](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2275-L2301), [registration loop](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687) |

The generated leaf counts reconcile with mustpass registration:

| Test family | Expansion | Leaves |
|-------------|-----------|-------:|
| `frontfacing` | 5 topologies × (1 `simple` + 4 UBO/cull cases) | 25 |
| `fragdepth` | 3 topology prefixes × 15 depth rows | 45 |
| `fragcoord_msaa` | 7 sample counts | 7 |
| `fragcoord_msaa_input` | 7 sample counts × 3 modes | 21 |
| `simple` | 5 direct leaves | 5 |
| `input_variations` | 8 input-bit combinations | 8 |
| **Total** | | **111** |

The Vulkan list records these leaves at [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L3913-L4023). The Vulkan SC list records the corresponding paths at [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L3050-L3160).

## Behavior Parameters

The test family is the primary behavioral axis because each direct child tests a different fragment built-in contract or shader input path.

### `frontfacing`: primitive facing and culling

The fragment shader turns `gl_FrontFacing` into a visible color. The UBO variant adds a uniform value to `1.0` or `-1.0`, then varies cull mode so the reference renderer can check facing and primitive removal together. Five primitive topologies cover points, lines, and triangle-based primitives.

### `fragdepth`: fragment-written depth

A first pass reads a controlled depth value, writes it to `gl_FragDepth`, and records covered sample locations. A second pass samples the depth attachment and writes per-sample values into an `R32_SFLOAT` storage image. The matrix changes primitive topology, depth format, clamping, unrestricted values, and multisample count.

### `fragcoord_msaa`: sample-shaded fragment coordinates

A sample-shaded fragment invocation stores `gl_FragCoord` in a per-sample slot selected with `gl_SampleID`. Host checks then compare the stored coordinate against the rules for pixel bounds, depth, reciprocal clip `w`, uniqueness, and standard sample positions when the device reports them.

### `fragcoord_msaa_input`: pixel- and sample-frequency coordinate input

This family reuses the multisample recorder but adds pixel-frequency variants. The base leaves use sample shading, `_no_sample_shading` records one coordinate for the pixel, and `_no_sample_shading_centroid_interpolation` applies the SPIR-V `Centroid` decoration to `gl_FragCoord`. The host uses mode-specific checks, including the pixel-center rule for non-sample-shaded, non-centroid leaves.

### `simple`: analytical coordinate checks

`fragcoord_xyz` and `fragcoord_w` render values derived from `gl_FragCoord` and compare them with analytical CPU references. The three point-coordinate leaves render 16 points and compare `gl_PointCoord` against a CPU point-rasterization reference. Their uniform variants move the same scale input between fragment and vertex consumption.

### `input_variations`: combinations of fragment inputs

Three bits independently enable `gl_FrontFacing`, an interpolated varying color, and a fragment push constant. The generated shader adds the selected contributions to a base color, while the host constructs the same combination for each pixel. This checks that built-in, varying, and constant input paths remain correct when used alone or together.

## Shader Analysis

The representative walkthrough uses the most complete `input_variations` leaf because one short fragment shader exposes all three optional input paths. Other families use different shader and runtime mechanisms, which the behavior and runtime sections describe.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.builtin_var.input_variations.input_builtin_varying_constant
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `input_builtin` | Enables the `gl_FrontFacing` conditional. |
| `input_varying` | Adds the interpolated RGB value received at location 0. |
| `input_constant` | Adds `pc.color` from the fragment push-constant block. |

#### Purpose

The shader checks whether one fragment invocation can consume a rasterization built-in, an interpolated stage input, and a push constant without changing their combined result.

#### Structural Design

| Step | Shader action |
|------|---------------|
| Base | Initialize `o_color` to `(0.1, 0.2, 0.3, 1.0)`. |
| Built-in | Add the varying contribution only for front-facing fragments. |
| Varying | Read interpolated RGB from `a_color`. |
| Constant | Add `pc.color` after the facing-dependent contribution. |

#### Shader Code

```glsl
#version 450
/// Location 0 receives the color interpolated from the vertex shader.
layout(location = 0) in highp vec4 a_color;
/// The host supplies one vec4 push constant to the fragment stage.
layout(push_constant) uniform PCBlock {
  vec4 color;
} pc;
layout(location = 0) out highp vec4 o_color;
void main (void)
{
    o_color = vec4(0.1, 0.2, 0.3, 1.0);
    /// gl_FrontFacing gates the interpolated contribution.
    if (gl_FrontFacing)
        o_color += vec4(a_color.xyz, 0.0);
    o_color += pc.color;
}
```

#### Additional Info

- The matching vertex shader forwards attribute location 1 to fragment location 0. The fragment shader is primary here because it consumes and combines all selected inputs.
- The host push-constant value is `(0.1, 0.05, 0.2, 0.0)` and the CPU reference adds the same value.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Built-in bit | Removing it deletes the `if (gl_FrontFacing)` line, so the color contribution applies to both facings. | [fragment specialization](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2471-L2486) |
| Varying bit | Removing it deletes both varying declarations and replaces the interpolated contribution with the fixed value `(0.3, 0.2, 0.1, 0.0)`. | [vertex and fragment specialization](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2464-L2484) |
| Constant bit | Removing it deletes the push-constant block and the `pc.color` addition. | [constant specialization](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2474-L2486) |

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
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %gl_FrontFacing %a_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %gl_FrontFacing "gl_FrontFacing"
               OpName %a_color "a_color"
               OpName %PCBlock "PCBlock"
               OpMemberName %PCBlock 0 "color"
               OpName %pc "pc"
               OpDecorate %o_color Location 0
               OpDecorate %gl_FrontFacing BuiltIn FrontFacing
               OpDecorate %a_color Location 0
               OpDecorate %PCBlock Block
               OpMemberDecorate %PCBlock 0 Offset 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
%float_0_100000001 = OpConstant %float 0.100000001
%float_0_200000003 = OpConstant %float 0.200000003
%float_0_300000012 = OpConstant %float 0.300000012
    %float_1 = OpConstant %float 1
         %14 = OpConstantComposite %v4float %float_0_100000001 %float_0_200000003 %float_0_300000012 %float_1
       %bool = OpTypeBool
%_ptr_Input_bool = OpTypePointer Input %bool
%gl_FrontFacing = OpVariable %_ptr_Input_bool Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %a_color = OpVariable %_ptr_Input_v4float Input
    %v3float = OpTypeVector %float 3
    %float_0 = OpConstant %float 0
    %PCBlock = OpTypeStruct %v4float
%_ptr_PushConstant_PCBlock = OpTypePointer PushConstant %PCBlock
         %pc = OpVariable %_ptr_PushConstant_PCBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v4float = OpTypePointer PushConstant %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %o_color %14
         %18 = OpLoad %bool %gl_FrontFacing
               OpSelectionMerge %20 None
               OpBranchConditional %18 %19 %20
         %19 = OpLabel
         %24 = OpLoad %v4float %a_color
         %25 = OpVectorShuffle %v3float %24 %24 0 1 2
         %27 = OpCompositeExtract %float %25 0
         %28 = OpCompositeExtract %float %25 1
         %29 = OpCompositeExtract %float %25 2
         %30 = OpCompositeConstruct %v4float %27 %28 %29 %float_0
         %31 = OpLoad %v4float %o_color
         %32 = OpFAdd %v4float %31 %30
               OpStore %o_color %32
               OpBranch %20
         %20 = OpLabel
         %39 = OpAccessChain %_ptr_PushConstant_v4float %pc %int_0
         %40 = OpLoad %v4float %39
         %41 = OpLoad %v4float %o_color
         %42 = OpFAdd %v4float %41 %40
               OpStore %o_color %42
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `frontfacing` draws six fixed vertices through the selected topology and cull mode. A software reference draw computes the expected image. `intThresholdPositionDeviationCompare()` accepts exact channel values with one-pixel positional deviation.
- `fragdepth` allocates a depth attachment, marker image, control buffer, and resolved-depth image. The first draw writes depth and marker data. The second draw reads each depth sample and stores it in a single-sample image. Transfer commands copy both result images to host-visible buffers, and `validateDepthBuffer()` checks covered and uncovered samples with a `0.001` tolerance.
- `fragcoord_msaa` and `fragcoord_msaa_input` render to a multisample image while fragment code records `gl_FragCoord`. The test copies those records to host memory. `validateSampleLocations()` checks `z` and `w`, in-pixel bounds, uniqueness where required, standard sample positions when advertised, and the pixel-center rule for the applicable pixel-frequency cases.
- `simple.fragcoord_xyz` compares the rendered image with CPU window-coordinate calculations. `simple.fragcoord_w` computes the projected interpolation reference and uses a `0.00001` component tolerance. The point-coordinate leaves compare 16 generated points with a CPU reference using a `0.02` fuzzy threshold.
- `input_variations` creates a push-constant range only when the constant bit is present, renders indexed triangles, and builds a CPU image from the selected contributions. `pixelThresholdCompare()` uses the channel threshold `(2, 2, 2, 2)`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `frontfacing` | Facing or culling does not produce the reference image for the selected topology. |
| `fragdepth` | Fragment-written depth, depth attachment behavior, per-sample resolve, or readback differs from the controlled depth values. |
| `fragcoord_msaa` | Sample-shaded `gl_FragCoord` values violate the checked coordinate or sample-location rules. |
| `fragcoord_msaa_input` | Pixel-frequency, sample-frequency, or centroid `gl_FragCoord` behavior violates its mode-specific checks. |
| `simple` | Analytical `gl_FragCoord` or `gl_PointCoord` values differ from the rendered output beyond the family tolerance. |
| `input_variations` | A built-in, varying, push constant, or their generated combination produces the wrong pixel color. |

Shared setup, synchronization, image transfer, or CPU-reference defects can also produce a mismatch in more than one family. A failed comparison identifies a disagreement at the checked output; it does not isolate one pipeline stage by itself.

### Cause Analysis

#### Facing or culling disagreement

**Possible failure symptoms:** `frontfacing` produces wrong red/green pixels or wrong scalar UBO results, including pixels that should have been removed by the selected cull mode.

**Possible implementation causes:** Incorrect primitive facing, cull application, `gl_FrontFacing` delivery, descriptor-backed uniform reads, or shader lowering can produce this image. The software reference and Vulkan draw use the same topology and cull parameters, so framework-side vertex or reference setup is another source-level investigation point.

#### Fragment depth or depth readback disagreement

**Possible failure symptoms:** A covered sample differs from its controlled depth by more than `0.001`, or an uncovered sample does not retain the expected default depth.

**Possible implementation causes:** The discrepancy can arise while lowering `gl_FragDepth`, applying depth clamping or unrestricted depth, storing the chosen depth format, sampling a multisample depth attachment, writing the resolve image, or copying it to host memory. The marker image distinguishes covered samples from untouched samples but does not identify which earlier step changed the depth.

#### Sample-shaded coordinate disagreement

**Possible failure symptoms:** A recorded coordinate has wrong `z` or `w`, lies outside its pixel, duplicates a location that should be unique, or differs from an advertised standard sample location.

**Possible implementation causes:** Fragment coordinate generation, sample-ID association, sample shading, storage-image addressing, or readback can corrupt the recorded tuple. Device-reported standard sample locations also participate in the expected-value calculation.

#### Pixel-frequency or centroid coordinate disagreement

**Possible failure symptoms:** A non-sample-shaded record misses the required pixel center, or a centroid-decorated coordinate falls outside the accepted covered region or fails the shared coordinate checks.

**Possible implementation causes:** Invocation-frequency selection, the `Centroid` decoration on `gl_FragCoord`, coverage handling, storage writes, or readback can produce the symptom. The CTS source uses inline SPIR-V for the centroid form, so investigation should compare that module and pipeline mode with the failing record.

#### Analytical coordinate disagreement

**Possible failure symptoms:** `fragcoord_xyz`, `fragcoord_w`, or a point-coordinate leaf produces pixels outside its stated component or fuzzy threshold.

**Possible implementation causes:** Window-coordinate generation, reciprocal clip-`w` interpolation, point rasterization, `gl_PointCoord` generation, uniform consumption, or color conversion can change the rendered value. CPU reference construction and generated point bounds are also relevant source-level checks.

#### Mixed input color disagreement

**Possible failure symptoms:** `input_variations` differs from the CPU image by more than `(2, 2, 2, 2)`, with the error tied to one or more enabled contributions.

**Possible implementation causes:** `gl_FrontFacing`, vertex-to-fragment interpolation, push-constant delivery, generated conditional control flow, or color attachment output can alter the sum. A failure shared by several bit combinations can narrow investigation to their common enabled input, but the comparison alone does not prove the faulty stage.

## Case Pruning

### Requirement-based pruning

- `frontfacing` triangle-fan cases throw `NotSupportedError` when `VK_KHR_portability_subset` is present and its `triangleFans` feature is false. The source compiles this query out for Vulkan SC.
- `fragdepth` requires `fragmentStoresAndAtomics`, `sampleRateShading`, the selected depth format and sample count, and storage-image support for `VK_FORMAT_R8G8B8A8_UINT`. `d32_sfloat_large_depth` also requires `VK_EXT_depth_range_unrestricted`; the two depth-clamp rows require `depthClamp`.
- The multisample coordinate instance requires `sampleRateShading`, `fragmentStoresAndAtomics`, the selected `R32G32B32A32_SFLOAT` color sample count, and storage-image support. In the inspected source, this constructor check also applies to the no-sample-shading leaves.
- These checks skip an unsupported case before its output comparison. They do not remove the registered path from the Vulkan or Vulkan SC mustpass inventory.

### Design-based pruning

- `frontfacing.none` fixes culling to `VK_CULL_MODE_NONE` and registers one `simple` leaf per topology. The four cull-mode leaves appear only under `add_ubo_load`.
- `fragdepth` combines only the three registered topology prefixes with the 15 explicit depth rows. No other format, topology, clamping, or sample-count combination belongs to this matrix.
- `fragcoord_msaa` contains only sample-shaded leaves. Pixel-frequency and centroid variants belong to `fragcoord_msaa_input`.
- `input_variations` enumerates the complete three-bit set, so it needs eight leaves and no duplicate ordering variants.

## Key Takeaways

- One source file owns six behaviorally distinct families and generates exactly 111 registered leaves.
- The tests use two kinds of oracle: final-image comparisons for visible coordinate or input effects, and storage-image readback for depth and multisample coordinate records.
- `fragcoord_msaa_input` separates sample-frequency, pixel-frequency, and centroid behavior even though all three use the same sample-count names.
- The registered `fragdepth.triangle_list_*` names map to triangle-strip topology in the inspected source; the documentation preserves the registered identifiers and records the implementation mapping.
- A comparison failure establishes a mismatch at the observed image or record. See `Failure Meaning` for the mechanisms that can contribute to each family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| GLSL package registration | [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1272) | Attaches `builtin_var` under `glsl`. |
| Group factory | [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690) | Defines direct children, parameter tables, loops, and leaf names. |
| Front-facing shader and support check | [`BuiltinGlFrontFacingCase`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L285-L383) | Generates both fragment variants and checks triangle-fan portability support. |
| Front-facing execution and comparison | [`BuiltinGlFrontFacingCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L159-L283) | Runs the Vulkan and software-reference draws. |
| Fragment-depth execution | [`BuiltinFragDepthCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L468-L1041) | Builds depth, marker, resolve, transfer, and readback resources. |
| Fragment-depth validation | [`validateDepthBuffer()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1043-L1087) | Defines covered-sample and tolerance checks. |
| Multisample coordinate shaders | [`BuiltinFragCoordMsaaTestCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1568-L1685) | Generates sample-shaded GLSL and centroid-decorated SPIR-V paths. |
| Sample-location validation | [`validateSampleLocations()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1394-L1530) | Checks coordinate components, pixel bounds, uniqueness, and sample positions. |
| Simple coordinate cases | [`fragcoord_xyz`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1837-L1938), [`fragcoord_w`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1951-L2053), [`pointcoord`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2067-L2273) | Implements analytical window and point-coordinate comparisons. |
| Input-variation shader generation | [`BuiltinInputVariationsCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2436-L2490) | Specializes the three optional input paths. |
| Input-variation execution | [`BuiltinInputVariationsCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2303-L2408) | Supplies vertices and push constants, builds the CPU reference, and compares pixels. |
| Vulkan default mustpass | [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L3913-L4023) | Lists all 111 `dEQP-VK.glsl.builtin_var` leaves. |
| Vulkan SC default mustpass | [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L3050-L3160) | Lists the corresponding 111 `dEQP-VKSC.glsl.builtin_var` leaves. |
