# Understanding Brief: `texture.filtering`

## One-Sentence Test Purpose

This test checks whether Vulkan samplers apply dimensional addressing, coordinate interpretation, texel filtering, mip-level selection, and cube-edge rules consistently in graphics and compute paths.

## Background Knowledge

### Filtering and implicit level of detail

A sampled image lookup first identifies an image level and then filters texels from that level. The sampler's `magFilter` controls magnification. Its `minFilter` controls filtering within a minified level, while `mipmapMode` controls selection or blending between neighboring levels. Implicit level of detail comes from coordinate derivatives, so changing the coordinate span over the same output area can move a lookup between magnification and minification and across mip levels. The Vulkan rules are defined in the [sampler chapter](../../../../vulkan-docs/src/chapters/samplers.adoc#L76-L95) and the [LOD and image-level selection sections](../../../../vulkan-docs/src/chapters/textures.adoc#L1525-L1531).

Why it matters here:

- Each test case renders four coordinate spans over gradient and grid textures. The spans create both positive and negative LOD regions.
- The compute path supplies `textureGrad` derivatives reconstructed from neighboring output coordinates. The graphics path uses the fragment shader's implicit derivatives.
- Verification admits the precision ranges allowed for coordinate, derivative, LOD, and filtered-color calculations instead of requiring one exact floating-point image.

### Coordinate domains and image dimensionality

Normalized coordinates use a zero-to-one domain before conversion to texel coordinates. Unnormalized coordinates use image-space values and carry sampler restrictions, including one mip level, equal minification and magnification filters, and clamp address modes. Array layer coordinates remain unnormalized even when the other coordinates are normalized. Cube coordinates are direction vectors that select and transform to a face, with separate edge behavior for seamless and non-seamless sampling.

Why it matters here:

- `unnormal` is not a smaller copy of `2d`. It changes the coordinate domain and removes mipmap behavior.
- `2d_array` varies the layer coordinate across the quad, but filtering does not blend adjacent array layers.
- `cube` checks face selection, edge crossings, and the `seamless` versus `non_seamless` sampler state.

## One Concrete Example

Consider `dEQP-VK.texture.filtering.2d.formats.r8g8b8a8_unorm.linear_mipmap_linear_compute`. The host creates two `64x64` `VK_FORMAT_R8G8B8A8_UNORM` textures with complete mip chains. One texture contains component gradients. The other contains a grid whose colors change by mip level. For each of four coordinate spans, the compute shader reconstructs the quad's perspective-correct texture coordinate, estimates neighboring coordinates in X and Y, and calls:

```glsl
// Conceptual extract reconstructed from initializePrograms().
vec2 texCoord  = interpolate(vec2(coord), size);
vec2 texCoordX = interpolate(vec2(coord) + vec2(1.0, 0.0), size);
vec2 texCoordY = interpolate(vec2(coord) + vec2(0.0, 1.0), size);
vec2 dPdx = texCoordX - texCoord;
vec2 dPdy = texCoordY - texCoord;
vec4 result = textureGrad(u_sampler, texCoord, dPdx, dPdy)
            * u_colorScale + u_colorBias;
imageStore(u_outputImage, coord + pc.u_offset, result);
```

`linear_mipmap_linear` requests linear filtering within each selected mip level and linear interpolation between two neighboring levels. The grid texture makes an incorrect level or blend visible, while the gradient texture makes coordinate and within-level interpolation errors visible. The paired graphics leaf runs the same sampler case with an implicit-LOD fragment lookup.

## End-to-End Test Flow

```text
[host] select one registered family, matrix branch, format, size, filter state, address state, and graphics or compute suffix
[host] reject combinations unsupported by the verifier or required Vulkan features
[host] generate the dimensional GLSL programs selected by the format's sampler type
[host] create two images with mip chains, then fill a gradient pattern and a level-distinguishing grid pattern
[host] upload the images, create image views and samplers, and prepare four coordinate cases
[host] submit a quad draw or a compute dispatch for the current coordinate case
[device] sample the image with implicit derivatives or explicit gradients and write an RGBA8 result image
[host] read the result and run the dimensional texture verifier with high-precision bounds
[host] retry only the verifier with lower LOD and lookup precision if the high-precision check fails
[host] fail if the low-precision check fails, otherwise advance until all four coordinate cases and cube faces pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`TextureTestCase::initPrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.hpp#L556-L580) calls [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L212). The generator specializes a GLSL 4.50 vertex shader, fragment shader, and compute shader for the selected dimensional program. It changes the coordinate vector width, sampler type, lookup expression, output image declaration, and derivative arguments. Floating-point filtering cases use `sampler2D`, `samplerCube`, `sampler2DArray`, or `sampler3D`. Stencil-aspect cases use the corresponding unsigned sampler.

The graphics path passes texture coordinates through the vertex shader and performs `texture(...)` in the fragment shader. The compute path reads quad positions and coordinates from a storage buffer, reproduces perspective interpolation, calculates adjacent-coordinate gradients, calls `textureGrad(...)`, and writes a storage image. No explicit `ShaderBuildOptions` are supplied, so the source collection baseline target is SPIR-V 1.0.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Gradient sampled image | yes | yes | read | no | Exposes coordinate and within-level interpolation errors. |
| Grid sampled image | yes | yes | read | no | Uses level-dependent colors to expose mip selection and mip-level blending errors. |
| Sampler | yes | yes | read as sampling state | no | Carries minification, magnification, mipmap, address, coordinate-normalization, and cube-seam state. |
| Uniform block | yes | yes | read | no | Supplies color scale and bias, view size, and shared generator fields. |
| Quad geometry buffer | yes for compute leaves | yes | read | no | Lets the compute shader reproduce the graphics quad's coordinate interpolation. |
| Output color or storage image | yes | yes | written | yes | Holds the sampled RGBA8 image that the host verifier checks. |
| CPU texture levels and reference views | yes | no | no | yes, host-only | Supply exact pattern data to the software verifier. They are not GPU resources. |

The filtering implementation passes the default regular image backing mode to `TextureRenderer`. It does not register sparse variants. Other texture source files use sparse image backing, but this page's source does not.

## What Is Checked

- Every registered test case runs four coordinate spans. Cube cases render all six faces for every span.
- `verifyTextureResult` compares each output pixel against values permitted by the software texture model, sampler state, image contents, coordinate interpolation, and LOD precision.
- The first check uses stronger bounds. For 2D, 2D array, and 3D it uses 18 derivative bits, 6 LOD bits, 20 coordinate bits, and 7 U/V/W lookup bits where applicable. Cube uses 10 derivative bits, 5 LOD bits, 10 coordinate bits, and 6 U/V lookup bits.
- If that check fails, the test retries with 4 LOD bits and 4 lookup bits. Passing this fallback still passes the case because both tiers represent accepted implementation precision.
- A case fails only when the lower-precision verification also rejects a result. The message is `Image verification failed`.
- In Vulkan SC builds, image verification executes only in subprocess mode.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family under `texture.filtering`
>
> **Candidate values:** `2d`, `unnormal`, `cube`, `2d_array`, `3d`

These values change coordinate interpretation, image-view dimensionality, sampler rules, generated shader types, reference-view types, and dimensional verification behavior. Matrix branches such as `formats`, `sizes`, and `combinations` vary coverage inside a family. The `_compute` suffix changes the execution route while preserving the intended sampled-image result.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect 2D coordinate addressing, minification or magnification filtering, mip-level selection or blending, format conversion, stencil sampling, or graphics/compute gradient handling. |
| `unnormal` | Incorrect unnormalized coordinate interpretation, clamp-to-edge or clamp-to-border behavior, single-level filtering, or unnormalized shader lookup handling. |
| `cube` | Incorrect direction-to-face mapping, transformed derivatives, face-edge handling, seamless or non-seamless behavior, or cube sampler filtering. |
| `2d_array` | Incorrect 2D filtering or LOD computation, incorrect unnormalized array-layer selection, or dimensional shader/reference handling. |
| `3d` | Incorrect three-coordinate addressing, R-axis wrapping, trilinear within-level filtering, mip-level selection, or dimensional gradient handling. |

Graphics-only or `_compute`-only failures narrow the likely cause to that pipeline's coordinate interpolation, derivative construction, descriptor layout, shader compilation, output write, or readback route. Failures shared by both routes point more directly to sampler and image behavior or shared setup and verification inputs.

## Important Variations and Special Cases

- `2d` adds cubic minification and magnification values. Cubic cases require `VK_EXT_filter_cubic`, per-view `filterCubic`, and `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_CUBIC_BIT_EXT`.
- `unnormal` has only `formats` and `sizes`. It uses no mip chain, keeps minification and magnification equal, and selects only `clamp_to_edge` or `clamp_to_border` as required by unnormalized sampler rules.
- `cube` adds `seamless` and `non_seamless` leaves throughout its matrix. `no_edges_visible` confines coordinates to a face interior and uses only nearest or linear filtering.
- `2d_array` varies the layer coordinate, including out-of-range values that clamp to available layers and a near-1.5 tie case.
- `3d` adds an independently varied R address mode.
- Every ordinary leaf has a `_compute` partner. A compute leaf requires a usable compute queue route.
- Integer channel formats with linear or cubic filters are not registered because `verifyTextureResult` cannot verify those combinations. This is design-based pruning, not a device capability skip.
- `mirror_clamp_to_edge`, cubic filtering, non-seamless cube maps, and `R10X6G10X6B10X6A10X6_UNORM_4PACK16` have extension or format-feature support checks.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category dispatcher | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Attaches `filtering` directly below `texture`. |
| Registered matrix | [`populateTextureFilteringTests`](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1207-L2076) | Defines the five direct families, all matrix values, graphics/compute pairs, and design pruning. |
| 2D runtime and verifier | [`Texture2DFilteringTestInstance`](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L242-L437) | Builds the patterns and coordinate cases, renders, and applies the two-tier verifier. |
| Cube runtime and verifier | [`TextureCubeFilteringTestInstance`](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L478-L709) | Adds face traversal, seamless state, cube coordinates, and cube-specific precision. |
| 2D array runtime and verifier | [`Texture2DArrayFilteringTestInstance`](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L754-L962) | Varies layers and validates a `Texture2DArrayView`. |
| 3D runtime and verifier | [`Texture3DFilteringTestInstance`](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1005-L1190) | Adds depth gradients, R wrapping, and `Texture3DView` verification. |
| Shader generator | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L759) | Generates dimensional graphics and compute GLSL, including `texture`, `textureLod`, and `textureGrad` paths. |
| Sampler conversion | [`createSampler`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L1351-L1391) | Maps CTS wrap and filter enums to the software-reference sampler. |
| Verification API | [`tcuTexVerifierUtil.hpp`](../../../../../framework/common/tcuTexVerifierUtil.hpp) | Declares the precision-aware image verification used by every family. |
| Mustpass examples | [`texture.txt`](../../../mustpass/main/vk-default/texture.txt#L3811-L3812) | Confirms the representative graphics and compute leaves. |
| Sampler semantics | [`samplers.adoc`](../../../../vulkan-docs/src/chapters/samplers.adoc#L76-L171) | Defines filter, mipmap, address, and unnormalized sampler state. |
| Image sampling semantics | [`textures.adoc`](../../../../vulkan-docs/src/chapters/textures.adoc#L1315-L1353) | Defines derivative inputs to LOD selection and sampled-image operations. |

## Questions / Risk Points for User Audit

- Is treating the five direct test families as the behavior parameter more useful than treating graphics versus compute as the primary axis?
- Does the compute example explain why `textureGrad` is comparable to the fragment path without implying bit-identical derivatives?
- Is the distinction between accepted high-precision and low-precision verifier bounds clear?
- The rewrite outline mentions sparse variants, but the current implementation always uses regular backing and registers no sparse leaves. Should the outline be corrected during category cleanup?
- Are the cube-edge and array-layer explanations detailed enough without reproducing the Vulkan equations?

## Conversion Notes for Final Wiki Rewrite

- Keep filtering, implicit LOD, unnormalized-coordinate restrictions, array-layer selection, and cube face behavior as compact prerequisites.
- Use the compute `2d.formats.r8g8b8a8_unorm.linear_mipmap_linear_compute` leaf for the representative shader walkthrough because it exposes coordinate interpolation and explicit gradient construction. Explain the shorter fragment path in the variation summary.
- Carry the direct-family behavior parameter and the Failure Cause Mapping table into the page unchanged.
- Preserve the two-tier verification rules and the explicit statement that this source registers no sparse variants.
- Move detailed source navigation to the final appendix.
