# Understanding Brief: `texture.compressed` and `texture.compressed_3D`

## One-Sentence Test Purpose

These tests check whether sampled images return the correct texels after the implementation decodes ETC2/EAC, ASTC, and BC compressed blocks in 2D and 3D images, including regular and sparse image backing.

## Background Knowledge

### Block-compressed image formats

A block-compressed format stores one fixed-size encoded block for a rectangular or three-dimensional group of texels. Sampling still addresses logical texels. The implementation must identify the block, decode the requested texel according to the format, apply the format's numeric interpretation, and then apply sampler behavior.

Why it matters here:
- The host uploads encoded blocks, not an ordinary uncompressed image.
- The host also decodes the same bytes with the CTS software decoder, which supplies the expected texel values.
- Different families cover normalized, signed-normalized, sRGB, and floating-point results, so one tolerance cannot serve every format.

### Regular and sparse image backing

A regular image has one ordinary memory binding. A sparse image can bind regions of the image to separate allocations through sparse binding. The logical sampled image and compressed bytes are the same in these cases; only the Vulkan memory association and upload path differ.

Why it matters here:
- A sparse failure can identify a compressed-image sparse binding, residency, upload, or synchronization problem even when the corresponding regular case passes.
- Sparse cases are omitted from Vulkan SC, where sparse resources are unavailable.

### Nearest sampling and coordinate tolerance

Nearest filtering selects a texel from the sample coordinate instead of blending neighboring texels. Rasterization and coordinate calculation can place an implementation's coordinate close to an integer texel boundary. The validator therefore searches a small coordinate neighborhood in the software reference, but every accepted candidate must still satisfy the format-specific color threshold.

Why it matters here:
- The neighborhood is an allowance for coordinate uncertainty, not an allowance to decode an unrelated compressed block.
- A full-image pass requires an accepted candidate for every rendered pixel and, for 3D cases, every tested slice.

## One Concrete Example

Consider `dEQP-VK.texture.compressed.astc_4x4_unorm_block_2d_npot`. The host creates a 51 by 65 ASTC 4x4 UNORM image. It uses seed 123 to generate valid ASTC blocks, stores the encoded bytes for upload, and decodes those bytes with the CTS ASTC software decoder into an uncompressed reference texture.

The graphics path draws a full-screen quad. Its generated fragment shader is equivalent to:

```glsl
// Simplified reconstruction of the generated fragment lookup.
vec2 texCoord = v_texCoord;
vec4 sampled = texture(u_sampler, texCoord);
dEQP_FragColor = sampled * u_colorScale + u_colorBias;
```

The sampler uses nearest magnification and nearest mip-level selection. This non-mipmapped case samples level 0. The host independently samples the software-decoded texture over the same coordinate range and checks every output pixel against nearby reference texels with the non-BC color threshold.

## End-to-End Test Flow

```text
[host] choose the test family, compressed format, extent, mip option, backing mode, and registered graphics or compute-marked variant
[host] generate deterministic compressed blocks, or ASTC void-extent blocks for the dedicated 2D cases
[host] decode the same blocks with the CTS software decoder and retain the uncompressed levels as the reference texture
[host] create an optimal-tiled sampled image and bind regular memory, or create a sparse image and bind its sparse regions
[host] upload the encoded blocks and create the image view, sampler, descriptors, output target, and generated programs
[host] submit a full-image lookup; a 3D case repeats it for three selected depth slices
[device] sample the compressed image, decode the addressed block, apply format conversion and sampler behavior, and write RGBA output
[host] build the software-sampled reference image and compare every result pixel with its permitted reference neighborhood
[host] pass only if every tested pixel in every tested slice has a threshold-compliant match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `TextureTestCase::initPrograms` calls `initializePrograms` for `PROGRAM_2D_FLOAT` or `PROGRAM_3D_FLOAT`.
- The shared generator emits a pass-through vertex shader, a fragment shader using `texture(...)`, and a compute shader using reconstructed coordinates and `textureGrad(...)`.
- The test matrix registers graphics leaves and compute-marked leaves for all base 2D and 3D formats. Current source sets `useCompute` on the marked parameters but does not pass it into either compressed test instance's `TextureRenderer`; this is an unresolved source-level discrepancy discussed below.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Compressed sampled image | yes | yes | read | no | Contains the exact ETC2/EAC, ASTC, or BC blocks whose device decoding is under test. |
| Regular or sparse image memory | yes | yes | image backing | no | Selects the ordinary binding path or sparse binding and residency path without changing logical texels. |
| Image view and sampler | yes | yes | read through descriptor | no | Expose the compressed image and define nearest filtering, mip selection, wrapping, and LOD clamps. |
| Uniform lookup parameters | yes | yes | read | no | Supply result scale and bias used to make signed or otherwise non-UNORM results observable in the RGBA output. |
| Quad geometry or compute geometry buffer | yes | yes | read | no | Supplies positions and texture coordinates for the full-image lookup. |
| Color attachment or compute output image | yes | yes | written | copied/read by renderer | Contains the implementation's sampled values. |
| Encoded host levels | yes | uploaded | read as image data | retained by host | The same bytes feed device sampling and software decompression. |
| Software-decoded texture and reference surface | yes | no | no | yes | Provide the independent expected texels and per-pixel neighborhood candidates. |
| Error mask | yes | no | no | yes | Marks accepted pixels green and rejected pixels red in failure logs. |

## What Is Checked

- The 2D family renders one full texture face. The 3D family performs three XY-plane lookups at Z coordinates computed from evenly spaced base-depth indices; those coordinates use the selected mip depth as the normalization denominator.
- `sampleTexture` builds the expected image from the software-decoded texture and the same sampler parameters.
- For each output pixel, `validateTexture` converts the pixel center to reference-texel coordinates and searches the integer coordinates covered by a `0.01` texel-coordinate tolerance.
- A candidate matches only when all RGBA component differences stay within the selected threshold:

| Format class | RGBA threshold |
|--------------|----------------|
| BC6H UFLOAT/SFLOAT and BC7 UNORM/SRGB | `(1, 1, 1, 1)` |
| Other BC in 2D | `(8, 8, 8, 8)` |
| Other BC sRGB in 3D | `(9, 9, 9, 9)` |
| Other BC in 3D | `(8, 8, 8, 8)` |
| ETC2, EAC, and ASTC | `R8G8B8A8_UNORM color threshold + (2, 2, 2, 2)` |

- The case fails on the first 3D slice containing a rejected pixel, or when any 2D output pixel lacks an accepted reference candidate.
- Failure logs contain the rendered image, an error mask, maximum observed difference, thresholds, and normalization information for values that do not fit directly in UNORM log images.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family below the `texture` test category
>
> **Candidate values:** `compressed`, `compressed_3D`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compressed` | Incorrect 2D compressed-block decoding or format conversion, wrong sampled-image upload or mip selection, ASTC void-extent handling, or a regular/sparse backing-path error. |
| `compressed_3D` | Incorrect decoding or addressing of compressed 3D image data, wrong depth-slice or mip handling, ASTC 3D format support, or a regular/sparse 3D backing-path error. |

## Important Variations and Special Cases

- The common list has 54 formats: 6 ETC2, 4 EAC, 28 ASTC 2D formats, and 16 BC formats. Both test families use this list.
- Non-Vulkan-SC builds add 30 native ASTC 3D formats: 10 block dimensions times UNORM, sRGB, and SFLOAT.
- `pot` uses 128 by 64, with depth 8 for 3D. `npot` and `npot_mip1` use 51 by 65, with depth 17 for 3D. Common-format `npot_mip1` cases force exact sampling of mip level 1. Native ASTC 3D leaves retain `mipmaps == false` despite the same size name.
- ASTC 2D formats add dedicated `voidextent` cases. They replace random valid blocks with generated ASTC void-extent LDR block data.
- Sparse cases use sparse binding and residency flags and a sparse upload path. The helper skips a case when the format and image type have no sparse image properties.
- Core ASTC LDR, ETC2/EAC, and BC support is checked explicitly by the 3D instance. Native ASTC 3D adds `VK_EXT_texture_compression_astc_3d` and `textureCompressionASTC_3D`. The 2D instance relies on image-format support checks in the shared image binding path.
- Base-format matrices register graphics and compute-marked leaves. Native ASTC 3D registers graphics-only leaves. Source inspection shows that the compressed instances construct `TextureRenderer` without forwarding `testParameters.useCompute`, so the compute-marked leaves currently select the default graphics backend despite generating compute shader programs. This is a source defect or intentional exception that requires owner confirmation; the documentation must not claim those leaves execute compute sampling in the current source.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Compressed format and size tables | [Format, size, and backing tables](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L58-L133) | Defines the common 54 formats, 30 ASTC 3D formats, three sizes, and regular/sparse modes. |
| 2D execution | [`Compressed2DTestInstance`](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L156-L429) | Creates and samples the 2D compressed texture and selects its threshold. |
| Shared neighborhood validation | [`validateTexture`](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L248-L349) | Builds the software reference, searches coordinate candidates, and sets pass/fail. |
| 3D execution and support | [`Compressed3DTestInstance`](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L431-L600) | Checks compressed-format features and samples three depth slices. |
| Case generation | [2D population](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L604-L656), [3D population](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L658-L719) | Defines exact names and graphics, compute-marked, sparse, void-extent, and ASTC 3D variations. |
| Deterministic block generation and host decode | [`populateCompressedLevels`](../../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L982-L1031), [void-extent generation](../../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L1033-L1052) | Produces encoded input and the software-decoded reference from identical bytes. |
| Regular and sparse image setup | [`TextureBinding::updateTextureData`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L808-L920) | Creates the sampled image, queries capabilities, and selects regular or sparse upload. |
| Shared shader generator | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L760) | Emits the graphics and compute sampling programs for `PROGRAM_2D_FLOAT` and `PROGRAM_3D_FLOAT`. |
| Dispatcher registration | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Registers both test families under `texture`. |
| Mustpass inventory | [`texture.txt`](../../../mustpass/main/vk-default/texture.txt#L1) | Contains the executable paths for both generated families. |
| Compressed format definitions | [Vulkan formats chapter](../../../../vulkan-docs/src/chapters/formats.adoc#L497-L683) | Defines the block-compressed texel encodings covered by the common matrix. |
| Compressed-format features | [ETC2/EAC and ASTC LDR](../../../../vulkan-docs/src/chapters/features.adoc#L372-L438), [BC](../../../../vulkan-docs/src/chapters/features.adoc#L440-L468), [ASTC 3D](../../../../vulkan-docs/src/chapters/features.adoc#L4026-L4079) | Defines the feature promises checked by the cases. |
| Sparse resource model | [Sparse Resources](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L4-L25) | Defines non-contiguous binding and the Vulkan SC exclusion. |

## Questions / Risk Points for User Audit

- Is the direct test-family axis, `compressed` versus `compressed_3D`, the most useful top-level failure split for this combined implementation page?
- Is the coordinate-neighborhood explanation clear that tolerance applies to sample location while color remains format-bounded?
- Is the distinction between encoded upload data and the host's software-decoded reference explicit enough?
- Source-level risk: both compressed constructors omit `testParameters.useCompute` when constructing `TextureRenderer`. The registered compute-marked leaves therefore appear to execute the graphics backend. Source-owner confirmation is needed to determine whether the constructors should forward the flag or the compute-marked registrations should be removed.
- Source-level risk: `smpDiff` in `validateTexture` is initialized once to zero and updated with component-wise minimum, so logged `maxDiff` remains zero. This affects diagnostics, not the match decision or pass condition.

## Conversion Notes for Final Wiki Rewrite

- Distill block compression, sparse backing, and neighborhood validation into short prerequisite bullets.
- Use `dEQP-VK.texture.compressed.astc_4x4_unorm_block_2d_npot` for one representative shader walkthrough.
- Explain 3D sampling, void-extent blocks, sparse backing, native ASTC 3D, and the compute-marked discrepancy in the variation and runtime sections rather than adding more walkthroughs.
- Carry the direct-family behavior axis into `## Behavior Parameters`.
- Copy the Failure Cause Mapping table unchanged.
- Keep the resource model as compact runtime bullets and move source navigation to the final appendix.
