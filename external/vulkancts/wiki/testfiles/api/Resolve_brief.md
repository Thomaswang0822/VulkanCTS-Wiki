# Understanding Brief: `resolve_image` test family

## One-Sentence Test Purpose

This test checks whether `vkCmdResolveImage` and `vkCmdResolveImage2` (via `VK_KHR_copy_commands2`) correctly average multisampled source texels into a single-sample destination, and whether multisampled-to-multisampled image copies performed before the resolve preserve per-sample data instead of silently resolving, shuffling, or duplicating samples.

## Background Knowledge

### Multisample resolve as a sample-averaging operation

`vkCmdResolveImage` reads a multisampled source image (samples > 1) and writes a single-sample destination image (samples == 1). For color formats, the Vulkan spec defines the resolved value of a destination texel as the average of the source texel's sample values. The region list is a set of `VkImageResolve` records, each with `srcSubresource`, `dstSubresource`, `srcOffset`, `dstOffset`, and `extent`. Source and destination images must share the same format, and the source must be multisampled while the destination must be `VK_SAMPLE_COUNT_1_BIT`. The resolve command is recorded into a command buffer and executes on a queue that supports transfer (which includes graphics and compute queues; transfer-only queues require the implementation to support resolve on transfer).

Why it matters here:

- The CTS host reference (`generateBuffer` with `FILL_MODE_MULTISAMPLE`) fills the source texture level with a per-pixel pattern that is identical across all samples within a pixel. Averaging identical samples reproduces the same value, so the host can compute the expected resolved image by copying the source pattern into the destination-shaped buffer via `copyRegionToTextureLevel`. A driver that picks one sample instead of averaging, or that drops samples, still passes for this fill pattern but is exposed by the intermediate-copy verification pass described below.
- `checkTestResult` compares the resolved destination against this reference with `tcu::fuzzyCompare` and a `0.01f` threshold, so small averaging-rounding differences are tolerated but missing-texel or wrong-region failures are not.

### Multisampled-to-multisampled image copy and the concurrent-access-bit rule

`vkCmdCopyImage` between two multisampled images is a separate operation from resolve: it copies each sample of the source to the corresponding sample of the destination, preserving the sample index. The Vulkan spec allows this when both images have the same sample count and compatible formats, and adds a concurrent-access rule: when the source and destination images overlap in memory (which can happen when a single multisampled image is both source and destination in chained operations), the implementation must serialize the per-sample copies such that no sample read is overwritten by an earlier region's write before that read happens. The test exercises the no-concurrent-access-bit path by using an intermediate image without `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` and inserting a pipeline barrier between two `vkCmdCopyImage` calls.

Why it matters here:

- For the `*_before_resolving` intermediate nodes, the test first copies the original multisampled image into a second multisampled image, then resolves that second image. The resolve output is compared to the same reference used for the direct resolve, because a correct MS→MS copy preserves per-sample data.
- The verification fragment shader in `checkIntermediateCopy` loads each sample of the source and the copy through input attachments and writes a `1` to a storage buffer when they match. A driver that shuffles samples, picks a single sample, or accidentally resolves during the copy will fail this check because at least one `(pixel, sample)` pair will mismatch.

### Queue family ownership transfer for compute/transfer-queue copies

When the multisampled-to-multisampled copy runs on a compute-only or transfer-only queue family, the source and copy images are created with `VK_SHARING_MODE_EXCLUSIVE`, so the test must release ownership from the universal queue family and acquire it on the target queue family before recording the copy. The release barrier sets `srcQueueFamilyIndex` to the universal family and `dstQueueFamilyIndex` to the target family; the acquire barrier swaps `srcAccessMask` to `0` and uses the same family indices. After the copy, ownership is released back to the universal queue family for the resolve, which is recorded on the universal queue.

Why it matters here:

- The `whole_copy_before_resolving_compute` and `whole_copy_before_resolving_transfer` nodes exercise this full release-acquire cycle. A driver that skips the ownership transfer or that performs the copy on the wrong queue will fail because the destination image's contents will be undefined on the universal queue when the resolve reads it.
- The test gate `checkSupport` throws `NotSupportedError` when no queue family exists that supports compute-only or transfer-only operations, so these nodes are skipped rather than failing on devices without dedicated compute/transfer queues.

## One Concrete Example

Take `dEQP-VK.api.copy_and_blit.core.resolve_image.whole_copy_before_resolving.4_bit` as a concrete case, reconstructed from `addResolveImageWholeCopyBeforeResolvingTests`:

```text
Source image:         VK_IMAGE_TYPE_2D, VK_FORMAT_R8G8B8A8_UNORM, 64x64, samples=4
Copy (intermediate):  VK_IMAGE_TYPE_2D, VK_FORMAT_R8G8B8A8_UNORM, 64x64, samples=4
Destination image:    VK_IMAGE_TYPE_2D, VK_FORMAT_R8G8B8A8_UNORM, 64x64, samples=1
Operation layout:     src=TRANSFER_SRC_OPTIMAL, dst=TRANSFER_DST_OPTIMAL
Resolve region:       srcOffset=(0,0,0), dstOffset=(0,0,0), extent=(64,64,1), layer 0, 1 layer
ResolveImageToImageOptions: COPY_MS_IMAGE_TO_MS_IMAGE
```

The host fills the source texture level with `FILL_MODE_MULTISAMPLE` (a per-pixel pattern of green, blue, and a diagonal teal mix that is identical across samples within a pixel), uploads it to the source image via a render pass clear and a colored-quad draw, runs `copyMSImageToMSImage(1)` to copy the source into the intermediate image, then records `vk.cmdResolveImage` from the intermediate image into the destination. After readback, `checkIntermediateCopy` runs first: it kicks off a render pass with the source and the intermediate bound as input attachments, executes the verification fragment shader that compares per-sample values, and reads the storage buffer back; any zero entry fails the test. If the intermediate check passes, `checkTestResult` fuzzy-compares the resolved destination against the host reference (a copy of the source pattern into a destination-sized buffer).

## End-to-End Test Flow

```text
[host] choose ResolveImageToImageOptions and registered subgroup
[host] checkSupport: framebufferColorSampleCounts, image format properties, fragmentStoresAndAtomics (when verifying intermediate copy), compute/transfer queue availability, COPY_COMMANDS_2 extension
[host] create multisampled source VkImage (samples = m_params.samples, COLOR_ATTACHMENT|TRANSFER_SRC|TRANSFER_DST|INPUT_ATTACHMENT usage)
[host] if option != NO_OPTIONAL_OPERATION: create multisampled intermediate copy image (and a second no-CAB image when option == COPY_MS_IMAGE_TO_MS_IMAGE_NO_CAB)
[host] create single-sample destination VkImage (TRANSFER_SRC|TRANSFER_DST usage; sparse flags when useSparseBinding)
[host] create render pass with one color attachment (samples = m_params.samples), pipeline, vertex buffer (upper-half triangle)
[host] fill destination TextureLevel via generateBuffer (default gradient)
[host] uploadImage destination into TRANSFER_DST_OPTIMAL
[host] fill source TextureLevel via generateBuffer with FILL_MODE_MULTISAMPLE
[host] generateExpectedResult by copying resolve regions into the destination-shaped expected level
[host] begin command buffer; barrier destination into TRANSFER_DST_OPTIMAL; clear source image to the multisample fill pattern through a render pass + colored-quad draw
[host] end render pass; pipeline barrier source -> operationLayout (and intermediate image barrier when option != NO_OPTIONAL_OPERATION)
[device] source image now holds the multisample fill pattern per sample
[host] if option is one of COPY_MS_IMAGE_TO_MS_IMAGE_*: copyMSImageToMSImage(copyArraySize)
  [host] if queueSelection != Universal: release ownership from universal queue, acquire on target queue
  [host] record vkCmdCopyImage (or vkCmdCopyImage2 with COPY_COMMANDS_2) from source to intermediate
  [host] if NO_CAB: extra vkCmdCopyImage from source to no-CAB image, barrier, then no-CAB image to intermediate
  [host] if queueSelection != Universal: release back to universal queue
[device] intermediate multisampled image now holds a per-sample copy of the source
[host] build VkImageResolve regions (or VkImageResolve2KHR with COPY_COMMANDS_2); for MULTIREGION each region extent is halved
[host] pipeline barrier source/intermediate -> operationLayout, destination -> operationLayout
[host] vkCmdResolveImage (or vkCmdResolveImage2) from intermediate (or source for NO_OPTIONAL_OPERATION) to destination
[host] pipeline barrier destination -> operationLayout with HOST_READ access
[host] submitCommandsAndWaitWithTransferSync (sparse semaphore when useSparseBinding)
[host] readImage destination into a TextureLevel
[host] if shouldVerifyIntermediateResults(option): checkIntermediateCopy()
  [host] build verification render pass with source + intermediate (or per-layer copies) as input attachments
  [host] record verification fragment shader draw over full-screen quad; per (pixel, sample) write 1 to storage buffer when source sample == intermediate sample
  [host] read back storage buffer; if any entry == 0 return fail
[host] checkTestResult: tcu::fuzzyCompare destination vs expected, threshold 0.01f, per-layer for arrays; COPY_MS_IMAGE_LAYER_TO_MS_IMAGE also checks unwritten layers are solid white
[host] report pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Two fixed GLSL shaders used by the source-image fill render pass: a vertex shader that passes `a_position` through to `gl_Position`, and a fragment shader that writes `vec4(0.0, 1.0, 0.0, 1.0)`. They are added under names `vert` and `frag` in `ResolveImageToImageTestCase::initPrograms` ([`vktApiResolveTests.cpp#L1659-L1673`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1659-L1673)).
- One generated verification fragment shader, added under the name `verify`, only generated for the intermediate-copy options (`COPY_MS_IMAGE_TO_MS_IMAGE`, `COPY_MS_IMAGE_TO_ARRAY_MS_IMAGE`, `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE`, `COPY_MS_IMAGE_TO_MS_IMAGE_MULTIREGION`, `COPY_MS_IMAGE_TO_MS_IMAGE_COMPUTE`, `COPY_MS_IMAGE_TO_MS_IMAGE_TRANSFER`). The shader reads `width`, `height`, and `samples` from push constants; declares `attachment0` as the source `subpassInputMS` and one additional `subpassInputMS` per destination layer (or a single `attachment1` for the layer-copy case); loops over every sample ID; loads `orig` from `attachment0` and `copyI` from `attachmentI`; writes `1` to `verificationFlags[(y*width + x)*samples + sampleID]` when all per-layer comparisons match, `0` otherwise. The pipeline is created with `VK_SAMPLE_COUNT_1_BIT` so a single fragment shader invocation per pixel iterates all samples in software ([`vktApiResolveTests.cpp#L1675-L1753`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1675-L1753)).
- The randomized test matrix is generated at registration time by the `addResolveImage*Tests` functions; each leaf enumerates the six sample counts (`VK_SAMPLE_COUNT_2_BIT`, `_4_BIT`, `_8_BIT`, `_16_BIT`, `_32_BIT`, `_64_BIT`) and optionally a `_bind_offset` variant that uses a non-zero memory bind offset equal to `VkMemoryRequirements::alignment`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `m_multisampledImage` | Yes | Yes (color attachment, transfer source, input attachment) | Cleared and drawn to in the fill render pass; read by `vkCmdCopyImage` and (for `NO_OPTIONAL_OPERATION`) by `vkCmdResolveImage`; read as input attachment by verification shader | No | Holds the per-sample source data. |
| `m_multisampledCopyImage` | Yes, when option != `NO_OPTIONAL_OPERATION` | Yes (color attachment, transfer source/destination, input attachment) | Written by `vkCmdCopyImage` from `m_multisampledImage`; read by `vkCmdResolveImage`; read as input attachment by verification shader | No | Holds the per-sample copy. Bugs in MS→MS copy surface here. |
| `m_multisampledCopyNoCabImage` | Yes, only for `COPY_MS_IMAGE_TO_MS_IMAGE_NO_CAB` | Yes (transfer source/destination, input attachment; no `COLOR_ATTACHMENT_BIT`) | Written by first `vkCmdCopyImage` from `m_multisampledImage`, read by second `vkCmdCopyImage` into `m_multisampledCopyImage` | No | Exercises the no-concurrent-access-bit path with a between-copies pipeline barrier. |
| `m_destination` | Yes (single-sample; sparse flags when `useSparseBinding`) | Yes (transfer source/destination) | Written by `vkCmdResolveImage` | Yes, via `readImage` | Holds the resolved output compared against the expected level. |
| Verification storage buffer | Yes, only when `shouldVerifyIntermediateResults(option)` is true | Yes (`VK_BUFFER_USAGE_STORAGE_BUFFER_BIT`, host-visible) | Written by verification fragment shader | Yes, via `invalidateAlloc` + `deMemcpy` | Holds one `int32_t` per `(pixel, sample)`; zero entries flag intermediate-copy mismatches. |
| Vertex buffer (upper-half triangle for fill; full-screen quad for verification) | Yes | Yes (`VK_BUFFER_USAGE_VERTEX_BUFFER_BIT`, host-visible) | Read by vertex shader | No | Drives the draw calls. |
| Push constants (`width`, `height`, `samples`) | Yes | Yes (push constant range in verification pipeline layout) | Read by verification fragment shader | No | Tells the verification shader the framebuffer dimensions and sample count. |

## What Is Checked

- `vkCmdResolveImage` / `vkCmdResolveImage2` output matches the host-computed expected level (the source's multisample fill pattern copied into the destination geometry) under `tcu::fuzzyCompare` with threshold `0.01f`. Comparison is per-layer for array destinations.
- For the `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE` option, every destination layer that was *not* the target of the layer copy must remain solid white `(1.0, 1.0, 1.0, 1.0)`; the copied layer must match the source's layer 2 against destination layer 4.
- For options where `shouldVerifyIntermediateResults` is true, the verification storage buffer must contain `1` at every `(pixel, sample)` index; any `0` fails the test before the resolve is compared.
- The check is done on the host for the resolved image and on the device (shader writes) plus host (buffer scan) for the intermediate copy.
- Each leaf case is checked independently; results are not aggregated.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node below `resolve_image` (the `ResolveImageToImageOptions` value chosen per subgroup, plus the resolve-region geometry for the direct-resolve nodes)
>
> **Candidate values:** `whole`, `partial`, `with_regions`, `diff_image_size`, `whole_copy_before_resolving`, `whole_copy_before_resolving_no_cab`, `whole_copy_before_resolving_compute`, `whole_copy_before_resolving_transfer`, `diff_layout_copy_before_resolving`, `layer_copy_before_resolving`, `copy_with_regions_before_resolving`, `whole_array_image`, `whole_array_image_one_region`

The candidate values cluster into three behavior groups:

1. Direct-resolve shape variants (`whole`, `partial`, `with_regions`, `diff_image_size`): vary the resolve region geometry without any intermediate MS→MS copy.
2. Resolve-after-MS-copy variants (`whole_copy_before_resolving`, `whole_copy_before_resolving_no_cab`, `whole_copy_before_resolving_compute`, `whole_copy_before_resolving_transfer`, `diff_layout_copy_before_resolving`, `layer_copy_before_resolving`, `copy_with_regions_before_resolving`): insert one or more `vkCmdCopyImage` calls between multisampled images before resolving, varying queue family, layout, concurrent-access bit, layer selection, and region count.
3. Array-image resolve variants (`whole_array_image`, `whole_array_image_one_region`): the destination is a 5-layer array image; `whole_array_image` emits one resolve region per layer, while `whole_array_image_one_region` emits a single region with `layerCount = 5` (and additional `VK_REMAINING_ARRAY_LAYERS` variants gated on `VK_KHR_maintenance5`).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `whole` | Resolve averaging wrong; whole-image region handling wrong; `vkCmdResolveImage2` diverges from `vkCmdResolveImage` (copy_commands2 variant); non-zero memory bind offset mishandled (`_bind_offset` leaf). |
| `partial` | Resolve region offset or extent handling wrong; out-of-region destination texels not preserved. |
| `with_regions` | Multiple resolve regions in one command batched incorrectly; per-region `srcOffset` / `dstOffset` / `extent` interpretation wrong. |
| `diff_image_size` | Resolve clamping or out-of-bounds handling wrong when source and destination extents differ; src-only or dst-only oversized image not supported. |
| `whole_copy_before_resolving` | MS→MS copy shuffled samples, picked a single sample, or accidentally resolved; resolve-then-compare reference no longer matches because the intermediate image diverged from the source. |
| `whole_copy_before_resolving_no_cab` | Concurrent-access rule violated: the no-CAB intermediate path requires a between-copies pipeline barrier; missing or mis-ordered barrier produces overwritten samples. |
| `whole_copy_before_resolving_compute` | Queue family ownership transfer (release/acquire) missing or wrong; compute-only queue recorded a command it does not support; image layout transition on the wrong queue. |
| `whole_copy_before_resolving_transfer` | Queue family ownership transfer missing or wrong; transfer-only queue recorded an unsupported command; layout transition on the wrong queue. |
| `diff_layout_copy_before_resolving` | Layout transition into or out of `GENERAL` / `TRANSFER_SRC_OPTIMAL` / `TRANSFER_DST_OPTIMAL` mishandled for the MS→MS copy or the resolve. |
| `layer_copy_before_resolving` | Per-layer `baseArrayLayer` / `layerCount` handling wrong in the MS→MS copy; unwritten destination layers not preserved as solid white. |
| `copy_with_regions_before_resolving` | Multiple MS→MS copy regions batched incorrectly; per-region `VkImageCopy` extent halved incorrectly; resolve region extents then mismatch the copy extents. |
| `whole_array_image` | Per-layer MS→MS copy loop wrong; destination array layer count handling wrong; input-attachment index mapping in verification shader wrong. |
| `whole_array_image_one_region` | `layerCount > 1` in a single resolve region mishandled; `VK_REMAINING_ARRAY_LAYERS` (maintenance5 variants) not honored; `baseArrayLayer != 0` not honored. |
| All values | Sample count not actually supported by the implementation but `checkSupport` did not catch it; format support gate (`getPhysicalDeviceImageFormatProperties`) skipped; `fragmentStoresAndAtomics` missing for intermediate-copy verification. |

## Important Variations and Special Cases

- **Sample-count matrix.** Every subgroup enumerates `VK_SAMPLE_COUNT_{2,4,8,16,32,64}_BIT`. The `checkSupport` gate reads `VkPhysicalDeviceLimits::framebufferColorSampleCounts` and throws `NotSupportedError` for unsupported counts, so a sample count that fails is a real averaging bug, not a feature gap.
- **Bind-offset leaves.** Most subgroups add a `_bind_offset` leaf when `allocationKind != ALLOCATION_KIND_DEDICATED`. The leaf sets `m_params.imageOffset = true`, which causes the source image memory to be bound at a non-zero offset equal to `VkMemoryRequirements::alignment`. This exercises alignment and offset handling in the driver's image memory binding path.
- **Variant roots.** The same `addResolveImageTests` is called from three sibling variant roots in `addCopiesAndBlittingTests`: `core` (suballocated, no extensions), `dedicated_allocation` (dedicated allocation, no extensions), and `copy_commands2` (dedicated allocation + `VK_KHR_copy_commands2`). The Level-3 page normalizes the registration hierarchy to the `core` variant root and notes that the implementation is identical across the three variants.
- **`VK_KHR_maintenance5` leaves.** `whole_array_image_one_region` adds three extra leaf families gated on `MAINTENANCE_5`: `_all_remaining_layers` and `_not_all_remaining_layers`, both using `VK_REMAINING_ARRAY_LAYERS` as the `layerCount` with `baseArrayLayer = 0` or `baseArrayLayer = 2`. These exercise the maintenance5 rule that `VK_REMAINING_ARRAY_LAYERS` resolves from `baseArrayLayer` to the end of the array.
- **Sparse-binding destination.** When `useSparseBinding` is set (only via the dispatcher's `sparse` variant root, which is not part of the canonical `core`/`dedicated_allocation`/`copy_commands2` set), the destination image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and bound through `allocateAndBindSparseImage` with a sparse semaphore. The resolve itself is unchanged; the sparse path only changes destination memory binding and submission synchronization.
- **Verification shader sample iteration.** The verification pipeline is created with `VK_SAMPLE_COUNT_1_BIT` and a loop over `sampleID` in the fragment shader. This deliberately avoids the `sampleRateShading` feature so the test can run on devices that do not expose it, at the cost of one fragment invocation per pixel iterating all samples in software.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `ResolveImageToImageOptions` enum | [`vktApiResolveTests.cpp#L35-L45`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L35-L45) | Defines the optional-operation values that select the MS→MS copy path. |
| `ResolveImageToImage` constructor (resource creation) | [`vktApiResolveTests.cpp#L86-L575`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L86-L575) | Creates source, intermediate, no-CAB, and destination images; sparse path; fill render pass; pipeline; vertex buffer. |
| `iterate()` (resolve recording) | [`vktApiResolveTests.cpp#L577-L769`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L577-L769) | Builds `VkImageResolve` regions, records pipeline barriers, calls `vkCmdResolveImage` or `vkCmdResolveImage2`. |
| `checkTestResult()` | [`vktApiResolveTests.cpp#L771-L812`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L771-L812) | Host-side `tcu::fuzzyCompare` with `0.01f` threshold; layer-copy white-color check. |
| `checkIntermediateCopy()` | [`vktApiResolveTests.cpp#L838-L1163`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L838-L1163) | Verification render pass + fragment shader + storage buffer scan. |
| `copyMSImageToMSImage()` | [`vktApiResolveTests.cpp#L1165-L1590`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1165-L1590) | MS→MS copy with queue ownership transfer, NO_CAB two-step copy, and multiregion extent halving. |
| `ResolveImageToImageTestCase::checkSupport` | [`vktApiResolveTests.cpp#L1610-L1652`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1610-L1652) | Sample-count, format, extension, queue-family, and `fragmentStoresAndAtomics` gates. |
| `initPrograms` (vert/frag/verify) | [`vktApiResolveTests.cpp#L1659-L1754`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1659-L1754) | Generates the verification fragment shader source string. |
| `samples[]` and `resolveExtent` | [`vktApiResolveTests.cpp#L1756-L1758`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1756-L1758) | The six sample counts and the 256×256 default resolve extent. |
| `addResolveImageTests` (root registration) | [`vktApiResolveTests.cpp#L2588-L2608`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2588-L2608) | Adds the 13 intermediate nodes (with `whole_copy_before_resolving_compute` and `_transfer` routed through `addComputeAndTransferQueueTests`). |
| `addResolveImageWholeCopyDiffLayoutsBeforeResolvingTests` | [`vktApiResolveTests.cpp#L2079-L2147`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2079-L2147) | Layout matrix `general × transfer_src_optimal × transfer_dst_optimal` with `transfer_dst_optimal`-as-src and `transfer_src_optimal`-as-dst skipped. |
| `addResolveImageWholeArrayImageSingleRegionTests` | [`vktApiResolveTests.cpp#L2346-L2507`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2346-L2507) | `layerCount = 5` single-region cases plus the maintenance5 `VK_REMAINING_ARRAY_LAYERS` leaves. |
| `addResolveImageDiffImageSizeTests` | [`vktApiResolveTests.cpp#L2509-L2584`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2509-L2584) | Src-only and dst-only oversized image extents. |
| Parent dispatcher | [`vktApiCopiesAndBlittingTests.cpp#L119-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) | Routes `resolve_image` under the `core`, `dedicated_allocation`, and `copy_commands2` variant roots. |
| `generateBuffer` / `FILL_MODE_MULTISAMPLE` | [`vktApiCopiesAndBlittingUtil.cpp#L1108-L1272`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1108-L1272) | Host reference fill pattern: green / blue / diagonal teal mix, identical across samples within a pixel. |
| `generateExpectedResult` | [`vktApiCopiesAndBlittingUtil.cpp#L1487-L1498`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1487-L1498) | Copies resolve regions into the destination-shaped expected level. |
| `defaultExtent` and constants | [`vktApiCopiesAndBlittingUtil.hpp#L160-L181`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L160-L181) | 64×64 default extent used by the `*_before_resolving` and `whole_array_image*` subgroups. |

## Questions / Risk Points for User Audit

- Is the three-cluster grouping of the 13 intermediate nodes (direct-resolve shape, resolve-after-MS-copy, array-image resolve) the right primary behavioral axis, or should the page split them into separate behavior parameter groups?
- The mustpass path uses `dEQP-VK.api.copy_and_blit.<variant>.resolve_image.<subgroup>.<leaf>`. The page normalizes the registration tree to `copy_and_blit.core.resolve_image` and mentions the `dedicated_allocation` and `copy_commands2` variant roots in prose. Is this normalization acceptable, or should the tree show all three variant roots?
- The verification shader is generated only for the six intermediate-copy options. Should the page treat `COPY_MS_IMAGE_TO_MS_IMAGE_NO_CAB` as a distinct behavior parameter value even though it shares the same shader, or fold it under the `whole_copy_before_resolving_no_cab` leaf description?
- The `whole_array_image_one_region` maintenance5 leaves (`_all_remaining_layers`, `_not_all_remaining_layers`) are registered only when `extensionFlags | MAINTENANCE_5` is enabled. Should the page note these as a separate variation or fold them into the `whole_array_image_one_region` description?
- The sparse-binding path is reachable only via the `sparse` variant root, which is not part of the canonical three variant roots (`core`, `dedicated_allocation`, `copy_commands2`). The page mentions it as a special case. Is this the right scope boundary?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge section into a brief unordered list of necessary prerequisites: multisample resolve as sample averaging, MS→MS copy as per-sample preservation, and queue family ownership transfer for compute/transfer queues. Drop the teaching scaffolding about "why it matters here" — those points belong in the page body.
- Use the concrete example only as a brief reference, not as a full walkthrough. The page does not include shader walkthroughs (Phase 5 is skipped).
- Carry the `### Failure Cause Mapping` table directly into the final page's `## Failure Meaning` → `### Failure Cause Mapping`. Write `### Cause Analysis` fresh, grouping the 13 causes into the three behavior clusters plus the shared infrastructure cause.
- Carry the `## Behavior Parameter Identification` conclusion (the 13 intermediate nodes grouped into three clusters) into `## Behavior Parameters`, with `### <subgroup> — <very brief description>` subsections for each cluster.
- Move the source-mapping table to the Source Reference Appendix as the page's source-link inventory.
- The risk points above are resolved by inspected source, registration, mustpass, and validation evidence; no user-blocking questions remain. Continue directly to the rewrite in the same task.
