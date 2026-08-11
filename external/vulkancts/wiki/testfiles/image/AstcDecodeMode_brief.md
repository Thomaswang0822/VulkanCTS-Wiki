# Understanding Brief: `image.astc_decode_mode`

## One-Sentence Test Purpose

This test checks whether an ASTC image view applies each legal `VK_EXT_astc_decode_mode` intermediate format and produces samples consistent with the corresponding default-decoded reference.

## Background Knowledge

### ASTC decode mode belongs to an image view

`VkImageViewASTCDecodeModeEXT` extends image-view creation and selects the intermediate format used when an ASTC-compressed image view decodes texels. Vulkan permits `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R8G8B8A8_UNORM`, and `VK_FORMAT_E5B9G9R9_UFLOAT_PACK32`; the shared-exponent option requires `decodeModeSharedExponent`. The view format must be ASTC, and `R8G8B8A8_UNORM` cannot decode ASTC HDR blocks. For an sRGB ASTC view, the specification says that the decode mode has no effect. See the [image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L7098-L7135) and [feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L2248-L2269).

Why it matters here:

- The test puts the extension structure only on the tested view. A second view of a duplicate image provides the default-decode comparison.
- The matrix includes the three legal decode formats, skips the 3D ASTC SFLOAT-to-`R8G8B8A8_UNORM` combination, and skips shared-exponent cases when the feature is unavailable.

### Sampling two identically populated images

The test writes the same generated valid ASTC blocks into two separate images. It samples the image whose view carries the decode-mode structure and samples the reference image through an ordinary view. A compute shader converts the comparison into a visible result image, so the host does not need an ASTC decoder to calculate each expected texel.

Why it matters here:

- A mismatch represents disagreement between the override path and the source-defined reference adjustment, not a comparison against hard-coded random texel values.
- Nearest filtering and one compute invocation per output texel keep the comparison tied to a single sampled coordinate.

## One Concrete Example

`dEQP-VK.image.astc_decode_mode.4x4_unorm_to_e5b9g9r9_ufloat_pack32` uses a 64 x 64 2D `VK_FORMAT_ASTC_4x4_UNORM_BLOCK` image. The CTS writes one generated block stream into both images, creates the tested view with `decodeMode = VK_FORMAT_E5B9G9R9_UFLOAT_PACK32`, and creates the reference view without the extension structure. The compute shader samples both views. Before comparing, it clamps the reference to nonnegative RGB and alpha 1, which matches the source's special handling for this decode mode. It writes `0.5` to an `R8G8B8A8_UNORM` result texel when `distance(tested, reference) < 0.01`; otherwise it writes zero. The host accepts bytes from 100 through 150, which covers the encoded value near 128 for 0.5.

## End-to-End Test Flow

```text
[host] select an ASTC source format, image type, extent, and decode mode
[host] check extension, feature, image-format-property, and storage-image support
[host] generate valid ASTC blocks and copy the same bytes into tested and reference images
[host] create a tested view with VkImageViewASTCDecodeModeEXT and a default reference view
[host] create a compute pipeline with two combined image samplers and one storage image
[host] transition images, dispatch one 1 x 1 x 1 workgroup per uncompressed texel, and copy the result image to a host buffer
[device] sample both views, apply any E5B9G9R9 comparison adjustment, and store 0.5 or 0.0
[host] invalidate the readback allocation and reject the case when any first result-channel byte lies outside 100..150
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`AstcDecodeModeCase::initPrograms()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L425-L479) builds one GLSL 4.50 compute shader per test case. Its sampler and storage-image types follow the selected image type and result format.
- [`createImageAstcDecodeModeTests()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L488-L617) builds the source-format and decode-mode matrix. The 2D matrix uses 14 UNORM/sRGB ASTC footprints; non-VulkanSC builds also add 3D UNORM, sRGB, and SFLOAT footprints.
- [`generateRandomValidBlocks()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L211-L224) supplies a random valid ASTC block stream. The source copies that stream into both compressed images.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Tested ASTC image and tested view | Yes | Yes | Sampled by binding 0 | No | Its view carries `VkImageViewASTCDecodeModeEXT`. |
| Reference ASTC image and ordinary view | Yes | Yes | Sampled by binding 1 | No | It contains identical blocks but uses default view decoding. |
| Host-visible input buffer | Yes | Yes | Read by transfer commands | No | Uploads the generated block bytes into both images. |
| `R8G8B8A8_UNORM` result image and view | Yes | Yes | Written through storage-image binding 2 | Yes, through the result buffer | Converts per-texel comparison into host-visible bytes. |
| Host-visible result buffer | Yes | Yes | Written by image-to-buffer copy | Yes | The host scans its first byte in each four-byte texel. |
| Nearest sampler and descriptor set | Yes | Yes | Used by the compute shader | No | Bindings 0 and 1 sample the compared views; binding 2 writes the result. |

## What Is Checked

- The shader samples both views at each generated coordinate and tests `distance(tested, reference) < 0.01` ([comparison generation](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L446-L475)).
- A matching comparison stores 0.5 in every component of the result texel. A mismatch stores zero.
- The host inspects the first byte of each result texel. A byte below 100 or above 150 fails the test ([readback check](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L358-L371)).
- Each registered test case runs and reports independently.

## Behavior Parameter Identification

> **Behavior parameter:** selected ASTC decode mode
>
> **Candidate values:** `r16g16b16a16_sfloat`, `r8g8b8a8_unorm`, `e5b9g9r9_ufloat_pack32`

The registered leaf also selects an ASTC source footprint and encoding. The decode-mode suffix is the primary behavioral axis because it changes the intermediate-format rule placed on the tested view.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `r16g16b16a16_sfloat` | The ASTC view override, floating-point intermediate conversion, tested/reference sampling, or result-image comparison path disagrees with the reference behavior. |
| `r8g8b8a8_unorm` | The normalized-unsigned override path, its legal non-HDR source handling, tested/reference sampling, or result-image comparison path disagrees with the reference behavior. |
| `e5b9g9r9_ufloat_pack32` | The shared-exponent feature/override path or its nonnegative-and-alpha comparison adjustment disagrees with the tested sample result. |

## Important Variations and Special Cases

- **2D versus 3D images.** The 2D cases use `UVec3(64, 64, 1)`; non-VulkanSC builds add 3D cases at `UVec3(64, 64, 3)`. The shader switches between 2D and 3D coordinates and sampler/image types ([generator branches](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L433-L457)).
- **Shared exponent.** `e5b9g9r9_ufloat_pack32` requires `decodeModeSharedExponent`; unsupported devices report the case as not supported rather than failing it ([support check](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L414-L416)).
- **SFLOAT source pruning.** The 3D SFLOAT source formats do not register an `r8g8b8a8_unorm` leaf ([registration guard](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L592-L613)), consistent with the ASTC HDR valid-usage restriction.
- **sRGB source formats.** The matrix includes sRGB ASTC formats. The specification states that decode mode has no effect for an sRGB view, so these leaves still exercise valid view construction and sampling without an overridden sRGB interpretation.
- **E5B9G9R9 comparison branch.** The shader adjusts the reference for UNORM and SFLOAT source flags before comparison; the SFLOAT branch also clamps the tested result to 65504 ([special-case code](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L459-L473)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters and resource setup | [`BasicComputeTestInstance::iterate()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L95-L371) | Creates the images, views, descriptors, transfer barriers, dispatch, readback, and host verdict. |
| Support requirements | [`AstcDecodeModeCase::checkSupport()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L392-L423) | Requires the extension, ASTC LDR support, supported image configurations, shared exponent when needed, and result storage-image support. |
| Shader generation | [`AstcDecodeModeCase::initPrograms()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L425-L479) | Emits the 2D/3D sampling comparison and E5B9G9R9 adjustments. |
| Matrix registration | [`createImageAstcDecodeModeTests()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L488-L617) | Defines ASTC footprints, decode modes, dimensions, VulkanSC guard, and excluded combinations. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) | Registers `astc_decode_mode` below the `image` test category. |
| View semantics | [ASTC decode-mode image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L7098-L7135) | Defines legal intermediate formats, feature dependence, HDR restriction, and sRGB behavior. |

## Questions / Risk Points for User Audit

- Does the page make clear that the test compares a decode-mode view with an ordinary view of a separate, identically populated image?
- Is the decode-mode suffix the right primary behavioral axis, with source ASTC format and dimensionality treated as matrix dimensions?
- Does the explanation distinguish source-level comparison adjustments from Vulkan's image-view validity rules?
- Should the final page keep one representative shader walkthrough for the shared-exponent UNORM case, or would a non-special case be easier to read?

## Conversion Notes for Final Wiki Rewrite

- Keep the decode-mode suffix as the primary behavior parameter and copy the failure-cause table unchanged.
- Distill the view-local decode mode and dual-image comparison concepts into short final-page background bullets.
- Use `4x4_unorm_to_e5b9g9r9_ufloat_pack32` for the shader walkthrough because it exposes the E5B9G9R9 comparison branch; describe ordinary paths in the variation summary.
- Move source detail into the appendix, retain the complete registration tree, and state the support and matrix pruning rules in their final-page sections.
