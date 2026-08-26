# Understanding Brief: `texture.shadow`

## One-Sentence Test Purpose

This test checks whether Vulkan depth-comparison sampling returns an allowed filtered comparison value across image view types, compare operations, formats, mip filters, sparse backing, and cube edge modes.

## Background Knowledge

### Depth-comparison sampling

A comparison sampler does not return the stored depth directly. A Dref sampling instruction supplies a reference value, and the sampler applies its `VkCompareOp` to that reference and each selected texel depth. A successful comparison contributes `1.0`; a failed comparison contributes `0.0`. The Vulkan specification defines the reference as the first compare operand and the texel depth as the second.

Why it matters here:

- Reversing the operands changes asymmetric operations such as `less` and `greater`.
- Unsigned normalized formats clamp the reference to `[0,1]` before comparison.
- The GLSL shadow-sampler lookup and the Vulkan sampler's `compareEnable` state must agree so that compilation produces a Dref instruction and execution applies the selected compare operation.

### Filtering comparison results

With nearest filtering, one selected comparison usually determines the result. With linear filtering, implementations may compute a value differently from ordinary color interpolation. Vulkan requires a result in `[0,1]` that should track a weighted proportion of passing or failing comparisons. Mipmap filters add level selection and, for linear mipmap filtering, possible blending between levels.

Why it matters here:

- A single ideal software image is useful but cannot represent every conformant linear comparison implementation.
- The verifier therefore asks whether each rendered pixel is within an allowed set derived from coordinate, LOD, reference, comparison, and PCF precision bounds.
- The second verification tier widens those bounds when the high-quality PCF assumption is too strict.

## One Concrete Example

Consider `dEQP-VK.texture.shadow.2d.linear.less_or_equal_d16_unorm`.

The host creates a mipmapped 2D image, uploads generated depth patterns, binds a comparison-enabled sampler with `VK_COMPARE_OP_LESS_OR_EQUAL`, and draws a quad. The generated fragment shader is conceptually:

```glsl
// Simplified from the generated PROGRAM_2D_SHADOW fragment shader.
layout(set = 0, binding = 0, std140) uniform Block {
    highp float u_bias;
    highp float u_ref;
    highp vec4 u_colorScale;
    highp vec4 u_colorBias;
};
layout(set = 1, binding = 0) uniform highp sampler2DShadow u_sampler;

void main()
{
    float compared = texture(u_sampler, vec3(v_texCoord, u_ref));
    dEQP_FragColor = vec4(compared, 0.0, 0.0, 1.0) * u_colorScale + u_colorBias;
}
```

The `vec3` contains the 2D coordinate followed by Dref. Linear comparison sampling may combine the outcomes of neighboring depth comparisons. The host reads the red channel and checks it against the software model's allowed interval for the exact coordinate and LOD uncertainty.

## End-to-End Test Flow

```text
[host] select image-view family, filter mode, compare operation, format, backing mode, and optional cube edge mode
[host] reject unsupported format, sparse, cube-array, or non-seamless combinations
[host] generate the matching GLSL shadow-sampler program
[host] build gradient and grid textures with complete mip chains
[host] create regular or sparse sampled images, bind memory, upload every required mip and layer, and create image views
[host] create a comparison-enabled sampler and bind the sampled image plus sampler
[host] choose one FilterCase with a texture, Dref value, and coordinate range
[host] draw a quad into an R8G8B8A8_UNORM target
[device] interpolate texture coordinates, select LOD and texels, compare Dref with texel depth, filter comparison outcomes, and write RGBA
[host] read the rendered target and build an ideal software reference image
[host] validate every pixel with high-quality coordinate, LOD, reference, result, and PCF precision bounds
[host] if that tier rejects pixels, retry with the lower precision bounds
[host] pass the FilterCase if either tier accepts every pixel, then repeat until all FilterCases, cube faces, and array layers finish
```

The `texel_replacement.d32_sfloat` test case follows a separate Amber flow. It samples outside a 2D image with an opaque-white border color, Dref `0.5`, and compare operation `greater`. It expects the comparison `0.5 > 1.0` to produce red `0` over the framebuffer.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `TextureTestCase::initPrograms()` calls `initializePrograms()` with one of six shadow program selectors: `PROGRAM_1D_SHADOW`, `PROGRAM_2D_SHADOW`, `PROGRAM_CUBE_SHADOW`, `PROGRAM_1D_ARRAY_SHADOW`, `PROGRAM_2D_ARRAY_SHADOW`, or `PROGRAM_CUBE_ARRAY_SHADOW`.
- `initializePrograms()` specializes shared GLSL 4.50 vertex, fragment, and compute templates. These cases execute through the graphics backend, so the vertex and fragment shaders form the runtime pipeline.
- The shadow program selector changes the coordinate type, shadow sampler type, and GLSL lookup signature. The compare operation itself is sampler state, not a shader text branch.
- `texel_replacement.d32_sfloat` loads a fixed Amber script with its own GLSL 4.30 fragment shader and sampler declaration.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Generated sampled texture images | yes | yes | read | no | Gradient and grid patterns expose compare direction, reference clamping, filtering, LOD selection, layers, and cube faces. |
| Comparison sampler | yes | yes | read as sampling state | no | Carries minification, magnification, mipmap, address, compare, and cube edge behavior. |
| Uniform block | yes | yes | read | no | Supplies Dref as `u_ref` and the output scale and bias used by the shared shader. |
| Vertex and texture-coordinate buffers | yes | yes | read | no | Define the quad and the coordinate gradients from which implicit LOD is selected. |
| R8G8B8A8_UNORM render target | yes | yes | written | yes | Stores the shadow result in red, with fixed green, blue, and alpha values also checked. |
| Sparse image allocations and binds | yes, sparse cases only | yes | sampled | no | Exercise the same lookup semantics with sparse image backing and complete residency. |
| Amber border-color image and sampler | yes, `texel_replacement` only | yes | read | no | Isolate border texel replacement before the depth comparison. |

## What Is Checked

- The main C++ cases first render an image and compute an ideal reference with `sampleTexture()`.
- If a rendered red value differs from the ideal value, `computeTextureCompareDiff()` reconstructs the pixel coordinate and legal LOD interval, then calls `tcu::isTexCompareResultValid()` to test whether the result is permitted by the configured comparison and precision bounds.
- Green, blue, and alpha must stay within fixed-point thresholds around the reference output.
- The first tier uses image-family-specific coordinate and derivative precision, `referenceBits = 16`, `pcfBits = 5`, and the output's effective red precision.
- A first-tier rejection logs a warning. The second tier sets `lodBits = 4`, lowers active `uvwBits` to `4`, and sets `pcfBits = 0`. The test fails only when this tier also rejects at least one pixel.
- Floating-point depth and depth-stencil source copies are clamped to `[0,1]` before software reference sampling to mirror the uploaded Vulkan image contents.
- The Amber case requires every output pixel to equal `(0,0,0,255)`.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family below `texture.shadow`
>
> **Candidate values:** `2d`, `cube`, `2d_array`, `1d`, `1d_array`, `cube_array`, `texel_replacement`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect 2D Dref operand handling, compare operation, implicit LOD, mip filtering, PCF result, format conversion, or sparse 2D sampling. |
| `cube` | A common comparison or filtering fault, or incorrect cube-face selection, edge handling, non-seamless mode, or sparse cube sampling. |
| `2d_array` | A common 2D comparison fault, or incorrect array-layer selection combined with depth comparison and filtering. |
| `1d` | Incorrect 1D shadow coordinate interpretation, implicit LOD, comparison, or filtering. |
| `1d_array` | A 1D comparison fault or incorrect separation of the array layer from the Dref operand. |
| `cube_array` | Incorrect cube-array direction, layer, and Dref operand handling, cube edge behavior, or common comparison and filtering logic. |
| `texel_replacement` | Incorrect clamp-to-border texel replacement or use of the replacement depth in the comparison. |

A failure across several families may instead come from shared sampler compare-state mapping, generated shadow-sampler shader lowering, image upload, or result readback.

## Important Variations and Special Cases

- Six intermediate filter nodes cover nearest and linear filtering with no mipmap selection, nearest mip selection, or linear mip blending.
- Eight compare operations cover ordered, equality, constant-true, and constant-false behavior.
- Six depth or depth-stencil formats and two color formats are registered. Every normal Vulkan case requires the sampled-image depth-comparison format feature.
- `regular` and `sparse_` leaves run the same shader and verifier. Sparse changes allocation, binding, upload, and image creation. It is omitted for `1d` and `1d_array` because sparse residency is not legal for those generated 1D images.
- `cube` and `cube_array` register seamless and `non_seamless_` leaves. The latter requires `VK_EXT_non_seamless_cube_map`.
- Test instances use in-range references plus `1.1` and `-0.1` cases. The out-of-range cases probe reference clamping where applicable.
- The `equal` and `not_equal` instances use endpoint references so generated fixed-point texels can exercise exact comparison outcomes.
- Vulkan SC omits sparse, non-seamless, and Amber registration. Its C++ image verification runs only in subprocess mode.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main implementation and verification wrapper | [`verifyTexCompareResult()`](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L155-L210) | Builds the ideal image, clamps floating-point depth copies, invokes the validity verifier, and logs failures. |
| Representative 2D setup and checks | [`Texture2DShadowTestInstance`](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L246-L468) | Shows generated textures, FilterCases, draw execution, and both precision tiers. |
| Family and matrix registration | [`populateTextureShadowTests()`](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1729-L2077) | Defines direct families, filters, compare operations, formats, backing modes, dimensions, and the Amber leaf. |
| Shader generator | [`initializePrograms()`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L760) | Specializes sampler types, coordinate forms, and Dref lookup signatures. |
| Image backing and upload | [`TextureBinding::updateTextureData()`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L808-L921) | Creates regular or sparse images and uploads them for shader reads. |
| Vulkan sampler mapping | [`mapSampler()`](../../../framework/vulkan/vkImageUtil.cpp#L4472-L4510) | Maps CTS compare and filtering state to `VkSamplerCreateInfo`. |
| Per-pixel 2D verifier | [`computeTextureCompareDiff()`](../../../../../framework/opengl/gluTextureTestUtil.cpp#L2648-L2765) | Reconstructs coordinates and LOD bounds before checking legal compare results. |
| PCF validity rules | [`tcuTexCompareVerifier.cpp`](../../../../../framework/common/tcuTexCompareVerifier.cpp) | Computes allowed nearest, bilinear, and trilinear comparison-result ranges. |
| Amber special case | [`d32_sfloat.amber`](../../../data/vulkan/amber/texture/shadow/texel_replacement/d32_sfloat.amber) | Defines the border replacement setup and exact expected output. |
| Vulkan depth comparison semantics | [Depth Compare Operation](../../../../vulkan-docs/src/chapters/textures.adoc#L703-L728) | Defines Dref ordering, reference clamping, and implementation-dependent linear comparison filtering. |
| Sampler compare state | [`VkSamplerCreateInfo`](../../../../vulkan-docs/src/chapters/samplers.adoc#L107-L108) | Defines `compareEnable`; nearby validity rules constrain `compareOp`. |
| Sparse image feature requirements | [Sparse image features](../../../../vulkan-docs/src/chapters/features.adoc#L727-L754) | Defines sparse binding and 2D sparse residency support. |

## Questions / Risk Points for User Audit

- Does the two-tier explanation make clear that tier 1 is diagnostic and tier 2 is the final conformance floor after tier 1 fails?
- Is the distinction between filtering depth values and filtering per-texel comparison outcomes clear enough without implying one fixed PCF algorithm?
- Does treating the seven direct test families as the primary behavioral axis give useful failure localization?
- Is the separate Amber border-replacement case clearly bounded from the generated C++ matrix?
- Are sparse backing and non-seamless cube behavior explained as execution variants rather than different comparison semantics?

No unresolved source ambiguity changes the final page semantics, representative walkthrough, or pass criteria.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.texture.shadow.2d.linear.less_or_equal_d16_unorm` for one representative fragment shader walkthrough.
- Keep depth comparison, Dref ordering, and implementation-dependent PCF as short local prerequisites.
- Present the seven direct test families as the primary behavior parameter, then describe filters, compare operations, formats, backing, and seam mode in the full parameter table.
- Preserve the two-tier verifier explanation and the separate Amber flow.
- Copy the `### Failure Cause Mapping` table into the final page unchanged.
- Move detailed source navigation into the final appendix.
