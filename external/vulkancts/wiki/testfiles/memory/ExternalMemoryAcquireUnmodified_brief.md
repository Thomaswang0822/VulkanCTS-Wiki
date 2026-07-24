# Understanding Brief: External Memory Acquire Unmodified

## One-Sentence Test Purpose

This test checks whether an implementation preserves an external-capable image's contents across release to and unmodified acquisition from `VK_QUEUE_FAMILY_FOREIGN_EXT`, including pixels outside a later partial update.

## Background Knowledge

### External queue-family ownership and the unmodified-acquire promise

An exclusive image has queue-family ownership. Vulkan represents release to, and acquisition from, an external consumer with special queue-family indices. `VK_QUEUE_FAMILY_FOREIGN_EXT` covers queues outside the current Vulkan instance regardless of physical device or driver version.

`VkExternalMemoryAcquireUnmodifiedEXT` may be chained to the acquiring image barrier. Setting `acquireUnmodifiedMemory` to `VK_TRUE` asserts that no range of memory bound to the barrier's image subresource range changed after the most recent release to the source queue family. The application must make that assertion truthfully. The implementation may use it to avoid the performance cost of recovering externally modified data.

Why it matters here:

- The test releases and reacquires the same whole image subresource through `VK_QUEUE_FAMILY_FOREIGN_EXT`.
- No external consumer accesses the image between those operations, so the unmodified assertion is valid.
- A partial write after acquisition leaves most pixels dependent on preservation of the pre-release contents.

### External-capable memory is not one allocation path

The external handle type changes how the image and memory are created. The Android Hardware Buffer path allocates an AHB, creates an external image, imports the AHB into dedicated Vulkan memory, and binds it. The DMA-BUF path creates a DRM-format-modifier image marked for DMA-BUF external memory, but allocates its memory through Vulkan rather than importing a DMA-BUF. Both paths exercise the ownership-transfer promise, but only the AHB path crosses a real external allocation/import boundary.

## One Concrete Example

Consider the registered case `dEQP-VK.memory.external_memory_acquire_unmodified.dma_buf.r8g8b8a8_unorm` with one compatible DRM format modifier:

1. The host creates a 512 by 512 external-capable image.
2. It fills the whole image with gradient A, then releases ownership to `VK_QUEUE_FAMILY_FOREIGN_EXT`.
3. Nothing modifies the image while foreign ownership is represented.
4. It reacquires the image with `acquireUnmodifiedMemory = VK_TRUE`.
5. It copies gradient B only into the centered 256 by 256 rectangle.
6. It reads back the whole image.

The expected image contains gradient B in the center and the original gradient A around it. A full-image comparison catches lost or corrupted outer pixels as well as an incorrect center update.

## End-to-End Test Flow

```text
[host] select the external memory handle type and image format
[host] create three host-visible buffers: original source, expected source, and result
[host] fill the original source with gradient A
[host] copy gradient A into the expected source, then replace its centered half-width, half-height rectangle with gradient B
[host] create the external-capable 512 x 512 image and bind memory
[host] for DMA-BUF, enumerate and retain compatible DRM format modifiers; run this flow once per retained modifier
[device] copy the full original source into the image
[device] release the whole image subresource from the universal queue family to VK_QUEUE_FAMILY_FOREIGN_EXT
[host] wait for the release submission; no external operation changes the image
[device] acquire the whole image from VK_QUEUE_FAMILY_FOREIGN_EXT with acquireUnmodifiedMemory = VK_TRUE
[device] copy only the centered rectangle from the expected source into the image
[device] copy the full image into the result buffer and make transfer writes visible to the host
[host] wait, invalidate the result allocation, and compare every pixel against the expected source with zero threshold
[host] pass only if every AHB run, or every compatible DMA-BUF modifier run, compares equal
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test uses transfer commands and barriers only. It creates no shaders, shader modules, descriptor layouts, or graphics/compute pipelines. The runtime-discovered DMA-BUF modifier list is the only generated matrix: the test queries modifiers for the chosen format and filters them for transfer features, external-image support, importability, and the fixed extent.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Original source buffer | yes | yes | read by transfer commands | no | Supplies gradient A for the initial full-image copy. |
| Expected source buffer | yes | yes | its center is read by transfer commands | host initializes it | Holds the complete expected image: A outside and B inside. |
| External-capable image | yes | yes | written, ownership-transferred, partially overwritten, then read | indirectly | Carries the contents whose preservation is under test. |
| Result buffer | yes | yes | written by the image-to-buffer copy | yes | Exposes every image pixel to the host comparison. |
| Android Hardware Buffer | AHB allocator creates it | imported and bound as dedicated memory | backs the image | no | Exercises an actual external allocation/import path. |
| DMA-BUF-capable allocation | Vulkan allocates it | bound to a DRM-modifier image | backs the image | no | Exercises DMA-BUF-compatible image behavior without importing or exporting a DMA-BUF. |

## What Is Checked

- The host compares the full 512 by 512 result against the complete expected source.
- The central 256 by 256 rectangle must contain gradient B from the partial post-acquire copy.
- Every pixel outside that rectangle must retain gradient A written before release.
- Float formats use `tcu::floatThresholdCompare`; UNORM formats use `tcu::intThresholdCompare`. Both use a zero threshold.
- An AHB case passes after its one image comparison. A DMA-BUF case passes only if every compatible modifier compares successfully; the loop continues after a failed modifier to preserve diagnostics.

## Behavior Parameter Identification

> **Behavior parameter:** external memory handle type (intermediate node)
>
> **Candidate values:** `dma_buf`, `android_hardware_buffer`

The image format changes pixel representation and comparison routine, while the handle type changes the external-memory allocation path and, for DMA-BUF, adds runtime modifier iteration. It is therefore the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dma_buf` | Unmodified foreign acquisition or content preservation fails for a DMA-BUF-capable DRM-modifier image; a modifier-specific image layout, transfer, or memory-binding path may also be wrong. |
| `android_hardware_buffer` | Unmodified foreign acquisition or content preservation fails for an imported Android Hardware Buffer image; AHB creation, property query, dedicated import, binding, or transfer handling may also be wrong. |

Both values share the full-image transfer, ownership barrier, partial update, readback, and host comparison path, so a failure across both can also indicate a defect in that shared path rather than in one external handle integration.

## Important Variations and Special Cases

- Five registered formats cover two 8-bit UNORM layouts, one 16-bit-per-channel UNORM layout, and two floating-point layouts. This changes texel size, channel ordering, and the exact comparison helper, but not the preservation mechanism.
- A DMA-BUF test case discovers compatible DRM format modifiers at runtime and tests all of them. No compatible modifier produces `NotSupported`, rather than a conformance failure.
- The DMA-BUF path requires importable external-image support but uses Vulkan-allocated memory. The source records a TODO for a GBM-allocated DMA-BUF path, which would cover more of the production graphics stack.
- The AHB path does import a real Android Hardware Buffer allocation into dedicated Vulkan memory.
- The source deliberately uses `VK_QUEUE_FAMILY_FOREIGN_EXT`. It excludes `VK_QUEUE_FAMILY_EXTERNAL` because that sentinel describes an external queue using the same device identity and driver, making the implementation behavior expected by this test less useful to exercise.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Fixed image and parameter definitions | [`imageExtent` and `TestParams`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L69-L76) | Defines the 512 by 512 image, format, and external handle type. |
| Support gates | [`TestCase::checkSupport()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L196-L215) | Requires the common extension and handle-specific extensions. |
| Buffers and expected gradients | [`TestInstance::iterate()` setup](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L272-L345) | Builds gradient A and the A-outside/B-inside expected image. |
| DMA-BUF modifier iteration | [`testDmaBuf()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L352-L386) | Runs every compatible modifier and aggregates failures. |
| Release, acquire, partial copy, and readback | [`testImage()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L389-L588) | Implements the tested ownership and preservation sequence. |
| Exact image comparison | [`testImage()` comparison](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L590-L617) | Defines the zero-threshold pass condition. |
| DMA-BUF compatibility filtering | [`getCompatibleDrmFormatModifiers()` and helpers](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L628-L720) | Selects legal runtime modifiers. |
| DMA-BUF image and allocation | [`DmaBufImageWithMemory`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L723-L800) | Shows the external-capable image and Vulkan allocation boundary. |
| AHB image and imported memory | [`AhbBufImageWithMemory`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L802-L858) | Shows actual AHB allocation, import, and binding. |
| Test registration | [`createExternalMemoryAcquireUnmodifiedTests()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L872-L913) | Registers both handle-type intermediate nodes and five format leaves under each. |
| Parent registration | [`createMemoryTests()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L61) | Attaches the test family to `memory`. |
| Mustpass leaves | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L905-L914) | Confirms all ten registered paths. |
| Unmodified-acquire semantics | [`VkExternalMemoryAcquireUnmodifiedEXT`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L8256-L8329) | Defines the assertion, its scope, and valid usage. |

## Questions / Risk Points for User Audit

- Is the distinction between the DMA-BUF-compatible Vulkan allocation and the imported AHB allocation clear?
- Is it clear that no external consumer runs and that this absence makes `acquireUnmodifiedMemory = VK_TRUE` valid?
- Does the full expected image explain why the partial update detects damage outside the copied rectangle?
- Is external memory handle type the right behavioral axis, with format and DRM modifier treated as secondary dimensions?
- Does the failure mapping avoid attributing a mismatch to one implementation layer before modifier logs and mismatch location are inspected?

The inspected source, registration, mustpass list, and synchronization specification resolve these questions for the final rewrite. No shader audit is needed because the test records transfer commands only.

## Conversion Notes for Final Wiki Rewrite

- Carry `external memory handle type` and its values `dma_buf` and `android_hardware_buffer` into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table and its following shared-cause paragraph unchanged.
- Keep the centered partial-update example as a compact runtime explanation rather than a shader walkthrough.
- Distill ownership-transfer and unmodified-acquire semantics into brief prerequisite bullets.
- Keep the DMA-BUF allocation limitation explicit in runtime or pruning notes.
- Move source entry points to the final appendix.
