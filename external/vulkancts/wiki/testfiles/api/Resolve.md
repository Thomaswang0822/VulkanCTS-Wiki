## Overview

**Core question:** does the implementation average multisampled source texels into a single-sample destination through `vkCmdResolveImage` and `vkCmdResolveImage2`, and does an intermediate multisampled-to-multisampled image copy preserve per-sample data instead of silently resolving, shuffling, or duplicating samples?

- Covers the `resolve_image` test family under the `copy_and_blit` test category, implemented in [`vktApiResolveTests.cpp`](../../../modules/vulkan/api/vktApiResolveTests.cpp) and dispatched from [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp).
- Implements 13 intermediate nodes under `resolve_image`: four direct-resolve shape variants, seven resolve-after-multisampled-copy variants, and two array-image resolve variants.
- Tests both `vkCmdResolveImage` (no extension) and `vkCmdResolveImage2` (via `VK_KHR_copy_commands2`).
- Enumerates six sample counts (`VK_SAMPLE_COUNT_{2,4,8,16,32,64}_BIT`) per subgroup and adds `_bind_offset` leaves that bind source image memory at a non-zero offset.
- Verifies the resolved destination against a host-computed reference with `tcu::fuzzyCompare` (threshold `0.01f`), and verifies the intermediate multisampled copy with a generated fragment shader that compares per-sample input-attachment reads.

## Background Knowledge

- **Multisample resolve as sample averaging.** `vkCmdResolveImage` reads a multisampled source image (samples > 1) and writes a single-sample destination image (`VK_SAMPLE_COUNT_1_BIT`). For color formats, the Vulkan spec defines the resolved texel value as the average of the source texel's sample values. Source and destination must share the same format.
- **Multisampled-to-multisampled image copy.** `vkCmdCopyImage` between two multisampled images copies each sample of the source to the corresponding sample of the destination, preserving the sample index. When source and destination overlap, the implementation must serialize per-sample reads and writes (the concurrent-access rule). The no-concurrent-access-bit path inserts a pipeline barrier between two `vkCmdCopyImage` calls to enforce serialization explicitly.
- **Queue family ownership transfer.** When a multisampled-to-multisampled copy runs on a compute-only or transfer-only queue, `VK_SHARING_MODE_EXCLUSIVE` images must be released by the universal queue family and acquired by the target queue family before the copy, then released back to the universal queue family before the resolve is recorded on the universal queue.

## Registration Hierarchy

```text
api.copy_and_blit.core.resolve_image
├── whole
├── partial
├── with_regions
├── whole_copy_before_resolving
├── whole_copy_before_resolving_no_cab
├── whole_copy_before_resolving_compute
├── whole_copy_before_resolving_transfer
├── diff_layout_copy_before_resolving
├── layer_copy_before_resolving
├── copy_with_regions_before_resolving
├── whole_array_image
├── whole_array_image_one_region
└── diff_image_size
```

The same `addResolveImageTests` implementation is also registered under the `api.copy_and_blit.dedicated_allocation.resolve_image` and `api.copy_and_blit.copy_commands2.resolve_image` variant roots through [`addCopiesAndBlittingTests`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230). The `core` root is shown above as the canonical registration tree; the implementation is identical across the three variants and differs only in `allocationKind` (`ALLOCATION_KIND_SUBALLOCATED` versus `ALLOCATION_KIND_DEDICATED`) and `extensionFlags` (`0` versus `COPY_COMMANDS_2`). The `compute` and `transfer` queue-specific children are registered as direct children `whole_copy_before_resolving_compute` and `whole_copy_before_resolving_transfer` by [`addComputeAndTransferQueueTests`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1965-L2022), rather than as a literal `compute_and_transfer_queue` path component.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Sample count | `VK_SAMPLE_COUNT_2_BIT`, `_4_BIT`, `_8_BIT`, `_16_BIT`, `_32_BIT`, `_64_BIT` | The number of samples per source texel that the resolve must average. Enumerated by every subgroup. | [`vktApiResolveTests.cpp#L1756-L1757`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1756-L1757) |
| Resolve region shape | whole, partial (offset 64,64 extent 128,128), multi-region (four 64×64 regions), `diff_image_size` extents | Varies the geometry of `VkImageResolve` regions recorded into `vkCmdResolveImage`. | [`vktApiResolveTests.cpp#L1760-L1909`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1760-L1909), [`vktApiResolveTests.cpp#L2509-L2584`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2509-L2584) |
| Optional operation | `NO_OPTIONAL_OPERATION`, `COPY_MS_IMAGE_TO_MS_IMAGE`, `COPY_MS_IMAGE_TO_MS_IMAGE_NO_CAB`, `COPY_MS_IMAGE_TO_MS_IMAGE_COMPUTE`, `COPY_MS_IMAGE_TO_MS_IMAGE_TRANSFER`, `COPY_MS_IMAGE_TO_ARRAY_MS_IMAGE`, `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE`, `COPY_MS_IMAGE_TO_MS_IMAGE_MULTIREGION` | Selects whether an intermediate multisampled-to-multisampled copy runs before the resolve, and which queue, layout, and region pattern that copy uses. | [`vktApiResolveTests.cpp#L35-L45`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L35-L45) |
| `extensionFlags` | `0`, `COPY_COMMANDS_2` | Selects `vkCmdResolveImage` versus `vkCmdResolveImage2` (and `vkCmdCopyImage` versus `vkCmdCopyImage2` for the intermediate copy). | [`vktApiResolveTests.cpp#L730-L749`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L730-L749) |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Selects suballocated versus dedicated image memory allocation. | [`vktApiResolveTests.cpp#L1773`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1773) |
| Memory bind offset | `imageOffset = false`, `imageOffset = true` (`_bind_offset` leaf) | When true, the source image is bound at a non-zero offset equal to `VkMemoryRequirements::alignment`. Skipped for `ALLOCATION_KIND_DEDICATED`. | [`vktApiResolveTests.cpp#L146-L150`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L146-L150), [`vktApiResolveTests.cpp#L1796-L1808`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1796-L1808) |
| Queue selection | `Universal`, `ComputeOnly`, `TransferOnly` | Selects the queue family for the intermediate multisampled copy. Compute/transfer variants trigger queue family ownership transfer. | [`vktApiResolveTests.cpp#L1965-L2022`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1965-L2022) |
| Image layout (source/destination) | `VK_IMAGE_LAYOUT_GENERAL`, `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` | The `diff_layout_copy_before_resolving` subgroup iterates the layout matrix, skipping `TRANSFER_DST_OPTIMAL`-as-source and `TRANSFER_SRC_OPTIMAL`-as-destination. | [`vktApiResolveTests.cpp#L2117-L2147`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2117-L2147) |
| Array layers | 1 (single), 5 (array), `VK_REMAINING_ARRAY_LAYERS` (maintenance5) | `whole_array_image` and `whole_array_image_one_region` use a 5-layer destination. The maintenance5 leaves use `VK_REMAINING_ARRAY_LAYERS` with `baseArrayLayer = 0` or `2`. | [`vktApiResolveTests.cpp#L2289-L2507`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2289-L2507) |
| Image size | 256×256×1 (`resolveExtent`), 64×64×1 (`defaultExtent`), 5-deep (`defaultExtent` with `depth = 5`), oversized variants `(266,256,1)`, `(256,512,1)`, `(256,256,11)` | Varies source and destination extents. `diff_image_size` makes only one of src or dst oversized. | [`vktApiResolveTests.cpp#L1758`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1758), [`vktApiResolveTests.cpp#L2544-L2583`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2544-L2583) |

## Behavior Parameters

The primary behavioral axis is the intermediate node below `resolve_image`. The 13 intermediate nodes cluster into three behavior groups, each exercising a distinct mechanism.

### Direct-resolve shape variants

These nodes record `vkCmdResolveImage` directly from the source image into the destination, with no intermediate multisampled copy. They vary the resolve region geometry.

#### `whole` — whole-image resolve

Records a single `VkImageResolve` with `srcOffset = (0,0,0)`, `dstOffset = (0,0,0)`, and `extent = (256,256,1)`. Source and destination are both `VK_FORMAT_R8G8B8A8_UNORM` at the `resolveExtent` (256×256). Enumerates all six sample counts and adds a `_bind_offset` leaf for each (when not dedicated allocation). This is the simplest averaging check.

#### `partial` — partial-image resolve with destination offset

Records a single region with `dstOffset = (64,64,0)` and `extent = (128,128,1)`. Out-of-region destination texels must be preserved from the initial `generateBuffer` fill, exposing drivers that overwrite outside the requested region.

#### `with_regions` — multiple resolve regions in one command

Records four regions with `srcOffset = (i,i,0)`, `dstOffset = (i,0,0)`, and `extent = (64,64,1)` for `i ∈ {0,64,128,192}`. Exercises batching of multiple `VkImageResolve` records in a single `vkCmdResolveImage` call.

#### `diff_image_size` — resolve between differently sized images

Records a single region with `extent = resolveExtent` but makes either the source or the destination oversized: `(266,256,1)`, `(256,512,1)`, or `(256,256,11)`. Source-only oversized cases (`src_*`) and destination-only oversized cases (`dst_*`) are registered as separate leaves. The `_bind_offset` leaf is added only for the destination-oversized cases.

### Resolve-after-multisampled-copy variants

These nodes call `copyMSImageToMSImage` to copy the source into an intermediate multisampled image before resolving from that intermediate. They exercise the per-sample preservation rule through `checkIntermediateCopy`.

#### `whole_copy_before_resolving` — full multisampled copy before resolve

Copies the full source image into `m_multisampledCopyImage` layer-by-layer using `vkCmdCopyImage` with one region per layer, then resolves from the intermediate. Uses `COPY_MS_IMAGE_TO_MS_IMAGE`. Source and destination are at `defaultExtent` (64×64).

#### `whole_copy_before_resolving_no_cab` — copy without concurrent access bit

Creates an additional `m_multisampledCopyNoCabImage` without `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT`. Records `vkCmdCopyImage` from source to no-CAB image, inserts a pipeline barrier with `VK_ACCESS_TRANSFER_WRITE_BIT` → `VK_ACCESS_TRANSFER_READ_BIT`, then records a second `vkCmdCopyImage` from no-CAB image to `m_multisampledCopyImage`. Exercises the explicit-barrier path required when concurrent access is not guaranteed.

#### `whole_copy_before_resolving_compute` — copy on a compute-only queue

Records the multisampled-to-multisampled copy on a compute-only queue family. Performs queue family ownership transfer (release from universal, acquire on compute, copy, release back) before recording the resolve on the universal queue. Gated on a compute-only queue family existing in `checkSupport`.

#### `whole_copy_before_resolving_transfer` — copy on a transfer-only queue

Same as the compute variant but on a transfer-only queue family. Gated on a transfer-only queue family existing in `checkSupport`.

#### `diff_layout_copy_before_resolving` — copy with different image layouts

Iterates the source and destination operation layouts over `VK_IMAGE_LAYOUT_GENERAL`, `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, and `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, skipping the invalid combinations `TRANSFER_DST_OPTIMAL`-as-source and `TRANSFER_SRC_OPTIMAL`-as-destination. Each leaf name encodes the layout pair as `<sample>_<src-layout>_<dst-layout>`. Uses `COPY_MS_IMAGE_TO_MS_IMAGE`.

#### `layer_copy_before_resolving` — single-layer multisampled copy

Source and destination are 5-layer multisampled images. Records a per-layer `VkImageResolve` for each of the 5 layers. The MS→MS copy uses `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE`: it copies source layer 2 into destination layer 4. `checkTestResult` requires that the four unwritten destination layers remain solid white `(1.0, 1.0, 1.0, 1.0)` and that the copied layer matches the source.

#### `copy_with_regions_before_resolving` — multi-region multisampled copy

Records two `VkImageCopy` regions with halved extents (lower-right to lower-left, upper-right to lower-right) during the MS→MS copy, then resolves from the intermediate. The resolve regions use the same halved extents to align with the copied data. Uses `COPY_MS_IMAGE_TO_MS_IMAGE_MULTIREGION`.

### Array-image resolve variants

These nodes use a 5-layer destination array image and verify per-layer through the verification shader's input-attachment-per-layer declaration.

#### `whole_array_image` — per-layer multisampled copy and resolve

Records five `VkImageResolve` records, one per destination layer, with `baseArrayLayer = layerNdx` and `layerCount = 1`. The MS→MS copy uses `COPY_MS_IMAGE_TO_ARRAY_MS_IMAGE` and copies source layer 0 into each of the 5 destination layers.

#### `whole_array_image_one_region` — single-region array resolve

Records a single `VkImageResolve` with `layerCount = 5`. Adds maintenance5-gated leaves that use `VK_REMAINING_ARRAY_LAYERS` instead of an explicit `layerCount`: `_all_remaining_layers` with `baseArrayLayer = 0`, and `_not_all_remaining_layers` with `baseArrayLayer = 2`. The maintenance5 leaves require `VK_KHR_maintenance5`.

## Shader Analysis

Shader code is not part of the tested behavior. The test records `vkCmdResolveImage` and `vkCmdCopyImage`, both of which are fixed-function transfer commands. A short vertex/fragment shader pair (`vert` and `frag`) is used only to fill the source image with the multisample pattern through a render pass, and a generated verification fragment shader (`verify`) is used only by `checkIntermediateCopy` to compare per-sample input-attachment reads into a storage buffer. Neither shader is the subject of the test, so no representative shader walkthrough is included.

## Runtime Execution and Result Checking

- **Source image fill.** The host creates a multisampled source image, transitions it to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, clears it, then runs a render pass with a colored-quad draw that writes `vec4(0.0, 1.0, 0.0, 1.0)` to the color attachment. The host-side `m_sourceTextureLevel` is filled separately with `FILL_MODE_MULTISAMPLE`, which writes a per-pixel pattern (green, blue, or diagonal teal) that is identical across samples within a pixel.
- **Expected result.** `generateExpectedResult` copies the resolve regions from the source texture level into a destination-shaped expected level via `copyRegionToTextureLevel`. Because the source pattern is sample-invariant, the host-side copy is equivalent to the spec's sample-averaging rule.
- **Optional intermediate copy.** When the option is not `NO_OPTIONAL_OPERATION`, `copyMSImageToMSImage` records `vkCmdCopyImage` (or `vkCmdCopyImage2` with `COPY_COMMANDS_2`) from the source into `m_multisampledCopyImage`. The `NO_CAB` path inserts an intermediate no-CAB image and a between-copies pipeline barrier. The `COMPUTE` and `TRANSFER` paths release ownership to the target queue, record the copy there, and release ownership back to the universal queue. The `MULTIREGION` path halves each region's extent. The `LAYER` path copies source layer 2 to destination layer 4. The `ARRAY` path copies source layer 0 to each of the 5 destination layers.
- **Resolve recording.** `iterate` builds the `VkImageResolve` (or `VkImageResolve2KHR`) list, records a pipeline barrier to move source and destination into `operationLayout`, calls `vk.cmdResolveImage` (or `vk.cmdResolveImage2`), and records a final pipeline barrier to make the destination `VK_ACCESS_HOST_READ_BIT`-visible.
- **Readback.** `readImage` copies the destination image into a host-visible buffer and produces a `tcu::TextureLevel`.
- **Intermediate-copy verification.** For options where `shouldVerifyIntermediateResults` is true, `checkIntermediateCopy` runs before `checkTestResult`. It builds a render pass with the source and the intermediate (or per-layer copies) bound as input attachments, records the verification fragment shader over a full-screen quad, and reads back a storage buffer of `int32_t` flags. Any zero entry fails the test.
- **Final pass/fail.** `checkTestResult` calls `tcu::fuzzyCompare` with threshold `0.01f` per layer. For `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE`, it also checks that the four unwritten destination layers are solid white and that the copied layer matches the source's layer 2 against destination layer 4.

## Failure Meaning

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

### Cause Analysis

#### Resolve averaging and region handling

**Possible failure symptoms:** the resolved destination texels differ from the host reference by more than the `0.01f` fuzzy threshold inside the requested region; out-of-region destination texels are overwritten when they should be preserved; the `with_regions` destination shows one region shifted or missing; the `diff_image_size` destination has clamped or out-of-bounds texels.

**Possible implementation causes:** the resolve unit picks a single sample instead of averaging, drops samples, or applies a non-uniform weighting; the region parser interprets `srcOffset` / `dstOffset` / `extent` in the wrong units (texels versus blocks, or with a sign error); multi-region batching reuses a scratch buffer between regions without flushing; out-of-bounds destination texels are written because the region extent is not clamped against the destination image extent. Per the Vulkan spec, the resolved value is the average of source samples; any deviation from that rule is a driver bug.

#### Intermediate multisampled-copy correctness

**Possible failure symptoms:** `checkIntermediateCopy` returns fail with a message naming a specific `(x, y, sample)` coordinate, meaning the source and intermediate images differ at that sample; the subsequent `checkTestResult` fuzzy compare also fails because the intermediate image diverged from the source.

**Possible implementation causes:** `vkCmdCopyImage` between multisampled images shuffles samples (writes sample N to sample M), picks a single sample and replicates it, or accidentally resolves during the copy; the concurrent-access rule is violated for the `NO_CAB` path because the between-copies pipeline barrier is missing or recorded with the wrong stage mask; the `MULTIREGION` path halves the copy extent but writes the wrong half, so the resolve regions then read uninitialized texels. Per the Vulkan spec, multisampled-to-multisampled `vkCmdCopyImage` copies each sample of the source to the corresponding sample of the destination; the CTS verification shader is designed specifically to detect any deviation from that rule.

#### Queue family ownership transfer

**Possible failure symptoms:** the `whole_copy_before_resolving_compute` or `whole_copy_before_resolving_transfer` leaf fails because the intermediate image contains stale or uninitialized data when the resolve reads it on the universal queue; in some cases the device reports a queue-family-related validation error or lost-device state.

**Possible implementation causes:** the release or acquire barrier used the wrong `srcQueueFamilyIndex` / `dstQueueFamilyIndex`, the wrong `srcAccessMask` / `dstAccessMask`, or the wrong pipeline stage; the driver recorded the `vkCmdCopyImage` on the wrong queue; the layout transition associated with the ownership transfer was applied to the wrong image. Vulkan queue family ownership transfer is a strict release-acquire protocol; any deviation leaves the destination image's contents undefined on the acquiring queue.

#### Layout transition handling

**Possible failure symptoms:** the `diff_layout_copy_before_resolving` leaf fails for a specific layout pair (for example `general`-as-source with `transfer_dst_optimal`-as-destination) but passes for others; the resolved destination shows partial writes or stale texels.

**Possible implementation causes:** the driver's layout transition for `VK_IMAGE_LAYOUT_GENERAL` does not preserve the multisampled sample data, or its `TRANSFER_SRC_OPTIMAL` and `TRANSFER_DST_OPTIMAL` layouts have an unexpected interaction when both source and destination of the MS→MS copy use `GENERAL`. Vulkan allows `vkCmdCopyImage` and `vkCmdResolveImage` in any of these layouts, so a layout-dependent failure is a driver bug.

#### Array layer and `VK_REMAINING_ARRAY_LAYERS` handling

**Possible failure symptoms:** the `whole_array_image` leaf fails on one layer but not others, indicating the per-layer loop is off-by-one; the `whole_array_image_one_region` leaf fails on the maintenance5 `_all_remaining_layers` or `_not_all_remaining_layers` leaf but not on the explicit-`layerCount = 5` leaf; the `layer_copy_before_resolving` leaf fails the unwritten-layer white-color check, meaning unwritten destination layers were modified.

**Possible implementation causes:** the resolve or copy command mishandles `baseArrayLayer != 0`; the maintenance5 rule that `VK_REMAINING_ARRAY_LAYERS` resolves from `baseArrayLayer` to the end of the array is not honored; the per-layer MS→MS copy loop reads from or writes to the wrong layer; the resolve command writes to layers outside the requested `layerCount`. Vulkan `VkImageSubresourceLayers` semantics are explicit about layer ranges; any deviation is a driver bug.

#### Bind offset and allocation-kind handling

**Possible failure symptoms:** the `_bind_offset` leaf fails for a given sample count while the non-`_bind_offset` leaf passes, in the same subgroup and variant root; the `dedicated_allocation` variant root fails where the `core` root passes, or vice versa.

**Possible implementation causes:** the driver's image memory binding path does not honor a non-zero `VkDeviceSize` offset in `vkBindImageMemory`, or the alignment handling for suballocated memory is wrong; the dedicated-allocation path enforces a different memory requirement than the suballocated path. Vulkan requires `vkBindImageMemory` to honor a non-zero offset that is a multiple of `VkMemoryRequirements::alignment`; a bind-offset-specific failure is a driver bug.

#### Shared infrastructure: sample-count and feature gates

**Possible failure symptoms:** every leaf for a given sample count fails across all subgroups; every intermediate-copy leaf fails with a verification-shader-related error; the compute or transfer queue leaf is reported as `NotSupportedError` rather than pass.

**Possible implementation causes:** the device reports a sample count in `framebufferColorSampleCounts` that it does not actually support for the `R8G8B8A8_UNORM` color attachment usage; `fragmentStoresAndAtomics` is reported as supported but the storage-buffer write in the verification shader does not land; the compute-only or transfer-only queue family index is reported but the queue does not support `vkCmdCopyImage` for multisampled images. These are device-feature reporting mismatches rather than resolve-averaging bugs, but they still produce test failures that must be investigated at the device-feature level rather than in the resolve path.

## Case Pruning

### Requirement-based pruning

- **Sample count support.** `checkSupport` reads `VkPhysicalDeviceLimits::framebufferColorSampleCounts` and throws `NotSupportedError` when the requested `VkSampleCountFlagBits` is not supported ([`vktApiResolveTests.cpp#L1621-L1622`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1621-L1622)).
- **Format support.** `getPhysicalDeviceImageFormatProperties` is queried for both source and destination formats with the required usage flags. `VK_ERROR_FORMAT_NOT_SUPPORTED` throws `NotSupportedError` ([`vktApiResolveTests.cpp#L1624-L1635`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1624-L1635)).
- **`fragmentStoresAndAtomics`.** Required for intermediate-copy verification. `checkSupport` throws `NotSupportedError` when the feature is missing and `shouldVerifyIntermediateResults(option)` is true ([`vktApiResolveTests.cpp#L1614-L1619`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1614-L1619)).
- **`VK_KHR_copy_commands2`.** Required for the `copy_commands2` variant root. `checkExtensionSupport` throws `NotSupportedError` when the extension is not enabled ([`vktApiResolveTests.cpp#L1637`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1637)).
- **`VK_KHR_maintenance5`.** Required for the `_all_remaining_layers` and `_not_all_remaining_layers` leaves of `whole_array_image_one_region`. The flag is added via `params.extensionFlags |= MAINTENANCE_5` ([`vktApiResolveTests.cpp#L2415`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2415), [`vktApiResolveTests.cpp#L2469`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2469)).
- **Compute-only and transfer-only queue families.** `checkSupport` throws `NotSupportedError` when no queue family exists that supports compute-only (no graphics) or transfer-only (no graphics, no compute) operations ([`vktApiResolveTests.cpp#L1640-L1651`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1640-L1651)).

### Design-based pruning

- **No `_bind_offset` leaf for dedicated allocation.** The `_bind_offset` variant is skipped when `allocationKind == ALLOCATION_KIND_DEDICATED` because dedicated allocations cannot honor a non-zero bind offset ([`vktApiResolveTests.cpp#L1803-L1807`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1803-L1807)).
- **Layout matrix skips.** The `diff_layout_copy_before_resolving` matrix skips `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` as source and `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` as destination because those layouts are not legal for the source or destination of a transfer command ([`vktApiResolveTests.cpp#L2131-L2133`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2131-L2133)).
- **No `with_regions` bind-offset variants.** `addResolveImageWithRegionsTests` sets `params.imageOffset` once based on `allocationKind` but does not register separate `_bind_offset` leaves; the `imageOffset` flag is fixed across the sample-count enumeration ([`vktApiResolveTests.cpp#L1877`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1877)).
- **No `diff_image_size` source bind-offset variants.** Only the destination-oversized leaves add a `_bind_offset` variant; the source-oversized leaves do not ([`vktApiResolveTests.cpp#L2548-L2582`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2548-L2582)).
- **`whole_array_image_one_region` second block uses `baseArrayLayer = 0`.** The maintenance5 `_all_remaining_layers` leaf uses `baseArrayLayer = 0` and `layerCount = VK_REMAINING_ARRAY_LAYERS`; the `_not_all_remaining_layers` leaf uses `baseArrayLayer = 2` and `layerCount = VK_REMAINING_ARRAY_LAYERS`. The explicit-`layerCount` (non-maintenance5) block uses `baseArrayLayer = 0` and `layerCount = 5`.

## Key Takeaways

- The test reduces the resolve-averaging rule to a sample-invariant fill pattern, so the host reference is a simple region copy. A driver that picks one sample instead of averaging still passes the direct-resolve leaves but is exposed by the intermediate-copy leaves through the verification shader.
- The 13 intermediate nodes are not 13 unrelated tests; they are three behavior clusters. Direct-resolve shape variants vary region geometry; resolve-after-multisampled-copy variants vary the copy's queue, layout, and region pattern; array-image variants vary layer handling.
- The verification fragment shader is verification infrastructure rather than tested behavior. It runs with `VK_SAMPLE_COUNT_1_BIT` and iterates samples in software to avoid the `sampleRateShading` feature.
- `VK_KHR_copy_commands2` is exercised by an entire variant root, not a leaf flag; the `copy_commands2` root uses `vkCmdResolveImage2` and `vkCmdCopyImage2` everywhere the `core` and `dedicated_allocation` roots use the unsuffixed commands.
- The `whole_array_image_one_region` maintenance5 leaves are the only place `VK_REMAINING_ARRAY_LAYERS` is exercised; a maintenance5-specific failure localizes to those leaves.
- See `## Failure Meaning` for the failure analysis grouped by behavior cluster.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ResolveImageToImage` class | [`vktApiResolveTests.cpp#L47-L84`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L47-L84) | Test instance owning source, intermediate, no-CAB, and destination images. |
| `ResolveImageToImage` constructor | [`vktApiResolveTests.cpp#L86-L575`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L86-L575) | Resource creation, sparse path, fill render pass, pipeline, vertex buffer. |
| `iterate()` | [`vktApiResolveTests.cpp#L577-L769`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L577-L769) | Builds `VkImageResolve` regions, records `vkCmdResolveImage` or `vkCmdResolveImage2`. |
| `checkTestResult()` | [`vktApiResolveTests.cpp#L771-L812`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L771-L812) | `tcu::fuzzyCompare` with `0.01f` threshold; layer-copy white-color check. |
| `copyRegionToTextureLevel()` | [`vktApiResolveTests.cpp#L814-L836`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L814-L836) | Host-side expected-level region copy, including `VK_REMAINING_ARRAY_LAYERS` depth expansion. |
| `checkIntermediateCopy()` | [`vktApiResolveTests.cpp#L838-L1163`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L838-L1163) | Verification render pass, fragment shader, storage buffer scan. |
| `copyMSImageToMSImage()` | [`vktApiResolveTests.cpp#L1165-L1590`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1165-L1590) | MS→MS copy with queue ownership transfer, NO_CAB two-step copy, multiregion extent halving. |
| `ResolveImageToImageTestCase::checkSupport` | [`vktApiResolveTests.cpp#L1610-L1652`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1610-L1652) | Sample-count, format, extension, queue-family, and `fragmentStoresAndAtomics` gates. |
| `ResolveImageToImageTestCase::initPrograms` | [`vktApiResolveTests.cpp#L1659-L1754`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1659-L1754) | Generates `vert`, `frag`, and (for intermediate-copy options) `verify` shader sources. |
| `samples[]` and `resolveExtent` | [`vktApiResolveTests.cpp#L1756-L1758`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1756-L1758) | The six sample counts and the 256×256 default resolve extent. |
| `addResolveImageWholeTests` | [`vktApiResolveTests.cpp#L1760-L1809`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1760-L1809) | `whole` subgroup registration. |
| `addResolveImagePartialTests` | [`vktApiResolveTests.cpp#L1811-L1860`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1811-L1860) | `partial` subgroup registration. |
| `addResolveImageWithRegionsTests` | [`vktApiResolveTests.cpp#L1862-L1909`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1862-L1909) | `with_regions` subgroup registration. |
| `addResolveImageWholeCopyBeforeResolvingTests` | [`vktApiResolveTests.cpp#L1911-L1963`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1911-L1963) | `whole_copy_before_resolving` subgroup registration. |
| `addComputeAndTransferQueueTests` | [`vktApiResolveTests.cpp#L1965-L2022`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1965-L2022) | `whole_copy_before_resolving_compute` and `_transfer` subgroup registration. |
| `addResolveImageWholeCopyWithoutCabBeforeResolvingTests` | [`vktApiResolveTests.cpp#L2024-L2077`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2024-L2077) | `whole_copy_before_resolving_no_cab` subgroup registration. |
| `addResolveImageWholeCopyDiffLayoutsBeforeResolvingTests` | [`vktApiResolveTests.cpp#L2079-L2147`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2079-L2147) | `diff_layout_copy_before_resolving` layout matrix. |
| `addResolveImageLayerCopyBeforeResolvingTests` | [`vktApiResolveTests.cpp#L2149-L2205`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2149-L2205) | `layer_copy_before_resolving` subgroup registration. |
| `addResolveCopyImageWithRegionsTests` | [`vktApiResolveTests.cpp#L2207-L2287`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2207-L2287) | `copy_with_regions_before_resolving` subgroup registration. |
| `addResolveImageWholeArrayImageTests` | [`vktApiResolveTests.cpp#L2289-L2344`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2289-L2344) | `whole_array_image` subgroup registration. |
| `addResolveImageWholeArrayImageSingleRegionTests` | [`vktApiResolveTests.cpp#L2346-L2507`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2346-L2507) | `whole_array_image_one_region` subgroup registration, including maintenance5 leaves. |
| `addResolveImageDiffImageSizeTests` | [`vktApiResolveTests.cpp#L2509-L2584`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2509-L2584) | `diff_image_size` subgroup registration with oversized src and dst extents. |
| `addResolveImageTests` | [`vktApiResolveTests.cpp#L2588-L2608`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2588-L2608) | Root registration that adds all 13 intermediate nodes. |
| `addCopiesAndBlittingTests` (parent dispatcher) | [`vktApiCopiesAndBlittingTests.cpp#L119-L230`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) | Routes `resolve_image` under the `core`, `dedicated_allocation`, and `copy_commands2` variant roots. |
| `generateBuffer` / `FILL_MODE_MULTISAMPLE` | [`vktApiCopiesAndBlittingUtil.cpp#L1108-L1272`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1108-L1272) | Host reference fill pattern: green / blue / diagonal teal, identical across samples. |
| `generateExpectedResult` | [`vktApiCopiesAndBlittingUtil.cpp#L1487-L1498`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L1487-L1498) | Copies resolve regions into the destination-shaped expected level. |
| `defaultExtent` and constants | [`vktApiCopiesAndBlittingUtil.hpp#L160-L181`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L160-L181) | 64×64 default extent used by the `*_before_resolving` and `whole_array_image*` subgroups. |
| Test header | [`vktApiResolveTests.hpp`](../../../modules/vulkan/api/vktApiResolveTests.hpp) | Public `addResolveImageTests` declaration consumed by the parent dispatcher. |
