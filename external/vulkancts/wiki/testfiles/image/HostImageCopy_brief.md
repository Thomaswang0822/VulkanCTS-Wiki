# Understanding Brief: `image.host_image_copy`

## One-Sentence Test Purpose

This family verifies that `VK_EXT_host_image_copy` can transition eligible image layouts and move correctly addressed image data between host memory and images, including image-to-image copies, while retaining the result through subsequent graphics or compute use where applicable.

## Background Knowledge

### Host image copy operations

`VK_EXT_host_image_copy` supplies host-side image layout transitions and copy entry points. The tested operations are `vkTransitionImageLayoutEXT`, `vkCopyMemoryToImageEXT`, `vkCopyImageToMemoryEXT`, and `vkCopyImageToImageEXT`. Their regions identify an image subresource, offset, extent, and, where applicable, a host pointer plus optional host row length and image height. Unlike command-buffer transfer commands, the host copy calls execute directly from the host.

Why it matters here:

- The family compares host-copy paths with ordinary queue-submitted transfers or with a later rendering/compute observation.
- The `memcpy` leaves set `VK_HOST_IMAGE_COPY_MEMCPY_EXT`; other host-copy leaves use zero flags.

### Eligible layouts and host-transfer image use

The extension properties return separate allowed source and destination layout lists. Images used as host-copy destinations or sources need the selected layout to appear in the applicable list, and host-transfer images use `VK_IMAGE_USAGE_HOST_TRANSFER_BIT_EXT`. Format support is also tiling-specific through `VK_FORMAT_FEATURE_2_HOST_IMAGE_TRANSFER_BIT_EXT`.

Why it matters here:

- Each operational case checks the feature bit, selected layouts, image-format support, and host-image-copy feature before running.
- The properties leaves independently check the returned layout lists and optimal-tiling UUID rather than performing a copy.

### Image aspects, formats, and comparison rules

A color image can commonly be checked as raw bytes, but depth/stencil images require aspect-specific copies and value-specific comparison. Compressed sampled inputs are observed after sampling instead of being treated as ordinary uncompressed texels. The source also masks unused precision bits for several packed formats before comparison.

Why it matters here:

- The primary draw/dispatch matrix confirms data by sampling the copied image and observing an output image.
- `depth_stencil` uses separate depth/stencil data paths, performs rendering that exercises both aspects, and checks color, depth, and stencil results.

## One Concrete Example

A leaf under `dEQP-VK.image.host_image_copy.draw_r8g8b8a8_unorm_r8g8b8a8_unorm.host_transition_host_copy.memory_to_image.general_general.general.optimal.0_1_0.16x16` chooses a graphics observation path, host layout transition, and host memory-to-image copy. The test creates a sampled RGBA8 image and an RGBA8 color output image, generates source bytes, transitions the sampled image from `UNDEFINED` to the host-copy destination layout, and calls `vkCopyMemoryToImageEXT`. It then records a fullscreen draw that samples the copied image into the output attachment, copies that attachment to host-visible memory, and compares the output with the expected sampled data. The selected leaf also has a configuration-specific dynamic-rendering choice and may select sparse storage according to the registration alternation.

## End-to-End Test Flow

```text
[host] choose a registered family, format/tiling/layout configuration, and supported image properties
[host] create images, allocations, views, host data, and (for the main matrix) graphics or compute programs
[host or queue] transition the sampled image from UNDEFINED to the selected copy layout
[host or queue] perform memory-to-image, image-to-memory, or image-to-image transfer
[queue] sample the copied image in a fullscreen draw or compute dispatch when the main matrix uses an observer
[queue] copy the observer output to host-visible memory and wait for completion
[host] compare bytes/pixels or, for query leaves, validate the returned property relationship
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`HostImageCopyTestCase::initPrograms()` generates three GLSL programs for the main matrix:

- a fullscreen vertex shader that produces texture coordinates;
- a fragment shader that samples `combinedSampler` into a color attachment; and
- a local-size-one compute shader that samples the same input and stores each result to an output image.

The query, properties, identical-memory-layout, array, preinitialized, and simple round-trip paths do not depend on these generated programs. `DepthStencilHostImageCopyTest` instead generates a small graphics pair that renders against the depth/stencil attachment.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|---------------|----------------|
| Source byte vector or host allocation | Yes | Directly referenced by host-copy calls; some paths also use a buffer | Read by host-copy or transfer operation | Yes, as reference | Supplies deterministic input for copies. |
| Host-transfer sampled/source image | Yes | Yes | Written/read by host copy and sampled by graphics/compute in the main matrix | Indirectly through output or direct copyback | Is the image whose host-copy behavior is being tested. |
| Optional second image | Yes | Yes | Receives `vkCopyImageToImageEXT` output | Indirectly/directly | Exercises host image-to-image copies and memcpy flag behavior. |
| Output image and copyback buffer | Yes | Yes | Written by draw/dispatch and transfer copyback | Yes | Produces the observable sampled result. |
| Image views, sampler, descriptors, pipeline | Yes | Yes | Read by the graphics/compute observer | No | Makes the copied sampled image observable through normal device use. |
| Depth/stencil image and color buffer | Yes | Yes | Host-copied, used as an attachment, then read back | Yes | Provides aspect-specific validation. |

## What Is Checked

- Main draw/dispatch leaves generate non-NaN input data, exercise the chosen host-copy or comparison transfer route, sample the result, and fail if the copied/sampled output differs from the expected value ([main execution and checks](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L391-L1201)).
- `array` uploads a selected layer range to one image, copies it to another image with potentially different layer offsets, copies the target range to host memory, and compares the bytes ([array execution](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3246-L3434)).
- The tiling/image-to-image/preinitialized leaves compare output bytes with the initially generated allocation data after the selected transition/copy route ([preinitialized execution](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1488-L1739)).
- `properties` checks nonempty source/destination layout lists, required `GENERAL` entries, a nonzero optimal-tiling UUID, and extra interchangeable-layout requirements when unified image layouts apply ([properties checks](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1924-L2065)).
- `query` checks consistency requirements for `VkHostImageCopyDevicePerformanceQueryEXT`, compressed-format optimal-device-access behavior, and the host-image-transfer feature when sampled support is advertised ([query checks](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2105-L2180)).
- `identical_memory_layout` creates otherwise comparable images with and without host-transfer use, copies their bound memory to verification buffers, and compares every byte ([memory-layout execution](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2414-L2584)).

## Behavior Parameter Identification

> **Behavior parameter:** registered direct test family
>
> **Candidate values:** generated draw/dispatch matrix, `large_images`, `array`, tiling/image-to-image/preinitialized paths, `capture_replay`, `properties`, `query`, `identical_memory_layout`, `depth_stencil`, `simple`

This is the primary behavioral axis because it changes the assertion being made. The main matrix combines host operations with a sampled graphics/compute observation; `array`, preinitialized, and simple leaves directly round-trip or relocate data; `properties` and `query` validate extension reporting; `identical_memory_layout` validates allocation-layout equivalence; and `depth_stencil` adds attachment-aspect semantics. Formats, layouts, tiling, extents, offsets, and copy flags expand coverage within those behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Main draw/dispatch matrix | Host transition, selected host copy direction or memcpy flag, image layout eligibility, region/mip addressing, or visibility of the copied data to the graphics/compute observer. |
| `large_images` | The main matrix’s host-copy path fails at a larger optimal-tiled extent, or allocation/region handling does not scale to the registered size. |
| `array` | Source/destination layer offsets, `VK_REMAINING_ARRAY_LAYERS`, cube-compatible constraints, or layer-range host copy is handled incorrectly. |
| Tiling/image-to-image/preinitialized paths | A selected source/destination layout, DRM modifier path, host image-to-image operation, image-memory offset, or copied data comparison is incorrect. |
| `capture_replay` | Descriptor-heap capture/replay image allocation or its host image-to-image copy route is not supported correctly. |
| `properties` / `query` | The implementation reports host-image-copy layouts, UUIDs, feature bits, or performance-query fields inconsistently with required relationships. |
| `identical_memory_layout` | Images that differ by host-transfer use do not meet the advertised identical-memory-layout behavior. |
| `depth_stencil` / `simple` | Aspect selection, depth/stencil packing, special packed-format comparison, image-to-image host copy, or a basic host-memory round trip is incorrect. |

## Important Variations and Special Cases

- **Main matrix.** The generated groups vary draw versus dispatch, host transition versus barrier transition, host-copy action, source/destination/intermediate layouts, linear or optimal tiling, mip level, region count, padding, and three 2D sizes. Format combinations include ordinary color, depth, compressed, and selected packed paths ([matrix registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L4595)).
- **Alternated environment coverage.** Main-matrix registration alternates dynamic rendering and sparse-image choices. Compressed sampled formats exclude sparse variants, and later-added formats keep only selected interesting combinations ([pruning and alternation](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4480-L4569)).
- **Array coverage.** Array cases vary five formats, linear/optimal tiling, layer ranges and nonzero source/destination layer offsets, region offsets/extents, `VK_REMAINING_ARRAY_LAYERS`, and legal cube-compatible configurations ([array registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4665-L4764)).
- **Layout coverage.** Linear, optimal, and DRM-modifier paths combine three operation styles with a curated set of source/destination layout pairs, four image shapes, two image-memory offsets, and six formats. The generator keeps every equal-layout pair and all pairs involving a common transfer/general layout ([layout registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4767-L4889)).
- **Feature and extension gates.** Every operational case requires `VK_EXT_host_image_copy` and its `hostImageCopy` feature. Individual paths additionally require dynamic rendering, sparse binding, DRM format modifiers, swapchain, maintenance/synchronization/depth-stencil layout extensions, descriptor heap, format features, and selected supported layouts as applicable ([main support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1224-L1345), [preinitialized support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1783-L1910)).
- **Vulkan SC availability.** The implementation is registered under `image.host_image_copy` only in non-VulkanSC builds by the parent image dispatcher ([parent registration guard](../../../modules/vulkan/image/vktImageTests.cpp#L49-L51), [child creation](../../../modules/vulkan/image/vktImageTests.cpp#L92-L94)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Format feature helper and main parameters | [helpers and parameter model](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L118-L297) | Defines input generation, host-transfer format gate, and main-matrix parameters. |
| Main matrix runtime | [`HostImageCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L391-L1201) | Creates copy/observer resources, executes routes, and verifies data. |
| Main support and generated programs | [`HostImageCopyTestCase`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1204-L1407) | Defines feature/layout checks and generated vertex, fragment, and compute shaders. |
| Preinitialized/image-to-image runtime | [`PreinitializedTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1488-L1739) | Covers image-to-image, memcpy, allocation offsets, and copyback verification. |
| Properties and query cases | [`PropertiesTestInstance` and `QueryTestInstance`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1913-L2180) | Validates extension properties and performance-query relationships. |
| Identical-memory-layout runtime | [`IdenticalMemoryLayoutTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2222-L2584) | Compares memory layouts with and without host-transfer image usage. |
| Depth/stencil and array runtimes | [depth/stencil](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2659-L3210) and [array](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3231-L3434) | Defines aspect-aware and layered-copy validation. |
| Simple round-trip and its gate | [`SimpleHostImageCopyTestInstance` and case](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3527-L4350) | Defines broad nonplanar-format round trips and special comparisons. |
| Registration | [`testGenerator()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L5013) | Defines every direct family, hierarchy, matrix, and pruning rule. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L49-L100) | Shows the non-VulkanSC registration condition and image-category placement. |

## Questions / Risk Points for User Audit

- The displayed direct-family list treats `linear`, `optimal`, and `drm_format_modifier` as three top-level tiling paths. Their leaves include `image_to_image_copy`, `image_to_image_memcpy`, and `preinitialized`; the last is an operation-style node, not a standalone top-level group.
- In the main matrix, “host transition” and “host copy” are independently selected. The `host_transition` name does not mean every transfer in that leaf is a host copy; its registration explicitly selects a queue copy for that combination.
- `identical_memory_layout` verifies allocation-byte equality for paired images. It is not a general assertion that arbitrary images share an internal layout.
- A successful `properties` or `query` leaf validates required relationships in returned structures; it does not itself prove that every host-copy operation succeeds on every format/layout combination.

## Conversion Notes for Final Wiki Rewrite

- Keep direct test family as the primary behavior parameter and retain the failure-cause table.
- Make the distinction between host calls, queue transfer commands used for comparison/readback, and shader observation explicit.
- Describe the large main matrix as a matrix rather than enumerating every leaf; retain the key axes and pruning rules.
- Keep the preinitialized, property/query, identical-memory-layout, depth/stencil, array, and simple paths visible because their validation mechanisms are materially different from the main matrix.
