## Overview

**Core question:** Do vertex-shader texture operations select the mip level requested by an integer level, explicit gradients, or an explicit floating-point LOD?

- This page covers `texture.subgroup_lod`, a Vulkan-only test family with three direct Amber test case leaves: `texelfetch`, `texturegrad`, and `texturelod`.
- The C++ source registers those leaves and maps each one to an Amber recipe. The recipes contain the pipelines, shaders, mip initialization, draw command, and exact result checks.
- Each mip level has a different solid color. The color at a framebuffer corner therefore identifies the level selected for the corresponding rectangle vertex.
- Despite the registered name, these tests do not use Vulkan subgroup operations. They vary LOD inputs between vertex invocations in one draw.

## Background Knowledge

For the shared concepts of texture coordinates and LOD, see [Background Knowledge](../../categories/texture.md#background-knowledge) of the `texture` page.

- `textureGrad` supplies two explicit coordinate derivatives. Vulkan uses those derivatives to calculate LOD, applies the sampler's LOD bounds, and then selects an image level. `textureLod` bypasses derivative calculation by supplying the floating-point LOD directly.
- `texelFetch` uses integer texel coordinates and fetches one texel from the integer level. It does not use sampler filtering.

## Registration Hierarchy

```text
texture.subgroup_lod
├── texelfetch
├── texturegrad
└── texturelod
```

All three children are direct executable test case leaves. The family and its children are omitted from Vulkan SC builds.

## Parameter Dimensions and Observed Values

The source does not generate a parameter matrix. Each operation is one fixed Amber case, but the recipes choose different mip counts and per-vertex inputs.

| Dimension | Observed values | Meaning in this test | Evidence |
|-----------|-----------------|----------------------|----------|
| Test case leaf | `texelfetch`, `texturegrad`, `texturelod` | Selects the texture operation and the way the shader requests a mip level. | [registration](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L38-L51) |
| Mip count | 4 for `texelfetch` and `texturelod`; 2 for `texturegrad` | Provides enough distinct solid-color levels to identify each requested result. | [fetch recipe](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L47-L49), [gradient recipe](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L50-L52), [LOD recipe](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L45-L47) |
| Request selected by `gl_VertexIndex` | integer levels 0 through 3; zero or unit gradients; floating-point LODs 0 through 3 | Makes the four rectangle corners carry results from different level-selection inputs. | [fetch shader](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L20-L33), [gradient shader](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L20-L36), [LOD shader](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L20-L31) |
| Validation sample positions | `(0,511)`, `(511,0)`, `(511,511)`, `(0,0)` | Checks one pixel at each exact framebuffer corner, where the interpolated color equals the corresponding vertex output. | [fetch expectations](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L101-L105), [gradient expectations](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L86-L90), [LOD expectations](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L99-L103) |

## Behavior Parameters

The primary behavioral axis is the direct test case leaf. Each leaf changes the texture instruction and the source of its mip-level choice.

### `texelfetch`: integer-coordinate fetch

This case checks `texelFetch` with `lod = gl_VertexIndex % 4`. The shader adjusts the integer center coordinate to the selected mip extent with `256 >> lod`, then fetches one texel. Four solid-color levels make an incorrect integer level visible at a corner.

### `texturegrad`: explicit-gradient sampling

This case checks `textureGrad` with zero gradients for even vertex indices and unit gradients for odd indices. The zero-gradient path selects the red base level. Against the 512 by 512 base image, the unit-gradient path produces a texel-space footprint large enough to exceed the sampler's `MAX_LOD` of 2.0; the sampler clamps the LOD to 2, and image-level selection then clamps it to level 1 because the image has only two levels. The odd vertices therefore return the green coarser level.

### `texturelod`: explicit floating-point LOD sampling

This case checks `textureLod` at normalized coordinate `(0.5, 0.5)`. Each vertex passes `float(gl_VertexIndex % 4)`, so the four corners must carry the colors of levels 0, 3, 2, and 1 in rectangle-vertex order.

## Shader Analysis

One walkthrough is enough because the recipes share the same graphics path and validation method. `texturegrad` is representative because its explicit `Grad` operands exercise derivative-to-LOD calculation; the variation table contrasts the direct integer and floating-point level forms.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.texture.subgroup_lod.texturegrad
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `texturegrad` | Uses explicit gradient vectors instead of an integer or floating-point LOD operand. |
| even versus odd `gl_VertexIndex` | Alternates between zero gradients and unit gradients, which must select different available mip levels. |
| two mip levels | Gives the gradient calculation a clear red base-level result and green coarse-level result. |

#### Purpose

The vertex shader checks whether explicit `Grad` operands produce the expected LOD choice for each rectangle vertex. The selected mip's solid color becomes the vertex output and later reaches an exact framebuffer-corner check.

#### Structural Design

| Shader phase | Operation | Observable consequence |
|--------------|-----------|------------------------|
| Position | Copy `position_in` to `gl_Position`. | Places each generated vertex at one rectangle corner. |
| Gradient choice | Use `(0,0)` for even indices and `(1,1)` for odd indices. | Alternates base-level and coarse-level requests. |
| Sample | Call `textureGrad` at normalized coordinate `(0.5,0.5)`. | Returns red from level 0 or green from level 1. |
| Output | Store the sampled color in `color_out`. | The fixed fragment shader writes that color to the framebuffer. |

#### Shader Code

```glsl
#version 430

layout(location = 0) in vec3 position_in;
layout(location = 0) out vec4 color_out;
/// Set 0 binding 0 combines the two-level B8G8R8A8_UNORM image with the sampler. Level 0 is red and level 1 is green.
layout(set = 0, binding = 0) uniform highp sampler2D tex;

void main() {
  /// Amber supplies the four corners of one rectangle at location 0; each vertex index selects one gradient pair.
  gl_Position = vec4(position_in, 1.0);
  // Vary dPdx and dPdy based on vertex index to force
  // LOD 0 or LOD 1.
  vec2 v = vec2(0);
  if (gl_VertexIndex % 2 != 0)
      v = vec2(1);

  /// Zero gradients select the base mip; unit gradients select the coarser available mip.
  color_out = vec4(textureGrad(tex, vec2(0.5), v, v));
}
```

#### Additional Info

- The fragment shader does not make a separate level-selection decision. It copies the interpolated location 0 input to color attachment 0.
- The recipe requests no alternate shader target, so the Amber test harness compiles the inline GLSL for SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| `texelfetch` | Replaces `textureGrad` with `texelFetch`, computes integer levels 0 through 3, and scales the integer center coordinate for each mip. | [fetch shader](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L20-L33) |
| `texturegrad` | Uses the shown zero or unit vectors as both explicit gradient operands. | [gradient shader](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L20-L36) |
| `texturelod` | Replaces explicit gradients with a floating-point LOD from `gl_VertexIndex % 4`. | [LOD shader](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L20-L31) |

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
; Bound: 52
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %position_in %gl_VertexIndex %color_out
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpName %_ ""
               OpName %position_in "position_in"
               OpName %v "v"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %color_out "color_out"
               OpName %tex "tex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpDecorate %position_in Location 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %color_out Location 0
               OpDecorate %tex Binding 0
               OpDecorate %tex DescriptorSet 0
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
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%position_in = OpVariable %_ptr_Input_v3float Input
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
    %float_0 = OpConstant %float 0
         %31 = OpConstantComposite %v2float %float_0 %float_0
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_2 = OpConstant %int 2
       %bool = OpTypeBool
         %41 = OpConstantComposite %v2float %float_1 %float_1
  %color_out = OpVariable %_ptr_Output_v4float Output
         %43 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %44 = OpTypeSampledImage %43
%_ptr_UniformConstant_44 = OpTypePointer UniformConstant %44
        %tex = OpVariable %_ptr_UniformConstant_44 UniformConstant
  %float_0_5 = OpConstant %float 0.5
         %49 = OpConstantComposite %v2float %float_0_5 %float_0_5
       %main = OpFunction %void None %3
          %5 = OpLabel
          %v = OpVariable %_ptr_Function_v2float Function
         %19 = OpLoad %v3float %position_in
         %21 = OpCompositeExtract %float %19 0
         %22 = OpCompositeExtract %float %19 1
         %23 = OpCompositeExtract %float %19 2
         %24 = OpCompositeConstruct %v4float %21 %22 %23 %float_1
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
               OpStore %v %31
         %34 = OpLoad %int %gl_VertexIndex
         %36 = OpSMod %int %34 %int_2
         %38 = OpINotEqual %bool %36 %int_0
               OpSelectionMerge %40 None
               OpBranchConditional %38 %39 %40
         %39 = OpLabel
               OpStore %v %41
               OpBranch %40
         %40 = OpLabel
         %47 = OpLoad %44 %tex
         %50 = OpLoad %v2float %v
         %51 = OpImageSampleExplicitLod %v4float %47 %49 Grad %50 %50
               OpStore %color_out %51
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The C++ registration selects one of three Amber scripts. Amber parses the script and compiles its inline vertex and fragment GLSL.
- Amber creates a `B8G8R8A8_UNORM` mipmapped `texture`, a `B8G8R8A8_UNORM` `framebuffer`, and a sampler whose `MAX_LOD` covers the recipe's range.
- A separate graphics pipeline binds each mip level as a color attachment and clears it to a unique solid color. Levels 0 through 3 are red, green, blue, and yellow. The gradient case uses only the first two levels.
- The tested `lod_pipeline` binds the texture and sampler at set 0, binding 0, clears the 512 by 512 framebuffer to opaque black, and executes one `DRAW_RECT`.
- The tested vertex shader produces a sampled color for each rectangle vertex. The fragment shader copies the interpolated color to the framebuffer.
- Amber checks one pixel at each corner with exact `EQ_RGBA` comparisons:

| Test case leaf | Expected colors at `(0,511)`, `(511,0)`, `(511,511)`, `(0,0)` |
|----------------|-------------------------------------------------------------------|
| `texelfetch` | red, yellow, blue, green |
| `texturegrad` | red, green, red, green |
| `texturelod` | red, yellow, blue, green |

Amber returns success only if all four expectations pass. `AmberTestInstance::iterate` maps that result to CTS `Pass` or `Fail`; this family has no separate C++ reference calculation.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `texelfetch` | Incorrect integer-coordinate fetch, integer `Lod` level selection, or lowering of `texelFetch`/`OpImageFetch`. |
| `texturegrad` | Incorrect handling of explicit `Grad` operands, derivative-to-LOD calculation or clamping, or lowering of `textureGrad`. |
| `texturelod` | Incorrect floating-point explicit-LOD selection, image-level clamping, or lowering of `textureLod`. |

A failure shared by all three values can also come from mip-level attachment views or clears, sampled-image binding, vertex output transport, rasterization, framebuffer writes, or Amber result handling.

### Cause Analysis

#### Integer fetch and level selection

**Possible failure symptoms:** One or more `texelfetch` corners contain the color of the wrong mip level or retain the black clear color.

**Possible implementation causes:** The implementation may lower the GLSL fetch to the wrong SPIR-V image operation, mishandle the integer `Lod`, select the wrong image-view level, or calculate the integer coordinate against the wrong mip extent. Vulkan defines an integer `Lod` on `OpImageFetch` as an offset from the image view's base level.

#### Explicit-gradient LOD calculation

**Possible failure symptoms:** Even corners do not return red, odd corners do not return green, or a corner remains black in `texturegrad`.

**Possible implementation causes:** The implementation may lower the explicit gradients incorrectly, calculate the texture footprint or logarithmic LOD incorrectly, or apply the sampler LOD bounds incorrectly. The generated SPIR-V carries the two vectors on the `Grad` operands of `OpImageSampleExplicitLod`, so this case does not depend on implicit fragment derivatives.

#### Explicit floating-point LOD selection

**Possible failure symptoms:** A `texturelod` corner reports a solid color belonging to a different numbered level or remains black.

**Possible implementation causes:** The implementation may lower the floating-point `Lod` operand incorrectly, apply image-level selection or LOD bounds incorrectly, or address the wrong level in the image view. Vulkan assigns an explicit `Lod` directly to the base LOD before applying the configured bounds.

#### Shared graphics or Amber path

**Possible failure symptoms:** Several or all corners fail across more than one test case, often with swapped level colors or the framebuffer's black clear value.

**Possible implementation causes:** Source inspection points to shared setup paths that can produce the same observation: per-level color attachment views and clears, combined image sampler binding, vertex-to-fragment transport, framebuffer rendering, or Amber's exact expectation processing. The corner result alone cannot distinguish these shared causes; test logs and source-level investigation are needed.

## Case Pruning

### Requirement-based pruning

- The dispatcher and family registration exclude `subgroup_lod` when `CTS_USES_VULKANSC` is defined, so these paths exist only in the Vulkan test tree.
- The recipes declare no optional feature or extension requirements. Amber checks script requirements before execution, but these three scripts add none.
- Amber rejects graphics recipes when CTS runs with `--deqp-compute-only=enable`; these cases use vertex and fragment shaders.

### Design-based pruning

- Each behavior is one fixed test case rather than a generated cross-product. The recipes use the mip counts needed to distinguish their operation's level choices.
- Every mip is a solid color. This design removes within-level coordinate precision and filtering variation from the expected result.
- Amber checks the four exact corners instead of the whole framebuffer because those pixels reproduce the four per-vertex outputs without an interpolation mixture.

## Key Takeaways

- `subgroup_lod` is a historical registered name; the shaders contain no subgroup operations.
- The three leaves isolate integer fetch LOD, explicit gradients, and explicit floating-point LOD while sharing one color-coded mip oracle.
- One draw produces vertex-dependent level requests: four distinct levels in `texelfetch` and `texturelod`, and alternating base/coarse requests in `texturegrad`. Four exact corner checks reveal which mip each vertex selected.
- See `Failure Meaning` for operation-specific and shared failure causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Texture dispatcher | [vktTextureTests.cpp#L48-L66](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Adds `subgroup_lod` to the Vulkan texture category and excludes it from Vulkan SC. |
| Family registration | [vktTextureSubgroupLodTests.cpp#L38-L62](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L38-L62) | Registers the three exact leaves and maps them to Amber files. |
| `texelfetch` recipe | [texel_fetch.amber#L18-L105](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L18-L105) | Defines integer fetch logic, four colored levels, the draw, and corner checks. |
| `texturegrad` recipe | [texture_grad.amber#L18-L90](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L18-L90) | Defines the explicit-gradient shader, two colored levels, and alternating expectations. |
| `texturelod` recipe | [texture_lod.amber#L18-L103](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L18-L103) | Defines floating-point explicit LOD selection and four-level expectations. |
| Amber compilation | [vktAmberTestCase.cpp#L435-L499](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L499) | Shows the default SPIR-V 1.0 target and stage-specific GLSL compilation. |
| Amber execution and result | [vktAmberTestCase.cpp#L546-L615](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Executes the recipe with compiled shaders and maps the Amber result to CTS status. |
| Default Vulkan mustpass | [texture.txt#L15770-L15774](../../../mustpass/main/vk-default/texture.txt#L15770-L15774) | Lists exactly the three executable Vulkan paths. |
| Explicit gradients and LOD operands | [textures.adoc#L1315-L1353](../../../../vulkan-docs/src/chapters/textures.adoc#L1315-L1353) | Defines derivative inputs and direct floating-point `Lod` handling. |
| LOD and image-level selection | [textures.adoc#L1654-L1720](../../../../vulkan-docs/src/chapters/textures.adoc#L1654-L1720) | Defines LOD bounds and conversion to an image level. |
| Integer fetch LOD | [textures.adoc#L2028-L2053](../../../../vulkan-docs/src/chapters/textures.adoc#L2028-L2053) | Defines level selection for integer-coordinate fetches. |
