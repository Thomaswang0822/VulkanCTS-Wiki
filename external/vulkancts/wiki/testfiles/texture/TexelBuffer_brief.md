# Understanding Brief: `texture.texel_buffer`

## One-Sentence Test Purpose

This test checks whether uniform texel-buffer reads apply the format's sRGB, packed-component, integer, floating-point, and SNORM interpretation and return the expected shader values.

## Background Knowledge

### Uniform texel buffers

A uniform texel buffer exposes a tightly packed one-dimensional array through a formatted buffer view. A GLSL `samplerBuffer`, `isamplerBuffer`, or `usamplerBuffer` performs integer-indexed `texelFetch` reads; the view format determines how stored bits become floating-point, signed-integer, or unsigned-integer components.

Why it matters here:
- The scripts supply raw bytes or 32-bit words, then rely on the Vulkan buffer-view format to decode each texel.
- The shader does no address filtering or LOD selection, so a wrong value points to formatted buffer access, conversion, or the surrounding resource path.

### Format conversion

sRGB formats store nonlinear RGB values and return linearized RGB values when sampled. SNORM formats map signed fixed-point integers to `[-1,1]`, including clamping the extra most-negative two's-complement encoding to `-1.0`. Packed formats assign several components to bit fields in one word and then interpret those fields as integer, normalized, or unsigned floating-point values.

Why it matters here:
- The sRGB scripts compare texel-buffer reads with sampled-image reads of identical formatted data.
- The packed scripts choose words whose decoded components form easy-to-recognize colors.
- The SNORM scripts remap fetched values from `[-1,1]` into `[0,1]` before writing an UNORM framebuffer.

## One Concrete Example

Consider `dEQP-VK.texture.texel_buffer.uniform.srgb.r8_srgb`. The script initializes an 8 by 8 `R8_SRGB` image and a uniform texel buffer with identical bytes. Each fragment samples the image at its interpolated coordinate and fetches the corresponding linear buffer element:

```glsl
// Simplified from r8_srgb.amber.
vec4 referenceValue = texture(referenceSampler, texCoordsIn);
vec4 bufferValue = texelFetch(
    bufferSampler,
    int((gl_FragCoord.y - 0.5) * 8 + (gl_FragCoord.x - 0.5)));
colorOut = (bufferValue.r == referenceValue.r)
         ? vec4(0.0, 1.0, 0.0, 1.0)
         : vec4(1.0, 0.0, 0.0, 1.0);
```

Amber requires all 64 result pixels to be opaque green. The comparison checks whether the texel-buffer path applies the same `R8_SRGB` nonlinear-to-linear conversion as the sampled-image path.

## End-to-End Test Flow

```text
[host] register one of 23 Amber recipes and check its format requirements
[host] parse the recipe, compile its fixed vertex and fragment shaders, and create the declared resources
[host] initialize the formatted texel buffer; sRGB cases also initialize a same-format 8x8 sampled image with identical data
[host] bind the buffer as a uniform texel buffer and configure the graphics pipeline
[device] draw a rectangle or two triangles and fetch formatted buffer elements with texelFetch
[device] compare sRGB paths in the shader, or write decoded packed/SNORM values to the UNORM framebuffer
[host/Amber] evaluate the recipe's EXPECT commands
[host] return pass only when every declared expectation succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Six sRGB recipes carry a pass-through vertex shader and a fragment shader that compares a sampled image with a uniform texel buffer.
- Seven packed-format recipes carry Amber's `PASSTHROUGH` vertex shader and a fragment shader that cycles through four packed words.
- Ten SNORM recipes use the same fixed vertex shader and a fragment shader that cycles through 39 8-bit texels or 35 16-bit texels, remapping the fetched result for UNORM output.
- The C++ registration layer selects the recipe filename and adds support requirements; it does not calculate expected values.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Formatted texel buffer and buffer view | yes | uniform texel-buffer descriptor | read | no | Holds the raw bytes or words whose formatted interpretation is under test. |
| Same-format 8 by 8 image, sRGB cases only | yes | combined image sampler | read | no | Supplies the sampled-image reference for exact shader-side comparison. |
| Sampler, sRGB cases only | yes | combined with the reference image | controls image read | no | Selects one source image texel for each fragment. |
| Vertex positions and coordinates, sRGB cases only | yes | vertex inputs | read | no | Map the 8 by 8 draw to the 64 reference texels. |
| `B8G8R8A8_UNORM` framebuffer | yes | color attachment | written | checked by Amber | Stores green/red equality signals or decoded packed/SNORM values. |

## What Is Checked

| Behavioral family | Device-side operation | Amber pass condition |
|-------------------|-----------------------|----------------------|
| `srgb` | Compare each formatted buffer read with the same texel read from a same-format image. | Every pixel of the 8 by 8 framebuffer equals opaque green exactly. |
| `packed` | Fetch four selected packed words through the matching floating-point, signed-integer, or unsigned-integer buffer sampler. | Eight one-pixel-wide, 100-pixel-high columns match the exact expected RGBA colors, covering the four-word sequence twice. |
| `snorm` | Convert 8-bit or 16-bit SNORM components, remap `(value + 1) / 2`, and preserve only channels present in the format. | Each of 39 8-bit or 35 16-bit expected columns matches for all 128 rows with byte tolerance 1. |

## Behavior Parameter Identification

> **Behavior parameter:** behavioral family within `texture.texel_buffer.uniform`
>
> **Candidate values:** `srgb`, `packed`, `snorm`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `srgb` | Uniform texel-buffer sRGB conversion differs from sampled-image conversion, or the image/buffer resources, indexing, or descriptor path supplies different data. |
| `packed` | Packed bit fields, component order, numeric interpretation, sampler type, or formatted buffer fetch produces the wrong output components. |
| `snorm` | Signed fixed-point decoding, the most-negative-value clamp, component order, or formatted buffer fetch returns values outside the expected SNORM conversion tolerance. |

A broad failure across all three families can also come from buffer-view creation, uniform texel-buffer descriptors, shader compilation, draw execution, synchronization, framebuffer output, or Amber result comparison.

## Important Variations and Special Cases

- The default Vulkan mustpass list contains 23 leaves: six `srgb`, seven `packed`, and ten `snorm` cases.
- sRGB registrations require both an 8 by 8 sampled image of the selected format and `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` in `bufferFeatures`.
- The registration code adds explicit uniform-texel-buffer requirements for non-mandatory SNORM formats. It treats `R8_SNORM` and `R8G8_SNORM` as mandatory and does not add a buffer requirement for them.
- `packed` and `snorm` have local Vulkan SC guards, and the texture dispatcher also omits the entire `texel_buffer` test family in Vulkan SC. This page describes the Vulkan path only.
- Source-level risk: the `b8g8r8a8-snorm` registration associates its support requirement with `VK_FORMAT_B8G8R8A8_SINT`, while the recipe declares `B8G8R8A8_SNORM`. The recipe still tests SNORM access, but the pre-execution buffer-feature check queries the wrong format.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Texture dispatcher | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Registers `texel_buffer` below `texture` for Vulkan, not Vulkan SC. |
| Family and case registration | [`createUniformTexelBufferTests`](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L38-L163) | Defines all 23 leaves, recipe paths, and support requirements. |
| Family factory | [`createTextureTexelBufferTests`](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L167-L174) | Creates `texture.texel_buffer` and attaches `uniform`. |
| Representative sRGB recipe | [`r8_srgb.amber`](../../../data/vulkan/amber/texture/texel_buffer/uniform/srgb/r8_srgb.amber) | Shows identical image/buffer data, exact shader comparison, and green framebuffer expectation. |
| Representative packed recipe | [`a2b10g10r10-uint-pack32.amber`](../../../data/vulkan/amber/texture/texel_buffer/uniform/packed/a2b10g10r10-uint-pack32.amber) | Shows packed input words, integer texel fetch, and exact color columns. |
| Representative SNORM recipe | [`r8-snorm.amber`](../../../data/vulkan/amber/texture/texel_buffer/uniform/snorm/r8-snorm.amber) | Shows endpoint data, SNORM remapping, and tolerance-1 expectations. |
| Amber support and execution | [`AmberTestCase::checkSupport`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286), [`AmberTestInstance::iterate`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Checks image/buffer format support, executes the Vulkan recipe, and maps Amber success to CTS status. |
| Mustpass inventory | [`vk-default/texture.txt`](../../../mustpass/main/vk-default/texture.txt#L27278-L27300) | Lists the exact 23 default Vulkan test paths. |
| Uniform texel-buffer semantics | [Uniform texel buffer descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L319-L333) | Defines the formatted one-dimensional array and required format feature. |
| Format conversion | [Normalized fixed-point conversion](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L1682-L1717), [sRGB image conversion](../../../../vulkan-docs/src/chapters/images.adoc#L129-L132) | Defines SNORM endpoint conversion and sRGB nonlinear-to-linear conversion. |

## Questions / Risk Points for User Audit

- Does `srgb`, `packed`, and `snorm` provide the most useful failure split even though these names occur below the direct `uniform` child?
- Is the distinction between device-side shader comparison in `srgb` and host-side Amber framebuffer comparison in the other families clear?
- Source owner review is needed for the `b8g8r8a8-snorm` registration's `VK_FORMAT_B8G8R8A8_SINT` support requirement.

## Conversion Notes for Final Wiki Rewrite

- Keep the registration tree at `texture.texel_buffer` with direct child `uniform`; describe `srgb`, `packed`, and `snorm` in prose rather than nesting them in the tree.
- Carry the three behavioral families into `## Behavior Parameters` and copy the Failure Cause Mapping table unchanged.
- Use `dEQP-VK.texture.texel_buffer.uniform.srgb.r8_srgb` for the representative shader walkthrough because it exposes the tested equality between image and buffer format conversion.
- Keep packed and SNORM mechanics in the variation, runtime, and failure sections rather than adding walkthroughs.
- Preserve the mismatched `B8G8R8A8_SINT` support requirement as an unresolved source-level risk.
