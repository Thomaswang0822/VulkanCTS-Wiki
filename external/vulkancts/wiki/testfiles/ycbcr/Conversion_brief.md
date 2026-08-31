# Understanding Brief: `ycbcr.conversion`

## One-Sentence Test Purpose

This test checks whether Vulkan sampler YCbCr conversion produces sampled colors within the bounds allowed by the selected format, conversion model, chroma reconstruction mode, and filtering parameters.

## Background Knowledge

### Multi-plane images and sampler conversion

A YCbCr image can store luma and chroma in separate planes, with chroma sampled at a lower resolution for 4:2:0 or 4:2:2 formats. A `VkSamplerYcbcrConversion` describes how a sampler interprets those planes, including the color model, range, chroma location, and reconstruction filter.

Why it matters here:
- The test fills the logical channels through `MultiPlaneImageData`, then lets the Vulkan sampler reconstruct and convert them.
- `VK_CHROMA_LOCATION_COSITED_EVEN` and `VK_CHROMA_LOCATION_MIDPOINT` select different legal sample locations for subsampled chroma.

### Filtered sampling has a range of valid results

Nearest and linear filtering can read one or several texels. Floating-point precision, filter precision, and the device's `subTexelPrecisionBits` affect the exact result, so the test compares each sampled component with an interval rather than one exact value.

Why it matters here:
- The reference uses the same format, filter, conversion model, range, chroma location, component mapping, and address modes to calculate minimum and maximum values.
- For implicit nearest sampling with cosited chroma, the implementation may use either the cosited or midpoint interpretation, so the result is accepted only when it lies in at least one of those two intervals.

## One Concrete Example

Consider a `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` case with `VK_SAMPLER_YCBCR_MODEL_CONVERSION_YCBCR_601`, full range, nearest texture filtering, and midpoint chroma locations. The host fills the R, G, and B logical channels with horizontal, vertical, and diagonal gradients. The generated shader samples one combined image sampler at each generated coordinate and writes the returned `vec4` to its output. The host reference predicts the range of legal converted values at the same coordinates and compares the device output with those ranges.

The sampler-array variant binds up to four samplers in one descriptor binding. The shader samples `u_sampler[0]` through `u_sampler[3]`, so the host checks one result image for each conversion model.

## End-to-End Test Flow

```text
[host] choose a format, conversion model, range, filters, chroma locations, tiling, disjoint state, shader type, and sampler binding
[host] create a `VkSamplerYcbcrConversion`, sampler, multi-plane image, image view, descriptor set, and shader executor
[host] fill the logical channels with gradients and generate normalized texture coordinates
[host] build or load the shader that samples the combined image sampler
[host] upload the image through a staging path for optimal tiling or fill linear-tiled memory directly
[host] make the image available in `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`
[device] execute the shader for all generated coordinates
[device] write one `vec4` result per coordinate and per sampler-array element
[host] calculate per-result lower and upper bounds from the source channels and selected conversion parameters
[host] compare every returned component with its bounds and decide pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `createTestShaders()` builds a `ShaderSpec` for a single sampler or an array of samplers. The source uses `texture(u_sampler, uv)` or one such expression per sampler-array element.
- `YCbCrConversionTestBuilder::buildTests()` generates format groups and the `color_conversion`, `chroma_reconstruction`, and `sampler_array` test families from the parameter lists in the source.
- The source collection compiles the selected shader type. The builder chooses among vertex, fragment, and compute shader types with its deterministic random generator.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multi-plane `VkImage` | yes | yes, through its image view | read by sampling | no | Stores the channel gradients in the selected format and tiling. |
| `VkSamplerYcbcrConversion` | yes | attached to sampler and image view | controls sampling interpretation | no | Selects model, range, chroma location, reconstruction, and component mapping. |
| Combined image sampler descriptor | yes | yes | read by shader | no | Carries one sampler and image view, or an array of them, at `samplerBinding`. |
| Texture-coordinate input `uv` | yes, as executor input | yes | read by shader | no | Selects the sample locations checked by the reference. |
| Shader output `o_color` | no, shader output | yes | written by shader | yes, through executor output storage | Carries the converted sample returned for each coordinate. |
| Host reference bounds | yes, CPU vectors | no | no | no | Defines the permitted interval for each expected result. |

## What Is Checked

- `textureConversionTest()` fills present channels with gradients, generates sample coordinates, executes the shader, and computes bounds with `calculateBounds()`.
- Each result component must be between its lower and upper bound. The test accepts a result from the midpoint bounds as well when the case uses implicit nearest sampling with a cosited chroma location.
- The test returns `Pass` when no result falls outside its permitted interval. It logs the result, bounds, coordinates, and nearby source values for failures, then returns `Result comparison failed`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `color_conversion`, `chroma_reconstruction`, `one_to_one`, `sampler_array`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color_conversion` | Incorrect model or range conversion, format interpretation, filtering, component mapping, descriptor binding, or shader sampling result. |
| `chroma_reconstruction` | Incorrect chroma filtering, chroma-location handling, explicit reconstruction behavior, disjoint-plane handling, or component mapping. |
| `one_to_one` | Incorrect sampling of a fixed-size 4:2:0 image at texel centers or incorrect handling of the selected tiling or chroma locations. |
| `sampler_array` | Incorrect creation, binding, indexing, or sampling of the array of converted samplers. |

## Important Variations and Special Cases

- Non-subsampled formats test color conversion without requiring chroma reconstruction. Subsampled formats add independent X and Y chroma-location choices and reconstruction cases.
- Full and narrow ITU ranges are generated. The builder omits narrow-range cases when any relevant YCbCr channel has fewer than 8 bits.
- `VK_IMAGE_TILING_LINEAR` uses host-visible image memory for initialization. `VK_IMAGE_TILING_OPTIMAL` uses an upload path.
- Disjoint cases create and validate plane-compatible support before execution.
- The `one_to_one` family fixes the format to `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, uses source sizes `16x16` and `20x12`, and samples at texel centers.
- The sampler-array family uses `VK_SAMPLER_YCBCR_MODEL_CONVERSION_LAST` as an internal sentinel. The runtime expands it to the first four model conversions and writes one output for each sampler.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader specification | [`createShaderSpec()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L92-L123) | Defines the single-sampler and sampler-array shader bodies. |
| Resource and descriptor setup | [`evalShader()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L399-L500) | Creates conversions, samplers, image views, descriptors, uploads the image, and executes the shader. |
| Feature checks | [`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L526-L646) | Shows the extension, feature, format-feature, filtering, reconstruction, disjoint, and chroma-location requirements. |
| Input and result checking | [`textureConversionTest()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L650-L1128) | Fills gradients, generates coordinates, computes bounds, executes sampling, and decides pass or fail. |
| Test generation | [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1362-L2139) | Generates format, conversion, reconstruction, and one-to-one cases. |
| Sampler arrays | [`buildArrayOfSamplersTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2141-L2180) | Generates the sampler-array family and its binding variants. |
| Bounds calculation | [`calculateBounds()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625-L1670) | Establishes the reference interval from filtering and conversion precision. |
| Sampler semantics | [`Samplers`](../../../../vulkan-docs/src/chapters/samplers.adoc#samplers) | Defines sampler filtering, addressing, and sampler-object behavior. |
| Image semantics | [`Images`](../../../../vulkan-docs/src/chapters/images.adoc#images) | Provides the Vulkan image and image-view context used by the conversion setup. |

## Questions / Risk Points for User Audit

- Is `test family` the right primary behavioral axis for the final page, or should `color_conversion` and `chroma_reconstruction` be treated as separate axes?
- Is the distinction between a host-created image resource and the shader-generated `uv` and `o_color` interface clear?
- Should the final walkthrough use a single-sampler fragment-stage example or a sampler-array example as its representative shader?
- Are the midpoint-versus-cosited bounds and their limited acceptance rule clear?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to the two concepts needed for interval-based YCbCr sampling: multi-plane conversion and bounded filtered results.
- Use the test family as the page's primary behavioral axis and carry the four-row failure table into the final page unchanged.
- Use one representative GLSL sampling walkthrough. The shader body is the generated single-sampler form; the page should explain that the builder can emit vertex, fragment, or compute variants without duplicating all three.
- Put the full generated matrix in `## Parameter Dimensions and Observed Values`; keep the registration tree at the format-group level.
- Explain the implicit-nearest cosited fallback in `## Failure Meaning`, not in Background Knowledge.
