## Overview

**Core question:** Do disjoint image regions retain the correct data when the test issues their copies without an intervening barrier for each region?

- `image.concurrent_copy` tests buffer-to-image copy results for three formats, two tilings, and 2D or 3D images.
- The implementation covers device copy commands and, outside Vulkan SC, `VK_EXT_host_image_copy` calls. Its `multiple` host cases start separate threads for the individual regions.
- Each test fills a source buffer, partitions the image extent into disjoint regions, copies those regions into one image, reads the image back, and compares the complete result with the original buffer.
- This page describes the copy-submission modes, the generated matrix, the layout handling for 2D-array-compatible 3D images, and the checks that turn data corruption into a CTS failure.

## Background Knowledge

For the shared concepts subresources, copies, layouts, and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Disjoint buffer-to-image regions.** A copy region identifies an image subresource, offset, extent, source-buffer offset, row length, and image height. The regions in this test partition the image extent, so each byte of the expected result has one source location and one destination location.
- **Slice-scoped transitions.** A 3D image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` can use 2D or 2D-array views. With `maintenance9`, an image barrier's array-layer range identifies the affected subset of 3D slices, including the layout transition. The 3D array-compatible cases depend on that interpretation during per-slice readback.

## Registration Hierarchy

```text
image.concurrent_copy
├── vk_format_r8g8b8a8_unorm
├── vk_format_r8_unorm
└── vk_format_r32g32_sfloat
```

[`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L94) registers `concurrent_copy` in the `image` test category. [`createImageConcurrentCopyTests()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L662-L795) creates the three direct format components and their deeper parameter hierarchy.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `vk_format_r8g8b8a8_unorm`, `vk_format_r8_unorm`, `vk_format_r32g32_sfloat` | Selects pixel size and the representation used in source data, region addressing, and the final byte comparison. | [Format set](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L666-L670) |
| Tiling | `vk_image_tiling_linear`, `vk_image_tiling_optimal` | Selects the image tiling whose transfer support the test checks. | [Tiling set](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L672-L675) |
| Image type | `vk_image_type_2d`, `vk_image_type_3d` | Sets depth to 1 or 32 and determines whether array-compatible coverage can be registered. | [Type set and dimensions](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L677-L680) and [instance setup](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L210-L221) |
| Submission grouping | `single`, `multiple` | `single` supplies all regions to one copy call. `multiple` records one device copy command per region or starts one host-copy thread per region. | [Command types](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L704-L711) and [copy branches](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L378-L439) |
| Data pattern | `random`, `gradient` | `random` uses format-aware values without NaNs. `gradient` derives an observable value from texel coordinates. | [Data types](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L713-L720) and [source initialization](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L222-L252) |
| Copy submission mode | `device`, `host` | Chooses queue-submitted `vkCmdCopyBufferToImage` or, outside Vulkan SC, `vkCopyMemoryToImageEXT`. | [Copy types](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L682-L691) and [execution branches](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L342-L484) |
| Host access mode | `write`, `read_and_write` | `write` performs host memory-to-image copies. `read_and_write`, available only with `host`, also reads each region through `vkCopyImageToMemoryEXT` and compares it in the worker thread. | [Access types and pruning](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L693-L702) and [host worker](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L97-L157) |
| Image flag | `none`, `2d_array_compatible` | The second value applies only to 3D images and changes setup and readback to use independently transitioned slice ranges. | [Image flags and registration pruning](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L722-L778) |

The test fixes the image extent at `128 × 128 × 1` for 2D or `128 × 128 × 32` for 3D. [`splitRegion()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L181-L194) divides each relevant extent into random lengths from 1 through 32, producing a set of adjacent, non-overlapping regions.

## Behavior Parameters

The primary behavioral axis is **copy submission mode**. `device` and `host` use different Vulkan APIs and execution models; tiling, image type, grouping, data pattern, access mode, and image flag select legal configurations around that choice.

### `device`: queue-submitted transfer copies

`device` records `vkCmdCopyBufferToImage` work in a command buffer. The `single` cases call it once with the full region array; `multiple` cases call it once per region in the same command buffer. Before copying, the test transitions the image from `VK_IMAGE_LAYOUT_UNDEFINED` to its destination layout. It later transitions the image for transfer readback and copies the complete image into the destination buffer.

### `host`: host-image-copy calls

`host`, omitted from Vulkan SC builds, requires `VK_EXT_host_image_copy` and adds `VK_IMAGE_USAGE_HOST_TRANSFER_BIT_EXT` to the image. `single` calls `vkCopyMemoryToImageEXT` once for all regions. `multiple` starts a `HostCopyThread` for each region in a batch; each thread invokes the host memory-to-image copy independently. `read_and_write` makes every worker also call `vkCopyImageToMemoryEXT` and compare that returned region before the common final readback.

## Shader Analysis

This test generates no shaders. Its tested behavior comes from transfer commands, host-image-copy calls, image layout transitions, and host-side comparisons.

## Runtime Execution and Result Checking

- The host allocates host-visible source and destination buffers. It fills the source with either a deterministic coordinate-based gradient or random format-aware data, then flushes that allocation.
- The host creates a transfer-source and transfer-destination image. Host cases also request host-transfer usage. It constructs `VkBufferImageCopy` regions whose offsets and pitches address matching portions of the source buffer.
- For ordinary images, the test transitions the full image to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, or to `VK_IMAGE_LAYOUT_GENERAL` when a host read is requested. For 2D-array-compatible 3D images, the multiple path transitions the slice range used by each region.
- Device cases issue the selected buffer-to-image copies and wait for their command-buffer submission. Host multiple cases create workers in batches of 256, start them, join them, and fail immediately if a `read_and_write` worker detected a mismatch.
- The final readback uses `vkCmdCopyImageToBuffer`. For ordinary images it transitions and copies the whole image. For 2D-array-compatible 3D images it randomizes layer order, transitions each single slice to alternating `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`, and copies each slice to its matching destination-buffer offset.
- The host invalidates the destination allocation and compares it against the source allocation with `memcmp`. On inequality, it logs up to ten mismatching bytes and emits reference and result images before reporting failure.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `device` | Buffer-to-image copy execution across the generated region list, required image layout transitions, image-to-buffer readback, or final byte comparison. |
| `host` | `VK_EXT_host_image_copy` memory-to-image or image-to-memory execution, host-copy layout support, concurrent per-region handling, or the shared final readback and comparison. |

### Cause Analysis

#### Device transfer, transitions, or final readback

**Possible failure symptoms:** A `device` case reports a source/destination byte mismatch after the final image-to-buffer copy. The log identifies up to ten mismatching byte offsets and displays the reference and result images.

**Possible implementation causes:** The failure can arise in the selected buffer-to-image copy, region addressing, transition to the required destination or readback layout, image-to-buffer copy, or the visibility of the readback allocation to the host. Cases with `multiple` also exercise the sequence of individual copy commands in one command buffer. Compare a failing format, tiling, image type, and grouping choice with its neighboring passing cases to isolate the relevant path.

#### Host image-copy operation or per-region read

**Possible failure symptoms:** A `host.read_and_write` case can fail before final readback when a worker's `vkCopyImageToMemoryEXT` result differs from the bytes in that worker's source region. Any host case can also fail the final whole-image comparison.

**Possible implementation causes:** The test first requires `VK_EXT_host_image_copy`, format support, and a supported destination layout. After those gates, a failure can involve `vkCopyMemoryToImageEXT`, the optional `vkCopyImageToMemoryEXT`, the selected host-copy layout, source pointer or row-layout interpretation, or handling of simultaneous per-region host calls. The final comparison also shares the device readback path with `device` cases, so a failure in that check alone does not establish which copy API first produced different contents.

## Case Pruning

### Requirement-based pruning

- Each case calls `getPhysicalDeviceImageFormatProperties()` with transfer-source and transfer-destination usage. The CTS raises `NotSupportedError` when that format, image type, tiling, and usage combination is unsupported.
- `host` requires `VK_EXT_host_image_copy`, host-transfer image usage, and a destination layout advertised through `VkPhysicalDeviceHostImageCopyProperties::pCopyDstLayouts`. The required layout is `VK_IMAGE_LAYOUT_GENERAL` for `read_and_write` and `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` otherwise.
- `2d_array_compatible` requires `VK_KHR_maintenance9`.

### Design-based pruning

- `read_and_write` is registered only below `host`; the `device` path has no per-region host image-to-memory operation.
- `2d_array_compatible` is registered only for `vk_image_type_3d`, because the creation flag applies to 3D images.
- Vulkan SC builds omit `host` and therefore omit `read_and_write`, matching the conditionally compiled host-image-copy implementation.

## Key Takeaways

- The test constructs a full image from disjoint regions and uses the original source buffer as the exact final reference.
- `multiple.device` tests individually recorded copy commands; `multiple.host` tests one host-copy worker per region, batched at 256 workers.
- Host `read_and_write` adds a per-region observation point, while every legal case still ends with the same whole-image byte comparison.
- Array-compatible 3D coverage checks slice-scoped layout transitions and readback with `maintenance9` support.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L94) | Places `concurrent_copy` in the `image` test category. |
| Region partitioning | [`splitRegion()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L181-L194) | Generates the bounded extents that tile the tested image. |
| Host worker | [`HostCopyThread::run()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L97-L157) | Performs one host memory-to-image copy and the optional region readback check. |
| Test iteration | [`ConcurrentCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L196-L579) | Creates resources, executes the copy modes, performs readback, and reports mismatches. |
| Support checks | [`ConcurrentCopyTestCase::checkSupport()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L600-L658) | Checks transfer format support, host-copy capability and layouts, and `maintenance9`. |
| Case matrix registration | [`createImageConcurrentCopyTests()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L662-L795) | Registers the format and parameter hierarchy. |
| Array-compatible image flag | [`resources.adoc#L4160-L4162`](../../../../vulkan-docs/src/chapters/resources.adoc#L4160-L4162) | States that `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` permits 2D and 2D-array image views. |
| Slice-scoped barrier semantics | [`synchronization.adoc#L7523-L7531`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L7523-L7531) | Defines `maintenance9` handling for barrier subresource ranges on 2D-array-compatible 3D images. |
