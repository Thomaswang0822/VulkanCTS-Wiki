## Overview

**Core question:** Does an image keep every untouched pixel when Vulkan reacquires it from a foreign queue with an unmodified-memory assertion and then updates only its center?

- This page covers the `memory.external_memory_acquire_unmodified` test family implemented by [`vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp).
- Each test fills an external-capable image, releases it to `VK_QUEUE_FAMILY_FOREIGN_EXT`, and reacquires it with `acquireUnmodifiedMemory = VK_TRUE` without any intervening external access.
- A post-acquire copy replaces only the centered quarter of the image area. The comparison checks the full image, so the copied center and the preserved outer region must both be exact.
- The two intermediate nodes cover DMA-BUF-capable DRM-modifier images and imported Android Hardware Buffer images.

## Background Knowledge

- **External queue-family ownership:** An exclusive image can move between a Vulkan queue family and a special external queue family. `VK_QUEUE_FAMILY_FOREIGN_EXT` represents queues outside the current Vulkan instance regardless of their physical device or driver version.
- **Unmodified acquisition:** Chaining `VkExternalMemoryAcquireUnmodifiedEXT` to an acquire barrier with `acquireUnmodifiedMemory = VK_TRUE` asserts that no memory range bound to the covered resource subresource changed after its most recent release to the source queue family. The implementation may use that fact to reduce acquisition cost. The application remains responsible for making a valid assertion.
- **DRM format modifiers:** A modifier describes an image's implementation-specific memory layout. DMA-BUF cases must select modifiers that support the required transfer operations and external-image use.

## Registration Hierarchy

```text
memory.external_memory_acquire_unmodified
├── android_hardware_buffer
└── dma_buf
```

Each intermediate node has the same five format-named test case leaves. The [default mustpass list](../../../mustpass/main/vk-default/memory.txt#L905-L914) contains all ten paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| External memory handle type | `android_hardware_buffer`, `dma_buf` | Selects the image allocation and external-memory integration path. | [Registration loop](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L877-L910) |
| Format test case leaf | `b8g8r8a8_unorm`, `r16g16b16a16_sfloat`, `r16g16b16a16_unorm`, `r32g32b32a32_sfloat`, `r8g8b8a8_unorm` | Changes channel layout, component width, numeric representation, buffer size, and comparison helper. | [Format array](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L882-L905) |
| DRM format modifier | Every compatible modifier reported for the selected format | Changes the implementation-specific image memory layout. This runtime dimension applies only to `dma_buf`. | [Modifier query and filtering](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L628-L720) |
| Image geometry | 512 by 512 by 1; one mip level, one array layer, one sample | Fixes the resource shape so cases differ in external-memory path and texel representation rather than geometry. | [Image constants](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L69-L70) |
| Updated rectangle | offset `(128, 128)`, extent `256 x 256` | Replaces the centered quarter of the image area and leaves the surrounding pixels dependent on preserved contents. | [Rectangle setup](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L287-L297) |

## Behavior Parameters

The primary behavioral axis is **external memory handle type**. It changes the allocation and binding path, while the ownership-transfer and full-image verification sequence stays common.

### `dma_buf`: DRM-modifier external-capable image

The test queries all DRM format modifiers for the selected format, retains those with transfer support and an importable DMA-BUF external-image configuration, and runs the preservation sequence for each retained modifier. The image declares `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`, but this implementation allocates and binds memory through Vulkan; it does not import or export a DMA-BUF. A failure can therefore be specific to one modifier or to the common DMA-BUF-capable image path.

### `android_hardware_buffer`: imported AHB-backed image

The test allocates an Android Hardware Buffer, creates an external Vulkan image, queries the AHB memory properties, imports the buffer through `VkImportAndroidHardwareBufferInfoANDROID`, and binds dedicated memory to the image. It then runs the same release, unmodified acquisition, partial update, and readback sequence. This value exercises a real external allocation and import boundary.

## Shader Analysis

This test uses transfer commands and pipeline barriers only. It creates no shader modules or shader pipelines, so shader and SPIR-V analysis do not apply.

## Runtime Execution and Result Checking

- The host creates an original source buffer, a complete expected-source buffer, and a result buffer. All three are host visible.
- The original source receives gradient A. The expected source starts as a copy of gradient A, after which the host fills its centered 256 by 256 rectangle with gradient B.
- The handle-specific path creates a 512 by 512 external-capable image. For `dma_buf`, the test repeats all later steps for each compatible DRM format modifier.
- The first command buffer transitions the image for transfer, copies gradient A over the whole image, then releases the image from the universal queue family to `VK_QUEUE_FAMILY_FOREIGN_EXT`. The release also changes the layout to `VK_IMAGE_LAYOUT_GENERAL`.
- The test waits for that submission. No external operation occurs and no memory bound to the image changes while foreign ownership is represented.
- The second command buffer acquires the image from `VK_QUEUE_FAMILY_FOREIGN_EXT`. Its image barrier chains [`VkExternalMemoryAcquireUnmodifiedEXT`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L495-L512) with `acquireUnmodifiedMemory = VK_TRUE` and transitions the image for transfer writes.
- A buffer-to-image copy writes only the centered rectangle from the expected-source buffer. A later barrier prepares the full image for reading, and an image-to-buffer copy writes every pixel to the result buffer.
- After waiting for completion, the host invalidates the result allocation. Float formats use `tcu::floatThresholdCompare`; UNORM formats use `tcu::intThresholdCompare`. Both comparisons use a zero threshold against the complete expected-source image.
- AHB has one comparison per registered leaf. A DMA-BUF leaf passes only if every compatible modifier passes; the loop continues after a failed modifier so the log identifies all failing modifiers.

The expected result has gradient B in the center and the original gradient A everywhere else. A mismatch inside the center points to the post-acquire transfer or its surrounding synchronization. A mismatch outside the center shows that contents written before release did not survive the unmodified acquire and subsequent partial update, or that a later full-image readback path corrupted them.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dma_buf` | Unmodified foreign acquisition or content preservation fails for a DMA-BUF-capable DRM-modifier image; a modifier-specific image layout, transfer, or memory-binding path may also be wrong. |
| `android_hardware_buffer` | Unmodified foreign acquisition or content preservation fails for an imported Android Hardware Buffer image; AHB creation, property query, dedicated import, binding, or transfer handling may also be wrong. |

Both values share the full-image transfer, ownership barrier, partial update, readback, and host comparison path, so a failure across both can also indicate a defect in that shared path rather than in one external handle integration.

### Cause Analysis

#### DMA-BUF unmodified-acquire or modifier-path failure

**Possible failure symptoms:** The log names one or more DRM format modifiers whose full-image comparison failed. Pixels outside the central rectangle may differ from gradient A, pixels inside may differ from gradient B, or both regions may be wrong. The registered case fails if any tested modifier fails.

**Possible implementation causes:** The implementation may mishandle content preservation when acquiring the DRM-modifier image from `VK_QUEUE_FAMILY_FOREIGN_EXT` with the valid unmodified assertion. A failure limited to one modifier can instead come from that modifier's image layout, transfer addressing, memory requirements, or binding path. The source tests all compatible modifiers and logs each result, so the modifier pattern and mismatch coordinates are needed to separate these causes.

#### Android Hardware Buffer import or unmodified-acquire failure

**Possible failure symptoms:** The full-image comparison for the AHB-backed image reports mismatches in the preserved outer region, the updated center, or both. Allocation and import failures may instead stop the case before comparison or produce a not-supported result where the source has an explicit support check.

**Possible implementation causes:** The implementation may fail to preserve the imported image's contents across the foreign release and unmodified acquire. AHB property reporting, dedicated import, memory binding, or transfer access to the imported allocation can also produce the same final mismatch. The comparison alone cannot assign the defect to one of these stages; API errors, validation output, and mismatch location provide the needed distinction.

#### Shared transfer, ownership, or readback failure

**Possible failure symptoms:** The same region pattern fails across both handle types or several formats. Outer-region mismatches expose lost pre-release data. Center-only mismatches expose the partial update path. Whole-image or channel-dependent mismatches can arise during initial upload, layout transitions, copyback, or host comparison input.

**Possible implementation causes:** The shared command sequence may mishandle the release/acquire barriers, image layout transitions, transfer visibility, partial-copy addressing, or image-to-buffer readback. Vulkan defines `acquireUnmodifiedMemory = VK_TRUE` as a statement that the bound ranges remained unmodified since release; in this test no operation changes them during that interval. An implementation that discards or needlessly reconstructs valid contents incorrectly can therefore damage the untouched region. Source-level investigation is required if logs do not isolate a handle type, format, modifier, or image region.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_external_memory_acquire_unmodified`.
- `dma_buf` also requires `VK_EXT_external_memory_dma_buf` and `VK_EXT_image_drm_format_modifier`. A reported modifier is retained only if it has transfer-source and transfer-destination features, supports the fixed image configuration, and reports importable external memory. A case with no compatible modifier reports `NotSupported`.
- `android_hardware_buffer` requires `VK_ANDROID_external_memory_android_hardware_buffer`, a usable AHB API, and an AHB allocation that supports the requested layer count.
- The source registers these tests only in the ordinary Vulkan build, not Vulkan SC.

### Design-based pruning

- The matrix contains only handle types that support the intended `VK_QUEUE_FAMILY_FOREIGN_EXT` path. It does not add a `VK_QUEUE_FAMILY_EXTERNAL` variant because that special family represents an external queue with the same device identity and driver version, for which the source expects the unmodified-acquire handling under study to offer no useful distinction.
- Geometry, mip count, layer count, and sample count stay fixed. The matrix varies handle integration, texel format, and DMA-BUF modifier instead.
- The DMA-BUF path does not cover a GBM-created and imported allocation. Vulkan allocates its memory, so the case targets driver behavior in isolation rather than the complete external allocator stack.

## Key Takeaways

- The partial center copy makes preservation observable: untouched pixels must retain the gradient written before foreign ownership, while center pixels must contain the new gradient.
- The unmodified assertion is valid because the test performs no access between release and reacquisition.
- `dma_buf` covers every compatible DRM modifier with Vulkan-allocated memory; `android_hardware_buffer` covers an actual external allocation and dedicated import.
- The host compares the complete image with zero tolerance. See `## Failure Meaning` for how handle-specific and shared failures differ.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test-family attachment | [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L78) | Registers this test family under `memory` in non-Vulkan-SC builds. |
| Support checks | [`TestCase::checkSupport()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L196-L215) | Defines common and handle-specific extension requirements. |
| Expected-image setup | [`TestInstance::iterate()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L272-L345) | Creates the buffers, gradients, and centered update rectangle. |
| DMA-BUF modifier loop | [`testDmaBuf()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L352-L386) | Aggregates results while retaining per-modifier diagnostics. |
| Ownership and copy sequence | [`testImage()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L389-L588) | Records the full upload, foreign release, unmodified acquire, partial copy, and readback. |
| Pass/fail comparison | [`testImage()` comparison](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L590-L617) | Compares the full result with zero threshold. |
| Modifier compatibility | [`DmaBufImageWithMemory` queries](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L628-L720) | Filters runtime DRM modifiers. |
| DMA-BUF image construction | [`DmaBufImageWithMemory` constructor](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L723-L800) | Creates the modifier image and documents the Vulkan-allocation coverage boundary. |
| AHB image construction | [`AhbBufImageWithMemory` constructor](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L802-L858) | Allocates, imports, and binds the Android Hardware Buffer. |
| Test matrix registration | [`createExternalMemoryAcquireUnmodifiedTests()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp#L872-L913) | Registers the handle-type intermediate nodes and five format leaves. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L905-L914) | Lists all ten executable paths. |
| Vulkan semantics | [`VkExternalMemoryAcquireUnmodifiedEXT`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L8256-L8329) | Defines the unmodified assertion, its scope, and valid usage. |
