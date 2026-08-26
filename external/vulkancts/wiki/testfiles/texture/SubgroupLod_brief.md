# Understanding Brief: `texture.subgroup_lod`

## One-Sentence Test Purpose

These Vulkan-only tests check whether vertex-shader `texelFetch`, `textureGrad`, and `textureLod` operations select the intended mip level when different rectangle vertices request different levels.

## Background Knowledge

### Mip levels and explicit level selection

A mipmapped image contains progressively smaller versions of one base image. A shader can select among them by supplying an integer level to a texel fetch, a floating-point LOD to an explicit sample, or explicit coordinate gradients from which the sampler calculates LOD.

Why it matters here:
- Each tested mip level contains one solid color, so the returned color identifies the selected level.
- The three test cases isolate three different SPIR-V routes: integer `Lod` on `OpImageFetch`, floating-point `Lod` on `OpImageSampleExplicitLod`, and `Grad` on `OpImageSampleExplicitLod`.

The Vulkan sampling chapter distinguishes sampling from fetching: sampling can filter neighboring texels through a sampler, while `OpImageFetch` returns one texel and does not use sampler state ([sampling instruction overview](../../../../vulkan-docs/src/chapters/textures.adoc#L7-L29)). Integer fetch coordinates address a level selected by an integer `Lod` operand ([integer coordinates](../../../../vulkan-docs/src/chapters/textures.adoc#L160-L206), [integer texel coordinate operations](../../../../vulkan-docs/src/chapters/textures.adoc#L2028-L2053)).

### Explicit gradients

For an explicit-gradient image instruction, the `Grad` operands provide the coordinate derivatives used for LOD selection ([derivative image operations](../../../../vulkan-docs/src/chapters/textures.adoc#L1315-L1353)). The sampler converts their texel-space footprint into a LOD, applies LOD bounds, and selects an image level ([scale factor and LOD selection](../../../../vulkan-docs/src/chapters/textures.adoc#L1525-L1531), [LOD operation](../../../../vulkan-docs/src/chapters/textures.adoc#L1654-L1698)).

The registered name `subgroup_lod` does not mean these shaders execute Vulkan subgroup operations. The scripts contain no subgroup extension, built-in, or instruction. Their distinguishing setup is per-vertex LOD selection within one draw.

## One Concrete Example

For `dEQP-VK.texture.subgroup_lod.texturegrad`, Amber creates two mip levels. Level 0 is red and level 1 is green. The tested vertex shader reconstructs as follows from the literal GLSL in the recipe:

```glsl
#version 430
layout(location = 0) in vec3 position_in;
layout(location = 0) out vec4 color_out;
layout(set = 0, binding = 0) uniform highp sampler2D tex;

void main() {
  gl_Position = vec4(position_in, 1.0);
  // Vary dPdx and dPdy based on vertex index to force
  // LOD 0 or LOD 1.
  vec2 v = vec2(0);
  if (gl_VertexIndex % 2 != 0)
      v = vec2(1);

  color_out = vec4(textureGrad(tex, vec2(0.5), v, v));
}
```

Even vertex indices supply zero gradients and must select the red base level. Odd indices supply unit gradients in both directions; against a 512 by 512 base image, that footprint reaches the coarser available level and must return green. The fragment shader only copies this vertex output to the framebuffer. Amber inspects the four exact rectangle corners, where interpolation reproduces each vertex's value.

## End-to-End Test Flow

```text
[host] register one Amber recipe for each direct child of texture.subgroup_lod
[host] parse the selected recipe and compile its inline GLSL to SPIR-V 1.0
[host] create the mipmapped B8G8R8A8_UNORM image, framebuffer image, sampler, and graphics pipelines
[device] clear each texture mip level through a level-specific color attachment view
[device] clear the output framebuffer to opaque black
[host] issue one 512 by 512 DRAW_RECT command
[device] run four tested vertex invocations with index-dependent LOD inputs
[device] interpolate each returned color and copy it through the fragment shader
[host] let Amber evaluate four one-pixel corner EXPECT commands
[host] return Pass only if every exact RGBA expectation succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- C++ loads `texture_lod.amber`, `texture_grad.amber`, or `texel_fetch.amber` according to the registered test case leaf ([Amber registration](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L38-L51)).
- Every recipe contains an inline tested GLSL vertex shader, a fixed GLSL fragment shader, and an Amber `PASSTHROUGH` vertex shader for mip clearing.
- Amber defines one graphics pipeline per mip level plus one tested `lod_pipeline`. The four-level recipes therefore define five pipelines; `texture_grad.amber` defines three.
- Since the scripts specify no alternate shader target, `AmberTestCase::initPrograms` chooses SPIR-V 1.0 and adds each GLSL stage with that build option ([Amber shader compilation](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L499)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `texture` | yes | yes, as per-level color attachment and set 0 binding 0 combined image sampler | cleared, then read | no direct readback | A distinct solid color identifies each selected mip level. |
| `sampler` | yes | yes, with `texture` | used by sampled operations; ignored by texel-fetch semantics | no | Sets `MAX_LOD` to cover the recipe's mip range. |
| `framebuffer` | yes | yes, as color attachment 0 | cleared and written | inspected through Amber `EXPECT` | Carries the sampled colors to exact corner checks. |
| rectangle position input | generated by Amber's `DRAW_RECT` | yes, at location 0 | read by the tested vertex shader | no | Produces four vertex indices and four framebuffer corners. |
| vertex-to-fragment `color_out`/`color_in` | pipeline interface, not a host resource | yes | written, interpolated, then read | no | Transports the selected mip color to the color attachment. |

## What Is Checked

| Test case leaf | Mip colors | Shader choice | Exact expected corner colors at `(0,511)`, `(511,0)`, `(511,511)`, `(0,0)` |
|----------------|------------|---------------|----------------------------------------------------------------------------------|
| `texelfetch` | red, green, blue, yellow | integer level `gl_VertexIndex % 4`; center coordinate scales as `256 >> lod` | red, yellow, blue, green |
| `texturegrad` | red, green | zero gradients for even vertices; unit gradients for odd vertices | red, green, red, green |
| `texturelod` | red, green, blue, yellow | floating-point LOD `gl_VertexIndex % 4` | red, yellow, blue, green |

Amber performs exact `EQ_RGBA` checks on one pixel at each corner. There is no tolerance, whole-image comparison, or C++-side reference calculation.

## Behavior Parameter Identification

> **Behavior parameter:** direct test case leaf
>
> **Candidate values:** `texelfetch`, `texturegrad`, `texturelod`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `texelfetch` | Incorrect integer-coordinate fetch, integer `Lod` level selection, or lowering of `texelFetch`/`OpImageFetch`. |
| `texturegrad` | Incorrect handling of explicit `Grad` operands, derivative-to-LOD calculation or clamping, or lowering of `textureGrad`. |
| `texturelod` | Incorrect floating-point explicit-LOD selection, image-level clamping, or lowering of `textureLod`. |

A failure shared by all three values can also come from mip-level attachment views or clears, sampled-image binding, vertex output transport, rasterization, framebuffer writes, or Amber result handling.

## Important Variations and Special Cases

- `texelfetch` uses integer texel coordinates and does not depend on sampler filtering. It changes its integer coordinate with the mip extent so every request remains near the center of the selected level.
- `texturelod` samples normalized coordinate `(0.5, 0.5)` and passes the level as a floating-point `Lod` operand.
- `texturegrad` has only two levels. It passes either zero or unit vectors as both explicit gradients, creating a base-level versus coarse-level contrast.
- The colors fill complete mip levels. This removes within-level coordinate and filter precision from the expected result.
- All three cases are absent from Vulkan SC builds. They are graphics cases and cannot run with the CTS compute-only option.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Texture dispatcher | [vktTextureTests.cpp#L48-L66](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Adds `subgroup_lod` only to the Vulkan test tree. |
| Test case registration | [vktTextureSubgroupLodTests.cpp#L38-L62](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L38-L62) | Maps the three exact leaf names to their Amber files. |
| `texelfetch` recipe | [texel_fetch.amber#L18-L105](../../../data/vulkan/amber/texture/subgroup_lod/texel_fetch.amber#L18-L105) | Defines four mips, integer fetch logic, draw, and expected corners. |
| `texturegrad` recipe | [texture_grad.amber#L18-L90](../../../data/vulkan/amber/texture/subgroup_lod/texture_grad.amber#L18-L90) | Defines the explicit-gradient contrast and two-color expectations. |
| `texturelod` recipe | [texture_lod.amber#L18-L103](../../../data/vulkan/amber/texture/subgroup_lod/texture_lod.amber#L18-L103) | Defines explicit floating-point LOD selection and four-color expectations. |
| Amber compilation | [vktAmberTestCase.cpp#L435-L499](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L499) | Shows the default SPIR-V 1.0 target and stage-specific GLSL insertion. |
| Amber execution/result | [vktAmberTestCase.cpp#L546-L615](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Supplies compiled binaries, executes the recipe, and maps success to CTS Pass. |
| Vulkan mustpass | [texture.txt#L15770-L15774](../../../mustpass/main/vk-default/texture.txt#L15770-L15774) | Confirms exactly three Vulkan executable paths. |
| Sampling and LOD semantics | [textures.adoc#L1287-L1353](../../../../vulkan-docs/src/chapters/textures.adoc#L1287-L1353) | Defines normalized operations and explicit derivative operands. |
| Integer fetch LOD semantics | [textures.adoc#L2028-L2053](../../../../vulkan-docs/src/chapters/textures.adoc#L2028-L2053) | Defines integer `Lod` level selection for image fetches. |

## Questions / Risk Points for User Audit

- Is it clear that `subgroup_lod` is a registered historical name rather than evidence of subgroup instructions?
- Does the concrete `texturegrad` example make the zero-gradient and unit-gradient level choices understandable?
- Are the Amber-created images, pipeline interface values, and host expectations distinguished clearly?
- Is exact corner validation described without implying a whole-framebuffer comparison?

No unresolved semantic risk remains after checking registration, all three recipes, the default Vulkan mustpass, Amber compilation/execution, and the Vulkan sampling chapter.

## Conversion Notes for Final Wiki Rewrite

- Keep the three direct test case leaves as the behavior axis and preserve their exact order: `texelfetch`, `texturegrad`, `texturelod`.
- Use `texturegrad` for the representative walkthrough because it exercises explicit derivative-to-LOD calculation, while the variation table can contrast integer fetch and direct floating-point LOD.
- Distill the background to mip levels, explicit gradients, and the fact that the registered name does not imply subgroup instructions.
- Preserve the exact corner table and the resource initialization sequence; they explain the complete oracle better than source narration.
- Copy the `### Failure Cause Mapping` table unchanged into the final page. Write cause analysis separately.
- Keep detailed C++ and Amber entry points in the source appendix.
