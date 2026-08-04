# Understanding Brief: pipeline image sampling

## One-Sentence Test Purpose

This test checks whether Vulkan image views, sampled images, samplers, and image memory allocations produce the expected sampled values across view types, formats, dimensions, image counts, and graphics or compute execution.

## Background Knowledge

### Image views and sampled images

A `VkImage` stores texels, while a `VkImageView` selects the view type, format interpretation, mip levels, and array layers used by a shader. The test creates sampled images and views for 1D, array, 2D, 3D, cube, and cube-array access. The Vulkan image-view rules define how those selections map to shader-visible coordinates ([Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#image-views)).

### Sampling and allocation

A sampled-image descriptor supplies an image to a shader. A combined image sampler supplies the image and sampler together; a separate `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` case binds a sampler independently. The test also changes whether each image uses suballocated memory or a dedicated allocation. These choices should not change the sampled result.

## One Concrete Example

A representative suballocated leaf uses a 2D view, a format from `formats::pipelineImageFormats`, one image, and a selected size. The host creates the image with sampled and transfer-destination usage, allocates and binds memory, uploads the test texture, creates the view and sampler, and binds the descriptor. The graphics shader passes interpolated texture coordinates to `texture()`. The compute shader reconstructs the same coordinates and writes sampled values to a storage image.

## End-to-End Test Flow

```text
[host] select allocation kind, descriptor form, view type, format, image count, size, array size, and pipeline path
[host] create images, allocate and bind memory, upload texture data, and create views and samplers
[host] generate GLSL for graphics or compute execution and build the selected pipeline
[host] submit commands and wait for completion
[device] sample the test image and write each result to a color attachment or storage image
[host] render reference coordinates, read result images, and compare each pixel with format-aware tolerances
[host] report pass when every image matches, otherwise report Image mismatch
```

## Behavior Parameter Identification

The primary behavioral axis is the registered allocation family, `suballocation` versus `dedicated_allocation`, combined with the sampling matrix below. The image count, view type, format, dimensions, and graphics/compute path change the image-sampling operation. The `pipeline_protected_flag` is an additional support and pipeline-access variant.

## Parameter and Behavior Matrix

| Axis | Observed values | Evidence |
|---|---|---|
| Allocation family | `suballocation`, `dedicated_allocation` | `createImageTests()` and allocation selection |
| Descriptor form | `combined`, `separate` | `createImageSamplingTypeTests()` |
| View type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array` | `createImageViewTypeTests()` |
| Image count | `1`, `4`, `8` for suballocation; `1` for dedicated allocation | `createImageCountTests()` |
| Format | `formats::pipelineImageFormats`; dedicated allocation restricts to `VK_FORMAT_R8G8B8A8_UNORM` and `VK_FORMAT_R16_SFLOAT` | `createImageFormatTests()` |
| Size and layers | POT and NPOT dimensions; array sizes depend on view type and image count | `createImageSizeTests()` |
| Execution | graphics leaf and matching `_compute` leaf | `createImageSizeTests()` |

## What Failure Means

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

## Audit Questions and Unresolved Risks

- Confirm the final mustpass count against the exact image-family predicate in each inspected pipeline file. The current inspected default files contain 122,912 monolithic leaves and 61,456 `shader-object-unlinked-spirv` leaves containing `.image.`.
- Keep compressed-format exclusions for 1D and 1D-array views, and the extra non-VulkanSC ASTC 3D cases, visible in the final page.
- Treat the shader as a mechanism for sampling and result production. The host-side reference comparison, not shader arithmetic, determines correctness.
