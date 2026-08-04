# Understanding Brief: pipeline multisample image tests

## One-Sentence Test Purpose

This test family checks whether Vulkan renders, reads, and orders data in multisampled images correctly across sampled-image, storage-image, standard-position, sample-order, and 3D-image paths.

## Background Knowledge

### Multisampled images

A multisampled image stores multiple coverage samples for each pixel. A graphics pipeline supplies its sample count through [`VkPipelineMultisampleStateCreateInfo`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200), and compatible rasterization and attachment sample counts are required by the pipeline rules ([`rasterizationSamples`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3016-L3028)). Sampling or fetching a multisampled image selects an individual sample rather than applying an implicit resolve.

Why it matters here:
- The tests create images with `2`, `4`, `8`, `16`, `32`, or `64` samples and make the sample data observable through a later shader or host readback.
- A resolved image can reveal aggregate color errors, while a shader can inspect each original sample.

### Storage access and sample identity

The [`shaderStorageImageMultisample`](../../../../vulkan-docs/src/chapters/features.adoc#L577-L581) feature controls whether shaders can access multisampled storage images. Standard sample locations provide defined sample positions when the device advertises `standardSampleLocations`; the source compares its rendered sample colors with those position-derived expectations.

Why it matters here:
- `storage_image`, `samples_mapping_order`, and `3d` require multisampled storage-image support.
- `standardsampleposition` stops as unsupported when the physical-device limit does not advertise standard sample locations.

## One Concrete Example

For `pipeline.monolithic.multisample.sampled_image.64x64_1.r8g8b8a8_unorm.samples_4`, CTS renders layered content into a four-sample color image. A later fragment shader reads the multisampled image at each sample index and writes a checksum image. The host copies that image to memory and fails if any checksum pixel reports an unexpected sample color.

## End-to-End Test Flow

```text
[host] select an intermediate node, image extent, layer count, format, sample count, and pipeline construction type
[host] check image-format properties and any feature or limit required by that behavior
[host] generate vertex, fragment, and, where needed, compute shader programs
[host] create multisampled attachments or images, descriptors, pipelines, and host-visible readback storage
[device] render sample-distinguishable values into the multisampled image
[device] sample, load/store, resolve, or inspect the image through the selected behavior
[host] submit, wait, invalidate mapped readback memory, and compare the observed data
[host] report pass only when the behavior-specific validator accepts the result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source constructs GLSL strings for each behavior. `sampled_image` uses fragment shaders to render and then sample individual multisample-image values. `storage_image` and `samples_mapping_order` also generate compute shaders. The generated shaders reflect the selected `VkFormat`, sample count, layer layout, and test mechanism.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multisampled image | Yes | Yes | Written by graphics; read by graphics or compute | Indirectly or directly | Holds the per-sample values under test. |
| Resolve or checksum image | Yes | Yes | Written after the test operation | Yes | Turns device observations into host-visible pixels. |
| Descriptor set and image views | Yes | Yes | Read by shaders | No | Exposes the selected multisampled image access mode. |
| Host-visible checksum or storage buffer | Yes | Yes | Written by a copy or compute shader | Yes | Carries validation data to CTS. |

## What Is Checked

- `sampled_image` compares each sample-derived checksum against the expected rendered color.
- `storage_image` reads multisample storage-image data through two paths and compares the resulting layered images, with integer-format tolerance handling in [`compareImages()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2074-L2139).
- `standardsampleposition` counts checksum failures after rendering colors derived from standard sample locations.
- `samples_mapping_order` calculates a sample-index-weighted value per pixel and requires every storage-buffer value to match the first.
- `3d` uses its dedicated 3D image setup and checksum validation path.

## Behavior Parameter Identification

> **Behavior parameter:** direct intermediate node under `pipeline.monolithic.multisample`
>
> **Candidate values:** `sampled_image`, `storage_image`, `standardsampleposition`, `samples_mapping_order`, `3d`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sampled_image` | Per-sample sampled-image read or sample-derived checksum does not match rendered data. |
| `storage_image` | Multisampled storage-image load/store behavior disagrees with the reference image path. |
| `standardsampleposition` | Rendered sample identity does not match the required standard sample positions. |
| `samples_mapping_order` | Sample indices do not map to a consistent order across fragments. |
| `3d` | 3D multisampled-image rendering, access, or checksum validation returns incorrect data. |

## Important Variations and Special Cases

- The common 2D matrix covers extents `64x64` and `79x31`, layer counts `1` and `4`, four formats, and six sample counts. This yields 96 leaves each for `sampled_image` and `storage_image` per construction root.
- `standardsampleposition` uses a `1x1` image, two formats, and six sample counts. `samples_mapping_order` uses a `16x16` `VK_FORMAT_R8G8B8A8_UNORM` image with six sample counts. `3d` uses `64x64x8_1`, `VK_FORMAT_R8G8B8A8_UNORM`, and six sample counts.
- The default mustpass scope contains 216 leaves in each of `monolithic`, `fast-linked-library`, and shader-object-unlinked SPIR-V; it contains 210 leaves in each remaining listed construction file because those files omit `samples_mapping_order`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Common format and feature check | [`checkImageFormatRequirements()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L590-L608) | Checks image-format support and storage-image feature use. |
| Sampled-image validation | [`SampledImage::test()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1183-L1391) | Produces and validates sample-derived checksums. |
| Storage-image comparison | [`StorageImage::test()` and `compareImages()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2152-L2208) | Defines the two-path image comparison. |
| Standard-position validation | [`StandardSamplePosition::test()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2299-L2491) | Counts unexpected per-sample colors. |
| Sample-order validation | [`SamplesMappingOrder::test()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2552-L2723) | Compares every computed sample-order value with the first. |
| Registration matrix | [`addTestCasesWithFunctions()` through the factories](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2748-L2988) | Creates the registered leaves and five intermediate nodes. |

## Questions / Risk Points for User Audit

- Does the direct intermediate-node axis make the five distinct validation mechanisms clear?
- Does the brief distinguish a resolved host observation from shader-side per-sample inspection?
- Is the mustpass difference for `samples_mapping_order` clear enough?

## Conversion Notes for Final Wiki Rewrite

The final page should retain the compact multisample-image and storage-access prerequisites, the direct intermediate-node behavior axis, the resource flow, and the failure mapping table unchanged. It should describe generated shaders by role rather than embed a representative generated artifact because this source contains several distinct generated shader paths.
