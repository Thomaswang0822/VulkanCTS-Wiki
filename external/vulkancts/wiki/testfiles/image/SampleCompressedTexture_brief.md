# Understanding Brief: `image.sample_texture`

## One-Sentence Test Purpose

This group verifies that a BC1 or BC3 image, written as block-sized unsigned-integer texels through a compatible uncompressed storage view, can subsequently be sampled through its compressed image view and decode to blue.

## Background Knowledge

### One uncompressed view texel represents one compressed block

The storage image is created in a block-compressed format and with mutable-format, extended-usage, and block-texel-view-compatible flags. The compute shader does not address the 80 x 80 decoded-pixel extent: it addresses the block grid through a size-compatible unsigned-integer view. BC1's 64-bit blocks use `VK_FORMAT_R32G32_UINT`; BC3's 128-bit blocks use `VK_FORMAT_R32G32B32A32_UINT`.

### The two view roles must not be confused

The test uses a **compressed-format view** for the meaningful fragment sample. It may also create an **uncompressed-format view** for the two-sampler variant. Sampling that integer view exposes block representation rather than BC-decoded color; the source deliberately renders that result first and overwrites it with the compressed-view result. It is not an assertion that the uncompressed-view sample itself is blue.

## One Concrete Example

`dEQP-VK.image.sample_texture.64_bit_compressed_format` creates an 80 x 80 `VK_FORMAT_BC1_RGB_UNORM_BLOCK` image. A `rgba32ui` compute shader views it as `VK_FORMAT_R32G32_UINT`, dispatches once per 4 x 4 compressed block, and stores hard-coded BC1 red data. A fragment shader samples the same image through a BC1 view and draws red. The test repeats the write with hard-coded BC1 blue data, samples again, copies the rendered `R8G8B8A8_UNORM` target to host memory, and compares it to solid blue with a 0.01 threshold.

## End-to-End Test Flow

```text
[host] select BC1/BC3, ordinary/cubemap, and one/two-sampler configuration
[host] verify maintenance2 and the combined image creation flags/usages
[host] create a compressed storage image plus compatible uncompressed storage view
[device] compute-write a red then blue (one sampler), or blue (two samplers), compressed block stream
[host] create a compressed sampled view with VkImageViewUsageCreateInfo excluding STORAGE usage
[device] draw a full-screen quad that samples the compressed view into an RGBA8 target
[host] copy target to host-visible buffer and require the final image to be blue
```

## Generated Test Artifacts and Bound Resources

| Artifact or resource | Producer / configuration | Role |
|---|---|---|
| Compute GLSL (`comp`) | `initPrograms()` | Writes literal BC1 or BC3 blocks through `rgba32ui` storage image. |
| Vertex GLSL (`vert`) | `initPrograms()` | Passes full-screen-quad UVs to the fragment shader. |
| Fragment GLSL (`frag`) | `initPrograms()` | Samples the compressed view; the two-sampler branch can first sample the raw integer view. |
| Compressed storage image | Host | BC1 or BC3 backing image, also transfer and sampled capable. |
| Compatible unsigned-integer view | Host | Compute storage-image view with one texel per compressed block. |
| Compressed sampled view | Host | Fragment sampler view that decodes BC data. |
| Optional integer sampled view | Host, two-sampler leaves only | First-pass raw block sample; its rendered values are intentionally not the verdict. |
| RGBA8 target and result buffer | Host | Receives fragment output and makes it readable by the host. |

## What Is Checked

- A BC1/BC3 image supports the selected flags and combined usage request.
- Storage writes through the compatible uncompressed view become valid compressed data for sampling through a compressed view.
- The final non-cubemap target matches opaque blue within `0.01` per component.
- A cubemap leaf writes and samples every array face, then checks that the final target has zero red and nonzero blue and alpha.

## Behavior Parameter Identification

> **Behavior parameter:** compressed block size / format class
>
> **Candidate values:** `64_bit_compressed_format` (BC1 / 64-bit block) and `128_bit_compressed_format` (BC3 / 128-bit block)

The suffixes `two_samplers` and `cubemap` are important execution variations: the former adds a raw integer-view sampling pass, and the latter repeats the storage-write and draw work for six layers.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `64_bit_compressed_format` | BC1 block-texel compatible view creation, BC1 storage write, compressed-view sampling/decoding, synchronization, or RGBA8 result comparison is incorrect. |
| `128_bit_compressed_format` | Equivalent failure in the 128-bit BC3 path, including the `R32G32B32A32_UINT` compatible view. |

## Important Variations and Special Cases

- **Two samplers.** The first render samples an uncompressed integer view and can produce garbage; the second render samples the compressed view and is the final result. The compute shader writes blue only once in this variant.
- **One sampler.** The source writes red in pass 0 and blue in pass 1, with both draws sampling the compressed view. Only the final blue render is compared.
- **Cubemap.** The image has six layers and uses a separate 2D view and descriptor set for each face, rather than a cube sampler. One RGBA8 target is reused; its final contents provide the host verdict, so it is not six independently retained readbacks.
- **Scope.** The registration has only BC1 and BC3 leaves; it does not sweep BC2/BC4–BC7, ETC/EAC, or ASTC. The fixed decoded extent is 80 x 80.

## Source Mapping

| Topic | Source link |
|---|---|
| Image flags, usages, and fixed dimensions | [`makeImageCreateInfo()` and constants](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L76-L120) |
| Resource setup, command recording, and verdict | [`SampleDrawnTextureTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L259-L689) |
| Support gates | [`SampleDrawnTextureTest::checkSupport()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L719-L753) |
| Generated shaders | [`SampleDrawnTextureTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L755-L836) |
| Registered leaves and their parameters | [`createImageSampleDrawnTextureTests()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L845-L915) |
| Parent `image` registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) |

## Questions / Risk Points for User Audit

- Does the distinction between the compatible integer view and the compressed sampled view remain clear?
- Does the cubemap caveat state the source behavior precisely: all six faces execute, but the host retains one reused target image?
- Does the behavior parameter correctly remain the BC1 or BC3 block class rather than the `two_samplers` or cubemap variation?

## Conversion Notes for Final Wiki Rewrite

- Preserve the distinction between the raw compatible integer view and the compressed sampled view.
- Describe the `two_samplers` first pass as intentional setup/coverage, not as a separate blue-result assertion.
- Keep the complete eight-leaf registration tree and expose BC1/BC3 as the primary behavior axis.
- State the cubemap readback limitation precisely: all faces are exercised, but one reused target supplies the final host check.
