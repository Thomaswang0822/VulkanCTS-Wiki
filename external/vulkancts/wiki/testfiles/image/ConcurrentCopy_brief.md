# Understanding Brief: `image.concurrent_copy`

## One-Sentence Test Purpose

This test checks whether image contents remain correct after one or more disjoint buffer-to-image copies, issued either through device commands or, outside Vulkan SC, host image-copy calls without barriers between the individual copy regions.

## Background Knowledge

### Disjoint image-copy regions

A buffer-to-image copy names an image subresource, offset, extent, and source-buffer layout. Separate copies can populate different regions of the same image without overwriting one another. The test divides a complete image into regions that tile its extent, so the expected final image is the original source buffer.

Why it matters here:
- The test checks data preservation across region boundaries, not the outcome of overlapping writes.
- The source offsets and row pitches make every region address its matching portion of the source buffer.

### Layout transitions for independently addressed 3D slices

A 3D image created with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` can support 2D and 2D-array image views. With `maintenance9` enabled, a barrier subresource range can affect only the specified slices of such a 3D image, including its layout transition.

Why it matters here:
- The `2d_array_compatible` cases split the depth dimension into slice ranges.
- The test transitions and reads those slices in a randomized order, alternating `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and `VK_IMAGE_LAYOUT_GENERAL` during readback.

## One Concrete Example

Consider this representative Vulkan case:

```text
dEQP-VK.image.concurrent_copy.vk_format_r8_unorm.vk_image_tiling_optimal.vk_image_type_2d.multiple.gradient.host.read_and_write.none
```

The host fills a `128 × 128` source buffer with the deterministic gradient. `splitRegion()` partitions the image width and height into random extents of at most 32 texels. For each region, the test creates one `VkMemoryToImageCopyEXT` that points into the matching source-buffer offset.

The `multiple` and `host` choices make the implementation start one `HostCopyThread` per region, in batches of at most 256. Each thread calls `vkCopyMemoryToImageEXT`; `read_and_write` then makes that same thread call `vkCopyImageToMemoryEXT` and compare its own region with the source bytes. After all threads join, the normal readback path copies the whole image into a destination buffer for a final byte-for-byte comparison.

## End-to-End Test Flow

```text
[host] choose format, tiling, image type, copy mode, data pattern, and image flag
[host] allocate host-visible source and destination buffers and fill the source buffer
[host] create a transfer-capable image and divide its extent into disjoint regions
[host] transition the whole image, or per-slice ranges for a 2D-array-compatible 3D image
[host] issue one batched or many individual device copies, or start host-copy threads outside Vulkan SC
[host] join host-copy threads and fail if a per-region host read differs from its source bytes
[device] execute queued buffer-to-image copies and image-to-buffer readback copies
[host] invalidate the destination allocation, compare all bytes, and report pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates no shaders, pipelines, descriptors, or SPIR-V. It builds a deterministic gradient or format-aware random source-data array, then derives a randomized tiling of that array with `splitRegion()`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source buffer | yes | yes | read by device-copy commands; its host address is the source for host copies | already host-visible | Holds the complete expected image contents. |
| Destination buffer | yes | yes | written by image-to-buffer readback commands | yes | Supplies the final whole-image comparison. |
| Test image | yes | yes | written by buffer-to-image or host memory-to-image copies; read by image-to-buffer or host image-to-memory copies | indirectly | Holds the partitioned copy results. |
| Region lists | yes | no | used as command or host-copy parameters | no | Associate each image extent with its matching buffer offset and row layout. |

## What Is Checked

- The source buffer and final destination buffer must match byte for byte across the complete `128 × 128 × depth` image allocation.
- In host `read_and_write` cases, every `HostCopyThread` also compares the bytes returned by `vkCopyImageToMemoryEXT` for its own copied region.
- On a mismatch, the test logs up to ten byte offsets and emits reference and result images before returning failure.

## Behavior Parameter Identification

> **Behavior parameter:** copy submission mode
>
> **Candidate values:** `device`, `host`

The `device` and `host` test-family components select different copy APIs and execution models. `single` versus `multiple` changes how the selected API submits the region list, while `write` versus `read_and_write` is only available with `host`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `device` | Buffer-to-image copy execution across the generated region list, required image layout transitions, image-to-buffer readback, or final byte comparison. |
| `host` | `VK_EXT_host_image_copy` memory-to-image or image-to-memory execution, host-copy layout support, concurrent per-region handling, or the shared final readback and comparison. |

## Important Variations and Special Cases

- `single` supplies all regions to one copy call. `multiple` supplies each device region in a separate command or each host region through a separate thread.
- `gradient` makes positions observable through a deterministic value; `random` uses format-aware random data that avoids NaNs.
- `read_and_write` applies only to `host`, because only `HostCopyThread` performs the optional `vkCopyImageToMemoryEXT` region check.
- `2d_array_compatible` applies only to 3D images. It requires `VK_KHR_maintenance9` and changes setup and readback to operate on slice ranges.
- Vulkan SC excludes `host` and `read_and_write` registrations because the host-image-copy implementation is conditionally compiled out.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L94) | Registers `concurrent_copy` in the `image` test category. |
| Test matrix factory | [`createImageConcurrentCopyTests()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L662-L795) | Creates the registered format, tiling, type, submission, data, copy, access, and image-flag hierarchy. |
| Region partitioning | [`splitRegion()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L181-L194) | Splits each tested extent into bounded disjoint region sizes. |
| Host copy worker | [`HostCopyThread::run()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L97-L157) | Issues host memory-to-image copies and optional host image-to-memory checks. |
| Execution and final check | [`ConcurrentCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L196-L579) | Creates resources, executes copies, performs readback, and compares results. |
| Support checks | [`ConcurrentCopyTestCase::checkSupport()`](../../../modules/vulkan/image/vktImageConcurrentCopyTests.cpp#L600-L658) | Checks format support, host-image-copy requirements, supported layouts, and `maintenance9`. |
| 3D slice barriers | [`synchronization.adoc#L7523-L7531`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L7523-L7531) | Defines the `maintenance9` behavior for subresource ranges on 2D-array-compatible 3D images. |

## Questions / Risk Points for User Audit

- Is “copy submission mode” the useful behavioral axis, with `device` and `host` as its values?
- Does the distinction between concurrent host threads and sequentially recorded device copy commands remain clear?
- Does the example make the two layers of host readback understandable: optional per-region checks and mandatory final whole-image comparison?

## Conversion Notes for Final Wiki Rewrite

- Keep the compact prerequisites on disjoint regions and per-slice transitions.
- Carry the behavior-parameter conclusion into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table verbatim into the final page; write fresh cause analysis from the observed checks.
- Omit shader walkthroughs because this test uses copy commands and host-image-copy calls only.
