## Overview

**Core question:** Do GLSL texture lookup, texel-fetch, and texture-query functions return results consistent with the configured image, sampler, coordinates, LOD controls, offsets, and shader stage?

- [`vktShaderRenderTextureFunctionTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L57-L8305) implements the `glsl.texture_functions` test family and its generated shader, texture, sampler, reference, and query-validation paths.
- Lookup cases cover implicit and explicit LOD selection, projection, explicit gradients, LOD clamps, offsets, depth comparison, sparse residency, and integer texel fetches. Query cases cover texture dimensions, multisample dimensions, sample counts, accessible mip levels, and computed LOD.
- The factory creates ordinary and sparse vertex, fragment, and compute variants where the case flags and support rules allow them. The page explains that generated matrix, shader construction, runtime checks, pruning, and failure interpretation.

## Background Knowledge

- A sampled-image operation combines an image view with sampler state. Normalized coordinates, filtering, mip selection, wrap mode, format interpretation, and comparison mode can all affect the returned value.
- Implicit-LOD sampling derives a level of detail from coordinate derivatives. Explicit-LOD calls supply the level directly, while gradient calls supply the derivatives used to calculate it. Projected forms divide texture coordinates by a projection component before lookup.
- `texelFetch` uses integer texel coordinates and does not perform normalized-coordinate filtering. Texture-query functions return image or sampler metadata rather than sampled texel values.
- Sparse lookup functions return both texel data and a residency code. The shader must check the code before treating the texel as resident.

## Registration Hierarchy

```text
glsl.texture_functions
├── texture
├── textureclamp
├── textureoffset
├── textureoffset_pcoffset
├── textureoffsetclamp
├── textureoffsetclamp_pcoffset
├── textureproj
├── textureprojoffset
├── textureprojoffset_pcoffset
├── texturelod
├── texturelodoffset
├── texturelodoffset_pcoffset
├── textureprojlod
├── textureprojlodoffset
├── textureprojlodoffset_pcoffset
├── texturegrad
├── texturegradclamp
├── texturegradoffset
├── texturegradoffset_pcoffset
├── texturegradoffsetclamp
├── texturegradoffsetclamp_pcoffset
├── textureprojgrad
├── textureprojgradoffset
├── textureprojgradoffset_pcoffset
├── texelfetch
├── texelfetchoffset
├── texelfetchoffset_pcoffset
└── query
```

`ShaderTextureFunctionTests::init()` creates these 28 direct children from case tables and registration loops ([factory and registration body](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4406-L8298)). `createCaseGroup()` appends stage suffixes and, outside Vulkan SC, adds eligible `sparse_` leaves ([case expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4948-L5007)). Offset families add a wrap-mode intermediate node before their generated leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Function behavior | Ordinary sampling, LOD clamp, projection, explicit LOD, explicit gradients, texel fetch, and metadata queries | Selects the GLSL operation and the reference rule used to check it. | [function classification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L57-L102), [query registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8027-L8296) |
| Texture type | 1D, 1D array, 2D, 2D array, 3D, cube, and cube array where the GLSL signature permits | Changes coordinate width, array-layer handling, projection forms, query result width, and required device features. | [sampler and coordinate selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2070-L2133), [query type tables](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8040-L8075) |
| Format and sampler class | Fixed-point normalized, floating-point, signed integer, unsigned integer, and depth-comparison configurations | Changes sampler type, returned scalar/vector type, filtering rules, scale/bias conversion, and comparison behavior. | [texture specifications](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5023-L5312) |
| Coordinates and LOD inputs | Source-defined coordinate ranges; optional bias or explicit LOD; explicit `dPdx` and `dPdy`; optional minimum-LOD clamp | Drives the lookup location and mip-selection path represented by each case-table row. | [`TextureLookupSpec`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L104-L149), [runtime input transforms](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1504-L1552) |
| Offset transport | No offset, a literal offset, or a `_pcoffset` push-constant offset | Distinguishes constant-offset GLSL from the maintenance8 non-constant offset path. | [shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2180-L2225), [push-constant upload](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1970-L1998) |
| Wrap mode for offset families | `clamp_to_edge`, `clamp_to_border`, `repeat`, `mirrored_repeat`, and `mirrored` | Exercises the sampler-addressing result when an offset moves a lookup toward or beyond an image edge. | [wrap table](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5009-L5022), [offset-family construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8007-L8025) |
| Execution stage | Vertex, fragment, and compute, subject to row flags and pruning | Moves the tested call between graphics stages and compute execution. Compute shaders reconstruct quad-varying inputs in a uniform buffer. | [stage expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4962-L5003), [compute interpolation source](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2187-L2280) |
| Image backing | Regular and, for eligible non-SC lookups, sparse | Changes image allocation and the GLSL call to the `sparse*ARB` form with an explicit residency check. | [sparse classes](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4478-L4505), [sparse operation generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4774-L4868) |
| Query mode | `texturesize`, `texturesizems`, `texturesamples`, `texturequerylevels`, and `texturequerylod` | Selects the returned metadata and the dedicated host-side oracle. `texturequerylod` also varies zero coordinate width, nonzero base level, and min/max LOD clamp modes. | [query case selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3988-L4005), [query registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8038-L8293) |
| Default mustpass profile | 7,907 Vulkan leaves and 5,948 Vulkan SC leaves; each profile has 435 query leaves | Records the generated cases selected by the two current default mustpass lists. The difference is concentrated in sparse-capable lookup coverage; query coverage is equal. | [Vulkan list](../../../mustpass/main/vk-default/glsl.txt#L15683-L23589), [Vulkan SC list](../../../mustpass/main/vksc-default/glsl.txt#L14621-L20568) |

The mustpass counts describe list membership, not results from executing the suite on the current host.

## Behavior Parameters

The primary behavioral axis is the operation group selected by the direct child name. Related direct children are combined below when they share one lookup mechanism and differ by clamp or offset controls.

### `texture*` sampling and LOD clamp

`texture`, `textureoffset`, and their clamp variants exercise ordinary filtered sampling. Fragment cases can use implicit derivatives; a source-defined bias can adjust the computed LOD. `textureclamp` and the `*clamp` variants apply a minimum LOD. Offset forms add either literal or push-constant texel offsets and run under each registered wrap mode ([ordinary shader operation construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2135-L2187), [clamped reference examples](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1034-L1065)).

### `textureproj*` projected sampling

`textureproj` and `textureprojoffset` test projected coordinate signatures. The generated call supplies the source coordinate vector, while the CPU evaluators divide the sampled coordinates by the appropriate projection component before evaluating the lookup. Offset and push-constant-offset variants retain that division and add sampler addressing behavior ([projection classification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L83-L89), [projected gradient reference forms](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1190-L1243)).

### `texturelod*` explicit-LOD sampling

`texturelod`, `texturelodoffset`, `textureprojlod`, and their offset variants pass a source-defined LOD to the GLSL call instead of deriving it from implicit derivatives. Projected forms combine explicit LOD with projection division. The reference path chooses the same LOD and applies the same texture and sampler configuration ([LOD classification](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L97-L102), [GLSL function-name selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2149-L2159)).

### `texturegrad*` explicit-gradient sampling

`texturegrad`, `texturegradoffset`, and the clamp variants supply explicit X and Y gradients. The reference evaluator derives LOD from those gradients, then samples the configured texture. Clamp variants bound the derived value from below; offset variants also apply literal or push-constant texel offsets ([gradient reference paths](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1070-L1167), [gradient-clamp paths](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1246-L1337)).

### `textureprojgrad*` projected-gradient sampling

`textureprojgrad` and its offset variants combine projection with explicit gradients. This separates coordinate projection from derivative supply: the lookup coordinates undergo the projection division, while the explicit gradients control mip selection ([projected-gradient reference paths](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1170-L1243)).

### `texelfetch*` integer fetches

`texelfetch` reads a specific integer texel coordinate from an explicit mip level. Offset forms add integer offsets before reading the texture level; they do not use normalized-coordinate filtering. The generated shader casts coordinates and LOD to integer types, and the C++ evaluator reads the corresponding level and texel directly ([fetch evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1371-L1407), [fetch registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L7974-L8025)).

### `query` metadata operations

The `query` child has five intermediate nodes. `texturesize` returns mip dimensions, `texturesizems` returns multisample image dimensions, `texturesamples` returns the sample count, `texturequerylevels` returns accessible mip levels, and `texturequerylod` returns a level/LOD pair derived from coordinates and sampler state. Dedicated instances compare these outputs with exact expected integers or source-calculated floating-point bounds ([query-instance dispatch](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3988-L4005), [generated query expressions](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4068-L4116)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.texture_functions.texturegrad.sampler2d_fixed_fragment
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `texturegrad` / `FUNCTION_TEXTUREGRAD` | Selects `textureGrad`, so the shader supplies both gradients explicitly rather than relying on implicit fragment derivatives. |
| `sampler2d_fixed` | Uses a normalized `GL_RGBA8` 2D texture, 256 x 256 texels with nine mip levels, and the repeat, linear-mipmap-nearest sampler. |
| Coordinate range `(-0.2, -0.4)` to `(1.5, 2.3)` | The host transforms the test quad's location-4 input across this range, including coordinates outside `[0, 1]` for repeat addressing. |
| X-gradient range `(0, 0)` to `(0.2, 0)`; Y gradient `(0, 0)` | Location 5 varies the explicit X gradient across the quad while location 6 remains zero, isolating one derivative component as required by this table row. |
| No offset, no LOD clamp, regular backing | Keeps the operation at the core four-argument `textureGrad` signature and uses the ordinary sampled-image path. |
| Fragment stage | `createCaseGroup()` appends `_fragment`; the companion vertex shader forwards the coordinate and gradients, while the fragment shader performs the tested lookup. |

#### Purpose

This shader checks that a fragment-stage `textureGrad` lookup on a mipmapped normalized 2D texture uses the source-provided gradients for mip selection and returns the value accepted by the CTS CPU texture evaluator.

#### Structural Design

| Shader-visible path | Role in the check |
|---|---|
| Locations 0-2 -> `v_texCoord`, `v_gradX`, `v_gradY` | Receive the coordinate and two explicit gradients forwarded from host-populated vertex attributes. |
| Set 0, binding 0 -> `u_sampler` | Combines the generated nine-level RGBA8 image with its repeat/linear-mipmap sampler. |
| `textureGrad(u_sampler, v_texCoord, v_gradX, v_gradY)` | Performs the operation under test; no implicit derivative, offset, projection, bias, or clamp argument is added. |
| Set 0, bindings 1-2 -> `u_scale`, `u_bias` | Convert the lookup result to the shared rendered-color comparison representation. |
| Location 0 -> `o_color` | Carries the final value into the shared image comparison path. |

#### Shader Code

```glsl
#version 450 core
/// Location 0 is the rendered comparison value consumed by the shared image oracle.
layout(location = 0) out mediump vec4 o_color;
/// Location 0 receives the interpolated high-precision 2D lookup coordinate produced by the companion vertex shader.
layout(location = 0) in highp vec2 v_texCoord;
/// Locations 1 and 2 carry the explicit X and Y gradients selected by this case; mip selection must use these values.
layout(location = 1) in highp vec2 v_gradX;
layout(location = 2) in highp vec2 v_gradY;
/// Set 0 binding 0 is the host-created 256x256, nine-level RGBA8 sampled image plus its repeat/linear-mipmap sampler.
layout(set = 0, binding = 0) uniform highp sampler2D u_sampler;
/// Bindings 1 and 2 are one-vec4 uniform buffers carrying host-derived format conversion factors.
layout(set = 0, binding = 1) uniform buf0 { highp vec4 u_scale; };
layout(set = 0, binding = 2) uniform buf1 { highp vec4 u_bias; };

void main()
{
	/// The tested operation supplies gradients explicitly, then converts the sampled value into the render target's comparison space.
	o_color = vec4(textureGrad(u_sampler, v_texCoord, v_gradX, v_gradY))*u_scale + u_bias;
}
```

#### Additional Info

- The exact leaf is registered by the `textureGradCases` row and `createCaseGroup(this, "texturegrad", ...)`, which expands its `ALL` flags into vertex, fragment, and compute leaves ([case row](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L7033-L7040), [stage expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4948-L5007)).
- The companion vertex shader is not shown because it does not execute the tested texture operation: for a fragment case it writes `gl_Position` and forwards `a_in0`, `a_in1`, and `a_in2` to the three fragment inputs ([graphics generator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2282-L2345), [forwarding branch](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2433-L2455)).
- Runtime setup binds the sampler at binding 0 and scale/bias UBOs at bindings 1 and 2; the selected 2D texture is populated with a mip-dependent grid before the shared renderer compares the image against `evalTexture2DGrad` ([uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1561-L1608), [2D texture initialization](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1629-L1661), [selected evaluator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L7037-L7040)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Function behavior | Other rows select `texture`, projected, explicit-LOD, projected-gradient, or `texelFetch` base names and add the corresponding coordinate casts and LOD, gradient, bias, projection, clamp, or offset arguments. | [function selection and argument construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2135-L2178), [operation emission](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2355-L2424) |
| Texture type and format class | Texture dimensionality changes coordinate and gradient widths; fixed/float, signed-integer, unsigned-integer, and comparison formats change the generated sampler type and result conversion. | [type derivation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2081-L2133) |
| Execution stage | A vertex leaf moves the lookup into the vertex shader and passes only its color to the fragment stage. A compute leaf instead declares an 8 x 8 workgroup, reconstructs quad-varying inputs from binding 3, and stores to binding 4. | [graphics interfaces](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2282-L2345), [compute generator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2187-L2280) |
| Offset source and LOD clamp | Offset rows append `Offset`, using either a literal integer vector or push-constant components; clamp rows append `ClampARB`, require the clamp extension, and add the selected minimum LOD. | [extensions and push constant](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2185-L2225), [operation suffixes and arguments](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2362-L2410) |
| Regular versus sparse backing | Eligible `sparse_` leaves use the separate sparse generator, an ARB sparse call, and an explicit residency-dependent fallback instead of this direct color assignment. | [sparse eligibility](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4953-L4997), [sparse shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4723-L4868) |

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
; Bound: 39
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %v_texCoord %v_gradX %v_gradY
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %u_sampler "u_sampler"
               OpName %v_texCoord "v_texCoord"
               OpName %v_gradX "v_gradX"
               OpName %v_gradY "v_gradY"
               OpName %buf0 "buf0"
               OpMemberName %buf0 0 "u_scale"
               OpName %_ ""
               OpName %buf1 "buf1"
               OpMemberName %buf1 0 "u_bias"
               OpName %__0 ""
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %u_sampler Binding 0
               OpDecorate %u_sampler DescriptorSet 0
               OpDecorate %v_texCoord Location 0
               OpDecorate %v_gradX Location 1
               OpDecorate %v_gradY Location 2
               OpDecorate %buf0 Block
               OpMemberDecorate %buf0 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %buf1 Block
               OpMemberDecorate %buf1 0 Offset 0
               OpDecorate %__0 Binding 2
               OpDecorate %__0 DescriptorSet 0
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
    %v_gradX = OpVariable %_ptr_Input_v2float Input
    %v_gradY = OpVariable %_ptr_Input_v2float Input
       %buf0 = OpTypeStruct %v4float
%_ptr_Uniform_buf0 = OpTypePointer Uniform %buf0
          %_ = OpVariable %_ptr_Uniform_buf0 Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
       %buf1 = OpTypeStruct %v4float
%_ptr_Uniform_buf1 = OpTypePointer Uniform %buf1
        %__0 = OpVariable %_ptr_Uniform_buf1 Uniform
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %u_sampler
         %18 = OpLoad %v2float %v_texCoord
         %20 = OpLoad %v2float %v_gradX
         %22 = OpLoad %v2float %v_gradY
         %23 = OpImageSampleExplicitLod %v4float %14 %18 Grad %20 %22
         %30 = OpAccessChain %_ptr_Uniform_v4float %_ %int_0
         %31 = OpLoad %v4float %30
         %32 = OpFMul %v4float %23 %31
         %36 = OpAccessChain %_ptr_Uniform_v4float %__0 %int_0
         %37 = OpLoad %v4float %36
         %38 = OpFAdd %v4float %32 %37
               OpStore %o_color %38
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- A lookup instance transforms the test grid into the case's coordinate, LOD/bias, or gradient ranges; creates and fills the requested texture; binds the sampler plus scale and bias uniforms; and supplies push constants when requested ([instance setup](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1461-L1608), [texture initialization](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1611-L1968)).
- `TexLookupEvaluator` calls the table-selected CPU evaluator for each reference sample. The shared shader-render instance executes the graphics draw or compute dispatch, builds the matching reference image, and returns pass only when image comparison succeeds ([evaluator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1409-L1429), [shared iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [comparison selection](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).
- Query cases use a one-pixel result for their metadata checks. `TextureSizeInstance` iterates image sizes, mip levels, and base levels, compares only defined LOD results, and skips type/size combinations that cannot represent a valid image ([size iterations and checking](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2880-L3035)).
- Multisample size and sample-count instances iterate supported sample counts. Integer multisample formats that expose no count above one produce a not-supported result rather than a false test failure ([multisample support handling](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3138-L3155), [sample-count comparison](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3379-L3409)).
- `TextureQueryLevelsInstance` calculates the accessible mip count after the selected base level and requires the shader's integer result to match ([level-count check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3479-L3604)). `TextureQueryLodInstance` accepts the returned level and LOD only within bounds that account for derivative precision, sampler filtering, accessible levels, and selected min/max LOD controls ([LOD bounds and check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3698-L3839)).
- The `texturesize.oob_lod` special case dispatches multiple compute invocations with valid and out-of-range LODs. The host checks only invocations whose LOD is valid because out-of-range results are undefined ([special-case shader and validation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4238-L4401)).

## Failure Meaning

A failure means that the complete generated lookup or query path did not produce the result accepted by its oracle. An image mismatch in a lookup case can involve shader compilation or execution, coordinate and LOD handling, image/sampler state, texture data, sparse residency handling, reference evaluation, or shared rendering. A query failure means the returned metadata lies outside the exact value or permitted range calculated by its dedicated instance.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `texture*` sampling and LOD clamp | Implicit derivative, bias, minimum-LOD clamp, filtering, comparison, wrap, offset, or sampler-state handling. |
| `textureproj*` projected sampling | Projection division, projected signature lowering, offset addressing, or the common sampling path. |
| `texturelod*` explicit-LOD sampling | Explicit LOD selection, projected explicit-LOD handling, offset addressing, or mip sampling. |
| `texturegrad*` explicit-gradient sampling | Gradient transport, gradient-to-LOD calculation, minimum-LOD clamp, offset addressing, or mip sampling. |
| `textureprojgrad*` projected-gradient sampling | Projection division combined with explicit-gradient LOD selection and optional offset addressing. |
| `texelfetch*` integer fetches | Integer coordinate/LOD conversion, offset addition, mip selection, or direct texel addressing. |
| `query` metadata operations | Texture dimension, sample-count, accessible-level, or LOD-query result generation and transport. |

Every row also depends on image creation and binding, shader compilation, pipeline execution, result transfer, and the corresponding host oracle.

### Cause Analysis

#### Sampling, projection, LOD, and gradient handling

**Possible failure symptoms:** A lookup image differs from the CPU reference, often in one operation group, sampler configuration, mip range, wrap mode, or stage while nearby cases pass.

**Possible implementation causes:** The generated call can disagree with expected GLSL behavior in coordinate projection, derivative or explicit-LOD use, gradient interpretation, LOD clamping, filtering, comparison sampling, or offset addressing. Texture creation, sampler mapping, scale/bias conversion, and the CPU reference also participate, so the mismatch alone does not identify a compiler or device defect.

#### Integer texel addressing

**Possible failure symptoms:** A `texelfetch*` leaf returns different texels from the reference, with failures potentially concentrated on one mip, offset direction, texture type, format class, or stage.

**Possible implementation causes:** Integer coordinate conversion, array-layer selection, explicit mip choice, offset addition, format interpretation, or direct image addressing can differ from the source-defined reference. The failing leaf and logged image comparison are needed to separate those causes from setup or harness errors.

#### Texture-query result handling

**Possible failure symptoms:** A query case reports `Got unexpected result`, or a `texturequerylod` result lies outside the logged level and LOD bounds. Multisample cases can instead report not supported when the format has no usable multisample count.

**Possible implementation causes:** The shader can return incorrect dimensions, sample counts, accessible levels, or computed LOD values. Image-view base level, sampler min/max LOD, derivative precision, result-component packing, or host-side expected-value calculation can also affect the observed comparison. The status does not isolate one source without the failing query mode and log.

#### Sparse residency and shared execution path

**Possible failure symptoms:** Only `sparse_` leaves show unexpected colors, or many unrelated regular and query leaves fail during compilation, setup, execution, or readback.

**Possible implementation causes:** Sparse image binding, residency-code handling, extension lowering, or fallback-color behavior can affect sparse-only failures. Broad failures can come from shared descriptor setup, graphics or compute pipeline creation, synchronization, rendering, result transfer, or comparison. Source-level investigation of the failing case is required.

## Case Pruning

### Requirement-based pruning

- Cube-array lookup instances require `imageCubeArray`; unsupported devices return not supported ([feature check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1431-L1439)).
- Depth-comparison cases require `mutableComparisonSamplers` when `VK_KHR_portability_subset` is present and exposes that feature gate ([portability check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1442-L1458)).
- Lookup cases with a LOD clamp require `shaderResourceMinLod` ([instance check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1494-L1502)). `_pcoffset` cases require `VK_KHR_maintenance8` ([support check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2047-L2053)).
- Compute cases that rely on implicit derivatives require `VK_KHR_compute_shader_derivatives` and `computeDerivativeGroupQuads`. Explicit-LOD, explicit-gradient, and texel-fetch compute cases do not use that gate ([compute support check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2054-L2065)).
- Multisample query instances retain only sample counts supported by the format and image usage. An integer format with no supported count above one is reported as not supported ([sample-count filtering](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3138-L3155)).

### Design-based pruning

- Source case flags decide whether each row receives vertex, fragment, and compute leaves. The generator does not force every stage onto every GLSL signature ([stage expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4962-L5003)).
- `_pcoffset` rows omit compute leaves because the generator retains compute only when `pcOffset` is false; the source comment records the constant-offset requirement ([compute condition](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4990-L5002)).
- Sparse variants exist only outside Vulkan SC. They exclude projected functions, 1D textures, 1D arrays, and cube arrays ([sparse eligibility](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4955-L4969)).
- `texturesizems` registers vertex and fragment leaves only. `texturequerylod` registers fragment leaves only, while ordinary `texturesize`, `texturesamples`, and `texturequerylevels` rows include vertex, fragment, and compute forms ([query loops](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8077-L8293)).
- Query instances skip incompatible texture dimensions, cube-array layer counts, or base levels during their internal iteration. `textureSize` observes out-of-range LOD values but does not compare them because GLSL leaves those results undefined ([size-case filtering](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2974-L3035)).

Runtime not-supported results come from requirement-based pruning. The registration and internal-loop exclusions above are generator design choices, not evidence of a failed test.

## Key Takeaways

- `glsl.texture_functions` covers sampled lookups, projected forms, explicit LOD and gradients, LOD clamps, offsets, integer fetches, sparse residency, and five metadata-query behaviors.
- Case tables define texture, sampler, coordinate, LOD, gradient, offset, and stage inputs. Registration loops add wrap-mode, push-constant-offset, sparse, and query variants without creating a full Cartesian product.
- Lookup cases compare rendered or compute-written images with a CPU texture evaluator. Query cases use dedicated exact-value or bounded-value checks.
- Feature gates and design pruning explain why some texture types, stages, sparse paths, or sample counts do not execute on every profile or device.
- A failed leaf identifies the operation, texture/sampler configuration, and stage that produced an unacceptable result. It does not by itself prove whether the fault lies in shader lowering, Vulkan state, device execution, reference calculation, or shared test infrastructure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Function and lookup specification | [`Function` and `TextureLookupSpec`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L57-L149) | Defines the operation classes and all coordinate, LOD, gradient, offset, and clamp inputs. |
| CPU lookup evaluator | [`TexLookupEvaluator`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1409-L1429) | Dispatches each lookup case to its table-selected C++ reference function. |
| Lookup runtime instance | [`ShaderTextureFunctionInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1461-L1998) | Prepares attributes, uniforms, push constants, textures, and regular or sparse backing. |
| Regular lookup case and shader generator | [`ShaderTextureFunctionCase`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2001-L2480) | Performs support checks and emits stage-specific GLSL lookup calls. |
| Query instances | [`TextureSizeInstance` through `TextureQueryLodInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2760-L3948) | Implements the metadata-specific iteration and validation rules. |
| Query case and shader generator | [`TextureQueryCase`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3950-L4231) | Selects a query instance and emits graphics or compute query shaders. |
| Out-of-bounds `textureSize` special case | [`SpecialCases`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4234-L4404) | Checks valid invocations in a mixed valid/out-of-range LOD compute dispatch. |
| Sparse lookup implementation | [`SparseShaderTextureFunctionCase`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4478-L4946) | Emits sparse GLSL, checks residency, and creates sparse-backed instances outside Vulkan SC. |
| Stage and sparse case expansion | [`createCaseGroup()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4948-L5007) | Converts each case-table row into supported stage and sparse leaves. |
| Test-family registration | [`ShaderTextureFunctionTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5009-L8298) | Defines samplers, textures, lookup tables, offset loops, and query children. |
| Public factory declaration | [`vktShaderRenderTextureFunctionTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.hpp#L22-L38) | Exposes `createTextureFunctionTests()`. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272) | Attaches `texture_functions` below `glsl`. |
| Shared image oracle | [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730) | Executes the regular render/compute path, builds the reference image, and returns pass or image mismatch. |
| Vulkan default mustpass coverage | [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L15683-L23589) | Lists 7,907 `dEQP-VK.glsl.texture_functions` leaves. |
| Vulkan SC default mustpass coverage | [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L14621-L20568) | Lists 5,948 `dEQP-VKSC.glsl.texture_functions` leaves. |
