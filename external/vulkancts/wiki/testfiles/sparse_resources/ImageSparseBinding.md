## Overview

**Core question:** Do fully resident sparse images remain usable when their opaque memory binds are packaged in different `vkQueueBindSparse` layouts?

- `vktSparseResourcesImageSparseBinding.cpp` implements the `image_sparse_binding` and `device_group_image_sparse_binding` test families.
- Each case creates a sparse image, backs its complete opaque binding range with aligned memory, copies a deterministic pattern through every plane and mip level, and compares the data after copyback.
- The three behavior families vary the structure of the sparse submission, while the image type, format, and size matrix broadens resource coverage.

## Background Knowledge

- A fully resident sparse image uses `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`. `VkSparseImageOpaqueMemoryBindInfo` maps aligned ranges in the image's opaque memory requirement to `VkDeviceMemory`; it does not identify individual image blocks.
- `vkQueueBindSparse` accepts one or more `VkBindSparseInfo` batches. A batch can contain one opaque-bind record with many binds, many records, or the test can submit many batches in one call.
- Device-group sparse binding adds `VkDeviceGroupBindSparseInfo`, whose resource and memory device indices identify the physical-device instances used by a batch.

## Registration Hierarchy

```text
sparse_resources.image_sparse_binding
├── multiple_sparse_memory_bind
├── multiple_sparse_image_opaque_memory_bind_info
└── multiple_bind_sparse_info

sparse_resources.device_group_image_sparse_binding
├── multiple_sparse_memory_bind
├── multiple_sparse_image_opaque_memory_bind_info
└── multiple_bind_sparse_info
```

The two roots use the same direct test families; the second root enables device-group binding metadata.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Registered roots | `image_sparse_binding`, `device_group_image_sparse_binding` | Selects regular or device-group sparse binding; both use the same matrix | [`createImageSparseBindingTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L720) |
| Bind packaging | `multiple_sparse_memory_bind`, `multiple_sparse_image_opaque_memory_bind_info`, `multiple_bind_sparse_info` | Selects how opaque binds are arranged in sparse submissions | [`BindType` and `toString`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L58-L82) |
| Image type | `1D`, `1DArray`, `2D`, `2DArray`, `3D`, `Cube`, `CubeArray` | Changes image dimensionality, layer count, and copy extents | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L635-L656) |
| Image sizes | Three sizes per type, including values such as `512x256x1`, `1024x128x1`, and `11x137x1` | Exercises regular and odd dimensions while preserving type-specific layer counts | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L635-L656) |
| Format | Formats from `getTestFormats()`, plus `VK_FORMAT_A8_UNORM_KHR` for regular cases outside Vulkan SC | Changes element size, plane count, alignment, and comparison rules | [`getSparseBindingTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L619-L626), [`getTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) |

## Behavior Parameters

The primary behavioral axis is the bind packaging test family. Image type, format, size, and the regular/device-group root change the resource matrix or routing, but these three values change how the sparse binding operation is submitted.

### `multiple_sparse_memory_bind` — one opaque record with many binds

The case creates one `VkSparseMemoryBind` for each alignment-sized range and places all of them in one `VkSparseImageOpaqueMemoryBindInfo`. One `VkBindSparseInfo` submits that record.

### `multiple_sparse_image_opaque_memory_bind_info` — many opaque records in one batch

The case still creates one aligned memory bind per range, but wraps each bind in its own `VkSparseImageOpaqueMemoryBindInfo`. One `VkBindSparseInfo` submits all records with `imageOpaqueBindCount` equal to the number of ranges.

### `multiple_bind_sparse_info` — many batches in one queue call

The case creates one opaque-bind record per range and one `VkBindSparseInfo` per record. It passes the complete array to `vkQueueBindSparse`, so the call contains multiple sparse-binding batches.

## Shader Analysis

No shader code participates in this test. The device-side work uses transfer commands to write and read the sparse image.

## Runtime Execution and Result Checking

- Support checks require `sparseBinding`, verify the selected image size against device limits, query sparse image format properties, select a compatible memory type, and reject an image allocation larger than `sparseAddressSpaceSize`. Device-group cases also check peer memory-copy support.
- The test creates the sparse image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, calculates its mip count, obtains the opaque memory requirement, allocates aligned memory objects, and submits the selected bind packaging with a fence.
- After waiting for the fence, it creates transfer command buffers on a compute-capable queue. Queue-family barriers handle ownership transfer when the sparse and compute queues differ.
- A host-visible input buffer receives the deterministic pattern `(byteIndex % alignment) + 1`. The command buffer copies it into every plane and mip level of the image, then copies the image into a host-visible output buffer.
- The test waits for command completion, invalidates the output allocation, and compares each returned byte with the corresponding reference byte. It masks the low six or four bits for formats where those bits are don't-care.
- Any masked mismatch returns `tcu::TestStatus::fail("Failed")`; a complete match returns `tcu::TestStatus::pass("Passed")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `multiple_sparse_memory_bind` | Incorrect handling of one opaque-bind record containing many aligned memory binds; sparse image binding or transfer/copyback failure |
| `multiple_sparse_image_opaque_memory_bind_info` | Incorrect handling of multiple opaque-bind records in one `VkBindSparseInfo`; sparse submission packaging or image backing failure |
| `multiple_bind_sparse_info` | Incorrect handling of multiple `VkBindSparseInfo` batches in one `vkQueueBindSparse` call; batch execution, binding, or transfer/copyback failure |

### Cause Analysis

#### Opaque range binding and image backing

**Possible failure symptoms:** The sparse bind call fails, the fence does not complete as expected, or the copyback comparison finds differences in one or more planes or mip levels.

**Possible implementation causes:** The source creates aligned `VkSparseMemoryBind` ranges and uses `VkSparseImageOpaqueMemoryBindInfo` for a fully resident image. Vulkan requires image sparse memory offsets to meet the image memory requirement alignment and requires each range to remain within the resource memory requirement. A violation in range coverage, alignment handling, or association between the image and memory can prevent valid access. The exact implementation cause requires investigation of the failing case.

#### Sparse submission packaging

**Possible failure symptoms:** One packaging family fails while the image matrix and transfer path pass under another family, or a subset of opaque ranges appears corrupted after copyback.

**Possible implementation causes:** The driver may mishandle the count or array layout of `VkSparseImageOpaqueMemoryBindInfo` records, or the batch array passed to `vkQueueBindSparse`. The Vulkan specification defines `imageOpaqueBindCount` as the number of opaque image bind records in a batch and `bindInfoCount` as the number of batches. The failing family identifies which packaging contract needs investigation; it does not by itself identify a hardware, driver, or host defect.

#### Transfer, synchronization, or copyback

**Possible failure symptoms:** Sparse binding completes, but the output bytes differ from the input pattern after buffer-to-image and image-to-buffer operations.

**Possible implementation causes:** The failure can arise from incorrect queue-family ownership transitions, transfer access or layout handling, plane and mip extents, device-group routing, or data preservation through the sparse image. The test waits for the sparse-bind fence and queue completion, so the remaining cause must be investigated against the specific resource and synchronization path rather than assumed in advance.

## Case Pruning

### Requirement-based pruning

- Cases require the core `sparseBinding` feature and a suitable sparse-binding queue plus a compute-capable queue.
- Image dimensions exceeding the device's image or array-layer limits are not supported.
- The image format must support sparse binding according to `getPhysicalDeviceImageFormatProperties`.
- `VK_FORMAT_A8_UNORM_KHR` requires `VK_KHR_maintenance5` outside Vulkan SC.
- R64 formats require `VK_EXT_shader_image_atomic_int64` and the `sparseImageInt64Atomics` feature.
- Device-group cases require the peer memory-copy capability used for the selected devices.

### Design-based pruning

- The generator skips image sizes that fail the format's X or Y alignment checks. This avoids invalid odd-sized cases for formats with subsampling or other alignment restrictions.
- The device-group root omits the extra `VK_FORMAT_A8_UNORM_KHR` format used by regular cases, while retaining the common core format matrix.

## Key Takeaways

- The three test families isolate the representation of the same fully resident opaque image binding: many binds in one record, many records in one batch, or many batches in one queue call.
- Passing the sparse bind operation is not sufficient. The test proves the result by copying data through every plane and mip level and checking the returned bytes.
- The device-group family keeps the same resource matrix but exercises explicit resource and memory device selection during sparse binding and transfer submission.
- Format planes, alignment, device limits, and don't-care bits affect which cases are legal and how their results are checked.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration and parameter generation | [`createImageSparseBindingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L631-L705) | Builds both roots, three bind families, and the image matrix |
| Support validation | [`ImageSparseBindingCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L107-L163) | Checks features, image limits, sparse support, memory, and queues |
| Sparse bind execution | [`ImageSparseBindingInstance::iterate`, bind switch](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L427) | Packages and submits the three binding variants |
| Data transfer and validation | [`ImageSparseBindingInstance::iterate`, transfer path](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L429-L611) | Copies all planes and mip levels and performs the masked comparison |
| Shared format and image helpers | [`getTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies the format matrix and planar formats |
| Opaque sparse image binding semantics | [`VkSparseImageOpaqueMemoryBindInfo`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L1516-L1568) | Defines the structure and its intended use |
| Queue submission semantics | [`vkQueueBindSparse`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L1691-L1758) | Defines sparse batch ordering and completion |
| Device-group sparse binding | [`VkDeviceGroupBindSparseInfo`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L1877-L1921) | Defines resource and memory device indices |
