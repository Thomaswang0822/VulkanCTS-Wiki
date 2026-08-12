# Understanding Brief: sparse image memory aliasing

## One-Sentence Test Purpose

This test checks whether two compatible sparse images that share physical memory for their ordinary residency blocks provide data-consistent aliasing when one image is initialized and the other is written by a compute shader, while separately bound mip tails remain independent.

## Background Knowledge

### Data-consistent sparse image aliasing

A sparse-residency image exposes bindable rectangular image blocks outside its mip tail. With `sparseResidencyAliased` enabled and `VK_IMAGE_CREATE_SPARSE_ALIASED_BIT` set, the same physical memory can be bound into multiple compatible sparse images. Vulkan requires those aliased locations to interpret the memory consistently and requires memory dependencies between accesses through different aliases.

Why it matters here:
- The read and write images receive the same `VkSparseImageMemoryBind` array for their ordinary sparse blocks, so a shader store through the write image must be visible when the read image is copied back.
- The command sequence orders initialization, shader writes, and readback so the comparison tests aliasing rather than an intentional race.

### Ordinary sparse blocks versus mip tails

Mip levels smaller than the implementation-reported sparse image granularity may be grouped into an opaque mip-tail region. Sparse image blocks can participate in data-consistent aliasing, but the Vulkan sparse-memory rules do not provide data-consistent aliasing for mip-tail memory.

Why it matters here:
- The test deliberately gives the read and write images separate opaque mip-tail allocations.
- Readback should therefore contain shader-generated values in the shared ordinary sparse blocks and the original upload pattern in the read image's mip tail.

## One Concrete Example

Consider a `2d` case with a single-plane integer format and several mip levels. The host creates `imageRead` and `imageWrite` with sparse binding, sparse residency, and sparse aliasing enabled. For every mip level before `imageMipTailFirstLod`, it allocates one residency backing range and places the resulting bind in the same bind array for both images. It allocates the two images' mip tails separately.

The host uploads a byte pattern to every mip level of `imageRead`. A compute shader then stores deterministic values through a storage-image view of `imageWrite`. Because the ordinary blocks alias, copying `imageRead` to a host-visible buffer must reveal the shader values in every pre-tail mip. Because the mip tails do not alias, tail mip levels copied from `imageRead` must still match the uploaded byte pattern.

## End-to-End Test Flow

```text
[host] select regular or device-group mode, image type, format, and extent
[host] require sparse-residency aliasing and check image, format, storage, memory, and device-group support
[host] create matching sparse read and write images
[host] allocate ordinary residency blocks once and bind the same block array to both images
[host] allocate and bind separate opaque mip-tail memory for the read and write images
[host] submit vkQueueBindSparse and signal semaphores for transfer and compute work
[host] fill and flush an input buffer with a deterministic per-mip byte pattern
[host] record barriers and copy the input buffer into imageRead
[host] create one storage-image view, descriptor set, and compute pipeline per plane and mip level
[device] dispatch each compute shader through imageWrite and store invocation-derived values
[host] order shader writes before transfer reads and copy imageRead into a host-visible output buffer
[host] submit while waiting for both sparse-bind semaphores, wait for completion, and invalidate the output allocation
[host] compare ordinary sparse-block mips with shader-generated values and mip-tail mips with the original input pattern
[host] return pass only if every checked channel and tail byte matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The case generates one GLSL compute shader for each image plane and mip level. The shader's image type, format qualifier, coordinate width, plane divisors, and integer or floating-point store value depend on the registered image type and format. Each invocation computes a linear logical index and stores `index % 127` in the available color channels, with alpha set to one. R64 cases enable the required 64-bit image extensions.

At runtime, the test creates a matching compute pipeline, storage-image view, and descriptor set for each generated shader. Multi-planar formats use plane-compatible, storage-compatible view formats.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Sparse `imageRead` | yes | yes | initialized by transfer and later copied to the output buffer | indirectly | Observes shader stores made through the aliased write image and retains its own tail data. |
| Sparse `imageWrite` | yes | yes | written through storage-image views by compute shaders | no | Supplies the second resource alias used to modify shared physical blocks. |
| Shared ordinary-block `VkDeviceMemory` allocations | yes | bound to both sparse images with identical residency binds | receive the upload through `imageRead` and shader stores through `imageWrite` | indirectly | Their data-consistent aliasing is the core property under test. |
| Separate read and write mip-tail allocations | yes | bound independently through opaque sparse binds | the read tail receives upload data; the write tail receives shader stores | the read tail is read indirectly | Demonstrate that mip-tail memory is not treated as a data-consistent shared alias. |
| Host-visible input buffer | yes | yes | read by the buffer-to-image copy | host writes it | Supplies a distinct reference byte pattern for every mip level. |
| Host-visible output buffer | yes | yes | written by the image-to-buffer copy | yes | Supplies ordinary-block channel values and tail bytes for final validation. |
| Storage-image views and descriptor sets | yes | yes | select one plane and mip level of `imageWrite` for each dispatch | no | Route shader stores through the write alias with the correct dimensionality and format. |
| Sparse-bind semaphores | yes | yes | order transfer and compute stages after sparse binding | no | Prevent use of either sparse image before its backing memory is established. |

## What Is Checked

- For every plane, channel, and mip level before `imageMipTailFirstLod`, the host checks the values copied from `imageRead` against the deterministic values stored through `imageWrite`.
- Integer channels are compared exactly. Fixed-point channels allow `1e-5` plus the format-derived fixed-point error; floating-point channels allow `1e-5`.
- Subsampled planes are checked only at sample coordinates that exist in that plane.
- For every mip level in the mip tail, the returned bytes from `imageRead` must exactly match the original per-mip upload pattern.
- Any mismatch returns `tcu::TestStatus::fail("Failed")`; all physical-device iterations must complete without a mismatch for the case to pass.

## Behavior Parameter Identification

> **Behavior parameter:** registered image-type intermediate node
>
> **Candidate values:** `2d`, `2d_array`, `cube`, `cube_array`, `3d`

The image type is the primary behavioral axis because it changes image dimensionality, coordinate construction, layer or depth interpretation, image-view type, dispatch geometry, and copy geometry. The regular and device-group test families repeat this axis; format and extent refine each concrete case.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect sparse aliasing, image layout transition, shader store, or transfer handling for a 2D image. |
| `2d_array` | Incorrect array-layer addressing or sparse binding for one or more layers. |
| `cube` | Incorrect cube-compatible setup, face mapping, sparse binding, or readback. |
| `cube_array` | Incorrect cube-face or array-layer mapping in the aliased access path. |
| `3d` | Incorrect depth handling, dispatch grid, sparse binding, or 3D image copy. |
| Any format | Unsupported storage-image or plane format handling, incorrect format-aware comparison, or an R64 feature mismatch. |
| Any device-group case | The regular path or its device-group bind, peer-memory selection, or device-targeted submission fails. |

The first five rows map the primary image-type behavior parameter. The final two rows preserve cross-cutting diagnosis for format and device-group dimensions represented by every image-type value.

## Important Variations and Special Cases

- The source registers the same five image-type values under `image_sparse_memory_aliasing` and `device_group_image_sparse_memory_aliasing`. Device-group mode adds resource-device, memory-device, peer-memory, and submission targeting without changing the image-type matrix.
- Every image type has four source-defined extents. Registration removes extents that violate format alignment, notably for some YCbCr formats.
- Format selection changes channel representation, plane count, storage-compatible image views, sparse aspect requirements, and comparison rules. It does not change the shared-block versus separate-tail mental model.
- Cube and cube-array cases add `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`. For array and cube variants, the source handles the third registered extent component as layer count; for `3d`, it is depth.
- R64 formats require `VK_EXT_shader_image_atomic_int64`, `shaderImageInt64Atomics`, and `sparseImageInt64Atomics` in addition to the ordinary sparse and storage-image requirements.
- Cross-device cases require peer memory to support copy source, copy destination, and generic destination access. Unsupported configurations are pruned rather than reported as aliasing failures.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support requirements and image creation | [`ImageSparseMemoryAliasingCase::checkSupport` and instance setup](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L340) | Establishes sparse aliasing, image-type, format, storage, address-space, memory-type, and peer-memory requirements. |
| Shared residency and separate mip-tail binds | [`Sparse bind construction`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L342-L492) | Shows the same ordinary bind array assigned to both images and distinct opaque tail binds. |
| Upload, image barriers, and shader resource setup | [`Command recording and descriptors`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L495-L733) | Defines the reference upload, alias layouts, plane/mip views, descriptors, and pipelines. |
| Dispatch, copyback, and synchronization | [`Dispatch and submission`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L734-L816) | Defines dispatch geometry, shader-to-transfer ordering, readback, sparse-bind waits, and device targeting. |
| Ordinary-block and mip-tail validation | [`Result verification`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L818-L929) | Separates generated-value checking before the tail from exact reference-byte checking in the tail. |
| Generated compute shaders | [`ImageSparseMemoryAliasingCase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L932-L1024) | Defines format-dependent shaders, plane coordinates, workgroup sizes, and stored values. |
| Registration matrix | [`createImageSparseMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104) | Defines both test-family roots, image types, extents, formats, alignment pruning, and case names. |
| Dispatcher registration | [`createSparseResourcesTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L36-L64) | Confirms both aliasing test families are children of `sparse_resources`. |
| Mustpass evidence | [`sparse-resources.txt`](../../../mustpass/main/vk-default/sparse-resources.txt) | Confirms executable regular and device-group paths for the registered image-type, format, and extent hierarchy. |
| Sparse blocks, mip tails, and aliasing semantics | [`Sparse memory`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-partially-resident-images), [`Sparse Memory Aliasing`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-sparse-memory-aliasing) | Grounds block residency, opaque tails, compatible sparse aliases, data consistency, and dependency requirements. |

## Questions / Risk Points for User Audit

- Is it clear that the ordinary sparse blocks alias but the read and write mip tails intentionally do not?
- Is image type the right primary behavior parameter, with device-group mode and format retained as cross-cutting dimensions?
- Does the validation explanation distinguish generated-value mismatches from preserved-tail byte mismatches?
- Is the device-group distinction explained at the right depth without making it look like a different image-behavior matrix?

## Conversion Notes for Final Wiki Rewrite

- Carry the five image-type values from `## Behavior Parameter Identification` into `## Behavior Parameters`; explain regular versus device-group mode as a separate matrix dimension.
- Preserve the shared ordinary-block versus separate mip-tail contrast in `## Background Knowledge` and the runtime section because it is necessary to interpret both halves of validation.
- Use one representative shader explanation rather than one per image type; dimensionality and plane differences can remain a compact variation summary.
- Copy the primary `### Failure Cause Mapping` table directly into the final page. Keep the cross-cutting table immediately after it if the final page diagnoses device-group, multi-planar, ordinary-block, and mip-tail-only failures separately.
- Write `### Cause Analysis` fresh from the two observable validation outcomes: generated-value mismatches before the mip tail and exact reference-byte mismatches in the mip tail.
