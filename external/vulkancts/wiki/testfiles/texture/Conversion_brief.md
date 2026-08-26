# Understanding Brief: `texture.conversion`

## One-Sentence Test Purpose

This test checks three conversion boundaries: negative values stored in an unsigned packed-float image, the most-negative SNORM encoding sampled as floating point, and SNORM values returned after linear filtering.

## Background Knowledge

### Unsigned floating-point image components

`VK_FORMAT_B10G11R11_UFLOAT_PACK32` has unsigned floating-point R, G, and B components. Negative shader values therefore cannot survive a store to that format as negative values. The format definition identifies the 10-bit B and 11-bit G/R components as unsigned floating point.

Why it matters here:

- The Amber case writes positive and negative `vec4` components through `imageStore`.
- A second shader loads the converted texels and expects each negative component to have become zero.

The numeric-format table and packed-format definition appear in the Vulkan specification's [Identification of Formats](../../../../vulkan-docs/src/chapters/formats.adoc#L1620-L1644) and [`VK_FORMAT_B10G11R11_UFLOAT_PACK32` definition](../../../../vulkan-docs/src/chapters/formats.adoc#L468-L472).

### SNORM conversion and post-processing clamp

A signed normalized component with `b` bits converts to `max(c / (2^(b-1) - 1), -1.0)`. This makes both the lowest ordinary endpoint and the extra two's-complement value map to `-1.0`. The specification also permits an implementation to carry a value below `-1.0` through intermediate processing such as texture filtering, but requires the value returned to the shader to be clamped.

Why it matters here:

- The `snorm_clamp` Amber cases place the most-negative bit pattern in a one-texel image and require every present channel to sample as exactly `-1.0`.
- The C++ `snorm_clamp_linear` cases fill a 7 by 7 texture with values at or near the negative endpoint, apply linear filtering, compare against a software lookup model, and separately reject any shader-visible component outside `[-1,1]`.

The governing conversion and filtering rule is in [Conversion From Normalized Fixed-Point to Floating-Point](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L1682-L1717).

## One Concrete Example

Consider `dEQP-VK.texture.conversion.snorm_clamp.r8_snorm`.

The Amber script creates a one-texel `VK_FORMAT_R8_SNORM` image filled with integer `-128`, binds it to a `sampler1D`, and draws a 32 by 32 rectangle. The fragment shader samples the texel and checks the one present channel:

```glsl
vec4 color = texture(tex_sampler, 0.0);
if (color[0] != -1.0)
    frag_out = vec4(1, 0, 0, 1);
else
    frag_out = vec4(0, 1, 0, 1);
```

Amber requires every framebuffer pixel to be opaque green. A red pixel means the most-negative SNORM encoding did not become exactly `-1.0` at the shader interface. The other twelve scripts use the same check with the format's channel count and either an 8-bit, 16-bit, or packed most-negative component pattern.

## End-to-End Test Flow

```text
1. ufloat_negative_values
[host] register one Amber recipe and declare a 50x50 B10G11R11 optimal-tiling storage image requirement
[host] compile two compute shaders from the recipe
[device] dispatch a 10x10-local-size shader over 5x5 workgroups and store coordinate-derived positive and negative values
[device] dispatch one verifier invocation, load all 2500 converted texels, and compare them with max(original, 0)
[device] write one integer pass flag
[host/Amber] require that flag to equal 1 and return pass or fail

2. snorm_clamp
[host] register one Amber recipe for each of 13 SNORM formats and declare a one-texel sampled-image requirement
[host] create the one-texel image with the most-negative component encoding and a 32x32 color target
[device] draw a rectangle and sample the SNORM texel in the fragment shader
[device] write green only when every present sampled channel equals -1.0
[host/Amber] compare the full framebuffer with opaque green and return pass or fail

3. snorm_clamp_linear
[host] choose one of 13 SNORM formats, derive a format-specific output size, and fill matching hardware/software 7x7 textures with an endpoint-focused pattern
[host] create a repeat-addressed linear sampler and generate the shared 2D float sampling programs
[device] sample the full [0,1] coordinate range into an R32G32B32A32_SFLOAT output image
[host] generate a software reference with the same texture data, coordinates, and sampler model
[host] run computeTextureLookupDiff with bounded coordinate, LOD, and color precision
[host] scan every rendered vec4 again and reject any component below -1.0 or above +1.0
[host] pass only when both checks report zero bad pixels
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`populateUfloatNegativeValuesTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L291-L322) loads one Amber recipe containing a writer compute shader and a verifier compute shader.
- [`populateSnormClampTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L324-L380) maps 13 registered leaves to 13 Amber recipes. Their fragment shaders share one structure but vary the image format, fill encoding, and number of checked channels.
- [`SnormLinearClampTestCase::initPrograms`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L281-L285) asks `initializePrograms` for `PROGRAM_2D_FLOAT` with high precision and an `R32G32B32A32_SFLOAT` output. The shared generator emits fragment and compute programs.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 50x50 `B10G11R11_UFLOAT_PACK32` storage image | yes | yes | written, then read | no | The image store performs the unsigned-float conversion under test. |
| One-int Amber result buffer | yes | yes | written | yes, through Amber expectation handling | Aggregates all 2500 unsigned-float comparisons. |
| One-texel SNORM sampled image | yes | yes | read | no | Holds the exact most-negative encoding for each direct sampling case. |
| 32x32 `B8G8R8A8_UNORM` Amber framebuffer | yes | yes | written | yes, through Amber expectation handling | Encodes exact per-fragment success as green. |
| 7x7 C++ SNORM hardware texture | yes | yes | read | no | Supplies the endpoint-focused pattern to Vulkan sampling. |
| Host-side 7x7 software texture | yes | no | no | used directly by host | Supplies identical texels to the software reference and lookup verifier. |
| `R32G32B32A32_SFLOAT` renderer output | yes | yes | written | yes | Preserves sampled float values for tolerance-based comparison and the explicit range scan. |
| Linear repeat sampler and renderer uniform/geometry data | yes | yes | read | no | Define filtering, coordinates, and the graphics or compute renderer plumbing. |

## What Is Checked

| Test family | Checked value | Check location | Pass condition |
|-------------|---------------|----------------|----------------|
| `ufloat_negative_values` | All 2500 loaded RGB values after storage conversion | verifier compute shader plus Amber `EXPECT` | Each loaded value equals `max(input, 0)`, so the result buffer remains `1`. |
| `snorm_clamp` | Every present component of the one sampled texel, for every framebuffer fragment | fragment shader plus Amber framebuffer expectation | Each checked component equals exactly `-1.0` and all 32x32 pixels are opaque green. |
| `snorm_clamp_linear` | Complete rendered float image versus software sampling model | host `computeTextureLookupDiff` | `numFailedPixels == 0` under the configured lookup and LOD precision. |
| `snorm_clamp_linear` | Every component of every rendered pixel | direct host range scan | No component lies below `-1.0` or above `+1.0`. |

The linear verifier masks absent channels, uses `derivateBits = 18`, `lodBits = 5`, `uvwBits = (5,5,0)`, and `coordBits = (20,20,0)`. Its color threshold is `0.9 / colorDistance` per component. A case passes only when the lookup-difference check and range scan both succeed.

## Behavior Parameter Identification

> **Behavior parameter:** test family below `texture.conversion`
>
> **Candidate values:** `ufloat_negative_values`, `snorm_clamp`, `snorm_clamp_linear`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ufloat_negative_values` | Incorrect negative-to-unsigned packed-float image-store conversion, storage-image load/store behavior, or device-side verification transport. |
| `snorm_clamp` | Incorrect conversion of the most-negative SNORM encoding to shader-visible `-1.0`, format/component handling, sampled-image access, or exact framebuffer signaling. |
| `snorm_clamp_linear` | Incorrect SNORM decoding or linear filtering near the negative endpoint, failure to clamp the returned value to `[-1,1]`, or a mismatch in generated renderer, upload, or readback behavior. |

A broad failure across families can also come from shared image-format capability reporting, image creation, shader compilation, descriptor binding, synchronization, or result transport. Source-level investigation must separate those infrastructure causes from the conversion operation itself.

## Important Variations and Special Cases

- The same 13 formats appear in `snorm_clamp` and `snorm_clamp_linear`: three packed formats, BGR/BGRA 8-bit formats, and R-based one- through four-component 8-bit or 16-bit formats.
- `snorm_clamp` uses exact shader equality on one converted texel. `snorm_clamp_linear` uses a full image comparison with permitted precision and then an exact inclusive range condition. These checks answer different questions.
- The linear render dimensions progress from 140 by 140 to 308 by 308 because the 7 by 7 source texture is multiplied by 20, then by successively larger even multipliers.
- The source registers unsuffixed and `_compute` linear leaves. It constructs both leaves with the same shared `Params` object, then changes `useCompute` to `true` before constructing the suffixed leaf. Because each test case retains that shared object, current source makes both registered leaves select the compute backend when instances are later created. The names therefore do not currently prove distinct graphics and compute execution. This is a source-level finding; the documentation must describe the actual aliasing rather than claim two distinct paths.
- The texture dispatcher registers the entire `conversion` family inside `#ifndef CTS_USES_VULKANSC`. No conversion leaf is reachable in Vulkan SC, even though only the two Amber population functions contain additional local guards.
- C++ linear cases require `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` for optimal tiling. Amber cases pass exact image-create requirements to the common Amber support check.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Texture dispatcher | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L67) | Registers `conversion` under `texture` only outside Vulkan SC. |
| Test family registration | [`populateTextureConversionTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L424-L440) | Establishes the three primary behavior values. |
| Unsigned-float registration | [`populateUfloatNegativeValuesTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L291-L322) | Defines the image requirement and Amber recipe. |
| Unsigned-float recipe | [`b10g11r11-ufloat-pack32.amber`](../../../data/vulkan/amber/texture/conversion/ufloat_negative_values/b10g11r11-ufloat-pack32.amber) | Contains the writer, verifier, resources, dispatches, and final expectation. |
| Direct SNORM registration | [`populateSnormClampTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L324-L380) | Defines all 13 formats and their image requirements. |
| Representative direct SNORM recipe | [`r8-snorm.amber`](../../../data/vulkan/amber/texture/conversion/snorm_clamp/r8-snorm.amber) | Shows exact `-1.0` checking and green framebuffer validation. |
| Linear texture construction | [`SnormLinearClampInstance` constructor](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L91-L129) | Builds the endpoint-focused 7x7 source pattern and matching host/device textures. |
| Linear execution | [`SnormLinearClampInstance::iterate`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L217-L252) | Configures linear repeat sampling, renders, and generates the software reference. |
| Linear validation | [`SnormLinearClampInstance::verifyPixels`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L145-L215) | Performs the lookup-difference and explicit range checks. |
| Linear case matrix | [`populateSnormLinearClampTests`](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L382-L422) | Defines formats, sizes, registered suffixes, and the shared-parameter behavior. |
| Shared shader generator | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L760) | Emits fragment and compute sampling programs for `PROGRAM_2D_FLOAT`. |
| Amber execution | [`AmberTestInstance::iterate`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Compiles supplied programs into execution data and converts Amber success into CTS status. |
| Mustpass inventory | [`vk-default/texture.txt`](../../../mustpass/main/vk-default/texture.txt#L1813-L1852) | Confirms 40 registered conversion leaves in the default Vulkan list. |
| SNORM specification | [Fixed-point conversion](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L1682-L1717) | Defines direct SNORM conversion and post-processing range clamping. |
| Format interpretation | [Numeric formats](../../../../vulkan-docs/src/chapters/formats.adoc#L1620-L1644) | Defines SNORM and UFLOAT component interpretation. |

## Questions / Risk Points for User Audit

- Does the three-family behavior axis make the distinct storage-conversion, direct-sampling, and filtered-sampling failures easy to separate?
- Is the distinction between device-side exact checks and host-side tolerance plus range checks clear?
- The shared `Params` mutation means the unsuffixed and `_compute` linear leaves currently select the same compute backend. This changes how those names should be interpreted and should be reviewed by the source maintainer.
- The C++ source calls the pattern a linear-clamp corner case, but it initializes components at or above the ordinary negative endpoint rather than writing the extra most-negative two's-complement encoding used by the Amber cases. The final page should describe the observed endpoint-focused pattern and avoid claiming that it contains the most-negative encoding.

No remaining documentation ambiguity prevents the final rewrite. The page can state current source behavior and keep both source-level findings explicit.

## Conversion Notes for Final Wiki Rewrite

- Keep UFLOAT unsigned range and the SNORM post-filter clamp as the two short Background Knowledge bullets.
- Use the Amber unsigned-float verifier as one representative shader walkthrough because it shows conversion and validation in one shader.
- Use one `snorm_clamp_linear` compute leaf as a second walkthrough because the generated renderer program and host validation differ from Amber's self-checking model.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Carry the three test families into `## Behavior Parameters` as the primary behavioral axis.
- State that the current unsuffixed and `_compute` leaves share `useCompute = true`; do not present the pair as verified graphics-versus-compute coverage.
- Keep source navigation in the final appendix and preserve the two source-level risk points in the relevant behavior, pruning, and failure sections.
