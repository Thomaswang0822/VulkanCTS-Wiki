## Overview

**Core question:** Do Vulkan images produce valid sampled values when CTS varies their allocation, descriptor form, view type, format, dimensions, count, and graphics or compute execution path?

[`vktPipelineImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L60-L88) implements the `pipeline.image` test family. It registers the allocation families `suballocation` and `dedicated_allocation`, then generates the descriptor, view-type, format, count, size, and execution leaves beneath each one ([`createImageTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L891-L928)). The common runtime implementation lives in [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L455-L1023).

The inspected default mustpass files contain 122,912 `pipeline.monolithic.image` leaves and 61,456 `pipeline.shader_object_unlinked_spirv.image` leaves. The monolithic total is twice the shader-object total because every monolithic leaf also has a `pipeline_protected_flag` variant that sets `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT`; that extension does not apply to shader objects.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

A `VkImage` stores texels. A `VkImageView` gives a shader a typed view over selected mip levels and layers, and its view type determines how shader coordinates address that data ([Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#image-views)). The family samples images through either a combined image-sampler descriptor or a sampled-image descriptor paired with a separate sampler.

The test initializes a software texture, uploads it to each Vulkan image, samples it on the device, then evaluates the observed pixels against a host-side texture reference. Image allocation choice should affect resource placement, not the sampled values.

## Registration Hierarchy

```text
pipeline.monolithic.image
├── suballocation
└── dedicated_allocation
```

[`createImageTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L917-L928) registers both direct intermediate nodes below the `image` group. This family is added only for the monolithic and unlinked shader-object construction roots ([`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L118)); the hierarchy above uses the monolithic root as the canonical example.

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Source evidence |
|---|---|---|
| Allocation family | `suballocation`, `dedicated_allocation` | [`createImageTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L891-L928) |
| Descriptor form | `combined` for `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER`; `separate` for `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` | [`createImageSamplingTypeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L869-L889) |
| Image-view type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array` | [`createImageViewTypeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L836-L867) |
| Image format | `formats::pipelineImageFormats` for suballocation; `VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R16_SFLOAT` for dedicated allocation | [`createImageFormatTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L770-L833) |
| Image count | `1`, `4`, `8` for suballocation; `1` for dedicated allocation | [`createImageCountTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L744-L768) |
| Dimensions and layers | Per-view POT and NPOT dimensions; array sizes selected by view type and count | [`createImageSizeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L650-L709) |
| Execution | A graphics test case and a matching `_compute` test case | [`createImageSizeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L725-L736) |
| Pipeline creation flag | Ordinary leaves and `pipeline_protected_flag` leaves that use `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT`, where applicable | [`getImageSamplingInstanceParams()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L203-L214); [`createImageSizeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L711-L739) |

Compressed formats do not enter the 1D or 1D-array matrix. Outside Vulkan SC, the source adds ASTC 3D formats only to suballocated 3D views ([`createImageFormatTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L786-L830)).

## Behavior Parameters

The primary behavioral axis is the allocation family. The direct intermediate nodes change how the test obtains image memory while the remaining matrix exercises the sampled-image operation.

### suballocation — sampling images from a shared allocation

This intermediate node requests suballocated memory for the sampled images, result images, and vertex buffer across the full format and image-count matrix. It checks that the allocator's suballocation offsets and bindings do not alter sampled values.

### dedicated_allocation — sampling images from dedicated memory

This intermediate node requests dedicated memory for each sampled image, result image, and the vertex buffer. It restricts the format set to `VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R16_SFLOAT` and uses image count `1` ([`createImageFormatTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L770-L833); [`createImageCountTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L744-L768)).

Descriptor form, view type, format, count, geometry, and execution path change the sampled-image operation within both allocation families.

For image counts above one, the generated shaders index an image array. The support check therefore requires `DEVICE_CORE_FEATURE_SHADER_SAMPLED_IMAGE_ARRAY_DYNAMIC_INDEXING` ([`ImageTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L109-L135)). The same check gates ASTC 3D formats, `VK_KHR_maintenance5` formats, pipeline-construction support, and image-sampling-instance support. The `pipeline_protected_flag` leaves also require `VK_EXT_pipeline_protected_access` and the `pipelineProtectedAccess` feature, even though the flag they exercise is specifically `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT` ([`ImageTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L137-L149)).

## Shader Analysis

The shaders execute the sampling operation under test, but they do not define the expected result. The host reference comparison defines acceptance.

For graphics leaves, the vertex shader passes position and texture coordinates through to the fragment shader. The fragment shader samples a type-specific sampler or texture-plus-sampler and writes one color attachment per image ([`ImageTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L333-L382)). For counts above one, it loops over the descriptor array and writes `fragColors[i]`.

The compute variant reconstructs the graphics texture coordinates from the vertex buffer, samples the same descriptor form, and writes each result through `imageStore` ([`ImageTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L251-L331)). It provides a second execution path for the same sampling property.

### SPIR-V boundary

The source generates GLSL from each leaf's selected format, view type, descriptor form, count, and execution mode. It does not embed a fixed representative SPIR-V module in this family. A static assembly walkthrough would therefore describe a reconstructed leaf rather than a protected source artifact. This page links the generator and keeps the analysis at that boundary.

## Runtime Execution and Result Checking

1. The test builds `ImageSamplingInstanceParams`: it selects render size, a mosaic of vertices, an identity component mapping, the full mip and layer range, and a nearest, clamp-to-edge sampler ([`ImageTest::getImageSamplingInstanceParams()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L152-L215)).
2. `ImageSamplingInstance::setup()` creates each sampled image with `VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`, allocates and binds memory using the chosen allocation kind, uploads the software texture, and creates its image view. It also applies the same allocation kind to the result images and vertex buffer, then creates the shared sampler ([`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L501-L567); [`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L594-L646)).
3. The graphics path transitions output images, renders the quad mosaic, and draws. The compute path transitions output images to `VK_IMAGE_LAYOUT_GENERAL`, binds the compute pipeline and descriptor set, then dispatches one invocation per output pixel ([`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L944-L1021)).
4. `iterate()` calls setup, submits the recorded command buffer, waits for completion, and invokes `verifyImage()` ([`ImageSamplingInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1029-L1040)).
5. `verifyImage()` renders reference coordinates, derives LOD bounds and format-aware lookup precision, reads every output image, and validates each pixel against the software texture view. It logs result and error-mask images for failed comparisons ([`ImageSamplingInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1640-L1778)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior fails | Likely cause category | Evidence to inspect |
|---|---|---|
| One allocation family fails across otherwise identical leaves | Image memory allocation or binding | Image allocation, `bindImageMemory`, and upload path |
| One descriptor form fails | Descriptor layout, descriptor update, or sampler/image pairing | Descriptor setup and generated declarations |
| One view type or layer shape fails | Image view type, subresource range, coordinate mapping, or layer count | View creation and coordinate helpers |
| One format fails | Format feature support, format conversion, compressed data path, or result tolerance | Format filtering, texture upload, and lookup precision |
| Counts greater than one fail | Array indexing, descriptor array setup, or dynamic indexing support | Generated loop and `shaderSampledImageArrayDynamicIndexing` requirement |
| Only `_compute` or only graphics fails | Pipeline-specific resource transitions or shader path | Dispatch/draw setup and result-image readback |
| Protected leaves fail support | Missing `VK_EXT_pipeline_protected_access` or feature state | `pipelineProtectedFlag` support check |

### Cause Analysis

#### Allocation-specific mismatch

**Possible failure symptoms:** `suballocation` leaves fail while matching dedicated leaves pass, or the inverse pattern appears.

**Possible implementation causes:** Inspect memory requirements, allocator offsets, image and buffer bindings, and upload synchronization. The shared setup path applies `m_allocationKind` to the sampled images, result images, and vertex buffer, so an allocation-family pattern does not by itself isolate the sampled-image allocation ([`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L534-L549); [`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L594-L646)).

#### Descriptor or dynamic-array mismatch

**Possible failure symptoms:** `separate` leaves fail while `combined` leaves pass, or only count `4` and `8` leaves fail.

**Possible implementation causes:** Inspect descriptor bindings and generated GLSL declarations. Counts above one add a loop over sampled descriptors and require dynamic sampled-image array indexing ([`ImageTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L311-L328); [`ImageTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L109-L114)).

#### View, format, or coordinate mismatch

**Possible failure symptoms:** failures cluster around a view type, layer form, compressed format, or selected dimension.

**Possible implementation causes:** Inspect view creation, subresource range selection, texture-coordinate swizzles, layer counts, compressed-data upload, and the format-dependent reference tolerance. Source-level investigation must distinguish a device sampling defect from a test setup or reference-model defect.

#### Execution-path mismatch

**Possible failure symptoms:** a graphics leaf fails while its `_compute` counterpart passes, or the reverse occurs.

**Possible implementation causes:** Inspect graphics render-pass and attachment transitions separately from compute storage-image transitions, dispatch, and readback layout/access selection ([`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L944-L1021); [`ImageSamplingInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1750-L1765)).

## Case Pruning

The generator narrows combinations where the source has explicit constraints:

- dedicated allocation uses two formats and count `1`;
- 1D and 1D-array views exclude compressed formats;
- ASTC 3D formats apply only to suballocated 3D views outside Vulkan SC;
- `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT` leaves do not apply to shader-object construction;
- image counts above one require dynamic sampled-image array indexing.

These are source-defined matrix boundaries, not pass/fail expectations.

## Key Takeaways

- `pipeline.image` compares device sampling against a host-side texture reference across allocation and image-description combinations.
- `suballocation` and `dedicated_allocation` are intermediate nodes below one implementation-bearing test family.
- Graphics and compute leaves exercise the same sampled-data property through different output paths.
- Result logs include the observed image and an error mask when any pixel falls outside the configured lookup tolerance.

## Source Reference Appendix

- [`vktPipelineImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L60-L928): case parameters, support checks, shader generation, matrix generation, and registration.
- [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L455-L1023): image setup, resource creation, pipeline setup, and commands.
- [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1640-L1778): reference comparison and test status.
- [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt): default monolithic image leaves.
- [`shader-object-unlinked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt): default shader-object image leaves.
- [Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#image-views): Vulkan image-view semantics.
