# Understanding Brief: `image.load_store_multisample`

## One-Sentence Test Purpose

This test checks whether compute shaders can store and reload an independently generated value for every sample of a multisampled storage-image texel.

## Background Knowledge

### Multisampled storage-image access

A multisampled image holds several samples at one texel coordinate. A shader accesses a particular sample with an integer sample index; it does not filter or resolve the samples. `imageStore` and `imageLoad` therefore operate on the address formed by the texel coordinate and sample index.

Why it matters here:
- The test must prove that each sample preserves its own value rather than checking one value per pixel.
- A checksum records how many individual sample loads matched the generated expectation.

### Storage-image visibility

A pipeline barrier can make shader writes available to later shader reads when it names the producer and consumer stages and access types. The image stays in `VK_IMAGE_LAYOUT_GENERAL` between the compute store and compute load passes; the barrier changes visibility rather than layout.

Why it matters here:
- The second dispatch reads data written by the first dispatch.
- A checksum mismatch covers the complete store, visibility, load, and comparison sequence, not only image addressing.

## One Concrete Example

Consider the registered test case:

```text
dEQP-VK.image.load_store_multisample.2d_array.r8g8b8a8_unorm_single_layer.samples_4
```

The host creates a 32x32 four-layer multisampled `VK_FORMAT_R8G8B8A8_UNORM` storage image and a four-layer, single-sample `VK_FORMAT_R32_SINT` checksum image. For each layer, it creates a 2D view, a descriptor set, and a uniform-buffer slice containing that layer index.

The store dispatch runs at `(32, 32, 1)` for each layer. Its shader loops over sample indices 0 through 3 and writes a coordinate- and sample-dependent color. After a compute write-to-read barrier, the load dispatch uses the same view and layer index, reloads all four samples, and writes the number of successful comparisons to the checksum image. The host copies the checksum image to a buffer and requires every integer to equal 4.

## End-to-End Test Flow

```text
[host] register a 2D or four-layer 2D-array texture, format, sample count, and view-binding mode
[host] reject unsupported storage-image format/sample combinations
[host] create the multisampled storage image, single-sample checksum image, views, descriptor sets, and host-visible buffers
[host] generate store and load compute shaders
[host] transition both images from UNDEFINED to GENERAL and submit the store dispatch
[device] store a generated value for every sample of every addressed texel
[host] record a compute shader-write to shader-read barrier for the multisampled image and submit the load dispatch
[device] reload every sample, count matching values, and write one checksum integer per texel/layer
[host] transition the checksum image to TRANSFER_SRC_OPTIMAL, copy it to the result buffer, and make transfer writes visible to the host
[host] invalidate the result allocation and require every checksum integer to equal the requested sample count
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` generates two GLSL 4.50 compute shaders for every case:

- `comp_store` declares a `writeonly` multisampled image at binding 1 and writes all samples.
- `comp_load` declares the same image as `readonly`, compares every loaded sample with the generated expectation, and writes an integer checksum to binding 2.
- For `A8_UNORM_KHR`, both shaders require `GL_EXT_shader_image_load_formatted` and omit the image-format layout qualifier.

The generated color uses XOR expressions of `gx`, `gy`, `gz`, and `sampleNdx`. The red term includes `(sampleNdx >> 5) ^ (sampleNdx & 31)`, which keeps the generated value in range for the 64-sample case. Integer formats compare vectors exactly. Float and normalized formats compare `abs(abs(actual) - abs(expected))` componentwise against a strict `0.02` threshold.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multisampled image | Yes | Binding 1 | Store pass writes; load pass reads | No | Holds the tested per-sample data in the case format. |
| Checksum image | Yes | Binding 2 in the load pass | Load pass writes | Yes, through the result buffer | Stores the number of samples that matched at each texel/layer. |
| Constants buffer | Yes | Binding 0 | Read only for `*_single_layer` | No | Supplies `u_layerNdx` for a single-layer view. |
| Result buffer | Yes | Transfer destination | Transfer writes | Yes | Receives the checksum image for the final host scan. |
| Image views and descriptor sets | Yes | Yes | Referenced by each dispatch | No | Select either all array layers or one layer at a time. |

The checksum image always has one sample and uses `VK_FORMAT_R32_SINT`. It validates the multisampled image; it does not resolve or preserve the source samples.

## What Is Checked

- The store shader writes one generated value for each `(x, y, layer, sample)` address.
- The load shader checks every sample of the same address. It increments a local checksum for each matching sample and stores the final count in the checksum image.
- The host checks every checksum value after copyback. The expected value is `caseDef.texture.numSamples()`.
- Unsupported format or sample-count combinations throw `NotSupportedError`; they are skipped rather than failed.

## Behavior Parameter Identification

> **Behavior parameter:** image topology and array-view binding strategy
>
> **Candidate values:** `2d`; `2d_array`; `2d_array.<format>_single_layer`.

The all-layer 2D-array case uses one `image2DMSArray` view and a z-sized dispatch. The `*_single_layer` case uses one 2D view and one dispatch per layer, with `u_layerNdx` supplying the global layer number for the shared color pattern. Format and sample count affect representation and loop extent, but keep the same store, barrier, load, checksum sequence.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Per-sample storage-image write/read addressing, generated value conversion/comparison, or the compute-to-compute visibility path. |
| `2d_array` | The `2d` causes, plus array image-view type or z-coordinate/layer addressing. |
| `2d_array.<format>_single_layer` | The `2d` causes, plus per-layer view range, descriptor-set selection, constants-buffer layer index, or repeated layer dispatch. |

## Important Variations and Special Cases

- The factory registers 2D images of size 32x32x1 and 2D-array images of size 32x32x4. The latter has both all-layer and single-layer view modes.
- The registered sample counts are `2`, `4`, `8`, `16`, `32`, and `64`. The source queries image-format properties and skips a count that the selected format does not support.
- The format matrix includes float, signed integer, unsigned integer, UNORM, and SNORM formats. `A8_UNORM_KHR` is registered only outside VulkanSC.
- `A8_UNORM_KHR` additionally requires `VK_KHR_maintenance5`, storage reads without format, and storage writes without format. Its generated pattern swaps alpha and red for the store and expects loaded RGB values of zero.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Generated shaders and per-sample pattern | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L81-L204) | Builds the store/load declarations, color expressions, and comparison rule. |
| Support gates | [`checkSupport()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L206-L240) | Requires the feature, supported sample count, and the alpha-only special requirements. |
| Views and descriptor sets | [`insertImageViews()` and `insertDescriptorSets()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L242-L286) | Select one all-layer view or one view/set per layer. |
| Resources, dispatches, barriers, and result scan | [`test()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L288-L538) | Implements the host-side sequence and pass condition. |
| Registered matrix | [`createImageMultisampleLoadStoreTests()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L543-L608) | Defines texture types, formats, sample counts, and group names. |
| Format scale/bias helpers | [`vktImageLoadStoreUtil.cpp`](../../../modules/vulkan/image/vktImageLoadStoreUtil.cpp#L37-L48) | Defines normalized-format scale and SNORM bias. |

## Questions / Risk Points for User Audit

- Does the distinction between per-sample storage-image access and a multisample resolve remain clear?
- Does the example explain why `*_single_layer` changes views, descriptors, dispatch dimensions, and the source of `gz`?
- Does the checksum model make it clear that a mismatch reports an aggregate count rather than the failing sample index?
- Should the final page use the UNORM single-layer case as its one representative shader walkthrough?

## Conversion Notes for Final Wiki Rewrite

The final page should retain the per-sample core question, all-layer versus single-layer behavioral axis, checksum pass rule, support pruning, `A8_UNORM_KHR` exception, and source references. It should distill the background material, copy the failure-cause mapping unchanged, and include one faithful `r8g8b8a8_unorm` store-shader walkthrough with compiler-produced SPIR-V. It must not call this test a resolve test.
